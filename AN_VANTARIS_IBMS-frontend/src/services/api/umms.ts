import request from './request'

export interface UmmsHealth {
  status: string
  moduleId: string
  moduleName: string
  runtimeMode: string
  provider: string
  sourceSemantics: string
  readOnly: boolean
  controlActionsEnabled: boolean
  dispatchEnabled: boolean
  mobileIntegrated: boolean
  notificationIntegrated: boolean
  assetRuntimeIntegrated: boolean
  edgeRuntimeIntegrated: boolean
  linkRuntimeIntegrated: boolean
  dbPersistenceIntegrated: boolean
  certified: boolean
  iec62443Certified: boolean
}

export interface WorkOrderRecord {
  workOrderId: string
  workOrderCode: string
  title: string
  description: string
  workOrderType: string
  workOrderCategory: string
  workOrderStatus: string
  priority: string
  lifecycleStage: string
  siteId: string
  siteName: string
  systemId: string
  systemName: string
  assetId: string
  assetName: string
  requestedBy: string
  assignedTeam: string
  assignedTechnician: string
  plannedStart: string
  plannedEnd: string
  createdAt: string
  updatedAt: string
  sourceSystem: string
  sourceRecordId: string
  provider: string
  runtimeMode: string
  sourceSemantics: string
  mockData: boolean
  readOnly: boolean
  dispatchEnabled: boolean
  mobileIntegrated: boolean
  notificationIntegrated: boolean
  assetRuntimeIntegrated: boolean
  edgeRuntimeIntegrated: boolean
  linkRuntimeIntegrated: boolean
  tags: string[]
  metadata: Record<string, unknown>
  limitations: string[]
  certified: boolean
  iec62443Certified: boolean
}

export interface MaintenanceSummary {
  totalWorkOrders: number
  preventiveCount: number
  correctiveCount: number
  inspectionCount: number
  safetyCount: number
  routineCount: number
  draftCount: number
  openCount: number
  plannedCount: number
  scheduledCount: number
  inReviewCount: number
  highPriorityCount: number
  mockWorkOrders: number
  runtimeLinkedWorkOrders: number
  dispatchedWorkOrders: number
  mobileLinkedWorkOrders: number
  notificationLinkedWorkOrders: number
  certifiedWorkOrders: number
  workOrderTypes: string[]
  workOrderCategories: string[]
  limitations: string[]
  certified: boolean
  iec62443Certified: boolean
}

export interface WorkOrderBreakdown {
  breakdownMode: string
  byType: Array<{ key: string; count: number }>
  byStatus: Array<{ key: string; count: number }>
  byPriority: Array<{ key: string; count: number }>
  byCategory: Array<{ key: string; count: number }>
  runtimeLinked: boolean
  certified: boolean
  iec62443Certified: boolean
}

export interface MaintenanceAssociationModel {
  associationMode: string
  siteAssociations: Array<{ siteId: string; siteName: string; workOrderIds: string[]; runtimeLinked: boolean }>
  systemAssociations: Array<{ systemId: string; systemName: string; workOrderIds: string[]; runtimeLinked: boolean }>
  assetAssociations: Array<{ assetId: string; assetName: string; workOrderIds: string[]; runtimeLinked: boolean }>
  runtimeLinked: boolean
  assetRuntimeIntegrated: boolean
  notes: string
  certified: boolean
  iec62443Certified: boolean
}

export interface WorkOrderListResponse {
  workOrders: WorkOrderRecord[]
  total: number
  filters: {
    workOrderType: string
    workOrderCategory: string
    workOrderStatus: string
    priority: string
    siteId: string
    systemId: string
    assetId: string
  }
  summary: MaintenanceSummary
  provider: string
  runtimeMode: string
  sourceSemantics: string
  mockData: boolean
  readOnly: boolean
  certified: boolean
  iec62443Certified: boolean
}

export interface GetWorkOrdersParams {
  workOrderType?: string
  workOrderCategory?: string
  workOrderStatus?: string
  priority?: string
  siteId?: string
  systemId?: string
  assetId?: string
}

