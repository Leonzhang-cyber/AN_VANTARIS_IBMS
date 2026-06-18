import request from './request'

export interface EsgCalculationDetail {
  calculationMode: string
  formulaMode: string
  inputReferences: string[]
  assumptions: string[]
  dataQuality: string
  calculationReady: boolean
  runtimeLinked: boolean
  carbonFactorDatabaseIntegrated: boolean
  meterIntegrationEnabled: boolean
  notes: string
  certified: boolean
  greenMarkCertified: boolean
  griCertified: boolean
  isoCertified: boolean
}

export interface EsgMetricRecord {
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
  calculationDetail: EsgCalculationDetail
  runtimeLinked: boolean
  certified: boolean
  iec62443Certified: boolean
  greenMarkCertified: boolean
  griCertified: boolean
  isoCertified: boolean
}

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

export interface EsgSummary {
  totalMetrics: number
  energyMetrics: number
  carbonMetrics: number
  waterMetrics: number
  wasteMetrics: number
  environmentMetrics: number
  mockMetrics: number
  categoryDetailReady: boolean
  calculationDetailReady: boolean
  associationDetailReady: boolean
  dataQualityReady: boolean
  trendPlaceholderReady: boolean
  runtimeLinkedMetrics: number
  meterLinkedMetrics: number
  carbonFactorLinkedMetrics: number
  reportReadyMetrics: number
  complianceCertifiedMetrics: number
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

export interface EsgCategoryDetail {
  categoryId: string
  categoryName: string
  categoryMode: string
  metricCount: number
  metrics: Array<{
    metricId: string
    metricName: string
    unit: string
    value: number
    dataQuality: string
  }>
  primaryUnit: string
  units: string[]
  totalValue: number
  dataQualitySummary: Record<string, number>
  calculationModes: string[]
  runtimeLinked: boolean
  meterIntegrationEnabled: boolean
  carbonFactorDatabaseIntegrated: boolean
  certified: boolean
  greenMarkCertified: boolean
  griCertified: boolean
  isoCertified: boolean
  limitations: string[]
}

export interface EsgCategoryDetailsResponse {
  categoryMode: string
  items: EsgCategoryDetail[]
  runtimeLinked: boolean
  certified: boolean
  greenMarkCertified: boolean
  griCertified: boolean
  isoCertified: boolean
  notes: string
}

export interface EsgAssociationModel {
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

export interface EsgAssociationDetail {
  associationMode: string
  associationSummary: {
    siteAssociationCount: number
    systemAssociationCount: number
    runtimeLinkedAssociations: number
    assetRuntimeIntegrated: boolean
  }
  siteAssociations: Array<{
    siteId: string
    siteName: string
    metricIds: string[]
    metricCategories: string[]
    runtimeLinked: boolean
  }>
  systemAssociations: Array<{
    systemId: string
    systemName: string
    metricIds: string[]
    metricCategories: string[]
    runtimeLinked: boolean
  }>
  runtimeLinked: boolean
  certified: boolean
  greenMarkCertified: boolean
  griCertified: boolean
  isoCertified: boolean
  limitations: string[]
}

export interface EsgDataQualitySummary {
  qualityMode: string
  totalMetrics: number
  qualityCounts: Record<string, number>
  runtimeLinked: boolean
  certified: boolean
  greenMarkCertified: boolean
  griCertified: boolean
  isoCertified: boolean
  limitations: string[]
}

export interface EsgTrendPlaceholder {
  trendMode: string
  periods: string[]
  trendCalculated: boolean
  periodComparisonReady: boolean
  series: unknown[]
  runtimeLinked: boolean
  limitations: string[]
  certified: boolean
  greenMarkCertified: boolean
  griCertified: boolean
  isoCertified: boolean
}

export interface EsgMetricCalculationResponse {
  metricId: string
  metricName: string
  metricCategory: string
  calculationDetail: EsgCalculationDetail
  runtimeLinked: boolean
  certified: boolean
  greenMarkCertified: boolean
  griCertified: boolean
  isoCertified: boolean
}

export interface UesgMetricListResponse {
  items: EsgMetricRecord[]
  total: number
  filters: {
    metricCategory: string
    metricScope: string
    metricPeriod: string
    siteId: string
    systemId: string
    dataQuality: string
  }
  summary: EsgSummary
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

function asNumberRecord(value: unknown): Record<string, number> {
  const data = asRecord(value)
  return Object.keys(data).reduce<Record<string, number>>((acc, key) => {
    acc[key] = Number(data[key] ?? 0)
    return acc
  }, {})
}

function unwrapData<T>(body: unknown): T {
  if (typeof body === 'object' && body !== null && 'data' in body) {
    return (body as { data: T }).data
  }
  return body as T
}

function normalizeCalculationDetail(raw: unknown): EsgCalculationDetail {
  const data = asRecord(raw)
  return {
    calculationMode: String(data.calculationMode ?? 'local-skeleton-estimate'),
    formulaMode: String(data.formulaMode ?? 'placeholder'),
    inputReferences: asStringArray(data.inputReferences),
    assumptions: asStringArray(data.assumptions),
    dataQuality: String(data.dataQuality ?? 'unknown'),
    calculationReady: Boolean(data.calculationReady),
    runtimeLinked: Boolean(data.runtimeLinked),
    carbonFactorDatabaseIntegrated: Boolean(data.carbonFactorDatabaseIntegrated),
    meterIntegrationEnabled: Boolean(data.meterIntegrationEnabled),
    notes: String(data.notes ?? ''),
    certified: Boolean(data.certified),
    greenMarkCertified: Boolean(data.greenMarkCertified),
    griCertified: Boolean(data.griCertified),
    isoCertified: Boolean(data.isoCertified),
  }
}

function normalizeMetric(raw: unknown): EsgMetricRecord {
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
    calculationDetail: normalizeCalculationDetail(data.calculationDetail),
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

function normalizeSummary(raw: unknown): EsgSummary {
  const data = asRecord(raw)
  return {
    totalMetrics: Number(data.totalMetrics ?? 0),
    energyMetrics: Number(data.energyMetrics ?? 0),
    carbonMetrics: Number(data.carbonMetrics ?? 0),
    waterMetrics: Number(data.waterMetrics ?? 0),
    wasteMetrics: Number(data.wasteMetrics ?? 0),
    environmentMetrics: Number(data.environmentMetrics ?? 0),
    mockMetrics: Number(data.mockMetrics ?? 0),
    categoryDetailReady: Boolean(data.categoryDetailReady),
    calculationDetailReady: Boolean(data.calculationDetailReady),
    associationDetailReady: Boolean(data.associationDetailReady),
    dataQualityReady: Boolean(data.dataQualityReady),
    trendPlaceholderReady: Boolean(data.trendPlaceholderReady),
    runtimeLinkedMetrics: Number(data.runtimeLinkedMetrics ?? 0),
    meterLinkedMetrics: Number(data.meterLinkedMetrics ?? 0),
    carbonFactorLinkedMetrics: Number(data.carbonFactorLinkedMetrics ?? 0),
    reportReadyMetrics: Number(data.reportReadyMetrics ?? 0),
    complianceCertifiedMetrics: Number(data.complianceCertifiedMetrics ?? 0),
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

function normalizeAssociationModel(raw: unknown): EsgAssociationModel {
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

function normalizeCategoryDetails(raw: unknown): EsgCategoryDetailsResponse {
  const data = asRecord(raw)
  return {
    categoryMode: String(data.categoryMode ?? 'local-skeleton-category'),
    items: asRecordArray(data.items).map((item) => ({
      categoryId: String(item.categoryId ?? ''),
      categoryName: String(item.categoryName ?? ''),
      categoryMode: String(item.categoryMode ?? 'local-skeleton-category'),
      metricCount: Number(item.metricCount ?? 0),
      metrics: asRecordArray(item.metrics).map((row) => ({
        metricId: String(row.metricId ?? ''),
        metricName: String(row.metricName ?? ''),
        unit: String(row.unit ?? ''),
        value: Number(row.value ?? 0),
        dataQuality: String(row.dataQuality ?? ''),
      })),
      primaryUnit: String(item.primaryUnit ?? ''),
      units: asStringArray(item.units),
      totalValue: Number(item.totalValue ?? 0),
      dataQualitySummary: asNumberRecord(item.dataQualitySummary),
      calculationModes: asStringArray(item.calculationModes),
      runtimeLinked: Boolean(item.runtimeLinked),
      meterIntegrationEnabled: Boolean(item.meterIntegrationEnabled),
      carbonFactorDatabaseIntegrated: Boolean(item.carbonFactorDatabaseIntegrated),
      certified: Boolean(item.certified),
      greenMarkCertified: Boolean(item.greenMarkCertified),
      griCertified: Boolean(item.griCertified),
      isoCertified: Boolean(item.isoCertified),
      limitations: asStringArray(item.limitations),
    })),
    runtimeLinked: Boolean(data.runtimeLinked),
    certified: Boolean(data.certified),
    greenMarkCertified: Boolean(data.greenMarkCertified),
    griCertified: Boolean(data.griCertified),
    isoCertified: Boolean(data.isoCertified),
    notes: String(data.notes ?? ''),
  }
}

function normalizeCalculationResponse(raw: unknown): EsgMetricCalculationResponse {
  const data = asRecord(raw)
  return {
    metricId: String(data.metricId ?? ''),
    metricName: String(data.metricName ?? ''),
    metricCategory: String(data.metricCategory ?? ''),
    calculationDetail: normalizeCalculationDetail(data.calculationDetail),
    runtimeLinked: Boolean(data.runtimeLinked),
    certified: Boolean(data.certified),
    greenMarkCertified: Boolean(data.greenMarkCertified),
    griCertified: Boolean(data.griCertified),
    isoCertified: Boolean(data.isoCertified),
  }
}

function normalizeAssociationDetail(raw: unknown): EsgAssociationDetail {
  const data = asRecord(raw)
  const summary = asRecord(data.associationSummary)
  return {
    associationMode: String(data.associationMode ?? 'local-skeleton-association-detail'),
    associationSummary: {
      siteAssociationCount: Number(summary.siteAssociationCount ?? 0),
      systemAssociationCount: Number(summary.systemAssociationCount ?? 0),
      runtimeLinkedAssociations: Number(summary.runtimeLinkedAssociations ?? 0),
      assetRuntimeIntegrated: Boolean(summary.assetRuntimeIntegrated),
    },
    siteAssociations: asRecordArray(data.siteAssociations).map((item) => ({
      siteId: String(item.siteId ?? ''),
      siteName: String(item.siteName ?? ''),
      metricIds: asStringArray(item.metricIds),
      metricCategories: asStringArray(item.metricCategories),
      runtimeLinked: Boolean(item.runtimeLinked),
    })),
    systemAssociations: asRecordArray(data.systemAssociations).map((item) => ({
      systemId: String(item.systemId ?? ''),
      systemName: String(item.systemName ?? ''),
      metricIds: asStringArray(item.metricIds),
      metricCategories: asStringArray(item.metricCategories),
      runtimeLinked: Boolean(item.runtimeLinked),
    })),
    runtimeLinked: Boolean(data.runtimeLinked),
    certified: Boolean(data.certified),
    greenMarkCertified: Boolean(data.greenMarkCertified),
    griCertified: Boolean(data.griCertified),
    isoCertified: Boolean(data.isoCertified),
    limitations: asStringArray(data.limitations),
  }
}

function normalizeDataQuality(raw: unknown): EsgDataQualitySummary {
  const data = asRecord(raw)
  return {
    qualityMode: String(data.qualityMode ?? 'local-skeleton-quality'),
    totalMetrics: Number(data.totalMetrics ?? 0),
    qualityCounts: asNumberRecord(data.qualityCounts),
    runtimeLinked: Boolean(data.runtimeLinked),
    certified: Boolean(data.certified),
    greenMarkCertified: Boolean(data.greenMarkCertified),
    griCertified: Boolean(data.griCertified),
    isoCertified: Boolean(data.isoCertified),
    limitations: asStringArray(data.limitations),
  }
}

function normalizeTrend(raw: unknown): EsgTrendPlaceholder {
  const data = asRecord(raw)
  return {
    trendMode: String(data.trendMode ?? 'local-skeleton-trend'),
    periods: asStringArray(data.periods),
    trendCalculated: Boolean(data.trendCalculated),
    periodComparisonReady: Boolean(data.periodComparisonReady),
    series: Array.isArray(data.series) ? data.series : [],
    runtimeLinked: Boolean(data.runtimeLinked),
    limitations: asStringArray(data.limitations),
    certified: Boolean(data.certified),
    greenMarkCertified: Boolean(data.greenMarkCertified),
    griCertified: Boolean(data.griCertified),
    isoCertified: Boolean(data.isoCertified),
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

export async function getUesgMetricsSummary(): Promise<EsgSummary> {
  const { data } = await request.get('/v1/uesg/metrics/summary')
  return normalizeSummary(unwrapData<unknown>(data))
}

export async function getUesgMetricsBreakdown(): Promise<UesgBreakdown> {
  const { data } = await request.get('/v1/uesg/metrics/breakdown')
  return normalizeBreakdown(unwrapData<unknown>(data))
}

export async function getUesgAssociations(): Promise<EsgAssociationModel> {
  const { data } = await request.get('/v1/uesg/associations')
  return normalizeAssociationModel(unwrapData<unknown>(data))
}

export async function getUesgMetricDetail(metricId: string): Promise<EsgMetricRecord> {
  const { data } = await request.get(`/v1/uesg/metrics/${encodeURIComponent(metricId)}`)
  return normalizeMetric(unwrapData<unknown>(data))
}

export async function getEsgCategoryDetails(): Promise<EsgCategoryDetailsResponse> {
  const { data } = await request.get('/v1/uesg/metrics/categories')
  return normalizeCategoryDetails(unwrapData<unknown>(data))
}

export async function getEsgMetricCalculation(metricId: string): Promise<EsgMetricCalculationResponse> {
  const { data } = await request.get(`/v1/uesg/metrics/${encodeURIComponent(metricId)}/calculation`)
  return normalizeCalculationResponse(unwrapData<unknown>(data))
}

export async function getEsgAssociationDetail(): Promise<EsgAssociationDetail> {
  const { data } = await request.get('/v1/uesg/associations/detail')
  return normalizeAssociationDetail(unwrapData<unknown>(data))
}

export async function getEsgDataQuality(): Promise<EsgDataQualitySummary> {
  const { data } = await request.get('/v1/uesg/data-quality')
  return normalizeDataQuality(unwrapData<unknown>(data))
}

export async function getEsgTrends(): Promise<EsgTrendPlaceholder> {
  const { data } = await request.get('/v1/uesg/trends')
  return normalizeTrend(unwrapData<unknown>(data))
}

