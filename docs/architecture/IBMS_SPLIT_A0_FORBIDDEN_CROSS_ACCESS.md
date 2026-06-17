# VANTARIS IBMS Split A0 Forbidden Cross Access

Extends `docs/architecture/IBMS_FORBIDDEN_ACCESS_MATRIX_A2.md` with source-split-specific rules.

---

## Forbidden access matrix

| From | Forbidden Access | Reason |
|---|---|---|
| frontend (Console) | Direct DB (MySQL, SQLAlchemy, pymysql) | Security boundary; single Core API entry |
| frontend | Secrets (.env, private keys, JWT secret, MQTT creds) | Secrets belong in backend env only |
| frontend | Filesystem data artifacts (`*.pkl`, backend `data/`, sim CSV) | Artifacts served via API or CDN, not local FS reads |
| frontend | Import Python backend modules | Wrong runtime; breaks deployment model |
| backend API | Import frontend source (Vue, TS) | No shared code path |
| backend API | Read/write frontend `node_modules` / `dist` | Separate build pipelines |
| simulator (`testMQTT`, test routes) | Production startup without guards | Test endpoints must not ship unguarded |
| contracts/ | Runtime imports from backend or frontend | Contracts are specs, not libraries |
| tests/ | Production secrets or prod DB URL | Tests use fixtures and env isolation |
| data/model artifacts | Git commit unless approved | Size, sensitivity, reproducibility |
| original `ibms_backend` config | Copy into canonical backend wholesale | Reintroduces hardcoded P0 secrets |
| original `ibms_backend` routes | Downgrade JWT/permission vs current backend | Regression on security line |
| CI/build | Push real `.env` or zip secrets | Credential leak |
| any package | Merge frontend + backend into single npm/python tree | User rule: do not merge frontend/backend |

---

## Allowed access (for clarity)

| From | To | Mechanism |
|---|---|---|
| frontend | backend | HTTPS `/api/*` with Bearer JWT |
| backend | DB | SQLAlchemy via env config |
| backend | MQTT / blockchain | Env-configured external services |
| developers | contracts | Read OpenAPI/matrix when implementing routes |
| migration scripts | both runtimes | Copy **selected** files after diff review — phase B only |

---

## Enforcement checkpoints

- Pre-commit: no `.env`, no `*.pkl` in staged files (unless LFS approved)
- PR review: route changes require contracts diff
- Split B4: verify forbidden matrix before each module move
