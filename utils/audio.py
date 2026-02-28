"""
Audio processing utilities for ASR prep pipeline.

Wraps demux, resample, overlap detection, and optional vocal isolation
with quality flagging.
"""

import hashlib
import json
import subprocess
import shutil
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import soundfile as sf
import numpy as np
from loguru import logger


@dataclass
class AudioInfo:
    """Audio metadata extracted from a file."""

    path: str
    duration_seconds: float
    sample_rate: int
    channels: int
    format: str
    bitrate: Optional[str] = None
    codec: Optional[str] = None


@dataclass
class PrepManifest:
    """Manifest for audio prep run capturing all metadata."""

    source_id: str
    source_path: str
    output_path: str
    duration_seconds: float
    sample_rate: int
    channels: int
    channel_map: str  # e.g., "mono", "stereo", "demuxed_left"
    checksum_sha256: str
    isolation_triggered: bool = False
    isolation_method: Optional[str] = None  # e.g., "demucs_htdemucs"
    isolation_quality_score: Optional[float] = None  # 0-1 estimated quality
    overlap_score: Optional[float] = None  # 0-1 estimated overlap
    snr_estimate_db: Optional[float] = None
    quality_flags: list[str] = field(default_factory=list)
    run_timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


def compute_checksum(filepath: Path, chunk_size: int = 8192) -> str:
    """
    Compute SHA256 checksum of a file.

    Args:
        filepath: Path to the file
        chunk_size: Size of chunks to read at a time

    Returns:
        Hex-encoded SHA256 checksum
    """
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_audio_info(filepath: Path) -> AudioInfo:
    """
    Extract audio metadata using ffprobe.

    Args:
        filepath: Path to audio/video file

    Returns:
        AudioInfo with duration, sample rate, channels, etc.

    Raises:
        RuntimeError: If ffprobe fails
    """
    cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(filepath),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {filepath}: {result.stderr}")

    data = json.loads(result.stdout)

    # Find audio stream
    audio_stream = None
    for stream in data.get("streams", []):
        if stream.get("codec_type") == "audio":
            audio_stream = stream
            break

    if audio_stream is None:
        raise RuntimeError(f"No audio stream found in {filepath}")

    format_info = data.get("format", {})

    # Get duration from stream or format
    duration = float(audio_stream.get("duration") or format_info.get("duration", 0))

    return AudioInfo(
        path=str(filepath),
        duration_seconds=duration,
        sample_rate=int(audio_stream.get("sample_rate", 0)),
        channels=int(audio_stream.get("channels", 1)),
        format=format_info.get("format_name", "unknown"),
        bitrate=format_info.get("bit_rate"),
        codec=audio_stream.get("codec_name"),
    )


def demux_to_mono_16k(
    input_path: Path,
    output_path: Path,
    overwrite: bool = False,
    channel: Optional[int] = None,
) -> AudioInfo:
    """
    Demux and resample audio to mono 16 kHz WAV.

    Args:
        input_path: Path to input video/audio file
        output_path: Path for output WAV file
        overwrite: If True, overwrite existing output
        channel: If set, extract specific channel (0=first, 1=second, etc.)

    Returns:
        AudioInfo for the output file

    Raises:
        RuntimeError: If ffmpeg fails
    """
    if output_path.exists() and not overwrite:
        logger.info(f"Output exists, skipping demux: {output_path}")
        return get_audio_info(output_path)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Build ffmpeg command
    cmd = [
        "ffmpeg",
        "-y" if overwrite else "-n",
        "-i",
        str(input_path),
        "-vn",  # No video
        "-acodec",
        "pcm_s16le",  # 16-bit PCM
        "-ar",
        "16000",  # 16 kHz sample rate
    ]

    # Handle channel selection
    if channel is not None:
        # Use pan filter to select specific channel
        # pan=mono|c0=c{channel} selects channel N
        cmd.extend(["-af", f"pan=mono|c0=c{channel}"])
    else:
        # Mix down to mono
        cmd.extend(["-ac", "1"])

    cmd.append(str(output_path))

    logger.info(f"Running ffmpeg demux: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg demux failed: {result.stderr}")

    logger.info(f"Demuxed audio to: {output_path}")
    return get_audio_info(output_path)


