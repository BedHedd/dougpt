#!/usr/bin/env python3
"""
ASR Pipeline CLI for DougDoug transcript extraction.

Consumes prepped audio from audio_prep.py, runs faster-whisper + whisperX
alignment with optional diarization, and exports normalized JSONL segments
with confidence metadata.
"""

import json
import os
from pathlib import Path
from typing import Optional

import typer
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from utils.paths import (
    project_parent,
    transcripts_dir,
    resolve_transcript_dir,
    check_rocm_visibility,
)
from utils.export import (
    export_raw_segments,
    export_normalized_segments,
    write_transcript_manifest,
    load_prep_manifest,
    resolve_audio_for_asr,
)
from utils.confidence import (
    aggregate_segment_confidence,
    flag_low_confidence_segments,
    compute_quality_summary,
    compute_segment_statistics,
    confidence_from_logprob,
)
from schemas.transcript import (
    WordTiming,
    RawSegment,
    NormalizedSegment,
    TranscriptManifest,
)

app = typer.Typer(
    name="asr-pipeline",
    help="ASR pipeline for DougDoug transcript extraction",
    add_completion=False,
)
console = Console()


def configure_logging(verbose: bool = False):
    """Configure loguru logging."""
    import sys

    logger.remove()
    level = "DEBUG" if verbose else "INFO"
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
    )


def normalize_text(text: str) -> str:
    """
    Normalize transcript text.

    - Sentence case
    - Trim whitespace
    - Keep fillers as spoken
    """
    text = text.strip()
    if not text:
        return ""
    # Sentence case: capitalize first letter
    return text[0].upper() + text[1:] if len(text) > 1 else text.upper()


def segment_id_from_timing(source_id: str, start_ms: int) -> str:
    """Generate segment ID from source and timing."""
    return f"{source_id}-{start_ms:06d}"


