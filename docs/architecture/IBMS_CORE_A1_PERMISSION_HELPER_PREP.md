# VANTARIS IBMS Core A1 Permission Helper Prep

**Task:** IBMS-CORE-A1-PREP  
**Status:** Inspection and design prep only — no runtime changes

---

## 1. Task Scope

- Prep and inspection only
- No runtime source code changed
- No DB schema changed
- No seed changed
- No JWT payload changed
- No login logic changed

---

## 2. Current Auth Utilities

### 2.1 `jwt_required` location

Primary decorator: `AN_VANTARIS_IBMS-backend/src/common/utils/jwt_util.py` (`jwt_required`).

**Usage counts (grep, prep date):**

| Module | `@jwt_required` count |
|---|---|
| `did_api.py` | 6 handlers (me, system/init, entity, vp/generate, vc/reissue, vc/revoke) |
| `modeling_api.py` | 7 (all modeling routes — A6) |
| `iot_api.py` | 17 (write/command/ingest — A7) |
| `sse_api.py` | 1 (`test-sse-push` — A8B) |
| `system_api.py` | 21 (entity-types, permissions, standard-fields/methods, versions) |
| `menu_api.py` | **0** — menu/version routes have no JWT decorator |

### 2.2 Token decode

- `decode_jwt(token)` in `jwt_util.py` uses `JWT_SECRET_KEY` and `JWT_ALGORITHM` from Flask config.
- `jwt_required` reads `Authorization: Bearer <token>`, decodes via `decode_jwt`, returns 401 on missing header, expiry, or invalid token.

### 2.3 Payload fields

Login (`did_api.py` `login`) issues:

```python
create_jwt({"sub": did, "perms": perms})
```

where `perms = user.permission_codes` from `DIDService.get_entity(did)`.

`jwt_required` stores on Flask `g`:

| Field | Source |
|---|---|
| `g.jwt_payload` | Full decoded payload |
| `g.current_did` | `payload.get('sub')` |
| `g.user_permissions` | `payload.get('perms', [])` |
| `g.frontend_perms` | `payload.get('frontend_perms', [])` |
| `g.api_perms` | `payload.get('api_perms', [])` |

**Note:** Login currently sets `perms` only — not `frontend_perms` or `api_perms`. Existing getters: `get_current_permissions()`, `get_current_did()`, `get_current_frontend_perms()`, `get_current_api_perms()`.

### 2.4 Current user context

- DID stored in `g.current_did`; accessible via `get_current_did()` after `@jwt_required`.
- No unified `get_current_principal()` yet.
- Debug `print` statements in `jwt_required` log path, DID, and permissions on every request.

### 2.5 Existing permission helpers

- `verify_api_permission(required_pattern, method)` — checks `g.api_perms` against `"METHOD /path/*"` patterns with `fnmatch`. **Not used by any route handler today.**
- `DIDService` / `User.permission_codes` (JSON column) — source of truth at login; may drift if permissions change in DB without re-login.

### 2.6 `system_api` permission usage

- All CRUD handlers use `@jwt_required` only.
- Permission table CRUD (`/system/permissions`) does **not** check caller has `system:admin` — any valid JWT can mutate permissions today.
- `get_current_did()` imported but used for audit/context in some handlers, not for authorization checks.

### 2.7 Related files (find)

```
AN_VANTARIS_IBMS-backend/src/common/utils/jwt_util.py
```

No dedicated `permission_util.py`, `authz_util.py`, or `auth_*` module exists yet. Permission data model lives under `src/DID/models.py` (`permission_codes` JSON on `User`) and `src/DID/dao.py`.

---

## 3. Proposed Helper Design

New module (suggested): `src/common/utils/permission_util.py` or `authz_util.py`.

| Helper | Purpose |
|---|---|
| `require_permission(permission_code: str)` | Decorator — after JWT, deny 403 if `permission_code` not in effective permissions |
| `require_any_permission(permission_codes: list)` | Decorator — allow if any code matches |
| `get_current_principal()` | Return `{did, permissions, payload}` from `g` |
| `safe_permission_denied_response(message=None)` | Consistent `Result.error` + HTTP 403 |

