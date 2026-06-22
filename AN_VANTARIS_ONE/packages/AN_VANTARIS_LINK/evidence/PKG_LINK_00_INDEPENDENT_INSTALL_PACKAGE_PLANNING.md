# PKG-LINK-00 — LINK Independent Install Package Planning

Status: PASS
Scope: AN_VANTARIS_LINK only
Read-only references: AN_VANTARIS_EDGE / AN_VANTARIS_Contracts
Date: 2026-06-20

## 1. Purpose

This evidence opens PKG-LINK independent install package work.

The purpose is to move AN_VANTARIS_LINK from the current STRUCTURE_ONLY offline bundle
toward an independent install package foundation comparable to the EDGE package foundation.

This stage does not enable production delivery.

## 2. Current Baseline

Completed before PKG-LINK:

- LINK-C1 Baseline / Architecture
- LINK-C2 Ingress Contract / Security
- LINK-C3 Queue / Partition / Durable State
- LINK-C4 Delivery / ACK / Idempotency / Reliability
- LINK-C5 Retry / DLQ
- LINK-C6 Audit / Evidence Chain
- LINK-C7 Runtime Operations / Diagnostics
- LINK-C8 Offline Deployment Package
- LINK-C9 EDGE-LINK Integration Readiness
- LINK-C10 Final LINK Closure / Release Readiness
- CONTRACTS-C1 Shared EDGE / LINK Foundation
- CONTRACTS-C2 Airport Shared Contract Foundation
- CONTRACTS-C3 Future Consumer Boundary Foundation
- CONTRACTS-C4 Final Contracts Aggregate Gate
- PKG-EDGE-00 EDGE Independent Install Package Final Check

## 3. Current LINK Package State

Current LINK package state:

- offline bundle structure exists
- package manifest exists
- verification script exists
- local healthcheck script exists
- rollback / uninstall plan exists
- package integrity evidence exists
- C8 aggregate gate complete
- C10 final LINK aggregate gate complete

Current limitation:

- LINK offline bundle is still STRUCTURE_ONLY
- LINK does not yet have EDGE-equivalent lifecycle manifest
- LINK does not yet have EDGE-equivalent release manifest / checksums foundation
- LINK does not yet have package-level install dry-run evidence
- LINK does not yet have full independent install package aggregate gate

## 4. PKG-LINK Goal

PKG-LINK must create an independent install package foundation for AN_VANTARIS_LINK while preserving all safety boundaries.

The package foundation should include:

- package lifecycle manifest
- release layout document
- install plan
- uninstall plan
- upgrade plan
- rollback plan
- package integrity manifest
- checksum placeholder / checksum generation foundation
- install dry-run script or install dry-run evidence
- uninstall dry-run evidence
- upgrade / rollback dry-run evidence
- package validation evidence
- final independent package aggregate gate

## 5. Planned PKG-LINK Tasks

Planned tasks:

- PKG-LINK-00 Independent Install Package Planning
- PKG-LINK-01 Lifecycle Manifest and Release Layout
- PKG-LINK-02 Install / Uninstall / Upgrade / Rollback Plans
- PKG-LINK-03 Package Integrity Manifest and Checksum Foundation
- PKG-LINK-04 Install Dry-run Validation
- PKG-LINK-05 Uninstall / Upgrade / Rollback Dry-run Validation
- PKG-LINK-06 Independent Package Integrity Evidence
- PKG-LINK-07 Final LINK Independent Install Package Gate

## 6. EDGE Package Reference Standard

EDGE read-only reference standard:

- offline-bundle manifest
- lifecycle manifest
- install plan
- uninstall guard
- upgrade plan
- rollback plan
- package integrity files
- release manifest
- checksum foundation
- precheck
- smokecheck
- healthcheck
- install / uninstall / upgrade / rollback scripts
- package evidence

LINK should align with the EDGE package standard where appropriate, but must not copy EDGE runtime or enable LINK production delivery.

## 7. Allowed Scope

Allowed paths:

- AN_VANTARIS_LINK/**

Read-only references:

- AN_VANTARIS_EDGE/**
- AN_VANTARIS_Contracts/**

## 8. Forbidden Scope

Forbidden:

- UFMS backend/frontend
- DB/schema/migration
- auth/login/credentials
- VANTARIS ONE runtime
- UMMS runtime
- UCDE runtime
- production delivery enablement
- endpoint approval
- real UFMS API delivery
- direct UFMS DB access
- writeback
- live EDGE runtime enablement
- live LINK runtime enablement
- live service start
- real install execution on host system

## 9. Runtime Boundary

PKG-LINK must preserve:

- linkProductionDeliveryAllowed=false
- endpointApproved=false
- directUfmsDbAccessAllowed=false
- writebackAllowed=false
- consumerImplementationIncluded=false
- realUfmsApiDeliveryEnabled=false
- serviceStartExecuted=false
- realInstallExecuted=false
- pilot not approved
- runtime enablement not approved

## 10. Validation Requirements

Each PKG-LINK task must preserve:

- node AN_VANTARIS_Contracts/scripts/validate-all-contract-schemas.mjs
- bash AN_VANTARIS_LINK/deploy/offline-bundle/scripts/verify-link-offline-package.sh
- bash AN_VANTARIS_LINK/deploy/offline-bundle/scripts/healthcheck-link-offline.sh
- npm --prefix AN_VANTARIS_LINK run typecheck
- bash AN_VANTARIS_LINK/scripts/link-boundary-scan.sh
- git status --short
- no generated dist tracked
- no .runtime tracked
- no package-lock or dependency drift unless explicitly authorized

## 11. Result

PKG_LINK_00_INDEPENDENT_INSTALL_PACKAGE_PLANNING_PASS

PKG-LINK independent install package work is opened.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
