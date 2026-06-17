# VANTARIS IBMS Security A0 P0 Remediation Plan

**Task ID:** IBMS-SECURITY-A0  
**Date:** 2026-06-16  
**Baseline Commits:** `af11e46`, `47d2667`, `f4becbb`  
**Related:** [contracts/SECURITY_BOUNDARY.md](../../contracts/SECURITY_BOUNDARY.md), [IBMS_BACKEND_INVENTORY_B2.md](../architecture/IBMS_BACKEND_INVENTORY_B2.md)

---

## 1. Task Scope

| Item | Status |
|---|---|
| Task ID | IBMS-SECURITY-A0 |
| Scope | Documentation-only security remediation plan |
| Runtime code changed | ❌ No |
| Secret moved | ❌ No |
| Service started | ❌ No |
| Dependency installed | ❌ No |
| Git commit | ❌ Not in this task |

This document registers P0 security debt discovered in B2 and defines a phased remediation order. **No remediation is executed in A0.**

---

## 2. Current Critical Findings

| Finding | Severity | Current Area | Risk |
|---|---|---|---|
| Hardcoded DB password | P0 | `src/common/config/default.py`, `src/common/core/database.py` | Credential leakage; repo exposure enables DB access |
| Hardcoded DB host (public IP) | P0 | `default.py` (`140.245.109.223:13306`) | Attack surface enumeration |
| Hardcoded JWT secret | P0 | `default.py` (`JWT_SECRET_KEY`), consumed by `jwt_util.py` | Token forgery; full auth bypass |
| Hardcoded DID private key | P0 | `default.py` (`system_did_private_key`); `main.py` startup | Identity compromise; entity impersonation |
| Private key printed on startup | P0 | `src/main.py` — first system entity creation | One-time key exposure in logs/console |
| Hardcoded MQTT credential | P0 | `default.py` (broker host); `src/testMQTT/*` (`MQTT_PASSWORD = "hexinic"`) | Broker compromise; telemetry spoofing |
| Modeling API JWT not confirmed | P0 | `/api/modeling/*` — no `@jwt_required` in B2 | Public train/predict; resource abuse; data leakage |
| RBAC boundary not confirmed | P0 | `system_api.py` partial; `menu_api.py`, `iot_api.py`, `did_api.py` largely unprotected | Privilege bypass; unauthorized admin/device ops |
| IoT ingest unauthenticated | P0 | `POST /api/iot/ingest/http` | Unvalidated external telemetry injection |
| Device command APIs unprotected | P0 | `/api/iot/device/*/command` | Unauthorized OT-style commands |
| Blockchain RPC hardcoded | P1 | `src/blockchain/config.py` (node URLs, contract address) | Infrastructure coupling; harder rotation |
| Test credential JSON in repo | P1 | `src/tests/credential_*.json` | Sample credentials may aid reconnaissance |
| Simulator routes mixed with production tree | P1 | `src/testMQTT/*`, `mock_isapi_camera.py` | Accidental exposure if run in production |

---

## 3. Immediate Non-Negotiable Rules

Effective immediately for all IBMS development (until remediated):

1. **Do not commit real secrets** — passwords, private keys, JWT secrets, MQTT credentials, or production RPC URLs in source, docs, or examples.
2. **Do not print private keys on startup** — system root entity creation must never log or stdout private key material.
3. **Do not expose modeling/train/predict without JWT/RBAC** — `/api/modeling/*` must not be treated as public API.
4. **Do not expose device command APIs without permission check** — commands require explicit `device:control` (or equivalent) scope.
5. **Do not run simulator routes in production** — `src/testMQTT/*` and standalone mock Flask apps are dev/test only.
6. **Do not let Console directly access DB or Storage credentials** — Console uses Core API only (per A2 matrix).
7. **Do not remediate all secrets in one large change** — one secret domain per SECURITY-A* task with rollback point.

---

## 4. Recommended Remediation Order

Each step is a **separate task** with its own commit, verification, and rollback plan.

