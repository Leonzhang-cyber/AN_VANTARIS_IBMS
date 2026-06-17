# IBMS Contracts Menu JWT Sync

**Task ID:** IBMS-CONTRACTS-MENU-JWT-SYNC  
**Date:** 2026-06-16

---

## 1. Task Scope

- Contract documentation only
- menu_api JWT state synced
- No runtime source changed
- No frontend changed
- No DB changed

---

## 2. Inputs

| Input | Reference |
|---|---|
| MENU-JWT | Commit `56234d8` — 19 `menu_api.py` routes `@jwt_required` |
| SYSTEM-B-PREP | Gap analysis — permission enforcement pending |
| Contracts A1/A2/A3 | Protected boundary, matrix, 403 sync |

---

## 3. Outputs

| File | Change |
|---|---|
| `contracts/openapi/ibms-protected-api-v1.openapi.yaml` | System tag + draft menu/version paths with bearerAuth, 401/500; write routes include 403 (permission pending note) |
| `contracts/PROTECTED_API_BOUNDARY_A1.md` | Split system_api vs menu_api; MENU-JWT status |
| `contracts/PERMISSION_MATRIX_A2.md` | Menu route rows — JWT only, permission pending |
| `docs/architecture/IBMS_CONTRACTS_MENU_JWT_SYNC.md` | This document |

---

## 4. Current Menu API Contract State

| Property | Status |
|---|---|
| **JWT** | Required on all 19 `menu_api.py` routes |
| **Permission** | **Not enforced** — `system:read` / `system:write` / `system:admin` are target codes only |
| **403 in OpenAPI** | Documented on write routes as *permission enforcement pending* (not active in runtime) |
| **Frontend** | Must send `Authorization: Bearer` — compatibility verification pending |

Runtime paths use concrete names (`menus-add`, `version-menus/{version_code}`) rather than generic `/menu/{id}` — OpenAPI uses draft groupings with descriptions mapping to actual handlers.

---

## 5. Pending

- `system:read` / `system:write` / `system:admin` enforcement (IBMS-SECURITY-SYSTEM-B)
- DB seed + user permission assignment execution
- Frontend token compatibility check on all menu/version calls
- Contract validation tests (CONTRACTS-A4)
- OpenAPI lint; optional full 19-route explicit listing

---

## Related Documents

- `docs/security/IBMS_SECURITY_MENU_JWT_PROTECTION.md`
- `docs/security/IBMS_SECURITY_SYSTEM_B_PREP.md`
