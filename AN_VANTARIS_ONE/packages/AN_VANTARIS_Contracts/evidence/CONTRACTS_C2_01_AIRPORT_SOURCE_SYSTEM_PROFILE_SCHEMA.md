# CONTRACTS-C2-01 — Airport Source System Profile Schema

Status: PASS
Scope: AN_VANTARIS_Contracts only
Date: 2026-06-20

## 1. Purpose

This evidence defines the airport source system profile shared schema.

The schema is used to describe existing airport systems that may later be connected
through EDGE and delivered through LINK.

This is a contract-only task. It does not implement any source-system connector,
airport runtime, VANTARIS ONE, UMMS, UCDE, UFMS backend/frontend, database schema,
authentication, login, or credentials.

## 2. Schema Added

Added schema:

- AN_VANTARIS_Contracts/schemas/airport/airport-source-system-profile.v1.json

## 3. Coverage

The schema covers:

- sourceSystemId
- sourceSystemName
- sourceSystemType
- discipline
- vendor
- productName
- productVersion
- ownerTeam
- criticality
- site / terminal / building / level / zone
- integrationMode
- protocol
- direction
- EDGE required flag
- LINK required flag
- connection profile reference
- commissioning status
- expected object types
- estimated point count
- tag naming availability
- asset mapping availability
- location mapping availability
- HMI locator availability
- sample data availability
- health / heartbeat / diagnostics capability
- evidence references
- contract-only boundary flags

## 4. Airport Systems Covered

The schema can represent airport systems such as:

- Bosch CCTV
- Bosch ACS / SMS
- PA System
- Radio System
- IPTV
- Clock System
- IPBX
- Toll System
- BMS
- EMS
- MMS
- e-Inspection
- iFeedback
- Security System
- Fire Alarm
- Lift / Escalator
- Lighting
- Power Metering
- HVAC
- Water

## 5. Boundary

This task does not modify EDGE runtime.

This task does not modify LINK runtime.

This task does not implement VANTARIS ONE, UMMS, UCDE, or UFMS runtime.

This task does not change DB/schema/migration/auth/login/credentials.

This task does not enable production delivery.

This task does not enable EDGE runtime.

This task does not allow writeback.

This task does not allow direct UFMS DB access.

## 6. Result

CONTRACTS_C2_01_AIRPORT_SOURCE_SYSTEM_PROFILE_SCHEMA_PASS

Airport source system profile shared schema is now defined.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
