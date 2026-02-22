# Project Research Summary

**Project:** DougPT
**Domain:** Local Twitch chat-style LLM tuned on DougDoug streams
**Researched:** 2026-02-21
**Confidence:** MEDIUM

## Executive Summary

Local-first pipeline to mimic DougDoug’s Twitch chat: ingest VODs + chat logs, align transcripts to messages, and fine-tune a chat-capable LLM with PEFT so it runs on consumer GPUs. Experts standardize manifests across ingestion, ASR, alignment, and dataset assembly to keep iterations reproducible and cheap.

Recommended approach: manifest-driven stages (download → demux/VAD → Whisper transcription → drift-corrected alignment → HF dataset) feeding a LoRA/QLoRA fine-tune on a chat-friendly base model, served via vLLM for fast, streaming inference. Guardrails (toxicity/spam filters, rate controls) and evaluation on held-out streams are baked in to prove tone and safety before demos.

Key risks: timestamp drift between VOD and chat, noisy transcripts, spam-heavy datasets, and train/infer prompt mismatches. Mitigate with per-VOD offset estimation and playback QA, strong Whisper + VAD with audits, spam/toxicity filtering and balanced sampling, strict manifest versioning, and enforcing the same context/prompt format across training and inference.

## Key Findings

### Recommended Stack

Torch 2.10 + Transformers 4.57 + PEFT/TRl provide the fine-tuning core; vLLM 0.15.1 serves streaming inference with KV-efficient attention. Accelerate/datasets handle device placement and data streaming; flash-attn speeds attention on SM80+ GPUs; faster-whisper supplies local ASR; uv/pre-commit/ruff keep environments reproducible.

**Core technologies:**
- torch 2.10.0: tensor/autograd backbone — broad CUDA support and ecosystem stability.
- transformers 4.57.6: model/tokenizer pipeline — compatible with vLLM (<5), supports recent chat bases.
- peft 0.18.1: LoRA/QLoRA adapters — fits 8–13B models on consumer GPUs.
- trl 0.28.0: chat-focused trainers — simplifies SFT/DPO shaping for Twitch tone.
- vllm 0.15.1: streaming inference server — fast KV cache/paged attention for chat pacing.

### Expected Features

Foundational pipeline features: VOD + chat ingestion with timestamps, ASR transcription + alignment, dataset cleaning/pairing, PEFT fine-tuning, held-out evaluation harness, and a local CLI/REST inference interface. Safety/UX layers include guardrails for toxicity/spam and reproducible manifests.

**Must have (table stakes):**
- VOD + chat ingestion with timestamps — core data source.
- ASR transcription + audio-chat alignment — provides context mapping.
- Dataset cleaning and pairing — removes spam/noise before training.
- Parameter-efficient fine-tuning — produces DougDoug-style model on local GPU.
- Evaluation harness on held-out clips — gates releases and regressions.
- Local inference interface (CLI/REST) — delivers offline chat-like replies.

**Should have (competitive):**
- DougDoug meme/lexicon adaptation — captures recurring bits.
- Time-synced playback simulator — QA against real chat timelines.
- Controllable sliders (toxicity/spam/enthusiasm) — tune chaos per session.
- Guardrails for toxicity/NSFW/spam — safe defaults post-MVP.

**Defer (v2+):**
- Scene/speaker-aware context selection — complexity; add when scaling.
- Data augmentation for style robustness — once overfitting appears.
- Small-model distillation — after strong teacher exists.
- On-device banword pack — when distributing broadly.

### Architecture Approach

Layered, manifest-driven pipeline: ingest (VOD/chat/metadata) → media processing (demux/VAD/Whisper, optional diarization) → alignment (offset search + windowing) → dataset assembly/filters → training/eval (tokenizer, PEFT loop, held-out metrics) → inference (context builder, generator, guardrails), with storage/registry for artifacts and configs.

**Major components:**
1. Ingest (vod_downloader, chat_parser) — fetch and normalize VODs/chat with manifests.
2. Audio/ASR + alignment (demux, vad, asr, offset_finder, window_builder) — produce timestamped transcripts and drift-corrected pairs.
3. Dataset/training/inference (build, filters, lora_trainer, eval, generate, guardrails) — assemble HF datasets, fine-tune adapters, and serve guarded chat-style outputs.

### Critical Pitfalls

