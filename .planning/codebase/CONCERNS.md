# Codebase Concerns

**Analysis Date:** 2026-02-26

## Tech Debt

**Notebook-first pipeline with minimal packaged code:**
- Issue: Core extraction/transcription/segmentation logic lives in a notebook instead of importable modules, while `src/` only contains Pydantic models.
- Files: `02-worktrees/audio-extraction-review/audio-extraction.ipynb`, `src/transcription/models.py`, `src/transcription/__init__.py`
- Impact: Reuse, testing, dependency management, and production hardening are difficult because behavior is coupled to notebook execution order.
- Fix approach: Move pipeline functions from `02-worktrees/audio-extraction-review/audio-extraction.ipynb` into versioned Python modules under `src/` and keep the notebook as a thin orchestration/demo layer.

**No dependency/packaging manifest in repo root:**
- Issue: Runtime dependencies are implied by notebook imports (`faster_whisper`, `whisperx`, `dotenv`) but no pinned manifest exists.
- Files: `02-worktrees/audio-extraction-review/audio-extraction.ipynb`, `.gitignore`
- Impact: Environment recreation is non-deterministic and failures depend on local machine state.
- Fix approach: Add `pyproject.toml` with pinned dependencies and optional extras for diarization/segmentation.

## Known Bugs

**Diarization regularly falls back due missing Hugging Face token:**
- Symptoms: Transcription records report fallback reason and output segments with no speaker assignment from diarization.
- Files: `00-supporting-files/data/audio-extraction-review/transcripts/sample-single.json`, `00-supporting-files/data/audio-extraction-review/logs/transcription-task2-verify.jsonl`, `02-worktrees/audio-extraction-review/audio-extraction.ipynb`
- Trigger: Run transcription with diarization enabled and no `HUGGINGFACE_TOKEN` in environment.
- Workaround: Set `HUGGINGFACE_TOKEN` or disable diarization in `CONFIG["diarization"]["enabled"]` in `02-worktrees/audio-extraction-review/audio-extraction.ipynb`.

**Extraction failure on missing media paths is present in persisted logs:**
- Symptoms: Extraction stage records `status: failed` with `error: input_not_found`.
- Files: `00-supporting-files/data/audio-extraction-review/logs/extraction-failures.jsonl`, `00-supporting-files/data/audio-extraction-review/logs/extraction-task1-batch.jsonl`, `02-worktrees/audio-extraction-review/audio-extraction.ipynb`
- Trigger: Provide `single_input`/batch item that does not resolve to an existing file.
- Workaround: Validate media inventory under `large-files/` before run and fail fast during config validation.

## Security Considerations

**Run artifacts persist sensitive local context and auth-style config fields:**
- Risk: Run metadata stores absolute filesystem paths and segmentation config snapshots including API-key-like fields.
- Files: `00-supporting-files/data/audio-extraction-review/runs/run-20260222T030354Z-206b1285.json`, `02-worktrees/audio-extraction-review/audio-extraction.ipynb`
- Current mitigation: `.env` is ignored in `.gitignore`; notebook supports loading env values from `00-supporting-files/data/.env`.
- Recommendations: Redact path fields and secrets before writing run snapshots; avoid storing `segmentation.api_key` in persisted `config_snapshot`.

## Performance Bottlenecks

**Large committed JSONL artifacts increase repo and tooling overhead:**
- Problem: Very large tracking data is committed directly in git.
- Files: `00-supporting-files/data/extractions/extractions.jsonl`, `00-supporting-files/data/extractions/metrics.jsonl`
- Cause: Pipeline/log outputs are versioned as normal source artifacts rather than externalized or rotated.
- Improvement path: Move heavy outputs to `large-files/` or external object storage, and track only compact manifests/summaries in git.

## Fragile Areas

**Broad exception handling masks root causes across pipeline stages:**
- Files: `02-worktrees/audio-extraction-review/audio-extraction.ipynb`
- Why fragile: Multiple `except Exception` branches convert failures into generic fallback strings and continue execution, which can hide actionable diagnostics.
- Safe modification: Refactor stage functions to catch specific exception types and standardize typed error records.
- Test coverage: No automated tests detected for extraction/transcription/segmentation paths.

**Path discovery depends on directory naming conventions:**
- Files: `02-worktrees/audio-extraction-review/audio-extraction.ipynb`
- Why fragile: `resolve_project_paths` infers project roots by searching for `00-supporting-files`; renames or moved notebooks break resolution.
- Safe modification: Introduce explicit root config/env override and validate required paths before stage execution.
- Test coverage: No path resolution tests detected.

## Scaling Limits

**Single-process local CPU pipeline with local model endpoint dependency:**
- Current capacity: Configuration defaults to `tiny.en` on `cpu`, synchronous stage execution, and local HTTP segmentation endpoint.
- Limit: Throughput degrades sharply for larger media batches and long transcripts.
- Scaling path: Add batched/parallel workers, GPU-aware config profiles, and queue-backed job orchestration outside notebook runtime.

## Dependencies at Risk

**Unpinned optional ML dependencies:**
- Risk: `faster_whisper`, `whisperx`, and diarization stack availability/version mismatches can break runs.
- Impact: Transcription or diarization stage fails or silently downgrades to fallback behavior.
- Migration plan: Pin dependency versions in `pyproject.toml`, split optional extras, and run compatibility checks in CI.

## Missing Critical Features

**No automated validation pipeline (tests + CI):**
- Problem: There is no test suite or CI workflow detected to guard notebook or model schema changes.
- Blocks: Safe refactoring of `02-worktrees/audio-extraction-review/audio-extraction.ipynb` into reusable modules and reliable regression detection.

## Test Coverage Gaps

**Core pipeline logic is untested:**
- What's not tested: Input discovery, ffmpeg extraction error branches, diarization fallback paths, segmentation schema validation, and export reload checks.
- Files: `02-worktrees/audio-extraction-review/audio-extraction.ipynb`, `src/transcription/models.py`
- Risk: Changes can introduce silent regressions in artifact shape or stage orchestration.
- Priority: High

---

*Concerns audit: 2026-02-26*
