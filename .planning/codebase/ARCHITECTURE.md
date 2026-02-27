# Architecture

**Analysis Date:** 2026-02-26

## Pattern Overview

**Overall:** Hybrid notebook-orchestrated pipeline with a small typed domain package.

**Key Characteristics:**
- Pipeline orchestration logic is implemented in a single notebook at `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.
- Reusable typed transcript schemas are centralized in `src/transcription/models.py` and re-exported by `src/transcription/__init__.py`.
- Durable pipeline artifacts are written to filesystem data folders under `00-supporting-files/data/audio-extraction-review/`.

## Layers

**Domain Schema Layer:**
- Purpose: Define validated transcript and metadata contracts.
- Location: `src/transcription/models.py`
- Contains: Pydantic `BaseModel` classes (`WordTimestamp`, `TranscriptSegment`, `TranscriptResult`, `TranscriptMetadata`).
- Depends on: `pydantic.BaseModel` and `pydantic.Field` from `src/transcription/models.py`.
- Used by: External callers importing from `src/transcription/__init__.py` and notebook/prototype code consuming transcript artifacts.

**Package API Layer:**
- Purpose: Provide stable import surface for transcription model types.
- Location: `src/transcription/__init__.py`
- Contains: Re-exports plus `__all__` public API list.
- Depends on: `src.transcription.models`.
- Used by: Any code importing `src.transcription` instead of deep module paths.

**Pipeline Orchestration Layer:**
- Purpose: Run stage-based processing (extract -> transcribe -> segment -> export).
- Location: `02-worktrees/audio-extraction-review/audio-extraction.ipynb`
- Contains: Config map, stage functions, run coordination (`run_pipeline`), and execution cells.
- Depends on: Filesystem paths resolved from `00-supporting-files/`, local binaries (ffmpeg/ffprobe), and local model endpoints configured in notebook config.
- Used by: Manual notebook execution.

**Artifact Storage Layer:**
- Purpose: Persist run logs, transcripts, segments, and run metadata as local files.
- Location: `00-supporting-files/data/audio-extraction-review/`
- Contains: `audio/`, `logs/`, `runs/`, `segments/`, `transcripts/` artifacts.
- Depends on: Pipeline writing JSON/JSONL/Markdown outputs.
- Used by: Subsequent reruns, review workflows, and offline analysis.

## Data Flow

**Audio Extraction Review Flow:**

1. `run_pipeline` in `02-worktrees/audio-extraction-review/audio-extraction.ipynb` resolves project paths and input media (`resolve_project_paths`, `discover_inputs`).
2. Extraction stage writes normalized audio artifacts and extraction logs under `00-supporting-files/data/audio-extraction-review/audio/` and `00-supporting-files/data/audio-extraction-review/logs/`.
3. Transcription stage produces transcript JSON artifacts in `00-supporting-files/data/audio-extraction-review/transcripts/` and stage logs in `00-supporting-files/data/audio-extraction-review/logs/`.
4. Segmentation stage optionally calls a local model endpoint, validates segment chronology, and builds segment records in memory.
5. Export stage writes `segments.json` and `segments.md` in `00-supporting-files/data/audio-extraction-review/segments/`.
6. Run metadata stage writes final run snapshot JSON to `00-supporting-files/data/audio-extraction-review/runs/`.

**State Management:**
- State is file-backed and run-scoped: runtime dictionaries are ephemeral, while durable state is appended or written to artifact files in `00-supporting-files/data/audio-extraction-review/`.

## Key Abstractions

**Transcript Schema Models:**
- Purpose: Represent typed ASR output and metadata with validation.
- Examples: `src/transcription/models.py`
- Pattern: Pydantic models with explicit fields, defaults, and descriptions.

**Stage Functions:**
- Purpose: Isolate pipeline responsibilities by stage.
- Examples: `run_extraction_stage`, `run_transcription_stage`, `run_segmentation_stage`, `run_segment_export_stage` in `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.
- Pattern: Pure-ish functions receiving config/paths/run_id and returning structured stage payloads (`records`, `failures`, `duration_seconds`).

**Artifact Contracts:**
- Purpose: Preserve reproducible outputs and resumability across runs.
- Examples: `00-supporting-files/data/audio-extraction-review/runs/run-*.json`, `00-supporting-files/data/audio-extraction-review/logs/*.jsonl`, `00-supporting-files/data/audio-extraction-review/segments/segments.json`.
- Pattern: JSON/JSONL/Markdown outputs keyed by run ID and stage.

## Entry Points

**Notebook Orchestration Entry Point:**
- Location: `02-worktrees/audio-extraction-review/audio-extraction.ipynb`
- Triggers: Manual execution of notebook cells (`RUN_RESULT = run_pipeline(RUN_CONFIG)`).
- Responsibilities: End-to-end media discovery, extraction, transcription, segmentation, export, and run metadata writing.

**Package Import Entry Point:**
- Location: `src/transcription/__init__.py`
- Triggers: Python imports (`from src.transcription import TranscriptResult`).
- Responsibilities: Expose stable model API without requiring deep-module imports.

## Error Handling

**Strategy:** Stage-local failure capture with non-destructive continuation and persisted failure details.

**Patterns:**
- Stage functions return structured `failures` arrays instead of raising unhandled exceptions as the only mechanism (notebook pipeline functions in `02-worktrees/audio-extraction-review/audio-extraction.ipynb`).
- Smoke-check gating short-circuits segmentation and records actionable guidance (`local_model_smoke_check`, `build_segmentation_guidance` in `02-worktrees/audio-extraction-review/audio-extraction.ipynb`).

## Cross-Cutting Concerns

**Logging:** JSONL append-based logging via helper functions in `02-worktrees/audio-extraction-review/audio-extraction.ipynb`, persisted under `00-supporting-files/data/audio-extraction-review/logs/`.
**Validation:** Schema validation for transcript models in `src/transcription/models.py` plus segment normalization/validation routines in `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.
**Authentication:** No centralized application auth layer detected; notebook config includes local endpoint/API key parameters for segmentation in `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.

---

*Architecture analysis: 2026-02-26*
