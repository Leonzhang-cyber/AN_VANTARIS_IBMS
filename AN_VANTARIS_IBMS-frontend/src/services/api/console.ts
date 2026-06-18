import request from './request'

export interface ConsoleHealth {
  status: string
  moduleId: string
  moduleName: string
  runtimeMode: string
  provider: string
  sourceSemantics: string
  readOnly: boolean
  controlActionsEnabled: boolean
  certified: boolean
  iec62443Certified: boolean
}

export interface PlatformModuleSummary {
  moduleId: string
  moduleName: string
  moduleType: string
  runtimeStatus: 'ready' | 'foundation' | 'planned' | 'not-integrated'
  readinessLevel: string
  route: string
  frontendReady: boolean
  backendReady: boolean
  auditReadiness: boolean
  permissionMode: string
  dataPersistenceMode: string
  securityNotes: string
  certified: boolean
  iec62443Certified: boolean
}

export interface ModuleHealthDetailItem {
  status: 'ready' | 'foundation' | 'planned' | 'not-integrated' | 'limited'
  label: string
  message: string
  score: number
}

export interface ModuleSecurityFlags {
  realRbacIntegrated: boolean
  dbAuditIntegrated: boolean
  siemIntegrated: boolean
  ucdeRuntimeIntegrated: boolean
  edgeRuntimeIntegrated: boolean
  linkRuntimeIntegrated: boolean
  certified: boolean
  iec62443Certified: boolean
}

export interface ModuleReadinessRecord {
  moduleId: string
  moduleName: string
  moduleType: string
  domain: string
  route: string
  runtimeStatus: 'ready' | 'foundation' | 'planned' | 'not-integrated'
  readinessLevel: string
  lifecycleStage: string
  frontendReady: boolean
  backendReady: boolean
  apiReady: boolean
  auditReadiness: string
  permissionMode: string
  dataPersistenceMode: string
  integrationMode: string
  healthStatus: string
  healthScore: number
  healthDetails: Record<string, ModuleHealthDetailItem>
  securityFlags: ModuleSecurityFlags
  limitations: string[]
  dependencies: string[]
  lastUpdated: string
  readOnly: boolean
  controlActionsEnabled: boolean
  certified: boolean
  iec62443Certified: boolean
}

export interface ModuleReadinessRegistryResponse {
  items: ModuleReadinessRecord[]
}

export interface ModuleHealthDetailsResponse {
  items: ModuleReadinessRecord[]
}

export interface ModuleReadinessSummary {
  totalModules: number
  readyModules: number
  foundationModules: number
  plannedModules: number
  notIntegratedModules: number
  auditReadyModules: number
  certifiedModules: number
  iec62443CertifiedModules: number
  averageHealthScore: number
  lowestHealthModules: Array<{ moduleId: string; healthScore: number }>
  highestHealthModules: Array<{ moduleId: string; healthScore: number }>
}

export interface OperationsDashboardSummary {
  totals: {
    totalModules: number
    readyModules: number
    foundationModules: number
    plannedModules: number
    auditReadyModules: number
    certifiedModules: number
    iec62443CertifiedModules: number
  }
  highlights: string[]
  warnings: string[]
  securityPosture: {
    auditReadinessFoundation: boolean
    realRbacIntegrated: boolean
    dbAuditIntegrated: boolean
    siemIntegrated: boolean
    ucdeRuntimeIntegrated: boolean
    certified: boolean
    iec62443Certified: boolean
  }
}

export interface ReportsReadinessSnapshot {
  routeReady: boolean
  menuReady: boolean
  queryReady: boolean
  exportReady: boolean
  manifestReady: boolean
  auditStoreReady: boolean
  auditVerifyReady: boolean
  permissionPlaceholderReady: boolean
  auditExportReady: boolean
  certified: boolean
  iec62443Certified: boolean
  limitations: string[]
}

function asRecord(value: unknown): Record<string, unknown> {
  return typeof value === 'object' && value !== null ? (value as Record<string, unknown>) : {}
}

function asStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.map((item) => String(item)) : []
}

function unwrapData<T>(body: unknown): T {
  if (typeof body === 'object' && body !== null && 'data' in body) {
    return (body as { data: T }).data
  }
  return body as T
}

