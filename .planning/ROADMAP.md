# Roadmap: Audio Extraction Review Workflow

## Overview

Build a notebook-first local workflow for audio extraction review. Phase 1 prepared the reusable template baseline. Phase 2 delivers a dedicated `audio-extraction-review` worktree pipeline for video audio extraction, local Whisper transcription, and local LLM segmentation into chat-style chunks.

## Phases

**Phase Numbering:**
- Integer phases (1, 2): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Template Preparation** - README template with placeholder variables on `00-experiments`
- [x] **Phase 2: Audio Extraction Review Pipeline** - Notebook flow on dedicated worktree for extraction, local transcription, and chat-style segment generation

## Phase Details

### Phase 1: Template Preparation
**Goal**: A proper README template exists on `00-experiments` so every new branch inherits a structured, populatable starting point
**Depends on**: Nothing (first phase)
**Requirements**: TMPL-01, TMPL-02
**Success Criteria** (what must be TRUE):
  1. `README.md` exists on the `00-experiments` branch with `$placeholder` variables (e.g., `$project_name`, `$description`)
  2. Template includes all required sections: project name, description, what it does, how to run, status
  3. Template contains a sentinel comment (e.g., `<!-- TEMPLATE: REPLACE ME -->`) that downstream tooling can detect to distinguish template vs populated README
**Plans:** 1 plan

Plans:
- [x] 01-01-PLAN.md — Create README template with $placeholder variables on 00-experiments

### Phase 2: Audio Extraction Review Pipeline
**Goal**: A user can run a local notebook on a dedicated `audio-extraction-review` worktree (separate from `chat-extraction`) to extract audio from video, transcribe with local Whisper, and segment transcript into chat-style output using a local LLM
**Depends on**: Phase 1 (template baseline)
**Requirements**: CHAT-01, CHAT-02, CHAT-03
**Success Criteria** (what must be TRUE):
  1. Notebook accepts a video input path and produces an extracted audio artifact usable for transcription
  2. Notebook runs a local Whisper model and outputs a transcript file with stable, reusable structure
  3. Notebook runs a local LLM pass that converts transcript into segment blocks aligned with the style used in `00-dev-log/2026-02-09.md`
  4. The full notebook flow runs locally end-to-end without requiring hosted APIs
**Plans**: 2 plans

Plans:
- [x] 02-01-PLAN.md — Build deterministic notebook extraction and transcription stages with reusable checkpoints
- [x] 02-02-PLAN.md — Add local LLM segmentation, dual-format export, and end-to-end notebook orchestration

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Template Preparation | 1/1 | Complete | 2026-02-13 |
| 2. Audio Extraction Review Pipeline | 2/2 | Complete | 2026-02-22 |
