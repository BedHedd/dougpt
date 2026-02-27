# Feature Research

**Domain:** Local video/chat extraction and conversational model training pipeline
**Researched:** 2026-02-26
**Confidence:** MEDIUM

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Deterministic video + chat ingestion | Local ML workflows require repeatable raw data pulls and reruns. | MEDIUM | Support scripted ingestion for VOD/video files and chat logs; persist source IDs and checksums. |
| Timestamp-accurate speech transcription | Chat-response pairing quality depends on timing, not just text. | HIGH | Use ASR with word-level timestamps and VAD/alignment; segment-level timestamps alone are usually too coarse. |
| Canonical training schema for conversations | SFT tools expect consistent conversational structure. | MEDIUM | Normalize to `messages` or prompt/completion format with strict role rules and required metadata columns. |
| Alignment pipeline (speech window -> candidate chat responses) | Core product value is high-quality prompt/response pairs. | HIGH | Include configurable temporal windows, dedupe, spam filtering, and confidence scoring per pair. |
| Dataset QA + filtering pass | Raw stream data is noisy (emotes, spam, overlap, ASR misses). | HIGH | Add hard filters (empty/garbled text, low-confidence timestamps) and review queues for borderline pairs. |
| Reproducible training runs with checkpoints | Fine-tuning must be restartable and comparable across experiments. | MEDIUM | Track config, seed, base model, data version, and output artifact paths for each run. |
| Baseline evaluation before/after tuning | Without eval, quality improvements are anecdotal. | MEDIUM | Include automatic regression checks on held-out conversation slices and curated persona prompts. |
| Local inference + sample generation harness | Usability requires quick qualitative checks after each run. | LOW | Single command to load latest adapter/model and run scripted prompt suites. |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Alignment confidence model (not only fixed rules) | Improves pair quality by learning which speech-chat links are credible. | HIGH | Start with heuristic score, then train/rank with weak labels from accepted/rejected pairs. |
| Human-in-the-loop correction UI for hard examples | Concentrates effort on the small fraction of ambiguous high-impact data. | MEDIUM | Lightweight review surface for timestamp shifts, bad transcript spans, and wrong response mapping. |
| Persona/style balancing controls | Prevents overfitting to spammy or one-note chat behavior. | MEDIUM | Add stratified sampling by stream context, message length, toxicity/emote density, and novelty. |
| Data lineage traceability per training sample | Makes debugging model behavior fast and concrete. | MEDIUM | Every training row links back to source video ID, chat message IDs, transcript span, and transform history. |
| Adapter-centric training modes (LoRA/QLoRA presets) | Delivers high-quality local iteration on limited hardware. | MEDIUM | Provide known-good presets for VRAM tiers and explicit train-on-assistant-only options. |
| Evaluation bundle with both objective and style metrics | Captures whether model is both correct enough and "Doug-style" enough. | HIGH | Pair benchmark-style eval with custom persona rubric (timing mimicry, humor cadence, chat-like brevity). |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Real-time live Twitch integration in v1 | Feels more exciting than offline processing. | Adds API, reliability, and moderation complexity before core dataset quality is proven. | Stay offline-first on existing VODs until alignment quality and model gains are validated. |
| Fully automatic dataset creation with zero review | Promises speed and no manual effort. | Silent alignment/transcription errors poison training data and are hard to detect later. | Add confidence thresholds plus targeted human review for ambiguous samples. |
| Training from scratch foundation models locally | Sounds like maximum control. | Unrealistic compute/data burden; slows core objective (persona adaptation). | Use SFT/adapter tuning on an existing open base model. |
| One-click "do everything" monolithic pipeline | Appears user-friendly initially. | Hard to debug failures, impossible to iterate individual stages, brittle at scale. | Keep composable stages (ingest, transcribe, align, filter, train, eval) with artifacts between each. |
| Aggressive long-context packing before quality is solved | Looks efficient for throughput metrics. | Can hide bad sample boundaries and worsen conversational signal quality. | Prioritize clean sample construction first; add packing after baseline quality is stable. |

## Feature Dependencies

```
[Deterministic video + chat ingestion]
    └──requires──> [Timestamp-accurate speech transcription]
                          └──requires──> [Canonical training schema]
                                                └──requires──> [Alignment pipeline]
                                                                      └──requires──> [Dataset QA + filtering]
                                                                                            └──requires──> [Reproducible training runs]
                                                                                                                  └──requires──> [Baseline evaluation]

[Data lineage traceability] ──enhances──> [Dataset QA + filtering]
[Human-in-the-loop correction UI] ──enhances──> [Alignment pipeline]
[Persona/style balancing controls] ──enhances──> [Baseline evaluation]

[Real-time live Twitch integration in v1] ──conflicts──> [Offline-first quality iteration]
```

