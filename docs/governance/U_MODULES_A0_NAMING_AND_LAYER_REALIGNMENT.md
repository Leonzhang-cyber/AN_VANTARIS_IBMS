# U Modules A0 Naming and Layer Realignment

## 1. Purpose

This governance document realigns VANTARIS ONE module naming and layer descriptions to the U-series model for docs, manifest, and roadmap consistency.

## 2. U-Series Naming Baseline

Naming mappings:

- ibms-core -> ucore
- mms -> umms
- esg -> uesg
- cde -> ucde
- idc-dcim -> udoc
- console -> uconsole

## 3. Layer Realignment Scope

Foundation Layer, reference-only:

- AN_VANTARIS_Contracts
- AN_VANTARIS_EDGE
- AN_VANTARIS_LINK
- AN_VANTARIS_DB

Platform Layer:

- ONE Adapter
- UConsole
- Reports
- Analytics
- Nexus AI Consumer

Unified Business Modules:

- UCore
- UMMS
- UESG
- UCDE
- UDOC

## 4. A0 Boundary

This task is docs/manifest/governance realignment only.
No runtime, API, DB, route, or source-code implementation is included.

Foundation Layer is reference-only in this task. This task does not modify AN_VANTARIS_EDGE, AN_VANTARIS_LINK, AN_VANTARIS_DB, AN_VANTARIS_Contracts, contracts, or schemas.
