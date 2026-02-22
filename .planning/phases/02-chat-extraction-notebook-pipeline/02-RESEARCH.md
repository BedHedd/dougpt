# Phase 2: Chat Extraction Notebook Pipeline - Research

**Researched:** 2026-02-21
**Domain:** Local notebook audio extraction + ASR + diarization + LLM segmentation
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

### Media input and extraction
- Support both single-file and batch processing modes.
- Canonical current input example is `large-files/Doug and Twitch Chat TAKE OVER EUROPE-VpmmuHlLPM0.mkv`.
- Resolve project-relative paths using the existing project-root anchor pattern based on locating `00-supporting-files`.
- Accept any input format that ffmpeg can decode.
- Extract to a storage/quality-balanced audio format (exact codec/container is implementation discretion, but should avoid unnecessarily large outputs).
- On extraction failure in batch mode, skip the file, log the failure, and continue.

### Transcript policy
- Transcript output should be mostly verbatim.
- Include both segment-level timestamps and word-level timestamps when available.
- Use local speaker diarization when feasible.
- Whisper model is configurable in the notebook, with quality-first defaults.

### Segment output schema
- Segment boundaries should be hybrid: semantic/topic-aware, but constrained by time windows.
- Generate both Markdown and JSON outputs in the same run.
- Required fields per segment: `id`, `start_time`, `end_time`, `speaker`, `summary`.
- Keep chronological ordering with slight overlap between adjacent segments.

### Notebook review and export workflow
- Default human review target is the final segmented output.
- Keep optional intermediate checkpoints available for extraction/transcript review when needed.
- Support editing both in-notebook and in generated files (`.md`/`.json`) with reload-friendly flow.
- Export proceeds automatically (no explicit approval gate).
- Record detailed run metadata (model names, parameters, durations, and similar execution context).
- Use path handling consistent with existing `00-supporting-files/data`-style project-relative workflows.

### Claude's Discretion
- Exact extracted audio codec/container and ffmpeg parameter values, as long as they meet the storage/quality balance requirement.
- Concrete diarization package/tooling choice and fallback behavior when diarization quality is poor.
- Exact overlap size and additional optional segment metadata beyond required fields.
- UI/layout details of notebook cells and helper functions.

### Deferred Ideas (OUT OF SCOPE)
- Integrate chat messages directly into transcript segmentation/alignment. This is out of scope for this phase and should be handled in a future dedicated phase.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| CHAT-01 | Notebook can extract audio from a local video file into a transcription-ready audio file | Use ffmpeg-based extraction stage with single+batch mode, resilient failure logging, and deterministic output audio settings |
| CHAT-02 | Notebook runs a local Whisper model and saves transcript output in a reusable file format | Use faster-whisper/WhisperX local transcription with segment and word timestamps, optional diarization, and saved JSON checkpoint |
| CHAT-03 | Notebook runs a local LLM pass that segments transcript content into chat-style blocks aligned with `00-dev-log/2026-02-09.md` | Use local OpenAI-compatible endpoint (LM Studio) + JSON schema constrained output, then render both JSON and Markdown from same segment objects |
</phase_requirements>

## Summary

This phase should be planned as a deterministic, checkpointed notebook pipeline with four explicit stages: input discovery/path resolution, audio extraction, transcription+diarization, and segmentation rendering. The current repo already uses a path-anchor pattern (`00-supporting-files`) and local OpenAI-compatible clients in notebooks, so the phase should extend those patterns rather than introducing a new app architecture.

For ASR, the most practical local stack is `faster-whisper` (speed, low memory options, word timestamps) with optional WhisperX/pyannote integration for improved word alignment and speaker labels. For segmentation, use local LLM inference through LM Studio OpenAI-compatible endpoints with JSON schema constraints so output is machine-safe first, then render Markdown and JSON from the same normalized segment objects.

The largest planning risk is not model quality but pipeline reliability and artifact design: partial failures in batch mode, non-resumable runs, and malformed intermediate files create rework. Plan for idempotent checkpoint files and run metadata as first-class outputs.

