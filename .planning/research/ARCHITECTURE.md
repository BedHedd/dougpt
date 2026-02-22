# Architecture Research

**Domain:** Local LLM fine-tuning from DougDoug VODs + Twitch chat
**Researched:** 2026-02-21
**Confidence:** MEDIUM

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Data Ingestion Layer                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌────────────┐  ┌─────────────┐               │
│  │ VOD DL │  │ Chat Import │  │ Metadata ETL│               │
│  └────┬────┘  └─────┬──────┘  └──────┬──────┘               │
│       │             │              │                        │
├───────┴─────────────┴──────────────┴────────────────────────┤
│               Media & Transcript Processing Layer            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌────────────┐  ┌───────────┐  │
│  │ Demux/VAD│  │ ASR (Wh.)│  │ Diarization│  │ Alignment │  │
│  └────┬─────┘  └────┬─────┘  └────┬───────┘  └─────┬─────┘  │
│       │             │             │               │         │
├───────┴─────────────┴─────────────┴───────────────┴─────────┤
│                  Dataset Assembly & QA Layer                │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────────┐  ┌──────────────┐             │
│  │ Window  │  │ Toxicity/QA │  │ HF Dataset   │             │
│  └────┬────┘  └──────┬──────┘  └──────┬───────┘             │
│       │              │               │                      │
├───────┴──────────────┴───────────────┴──────────────────────┤
│                Training & Evaluation Layer                  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐         │
│  │ Tokenizer   │  │ PEFT FineTune│  │ Eval Harness │         │
│  └────┬────────┘  └──────┬───────┘  └──────┬──────┘         │
│       │                 │                │                 │
├───────┴─────────────────┴────────────────┴─────────────────┤
│                     Inference & Serving                     │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌───────────────┐  ┌──────────────┐          │
│  │ Context  │  │ Chat Generator │  │ Guardrails  │          │
│  └──────────┘  └──────┬────────┘  └──────────────┘          │
│                       │                                     │
└───────────────────────┴─────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| VOD downloader | Fetch raw VOD video and associated metadata to local storage | `yt-dlp`/Twitch API + checksum + manifest |
| Chat import | Export chat logs with message timestamps, user IDs, badges | Twitch chat export, JSONL normalization |
| Demux/VAD | Extract audio, normalize loudness, trim silence, split by speech | `ffmpeg` + WebRTC VAD + segment manifest |
| ASR | Transcribe audio with token-level timestamps | Whisper CLI/Python (`transcribe` sliding windows) |
| Diarization (optional) | Identify speaker turns to mask streamer vs chat TTS | `pyannote.audio` diarization pipeline |
| Alignment | Align chat messages to transcript windows; handle drift/offsets | Heuristic offset search + dynamic windowing; store offsets per segment |
| Dataset assembly | Build supervised pairs (audio context or transcript + prior chat → next chat message) | HF `datasets` builder with schema and dataset card |
| Quality gates | Filter toxicity/spam, drop low-ASR-confidence spans | Detoxify/regex filters + ASR logprob thresholds |
| Tokenizer & formatting | Format chat style prompts, insert metadata tokens, pad/truncate | HF `transformers` tokenizer with special tokens |
| Fine-tuning | Parameter-efficient SFT (LoRA/QLoRA) on local causal LM | HF `transformers` + `peft` training loop |
| Eval harness | Held-out segments + toxicity/fluency metrics; regression suite | Scripted eval with BLEU/ROUGE + heuristic repetition checks |
| Inference pipeline | Consume recent audio/transcript context, generate chat-like replies | Sliding context window + greedy/sampling decoding |
| Guardrails | Block banned words/spam, limit repetition and rate | Regex lists, similarity checks, max responses/min timeout |
| Storage | Persist raw media, transcripts, aligned pairs, checkpoints | Local object store (filesystem/LMDB) with versioned manifests |

## Recommended Project Structure