### Design constraints

1. **Reuse `jwt_required`** — permission decorators should compose innermost-after or wrap JWT (e.g. `@jwt_required` + `@require_permission('modeling:train')`, or combined `@auth_required('modeling:train')` that calls JWT logic first).
2. **Do not change JWT payload in phase 1** — read `g.user_permissions` from existing `perms` claim.
3. **If payload contains `perms`, use payload first** — avoids DB round-trip per request; document stale-token risk.
4. **DB permission lookup is a separate task** — if live DB check needed (permission revoked after token issued), open follow-up; do not block CORE-A1 on DB refactor.

### Effective permission check (phase 1 pseudocode)

```
effective = get_current_permissions()  # from g.user_permissions / payload perms
allow if permission_code in effective or '*' in effective
deny -> safe_permission_denied_response()
```

Align codes with `contracts/PERMISSION_MATRIX_A2.md`.

---

## 4. Candidate Implementation Location

**Recommended:** `AN_VANTARIS_IBMS-backend/src/common/utils/permission_util.py`

Rationale:

- Sits alongside `jwt_util.py` in `common/utils`
- Imported by `modeling_api`, `iot_api`, `did_api`, `system_api`
- Keeps JWT crypto separate from authorization policy

Alternative name `authz_util.py` if team prefers separating authentication (`jwt_util`) from authorization (`authz_util`).

---

## 5. First Enforcement Targets

From `contracts/PERMISSION_MATRIX_A2.md` — apply after helper exists:

| Route / area | Target permission |
|---|---|
| `POST .../train` | `modeling:train` |
| `POST .../predict`, `predict_future` | `modeling:predict` |
| IoT command routes | `iot:command` or `device:control` |
| `POST /iot/ingest/http` | `iot:ingest` |
| `POST /did/vc/revoke` | `did:revoke` |
| `POST /did/vc/reissue`, `/did/vp/generate`, `/did/entity` | `did:issue` |
| `POST /did/system/init` | `did:manage` or `system:admin` |

Modeling GET routes → `modeling:read` in SECURITY-A6B. IoT device register/update → `device:manage` / `iot:write` in SECURITY-A7B.

---

## 6. Risks

| Risk | Detail |
|---|---|
| Token payload may not contain stable permissions | Login embeds `permission_codes` snapshot; DB updates do not invalidate JWT |
| Permission DB model may not align with API permissions | `User.permission_codes` vs `imbs_permission` table vs A2 matrix — naming drift possible |
| Frontend role menu may not map yet | `menu_api.py` unprotected; no route-level link from menu roles to API permissions |
| Backward compatibility | Strict enforcement may break integrators who have JWT but empty `perms` |
| Service/machine identity not finalized | M2M tokens, edge identity, and `*` root wildcard behavior need explicit policy |
| `verify_api_permission` unused | Dead code path using `api_perms` — avoid duplicating incompatible model |
| `menu_api` JWT gap | Documented as JWT-protected in contracts but handlers lack `@jwt_required` — resolve in separate security task |

---

## 7. Recommended Implementation Steps

1. **CORE-A1** — implement helper module + compose with `jwt_required`
2. **CORE-A1 dry review** — manual route inventory vs matrix (no test run required in prep scope)
3. **SECURITY-A6B** — modeling permissions
4. **SECURITY-A7B** — IoT permissions
5. **SECURITY-A10B** — DID permissions
6. **Later:** DB seed alignment, admin UI mapping, optional live DB permission refresh, menu_api JWT + permission audit

---

## Related Documents

- `contracts/PERMISSION_MATRIX_A2.md`
- `contracts/PERMISSION_BOUNDARY_A0.md`
- `docs/security/IBMS_CORE_A1_PERMISSION_HELPER_RISK_REVIEW.md`
