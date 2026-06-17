# VANTARIS IBMS Contracts A0 Completion Note

**Task ID:** IBMS-CONTRACTS-A0  
**Date:** 2026-06-16  
**Baseline Commits:** `47d2667`, `f4becbb`  
**Status:** Complete (documentation-only — not committed)

---

## 1. Task Scope

| Item | Value |
|---|---|
| Task | Define IBMS contracts naming, API groups, versioning, and security boundary |
| Scope | `contracts/**`, `docs/architecture/IBMS_CONTRACTS_A0.md` |
| OpenAPI generation | ❌ Not in scope (deferred to A1) |
| Business code changes | ❌ None |
| Dependency install | ❌ None |
| Service execution | ❌ None |
| Git commit | ❌ Not in this task |

---

## 2. Files Created / Updated

| # | File | Action |
|---|---|---|
| 1 | `contracts/README.md` | Updated |
| 2 | `contracts/VERSIONING.md` | Created |
| 3 | `contracts/API_GROUPS.md` | Created |
| 4 | `contracts/ERROR_CODES.md` | Created |
| 5 | `contracts/STATUS_CODES.md` | Created |
| 6 | `contracts/SECURITY_BOUNDARY.md` | Created |
| 7 | `contracts/schemas/README.md` | Created |
| 8 | `contracts/openapi/README.md` | Created |
| 9 | `contracts/examples/README.md` | Created |
| 10 | `docs/architecture/IBMS_CONTRACTS_A0.md` | Created (this file) |

Existing placeholder directories retained: `contracts/errors/`, `contracts/status/` (`.gitkeep`).

---

## 3. API Groups Recognized from B2

| Group | Prefix | Routes (approx.) | Module |
|---|---|---|---|
| DID API | `/api/did/*` | 17 | Core / Security |
| System API | `/api/system/*` | 35+ | Core / Administration |
| IoT API | `/api/iot/*` | 24 | Link-like / Edge / Core |
| SSE / Streaming | `/api/iot/device/*/stream`, `/latest` | 4 | Link-like |
| Data Modeling API | `/api/modeling/*` | 7 | NexusAI Interface |
| Simulator / testMQTT | `src/testMQTT/*` | Dev-only | Edge Simulator |

Detail: [contracts/API_GROUPS.md](../../contracts/API_GROUPS.md)

---

## 4. Versioning Policy Summary

| Format | Example |
|---|---|
| Contract version | `ibms.contract.v1` |
| API path (target) | `/api/v1/did/login` |
| Schema ID | `ibms.did.login-request.v1` |

Breaking vs non-breaking change rules defined in [contracts/VERSIONING.md](../../contracts/VERSIONING.md).

Required schema fields: `schemaVersion`, `traceId` (where applicable), `timestamp` (where applicable).

---

## 5. Error / Status Baseline

### Error Codes

- General: `INVALID_REQUEST`, `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`, etc.
- Auth: `TOKEN_MISSING`, `TOKEN_INVALID`, `PERMISSION_DENIED`, `RBAC_SCOPE_DENIED`
- Domain-specific: IoT, DID/Blockchain, AI/Modeling, Storage

Standard error response envelope defined in [contracts/ERROR_CODES.md](../../contracts/ERROR_CODES.md).

### Status Machines

- Device, telemetry quality, alarm, work order, modeling job, delivery, DID/VC statuses

Defined in [contracts/STATUS_CODES.md](../../contracts/STATUS_CODES.md).

---

## 6. Security Boundary Notes

P0 findings from B2 recorded (not remediated):

- Hardcoded DB password, JWT secret, DID private key, MQTT credentials
- Modeling API without confirmed JWT protection
- RBAC boundary not fully confirmed
- Private key printed on startup

Future mandatory rules and audit field requirements: [contracts/SECURITY_BOUNDARY.md](../../contracts/SECURITY_BOUNDARY.md)

Remediation tracked under **IBMS-SECURITY-A0**.

---

## 7. No-Code-Change Confirmation

| Check | Result |
|---|---|
| `AN_VANTARIS_IBMS-backend/src/**` modified | ❌ No |
| `AN_VANTARIS_IBMS-main/**` modified | ❌ No |
| `requirements.txt` modified | ❌ No |
| `.env` / secrets in runtime config modified | ❌ No |
| JWT / auth / DID / blockchain / MQTT logic modified | ❌ No |
| Dependencies installed | ❌ No |
| Backend / tests / migration executed | ❌ No |
| Full OpenAPI YAML generated | ❌ No (A1) |
| Only `contracts/**` and `docs/architecture/**` touched | ✅ Yes |

---

## 8. Recommended Next Tasks

| Priority | Task | Description |
|---|---|---|
| 1 | **IBMS-CONTRACTS-A1** | Draft OpenAPI stubs + JSON Schema for DID, System, IoT, Modeling groups |
| 2 | **IBMS-SECURITY-A0** | P0 remediation plan for hardcoded secrets and unprotected routes |
| 3 | **IBMS-DATA-A0** | Data Repository interface; isolate raw SQL in menu_api |
| 4 | **IBMS-CORE-A0** | Unified JWT/RBAC middleware; close auth gaps on IoT/modeling/menu |

**Deferred:**

- IBMS-CONSOLE-A0 (awaiting final frontend package)
- IBMS-LINK-B0 / IBMS-EDGE-INTERFACE-B0 (after Core auth baseline)

---

## 9. Document Index

```
contracts/
├── README.md
├── VERSIONING.md
├── API_GROUPS.md
├── ERROR_CODES.md
├── STATUS_CODES.md
├── SECURITY_BOUNDARY.md
├── schemas/README.md
├── openapi/README.md
├── examples/README.md
├── errors/.gitkeep
└── status/.gitkeep

docs/architecture/
└── IBMS_CONTRACTS_A0.md
```

---

## 10. Related Documents

- [IBMS_BACKEND_INVENTORY_B2.md](./IBMS_BACKEND_INVENTORY_B2.md)
- [IBMS_LOGICAL_MODULE_BOUNDARY_A2.md](./IBMS_LOGICAL_MODULE_BOUNDARY_A2.md)
- [IBMS_FORBIDDEN_ACCESS_MATRIX_A2.md](./IBMS_FORBIDDEN_ACCESS_MATRIX_A2.md)
- [IBMS_WORKSPACE_B1_BASELINE.md](./IBMS_WORKSPACE_B1_BASELINE.md)
