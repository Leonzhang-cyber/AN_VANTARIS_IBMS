# VANTARIS IBMS Repo Baseline Recovery 1

## 1. Task Scope

- recover clean git baseline
- no business feature development
- no backend/frontend runtime execution
- no DB/seed/migration
- no raw source modification
- no UFMS content merge

Base commit: `3724ed6` — docs(ibms): add UFMS boundary guard

---

## 2. Initial State

| Item | Value |
| ---- | ----- |
| Untracked paths | **190** |
| Tracked modified | **0** |
| Staged | **0** |
| Tracked files in HEAD | **17** |
| Reason for recovery | Truncated git history — full IBMS tree on disk but only smoke/docs subset tracked after incremental commits |

---

## 3. Classification Summary

| Category | Count | Action |
| -------- | ----- | ------ |
| runtime artifacts | 0 visible in status | ignored (`node_modules/`, `dist/`, `.venv/` already on disk, hidden by `.gitignore`) |
| archives/backups | 0 in status | ignored (`*.zip`, `Files/`, etc.) |
| raw source packages | 2 dirs on disk (`ibms_front`, `ibms_backend`) | ignored — not in status |
| env/secrets candidates | 2 `.env.example` + doc titles referencing secrets | `.env.example` tracked; real `.env` absent; credential JSON gitignored |
| docs | 148 | tracked |
| project config + IBMS source | ~42 top-level untracked paths (backend/frontend/contracts/scripts) | tracked |
| UFMS candidates | 0 in untracked | none |
| unknown | 0 | none — all untracked classified |

---

## 4. UFMS Boundary Check

| Item | Result |
| ---- | ------ |
| UFMS content in business source | **Not found** |
| Hits | Boundary guard docs, risk review, inventory note (`Files/UFMS-Products.xlsx` excluded) |
| Contamination | **No** |
| Execution stopped | **No** — references are governance/inventory only |

---

## 5. Files Tracked

This commit adds the canonical IBMS project tree:

- `docs/**` — architecture, security, governance, smoke notes
- `contracts/**` — OpenAPI, permission matrix, API boundary docs
- `AN_VANTARIS_IBMS-backend/**` — README, requirements, scripts, `src/**`, `.env.example` (excluding gitignored credentials/venv)
- `AN_VANTARIS_IBMS-frontend/**` — package metadata, config, `src/**`, `.env.example`
- `AN_VANTARIS_IBMS-main/README.md`
- Updated `.gitignore`

Already tracked (unchanged): smoke tests, boundary rules, prior recovery docs.

---

## 6. Files Ignored

Updated root `.gitignore`:

- `**/.pytest_cache/`
- `*.7z`, `*.rar`, `*.bak`, `*.backup`, `*.tar.gz`

Existing rules retained: `node_modules/`, `dist/`, `.venv/`, raw packages (`ibms_front/`, `ibms_backend/`), archives, credentials, `.env`.

---

## 7. Final State

| Item | Result |
| ---- | ------ |
| git status | **clean** (target) |
| Remaining blockers | none if all safe paths staged |

---

## 8. Next Tasks

- DB local-smoke
- JWT + DB 200 smoke
- permission enforcement
- DID prep
