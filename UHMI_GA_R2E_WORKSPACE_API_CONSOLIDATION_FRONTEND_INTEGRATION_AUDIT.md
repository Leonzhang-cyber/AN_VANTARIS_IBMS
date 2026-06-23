# UHMI-GA-R2E Workspace API Consolidation + Frontend Integration Audit

PASS marker: `UHMI_GA_R2E_WORKSPACE_API_CONSOLIDATION_FRONTEND_INTEGRATION_AUDIT_PASS`

## Scope

UHMI-GA-R2E consolidates the read-only UHMI Workspace API contract and audits the frontend integration surface created through UHMI-GA-R2A, UHMI-GA-R2B, UHMI-GA-R2C, and UHMI-GA-R2D.

UHMI remains Unified Human-Machine Interface under `UConsole / UHMI Workspace`. VANTARIS ONE is cross-industry and not airport-only. UHMI is not SCADA and not independent HMI server infrastructure. R2E does not add business functionality, runtime activation, control execution, device writes, DB writes, package mutation, install, rollback, or permission mutation.

## Consolidated Read-only API Baseline

R2E records the common UHMI response fields expected across workspace-facing read-only payloads:

- `scope`
- `mode`
- `visualStyle`
- `workspace`
- `apiVersion`
- `readOnly`
- `safety`
- `guardrails`
- `futureControlPath`
- `generatedAt`
- `staticSnapshotAt`

The R2E audit endpoint is:

- `GET /api/one/uconsole/uhmi/integration-audit`

Existing UHMI endpoints remain GET-only:

- `GET /api/one/uconsole/uhmi/workspace`
- `GET /api/one/uconsole/uhmi/status`
- `GET /api/one/uconsole/uhmi/panels`
- `GET /api/one/uconsole/uhmi/systems`
- `GET /api/one/uconsole/uhmi/devices`
- `GET /api/one/uconsole/uhmi/events`
- `GET /api/one/uconsole/uhmi/evidence`
- `GET /api/one/uconsole/uhmi/guardrails`
- `GET /api/one/uconsole/uhmi/roles`
- `GET /api/one/uconsole/uhmi/role-views`
- `GET /api/one/uconsole/uhmi/role-visibility`

## R2E Audit Flags

The audit payload freezes these read-only statements:

- `scope: UHMI_GA_R2E`
- `mode: read_only`
- `visualStyle: VANTARIS_LIGHT_OPERATIONS_CONSOLE`
- `workspace: UConsole / UHMI Workspace`
- `apiConsolidation: true`
- `frontendIntegrationAudit: true`
- `routeMenuPackageAlignment: true`
- `staticDataConsistency: true`
- `readOnlySafetyVerified: true`
- `previousStages: UHMI-GA-R2A, UHMI-GA-R2B, UHMI-GA-R2C, UHMI-GA-R2D`

## Read-only Safety Fields

The R2E contract requires these safety fields to remain false:

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

## Boundary Statement

R2E does not execute the future controlled action path. The future path remains documented only:

`UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device`

Direct paths remain forbidden:

- `UHMI -> Device`
- `UHMI -> DB write`
- `UHMI -> EDGE command`
- `UHMI -> LINK command`
- `UHMI -> NEXUS AI execution`
- `UHMI -> bypass CODE`

`UHMI_GA_R2E_WORKSPACE_API_CONSOLIDATION_FRONTEND_INTEGRATION_AUDIT_PASS`
