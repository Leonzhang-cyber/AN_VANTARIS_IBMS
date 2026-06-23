# UCDE-GA-R4 Evidence Object Model And Catalog

PASS marker: UCDE_GA_R4_EVIDENCE_CENTER_CUSTOMER_PREVIEW_PASS

## Object Model

The UCDE-GA-R4 Evidence Center Customer Preview uses a static fixture object model only. No Evidence DB is introduced. No DB Write is allowed. No Evidence Write is allowed.

Required evidence fields:

- evidenceId.
- evidenceType.
- title.
- sourceModule.
- linkedWorkspace.
- linkedObjectType.
- linkedObjectId.
- customerVisible.
- engineerVisible.
- integrityStatus.
- timestamp.
- readOnly.
- linkedUhmiPanel.
- linkedReport.
- linkedDeliveryItem.
- guardrailStatus.

## Evidence Types

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

## Catalog Rules

- sourceModule identifies the originating ONE module or release artifact.
- linkedObjectType identifies whether the record points to a workspace, panel, report, validator, checklist, hand-off, or release decision.
- customerVisible records are safe for Customer-readable Evidence Catalog review.
- engineerVisible records are safe for Engineer Trace Context review.
- integrityStatus describes local preview integrity such as STATIC_FIXTURE_VERIFIED.
- readOnly is always true.
- guardrailStatus confirms read-only preview guardrails.

## Static Fixture Boundary

The catalog is static fixture only. It is suitable for local preview, document evidence, and validation evidence, but it is not a runtime evidence store. Runtime activation is NOT EXECUTED. Device control is NOT EXECUTED. EDGE command execution and LINK command execution are NOT EXECUTED. auth / login / JWT / RBAC mutation is NOT EXECUTED.

Future controlled action path:

UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device

This path is NOT EXECUTED in R4.
