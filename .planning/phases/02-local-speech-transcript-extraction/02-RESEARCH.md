# Phase 02: Local Speech Transcript Extraction - Research

**Researched:** 2026-02-28
**Domain:** Local ASR, diarization, vocal isolation for DougDoug streams
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
#### Transcript granularity & normalization
- Segment by natural phrases/sentences, keep per-word timestamps inside each segment; target segment length ~8–12 seconds.
- Normalize text to sentence case with punctuation; retain fillers as spoken but tag non-speech sounds inline (e.g., [laughter]/[music]/[noise]).

#### Voice isolation policy
- Start from demuxed audio; run vocal isolation only when music/overlap is detected.
- Tag non-Doug segments instead of dropping; include speaker labels for later filtering.
- Apply light music/SFX reduction only when present; flag low-quality/separation-poor segments for review instead of auto-dropping.

#### Confidence metadata & filtering
- Store per-word and per-segment confidence scores; include ASR logprobs plus VAD/overlap flags.
- Default export only for segments with confidence >= 0.70.
- If a segment contains low-confidence spans, keep the segment but flag the questionable words/spans.

#### Export format & storage
- Export as JSONL (one segment per line).
- Store under `00-supporting-files/data/transcripts/{source_id}/`.
- Each record should include raw and normalized text, start/end timestamps, speaker label, per-word and per-segment confidences, logprobs/VAD/overlap flags, and quality flags.
- Keep raw and normalized versions side-by-side for traceability.

### Claude's Discretion
- Exact field names/schema shape within the JSONL records.
- How to score/flag low-quality separation and VAD/overlap heuristics.
- When to trigger optional vocal isolation based on detected music/overlap.

### Deferred Ideas (OUT OF SCOPE)
- None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| ASR-01 | User can extract DougDoug-only audio tracks from stream videos using local tooling. | Pipeline covers demux + conditional vocal isolation (Demucs/UVR5) with quality flags; reuse path discovery helpers for locating demuxed audio. |
| ASR-02 | User can generate timestamped speech transcripts locally without paid APIs. | Recommend faster-whisper/whisperX on ROCm GPU with word timestamps + VAD-based segmentation; local models only. |
| ASR-03 | User can export normalized transcript segments with confidence metadata for alignment. | JSONL schema guidance with per-word logprobs/confidence aggregation, normalization rules, and storage path `00-supporting-files/data/transcripts/{source_id}/`. |
</phase_requirements>

## Summary

Local-only ASR should center on faster-whisper (CTranslate2 backend) for speed and stability, layered with whisperX alignment/diarization to get reliable word timestamps and speaker tags. Demux audio from the ingested videos, probe for music/overlap, and only then run light source separation (Demucs/UVR5) to preserve DougDoug voice quality while flagging questionable separation instead of dropping audio. Silero VAD (bundled in faster-whisper) should gate speech regions and detect overlap/music cues that drive the isolation heuristic.

Confidence metadata must be preserved: per-word logprobs from faster-whisper, aggregated per-segment confidence, and VAD/overlap flags rolled into the JSONL export. Normalize text with punctuation, keep fillers, and inline non-speech tags. Store raw + normalized side-by-side under `00-supporting-files/data/transcripts/{source_id}/` with deterministic filenames to mirror existing data artifacts.

