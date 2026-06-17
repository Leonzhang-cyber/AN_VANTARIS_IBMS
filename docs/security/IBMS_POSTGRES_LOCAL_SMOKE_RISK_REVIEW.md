# VANTARIS IBMS PostgreSQL Local Smoke Risk Review

## 1. Security Boundary

| Control | Status |
| ------- | ------ |
| Local PostgreSQL only | **Yes** — prep docs reference 127.0.0.1 |
| Production DB | **Not used** |
| Customer data | **None** |
| Real `.env` | **Not created** |
| Credential committed | **No** — placeholder only in docs |
| Token committed | **No** |
| Write APIs tested | **No** — GET-only in EXEC plan |

---

## 2. DDL Safety

- Smoke-only DDL documented, **not executed** in prep task
- Not a production migration
- Separate from MySQL smoke DDL (`IBMS_DB_LOCAL_SMOKE_MINIMAL_DDL.md`)
- Seed rows are disposable local fixtures only

---

## 3. Follow-up Controls

- Execution as **POSTGRES-LOCAL-SMOKE-EXEC-1** separate task
- JWT in `/tmp` only; delete after smoke
- DB password via shell env `<LOCAL_SMOKE_DB_PASSWORD>`
- No production migration without backup/rollback plan
- Keep MySQL route paused unless Leon approves
- UFMS content must not enter IBMS schema

---

## 4. Remaining Technical Risks

| Risk | Mitigation |
| ---- | ---------- |
| `menu_api.py` raw MySQL SQL | May fail on PG until ORM align task |
| `updated_at` without trigger | Acceptable for smoke reads |
| Permission id format | Must match ORM `VARCHAR(32)` hex |
