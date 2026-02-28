# dougpt Twitch Chat Model

## What This Is

dougpt Twitch Chat Model is a local data and model-training project that recreates DougDoug-style stream interactions by modeling Twitch chat responses to DougDoug's spoken prompts. The system ingests DougDoug videos, extracts and transcribes DougDoug's audio track, extracts Twitch chat logs from the same videos, and aligns both timelines into training-ready conversation data. The target user is DougDoug himself, with all processing designed to run locally without paid external services.

## Core Value

Create high-quality, locally generated DougDoug-speaker to Twitch-chat response pairs that are accurate enough to fine-tune a local language model.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Extract Twitch chat messages and timestamps from DougDoug videos.
- [ ] Extract DougDoug's speech timeline from stream audio with local transcription.
- [ ] Align speech segments to nearby chat responses into structured training examples.
- [ ] Provide local scripts and reproducible pipelines for ingestion, alignment, and dataset export.
- [ ] Fine-tune a local language model on the aligned dataset and run local inference.

### Out of Scope

- Real-time live-stream integration with Twitch APIs — this project focuses on offline video-derived datasets first.
- Paid third-party APIs or hosted training services — must run locally with free/open tooling.
- Production deployment infrastructure — initial milestone is local research and model iteration.

## Context

The project is greenfield for planning artifacts but targets an existing code repository. The domain is multimodal-ish stream processing, where one timeline comes from DougDoug audio/transcript data and one timeline comes from Twitch chat extraction. The main technical risk is timestamp quality and alignment heuristics, because model quality depends heavily on precise conversational pairing.

## Constraints

- **Budget**: Zero recurring API cost — all extraction, transcription, alignment, and training must use local/free tools.
- **Tech stack**: Python-first local scripts and model tooling — avoids dependence on cloud services.
- **Data quality**: Timestamp fidelity is required — poor alignment will degrade fine-tuning outcomes.
- **User fit**: Designed for DougDoug persona interactions — prompt/response format must reflect stream dynamics.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Prioritize offline pipeline from existing videos | Fastest path to collect paired supervision data | — Pending |
| Use local-only tooling for extraction/transcription/training | Avoids paid services and keeps workflow reproducible | — Pending |
| Model DougDoug speech as input and Twitch chat as response | Matches intended interaction loop of the final AI | — Pending |

---
*Last updated: 2026-02-26 after initialization*
