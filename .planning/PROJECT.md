# Project Template Workflow

## What This Is

A personal project template repository that serves as a launchpad for experiments and features. Uses git worktrees for parallel development — each new project branches off `00-experiments`, gets a worktree in `02-worktrees/`, and becomes a self-contained, self-documenting branch with its own README, project name, and dependencies.

## Core Value

Every experiment/feature branch is self-documenting from creation — branching, worktree setup, README population, and project naming happen automatically so you can start building immediately.

## Requirements

### Validated

- ✓ Numbered directory convention for organization — existing
- ✓ Git worktree support via `02-worktrees/` — existing
- ✓ Dev log templates via `00-dev-log/` and Foam — existing
- ✓ Python 3.13 base environment on `00-experiments` branch — existing
- ✓ uv dependency management on `00-experiments` branch — existing
- ✓ Git submodule for dev onboarding — existing
- ✓ Comprehensive Python `.gitignore` — existing

### Active

- [ ] Template README on `00-experiments` branch with placeholder sections for new projects
- [ ] GSD workflow branches from `00-experiments` and creates worktree in `02-worktrees/`
- [ ] GSD populates branch README with project context on new project init
- [ ] GSD updates `pyproject.toml` project name to match the experiment/feature
- [ ] Root repo README updated to reference active branches/experiments

### Out of Scope

- `03-app/` folder — removed; redundant with worktree-based workflow
- CI/CD pipelines — not needed for a personal template repo
- Publishing/packaging — experiments are local, not distributed

## Context

- The `00-experiments` branch is a standalone Python project tree (pyproject.toml, uv.lock, .python-version, sandbox.ipynb) — completely separate from the master branch structure
- `00-experiments` branch already references a README in pyproject.toml but none exists yet
- `03-app/` has been removed — app code lives on feature/experiment branches, not the template
- Current branches: `master`, `vibe-coding`, `worktrees`, `00-experiments`
- The `02-worktrees/` directory contents are gitignored except for its README
- Git submodule `01-dev-onboarding` points to `https://github.com/progressEdd/dev-onboarding.git`

## Constraints

- **Branching model**: All new projects must branch from `00-experiments` to inherit the Python/uv setup
- **Worktree location**: Worktrees live in `02-worktrees/` to keep the root clean
- **Self-contained branches**: Each branch's README must fully describe the project without referencing the template repo

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Removed `03-app/` | Redundant with worktree-based workflow — app code lives on branches | ✓ Good |
| Branch from `00-experiments` not `master` | `00-experiments` has Python/uv setup ready to go; `master` has the template structure | — Pending |
| Keep `02-worktrees/` naming | Consistent with existing numbered directory convention | — Pending |
| Branch README replaces root README per-branch | Each branch should be self-contained and self-documenting | — Pending |

---
*Last updated: 2026-02-13 after initialization*
