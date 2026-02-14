# Architecture

**Analysis Date:** 2026-02-13

## Pattern Overview

**Overall:** Project Template / Scaffold Repository

**Key Characteristics:**
- This is a project template, not an application - it provides structure for new projects
- Uses numbered directory prefixes (`00-`, `01-`, `02-`) to enforce ordering and categorization
- Separates concerns into documentation, onboarding, and development workflows
- Leverages git submodules for shared resources and git worktrees for parallel development

## Layers

**Documentation Layer (`00-dev-log/`, `.foam/`):**
- Purpose: Developer notes, daily logs, and knowledge management
- Location: `00-dev-log/` and `.foam/templates/`
- Contains: Markdown templates for daily notes and dev logs
- Depends on: VS Code Foam extension (optional)
- Used by: Developers for tracking progress

**Supporting Resources (`00-supporting-files/`):**
- Purpose: Data files, environment templates, and reference materials
- Location: `00-supporting-files/data/`
- Contains: Sample configuration files (e.g., `sample.env.file`)
- Depends on: Nothing
- Used by: Application code and developers for setup

**Onboarding (`01-dev-onboarding/`):**
- Purpose: Developer onboarding materials (external submodule)
- Location: `01-dev-onboarding/` (git submodule)
- Contains: Content from `https://github.com/progressEdd/dev-onboarding.git`
- Depends on: Git submodule initialization
- Used by: New developers joining the project

**Development Workspace (`02-worktrees/`):**
- Purpose: Git worktree directory for parallel branch development
- Location: `02-worktrees/`
- Contains: Git worktrees (gitignored except `README.md`)
- Depends on: Git worktree feature
- Used by: Developers working on multiple branches simultaneously

## Data Flow

**No application data flow exists.** The codebase is a scaffold — application code lives on feature/experiment branches via worktrees.

**Development Workflow:**

1. Clone repo with `git clone --recurse-submodules`
2. Branch from `00-experiments` for new projects
3. Create worktree in `02-worktrees/` for parallel branch work
4. Track progress in `00-dev-log/` using Foam templates

**State Management:**
- Git manages all state (branches, submodules, worktrees)
- No application state management

## Key Abstractions

**Numbered Directory Convention:**
- Purpose: Organize project into logical, ordered sections
- Examples: `00-dev-log/`, `00-supporting-files/`, `01-dev-onboarding/`, `02-worktrees/`
- Pattern: `NN-descriptive-name/` where `NN` is a two-digit prefix

## Entry Points

**Repository Entry Point:**
- Location: `README.md`
- Triggers: Developer reads on clone
- Responsibilities: Setup instructions, submodule initialization

**Application Entry Points:**
- Application code lives on feature/experiment branches (branched from `00-experiments`)
- Each branch defines its own entry point and structure

## Error Handling

**Strategy:** Not applicable at template level — error handling is branch-specific

## Cross-Cutting Concerns

**Logging:** Not configured
**Validation:** Not configured
**Authentication:** Not configured

---

*Architecture analysis: 2026-02-13*
