# IBMS Core A0 Auth Permission Security Mapping

## 1. Purpose

This document maps **security risks** to **current mitigations** and **target controls**. It is a planning artifact for CORE-A0 — **not** a runtime implementation spec.

## 2. Security Mapping

| Risk | Current Mitigation | Target Control | Task |
|---|---|---|---|
| Open modeling API | JWT on all modeling routes (A6) | JWT + `modeling:train` / `modeling:predict` checks | SECURITY-A6B |
| IoT command abuse | JWT on command endpoints (A7) | JWT + `iot:command` / `device:control` | SECURITY-A7B |
| Ingest poisoning | JWT on `/iot/ingest/http` (A7) | JWT + `iot:ingest` + device scope validation | SECURITY-A7B |
| Simulator exposure | Production guard + no blueprint registration (A8) | Guard + env flags + no prod routes | A8 done |
| SSE test push abuse | JWT + production disabled (A8B) | Same + audit trace | A8B done |
| DID issuance abuse | High-risk POST JWT (A10) | JWT + `did:issue` / parent authority check | SECURITY-A10B |
| VC revoke abuse | JWT on revoke/reissue (A10) | JWT + `did:revoke` | SECURITY-A10B |
| Unprotected read APIs | Documented gap (IoT GET, DID GET, SSE stream) | Policy + optional JWT + `*:read` | SECURITY-A11 |
| Missing fine-grained permissions | JWT only; `perms` in payload unused at route level | Permission helper + contract matrix | CORE-A1, CONTRACTS-A2 |
| Missing centralized audit storage | A9 log summaries only | Audit pipeline + `audit:read` | Future data task |
| System admin abuse | JWT on system routes (B2) | JWT + `system:admin` | CORE-A1 |
| Login / challenge abuse | Public endpoints | Rate limit + lockout (future) | Hardening backlog |

## 3. Non-Scope

CORE-A0 does **not** include:

- DB migration or new permission tables
- Permission seed data
- Unified middleware implementation
- Frontend menu / route guard changes
- Login flow or JWT payload changes
- Runtime changes to `jwt_util.py`
