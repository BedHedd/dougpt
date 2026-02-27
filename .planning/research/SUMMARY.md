# Project Research Summary

**Project:** dougpt Twitch Chat Model
**Domain:** Local multimodal (video/audio/chat) extraction, alignment, and local LLM adapter fine-tuning
**Researched:** 2026-02-26
**Confidence:** MEDIUM-HIGH

## Executive Summary

This project is a local-first data and training pipeline product, not a single model script. The core goal is to convert DougDoug videos into high-quality prompt/response supervision where DougDoug speech is the prompt and Twitch chat is the response, then fine-tune a local model with reproducible runs. The research is consistent across stack, feature, and architecture outputs: experts build this class of system as a staged pipeline with strict schema contracts, immutable raw artifacts, and explicit quality gates before any training.

The recommended approach is to prioritize deterministic ingestion and timestamp quality over early model iteration speed. Use Python 3.12, FFmpeg, WhisperX (with word-level alignment), and a normalized chat extraction path (prefer direct chat export when available, OCR fallback when only rendered video exists). Persist data through medallion-style tiers (`raw -> staged -> curated`), run alignment as candidate generation plus scoring (not naive nearest timestamp), and only train once alignment confidence and QA thresholds are stable.

The key risks are timing/provenance errors that silently poison training data, plus training configuration mismatches that look successful but degrade inference quality. Mitigation is clear: canonical timestamp/provenance fields at ingest, transcript normalization and confidence tracking, adaptive lag calibration, reject-reason logging, and strict chat-template/loss-masking validation before full runs.

## Key Findings

### Recommended Stack

The stack converges on a Python-native local pipeline with reproducibility tooling around it. FFmpeg anchors deterministic media extraction, WhisperX/faster-whisper handle timestamped ASR, and PaddleOCR+OpenCV provide a fallback path for rendered chat recovery. DuckDB + Polars support fast local QA/joins, while Transformers + PEFT + TRL + bitsandbytes/Unsloth provide a pragmatic QLoRA-first fine-tuning path for consumer hardware.

**Core technologies:**
- `Python 3.12.x`: single runtime for extraction, alignment, and training; minimizes glue overhead.
- `FFmpeg 8.0.1`: deterministic media demux/resample/frame extraction with stable CLI behavior.
- `WhisperX 3.8.1` (+ `faster-whisper 1.2.1`): word-level timestamps and alignment required for pairing quality.
- `PaddleOCR 3.4.0` + `OpenCV 4.13.0.92`: practical local OCR preprocessing/recognition for overlay chat.
- `PyTorch 2.10.0` + `Transformers 5.2.0` + `PEFT 0.18.1` + `TRL 0.29.0`: standard adapter fine-tuning stack.
- `DuckDB 1.4.4` + `Polars 1.38.1` + `DVC 3.66.1` + `Snakemake 9.16.3`: reproducible dataset lineage, orchestration, and QA analytics.

### Expected Features

The research defines a tight MVP boundary: prove end-to-end data quality and learning value offline before expanding capability. v1 must ship deterministic ingestion, timestamp-accurate transcription/alignment/QA, and reproducible adapter training with baseline evaluation and local inference checks. Differentiators should follow only after pipeline quality is stable.

**Must have (table stakes):**
- Deterministic ingestion with source IDs/checksums and rerunnable artifact generation.
- Word-timestamped transcription and robust speech-window to chat-window alignment.
- Canonical conversation schema plus dataset QA/filtering with confidence fields.
- Reproducible training/evaluation runs tied to data versions and config seeds.
- Local inference/sample harness for quick qualitative verification.

**Should have (competitive):**
- Human-in-the-loop correction for ambiguous high-impact alignment cases.
- Persona/style balancing controls to avoid overfitting to spammy chat modes.
- Data lineage traceability per training sample for fast debugging.

**Defer (v2+):**
- Learned alignment confidence/ranking model.
- Live Twitch ingestion and real-time processing.

