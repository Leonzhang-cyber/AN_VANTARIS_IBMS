# IBMS FRONTEND-A9-EXEC-2 — System Settings Security Notes

**Task:** FRONTEND-A9-EXEC-2  
**Risk level:** Medium (configuration visibility)

---

## Settings page can expose sensitive config if not controlled

A settings UI can reveal operational details (API endpoints, debug flags, feature toggles) that aid reconnaissance if shown to unauthorized users.

Mitigations in this migration:

- Page requires authentication (`requiresAuth: true`)
- All fields are read-only; no client-side persistence of secrets
- Save is disabled until a vetted backend config API exists

Production deployments should still enforce backend authorization before exposing any future writable settings.

---

## No secret shown

The page does not display tokens, passwords, private keys, or database credentials. Environment values shown are non-secret build-time configuration (`VITE_*`).

---

## API base URL is non-secret env display only

`VITE_IBMS_API_BASE_URL` (or `/api` fallback) is displayed for operator clarity. This is not a credential. Avoid placing secrets in `VITE_*` variables — they are embedded in frontend bundles.

---

## Backend remains source of truth

Menu mode detection probes `GET /system/menus` but authoritative system policy (permissions, feature flags, tenant config) must come from backend APIs when implemented. Frontend env vars are deployment hints only.

---

## Frontend route permission is not security

Route meta `permissions: ['system:read']` is advisory for future guards. It does not authorize API access or prevent direct API calls.

---

## No direct axios

Settings view imports `menuApi` and `resolveBaseUrl` from domain modules. HTTP is centralized in `request.ts`.

---

## No production URL hardcode

No hardcoded production API hosts. Base URL comes from environment configuration or `/api` default.

---

## Error handling

Menu mode probe failures silently fall back to `fallback` mode label. No full error response bodies are logged or displayed.
