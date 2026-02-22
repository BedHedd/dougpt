# Architecture

**Analysis Date:** 2026-02-21

## Pattern Overview

**Overall:** Interactive notebook-style pipeline (marimo app + ad hoc cells)

**Key Characteristics:**
- Marimo cells orchestrate path discovery, media extraction, and LLM prompts in `02-worktrees/chat-extraction/chat-extraction.py`
- Shared data (frames, cached outputs) live outside code under `00-supporting-files/`
- Vision model requests flow through the OpenAI Python client pointed at a local server (`http://localhost:1234/v1`)

## Layers

**Application Notebook:**
- Purpose: Drive video frame extraction and chat text detection experiments via marimo UI cells.
- Location: `02-worktrees/chat-extraction/chat-extraction.py`
- Contains: marimo cell definitions, path resolution helpers, ffmpeg/OpenCV experiments, OpenAI client calls, structured prompt drafts.
- Depends on: `opencv-python`, `openai`, local ffmpeg binaries, images in `00-supporting-files/data/` and `00-supporting-files/images/`.
- Used by: marimo runtime when launching the app.

**Shared Data Assets:**
- Purpose: Source media for experiments and cached intermediate outputs.
- Location: `00-supporting-files/data/`, `00-supporting-files/images/`
- Contains: keyframe caches, cropped chat frame sets, example images, extraction outputs.
- Depends on: External tooling (ffmpeg/OpenCV) and filesystem layout.
- Used by: marimo cells that read frames, send images to models, and display outputs.

**Worktree Shells:**
- Purpose: Isolate branch-specific workspaces and dependencies.
- Location: `02-worktrees/00-experiments/`, `02-worktrees/chat-extraction/`, `02-worktrees/old-master/`
- Contains: Branch-local `pyproject.toml`, notebooks, optional `.venv/` environments.
- Depends on: uv/venv tooling for dependency resolution.
- Used by: Developers per branch; only `chat-extraction` has functional code.

## Data Flow

**Chat extraction experiment:**

1. Resolve project roots and shared assets by walking parents to locate `00-supporting-files` (`chat-extraction.py`, early cells using `pathlib.Path`).
2. Define media sources: `video_dir` points to `../large-files`, image inputs come from `00-supporting-files/data/chat_frames_test_30s_color` or cached PNGs in `00-supporting-files/data` and `00-supporting-files/images`.
3. (Optional) Extract compressed frames via ffmpeg/OpenCV to PNGs for inspection (commented cells running subprocess commands).
4. Build OpenAI client targeting a local server and convert images to data URLs before sending prompts that request chat message text/emote bounding boxes (`chat-extraction.py`, OpenAI cells).
5. Display model responses inline in the marimo UI; future cells sketch pydantic schemas for structured outputs but keep them commented.

**State Management:**
- marimo manages reactive cell state; no persistent state beyond files under `00-supporting-files`.

## Key Abstractions

**Path resolution helper:**
- Purpose: Discover repository root and supporting files directory regardless of launch location.
- Examples: `chat-extraction.py` cells computing `start`, `project_parent`, `supporting_files`.
- Pattern: Walk parent directories with `Path.parents` until `00-supporting-files` is found.

**Vision model request wrapper:**
- Purpose: Encapsulate OpenAI client setup and image-to-data-URL conversion for vision prompts.
- Examples: `image_file_to_data_url` and `client = OpenAI(...)` in `chat-extraction.py`.
- Pattern: Build base64 data URLs, send `chat.completions.create` with mixed text/image content.

**Structured output schema (sketched):**
- Purpose: Define pydantic models for chat message extraction and emote bounding boxes.
- Examples: Commented `EmoteBox`, `ChatMessage`, `BatchExtraction` classes in `chat-extraction.py`.
- Pattern: pydantic `BaseModel` with typed fields and descriptions for OpenAI tool/response parsing.

## Entry Points

**marimo app:**
- Location: `02-worktrees/chat-extraction/chat-extraction.py`
- Triggers: Run via `marimo run chat-extraction.py` (or equivalent) inside `02-worktrees/chat-extraction` environment.
- Responsibilities: Initialize paths, reference media assets, optionally run ffmpeg/OpenCV diagnostics, invoke vision models, and render responses.

**Notebooks:**
- Locations: `02-worktrees/chat-extraction/chat-extraction-script.ipynb`, `02-worktrees/chat-extraction/extraction-review.ipynb`, `02-worktrees/chat-extraction/sandbox.ipynb`
- Triggers: Open in Jupyter-compatible environment per worktree.
- Responsibilities: Ad hoc exploration; no reusable library code.

## Error Handling

**Strategy:** Pragmatic, print-driven validation within cells; no centralized exception handling.

**Patterns:**
- Inspect subprocess return codes from ffmpeg/OpenCV calls and print stderr (`chat-extraction.py`, ffmpeg cell).
- Rely on marimo to surface exceptions inline; no retries or guards around OpenAI calls.

## Cross-Cutting Concerns

**Logging:** Inline `print` statements in cells; no structured logging.
**Validation:** Commented pydantic schemas intended for LLM structured output; not enforced at runtime.
**Authentication:** OpenAI client configured with placeholder API key (`unused`) and local `base_url`; expects external service to handle auth.

---

*Architecture analysis: 2026-02-21*
