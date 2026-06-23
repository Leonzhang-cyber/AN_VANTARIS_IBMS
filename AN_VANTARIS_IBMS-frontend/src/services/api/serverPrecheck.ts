import request from './request'

export interface ServerPrecheckSummary {
  scope: string
  moduleId: string
  readOnly: boolean
  sshExecuted: boolean
  deploymentExecuted: boolean
  installExecuted: boolean
  dbConnectionExecuted: boolean
  dbMigrationExecuted: boolean
  dbWriteEnabled: boolean
  healthcheckRuntimeExecuted: boolean
  nginxSetupExecuted: boolean
  pm2SetupExecuted: boolean
  systemdSetupExecuted: boolean
  edgeCommandExecution: boolean
  linkCommandExecution: boolean
  deviceControlEnabled: boolean
  productionActivation: boolean
  visualStyle: string
  appServerIp: string
  dbServerIp: string
  appServerRoleCount: number
  dbServerRoleCount: number
  checklistTotal: number
  blockersTotal: number
  readyForServerAccess: boolean
  readyForDeployment: boolean
  productionGaStatus: string
  pushExecuted: boolean
  remoteAligned: boolean
  limitations: string[]
}

export interface ServerPlan {
  appServer: Record<string, unknown>
  dbServer: Record<string, unknown>
  networkAssumption: string[]
}

export interface ChecklistItem {
  itemId: string
  category: string
  title: string
  expectedEvidence: string
  currentStatus: string
  executionStatus: string
  ownerRole: string
}

export interface BlockerItem {
  blockerId: string
  title: string
  severity: string
  affectedServer: string
  reason: string
  requiredActionBeforeGA: string
  currentStatus: string
}

export interface HandoffReadiness {
  customerHandoffStatus: string
  serverPrecheckStatus: string
  deploymentStatus: string
  dbActivationStatus: string
  productionGaStatus: string
  nextRecommendedStep: string
  linkedModules: string[]
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

function normalizeSummary(raw: unknown): ServerPrecheckSummary {
  const data = asRecord(raw)
  return {
    scope: String(data.scope ?? 'SERVER_PRECHECK_R1'),
    moduleId: String(data.moduleId ?? 'server-precheck'),
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    sshExecuted: Boolean(data.sshExecuted),
    deploymentExecuted: Boolean(data.deploymentExecuted),
    installExecuted: Boolean(data.installExecuted),
    dbConnectionExecuted: Boolean(data.dbConnectionExecuted),
    dbMigrationExecuted: Boolean(data.dbMigrationExecuted),
    dbWriteEnabled: Boolean(data.dbWriteEnabled),
    healthcheckRuntimeExecuted: Boolean(data.healthcheckRuntimeExecuted),
    nginxSetupExecuted: Boolean(data.nginxSetupExecuted),
    pm2SetupExecuted: Boolean(data.pm2SetupExecuted),
    systemdSetupExecuted: Boolean(data.systemdSetupExecuted),
    edgeCommandExecution: Boolean(data.edgeCommandExecution),
    linkCommandExecution: Boolean(data.linkCommandExecution),
    deviceControlEnabled: Boolean(data.deviceControlEnabled),
    productionActivation: Boolean(data.productionActivation),
    visualStyle: String(data.visualStyle ?? 'VANTARIS_LIGHT_OPERATIONS_CONSOLE'),
    appServerIp: String(data.appServerIp ?? '192.168.60.21'),
    dbServerIp: String(data.dbServerIp ?? '192.168.60.22'),
    appServerRoleCount: Number(data.appServerRoleCount ?? 0),
    dbServerRoleCount: Number(data.dbServerRoleCount ?? 0),
    checklistTotal: Number(data.checklistTotal ?? 0),
    blockersTotal: Number(data.blockersTotal ?? 0),
    readyForServerAccess: Boolean(data.readyForServerAccess),
    readyForDeployment: Boolean(data.readyForDeployment),
    productionGaStatus: String(data.productionGaStatus ?? 'NOT_YET'),
    pushExecuted: Boolean(data.pushExecuted),
    remoteAligned: Boolean(data.remoteAligned),
    limitations: asStringArray(data.limitations),
  }
}

function normalizeChecklist(raw: unknown): ChecklistItem {
  const data = asRecord(raw)
  return {
    itemId: String(data.itemId ?? ''),
    category: String(data.category ?? ''),
    title: String(data.title ?? ''),
    expectedEvidence: String(data.expectedEvidence ?? ''),
    currentStatus: String(data.currentStatus ?? ''),
    executionStatus: String(data.executionStatus ?? ''),
    ownerRole: String(data.ownerRole ?? ''),
  }
}

function normalizeBlocker(raw: unknown): BlockerItem {
  const data = asRecord(raw)
  return {
    blockerId: String(data.blockerId ?? ''),
    title: String(data.title ?? ''),
    severity: String(data.severity ?? ''),
    affectedServer: String(data.affectedServer ?? ''),
    reason: String(data.reason ?? ''),
    requiredActionBeforeGA: String(data.requiredActionBeforeGA ?? ''),
    currentStatus: String(data.currentStatus ?? ''),
  }
}

export async function getServerPrecheckSummary(): Promise<ServerPrecheckSummary> {
  return normalizeSummary(unwrap(await request.get('/v1/one/server-precheck/summary')))
}

export async function getServerPrecheckPlan(): Promise<ServerPlan> {
  const data = asRecord(unwrap(await request.get('/v1/one/server-precheck/server-plan')))
  return {
    appServer: asRecord(data.appServer),
    dbServer: asRecord(data.dbServer),
    networkAssumption: asStringArray(data.networkAssumption),
  }
}

export async function getServerPrecheckAppServer(): Promise<Record<string, unknown>> {
  return asRecord(unwrap(await request.get('/v1/one/server-precheck/app-server')))
}

export async function getServerPrecheckDbServer(): Promise<Record<string, unknown>> {
  return asRecord(unwrap(await request.get('/v1/one/server-precheck/db-server')))
}

export async function getServerPrecheckChecklist(): Promise<ChecklistItem[]> {
  const data = asRecord(unwrap(await request.get('/v1/one/server-precheck/checklist')))
  return asRecordArray(data.items).map((item) => normalizeChecklist(item))
}

export async function getServerPrecheckBlockers(): Promise<BlockerItem[]> {
  const data = asRecord(unwrap(await request.get('/v1/one/server-precheck/blockers')))
  return asRecordArray(data.items).map((item) => normalizeBlocker(item))
}

export async function getServerPrecheckHandoff(): Promise<HandoffReadiness> {
  const data = asRecord(unwrap(await request.get('/v1/one/server-precheck/handoff-readiness')))
  return {
    customerHandoffStatus: String(data.customerHandoffStatus ?? ''),
    serverPrecheckStatus: String(data.serverPrecheckStatus ?? ''),
    deploymentStatus: String(data.deploymentStatus ?? ''),
    dbActivationStatus: String(data.dbActivationStatus ?? ''),
    productionGaStatus: String(data.productionGaStatus ?? 'NOT_YET'),
    nextRecommendedStep: String(data.nextRecommendedStep ?? ''),
    linkedModules: asStringArray(data.linkedModules),
  }
}

