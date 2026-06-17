# IBMS DB Seed User Permissions Script

**Task ID:** IBMS-DB-SEED-USER-PERMS-SCRIPT  
**Date:** 2026-06-16

---

## 1. Task Scope

- Add idempotent root/admin permission assignment script
- **Do not execute** in this task
- No schema, login, or JWT payload changes
- Does not run `seed_permissions.py`

---

## 2. Files Changed

| File | Purpose |
|---|---|
| `AN_VANTARIS_IBMS-backend/scripts/assign_root_permissions.py` | Merge codes into `User.permission_codes` |
| `docs/architecture/IBMS_DB_SEED_USER_PERMS_SCRIPT.md` | This document |
| `docs/security/IBMS_DB_SEED_USER_PERMS_EXECUTION_GUARD.md` | Execution guardrails |

---

## 3. Script Behavior

| Behavior | Detail |
|---|---|
| **Default** | Dry-run — prints planned merges, no DB write |
| **`--apply`** | Required to persist changes |
| **Idempotent** | Merges missing codes only; never removes existing codes |
| **No duplicates** | Set merge on JSON array |
| **Target** | Default: single `system` type user with `username=system`; else `--did` |
| **Bootstrap** | Lightweight Flask + `init_database()` (same as seed script) |

---

## 4. Permissions Included

Same 18 A2 codes as `seed_permissions.py` (explicit list, no `*`).

---

## 5. Root / Admin Identification Strategy

1. If `--did` provided → exactly that `imbs_users.did`
2. Else → `UserDAO.get_by_type("system")`
3. If exactly one user with `username == "system"` → use it
4. If exactly one system-type user → use it
5. If multiple system users → **exit with error**; require `--did`

Does **not** update all users in bulk.

---

## 6. Re-login Requirement

After `--apply`, affected users must call `/api/did/login` again. Script prints a warning; JWT `perms` remain stale until re-login.

---

## 7. How to Execute Later

**DO NOT EXECUTE IN THIS TASK.**

```bash
cd AN_VANTARIS_IBMS-backend
# 1. seed permission definitions first (separate script)
python scripts/seed_permissions.py
# 2. dry-run assignment
python scripts/assign_root_permissions.py
# 3. apply after review
python scripts/assign_root_permissions.py --apply
# or explicit DID:
python scripts/assign_root_permissions.py --did 'did:imbs:system:root:...' --apply
```

---

## 8. Pending Validation

- [ ] `UserDAO` + Flask `db.session` against live MySQL
- [ ] Multiple system-user edge case in staging
- [ ] JWT `perms` spot-check after re-login
- [ ] Confirm no conflict with wildcard `*` already on root

---

## Related Documents

- `docs/architecture/IBMS_DB_SEED_USER_PERMS_PREP.md`
- `docs/security/IBMS_DB_SEED_USER_PERMS_EXECUTION_GUARD.md`
