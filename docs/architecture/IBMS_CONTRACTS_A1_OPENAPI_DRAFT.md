# IBMS Contracts A1 OpenAPI Draft Completion

**Task ID:** IBMS-CONTRACTS-A1-OPENAPI  
**Date:** 2026-06-16  
**Type:** Contract documentation only — no runtime changes

---

## 1. Task Scope

- Task ID: IBMS-CONTRACTS-A1-OPENAPI
- Contract documentation only
- No runtime source code changed
- No frontend code changed
- No service started
- No dependency installed

---

## 2. Inputs

| Input | Reference |
|---|---|
| CONTRACTS-A1 protected API boundary | `contracts/PROTECTED_API_BOUNDARY_A1.md` |
| SECURITY-A6 | Modeling JWT (7 routes) |
| SECURITY-A7 | IoT write JWT (17 routes) |
| SECURITY-A8B | SSE test endpoint guard |
| SECURITY-A10 | DID high-risk JWT (5 routes) |
| CORE-A0 | Auth/permission boundary design |

---

## 3. Outputs

| File | Purpose |
|---|---|
| `contracts/openapi/ibms-protected-api-v1.openapi.yaml` | OpenAPI 3.0.3 draft for protected routes |
| `contracts/openapi/README.md` | Updated index and status |
| `docs/architecture/IBMS_CONTRACTS_A1_OPENAPI_DRAFT.md` | This completion report |

---

## 4. Coverage

| Domain | Paths in draft |
|---|---|
| Modeling | 7 path patterns (csv, train, predict, predict_future, model_info, generic method) |
| IoT protected | 13 path patterns (register, device CRUD, mappings, command, ingest, reconnect, standard field/method) |
| SSE test | 1 path (`test-sse-push`) with 403 note |
| DID high-risk | 5 paths (system/init, entity, vp/generate, vc/reissue, vc/revoke) |

Global: `bearerAuth`, optional `X-Trace-Id`, shared error response components.

---

## 5. Draft Limitations

- Schemas are draft placeholders where runtime request bodies are not fully confirmed (`additionalProperties: true` where needed).
- Permission matrix not enforced in runtime — OpenAPI documents JWT only.
- Contract tests not included.
- Full OpenAPI validation not executed in this task (no spectral/redocly run).
- Unprotected routes (IoT GET, DID GET, SSE stream/latest, login) intentionally excluded.
- System API routes not included in this v1 protected draft.

---

## 6. A10 Follow-up Sync (898f99c)

Commit `898f99c` added the missing `@jwt_required` guard on `POST /api/did/vc/revoke` (`revoke_vc`). This follow-up task (IBMS-CONTRACTS-A1-OPENAPI-FIX) synced that route into:

| Artifact | Update |
|---|---|
| `contracts/openapi/ibms-protected-api-v1.openapi.yaml` | Explicit `bearerAuth`, draft request body, responses 200/400/401/403/500 |
| `contracts/PROTECTED_API_BOUNDARY_A1.md` | DID protected inventory includes `vc/revoke` |
| `docs/security/IBMS_SECURITY_A10_DID_API_PROTECTION.md` | 898f99c follow-up note |
| `docs/architecture/IBMS_CONTRACTS_A1_OPENAPI_DRAFT.md` | This section |

No runtime source changes in the contract sync task.

---

## 7. Recommended Next Tasks

- IBMS-CONTRACTS-A2 — permission matrix in contracts
- IBMS-CONTRACTS-A3 — schema examples with JSON Schema refs
- IBMS-CONTRACTS-A4 — contract validation tests (401/403)
- IBMS-CORE-A1 — permission helper aligned with OpenAPI security extensions
