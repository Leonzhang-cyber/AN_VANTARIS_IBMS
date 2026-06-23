# UHMI-GA-R5 Risk Limitation Exclusion Matrix

PASS marker: `UHMI_GA_R5_FINAL_CUSTOMER_PREVIEW_READINESS_DECISION_PASS`

| Item | Classification | Notes |
| --- | --- | --- |
| Existing boundary legacy warnings | NON_BLOCKING_FOR_CUSTOMER_PREVIEW | Boundary baseline PASS; warnings are existing non-blocking legacy warnings. |
| Frontend build warnings from R2E/R2D | NON_BLOCKING | R2E/R2D build evidence remains referenced; R5 does not change frontend functionality. |
| Production activation not executed | INTENTIONAL | Production Activation: NOT EXECUTED. |
| DB migration not executed | INTENTIONAL | No DB Write. |
| Runtime control not executed | INTENTIONAL | No Runtime Activation. |
| EDGE/LINK command not executed | INTENTIONAL | No EDGE Command Execution; No LINK Command Execution. |
| Auth/RBAC mutation not executed | INTENTIONAL | No auth / login / JWT / RBAC mutation. |
| No real device connectivity | INTENTIONAL | No Direct Device Control. |
| No runnable production package | INTENTIONAL | No runnable production package. |
| No dist/build committed | INTENTIONAL | No dist/build committed. |

## Customer Preview Risks

- Customer may confuse customer preview GO with production GA. Mitigation: decision scope is `READ_ONLY_CUSTOMER_PREVIEW_OFFLINE_DEMO_HANDOFF`.
- Customer may interpret disabled/future-only controls as active. Mitigation: all controls remain documentation-only and require future policy gates.

## Demo Limitations

- Demo is read-only.
- Demo is view-only.
- Demo is not a production install.
- Demo does not execute device, DB, EDGE, LINK, runtime, auth, login, JWT, or RBAC actions.

## Future Production Prerequisites

- production activation plan
- deployment environment verification
- DB migration plan
- runtime control policy gate
- approval workflow
- EDGE/LINK execution guard
- security acceptance
- customer UAT

Visual style: `VANTARIS_LIGHT_OPERATIONS_CONSOLE`. UHMI is not HMI Server. UHMI is not SCADA replacement.

`UHMI_GA_R5_FINAL_CUSTOMER_PREVIEW_READINESS_DECISION_PASS`
