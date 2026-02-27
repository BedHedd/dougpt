# External Integrations

**Analysis Date:** 2026-02-26

## APIs & External Services

**LLM APIs (configured/inferred):**
- OpenAI-compatible local endpoint (LM Studio) - Segment generation pipeline target recorded in `00-supporting-files/data/audio-extraction-review/runs/run-20260222T030354Z-206b1285.json:49`
  - SDK/Client: Not committed in source (endpoint metadata only in run artifact)
  - Auth: `api_key` field recorded in run metadata at `00-supporting-files/data/audio-extraction-review/runs/run-20260222T030354Z-206b1285.json:50`
- Azure OpenAI (template configuration) - Declared in sample environment template `00-supporting-files/data/sample.env.file:1`
  - SDK/Client: Not detected in committed source files under `src/`
  - Auth: `AZURE_OPENAI_API_KEY` in `00-supporting-files/data/sample.env.file:4`
- NVIDIA NIMS API (template configuration) - Base URL declared in `00-supporting-files/data/sample.env.file:6`
  - SDK/Client: Not detected in committed source files under `src/`
  - Auth: `NIMS_API_KEY` in `00-supporting-files/data/sample.env.file:7`

**Speech/Transcription Tooling (artifact-inferred):**
- faster-whisper - Transcription engine recorded in `00-supporting-files/data/audio-extraction-review/transcripts/sample-single.json:11`
  - SDK/Client: Not committed in repository code (engine usage captured in output artifacts)
  - Auth: None indicated in transcript artifact
- whisperx - Diarization provider recorded in `00-supporting-files/data/audio-extraction-review/transcripts/sample-single.json:22`
  - SDK/Client: Not committed in repository code (provider usage captured in output artifacts)
  - Auth: Hugging Face token dependency implied by fallback reason in `00-supporting-files/data/audio-extraction-review/transcripts/sample-single.json:24`

## Data Storage

**Databases:**
- Not detected
  - Connection: Not applicable
  - Client: Not applicable

**File Storage:**
- Local filesystem only (artifact directories under `00-supporting-files/data/audio-extraction-review/`)

**Caching:**
- Filesystem cache directories present (`00-supporting-files/data/keyframe_cache/`, `00-supporting-files/data/cropped_keyframe_cache/`, `00-supporting-files/data/ai_invasion_1_keyframe_cache/`)

## Authentication & Identity

**Auth Provider:**
- API key-based service auth only (no user identity provider detected)
  - Implementation: Environment variables/templates in `00-supporting-files/data/sample.env.file`; local `.env` file present at `00-supporting-files/data/.env` (contents not read)

## Monitoring & Observability

**Error Tracking:**
- None detected (no Sentry/Bugsnag/etc. integration files in repository root or `src/`)

**Logs:**
- JSONL run logs written to local paths captured in `00-supporting-files/data/audio-extraction-review/runs/run-20260222T030354Z-206b1285.json:69`

## CI/CD & Deployment

**Hosting:**
- Not detected

**CI Pipeline:**
- None detected (no `.github/workflows/*` files committed)

## Environment Configuration

**Required env vars:**
- `OPENAI_API_TYPE` (`00-supporting-files/data/sample.env.file:1`)
- `OPENAI_API_VERSION` (`00-supporting-files/data/sample.env.file:2`)
- `AZURE_OPENAI_ENDPOINT` (`00-supporting-files/data/sample.env.file:3`)
- `AZURE_OPENAI_API_KEY` (`00-supporting-files/data/sample.env.file:4`)
- `NIMS_BASE_URL` (`00-supporting-files/data/sample.env.file:6`)
- `NIMS_API_KEY` (`00-supporting-files/data/sample.env.file:7`)
- Hugging Face token required for diarization path (inferred from `missing_huggingface_token` in `00-supporting-files/data/audio-extraction-review/transcripts/sample-single.json:24`)

**Secrets location:**
- Local env file at `00-supporting-files/data/.env` (exists; contents intentionally not read)

## Webhooks & Callbacks

**Incoming:**
- None detected

**Outgoing:**
- None detected

---

*Integration audit: 2026-02-26*
