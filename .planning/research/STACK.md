# Stack Research

**Domain:** Local video/chat extraction + transcript alignment + local LLM fine-tuning
**Researched:** 2026-02-26
**Confidence:** HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.12.x | Single runtime for extraction, alignment, training | 2025/2026 ecosystem center for ASR/OCR/LLM tooling; avoids polyglot glue cost. |
| FFmpeg | 8.0.1 | Deterministic audio/video demux, resample, frame extraction | Most reliable local media foundation; broad codec support and stable CLI behavior for reproducible pipelines. |
| WhisperX | 3.8.1 | ASR with word timestamps + optional diarization | Built for long-form ASR with forced alignment and word-level timestamps; better fit than plain Whisper for timeline alignment. |
| PaddleOCR | 3.4.0 | OCR on rendered Twitch chat in video frames | Strong scene-text OCR with active 3.x releases and CPU/GPU deployment paths; practical for overlay chat extraction from recordings. |
| OpenCV (opencv-python) | 4.13.0.92 | Frame ROI detection, denoise, text-region preprocessing | Standard CV baseline for improving OCR quality before recognition; low cost and mature. |
| PyTorch | 2.10.0 | Local training/inference backend | Required by modern fine-tuning stack and broad model compatibility. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| faster-whisper | 1.2.1 | Fast Whisper inference backend (CTranslate2) | Use as WhisperX backend for faster/cheaper ASR runs on local GPU or quantized CPU. |
| pyannote.audio | 4.0.4 | Speaker diarization | Use only if speaker turns matter; skip for single-speaker streams to reduce complexity. |
| Transformers | 5.2.0 | Model loading/training interface | Base API for local SFT workflows and checkpoint management. |
| PEFT | 0.18.1 | LoRA/QLoRA adapters | Default fine-tuning method for low VRAM and low cost. |
| TRL | 0.29.0 | SFT trainer and post-training loops | Use for supervised chat fine-tuning first; add RL later only if needed. |
| bitsandbytes | 0.49.2 | 4-bit/8-bit quantization for QLoRA | Use on NVIDIA GPUs for memory-efficient fine-tuning and bigger models on small hardware. |
| Unsloth | 2026.2.1 | Faster local fine-tuning workflows | Use when optimizing for speed/VRAM on consumer GPUs; exports to GGUF pipelines cleanly. |
| DuckDB | 1.4.4 | Local analytics DB for aligned dataset | Use as canonical local store (Parquet + SQL) for dataset QA and reproducible splits. |
| Polars | 1.38.1 | High-speed dataframe transforms | Use for timestamp joins/filtering instead of pandas for large transcript/chat tables. |
| RapidFuzz | 3.14.3 | Fuzzy lexical matching in alignment heuristics | Use to recover slight ASR/OCR mismatches while joining utterances to chat bursts. |
| intervaltree | 3.2.1 | Time-window overlap joins | Use for deterministic "speech window -> chat window" matching logic. |
| TwitchDownloaderCLI | 1.56.4 | Optional direct Twitch chat export | Use only when you still have source VOD IDs; bypasses OCR and improves chat fidelity. |
| llama.cpp | b8169 | Local GGUF inference runtime | Use for low-cost local inference/benchmarking after fine-tune export. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| uv | 0.10.6 | Python env + dependency management | Fast lock/sync; use one lockfile for deterministic local setup. |
| Snakemake | 9.16.3 | Reproducible multi-stage pipeline orchestration | Best fit for file-driven steps (demux -> ASR -> OCR -> align -> train). |
| DVC | 3.66.1 | Dataset/model versioning with Git linkage | Track heavy artifacts without bloating Git history. |

## Installation

