# External Integrations

**Analysis Date:** 2026-02-21

## APIs & External Services

**Model Inference APIs:**
- OpenAI-compatible local API - Used for multimodal chat completion calls in the extraction workflow.
  - SDK/Client: `openai` package (`02-worktrees/chat-extraction/pyproject.toml`), used in `02-worktrees/chat-extraction/chat-extraction.py`.
  - Auth: `api_key` argument passed inline with placeholder value in `02-worktrees/chat-extraction/chat-extraction.py` (no named env var detected).
- Local LLM server endpoint - Requests target `http://localhost:1234/v1` (and commented alternative `http://localhost:8000/v1`) in `02-worktrees/chat-extraction/chat-extraction.py`.
  - SDK/Client: `openai` Python client configured with custom `base_url` in `02-worktrees/chat-extraction/chat-extraction.py`.
  - Auth: placeholder key pattern (`api_key="unused"`) in `02-worktrees/chat-extraction/chat-extraction.py`.

**Package Registry:**
- PyPI - Dependency artifacts resolved from `https://pypi.org/simple` via uv lockfiles (`02-worktrees/00-experiments/uv.lock`, `02-worktrees/chat-extraction/uv.lock`, `02-worktrees/old-master/uv.lock`).
  - SDK/Client: uv package manager and lock format (`02-worktrees/*/uv.lock`, `02-worktrees/*/README.md`).
  - Auth: Not applicable.

## Data Storage

**Databases:**
- Not detected.
  - Connection: Not applicable.
  - Client: Not applicable.

**File Storage:**
- Local filesystem only.
  - Inputs and derived assets are read/written under `00-supporting-files/` and project-adjacent paths referenced in `02-worktrees/chat-extraction/chat-extraction.py`.
  - Video/media source paths are constructed from local directories (for example `large-files`) in `02-worktrees/chat-extraction/chat-extraction.py`.

**Caching:**
- None detected as a dedicated service.

## Authentication & Identity

**Auth Provider:**
- Custom/local-only placeholder auth for local model endpoints.
  - Implementation: OpenAI client receives inline placeholder token strings in `02-worktrees/chat-extraction/chat-extraction.py`; no OAuth, JWT provider, or external identity service is integrated.

## Monitoring & Observability

**Error Tracking:**
- None detected.

**Logs:**
- Ad hoc stdout/print logging in notebook cells (`02-worktrees/chat-extraction/chat-extraction.py`).

## CI/CD & Deployment

**Hosting:**
- Not detected.

**CI Pipeline:**
- None detected (no `.github/workflows/` present in tracked root tree; workflow appears local-first via notebooks and worktrees described in `02-worktrees/README.md`).

## Environment Configuration

**Required env vars:**
- Not explicitly required by checked-in code paths.
- `python-dotenv` is present and imported in `02-worktrees/chat-extraction/chat-extraction.py`, but no specific `os.getenv("...")` contract is defined in scanned source files.

**Secrets location:**
- `.env` conventions are implied and ignored by `.gitignore`, `02-worktrees/chat-extraction/.gitignore`, and `02-worktrees/old-master/.gitignore`.
- No secrets files are committed in scanned root/worktree directories.

## Webhooks & Callbacks

**Incoming:**
- None detected.

**Outgoing:**
- None detected (API usage is request/response client calls in `02-worktrees/chat-extraction/chat-extraction.py`, not webhook dispatch).

---

*Integration audit: 2026-02-21*
