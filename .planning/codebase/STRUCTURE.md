# Codebase Structure

**Analysis Date:** 2026-02-26

## Directory Layout

```text
dougpt/
├── src/                     # Primary Python source package(s)
├── 00-supporting-files/     # Data artifacts, media, and review outputs
├── .planning/               # Planning docs, phase plans, and codebase maps
├── 00-dev-log/              # Date-based development journal entries
├── 02-worktrees/            # Git worktree area for parallel experiments
├── 01-dev-onboarding/       # Git submodule path (currently empty until init)
├── .foam/                   # Note templates for dev logging workflow
├── .gitmodules              # Submodule declarations
├── .gitignore               # Ignore rules including worktree content policy
└── README.md                # Repository onboarding and setup
```

## Directory Purposes

**src:**
- Purpose: Hold production Python modules and shared domain types.
- Contains: `transcription/` package with model definitions and package API export.
- Key files: `src/transcription/models.py`, `src/transcription/__init__.py`.

**00-supporting-files:**
- Purpose: Store working datasets and generated artifacts used by pipeline experimentation/review.
- Contains: `data/` (JSON, JSONL, images, audio, frame caches) and `images/` snapshots.
- Key files: `00-supporting-files/data/audio-extraction-review/transcripts/sample-single.json`, `00-supporting-files/data/audio-extraction-review/segments/segments.json`, `00-supporting-files/data/extractions/extractions.jsonl`.

**.planning:**
- Purpose: Centralize project requirements, roadmap, phases, and mapping outputs.
- Contains: Global planning docs, phase folders, and `.planning/codebase/` reference docs.
- Key files: `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/phases/02-transcription-alignment/02-01-PLAN.md`.

**00-dev-log:**
- Purpose: Capture periodic progress notes in markdown.
- Contains: Date-named markdown files and template file.
- Key files: `00-dev-log/00-template.md`, `00-dev-log/2026-02-09.md`.

**02-worktrees:**
- Purpose: Isolate branch-specific experiments in separate git worktrees.
- Contains: `README.md` tracked in main repo; worktree contents ignored by root `.gitignore` except explicitly tracked files.
- Key files: `02-worktrees/README.md`, `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.

## Key File Locations

**Entry Points:**
- `README.md`: Repository bootstrap and submodule initialization entry point.
- `src/transcription/__init__.py`: Python package import entry point for transcription models.
- `02-worktrees/audio-extraction-review/audio-extraction.ipynb`: Notebook execution entry point for extraction review workflow.

**Configuration:**
- `.gitignore`: Ignore strategy for environments, caches, worktrees, and generated files.
- `.gitmodules`: Submodule configuration for `01-dev-onboarding`.
- `.planning/config.json`: Planning system configuration.

**Core Logic:**
- `src/transcription/models.py`: Canonical typed models for transcript structures.

**Testing:**
- Not detected in current tracked tree (`*.test.*`, `*.spec.*`, `tests/` are not present).

## Naming Conventions

**Files:**
- `snake_case.py` for Python modules: `src/transcription/models.py`.
- Date-stamped markdown notes `YYYY-MM-DD.md`: `00-dev-log/2026-02-01.md`.
- Pipeline artifact files with semantic suffixes: `run-<timestamp>-<id>.json` in `00-supporting-files/data/audio-extraction-review/runs/`.

**Directories:**
- Numeric prefixes for top-level purpose ordering: `00-supporting-files/`, `01-dev-onboarding/`, `02-worktrees/`.
- Domain-first package naming under `src/`: `src/transcription/`.

## Where to Add New Code

**New Feature:**
- Primary code: Add package/module code under `src/` (for transcription-related logic, place in `src/transcription/`).
- Tests: Create `tests/` at repository root (for example `tests/transcription/`) because no existing test directory is present.

**New Component/Module:**
- Implementation: Add new Python module alongside related package files, for example `src/transcription/<component>.py`, and export public types/functions from `src/transcription/__init__.py` if part of public API.

**Utilities:**
- Shared helpers: Add shared helper modules under `src/` in a dedicated package (for example `src/common/` or `src/transcription/utils.py`) and keep notebook-only utilities inside `02-worktrees/` worktrees when they are experimental.

## Special Directories

**02-worktrees/:**
- Purpose: Hold branch-specific isolated working directories.
- Generated: Yes (directories are created via `git worktree add`).
- Committed: Partially; only selected files like `02-worktrees/README.md` (and explicitly tracked exceptions) are committed from the main repo.

**01-dev-onboarding/:**
- Purpose: Submodule mount path for onboarding content.
- Generated: Yes (materialized when submodule is initialized).
- Committed: Yes as a gitlink/submodule reference declared in `.gitmodules`.

**00-supporting-files/data/:**
- Purpose: Persist intermediate and output artifacts from extraction/transcription workflows.
- Generated: Yes for most files (runs, logs, extracted media derivatives).
- Committed: Mixed; many artifacts are currently tracked, and local secrets file `00-supporting-files/data/.env` exists but is ignored.

---

*Structure analysis: 2026-02-26*
