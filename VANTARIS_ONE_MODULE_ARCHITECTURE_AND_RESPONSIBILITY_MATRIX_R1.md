# VANTARIS ONE Module Architecture And Responsibility Matrix R1

VANTARIS ONE is a cross-industry unified operations platform. It is not an airport-only system; airport is one projection over shared platform layers.

This matrix states responsibility, allowed actions, forbidden actions, current status, gap to GA, and next task ID. It is intentionally conservative: no module is marked full GA unless current branch evidence supports that claim.

## UCode / CODE Layer (UCODE)

- Purpose: backend API, execution boundary, integration API.
- Owner layer: CODE API execution layer.
- Inputs: contract envelopes, role context, package entitlement state, source-system or module records relevant to UCode / CODE Layer.
- Outputs: validated API responses, events, evidence records, readiness state, reports, or handoff envelopes.
- Allowed actions: read approved data, validate contracts, publish read-only projections, produce audit/evidence artifacts, and request approved workflow transitions through CODE.
- Forbidden actions: bypass CODE, directly control devices from UConsole or NEXUS AI, activate runtime without approval, run DB migrations without approval, create secrets, or mutate foundation package content during design work.
- Current status: Freeze required.
- Gap to GA: final module-specific capability audit, UConsole entry alignment, security/route validation, acceptance evidence, and customer activation plan as applicable.
- Next recommended task ID: UCODE-GA-R1 CODE Layer Final API/Execution Boundary Freeze.
## UMMS (UMMS)

- Purpose: maintenance/facility management, asset/service workflows.
- Owner layer: Domain module.
- Inputs: contract envelopes, role context, package entitlement state, source-system or module records relevant to UMMS.
- Outputs: validated API responses, events, evidence records, readiness state, reports, or handoff envelopes.
- Allowed actions: read approved data, validate contracts, publish read-only projections, produce audit/evidence artifacts, and request approved workflow transitions through CODE.
- Forbidden actions: bypass CODE, directly control devices from UConsole or NEXUS AI, activate runtime without approval, run DB migrations without approval, create secrets, or mutate foundation package content during design work.
- Current status: Freeze/read-only capability complete; final module GA freeze required.
- Gap to GA: final module-specific capability audit, UConsole entry alignment, security/route validation, acceptance evidence, and customer activation plan as applicable.
- Next recommended task ID: UMMS-GA-R1 Final Module Consolidated Freeze.
## UFMS (UFMS)

- Purpose: unified fault/event management, alarm/event correlation.
- Owner layer: Domain module.
- Inputs: contract envelopes, role context, package entitlement state, source-system or module records relevant to UFMS.
- Outputs: validated API responses, events, evidence records, readiness state, reports, or handoff envelopes.
- Allowed actions: read approved data, validate contracts, publish read-only projections, produce audit/evidence artifacts, and request approved workflow transitions through CODE.
- Forbidden actions: bypass CODE, directly control devices from UConsole or NEXUS AI, activate runtime without approval, run DB migrations without approval, create secrets, or mutate foundation package content during design work.
- Current status: Foundation/projection evidence present; final full-product GA evidence required.
- Gap to GA: final module-specific capability audit, UConsole entry alignment, security/route validation, acceptance evidence, and customer activation plan as applicable.
- Next recommended task ID: UCONSOLE-GA-R1 Full Module Entry & Menu Consistency Freeze.
## UESG (UESG)

- Purpose: energy, sustainability, compliance evidence.
- Owner layer: Domain module.
- Inputs: contract envelopes, role context, package entitlement state, source-system or module records relevant to UESG.
- Outputs: validated API responses, events, evidence records, readiness state, reports, or handoff envelopes.
- Allowed actions: read approved data, validate contracts, publish read-only projections, produce audit/evidence artifacts, and request approved workflow transitions through CODE.
- Forbidden actions: bypass CODE, directly control devices from UConsole or NEXUS AI, activate runtime without approval, run DB migrations without approval, create secrets, or mutate foundation package content during design work.
- Current status: Freeze/read-only capability complete; final module GA freeze required.
- Gap to GA: final module-specific capability audit, UConsole entry alignment, security/route validation, acceptance evidence, and customer activation plan as applicable.
- Next recommended task ID: UESG-GA-R1 Final Module Consolidated Freeze.
## UCDE (UCDE)

