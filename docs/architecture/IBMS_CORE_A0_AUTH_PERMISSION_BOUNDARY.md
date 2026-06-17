# VANTARIS IBMS Core A0 Auth Permission Boundary

## 1. Task Scope

- Task ID: IBMS-CORE-A0
- Scope: define unified auth and permission boundary
- Design-only baseline
- No runtime source code changed
- No DB schema changed
- No seed changed
- No JWT payload changed
- No login logic changed
- No service started
- No dependency installed

## 2. Current Auth Baseline

| Area | Current State |
|---|---|
| JWT decorator | `@jwt_required` in `src/common/utils/jwt_util.py` |
| Modeling API | All 7 routes JWT-protected (SECURITY-A6) |
| IoT write / command / ingest | 17 write routes JWT-protected (SECURITY-A7) |
| SSE test endpoint | JWT + production guard + feature flags (SECURITY-A8B) |
| DID API | `/api/did/me` JWT-protected; high-risk writes targeted in SECURITY-A10 |
| System API | Admin routes JWT-protected per B2 inventory (~22 handlers) |
| Audit trace | Lightweight `X-Trace-Id` logging on sensitive APIs (SECURITY-A9) |
| Fine-grained permissions | **Not enforced** — JWT carries `perms` but route-level permission checks are incomplete |

## 3. Target Auth Layers

| Layer | Purpose | Example |
|---|---|---|
| Authentication | Verify user/service identity | Bearer JWT from `/api/did/login` |
| Authorization | Check permission code | `modeling:train`, `iot:command` |
| Runtime Guard | Environment/feature guard | Simulator disabled when `IBMS_ENV=production` |
| Audit Trace | Trace sensitive actions | `X-Trace-Id` header + `[AUDIT]` log summary |

Layers are **additive**: authentication does not replace runtime guards; authorization does not replace authentication.

## 4. Principal Types

| Principal | Description | Current Support |
|---|---|---|
| Human user | Interactive operator via Console | JWT via challenge/signature login |
| Admin user | System configuration / RBAC admin | JWT + system routes |
| Operator | Day-to-day device / building operations | JWT (perms in payload) |
| Engineer | Modeling / integration / debugging | JWT + dev feature flags |
| System service | Internal batch or automation (future) | **Pending** — no m2m token yet |
| Edge / machine identity | Device or gateway identity (future) | DID/VC at edge; API auth TBD |
| Future DID / VC based identity | VP-based session or service VC | Partial — VP login path exists |

## 5. Permission Namespace Draft

| Domain | Permission Examples |
|---|---|
| modeling | `modeling:read`, `modeling:predict`, `modeling:train` |
| iot | `iot:read`, `iot:write`, `iot:ingest`, `iot:command` |
| device | `device:read`, `device:manage`, `device:control` |
| did | `did:read`, `did:issue`, `did:revoke`, `did:manage` |
| system | `system:read`, `system:write`, `system:admin` |
| contract | `contract:read`, `contract:write` |
| audit | `audit:read` |

Naming rule: `<domain>:<action>` — see `contracts/PERMISSION_BOUNDARY_A0.md`.

## 6. API Protection Matrix

| API Area | Current Protection | Target Protection | Follow-up |
|---|---|---|---|
| Modeling | JWT all routes (A6) | JWT + `modeling:*` per operation | SECURITY-A6B |
| IoT write/command/ingest | JWT on 17 routes (A7) | JWT + `iot:*` / `device:*` | SECURITY-A7B |
| IoT GET | **Unprotected** (A7 scope) | JWT + `iot:read` policy decision | SECURITY-A11 / policy task |
| SSE stream/latest | **Unprotected** | Auth decision + `iot:read` or device scope | SECURITY-A11 |
| SSE test-sse-push | JWT + prod guard (A8B) | Same + optional `iot:write` | A8B done |
| DID issue/revoke/manage | A10 JWT on high-risk POST | JWT + `did:issue` / `did:revoke` / `did:manage` | SECURITY-A10B |
| DID login/challenge | Public (by design) | Public + rate limit (future) | Hardening backlog |
| DID low-risk GET | **Unprotected** | JWT + `did:read` | SECURITY-A10B / policy |
| System menus/permissions | JWT (B2) | JWT + `system:admin` | CORE-A1 |
| Simulator/testMQTT | Production guard (A8) | Guard + no API registration | A8 done |

## 7. Implementation Principles

- Use existing `@jwt_required` until unified middleware is implemented (CORE-A1).
- Do not change JWT payload until contract is approved (`sub`, `perms` remain canonical).
- Permission checks should be **additive**, not replacing authentication.
- DB seed/migration must be separate tasks — no permission rows in CORE-A0.
- Runtime guards (simulator, SSE test) are **not** substitutes for authentication.
- Audit trace must not log secrets, tokens, or full request bodies (A9 baseline).
- Contract documents lead runtime changes; OpenAPI reflects protected boundary (CONTRACTS-A1-OPENAPI).

## 8. Follow-up Tasks

- IBMS-CORE-A1 — implement unified permission helper
- IBMS-SECURITY-A6B — modeling fine-grained permissions
- IBMS-SECURITY-A7B — IoT fine-grained permissions
- IBMS-SECURITY-A10 — DID high-risk route JWT protection
- IBMS-SECURITY-A11 — SSE stream/latest auth decision
- IBMS-CONTRACTS-A2 — permission contract matrix
