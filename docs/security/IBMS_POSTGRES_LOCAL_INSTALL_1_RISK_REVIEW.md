# VANTARIS IBMS PostgreSQL Local Install 1 Risk Review

## 1. Security Boundary

| Control | Status |
| ------- | ------ |
| Production DB used | **No** |
| Real `.env` created | **No** |
| DB credential committed | **No** |
| Token committed | **No** |
| DDL executed | **No** |
| Seed/migration executed | **No** |
| Backend started | **No** |

---

## 2. Local Service Risk

- PostgreSQL runs locally via Homebrew LaunchAgent (`homebrew.mxcl.postgresql@16`)
- Default cluster: `/usr/local/var/postgresql@16` — local peer auth for OS user
- Do not expose port 5432 externally
- No production or customer data

---

## 3. Follow-up Controls

- Create disposable DB/user only in smoke execution task
- Use `<LOCAL_SMOKE_DB_PASSWORD>` placeholder in docs — never commit
- Keep MySQL local-smoke route paused unless Leon approves
- UFMS boundary guard remains active
