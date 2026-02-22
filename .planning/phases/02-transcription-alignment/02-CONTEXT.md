# Phase 2: Transcription & Alignment - Context

**Gathered:** 2026-02-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Process VOD audio through local Whisper to generate word-level transcripts, then align chat messages to transcript windows for downstream training pairs. Videos are already downloaded — this phase handles transcription and alignment only.

</domain>

<decisions>
## Implementation Decisions

### Transcript Output Format
- Both word-level AND segment-level timestamps in output
- Both JSON (for pipelines) + SRT (for human review) formats
- Whisper metadata (confidence, language, model version) in separate sidecar file
- Single transcript file per VOD (not chunked into multiple files)

### Alignment Approach
- Auto-detect chat↔transcript offset automatically (not manual calibration)
- Window-based alignment — chat reacts to Doug with a delay, so align "Doug says X" with "chat responding to Doug"
- Topic matching near timestamp — avoid matching chat from much later in VOD (e.g., 1hr chat shouldn't align to 2min transcript)
- Store alignment data in separate offset file (not inline in chat or transcript)

### Claude's Discretion
- Exact window size for alignment
- Topic matching algorithm/approach
- How to handle edge cases (silence, overlapping speech, missing chat segments)

</decisions>

<specifics>
## Specific Ideas

- Chat has natural delay relative to Doug's speech — alignment must account for this reaction lag
- Topic matching should respect temporal proximity (nearby in time, not just topic similarity)

</specifics>

<deferred>
## Deferred Ideas

- Non-Python runtime choices — future decision
- Cloud ASR providers — out of scope, local Whisper only

</deferred>

---

*Phase: 02-transcription-alignment*
*Context gathered: 2026-02-22*
