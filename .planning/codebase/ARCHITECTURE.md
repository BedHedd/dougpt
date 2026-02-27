# Architecture

**Analysis Date:** 2026-02-26

## Pattern Overview

**Overall:** Workspace-style research architecture (meta-repo + git worktrees + file-based data pipeline)

**Key Characteristics:**
- Keep shared assets and project governance in repository root (`README.md`, `.gitmodules`, `.gitignore`) and run experiments in isolated worktrees under `02-worktrees/`.
- Drive implementation from notebook and marimo workflows (`02-worktrees/chat-extraction/chat-extraction.py`, `02-worktrees/chat-extraction/*.ipynb`) instead of a package-style `src/` module tree.
- Persist pipeline state as files in `00-supporting-files/data/` (images, reports, JSONL outputs) and use development logs in `00-dev-log/` to document decisions and failure modes.

## Layers

**Workspace Orchestration Layer:**
- Purpose: Define repo operating model, submodule setup, and worktree workflow.
- Location: `README.md`, `.gitmodules`, `.gitignore`, `02-worktrees/README.md`
- Contains: Submodule wiring, git worktree instructions, ignore rules.
- Depends on: Git and local filesystem conventions.
- Used by: All experiment and data workflows.

**Experiment Execution Layer:**
- Purpose: Execute frame extraction, model prompting, and iterative analysis logic.
- Location: `02-worktrees/chat-extraction/chat-extraction.py`, `02-worktrees/chat-extraction/chat-extraction-script.ipynb`, `02-worktrees/chat-extraction/extraction-review.ipynb`, `02-worktrees/00-experiments/sandbox.ipynb`
- Contains: Marimo app cells, notebook exploration, OpenCV/ffmpeg probes, model prompt code.
- Depends on: Python runtime and dependencies declared in `02-worktrees/chat-extraction/pyproject.toml` and `02-worktrees/00-experiments/pyproject.toml`.
- Used by: Manual runs during extraction and evaluation iterations.

**Data Artifact Layer:**
- Purpose: Store reproducible intermediate and output artifacts from extraction runs.
- Location: `00-supporting-files/data/`
- Contains: Frame sets (`00-supporting-files/data/chat_frames_test_30s_color/`), extraction outputs (`00-supporting-files/data/extractions/extractions.jsonl`, `00-supporting-files/data/extractions/metrics.jsonl`, `00-supporting-files/data/extractions/failed_extractions.jsonl`), and run reports (`00-supporting-files/data/chat_frames_test_30s_color/report.json`, `00-supporting-files/data/full_chat_frames_report.json`).
- Depends on: Extraction jobs in `02-worktrees/chat-extraction/chat-extraction.py` and external video files referenced in report JSON.
- Used by: Review notebooks and dev logs.

**Research Traceability Layer:**
- Purpose: Capture rationale, experiments, regressions, and mitigation notes.
- Location: `00-dev-log/*.md`
- Contains: Daily entries, screenshots, command snippets, observed model behavior.
- Depends on: Outputs from `00-supporting-files/images/` and `00-supporting-files/data/`.
- Used by: Human planning and phase scoping.

## Data Flow

**Chat Extraction Pipeline:**

1. Locate project roots and data directories in `02-worktrees/chat-extraction/chat-extraction.py` by resolving `00-supporting-files` and `large-files` parents.
2. Generate or reference frame artifacts and frame-selection reports under `00-supporting-files/data/chat_frames_test_30s_color/` and `00-supporting-files/data/full_chat_frames_report.json`.
3. Send frame content to local or OpenAI-compatible model endpoints in `02-worktrees/chat-extraction/chat-extraction.py` and serialize parsed chat outputs to `00-supporting-files/data/extractions/extractions.jsonl` with metrics in `00-supporting-files/data/extractions/metrics.jsonl`.

**State Management:**
- Use filesystem-backed state only (JSON, JSONL, PNG) in `00-supporting-files/data/`; no database, queue, or persistent service layer is detected.

## Key Abstractions

**Path Discovery Abstraction:**
- Purpose: Make notebooks/worktrees relocatable by deriving the canonical project data path at runtime.
- Examples: `02-worktrees/chat-extraction/chat-extraction.py`, `02-worktrees/old-master/02-development/chat-extraction/chat-extraction.py`
- Pattern: Walk upward from current file/cwd until `00-supporting-files` exists, then derive sibling paths.

**Frame Artifact Abstraction:**
- Purpose: Represent sampled chat states as deterministic files tied to timestamp and frame index.
- Examples: `00-supporting-files/data/chat_frames_test_30s_color/frame_000023_t000007.667.png`, `00-supporting-files/data/chat_frames_test_30s_color/report.json`
- Pattern: Use filename schema `frame_{index}_t{seconds}.png` and pair with report metadata containing `corr`, `dy_step_px`, and `saved_path`.

**Extraction Record Abstraction:**
- Purpose: Represent OCR/VLM output and run telemetry separately for downstream analysis.
- Examples: `00-supporting-files/data/extractions/extractions.jsonl`, `00-supporting-files/data/extractions/metrics.jsonl`
- Pattern: Keep semantic chat output and operational metrics in separate append-friendly JSONL files.

## Entry Points

**Repository Entry:**
- Location: `README.md`
- Triggers: Developer onboarding in repository root.
- Responsibilities: Explain clone/submodule setup and base repo purpose.

**Worktree Workflow Entry:**
- Location: `02-worktrees/README.md`
- Triggers: Creating and managing isolated branches for experiments.
- Responsibilities: Define git worktree commands and expected directory model.

**Primary Execution Entry:**
- Location: `02-worktrees/chat-extraction/chat-extraction.py`
- Triggers: Running marimo app in the `chat-extraction` worktree.
- Responsibilities: Orchestrate path resolution, frame-level experiments, model requests, and structured extraction trials.

## Error Handling

**Strategy:** Interactive recovery and artifact inspection.

**Patterns:**
- Check subprocess results and stderr directly in notebook/app cells (for example ffmpeg invocation paths in `02-worktrees/chat-extraction/chat-extraction.py`).
- Capture failed extraction metadata into dedicated files (`00-supporting-files/data/extractions/failed_extractions.jsonl`) and document root-cause analysis in `00-dev-log/2026-02-09.md`.

## Cross-Cutting Concerns

**Logging:** File-first logs through `00-dev-log/*.md` and JSONL metrics in `00-supporting-files/data/extractions/metrics.jsonl`.
**Validation:** Use schema-oriented parsing patterns in marimo extraction code (`pydantic` models in `02-worktrees/chat-extraction/chat-extraction.py`) and strict JSON-oriented prompts captured in `00-dev-log/2026-02-09.md`.
**Authentication:** Load environment config in experiment code (`dotenv` import in `02-worktrees/chat-extraction/chat-extraction.py`); keep env values outside committed code (for example `.env` exists at `00-supporting-files/data/.env`).

---

*Architecture analysis: 2026-02-26*
