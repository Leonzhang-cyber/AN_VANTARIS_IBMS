# VANTARIS IBMS PostgreSQL ORM Align 1

## 1. Task Scope

* reduce PostgreSQL raw SQL risk
* focus on system/menu DB path
* no schema migration
* no seed
* no production DB
* no frontend source change
* no contracts change

## 2. Findings

| File | MySQL-specific Risk | Action |
| ---- | ------------------- | ------ |
| `menu_api.py` | `ON DUPLICATE KEY` in version-menu write paths | Replaced with PostgreSQL-safe update-then-insert flow |
| `menu_api.py` | `GROUP_CONCAT` in init-data read path | Replaced with separate query + Python aggregation |
| `menu_api.py` | raw SQL remains for many routes | Kept where smoke-verified; no contract change in this task |

## 3. Files Changed

| File | Change |
| ---- | ------ |
| `AN_VANTARIS_IBMS-backend/src/api/system/menu_api.py` | Removed MySQL-only upsert and GROUP_CONCAT usage |
| `docs/architecture/IBMS_POSTGRES_ORM_ALIGN_1.md` | Task record |
| `docs/security/IBMS_POSTGRES_ORM_ALIGN_1_RISK_REVIEW.md` | Security/risk notes |

## 4. Verification

| Check | Result |
| ---- | ------ |
| Config PostgreSQL URI import | PASS |
| GET /api/system/menus | PASS (401/401/200) |
| GET /api/system/permissions | PASS (401/401/200) |
| GET /api/system/versions | PASS (401/401/200) |
| npm run build | PASS |

Notes:
- PostgreSQL checks used local disposable DB (`ibms_db`) and existing local backend on 127.0.0.1:5001.
- Temporary JWT was created under `/tmp` and deleted.

## 5. Remaining Gaps

* full ORM model unification pending
* Alembic baseline pending
* production schema pending
* write-path behavior requires later dedicated tests