**Primary recommendation:** Plan a staged notebook with strict intermediate artifacts (`audio -> transcript.json -> segments.json -> segments.md`) and schema validation at each stage.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| ffmpeg (CLI) | system tool | Decode broad video formats and extract audio tracks | De-facto media decode/transform tool; Whisper ecosystem expects ffmpeg-compatible media workflows |
| faster-whisper | 1.2.1 | Local Whisper transcription with segment+word timing support | Faster and lower-memory Whisper inference, supports word timestamps and VAD filtering |
| openai (Python SDK) + LM Studio OpenAI-compatible server | openai 1.93.0 + LM Studio local server | Local LLM segmentation pass via OpenAI-style API | Reuses current repo pattern (`base_url=http://localhost:1234/v1`) and supports JSON schema response format |
| marimo / Jupyter notebook runtime | marimo 0.20.1 + ipykernel 6.29.5 | Interactive, local-first notebook execution and review | Already present in worktree and consistent with current development workflow |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| whisperx | 3.8.1 | Forced alignment + diarization workflow around Whisper | Use when better word timing and speaker assignment is needed than baseline Whisper timestamps |
| pyannote.audio | 4.0.4 | Local speaker diarization pipeline | Use when diarization quality is acceptable and HF token/model access is configured |
| pydantic | (via openai sdk deps) | Validate transcript/segment schemas | Use for hard validation before writing JSON/Markdown outputs |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| faster-whisper | openai-whisper | Simpler canonical implementation but usually slower and heavier for local iterative notebook runs |
| pyannote/WhisperX diarization | no diarization | Lower setup complexity but loses speaker labels required by desired segment schema quality |
| JSON-schema constrained LLM output | freeform prompting | Faster to prototype but less reliable and higher post-processing/retry complexity |

**Installation:**
```bash
uv add faster-whisper whisperx pyannote.audio
```

## Architecture Patterns

### Recommended Project Structure
```
00-supporting-files/
└── data/
    └── chat-extraction/
        ├── audio/                # extracted transcription-ready audio
        ├── transcripts/          # whisper/whisperx reusable JSON outputs
        ├── segments/             # final segments.json + segments.md
        ├── runs/                 # per-run metadata, timings, config snapshots
        └── logs/                 # batch failures and retry events
```

### Pattern 1: Stage-gated notebook pipeline
**What:** Each stage writes a durable artifact and only consumes prior stage output.
**When to use:** Always, especially for batch runs and iterative review.
**Example:**
```python
# Source: local project pattern in 02-worktrees/chat-extraction/chat-extraction.py
from pathlib import Path

start = Path.cwd()
supporting_files = next(p / "00-supporting-files" for p in (start, *start.parents) if (p / "00-supporting-files").exists())
base_dir = supporting_files / "data" / "chat-extraction"
audio_dir = base_dir / "audio"
transcript_dir = base_dir / "transcripts"
segments_dir = base_dir / "segments"
```

### Pattern 2: Deterministic extraction command
**What:** Normalize audio to ASR-friendly mono sample rate and stable codec/container.
**When to use:** Every input file before ASR.
**Example:**
```bash
# Source: ffmpeg CLI options + Whisper ecosystem usage
ffmpeg -v error -y -i "input.mkv" -vn -ac 1 -ar 16000 -c:a flac "output.flac"
```

### Pattern 3: Structured segment generation via local OpenAI-compatible API
**What:** Request strict JSON schema from local LLM endpoint, then parse/validate.
**When to use:** Segment synthesis stage.
**Example:**
```python
# Source: https://lmstudio.ai/docs/developer/openai-compat/structured-output
from openai import OpenAI
import json

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
resp = client.chat.completions.create(
    model="local-model",
    messages=[{"role": "user", "content": "Segment transcript..."}],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "chat_segments",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {"segments": {"type": "array"}},
                "required": ["segments"],
                "additionalProperties": False,
            },
        },
    },
)
segments = json.loads(resp.choices[0].message.content)
```

