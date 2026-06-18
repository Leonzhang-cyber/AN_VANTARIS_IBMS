# ONE Adapter A0 Data Consumption Model

This document defines the VANTARIS ONE consumption model for shared foundation data. The current stage defines consumption structure only and does not create database mapping, does not modify API routes, and does not implement runtime adapters.

## 1) Telemetry

- source: UFMS-led Shared EDGE via Shared LINK envelope
- contract dependency: shared telemetry contract object in shared contracts envelope
- ONE target module: IBMS Core, Analytics, Console
- required identity fields: tenantId, projectId, siteId, sourceId
- traceability fields: messageId, traceId, correlationId, eventAt
- current status: A0 model definition only

## 2) Event

- source: UFMS-led Shared EDGE/UFMS-led Shared LINK
- contract dependency: shared event contract object
- ONE target module: IBMS Core, Reports, Console
- required identity fields: tenantId, projectId, siteId, sourceId
- traceability fields: messageId, traceId, correlationId, eventAt
- current status: A0 model definition only

## 3) Alarm

- source: UFMS-led Shared EDGE and/or UFMS-led Shared LINK
- contract dependency: shared alarm contract object
- ONE target module: IBMS Core, MMS, Console
- required identity fields: tenantId, projectId, siteId, sourceId, alarmId
- traceability fields: messageId, traceId, correlationId, raisedAt
- current status: A0 model definition only

## 4) Edge Health

- source: UFMS-led Shared EDGE health output
- contract dependency: shared edge health contract object
- ONE target module: Console, Analytics
- required identity fields: tenantId, projectId, siteId, edgeNodeId
- traceability fields: messageId, traceId, correlationId, observedAt
- current status: A0 model definition only

## 5) Link Delivery State

- source: UFMS-led Shared LINK delivery pipeline
- contract dependency: shared link state/ack/delivery contract object
- ONE target module: Console, Reports
- required identity fields: tenantId, projectId, siteId, routeId
- traceability fields: messageId, traceId, correlationId, deliveryAt
- current status: A0 model definition only

## 6) Evidence

- source: shared evidence objects emitted through shared contracts boundary
- contract dependency: shared evidence contract object
- ONE target module: CDE, IBMS Core, Reports
- required identity fields: tenantId, projectId, siteId, evidenceId
- traceability fields: messageId, traceId, correlationId, collectedAt
- current status: A0 model definition only

## 7) Audit

- source: shared foundation integration/audit stream
- contract dependency: shared audit contract object
- ONE target module: CDE, Console, Reports
- required identity fields: tenantId, projectId, siteId, actorId
- traceability fields: messageId, traceId, correlationId, auditAt
- current status: A0 model definition only

## 8) Fault Intelligence Output from UFMS, optional

- source: UFMS fault intelligence output exposed via approved adapter boundary
- contract dependency: optional shared fault intelligence output contract
- ONE target module: IBMS Core, MMS, ESG, Analytics, Console
- required identity fields: tenantId, projectId, siteId, intelligenceSourceId
- traceability fields: messageId, traceId, correlationId, generatedAt
- current status: optional A0 model definition only

## Target Module Coverage

The current model covers these ONE target modules:

- IBMS Core
- MMS
- ESG
- CDE
- Reports
- Console
- Analytics

Current phase is consumption-model documentation only; database mapping, API changes, and runtime adapter implementation remain out of scope.