export interface UmmsReadonlyGuard {
  readOnly: boolean
  runtimeEnabled: boolean
  productionEnabled: boolean
  dbWriteEnabled: boolean
  workflowEnabled: boolean
  approvalEnabled: boolean
  writeActionsEnabled: boolean
  edgeRuntimeCall: boolean
  linkRuntimeCall: boolean
  oneAdapterIntroduced: boolean
}

export interface UmmsPackageEntry extends UmmsReadonlyGuard {
  platform: string
  module: string
  projection: string
  packageId: string
  packageName: string
  packageDisplayName: string
  packageStatus: string
  entryMode: string
  latestTag: string
  stakeholderReviewPackage: string
}

export interface UmmsReadinessStage {
  stage: string
  title: string
  status: string
  passMarker: string
  tagReference?: string
}

export interface UmmsStakeholderReview extends UmmsReadonlyGuard {
  reviewPackageId: string
  baselineHead: string
  publishedTags: string[]
  readinessChain: UmmsReadinessStage[]
  knownLimitations: string[]
  recommendedNextSteps: string[]
}

export interface UmmsCustomerCoreFunction {
  function: string
  coverageStatus: string
  readinessStage: string
  runtimeEnabled: boolean
  futureOwner: string
  remainingGap: string
}

export interface UmmsCustomerCoreFunctions extends UmmsReadonlyGuard {
  customerCoreFunctions: UmmsCustomerCoreFunction[]
  totalFunctions: number
}

export interface UmmsSafetyPosture extends UmmsReadonlyGuard {
  safetyPosture: Record<string, boolean>
}

export interface UmmsReadinessSummary extends UmmsReadonlyGuard {
  readinessStages: UmmsReadinessStage[]
}

