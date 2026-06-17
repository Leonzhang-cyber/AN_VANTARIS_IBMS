# IBMS Contracts Versioning Policy

**Task:** IBMS-CONTRACTS-A0  
**Status:** Defined (documentation-only)

---

## 1. Version Formats

| Artifact | Format | Example |
|---|---|---|
| Contract version | `ibms.contract.v{N}` | `ibms.contract.v1` |
| API path version | `/api/v{N}/...` | `/api/v1/did/login` |
| JSON Schema ID | `ibms.<domain>.<object>.v{N}` | `ibms.did.entity.v1` |

> **Current backend** uses unversioned paths (`/api/did/*`, `/api/iot/*`, etc.). Future API versions should introduce `/api/v1/` prefix without breaking existing clients until deprecation window closes.

---

## 2. Schema ID Examples

| Schema ID | Purpose |
|---|---|
| `ibms.did.entity.v1` | DID entity object |
| `ibms.did.login-request.v1` | Login request payload |
| `ibms.did.login-response.v1` | Login response (JWT) |
| `ibms.iot.telemetry.v1` | Telemetry ingest payload |
| `ibms.iot.device.v1` | Device registration object |
| `ibms.system.menu.v1` | Menu tree node |
| `ibms.system.permission.v1` | Permission definition |
| `ibms.modeling.prediction.v1` | Prediction request/result |
| `ibms.modeling.train-request.v1` | Model training request |
| `ibms.link.message.v1` | Link ingress message envelope |
| `ibms.error.response.v1` | Standard error response |
| `ibms.storage.object-meta.v1` | Storage object metadata |

---

## 3. File Naming Convention

```
schemas/<domain>.<object>.schema.json
examples/<domain>.<action>.<direction>.json
openapi/ibms-<group>-api.openapi.yaml
```

Examples:

- `schemas/did.login-request.schema.json`
- `schemas/iot.telemetry.schema.json`
- `examples/did.login.request.json`
- `openapi/ibms-did-api.openapi.yaml`

---

## 4. Breaking Changes

The following require a **new major version** (`v1` → `v2`):

| Change Type | Example |
|---|---|
| Remove field | Delete `permissions` from login response |
| Change field type | `deviceId` string → integer |
| Change required fields | Make optional field required |
| Change enum meaning | Redefine `status: "active"` semantics |
| Change authentication | Bearer JWT → mTLS only |
| Change state machine meaning | `resolved` no longer terminal for alarms |
| Change error code semantics | `DEVICE_NOT_FOUND` now includes gateway errors |

Breaking changes **must**:

1. Bump schema/API major version.
2. Document migration path in `docs/contracts/` or architecture notes.
3. Maintain previous version for deprecation period (minimum 90 days for production APIs).

---

## 5. Non-Breaking Changes

The following are **compatible within the same major version**:

| Change Type | Example |
|---|---|
| Add optional field | Add `metadata.tags` to device object |
| Add enum value (backward compatible) | Add `status: "degraded"` without changing existing values |
| Add response metadata | Add `traceId`, `pagination` wrapper |
| Add example file | New file under `examples/` |
| Add OpenAPI description | Documentation-only update |
| Deprecation notice (field retained) | Mark field `deprecated: true` in schema |

---

## 6. Required Schema Fields

Every JSON Schema under `contracts/schemas/` **must** include:

| Field | Required | Notes |
|---|---|---|
| `$schema` | Yes | Draft 2020-12 or org standard |
| `$id` | Yes | e.g. `ibms.did.entity.v1` |
| `schemaVersion` | Yes | Mirror `$id` version string |
| `title` | Yes | Human-readable name |
| `description` | Recommended | Purpose and module ownership |

Request/response payloads **where applicable** must support:

| Field | When |
|---|---|
| `traceId` | All cross-module requests and error responses |
| `timestamp` | Events, telemetry, audit records, async job status |

---

## 7. API Version Migration Strategy

```
Phase 1 (current):  /api/did/login          → document as legacy
Phase 2 (target):   /api/v1/did/login       → contract-backed
Phase 3 (future):   /api/v2/did/login       → breaking change only
```

- Console and external integrators bind to `/api/v{N}/` paths.
- Legacy unversioned paths remain during transition with `Sunset` header.
- Contracts directory holds both v1 and v2 schemas when coexisting.

---

## 8. Ownership

| Domain | Schema prefix | Logical module |
|---|---|---|
| `did.*` | Core / Security | DID identity |
| `system.*` | Core | Administration |
| `iot.*` | Link-like / Edge | Device & telemetry |
| `modeling.*` | NexusAI Interface | ML train/predict |
| `link.*` | Link-like Module | Ingress/delivery |
| `storage.*` | Storage | Object metadata |
| `error.*` | Contracts | Cross-cutting |
