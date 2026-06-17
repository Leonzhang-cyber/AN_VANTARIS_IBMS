# VANTARIS IBMS PostgreSQL Migration Risk Review

## 1. Security Boundary

| Control | Status |
| ------- | ------ |
| Production DB used | **No** — read-only study |
| Real `.env` created | **No** |
| DB credential committed | **No** |
| Token committed | **No** |
| Seed/migration executed | **No** |
| Backend source changed | **No** |
| Frontend source changed | **No** |
| UFMS content merged | **No** |
| MySQL smoke continued | **No** — route paused per direction change |

---

## 2. Migration Risks

| Risk | Severity | Mitigation |
| ---- | -------- | ---------- |
| MySQL-specific SQL fails on PostgreSQL | **High** | Phase 4 rewrite; prioritize `menu_api.py` |
| `database.py` ignores `IBMS_DATABASE_URL` scheme | **High** | Phase 2 config abstraction |
| Raw SQL bypasses ORM portability | **High** | ORM-first policy; audit all `text()` usage |
| Schema mismatch breaks API JSON shape | **Medium** | Contract tests + GET smoke after PG DDL |
| Dev fallback credentials in production | **Medium** | Externalize secrets; block prod without env |
| Local-smoke schema mistaken for production | **Medium** | Document smoke-only; separate Alembic baseline |
| Duplicate ORM models diverge | **Medium** | Consolidate `EntityType`/`Permission` before Alembic |
| Dual declarative base vs `db.Model` | **Medium** | Single metadata strategy for migrations |

---

## 3. Data Risks

- No customer data imported in this task
- No production dump used
- Production migration requires backup/rollback plan before approval
- Seed scripts (`seed_permissions.py`) must target disposable local DB only when `--apply` is explicitly run

---

## 4. Cross-System Risk

- UFMS schema or code must not be copied into IBMS
- Integration should use contracts/API only
- Any UFMS DB reference inside IBMS runtime code must stop execution and await Leon instruction
- Boundary check this task: **passed** (governance docs only)

---

## 5. Follow-up Controls

| Follow-up | Separate task |
| --------- | ------------- |
| PostgreSQL driver in requirements | POSTGRES-DEPS-PREP-1 |
| Config / URI abstraction | POSTGRES-CONFIG-ABSTRACTION-1 |
| PostgreSQL local install | POSTGRES-LOCAL-INSTALL-1 |
| PostgreSQL local-smoke | POSTGRES-LOCAL-SMOKE-EXEC-1 |
| ORM + raw SQL alignment | POSTGRES-ORM-ALIGN-1 |
| Alembic baseline | POSTGRES-MIGRATION-FRAMEWORK-1 |
| Do **not** resume MySQL smoke unless Leon explicitly approves |
