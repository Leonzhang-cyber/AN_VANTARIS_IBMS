# CDE A0 Module Rules

1. CDE is a VANTARIS ONE evidence and traceability business module.
2. CDE owns evidence reference and traceability context, not business workflow.
3. CDE must consume Shared Foundation data through ONE adapter/contracts.
4. CDE may consume UFMS fault intelligence evidence only through approved boundary.
5. CDE may consume MMS / ESG / IDC / IBMS Core evidence references through approved module boundaries.
6. CDE must not import UFMS backend/runtime source.
7. CDE must not redefine global Contracts.
8. CDE must not implement protocol drivers.
9. CDE must preserve tenantId / projectId / siteId.
10. CDE must preserve messageId / traceId / correlationId.
11. CDE runtime implementation requires separate CDE-A1 approval.
12. Any menu/API/DB change requires separate task approval.