- Purpose: decision/evidence/traceability, read-only evidence chain.
- Owner layer: Domain module.
- Inputs: contract envelopes, role context, package entitlement state, source-system or module records relevant to UCDE.
- Outputs: validated API responses, events, evidence records, readiness state, reports, or handoff envelopes.
- Allowed actions: read approved data, validate contracts, publish read-only projections, produce audit/evidence artifacts, and request approved workflow transitions through CODE.
- Forbidden actions: bypass CODE, directly control devices from UConsole or NEXUS AI, activate runtime without approval, run DB migrations without approval, create secrets, or mutate foundation package content during design work.
- Current status: Freeze/read-only capability complete; final capability audit required.
- Gap to GA: final module-specific capability audit, UConsole entry alignment, security/route validation, acceptance evidence, and customer activation plan as applicable.
- Next recommended task ID: UCDE-GA-R1 Final Capability Audit + Consolidated Freeze.
## UDOC (UDOC)

- Purpose: document, handover, manuals, evidence documents.
- Owner layer: Domain module.
- Inputs: contract envelopes, role context, package entitlement state, source-system or module records relevant to UDOC.
- Outputs: validated API responses, events, evidence records, readiness state, reports, or handoff envelopes.
- Allowed actions: read approved data, validate contracts, publish read-only projections, produce audit/evidence artifacts, and request approved workflow transitions through CODE.
- Forbidden actions: bypass CODE, directly control devices from UConsole or NEXUS AI, activate runtime without approval, run DB migrations without approval, create secrets, or mutate foundation package content during design work.
- Current status: Incomplete/not confirmed by final GA-specific evidence.
- Gap to GA: final module-specific capability audit, UConsole entry alignment, security/route validation, acceptance evidence, and customer activation plan as applicable.
- Next recommended task ID: UDOC-GA-R1 Document & Evidence Package Skeleton.
## Automated Rules & Policy (AUTOMATED_RULES_POLICY)

- Purpose: rule evaluation, thresholds, SLA, policy guardrails.
- Owner layer: Policy layer.
- Inputs: contract envelopes, role context, package entitlement state, source-system or module records relevant to Automated Rules & Policy.
- Outputs: validated API responses, events, evidence records, readiness state, reports, or handoff envelopes.
- Allowed actions: read approved data, validate contracts, publish read-only projections, produce audit/evidence artifacts, and request approved workflow transitions through CODE.
- Forbidden actions: bypass CODE, directly control devices from UConsole or NEXUS AI, activate runtime without approval, run DB migrations without approval, create secrets, or mutate foundation package content during design work.
- Current status: Freeze required before GA.
- Gap to GA: final module-specific capability audit, UConsole entry alignment, security/route validation, acceptance evidence, and customer activation plan as applicable.
- Next recommended task ID: GOVERNANCE-SECURITY-GA-R1 Final Governance & Security Freeze.
## ONE Orchestrator (ONE_ORCHESTRATOR)

- Purpose: workflow coordination, escalation, package orchestration.
- Owner layer: Coordination layer.
- Inputs: contract envelopes, role context, package entitlement state, source-system or module records relevant to ONE Orchestrator.
- Outputs: validated API responses, events, evidence records, readiness state, reports, or handoff envelopes.
- Allowed actions: read approved data, validate contracts, publish read-only projections, produce audit/evidence artifacts, and request approved workflow transitions through CODE.
- Forbidden actions: bypass CODE, directly control devices from UConsole or NEXUS AI, activate runtime without approval, run DB migrations without approval, create secrets, or mutate foundation package content during design work.
- Current status: Scaffold/current branch integration not confirmed.
- Gap to GA: final module-specific capability audit, UConsole entry alignment, security/route validation, acceptance evidence, and customer activation plan as applicable.
- Next recommended task ID: ONE-ORCH-GA-R1 Orchestrator Read-only Workflow Freeze.
## UConsole (UCONSOLE)

- Purpose: operator/engineer/admin/customer control surface.
- Owner layer: Presentation layer.
- Inputs: contract envelopes, role context, package entitlement state, source-system or module records relevant to UConsole.
- Outputs: validated API responses, events, evidence records, readiness state, reports, or handoff envelopes.
- Allowed actions: read approved data, validate contracts, publish read-only projections, produce audit/evidence artifacts, and request approved workflow transitions through CODE.
- Forbidden actions: bypass CODE, directly control devices from UConsole or NEXUS AI, activate runtime without approval, run DB migrations without approval, create secrets, or mutate foundation package content during design work.
- Current status: Freeze/read-only capability complete; unified entry consistency required.
- Gap to GA: final module-specific capability audit, UConsole entry alignment, security/route validation, acceptance evidence, and customer activation plan as applicable.
- Next recommended task ID: UCONSOLE-GA-R1 Full Module Entry & Menu Consistency Freeze.
## Reports & Analytics (REPORTS_ANALYTICS)

