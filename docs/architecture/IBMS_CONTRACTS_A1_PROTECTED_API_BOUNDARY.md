# IBMS Contracts A1 Protected API Boundary Completion

**Task ID:** IBMS-CONTRACTS-A1  
**Date:** 2026-06-16  
**Type:** Documentation only — no runtime changes

---

## 1. Task Scope

- Documentation-only contract boundary for currently protected APIs
- No runtime code changed
- No frontend code changed
- No `.env` changed
- No service started

---

## 2. Inputs

| Input | Reference |
|---|---|
| A6 Modeling API JWT protection | `173a0fc` — 7/7 modeling routes |
| A7 IoT write/command/ingest JWT | `9369c8f` — 17 IoT write routes |
| A8 / A8B simulator & SSE test guard | `49ca8a7`, `c941113` |
| A9 audit traceId boundary | `181ff06` — `X-Trace-Id` + sensitive API logging |
| B2 backend inventory | `47d2667` — DID/System route inventory |
| Contracts A0 | `af11e46` — `contracts/API_GROUPS.md`, error/status baselines |

---

## 3. Outputs

| File | Purpose |
|---|---|
| `contracts/PROTECTED_API_BOUNDARY_A1.md` | Authoritative protected-route inventory and auth rules |
| `contracts/examples/protected-api-request-example.md` | Placeholder request examples for integrators |
| `docs/architecture/IBMS_CONTRACTS_A1_PROTECTED_API_BOUNDARY.md` | This completion report |

---

## 4. Current Contract Boundary

```
Client
  │
  ├─► /api/did/login ──► JWT (sub, perms)
  │
  └─► Protected routes
        ├─ Authorization: Bearer <token>  (required)
        ├─ X-Trace-Id: <optional>         (A9 audit)
        │
        ├─ /api/modeling/*                (JWT — A6)
        ├─ /api/iot/* write/command/ingest (JWT — A7)
        ├─ /api/iot/.../test-sse-push     (JWT + prod guard — A8B)
        ├─ /api/did/me                    (JWT — B2)
        └─ /api/system/* admin            (JWT — B2)
```

**Not in protected boundary (documented gaps):**

- Most `/api/did/*` routes except `/me`
- IoT read GET routes (device list, standard dictionaries, SSE stream/latest)
- Public challenge/login endpoints

Fine-grained permission codes are documented as **targets** but not enforced in runtime contract yet.

---

## 5. Pending

- Full OpenAPI generation (`IBMS-CONTRACTS-A1-openapi` or follow-on)
- JSON Schema for modeling / IoT request bodies
- Permission matrix contract aligned with CORE-A0
- Contract tests (HTTP-level auth negative cases)
- DID route protection policy update
- Machine identity / service account tokens

---

## 6. Verification

- No files under `AN_VANTARIS_IBMS-backend/src/` modified
- No files under `AN_VANTARIS_IBMS-main/` modified
- Documentation cross-references A6–A9 security docs

---

## Recommended Next Tasks

1. IBMS-CORE-A0 — unified auth middleware and permission enforcement
2. IBMS-SECURITY-A6B / A7B — fine-grained modeling / IoT permissions
3. OpenAPI spec generation from protected inventory
4. Contract test suite for 401/403 on protected routes
