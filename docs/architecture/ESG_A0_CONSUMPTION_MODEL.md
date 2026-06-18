# ESG A0 Consumption Model

Current phase defines ESG consumption model only. It does not create DB mapping, does not modify API, does not add frontend routes, does not implement runtime data services, and does not provide a formal carbon audit certification engine.

## 1) Site / Building / Zone

- Source: IBMS Core operational context and shared location context through ONE adapter
- Contract / adapter dependency: approved shared contracts envelope and ONE adapter boundary
- ESG usage: normalize sustainability aggregation scope by site/building/zone
- Required identity fields: tenantId, projectId, siteId, buildingId, zoneId
- Traceability fields: messageId, traceId, correlationId, observedAt
- Current status: A0 documentation only

## 2) Asset / Device / Point

- Source: shared foundation normalized asset/device/point references
- Contract / adapter dependency: approved asset/device contract objects through adapter
- ESG usage: attribute consumption and impact to equipment-level context
- Required identity fields: tenantId, projectId, siteId, assetId, deviceId, pointId
- Traceability fields: messageId, traceId, correlationId, sourceTimestamp
- Current status: A0 documentation only

## 3) Meter / Utility Point

- Source: shared meter/utility references and adapter-normalized metadata
- Contract / adapter dependency: approved utility meter contract profile through adapter
- ESG usage: utility grouping and meter-level consolidation
- Required identity fields: tenantId, projectId, siteId, meterId, utilityPointId
- Traceability fields: messageId, traceId, correlationId, sampledAt
- Current status: A0 documentation only

## 4) Telemetry summary

- Source: shared foundation telemetry summary output
- Contract / adapter dependency: shared telemetry contract object via ONE adapter
- ESG usage: baseline comparison and trend-level sustainability interpretation
- Required identity fields: tenantId, projectId, siteId, sourceId
- Traceability fields: messageId, traceId, correlationId, eventAt
- Current status: A0 documentation only

## 5) Energy consumption reading

- Source: shared energy readings via telemetry/meter channels
- Contract / adapter dependency: approved energy reading contract through adapter boundary
- ESG usage: electricity consumption rollups and intensity context
- Required identity fields: tenantId, projectId, siteId, meterId, readingId
- Traceability fields: messageId, traceId, correlationId, readingAt
- Current status: A0 documentation only

## 6) Water / Gas / Chilled water reading

- Source: shared utility readings for water/gas/chilled-water channels
- Contract / adapter dependency: approved utility reading contracts via ONE adapter
- ESG usage: multi-utility sustainability view and utility impact decomposition
- Required identity fields: tenantId, projectId, siteId, utilityType, meterId
- Traceability fields: messageId, traceId, correlationId, readingAt
- Current status: A0 documentation only

## 7) Event / Alarm with energy impact

- Source: shared event/alarm outputs from approved boundary
- Contract / adapter dependency: shared event/alarm contract objects through adapter
- ESG usage: classify operational events that affect sustainability KPIs
- Required identity fields: tenantId, projectId, siteId, sourceId, eventIdOrAlarmId
- Traceability fields: messageId, traceId, correlationId, occurredAt
- Current status: A0 documentation only

## 8) Fault Intelligence Output, optional

- Source: UFMS fault intelligence output exposed through approved adapter boundary
- Contract / adapter dependency: optional FI output contract and boundary-approved adapter mapping
- ESG usage: annotate likely cause/effect for energy-impact analysis
- Required identity fields: tenantId, projectId, siteId, intelligenceSourceId
- Traceability fields: messageId, traceId, correlationId, generatedAt
- Current status: optional A0 documentation only

## 9) Maintenance outcome reference

- Source: MMS maintenance outcome references through approved module boundary
- Contract / adapter dependency: approved MMS-to-ESG reference contract/context
- ESG usage: evaluate maintenance-driven change in energy performance
- Required identity fields: tenantId, projectId, siteId, maintenanceRefId
- Traceability fields: messageId, traceId, correlationId, completedAt
- Current status: A0 documentation only

## 10) Evidence reference

- Source: shared evidence and audit references exposed through approved contracts
- Contract / adapter dependency: shared evidence reference contract and adapter boundary
- ESG usage: attach report lineage and evidence pointers without owning chain core
- Required identity fields: tenantId, projectId, siteId, evidenceRefId
- Traceability fields: messageId, traceId, correlationId, referencedAt
- Current status: A0 documentation only

## 11) Carbon factor reference

- Source: approved factor reference datasets through governance boundary
- Contract / adapter dependency: approved factor reference object through adapter/module boundary
- ESG usage: non-certified estimation context for carbon interpretation
- Required identity fields: tenantId, projectId, siteId, factorSetId
- Traceability fields: messageId, traceId, correlationId, factorVersionAt
- Current status: A0 documentation only

## 12) Sustainability KPI

- Source: ESG aggregation over approved readings/events/references
- Contract / adapter dependency: approved upstream contracts and ESG metric boundary
- ESG usage: publish sustainability scorecards and report-readiness context
- Required identity fields: tenantId, projectId, siteId, kpiId
- Traceability fields: messageId, traceId, correlationId, calculatedAt
- Current status: A0 documentation only
