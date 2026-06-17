# IBMS Frontend A2 Route Security Notes

## 1. Route guard is frontend convenience only

- Guards improve UX by blocking unauthenticated navigation
- They do **not** replace backend authorization
- All API calls must still handle 401/403 from server

## 2. Backend remains source of truth

- JWT validation and `@require_permission` enforced on `AN_VANTARIS_IBMS-backend`
- Frontend `hasPermission()` placeholder must be wired to real permission data before relying on UI hiding

## 3. 401 / 403 must be enforced by backend

- Even if route guard passes, API may return 403 for missing permission
- Request client handlers (A1) must complement route guards

## 4. Stale token risk

- Token may exist in localStorage but be expired or revoked
- Route guard sees authenticated; API returns 401
- Wire `setUnauthorizedHandler` to clear session + redirect login (A3)

## 5. Permission UI hiding is not security

- Hiding menu items or routes does not protect APIs
- Never assume hidden routes are inaccessible without backend checks

## 6. menu_api JWT compatibility

- Menu/version API requires Bearer token on backend
- Load menu only after login sets token
- Route guard ensures dashboard routes need auth; menu fetch is separate API concern

## 7. Non-scope

- No raw router/views copied
- No `.vue` files
- No npm install / build
- No backend changes
