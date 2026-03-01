# Phase 2: Local Speech Transcript Extraction - Context

**Gathered:** 2026-02-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Generate DougDoug-only, timestamped, normalized speech transcripts locally (no paid APIs). Outputs must include confidence metadata for downstream alignment.

</domain>

<decisions>
## Implementation Decisions

### Transcript granularity & normalization
- Segment by natural phrases/sentences, keep per-word timestamps inside each segment; target segment length ~8–12 seconds.
- Normalize text to sentence case with punctuation; retain fillers as spoken but tag non-speech sounds inline (e.g., [laughter]/[music]/[noise]).

### Voice isolation policy
- Start from demuxed audio; run vocal isolation only when music/overlap is detected.
- Tag non-Doug segments instead of dropping; include speaker labels for later filtering.
- Apply light music/SFX reduction only when present; flag low-quality/separation-poor segments for review instead of auto-dropping.

### Confidence metadata & filtering
- Store per-word and per-segment confidence scores; include ASR logprobs plus VAD/overlap flags.
- Default export only for segments with confidence >= 0.70.
- If a segment contains low-confidence spans, keep the segment but flag the questionable words/spans.

### Export format & storage
- Export as JSONL (one segment per line).
- Store under `00-supporting-files/data/transcripts/{source_id}/`.
- Each record should include raw and normalized text, start/end timestamps, speaker label, per-word and per-segment confidences, logprobs/VAD/overlap flags, and quality flags.
- Keep raw and normalized versions side-by-side for traceability.

### Claude's Discretion
- Exact field names/schema shape within the JSONL records.
- How to score/flag low-quality separation and VAD/overlap heuristics.
- When to trigger optional vocal isolation based on detected music/overlap.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- Path discovery pattern (`supporting_files`, `project_parent`) in `02-worktrees/chat-extraction/chat-extraction.py` for locating `00-supporting-files` and `large-files`.
- File-first data artifacts in `00-supporting-files/data/` with JSONL outputs (e.g., extractions/metrics) and Pydantic-style validation in marimo cells.
- OpenAI-compatible local client setup in `02-worktrees/chat-extraction/chat-extraction.py` (points to `http://localhost:1234/v1`).
- ffmpeg usage patterns in marimo cells for demuxing/inspection and OpenCV probes for video/audio handling.

### Established Patterns
- Store run artifacts under `00-supporting-files/data/` with deterministic filenames and JSON/JSONL structures.
- Use marimo notebooks/scripts inside `02-worktrees/` with in-cell imports and helper functions; no central `src/` package or test suite.
- Environment variables loaded via `python-dotenv` with `.env` under `00-supporting-files/data/`.

### Integration Points
- New ASR runner can live in a dedicated worktree (e.g., `02-worktrees/<asr-runner>/`) with its own `pyproject.toml`; keep outputs in `00-supporting-files/data/transcripts/{source_id}/` alongside existing artifacts.
- Follow existing path resolution helpers so scripts remain relocatable across worktrees.
- Dependency management via `uv` and Python 3.13.x; ROCm GPU environment available.

</code_context>

<specifics>
## Specific Ideas

- Evaluate additional Whisper endpoints: moonshine (https://github.com/moonshine-ai/moonshine) and whisper.cpp (https://github.com/ggml-org/whisper.cpp).
- Use `uv add` for dependencies with ROCm wheels from the PyTorch ROCm index; prior working `pyproject.toml` includes faster-whisper, whisperx, torch/vision/audio with `pytorch-rocm` index and `pytorch-triton-rocm`.
- Keep ROCm GPU as the target acceleration environment.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-local-speech-transcript-extraction*
*Context gathered: 2026-02-28*
