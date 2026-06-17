# IBMS DB Seed Permissions Script

**Task ID:** IBMS-DB-SEED-PERMS-SCRIPT  
**Date:** 2026-06-16

---

## 1. Task Scope

- Add idempotent permission seed script
- Do **not** execute in this task
- Do not change schema, login, JWT payload, or API routes
- Do not assign permissions to users

---

## 2. Files Changed

| File | Purpose |
|---|---|
| `AN_VANTARIS_IBMS-backend/scripts/seed_permissions.py` | Idempotent upsert script |
| `docs/architecture/IBMS_DB_SEED_PERMS_SCRIPT.md` | This document |
| `docs/security/IBMS_DB_SEED_PERMS_EXECUTION_GUARD.md` | Execution guardrails |

---

## 3. Permission Codes Included

18 codes (see `PERMISSION_SEED` dict in script):

`modeling:read`, `modeling:predict`, `modeling:train`, `iot:read`, `iot:write`, `iot:ingest`, `iot:command`, `device:read`, `device:manage`, `device:control`, `did:read`, `did:issue`, `did:revoke`, `did:manage`, `system:read`, `system:write`, `system:admin`, `audit:read`

---

## 4. Script Behavior

| Behavior | Detail |
|---|---|
| **Default** | Dry-run — prints planned create/update/skip; no DB write |
| **`--apply`** | Required to persist changes |
| Idempotent | Existing `perm_code` → skip or update `description` only |
| No delete | Never removes permission rows |
| No user mutation | Does not update `imbs_users.permission_codes` |
| DB config | Uses `Config` + `init_database()` (same env vars as runtime) |
| Bootstrap | Lightweight Flask app — **not** full `create_app()` (avoids blockchain/IoT startup) |
| Exit | `if __name__ == "__main__"` guard — no import side effects |

---

## 5. How to Execute Later

**DO NOT EXECUTE IN THIS TASK.**

When approved for staging:

```bash
cd AN_VANTARIS_IBMS-backend
# Ensure IBMS_DB_* or IBMS_DATABASE_URL env vars are set (see .env.example)
python scripts/seed_permissions.py              # dry-run (default)
python scripts/seed_permissions.py --apply      # write DB after review
```

Dry-run output includes `DRY RUN: no database changes` and planned code lists.

Expected apply output: `created=N, updated=M, skipped=K, expected=18`

Re-run with `--apply` should show `created=0` when all codes exist.

---

## 6. Pending Validation

- [ ] Confirm `session.query(Permission)` works with Flask-SQLAlchemy `db.session` against live MySQL
- [ ] Verify lightweight bootstrap vs full `create_app()` in target deployment
- [ ] Root user permission refresh after seed (separate task)
- [ ] Staging re-login + A6B/A7B/A10B smoke checks

---

## Related Documents

- `docs/architecture/IBMS_DB_SEED_PERMS_PREP.md`
- `docs/security/IBMS_DB_SEED_PERMS_EXECUTION_GUARD.md`
