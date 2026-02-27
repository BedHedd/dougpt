# External Integrations

**Analysis Date:** 2026-02-26

## APIs & External Services

**LLM inference (OpenAI-compatible local endpoint):**
- LM Studio-hosted local API - transcript segmentation/summarization in run config snapshots
  - SDK/Client: `openai` Python client usage shown in `00-dev-log/2026-02-01.md`
  - Endpoint: `http://localhost:1234/v1` captured in `00-supporting-files/data/audio-extraction-review/runs/run-20260222T030354Z-206b1285.json`
  - Auth: API key field configured per run (`api_key` key in run JSON); env var name not explicitly codified in tracked files

**Speech transcription/diarization engines:**
- Faster-Whisper - ASR engine recorded in transcript metadata `00-supporting-files/data/audio-extraction-review/transcripts/sample-single.json`
  - SDK/Client: runtime pipeline (source file not tracked in this branch); evidence in `transcription.engine`
  - Auth: none required in observed run snapshots
- WhisperX diarization - speaker diarization provider recorded in run snapshots `00-supporting-files/data/audio-extraction-review/runs/run-20260222T023330Z-f9bdbf0d.json`
  - SDK/Client: runtime pipeline (source file not tracked in this branch)
  - Auth: Hugging Face token required when diarization is enabled; missing-token fallback logged as `missing_huggingface_token` in `00-supporting-files/data/audio-extraction-review/logs/transcription-20260222T023330Z-f9bdbf0d.jsonl`

**Media ingestion tools:**
- FFmpeg - media decode/extraction/transcode operations in `00-dev-log/2026-01-04.md` and run `config_snapshot.ffmpeg` in `00-supporting-files/data/audio-extraction-review/runs/run-20260222T023331Z-42b31623.json`
- yt-dlp - manual source video download step documented in `00-dev-log/2026-01-04.md`

## Data Storage

**Databases:**
- Not detected
  - Connection: Not applicable
  - Client: Not applicable

**File Storage:**
- Local filesystem only (artifact trees under `00-supporting-files/data/audio-extraction-review/`)

**Caching:**
- Local artifact reuse/checkpoint behavior via prior files (`allow_transcript_checkpoint_reuse`) in `00-supporting-files/data/audio-extraction-review/runs/run-20260222T030354Z-206b1285.json`

## Authentication & Identity

**Auth Provider:**
- Custom/local token usage only (no OAuth/IdP integration detected)
  - Implementation: pipeline config fields for local API key and optional Hugging Face token dependency in run/log metadata (`00-supporting-files/data/audio-extraction-review/runs/run-20260222T030354Z-206b1285.json`, `00-supporting-files/data/audio-extraction-review/logs/transcription-20260222T023330Z-f9bdbf0d.jsonl`)

## Monitoring & Observability

**Error Tracking:**
- None (no Sentry/Bugsnag/etc. detected)

**Logs:**
- Structured JSONL stage logs per run in `00-supporting-files/data/audio-extraction-review/logs/*.jsonl`

## CI/CD & Deployment

**Hosting:**
- Not detected (local execution paths and localhost service endpoints only)

**CI Pipeline:**
- None detected (`.github/workflows/` not present)

## Environment Configuration

**Required env vars:**
- Hugging Face access token for WhisperX diarization (exact variable name not present in tracked source; missing token causes fallback) evidenced by `missing_huggingface_token` in `00-supporting-files/data/audio-extraction-review/logs/transcription-20260222T023330Z-f9bdbf0d.jsonl`
- Local OpenAI-compatible API key value is expected by segmentation config (`api_key` key) in `00-supporting-files/data/audio-extraction-review/runs/run-20260222T030354Z-206b1285.json`

**Secrets location:**
- `.env` file present at `00-supporting-files/data/.env` (contents intentionally not read)
- sample env template present at `00-supporting-files/data/sample.env.file` (contents intentionally not read)

## Webhooks & Callbacks

**Incoming:**
- None detected

**Outgoing:**
- None detected

---

*Integration audit: 2026-02-26*
