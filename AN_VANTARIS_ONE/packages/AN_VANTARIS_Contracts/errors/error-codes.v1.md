# Error Codes (v1)

Canonical error codes for cross-package responses. All codes use `error-response.v1.schema.json`.

## Transport and validation

| Code | HTTP | Description |
|------|------|-------------|
| `INVALID_SCHEMA` | 400 | Payload failed JSON Schema validation |
| `INVALID_ENVELOPE` | 400 | Missing required envelope fields |
| `UNSUPPORTED_VERSION` | 400 | Unknown schemaVersion |
| `UNAUTHORIZED` | 401 | Missing or invalid credentials |
| `FORBIDDEN_BOUNDARY` | 403 | Caller violates package communication rules |

## LINK ↔ Code

| Code | HTTP | Description |
|------|------|-------------|
| `DUPLICATE_MESSAGE` | 409 | messageId or dedupeKey already processed |
| `DELIVERY_REJECTED` | 422 | Policy rejection after schema pass |
| `LINK_ACK_UNKNOWN` | 404 | Ack references unknown messageId |

## Code ↔ NexusAI

| Code | HTTP | Description |
|------|------|-------------|
| `NEXUS_UNAVAILABLE` | 503 | NexusAI health check failed |
| `NEXUS_TIMEOUT` | 504 | Triage request timed out |
| `NEXUS_INVALID_RESPONSE` | 502 | Response failed schema validation |

## Code ↔ DB

| Code | HTTP | Description |
|------|------|-------------|
| `DB_CONNECTION_FAILED` | 503 | Cannot reach PostgreSQL |
| `DB_MIGRATION_REQUIRED` | 503 | Schema version mismatch |
| `DB_WRITE_FAILED` | 500 | Persist operation failed |

## General

| Code | HTTP | Description |
|------|------|-------------|
| `INTERNAL_ERROR` | 500 | Unhandled server error |
| `SERVICE_DEGRADED` | 503 | Partial functionality; see health details |

## Versioning

New codes may be added in v1 without breaking consumers. Renaming or reusing codes requires v2.
