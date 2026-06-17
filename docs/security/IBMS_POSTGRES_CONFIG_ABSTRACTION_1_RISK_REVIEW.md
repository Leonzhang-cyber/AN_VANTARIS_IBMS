# VANTARIS IBMS PostgreSQL Config Abstraction 1 Risk Review

## 1. Security Boundary

| Control | Status |
| ------- | ------ |
| Real `.env` created | **No** |
| DB credential committed | **No** |
| Token committed | **No** |
| Production DB used | **No** |
| DB connection performed | **No** |
| Seed/migration executed | **No** |
| UFMS content merged | **No** |

---

## 2. Config Safety

- DB URI must come from environment / `Config.SQLALCHEMY_DATABASE_URI`
- No hardcoded production URI in `database.py`
- Placeholder passwords only in smoke test shell (not committed)
- MySQL fallback remains legacy-only when `IBMS_DATABASE_URL` unset

---

## 3. Remaining Risks

| Risk | Status |
| ---- | ------ |
| PostgreSQL local DB not installed | Pending B2 |
| Raw MySQL SQL in `menu_api.py` | Pending ORM align task |
| ORM dialect types (MySQL) | Pending ORM align task |
| Alembic baseline | Pending migration framework task |

---

## 4. Follow-up Controls

- Install local PostgreSQL before smoke execution
- Use shell env `IBMS_DATABASE_URL` only — never commit credentials
- Keep MySQL local-smoke route paused unless Leon approves
