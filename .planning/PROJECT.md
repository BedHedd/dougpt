# DougPT

## What This Is

DougPT is a small project to build a chat-style AI model that behaves like Twitch chat from DougDoug streams.
It focuses on extracting/cleaning chat messages from DougDoug stream recordings (or associated chat logs) and fine-tuning a ChatGPT-family model so it can generate “stream chat-like” responses on demand.

## Core Value

Given an input prompt, the system can generate safe, coherent, Twitch-chat-style output that feels like DougDoug stream chat.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Extract and normalize DougDoug Twitch chat messages into a training dataset
- [ ] Fine-tune a ChatGPT-family model on the dataset and run basic eval/sanity checks
- [ ] Provide a simple way to run inference (CLI or small app) to test the tuned model

### Out of Scope

- Live Twitch bot integration — not needed to validate the model and dataset pipeline
- Audio/voice modeling — focus is text chat only

## Context

- Training data is Twitch chat from DougDoug streams; source material may be VOD chat logs or chat reconstructed from stream recordings.
- Data quality matters (spam, emotes, copypasta, duplicates, timestamps, user ids) and will drive model behavior.
- Compliance and safety matter (Twitch terms, privacy, disallowed content). Assume we need filtering and clear provenance.

## Constraints

- **Model**: Use ChatGPT-family models / OpenAI-compatible fine-tuning path — aligns with the intended deployment target.
- **Safety**: Include dataset filtering and output guardrails appropriate for public chat-style text.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Fine-tune a ChatGPT-family model | User explicitly wants “chatgpt models” | — Pending |
| Train primarily on DougDoug stream chat | Keeps the style target narrow and testable | — Pending |

---
*Last updated: 2026-02-22 after initialization*
