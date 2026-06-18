# Console A0 Shared Foundation Health View

## 1. Purpose

Console is the VANTARIS ONE platform console and health-view entry point for Shared Foundation, ONE Adapter, business modules, platform configuration, and operations status.
Console does not own Edge/Link/Contracts runtime and does not replace business modules.

## 2. Console Owns

- platform module status view
- Shared Foundation health view
- ONE Adapter health view
- business module enablement view
- license / feature visibility context, future
- user / role / permission administration context, future
- audit visibility context
- integration status overview
- deployment mode visibility
- package/version visibility
- operational health dashboard
- configuration governance entry, future
- patch/version governance entry, future

## 3. Console Does Not Own

- Edge protocol drivers
- Edge connector registry runtime
- Link ACK / DLQ / retry runtime
- global Contracts schema
- UFMS runtime
- UFMS RCA / correlation engine
- IBMS Core operations business logic
- MMS work order lifecycle
- ESG calculation model
- IDC/DCIM capacity/PUE model
- CDE evidence chain core
- NexusAI model runtime
- DB schema ownership outside approved module boundary

## 4. Relationship With Shared Foundation

Console may display:

- Shared EDGE health
- Shared LINK delivery state
- Shared Contracts version
- connector status summary
- machine identity status summary, future
- audit/evidence status summary

through ONE Adapter and approved APIs/contracts.

## 5. Relationship With Business Modules

Console displays module enablement and health status for:

- IBMS Core
- MMS
- ESG
- IDC/DCIM
- CDE
- Reports
- Analytics
- ONE Adapter

But each business module owns its own business logic.

## 6. Relationship With UFMS

Console may display UFMS integration status and fault intelligence feed health through approved boundary.
Console must not import UFMS runtime source.
