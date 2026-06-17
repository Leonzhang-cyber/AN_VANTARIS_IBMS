# VANTARIS IBMS DB Local Smoke Exec A

## 1. Task Scope

- local MySQL smoke DB
- disposable local data only
- no production DB
- no real `.env`
- no seed/migration scripts executed
- GET-only smoke (when MySQL available)
- no backend/frontend source changed

Base commit: `16a1abe` — chore(ibms): recover repository baseline

---

## 2. Environment

| Item | Value |
| ---- | ----- |
| MySQL available | **No** — `mysql` CLI not found; port 3306 not listening |
| Block reason | Local MySQL not installed on host; task rule: do not install MySQL in this task |
| DB host | 127.0.0.1 (planned) |
| DB name | ibms_db (planned) |
| DB user | ibms_user (planned) |
| DB password | `<LOCAL_SMOKE_DB_PASSWORD>` — not committed |
| Backend URL | http://127.0.0.1:5001 (not started) |
| IBMS_ENV | local-smoke (not run) |

### Config keys (names only)

From `src/common/config/default.py`:

- `IBMS_DATABASE_URL` (optional override)
- `IBMS_DB_HOST`, `IBMS_DB_PORT`, `IBMS_DB_NAME`, `IBMS_DB_USER`, `IBMS_DB_PASSWORD`
- `SQLALCHEMY_DATABASE_URI` (derived)

---

## 3. Minimal DDL Summary

See [IBMS_DB_LOCAL_SMOKE_MINIMAL_DDL.md](./IBMS_DB_LOCAL_SMOKE_MINIMAL_DDL.md).

| Table | Purpose | Minimal Rows (planned) |
| ----- | ------- | ---------------------- |
| `sys_menu` | menu read smoke | 2 (`menu_path` ORM columns) |
| `sys_version` | version read smoke | 1 (`local-smoke`) |
| `imbs_permission` | permission read smoke | 1 (`system:read`, VARCHAR(32) id) |

**DDL executed:** **No** — blocked by missing MySQL

---

## 4. API Smoke Results

| Endpoint | No Token | Valid Dev Token | Notes |
| -------- | -------- | --------------- | ----- |
| GET /api/system/menus | **SKIPPED** | **SKIPPED** | Backend not started — MySQL BLOCKED |
| GET /api/system/permissions | **SKIPPED** | **SKIPPED** | |
| GET /api/system/versions | **SKIPPED** | **SKIPPED** | |

Expected when unblocked:

- no token → 401
- valid dev token → 200 or explicit JSON error (not connection refused)

---

## 5. Frontend Proxy Smoke

| Route | Result | Notes |
| ----- | ------ | ----- |
| /login | **SKIPPED** | Backend not started |
| /system/permissions | **SKIPPED** | |

---

## 6. Build Verification

| Check | Result |
| ----- | ------ |
| `npm run build` | **PASS** — vue-tsc + vite build ~1.6s |

---

## 7. Temporary Artifacts

| Artifact | Status |
| -------- | ------ |
| `/tmp/ibms-local-smoke-ddl.sql` | Not created (MySQL blocked) |
| `/tmp/ibms-local-smoke-token.txt` | Not created / removed |
| Token committed | **No** |

---

## 8. UFMS Boundary Check

| Item | Result |
| ---- | ------ |
| UFMS in business source | **Not found** |
| Hits | Boundary/inventory docs only — non-contamination reference |
| Execution stopped | **No** |

---

## 9. Remaining Gaps

- **Install/start local MySQL** (separate host prep task) before re-running Exec A
- Apply ORM-aligned minimal DDL from `IBMS_DB_LOCAL_SMOKE_MINIMAL_DDL.md`
- Re-run GET smoke with shell env DB overrides (no `.env`)
- Permission enforcement still pending
- Formal DB migration as separate task
- Contract tests against running backend
