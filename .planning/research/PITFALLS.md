# Pitfalls Research

**Domain:** Local stream-data extraction and model fine-tuning (DougDoug speech -> Twitch chat)
**Researched:** 2026-02-26
**Confidence:** MEDIUM

## Critical Pitfalls

### Pitfall 1: Using ingest-time chat timestamps instead of source timestamps

**What goes wrong:**
Chat messages are aligned by when your collector received them, not when Twitch sent them, causing systematic chat/audio offset and noisy training pairs.

**Why it happens:**
Teams parse IRC `PRIVMSG` text but ignore or inconsistently trust tags like `tmi-sent-ts`; they also miss that IRC delivery order is not guaranteed and duplicates can occur.

**How to avoid:**
Treat `tmi-sent-ts` as canonical event time, persist raw message IDs, and deduplicate by message ID. Build a reorder window in ingestion and keep raw + normalized logs for replay.

**Warning signs:**
- Frequent negative lag (chat appears before prompt) or bimodal lag histograms
- Duplicate chat rows with same content/user around the same second
- Alignment quality changes between runs on identical input

**Phase to address:**
Phase 1 - Data ingestion and timestamp normalization

---

### Pitfall 2: Ignoring Shared Chat metadata and room provenance

**What goes wrong:**
Messages from shared-chat sessions are attributed to the wrong room/context, mixing audience behavior from different channels into one training set.

**Why it happens:**
Teams consume IRC messages without preserving `source-room-id` / `source-id` tags and assume one room timeline.

**How to avoid:**
Store both `room-id` and `source-room-id`; segment datasets by source room; exclude cross-room data unless explicitly modeling shared chat.

**Warning signs:**
- Sudden style shifts in chat language within a single segment
- Inexplicable spikes in chatter count unrelated to on-screen events
- Same logical message appearing with different channel context

**Phase to address:**
Phase 1 - Data ingestion and provenance schema

---

### Pitfall 3: Treating Whisper segment timestamps as ground truth

**What goes wrong:**
DougDoug prompt boundaries drift by seconds, causing chat responses to be paired with the wrong prompt and reducing fine-tune signal quality.

**Why it happens:**
OpenAI Whisper uses sliding 30-second windows; teams skip post-alignment and assume segment times are precise enough for conversational pairing.

**How to avoid:**
Run forced alignment (word-level) after ASR, use VAD-aware segmentation, and store confidence per token/word. Reject low-confidence prompt boundaries.

**Warning signs:**
- Many high-quality chat replies appear outside the expected response window
- Manual spot checks show prompts shifted by ~1-4 seconds
- Alignment quality degrades more on long monologues

**Phase to address:**
Phase 2 - Transcription and transcript quality gates

---

### Pitfall 4: Failing to normalize transcript text for aligners

**What goes wrong:**
Large portions of transcript cannot be aligned (numbers, symbols, currency, stylized text), leaving holes exactly where temporal precision is needed.

**Why it happens:**
Forced aligners are language/model dependent; unsupported tokens and punctuation are passed through unnormalized.

**How to avoid:**
Add a transcript normalization stage (number verbalization, punctuation policy, symbol mapping), with per-language aligner checks and fallback behavior.

**Warning signs:**
- High proportion of words with missing timestamps
- Alignment drops sharply on donation amounts, years, URLs, or emotes
- Frequent null/NaN word boundaries in aligned output

**Phase to address:**
Phase 2 - Transcript preprocessing and alignment readiness

---

### Pitfall 5: Ignoring overlapping speech / crowd noise failure modes

**What goes wrong:**
Prompt extraction includes cross-talk, TTS overlays, or game audio as if it were DougDoug, contaminating prompt text and timing.

**Why it happens:**
Teams assume single-speaker clean audio, but stream audio is multi-source; diarization quality is imperfect and often skipped for speed.

**How to avoid:**
Apply source separation or diarization where feasible, maintain a "prompt purity" score, and filter low-purity segments out of training.

**Warning signs:**
- Prompt text includes unrelated in-game narration or voice-over
- High WER only during hype/chaotic segments
- Repeated model errors tied to specific stream formats

**Phase to address:**
Phase 2 - Audio quality controls and speaker isolation

---

### Pitfall 6: Building alignment windows without empirical lag calibration

**What goes wrong:**
Static "chat within N seconds" rules overfit to a few videos; response windows miss real reactions or include unrelated chatter.

**Why it happens:**
Teams hard-code one lag assumption and never estimate lag distribution per stream, segment type, or event intensity.

**How to avoid:**
Calibrate lag on a labeled subset, track per-video lag distributions, and use adaptive windows (plus confidence scoring) instead of fixed cutoffs.

**Warning signs:**
- Alignment precision swings across videos from different eras/events
- High proportion of generic chat mapped to specific prompts
- Manual labeling disagreement concentrated on boundary cases

**Phase to address:**
Phase 3 - Pairing heuristics and dataset assembly

---

### Pitfall 7: Training with mismatched chat template and loss masking

