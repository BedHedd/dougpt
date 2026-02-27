# Technology Stack

**Analysis Date:** 2026-02-26

## Languages

**Primary:**
- Python 3.13.3 - typed domain models in `src/transcription/models.py` and package exports in `src/transcription/__init__.py`

**Secondary:**
- Markdown - project/process documentation and embedded code snippets in `README.md` and `00-dev-log/2026-02-01.md`
- JSON/JSONL - pipeline run metadata and artifacts in `00-supporting-files/data/audio-extraction-review/runs/run-20260222T030354Z-206b1285.json` and `00-supporting-files/data/audio-extraction-review/logs/transcription-20260222T023330Z-f9bdbf0d.jsonl`

## Runtime

**Environment:**
- CPython 3.13.3 (virtual environment metadata) in `.venv/pyvenv.cfg`

**Package Manager:**
- uv 0.10.2 (venv creator) in `.venv/pyvenv.cfg`
- Lockfile: missing (no `uv.lock`, `poetry.lock`, `Pipfile.lock`, or `requirements.txt` at project root)

## Frameworks

**Core:**
- Pydantic 2.12.5 - schema/type validation for transcription models in `src/transcription/models.py` and package metadata in `.venv/lib/python3.13/site-packages/pydantic-2.12.5.dist-info/METADATA`

**Testing:**
- Not detected (no `pytest`, `unittest`, `nose`, `tox`, or test config files tracked)

**Build/Dev:**
- FFmpeg CLI - audio extraction/transcode settings captured in `00-supporting-files/data/audio-extraction-review/runs/run-20260222T023330Z-f9bdbf0d.json` and command examples in `00-dev-log/2026-01-04.md`
- Jupyter Notebook workflow - exploratory notebooks in `02-worktrees/audio-extraction-review/audio-extraction.ipynb` and `02-worktrees/extraction-exploration/extraction-review.ipynb`

## Key Dependencies

**Critical:**
- `pydantic==2.12.5` - enforces typed transcript schema contracts used by importers/consumers in `src/transcription/models.py`
- `pydantic-core==2.41.5` - runtime engine for Pydantic models in `.venv/lib/python3.13/site-packages/pydantic_core-2.41.5.dist-info/METADATA`

**Infrastructure:**
- `faster-whisper` (version not pinned in repo) - transcription engine recorded in artifact metadata `00-supporting-files/data/audio-extraction-review/transcripts/sample-single.json`
- `whisperx` (version not pinned in repo) - diarization provider recorded in run snapshots `00-supporting-files/data/audio-extraction-review/runs/run-20260222T023331Z-42b31623.json`
- `openai` SDK (version not pinned in repo) - OpenAI-compatible client usage in workflow notes `00-dev-log/2026-02-01.md`

## Configuration

**Environment:**
- Environment file path is referenced by runs as `00-supporting-files/data/.env` in `00-supporting-files/data/audio-extraction-review/runs/run-20260222T030354Z-206b1285.json` (contents intentionally not read)
- Project contains a sample env file `00-supporting-files/data/sample.env.file` (contents intentionally not read)
- Key runtime knobs are serialized per run under `config_snapshot` in `00-supporting-files/data/audio-extraction-review/runs/run-20260222T023330Z-f9bdbf0d.json`

**Build:**
- No centralized build config detected (`pyproject.toml`, `setup.cfg`, `setup.py`, `Makefile`, and Dockerfiles not detected)
- Operational settings are run-local JSON snapshots in `00-supporting-files/data/audio-extraction-review/runs/*.json`

## Platform Requirements

**Development:**
- Linux-like local environment with Python 3.13 virtualenv paths under `.venv/` and absolute `/home/...` paths in `00-supporting-files/data/audio-extraction-review/runs/run-20260222T030354Z-206b1285.json`
- FFmpeg binary available on PATH for extraction/transcoding flows shown in `00-dev-log/2026-01-04.md`

**Production:**
- Not detected; repository is currently structured as local research/prototyping plus artifact storage (`src/`, `00-dev-log/`, `00-supporting-files/data/`)

---

*Stack analysis: 2026-02-26*
