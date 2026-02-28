"""
Export utilities for ASR transcripts.

Writes raw and normalized JSONL outputs under the transcripts directory
with deterministic filenames.
"""

import json
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

from loguru import logger

from schemas.transcript import (
    RawSegment,
    NormalizedSegment,
    TranscriptManifest,
    WordTiming,
)


def write_jsonl(
    segments: list,
    output_path: Path,
    line_transform: Optional[callable] = None,
) -> int:
    """
    Write segments to JSONL file.

    Args:
        segments: List of segment objects (RawSegment or NormalizedSegment)
        output_path: Path to output JSONL file
        line_transform: Optional function to transform each segment before writing

    Returns:
        Number of lines written
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines_written = 0
    with open(output_path, "w") as f:
        for segment in segments:
            if line_transform:
                data = line_transform(segment)
            else:
                data = segment.model_dump() if hasattr(segment, "model_dump") else segment

            f.write(json.dumps(data, ensure_ascii=False) + "\n")
            lines_written += 1

    logger.info(f"Wrote {lines_written} segments to {output_path}")
    return lines_written


def export_raw_segments(
    segments: list[RawSegment],
    output_dir: Path,
    source_id: str,
) -> Path:
    """
    Export raw ASR segments to JSONL.

    Args:
        segments: List of RawSegment objects
        output_dir: Output directory
        source_id: Source identifier

    Returns:
        Path to the written file
    """
    output_path = output_dir / f"segments-{source_id}-raw.jsonl"

    def transform(seg: RawSegment) -> dict:
        data = seg.model_dump()
        # Add computed fields
        data["duration_seconds"] = seg.end - seg.start
        return data

    write_jsonl(segments, output_path, transform)
    return output_path


def export_normalized_segments(
    segments: list[NormalizedSegment],
    output_dir: Path,
    source_id: str,
    min_confidence: float = 0.0,
) -> tuple[Path, int]:
    """
    Export normalized transcript segments to JSONL.

    Args:
        segments: List of NormalizedSegment objects
        output_dir: Output directory
        source_id: Source identifier
        min_confidence: Minimum confidence threshold for export

    Returns:
        Tuple of (path to written file, count of segments exported)
    """
    output_path = output_dir / f"segments-{source_id}-normalized.jsonl"

    # Filter by confidence if threshold set
    filtered = (
        [s for s in segments if s.confidence >= min_confidence] if min_confidence > 0 else segments
    )

    def transform(seg: NormalizedSegment) -> dict:
        return seg.model_dump()

    write_jsonl(filtered, output_path, transform)
    return output_path, len(filtered)


def write_transcript_manifest(
    manifest: TranscriptManifest,
    output_dir: Path,
) -> Path:
    """
    Write transcript manifest JSON.

    Args:
        manifest: TranscriptManifest object
        output_dir: Output directory

    Returns:
        Path to the written file
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / f"transcript-manifest-{manifest.source_id}.json"

    with open(manifest_path, "w") as f:
        f.write(manifest.model_dump_json(indent=2))

    logger.info(f"Wrote transcript manifest: {manifest_path}")
    return manifest_path


def load_prep_manifest(source_id: str, transcripts_dir: Path) -> Optional[dict]:
    """
    Load audio prep manifest for reference.

    Args:
        source_id: Source identifier
        transcripts_dir: Base transcripts directory

    Returns:
        Manifest dict if found, None otherwise
    """
    manifest_path = transcripts_dir / source_id / f"prep-manifest-{source_id}.json"

    if not manifest_path.exists():
        logger.warning(f"Prep manifest not found: {manifest_path}")
        return None

    with open(manifest_path) as f:
        return json.load(f)


def resolve_audio_for_asr(
    source_id: str,
    transcripts_dir: Path,
    prefer_vocal: bool = True,
) -> Optional[Path]:
    """
    Resolve the audio file to use for ASR.

    Prefers vocal-isolated audio if available, falls back to mono mix.

    Args:
        source_id: Source identifier
        transcripts_dir: Base transcripts directory
        prefer_vocal: Whether to prefer vocal-isolated audio

    Returns:
        Path to audio file if found, None otherwise
    """
    source_dir = transcripts_dir / source_id

    if prefer_vocal:
        vocal_path = source_dir / f"source-{source_id}-vocal.wav"
        if vocal_path.exists():
            logger.info(f"Using vocal-isolated audio: {vocal_path}")
            return vocal_path

    mono_path = source_dir / f"source-{source_id}-mono16k.wav"
    if mono_path.exists():
        logger.info(f"Using mono audio: {mono_path}")
        return mono_path

    logger.error(f"No audio file found for source: {source_id}")
    return None
