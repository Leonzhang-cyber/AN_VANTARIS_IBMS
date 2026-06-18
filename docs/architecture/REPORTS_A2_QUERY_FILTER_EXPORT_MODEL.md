# REPORTS A2 Query Filter Export Model

## Time range filters

- candidate dimensions: absolute range, relative range, reporting period
- A2 decision: filter model candidate only

## Site/building/floor/zone filters

- candidate dimensions: siteId, buildingId, floorId, zoneId
- A2 decision: location filtering context only

## Module filters

- candidate dimensions: sourceModuleId, moduleCategory, moduleStatus
- A2 decision: module scope candidate only

## Asset/device/point filters

- candidate dimensions: assetId, deviceId, pointId, assetType
- A2 decision: technical filter candidate only

## Severity/status/category filters

- candidate dimensions: severity, status, category, subCategory
- A2 decision: event/state candidate filter only

## Evidence-linked filters

- candidate dimensions: evidenceReferenceId, traceId, correlationId, evidenceType
- A2 decision: evidence-linked candidate filter only

## Aggregation levels

- candidate levels: raw-reference summary, hourly, daily, weekly, monthly, module-level aggregate
- A2 decision: aggregation candidate only

## Export format candidates

- candidate formats: CSV, XLSX, PDF, JSON export package reference
- A2 decision: format candidates only, no export runtime

## Schedule policy candidates

- candidate policies: on-demand, daily, weekly, monthly, threshold-triggered candidate
- A2 decision: schedule candidates only, no scheduler runtime

## Retention class candidates

- candidate classes: short-term operational, compliance retention, audit retention
- A2 decision: retention candidate only, no persistence implementation

## A2 Boundary Declaration

- A2 does not implement filter engine.
- A2 does not implement export.
- A2 does not implement schedule jobs.
