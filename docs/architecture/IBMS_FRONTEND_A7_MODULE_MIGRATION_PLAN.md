# VANTARIS IBMS Frontend A7 Module Migration Plan

## 1. Task Scope

- migration plan only
- no page migration in this task
- no raw source copied

Target: `AN_VANTARIS_IBMS-frontend/`  
Reference: `AN_VANTARIS_IBMS-ibms_front/` (758 `.vue` files)

---

## 2. Migration Prerequisites

| Prerequisite | Status |
|---|---|
| Request/auth baseline (A1) | ✅ |
| Router auth guard (A2) | ✅ |
| App shell + login (A5) | ✅ |
| Element Plus layout (A6) | ✅ |
| Domain API modules (A4) | ✅ |
| Frontend OpenAPI contract (CONTRACTS-B1) | ✅ |
| npm install + smoke dev | ⏳ future batch |
| Permission seed on staging | ⏳ DB-B1 |

---

## 3. Migration Order

1. **Dashboard** — replace `DashboardPlaceholder` with real overview (minimal widgets)
2. **System / Menu** — Administration subset; wire `menuApi` to layout sidebar
3. **DID** — Blockchain/TrustIdentity pages; wire `didApi`
4. **IoT / Device** — SystemsDevices + Device entry pages; wire `iotApi`
5. **Modeling** — Intelligence/Prediction subset; wire `modelingApi`; add echarts dep
6. **Operations** — Maintenance, DataCenterOperations, Energy (batch by subfolder)
7. **Heavy charts / assets** — after dependency + CDN review (echarts, three, images)

---

## 4. Per-Module Rules

Each migration batch must:

- migrate **one page group** at a time (≤15 `.vue` files recommended)
- remove hardcoded API URLs (use `VITE_IBMS_API_BASE_URL` + domain modules)
- use `src/services/api/*` — no direct axios unless approved
- no raw assets until reviewed (images, mp4, large JSON)
- no secrets / demo tokens in migrated code
- preserve `meta.requiresAuth` and future `meta.permissions`
- add routes under `src/modules/<domain>/` then register in `routes.ts`
- update CONTRACTS reference if new API surface exposed

---

## 5. Suggested Batches (FRONTEND-A8+)

| Batch ID | Scope | Est. files | Dependencies |
|---|---|---|---|
| **A8** | Dynamic menu from backend | 0 views | menuApi JWT |
| **A9** | System admin (5–10 pages) | ~10 | element-plus only |
| **A10** | DID (Blockchain core) | ~8 | ethers (pending) |
| **A11** | IoT device registry subset | ~10 | — |
| **A12** | Modeling dashboard subset | ~8 | echarts (pending) |
| **A13** | Operations slice 1 | ~15 | mixed |
| **A14** | Assets + images review | TBD | CDN/LFS |

---

## 6. Stop Conditions

Stop migration batch if:

- hardcoded production URL found in raw page diff
- secret / token / private key in page or asset
- large asset dependency without approval (>500KB per file default)
- missing backend contract for API used by page
- npm dependency not reviewed (ethers, three, echarts, etc.)
- page requires >15 files to migrate atomically — split plan first

---

## 7. Next Tasks

- **FRONTEND-A8** — dynamic menu from `menuApi`
- **CONTRACTS-B2** — runtime OpenAPI validation
- **FRONTEND-A9** — first System module page group
- **FRONTEND-A0-deps** — approve echarts/ethers/three additions
