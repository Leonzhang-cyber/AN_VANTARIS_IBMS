# CODE-GA-R1 Read-only Policy Gate + Execution Boundary Preview

PASS marker: ONE_CODE_GA_R1_POLICY_GATE_PREVIEW_PASS

CODE-GA-R1 adds a VANTARIS ONE read-only CODE Policy Gate preview layer for customer and engineer review of a future control-chain safety boundary.

## Future Control Chain

UHMI / UMMS / Asset Context -> CODE Policy Gate -> Approval Boundary -> Audit / UCDE Evidence -> LINK -> EDGE -> Device

R1 does not execute this path. It provides boundary explanation, policy gate preview, approval boundary preview, UCDE evidence linkage preview, and local graph projection only.

## Scope

- Scope: CODE_GA_R1
- Module ID: code-policy
- Visual style: VANTARIS_LIGHT_OPERATIONS_CONSOLE
- Graph mode: local-readonly-code-policy-projection
- UI route: /one/code/policy-gate
- API namespace: /api/v1/one/code-policy

## Read-only Flags

- readOnly: true
- runtimeEnabled: false
- approvalExecutionEnabled: false
- policyMutationEnabled: false
- workflowExecutionEnabled: false
- commandExecutionEnabled: false
- dbWriteEnabled: false
- edgeCommandExecution: false
- linkCommandExecution: false
- deviceControlEnabled: false
- productionActivation: false

## API Surface

- GET /api/v1/one/code-policy/health
- GET /api/v1/one/code-policy/summary
- GET /api/v1/one/code-policy/policy-gates
- GET /api/v1/one/code-policy/execution-boundary
- GET /api/v1/one/code-policy/approval-boundary
- GET /api/v1/one/code-policy/evidence-linkage
- GET /api/v1/one/code-policy/control-path
- GET /api/v1/one/code-policy/guardrails

## Blocked Direct Paths

- UHMI -> Device
- UMMS -> Device
- Asset Context -> Device
- UHMI -> EDGE
- UHMI -> LINK
- UMMS -> EDGE
- UMMS -> LINK
- Asset Context -> DB write
- Reports -> Export execution

## Approval Boundary

Approval stages are represented as read-only preview state:

- request-intent
- policy-check
- role-review
- supervisor-approval
- code-final-gate
- ucde-audit-evidence: future-not-enabled
- link-dispatch: future-not-enabled
- edge-execution: future-not-enabled
- device-action: future-not-enabled

approvalExecutionEnabled is false.

## Evidence Linkage

CODE-GA-R1 links conceptually to UCDE Evidence Center:

- sourceObjectTypes: policyGate, approvalBoundary, controlIntent, blockedDirectPath, executionBoundary
- evidenceMode: read-only-preview
- evidenceWriteEnabled: false
- hashOnlyLocalPreview: true

## Guardrails

- No direct device control
- No EDGE/LINK command
- No DB write
- No approval execution
- No runtime activation
- No production activation
- No bypass CODE
- No auth/RBAC mutation

This task does not modify auth/login/JWT/RBAC, governance/audit runtime behavior, Asset Graph persistence, ONE Adapter boundaries, deployment, installation, DB migration, runtime activation, EDGE/LINK, or device control.