### Architecture Approach

Architecture should be modular and contract-first: ingestion adapters, extraction workers, alignment engine, curation/QA gates, training orchestrator, and evaluation harness, all coordinated through DVC lineage and artifactized data tiers. The strongest pattern recommendation is medallion-style data flow with idempotent, content-addressed stages and explicit boundaries (`ingest -> extract -> align -> curate -> train -> evaluate`) so failures are debuggable, reruns are cheap, and model metrics are attributable to exact data snapshots.

**Major components:**
1. Ingestion and manifesting - acquire sources, compute checksums, and assign canonical IDs.
2. Extraction and normalization - deterministic media derivatives, ASR outputs, and chat event schema.
3. Alignment and scoring - candidate generation, confidence scoring, reject-reason capture.
4. Curation and QA gates - dedupe/filter/split/export with contract validation.
5. Training and evaluation - adapter tuning with run tracking and fixed regression suites.

### Critical Pitfalls

1. **Using ingest-time chat timestamps as truth** - enforce canonical source timestamps (`tmi-sent-ts`), message IDs, dedupe, and reorder windows.
2. **Treating Whisper segment timestamps as precise boundaries** - require word-level forced alignment, VAD-aware segmentation, and confidence-based rejection.
3. **Skipping transcript normalization for aligners** - normalize numbers/symbols/punctuation and monitor unaligned-token rates.
4. **Using static lag windows without calibration** - estimate lag distributions per stream context and apply adaptive windows with confidence scoring.
5. **Mismatching chat templates/loss masking in SFT** - lock one dataset format, validate rendered samples, and enforce assistant/completion-only loss settings.

## Implications for Roadmap

Based on dependencies, risk, and architecture boundaries, the safest roadmap is five phases.

### Phase 1: Foundation and Deterministic Ingestion
**Rationale:** Every downstream quality decision depends on trustworthy IDs, timestamps, and immutable inputs.
**Delivers:** Contracts, directory conventions, manifests/checksums, ingestion adapters, raw/staged skeleton.
**Addresses:** Deterministic ingestion, canonical schema prerequisites, provenance lineage.
**Avoids:** Ingest-time timestamp drift and shared-chat provenance loss.

### Phase 2: Transcript and Chat Extraction Quality
**Rationale:** Alignment quality is impossible without high-fidelity speech/chat timelines.
**Delivers:** FFmpeg media derivation, WhisperX word timestamps, chat normalization (direct export first, OCR fallback), transcript normalization and confidence columns.
**Uses:** FFmpeg, WhisperX/faster-whisper, PaddleOCR/OpenCV, DuckDB/Polars.
**Implements:** Extraction workers and normalized staged contracts.
**Avoids:** Coarse ASR timing errors, unaligned token holes, overlap/noise contamination.

### Phase 3: Alignment Engine and Curation Gates
**Rationale:** Pair-quality risk is the highest leverage risk before training.
**Delivers:** Candidate-window generation, adaptive lag-calibrated scoring, reject reasons, dedupe/filter/split, curated dataset exports.
**Addresses:** Alignment pipeline, dataset QA/filtering, lineage traceability.
**Avoids:** Static-window overfitting and silent bad-pair propagation into training.

### Phase 4: Reproducible Fine-Tuning and Eval Baseline
**Rationale:** Model iteration is only meaningful once curated data quality is measurable.
**Delivers:** QLoRA-first adapter training presets, run metadata binding (data version/config), fixed holdout eval suite, local inference harness.
**Uses:** Transformers, PEFT, TRL, bitsandbytes/Unsloth, MLflow.
**Implements:** Training orchestrator and regression harness.
**Avoids:** Template/loss mismatch and unsupported quantized full-finetune assumptions.

