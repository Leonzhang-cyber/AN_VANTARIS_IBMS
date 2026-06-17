# IBMS DB Seed Dry-run Validation Risk Review

**Task ID:** IBMS-DB-SEED-DRYRUN-VALIDATION

---

## Dry-run Result Risk

| Risk | Assessment |
|---|---|
| Scripts appear broken | Import failure is **environment** issue (missing Flask), not logic failure |
| False confidence | Local dry-run did not prove DB plan — staging re-run required |
| Accidental write | **Mitigated** — import failed before any session; `--apply` not used |

---

## Import / Bootstrap Risk

- Both scripts depend on `flask`, `flask_sqlalchemy`, project `src.*` packages
- `seed_permissions.py` fails with controlled message (exit 1)
- `assign_root_permissions.py` raises traceback on import — cosmetic inconsistency; no write occurred
- **Precondition:** activate project venv before staging dry-run

---

## Root Identification Risk

Not validated in this run. When DB is reachable:

- Multiple `system` type users may require `--did`
- Dry-run should be reviewed before `--apply`

---

## Stale JWT Risk

Unchanged by dry-run. After future `--apply` on assignment script, users must re-login.

---

## Final Preconditions Before Real `--apply`

| # | Precondition |
|---|---|
| 1 | Staging DB backup confirmed |
| 2 | Project venv active; `requirements.txt` satisfied |
| 3 | `IBMS_DB_*` or `IBMS_DATABASE_URL` set (never commit secrets) |
| 4 | `seed_permissions.py` dry-run reviewed — planned create/update/skip acceptable |
| 5 | `assign_root_permissions.py` dry-run reviewed — target DID and merge list acceptable |
| 6 | Operator explicit approval for `--apply` on each script |
| 7 | Re-login plan communicated |

---

## Recommendation

**Do not run `--apply` until staging backup is confirmed and dry-run succeeds with venv + DB connectivity.**

---

## Related Documents

- `docs/architecture/IBMS_DB_SEED_DRYRUN_VALIDATION.md`
- `docs/security/IBMS_DB_SEED_PERMS_EXECUTION_GUARD.md`
