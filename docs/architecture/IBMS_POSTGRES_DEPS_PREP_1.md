# VANTARIS IBMS PostgreSQL Dependency Prep 1

## 1. Task Scope

- add PostgreSQL driver dependency
- keep MySQL driver temporarily
- no runtime DB switch
- no `database.py` change
- no PostgreSQL install/start
- no seed/migration
- no backend source change
- no frontend source change
- **MySQL local-smoke route paused** — PostgreSQL is target canonical DB

Base commit: `33b4adc` — docs(ibms): study PostgreSQL database architecture

---

## 2. Dependency Change

| Dependency | Action | Reason |
| ---------- | ------ | ------ |
| `psycopg[binary]==3.2.13` | **Added** | PostgreSQL target driver (SQLAlchemy: `postgresql+psycopg://`) |
| `PyMySQL==1.1.2` | **Kept** | Legacy MySQL compatibility during staged migration |
| Alembic / Flask-Migrate | **Not added** | Migration framework is separate task |

`requirements-macos-smoke.txt` unchanged — continues `-r requirements.txt`.

---

## 3. Verification

| Check | Result | Notes |
| ----- | ------ | ----- |
| pip install `psycopg[binary]==3.2.13` | **PASS** | Python 3.11 venv; installed psycopg 3.2.13 + psycopg-binary |
| import psycopg | **PASS** | 3.2.13 |
| import pymysql | **PASS** | present in venv (pinned 1.1.2 in requirements) |
| import sqlalchemy | **PASS** | 2.0.49 |
| local-smoke Config import | **PASS** | `IS_LOCAL_SMOKE=True`, URI configured (still MySQL scheme) |
| npm run build | **FAIL** | `vue-tsc: command not found` — frontend deps not installed in this task scope |

Install note: `requirements.txt` remains UTF-16LE on disk; pip used `iconv` → `/tmp/ibms-requirements-utf8.txt` for install. No DB connection attempted.

---

## 4. Not Changed

- no `database.py` change
- no runtime DB switch (URI still `mysql+pymysql://` via config)
- no `IBMS_DATABASE_URL` change
- no backend API test
- no PostgreSQL/MySQL DB install in this task
- no seed/migration
- no frontend source change
- no contracts change

---

## 5. UFMS Boundary Check

| Item | Result |
| ---- | ------ |
| UFMS contamination | **Not found** — boundary/inventory docs only |

---

## 6. Pre-check Note

Working tree had unrelated dirty docs (`docs/IBMS_REPO_BASELINE_RECOVERY_REPORT.md`, untracked `docs/IBMS_BASELINE_COMMIT_REPORT.md`) — **not included** in this commit.

---

## 7. Next Tasks

- **POSTGRES-CONFIG-ABSTRACTION-1** — unify URI init; support `postgresql+psycopg://`
- **POSTGRES-LOCAL-INSTALL-1** — install/start local PostgreSQL
- **POSTGRES-LOCAL-SMOKE-EXEC-1** — disposable DB + GET JWT smoke
- **POSTGRES-ORM-ALIGN-1** — MySQL raw SQL rewrite
- **POSTGRES-MIGRATION-FRAMEWORK-1** — Alembic baseline
