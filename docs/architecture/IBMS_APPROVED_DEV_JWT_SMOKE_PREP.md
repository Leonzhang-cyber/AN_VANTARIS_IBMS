# VANTARIS IBMS Approved Dev JWT Smoke Prep

## 1. Task Scope

- prepare non-production dev JWT smoke
- no token generated
- no real `.env` created
- no production secret used
- no DB write
- no seed/migration
- no backend/frontend source changed

Base commit: `e0bd8f5` — fix(ibms): return JSON 401 for JWT auth failures

---

## 2. Current Auth State

- **BACKEND-AUTH-401-FIX-1** fixed missing/invalid token responses from **500 → 401** with JSON body `{"code":401,"data":null,"message":"Unauthorized"}`.
- **Backend local-smoke** binds `127.0.0.1:5001` when `IBMS_ENV=local-smoke`; blockchain and IoT DeviceManager startup are skipped.
- **No-token GET** on protected system routes returns **401** (verified in AUTH-401-FIX-1).
- **Next step (DEV-JWT-SMOKE-EXEC):** with an approved in-memory dev token, verify **200** (or **500** if DB unavailable) on GET smoke endpoints; **403** only on routes that use `@require_permission`.

---

## 3. JWT Verification Findings

| Item | Finding | Evidence |
| ---- | ------- | -------- |
| JWT utility file | `AN_VANTARIS_IBMS-backend/src/common/utils/jwt_util.py` — `create_jwt`, `decode_jwt`, `@jwt_required` | Lines 9–86 |
| Secret/config key | Env **`IBMS_JWT_SECRET`** → Flask config **`JWT_SECRET_KEY`**. If unset, dev-only fallback constant in `default.py` (not production-safe). No separate local-smoke JWT key. | `default.py` L101–105; `jwt_util._get_secret()` L9–16 |
| Expected header | `Authorization: Bearer <token>` | `jwt_util.jwt_required` L54–58 |
| Expected payload fields | **`sub`** (DID / principal id, required for `g.current_did`). **`exp`**, **`iat`** added automatically by `create_jwt`. Permissions optional via **`perms`**, **`permission_codes`**, or **`permissions`** (list). Legacy optional: **`frontend_perms`**, **`api_perms`**. Production login path uses `{"sub": did, "perms": perms}`. | `jwt_util.create_jwt` L18–37; `jwt_required` L66–83; `did_api.login` L448, L461 |
| Algorithm | **HS256** (config `JWT_ALGORITHM`, default HS256) | `default.py` L104; `jwt_util` L34–37, L47–48 |
| Expiration handling | Default **8 hours** (`JWT_EXPIRATION_HOURS`); `ExpiredSignatureError` → **401 Unauthorized** | `default.py` L105; `jwt_util` L25–30, L61–62 |
| Missing token behavior | **401** — `Result.error(code=401, message="Unauthorized")` | `jwt_util` L55–56 |
| Invalid token behavior | **401** — same envelope for bad signature / malformed token | `jwt_util` L63–64 |

**Secret handling for EXEC (no real values in repo):**

- Use existing dev fallback by starting with **no `.env`** (same as RUN-2), **or**
- Set ephemeral session env only: `IBMS_JWT_SECRET=<LOCAL_SMOKE_JWT_SECRET>` (generate per-run, never commit).
- Token must be signed with the **same** secret the running backend reads from `JWT_SECRET_KEY`.

**Minimal dev payload for system GET smoke** (no permission decorator on target routes):

```json
{
  "sub": "did:imbs:smoke:dev:local"
}
```

Optional `perms: []` or `perms: ["*"]` — not required for `/api/system/menus|permissions|versions` GET.

---

## 4. Protected Route Findings

All three smoke GET endpoints use **`@jwt_required` only** — no `@require_permission` on these handlers.

