# Technology Stack

**Analysis Date:** 2026-02-26

## Languages

**Primary:**
- Python 3.13.3 - scripting and data-processing workflows are captured in code snippets within `00-dev-log/2026-02-01.md` and `00-dev-log/2026-01-25.md`, with the active venv runtime defined in `.venv/pyvenv.cfg`.

**Secondary:**
- Markdown - project documentation and execution notes in `README.md` and `00-dev-log/*.md`.
- JSON/JSONL - extracted dataset artifacts and run metrics in `00-supporting-files/data/extractions/extractions.jsonl`, `00-supporting-files/data/extractions/metrics.jsonl`, and `00-supporting-files/data/full_chat_frames_report.json`.

## Runtime

**Environment:**
- CPython 3.13.3 (uv-managed venv) from `.venv/pyvenv.cfg`.

**Package Manager:**
- uv 0.10.4 (CLI on host) and uv 0.10.2 metadata in `.venv/pyvenv.cfg`.
- Lockfile: missing (`uv.lock`, `poetry.lock`, `Pipfile.lock`, and `package-lock.json` are not present in the repository root).

## Frameworks

**Core:**
- No application framework detected in tracked source files; the repo currently acts as a research/documentation workspace centered on scripts documented in `00-dev-log/*.md`.

**Testing:**
- Not detected (no `pytest`, `unittest`, `jest`, `vitest`, or test configuration files found in tracked files).

**Build/Dev:**
- ffmpeg (system CLI) - frame extraction and video encoding workflow documented in `00-dev-log/2026-01-04.md` and `00-dev-log/2026-01-25.md`.
- yt-dlp (system CLI) - YouTube media acquisition documented in `00-dev-log/2026-01-04.md`.
- Git submodules/worktrees - repository composition and parallel branches described in `.gitmodules` and `02-worktrees/README.md`.

## Key Dependencies

**Critical:**
- `pydantic` 2.12.5 - structured extraction schemas and validation pattern (`ChatExtraction`, `ChatMessage`, `EmoteBox`) shown in `00-dev-log/2026-02-01.md`; package currently installed in the local venv (`uv pip list --python .venv/bin/python`).
- `openai` (version not pinned in repo) - OpenAI-compatible chat completion client usage shown in `00-dev-log/2026-02-01.md` and SDK compatibility handling shown in `00-dev-log/2026-02-09.md`.

**Infrastructure:**
- `python-dotenv` (version not pinned in repo) - environment loading usage (`load_dotenv`) shown in `00-dev-log/2026-02-01.md`.
- `requests` (version not pinned in repo) - HTTP client import shown in `00-dev-log/2026-02-01.md`.

## Configuration

**Environment:**
- `.env` file present at `00-supporting-files/data/.env` (contains environment configuration; contents intentionally not inspected).
- Example env template at `00-supporting-files/data/sample.env.file` indicates required provider variables for OpenAI-compatible endpoints.

**Build:**
- No dedicated build-system config files detected (`pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`, `Dockerfile`, and CI pipeline files are not present at repo root).

## Platform Requirements

**Development:**
- Linux/macOS shell with `uv`, Python 3.13.x, and `ffmpeg` available; runtime behavior indicates local model endpoint access at `http://localhost:1234` from `00-dev-log/2026-02-01.md`.
- Access to large media assets outside git at sibling path `/home/bedhedd/Documents/development_projects/bedhedd_projects/dougpt/large-files` referenced by `00-supporting-files/data/full_chat_frames_report.json`.

**Production:**
- Not detected; current tracked files describe local/offline dataset preparation rather than a deployed service (`README.md`, `00-dev-log/*.md`).

---

*Stack analysis: 2026-02-26*
