# Coding Conventions

**Analysis Date:** 2026-02-21

## Naming Patterns

**Files:**
- Use `kebab-case` for marimo notebook-exported scripts (for example `02-worktrees/chat-extraction/chat-extraction.py` and `02-worktrees/old-master/02-development/chat-extraction/chat-extraction.py`).
- Use `UPPERCASE.md` for codebase mapping docs under `.planning/codebase/` (for example `.planning/codebase/CONVENTIONS.md`).

**Functions:**
- Use marimo cell wrapper functions named `_` in `@app.cell` blocks for notebook-style execution flow (`02-worktrees/chat-extraction/chat-extraction.py`).
- Use `snake_case` for helper function names when declared (for example `image_file_to_data_url` in `02-worktrees/chat-extraction/chat-extraction.py`).

**Variables:**
- Use `snake_case` for local variables (`project_parent`, `supporting_files`, `compressed_frame`) in `02-worktrees/chat-extraction/chat-extraction.py`.
- Use `UPPER_SNAKE_CASE` for notebook-level configuration constants (`FRAMES_DIR`, `MODEL`, `BASE_URL`, `API_KEY`) in `02-worktrees/chat-extraction/chat-extraction.py`.

**Types:**
- Use `PascalCase` for Pydantic model names when schema classes are introduced (`EmoteBox`, `ChatMessage`, `ImageOnlyExtraction`, `BatchExtraction`) in `02-worktrees/chat-extraction/chat-extraction.py`.

## Code Style

**Formatting:**
- Not detected: no formatter config files in repo root (`.prettierrc*`, `ruff.toml`, `.ruff.toml`, `pyproject` tool formatting sections not present in `/home/bedhedd/Documents/development_projects/bedhedd_projects/dougpt/dougpt`).
- Keep standard Python indentation and multiline trailing-comma style seen in `02-worktrees/chat-extraction/chat-extraction.py` and dependency arrays in `02-worktrees/chat-extraction/pyproject.toml`.

**Linting:**
- Not detected: no lint config files (`ruff`, `flake8`, `pylint`, `mypy`, ESLint) in `/home/bedhedd/Documents/development_projects/bedhedd_projects/dougpt/dougpt`.
- Keep code review-driven style checks until lint tooling is added.

## Import Organization

**Order:**
1. Third-party imports are grouped inside marimo cells close to usage (for example `import marimo as mo` and `from IPython.display import Markdown, display` in `02-worktrees/chat-extraction/chat-extraction.py`).
2. Standard-library imports are also often cell-local (`import base64`, `import mimetypes`, `from pathlib import Path`) in `02-worktrees/chat-extraction/chat-extraction.py`.
3. Project-internal imports are not detected in current Python files (`02-worktrees/chat-extraction/chat-extraction.py`, `02-worktrees/old-master/03-app/app.py`).

**Path Aliases:**
- Not applicable: Python path alias configuration is not detected in `02-worktrees/00-experiments/pyproject.toml`, `02-worktrees/chat-extraction/pyproject.toml`, or `02-worktrees/old-master/pyproject.toml`.

## Error Handling

**Patterns:**
- Use targeted `try/except` for runtime context resolution (for example fallback from `Path(__file__)` to `Path.cwd()` in `02-worktrees/chat-extraction/chat-extraction.py`).
- Prefer explicit command result checks via `subprocess.run(..., capture_output=True, text=True)` plus return-code inspection in notebook cells (`02-worktrees/chat-extraction/chat-extraction.py`).
- Hard fail patterns (`raise RuntimeError(...)`) currently appear only in commented examples, not active execution paths (`02-worktrees/chat-extraction/chat-extraction.py`).

## Logging

**Framework:** console

**Patterns:**
- Use `print(...)` for diagnostics and ad-hoc runtime checks in marimo cells (`02-worktrees/chat-extraction/chat-extraction.py`).
- No structured logging framework is configured in `02-worktrees/chat-extraction/pyproject.toml` or `02-worktrees/00-experiments/pyproject.toml`.

## Comments

**When to Comment:**
- Keep explanatory comments for experiment setup, shell command examples, and model-inference instructions inside notebook-exported scripts (`02-worktrees/chat-extraction/chat-extraction.py`).
- Large commented blocks are used as optional experiment branches rather than deleted code in `02-worktrees/chat-extraction/chat-extraction.py`.

**JSDoc/TSDoc:**
- Not applicable: no TypeScript/JavaScript source files detected in `/home/bedhedd/Documents/development_projects/bedhedd_projects/dougpt/dougpt`.
- Python docstrings are sparse; add concise docstrings only for reusable helper functions (pattern shown in planning examples at `.planning/research/STACK.md`).

## Function Design

**Size:**
- Keep functions small and cell-scoped in marimo scripts, with each `@app.cell` performing one step (`02-worktrees/chat-extraction/chat-extraction.py`).

**Parameters:**
- Pass dependencies explicitly through marimo cell arguments (for example `def _(Markdown, client, compressed_frame, image_file_to_data_url):`) in `02-worktrees/chat-extraction/chat-extraction.py`.

**Return Values:**
- Return tuple-wrapped values from cells for downstream dependency wiring (`return (project_parent,)`, `return client, image_file_to_data_url`) in `02-worktrees/chat-extraction/chat-extraction.py`.

## Module Design

**Exports:**
- Use marimo app entrypoint pattern (`app = marimo.App(...)` and final `if __name__ == "__main__": app.run()` style expected for generated files) in `02-worktrees/chat-extraction/chat-extraction.py`.
- Traditional reusable package/module exports are not established in `02-worktrees/old-master/03-app/app.py` (currently empty).

**Barrel Files:**
- Not applicable: no package barrel files (`__init__.py` aggregation patterns) are detected under `02-worktrees/`.

---

*Convention analysis: 2026-02-21*
