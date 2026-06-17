# IBMS Status Codes and State Machines

**Task:** IBMS-CONTRACTS-A0  
**Status:** Baseline state definitions (documentation-only)

---

## 1. Purpose

本文档定义 IBMS 跨模块共享的**状态枚举**与**状态机转移规则基线**。具体 JSON Schema 将在 A1 阶段写入 `contracts/schemas/` 和 `contracts/status/`。

---

## 2. Device Status

| Status | Description | Terminal |
|---|---|---|
| `online` | Device connected and reporting | No |
| `offline` | Device not reachable | No |
| `warning` | Connected with degraded telemetry | No |
| `fault` | Device reported fault condition | No |
| `unknown` | Status not yet determined | No |

**Allowed transitions (baseline):**

```
unknown → online | offline
offline → online
online → warning | fault | offline
warning → online | fault | offline
fault → online | offline
```

---

## 3. Telemetry Quality

| Status | Description |
|---|---|
| `good` | Within expected range and freshness |
| `bad` | Out of range or stale |
| `uncertain` | Partial or interpolated data |
| `simulated` | From testMQTT / simulator source |

> Simulated telemetry **must** be tagged `simulated` and must not enter production alarm pipelines without explicit policy.

---

## 4. Alarm Status

| Status | Description | Terminal |
|---|---|---|
| `new` | Alarm raised, unacknowledged | No |
| `acknowledged` | Operator acknowledged | No |
| `in_progress` | Investigation or remediation active | No |
| `resolved` | Condition cleared | No |
| `closed` | Alarm closed with record | Yes |
| `suppressed` | Temporarily suppressed | No |

**Baseline flow:**

```
new → acknowledged → in_progress → resolved → closed
new → suppressed → acknowledged
any → closed (with audit)
```

---

## 5. Work Order Status

| Status | Description | Terminal |
|---|---|---|
| `open` | Created, unassigned | No |
| `assigned` | Assigned to operator/team | No |
| `in_progress` | Work underway | No |
| `pending_verification` | Awaiting verification | No |
| `completed` | Work done, pending close | No |
| `closed` | Work order closed | Yes |
| `cancelled` | Cancelled with reason | Yes |

**Baseline flow:**

```
open → assigned → in_progress → pending_verification → completed → closed
open → cancelled
assigned → cancelled
```

---

## 6. Modeling Job Status

| Status | Description | Terminal |
|---|---|---|
| `queued` | Job accepted, waiting | No |
| `running` | Training/inference executing | No |
| `completed` | Job finished successfully | Yes |
| `failed` | Job failed with error | Yes |
| `cancelled` | Job cancelled by user/system | Yes |

**Applies to:** `/api/modeling/*/train`, batch predict, future async workers.

---

## 7. Delivery Status (Link-like Module)

| Status | Description | Terminal |
|---|---|---|
| `received` | Message received at ingress | No |
| `validated` | Schema and auth validation passed | No |
| `queued` | Accepted into delivery queue | No |
| `delivered` | Delivered to Core or adapter | No |
| `acknowledged` | Consumer acknowledged | Yes |
| `retrying` | Retry in progress | No |
| `failed` | Delivery failed after retries | Yes |
| `dead_lettered` | Moved to dead-letter queue | Yes |

**Baseline flow:**

```
received → validated → queued → delivered → acknowledged
validated → failed → retrying → delivered | dead_lettered
```

---

## 8. DID / VC Status

| Status | Description | Terminal |
|---|---|---|
| `active` | Valid and usable | No |
| `revoked` | Explicitly revoked | Yes |
| `expired` | Past expiration date | Yes |
| `pending` | Issuance in progress | No |
| `invalid` | Failed validation | Yes |

**VC lifecycle:**

```
pending → active → revoked | expired
pending → invalid
```

---

## 9. Schema Placement (Future A1)

| Domain | Schema file (planned) |
|---|---|
| Device | `schemas/iot.device-status.schema.json` |
| Telemetry | `schemas/iot.telemetry-quality.schema.json` |
| Alarm | `schemas/core.alarm-status.schema.json` |
| Work order | `schemas/core.work-order-status.schema.json` |
| Modeling job | `schemas/modeling.job-status.schema.json` |
| Delivery | `schemas/link.delivery-status.schema.json` |
| VC | `schemas/did.vc-status.schema.json` |

Machine-readable state machine graphs: `contracts/status/*.json` (future).
