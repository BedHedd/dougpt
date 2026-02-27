# Technology Stack

**Analysis Date:** 2026-02-26

## Languages

**Primary:**
- Python 3.13 - Application code in `src/transcription/models.py` and `src/transcription/__init__.py`

**Secondary:**
- Markdown - Project and process docs in `README.md`, `00-dev-log/*.md`, and `02-worktrees/README.md`
- JSON - Pipeline artifacts and structured outputs in `00-supporting-files/data/audio-extraction-review/**/*.json`

## Runtime

**Environment:**
- CPython 3.13 (local virtual environment path `/.venv/lib/python3.13/`)

**Package Manager:**
- pip/venv workflow (virtual environment present at `/.venv/`)
- Lockfile: missing (no `requirements.txt`, `pyproject.toml`, `poetry.lock`, or `uv.lock` detected in repository root)

## Frameworks

**Core:**
- Pydantic (version not pinned in repository manifests) - Typed data models for transcription entities in `src/transcription/models.py`

**Testing:**
- Not detected (no `pytest`, `unittest`, `jest`, `vitest`, or test config files committed)

**Build/Dev:**
- Git submodules - External onboarding repository wiring in `.gitmodules`
- Git worktrees - Parallel branch workflow documented in `02-worktrees/README.md`

## Key Dependencies

**Critical:**
- `pydantic` (imported directly) - Model validation and schema typing in `src/transcription/models.py:3`

**Infrastructure:**
- ffmpeg (toolchain dependency inferred from run artifacts) - Audio extraction settings captured in `00-supporting-files/data/audio-extraction-review/runs/run-20260222T030354Z-206b1285.json:27`
- faster-whisper (inferred from transcript artifacts) - Transcription engine recorded in `00-supporting-files/data/audio-extraction-review/transcripts/sample-single.json:11`
- whisperx (inferred from run artifacts) - Diarization provider recorded in `00-supporting-files/data/audio-extraction-review/transcripts/sample-single.json:22`

## Configuration

**Environment:**
- Local environment file exists at `00-supporting-files/data/.env` (contents intentionally not read)
- Sample env template defines external API settings in `00-supporting-files/data/sample.env.file`
- Source code package exports are configured via `src/transcription/__init__.py`

**Build:**
- No committed build config files detected (`pyproject.toml`, `setup.py`, `Dockerfile`, CI workflow YAML not present)

## Platform Requirements

**Development:**
- Python runtime with virtual environment support (`/.venv/` expected)
- Local filesystem access for media/data paths used in artifacts (`00-supporting-files/data/audio-extraction-review/runs/run-20260222T030354Z-206b1285.json`)

**Production:**
- Not detected (no deployment target, container config, or CI/CD pipeline definitions committed)

---

*Stack analysis: 2026-02-26*
