# IBMS Contracts A3 Permission Response Sync

**Task ID:** IBMS-CONTRACTS-A3  
**Date:** 2026-06-16  
**Type:** Contract documentation only — no runtime changes

---

## 1. Task Scope

- Contract documentation only
- No runtime source changed
- No frontend changed
- No DB changed

---

## 2. Inputs

| Input | Reference |
|---|---|
| CORE-A1 | `permission_util` — 403 on missing permission |
| SECURITY-A6B | Modeling permission enforcement |
| SECURITY-A7B | IoT 17-route permission enforcement |
| SECURITY-A10B | DID 5-route permission enforcement |
| SECURITY-A8B | SSE test production / feature-flag 403 |
| CONTRACTS-A2 | `PERMISSION_MATRIX_A2.md` |

---

## 3. Outputs

| File | Change |
|---|---|
| `contracts/openapi/ibms-protected-api-v1.openapi.yaml` | `403 ForbiddenError` on 30 path operations; updated component description + example |
| `contracts/PERMISSION_MATRIX_A2.md` | Enforcement status → **Enforced** for A6B/A7B/A10B rows |
| `contracts/PROTECTED_API_BOUNDARY_A1.md` | 401 vs 403 boundary, updated protection summary |
| `docs/architecture/IBMS_CONTRACTS_A3_PERMISSION_RESPONSE_SYNC.md` | This document |

---

## 4. 401 vs 403 Boundary

| HTTP | Meaning | Runtime source |
|---|---|---|
| **401** | Missing, invalid, or expired JWT | `@jwt_required` |
| **403** | Valid JWT but missing required permission code | `@require_permission` / `@require_any_permission` |
| **403** | Environment guard (production SSE test, feature flags) | `sse_api` A8B guards |

403 body follows existing `Result.error` envelope:

```json
{
  "code": 403,
  "message": "Permission denied: requires [modeling:train]"
}
```

---

## 5. Coverage

| Domain | OpenAPI paths | 403 reason |
|---|---|---|
| **Modeling** | 7 route patterns (8 operations incl. GET/POST `{method}`) | Missing `modeling:read` / `train` / `predict` |
| **IoT** | 17 write/command/ingest operations | Missing `device:manage`, `iot:command`, `device:control`, `iot:ingest`, `iot:write` |
| **DID** | 5 high-risk POST | Missing `did:issue`, `did:revoke`, `did:manage`, `system:admin` |
| **SSE test** | `test-sse-push` | Production / feature-flag guard (A8B); no permission decorator in runtime |

---

## 6. Pending

- Contract validation tests (CONTRACTS-A4) — assert 401 vs 403
- Real OpenAPI lint (Spectral / Redocly)
- DB seed alignment so integrators receive non-empty `perms`
- System / menu routes not in OpenAPI v1 draft

---

## Related Documents

- `contracts/openapi/ibms-protected-api-v1.openapi.yaml`
- `docs/security/IBMS_SECURITY_A6B_MODELING_PERMISSION_ENFORCEMENT.md`
- `docs/security/IBMS_SECURITY_A7B_IOT_PERMISSION_ENFORCEMENT.md`
- `docs/security/IBMS_SECURITY_A10B_DID_PERMISSION_ENFORCEMENT.md`
