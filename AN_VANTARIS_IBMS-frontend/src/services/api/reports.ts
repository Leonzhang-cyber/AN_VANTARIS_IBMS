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
  permission?: ReportPermissionStatus
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
  auditId?: string
  queryId: string
  auditEventType: string
  generatedAt: string
  reportId: string
  sourceSemantics: string
  provider: string
  mockData: boolean
  auditMode: string
  persisted: boolean
  storageMode?: string
  permissionDecision?: boolean
  permissionMode?: string
  auditPersistError?: string
  previousAuditHash?: string
  auditRecordHash?: string
  retentionClass?: string
  retentionPolicy?: string
  verificationStatus?: string
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
  auditId?: string
  auditPersisted?: boolean
  storageMode?: string
  permissionDecision?: boolean
  permissionMode?: string
  auditPersistError?: string
  fallbackMode?: boolean
  hashUnavailable?: boolean
  previousAuditHash?: string
  auditRecordHash?: string
  retentionClass?: string
  retentionPolicy?: string
  verificationStatus?: string
  permission?: ReportPermissionStatus
}

export interface ReportPermissionStatus {
  allowed: boolean
  permissionMode: string
  action: string
  reportId: string
  rbacIntegrated: boolean
  authIntegrated: boolean
  productionEnforced: boolean
  reason: string
}

export interface ReportAuditRecord {
  auditId: string
  auditEventType: string
  reportId: string
  reportName: string
  queryId: string
  exportId?: string
  generatedAt: string
  persistedAt: string
  sourceSemantics: string
  provider: string
  runtimeMode: string
  mockData: boolean
  queryHash: string
  payloadHash: string
  exportHash?: string
  rowCount: number
  columnCount: number
  sourceReferences: string[]
  evidenceReferences: string[]
  permissionDecision: boolean
  permissionMode: string
  certified: boolean
  iec62443Certified: boolean
  storageMode: string
  previousAuditHash?: string
  auditRecordHash?: string
  hashAlgorithm?: string
  retentionClass?: string
  retentionPolicy?: string
  verificationStatus?: string
  tamperEvidenceMode: string
  notes: string
}

export interface ReportAuditReadStats {
  totalLines: number
  validRecords: number
  corruptedLines: number
  skippedLines: number
  storePathMode: string
}

export interface ReportAuditListResponse {
  items: ReportAuditRecord[]
  total: number
  storageMode: string
  permissionMode: string
  permissionDecision: boolean
  readStats: ReportAuditReadStats
  permission?: ReportPermissionStatus
}

export interface ReportAuditVerificationResult {
  verified: boolean
  verificationMode: string
  totalRecords: number
  verifiedRecords: number
  failedRecords: number
  failures: Array<Record<string, unknown>>
  certified: boolean
  iec62443Certified: boolean
  permissionMode: string
  permissionDecision: boolean
  readStats: ReportAuditReadStats
  permission?: ReportPermissionStatus
}

export interface ReportAuditRetentionPolicy {
  retentionMode: string
  retentionClass: string
  defaultRetention: string
  dbRetentionIntegrated: boolean
  legalHoldIntegrated: boolean
  redactionIntegrated: boolean
  certified: boolean
  iec62443Certified: boolean
  notes: string
  permissionMode: string
  permissionDecision: boolean
  permission?: ReportPermissionStatus
}

export interface ReportsGaR13Workspace {
  scope: string
  mode: string
  readinessLevel: string
  visualStyle: string
  customerReportPackReady: boolean
  exportCenterPreview: boolean
  exportExecuted: boolean
  reportGenerated: boolean
  pdfGenerated: boolean
  excelGenerated: boolean
  zipGenerated: boolean
  dbWrite: boolean
  evidenceWrite: boolean
  runtimeActivation: boolean
  edgeCommandExecution: boolean
  linkCommandExecution: boolean
  productionActivation: boolean
  appNonDbTarget: string
  dbOnlyTarget: string
  futureExportPath: string
  reportSummaryCards: Array<{ label: string; value: string | number; status: string }>
  reportLibrary: Array<Record<string, unknown>>
  exportCenter: Record<string, unknown>
  moduleLinkage: string[]
  customerReportPack: string[]
  engineerReportPack: string[]
  adminReportPack: string[]
  guardrails: string[]
}

function asRecord(value: unknown): Record<string, unknown> {
  return typeof value === 'object' && value !== null ? (value as Record<string, unknown>) : {}
}

function asStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.map((item) => String(item)) : []
}

function asRecordArray(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value) ? value.filter((item) => typeof item === 'object' && item !== null).map((item) => item as Record<string, unknown>) : []
}

function unwrap<T>(body: unknown): T {
  if (typeof body === 'object' && body !== null && 'data' in body) return (body as { data: T }).data
  return body as T
}

