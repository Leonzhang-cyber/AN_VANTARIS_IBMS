# IBMS Baseline Commit Report

**Task:** IBMS-REPO-BASELINE-2  
**Date:** 2026-06-17  
**Workspace:** `/Users/mac/Desktop/AN_VANTARIS_IBMS`

---

## 1. Purpose

Establish a **controlled local Git baseline** (Option B from `docs/IBMS_REPO_BASELINE_RECOVERY_REPORT.md`) by staging the canonical IBMS tree—backend, frontend, contracts, and documentation—under root `.gitignore` rules, without building, testing, or pushing. This commit makes the on-disk authoritative project tree trackable for subsequent work (starting with **IBMS-FE-BUILD-1**).

---

## 2. Baseline source

| Source | Role |
|--------|------|
| On-disk tree at `/Users/mac/Desktop/AN_VANTARIS_IBMS` | Authoritative project content |
| Prior commits `109aba8`, `1b1f854` | Smoke patch + recovery documentation (retained as history) |
| Root `.gitignore` | Excludes secrets, dependencies, build artifacts, legacy raw packages, archives, and local reference material |

**Note:** The workspace directory was not present on Desktop at task start; the repository was **moved from Trash** to the expected path before staging (same `HEAD`, same tree).

---

## 3. Remote status

| Check | Result |
|-------|--------|
| `git remote -v` | **Empty** — no remote configured |
| Push / fetch | **Not performed** |

---

## 4. Staged for baseline commit

**Command:**

```bash
git add .gitignore AN_VANTARIS_IBMS-main contracts docs AN_VANTARIS_IBMS-frontend AN_VANTARIS_IBMS-backend
```

**Approximate counts (index after add, before this report file):**

| Area | Staged paths (new in index diff) | Notes |
|------|----------------------------------|-------|
| `.gitignore` | 1 | Secret / artifact patterns |
| `AN_VANTARIS_IBMS-main/` | 1 | README only |
| `contracts/` | 22 | OpenAPI, schemas, tools |
| `docs/` | 139 | architecture + security (+ recovery report) |
| `AN_VANTARIS_IBMS-frontend/` | 57 | Source + config; **no** `node_modules` / `dist` |
| `AN_VANTARIS_IBMS-backend/` | 105 | Source + requirements; **no** `.venv` |
| **New paths in cached diff** | **325** | Plus **7** files already tracked from `109aba8` |

**Top-level directories represented in the index:** `.gitignore`, `AN_VANTARIS_IBMS-backend`, `AN_VANTARIS_IBMS-frontend`, `AN_VANTARIS_IBMS-main`, `contracts`, `docs`.

---

## 5. Excluded (intentionally not staged)

Enforced by `.gitignore` and/or policy; verified absent from cached path list:

| Category | Examples on disk | Handling |
|----------|------------------|----------|
| Dependencies | `AN_VANTARIS_IBMS-frontend/node_modules/` | Ignored |
| Build output | `AN_VANTARIS_IBMS-frontend/dist/` | Ignored |
| Virtualenv | `AN_VANTARIS_IBMS-backend/.venv/` | Ignored |
| Real env files | No `.env` (only `.env.example`) | Ignored |
| Credentials / VC fixtures | `src/tests/credential_*.json`, `vc_credential.json` | Ignored |
| Large data / models | `*.csv`, `*.pkl`, `*.mp4`, `data/` | Ignored |
| Archives | `*.zip` at repo root | Ignored |
| Legacy raw packages | `AN_VANTARIS_IBMS-ibms_backend/`, `-ibms_front/` | Ignored |
| Reference tree | `Files/` | Ignored |
| IDE metadata | `AN_VANTARIS_IBMS-backend/.idea/` | Ignored |

**Untracked docs (6 files, not in add scope failure):** npm/vite smoke and audit notes under `docs/architecture/` and `docs/security/` — left untracked; may be added in a follow-up docs commit.

---

## 6. Secret / forbidden artifact scan

### 6.1 Path-based (staged names)

| Pattern | Matches (excluding `.env.example`) |
|---------|----------------------------------|
| `node_modules` | 0 |
| `/dist/` | 0 |
| `.venv` / `venv` | 0 |
| Real `.env` | 0 |
| `credential*.json` | 0 |
| `*.pem` / `*.key` | 0 |
| `*.sql` | 0 |
| `*.log` / `logs/` | 0 |
| `Files/` | 0 |
| Legacy `ibms_backend` / `ibms_front` | 0 |
| `*.zip` | 0 |

Documentation and source files with names containing `token` or `secret` (e.g. security notes, `token.ts`) are **expected**; they are not credential files.

### 6.2 Content-based (cached diff)

- Grep for AWS-key / PEM private-key / inline JWT secret patterns on staged blobs: **no hits**
- No staged `*.pem` paths

---

## 7. Blockers and issues encountered

| Issue | Impact | Mitigation |
|-------|--------|------------|
| **Disk ~97% full** (~9.6 GiB free) | Prior `fatal: unable to write new index file`; slow `git add` (~286 s) | Removed `.git/index.lock`; monitor space before large operations |
| **Repo path missing on Desktop** | Task path did not exist | Restored `AN_VANTARIS_IBMS` from Trash to Desktop |
| **No remote** | Cannot verify against team canonical branch | Add remote before any shared push |
| **6 untracked doc files** | Incomplete npm/vite audit doc set in Git | Optional follow-up commit |

**Pre-step:** `rm -f .git/index.lock` executed successfully.

---

## 8. Next task

**IBMS-FE-BUILD-1** — frontend build/smoke work on this baseline (install/build only when explicitly authorized for that task).

---

## 9. Task constraints observed

- No `npm install`, build, test, or push
- No application source logic modified
- No files deleted
- Legacy packages and local archives remain on disk but untracked