function normalizeHealth(raw: unknown): ConsoleHealth {
  const data = asRecord(raw)
  return {
    status: String(data.status ?? 'unknown'),
    moduleId: String(data.moduleId ?? 'uconsole'),
    moduleName: String(data.moduleName ?? 'UConsole / Platform Operations Dashboard'),
    runtimeMode: String(data.runtimeMode ?? 'skeleton'),
    provider: String(data.provider ?? 'local-platform-summary'),
    sourceSemantics: String(data.sourceSemantics ?? 'ibms-neutral'),
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    controlActionsEnabled: Boolean(data.controlActionsEnabled),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeModule(raw: unknown): PlatformModuleSummary {
  const data = asRecord(raw)
  return {
    moduleId: String(data.moduleId ?? ''),
    moduleName: String(data.moduleName ?? ''),
    moduleType: String(data.moduleType ?? 'platform-module'),
    runtimeStatus: String(data.runtimeStatus ?? 'planned') as PlatformModuleSummary['runtimeStatus'],
    readinessLevel: String(data.readinessLevel ?? 'not-integrated'),
    route: String(data.route ?? ''),
    frontendReady: Boolean(data.frontendReady),
    backendReady: Boolean(data.backendReady),
    auditReadiness: Boolean(data.auditReadiness),
    permissionMode: String(data.permissionMode ?? 'not-integrated'),
    dataPersistenceMode: String(data.dataPersistenceMode ?? 'not-integrated'),
    securityNotes: String(data.securityNotes ?? ''),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeHealthDetail(raw: unknown): ModuleHealthDetailItem {
  const data = asRecord(raw)
  return {
    status: String(data.status ?? 'planned') as ModuleHealthDetailItem['status'],
    label: String(data.label ?? ''),
    message: String(data.message ?? ''),
    score: Number(data.score ?? 0),
  }
}

function normalizeSecurityFlags(raw: unknown): ModuleSecurityFlags {
  const data = asRecord(raw)
  return {
    realRbacIntegrated: Boolean(data.realRbacIntegrated),
    dbAuditIntegrated: Boolean(data.dbAuditIntegrated),
    siemIntegrated: Boolean(data.siemIntegrated),
    ucdeRuntimeIntegrated: Boolean(data.ucdeRuntimeIntegrated),
    edgeRuntimeIntegrated: Boolean(data.edgeRuntimeIntegrated),
    linkRuntimeIntegrated: Boolean(data.linkRuntimeIntegrated),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeReadinessRecord(raw: unknown): ModuleReadinessRecord {
  const data = asRecord(raw)
  const healthDetailsRaw = asRecord(data.healthDetails)
  const normalizedDetails: Record<string, ModuleHealthDetailItem> = {}
  for (const [key, value] of Object.entries(healthDetailsRaw)) {
    normalizedDetails[key] = normalizeHealthDetail(value)
  }
  return {
    moduleId: String(data.moduleId ?? ''),
    moduleName: String(data.moduleName ?? ''),
    moduleType: String(data.moduleType ?? 'platform-module'),
    domain: String(data.domain ?? 'platform-operations'),
    route: String(data.route ?? ''),
    runtimeStatus: String(data.runtimeStatus ?? 'planned') as ModuleReadinessRecord['runtimeStatus'],
    readinessLevel: String(data.readinessLevel ?? 'not-integrated'),
    lifecycleStage: String(data.lifecycleStage ?? 'planned'),
    frontendReady: Boolean(data.frontendReady),
    backendReady: Boolean(data.backendReady),
    apiReady: Boolean(data.apiReady),
    auditReadiness: String(data.auditReadiness ?? 'planned'),
    permissionMode: String(data.permissionMode ?? 'not-integrated'),
    dataPersistenceMode: String(data.dataPersistenceMode ?? 'not-integrated'),
    integrationMode: String(data.integrationMode ?? 'not-integrated'),
    healthStatus: String(data.healthStatus ?? 'planned'),
    healthScore: Number(data.healthScore ?? 0),
    healthDetails: normalizedDetails,
    securityFlags: normalizeSecurityFlags(data.securityFlags),
    limitations: asStringArray(data.limitations),
    dependencies: asStringArray(data.dependencies),
    lastUpdated: String(data.lastUpdated ?? ''),
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    controlActionsEnabled: Boolean(data.controlActionsEnabled),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeSummary(raw: unknown): OperationsDashboardSummary {
  const data = asRecord(raw)
  const totals = asRecord(data.totals)
  const security = asRecord(data.securityPosture)
  return {
    totals: {
      totalModules: Number(totals.totalModules ?? 0),
      readyModules: Number(totals.readyModules ?? 0),
      foundationModules: Number(totals.foundationModules ?? 0),
      plannedModules: Number(totals.plannedModules ?? 0),
      auditReadyModules: Number(totals.auditReadyModules ?? 0),
      certifiedModules: Number(totals.certifiedModules ?? 0),
      iec62443CertifiedModules: Number(totals.iec62443CertifiedModules ?? 0),
    },
    highlights: asStringArray(data.highlights),
    warnings: asStringArray(data.warnings),
    securityPosture: {
      auditReadinessFoundation: Boolean(security.auditReadinessFoundation),
      realRbacIntegrated: Boolean(security.realRbacIntegrated),
      dbAuditIntegrated: Boolean(security.dbAuditIntegrated),
      siemIntegrated: Boolean(security.siemIntegrated),
      ucdeRuntimeIntegrated: Boolean(security.ucdeRuntimeIntegrated),
      certified: Boolean(security.certified),
      iec62443Certified: Boolean(security.iec62443Certified),
    },
  }
}

function normalizeReportsReadiness(raw: unknown): ReportsReadinessSnapshot {
  const data = asRecord(raw)
  return {
    routeReady: Boolean(data.routeReady),
    menuReady: Boolean(data.menuReady),
    queryReady: Boolean(data.queryReady),
    exportReady: Boolean(data.exportReady),
    manifestReady: Boolean(data.manifestReady),
    auditStoreReady: Boolean(data.auditStoreReady),
    auditVerifyReady: Boolean(data.auditVerifyReady),
    permissionPlaceholderReady: Boolean(data.permissionPlaceholderReady),
    auditExportReady: Boolean(data.auditExportReady),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
    limitations: asStringArray(data.limitations),
  }
}

export async function getConsoleHealth(): Promise<ConsoleHealth> {
  const { data } = await request.get('/v1/console/health')
  return normalizeHealth(unwrapData<unknown>(data))
}

export async function getConsoleModules(): Promise<PlatformModuleSummary[]> {
  const { data } = await request.get('/v1/console/modules')
  const payload = unwrapData<{ items?: unknown[] } | unknown[]>(data)
  if (Array.isArray(payload)) {
    return payload.map((item) => normalizeModule(item))
  }
  return Array.isArray(payload.items) ? payload.items.map((item) => normalizeModule(item)) : []
}

export async function getConsoleReadinessRegistry(): Promise<ModuleReadinessRegistryResponse> {
  const { data } = await request.get('/v1/console/readiness/registry')
  const payload = unwrapData<{ items?: unknown[] } | unknown>(data)
  const body = asRecord(payload)
  return {
    items: Array.isArray(body.items) ? body.items.map((item) => normalizeReadinessRecord(item)) : [],
  }
}

export async function getConsoleModuleHealth(moduleId: string): Promise<ModuleReadinessRecord> {
  const { data } = await request.get(`/v1/console/modules/${encodeURIComponent(moduleId)}/health`)
  return normalizeReadinessRecord(unwrapData<unknown>(data))
}

export async function getConsoleAllModuleHealth(): Promise<ModuleHealthDetailsResponse> {
  const { data } = await request.get('/v1/console/modules/health')
  const payload = unwrapData<{ items?: unknown[] } | unknown>(data)
  const body = asRecord(payload)
  return {
    items: Array.isArray(body.items) ? body.items.map((item) => normalizeReadinessRecord(item)) : [],
  }
}

export async function getConsoleReadinessSummary(): Promise<ModuleReadinessSummary> {
  const { data } = await request.get('/v1/console/readiness/summary')
  const body = asRecord(unwrapData<unknown>(data))
  const lowest = Array.isArray(body.lowestHealthModules)
    ? body.lowestHealthModules.map((item) => {
        const row = asRecord(item)
        return { moduleId: String(row.moduleId ?? ''), healthScore: Number(row.healthScore ?? 0) }
      })
    : []
  const highest = Array.isArray(body.highestHealthModules)
    ? body.highestHealthModules.map((item) => {
        const row = asRecord(item)
        return { moduleId: String(row.moduleId ?? ''), healthScore: Number(row.healthScore ?? 0) }
      })
    : []
  return {
    totalModules: Number(body.totalModules ?? 0),
    readyModules: Number(body.readyModules ?? 0),
    foundationModules: Number(body.foundationModules ?? 0),
    plannedModules: Number(body.plannedModules ?? 0),
    notIntegratedModules: Number(body.notIntegratedModules ?? 0),
    auditReadyModules: Number(body.auditReadyModules ?? 0),
    certifiedModules: Number(body.certifiedModules ?? 0),
    iec62443CertifiedModules: Number(body.iec62443CertifiedModules ?? 0),
    averageHealthScore: Number(body.averageHealthScore ?? 0),
    lowestHealthModules: lowest,
    highestHealthModules: highest,
  }
}

export async function getConsoleOperationsSummary(): Promise<OperationsDashboardSummary> {
  const { data } = await request.get('/v1/console/operations/summary')
  return normalizeSummary(unwrapData<unknown>(data))
}

export async function getConsoleReportsReadiness(): Promise<ReportsReadinessSnapshot> {
  const { data } = await request.get('/v1/console/reports/readiness')
  return normalizeReportsReadiness(unwrapData<unknown>(data))
}

