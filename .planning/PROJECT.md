# DougPT

## What This Is

DougPT is a pipeline and local LLM that ingests DougDoug stream recordings with their Twitch chat logs, aligns audio/video with chat messages, and fine-tunes a local model to respond like Twitch chat to DougDoug’s audio context. It targets creating realistic, time-synced chat-style responses for experimentation and offline playbacks.

## Core Value

A locally fine-tuned model that reliably produces authentic DougDoug Twitch chat-style responses from recent audio context.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Ingest DougDoug VODs and corresponding Twitch chat logs with timestamps.
- [ ] Transcribe stream audio and align it to chat message timing.
- [ ] Build a clean paired dataset (audio/context → chat response) suitable for fine-tuning.
- [ ] Fine-tune a local LLM to emulate DougDoug chat tone, memes, and pacing.
- [ ] Provide an inference interface that consumes audio (or transcript context) and returns chat-style replies.
- [ ] Evaluate quality with held-out segments and guardrails (toxicity, spam) before using outputs.

### Out of Scope

- Full production Twitch integration or live deployment — focus on offline/local usage first.
- Cloud-hosted proprietary LLM APIs — prioritize locally runnable models for cost/control.

## Context

- Goal: create a reproducible pipeline from raw DougDoug streams + chat to a fine-tuned, local chat-mimicking model.
- Existing codebase detected but unmapped; treat as greenfield for planning and build a map later if needed.
- Source data: Twitch VOD recordings (audio/video) and exported chat logs; transcripts will be derived via ASR.

## Constraints

- **Local-first**: Run models and training locally to avoid API cost and keep control over data.
- **Data licensing/usage**: Use publicly available DougDoug streams and chat under fair-use-like constraints; avoid redistributing copyrighted media.
- **Compute budget**: Target consumer-grade GPU setups; prefer parameter-efficient fine-tuning.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Local LLM over hosted API | Control cost, allow custom guardrails and offline use | — Pending |

---
*Last updated: 2026-02-21 after initialization*