### Phase 5: Targeted Quality Amplifiers (v1.x)
**Rationale:** Add complexity only where measured failure clusters remain.
**Delivers:** Human review loop for ambiguous pairs, persona/style balancing controls, improved sampling policy.
**Addresses:** Differentiators that improve consistency and precision.
**Avoids:** Overbuilding v2 features before core ROI is validated.

### Phase Ordering Rationale

- Ordering follows hard dependencies: ingestion/timestamps -> extraction fidelity -> alignment/QA -> training/eval.
- Grouping mirrors architecture seams, which reduces coupling and makes each phase testable in isolation.
- Sequence explicitly front-loads the pitfalls with highest blast radius (timestamp/provenance/alignment) before expensive model runs.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2:** OCR fallback tuning for Twitch-style overlays is environment-dependent (theme, compression, motion).
- **Phase 3:** Adaptive lag calibration and confidence scoring thresholds need empirical validation strategy.
- **Phase 4:** VRAM envelope and quantization/training compatibility checks vary by local hardware profile.

Phases with standard patterns (skip research-phase):
- **Phase 1:** deterministic ingestion/manifests/schema contracts are well-established.
- **Phase 5:** human review workflow and stratified balancing are iterative product tuning, not architecture unknowns.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Strong official-doc coverage and clear ecosystem convergence around local QLoRA and FFmpeg/WhisperX pipeline patterns. |
| Features | MEDIUM | Solid prioritization, but differentiator impact and review-UI scope require project-specific validation. |
| Architecture | MEDIUM-HIGH | Patterns are mature and coherent, with minor uncertainty in scale breakpoints and tooling overhead trade-offs. |
| Pitfalls | MEDIUM-HIGH | Risks are concrete and evidence-backed, but some prevention thresholds (lag, purity, confidence cutoffs) remain empirical. |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **OCR viability envelope:** Define objective acceptance criteria by video quality class; run a representative benchmark set before committing heavily to OCR-first workloads.
- **Alignment threshold policy:** Establish labeled validation slices early to tune lag windows, score thresholds, and reject/accept cut lines.
- **Evaluation rubric calibration:** Convert "Doug-style" goals into explicit metrics/rubric items so style quality can regress-test reliably.
- **Hardware profile matrix:** Document minimum/target GPU/CPU tiers and map them to training presets and runtime expectations.

## Sources

### Primary (HIGH confidence)
- https://ffmpeg.org/download.html - FFmpeg release and platform baseline
- https://huggingface.co/docs/trl/en/sft_trainer - SFT format, loss masking, and training expectations
- https://huggingface.co/docs/transformers/en/chat_templating - chat formatting and EOS/template correctness
- https://huggingface.co/docs/transformers/quantization/bitsandbytes - quantized training constraints and compatibility
- https://huggingface.co/docs/peft/en/developer_guides/lora - adapter training strategy
- https://huggingface.co/docs/datasets/en/about_dataset_features - dataset schema contract guidance
- https://dvc.org/doc/start - reproducible data/model versioning patterns
- https://dvc.org/doc/start/data-pipelines/data-pipelines - pipeline DAG/lockfile orchestration
- https://duckdb.org/docs/stable/data/parquet/overview - local analytics/query model over artifacts
- https://dev.twitch.tv/docs/chat/irc/ - canonical chat timestamp/provenance tags and delivery caveats

### Secondary (MEDIUM confidence)
- https://github.com/m-bain/whisperX - word-level alignment capabilities and caveats
- https://github.com/openai/whisper/blob/main/README.md - segment timestamp limitations context
- https://github.com/lay295/TwitchDownloader - chat export capabilities and automation options
- https://raw.githubusercontent.com/PaddlePaddle/PaddleOCR/main/README.md - OCR capabilities and migration notes
- https://github.com/pyannote/pyannote-audio - diarization pipeline considerations
- https://docs.unsloth.ai/ - local fine-tuning acceleration claims and workflows

### Tertiary (LOW confidence)
- None identified in current research set.

---
*Research completed: 2026-02-26*
*Ready for roadmap: yes*
