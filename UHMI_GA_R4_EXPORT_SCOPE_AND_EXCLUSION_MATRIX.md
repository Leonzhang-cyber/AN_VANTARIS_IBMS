# UHMI-GA-R4 Export Scope and Exclusion Matrix

PASS marker: `UHMI_GA_R4_CUSTOMER_PREVIEW_EXPORT_PACKAGE_PASS`

| Item | Status | Notes |
| --- | --- | --- |
| UHMI docs | INCLUDED | R4 hand-off docs and prior evidence references. |
| UHMI registries | INCLUDED | R4 registry and prior registry links. |
| UHMI validators | INCLUDED | R4 validator and prior validator links. |
| Demo flow | INCLUDED | R3 demo flow referenced. |
| Evidence pack | INCLUDED | R2F evidence pack referenced. |
| Customer acceptance checklist | INCLUDED | R4 customer handover and R3 checklist referenced. |
| Engineer runbook | INCLUDED | R4 engineer demo runbook. |
| Frontend source references | REFERENCED | References only; no frontend functionality changed. |
| Backend source references | REFERENCED | References only; no backend functionality changed. |
| Dist/build artifacts | EXCLUDED | No dist/build committed. |
| .env/secrets | EXCLUDED | No .env/secrets committed. |
| Runtime data | EXCLUDED | No Runtime Activation. |
| Device credentials | EXCLUDED | No Direct Device Control. |
| DB migrations | EXCLUDED / NOT EXECUTED | No DB Write. |
| EDGE/LINK commands | EXCLUDED / NOT EXECUTED | No EDGE Command Execution; No LINK Command Execution. |
| Install/rollback scripts | EXCLUDED / NOT EXECUTED | Install/rollback: NOT EXECUTED. |
| Production activation | EXCLUDED / NOT EXECUTED | Production activation: NOT EXECUTED. |

Export package type: `MANIFEST_EVIDENCE_RUNBOOK_ONLY`.

No runnable production package generated. No auth / login / JWT / RBAC mutation. Visual style: `VANTARIS_LIGHT_OPERATIONS_CONSOLE`. UHMI is not HMI Server. UHMI is not SCADA replacement.

`UHMI_GA_R4_CUSTOMER_PREVIEW_EXPORT_PACKAGE_PASS`
