# MMS A0 Consumption Model

This phase defines the MMS consumption model only. It does not create DB mapping, does not modify API, does not add frontend routes, and does not implement runtime data services.

## 1) Site / Building / Zone

- Source: IBMS Core operational context and shared foundation normalized location context through ONE adapter
- Contract / adapter dependency: approved shared contracts envelope and ONE adapter boundary
- MMS usage: scope maintenance dispatch, scheduling, and work execution context
- Required identity fields: tenantId, projectId, siteId, buildingId, floorId, zoneId
- Traceability fields: messageId, traceId, correlationId, observedAt
- Current status: A0 documentation only

## 2) Asset / Device / Point

- Source: shared foundation normalized references and IBMS Core business context
- Contract / adapter dependency: approved asset/device contract objects through adapter
- MMS usage: bind work orders, inspections, and preventive tasks to asset hierarchy
- Required identity fields: tenantId, projectId, siteId, assetId, deviceId, pointId
- Traceability fields: messageId, traceId, correlationId, sourceTimestamp
- Current status: A0 documentation only

## 3) Event

- Source: shared foundation event output via ONE adapter
- Contract / adapter dependency: shared event contract object and adapter conversion rules
- MMS usage: triage event-driven maintenance actions and optional work order initiation
- Required identity fields: tenantId, projectId, siteId, sourceId, eventId
- Traceability fields: messageId, traceId, correlationId, eventAt
- Current status: A0 documentation only

## 4) Alarm

- Source: shared foundation alarm output via ONE adapter
- Contract / adapter dependency: shared alarm contract object and approved boundary mapping
- MMS usage: prioritize corrective maintenance and SLA tracking entry points
- Required identity fields: tenantId, projectId, siteId, sourceId, alarmId
- Traceability fields: messageId, traceId, correlationId, raisedAt
- Current status: A0 documentation only

## 5) Fault Intelligence Output, optional

- Source: UFMS fault intelligence output through approved adapter boundary
- Contract / adapter dependency: optional FI output contract and ONE adapter mediation
- MMS usage: enrich triage recommendations for maintenance action planning
- Required identity fields: tenantId, projectId, siteId, intelligenceSourceId
- Traceability fields: messageId, traceId, correlationId, generatedAt
- Current status: optional A0 documentation only

## 6) Work Order

- Source: MMS internal lifecycle context seeded by approved event/alarm/fault inputs
- Contract / adapter dependency: approved input contracts and MMS internal workflow model boundary
- MMS usage: create, assign, execute, complete, and close maintenance tasks
- Required identity fields: tenantId, projectId, siteId, workOrderId
- Traceability fields: messageId, traceId, correlationId, createdAt
- Current status: A0 documentation only

## 7) Inspection Task

- Source: schedule/template-driven MMS planning context
- Contract / adapter dependency: approved schedule/context inputs and MMS workflow boundary
- MMS usage: execute inspection process and capture findings
- Required identity fields: tenantId, projectId, siteId, inspectionTaskId
- Traceability fields: messageId, traceId, correlationId, plannedAt
- Current status: A0 documentation only

## 8) Maintenance Schedule

- Source: asset policy context and planner-defined schedules
- Contract / adapter dependency: approved schedule context references through adapter and module boundary
- MMS usage: preventive maintenance planning and dispatch windows
- Required identity fields: tenantId, projectId, siteId, scheduleId
- Traceability fields: messageId, traceId, correlationId, scheduleAt
- Current status: A0 documentation only

## 9) Spare Part Reference

- Source: approved inventory references and maintenance context
- Contract / adapter dependency: approved reference objects through module boundary
- MMS usage: record material usage context and maintenance completion details
- Required identity fields: tenantId, projectId, siteId, partRefId
- Traceability fields: messageId, traceId, correlationId, usedAt
- Current status: A0 documentation only

## 10) Evidence Reference

- Source: shared evidence/audit references through approved adapter boundary
- Contract / adapter dependency: shared evidence reference contract
- MMS usage: connect maintenance steps and closure to auditable references
- Required identity fields: tenantId, projectId, siteId, evidenceRefId
- Traceability fields: messageId, traceId, correlationId, referencedAt
- Current status: A0 documentation only

## 11) SLA / Response Metrics

- Source: MMS workflow timestamps and approved incoming alarm/event context
- Contract / adapter dependency: shared event/alarm inputs and module-level SLA model boundary
- MMS usage: monitor response/repair performance and maintenance KPIs
- Required identity fields: tenantId, projectId, siteId, slaPolicyId
- Traceability fields: messageId, traceId, correlationId, responseAt
- Current status: A0 documentation only

## 12) Technician / Team Assignment

- Source: MMS planner assignment context and approved organizational references
- Contract / adapter dependency: approved identity and assignment context through module boundary
- MMS usage: dispatch technician/team ownership for work orders and inspections
- Required identity fields: tenantId, projectId, siteId, assignmentId, teamId, technicianId
- Traceability fields: messageId, traceId, correlationId, assignedAt
- Current status: A0 documentation only
