#!/usr/bin/env python3
"""
ASR Pipeline CLI for DougDoug transcript extraction.

Consumes prepped audio from audio_prep.py, runs Moonshine ASR,
and exports normalized JSONL segments with confidence metadata.
"""

import json
from pathlib import Path
from typing import Optional

import typer
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from utils.paths import (
    transcripts_dir,
    resolve_transcript_dir,
)
from utils.export import (
    write_transcript_manifest,
    load_prep_manifest,
    resolve_audio_for_asr,
)
from utils.confidence import (
    compute_quality_summary,
    compute_segment_statistics,
)
from schemas.transcript import (
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

MOONSHINE_MODEL_CACHE = Path.home() / ".cache" / "moonshine_voice" / "download.moonshine.ai"


def configure_logging(verbose: bool = False):
    import sys

    logger.remove()
    level = "DEBUG" if verbose else "INFO"
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
    )


def normalize_text(text: str) -> str:
    text = text.strip()
    if not text:
        return ""
    return text[0].upper() + text[1:] if len(text) > 1 else text.upper()


def segment_id_from_timing(source_id: str, start_ms: int) -> str:
    return f"{source_id}-{start_ms:06d}"


def get_moonshine_model_path(model: str, language: str = "en") -> tuple[str, int]:
    """
    Resolve Moonshine model path.
    Returns (path, arch_int) where arch_int is the model architecture number.
    """
    model_map = {
        "tiny": ("tiny-streaming-en", 1),
        "base": ("base-streaming-en", 2),
        "small": ("small-streaming-en", 3),
        "medium": ("medium-streaming-en", 5),
    }

    if model in model_map:
        model_name, arch = model_map[model]
    else:
        model_name, arch = model_map["medium"]

    model_path = MOONSHINE_MODEL_CACHE / "model" / model_name / "quantized"
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found at {model_path}. "
            f"Run: uv run python -m moonshine_voice.download --language {language}"
        )

    return str(model_path), arch


class StreamingJSONLWriter:
    """Writes segments to JSONL files as they're processed."""

    def __init__(self, output_dir: Path, source_id: str):
        self.output_dir = output_dir
        self.source_id = source_id
        self.raw_path = output_dir / f"segments-{source_id}-raw.jsonl"
        self.norm_path = output_dir / f"segments-{source_id}-normalized.jsonl"
        self.raw_file = open(self.raw_path, "w")
        self.norm_file = open(self.norm_path, "w")
        self.count = 0

    def write_segment(self, raw: RawSegment, normalized: NormalizedSegment):
        self.raw_file.write(raw.model_dump_json() + "\n")
        self.norm_file.write(normalized.model_dump_json() + "\n")
        self.count += 1

    def close(self):
        self.raw_file.close()
        self.norm_file.close()

    def paths(self) -> tuple[Path, Path]:
        return self.raw_path, self.norm_path


