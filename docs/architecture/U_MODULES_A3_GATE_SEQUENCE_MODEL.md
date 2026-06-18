# U Modules A3 Gate Sequence Model

## Gate Sequence Table

| Gate ID | Gate Name | Target module | Allowed work | Forbidden work | Required approvals | Dependencies | Output artifacts | Risk level | Recommended order |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G1 | ONE-ADAPTER-A2-FOUNDATION-CONSUMER-GATE | `one-adapter` | consumer-boundary design planning | runtime/API/DB/schema/contracts changes | explicit gate approval | A2 readiness review complete | boundary/interface design plan | high | 1 |
| G2 | UCDE-A3-FORMAL-CONTRACT-PROMOTION-GATE | `ucde` | promotion feasibility planning | contracts/schemas edits, runtime implementation | explicit gate approval + promotion authorization | G1 planning output | promotion criteria + promotion decision plan | high | 2 |
| G3 | UCONSOLE-A2-MODULE-STATUS-API-GATE | `uconsole` | status API design planning | backend/frontend implementation | explicit gate approval | G1 + module status readiness | API design gate plan | medium | 3 |
| G4 | UCORE-A2-OPERATION-COORDINATION-GATE | `ucore` | coordination contract/API design planning | runtime implementation | explicit gate approval | G1, G3 context | coordination design gate plan | medium | 4 |
| G5 | UMMS/UESG/UDOC Business Runtime Gates | `umms`, `uesg`, `udoc` | per-module implementation gate planning | batch runtime implementation | per-module explicit approvals | G1-G4 outcomes | per-module gate decisions and plans | high | 5 |

## Ordering Rationale

- ONE Adapter first because it defines consumer boundary and shared reference path.
- UCDE second because formal evidence contract promotion can affect future schema direction.
- UConsole third because module status API planning depends on stabilized module/readiness metadata.
- UCore and business modules later because they are closer to runtime-facing scope and require prior platform gating.
