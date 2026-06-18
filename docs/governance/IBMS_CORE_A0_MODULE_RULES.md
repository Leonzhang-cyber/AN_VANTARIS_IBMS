# IBMS Core A0 Module Rules

1. IBMS Core is a VANTARIS ONE business module.
2. IBMS Core must consume Shared Foundation data through approved adapter/contracts.
3. IBMS Core must not implement Edge protocol drivers.
4. IBMS Core must not implement Link ACK/DLQ/retry.
5. IBMS Core must not redefine global Contracts.
6. IBMS Core must not import UFMS backend/runtime source.
7. IBMS Core must preserve tenantId / projectId / siteId.
8. IBMS Core must preserve messageId / traceId / correlationId when displaying shared events.
9. IBMS Core runtime implementation requires separate IBMS-CORE-A1 approval.
10. Any menu/API/DB change requires separate task approval.
