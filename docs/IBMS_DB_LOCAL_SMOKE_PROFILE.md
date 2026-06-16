# IBMS Local DB Smoke Profile

**Task:** IBMS-DB-SMOKE-1  
**Scope:** Read-only system routes with valid dev JWT — no auth bypass, no committed secrets

---

## 1. Purpose

Provide a repeatable local smoke profile for:

- `GET /api/system/menus`
- `GET /api/system/permissions`
- `GET /api/system/versions`

Valid JWT requests must reach the route handler and return **stable JSON** — either HTTP 200 with fixture data (mock profile) or HTTP 500 with a fixed `DB_UNAVAILABLE` payload when MySQL is not running. Unauthenticated requests must remain **401**.

---

## 2. Database configuration path

Backend DB settings are resolved in `AN_VANTARIS_IBMS-backend/src/common/config/default.py`:

| Setting | Source | Default (dev fallback) |
|---------|--------|-------------------------|
| Host | `IBMS_DB_HOST` or `IBMS_DATABASE_URL` | `127.0.0.1` |
| Port | `IBMS_DB_PORT` | `3306` |
| Database | `IBMS_DB_NAME` | `ibms_db` |
| User | `IBMS_DB_USER` | `ibms_user` |
| Password | `IBMS_DB_PASSWORD` | placeholder only |
| ORM | SQLAlchemy + PyMySQL | `SQLALCHEMY_DATABASE_URI` |

Route data access:

| Route | Module | Access |
|-------|--------|--------|
| `/api/system/menus` | `menu_api.get_menu_tree` | `MenuService.get_menu_tree` → SQLAlchemy |
| `/api/system/permissions` | `system_api.list_permissions` | `SystemService.list_permissions` → SQLAlchemy |
| `/api/system/versions` | `menu_api.list_versions` | raw SQL `SELECT * FROM sys_version` |

See `AN_VANTARIS_IBMS-backend/.env.example` for documented environment variables. **Do not commit `.env`.**

---

## 3. Local smoke modes

### Option A — Local MySQL (preferred when available)

1. Start MySQL on `127.0.0.1:3306` with database `ibms_db`.
2. Copy `.env.example` → gitignored `.env` and set `IBMS_DB_*` placeholders locally.
3. Run migrations/seeds per existing IBMS DB docs.
4. Leave `IBMS_LOCAL_SMOKE` unset → routes read live data (HTTP 200 when schema is seeded).

### Option B — Mock profile (no MySQL required)

1. Copy `AN_VANTARIS_IBMS-backend/config/local-smoke.env.example` values into a **gitignored** `.env`.
2. Set `IBMS_LOCAL_SMOKE=true`.
3. Valid JWT requests return stable fixture JSON (HTTP 200) for the three routes.
4. JWT is still required — mock data is **not** a public bypass.

Fixtures live in `src/common/utils/local_smoke.py`.

### Option C — DB unavailable JSON normalization (default without mock)

When `IBMS_LOCAL_SMOKE` is not enabled and MySQL is down:

```json
{
  "success": false,
  "error": {
    "code": "DB_UNAVAILABLE",
    "message": "Database unavailable during local smoke"
  }
}
```

HTTP status: **500**. No HTML error pages, no stack traces, no secrets.

Previously, `GET /api/system/permissions` could return an HTML 500 because it lacked a `try/except` handler; that path is now aligned with menus/versions.

---

## 4. Generating a dev JWT (never commit the token)

Use the development JWT secret from environment or the documented dev fallback in `default.py` (`IBMS_JWT_SECRET` / `dev-only-jwt-secret-do-not-use-in-production`).

Example (token written only under `/tmp`):

```bash
cd AN_VANTARIS_IBMS-backend
python3 - <<'PY'
import os, tempfile
from pathlib import Path
os.environ.setdefault("IBMS_LOCAL_SMOKE", "true")
from unittest.mock import patch
with patch("src.main.init_system_on_startup"), patch("src.main.init_iot_device_manager"):
    from src.main import create_app
    from src.common.utils.jwt_util import create_jwt
    app = create_app()
    with app.app_context():
        token = create_jwt({"sub": "did:imbs:smoke:dev", "perms": ["system:smoke:read"]})
    path = Path(tempfile.gettempdir()) / "ibms-dev-jwt-smoke.token"
    path.write_text(token)
    print(f"Token written to {path} (delete after smoke)")
PY
```

Delete the file immediately after curl checks:

```bash
rm -f /tmp/ibms-dev-jwt-smoke.token
```

---

## 5. Expected curl results

Base URL (DEV-JWT-SMOKE-EXEC): `http://127.0.0.1:5001/api`

```bash
# No token → 401
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:5001/api/system/menus

# Invalid token → 401
curl -s -o /dev/null -w "%{http_code}\n" \
  -H "Authorization: Bearer not-a-valid-token" \
  http://127.0.0.1:5001/api/system/menus

# Valid token, DB down, mock off → 500 JSON DB_UNAVAILABLE
curl -s -H "Authorization: Bearer $(cat /tmp/ibms-dev-jwt-smoke.token)" \
  http://127.0.0.1:5001/api/system/permissions

# Valid token, IBMS_LOCAL_SMOKE=true → 200 JSON with fixture data
curl -s -H "Authorization: Bearer $(cat /tmp/ibms-dev-jwt-smoke.token)" \
  http://127.0.0.1:5001/api/system/menus
```

Automated check (Flask test client, no live server required):

```bash
cd AN_VANTARIS_IBMS-backend
bash test/smoke/run_db_jwt_smoke.sh
```

---

## 6. Frontend proxy sanity

Frontend API base is configured via `VITE_IBMS_API_BASE_URL` (see `AN_VANTARIS_IBMS-frontend/.env.example`). Vite dev server does not embed JWT tokens in the proxy config — tokens remain in client storage / request headers only. No frontend auth changes are required for this smoke profile.

---

## 7. Forbidden changes

- Do **not** commit `.env`, production secrets, or generated JWT tokens
- Do **not** modify JWT validation, auth middleware, login, or password logic
- Do **not** disable `@jwt_required` or bypass auth guards
- Do **not** change production seed credentials or schema/migrations in smoke-only work

---

## 8. Related files

| File | Role |
|------|------|
| `src/common/utils/local_smoke.py` | Mock fixtures + DB error helper |
| `src/api/system/menu_api.py` | Menus + versions handlers |
| `src/api/system/system_api.py` | Permissions handler |
| `config/local-smoke.env.example` | Example mock profile flags |
| `test/smoke/db_jwt_smoke.py` | Automated smoke script |
| `test/smoke/run_db_jwt_smoke.sh` | Shell wrapper |
