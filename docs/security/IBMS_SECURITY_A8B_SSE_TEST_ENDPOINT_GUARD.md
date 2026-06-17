# VANTARIS IBMS Security A8B SSE Test Endpoint Guard

## 1. Task Scope

- Task ID: IBMS-SECURITY-A8B
- Scope: protect or disable SSE test-sse-push endpoint
- Official SSE stream/latest behavior not changed
- IoT API not changed
- Simulator files not changed
- No DB schema changed
- No JWT payload changed
- No login logic changed
- No service started
- No dependency installed

## 2. Files Changed

| File | Change |
|---|---|
| `AN_VANTARIS_IBMS-backend/src/api/iot/sse_api.py` | Added `@jwt_required` and production/feature-flag guard for `test-sse-push` |
| `docs/security/IBMS_SECURITY_A8B_SSE_TEST_ENDPOINT_GUARD.md` | This document |

## 3. Guarded Route

| Route | Method | Guard Applied | Production Behavior |
|---|---|---|---|
| `/api/iot/device/<device_code>/test-sse-push` | POST | `@jwt_required` + `IS_PRODUCTION` check + feature flags | Returns 403; endpoint disabled |

Non-production: requires `IBMS_SIMULATOR_ENABLED=true` or `IBMS_TESTMQTT_ENABLED=true` (via `Config.SIMULATOR_ENABLED` / `Config.TESTMQTT_ENABLED`).

## 4. Not Changed

- `/stream` not changed.
- `/latest` not changed.
- `iot_api.py` not changed.
- testMQTT not changed.
- MQTT driver not changed.
- Device manager not changed.
- Telemetry storage not changed.

## 5. Verification

- `sse_api.py` reviewed.
- `test-sse-push` guarded with JWT and production/feature-flag checks.
- Official SSE routes unchanged.
- `git diff` reviewed.
- No service started.

## 6. Recommended Next Tasks

- IBMS-SECURITY-A9
- IBMS-CONTRACTS-A1
- IBMS-CORE-A0
