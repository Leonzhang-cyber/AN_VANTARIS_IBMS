# IBMS CONTRACTS-B3 — OpenAPI Risk Review

**Task:** CONTRACTS-B3  
**Review type:** Static contract completion (no runtime)

---

## OpenAPI still draft

Both `ibms-frontend-api-v1.openapi.yaml` and `ibms-protected-api-v1.openapi.yaml` remain **draft** specifications. Schemas use `additionalProperties: true` placeholders. Do not treat generated clients or docs as production-ready without runtime validation.

---

## Static route mismatch risk

CONTRACTS-B2 validation compares literal Flask `@route` paths to OpenAPI path keys. Contract alias paths (e.g. `/system/menu`) will continue to appear as “missing” relative to Flask even when correctly documented with `x-ibms-backend-route`.

Risk: engineers may assume 100% path parity from validator output alone. Always read alias annotations and protected vs frontend spec intent.

---

## System / menu permission pending risk

Menu and permission write routes document **403 ForbiddenError**, but runtime `@require_permission` for `system:admin` / `system:write` may not be fully applied on all menu endpoints.

Risk: authenticated users could mutate menus or permissions until backend enforcement lands (SYSTEM-B). Frontend OpenAPI must not be interpreted as proof of authorization.

---

## No runtime changed

This batch modified OpenAPI YAML and documentation only. No backend decorators, middleware, or frontend API modules were altered in CONTRACTS-B3.

---

## No service started

No Flask app, database, or frontend dev server was run. Coverage improvements are from static scan of `menu_api.py`, `system_api.py`, and existing B2 tooling.

---

## Next validation requirement

Before production SDK or contract tests:

1. Start backend with test JWT and verify each documented system/menu route (status codes, 403 when permission denied).
2. Run CONTRACTS-B4 method-level diff if available.
3. Re-run `validate_flask_openapi_routes.py` after any backend path refactor.
4. Align `x-ibms-required-permission` extensions when PERMISSION_MATRIX work completes.

---

## High-risk surfaces documented

| Surface | Risk |
|---|---|
| POST/PUT/DELETE `/system/permissions/*` | Expands authorization model |
| Menu version switch | Changes active navigation for all users |
| Version-menu batch/incremental/diff | Bulk navigation mutations |

Treat these as administrator-only in deployment policy regardless of OpenAPI draft status.
