# Stack Research

**Project:** Project Template Workflow (git worktree automation)
**Researched:** 2026-02-13
**Overall confidence:** HIGH

## Executive Summary

This project automates three operations when creating new experiment/feature branches: (1) branch from `00-experiments` and create a worktree in `02-worktrees/`, (2) update `pyproject.toml`'s `name` field to match the new project, and (3) populate a README with project context. The automation is invoked by the GSD AI workflow system (Claude/Codex), not by human CLI users.

The stack should be **zero-dependency shell scripts + Python stdlib**. The operations are simple enough that adding libraries like GitPython, tomlkit, or Jinja2 would be over-engineering. Git's CLI is the authoritative interface for worktree management, Python's `re` module handles single-field TOML edits, and `string.Template` from stdlib handles README templating.

## Recommended Stack

### Git Worktree Automation

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| `git` CLI via `subprocess` | 2.51.2 (installed) | Branch creation, worktree add/list/remove | Git CLI is the only reliable interface for worktrees. No Python library wraps worktree commands well. `--porcelain` flag gives machine-parseable output. |
| `subprocess.run()` | Python 3.13 stdlib | Execute git commands from Python | `capture_output=True, text=True, check=True` gives clean error handling. No dependency needed. |

**Approach: Shell-first, Python-optional.**

The GSD orchestrator (Claude/Codex) already executes shell commands natively. The automation can be a simple bash script or a Python script that calls git via subprocess. Given that the GSD system works through tool calls (Bash, Edit, Write), the most natural implementation is:

```bash
# Core workflow (3 commands):
git checkout -b <branch-name> 00-experiments
git worktree add 02-worktrees/<branch-name> <branch-name>
# Then file edits (pyproject.toml, README.md) in the worktree
```

**Why subprocess over GitPython:**
- GitPython is in **maintenance mode** (explicitly stated on PyPI: "no feature development, no bug fixes unless safety-critical"). It was designed before modern git features and leaks system resources.
- GitPython's worktree support is limited — it wraps `git worktree list` but the `add` command requires falling back to `git.cmd` anyway.
- `subprocess.run(['git', 'worktree', 'add', ...])` is 1 line, zero dependencies, and uses the same git version the user has.
- For a personal template repo, the overhead of GitPython (208KB wheel + gitdb + smmap dependencies) is unjustified.

**Porcelain parsing for validation:**

```python
import subprocess

def list_worktrees(repo_path: str) -> list[dict]:
    """Parse git worktree list --porcelain into structured data."""
    result = subprocess.run(
        ['git', 'worktree', 'list', '--porcelain'],
        capture_output=True, text=True, check=True,
        cwd=repo_path
    )
    worktrees = []
    current = {}
    for line in result.stdout.strip().split('\n'):
        if line == '':
            if current:
                worktrees.append(current)
                current = {}
        elif line.startswith('worktree '):
            current['path'] = line[9:]
        elif line.startswith('HEAD '):
            current['head'] = line[5:]
        elif line.startswith('branch '):
            current['branch'] = line[7:]
    if current:
        worktrees.append(current)
    return worktrees
```

### pyproject.toml Management

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| `re` (regex) | Python 3.13 stdlib | Replace `name` field value in pyproject.toml | Single-field replacement preserves all formatting. No dependency needed. |
| `tomllib` (stdlib, read-only) | Python 3.13 stdlib | Validate TOML after edit (optional) | Read-only parser in stdlib since Python 3.11. Use for validation, not for writing. |

**Approach: Targeted regex replacement, not full parse-modify-write.**

The pyproject.toml on `00-experiments` is simple (11 lines). We only need to change the `name` field. A full parse-modify-write cycle (tomlkit/tomli_w) is unnecessary and risks reformatting the file.

```python
import re
from pathlib import Path

def update_project_name(pyproject_path: Path, new_name: str) -> None:
    """Update the project name in pyproject.toml, preserving all formatting."""
    content = pyproject_path.read_text()
    updated = re.sub(
        r'^(name\s*=\s*)"[^"]*"',
        rf'\1"{new_name}"',
        content,
        count=1,
        flags=re.MULTILINE
    )
    if updated == content:
        raise ValueError(f"Could not find name field in {pyproject_path}")
    pyproject_path.write_text(updated)
```

