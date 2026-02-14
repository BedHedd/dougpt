# Technology Stack

**Analysis Date:** 2026-02-13

## Languages

**Primary:**
- Python 3.13 (pinned on `00-experiments` branch via `.python-version`)
- Markdown - Documentation, dev logs, and Foam templates

**Secondary:**
- None detected

## Runtime

**Environment:**
- Python 3.13 (pinned on `00-experiments` branch)
- Virtual environment managed by uv on experiment branches

**Package Manager:**
- uv (on `00-experiments` branch — `pyproject.toml` + `uv.lock`)
- Template branches (master/vibe-coding) have no package manager — by design

## Frameworks

**Core:**
- None on template branches — application frameworks are branch-specific
- `00-experiments` branch includes: ipykernel, openai, python-dotenv

**Testing:**
- None configured - no test framework detected

**Build/Dev:**
- Foam (VS Code extension) - Knowledge management / note templates in `.foam/templates/`
- Git submodules - Used for embedding external repos (see `.gitmodules`)
- Git worktrees - Supported workflow for parallel development (see `02-worktrees/README.md`)

## Key Dependencies

**Critical:**
- ipykernel >=6.29.5 (on `00-experiments` branch)
- openai >=1.91.0 (on `00-experiments` branch)
- python-dotenv >=1.1.0 (on `00-experiments` branch)

**Infrastructure:**
- Git submodule: `01-dev-onboarding` from `https://github.com/progressEdd/dev-onboarding.git` (master branch)

## Configuration

**Environment:**
- `.env` is gitignored
- `00-supporting-files/data/sample.env.file` exists as a reference template (contents blocked from reading)
- No environment variable loading code detected

**Build:**
- No build configuration files present
- `.gitignore` is comprehensive Python-oriented (covers `__pycache__`, `.venv`, `.env`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache/`, etc.)

## Platform Requirements

**Development:**
- Git with submodule support
- VS Code with Foam extension (optional, for knowledge management)
- Python 3.13 interpreter (pinned on experiment branches)

**Production:**
- No deployment target configured — this is a project template; deployment is branch-specific

---

*Stack analysis: 2026-02-13*
