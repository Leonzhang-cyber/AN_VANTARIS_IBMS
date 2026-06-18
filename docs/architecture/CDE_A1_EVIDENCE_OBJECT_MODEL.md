# UCDE A1 Evidence Object Model

## 1. Core Evidence Object Draft

Document-level draft object (not contracts/schema):

- evidenceId
- evidenceType
- tenantId
- projectId
- siteId
- sourceModule
- sourceObjectType
- sourceObjectId
- messageId
- traceId
- correlationId
- capturedAt
- receivedAt
- createdAt
- evidenceHash, future
- retentionPolicy, future
- custodyStatus, future

## 2. Evidence Types

- alarm_evidence
- event_evidence
- telemetry_snapshot
- work_order_evidence
- inspection_evidence
- esg_report_evidence
- idc_incident_evidence
- audit_event_evidence
- user_action_evidence
- document_reference
- media_reference
- ai_recommendation_evidence_future

## 3. Linkage Rules

- every evidence reference should preserve traceId where available
- every event/alarm derived evidence should preserve messageId
- every cross-module chain should preserve correlationId
- UCDE must not mutate source business record
- UCDE must not become system of record for source business modules

## 4. A1 Boundary

This is not JSON Schema.
This is not DB schema.
This is not API contract.
Only UCDE-A2 may propose evidence contract draft.
