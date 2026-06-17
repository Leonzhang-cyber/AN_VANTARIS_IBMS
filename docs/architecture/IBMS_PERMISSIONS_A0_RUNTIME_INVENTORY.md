# VANTARIS IBMS Permissions A0 Runtime Inventory

**Task:** IBMS-PERMISSIONS-A0  
**Date:** 2026-06-16  
**Type:** Read-only inventory — no runtime or DB changes

---

## 1. Task Scope

- Inventory only
- No runtime source changed
- No DB schema changed
- No seed changed
- No login changed
- No JWT payload changed

---

## 2. Current Permission Sources

### 2.1 JWT payload fields

Login (`did_api.py` `login`) issues:

```python
create_jwt({"sub": did, "perms": perms})
```

where `perms = user.permission_codes` from `DIDService.get_entity(did)`.

**Issued claim:** `sub` (DID), `perms` (list of permission codes), plus standard `exp` / `iat`.

**Not issued at login today:** `permission_codes`, `permissions`, `frontend_perms`, `api_perms`.

### 2.2 jwt_util.py — decode and Flask `g`

After `@jwt_required`:

| `g` field | Source |
|---|---|
| `g.jwt_payload` | Full decoded payload |
| `g.current_did` | `payload['sub']` |
| `g.user_permissions` | First non-empty among `perms`, `permission_codes`, `permissions` |
| `g.current_principal` | `{did, permissions}` |
| `g.frontend_perms` | `payload.get('frontend_perms', [])` |
| `g.api_perms` | `payload.get('api_perms', [])` |

### 2.3 permission_util.py behavior

- Reads effective permissions from `g.current_principal` → `g.user_permissions` → `g.jwt_payload` (field priority above).
- **No DB query** at enforcement time.
- Wildcards supported: `*` (superuser), `domain:*` (e.g. `modeling:*` matches `modeling:train`).
- Decorators: `require_permission`, `require_any_permission` → HTTP 403 via `Result.error(message=..., code=403)`.

### 2.4 verify_api_permission (legacy, unused)

`jwt_util.verify_api_permission(required_pattern, method)` checks `g.api_perms` against `"METHOD /path/*"` patterns with `fnmatch`. **Not used by any route handler.** Separate from A2 `domain:action` model.

### 2.5 DB permission model

| Artifact | Location | Notes |
|---|---|---|
| `imbs_permission` table | `DID/models.py` `Permission` | `perm_code`, metadata |
| User permissions | `DID/models.py` `User.permission_codes` | JSON column |
| Permission DAO | `DID/dao.py` `PermissionDAO` | CRUD, lookup by code |
| User DAO | `DID/dao.py` | `update_permissions`, `json_contains` query |
| System permission API | `system/system_api.py` | JWT only — no permission check on CRUD |
| `_resolve_permission_codes` | `DID/did_service.py` | Resolves perm IDs or codes at entity creation |

**Seed files:** No dedicated `*seed*` Python/SQL files found under `AN_VANTARIS_IBMS-backend`. System root entity loads **all rows** from `imbs_permission` at `init_system_entity()` — not literal `["*"]` unless table contains that code.

### 2.6 Root / admin wildcard

- `DID/__init__.py` comments note root may have `permission_codes = ["*"]` or all codes.
- **Runtime `init_system_entity()`** sets `permission_codes=all_perm_codes` from `perm_dao.get_all()` — depends on `imbs_permission` table contents.
- Helper treats `*` in JWT `perms` as allow-all; individual codes from table also work if list is complete.

---

## 3. Current Enforcement Points

| Domain | Commit | Routes | Permissions enforced |
|---|---|---|---|
| **Modeling A6B** | `c236cc4` | 7 route patterns | `modeling:read`, `modeling:train`, `modeling:predict`, `require_any` on generic `{method}` |
| **IoT A7B** | `7840f0e` | 17 JWT write/command/ingest routes | `device:manage`, `iot:command`/`device:control`, `iot:ingest`, `iot:write`, `device:control` |
| **DID A10B** | `d3e2d38` | 5 high-risk POST | `system:admin`/`did:manage`, `did:manage`, `did:issue`, `did:revoke` |

**Not enforced:** `/api/did/me`, system/menu routes, IoT GET, SSE stream/latest, login/challenge.

---

## 4. Lockout Risk

- **Empty `perms` JWT** — Valid authentication but empty permission list → **403** on all A6B/A7B/A10B routes.
- **Stale JWT** — DB `permission_codes` changes do not refresh issued tokens; users need **re-login** (or future token refresh) to pick up new permissions.
- **Root / admin `*`** — Only effective if present in JWT `perms` at login; table-driven root gets explicit codes, not necessarily `*`.
- **System service / edge machine identity** — Not defined; no dedicated M2M token or scoped machine roles in login flow.

---

## 5. Seed Alignment Candidates

Suggested permission codes for `imbs_permission` and role assignment (from A0/A2):

| Code | Domain use |
|---|---|
| `*` | Superuser (optional explicit root) |
| `modeling:read`, `modeling:predict`, `modeling:train` | Modeling API |
| `iot:read`, `iot:write`, `iot:ingest`, `iot:command` | IoT API |
| `device:read`, `device:manage`, `device:control` | Device lifecycle / commands |
| `did:read`, `did:issue`, `did:revoke`, `did:manage` | DID API |
| `system:read`, `system:write`, `system:admin` | System / menu admin |
| `audit:read` | Future audit UI |

Domain wildcards (`modeling:*`, `iot:*`) may be stored if helper wildcard policy is accepted for seed.

---

## 6. Recommended Next Tasks

- **IBMS-DB-SEED-PERMS-PREP** — seed file design and migration strategy (no runtime yet)
- **IBMS-DB-SEED-PERMS** — populate `imbs_permission` and default role mappings
- **IBMS-SECURITY-SYSTEM-B** — JWT + permission on `menu_api` and `system_api`
- **IBMS-SECURITY-A11** — SSE stream/latest and DID GET policy

---

## Related Documents

- `docs/security/IBMS_PERMISSIONS_A0_LOCKOUT_RISK_REVIEW.md`
- `contracts/PERMISSION_MATRIX_A2.md`
- `docs/architecture/IBMS_CORE_A1_PERMISSION_HELPER_PREP.md`
