# CONTRACTS-C2-05 — Airport Asset / Location / HMI Locator Metadata Schema

Status: PASS
Scope: AN_VANTARIS_Contracts only
Date: 2026-06-20

## 1. Purpose

This evidence defines the airport asset / location / HMI locator metadata shared schema.

The schema standardizes how airport assets, devices, points, locations, hierarchy,
engineering metadata, and HMI locator references are represented for future EDGE/LINK
integration planning.

This is a contract-only task. It does not implement any source-system connector,
EDGE runtime, LINK runtime, airport runtime, VANTARIS ONE, UMMS, UCDE, UFMS backend/frontend,
database schema, authentication, login, or credentials.

## 2. Schema Added

Added schema:

- AN_VANTARIS_Contracts/schemas/airport/airport-asset-location-hmi-locator.v1.json

## 3. Coverage

The schema covers:

- locatorSetId
- sourceSystemProfileRef
- connectorMatrixItemRef
- onboardingPacketRef
- tagMappingSetRef
- site / airport / timezone
- assetRef
- assetName
- assetType
- discipline
- sourceSystemRef
- deviceRef
- pointRefs
- tagRefs
- asset hierarchy
- parentAssetRef
- rootAssetRef
- hierarchyPath
- locationRef
- terminal / building / level / floor / room / zone / area
- GPS optional metadata
- HMI locator availability
- HMI system reference
- drawingRef
- pageRef
- symbolRef
- coordinate
- deepLinkRef
- screenshotRef
- engineering metadata
- asset review status
- location review status
- HMI review status
- engineering review status
- evidence references
- contract-only boundary flags

## 4. Boundary

This task does not modify EDGE runtime.

This task does not modify LINK runtime.

This task does not implement VANTARIS ONE, UMMS, UCDE, or UFMS runtime.

This task does not change DB/schema/migration/auth/login/credentials.

This task does not enable production delivery.

This task does not enable EDGE runtime.

This task does not apply runtime asset writes.

This task does not apply runtime location writes.

This task does not allow writeback.

This task does not allow direct UFMS DB access.

## 5. Result

CONTRACTS_C2_05_AIRPORT_ASSET_LOCATION_HMI_LOCATOR_SCHEMA_PASS

Airport asset / location / HMI locator metadata shared schema is now defined.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