### Anti-Patterns to Avoid
- **Single giant in-memory pass:** risks losing all work on failure; persist per-stage artifacts.
- **Freeform LLM text output for final artifacts:** causes brittle parsing and schema drift.
- **Ambiguous pseudo-JSONL outputs:** existing repo has prior pain from inconsistent JSONL shape; use true JSON array or true NDJSON, not mixed format.
- **No batch continuation strategy:** locked decision requires skip+log+continue on extraction failures.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Speaker diarization | Custom clustering over embeddings | `pyannote.audio` / WhisperX diarization | Diarization quality edge cases are hard; established pipelines already handle segmentation+speaker assignment workflows |
| Word-level alignment | Heuristic token-to-time interpolation | WhisperX alignment or faster-whisper word timestamps | Forced alignment and timing are non-trivial and already solved by dedicated tooling |
| Structured output parsing | Regex extraction from LLM text | JSON schema response_format + Pydantic validation | Prevents invalid/partial JSON and reduces retry complexity |
| Media decode compatibility | Per-extension custom decoders | ffmpeg decoding | ffmpeg already handles wide codec/container matrix reliably |

**Key insight:** In this phase, reliability comes from standard tooling plus strict artifacts, not from custom algorithms.

## Common Pitfalls

### Pitfall 1: Transcript artifacts are not truly reusable
**What goes wrong:** Only final prose output is saved; reruns require full re-transcription.
**Why it happens:** No dedicated transcript checkpoint schema.
**How to avoid:** Persist normalized transcript JSON with segments, words, optional speakers, model+params metadata.
**Warning signs:** Need to rerun ASR for tiny segmentation prompt changes.

### Pitfall 2: Batch mode silently drops failures
**What goes wrong:** Some files never make it to output but run appears successful.
**Why it happens:** Errors printed to cell output but not written as machine-readable log.
**How to avoid:** Always append failure record `{input, stage, error, traceback, ts}` and continue.
**Warning signs:** Output count mismatch between discovered input files and transcript artifacts.

### Pitfall 3: Diarization over-promised quality
**What goes wrong:** Speaker labels are unstable or wrong in noisy/overlapping speech.
**Why it happens:** Diarization is hard; docs explicitly note limitations.
**How to avoid:** Treat diarization as best-effort, keep fallback speaker `UNKNOWN`, and log quality flags.
**Warning signs:** Frequent speaker switching within short contiguous speech spans.

### Pitfall 4: LLM segmentation drift from style target
**What goes wrong:** Segments become generic summaries, not chat-style blocks aligned to `00-dev-log/2026-02-09.md`.
**Why it happens:** Prompt lacks explicit style constraints and overlap/chronology checks.
**How to avoid:** Feed explicit style examples, enforce schema, and post-validate chronology + overlap + required fields.
**Warning signs:** Missing `speaker`/time fields, non-chronological IDs, no overlap between adjacent segments.

## Code Examples

Verified patterns from official sources:

### Local transcription with word timestamps (faster-whisper)
```python
# Source: https://github.com/SYSTRAN/faster-whisper
from faster_whisper import WhisperModel

model = WhisperModel("large-v3", device="cuda", compute_type="float16")
segments, info = model.transcribe("audio.flac", word_timestamps=True, vad_filter=True)

for segment in segments:
    for word in (segment.words or []):
        print(word.start, word.end, word.word)
```

### WhisperX diarization assignment
```python
# Source: https://github.com/m-bain/whisperX
import whisperx
from whisperx.diarize import DiarizationPipeline

audio = whisperx.load_audio("audio.flac")
model = whisperx.load_model("large-v2", "cuda", compute_type="float16")
result = model.transcribe(audio, batch_size=16)

align_model, metadata = whisperx.load_align_model(language_code=result["language"], device="cuda")
result = whisperx.align(result["segments"], align_model, metadata, audio, "cuda")

diarize = DiarizationPipeline(token="HUGGINGFACE_ACCESS_TOKEN", device="cuda")
speakers = diarize(audio)
result = whisperx.assign_word_speakers(speakers, result)
```

