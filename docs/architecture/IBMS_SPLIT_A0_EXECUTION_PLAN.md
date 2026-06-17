# VANTARIS IBMS Split A0 Execution Plan

Phased plan for **code migration** (future batches).  
**This document does not authorize execution in SOURCE-A0 batch.**

Prerequisites complete:

- SOURCE-A0: package snapshot
- SOURCE-A1: backend inventory
- SOURCE-A2: frontend inventory
- SPLIT-A0: rules + map (this series)

---

## Phase B1 — Select canonical backend

**Goal:** Lock runtime backend to `AN_VANTARIS_IBMS-backend`.

| Step | Action |
|---|---|
| B1.1 | Document decision in `docs/architecture/` (SPLIT-B1) |
| B1.2 | Mark `ibms_backend` as reference-only (gitignore or `reference/`) |
| B1.3 | Diff any unique features in original not in current — port with security guards |
| B1.4 | Verify env template covers all `IBMS_*` vars |

**Exit criteria:** No ambiguity about which backend runs; no secret in tracked config.

---

## Phase B2 — Select canonical frontend

**Goal:** Lock Console source to `ibms_front` → `AN_VANTARIS_IBMS-frontend`.

| Step | Action |
|---|---|
| B2.1 | Document decision (SPLIT-B2) |
| B2.2 | Externalize API base URL (`VITE_API_BASE_URL`) |
| B2.3 | Add router auth guard |
| B2.4 | Confirm `main` remains non-runtime |

**Exit criteria:** Frontend builds against staging API; login + menu work with JWT.

---

## Phase B3 — Establish target skeleton

**Goal:** Create directory layout without business logic moves.

| Step | Action |
|---|---|
| B3.1 | Create `AN_VANTARIS_IBMS-frontend/` skeleton (package.json, vite, tsconfig from ibms_front) |
| B3.2 | Root README for monorepo |
| B3.3 | Optional `reference/` for original zips/folders |
| B3.4 | Update `.gitignore` for zips, reference snapshots, artifacts |

**Exit criteria:** Empty/shell packages exist; no duplicate runtime.

---

## Phase B4 — Module migration (ordered)

**Goal:** Move code by logical module with security preserved.

| Order | Module | Source → Target |
|---|---|---|
| 1 | docs | extend governance |
| 2 | contracts | OpenAPI + permission matrix sync |
| 3 | backend Core/Auth/System | already canonical — gap fill only |
| 4 | backend IoT / DID / Modeling | port deltas from ibms_backend if any |
| 5 | frontend shell | request, router, Login, Layout |
| 6 | frontend API clients | system, did, + new iot/modeling |
| 7 | frontend views | by domain folder incrementally |
| 8 | assets | images via CDN/LFS decision |

**Rule:** Never copy `ibms_backend/src/common/config/default.py` literals.

---

## Phase B5 — Contract validation

**Goal:** Backend routes match contracts.

| Step | Action |
|---|---|
| B5.1 | OpenAPI diff vs live Flask routes |
| B5.2 | Permission matrix vs `@require_permission` decorators |
| B5.3 | Menu JWT documented for frontend team |
| B5.4 | 401/403 response shapes consistent |

**Exit criteria:** Contract checklist green for protected APIs.

---

## Phase B6 — Runtime smoke test

**Goal:** Minimal end-to-end validation (future batch — requires venv/npm).

| Step | Action |
|---|---|
| B6.1 | Backend with env + DB (staging) |
| B6.2 | Permission seed dry-run then `--apply` on staging |
| B6.3 | Frontend dev against staging API |
| B6.4 | Login → menu load → one route per domain (system, iot, did, modeling) |

**Exit criteria:** No P0 secret leak; auth flows work.

---

## Stop Conditions

Stop migration immediately if:

| Condition | Action |
|---|---|
| Real secret detected in staged files | Remove, rotate creds, document incident |
| Unknown duplicate package with divergent history | Inventory (SOURCE-style) before proceed |
| Frontend API break risk (403 on menu/login) | Fix seeds or frontend client first |
| DB migration risk (schema unknown) | Schema inventory + backup before migrate |
| Package has own `.git` history | Resolve submodule/subtree policy first |
| Accidental downgrade of JWT/permission vs current backend | Reject PR |

---

## Recommended next batch (after SPLIT-A0)

| Task ID | Description |
|---|---|
| SPLIT-B1 | Declare canonical backend + reference ignore policy |
| SPLIT-B2 | Declare canonical frontend + env URL + auth guard prep |
| SPLIT-B3 | Target skeleton directories |
| CONTRACTS-B1 | Frontend-facing OpenAPI subset for system/menu/iot/did/modeling |
| SECURITY-B1 | Frontend token + 403 handling spec |
| DB-B1 | Staging seed execution with venv (permission alignment) |

Estimated count: **6 tasks** in next batch (can split into 2 commits each if needed).
