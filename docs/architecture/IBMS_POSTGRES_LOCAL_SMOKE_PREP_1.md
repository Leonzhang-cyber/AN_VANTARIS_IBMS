# VANTARIS IBMS PostgreSQL Local Smoke Prep 1

## 1. Task Scope

- prepare PostgreSQL local smoke plan and DDL (documentation only)
- no DB/user created in this task
- no DDL executed
- no backend started
- no JWT generated
- no seed/migration executed

Base commit: `90e2988` — docs(ibms): record local PostgreSQL install

---

## 2. Target Smoke Endpoints

| Endpoint | Table | Expected (with JWT + DB) |
| -------- | ----- | ------------------------ |
| GET `/api/system/menus` | `sys_menu` | 200 JSON (ORM via `MenuService`) |
| GET `/api/system/permissions` | `imbs_permission` | 200 JSON (ORM via `SystemService`) |
| GET `/api/system/versions` | `sys_version` | 200 JSON (raw SQL read path — ORM align pending) |

Auth: no token → 401; valid dev JWT → 200 or explicit JSON error (not connection refused).

---

## 3. Required Local Environment

| Item | Value |
| ---- | ----- |
| PostgreSQL | Running on `127.0.0.1:5432` (see `IBMS_POSTGRES_LOCAL_INSTALL_1.md`) |
| Disposable DB | `ibms_db` (created in EXEC task) |
| Disposable user | `ibms_user` (created in EXEC task) |
| Password | `<LOCAL_SMOKE_DB_PASSWORD>` — shell env only |
| Backend env | `IBMS_DATABASE_URL=postgresql+psycopg://ibms_user:<LOCAL_SMOKE_DB_PASSWORD>@127.0.0.1:5432/ibms_db` |
| Production data | **None** |

---

## 4. Execution Plan (POSTGRES-LOCAL-SMOKE-EXEC-1)

1. Create local DB/user via `psql` (shell only, password not committed)
2. Apply smoke DDL from `IBMS_POSTGRES_LOCAL_SMOKE_MINIMAL_DDL.md` → `/tmp/ibms-pg-smoke-ddl.sql`
3. Start backend: `IBMS_ENV=local-smoke` + `IBMS_DATABASE_URL=...`
4. Generate short-lived dev JWT → `/tmp/ibms-local-smoke-token.txt`
5. GET-only curl smoke (menus, permissions, versions)
6. Remove temp token file
7. Do **not** run POST/PUT/DELETE

---

## 5. ORM Alignment Notes

DDL derived from:

- `src/system/menu_models.py` — `sys_menu`, `sys_version`
- `src/system/models.py` — `imbs_permission`

Differences from legacy MySQL smoke DDL:

- `imbs_permission.id` is `VARCHAR(32)` UUID hex, not integer AI
- Column names: `menu_path`, `menu_title` (not `path`, `name`)
- `timestamptz` instead of `DATETIME`
- No `ENGINE`, `CHARSET`, `ON UPDATE CURRENT_TIMESTAMP`

---

## 6. Not Executed (this task)

- no CREATE DATABASE / USER
- no DDL apply
- no backend / JWT / API test

---

## 7. Next Task

**POSTGRES-LOCAL-SMOKE-EXEC-1**
