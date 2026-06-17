# VANTARIS IBMS MySQL Local Install 1

## 1. Task Scope

- install/start local MySQL only
- no IBMS DB created
- no DB user created
- no DDL executed
- no seed/migration
- no backend started
- no JWT generated
- no production DB used

Base commit: `a6fb4a8` — test(ibms): run DB local smoke

---

## 2. Environment

| Item | Value |
| ---- | ----- |
| Homebrew available | **Yes** — Homebrew 6.0.2 |
| MySQL installed | **Yes** — Homebrew `mysql` 9.6.0_3 |
| mysql CLI | `/usr/local/bin/mysql` |
| MySQL version | **9.6.0** |
| 3306 listening | **Yes** — `mysqld` PID listening on `*:3306` |
| root/socket SELECT VERSION | **PASS** — returned `9.6.0` |

---

## 3. Commands Executed

```bash
brew --version
mysql --version          # not found (pre-install)
brew install mysql
mysql --version          # 9.6.0
which mysql              # /usr/local/bin/mysql
brew services start mysql
brew services list | grep -i mysql
lsof -iTCP:3306 -sTCP:LISTEN -n -P
mysql -uroot -e "SELECT VERSION();"
```

Homebrew initialized MySQL with `--initialize-insecure` (empty root password, localhost only). No password was written to the repository.

---

## 4. Result

| Check | Result |
| ----- | ------ |
| MySQL install | **Success** |
| MySQL service start | **Success** — `brew services` reports `mysql started` |
| root/socket available | **Yes** — `SELECT VERSION()` returned 9.6.0 |
| Ready for DB-LOCAL-SMOKE-EXEC-A-RETRY | **Yes** |

---

## 5. Not Executed

- no DB created
- no user created
- no DDL
- no seed/migration
- no backend start
- no JWT generation
- no API curl
- no `mysql_secure_installation` (optional follow-up on host)

---

## 6. UFMS Boundary Check

| Item | Result |
| ---- | ------ |
| UFMS contamination | **Not found** — boundary/inventory docs only |

---

## 7. Next Tasks

- **DB-LOCAL-SMOKE-EXEC-A-RETRY** — create disposable `ibms_db` / `ibms_user`, apply smoke DDL, run GET JWT smoke
- JWT + DB 200 smoke
- permission enforcement
- DID prep