def write_manifest(manifest: PrepManifest, output_dir: Path) -> Path:
    """
    Write manifest JSON to the output directory.

    Args:
        manifest: PrepManifest to write
        output_dir: Directory to write manifest to

    Returns:
        Path to the written manifest file
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / f"prep-manifest-{manifest.source_id}.json"

    with open(manifest_path, "w") as f:
        f.write(manifest.to_json())

    logger.info(f"Wrote manifest: {manifest_path}")
    return manifest_path


def detect_overlap(
    audio_path: Path,
    window_seconds: float = 0.5,
    hop_seconds: float = 0.25,
    energy_threshold_db: float = -40.0,
    spectral_threshold: float = 0.3,
) -> tuple[float, bool]:
    """
    Detect potential music/overlap in audio using band-energy analysis.

    This is a lightweight heuristic to decide if vocal isolation is needed.
    Uses spectral centroid and band energy ratios to detect non-speech content.

    Args:
        audio_path: Path to audio file
        window_seconds: Analysis window length
        hop_seconds: Hop between windows
        energy_threshold_db: Threshold for low-energy detection
        spectral_threshold: Threshold for spectral complexity (higher = more music-like)

    Returns:
        Tuple of (overlap_score 0-1, should_isolate bool)
    """
    try:
        import librosa
    except ImportError:
        logger.warning("librosa not installed, skipping overlap detection")
        return 0.0, False

    # Load audio
    y, sr = librosa.load(str(audio_path), sr=16000, mono=True)

    # Compute spectral features
    # Spectral centroid - higher values often indicate music/bright sounds
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    centroid_mean = np.mean(spectral_centroid)

    # Spectral bandwidth - variance in frequency distribution
    spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    bandwidth_mean = np.mean(spectral_bandwidth)

    # Spectral flatness - measures how noise-like vs tonal
    # Higher values (>0.5) often indicate music/tone, lower values indicate speech
    spectral_flatness = librosa.feature.spectral_flatness(y=y)
    flatness_mean = np.mean(spectral_flatness)

    # Spectral rolloff - frequency below which 85% of energy is contained
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
    rolloff_mean = np.mean(rolloff)

    # RMS energy
    rms = librosa.feature.rms(y=y)
    rms_mean = np.mean(rms)

    logger.debug(
        f"Spectral analysis: centroid={centroid_mean:.0f}Hz, "
        f"bandwidth={bandwidth_mean:.0f}Hz, flatness={flatness_mean:.3f}, "
        f"rolloff={rolloff_mean:.0f}Hz, rms={rms_mean:.4f}"
    )

    # Heuristic scoring for music/overlap
    # Music tends to have: higher flatness, higher centroid, higher bandwidth
    # Speech tends to have: lower flatness, moderate centroid, lower bandwidth

    overlap_score = 0.0
    flags = []

    # Spectral flatness: music typically > 0.3, speech < 0.2
    if flatness_mean > 0.4:
        overlap_score += 0.4
        flags.append("high_flatness")
    elif flatness_mean > 0.25:
        overlap_score += 0.2

    # Spectral centroid: music typically > 2000Hz for full mix
    if centroid_mean > 3000:
        overlap_score += 0.3
        flags.append("high_centroid")
    elif centroid_mean > 2000:
        overlap_score += 0.15

    # Spectral bandwidth: wider bandwidth often indicates complex music
    if bandwidth_mean > 3000:
        overlap_score += 0.2
        flags.append("wide_bandwidth")
    elif bandwidth_mean > 2000:
        overlap_score += 0.1

    # Rolloff: high rolloff indicates high-frequency content (cymbals, etc.)
    if rolloff_mean > 6000:
        overlap_score += 0.1
        flags.append("high_rolloff")

    # Clamp score to 0-1
    overlap_score = min(1.0, overlap_score)

    # Determine if isolation is warranted
    # Threshold tuned for DougDoug streams - may need calibration
    should_isolate = overlap_score >= spectral_threshold

    logger.info(
        f"Overlap detection: score={overlap_score:.2f}, isolate={should_isolate}, flags={flags}"
    )

    return overlap_score, should_isolate


def estimate_snr(audio_path: Path) -> Optional[float]:
    """
    Estimate signal-to-noise ratio of audio.

    This is a rough estimate based on RMS energy distribution.
    Real SNR measurement would need a reference clean signal.

    Args:
        audio_path: Path to audio file

    Returns:
        Estimated SNR in dB, or None if estimation fails
    """
    try:
        import librosa
    except ImportError:
        return None

    try:
        y, sr = librosa.load(str(audio_path), sr=16000, mono=True)

        # Use percentile-based estimation
        # Assume the 10th percentile of RMS represents noise floor
        # and 90th percentile represents signal
        rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)
        rms_flat = rms.flatten()

        noise_floor = np.percentile(rms_flat, 10)
        signal_level = np.percentile(rms_flat, 90)

        if noise_floor < 1e-10:
            return None  # Avoid division by zero

        snr_db = 20 * np.log10(signal_level / noise_floor)
        return float(snr_db)

    except Exception as e:
        logger.warning(f"SNR estimation failed: {e}")
        return None


def run_vocal_isolation(
    input_path: Path,
    output_path: Path,
    method: str = "demucs",
    model: str = "htdemucs",
    overwrite: bool = False,
) -> tuple[Path, float]:
    """
    Run vocal isolation on audio file.

    Args:
        input_path: Path to input audio file
        output_path: Path for isolated vocals output
        method: Separation method ("demucs" or "uvr5")
        model: Model to use for separation
        overwrite: If True, overwrite existing output

    Returns:
        Tuple of (path to isolated vocals, quality score estimate)

    Raises:
        RuntimeError: If separation fails
    """
    if output_path.exists() and not overwrite:
        logger.info(f"Isolated vocals exist, skipping: {output_path}")
        return output_path, 0.8  # Assume acceptable quality if already processed

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if method == "demucs":
        return _run_demucs(input_path, output_path, model)
    else:
        raise ValueError(f"Unknown isolation method: {method}")


def _run_demucs(
    input_path: Path,
    output_path: Path,
    model: str = "htdemucs",
) -> tuple[Path, float]:
    """
    Run Demucs separation.

    Args:
        input_path: Input audio path
        output_path: Output path for vocals
        model: Demucs model name

    Returns:
        Tuple of (vocals path, quality estimate)
    """
    # Check if demucs is available
    if shutil.which("demucs") is None:
        logger.warning("demucs not installed, skipping vocal isolation")
        raise RuntimeError("demucs CLI not found - install with: pip install demucs")

    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        cmd = [
            "demucs",
            "-n",
            model,
            "-o",
            tmpdir,
            "--two-stems=vocals",  # Only output vocals
            str(input_path),
        ]

        logger.info(f"Running Demucs: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Demucs failed: {result.stderr}")

        # Demucs outputs to tmpdir/model/input_stem/vocals.wav
        vocals_dir = Path(tmpdir) / model / input_path.stem
        vocals_file = vocals_dir / "vocals.wav"

        if not vocals_file.exists():
            raise RuntimeError(f"Demucs output not found at {vocals_file}")

        # Copy to final location
        shutil.copy(vocals_file, output_path)
        logger.info(f"Demucs vocals saved to: {output_path}")

    # Estimate quality based on SNR
    quality_score = 0.7  # Default acceptable quality
    snr = estimate_snr(output_path)
    if snr is not None:
        # Map SNR to quality score
        # Higher SNR = better separation
        # SNR < 10dB = poor, 10-20dB = acceptable, >20dB = good
        if snr < 10:
            quality_score = 0.5
        elif snr < 15:
            quality_score = 0.7
        elif snr < 20:
            quality_score = 0.85
        else:
            quality_score = 0.95

    return output_path, quality_score
