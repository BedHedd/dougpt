# Feature Landscape

**Domain:** Git worktree-based project template workflow
**Researched:** 2026-02-13
**Overall confidence:** HIGH (based on existing repo analysis, PROJECT.md requirements, architecture/pitfalls research)

## Table Stakes

Features the workflow requires. Missing = the workflow breaks or produces inconsistent state.

| # | Feature | Why Expected | Complexity | Dependencies | Notes |
|---|---------|--------------|------------|--------------|-------|
| T1 | Branch creation from `00-experiments` | Every new project inherits the Python 3.13 + uv environment. Branching from `master` would give the wrong file tree (numbered dirs, submodules) and hit the git worktree + submodule incompatibility bug. | **Low** | None | Use atomic `git worktree add -b <name> 02-worktrees/<name> 00-experiments` — creates branch + worktree in one command. Must fetch `origin/00-experiments` first to avoid stale base. |
| T2 | Worktree creation in `02-worktrees/` | Worktrees provide parallel development without branch switching. The `02-worktrees/` directory is already gitignored (except README). Without this, users would need to `git checkout` between projects, losing open files and IDE state. | **Low** | T1 (branch must exist or be created atomically) | Path basename must match branch name exactly to avoid the admin-dir naming mismatch pitfall (see PITFALLS.md). |
| T3 | README template on `00-experiments` branch | New branches inherit all files from `00-experiments`. If no template README exists, GSD must create one from scratch every time — no consistent structure, no placeholders to fill. The `pyproject.toml` already references `readme = "README.md"` but the file doesn't exist yet. | **Low** | None — can be created independently | Use `$placeholder` syntax (`string.Template`) for variables: `$project_name`, `$description`, `$branch_name`, `$created_date`. Include a sentinel comment (`<!-- TEMPLATE: REPLACE ME -->`) for idempotency detection. |
| T4 | README population with project context on new branches | Each branch must be self-contained and self-documenting (per PROJECT.md constraint). An unpopulated template README with `$placeholders` is worse than no README — it signals an incomplete setup. | **Medium** | T2 (worktree must exist so files are editable), T3 (template must exist to be populated) | GSD substitutes placeholders via `string.Template.safe_substitute()`. Must check for sentinel before overwriting to prevent clobbering user edits on re-run. |
| T5 | `pyproject.toml` name update on new branches | The base `pyproject.toml` has `name = "template-repo"`. Every branch inheriting this will have the wrong project name, which affects `uv` environment naming, import paths, and project identity. | **Low** | T2 (worktree must exist so the file is editable) | Single regex replacement: `re.sub(r'^(name\s*=\s*)"[^"]*"', ...)`. Check that current name is still `"template-repo"` before replacing — idempotency guard against clobbering a previously renamed project. |

### Table Stakes — Implementation Order

```
T3 (README template on 00-experiments) ─── no dependencies, do first
    │
    ├── T1 + T2 (branch + worktree creation) ─── atomic via single git command
    │       │
    │       ├── T4 (README population) ─── requires worktree + template
    │       │
    │       └── T5 (pyproject.toml rename) ─── requires worktree
    │
    └── Commit on new branch
```

**Critical path:** T3 → T1/T2 → T4 + T5 → commit. This is one GSD workflow invocation (~5 commands).

---

## Differentiators

Features that improve the workflow but aren't required for it to function. Not expected, but valued.

| # | Feature | Value Proposition | Complexity | Dependencies | Notes |
|---|---------|-------------------|------------|--------------|-------|
| D1 | Root repo README auto-updated with active branches list | The template repo becomes a project dashboard — one glance shows all active experiments. Without it, you need `git branch` or `git worktree list` to know what exists. Listed as an active requirement in PROJECT.md. | **Medium** | T1/T2 (needs branch info to add) | Architecturally tricky: root README lives on `master`, but project creation happens on feature branches. GSD must switch context to root worktree (which is typically on `master`) to edit. Must handle case where root worktree is on a different branch. See ARCHITECTURE.md Flow 3 for options. |
| D2 | `uv sync` auto-run after worktree creation | New worktrees have `pyproject.toml` + `uv.lock` but no `.venv`. Without this, the first `python` or `import` command fails with `ModuleNotFoundError`. Documented as a common mistake in PITFALLS.md. | **Low** | T2 (worktree must exist) | Single command: `uv sync` run from within the worktree directory. Takes 5-15 seconds. Could fail if Python version isn't available — should handle gracefully. |
| D3 | Duplicate branch/worktree detection | Git refuses to check out a branch that's already in a worktree (`fatal: 'X' is already used by worktree at...`). Pre-checking avoids a hard failure and gives a meaningful error message. | **Low** | None (pre-flight check before T1/T2) | Parse `git worktree list --porcelain` to check if target branch name already exists. Also check `git branch --list <name>` for branches without worktrees. Report existing worktree path if found. |
| D4 | Worktree cleanup commands | Over time, stale worktrees accumulate (`02-worktrees/` fills up, `.git/worktrees/` has dead entries). Proper cleanup requires `git worktree remove` (not `rm -rf`) followed by optional branch deletion. | **Medium** | None | Must use `git worktree remove <path>` — never filesystem deletion. Should also `git worktree prune` to clean admin entries. Optionally delete the branch: `git branch -d <name>`. Could update root README to remove the entry (depends on D1). |
| D5 | IDE workspace file generation | Generate a `.code-workspace` file that includes the new worktree directory, so the user can open it directly in VS Code. The repo already has a `vs-dev.code-profile` in dev onboarding. | **Low** | T2 (worktree must exist) | Generate a JSON file: `{ "folders": [{ "path": "02-worktrees/<name>" }], "settings": {} }`. Place in repo root or in the worktree. Low value for a single-person workflow since opening a folder is one click anyway. |

