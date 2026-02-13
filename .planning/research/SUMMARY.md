# Project Research Summary

**Project:** Project Template Workflow
**Domain:** Git worktree-based project automation (developer tooling)
**Researched:** 2026-02-13
**Confidence:** HIGH

## Executive Summary

This project automates the creation of self-contained experiment/feature branches from a shared Python base environment (`00-experiments`), using git worktrees for parallel development. The domain is well-understood: git worktree operations, stdlib file templating, and targeted TOML editing. Every technology choice has been verified against official docs and the live repo — there are no unknowns in the stack. The entire automation is ~8 commands with zero external dependencies.

The recommended approach is **GSD-inline automation** — no shell scripts, no CLI frameworks, no libraries. The GSD orchestrator executes git commands via subprocess, edits files with `re.sub()` and `string.Template`, and commits. The workflow is: fetch → pre-flight checks → atomic branch+worktree creation → populate README → rename pyproject.toml → `uv sync` → commit. This is a single-invocation flow that produces a ready-to-code worktree.

The primary risks are operational, not technical: (1) the git worktree + submodule incompatibility bug (mitigated by always branching from `00-experiments` which has no submodules), (2) clobbering user edits on re-run (mitigated by sentinel-based idempotency checks), and (3) the cross-branch root README update (architecturally tricky — defer to a later phase). None of these are blockers; all have clear prevention strategies documented in the research.

## Key Findings

### Recommended Stack

**Zero dependencies.** Python 3.13 stdlib + git CLI covers everything. No pip/uv installs needed for the automation itself.

**Core technologies:**
- **`subprocess.run()` + git CLI:** Branch/worktree creation, validation, cleanup — git's porcelain output gives machine-parseable data. GitPython is in maintenance mode and doesn't wrap worktree commands well.
- **`re.sub()`:** Single-field `pyproject.toml` name replacement — preserves all formatting. tomlkit is overkill; tomli-w destroys formatting on round-trip.
- **`string.Template.safe_substitute()`:** README placeholder population — `$variable` syntax has zero conflicts with Markdown. Jinja2's `{{ }}` conflicts with code blocks.
- **`pathlib.Path`:** File I/O — modern, cross-platform, stdlib.
- **`tomllib`:** Optional post-edit TOML validation (read-only, stdlib since 3.11).

**What NOT to use:** GitPython (maintenance mode), Cookiecutter/Copier (wrong scope), tomli-w for edits (destroys formatting), Click/Typer (GSD is the CLI), pre-commit hooks (wrong trigger).

### Expected Features

**Must have (table stakes):**
- **T1+T2: Atomic branch + worktree creation** — single `git worktree add -b` command from `00-experiments`
- **T3: README template on `00-experiments`** — `$placeholder` syntax with sentinel comment for idempotency
- **T4: README population** — `string.Template.safe_substitute()` with project name, description, branch, date
- **T5: pyproject.toml name update** — `re.sub()` to replace `"template-repo"` with project name

**Should have (promoted differentiators):**
- **D3: Duplicate branch/worktree detection** — pre-flight `git worktree list --porcelain` check. Prevents confusing git fatal errors.
- **D2: `uv sync` post-creation** — prevents the most common failure (missing `.venv`, `ModuleNotFoundError` on first use)

**Defer (v2+):**
- **D1: Root README auto-update** — requires cross-branch editing (master ← feature branch). Architecturally complex. Defer until core flow is validated.
- **D4: Worktree cleanup commands** — not needed until stale worktrees accumulate (5+ projects)
- **D5: IDE workspace generation** — low value for single-person workflow

**Anti-features (do NOT build):**
- Shell script wrappers (GSD IS the automation)
- GUI/TUI for worktree management
- Auto-sync between experiment branches
- Complex branch naming enforcement
- Template inheritance/composition engine

### Architecture Approach

Five components span two branch families: the Template Skeleton (master), the Base Environment (`00-experiments`), the Branch Lifecycle Manager (GSD workflow — the thing being built), per-branch Project Instances, and the Root README Index (cross-cutting). The critical insight is that master and `00-experiments` have **completely different file trees** — master is scaffolding, `00-experiments` is a standalone Python project root. All project branches must fork from `00-experiments` to inherit the correct environment.

**Major components:**
1. **Base Environment (`00-experiments`)** — inheritable Python dev environment (pyproject.toml, uv.lock, .python-version). Missing a README template — must be created first.
2. **Branch Lifecycle Manager (GSD)** — the automation layer. Orchestrates creation, population, and environment setup. Lives in `.planning/` docs, not scripts.
3. **Project Branch Instance** — self-contained, self-documenting branch with populated README and renamed pyproject.toml. Each is independent after creation.
4. **Root README Index (master)** — project dashboard. Cross-branch update is architecturally the hardest part — defer.

### Critical Pitfalls

1. **Submodules are broken in worktrees** — git officially warns against it. `00-experiments` has no submodules (safe), but never let `.gitmodules` leak into experiment branches. Always branch from `00-experiments`, never from `master`.

2. **Branch locking — same branch can't be in two worktrees** — `git worktree add` will fatal-error if the branch is already checked out elsewhere. Pre-flight check with `git worktree list --porcelain` is mandatory.

3. **Admin dir name ≠ branch name ≠ worktree path** — observable in the live repo right now (`experiments` vs `00-experiments`). Always use porcelain output for lookups, never derive from directory names. Enforce path-basename == branch-name at creation time.

4. **Missing `uv sync` after worktree creation** — worktrees have `pyproject.toml` but no `.venv`. Everything looks ready but imports fail. Confirmed in live repo: the `00-experiments` worktree has no `.venv`.

