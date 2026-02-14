# Codebase Structure

**Analysis Date:** 2026-02-13

## Directory Layout

```
project-template/
├── .foam/                    # VS Code Foam knowledge management
│   └── templates/            # Note templates
│       ├── daily-note.md     # Daily log template
│       └── new-template.md   # Generic note template
├── 00-dev-log/               # Developer progress logs
│   └── 00-template.md        # Dev log entry template
├── 00-supporting-files/      # Reference data and configs
│   └── data/                 # Data files
│       └── sample.env.file   # Environment variable template
├── 01-dev-onboarding/        # Git submodule: onboarding materials
├── 02-worktrees/             # Git worktrees (gitignored contents)
│   └── README.md             # Worktree usage instructions
├── .gitignore                # Python-oriented gitignore
├── .gitmodules               # Git submodule definitions
└── README.md                 # Project setup instructions
```

## Directory Purposes

**`.foam/templates/`:**
- Purpose: Foam (VS Code extension) note templates
- Contains: Markdown templates with VS Code snippet variables
- Key files: `daily-note.md`, `new-template.md`

**`00-dev-log/`:**
- Purpose: Daily development logs and progress tracking
- Contains: Markdown log entries
- Key files: `00-template.md` (template for new entries)

**`00-supporting-files/`:**
- Purpose: Supporting data, configuration templates, reference materials
- Contains: Data files and sample configs
- Key files: `data/sample.env.file`

**`01-dev-onboarding/`:**
- Purpose: Developer onboarding resources (git submodule)
- Contains: Submodule from `https://github.com/progressEdd/dev-onboarding.git`
- Key files: Submodule contents (must be initialized with `git submodule update --init`)

**`02-worktrees/`:**
- Purpose: Directory for git worktree checkouts
- Contains: Worktree directories (all gitignored except `README.md`)
- Key files: `README.md` (usage instructions)

## Key File Locations

**Entry Points:**
- Application code lives on feature/experiment branches (branched from `00-experiments`)

**Configuration:**
- `.gitmodules`: Git submodule definitions
- `.gitignore`: Comprehensive Python gitignore
- `00-supporting-files/data/sample.env.file`: Environment variable template

**Documentation:**
- `README.md`: Project overview and setup instructions
- `02-worktrees/README.md`: Git worktree usage guide

**Templates:**
- `.foam/templates/daily-note.md`: Foam daily note template
- `.foam/templates/new-template.md`: Foam generic note template
- `00-dev-log/00-template.md`: Dev log entry template

## Naming Conventions

**Files:**
- Lowercase with hyphens: `daily-note.md`, `new-template.md`, `sample.env.file`
- Numeric prefix for ordering within directories: `00-template.md`

**Directories:**
- Numeric prefix + hyphenated name: `00-dev-log/`, `01-dev-onboarding/`, `02-worktrees/`
- Two-digit prefix establishes order: `00` = meta/support, `01` = onboarding, `02` = development
- Hidden directories for tooling: `.foam/`

## Where to Add New Code

**New Application/Experiment:**
- Branch from `00-experiments` and create a worktree in `02-worktrees/`
- App code lives on the branch, not in the template repo

**New Supporting Data/Config:**
- Data files: `00-supporting-files/data/`
- Environment templates: `00-supporting-files/data/`

**New Dev Log Entry:**
- Copy `00-dev-log/00-template.md` and fill in the date and progress

**New Git Submodule:**
- Add to `.gitmodules` and initialize in an appropriately numbered directory

**New Top-Level Section:**
- Follow the `NN-descriptive-name/` convention
- Use the next available number (currently `03-*` is next)

**New Worktree:**
- Run `git worktree add 02-worktrees/<branch-name> <branch-name>`
- Contents are automatically gitignored

## Special Directories

**`01-dev-onboarding/`:**
- Purpose: External developer onboarding content
- Generated: No (git submodule)
- Committed: Reference only (submodule pointer committed, content fetched on init)

**`02-worktrees/`:**
- Purpose: Git worktree working directories
- Generated: Yes (created by `git worktree add`)
- Committed: No (contents gitignored; only `README.md` is tracked)

## Git Branches

**Active branches:**
- `master` - Main/default branch
- `vibe-coding` - Current working branch
- `worktrees` - Worktree structure branch
- `00-experiments` / `experiments` - Sandbox/experimentation branch

---

*Structure analysis: 2026-02-13*