| Order | Task | Objective |
|---|---|---|
| 1 | **SECURITY-A1** | Create `.env.example` and secret inventory **without** changing runtime behavior |
| 2 | **SECURITY-A2** | Externalize JWT secret (`IBMS_JWT_SECRET`); remove default from `default.py` |
| 3 | **SECURITY-A3** | Externalize DB connection string (`IBMS_DATABASE_URL` or component vars) |
| 4 | **SECURITY-A4** | Externalize MQTT broker credentials (`IBMS_MQTT_*`) |
| 5 | **SECURITY-A5** | Externalize DID private key; **stop key printing** in `main.py` |
| 6 | **SECURITY-A6** | Protect modeling API with JWT + RBAC (`modeling:train`, `modeling:predict`) |
| 7 | **SECURITY-A7** | Protect device command APIs and ingest with JWT/RBAC + audit |
| 8 | **SECURITY-A8** | Disable simulator routes in production mode (`IBMS_SIMULATOR_ENABLED=false`) |
| 9 | **SECURITY-A9** | Add audit `traceId` for sensitive API boundaries |

**Parallel (non-blocking):**

- **IBMS-CONTRACTS-A1** — OpenAPI security schemes document required auth per route group
- **IBMS-CORE-A0** — Unified auth middleware architecture before broad route changes

---

## 5. Environment Variable Plan

Suggested variable names (values **never** in repo):

| Variable | Purpose | Replaces (current) |
|---|---|---|
| `IBMS_ENV` | `development` \| `staging` \| `production` | — |
| `IBMS_SECRET_KEY` | Flask app secret (if used) | — |
| `IBMS_JWT_SECRET` | JWT signing key | `JWT_SECRET_KEY` in `default.py` |
| `IBMS_DATABASE_URL` | Full SQLAlchemy URI (preferred) | `SQLALCHEMY_DATABASE_URI` construction |
| `IBMS_DB_HOST` | MySQL host | `DB_HOST` |
| `IBMS_DB_PORT` | MySQL port | `DB_PORT` |
| `IBMS_DB_NAME` | Database name | `DB_NAME` |
| `IBMS_DB_USER` | Database user | `DB_USER` |
| `IBMS_DB_PASSWORD` | Database password | `DB_PASSWORD` |
| `IBMS_MQTT_HOST` | MQTT broker host | `MQTT_BROKER_HOST` |
| `IBMS_MQTT_PORT` | MQTT broker port | `MQTT_BROKER_PORT` |
| `IBMS_MQTT_USERNAME` | MQTT username | Hardcoded in simulators/drivers |
| `IBMS_MQTT_PASSWORD` | MQTT password | Hardcoded in simulators |
| `IBMS_DID_PRIVATE_KEY` | System root DID private key | `system_did_private_key` in `default.py` |
| `IBMS_BLOCKCHAIN_RPC_URL` | Primary RPC (or comma-separated list) | `NODE_URLS[0]` |
| `IBMS_BLOCKCHAIN_CHAIN_ID` | Chain ID | `CHAIN_ID` in blockchain config |
| `IBMS_SIMULATOR_ENABLED` | Enable testMQTT/simulators | — (default `false` in production) |
| `IBMS_MODELING_API_ENABLED` | Kill-switch for modeling routes | — (optional guard) |

**`.env.example` rules (SECURITY-A1):**

- Placeholder values only: `change-me`, `your-host`, `0`
- Never copy production values
- Document required vs optional per environment

---

## 6. API Protection Backlog

| API Group | Current Protection | Required Protection | Priority | Notes |
|---|---|---|---|---|
| `/api/did/login` | partial | JWT issuance + rate limit + audit log | P0 | Login endpoint — brute-force risk |
| `/api/did/*` (except login/me) | unknown | JWT + RBAC + audit log | P0 | Entity/VC/VP ops; parent key in body today |
| `/api/did/me` | confirmed | JWT | P0 | Already `@jwt_required` |
| `/api/system/entity-types`, `/permissions`, `/standard-*` | confirmed | JWT + RBAC | P0 | `system_api.py` protected in B2 |
| `/api/system/versions`, `/menus`, `/menu/*` | unknown | JWT + RBAC (admin scope) | P0 | `menu_api.py` — raw SQL, no JWT in B2 |
| `/api/iot/device/register`, CRUD | unknown | JWT + RBAC | P0 | Device lifecycle |
| `/api/iot/ingest/http` | unknown | service identity or device token + rate limit + audit log | P0 | External ingress boundary |
| `/api/iot/device/*/command` | unknown | JWT + RBAC (`device:control`) + audit log | P0 | OT command risk |
| `/api/iot/standard-fields`, `/standard-methods` | unknown | JWT + RBAC | P1 | Schema definitions |
| `/api/iot/device/*/stream` (SSE) | unknown | JWT + rate limit | P0 | Real-time data leak |
| `/api/iot/device/*/latest` | unknown | JWT | P1 | Snapshot access |
| `/api/iot/device/*/test-sse-push` | unknown | disabled in production | P1 | Test-only endpoint |
| `/api/modeling/csv/list`, `/csv/*` | unknown | JWT + RBAC | P1 | Data summary exposure |
| `/api/modeling/*/train` | unknown | JWT + RBAC + audit log | P0 | CPU/resource abuse |
| `/api/modeling/*/predict`, `/predict_future` | unknown | JWT + RBAC | P0 | Inference abuse |
| `/api/modeling/*/model_info` | unknown | JWT + RBAC | P1 | Model metadata |
| `src/testMQTT/*` | not production API | disabled in production | P1 | Simulators; separate process or flag |
| `mock_isapi_camera.py` routes | not production API | disabled in production | P1 | Standalone Flask — not on `api_bp` |

