# REPORTS A3 Report Metadata Model

This model is docs-level candidate metadata only.
It is not DB schema and not DTO.

## 1) Identity metadata
- field candidates: reportId, reportCode, reportName, reportVersionCandidate
- purpose: uniquely identify report candidates
- risk note: identifier collision across groups
- future validation needed: naming/version governance check
- A3 decision: candidate-only

## 2) Grouping metadata
- field candidates: reportGroupId, reportGroupName, reportCategory, moduleDomain
- purpose: classify catalog candidates by logical group
- risk note: ambiguous group boundaries
- future validation needed: governance taxonomy validation
- A3 decision: candidate-only

## 3) Source reference metadata
- field candidates: sourceModules, sourceReferences, sourceScope, sourceFreshnessCandidate
- purpose: define source boundaries for each report candidate
- risk note: cross-module leakage and source-of-record confusion
- future validation needed: source boundary and ownership validation
- A3 decision: candidate-only

## 4) Filter metadata
- field candidates: defaultFilters, supportedFilters, filterValidationHints
- purpose: define candidate filter behavior and constraints
- risk note: excessive filtering scope may leak sensitive context
- future validation needed: filter scope and sensitivity review
- A3 decision: candidate-only

## 5) Aggregation metadata
- field candidates: aggregationLevelCandidates, groupingDimensions, summaryMetricsCandidates
- purpose: define aggregation semantics for report candidates
- risk note: over-aggregation may hide important trace context
- future validation needed: aggregation correctness review
- A3 decision: candidate-only

## 6) Export metadata
- field candidates: exportFormatCandidates, exportScope, exportPolicyHint
- purpose: define export options as planning candidates
- risk note: export misuse and data overexposure
- future validation needed: export authorization and data minimization review
- A3 decision: candidate-only

## 7) Schedule metadata
- field candidates: scheduleEligible, schedulePolicyCandidates, deliveryWindowCandidates
- purpose: define scheduling eligibility as planning candidates
- risk note: schedule leakage and unauthorized delivery assumptions
- future validation needed: schedule policy and delivery control review
- A3 decision: candidate-only

## 8) Permission metadata
- field candidates: permissionScope, roleCandidate, accessLevelCandidate
- purpose: define access boundary candidates
- risk note: RBAC ambiguity without explicit policy
- future validation needed: security governance approval
- A3 decision: candidate-only

## 9) Audit metadata
- field candidates: auditRequired, auditEventCandidates, auditRetentionHint
- purpose: define audit-trace expectations for report usage
- risk note: incomplete audit trace coverage
- future validation needed: audit completeness validation
- A3 decision: candidate-only

## 10) Evidence linkage metadata
- field candidates: evidenceLinked, evidenceReferenceCandidates, traceabilityHint
- purpose: define evidence-linked reporting boundary candidates
- risk note: privacy leakage from evidence references
- future validation needed: privacy and redaction review
- A3 decision: candidate-only

## 11) Retention metadata
- field candidates: retentionClass, retentionWindowCandidate, retentionPolicyHint
- purpose: define retention candidate semantics
- risk note: retention-policy mismatch with compliance needs
- future validation needed: compliance and retention approval
- A3 decision: candidate-only
