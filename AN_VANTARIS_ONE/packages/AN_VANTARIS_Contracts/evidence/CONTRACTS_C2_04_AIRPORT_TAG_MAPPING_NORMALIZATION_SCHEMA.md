# CONTRACTS-C2-04 — Airport Tag Mapping / Normalization Schema

Status: PASS
Scope: AN_VANTARIS_Contracts only
Date: 2026-06-20

## 1. Purpose

This evidence defines the airport tag mapping / normalization shared schema.

The schema standardizes how airport source-system raw tags are mapped to canonical
asset, device, point, telemetry, event, alarm, location, and HMI locator references.

This is a contract-only task. It does not implement any source-system connector,
EDGE runtime, LINK runtime, airport runtime, VANTARIS ONE, UMMS, UCDE, UFMS backend/frontend,
database schema, authentication, login, or credentials.

## 2. Schema Added

Added schema:

- AN_VANTARIS_Contracts/schemas/airport/airport-tag-mapping-normalization.v1.json

## 3. Coverage

The schema covers:

- mappingSetId
- sourceSystemProfileRef
- connectorMatrixItemRef
- onboardingPacketRef
- source system context
- normalization policy
- rawTagName
- rawAddress
- rawObjectType
- normalizedTagName
- objectType
- assetRef
- deviceRef
- pointRef
- sourceSystemRef
- signalType
- unit / engineeringUnit
- normalization rule
- value transform
- quality mapping
- deadband
- heartbeat policy
- event mapping
- alarm mapping
- severity mapping
- locationRef
- terminal / building / level / room / zone
- HMI locator
- mapping review status
- evidence references
- contract-only boundary flags

## 4. Boundary

This task does not modify EDGE runtime.

This task does not modify LINK runtime.

This task does not implement VANTARIS ONE, UMMS, UCDE, or UFMS runtime.

This task does not change DB/schema/migration/auth/login/credentials.

This task does not enable production delivery.

This task does not enable EDGE runtime.

This task does not apply runtime mapping.

This task does not allow writeback.

This task does not allow direct UFMS DB access.

## 5. Result

CONTRACTS_C2_04_AIRPORT_TAG_MAPPING_NORMALIZATION_SCHEMA_PASS

Airport tag mapping / normalization shared schema is now defined.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
