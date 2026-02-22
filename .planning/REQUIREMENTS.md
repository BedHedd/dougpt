# Requirements: DougPT

**Defined:** 2026-02-21
**Core Value:** A locally fine-tuned model that reliably produces authentic DougDoug Twitch chat-style responses from recent audio context.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Ingestion & Manifests

- [ ] **ING-01**: Fetch DougDoug VODs and Twitch chat logs with timestamps into versioned manifests.
- [ ] **ING-02**: Demux audio from VODs and store checksums/metadata for reproducibility.

### Transcription & Alignment

- [ ] **ALGN-01**: Transcribe VOD audio locally (Whisper or equivalent) with word-level timestamps.
- [ ] **ALGN-02**: Estimate per-VOD chat/VOD time offsets and align chat messages to transcript windows with QA hooks.

### Dataset & Cleaning

- [ ] **DATA-01**: Build paired training dataset (audio/transcript context → chat reply) with manifests and immutable splits.
- [ ] **DATA-02**: Filter spam/bots/mod commands/emote-only noise; cap repeats and flag toxicity.
- [ ] **DATA-03**: Include provenance (VOD id, offsets, ASR model/config) for every example.

### Fine-Tuning

- [ ] **TRAIN-01**: Tokenize/prepare data with fixed prompt/context format shared with inference.
- [ ] **TRAIN-02**: Fine-tune a local chat-capable base model using PEFT/QLoRA within single-GPU budget.

### Evaluation

- [ ] **EVAL-01**: Hold out streams/clips and report style/safety metrics plus human spot-checks.
- [ ] **EVAL-02**: Detect regressions vs prior checkpoints and fail gate on safety/style drops.

### Inference & Guardrails

- [ ] **INF-01**: Provide local CLI/REST interface that returns chat-style responses from recent audio/transcript context.
- [ ] **INF-02**: Enforce the same prompt/context spec as training; shadow-evaluate outputs for parity.
- [ ] **SAFE-01**: Apply guardrails (toxicity/spam filters, rate limits) before returning responses.

## v2 Requirements

### Differentiators & UX

- **DIFF-01**: Time-synced playback simulator to compare model outputs against real chat.
- **DIFF-02**: Style controls (e.g., toxicity/chaos/enthusiasm sliders) to tune chat energy.
- **DIFF-03**: DougDoug meme/lexicon augmentation to boost authenticity.
- **DIFF-04**: Scene/speaker-aware context selection for harder clips.
- **DIFF-05**: Data augmentation for robustness (e.g., synthetic paraphrases or timing jitter).
- **DIFF-06**: Distill to a smaller model for low-VRAM inference once quality is validated.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Live Twitch bot deployment | Focus on offline/local usage first; avoid TOS/automation risk. |
| Cloud-hosted proprietary LLM APIs | Local-first for cost/control and reproducibility. |
| Redistribution of VOD media | Licensing risk; use data for internal training only. |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| ING-01 | Phase  | Pending |
| ING-02 | Phase  | Pending |
| ALGN-01 | Phase  | Pending |
| ALGN-02 | Phase  | Pending |
| DATA-01 | Phase  | Pending |
| DATA-02 | Phase  | Pending |
| DATA-03 | Phase  | Pending |
| TRAIN-01 | Phase  | Pending |
| TRAIN-02 | Phase  | Pending |
| EVAL-01 | Phase  | Pending |
| EVAL-02 | Phase  | Pending |
| INF-01 | Phase  | Pending |
| INF-02 | Phase  | Pending |
| SAFE-01 | Phase  | Pending |
| DIFF-01 | Phase  | Pending |
| DIFF-02 | Phase  | Pending |
| DIFF-03 | Phase  | Pending |
| DIFF-04 | Phase  | Pending |
| DIFF-05 | Phase  | Pending |
| DIFF-06 | Phase  | Pending |

**Coverage:**
- v1 requirements: 14 total
- Mapped to phases: 0
- Unmapped: 14 ⚠️

---
*Requirements defined: 2026-02-21*
*Last updated: 2026-02-21 after initial definition*
