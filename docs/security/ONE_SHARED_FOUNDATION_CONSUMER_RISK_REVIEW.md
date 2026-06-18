# ONE Shared Foundation Consumer Risk Review

## 1) ONE continues duplicate Edge development

- description: ONE continues building private Edge runtime path.
- impact: duplicated connector and lifecycle stack.
- control: pause ONE-private Edge runtime tasks; enforce consumer model.
- current status: controlled by governance update.
- next mitigation task: ONE-ADAPTER-A0-SHARED-FOUNDATION-INTERFACE

## 2) ONE continues duplicate Link development

- description: ONE starts private Link ACK/retry/DLQ implementation.
- impact: delivery semantics drift and duplicated operations burden.
- control: SHARED-LINK ownership rule and task pause.
- current status: controlled by governance update.
- next mitigation task: SHARED-LINK governance alignment in UFMS-led roadmap

## 3) ONE redefines Contracts independently

- description: ONE modifies global contracts outside shared process.
- impact: schema/version divergence across products.
- control: treat ONE contracts work as seed/reference pending shared reconciliation.
- current status: controlled by reclassification.
- next mitigation task: SHARED-CONTRACTS-A2-MODULE-PATCH-LICENSE-CDE-SCHEMAS

## 4) UFMS-led foundation becomes incompatible with ONE

- description: shared foundation evolves without ONE consumer compatibility guard.
- impact: adapter break and delayed integration.
- control: adapter contract checkpoints and compatibility review gates.
- current status: open.
- next mitigation task: UFMS-ONE-ADAPTER-CONTRACT-A0

## 5) Adapter boundary unclear

- description: unclear ownership of translation/adaptation layer.
- impact: cross-layer leakage and rework.
- control: define ONE adapter scope and interface ownership explicitly.
- current status: open.
- next mitigation task: ONE-ADAPTER-A0-SHARED-FOUNDATION-INTERFACE

## 6) ONE directly imports UFMS runtime

- description: ONE runtime may attempt direct UFMS runtime coupling.
- impact: boundary contamination and deployment coupling.
- control: adapter/API/contract boundary only; no runtime/source/auth/login/seed/migration copy.
- current status: controlled by policy.
- next mitigation task: boundary checks in adapter design review

## 7) ONE depends on unstable shared foundation draft too early

- description: ONE integration begins before shared assets stabilize.
- impact: frequent breaking changes and integration churn.
- control: stage-gated consumer adoption and version pinning.
- current status: open.
- next mitigation task: shared versioning and compatibility matrix definition

## 8) Shared foundation sales/product ownership unclear

- description: ownership ambiguity between ONE and UFMS teams.
- impact: duplicated planning and delivery conflict.
- control: UFMS-led shared foundation ownership documented and decision-log tracked.
- current status: controlled at governance level.
- next mitigation task: SHARED-FOUNDATION-A1-ROADMAP-RENUMBERING

## 9) Version drift between UFMS-led foundation and ONE consumer

- description: ONE consumes mismatched shared versions.
- impact: runtime incompatibility and incident risk.
- control: contract/API version gates and integration certification checkpoints.
- current status: open.
- next mitigation task: shared release compatibility policy

## 10) Security identity drift

- description: identity/error/status semantics diverge between foundation and consumer modules.
- impact: inconsistent security posture and audit issues.
- control: shared identity/error/status definitions via contracts boundary.
- current status: open.
- next mitigation task: UFMS-ONE-ADAPTER-CONTRACT-A0
