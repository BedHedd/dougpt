# Pitfalls Research

**Domain:** Git worktree-based project template workflow
**Researched:** 2026-02-13
**Overall confidence:** HIGH (verified against official git docs, observed in live repo)

## Critical Pitfalls

### Pitfall 1: Submodules Are Broken in Worktrees

**What goes wrong:** Git's official documentation explicitly warns: "the support for submodules is incomplete. It is NOT recommended to make multiple checkouts of a superproject." The `01-dev-onboarding` submodule from the `master` branch will not be initialized in worktrees. Worktrees that branch from `00-experiments` (which has no `.gitmodules`) are unaffected today — but if submodule references ever leak into experiment branches, worktrees will break.

**Why it happens:** Submodule metadata lives in `.git/modules/` in the main worktree. Linked worktrees use `.git` *files* (not directories) that point back to the main repo's `$GIT_DIR/worktrees/<name>/`. Git's submodule plumbing doesn't correctly resolve paths across this indirection, so `git submodule init` and `git submodule update` can fail or produce inconsistent state.

**Verified evidence:**
- The `00-experiments` worktree at `02-worktrees/00-experiments/` has no `01-dev-onboarding/` directory (confirmed: "Submodule directory missing or empty in worktree")
- This is currently benign because `00-experiments` branch has no `.gitmodules` file
- Official git-worktree docs (git 2.53.0, 2026-02-02): BUGS section explicitly warns against this

**Consequences:** If automation ever creates branches that include submodule references, `git submodule` commands will fail in those worktrees. Users who `cd` into a worktree and try to use submodule content will find empty directories.

**Warning signs:**
- `.gitmodules` appearing on any experiment/feature branch
- `git submodule status` returning errors inside a worktree
- Empty directories where submodule content should be

**Prevention:**
- Keep `00-experiments` as a clean slate: no `.gitmodules`, no submodule references
- Automation must never copy `.gitmodules` or submodule directories when branching from `00-experiments`
- If shared libraries are needed across branches, use a different mechanism (uv dependencies, vendoring, or symlinks)
- Document this limitation in the worktree README

**Phase to address:** Phase 1 (branch creation automation) — ensure branching logic never inherits submodule state.

**Confidence:** HIGH — verified against official docs and observed in live repo.

---

### Pitfall 2: Branch Locking — Cannot Check Out Same Branch in Two Worktrees

**What goes wrong:** Git refuses to check out a branch that's already checked out in another worktree. If automation tries to create a worktree for a branch that's already active somewhere, it will fail with a fatal error.

**Why it happens:** Git enforces single-checkout per branch to prevent conflicting index states. Each worktree has its own `HEAD` and `index`, but refs are shared. Two worktrees on the same branch would cause commits in one to silently invalidate the other's working state.

**Verified evidence:**
```
$ git worktree add /tmp/test-dup 00-experiments
fatal: '00-experiments' is already used by worktree at
'/Users/progressedd/personal-projects/project-template/02-worktrees/00-experiments'
```

**Consequences:** Automation that doesn't check for existing worktrees before creating new ones will fail hard. Users who manually create worktrees before running automation will hit errors.

**Warning signs:**
- Fatal errors containing "is already used by worktree at"
- Automation scripts that don't pre-check `git worktree list`

**Prevention:**
- Before creating a worktree, always run `git worktree list --porcelain` and check if the target branch is already checked out
- Automation should handle this gracefully: detect existing worktree, report it, and skip or reuse
- Use `--force` flag only as a deliberate override, never as a default

**Phase to address:** Phase 1 (branch + worktree creation) — build pre-flight checks into automation.

**Confidence:** HIGH — verified by direct test.

---

### Pitfall 3: Worktree Admin Directory Name ≠ Branch Name ≠ Worktree Path

**What goes wrong:** The worktree admin directory (inside `.git/worktrees/`) is named after the *basename of the path* at creation time, not the branch name. If the worktree path basename differs from the branch name, three different names exist for the same worktree, making scripting error-prone.

**Why it happens:** This is observable in the live repo right now:
- Branch name: `00-experiments`
- Worktree path: `02-worktrees/00-experiments`
- Admin directory: `.git/worktrees/experiments` (from original creation path)

