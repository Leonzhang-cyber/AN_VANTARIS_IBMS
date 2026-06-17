# IBMS CONTRACTS-B5 — DID / IoT OpenAPI Completion

**Task:** CONTRACTS-B5  
**Status:** Complete (static contract update only)  
**Prior work:** CONTRACTS-B4 method validation

---

## Task scope

Close **method-level** OpenAPI gaps for DID and IoT route groups identified by B4 static validation. Update frontend-facing and protected OpenAPI drafts without modifying runtime code.

In scope:

- DID read, verify, challenge, login, subordinates, chain routes
- IoT device read, stream, standard dictionary, mapping info routes
- Consistent 401/403 semantics for JWT-protected writes
- Public-runtime routes documented with `security: []` and auth-pending notes

Out of scope:

- System standard-fields / entity-types (deferred to SYSTEM OpenAPI batch)
- Backend / frontend runtime changes
- Live API verification

---

## Inputs from B4 method validation

**Before B5** (commit `ab797f7`):

| Metric | Value |
|---|---|
| Flask route-method pairs | 97 |
| OpenAPI operations (union) | 73 |
| Missing in OpenAPI | **40** |
| OpenAPI-only (contract aliases) | 9 |

DID/IoT missing examples: `/did/challenge`, `/did/entity/{did}`, `/did/vp/verify`, `/iot/device/{device_code}/stream`, `/iot/standard-methods`, etc.

**After B5** (this commit):

| Metric | Value |
|---|---|
| Flask route-method pairs | 97 |
| OpenAPI operations (union) | **96** |
| Missing in OpenAPI | **17** (system admin only) |
| OpenAPI-only | 9 (unchanged contract aliases) |

All DID and IoT Flask route-methods from B4 missing list are now covered in OpenAPI.

---

## Files changed

| File | Change |
|---|---|
| `contracts/openapi/ibms-frontend-api-v1.openapi.yaml` | Frontend DID/IoT subset expansion |
| `contracts/openapi/ibms-protected-api-v1.openapi.yaml` | Full DID read + IoT read/stream coverage |
| `contracts/openapi/README.md` | B5 reference |

---

## DID routes completed

| Path | Methods | Auth notes |
|---|---|---|
| `/did/login` | POST | Public (`security: []`) |
| `/did/me` | GET | JWT — 401 |
| `/did/challenge` | GET | Public |
| `/did/entity` | POST | JWT + 403 (existing) |
| `/did/entity/{did}` | GET | Public — auth pending |
| `/did/vp/generate` | POST | JWT + 403 (existing) |
| `/did/vp/verify` | POST | Public |
| `/did/vc/status` | POST | Public |
| `/did/vc/reissue` | POST | JWT + 403 (existing) |
| `/did/vc/revoke` | POST | JWT + 403 (existing) |
| `/did/system/init` | POST | JWT + 403 (existing) |
| `/did/subordinates/direct` | GET | Public |
| `/did/subordinates/tree` | GET | Public |
| `/did/subordinates/flat` | GET | Public |
| `/did/chain/entity-hash/{did}` | GET | Public |
| `/did/chain/vc-hash/{vc_id}` | GET | Public |
| `/did/chain/events` | GET | Public |
| `/did/verify/entity/{did}` | GET | Public |

No Flask `/did/entities` route — not documented.

---

## IoT routes completed

| Path | Methods | Auth notes |
|---|---|---|
| `/iot/device/register` | POST | JWT + 403 (existing) |
| `/iot/device/parent/{parent_did}` | GET | Public — auth pending |
| `/iot/device/did/{device_did}` | GET, PUT, PATCH, DELETE | GET public; writes JWT + 403 |
| `/iot/device/code/{device_code}` | GET | Public |
| `/iot/device/did/{device_did}/status` | PUT | JWT + 403 (existing) |
| `/iot/device/did/{device_did}/field-mappings` | PUT | JWT + 403 (existing) |
| `/iot/device/did/{device_did}/method-mappings` | PUT | JWT + 403 (existing) |
| `/iot/device/{device_did}/command` | POST | JWT + 403 (existing) |
| `/iot/device/code/{device_code}/command` | POST | JWT + 403 |
| `/iot/ingest/http` | POST | JWT + 403 (existing) |
| `/iot/device/{device_code}/reconnect` | POST | JWT + 403 (existing) |
| `/iot/device/{device_code}/sse-url` | GET | Public |
| `/iot/device/{device_code}/stream` | GET, OPTIONS | Public — SSE auth pending |
| `/iot/device/{device_code}/latest` | GET | Public |
| `/iot/device/{device_code}/test-sse-push` | POST | JWT + 403 (existing) |
| `/iot/standard-fields` | GET, POST, … | GET public; write JWT + 403 |
| `/iot/standard-fields/{field_code}` | GET, PUT, DELETE | GET public; write JWT + 403 |
| `/iot/standard-methods` | GET, POST, … | GET public; write JWT + 403 |
| `/iot/standard-methods/{method_code}` | GET, PUT, DELETE | GET public; write JWT + 403 |
| `/iot/{device_did}/field-mappings-info` | GET | Public |
| `/iot/{device_did}/method-mappings-info` | GET | Public |

No Flask `/iot/devices` list route — not documented.

---

## Runtime alias notes

Frontend contract paths align with Flask runtime paths for DID/IoT in this batch. Param names normalized by B4 validator (`<device_code>` ↔ `{device_code}`).

Protected spec is superset; frontend spec includes migration-facing subset only.

---

## 401 / 403 rule

| Route class | OpenAPI security | Responses |
|---|---|---|
| JWT write (`@jwt_required` + `@require_permission`) | `bearerAuth` | 401, 403, 500 |
| JWT read only (`@jwt_required`) | `bearerAuth` | 401, 500 |
| Public runtime (no JWT decorator) | `security: []` | 200/500; description notes auth pending |

Write routes retain `403 ForbiddenError` with permission semantics consistent with B3.

---

## Remaining gaps (17 route-methods)

All remaining missing operations are **system admin** routes (standard-fields CRUD, entity-types, `/system/test`) — out of B5 scope:

- `/system/create-standard-fields`, `/system/list-standard-fields`, …
- `/system/entity-types*`
- `/system/test`

Contract alias operations (9) unchanged — expected OpenAPI-only entries.

---

## Not changed

- `AN_VANTARIS_IBMS-backend/src/**`
- `AN_VANTARIS_IBMS-frontend/src/**`
- No services started
