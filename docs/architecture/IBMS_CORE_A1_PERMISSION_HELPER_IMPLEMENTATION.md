# IBMS Core A1 Permission Helper Implementation

**Task ID:** IBMS-CORE-A1  
**Date:** 2026-06-16  
**Type:** Runtime helper only — not applied to business routes in this task

---

## 1. Task Scope

- Implement unified permission helper module for A6B / A7B / A10B
- Minimal `jwt_util.py` changes to populate Flask `g` principal fields
- No business route enforcement in this commit
- No JWT payload change, no login change, no DB query

---

## 2. Files Changed

| File | Change |
|---|---|
| `AN_VANTARIS_IBMS-backend/src/common/utils/permission_util.py` | New authorization helpers |
| `AN_VANTARIS_IBMS-backend/src/common/utils/jwt_util.py` | Populate `g.current_principal`; normalize permission fields; remove debug payload logging |
| `docs/architecture/IBMS_CORE_A1_PERMISSION_HELPER_IMPLEMENTATION.md` | This document |
| `docs/security/IBMS_CORE_A1_PERMISSION_HELPER_SECURITY_NOTES.md` | Security notes |

---

## 3. Helper Functions

| Function | Purpose |
|---|---|
| `get_current_principal()` | `{did, permissions}` from Flask `g` |
| `get_current_permissions()` | Effective permission code list |
| `has_permission(code)` | Check single code; supports `*` and `domain:*` wildcards |
| `has_any_permission(codes)` | Check if any code matches |
| `require_permission(code)` | Decorator — 403 if missing (use after `@jwt_required`) |
| `require_any_permission(codes)` | Decorator — 403 if none match |
| `safe_permission_denied_response(code_or_list)` | `Result.error` + HTTP 403 |

---

## 4. Permission Source Priority

1. `g.current_principal['permissions']`
2. `g.user_permissions`
3. `g.jwt_payload` fields (in order): `perms`, `permission_codes`, `permissions`

No database lookup. Permissions reflect JWT snapshot at login.

---

## 5. No JWT Payload Change

Login continues to issue `create_jwt({"sub": did, "perms": perms})`. Helper reads existing claim names only.

---

## 6. No DB Permission Query

Phase 1 reads Flask `g` only. Live DB permission refresh is a separate future task.

---

## 7. Follow-up A6B / A7B / A10B

Apply decorators on protected routes:

- **A6B** — `modeling_api.py`
- **A7B** — `iot_api.py` (17 JWT write/command/ingest routes)
- **A10B** — `did_api.py` (5 high-risk POST routes; not login, not `/did/me`)

Decorator order:

```python
@api_bp.route(...)
@jwt_required
@require_permission('domain:action')
def handler():
    ...
```
