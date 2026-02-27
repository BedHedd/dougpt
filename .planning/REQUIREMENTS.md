# Requirements: DougGPT Twitch Chat Model

**Defined:** 2026-02-26
**Core Value:** Create high-quality, locally generated DougDoug-speaker to Twitch-chat response pairs that are accurate enough to fine-tune a local language model.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Ingestion

- [ ] **ING-01**: User can ingest one or more DougDoug video sources into a local raw dataset with stable source IDs.
- [ ] **ING-02**: User can extract Twitch chat logs with message IDs and source timestamps for each ingested video.
- [ ] **ING-03**: User can rerun ingestion idempotently and get deterministic outputs for unchanged inputs.

### Transcript Extraction

- [ ] **ASR-01**: User can extract DougDoug-only audio tracks from stream videos using local tooling.
- [ ] **ASR-02**: User can generate timestamped speech transcripts locally without paid APIs.
- [ ] **ASR-03**: User can export normalized transcript segments with confidence metadata for alignment.

### Alignment and Curation

- [ ] **ALG-01**: User can align DougDoug speech windows to candidate Twitch chat response windows using reproducible rules.
- [ ] **ALG-02**: User can score alignment confidence and reject low-quality pairs.
- [ ] **ALG-03**: User can export curated prompt/response training samples in a canonical schema with provenance fields.
- [ ] **ALG-04**: User can run dataset QA filters to remove duplicate, empty, or malformed records before training.

### Training and Evaluation

- [ ] **TRN-01**: User can fine-tune a local language model adapter on curated data using reproducible configuration.
- [ ] **TRN-02**: User can run baseline evaluation on held-out samples before and after fine-tuning.
- [ ] **TRN-03**: User can run local inference with the fine-tuned model to inspect DougDoug-prompt to chat-response behavior.

### Pipeline Operations

- [ ] **OPS-01**: User can execute the full pipeline through local scripts/commands without paid external services.
- [ ] **OPS-02**: User can track dataset version, training config, and output artifact paths for each run.

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Quality Amplifiers

- **QLT-01**: User can correct ambiguous alignment samples through a lightweight human-review workflow.
- **QLT-02**: User can apply persona/style balancing controls to reduce overfitting to spam-heavy chat patterns.
- **QLT-03**: User can use a learned alignment confidence model to rank candidate chat responses.

### Expansion

- **EXP-01**: User can ingest live Twitch chat streams in real time.
- **EXP-02**: User can support production deployment workflows for serving the model.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Paid API-based transcription or training services | Conflicts with local-only and zero recurring-cost constraint |
| End-to-end real-time livestream agent in v1 | Adds infrastructure complexity before offline data quality is proven |
| Training a foundation model from scratch locally | Not required for v1 objective and unrealistic for available local resources |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| ING-01 | Phase 1 | Pending |
| ING-02 | Phase 1 | Pending |
| ING-03 | Phase 1 | Pending |
| ASR-01 | Phase 2 | Pending |
| ASR-02 | Phase 2 | Pending |
| ASR-03 | Phase 2 | Pending |
| ALG-01 | Phase 3 | Pending |
| ALG-02 | Phase 3 | Pending |
| ALG-03 | Phase 3 | Pending |
| ALG-04 | Phase 3 | Pending |
| TRN-01 | Phase 4 | Pending |
| TRN-02 | Phase 4 | Pending |
| TRN-03 | Phase 4 | Pending |
| OPS-01 | Phase 4 | Pending |
| OPS-02 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 15 total
- Mapped to phases: 15
- Unmapped: 0

---
*Requirements defined: 2026-02-26*
*Last updated: 2026-02-26 after roadmap mapping*