```
src/
├── ingest/                 # VOD downloaders, chat importers, manifests
│   ├── twitch_api.py       # Twitch/VOD metadata fetching
│   ├── vod_downloader.py   # yt-dlp/ffmpeg wrappers
│   └── chat_parser.py      # Parse/export chat logs → JSONL
├── audio/                  # Media prep and transcription
│   ├── demux.py            # ffmpeg demux + loudness normalize
│   ├── vad.py              # VAD-based segmenter
│   ├── asr.py              # Whisper transcription + timestamps
│   └── diarize.py          # Optional speaker diarization
├── alignment/              # Time alignment and pairing
│   ├── offset_finder.py    # Drift estimation between chat and audio
│   ├── window_builder.py   # Build context windows around messages
│   └── align_manifest.py   # Persist alignment metadata
├── dataset/                # Dataset assembly and quality filters
│   ├── schema.py           # HF dataset schema + features
│   ├── build.py            # Create train/val/test splits
│   └── filters.py          # Toxicity/quality filters
├── training/               # Fine-tuning and evaluation
│   ├── tokenizer.py        # Special tokens, formatting
│   ├── lora_trainer.py     # PEFT/QLoRA training loop
│   ├── eval.py             # Held-out eval + metrics
│   └── config/             # YAML configs per run
├── inference/              # Local inference pipeline
│   ├── context_builder.py  # Recent audio/transcript windowing
│   ├── generate.py         # Chat-style decoding + sampling
│   └── guardrails.py       # Safety/rate controls
├── storage/                # Paths and manifest management
│   ├── layout.py           # Directory conventions
│   └── registry.py         # Versioned artifacts, checksums
└── cli/                    # Entry points for jobs
    └── main.py
```

### Structure Rationale

