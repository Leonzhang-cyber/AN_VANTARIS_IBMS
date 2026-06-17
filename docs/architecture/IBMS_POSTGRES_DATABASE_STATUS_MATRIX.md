# VANTARIS IBMS PostgreSQL Database Status Matrix

| Layer                           | Status      | Notes                                           |
| ------------------------------- | ----------- | ----------------------------------------------- |
| Runtime PostgreSQL connectivity | PASS        | local-smoke verified                            |
| System config minimal tables    | PASS        | sys_menu/sys_version/imbs_permission smoke only |
| Formal migration framework      | PENDING     | Alembic/Flask-Migrate not yet established       |
| Production schema baseline      | PENDING     | target schema pending                           |
| Raw SQL portability             | IN PROGRESS | menu_api.py risk remains                        |
| Permission enforcement DB path  | PENDING     | 403 verification pending                        |
| Full IBMS domain schema         | PENDING     | MMS/ESG/Asset/Integration/Audit/AI pending      |
