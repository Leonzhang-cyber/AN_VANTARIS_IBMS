# UCDE A3 Promotion Risk Review

## 1) Premature contract creation risk

- risk level: high
- description: teams may interpret A3 gate as permission to create formal contracts.
- mitigation: explicit gate-only declaration and promotionExecuted false controls.
- A3 decision: controlled.

## 2) Schemas boundary breach risk

- risk level: high
- description: planning outputs may drift into `schemas/` changes.
- mitigation: schema boundary statements and boundary check enforcement.
- A3 decision: controlled.

## 3) Contracts package pollution risk

- risk level: high
- description: docs work may accidentally create package-level contract artifacts.
- mitigation: no-formal-artifact rule and explicit prohibited paths.
- A3 decision: controlled.

## 4) Evidence immutability overclaim risk

- risk level: medium
- description: immutability may be overclaimed without formal policy review.
- mitigation: treat immutability semantics as draft references only.
- A3 decision: controlled.

## 5) Source-of-record conflict risk

- risk level: high
- description: producer ownership could conflict across modules and foundation references.
- mitigation: defer final ownership resolution to A4 planning artifact.
- A3 decision: controlled.

## 6) Privacy/redaction insufficiency risk

- risk level: medium
- description: redaction/privacy requirements may be incomplete for future formalization.
- mitigation: require retention/redaction readiness planning in A4.
- A3 decision: controlled.

## 7) Retention policy ambiguity risk

- risk level: medium
- description: unclear retention classes may cause future contract inconsistency.
- mitigation: define retention boundary matrix in A4.
- A3 decision: controlled.

## 8) Cross-module data leakage risk

- risk level: high
- description: broad evidence linkage could leak context across modules.
- mitigation: enforce linkage boundary model and module obligation review.
- A3 decision: controlled.

## 9) Backend DTO/API creep risk

- risk level: high
- description: promotion planning may accidentally trigger DTO/API design implementation.
- mitigation: explicit no-DTO/no-API implementation gate controls.
- A3 decision: controlled.

## 10) Edge/Link/DB access confusion risk

- risk level: high
- description: teams may assume direct access to Edge/Link/DB runtime from UCDE scope.
- mitigation: restate shared-foundation non-ownership and adapter-boundary-only model.
- A3 decision: controlled.

## 11) Rollback complexity risk

- risk level: medium
- description: unclear rollback rules can complicate reversal when boundaries are breached.
- mitigation: enforce docs-only rollback requirement to last approved gate baseline.
- A3 decision: controlled.

## Overall Conclusion

UCDE-A3 acceptable only as promotion gate. Formal contract creation remains blocked.