@app.command()
def transcribe(
    source_id: str = typer.Option(
        ..., "--source-id", "-s", help="Unique identifier for the source"
    ),
    input_audio: Optional[str] = typer.Option(
        None, "--input", "-i", help="Input audio file (default: auto-resolve from prep)"
    ),
    model: str = typer.Option(
        "medium", "--model", "-m", help="Moonshine model: tiny, base, small, medium"
    ),
    language: str = typer.Option("en", "--language", "-l", help="Language code"),
    min_confidence: float = typer.Option(
        0.70, "--min-confidence", help="Minimum confidence threshold for quality flags"
    ),
    chunk_seconds: int = typer.Option(
        300, "--chunk-size", help="Process audio in chunks of this many seconds"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show plan without running"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """
    Run ASR transcription on prepared audio using Moonshine.
    """
    configure_logging(verbose)

    if input_audio:
        audio_path = Path(input_audio)
        if not audio_path.is_absolute():
            audio_path = Path.cwd() / input_audio
    else:
        audio_path = resolve_audio_for_asr(source_id, transcripts_dir)
        if audio_path is None:
            console.print(f"[red]Error: No prepared audio found for source: {source_id}[/red]")
            console.print(
                f"Run audio-prep first: uv run python audio_prep.py prep --source-id {source_id} --input <video>"
            )
            raise typer.Exit(1)

    if not audio_path.exists():
        console.print(f"[red]Error: Audio file not found: {audio_path}[/red]")
        raise typer.Exit(1)

    prep_manifest = load_prep_manifest(source_id, transcripts_dir)
    output_dir = resolve_transcript_dir(source_id)

    console.print(
        Panel(
            f"[bold]Source ID:[/bold] {source_id}\n"
            f"[bold]Audio:[/bold] {audio_path}\n"
            f"[bold]Model:[/bold] moonshine-{model}\n"
            f"[bold]Language:[/bold] {language}\n"
            f"[bold]Chunk Size:[/bold] {chunk_seconds}s\n"
            f"[bold]Output:[/bold] {output_dir}",
            title="Moonshine ASR Pipeline",
            border_style="blue",
        )
    )

    if dry_run:
        console.print("[yellow]Dry run - not executing transcription[/yellow]")
        return

    from moonshine_voice import Transcriber, load_wav_file, ModelArch

    try:
        model_path, model_arch_int = get_moonshine_model_path(model, language)
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

    console.print(f"[bold cyan]Loading Moonshine model from {model_path}...[/bold cyan]")

    arch_map = {
        1: ModelArch.TINY_STREAMING,
        2: ModelArch.BASE_STREAMING,
        3: ModelArch.SMALL_STREAMING,
        5: ModelArch.MEDIUM_STREAMING,
    }
    model_arch = arch_map.get(model_arch_int, ModelArch.MEDIUM_STREAMING)

    console.print("[bold cyan]Loading audio...[/bold cyan]")
    audio_data, sample_rate = load_wav_file(audio_path)
    total_samples = len(audio_data)
    duration_seconds = total_samples / sample_rate
    console.print(f"[green]Loaded {duration_seconds:.2f}s of audio ({sample_rate}Hz)[/green]")

    transcriber = Transcriber(model_path=model_path, model_arch=model_arch)

    writer = StreamingJSONLWriter(output_dir, source_id)
    all_segments = []

    chunk_samples = chunk_seconds * sample_rate
    num_chunks = (total_samples + chunk_samples - 1) // chunk_samples

    console.print(f"[bold cyan]Transcribing in {num_chunks} chunks...[/bold cyan]")

    for chunk_idx in range(num_chunks):
        start_sample = chunk_idx * chunk_samples
        end_sample = min((chunk_idx + 1) * chunk_samples, total_samples)
        chunk_audio = audio_data[start_sample:end_sample]
        chunk_duration = len(chunk_audio) / sample_rate
        chunk_offset = start_sample / sample_rate

        console.print(
            f"[dim]Chunk {chunk_idx + 1}/{num_chunks}: {chunk_offset:.1f}s - {chunk_offset + chunk_duration:.1f}s[/dim]"
        )

        try:
            transcript = transcriber.transcribe_without_streaming(chunk_audio, sample_rate)
        except Exception as e:
            logger.error(f"Chunk {chunk_idx + 1} failed: {e}")
            continue

        lines = transcript.lines
        for i, line in enumerate(lines):
            start_time = line.start_time + chunk_offset
            if i + 1 < len(lines):
                end_time = lines[i + 1].start_time + chunk_offset
            else:
                end_time = chunk_offset + chunk_duration

            text = line.text.strip()
            if not text:
                continue

            start_ms = int(start_time * 1000)
            seg_id = segment_id_from_timing(source_id, start_ms)

            quality_flags = []
            if end_time - start_time < 1.0:
                quality_flags.append("short_segment")
            quality_flags.append("no_speaker")

            raw = RawSegment(
                text=text,
                start=start_time,
                end=end_time,
                words=[],
                speaker=None,
                language=language,
                language_probability=None,
            )

            norm = NormalizedSegment(
                segment_id=seg_id,
                source_id=source_id,
                start=start_time,
                end=end_time,
                duration_seconds=end_time - start_time,
                text_raw=text,
                text_normalized=normalize_text(text),
                speaker=None,
                confidence=0.0,
                confidence_method="none",
                word_count=len(text.split()),
                low_confidence_words=0,
                quality_flags=quality_flags,
                words=[],
                sample_rate=sample_rate,
                channel_map=prep_manifest.get("channel_map", "mono") if prep_manifest else "mono",
            )

            writer.write_segment(raw, norm)
            all_segments.append(norm)

    transcriber.close()
    writer.close()

    raw_path, norm_path = writer.paths()

    console.print(f"[green]Transcribed {len(all_segments)} total segments[/green]")

    stats = compute_segment_statistics(all_segments)
    quality_summary = compute_quality_summary(all_segments)

    manifest = TranscriptManifest(
        source_id=source_id,
        audio_path=str(audio_path),
        manifest_path=str(output_dir / f"prep-manifest-{source_id}.json")
        if prep_manifest
        else None,
        model=f"moonshine-{model}",
        language=language,
        compute_type="onnx",
        device="auto",
        total_segments=stats["total_segments"],
        total_duration_seconds=stats["total_duration_seconds"],
        total_words=stats["total_words"],
        avg_confidence=stats["avg_confidence"],
        low_confidence_segments=stats["low_confidence_segments"],
        quality_summary=quality_summary,
        raw_output=str(raw_path),
        normalized_output=str(norm_path),
    )

    write_transcript_manifest(manifest, output_dir)
    _print_summary(manifest, raw_path, norm_path)


def _print_summary(manifest: TranscriptManifest, raw_path: Path, norm_path: Path) -> None:
    table = Table(title="ASR Pipeline Summary")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Source ID", manifest.source_id)
    table.add_row("Model", manifest.model)
    table.add_row("Language", manifest.language or "auto-detected")
    table.add_row("Total Segments", str(manifest.total_segments))
    table.add_row("Total Duration", f"{manifest.total_duration_seconds:.2f}s")
    table.add_row("Total Words", str(manifest.total_words))

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


@app.command()
def download(
    language: str = typer.Option("en", "--language", "-l", help="Language to download"),
) -> None:
    """Download Moonshine model for a language."""
    from moonshine_voice import download as moonshine_download

    console.print(f"[bold cyan]Downloading Moonshine model for language: {language}[/bold cyan]")
    moonshine_download(language)
    console.print("[green]Download complete![/green]")


if __name__ == "__main__":
    app()