```bash
# Base environment
uv python install 3.12
uv venv
source .venv/bin/activate

# Core extraction + alignment
uv pip install whisperx==3.8.1 faster-whisper==1.2.1 paddleocr==3.4.0 opencv-python==4.13.0.92 pyannote.audio==4.0.4
uv pip install duckdb==1.4.4 polars==1.38.1 rapidfuzz==3.14.3 intervaltree==3.2.1

# Fine-tuning stack
uv pip install torch==2.10.0 transformers==5.2.0 peft==0.18.1 trl==0.29.0 bitsandbytes==0.49.2 unsloth==2026.2.1

# Workflow tooling
uv pip install snakemake==9.16.3 dvc==3.66.1
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| WhisperX | plain `openai/whisper` | Use only for quick baseline transcripts when exact word timing is not needed. |
| PaddleOCR + OpenCV | EasyOCR/Tesseract-only | Use only for very simple, high-contrast overlays or CPU-only minimal setup. |
| PEFT + TRL (QLoRA-first) | Full fine-tuning | Use only if you have high-VRAM hardware and proven need for full-weight updates. |
| Snakemake | Ad-hoc shell scripts | Use only for one-off prototypes; avoid for repeatable dataset generation. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `ffmpeg-python` as core media layer | Stale package (`0.2.0`, 2019) and weaker debuggability than direct CLI | Use native FFmpeg CLI commands with explicit args. |
| API-dependent transcription/chat extraction stack | Violates local-first/zero-recurring-cost constraint and can break reproducibility | Use WhisperX/faster-whisper + OCR/TwitchDownloaderCLI locally. |
| Full-model fine-tuning as default | High VRAM/time cost; poor cost-performance early in project | Use QLoRA (PEFT + bitsandbytes), then escalate only if needed. |
| OCR-only chat extraction without optional VOD path | Unnecessarily fragile when VOD ID exists | Prefer TwitchDownloaderCLI when VOD is available, fallback to OCR otherwise. |

## Stack Patterns by Variant

**If source Twitch VOD IDs are available:**
- Use `TwitchDownloaderCLI` for chat JSON, WhisperX for speech, then timestamp-join in DuckDB/Polars.
- Because chat fidelity and timestamps are higher than OCR-derived chat.

**If only rendered video files are available (YouTube/local exports):**
- Use FFmpeg frame sampling + OpenCV ROI cleanup + PaddleOCR + temporal dedupe.
- Because this is the only robust local-first way to recover on-screen chat.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| whisperx==3.8.1 | faster-whisper==1.2.1 | WhisperX v3 uses faster-whisper backend and CUDA 12.8 guidance in upstream docs. |
| faster-whisper==1.2.1 | ctranslate2<5,>=4.0 | Declared upstream dependency; pin to avoid runtime mismatch. |
| transformers==5.2.0 | peft==0.18.1, trl==0.29.0 | Current HF stack alignment for modern SFT workflows. |
| bitsandbytes==0.49.2 | CUDA 11.8-13.0 | HF docs confirm support window; verify driver/toolkit locally. |
| paddleocr==3.4.0 | Python 3.8-3.12 | PaddleOCR docs emphasize 3.x API changes and 2.x incompatibility. |

## Confidence by Recommendation

| Area | Confidence | Reason |
|------|------------|--------|
| Media extraction (FFmpeg) | HIGH | Official release docs and long-term ecosystem standard. |
| ASR/timestamping (WhisperX/faster-whisper) | HIGH | Official docs + active releases + explicit word-level alignment capability. |
| Chat extraction (PaddleOCR + OpenCV) | MEDIUM | Strong OCR docs, but Twitch-overlay-specific accuracy depends on video quality and theme variance. |
| Fine-tuning stack (Transformers/PEFT/TRL/bitsandbytes/Unsloth) | HIGH | Official HF/Unsloth docs and current package ecosystem convergence around QLoRA-first workflows. |
| Pipeline orchestration (Snakemake + DVC) | HIGH | Mature reproducibility tools with clear fit for file-driven local ML pipelines. |

## Sources

- https://ffmpeg.org/download.html - latest stable FFmpeg releases and cadence (official)
- https://github.com/m-bain/whisperX/blob/main/README.md - WhisperX capabilities and setup (official)
- https://pypi.org/pypi/whisperx/json - current WhisperX version metadata
- https://pypi.org/pypi/faster-whisper/json - current faster-whisper version + dependency metadata
- https://huggingface.co/docs/transformers/quantization/bitsandbytes - QLoRA/8-bit support and hardware compatibility
- https://pypi.org/pypi/transformers/json - current Transformers version metadata
- https://pypi.org/pypi/peft/json - current PEFT version metadata
- https://pypi.org/pypi/trl/json - current TRL version metadata
- https://docs.unsloth.ai/ - local fine-tuning focus and workflow claims (official)
- https://pypi.org/pypi/unsloth/json - current Unsloth version metadata
- https://raw.githubusercontent.com/PaddlePaddle/PaddleOCR/main/README.md - PaddleOCR 3.x capabilities and upgrade notes
- https://pypi.org/pypi/paddleocr/json - current PaddleOCR version metadata
- https://api.github.com/repos/lay295/TwitchDownloader/releases/latest - latest TwitchDownloaderCLI release
- https://raw.githubusercontent.com/lay295/TwitchDownloader/master/README.md - chat download capabilities
- https://api.github.com/repos/ggml-org/llama.cpp/releases/latest - latest llama.cpp release
- https://raw.githubusercontent.com/ggml-org/llama.cpp/master/README.md - local GGUF inference capabilities
- https://snakemake.readthedocs.io/en/stable/ - Snakemake version and reproducibility model
- https://dvc.org/doc - DVC project docs

---
*Stack research for: local Twitch-style audio/chat alignment and local fine-tuning pipeline*
*Researched: 2026-02-26*
