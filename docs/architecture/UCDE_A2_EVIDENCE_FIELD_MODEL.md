# UCDE A2 Evidence Field Model

UCDE-A2 is a VANTARIS ONE docs-level evidence contract draft only. It does not modify AN_VANTARIS_Contracts, contracts/, schemas/, backend/, frontend/, DB, Edge, or Link.

This field model is:

- not JSON Schema
- not DB schema
- not OpenAPI schema
- not runtime DTO

## 1) Identity fields

- field name: `evidenceId`; purpose: unique evidence reference identity; ownership: UCDE docs-level draft; A2 decision: retained as required identity anchor.
- field name: `evidenceType`; purpose: evidence category reference; ownership: UCDE docs-level draft; A2 decision: required for cross-module filtering.
- field name: `evidenceVersion`; purpose: draft evidence shape versioning reference; ownership: UCDE docs-level draft; A2 decision: required for future promotion gating.
- field name: `tenantId`; purpose: tenant scope reference; ownership: source module reference + UCDE linkage; A2 decision: required.
- field name: `projectId`; purpose: project scope reference; ownership: source module reference + UCDE linkage; A2 decision: required.

## 2) Source reference fields

- field name: `sourceModuleId`; purpose: identifies source module reference; ownership: source module reference; A2 decision: required.
- field name: `sourceSystem`; purpose: identifies source system reference; ownership: shared reference boundary; A2 decision: required.
- field name: `sourceRecordId`; purpose: points to original source record; ownership: source module reference; A2 decision: required.
- field name: `sourceRecordType`; purpose: source record classification; ownership: source module reference; A2 decision: required.

## 3) Traceability fields

- field name: `traceId`; purpose: trace correlation across modules; ownership: shared traceability context; A2 decision: required.
- field name: `correlationId`; purpose: cross-event correlation reference; ownership: shared traceability context; A2 decision: required.
- field name: `messageId`; purpose: message-level linkage identity; ownership: integration reference layer; A2 decision: required.
- field name: `createdAt`; purpose: evidence draft creation timestamp reference; ownership: UCDE draft semantics; A2 decision: required.
- field name: `updatedAt`; purpose: evidence draft update timestamp reference; ownership: UCDE draft semantics; A2 decision: required.

## 4) Context linkage fields

- field name: `assetId`; purpose: asset context linkage; ownership: source module reference; A2 decision: optional-by-context.
- field name: `deviceId`; purpose: device context linkage; ownership: source module reference; A2 decision: optional-by-context.
- field name: `eventId`; purpose: event context linkage; ownership: source module reference; A2 decision: optional-by-context.
- field name: `alarmId`; purpose: alarm context linkage; ownership: source module reference; A2 decision: optional-by-context.
- field name: `workOrderId`; purpose: maintenance linkage reference; ownership: UMMS source reference; A2 decision: optional-by-context.
- field name: `energyContextId`; purpose: sustainability linkage reference; ownership: UESG source reference; A2 decision: optional-by-context.
- field name: `operationContextId`; purpose: core operation linkage reference; ownership: UCore source reference; A2 decision: optional-by-context.

## 5) Integrity reference fields

- field name: `sourceHashReference`; purpose: source payload integrity reference; ownership: source reference + UCDE linkage; A2 decision: draft required.
- field name: `payloadHashReference`; purpose: payload fingerprint reference; ownership: UCDE draft semantics; A2 decision: draft required.
- field name: `signatureReference`; purpose: signature pointer reference only; ownership: source reference domain; A2 decision: reference-only.
- field name: `chainReference`; purpose: chain pointer reference only; ownership: future formal contract scope; A2 decision: reference-only.
- field name: `previousEvidenceId`; purpose: evidence sequence linkage; ownership: UCDE draft semantics; A2 decision: optional sequence reference.

## 6) Retention / classification fields

- field name: `retentionClass`; purpose: retention policy class reference; ownership: governance reference; A2 decision: required policy pointer.
- field name: `classification`; purpose: data classification reference; ownership: governance/security reference; A2 decision: required.
- field name: `immutabilityPolicy`; purpose: immutability expectation reference; ownership: governance reference; A2 decision: draft policy pointer only.

## 7) Redaction / privacy fields

- field name: `redactionPolicy`; purpose: redaction policy reference; ownership: governance/security reference; A2 decision: required policy pointer.
- field name: `riskContextId`; purpose: privacy/risk linkage reference; ownership: governance/security reference; A2 decision: optional-by-context.

## 8) Readiness / lifecycle fields

- field name: `contractStatus`; purpose: draft lifecycle status; ownership: UCDE draft governance; A2 decision: required, `draft-a2`.
- field name: `runtimeReady`; purpose: runtime readiness indicator; ownership: UCDE draft governance; A2 decision: fixed false in A2.
- field name: `schemaReady`; purpose: schema readiness indicator; ownership: UCDE draft governance; A2 decision: fixed false in A2.
- field name: `apiReady`; purpose: API readiness indicator; ownership: UCDE draft governance; A2 decision: fixed false in A2.
- field name: `dbReady`; purpose: DB readiness indicator; ownership: UCDE draft governance; A2 decision: fixed false in A2.
- field name: `contractsPackageReady`; purpose: formal contracts package readiness indicator; ownership: UCDE draft governance; A2 decision: fixed false in A2.
