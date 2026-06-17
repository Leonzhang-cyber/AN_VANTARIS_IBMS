# IBMS Security A7B IoT Permission Enforcement

**Task ID:** IBMS-SECURITY-A7B  
**Date:** 2026-06-16

---

## 1. Task Scope

- Enforce fine-grained permissions on IoT high-risk write / command / ingest routes (A7 JWT scope)
- Reuse CORE-A1 decorators after `@jwt_required`
- No GET routes, SSE, MQTT driver, device_manager, or payload changes

---

## 2. Files Changed

| File | Change |
|---|---|
| `AN_VANTARIS_IBMS-backend/src/api/iot/iot_api.py` | Permission decorators on 17 JWT-protected routes |
| `docs/security/IBMS_SECURITY_A7B_IOT_PERMISSION_ENFORCEMENT.md` | This document |

---

## 3. Route Permission Matrix (17 routes)

| Route | Method | Handler | Permission |
|---|---|---|---|
| `/api/iot/device/register` | POST | `register_device` | `device:manage` |
| `/api/iot/device/did/<device_did>` | PUT | `update_device` | `device:manage` |
| `/api/iot/device/did/<device_did>` | PATCH | `patch_device` | `device:manage` |
| `/api/iot/device/did/<device_did>` | DELETE | `delete_device` | `device:manage` |
| `/api/iot/device/did/<device_did>/status` | PUT | `update_device_status` | `device:manage` |
| `/api/iot/device/did/<device_did>/field-mappings` | PUT | `update_device_field_mappings` | `device:manage` |
| `/api/iot/device/did/<device_did>/method-mappings` | PUT | `update_device_method_mappings` | `device:manage` |
| `/api/iot/device/<device_did>/command` | POST | `send_device_command` | `iot:command` **or** `device:control` |
| `/api/iot/device/code/<device_code>/command` | POST | `send_command_by_code` | `iot:command` **or** `device:control` |
| `/api/iot/ingest/http` | POST | `http_data_ingest` | `iot:ingest` |
| `/api/iot/device/<device_code>/reconnect` | POST | `reconnect_device` | `device:control` |
| `/api/iot/standard-fields` | POST | `create_standard_field` | `iot:write` |
| `/api/iot/standard-fields/<field_code>` | PUT | `update_standard_field` | `iot:write` |
| `/api/iot/standard-fields/<field_code>` | DELETE | `delete_standard_field` | `iot:write` |
| `/api/iot/standard-methods` | POST | `create_standard_method` | `iot:write` |
| `/api/iot/standard-methods/<method_code>` | PUT | `update_standard_method` | `iot:write` |
| `/api/iot/standard-methods/<method_code>` | DELETE | `delete_standard_method` | `iot:write` |

---

## 4. GET Routes Unchanged

Device queries, standard dictionary GET, mapping-info GET remain without JWT or permission enforcement (A7 policy).

---

## 5. SSE Unchanged

`sse_api.py` and `test-sse-push` not modified in this task.

---

## 6. Not Changed

- Request/response envelopes and handler bodies
- MQTT driver, device_manager, telemetry storage
- JWT login and payload
- DB schema / seed

---

## 7. Recommended Next Tasks

- IBMS-SECURITY-A10B — DID permissions
- IBMS-SECURITY-A11 — SSE stream/latest auth policy
- DB seed for `iot:*`, `device:manage`, `device:control` on operator/service roles