export interface UmmsReadonlyOverview {
  packageEntry: UmmsPackageEntry
  stakeholderReview: UmmsStakeholderReview
  readinessSummary: UmmsReadinessSummary
  customerCoreFunctions: UmmsCustomerCoreFunctions
  safetyPosture: UmmsSafetyPosture
  fallbackActive: boolean
  fallbackMessage: string
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

function unwrapData<T>(body: unknown): T {
  if (typeof body === 'object' && body !== null && 'data' in body) {
    return (body as { data: T }).data
  }
  return body as T
}

function normalizeHealth(raw: unknown): UmmsHealth {
  const data = asRecord(raw)
  return {
    status: String(data.status ?? 'unknown'),
    moduleId: String(data.moduleId ?? 'umms'),
    moduleName: String(data.moduleName ?? 'UMMS Maintenance'),
    runtimeMode: String(data.runtimeMode ?? 'skeleton'),
    provider: String(data.provider ?? 'local-umms-provider'),
    sourceSemantics: String(data.sourceSemantics ?? 'ibms-neutral'),
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    controlActionsEnabled: Boolean(data.controlActionsEnabled),
    dispatchEnabled: Boolean(data.dispatchEnabled),
    mobileIntegrated: Boolean(data.mobileIntegrated),
    notificationIntegrated: Boolean(data.notificationIntegrated),
    assetRuntimeIntegrated: Boolean(data.assetRuntimeIntegrated),
    edgeRuntimeIntegrated: Boolean(data.edgeRuntimeIntegrated),
    linkRuntimeIntegrated: Boolean(data.linkRuntimeIntegrated),
    dbPersistenceIntegrated: Boolean(data.dbPersistenceIntegrated),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeWorkOrder(raw: unknown): WorkOrderRecord {
  const data = asRecord(raw)
  return {
    workOrderId: String(data.workOrderId ?? ''),
    workOrderCode: String(data.workOrderCode ?? ''),
    title: String(data.title ?? ''),
    description: String(data.description ?? ''),
    workOrderType: String(data.workOrderType ?? ''),
    workOrderCategory: String(data.workOrderCategory ?? ''),
    workOrderStatus: String(data.workOrderStatus ?? ''),
    priority: String(data.priority ?? ''),
    lifecycleStage: String(data.lifecycleStage ?? ''),
    siteId: String(data.siteId ?? ''),
    siteName: String(data.siteName ?? ''),
    systemId: String(data.systemId ?? ''),
    systemName: String(data.systemName ?? ''),
    assetId: String(data.assetId ?? ''),
    assetName: String(data.assetName ?? ''),
    requestedBy: String(data.requestedBy ?? ''),
    assignedTeam: String(data.assignedTeam ?? ''),
    assignedTechnician: String(data.assignedTechnician ?? ''),
    plannedStart: String(data.plannedStart ?? ''),
    plannedEnd: String(data.plannedEnd ?? ''),
    createdAt: String(data.createdAt ?? ''),
    updatedAt: String(data.updatedAt ?? ''),
    sourceSystem: String(data.sourceSystem ?? ''),
    sourceRecordId: String(data.sourceRecordId ?? ''),
    provider: String(data.provider ?? 'local-umms-provider'),
    runtimeMode: String(data.runtimeMode ?? 'skeleton'),
    sourceSemantics: String(data.sourceSemantics ?? 'ibms-neutral'),
    mockData: data.mockData !== undefined ? Boolean(data.mockData) : true,
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    dispatchEnabled: Boolean(data.dispatchEnabled),
    mobileIntegrated: Boolean(data.mobileIntegrated),
    notificationIntegrated: Boolean(data.notificationIntegrated),
    assetRuntimeIntegrated: Boolean(data.assetRuntimeIntegrated),
    edgeRuntimeIntegrated: Boolean(data.edgeRuntimeIntegrated),
    linkRuntimeIntegrated: Boolean(data.linkRuntimeIntegrated),
    tags: asStringArray(data.tags),
    metadata: asRecord(data.metadata),
    limitations: asStringArray(data.limitations),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeSummary(raw: unknown): MaintenanceSummary {
  const data = asRecord(raw)
  return {
    totalWorkOrders: Number(data.totalWorkOrders ?? 0),
    preventiveCount: Number(data.preventiveCount ?? 0),
    correctiveCount: Number(data.correctiveCount ?? 0),
    inspectionCount: Number(data.inspectionCount ?? 0),
    safetyCount: Number(data.safetyCount ?? 0),
    routineCount: Number(data.routineCount ?? 0),
    draftCount: Number(data.draftCount ?? 0),
    openCount: Number(data.openCount ?? 0),
    plannedCount: Number(data.plannedCount ?? 0),
    scheduledCount: Number(data.scheduledCount ?? 0),
    inReviewCount: Number(data.inReviewCount ?? 0),
    highPriorityCount: Number(data.highPriorityCount ?? 0),
    mockWorkOrders: Number(data.mockWorkOrders ?? 0),
    runtimeLinkedWorkOrders: Number(data.runtimeLinkedWorkOrders ?? 0),
    dispatchedWorkOrders: Number(data.dispatchedWorkOrders ?? 0),
    mobileLinkedWorkOrders: Number(data.mobileLinkedWorkOrders ?? 0),
    notificationLinkedWorkOrders: Number(data.notificationLinkedWorkOrders ?? 0),
    certifiedWorkOrders: Number(data.certifiedWorkOrders ?? 0),
    workOrderTypes: asStringArray(data.workOrderTypes),
    workOrderCategories: asStringArray(data.workOrderCategories),
    limitations: asStringArray(data.limitations),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeBreakdown(raw: unknown): WorkOrderBreakdown {
  const data = asRecord(raw)
  const group = (value: unknown) =>
    asRecordArray(value).map((item) => ({
      key: String(item.key ?? ''),
      count: Number(item.count ?? 0),
    }))
  return {
    breakdownMode: String(data.breakdownMode ?? 'local-skeleton-breakdown'),
    byType: group(data.byType),
    byStatus: group(data.byStatus),
    byPriority: group(data.byPriority),
    byCategory: group(data.byCategory),
    runtimeLinked: Boolean(data.runtimeLinked),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeAssociations(raw: unknown): MaintenanceAssociationModel {
  const data = asRecord(raw)
  return {
    associationMode: String(data.associationMode ?? 'local-skeleton-association'),
    siteAssociations: asRecordArray(data.siteAssociations).map((item) => ({
      siteId: String(item.siteId ?? ''),
      siteName: String(item.siteName ?? ''),
      workOrderIds: asStringArray(item.workOrderIds),
      runtimeLinked: Boolean(item.runtimeLinked),
    })),
    systemAssociations: asRecordArray(data.systemAssociations).map((item) => ({
      systemId: String(item.systemId ?? ''),
      systemName: String(item.systemName ?? ''),
      workOrderIds: asStringArray(item.workOrderIds),
      runtimeLinked: Boolean(item.runtimeLinked),
    })),
    assetAssociations: asRecordArray(data.assetAssociations).map((item) => ({
      assetId: String(item.assetId ?? ''),
      assetName: String(item.assetName ?? ''),
      workOrderIds: asStringArray(item.workOrderIds),
      runtimeLinked: Boolean(item.runtimeLinked),
    })),
    runtimeLinked: Boolean(data.runtimeLinked),
    assetRuntimeIntegrated: Boolean(data.assetRuntimeIntegrated),
    notes: String(data.notes ?? ''),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeList(raw: unknown): WorkOrderListResponse {
  const data = asRecord(raw)
  const filters = asRecord(data.filters)
  return {
    workOrders: asRecordArray(data.workOrders).map((item) => normalizeWorkOrder(item)),
    total: Number(data.total ?? 0),
    filters: {
      workOrderType: String(filters.workOrderType ?? ''),
      workOrderCategory: String(filters.workOrderCategory ?? ''),
      workOrderStatus: String(filters.workOrderStatus ?? ''),
      priority: String(filters.priority ?? ''),
      siteId: String(filters.siteId ?? ''),
      systemId: String(filters.systemId ?? ''),
      assetId: String(filters.assetId ?? ''),
    },
    summary: normalizeSummary(data.summary),
    provider: String(data.provider ?? 'local-umms-provider'),
    runtimeMode: String(data.runtimeMode ?? 'skeleton'),
    sourceSemantics: String(data.sourceSemantics ?? 'ibms-neutral'),
    mockData: data.mockData !== undefined ? Boolean(data.mockData) : true,
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeGuard(data: Record<string, unknown>): UmmsReadonlyGuard {
  return {
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    runtimeEnabled: Boolean(data.runtimeEnabled),
    productionEnabled: Boolean(data.productionEnabled),
    dbWriteEnabled: Boolean(data.dbWriteEnabled),
    workflowEnabled: Boolean(data.workflowEnabled),
    approvalEnabled: Boolean(data.approvalEnabled),
    writeActionsEnabled: Boolean(data.writeActionsEnabled),
    edgeRuntimeCall: Boolean(data.edgeRuntimeCall),
    linkRuntimeCall: Boolean(data.linkRuntimeCall),
    oneAdapterIntroduced: Boolean(data.oneAdapterIntroduced),
  }
}

function normalizeReadinessStage(raw: unknown): UmmsReadinessStage {
  const data = asRecord(raw)
  return {
    stage: String(data.stage ?? ''),
    title: String(data.title ?? ''),
    status: String(data.status ?? ''),
    passMarker: String(data.passMarker ?? ''),
    tagReference: data.tagReference === undefined ? undefined : String(data.tagReference),
  }
}

function normalizePackageEntry(raw: unknown): UmmsPackageEntry {
  const data = asRecord(raw)
  return {
    ...normalizeGuard(data),
    platform: String(data.platform ?? 'VANTARIS ONE'),
    module: String(data.module ?? 'UMMS'),
    projection: String(data.projection ?? 'umms_package_entry'),
    packageId: String(data.packageId ?? 'umms'),
    packageName: String(data.packageName ?? 'Unified Maintenance Management System'),
    packageDisplayName: String(data.packageDisplayName ?? 'UMMS'),
    packageStatus: String(data.packageStatus ?? 'stakeholder_review_ready'),
    entryMode: String(data.entryMode ?? 'read_only_stakeholder_review'),
    latestTag: String(data.latestTag ?? 'umms-r11-readonly-api-entry-skeleton-local-freeze-20260621'),
    stakeholderReviewPackage: String(data.stakeholderReviewPackage ?? 'ONE_UMMS_R10_STAKEHOLDER_REVIEW_PACKAGE.md'),
  }
}

function normalizeStakeholderReview(raw: unknown): UmmsStakeholderReview {
  const data = asRecord(raw)
  return {
    ...normalizeGuard(data),
    reviewPackageId: String(data.reviewPackageId ?? 'umms-stakeholder-review-package.v1'),
    baselineHead: String(data.baselineHead ?? ''),
    publishedTags: asStringArray(data.publishedTags),
    readinessChain: asRecordArray(data.readinessChain).map((item) => normalizeReadinessStage(item)),
    knownLimitations: asStringArray(data.knownLimitations),
    recommendedNextSteps: asStringArray(data.recommendedNextSteps),
  }
}

function normalizeReadinessSummary(raw: unknown): UmmsReadinessSummary {
  const data = asRecord(raw)
  return {
    ...normalizeGuard(data),
    readinessStages: asRecordArray(data.readinessStages).map((item) => normalizeReadinessStage(item)),
  }
}

function normalizeCustomerCoreFunction(raw: unknown): UmmsCustomerCoreFunction {
  const data = asRecord(raw)
  return {
    function: String(data.function ?? ''),
    coverageStatus: String(data.coverageStatus ?? ''),
    readinessStage: String(data.readinessStage ?? ''),
    runtimeEnabled: Boolean(data.runtimeEnabled),
    futureOwner: String(data.futureOwner ?? ''),
    remainingGap: String(data.remainingGap ?? ''),
  }
}

function normalizeCustomerCoreFunctions(raw: unknown): UmmsCustomerCoreFunctions {
  const data = asRecord(raw)
  return {
    ...normalizeGuard(data),
    customerCoreFunctions: asRecordArray(data.customerCoreFunctions).map((item) => normalizeCustomerCoreFunction(item)),
    totalFunctions: Number(data.totalFunctions ?? 0),
  }
}

function normalizeSafetyPosture(raw: unknown): UmmsSafetyPosture {
  const data = asRecord(raw)
  const posture = asRecord(data.safetyPosture)
  return {
    ...normalizeGuard(data),
    safetyPosture: Object.fromEntries(Object.entries(posture).map(([key, value]) => [key, Boolean(value)])),
  }
}

function fallbackPackageEntry(): UmmsPackageEntry {
  return normalizePackageEntry({})
}

function fallbackStakeholderReview(): UmmsStakeholderReview {
  return normalizeStakeholderReview({
    knownLimitations: ['UMMS readiness data unavailable, read-only fallback active.'],
    recommendedNextSteps: ['UMMS read-only frontend freeze / archive'],
  })
}

function fallbackReadinessSummary(): UmmsReadinessSummary {
  return normalizeReadinessSummary({ readinessStages: [] })
}

function fallbackCustomerCoreFunctions(): UmmsCustomerCoreFunctions {
  return normalizeCustomerCoreFunctions({
    customerCoreFunctions: [
      'Work Order Management',
      'Asset Registry',
      'Preventive Maintenance',
      'Spare Parts / Inventory',
      'Vendor / Contract / SLA',
      'UCDE Evidence Closure Alignment',
      'HMI Locator Binding',
      'Existing System Onboarding',
      'Engineer Commissioning Diagnostics',
      'Remote / Distributed Deployment Readiness',
    ].map((name) => ({
      function: name,
      coverageStatus: 'read_only_fallback',
      readinessStage: 'UMMS-R12 fallback',
      runtimeEnabled: false,
      futureOwner: 'UMMS future implementation phase',
      remainingGap: 'API data unavailable; fallback remains read-only.',
    })),
    totalFunctions: 10,
  })
}

function fallbackSafetyPosture(): UmmsSafetyPosture {
  return normalizeSafetyPosture({
    safetyPosture: {
      readOnly: true,
      productionActivation: false,
      runtimeActivation: false,
      dbWrite: false,
      approvalExecution: false,
      workflowExecution: false,
      workOrderRuntimeExecution: false,
      pmExecution: false,
      inventoryTransaction: false,
      vendorContractSlaRuntime: false,
      evidenceClosureExecution: false,
      hmiRuntimeExecution: false,
      deviceConnection: false,
      connectorExecution: false,
      edgeRuntimeCall: false,
      linkRuntimeCall: false,
      oneAdapterIntroduced: false,
    },
  })
}

export async function getUmmsHealth(): Promise<UmmsHealth> {
  const { data } = await request.get('/v1/umms/health')
  return normalizeHealth(unwrapData<unknown>(data))
}

export async function getWorkOrders(params: GetWorkOrdersParams = {}): Promise<WorkOrderListResponse> {
  const { data } = await request.get('/v1/umms/work-orders', { params })
  return normalizeList(unwrapData<unknown>(data))
}

export async function getWorkOrderDetail(workOrderId: string): Promise<WorkOrderRecord> {
  const { data } = await request.get(`/v1/umms/work-orders/${encodeURIComponent(workOrderId)}`)
  return normalizeWorkOrder(unwrapData<unknown>(data))
}

export async function getMaintenanceSummary(): Promise<MaintenanceSummary> {
  const { data } = await request.get('/v1/umms/work-orders/summary')
  return normalizeSummary(unwrapData<unknown>(data))
}

export async function getWorkOrderBreakdown(): Promise<WorkOrderBreakdown> {
  const { data } = await request.get('/v1/umms/work-orders/breakdown')
  return normalizeBreakdown(unwrapData<unknown>(data))
}

export async function getMaintenanceAssociations(): Promise<MaintenanceAssociationModel> {
  const { data } = await request.get('/v1/umms/associations')
  return normalizeAssociations(unwrapData<unknown>(data))
}

export async function getUmmsReadonlyPackageEntry(): Promise<UmmsPackageEntry> {
  const { data } = await request.get('/v1/one/umms/package-entry')
  return normalizePackageEntry(unwrapData<unknown>(data))
}

export async function getUmmsReadonlyStakeholderReview(): Promise<UmmsStakeholderReview> {
  const { data } = await request.get('/v1/one/umms/stakeholder-review')
  return normalizeStakeholderReview(unwrapData<unknown>(data))
}

export async function getUmmsReadonlyReadinessSummary(): Promise<UmmsReadinessSummary> {
  const { data } = await request.get('/v1/one/umms/readiness-summary')
  return normalizeReadinessSummary(unwrapData<unknown>(data))
}

export async function getUmmsReadonlyCustomerCoreFunctions(): Promise<UmmsCustomerCoreFunctions> {
  const { data } = await request.get('/v1/one/umms/customer-core-functions')
  return normalizeCustomerCoreFunctions(unwrapData<unknown>(data))
}

export async function getUmmsReadonlySafetyPosture(): Promise<UmmsSafetyPosture> {
  const { data } = await request.get('/v1/one/umms/safety-posture')
  return normalizeSafetyPosture(unwrapData<unknown>(data))
}

export async function getUmmsReadonlyOverview(): Promise<UmmsReadonlyOverview> {
  try {
    const [packageEntry, stakeholderReview, readinessSummary, customerCoreFunctions, safetyPosture] = await Promise.all([
      getUmmsReadonlyPackageEntry(),
      getUmmsReadonlyStakeholderReview(),
      getUmmsReadonlyReadinessSummary(),
      getUmmsReadonlyCustomerCoreFunctions(),
      getUmmsReadonlySafetyPosture(),
    ])
    return {
      packageEntry,
      stakeholderReview,
      readinessSummary,
      customerCoreFunctions,
      safetyPosture,
      fallbackActive: false,
      fallbackMessage: '',
    }
  } catch {
    return {
      packageEntry: fallbackPackageEntry(),
      stakeholderReview: fallbackStakeholderReview(),
      readinessSummary: fallbackReadinessSummary(),
      customerCoreFunctions: fallbackCustomerCoreFunctions(),
      safetyPosture: fallbackSafetyPosture(),
      fallbackActive: true,
      fallbackMessage: 'UMMS readiness data unavailable, read-only fallback active.',
    }
  }
}
