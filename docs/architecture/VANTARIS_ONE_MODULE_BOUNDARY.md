# VANTARIS ONE Module Boundary

## 1. Allowed Dependencies

允许依赖方向：

- Contracts -> all modules as reference
- Edge -> Link only for delivery
- Link -> Code / NexusAI / external adapter by route policy
- Code -> DB through approved data access layer
- Console -> Code/Edge/Link/NexusAI/DB admin APIs
- NexusAI -> Code/CDE APIs, not direct business DB
- DB -> no outbound business calls

## 2. Forbidden Dependencies

- Edge must not direct-write DB
- Edge must not call UFMS runtime directly unless through approved adapter contract
- Link must not implement business logic
- Link must not direct-write business DB
- NexusAI must not bypass Code to modify business state
- Console must not bypass Code for business write operations
- UFMS runtime/source/schema/auth/login/seed/migration must not be copied into ONE
- IBMS legacy runtime must not be treated as total platform after transition
- Business modules must not directly mutate other module schemas

## 3. Shared Object Ownership

- Site / Building / Floor / Space / Asset / Device / Point -> asset_foundation
- Gateway / Connector / SourceSystem / TagMapping -> integration
- Telemetry / Event / Alarm / FaultCase -> event_alarm
- WorkOrder / Inspection / MaintenancePlan -> work_management
- ESG readings/report -> esg
- AI inference/model/job -> ai
- CDE case/step/evidence/hashAnchor -> decision_evidence
- License / DID / VC / Patch -> trust / platform_core

## 4. Cross-module Communication

所有跨模块通信必须通过：

- Contracts
- API
- Event
- Adapter
- Route policy
- Module registry

禁止跨模块直接 import runtime internals。
