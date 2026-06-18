# MMS A0 Module Rules

1. MMS is a VANTARIS ONE business module.
2. MMS owns maintenance workflow, not Edge/Link/Contracts.
3. MMS must consume Shared Foundation data through ONE adapter/contracts.
4. MMS may consume UFMS fault intelligence output only through approved boundary.
5. MMS must not import UFMS backend/runtime source.
6. MMS must not redefine global Contracts.
7. MMS must not implement protocol drivers.
8. MMS must preserve tenantId / projectId / siteId.
9. MMS must preserve messageId / traceId / correlationId when converting events to work orders.
10. MMS runtime implementation requires separate MMS-A1 approval.
11. Any menu/API/DB change requires separate task approval.
