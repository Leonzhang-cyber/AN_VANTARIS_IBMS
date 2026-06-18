# CDE A0 Evidence Traceability Model

## 1. Core Traceability Fields

- tenantId
- projectId
- siteId
- messageId
- traceId
- correlationId
- sourceSystemId
- gatewayId
- connectorId
- assetCode / assetUid
- deviceCode / deviceUid
- pointCode / pointUid
- evidenceId
- evidenceType
- evidenceHash, future
- createdAt
- capturedAt
- receivedAt

## 2. Evidence Linkage

Shared Foundation object  
-> ONE Adapter  
-> Business Module context  
-> CDE evidence reference  
-> Report / Audit / Export context

## 3. Cross-module Evidence Examples

- alarm -> UFMS fault output -> MMS work order -> CDE closure evidence
- meter telemetry -> ESG KPI -> CDE report evidence
- UPS alarm -> IDC incident view -> MMS work order -> CDE incident package
- user action -> audit event -> CDE audit reference
- AI recommendation -> human decision -> CDE decision evidence, future

## 4. A0 Boundary

A0 does not create evidence DB.
A0 does not implement hash chain.
A0 does not implement external audit export.
A0 does not modify API/frontend.
