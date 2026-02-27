# Codebase Concerns

**Analysis Date:** 2026-02-26

## Tech Debt

**Notebook-as-production pipeline:**
- Issue: Core extraction/transcription/segmentation orchestration lives in a tracked `.ipynb` JSON document, making refactors, code review, and safe diffs harder than module-based Python.
- Files: `02-worktrees/audio-extraction-review/audio-extraction.ipynb`
- Impact: High change risk for routine edits, difficult merge conflict resolution, and weak reuse from `src/` modules.
- Fix approach: Move executable pipeline logic into `src/` Python modules and keep the notebook as a thin orchestrator/visualization layer.

**Artifact/source-of-truth drift in committed data:**
- Issue: Run metadata points to artifacts not present in the repository snapshot.
- Files: `00-supporting-files/data/audio-extraction-review/runs/run-20260222T030354Z-206b1285.json`, `00-supporting-files/data/audio-extraction-review/transcripts`, `00-supporting-files/data/audio-extraction-review/logs`
- Impact: Reproducibility is degraded because historical runs cannot be revalidated from committed artifacts alone.
- Fix approach: Add a post-run integrity check that verifies every referenced path exists before run metadata is persisted.

**Incomplete packaging/runtime definition:**
- Issue: Tracked runtime behavior depends on optional notebook imports (`faster_whisper`, `whisperx`, `dotenv`) without a tracked root dependency manifest.
- Files: `02-worktrees/audio-extraction-review/audio-extraction.ipynb`, `src/transcription/models.py`
- Impact: Environment setup is brittle across machines and CI bootstrapping is ambiguous.
- Fix approach: Add a root `pyproject.toml` (or equivalent) that declares all runtime and optional extras used by tracked pipeline code.

## Known Bugs

**Batch segmentation export drops all but first successful transcript:**
- Symptoms: In multi-input runs, only the first successful segmentation result is exported to `segments.json`/`segments.md`.
- Files: `02-worktrees/audio-extraction-review/audio-extraction.ipynb`
- Trigger: `run_segment_export_stage()` sets `primary = successes[0]` and exports only that record.
- Workaround: Run segmentation one transcript at a time or manually merge records from segmentation logs.

**Run metadata may reference non-existent transcript/log artifacts:**
- Symptoms: A committed run references transcript/log paths that are absent from the tracked tree.
- Files: `00-supporting-files/data/audio-extraction-review/runs/run-20260222T030354Z-206b1285.json`, `00-supporting-files/data/audio-extraction-review/transcripts`, `00-supporting-files/data/audio-extraction-review/logs`
- Trigger: Metadata snapshots can be committed independently of full artifact sets.
- Workaround: Validate referenced files manually before using a run as baseline input.

**Segmentation can include stale transcripts from prior runs:**
- Symptoms: A run can segment transcripts not generated in the current extraction/transcription cycle.
- Files: `02-worktrees/audio-extraction-review/audio-extraction.ipynb`, `00-supporting-files/data/audio-extraction-review/transcripts`
- Trigger: `collect_transcript_records_for_segmentation()` reuses all files matching `reuse_transcript_glob` in `transcripts_dir`.
- Workaround: Disable checkpoint reuse (`allow_transcript_checkpoint_reuse=False`) when strict run isolation is required.

## Security Considerations

**Local path disclosure in committed artifacts:**
- Risk: Absolute host paths are persisted in logs/runs and expose workstation directory structure.
- Files: `00-supporting-files/data/audio-extraction-review/runs/run-20260222T023330Z-f9bdbf0d.json`, `00-supporting-files/data/audio-extraction-review/logs/extraction-20260222T023330Z-f9bdbf0d.jsonl`
- Current mitigation: None detected beyond normal git hygiene.
- Recommendations: Persist project-relative paths in committed artifacts; keep absolute paths only in local, ignored debug outputs.

**Credential-loading flow without strict source controls:**
- Risk: Notebook logic auto-loads `.env` if present and expects API tokens for optional stages.
- Files: `02-worktrees/audio-extraction-review/audio-extraction.ipynb`, `00-supporting-files/data/sample.env.file`, `00-supporting-files/data/.env` (present)
- Current mitigation: `.env` is gitignored by `.gitignore`.
- Recommendations: Restrict to an explicit allowlisted env file path for local runs and fail fast if unexpected env sources are detected.

