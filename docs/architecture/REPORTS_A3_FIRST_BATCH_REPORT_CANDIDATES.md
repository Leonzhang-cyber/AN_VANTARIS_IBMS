# REPORTS A3 First Batch Report Candidates

All entries are docs-level candidates only.
No runtime report implementation is included in A3.

## 1) Fault & Alarm Reports

### UFMS Fault Summary Report
- purpose: summarize fault occurrences and impacts by module/site/time period
- source modules: ufms, ucde, uconsole
- source references: fault references, evidence references, status references
- default filters: timeRange, siteId, severity, status
- aggregation candidates: daily count, severity distribution, escalation trend
- export candidates: view-only, pdf-candidate, csv-candidate
- evidence linkage: required
- A3 decision: candidate-only

### UFMS Alarm/Event Trend Report
- purpose: track alarm and event trends over time windows
- source modules: ufms, ucde
- source references: alarm/event references, evidence references
- default filters: timeRange, category, severity, moduleId
- aggregation candidates: hourly/daily trend, category distribution
- export candidates: view-only, excel-candidate, csv-candidate
- evidence linkage: optional
- A3 decision: candidate-only

### Fault Impact and Escalation Report
- purpose: show impact level and escalation status for major fault clusters
- source modules: ufms, ucore, uconsole
- source references: fault impact references, escalation status references
- default filters: timeRange, impactLevel, status, siteId
- aggregation candidates: impact bucket, escalation delay trend
- export candidates: view-only, pdf-candidate
- evidence linkage: optional
- A3 decision: candidate-only

## 2) Maintenance Reports

### UMMS Work Order Summary Report
- purpose: summarize work order lifecycle and closure metrics
- source modules: umms, ucde
- source references: work order references, evidence references
- default filters: timeRange, status, priority, siteId
- aggregation candidates: completion trend, backlog distribution
- export candidates: view-only, excel-candidate, csv-candidate
- evidence linkage: optional
- A3 decision: candidate-only

### UMMS SLA Compliance Report
- purpose: track SLA fulfillment and breach candidates
- source modules: umms, uconsole
- source references: SLA references, module status references
- default filters: timeRange, slaClass, status, team
- aggregation candidates: compliance rate, breach trend
- export candidates: view-only, pdf-candidate, excel-candidate
- evidence linkage: optional
- A3 decision: candidate-only

### Preventive Maintenance Completion Report
- purpose: monitor preventive maintenance plan completion progress
- source modules: umms
- source references: maintenance plan references, work order references
- default filters: timeRange, assetId, maintenanceType, status
- aggregation candidates: completion ratio, overdue counts
- export candidates: view-only, excel-candidate
- evidence linkage: optional
- A3 decision: candidate-only

## 3) Energy & Sustainability Reports

### UESG Energy Consumption Report
- purpose: summarize energy consumption references by period and site
- source modules: uesg, udoc
- source references: energy references, operations references
- default filters: timeRange, siteId, buildingId, category
- aggregation candidates: period totals, trend line
- export candidates: view-only, excel-candidate, csv-candidate
- evidence linkage: optional
- A3 decision: candidate-only

### UESG Sustainability KPI Report
- purpose: track sustainability KPI candidate indicators
- source modules: uesg, uconsole
- source references: sustainability KPI references, governance status references
- default filters: timeRange, kpiCategory, siteId
- aggregation candidates: KPI score trend, category summary
- export candidates: view-only, pdf-candidate
- evidence linkage: optional
- A3 decision: candidate-only

### Carbon and Utility Trend Report
- purpose: visualize carbon and utility trend candidates
- source modules: uesg, udoc
- source references: carbon references, utility references
- default filters: timeRange, utilityType, siteId
- aggregation candidates: monthly trend, comparative summary
- export candidates: view-only, excel-candidate, csv-candidate
- evidence linkage: optional
- A3 decision: candidate-only

## 4) Evidence & Audit Reports

### UCDE Evidence Traceability Report
- purpose: trace evidence linkage across modules and time ranges
- source modules: ucde, uconsole
- source references: evidence references, module status references
- default filters: timeRange, evidenceReferenceId, moduleId
- aggregation candidates: traceability coverage, link depth summary
- export candidates: view-only, pdf-candidate
- evidence linkage: required
- A3 decision: candidate-only

### Audit Trail Report
- purpose: summarize audit activity references for report-related actions
- source modules: uconsole, ucde
- source references: audit references, action references
- default filters: timeRange, actionType, moduleId
- aggregation candidates: action counts, action trend
- export candidates: view-only, csv-candidate
- evidence linkage: optional
- A3 decision: candidate-only

