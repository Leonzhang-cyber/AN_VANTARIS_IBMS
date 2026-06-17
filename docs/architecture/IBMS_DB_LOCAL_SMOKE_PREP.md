# VANTARIS IBMS DB Local Smoke Prep

## 1. Task Scope

- prepare DB local-smoke plan
- no DB started
- no real `.env` created
- no DB credential written
- no seed/migration executed
- no backend/frontend source changed
- no contracts changed

Base commit: `26a6ff6` — test(ibms): execute approved dev JWT smoke

---

## 2. Current State

- **DEV-JWT-SMOKE-EXEC** confirmed JWT gate works: no/invalid token → **401**; valid dev token → **not 401**.
- Valid dev token **reaches DB/business layer** — server logs show handler execution after `@jwt_required`.
- **Current blocker:** MySQL connection refused on dev fallback `127.0.0.1:3306` (`OperationalError 2003`).
- **menus / permissions / versions** are DB-backed read paths; JWT alone is insufficient for **200**.
- **Error format inconsistency:** menus/versions return JSON 500 on DB failure; permissions returns Flask **HTML 500** (unhandled exception).

---

## 3. DB Configuration Findings

| Item | Finding | Evidence |
| ---- | ------- | ---------- |
| DB engine | **MySQL** via `mysql+pymysql` | `database.py` L23–26; `default.py` L71 |
| Host fallback | `127.0.0.1` | `default.py` `_DEV_DB_HOST` L15 |
| Port fallback | `3306` | `default.py` `_DEV_DB_PORT` L16 |
| Database name key | `IBMS_DB_NAME` (fallback `ibms_db`) | `default.py` L17, L70 |
| Username key | `IBMS_DB_USER` (fallback `ibms_user`) | `default.py` L13, L66 |
| Password source | `IBMS_DB_PASSWORD` env or **dev fallback exists** (do not use in production) | `default.py` L14, L67; `_env_secret()` L26–30 |
| Full URI override | `IBMS_DATABASE_URL` (optional) | `default.py` L48–64 |
| Init behavior | `init_database(app)` sets `SQLALCHEMY_DATABASE_URI` + `db.init_app(app)` — **no startup connection test**, **no `create_all`** | `database.py` L14–33; no `create_all`/`alembic` in repo |
| local-smoke DB profile | **Same Config as development** — no SQLite/mock branch for `IS_LOCAL_SMOKE` | `default.py` L116; `main.py` skips blockchain/IoT only |

**Credential rule for EXEC:** use disposable local MySQL credentials via env or session export — never commit passwords.

---

## 4. System Endpoint DB Dependencies

| Endpoint | Function / File | Tables / Models | Current Error Handling | Expected Smoke Result |
| -------- | --------------- | --------------- | ---------------------- | --------------------- |
| GET `/api/system/menus` | `get_menu_tree` — `menu_api.py` L195–203 | `sys_menu` via `MenuService.get_menu_tree` → `MenuDAO.get_all` | **try/except** → `Result.error(code=500)` JSON | **401** no token; **200** `[]` or tree if MySQL + table OK |
| GET `/api/system/permissions` | `list_permissions` — `system_api.py` L241–254 | `imbs_permission` via `SystemService.list_permissions` → `PermissionDAO.get_all` | **No try/except** → Flask HTML **500** on DB error | **401** no token; **200** `[]` or list if MySQL + table OK |
| GET `/api/system/versions` | `list_versions` — `menu_api.py` L18–32 | `sys_version` raw SQL `SELECT * FROM sys_version` | **try/except** → `Result.error(code=500)` JSON | **401** no token; **200** `[]` or rows if MySQL + table OK |

All three: `@jwt_required` only — **no** `@require_permission`.

---

## 5. Candidate DB Local-Smoke Options

### Option A — Local MySQL

| Pros | Cons |
| ---- | ---- |
| Closest to production runtime (PyMySQL + MySQL dialect) | Requires MySQL install/start on host |
| No code changes | Schema must be created manually (no migration tool in repo) |
| Works with existing ORM models and raw SQL | Seed scripts need explicit `--apply` approval |

**Steps (EXEC):** install/start MySQL → create `ibms_db` + user → apply minimal DDL from ORM models → optional `seed_permissions.py --apply` → curl with dev JWT.

### Option B — Docker MySQL

| Pros | Cons |
| ---- | ---- |
| Isolated, disposable | Requires Docker availability |
| Repeatable port mapping `3306:3306` | Same schema/seed gap as Option A |
| No host MySQL pollution | Still need credentials via env (not committed) |

**Steps (EXEC):** `docker run` MySQL 8 with env vars → map 3306 → run minimal schema/seed → smoke.

### Option C — Mock / SQLite adapter

| Pros | Cons |
| ---- | ---- |
| Fastest for GET smoke if implemented | **Requires backend src changes** (URI switch, dialect differences) |
| No MySQL daemon | Raw SQL in `list_versions` may differ; `sys_*` vs SQLite |
| | Diverges from production MySQL behavior |

**Not recommended for next EXEC** — violates current “no src change” boundary unless dedicated refactor task approved.

---

## 6. Recommended Next Step

**Primary:** **DB-LOCAL-SMOKE-EXEC-A** — local MySQL with disposable database, if host MySQL install is acceptable.

**Alternative:** **DB-LOCAL-SMOKE-DOCKER-PREP** → **EXEC** if Docker preferred and local MySQL undesirable.

**Before seed/migration:**

1. Identify **minimal tables:** `sys_menu`, `sys_version`, `imbs_permission` (see `IBMS_SYSTEM_DB_READ_PATH_MAP.md`).
2. Derive DDL from SQLAlchemy models in `menu_models.py` and `system/models.py` — **no `.sql` files in repo**.
3. Optional: `scripts/seed_permissions.py --apply` for permission rows (includes `system:read`); dry-run first.
4. Re-run **DEV-JWT + GET curl** smoke expecting **200** (empty arrays acceptable).

**Parallel (non-blocking):** **SYSTEM-DB-ERROR-JSON-1** — add try/except to `list_permissions` for JSON 500 consistency.

---

## 7. Stop Conditions

| Condition | Status in prep |
| --------- | -------------- |
| Requires production DB credentials | **Stop** — use local disposable DB only |
| Requires production data dump | **Stop** — no customer data |
| Requires destructive migration | **Stop** — no migration framework found; manual DDL only with approval |
| Requires broad ORM rewrite (SQLite) | **Stop** — separate task |
| Requires committing password/secret | **Stop** — env/session only |

---

## 8. Schema / Seed Availability (Read-Only)

| Asset | Location | Notes |
| ----- | -------- | ----- |
| SQL migration files | **None found** | No `.sql`, alembic, or flyway in backend |
| ORM table definitions | `menu_models.py`, `system/models.py` | Source of truth for DDL derivation |
| Permission seed | `scripts/seed_permissions.py` | Dry-run default; `--apply` writes `imbs_permission` |
| Root user permission assign | `scripts/assign_root_permissions.py` | Not required for GET list smoke |
| Menu/version seed | **Unknown** — no dedicated seed script found | Empty tables may still return **200** `[]` |
