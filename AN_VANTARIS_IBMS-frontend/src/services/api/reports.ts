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
  integrity?: ReportIntegrity
  audit?: ReportAuditMetadata
  traceability?: ReportTraceability
}

export interface ReportIntegrity {
  queryHash: string
  payloadHash: string
  exportHash?: string
  hashAlgorithm: string
  tamperEvidenceMode: string
  certified: boolean
  iec62443Certified: boolean
}

export interface ReportAuditMetadata {
  queryId: string
  auditEventType: string
  generatedAt: string
  reportId: string
  sourceSemantics: string
  provider: string
  mockData: boolean
  auditMode: string
  persisted: boolean
}

export interface ReportTraceability {
  sourceReferences: string[]
  evidenceReferences: string[]
  sourceReferenceTypes: string[]
  evidenceLinked: boolean
}

export interface ReportExportManifest {
  manifestVersion: string
  exportId: string
  queryId: string
  reportId: string
  reportName: string
  generatedAt: string
  exportedAt: string
  sourceSemantics: string
  provider: string
  runtimeMode: string
  mockData: boolean
  queryHash: string
  payloadHash: string
  exportHash: string
  rowCount: number
  columnCount: number
  sourceReferences: string[]
  evidenceReferences: string[]
  sourceReferenceTypes: string[]
  evidenceLinked: boolean
  hashAlgorithm: string
  tamperEvidenceMode: string
  certified: boolean
  iec62443Certified: boolean
  notes: string
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
  const integrityRaw = asRecord(data.integrity)
  const auditRaw = asRecord(data.audit)
  const traceabilityRaw = asRecord(data.traceability)
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
    integrity:
      Object.keys(integrityRaw).length > 0
        ? {
            queryHash: String(integrityRaw.queryHash ?? ''),
            payloadHash: String(integrityRaw.payloadHash ?? ''),
            exportHash:
              integrityRaw.exportHash !== undefined ? String(integrityRaw.exportHash ?? '') : undefined,
            hashAlgorithm: String(integrityRaw.hashAlgorithm ?? 'SHA-256'),
            tamperEvidenceMode: String(integrityRaw.tamperEvidenceMode ?? 'hash-only'),
            certified: Boolean(integrityRaw.certified),
            iec62443Certified: Boolean(integrityRaw.iec62443Certified),
          }
        : undefined,
    audit:
      Object.keys(auditRaw).length > 0
        ? {
            queryId: String(auditRaw.queryId ?? ''),
            auditEventType: String(auditRaw.auditEventType ?? ''),
            generatedAt: String(auditRaw.generatedAt ?? ''),
            reportId: String(auditRaw.reportId ?? ''),
            sourceSemantics: String(auditRaw.sourceSemantics ?? 'ibms-neutral'),
            provider: String(auditRaw.provider ?? 'local-mock-provider'),
            mockData: Boolean(auditRaw.mockData),
            auditMode: String(auditRaw.auditMode ?? 'runtime-skeleton-local'),
            persisted: Boolean(auditRaw.persisted),
          }
        : undefined,
    traceability:
      Object.keys(traceabilityRaw).length > 0
        ? {
            sourceReferences: asStringArray(traceabilityRaw.sourceReferences),
            evidenceReferences: asStringArray(traceabilityRaw.evidenceReferences),
            sourceReferenceTypes: asStringArray(traceabilityRaw.sourceReferenceTypes),
            evidenceLinked: Boolean(traceabilityRaw.evidenceLinked),
          }
        : undefined,
  }
}

function normalizeExportManifest(raw: unknown): ReportExportManifest {
  const data = asRecord(raw)
  return {
    manifestVersion: String(data.manifestVersion ?? 'reports-export-manifest-v1'),
    exportId: String(data.exportId ?? ''),
    queryId: String(data.queryId ?? ''),
    reportId: String(data.reportId ?? ''),
    reportName: String(data.reportName ?? ''),
    generatedAt: String(data.generatedAt ?? ''),
    exportedAt: String(data.exportedAt ?? ''),
    sourceSemantics: String(data.sourceSemantics ?? 'ibms-neutral'),
    provider: String(data.provider ?? 'local-mock-provider'),
    runtimeMode: String(data.runtimeMode ?? 'skeleton'),
    mockData: Boolean(data.mockData),
    queryHash: String(data.queryHash ?? ''),
    payloadHash: String(data.payloadHash ?? ''),
    exportHash: String(data.exportHash ?? ''),
    rowCount: Number(data.rowCount ?? 0),
    columnCount: Number(data.columnCount ?? 0),
    sourceReferences: asStringArray(data.sourceReferences),
    evidenceReferences: asStringArray(data.evidenceReferences),
    sourceReferenceTypes: asStringArray(data.sourceReferenceTypes),
    evidenceLinked: Boolean(data.evidenceLinked),
    hashAlgorithm: String(data.hashAlgorithm ?? 'SHA-256'),
    tamperEvidenceMode: String(data.tamperEvidenceMode ?? 'hash-only-local-manifest'),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
    notes: String(data.notes ?? ''),
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

export interface BuildReportExportManifestPayload {
  reportId: string
  reportName?: string
  queryId: string
  generatedAt: string
  filters?: Record<string, unknown>
  limit?: number
  aggregationLevel?: string
  columns: string[]
  rows: Record<string, unknown>[]
  summary: Record<string, unknown>
  provider?: string
  runtimeMode?: string
  mockData?: boolean
}

export async function buildReportExportManifest(
  payload: BuildReportExportManifestPayload,
): Promise<ReportExportManifest> {
  const { data } = await request.post('/v1/reports/export/manifest', payload)
  const unwrapped = unwrapData<{ manifest?: unknown } | unknown>(data)
  const manifestRaw =
    typeof unwrapped === 'object' && unwrapped !== null && 'manifest' in unwrapped
      ? (unwrapped as { manifest?: unknown }).manifest
      : unwrapped
  return normalizeExportManifest(manifestRaw)
}

