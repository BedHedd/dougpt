# Architecture

**Analysis Date:** 2026-02-26

## Pattern Overview

**Overall:** Schema-centric domain package with artifact-driven workflow architecture.

**Key Characteristics:**
- Keep executable domain code minimal and typed in `src/transcription/models.py`.
- Expose a narrow package API surface from `src/transcription/__init__.py`.
- Drive processing workflow through persisted artifacts in `00-supporting-files/data/` and planning docs in `.planning/`.

## Layers

**Domain Schema Layer:**
- Purpose: Define canonical in-memory structures for transcript and metadata data.
- Location: `src/transcription/models.py`
- Contains: Pydantic `BaseModel` classes (`WordTimestamp`, `TranscriptSegment`, `TranscriptResult`, `TranscriptMetadata`).
- Depends on: `pydantic` (`BaseModel`, `Field`) imported in `src/transcription/models.py`.
- Used by: Package consumers importing from `src/transcription/__init__.py` and pipeline code expected to read/write transcript artifacts.

**Package Boundary Layer:**
- Purpose: Provide stable import surface for transcription types.
- Location: `src/transcription/__init__.py`
- Contains: Re-exports and `__all__` declarations for domain models.
- Depends on: `src.transcription.models`.
- Used by: Any module or notebook importing transcription types from `src.transcription`.

**Artifact Storage Layer:**
- Purpose: Persist pipeline inputs, outputs, logs, and review snapshots on disk.
- Location: `00-supporting-files/data/`
- Contains: Audio samples (`00-supporting-files/data/audio-extraction-review/audio/`), run logs (`00-supporting-files/data/audio-extraction-review/logs/`), run summaries (`00-supporting-files/data/audio-extraction-review/runs/`), transcript JSON (`00-supporting-files/data/audio-extraction-review/transcripts/`), and segment summaries (`00-supporting-files/data/audio-extraction-review/segments/segments.json`).
- Depends on: Filesystem conventions and JSON/JSONL formats.
- Used by: Notebook-based and script-based extraction/transcription workflows.

**Planning and Process Layer:**
- Purpose: Define roadmap, phase plans, and execution context for work.
- Location: `.planning/`
- Contains: State and requirements docs (`.planning/STATE.md`, `.planning/REQUIREMENTS.md`), phased implementation plans (`.planning/phases/`), and codebase mapping outputs (`.planning/codebase/`).
- Depends on: Manual updates and GSD orchestration commands.
- Used by: Contributors and automation processes coordinating implementation phases.

## Data Flow

**Transcription Artifact Flow:**

1. Media and extracted audio references are captured in transcript artifacts such as `00-supporting-files/data/audio-extraction-review/transcripts/sample-single.json` (`source.media_path`, `source.audio_path`).
2. Transcript engine metadata and transcript segments are serialized to JSON artifacts in `00-supporting-files/data/audio-extraction-review/transcripts/` and then summarized into segment-level outputs in `00-supporting-files/data/audio-extraction-review/segments/segments.json`.
3. Run-level operational logs and outcomes are appended to JSONL and JSON records under `00-supporting-files/data/audio-extraction-review/logs/` and `00-supporting-files/data/audio-extraction-review/runs/`.

**State Management:**
- Manage state as file-based artifacts rather than long-lived application state; treat JSON/JSONL files in `00-supporting-files/data/` as the source of truth for run outputs.

## Key Abstractions

**Word-Level Timing Model:**
- Purpose: Represent token timing and optional confidence for aligned transcription words.
- Examples: `src/transcription/models.py` (`WordTimestamp`).
- Pattern: Typed Pydantic model with explicit field descriptions.

**Segment-Level Transcript Model:**
- Purpose: Represent ordered transcript chunks and their nested word timestamps.
- Examples: `src/transcription/models.py` (`TranscriptSegment`).
- Pattern: Composite model that nests `WordTimestamp` in a `list` field.

**Run Transcript Aggregate Model:**
- Purpose: Represent full transcript output for a single audio source.
- Examples: `src/transcription/models.py` (`TranscriptResult`).
- Pattern: Aggregate root model containing segment collection and language metadata.

**Transcript Metadata Model:**
- Purpose: Store sidecar metadata needed for reproducibility.
- Examples: `src/transcription/models.py` (`TranscriptMetadata`).
- Pattern: Flat metadata model carrying model identifiers and execution parameters.

## Entry Points

**Package Import Entry Point:**
- Location: `src/transcription/__init__.py`
- Triggers: `import src.transcription` from notebooks/scripts/modules.
- Responsibilities: Re-export canonical model types and define public API surface via `__all__`.

**Workflow Documentation Entry Point:**
- Location: `README.md`
- Triggers: Repository onboarding and setup activities.
- Responsibilities: Document submodule bootstrap and repository initialization commands.

**Notebook Execution Entry Point (workflow artifact):**
- Location: `02-worktrees/audio-extraction-review/audio-extraction.ipynb`
- Triggers: Manual exploratory execution in the dedicated worktree.
- Responsibilities: Execute end-to-end extraction/review flow outside the main `src/` package.

## Error Handling

**Strategy:** Prefer schema validation and artifact-level status encoding over centralized exception handling.

**Patterns:**
- Validate shape/types at model boundaries with Pydantic models in `src/transcription/models.py`.
- Record fallback reasons and run outcomes directly in output artifacts (for example `diarization.fallback_reason` in `00-supporting-files/data/audio-extraction-review/transcripts/sample-single.json`).

## Cross-Cutting Concerns

**Logging:** Persist operational events to JSONL files in `00-supporting-files/data/audio-extraction-review/logs/`.
**Validation:** Use typed model validation in `src/transcription/models.py` and schema markers (`schema_version`) in JSON artifacts like `00-supporting-files/data/audio-extraction-review/segments/segments.json`.
**Authentication:** No application-level auth layer is implemented in `src/`; environment-based credentials are handled externally, and `00-supporting-files/data/.env` is present for local configuration.

---

*Architecture analysis: 2026-02-26*
