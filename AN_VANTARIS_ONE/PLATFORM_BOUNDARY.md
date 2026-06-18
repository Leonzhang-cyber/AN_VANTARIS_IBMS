# VANTARIS ONE Platform Boundary (A5)

## 1. Skeleton boundary

- no runtime source copied
- no backend/frontend migration in A5
- no DB migration in A5
- no Edge/Link runtime implementation in A5

## 2. Allowed future migration source

- `AN_VANTARIS_IBMS-backend` -> `AN_VANTARIS_Code` / `ibms-core` after A6+
- `AN_VANTARIS_IBMS-frontend` -> `AN_VANTARIS_Console` / module UI after A6+
- `AN_VANTARIS_IBMS-backend/src/Iot/drivers` -> `AN_VANTARIS_EDGE` protocol plugins after EDGE source audit
- `contracts` -> `AN_VANTARIS_Contracts` after Contracts A0/A1
- DB/migration -> `AN_VANTARIS_DB` after DB schema baseline

## 3. Forbidden boundaries

- no UFMS runtime/source/schema/auth/login/seed/migration copy
- no direct DB writes from Edge
- no business logic inside Link
- no NexusAI direct business DB mutation
- no Console direct business DB bypass
- no global rename IBMS to ONE
