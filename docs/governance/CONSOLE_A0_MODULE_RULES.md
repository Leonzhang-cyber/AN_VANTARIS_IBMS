# Console A0 Module Rules

1. Console is a VANTARIS ONE platform control and health view module.
2. Console displays Shared Foundation health but does not own Shared Foundation runtime.
3. Console displays business module status but does not own business logic.
4. Console must consume status through approved adapter/API/contracts.
5. Console must not import UFMS backend/runtime source.
6. Console must not redefine global Contracts.
7. Console must not implement protocol drivers.
8. Console must not implement Link ACK/DLQ/retry.
9. Console must preserve tenantId / projectId / siteId where applicable.
10. Console must preserve traceId / correlationId when displaying integration events.
11. Console runtime implementation requires separate CONSOLE-A1 approval.
12. Any menu/API/DB/RBAC change requires separate task approval.
