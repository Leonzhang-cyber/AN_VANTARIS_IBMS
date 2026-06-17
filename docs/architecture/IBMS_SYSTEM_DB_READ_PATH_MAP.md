# VANTARIS IBMS System DB Read Path Map

## 1. Scope

- system menus / permissions / versions **read paths**
- GET-only local-smoke targets
- no DB write in smoke scope

Evidence base: read-only code review at commit `26a6ff6`.

---

## 2. Endpoint Read Map

| Endpoint | Route File | Handler | DB Access | Tables / Models | Auth Guard |
| -------- | ---------- | ------- | --------- | --------------- | ---------- |
| GET `/api/system/menus` | `src/api/system/menu_api.py` | `get_menu_tree` (L195) | SQLAlchemy ORM query | **`sys_menu`** (`SysMenu`) | `@jwt_required` |
| GET `/api/system/permissions` | `src/api/system/system_api.py` | `list_permissions` (L241) | SQLAlchemy ORM query | **`imbs_permission`** (`Permission`) | `@jwt_required` |
| GET `/api/system/versions` | `src/api/system/menu_api.py` | `list_versions` (L18) | Raw SQL via `db.session.execute` | **`sys_version`** | `@jwt_required` |

### Call chain detail

**Menus**

```
get_menu_tree → MenuService.get_menu_tree(session)
              → MenuDAO.get_all(session)
              → session.query(SysMenu).order_by(...)
```

**Permissions**

```
list_permissions → SystemService.list_permissions(limit, offset)
                 → PermissionDAO.get_all(session, limit, offset)
                 → session.query(Permission).offset().limit().all()
```

**Versions**

```
list_versions → text("SELECT * FROM sys_version ORDER BY sort_order")
              → manual row → dict mapping (8 columns)
```

Related table **`sys_version_menu`** is **not** queried by GET `/api/system/menus` (tree uses `sys_menu` only).

---

## 3. Error Handling Map

| Endpoint | Has Try/Except | Error Format on DB Failure | Current Gap |
| -------- | -------------- | ---------------------------- | ----------- |
| GET `/api/system/menus` | **Yes** (`menu_api.py` L198–203) | JSON `{"code":500,"message":"..."}` via `Result.error` | Message may include driver exception text |
| GET `/api/system/permissions` | **No** | Flask default **HTML 500** page | **Confirmed gap** — unhandled `OperationalError` propagates |
| GET `/api/system/versions` | **Yes** (`menu_api.py` L21–32) | JSON `{"code":500,"message":"..."}` via `Result.error` | Same as menus |

### Permissions HTML 500 root cause (confirmed)

`list_permissions` (`system_api.py` L241–254) calls `service.list_permissions()` **without** try/except. When MySQL is unreachable, SQLAlchemy raises `OperationalError` before `Result.success` — Flask returns HTML 500. DEV-JWT-SMOKE-EXEC logs confirm stack trace through `PermissionDAO.get_all` → `session.query(Permission)`.

This is **not** an auth failure — JWT decorator completes first (`jwt_util.py` L85).

---

## 4. Minimal Data Needed

Derived from ORM models; exact DDL not in repo — **derive from models before EXEC**.

| Table / Model | Required Columns (minimal) | Minimal Rows | Used By |
| ------------- | -------------------------- | ------------ | ------- |
| `sys_menu` / `SysMenu` | `id`, `parent_id`, `menu_path`, `menu_title`, `menu_icon`, `menu_type`, `has_children`, `redirect_path`, `sort_order`, `is_visible` | **0 rows OK** — returns empty tree `[]` | GET `/api/system/menus` |
| `sys_version` / `SysVersion` | `id`, `version_code`, `version_name`, `description`, `icon`, `sort_order`, `is_active`, `is_default` (+ timestamps if NOT NULL in DDL) | **0 rows OK** — returns empty list `[]` | GET `/api/system/versions` |
| `imbs_permission` / `Permission` | `id`, `perm_code`, `description`, `extra`, `created_at` | **0 rows OK** — returns empty list `[]`; optional seed via `seed_permissions.py` | GET `/api/system/permissions` |
| `sys_version_menu` / `SysVersionMenu` | — | **Not required** for these three GET endpoints | Other menu/version config routes |

**Note:** Table must **exist** even if empty. Missing table → likely **500** (not 404). Connection refused → **500** (current state).

---

## 5. JSON Error Consistency Gap

| Route | Behavior | Recommendation |
| ----- | -------- | -------------- |
| `/api/system/permissions` | HTML 500 on DB failure | Separate task: **SYSTEM-DB-ERROR-JSON-1** — wrap handler in try/except → `Result.error(code=500, message="...")` |
| `/api/system/menus` | JSON 500 | Acceptable for smoke; consider sanitizing exception message (no stack in body) |
| `/api/system/versions` | JSON 500 | Same as menus |

API clients and frontend proxy expect JSON — HTML 500 on permissions is a **client-handling risk** even after DB is fixed.

---

## 6. Config Keys Reference (no values)

| Env key | Purpose |
| ------- | ------- |
| `IBMS_DATABASE_URL` | Full MySQL URI override |
| `IBMS_DB_HOST` | Host (fallback localhost) |
| `IBMS_DB_PORT` | Port (fallback 3306) |
| `IBMS_DB_NAME` | Database name |
| `IBMS_DB_USER` | Username |
| `IBMS_DB_PASSWORD` | Password — **never commit** |
