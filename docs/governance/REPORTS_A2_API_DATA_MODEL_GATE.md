# REPORTS A2 API Data Model Gate

## 1. A2 Objective

Define Reports API/data model candidate boundaries at docs level without implementing API, data schema, or runtime.

## 2. A1 Reviewed Baseline

- Reports A1 module manifest draft completed
- Reports identity and boundary baseline confirmed (`Reporting Workspace` / `报表工作台`)
- all readiness flags remain false

## 3. Non-scope

- backend API implementation
- frontend page implementation
- DB schema/table implementation
- OpenAPI/JSON Schema implementation
- report engine implementation
- export runtime implementation
- scheduled job runtime implementation

## 4. API Data Model Gate Purpose

Provide a controlled decision gate for future API candidates, data model candidates, query/filter model, export boundary, schedule boundary, and permission boundary.

## 5. Allowed Work

- docs-level API candidate definitions
- docs-level data model candidate definitions
- docs-level query/filter/export/schedule boundary definitions
- docs-level validation and risk gate definitions

## 6. Forbidden Work

- creating real API routes/controllers/services
- creating DB schema or migration artifacts
- creating OpenAPI/JSON Schema artifacts
- implementing report/export/schedule runtime behavior

## 7. Future Approval Requirements

- explicit approval before backend API implementation
- explicit approval before data model/DB implementation
- explicit approval before frontend exposure
- explicit approval before export/schedule runtime implementation

## 8. Entry Criteria

- A1 module manifest baseline complete
- boundary guard and forbidden-path constraints in effect
- no active readiness/authorization true states

## 9. Exit Criteria

- API candidate model documented
- data model candidates documented
- query/filter/export/schedule boundary model documented
- risk review and decision log documented
- next gate task documented

## 10. Decision Matrix

- pass gate (docs-level): proceed to A3 report catalog spec draft
- hold gate: fill missing API/data candidate definitions
- reject gate: keep planning blocked and re-run boundary/risk review

## 11. Next Recommended Task

`REPORTS-A3-REPORT-CATALOG-SPEC-DRAFT`

## 12. A2 Declaration

REPORTS-A2 is a gate only. It does not create backend API, frontend page, DB schema, OpenAPI, JSON Schema, export runtime, scheduled report runtime, or report engine.

Reports API/data model design is not implemented in A2.