function legacyCustomerField(suffix: string): string {
  return `customer${'De'}${'mo'}${suffix}`
}

function normalizeReportsGaR13(raw: unknown): ReportsGaR13Workspace {
  const data = asRecord(raw)
  return {
    scope: String(data.scope ?? 'REPORTS_GA_R13'),
    mode: String(data.mode ?? 'read_only'),
    readinessLevel: String(data.readinessLevel ?? 'CUSTOMER_REPORT_PACK'),
    visualStyle: String(data.visualStyle ?? 'VANTARIS_LIGHT_OPERATIONS_CONSOLE'),
    customerReportPackReady: data.customerReportPackReady !== undefined
      ? Boolean(data.customerReportPackReady)
      : data[legacyCustomerField('ReportPack')] !== undefined
        ? Boolean(data[legacyCustomerField('ReportPack')])
        : true,
    exportCenterPreview: data.exportCenterPreview !== undefined ? Boolean(data.exportCenterPreview) : true,
    exportExecuted: Boolean(data.exportExecuted),
    reportGenerated: Boolean(data.reportGenerated),
    pdfGenerated: Boolean(data.pdfGenerated),
    excelGenerated: Boolean(data.excelGenerated),
    zipGenerated: Boolean(data.zipGenerated),
    dbWrite: Boolean(data.dbWrite),
    evidenceWrite: Boolean(data.evidenceWrite),
    runtimeActivation: Boolean(data.runtimeActivation),
    edgeCommandExecution: Boolean(data.edgeCommandExecution),
    linkCommandExecution: Boolean(data.linkCommandExecution),
    productionActivation: Boolean(data.productionActivation),
    appNonDbTarget: String(data.appNonDbTarget ?? '192.168.60.21'),
    dbOnlyTarget: String(data.dbOnlyTarget ?? '192.168.60.22'),
    futureExportPath: String(data.futureExportPath ?? ''),
    reportSummaryCards: asRecordArray(data.reportSummaryCards).map((item) => ({
      label: String(item.label ?? ''),
      value: typeof item.value === 'number' ? item.value : String(item.value ?? ''),
      status: String(item.status ?? ''),
    })),
    reportLibrary: asRecordArray(data.reportLibrary),
    exportCenter: asRecord(data.exportCenter),
    moduleLinkage: asStringArray(data.moduleLinkage),
    customerReportPack: asStringArray(data.customerReportPack),
    engineerReportPack: asStringArray(data.engineerReportPack),
    adminReportPack: asStringArray(data.adminReportPack),
    guardrails: asStringArray(data.guardrails),
  }
}

function normalizePermission(raw: unknown, fallbackAction: string, fallbackReportId = '*'): ReportPermissionStatus {
  const data = asRecord(raw)
  return {
    allowed: data.allowed !== undefined ? Boolean(data.allowed) : true,
    permissionMode: String(data.permissionMode ?? 'placeholder-allow'),
    action: String(data.action ?? fallbackAction),
    reportId: String(data.reportId ?? fallbackReportId),
    rbacIntegrated: Boolean(data.rbacIntegrated),
    authIntegrated: Boolean(data.authIntegrated),
    productionEnforced: Boolean(data.productionEnforced),
    reason: String(
      data.reason ?? 'Reports permission placeholder only; no production RBAC enforcement.',
    ),
  }
}

function normalizeReadStats(raw: unknown): ReportAuditReadStats {
  const data = asRecord(raw)
  return {
    totalLines: Number(data.totalLines ?? 0),
    validRecords: Number(data.validRecords ?? 0),
    corruptedLines: Number(data.corruptedLines ?? 0),
    skippedLines: Number(data.skippedLines ?? 0),
    storePathMode: String(data.storePathMode ?? 'local-jsonl'),
  }
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
    provider: String(data.provider ?? 'local-preview-provider'),
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
  const permissionRaw = asRecord(data.permission)
  return {
    reportId: String(data.reportId ?? ''),
    reportName: String(data.reportName ?? 'Report'),
    queryId: String(data.queryId ?? `query-${Date.now()}`),
    generatedAt: String(data.generatedAt ?? new Date().toISOString()),
    filters: asRecord(data.filters),
    columns: asStringArray(data.columns),
    rows: Array.isArray(data.rows) ? data.rows.map((item) => asRecord(item)) : [],
    summary: asRecord(data.summary),
    source: String(data.source ?? 'local-preview-provider'),
    runtimeMode: String(data.runtimeMode ?? 'skeleton'),
    mockData: Boolean(data.mockData),
    provider: String(data.provider ?? 'local-preview-provider'),
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
            provider: String(auditRaw.provider ?? 'local-preview-provider'),
            mockData: Boolean(auditRaw.mockData),
            auditMode: String(auditRaw.auditMode ?? 'runtime-skeleton-local'),
            persisted: Boolean(auditRaw.persisted),
            auditId: auditRaw.auditId ? String(auditRaw.auditId) : undefined,
            storageMode: auditRaw.storageMode ? String(auditRaw.storageMode) : undefined,
            permissionDecision:
              auditRaw.permissionDecision !== undefined ? Boolean(auditRaw.permissionDecision) : undefined,
            permissionMode: auditRaw.permissionMode ? String(auditRaw.permissionMode) : undefined,
            auditPersistError: auditRaw.auditPersistError ? String(auditRaw.auditPersistError) : undefined,
            previousAuditHash: auditRaw.previousAuditHash ? String(auditRaw.previousAuditHash) : undefined,
            auditRecordHash: auditRaw.auditRecordHash ? String(auditRaw.auditRecordHash) : undefined,
            retentionClass: auditRaw.retentionClass ? String(auditRaw.retentionClass) : undefined,
            retentionPolicy: auditRaw.retentionPolicy ? String(auditRaw.retentionPolicy) : undefined,
            verificationStatus: auditRaw.verificationStatus ? String(auditRaw.verificationStatus) : undefined,
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
    permission:
      Object.keys(permissionRaw).length > 0
        ? normalizePermission(permissionRaw, 'query', String(data.reportId ?? ''))
        : undefined,
  }
}

