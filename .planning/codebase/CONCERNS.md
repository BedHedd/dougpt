# Codebase Concerns

**Analysis Date:** 2026-02-26

## Tech Debt

**Untracked primary implementation in worktree directories:**
- Issue: The main implementation is in `02-worktrees/chat-extraction/chat-extraction.py` (4,590 lines) and is duplicated in `02-worktrees/old-master/02-development/chat-extraction/chat-extraction.py`, while top-level `.gitignore` excludes `02-worktrees/*` except `02-worktrees/README.md`.
- Files: `.gitignore`, `02-worktrees/chat-extraction/chat-extraction.py`, `02-worktrees/old-master/02-development/chat-extraction/chat-extraction.py`, `02-worktrees/README.md`
- Impact: Changes in the real pipeline are easy to lose, hard to review, and difficult to reuse from the tracked project root.
- Fix approach: Promote one canonical implementation path under a tracked directory (for example `src/`), keep `02-worktrees/` for temporary work only, and delete the duplicate copy.

**Monolithic notebook-export script used as production logic:**
- Issue: The extraction workflow, ffmpeg orchestration, frame reduction, and model calls are combined into one generated marimo script.
- Files: `02-worktrees/chat-extraction/chat-extraction.py`
- Impact: High change risk, poor testability, and fragile cross-cell dependency coupling.
- Fix approach: Split into small tracked modules (I/O, ffmpeg wrapper, extraction logic, schema/models, reporting), and keep notebook UI as a thin caller.

**Repository stores generated artifacts as source-of-truth:**
- Issue: Large generated outputs are committed directly instead of regenerated in pipeline steps.
- Files: `00-supporting-files/data/extractions/extractions.jsonl`, `00-supporting-files/data/extractions/metrics.jsonl`, `00-supporting-files/data/full_chat_frames_report.json`, `00-supporting-files/data/chat_frames_full_color/report.json`
- Impact: Repo churn, heavy diffs, and lower confidence in reproducibility.
- Fix approach: Keep only fixtures/samples in git, move full generated artifacts to release storage, and add deterministic regeneration scripts.

## Known Bugs

**Syntax error in both chat extraction script copies:**
- Symptoms: Python compilation fails with `SyntaxError: f-string: expecting '}'`.
- Files: `02-worktrees/chat-extraction/chat-extraction.py`, `02-worktrees/old-master/02-development/chat-extraction/chat-extraction.py`
- Trigger: Run `python3 -m py_compile 02-worktrees/chat-extraction/chat-extraction.py`.
- Workaround: Replace the malformed f-string command construction at line 92 with safe argument-list construction.

**Tracked modules currently missing from working tree:**
- Symptoms: Package files are tracked in git but absent locally (`git status` shows deleted).
- Files: `src/transcription/__init__.py`, `src/transcription/models.py`, `02-worktrees/audio-extraction-review/audio-extraction.ipynb`
- Trigger: Fresh checkout in current state without restoring deleted tracked files.
- Workaround: Restore tracked files before running importers/tools that depend on transcription types.

**Empty app entrypoint in legacy worktree:**
- Symptoms: App entrypoint exists but has no implementation.
- Files: `02-worktrees/old-master/03-app/app.py`
- Trigger: Attempt to run app from old-master tree.
- Workaround: Use notebook-based flow only, or implement a minimal CLI/app entrypoint.

## Security Considerations

**Environment file present in data directory:**
- Risk: Secret-bearing env files are colocated with project data and can be accidentally copied or committed in adjacent repos.
- Files: `00-supporting-files/data/.env`, `.gitignore`
- Current mitigation: `.env` is git-ignored in `.gitignore`.
- Recommendations: Move runtime secrets out of repository directories and use OS-level secret storage or per-user env injection.

**Weak local API authentication assumptions:**
- Risk: Model API client is configured with HTTP localhost and `api_key="unused"`, which is unsafe if endpoint binding changes.
- Files: `02-worktrees/chat-extraction/chat-extraction.py`
- Current mitigation: Endpoint currently targets localhost (`http://localhost:1234/v1`).
- Recommendations: Require non-placeholder tokens, validate host allowlist, and centralize endpoint/auth config.

