# REPORTS A1 Risk Review

## 1) Report data overexposure risk
- risk level: high
- description: report candidate scope may expose excessive cross-module data.
- mitigation: define reference-only and data-minimization rules in A1 docs.
- A1 decision: controlled.

## 2) Cross-module data leakage risk
- risk level: high
- description: mixed references may blur module boundaries.
- mitigation: enforce source-module reference tagging and governance checks.
- A1 decision: controlled.

## 3) Evidence privacy risk
- risk level: high
- description: evidence-linked report references may include sensitive context.
- mitigation: require privacy classification/redaction review in later gates.
- A1 decision: controlled.

## 4) Export abuse risk
- risk level: medium
- description: future export capability could be abused without controls.
- mitigation: keep export as context-only in A1 and require explicit authorization later.
- A1 decision: controlled.

## 5) Scheduled report delivery risk
- risk level: medium
- description: scheduling semantics may be mistaken for runtime capability.
- mitigation: explicit no scheduler runtime declaration in A1.
- A1 decision: controlled.

## 6) Source-of-record confusion risk
- risk level: medium
- description: reports could be mistaken as source-of-record.
- mitigation: explicit rule that reports consume references only and do not own source records.
- A1 decision: controlled.

## 7) Direct DB access risk
- risk level: high
- description: teams may infer direct DB integration from reporting requirements.
- mitigation: explicit no DB schema/runtime ownership and no DB implementation in A1.
- A1 decision: controlled.

## 8) Permission/RBAC scope creep risk
- risk level: medium
- description: report access-control work may creep into implementation.
- mitigation: keep RBAC out of scope in A1 and require separate authorization.
- A1 decision: controlled.

## 9) Secret/config leakage risk
- risk level: medium
- description: docs may accidentally include credentials.
- mitigation: no secret rule and keyword scanning.
- A1 decision: controlled.

## 10) Premature runtime implementation risk
- risk level: high
- description: docs artifacts may trigger unapproved runtime work.
- mitigation: clear docs-only declaration and readiness flags kept false.
- A1 decision: controlled.

## Overall Conclusion

Reports-A1 risk acceptable only because it is docs-only and manifest-only.
