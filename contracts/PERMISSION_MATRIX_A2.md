# VANTARIS IBMS Permission Matrix A2

**Task:** IBMS-CONTRACTS-A2  
**Status:** Contract matrix — A6B/A7B/A10B enforced in runtime (commits c236cc4, 7840f0e, d3e2d38)

---

## 1. Scope

- Contract-only permission matrix
- No runtime enforcement in this task
- No DB seed in this task
- No frontend menu change in this task

---

## 2. Permission Naming Rule

Format:

```
<domain>:<action>
```

See `contracts/PERMISSION_BOUNDARY_A0.md` for registry vocabulary. Wildcards (e.g. `iot:*`) reserved for CORE-A1 helper design — not seeded yet.

---

## 3. API Permission Matrix

| API Area | Route Pattern | Method | Current Protection | Target Permission | Enforcement Status |
|---|---|---|---|---|---|
| Modeling | `/api/modeling/csv/list` | GET | JWT + permission (A6B) | `modeling:read` | **Enforced** A6B |
| Modeling | `/api/modeling/csv/{device_code}` | GET | JWT + permission (A6B) | `modeling:read` | **Enforced** A6B |
| Modeling | `/api/modeling/{device_code}/train` | POST | JWT + permission (A6B) | `modeling:train` | **Enforced** A6B |
| Modeling | `/api/modeling/{device_code}/predict` | POST | JWT + permission (A6B) | `modeling:predict` | **Enforced** A6B |
| Modeling | `/api/modeling/{device_code}/predict_future` | POST | JWT + permission (A6B) | `modeling:predict` | **Enforced** A6B |
| Modeling | `/api/modeling/{device_code}/model_info` | GET | JWT + permission (A6B) | `modeling:read` | **Enforced** A6B |
| Modeling | `/api/modeling/{device_code}/{method}` | GET | JWT + permission (A6B) | `modeling:read` or `modeling:predict` | **Enforced** A6B (`require_any`) |
| Modeling | `/api/modeling/{device_code}/{method}` | POST | JWT + permission (A6B) | `modeling:read` or `modeling:predict` | **Enforced** A6B (`require_any`) |
| IoT | `/api/iot/device/register` | POST | JWT + permission (A7B) | `device:manage` | **Enforced** A7B |
| IoT | `/api/iot/device/did/{device_did}` | PUT, PATCH, DELETE | JWT + permission (A7B) | `device:manage` | **Enforced** A7B |
| IoT | `/api/iot/device/did/{device_did}/status` | PUT | JWT + permission (A7B) | `device:manage` | **Enforced** A7B |
| IoT | `/api/iot/device/did/{device_did}/field-mappings` | PUT | JWT + permission (A7B) | `device:manage` | **Enforced** A7B |
| IoT | `/api/iot/device/did/{device_did}/method-mappings` | PUT | JWT + permission (A7B) | `device:manage` | **Enforced** A7B |
| IoT | `/api/iot/device/{device_did}/command` | POST | JWT + permission (A7B) | `iot:command` / `device:control` | **Enforced** A7B (`require_any`) |
| IoT | `/api/iot/device/code/{device_code}/command` | POST | JWT + permission (A7B) | `iot:command` / `device:control` | **Enforced** A7B (`require_any`) |
| IoT | `/api/iot/ingest/http` | POST | JWT + permission (A7B) | `iot:ingest` | **Enforced** A7B |
| IoT | `/api/iot/device/{device_code}/reconnect` | POST | JWT + permission (A7B) | `device:control` | **Enforced** A7B |
| IoT | `/api/iot/standard-fields` | POST | JWT + permission (A7B) | `iot:write` | **Enforced** A7B |
| IoT | `/api/iot/standard-fields/{field_code}` | PUT, DELETE | JWT + permission (A7B) | `iot:write` | **Enforced** A7B |
| IoT | `/api/iot/standard-methods` | POST | JWT + permission (A7B) | `iot:write` | **Enforced** A7B |
| IoT | `/api/iot/standard-methods/{method_code}` | PUT, DELETE | JWT + permission (A7B) | `iot:write` | **Enforced** A7B |
| IoT | `/api/iot/device/{device_code}/test-sse-push` | POST | JWT + prod guard (A8B) | `iot:write` or `iot:test` | JWT + env guard only (no permission decorator) |
| IoT | `/api/iot/device/{device_code}/stream`, `/latest` | GET | **Unprotected** | Pending auth decision | Pending SECURITY-A11 |
| DID | `/api/did/system/init` | POST | JWT + permission (A10B) | `system:admin` or `did:manage` | **Enforced** A10B (`require_any`) |
| DID | `/api/did/entity` | POST | JWT + permission (A10B) | `did:manage` | **Enforced** A10B |
| DID | `/api/did/vp/generate` | POST | JWT + permission (A10B) | `did:issue` | **Enforced** A10B |
| DID | `/api/did/vc/reissue` | POST | JWT + permission (A10B) | `did:issue` | **Enforced** A10B |
| DID | `/api/did/vc/revoke` | POST | JWT + permission (A10B) | `did:revoke` | **Enforced** A10B |
| DID | `/api/did/me` | GET | JWT only (pre-A10) | `did:read` | Pending SECURITY-A10B |
| DID | `/api/did/login`, `/api/did/challenge` | POST, GET | Public | — | N/A |
| System | `/api/system/*` admin routes (`system_api.py`) | various | JWT only (B2) | `system:read` / `system:write` / `system:admin` | JWT only — permission pending SYSTEM-B |
| System menu | `/api/system/versions`, `/api/system/menus*`, `/api/system/menu/*`, `/api/system/version-menus/*` | GET | JWT only (MENU-JWT) | `system:read` | JWT only — permission pending |
| System menu | `/api/system/versions`, `/api/system/menus-add`, `menus-update`, `menus-delete`, `menus/batch-sort`, `/api/system/version-menus/*` batch/incremental/diff, `/api/system/versions/switch/*` | POST, PUT, DELETE | JWT only (MENU-JWT) | `system:write` or `system:admin` | JWT only — permission pending |

