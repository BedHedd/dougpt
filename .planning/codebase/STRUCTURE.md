# Codebase Structure

**Analysis Date:** 2026-02-21

## Directory Layout

```text
[project-root]/
├── .planning/                    # Planning, roadmap, phase docs, and generated codebase maps
├── 00-dev-log/                   # Date-based engineering notes and debugging logs
├── 00-supporting-files/          # Shared data/images/artifacts used by experiments
├── 01-dev-onboarding/            # Git submodule mount point (currently empty here)
├── 02-worktrees/                 # Git worktree directories for branch-isolated experiments
├── .foam/                        # Foam note templates
├── .gitmodules                   # Submodule declaration for `01-dev-onboarding/`
├── .gitignore                    # Root ignore policy (includes worktree content ignore)
└── README.md                     # Root repository orientation and setup
```

## Directory Purposes

**`.planning/`:**
- Purpose: Keep project state, requirements, roadmap, research, and machine-generated architecture docs.
- Contains: `PROJECT.md`, `REQUIREMENTS.md`, `ROADMAP.md`, `STATE.md`, `.planning/phases/`, `.planning/research/`, `.planning/codebase/`.
- Key files: `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`.

**`00-dev-log/`:**
- Purpose: Track chronological work notes and experiments.
- Contains: Daily markdown files named by date and a template.
- Key files: `00-dev-log/00-template.md`, `00-dev-log/2026-02-09.md`.

**`00-supporting-files/`:**
- Purpose: Hold shared inputs/outputs for extraction experiments.
- Contains: `data/` frame caches/reports/jsonl outputs and `images/` dated image snapshots.
- Key files: `00-supporting-files/data/extractions/extractions.jsonl`, `00-supporting-files/data/full_chat_frames_report.json`, `00-supporting-files/data/sample.env.file`.

**`02-worktrees/`:**
- Purpose: Store per-branch worktrees as independent project roots.
- Contains: Experiment worktrees (`00-experiments/`, `chat-extraction/`) and historical branch snapshot (`old-master/`).
- Key files: `02-worktrees/README.md`, `02-worktrees/chat-extraction/pyproject.toml`, `02-worktrees/chat-extraction/chat-extraction.py`.

**`01-dev-onboarding/`:**
- Purpose: Reserved path for the `01-dev-onboarding` git submodule declared in `.gitmodules`.
- Contains: Not detected in this checkout (empty directory state).
- Key files: `.gitmodules` (source of truth for this mapping).

## Key File Locations

**Entry Points:**
- `README.md`: Root clone/setup guidance and high-level project framing.
- `02-worktrees/README.md`: Operational entry for worktree lifecycle commands.
- `02-worktrees/chat-extraction/chat-extraction.py`: Marimo app entry for extraction experiments.
- `02-worktrees/chat-extraction/chat-extraction-script.ipynb`: Notebook entry for iterative/batch extraction experiments.

**Configuration:**
- `.gitignore`: Repository-wide ignore rules and worktree-ignore behavior.
- `.gitmodules`: Submodule definition for `01-dev-onboarding`.
- `.planning/config.json`: Planning system configuration.
- `02-worktrees/chat-extraction/pyproject.toml`: Active experiment dependency/runtime metadata.
- `02-worktrees/00-experiments/pyproject.toml`: Base branch dependency/runtime metadata.

**Core Logic:**
- `02-worktrees/chat-extraction/chat-extraction.py`: Interactive extraction cells, model calls, and prompt experiments.
- `02-worktrees/chat-extraction/chat-extraction-script.ipynb`: Helper functions, schema validation, and extraction pipeline experiments.

**Testing:**
- Not detected (no `tests/` directory or test configuration files in this checkout).

## Naming Conventions

**Files:**
- Use markdown planning/log files in uppercase or date-oriented names (examples: `.planning/PROJECT.md`, `00-dev-log/2026-02-09.md`).
- Use hyphenated names for experiment scripts/notebooks (examples: `02-worktrees/chat-extraction/chat-extraction.py`, `02-worktrees/chat-extraction/chat-extraction-script.ipynb`).

**Directories:**
- Use numbered prefixes for top-level organizational buckets (examples: `00-dev-log/`, `00-supporting-files/`, `01-dev-onboarding/`, `02-worktrees/`).
- Use branch-like names for worktree subdirectories (examples: `02-worktrees/00-experiments/`, `02-worktrees/chat-extraction/`).

## Where to Add New Code

**New Feature:**
- Primary code: Create a new worktree directory under `02-worktrees/<new-branch>/` and place implementation files there.
- Tests: Add tests inside that worktree root (for example `02-worktrees/<new-branch>/tests/`) because no shared root test harness exists.

**New Component/Module:**
- Implementation: Place module code in the active experiment worktree (for example `02-worktrees/chat-extraction/`) alongside its `pyproject.toml`.

**Utilities:**
- Shared helpers: Put reusable dataset/asset artifacts in `00-supporting-files/data/` and reference them from worktree code.

## Special Directories

**`02-worktrees/`:**
- Purpose: Container for branch-linked worktrees used for parallel development.
- Generated: Yes (directories are created/managed through git worktree operations).
- Committed: Partially (directory + `02-worktrees/README.md` are committed; most child worktree contents are ignored by root `.gitignore`).

**`.planning/codebase/`:**
- Purpose: Generated architecture/convention maps consumed by GSD planning and execution commands.
- Generated: Yes.
- Committed: Yes (intended documentation artifacts).

**`00-supporting-files/data/extractions/`:**
- Purpose: Persist extraction outputs and run metrics as JSONL artifacts.
- Generated: Yes.
- Committed: Yes in this checkout state.

---

*Structure analysis: 2026-02-21*
