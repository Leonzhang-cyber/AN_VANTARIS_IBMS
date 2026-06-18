# CDE A1 Manifest Rules

1. UCDE moduleId must remain `ucde`.
2. UCDE A1 manifest must align with module-manifest.baseline.json.
3. UCDE must not own source business workflows.
4. UCDE must not import UFMS runtime source.
5. UCDE must not implement Edge/Link runtime.
6. UCDE must not redefine global Contracts.
7. UCDE must preserve tenantId / projectId / siteId.
8. UCDE must preserve messageId / traceId / correlationId.
9. UCDE evidence object draft is not DB schema.
10. UCDE evidence object draft is not API contract.
11. Runtime implementation requires separate approval.
12. API/DB/menu/RBAC changes require separate approval.