**Legend:** A6B/A7B/A10B routes enforce JWT + permission codes via `permission_util`. OpenAPI documents 403 for missing permission (CONTRACTS-A3).

---

## 4. Role Permission Draft

| Role | Suggested Permissions |
|---|---|
| Admin | `system:admin`, `system:write`, `system:read`, `did:manage`, `did:issue`, `did:revoke`, `device:manage`, `iot:*`, `modeling:*`, `audit:read` |
| Supervisor | `system:read`, `did:read`, `did:issue`, `device:manage`, `iot:write`, `iot:command`, `iot:ingest`, `modeling:read`, `modeling:predict`, `modeling:train` |
| Engineer | `modeling:read`, `modeling:predict`, `modeling:train`, `iot:read`, `device:read`, `did:read` |
| Operator | `iot:read`, `device:read`, `iot:command`, `modeling:read`, `modeling:predict`, `did:read` |
| System service | `iot:ingest`, `device:manage`, `did:issue` (machine-scoped), `system:read` |
| Edge machine identity | `iot:ingest`, `device:control` (device-bound), optional `iot:command` for local actuation |

Draft only — role-to-permission mapping requires DB seed and admin UI work.

---

## 5. Enforcement Roadmap

1. **CORE-A1** — implement permission helper (`require_permission`, etc.)
2. **SECURITY-A6B** — modeling route permissions (`modeling:read`, `modeling:train`, `modeling:predict`)
3. **SECURITY-A7B** — IoT write/command/ingest permissions
4. **SECURITY-A10B** — DID high-risk permissions (`did:issue`, `did:revoke`, `did:manage`)
5. **DB seed task** — align `imbs_permission` / user `permission_codes` with matrix
6. **Admin UI mapping task** — frontend menu ↔ permission codes

---

## 6. Non-Scope

- Runtime enforcement
- DB migration
- Seed update
- Frontend permission UI
- JWT payload change

---

## Related Documents

- `contracts/PERMISSION_BOUNDARY_A0.md` — naming registry (A0)
- `contracts/PROTECTED_API_BOUNDARY_A1.md` — JWT-protected route inventory
- `docs/architecture/IBMS_CORE_A0_AUTH_PERMISSION_BOUNDARY.md` — CORE-A0 design
