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

