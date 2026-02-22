# Stack Research

**Domain:** Local Twitch chat-style LLM tuned on DougDoug streams (audio + chat)
**Researched:** 2026-02-21
**Confidence:** MEDIUM (fast-moving ML ecosystem; versions verified via PyPI metadata)

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| torch | 2.10.0 | GPU/CPU tensor and autograd backbone for training and inference | Ubiquitous deep-learning runtime with mature CUDA support and ecosystem tooling; required by most downstream libraries |
| transformers | 4.57.6 | Model loading, tokenization, and training pipelines | Stable 4.x line remains compatible with vLLM (<5 requirement) while supporting Llama 3/other 2025 chat models |
| peft | 0.18.1 | Parameter-efficient fine-tuning (LoRA/QLoRA) | Enables 8–14B chat models to train on consumer GPUs without full-precision memory costs |
| trl | 0.28.0 | Supervised/DPO/RLHF-style chat fine-tuning utilities | Provides chat-centric trainers and reward-free preference optimization to shape Twitch-chat tone |
| vllm | 0.15.1 | High-throughput, streaming inference server | Efficient KV-cache management and paged attention for rapid chat-style responses on a single GPU |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| accelerate | 1.12.0 | Device placement, mixed precision, multi-GPU orchestration | Always, to keep training scripts simple and reproducible |
| datasets | 4.5.0 | Streaming/loading/preprocessing of large chat+audio-text pairs | When building the paired transcript → reply datasets and shuffling efficiently |
| flash-attn | 2.8.3 | Fused attention kernels for faster training/inference | On NVIDIA SM80+ GPUs to speed 7–13B training/inference and reduce memory |
| faster-whisper | 1.2.1 | Local Whisper transcription with word-level timestamps | For VOD transcription and alignment without cloud APIs |
| uv | 0.10.4 | Python package and venv manager | For reproducible, fast isolated environments on developer machines |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| pre-commit | Enforce formatting and linting on commit | Add hooks for ruff/black to keep data scripts clean |
| ruff | Fast Python linter/formatter | Run in CI and pre-commit; configure for src and notebooks |
| Weights & Biases (optional) | Experiment tracking | Use offline mode to respect local-first constraint; helps compare LoRA sweeps |

## Installation

```bash
# Core
pip install "torch==2.10.0" "transformers==4.57.6" "peft==0.18.1" "trl==0.28.0" "vllm==0.15.1"

# Supporting
pip install "accelerate==1.12.0" "datasets==4.5.0" "flash-attn==2.8.3" "faster-whisper==1.2.1"

# Dev tools
pip install "uv==0.10.4" "pre-commit==4.5.1" "ruff==0.15.2"
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| vllm | llama.cpp (GGUF) | CPU-only or sub-8GB VRAM inference where CUDA is unavailable |
| faster-whisper | WhisperX | When you need forced alignment/diarization beyond faster-whisper’s timestamps |
| flash-attn | xformers | If GPU lacks SM80+ support or flash-attn build fails |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| transformers 5.x with vllm 0.15.1 | vLLM metadata pins transformers<5; 5.x will fail dependency resolution | Pin transformers 4.57.6 until vLLM updates its cap |
| Full-precision fine-tuning of 7–13B on consumer GPUs | Exceeds VRAM and slows iterations, risking instability | Use PEFT/QLoRA via peft + bitsandbytes (optional) |
| Cloud-only ASR APIs for transcription | Violates local-first constraint and adds cost/latency | Use faster-whisper locally |

## Stack Patterns by Variant

**If single 12–16GB GPU:**
- Use 4-bit QLoRA (peft) with flash-attn and gradient checkpointing to fit 8B models; stream inference via vLLM.

**If multi-GPU or >24GB VRAM:**
- Use BF16 training with accelerate + flash-attn for faster convergence; consider 13B base models for richer chat style.

**If CPU-only or laptop iGPU:**
- Skip training; run inference with llama.cpp GGUF quantization and focus on data pipeline validation.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| transformers 4.57.6 | vllm 0.15.1 | vLLM requires transformers<5 per PyPI metadata |
| torch 2.10.0 | flash-attn 2.8.3 | Tested pairing; requires NVIDIA GPU with SM80+ for speedups |
| torch 2.10.0 | accelerate 1.12.0 | accelerate requires torch>=2.0; no pin conflicts |
| peft 0.18.1 | transformers 4.57.6 | No upper-bound pins; used together in current HF examples |
| faster-whisper 1.2.1 | torch optional | Uses CTranslate2; torch not required, can coexist in env |

## Sources

- https://pypi.org/pypi/torch/json — verified latest torch 2.10.0
- https://pypi.org/pypi/transformers/json — latest 5.2.0; selected 4.57.6 for vLLM compatibility (latest 4.x)
- https://pypi.org/pypi/peft/json — verified 0.18.1
- https://pypi.org/pypi/trl/json — verified 0.28.0
- https://pypi.org/pypi/vllm/json — verified 0.15.1 and requirement transformers<5
- https://pypi.org/pypi/datasets/json — verified 4.5.0
- https://pypi.org/pypi/accelerate/json — verified 1.12.0 and torch>=2.0 requirement
- https://pypi.org/pypi/faster-whisper/json — verified 1.2.1
- https://pypi.org/pypi/flash-attn/json — verified 2.8.3
- https://pypi.org/pypi/uv/json — verified 0.10.4
- https://pypi.org/pypi/pre-commit/json — verified 4.5.1
- https://pypi.org/pypi/ruff/json — verified 0.15.2

---
*Stack research for: Local Twitch chat-style LLM tuned on DougDoug streams (audio + chat)*
*Researched: 2026-02-21*
