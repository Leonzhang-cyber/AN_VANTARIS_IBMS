import request from './request'

export interface ReportsHealth {
  module: string
  status: string
  runtimeMode: string
  provider: string
  sourceSemantics: string
}

export interface ReportsCatalogItem {
  reportId: string
  reportName: string
  groupId: string
  groupName: string
  sourceModules: string[]
  sourceReferenceTypes: string[]
  supportedFilters: string[]
  defaultFilters: Record<string, unknown>
  aggregationLevels: string[]
  exportFormats: string[]
  evidenceLinked: boolean
  scheduleEligible: boolean
  status: string
}

export interface QueryReportPayload {
  reportId: string
  limit?: number
  aggregationLevel?: string
  filters?: Record<string, unknown>
}

export interface QueryReportResult {
  reportId: string
  reportName: string
  queryId: string
  generatedAt: string
  filters: Record<string, unknown>
  columns: string[]
  rows: Record<string, unknown>[]
  summary: Record<string, unknown>
  source: string
  runtimeMode: string
  mockData: boolean
  provider: string
  sourceSemantics: string
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

function normalizeReportsHealth(raw: unknown): ReportsHealth {
  const data = asRecord(raw)
  return {
    module: String(data.module ?? 'reports'),
    status: String(data.status ?? 'unknown'),
    runtimeMode: String(data.runtimeMode ?? 'skeleton'),
    provider: String(data.provider ?? 'local-mock-provider'),
    sourceSemantics: String(data.sourceSemantics ?? 'ibms-neutral'),
  }
}

function normalizeCatalogItem(raw: unknown, reportIdFallback = ''): ReportsCatalogItem {
  const row = asRecord(raw)
  const reportId = String(row.reportId ?? reportIdFallback ?? '')
  const reportName = String(row.reportName ?? (reportId || 'Report'))
  return {
    reportId,
    reportName,
    groupId: String(row.groupId ?? 'general-reports'),
    groupName: String(row.groupName ?? 'General Reports'),
    sourceModules: asStringArray(row.sourceModules),
    sourceReferenceTypes: asStringArray(row.sourceReferenceTypes),
    supportedFilters: asStringArray(row.supportedFilters),
    defaultFilters: asRecord(row.defaultFilters),
    aggregationLevels: asStringArray(row.aggregationLevels),
    exportFormats: asStringArray(row.exportFormats),
    evidenceLinked: Boolean(row.evidenceLinked),
    scheduleEligible: Boolean(row.scheduleEligible),
    status: String(row.status ?? 'runtime-skeleton'),
  }
}

function normalizeQueryResult(raw: unknown): QueryReportResult {
  const data = asRecord(raw)
  return {
    reportId: String(data.reportId ?? ''),
    reportName: String(data.reportName ?? 'Report'),
    queryId: String(data.queryId ?? `query-${Date.now()}`),
    generatedAt: String(data.generatedAt ?? new Date().toISOString()),
    filters: asRecord(data.filters),
    columns: asStringArray(data.columns),
    rows: Array.isArray(data.rows) ? data.rows.map((item) => asRecord(item)) : [],
    summary: asRecord(data.summary),
    source: String(data.source ?? 'local-mock-provider'),
    runtimeMode: String(data.runtimeMode ?? 'skeleton'),
    mockData: Boolean(data.mockData),
    provider: String(data.provider ?? 'local-mock-provider'),
    sourceSemantics: String(data.sourceSemantics ?? 'ibms-neutral'),
  }
}

export async function getReportsHealth(): Promise<ReportsHealth> {
  const { data } = await request.get('/v1/reports/health')
  return normalizeReportsHealth(unwrapData<unknown>(data))
}

export async function getReportsCatalog(): Promise<ReportsCatalogItem[]> {
  const { data } = await request.get('/v1/reports/catalog')
  const payload = unwrapData<{ items?: unknown[] } | unknown[]>(data)
  if (Array.isArray(payload)) {
    return payload.map((item) => normalizeCatalogItem(item))
  }
  return Array.isArray(payload.items) ? payload.items.map((item) => normalizeCatalogItem(item)) : []
}

export async function getReportCatalogItem(reportId: string): Promise<ReportsCatalogItem> {
  const { data } = await request.get(`/v1/reports/catalog/${encodeURIComponent(reportId)}`)
  return normalizeCatalogItem(unwrapData<unknown>(data), reportId)
}

export async function queryReport(payload: QueryReportPayload): Promise<QueryReportResult> {
  const { data } = await request.post('/v1/reports/query', payload)
  return normalizeQueryResult(unwrapData<unknown>(data))
}

