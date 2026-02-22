# Coding Conventions

**Analysis Date:** 2026-02-21

## Naming Patterns

**Files:**
- Hyphenated snake_case filenames for marimo notebooks (`02-worktrees/chat-extraction/chat-extraction.py`, `02-worktrees/old-master/02-development/chat-extraction/chat-extraction.py`).

**Functions:**
- Marimo-generated cell functions named `_` and decorated with `@app.cell`, relying on dependency injection rather than explicit function names.

**Variables:**
- snake_case for locals such as `project_parent`, `video_dir`, `compressed_frame`; uppercase constants for configuration (`MODEL`, `BASE_URL`, `API_KEY`) in `02-worktrees/chat-extraction/chat-extraction.py`.

**Types:**
- Minimal typing; only commented-out Pydantic models include annotations in `02-worktrees/chat-extraction/chat-extraction.py`; no repository-level type checker configuration.

## Code Style

**Formatting:**
- No formatter configuration (no Black/ruff/flake8 configs); formatting is manual with multi-line comment blocks and long strings kept inline.

**Linting:**
- No linting tools configured or referenced in `pyproject.toml`; style enforcement is ad hoc.

## Import Organization

**Order:**
1. Standard library modules pulled per cell (e.g., `pathlib`, `base64`, `subprocess`).
2. Third-party imports (`marimo`, `openai`, `opencv-python`, `pydantic`, `dotenv`).
3. Local paths derived via `Path` and returned from prior cells; no intra-package imports.

**Path Aliases:**
- None; paths are built with `pathlib.Path` literals.

## Error Handling

**Patterns:**
- Limited handling: `try/except NameError` fallback to `Path.cwd()` in `02-worktrees/chat-extraction/chat-extraction.py`; external commands executed with `subprocess.run(..., capture_output=True)` and outputs printed without retries or exceptions; most cells assume happy paths.

## Logging

**Framework:**
- Console-style logging via `print`; markdown and `mo.md`/`Markdown` outputs used for interactive display; no structured logging library.

**Patterns:**
- Diagnostic prints for subprocess return codes and stderr; otherwise silent unless marimo renders markdown.

## Comments

**When to Comment:**
- Heavy use of commented-out experimental code blocks to toggle steps (FFmpeg/OpenCV diagnostics, model prompts) inside `02-worktrees/chat-extraction/chat-extraction.py`; few inline clarifying comments.

**JSDoc/TSDoc:**
- Not applicable; no docstrings or structured doc comments present.

## Function Design

**Size:**
- Cells are short and single-purpose, often returning data or printing diagnostics; many placeholder cells return immediately.

**Parameters:**
- Parameters mirror marimo dependency injection (e.g., `def _(Markdown, client, compressed_frame, image_file_to_data_url):`), pulling values from prior cells rather than explicit argument passing.

**Return Values:**
- Cells typically return tuples or nothing; no explicit result objects or error propagation.

## Module Design

**Exports:**
- Modules expose a single `app = marimo.App(...)` entry point; no reusable helpers or classes are exported.

**Barrel Files:**
- None; single-module layout without packaging structure.

---

*Convention analysis: 2026-02-21*
