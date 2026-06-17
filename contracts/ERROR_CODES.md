# IBMS Error Codes

**Task:** IBMS-CONTRACTS-A0  
**Status:** Baseline registry defined (documentation-only)

---

## 1. Standard Error Response Format

All API error responses **should** conform to:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_SCHEMA",
    "message": "Request payload is invalid",
    "details": []
  },
  "traceId": "trace-xxx",
  "timestamp": "2026-01-01T00:00:00Z"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `success` | boolean | Yes | Always `false` for errors |
| `error.code` | string | Yes | Machine-readable code from this registry |
| `error.message` | string | Yes | Human-readable, no secrets/SQL/stack traces |
| `error.details` | array | No | Field-level validation errors |
| `traceId` | string | Yes | Distributed trace ID |
| `timestamp` | string (ISO 8601) | Yes | UTC |

Schema ID: `ibms.error.response.v1`

---

## 2. General Errors

| Code | HTTP | Description |
|---|---|---|
| `INVALID_REQUEST` | 400 | Malformed request (syntax, missing Content-Type) |
| `INVALID_SCHEMA` | 400 | Payload fails JSON Schema validation |
| `UNAUTHORIZED` | 401 | Authentication required or failed |
| `FORBIDDEN` | 403 | Authenticated but not permitted |
| `NOT_FOUND` | 404 | Resource does not exist |
| `CONFLICT` | 409 | State conflict (duplicate, version mismatch) |
| `RATE_LIMITED` | 429 | Rate limit exceeded |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## 3. Authentication & Authorization

| Code | HTTP | Description |
|---|---|---|
| `TOKEN_MISSING` | 401 | Authorization header absent |
| `TOKEN_INVALID` | 401 | JWT malformed or signature invalid |
| `TOKEN_EXPIRED` | 401 | JWT expired |
| `PERMISSION_DENIED` | 403 | User lacks required permission |
| `RBAC_SCOPE_DENIED` | 403 | Action outside tenant/site/DID scope |

---

## 4. Data Layer

| Code | HTTP | Description |
|---|---|---|
| `DB_UNAVAILABLE` | 503 | Database connection failed |
| `DB_CONSTRAINT_VIOLATION` | 409 | Unique/FK constraint violation |
| `DATA_NOT_FOUND` | 404 | Record not found in persistence layer |
| `DUPLICATE_RECORD` | 409 | Insert would duplicate existing record |

---

## 5. IoT / Link-like

| Code | HTTP | Description |
|---|---|---|
| `DEVICE_NOT_FOUND` | 404 | Device DID or code unknown |
| `DEVICE_OFFLINE` | 409 | Device not connected |
| `TELEMETRY_INVALID` | 400 | Telemetry payload invalid |
| `INGESTION_REJECTED` | 422 | Message failed validation at ingress |
| `MQTT_UNAVAILABLE` | 503 | MQTT broker unreachable |
| `COMMAND_REJECTED` | 422 | Device rejected or could not execute command |

---

## 6. DID / Blockchain

| Code | HTTP | Description |
|---|---|---|
| `DID_NOT_FOUND` | 404 | DID does not resolve |
| `VC_INVALID` | 400 | Verifiable Credential invalid |
| `VP_INVALID` | 400 | Verifiable Presentation invalid |
| `SIGNATURE_INVALID` | 401 | Cryptographic signature verification failed |
| `CHAIN_UNAVAILABLE` | 503 | Blockchain node unreachable |
| `ANCHOR_FAILED` | 502 | On-chain anchor transaction failed |

---

## 7. AI / Modeling

| Code | HTTP | Description |
|---|---|---|
| `MODEL_NOT_FOUND` | 404 | No model registered for device |
| `MODEL_UNAVAILABLE` | 503 | Model file missing or unloadable |
| `PREDICTION_FAILED` | 422 | Inference execution failed |
| `TRAINING_FAILED` | 422 | Training job failed |
| `MODEL_ARTIFACT_MISSING` | 404 | Expected pkl/artifact not on disk |

---

## 8. Storage

| Code | HTTP | Description |
|---|---|---|
| `FILE_TOO_LARGE` | 413 | Upload exceeds size limit |
| `FILE_TYPE_NOT_ALLOWED` | 415 | MIME/extension not permitted |
| `OBJECT_NOT_FOUND` | 404 | Storage object does not exist |
| `SIGNED_URL_EXPIRED` | 410 | Pre-signed URL no longer valid |

---

## 9. Mapping to Current Backend

Current backend uses `src/common/models/response.py` with numeric codes (e.g. `UNAUTHORIZED = 40001`, `PERMISSION_DENIED = 41006`, `DID_INVALID = 41001`).

| Current (numeric) | Future (string) | Notes |
|---|---|---|
| `40001` UNAUTHORIZED | `UNAUTHORIZED` / `TOKEN_*` | Migrate in A1 |
| `41006` PERMISSION_DENIED | `PERMISSION_DENIED` | |
| `41001` DID_INVALID | `DID_NOT_FOUND` / `VC_INVALID` | Split by context |
| `41004` VP_VERIFY_FAILED | `VP_INVALID` | |

Future schemas and OpenAPI **should** use string codes from this registry. Numeric codes may remain as `error.legacyCode` during migration.

---

## 10. File Placement

| Artifact | Path |
|---|---|
| Error code registry (this file) | `contracts/ERROR_CODES.md` |
| Error response schema | `contracts/schemas/error-response.schema.json` (A1) |
| Example payloads | `contracts/examples/error.*.json` (A1) |
| Machine-readable export | `contracts/errors/` (future JSON index) |
