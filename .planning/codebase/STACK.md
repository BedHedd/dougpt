# Technology Stack

**Analysis Date:** 2026-02-21

## Languages

**Primary:**
- Python 3.13 - Application and experimentation code in `02-worktrees/chat-extraction/chat-extraction.py`, `02-worktrees/old-master/02-development/chat-extraction/chat-extraction.py`, and project manifests in `02-worktrees/*/pyproject.toml`.

**Secondary:**
- TOML - Project and dependency metadata in `02-worktrees/00-experiments/pyproject.toml`, `02-worktrees/chat-extraction/pyproject.toml`, `02-worktrees/old-master/pyproject.toml`, and lockfiles in `02-worktrees/*/uv.lock`.
- Jupyter Notebook JSON - Experiment notebooks in `02-worktrees/chat-extraction/chat-extraction-script.ipynb`, `02-worktrees/chat-extraction/extraction-review.ipynb`, and `02-worktrees/*/sandbox.ipynb`.
- Markdown - Project documentation in `README.md`, `02-worktrees/README.md`, and `02-worktrees/*/README.md`.

## Runtime

**Environment:**
- CPython 3.13 (minimum `>=3.13` in `02-worktrees/00-experiments/pyproject.toml`, `02-worktrees/chat-extraction/pyproject.toml`, `02-worktrees/old-master/pyproject.toml`; pinned locally via `02-worktrees/*/.python-version`).

**Package Manager:**
- uv (usage documented in `02-worktrees/README.md` and `02-worktrees/*/README.md` with `uv sync` and `uv add`).
- Lockfile: present (`02-worktrees/00-experiments/uv.lock`, `02-worktrees/chat-extraction/uv.lock`, `02-worktrees/old-master/uv.lock`).

## Frameworks

**Core:**
- marimo >=0.18.4 - Notebook app framework for interactive Python workflows (`02-worktrees/chat-extraction/pyproject.toml`, `02-worktrees/chat-extraction/chat-extraction.py`).
- openai >=1.91.0 - OpenAI-compatible client used for chat-completions inference (`02-worktrees/chat-extraction/pyproject.toml`, `02-worktrees/chat-extraction/chat-extraction.py`).

**Testing:**
- Not detected (no pytest/jest/vitest configs or test directories in repository root; `03-app/app.py` is empty at `02-worktrees/old-master/03-app/app.py`).

**Build/Dev:**
- ipykernel >=6.29.5 - Notebook kernel support (`02-worktrees/*/pyproject.toml`).
- python-dotenv >=1.1.0 - Local environment variable loading (`02-worktrees/chat-extraction/pyproject.toml`, imported in `02-worktrees/chat-extraction/chat-extraction.py`).
- opencv-python >=4.12.0.88, pandas >=2.3.3, pillow >=12.1.0, plotly >=6.5.2 - Data and vision tooling in the chat extraction workflow (`02-worktrees/chat-extraction/pyproject.toml`).

## Key Dependencies

**Critical:**
- `marimo` - Defines the executable app surface via `marimo.App(...)` and `@app.cell` orchestration in `02-worktrees/chat-extraction/chat-extraction.py`.
- `openai` - Drives model calls via `OpenAI(...).chat.completions.create(...)` in `02-worktrees/chat-extraction/chat-extraction.py`.
- `opencv-python` - Used for frame/video handling and FFmpeg-backed decoding experiments in `02-worktrees/chat-extraction/chat-extraction.py`.

**Infrastructure:**
- `uv` lock model - Reproducible Python environments backed by `02-worktrees/*/uv.lock`.
- `python-dotenv` - Intended local env configuration loader imported in `02-worktrees/chat-extraction/chat-extraction.py`.
- Git worktrees - Multi-branch workspace layout documented in `02-worktrees/README.md` and reflected by `02-worktrees/00-experiments`, `02-worktrees/chat-extraction`, `02-worktrees/old-master`.

## Configuration

**Environment:**
- Python version baseline is configured via `02-worktrees/00-experiments/.python-version`, `02-worktrees/chat-extraction/.python-version`, and `02-worktrees/old-master/.python-version`.
- `python-dotenv` is included and imported (`02-worktrees/chat-extraction/pyproject.toml`, `02-worktrees/chat-extraction/chat-extraction.py`), but no checked-in `.env` file is detected in scanned directories.
- `.env` files are ignored by policy in `.gitignore`, `02-worktrees/chat-extraction/.gitignore`, and `02-worktrees/old-master/.gitignore`.

**Build:**
- Build/package metadata is centralized in `02-worktrees/*/pyproject.toml`.
- Dependency resolution is pinned in `02-worktrees/*/uv.lock`.
- marimo runtime config is set in `02-worktrees/old-master/pyproject.toml` under `[tool.marimo.runtime]`.

## Platform Requirements

**Development:**
- Python 3.13 runtime (`02-worktrees/*/.python-version`, `02-worktrees/*/pyproject.toml`).
- uv installed for `uv sync` workflows (`02-worktrees/README.md`, `02-worktrees/*/README.md`).
- FFmpeg binary available for subprocess calls in extraction workflows (`02-worktrees/chat-extraction/chat-extraction.py`).

**Production:**
- Not detected (repository state is experimentation-oriented notebooks/worktrees with no deployment manifest or production service entrypoint; `02-worktrees/old-master/03-app/app.py` is empty).

---

*Stack analysis: 2026-02-21*