### Dependency Notes

- **Alignment pipeline requires timestamp-accurate transcription:** alignment quality collapses if transcript timing is coarse or unstable.
- **QA/filtering requires canonical schema:** quality rules and analytics are only reliable when fields are normalized and typed.
- **Reproducible training runs require versioned data artifacts:** otherwise model deltas cannot be attributed to data vs hyperparameter changes.
- **Baseline evaluation requires stable holdout slices:** if holdouts drift every run, trend comparison is meaningless.
- **Real-time integration conflicts with offline-first iteration:** it consumes effort on infra while the core uncertainty is data-pair quality.

## MVP Definition

### Launch With (v1)

Minimum viable product - what's needed to validate the concept.

- [ ] Deterministic video + chat ingestion - guarantees reproducible raw inputs.
- [ ] Timestamp-accurate transcription + alignment + QA - creates trustworthy prompt/response pairs.
- [ ] Reproducible adapter fine-tuning + baseline evaluation + local inference harness - proves end-to-end learning value.

### Add After Validation (v1.x)

Features to add once core is working.

- [ ] Human-in-the-loop correction UI - add when automated confidence filtering identifies recurring ambiguous cases.
- [ ] Persona/style balancing controls - add when initial model is coherent but stylistically inconsistent.

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] Alignment confidence model (learned ranking) - add when enough accepted/rejected data exists to train it reliably.
- [ ] Live ingestion extensions - add only after offline pipeline quality and throughput are stable.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Deterministic ingestion | HIGH | MEDIUM | P1 |
| Timestamp-accurate transcription | HIGH | HIGH | P1 |
| Alignment + QA filtering | HIGH | HIGH | P1 |
| Reproducible training + eval | HIGH | MEDIUM | P1 |
| Local inference harness | HIGH | LOW | P1 |
| Human-in-the-loop correction UI | MEDIUM | MEDIUM | P2 |
| Persona/style balancing controls | MEDIUM | MEDIUM | P2 |
| Learned alignment confidence model | HIGH | HIGH | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | Competitor A | Competitor B | Our Approach |
|---------|--------------|--------------|--------------|
| Chat extraction/export | TwitchDownloader supports chat download in JSON/HTML/text and CLI automation. | Generic VOD download tools often lack structured chat export. | Standardize on machine-readable chat export with explicit metadata + checksums. |
| Timestamped transcription | WhisperX emphasizes word-level timestamps, VAD, and optional diarization. | Baseline Whisper workflows often rely on coarser segment timestamps. | Require word/segment alignment quality gates before pair generation. |
| Dataset structure | Hugging Face Datasets defines explicit feature schemas and audio columns. | Ad-hoc CSV/JSONL formats vary widely by project. | Enforce strict schema + validation for role, timestamps, and provenance fields. |
| Training format compatibility | TRL SFTTrainer supports conversational `messages` and prompt/completion. | Custom training loops frequently re-implement formatting incorrectly. | Export directly to SFT-friendly formats and preserve chat template compatibility. |
| Experiment reproducibility | DVC provides data/model versioning and reproducible pipeline patterns. | Script-only workflows are often non-reproducible over time. | Version datasets/models/configs and bind each model artifact to exact data revision. |

## Sources

- https://github.com/lay295/TwitchDownloader (official README; chat download/export and CLI automation) [MEDIUM]
- https://github.com/m-bain/whisperX (official README; word-level timestamps, VAD, diarization, limitations) [MEDIUM]
- https://huggingface.co/docs/datasets/en/about_dataset_features (official docs; dataset schema/features typing) [HIGH]
- https://huggingface.co/docs/trl/en/sft_trainer (official docs; conversational formats and SFT expectations) [HIGH]
- https://huggingface.co/docs/transformers/en/chat_templating (official docs; chat template correctness requirements) [HIGH]
- https://huggingface.co/docs/peft/en/developer_guides/lora (official docs; adapter/LoRA training patterns) [HIGH]
- https://dvc.org/doc/start (official docs; data/model versioning and reproducible ML pipeline workflow) [HIGH]
- https://huggingface.co/docs/hub/en/datasets-cards (official docs; dataset documentation and metadata expectations) [HIGH]

---
*Feature research for: local dataset + model pipeline usability and quality*
*Researched: 2026-02-26*