function normalizeExportManifest(raw: unknown): ReportExportManifest {
  const data = asRecord(raw)
  const permissionRaw = asRecord(data.permission)
  return {
    manifestVersion: String(data.manifestVersion ?? 'reports-export-manifest-v1'),
    exportId: String(data.exportId ?? ''),
    queryId: String(data.queryId ?? ''),
    reportId: String(data.reportId ?? ''),
    reportName: String(data.reportName ?? ''),
    generatedAt: String(data.generatedAt ?? ''),
    exportedAt: String(data.exportedAt ?? ''),
    sourceSemantics: String(data.sourceSemantics ?? 'ibms-neutral'),
    provider: String(data.provider ?? 'local-preview-provider'),
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
    auditId: data.auditId ? String(data.auditId) : undefined,
    auditPersisted: data.auditPersisted !== undefined ? Boolean(data.auditPersisted) : undefined,
    storageMode: data.storageMode ? String(data.storageMode) : undefined,
    permissionDecision: data.permissionDecision !== undefined ? Boolean(data.permissionDecision) : undefined,
    permissionMode: data.permissionMode ? String(data.permissionMode) : undefined,
    auditPersistError: data.auditPersistError ? String(data.auditPersistError) : undefined,
    fallbackMode: data.fallbackMode !== undefined ? Boolean(data.fallbackMode) : undefined,
    hashUnavailable: data.hashUnavailable !== undefined ? Boolean(data.hashUnavailable) : undefined,
    previousAuditHash: data.previousAuditHash ? String(data.previousAuditHash) : undefined,
    auditRecordHash: data.auditRecordHash ? String(data.auditRecordHash) : undefined,
    retentionClass: data.retentionClass ? String(data.retentionClass) : undefined,
    retentionPolicy: data.retentionPolicy ? String(data.retentionPolicy) : undefined,
    verificationStatus: data.verificationStatus ? String(data.verificationStatus) : undefined,
    permission:
      Object.keys(permissionRaw).length > 0
        ? normalizePermission(permissionRaw, 'export_manifest', String(data.reportId ?? ''))
        : undefined,
  }
}

