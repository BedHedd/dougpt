# Roadmap: DougGPT Twitch Chat Model

## Overview

This roadmap delivers a local-first pipeline that turns DougDoug videos into trustworthy DougDoug-prompt to Twitch-chat response training pairs, then proves model improvement through reproducible local fine-tuning and evaluation. Phase order follows hard data dependencies: deterministic ingestion first, then transcript quality, then alignment and curation, then end-to-end training operations.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Deterministic Video Ingestion** - Build stable local source manifests and repeatable chat extraction inputs.
- [ ] **Phase 2: Local Speech Transcript Extraction** - Produce DougDoug-only, timestamped, normalized transcript data for alignment.
- [ ] **Phase 3: Alignment and Dataset Curation** - Convert timelines into confidence-scored, QA-filtered training samples.
- [ ] **Phase 4: Reproducible Training and End-to-End Ops** - Fine-tune locally, evaluate quality deltas, and run full pipeline with tracked artifacts.

## Phase Details

### Phase 1: Deterministic Video Ingestion
**Goal**: Users can ingest DougDoug video sources into stable, reproducible local datasets with trustworthy source and chat provenance.
**Depends on**: Nothing (first phase)
**Requirements**: ING-01, ING-02, ING-03
**Success Criteria** (what must be TRUE):
  1. User can ingest one or more videos and get stable source IDs for each source.
  2. User can extract Twitch chat logs tied to source timestamps and message IDs for each ingested video.
  3. User can rerun ingestion for unchanged inputs and receive deterministic outputs without duplicate records.
**Plans**: TBD

### Phase 2: Local Speech Transcript Extraction
**Goal**: Users can generate high-fidelity, local-only DougDoug speech timelines ready for downstream pairing.
**Depends on**: Phase 1
**Requirements**: ASR-01, ASR-02, ASR-03
**Success Criteria** (what must be TRUE):
  1. User can extract a DougDoug-only audio track from each ingested stream video using local tooling.
  2. User can generate timestamped speech transcripts locally with no paid API dependency.
  3. User can export normalized transcript segments that include confidence metadata for alignment decisions.
**Plans**: TBD

### Phase 3: Alignment and Dataset Curation
**Goal**: Users can produce canonical, quality-filtered DougDoug prompt to Twitch chat response training datasets from aligned timelines.
**Depends on**: Phase 2
**Requirements**: ALG-01, ALG-02, ALG-03, ALG-04
**Success Criteria** (what must be TRUE):
  1. User can align speech windows to candidate chat response windows using reproducible rules.
  2. User can score alignment confidence and exclude low-quality pairings before export.
  3. User can export curated prompt/response samples in a canonical schema with provenance fields.
  4. User can run QA filters that remove duplicate, empty, or malformed records before training.
**Plans**: TBD

### Phase 4: Reproducible Training and End-to-End Ops
**Goal**: Users can run the full local pipeline from ingestion through inference, with reproducible training, evaluation, and artifact tracking.
**Depends on**: Phase 3
**Requirements**: TRN-01, TRN-02, TRN-03, OPS-01, OPS-02
**Success Criteria** (what must be TRUE):
  1. User can execute the full local pipeline through scripts/commands without paid external services.
  2. User can fine-tune a local adapter model on curated data using reproducible configuration.
  3. User can run baseline held-out evaluation before and after fine-tuning and inspect the quality delta.
  4. User can run local inference with the fine-tuned model to inspect DougDoug-prompt to chat-response behavior.
  5. User can trace each run to dataset version, training config, and output artifact paths.
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Deterministic Video Ingestion | 0/TBD | Not started | - |
| 2. Local Speech Transcript Extraction | 0/TBD | Not started | - |
| 3. Alignment and Dataset Curation | 0/TBD | Not started | - |
| 4. Reproducible Training and End-to-End Ops | 0/TBD | Not started | - |