5. **Template clobber on re-run** — file writes are destructive. Use sentinel markers in README (`<!-- TEMPLATE: REPLACE ME -->`) and check for default `name = "template-repo"` before overwriting pyproject.toml.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Template Preparation
**Rationale:** Everything downstream depends on having a proper template README on `00-experiments`. This is the only prerequisite with zero dependencies — and without it, every new branch inherits nothing to populate.
**Delivers:** A `README.md` template on `00-experiments` with `$placeholder` variables and a sentinel comment. Optionally clean up the inherited `.gitignore` (remove irrelevant `02-worktrees/` rules).
**Addresses:** T3 (README template)
**Avoids:** Template clobber pitfall (sentinel enables idempotency from day one)

### Phase 2: Core Branch Creation Flow
**Rationale:** This is the primary workflow — the thing that makes the repo useful. It depends on Phase 1 (template exists to be populated). All table-stakes features and promoted differentiators ship here.
**Delivers:** Complete new-project creation: pre-flight checks → fetch → atomic branch+worktree → README population → pyproject.toml rename → `uv sync` → initial commit.
**Addresses:** T1, T2, T4, T5, D2, D3
**Avoids:** Branch locking (D3 pre-flight), race condition (atomic `git worktree add -b`), stale base (fetch before branch), missing venv (D2 `uv sync`), admin dir mismatch (enforce naming)
**Uses:** `subprocess.run()`, `re.sub()`, `string.Template`, `pathlib.Path`
**Implements:** Branch Lifecycle Manager component

### Phase 3: Root README Index
**Rationale:** Cross-branch editing (feature branch → master README) is architecturally the trickiest part. Deferring it lets the core flow stabilize first. It's also listed in PROJECT.md requirements, so it can't be skipped forever.
**Delivers:** Root `README.md` on master updated with new project entry (name, description, worktree path) after each creation.
**Addresses:** D1 (root README auto-update)
**Avoids:** Parallel update conflicts (serialize as a separate step), wrong-branch commits (verify root worktree is on master before editing)

### Phase 4: Lifecycle Management (optional)
**Rationale:** Only needed after multiple projects exist. Cleanup, archiving, and status tracking become valuable at 5+ worktrees.
**Delivers:** Worktree removal (`git worktree remove`), branch cleanup, root README entry removal, stale entry pruning.
**Addresses:** D4 (worktree cleanup)
**Avoids:** Accidental `rm -rf` (always use `git worktree remove`), premature prune (use `--dry-run` first)

### Phase Ordering Rationale

- **Phase 1 → 2 is a hard dependency:** The template must exist on `00-experiments` before any branch inherits it. Creating the template is a one-time setup; the creation flow is the repeating workflow.
- **Phase 2 is self-contained:** All table-stakes features ship together because they're a single logical operation (~8 commands). Splitting them would leave the workflow incomplete.
- **Phase 3 is deliberately deferred:** The root README update requires cross-branch editing and has edge cases (root worktree not on master). The core flow works perfectly without it — new branches are self-documenting regardless.
- **Phase 4 is optional:** Cleanup is a maintenance concern, not a creation concern. Build it when the need arises.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 3 (Root README Index):** Cross-branch commit workflow needs validation. Options A/B/C from ARCHITECTURE.md need a concrete decision. The root worktree may not be on `master` during development — need a fallback strategy.

Phases with standard patterns (skip research-phase):
- **Phase 1 (Template Preparation):** Straightforward file creation on a branch. No unknowns.
- **Phase 2 (Core Creation Flow):** All commands verified against live repo and official docs. Patterns are well-documented. The entire flow has been prototyped in research.
- **Phase 4 (Lifecycle Management):** Standard git operations. Only build when needed.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | **HIGH** | All recommendations verified against official docs, PyPI, and local testing. Zero ambiguity — stdlib-only, no decisions to revisit. |
| Features | **HIGH** | Requirements directly from PROJECT.md. Feature prioritization validated against architecture constraints and pitfall research. |
| Architecture | **HIGH** | Based on live codebase analysis. Component boundaries are clear. Only uncertainty is Phase 3 cross-branch update strategy. |
| Pitfalls | **HIGH** | Top 3 pitfalls verified by direct reproduction in the live repo. Prevention strategies are concrete and tested. |

**Overall confidence:** HIGH

### Gaps to Address

- **Root README update strategy:** ARCHITECTURE.md proposes Option A (GSD switches to master worktree) but this needs validation during Phase 3 planning. What happens when the root worktree is on a non-master branch? Graceful skip? Temporary switch? Separate worktree for master?
- **Branch naming convention:** PITFALLS.md raises numbered prefix collision. For a personal project this is low risk, but the roadmapper should decide: auto-increment numbers, or let the user pick freely? FEATURES.md anti-feature A4 recommends letting the user pick — that's the right call.
- **`00-experiments` `.gitignore` cleanup:** Contains `02-worktrees/` rules that are irrelevant on experiment branches. Minor hygiene — include in Phase 1 or ignore.

## Sources

### Primary (HIGH confidence)
- Git worktree official docs (git 2.53.0, 2026-02-02) — worktree operations, submodule warnings, porcelain output, atomic `-b` flag
- Live repo observation (2026-02-13) — submodule behavior, branch locking, admin dir naming, missing `.venv`, file tree analysis
- Python 3.13 stdlib docs — `string.Template`, `re`, `tomllib`, `subprocess`, `pathlib`
- PROJECT.md — first-party requirements

### Secondary (MEDIUM confidence)
- PyPI package analysis — GitPython (maintenance mode confirmed), tomlkit (actively maintained), tomli-w (no format preservation), Jinja2 (overkill verified)

### Tertiary (LOW confidence)
- IDE worktree indexing behavior — varies by IDE, `.vscode/settings.json` exclusion is a best-guess mitigation

---
*Research completed: 2026-02-13*
*Ready for roadmap: yes*
