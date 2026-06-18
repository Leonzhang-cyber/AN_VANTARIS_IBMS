# CDE A1 Manifest Rules

1. CDE moduleId must remain `cde`.
2. CDE A1 manifest must align with module-manifest.baseline.json.
3. CDE must not own source business workflows.
4. CDE must not import UFMS runtime source.
5. CDE must not implement Edge/Link runtime.
6. CDE must not redefine global Contracts.
7. CDE must preserve tenantId / projectId / siteId.
8. CDE must preserve messageId / traceId / correlationId.
9. CDE evidence object draft is not DB schema.
10. CDE evidence object draft is not API contract.
11. Runtime implementation requires separate approval.
12. API/DB/menu/RBAC changes require separate approval.
