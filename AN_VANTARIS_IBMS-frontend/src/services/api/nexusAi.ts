import request from './request'

export interface NexusBranchSummary {
  scope: string
  moduleId: string
  readOnly: boolean
  aiRuntimeEnabled: boolean
  modelApiCallEnabled: boolean
  autoFixEnabled: boolean
  codeMutationEnabled: boolean
  workflowExecutionEnabled: boolean
  dbWriteEnabled: boolean
  edgeCommandExecution: boolean
  linkCommandExecution: boolean
  deviceControlEnabled: boolean
  productionActivation: boolean
  visualStyle: string
  branch: string
  baselineRemoteHead: string
  currentLocalHead: string
  localCommitCountSinceRemote: number
  auditedCommits: number
  auditedModules: number
  riskCount: number
  customerDemoReadinessImpact: string
  productionGaStatus: string
  remoteAligned: boolean
  pushExecuted: boolean
  deploymentExecuted: boolean
  limitations: string[]
}

export interface NexusCommitItem {
  commitHash: string
  shortHash: string
  title: string
  localTag: string
  changeType: string
  modulesTouched: string[]
  customerDemoImpact: string
  riskBoundary: string
  validationMarker: string
  buildStatus: string
  remoteStatus: string
}

export interface NexusModuleItem {
  moduleId: string
  moduleName: string
  readinessBefore: string
  readinessAfter: string
  linkageAdded: string
  evidenceLinkage: string
  reportLinkage: string
  guardrails: string
  productionGaStatus: string
}

export interface NexusRiskItem {
  riskId: string
  title: string
  severity: string
  status: string
  affectedModules: string[]
  mitigation: string
  boundary: string
  productionImpact: string
}

export interface NexusEvidenceLinkage {
  auditMode: string
  ucdeEvidenceReferences: string[]
  reportsReferences: string[]
  registryReferences: string[]
  validationMarkers: string[]
  localFreezeTags: string[]
}

