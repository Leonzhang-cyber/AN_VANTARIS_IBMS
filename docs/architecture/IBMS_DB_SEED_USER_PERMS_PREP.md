# VANTARIS IBMS DB Seed User Permissions Prep

**Task:** IBMS-DB-SEED-USER-PERMS-PREP  
**Date:** 2026-06-16  
**Type:** Read-only inventory — no runtime or DB changes

---

## 1. Task Scope

- Inventory only
- No runtime source changed
- No DB schema changed
- No seed executed
- No login changed
- No JWT payload changed

---

## 2. User / Entity Permission Storage

| Property | Detail |
|---|---|
| **Table** | `imbs_users` |
| **Model** | `DID/models.py` — class `User` |
| **Field** | `permission_codes` — `JSON` column, nullable |
| **Format** | JSON array of strings, e.g. `["device:read", "modeling:train"]` |
| **No role table** | No separate `imbs_role` — permissions stored per entity |
| **Entity type** | `entity_type_id` → `imbs_entity_type.type_code` (`system`, `property`, etc.) |
| **Hierarchy** | `imbs_relationship` parent/child DIDs; sub-entity permissions must ⊆ parent at creation |
| **Login → JWT** | `did_api.login` → `user.permission_codes` → `create_jwt({"sub": did, "perms": perms})` |

**Admin vs user:** No dedicated admin flag. "Root" is the `system` entity type user created by `init_system_entity()`. Other entities get permissions at VC issuance / entity creation.

---

## 3. Existing Root Behavior

| Event | Behavior |
|---|---|
| **First `init_system_entity()`** | Loads `perm_dao.get_all()` → assigns all `perm_code` values to new root `User.permission_codes` |
| **Root already exists** | Returns existing DID; **does not** refresh permissions from table |
| **After `seed_permissions.py`** | New rows in `imbs_permission` are **not** auto-merged into existing root |
| **Assignment needed** | Explicit script required to merge A2 codes into root (and optionally other admin DIDs) |

---

## 4. Required Assignment Strategy

| Target | Suggested codes |
|---|---|
| **Root / admin** | Full A2 set (18 codes) or superset from `imbs_permission` after seed |
| **Role-based** | Later task — map Supervisor/Engineer/Operator per A2 matrix |
| **System service / edge** | Pending machine identity design |
| **Password** | Do not change `password_hash` in assignment |
| **Re-login** | Required after `permission_codes` update for JWT `perms` to refresh |

Recommended order:

1. Run `seed_permissions.py` (permission definitions)
2. Run `assign_root_permissions.py --dry-run` (default)
3. Review diff → `--apply`
4. Re-login root/admin DIDs in staging
5. Verify A6B/A7B/A10B and menu JWT routes

---

## 5. Safety Requirements

- **Idempotent** — merge missing codes only; no duplicate entries in JSON array
- **No destructive delete** — do not remove existing codes from `permission_codes`
- **No password reset** — assignment touches `permission_codes` only
- **No login / JWT payload change** — runtime login code unchanged
- **Backup before execution** — export `imbs_users` permission columns
- **Staging first** — never first-run on production

---

## Related Documents

- `docs/security/IBMS_DB_SEED_USER_PERMS_RISK_REVIEW.md`
- `docs/architecture/IBMS_DB_SEED_PERMS_PREP.md`
- `AN_VANTARIS_IBMS-backend/scripts/seed_permissions.py`
