# VANTARIS IBMS Frontend A1 Request Auth Baseline

## 1. Task Scope

- request/auth baseline only
- no pages migrated
- no raw `request.js` copied
- no backend connection
- no npm install/build/dev executed

---

## 2. Files Created

| File | Purpose |
|---|---|
| `src/services/auth/token.ts` | Token get/set/clear via localStorage |
| `src/services/auth/session.ts` | Session helpers, local logout |
| `src/services/api/errors.ts` | `ApiError`, 401/403 helpers, error normalization |
| `src/services/api/request.ts` | Axios client, env base URL, Bearer interceptor |

**Not migrated:** raw `did_api.js`, `system_api.js`.

---

## 3. API Base URL Rule

- Read from `import.meta.env.VITE_IBMS_API_BASE_URL`
- Fallback: `/api` (relative — no production domain)
- Configured in `.env.example` as `http://localhost:5001/api`
- Vite config does **not** embed API URL

---

## 4. Bearer Token Flow

1. Login flow (future) calls `setAccessToken(token)` after backend auth
2. `request` interceptor reads token via `getAccessToken()`
3. Sets header `Authorization: Bearer <token>` when present
4. `logoutLocal()` clears token and optional user info key

---

## 5. 401 / 403 Behavior

| Status | Client behavior |
|---|---|
| **401** | Normalize to `ApiError`; invoke `setUnauthorizedHandler` hook if registered |
| **403** | Normalize to `ApiError`; invoke `setForbiddenHandler` hook if registered |

- Interceptors do **not** redirect or mutate router — handlers registered by app shell (A3) or router (A2)
- Rejected promise carries `ApiError` for caller handling

---

## 6. Not Changed

- Raw frontend source
- Backend runtime
- Router / views (except service layer)
- Domain API modules

---

## 7. Next Tasks

- **FRONTEND-A2** — router/auth guard baseline (wire handlers to `/login`, `/403`)
- **FRONTEND-A3** — app shell (`main.ts`, login form)
- **FRONTEND-A4** — domain API modules (system, did, iot, modeling)
