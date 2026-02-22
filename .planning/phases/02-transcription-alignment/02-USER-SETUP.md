# Phase 2: User Setup Required

**Generated:** 2026-02-22
**Phase:** 02-transcription-alignment
**Status:** Incomplete

Complete these items for local transcription acceleration support.

## Environment Variables

None.

## Account Setup

None.

## Dashboard Configuration

None.

## Local Environment Setup

- [ ] **Install and verify local Whisper model runtime**
  - Action: Run transcription once so Whisper/WhisperX downloads required local model artifacts.
  - Notes: First run may take several minutes depending on model size.

- [ ] **Confirm CUDA availability for GPU acceleration (optional but recommended)**
  - Action: Ensure NVIDIA drivers/CUDA runtime are available and your Python environment can access GPU.
  - Notes: CPU fallback works, but transcription will be slower.

## Verification

After setup, verify with:

```bash
cd 02-worktrees/phase2-transcription-alignment
uv run python -c "import whisperx; print('whisperx available')"
```

Expected results:
- Command prints `whisperx available` without import errors.

---

**Once all items complete:** Mark status as "Complete" at top of file.
