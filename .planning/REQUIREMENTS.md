# Requirements: Project Template Workflow

**Defined:** 2026-02-13
**Core Value:** Every experiment/feature branch is self-documenting from creation — GSD handles branching, worktree setup, README population, and project naming automatically.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Template Preparation

- [x] **TMPL-01**: README template exists on `00-experiments` branch with `$placeholder` variables
- [x] **TMPL-02**: Template includes sections: project name, description, what it does, how to run, status

### Branch & Worktree Creation

- [x] **WKTR-01**: New branch created from `00-experiments` via atomic `git worktree add -b`
- [x] **WKTR-02**: Worktree created in `02-worktrees/<branch-name>`
- [x] **WKTR-03**: Pre-flight check detects duplicate branch or worktree before creation

### File Population

- [x] **FILE-01**: README populated with project context (name, description, purpose)
- [x] **FILE-02**: `pyproject.toml` `name` field updated to match project name
- [x] **FILE-03**: `pyproject.toml` `description` field updated with project description
- [x] **FILE-04**: `uv sync` runs after worktree creation to set up venv

### Root README

- [x] **ROOT-01**: Root repo README on main branch updated to list active experiments/branches

## v2 Requirements

### Workflow Enhancements

- **WKFL-01**: Custom base branch option (not just `00-experiments`)
- **WKFL-02**: Auto-generated table in root README with branch status
- **WKFL-03**: Worktree cleanup/pruning commands
- **WKFL-04**: Stale branch detection
- **WKFL-05**: Branch naming convention enforcement

## Out of Scope

| Feature | Reason |
|---------|--------|
| Shell script wrapper | GSD handles the workflow directly |
| Shared venvs across worktrees | Each worktree gets its own venv from `uv sync` |
| GUI/TUI for worktree management | CLI + GSD is sufficient |
| Auto-merge between experiment branches | Experiments are independent |
| `02-worktrees/README.md` updates | Serves manual users, not GSD workflow |
| Template inheritance/composition | Over-engineering for a personal template |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| TMPL-01 | Phase 1: Template Preparation | Done |
| TMPL-02 | Phase 1: Template Preparation | Done |
| WKTR-01 | Phase 2: Branch Creation Flow | Done |
| WKTR-02 | Phase 2: Branch Creation Flow | Done |
| WKTR-03 | Phase 2: Branch Creation Flow | Done |
| FILE-01 | Phase 2: Branch Creation Flow | Done |
| FILE-02 | Phase 2: Branch Creation Flow | Done |
| FILE-03 | Phase 2: Branch Creation Flow | Done |
| FILE-04 | Phase 2: Branch Creation Flow | Done |
| ROOT-01 | Phase 3: Root README Index | Done |

**Coverage:**
- v1 requirements: 10 total
- Mapped to phases: 10 ✓
- Unmapped: 0
- **Completed: 10/10 ✓**

---
*Requirements defined: 2026-02-13*
*Last updated: 2026-02-13 — all v1 requirements delivered*
