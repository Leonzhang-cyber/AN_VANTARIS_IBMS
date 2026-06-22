# Contract Validation Baseline v1

## 1. Purpose

Define baseline validation expectations for `AN_VANTARIS_Contracts` authority integrity and generated consumer placeholder safety.

## 2. Validation scripts

- `AN_VANTARIS_Contracts/scripts/validate-contracts.sh`
- `AN_VANTARIS_Contracts/scripts/contract-drift-scan.sh`

## 3. Hard fail conditions

- invalid JSON in any `AN_VANTARIS_Contracts/*.json`
- missing authority metadata files
- missing required contracts directories
- missing P0 schemas/OpenAPI/examples
- missing required engineer handoff docs
- runtime package import leakage in Contracts authority
- fake secret patterns in `dto-examples`
- missing required generated consumer directories
- missing generated contracts README banner for EDGE/LINK consumer trees

## 4. Warning-only conditions

- potential DB implementation leakage terms detected in contract schemas
- generated placeholder README missing in protocol/security generated trees

## 5. P0 authority file baseline

- wire event schema
- machine identity ref schema
- signature headers schema
- signed handoff envelope schema
- edge handoff event schema
- delivery ack schema
- EDGE->LINK OpenAPI
- P0 DTO examples
- engineer handoff core docs

## 5A. P1 canonical schema baseline

- common schema baseline:
  - `common-identifiers-v1.schema.json`
  - `common-trace-context-v1.schema.json`
  - `common-audit-fields-v1.schema.json`
  - `common-health-status-v1.schema.json`
- canonical object schema baseline:
  - tenant/site/building/floor/space
  - gateway/connector/source-system
  - asset/device/point/telemetry
  - event/alarm/evidence/health/throughput
  - sync-batch/audit/config-version
- canonical example baseline under `dto-examples/canonical/` (20 files)

## 5B. P1B DB mapping YAML baseline

- required DB mapping files:
  - `AN_VANTARIS_Contracts/db/canonical-to-db-map.v1.yaml`
  - `AN_VANTARIS_Contracts/db/field-type-mapping.v1.yaml`
  - `AN_VANTARIS_Contracts/db/migration-metadata-contract.v1.yaml`
  - `AN_VANTARIS_Contracts/db/DB_MAPPING_README_V1.md`
- baseline text markers:
  - `schemaVersion`
  - `contractVersion`
  - `canonicalObjectMappings` (canonical-to-db map)
  - `EDGE/LINK must not direct-write UFMS DB` policy statement

## 5C. P1C reliability baseline

- retry/DLQ/replay schema baseline:
  - `link-delivery-attempt-v1.schema.json`
  - `link-retry-policy-v1.schema.json`
  - `link-dlq-item-v1.schema.json`
  - `link-replay-request-v1.schema.json`
  - `link-replay-result-v1.schema.json`
  - `link-delivery-batch-v1.schema.json`
  - `link-partition-state-v1.schema.json`
- reliability examples baseline:
  - `dto-examples/reliability/link-delivery-attempt.example.json`
  - `dto-examples/reliability/link-retry-policy.example.json`
  - `dto-examples/reliability/link-dlq-item.example.json`
  - `dto-examples/reliability/link-replay-request.example.json`
  - `dto-examples/reliability/link-replay-result.example.json`
  - `dto-examples/reliability/link-delivery-batch.example.json`
  - `dto-examples/reliability/link-partition-state.example.json`
- reliability docs baseline:
  - `versions/link-reliability-profile-v1.md`
  - `openapi/link-reliability.openapi.yaml`
  - `engineering-handoff/LINK_RELIABILITY_ENGINEER_GUIDE_V1.md`

## 5D. P1D semantic example validation baseline

- script baseline:
  - `AN_VANTARIS_Contracts/scripts/validate-schema-examples.py`
- current semantic validation scope:
  - JSON parse for mapped schemas and examples
  - required top-level fields exist in mapped examples
  - required fields must be non-null
  - top-level object type check when schema declares `type: object`
  - secret marker scan in examples
- mapping groups:
  - P0 examples to P0 schemas
  - canonical examples to canonical schemas
  - reliability examples to reliability schemas

## 5E. Product naming normalization baseline

- Contracts authority naming is VANTARIS ONE-first and product-profile aware.
- Hard-block terms in Contracts authority:
  - Forbidden external product package/path aliases and task-family markers defined in `validate-contracts.sh`.
- Soft-allowed future profile terms:
  - Future product profile terms are allowed only in explicit naming-policy allowlist contexts.
- UFMS naming is used for UFMS product-profile semantics and UFMS-specific integration boundaries.

## 6. Generated consumer baseline

- Required placeholder trees:
  - `AN_VANTARIS_EDGE/src/generated/{contracts,protocol,security}`
  - `AN_VANTARIS_LINK/src/generated/{contracts,protocol,security}`
- Contracts consumer README files require banner:
  `AUTO-GENERATED FROM AN_VANTARIS_Contracts. DO NOT EDIT.`

## 7. Known acceptable current limitations

- generated consumer trees are README-only placeholders
- LINK runtime import gate still pending
- semantic schema-to-example validation still pending
- YAML structural validation is currently text-based only
- reliability semantic workflow validation is pending runtime dry-run
- no full JSON Schema semantic validation engine (stdlib-only mode)
- no OpenAPI parser validation
- no product-name contextual NLP validation (regex allowlist/blocklist only)
- no formal IEC certification evidence workflow automation yet

## 8. Next validation evolution

- JSON Schema semantic validation against examples
- OpenAPI parser validation
- generated TS/Python consumer diff
- contract version compatibility enforcement
- YAML semantic validator for DB mapping contracts
- DB migration drift validator against contract milestones
- optional `jsonschema`-based deep validation when package policy approves dependency
- runtime dry-run validation for reliability workflows
- richer naming policy parser for future-profile context validation

## 5F. IEC 62443 aligned security baseline

- required security baseline files:
  - `security/iec62443-security-baseline.v1.md`
  - `security/auditability-contract.v1.md`
  - `security/industrial-safety-cyber-boundary.v1.md`
  - `security/security-traceability-matrix.v1.md`
  - `security/deployment-profile-security-baseline.v1.md`
- governance/manifest baseline additions:
  - security baseline governance statements in `GOVERNANCE.md`
  - security metadata fields in `contract-manifest.json`
- certification wording guard:
  - hard-fail forbidden phrases that imply formal certification
  - allow wording such as "IEC 62443 aligned" and "certification-ready"
- certification evidence-pack linter and traceability completeness checks
