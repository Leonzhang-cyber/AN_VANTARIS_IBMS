# IBMS Frontend A6 Layout Security Notes

## 1. UI menu hiding is not security

- Sidebar items are static placeholders
- Users can navigate directly via URL; route guards + backend enforce access

## 2. Backend permissions remain source of truth

- `@require_permission` on API routes is authoritative
- Static menu does not reflect user permissions yet

## 3. logoutLocal clears token only

- No server-side session invalidation (JWT is stateless)
- Token may remain valid until expiry — acceptable for baseline

## 4. No raw layout copied

- Raw `Layout.vue` may embed menu data, user info, and production URLs — not migrated

## 5. No secrets

- Layout contains no tokens, keys, or API URLs

## 6. Frontend menu must later align with backend menu_api JWT

- Future: load menu from `GET /system/menu/active` with Bearer token
- Hide items based on permissions from login response or `/did/me`

## 7. Non-scope

- No npm install (Element Plus declared in package.json only)
- No backend changes
