# VANTARIS ONE Customer Delivery And Deployment Design R1

## Offline Delivery Structure

Offline delivery is organized as a signed/checksummed customer package containing foundation packages, manifest metadata, delivery notes, package counts, backup/restore metadata, acceptance checklists, and dry-run scripts. The R9 scaffold exists under `deployment/prod-ga/customer-delivery` and separates delivery acceptance from production activation.

## Engineer Installer Console

The engineer console is an engineer-only surface for precheck, package integrity, topology selection, dry-run install, verify, rollback dry-run, evidence export, and approval gate review. It must show package state as locked, entitled, installed, enabled, visible, or not activated.

## Precheck Flow

- Confirm customer identity, site, edition, package entitlement, operator roles, hardware/OS prerequisites, time sync, disk capacity, network plan, and backup location.
- Verify package counts: EDGE 248, LINK 153, DB 14, Contracts 174.
- Confirm no production secrets are bundled and .env configuration is externalized.

## Install Dry-Run Flow

- Parse manifest and topology.
- Validate package integrity and permissions.
- Build a proposed action plan without starting services, applying DB migrations, or activating runtime.
- Export engineer-readable dry-run evidence.

## Verify Flow

- Verify package files, checksums, route boundaries, contract schemas, DB backup plan, and UConsole/customer delivery readiness.
- Verify that production activation remains blocked until explicit approval.

## Rollback Dry-Run Flow

- Validate rollback authority, backup availability, package manifest, and proposed restore sequence.
- Produce rollback evidence without destructive action.

## DB Plan

- PostgreSQL is the production database target.
- No default migration is performed.
- Backup first is mandatory before any future migration or activation.
- Migration execution requires explicit customer and engineering approval.

## EDGE/LINK Deployment

- All-in-one: EDGE and LINK co-located with application services for constrained deployments.
- Multi-edge single-link: many EDGE nodes buffer and hand off to one central LINK gateway.
- Customer server split: app/CODE/UConsole separated from PostgreSQL and optional EDGE nodes.

## Production Activation Approval Gates

- Business owner approval.
- Engineering owner approval.
- Security/governance approval.
- Backup confirmation.
- Rollback authority.
- Deployment window.
- Acceptance signer.
- Runtime activation plan.

## Acceptance Evidence Package

- Package manifest and counts.
- Checksum verification.
- Precheck result.
- Install dry-run result.
- Verify result.
- Rollback dry-run result.
- DB backup plan.
- Route/boundary validation.
- Customer acceptance checklist.

## What R9 Completed

R9 completed a customer delivery scaffold, dry-run installer/verify/rollback scripts, engineer installer console specification, customer delivery UI flow, checklists, manifest/registry, and PASS validation. R9 did not execute installation, rollback, DB migration, runtime activation, push, tag, merge, or rebase.

## What Remains For Real Customer Deployment

A real customer deployment still needs environment-specific activation planning, production secrets outside the repo, approved PostgreSQL backup/migration window, UConsole entitlement/enablement binding, EDGE/LINK connectivity verification, security acceptance, and signed activation evidence.

PASS marker: `ONE_DESIGN_R1_FULL_PRODUCT_DESIGN_BLUEPRINT_PASS`