The admin dir was named `experiments` because the worktree was originally created at a path ending in `experiments`, then later moved/renamed to `00-experiments` and repaired.

**Consequences:** Scripts that assume admin-dir-name == branch-name will break. Scripts that derive branch name from path basename will be wrong if the worktree was moved. Cleanup scripts that scan `.git/worktrees/` won't match expected names.

**Warning signs:**
- Automation that assumes any two of these three names are the same
- Worktree listing showing unexpected admin directory names
- `git worktree repair` needed after manual path changes

**Prevention:**
- Always use `git worktree list --porcelain` to discover worktree-to-branch mappings — never derive from directory names
- Automation should create worktrees where path basename matches branch name exactly: `git worktree add 02-worktrees/XX-name -b XX-name 00-experiments`
- Establish a naming convention: branch name `XX-project-name`, worktree path `02-worktrees/XX-project-name` — keep them identical
- Never manually move/rename worktree directories; use `git worktree move` instead

**Phase to address:** Phase 1 (worktree creation) — enforce naming consistency from the start.

**Confidence:** HIGH — observed directly in live repo.

## Common Mistakes

### Mistake 1: Forgetting `uv sync` After Worktree Creation

**What goes wrong:** New worktrees from `00-experiments` have `pyproject.toml` and `uv.lock` but no `.venv`. The project appears ready but `python` and `import` statements fail because dependencies aren't installed.

**Why it happens:** `git worktree add` checks out files but doesn't run post-checkout hooks or package manager commands. Each worktree needs its own `.venv` directory (correctly gitignored), but nothing triggers its creation.

**Verified evidence:** The `00-experiments` worktree at `02-worktrees/00-experiments/` has no `.venv` directory.

**Warning signs:**
- `ModuleNotFoundError` immediately after starting work in a new worktree
- No `.venv` directory in the worktree root

**Prevention:**
- Automation must run `uv sync` as a post-worktree-creation step
- Or: use a git `post-checkout` hook that detects worktree creation and runs `uv sync`
- Document the setup step in the worktree README

**Phase to address:** Phase 1 (worktree setup automation) — include `uv sync` in the creation flow.

**Confidence:** HIGH — verified by inspecting live worktree.

---

### Mistake 2: Stash Is Shared Across All Worktrees

**What goes wrong:** `git stash` in one worktree is visible in all other worktrees. A user stashes in worktree A, then runs `git stash pop` in worktree B, applying unrelated changes to the wrong branch.

**Why it happens:** Stash is stored in `refs/stash` which is in the shared `$GIT_COMMON_DIR`. It's not per-worktree state.

**Warning signs:**
- Unexpected changes after `git stash pop`
- Stash list showing entries from other worktrees/branches

**Prevention:**
- Avoid `git stash` in a multi-worktree workflow — it's rarely needed since each worktree is its own branch
- If stashing is needed, use named stashes: `git stash push -m "worktree-XX: description"`
- Document this gotcha for users

**Phase to address:** Documentation phase — mention in worktree README.

**Confidence:** HIGH — this is documented git behavior.

---

### Mistake 3: Running `git` Commands From the Wrong Directory

**What goes wrong:** Running `git` commands from the main worktree (repo root) affects the main worktree's branch, not the experiment branch. Users who are accustomed to a single-worktree workflow forget that `git commit` in the root commits to `master`/`vibe-coding-gsd`, not to their experiment.

**Why it happens:** Each worktree has its own `HEAD`, `index`, and working tree. Git determines which worktree you're operating on by your current working directory.

**Warning signs:**
- Commits appearing on the wrong branch
- Files staged in one worktree showing up in `git status` of the root

**Prevention:**
- Automation should `cd` into the worktree directory before performing git operations
- Scripts should use `git -C <worktree-path>` to explicitly target the correct worktree
- Consider adding the branch name to the shell prompt (most shells already do this)

**Phase to address:** Phase 1 (automation) — all automated git commands must use explicit `-C` paths.

**Confidence:** HIGH — fundamental git behavior.

