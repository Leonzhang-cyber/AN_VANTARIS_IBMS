# UHMI-GA-R3 Customer Preview Package Guide

PASS marker: `UHMI_GA_R3_CUSTOMER_PREVIEW_PACKAGE_PASS`

## Purpose

The UHMI-GA-R3 Customer Preview Package prepares a demo-ready read-only UHMI Workspace package for customer review. It links the R1-R2F release evidence chain, documents the guided demo path, and records preview acceptance checks.

UHMI = Unified Human-Machine Interface. VANTARIS ONE is a cross-industry unified operations platform, not an airport-only system. UHMI remains UConsole-owned and may be surfaced as a high-frequency L1 entry while remaining part of the UConsole Workspace. UHMI is not HMI Server. UHMI is not SCADA replacement.

## Demo-ready Read-only Workspace Scope

R3 is documentation and evidence only. It does not add business functionality, UI functionality, control capability, runtime capability, device connectivity, production activation, package mutation, install, rollback, DB migration, auth mutation, login mutation, JWT mutation, or RBAC mutation.

Visual style remains:

`VANTARIS_LIGHT_OPERATIONS_CONSOLE`

## Customer Demo Path

1. Open UConsole.
2. Open UHMI Workspace.
3. Show `VANTARIS_LIGHT_OPERATIONS_CONSOLE`.
4. Show overview metrics.
5. Show system context panels.
6. Show device context table.
7. Show mimic panel preview.
8. Show event context.
9. Show evidence context.
10. Show role-based views.
11. Show disabled actions.
12. Show guardrails.
13. Show future control path.
14. Show R2F evidence pack and release index.

Every step is read-only, view-only, and demo-only.

## Role Demo Paths

- Customer: view workspace summary, evidence context, disabled actions, and release evidence.
- Engineer: view system/device context, mimic preview, event context, guardrails, and future control path.
- Admin: view role visibility context without real RBAC mutation.
- Operator: view operational context, alarm/event status, evidence links, and disabled actions.

## What Can Be Shown

- UConsole-owned UHMI Workspace.
- Demo-ready Read-only Workspace.
- `VANTARIS_LIGHT_OPERATIONS_CONSOLE`.
- Overview cards, system panels, device table, mimic preview, event context, evidence context, role-based views, guardrails, disabled actions, and R2F evidence chain.

## What Cannot Be Executed

- Production Activation Not Executed.
- Device control: `NOT EXECUTED`.
- DB migration/write: `NOT EXECUTED`.
- Runtime activation: `NOT EXECUTED`.
- EDGE/LINK command execution: `NOT EXECUTED`.
- Auth/RBAC mutation: `NOT EXECUTED`.
- Install or rollback: `NOT EXECUTED`.

## Read-only Safety Statement

No Direct Device Control. No Runtime Activation. No DB Write. No EDGE Command Execution. No LINK Command Execution. No auth / login / JWT / RBAC mutation.

All future control must follow:

`UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device`

## Evidence Pack Linkage

R3 links to:

- `UHMI_GA_R2F_FINAL_READONLY_WORKSPACE_RELEASE_INDEX.md`
- `UHMI_GA_R2F_EVIDENCE_PACK.md`
- `AN_VANTARIS_ONE/registries/uhmi-ga-r2f/uhmi-r2f-tag-commit-chain.txt`
- `AN_VANTARIS_ONE/registries/uhmi-ga-r3/uhmi-r3-release-chain.txt`

## R1-R2F Release Chain Linkage

R3 is based on the completed UHMI-GA-R1, UHMI-GA-R2A, UHMI-GA-R2B, UHMI-GA-R2C, UHMI-GA-R2D, UHMI-GA-R2E, and UHMI-GA-R2F chain.

`UHMI_GA_R3_CUSTOMER_PREVIEW_PACKAGE_PASS`
