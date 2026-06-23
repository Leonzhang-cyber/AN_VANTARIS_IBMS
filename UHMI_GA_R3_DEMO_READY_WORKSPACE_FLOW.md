# UHMI-GA-R3 Demo-ready Read-only Workspace Flow

PASS marker: `UHMI_GA_R3_CUSTOMER_PREVIEW_PACKAGE_PASS`

All demo steps are read-only, view-only, and demo-only. Production Activation Not Executed. No Direct Device Control. No Runtime Activation. No DB Write. No EDGE Command Execution. No LINK Command Execution. No auth / login / JWT / RBAC mutation.

| Step | Demo Action | Read-only Evidence |
| --- | --- | --- |
| 1 | Open UConsole | View-only entry point; no login or auth mutation. |
| 2 | Open UHMI Workspace | View-only UConsole-owned workspace. |
| 3 | Show `VANTARIS_LIGHT_OPERATIONS_CONSOLE` visual style | Demo-ready Read-only Workspace visual evidence. |
| 4 | Show Overview metric cards | View-only static/read-model context. |
| 5 | Show System Context Panels | View-only system context. |
| 6 | Show Device Context Table | View-only device status; no direct device control. |
| 7 | Show Mimic Panel Preview | View-only preview; no command surface. |
| 8 | Show Event Context | View-only event context. |
| 9 | Show Evidence Context | View-only evidence context. |
| 10 | Show Role-based views | View-only role context; no RBAC mutation. |
| 11 | Show Customer view | View-only customer context. |
| 12 | Show Engineer view | View-only engineer context. |
| 13 | Show Admin view | View-only admin context; no real permission write. |
| 14 | Show Operator view | View-only operator context. |
| 15 | Show Disabled Actions | Demo-only disabled/future-only explanation. |
| 16 | Show Guardrails | Read-only safety guardrails. |
| 17 | Show Future Control Path | Documentation-only future path. |
| 18 | Show R2F Evidence Pack / Release Index | View-only evidence chain. |

Future control path, not executed in R3:

`UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device`

UHMI is not HMI Server. UHMI is not SCADA replacement.

`UHMI_GA_R3_CUSTOMER_PREVIEW_PACKAGE_PASS`