## Git Worktree Gotchas

### Gotcha 1: Hooks Are Shared, Not Per-Worktree

**What goes wrong:** Git hooks (`.git/hooks/`) are in the shared `$GIT_COMMON_DIR`. A pre-commit hook installed in the main worktree fires for commits in all worktrees. If hooks assume paths or branch names specific to the main worktree, they'll produce wrong results or errors in linked worktrees.

**Why it happens:** Hooks live at `.git/hooks/`, which is in the shared common directory. There's no per-worktree hooks directory by default.

**Prevention:**
- Any hooks must be worktree-aware: use `git rev-parse --show-toplevel` not hardcoded paths
- If worktree-specific hooks are needed, use `core.hooksPath` with `extensions.worktreeConfig`
- For this project: hooks are currently sample-only (no custom hooks), so this is a future concern

**Phase to address:** Future phases if hooks are added.

**Confidence:** HIGH — verified by inspecting `.git/hooks/` (contains only `.sample` files).

---

### Gotcha 2: `.gitignore` Rules for `02-worktrees/` Are Inherited but Irrelevant on Branches

**What goes wrong:** The `00-experiments` branch's `.gitignore` includes rules for `02-worktrees/*`. When a new branch is created from `00-experiments` and checked out as a worktree inside `02-worktrees/`, that `.gitignore` rule references a directory (`02-worktrees/`) that doesn't exist relative to the worktree root. This is benign but confusing — the rule silently does nothing.

**Why it happens:** Branch content is inherited verbatim from `00-experiments`. The `.gitignore` was written for the repo root context, not the worktree context.

**Prevention:**
- Clean up the `.gitignore` on `00-experiments` to remove `02-worktrees/` rules — they're only relevant on `master`
- Or: accept the noise and document that these rules are inherited but inactive on worktree branches
- If cleaning up: do it as part of the template README creation phase since `.gitignore` is being touched anyway

**Phase to address:** Phase 1 (template preparation on `00-experiments`).

**Confidence:** HIGH — verified by reading the `.gitignore` file on the `00-experiments` branch.

---

### Gotcha 3: `git worktree prune` Can Delete Worktrees You're Using

**What goes wrong:** If a worktree directory is deleted manually (e.g., `rm -rf 02-worktrees/XX-name`) without running `git worktree remove`, the admin entries in `.git/worktrees/` become stale. Running `git worktree prune` then cleans up those admin entries — but if the directory was only temporarily unmounted or inaccessible, the metadata is lost.

**Why it happens:** Git can't distinguish between "intentionally deleted" and "temporarily unavailable."

**Prevention:**
- Always use `git worktree remove` instead of `rm -rf` for cleanup
- Use `git worktree lock` for worktrees on removable storage
- Automation cleanup should use `git worktree remove <path>` not filesystem deletion
- Run `git worktree prune --dry-run` before `git worktree prune` to see what would be removed

**Phase to address:** Phase 3 (cleanup/lifecycle automation, if implemented).

**Confidence:** HIGH — documented in official git docs.

---

### Gotcha 4: Worktree Inside the Main Repo Tree Creates Filesystem Nesting

**What goes wrong:** The `02-worktrees/` directory is inside the main repo's working tree. This means worktree checkouts are nested within the repo's filesystem. Although the contents are gitignored, tools like IDE file watchers, `find` commands, and backup systems will traverse into these directories, leading to:
- IDE indexing all worktree files as part of the main project
- Slow file searches that recurse into worktree directories
- Backup/sync tools doubling the effective repo size

**Why it happens:** Worktrees inside the repo tree are convenient for organization but create filesystem nesting. The git-worktree docs show examples with worktrees *outside* the repo tree (e.g., `../hotfix`).

**Prevention:**
- Add `02-worktrees/` to IDE exclude/ignore settings (`.vscode/settings.json` → `files.exclude`)
- This is already partially handled by `.gitignore`, but IDEs don't always respect `.gitignore` for indexing
- Accept this tradeoff — the organizational benefit of keeping worktrees in `02-worktrees/` outweighs the minor IDE config needed
- Consider adding an `.editorconfig` or workspace settings file