export interface NexusCustomerDemoImpact {
  positiveImpact: string[]
  remainingGaps: string[]
  recommendation: string[]
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

function normalizeSummary(raw: unknown): NexusBranchSummary {
  const data = asRecord(raw)
  return {
    scope: String(data.scope ?? 'NEXUSAI_GA_R3'),
    moduleId: String(data.moduleId ?? 'nexus-ai-branch-audit'),
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    aiRuntimeEnabled: Boolean(data.aiRuntimeEnabled),
    modelApiCallEnabled: Boolean(data.modelApiCallEnabled),
    autoFixEnabled: Boolean(data.autoFixEnabled),
    codeMutationEnabled: Boolean(data.codeMutationEnabled),
    workflowExecutionEnabled: Boolean(data.workflowExecutionEnabled),
    dbWriteEnabled: Boolean(data.dbWriteEnabled),
    edgeCommandExecution: Boolean(data.edgeCommandExecution),
    linkCommandExecution: Boolean(data.linkCommandExecution),
    deviceControlEnabled: Boolean(data.deviceControlEnabled),
    productionActivation: Boolean(data.productionActivation),
    visualStyle: String(data.visualStyle ?? 'VANTARIS_LIGHT_OPERATIONS_CONSOLE'),
    branch: String(data.branch ?? ''),
    baselineRemoteHead: String(data.baselineRemoteHead ?? ''),
    currentLocalHead: String(data.currentLocalHead ?? ''),
    localCommitCountSinceRemote: Number(data.localCommitCountSinceRemote ?? 0),
    auditedCommits: Number(data.auditedCommits ?? 0),
    auditedModules: Number(data.auditedModules ?? 0),
    riskCount: Number(data.riskCount ?? 0),
    customerDemoReadinessImpact: String(data.customerDemoReadinessImpact ?? ''),
    productionGaStatus: String(data.productionGaStatus ?? 'NOT_YET'),
    remoteAligned: Boolean(data.remoteAligned),
    pushExecuted: Boolean(data.pushExecuted),
    deploymentExecuted: Boolean(data.deploymentExecuted),
    limitations: asStringArray(data.limitations),
  }
}

function normalizeCommit(raw: unknown): NexusCommitItem {
  const data = asRecord(raw)
  return {
    commitHash: String(data.commitHash ?? ''),
    shortHash: String(data.shortHash ?? ''),
    title: String(data.title ?? ''),
    localTag: String(data.localTag ?? ''),
    changeType: String(data.changeType ?? ''),
    modulesTouched: asStringArray(data.modulesTouched),
    customerDemoImpact: String(data.customerDemoImpact ?? ''),
    riskBoundary: String(data.riskBoundary ?? ''),
    validationMarker: String(data.validationMarker ?? ''),
    buildStatus: String(data.buildStatus ?? ''),
    remoteStatus: String(data.remoteStatus ?? ''),
  }
}

function normalizeModule(raw: unknown): NexusModuleItem {
  const data = asRecord(raw)
  return {
    moduleId: String(data.moduleId ?? ''),
    moduleName: String(data.moduleName ?? ''),
    readinessBefore: String(data.readinessBefore ?? ''),
    readinessAfter: String(data.readinessAfter ?? ''),
    linkageAdded: String(data.linkageAdded ?? ''),
    evidenceLinkage: String(data.evidenceLinkage ?? ''),
    reportLinkage: String(data.reportLinkage ?? ''),
    guardrails: String(data.guardrails ?? ''),
    productionGaStatus: String(data.productionGaStatus ?? 'NOT_YET'),
  }
}

function normalizeRisk(raw: unknown): NexusRiskItem {
  const data = asRecord(raw)
  return {
    riskId: String(data.riskId ?? ''),
    title: String(data.title ?? ''),
    severity: String(data.severity ?? ''),
    status: String(data.status ?? ''),
    affectedModules: asStringArray(data.affectedModules),
    mitigation: String(data.mitigation ?? ''),
    boundary: String(data.boundary ?? ''),
    productionImpact: String(data.productionImpact ?? ''),
  }
}

export async function getNexusBranchSummary(): Promise<NexusBranchSummary> {
  return normalizeSummary(unwrap(await request.get('/v1/one/nexus-ai/branch-audit/summary')))
}

export async function getNexusBranchCommits(): Promise<NexusCommitItem[]> {
  const data = asRecord(unwrap(await request.get('/v1/one/nexus-ai/branch-audit/commits')))
  return asRecordArray(data.items).map((item) => normalizeCommit(item))
}

export async function getNexusBranchModules(): Promise<NexusModuleItem[]> {
  const data = asRecord(unwrap(await request.get('/v1/one/nexus-ai/branch-audit/modules')))
  return asRecordArray(data.items).map((item) => normalizeModule(item))
}

export async function getNexusBranchRisks(): Promise<NexusRiskItem[]> {
  const data = asRecord(unwrap(await request.get('/v1/one/nexus-ai/branch-audit/risks')))
  return asRecordArray(data.items).map((item) => normalizeRisk(item))
}

export async function getNexusEvidenceLinkage(): Promise<NexusEvidenceLinkage> {
  const data = asRecord(unwrap(await request.get('/v1/one/nexus-ai/branch-audit/evidence-linkage')))
  return {
    auditMode: String(data.auditMode ?? 'read-only-branch-diff-preview'),
    ucdeEvidenceReferences: asStringArray(data.ucdeEvidenceReferences),
    reportsReferences: asStringArray(data.reportsReferences),
    registryReferences: asStringArray(data.registryReferences),
    validationMarkers: asStringArray(data.validationMarkers),
    localFreezeTags: asStringArray(data.localFreezeTags),
  }
}

export async function getNexusCustomerDemoImpact(): Promise<NexusCustomerDemoImpact> {
  const data = asRecord(unwrap(await request.get('/v1/one/nexus-ai/branch-audit/customer-demo-impact')))
  return {
    positiveImpact: asStringArray(data.positiveImpact),
    remainingGaps: asStringArray(data.remainingGaps),
    recommendation: asStringArray(data.recommendation),
  }
}

