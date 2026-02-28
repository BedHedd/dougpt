# ASR Runner

Audio preparation worktree for DougDoug ASR pipeline.

## Overview

This worktree provides CLI tools for preparing audio from DougDoug stream videos for ASR transcription:

- Demux video to mono 16 kHz WAV
- Detect music/overlap in audio
- Conditionally run vocal isolation
- Log prep metadata for downstream processing

## Installation

```bash
cd 02-worktrees/asr-runner
uv sync
```

## Usage

```bash
# Prepare audio
uv run python audio_prep.py prep --source-id "VIDEO_ID" --input "/path/to/video.mp4"

# Inspect prepared source
uv run python audio_prep.py info --source-id "VIDEO_ID"

# List all prepared sources
uv run python audio_prep.py list-sources
```

## ROCm Support

This worktree is designed for ROCm GPU acceleration. Vocal isolation (Demucs) will automatically use ROCm if available. Check GPU visibility with:

```bash
uv run python -c "import torch; print(torch.cuda.is_available())"
```

## Output Structure

Prepared audio and manifests are written to:

```
00-supporting-files/data/transcripts/{source_id}/
├── source-{source_id}-mono16k.wav
├── source-{source_id}-vocal.wav    # optional
└── prep-manifest-{source_id}.json
```