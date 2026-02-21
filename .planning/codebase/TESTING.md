# Testing Patterns

**Analysis Date:** 2026-02-21

## Test Framework

**Runner:**
- Not detected for automated code tests in current codebase.
- Config: Not detected (`pytest.ini`, `tox.ini`, `jest.config.*`, `vitest.config.*` are absent in `/home/bedhedd/Documents/development_projects/bedhedd_projects/dougpt/dougpt`).

**Assertion Library:**
- Built-in Python `assert` is used in documented one-liner checks inside planning/UAT docs (`.planning/phases/01-template-preparation/01-01-PLAN.md`).

**Run Commands:**
```bash
# Automated unit/integration suite
Not applicable (no test runner configured)

# Manual template substitution verification
python3 -c "from string import Template; t = Template(open('02-worktrees/00-experiments/README.md').read()); r = t.safe_substitute(project_name='Test', description='A test project', branch_name='test-branch', created_date='2026-01-01'); assert '$project_name' not in r"

# Manual UAT evidence location
Read .planning/phases/01-template-preparation/01-UAT.md
```

## Test File Organization

**Location:**
- No `*.test.*`, `*.spec.*`, `test_*.py`, or `*_test.py` files are detected in `/home/bedhedd/Documents/development_projects/bedhedd_projects/dougpt/dougpt`.
- Manual acceptance tests are documented in `.planning/phases/01-template-preparation/01-UAT.md`.

**Naming:**
- UAT files follow phase naming pattern `{phase-id}-UAT.md` and `{phase-id}-{plan-id}-PLAN.md` (for example `.planning/phases/01-template-preparation/01-UAT.md`).

**Structure:**
```
.planning/phases/<phase-name>/
  <phase>-<plan>-PLAN.md
  <phase>-<plan>-SUMMARY.md
  <phase>-UAT.md
```

## Test Structure

**Suite Organization:**
```typescript
### 1. <Behavior being validated>
expected: <deterministic command and expected output>
result: pass|fail
```

**Patterns:**
- Setup pattern: define explicit shell/python command and expected observable output in plan docs (`.planning/phases/01-template-preparation/01-01-PLAN.md`).
- Teardown pattern: verify clean git status (`git -C 02-worktrees/00-experiments status --porcelain`) documented in `.planning/phases/01-template-preparation/01-01-PLAN.md`.
- Assertion pattern: use direct `assert` checks in Python one-liners and mark `result: pass` in UAT (`.planning/phases/01-template-preparation/01-UAT.md`).

## Mocking

**Framework:** Not used

**Patterns:**
```typescript
Not applicable: no unittest/pytest mocking fixtures or mock libraries detected.
```

**What to Mock:**
- No established code-test mock boundary exists yet; current checks validate generated template output directly (`.planning/phases/01-template-preparation/01-01-PLAN.md`).

**What NOT to Mock:**
- Do not mock template substitution behavior when validating `string.Template.safe_substitute()`; run it directly against `02-worktrees/00-experiments/README.md` as shown in `.planning/phases/01-template-preparation/01-01-PLAN.md`.

## Fixtures and Factories

**Test Data:**
```typescript
project_name='Test Project'
description='A test'
branch_name='test-branch'
created_date='2026-01-01'
```

**Location:**
- Inline in test command snippets within `.planning/phases/01-template-preparation/01-01-PLAN.md`.

## Coverage

**Requirements:**
- None enforced: no coverage tool config (`coverage.py`, `pytest-cov`, nyc, lcov) is detected in `/home/bedhedd/Documents/development_projects/bedhedd_projects/dougpt/dougpt`.

**View Coverage:**
```bash
Not applicable (no coverage pipeline configured)
```

## Test Types

**Unit Tests:**
- Not used in executable source directories (`02-worktrees/chat-extraction/`, `02-worktrees/old-master/03-app/`).

**Integration Tests:**
- Manual integration checks are documented as command-based acceptance criteria in `.planning/phases/01-template-preparation/01-01-PLAN.md` and reported in `.planning/phases/01-template-preparation/01-UAT.md`.

**E2E Tests:**
- Not used.

## Common Patterns

**Async Testing:**
```typescript
Not detected: no async test framework usage.
```

**Error Testing:**
```typescript
# Pattern documented in plan: assertions fail with explicit messages
assert data['project']['readme'] == 'README.md', 'readme field mismatch'
```

---

*Testing analysis: 2026-02-21*
