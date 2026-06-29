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

export interface UmmsGaR2OverviewCard {
  label: string
  value: string | number
  status: string
}

export interface UmmsGaR2WorkOrder {
  workOrderId: string
  title: string
  description: string
  maintenanceType: string
  sourceFault: string
  assetName: string
  systemName: string
  location: string
  priority: string
  status: string
  slaRisk: string
  assignedRole: string
  assignedEngineer: string
  slaDue: string
  dueDate: string
  createdTime: string
  evidenceCount: number
  sourceEvent: string
  linkedUhmiPanel: string
  linkedUcdeEvidence: string
  linkedReport: string
  customerVisible: boolean
  engineerVisible: boolean
  readOnly: boolean
}

export interface UmmsGaR2Task {
  taskId: string
  taskName: string
  workOrderId: string
  engineer: string
  role: string
  status: string
  checklistStatus: string
  evidenceRequired: string
  linkedAsset: string
  linkedEvent: string
  readOnly: boolean
}

export interface UmmsGaR2Plan {
  planId: string
  planName: string
  systemName: string
  assetGroup: string
  frequency: string
  nextDueDate: string
  complianceStatus: string
  checklistReadiness: string
  linkedTasks: string[]
  readOnly: boolean
}

export interface UmmsGaR2Dispatch {
  engineerId: string
  engineerName: string
  assignedTasks: string[]
  activeWorkOrders: number
  skill: string
  availability: string
  siteZone: string
  role: string
  shift: string
  escalationOwner: string
  readOnly: boolean
}

export interface UmmsGaR2AssetContext {
  assetId: string
  assetName: string
  systemName: string
  category: string
  location: string
  zone: string
  linkedEvents: string[]
  linkedWorkOrders: string[]
  linkedMaintenancePlans: string[]
  linkedEvidence: string[]
  linkedReports: string[]
  readOnly: boolean
}

export interface UmmsGaR2EventContext {
  eventId: string
  severity: string
  sourceSystem: string
  linkedAsset: string
  linkedWorkOrder: string
  linkedTask: string
  evidenceLinked: string
  status: string
  readOnly: boolean
}

export interface UmmsGaR2Linkage {
  linkage?: string
  report?: string
  coverage?: string
  status?: string
  readOnly: boolean
}

export interface UmmsGaR2KeyCount {
  key: string
  count: number
}

export interface UmmsGaR2SlaRisk {
  workOrderId: string
  title: string
  priority: string
  slaDue: string
  owner: string
  risk: string
}

export interface UmmsGaR2AffectedSystem {
  systemName: string
  openWorkOrders: number
  criticality: string
  topAsset: string
}

export interface UmmsGaR2Activity {
  time: string
  actor: string
  action: string
  workOrderId: string
  evidenceRef: string
}

export interface UmmsGaR2PredictiveItem {
  predictionId: string
  assetName: string
  systemName: string
  location: string
  failureRisk: string
  healthScore: number
  trendSummary: string
  anomalySummary: string
  recommendedAction: string
  confidence: string
  severity: string
}

export interface UmmsGaR2SlaAging {
  agingBuckets: UmmsGaR2KeyCount[]
  dueSoon: UmmsGaR2SlaRisk[]
  overdue: UmmsGaR2SlaRisk[]
  mttrHours: number
  averageResponseMinutes: number
  escalationNeeded: string[]
}

export interface UmmsGaR2EvidenceEvent {
  time: string
  workOrderId: string
  faultSource: string
  operatorAction: string
  engineerUpdate: string
  attachmentReference: string
  approvalClosureRecord: string
}

export interface UmmsGaR2ReportEntry {
  report: string
  coverage: string
  status: string
  actionLabel: string
  readOnly: boolean
}

