# IBMS Split B2 Frontend Security Notes

## 1. Security Boundary

- frontend must not store secrets (passwords, private keys, JWT signing keys, DB credentials)
- frontend must use bearer token only — attach via centralized HTTP client, not per-view ad hoc headers
- frontend must not call DB — all data via `AN_VANTARIS_IBMS-backend` `/api/*`
- frontend must not embed production API URL permanently — use `VITE_IBMS_API_BASE_URL` at build time

Raw reference (`ibms_front`) currently violates the last rule; target package must not inherit it without remediation.

---

## 2. Token / API Risk

| Risk | Current raw behavior | Target requirement |
|---|---|---|
| **menu_api JWT** | Backend requires JWT on all 19 menu routes | Token must exist before menu/version API calls |
| **Authorization header** | `request.js` adds Bearer from `localStorage` | Centralize in `src/services/api/` (target skeleton) |
| **401 handling** | Token cleared + redirect `/login` | Standardize in one interceptor; apply to all API modules |
| **403 handling** | Not standardized | Show permission error; optional redirect; log for audit |
| **Token storage** | `localStorage` | Document XSS risk; consider httpOnly cookie only if backend supports (future) |
| **Unauthenticated routes** | No router guard | Block protected routes when token absent |

---

## 3. Asset Risk

- `AN_VANTARIS_IBMS-ibms_front/src/images/` contains large binary assets (~majority of 200M package size)
- large images must be reviewed before migration — prefer CDN, Git LFS, or external Storage/Artifacts
- no raw upload/video/model/data artifacts in frontend runtime unless explicitly approved
- do not commit `node_modules/`, `dist/`, or zip archives into target frontend package

---

## 4. Non-Scope

- no frontend source changed in B2
- no build executed
- no npm install
- no API behavior changed on backend
- no raw frontend copied
