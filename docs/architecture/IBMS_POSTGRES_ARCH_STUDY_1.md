# VANTARIS IBMS PostgreSQL Architecture Study 1

## 1. Task Scope

- study current IBMS DB architecture
- prepare PostgreSQL migration direction
- no source code changed
- no PostgreSQL installed
- no migration executed
- no seed executed
- no real `.env` created
- **MySQL local-smoke route paused** — PostgreSQL is now the target canonical DB

Base commit: `d060427` — docs(ibms): record local MySQL install

---

## 2. Current DB State

| Item | Current Finding |
| ---- | --------------- |
| Current DB engine | **MySQL** (hard-coded in runtime init) |
| Current driver | **PyMySQL** (`mysql+pymysql://`) |
| ORM | **SQLAlchemy 2.x** + **Flask-SQLAlchemy 3.1.1** |
| DB config keys | `IBMS_DATABASE_URL` (optional), `IBMS_DB_HOST`, `IBMS_DB_PORT`, `IBMS_DB_NAME`, `IBMS_DB_USER`, `IBMS_DB_PASSWORD` |
| Fallback DB host | `127.0.0.1` |
| Fallback DB port | **3306** |
| Fallback DB name | `ibms_db` |
| Fallback DB user | `ibms_user` |
| Fallback password | dev fallback exists, value not documented |
| Raw SQL present | **Yes** — extensive in `menu_api.py`, partial in `menu_service.py` |
| Migration framework | **Absent** — no Alembic / Flask-Migrate |
| Seed scripts | **Present** — `scripts/seed_permissions.py`, `scripts/assign_root_permissions.py` (dry-run default) |
| `create_all` / auto schema | **Not found** at startup |
| Startup DB connection | `init_database(app)` → `db.init_app(app)`; connection tested lazily on first query |

### Config layering notes

| Layer | Behavior | PostgreSQL impact |
| ----- | -------- | ----------------- |
| `default.py` | Builds `SQLALCHEMY_DATABASE_URI`; supports `IBMS_DATABASE_URL` passthrough | URL scheme must become `postgresql+psycopg://` |
| `database.py` | **Re-builds** `mysql+pymysql://...` from component vars, **ignores** `Config.SQLALCHEMY_DATABASE_URI` | Must unify on single URI source for PG |
| `local_smoke.py` | Fixture responses when `IBMS_LOCAL_SMOKE=true` for menus/versions | Bypasses DB; separate from engine migration |

---

## 3. Model Inventory

| Model / File | Table | Key fields | PostgreSQL notes |
| ------------ | ----- | ---------- | ---------------- |
| `Iot/models.py` → `IMSDevice` | `imbs_device` | `id` CHAR(32), JSON cols, SmallInteger status | Replace `dialects.mysql.CHAR/VARCHAR/TINYINT` with generic types |
| `Iot/models.py` → `IMSStandardField` | `imbs_standard_field` | DECIMAL, Boolean, JSON | JSON → **jsonb** preferred |
| `Iot/models.py` → `IMSFieldMapping` | `imbs_field_mapping` | FK → standard_field | Standard FK |
| `Iot/models.py` → `IMSMethodMapping` | `imbs_method_mapping` | Enum direction | PG native ENUM or VARCHAR check |
| `Iot/models.py` → `IMSStandardMethod` | `imbs_standard_method` | JSON schemas | jsonb |
| `system/models.py` → `EntityType` | `imbs_entity_type` | `id` String(32), self-FK | Duplicate model vs DID |
| `system/models.py` → `Permission` | `imbs_permission` | `id` String(32), `perm_code`, JSON extra | Table name **`imbs_permission`** (not `ibms_permission`) |
| `DID/models.py` → `EntityType` | `imbs_entity_type` | same as system duplicate | Consolidate to single model |
| `DID/models.py` → `Permission` | `imbs_permission` | duplicate | Consolidate |
| `DID/models.py` → `EntityRelationship` | `imbs_relationship` | parent/child DID | |
| `DID/models.py` → `User` | `imbs_users` | JSON permissions, SmallInteger active | `ON UPDATE CURRENT_TIMESTAMP` in server_default |
| `DID/models.py` → `VCAnchor` | `imbs_vc_anchor` | hash/tx fields | |
| `DID/models.py` → `VCRevocation` | `imbs_vc_revocation` | vc_id PK | |
| `system/menu_models.py` → `SysVersion` | `sys_version` | BigInteger PK, SmallInteger flags | AI → IDENTITY |
| `system/menu_models.py` → `SysMenu` | `sys_menu` | menu_path unique, parent_id | |
| `system/menu_models.py` → `SysVersionMenu` | `sys_version_menu` | version_code + menu_id | upsert uses MySQL syntax in API |

