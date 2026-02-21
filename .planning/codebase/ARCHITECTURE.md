# Architecture

**Analysis Date:** 2026-02-21

## Pattern Overview

**Overall:** Worktree-oriented template repository with notebook-first experiment execution.

**Key Characteristics:**
- Keep repository-level scaffolding in numbered root directories such as `00-dev-log/`, `00-supporting-files/`, `02-worktrees/`, and `.planning/`.
- Treat each experiment as an isolated Python project in its own worktree under `02-worktrees/<branch>/` (for example `02-worktrees/chat-extraction/`).
- Implement active extraction logic as interactive notebooks and marimo cells instead of package/module layers (`02-worktrees/chat-extraction/chat-extraction.py`, `02-worktrees/chat-extraction/chat-extraction-script.ipynb`).

## Layers

**Repository Orchestration Layer:**
- Purpose: Define branch/worktree workflow and project-planning state.
- Location: `README.md`, `02-worktrees/README.md`, `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`.
- Contains: Workflow rules, phase state, requirements tracking, and manual worktree commands.
- Depends on: Git worktree operations and branch conventions documented in `02-worktrees/README.md`.
- Used by: Humans and GSD automation workflows that initialize and manage experiment branches.

**Experiment Runtime Layer:**
- Purpose: Run branch-local experimental code and model calls.
- Location: `02-worktrees/chat-extraction/chat-extraction.py`, `02-worktrees/chat-extraction/chat-extraction-script.ipynb`, `02-worktrees/chat-extraction/pyproject.toml`.
- Contains: Marimo app cells, OpenAI/LM Studio client setup, Pydantic schemas, image-processing helpers, and extraction prompts.
- Depends on: Local Python environment from `pyproject.toml` and `uv.lock`, plus shared assets from `00-supporting-files/`.
- Used by: Interactive development sessions (marimo/Jupyter) for chat extraction experiments.

**Shared Data and Artifact Layer:**
- Purpose: Store reusable frame/image inputs and extraction outputs.
- Location: `00-supporting-files/data/`, `00-supporting-files/images/`, `00-supporting-files/data/extractions/`.
- Contains: Frame caches, reports, reference images, and JSONL extraction artifacts.
- Depends on: Experiment code in `02-worktrees/chat-extraction/` that reads and writes these artifacts.
- Used by: Notebook/marimo workflows and manual review in `00-dev-log/*.md`.

**Historical/Reference Layer:**
- Purpose: Preserve prior branch trees and research context.
- Location: `02-worktrees/old-master/`, `.planning/research/`, `00-dev-log/`.
- Contains: Older project layouts, architecture research, and chronological investigation notes.
- Depends on: None for runtime behavior; this layer is informational.
- Used by: Future planning and comparison when evolving experiment workflow.

## Data Flow

**Worktree Project Initialization Flow:**

1. Define branch/worktree creation pattern in `02-worktrees/README.md` and planning docs such as `.planning/PROJECT.md`.
2. Create a new experiment worktree under `02-worktrees/<branch>/` from base branch `00-experiments` using the documented `git worktree add` workflow.
3. Populate branch-local metadata (`README.md`, `pyproject.toml`) and sync environment in that worktree (`uv sync` flow documented in `.planning/REQUIREMENTS.md`).

**Chat Extraction Experiment Flow:**

1. Resolve repository-relative paths to `00-supporting-files/` from notebook/marimo code (`02-worktrees/chat-extraction/chat-extraction.py`, `02-worktrees/chat-extraction/chat-extraction-script.ipynb`).
2. Load source frames from `00-supporting-files/data/` and encode images to data URLs in notebook helpers.
3. Send prompts to local model-compatible endpoints via OpenAI-style client calls, validate outputs with Pydantic schemas, and persist extraction artifacts under `00-supporting-files/data/extractions/`.

**State Management:**
- Keep state primarily in files (markdown planning docs, JSON/JSONL artifacts, generated images) rather than in long-lived application services.

## Key Abstractions

**Worktree Instance:**
- Purpose: Represent one independent experiment project with isolated dependencies and docs.
- Examples: `02-worktrees/00-experiments/`, `02-worktrees/chat-extraction/`, `02-worktrees/old-master/`.
- Pattern: One branch per directory under `02-worktrees/`, with branch-local `pyproject.toml`, `uv.lock`, and README.

**Notebook Cell Pipeline:**
- Purpose: Break extraction workflow into composable interactive steps.
- Examples: `02-worktrees/chat-extraction/chat-extraction.py`, `02-worktrees/chat-extraction/chat-extraction-script.ipynb`.
- Pattern: Define data paths, client setup, schema validation, and post-processing in sequential cells.

**Extraction Schema Contract:**
- Purpose: Enforce structure on model outputs.
- Examples: `ChatExtraction`, `ChatMessage`, `EmoteBox` definitions in `02-worktrees/chat-extraction/chat-extraction-script.ipynb` and corresponding commented schema blocks in `02-worktrees/chat-extraction/chat-extraction.py`.
- Pattern: Pydantic models validate and normalize model responses before downstream artifact writing.

## Entry Points

**Repository Workflow Entry:**
- Location: `README.md`.
- Triggers: Initial clone/setup and submodule initialization.
- Responsibilities: Document repository purpose and baseline setup commands.

**Worktree Operations Entry:**
- Location: `02-worktrees/README.md`.
- Triggers: Manual branch/worktree creation and cleanup.
- Responsibilities: Define canonical `git worktree` command patterns.

**Active Experiment Entry:**
- Location: `02-worktrees/chat-extraction/chat-extraction.py`.
- Triggers: Running marimo app cells.
- Responsibilities: Execute interactive extraction experiments and visualize results.

**Batch/Notebook Exploration Entry:**
- Location: `02-worktrees/chat-extraction/chat-extraction-script.ipynb`.
- Triggers: Jupyter notebook execution.
- Responsibilities: Perform batch extraction prompts, schema validation, and helper-driven post-processing.

## Error Handling

**Strategy:** Localized defensive handling inside notebook/marimo cells.

**Patterns:**
- Use path fallback when `__file__` is unavailable (fallback to `Path.cwd()`) in `02-worktrees/chat-extraction/chat-extraction.py` and `02-worktrees/chat-extraction/chat-extraction-script.ipynb`.
- Use schema-validated parsing with fallback JSON extraction in `lmstudio_v1_chat_parse` within `02-worktrees/chat-extraction/chat-extraction-script.ipynb`.

## Cross-Cutting Concerns

**Logging:** Runtime observations are captured in markdown journals under `00-dev-log/` and structured outputs under `00-supporting-files/data/extractions/`.
**Validation:** Structured extraction responses rely on Pydantic model validation in `02-worktrees/chat-extraction/chat-extraction-script.ipynb`.
**Authentication:** External auth wiring is not centralized; local model endpoints are configured inline in experiment notebooks (`02-worktrees/chat-extraction/chat-extraction.py`, `02-worktrees/chat-extraction/chat-extraction-script.ipynb`).

---

*Architecture analysis: 2026-02-21*
