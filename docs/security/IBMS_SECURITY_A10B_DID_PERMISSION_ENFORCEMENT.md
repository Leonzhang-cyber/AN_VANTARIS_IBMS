# IBMS Security A10B DID Permission Enforcement

**Task ID:** IBMS-SECURITY-A10B  
**Date:** 2026-06-16

---

## 1. Task Scope

- Enforce fine-grained permissions on DID high-risk POST routes (A10 JWT scope)
- Reuse CORE-A1 decorators after `@jwt_required`
- No login protection, no DID/VC/VP payload or service changes

---

## 2. Files Changed

| File | Change |
|---|---|
| `AN_VANTARIS_IBMS-backend/src/api/did/did_api.py` | Permission decorators on 5 high-risk routes |
| `docs/security/IBMS_SECURITY_A10B_DID_PERMISSION_ENFORCEMENT.md` | This document |

---

## 3. DID Route Permission Matrix

| Route | Method | Handler | Permission |
|---|---|---|---|
| `/api/did/system/init` | POST | `init_system` | `system:admin` **or** `did:manage` |
| `/api/did/entity` | POST | `create_entity` | `did:manage` |
| `/api/did/vp/generate` | POST | `generate_vp` | `did:issue` |
| `/api/did/vc/reissue` | POST | `revoke_and_reissue` | `did:issue` |
| `/api/did/vc/revoke` | POST | `revoke_vc` | `did:revoke` |

---

## 4. Login Unchanged

`/api/did/login` and `/api/did/challenge` remain public.

---

## 5. GET Routes Pending

`/api/did/me` (JWT only, no permission check), subordinate/entity/chain GET, `vp/verify`, `vc/status` — policy pending future tasks.

---

## 6. Not Changed

- DID service, blockchain, VC/VP payloads
- JWT login and token payload structure
- DB schema / seed
- Modeling and IoT modules

---

## 7. Recommended Next Tasks

- DB seed for `did:issue`, `did:revoke`, `did:manage`, `system:admin`
- `/api/did/me` → optional `did:read` enforcement
- DID GET route protection policy
- System API `/system/permissions` → `system:admin` enforcement
