# Codebase Concerns

**Analysis Date:** 2026-02-21

## Tech Debt

**Worktree-only source of truth:**
- Issue: Tracked planning docs prescribe implementation paths inside ignored worktrees, so the main checkout cannot validate or execute those references.
- Files: `.gitignore`, `README.md`, `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STACK.md`, `.planning/codebase/CONVENTIONS.md`, `.planning/codebase/STRUCTURE.md`, `.planning/codebase/INTEGRATIONS.md`.
- Impact: Planning and execution can target files that do not exist in the current branch, causing broken automation and misleading implementation guidance.
- Fix approach: Either commit canonical source files in the main branch or regenerate `.planning/codebase/*.md` from files that exist in this checkout and gate mapping docs with path-existence validation.

**Data format inconsistency in extraction artifacts:**
- Issue: Files named `*.jsonl` are not line-delimited JSON; `00-supporting-files/data/extractions/metrics.jsonl` and `00-supporting-files/data/extractions/failed_extractions.jsonl` store pretty-printed concatenated JSON objects, while `00-supporting-files/data/extractions/extractions.jsonl` stores one large JSON array.
- Files: `00-supporting-files/data/extractions/extractions.jsonl`, `00-supporting-files/data/extractions/metrics.jsonl`, `00-supporting-files/data/extractions/failed_extractions.jsonl`.
- Impact: Standard JSONL tooling and streaming pipelines fail, increasing parser complexity and error risk.
- Fix approach: Normalize all extraction outputs to true JSONL (one compact JSON object per line) and add a schema/format validator in generation scripts.

## Known Bugs

**Extraction output duplication and missing frames:**
- Symptoms: Expected kept frames are `6543` (`00-supporting-files/data/chat_frames_full_color/report.json`), but only `6539` unique filenames appear in `00-supporting-files/data/extractions/extractions.jsonl`; missing frames include `frame_005220_t001740.000.png`, `frame_018816_t006272.000.png`, `frame_040791_t013597.000.png`, `frame_046417_t015472.333.png`.
- Files: `00-supporting-files/data/chat_frames_full_color/report.json`, `00-supporting-files/data/extractions/extractions.jsonl`, `00-supporting-files/data/extractions/failed_extractions.jsonl`.
- Trigger: Retry/append behavior records repeated extractions for the same filename and leaves gaps for some expected frames.
- Workaround: Post-process by deduplicating on `filename` and reconciling against frame report filenames before downstream use.

**Failed extraction log has duplicate and incomplete records:**
- Symptoms: `00-supporting-files/data/extractions/failed_extractions.jsonl` contains 5 records but only 2 unique filenames; `frame_040791_t013597.000.png` is logged 4 times and some missing output frames are not logged there.
- Files: `00-supporting-files/data/extractions/failed_extractions.jsonl`, `00-supporting-files/data/extractions/extractions.jsonl`, `00-supporting-files/data/chat_frames_full_color/report.json`.
- Trigger: Repeated retry failure appends duplicate rows and does not reliably capture every unrecovered frame.
- Workaround: Rebuild failure inventory by diffing expected frame list from `report.json` against unique extracted filenames.

**Long-tail model generation loop on wrapped text:**
- Symptoms: Model output can repeat trailing characters until token cap is hit (documented example with repeated `k` and `finish_reason: "length"`).
- Files: `00-dev-log/2026-02-09.md`, `00-supporting-files/images/2026-02-09/20260209234035_frame_018816_t006272.000.png`.
- Trigger: Frames with wrapped or ambiguous text cause runaway continuation behavior.
- Workaround: Prompt constraint (`"Transcribe exactly what’s visible; do not continue a pattern."`) and capped retry strategy documented in `00-dev-log/2026-02-09.md`.

## Security Considerations

**User-generated chat content stored in committed artifacts:**
- Risk: `00-supporting-files/data/extractions/extractions.jsonl` and `00-dev-log/2026-02-09.md` include raw usernames/messages, including profanity and potentially sensitive user text.
- Files: `00-supporting-files/data/extractions/extractions.jsonl`, `00-dev-log/2026-02-09.md`.
- Current mitigation: Not detected.
- Recommendations: Add redaction/anonymization before commit, and keep raw extraction outputs in untracked storage for private analysis.