**Primary recommendation:** Build a batchable ASR runner that (1) demuxes audio, (2) applies VAD + optional vocal separation, (3) runs faster-whisper with word timestamps + whisperX alignment/diarization, (4) computes confidence/quality flags, and (5) emits JSONL segments in the established data directory.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| faster-whisper | 1.2.x | Whisper inference via CTranslate2 with word timestamps, VAD, quantization | Fast, GPU-friendly, supports word-level confidences and built-in Silero VAD; release 1.2.1 (2025-10-31) is current |
| whisperX | 3.8.x | Forced alignment + diarization + batched Whisper backend | Adds accurate word alignment and speaker labels; current release v3.8.1 (2026-02-14) built atop faster-whisper |
| ffmpeg | 6.x | Demux/resample audio from video inputs | Stable CLI for extracting audio tracks and channel maps; matches existing repo patterns |
| Demucs/UVR5 (MDX nets) | 4.x models | Optional vocal/music separation when overlap detected | Well-known music/SFX reduction for speech isolation; runs locally on PyTorch/ROCm |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| torch / torchaudio (ROCm build) | 2.4+ rocm wheels | Backend for whisperX alignment/diarization and Demucs | Required for AMD GPU acceleration; install from PyTorch ROCm index |
| pyannote-audio | 3.2+ | Speaker diarization embeddings | Needed when assigning speaker labels for Doug vs non-Doug; requires local HF model download |
| silero-vad (via faster-whisper or standalone) | 5.x models | Speech/non-speech and overlap gating | Use for segmenting and overlap detection to decide isolation |
| pysoundfile / librosa | 0.12+ | Resampling, duration checks | For precise timestamp integrity and loudness/overlap probes |
| pydantic / msgspec | 2.x / 0.18+ | Validate/export JSONL schema | Enforce schema for raw + normalized transcript records |
| rich / loguru | 13.x / 0.7+ | Structured logging with timestamps | For run artifact logs and debug traces |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| faster-whisper | openai/whisper (PyTorch) | Simpler dependency stack but slower and higher VRAM; lacks built-in VAD and quantization options |
| whisperX | pure faster-whisper timestamps | Faster but loses forced alignment and diarization quality; less reliable word timing |
| Demucs/UVR5 | No separation step | Avoids artifacts but leaves music bleed; violates voice-isolation policy for overlap cases |
| pyannote-audio | in-house diarization | Custom diarization is complex and brittle; pyannote is battle-tested |

**Installation (ROCm-oriented):**
```bash
uv add faster-whisper==1.2.1 whisperx==3.8.1 ffmpeg-python
uv add --index-url https://download.pytorch.org/whl/rocm6.0 torch torchaudio
# optional separation/diarization extras
uv add demucs pyannote.audio==3.2.1
```

## Architecture Patterns

### Recommended Project Structure
```
02-worktrees/
  asr-runner/            # New worktree with its own pyproject
    pyproject.toml
    asr_pipeline.py      # CLI entrypoint for batch runs
    utils/paths.py       # Reuse supporting_files/project_parent helpers
    utils/audio.py       # Demux, resample, loudness/overlap probes
    utils/confidence.py  # Per-word→segment confidence aggregation
    schemas/transcript.py# JSONL pydantic/msgspec models
00-supporting-files/data/transcripts/{source_id}/  # Outputs
```

### Pattern 1: ASR Pipeline (demux → VAD/overlap → optional separation → ASR → postprocess → export)
**What:** Deterministic pipeline that extracts mono 16 kHz WAV, detects speech/music overlap, conditionally runs separation, transcribes with word timestamps, aggregates confidence, and writes JSONL.
**When to use:** Every ingestion rerun; batch over source IDs for reproducibility.
**Example:**
```python
from faster_whisper import WhisperModel

model = WhisperModel(
    "large-v3", device="cuda", compute_type="float16",
)
segments, info = model.transcribe(
    "audio.wav",
    beam_size=5,
    word_timestamps=True,
    vad_filter=True,
    vad_parameters={"min_silence_duration_ms": 500},
)
segments = list(segments)
```
// Source: https://github.com/SYSTRAN/faster-whisper (README usage + VAD filter, word timestamps)

### Pattern 2: WhisperX Alignment + Diarization
**What:** Align faster-whisper segments to audio for tighter word timings, then assign speaker labels.
**When to use:** After transcription when diarization is needed to tag Doug vs non-Doug or to refine timestamps.
**Example:**
```python
import whisperx

audio = whisperx.load_audio("audio.wav")
asr = whisperx.load_model("large-v3", "cuda", compute_type="float16")
result = asr.transcribe(audio, batch_size=16)

align_model, metadata = whisperx.load_align_model(
    language_code=result["language"], device="cuda",
)
result = whisperx.align(result["segments"], align_model, metadata, audio, device="cuda")

# Optional diarization (requires HF token for local model download)
# diarize = whisperx.DiarizationPipeline(token=HF_TOKEN, device="cuda")
# diar_segments = diarize(audio)
# result = whisperx.assign_word_speakers(diar_segments, result)
```
// Source: https://github.com/m-bain/whisperX (README python usage)