### Differentiators — Priority Ranking

1. **D2 (`uv sync`)** — Low complexity, prevents the most common post-creation failure. Should be part of the core flow.
2. **D3 (Duplicate detection)** — Low complexity, prevents confusing git errors. Should be a pre-flight check in the core flow.
3. **D1 (Root README)** — Medium complexity, listed in PROJECT.md requirements. Implement after core flow works.
4. **D4 (Cleanup)** — Medium complexity, not needed until multiple projects exist. Defer to later phase.
5. **D5 (IDE workspace)** — Low complexity, low value. Nice to have, not a priority.

### Differentiator Recommendation

**Promote D2 and D3 to the core flow** — they're low complexity and prevent the two most common failure modes (missing venv, duplicate branch error). The implementation adds ~3 lines each:

```bash
# D3: Pre-flight duplicate check
git worktree list --porcelain | grep "branch refs/heads/<name>" && echo "ERROR: branch already in use"

# D2: Post-creation dependency sync  
uv sync  # run from within 02-worktrees/<name>/
```

---

## Anti-Features

Features to explicitly NOT build. These are scope traps that add complexity without proportional value.

| # | Anti-Feature | Why Avoid | What to Do Instead |
|---|--------------|-----------|-------------------|
| A1 | Shell script wrapper (`scripts/new-project.sh`) | The GSD AI orchestrator IS the automation layer. It reads `PROJECT.md`, executes git/file commands directly via tool calls, and handles errors conversationally. A shell script duplicates this capability, adds a maintenance surface, and introduces a second source of truth for the workflow. The STACK.md and ARCHITECTURE.md research both conclude that GSD inline commands are the right approach. | Encode the workflow in `PROJECT.md` requirements and `.planning/` research docs. GSD reads these and executes the steps. If a script is ever needed (team usage, CI), create it then — not proactively. |
| A2 | GUI/TUI for worktree management | This is a personal template repo for one developer. A TUI (curses, textual, rich) adds dependencies and code for a feature used once per project creation. The GSD orchestrator provides a better UX: natural language intent → automated execution. | Use GSD for project creation. Use `git worktree list` for inspection. Use `git worktree remove` for cleanup. These are 3 commands, not a TUI. |
| A3 | Auto-merge/sync between experiment branches | Experiment branches are intentionally independent after creation. Auto-syncing changes from `00-experiments` into project branches would create merge conflicts and break the isolation model. If a project needs updated base deps, the user should explicitly `git merge 00-experiments` or cherry-pick. | Document that `git merge 00-experiments` is available for pulling in base updates. Each branch owns its own dependency tree after creation. |
| A4 | Complex branch naming enforcement | The current convention is `XX-descriptive-name` with numbered prefixes. Adding strict validation (regex patterns, reserved prefixes, uniqueness checks beyond what git enforces) adds complexity for marginal value in a single-person workflow. Numbered prefix auto-assignment (scanning existing branches, incrementing) is fragile and over-engineered. | Let the user (or GSD) choose the branch name. The only validation needed is: (1) git accepts it as a valid ref name, (2) it's not already in use (D3 handles this). Don't auto-assign numbers — let the user pick meaningful names. |
| A5 | Template inheritance/composition | A system where branch templates can inherit from or compose with other templates (e.g., "Python + FastAPI template", "Python + data science template"). This is project scaffolding (Cookiecutter territory) — a category error for this workflow. The base is always `00-experiments`; customization happens after branching. | Keep `00-experiments` as the single base. If different project types need different starting points, create new base branches (`00-web-api`, `00-data-science`) and document them. Don't build a template composition engine. |

### Anti-Feature Rationale — The "Why Not" Pattern

Every anti-feature above follows the same pattern: **it solves a problem that doesn't exist yet for a single-person workflow**. The decision tree is:

