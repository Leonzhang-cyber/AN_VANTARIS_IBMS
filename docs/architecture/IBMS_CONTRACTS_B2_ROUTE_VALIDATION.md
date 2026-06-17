# VANTARIS IBMS Contracts B2 Route Validation

## 1. Task Scope

- static validation tool only
- no backend service started
- no DB connection
- no OpenAPI yaml content changed (README index only)
- no frontend/backend runtime changed

---

## 2. Files Changed

| File | Purpose |
|---|---|
| `contracts/tools/validate_flask_openapi_routes.py` | Stdlib static scanner |
| `docs/architecture/IBMS_CONTRACTS_B2_ROUTE_VALIDATION.md` | This document |
| `docs/security/IBMS_CONTRACTS_B2_ROUTE_VALIDATION_RISK_REVIEW.md` | Risk notes |
| `contracts/openapi/README.md` | Tool index |

---

## 3. Static Validation Method

1. **Flask:** regex scan `@*.route('...')` in `AN_VANTARIS_IBMS-backend/src/api/**/*.py`
2. **OpenAPI:** regex scan path keys in `contracts/openapi/*.yaml`
3. **Normalize:** Flask `<type:name>` → `{name}`; compare with param-name-agnostic signature
4. **Report:** missing in OpenAPI, extra in OpenAPI

No Flask import, no HTTP requests.

---

## 4. Script Command

```bash
python3 contracts/tools/validate_flask_openapi_routes.py \
  --backend-root AN_VANTARIS_IBMS-backend/src/api \
  --openapi-dir contracts/openapi
```

Exit codes: `0` = report printed; `2` = input path missing.

---

## 5. Result Summary (initial run)

| Metric | Count |
|---|---|
| Backend routes (static) | **78** |
| OpenAPI paths (union) | **42** |
| — `ibms-protected-api-v1.openapi.yaml` | 35 |
| — `ibms-frontend-api-v1.openapi.yaml` | 22 |
| Likely missing in OpenAPI | **39** |
| OpenAPI-only (contract aliases) | **3** |

**OpenAPI-only paths (expected contract aliases):**

- `/system/menu`, `/system/menu/{id}`, `/system/version/{version_id}/menus`

**Major missing groups:**

- DID read/verify/challenge/subordinates/chain
- IoT read/SSE/stream/parent routes
- System entity-types and standard fields/methods CRUD
- Menu batch/incremental/diff/version switch routes

---

## 6. Known Limitations

- Regex may miss dynamically constructed routes (none expected in current backend)
- Duplicate routes across files counted once per unique path
- HTTP method not compared (path-only)
- OpenAPI `$ref` paths not expanded
- Contract frontend paths intentionally differ from Flask (`/system/menu` vs `/system/menus-add`)

---

## 7. Next Tasks

- **CONTRACTS-B3** — expand OpenAPI coverage for system entity-types + menu admin routes
- **CONTRACTS-B4** — method-level diff (GET/POST) per path
- **CI hook** — run script in docs-only check (no fail on drift until baseline locked)
