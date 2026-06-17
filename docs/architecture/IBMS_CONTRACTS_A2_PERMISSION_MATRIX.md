# IBMS Contracts A2 Permission Matrix Completion

**Task ID:** IBMS-CONTRACTS-A2  
**Date:** 2026-06-16  
**Type:** Contract documentation only — no runtime changes

---

## 1. Task Scope

- Define API-to-permission matrix contract from CORE-A0 naming
- Map modeling, IoT, DID, SSE, and system admin routes to target permission codes
- Draft role permission bundles for future seed and UI work
- No runtime enforcement, no DB seed, no frontend changes

---

## 2. Inputs

| Input | Reference |
|---|---|
| CORE-A0 permission naming | `contracts/PERMISSION_BOUNDARY_A0.md`, `docs/architecture/IBMS_CORE_A0_AUTH_PERMISSION_BOUNDARY.md` |
| SECURITY-A6 | Modeling JWT protection |
| SECURITY-A7 | IoT write/command JWT protection |
| SECURITY-A10 / 898f99c | DID high-risk JWT including `vc/revoke` |
| SECURITY-A8B | SSE test endpoint guard |
| CONTRACTS-A1 | Protected API boundary and OpenAPI draft |

---

## 3. Outputs

| File | Purpose |
|---|---|
| `contracts/PERMISSION_MATRIX_A2.md` | Primary API permission matrix and role draft |
| `contracts/PERMISSION_BOUNDARY_A0.md` | Link to A2 matrix (A0 semantics unchanged) |
| `contracts/README.md` | Index entry for A2 |
| `docs/architecture/IBMS_CONTRACTS_A2_PERMISSION_MATRIX.md` | This completion report |

---

## 4. Current Limitation

The matrix is **not enforced** in runtime. All listed routes (except public login/challenge and documented unprotected reads) require JWT only via `@jwt_required`. JWT payload may include `perms` from login, but route handlers do not yet call a permission helper.

---

## 5. Recommended Next Tasks

1. **IBMS-CORE-A1** — implement `require_permission()` helper (prep in CORE-A1-PREP docs)
2. **IBMS-SECURITY-A6B / A7B / A10B** — enforce matrix per domain
3. **IBMS-SECURITY-A11** — SSE stream/latest auth policy decision
4. **DB seed + admin UI** — align roles and `permission_codes` with matrix
5. **IBMS-CONTRACTS-A3 / A4** — schema examples and contract tests (401/403)
