# IBMS OpenAPI Directory

**Task:** IBMS-CONTRACTS-A0 / A1-OPENAPI  
**Status:** Protected API draft added — full per-group specs pending

---

## Purpose

本目录存放 IBMS REST API 的 OpenAPI 3.x 规范。每个文件对应一个 API 分组（见 [API_GROUPS.md](../API_GROUPS.md)）。

---

## Published / Draft Files

| File | API Group | Status | Source |
|---|---|---|---|
| `ibms-protected-api-v1.openapi.yaml` | Protected boundary (Modeling + IoT write + SSE test + DID high-risk) | **Draft** | A6, A7, A8B, A10, CONTRACTS-A1, CORE-A0, **CONTRACTS-B6** |
| `ibms-frontend-api-v1.openapi.yaml` | Frontend-facing subset (System/Menu + DID + IoT + Modeling) | **Draft** | CONTRACTS-B1, FRONTEND-A4, CONTRACTS-B3, **CONTRACTS-B5** |

### Frontend API contract (`ibms-frontend-api-v1.openapi.yaml`)

- **Audience:** `AN_VANTARIS_IBMS-frontend` domain API modules
- **Version:** `ibms.frontend.contract.v1`
- **Server:** `/api` (legacy unversioned prefix)
- **Security:** `bearerAuth` (JWT); `/did/login` is public
- **401:** All protected routes
- **403:** Routes with backend `@require_permission` (modeling, IoT write, DID mutate); system/menu write routes note permission pending with unified forbidden description (CONTRACTS-B3)
- **500:** System and menu protected routes include server error response (CONTRACTS-B3)
- **Path mapping:** Contract paths may differ from Flask routes — see `x-ibms-backend-route` extensions (e.g. `/system/menu` → `/system/menus-add`)

See: `docs/architecture/IBMS_CONTRACTS_B1_FRONTEND_API_SUBSET.md`  
See: `docs/architecture/IBMS_CONTRACTS_B3_SYSTEM_MENU_OPENAPI_COMPLETION.md`

### Route validation (CONTRACTS-B2)

Static comparison of Flask `@route` paths vs OpenAPI yaml (no service, no DB):

```bash
python3 contracts/tools/validate_flask_openapi_routes.py \
  --backend-root AN_VANTARIS_IBMS-backend/src/api \
  --openapi-dir contracts/openapi
```

See: `docs/architecture/IBMS_CONTRACTS_B2_ROUTE_VALIDATION.md`

### Method validation (CONTRACTS-B4)

HTTP verb-level comparison (path + method) — complements B2:

```bash
python3 contracts/tools/validate_flask_openapi_methods.py \
  --backend-root AN_VANTARIS_IBMS-backend/src/api \
  --openapi-dir contracts/openapi
```

Reports Flask `(path, method)` pairs missing from OpenAPI and OpenAPI-only operations (contract aliases). Exit code `0` even when diffs exist; `2` if input directories missing.

See: `docs/architecture/IBMS_CONTRACTS_B4_METHOD_VALIDATION.md`

### DID / IoT OpenAPI completion (CONTRACTS-B5)

Method-level gaps for DID read/verify and IoT device/stream routes closed per B4 output. Public-runtime routes documented with `security: []` and auth-pending notes.

See: `docs/architecture/IBMS_CONTRACTS_B5_DID_IOT_OPENAPI_COMPLETION.md`

### System admin OpenAPI completion (CONTRACTS-B6)

Closes remaining B5 method-level gaps for entity-types, system standard-fields/methods (Flask runtime paths), and `/system/test` diagnostic route.

See: `docs/architecture/IBMS_CONTRACTS_B6_SYSTEM_OPENAPI_COMPLETION.md`

---

## Planned OpenAPI Files

| File | API Group | Current Backend Prefix | Logical Module |
|---|---|---|---|
| `ibms-did-api.openapi.yaml` | DID API (full) | `/api/did/*` | Core / Security |
| `ibms-system-api.openapi.yaml` | System API | `/api/system/*` | Core / Administration |
| `ibms-iot-api.openapi.yaml` | IoT + SSE API (full) | `/api/iot/*` | Link-like / Edge |
| `ibms-modeling-api.openapi.yaml` | Data Modeling API | `/api/modeling/*` | NexusAI Interface |
| `ibms-core-api.openapi.yaml` | Aggregated Core surface | (future `/api/v1/*`) | Core |
| `ibms-console-api.openapi.yaml` | Console client contract | (future) | Console → Core only |

---

## Optional / Dev-Only

| File | Purpose |
|---|---|
| `ibms-edge-simulator.openapi.yaml` | Document testMQTT mock routes (dev reference only) |

> Simulator OpenAPI **must** be marked `x-ibms-environment: development-only` and excluded from production SDK generation.

---

## OpenAPI Conventions

Each spec **should** include:

```yaml
openapi: 3.0.3
info:
  title: VANTARIS IBMS Protected API
  version: ibms.contract.v1
servers:
  - url: /api
security:
  - bearerAuth: []
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

Common headers in protected draft:

- `Authorization: Bearer <token>`
- `X-Trace-Id` (optional, audit)
- `Content-Type: application/json`

---

## Version Alignment

- OpenAPI `info.version` maps to `ibms.contract.vN` (see [VERSIONING.md](../VERSIONING.md)).
- Path versioning: prefer `/api/v1/...` in new specs; document legacy `/api/...` as current backend.
- Schema `$ref` points to `../schemas/*.schema.json` (pending A3).

---

## Pending

- Full schema validation against runtime
- Permission matrix (`x-ibms-required-permission`) — CONTRACTS-A2
- Contract tests — CONTRACTS-A4
- Split protected draft into per-group specs if needed

---

## Related

- [PROTECTED_API_BOUNDARY_A1.md](../PROTECTED_API_BOUNDARY_A1.md)
- [PERMISSION_BOUNDARY_A0.md](../PERMISSION_BOUNDARY_A0.md)
- [examples/protected-api-request-example.md](../examples/protected-api-request-example.md)
