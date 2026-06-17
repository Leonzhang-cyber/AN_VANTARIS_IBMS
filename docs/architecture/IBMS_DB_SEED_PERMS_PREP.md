# VANTARIS IBMS DB Seed Permissions Prep

**Task:** IBMS-DB-SEED-PERMS-PREP  
**Date:** 2026-06-16  
**Type:** Read-only inventory — no runtime, DB, or seed execution

---

## 1. Task Scope

- Inventory only
- No runtime source changed
- No DB schema changed
- No seed executed
- No login changed
- No JWT payload changed

---

## 2. Permission Table / Model Inventory

| Property | Value |
|---|---|
| **Primary model (system module)** | `AN_VANTARIS_IBMS-backend/src/system/models.py` — class `Permission` |
| **Duplicate model (DID module)** | `AN_VANTARIS_IBMS-backend/src/DID/models.py` — class `Permission` (same table) |
| **Table name** | `imbs_permission` |
| **Permission code field** | `perm_code` (`String(64)`, **unique**) |
| **Description field** | `description` (`String(128)`, required) — no separate `name` column |
| **Extra metadata** | `extra` (`JSON`, nullable) |
| **Timestamps** | `created_at` (`DateTime`, server default `CURRENT_TIMESTAMP`); no `updated_at` on permission row |
| **Primary key** | `id` (`String(32)`, UUID hex) |
| **Unique constraint** | `perm_code` unique (SQLAlchemy `unique=True`) |

**DAO layers:**

| Module | File | Class |
|---|---|---|
| System | `src/system/dao.py` | `PermissionDAO` (static methods, used by `SystemService`) |
| DID | `src/DID/dao.py` | `PermissionDAO` (instance methods, used by `DIDService`) |

**CRUD API:** `src/api/system/system_api.py` — `/api/system/permissions` POST/GET/PUT/DELETE (JWT only, no permission check).

**No dedicated seed files** found under backend (`*seed*` glob empty). No SQL migration directory in repo.

---

## 3. Login Permission Flow

```
POST /api/did/login
  → DIDService.get_entity(did)
  → user.permission_codes (JSON column on imbs_users)
  → create_jwt({"sub": did, "perms": perms})
```

| Step | Detail |
|---|---|
| **JWT payload today** | `sub`, `perms`, `exp`, `iat` |
| **Not in JWT** | `permission_codes`, `permissions`, `frontend_perms`, `api_perms` (helper can read if present) |
| **Root permissions** | `init_system_entity()` loads `perm_dao.get_all()` → assigns all `perm_code` values to root `User.permission_codes` at **first** system entity creation only |
| **Existing root** | If system entity already exists, seeding new permission rows does **not** auto-append to root — manual update or re-init policy required (separate task) |
| **Token stale risk** | Login embeds snapshot; DB permission changes require re-login for JWT to reflect new codes |

---

## 4. Required Permission Codes

Aligned with A0/A2 matrix and A6B/A7B/A10B enforcement:

| Code | Domain |
|---|---|
| `modeling:read` | Modeling CSV / model_info / generic read |
| `modeling:predict` | predict, predict_future |
| `modeling:train` | train |
| `iot:read` | IoT GET (future) |
| `iot:write` | standard field/method writes |
| `iot:ingest` | HTTP ingest |
| `iot:command` | device command |
| `device:read` | Device GET (future) |
| `device:manage` | register, update, mappings |
| `device:control` | command alternate, reconnect |
| `did:read` | `/did/me`, GET (future) |
| `did:issue` | VP generate, VC reissue |
| `did:revoke` | VC revoke |
| `did:manage` | entity create, system init alternate |
| `system:read` | system/menu read (future SYSTEM-B) |
| `system:write` | system standard CRUD (future) |
| `system:admin` | permission table, menu admin (future) |
| `audit:read` | Future audit UI |

Optional bootstrap: `*` (superuser wildcard) — **not** in default seed list; document separately if used.

---

## 5. Seed Script Requirements

- **Idempotent** — skip or update description when `perm_code` exists; never duplicate insert
- **No destructive delete** — do not remove existing permissions or user assignments
- **Safe to re-run** — second run should report skipped/updated only
- **No password / secret** — uses env-based DB config via `Config` / `init_database`
- **No user assignment** — seed `imbs_permission` rows only; do not mutate `imbs_users.permission_codes` in v1 script
- **Execution manual and separate** — script invoked explicitly; not run at app startup
- **Lightweight app bootstrap** — prefer `init_database` only (avoid full `create_app()` blockchain/IoT side effects) — see script doc pending validation

---

## 6. Recommended Next Tasks

- **IBMS-DB-SEED-PERMS-SCRIPT** — add `scripts/seed_permissions.py` (do not execute)
- **IBMS-DB-SEED-PERMS-EXECUTE** — manual staging run + root user permission refresh policy
- **IBMS-SECURITY-SYSTEM-B** — system API permission enforcement
- **IBMS-CONTRACTS-A4** — contract tests after seed

---

## Related Documents

- `docs/security/IBMS_DB_SEED_PERMS_RISK_REVIEW.md`
- `docs/architecture/IBMS_PERMISSIONS_A0_RUNTIME_INVENTORY.md`
