# UCDE-GA-R4 UHMI Evidence Linkage Spec

PASS marker: UCDE_GA_R4_EVIDENCE_CENTER_CUSTOMER_PREVIEW_PASS

## UHMI Release Chain

UCDE-GA-R4 links the completed UHMI R1-R6 read-only customer preview chain into UCDE Evidence Center:

- UHMI-GA-R1: read-only UConsole / UHMI Workspace foundation.
- UHMI-GA-R2A: full UConsole menu IA and UI/API skeleton.
- UHMI-GA-R2B: workspace panels and system context.
- UHMI-GA-R2C: role-based workspace views.
- UHMI-GA-R2D: light console visual polish.
- UHMI-GA-R2E: workspace API and frontend integration audit.
- UHMI-GA-R2F: final read-only workspace release index.
- UHMI-GA-R3: customer preview package.
- UHMI-GA-R4: customer preview export package and offline hand-off.
- UHMI-GA-R5: customer preview release decision.
- UHMI-GA-R6: customer preview final archive.

## Linkage Model

UHMI Evidence Context -> UCDE Evidence Center is a read-only evidence relationship. UCDE presents the evidence record, link target, source module, linked workspace area, and guardrail status. UHMI remains a read-only workspace and UCDE remains evidence context.

Linked workspace areas:

- UHMI Overview.
- System Context Panels.
- Device Context Table.
- Mimic Panel Preview.
- Event Context.
- Evidence Context.
- Role-based Views.
- Guardrails.
- Future Control Path.
- Customer Preview Package.
- Offline Demo Hand-off.
- Final Release Decision.

Linked evidence types:

- UHMI_WORKSPACE_EVIDENCE.
- SYSTEM_CONTEXT_EVIDENCE.
- DEVICE_CONTEXT_EVIDENCE.
- EVENT_CONTEXT_EVIDENCE.
- CUSTOMER_PREVIEW_EVIDENCE.
- RELEASE_INDEX_EVIDENCE.
- VALIDATOR_RESULT_EVIDENCE.
- ACCEPTANCE_CHECKLIST_EVIDENCE.
- OFFLINE_DEMO_HANDOFF_EVIDENCE.
- RELEASE_DECISION_EVIDENCE.

## Visibility Rules

- customerVisible means the evidence can be shown in customer preview language.
- engineerVisible means the evidence includes trace context useful for implementation review.
- Evidence records may be both customerVisible and engineerVisible.
- Integrity status is descriptive and local to the frozen evidence object model.
- Read-only linkage means no evidence write, no DB write, and no runtime activation.

## Guardrails

- No Evidence Write.
- No DB Write.
- No Runtime Activation.
- No Direct Device Control.
- No EDGE Command Execution.
- No LINK Command Execution.
- No auth / login / JWT / RBAC mutation.

Future controlled action path:

UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device

This path is NOT EXECUTED in R4.