- Purpose: dashboards, exports, trend reports.
- Owner layer: Analytics layer.
- Inputs: contract envelopes, role context, package entitlement state, source-system or module records relevant to Reports & Analytics.
- Outputs: validated API responses, events, evidence records, readiness state, reports, or handoff envelopes.
- Allowed actions: read approved data, validate contracts, publish read-only projections, produce audit/evidence artifacts, and request approved workflow transitions through CODE.
- Forbidden actions: bypass CODE, directly control devices from UConsole or NEXUS AI, activate runtime without approval, run DB migrations without approval, create secrets, or mutate foundation package content during design work.
- Current status: Freeze/read-only capability complete; final analytics freeze required.
- Gap to GA: final module-specific capability audit, UConsole entry alignment, security/route validation, acceptance evidence, and customer activation plan as applicable.
- Next recommended task ID: REPORTS-GA-R1 Final Reports & Analytics Freeze.
## Governance & Security (GOVERNANCE_SECURITY)

- Purpose: RBAC, audit, policy, IEC62443 posture, route enforcement.
- Owner layer: Governance layer.
- Inputs: contract envelopes, role context, package entitlement state, source-system or module records relevant to Governance & Security.
- Outputs: validated API responses, events, evidence records, readiness state, reports, or handoff envelopes.
- Allowed actions: read approved data, validate contracts, publish read-only projections, produce audit/evidence artifacts, and request approved workflow transitions through CODE.
- Forbidden actions: bypass CODE, directly control devices from UConsole or NEXUS AI, activate runtime without approval, run DB migrations without approval, create secrets, or mutate foundation package content during design work.
- Current status: Route/boundary evidence present; final governance freeze required.
- Gap to GA: final module-specific capability audit, UConsole entry alignment, security/route validation, acceptance evidence, and customer activation plan as applicable.
- Next recommended task ID: GOVERNANCE-SECURITY-GA-R1 Final Governance & Security Freeze.
## NEXUS AI (NEXUS_AI)

- Purpose: triage, recommendation, model selection, risk scoring; no execution.
- Owner layer: Decision/context layer.
- Inputs: contract envelopes, role context, package entitlement state, source-system or module records relevant to NEXUS AI.
- Outputs: validated API responses, events, evidence records, readiness state, reports, or handoff envelopes.
- Allowed actions: read approved data, validate contracts, publish read-only projections, produce audit/evidence artifacts, and request approved workflow transitions through CODE.
- Forbidden actions: bypass CODE, directly control devices from UConsole or NEXUS AI, activate runtime without approval, run DB migrations without approval, create secrets, or mutate foundation package content during design work.
- Current status: Not activated; current branch integration freeze required.
- Gap to GA: final module-specific capability audit, UConsole entry alignment, security/route validation, acceptance evidence, and customer activation plan as applicable.
- Next recommended task ID: NEXUSAI-GA-R1 Current Branch Integration Freeze.
## EDGE (EDGE)

- Purpose: local connector/runtime foundation, read-only collectors, local buffer.
- Owner layer: Foundation package.
- Inputs: contract envelopes, role context, package entitlement state, source-system or module records relevant to EDGE.
- Outputs: validated API responses, events, evidence records, readiness state, reports, or handoff envelopes.
- Allowed actions: read approved data, validate contracts, publish read-only projections, produce audit/evidence artifacts, and request approved workflow transitions through CODE.
- Forbidden actions: bypass CODE, directly control devices from UConsole or NEXUS AI, activate runtime without approval, run DB migrations without approval, create secrets, or mutate foundation package content during design work.
- Current status: GA-ready for declared package scope.
- Gap to GA: final module-specific capability audit, UConsole entry alignment, security/route validation, acceptance evidence, and customer activation plan as applicable.
- Next recommended task ID: ONE-PROD-GA-R11 Customer Activation Plan.
## LINK (LINK)

- Purpose: gateway/API handoff, delivery, queue, ack, DLQ.
- Owner layer: Foundation package.
- Inputs: contract envelopes, role context, package entitlement state, source-system or module records relevant to LINK.
- Outputs: validated API responses, events, evidence records, readiness state, reports, or handoff envelopes.
- Allowed actions: read approved data, validate contracts, publish read-only projections, produce audit/evidence artifacts, and request approved workflow transitions through CODE.
- Forbidden actions: bypass CODE, directly control devices from UConsole or NEXUS AI, activate runtime without approval, run DB migrations without approval, create secrets, or mutate foundation package content during design work.
- Current status: GA-ready for declared package scope.
- Gap to GA: final module-specific capability audit, UConsole entry alignment, security/route validation, acceptance evidence, and customer activation plan as applicable.
- Next recommended task ID: ONE-PROD-GA-R11 Customer Activation Plan.
## DB (DB)

