# Architecture Research

**Domain:** Local multimodal (video/audio/chat) data pipeline and local LLM fine-tuning
**Researched:** 2026-02-26
**Confidence:** MEDIUM-HIGH

## Standard Architecture

### System Overview

```text
┌───────────────────────────────────────────────────────────────────────────┐
│                         Orchestration + Lineage                          │
│        (DVC pipeline graph + run manifest + experiment IDs)              │
├───────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Ingestion    │  │ Extraction   │  │ Alignment    │  │ Curation     │  │
│  │ Adapters     │  │ Workers      │  │ Engine       │  │ + QA Gates   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │                 │          │
├─────────┴─────────────────┴─────────────────┴─────────────────┴──────────┤
│                           Training + Evaluation                            │
│             (HF Datasets -> TRL SFTTrainer + PEFT adapters)               │
├───────────────────────────────────────────────────────────────────────────┤
│                            Storage Tiers                                   │
│  raw/ (immutable) | staged/ (normalized) | curated/ (train-ready)         │
│  + metadata DB (DuckDB) + artifacts (checkpoints, metrics, reports)       │
└───────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| Ingestion adapters | Acquire source videos and sidecar metadata, assign canonical IDs, persist immutable originals | `yt-dlp` + content manifest writer + checksum ledger |
| Media extraction workers | Produce deterministic audio/video derivative assets and technical metadata | `ffmpeg` worker stage with fixed codec/sample-rate settings |
| Speech transcription service | Produce transcript segments with timestamps and confidence fields | Whisper/WhisperX batch worker with versioned model config |
| Chat extraction service | Produce normalized chat events `(ts, user, text, source)` in a single schema | Source-specific parser adapters with strict schema validation |
| Alignment engine | Join speech and chat timelines into candidate prompt/response pairs and scores | Windowed join + scoring/rerank + reject reasons |
| Curation and quality gates | Enforce dataset contract, deduplicate, split train/val/test, emit final parquet/jsonl | Rule-based filters + HF Datasets map/filter + validation reports |
| Training orchestrator | Fine-tune base model from curated dataset and log reproducible runs | TRL `SFTTrainer` + PEFT LoRA + MLflow run tracking |
| Evaluation harness | Run offline evals/regression checks before promoting a checkpoint | Fixed prompt suite + metric scripts + artifact comparator |

## Recommended Project Structure

```text
src/
├── contracts/                # Pydantic schemas and dataset contracts
│   ├── events.py             # Raw/staged/curated record models
│   └── quality.py            # Quality gate result models
├── ingest/                   # Source adapters and canonical manifesting
│   ├── video_sources.py      # yt-dlp and local file source adapters
│   └── manifest.py           # Deterministic content identity logic
├── extract/                  # Media and transcript extraction stages
│   ├── media.py              # ffmpeg audio/video derivative pipeline
│   └── asr.py                # Whisper/WhisperX transcription runners
├── align/                    # Temporal alignment and scoring
│   ├── candidate_windows.py  # Speech-to-chat candidate generation
│   └── ranker.py             # Pair scoring and thresholding
├── curate/                   # Cleaning, filtering, balancing, split logic
│   ├── dedupe.py             # Near-duplicate removal and spam filters
│   └── export.py             # Parquet/JSONL export for training
├── train/                    # Fine-tune and eval entrypoints
│   ├── sft.py                # TRL SFTTrainer + PEFT config
│   └── evaluate.py           # Offline eval and regression reports
└── infra/
    ├── dvc/                  # dvc.yaml stage definitions
    └── tracking.py           # MLflow helpers and run metadata binding

