# VANTARIS IBMS Split B2 Canonical Frontend

## 1. Task Scope

- Declare canonical frontend source only
- No source moved
- No source copied
- No raw frontend changed
- No npm install/build executed

Prerequisites: SOURCE-A2, SPLIT-A0, SPLIT-B1 (`47ce74d`), WORKSPACE-A1.

---

## 2. Canonical Decision

| Role | Package | Decision |
|---|---|---|
| Raw frontend source | `AN_VANTARIS_IBMS-ibms_front/` | read-only source (gitignored) |
| Target frontend package | `AN_VANTARIS_IBMS-frontend/` | to be created as sanitized target (SPLIT-B3) |
| Main package | `AN_VANTARIS_IBMS-main/` | placeholder only, not runtime frontend |

**Tracked main content:** `AN_VANTARIS_IBMS-main/README.md` only — no `package.json`, no `src/`.

---

## 3. Frontend Stack Summary

| Area | Raw source (`ibms_front`) |
|---|---|
| **Framework** | Vue 3.5, Vite 8, TypeScript |
| **UI / state** | Element Plus, Pinia, vue-i18n |
| **Routing** | Vue Router 4 — `src/router/index.ts` (~4595 lines, nested under `Layout`) |
| **HTTP** | axios via `src/utils/request.js` |
| **API modules** | `src/api/system_api.js`, `src/api/did_api.js` only |
| **Entry** | `index.html` → `src/main.ts` → `App.vue` |
| **package.json name** | `ibms-bigdata-fronted` v0.0.0 |
| **Views** | 755 `.vue` files under `src/views/` (40+ domain folders) |
| **Stores** | `src/stores/` present |
| **Utils** | `src/utils/request.js` (central HTTP client) |

### request / baseURL behavior

- `src/utils/request.js` defines `DevUrl = http://127.0.0.1:5000/api` and `Online = https://ibms.aegisnx.com/api`
- **`BASE_URL` is hardcoded to `Online` (production)** — dev URL commented out
- Request interceptor reads `localStorage.getItem('token')` and sets `Authorization: Bearer ${token}`
- 401 response removes token and redirects to `/login`

### token handling

- `Login.vue` stores `token` and `userInfo` in `localStorage` after login
- `Layout.vue` clears token on logout
- No refresh-token flow observed

### menu / auth gap

- `router.beforeEach` only sets document title — **no auth redirect** despite `requiresAuth: false` on login route
- Backend `menu_api` requires JWT (commit `56234d8`) — frontend sends Bearer if token exists, but unauthenticated navigation is not blocked
- No dedicated permission store; 403 handling not standardized across views
- Only system + DID API wrappers exist — IoT/modeling pages mostly UI shells

---

## 4. Migration Rule

- **Do not copy raw frontend wholesale** into `AN_VANTARIS_IBMS-frontend/`
- **Do not copy** `node_modules/`, `dist/`, `.vite/`, cache directories
- **Do not copy secrets** or hardcoded production URLs
- **Do not copy large images** under `src/images/` until asset review (bulk of ~200M raw size)
- **Migrate package metadata first** (reviewed `package.json` / lockfile in FRONTEND-A0 — not in B3)
- **Then migrate `src` by logical module** (system → iot → did → modeling → operations)
- **Then normalize API base URL** to `VITE_IBMS_API_BASE_URL` env
- **Then add route auth guard** and centralized 401/403 handling

---

## 5. Canonical Frontend Risks

| Risk | Description | Mitigation phase |
|---|---|---|
| **Production API hardcode** | `request.js` defaults to `https://ibms.aegisnx.com/api` | FRONTEND-A1 env baseline |
| **No route auth guard** | Router allows deep links without login check | FRONTEND-A2 router guard |
| **Menu JWT compatibility** | Menu API requires JWT; token must be present before menu fetch | FRONTEND-A1 auth + login flow |
| **Large assets** | `src/images/` contains many multi-MB PNG/JPG files | Asset review before copy; CDN/LFS |
| **Placeholder main risk** | `AN_VANTARIS_IBMS-main/` could be mistaken for frontend app | B2 declaration: placeholder only |
| **403 after permission seed** | Backend enforces permissions; UI may not handle 403 | FRONTEND-A1 standardized error handling |
| **Incomplete API layer** | No iot/modeling API modules | FRONTEND-A3+ per domain |

---

## 6. Next Tasks

- **SPLIT-B3** — frontend target skeleton
- **FRONTEND-A0** — package metadata migration (reviewed)
- **FRONTEND-A1** — request/auth baseline
- **FRONTEND-A2** — route guard baseline