### Local structured segmentation request
```python
# Source: https://lmstudio.ai/docs/developer/openai-compat/structured-output
from openai import OpenAI

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
completion = client.chat.completions.create(
    model="your-local-model",
    messages=[{"role": "user", "content": "Segment transcript"}],
    response_format={"type": "json_schema", "json_schema": {"name": "segments", "strict": True, "schema": {"type": "object"}}},
)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| openai-whisper-only timestamps | faster-whisper + optional WhisperX alignment/diarization | WhisperX v3 era and recent faster-whisper releases | Better throughput, optional improved word timing and speaker labeling |
| Freeform LLM output text | JSON-schema constrained output (`response_format`) | Structured output support in modern OpenAI-compatible endpoints | Lower parsing failures and simpler downstream validation |
| Monolithic notebook runs | Stage-gated artifact checkpoints | Current best practice for local long-form media pipelines | Faster iteration, resumability, easier debugging |

**Deprecated/outdated:**
- Assuming diarization is always reliable: WhisperX and pyannote docs both call out limitations.
- Treating `.jsonl` as arbitrary pretty JSON: use strict NDJSON or `.json` arrays only.

## Open Questions

1. **Diarization token dependency acceptance**
   - What we know: pyannote/WhisperX diarization workflows commonly require accepting model terms and using HF token.
   - What's unclear: Whether phase plan should require this setup or default to non-diarized fallback first.
   - Recommendation: Plan fallback path with `speaker="UNKNOWN"` when token/model unavailable.

2. **Default audio extraction format final choice**
   - What we know: Decision allows discretion; ffmpeg+Whisper tooling supports many formats.
   - What's unclear: Final default between FLAC (quality/size), WAV (max compatibility), Opus (smallest lossy).
   - Recommendation: Use FLAC mono 16k default; expose override cell for codec/container.

3. **Local segmentation model capability for strict schema**
   - What we know: LM Studio supports schema-constrained output, but not all small models comply reliably.
   - What's unclear: Which locally available model in this repo environment is most stable for required schema.
   - Recommendation: Add quick schema conformance smoke test cell before full batch segmentation.

## Sources

### Primary (HIGH confidence)
- https://github.com/openai/whisper - setup requirements, ffmpeg dependency, model options, Python API
- https://github.com/SYSTRAN/faster-whisper - word timestamps, VAD, performance/requirements, current release info
- https://github.com/m-bain/whisperX - alignment + diarization pipeline, limitations, current release info
- https://github.com/pyannote/pyannote-audio - local diarization pipeline usage, benchmark update, token requirements
- https://lmstudio.ai/docs/developer/openai-compat - local OpenAI-compatible endpoint support
- https://lmstudio.ai/docs/developer/openai-compat/structured-output - JSON schema structured output on local server

### Secondary (MEDIUM confidence)
- https://docs.marimo.io/ - notebook runtime and workflow capabilities
- Local repository context:
  - `02-worktrees/chat-extraction/chat-extraction.py`
  - `02-worktrees/chat-extraction/extraction-review.ipynb`
  - `02-worktrees/chat-extraction/pyproject.toml`
  - `02-worktrees/chat-extraction/uv.lock`

### Tertiary (LOW confidence)
- https://platform.openai.com/docs/guides/structured-outputs - cross-check for schema concepts; not directly authoritative for local LM Studio model behavior

## Metadata

**Confidence breakdown:**
- Standard stack: MEDIUM - tool capabilities are well documented, but local model/hardware constraints are environment-specific
- Architecture: HIGH - strongly grounded in existing repo patterns and proven notebook workflows
- Pitfalls: HIGH - corroborated by current repo artifacts and known upstream limitations

**Research date:** 2026-02-21
**Valid until:** 2026-03-23