- Purpose: PostgreSQL package/migrations/seed/backup/restore.
- Owner layer: Foundation package.
- Inputs: contract envelopes, role context, package entitlement state, source-system or module records relevant to DB.
- Outputs: validated API responses, events, evidence records, readiness state, reports, or handoff envelopes.
- Allowed actions: read approved data, validate contracts, publish read-only projections, produce audit/evidence artifacts, and request approved workflow transitions through CODE.
- Forbidden actions: bypass CODE, directly control devices from UConsole or NEXUS AI, activate runtime without approval, run DB migrations without approval, create secrets, or mutate foundation package content during design work.
- Current status: GA-ready for declared package scope; no default migration.
- Gap to GA: final module-specific capability audit, UConsole entry alignment, security/route validation, acceptance evidence, and customer activation plan as applicable.
- Next recommended task ID: ONE-PROD-GA-R11 Customer Activation Plan.
## Contracts (CONTRACTS)

- Purpose: schemas, OpenAPI, envelope contracts.
- Owner layer: Foundation package.
- Inputs: contract envelopes, role context, package entitlement state, source-system or module records relevant to Contracts.
- Outputs: validated API responses, events, evidence records, readiness state, reports, or handoff envelopes.
- Allowed actions: read approved data, validate contracts, publish read-only projections, produce audit/evidence artifacts, and request approved workflow transitions through CODE.
- Forbidden actions: bypass CODE, directly control devices from UConsole or NEXUS AI, activate runtime without approval, run DB migrations without approval, create secrets, or mutate foundation package content during design work.
- Current status: GA-ready for declared package scope.
- Gap to GA: final module-specific capability audit, UConsole entry alignment, security/route validation, acceptance evidence, and customer activation plan as applicable.
- Next recommended task ID: ONE-PROD-GA-R11 Customer Activation Plan.
## Customer Delivery / Installer (CUSTOMER_DELIVERY_INSTALLER)

- Purpose: engineer-only installer scaffold, dry-run install/verify/rollback.
- Owner layer: Customer delivery.
- Inputs: contract envelopes, role context, package entitlement state, source-system or module records relevant to Customer Delivery / Installer.
- Outputs: validated API responses, events, evidence records, readiness state, reports, or handoff envelopes.
- Allowed actions: read approved data, validate contracts, publish read-only projections, produce audit/evidence artifacts, and request approved workflow transitions through CODE.
- Forbidden actions: bypass CODE, directly control devices from UConsole or NEXUS AI, activate runtime without approval, run DB migrations without approval, create secrets, or mutate foundation package content during design work.
- Current status: Scaffold PASS; production activation not executed.
- Gap to GA: final module-specific capability audit, UConsole entry alignment, security/route validation, acceptance evidence, and customer activation plan as applicable.
- Next recommended task ID: ONE-PROD-GA-R11 Customer Activation Plan.
## Offline Export (OFFLINE_EXPORT)

- Purpose: backup-ready tarball/checksum/restore metadata.
- Owner layer: Customer delivery.
- Inputs: contract envelopes, role context, package entitlement state, source-system or module records relevant to Offline Export.
- Outputs: validated API responses, events, evidence records, readiness state, reports, or handoff envelopes.
- Allowed actions: read approved data, validate contracts, publish read-only projections, produce audit/evidence artifacts, and request approved workflow transitions through CODE.
- Forbidden actions: bypass CODE, directly control devices from UConsole or NEXUS AI, activate runtime without approval, run DB migrations without approval, create secrets, or mutate foundation package content during design work.
- Current status: Offline export package PASS.
- Gap to GA: final module-specific capability audit, UConsole entry alignment, security/route validation, acceptance evidence, and customer activation plan as applicable.
- Next recommended task ID: ONE-PROD-GA-R11 Customer Activation Plan.

## Summary Decision

- Foundation package GA: PASS
- Offline export package: PASS
- Customer delivery scaffold: PASS
- Full customer production activation: NOT EXECUTED
- Full international GA across all modules: NOT YET

PASS marker: `ONE_DESIGN_R1_FULL_PRODUCT_DESIGN_BLUEPRINT_PASS`