### Anti-Patterns to Avoid
- **Dropping low-confidence segments:** Violates locked decision; keep and flag questionable spans instead.
- **Single-pass transcripts without alignment:** Skipping alignment/diarization yields sloppy timestamps and mislabels Doug vs non-Doug.
- **Ad-hoc path building:** Hardcoding paths breaks relocatability; reuse supporting_files/project_parent discovery.
- **Over-aggressive separation:** Heavy denoising can distort speech; keep isolation optional and flag poor separation.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Voice activity detection & overlap gating | Custom energy thresholds | Silero VAD (via faster-whisper) | Handles noise/short pauses; tuned defaults; configurable |
| Speaker diarization | DIY clustering/embeddings | pyannote-audio diarization pipeline | Pretrained, well-tested, supports word-level speaker tags |
| Forced alignment | Custom DTW/phoneme alignment | whisperX aligner | Robust timestamp refinement with wav2vec2 models |
| Vocal separation | Hand-tuned bandpass filters | Demucs/UVR5 MDX nets | Modern source separation; fewer artifacts when music present |
| JSONL schema validation | Ad-hoc dict assembly | pydantic/msgspec models | Ensures fields and defaults match export contract |

**Key insight:** These areas hide edge cases (breath noises, overlaps, punctuation drift, encoding quirks); mature libraries reduce error rates and save GPU time.

## Common Pitfalls

### Pitfall 1: Timestamp drift from resampling/mismatched sample rates
**What goes wrong:** Audio demuxed at 48 kHz but ASR expects 16 kHz; offsets skew segments and confidence aggregation.
**Why it happens:** ffmpeg defaults differ from model expectations.
**How to avoid:** Normalize to mono 16 kHz WAV before ASR; assert duration consistency with soundfile/librosa; log detected rate.
**Warning signs:** Segment start/end exceed file duration; alignment fails; negative durations after re-encoding.

### Pitfall 2: ROCm wheel mismatch for torch/ctranslate2
**What goes wrong:** Installing CUDA wheels on AMD GPUs or mixing ROCm versions causes runtime errors or CPU fallback.
**Why it happens:** Default PyPI wheels target CUDA; ROCm needs specific indices/wheels.
**How to avoid:** Pin torch/torchaudio from the ROCm index; verify `torch.version.hip` and GPU visibility; consider building ctranslate2 from source if ROCm wheels lag.
**Warning signs:** `HIP error`, `no kernel image`, or `Using CPU device` logs despite GPU.

### Pitfall 3: Over-cleaning audio removes DougDoug characteristics
**What goes wrong:** Heavy separation/denoise strips prosody/fillers that matter for alignment and style.
**Why it happens:** Aggressive Demucs/UVR5 configs or multi-band gates.
**How to avoid:** Run separation only when overlap/music detected; prefer light models; keep raw mix for reference; store quality flags.
**Warning signs:** Hollow/metallic speech; sharply reduced RMS; ASR hallucinations increase.

### Pitfall 4: Missing confidence propagation
**What goes wrong:** Per-word logprobs exist but are not aggregated; exports lack usable segment-level confidence and flags.
**Why it happens:** Pipeline drops metadata when normalizing text.
**How to avoid:** Compute segment confidence (e.g., mean/min of word logprobs), carry VAD/overlap flags, and store raw text with tokens; validate schema before writing JSONL.
**Warning signs:** Downstream alignment receives uniform confidence values or none; QA cannot filter low-quality spans.

## Code Examples

### Faster-Whisper Transcription with VAD and Word Timestamps
```python
from faster_whisper import WhisperModel

model = WhisperModel("large-v3", device="cuda", compute_type="float16")
segments, info = model.transcribe(
    "audio.wav",
    word_timestamps=True,
    vad_filter=True,
    vad_parameters={"min_silence_duration_ms": 500},
)
segments = list(segments)
print(info.language, info.language_probability)
```
// Source: https://github.com/SYSTRAN/faster-whisper (README)