**Phase to address:** Phase 1 (workspace setup) — add IDE exclusion config.

**Confidence:** MEDIUM — based on general IDE behavior; specific IDE behavior varies.

## Automation Risks

### Risk 1: Race Condition Between Branch Creation and Worktree Add

**What goes wrong:** If automation creates a branch (`git branch XX-name 00-experiments`) as a separate step from worktree creation (`git worktree add 02-worktrees/XX-name XX-name`), a failure between the two steps leaves a branch with no worktree. Re-running automation may fail because the branch already exists.

**Why it happens:** Two-step process without transactional guarantees.

**Prevention:**
- Use the atomic form: `git worktree add -b XX-name 02-worktrees/XX-name 00-experiments`
- This creates the branch and worktree in a single command — if it fails, neither is created
- Automation should still handle the "branch already exists" case by offering to attach an existing branch to a new worktree

**Phase to address:** Phase 1 (core automation) — use atomic `worktree add -b` command.

**Confidence:** HIGH — verified from official docs; `-b` flag creates branch and worktree atomically.

---

### Risk 2: Template File Replacement Clobbers User Work

**What goes wrong:** If automation updates `README.md` or `pyproject.toml` after the user has already started editing them, user work is lost. This can happen if:
- Automation runs twice (e.g., retry after partial failure)
- Automation runs on an existing branch/worktree instead of a fresh one
- User creates branch manually, starts working, then runs automation

**Why it happens:** File templating logic uses write-all semantics, not merge semantics.

**Prevention:**
- Automation should check if files already have custom content before overwriting
- Use a sentinel marker (e.g., `<!-- TEMPLATE: REPLACE ME -->`) in the template README — automation only replaces if the sentinel is present
- For `pyproject.toml`: check if `name` is still the default `"template-repo"` before updating
- Always create a fresh branch + worktree before templating; never template an existing branch

**Phase to address:** Phase 2 (file templating) — implement idempotency checks.

**Confidence:** HIGH — logical consequence of write-all file operations.

---

### Risk 3: Root README Update Conflicts Across Simultaneous Worktrees

**What goes wrong:** Multiple worktree creation sessions running in parallel could both try to update the root `README.md` to reference their new branch. Since the root README is on the `master` branch (main worktree), this creates a merge conflict or last-writer-wins situation.

**Why it happens:** The root README is a shared resource on the main worktree. Parallel automation sessions all target the same file.

**Prevention:**
- Make root README updates a manual or queued step, not part of the atomic worktree creation
- Or: use a lockfile mechanism to serialize root README updates
- Or: generate the root README dynamically from `git worktree list` + `git branch` output, rather than maintaining it manually
- Simplest: accept that root README updates are a separate, infrequent step

**Phase to address:** Phase 3 (root README update) — design for non-conflicting updates.

**Confidence:** MEDIUM — only relevant if parallel automation is used; unlikely for a personal project but worth designing for.

---

### Risk 4: Automation Assumes `00-experiments` Is Up-to-Date

**What goes wrong:** If automation branches from the local `00-experiments` ref without fetching, new branches miss upstream changes. The local `00-experiments` branch may be behind `origin/00-experiments`.

**Why it happens:** `git worktree add -b XX-name 02-worktrees/XX-name 00-experiments` uses the local ref, not the remote.