```
Is this a team tool?  → NO  → Don't build team features (A2, A4)
Is this a scaffolding tool?  → NO  → Don't build scaffolding features (A5)  
Does GSD already handle this?  → YES  → Don't duplicate in scripts (A1)
Does this break branch isolation?  → YES  → Don't build it (A3)
```

If any of these conditions change (e.g., the template is shared with a team), revisit the anti-feature classification.

---

## Feature Dependencies

```
                    ┌─────────────────────┐
                    │ T3: README Template  │  (no dependencies)
                    │   on 00-experiments  │
                    └──────────┬──────────┘
                               │ inherited by new branches
                               ▼
┌──────────────┐    ┌─────────────────────┐
│ D3: Duplicate│───▶│ T1+T2: Branch +     │  (atomic command)
│   Detection  │    │   Worktree Creation  │
│ (pre-flight) │    └──────────┬──────────┘
└──────────────┘               │ files now exist in worktree
                    ┌──────────┼──────────┐
                    ▼          ▼          ▼
              ┌──────────┐ ┌────────┐ ┌──────────┐
              │ T4: README│ │T5: pyp-│ │D2: uv    │
              │ Population│ │roject  │ │   sync   │
              │           │ │.toml   │ │          │
              └──────────┘ └────────┘ └──────────┘
                    │          │
                    ▼          ▼
              ┌─────────────────────┐
              │   Commit on branch  │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ D1: Root README     │  (optional, separate commit on master)
              │   Auto-Update       │
              └─────────────────────┘

              ┌─────────────────────┐
              │ D4: Worktree        │  (independent lifecycle, run anytime)
              │   Cleanup           │
              └─────────────────────┘

              ┌─────────────────────┐
              │ D5: IDE Workspace   │  (optional, after T2)
              │   File Generation   │
              └─────────────────────┘
```

---

## MVP Recommendation

### Must Ship (core workflow — one GSD invocation)

1. **T3: README template on `00-experiments`** — Create the template file with `$placeholder` variables and a sentinel comment. This is a one-time setup that all future branches inherit.

2. **T1 + T2: Branch + worktree creation** — Atomic `git worktree add -b` command. Include `git fetch origin 00-experiments` as a pre-step to avoid stale base.

3. **T4: README population** — `string.Template.safe_substitute()` with project context (name, description, branch, date).

4. **T5: pyproject.toml rename** — `re.sub()` to change `name = "template-repo"` to the project name.

5. **D3: Duplicate detection** (promoted from differentiator) — Pre-flight check via `git worktree list --porcelain`. Prevents confusing git errors.

6. **D2: `uv sync`** (promoted from differentiator) — Post-creation dependency install. Prevents `ModuleNotFoundError` on first use.

### Defer

| Feature | Defer Reason | When to Revisit |
|---------|-------------|-----------------|
| D1: Root README auto-update | Architecturally complex (cross-branch editing). Core workflow works without it. | After MVP is validated and the first 2-3 projects are created. |
| D4: Worktree cleanup | Not needed until multiple stale projects accumulate. | After 5+ worktrees exist. |
| D5: IDE workspace generation | Low value — opening a folder in VS Code is trivial. | Only if opening worktrees becomes a repeated friction point. |

### MVP Flow Summary

```bash
# Pre-flight
git fetch origin 00-experiments
git worktree list --porcelain  # check for duplicates (D3)

# Create (atomic)
git worktree add -b <name> 02-worktrees/<name> 00-experiments

# Configure (in worktree)
# → Edit README.md: substitute $placeholders (T4)
# → Edit pyproject.toml: rename project (T5)

# Environment
uv sync  # from within 02-worktrees/<name>/ (D2)

# Commit
git -C 02-worktrees/<name> add .
git -C 02-worktrees/<name> commit -m "initialize <name> project"
```

**Total: ~8 commands, zero dependencies beyond git + uv + Python stdlib.**

---

## Sources

- `PROJECT.md` requirements — active requirements checklist (first-party, HIGH confidence)
- `ARCHITECTURE.md` research — component boundaries, data flows, cross-branch update patterns (HIGH confidence)
- `PITFALLS.md` research — duplicate branch errors, missing `.venv`, admin dir naming (HIGH confidence, verified in live repo)
- `STACK.md` research — `string.Template`, `re.sub()`, subprocess approach (HIGH confidence)
- `02-worktrees/README.md` — existing worktree documentation and conventions (first-party)
- Root `README.md` — current state of project dashboard (first-party)
- `.planning/codebase/CONVENTIONS.md` — naming conventions, git conventions (first-party)
- Git worktree official docs (git 2.53.0, 2026-02-02) — atomic `-b` flag, `--porcelain` output

---

*Feature landscape research: 2026-02-13*