## Performance Bottlenecks

**Chunking implementation re-scans all transcript segments per window:**
- Problem: Window generation performs repeated full-list scans in `chunk_transcript_for_segmentation()`.
- Files: `02-worktrees/audio-extraction-review/audio-extraction.ipynb`
- Cause: `while` loop plus list-comprehension over all segments for each cursor step creates avoidable O(n*windows) behavior.
- Improvement path: Use a two-pointer/sliding-window index to avoid rescanning already-past segments.

**Segmentation requests are strictly serial per chunk:**
- Problem: Large transcripts incur linear wall-clock delay from sequential HTTP calls.
- Files: `02-worktrees/audio-extraction-review/audio-extraction.ipynb`
- Cause: `run_segmentation_stage()` loops through chunks and calls `llm_segment_chunk()` one-by-one.
- Improvement path: Add bounded concurrency with retry/backoff and deterministic ordering on response merge.

## Fragile Areas

**Pipeline control flow duplicated across smoke checks:**
- Files: `02-worktrees/audio-extraction-review/audio-extraction.ipynb`
- Why fragile: `local_model_smoke_check()` is called both in `run_pipeline()` and `run_segmentation_stage()`, creating duplicated branching and possible divergence.
- Safe modification: Centralize smoke-check gating in one place and make stage functions assume validated prerequisites.
- Test coverage: No automated tests currently validate these branches.

**Regex-based markdown reload parser tightly coupled to exact output format:**
- Files: `02-worktrees/audio-extraction-review/audio-extraction.ipynb`, `00-supporting-files/data/audio-extraction-review/segments/segments.md`
- Why fragile: Small markdown formatting changes can silently break `load_segments_from_markdown()` parsing behavior.
- Safe modification: Treat JSON as canonical and reduce markdown parsing to optional diagnostics.
- Test coverage: No parser regression tests detected.

## Scaling Limits

**Repository growth driven by committed binary artifacts:**
- Current capacity: Tracked support data already contains many audio/image artifacts under `00-supporting-files/data`.
- Limit: Git history and clone/pull cost increase quickly as run artifacts and media derivatives accumulate.
- Scaling path: Move heavy artifacts to object storage or release assets and keep only lightweight manifests/checksums in git.

**Single-machine local inference throughput:**
- Current capacity: Pipeline defaults to CPU transcription and localhost model endpoint assumptions.
- Limit: End-to-end latency scales poorly for longer media or batch runs.
- Scaling path: Add queue-based job execution with configurable workers and optional GPU-aware profiles.

## Dependencies at Risk

**Optional diarization stack not guaranteed in runtime:**
- Risk: Diarization behavior degrades to `UNKNOWN` when required libraries/tokens are unavailable.
- Impact: Speaker attribution quality is inconsistent across environments.
- Migration plan: Declare `whisperx`/`pyannote` as optional extras and gate runs with explicit capability checks before execution.

## Missing Critical Features

**No CLI/service entrypoint for tracked `src/transcription` package:**
- Problem: `src/transcription` currently exposes models only, with no stable executable interface for pipeline runs.
- Blocks: Reliable automation in CI and repeatable non-notebook execution.

**No automated integrity verification command for committed run artifacts:**
- Problem: Artifact references can drift from file reality without a guardrail.
- Blocks: Trustworthy reuse of prior run metadata in planning/execution workflows.

## Test Coverage Gaps

**No automated tests for pipeline stages and validations:**
- What's not tested: Extraction/transcription/segmentation flows, overlap normalization, export/reload integrity, and failure-path handling.
- Files: `02-worktrees/audio-extraction-review/audio-extraction.ipynb`, `src/transcription/models.py`
- Risk: Regressions in stage orchestration and data contracts can ship unnoticed.
- Priority: High

**No tests for schema/model compatibility with generated artifacts:**
- What's not tested: Whether transcript artifacts in `00-supporting-files/data/audio-extraction-review/transcripts` continue to satisfy model expectations from `src/transcription/models.py`.
- Files: `src/transcription/models.py`, `00-supporting-files/data/audio-extraction-review/transcripts/sample-single.json`
- Risk: Runtime validation or downstream processing failures during format evolution.
- Priority: Medium

---

*Concerns audit: 2026-02-26*
