# Codebase Structure

**Analysis Date:** 2026-02-26

## Directory Layout

```text
[project-root]/
├── 00-dev-log/                    # Dated research and progress notes
├── 00-supporting-files/           # Data artifacts and image snapshots
├── 01-dev-onboarding/             # Git submodule slot (currently not populated)
├── 02-worktrees/                  # Active and archived experimental worktrees
├── .planning/codebase/            # GSD codebase mapping docs
├── README.md                      # Repo-level onboarding and purpose
├── .gitmodules                    # Submodule configuration
└── .gitignore                     # Root ignore policy (includes worktree content)
```

## Directory Purposes

**00-dev-log:**
- Purpose: Maintain chronological engineering notes and experiment outcomes.
- Contains: Daily markdown files and an entry template.
- Key files: `00-dev-log/00-template.md`, `00-dev-log/2026-02-09.md`, `00-dev-log/2026-01-18.md`

**00-supporting-files:**
- Purpose: Store all durable artifacts used by experiments.
- Contains: `data/` for extraction inputs/outputs and `images/` for manual snapshots.
- Key files: `00-supporting-files/data/full_chat_frames_report.json`, `00-supporting-files/data/chat_frames_test_30s_color/report.json`, `00-supporting-files/data/extractions/extractions.jsonl`

**01-dev-onboarding:**
- Purpose: Submodule mount point for onboarding materials.
- Contains: Gitlink path only in current checkout.
- Key files: `.gitmodules`, `README.md`

**02-worktrees:**
- Purpose: Isolate branch-specific experiments from root workspace.
- Contains: Multiple worktree directories, each with its own Python project/notebooks.
- Key files: `02-worktrees/README.md`, `02-worktrees/chat-extraction/chat-extraction.py`, `02-worktrees/00-experiments/pyproject.toml`, `02-worktrees/old-master/02-development/chat-extraction/chat-extraction.py`

**.planning/codebase:**
- Purpose: Store architecture/quality/stack maps for GSD planning and execution.
- Contains: Mapper-generated markdown documents.
- Key files: `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STRUCTURE.md`

## Key File Locations

**Entry Points:**
- `README.md`: Root onboarding and repository intent.
- `02-worktrees/README.md`: Worktree lifecycle commands and conventions.
- `02-worktrees/chat-extraction/chat-extraction.py`: Primary runnable marimo experiment app.

**Configuration:**
- `.gitmodules`: Submodule path and remote definition.
- `.gitignore`: Root-wide ignore rules, including `02-worktrees/*` content policy.
- `02-worktrees/chat-extraction/pyproject.toml`: Dependencies for extraction worktree.
- `02-worktrees/00-experiments/pyproject.toml`: Dependencies for sandbox worktree.

**Core Logic:**
- `02-worktrees/chat-extraction/chat-extraction.py`: Frame extraction, model prompting, structured output experiments.
- `02-worktrees/old-master/02-development/chat-extraction/chat-extraction.py`: Legacy snapshot of the same workflow in prior layout.

**Testing:**
- Not detected (no committed `tests/` directory, `*.test.*`, or `*.spec.*` files in the analyzed tracked structure).

## Naming Conventions

**Files:**
- Use numeric prefixes to encode top-level intent (`00-dev-log`, `00-supporting-files`, `01-dev-onboarding`, `02-worktrees`).
- Name daily logs as ISO dates (`00-dev-log/2026-02-09.md`).
- Name extracted frames with index and timestamp (`00-supporting-files/data/chat_frames_test_30s_color/frame_000053_t000017.667.png`).

**Directories:**
- Use kebab-case for feature/worktree directories (`02-worktrees/chat-extraction`, `02-worktrees/extraction-exploration`).
- Group artifacts by domain (`00-supporting-files/data/extractions`, `00-supporting-files/data/chat_frames_test_30s_color`).

## Where to Add New Code

**New Feature:**
- Primary code: Add to a dedicated worktree directory under `02-worktrees/<feature-name>/` with a local `pyproject.toml`.
- Tests: Add `tests/` under the same worktree directory (for example `02-worktrees/<feature-name>/tests/`) since no shared root testing harness is present.

**New Component/Module:**
- Implementation: Place implementation in the relevant worktree root (for example `02-worktrees/chat-extraction/`) and keep data products in `00-supporting-files/data/<new-artifact-group>/`.

**Utilities:**
- Shared helpers: If reusable across experiments, add a small utility module in the active worktree first (for example `02-worktrees/chat-extraction/utils.py`), then promote only stable utilities to a dedicated shared directory at root (for example `02-development/` when that tree exists in active branch).

## Special Directories

**02-worktrees:**
- Purpose: Parallel branch workspaces with independent files and environments.
- Generated: Partially (directory tracked; contents mostly excluded by root `.gitignore`).
- Committed: `02-worktrees/README.md` is committed; most branch worktree contents are intentionally not committed in root.

**00-supporting-files/data:**
- Purpose: Durable extraction inputs/outputs and reports.
- Generated: Yes.
- Committed: Yes (reports and extraction outputs are present in repository).

**.venv:**
- Purpose: Local Python environment.
- Generated: Yes.
- Committed: No (ignored via `.gitignore`).

---

*Structure analysis: 2026-02-26*
