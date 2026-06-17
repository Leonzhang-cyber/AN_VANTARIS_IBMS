# VANTARIS IBMS Split B3 Frontend Target Skeleton

## 1. Task Scope

- Create frontend target skeleton only
- No raw frontend copied
- No package.json migrated
- No source business pages migrated
- No npm install/build executed

Prerequisites: SPLIT-B2 (`170aa12`).

---

## 2. Files Created

| Path | Purpose |
|---|---|
| `AN_VANTARIS_IBMS-frontend/README.md` | Package rules and source references |
| `AN_VANTARIS_IBMS-frontend/package.manifest.json` | Migration policy manifest (not npm package.json) |
| `AN_VANTARIS_IBMS-frontend/.env.example` | Env-driven API base URL template |
| `AN_VANTARIS_IBMS-frontend/src/**/.gitkeep` | Directory placeholders (17 gitkeep files) |
| `docs/architecture/IBMS_SPLIT_B3_FRONTEND_TARGET_SKELETON.md` | This document |

**Not created:** `package.json`, `package-lock.json`, `vite.config.*`, `index.html`, any `.vue` files, any images.

---

## 3. Target Directory Purpose

| Directory | Purpose |
|---|---|
| `src/app` | App bootstrap, root layout shell (future `main.ts` / `App.vue`) |
| `src/router` | Vue Router config and navigation guards |
| `src/services/api` | Centralized axios/fetch client and domain API modules |
| `src/stores` | Pinia session, menu, permission state |
| `src/views` | Top-level routed pages (thin wrappers) |
| `src/assets` | Reviewed static assets only (no raw bulk copy) |
| `src/components` | Shared UI components |
| `src/modules/system` | System/menu/admin logical module |
| `src/modules/iot` | IoT/device logical module |
| `src/modules/did` | DID/trust logical module |
| `src/modules/modeling` | Modeling/AI logical module |
| `src/modules/operations` | Operations/energy/DC ops logical module |

---

## 4. Migration Rules

- package metadata migration (`package.json`, lockfile, vite/tsconfig) must be reviewed separately in **FRONTEND-A0**
- request/auth baseline before route migration (**FRONTEND-A1**)
- router auth guard before bulk view migration (**FRONTEND-A2**)
- no large assets until asset review
- no production API hardcode — use `VITE_IBMS_API_BASE_URL`
- central bearer token handling in `src/services/api/`
- migrate by module under `src/modules/*`, not wholesale `views/` copy

---

## 5. Next Tasks

- **FRONTEND-A0** — package metadata review
- **FRONTEND-A1** — request/auth baseline
- **FRONTEND-A2** — router/auth guard baseline
- **FRONTEND-A3** — module migration plan
