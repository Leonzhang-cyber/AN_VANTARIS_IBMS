import request from './request'

export interface FoundationDiagnosticsWorkspace {
  scope: string
  mode: string
  readinessLevel: string
  visualStyle: string
  engineerDiagnosticsWorkspace: boolean
  appNonDbTarget: string
  dbOnlyTarget: string
  sshExecuted: boolean
  deploymentExecuted: boolean
  installExecuted: boolean
  uninstallExecuted: boolean
  rollbackExecuted: boolean
  dbConnectionExecuted: boolean
  dbMigrationExecuted: boolean
  dbWrite: boolean
  edgeCommandExecution: boolean
  linkCommandExecution: boolean
  deviceControl: boolean
  runtimeActivation: boolean
  productionActivation: boolean
  futureExecutionPath: string
  title: string
  overviewCards: Array<{ label: string; value: string; status: string }>
  serverPlan: Record<string, Record<string, unknown>>
  packageReadiness: Array<Record<string, unknown>>
  edgeReadiness: Record<string, unknown>
  linkReadiness: Record<string, unknown>
  dbReadiness: Record<string, unknown>
  contractsReadiness: Record<string, unknown>
  offlineChecklist: string[]
  healthcheckPreview: Array<Record<string, unknown>>
  packageIntegrityPreview: Array<Record<string, unknown>>
  rollbackReadiness: Array<Record<string, unknown>>
  guardrails: string[]
}

function asRecord(value: unknown): Record<string, unknown> {
  return typeof value === 'object' && value !== null ? (value as Record<string, unknown>) : {}
}

function asArray(value: unknown): Array<Record<string, unknown>> {
  return Array.isArray(value) ? value.filter((item) => typeof item === 'object' && item !== null).map((item) => item as Record<string, unknown>) : []
}

function asStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.map((item) => String(item)) : []
}

function unwrap<T>(body: unknown): T {
  if (typeof body === 'object' && body !== null && 'data' in body) return (body as { data: T }).data
  return body as T
}

function normalize(raw: unknown): FoundationDiagnosticsWorkspace {
  const data = asRecord(raw)
  return {
    scope: String(data.scope ?? 'FOUNDATION_DIAGNOSTICS_GA_R1'),
    mode: String(data.mode ?? 'read_only'),
    readinessLevel: String(data.readinessLevel ?? 'ENGINEER_DIAGNOSTICS_WORKSPACE'),
    visualStyle: String(data.visualStyle ?? 'VANTARIS_LIGHT_OPERATIONS_CONSOLE'),
    engineerDiagnosticsWorkspace: data.engineerDiagnosticsWorkspace !== undefined ? Boolean(data.engineerDiagnosticsWorkspace) : true,
    appNonDbTarget: String(data.appNonDbTarget ?? '192.168.60.21'),
    dbOnlyTarget: String(data.dbOnlyTarget ?? '192.168.60.22'),
    sshExecuted: Boolean(data.sshExecuted),
    deploymentExecuted: Boolean(data.deploymentExecuted),
    installExecuted: Boolean(data.installExecuted),
    uninstallExecuted: Boolean(data.uninstallExecuted),
    rollbackExecuted: Boolean(data.rollbackExecuted),
    dbConnectionExecuted: Boolean(data.dbConnectionExecuted),
    dbMigrationExecuted: Boolean(data.dbMigrationExecuted),
    dbWrite: Boolean(data.dbWrite),
    edgeCommandExecution: Boolean(data.edgeCommandExecution),
    linkCommandExecution: Boolean(data.linkCommandExecution),
    deviceControl: Boolean(data.deviceControl),
    runtimeActivation: Boolean(data.runtimeActivation),
    productionActivation: Boolean(data.productionActivation),
    futureExecutionPath: String(data.futureExecutionPath ?? ''),
    title: String(data.title ?? 'Foundation Diagnostics Workspace'),
    overviewCards: asArray(data.overviewCards).map((item) => ({
      label: String(item.label ?? ''),
      value: String(item.value ?? ''),
      status: String(item.status ?? ''),
    })),
    serverPlan: asRecord(data.serverPlan) as Record<string, Record<string, unknown>>,
    packageReadiness: asArray(data.packageReadiness),
    edgeReadiness: asRecord(data.edgeReadiness),
    linkReadiness: asRecord(data.linkReadiness),
    dbReadiness: asRecord(data.dbReadiness),
    contractsReadiness: asRecord(data.contractsReadiness),
    offlineChecklist: asStringArray(data.offlineChecklist),
    healthcheckPreview: asArray(data.healthcheckPreview),
    packageIntegrityPreview: asArray(data.packageIntegrityPreview),
    rollbackReadiness: asArray(data.rollbackReadiness),
    guardrails: asStringArray(data.guardrails),
  }
}

export async function getFoundationDiagnosticsWorkspace(): Promise<FoundationDiagnosticsWorkspace> {
  const { data } = await request.get('/v1/one/foundation-diagnostics/workspace')
  return normalize(unwrap<unknown>(data))
}
