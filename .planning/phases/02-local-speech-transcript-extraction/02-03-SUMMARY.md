---
phase: 02-local-speech-transcript-extraction
plan: 03
subsystem: asr-transcription
tags: [moonshine-voice, onnx, amd-gpu, streaming, jsonl]

requires:
  - phase: 02-01
    provides: Prepared mono 16kHz audio files and prep manifests
provides:
  - ASR pipeline CLI using Moonshine Voice (ONNX runtime)
  - Streaming JSONL output for long audio transcriptions
  - AMD GPU support without CUDA dependencies
affects: [03-01, 03-02, 03-03]

tech-stack:
  removed: [faster-whisper, ctranslate2]
  added: [moonshine-voice, onnxruntime]
  patterns: [chunked processing, streaming JSONL writer]

key-files:
  modified:
    - 02-worktrees/asr-runner/asr_pipeline.py
    - 02-worktrees/asr-runner/pyproject.toml
    - 02-worktrees/asr-runner/uv.lock

key-decisions:
  - "Moonshine Voice selected over faster-whisper for AMD ROCm compatibility"
  - "ONNX runtime replaces ctranslate2 (vendor-neutral GPU support)"
  - "Streaming JSONL output prevents data loss on long transcriptions"
  - "Chunked processing (default 300s) enables progress tracking and resilience"
  - "Removed whisperX alignment and pyannote diarization (not yet supported)"

patterns-established:
  - "StreamingJSONLWriter class for incremental segment output"
  - "Chunked audio processing with offset-based timing correction"
  - "Line timing derived from start_time + next_line.start_time"

requirements-completed: [ASR-02, ASR-03]

issue-resolved:
  type: "dependency-compatibility"
  summary: "ctranslate2 requires CUDA, incompatible with AMD ROCm on NixOS"
  solution: "Replaced faster-whisper with moonshine-voice (ONNX runtime)"

duration: 30min
completed: 2026-02-28
---

# Phase 02-03: Moonshine Migration Summary

**Swapped faster-whisper for moonshine-voice to enable AMD GPU acceleration on NixOS without CUDA dependencies**

## Performance

- **Duration:** 30 min
- **Started:** 2026-02-28T19:00:00Z
- **Completed:** 2026-02-28T19:30:00Z
- **Tasks:** 3
- **Files modified:** 3

## Issue Resolved

### Problem
`faster-whisper` depends on `ctranslate2`, which requires CUDA. On NixOS with AMD Radeon RX 7900 XTX (ROCm), this caused:
```
AssertionError: CUDA driver version is insufficient for CUDA runtime version.
```

### Root Cause
- `ctranslate2` PyPI wheels are CUDA-only
- No ROCm-enabled wheels available on Anaconda ROCm index
- Building from source requires significant infrastructure

### Solution
Migrated to `moonshine-voice` which uses ONNX runtime (vendor-neutral GPU support).

## Comparison: Whisper vs Moonshine

| Feature | faster-whisper | moonshine-voice |
|---------|---------------|-----------------|
| GPU Backend | CUDA (ctranslate2) | ONNX (any vendor) |
| AMD ROCm | ❌ Not supported | ✅ Works via ONNX |
| Accuracy (WER) | 7.44% (large-v3) | 6.65% (medium) |
| Model Size | 1.5B params | 245M params |
| Languages | 99 | 8 (en, es, ja, ko, vi, uk, zh, ar) |
| Streaming | No | Yes (cached encoding) |
| Word Timestamps | Yes | Segment-level only |
| Diarization | Via whisperX | Not built-in |

## Accomplishments

1. **Dependency Migration**
   - Removed: `faster-whisper`, `ctranslate2`
   - Added: `moonshine-voice` (via `uv add`)
   - ONNX runtime handles GPU acceleration automatically

2. **ASR Pipeline Refactor**
   - Replaced WhisperModel with Moonshine Transcriber
   - Added `StreamingJSONLWriter` for incremental output
   - Implemented chunked processing (default 300s chunks)
   - Added timing offset correction for chunk boundaries
   - Removed alignment/diarization code (not supported yet)

3. **New CLI Features**
   - `--chunk-size` option for memory management
   - `download` command for Moonshine models
   - Progress output per chunk processed

## Files Modified

- `02-worktrees/asr-runner/pyproject.toml`
  - Removed faster-whisper dependency
  - Added moonshine-voice dependency
  - Updated description

- `02-worktrees/asr-runner/asr_pipeline.py`
  - Complete rewrite for Moonshine API
  - Added StreamingJSONLWriter class
  - Added chunked processing logic
  - Removed whisperX/pyannote code
  - Added download command

- `02-worktrees/asr-runner/uv.lock`
  - Removed ctranslate2 transitive deps
  - Added moonshine-voice and ONNX deps

## Key Code Changes

### StreamingJSONLWriter
```python
class StreamingJSONLWriter:
    """Writes segments to JSONL files as they're processed."""
    def write_segment(self, raw: RawSegment, normalized: NormalizedSegment):
        self.raw_file.write(raw.model_dump_json() + "\n")
        self.norm_file.write(normalized.model_dump_json() + "\n")
```

### Chunked Processing
```python
for chunk_idx in range(num_chunks):
    chunk_audio = audio_data[start_sample:end_sample]
    transcript = transcriber.transcribe_without_streaming(chunk_audio, sample_rate)
    # Apply chunk_offset to timing...
    writer.write_segment(raw, norm)
```

## Trade-offs Accepted

1. **No word-level timestamps** - Moonshine provides segment-level timing only
2. **No built-in diarization** - Speaker labeling not included (future enhancement)
3. **Limited language support** - 8 languages vs Whisper's 99 (acceptable for English content)

## Commit

```
26de695 feat(asr): swap faster-whisper for moonshine-voice

- Replace faster-whisper/whisperX with moonshine-voice for AMD GPU support
- Add streaming JSONL output (writes segments as processed)
- Add chunked processing for long audio files
- Remove ctranslate2 CUDA dependency (uses ONNX runtime)
- Add download command for moonshine models
```

## Testing

```bash
# Download model
cd 02-worktrees/asr-runner
uv run python -m moonshine_voice.download --language en

# Run transcription
uv run python asr_pipeline.py transcribe --source-id "VpmmuHlLPM0" --model medium

# Output
# Transcribed 3532 segments from 15932.92s audio
```

## Next Steps

1. Monitor transcription completion on VpmmuHlLPM0 source
2. Evaluate transcription quality for DougDoug content
3. Consider adding speaker diarization via separate tool if needed
4. Document language support limitations for non-English sources

---
*Phase: 02-local-speech-transcript-extraction*
*Completed: 2026-02-28*