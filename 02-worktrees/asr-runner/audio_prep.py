#!/usr/bin/env python3
"""
Audio preparation CLI for ASR pipeline.

Demuxes video/audio to mono 16 kHz WAV, optionally runs vocal isolation
when music/overlap is detected, and logs prep metadata for reuse.
"""

from pathlib import Path
from typing import Optional

import typer
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from utils.paths import (
    project_parent,
    supporting_files,
    transcripts_dir,
    large_files_dir,
    resolve_transcript_dir,
    check_rocm_visibility,
)
from utils.audio import (
    demux_to_mono_16k,
    get_audio_info,
    compute_checksum,
    write_manifest,
    detect_overlap,
    estimate_snr,
    run_vocal_isolation,
    PrepManifest,
    AudioInfo,
)

app = typer.Typer(
    name="audio-prep",
    help="Audio preparation CLI for DougDoug ASR pipeline",
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


@app.command()
def prep(
    source_id: str = typer.Option(
        ..., "--source-id", "-s", help="Unique identifier for the source"
    ),
    input_file: str = typer.Option(..., "--input", "-i", help="Input video/audio file path"),
    output_dir: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output directory (default: transcripts/{source_id})"
    ),
    overwrite: bool = typer.Option(False, "--overwrite", "-f", help="Overwrite existing outputs"),
    skip_isolation: bool = typer.Option(
        False, "--skip-isolation", help="Skip vocal isolation even if overlap detected"
    ),
    force_isolation: bool = typer.Option(
        False, "--force-isolation", help="Force vocal isolation regardless of overlap detection"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
) -> None:
    """
    Prepare audio for ASR transcription.

    Demuxes to mono 16 kHz WAV, optionally isolates vocals, and writes manifest.
    """
    configure_logging(verbose)

    # Resolve input path
    input_path = Path(input_file)
    if not input_path.is_absolute():
        # Try relative to large-files first
        large_path = large_files_dir / input_file
        if large_path.exists():
            input_path = large_path
        else:
            input_path = Path.cwd() / input_file

    if not input_path.exists():
        console.print(f"[red]Error: Input file not found: {input_path}[/red]")
        raise typer.Exit(1)

    # Resolve output directory
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = resolve_transcript_dir(source_id)

    output_path.mkdir(parents=True, exist_ok=True)

    console.print(
        Panel(
            f"[bold]Source ID:[/bold] {source_id}\n"
            f"[bold]Input:[/bold] {input_path}\n"
            f"[bold]Output:[/bold] {output_path}",
            title="Audio Prep",
            border_style="blue",
        )
    )

    # Step 1: Demux and resample
    console.print("[bold cyan]Step 1: Demuxing to mono 16 kHz WAV...[/bold cyan]")
    mono_output = output_path / f"source-{source_id}-mono16k.wav"

    try:
        audio_info = demux_to_mono_16k(input_path, mono_output, overwrite=overwrite)
        logger.info(
            f"Demuxed audio: {audio_info.duration_seconds:.2f}s, {audio_info.sample_rate}Hz, {audio_info.channels}ch"
        )
    except Exception as e:
        console.print(f"[red]Error during demux: {e}[/red]")
        raise typer.Exit(1)

    # Step 2: Detect overlap and decide on isolation
    console.print("[bold cyan]Step 2: Analyzing for music/overlap...[/bold cyan]")
    overlap_score, should_isolate = detect_overlap(mono_output)

    # Determine isolation decision
    isolation_triggered = False
    vocal_output = None
    isolation_method = None
    isolation_quality = None

    if force_isolation and not skip_isolation:
        console.print("[yellow]Forcing vocal isolation (user requested)[/yellow]")
        isolation_triggered = True
    elif skip_isolation:
        console.print("[yellow]Skipping vocal isolation (user requested)[/yellow]")
        isolation_triggered = False
    elif should_isolate:
        console.print(
            f"[yellow]Overlap detected (score: {overlap_score:.2f}), running vocal isolation...[/yellow]"
        )
        isolation_triggered = True

    # Step 3: Run vocal isolation if needed
    if isolation_triggered:
        console.print("[bold cyan]Step 3: Running vocal isolation...[/bold cyan]")
        vocal_output = output_path / f"source-{source_id}-vocal.wav"

        try:
            # Check ROCm availability first
            check_rocm_visibility()

            vocal_output, isolation_quality = run_vocal_isolation(
                mono_output,
                vocal_output,
                method="demucs",
                model="htdemucs",
                overwrite=overwrite,
            )
            isolation_method = "demucs_htdemucs"
            console.print(f"[green]Vocal isolation complete: {vocal_output}[/green]")
            console.print(f"[green]Quality score: {isolation_quality:.2f}[/green]")

        except Exception as e:
            console.print(f"[red]Warning: Vocal isolation failed: {e}[/red]")
            console.print("[yellow]Proceeding with original mono mix[/yellow]")
            isolation_triggered = False
            vocal_output = None
            isolation_quality = None

    # Step 4: Compute final audio stats
    console.print("[bold cyan]Step 4: Computing audio statistics...[/bold cyan]")
    final_audio = vocal_output if vocal_output else mono_output
    checksum = compute_checksum(final_audio)
    snr = estimate_snr(final_audio)

    # Build quality flags
    quality_flags = []
    if overlap_score > 0.5:
        quality_flags.append("high_overlap")
    if isolation_quality is not None and isolation_quality < 0.6:
        quality_flags.append("low_separation_quality")
    if snr is not None and snr < 10:
        quality_flags.append("low_snr")

    # Step 5: Write manifest
    console.print("[bold cyan]Step 5: Writing manifest...[/bold cyan]")
    manifest = PrepManifest(
        source_id=source_id,
        source_path=str(input_path),
        output_path=str(final_audio),
        duration_seconds=audio_info.duration_seconds,
        sample_rate=16000,
        channels=1,
        channel_map="mono_demuxed",
        checksum_sha256=checksum,
        isolation_triggered=isolation_triggered,
        isolation_method=isolation_method,
        isolation_quality_score=isolation_quality,
        overlap_score=overlap_score,
        snr_estimate_db=snr,
        quality_flags=quality_flags,
    )

    manifest_path = write_manifest(manifest, output_path)

    # Summary
    _print_summary(manifest, mono_output, vocal_output)


def _print_summary(manifest: PrepManifest, mono_output: Path, vocal_output: Optional[Path]) -> None:
    """Print a summary table of the prep run."""
    table = Table(title="Audio Prep Summary")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Source ID", manifest.source_id)
    table.add_row("Duration", f"{manifest.duration_seconds:.2f}s")
    table.add_row("Sample Rate", f"{manifest.sample_rate} Hz")
    table.add_row("Channel Map", manifest.channel_map)
    table.add_row("Overlap Score", f"{manifest.overlap_score:.2f}")
    table.add_row("Isolation Triggered", str(manifest.isolation_triggered))
    if manifest.isolation_method:
        table.add_row("Isolation Method", manifest.isolation_method)
    if manifest.isolation_quality_score:
        table.add_row("Isolation Quality", f"{manifest.isolation_quality_score:.2f}")
    if manifest.snr_estimate_db:
        table.add_row("SNR Estimate", f"{manifest.snr_estimate_db:.1f} dB")
    table.add_row("Quality Flags", ", ".join(manifest.quality_flags) or "None")
    table.add_row("Checksum", manifest.checksum_sha256[:16] + "...")

    console.print(table)

    console.print("\n[bold]Output Files:[/bold]")
    console.print(f"  Mono 16kHz: {mono_output}")
    if vocal_output:
        console.print(f"  Vocals:     {vocal_output}")
    console.print(f"  Manifest:   {manifest.source_id}/prep-manifest-{manifest.source_id}.json")


@app.command()
def info(
    source_id: str = typer.Option(..., "--source-id", "-s", help="Source ID to inspect"),
) -> None:
    """Show info about a prepared audio source."""
    from utils.paths import transcripts_dir

    manifest_path = transcripts_dir / source_id / f"prep-manifest-{source_id}.json"

    if not manifest_path.exists():
        console.print(f"[red]No manifest found for source: {source_id}[/red]")
        console.print(f"Expected: {manifest_path}")
        raise typer.Exit(1)

    import json

    with open(manifest_path) as f:
        data = json.load(f)

    table = Table(title=f"Source: {source_id}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    for key, value in data.items():
        if isinstance(value, list):
            value = ", ".join(str(v) for v in value) or "None"
        table.add_row(key.replace("_", " ").title(), str(value))

    console.print(table)


@app.command()
def list_sources() -> None:
    """List all prepared audio sources."""
    if not transcripts_dir.exists():
        console.print("[yellow]No transcripts directory found[/yellow]")
        return

    sources = []
    for source_dir in transcripts_dir.iterdir():
        if source_dir.is_dir():
            manifest = source_dir / f"prep-manifest-{source_dir.name}.json"
            wav_files = list(source_dir.glob("*.wav"))
            sources.append(
                {
                    "id": source_dir.name,
                    "has_manifest": manifest.exists(),
                    "wav_count": len(wav_files),
                }
            )

    if not sources:
        console.print("[yellow]No prepared sources found[/yellow]")
        return

    table = Table(title="Prepared Audio Sources")
    table.add_column("Source ID", style="cyan")
    table.add_column("Manifest", style="green")
    table.add_column("WAV Files", style="yellow")

    for source in sorted(sources, key=lambda x: x["id"]):
        table.add_row(
            source["id"],
            "✓" if source["has_manifest"] else "✗",
            str(source["wav_count"]),
        )

    console.print(table)


if __name__ == "__main__":
    app()
