# VANTARIS IBMS Forbidden Access Matrix A2

**Task:** IBMS-BOUNDARY-A2  
**Date:** 2026-06-16  
**Status:** Defined

---

## 1. Purpose

本文档定义 VANTARIS IBMS 逻辑模块之间的**允许访问**与**禁止访问**规则，以及审计要求与安全注意事项。适用于当前双包单体阶段及未来物理拆分演进。

---

## 2. Allowed Access Matrix

| From | To | Allowed | Method | Reason |
|---|---|---|---|---|
| Console | Core | **Yes** | HTTPS / JWT | User-facing business API; sole frontend entry point |
| Admin (Human Operator) | Console | **Yes** | HTTPS | User operation via Web UI |
| Core | Data | **Yes** | Repository / ORM | Business persistence through data access layer |
| Core | Storage | **Yes** | Controlled internal service | Attachments, evidence, report files via signed URL policy |
| Core | NexusAI Interface | **Yes** | Internal service call | AI triage, summary, recommendation, RCA orchestration |
| Core | Link-like Module | **Yes** | Internal service / API | Notification intent dispatch, delivery ack |
| Link-like Module | Core | **Yes** | Internal API / service | Validated event/message delivery to business layer |
| Edge Interface | Link-like / Core boundary | **Yes** | Controlled API | Device data ingestion; must pass validation before Core |
| NexusAI Interface | Core | **Yes** | Internal callback | AI results returned to Core for persistence & authorization |
| Core | External notification adapter (via Link) | **Yes** | Adapter protocol | Email / Teams / Webhook / CMMS / SIEM outbound |
| Data | Core (read path) | **Yes** | Repository return | Data layer returns query results to Core callers |
| Storage | Core (metadata) | **Yes** | Internal API | File metadata queries initiated by Core |

---

## 3. Forbidden Access Matrix

| From | To | Forbidden Rule | Reason |
|---|---|---|---|
| Console | DB (direct) | **Forbidden** | Bypasses RBAC, exposes credentials, breaks audit trail |
| Console | Link-like Module (direct) | **Forbidden** | Integration ingress must be server-side; prevents message injection |
| Console | Edge Interface (direct) | **Forbidden** | OT boundary must not be exposed to browser clients |
| Console | NexusAI Interface (direct) | **Forbidden** | AI calls must be orchestrated and authorized by Core |
| Console | Storage (long-lived key) | **Forbidden** | Object storage credentials must never reach client; use short-lived signed URLs only |
| Edge Interface | Business DB (direct) | **Forbidden** | Ingested data must pass Core validation before persistence |
| Link-like Module | Business DB (direct) | **Forbidden** | Messages must be validated and routed through Core business logic |
| Link-like Module | Work Order creation (direct) | **Forbidden** | WO lifecycle owned by Core; Link delivers events only |
| NexusAI Interface | Work Order creation (direct) | **Forbidden** | AI suggestions require human/Core approval before WO creation |
| NexusAI Interface | Business DB (direct) | **Forbidden** | AI results persisted only through Core orchestration |
| Data | Core business process | **Forbidden** | Data layer must not initiate business workflows (create WO, execute rules, send notifications) |
| Storage | Business permission decision | **Forbidden** | Authorization is Core responsibility; Storage executes authorized operations only |
| NexusAI Interface | Storage (long-lived key) | **Forbidden** | AI module uses Core-mediated short-lived URLs |
| Edge Interface | OT device control (real PLC) | **Forbidden** | Current Edge Interface is ingest-only; no real OT control |
| Any module | `.env` / secrets (direct read by Console) | **Forbidden** | Secrets confined to server-side configuration |
| Contracts | Any runtime system (DB/API) | **Forbidden** | Contracts is documentation-only; no runtime connections |

---

## 4. Audit Requirements

The following cross-module boundaries **must** record structured audit entries containing at minimum:

- `traceId` — distributed trace identifier
- `caller` — originating module / service identity / user ID
- `target` — destination module / endpoint / resource
- `result` — success / failure / partial
- `latency` — request duration in milliseconds
- `errorReason` — error code and sanitized message (if failed)

