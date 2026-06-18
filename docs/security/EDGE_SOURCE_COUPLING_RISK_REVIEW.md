# EDGE Source Coupling Risk Review

## 1) Driver imports backend DAO/model directly

- description: Driver logic depends on backend DAO/model layer.
- affected drivers: `mqtt_driver.py`
- impact: EDGE runtime cannot stay independent from backend DB/application model.
- control: Split mapping/lookup into EDGE-side adapter service contract.
- current status: Present.
- next mitigation task: `EDGE-A0` decouple DAO/model before extraction.

## 2) Driver emits to UI/SSE/API directly

- description: Driver directly pushes to SSE/API layer.
- affected drivers: `isapi_driver.py`, `isup_driver.py`, `rtsp_driver.py`
- impact: Transport layer mixed with presentation/API concerns.
- control: Replace direct SSE calls with Link envelope producer boundary.
- current status: Present.
- next mitigation task: `EDGE-A0` remove direct `push_to_device` usage.

## 3) Driver handles credentials unsafely

- description: Runtime config carries credentials directly in driver context.
- affected drivers: `isapi_driver.py`, `mqtt_driver.py`, `http_driver.py`
- impact: Credential leakage and weak secret handling boundary.
- control: Introduce secure credential provider and redaction policy.
- current status: Present.
- next mitigation task: `EDGE-SECURITY-A0` credential boundary hardening.

## 4) Driver writes or assumes DB state

- description: Driver command flow relies on DB-backed mapping lookup.
- affected drivers: `mqtt_driver.py` (direct), ecosystem impact via `device_manager.py`
- impact: Blocks standalone EDGE deployment and complicates retries.
- control: Contracted mapping snapshot/config feed to EDGE adapter.
- current status: Present.
- next mitigation task: `EDGE-A0` config abstraction.

## 5) Driver uses long-running socket/thread without lifecycle manager

- description: Drivers own sockets/threads internally without unified lifecycle manager.
- affected drivers: `http_driver.py`, `isapi_driver.py`, `isup_driver.py`, `rtsp_driver.py`
- impact: Resource leaks, restart instability, uncertain shutdown behavior.
- control: Add lifecycle supervisor interface in future EDGE package.
- current status: Present.
- next mitigation task: `EDGE-RUNTIME-LIFECYCLE-A0`.

## 6) Driver protocol implementation is simulator-only

- description: Implementation quality/functionality not production-ready.
- affected drivers: `modbus_driver.py`, `rtsp_driver.py`
- impact: Production extraction would fail or be unstable.
- control: Mark simulator/legacy-only until rewrite.
- current status: Present.
- next mitigation task: `EDGE-PROTOCOL-REWRITE-A0`.

## 7) Driver output is not normalized to Contracts Edge schema

- description: Current callback payloads are ad hoc and inconsistent.
- affected drivers: all current drivers
- impact: Link ingestion inconsistency and schema drift.
- control: Enforce `edge-normalized-object.schema.json` as output contract.
- current status: Present.
- next mitigation task: `EDGE-NORMALIZATION-A0`.

## 8) Driver bypasses Link delivery path

- description: Data path currently couples driver -> manager/SSE directly.
- affected drivers: `isapi_driver.py`, `isup_driver.py`, `rtsp_driver.py`, indirectly others
- impact: Missing envelope, ACK, retry, DLQ guarantees.
- control: Future EDGE path must publish via Link envelope contracts.
- current status: Present.
- next mitigation task: `EDGE-LINK-INTEGRATION-A0`.

## 9) Driver copies legacy runtime into EDGE

- description: Direct file copy risk from legacy backend into new EDGE package.
- affected drivers: all candidates
- impact: Legacy coupling and hidden dependencies leak into EDGE runtime.
- control: Adapter/wrapper extraction only; no direct source copy.
- current status: Preventive control active.
- next mitigation task: enforce in `EDGE-A0` implementation checklist.

## 10) UFMS contamination risk

- description: EDGE extraction may accidentally introduce UFMS runtime coupling.
- affected drivers: none currently direct, risk at future integration layer
- impact: Boundary violation between platform modules.
- control: UFMS only through adapter boundary contracts, never runtime direct call.
- current status: Controlled.
- next mitigation task: `EDGE-A0` boundary gate and review sign-off.
