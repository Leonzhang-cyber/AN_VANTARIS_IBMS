# ONE Adapter A1 Consumer Rules

1. ONE Adapter is a platform consumer boundary module.
2. ONE Adapter does not own `AN_VANTARIS_EDGE` runtime.
3. ONE Adapter does not own `AN_VANTARIS_LINK` runtime.
4. ONE Adapter does not own `AN_VANTARIS_DB` runtime or schema.
5. ONE Adapter does not own `AN_VANTARIS_Contracts` schema ownership.
6. ONE Adapter does not modify `contracts/` or `schemas/`.
7. ONE Adapter does not create backend runtime or frontend runtime.
8. ONE Adapter does not create API routes, DB tables, or migrations.
9. ONE Adapter does not implement auth/login/RBAC runtime.
10. ONE Adapter does not include real secret/token/credential content.
11. Foundation dependencies remain reference-only.
12. A1 output remains docs-only contract draft and non-executable.
