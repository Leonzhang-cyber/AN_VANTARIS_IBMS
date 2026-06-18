# VANTARIS ONE Contract Domain Matrix

| Contract Domain | Purpose | Owner Module | Consumer Modules | Required Artifacts | Current Status |
| --------------- | ------- | ------------ | ---------------- | ------------------ | -------------- |
| platform object model | define cross-module canonical platform entities | `AN_VANTARIS_Contracts` | `AN_VANTARIS_Code`, `AN_VANTARIS_Console`, `AN_VANTARIS_DB` | canonical object schema set | PARTIAL |
| asset object model | standardize site/building/asset structures | `AN_VANTARIS_Contracts` | `asset-topology`, `AN_VANTARIS_Code`, `AN_VANTARIS_DB` | asset schema definitions | TO_BE_ALIGNED |
| device / point object model | normalize device-point identity and metadata | `AN_VANTARIS_Contracts` | `AN_VANTARIS_EDGE`, `integration-management`, `AN_VANTARIS_Code` | device/point schema package | TO_BE_ALIGNED |
| gateway / connector / source system | unify integration endpoint representation | `AN_VANTARIS_Contracts` | `AN_VANTARIS_EDGE`, `AN_VANTARIS_LINK`, `integration-management` | connector/source-system schemas | MISSING |
| telemetry | standardize telemetry payload and metadata | `AN_VANTARIS_Contracts` | `AN_VANTARIS_EDGE`, `AN_VANTARIS_LINK`, `AN_VANTARIS_Code` | telemetry schema + examples | PARTIAL |
| event | define system and integration events | `AN_VANTARIS_Contracts` | `alarm-event`, `cde-traceability`, `AN_VANTARIS_Code` | event taxonomy + event schemas | PARTIAL |
| alarm | normalize alarm lifecycle/state contract | `AN_VANTARIS_Contracts` | `alarm-event`, `AN_VANTARIS_Console`, `ufms-adapter` | alarm status/event schema | TO_BE_ALIGNED |
| fault case | define fault diagnosis and resolution object | `AN_VANTARIS_Contracts` | `ufms-adapter`, `nexus-ai-adapter`, `mms` | fault-case contract schema | MISSING |
| work order | define work-management lifecycle contract | `AN_VANTARIS_Contracts` | `mms`, `AN_VANTARIS_Console`, `AN_VANTARIS_DB` | work-order schema package | MISSING |
| ESG reading / report | unify ESG metrics and reporting payloads | `AN_VANTARIS_Contracts` | `esg`, `reports`, `AN_VANTARIS_Console` | ESG reading/report schemas | MISSING |
| CDE decision case / step / evidence / hash anchor | preserve decision/evidence chain integrity | `AN_VANTARIS_Contracts` | `cde-traceability`, `AN_VANTARIS_NexusAI`, `AN_VANTARIS_DB` | CDE core schema + hash anchor schema | MISSING |
| AI inference request / response / trace | standardize AI input/output and trace | `AN_VANTARIS_Contracts` | `AN_VANTARIS_NexusAI`, `AN_VANTARIS_Code`, `cde-traceability` | inference request/response/trace schema | TO_BE_ALIGNED |
| Edge local normalized object | define edge normalization output | `AN_VANTARIS_Contracts` | `AN_VANTARIS_EDGE`, `AN_VANTARIS_LINK` | normalized-object schema | MISSING |
| Link envelope | define delivery envelope format | `AN_VANTARIS_Contracts` | `AN_VANTARIS_LINK`, `AN_VANTARIS_Code`, adapters | envelope schema | MISSING |
| Link ACK | define acknowledgement contract | `AN_VANTARIS_Contracts` | `AN_VANTARIS_LINK`, `AN_VANTARIS_EDGE` | ack schema | MISSING |
| Retry policy | define retry semantics and fields | `AN_VANTARIS_Contracts` | `AN_VANTARIS_LINK`, `AN_VANTARIS_EDGE` | retry policy schema | MISSING |
| DLQ | define dead-letter payload contract | `AN_VANTARIS_Contracts` | `AN_VANTARIS_LINK`, ops modules | DLQ schema | MISSING |
| Replay request | define replay request/response format | `AN_VANTARIS_Contracts` | `AN_VANTARIS_LINK`, `AN_VANTARIS_Code`, ops tools | replay schema | MISSING |
| Route policy | define routing rule contract | `AN_VANTARIS_Contracts` | `AN_VANTARIS_LINK`, `integration-management` | route policy schema | MISSING |
| Module manifest | define module identity/capability manifest | `AN_VANTARIS_Contracts` | all runtime modules | module manifest contract | TO_BE_ALIGNED |
| Patch manifest | define patch package contract | `AN_VANTARIS_Contracts` | `AN_VANTARIS_Code`, `AN_VANTARIS_Console`, module runtimes | patch manifest schema | MISSING |
| License VC | define license verifiable credential format | `AN_VANTARIS_Contracts` | `AN_VANTARIS_Code`, `AN_VANTARIS_Console`, trust modules | license VC schema | MISSING |
| DID / VC | define trust identity and credential format | `AN_VANTARIS_Contracts` | `AN_VANTARIS_Code`, `AN_VANTARIS_NexusAI`, adapters | DID/VC schema and validation rules | PARTIAL |
| Error codes | standardize platform error taxonomy | `AN_VANTARIS_Contracts` | all modules | error code catalog | EXISTING |
| Status codes | standardize status/result taxonomy | `AN_VANTARIS_Contracts` | all modules | status code catalog | EXISTING |
| Ports / network boundary | define network boundary and port policy | `AN_VANTARIS_Contracts` | deployment/runtime/security governance | port/boundary catalog | PARTIAL |
| DB schema reference | provide contract-level schema reference, not direct migration | `AN_VANTARIS_Contracts` | `AN_VANTARIS_DB`, `AN_VANTARIS_Code` | db reference schema/catalog | PARTIAL |
| Audit event | define audit event envelope and fields | `AN_VANTARIS_Contracts` | `AN_VANTARIS_Code`, `cde-traceability`, `AN_VANTARIS_DB` | audit event schema | TO_BE_ALIGNED |
