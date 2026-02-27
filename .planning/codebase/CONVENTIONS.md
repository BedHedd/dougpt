# Coding Conventions

**Analysis Date:** 2026-02-26

## Naming Patterns

**Files:**
- Use `snake_case.py` for module filenames, as shown in `src/transcription/models.py` and package initializer `src/transcription/__init__.py`.

**Functions:**
- Not applicable in current source slice; no functions are defined in `src/transcription/models.py` or `src/transcription/__init__.py`.

**Variables:**
- Use `snake_case` for model attributes (`language_probability`, `duration_seconds`, `batch_size`) in `src/transcription/models.py`.

**Types:**
- Use `PascalCase` for Pydantic model classes (`WordTimestamp`, `TranscriptSegment`, `TranscriptResult`, `TranscriptMetadata`) in `src/transcription/models.py`.

## Code Style

**Formatting:**
- Formatter configuration file not detected (no `pyproject.toml`, `ruff.toml`, `setup.cfg`, or `tox.ini` in repository root).
- Keep line lengths moderate and wrap long calls with hanging indentation, matching `Field(...)` blocks in `src/transcription/models.py`.

**Linting:**
- Linter configuration file not detected in tracked root files (`.gitignore`, `README.md`, `.gitmodules`).
- `.gitignore` includes `.ruff_cache/`, indicating Ruff usage is expected locally even though project-level rules are not committed (`.gitignore`).

## Import Organization

**Order:**
1. Start with a module docstring (`src/transcription/models.py`, `src/transcription/__init__.py`).
2. Use grouped import statements directly under the docstring (`from pydantic import BaseModel, Field` in `src/transcription/models.py`).
3. Export public API via explicit import list and `__all__` in package init (`src/transcription/__init__.py`).

**Path Aliases:**
- No alias system detected; imports use explicit package paths such as `from src.transcription.models import ...` in `src/transcription/__init__.py`.

## Error Handling

**Patterns:**
- Error-handling conventions are not represented in committed Python source; only schema definitions are present in `src/transcription/models.py`.
- Use Pydantic validation as the current defensive boundary for data shape and type enforcement (`src/transcription/models.py`).

## Logging

**Framework:** console

**Patterns:**
- Logging pattern not detected in committed runtime modules (`src/transcription/models.py`, `src/transcription/__init__.py`).

## Comments

**When to Comment:**
- Use concise module/class docstrings to describe intent, as in `src/transcription/models.py` and `src/transcription/__init__.py`.
- Prefer descriptive `Field(description=...)` metadata for attribute-level documentation in `src/transcription/models.py`.

**JSDoc/TSDoc:**
- Not applicable; repository code in scope is Python and uses Python docstrings (`src/transcription/models.py`).

## Function Design

**Size:**
- Not applicable in current committed Python modules (`src/transcription/models.py`, `src/transcription/__init__.py`).

**Parameters:**
- Not applicable in current committed Python modules (`src/transcription/models.py`, `src/transcription/__init__.py`).

**Return Values:**
- Not applicable in current committed Python modules (`src/transcription/models.py`, `src/transcription/__init__.py`).

## Module Design

**Exports:**
- Define a narrow package API with explicit re-exports and `__all__`, matching `src/transcription/__init__.py`.

**Barrel Files:**
- Use package-level aggregator modules (`src/transcription/__init__.py`) to centralize public imports from implementation modules (`src/transcription/models.py`).

---

*Convention analysis: 2026-02-26*
