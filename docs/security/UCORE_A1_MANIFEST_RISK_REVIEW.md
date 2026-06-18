# UCORE A1 Manifest Risk Review

## 1) Boundary confusion risk

- risk level: medium
- description: UCore A1 could be misread as runtime implementation approval.
- mitigation: preserve explicit docs-only and manifest-only boundary language.
- A1 decision: accepted with controls.

## 2) Core scope creep risk

- risk level: medium
- description: A1 may drift into command center runtime implementation.
- mitigation: explicitly forbid command center runtime in A1.
- A1 decision: accepted with scope freeze.

## 3) Auth/RBAC implementation risk

- risk level: high
- description: UCore A1 could be used to introduce auth/login/RBAC runtime prematurely.
- mitigation: explicitly ban auth/login/RBAC implementation in A1.
- A1 decision: controlled by rules.

## 4) Direct DB/schema ownership risk

- risk level: high
- description: UCore might be interpreted as DB/schema owner.
- mitigation: enforce no DB/schema rule and keep impact none-in-a1-draft.
- A1 decision: controlled by manifest rules.

## 5) Edge/Link ownership confusion risk

- risk level: high
- description: UCore may be mistaken as owner of foundation runtimes.
- mitigation: reference-only foundation model and forbidden ownership statements.
- A1 decision: controlled by governance.

## 6) Secret/config leakage risk

- risk level: medium
- description: accidental secret or token inclusion in docs.
- mitigation: no-real-secret rule and scan checks.
- A1 decision: controlled in this task.

## 7) Premature runtime implementation risk

- risk level: high
- description: A1 artifacts may be consumed as runtime instructions.
- mitigation: runtimeReady false and no-runtime statements across docs.
- A1 decision: controlled by draft status.

## Overall Conclusion

UCORE-A1 risk acceptable only because it is docs-only and manifest-only.
