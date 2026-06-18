# CDE A0 Consumption Model

Current phase defines CDE consumption model only. It does not create DB mapping, does not modify API, does not add frontend routes, does not implement runtime evidence service, and does not implement a formal immutable chain or blockchain anchoring.

## 1) Evidence Reference

- Source: shared foundation and module-level evidence references via ONE adapter
- Contract / adapter dependency: approved evidence reference contract through adapter boundary
- CDE usage: normalize evidence pointer records and index across modules
- Required identity fields: tenantId, projectId, siteId, evidenceId, evidenceType
- Traceability fields: messageId, traceId, correlationId, capturedAt
- Current status: A0 documentation only

## 2) Audit Event

- Source: shared audit stream and module-generated audit references
- Contract / adapter dependency: approved audit event contract via ONE adapter
- CDE usage: build audit linkage context for traceability views
- Required identity fields: tenantId, projectId, siteId, actorId, auditEventId
- Traceability fields: messageId, traceId, correlationId, createdAt
- Current status: A0 documentation only

## 3) Event / Alarm Reference

- Source: shared foundation event/alarm outputs through adapter boundary
- Contract / adapter dependency: approved event/alarm contracts via ONE adapter
- CDE usage: associate operational incidents with evidence records
- Required identity fields: tenantId, projectId, siteId, sourceId, eventIdOrAlarmId
- Traceability fields: messageId, traceId, correlationId, occurredAt
- Current status: A0 documentation only

## 4) Telemetry Snapshot Reference

- Source: shared telemetry outputs and selected module snapshot references
- Contract / adapter dependency: approved telemetry contracts through ONE adapter
- CDE usage: store snapshot pointers for investigation and reporting traceability
- Required identity fields: tenantId, projectId, siteId, snapshotRefId
- Traceability fields: messageId, traceId, correlationId, capturedAt
- Current status: A0 documentation only

## 5) Edge Health Evidence

- Source: shared edge health output
- Contract / adapter dependency: approved edge health contract through adapter
- CDE usage: link health posture to incident and evidence package context
- Required identity fields: tenantId, projectId, siteId, edgeNodeId
- Traceability fields: messageId, traceId, correlationId, observedAt
- Current status: A0 documentation only

## 6) Link Delivery Evidence

- Source: shared link delivery state output
- Contract / adapter dependency: approved link delivery contract via adapter
- CDE usage: preserve delivery-state evidence for audit and report completeness checks
- Required identity fields: tenantId, projectId, siteId, routeId
- Traceability fields: messageId, traceId, correlationId, deliveryAt
- Current status: A0 documentation only

## 7) UFMS Fault Intelligence Evidence, optional

- Source: UFMS fault intelligence output through approved adapter boundary
- Contract / adapter dependency: optional FI output contract and adapter mediation
- CDE usage: reference fault intelligence evidence in cross-module chains
- Required identity fields: tenantId, projectId, siteId, intelligenceSourceId
- Traceability fields: messageId, traceId, correlationId, generatedAt
- Current status: optional A0 documentation only

## 8) MMS Work Order Evidence

- Source: MMS work order and maintenance history evidence references
- Contract / adapter dependency: approved MMS evidence/handoff boundary contracts
- CDE usage: link maintenance lifecycle evidence to incidents and outcomes
- Required identity fields: tenantId, projectId, siteId, workOrderIdOrRef
- Traceability fields: messageId, traceId, correlationId, completedAt
- Current status: A0 documentation only

## 9) Inspection Evidence

- Source: MMS inspection task evidence references
- Contract / adapter dependency: approved inspection evidence references via module boundary
- CDE usage: capture field-inspection traceability for audits and closures
- Required identity fields: tenantId, projectId, siteId, inspectionTaskId
- Traceability fields: messageId, traceId, correlationId, inspectedAt
- Current status: A0 documentation only

## 10) ESG Report / Meter Evidence

- Source: ESG report references, meter evidence pointers, KPI evidence references
- Contract / adapter dependency: approved ESG evidence boundary objects
- CDE usage: connect sustainability outputs with upstream evidence references
- Required identity fields: tenantId, projectId, siteId, esgReportRefId
- Traceability fields: messageId, traceId, correlationId, reportedAt
- Current status: A0 documentation only

## 11) IDC/DCIM Incident / Capacity / PUE Evidence

- Source: IDC/DCIM incident and capacity-energy evidence references
- Contract / adapter dependency: approved IDC/DCIM evidence boundary references
- CDE usage: build data-center incident and capacity evidence packages
- Required identity fields: tenantId, projectId, siteId, dcimEvidenceRefId
- Traceability fields: messageId, traceId, correlationId, referencedAt
- Current status: A0 documentation only

## 12) NexusAI Recommendation Evidence, future

- Source: future AI recommendation references through approved module boundary
- Contract / adapter dependency: future approved recommendation evidence contract
- CDE usage: retain recommendation-to-decision trace references
- Required identity fields: tenantId, projectId, siteId, recommendationRefId
- Traceability fields: messageId, traceId, correlationId, generatedAt
- Current status: future scope only

## 13) User Action Evidence

- Source: approved user action audit references
- Contract / adapter dependency: approved action audit contracts through boundaries
- CDE usage: preserve human action lineage in evidence chains
- Required identity fields: tenantId, projectId, siteId, actorId, actionRefId
- Traceability fields: messageId, traceId, correlationId, actedAt
- Current status: A0 documentation only

## 14) Configuration Change Evidence

- Source: approved configuration-change audit references
- Contract / adapter dependency: approved config-change contracts/references
- CDE usage: tie system-change context to incident and compliance evidence
- Required identity fields: tenantId, projectId, siteId, configChangeRefId
- Traceability fields: messageId, traceId, correlationId, changedAt
- Current status: A0 documentation only

## 15) Attachment / Media / Document Reference

- Source: module-level attachment metadata references through approved boundaries
- Contract / adapter dependency: approved attachment/document reference contract
- CDE usage: maintain document/media references without owning storage runtime
- Required identity fields: tenantId, projectId, siteId, attachmentRefId
- Traceability fields: messageId, traceId, correlationId, attachedAt
- Current status: A0 documentation only

## 16) External Audit Package, future

- Source: future export context from approved module evidence references
- Contract / adapter dependency: future approved audit package contract
- CDE usage: aggregate evidence references for external audit packaging
- Required identity fields: tenantId, projectId, siteId, auditPackageRefId
- Traceability fields: messageId, traceId, correlationId, packagedAt
- Current status: future scope only
