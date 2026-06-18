# ONE Adapter A2 Module Consumption Flow

## 1. UCore Consumption Flow

- input reference: contracts/edge/link/db references via ONE Adapter boundary
- ONE Adapter role: provide docs-level boundary mapping and dependency semantics
- module usage: core operation context linkage planning
- forbidden shortcut: direct ownership/read/write to foundation runtime or schemas
- future implementation gate: `UCORE-A2-OPERATION-COORDINATION-GATE`

## 2. UMMS Consumption Flow

- input reference: contracts + edge/link status references
- ONE Adapter role: route maintenance-relevant references in docs-level map
- module usage: maintenance linkage planning
- forbidden shortcut: direct edge/link/db integration implementation
- future implementation gate: UMMS business module gate

## 3. UESG Consumption Flow

- input reference: contracts + telemetry/linkage references
- ONE Adapter role: define sustainability consumption boundary
- module usage: sustainability linkage planning
- forbidden shortcut: direct contracts/schema modifications
- future implementation gate: UESG business module gate

## 4. UCDE Consumption Flow

- input reference: contracts + source linkage references
- ONE Adapter role: define evidence linkage intake boundaries
- module usage: evidence reference linkage planning
- forbidden shortcut: direct contracts/schemas promotion without gate
- future implementation gate: `UCDE-A3-FORMAL-CONTRACT-PROMOTION-GATE`

## 5. UDOC Consumption Flow

- input reference: contracts + edge/link/db context references
- ONE Adapter role: define operations-context reference intake boundary
- module usage: operations context planning
- forbidden shortcut: direct foundation runtime ownership
- future implementation gate: UDOC business module gate

## 6. UConsole Consumption Flow

- input reference: readiness/dependency status references
- ONE Adapter role: provide status and dependency boundary references
- module usage: status model planning
- forbidden shortcut: direct backend/frontend implementation
- future implementation gate: `UCONSOLE-A2-MODULE-STATUS-API-GATE`

## 7. Reports / Analytics / Nexus AI Consumer Future Flow

- input reference: module output and readiness references via ONE Adapter boundary
- ONE Adapter role: define future platform consumption boundary
- module usage: future reporting/analytics/AI planning
- forbidden shortcut: direct runtime ingestion implementation
- future implementation gate: respective future platform module gates

## Global Boundary Notes

- business modules must not bypass ONE Adapter to own Foundation references directly.
- business modules must not directly connect to Edge/Link/DB runtime.
- business modules must not modify contracts/schemas.
- future implementation requires explicit gate approval.
