# IBMS CONTRACTS-B5 — OpenAPI Risk Review

**Task:** CONTRACTS-B5  
**Review type:** Static contract completion (no runtime)

---

## OpenAPI still draft

DID and IoT operations added in this batch use placeholder schemas (`additionalProperties: true`). Do not treat OpenAPI as production SDK or security baseline without runtime validation.

---

## Static route mismatch risk

B4 validation normalizes path parameters but cannot detect dynamic registration. Contract alias system/menu operations still appear as OpenAPI-only — expected.

---

## DID auth decision risk

Several DID routes are **public at runtime** (no `@jwt_required`): `/did/challenge`, `/did/vp/verify`, `/did/vc/status`, entity read, subordinates, chain queries.

OpenAPI documents these with `security: []` and auth-pending notes. Production deployments must review whether public access is acceptable before exposure to untrusted networks.

---

## SSE stream / latest auth decision risk

`/iot/device/{device_code}/stream`, `/latest`, and `/sse-url` are public at runtime. SSE streams may leak device telemetry without authentication.

Documented as auth-pending. Hardening should add JWT or device-scoped tokens before production edge deployment.

---

## No runtime changed

This batch modified OpenAPI YAML and documentation only. No Flask decorators, middleware, or frontend modules were altered.

---

## No service started

No backend, database, or frontend dev server was run. Coverage derived from static Flask source scan and B4 tooling.

---

## Next validation requirement

1. Re-run B4 after any backend route change:
   ```bash
   python3 contracts/tools/validate_flask_openapi_methods.py \
     --backend-root AN_VANTARIS_IBMS-backend/src/api \
     --openapi-dir contracts/openapi
   ```
2. Live integration tests for public DID/IoT reads — confirm 401/403 when auth is added.
3. CONTRACTS-B6 candidate: system standard-fields / entity-types OpenAPI completion.
4. CONTRACTS-A4: contract tests against running backend.

---

## High-risk surfaces documented

| Surface | Risk |
|---|---|
| POST `/did/login` | Token issuance |
| POST `/did/vp/verify` | VP validation bypass if misconfigured |
| GET `/iot/device/{device_code}/stream` | Telemetry exposure |
| POST `/iot/device/*/command` | Device control — JWT + permission required |

Write routes document 403; public reads require separate deployment policy review.
