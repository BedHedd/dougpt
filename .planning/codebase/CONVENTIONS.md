# Coding Conventions

**Analysis Date:** 2026-02-26

## Naming Patterns

**Files:**
- Use kebab-case for marimo notebook exports, shown by `02-worktrees/chat-extraction/chat-extraction.py`.
- Use lowercase with underscores for Python module files when present in package-style code, shown by deleted-but-tracked paths `src/transcription/__init__.py` and `src/transcription/models.py` in `git status`.

**Functions:**
- Use marimo cell function signature `def _(...):` for notebook-exported execution blocks in `02-worktrees/chat-extraction/chat-extraction.py`.
- Use snake_case for helper and utility functions inside cells, e.g. `_safe_clamped_bbox`, `draw_emote_bboxes_safe`, `_parse_packets_pts`, `reduce_chat_frames_by_scroll_color` in `02-worktrees/chat-extraction/chat-extraction.py`.

**Variables:**
- Use snake_case for locals and parameters (`supporting_files`, `project_parent`, `bottom_change_thr`) in `02-worktrees/chat-extraction/chat-extraction.py`.
- Use UPPER_CASE for cell-local config constants (`MODEL`, `FRAMES_DIR`, `BASE_URL`, `API_KEY`) in `02-worktrees/chat-extraction/chat-extraction.py`.

**Types:**
- Use PascalCase for dataclasses and Pydantic models (`KeyframeReport`) in `02-worktrees/chat-extraction/chat-extraction.py`.
- Use explicit type aliases for path-like and compound types (`PathLike = Union[str, Path]`) in `02-worktrees/chat-extraction/chat-extraction.py`.

## Code Style

**Formatting:**
- Tool used: No formatter configuration detected (`.prettierrc*`, `eslint.config.*`, `biome.json`, `ruff.toml`, `pytest.ini` are not present at repo root).
- Practical rule: Keep style compatible with current source in `02-worktrees/chat-extraction/chat-extraction.py` (4-space indentation, trailing commas in multiline calls, typed signatures where logic is reusable).

**Linting:**
- Tool used: Not detected in repository-level config.
- Practical rule: Follow existing typed-Python style in `02-worktrees/chat-extraction/chat-extraction.py` because no enforced lint config is present.

## Import Organization

**Order:**
1. Keep marimo bootstrap import at top-level (`import marimo`) in `02-worktrees/chat-extraction/chat-extraction.py`.
2. Place most imports inside the cell where they are used (`from pathlib import Path`, `from dotenv import load_dotenv`, `import cv2`) in `02-worktrees/chat-extraction/chat-extraction.py`.
3. Group standard library before third-party inside a cell (`import json`, `import re`, then other libs) in `02-worktrees/chat-extraction/chat-extraction.py`.

**Path Aliases:**
- Not detected. Use direct module imports and `pathlib.Path` composition as shown in `02-worktrees/chat-extraction/chat-extraction.py`.

## Error Handling

**Patterns:**
- Wrap environment-dependent path resolution with narrow exceptions and fallback behavior (`try: start = Path(__file__).resolve() except NameError: start = Path.cwd()`) in `02-worktrees/chat-extraction/chat-extraction.py`.
- Convert subprocess failures into domain-level `RuntimeError` with actionable context in `_run` (`FileNotFoundError` and `subprocess.CalledProcessError`) in `02-worktrees/chat-extraction/chat-extraction.py`.
- Validate file/path preconditions early and raise specific exceptions (`FileNotFoundError`, `ValueError`) before expensive work in `keyframe_report` in `02-worktrees/chat-extraction/chat-extraction.py`.

## Logging

**Framework:** `print`

**Patterns:**
- Use lightweight progress prints during long loops (`[reduce] decoded=...`) in `reduce_chat_frames_by_scroll_color` at `02-worktrees/chat-extraction/chat-extraction.py`.
- Print diagnostic metadata for environment troubleshooting (`cv2.__file__`, `sys.executable`) in `02-worktrees/chat-extraction/chat-extraction.py`.
- Prefer structured JSON artifact output for durable debugging (`report.json`) rather than only console output in `02-worktrees/chat-extraction/chat-extraction.py`.

## Comments

**When to Comment:**
- Comment non-obvious algorithm choices and fallback intent (packets vs frames probing, bounds-clamping rationale) in `02-worktrees/chat-extraction/chat-extraction.py`.
- Keep exploratory cells commented instead of deleted for reproducibility during iteration in `02-worktrees/chat-extraction/chat-extraction.py`.

**JSDoc/TSDoc:**
- Not applicable (Python codebase). Use Python docstrings for reusable helpers (`keyframe_report`, `extract_keyframes`) as shown in `02-worktrees/chat-extraction/chat-extraction.py`.

## Function Design

**Size:**
- Keep marimo cell wrappers short and return only shared artifacts.
- Put complex logic into named helpers inside cells (for example `reduce_chat_frames_by_scroll_color` and `keyframe_report`) in `02-worktrees/chat-extraction/chat-extraction.py`.

**Parameters:**
- Use keyword-rich signatures with defaults for tuning-heavy pipelines (`lines_per_keep`, `min_corr`, `bottom_change_thr`) in `02-worktrees/chat-extraction/chat-extraction.py`.

**Return Values:**
- Return tuples from cells for dependency wiring (`return (video_dir,)`, `return (compact_batch,)`) in `02-worktrees/chat-extraction/chat-extraction.py`.
- Return typed domain objects or explicit lists from helpers (`KeyframeReport`, `list[Path]`, `list[KeptFrame]`) in `02-worktrees/chat-extraction/chat-extraction.py`.

## Module Design

**Exports:**
- Marimo app modules export behavior by `@app.cell` dependencies and terminate with `if __name__ == "__main__": app.run()` in `02-worktrees/chat-extraction/chat-extraction.py`.

**Barrel Files:**
- Not detected. No explicit re-export modules are present.

---

*Convention analysis: 2026-02-26*
