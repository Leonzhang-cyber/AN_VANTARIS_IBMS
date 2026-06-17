# VANTARIS IBMS Security A3 DB Externalization

**Task ID:** IBMS-SECURITY-A3  
**Date:** 2026-06-16  
**Baseline Commit:** `ef6fdbc` (A2)

---

## 1. Task Scope

| Item | Status |
|---|---|
| Scope | Externalize database connection string only |
| Schema changed | ❌ No |
| Migration executed | ❌ No |
| DAO logic changed | ❌ No |
| Real DB password committed | ❌ No |
| Service started | ❌ No |

---

## 2. Files Changed

| File | Change |
|---|---|
| `AN_VANTARIS_IBMS-backend/src/common/config/default.py` | `_build_db_config()` — env-first DB URI and components |
| `AN_VANTARIS_IBMS-backend/.env.example` | SECURITY-A3 comment on database section |
| `docs/security/IBMS_SECURITY_A3_DB_EXTERNALIZATION.md` | This document |

**Unchanged:** `database.py` still reads `AppConfig.DB_*` at init — values now come from env via Config.

---

## 3. Environment Variables Used

| Variable | Purpose |
|---|---|
| `IBMS_DATABASE_URL` | Full SQLAlchemy database URL (highest priority) |
| `IBMS_DB_HOST` | DB host |
| `IBMS_DB_PORT` | DB port |
| `IBMS_DB_NAME` | DB name |
| `IBMS_DB_USER` | DB user |
| `IBMS_DB_PASSWORD` | DB password |

---

## 4. Runtime Behavior

Priority order:

1. **`IBMS_DATABASE_URL`** — used directly; components derived via URL parse for `DB_*` attributes
2. **Component variables** — `IBMS_DB_HOST`, `IBMS_DB_PORT`, `IBMS_DB_NAME`, `IBMS_DB_USER`, `IBMS_DB_PASSWORD` assembled into URI
3. **Development fallback** — legacy dev defaults in `_DEV_DB_*` constants (local compatibility only)

- No DB password is printed.
- SQLAlchemy initialization path unchanged (`init_database` → `AppConfig.DB_*`).
- No table, model, or DAO changes.

---

## 5. Not Changed

| Area | Status |
|---|---|
| MQTT | ❌ Not changed |
| DID | ❌ Not changed |
| Blockchain | ❌ Not changed |
| JWT / Flask secrets | ❌ Not changed (A2) |
| RBAC | ❌ Not changed |
| Models / DAO | ❌ Not changed |

---

## 6. Production Requirement

Production **must** set either:

- `IBMS_DATABASE_URL`, **or**
- All of `IBMS_DB_HOST`, `IBMS_DB_PORT`, `IBMS_DB_NAME`, `IBMS_DB_USER`, `IBMS_DB_PASSWORD`

Do not rely on development fallbacks in production.

---

## 7. No Real Secret Confirmation

- `.env.example` uses placeholder passwords only.
- No new real DB password added to committed files.
- Dev fallbacks retain pre-existing baseline values for unset-env local dev only.

---

## 8. Recommended Next Tasks

- **IBMS-SECURITY-A3-COMMIT** (included in batch)
- **IBMS-SECURITY-A4** — MQTT externalization
- **IBMS-SECURITY-A5** — DID / blockchain externalization
