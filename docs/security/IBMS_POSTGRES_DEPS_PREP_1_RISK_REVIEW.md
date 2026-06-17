# VANTARIS IBMS PostgreSQL Dependency Prep 1 Risk Review

## 1. Security Boundary

| Control | Status |
| ------- | ------ |
| Real `.env` created | **No** |
| DB credential committed | **No** |
| Token committed | **No** |
| Production DB used | **No** |
| Seed/migration executed | **No** |
| Backend source changed | **No** |
| UFMS content merged | **No** |

---

## 2. Dependency Risk

| Item | Assessment |
| ---- | ---------- |
| psycopg added | Driver only — no runtime switch in this task |
| Runtime unchanged | Backend still builds MySQL URI in `database.py` |
| PyMySQL retained | Temporary dual-driver period during migration |
| No Alembic yet | Schema changes still manual/smoke-only until Phase 5 |
| No forced upgrades | Only added `psycopg[binary]`; other pins unchanged |
| UTF-16LE requirements | Encoding quirk documented; install via iconv workaround |

---

## 3. Follow-up Controls

- `database.py` config abstraction as **POSTGRES-CONFIG-ABSTRACTION-1**
- PostgreSQL local smoke as **POSTGRES-LOCAL-SMOKE-EXEC-1**
- Migration framework as **POSTGRES-MIGRATION-FRAMEWORK-1**
- No production data migration until approved
- Do not resume MySQL smoke unless Leon explicitly approves
- Do not connect psycopg to any DB until disposable local PostgreSQL is ready

---

## 4. Cross-System Boundary

- IBMS/UFMS boundary check passed
- No UFMS DB schema or driver logic introduced
