# VANTARIS IBMS PostgreSQL Local Smoke Exec 1

## 1. Task Scope

* PostgreSQL local smoke execution
* disposable local DB/user
* smoke-only DDL
* backend local-smoke with PostgreSQL URL
* short-lived dev JWT
* GET-only API smoke
* no write API testing
* no production DB
* no real .env
* no seed/migration
* no backend/frontend source change

## 2. Execution Summary

| Item                        | Result    |
| --------------------------- | --------- |
| PostgreSQL local service    | PASS      |
| DB created/existed          | ibms_db   |
| User created/existed        | ibms_user |
| DDL applied                 | PASS      |
| Backend PostgreSQL startup  | PASS      |
| JWT smoke                   | PASS      |
| Frontend source modified    | No        |
| Backend source modified     | No        |
| Raw/contracts modified      | No        |
| Token committed             | No        |
| DB password committed       | No        |
| Runtime artifacts committed | No        |

## 3. Environment

| Item          | Value                                    |
| ------------- | ---------------------------------------- |
| PostgreSQL    | 16.14                                    |
| Host          | 127.0.0.1                                |
| Port          | 5432                                     |
| DB            | ibms_db                                  |
| User          | ibms_user                                |
| Password      | <LOCAL_SMOKE_DB_PASSWORD>, not committed |
| Backend URL   | http://127.0.0.1:5001                    |
| IBMS_ENV      | local-smoke                              |
| DB URL Scheme | postgresql+psycopg                       |

## 4. DDL Result

| Table           | Result         | Row Count |
| --------------- | -------------- | --------- |
| sys_menu        | CREATED/EXISTS | 2         |
| sys_version     | CREATED/EXISTS | 1         |
| imbs_permission | CREATED/EXISTS | 1         |

## 5. API Smoke Results

| Endpoint                    | No Token | Invalid Token | Valid Dev Token | Notes                              |
| --------------------------- | -------- | ------------- | --------------- | ---------------------------------- |
| GET /api/system/menus       | 401      | 401           | 200             | PostgreSQL path passed             |
| GET /api/system/permissions | 401      | 401           | 200             | ORM path passed                    |
| GET /api/system/versions    | 401      | 401           | 200             | Raw SQL did not fail in this smoke |

## 6. Interpretation

* PostgreSQL URI abstraction works in runtime.
* Backend can start using `postgresql+psycopg://`.
* Valid dev JWT passes auth gate and reaches DB-backed business routes.
* System menus, permissions, and versions all reached HTTP 200.
* The previous MySQL connection-refused blocker is resolved by PostgreSQL local smoke.
* No immediate PostgreSQL raw SQL incompatibility was triggered by the three GET endpoints.
* This is smoke-only, not production migration.

## 7. Temporary Artifacts

* Temporary JWT was stored in `/tmp` only.
* Temporary JWT was deleted after smoke.
* Temporary DDL SQL was not committed.
* No `.env` was created.
* No DB password/token was committed.

## 8. Remaining Gaps

* smoke-only DDL is not production schema
* formal Alembic / Flask-Migrate baseline pending
* raw SQL review still required
* permission enforcement pending
* PostgreSQL ORM alignment still pending
* production deployment DB policy pending