**Legend — Current Protection:**

- **confirmed** — `@jwt_required` observed on all routes in group (B2)
- **partial** — some routes protected or alternate auth (e.g. DID signature)
- **unknown** — no decorator confirmed in B2
- **not production API** — dev/test tooling only

**Legend — Required Protection:**

- **JWT** — Bearer token required
- **RBAC** — Permission check beyond authentication
- **service identity** — mTLS or internal service token for ingress
- **disabled in production** — Route not registered when `IBMS_ENV=production`
- **rate limit** — Per-IP or per-token throttling
- **audit log** — traceId + caller + action recorded

---

## 7. Verification Plan

Each **SECURITY-A1 through A9** task completion **must** return:

| Check | Requirement |
|---|---|
| `git diff --stat` | Shows only intended files for that task |
| Affected files | Listed explicitly in task completion note |
| Secret not printed | No private key/password in stdout, logs, or error messages |
| `.env.example` updated | If new env var introduced (A1+) |
| No real secret committed | `git diff` and staged files reviewed |
| Focused route protection check | Manual or doc note for routes touched (A6–A7) |
| Service startup | **Only when explicitly approved** for that task |

**A0 (this task) verification:**

```bash
git status --short   # new doc only
git diff --stat      # no backend/src changes
```

---

## 8. Forbidden Remediation Pattern

Do **not**:

| Pattern | Reason |
|---|---|
| One large change fixing all secrets | No rollback; high blast radius |
| Delete existing DID / blockchain / MQTT functionality | Business continuity |
| Modify real production credentials in repo | Operational risk |
| Write secrets into `.env.example` | Becomes committed template leak |
| Write secrets into README or contracts examples | Documentation leak |
| Change auth runtime without rollback point | Auth outage risk |
| Change `main.py` before startup mode is confirmed | uWSGI/Flask deployment unknown |
| Rotate production secrets during doc-only tasks | Out of scope for A0–A1 |

---

## 9. Required Follow-up Tasks

| Task | Focus |
|---|---|
| **IBMS-SECURITY-A1** | `.env.example` + secret inventory (no runtime change) |
| **IBMS-SECURITY-A2** | JWT secret externalization |
| **IBMS-SECURITY-A3** | DB connection externalization |
| **IBMS-SECURITY-A4** | MQTT credentials externalization |
| **IBMS-SECURITY-A5** | DID private key externalization + stop key printing |
| **IBMS-SECURITY-A6** | Modeling API JWT/RBAC |
| **IBMS-SECURITY-A7** | Device command + ingest protection |
| **IBMS-SECURITY-A8** | Production simulator disable |
| **IBMS-SECURITY-A9** | Audit traceId on sensitive boundaries |
| **IBMS-CONTRACTS-A1** | OpenAPI `securitySchemes` + per-route auth metadata |
| **IBMS-CORE-A0** | Unified auth middleware design |

---

## 10. No-Code-Change Confirmation

| Check | Result |
|---|---|
| No backend source code was modified | ✅ |
| No frontend source code was modified | ✅ |
| No environment file was modified | ✅ |
| No secret was moved or changed | ✅ |
| No dependency was installed | ✅ |
| No service was started | ✅ |
| Only `docs/security/` documentation added | ✅ |

---

## 11. Related Documents

- [contracts/SECURITY_BOUNDARY.md](../../contracts/SECURITY_BOUNDARY.md)
- [IBMS_BACKEND_INVENTORY_B2.md](../architecture/IBMS_BACKEND_INVENTORY_B2.md)
- [IBMS_FORBIDDEN_ACCESS_MATRIX_A2.md](../architecture/IBMS_FORBIDDEN_ACCESS_MATRIX_A2.md)
- [IBMS_CONTRACTS_A0.md](../architecture/IBMS_CONTRACTS_A0.md)
