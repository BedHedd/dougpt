# Transcripts Directory

This directory stores prepared audio and transcript outputs for the DougDoug ASR pipeline.

## Directory Structure

```
transcripts/
├── {source_id}/                          # One directory per source video
│   ├── source-{source_id}-mono16k.wav    # Demuxed mono 16 kHz audio
│   ├── source-{source_id}-vocal.wav      # Isolated vocals (if isolation triggered)
│   └── prep-manifest-{source_id}.json    # Audio prep metadata
└── README.md                              # This file
```

## File Naming Convention

### Audio Files

- **`source-{source_id}-mono16k.wav`**: The primary demuxed audio file
  - Mono channel
  - 16 kHz sample rate
  - 16-bit PCM WAV format
  - Derived from the original video's audio track

- **`source-{source_id}-vocal.wav`**: Isolated vocals (optional)
  - Same format as mono16k
  - Generated when overlap/music detection triggers vocal isolation
  - Uses Demucs htdemucs model for separation

### Manifest File

- **`prep-manifest-{source_id}.json`**: Metadata for the prep run

## Manifest Schema

```json
{
  "source_id": "VpmmuHlLPM0",
  "source_path": "/path/to/original/video.mp4",
  "output_path": "/path/to/transcripts/VpmmuHlLPM0/source-VpmmuHlLPM0-mono16k.wav",
  "duration_seconds": 3600.5,
  "sample_rate": 16000,
  "channels": 1,
  "channel_map": "mono_demuxed",
  "checksum_sha256": "abc123...",
  "isolation_triggered": true,
  "isolation_method": "demucs_htdemucs",
  "isolation_quality_score": 0.85,
  "overlap_score": 0.45,
  "snr_estimate_db": 18.5,
  "quality_flags": [],
  "run_timestamp": "2026-02-28T22:00:00+00:00",
  "warnings": []
}
```

### Manifest Fields

| Field | Type | Description |
|-------|------|-------------|
| `source_id` | string | Unique identifier for the source |
| `source_path` | string | Original input file path |
| `output_path` | string | Final output audio path (may be vocal-isolated) |
| `duration_seconds` | float | Audio duration in seconds |
| `sample_rate` | int | Sample rate (always 16000) |
| `channels` | int | Number of channels (always 1) |
| `channel_map` | string | Channel mapping description |
| `checksum_sha256` | string | SHA256 checksum of final audio |
| `isolation_triggered` | bool | Whether vocal isolation was run |
| `isolation_method` | string? | Method used for isolation (e.g., "demucs_htdemucs") |
| `isolation_quality_score` | float? | Estimated separation quality (0-1) |
| `overlap_score` | float? | Detected music/overlap score (0-1) |
| `snr_estimate_db` | float? | Estimated signal-to-noise ratio in dB |
| `quality_flags` | string[] | Quality warning flags |
| `run_timestamp` | string | ISO 8601 timestamp of prep run |
| `warnings` | string[] | Any warnings encountered |

### Quality Flags

- `high_overlap`: High detected music/overlap in original audio
- `low_separation_quality`: Vocal isolation produced low-quality results
- `low_snr`: Low signal-to-noise ratio detected

## Usage

### Prepare Audio

```bash
# From the asr-runner worktree
cd 02-worktrees/asr-runner

# Prepare audio from a video file
uv run python audio_prep.py prep \
  --source-id "VpmmuHlLPM0" \
  --input "../../large-files/Doug_Europe_Stream.mp4"

# Force vocal isolation (override detection)
uv run python audio_prep.py prep \
  --source-id "VpmmuHlLPM0" \
  --input "../../large-files/Doug_Europe_Stream.mp4" \
  --force-isolation

# Skip vocal isolation (override detection)
uv run python audio_prep.py prep \
  --source-id "VpmmuHlLPM0" \
  --input "../../large-files/Doug_Europe_Stream.mp4" \
  --skip-isolation
```

### Inspect Prepared Source

```bash
uv run python audio_prep.py info --source-id "VpmmuHlLPM0"
```

### List All Prepared Sources

```bash
uv run python audio_prep.py list-sources
```

## Downstream Usage

Prepared audio files in this directory are inputs to the ASR transcription pipeline:

1. **ASR Transcription**: `source-{source_id}-vocal.wav` (if exists) or `source-{source_id}-mono16k.wav`
2. **Confidence Filtering**: Use `quality_flags` from manifest to filter low-quality segments
3. **Alignment**: Timestamps and confidence metadata feed into alignment pipeline

## Notes

- Files are deterministic: same input produces same output filename
- Re-runs are idempotent with `--overwrite` flag
- Vocal isolation is conditional based on overlap detection
- Raw mono mix is always retained even if isolation runs
- Quality flags enable downstream filtering without dropping audio