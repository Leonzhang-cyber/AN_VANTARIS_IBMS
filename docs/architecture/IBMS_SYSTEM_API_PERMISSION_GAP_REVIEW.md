# IBMS System API Permission Gap Review

**Task:** IBMS-SECURITY-SYSTEM-B-PREP  
**Date:** 2026-06-16

---

## Current Gaps

| Gap | Detail | Severity |
|---|---|---|
| **menu_api unauthenticated** | 19 routes have no `@jwt_required` — publicly callable | **Critical** |
| **Permission CRUD unguarded** | Any valid JWT can POST/PUT/DELETE `/system/permissions` | **Critical** |
| **JWT without authorization** | `system_api` 21 routes authenticate but do not check `system:*` codes | **High** |
| **Contract vs runtime mismatch** | `PROTECTED_API_BOUNDARY_A1` lists menu routes as JWT-protected (B2 era) — not true in code | **High** |
| **No OpenAPI coverage** | System/menu routes excluded from protected API v1 draft | Medium |

---

## Risk Level Summary

| Module | Auth | Authz | Overall |
|---|---|---|---|
| `system_api.py` | JWT (21/21) | None | High |
| `menu_api.py` | None (0/19) | None | Critical |

An attacker or misconfigured client can mutate menus, versions, and version-menu mappings **without any token**. A holder of any valid JWT can redefine the permission table.

---

## Proposed Enforcement Order

1. **Phase 1 — menu_api JWT** — Add `@jwt_required` to all menu/version routes (except optional public `/system/test` policy decision).
2. **Phase 2 — system:admin on permission CRUD** — Highest blast radius.
3. **Phase 3 — menu/version mutation** — `system:admin` or `system:write`.
4. **Phase 4 — system_api read routes** — `system:read`.
5. **Phase 5 — entity-type admin** — `system:admin`.
6. **Phase 6 — contracts/OpenAPI** — Add system routes to protected draft.

---

## Backward Compatibility Risk

- Frontend may call menu/version APIs without Authorization today — **breaking change** when JWT added.
- Console admin users need `system:read` / `system:write` / `system:admin` in JWT `perms` after seed.
- Empty-`perms` JWT holders will get 403 on all system routes post-enforcement (same as A6B/A7B/A10B lockout pattern).

---

## Rollback Strategy

1. Revert SYSTEM-B commit(s) — restore menu_api without JWT and system_api without permission decorators.
2. Keep JWT on system_api if menu JWT was merged separately — document partial rollback.
3. Seed rollback independent — codes in DB do not require code revert.

---

## Related Documents

- `docs/security/IBMS_SECURITY_SYSTEM_B_PREP.md`
- `contracts/PROTECTED_API_BOUNDARY_A1.md`
- `docs/security/IBMS_PERMISSIONS_A0_LOCKOUT_RISK_REVIEW.md`
