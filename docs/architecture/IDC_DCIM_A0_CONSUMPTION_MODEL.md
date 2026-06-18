# IDC / DCIM A0 Consumption Model

Current phase defines IDC / DCIM consumption model only. It does not create DB mapping, does not modify API, does not add frontend routes, and does not implement runtime data services.

## 1) Data Center / Room / Hall / Zone

- Source: IBMS Core location context and shared foundation normalized context through ONE adapter
- Contract / adapter dependency: approved shared contracts envelope and ONE adapter boundary
- IDC / DCIM usage: establish data-center spatial operating scope
- Required identity fields: tenantId, projectId, siteId, dataCenterId, roomId, hallId, zoneId
- Traceability fields: messageId, traceId, correlationId, observedAt
- Current status: A0 documentation only

## 2) Row / Rack / Cabinet / U-space

- Source: data-center topology references via approved adapter boundary
- Contract / adapter dependency: approved topology contract references through ONE adapter
- IDC / DCIM usage: rack/cabinet/U-space operational capacity and placement views
- Required identity fields: tenantId, projectId, siteId, rowId, rackId, cabinetId, uSpaceRefId
- Traceability fields: messageId, traceId, correlationId, updatedAt
- Current status: A0 documentation only

## 3) Server / Network / Storage Asset

- Source: shared asset references and module-approved placement context
- Contract / adapter dependency: approved asset/device contract objects and adapter normalization
- IDC / DCIM usage: map IT assets to rack/room context for capacity and risk views
- Required identity fields: tenantId, projectId, siteId, assetId, assetType
- Traceability fields: messageId, traceId, correlationId, sourceTimestamp
- Current status: A0 documentation only

## 4) UPS / PDU / RPP / Rack PDU

- Source: shared telemetry/object references for power distribution chain
- Contract / adapter dependency: approved power-chain contracts through ONE adapter
- IDC / DCIM usage: power hierarchy monitoring and chain risk context
- Required identity fields: tenantId, projectId, siteId, upsId, pduId, rppId, rackPduId
- Traceability fields: messageId, traceId, correlationId, sampledAt
- Current status: A0 documentation only

## 5) Cooling Equipment / CRAH / CRAC / In-row Cooling

- Source: shared equipment and telemetry references through approved boundary
- Contract / adapter dependency: approved cooling equipment contracts and adapter mapping
- IDC / DCIM usage: cooling chain operation and thermal capacity context
- Required identity fields: tenantId, projectId, siteId, coolingUnitId, coolingUnitType
- Traceability fields: messageId, traceId, correlationId, sampledAt
- Current status: A0 documentation only

## 6) Temperature / Humidity / Airflow telemetry

- Source: shared environmental telemetry stream
- Contract / adapter dependency: approved telemetry contracts via ONE adapter
- IDC / DCIM usage: thermal/humidity risk and airflow condition visibility
- Required identity fields: tenantId, projectId, siteId, sensorId, zoneId
- Traceability fields: messageId, traceId, correlationId, eventAt
- Current status: A0 documentation only

## 7) Power telemetry / load / capacity

- Source: shared power telemetry channels
- Contract / adapter dependency: approved power telemetry contracts and adapter validation
- IDC / DCIM usage: load tracking, capacity headroom, and overload risk context
- Required identity fields: tenantId, projectId, siteId, powerNodeId
- Traceability fields: messageId, traceId, correlationId, eventAt
- Current status: A0 documentation only

## 8) Cooling telemetry / thermal capacity

- Source: shared cooling telemetry channels
- Contract / adapter dependency: approved cooling telemetry contracts through adapter
- IDC / DCIM usage: cooling capacity, efficiency context, and thermal risk monitoring
- Required identity fields: tenantId, projectId, siteId, coolingNodeId
- Traceability fields: messageId, traceId, correlationId, eventAt
- Current status: A0 documentation only

## 9) Event / Alarm

- Source: shared foundation event/alarm outputs via ONE adapter
- Contract / adapter dependency: approved shared event/alarm contract objects
- IDC / DCIM usage: incident triage and availability impact context
- Required identity fields: tenantId, projectId, siteId, sourceId, eventIdOrAlarmId
- Traceability fields: messageId, traceId, correlationId, occurredAt
- Current status: A0 documentation only

## 10) Edge Health

- Source: shared foundation edge health output
- Contract / adapter dependency: shared edge health contract via approved adapter boundary
- IDC / DCIM usage: upstream data-source reliability context for incident interpretation
- Required identity fields: tenantId, projectId, siteId, edgeNodeId
- Traceability fields: messageId, traceId, correlationId, observedAt
- Current status: A0 documentation only

## 11) Link Delivery State

- Source: shared foundation link delivery state output
- Contract / adapter dependency: shared link delivery state contract via adapter
- IDC / DCIM usage: delivery confidence and data freshness context
- Required identity fields: tenantId, projectId, siteId, routeId
- Traceability fields: messageId, traceId, correlationId, deliveryAt
- Current status: A0 documentation only

## 12) Fault Intelligence Output, optional

- Source: UFMS fault intelligence output through approved adapter boundary
- Contract / adapter dependency: optional FI output contract and adapter mediation
- IDC / DCIM usage: enrich incident risk summary and RCA context for operators
- Required identity fields: tenantId, projectId, siteId, intelligenceSourceId
- Traceability fields: messageId, traceId, correlationId, generatedAt
- Current status: optional A0 documentation only

## 13) Work Order / MMS Handoff

- Source: IDC / DCIM incident and maintenance context routed to MMS boundary
- Contract / adapter dependency: approved module-boundary handoff contract references
- IDC / DCIM usage: trigger and track maintenance handoff references
- Required identity fields: tenantId, projectId, siteId, workOrderRefId
- Traceability fields: messageId, traceId, correlationId, handoffAt
- Current status: A0 documentation only

## 14) Energy / ESG Handoff

- Source: IDC / DCIM energy/power/cooling context for ESG boundary consumption
- Contract / adapter dependency: approved handoff references through adapter/module boundary
- IDC / DCIM usage: provide energy/PUE and efficiency context to ESG
- Required identity fields: tenantId, projectId, siteId, handoffRefId
- Traceability fields: messageId, traceId, correlationId, handoffAt
- Current status: A0 documentation only

## 15) Evidence Reference

- Source: shared evidence/audit references exposed by approved contracts
- Contract / adapter dependency: shared evidence reference contract and adapter boundary
- IDC / DCIM usage: attach incident/capacity viewpoints to auditable references
- Required identity fields: tenantId, projectId, siteId, evidenceRefId
- Traceability fields: messageId, traceId, correlationId, referencedAt
- Current status: A0 documentation only

## 16) SLA / Availability / Incident Metrics

- Source: module-level aggregation over approved event/alarm/health inputs
- Contract / adapter dependency: approved upstream contracts and IDC/DCIM metric boundary
- IDC / DCIM usage: uptime/SLA/incidence reporting context
- Required identity fields: tenantId, projectId, siteId, metricId
- Traceability fields: messageId, traceId, correlationId, calculatedAt
- Current status: A0 documentation only
