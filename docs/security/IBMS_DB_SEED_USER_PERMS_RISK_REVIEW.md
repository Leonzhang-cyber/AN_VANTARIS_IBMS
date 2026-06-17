# IBMS DB Seed User Permissions Risk Review

**Task:** IBMS-DB-SEED-USER-PERMS-PREP

---

## Root Lockout Risk

| Scenario | Impact |
|---|---|
| Assignment skipped after seed | Root JWT missing new codes → 403 on enforced routes |
| Wrong user targeted | Non-root entity over-privileged or root unchanged |
| Empty merge on wrong DID | Operator thinks root updated but login still has old `perms` |

**Mitigation:** Dry-run default; require explicit `--did` when multiple system users exist.

---

## Stale JWT Risk

Updating `permission_codes` does not invalidate outstanding tokens. All clients must **re-login** after assignment.

---

## Over-Privilege Risk

Assigning full 18-code bundle to wrong DID grants broad API access. Script must not bulk-update all users without explicit flag.

Default target: single system root user (`username=system` or `--did`).

---

## Wildcard vs Explicit Permissions

- Root may historically have explicit list from `get_all()` at init time
- Adding literal `*` is optional and grants superuser via `permission_util`
- Assignment script uses **explicit A2 codes** only (no `*` by default)

---

## Rollback Strategy

1. Restore `permission_codes` JSON from backup per DID
2. Re-login to refresh JWT
3. Revert script commit does not undo DB — manual restore required

---

## Execution Checklist

| # | Step |
|---|---|
| 1 | DB backup (`imbs_users`, `imbs_permission`) |
| 2 | Confirm `seed_permissions.py` already run on staging |
| 3 | Export root `did` and current `permission_codes` |
| 4 | Run assignment **dry-run** (default) |
| 5 | Review added codes list |
| 6 | Run with `--apply` only after approval |
| 7 | Re-login root; decode JWT `perms` (no secret logging) |
| 8 | Spot-check modeling / IoT / DID / menu routes |
| 9 | Document production rollout + re-login comms |

---

## Related Documents

- `docs/architecture/IBMS_DB_SEED_USER_PERMS_PREP.md`
- `docs/security/IBMS_DB_SEED_PERMS_EXECUTION_GUARD.md`
