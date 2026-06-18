# VANTARIS ONE U Module Naming Model

## 1. Purpose

Define canonical U-series naming for VANTARIS ONE modules and deprecated-name mapping for transition consistency.

## 2. Canonical Module Names

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

## 3. Deprecated-to-U Mapping

- ibms-core -> ucore
- MMS / mms -> UMMS / umms
- ESG / esg -> UESG / uesg
- CDE / cde -> UCDE / ucde
- IDC/DCIM / idc-dcim / Data Center Operations -> UDOC / udoc
- Console / console -> UConsole / uconsole

## 4. Naming Rules

- Use U-series names in roadmap primary task naming.
- Allow deprecated names only in historical/deprecated/replaced-by context.
- Keep file paths stable unless a separate approved task allows directory rename.

## 5. A0 Boundary

This naming model is docs/manifest alignment only.

Foundation Layer is reference-only in this task. This task does not modify AN_VANTARIS_EDGE, AN_VANTARIS_LINK, AN_VANTARIS_DB, AN_VANTARIS_Contracts, contracts, or schemas.
