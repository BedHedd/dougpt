# Feature Research

**Domain:** Local LLM fine-tuning to mimic DougDoug Twitch chat
**Researched:** 2026-02-21
**Confidence:** MEDIUM

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| VOD + chat ingestion with timestamps | Core data source; without aligned pairs the model cannot learn chat timing | MEDIUM | Import Twitch VODs and exported chat logs; preserve message metadata (username, emotes, timestamps). |
| ASR transcription + audio-chat alignment | Chat depends on what DougDoug said; need transcript aligned to message times | HIGH | Use ASR (e.g., Whisper) with word/phrase timestamps; align chat window to nearest preceding audio span. |
| Dataset cleaning and pairing pipeline | Noisy chat (spam/duplicates); must build clean (context → chat) pairs | MEDIUM | Filter bots, rate-limit spam bursts, drop low-signal messages, keep emotes/text, standardize encoding. |
| Parameter-efficient fine-tuning (PEFT/LoRA) | Local GPUs require efficient adaptation; baseline fine-tune is the core deliverable | MEDIUM | Support resume/checkpointing; configurable hyperparams; handle tokenizer choices (BPE vs sentencepiece). |
| Evaluation harness on held-out clips | Need proof model matches chat tone and pacing; guards against regressions | MEDIUM | Metrics: response style similarity, repetition rate, toxicity/off-topic flags; compare to baseline (prompted base model). |
| Guardrails for toxicity/NSFW/spam | Twitch chat can be edgy; need lightweight filters for safe offline use | MEDIUM | Rule-based + classifier; configurable thresholds; log filtered outputs for review. |
| Local inference interface (CLI/REST) | Users must run locally and feed new audio/transcript to get chat-like replies | LOW | Accept transcript/context text; return top-k candidates; simple REST + CLI script. |
| Reproducible data/version tracking | Experiments need traceability; avoid data drift | LOW | Track dataset versions, model checkpoints, and config hashes; small manifest per run. |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| DougDoug meme/lexicon adaptation | Captures recurring bits ("EAT", "walmart", emote culture) to feel authentic | HIGH | Build lexicon and style prompts; augment training with mined meme snippets; possible bias tuning via reward model. |
| Time-synced playback simulator | Lets users preview model outputs over video like real chat | MEDIUM | Render chat overlay against VOD timeline; compare model vs real chat for QA. |
| Controllable sliders (toxicity/spam/enthusiasm) | Adjusts how chaotic the chat feels per session | MEDIUM | Sampling controls + logits biasing on spammy tokens; expose presets (wholesome/chaos). |
| Data augmentation for style robustness | Reduces overfitting to exact phrasing; improves generalization | MEDIUM | Paraphrase transcripts, inject emote variants, negative samples for off-topic suppression. |
| Scene/speaker change-aware context selection | Keeps context window relevant when topics shift quickly | HIGH | Use VAD + scene change detection; reset/trim context automatically. |
| Small-model distillation for low VRAM | Expands local usability to smaller GPUs | HIGH | Distill fine-tuned model into 7B-ish target; requires eval parity tracking. |
| On-device safety/banword pack tuned to DougDoug | Prevents bannable/DMCA phrases while retaining humor | LOW | Maintain configurable denylist/allowlist; offline classifier. |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Live Twitch integration/production bot | Feels like “real chat" | Scope creep, moderation liability, TOS risk | Keep offline/local playback; optionally export logs for manual use. |
| Cloud-dependent fine-tuning/inference | Convenience | Violates local-first, increases cost and data risk | Local GPU with PEFT; optional CPU/quantized fallback. |
| Heavy-handed censorship of humor | Avoid offense | Strips DougDoug chat identity; yields bland outputs | Balanced guardrails with configurable thresholds and review logs. |
| Redistribution of VOD media | Share outputs/media | Copyright exposure | Store manifests only; require user-supplied media paths. |

## Feature Dependencies

