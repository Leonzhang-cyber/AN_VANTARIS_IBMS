# VANTARIS IBMS PostgreSQL ORM Align 1 Risk Review

## 1. Security Boundary

* no production DB
* no real .env
* no token/password committed
* no seed/migration
* no customer data
* no UFMS content merged

## 2. Risk Reduced

* MySQL-specific raw SQL reduced (`ON DUPLICATE KEY`, `GROUP_CONCAT`)
* JSON error consistency maintained for smoke-verified GET path
* PostgreSQL path protected for menus/permissions/versions read verification

## 3. Remaining Risk

* deeper raw SQL may remain
* production migration not yet established
* write-path behavior requires later dedicated tests
