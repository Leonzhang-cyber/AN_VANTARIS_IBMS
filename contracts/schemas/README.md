# IBMS JSON Schema Directory

**Task:** IBMS-CONTRACTS-A0  
**Status:** Naming rules defined — schema files deferred to A1

---

## Purpose

本目录存放 IBMS 跨模块 JSON Schema 定义。每个 schema 对应一个 `$id`（见 [VERSIONING.md](../VERSIONING.md)）并归属一个逻辑模块。

---

## Naming Rules

```
<domain>.<object>.schema.json
```

| Part | Description | Examples |
|---|---|---|
| `domain` | Contracts domain prefix | `did`, `iot`, `system`, `modeling`, `link`, `storage`, `error` |
| `object` | Entity or payload type | `entity`, `login-request`, `telemetry`, `menu` |
| `schema.json` | Fixed suffix | — |

---

## Planned Schema Files (A1)

### DID / Security

| File | Schema ID |
|---|---|
| `did.entity.schema.json` | `ibms.did.entity.v1` |
| `did.login-request.schema.json` | `ibms.did.login-request.v1` |
| `did.login-response.schema.json` | `ibms.did.login-response.v1` |
| `did.vc.schema.json` | `ibms.did.vc.v1` |
| `did.vp.schema.json` | `ibms.did.vp.v1` |

### IoT / Link-like

| File | Schema ID |
|---|---|
| `iot.device.schema.json` | `ibms.iot.device.v1` |
| `iot.telemetry.schema.json` | `ibms.iot.telemetry.v1` |
| `iot.command-request.schema.json` | `ibms.iot.command-request.v1` |
| `iot.command-response.schema.json` | `ibms.iot.command-response.v1` |
| `link.message.schema.json` | `ibms.link.message.v1` |

### System / Core

| File | Schema ID |
|---|---|
| `system.menu.schema.json` | `ibms.system.menu.v1` |
| `system.permission.schema.json` | `ibms.system.permission.v1` |
| `system.entity-type.schema.json` | `ibms.system.entity-type.v1` |

### NexusAI / Modeling

| File | Schema ID |
|---|---|
| `modeling.prediction-request.schema.json` | `ibms.modeling.prediction-request.v1` |
| `modeling.prediction-response.schema.json` | `ibms.modeling.prediction-response.v1` |
| `modeling.train-request.schema.json` | `ibms.modeling.train-request.v1` |
| `modeling.job-status.schema.json` | `ibms.modeling.job-status.v1` |

### Cross-cutting

| File | Schema ID |
|---|---|
| `error-response.schema.json` | `ibms.error.response.v1` |
| `audit-record.schema.json` | `ibms.audit.record.v1` |

---

## Required Schema Properties

Every schema file **must** include:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ibms.did.entity.v1",
  "schemaVersion": "ibms.did.entity.v1",
  "title": "DID Entity",
  "description": "Core identity entity object",
  "type": "object",
  "properties": {}
}
```

Request/response payloads should include `traceId` and `timestamp` where applicable (see VERSIONING.md).

---

## Module Ownership

| Domain prefix | Logical module |
|---|---|
| `did.*` | Core / Security |
| `system.*` | Core |
| `iot.*` | Link-like / Edge Interface |
| `modeling.*` | NexusAI Interface |
| `link.*` | Link-like Module |
| `storage.*` | Storage |
| `error.*`, `audit.*` | Contracts (cross-cutting) |

---

## Current Contents

This directory currently contains only this README. Schema JSON files will be added in **IBMS-CONTRACTS-A1**.
