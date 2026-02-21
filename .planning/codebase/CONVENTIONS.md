# Coding Conventions

**Analysis Date:** 2026-02-13

## Naming Patterns

**Files:**
- Use lowercase with hyphens for markdown files: `daily-note.md`, `new-template.md`
- Use lowercase for Python files: `app.py`
- Use numeric prefixes (`00-`) for ordering within directories

**Directories:**
- Use two-digit numeric prefix + hyphenated descriptive name: `00-dev-log/`, `02-worktrees/`
- Prefix numbers indicate category: `00` = meta/support, `01` = onboarding, `02` = dev tools

**Functions:**
- Not yet established (no application code)

**Variables:**
- Not yet established (no application code)

**Types:**
- Not yet established (no application code)

## Code Style

**Formatting:**
- No formatter configured (no `.prettierrc`, `pyproject.toml` with black/ruff settings, etc.)
- Recommendation: Configure `ruff` (already referenced in `.gitignore` via `.ruff_cache/`)

**Linting:**
- No linter configured
- `.gitignore` includes entries for `ruff`, `mypy`, `pytype`, and `pyre`, suggesting Python type checking may be added
- Recommendation: Configure `ruff` for linting and formatting

## Import Organization

**Order:**
- Not yet established (no imports in codebase)

**Path Aliases:**
- None configured

## Error Handling

**Patterns:**
- Not yet established

## Logging

**Framework:** Not configured

**Patterns:**
- Not yet established

## Comments

**When to Comment:**
- Not yet established

**JSDoc/TSDoc:**
- Not applicable (Python codebase)

## Function Design

**Size:** Not yet established
**Parameters:** Not yet established
**Return Values:** Not yet established

## Module Design

**Exports:** Not yet established
**Barrel Files:** Not applicable

## Documentation Conventions

**README files:**
- Each major directory has or should have a `README.md` explaining its purpose
- `02-worktrees/README.md` is the exemplar: includes "What", "Usage" with code examples, and "Notes"

**Dev Logs:**
- Follow template in `00-dev-log/00-template.md`: Date heading, "Overall Progress" checklist, "Elaboration" section

**Foam Templates:**
- Use VS Code snippet variables: `${CURRENT_YEAR}`, `${CURRENT_MONTH}`, `${CURRENT_DATE}`
- Located in `.foam/templates/`

## Git Conventions

**Commit Messages:**
- Lowercase, imperative style: "move python files to worktree", "add markdown display code", "update instructions to use experiments branch"
- No conventional commit prefixes (no `feat:`, `fix:`, etc.)

**Branch Naming:**
- Descriptive hyphenated names: `vibe-coding`, `worktrees`
- Numeric prefix for experimental: `00-experiments`

**Submodules:**
- External shared resources are added as git submodules
- Defined in `.gitmodules`

---

*Convention analysis: 2026-02-13*
