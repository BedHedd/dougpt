# External Integrations

**Analysis Date:** 2026-02-13

## APIs & External Services

**None detected.**
- No SDK imports, API client code, or service integrations exist on template branches
- Application code lives on experiment/feature branches (branched from `00-experiments`)

## Data Storage

**Databases:**
- None configured

**File Storage:**
- Local filesystem only
- `00-supporting-files/data/` directory exists for supporting data files

**Caching:**
- None

## Authentication & Identity

**Auth Provider:**
- None

## Monitoring & Observability

**Error Tracking:**
- None

**Logs:**
- None configured

## CI/CD & Deployment

**Hosting:**
- GitHub (repository: `https://github.com/progressEdd/project-template.git`)

**CI Pipeline:**
- None detected - no `.github/workflows/`, `Jenkinsfile`, or CI config files present

## Environment Configuration

**Required env vars:**
- None currently required (no code that reads environment variables)
- `00-supporting-files/data/sample.env.file` exists as a reference template for future use

**Secrets location:**
- `.env` files are gitignored

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## Git Submodules

**`01-dev-onboarding`:**
- Source: `https://github.com/progressEdd/dev-onboarding.git`
- Branch: `master`
- Config: `.gitmodules`
- Purpose: Developer onboarding documentation/resources

---

*Integration audit: 2026-02-13*
