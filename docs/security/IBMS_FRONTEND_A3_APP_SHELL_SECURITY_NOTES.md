# IBMS Frontend A3 App Shell Security Notes

## 1. Frontend route guard is not backend security

- A2 guards and A3 error handlers improve UX only
- Backend JWT and `@require_permission` remain authoritative

## 2. 401 clears local token/session

- `handleUnauthorized` calls `logoutLocal()` before redirecting to login
- Prevents stale token loops on expired JWT

## 3. 403 routes to forbidden page

- `handleForbidden` navigates to `/403` placeholder
- User sees permission denial without exposing backend internals

## 4. No secrets in frontend

- App shell contains no credentials, signing keys, or sample tokens
- Login form not yet implemented (A5)

## 5. No production URL hardcode

- API base remains env-driven via `VITE_IBMS_API_BASE_URL`
- Shell does not embed external API domains

## 6. Raw UI not copied

- No raw layout, images, or demo credentials from `ibms_front`
- Reduces risk of inheriting hardcoded production URL patterns

## 7. Non-scope

- No npm install / build / dev
- No backend changes
- No real `.env` created