**Naming:** project uses **`imbs_`** prefix (Integrated Management Building System), not `ibms_`.

**Dual Base pattern:** IoT uses `db.Model`; DID/menu/system use separate `declarative_base()` — not all models registered on Flask-SQLAlchemy metadata.

---

## 4. Raw SQL Inventory

| File | SQL usage | MySQL-specific risk | PostgreSQL action |
| ---- | --------- | ------------------- | ----------------- |
| `api/system/menu_api.py` | `SELECT * FROM sys_version`, menu CRUD | Positional row indexing; LIMIT | Use ORM or explicit column names |
| `api/system/menu_api.py` | `ON DUPLICATE KEY UPDATE` (version-menu batch) | **High** | `ON CONFLICT ... DO UPDATE` |
| `api/system/menu_api.py` | `GROUP_CONCAT` in init-data query | **High** | `string_agg` |
| `api/system/menu_api.py` | `VALUES(is_visible)` upsert variant | MySQL 8 syntax | PG `EXCLUDED.col` |
| `system/menu_service.py` | version switch UPDATEs | SmallInteger 0/1 flags | boolean or smallint |
| `DID/models.py`, `menu_models.py` | `CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP` | **High** | trigger or app-level `updated_at` |
| `Iot/models.py` | `from sqlalchemy.dialects.mysql import CHAR, VARCHAR, TINYINT` | **High** | generic SQLAlchemy types |

No standalone `.sql` migration files in repo. Smoke DDL docs exist for MySQL only (`IBMS_DB_LOCAL_SMOKE_MINIMAL_DDL.md`).

---

## 5. System Endpoint DB Path

| Endpoint | Current DB access | Tables | PostgreSQL impact |
| -------- | ----------------- | ------ | ----------------- |
| GET `/api/system/menus` | **ORM** via `MenuService.get_menu_tree` when `IBMS_LOCAL_SMOKE` off; **fixture** when on | `sys_menu`, `sys_version_menu` | ORM portable; menu_service raw SQL needs rewrite |
| GET `/api/system/permissions` | **ORM** via `SystemService` → `PermissionDAO` | `imbs_permission` | Portable if table exists; JSON `extra` → jsonb |
| GET `/api/system/versions` | **Raw SQL** `SELECT * FROM sys_version` when smoke off; **fixture** when on | `sys_version` | Replace raw SQL or use ORM; remove `SELECT *` |

### Error handling

| Route | Wrapper | HTML 500 risk |
| ----- | ------- | ------------- |
| `list_permissions` | JSON `Result.error(500, "Failed to load permissions")` | Low |
| `list_versions` / `get_menu_tree` | `handle_db_smoke_error` → JSON `DB_UNAVAILABLE` on connection errors | Low for connection; other errors may leak message |
| Other menu routes | Mixed `Result.error` / `str(e)` | Medium on unhandled paths |

---

## 6. Requirements Snapshot (read-only)

From `requirements.txt` (UTF-16LE on disk):

| Package | Version | Notes |
| ------- | ------- | ----- |
| SQLAlchemy | 2.0.49 | |
| Flask-SQLAlchemy | 3.1.1 | |
| PyMySQL | 1.1.2 | MySQL driver only |
| psycopg / psycopg2 | **Absent** | Add in Phase 1 |
| Alembic / Flask-Migrate | **Absent** | Add in Phase 5 |

---

## 7. Key Findings

- **MySQL local-smoke route is paused** — do not continue MySQL disposable DB work unless Leon explicitly approves.
- **PostgreSQL is now the target canonical DB** for IBMS relational storage.
- Migration must be **staged** — config unification, driver swap, raw SQL rewrite, then Alembic.
- **No production data migration** in current phase.
- **No UFMS schema/code** should be copied — IBMS-only tables (`imbs_*`, `sys_*`).
- **`database.py` hard-codes MySQL URI** — critical blocker even if `IBMS_DATABASE_URL` points to PostgreSQL.
- **`menu_api.py` is the highest MySQL coupling** (ON DUPLICATE KEY, GROUP_CONCAT, extensive raw SQL).
- **Duplicate ORM models** (`EntityType`, `Permission` in `system/models.py` and `DID/models.py`) need consolidation before migration tooling.
- **Dual declarative base** vs `db.Model` split complicates Alembic autogenerate.

---

## 8. UFMS Boundary Check

| Item | Result |
| ---- | ------ |
| UFMS in business source | **Not found** |
| Hits | Boundary/inventory docs only |
| Contamination | **No** |
