# Codebase Concerns

**Analysis Date:** 2026-02-13

## Tech Debt

**No dependency management on template branches (master/vibe-coding):**
- Issue: No `requirements.txt`, `pyproject.toml`, `Pipfile`, or `setup.py` on the template branches. The `00-experiments` branch has `pyproject.toml` with uv.
- Files: Project root on template branches (missing file)
- Impact: Template branches have no dependency management — but this is by design since app code lives on experiment branches.
- Fix approach: Not needed for template branches. Experiment branches inherit `pyproject.toml` from `00-experiments`.

**No Python version pinned on template branches:**
- Issue: No `.python-version` on template branches. The `00-experiments` branch pins Python 3.13.
- Files: Project root on template branches (missing file)
- Impact: Not a concern — experiment branches inherit `.python-version` from `00-experiments`.
- Fix approach: Not needed for template branches.

## Known Bugs

**None detected** - no application code to have bugs.

## Security Considerations

**No secrets management pattern established:**
- Risk: As the project grows, developers may hardcode secrets without a clear pattern to follow.
- Files: `00-supporting-files/data/sample.env.file` (exists but no loading code)
- Current mitigation: `.env` is gitignored
- Recommendations: Add a secrets loading pattern (e.g., `python-dotenv` or `pydantic-settings`) in the application code. Document required environment variables in the sample env file.

**Git submodule from public repo:**
- Risk: `01-dev-onboarding` submodule points to public GitHub repo. Supply chain risk if repo is compromised.
- Files: `.gitmodules`
- Current mitigation: Pinned to `master` branch (but not a specific commit SHA)
- Recommendations: Consider pinning submodule to a specific commit SHA for reproducibility.

## Performance Bottlenecks

**None detected** - no application code exists.

## Fragile Areas

**Git submodule initialization:**
- Files: `.gitmodules`, `01-dev-onboarding/`
- Why fragile: Developers must remember to run `git submodule update --init --recursive` after cloning. Forgetting this leaves `01-dev-onboarding/` empty.
- Safe modification: Always test clone with `--recurse-submodules` flag
- Test coverage: None

## Scaling Limits

**None applicable** - project template, not a running system.

## Dependencies at Risk

**Git submodule `01-dev-onboarding`:**
- Risk: External repository dependency with no version pinning beyond branch name
- Impact: Breaking changes in the submodule propagate without warning
- Migration plan: Pin to specific commit SHA, or vendor the content directly

## Missing Critical Features

**No linter/formatter configuration:**
- Problem: Despite `.gitignore` entries for `ruff` and `mypy`, neither tool is configured
- Blocks: Consistent code style enforcement across contributors

**No test infrastructure:**
- Problem: No test framework, test directory, or test configuration exists on template branches
- Blocks: Not applicable at template level — test infrastructure should be set up per experiment branch

**No CI/CD pipeline:**
- Problem: No GitHub Actions workflows, no `Makefile`, no automation
- Blocks: Automated testing, linting, and deployment (out of scope for personal template)

**No `pyproject.toml` on template branches:**
- Problem: Template branches lack `pyproject.toml` — but `00-experiments` branch has one
- Blocks: Nothing — experiment branches inherit from `00-experiments`

## Test Coverage Gaps

**Not applicable at template level:**
- Template repo has no application code to test
- Test infrastructure should be set up per experiment branch
- The `00-experiments` branch could include a test skeleton as part of the template

---

*Concerns audit: 2026-02-13*