- **ingest/**: Isolate Twitch/VOD dependencies; produces stable manifests that downstream steps consume.
- **audio/**: Groups expensive media transforms; enables reuse of transcripts across experiments.
- **alignment/**: Keeps drift-handling logic separate to iterate independently from ASR.
- **dataset/**: Centralizes schema, filters, and split logic to avoid leakage and reproducibility issues.
- **training/**: Encapsulates PEFT configs and eval so model iterations do not affect ingestion.
- **inference/**: Thin layer to adapt trained checkpoints into local chat-like responders with guardrails.
- **storage/**: Single source of truth for file layout and checksums to prevent path drift.

## Architectural Patterns

### Pattern 1: Manifest-driven pipeline

**What:** Each stage writes a manifest (JSON/YAML) describing inputs, outputs, timestamps, offsets, and checksums.
**When to use:** Anytime data volumes are moderate and steps may be rerun; enables incremental recompute and auditing.
**Trade-offs:** Requires discipline to version manifests; slight overhead to maintain.

**Example:**
```python
manifest = {
    "vod_id": vod_id,
    "audio_path": audio_path,
    "segments": segments,  # start/end, asr_confidence
    "chat_offset_sec": best_offset,
    "dataset_version": dataset_version,
}
write_json(manifest_path, manifest)
```

### Pattern 2: Sliding-window alignment

**What:** Use sliding transcript windows with candidate time offsets to pair chat messages to nearby audio text.
**When to use:** When chat timestamps drift relative to VOD timecodes or start late/early.
**Trade-offs:** Heuristic; needs evaluation to avoid mislabeling. Adds compute proportional to offset search space.

**Example:**
```python
def align_message(msg_ts, transcript, offsets=(-10, 10), window=15):
    candidates = []
    for o in offsets:
        window_ts = (msg_ts + o, msg_ts + o + window)
        text = transcript.slice(window_ts)
        score = keyword_overlap(msg.text, text)
        candidates.append((score, o, text))
    return max(candidates)
```

### Pattern 3: Parameter-efficient fine-tuning (PEFT)

**What:** Attach low-rank adapters (LoRA/QLoRA) to a base chat-competent causal LM and fine-tune on aligned pairs.
**When to use:** Consumer GPUs; need fast iteration and small checkpoints.
**Trade-offs:** Slightly lower ceiling than full fine-tune; requires base model availability and quantization care.

**Example:**
```python
from peft import LoraConfig, get_peft_model

config = LoraConfig(r=8, lora_alpha=16, target_modules=["q_proj", "v_proj"], lora_dropout=0.05)
model = AutoModelForCausalLM.from_pretrained(base_model, load_in_4bit=True)
model = get_peft_model(model, config)
```

## Data Flow

### Request Flow

```
Raw VOD → VOD downloader → Audio demux/VAD → Whisper ASR (timestamps)
    ↓
Chat export → Chat parser → Normalized chat JSONL
    ↓
Alignment engine (offset search + windowing) → Paired samples
    ↓
Dataset builder (splits + filters) → HF dataset
    ↓
Tokenizer/formatter → PEFT trainer → Checkpoint
    ↓
Inference pipeline (context builder + generator + guardrails)
```

### State Management

```
Manifest store
    ↓ (read-only)
Pipeline stages → update manifests → artifacts on disk
    ↓
Training configs → checkpoints → inference configs
```

### Key Data Flows

1. **Media → Transcript:** Demuxed audio segments feed Whisper, producing timestamped tokens; manifests capture confidence/logprob.
2. **Chat → Alignment:** Chat messages with absolute timestamps are offset-adjusted, matched to transcript windows, and produce (context, target) pairs with provenance.
3. **Dataset → Training:** Clean pairs are tokenized with special chat tokens and streamed into a PEFT trainer; checkpoints and eval metrics are versioned.
4. **Context → Inference:** Recent transcript window is built, passed through the fine-tuned model with guardrails before emitting chat-style text.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-1k users / few VODs | Single-machine pipeline; serial jobs; local disk store. |
| 1k-100k users / tens of VODs | Parallelize ingestion/transcription; use job queue (Celery/RQ); cache Whisper features; incremental manifests. |
| 100k+ users / hundreds of VODs | Move media to object storage; distributed ASR workers; sharded HF datasets; evaluation farm; separate inference service with batching. |

### Scaling Priorities

1. **First bottleneck:** ASR throughput; mitigate with batched Whisper inference or smaller models for drafts.
2. **Second bottleneck:** Disk and I/O for media; mitigate with compressed intermediates and object storage with signed URLs.
3. **Third bottleneck:** Training time; mitigate with QLoRA, gradient checkpointing, and smaller context windows.

## Anti-Patterns

### Anti-Pattern 1: No drift correction

**What people do:** Assume chat timestamps align perfectly to VOD; build pairs without offset search.
**Why it's wrong:** Small delays/desync produce mislabeled pairs, harming fine-tune quality.
**Do this instead:** Estimate per-VOD offset via keyword overlap or correlation against transcript; store offsets in manifests.

### Anti-Pattern 2: Mixing streamer speech and chat targets

**What people do:** Use raw ASR text (mostly streamer speech) as model input without masking speaker/role.
**Why it's wrong:** Model learns to mimic streamer, not chat; responses become incoherent.
**Do this instead:** Use diarization or channel heuristics to mask streamer voice and preserve only chat-relevant context.

### Anti-Pattern 3: Training/test leakage across same VOD

**What people do:** Randomly split samples, causing adjacent windows from a single stream to appear in both train and eval.
**Why it's wrong:** Inflates metrics; hides overfitting to stream-specific memes.
**Do this instead:** Split by VOD/session; hold out entire streams for evaluation.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Twitch/YouTube VOD | API + `yt-dlp` download with manifest logging | Handle auth rate limits; cache metadata |
| Whisper ASR | Local Python/CLI with GPU | Requires `ffmpeg`; sliding 30s windows with timestamps (Whisper README) |
| PEFT/Transformers | Local training for LoRA/QLoRA | Keep base model weights locally; monitor VRAM |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| ingest ↔ audio | File manifests + paths | Decouple API credentials from media transforms |
| audio ↔ alignment | Transcript JSON + segment metadata | Preserve timestamps/confidence for alignment heuristics |
| alignment ↔ dataset | Aligned pairs + offsets | Include provenance (VOD ID, message ID) to debug |
| dataset ↔ training | HF dataset + tokenizer config | Freeze schema versions per experiment |
| training ↔ inference | Checkpoint + generation config | Store sampling defaults with model card |

## Sources

- Whisper README (timestamped ASR, sliding 30s windows): https://github.com/openai/whisper
- Hugging Face PEFT docs (parameter-efficient fine-tuning for consumer hardware): https://huggingface.co/docs/peft/index

---
*Architecture research for: Local LLM fine-tuning from DougDoug VODs + Twitch chat*
*Researched: 2026-02-21*
