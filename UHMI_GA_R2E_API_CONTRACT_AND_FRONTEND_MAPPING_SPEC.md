# UHMI-GA-R2E API Contract and Frontend Mapping Spec

PASS marker: `UHMI_GA_R2E_WORKSPACE_API_CONSOLIDATION_FRONTEND_INTEGRATION_AUDIT_PASS`

## API Contract

The R2E audit endpoint is a static read-only consolidation endpoint:

- Method: `GET`
- Path: `/api/one/uconsole/uhmi/integration-audit`
- Scope: `UHMI_GA_R2E`
- Mode: `read_only`
- Workspace: `UConsole / UHMI Workspace`
- Visual style: `VANTARIS_LIGHT_OPERATIONS_CONSOLE`
- API version: `uhmi-workspace-readonly.v1`

The payload exposes the consolidated audit fields:

- `apiConsolidation`
- `frontendIntegrationAudit`
- `routeMenuPackageAlignment`
- `staticDataConsistency`
- `readOnlySafetyVerified`
- `previousStages`
- `apiEndpoints`
- `commonResponseFields`
- `safety`
- `guardrails`
- `futureControlPath`
- `generatedAt`
- `staticSnapshotAt`

## Frontend Mapping

Frontend service mapping is centralized in:

- `AN_VANTARIS_IBMS-frontend/src/services/api/uhmi.ts`

The service exposes:

- `UhmiIntegrationAuditPayload`
- `getUhmiIntegrationAudit()`

The mapping is read-only and uses a GET request only. It does not expose buttons, commands, mutations, form submissions, package actions, install actions, rollback actions, device actions, EDGE commands, LINK commands, DB writes, auth changes, login changes, JWT changes, or real RBAC writes.

## UI Alignment

The existing UHMI Workspace UI remains the R2D light operations console:

- `VANTARIS_LIGHT_OPERATIONS_CONSOLE`
- `Read-only Mode`
- `No Direct Device Control`
- `No Runtime Activation`
- `No DB Write`
- `No Real RBAC Mutation`
- `Future Control Path`

R2E audits this alignment rather than redesigning the workspace.

## Menu / Route / Package Alignment

R2E keeps the UConsole / UHMI Workspace information architecture established in R2A:

- `HMI Overview`
- `System HMI`
- `Device HMI`
- `Alarm & Event HMI`
- `EDGE / LINK Diagnostics`
- `Evidence & Reports`

Sidebar navigation remains L1/L2 only. L3 workspace navigation remains inside the page.

## Safety Contract

Required false safety fields:

- `controlEnabled`
- `runtimeActivation`
- `deviceWrite`
- `dbWrite`
- `edgeCommandExecution`
- `linkCommandExecution`
- `realRbacMutation`
- `permissionWrite`
- `packageStateMutation`
- `installExecution`
- `rollbackExecution`

`UHMI_GA_R2E_WORKSPACE_API_CONSOLIDATION_FRONTEND_INTEGRATION_AUDIT_PASS`
