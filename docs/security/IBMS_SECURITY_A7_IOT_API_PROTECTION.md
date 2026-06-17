# VANTARIS IBMS Security A7 IoT API Protection

## 1. Task Scope

- Task ID: IBMS-SECURITY-A7
- Scope: protect high-risk IoT write, command, and ingest APIs with JWT
- No MQTT driver changed
- No telemetry storage changed
- No device model changed
- No DB schema changed
- No JWT payload changed
- No login logic changed
- No global RBAC refactor
- No service started
- No dependency installed

## 2. Files Changed

| File | Change |
|---|---|
| `AN_VANTARIS_IBMS-backend/src/api/iot/iot_api.py` | Added `@jwt_required` to 17 high-risk write/command/ingest/config routes |
| `docs/security/IBMS_SECURITY_A7_IOT_API_PROTECTION.md` | This document |

**Out of scope (unchanged):** `sse_api.py` — SSE stream/latest/test-push routes not modified in A7.

## 3. Protected Routes

| Route | Method | Handler | Protection Applied | Risk Category |
|---|---|---|---|---|
| `/api/iot/device/register` | POST | `register_device` | `@jwt_required` | Device CRUD write |
| `/api/iot/device/did/<device_did>` | PUT | `update_device` | `@jwt_required` | Device CRUD write |
| `/api/iot/device/did/<device_did>` | PATCH | `patch_device` | `@jwt_required` | Device CRUD write |
| `/api/iot/device/did/<device_did>` | DELETE | `delete_device` | `@jwt_required` | Device CRUD write |
| `/api/iot/device/did/<device_did>/status` | PUT | `update_device_status` | `@jwt_required` | Device enable/disable |
| `/api/iot/device/did/<device_did>/field-mappings` | PUT | `update_device_field_mappings` | `@jwt_required` | Mapping config write |
| `/api/iot/device/did/<device_did>/method-mappings` | PUT | `update_device_method_mappings` | `@jwt_required` | Mapping config write |
| `/api/iot/device/<device_did>/command` | POST | `send_device_command` | `@jwt_required` | Device command |
| `/api/iot/device/code/<device_code>/command` | POST | `send_command_by_code` | `@jwt_required` | Device command |
| `/api/iot/ingest/http` | POST | `http_data_ingest` | `@jwt_required` | Telemetry ingest |
| `/api/iot/device/<device_code>/reconnect` | POST | `reconnect_device` | `@jwt_required` | Device control |
| `/api/iot/standard-fields` | POST | `create_standard_field` | `@jwt_required` | Config write |
| `/api/iot/standard-fields/<field_code>` | PUT | `update_standard_field` | `@jwt_required` | Config write |
| `/api/iot/standard-fields/<field_code>` | DELETE | `delete_standard_field` | `@jwt_required` | Config write |
| `/api/iot/standard-methods` | POST | `create_standard_method` | `@jwt_required` | Config write |
| `/api/iot/standard-methods/<method_code>` | PUT | `update_standard_method` | `@jwt_required` | Config write |
| `/api/iot/standard-methods/<method_code>` | DELETE | `delete_standard_method` | `@jwt_required` | Config write |

### Unprotected read routes (intentional)

| Route | Method | Handler | Notes |
|---|---|---|---|
| `/api/iot/device/parent/<parent_did>` | GET | `get_devices_by_parent` | Read-only list |
| `/api/iot/device/did/<device_did>` | GET | `get_device_by_did` | Read-only detail |
| `/api/iot/device/code/<device_code>` | GET | `get_device_by_code` | Read-only lookup |
| `/api/iot/device/<device_code>/sse-url` | GET | `get_device_sse_url` | SSE URL helper |
| `/api/iot/standard-methods` | GET | `get_standard_methods` | Dictionary read |
| `/api/iot/standard-methods/<method_code>` | GET | `get_standard_method_detail` | Dictionary read |
| `/api/iot/standard-fields` | GET | `get_standard_fields` | Dictionary read |
| `/api/iot/standard-fields/<field_code>` | GET | `get_standard_field_detail` | Dictionary read |
| `/api/iot/<device_did>/field-mappings-info` | GET | `get_device_field_mappings` | Mapping read |
| `/api/iot/<device_did>/method-mappings-info` | GET | `get_device_method_mappings` | Mapping read |

## 4. Auth Strategy

- Existing `@jwt_required` decorator from `src.common.utils.jwt_util` reused (same pattern as modeling and system APIs).
- JWT payload format not changed.
- Login behavior not changed.
- Fine-grained RBAC (`iot:command`, `iot:ingest`, etc.) remains pending **IBMS-CORE-A0** / **IBMS-SECURITY-A7B**; no permission seed in this task.

## 5. Recommended Permissions

Target permission codes for future CORE-A0 / SECURITY-A7B (not seeded in A7):

| Permission | Suggested use |
|---|---|
| `iot:read` | Device/mapping/dictionary GET routes |
| `iot:write` | Device register, update, delete, mapping writes |
| `iot:command` | Command endpoints |
| `iot:ingest` | HTTP telemetry ingest |
| `device:manage` | Standard field/method admin, reconnect |

## 6. Not Changed

- MQTT driver not changed.
- Device manager not changed.
- Telemetry CSV storage not changed.
- DB schema not changed.
- DID / blockchain not changed.
- Modeling API not changed.
- Simulator not changed.
- JWT payload not changed.
- Login logic not changed.

## 7. Verification

- `iot_api.py` reviewed: 17 write/command/ingest/config routes protected.
- 10 read routes left unprotected per A7 scope (low-risk reads).
- `git diff` reviewed; changes limited to decorator import and route guards.
- No real secret committed.
- No service started.

## 8. Recommended Next Tasks

- IBMS-SECURITY-A7-COMMIT
- IBMS-SECURITY-A7B — fine-grained IoT permissions if needed
- IBMS-SECURITY-A8 — disable simulator in production
- IBMS-CONTRACTS-A1
- IBMS-CORE-A0
