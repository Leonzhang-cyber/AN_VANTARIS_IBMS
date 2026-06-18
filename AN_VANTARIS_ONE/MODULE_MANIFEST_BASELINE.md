# VANTARIS ONE Module Manifest Baseline

## 1. Purpose

This document defines the current A0 module manifest baseline for VANTARIS ONE and serves as the baseline for subsequent A1 module manifest drafts.

## 2. Current Modules

- ONE Adapter
- UCore
- UMMS
- UESG
- UDOC
- UCDE
- UConsole
- Reports
- Analytics
- Nexus AI Consumer, future

## 3. Shared Foundation Dependencies

AN_VANTARIS_Contracts, AN_VANTARIS_EDGE, and AN_VANTARIS_LINK are UFMS-led Shared Foundation dependencies.
VANTARIS ONE consumes these dependencies and does not privately fork runtime.

Foundation Layer is reference-only in this task. This task does not modify AN_VANTARIS_EDGE, AN_VANTARIS_LINK, AN_VANTARIS_DB, AN_VANTARIS_Contracts, contracts, or schemas.

## 4. A1 Manifest Rule

Each A1 manifest must define:

- moduleId
- module owner scope
- consumed objects
- provided objects
- status model
- traceability fields
- integration boundary
- forbidden ownership
- API/DB/menu impact, if any
- runtime readiness

## 5. Current Boundary

A0 manifest does not represent runtime ready status, does not create real modules, and does not modify API/DB/frontend.

## 6. UDOC A1 Realignment

UDOC A1 module manifest draft is established.
Historical A0 wording `idc-dcim` is realigned to UDOC as the primary module name.
UDOC remains `runtimeReady: false`.
UDOC impact remains `none-in-a1-draft` for API, DB, menu, runtime, and schema.