**Prevention:**
- Automation should fetch before branching: `git fetch origin 00-experiments`
- Then branch from the fetched ref: `git worktree add -b XX-name 02-worktrees/XX-name origin/00-experiments`
- Or: fast-forward the local branch first: `git branch -f 00-experiments origin/00-experiments` (only safe if `00-experiments` worktree isn't active or has no uncommitted changes)
- Simplest for single-user: fetch + branch from `origin/00-experiments`

**Phase to address:** Phase 1 (branch creation) — include fetch step.

**Confidence:** HIGH — standard git behavior.

---

### Risk 5: Numbered Prefix Convention Requires Manual Coordination

**What goes wrong:** The `XX-project-name` naming convention requires choosing a number that doesn't collide with existing branches. If automation auto-assigns numbers, two users (or two automation runs) could pick the same number. If users pick manually, they may not know which numbers are taken.

**Why it happens:** No single source of truth for "next available number." Branch listing requires scanning and parsing.

**Prevention:**
- Automation should scan existing branches matching `^\d{2}-` and auto-increment
- Use `git branch --list '[0-9][0-9]-*'` to find existing numbered branches
- Reserve `00-` for template/shared branches, start user projects at a higher range (e.g., `10-`, `20-`)
- For a personal project, sequential numbering is fine; for teams, use timestamps or UUIDs instead

**Phase to address:** Phase 1 (branch naming logic).

**Confidence:** MEDIUM — depends on usage patterns; personal project mitigates collision risk.

## Prevention Strategies

| Pitfall | Prevention Strategy | Implementation |
|---------|---------------------|----------------|
| Submodules in worktrees | Keep `00-experiments` submodule-free | Validate on branch creation |
| Branch already checked out | Pre-check `git worktree list --porcelain` | Add to automation pre-flight |
| Name mismatch (admin/branch/path) | Use `git worktree add -b NAME path/NAME base` | Enforce in automation |
| Missing `uv sync` | Run `uv sync` post-worktree-add | Add to automation flow |
| Shared stash confusion | Document; avoid stash in multi-worktree | Add to worktree README |
| Wrong directory for git commands | Use `git -C <path>` in automation | Enforce in all scripts |
| Shared hooks | Make hooks worktree-aware | Audit if hooks are added |
| Irrelevant `.gitignore` rules | Clean `02-worktrees/` rules from experiment branches | Phase 1 template prep |
| Accidental worktree prune | Use `git worktree remove`, never `rm -rf` | Automation cleanup |
| IDE indexing worktree dirs | Add IDE exclude config | Workspace settings |
| Race condition (branch + worktree) | Use atomic `git worktree add -b` | Single-command creation |
| Template clobber | Check for sentinel/default values before overwriting | Idempotency guard |
| Root README conflicts | Generate dynamically or serialize updates | Design for concurrency |
| Stale `00-experiments` base | Fetch before branching | Pre-flight fetch |
| Number collision | Auto-scan + increment numbered branches | Branch naming logic |

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Branch creation | Race condition between `git branch` and `git worktree add` | Use atomic `git worktree add -b` |
| Branch creation | Branch already checked out in existing worktree | Pre-check with `git worktree list --porcelain` |
| Branch creation | Stale base branch | Fetch `origin/00-experiments` before branching |
| Worktree setup | Missing `.venv` / dependencies not installed | Run `uv sync` as post-creation step |
| Worktree setup | Admin dir name ≠ branch name | Enforce path-basename == branch-name convention |
| File templating (README) | Clobber existing user content on re-run | Sentinel-based idempotency check |
| File templating (pyproject.toml) | Clobber custom project name | Check for default value before replacing |
| Root README update | Parallel update conflicts | Serialize or generate dynamically |
| Cleanup/teardown | Manual `rm -rf` leaves stale admin entries | Always use `git worktree remove` |
| Cleanup/teardown | Deleting branch before removing worktree | Remove worktree first, then delete branch |

## Sources

- [git-worktree official docs (git 2.53.0, 2026-02-02)](https://git-scm.com/docs/git-worktree) — HIGH confidence
  - BUGS section: "support for submodules is incomplete. It is NOT recommended to make multiple checkouts of a superproject."
  - REFS section: stash and most refs are shared; HEAD/index are per-worktree
  - CONFIGURATION FILE section: `extensions.worktreeConfig` for per-worktree config
  - DETAILS section: admin directory naming from path basename
- Live repo observation (2026-02-13) — HIGH confidence
  - Submodule missing in worktree: confirmed
  - Branch lock error: reproduced
  - Admin dir naming mismatch: observed (`experiments` vs `00-experiments`)
  - No `.venv` in worktree: confirmed
- Git local config inspection — HIGH confidence
  - `submodule.01-dev-onboarding.active=true` in shared config
  - No `extensions.worktreeConfig` enabled

---

*Pitfalls research: 2026-02-13*