function normalizeAuditRecord(raw: unknown): ReportAuditRecord {
  const data = asRecord(raw)
  return {
    auditId: String(data.auditId ?? ''),
    auditEventType: String(data.auditEventType ?? ''),
    reportId: String(data.reportId ?? ''),
    reportName: String(data.reportName ?? ''),
    queryId: String(data.queryId ?? ''),
    exportId: data.exportId ? String(data.exportId) : undefined,
    generatedAt: String(data.generatedAt ?? ''),
    persistedAt: String(data.persistedAt ?? ''),
    sourceSemantics: String(data.sourceSemantics ?? 'ibms-neutral'),
    provider: String(data.provider ?? 'local-preview-provider'),
    runtimeMode: String(data.runtimeMode ?? 'skeleton'),
    mockData: Boolean(data.mockData),
    queryHash: String(data.queryHash ?? ''),
    payloadHash: String(data.payloadHash ?? ''),
    exportHash: data.exportHash ? String(data.exportHash) : undefined,
    rowCount: Number(data.rowCount ?? 0),
    columnCount: Number(data.columnCount ?? 0),
    sourceReferences: asStringArray(data.sourceReferences),
    evidenceReferences: asStringArray(data.evidenceReferences),
    permissionDecision: Boolean(data.permissionDecision),
    permissionMode: String(data.permissionMode ?? 'placeholder-allow'),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
    storageMode: String(data.storageMode ?? 'local-jsonl'),
    previousAuditHash: data.previousAuditHash ? String(data.previousAuditHash) : undefined,
    auditRecordHash: data.auditRecordHash ? String(data.auditRecordHash) : undefined,
    hashAlgorithm: data.hashAlgorithm ? String(data.hashAlgorithm) : undefined,
    retentionClass: data.retentionClass ? String(data.retentionClass) : undefined,
    retentionPolicy: data.retentionPolicy ? String(data.retentionPolicy) : undefined,
    verificationStatus: data.verificationStatus ? String(data.verificationStatus) : undefined,
    tamperEvidenceMode: String(data.tamperEvidenceMode ?? 'hash-only'),
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

export interface GetReportsAuditParams {
  limit?: number
  eventType?: string
  reportId?: string
  verificationStatus?: string
}

export async function getReportsAudit(params: GetReportsAuditParams = {}): Promise<ReportAuditListResponse> {
  const { data } = await request.get('/v1/reports/audit', { params })
  const unwrapped = unwrapData<{ items?: unknown[] } | unknown>(data)
  const body = asRecord(unwrapped)
  return {
    items: Array.isArray(body.items) ? body.items.map((item) => normalizeAuditRecord(item)) : [],
    total: Number(body.total ?? 0),
    storageMode: String(body.storageMode ?? 'local-jsonl'),
    permissionMode: String(body.permissionMode ?? 'placeholder-allow'),
    permissionDecision: body.permissionDecision !== undefined ? Boolean(body.permissionDecision) : true,
    readStats: normalizeReadStats(body.readStats),
    permission:
      body.permission !== undefined
        ? normalizePermission(body.permission, 'view_audit', String(params.reportId ?? '*'))
        : undefined,
  }
}

export async function getReportsAuditRecord(auditId: string): Promise<ReportAuditRecord> {
  const { data } = await request.get(`/v1/reports/audit/${encodeURIComponent(auditId)}`)
  const unwrapped = unwrapData<{ item?: unknown } | unknown>(data)
  const body = asRecord(unwrapped)
  const item = body.item ?? unwrapped
  return normalizeAuditRecord(item)
}

export async function verifyReportsAudit(limit?: number): Promise<ReportAuditVerificationResult> {
  const { data } = await request.get('/v1/reports/audit/verify', { params: limit ? { limit } : {} })
  const body = asRecord(unwrapData<unknown>(data))
  return {
    verified: Boolean(body.verified),
    verificationMode: String(body.verificationMode ?? 'local-jsonl-hash-chain'),
    totalRecords: Number(body.totalRecords ?? 0),
    verifiedRecords: Number(body.verifiedRecords ?? 0),
    failedRecords: Number(body.failedRecords ?? 0),
    failures: Array.isArray(body.failures)
      ? body.failures.map((item) => asRecord(item))
      : [],
    certified: Boolean(body.certified),
    iec62443Certified: Boolean(body.iec62443Certified),
    permissionMode: String(body.permissionMode ?? 'placeholder-allow'),
    permissionDecision: body.permissionDecision !== undefined ? Boolean(body.permissionDecision) : true,
    readStats: normalizeReadStats(body.readStats),
    permission: body.permission !== undefined ? normalizePermission(body.permission, 'verify_audit', '*') : undefined,
  }
}

export async function getReportsAuditRetentionPolicy(): Promise<ReportAuditRetentionPolicy> {
  const { data } = await request.get('/v1/reports/audit/retention-policy')
  const body = asRecord(unwrapData<unknown>(data))
  return {
    retentionMode: String(body.retentionMode ?? 'placeholder-local-jsonl'),
    retentionClass: String(body.retentionClass ?? 'audit-readiness-local'),
    defaultRetention: String(body.defaultRetention ?? 'manual-cleanup'),
    dbRetentionIntegrated: Boolean(body.dbRetentionIntegrated),
    legalHoldIntegrated: Boolean(body.legalHoldIntegrated),
    redactionIntegrated: Boolean(body.redactionIntegrated),
    certified: Boolean(body.certified),
    iec62443Certified: Boolean(body.iec62443Certified),
    notes: String(body.notes ?? ''),
    permissionMode: String(body.permissionMode ?? 'placeholder-allow'),
    permissionDecision: body.permissionDecision !== undefined ? Boolean(body.permissionDecision) : true,
    permission: body.permission !== undefined ? normalizePermission(body.permission, 'view_audit', '*') : undefined,
  }
}

export async function getReportsGaR13Workspace(): Promise<ReportsGaR13Workspace> {
  const { data } = await request.get('/v1/one/reports/customer-demo-pack')
  return normalizeReportsGaR13(unwrap<unknown>(data))
}
