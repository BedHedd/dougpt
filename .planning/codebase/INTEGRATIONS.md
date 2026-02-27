# External Integrations

**Analysis Date:** 2026-02-26

## APIs & External Services

**LLM/VLM Inference:**
- OpenAI-compatible Chat Completions API - structured vision/text extraction workflow.
  - SDK/Client: `openai` client usage shown in `00-dev-log/2026-02-01.md` and compatibility handling in `00-dev-log/2026-02-09.md`.
  - Auth: API key passed to client (`api_key`) in examples in `00-dev-log/2026-02-01.md`.
- Local LM Studio endpoint - local inference server used via OpenAI-compatible base URLs.
  - SDK/Client: `OpenAI(base_url="http://localhost:1234/v0")` and `OpenAI(base_url="http://localhost:1234/v1")` shown in `00-dev-log/2026-02-01.md`.
  - Auth: local key placeholder (`api_key="lm-studio"` / `"unused"`) in `00-dev-log/2026-02-01.md`.
- Azure OpenAI - provider configuration template exists.
  - SDK/Client: OpenAI-compatible variables defined in `00-supporting-files/data/sample.env.file`.
  - Auth: `AZURE_OPENAI_API_KEY` in `00-supporting-files/data/sample.env.file`.
- NVIDIA NIMs API - provider configuration template exists.
  - SDK/Client: base URL `https://integrate.api.nvidia.com/v1` in `00-supporting-files/data/sample.env.file`.
  - Auth: `NIMS_API_KEY` in `00-supporting-files/data/sample.env.file`.

**Media/Data Sources:**
- YouTube - source VOD download and reference links for dataset generation.
  - SDK/Client: `yt-dlp` CLI usage in `00-dev-log/2026-01-04.md`.
  - Auth: Not required for documented public URLs in `00-dev-log/2026-01-01.md` and `00-dev-log/2026-01-04.md`.

## Data Storage

**Databases:**
- Not detected.
  - Connection: Not applicable.
  - Client: Not applicable.

**File Storage:**
- Local filesystem only.
  - Raw/derived artifacts live under `00-supporting-files/data/` (for example `00-supporting-files/data/extractions/extractions.jsonl`, `00-supporting-files/data/extractions/metrics.jsonl`, and `00-supporting-files/data/chat_frames_test_30s_color/`).
  - Source video path references external local folder `/home/bedhedd/Documents/development_projects/bedhedd_projects/dougpt/large-files/...` from `00-supporting-files/data/full_chat_frames_report.json`.

**Caching:**
- Local file cache directories only (`00-supporting-files/data/keyframe_cache/`, `00-supporting-files/data/cropped_keyframe_cache/`, `00-supporting-files/data/ai_invasion_1_keyframe_cache/`).

## Authentication & Identity

**Auth Provider:**
- API-key based provider auth for LLM services.
  - Implementation: environment variables in `00-supporting-files/data/sample.env.file`, plus runtime key passing in `00-dev-log/2026-02-01.md`.

## Monitoring & Observability

**Error Tracking:**
- None detected.

**Logs:**
- File-based run metrics and failure capture pattern.
  - Execution token/latency metrics in `00-supporting-files/data/extractions/metrics.jsonl`.
  - Failure logging strategy discussed with `failed_extractions_out` in `00-dev-log/2026-02-09.md`.

## CI/CD & Deployment

**Hosting:**
- Not detected (no deployment manifests or hosting configs in tracked files).

**CI Pipeline:**
- None detected (no `.github/workflows/*`, GitLab CI, or other CI config files present).

## Environment Configuration

**Required env vars:**
- `OPENAI_API_TYPE`
- `OPENAI_API_VERSION`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `NIMS_BASE_URL`
- `NIMS_API_KEY`
- Variables are defined as template placeholders in `00-supporting-files/data/sample.env.file`.

**Secrets location:**
- `.env` file present at `00-supporting-files/data/.env` (values intentionally not read).

## Webhooks & Callbacks

**Incoming:**
- None detected.

**Outgoing:**
- None detected.

---

*Integration audit: 2026-02-26*
