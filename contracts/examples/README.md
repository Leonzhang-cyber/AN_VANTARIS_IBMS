# IBMS Contract Examples Directory

**Task:** IBMS-CONTRACTS-A0  
**Status:** Naming defined — example JSON deferred to A1

---

## Purpose

本目录存放与 JSON Schema 和 OpenAPI 规范配套的**示例 payload**，供 Console 开发、集成测试和文档生成使用。

示例文件 **不包含真实 secrets、private keys、或 production credentials**。

---

## Naming Rules

```
<domain>.<action>.<direction>.json
```

| Part | Values | Example |
|---|---|---|
| `domain` | `did`, `iot`, `system`, `modeling`, `link`, `error` | `did` |
| `action` | Operation name | `login`, `telemetry.ingest`, `predict` |
| `direction` | `request` or `response` | `request` |

Alternative error examples:

```
error.<error-code>.json
```

---

## Planned Example Files (A1)

### DID / Auth

| File | Description |
|---|---|
| `did.login.request.json` | DID signature login request |
| `did.login.response.json` | JWT token response |
| `did.entity.create.request.json` | Create sub-entity payload |
| `did.entity.create.response.json` | Entity + VC response |

### IoT / Telemetry

| File | Description |
|---|---|
| `iot.telemetry.ingest.request.json` | HTTP ingest payload |
| `iot.telemetry.ingest.response.json` | Ingest acknowledgment |
| `iot.device.register.request.json` | Device registration |
| `iot.command.request.json` | Device command |

### System

| File | Description |
|---|---|
| `system.menu.response.json` | Menu tree response |
| `system.permission.create.request.json` | Permission CRUD |

### Modeling

| File | Description |
|---|---|
| `modeling.predict.request.json` | Single-point prediction input |
| `modeling.predict.response.json` | Prediction result |
| `modeling.train.request.json` | Training job parameters |
| `modeling.predict-future.request.json` | Multi-day forecast input |

### Errors

| File | Description |
|---|---|
| `error.invalid-schema.json` | `INVALID_SCHEMA` example |
| `error.unauthorized.json` | `TOKEN_MISSING` example |
| `error.permission-denied.json` | `PERMISSION_DENIED` example |
| `error.device-not-found.json` | `DEVICE_NOT_FOUND` example |

---

## Example Content Rules

1. Use fictional DIDs, device codes, and trace IDs.
2. Never include real passwords, private keys, or JWT signing secrets.
3. Include `traceId` and `timestamp` on request/response examples where applicable.
4. Mark simulated data with `"telemetryQuality": "simulated"` where relevant.
5. Each example should validate against its corresponding schema in `../schemas/` (A1).

---

## Sample Structure

```json
{
  "traceId": "trace-00000000-0000-4000-8000-000000000001",
  "timestamp": "2026-06-16T12:00:00Z",
  "deviceCode": "HVAC_SIM_001",
  "payload": {}
}
```

---

## Current Contents

This directory currently contains only this README and `.gitkeep`. Example JSON files will be added in **IBMS-CONTRACTS-A1**.
