# REPORTS A2 Data Model Candidates

These are docs-level candidate objects only.
They are not DB schema, not DTO, and not JSON Schema.

## 1) ReportCatalogItem

- purpose: represent catalog-level report candidate metadata
- candidate fields: reportId, reportName, reportCategory, sourceModuleId, status, versionCandidate, tags, updatedAt
- source module references: UCore, UMMS, UESG, UCDE, UDOC, UConsole
- ownership: Reports catalog context
- A2 decision: candidate-only, no implementation

## 2) ReportDefinition

- purpose: represent report definition candidate metadata
- candidate fields: reportId, definitionVersion, metricCandidates, dimensionCandidates, filterCandidates, aggregationCandidates
- source module references: standardized module reference metadata
- ownership: Reports definition planning context
- A2 decision: candidate-only, no implementation

## 3) ReportQueryContext

- purpose: represent query request context candidate
- candidate fields: tenantId, projectId, siteId, reportId, timeRange, filterSetId, aggregationLevel, requestId, traceId
- source module references: module reference and governance metadata
- ownership: Reports query planning context
- A2 decision: candidate-only, no runtime query engine

## 4) ReportFilterSet

- purpose: represent filter set candidate
- candidate fields: moduleFilter, siteFilter, assetFilter, severityFilter, statusFilter, categoryFilter, evidenceLinkedFilter
- source module references: cross-module filter metadata references
- ownership: Reports filter planning context
- A2 decision: candidate-only, no filter engine

## 5) ReportDataReference

- purpose: represent standardized data reference candidate
- candidate fields: sourceModuleId, sourceReferenceId, evidenceReferenceId, timestamp, measureCandidate, qualityStatus
- source module references: UCore/UMMS/UESG/UCDE/UDOC/UConsole references
- ownership: Reports reference consumption context
- A2 decision: candidate-only, no data pipeline implementation

## 6) ReportExportRequest

- purpose: represent export request candidate
- candidate fields: exportRequestId, reportId, filterSetId, formatCandidate, requestedBy, requestedAt, statusCandidate
- source module references: report definition/filter references
- ownership: Reports export planning context
- A2 decision: candidate-only, no export runtime

## 7) ReportSchedulePolicy

- purpose: represent schedule policy candidate
- candidate fields: schedulePolicyId, frequencyCandidate, timeWindow, timezone, triggerCondition, recipientGroupCandidate
- source module references: governance schedule policy references
- ownership: Reports scheduling planning context
- A2 decision: candidate-only, no scheduler runtime

## 8) ReportPermissionContext

- purpose: represent permission boundary candidate
- candidate fields: subjectId, roleCandidate, moduleScope, reportScope, actionCandidate, decisionHint
- source module references: governance and module metadata references
- ownership: Reports access governance planning context
- A2 decision: candidate-only, no RBAC runtime

## 9) ReportAuditReference

- purpose: represent audit trace candidate for report interactions
- candidate fields: auditRefId, actionType, reportId, actorRef, traceId, occurredAt, policyRef
- source module references: audit and governance references
- ownership: Reports audit planning context
- A2 decision: candidate-only, no audit runtime pipeline
