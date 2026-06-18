# REPORTS A2 API Data Risk Review

## 1) Report API overexposure risk
- risk level: high
- description: future API candidates may expose excessive cross-module data context.
- mitigation: enforce candidate-level data minimization and approval gate before implementation.
- A2 decision: controlled.

## 2) Cross-module data leakage risk
- risk level: high
- description: combined report views may blur module boundaries and leak scoped data.
- mitigation: module-scoped source references and filter boundaries in candidate model.
- A2 decision: controlled.

## 3) UFMS fault data sensitivity risk
- risk level: high
- description: UFMS fault/alarm/event references may contain sensitive operational context.
- mitigation: sensitivity classification and explicit approval prior to runtime access.
- A2 decision: controlled.

## 4) UCDE evidence privacy risk
- risk level: high
- description: evidence-linked reporting may expose privacy-sensitive metadata.
- mitigation: evidence filter boundary and privacy/redaction review in later gate.
- A2 decision: controlled.

## 5) Export abuse risk
- risk level: medium
- description: export candidate definitions may be interpreted as active export capability.
- mitigation: explicit no export runtime declaration and separate authorization requirement.
- A2 decision: controlled.

## 6) Scheduled delivery leakage risk
- risk level: medium
- description: schedule candidates may be misused as real delivery workflows.
- mitigation: explicit no schedule runtime declaration and scheduling authorization gate.
- A2 decision: controlled.

## 7) Permission/RBAC ambiguity risk
- risk level: medium
- description: permission candidates may be interpreted as implemented RBAC.
- mitigation: define permission context as candidate-only and require security approval.
- A2 decision: controlled.

## 8) Direct DB query risk
- risk level: high
- description: API/data planning could drift into direct DB query implementation.
- mitigation: explicit DB non-scope and no schema/no query runtime rule.
- A2 decision: controlled.

## 9) Report template injection risk
- risk level: medium
- description: future template/runtime assumptions could introduce injection risks.
- mitigation: keep template behavior out of scope and assess security in later implementation gate.
- A2 decision: controlled.

## 10) Premature backend/frontend implementation risk
- risk level: high
- description: gate outputs may trigger unauthorized backend/frontend work.
- mitigation: enforce docs-only gate constraint and readiness/authorization false checks.
- A2 decision: controlled.

## Overall Conclusion

Reports A2 is acceptable only as API/data model gate. Implementation remains blocked.
