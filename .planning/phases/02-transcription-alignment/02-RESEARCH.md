# Phase 2: Transcription & Alignment - Research

**Researched:** 2026-02-22
**Domain:** Local ASR transcription with Whisper, chat-transcript temporal alignment
**Confidence:** HIGH

## Summary

This phase requires local Whisper transcription with word-level timestamps (ALGN-01) and automatic chat-transcript offset detection with window-based alignment (ALGN-02). The research identifies **faster-whisper** as the optimal transcription backend (4x faster than OpenAI whisper, lower memory) combined with **WhisperX** for accurate word-level timestamps via wav2vec2 forced alignment. For chat-transcript alignment, a custom algorithm is needed that accounts for Twitch chat's natural reaction lag (typically 2-10 seconds) and uses temporal window matching.

**Primary recommendation:** Use faster-whisper + WhisperX for transcription; implement custom window-based alignment algorithm with configurable reaction lag window (default 5-15 seconds) and topic proximity constraints.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Both word-level AND segment-level timestamps in output
- Both JSON (for pipelines) + SRT (for human review) formats
- Whisper metadata (confidence, language, model version) in separate sidecar file
- Single transcript file per VOD (not chunked into multiple files)
- Auto-detect chat↔transcript offset automatically (not manual calibration)
- Window-based alignment — chat reacts to Doug with a delay, so align "Doug says X" with "chat responding to Doug"
- Topic matching near timestamp — avoid matching chat from much later in VOD (e.g., 1hr chat shouldn't align to 2min transcript)
- Store alignment data in separate offset file (not inline in chat or transcript)

### Claude's Discretion
- Exact window size for alignment
- Topic matching algorithm/approach
- How to handle edge cases (silence, overlapping speech, missing chat segments)

### Deferred Ideas (OUT OF SCOPE)
- Non-Python runtime choices — future decision
- Cloud ASR providers — out of scope, local Whisper only
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| ALGN-01 | Transcribe VOD audio locally (Whisper or equivalent) with word-level timestamps. | faster-whisper + WhisperX pipeline; word_timestamps=True parameter; JSON/SRT output |
| ALGN-02 | Estimate per-VOD chat/VOD time offsets and align chat messages to transcript windows with QA hooks. | Window-based alignment with configurable reaction lag; cross-correlation for initial offset detection; topic proximity constraints |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| faster-whisper | 1.1.1+ | Whisper transcription backend | 4x faster than openai/whisper, lower memory, CTranslate2 optimization, supports GPU/CPU |
| whisperx | 3.3+ | Word-level timestamp accuracy | wav2vec2 forced alignment for accurate word timestamps; batched inference for speed |
| pyannote-audio | (via whisperx) | Voice Activity Detection | Integrated VAD reduces hallucinations; improves batching |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| stable-ts | 2.19+ | Alternative timestamp stabilization | If WhisperX has issues with specific audio; better silence handling |
| whisper-timestamped | 1.15+ | Alternative with confidence scores | If per-word confidence is critical; DTW-based alignment |
| torch | 2.0+ | GPU acceleration | Required for faster-whisper GPU inference |
| numpy | 1.24+ | Array operations | Transcript processing, alignment algorithms |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| faster-whisper | openai/whisper | Simpler API but 4x slower, higher memory |
| WhisperX alignment | stable-ts alignment | stable-ts more flexible but less accurate word timestamps |
| whisper-timestamped | WhisperX | Better confidence scores but slower, less maintained |

**Installation:**
```bash
pip install faster-whisper whisperx
# For GPU support (CUDA 12):
pip install nvidia-cublas-cu12 nvidia-cudnn-cu12
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── transcription/
│   ├── __init__.py
│   ├── transcriber.py      # WhisperX/faster-whisper wrapper
│   ├── output.py           # JSON/SRT/metadata output
│   └── models.py           # Model loading, caching
├── alignment/
│   ├── __init__.py
│   ├── offset_detector.py  # Auto offset detection
│   ├── window_aligner.py   # Window-based chat alignment
│   └── topic_matcher.py    # Topic proximity logic
└── pipeline/
    ├── __init__.py
    └── phase2_runner.py    # Orchestrates transcription + alignment
```

### Pattern 1: WhisperX Transcription Pipeline
**What:** Use WhisperX for fast transcription with accurate word-level timestamps
**When to use:** All VOD transcription in this phase
**Example:**
```python
# Source: https://github.com/m-bain/whisperX
import whisperx

device = "cuda"
audio_file = "vod_audio.mp3"
batch_size = 16  # Reduce if low on GPU memory
compute_type = "float16"  # Use "int8" for lower memory

# 1. Transcribe with whisper (batched)
model = whisperx.load_model("large-v3", device, compute_type=compute_type)
audio = whisperx.load_audio(audio_file)
result = model.transcribe(audio, batch_size=batch_size)

# 2. Align whisper output for word-level timestamps
model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
result = whisperx.align(result["segments"], model_a, metadata, audio, device)

# result["segments"] now contains word-level timestamps
for segment in result["segments"]:
    for word in segment.get("words", []):
        print(f"{word['start']:.2f}-{word['end']:.2f}: {word['word']}")
```

### Pattern 2: Faster-Whisper Direct Usage
**What:** Use faster-whisper directly for simpler cases
**When to use:** When WhisperX alignment isn't needed or GPU memory is limited
**Example:**
```python
# Source: https://github.com/SYSTRAN/faster-whisper
from faster_whisper import WhisperModel

model_size = "large-v3"
model = WhisperModel(model_size, device="cuda", compute_type="float16")

# Transcribe with word-level timestamps
segments, info = model.transcribe("audio.mp3", word_timestamps=True)

print(f"Detected language '{info.language}' with probability {info.language_probability}")

for segment in segments:
    for word in segment.words:
        print("[%.2fs -> %.2fs] %s" % (word.start, word.end, word.word))
```

### Pattern 3: Chat-Transcript Alignment Algorithm
**What:** Window-based alignment accounting for chat reaction lag
**When to use:** Aligning chat messages to transcript segments
**Example:**
```python
def align_chat_to_transcript(
    chat_messages: list[dict],  # [{timestamp, text, user}]
    transcript_segments: list[dict],  # [{start, end, text, words}]
    reaction_window: tuple[float, float] = (2.0, 15.0),  # min/max lag
    topic_proximity_threshold: float = 30.0,  # seconds
) -> list[dict]:
    """
    Align chat messages to transcript segments with reaction lag.
    
    Returns list of alignments:
    [{chat_msg, transcript_segment, offset, confidence}]
    """
    alignments = []
    
    for chat in chat_messages:
        chat_time = chat["timestamp"]
        
        # Find candidate transcript windows
        candidates = []
        for seg in transcript_segments:
            # Calculate expected chat response window
            expected_start = seg["start"] + reaction_window[0]
            expected_end = seg["end"] + reaction_window[1]
            
            # Check if chat falls in reaction window
            if expected_start <= chat_time <= expected_end:
                # Topic proximity check
                time_diff = abs(chat_time - seg["start"])
                if time_diff <= topic_proximity_threshold:
                    candidates.append({
                        "segment": seg,
                        "offset": chat_time - seg["start"],
                        "proximity": time_diff
                    })
        
        # Score candidates by proximity (closer = better)
        if candidates:
            best = min(candidates, key=lambda x: x["proximity"])
            alignments.append({
                "chat_msg": chat,
                "transcript_segment": best["segment"],
                "offset": best["offset"],
                "confidence": 1.0 / (1.0 + best["proximity"] / 10.0)
            })
    
    return alignments
```

### Anti-Patterns to Avoid
- **Using openai/whisper directly for long VODs:** 4x slower, memory issues; use faster-whisper instead
- **Ignoring VAD preprocessing:** Leads to hallucinations in silence; always enable VAD
- **Single-pass alignment without offset detection:** Chat-VOD timing varies per stream; detect offset per-VOD
- **Matching chat to transcript by text similarity only:** Ignores temporal constraints; combine with time proximity

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Word-level timestamps | Custom DTW on attention weights | WhisperX alignment | Proven accuracy, handles edge cases |
| Audio loading/preprocessing | Custom FFmpeg wrapper | whisperx.load_audio() | Handles sample rate, normalization |
| VAD (Voice Activity Detection) | Custom energy threshold | Silero VAD (via whisperx) | Handles noise, pauses correctly |
| SRT/VTT generation | Custom formatter | stable-ts result.to_srt_vtt() | Handles edge cases, word highlighting |

**Key insight:** The Whisper ecosystem has mature implementations for word-level timestamps. WhisperX's wav2vec2 forced alignment is state-of-the-art for timestamp accuracy.

## Common Pitfalls

### Pitfall 1: Whisper Hallucinations in Silence
**What goes wrong:** Whisper generates fabricated text during silent portions or non-speech audio
**Why it happens:** Model wasn't trained on sufficient silence; attempts to predict text anyway
**How to avoid:** 
- Enable VAD filtering (`vad_filter=True` in faster-whisper)
- Use `suppress_silence=True` in stable-ts
- Post-process to remove segments with very low confidence
**Warning signs:** Repeated phrases, text appearing in known silent sections, segments with no audio activity

### Pitfall 2: Timestamp Drift in Long VODs
**What goes wrong:** Timestamps become increasingly inaccurate as the VOD progresses
**Why it happens:** Accumulated error in chunk-based processing; model context drift
**How to avoid:**
- Use WhisperX's forced alignment which recalibrates per-segment
- Reset context periodically with `condition_on_previous_text=False`
- Process in chunks with overlap and merge
**Warning signs:** Segments with impossible durations, words appearing before previous words end

### Pitfall 3: Incorrect Chat-Transcript Offset
**What goes wrong:** All chat messages align to wrong transcript segments
**Why it happens:** VOD timestamp doesn't match chat timestamp due to stream delay, VOD editing, or timezone issues
**How to avoid:**
- Auto-detect offset using cross-correlation on activity peaks
- Sample multiple time points to verify offset consistency
- Allow per-VOD offset adjustment
**Warning signs:** Chat reactions don't match content; "early" reactions to events not yet spoken

### Pitfall 4: GPU Memory Exhaustion
**What goes wrong:** OOM errors during transcription of long VODs
**Why it happens:** Large models + batch processing + long audio exceeds VRAM
**How to avoid:**
- Use `compute_type="int8"` for 8-bit quantization
- Reduce `batch_size` (default 16, try 4 or 8)
- Process audio in segments with model unloading between chunks
- Use smaller model (medium instead of large) for initial pass
**Warning signs:** Slow performance before crash, CUDA out of memory errors

### Pitfall 5: Repetition Loops
**What goes wrong:** Whisper gets stuck repeating the same phrase
**Why it happens:** Model enters failure loop, often on difficult audio sections
**How to avoid:**
- Set `condition_on_previous_text=False` (default in WhisperX)
- Use temperature fallback (default in whisper: 0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
- Enable compression ratio threshold
**Warning signs:** Same phrase repeated multiple times, segments with identical text

## Code Examples

### Complete Transcription + Output Pipeline
```python
# Source: Synthesized from faster-whisper and WhisperX docs
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import whisperx
from faster_whisper import WhisperModel

@dataclass
class TranscriptOutput:
    json_path: Path
    srt_path: Path
    metadata_path: Path

def transcribe_vod(
    audio_path: str,
    output_dir: str,
    model_size: str = "large-v3",
    device: str = "cuda",
    compute_type: str = "float16",
    batch_size: int = 16,
) -> TranscriptOutput:
    """
    Transcribe VOD audio with word-level timestamps.
    Outputs JSON, SRT, and metadata files.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 1. Load audio
    audio = whisperx.load_audio(audio_path)
    
    # 2. Transcribe with faster-whisper backend
    model = whisperx.load_model(model_size, device, compute_type=compute_type)
    result = model.transcribe(audio, batch_size=batch_size)
    
    # 3. Align for word-level timestamps
    align_model, align_metadata = whisperx.load_align_model(
        language_code=result["language"], 
        device=device
    )
    result = whisperx.align(
        result["segments"], 
        align_model, 
        align_metadata, 
        audio, 
        device
    )
    
    # 4. Prepare outputs
    base_name = Path(audio_path).stem
    
    # JSON output (full data)
    json_path = output_path / f"{base_name}.json"
    with open(json_path, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    # SRT output (for human review)
    srt_path = output_path / f"{base_name}.srt"
    segments_to_srt(result["segments"], srt_path)
    
    # Metadata sidecar
    metadata_path = output_path / f"{base_name}.metadata.json"
    metadata = {
        "source_file": audio_path,
        "language": result["language"],
        "model": model_size,
        "align_model": align_metadata.get("model_name"),
        "word_count": sum(len(s.get("words", [])) for s in result["segments"]),
        "duration_seconds": result["segments"][-1]["end"] if result["segments"] else 0,
    }
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    
    return TranscriptOutput(json_path, srt_path, metadata_path)

def segments_to_srt(segments: list, output_path: Path):
    """Convert segments to SRT format."""
    def format_time(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    
    with open(output_path, "w") as f:
        for i, seg in enumerate(segments, 1):
            f.write(f"{i}\n")
            f.write(f"{format_time(seg['start'])} --> {format_time(seg['end'])}\n")
            f.write(f"{seg['text'].strip()}\n\n")
```

### Auto Offset Detection
```python
import numpy as np
from scipy import signal

def detect_chat_vod_offset(
    chat_messages: list[dict],
    transcript_segments: list[dict],
    search_range: tuple[float, float] = (-30.0, 30.0),
    resolution: float = 0.5,
) -> float:
    """
    Auto-detect the offset between chat timestamps and transcript timestamps.
    
    Uses cross-correlation on activity histograms to find optimal offset.
    
    Returns: offset in seconds (add to transcript time to get chat time)
    """
    # Build activity histograms
    max_time = max(
        max(m["timestamp"] for m in chat_messages),
        max(s["end"] for s in transcript_segments)
    )
    
    bins = np.arange(0, max_time + resolution, resolution)
    
    # Chat activity (count of messages per bin)
    chat_times = [m["timestamp"] for m in chat_messages]
    chat_hist, _ = np.histogram(chat_times, bins=bins)
    
    # Transcript activity (total speech duration per bin)
    transcript_activity = np.zeros(len(bins) - 1)
    for seg in transcript_segments:
        start_bin = int(seg["start"] / resolution)
        end_bin = int(seg["end"] / resolution)
        transcript_activity[start_bin:end_bin] += 1
    
    # Cross-correlation
    correlation = signal.correlate(chat_hist, transcript_activity, mode='full')
    lags = signal.correlation_lags(len(chat_hist), len(transcript_activity), mode='full')
    
    # Find best offset within search range
    min_offset_samples = int(search_range[0] / resolution)
    max_offset_samples = int(search_range[1] / resolution)
    
    valid_mask = (lags >= min_offset_samples) & (lags <= max_offset_samples)
    valid_correlation = correlation[valid_mask]
    valid_lags = lags[valid_mask]
    
    best_idx = np.argmax(valid_correlation)
    best_offset = -valid_lags[best_idx] * resolution  # Negative because chat lags
    
    return best_offset
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| openai/whisper for all transcription | faster-whisper with CTranslate2 | 2023 | 4x faster, lower memory |
| Whisper segment timestamps only | wav2vec2 forced alignment (WhisperX) | 2023 | Accurate word-level timestamps |
| Manual timestamp correction | stable-ts VAD-based adjustment | 2023 | More reliable timestamps |
| Single-model transcription | Whisper + wav2vec2 alignment pipeline | 2023 | Best of both: speed + accuracy |

**Deprecated/outdated:**
- **openai/whisper word_timestamps:** Native word timestamps are unreliable; use forced alignment instead
- **Direct timestamp extraction from attention:** WhisperX's approach is more robust

## Open Questions

1. **What is the typical reaction lag for Twitch chat?**
   - What we know: Research shows live streaming latency varies; Twitch typically has 10-30s stream delay plus user reaction time
   - What's unclear: Exact lag for DougDoug's specific chat patterns
   - Recommendation: Start with 5-15s window, make configurable; analyze sample VODs to calibrate

2. **How to handle overlapping speech or multiple speakers?**
   - What we know: WhisperX supports speaker diarization via pyannote
   - What's unclear: Whether diarization is needed (DougDoug streams are typically single speaker)
   - Recommendation: Start without diarization; add if alignment quality issues arise

3. **What confidence threshold to use for filtering low-quality transcriptions?**
   - What we know: Whisper provides per-word probability; whisper-timestamped adds confidence scores
   - What's unclear: Optimal thresholds for DougDoug's audio quality (game audio + voice)
   - Recommendation: Start with 0.5 threshold for words, adjust based on QA results

## Sources

### Primary (HIGH confidence)
- https://github.com/SYSTRAN/faster-whisper - faster-whisper documentation and benchmarks
- https://github.com/m-bain/whisperX - WhisperX documentation and examples
- https://github.com/jianfch/stable-ts - stable-ts timestamp stabilization techniques
- https://arxiv.org/abs/2303.00747 - WhisperX paper on batched inference and alignment

### Secondary (MEDIUM confidence)
- https://modal.com/blog/choosing-whisper-variants - Comparison of Whisper variants
- https://github.com/linto-ai/whisper-timestamped - Alternative word-level timestamp approach
- https://arxiv.org/abs/2408.16589 - CrisperWhisper paper on timestamp accuracy

### Tertiary (LOW confidence)
- Various web search results on chat-transcript alignment (no specific authoritative source found; custom implementation recommended)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Multiple official sources, active community, proven in production
- Architecture: HIGH - Based on official documentation and examples
- Pitfalls: HIGH - Documented in multiple sources including official discussions and research papers
- Alignment algorithm: MEDIUM - Custom implementation needed; based on general principles rather than Twitch-specific research

**Research date:** 2026-02-22
**Valid until:** 30 days (stable Whisper ecosystem, but new models may emerge)
