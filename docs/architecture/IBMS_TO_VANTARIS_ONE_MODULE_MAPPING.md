# IBMS to VANTARIS ONE Module Mapping

| Current Area | Current Evidence / Path | Target VANTARIS ONE Module | Migration Action | Risk |
| ------------ | ----------------------- | -------------------------- | ---------------- | ---- |
| backend | `AN_VANTARIS_IBMS-backend/src/**` | `AN_VANTARIS_Code` + `ibms-core` | keep runtime in place, map by bounded context first | monolith coupling |
| frontend | `AN_VANTARIS_IBMS-frontend/src/**` | `AN_VANTARIS_Console` + business module UIs | keep route compatibility, module-by-module UI alignment | route/menu drift |
| system/menu/permission | `src/api/system/**`, `src/system/**`, `src/common/utils/permission_util.py` | `AN_VANTARIS_Code` (platform-core) + `AN_VANTARIS_Console` | preserve API names, map ownership to platform-core/admin | authorization regression |
| auth/session | `src/api/did/**`, `src/DID/**`, `frontend/src/services/auth/**` | `AN_VANTARIS_Code` + `ibms-core` (compatibility) | keep existing session keys and JWT flow in compatibility phase | session compatibility break |
| IoT drivers | `src/Iot/drivers/**`, `src/Iot/**`, `src/api/iot/**` | `AN_VANTARIS_EDGE` + `integration-management` + `edge-link-adapter` | extract drivers in phases after decoupling dao/service/api | hidden DB/runtime coupling |
| HTTP driver | `src/Iot/drivers/http_driver.py` | `AN_VANTARIS_EDGE` protocol plugins | move to plugin package with contractized envelope | protocol behavior drift |
| ISAPI driver | `src/Iot/drivers/isapi_driver.py` | `AN_VANTARIS_EDGE` protocol plugins | isolate protocol logic from backend internals | camera integration break |
| ISUP driver | `src/Iot/drivers/isup_driver.py` | `AN_VANTARIS_EDGE` protocol plugins | decouple from simulator/runtime dependencies | transport incompatibility |
| Modbus driver | `src/Iot/drivers/modbus_driver.py` | `AN_VANTARIS_EDGE` protocol plugins | split protocol adapter from DAO/model layer | field mapping mismatch |
| MQTT driver | `src/Iot/drivers/mqtt_driver.py` | `AN_VANTARIS_EDGE` protocol plugins | enforce contract-driven topic/envelope mapping | event contract drift |
| OPC UA driver | current backend driver file not found; raw frontend protocol references under `AN_VANTARIS_IBMS-ibms_front/src/views/**/OpcUa*` | `AN_VANTARIS_EDGE` roadmap plugin + `integration-management` | treat as planned capability pending source confirmation | capability gap |
| RTSP driver | `src/Iot/drivers/rtsp_driver.py` | `AN_VANTARIS_EDGE` protocol plugins | separate stream adapter from backend service orchestration | media path coupling |
| asset/device model | `src/system/models.py`, `src/Iot/models.py` | `asset-topology` + `AN_VANTARIS_DB` | keep table names short-term, map ownership in model registry | schema ownership conflict |
| alarm/event logic | `src/api/iot/sse_api.py`, event-related IoT services | `alarm-event` + `AN_VANTARIS_Code` + `ufms-adapter` | preserve API compatibility, introduce adapter-mediated fault flow | event/audit drift |
| work/maintenance logic | currently implied in docs and module naming; no dedicated runtime package in current skeleton | `mms` | define mms boundaries in A6 before runtime extraction | module ambiguity |
| energy/esg logic | current explicit runtime path limited; ESG appears in planning/docs and raw-front capability set | `esg` | document-first and contract-first before runtime lift | missing runtime evidence |
| AI related logic | `src/data_modeling/**`, `src/api/data_modeling/**`, `src/blockchain/**` | `AN_VANTARIS_NexusAI` adapter + `nexus-ai-adapter` | keep compatibility wrapper; separate inference APIs/contracts | AI overreach risk |
| audit/evidence logic | `src/common/utils/audit_trace.py`, governance/security docs | `cde-traceability` + `AN_VANTARIS_Code` + `AN_VANTARIS_DB` | standardize evidence schema and trace IDs via contracts | evidence chain inconsistency |
| DB/migration files | `alembic.ini`, `migrations/**`, `src/common/core/database.py` | `AN_VANTARIS_DB` | no table rename now; migrate by framework and staged approval | migration break risk |
| docs/contracts | `docs/**`, `contracts/**` | `AN_VANTARIS_Contracts` + platform governance | align product family and namespace in A4 | contract drift |
| deployment scripts | `AN_VANTARIS_IBMS-backend/scripts/**`, `test/smoke/**` | `AN_VANTARIS_Code` ops + platform deployment governance | keep scripts compatible; add staged wrapper strategy | deployment compatibility break |
| legacy compatibility layer | `AN_VANTARIS_IBMS-ibms_backend/**`, `AN_VANTARIS_IBMS-ibms_front/**`, `AN_VANTARIS_IBMS-main` | `legacy_ibms` + `IBMS Adapter` + `ibms-core` compatibility | preserve as reference/compat source, no direct merge into new runtime | contamination and divergence |
