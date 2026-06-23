import request from './request'

export interface CodePolicySummary {
  scope: string
  moduleId: string
  readOnly: boolean
  runtimeEnabled: boolean
  approvalExecutionEnabled: boolean
  policyMutationEnabled: boolean
  workflowExecutionEnabled: boolean
  commandExecutionEnabled: boolean
  dbWriteEnabled: boolean
  edgeCommandExecution: boolean
  linkCommandExecution: boolean
  deviceControlEnabled: boolean
  productionActivation: boolean
  visualStyle: string
  policyGateCount: number
  controlPathStageCount: number
  blockedDirectPathCount: number
  evidenceLinkCount: number
  approvalBoundaryCount: number
  executionBoundaryStatus: string
  integrationStatus: string
  limitations: string[]
  guardrails: string[]
}

export interface CodePolicyGateItem {
  gateId: string
  gateName: string
  purpose: string
  sourceModule: string
  protectedActionType: string
  decisionMode: string
  allowedDecisionStates: string[]
  readOnly: boolean
  mutationEnabled: boolean
  runtimeLinked: boolean
}

export interface CodePolicyControlPath {
  graphMode: string
  nodes: Record<string, unknown>[]
  edges: Record<string, unknown>[]
  directToDeviceEdgesAbsent: boolean
}

export interface CodePolicyApprovalBoundary {
  approvalStages: Record<string, unknown>[]
  approvalExecutionEnabled: boolean
}

export interface CodePolicyExecutionBoundary {
  directPathsBlocked: string[]
  requiredPath: string
  r1Status: Record<string, boolean>
  executionBoundaryStatus: string
}

export interface CodePolicyEvidenceLinkage {
  sourceObjectTypes: string[]
  evidenceMode: string
  evidenceWriteEnabled: boolean
  hashOnlyLocalPreview: boolean
  links: Record<string, unknown>[]
}

function asRecord(value: unknown): Record<string, unknown> {
  return typeof value === 'object' && value !== null ? (value as Record<string, unknown>) : {}
}

function asRecordArray(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value)
    ? value.filter((item) => typeof item === 'object' && item !== null).map((item) => item as Record<string, unknown>)
    : []
}

function asStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.map((item) => String(item)) : []
}

function unwrap<T>(body: unknown): T {
  if (typeof body === 'object' && body !== null && 'data' in body) {
    return (body as { data: T }).data
  }
  return body as T
}

function normalizeSummary(raw: unknown): CodePolicySummary {
  const data = asRecord(raw)
  return {
    scope: String(data.scope ?? 'CODE_GA_R1'),
    moduleId: String(data.moduleId ?? 'code-policy'),
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    runtimeEnabled: Boolean(data.runtimeEnabled),
    approvalExecutionEnabled: Boolean(data.approvalExecutionEnabled),
    policyMutationEnabled: Boolean(data.policyMutationEnabled),
    workflowExecutionEnabled: Boolean(data.workflowExecutionEnabled),
    commandExecutionEnabled: Boolean(data.commandExecutionEnabled),
    dbWriteEnabled: Boolean(data.dbWriteEnabled),
    edgeCommandExecution: Boolean(data.edgeCommandExecution),
    linkCommandExecution: Boolean(data.linkCommandExecution),
    deviceControlEnabled: Boolean(data.deviceControlEnabled),
    productionActivation: Boolean(data.productionActivation),
    visualStyle: String(data.visualStyle ?? 'VANTARIS_LIGHT_OPERATIONS_CONSOLE'),
    policyGateCount: Number(data.policyGateCount ?? 0),
    controlPathStageCount: Number(data.controlPathStageCount ?? 0),
    blockedDirectPathCount: Number(data.blockedDirectPathCount ?? 0),
    evidenceLinkCount: Number(data.evidenceLinkCount ?? 0),
    approvalBoundaryCount: Number(data.approvalBoundaryCount ?? 0),
    executionBoundaryStatus: String(data.executionBoundaryStatus ?? 'preview-only-not-executable'),
    integrationStatus: String(data.integrationStatus ?? 'available'),
    limitations: asStringArray(data.limitations),
    guardrails: asStringArray(data.guardrails),
  }
}

function normalizeGate(raw: unknown): CodePolicyGateItem {
  const data = asRecord(raw)
  return {
    gateId: String(data.gateId ?? ''),
    gateName: String(data.gateName ?? ''),
    purpose: String(data.purpose ?? ''),
    sourceModule: String(data.sourceModule ?? ''),
    protectedActionType: String(data.protectedActionType ?? ''),
    decisionMode: String(data.decisionMode ?? 'preview-only'),
    allowedDecisionStates: asStringArray(data.allowedDecisionStates),
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    mutationEnabled: Boolean(data.mutationEnabled),
    runtimeLinked: Boolean(data.runtimeLinked),
  }
}

export async function getCodePolicySummary(): Promise<CodePolicySummary> {
  return normalizeSummary(unwrap(await request.get('/v1/one/code-policy/summary')))
}

export async function getCodePolicyGates(): Promise<CodePolicyGateItem[]> {
  const data = asRecord(unwrap(await request.get('/v1/one/code-policy/policy-gates')))
  return asRecordArray(data.items).map((item) => normalizeGate(item))
}

export async function getCodePolicyControlPath(): Promise<CodePolicyControlPath> {
  const data = asRecord(unwrap(await request.get('/v1/one/code-policy/control-path')))
  return {
    graphMode: String(data.graphMode ?? 'local-readonly-code-policy-projection'),
    nodes: asRecordArray(data.nodes),
    edges: asRecordArray(data.edges),
    directToDeviceEdgesAbsent: data.directToDeviceEdgesAbsent !== undefined ? Boolean(data.directToDeviceEdgesAbsent) : true,
  }
}

export async function getCodePolicyApprovalBoundary(): Promise<CodePolicyApprovalBoundary> {
  const data = asRecord(unwrap(await request.get('/v1/one/code-policy/approval-boundary')))
  return {
    approvalStages: asRecordArray(data.approvalStages),
    approvalExecutionEnabled: Boolean(data.approvalExecutionEnabled),
  }
}

export async function getCodePolicyExecutionBoundary(): Promise<CodePolicyExecutionBoundary> {
  const data = asRecord(unwrap(await request.get('/v1/one/code-policy/execution-boundary')))
  return {
    directPathsBlocked: asStringArray(data.directPathsBlocked),
    requiredPath: String(data.requiredPath ?? ''),
    r1Status: asRecord(data.r1Status) as Record<string, boolean>,
    executionBoundaryStatus: String(data.executionBoundaryStatus ?? 'preview-only-not-executable'),
  }
}

export async function getCodePolicyEvidenceLinkage(): Promise<CodePolicyEvidenceLinkage> {
  const data = asRecord(unwrap(await request.get('/v1/one/code-policy/evidence-linkage')))
  return {
    sourceObjectTypes: asStringArray(data.sourceObjectTypes),
    evidenceMode: String(data.evidenceMode ?? 'read-only-preview'),
    evidenceWriteEnabled: Boolean(data.evidenceWriteEnabled),
    hashOnlyLocalPreview: Boolean(data.hashOnlyLocalPreview),
    links: asRecordArray(data.links),
  }
}

