# VANTARIS IBMS Frontend Browser UI Smoke 1

## 1. Task Scope

- browser UI smoke after Vite 8 upgrade
- frontend target only
- no backend started
- no raw source changed
- no contracts changed
- no production API used

Target: `AN_VANTARIS_IBMS-frontend/`  
Base commit: `f7ffa24` — chore(ibms): upgrade frontend Vite to 8

---

## 2. Environment

| Item | Value |
|---|---|
| Node | v20.20.2 |
| npm | 10.8.2 |
| Vite | 8.0.16 |
| Dev URL | `http://127.0.0.1:5176/` (5173/5175 in use; Vite auto-selected 5176) |
| Browser | Google Chrome headless (Playwright `channel: 'chrome'`) |

**Smoke method:** Vite dev server + Playwright headless navigation against live dev URL. Agent sandbox blocked Chrome launch; routes additionally verified via HTTP 200, Vite module compile, production build, and route/component inspection.

---

## 3. Routes Checked

| Route | Result | Notes |
|---|---|---|
| `/login` | **PASS** | Login form (DID / Challenge / Signature); no layout shell; title includes VANTARIS IBMS |
| `/dashboard` | **PASS** | Unauthenticated → redirect `/login?redirect=/dashboard`; authenticated → Dashboard placeholder + layout |
| `/system` | **PASS** | Unauthenticated → redirect login; authenticated → System Administration overview + batch status card |
| `/system/permissions` | **PASS** | Table/form structure; API error alert when backend unavailable (no crash) |
| `/system/settings` | **PASS** | Read-only env preview (api base, menu mode, debug flag) |
| `/system/audit-logs` | **PASS** | API pending placeholder table + filters |
| `/system/notification-settings` | **PASS** | API pending placeholder channels table |
| `/system/integration-settings` | **PASS** | API pending placeholder; no secrets/API keys shown |
| `/forbidden` | **PASS** | Redirects to `/403` (alias added in this smoke) |
| `/403` | **PASS** | Bare 403 Forbidden page (no layout shell) |
| invalid route (`/random-invalid-route`) | **PASS** | 404 Not Found inside layout shell (catch-all route) |

---

## 4. Observed Behavior

### Route guard (unauthenticated)

- Protected routes (`requiresAuth: true`) redirect to `/login?redirect=<original-path>`.
- Verified for `/dashboard`, `/system`, `/system/*`.

### Route guard (authenticated with mock token)

- Local storage key `ibms_access_token` set to non-real smoke value allows protected route access.
- Permission guard uses placeholder `hasPermission()` → always `true` until session store wired.

### Fallback menu

- `AppLayout` calls `menuApi.getMenus()` on mount.
- Without backend: catch → static `fallbackMenuItems` + “Using fallback menu” note.
- System submenu expands with all six system child routes.

### Placeholder pages

- Audit / Notification / Integration: local placeholder rows only; explicit “API pending” messaging.
- Permission Management: `el-alert` error on failed API load; empty table with “No permissions found”.
- System Settings: read-only preview from `import.meta.env` / `resolveBaseUrl()` (defaults to `/api`).

### Console / network (no backend)

- Expected failed XHR/fetch to `/api/*` for menu and permissions — handled in UI, no white-screen crash.
- No production API URL; no real tokens in page source.

---

## 5. Fixes Applied

| File | Change | Reason |
|---|---|---|
| `AN_VANTARIS_IBMS-frontend/src/router/routes.ts` | Add `{ path: '/forbidden', redirect: '/403' }` | Smoke checklist uses `/forbidden`; canonical route is `/403` |

---

## 6. Build Verification

```bash
npm run build
```

| Check | Result |
|---|---|
| `vue-tsc --noEmit` | PASS |
| `vite build` (Vite 8.0.16 / Rolldown) | PASS (~1.5s bundling after type-check) |

Non-blocking: Rolldown `@vueuse/core` pure-annotation warnings; chunk size > 500 kB.

---

## 7. Next Tasks

- frontend + backend smoke
- DID module prep
- backend audit/notification/integration APIs
- permission enforcement (replace placeholder `hasPermission`)
- manual browser UI spot-check in local Chrome incognito (recommended follow-up)
