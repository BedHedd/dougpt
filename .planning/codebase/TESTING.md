# Testing Patterns

**Analysis Date:** 2026-02-26

## Test Framework

**Runner:**
- Not detected (no `pytest`, `unittest`, `nose`, `tox`, `vitest`, or `jest` config found in repo root or `02-worktrees/chat-extraction`).
- Config: Not detected.

**Assertion Library:**
- Not detected.

**Run Commands:**
```bash
Not applicable: no automated test runner configured in `pyproject.toml` at `02-worktrees/chat-extraction/pyproject.toml`
Not applicable: no watch-mode test runner configured
Not applicable: no coverage command configured
```

## Test File Organization

**Location:**
- No dedicated `tests/` directory detected.
- Validation and experimentation are embedded as marimo cells in `02-worktrees/chat-extraction/chat-extraction.py`.

**Naming:**
- No `*.test.py` or `*_test.py` files detected.
- Exploratory sections are named with markdown headers inside cells (for example `# tests with chat extraction` and `# batch processing tests`) in `02-worktrees/chat-extraction/chat-extraction.py`.

**Structure:**
```
02-worktrees/chat-extraction/
└── chat-extraction.py   # marimo notebook export containing manual validation cells
```

## Test Structure

**Suite Organization:**
```python
@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## using a compressed frame
    """)

@app.cell
def _(Markdown, client, compressed_frame, image_file_to_data_url):
    _resp = client.chat.completions.create(...)
    print(_resp.choices[0].message.content)
    Markdown(_resp.choices[0].message.content)
```

**Patterns:**
- Setup pattern: assemble inputs and clients in earlier cells (`client`, `compressed_frame`, `source_frame`) before verification cells in `02-worktrees/chat-extraction/chat-extraction.py`.
- Teardown pattern: Not explicit; tests are stateless cell executions with artifact files written to `00-supporting-files/data/...` paths from `02-worktrees/chat-extraction/chat-extraction.py`.
- Assertion pattern: visual/manual assertion via printed model output, rendered markdown, and generated artifacts (`report.json`, saved PNGs) in `02-worktrees/chat-extraction/chat-extraction.py`.

## Mocking

**Framework:** Not detected

**Patterns:**
```python
# Not used: calls target local model endpoints directly
client = OpenAI(base_url="http://localhost:1234/v1", api_key="unused")
resp = client.chat.completions.create(...)
```

**What to Mock:**
- For future automated tests, mock `subprocess.run` and `subprocess.Popen` used in ffprobe/ffmpeg paths in `02-worktrees/chat-extraction/chat-extraction.py`.
- Mock OpenAI client responses for `client.chat.completions.create` and `client.beta.chat.completions.parse` in `02-worktrees/chat-extraction/chat-extraction.py`.

**What NOT to Mock:**
- Do not mock pure data transforms (`_safe_clamped_bbox`, `_parse_packets_pts`, `_parse_frames_ts`) in `02-worktrees/chat-extraction/chat-extraction.py`; these should be unit-tested with real inputs.

## Fixtures and Factories

**Test Data:**
```python
FRAMES_DIR = supporting_files / "data" / "chat_frames_test_30s_color"
next_example = supporting_files / "images" / "2026-01-12" / "20260112200709.png"
```

**Location:**
- Image and report fixtures live under `00-supporting-files/data/` and `00-supporting-files/images/`, referenced from `02-worktrees/chat-extraction/chat-extraction.py`.

## Coverage

**Requirements:** None enforced

**View Coverage:**
```bash
Not applicable: no coverage tool configured
```

## Test Types

**Unit Tests:**
- Not implemented as standalone test files.
- Unit-like checks are done interactively by calling helper functions and inspecting outputs in `02-worktrees/chat-extraction/chat-extraction.py`.

**Integration Tests:**
- Present as manual integrations against real dependencies (ffmpeg binaries, local OpenAI-compatible endpoint) in `02-worktrees/chat-extraction/chat-extraction.py`.

**E2E Tests:**
- Not used.

## Common Patterns

**Async Testing:**
```python
# Not detected; calls are synchronous
resp = client.chat.completions.create(...)
```

**Error Testing:**
```python
if not in_p.exists():
    raise FileNotFoundError(f"Input not found: {in_p}")

except subprocess.CalledProcessError as e:
    raise RuntimeError(f"Command failed:\n{' '.join(cmd)}\n\n{e.stderr.strip()}") from e
```

---

*Testing analysis: 2026-02-26*
