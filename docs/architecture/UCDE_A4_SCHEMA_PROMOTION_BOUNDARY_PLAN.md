# UCDE A4 Schema Promotion Boundary Plan

This is a boundary planning document only.
It is not JSON Schema, not DB schema, not OpenAPI, not runtime DTO, and does not modify `schemas/`.

## 1. Docs-level Field Model to Future Schema Candidate Boundary

- eligible-for-future-candidate consideration: evidence identity/context/integrity fields already defined in UCDE draft
- planning-only boundary: fields remain semantic references until future authorized phases

## 2. Fields Potentially Entering Future Schema Candidate

- identity group: `evidenceId`, `evidenceType`, `evidenceVersion`, `tenantId`, `projectId`, `siteId`
- context group: `sourceModuleId`, `sourceSystem`, `sourceRecordId`, `sourceRecordType`
- traceability group: `traceId`, `correlationId`, `messageId`, `createdAt`, `updatedAt`

## 3. Fields That Must Stay Reference-only in A4

- `sourceHashReference`
- `payloadHashReference`
- `signatureReference`
- `chainReference`
- `immutabilityPolicy`

## 4. Fields Requiring Security/Privacy Review

- `classification`
- `redactionPolicy`
- `sourceRecordId`
- `sourceRecordType`
- any cross-module context linkage identifiers

## 5. Fields Requiring Retention/Redaction Decision

- `retentionClass`
- `classification`
- `redactionPolicy`
- `previousEvidenceId` (chain retention effect)

## 6. Fields That Cannot Be Frozen in A4

- final producer-specific optional fields
- final consumer-specific query/response fields
- implementation transport fields
- persistence and indexing directives

## 7. A4 Boundary Reminder

- no schema artifact is created in this task
- no DB model is created in this task
- no API/OpenAPI artifact is created in this task
