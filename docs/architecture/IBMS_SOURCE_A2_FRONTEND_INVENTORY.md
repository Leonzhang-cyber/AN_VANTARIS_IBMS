# VANTARIS IBMS Source A2 Frontend Inventory

## 1. Task Scope

- frontend inventory only
- no source changed
- no npm install/build executed

Packages analyzed:

- `AN_VANTARIS_IBMS-ibms_front/`
- `AN_VANTARIS_IBMS-main/`

---

## 2. Frontend Package Summary

### 2.1 `AN_VANTARIS_IBMS-ibms_front`

| Area | Details |
|---|---|
| **Path / size** | `AN_VANTARIS_IBMS-ibms_front/` (~200M; mostly `src/images/` PNG/JPG assets) |
| **Tech stack** | Vue 3.5, Vite 8, TypeScript, Element Plus, Pinia, Vue Router 4, axios, vue-i18n, echarts, three.js, ethers, leaflet |
| **package.json name** | `ibms-bigdata-fronted` v0.0.0 |
| **Scripts** | `dev`, `build`, `preview`, `build-only`, `type-check` |
| **Node engines** | `^20.19.0 \|\| >=22.12.0` |
| **Entry** | `index.html` → `src/main.ts` → `App.vue` |
| **Router** | `src/router/index.ts` (~4595 lines) — deeply nested routes under `Layout` |
| **API client** | `src/utils/request.js` — axios instance, Bearer from `localStorage` |
| **API modules** | `src/api/system_api.js`, `src/api/did_api.js` only (no dedicated iot/modeling API files) |
| **Auth token** | Login stores `token` + `userInfo` in `localStorage`; request interceptor adds `Authorization: Bearer` |
| **Menu / permission** | No dedicated permission store observed; menu likely loaded via system API (backend menu routes now JWT-protected) |
| **Pages / modules** | 755 `.vue` files; 40+ top-level folders under `src/views/` |
| **Build artifacts** | No `dist/` or `node_modules/` in snapshot |
| **Analysis artifacts** | `views_analysis_report.txt` (587 planned / 748 exist / 43 missing), `missing_files_list.txt` |

**Representative view domains:**

| Domain folder | Console relevance |
|---|---|
| Home, CommandCenter, Dashboard | UI shell / overview |
| Login, layout/Layout.vue | Auth shell |
| SystemsDevices, Device, IoT-related | IoT/device pages (mostly UI) |
| Blockchain | DID/trust UI |
| Intelligence, Prediction, AiVideoAnalytics | Modeling/AI UI |
| IntegrationHub, DeveloperCenter | API/integration sandbox |
| Administration, Settings, SecurityCompliance | System/admin |
| Energy, DataCenterOperations, AlarmsEvents | Vertical IBMS modules |

### 2.2 `AN_VANTARIS_IBMS-main`

| Area | Details |
|---|---|
| **Path / size** | `AN_VANTARIS_IBMS-main/` (4K) |
| **Contents** | `README.md` only: `# AN_VANTARIS_IBMS` / `Source Code` |
| **Tech stack** | None |
| **package.json** | **Missing** |
| **src/** | **Missing** |
| **Role** | Repository label / placeholder — **not** a frontend application |

---

## 3. Package Relationship

| Question | Answer |
|---|---|
| **Primary frontend?** | `AN_VANTARIS_IBMS-ibms_front` — full Vue SPA |
| **Shell / main package?** | `AN_VANTARIS_IBMS-main` — placeholder only (name suggests monorepo root label, not runtime shell) |
| **Placeholder?** | `main` is placeholder; `front` is real app |
| **Duplicate / divergent?** | No code overlap — `main` has no source; no second frontend copy in workspace |
| **Missing package.json / src?** | Only on `main` (expected for placeholder) |

**Integrated vs split:** Original delivery appears as **separate** backend zip + frontend zip + empty main readme — not a unified npm monorepo.

---

## 4. Console Split Readiness

| Console capability | ibms_front readiness | Notes |
|---|---|---|
| **UI shell** | Strong | `Layout.vue`, Element Plus, i18n |
| **Routing** | Strong structure, weak guards | Large route tree; `beforeEach` sets title only — **no auth redirect** |
| **Auth / session** | Partial | Token in localStorage; login/logout in Login + Layout; no global `requiresAuth` enforcement |
| **Menu / permission** | Partial | Backend menu API exists; frontend system_api likely used; must align with MENU-JWT + future permission UI |
| **API client** | Minimal surface | Only system + DID wrappers; most views are static/demo UI |
| **System / menu pages** | Present | Administration, Settings modules |
| **IoT / device pages** | Present (UI-heavy) | SystemsDevices, Device, IntegrationHub — few wired API calls |
| **DID / trust pages** | Present | Blockchain/* + did_api.js |
| **Modeling / AI pages** | Present (UI-heavy) | Intelligence, Prediction — no modeling_api.js |

---

## 5. Split Recommendation

- **Do not** physically split frontend into multiple npm packages until canonical source is declared.
- **Canonical frontend candidate:** `AN_VANTARIS_IBMS-ibms_front` → future `AN_VANTARIS_IBMS-frontend` (or Console package name per split map).
- **`AN_VANTARIS_IBMS-main`** should not become a third frontend; treat as historical repo title or future monorepo README only.
- **Logical Console modules** should map to `src/views/<Domain>/` folders first; shared layers:
  - `src/utils/request.js` — API boundary
  - `src/router/` — navigation boundary
  - `src/stores/` — session/state boundary
  - `src/api/` — expand per domain when wiring backend
- Before migration: add **route auth guard**, **env-based API URL**, and **IoT/modeling API modules** to match hardened backend.