| Endpoint | Guard | Permission decorator | DB dependency | Expected without token | Expected with dev token |
| -------- | ----- | -------------------- | ------------- | ---------------------- | ----------------------- |
| GET `/api/system/menus` | `@jwt_required` | None | **Yes** — `MenuService.get_menu_tree()` → `sys_menu` via SQLAlchemy | **401** | **200** with menu tree (possibly `[]`) if MySQL reachable; **500** if connection/query fails |
| GET `/api/system/permissions` | `@jwt_required` | None | **Yes** — `SystemService.list_permissions()` | **401** | **200** with permission list (possibly `[]`); **500** on DB error |
| GET `/api/system/versions` | `@jwt_required` | None | **Yes** — raw SQL `SELECT * FROM sys_version` | **401** | **200** with version rows (possibly `[]`); **500** on DB error |

**403 note:** `@require_permission` exists in `permission_util.py` and is used on DID/IoT/modeling routes (e.g. `did:manage`, `device:manage`) but **not** on the three system GET smoke targets. Valid dev token on these routes should **not** return 403 unless a future change adds permission guards.

**Reference routes:**

- `menu_api.py` — `get_menu_tree` L195–203, `list_versions` L18–32
- `system_api.py` — `list_permissions` L241–254

---

## 5. Proposed DEV-JWT-SMOKE-EXEC

Subsequent execution task (requires explicit approval):

1. **local-smoke only** — `IBMS_ENV=local-smoke`, bind `127.0.0.1:5001`.
2. **Non-production placeholder secret** — use dev fallback or ephemeral `IBMS_JWT_SECRET=<LOCAL_SMOKE_JWT_SECRET>` in shell only; **no `.env` file**.
3. **Generate short-lived dev token in memory or `/tmp` script only** — use `create_jwt({"sub": "did:imbs:smoke:dev:local"})` inside a one-off Python snippet with Flask app context, or equivalent PyJWT with same secret/algorithm/exp.
4. **Do not commit token** — stdout for curl only; redact in logs/docs.
5. **Start backend** on `127.0.0.1:5001` (existing Python 3.11 venv).
6. **GET-only curl smoke:**
   - No header → expect **401**
   - `Authorization: Bearer invalid.local.smoke.token` → **401**
   - Valid dev Bearer → expect **200** (or document **500** as DB-blocked, not auth failure)
7. **Stop backend** after verification.

**Optional pre-check:** `GET /api/system/test` (`@jwt_required`, no DB) can validate JWT acceptance before DB-dependent routes.

---

## 6. Stop Conditions

Stop DEV-JWT-SMOKE-EXEC and record **BLOCKED** if:

| Condition | Status in prep |
| --------- | -------------- |
| Requires production secret | **Not required** — dev fallback available |
| Requires production DB | **Not required** — local MySQL with dev fallbacks; 500 acceptable if DB absent (document separately) |
| Requires seed/migration | **Not for auth gate** — empty tables may still return 200 with `[]` |
| Requires write API testing | **No** |
| Requires committing token | **No** |
| Requires broad auth rewrite | **No** — only in-memory token generation for EXEC |

**Recommendation:** Proceed to **DEV-JWT-SMOKE-EXEC** after explicit approval. Coordinate **DB local-smoke** in parallel if **200 with data** is required; auth-only EXEC can still prove **401 → 200/500** transition.

---

## 7. Local-Smoke Config Summary

| Item | Value / source |
| ---- | -------------- |
| `IBMS_ENV` | `local-smoke` |
| `IS_LOCAL_SMOKE` | `True` |
| `BIND_HOST` / `BIND_PORT` | `127.0.0.1` / `5001` (defaults) |
| `JWT_SECRET_KEY` | `IBMS_JWT_SECRET` env or dev fallback |
| `JWT_ALGORITHM` | `HS256` |
| `JWT_EXPIRATION_HOURS` | `8` |
| DB | Dev fallbacks `127.0.0.1:3306` / `ibms_db` — not required for server bind |

No `.env` or production credentials needed for JWT smoke prep or proposed EXEC auth boundary.
