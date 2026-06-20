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
  nextActions: string[]
  readinessNotes: string[]
  boundaryNotes: string[]
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

export interface ReadinessScoreComponent {
  score: number
  weight: number
  basis: string
}

export interface PlatformReadinessScore {
  overallScore: number
  scoreBand: 'early-foundation' | 'foundation' | 'readiness-candidate' | 'operational-candidate'
  scoreMode: 'registry-derived' | 'frontend-local-fallback'
  certified: boolean
  iec62443Certified: boolean
  components: {
    moduleReadiness: ReadinessScoreComponent
    auditReadiness: ReadinessScoreComponent
    securityPosture: ReadinessScoreComponent
    integrationReadiness: ReadinessScoreComponent
  }
  drivers: string[]
  risks: string[]
  recommendations: string[]
}

export interface PlatformNavigationItem {
  moduleId: string
  moduleName: string
  route: string | null
  launchEnabled: boolean
  launchLabel: string
  status: string
  disabledReason: string | null
  boundaryNote: string | null
  readOnly: boolean
  controlActionsEnabled: boolean
  certified: boolean
  iec62443Certified: boolean
}

export interface PlatformNavigationModel {
  navigationMode: string
  controlActionsEnabled: boolean
  items: PlatformNavigationItem[]
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
  readinessScore?: PlatformReadinessScore
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
    nextActions: asStringArray(data.nextActions),
    readinessNotes: asStringArray(data.readinessNotes),
    boundaryNotes: asStringArray(data.boundaryNotes),
    lastUpdated: String(data.lastUpdated ?? ''),
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    controlActionsEnabled: Boolean(data.controlActionsEnabled),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeReadinessScoreComponent(raw: unknown): ReadinessScoreComponent {
  const data = asRecord(raw)
  return {
    score: Number(data.score ?? 0),
    weight: Number(data.weight ?? 0),
    basis: String(data.basis ?? ''),
  }
}

function normalizeReadinessScore(raw: unknown): PlatformReadinessScore {
  const data = asRecord(raw)
  const components = asRecord(data.components)
  return {
    overallScore: Number(data.overallScore ?? 0),
    scoreBand: String(data.scoreBand ?? 'foundation') as PlatformReadinessScore['scoreBand'],
    scoreMode: String(data.scoreMode ?? 'registry-derived') as PlatformReadinessScore['scoreMode'],
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
    components: {
      moduleReadiness: normalizeReadinessScoreComponent(components.moduleReadiness),
      auditReadiness: normalizeReadinessScoreComponent(components.auditReadiness),
      securityPosture: normalizeReadinessScoreComponent(components.securityPosture),
      integrationReadiness: normalizeReadinessScoreComponent(components.integrationReadiness),
    },
    drivers: asStringArray(data.drivers),
    risks: asStringArray(data.risks),
    recommendations: asStringArray(data.recommendations),
  }
}

function normalizeNavigationItem(raw: unknown): PlatformNavigationItem {
  const data = asRecord(raw)
  const routeValue = data.route
  return {
    moduleId: String(data.moduleId ?? ''),
    moduleName: String(data.moduleName ?? ''),
    route: routeValue === null || routeValue === undefined || String(routeValue) === '' ? null : String(routeValue),
    launchEnabled: Boolean(data.launchEnabled),
    launchLabel: String(data.launchLabel ?? 'Open Module'),
    status: String(data.status ?? 'planned'),
    disabledReason: data.disabledReason === null || data.disabledReason === undefined ? null : String(data.disabledReason),
    boundaryNote: data.boundaryNote === null || data.boundaryNote === undefined ? null : String(data.boundaryNote),
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
    readinessScore: data.readinessScore ? normalizeReadinessScore(data.readinessScore) : undefined,
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

export async function getConsoleReadinessScore(): Promise<PlatformReadinessScore> {
  const { data } = await request.get('/v1/console/readiness/score')
  return normalizeReadinessScore(unwrapData<unknown>(data))
}

export async function getConsoleNavigationModules(): Promise<PlatformNavigationModel> {
  const { data } = await request.get('/v1/console/navigation/modules')
  const payload = asRecord(unwrapData<unknown>(data))
  return {
    navigationMode: String(payload.navigationMode ?? 'read-only-module-launch'),
    controlActionsEnabled: Boolean(payload.controlActionsEnabled),
    items: Array.isArray(payload.items) ? payload.items.map((item) => normalizeNavigationItem(item)) : [],
  }
}

export interface ModulePackageEntry {
  enabled: boolean
  visible: boolean
  route: string
  label: string
  entryMode: string
  lockedReason: string | null
}

export interface ModuleRoleVisibility {
  customer: boolean
  engineer: boolean
  admin: boolean
}

export interface ModulePackageRecord {
  packageId: string
  packageCode: string
  packageName: string
  moduleId: string
  moduleName: string
  moduleType: string
  packageCategory: string
  installed: boolean
  entitled: boolean
  enabled: boolean
  visible: boolean
  installedVersion: string
  availableVersion: string
  patchStatus: string
  patchMode: string
  upgradeRequired: boolean
  activationMode: string
  lockedReason: string | null
  customerEntry: ModulePackageEntry
  engineerEntry: ModulePackageEntry
  adminEntry: ModulePackageEntry
  roleVisibility: ModuleRoleVisibility
  entryStatus: string
  platform: string
  industryProjection: string
  description: string
  productionActivation: boolean
  runtimeActivation: boolean
  dbWrite: boolean
  approvalExecution: boolean
  deploymentExecution: boolean
  edgeLinkRuntimeCall: boolean
  customerIdentifierLeakage: boolean
  runtimeMode: string
  provider: string
  readOnly: boolean
  controlActionsEnabled: boolean
  patchActionsEnabled: boolean
  licenseServerIntegrated: boolean
  entitlementRuntimeIntegrated: boolean
  hotPlugArchitectureReady: boolean
  roleEntryModelReady: boolean
  certified: boolean
  iec62443Certified: boolean
  limitations: string[]
  nextActions: string[]
}

export interface PackageCenterHealth {
  status: string
  moduleId: string
  moduleName: string
  runtimeMode: string
  provider: string
  readOnly: boolean
  controlActionsEnabled: boolean
  patchActionsEnabled: boolean
  licenseServerIntegrated: boolean
  entitlementRuntimeIntegrated: boolean
  hotPlugArchitectureReady: boolean
  roleEntryModelReady: boolean
  certified: boolean
  iec62443Certified: boolean
}

export interface PackageSummary {
  totalPackages: number
  installedPackages: number
  entitledPackages: number
  enabledPackages: number
  visiblePackages: number
  lockedPackages: number
  customerEntryCount: number
  engineerEntryCount: number
  adminEntryCount: number
  patchReadyPackages: number
  upgradeRequiredPackages: number
  licenseServerIntegrated: boolean
  patchActionsEnabled: boolean
  controlActionsEnabled: boolean
  roleEntryModelReady: boolean
  hotPlugArchitectureReady: boolean
  limitations: string[]
  certified: boolean
  iec62443Certified: boolean
}

export interface PackageEntryCenter {
  customerApplications: Array<{
    packageId: string
    moduleId: string
    moduleName: string
    entry: ModulePackageEntry
    entitled: boolean
    enabled: boolean
    visible: boolean
    lockedReason: string | null
  }>
  engineerWorkspace: Array<{
    packageId: string
    moduleId: string
    moduleName: string
    entry: ModulePackageEntry
  }>
  adminPackageCenter: Array<{
    packageId: string
    moduleId: string
    moduleName: string
    entry: ModulePackageEntry
    entitled: boolean
    enabled: boolean
    visible: boolean
    patchStatus: string
    upgradeRequired: boolean
  }>
  lockedPackages: ModulePackageRecord[]
  entryMode: string
  roleAware: boolean
  runtimeLinked: boolean
  certified: boolean
  iec62443Certified: boolean
}

export interface PatchReadiness {
  patchMode: string
  patchActionsEnabled: boolean
  packages: Array<{
    packageId: string
    packageCode: string
    patchStatus: string
    upgradeRequired: boolean
    installedVersion: string
    availableVersion: string
  }>
  upgradeRequiredPackages: string[]
  patchReadyPackages: string[]
  licenseServerIntegrated: boolean
  limitations: string[]
  certified: boolean
  iec62443Certified: boolean
}

export interface PackageListResponse {
  items: ModulePackageRecord[]
  summary: PackageSummary
  filters: Record<string, unknown>
  runtimeMode: string
  provider: string
  readOnly: boolean
  controlActionsEnabled: boolean
  patchActionsEnabled: boolean
  certified: boolean
  iec62443Certified: boolean
}

export interface GetModulePackagesParams {
  moduleId?: string
  packageCategory?: string
  installed?: boolean
  entitled?: boolean
  enabled?: boolean
  visible?: boolean
  patchStatus?: string
  role?: string
}

function normalizePackageEntry(raw: unknown): ModulePackageEntry {
  const data = asRecord(raw)
  return {
    enabled: Boolean(data.enabled),
    visible: Boolean(data.visible),
    route: String(data.route ?? ''),
    label: String(data.label ?? ''),
    entryMode: String(data.entryMode ?? ''),
    lockedReason: data.lockedReason === null || data.lockedReason === undefined ? null : String(data.lockedReason),
  }
}

function normalizeRoleVisibility(raw: unknown): ModuleRoleVisibility {
  const data = asRecord(raw)
  return {
    customer: Boolean(data.customer),
    engineer: Boolean(data.engineer),
    admin: Boolean(data.admin),
  }
}

function normalizePackage(raw: unknown): ModulePackageRecord {
  const data = asRecord(raw)
  return {
    packageId: String(data.packageId ?? ''),
    packageCode: String(data.packageCode ?? ''),
    packageName: String(data.packageName ?? ''),
    moduleId: String(data.moduleId ?? ''),
    moduleName: String(data.moduleName ?? ''),
    moduleType: String(data.moduleType ?? ''),
    packageCategory: String(data.packageCategory ?? ''),
    installed: Boolean(data.installed),
    entitled: Boolean(data.entitled),
    enabled: Boolean(data.enabled),
    visible: Boolean(data.visible),
    installedVersion: String(data.installedVersion ?? ''),
    availableVersion: String(data.availableVersion ?? ''),
    patchStatus: String(data.patchStatus ?? ''),
    patchMode: String(data.patchMode ?? ''),
    upgradeRequired: Boolean(data.upgradeRequired),
    activationMode: String(data.activationMode ?? ''),
    lockedReason: data.lockedReason === null || data.lockedReason === undefined ? null : String(data.lockedReason),
    customerEntry: normalizePackageEntry(data.customerEntry),
    engineerEntry: normalizePackageEntry(data.engineerEntry),
    adminEntry: normalizePackageEntry(data.adminEntry),
    roleVisibility: normalizeRoleVisibility(data.roleVisibility),
    entryStatus: String(data.entryStatus ?? ''),
    platform: String(data.platform ?? 'VANTARIS ONE'),
    industryProjection: String(data.industryProjection ?? ''),
    description: String(data.description ?? ''),
    productionActivation: Boolean(data.productionActivation),
    runtimeActivation: Boolean(data.runtimeActivation),
    dbWrite: Boolean(data.dbWrite),
    approvalExecution: Boolean(data.approvalExecution),
    deploymentExecution: Boolean(data.deploymentExecution),
    edgeLinkRuntimeCall: Boolean(data.edgeLinkRuntimeCall),
    customerIdentifierLeakage: Boolean(data.customerIdentifierLeakage),
    runtimeMode: String(data.runtimeMode ?? 'local-skeleton'),
    provider: String(data.provider ?? 'local-package-registry'),
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    controlActionsEnabled: Boolean(data.controlActionsEnabled),
    patchActionsEnabled: Boolean(data.patchActionsEnabled),
    licenseServerIntegrated: Boolean(data.licenseServerIntegrated),
    entitlementRuntimeIntegrated: Boolean(data.entitlementRuntimeIntegrated),
    hotPlugArchitectureReady: Boolean(data.hotPlugArchitectureReady),
    roleEntryModelReady: Boolean(data.roleEntryModelReady),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
    limitations: asStringArray(data.limitations),
    nextActions: asStringArray(data.nextActions),
  }
}

function normalizePackageSummary(raw: unknown): PackageSummary {
  const data = asRecord(raw)
  return {
    totalPackages: Number(data.totalPackages ?? 0),
    installedPackages: Number(data.installedPackages ?? 0),
    entitledPackages: Number(data.entitledPackages ?? 0),
    enabledPackages: Number(data.enabledPackages ?? 0),
    visiblePackages: Number(data.visiblePackages ?? 0),
    lockedPackages: Number(data.lockedPackages ?? 0),
    customerEntryCount: Number(data.customerEntryCount ?? 0),
    engineerEntryCount: Number(data.engineerEntryCount ?? 0),
    adminEntryCount: Number(data.adminEntryCount ?? 0),
    patchReadyPackages: Number(data.patchReadyPackages ?? 0),
    upgradeRequiredPackages: Number(data.upgradeRequiredPackages ?? 0),
    licenseServerIntegrated: Boolean(data.licenseServerIntegrated),
    patchActionsEnabled: Boolean(data.patchActionsEnabled),
    controlActionsEnabled: Boolean(data.controlActionsEnabled),
    roleEntryModelReady: Boolean(data.roleEntryModelReady),
    hotPlugArchitectureReady: Boolean(data.hotPlugArchitectureReady),
    limitations: asStringArray(data.limitations),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizePackageHealth(raw: unknown): PackageCenterHealth {
  const data = asRecord(raw)
  return {
    status: String(data.status ?? 'unknown'),
    moduleId: String(data.moduleId ?? 'uconsole-package-center'),
    moduleName: String(data.moduleName ?? 'UConsole Module Package Center'),
    runtimeMode: String(data.runtimeMode ?? 'local-skeleton'),
    provider: String(data.provider ?? 'local-package-registry'),
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    controlActionsEnabled: Boolean(data.controlActionsEnabled),
    patchActionsEnabled: Boolean(data.patchActionsEnabled),
    licenseServerIntegrated: Boolean(data.licenseServerIntegrated),
    entitlementRuntimeIntegrated: Boolean(data.entitlementRuntimeIntegrated),
    hotPlugArchitectureReady: Boolean(data.hotPlugArchitectureReady),
    roleEntryModelReady: Boolean(data.roleEntryModelReady),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizePatchReadiness(raw: unknown): PatchReadiness {
  const data = asRecord(raw)
  return {
    patchMode: String(data.patchMode ?? 'local-skeleton-patch-readiness'),
    patchActionsEnabled: Boolean(data.patchActionsEnabled),
    packages: Array.isArray(data.packages)
      ? data.packages.map((item) => {
          const row = asRecord(item)
          return {
            packageId: String(row.packageId ?? ''),
            packageCode: String(row.packageCode ?? ''),
            patchStatus: String(row.patchStatus ?? ''),
            upgradeRequired: Boolean(row.upgradeRequired),
            installedVersion: String(row.installedVersion ?? ''),
            availableVersion: String(row.availableVersion ?? ''),
          }
        })
      : [],
    upgradeRequiredPackages: asStringArray(data.upgradeRequiredPackages),
    patchReadyPackages: asStringArray(data.patchReadyPackages),
    licenseServerIntegrated: Boolean(data.licenseServerIntegrated),
    limitations: asStringArray(data.limitations),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeEntryCenter(raw: unknown): PackageEntryCenter {
  const data = asRecord(raw)
  const normalizeGenericEntry = (item: unknown) => {
    const row = asRecord(item)
    return {
      packageId: String(row.packageId ?? ''),
      moduleId: String(row.moduleId ?? ''),
      moduleName: String(row.moduleName ?? ''),
      entry: normalizePackageEntry(row.entry),
    }
  }
  return {
    customerApplications: Array.isArray(data.customerApplications)
      ? data.customerApplications.map((item) => {
          const row = asRecord(item)
          const base = normalizeGenericEntry(row)
          return {
            ...base,
            entitled: Boolean(row.entitled),
            enabled: Boolean(row.enabled),
            visible: Boolean(row.visible),
            lockedReason: row.lockedReason === null || row.lockedReason === undefined ? null : String(row.lockedReason),
          }
        })
      : [],
    engineerWorkspace: Array.isArray(data.engineerWorkspace) ? data.engineerWorkspace.map((item) => normalizeGenericEntry(item)) : [],
    adminPackageCenter: Array.isArray(data.adminPackageCenter)
      ? data.adminPackageCenter.map((item) => {
          const row = asRecord(item)
          const base = normalizeGenericEntry(row)
          return {
            ...base,
            entitled: Boolean(row.entitled),
            enabled: Boolean(row.enabled),
            visible: Boolean(row.visible),
            patchStatus: String(row.patchStatus ?? ''),
            upgradeRequired: Boolean(row.upgradeRequired),
          }
        })
      : [],
    lockedPackages: Array.isArray(data.lockedPackages) ? data.lockedPackages.map((item) => normalizePackage(item)) : [],
    entryMode: String(data.entryMode ?? 'local-skeleton-entry-center'),
    roleAware: Boolean(data.roleAware),
    runtimeLinked: Boolean(data.runtimeLinked),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

export async function getPackageCenterHealth(): Promise<PackageCenterHealth> {
  const { data } = await request.get('/v1/console/packages/health')
  return normalizePackageHealth(unwrapData<unknown>(data))
}

export async function getModulePackages(params: GetModulePackagesParams = {}): Promise<PackageListResponse> {
  const { data } = await request.get('/v1/console/packages', { params })
  const body = asRecord(unwrapData<unknown>(data))
  return {
    items: Array.isArray(body.items) ? body.items.map((item) => normalizePackage(item)) : [],
    summary: normalizePackageSummary(body.summary),
    filters: asRecord(body.filters),
    runtimeMode: String(body.runtimeMode ?? 'local-skeleton'),
    provider: String(body.provider ?? 'local-package-registry'),
    readOnly: body.readOnly !== undefined ? Boolean(body.readOnly) : true,
    controlActionsEnabled: Boolean(body.controlActionsEnabled),
    patchActionsEnabled: Boolean(body.patchActionsEnabled),
    certified: Boolean(body.certified),
    iec62443Certified: Boolean(body.iec62443Certified),
  }
}

export async function getModulePackageDetail(packageIdOrModuleId: string): Promise<{ item: ModulePackageRecord | null; found: boolean }> {
  const { data } = await request.get(`/v1/console/packages/${encodeURIComponent(packageIdOrModuleId)}`)
  const body = asRecord(unwrapData<unknown>(data))
  const found = Boolean(body.found)
  const item = body.item ? normalizePackage(body.item) : null
  return { item, found }
}

export async function getPackageSummary(): Promise<PackageSummary> {
  const { data } = await request.get('/v1/console/packages/summary')
  return normalizePackageSummary(unwrapData<unknown>(data))
}

export async function getPackageEntries(): Promise<PackageEntryCenter> {
  const { data } = await request.get('/v1/console/packages/entries')
  return normalizeEntryCenter(unwrapData<unknown>(data))
}

export async function getLockedPackages(): Promise<ModulePackageRecord[]> {
  const { data } = await request.get('/v1/console/packages/locked')
  const body = asRecord(unwrapData<unknown>(data))
  return Array.isArray(body.items) ? body.items.map((item) => normalizePackage(item)) : []
}

export async function getPatchReadiness(): Promise<PatchReadiness> {
  const { data } = await request.get('/v1/console/packages/patch-readiness')
  return normalizePatchReadiness(unwrapData<unknown>(data))
}

export type ConsoleRole = 'customer' | 'engineer' | 'admin'

export interface RolePackageVisibility {
  role: ConsoleRole
  packageId: string
  packageCode: string
  packageName: string
  moduleId: string
  moduleName: string
  entryMode: string
  label: string
  route: string
  visible: boolean
  enabled: boolean
  entitled: boolean
  installed: boolean
  contextOnly: boolean
  lockedReason: string | null
  state: string
  readOnly: boolean
  controlActionsEnabled: boolean
  realRbacIntegrated: boolean
  authIntegrated: boolean
  routeGuardIntegrated: boolean
  certified: boolean
  iec62443Certified: boolean
}

export interface RoleVisibilityPolicy {
  role: ConsoleRole
  roleLabel: string
  visibilityMode: string
  realRbacIntegrated: boolean
  authIntegrated: boolean
  routeGuardIntegrated: boolean
  readOnly: boolean
  allowedEntryModes: string[]
  hiddenEntryModes: string[]
  visiblePackages: RolePackageVisibility[]
  lockedPackages: RolePackageVisibility[]
  hiddenPackages: RolePackageVisibility[]
  menuPreview: RolePackageVisibility[]
  hiddenOrLockedReasons: Array<{
    role: ConsoleRole
    packageCode: string
    moduleName: string
    entryMode: string
    reason: string
    state: string
    certified: boolean
    iec62443Certified: boolean
  }>
  limitations: string[]
  certified: boolean
  iec62443Certified: boolean
}

export interface RoleEntryView {
  role: ConsoleRole
  roleLabel: string
  entryMode: string
  visiblePackages: RolePackageVisibility[]
  lockedPackages: RolePackageVisibility[]
  hiddenPackages: RolePackageVisibility[]
  readOnly: boolean
  controlActionsEnabled: boolean
  realRbacIntegrated: boolean
  authIntegrated: boolean
  routeGuardIntegrated: boolean
  certified: boolean
  iec62443Certified: boolean
}

export interface RoleMenuPreview {
  role: ConsoleRole
  roleLabel: string
  menuPreviewMode: string
  items: RolePackageVisibility[]
  readOnly: boolean
  realRbacIntegrated: boolean
  authIntegrated: boolean
  routeGuardIntegrated: boolean
  certified: boolean
  iec62443Certified: boolean
}

export interface RoleVisibilitySummary {
  supportedRoles: ConsoleRole[]
  roleVisibilityMode: string
  realRbacIntegrated: boolean
  authIntegrated: boolean
  routeGuardIntegrated: boolean
  customerVisibleCount: number
  engineerVisibleCount: number
  adminVisibleCount: number
  lockedPackageCount: number
  hiddenPackageCount: number
  readOnly: boolean
  controlActionsEnabled: boolean
  certified: boolean
  iec62443Certified: boolean
}

function normalizeRole(value: unknown): ConsoleRole {
  const role = String(value ?? '').toLowerCase()
  if (role === 'customer' || role === 'engineer' || role === 'admin') {
    return role
  }
  return 'customer'
}

function normalizeRolePackageVisibility(raw: unknown): RolePackageVisibility {
  const data = asRecord(raw)
  return {
    role: normalizeRole(data.role),
    packageId: String(data.packageId ?? ''),
    packageCode: String(data.packageCode ?? ''),
    packageName: String(data.packageName ?? ''),
    moduleId: String(data.moduleId ?? ''),
    moduleName: String(data.moduleName ?? ''),
    entryMode: String(data.entryMode ?? ''),
    label: String(data.label ?? ''),
    route: String(data.route ?? ''),
    visible: Boolean(data.visible),
    enabled: Boolean(data.enabled),
    entitled: Boolean(data.entitled),
    installed: Boolean(data.installed),
    contextOnly: Boolean(data.contextOnly),
    lockedReason: data.lockedReason === null || data.lockedReason === undefined ? null : String(data.lockedReason),
    state: String(data.state ?? 'hidden'),
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    controlActionsEnabled: Boolean(data.controlActionsEnabled),
    realRbacIntegrated: Boolean(data.realRbacIntegrated),
    authIntegrated: Boolean(data.authIntegrated),
    routeGuardIntegrated: Boolean(data.routeGuardIntegrated),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeRoleEntryView(raw: unknown): RoleEntryView {
  const data = asRecord(raw)
  return {
    role: normalizeRole(data.role),
    roleLabel: String(data.roleLabel ?? ''),
    entryMode: String(data.entryMode ?? 'local-skeleton-role-entry-view'),
    visiblePackages: Array.isArray(data.visiblePackages) ? data.visiblePackages.map((item) => normalizeRolePackageVisibility(item)) : [],
    lockedPackages: Array.isArray(data.lockedPackages) ? data.lockedPackages.map((item) => normalizeRolePackageVisibility(item)) : [],
    hiddenPackages: Array.isArray(data.hiddenPackages) ? data.hiddenPackages.map((item) => normalizeRolePackageVisibility(item)) : [],
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    controlActionsEnabled: Boolean(data.controlActionsEnabled),
    realRbacIntegrated: Boolean(data.realRbacIntegrated),
    authIntegrated: Boolean(data.authIntegrated),
    routeGuardIntegrated: Boolean(data.routeGuardIntegrated),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeRoleMenuPreview(raw: unknown): RoleMenuPreview {
  const data = asRecord(raw)
  return {
    role: normalizeRole(data.role),
    roleLabel: String(data.roleLabel ?? ''),
    menuPreviewMode: String(data.menuPreviewMode ?? 'local-skeleton-role-menu-preview'),
    items: Array.isArray(data.items) ? data.items.map((item) => normalizeRolePackageVisibility(item)) : [],
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    realRbacIntegrated: Boolean(data.realRbacIntegrated),
    authIntegrated: Boolean(data.authIntegrated),
    routeGuardIntegrated: Boolean(data.routeGuardIntegrated),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeRoleVisibilityPolicy(raw: unknown): RoleVisibilityPolicy {
  const data = asRecord(raw)
  const reasonsRaw = Array.isArray(data.hiddenOrLockedReasons) ? data.hiddenOrLockedReasons : []
  return {
    role: normalizeRole(data.role),
    roleLabel: String(data.roleLabel ?? ''),
    visibilityMode: String(data.visibilityMode ?? 'local-skeleton-role-visibility'),
    realRbacIntegrated: Boolean(data.realRbacIntegrated),
    authIntegrated: Boolean(data.authIntegrated),
    routeGuardIntegrated: Boolean(data.routeGuardIntegrated),
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    allowedEntryModes: asStringArray(data.allowedEntryModes),
    hiddenEntryModes: asStringArray(data.hiddenEntryModes),
    visiblePackages: Array.isArray(data.visiblePackages) ? data.visiblePackages.map((item) => normalizeRolePackageVisibility(item)) : [],
    lockedPackages: Array.isArray(data.lockedPackages) ? data.lockedPackages.map((item) => normalizeRolePackageVisibility(item)) : [],
    hiddenPackages: Array.isArray(data.hiddenPackages) ? data.hiddenPackages.map((item) => normalizeRolePackageVisibility(item)) : [],
    menuPreview: Array.isArray(data.menuPreview) ? data.menuPreview.map((item) => normalizeRolePackageVisibility(item)) : [],
    hiddenOrLockedReasons: reasonsRaw.map((item) => {
      const row = asRecord(item)
      return {
        role: normalizeRole(row.role),
        packageCode: String(row.packageCode ?? ''),
        moduleName: String(row.moduleName ?? ''),
        entryMode: String(row.entryMode ?? ''),
        reason: String(row.reason ?? ''),
        state: String(row.state ?? ''),
        certified: Boolean(row.certified),
        iec62443Certified: Boolean(row.iec62443Certified),
      }
    }),
    limitations: asStringArray(data.limitations),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeRoleVisibilitySummary(raw: unknown): RoleVisibilitySummary {
  const data = asRecord(raw)
  return {
    supportedRoles: Array.isArray(data.supportedRoles) ? data.supportedRoles.map((item) => normalizeRole(item)) : ['customer', 'engineer', 'admin'],
    roleVisibilityMode: String(data.roleVisibilityMode ?? 'local-skeleton-role-visibility'),
    realRbacIntegrated: Boolean(data.realRbacIntegrated),
    authIntegrated: Boolean(data.authIntegrated),
    routeGuardIntegrated: Boolean(data.routeGuardIntegrated),
    customerVisibleCount: Number(data.customerVisibleCount ?? 0),
    engineerVisibleCount: Number(data.engineerVisibleCount ?? 0),
    adminVisibleCount: Number(data.adminVisibleCount ?? 0),
    lockedPackageCount: Number(data.lockedPackageCount ?? 0),
    hiddenPackageCount: Number(data.hiddenPackageCount ?? 0),
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    controlActionsEnabled: Boolean(data.controlActionsEnabled),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

export async function getSupportedPackageRoles(): Promise<ConsoleRole[]> {
  const { data } = await request.get('/v1/console/packages/roles')
  const payload = asRecord(unwrapData<unknown>(data))
  return Array.isArray(payload.items) ? payload.items.map((item) => normalizeRole(item)) : []
}

export async function getRoleVisibilitySummary(): Promise<RoleVisibilitySummary> {
  const { data } = await request.get('/v1/console/packages/roles/summary')
  return normalizeRoleVisibilitySummary(unwrapData<unknown>(data))
}

export async function getRoleVisibility(role: ConsoleRole): Promise<RoleVisibilityPolicy> {
  const { data } = await request.get(`/v1/console/packages/roles/${encodeURIComponent(role)}`)
  return normalizeRoleVisibilityPolicy(unwrapData<unknown>(data))
}

export async function getRoleEntries(role: ConsoleRole): Promise<RoleEntryView> {
  const { data } = await request.get(`/v1/console/packages/roles/${encodeURIComponent(role)}/entries`)
  return normalizeRoleEntryView(unwrapData<unknown>(data))
}

export async function getRoleMenuPreview(role: ConsoleRole): Promise<RoleMenuPreview> {
  const { data } = await request.get(`/v1/console/packages/roles/${encodeURIComponent(role)}/menu-preview`)
  return normalizeRoleMenuPreview(unwrapData<unknown>(data))
}

export interface ModuleContentCard {
  moduleId: string
  moduleName: string
  packageCode: string
  contentMode: string
  runtimeLinked: boolean
  visible: boolean
  enabled: boolean
  entitled: boolean
  route: string
  status: string
  summary: Record<string, unknown>
  highlights: string[]
  risks: string[]
  limitations: string[]
  lastUpdated: string
  fallbackUsed: boolean
  lockedReason: string | null
  entryMode: string
  roleVisibility: ModuleRoleVisibility
  packageState: {
    installed: boolean
    entitled: boolean
    enabled: boolean
    visible: boolean
    patchStatus: string
    upgradeRequired: boolean
    lockedReason: string | null
  }
  readOnly: boolean
  controlActionsEnabled: boolean
  realRbacIntegrated: boolean
  routeGuardIntegrated: boolean
  certified: boolean
  iec62443Certified: boolean
}

export interface ModuleContentSummary {
  role: ConsoleRole
  totalContentCards: number
  visibleContentCards: number
  fallbackCards: number
  lockedPreviewCards: number
  readOnly: boolean
  runtimeLinked: boolean
  realRbacIntegrated: boolean
  routeGuardIntegrated: boolean
  certified: boolean
  iec62443Certified: boolean
}

export interface ModuleContentDashboard {
  role: ConsoleRole
  summary: ModuleContentSummary
  cards: ModuleContentCard[]
  contentMode: string
  runtimeLinked: boolean
  readOnly: boolean
  controlActionsEnabled: boolean
  realRbacIntegrated: boolean
  routeGuardIntegrated: boolean
  limitations: string[]
  certified: boolean
  iec62443Certified: boolean
}

export interface ModuleContentDetail {
  role: ConsoleRole
  item: ModuleContentCard
  readOnly: boolean
  runtimeLinked: boolean
  realRbacIntegrated: boolean
  routeGuardIntegrated: boolean
  certified: boolean
  iec62443Certified: boolean
}

function normalizeModuleContentCard(raw: unknown): ModuleContentCard {
  const data = asRecord(raw)
  const packageState = asRecord(data.packageState)
  return {
    moduleId: String(data.moduleId ?? ''),
    moduleName: String(data.moduleName ?? ''),
    packageCode: String(data.packageCode ?? ''),
    contentMode: String(data.contentMode ?? 'local-skeleton-summary'),
    runtimeLinked: Boolean(data.runtimeLinked),
    visible: Boolean(data.visible),
    enabled: Boolean(data.enabled),
    entitled: Boolean(data.entitled),
    route: String(data.route ?? ''),
    status: String(data.status ?? ''),
    summary: asRecord(data.summary),
    highlights: asStringArray(data.highlights),
    risks: asStringArray(data.risks),
    limitations: asStringArray(data.limitations),
    lastUpdated: String(data.lastUpdated ?? ''),
    fallbackUsed: Boolean(data.fallbackUsed),
    lockedReason: data.lockedReason === null || data.lockedReason === undefined ? null : String(data.lockedReason),
    entryMode: String(data.entryMode ?? ''),
    roleVisibility: normalizeRoleVisibility(data.roleVisibility),
    packageState: {
      installed: Boolean(packageState.installed),
      entitled: Boolean(packageState.entitled),
      enabled: Boolean(packageState.enabled),
      visible: Boolean(packageState.visible),
      patchStatus: String(packageState.patchStatus ?? ''),
      upgradeRequired: Boolean(packageState.upgradeRequired),
      lockedReason:
        packageState.lockedReason === null || packageState.lockedReason === undefined ? null : String(packageState.lockedReason),
    },
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    controlActionsEnabled: Boolean(data.controlActionsEnabled),
    realRbacIntegrated: Boolean(data.realRbacIntegrated),
    routeGuardIntegrated: Boolean(data.routeGuardIntegrated),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeModuleContentSummary(raw: unknown): ModuleContentSummary {
  const data = asRecord(raw)
  return {
    role: normalizeRole(data.role),
    totalContentCards: Number(data.totalContentCards ?? 0),
    visibleContentCards: Number(data.visibleContentCards ?? 0),
    fallbackCards: Number(data.fallbackCards ?? 0),
    lockedPreviewCards: Number(data.lockedPreviewCards ?? 0),
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    runtimeLinked: Boolean(data.runtimeLinked),
    realRbacIntegrated: Boolean(data.realRbacIntegrated),
    routeGuardIntegrated: Boolean(data.routeGuardIntegrated),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeModuleContentDashboard(raw: unknown): ModuleContentDashboard {
  const data = asRecord(raw)
  return {
    role: normalizeRole(data.role),
    summary: normalizeModuleContentSummary(data.summary),
    cards: Array.isArray(data.cards) ? data.cards.map((item) => normalizeModuleContentCard(item)) : [],
    contentMode: String(data.contentMode ?? 'local-skeleton-content-dashboard'),
    runtimeLinked: Boolean(data.runtimeLinked),
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    controlActionsEnabled: Boolean(data.controlActionsEnabled),
    realRbacIntegrated: Boolean(data.realRbacIntegrated),
    routeGuardIntegrated: Boolean(data.routeGuardIntegrated),
    limitations: asStringArray(data.limitations),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeModuleContentDetail(raw: unknown): ModuleContentDetail {
  const data = asRecord(raw)
  return {
    role: normalizeRole(data.role),
    item: normalizeModuleContentCard(data.item),
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    runtimeLinked: Boolean(data.runtimeLinked),
    realRbacIntegrated: Boolean(data.realRbacIntegrated),
    routeGuardIntegrated: Boolean(data.routeGuardIntegrated),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

export async function getModuleContentDashboard(role?: ConsoleRole): Promise<ModuleContentDashboard> {
  const { data } = await request.get('/v1/console/content/dashboard', { params: role ? { role } : undefined })
  return normalizeModuleContentDashboard(unwrapData<unknown>(data))
}

export async function getModuleContentCards(role?: ConsoleRole): Promise<ModuleContentCard[]> {
  const { data } = await request.get('/v1/console/content/cards', { params: role ? { role } : undefined })
  const payload = asRecord(unwrapData<unknown>(data))
  return Array.isArray(payload.items) ? payload.items.map((item) => normalizeModuleContentCard(item)) : []
}

export async function getModuleContentSummary(role?: ConsoleRole): Promise<ModuleContentSummary> {
  const { data } = await request.get('/v1/console/content/summary', { params: role ? { role } : undefined })
  return normalizeModuleContentSummary(unwrapData<unknown>(data))
}

export async function getModuleContentDetail(moduleId: string, role?: ConsoleRole): Promise<ModuleContentDetail> {
  const { data } = await request.get(`/v1/console/content/modules/${encodeURIComponent(moduleId)}`, {
    params: role ? { role } : undefined,
  })
  return normalizeModuleContentDetail(unwrapData<unknown>(data))
}