@app.command()
def transcribe(
    source_id: str = typer.Option(
        ..., "--source-id", "-s", help="Unique identifier for the source"
    ),
    input_audio: Optional[str] = typer.Option(
        None, "--input", "-i", help="Input audio file (default: auto-resolve from prep)"
    ),
    model: str = typer.Option("large-v3", "--model", "-m", help="Whisper model to use"),
    language: Optional[str] = typer.Option(
        None, "--language", "-l", help="Language code (auto-detect if not specified)"
    ),
    device: str = typer.Option("cuda", "--device", "-d", help="Device: cuda or cpu"),
    compute_type: str = typer.Option(
        "float16", "--compute-type", "-c", help="Compute type: float16, int8, float32"
    ),
    min_confidence: float = typer.Option(
        0.70, "--min-confidence", help="Minimum confidence for export"
    ),
    skip_diarization: bool = typer.Option(
        False, "--skip-diarization", help="Skip speaker diarization"
    ),
    skip_alignment: bool = typer.Option(False, "--skip-alignment", help="Skip whisperX alignment"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show plan without running"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """
    Run ASR transcription on prepared audio.

    Consumes audio from audio_prep.py and exports JSONL transcripts.
    """
    configure_logging(verbose)

    # Check ROCm availability
    check_rocm_visibility()

    # Resolve input audio
    if input_audio:
        audio_path = Path(input_audio)
        if not audio_path.is_absolute():
            audio_path = Path.cwd() / input_audio
    else:
        audio_path = resolve_audio_for_asr(source_id, transcripts_dir)
        if audio_path is None:
            console.print(f"[red]Error: No prepared audio found for source: {source_id}[/red]")
            console.print(
                "Run audio-prep first: uv run python audio_prep.py prep --source-id {source_id} --input <video>"
            )
            raise typer.Exit(1)

    if not audio_path.exists():
        console.print(f"[red]Error: Audio file not found: {audio_path}[/red]")
        raise typer.Exit(1)

    # Load prep manifest for metadata
    prep_manifest = load_prep_manifest(source_id, transcripts_dir)

    # Output directory
    output_dir = resolve_transcript_dir(source_id)

    console.print(
        Panel(
            f"[bold]Source ID:[/bold] {source_id}\n"
            f"[bold]Audio:[/bold] {audio_path}\n"
            f"[bold]Model:[/bold] {model}\n"
            f"[bold]Device:[/bold] {device}\n"
            f"[bold]Output:[/bold] {output_dir}",
            title="ASR Pipeline",
            border_style="blue",
        )
    )

    if dry_run:
        console.print("[yellow]Dry run - not executing transcription[/yellow]")
        return

    # Import ASR libraries
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        console.print("[red]Error: faster-whisper not installed[/red]")
        console.print("Install with: uv pip install faster-whisper")
        raise typer.Exit(1)

    # Step 1: Run faster-whisper transcription
    console.print("[bold cyan]Step 1: Running faster-whisper transcription...[/bold cyan]")

    whisper_model = WhisperModel(
        model,
        device=device,
        compute_type=compute_type,
    )

    segments, info = whisper_model.transcribe(
        str(audio_path),
        language=language,
        word_timestamps=True,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 500},
    )
    segments = list(segments)

    console.print(
        f"[green]Transcribed {len(segments)} segments "
        f"(language: {info.language}, probability: {info.language_probability:.2f})[/green]"
    )

    # Convert to RawSegment objects
    raw_segments = []
    for seg in segments:
        words = []
        for w in seg.words:
            word_conf = confidence_from_logprob(w.probability) if w.probability else None
            words.append(
                WordTiming(
                    word=w.word,
                    start=w.start,
                    end=w.end,
                    confidence=word_conf,
                    logprob=w.probability,
                )
            )

        raw_segments.append(
            RawSegment(
                text=seg.text,
                start=seg.start,
                end=seg.end,
                words=words,
                speaker=None,  # Will be filled by diarization
                language=info.language,
                language_probability=info.language_probability,
            )
        )

    # Step 2: Run whisperX alignment (optional)
    if not skip_alignment:
        console.print("[bold cyan]Step 2: Running whisperX alignment...[/bold cyan]")
        try:
            import whisperx

            # Load audio
            audio = whisperx.load_audio(str(audio_path))

            # Load alignment model
            align_model, align_metadata = whisperx.load_align_model(
                language_code=info.language,
                device=device,
            )

            # Prepare segments for alignment
            seg_dicts = [{"start": s.start, "end": s.end, "text": s.text} for s in raw_segments]

            # Align
            aligned = whisperx.align(
                seg_dicts,
                align_model,
                align_metadata,
                audio,
                device,
            )

            # Update segments with aligned timings
            for i, seg in enumerate(aligned.get("segments", [])):
                if i < len(raw_segments):
                    raw_segments[i].start = seg.get("start", raw_segments[i].start)
                    raw_segments[i].end = seg.get("end", raw_segments[i].end)
                    # Update words if available
                    if "words" in seg:
                        raw_segments[i].words = [
                            WordTiming(
                                word=w.get("word", ""),
                                start=w.get("start", 0),
                                end=w.get("end", 0),
                                confidence=w.get("score"),
                            )
                            for w in seg["words"]
                        ]

            console.print("[green]Alignment complete[/green]")

        except ImportError:
            console.print("[yellow]whisperX not installed, skipping alignment[/yellow]")
        except Exception as e:
            logger.warning(f"Alignment failed: {e}")
            console.print(f"[yellow]Alignment failed: {e}[/yellow]")

    # Step 3: Run diarization (optional)
    if not skip_diarization:
        console.print("[bold cyan]Step 3: Running speaker diarization...[/bold cyan]")
        hf_token = os.environ.get("HF_TOKEN")

        if not hf_token:
            console.print("[yellow]HF_TOKEN not set, skipping diarization[/yellow]")
            console.print("Set HF_TOKEN environment variable to enable diarization")
        else:
            try:
                import whisperx

                diarize_model = whisperx.DiarizationPipeline(
                    use_auth_token=hf_token,
                    device=device,
                )

                audio = whisperx.load_audio(str(audio_path))
                diar_segments = diarize_model(audio)

                # Assign speakers to segments
                for seg in raw_segments:
                    # Find overlapping diarization segment
                    seg_mid = (seg.start + seg.end) / 2
                    for ds in diar_segments:
                        if ds["start"] <= seg_mid <= ds["end"]:
                            seg.speaker = f"SPEAKER_{ds.get('speaker', '00')}"
                            break

                console.print("[green]Diarization complete[/green]")

            except ImportError:
                console.print("[yellow]whisperX not installed, skipping diarization[/yellow]")
            except Exception as e:
                logger.warning(f"Diarization failed: {e}")
                console.print(f"[yellow]Diarization failed: {e}[/yellow]")

    # Step 4: Create normalized segments
    console.print("[bold cyan]Step 4: Creating normalized segments...[/bold cyan]")

    normalized_segments = []
    for seg in raw_segments:
        # Aggregate confidence
        seg_conf, low_conf_words, total_words = aggregate_segment_confidence(
            seg.words, method="mean"
        )

        # Create segment ID
        start_ms = int(seg.start * 1000)
        seg_id = segment_id_from_timing(source_id, start_ms)

        # Quality flags
        quality_flags = []
        if seg_conf < min_confidence:
            quality_flags.append("low_confidence")
        if seg.end - seg.start < 1.0:
            quality_flags.append("short_segment")
        if seg.speaker is None:
            quality_flags.append("no_speaker")

        normalized_segments.append(
            NormalizedSegment(
                segment_id=seg_id,
                source_id=source_id,
                start=seg.start,
                end=seg.end,
                duration_seconds=seg.end - seg.start,
                text_raw=seg.text,
                text_normalized=normalize_text(seg.text),
                speaker=seg.speaker,
                confidence=seg_conf,
                confidence_method="mean_word",
                word_count=total_words,
                low_confidence_words=low_conf_words,
                quality_flags=quality_flags,
                words=seg.words,
                sample_rate=16000,
                channel_map=prep_manifest.get("channel_map", "mono") if prep_manifest else "mono",
            )
        )

    # Flag low-confidence segments
    flag_low_confidence_segments(normalized_segments, threshold=min_confidence)

    # Step 5: Export
    console.print("[bold cyan]Step 5: Exporting transcripts...[/bold cyan]")

    raw_path = export_raw_segments(raw_segments, output_dir, source_id)
    norm_path, norm_count = export_normalized_segments(
        normalized_segments, output_dir, source_id, min_confidence=min_confidence
    )

    # Compute statistics
    stats = compute_segment_statistics(normalized_segments)
    quality_summary = compute_quality_summary(normalized_segments)

    # Write manifest
    manifest = TranscriptManifest(
        source_id=source_id,
        audio_path=str(audio_path),
        manifest_path=str(output_dir / f"prep-manifest-{source_id}.json")
        if prep_manifest
        else None,
        model=model,
        language=info.language,
        compute_type=compute_type,
        device=device,
        total_segments=stats["total_segments"],
        total_duration_seconds=stats["total_duration_seconds"],
        total_words=stats["total_words"],
        avg_confidence=stats["avg_confidence"],
        low_confidence_segments=stats["low_confidence_segments"],
        quality_summary=quality_summary,
        raw_output=str(raw_path),
        normalized_output=str(norm_path),
    )

    manifest_path = write_transcript_manifest(manifest, output_dir)

    # Summary
    _print_summary(manifest, raw_path, norm_path)


def _print_summary(manifest: TranscriptManifest, raw_path: Path, norm_path: Path) -> None:
    """Print a summary table of the ASR run."""
    table = Table(title="ASR Pipeline Summary")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Source ID", manifest.source_id)
    table.add_row("Model", manifest.model)
    table.add_row("Language", manifest.language or "auto-detected")
    table.add_row("Total Segments", str(manifest.total_segments))
    table.add_row("Total Duration", f"{manifest.total_duration_seconds:.2f}s")
    table.add_row("Total Words", str(manifest.total_words))
    table.add_row("Avg Confidence", f"{manifest.avg_confidence:.2f}")
    table.add_row("Low Confidence Segments", str(manifest.low_confidence_segments))

    console.print(table)

    console.print("\n[bold]Output Files:[/bold]")
    console.print(f"  Raw:        {raw_path}")
    console.print(f"  Normalized: {norm_path}")
    console.print(
        f"  Manifest:   {manifest.source_id}/transcript-manifest-{manifest.source_id}.json"
    )


@app.command()
def info(
    source_id: str = typer.Option(..., "--source-id", "-s", help="Source ID to inspect"),
) -> None:
    """Show info about a transcribed source."""
    manifest_path = transcripts_dir / source_id / f"transcript-manifest-{source_id}.json"

    if not manifest_path.exists():
        console.print(f"[red]No transcript manifest found for source: {source_id}[/red]")
        console.print(f"Expected: {manifest_path}")
        raise typer.Exit(1)

    with open(manifest_path) as f:
        data = json.load(f)

    table = Table(title=f"Transcript: {source_id}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    for key, value in data.items():
        if isinstance(value, dict):
            value = ", ".join(f"{k}: {v}" for k, v in value.items())
        elif isinstance(value, list):
            value = ", ".join(str(v) for v in value) or "None"
        table.add_row(key.replace("_", " ").title(), str(value))

    console.print(table)


if __name__ == "__main__":
    app()
