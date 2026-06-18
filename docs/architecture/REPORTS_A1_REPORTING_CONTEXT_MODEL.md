# REPORTS A1 Reporting Context Model

## 1) Operational reports

- reference scope: UCore operational summary and operational KPI references
- A1 decision: context-only definition, no runtime

## 2) UFMS fault / alarm / event reports

- reference scope: UFMS fault/alarm/event standardized references
- A1 decision: reference-only reporting context

## 3) UMMS maintenance reports

- reference scope: work order, SLA, maintenance lifecycle references
- A1 decision: context-only, no scheduling/export runtime

## 4) UESG sustainability reports

- reference scope: sustainability/energy references and aggregated context
- A1 decision: no model implementation, no source mutation

## 5) UCDE evidence-linked reports

- reference scope: evidence linkage and traceability reference context
- A1 decision: evidence-linked reporting context only

## 6) UDOC data operations reports

- reference scope: data operations/capacity/operations references
- A1 decision: docs-level context only

## 7) UConsole module status reports

- reference scope: module readiness/status/dependency references
- A1 decision: reporting context only, no live status API implementation

## 8) Audit / governance reports

- reference scope: governance/audit metadata references
- A1 decision: metadata aggregation context only

## 9) Scheduled report context

- reference scope: schedule policy and recurrence metadata references
- A1 decision: no scheduler runtime implementation in A1

## 10) Export context

- reference scope: export format and export policy metadata references
- A1 decision: no PDF/Excel/export runtime in A1

## Boundary Clarifications

- Reports is not a source-of-record.
- Reports does not modify source module records.
- Reports consumes only references, metadata, and aggregated context semantics.
- Reports A1 does not define real DB schema.
- Reports A1 does not define API contracts.
- Reports A1 does not implement export or schedule runtime.
