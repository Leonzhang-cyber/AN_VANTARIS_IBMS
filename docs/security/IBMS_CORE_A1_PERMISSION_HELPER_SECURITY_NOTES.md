# IBMS Core A1 Permission Helper Security Notes

**Task ID:** IBMS-CORE-A1

---

## No Token Logging

- `jwt_util.jwt_required` no longer prints Authorization token or full JWT payload.
- `permission_util` does not log tokens, secrets, or raw payloads.

---

## No Secret Logging

Helper modules must not log `JWT_SECRET_KEY`, private keys, or credential bodies.

---

## Empty Permission Behavior

If JWT is valid but `perms` / `permission_codes` / `permissions` is empty or absent:

- `has_permission` / `has_any_permission` return `False`
- `@require_permission` / `@require_any_permission` return HTTP **403**

Integrators with JWT but no permission codes will be denied once enforcement lands (A6B/A7B/A10B).

---

## 401 vs 403 Boundary

| Condition | Handler | HTTP |
|---|---|---|
| Missing / invalid JWT | `@jwt_required` | 401 |
| Valid JWT, missing permission | `@require_permission` / `@require_any_permission` | 403 |

Permission helpers do not authenticate; they must be composed **after** `@jwt_required`.

---

## Stale Permission Risk

Permissions are embedded in JWT at login. DB permission changes do not invalidate outstanding tokens until expiry or re-login.

---

## Machine Identity Pending

Service accounts, edge devices, and M2M tokens are not defined in this phase. Wildcard `*` in root entity permissions is supported by the helper but policy must be documented before production enforcement.

---

## Related Documents

- `docs/architecture/IBMS_CORE_A1_PERMISSION_HELPER_IMPLEMENTATION.md`
- `docs/architecture/IBMS_CORE_A1_PERMISSION_HELPER_PREP.md`
- `contracts/PERMISSION_MATRIX_A2.md`
