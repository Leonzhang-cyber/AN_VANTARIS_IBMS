# UHMI-GA-R3 Engineer Demo Checklist

PASS marker: `UHMI_GA_R3_CUSTOMER_PREVIEW_PACKAGE_PASS`

| Engineering Check | Required State |
| --- | --- |
| Local branch/HEAD verification | Confirm branch `sync/ufms-foundation-packages-20260622-104646` and R3 baseline `b9e74f09394dee25d3a3b09da729f034431d3cf2`. |
| R3 validator execution | PASS: `python3 scripts/validation/validate-uhmi-ga-r3-customer-preview-package.py`. |
| R2F validator execution | PASS: `python3 scripts/validation/validate-uhmi-ga-r2f-final-readonly-workspace-release-index.py`. |
| R2E/R2D/R2C/R2B/R2A/R1 validator execution | PASS. |
| Package route enforcement | PASS. |
| Boundary baseline | PASS with existing non-blocking legacy warnings only. |
| Frontend build optional | Not executed by R3 because R3 does not change frontend functionality. |
| No dist/build committed | Required. |
| No .env/secrets committed | Required. |
| No runtime activation | Required. |
| No DB migration | Required. |
| No EDGE/LINK command | Required. |
| No production activation | Required. |

Read-only demo guardrails:

- No Direct Device Control.
- No Runtime Activation.
- No DB Write.
- No EDGE Command Execution.
- No LINK Command Execution.
- No auth / login / JWT / RBAC mutation.
- Production Activation Not Executed.

UHMI is not HMI Server. UHMI is not SCADA replacement.

`UHMI_GA_R3_CUSTOMER_PREVIEW_PACKAGE_PASS`
