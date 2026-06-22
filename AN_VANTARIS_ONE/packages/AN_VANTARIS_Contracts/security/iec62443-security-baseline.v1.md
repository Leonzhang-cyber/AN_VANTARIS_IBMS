# IEC 62443 Security Baseline v1

## 1. Purpose

Define an IEC 62443 aligned baseline for VANTARIS ONE, standalone UFMS, EDGE, LINK, Code/API, DB, Console, NexusAI, and future module profiles.

## 2. Scope

Applies to:

- Contracts
- EDGE
- LINK
- Code/API
- DB architecture
- Console architecture
- NexusAI integration
- deployment profiles
- module profiles

## 3. Single Unified Platform Rule

- one Contracts authority
- one EDGE runtime
- one LINK runtime
- one Code/API architecture
- one DB architecture
- one Console architecture
- one NexusAI integration architecture
- standalone UFMS and VANTARIS ONE differ by profile/config, not forks

## 4. IEC 62443 alignment categories

- secure product development lifecycle alignment
- component technical security requirement alignment
- system segmentation / zones and conduits alignment
- security level target baseline
- operational maintenance and patch evidence
- auditability and traceability

## 5. Foundational security requirements mapping

| IEC alignment area | VANTARIS control objective | Applicable packages | Evidence artifact | Validation method | Current status |
|---|---|---|---|---|---|
| identification and authentication control | machine identity for service-to-service boundaries | Contracts, EDGE, LINK, Code/API | machine identity standard, signed handoff headers | contract schema + integration checklist validation | BASELINE |
| use control | least privilege runtime and operator control paths | EDGE, LINK, Code/API, Console | deployment profile security baseline | config/profile review + boundary scan | PENDING_RUNTIME |
| system integrity | signed handoff, immutable event paths, change traceability | Contracts, EDGE, LINK | signature standard, reliability profile, contract drift checks | validate-contracts + contract-drift scan | BASELINE |
| data confidentiality | secrets outside repo and secure config handling | Contracts, EDGE, LINK, Code/API | no-secrets policy + deployment/package baseline docs | secret marker scans + review checklist | BASELINE |
| restricted data flow | explicit zone/conduit boundaries and no direct DB write from EDGE/LINK | Contracts, EDGE, LINK, Code/API, DB | DB boundary docs + architecture standards | boundary scans + policy review | BASELINE |
| timely response to events | security event classification and response evidence hooks | LINK, Code/API, Console, NexusAI | auditability contract + traceability matrix | test checklist + response drill evidence placeholder | PENDING_EVIDENCE |
| resource availability | buffer/restart resilience and bounded resource behavior | EDGE, LINK | reliability contracts + GA checklist | smoke validation + runtime evidence pack | PENDING_RUNTIME |

## 6. Security Level Target baseline

- SL-T baseline target: SL2-aligned for initial International GA engineering baseline.
- Higher SL-T profiles can be project-specific.
- No certification claim is made in this baseline.
- Project-specific risk assessment is required for SL claim.

## 7. Zones and conduits model

### Default conceptual zones

- Field Device Zone
- EDGE Zone
- LINK / Integration Zone
- Code/API Zone
- DB Zone
- Console / Operator Zone
- NexusAI / Insight Zone
- Admin / Maintenance Zone

### Conduits

- Device to EDGE
- EDGE to LINK
- LINK to Code/API
- Code/API to DB
- Console to Code/API
- Code/API to NexusAI
- Admin maintenance conduit

## 8. Mandatory cross-package controls

- no EDGE/LINK direct DB write
- machine identity for service-to-service
- no human JWT for machine runtime
- signed handoff
- idempotency
- replay protection
- least privilege
- no secrets in repo
- secure config
- audit logs
- change trace
- patch/rollback evidence
- vulnerability response evidence

## 9. Certification-ready evidence baseline

Required evidence artifacts:

- architecture diagrams
- threat model
- zone/conduit model
- security requirements traceability matrix
- secure development checklist
- dependency inventory
- vulnerability scan report placeholder
- hardening checklist
- test evidence
- deployment evidence
- patch/rollback evidence
- incident response checklist
