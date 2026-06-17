# IBMS FRONTEND-A9-EXEC-1 — Permission Page Security Notes

**Task:** FRONTEND-A9-EXEC-1  
**Risk level:** High (permission CRUD surface)

---

## Permission CRUD is high risk

Creating, updating, or deleting permission codes can expand or shrink the authorization surface for all protected IBMS APIs. Treat this page as **administration-grade** functionality even when the UI is minimal.

Operational guidance:

- Restrict access in production to trusted administrators only.
- Audit permission changes when backend audit hooks are available.
- Do not expose this route on public or demo deployments without explicit review.

---

## Backend must enforce system:admin / system:write later

Current backend routes require JWT (`@jwt_required`) but fine-grained permission checks for permission CRUD may be incomplete or pending (see SYSTEM-B / PERMISSION_MATRIX work).

**Required follow-up:**

- Enforce `system:admin` or `system:write` on POST/PUT/DELETE `/system/permissions/*`.
- Return **403** when an authenticated user lacks write permission.
- Do not rely on frontend hiding buttons as a control.

---

## Frontend route permission is not security

Route meta `permissions: ['system:read']` is a **navigation hint** for future guards. It does not authenticate users or authorize API calls. All security decisions must occur on the server.

---

## Bearer token centralized

API calls use `services/api/request.ts`:

- Base URL from `VITE_IBMS_API_BASE_URL` (see `.env.example`)
- `Authorization: Bearer <token>` attached via interceptor from session storage
- No per-page token handling or duplicated auth logic

---

## No raw secret copied

- No production tokens, passwords, or private keys in source or docs
- No real `.env` committed
- Login flow remains on existing DID challenge path

---

## No direct axios

`PermissionListView.vue` imports only `@/services/api/system`. HTTP is centralized in `request.ts` for consistent 401/403 handling.

---

## No production URL hardcode

No hardcoded `https://` production API hosts in the migrated page or `system.ts`. Base URL is environment-driven.

---

## Error handling

UI surfaces short user-facing messages via `ApiError.message`. Full error response bodies are not logged to the console or displayed verbatim to reduce accidental leakage of internal details.
