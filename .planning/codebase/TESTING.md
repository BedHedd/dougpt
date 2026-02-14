# Testing Patterns

**Analysis Date:** 2026-02-13

## Test Framework

**Runner:**
- None configured
- No test framework installed or configured
- No `pytest.ini`, `pyproject.toml`, `setup.cfg`, `tox.ini`, or `conftest.py` detected

**Assertion Library:**
- None

**Run Commands:**
```bash
# No test commands configured
# .gitignore includes entries for pytest (.pytest_cache/), tox (.tox/), nox (.nox/),
# coverage (.coverage, htmlcov/, coverage.xml), and hypothesis (.hypothesis/),
# suggesting pytest is the intended test framework
```

## Test File Organization

**Location:**
- No test files exist

**Naming:**
- Not yet established

**Structure:**
- Not yet established

## Recommended Setup

Based on `.gitignore` entries referencing pytest, coverage, hypothesis, tox, and nox, the intended testing stack is:

```bash
# Install pytest (recommended based on gitignore patterns)
pip install pytest pytest-cov

# Run tests (on experiment branches — no app code on template branches)
pytest tests/

# Run with coverage
pytest --cov --cov-report=html tests/
```

## Test Structure

**Suite Organization:**
- Not yet established

## Mocking

**Framework:** Not configured

**Patterns:**
- Not yet established

## Fixtures and Factories

**Test Data:**
- `00-supporting-files/data/` directory exists and could house test fixtures
- No test data files present

**Location:**
- Not yet established

## Coverage

**Requirements:** None enforced
**Tools referenced in `.gitignore`:** `.coverage`, `htmlcov/`, `coverage.xml`, `*.cover`, `*.py,cover`

## Test Types

**Unit Tests:**
- None exist

**Integration Tests:**
- None exist

**E2E Tests:**
- None exist

## Where to Add Tests

**When creating tests, follow this pattern (on experiment branches):**
1. Create a `tests/` directory at the branch root
2. Name test files `test_<module>.py` (pytest convention)
3. Use `conftest.py` for shared fixtures
4. Place test data in `tests/fixtures/` or `00-supporting-files/data/`

---

*Testing analysis: 2026-02-13*
