# Roadmap: DougPT

## Overview

Pipeline to ingest DougDoug VODs and chat logs, align transcripts to messages, assemble a filtered dataset with provenance, fine-tune a local chat-style model, and serve guarded chat-like responses via local interfaces.

## Phases

- [ ] **Phase 1: Data Ingestion & Manifests** - VOD/chat assets ingested with versioned manifests and demuxed audio.
- [ ] **Phase 2: Transcription & Alignment** - Local transcripts produced and chat aligned with QA hooks.
- [ ] **Phase 3: Dataset & Cleaning** - Filtered paired datasets with provenance and immutable splits.
- [ ] **Phase 4: Fine-Tuning & Evaluation** - PEFT fine-tune with shared prompt spec and regression-gated evals.
- [ ] **Phase 5: Inference & Guardrails** - Local CLI/REST with prompt parity, shadow checks, and safety filters.

## Phase Details

### Phase 1: Data Ingestion & Manifests
**Goal**: VODs and chat logs are fetched, demuxed, and recorded in versioned manifests with reproducible metadata.
**Depends on**: Nothing (first phase)
**Requirements**: ING-01, ING-02
**Success Criteria** (what must be TRUE):
  1. User can fetch a VOD and matching chat log by ID and see both recorded in a versioned manifest with timestamps.
  2. User can retrieve demuxed audio for any ingested VOD with checksums matching manifest entries.
  3. User can view per-asset metadata (duration, source URLs, storage paths, checksums) in manifests for reproducibility.
  4. Re-running ingestion preserves deterministic manifests without duplicating or losing entries.
**Plans**: 2 plans

Plans:
- [ ] 01-data-ingestion-manifests-01-PLAN.md — Build ingestion CLI for VOD+chat manifests
- [ ] 01-data-ingestion-manifests-02-PLAN.md — Integrate audio demux and manifest validation

### Phase 2: Transcription & Alignment
**Goal**: VOD audio is transcribed locally and chat messages are aligned to transcript windows with verified offsets.
**Depends on**: Phase 1
**Requirements**: ALGN-01, ALGN-02
**Success Criteria** (what must be TRUE):
  1. User can run local transcription on a VOD and obtain word-level timestamped text.
  2. User can see per-VOD chat↔transcript offset estimates and aligned chat messages to transcript windows.
  3. User can play back sample segments or QA hooks to verify chat/message alignment accuracy.
**Plans**: 2 plans

Plans:
- [ ] 02-01-PLAN.md — Build WhisperX transcription pipeline with word-level timestamps
- [ ] 02-02-PLAN.md — Build chat-transcript alignment with auto offset detection

### Phase 3: Dataset & Cleaning
**Goal**: Build a filtered, provenance-rich paired dataset with immutable splits ready for training.
**Depends on**: Phase 2
**Requirements**: DATA-01, DATA-02, DATA-03
**Success Criteria** (what must be TRUE):
  1. User can export train/validation/test splits of audio/transcript context → chat reply pairs with a fixed schema.
  2. Spam/bots/mod commands/emote-only noise are removed or flagged; repeats are capped with reports available.
  3. Each dataset example includes provenance (VOD id, offsets, ASR model/config, manifest version) accessible for audits.
  4. Dataset manifests record immutable split membership so reruns reproduce identical splits.
**Plans**: TBD

Plans:
- [ ] TBD

### Phase 4: Fine-Tuning & Evaluation
**Goal**: Fine-tune a local chat-capable model with PEFT and gate releases on held-out style/safety evaluation.
**Depends on**: Phase 3
**Requirements**: TRAIN-01, TRAIN-02, EVAL-01, EVAL-02
**Success Criteria** (what must be TRUE):
  1. User can tokenize/format data with the shared prompt/context spec identical to inference.
  2. User can run PEFT/QLoRA fine-tuning within single-GPU budget and produce adapters/checkpoints.
  3. User can evaluate on held-out streams/clips and see style/safety metrics plus human spot-check results.
  4. Regression detection compares current runs to prior checkpoints and blocks promotion on style/safety drops.
**Plans**: TBD

Plans:
- [ ] TBD

### Phase 5: Inference & Guardrails
**Goal**: Serve local chat-style responses with prompt parity and safety controls.
**Depends on**: Phase 4
**Requirements**: INF-01, INF-02, SAFE-01
**Success Criteria** (what must be TRUE):
  1. User can query a local CLI/REST interface with recent audio/transcript context and receive chat-style responses.
  2. Responses use the same prompt/context format as training, and shadow evaluation logs parity during inference.
  3. Guardrails apply toxicity/spam filters and rate limits before responses are returned.
  4. User can inspect logs of responses and guardrail actions for QA.
**Plans**: TBD

Plans:
- [ ] TBD

## Progress

**Execution Order:** Phases execute in numeric order.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Data Ingestion & Manifests | 0/2 | Not started | - |
| 2. Transcription & Alignment | 1/2 | In Progress|  |
| 3. Dataset & Cleaning | 0/TBD | Not started | - |
| 4. Fine-Tuning & Evaluation | 0/TBD | Not started | - |
| 5. Inference & Guardrails | 0/TBD | Not started | - |
