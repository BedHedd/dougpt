# Pitfalls Research

**Domain:** Twitch VOD→chat alignment and local LLM fine-tuning (DougDoug)
**Researched:** 2026-02-21
**Confidence:** MEDIUM

## Critical Pitfalls

### Pitfall 1: Drifted VOD↔chat timestamps

**What goes wrong:** Chat messages lead/lag the audio; paired samples point to the wrong context, training the model to respond to unrelated moments.

**Why it happens:** VOD downloads start late, chat exports keep absolute timestamps, frame drops/ads create gaps, and a single global offset is assumed without per-VOD calibration.

**How to avoid:** Normalize all times to a common epoch; derive per-VOD offsets using anchor events (e.g., “stream starting soon”, loud countdowns); run cross-correlation between message density and audio energy peaks; store the final offset and drift curve with the dataset manifest.

**Warning signs:** Consistent +/− delay visible when replaying audio with chat; cross-correlation peak far from zero; high rate of “off-topic” responses in eval despite good loss.

**Phase to address:** Data ingestion & alignment (Phase 1).

---

### Pitfall 2: Noisy/incorrect transcripts for ASR

**What goes wrong:** Mis-heard words, overlapping speech, and music produce garbled context; fine-tuning learns artifacts instead of DougDoug’s phrasing.

**Why it happens:** Using a small/fast ASR model, skipping domain vocabulary, no VAD/diarization, and not spot-checking WER on representative clips.

**How to avoid:** Use a strong Whisper-family model with VAD; add DougDoug-specific lexicon; segment audio around chat windows; reject clips with high WER or low ASR confidence; manually audit random samples each VOD.

**Warning signs:** Transcripts show repeated “music”, “[inaudible]”, or wrong meme phrases; large mismatch between ASR confidence and human perception; training loss low but generated replies ignore audio details.

**Phase to address:** Transcription & dataset curation (Phase 2).

---

### Pitfall 3: Dataset dominated by spam/emote noise

**What goes wrong:** The model parrots emote spam, copypasta, or moderation commands instead of varied chat tone.

**Why it happens:** Ingesting raw chat without filtering bots, timeouts, mass emotes, or repeated copypasta; no per-user rate limits; imbalance across streams.

**How to avoid:** Filter moderation commands and bot usernames; cap identical message repeats per window; down-weight pure emote lines; enforce per-stream sampling balance; include toxicity/profanity screening aligned to guardrails.

**Warning signs:** Token frequency spikes for single emotes; eval generations collapse to emote-only replies; entropy of responses drops over training.

**Phase to address:** Dataset cleaning & balance (Phase 2).

---

### Pitfall 4: Train/inference context mismatch

**What goes wrong:** The fine-tuned model expects longer or richer context than provided at inference, producing off-topic or generic replies.

**Why it happens:** Training pairs include multi-minute transcripts, but the inference path supplies only short windows or audio embeddings; prompt formats differ between training and runtime.

**How to avoid:** Fix a standard context window (e.g., last N seconds transcript + recent chat) and use it identically in training and inference; freeze a single prompt template; run shadow inference during training to confirm parity.

**Warning signs:** Offline eval good when using training prompt, but live inference degrades; models hallucinate missing context; large prompt-engineering changes needed after training.

**Phase to address:** Prompting & model integration (Phase 3).

---

### Pitfall 5: No data provenance or versioning

**What goes wrong:** Mixing datasets with different offsets/filters; inability to reproduce a training run or trace bad generations back to source clips.

**Why it happens:** One-off scripts, overwritten exports, and absent manifests for audio, transcripts, and filters.

**How to avoid:** Version manifests with checksums and offsets per VOD; keep raw, aligned, and filtered splits; log filter parameters and ASR model version; store train/eval splits immutably.

**Warning signs:** Two runs on “same” data yield different sample counts; unclear which ASR model produced current transcripts; bug fixes require reprocessing everything from scratch.

**Phase to address:** Data engineering foundation (Phase 1).

---

### Pitfall 6: Overfitting small slices of streams

**What goes wrong:** Model memorizes specific bits and loses general DougDoug chat style; eval looks good on nearby clips but fails on other streams.

**Why it happens:** Limited curated data, no stream-level cross-validation, and too many training epochs/low regularization on parameter-efficient fine-tunes.

**How to avoid:** Use stream-level holdouts; early-stop on held-out VODs; apply dropout/weight decay appropriate for LoRA; augment with slight timing jitter to avoid memorizing exact windows.

**Warning signs:** Sharp train/val loss gap; responses quote exact phrases from training clips; quality craters on unseen streams.

