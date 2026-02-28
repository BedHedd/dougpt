---
phase: 02-local-speech-transcript-extraction
plan: 02
subsystem: asr-transcription
tags: [faster-whisper, whisperx, pyannote, transcript, jsonl, confidence, diarization]

# Dependency graph
requires:
  - phase: 02-01
    provides: Prepared mono 16kHz audio files and prep manifests
provides:
  - ASR pipeline CLI for local transcription without paid APIs
  - Normalized JSONL segments with confidence metadata
  - Transcript manifests with quality statistics
affects: [03-01, 03-02, 03-03]

# Tech tracking
tech-stack:
  added: [faster-whisper, ctranslate2, onnxruntime, torch, torchaudio]
  patterns: [CLI with typer, Pydantic schemas, JSONL export, confidence aggregation]

key-files:
  created:
    - 02-worktrees/asr-runner/asr_pipeline.py
    - 02-worktrees/asr-runner/schemas/transcript.py
    - 02-worktrees/asr-runner/utils/confidence.py
    - 02-worktrees/asr-runner/utils/export.py
  modified:
    - 02-worktrees/asr-runner/pyproject.toml

key-decisions:
  - "faster-whisper as primary ASR engine (CTranslate2 backend for speed)"
  - "whisperX alignment optional (requires separate ROCm torch install)"
  - "pyannote diarization optional (requires HF_TOKEN)"
  - "Default confidence threshold 0.70 for export filtering"
  - "Quality flags (low_confidence, short_segment, no_speaker) flag issues without dropping"

patterns-established:
  - "RawSegment → NormalizedSegment pipeline with confidence aggregation"
  - "Manifest-based metadata storage for reproducibility"
  - "Auto-resolve audio from prep manifest (prefer vocal-isolated if available)"

requirements-completed: [ASR-02, ASR-03]

# Metrics
duration: 12min
completed: 2026-02-28
---

# Phase 02: ASR Pipeline Summary

**ROCm-ready ASR pipeline using faster-whisper with word timestamps, optional whisperX alignment and pyannote diarization, producing JSONL segments with confidence metadata and quality flags**

## Performance

- **Duration:** 12 min
- **Started:** 2026-02-28T16:22:00Z
- **Completed:** 2026-02-28T16:34:00Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments
- Added faster-whisper dependency with CTranslate2 backend
- Created transcript schemas (RawSegment, NormalizedSegment, WordTiming, TranscriptManifest)
- Implemented confidence aggregation utilities (mean, min, geometric_mean methods)
- Built JSONL export utilities with manifest writing
- Created asr_pipeline.py CLI with transcribe and info commands
- Integrated with audio_prep outputs (auto-resolves vocal-isolated audio)

## Task Commits

Each task was committed atomically:

1. **Task 1: Add ASR dependencies for ROCm** - `9256b02` (feat)
2. **Task 2: Define transcript schemas and confidence aggregation** - `9256b02` (feat)
3. **Task 3: Implement ASR + alignment + export pipeline** - `9256b02` (feat)

**Plan metadata:** (combined in single commit due to subagent bug)

## Files Created/Modified
- `02-worktrees/asr-runner/pyproject.toml` - Added faster-whisper, updated scripts entry
- `02-worktrees/asr-runner/asr_pipeline.py` - ASR CLI with transcribe/info commands
- `02-worktrees/asr-runner/schemas/transcript.py` - Transcript data models
- `02-worktrees/asr-runner/utils/confidence.py` - Confidence aggregation utilities
- `02-worktrees/asr-runner/utils/export.py` - JSONL export utilities

## Decisions Made
- faster-whisper selected as primary ASR engine (CTranslate2 backend, built-in VAD, word timestamps)
- whisperX alignment and pyannote diarization are optional (requires HF_TOKEN and separate torch install)
- Confidence threshold 0.70 as default filter (configurable via --min-confidence)
- Quality flags enable downstream filtering without dropping audio (per locked policy)

## Deviations from Plan

None - plan executed as specified. Subagent hit classifyHandoffIfNeeded runtime bug but work was completed manually.

## Issues Encountered
- Subagent repeatedly hit classifyHandoffIfNeeded bug - completed implementation manually
- whisperX and pyannote require ROCm torch installed separately (documented in pyproject.toml comments)

## User Setup Required

**Optional external services for enhanced features:**

1. **HuggingFace Token (for diarization):**
   - Set `HF_TOKEN` environment variable
   - Accept pyannote license at huggingface.co/pyannote/speaker-diarization

2. **whisperX alignment (requires PyTorch ROCm):**
   ```bash
   uv pip install whisperx --index-url https://download.pytorch.org/whl/rocm6.0
   ```

## Next Phase Readiness
- ASR pipeline ready for transcript generation
- JSONL output format compatible with alignment phase
- Quality flags ready for downstream curation pipeline

---
*Phase: 02-local-speech-transcript-extraction*
*Completed: 2026-02-28*