## Performance Bottlenecks

**Frame processing loop is CPU-heavy and Python-bound:**
- Problem: Raw frames are streamed from ffmpeg and processed per-frame in Python/numpy with row-energy and correlation calculations.
- Files: `02-worktrees/chat-extraction/chat-extraction.py`
- Cause: Full-frame decoding (`_iter_rgb_frames_ffmpeg`) + per-frame CPU feature extraction and write paths.
- Improvement path: Add bounded worker parallelism and profiling-guided vectorization; push more filtering down to ffmpeg where possible.

**Large extraction datasets inflate local workflows:**
- Problem: Artifacts are large and duplicated across directories (`00-supporting-files` plus `02-worktrees/old-master/00-supporting-files`).
- Files: `00-supporting-files/data/extractions/extractions.jsonl`, `02-worktrees/old-master/00-supporting-files/data/extractions/extractions.jsonl`
- Cause: Full history and generated outputs retained in multiple locations.
- Improvement path: Keep one canonical artifact location, compress/archive historical runs, and prune duplicated trees.

## Fragile Areas

**Cell-order-dependent marimo script wiring:**
- Files: `02-worktrees/chat-extraction/chat-extraction.py`
- Why fragile: Many `@app.cell` functions depend on implicit symbol passing and state mutation; minor edits can break dependency resolution.
- Safe modification: Extract shared functions into importable modules and keep each cell side-effect-free.
- Test coverage: No automated regression tests detected for cell dependency execution order.

**Duplicate script copies diverge easily:**
- Files: `02-worktrees/chat-extraction/chat-extraction.py`, `02-worktrees/old-master/02-development/chat-extraction/chat-extraction.py`
- Why fragile: Same 4,590-line file exists in two places; bug fixes must be manually mirrored.
- Safe modification: Delete one copy and replace with import references to a single tracked module.
- Test coverage: No sync guard or test ensures behavioral parity between copies.

## Scaling Limits

**Repository footprint grows with experiment outputs:**
- Current capacity: `00-supporting-files` is ~55 MB in workspace and includes high-volume generated image/jsonl artifacts.
- Limit: Routine iteration causes repository size and clone/update time growth.
- Scaling path: Store heavy outputs outside git (artifact store/object storage) and keep small golden fixtures only.

**Worktree environment growth becomes costly:**
- Current capacity: `02-worktrees/chat-extraction` is ~567 MB (includes local environment and generated outputs).
- Limit: Parallel worktrees multiply storage and dependency-sync time.
- Scaling path: Centralize environment management and prune worktree-local caches/venvs regularly.

## Dependencies at Risk

**Python/runtime floor limits contributor compatibility:**
- Risk: `requires-python = ">=3.13"` narrows supported dev environments.
- Impact: Onboarding friction and CI runner compatibility risk.
- Migration plan: Evaluate 3.11/3.12 support unless 3.13-only features are required.

**Critical external binaries are not preflight-validated:**
- Risk: ffmpeg/ffprobe absence fails at runtime; availability is not checked up front.
- Impact: Pipeline failures surface late in execution.
- Migration plan: Add startup preflight checks and explicit install docs bound to executable versions.

## Missing Critical Features

**No stable tracked execution entrypoint for extraction pipeline:**
- Problem: Core logic is in ignored worktrees rather than tracked application code.
- Blocks: Reliable CI execution, packaging, and reproducible team workflows.

**No CI/test automation for extraction and transcription flows:**
- Problem: Test harness and automated validation are absent in tracked code paths.
- Blocks: Safe refactors and quick detection of extraction regressions.

## Test Coverage Gaps

**Extraction pipeline and ffmpeg wrappers are untested:**
- What's not tested: command construction, keyframe report generation, and frame reduction behavior.
- Files: `02-worktrees/chat-extraction/chat-extraction.py`
- Risk: Silent output drift and runtime failures from small refactors.
- Priority: High

**Transcription model schema compatibility lacks checks in current tree:**
- What's not tested: model serialization and downstream contract compatibility.
- Files: `src/transcription/models.py`, `src/transcription/__init__.py`
- Risk: Consumer breakage when schema fields change.
- Priority: High

---

*Concerns audit: 2026-02-26*
