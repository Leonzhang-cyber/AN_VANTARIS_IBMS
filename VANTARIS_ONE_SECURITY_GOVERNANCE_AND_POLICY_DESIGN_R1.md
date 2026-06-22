# VANTARIS ONE Security Governance And Policy Design R1

## RBAC Model

- Customer: delivery acceptance, package visibility, reports, and approved evidence review.
- Operator: command center, event review, work queue participation, and governed acknowledgement.
- Engineer: installer console, topology validation, package verification, dry-run install/rollback evidence, technical acceptance.
- Supervisor: escalation approval, SLA review, cross-module operational oversight.
- Admin: tenant/site configuration, role assignment, entitlement mapping, governance configuration.

## Governance Domains

- Package entitlement: contract/customer right to access package capability.
- Package enablement: operational switch under policy and approval.
- Audit: immutable record of actor, action, route, package, approval, and evidence.
- Approval workflow: business, engineering, security, backup, rollback, and activation gates.
- Policy registry: thresholds, route declarations, SLA policy, entitlement rules, and forbidden actions.
- Evidence chain: UCDE-backed validation and acceptance trail.

## IEC62443 Posture

The current posture should be treated as IEC62443-aligned evidence building, not a completed certification claim. Required controls include role separation, least privilege, auditability, route enforcement, boundary validation, network segmentation planning, backup/restore evidence, and explicit activation gates.

## Secret Policy

No secrets in repo. .env files are externalized and must not be committed. Production secrets are provisioned through customer-approved secret management outside this repository.

## Offline Deployment Governance

Offline deployment requires manifest integrity, checksum verification, package counts, dry-run evidence, backup plan, rollback authority, customer acceptance, and activation approvals. Offline delivery does not imply runtime activation.

## Route Enforcement

All production routes must be declared, validated, and mapped to module boundaries. UConsole and modules must route through CODE/API boundaries. EDGE/LINK handoff follows contract envelopes and does not directly mutate module databases.

## Boundary Validation

Boundary validation must confirm package isolation, module ownership, read-only projection status where applicable, no direct DB bypass, no uncontrolled runtime activation, and no forbidden package writes.

## AI Governance

NEXUS AI is advisory/control-plane context. It may triage, recommend, score risk, and select models under policy, but it performs no autonomous execution and no device control.

## Production Activation Approvals

Activation requires customer approval, engineering approval, security/governance approval, backup confirmation, rollback owner, deployment window, and acceptance evidence. Current R10 state: full customer production activation NOT EXECUTED and full international GA across all modules NOT YET.

PASS marker: `ONE_DESIGN_R1_FULL_PRODUCT_DESIGN_BLUEPRINT_PASS`
