# CUSTOMER-DELIVERY-GA-R1 Engineer Installer Console Read-only Preview

PASS marker: CUSTOMER_DELIVERY_GA_R1_ENGINEER_INSTALLER_CONSOLE_READONLY_PREVIEW_PASS

## Purpose

CUSTOMER-DELIVERY-GA-R1 freezes a read-only preview for Customer Delivery / Engineer Installer Console under UConsole / Customer Delivery. VANTARIS ONE remains a cross-industry unified operations platform and is not airport-only.

## Preview Scope

- Engineer Installer Console read-only preview scope: package readiness, server plan, offline handoff, precheck, installation plan, verification plan, rollback plan, acceptance checklist, and diagnostics preview.
- Customer Delivery workspace preview scope: customer-facing delivery planning and acceptance review.
- This is not a production installer.
- This does not execute install / uninstall / rollback.
- This does not execute deployment.
- This does not execute SSH.

## Server Planning

- APP / non-DB target: 192.168.60.21.
- DB-only target: 192.168.60.22.
- Server planning is read-only preview only.
- No SSH.
- No Install.
- No Rollback.
- No DB Migration.
- No DB Write.

## Runtime Boundary

- No Runtime Activation.
- No Direct Device Control.
- No EDGE Command Execution.
- No LINK Command Execution.
- No auth / login / JWT / RBAC mutation.
- No Production Activation.
- No runnable production package.
- No dist/build committed.

visualStyle: VANTARIS_LIGHT_OPERATIONS_CONSOLE.

Future controls require:

UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device
