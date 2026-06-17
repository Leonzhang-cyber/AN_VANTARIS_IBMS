# IBMS CONTRACTS-B6 — OpenAPI Risk Review

**Task:** CONTRACTS-B6  
**Review type:** Static contract completion (no runtime)

---

## OpenAPI still draft

System admin operations use placeholder schemas. Entity-type and standard-field payloads are not fully specified. Do not generate production SDKs without runtime validation.

---

## Static route mismatch risk

Standard-fields/methods use Flask-specific path segments (`list-standard-fields`, `getById-standard-fields/{field_id}`). Contract aliases like `/system/standard-fields` are documented but not added as separate paths to avoid false negatives in B4 while Flask uses different URLs.

Menu contract aliases still appear as OpenAPI-only operations — expected.

---

## System permission pending risk

Entity-types and standard-fields routes require JWT at runtime but lack `@require_permission` in current Flask source. OpenAPI documents **403 on writes** as target/pending policy — not proof of enforcement.

---

## /system/test exposure risk

`GET /system/test` is a diagnostic endpoint protected by JWT only. It can confirm API availability to any authenticated token holder.

**Production exposure must be reviewed** — consider disabling, network-restricting, or adding admin permission before production deployment.

---

## No runtime changed

This batch modified OpenAPI YAML and documentation only.

---

## No service started

No backend, database, or frontend dev server was run.

---

## Next validation requirement

1. Re-run B4 after backend route or OpenAPI changes:
   ```bash
   python3 contracts/tools/validate_flask_openapi_methods.py \
     --backend-root AN_VANTARIS_IBMS-backend/src/api \
     --openapi-dir contracts/openapi
   ```
2. Live tests for entity-types and standard-fields CRUD with JWT.
3. Define audit log OpenAPI when backend implements audit query API (pairs with FRONTEND-A9-EXEC-4 placeholder page).
4. CONTRACTS-A4: contract tests against running backend.

---

## High-risk surfaces

| Surface | Risk |
|---|---|
| POST/DELETE entity-types | Schema mutation |
| POST/DELETE standard-fields/methods | Global dictionary changes |
| GET /system/test | Diagnostic leak / reconnaissance |

Write routes should receive `system:admin` enforcement in SYSTEM-B follow-up.