### Evidence Retention and Redaction Report
- purpose: summarize retention and redaction metadata candidates
- source modules: ucde
- source references: retentionClass references, redaction policy references
- default filters: timeRange, retentionClass, status
- aggregation candidates: retention distribution, redaction summary
- export candidates: view-only, pdf-candidate
- evidence linkage: required
- A3 decision: candidate-only

## 5) Data Operations Reports

### UDOC Data Operations Summary Report
- purpose: summarize data operations readiness and throughput references
- source modules: udoc, ucore
- source references: operations references, module metadata references
- default filters: timeRange, siteId, operationType
- aggregation candidates: operations volume, readiness summary
- export candidates: view-only, excel-candidate
- evidence linkage: optional
- A3 decision: candidate-only

### Capacity and Availability Report
- purpose: show capacity and availability reference trends
- source modules: udoc
- source references: capacity references, availability references
- default filters: timeRange, siteId, buildingId
- aggregation candidates: utilization, availability trend
- export candidates: view-only, pdf-candidate, csv-candidate
- evidence linkage: optional
- A3 decision: candidate-only

### Power Cooling and Environment Report
- purpose: summarize power/cooling/environment reference indicators
- source modules: udoc, uesg
- source references: power references, cooling references, environment references
- default filters: timeRange, zoneId, category
- aggregation candidates: trend and threshold summary
- export candidates: view-only, excel-candidate
- evidence linkage: optional
- A3 decision: candidate-only

## 6) Operations Summary Reports

### UCore Operations Summary Report
- purpose: aggregate cross-domain operations status references
- source modules: ucore, uconsole
- source references: operations references, module status references
- default filters: timeRange, siteId, moduleId
- aggregation candidates: KPI summary, trend summary
- export candidates: view-only, pdf-candidate
- evidence linkage: optional
- A3 decision: candidate-only

### Daily Operations Brief Report
- purpose: produce daily brief candidate from key module references
- source modules: ucore, umms, uesg, udoc
- source references: daily operational references, alerts, maintenance, sustainability
- default filters: date, siteId, moduleId
- aggregation candidates: daily snapshot
- export candidates: view-only, pdf-candidate
- evidence linkage: optional
- A3 decision: candidate-only

### Cross-Module Operational KPI Report
- purpose: compare KPI candidates across multiple modules
- source modules: ucore, umms, uesg, udoc, uconsole
- source references: cross-module KPI references
- default filters: timeRange, moduleId, kpiCategory
- aggregation candidates: module comparison matrix
- export candidates: view-only, excel-candidate, csv-candidate
- evidence linkage: optional
- A3 decision: candidate-only

## 7) Module Status Reports

### Module Readiness Report
- purpose: display module readiness references
- source modules: uconsole
- source references: readiness references, dependency references
- default filters: moduleId, status, timeRange
- aggregation candidates: readiness distribution
- export candidates: view-only, pdf-candidate
- evidence linkage: optional
- A3 decision: candidate-only

### Module Health and Dependency Report
- purpose: show module health/dependency relationship references
- source modules: uconsole
- source references: health references, dependency references
- default filters: moduleId, dependencyType, status
- aggregation candidates: dependency risk summary
- export candidates: view-only, csv-candidate
- evidence linkage: optional
- A3 decision: candidate-only

### Roadmap and Governance Status Report
- purpose: summarize roadmap and governance status references
- source modules: uconsole, governance
- source references: roadmap references, governance status references
- default filters: phase, status, moduleId
- aggregation candidates: phase completion summary
- export candidates: view-only, pdf-candidate
- evidence linkage: optional
- A3 decision: candidate-only

## 8) Governance & Compliance Reports

### Governance Decision Log Report
- purpose: summarize governance decisions and status references
- source modules: governance, uconsole
- source references: decision log references, status references
- default filters: timeRange, domain, decisionType
- aggregation candidates: decision volume and status summary
- export candidates: view-only, pdf-candidate
- evidence linkage: optional
- A3 decision: candidate-only

### Compliance Evidence Summary Report
- purpose: summarize compliance evidence-linked references
- source modules: ucde, governance
- source references: evidence references, compliance references
- default filters: timeRange, complianceDomain, moduleId
- aggregation candidates: compliance coverage summary
- export candidates: view-only, excel-candidate
- evidence linkage: required
- A3 decision: candidate-only

### Security Risk Review Report
- purpose: summarize security risk review references
- source modules: governance, uconsole
- source references: security risk references, mitigation status references
- default filters: riskLevel, status, timeRange
- aggregation candidates: risk distribution and trend
- export candidates: view-only, pdf-candidate
- evidence linkage: optional
- A3 decision: candidate-only