### WhisperX Alignment + Optional Diarization
```python
import whisperx

audio = whisperx.load_audio("audio.wav")
model = whisperx.load_model("large-v3", device="cuda", compute_type="float16")
result = model.transcribe(audio, batch_size=16)

align_model, metadata = whisperx.load_align_model(language_code=result["language"], device="cuda")
aligned = whisperx.align(result["segments"], align_model, metadata, audio, device="cuda")

# diarizer = whisperx.DiarizationPipeline(token=HF_TOKEN, device="cuda")
# diar_segments = diarizer(audio)
# aligned = whisperx.assign_word_speakers(diar_segments, aligned)
```
// Source: https://github.com/m-bain/whisperX (README)

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| openai/whisper FP16 on PyTorch | faster-whisper 1.2.x on CTranslate2 with batching | 2025-10 | ~4x speedup, lower VRAM, built-in VAD/word timestamps |
| Utterance-level timestamps only | whisperX forced alignment + diarization | 2023-2026 | Tighter word timing, speaker labels for filtering |
| Always run source separation | Conditional Demucs/UVR5 based on overlap/music detection | 2024+ | Preserves speech quality; avoids artifacts when clean audio |
| Raw text export | Normalized text + confidence/logprob metadata + quality flags | 2025+ | Enables downstream alignment and QA filtering |

**Deprecated/outdated:**
- Using paid/cloud ASR (out of scope and conflicts with requirements).
- Manual threshold-based diarization without embeddings (poor accuracy vs pyannote).

## Open Questions

1. **ROCm support path for faster-whisper/ctranslate2**
   - What we know: CTranslate2 claims AMD support; ROCm wheels sometimes lag behind CUDA; may require source build.
   - What's unclear: Are prebuilt ROCm wheels available for 1.2.x on ROCm 6.0? Do we need to pin ctranslate2 to a specific version?
   - Recommendation: Test pip install on the target machine; fall back to source build with `-DWITH_CUDA=OFF -DWITH_ROCM=ON`; document tested versions.

2. **Best lightweight metric for overlap/music detection**
   - What we know: Silero VAD can flag speech/non-speech; Demucs runs are expensive.
   - What's unclear: Which quick probe (e.g., RMS ratio by band, torchaudio `spectral_centroid`) is most reliable for triggering separation?
   - Recommendation: Prototype a short-window band-energy heuristic and log scores alongside VAD; calibrate thresholds on a few Doug streams.

3. **Speaker labeling without HF token?**
   - What we know: pyannote diarization models require HF token acceptance; the policy forbids paid APIs but allows local downloads.
   - What's unclear: Whether offline tokenless models (e.g., speaker-diarization-community-1 with pre-accepted license) are already cached.
   - Recommendation: Cache required diarization model locally in `large-files` and document token setup; provide fallback of tagging segments as "unknown" but still distinguishing Doug vs non-Doug via energy heuristics if token unavailable.

## Sources

### Primary (HIGH confidence)
- SYSTRAN/faster-whisper README (release v1.2.1, 2025-10-31) — usage, VAD filter, word timestamps, batched inference.
- m-bain/whisperX README (release v3.8.1, 2026-02-14) — alignment, diarization, batching, GPU requirements.

### Secondary (MEDIUM confidence)
- Prior repo patterns in `02-worktrees/old-master/02-development/chat-extraction/chat-extraction.py` — path discovery and data directory conventions.

### Tertiary (LOW confidence)
- ROCm wheel availability for ctranslate2/faster-whisper — needs validation on target machine.

## Metadata

**Confidence breakdown:**
- Standard Stack: MEDIUM — versions pulled from latest releases; ROCm availability needs confirmation.
- Architecture: MEDIUM — based on established ASR pipelines and repo path patterns; separation trigger heuristic still open.
- Pitfalls: MEDIUM — drawn from common ASR issues and ROCm experience; need validation on this hardware.

**Research date:** 2026-02-28
**Valid until:** 2026-03-30
