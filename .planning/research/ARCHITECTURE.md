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

## Recommended Project Structure (Worktree Convention)

```text
[project-root]/
├── 00-dev-log/                               # Research notes and execution logs
├── 00-supporting-files/
│   ├── data/
│   │   ├── raw/                              # Immutable source media/chat assets
│   │   ├── staged/                           # Normalized transcript/chat/alignment outputs
│   │   ├── curated/                          # Train-ready datasets and split manifests
│   │   └── artifacts/                        # Training checkpoints, eval reports, plots
│   └── images/                               # Snapshot images and debug captures
├── 02-worktrees/
│   ├── README.md                             # Worktree lifecycle and naming convention
│   └── <feature-worktree>/
│       ├── pyproject.toml                    # Worktree-local dependencies
│       ├── ingest/                           # Source adapters + deterministic manifests
│       ├── extract/                          # ffmpeg/ASR/OCR stages
│       ├── align/                            # Candidate windows + scoring
│       ├── curate/                           # QA gates, dedupe, export
│       ├── train/                            # PEFT/TRL training + eval entrypoints
│       └── tests/                            # Worktree-local tests
└── .planning/
    ├── research/                             # Domain research and architecture decisions
    └── codebase/                             # Repository structure and conventions mapping
```

### Structure Rationale

- **`02-worktrees/<feature-worktree>/`:** isolates branch-scoped implementation so parallel experiments do not collide.
- **`00-supporting-files/data/`:** keeps durable artifacts in one canonical location shared across worktrees.
- **`ingest/` -> `train/` inside each worktree:** preserves clear stage boundaries while keeping code near the active branch context.
- **`tests/` inside each worktree:** matches current repo convention where there is no single root test harness.
- **`.planning/research/` and `.planning/codebase/`:** keeps planning context in tracked root docs while implementation stays worktree-local.

## Architectural Patterns

### Pattern 1: Medallion-style Data Tiers (Raw -> Staged -> Curated)

**What:** Treat every stage as a one-way transformation into a stricter schema tier.
**When to use:** Always, because timestamp and pairing defects are easiest to detect before training.
**Trade-offs:** Extra storage and slower early iteration, but drastically lower rewrite risk.

**Example:**
```python
from typing import TypedDict


class RawAsset(TypedDict):
    asset_id: str
    source_uri: str
    sha256: str


class StagedUtterance(TypedDict):
    asset_id: str
    start_ms: int
    end_ms: int
    text: str


class CuratedPair(TypedDict):
    sample_id: str
    prompt: str
    response: str
    alignment_score: float
    provenance: dict[str, object]
```

### Pattern 2: Idempotent Stage Contracts with Content-addressed Outputs

**What:** Each stage output path/hash is a function of input hashes + config version.
**When to use:** For all expensive steps (ASR, alignment, training) to allow safe reruns and caching.
**Trade-offs:** More plumbing for manifests, but major savings in rerun cost and debugging time.

**Example:**
```python
import hashlib


def stage_key(stage_name: str, input_hashes: list[str], config_hash: str) -> str:
    payload = f"{stage_name}:{','.join(sorted(input_hashes))}:{config_hash}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
```

### Pattern 3: Alignment as Candidate Generation + Scoring, Not Direct Join

**What:** First generate candidate chat windows near each speech segment, then rank/threshold.
**When to use:** Any stream-like conversation data where temporal proximity alone is noisy.
**Trade-offs:** Slightly more complexity than nearest-neighbor timestamps, much better precision.

**Example:**
```python
def build_candidates(speech_start_ms: int, speech_end_ms: int, chat_events: list[int]) -> list[int]:
    pre_window = (speech_start_ms - 8000, speech_start_ms + 2000)
    return [ts for ts in chat_events if pre_window[0] <= ts <= pre_window[1]]
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

## Where Automation Lives

### GSD Instructions + Worktree Rules (primary)

The automation engine is GSD plus Git worktree conventions:

1. **`02-worktrees/README.md`** defines branch/worktree lifecycle commands.
2. **`.planning/PROJECT.md`** defines requirements and execution intent.
3. **`.planning/codebase/` + `.planning/research/`** encode structure and decision context.
4. **GSD orchestration** executes git/worktree/file-edit flows directly per task.

This repo intentionally avoids heavy script wrappers in v1 because worktree operations are simple and infrequent, and the AI workflow already executes git commands deterministically.

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
