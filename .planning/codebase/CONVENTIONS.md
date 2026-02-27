# Coding Conventions

**Analysis Date:** 2026-02-26

## Naming Patterns

**Files:**
- Use `snake_case.py` for Python modules in `src/transcription/models.py` and `src/transcription/__init__.py`.
- Keep notebook filenames descriptive and hyphenated for workflow context, as in `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.

**Functions:**
- Use `snake_case` for function names in notebook pipeline code, e.g. `run_transcription_stage` and `normalize_and_validate_segments` in `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.

**Variables:**
- Use `snake_case` for locals and dictionary keys in `src/transcription/models.py` and `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.
- Use `UPPER_SNAKE_CASE` for runtime-tunable constants/config roots, e.g. `CONFIG` and `RUN_CONFIG` in `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.

**Types:**
- Use `PascalCase` for model/type classes, e.g. `WordTimestamp`, `TranscriptResult`, and `TranscriptMetadata` in `src/transcription/models.py`.
- Use Python 3.10+ type syntax (`list[...]`, `dict[...]`, `X | None`) in both `src/transcription/models.py` and `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.

## Code Style

**Formatting:**
- Tool used: Not detected (no formatter config found in repository root; `pyproject.toml`, `ruff.toml`, and `.black` config files are not present at `/home/bedhedd/Documents/development_projects/bedhedd_projects/dougpt/dougpt`).
- Key settings: Follow existing style from `src/transcription/models.py` and `02-worktrees/audio-extraction-review/audio-extraction.ipynb`: 4-space indentation, double-quoted strings, trailing commas in multiline literals, and line wraps around ~88-100 chars.

**Linting:**
- Tool used: Not detected (no lint config files committed; no `pyproject.toml`, `.ruff.toml`, `.flake8`, or `setup.cfg` present at `/home/bedhedd/Documents/development_projects/bedhedd_projects/dougpt/dougpt`).
- Key rules: Enforce type hints and descriptive model fields by convention, based on `src/transcription/models.py` and `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.

## Import Organization

**Order:**
1. Future import first when needed (`from __future__ import annotations`) in `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.
2. Standard library imports next (`json`, `os`, `subprocess`, `Path`, typing) in `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.
3. Third-party and local imports last (`pydantic` in `src/transcription/models.py`, package export import in `src/transcription/__init__.py`), with optional dependency imports inside functions for graceful fallback in `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.

**Path Aliases:**
- No alias system detected; use package-qualified imports such as `from src.transcription.models import ...` in `src/transcription/__init__.py`.

## Error Handling

**Patterns:**
- Use guard clauses for expected precondition failures and return structured status dictionaries in `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.
- Wrap integration boundaries in `try/except` and either return explicit fallback metadata (e.g., diarization fallback) or raise typed runtime errors (`RuntimeError`) in `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.
- Capture exception context for run artifacts with `traceback.format_exc()` in stage functions in `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.

## Logging

**Framework:** File-based JSONL records via helper functions; no `logging` module usage detected in `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.

**Patterns:**
- Use append-only JSONL logs (`append_jsonl`) per stage and per run in `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.
- Include stable keys (`run_id`, `timestamp`, `stage`, `status`, `error`) in log records in `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.

## Comments

**When to Comment:**
- Prefer concise docstrings for module and class intent in `src/transcription/models.py` and `src/transcription/__init__.py`.
- Use inline comments only for non-obvious context, e.g. absolute path provenance in `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.

**JSDoc/TSDoc:**
- Not applicable for this Python codebase; Python docstrings are used in `src/transcription/models.py` and `src/transcription/__init__.py`.

## Function Design

**Size:** Use small, single-purpose helpers (`ffprobe_duration_seconds`, `output_audio_path`) and compose them in stage orchestrators (`run_extraction_stage`, `run_transcription_stage`, `run_pipeline`) in `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.

**Parameters:**
- Use explicit typed parameters; prefer keyword-only parameters for complex functions via `*` in `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.
- Pass shared runtime state as `config: dict[str, Any]` and `paths: dict[str, Path]` in `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.

**Return Values:**
- Return structured dictionaries with status and metrics for stage outputs in `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.
- Return Pydantic model instances for schema-level objects in `src/transcription/models.py`.

## Module Design

**Exports:**
- Re-export public API from package `__init__.py` and lock the surface with `__all__` in `src/transcription/__init__.py`.
- Keep schema definitions centralized in `src/transcription/models.py`.

**Barrel Files:**
- Use package barrel export at `src/transcription/__init__.py`; no additional barrel layers detected.

---

*Convention analysis: 2026-02-26*
