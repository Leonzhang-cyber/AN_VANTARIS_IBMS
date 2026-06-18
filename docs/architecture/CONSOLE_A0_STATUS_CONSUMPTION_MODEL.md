# Console A0 Status Consumption Model

Current phase defines status consumption model only. It does not create DB mapping, does not modify API, does not add frontend routes, and does not implement a Console runtime page.

## 1) Shared EDGE Health

- Source: shared foundation edge health outputs via ONE adapter
- Contract / adapter dependency: approved edge health contracts and adapter boundary
- Console usage: render upstream collection health overview
- Required identity fields: tenantId, projectId, siteId, edgeNodeId
- Traceability fields: messageId, traceId, correlationId, observedAt
- Current status: A0 documentation only

## 2) Shared LINK Health

- Source: shared foundation link health references
- Contract / adapter dependency: approved link health/status contract objects
- Console usage: display link path availability and service posture
- Required identity fields: tenantId, projectId, siteId, linkServiceId
- Traceability fields: messageId, traceId, correlationId, observedAt
- Current status: A0 documentation only

## 3) Link Delivery State

- Source: shared link delivery state outputs
- Contract / adapter dependency: approved link delivery contracts through adapter
- Console usage: visualize delivery reliability summary and queue-state posture
- Required identity fields: tenantId, projectId, siteId, routeId
- Traceability fields: messageId, traceId, correlationId, deliveryAt
- Current status: A0 documentation only

## 4) Shared Contracts Version

- Source: shared contracts version references
- Contract / adapter dependency: approved contracts/version metadata boundary
- Console usage: surface current version visibility and compatibility context
- Required identity fields: tenantId, projectId, siteId, contractFamilyId
- Traceability fields: messageId, traceId, correlationId, versionObservedAt
- Current status: A0 documentation only

## 5) ONE Adapter Status

- Source: ONE adapter status and integration health references
- Contract / adapter dependency: adapter health/status boundary contracts
- Console usage: monitor adapter state, readiness, and dependency posture
- Required identity fields: tenantId, projectId, siteId, adapterInstanceId
- Traceability fields: messageId, traceId, correlationId, statusAt
- Current status: A0 documentation only

## 6) UFMS Integration Status, optional

- Source: UFMS integration feed health via approved adapter boundary
- Contract / adapter dependency: optional UFMS integration status contract
- Console usage: show fault-intelligence feed connectivity and freshness summary
- Required identity fields: tenantId, projectId, siteId, integrationId
- Traceability fields: messageId, traceId, correlationId, observedAt
- Current status: optional A0 documentation only

## 7) IBMS Core Module Status

- Source: IBMS Core module status references through approved boundaries
- Contract / adapter dependency: module status contract and adapter/API boundary
- Console usage: module enablement and operational posture visibility
- Required identity fields: tenantId, projectId, siteId, moduleId
- Traceability fields: messageId, traceId, correlationId, statusAt
- Current status: A0 documentation only

## 8) MMS Module Status

- Source: MMS module status references
- Contract / adapter dependency: approved module status contract
- Console usage: show maintenance module health and availability state
- Required identity fields: tenantId, projectId, siteId, moduleId
- Traceability fields: messageId, traceId, correlationId, statusAt
- Current status: A0 documentation only

## 9) ESG Module Status

- Source: ESG module status references
- Contract / adapter dependency: approved module status contract
- Console usage: show sustainability module health and readiness state
- Required identity fields: tenantId, projectId, siteId, moduleId
- Traceability fields: messageId, traceId, correlationId, statusAt
- Current status: A0 documentation only

## 10) IDC/DCIM Module Status

- Source: IDC/DCIM module status references
- Contract / adapter dependency: approved module status contract
- Console usage: show data-center module health and service posture
- Required identity fields: tenantId, projectId, siteId, moduleId
- Traceability fields: messageId, traceId, correlationId, statusAt
- Current status: A0 documentation only

## 11) CDE Module Status

- Source: CDE module status references
- Contract / adapter dependency: approved module status contract
- Console usage: show evidence/traceability module health and readiness state
- Required identity fields: tenantId, projectId, siteId, moduleId
- Traceability fields: messageId, traceId, correlationId, statusAt
- Current status: A0 documentation only

## 12) License / Feature Status, future

- Source: future license and feature-visibility references
- Contract / adapter dependency: future governance/license status contracts
- Console usage: present capability visibility and entitlement posture
- Required identity fields: tenantId, projectId, siteId, licenseRefId
- Traceability fields: messageId, traceId, correlationId, evaluatedAt
- Current status: future scope only

## 13) Patch / Version Status, future

- Source: future patch and package version governance references
- Contract / adapter dependency: future patch/version status contracts
- Console usage: visualize patch readiness and version governance posture
- Required identity fields: tenantId, projectId, siteId, packageRefId
- Traceability fields: messageId, traceId, correlationId, checkedAt
- Current status: future scope only

## 14) Audit / Evidence Status

- Source: CDE evidence and audit readiness references
- Contract / adapter dependency: approved evidence/audit status contracts
- Console usage: provide audit visibility and evidence readiness summary
- Required identity fields: tenantId, projectId, siteId, evidenceStatusRefId
- Traceability fields: messageId, traceId, correlationId, referencedAt
- Current status: A0 documentation only

## 15) Deployment Mode Status

- Source: deployment/environment status references from approved boundaries
- Contract / adapter dependency: approved deployment status metadata contracts
- Console usage: display environment/deployment mode visibility
- Required identity fields: tenantId, projectId, siteId, deploymentRefId
- Traceability fields: messageId, traceId, correlationId, observedAt
- Current status: A0 documentation only

## 16) System Health Summary

- Source: aggregated status references from shared foundation, adapter, and modules
- Contract / adapter dependency: approved status aggregation boundary contracts
- Console usage: render overall platform health summary
- Required identity fields: tenantId, projectId, siteId, systemHealthRefId
- Traceability fields: messageId, traceId, correlationId, summarizedAt
- Current status: A0 documentation only
