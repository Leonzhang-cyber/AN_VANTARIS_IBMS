# VANTARIS ONE Data Flow Model

## 1. Telemetry Flow

- source: Device telemetry (`BMS/FAS/ACS/CCTV/Lift/PLC/SCADA/IoT`)
- transport: protocol adapter + message envelope
- target: `Edge -> Link -> Code -> DB -> Console`
- contract dependency: edge protocol contract + envelope schema + telemetry API/event contract
- persistence: hot telemetry store + history tables
- audit requirement: ingest trace, route trace, write trace
- security requirement: source authentication, transport integrity, replay protection

## 2. Alarm/Event Flow

- source: Device/System alarm and event signals
- transport: edge event publish + link route delivery
- target: `Edge -> Link -> Code/Event Alarm -> UFMS Adapter(optional) -> CDE`
- contract dependency: event taxonomy + severity/state contract
- persistence: event ledger + alarm state store + CDE references
- audit requirement: event lifecycle audit and operator action trail
- security requirement: tamper-evident event id, RBAC on alarm actions

## 3. Fault Intelligence Flow

- source: alarm/event context
- transport: adapter/API call
- target: `UFMS Adapter / NexusAI -> CDE -> Work Management`
- contract dependency: fault case contract + RCA result contract
- persistence: fault case store + RCA trace + action recommendations
- audit requirement: inference provenance and decision audit
- security requirement: adapter boundary isolation, explainability trace retention

## 4. Work Order Flow

- source: alarm/fault triggers or planned maintenance requests
- transport: business API + workflow events
- target: `Code/MMS -> DB -> Console/Mobile`
- contract dependency: work order schema + state transition contract
- persistence: work order tables + assignment and SLA history
- audit requirement: who/when state change and execution evidence
- security requirement: permission checks on assign/close/override

## 5. AI Inference Flow

- source: `Code` or `UFMS Adapter` inference request
- transport: AI gateway API
- target: `NexusAI -> CDE Trace -> Code`
- contract dependency: AI request/response contract + model registry contract
- persistence: inference metadata, prompt/feature hash, output references
- audit requirement: model/version/request-id traceability
- security requirement: AI safety guard, output policy validation, PII minimization

## 6. Evidence Flow

- source: `Edge / Code / NexusAI`
- transport: evidence API + signed metadata
- target: `CDE Evidence -> DB/Object Storage -> Hash Anchor`
- contract dependency: evidence object schema + hash anchor contract
- persistence: evidence metadata + immutable hash chain references
- audit requirement: full custody chain and verification logs
- security requirement: integrity hash, access control, retention policy

## 7. License/Patch Flow

- source: Console operations
- transport: control API + signed patch/license manifest
- target: `Code/Patch Manager -> Module/Edge/Link/NexusAI -> Audit/CDE`
- contract dependency: patch manifest + module manifest + license VC contract
- persistence: deployment records + activation records + rollback logs
- audit requirement: approval trail, deployment trail, rollback trail
- security requirement: signature verification, environment gate, staged rollout

## 8. Trust Flow

- source: Machine DID / License VC / Patch VC / Module VC
- transport: trust verification API
- target: `Trust Registry -> runtime verification`
- contract dependency: DID/VC trust contract + verification policy contract
- persistence: trust registry tables + verification receipts
- audit requirement: verification result logs and non-repudiation evidence
- security requirement: cryptographic verification, key rotation support, revocation checks
