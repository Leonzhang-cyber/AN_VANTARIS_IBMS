# VANTARIS IBMS Protected API Boundary A1

**Task:** IBMS-CONTRACTS-A1  
**Status:** Documentation boundary — not a full OpenAPI specification  
**Latest security commits:** A6B/A7B/A10B (permission enforcement), CONTRACTS-A3 (403 sync), MENU-JWT (`56234d8`)

---

## 1. Scope

This document records the **currently protected API boundary** as implemented in the backend. It is a contract-oriented inventory for integrators and security reviewers — **not** a complete OpenAPI spec, JSON Schema catalog, or permission matrix.

Unlisted routes may exist and may be unprotected. See [Pending Contract Work](#7-pending-contract-work).

---

## 2. Protected API Groups

| API Group | Path Pattern | Protection | Notes |
|---|---|---|---|
| Modeling API | `/api/modeling/*` | Bearer JWT + permission (A6B) | All 7 routes — 403 if missing `modeling:*` codes |
| IoT write / command / ingest | `/api/iot/device/register`, PUT/PATCH/DELETE device, command, ingest, standard-field/method writes, reconnect | Bearer JWT + permission (A7B) | 17 routes — 403 if missing `device:*` / `iot:*` codes |
| SSE test endpoint | `/api/iot/device/<device_code>/test-sse-push` | JWT + production guard + feature flags (A8B) | 403 in production or without flags; no permission decorator |
| DID session / high-risk | `/api/did/me`, `/api/did/system/init`, `/api/did/entity`, `/api/did/vp/generate`, `/api/did/vc/reissue`, `/api/did/vc/revoke` | Bearer JWT; A10B permission on 5 POST routes | `/did/me` JWT only; high-risk POST 403 without `did:*` / `system:admin` |
| System admin (`system_api.py`) | `/api/system/entity-types`, permissions, standard-fields/methods | Bearer JWT (B2) | Permission enforcement pending (SYSTEM-B) |
| System menu (`menu_api.py`) | `/api/system/versions`, `/api/system/menus*`, `/api/system/menu/*`, `/api/system/version-menus/*` | Bearer JWT (MENU-JWT, 19 routes) | JWT enforced; `system:*` permission **pending**; frontend token compatibility **pending** |
| Public auth | `/api/did/login`, `/api/did/challenge` | **Not** JWT-protected | Issues JWT via login |

---

## 3. Authentication Rule

- Protected APIs require `Authorization: Bearer <token>`.
- JWT is issued by the existing `/api/did/login` flow (challenge + signature); payload includes `sub` (DID) and `perms` — **payload format unchanged** by A6–A9.
- Machine / service identity refinement is **pending** a later phase.
- Fine-grained RBAC enforced on modeling (A6B), IoT write (A7B), DID high-risk POST (A10B) via `permission_util`.
- Invalid or missing token returns HTTP **401** (`jwt_required`).
- Valid JWT but missing required permission returns HTTP **403** (`Result.error`, message e.g. `Permission denied: requires [modeling:train]`).

---

## 4. Headers

| Header | Required | Description |
|---|---|---|
| `Authorization` | Yes (protected routes) | `Bearer <jwt-token>` from `/api/did/login` |
| `X-Trace-Id` | Optional | Client-supplied correlation id; server generates UUID if absent (A9 audit) |
| `Content-Type` | Yes (JSON bodies) | `application/json` for POST/PUT/PATCH with body |

---

## 5. Error Behavior

Protected routes follow **existing runtime behavior**:

| Condition | Typical HTTP | Body style |
|---|---|---|
| Missing / invalid `Authorization` | **401** | `Result.error(message="Missing or invalid Authorization header")` or token errors |
| Expired JWT | **401** | `Result.error(message="Token has expired")` |
| Invalid JWT | **401** | `Result.error(message="Invalid token")` |
| Valid JWT, missing required permission | **403** | `Result.error(message="Permission denied: requires [...]", code=403)` |
| SSE test in production | **403** | `Result.error(message="SSE test endpoint disabled in production", code=403)` |
| SSE test without feature flag | **403** | `Result.error` with feature-flag message |

**401 vs 403 boundary (CONTRACTS-A3):**

- **401** — authentication failure (no token, bad token, expired token).
- **403** — authenticated but forbidden (missing permission code, or environment guard such as production SSE disable).

This document does **not** define a new unified error envelope. See `contracts/ERROR_CODES.md` and `contracts/STATUS_CODES.md` for A0 baseline.

---

## 6. Protected Route Inventory

### 6.1 Modeling API (A6 — all routes JWT)

| Route | Method |
|---|---|
| `/api/modeling/csv/list` | GET |
| `/api/modeling/csv/<device_code>` | GET |
| `/api/modeling/<device_code>/train` | POST |
| `/api/modeling/<device_code>/predict` | POST |
| `/api/modeling/<device_code>/predict_future` | POST |
| `/api/modeling/<device_code>/model_info` | GET |
| `/api/modeling/<device_code>/<method>` | GET, POST |

**A9 audit trace:** train, predict, predict_future.

### 6.2 IoT API — protected write / command / ingest (A7)

| Route | Method |
|---|---|
| `/api/iot/device/register` | POST |
| `/api/iot/device/did/<device_did>` | PUT, PATCH, DELETE |
| `/api/iot/device/did/<device_did>/status` | PUT |
| `/api/iot/device/did/<device_did>/field-mappings` | PUT |
| `/api/iot/device/did/<device_did>/method-mappings` | PUT |
| `/api/iot/device/<device_did>/command` | POST |
| `/api/iot/device/code/<device_code>/command` | POST |
| `/api/iot/ingest/http` | POST |
| `/api/iot/device/<device_code>/reconnect` | POST |
| `/api/iot/standard-fields` | POST |
| `/api/iot/standard-fields/<field_code>` | PUT, DELETE |
| `/api/iot/standard-methods` | POST |
| `/api/iot/standard-methods/<method_code>` | PUT, DELETE |

**A9 audit trace:** register, update, patch, delete, command (both), ingest, standard field/method writes.

**A7 intentionally unprotected (read):** device GET queries, standard dictionary GET, mapping-info GET, SSE `/stream` and `/latest`.

### 6.3 SSE test endpoint (A8B)

| Route | Method | Guard |
|---|---|---|
| `/api/iot/device/<device_code>/test-sse-push` | POST | JWT + production disabled + `IBMS_SIMULATOR_ENABLED` or `IBMS_TESTMQTT_ENABLED` in non-production |

### 6.4 DID API (A10 + 898f99c — high-risk JWT)

| Route | Method | Handler | Protected |
|---|---|---|---|
| `/api/did/me` | GET | `get_current_user_info` | Yes (pre-A10) |
| `/api/did/system/init` | POST | `init_system` | Yes (A10) |
| `/api/did/entity` | POST | `create_entity` | Yes (A10) |
| `/api/did/vp/generate` | POST | `generate_vp` | Yes (A10) |
| `/api/did/vc/reissue` | POST | `revoke_and_reissue` | Yes (A10) |
| `/api/did/vc/revoke` | POST | `revoke_vc` | Yes (898f99c — JWT guard added after initial A10 commit) |

**Public (no JWT):** `/api/did/login`, `/api/did/challenge`.

**Unprotected read / verify (pending policy):** `/api/did/vp/verify`, `/api/did/vc/status`, subordinate/entity/chain GET routes.

### 6.5 System API (B2 — JWT on admin routes)

All routes under `/api/system/entity-types`, `/api/system/permissions`, `/api/system/*standard-fields*`, `/api/system/*standard-methods*`, `/api/system/versions`, `/api/system/menus*`, `/api/system/menu/*`, `/api/system/version-menus/*` use `@jwt_required` per B2 inventory (22 handlers).

---

## 7. Pending Contract Work

- Full OpenAPI specification (`contracts/openapi/`)
- JSON Schema examples for request/response bodies
- Error envelope normalization across all modules
- Permission matrix and RBAC contract (`modeling:*`, `iot:*`, `device:manage`)
- Machine / service identity and m2m tokens
- Contract tests and CI validation
- Fine-grained DID permissions (`did:issue`, `did:revoke`, `did:manage`) — JWT only today
- Unprotected IoT read routes policy decision

---

## Related Documents

- `contracts/API_GROUPS.md` — A0 grouping
- `contracts/SECURITY_BOUNDARY.md` — security contract baseline
- `docs/security/IBMS_SECURITY_A6_MODELING_API_PROTECTION.md`
- `docs/security/IBMS_SECURITY_A7_IOT_API_PROTECTION.md`
- `docs/security/IBMS_SECURITY_A8B_SSE_TEST_ENDPOINT_GUARD.md`
- `docs/security/IBMS_SECURITY_A9_AUDIT_TRACEID_BOUNDARY.md`
- `docs/security/IBMS_SECURITY_A10_DID_API_PROTECTION.md`