**Why not tomlkit:**
- tomlkit (0.14.0, actively maintained by Poetry team) is the gold standard for style-preserving TOML edits. It's a real parser that preserves comments, whitespace, and ordering.
- **But it's overkill here.** We're changing one field (`name`) in a simple file. Regex does this in 3 lines with zero dependencies.
- If the project later needs to add/remove dependencies programmatically (manipulating arrays, adding sections), tomlkit becomes worth it. For now, it doesn't.

**Why not tomli-w:**
- tomli-w (1.2.0) is a write companion to tomllib. It serializes a Python dict to TOML.
- **It does NOT preserve formatting.** Round-tripping through `tomllib.loads()` → modify → `tomli_w.dumps()` will reformat the file (different quoting, ordering, whitespace).
- Only use tomli-w if you're generating TOML from scratch, not editing existing files.

**Why not sed:**
- `sed` works but is less portable across macOS (BSD sed) vs Linux (GNU sed). The `-i` flag behaves differently.
- Python regex is consistent everywhere and easier to test.

### README Templating

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| `string.Template` | Python 3.13 stdlib | Populate README placeholders with project context | `$variable` syntax is clean in Markdown. `safe_substitute()` leaves unresolved placeholders intact. Zero dependencies. |

**Approach: Template file on `00-experiments` branch with `$placeholder` variables.**

Create a `README.md` on the `00-experiments` branch as a template:

```markdown
# $project_name

## Overview

$description

## Getting Started

### Prerequisites

- Python $python_version
- [uv](https://docs.astral.sh/uv/) package manager

### Setup

```bash
uv sync
```

## Branch Info

- **Branch:** `$branch_name`
- **Parent:** `$parent_branch`
- **Created:** $created_date
```

Then populate on branch creation:

```python
from string import Template
from pathlib import Path
from datetime import date

def populate_readme(readme_path: Path, context: dict) -> None:
    """Replace $placeholders in README template with project context."""
    template = Template(readme_path.read_text())
    readme_path.write_text(template.safe_substitute(context))
```

**Why not Jinja2:**
- Jinja2 (3.1.6) is a full templating engine with inheritance, macros, filters, loops, conditionals, and autoescaping.
- A README template has ~5 variable substitutions. Jinja2's `{{ variable }}` syntax also conflicts with code blocks in Markdown that show curly braces.
- Adding Jinja2 (134KB wheel + MarkupSafe dependency) for string interpolation is over-engineering.

**Why not f-strings or `.format()`:**
- f-strings require the template to be Python code, not a standalone file.
- `.format()` uses `{variable}` syntax which conflicts with JSON/code blocks in Markdown.
- `string.Template` uses `$variable` which has no conflicts in Markdown and reads naturally.

### Supporting Infrastructure

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| `pathlib.Path` | Python 3.13 stdlib | File path manipulation | Modern, cross-platform, already standard in Python 3.13 |
| `datetime.date` | Python 3.13 stdlib | Timestamps for README metadata | `date.today().isoformat()` |
| `argparse` or script args | Python 3.13 stdlib | CLI interface (if making a standalone script) | Only if wrapping as a reusable script. GSD may just inline the commands. |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Git automation | `subprocess` + git CLI | GitPython 3.1.46 | Maintenance mode, resource leaks, poor worktree support, unnecessary dependency |
| TOML editing | `re` (regex) | tomlkit 0.14.0 | Overkill for single-field replacement; revisit if manipulating dependencies |
| TOML editing | `re` (regex) | tomli-w 1.2.0 | Does NOT preserve formatting; only for generating TOML from scratch |
| TOML editing | `re` (regex) | `sed` | BSD/GNU portability issues on macOS vs Linux |
| README templating | `string.Template` | Jinja2 3.1.6 | Overkill; `{{ }}` syntax conflicts with Markdown code blocks |
| README templating | `string.Template` | `.format()` | `{}` syntax conflicts with JSON/code blocks in Markdown |
| README templating | `string.Template` | Cookiecutter | Project scaffolding tool — wrong scope. We're populating a single file, not generating a project tree. |

## What NOT to Use

### GitPython — Don't add it
- **Why:** Explicitly in maintenance mode. The maintainer says "no feature development, no bug fixes unless safety-critical." Multiple yanked releases show instability history. It leaks system resources (documented limitation). Its worktree support requires falling back to raw git commands anyway.
- **Instead:** `subprocess.run(['git', ...])` — direct, zero-dependency, uses the user's git version.

