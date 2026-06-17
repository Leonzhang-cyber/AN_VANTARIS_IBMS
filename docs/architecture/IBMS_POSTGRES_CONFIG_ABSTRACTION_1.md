# VANTARIS IBMS PostgreSQL Config Abstraction 1

## 1. Task Scope

- support PostgreSQL DB URI selection
- preserve MySQL legacy fallback
- no PostgreSQL install/start
- no DB connection
- no seed/migration
- no model/raw SQL migration
- no frontend source change
- no contracts change

Base commit: `15991df` — chore(ibms): recover PostgreSQL prep worktree

---

## 2. Root Cause

| Issue | Detail |
| ----- | ------ |
| Hard-coded MySQL URI | `init_database()` rebuilt `mysql+pymysql://...` from component vars |
| Ignored config URL | `Config.SQLALCHEMY_DATABASE_URI` / `IBMS_DATABASE_URL` was bypassed |
| PostgreSQL blocked | Even with `psycopg` installed, runtime always targeted MySQL |

---

## 3. Files Changed

| File | Change |
| ---- | ------ |
| `src/common/core/database.py` | Added `resolve_database_uri()`; `init_database()` uses Config URI first |
| `src/common/config/default.py` | Added `normalize_database_uri()` for `postgresql://` → `postgresql+psycopg://` |
| `AN_VANTARIS_IBMS-backend/README.md` | PostgreSQL URI env notes |
| This doc + risk review | Task record |

---

## 4. URI Resolution Rule

| Priority | Source | Example scheme |
| -------- | ------ | -------------- |
| 1 | `IBMS_DATABASE_URL` → `Config.SQLALCHEMY_DATABASE_URI` | `postgresql+psycopg` |
| 1b | Normalized `postgresql://` / `postgres://` | → `postgresql+psycopg` |
| 2 | Legacy `IBMS_DB_*` component fallback | `mysql+pymysql` |

Password values come from environment only; dev fallback exists in config module (not documented here).

`init_database()` order:

1. `app.config["SQLALCHEMY_DATABASE_URI"]` if already set
2. else `resolve_database_uri()` → `Config.SQLALCHEMY_DATABASE_URI`
3. else legacy MySQL component assembly

No DB connection is opened during import or `init_database()`.

---

## 5. Verification

| Check | Result | Notes |
| ----- | ------ | ----- |
| PostgreSQL URI config import | **PASS** | `postgresql+psycopg://...` |
| `postgresql://` normalization | **PASS** | → `postgresql+psycopg://` |
| database module import | **PASS** | `resolve_database_uri()` matches Config |
| legacy fallback import | **PASS** | `mysql+pymysql://` when no `IBMS_DATABASE_URL` |
| npm run build | **PASS** | ~2.2s |

---

## 6. Not Changed

- no DB installed
- no DB created
- no migration / seed
- no API smoke
- no raw SQL / ORM model changes
- no frontend source / contracts

---

## 7. Next Tasks

- POSTGRES-LOCAL-INSTALL-1
- POSTGRES-LOCAL-SMOKE-PREP-1
- POSTGRES-LOCAL-SMOKE-EXEC-1
- POSTGRES-ORM-ALIGN-1