```
VOD + chat ingestion
    └──requires──> ASR transcription + audio-chat alignment
                        └──requires──> Dataset cleaning and pairing
                                            └──requires──> Reproducible data/version tracking
                                                    └──requires──> Parameter-efficient fine-tuning
                                                            └──requires──> Evaluation harness
                                                                    └──enhances──> Guardrails for toxicity/NSFW/spam
                                                                                └──enhances──> Local inference interface (CLI/REST)

Scene/speaker change-aware context selection ──enhances──> ASR alignment & dataset pairing
DougDoug meme/lexicon adaptation ──enhances──> Parameter-efficient fine-tuning
Controllable sliders ──enhances──> Local inference interface
Time-synced playback simulator ──requires──> Local inference interface
Data augmentation ──enhances──> Fine-tuning quality; requires cleaned dataset
Small-model distillation ──requires──> Fine-tuned teacher + evaluation harness
On-device banword pack ──enhances──> Guardrails
```

### Dependency Notes

- **Ingestion requires ASR alignment:** chat timing only makes sense when mapped to what DougDoug said nearby.
- **Cleaning precedes fine-tuning:** noisy chat produces degenerate outputs; must filter before training.
- **Evaluation gates releases:** fine-tune builds should not ship without passing style/toxicity checks.
- **Simulator depends on inference:** playback needs generated messages synced to timelines.
- **Distillation depends on a strong teacher:** need validated larger model to distill into smaller targets.

## MVP Definition

### Launch With (v1)

Minimum viable product — what's needed to validate the concept.

- [ ] VOD + chat ingestion with timestamps — foundational data
- [ ] ASR transcription + audio-chat alignment — supplies context
- [ ] Dataset cleaning and pairing pipeline — ensures usable pairs
- [ ] Parameter-efficient fine-tuning — produce a DougDoug-style model
- [ ] Evaluation harness on held-out clips — verify tone/quality and safety
- [ ] Local inference interface (CLI/REST) — deliver chat-like replies offline

### Add After Validation (v1.x)

Features to add once core is working.

- [ ] Guardrails for toxicity/NSFW/spam — tighten safety after baseline proves style
- [ ] DougDoug meme/lexicon adaptation — sharpen authenticity once base works
- [ ] Time-synced playback simulator — improve QA and demos
- [ ] Controllable sliders (toxicity/spam/enthusiasm) — allow user-tunable chaos

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] Scene/speaker change-aware context selection — complexity; add when scaling datasets
- [ ] Data augmentation for style robustness — add once baseline overfits
- [ ] Small-model distillation for low VRAM — after teacher is solid
- [ ] On-device banword pack tuned to DougDoug — when deploying beyond internal use

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| VOD + chat ingestion | HIGH | MEDIUM | P1 |
| ASR transcription + alignment | HIGH | HIGH | P1 |
| Dataset cleaning and pairing | HIGH | MEDIUM | P1 |
| Parameter-efficient fine-tuning | HIGH | MEDIUM | P1 |
| Evaluation harness | HIGH | MEDIUM | P1 |
| Local inference interface | HIGH | LOW | P1 |
| Guardrails (toxicity/spam) | HIGH | MEDIUM | P2 |
| DougDoug meme/lexicon adaptation | MEDIUM | HIGH | P2 |
| Time-synced playback simulator | MEDIUM | MEDIUM | P2 |
| Controllable sliders | MEDIUM | MEDIUM | P2 |
| Scene/speaker-aware context | MEDIUM | HIGH | P3 |
| Data augmentation | MEDIUM | MEDIUM | P3 |
| Small-model distillation | HIGH | HIGH | P3 |
| On-device banword pack | MEDIUM | LOW | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | Competitor A | Competitor B | Our Approach |
|---------|--------------|--------------|--------------|
| Persona prompting only (no fine-tune) | Base LLM with manual prompt; drifts off-tone | Same; relies on hosted API | Fine-tuned local model with style lexicon to stay on-brand. |
| Generic fine-tune scripts (e.g., Alpaca variants) | No timing alignment; text-only datasets | Limited guardrails; no playback tools | Alignment-focused pipeline with DougDoug-specific guardrails and simulator. |
| Hosted inference | Cloud API pay-per-call | Cloud API | Offline local inference with PEFT + optional distillation for low VRAM. |

## Sources

- Domain patterns from open-source LLM fine-tuning pipelines (2024-2026), Twitch chat dataset practices, and local-inference guardrail guides. (Confidence: MEDIUM)

---
*Feature research for: DougPT — local LLM mimicking DougDoug Twitch chat*
*Researched: 2026-02-21*