data/
├── raw/                      # Immutable downloaded/source assets
├── staged/                   # Extracted transcripts/chat normalized records
├── curated/                  # Final train-ready datasets
└── artifacts/                # Checkpoints, eval outputs, plots
```

### Structure Rationale

- **`contracts/`:** centralizes schema ownership so extraction/alignment/training cannot silently drift.
- **`ingest/` and `extract/`:** isolates source volatility from core logic and keeps transformations reproducible.
- **`align/` and `curate/`:** separates "pairing logic" from "quality policy" so you can tune each independently.
- **`train/`:** keeps model iteration independent from data engineering, while consuming only curated contracts.
- **`infra/`:** enforces lineage and run reproducibility without mixing orchestration code into domain logic.

## Architectural Patterns

### Pattern 1: Medallion-style Data Tiers (Raw -> Staged -> Curated)

**What:** Treat every stage as a one-way transformation into a stricter schema tier.
**When to use:** Always, because timestamp and pairing defects are easiest to detect before training.
**Trade-offs:** Extra storage and slower early iteration, but drastically lower rewrite risk.

**Example:**
```typescript
type RawAsset = { assetId: string; sourceUri: string; sha256: string };
type StagedUtterance = { assetId: string; startMs: number; endMs: number; text: string };
type CuratedPair = {
  sampleId: string;
  prompt: string;
  response: string;
  alignmentScore: number;
  provenance: { assetId: string; speechSpanMs: [number, number]; chatSpanMs: [number, number] };
};
```

### Pattern 2: Idempotent Stage Contracts with Content-addressed Outputs

**What:** Each stage output path/hash is a function of input hashes + config version.
**When to use:** For all expensive steps (ASR, alignment, training) to allow safe reruns and caching.
**Trade-offs:** More plumbing for manifests, but major savings in rerun cost and debugging time.

**Example:**
```typescript
function stageKey(stageName: string, inputHashes: string[], configHash: string): string {
  return sha256(`${stageName}:${inputHashes.sort().join(",")}:${configHash}`);
}
```

### Pattern 3: Alignment as Candidate Generation + Scoring, Not Direct Join

**What:** First generate candidate chat windows near each speech segment, then rank/threshold.
**When to use:** Any stream-like conversation data where temporal proximity alone is noisy.
**Trade-offs:** Slightly more complexity than nearest-neighbor timestamps, much better precision.

**Example:**
```typescript
function buildCandidates(speechStartMs: number, speechEndMs: number, chatEvents: number[]): number[] {
  const preWindow = [speechStartMs - 8000, speechStartMs + 2000];
  return chatEvents.filter((ts) => ts >= preWindow[0] && ts <= preWindow[1]);
}
```

## Data Flow

### Request Flow

```text
[Video URI list]
    ↓
[Ingestion Adapter] -> [Manifest + Checksums] -> [raw/]
    ↓
[Media Extraction] -> [Audio Derivatives] -> [staged/audio]
    ↓
[ASR Transcription] -> [Speech Segments + Word/segment timestamps] -> [staged/speech]
    ↓
[Chat Extraction] -> [Normalized chat events] -> [staged/chat]
    ↓
[Alignment Engine] -> [Candidate pairs + scores + rejects] -> [staged/aligned]
    ↓
[Curation + QA] -> [Curated train/val/test parquet/jsonl] -> [curated/]
    ↓
[Training] -> [Adapter checkpoints + metrics] -> [artifacts/models]
    ↓
[Evaluation] -> [Regression report + promoted model tag]
```

### State Management

```text
[DVC stage graph + lockfile]
    ↓ (materialization)
[raw/staged/curated artifact states]
    ↓ (run metadata)
[MLflow experiment/runs + model artifacts]
    ↓ (query)
