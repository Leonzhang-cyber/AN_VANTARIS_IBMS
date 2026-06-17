# VANTARIS IBMS PostgreSQL Local Install 1

## 1. Task Scope

- install/start local PostgreSQL only
- no IBMS DB created
- no DB user created
- no DDL
- no seed/migration
- no backend start
- no JWT

Base commit: `80861bf` — feat(ibms): support PostgreSQL database URI

---

## 2. Environment

| Item | Value |
| ---- | ----- |
| Homebrew available | **Yes** — Homebrew 6.0.2 |
| PostgreSQL installed | **Yes** — Homebrew `postgresql@16` 16.14 |
| psql path | `/usr/local/opt/postgresql@16/bin/psql` |
| psql version | **16.14** (Homebrew) |
| 5432 listening | **Yes** — `127.0.0.1:5432` and `[::1]:5432` |
| SELECT version() | **PASS** |

---

## 3. Commands Executed

```bash
brew install postgresql@16
brew services start postgresql@16
export PATH="/usr/local/opt/postgresql@16/bin:$PATH"
psql --version
psql postgres -c "SELECT version();"
```

---

## 4. Result

| Check | Result |
| ----- | ------ |
| Install | **Success** |
| Service start | **Success** — `postgresql@16 started` |
| Local connection | **PASS** — peer/local socket via `psql postgres` |

Ready for **POSTGRES-LOCAL-SMOKE-EXEC-1** (disposable DB/user + smoke DDL).

---

## 5. Not Executed

- no IBMS DB created
- no DB user created
- no DDL
- no seed/migration
- no backend start
- no JWT generation

---

## 6. Next Tasks

- POSTGRES-LOCAL-SMOKE-PREP-1 (docs — may overlap with this batch B3)
- POSTGRES-LOCAL-SMOKE-EXEC-1
