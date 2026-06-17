# IBMS Security Boundary Contract

**Task:** IBMS-CONTRACTS-A0  
**Status:** Baseline defined (documentation-only — no runtime changes)

---

## 1. Current Critical Findings from B2

The following issues were identified in read-only backend inventory B2. **This task does not remediate them** — they are recorded as **P0 security remediation backlog**.

| Finding | Location | Severity |
|---|---|---|
| Hardcoded DB password | `src/common/config/default.py` | **P0** |
| Hardcoded DB host (public IP) | `src/common/config/default.py` | **P0** |
| Hardcoded JWT secret | `src/common/config/default.py` (`your-secret-key-change-in-production`) | **P0** |
| Hardcoded DID private key | `src/common/config/default.py` | **P0** |
| Hardcoded MQTT broker + credentials | `default.py`, `src/testMQTT/*` (`hexinic`) | **P0** |
| Modeling API JWT protection not confirmed | `src/api/data_modeling/modeling_api.py` — no `@jwt_required` | **P0** |
| RBAC boundary not fully confirmed | IoT, menu, most DID routes unprotected | **P0** |
| Private key printed on startup | `src/main.py` — system root entity first creation | **P0** |
| Test credential JSON in repo | `src/tests/credential_*.json` | **P1** |
| Blockchain node URLs hardcoded | `src/blockchain/config.py` | **P1** |

---

## 2. Current A0 Rule

| Rule | Applies |
|---|---|
| Do **not** modify secrets, auth, JWT, DID, blockchain, or MQTT runtime logic in CONTRACTS-A0 | ✅ |
| Do **not** change `.env`, database config, or `requirements.txt` | ✅ |
| Record findings only; remediation tracked under **IBMS-SECURITY-A0** | ✅ |

---

## 3. Mandatory Future Rules

### 3.1 Secrets Management

- All secrets **must** move to environment variables or a secret manager.
- No passwords, private keys, or JWT secrets in source code.
- `.env` files **must not** be committed; use `.env.example` with placeholder values only.

### 3.2 Authentication & Authorization

- All protected APIs **must** use JWT + RBAC via Core middleware.
- `@jwt_required` alone is insufficient — route-level permission checks required.
- `verify_api_permission()` must be applied consistently (currently defined but underused).

### 3.3 API Exposure

| API Group | Rule |
|---|---|
| Modeling train/predict | **Must not** be public — JWT + `modeling:*` permission |
| Device command | **Must** require explicit `device:control` (or equivalent) permission |
| IoT ingest | **Must** validate device identity at Link boundary before Core |
| Menu/version admin | **Must** require admin RBAC scope |
| DID entity creation | **Must** require parent authorization + audit |

### 3.4 Runtime Isolation

- **Simulator routes** (`src/testMQTT/*`) **must not** run in production.
- Mock ISAPI Flask app is dev/test tooling only.
- Production Edge agents connect via controlled Link ingress — not simulator endpoints.

### 3.5 Data & Artifacts

- Model artifacts (`*.pkl`) **must not** be committed to git.
- Large CSV/MP4 samples remain gitignored.
- Console **must not** hold long-lived storage keys (per A2 matrix).

### 3.6 Audit & Traceability

- All exports, uploads, and downloads **must** be audited.
- `traceId` **required** on sensitive cross-module boundaries (see §4).

---

## 4. Required Audit Fields

Every audited cross-module operation **must** record:

| Field | Type | Description |
|---|---|---|
| `traceId` | string | Distributed trace identifier |
| `caller` | string | User DID, service identity, or edge node ID |
| `target` | string | API path, resource ID, or module name |
| `action` | string | HTTP method + operation (e.g. `POST /modeling/train`) |
| `result` | string | `success` \| `failure` \| `partial` |
| `latencyMs` | number | Request duration in milliseconds |
| `errorCode` | string | From `ERROR_CODES.md` if failed |
| `timestamp` | string (ISO 8601 UTC) | Event time |
| `sourceIp` | string | Client IP where available |

### Mandatory Audit Boundaries (from A2)

- Console → Core
- Edge Interface → Link-like / Core boundary
- Link-like → Core
- Core → Data
- Core → Storage
- Core → NexusAI Interface
- Core → external notification adapter

High-risk operations (auth change, role change, migration, file upload/download, WO transition) **must** include before/after state snapshots.

---

## 5. Error Disclosure Rules

Production error responses **must not** leak:

- Database credentials or connection strings
- Raw SQL statements
- Internal file system paths
- Stack traces
- API keys, MinIO secrets, JWT signing keys, DID private keys

Use standardized codes from `contracts/ERROR_CODES.md`.

---

## 6. Network & Module Boundaries (Target State)

| From | To | Allowed | Contract Reference |
|---|---|---|---|
| Console | Core API | Yes | `ibms-core-api.openapi.yaml` (future) |
| Console | IoT ingest / Modeling | **No** | A2 forbidden matrix |
| Link ingress | Core | Yes (validated) | `ibms.link.message.v1` |
| NexusAI | Business DB direct | **No** | Core orchestration only |
| Simulator | Production DB | **No** | Dev isolation |

---

## 7. Remediation Backlog Reference

| Task | Scope |
|---|---|
| **IBMS-SECURITY-A0** | P0 findings remediation plan |
| **IBMS-CORE-A0** | Unified auth middleware |
| **IBMS-CONTRACTS-A1** | OpenAPI security schemes (Bearer JWT) |

---

## 8. Related Documents

- [ERROR_CODES.md](./ERROR_CODES.md)
- [API_GROUPS.md](./API_GROUPS.md)
- `docs/architecture/IBMS_FORBIDDEN_ACCESS_MATRIX_A2.md`
- `docs/architecture/IBMS_BACKEND_INVENTORY_B2.md`
