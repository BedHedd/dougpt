# Codebase Concerns

**Analysis Date:** 2026-02-21

## Tech Debt

**Monolithic notebook code:** `02-worktrees/chat-extraction/chat-extraction.py` is a 4.5k-line marimo notebook that mixes UI cells, data samples, ffmpeg helpers, and model calls in one file, making it hard to reason about or reuse. Refactor into modules (I/O, vision extraction, model prompts) and move static sample outputs into fixtures or JSON under `00-supporting-files/data`.
**Hard-coded paths & project discovery:** Multiple cells derive paths by searching for `00-supporting-files` and assume a sibling `large-files` directory with specific video names (e.g., `Doug and Twitch Chat TAKE OVER EUROPE-VpmmuHlLPM0.mkv`). Running outside this repo structure raises `StopIteration` before any work starts. Add explicit configuration (env/CLI args) and clear errors when required assets are missing.
**Stale duplicate copy:** An older copy lives at `02-worktrees/old-master/02-development/chat-extraction/chat-extraction.py`, risking drift between worktrees. Consolidate to a single maintained module and delete or archive the obsolete variant.
**Missing configuration loading:** `dotenv` is imported but never invoked; API hosts, model names, and paths are hard-coded in the notebook. Wire configuration through environment variables and load them explicitly at startup.

## Known Bugs

**Undefined variables in ffmpeg cell:** `02-worktrees/chat-extraction/chat-extraction.py:88` references `p`, `shlex`, and `subprocess` without defining or importing them, so executing the cell throws `NameError`. Remove the cell or add the missing imports and inputs.
**Unreleased video handles:** `02-worktrees/chat-extraction/chat-extraction.py:213-239` opens a `cv2.VideoCapture` without closing it; repeated runs can leak file descriptors. Ensure captures are released via `with`-style helpers or explicit `release()`.
**Asset assumptions without guards:** Keyframe inspection cells (`02-worktrees/chat-extraction/chat-extraction.py:3389-3452`, `4188-4190`) expect specific video files and cached reports to exist; when absent, they fail without actionable messaging. Add existence checks and user-facing errors.

## Security Considerations

**Insecure default API target:** OpenAI client construction in `02-worktrees/chat-extraction/chat-extraction.py:344-380` uses `http://localhost:1234/v1` with no TLS or timeout, so accidental port exposure would transmit frames in cleartext or hang indefinitely. Parameterize the base URL, enforce HTTPS for remote hosts, and set conservative timeouts.
**User data embedded in repo:** Sample Twitch chat frames and extracted text live under `00-supporting-files/data` and inline dictionaries (e.g., `qwen3_vl_30b_resp`), storing usernames and messages in git. If distribution is a concern, move samples to redacted fixtures or exclude them from the main history.

## Performance Bottlenecks

**Full-video decoding in Python loop:** `reduce_chat_frames_by_scroll_color` (`02-worktrees/chat-extraction/chat-extraction.py:4300-4502`) streams entire videos through ffmpeg into Python, iterating frame-by-frame and optionally writing PNGs. Long videos will be CPU- and disk-heavy, and `kept` accumulates in memory. Consider downsampling earlier, chunked processing, and streaming results to disk without retaining full history.
**Huge inline sample payloads:** Large hard-coded response dictionaries (e.g., `qwen3_vl_30b_resp` around `02-worktrees/chat-extraction/chat-extraction.py:1781`) inflate load time and memory for the notebook. Externalize samples to data files and lazy-load only when needed.

## Fragile Areas

**External tooling assumptions:** Many cells call `ffmpeg` and VAAPI-specific options (`02-worktrees/chat-extraction/chat-extraction.py:3380-3468`, `4305-4350`) without checking tool availability or GPU support, leading to abrupt failures on machines without those binaries/drivers. Add capability checks and graceful fallbacks.
**Unbounded cache/output writes:** Frame extraction writes to tracked directories such as `00-supporting-files/data/chat_frames_test_30s_color` and `.../cropped_keyframe_cache` without cleanup or size limits. Large runs will bloat the repo and consume disk; direct outputs to git-ignored temp dirs and prune after runs.

## Scaling Limits

**Single-threaded, in-memory processing:** Extraction flows (`02-worktrees/chat-extraction/chat-extraction.py:4300-4502`) operate serially and store metadata for every kept frame, limiting throughput for multi-hour videos. Introduce batched processing, progress checkpoints, and streaming metadata to disk to handle larger corpora.
**Manual notebook workflow only:** All functionality is embedded in an interactive marimo notebook with no CLI or pipeline hooks, blocking automation or batch scaling. Extract reusable functions into a package and provide a script/CLI entry point.

## Dependencies at Risk

**System ffmpeg and OpenCV coupling:** Functions depend on system `ffmpeg` and `opencv-python` (`02-worktrees/chat-extraction/chat-extraction.py:3380-3468`, `213-239`) with no version pin or feature detection; differing builds (e.g., missing AV1/VAAPI) will break extraction. Pin tested versions in `pyproject.toml`/`uv.lock` and add runtime capability checks.
**Marimo-only orchestration:** The notebook relies on marimo execution order (`02-worktrees/chat-extraction/chat-extraction.py`) rather than importable modules, so library upgrades or marimo API changes can silently break cells. Stabilize on a tested marimo version and migrate shared logic into plain Python modules.

## Missing Critical Features

**No reproducible pipeline:** There is no scripted path to go from raw video to extracted chat text; everything is manual cell execution. Provide a documented CLI that ingests a video path, extracts frames, and runs the VLM with configurable parameters and outputs.
**Lack of validation/QA:** Model outputs are not checked against any ground truth; stored samples are anecdotal. Add small labeled fixtures under `00-supporting-files/data/extractions` and assertions to measure accuracy and bounding-box consistency.

## Test Coverage Gaps

**No automated tests:** The repository has no unit or integration tests covering ffmpeg helpers, frame selection heuristics, or OpenAI client code (`02-worktrees/chat-extraction/chat-extraction.py`, `pyproject.toml`). Introduce at least smoke tests for frame extraction and deterministic parsing, and mock API calls to keep tests offline.

---

*Concerns audit: 2026-02-21*
