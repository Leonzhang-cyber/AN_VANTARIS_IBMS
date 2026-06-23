# ASSET-CONTEXT-GA-R1 Unified Asset Context Linkage

PASS marker: ONE_ASSET_CONTEXT_GA_R1_UNIFIED_LINKAGE_PASS

ASSET-CONTEXT-GA-R1 adds a VANTARIS ONE read-only Asset Context aggregation layer for customer preview review. It links Asset / System / Device / Event / Work Order / Maintenance Task / UHMI Panel / UCDE Evidence / Reports / Customer Delivery / Foundation Diagnostics into a unified local context projection.

## Scope

- Scope: ASSET_CONTEXT_GA_R1
- Module ID: asset-context
- Visual style: VANTARIS_LIGHT_OPERATIONS_CONSOLE
- Graph mode: local-readonly-asset-context-projection
- UI route: /one/assets/context
- API namespace: /api/v1/one/asset-context

## Read-only Guardrails

- readOnly: true
- runtimeEnabled: false
- dbWriteEnabled: false
- assetGraphWriteEnabled: false
- edgeCommandExecution: false
- linkCommandExecution: false
- deviceControlEnabled: false
- productionActivation: false
- No DB migration
- No auth/login/JWT/RBAC mutation
- No Asset Graph canonical write or persistence contract change
- No ONE Adapter introduction
- No SSH, deployment, install, or runtime activation

## API Surface

- GET /api/v1/one/asset-context/health
- GET /api/v1/one/asset-context/summary
- GET /api/v1/one/asset-context/assets
- GET /api/v1/one/asset-context/assets/<asset_id>
- GET /api/v1/one/asset-context/assets/<asset_id>/links
- GET /api/v1/one/asset-context/graph
- GET /api/v1/one/asset-context/guardrails

All endpoints are read-only and expose local projection data only.

## Linkage Model

Asset Context references these object types:

- asset
- system
- device
- event
- workOrder
- maintenanceTask
- uhmiPanel
- ucdeEvidence
- report
- customerDelivery
- foundationDiagnostics

Graph edge semantics:

- belongs-to
- located-in
- has-work-order
- has-event
- has-evidence
- shown-in-panel
- included-in-report
- referenced-by-delivery
- checked-by-diagnostics

## Provider Resilience

The provider aggregates existing read-only modules when available:

- AssetsTopologyService
- UmmsMaintenanceService
- UcdeEvidenceService
- UHMI provider read-only functions
- Reports GA R13 service
- Customer Delivery read-only provider
- Foundation Diagnostics service

If a provider cannot be imported or called, Asset Context records integrationStatus: unavailable and adds a limitation. The API remains available.

## UI

The UI presents:

- Summary cards
- Asset context table
- Selected asset detail panel
- Linkage matrix: Asset -> Work Orders -> Events -> Evidence -> Reports -> UHMI Panels
- Read-only guardrails panel
- Limitations / Not Production GA note

This is a customer preview read-only projection and not production activation.

