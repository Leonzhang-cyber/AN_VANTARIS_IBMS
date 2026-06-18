# IBMS Legacy Inventory Summary

## 1. Current Repository Structure Summary

Top-level structure (runtime-relevant):

- `AN_VANTARIS_IBMS-backend`
- `AN_VANTARIS_IBMS-frontend`
- `AN_VANTARIS_IBMS-ibms_backend` (legacy/raw-like backend copy)
- `AN_VANTARIS_IBMS-ibms_front` (legacy/raw-like frontend copy)
- `contracts`
- `docs`

Inventory notes:

- Current implementation is centered on `AN_VANTARIS_IBMS-backend` + `AN_VANTARIS_IBMS-frontend`
- Legacy compatibility candidates exist in `AN_VANTARIS_IBMS-ibms_backend` and `AN_VANTARIS_IBMS-ibms_front`
- Contract and governance assets are already separated under `contracts` and `docs`

## 2. Current Backend Capability Summary

Observed capability paths include:

- API host: `AN_VANTARIS_IBMS-backend/src/api/**`
- System/menu/permission: `AN_VANTARIS_IBMS-backend/src/api/system/**`, `src/system/**`, `src/common/utils/permission_util.py`
- IoT domain: `AN_VANTARIS_IBMS-backend/src/Iot/**`, `src/api/iot/**`
- Auth/session and DID: `AN_VANTARIS_IBMS-backend/src/api/did/**`, `src/DID/**`
- Data/AI-like modeling: `AN_VANTARIS_IBMS-backend/src/data_modeling/**`, `src/api/data_modeling/**`
- Audit traces: `AN_VANTARIS_IBMS-backend/src/common/utils/audit_trace.py`
- Test/simulator runtime candidates: `AN_VANTARIS_IBMS-backend/src/testMQTT/**`

## 3. Current Frontend Capability Summary

Observed capability paths include:

- Router/layout/app shell: `AN_VANTARIS_IBMS-frontend/src/router/**`, `src/components/AppLayout.vue`, `src/app/**`
- Auth/session/token: `AN_VANTARIS_IBMS-frontend/src/services/auth/**`
- API clients: `AN_VANTARIS_IBMS-frontend/src/services/api/**`
- System/permission/admin views: `AN_VANTARIS_IBMS-frontend/src/modules/system/**`
- Placeholder module structure: `src/modules/did`, `src/modules/iot`, `src/modules/modeling`, `src/modules/operations`

## 4. Current Protocol/IoT/Driver Summary

Formal target `AN_VANTARIS_EDGE` directory: **not present**.

Current driver source is mainly in backend runtime:

- `AN_VANTARIS_IBMS-backend/src/Iot/drivers/base_driver.py`
- `AN_VANTARIS_IBMS-backend/src/Iot/drivers/http_driver.py`
- `AN_VANTARIS_IBMS-backend/src/Iot/drivers/isapi_driver.py`
- `AN_VANTARIS_IBMS-backend/src/Iot/drivers/isup_driver.py`
- `AN_VANTARIS_IBMS-backend/src/Iot/drivers/modbus_driver.py`
- `AN_VANTARIS_IBMS-backend/src/Iot/drivers/mqtt_driver.py`
- `AN_VANTARIS_IBMS-backend/src/Iot/drivers/rtsp_driver.py`

Coupled runtime areas that require careful extraction sequencing:

- `AN_VANTARIS_IBMS-backend/src/Iot/dao.py`
- `AN_VANTARIS_IBMS-backend/src/Iot/models.py`
- `AN_VANTARIS_IBMS-backend/src/Iot/services/**`
- `AN_VANTARIS_IBMS-backend/src/api/iot/**`
- `AN_VANTARIS_IBMS-backend/src/api/iot/sse_api.py`

## 5. Current DB/Migration Summary

Current DB/migration artifacts:

- `AN_VANTARIS_IBMS-backend/src/common/core/database.py`
- `AN_VANTARIS_IBMS-backend/alembic.ini`
- `AN_VANTARIS_IBMS-backend/migrations/**`
- `AN_VANTARIS_IBMS-backend/src/system/models.py`
- `AN_VANTARIS_IBMS-backend/src/system/menu_models.py`
- `AN_VANTARIS_IBMS-backend/src/Iot/models.py`
- `AN_VANTARIS_IBMS-backend/src/DID/models.py`

Status:

- Migration framework scaffold exists
- DB naming is still legacy-anchored and not yet modularized by target package boundaries

## 6. Current Docs/Contracts Summary

- Contracts are available under `contracts/**` (openapi/schemas/errors/examples/status/tools)
- Naming/architecture governance is available under `docs/governance/**` and `docs/architecture/**`
- Security and risk governance is available under `docs/security/**`

## 7. Missing Target Packages Summary

Current presence check for A1/A2 frozen 6+1 packages:

- `AN_VANTARIS_EDGE`: **missing**
- `AN_VANTARIS_LINK`: **missing**
- `AN_VANTARIS_Code`: **missing**
- `AN_VANTARIS_Console`: **missing**
- `AN_VANTARIS_NexusAI`: **missing**
- `AN_VANTARIS_DB`: **missing**
- `AN_VANTARIS_Contracts`: **missing**

Interpretation:

- A3 confirms this repository is still a legacy implementation base and mapping source.
- Target packages should be introduced in later staged tasks (not in A3).
