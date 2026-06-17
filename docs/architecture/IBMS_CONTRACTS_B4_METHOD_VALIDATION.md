# IBMS CONTRACTS-B4 — Method-Level OpenAPI Validation

**Task:** CONTRACTS-B4  
**Status:** Complete (static tooling only)  
**Prior work:** CONTRACTS-B2 path validation, CONTRACTS-B3 system/menu OpenAPI completion

---

## Task scope

Add HTTP **method-level** static comparison between Flask `@route` decorators and OpenAPI path operations. Complements B2 path-only validation without modifying OpenAPI YAML or runtime code.

In scope:

- New stdlib Python script `validate_flask_openapi_methods.py`
- Architecture and security notes
- README update

Out of scope:

- Backend / frontend runtime changes
- OpenAPI YAML edits
- Live API requests or DB access

---

## Files changed

| File | Change |
|---|---|
| `contracts/tools/validate_flask_openapi_methods.py` | New method-level validator |
| `contracts/openapi/README.md` | B4 usage section |
| `docs/architecture/IBMS_CONTRACTS_B4_METHOD_VALIDATION.md` | This document |
| `docs/security/IBMS_CONTRACTS_B4_METHOD_VALIDATION_RISK_REVIEW.md` | Risk review |

---

## Method-level static validation method

1. **Flask scan:** Regex finds `@*.route(` blocks in `AN_VANTARIS_IBMS-backend/src/api/**/*.py`, extracts path and `methods=[...]`. If `methods` omitted, assumes **GET**.
2. **OpenAPI scan:** Parses `contracts/openapi/*.yaml` path keys and child HTTP verbs (`get`, `post`, `put`, `patch`, `delete`, etc.).
3. **Normalization:** Flask `<int:id>` / `<device_code>` → `{id}` / `{device_code}`; param-name-agnostic matching via `{}` signature (same as B2).
4. **Diff:** Reports Flask `(path, method)` pairs missing from OpenAPI union and OpenAPI operations not found in Flask scan.

Exit codes: `0` = script completed (differences OK), `2` = input directory missing.

---

## Script command

```bash
python3 contracts/tools/validate_flask_openapi_methods.py \
  --backend-root AN_VANTARIS_IBMS-backend/src/api \
  --openapi-dir contracts/openapi
```

Compare with B2 path tool:

```bash
python3 contracts/tools/validate_flask_openapi_routes.py \
  --backend-root AN_VANTARIS_IBMS-backend/src/api \
  --openapi-dir contracts/openapi
```

---

## Result summary (initial run, post-B3)

| Metric | B2 (paths) | B4 (methods) |
|---|---|---|
| Flask (static) | 78 paths | **97 route-method pairs** |
| OpenAPI (union) | 55 paths | **73 operations** |
| Missing in OpenAPI | 32 paths | **40 route-methods** |
| OpenAPI-only | contract aliases | **9 operations** (contract aliases) |

System/menu permission and version routes largely aligned at method level after B3. Remaining Flask gaps concentrate on DID read routes, IoT device/stream routes, and system standard-fields / entity-types admin.

OpenAPI-only operations (expected contract aliases):

- `POST/PUT/DELETE /system/menu*`
- `GET /system/menus/{id}`
- `GET/POST /system/version/{version_id}/menus`
- `PUT/DELETE /system/version/{version_id}/menu/{menu_id}`

---

## Known limitations

- **Static regex only** — does not evaluate Blueprint registration, conditional routes, or dynamic path builders.
- **Default GET assumption** — Flask routes without `methods=` are counted as GET; misreporting if runtime uses non-default verbs.
- **Multi-line decorators** — parenthesis-balanced scan handles most cases; exotic formatting may be missed.
- **OpenAPI `$ref` operations** — only inline path verbs under each path key are detected.
- **Duplicate paths across yaml files** — union dedupes identical `(path, method)` pairs.
- **Contract vs runtime** — alias paths intentionally appear as OpenAPI-only operations.

---

## Relationship to B2 path validation

| Tool | Granularity | Use when |
|---|---|---|
| `validate_flask_openapi_routes.py` | Path | Quick coverage sweep, alias discovery |
| `validate_flask_openapi_methods.py` | Path + HTTP method | Verb mismatches (GET documented but POST at runtime) |

Run both in CI/docs workflows: B2 for breadth, B4 for verb accuracy.

---

## Next tasks

1. **CONTRACTS-B5** — Close DID/IoT method gaps in OpenAPI (or split per API group specs)
2. **CONTRACTS-A4** — Contract tests against running backend
3. **SYSTEM OpenAPI** — standard-fields / entity-types route group
4. **FRONTEND-A9-EXEC-3+** — Continue System page migrations

---

## Not changed

- `AN_VANTARIS_IBMS-backend/src/**`
- `AN_VANTARIS_IBMS-frontend/src/**`
- `contracts/openapi/*.yaml`
