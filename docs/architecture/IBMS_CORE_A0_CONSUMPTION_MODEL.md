# IBMS Core A0 Consumption Model

This stage defines the IBMS Core consumption model only. It does not create DB mapping, does not modify API, does not add frontend routes, and does not implement runtime data services.

## 1) Site / Building / Zone

- Source: shared foundation normalized context objects through ONE adapter
- Contract / adapter dependency: approved shared contracts envelope and ONE adapter boundary
- IBMS Core usage: building operation overview and zone-level operational workspace
- Required identity fields: tenantId, projectId, siteId, buildingId, zoneId
- Traceability fields: messageId, traceId, correlationId, observedAt
- Current status: A0 documentation only

## 2) Asset / Device / Point

- Source: shared foundation normalized asset/device/point references through ONE adapter
- Contract / adapter dependency: approved shared contracts and adapter mapping profile
- IBMS Core usage: asset and device operational view and point-level status context
- Required identity fields: tenantId, projectId, siteId, assetId, deviceId, pointId
- Traceability fields: messageId, traceId, correlationId, sourceTimestamp
- Current status: A0 documentation only

## 3) Telemetry summary

- Source: shared foundation normalized telemetry stream
- Contract / adapter dependency: telemetry object contract through approved adapter
- IBMS Core usage: operational trend summary, dashboard KPIs, and facility context
- Required identity fields: tenantId, projectId, siteId, sourceId
- Traceability fields: messageId, traceId, correlationId, eventAt
- Current status: A0 documentation only

## 4) Event

- Source: shared foundation event outputs
- Contract / adapter dependency: shared event contract via ONE adapter
- IBMS Core usage: event workspace, triage context, and business-level timeline
- Required identity fields: tenantId, projectId, siteId, sourceId, eventId
- Traceability fields: messageId, traceId, correlationId, eventAt
- Current status: A0 documentation only

## 5) Alarm

- Source: shared foundation alarm outputs
- Contract / adapter dependency: shared alarm contract via approved adapter boundary
- IBMS Core usage: alarm business view, severity context, and operator actions
- Required identity fields: tenantId, projectId, siteId, sourceId, alarmId
- Traceability fields: messageId, traceId, correlationId, raisedAt
- Current status: A0 documentation only

## 6) Edge health

- Source: shared foundation edge health output
- Contract / adapter dependency: shared edge health contract and adapter interpretation layer
- IBMS Core usage: system status dashboard and operations visibility
- Required identity fields: tenantId, projectId, siteId, edgeNodeId
- Traceability fields: messageId, traceId, correlationId, observedAt
- Current status: A0 documentation only

## 7) Link delivery state

- Source: shared foundation link delivery state output
- Contract / adapter dependency: shared delivery-state contract via adapter
- IBMS Core usage: integration visibility and delivery confidence in business workspace
- Required identity fields: tenantId, projectId, siteId, routeId
- Traceability fields: messageId, traceId, correlationId, deliveryAt
- Current status: A0 documentation only

## 8) Work order / MMS handoff

- Source: IBMS Core business triggers plus shared events/alarms through adapter
- Contract / adapter dependency: adapter-consumed event/alarm objects and approved handoff contract to MMS
- IBMS Core usage: create or update maintenance handoff context for MMS
- Required identity fields: tenantId, projectId, siteId, workOrderRefId
- Traceability fields: messageId, traceId, correlationId, handoffAt
- Current status: A0 documentation only

## 9) Evidence reference

- Source: shared evidence and audit references exposed through approved boundary
- Contract / adapter dependency: shared evidence/audit reference contract and adapter translation
- IBMS Core usage: link operations context to evidence trace references
- Required identity fields: tenantId, projectId, siteId, evidenceRefId
- Traceability fields: messageId, traceId, correlationId, referencedAt
- Current status: A0 documentation only

## 10) UFMS fault intelligence output, optional

- Source: UFMS fault intelligence output exposed through approved adapter boundary
- Contract / adapter dependency: optional FI output contract via ONE adapter
- IBMS Core usage: assist operations prioritization and business-level decision support
- Required identity fields: tenantId, projectId, siteId, intelligenceSourceId
- Traceability fields: messageId, traceId, correlationId, generatedAt
- Current status: optional A0 documentation only
