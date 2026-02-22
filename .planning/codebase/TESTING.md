# Testing Patterns

**Analysis Date:** 2026-02-21

## Test Framework

**Runner:**
- Not detected; no pytest/unittest configuration in `pyproject.toml` under `02-worktrees/chat-extraction` or `02-worktrees/old-master`.

**Assertion Library:**
- Not applicable (no test suite present).

**Run Commands:**
```bash
# Not configured (no test runner defined)
```

## Test File Organization

**Location:**
- No test files in the repository; introduce new tests under `02-worktrees/chat-extraction/tests/` or co-located `test_*.py` files alongside modules such as `02-worktrees/chat-extraction/chat-extraction.py`.

**Naming:**
- Not established; adopt pytest-style `test_*.py` and `Test*` classes for future work.

**Structure:**
```
# Not defined; prefer pytest modules grouped by feature under tests/
```

## Test Structure

**Suite Organization:**
```
# None implemented; use pytest functions or classes with fixtures when added
```

**Patterns:**
- Setup/Teardown: Not defined; use pytest fixtures for shared paths (e.g., sample frame directories) when tests are created.
- Assertion: No pattern; prefer explicit `assert` statements with clear failure messages.
- Async: Not in use; handle sync I/O only.

## Mocking

**Framework:**
- None in use; future tests can rely on `unittest.mock` or `pytest` monkeypatching for OpenAI clients and filesystem access.

**Patterns:**
```
# No mocking examples; wrap external services (OpenAI, subprocess, file I/O) behind fixtures for determinism
```

**What to Mock:**
- External APIs (`openai.OpenAI`), subprocess invocations (`subprocess.run` for FFmpeg), and filesystem-heavy operations when adding tests.

**What NOT to Mock:**
- Pure data formatting helpers and Pydantic models once they are enabled.

## Fixtures and Factories

**Test Data:**
```
# None present; create fixtures for sample frames under 02-worktrees/chat-extraction/tests/data/
```

**Location:**
- Not defined; co-locate fixtures with tests or under `02-worktrees/chat-extraction/tests/data/` for reproducible assets.

## Coverage

**Requirements:**
- None enforced; no coverage tools configured.

**View Coverage:**
```bash
# Add pytest-cov and run: uv run pytest --cov=chat_extraction --cov-report=term-missing
```

## Test Types

**Unit Tests:**
- Not present; add around isolated helpers once extracted from `02-worktrees/chat-extraction/chat-extraction.py`.

**Integration Tests:**
- Not present; consider validating OpenAI response parsing with recorded fixtures.

**E2E Tests:**
- Not used; manual marimo execution only.

## Common Patterns

**Async Testing:**
```
# Not applicable; codebase is synchronous
```

**Error Testing:**
```
# Not implemented; add tests asserting failures when frames or API responses are missing
```

---

*Testing analysis: 2026-02-21*