**External dependency trust boundary via submodule:**
- Risk: `01-dev-onboarding` is sourced from an external repository with branch tracking (`master`), creating supply-chain and availability risk if upstream changes or disappears.
- Files: `.gitmodules`, `README.md`.
- Current mitigation: Submodule pinning is implicit in git metadata, but no documented validation process exists in tracked docs.
- Recommendations: Document integrity checks for submodule updates and record a fallback onboarding path in this repository.

## Performance Bottlenecks

**Extraction latency outliers dominate wall-clock runtime:**
- Problem: `00-supporting-files/data/extractions/metrics.jsonl` shows extreme per-frame outliers (for example `59567.825s` for `frame_006302_t002100.667.png`) while median latency is much lower.
- Files: `00-supporting-files/data/extractions/metrics.jsonl`.
- Cause: Retry/hang behavior on hard frames without strict per-request timeout and isolation.
- Improvement path: Enforce hard request timeout, circuit-breaker retry policy, and quarantine of pathological frames to a separate queue.

**Repository artifact growth from generated outputs:**
- Problem: Large generated files (for example `00-supporting-files/data/extractions/extractions.jsonl` ~16.5MB and `00-supporting-files/data/extractions/metrics.jsonl` ~2.5MB) are tracked in git.
- Files: `00-supporting-files/data/extractions/extractions.jsonl`, `00-supporting-files/data/extractions/metrics.jsonl`, `00-supporting-files/data/full_chat_frames_report.json`, `00-supporting-files/data/chat_frames_full_color/report.json`.
- Cause: Full-run artifacts are committed without archival or partitioning strategy.
- Improvement path: Keep only sampled fixtures in git, move full-run artifacts to ignored storage, and generate summaries for reproducible analysis.

## Fragile Areas

**Codebase maps can drift from actual checkout:**
- Files: `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STACK.md`, `.planning/codebase/CONVENTIONS.md`, `.planning/codebase/STRUCTURE.md`, `.planning/codebase/INTEGRATIONS.md`, `.gitignore`.
- Why fragile: These documents reference many worktree files not present in the current tree, so future automation can fail before implementation starts.
- Safe modification: Add a map-validation step that rejects docs containing non-existent required paths for the current branch.
- Test coverage: No automated validation detected for `.planning/codebase/*.md` path integrity.

## Scaling Limits

**Per-frame LLM extraction scales linearly with high token burn:**
- Current capacity: One processed run contains `9523` extraction records and `15,975,030` total tokens in `00-supporting-files/data/extractions/metrics.jsonl`.
- Limit: Throughput and cost increase linearly with frame count; retry outliers can dominate total runtime.
- Scaling path: Add upstream frame reduction/dedup before extraction, enforce bounded retries, and checkpoint progress in resumable batches.

## Dependencies at Risk

**`01-dev-onboarding` submodule availability:**
- Risk: Upstream repository availability and branch behavior can block onboarding flows.
- Impact: Setup paths documented in `README.md` can fail for fresh clones if submodule fetch or branch resolution fails.
- Migration plan: Mirror critical onboarding docs/scripts into tracked files in this repository and treat submodule as optional enhancement.

## Missing Critical Features

**No tracked runtime project files in the main branch checkout:**
- Problem: No tracked `pyproject.toml`, `package.json`, or executable source modules exist in the current branch, while planning docs assume active runtime code under `02-worktrees/`.
- Blocks: Reproducible environment setup and direct execution/validation from this checkout.

## Test Coverage Gaps

**No automated checks for extraction data integrity:**
- What's not tested: Uniqueness of extracted filenames, expected-vs-produced frame completeness, and failure-log consistency.
- Files: `00-supporting-files/data/chat_frames_full_color/report.json`, `00-supporting-files/data/extractions/extractions.jsonl`, `00-supporting-files/data/extractions/failed_extractions.jsonl`, `00-supporting-files/data/extractions/metrics.jsonl`.
- Risk: Silent data corruption (duplicates, missing frames, malformed JSONL) propagates into downstream analysis.
- Priority: High.

**No CI or test harness in tracked root:**
- What's not tested: Planning doc path validity, worktree assumptions, and schema/format compliance for generated artifacts.
- Files: `.planning/codebase/*.md`, `.planning/phases/01-template-preparation/01-01-PLAN.md`, `.planning/phases/01-template-preparation/01-UAT.md`.
- Risk: Operational drift accumulates until manual checks fail late.
- Priority: High.

---

*Concerns audit: 2026-02-21*
