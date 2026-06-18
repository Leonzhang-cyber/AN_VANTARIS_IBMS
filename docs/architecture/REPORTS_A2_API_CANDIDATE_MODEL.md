# REPORTS A2 API Candidate Model

This document defines future API candidates only.
It is not OpenAPI and does not create backend routes/controllers/services.

## 1) Report catalog query candidate

- purpose: query report catalog candidates by module/category/type
- candidate input: tenant/project/site/module/category/search/page/sort
- candidate output: report catalog item list and pagination metadata
- source references: report catalog candidate metadata, module status references
- forbidden A2 implementation: no API route/controller/service
- future approval required: backend API design authorization

## 2) Report definition candidate

- purpose: resolve report definition metadata for selected candidate
- candidate input: reportId/reportType/moduleId/version candidate
- candidate output: definition metadata, field candidates, constraints candidates
- source references: report definition candidate metadata
- forbidden A2 implementation: no backend definition runtime
- future approval required: data model and API approval

## 3) Report data query candidate

- purpose: query standardized report data references across modules
- candidate input: reportId/timeRange/filterSet/aggregationLevel
- candidate output: aggregated reference data set and summary metadata
- source references: UCore/UMMS/UESG/UCDE/UDOC/UConsole standardized references
- forbidden A2 implementation: no runtime query engine
- future approval required: backend API + data access authorization

## 4) Report filter candidate

- purpose: define filter candidate contract for report queries
- candidate input: module/site/asset/severity/status/category/evidence-linked filters
- candidate output: normalized filter metadata and validation candidates
- source references: query/filter metadata candidates
- forbidden A2 implementation: no filter engine implementation
- future approval required: API/data model authorization

## 5) Report export request candidate

- purpose: define future export request boundary candidate
- candidate input: reportId/filterSet/exportFormat/deliveryOption
- candidate output: export request metadata and status reference
- source references: export policy and report context references
- forbidden A2 implementation: no export runtime implementation
- future approval required: export runtime authorization

## 6) Scheduled report candidate

- purpose: define scheduled reporting request boundary candidate
- candidate input: schedulePolicy/reportId/filterSet/deliveryWindow
- candidate output: schedule metadata and schedule status reference
- source references: schedule policy references and governance constraints
- forbidden A2 implementation: no scheduled job runtime
- future approval required: scheduling runtime authorization

## 7) Report permission candidate

- purpose: define access-control boundary candidate for report usage
- candidate input: subject/moduleScope/reportScope/action
- candidate output: permission evaluation metadata candidate
- source references: governance status and module metadata references
- forbidden A2 implementation: no RBAC runtime implementation
- future approval required: security and governance authorization

## 8) Report audit candidate

- purpose: define audit trace candidate for report query/export/schedule actions
- candidate input: action/reportId/subject/time/context
- candidate output: audit reference metadata candidate
- source references: audit references and module status metadata
- forbidden A2 implementation: no audit runtime pipeline
- future approval required: audit implementation authorization

## A2 Constraint

A2 does not create real API route/controller/service/OpenAPI.
