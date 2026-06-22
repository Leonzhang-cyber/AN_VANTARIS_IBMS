# CONTRACTS-C2-02 — Airport ELV Connector Matrix Schema

Status: PASS
Scope: AN_VANTARIS_Contracts only
Date: 2026-06-20

## 1. Purpose

This evidence defines the airport ELV connector matrix shared schema.

The schema is used to describe the connector readiness, protocol preference,
fallback protocol, EDGE adapter requirement, data objects, commissioning priority,
and integration risk for airport ELV, BMS, EMS, MMS, security, and facility systems.

This is a contract-only task. It does not implement any source-system connector,
EDGE runtime, LINK runtime, airport runtime, VANTARIS ONE, UMMS, UCDE, UFMS backend/frontend,
database schema, authentication, login, or credentials.

## 2. Schema Added

Added schema:

- AN_VANTARIS_Contracts/schemas/airport/airport-elv-connector-matrix.v1.json

## 3. Coverage

The schema covers:

- matrixId
- site / airport / terminal reference
- sourceSystemProfileRef
- sourceSystemType
- discipline
- vendor
- productName
- preferredProtocol
- fallbackProtocols
- connectorReadiness
- EDGE adapter requirement
- readOnly=true
- writebackAllowed=false
- supported data objects
- estimated point count
- estimated device count
- alarm / telemetry / health / evidence support
- tag mapping requirement
- asset mapping requirement
- location mapping requirement
- HMI locator requirement
- commissioning priority
- commissioning status
- integration risk
- data quality risk
- security risk
- evidence references
- contract-only boundary flags

## 4. Airport Systems Covered

The schema can represent connector matrix rows for:

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

This task does not implement runtime connector code.

This task does not allow writeback.

This task does not allow direct UFMS DB access.

## 6. Result

CONTRACTS_C2_02_AIRPORT_ELV_CONNECTOR_MATRIX_SCHEMA_PASS

Airport ELV connector matrix shared schema is now defined.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
