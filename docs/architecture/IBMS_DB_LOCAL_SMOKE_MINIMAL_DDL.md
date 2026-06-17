# IBMS Local Smoke Minimal DDL

**Warning:** smoke-only schema for disposable local MySQL verification. **Not** a production migration. Column names and types are derived from ORM models in `AN_VANTARIS_IBMS-backend/src/system/menu_models.py` and `src/system/models.py`.

Do **not** commit DB passwords. Use `<LOCAL_SMOKE_DB_PASSWORD>` in shell only.

---

## Tables

| Table | ORM model | Purpose |
| ----- | --------- | ------- |
| `sys_menu` | `SysMenu` | Menu read smoke (`GET /api/system/menus`) |
| `sys_version` | `SysVersion` | Version read smoke (`GET /api/system/versions`) |
| `imbs_permission` | `Permission` | Permission read smoke (`GET /api/system/permissions`) |

Optional for full menu/version filtering: `sys_version_menu` (`SysVersionMenu`) — not required for minimal list endpoints if DAO queries base tables only.

---

## Columns (ORM-aligned)

### `sys_version`

| Column | Type | Notes |
| ------ | ---- | ----- |
| `id` | BIGINT PK AI | |
| `version_code` | VARCHAR(50) NOT NULL UNIQUE | |
| `version_name` | VARCHAR(100) NOT NULL | |
| `description` | VARCHAR(500) NULL | |
| `icon` | VARCHAR(50) NULL | |
| `sort_order` | INT DEFAULT 0 | |
| `is_active` | SMALLINT DEFAULT 1 | |
| `is_default` | SMALLINT DEFAULT 0 | |
| `created_at` | DATETIME | server default CURRENT_TIMESTAMP |
| `updated_at` | DATETIME | ON UPDATE CURRENT_TIMESTAMP |

### `sys_menu`

| Column | Type | Notes |
| ------ | ---- | ----- |
| `id` | BIGINT PK AI | |
| `parent_id` | BIGINT DEFAULT 0 | 0 = top level |
| `menu_path` | VARCHAR(200) NOT NULL UNIQUE | route path / identifier |
| `menu_title` | VARCHAR(100) NOT NULL | display title |
| `menu_icon` | VARCHAR(50) NULL | |
| `menu_type` | VARCHAR(20) DEFAULT 'menu' | |
| `has_children` | SMALLINT DEFAULT 0 | |
| `redirect_path` | VARCHAR(200) NULL | |
| `sort_order` | INT DEFAULT 0 | |
| `is_visible` | SMALLINT DEFAULT 1 | not `status` |
| `remark` | VARCHAR(255) NULL | |
| `created_at` / `updated_at` | DATETIME | timestamps |

### `imbs_permission`

| Column | Type | Notes |
| ------ | ---- | ----- |
| `id` | VARCHAR(32) PK | UUID hex (not INT AI) |
| `perm_code` | VARCHAR(64) NOT NULL UNIQUE | |
| `description` | VARCHAR(128) NOT NULL | not separate `name` column |
| `extra` | JSON NULL | |
| `created_at` | DATETIME | |

---

## Minimal seed rows (smoke-only)

| Table | Rows | Example |
| ----- | ---- | ------- |
| `sys_menu` | 2 | `/system`, `/system/permissions` |
| `sys_version` | 1 | `version_code=local-smoke` |
| `imbs_permission` | 1 | `perm_code=system:read` |

---

## Deployment

- SQL file location: `/tmp/ibms-local-smoke-ddl.sql` (not in repo)
- Apply only when local MySQL is available: `mysql -uroot < /tmp/ibms-local-smoke-ddl.sql`
- Password placeholder: `<LOCAL_SMOKE_DB_PASSWORD>` — never commit

---

## ORM mismatch note

Task template DDL using columns `name`, `path`, `status` does **not** match IBMS ORM. Use this document's column names when creating smoke DDL.
