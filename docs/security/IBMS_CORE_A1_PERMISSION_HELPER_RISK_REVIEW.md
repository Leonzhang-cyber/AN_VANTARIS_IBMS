# IBMS Core A1 Permission Helper Risk Review

**Task:** IBMS-CORE-A1-PREP  
**Type:** Security prep — no runtime changes

---

## 1. Permission Helper Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | JWT `perms` empty for valid users | Medium | High — 403 lockout after enforcement | Seed default permissions; grace period logging before hard deny |
| R2 | Stale permissions in token vs DB | High | Medium — revoked user retains access until expiry | Document re-login requirement; optional future token refresh task |
| R3 | Wildcard `*` in root entity permissions | Low | High — over-broad access | Explicit policy: `*` only for system root; helper treats `*` as superuser |
| R4 | Inconsistent permission code strings | Medium | Medium — false denials | Enforce A0/A2 registry; validate at seed time |
| R5 | Decorator ordering bugs | Medium | High — unauthenticated access | Standard pattern: JWT before permission; code review checklist |
| R6 | menu_api unprotected | Known | High — admin menu CRUD without JWT | Separate security task; do not assume menu routes are protected |
| R7 | system permission CRUD without admin check | Known | Critical — any JWT can edit permission table | Target `system:admin` on first enforcement wave |
| R8 | Breaking existing API clients | Medium | High | Phased rollout: log-only mode before 403 |

---

## 2. Non-Scope (this prep task)

- Runtime helper implementation
- DB migration or seed updates
- JWT payload / login changes
- Frontend permission UI
- Contract file changes
- Automated tests
- Service startup or dependency installation

---

## 3. Required Preconditions

Before CORE-A1 implementation merges:

1. **Frozen permission vocabulary** — `contracts/PERMISSION_BOUNDARY_A0.md` and `PERMISSION_MATRIX_A2.md` reviewed by security owner.
2. **Login emits `perms`** — already true via `create_jwt({"sub", "perms"})`; confirm test users have non-empty `permission_codes` in DB for staging validation.
3. **Decorator inventory** — all routes in matrix identified; gaps (e.g. `menu_api`) tracked as blockers or parallel fixes.
4. **403 response shape** — align with existing `Result.error(message=..., code=403)` pattern used by SSE production guard.
5. **Rollback plan agreed** — feature flag or revert commits per domain (A6B/A7B/A10B).

---

## 4. Rollback Strategy

1. **Per-domain revert** — SECURITY-A6B/A7B/A10B commits can revert permission decorators while leaving `jwt_required` in place.
2. **Helper-only revert** — remove `permission_util.py` and decorator imports; routes fall back to JWT-only behavior (current state).
3. **Log-only mode (recommended interim)** — helper logs `[AUTHZ] denied` but does not return 403; remove after seed validation.
4. **No DB rollback required** — phase 1 reads JWT payload only; no schema dependency.

---

## 5. Verification Plan

Manual / dry review (no test execution in batch rules):

| Step | Action |
|---|---|
| V1 | Inventory routes with `@jwt_required` vs A2 matrix |
| V2 | Confirm login payload includes `perms` for sample DIDs |
| V3 | Document expected 403 for missing permission per route |
| V4 | Confirm no change to JWT secret, expiry, or login challenge flow |
| V5 | Review `menu_api` and unprotected GET policy separately |
| V6 | Post-A6B/A7B/A10B: spot-check 401 (no token) vs 403 (token, no perm) |

Future automated contract tests (CONTRACTS-A4) should assert 401 without JWT and 403 without permission once enforcement lands.

---

## Related Documents

- `docs/architecture/IBMS_CORE_A1_PERMISSION_HELPER_PREP.md`
- `contracts/PERMISSION_MATRIX_A2.md`
- `docs/security/IBMS_CORE_A0_AUTH_PERMISSION_SECURITY_MAPPING.md`
