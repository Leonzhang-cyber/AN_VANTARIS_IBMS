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

function unwrapData<T>(body: unknown): T {
  if (typeof body === 'object' && body !== null && 'data' in body) {
    return (body as { data: T }).data
  }
  return body as T
}

export async function getReportsHealth(): Promise<ReportsHealth> {
  const { data } = await request.get('/v1/reports/health')
  return unwrapData<ReportsHealth>(data)
}

export async function getReportsCatalog(): Promise<ReportsCatalogItem[]> {
  const { data } = await request.get('/v1/reports/catalog')
  const payload = unwrapData<{ items?: ReportsCatalogItem[] } | ReportsCatalogItem[]>(data)
  if (Array.isArray(payload)) {
    return payload
  }
  return Array.isArray(payload.items) ? payload.items : []
}

export async function getReportCatalogItem(reportId: string): Promise<ReportsCatalogItem> {
  const { data } = await request.get(`/v1/reports/catalog/${encodeURIComponent(reportId)}`)
  return unwrapData<ReportsCatalogItem>(data)
}

export async function queryReport(payload: QueryReportPayload): Promise<QueryReportResult> {
  const { data } = await request.post('/v1/reports/query', payload)
  return unwrapData<QueryReportResult>(data)
}