**Phase to address:** Fine-tuning & evaluation (Phase 3).

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hard-coded global time offset per VOD | Quick alignment proof-of-concept | Misaligned pairs when drift/ads occur; hard to fix downstream | MVP only with manual spot-checks |
| Keeping only processed transcripts (no raw audio slices) | Saves disk space | Cannot re-run better ASR or filters; irreproducible | Never; store at least compressed raw clips |
| Training without dataset manifests | Faster iteration | Impossible to trace bad samples; inconsistent eval splits | Never |
| Single-stage script for download→ASR→align | One command convenience | Any failure requires rerunning all stages; no caching | Acceptable for first VOD, replace with staged pipeline after |
| Ignoring speaker diarization | Faster ASR | Chat replies tied to wrong speaker/context in multi-voice segments | Only if clips are strictly single speaker |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Twitch chat exports | Assuming timestamps are relative to VOD start | Normalize to UTC epoch and compute offset to actual VOD start; record offset |
| VOD downloads (ffmpeg/TwitchDownloader) | Losing exact start time/ads trimmed differently than chat | Preserve original duration metadata; note trims; avoid auto-trim that desyncs chat |
| ASR (Whisper-family) | Running without VAD/diarization on long streams | Apply VAD + chunking; diarize if guests appear; batch by segment to keep timestamps stable |
| Dataset storage | Storing paths without checksums | Record checksums and byte ranges; keep manifests versioned |
| PEFT fine-tuning (LoRA/QLoRA) | Mismatched quantization vs adapter config | Keep consistent base quantization during train/infer; export adapters with config tracked |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Re-encoding full VODs for every stage | Long preprocessing times; disk churn | Cache extracted audio and transcripts; stage pipeline with idempotent steps | Breaks once >5 VODs processed |
| Huge context windows during training | OOM on consumer GPU; slow epochs | Cap tokens per sample; slide windows with overlap; use gradient accumulation judiciously | Breaks around 2–4K tokens on 12–24GB GPUs |
| Unsharded datasets | Single worker bottleneck; no resume | Shard by VOD and stream through dataloader; checkpoint progress | Breaks when adding more than a few hours of data |
| No mixed precision in ASR and training | Slow throughput | Use fp16/bf16 where supported; benchmark for quality impact | Breaks time budget on long VODs |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Keeping OAuth/Twitch tokens in scripts | Token leakage, unauthorized access | Use env vars/secrets files excluded from repo; rotate tokens |
| Publishing chat logs with usernames intact | Privacy concerns and potential TOS issues | Anonymize or hash usernames in shared artifacts; keep raw logs private |
| Shipping VOD excerpts without license notes | Reuse beyond fair-use-like bounds | Store usage notes with datasets; avoid redistribution; limit to internal use |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| No alignment QA UI (audio+chat playback) | Hidden offsets until training fails | Build a lightweight reviewer to scrub through aligned segments and flag offsets |
| Lack of controllable chat style knobs | Hard to adjust tone away from spam/toxicity | Expose temperature and filtering presets; allow toggling emote density |
| Missing eval visualizations | Stakeholders cannot tell if model matches chat timing | Show side-by-side audio timeline, gold chat, and model outputs for held-out clips |

## "Looks Done But Isn't" Checklist

- [ ] **Alignment verified per VOD:** Anchor events checked; offset/drift recorded.
- [ ] **ASR quality sampled:** Manual audit of random clips; confidence thresholds enforced.
- [ ] **Spam/toxicity filtered:** Emote spam capped; bots/mod commands removed; toxicity pass applied.
- [ ] **Manifest versioned:** Offsets, ASR model, filters, and splits recorded.
- [ ] **Train/infer parity tested:** Shadow inference uses same prompt/context as training.
- [ ] **Holdout eval ready:** Stream-level holdouts defined with metrics.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Drifted timestamps | MEDIUM | Recompute offsets with anchors; regenerate pairs; retrain on corrected dataset |
| Noisy transcripts | MEDIUM | Re-run ASR with better model/VAD; replace low-confidence segments; partial fine-tune refresh |
| Spam-dominated dataset | LOW | Refilter dataset with stricter rules; rebalance samples; light adapter retrain |
| Train/infer mismatch | LOW | Standardize prompt/context; regenerate training pairs; short adapter refresh |
| Missing provenance | HIGH | Reprocess from raw VOD/chat; recreate manifests; rerun training |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Drifted VOD↔chat timestamps | Phase 1: Data ingestion & alignment | Spot-check playback; stored offsets per VOD |
| Noisy/incorrect transcripts | Phase 2: Transcription & curation | WER/confidence sampling; manual audits |
| Spam/emote noise dominance | Phase 2: Dataset cleaning & balance | Token frequency checks; toxicity filter reports |
| Train/inference context mismatch | Phase 3: Prompting & integration | Shadow inference parity tests |
| No data provenance/versioning | Phase 1: Data engineering foundation | Manifests with checksums; reproducible splits |
| Overfitting small slices | Phase 3: Fine-tuning & eval | Stream-level holdout metrics; generalization tests |

## Sources

- Personal experience with VOD alignment, ASR pipelines, and PEFT fine-tuning for chat-like models (needs validation for DougDoug-specific data).
- Community discussions on Twitch chat exports and Whisper alignment practices (LOW confidence until project-specific validation).

---
*Pitfalls research for: Twitch VOD→chat alignment and local LLM fine-tuning*
*Researched: 2026-02-21*
