# IBMS DB Seed Permissions Risk Review

**Task:** IBMS-DB-SEED-PERMS-PREP

---

## Lockout Risk

| Scenario | Effect |
|---|---|
| Seed runs but users not updated | JWT `perms` still empty → 403 on A6B/A7B/A10B |
| Seed adds codes root never receives | Root login lacks new codes until `permission_codes` updated |
| Partial seed failure mid-run | Some routes work, others 403 — inconsistent UX |

**Mitigation:** After seed, assign codes to roles/root in separate task; force re-login in staging before production.

---

## Stale JWT Risk

Seeding `imbs_permission` does not change outstanding JWTs. Users must re-login after `User.permission_codes` is updated.

Root entity created before seed has `permission_codes = all_perm_codes_at_init_time` — **new seed rows are not auto-merged** into existing root user.

---

## Duplicate Permission Risk

- `perm_code` has DB unique constraint — duplicate insert fails hard if idempotency broken
- Duplicate Permission models (system vs DID) map same table — use one DAO path in script
- Manual API-created codes with same `perm_code` — script should skip, not fail

---

## Rollback Strategy

1. **Script rollback** — no auto-delete; remove rows manually via SQL or admin API if needed
2. **User assignment rollback** — restore `permission_codes` from backup
3. **Code rollback** — revert seed script commit; DB data remains unless manually cleaned

---

## Verification Checklist Before Execution

| # | Check |
|---|---|
| 1 | DB backup taken (staging first) |
| 2 | `imbs_permission` current row count documented |
| 3 | Root / test user `permission_codes` exported |
| 4 | Env vars set (`IBMS_DB_*` or `IBMS_DATABASE_URL`) — no secrets in script |
| 5 | **Dry-run** `python scripts/seed_permissions.py` — review planned create/update/skip |
| 6 | Run on staging, not production first |
| 7 | **`--apply` only after dry-run approved** |
| 8 | After seed: verify 18 codes present via `SELECT perm_code FROM imbs_permission` |
| 7 | Update test user permissions + re-login |
| 8 | Spot-check modeling/IoT/DID route 200 vs 403 |
| 9 | Confirm no duplicate key errors on re-run |
| 10 | Plan root user permission refresh (separate task if root already exists)

---

## Related Documents

- `docs/architecture/IBMS_DB_SEED_PERMS_PREP.md`
- `docs/security/IBMS_PERMISSIONS_A0_LOCKOUT_RISK_REVIEW.md`