1. **Drifted VOD↔chat timestamps** — derive per-VOD offsets with anchors/cross-correlation; record in manifests; QA via playback.
2. **Noisy/incorrect transcripts** — use strong Whisper + VAD, domain lexicon, confidence thresholds, and manual audits.
3. **Spam/emote-dominated dataset** — filter bots/mod commands, cap repeats, balance samples, apply toxicity filters.
4. **Train/inference context mismatch** — fix one prompt/context window; enforce parity and shadow inference during training.
5. **Missing provenance/versioning** — version manifests, checksums, ASR model info, and immutable splits.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Data Foundation & Alignment
**Rationale:** Timestamp drift and provenance are the biggest failure modes; fixing early prevents wasted fine-tunes.
**Delivers:** VOD/chat manifests, demuxed audio, per-VOD offset estimation, alignment QA playback hooks, versioned storage layout.
**Addresses:** VOD+chat ingestion, reproducible tracking.
**Avoids:** Drifted timestamps; missing provenance.

### Phase 2: Transcription, Cleaning, and Pairing
**Rationale:** High-quality transcripts and filtered chat pairs gate model quality; dependent on Phase 1 offsets.
**Delivers:** Whisper transcripts with confidence, filtered/aligned HF datasets, spam/toxicity reports.
**Addresses:** ASR transcription + alignment, dataset cleaning/pairing, guardrail-ready filters.
**Avoids:** Noisy transcripts; spam/emote dominance.

### Phase 3: Fine-Tuning & Evaluation
**Rationale:** Once data is reliable, adapt the model with PEFT and prove style/safety on held-out streams.
**Delivers:** PEFT adapters/checkpoints, tokenizer/prompt spec, eval harness with stream-level holdouts, shadow-inference parity checks.
**Addresses:** Parameter-efficient fine-tuning, evaluation harness, train/infer parity.
**Avoids:** Overfitting slices; train/infer mismatch.

### Phase 4: Inference UX & Differentiators
**Rationale:** Build user-facing pieces after core model is validated; add authenticity and QA tooling.
**Delivers:** Local CLI/REST server with guardrails, playback simulator, controllable style knobs, meme/lexicon augmentation; optional distillation prep.
**Addresses:** Local inference interface, guardrails, simulator, controllable sliders, meme adaptation.
**Avoids:** UX pitfalls (no review UI, no knobs); balances safety vs authenticity.

### Phase Ordering Rationale

- Alignment and manifests come first to stop data drift from contaminating all downstream steps.
- Transcription/cleaning depends on accurate offsets; fine-tuning depends on clean, versioned datasets; UX layers depend on validated models.
- Ordering directly targets top pitfalls (drift, noisy ASR, spam, provenance, parity) before model/UX work.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2:** Whisper config/lexicon choices and alignment heuristics may need benchmarks on DougDoug clips.
- **Phase 3:** Base-model selection and PEFT hyperparams vs VRAM budgets; eval metrics for style similarity.
- **Phase 4:** Distillation target size and style-preservation techniques if low-VRAM support is required.

Phases with standard patterns (skip research-phase):
- **Phase 1:** Manifest-driven ingestion/alignment patterns are established; needs execution, not novel research.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | PyPI versions verified; fast-moving ML stack may shift. |
| Features | MEDIUM | Based on common LLM fine-tuning pipelines and Twitch chat needs. |
| Architecture | MEDIUM | Standard manifest-driven LLM data pipeline; needs validation on DougDoug specifics. |
| Pitfalls | MEDIUM | Derived from prior VOD/ASR/PEFT experience; project-specific proof pending. |

**Overall confidence:** MEDIUM

### Gaps to Address

- Base model choice (size and license) for best DougDoug fit — benchmark a few chat-friendly models with small DougDoug slices.
- Style evaluation metrics beyond BLEU/ROUGE — define chat-style similarity heuristics and human review protocol.
- Data licensing boundaries for VOD/chat use — confirm storage/sharing policy to avoid redistribution issues.
- Alignment QA UX requirements — decide minimal playback/review tooling scope.

## Sources

### Primary (HIGH confidence)
- PyPI metadata for torch, transformers, peft, trl, vllm, datasets, accelerate, faster-whisper, flash-attn, uv, pre-commit, ruff — version verification.
- Whisper README — timestamped ASR guidance; sliding window practice.
- Hugging Face PEFT docs — parameter-efficient fine-tuning patterns.

### Secondary (MEDIUM confidence)
- Open-source LLM fine-tuning and Twitch chat pipeline patterns (2024–2026) — feature expectations and guardrail practices.
- Personal/industry experience with VOD alignment, ASR pipelines, and PEFT chat models — pitfalls and mitigations.

### Tertiary (LOW confidence)
- Community discussions on Twitch chat exports and Whisper alignment specifics — need DougDoug-specific validation.

---
*Research completed: 2026-02-21*
*Ready for roadmap: yes*
