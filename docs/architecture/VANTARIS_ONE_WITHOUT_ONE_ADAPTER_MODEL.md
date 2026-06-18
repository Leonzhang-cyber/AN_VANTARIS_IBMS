# VANTARIS ONE Without ONE Adapter Model

## 1. Before Model

External -> EDGE/LINK -> ONE Adapter -> Business Modules

## 2. After Model

External -> EDGE Fleet -> LINK -> Shared Foundation outputs -> VANTARIS ONE modules

No ONE Adapter in primary topology.

## 3. Ingress Model

All external ingress enters through EDGE Fleet instances.
VANTARIS ONE business modules do not directly connect to external systems.

## 4. Delivery Model

LINK is the secure delivery layer for envelope delivery, ACK, retry, DLQ, route policy, delivery audit, and message trace.

## 5. Consumption Model

VANTARIS ONE modules consume standardized outputs, status, evidence, event references, and metadata.
UConsole, Reports, Analytics, and Nexus AI consume standardized results rather than direct external ingress.

## 6. Module Boundary

- UCore / UMMS / UFMS / UESG / UCDE / UDOC do not directly connect to external systems.
- UCDE owns evidence identity and business traceability context.
- UConsole owns module readiness/status/dependency display.

## 7. Platform Boundary

Platform layer focuses on status/reporting/analytics/shared AI service and governance metadata; no middleware-style ONE Adapter remains.

## 8. Foundation Boundary

Shared Foundation remains Contracts/EDGE/LINK/DB and is not modified by this task.

## 9. Nexus AI Note

Nexus AI is a shared AI service that serves all core modules, including UFMS.

## 10. Non-scope

- no runtime implementation
- no API route implementation
- no DB/schema implementation
- no contracts/schemas repository modifications
