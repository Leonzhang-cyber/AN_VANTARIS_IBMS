import request from './request'

export interface UesgHealth {
  status: string
  moduleId: string
  moduleName: string
  provider: string
  runtimeMode: string
  sourceSemantics: string
  mockData: boolean
  readOnly: boolean
  controlActionsEnabled: boolean
  meterIntegrationEnabled: boolean
  edgeRuntimeIntegrated: boolean
  linkRuntimeIntegrated: boolean
  carbonFactorDatabaseIntegrated: boolean
  totalMetrics: number
  runtimeLinkedMetrics: number
  certified: boolean
  iec62443Certified: boolean
  greenMarkCertified: boolean
  griCertified: boolean
  isoCertified: boolean
}

export interface UesgMetric {
  metricId: string
  metricName: string
  metricCategory: string
  metricScope: string
  metricPeriod: string
  siteId: string
  siteName: string
  systemId: string
  systemName: string
  value: number
  unit: string
  dataQuality: string
  sourceSystem: string
  sourceRecordId: string
  provider: string
  runtimeMode: string
  sourceSemantics: string
  mockData: boolean
  readOnly: boolean
  controlActionsEnabled: boolean
  meterIntegrationEnabled: boolean
  edgeRuntimeIntegrated: boolean
  linkRuntimeIntegrated: boolean
  carbonFactorDatabaseIntegrated: boolean
  createdAt: string
  updatedAt: string
  tags: string[]
  metadata: Record<string, unknown>
  limitations: string[]
  runtimeLinked: boolean
  certified: boolean
  iec62443Certified: boolean
  greenMarkCertified: boolean
  griCertified: boolean
  isoCertified: boolean
}

export interface UesgMetricsSummary {
  totalMetrics: number
  energyMetrics: number
  carbonMetrics: number
  waterMetrics: number
  wasteMetrics: number
  environmentMetrics: number
  mockMetrics: number
  runtimeLinkedMetrics: number
  certifiedMetrics: number
  iec62443CertifiedMetrics: number
  greenMarkCertifiedMetrics: number
  griCertifiedMetrics: number
  isoCertifiedMetrics: number
  metricCategories: string[]
  metricScopes: string[]
  metricPeriods: string[]
  dataQualityLevels: string[]
  limitations: string[]
}

export interface UesgBreakdown {
  breakdownMode: string
  items: Array<{
    category: string
    count: number
    scopes: string[]
    periods: string[]
    runtimeLinked: boolean
  }>
  runtimeLinked: boolean
  certified: boolean
  iec62443Certified: boolean
  greenMarkCertified: boolean
  griCertified: boolean
  isoCertified: boolean
  notes: string
}

export interface UesgAssociations {
  associationMode: string
  items: Array<{
    associationId: string
    metricId: string
    siteId: string
    systemId: string
    associationType: string
    runtimeLinked: boolean
    notes: string
  }>
  runtimeLinked: boolean
  certified: boolean
  iec62443Certified: boolean
  greenMarkCertified: boolean
  griCertified: boolean
  isoCertified: boolean
  notes: string
}

export interface UesgMetricListResponse {
  items: UesgMetric[]
  total: number
  filters: {
    metricCategory: string
    metricScope: string
    metricPeriod: string
    siteId: string
    systemId: string
    dataQuality: string
  }
  summary: UesgMetricsSummary
  provider: string
  runtimeMode: string
  sourceSemantics: string
  mockData: boolean
  readOnly: boolean
  certified: boolean
  iec62443Certified: boolean
  greenMarkCertified: boolean
  griCertified: boolean
  isoCertified: boolean
}

