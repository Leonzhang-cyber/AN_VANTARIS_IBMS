# VANTARIS ONE Rebrand Phase Plan

## Phase R0 — Docs-only brand alignment

允许：

- README
- docs title
- architecture docs
- product description
- menu display proposal
- no runtime source change

## Phase R1 — Root documentation and platform metadata

允许：

- top-level README
- product metadata docs
- no runtime rename
- no API change
- no DB change

## Phase R2 — Contracts baseline completion

必须先完成：

- contract-manifest
- versioning policy
- API namespace policy
- Edge normalized object schema
- Link envelope / ACK / Retry / DLQ
- module manifest
- patch manifest
- license VC
- CDE base schema

## Phase R3 — Source package extraction planning

包括：

- EDGE-SOURCE-AUDIT
- CODE-MODULE-A0
- DB-SCHEMA-BASELINE
- CONSOLE-MODULE-A0
- NEXUSAI-A0

## Phase R4 — Runtime package migration

严格分开：

- EDGE extraction commit
- Code module extraction commit
- Console extraction commit
- DB schema commit
- Contracts generated artifact commit

## Phase R5 — API namespace introduction

新增：

- `/api/v1/platform/*`
- `/api/v1/ibms/*`
- `/api/v1/assets/*`
- `/api/v1/integration/*`
- `/api/v1/events/*`
- `/api/v1/mms/*`
- `/api/v1/esg/*`
- `/api/v1/cde/*`
- `/api/v1/ai/*`

保留 legacy compatibility。

## Phase R6 — Deployment package alignment

服务名、安装包、systemd/docker、backup/restore、ports。

## Phase R7 — Legacy deprecation

只有 GA owner 批准后才能删除 legacy。
