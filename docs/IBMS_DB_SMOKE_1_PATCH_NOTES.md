# IBMS-DB-SMOKE-1 Patch Notes

**Source commit:** `109aba8` — `test(ibms): prepare local DB smoke profile`  
**Purpose:** Extractable record of smoke-task changes for re-application after baseline recovery  
**Secrets:** None — no tokens, real `.env`, or credentials in this patch set

---

## 1. Commit summary

```
109aba8 test(ibms): prepare local DB smoke profile
 AN_VANTARIS_IBMS-backend/config/local-smoke.env.example |  17 +
 AN_VANTARIS_IBMS-backend/src/api/system/menu_api.py      | 795 +++++++++++++++++++++
 AN_VANTARIS_IBMS-backend/src/api/system/system_api.py    | 534 ++++++++++++++
 AN_VANTARIS_IBMS-backend/src/common/utils/local_smoke.py | 109 +++
 AN_VANTARIS_IBMS-backend/test/smoke/db_jwt_smoke.py     | 134 ++++
 AN_VANTARIS_IBMS-backend/test/smoke/run_db_jwt_smoke.sh |  15 +
 docs/IBMS_DB_LOCAL_SMOKE_PROFILE.md                      | 171 +++++
 7 files changed, 1775 insertions(+)
```

No binary patch file is included. Re-apply by cherry-picking `109aba8`, copying files from this workspace, or following the summaries below.

---

## 2. Files in the patch (7)

| # | Path | Role |
|---|------|------|
| 1 | `AN_VANTARIS_IBMS-backend/src/common/utils/local_smoke.py` | **New** — `IBMS_LOCAL_SMOKE` mock fixtures; stable `DB_UNAVAILABLE` JSON helper |
| 2 | `AN_VANTARIS_IBMS-backend/src/api/system/system_api.py` | **Modified** — `GET /system/permissions`: mock path + `try/except` for stable JSON on DB failure |
| 3 | `AN_VANTARIS_IBMS-backend/src/api/system/menu_api.py` | **Modified** — `GET /system/menus`, `GET /system/versions`: mock path + stable DB error handling |
| 4 | `AN_VANTARIS_IBMS-backend/config/local-smoke.env.example` | **New** — example env flags (`IBMS_LOCAL_SMOKE=true`; placeholders only) |
| 5 | `AN_VANTARIS_IBMS-backend/test/smoke/db_jwt_smoke.py` | **New** — automated smoke (Flask test client; temp JWT under `/tmp`, deleted after run) |
| 6 | `AN_VANTARIS_IBMS-backend/test/smoke/run_db_jwt_smoke.sh` | **New** — shell wrapper for smoke script |
| 7 | `docs/IBMS_DB_LOCAL_SMOKE_PROFILE.md` | **New** — smoke profile documentation |

---

## 3. Behavioral summary (no auth changes)

### Routes covered

- `GET /api/system/menus`
- `GET /api/system/permissions`
- `GET /api/system/versions`

All remain protected by `@jwt_required` — **no auth bypass**.

### Modes

| Mode | Condition | Valid JWT result |
|------|-----------|------------------|
| Mock profile | `IBMS_LOCAL_SMOKE=true` | HTTP **200** with stable fixture JSON (`Result.success`) |
| DB unavailable | Mock off, MySQL down | HTTP **500** JSON: `{"success":false,"error":{"code":"DB_UNAVAILABLE","message":"Database unavailable during local smoke"}}` |
| Live DB | Mock off, MySQL up + seeded | HTTP **200** with live data |

### Key fix

`GET /api/system/permissions` previously returned **HTML 500** when the database was unavailable (no `try/except`). It now returns the same stable JSON shape as menus/versions.

---

## 4. Re-application after baseline recovery (Option A or B)

1. Restore full project baseline (clone or controlled commit).
2. Copy the seven files above from commit `109aba8` or this Desktop workspace.
3. Verify `.gitignore` excludes `.env`, `node_modules`, `dist`, `.venv`.
4. Run `bash AN_VANTARIS_IBMS-backend/test/smoke/run_db_jwt_smoke.sh` (requires Python env — not part of baseline task).
5. Confirm no token files under `/tmp` remain after smoke.

---

## 5. Explicit non-changes

- JWT secret logic — unchanged
- Auth middleware / `jwt_util.py` — unchanged
- Login / password logic — unchanged
- Database schema / migrations — unchanged
- Frontend auth — unchanged
- Real `.env` — not created or committed

---

## 6. Reference

Full smoke runbook: `docs/IBMS_DB_LOCAL_SMOKE_PROFILE.md`  
Baseline recovery: `docs/IBMS_REPO_BASELINE_RECOVERY_REPORT.md`
