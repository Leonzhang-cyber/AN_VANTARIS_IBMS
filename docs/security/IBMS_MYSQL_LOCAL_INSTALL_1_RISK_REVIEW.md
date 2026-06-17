# VANTARIS IBMS MySQL Local Install 1 Risk Review

## 1. Security Boundary

| Control | Status |
| ------- | ------ |
| Production DB used | **No** |
| Real `.env` created | **No** |
| DB password committed | **No** |
| Token committed | **No** |
| Seed/migration executed | **No** |
| DDL in this task | **No** |
| Backend API testing | **No** |

---

## 2. Local Service Risk

- MySQL runs locally via Homebrew LaunchAgent (`homebrew.mxcl.mysql`)
- Default install: localhost connections only (per Homebrew caveats)
- Empty root password on fresh install — acceptable for disposable local smoke only; do not expose externally
- Do not use production data
- Do not store DB credentials in repo

---

## 3. Follow-up Controls

- Create disposable DB/user only in **DB-LOCAL-SMOKE-EXEC-A-RETRY**
- Use `<LOCAL_SMOKE_DB_PASSWORD>` placeholder in docs — never commit real password
- DDL must stay smoke-only unless promoted in a formal migration task
- No customer data
- Consider `mysql_secure_installation` on host before non-smoke use (out of scope for this task)

---

## 4. Cross-System Boundary

- IBMS/UFMS boundary check passed — no UFMS content in install scope
