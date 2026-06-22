# VANTARIS ONE GA Gap And Roadmap R1

## Current GA Status By Module

| Module | Current status | GA status |
| --- | --- | --- |
| UCode / CODE Layer | Freeze required | Not full GA yet |
| UMMS | Freeze/read-only capability complete; final module GA freeze required | Not full GA yet |
| UFMS | Foundation/projection evidence present; final full-product GA evidence required | Not full GA yet |
| UESG | Freeze/read-only capability complete; final module GA freeze required | Not full GA yet |
| UCDE | Freeze/read-only capability complete; final capability audit required | Not full GA yet |
| UDOC | Incomplete/not confirmed by final GA-specific evidence | Not full GA yet |
| Automated Rules & Policy | Freeze required before GA | Not full GA yet |
| ONE Orchestrator | Scaffold/current branch integration not confirmed | Not full GA yet |
| UConsole | Freeze/read-only capability complete; unified entry consistency required | Not full GA yet |
| Reports & Analytics | Freeze/read-only capability complete; final analytics freeze required | Not full GA yet |
| Governance & Security | Route/boundary evidence present; final governance freeze required | Not full GA yet |
| NEXUS AI | Not activated; current branch integration freeze required | Not full GA yet |
| EDGE | GA-ready for declared package scope | Foundation GA scope PASS |
| LINK | GA-ready for declared package scope | Foundation GA scope PASS |
| DB | GA-ready for declared package scope; no default migration | Foundation GA scope PASS |
| Contracts | GA-ready for declared package scope | Foundation GA scope PASS |
| Customer Delivery / Installer | Scaffold PASS; production activation not executed | Scaffold PASS; activation NOT EXECUTED |
| Offline Export | Offline export package PASS | Foundation GA scope PASS |

## Gap Severity

- P0 blocker: customer production activation not executed; full international GA across all modules not yet; DB migration and runtime activation approvals not established for a real customer deployment.
- P1 required before GA: final freeze for UCDE, UConsole, UMMS, UESG, Reports, Governance/Security, NEXUS AI, UCode, UDOC, and ONE Orchestrator; acceptance evidence package; package entitlement/enablement state; route and boundary validation.
- P2 post-GA hardening: HA/DR playbooks, performance baselines, operational runbooks, training packs, extended IEC62443 evidence, additional industry projection packs.

## Recommended Next Milestones

- UCDE-GA-R1 Final Capability Audit + Consolidated Freeze
- UCONSOLE-GA-R1 Full Module Entry & Menu Consistency Freeze
- UMMS-GA-R1 Final Module Consolidated Freeze
- UESG-GA-R1 Final Module Consolidated Freeze
- REPORTS-GA-R1 Final Reports & Analytics Freeze
- GOVERNANCE-SECURITY-GA-R1 Final Governance & Security Freeze
- NEXUSAI-GA-R1 Current Branch Integration Freeze
- UCODE-GA-R1 CODE Layer Final API/Execution Boundary Freeze
- UDOC-GA-R1 Document & Evidence Package Skeleton
- ONE-ORCH-GA-R1 Orchestrator Read-only Workflow Freeze
- ONE-PROD-GA-R11 Customer Activation Plan

## Realistic GA Path

- Phase A: module freeze for UCDE, UConsole, UMMS, UESG, Reports, Governance/Security, NEXUS AI, UCode, UDOC, and ONE Orchestrator.
- Phase B: UConsole unified entry with L1/L2 navigation, module readiness badges, entitlement states, and no production mock/demo/pilot labels.
- Phase C: installer/customer delivery with dry-run evidence, explicit backup-first DB plan, package integrity, and acceptance signoff.
- Phase D: runtime activation pilot under explicit customer approval, rollback authority, and audit capture.
- Phase E: international GA after module freezes, pilot evidence, operational runbooks, and governance/security acceptance are complete.

## Explicit Current State

The current state is a strong foundation, not full customer activated GA.

- Foundation package GA: PASS
- Offline export package: PASS
- Customer delivery scaffold: PASS
- Full customer production activation: NOT EXECUTED
- Full international GA across all modules: NOT YET

PASS marker: `ONE_DESIGN_R1_FULL_PRODUCT_DESIGN_BLUEPRINT_PASS`
