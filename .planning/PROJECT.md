# DougPT

## What This Is

DougPT is an AI dataset and pipeline project built around DougDoug stream videos, where DougDoug's extracted audio/transcript acts as the user side and aligned Twitch chat messages act as the responder side. The project focuses on repeatable scripts for video ingest, audio extraction, chat extraction, transcript generation, and timestamp alignment. It is for building a high-quality paired interaction dataset that can later power training and evaluation.

## Core Value

Produce reliable, timestamp-aligned DougDoug speech and Twitch chat pairs from stream videos so downstream model work has clean, trustworthy data.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

(None yet — ship to validate)

### Active

<!-- Current scope. Building toward these. -->

- [ ] Extract DougDoug audio tracks from source stream videos with reproducible scripts.
- [ ] Extract Twitch chat logs from the same videos with precise timestamps.
- [ ] Generate or ingest transcripts for DougDoug audio with normalized timing metadata.
- [ ] Align transcript segments to Twitch chat windows into machine-readable training pairs.
- [ ] Export aligned datasets and run quality checks for coverage, drift, and timestamp consistency.

### Out of Scope

<!-- Explicit boundaries. Includes reasoning to prevent re-adding. -->

- Building a production chat UI/app for end users — current milestone is data pipeline and alignment foundations.
- Full model training, serving, and RLHF loops — deferred until dataset quality is validated.

## Context

- Existing repository already contains stream/audio transcription-oriented assets and worktrees; this initiative consolidates and formalizes that effort into a structured project plan.
- The primary data source is DougDoug stream video content and corresponding Twitch chat, with temporal alignment as the core technical challenge.
- Success depends on deterministic processing scripts, robust metadata schemas, and explicit quality gates for alignment confidence.
- The immediate need is to define v1 scope and roadmap so execution can proceed phase-by-phase with verifiable outputs.

## Constraints

- **Data Source**: Must use available DougDoug video/chat artifacts — scope is constrained by what can be legally and technically extracted.
- **Reliability**: Alignment outputs must be reproducible — non-deterministic pipelines undermine model training quality.
- **Compatibility**: Scripts should run in the existing repository environment and toolchain — avoids introducing incompatible infrastructure early.
- **Performance**: Processing should scale to long stream videos and large chat volumes — one-off/manual workflows are insufficient.
- **Security**: No secret leakage in artifacts/logs — planning and generated docs must remain safe for version control.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Prioritize extraction + alignment scripts before model training | Data quality is the bottleneck; model work without aligned pairs is premature | — Pending |
| Treat DougDoug transcript as user channel and Twitch chat as responder channel | Matches intended simulation target and keeps labeling consistent | — Pending |
| Use auto workflow with research and roadmap generation enabled | Faster initialization while still producing structured planning artifacts | — Pending |

---
*Last updated: 2026-02-26 after initialization*