export interface GetUesgMetricsParams {
  metricCategory?: string
  metricScope?: string
  metricPeriod?: string
  siteId?: string
  systemId?: string
  dataQuality?: string
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

function normalizeMetric(raw: unknown): UesgMetric {
  const data = asRecord(raw)
  return {
    metricId: String(data.metricId ?? ''),
    metricName: String(data.metricName ?? ''),
    metricCategory: String(data.metricCategory ?? ''),
    metricScope: String(data.metricScope ?? ''),
    metricPeriod: String(data.metricPeriod ?? ''),
    siteId: String(data.siteId ?? ''),
    siteName: String(data.siteName ?? ''),
    systemId: String(data.systemId ?? ''),
    systemName: String(data.systemName ?? ''),
    value: Number(data.value ?? 0),
    unit: String(data.unit ?? ''),
    dataQuality: String(data.dataQuality ?? ''),
    sourceSystem: String(data.sourceSystem ?? ''),
    sourceRecordId: String(data.sourceRecordId ?? ''),
    provider: String(data.provider ?? 'local-uesg-provider'),
    runtimeMode: String(data.runtimeMode ?? 'skeleton'),
    sourceSemantics: String(data.sourceSemantics ?? 'ibms-neutral'),
    mockData: data.mockData !== undefined ? Boolean(data.mockData) : true,
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    controlActionsEnabled: Boolean(data.controlActionsEnabled),
    meterIntegrationEnabled: Boolean(data.meterIntegrationEnabled),
    edgeRuntimeIntegrated: Boolean(data.edgeRuntimeIntegrated),
    linkRuntimeIntegrated: Boolean(data.linkRuntimeIntegrated),
    carbonFactorDatabaseIntegrated: Boolean(data.carbonFactorDatabaseIntegrated),
    createdAt: String(data.createdAt ?? ''),
    updatedAt: String(data.updatedAt ?? ''),
    tags: asStringArray(data.tags),
    metadata: asRecord(data.metadata),
    limitations: asStringArray(data.limitations),
    runtimeLinked: Boolean(data.runtimeLinked),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
    greenMarkCertified: Boolean(data.greenMarkCertified),
    griCertified: Boolean(data.griCertified),
    isoCertified: Boolean(data.isoCertified),
  }
}

function normalizeHealth(raw: unknown): UesgHealth {
  const data = asRecord(raw)
  return {
    status: String(data.status ?? 'unknown'),
    moduleId: String(data.moduleId ?? 'uesg'),
    moduleName: String(data.moduleName ?? 'UESG Sustainability'),
    provider: String(data.provider ?? 'local-uesg-provider'),
    runtimeMode: String(data.runtimeMode ?? 'skeleton'),
    sourceSemantics: String(data.sourceSemantics ?? 'ibms-neutral'),
    mockData: data.mockData !== undefined ? Boolean(data.mockData) : true,
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    controlActionsEnabled: Boolean(data.controlActionsEnabled),
    meterIntegrationEnabled: Boolean(data.meterIntegrationEnabled),
    edgeRuntimeIntegrated: Boolean(data.edgeRuntimeIntegrated),
    linkRuntimeIntegrated: Boolean(data.linkRuntimeIntegrated),
    carbonFactorDatabaseIntegrated: Boolean(data.carbonFactorDatabaseIntegrated),
    totalMetrics: Number(data.totalMetrics ?? 0),
    runtimeLinkedMetrics: Number(data.runtimeLinkedMetrics ?? 0),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
    greenMarkCertified: Boolean(data.greenMarkCertified),
    griCertified: Boolean(data.griCertified),
    isoCertified: Boolean(data.isoCertified),
  }
}

function normalizeSummary(raw: unknown): UesgMetricsSummary {
  const data = asRecord(raw)
  return {
    totalMetrics: Number(data.totalMetrics ?? 0),
    energyMetrics: Number(data.energyMetrics ?? 0),
    carbonMetrics: Number(data.carbonMetrics ?? 0),
    waterMetrics: Number(data.waterMetrics ?? 0),
    wasteMetrics: Number(data.wasteMetrics ?? 0),
    environmentMetrics: Number(data.environmentMetrics ?? 0),
    mockMetrics: Number(data.mockMetrics ?? 0),
    runtimeLinkedMetrics: Number(data.runtimeLinkedMetrics ?? 0),
    certifiedMetrics: Number(data.certifiedMetrics ?? 0),
    iec62443CertifiedMetrics: Number(data.iec62443CertifiedMetrics ?? 0),
    greenMarkCertifiedMetrics: Number(data.greenMarkCertifiedMetrics ?? 0),
    griCertifiedMetrics: Number(data.griCertifiedMetrics ?? 0),
    isoCertifiedMetrics: Number(data.isoCertifiedMetrics ?? 0),
    metricCategories: asStringArray(data.metricCategories),
    metricScopes: asStringArray(data.metricScopes),
    metricPeriods: asStringArray(data.metricPeriods),
    dataQualityLevels: asStringArray(data.dataQualityLevels),
    limitations: asStringArray(data.limitations),
  }
}

function normalizeBreakdown(raw: unknown): UesgBreakdown {
  const data = asRecord(raw)
  return {
    breakdownMode: String(data.breakdownMode ?? 'local-skeleton-breakdown'),
    items: asRecordArray(data.items).map((item) => ({
      category: String(item.category ?? ''),
      count: Number(item.count ?? 0),
      scopes: asStringArray(item.scopes),
      periods: asStringArray(item.periods),
      runtimeLinked: Boolean(item.runtimeLinked),
    })),
    runtimeLinked: Boolean(data.runtimeLinked),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
    greenMarkCertified: Boolean(data.greenMarkCertified),
    griCertified: Boolean(data.griCertified),
    isoCertified: Boolean(data.isoCertified),
    notes: String(data.notes ?? ''),
  }
}

function normalizeAssociations(raw: unknown): UesgAssociations {
  const data = asRecord(raw)
  return {
    associationMode: String(data.associationMode ?? 'local-skeleton-associations'),
    items: asRecordArray(data.items).map((item) => ({
      associationId: String(item.associationId ?? ''),
      metricId: String(item.metricId ?? ''),
      siteId: String(item.siteId ?? ''),
      systemId: String(item.systemId ?? ''),
      associationType: String(item.associationType ?? ''),
      runtimeLinked: Boolean(item.runtimeLinked),
      notes: String(item.notes ?? ''),
    })),
    runtimeLinked: Boolean(data.runtimeLinked),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
    greenMarkCertified: Boolean(data.greenMarkCertified),
    griCertified: Boolean(data.griCertified),
    isoCertified: Boolean(data.isoCertified),
    notes: String(data.notes ?? ''),
  }
}

function normalizeList(raw: unknown): UesgMetricListResponse {
  const data = asRecord(raw)
  const filters = asRecord(data.filters)
  return {
    items: asRecordArray(data.items).map((item) => normalizeMetric(item)),
    total: Number(data.total ?? 0),
    filters: {
      metricCategory: String(filters.metricCategory ?? ''),
      metricScope: String(filters.metricScope ?? ''),
      metricPeriod: String(filters.metricPeriod ?? ''),
      siteId: String(filters.siteId ?? ''),
      systemId: String(filters.systemId ?? ''),
      dataQuality: String(filters.dataQuality ?? ''),
    },
    summary: normalizeSummary(data.summary),
    provider: String(data.provider ?? 'local-uesg-provider'),
    runtimeMode: String(data.runtimeMode ?? 'skeleton'),
    sourceSemantics: String(data.sourceSemantics ?? 'ibms-neutral'),
    mockData: data.mockData !== undefined ? Boolean(data.mockData) : true,
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
    greenMarkCertified: Boolean(data.greenMarkCertified),
    griCertified: Boolean(data.griCertified),
    isoCertified: Boolean(data.isoCertified),
  }
}

export async function getUesgHealth(): Promise<UesgHealth> {
  const { data } = await request.get('/v1/uesg/health')
  return normalizeHealth(unwrapData<unknown>(data))
}

export async function getUesgMetrics(params: GetUesgMetricsParams = {}): Promise<UesgMetricListResponse> {
  const { data } = await request.get('/v1/uesg/metrics', { params })
  return normalizeList(unwrapData<unknown>(data))
}

export async function getUesgMetricsSummary(): Promise<UesgMetricsSummary> {
  const { data } = await request.get('/v1/uesg/metrics/summary')
  return normalizeSummary(unwrapData<unknown>(data))
}

export async function getUesgMetricsBreakdown(): Promise<UesgBreakdown> {
  const { data } = await request.get('/v1/uesg/metrics/breakdown')
  return normalizeBreakdown(unwrapData<unknown>(data))
}

export async function getUesgAssociations(): Promise<UesgAssociations> {
  const { data } = await request.get('/v1/uesg/associations')
  return normalizeAssociations(unwrapData<unknown>(data))
}

export async function getUesgMetricDetail(metricId: string): Promise<UesgMetric> {
  const { data } = await request.get(`/v1/uesg/metrics/${encodeURIComponent(metricId)}`)
  return normalizeMetric(unwrapData<unknown>(data))
}