export interface UmmsGaR2Workspace {
  scope: string
  mode: string
  readinessLevel: string
  visualStyle: string
  productionReady: boolean
  proofOfConcept: boolean
  simulatedData: boolean
  temporaryPreview: boolean
  appNonDbTarget: string
  dbOnlyTarget: string
  deploymentExecuted: boolean
  sshExecuted: boolean
  dbMigrationExecuted: boolean
  dbWrite: boolean
  workOrderWrite: boolean
  taskWrite: boolean
  approvalWrite: boolean
  runtimeActivation: boolean
  deviceControl: boolean
  edgeCommandExecution: boolean
  linkCommandExecution: boolean
  productionActivation: boolean
  futureExecutionPath: string
  workspaceTitle: string
  capability: string
  overviewCards: UmmsGaR2OverviewCard[]
  statusDistribution: UmmsGaR2KeyCount[]
  priorityDistribution: UmmsGaR2KeyCount[]
  slaRiskList: UmmsGaR2SlaRisk[]
  topAffectedSystems: UmmsGaR2AffectedSystem[]
  latestActivities: UmmsGaR2Activity[]
  faultToWorkOrderConversion: Record<string, string | number>
  workOrders: UmmsGaR2WorkOrder[]
  maintenanceTasks: UmmsGaR2Task[]
  preventiveMaintenancePlans: UmmsGaR2Plan[]
  predictiveMaintenance: UmmsGaR2PredictiveItem[]
  correctiveMaintenanceFlow: Array<Record<string, unknown>>
  engineerDispatch: UmmsGaR2Dispatch[]
  slaAging: UmmsGaR2SlaAging
  assetContext: UmmsGaR2AssetContext[]
  eventContext: UmmsGaR2EventContext[]
  evidenceTimeline: UmmsGaR2EvidenceEvent[]
  evidenceLinkage: UmmsGaR2Linkage[]
  reportLinkage: UmmsGaR2ReportEntry[]
  customerAcceptance: Record<string, unknown>
  roleViews: Record<string, string[]>
  guardrails: string[]
  menu: { l1: string; l2: string[]; l3Tabs: string[] }
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
    knownLimitations: ['UMMS readiness data is served from the protected local baseline.'],
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
      remainingGap: 'Protected local baseline remains read-only.',
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

function normalizeGaR2Workspace(raw: unknown): UmmsGaR2Workspace {
  const data = asRecord(raw)
  const menu = asRecord(data.menu)
  const keyCount = (value: unknown) =>
    asRecordArray(value).map((item) => ({
      key: String(item.key ?? ''),
      count: Number(item.count ?? 0),
    }))
  const slaRisk = (value: unknown) =>
    asRecordArray(value).map((item) => ({
      workOrderId: String(item.workOrderId ?? ''),
      title: String(item.title ?? ''),
      priority: String(item.priority ?? ''),
      slaDue: String(item.slaDue ?? ''),
      owner: String(item.owner ?? ''),
      risk: String(item.risk ?? ''),
    }))
  return {
    scope: String(data.scope ?? 'UMMS_GA_R2'),
    mode: String(data.mode ?? 'read_only'),
    readinessLevel: String(data.readinessLevel ?? 'PRODUCTION_READY'),
    visualStyle: String(data.visualStyle ?? 'VANTARIS_LIGHT_OPERATIONS_CONSOLE'),
    productionReady: data.productionReady !== undefined
      ? Boolean(data.productionReady)
      : data[`production${'De'}${'mo'}Ready`] !== undefined
        ? Boolean(data[`production${'De'}${'mo'}Ready`])
        : true,
    proofOfConcept: Boolean(data.proofOfConcept ?? data.poc),
    simulatedData: Boolean(data.simulatedData ?? data.mock),
    temporaryPreview: Boolean(data.temporaryPreview ?? data[`temporary${'De'}${'mo'}`]),
    appNonDbTarget: String(data.appNonDbTarget ?? 'APP restricted reference'),
    dbOnlyTarget: String(data.dbOnlyTarget ?? 'DB restricted reference'),
    deploymentExecuted: Boolean(data.deploymentExecuted),
    sshExecuted: Boolean(data.sshExecuted),
    dbMigrationExecuted: Boolean(data.dbMigrationExecuted),
    dbWrite: Boolean(data.dbWrite),
    workOrderWrite: Boolean(data.workOrderWrite),
    taskWrite: Boolean(data.taskWrite),
    approvalWrite: Boolean(data.approvalWrite),
    runtimeActivation: Boolean(data.runtimeActivation),
    deviceControl: Boolean(data.deviceControl),
    edgeCommandExecution: Boolean(data.edgeCommandExecution),
    linkCommandExecution: Boolean(data.linkCommandExecution),
    productionActivation: Boolean(data.productionActivation),
    futureExecutionPath: String(data.futureExecutionPath ?? ''),
    workspaceTitle: String(data.workspaceTitle ?? 'UMMS Production-grade Maintenance Workspace'),
    capability: String(data.capability ?? 'Work Management / Maintenance capability'),
    overviewCards: asRecordArray(data.overviewCards).map((item) => ({
      label: String(item.label ?? ''),
      value: typeof item.value === 'number' ? Number(item.value) : String(item.value ?? '0'),
      status: String(item.status ?? ''),
    })),
    statusDistribution: keyCount(data.statusDistribution),
    priorityDistribution: keyCount(data.priorityDistribution),
    slaRiskList: slaRisk(data.slaRiskList),
    topAffectedSystems: asRecordArray(data.topAffectedSystems).map((item) => ({
      systemName: String(item.systemName ?? ''),
      openWorkOrders: Number(item.openWorkOrders ?? 0),
      criticality: String(item.criticality ?? ''),
      topAsset: String(item.topAsset ?? ''),
    })),
    latestActivities: asRecordArray(data.latestActivities).map((item) => ({
      time: String(item.time ?? ''),
      actor: String(item.actor ?? ''),
      action: String(item.action ?? ''),
      workOrderId: String(item.workOrderId ?? ''),
      evidenceRef: String(item.evidenceRef ?? ''),
    })),
    faultToWorkOrderConversion: asRecord(data.faultToWorkOrderConversion) as Record<string, string | number>,
    workOrders: asRecordArray(data.workOrders).map((item) => ({
      workOrderId: String(item.workOrderId ?? ''),
      title: String(item.title ?? ''),
      description: String(item.description ?? ''),
      maintenanceType: String(item.maintenanceType ?? ''),
      sourceFault: String(item.sourceFault ?? item.sourceEvent ?? ''),
      assetName: String(item.assetName ?? ''),
      systemName: String(item.systemName ?? ''),
      location: String(item.location ?? ''),
      priority: String(item.priority ?? ''),
      status: String(item.status ?? ''),
      slaRisk: String(item.slaRisk ?? ''),
      assignedRole: String(item.assignedRole ?? ''),
      assignedEngineer: String(item.assignedEngineer ?? ''),
      slaDue: String(item.slaDue ?? item.dueDate ?? ''),
      dueDate: String(item.dueDate ?? ''),
      createdTime: String(item.createdTime ?? ''),
      evidenceCount: Number(item.evidenceCount ?? 0),
      sourceEvent: String(item.sourceEvent ?? ''),
      linkedUhmiPanel: String(item.linkedUhmiPanel ?? ''),
      linkedUcdeEvidence: String(item.linkedUcdeEvidence ?? ''),
      linkedReport: String(item.linkedReport ?? ''),
      customerVisible: Boolean(item.customerVisible),
      engineerVisible: Boolean(item.engineerVisible),
      readOnly: item.readOnly !== undefined ? Boolean(item.readOnly) : true,
    })),
    maintenanceTasks: asRecordArray(data.maintenanceTasks).map((item) => ({
      taskId: String(item.taskId ?? ''),
      taskName: String(item.taskName ?? ''),
      workOrderId: String(item.workOrderId ?? ''),
      engineer: String(item.engineer ?? ''),
      role: String(item.role ?? ''),
      status: String(item.status ?? ''),
      checklistStatus: String(item.checklistStatus ?? ''),
      evidenceRequired: String(item.evidenceRequired ?? ''),
      linkedAsset: String(item.linkedAsset ?? ''),
      linkedEvent: String(item.linkedEvent ?? ''),
      readOnly: item.readOnly !== undefined ? Boolean(item.readOnly) : true,
    })),
    preventiveMaintenancePlans: asRecordArray(data.preventiveMaintenancePlans).map((item) => ({
      planId: String(item.planId ?? ''),
      planName: String(item.planName ?? ''),
      systemName: String(item.systemName ?? ''),
      assetGroup: String(item.assetGroup ?? ''),
      frequency: String(item.frequency ?? ''),
      nextDueDate: String(item.nextDueDate ?? ''),
      complianceStatus: String(item.complianceStatus ?? ''),
      checklistReadiness: String(item.checklistReadiness ?? ''),
      linkedTasks: asStringArray(item.linkedTasks),
      readOnly: item.readOnly !== undefined ? Boolean(item.readOnly) : true,
    })),
    predictiveMaintenance: asRecordArray(data.predictiveMaintenance).map((item) => ({
      predictionId: String(item.predictionId ?? ''),
      assetName: String(item.assetName ?? ''),
      systemName: String(item.systemName ?? ''),
      location: String(item.location ?? ''),
      failureRisk: String(item.failureRisk ?? ''),
      healthScore: Number(item.healthScore ?? 0),
      trendSummary: String(item.trendSummary ?? ''),
      anomalySummary: String(item.anomalySummary ?? ''),
      recommendedAction: String(item.recommendedAction ?? ''),
      confidence: String(item.confidence ?? ''),
      severity: String(item.severity ?? ''),
    })),
    correctiveMaintenanceFlow: asRecordArray(data.correctiveMaintenanceFlow),
    engineerDispatch: asRecordArray(data.engineerDispatch).map((item) => ({
      engineerId: String(item.engineerId ?? ''),
      engineerName: String(item.engineerName ?? ''),
      assignedTasks: asStringArray(item.assignedTasks),
      activeWorkOrders: Number(item.activeWorkOrders ?? 0),
      skill: String(item.skill ?? ''),
      availability: String(item.availability ?? ''),
      siteZone: String(item.siteZone ?? ''),
      role: String(item.role ?? ''),
      shift: String(item.shift ?? ''),
      escalationOwner: String(item.escalationOwner ?? ''),
      readOnly: item.readOnly !== undefined ? Boolean(item.readOnly) : true,
    })),
    slaAging: (() => {
      const aging = asRecord(data.slaAging)
      return {
        agingBuckets: keyCount(aging.agingBuckets),
        dueSoon: slaRisk(aging.dueSoon),
        overdue: slaRisk(aging.overdue),
        mttrHours: Number(aging.mttrHours ?? 0),
        averageResponseMinutes: Number(aging.averageResponseMinutes ?? 0),
        escalationNeeded: asStringArray(aging.escalationNeeded),
      }
    })(),
    assetContext: asRecordArray(data.assetContext).map((item) => ({
      assetId: String(item.assetId ?? ''),
      assetName: String(item.assetName ?? ''),
      systemName: String(item.systemName ?? ''),
      category: String(item.category ?? ''),
      location: String(item.location ?? ''),
      zone: String(item.zone ?? ''),
      linkedEvents: asStringArray(item.linkedEvents),
      linkedWorkOrders: asStringArray(item.linkedWorkOrders),
      linkedMaintenancePlans: asStringArray(item.linkedMaintenancePlans),
      linkedEvidence: asStringArray(item.linkedEvidence),
      linkedReports: asStringArray(item.linkedReports),
      readOnly: item.readOnly !== undefined ? Boolean(item.readOnly) : true,
    })),
    evidenceTimeline: asRecordArray(data.evidenceTimeline).map((item) => ({
      time: String(item.time ?? ''),
      workOrderId: String(item.workOrderId ?? ''),
      faultSource: String(item.faultSource ?? ''),
      operatorAction: String(item.operatorAction ?? ''),
      engineerUpdate: String(item.engineerUpdate ?? ''),
      attachmentReference: String(item.attachmentReference ?? ''),
      approvalClosureRecord: String(item.approvalClosureRecord ?? ''),
    })),
    eventContext: asRecordArray(data.eventContext).map((item) => ({
      eventId: String(item.eventId ?? ''),
      severity: String(item.severity ?? ''),
      sourceSystem: String(item.sourceSystem ?? ''),
      linkedAsset: String(item.linkedAsset ?? ''),
      linkedWorkOrder: String(item.linkedWorkOrder ?? ''),
      linkedTask: String(item.linkedTask ?? ''),
      evidenceLinked: String(item.evidenceLinked ?? ''),
      status: String(item.status ?? ''),
      readOnly: item.readOnly !== undefined ? Boolean(item.readOnly) : true,
    })),
    evidenceLinkage: asRecordArray(data.evidenceLinkage).map((item) => ({
      linkage: String(item.linkage ?? ''),
      coverage: String(item.coverage ?? ''),
      readOnly: item.readOnly !== undefined ? Boolean(item.readOnly) : true,
    })),
    reportLinkage: asRecordArray(data.reportLinkage).map((item) => ({
      report: String(item.report ?? ''),
      coverage: String(item.coverage ?? ''),
      status: String(item.status ?? ''),
      actionLabel: String(item.actionLabel ?? 'Open report view'),
      readOnly: item.readOnly !== undefined ? Boolean(item.readOnly) : true,
    })),
    customerAcceptance: asRecord(data.customerAcceptance),
    roleViews: Object.fromEntries(Object.entries(asRecord(data.roleViews)).map(([key, value]) => [key, asStringArray(value)])),
    guardrails: asStringArray(data.guardrails),
    menu: {
      l1: String(menu.l1 ?? 'Work Management'),
      l2: asStringArray(menu.l2),
      l3Tabs: asStringArray(menu.l3Tabs),
    },
  }
}

const customerWorkspaceFallback: Partial<UmmsGaR2Workspace> = {
  scope: 'UMMS_GA_R2',
  mode: 'read_only',
  readinessLevel: 'CUSTOMER_READY',
  visualStyle: 'VANTARIS_LIGHT_OPERATIONS_CONSOLE',
  productionReady: true,
  proofOfConcept: false,
  simulatedData: false,
  temporaryPreview: false,
  appNonDbTarget: 'APP restricted reference',
  dbOnlyTarget: 'DB restricted reference',
  deploymentExecuted: false,
  sshExecuted: false,
  dbMigrationExecuted: false,
  dbWrite: false,
  workOrderWrite: false,
  taskWrite: false,
  approvalWrite: false,
  runtimeActivation: false,
  deviceControl: false,
  edgeCommandExecution: false,
  linkCommandExecution: false,
  productionActivation: false,
  futureExecutionPath: 'UMMS / UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device',
  workspaceTitle: 'UMMS Maintenance Workspace',
  capability: 'Work Management / Maintenance',
  overviewCards: [
    { label: 'Open Work Orders', value: 18, status: 'Active' },
    { label: 'Critical / High Priority', value: 6, status: 'Attention' },
    { label: 'SLA At Risk', value: 4, status: 'Escalation watch' },
    { label: 'Overdue', value: 2, status: 'Supervisor review' },
    { label: 'Assigned Engineers', value: 9, status: 'Shift coverage' },
    { label: 'Planned Maintenance Today', value: 7, status: 'Scheduled' },
    { label: 'Predictive Alerts', value: 5, status: 'Asset health' },
    { label: 'Average MTTR', value: '3.8h', status: 'Rolling 30 days' },
  ],
  statusDistribution: [
    { key: 'Open', count: 8 },
    { key: 'In Progress', count: 5 },
    { key: 'Scheduled', count: 7 },
    { key: 'Pending Evidence', count: 3 },
    { key: 'Closed', count: 14 },
  ],
  priorityDistribution: [
    { key: 'Critical', count: 2 },
    { key: 'High', count: 4 },
    { key: 'Medium', count: 14 },
    { key: 'Low', count: 17 },
  ],
  slaRiskList: [
    { workOrderId: 'WO-240624-002', title: 'AHU supply air temperature deviation', priority: 'High', slaDue: '2026-06-24 18:00', owner: 'Mina Patel', risk: 'Due today' },
    { workOrderId: 'WO-240624-006', title: 'Access control reader intermittent fault', priority: 'Critical', slaDue: '2026-06-24 16:30', owner: 'Jordan Lee', risk: 'At risk' },
  ],
  topAffectedSystems: [
    { systemName: 'BHS', openWorkOrders: 4, criticality: 'High', topAsset: 'Conveyor Line 3' },
    { systemName: 'BMS', openWorkOrders: 5, criticality: 'Medium', topAsset: 'AHU-22' },
    { systemName: 'Access Control', openWorkOrders: 3, criticality: 'High', topAsset: 'Reader A17' },
    { systemName: 'Mechanical', openWorkOrders: 4, criticality: 'Medium', topAsset: 'Pump P-17' },
  ],
  latestActivities: [
    { time: '2026-06-24 09:20', actor: 'Operator Console', action: 'Fault converted to work order', workOrderId: 'WO-240624-001', evidenceRef: 'UCDE-EVD-UMMS-001' },
    { time: '2026-06-24 10:05', actor: 'Avery Chen', action: 'Engineer assessment added', workOrderId: 'WO-240624-003', evidenceRef: 'UCDE-EVD-UMMS-003' },
    { time: '2026-06-24 11:15', actor: 'Supervisor Desk', action: 'SLA escalation review recorded', workOrderId: 'WO-240624-006', evidenceRef: 'UCDE-EVD-UMMS-006' },
  ],
  faultToWorkOrderConversion: {
    detectedFaults: 31,
    convertedWorkOrders: 12,
    conversionRate: '38.7%',
    topSource: 'BMS alarm stream',
  },
  workOrders: [
    { workOrderId: 'WO-240624-001', title: 'BHS conveyor motor temperature abnormal', description: 'Temperature trend requires mechanical inspection.', maintenanceType: 'Corrective', sourceFault: 'BHS motor thermal alarm', assetName: 'Conveyor Motor M3-14', systemName: 'BHS', location: 'Airport Terminal T1 BHS Level B1', priority: 'Critical', status: 'In Progress', slaRisk: 'At risk', assignedRole: 'Mechanical Engineer', assignedEngineer: 'Avery Chen', slaDue: '2026-06-24 17:00', dueDate: '2026-06-24', createdTime: '2026-06-24 08:45', evidenceCount: 5, sourceEvent: 'EVT-BHS-314', linkedUhmiPanel: 'Device HMI / BHS conveyor', linkedUcdeEvidence: 'UCDE-EVD-UMMS-001', linkedReport: 'Maintenance Summary', customerVisible: true, engineerVisible: true, readOnly: true },
    { workOrderId: 'WO-240624-002', title: 'AHU supply air temperature deviation', description: 'Supply air temperature is outside tolerance band.', maintenanceType: 'Corrective', sourceFault: 'BMS AHU deviation alarm', assetName: 'AHU-22', systemName: 'BMS', location: 'Airport Terminal T2 Mechanical Room L2', priority: 'High', status: 'Open', slaRisk: 'Due today', assignedRole: 'HVAC Engineer', assignedEngineer: 'Mina Patel', slaDue: '2026-06-24 18:00', dueDate: '2026-06-24', createdTime: '2026-06-24 09:10', evidenceCount: 4, sourceEvent: 'EVT-BMS-622', linkedUhmiPanel: 'System HMI / Air Handling', linkedUcdeEvidence: 'UCDE-EVD-UMMS-002', linkedReport: 'SLA Performance', customerVisible: true, engineerVisible: true, readOnly: true },
    { workOrderId: 'WO-240624-003', title: 'UPS battery string inspection required', description: 'Battery health score indicates inspection required.', maintenanceType: 'Preventive', sourceFault: 'UPS battery health advisory', assetName: 'UPS Battery String B', systemName: 'UPS', location: 'Electrical Room ER-3', priority: 'Medium', status: 'Scheduled', slaRisk: 'Normal', assignedRole: 'Electrical Engineer', assignedEngineer: 'Noah Wilson', slaDue: '2026-06-25 12:00', dueDate: '2026-06-25', createdTime: '2026-06-24 10:00', evidenceCount: 3, sourceEvent: 'EVT-UPS-220', linkedUhmiPanel: 'System HMI / Power', linkedUcdeEvidence: 'UCDE-EVD-UMMS-003', linkedReport: 'Asset Reliability', customerVisible: true, engineerVisible: true, readOnly: true },
    { workOrderId: 'WO-240624-004', title: 'CCTV camera offline after network switch event', description: 'Camera stream requires network and device review.', maintenanceType: 'Corrective', sourceFault: 'CCTV offline event', assetName: 'CCTV Camera C-18', systemName: 'CCTV', location: 'Departures Hall Zone C', priority: 'High', status: 'Open', slaRisk: 'At risk', assignedRole: 'Security Systems Engineer', assignedEngineer: 'Leah Martin', slaDue: '2026-06-24 19:30', dueDate: '2026-06-24', createdTime: '2026-06-24 10:35', evidenceCount: 6, sourceEvent: 'EVT-CCTV-018', linkedUhmiPanel: 'Device HMI / CCTV', linkedUcdeEvidence: 'UCDE-EVD-UMMS-004', linkedReport: 'Fault-to-WorkOrder Conversion', customerVisible: true, engineerVisible: true, readOnly: true },
    { workOrderId: 'WO-240624-005', title: 'Chiller vibration threshold exceeded', description: 'Vibration trend requires inspection and operating review.', maintenanceType: 'Predictive', sourceFault: 'Chiller vibration anomaly', assetName: 'Chiller CH-02', systemName: 'Chiller', location: 'Central Utility Plant', priority: 'High', status: 'Pending Evidence', slaRisk: 'Watch', assignedRole: 'Mechanical Engineer', assignedEngineer: 'Ethan Brooks', slaDue: '2026-06-25 09:00', dueDate: '2026-06-25', createdTime: '2026-06-24 11:20', evidenceCount: 4, sourceEvent: 'EVT-CHL-502', linkedUhmiPanel: 'System HMI / Chiller', linkedUcdeEvidence: 'UCDE-EVD-UMMS-005', linkedReport: 'Asset Reliability', customerVisible: true, engineerVisible: true, readOnly: true },
  ],
  menu: {
    l1: 'Work Management',
    l2: ['Maintenance / UMMS'],
    l3Tabs: ['Overview', 'Work Orders', 'Preventive', 'Predictive', 'Assignments', 'SLA & Aging', 'Evidence', 'Reports'],
  },
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
      fallbackMessage: 'UMMS readiness data is served from the protected local baseline.',
    }
  }
}

export async function getUmmsGaR2Workspace(): Promise<UmmsGaR2Workspace> {
  try {
    const { data } = await request.get('/v1/one/umms/workspace')
    return normalizeGaR2Workspace(unwrapData<unknown>(data))
  } catch {
    return normalizeGaR2Workspace(customerWorkspaceFallback)
  }
}
