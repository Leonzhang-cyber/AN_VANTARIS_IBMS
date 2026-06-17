# IBMS DB Seed User Permissions Execution Guard

**Task ID:** IBMS-DB-SEED-USER-PERMS-SCRIPT

---

## Execution Preconditions

| # | Requirement |
|---|---|
| 1 | Staging environment with DB access |
| 2 | **`seed_permissions.py` run first** — permission rows must exist in `imbs_permission` |
| 3 | Backup completed |
| 4 | Root `did` documented |
| 5 | Operator approval for `--apply` |

---

## Backup Requirement

Before `--apply`:

- Export `imbs_users` (`did`, `username`, `permission_codes`) for target and related admin DIDs
- Keep copy of pre-assignment JWT test results if available

---

## Staging First

1. Staging: `seed_permissions.py`
2. Staging: `assign_root_permissions.py` (dry-run)
3. Staging: `assign_root_permissions.py --apply`
4. Staging: re-login + verify
5. Only then production with same steps

---

## Recommended Run Order

```bash
python scripts/seed_permissions.py
python scripts/assign_root_permissions.py          # dry-run — review output
python scripts/assign_root_permissions.py --apply  # only after review
```

Use `--did` when script reports multiple system users.

---

## Verify After Re-login

- Login as root/admin → confirm JWT contains expected `perms` (do not log token)
- Hit protected modeling / IoT / DID route (200 with codes)
- Hit menu route with Bearer (401 without token)

---

## Rollback Plan

1. Restore `permission_codes` from backup SQL/export
2. Re-login all affected users
3. Script commit revert does not undo DB

---

## No Secret Logging

Script must not print passwords, JWT tokens, DB passwords, or private keys.

---

## Related Documents

- `docs/architecture/IBMS_DB_SEED_USER_PERMS_SCRIPT.md`
- `docs/security/IBMS_DB_SEED_USER_PERMS_RISK_REVIEW.md`
