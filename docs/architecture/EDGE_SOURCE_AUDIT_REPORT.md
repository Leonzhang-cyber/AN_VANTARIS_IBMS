# EDGE Source Audit Report

## 1. Scope

- Audit legacy IoT/protocol driver sources as future `AN_VANTARIS_EDGE` inputs.
- Assess extractability, coupling risks, and migration priority.
- Keep this task read-only for runtime source; docs output only.

## 2. Pre-check result

- Git worktree status: clean before audit.
- Baseline commits confirmed:
  - `ab2e953` (`CONTRACTS-A0-MANIFEST-BASELINE`)
  - `cc7f4c6` (`CONTRACTS-A1-EDGE-LINK-SCHEMAS`)

## 3. EDGE runtime package status

- `AN_VANTARIS_EDGE` runtime package currently does not exist.
- `AN_VANTARIS_ONE/packages/AN_VANTARIS_EDGE` exists as skeleton only.
- No dedicated edge runtime directory found under repository runtime roots.

## 4. Current driver inventory

Primary driver candidates in legacy backend:

- `AN_VANTARIS_IBMS-backend/src/Iot/drivers/base_driver.py`
- `AN_VANTARIS_IBMS-backend/src/Iot/drivers/http_driver.py`
- `AN_VANTARIS_IBMS-backend/src/Iot/drivers/isapi_driver.py`
- `AN_VANTARIS_IBMS-backend/src/Iot/drivers/isup_driver.py`
- `AN_VANTARIS_IBMS-backend/src/Iot/drivers/modbus_driver.py`
- `AN_VANTARIS_IBMS-backend/src/Iot/drivers/mqtt_driver.py`
- `AN_VANTARIS_IBMS-backend/src/Iot/drivers/rtsp_driver.py`

No `opcua_driver.py` detected in current tree.

Coupling-sensitive files:

- `AN_VANTARIS_IBMS-backend/src/Iot/dao.py`
- `AN_VANTARIS_IBMS-backend/src/Iot/models.py`
- `AN_VANTARIS_IBMS-backend/src/Iot/services/*`
- `AN_VANTARIS_IBMS-backend/src/Iot/device_manager.py`
- `AN_VANTARIS_IBMS-backend/src/api/iot/iot_api.py`
- `AN_VANTARIS_IBMS-backend/src/api/iot/sse_api.py`

## 5. Driver-by-driver findings

1) `base_driver.py`
- Role: protocol abstraction interface (`connect/disconnect/send_command/subscribe` + callbacks).
- Coupling: minimal, no direct DB/API code.
- Extractability: `READY_TO_WRAP`.

2) `http_driver.py`
- Role: HTTP/HTTPS poll/report transport.
- Coupling: callback-based, but inline polling thread and request session lifecycle in driver.
- Dependencies: `requests`, runtime thread.
- Extractability: `NEEDS_ADAPTER`.

3) `isapi_driver.py`
- Role: Hikvision ISAPI management + video stream + PTZ + alarm polling.
- Coupling: direct SSE push (`src.api.iot.sse_api.push_to_device`), inline credential handling, OpenCV video loop.
- Dependencies: `requests`, `cv2`, `numpy`, `threading`.
- Extractability: `NEEDS_REWRITE` (or strict adapter split).

4) `isup_driver.py`
- Role: ISUP/Ehome server-side ingress with socket protocol handling.
- Coupling: direct SSE push in data/alarm handlers, embedded long-running server/heartbeat lifecycle.
- Dependencies: `socket`, `threading`, protocol parsing.
- Extractability: `NEEDS_ADAPTER`.

5) `modbus_driver.py`
- Role: placeholder only (`pass` methods).
- Coupling: none currently.
- Extractability: `NEEDS_REWRITE` (no usable implementation yet).

6) `mqtt_driver.py`
- Role: MQTT connectivity and command downlink.
- Coupling: direct DAO access inside driver (`StandardMethodDAO`, `MethodMappingDAO`, `DeviceDAO`) for mapping and validation.
- Dependencies: `paho.mqtt.client`.
- Extractability: `NEEDS_ADAPTER` with DAO-decoupling first.

7) `rtsp_driver.py`
- Role: RTP/RTSP receive loop and telemetry/video-like handling.
- Coupling: direct SSE push, socket/thread lifecycle embedded, fixed port behavior.
- Dependencies: `socket`, `threading`.
- Extractability: `SIMULATOR_ONLY` in current form (requires redesign before production EDGE).

## 6. Existing coupling summary

- DB/DAO/model coupling:
  - High in `mqtt_driver.py` (direct DAO calls).
  - Platform-wide in surrounding IoT stack (`dao.py`, `models.py`, `device_manager.py`).
- UI/SSE/API coupling:
  - `isapi_driver.py`, `isup_driver.py`, `rtsp_driver.py` directly call SSE push API.
- Lifecycle coupling:
  - Multiple drivers own sockets/threads without independent EDGE lifecycle manager abstraction.
- Credential handling risk:
  - `isapi_driver.py` and `mqtt_driver.py` process credentials in driver runtime path.

## 7. Which drivers can be wrapped first

- `base_driver.py` (direct protocol-plugin contract base).
- `http_driver.py` (adapter-first wrapping feasible).
- `mqtt_driver.py` (after DAO/mapping extraction to adapter/service boundary).

## 8. Which drivers need adapter/rewrite

- Needs adapter:
  - `http_driver.py`
  - `isup_driver.py`
  - `mqtt_driver.py`
- Needs rewrite:
  - `isapi_driver.py` (video/SSE/auth coupling too deep)
  - `modbus_driver.py` (placeholder implementation)
- Simulator-first / non-production-ready:
  - `rtsp_driver.py`

## 9. Which files must not be directly copied into EDGE

- `AN_VANTARIS_IBMS-backend/src/Iot/dao.py`
- `AN_VANTARIS_IBMS-backend/src/Iot/models.py`
- `AN_VANTARIS_IBMS-backend/src/Iot/services/*`
- `AN_VANTARIS_IBMS-backend/src/Iot/device_manager.py`
- `AN_VANTARIS_IBMS-backend/src/api/iot/sse_api.py`
- `AN_VANTARIS_IBMS-backend/src/api/iot/iot_api.py`

Rationale:
- These files embed DB/session/API/SSE behavior that must not be copied into standalone EDGE runtime.

## 10. Source audit conclusion

- Existing drivers remain in `AN_VANTARIS_IBMS-backend/src/Iot/drivers`.
- Current driver set is usable as migration source reference, not direct package copy source.
- Adapter/wrapper extraction path is mandatory, with explicit decoupling from DAO/models/SSE/API.
- No runtime source moved in this task.

## 11. Recommended next task

- `EDGE-A0-SKELETON-PACKAGE` (after audit approval), using adapter-first extraction plan.
- In parallel contracts track: maintain Edge output alignment to `contracts/schemas/edge-link/edge-normalized-object.schema.json`.