**What goes wrong:**
The model learns formatting artifacts or predicts user/prompt tokens instead of assistant/chat response behavior, hurting inference quality.

**Why it happens:**
Dataset format and training config are inconsistent (e.g., wrong template, missing assistant-only/completion-only masking, EOS mismatch).

**How to avoid:**
Lock one canonical conversation format, validate rendered training text before runs, and enforce assistant/completion-only loss where appropriate.

**Warning signs:**
- Model outputs role tokens or malformed chat wrappers
- Good train loss but weak response quality in eval prompts
- Early EOS truncation or run-on completions

**Phase to address:**
Phase 4 - Fine-tuning pipeline and config validation

---

### Pitfall 8: Assuming quantized full-model fine-tuning is available locally

**What goes wrong:**
Runs fail or silently degrade because the team attempts unsupported full-parameter training on 4-bit/8-bit models in constrained hardware.

**Why it happens:**
Teams confuse inference quantization with full training support; they skip adapter-based design and memory budgeting.

**How to avoid:**
Use PEFT/LoRA-style adapter training on quantized base models, pre-compute VRAM budgets, and gate runs with a dry-run memory check.

**Warning signs:**
- OOM at first optimizer step despite successful model load
- Frequent precision/dtype instability changes between runs
- Training scripts work only on one machine and are not reproducible

**Phase to address:**
Phase 4 - Local training strategy and hardware envelope

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Skip confidence columns in transcript/alignment tables | Faster initial pipeline | No way to quarantine low-quality pairs later | Never |
| Keep only final aligned dataset, discard raw events | Less storage complexity | Impossible to re-align with improved heuristics | Never |
| One global lag window for all videos | Simple implementation | Biased dataset; weak cross-stream generalization | MVP only, with explicit TODO + metrics |
| Hand-edited training JSON without schema checks | Quick fixes | Non-reproducible experiments and silent format drift | Never |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Re-running ASR for every alignment tweak | Iterations take hours/days | Cache immutable artifacts per stage (audio, ASR, alignment) | >20 long VODs |
| Single-process dataset transforms | CPU pegged but low throughput | Batched + multiprocessing preprocessing with deterministic seeds | Mid-size corpora (10k+ pairs) |
| No shard/checkpoint strategy during fine-tuning | Lost runs on crash/OOM | Frequent checkpoints + resumable dataloaders | Long runs on consumer GPUs |

## "Looks Done But Isn't" Checklist

- [ ] **Timeline alignment:** Validate lag histogram and manual spot checks on at least 3 stream types
- [ ] **Transcript quality:** Track WER proxy/confidence and % unaligned words before dataset export
- [ ] **Pair quality:** Require per-example alignment confidence and filter thresholds in export script
- [ ] **Fine-tuning:** Verify chat template render + EOS behavior with a tiny overfit sanity run
- [ ] **Reproducibility:** Freeze config, random seeds, and tool versions in each training artifact

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Ingest-time timestamps used as truth | Phase 1 | Offset histogram stable; duplicates removed by message ID |
| Shared-chat provenance loss | Phase 1 | `room-id` and `source-room-id` present in schema and tests |
| Whisper timestamps treated as exact | Phase 2 | Word-level alignment coverage and manual boundary checks pass |
| Unnormalized transcript text for aligner | Phase 2 | Unaligned-token rate below threshold |
| Overlap/noise contamination | Phase 2 | Prompt-purity score enforced in filtering |
| Uncalibrated lag windows | Phase 3 | Labeled validation set shows precision/recall targets met |
| Template/loss masking mismatch | Phase 4 | Sanity run outputs correctly formatted replies |
| Unsupported quantized full fine-tune assumptions | Phase 4 | Dry-run memory + train step pass on target hardware |

## Sources

- Twitch IRC Concepts and tag reference (ordering, duplicate delivery risk, `tmi-sent-ts`, shared-chat tags): https://dev.twitch.tv/docs/chat/irc/ (HIGH)
- OpenAI Whisper README (30-second sliding window; segment timestamp limitations context): https://github.com/openai/whisper/blob/main/README.md (HIGH)
- WhisperX README and limitations (word-level alignment benefits; unsupported tokens, overlap and diarization limitations): https://github.com/m-bain/whisperX/blob/main/README.md (MEDIUM)
- Torchaudio forced alignment tutorial (API deprecation note; alignment workflow and confidence interpretation): https://pytorch.org/audio/stable/tutorials/forced_alignment_tutorial.html (MEDIUM)
- TRL SFT Trainer docs (dataset formats, assistant/completion-only loss, chat template and EOS caveats): https://huggingface.co/docs/trl/sft_trainer (HIGH)
- Transformers chat templating docs (format mismatch and special-token duplication risks): https://huggingface.co/docs/transformers/chat_templating (HIGH)
- Transformers bitsandbytes docs (4-bit/8-bit training supports extra parameters only; quantization caveats): https://huggingface.co/docs/transformers/quantization/bitsandbytes (HIGH)

---
*Pitfalls research for: DougGPT Twitch Chat Model (pitfalls dimension)*
*Researched: 2026-02-26*
