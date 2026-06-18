# IDC / DCIM A0 Module Rules

1. IDC / DCIM is a VANTARIS ONE business module.
2. IDC / DCIM owns data center infrastructure operations context.
3. IDC / DCIM must consume Shared Foundation data through ONE adapter/contracts.
4. IDC / DCIM may consume UFMS fault intelligence output only through approved boundary.
5. IDC / DCIM may hand off maintenance context to MMS, but does not own work order lifecycle.
6. IDC / DCIM may provide energy/PUE context to ESG, but does not own ESG carbon reporting.
7. IDC / DCIM may provide evidence reference to CDE, but does not own CDE evidence chain.
8. IDC / DCIM must not import UFMS backend/runtime source.
9. IDC / DCIM must not redefine global Contracts.
10. IDC / DCIM must not implement protocol drivers.
11. IDC / DCIM must preserve tenantId / projectId / siteId.
12. IDC / DCIM must preserve messageId / traceId / correlationId.
13. IDC / DCIM runtime implementation requires separate IDC-DCIM-A1 approval.
14. Any menu/API/DB change requires separate task approval.