### 4.1 Mandatory Audit Boundaries

| Boundary | Audit Fields Required | Retention |
|---|---|---|
| Console → Core | traceId, caller (userId), target (API path), result, latency, errorReason | ≥ 90 days |
| Edge Interface → Link-like / Core boundary | traceId, caller (edgeId), target, result, latency, errorReason, payload hash | ≥ 180 days |
| Link-like Module → Core | traceId, caller (linkServiceId), target, result, latency, errorReason, messageId | ≥ 180 days |
| Core → Data | traceId, caller (coreServiceId), target (table/operation), result, latency, errorReason | ≥ 90 days |
| Core → Storage | traceId, caller, target (bucket/object), result, latency, errorReason, operation (upload/download/delete) | ≥ 365 days |
| Core → NexusAI Interface | traceId, caller, target (AI operation type), result, latency, errorReason, modelVersion | ≥ 90 days |
| Core → external notification adapter | traceId, caller, target (adapter/channel), result, latency, errorReason, recipient (masked) | ≥ 365 days |

### 4.2 High-Risk Operation Audit (Before/After)

The following operations require **before/after state snapshots** in addition to standard audit fields:

- User role / permission changes
- Auth configuration changes
- Database schema migration execution
- File upload / download / delete
- Report export
- AI triage result applied to alarm/event
- Work order status transitions
- Edge device registration / deregistration

---

## 5. Security Notes

### 5.1 Authentication & Authorization

- All user requests **must** pass through JWT validation and RBAC enforcement at the Core boundary.
- Console **must not** store refresh tokens in localStorage without encryption; prefer httpOnly cookies where applicable.
- Token expiry and refresh rotation policies are owned by Core.

### 5.2 Service Identity

- All inter-module service calls **must** carry a service identity (service account / mTLS cert / internal JWT).
- Service identities **must** be scoped to minimum required permissions per module.
- Future physical split **must** enforce service identity at network boundary (not just application layer).

### 5.3 Export / Upload / Download Audit

- Every file upload, download, and export operation **must** produce an audit record.
- Signed URLs **must** be short-lived (recommended: ≤ 15 minutes for download, ≤ 5 minutes for upload).
- Download URLs **must not** be reusable after expiry.

### 5.4 High-Risk Operations

- Operations affecting auth, RBAC, schema, or OT boundaries **must** record before/after state.
- Multi-step destructive operations **must** require confirmation and produce immutable audit entries.

### 5.5 Error Information Disclosure

- Error responses **must not** leak:
  - Database credentials or connection strings
  - Raw SQL statements
  - Internal file system paths
  - Stack traces (in production)
  - API keys, MinIO secrets, or JWT signing keys
- Production error messages **must** use standardized error codes from `contracts/errors/` (future).

### 5.6 Network Segmentation (Future)

When physically split:

| Zone | Modules | Exposure |
|---|---|---|
| DMZ / Edge Zone | Edge Interface, Link ingress | External-facing, hardened |
| Application Zone | Core, NexusAI Interface | Internal only |
| Data Zone | Data, Storage, PostgreSQL, Redis, MinIO | Internal only, no direct external access |
| Client Zone | Console (static) | Public HTTPS only |

---

## 6. Enforcement Stages

| Stage | Enforcement Mechanism |
|---|---|
| **Current (A0–A3)** | Documentation + code review checklist |
| **IBMS-CORE-A0** | Core middleware: JWT/RBAC gate on all routes |
| **IBMS-CONTRACTS-A0** | OpenAPI + JSON Schema validation at boundaries |
| **Physical split** | Network policy + mTLS + service identity tokens |

---

## 7. Related Documents

- [IBMS_LOGICAL_MODULE_BOUNDARY_A2.md](./IBMS_LOGICAL_MODULE_BOUNDARY_A2.md)
- [IBMS_MODULAR_BOUNDARY_A0.md](./IBMS_MODULAR_BOUNDARY_A0.md)
- [IBMS_DEPLOYMENT_MODES_A3.md](./IBMS_DEPLOYMENT_MODES_A3.md)
