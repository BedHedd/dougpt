# Phase 02 User Setup

## Service: huggingface

Why: Enable optional local diarization with pyannote/WhisperX when available.

### Environment Variables

| Name | Required | Source |
| --- | --- | --- |
| `HUGGINGFACE_TOKEN` | Optional (required for diarization) | Hugging Face Settings -> Access Tokens |

### Setup Steps

1. Sign in at https://huggingface.co/.
2. Create a token in Settings -> Access Tokens.
3. Export token before running diarization-enabled notebook cells:

```bash
export HUGGINGFACE_TOKEN="your-token"
```

### Verification

Run the notebook transcription stage with diarization enabled and verify transcript JSON `diarization.used` becomes `true` when dependencies are installed.

Status: Incomplete (pending user token setup)