### Cookiecutter / Copier / Yeoman — Don't use project scaffolding tools
- **Why:** These are designed for generating entire project trees from templates. We're populating 2 files (README.md, pyproject.toml) on an existing branch. Using a scaffolding tool to substitute 5 variables is a category error.
- **Instead:** `string.Template` + `re.sub()` — 10 lines of code total.

### tomli-w for editing existing TOML — Don't round-trip through it
- **Why:** `tomllib.loads()` → modify dict → `tomli_w.dumps()` will reformat the entire file. Comments are lost (tomllib doesn't parse them), whitespace changes, array formatting changes. The diff will show every line modified when only one field changed.
- **Instead:** `re.sub()` for targeted edits. Use tomli-w only if generating TOML files from scratch.

### Click / Typer for CLI — Don't add CLI frameworks
- **Why:** The GSD orchestrator invokes automation through tool calls (Bash, Edit, Write), not through a CLI. A CLI framework adds dependency weight for zero benefit. If a human needs to run it, `argparse` (stdlib) or positional shell args suffice.
- **Instead:** Positional arguments or a simple function that the GSD system calls inline.

### pre-commit hooks for automation — Don't use hooks for this
- **Why:** The automation needs to run once (at branch creation time), not on every commit. Hooks are the wrong trigger mechanism. They also add friction if someone just wants to make a normal commit.
- **Instead:** A script/function invoked explicitly by GSD during project initialization.

## Installation

```bash
# No installation needed. Everything uses Python 3.13 stdlib + git CLI.
# Zero additional dependencies required.
```

If the project later needs tomlkit (for dependency manipulation):

```bash
# Only add if/when needed for complex TOML edits
uv add --dev tomlkit
```

## Implementation Shape

The automation is ~50 lines of Python or ~20 lines of bash. Here's the logical flow:

```
1. git checkout -b <branch-name> 00-experiments
2. git worktree add 02-worktrees/<branch-name> <branch-name>
3. In worktree: re.sub() name in pyproject.toml
4. In worktree: string.Template.safe_substitute() on README.md
5. In worktree: git add + git commit
```

This can be:
- **A bash script** (`scripts/new-project.sh`) called by GSD
- **A Python script** (`scripts/new_project.py`) called by GSD
- **Inline commands** that GSD executes directly via tool calls

Given the GSD model profile is Codex/Copilot (which executes bash/python natively), inline commands may be sufficient — no script file needed.

## Confidence Levels

| Recommendation | Confidence | Basis |
|----------------|------------|-------|
| `subprocess` over GitPython | **HIGH** | GitPython PyPI page explicitly states maintenance mode. Verified git 2.51.2 worktree CLI. Tested `--porcelain` output parsing. |
| `re.sub()` for pyproject.toml | **HIGH** | Tested regex replacement against actual `00-experiments` pyproject.toml content. Confirmed tomllib is read-only (stdlib). |
| `string.Template` for README | **HIGH** | Tested against representative README content. Verified `$variable` syntax has no Markdown conflicts. |
| No Jinja2 needed | **HIGH** | Verified Jinja2 3.1.6 capabilities on PyPI. Confirmed `{{ }}` syntax conflicts with Markdown code blocks. |
| tomlkit as future upgrade path | **MEDIUM** | tomlkit 0.14.0 confirmed actively maintained (Jan 2026 release, Poetry team). Not needed now but valid if scope grows. |
| No CLI framework needed | **HIGH** | Verified GSD config shows Codex model profile with tool-call-based execution. |

## Sources

- Git worktree CLI: `git worktree --help` (git 2.51.2, verified locally)
- GitPython: https://pypi.org/project/GitPython/ (v3.1.46, Jan 2026, maintenance mode confirmed)
- tomlkit: https://pypi.org/project/tomlkit/ (v0.14.0, Jan 2026, actively maintained)
- tomli-w: https://pypi.org/project/tomli-w/ (v1.2.0, Jan 2025, does not preserve formatting)
- Jinja2: https://pypi.org/project/Jinja2/ (v3.1.6, Mar 2025)
- Python `tomllib`: Verified in Python 3.13.1 stdlib (read-only TOML parser)
- Python `string.Template`: Verified in Python 3.13.1 stdlib
- `git worktree list --porcelain`: Tested locally, confirmed machine-parseable output
- `re.sub()` on pyproject.toml: Tested locally against actual `00-experiments` branch content
- uv: v0.9.18 verified locally
