# External Integrations

**Analysis Date:** 2026-02-21

## APIs & External Services

**LLM/VLM:**
- OpenAI-compatible server (e.g., LM Studio / llama-server) – used for chat and vision model completions in marimo apps (`02-worktrees/chat-extraction/chat-extraction.py`, `02-worktrees/old-master/02-development/chat-extraction/chat-extraction.py`).
  - SDK/Client: `openai` Python SDK (`openai.OpenAI` with `base_url="http://localhost:1234/v1"`).
  - Auth: API key passed as `"unused"`; recommend storing a real token in `.env` as `OPENAI_API_KEY` when targeting hosted endpoints.

## Data Storage

**Databases:**
- Not detected

**File Storage:**
- Local filesystem only; video sources expected in `../large-files` relative to worktrees, and processed images/frames in `00-supporting-files/data` (`02-worktrees/chat-extraction/chat-extraction.py`).

**Caching:**
- None

## Authentication & Identity

**Auth Provider:**
- None; OpenAI-compatible calls accept a token but examples use a placeholder key for local servers.

## Monitoring & Observability

**Error Tracking:**
- None

**Logs:**
- Standard console output from marimo cells and FFmpeg commands.

## CI/CD & Deployment

**Hosting:**
- Local notebooks/marimo apps; no deployment target defined.

**CI Pipeline:**
- None

## Environment Configuration

**Required env vars:**
- `OPENAI_API_KEY` (recommended when pointing to hosted OpenAI-compatible services)
- `OPENAI_BASE_URL` or similar override if not using the default; current notebooks hardcode `http://localhost:1234/v1`.

**Secrets location:**
- `.env` at `00-supporting-files/data/.env` (not inspected); loaded via `python-dotenv` in marimo notebooks.

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

---

*Integration audit: 2026-02-21*
