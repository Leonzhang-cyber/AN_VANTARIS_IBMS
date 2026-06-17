# VANTARIS IBMS Security A8 Simulator Production Guard

## 1. Task Scope

- Task ID: IBMS-SECURITY-A8
- Scope: disable simulator / testMQTT / mock route exposure in production
- No simulator files deleted
- No MQTT topic or payload changed
- No IoT API behavior changed
- No DB schema changed
- No JWT payload changed
- No login logic changed
- No global RBAC refactor
- No service started
- No dependency installed

## 2. Files Changed

| File | Change |
|---|---|
| `AN_VANTARIS_IBMS-backend/src/common/config/default.py` | Added `IBMS_ENV`, `IS_PRODUCTION`, `SIMULATOR_ENABLED`, `TESTMQTT_ENABLED` (env-first; forced off in production) |
| `AN_VANTARIS_IBMS-backend/src/main.py` | Logs A8 guard status at startup; confirms testMQTT not registered on main blueprint |
| `AN_VANTARIS_IBMS-backend/src/testMQTT/_runtime_guard.py` | Shared production guard for standalone script entry points |
| `AN_VANTARIS_IBMS-backend/src/testMQTT/hvac_mqtt_simulator.py` | Entry guard via `require_testmqtt_enabled` |
| `AN_VANTARIS_IBMS-backend/src/testMQTT/air_quality_simulator.py` | Entry guard via `require_testmqtt_enabled` |
| `AN_VANTARIS_IBMS-backend/src/testMQTT/test_air_quality_receiver.py` | Entry guard via `require_testmqtt_enabled` |
| `AN_VANTARIS_IBMS-backend/src/testMQTT/mqtt_subscriber.py` | Entry guard via `require_testmqtt_enabled` |
| `AN_VANTARIS_IBMS-backend/src/testMQTT/http_device_simulator.py` | Entry guard via `require_simulator_enabled` |
| `AN_VANTARIS_IBMS-backend/src/testMQTT/mock_isapi_camera.py` | Entry guard via `require_simulator_enabled` |
| `AN_VANTARIS_IBMS-backend/src/testMQTT/isup_simulator.py` | Entry guard via `require_simulator_enabled` |
| `AN_VANTARIS_IBMS-backend/src/testMQTT/rtsp_simulator.py` | Entry guard via `require_simulator_enabled` |
| `AN_VANTARIS_IBMS-backend/.env.example` | SECURITY-A8 notes on feature flags |
| `docs/security/IBMS_SECURITY_A8_SIMULATOR_PRODUCTION_GUARD.md` | This document |

## 3. Feature Flags

| Variable | Purpose | Default | Production Behavior |
|---|---|---|---|
| `IBMS_ENV` | Runtime environment name | `development` | When `production`, simulators forced off |
| `IBMS_SIMULATOR_ENABLED` | Enable standalone device/mock simulators | `false` | Ignored; always treated as disabled |
| `IBMS_TESTMQTT_ENABLED` | Enable testMQTT MQTT/WebSocket scripts | `false` | Ignored; always treated as disabled |

Config class exposes: `IS_PRODUCTION`, `SIMULATOR_ENABLED`, `TESTMQTT_ENABLED` (computed from env).

## 4. Guarded Components

| Component | File | Guard Applied | Notes |
|---|---|---|---|
| Main Flask app | `main.py` | Startup log + no testMQTT blueprint registration | testMQTT never registered on `api_bp` |
| HVAC MQTT simulator | `hvac_mqtt_simulator.py` | `require_testmqtt_enabled` | Standalone `python` entry |
| Air quality simulator | `air_quality_simulator.py` | `require_testmqtt_enabled` | Standalone entry |
| Air quality receiver | `test_air_quality_receiver.py` | `require_testmqtt_enabled` | Standalone entry |
| MQTT/WebSocket subscriber | `mqtt_subscriber.py` | `require_testmqtt_enabled` | Standalone entry |
| HTTP device simulator | `http_device_simulator.py` | `require_simulator_enabled` | Standalone entry |
| Mock ISAPI camera (Flask) | `mock_isapi_camera.py` | `require_simulator_enabled` | Blocks `app.run` in production |
| ISUP simulator | `isup_simulator.py` | `require_simulator_enabled` | Standalone entry |
| RTSP simulator | `rtsp_simulator.py` | `require_simulator_enabled` | Standalone entry |
| Runtime guard helper | `_runtime_guard.py` | Central guard logic | Exits before simulator startup |

**Not guarded (data/static only):** `hvac_2025_prediction_data.csv`, `air_quality_data.csv`, `testws.html`, `video.mp4` — no Python entry point.

## 5. Runtime Behavior

- Production mode (`IBMS_ENV=production`) disables simulator/testMQTT flags in `Config` regardless of env values.
- Non-production requires explicit `IBMS_SIMULATOR_ENABLED=true` or `IBMS_TESTMQTT_ENABLED=true` to run standalone scripts.
- Official IoT API routes (`iot_api.py`, `sse_api.py`) are unchanged.
- Simulator files remain in the repo for development and manual testing.
- Main app does not register testMQTT Flask routes or auto-start simulators.

## 6. Not Changed

- IoT API not changed.
- SSE API not changed.
- MQTT driver not changed.
- Device manager not changed.
- Telemetry storage not changed.
- Modeling API not changed.
- DID / blockchain not changed.
- DB schema not changed.
- JWT payload not changed.
- Login logic not changed.

## 7. Verification

- testMQTT exposure points reviewed (8 standalone Python entry points + main app startup).
- Production guard added at Config level and script entry points.
- `git diff` reviewed; no simulator business logic or MQTT topic/payload changes.
- No real secret committed.
- No service started.

## 8. Recommended Next Tasks

- IBMS-SECURITY-A8-COMMIT
- IBMS-SECURITY-A9 — sensitive API audit traceId
- IBMS-SECURITY-A6B — fine-grained modeling permissions
- IBMS-SECURITY-A7B — fine-grained IoT permissions
- IBMS-CONTRACTS-A1
- IBMS-CORE-A0
