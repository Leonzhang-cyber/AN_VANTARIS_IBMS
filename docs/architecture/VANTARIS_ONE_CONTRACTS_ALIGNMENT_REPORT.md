# VANTARIS ONE Contracts Alignment Report

## 1. Current Contracts Inventory

Detected contract assets:

- `contracts/` exists
- `contracts/openapi/` exists
- `contracts/schemas/` exists
- `contracts/errors/` exists
- `contracts/status/` exists
- `contracts/tools/` exists
- `contracts/examples/` exists
- key documents:
  - `contracts/README.md`
  - `contracts/ERROR_CODES.md`
  - `contracts/STATUS_CODES.md`
  - `contracts/SECURITY_BOUNDARY.md`
  - `contracts/VERSIONING.md`
  - `contracts/API_GROUPS.md`
  - `contracts/openapi/ibms-protected-api-v1.openapi.yaml`
  - `contracts/openapi/ibms-frontend-api-v1.openapi.yaml`

Not detected as dedicated contract top-level directories:

- `AN_VANTARIS_Contracts/` (missing in current repo)
- `contracts/events/` (missing)
- `contracts/protocols/` (missing)
- `contracts/modules/` (missing)
- `contracts/patches/` (missing)
- `contracts/db/` (missing)
- `contracts/security/` (missing as dedicated subdirectory)

## 2. Missing Contract Areas

Required checks:

- Edge normalized object schema: **MISSING**
- Link envelope schema: **MISSING**
- ACK schema: **MISSING**
- Retry policy schema: **MISSING**
- DLQ schema: **MISSING**
- Route policy schema: **MISSING**
- Module manifest schema: **TO_BE_ALIGNED**
- Patch manifest schema: **MISSING**
- License VC schema: **MISSING**
- DID / VC schema: **PARTIAL**
- CDE schema: **MISSING**
- AI request/response schema: **TO_BE_ALIGNED**
- Error code catalog: **EXISTING**
- Status code catalog: **EXISTING**
- Port/network boundary catalog: **PARTIAL**
- DB schema reference: **PARTIAL**

## 3. Required VANTARIS ONE Contract Structure

Recommended target structure:

```text
AN_VANTARIS_Contracts/
├── README.md
├── VERSION
├── GOVERNANCE.md
├── contract-manifest.json
├── standards/
├── schemas/
│   ├── platform/
│   ├── asset/
│   ├── integration/
│   ├── telemetry/
│   ├── event-alarm/
│   ├── work-management/
│   ├── esg/
│   ├── cde/
│   ├── ai/
│   ├── trust/
│   └── audit/
├── openapi/
├── events/
├── protocols/
├── edge-link/
├── modules/
├── patches/
├── db/
├── security/
├── examples/
└── tools/
```

## 4. Alignment Priority

P0:

- contract-manifest
- versioning policy
- object identity standard
- error/status code
- Edge normalized object
- Link envelope / ACK / DLQ / retry
- module manifest
- patch manifest
- license VC
- CDE base schema
- API namespace policy

P1:

- protocol pack manifest
- AI request/response
- DB schema reference
- audit event
- route policy
- replay request
- trust registry reference

P2:

- generated SDK
- compatibility tests
- formal schema drift checker
- OpenAPI validation pipeline

## 5. Blockers

- `AN_VANTARIS_EDGE` 当前未发现
- `AN_VANTARIS_LINK` 当前未发现
- IoT drivers 当前仍在 backend 内，未来需要抽取
- Contracts 目录当前存在（`contracts/`），但尚未完整对齐为目标 6+1 契约域结构
- 暂不移动 runtime 源码
