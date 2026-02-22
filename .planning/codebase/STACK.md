# Technology Stack

**Analysis Date:** 2026-02-21

## Languages

**Primary:**
- Python 3.13 – interactive notebooks and scripts in `02-worktrees/chat-extraction`, `02-worktrees/00-experiments`, `02-worktrees/old-master` (`.python-version` in each worktree)

**Secondary:**
- Not detected

## Runtime

**Environment:**
- CPython 3.13 (per `02-worktrees/chat-extraction/.python-version`, `02-worktrees/00-experiments/.python-version`, `02-worktrees/old-master/.python-version`)

**Package Manager:**
- uv – Python dependency management (`02-worktrees/chat-extraction/pyproject.toml`, `02-worktrees/00-experiments/pyproject.toml`, `02-worktrees/old-master/pyproject.toml`)
- Lockfile: present (`02-worktrees/chat-extraction/uv.lock`, `02-worktrees/00-experiments/uv.lock`, `02-worktrees/old-master/uv.lock`)

## Frameworks

**Core:**
- marimo 0.19.4 – reactive notebook-style app framework used for chat extraction workflows (`02-worktrees/chat-extraction/chat-extraction.py`, `02-worktrees/old-master/02-development/chat-extraction/chat-extraction.py`)
- OpenAI Python SDK 1.93.0 – OpenAI-compatible client for VLM/VLM chat completion calls (`02-worktrees/chat-extraction/chat-extraction.py`, `02-worktrees/old-master/02-development/chat-extraction/chat-extraction.py`)

**Testing:**
- Not detected

**Build/Dev:**
- ipykernel / Jupyter stack – notebook execution support (`02-worktrees/chat-extraction/pyproject.toml`)
- FFmpeg (external) – invoked for compressed frame extraction in marimo cells (`02-worktrees/chat-extraction/chat-extraction.py`)

## Key Dependencies

**Critical:**
- `openai` 1.93.0 – OpenAI-compatible chat and vision API client (`02-worktrees/chat-extraction/chat-extraction.py`)
- `marimo` 0.19.4 – UI/runtime for interactive experiments (`02-worktrees/chat-extraction/chat-extraction.py`)

**Infrastructure:**
- `opencv-python` 4.12.0.88 – video frame capture and AV1/VAAPI experimentation (`02-worktrees/chat-extraction/chat-extraction.py`)
- `python-dotenv` 1.1.1 – loads `.env` for API/server config (`02-worktrees/chat-extraction/chat-extraction.py`)
- `pandas` 2.3.3 – data wrangling support (`02-worktrees/chat-extraction/pyproject.toml`)
- `pillow` 12.1.0 – image loading/processing (`02-worktrees/chat-extraction/pyproject.toml`)
- `plotly` 6.5.2 – visualization utilities (`02-worktrees/chat-extraction/pyproject.toml`)
- `pydantic` 2.11.7 – structured response modeling in experiments (`02-worktrees/chat-extraction/chat-extraction.py`)

## Configuration

**Environment:**
- Environment variables loaded via `python-dotenv`; `.env` present at `00-supporting-files/data/.env` (contents not inspected).
- OpenAI-compatible base URL and API key are set inline for local servers in marimo notebooks (e.g., `base_url="http://localhost:1234/v1"`, `api_key="unused"` in `02-worktrees/chat-extraction/chat-extraction.py`).

**Build:**
- Project metadata and dependencies defined in `pyproject.toml` files under `02-worktrees/chat-extraction/`, `02-worktrees/00-experiments/`, and `02-worktrees/old-master/`.

## Platform Requirements

**Development:**
- Python 3.13 with uv installed; run `uv sync` inside each worktree to create the virtual environment (per `02-worktrees/chat-extraction/README.md`).
- FFmpeg available on PATH for video frame extraction in marimo cells (`02-worktrees/chat-extraction/chat-extraction.py`).
- Local OpenAI-compatible server reachable at `http://localhost:1234/v1` for VLM experiments.

**Production:**
- Not defined; current usage is local experimentation via marimo notebooks and local OpenAI-compatible servers.

---

*Stack analysis: 2026-02-21*
