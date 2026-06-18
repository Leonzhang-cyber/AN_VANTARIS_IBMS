# VANTARIS ONE Product Naming Model

## Naming Mapping Table

| Layer | Current Name | Target Name | Action |
| ----- | ------------ | ----------- | ------ |
| Repository Platform | `AN_VANTARIS_IBMS` | `AN_VANTARIS_ONE` | docs-first rebrand, code path staged migration |
| Backend Runtime | `AN_VANTARIS_IBMS-backend` | `AN_VANTARIS_Code` + `ibms-core` | keep runtime path for now, map domain ownership first |
| Frontend Runtime | `AN_VANTARIS_IBMS-frontend` | `AN_VANTARIS_Console` + module UI | keep route/import compatibility, rename display and docs first |
| Edge Drivers | `src/Iot/drivers` | `AN_VANTARIS_EDGE` protocol plugins | classify and extract as shared edge foundation |
| System Menu/Permission | `system/menu/permission` | platform-core + Console | preserve API/runtime compatibility, align naming in contracts/docs |
| DB Models | SQLAlchemy models in backend | `AN_VANTARIS_DB` domain model | DB rename deferred, migration-framework controlled |
| Contracts/Docs | `contracts/*`, governance docs | `AN_VANTARIS_Contracts` | align product family and namespace progressively |
| AI Functions | AI related service/functions | `AN_VANTARIS_NexusAI` adapter | isolate as adapter boundary and shared capability |
| Audit/Trace | audit/event records | audit + `cde-traceability` | keep IBMS compatibility while defining ONE governance names |
| Integration API | integration endpoints/adapters | `AN_VANTARIS_LINK` route / adapters | no immediate API path break, contract-aligned namespace shift later |

## Platform Role Definition

- `VANTARIS ONE` = platform
- `IBMS Core` = business module (`ibms-core`)
- `UFMS` = separate fault intelligence engine or adapter boundary
- `Edge/LINK` = shared integration foundation
