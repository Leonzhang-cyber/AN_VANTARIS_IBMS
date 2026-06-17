# VANTARIS IBMS Security A9 Audit TraceId Boundary

## 1. Task Scope

- Task ID: IBMS-SECURITY-A9
- Scope: add lightweight traceId audit boundary for sensitive APIs
- No DB schema changed
- No audit table created
- No JWT payload changed
- No login logic changed
- No response envelope intentionally changed
- No service started
- No dependency installed

## 2. Files Changed

| File | Change |
|---|---|
| `AN_VANTARIS_IBMS-backend/src/common/utils/audit_trace.py` | New helper: `get_or_create_trace_id`, `log_sensitive_api` |
| `AN_VANTARIS_IBMS-backend/src/api/data_modeling/modeling_api.py` | Audit logging on train / predict / predict_future |
| `AN_VANTARIS_IBMS-backend/src/api/iot/iot_api.py` | Audit logging on IoT high-risk write/command/ingest handlers |
| `docs/security/IBMS_SECURITY_A9_AUDIT_TRACEID_BOUNDARY.md` | This document |

## 3. Trace Strategy

- Reuses `X-Trace-Id` request header when provided; otherwise generates `uuid4`.
- Stores trace id on `g.audit_trace_id` for handler scope (not returned in response body).
- Uses standard `logging` at INFO level with `[AUDIT]` prefix.
- Does not log tokens, passwords, private keys, Authorization headers, or full request bodies.
- No database write in this task.

## 4. Covered Sensitive APIs

| API Area | Handler / Route | Audit Summary Added |
|---|---|---|
| Modeling | `POST /api/modeling/<device_code>/train` | Yes — `modeling.train` |
| Modeling | `POST /api/modeling/<device_code>/predict` | Yes — `modeling.predict` |
| Modeling | `POST /api/modeling/<device_code>/predict_future` | Yes — `modeling.predict_future` |
| IoT | `POST /api/iot/device/register` | Yes — `iot.device.register` |
| IoT | `PUT /api/iot/device/did/<device_did>` | Yes — `iot.device.update` |
| IoT | `PATCH /api/iot/device/did/<device_did>` | Yes — `iot.device.patch` |
| IoT | `DELETE /api/iot/device/did/<device_did>` | Yes — `iot.device.delete` |
| IoT | `POST /api/iot/device/<device_did>/command` | Yes — `iot.device.command` |
| IoT | `POST /api/iot/device/code/<device_code>/command` | Yes — `iot.device.command` |
| IoT | `POST /api/iot/ingest/http` | Yes — `iot.ingest.http` |
| IoT | `POST /api/iot/standard-fields` | Yes — `iot.standard_field.create` |
| IoT | `PUT /api/iot/standard-fields/<field_code>` | Yes — `iot.standard_field.update` |
| IoT | `DELETE /api/iot/standard-fields/<field_code>` | Yes — `iot.standard_field.delete` |
| IoT | `POST /api/iot/standard-methods` | Yes — `iot.standard_method.create` |
| IoT | `PUT /api/iot/standard-methods/<method_code>` | Yes — `iot.standard_method.update` |
| IoT | `DELETE /api/iot/standard-methods/<method_code>` | Yes — `iot.standard_method.delete` |

## 5. Not Changed

- DB schema not changed.
- MQTT driver not changed.
- DID / blockchain not changed.
- Modeling algorithm not changed.
- IoT payload not changed.
- JWT payload not changed.
- Login logic not changed.
- RBAC not changed.

## 6. Verification

- Diff reviewed; audit helper logs metadata only.
- Sensitive fields not logged by audit helper.
- No service started.
- No dependency installed.

## 7. Recommended Next Tasks

- IBMS-CONTRACTS-A1
- IBMS-CORE-A0
- IBMS-SECURITY-A6B
- IBMS-SECURITY-A7B
