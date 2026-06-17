# IBMS DB Seed Permissions Execution Guard

**Task ID:** IBMS-DB-SEED-PERMS-SCRIPT

---

## Execution Preconditions

| # | Requirement |
|---|---|
| 1 | Staging environment with valid DB connectivity |
| 2 | `IBMS_DATABASE_URL` or `IBMS_DB_*` exported — **never** hardcode credentials in script |
| 3 | DBA / operator approval for `imbs_permission` writes |
| 4 | Backup completed (see below) |
| 5 | No concurrent permission table migrations |
| 6 | **Dry-run first** — `python scripts/seed_permissions.py` (no `--apply`) |
| 7 | **`--apply` only after dry-run review** |

---

## Dry-run Default (SEED-SAFETY-GUARD)

Both seed scripts default to dry-run:

| Script | Default | Write DB |
|---|---|---|
| `seed_permissions.py` | dry-run | `--apply` required |
| `assign_root_permissions.py` | dry-run | `--apply` required |

Never pass `--apply` without staging backup and operator review.

---

## Backup Requirement

Before first execution:

- Full DB backup or at minimum `imbs_permission` + `imbs_users` export
- Record current `perm_code` list and root `permission_codes` JSON

---

## Staging First

- **Never** first-run seed directly on production
- Re-run script on staging twice to confirm idempotency (`created=0` on second run)
- Only then promote to production with same procedure

---

## Rollback Plan

1. Script does not delete — rollback is manual DELETE of seeded rows (if needed) or restore from backup
2. Restore `imbs_users.permission_codes` if accidentally modified in follow-up task
3. Revert script commit does not undo DB state

---

## Re-login Requirement After Seed

Seeding permission **definitions** does not update JWTs. After user `permission_codes` are updated (separate task):

- All clients must obtain new token via `/api/did/login`
- Until re-login, stale or empty `perms` cause 403 on enforced routes

---

## No Secret Logging

Script must not print:

- Database passwords
- JWT tokens
- Private keys
- Full connection URIs with credentials

Script prints counts and planned code lists only (`created` / `updated` / `skipped` / `planned create|update|skip`).

---

## Accidental Write Risk (mitigated)

Prior versions of `seed_permissions.py` wrote on every invocation. **SEED-SAFETY-GUARD** requires explicit `--apply`. Always dry-run first.

---

## Related Documents

- `docs/architecture/IBMS_DB_SEED_PERMS_SCRIPT.md`
- `docs/security/IBMS_DB_SEED_PERMS_RISK_REVIEW.md`