[DuckDB metadata views for audit/debug]
```

### Key Data Flows

1. **Extraction flow:** source video -> deterministic media derivatives -> timestamped speech/chat records.
2. **Alignment flow:** staged speech/chat -> scored candidate pairs -> reject/accept decisions with provenance.
3. **Training flow:** curated dataset snapshot -> adapter fine-tune run -> metrics/checkpoints linked to data version.

## Suggested Build Order (Safest)

1. **Foundation and contracts first**
   - Create schemas, manifest IDs, directory conventions, and DVC stage skeleton.
   - Why first: prevents downstream schema churn and untraceable data drift.

2. **Ingestion + immutable raw storage**
   - Implement source acquisition and checksumming only.
   - Why second: gives a reproducible baseline corpus before any lossy transforms.

3. **Speech extraction pipeline (audio + ASR timestamps)**
   - Add ffmpeg derivatives and Whisper/WhisperX outputs.
   - Why third: speech timeline is the primary anchor for alignment.

4. **Chat extraction and normalization**
   - Implement parser adapters that output one canonical chat-event schema.
   - Why fourth: alignment is blocked until both timelines are normalized.

5. **Alignment engine + error analysis tooling**
   - Build candidate windows, scoring, thresholds, and manual review exports.
   - Why fifth: this is the highest quality risk and should be stabilized pre-training.

6. **Curation and dataset QA gates**
   - Dedup, safety/quality filters, split generation, final export.
   - Why sixth: training only on validated, contract-compliant data avoids expensive bad runs.

7. **Fine-tuning and evaluation harness**
   - Add TRL + PEFT training scripts and repeatable eval suites.
   - Why last: model iteration is only useful after alignment quality is measurable and stable.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-1k hours source media | Single-machine pipeline with DVC + local disk; batch extraction is enough |
| 1k-20k hours | Split workers by stage (extract/align/train), adopt queue-based batch execution, keep centralized metadata |
| 20k+ hours | Distributed extraction/alignment workers, shard-wise curation, object storage for artifacts, stronger dataset governance |

### Scaling Priorities

1. **First bottleneck: ASR throughput and GPU memory** -> batch sizing, model size tiers, cache immutable stage outputs.
2. **Second bottleneck: alignment QA effort** -> confidence-driven triage and sampled human review before training.

## Anti-Patterns

### Anti-Pattern 1: Training Directly from Freshly Extracted Data

**What people do:** feed ASR/chat outputs directly into fine-tuning.
**Why it is wrong:** alignment mistakes become model behavior and are hard to unwind.
**Do this instead:** require staged alignment scores and curation gates before any training job.

### Anti-Pattern 2: Mixing Source-specific Parsing Rules Inside Alignment Logic

**What people do:** put Twitch/YouTube/source quirks directly in alignment code.
**Why it is wrong:** boundaries blur, and every new source breaks alignment behavior.
**Do this instead:** isolate source adapters in `ingest/` and emit one normalized event contract.

### Anti-Pattern 3: Non-versioned Prompts/Splits During Training

**What people do:** rerun training with changed templates/splits but same run label.
**Why it is wrong:** metrics are not comparable and regressions become invisible.
**Do this instead:** hash prompt templates + split manifests and log them as first-class run artifacts.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| yt-dlp | CLI adapter in ingestion stage | Strong site support; keep deterministic output templates |
| ffmpeg | CLI transform worker | Canonical media decode/encode backbone for all downstream stages |
| Whisper / WhisperX | Python worker API | WhisperX provides word-level alignment and diarization hooks |
| Hugging Face Datasets | Python API for map/filter/export | Efficient dataset transforms and local disk persistence |
| TRL + PEFT | Python training stack | Standard local SFT + LoRA adapter path |
| DVC | Pipeline DAG + lockfiles | Reproducible stage orchestration and run cache |
| MLflow | Experiment tracking API/UI | Structured linkage of params, metrics, and artifacts |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| ingest -> extract | file manifests + immutable asset IDs | Never mutate raw assets after ingestion |
| extract -> align | staged schema records (`speech`, `chat`) | Enforce strict timestamp units (ms) and timezone policy |
| align -> curate | scored pairs + reject reasons | Keep rejects for diagnostics, not just accepted samples |
| curate -> train | versioned dataset snapshot ID | Training must reference explicit curated snapshot |
| train -> evaluate | checkpoint IDs + eval suite version | Promotion requires regression pass against fixed suite |

## Sources

- DVC data pipelines and reproducible DAG workflows (official docs, current): https://dvc.org/doc/start/data-pipelines/data-pipelines (HIGH)
- Hugging Face Datasets processing and local persistence formats (official docs): https://huggingface.co/docs/datasets/en/process (HIGH)
- Hugging Face Datasets audio loading/resampling behavior: https://huggingface.co/docs/datasets/en/audio_load (HIGH)
- TRL SFTTrainer dataset contracts and training flow: https://huggingface.co/docs/trl/en/sft_trainer (HIGH)
- PEFT LoRA/QLoRA operational guidance: https://huggingface.co/docs/peft/en/developer_guides/lora (HIGH)
- Whisper baseline capabilities and ffmpeg dependency: https://github.com/openai/whisper (MEDIUM)
- WhisperX architecture for word-level timestamps + alignment + diarization: https://github.com/m-bain/whisperX (MEDIUM)
- pyannote speaker diarization local pipeline and benchmarks: https://github.com/pyannote/pyannote-audio (MEDIUM)
- DuckDB Parquet read/write + pushdown for metadata/query workflows: https://duckdb.org/docs/stable/data/parquet/overview (HIGH)
- MLflow tracking model/run metadata and artifacts: https://mlflow.org/docs/latest/ml/tracking/ (HIGH)
- Torchaudio forced alignment API deprecation notice (used as caution): https://pytorch.org/audio/stable/tutorials/ctc_forced_alignment_api_tutorial.html (HIGH)

---
*Architecture research for: local multimodal extraction-alignment-curation-training pipeline*
*Researched: 2026-02-26*
