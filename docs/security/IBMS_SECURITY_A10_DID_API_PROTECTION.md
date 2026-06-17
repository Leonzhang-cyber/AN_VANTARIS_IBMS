# VANTARIS IBMS Security A10 DID API Protection

## 1. Task Scope

- Task ID: IBMS-SECURITY-A10
- Scope: protect high-risk DID write / issuance / revoke APIs with JWT
- DID/VC/VP payload not changed
- DID service logic not changed
- Blockchain runtime not changed
- Login logic not changed
- JWT payload not changed
- No global RBAC refactor
- No DB schema changed
- No service started
- No dependency installed

## 2. Files Changed

| File | Change |
|---|---|
| `AN_VANTARIS_IBMS-backend/src/api/did/did_api.py` | Added `@jwt_required` to 5 high-risk POST routes (A10); `revoke_vc` guard completed in 898f99c |
| `docs/security/IBMS_SECURITY_A10_DID_API_PROTECTION.md` | This document |

**898f99c follow-up:** Initial A10 commit (`2316904`) omitted `@jwt_required` on `revoke_vc`; fixed in `898f99c`. Contract/docs sync tracked in IBMS-CONTRACTS-A1-OPENAPI-FIX.

## 3. Protected Routes

| Route | Method | Handler | Protection Applied | Risk Category |
|---|---|---|---|---|
| `/api/did/system/init` | POST | `init_system` | `@jwt_required` | System / entity bootstrap |
| `/api/did/entity` | POST | `create_entity` | `@jwt_required` | Entity creation + VC issuance |
| `/api/did/vp/generate` | POST | `generate_vp` | `@jwt_required` | VP creation |
| `/api/did/vc/reissue` | POST | `revoke_and_reissue` | `@jwt_required` | VC revoke + reissue |
| `/api/did/vc/revoke` | POST | `revoke_vc` | `@jwt_required` | VC revocation |

## 4. Unchanged / Pending Routes

| Route | Method | Status |
|---|---|---|
| `/api/did/login` | POST | **Public** — issues JWT |
| `/api/did/challenge` | GET | **Public** — login helper |
| `/api/did/me` | GET | Already JWT-protected (pre-A10) |
| `/api/did/vp/verify` | POST | Unprotected — verification only, no mutation |
| `/api/did/vc/status` | POST | Unprotected — status check |
| `/api/did/subordinates/*` | GET | Unprotected — read gap |
| `/api/did/entity/<did>` | GET | Unprotected — read gap |
| `/api/did/chain/*` | GET | Unprotected — chain read |
| `/api/did/verify/entity/<did>` | GET | Unprotected — integrity check read |

Fine-grained `did:*` permissions pending **CORE-A1** / **SECURITY-A10B**.

## 5. Auth Strategy

- Existing `@jwt_required` decorator reused (same as modeling/IoT/system APIs).
- JWT payload format not changed (`sub`, `perms`).
- Login behavior not changed.
- Fine-grained RBAC not enforced in this task.

## 6. Recommended Permissions

| Permission | Suggested use |
|---|---|
| `did:read` | Entity/subordinate GET routes (future) |
| `did:issue` | create_entity, reissue, generate_vp |
| `did:revoke` | revoke_vc, reissue (revoke leg) |
| `did:manage` | system/init, hierarchy mutations |

## 7. Not Changed

- DID service not changed.
- VC/VP payload not changed.
- Blockchain runtime not changed.
- DB schema not changed.
- JWT payload not changed.
- Login logic not changed.
- Modeling / IoT not changed.

## 8. Verification

- `did_api.py` reviewed: 5 high-risk POST routes now require JWT.
- Login and `/did/me` handling unchanged.
- `git diff` limited to decorator additions.
- No real secret committed.
- No service started.

## 9. Recommended Next Tasks

- IBMS-SECURITY-A10B — fine-grained DID permissions
- IBMS-SECURITY-A11 — SSE stream/latest auth decision
- IBMS-CORE-A1 — unified permission helper
- IBMS-CONTRACTS-A2 — permission contract matrix
