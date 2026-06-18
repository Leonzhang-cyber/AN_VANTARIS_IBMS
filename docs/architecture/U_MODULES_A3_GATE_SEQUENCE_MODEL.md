# U Modules A3 Gate Sequence Model

## Gate Sequence Table

| Gate ID | Gate Name | Target module | Allowed work | Forbidden work | Required approvals | Dependencies | Output artifacts | Risk level | Recommended order |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G1 | EDGE-FLEET-A1-CONSUMPTION-MODEL-DRAFT | `edge-fleet-consumption-model` | direct-consumption topology planning | runtime/API/DB/schema/contracts changes | explicit gate approval | one-adapter cancellation decision | edge-fleet/link direct consumption model plan | high | 1 |
| G1-H | ONE-ADAPTER-A2-FOUNDATION-CONSUMER-GATE (cancelled/superseded) | `one-adapter` | historical record only | any continued implementation path | not applicable | superseded by cancellation decision | historical reference only | high | historical |
| G2 | UCDE-A3-FORMAL-CONTRACT-PROMOTION-GATE (deferred in active sequence) | `ucde` | promotion feasibility planning | contracts/schemas edits, runtime implementation | explicit gate approval + promotion authorization | G1 planning output | promotion criteria + promotion decision plan | high | 2 |
| G3 | UCONSOLE-A2-MODULE-STATUS-API-GATE (deferred in active sequence) | `uconsole` | status API design planning | backend/frontend implementation | explicit gate approval | G1 + module status readiness | API design gate plan | medium | 3 |
| G4 | UCORE-A2-OPERATION-COORDINATION-GATE (deferred in active sequence) | `ucore` | coordination contract/API design planning | runtime implementation | explicit gate approval | G1, G3 context | coordination design gate plan | medium | 4 |
| G5 | UMMS/UESG/UDOC Business Runtime Gates (deferred in active sequence) | `umms`, `uesg`, `udoc` | per-module implementation gate planning | batch runtime implementation | per-module explicit approvals | G1-G4 outcomes | per-module gate decisions and plans | high | 5 |

## Ordering Rationale

- ONE Adapter gate is cancelled/superseded and retained as historical record only.
- EDGE Fleet direct consumption model is now first because ingress and secure delivery boundaries must be stabilized first.
- UCDE second because formal evidence contract promotion can affect future schema direction.
- UConsole third because module status API planning depends on stabilized module/readiness metadata.
- UCore and business modules later because they are closer to runtime-facing scope and require prior platform gating.
