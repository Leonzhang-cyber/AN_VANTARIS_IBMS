# IBMS Frontend A8 Menu Security Notes

## 1. menu_api requires JWT

- Backend protects menu routes with `@jwt_required`
- Menu load only succeeds after login sets Bearer token

## 2. Frontend menu is not security boundary

- Sidebar visibility does not grant API access
- Users can navigate directly to routes; backend enforces permissions

## 3. Backend permission remains source of truth

- Menu items may include `permission` field for future UI filtering
- `@require_permission` on APIs is authoritative

## 4. 401 / 403 behavior

- **401:** request handler clears session → `/login`
- **403:** request handler → `/403`
- Menu load failure falls back to static menu (does not bypass auth on routes)

## 5. No raw menu copied

- Raw EditionManagement/MenuManagement not migrated
- Normalizer is new code with strict path sanitization

## 6. No eval / unsafe dynamic execution

- `normalizeBackendMenu` uses static field mapping only
- No `eval`, `Function`, or dynamic import from backend strings

## 7. Fallback menu risk

- Static fallback exposes all module stub routes to authenticated users
- Acceptable for dev baseline; replace with permission-filtered menu in A11
- Fallback does not bypass `requiresAuth` on routes

## 8. Non-scope

- No npm install / build
- No real tokens in source
- No production URL hardcode
