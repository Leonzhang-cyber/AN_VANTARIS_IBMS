<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { ApiError } from '@/services/api/errors'
import {
  buildReportExportManifest,
  getReportsAudit,
  getReportsAuditRecord,
  getReportsAuditRetentionPolicy,
  getReportCatalogItem,
  getReportsCatalog,
  getReportsHealth,
  queryReport,
  type ReportAuditRecord,
  type ReportAuditRetentionPolicy,
  type ReportAuditVerificationResult,
  type ReportExportManifest,
  type ReportPermissionStatus,
  type QueryReportPayload,
  type QueryReportResult,
  type ReportsCatalogItem,
  type ReportsHealth,
  verifyReportsAudit,
} from '@/services/api/reports'

interface QueryFilters {
  timeRange: string
  siteId: string
  moduleId: string
  status: string
  severity: string
  category: string
  assetId: string
  deviceId: string
  evidenceReferenceId: string
  aggregationLevel: string
  limit: number
}

type FilterFieldKey =
  | 'timeRange'
  | 'siteId'
  | 'moduleId'
  | 'status'
  | 'severity'
  | 'category'
  | 'assetId'
  | 'deviceId'
  | 'evidenceReferenceId'
  | 'aggregationLevel'
  | 'limit'

const FILTER_FIELD_KEYS: FilterFieldKey[] = [
  'timeRange',
  'siteId',
  'moduleId',
  'status',
  'severity',
  'category',
  'assetId',
  'deviceId',
  'evidenceReferenceId',
  'aggregationLevel',
  'limit',
]

const loadingHealth = ref(false)
const loadingCatalog = ref(false)
const loadingAudit = ref(false)
const querying = ref(false)
const exportingCsv = ref(false)
const queryExecuted = ref(false)
const fallbackMode = ref(false)
const apiUnavailable = ref(false)

const healthError = ref('')
const catalogError = ref('')
const queryError = ref('')
const auditError = ref('')

const selectedReportId = ref('')
const catalogItems = ref<ReportsCatalogItem[]>([])
const auditRecords = ref<ReportAuditRecord[]>([])
const auditStorageMode = ref('local-jsonl')
const auditPermissionMode = ref('placeholder-allow')
const auditReadStats = ref({
  totalLines: 0,
  validRecords: 0,
  corruptedLines: 0,
  skippedLines: 0,
  storePathMode: 'local-jsonl',
})
const verifyingAudit = ref(false)
const auditVerification = ref<ReportAuditVerificationResult | null>(null)
const auditRetentionPolicy = ref<ReportAuditRetentionPolicy | null>(null)
const loadingAuditDetail = ref(false)
const showAuditDetailDrawer = ref(false)
const selectedAuditDetail = ref<ReportAuditRecord | null>(null)

const auditFilters = reactive({
  eventType: '',
  reportId: '',
  limit: 20,
})
const health = ref<ReportsHealth>({
  module: 'reports',
  status: 'unknown',
  runtimeMode: 'skeleton',
  provider: 'local-mock-provider',
  sourceSemantics: 'ibms-neutral',
})

const queryResult = ref<QueryReportResult | null>(null)
const exportManifest = ref<ReportExportManifest | null>(null)
const permissionByAction = ref<Record<string, ReportPermissionStatus>>({})

const filters = reactive<QueryFilters>({
  timeRange: 'last_24h',
  siteId: '',
  moduleId: '',
  status: '',
  severity: '',
  category: '',
  assetId: '',
  deviceId: '',
  evidenceReferenceId: '',
  aggregationLevel: '',
  limit: 20,
})

const fallbackCatalog: ReportsCatalogItem[] = [
  {
    reportId: 'incident-summary',
    reportName: 'Incident Summary Report',
    groupId: 'incident-event-reports',
    groupName: 'Incident & Event Reports',
    sourceModules: ['source-reference', 'evidence-reference', 'module-status'],
    sourceReferenceTypes: ['incident', 'evidence', 'module-status'],
    supportedFilters: [
      'timeRange',
      'siteId',
      'moduleId',
      'status',
      'severity',
      'category',
      'aggregationLevel',
      'limit',
    ],
    defaultFilters: { timeRange: 'last_24h' },
    aggregationLevels: ['raw', 'hourly', 'daily'],
    exportFormats: ['view-only'],
    evidenceLinked: true,
    scheduleEligible: false,
    status: 'runtime-skeleton',
  },
  {
    reportId: 'event-trend',
    reportName: 'Event Trend Report',
    groupId: 'incident-event-reports',
    groupName: 'Incident & Event Reports',
    sourceModules: ['source-reference', 'evidence-reference'],
    sourceReferenceTypes: ['event', 'evidence'],
    supportedFilters: ['timeRange', 'siteId', 'moduleId', 'severity', 'category', 'aggregationLevel', 'limit'],
    defaultFilters: { timeRange: 'last_7d' },
    aggregationLevels: ['hourly', 'daily'],
    exportFormats: ['view-only'],
    evidenceLinked: true,
    scheduleEligible: false,
    status: 'runtime-skeleton',
  },
]

const queryColumns = computed(() => queryResult.value?.columns ?? [])
const queryRows = computed(() => queryResult.value?.rows ?? [])
const canExportCsv = computed(() => !querying.value && !exportingCsv.value && queryRows.value.length > 0)
const queryRowsEmpty = computed(() => queryResult.value !== null && queryRows.value.length === 0)
const hasCatalogItems = computed(() => catalogItems.value.length > 0)
const exportButtonHelperText = computed(() =>
  canExportCsv.value ? 'Exports current table rows as CSV in browser-local mode.' : 'Run a report query before exporting CSV.',
)
const selectedReport = computed(() =>
  catalogItems.value.find((item) => item.reportId === selectedReportId.value) ?? null,
)
const selectedReportSupportedFilters = computed<Set<FilterFieldKey>>(() => {
  const report = selectedReport.value
  if (!report) {
    return new Set<FilterFieldKey>(['limit'])
  }
  const filtersFromCatalog = Array.isArray(report.supportedFilters) ? report.supportedFilters : []
  return new Set(
    filtersFromCatalog.filter((name): name is FilterFieldKey =>
      FILTER_FIELD_KEYS.includes(name as FilterFieldKey),
    ),
  )
})

const activeFilterEntries = computed(() => {
  const payload = buildQueryPayload()
  const entries: Array<{ key: string; value: string }> = [{ key: 'reportId', value: payload.reportId }]
  entries.push({ key: 'sourceSemantics', value: 'ibms-neutral' })
  if (payload.aggregationLevel) {
    entries.push({ key: 'aggregationLevel', value: payload.aggregationLevel })
  }
  if (!payload.filters) {
    return entries
  }
  for (const [key, value] of Object.entries(payload.filters)) {
    entries.push({ key, value: String(value) })
  }
  return entries
})

const permissionGateRows = computed(() => {
  const reportId = selectedReportId.value || '*'
  const fallback = (action: string): ReportPermissionStatus => ({
    allowed: true,
    permissionMode: 'placeholder-allow',
    action,
    reportId,
    rbacIntegrated: false,
    authIntegrated: false,
    productionEnforced: false,
    reason: 'Reports permission placeholder only; no production RBAC enforcement.',
  })
  const actions = ['query', 'export_manifest', 'view_audit', 'verify_audit']
  return actions.map((action) => permissionByAction.value[action] ?? fallback(action))
})

const canExportAuditRecords = computed(() => !loadingAudit.value && auditRecords.value.length > 0)
const auditExportHelperText = computed(() =>
  canExportAuditRecords.value
    ? 'Exports currently loaded audit records from the browser. No backend export job is created.'
    : 'Load audit records before exporting.',
)

function normalizeError(error: unknown, fallback: string): string {
  return error instanceof ApiError ? error.message : fallback
}

function buildFallbackPermission(action: string, reportId: string): ReportPermissionStatus {
  return {
    allowed: true,
    permissionMode: 'placeholder-allow',
    action,
    reportId,
    rbacIntegrated: false,
    authIntegrated: false,
    productionEnforced: false,
    reason: 'Reports permission placeholder only; no production RBAC enforcement.',
  }
}

function updatePermissionState(action: string, value: Partial<ReportPermissionStatus> | undefined): void {
  const reportId = String(value?.reportId ?? selectedReportId.value ?? '*')
  permissionByAction.value[action] = {
    ...buildFallbackPermission(action, reportId),
    ...value,
    action,
    reportId,
  }
}

async function loadAuditTrail(): Promise<void> {
  loadingAudit.value = true
  auditError.value = ''
  try {
    const result = await getReportsAudit({
      limit: auditFilters.limit,
      eventType: auditFilters.eventType || undefined,
      reportId: auditFilters.reportId || undefined,
    })
    auditRecords.value = result.items
    auditStorageMode.value = result.storageMode
    auditPermissionMode.value = result.permissionMode
    auditReadStats.value = result.readStats
    updatePermissionState('view_audit', result.permission)
  } catch (error) {
    auditError.value = normalizeError(error, 'Audit trail is temporarily unavailable.')
  } finally {
    loadingAudit.value = false
  }
}

function sanitizeAuditLimit(value: unknown): number {
  const parsed = Number(value)
  if (!Number.isFinite(parsed)) {
    return 20
  }
  return Math.min(Math.max(Math.trunc(parsed), 1), 200)
}

function refreshAuditTrail(): void {
  auditFilters.limit = sanitizeAuditLimit(auditFilters.limit)
  void loadAuditTrail()
}

async function verifyAuditChainNow(): Promise<void> {
  verifyingAudit.value = true
  try {
    auditVerification.value = await verifyReportsAudit(auditFilters.limit)
    updatePermissionState('verify_audit', auditVerification.value.permission)
    ElMessage.success(auditVerification.value.verified ? 'Audit chain verified.' : 'Audit chain verification found issues.')
    void loadAuditTrail()
  } catch (error) {
    auditError.value = normalizeError(error, 'Audit verification is temporarily unavailable.')
  } finally {
    verifyingAudit.value = false
  }
}

async function loadRetentionPolicy(): Promise<void> {
  try {
    auditRetentionPolicy.value = await getReportsAuditRetentionPolicy()
    updatePermissionState('view_audit', auditRetentionPolicy.value.permission)
  } catch (error) {
    auditError.value = normalizeError(error, 'Retention policy API is temporarily unavailable.')
  }
}

async function openAuditDetail(row: ReportAuditRecord): Promise<void> {
  showAuditDetailDrawer.value = true
  loadingAuditDetail.value = true
  selectedAuditDetail.value = row
  try {
    selectedAuditDetail.value = await getReportsAuditRecord(row.auditId)
  } catch (error) {
    auditError.value = normalizeError(error, 'Failed to load audit detail.')
  } finally {
    loadingAuditDetail.value = false
  }
}

function catalogRowClassName({ row }: { row: ReportsCatalogItem }): string {
  return row.reportId === selectedReportId.value ? 'catalog-row-selected' : ''
}

function isFilterSupported(name: FilterFieldKey): boolean {
  return selectedReportSupportedFilters.value.has(name)
}

function sanitizeLimit(value: unknown): number {
  const parsed = Number(value)
  if (!Number.isFinite(parsed)) {
    return 20
  }
  return Math.min(Math.max(Math.trunc(parsed), 1), 100)
}

function resetFilters(): void {
  filters.timeRange = ''
  filters.siteId = ''
  filters.moduleId = ''
  filters.status = ''
  filters.severity = ''
  filters.category = ''
  filters.assetId = ''
  filters.deviceId = ''
  filters.evidenceReferenceId = ''
  filters.aggregationLevel = ''
  filters.limit = 20
}

function applySelectedReportDefaults(report: ReportsCatalogItem): void {
  resetFilters()
  queryResult.value = null
  exportManifest.value = null
  queryError.value = ''
  queryExecuted.value = false

  const defaults = (report.defaultFilters ?? {}) as Record<string, unknown>
  for (const key of FILTER_FIELD_KEYS) {
    if (!(key in defaults)) {
      continue
    }
    if (key === 'limit') {
      filters.limit = sanitizeLimit(defaults.limit)
      continue
    }
    if (key === 'aggregationLevel') {
      const value = defaults.aggregationLevel
      if (value !== null && value !== undefined) {
        filters.aggregationLevel = String(value).trim()
      }
      continue
    }
    const value = defaults[key]
    if (value !== null && value !== undefined) {
      filters[key] = String(value).trim()
    }
  }

  if (!filters.aggregationLevel && Array.isArray(report.aggregationLevels) && report.aggregationLevels.length > 0) {
    filters.aggregationLevel = report.aggregationLevels[0]
  }

  filters.limit = sanitizeLimit(filters.limit)
}

function buildCleanFilters(): Record<string, unknown> {
  const rawEntries: Array<[FilterFieldKey, unknown]> = [
    ['timeRange', filters.timeRange],
    ['siteId', filters.siteId],
    ['moduleId', filters.moduleId],
    ['status', filters.status],
    ['severity', filters.severity],
    ['category', filters.category],
    ['assetId', filters.assetId],
    ['deviceId', filters.deviceId],
    ['evidenceReferenceId', filters.evidenceReferenceId],
  ]
  const clean: Record<string, unknown> = {}
  for (const [key, value] of rawEntries) {
    if (!isFilterSupported(key)) {
      continue
    }
    if (value === null || value === undefined) {
      continue
    }
    const normalized = String(value).trim()
    if (!normalized) {
      continue
    }
    clean[key] = normalized
  }
  return clean
}

function buildQueryPayload(): QueryReportPayload {
  const payload: QueryReportPayload = {
    reportId: selectedReportId.value,
    limit: sanitizeLimit(filters.limit),
  }
  const cleanFilters = buildCleanFilters()
  if (Object.keys(cleanFilters).length > 0) {
    payload.filters = cleanFilters
  }
  if (isFilterSupported('aggregationLevel')) {
    const value = String(filters.aggregationLevel ?? '').trim()
    if (value) {
      payload.aggregationLevel = value
    }
  }
  return payload
}

async function loadHealth(): Promise<void> {
  loadingHealth.value = true
  healthError.value = ''
  try {
    health.value = await getReportsHealth()
  } catch (error) {
    apiUnavailable.value = true
    fallbackMode.value = true
    healthError.value = normalizeError(error, 'Reports health API unavailable.')
    health.value = {
      module: 'reports',
      status: 'api-unavailable',
      runtimeMode: 'skeleton',
      provider: 'local-mock-provider',
      sourceSemantics: 'ibms-neutral',
    }
  } finally {
    loadingHealth.value = false
  }
}

async function loadCatalog(): Promise<void> {
  loadingCatalog.value = true
  catalogError.value = ''
  try {
    catalogItems.value = await getReportsCatalog()
    if (catalogItems.value.length === 0) {
      catalogItems.value = [...fallbackCatalog]
      fallbackMode.value = true
    }
  } catch (error) {
    apiUnavailable.value = true
    fallbackMode.value = true
    catalogError.value = normalizeError(error, 'Reports catalog API unavailable.')
    catalogItems.value = [...fallbackCatalog]
  } finally {
    if (!selectedReportId.value && catalogItems.value.length > 0) {
      selectedReportId.value = catalogItems.value[0].reportId
      applySelectedReportDefaults(catalogItems.value[0])
    }
    loadingCatalog.value = false
  }
}

async function selectReport(report: ReportsCatalogItem): Promise<void> {
  selectedReportId.value = report.reportId
  queryError.value = ''
  queryResult.value = null
  if (fallbackMode.value) {
    applySelectedReportDefaults(report)
    return
  }
  try {
    const detail = await getReportCatalogItem(report.reportId)
    selectedReportId.value = detail.reportId
    applySelectedReportDefaults(detail)
  } catch (error) {
    const message = normalizeError(error, 'Failed to load report catalog detail.')
    queryError.value = message
    ElMessage.warning(message)
    applySelectedReportDefaults(report)
  }
}

function buildLocalFallbackQueryResult(payload: QueryReportPayload): QueryReportResult {
  const limit = sanitizeLimit(payload.limit)
  const cleanFilters = payload.filters ?? {}
  const rows = Array.from({ length: limit }, (_, index) => ({
    recordId: `${payload.reportId}-fallback-${index + 1}`,
    sourceType: 'reference',
    sourceReferenceId: `fallback-ref-${index + 1}`,
    sourceModuleId: String(cleanFilters.moduleId ?? 'source-reference'),
    status: String(cleanFilters.status ?? 'open'),
    severity: String(cleanFilters.severity ?? 'medium'),
    category: String(cleanFilters.category ?? 'general'),
    timestamp: new Date().toISOString(),
    evidenceReferenceId: `fallback-ev-${index + 1}`,
    summary: `Fallback mock row ${index + 1} for ${payload.reportId}`,
    count: index + 1,
    trendValue: Number(((index + 1) * 1.2).toFixed(2)),
    aggregationLevel: String(payload.aggregationLevel ?? 'raw'),
  }))
  const columns = Object.keys(rows[0] ?? {})
  return {
    reportId: payload.reportId,
    reportName:
      catalogItems.value.find((item) => item.reportId === payload.reportId)?.reportName ??
      'Fallback Report',
    queryId: `fallback-${Date.now()}`,
    generatedAt: new Date().toISOString(),
    filters: cleanFilters,
    columns,
    rows,
    summary: {
      rowCount: rows.length,
      fallbackMode: true,
      sourceSemantics: 'ibms-neutral',
      mockData: true,
    },
    source: 'local-fallback-provider',
    runtimeMode: 'skeleton',
    mockData: true,
    provider: 'local-mock-provider',
    sourceSemantics: 'ibms-neutral',
  }
}

async function runQuery(): Promise<void> {
  queryError.value = ''
  exportManifest.value = null
  if (!selectedReportId.value) {
    queryError.value = 'Please select a report first.'
    return
  }

  querying.value = true
  queryExecuted.value = true
  const payload = buildQueryPayload()
  filters.limit = sanitizeLimit(payload.limit)
  try {
    if (fallbackMode.value) {
      queryResult.value = buildLocalFallbackQueryResult(payload)
      updatePermissionState('query', buildFallbackPermission('query', payload.reportId))
      refreshAuditTrail()
      return
    }
    queryResult.value = await queryReport(payload)
    updatePermissionState('query', queryResult.value.permission)
    refreshAuditTrail()
  } catch (error) {
    const message = normalizeError(error, 'Failed to query report.')
    if (apiUnavailable.value) {
      queryResult.value = buildLocalFallbackQueryResult(payload)
      queryError.value = `${message} Switched to fallback mock mode.`
      refreshAuditTrail()
    } else {
      queryError.value = message
      queryResult.value = null
    }
  } finally {
    querying.value = false
  }
}

function renderCellValue(value: unknown): string {
  if (value === null || value === undefined) {
    return '-'
  }
  if (typeof value === 'object') {
    return JSON.stringify(value)
  }
  return String(value)
}

function escapeCsvValue(value: unknown): string {
  if (value === null || value === undefined) {
    return ''
  }
  const text = typeof value === 'object' ? JSON.stringify(value) : String(value)
  return `"${text.replace(/"/g, '""')}"`
}

interface CsvColumnInfo {
  key: string
  header: string
}

function normalizeCsvColumns(columns: unknown[], rows: Record<string, unknown>[]): CsvColumnInfo[] {
  const normalized = columns
    .map((column) => {
      if (typeof column === 'string') {
        return { key: column, header: column }
      }
      if (typeof column === 'object' && column !== null) {
        const data = column as Record<string, unknown>
        const keyCandidate = data.key ?? data.field ?? data.name ?? data.title ?? data.label
        const headerCandidate = data.label ?? data.title ?? data.name ?? data.key ?? data.field
        if (typeof keyCandidate === 'string' && keyCandidate.trim()) {
          return {
            key: keyCandidate.trim(),
            header:
              typeof headerCandidate === 'string' && headerCandidate.trim()
                ? headerCandidate.trim()
                : keyCandidate.trim(),
          }
        }
      }
      return null
    })
    .filter((item): item is CsvColumnInfo => Boolean(item))

  if (normalized.length > 0) {
    return normalized
  }

  const firstRow = rows[0] ?? {}
  return Object.keys(firstRow).map((key) => ({ key, header: key }))
}

function buildCsv(columns: unknown[], rows: Record<string, unknown>[]): string {
  const csvColumns = normalizeCsvColumns(columns, rows)
  if (csvColumns.length === 0) {
    return ''
  }

  const headerLine = csvColumns.map((column) => escapeCsvValue(column.header)).join(',')
  const dataLines = rows.map((row) =>
    csvColumns.map((column) => escapeCsvValue(row[column.key])).join(','),
  )

  return [headerLine, ...dataLines].join('\r\n')
}

function formatTimestampForFilename(date: Date): string {
  const pad2 = (value: number) => String(value).padStart(2, '0')
  const yyyy = date.getFullYear()
  const mm = pad2(date.getMonth() + 1)
  const dd = pad2(date.getDate())
  const hh = pad2(date.getHours())
  const mi = pad2(date.getMinutes())
  const ss = pad2(date.getSeconds())
  return `${yyyy}${mm}${dd}-${hh}${mi}${ss}`
}

function downloadCsv(filename: string, csvContent: string): void {
  const blob = new Blob(['\uFEFF', csvContent], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  document.body.appendChild(anchor)
  anchor.click()
  document.body.removeChild(anchor)
  URL.revokeObjectURL(url)
}

function buildCsvFilename(reportId: string): string {
  const timestamp = formatTimestampForFilename(new Date())
  const safeReportId = reportId.replace(/[^a-zA-Z0-9_-]/g, '-')
  return `reports-${safeReportId}-${timestamp}.csv`
}

function buildManifestFilename(reportId: string): string {
  const timestamp = formatTimestampForFilename(new Date())
  const safeReportId = reportId.replace(/[^a-zA-Z0-9_-]/g, '-')
  return `reports-${safeReportId}-${timestamp}.manifest.json`
}

function canonicalJson(value: unknown): string {
  const normalize = (input: unknown): unknown => {
    if (Array.isArray(input)) {
      return input.map((item) => normalize(item))
    }
    if (input && typeof input === 'object') {
      return Object.keys(input as Record<string, unknown>)
        .sort()
        .reduce<Record<string, unknown>>((acc, key) => {
          acc[key] = normalize((input as Record<string, unknown>)[key])
          return acc
        }, {})
    }
    return input
  }
  return JSON.stringify(normalize(value))
}

async function buildLocalHash(input: unknown): Promise<{ hash: string; hashUnavailable: boolean }> {
  const text = canonicalJson(input)
  const hasWebCrypto = typeof globalThis.crypto !== 'undefined' && globalThis.crypto.subtle
  if (!hasWebCrypto) {
    return { hash: `hash-unavailable-${text.length}`, hashUnavailable: true }
  }
  try {
    const encoded = new TextEncoder().encode(text)
    const digest = await globalThis.crypto.subtle.digest('SHA-256', encoded)
    const bytes = Array.from(new Uint8Array(digest))
    const hash = bytes.map((b) => b.toString(16).padStart(2, '0')).join('')
    return { hash, hashUnavailable: false }
  } catch {
    return { hash: `hash-unavailable-${text.length}`, hashUnavailable: true }
  }
}

function downloadJson(filename: string, data: unknown): void {
  const json = `${JSON.stringify(data, null, 2)}\n`
  const blob = new Blob([json], { type: 'application/json;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  document.body.appendChild(anchor)
  anchor.click()
  document.body.removeChild(anchor)
  URL.revokeObjectURL(url)
}

function buildAuditExportFilename(extension: 'json' | 'csv'): string {
  const timestamp = formatTimestampForFilename(new Date())
  return `reports-audit-records-${timestamp}.${extension}`
}

function buildAuditCsv(): string {
  const columns = [
    'auditId',
    'auditEventType',
    'reportId',
    'reportName',
    'queryId',
    'exportId',
    'generatedAt',
    'persistedAt',
    'permissionMode',
    'allowed',
    'storageMode',
    'retentionClass',
    'verificationStatus',
    'queryHash',
    'payloadHash',
    'exportHash',
    'previousAuditHash',
    'auditRecordHash',
    'certified',
    'iec62443Certified',
  ]
  const rows = auditRecords.value.map((record) => ({
    auditId: record.auditId,
    auditEventType: record.auditEventType,
    reportId: record.reportId,
    reportName: record.reportName,
    queryId: record.queryId,
    exportId: record.exportId ?? '',
    generatedAt: record.generatedAt,
    persistedAt: record.persistedAt,
    permissionMode: record.permissionMode,
    allowed: record.permissionDecision,
    storageMode: record.storageMode,
    retentionClass: record.retentionClass ?? '',
    verificationStatus: record.verificationStatus ?? '',
    queryHash: record.queryHash,
    payloadHash: record.payloadHash,
    exportHash: record.exportHash ?? '',
    previousAuditHash: record.previousAuditHash ?? '',
    auditRecordHash: record.auditRecordHash ?? '',
    certified: record.certified,
    iec62443Certified: record.iec62443Certified,
  }))
  return buildCsv(columns, rows)
}

function exportCurrentAuditJson(): void {
  if (!canExportAuditRecords.value) {
    return
  }
  try {
    const payload = {
      exportType: 'reports-audit-records-json',
      exportedAt: new Date().toISOString(),
      sourceSemantics: 'ibms-neutral',
      storageMode: 'browser-local',
      certified: false,
      iec62443Certified: false,
      filters: {
        eventType: auditFilters.eventType,
        reportId: auditFilters.reportId,
        limit: auditFilters.limit,
      },
      readStats: auditReadStats.value,
      verification: auditVerification.value,
      retentionPolicy: auditRetentionPolicy.value,
      records: auditRecords.value,
    }
    downloadJson(buildAuditExportFilename('json'), payload)
    ElMessage.success('Audit JSON exported.')
  } catch {
    ElMessage.error('Audit JSON export failed.')
  }
}

function exportCurrentAuditCsv(): void {
  if (!canExportAuditRecords.value) {
    return
  }
  try {
    const csv = buildAuditCsv()
    if (!csv) {
      ElMessage.error('No audit records to export.')
      return
    }
    downloadCsv(buildAuditExportFilename('csv'), csv)
    ElMessage.success('Audit CSV exported.')
  } catch {
    ElMessage.error('Audit CSV export failed.')
  }
}

async function buildLocalExportManifest(
  result: QueryReportResult,
  payload: QueryReportPayload,
): Promise<ReportExportManifest> {
  const queryHashResult = await buildLocalHash({
    reportId: result.reportId,
    filters: payload.filters ?? {},
    limit: payload.limit ?? result.rows.length,
    aggregationLevel: payload.aggregationLevel ?? '',
  })
  const payloadHashResult = await buildLocalHash({
    columns: result.columns,
    rows: result.rows,
    summary: result.summary,
  })

  const sourceReferences = result.rows
    .map((row) => row.sourceReferenceId)
    .filter((value): value is string => typeof value === 'string' && value.trim().length > 0)
  const evidenceReferences = result.rows
    .map((row) => row.evidenceReferenceId)
    .filter((value): value is string => typeof value === 'string' && value.trim().length > 0)

  const seed = {
    exportId: `frontend-export-${Date.now()}`,
    queryId: result.queryId,
    reportId: result.reportId,
    reportName: result.reportName,
    generatedAt: result.generatedAt,
    exportedAt: new Date().toISOString(),
    sourceSemantics: 'ibms-neutral',
    provider: 'frontend-local-manifest',
    runtimeMode: result.runtimeMode,
    mockData: result.mockData,
    queryHash: queryHashResult.hash,
    payloadHash: payloadHashResult.hash,
    rowCount: result.rows.length,
    columnCount: result.columns.length,
    sourceReferences: Array.from(new Set(sourceReferences)).sort(),
    evidenceReferences: Array.from(new Set(evidenceReferences)).sort(),
    sourceReferenceTypes: result.traceability?.sourceReferenceTypes ?? [],
    evidenceLinked: Boolean(result.traceability?.evidenceLinked),
    hashAlgorithm: 'SHA-256',
    tamperEvidenceMode: 'hash-only-local-fallback',
    certified: false,
    iec62443Certified: false,
    fallbackMode: true,
    hashUnavailable: queryHashResult.hashUnavailable || payloadHashResult.hashUnavailable,
    notes: 'Hash-only local manifest for audit readiness; no formal certification claim.',
  }
  const exportHashResult = await buildLocalHash(seed)
  return {
    manifestVersion: 'reports-export-manifest-v1',
    exportId: seed.exportId,
    queryId: seed.queryId,
    reportId: seed.reportId,
    reportName: seed.reportName,
    generatedAt: seed.generatedAt,
    exportedAt: seed.exportedAt,
    sourceSemantics: seed.sourceSemantics,
    provider: seed.provider,
    runtimeMode: seed.runtimeMode,
    mockData: seed.mockData,
    queryHash: seed.queryHash,
    payloadHash: seed.payloadHash,
    exportHash: exportHashResult.hash,
    rowCount: seed.rowCount,
    columnCount: seed.columnCount,
    sourceReferences: seed.sourceReferences,
    evidenceReferences: seed.evidenceReferences,
    sourceReferenceTypes: seed.sourceReferenceTypes,
    evidenceLinked: seed.evidenceLinked,
    hashAlgorithm: seed.hashAlgorithm,
    tamperEvidenceMode: seed.tamperEvidenceMode,
    certified: seed.certified,
    iec62443Certified: seed.iec62443Certified,
    notes: seed.notes,
  }
}

async function exportCurrentResultCsv(): Promise<void> {
  if (!queryResult.value || !canExportCsv.value) {
    return
  }

  exportingCsv.value = true
  const result = queryResult.value
  const reportId = result.reportId || selectedReportId.value || 'report'
  const queryPayload = buildQueryPayload()
  try {
    const csv = buildCsv(result.columns as unknown[], result.rows)
    if (!csv) {
      ElMessage.error('No exportable data in current result.')
      return
    }
    downloadCsv(buildCsvFilename(reportId), csv)

    let manifest: ReportExportManifest
    try {
      manifest = await buildReportExportManifest({
        reportId,
        reportName: result.reportName,
        queryId: result.queryId,
        generatedAt: result.generatedAt,
        filters: result.filters,
        limit: queryPayload.limit,
        aggregationLevel: queryPayload.aggregationLevel,
        columns: result.columns,
        rows: result.rows,
        summary: result.summary,
        provider: result.provider,
        runtimeMode: result.runtimeMode,
        mockData: result.mockData,
      })
    } catch {
      manifest = await buildLocalExportManifest(result, queryPayload)
    }

    exportManifest.value = manifest
    updatePermissionState(
      'export_manifest',
      manifest.permission ?? buildFallbackPermission('export_manifest', reportId),
    )
    downloadJson(buildManifestFilename(reportId), manifest)
    refreshAuditTrail()
    ElMessage.success('CSV and manifest exported.')
  } catch {
    ElMessage.error('CSV or manifest export failed.')
  } finally {
    exportingCsv.value = false
  }
}

onMounted(() => {
  void loadHealth()
  void loadCatalog()
  void loadAuditTrail()
  void loadRetentionPolicy()
})
</script>

<template>
  <div class="reports-page">
    <el-card shadow="never" class="page-card page-hero block-space">
      <div class="page-header">
        <div>
          <h1>Reports / 报表工作台</h1>
          <p>IBMS-neutral reporting workspace for runtime skeleton queries.</p>
        </div>
        <el-space wrap>
          <el-tag type="info">runtimeMode: {{ health.runtimeMode }}</el-tag>
          <el-tag type="success">provider: {{ health.provider }}</el-tag>
          <el-tag>sourceSemantics: {{ health.sourceSemantics }}</el-tag>
        </el-space>
      </div>
    </el-card>

    <el-alert
      v-if="apiUnavailable"
      type="warning"
      show-icon
      :closable="false"
      title="API unavailable"
      description="Using local fallback mode for catalog and query preview."
      class="block-space"
    />

    <el-alert
      v-if="fallbackMode"
      type="info"
      show-icon
      :closable="false"
      title="fallbackMode enabled"
      description="sourceSemantics: ibms-neutral, runtimeMode: skeleton, provider: local-mock-provider"
      class="block-space"
    />

    <el-card shadow="never" class="block-space">
      <template #header>
        <div class="section-title">Health</div>
      </template>
      <el-skeleton v-if="loadingHealth" :rows="2" animated />
      <template v-else>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="status">{{ health.status }}</el-descriptions-item>
          <el-descriptions-item label="runtimeMode">{{ health.runtimeMode }}</el-descriptions-item>
          <el-descriptions-item label="provider">{{ health.provider }}</el-descriptions-item>
          <el-descriptions-item label="sourceSemantics">{{ health.sourceSemantics }}</el-descriptions-item>
          <el-descriptions-item label="fallbackMode">
            <el-tag :type="fallbackMode ? 'warning' : 'success'" size="small">{{ fallbackMode }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </template>
      <el-alert
        v-if="healthError"
        type="error"
        show-icon
        :closable="false"
        :title="healthError"
        class="block-space top-space"
      />
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header>
        <div class="section-title">Permission Gate</div>
      </template>
      <el-alert
        type="info"
        show-icon
        :closable="false"
        title="Permission display is a placeholder. Production auth/RBAC is not integrated in this stage."
        class="block-space"
      />
      <el-table :data="permissionGateRows" row-key="action" empty-text="No permission records">
        <el-table-column prop="action" label="action" min-width="140" />
        <el-table-column prop="permissionMode" label="permissionMode" min-width="170" />
        <el-table-column prop="allowed" label="allowed" min-width="90" />
        <el-table-column prop="reportId" label="reportId" min-width="130" />
        <el-table-column prop="rbacIntegrated" label="rbacIntegrated" min-width="130" />
        <el-table-column prop="authIntegrated" label="authIntegrated" min-width="130" />
        <el-table-column prop="reason" label="reason" min-width="340" show-overflow-tooltip />
      </el-table>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header>
        <div class="section-title">Report Catalog</div>
      </template>
      <el-skeleton v-if="loadingCatalog" :rows="4" animated />
      <template v-else>
        <el-empty v-if="!hasCatalogItems" description="No report catalog available." />
        <el-table
          v-else
          :data="catalogItems"
          row-key="reportId"
          :row-class-name="catalogRowClassName"
          empty-text="No reports available"
        >
          <el-table-column prop="reportName" label="Report Name" min-width="200" />
          <el-table-column prop="groupName" label="Group" min-width="180" />
          <el-table-column label="Source Modules" min-width="280">
            <template #default="{ row }">
              <el-space wrap>
                <el-tag v-for="moduleName in row.sourceModules" :key="moduleName" size="small" type="info">
                  {{ moduleName }}
                </el-tag>
              </el-space>
            </template>
          </el-table-column>
          <el-table-column label="Evidence Linked" width="130">
            <template #default="{ row }">
              <el-tag :type="row.evidenceLinked ? 'success' : 'info'" size="small">
                {{ row.evidenceLinked }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Schedule Eligible" width="140">
            <template #default="{ row }">
              <el-tag :type="row.scheduleEligible ? 'warning' : 'success'" size="small">
                {{ row.scheduleEligible }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="Status" min-width="140" />
          <el-table-column label="Action" width="120" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" :disabled="querying" @click="selectReport(row)">
                {{ selectedReportId === row.reportId ? 'Selected' : 'Select' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </template>
      <el-alert
        v-if="catalogError"
        type="error"
        show-icon
        :closable="false"
        :title="catalogError"
        class="block-space top-space"
      />
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header>
        <div class="section-title">Selected Report</div>
      </template>
      <el-empty
        v-if="!selectedReport"
        description="Select a report from catalog to view summary and filter options."
      />
      <el-descriptions v-else :column="2" border>
        <el-descriptions-item label="reportName">{{ selectedReport.reportName }}</el-descriptions-item>
        <el-descriptions-item label="groupName">{{ selectedReport.groupName }}</el-descriptions-item>
        <el-descriptions-item label="sourceReferenceTypes">
          <el-space wrap>
            <el-tag v-for="item in selectedReport.sourceReferenceTypes" :key="item" size="small">{{ item }}</el-tag>
          </el-space>
        </el-descriptions-item>
        <el-descriptions-item label="supportedFilters">
          <el-space wrap>
            <el-tag v-for="item in selectedReport.supportedFilters" :key="item" size="small" type="info">
              {{ item }}
            </el-tag>
          </el-space>
        </el-descriptions-item>
        <el-descriptions-item label="aggregationLevels">
          <el-space wrap>
            <el-tag v-for="item in selectedReport.aggregationLevels" :key="item" size="small" type="warning">
              {{ item }}
            </el-tag>
          </el-space>
        </el-descriptions-item>
        <el-descriptions-item label="exportFormats">
          <el-space wrap>
            <el-tag v-for="item in selectedReport.exportFormats" :key="item" size="small">{{ item }}</el-tag>
          </el-space>
        </el-descriptions-item>
        <el-descriptions-item label="evidenceLinked">{{ selectedReport.evidenceLinked }}</el-descriptions-item>
        <el-descriptions-item label="scheduleEligible">{{ selectedReport.scheduleEligible }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header>
        <div class="section-title">Query Filters</div>
      </template>
      <el-alert
        v-if="!selectedReport"
        type="info"
        show-icon
        :closable="false"
        title="No selected report"
        description="Select a report before configuring filters."
        class="block-space"
      />
      <template v-else>
        <el-form label-position="top">
          <el-row :gutter="12">
            <el-col :xs="24" :sm="12" :md="6">
              <el-form-item label="Selected Report">
                <el-input :model-value="selectedReportId" disabled />
              </el-form-item>
            </el-col>
            <el-col v-if="isFilterSupported('timeRange')" :xs="24" :sm="12" :md="6">
              <el-form-item label="timeRange">
                <el-input v-model="filters.timeRange" placeholder="last_24h" />
              </el-form-item>
            </el-col>
            <el-col v-if="isFilterSupported('siteId')" :xs="24" :sm="12" :md="6">
              <el-form-item label="siteId">
                <el-input v-model="filters.siteId" placeholder="site-001" />
              </el-form-item>
            </el-col>
            <el-col v-if="isFilterSupported('moduleId')" :xs="24" :sm="12" :md="6">
              <el-form-item label="moduleId">
                <el-input v-model="filters.moduleId" placeholder="source-reference" />
              </el-form-item>
            </el-col>
            <el-col v-if="isFilterSupported('status')" :xs="24" :sm="12" :md="6">
              <el-form-item label="status">
                <el-input v-model="filters.status" placeholder="open" />
              </el-form-item>
            </el-col>
            <el-col v-if="isFilterSupported('severity')" :xs="24" :sm="12" :md="6">
              <el-form-item label="severity">
                <el-input v-model="filters.severity" placeholder="medium" />
              </el-form-item>
            </el-col>
            <el-col v-if="isFilterSupported('category')" :xs="24" :sm="12" :md="6">
              <el-form-item label="category">
                <el-input v-model="filters.category" placeholder="general" />
              </el-form-item>
            </el-col>
            <el-col v-if="isFilterSupported('assetId')" :xs="24" :sm="12" :md="6">
              <el-form-item label="assetId">
                <el-input v-model="filters.assetId" placeholder="asset-001" />
              </el-form-item>
            </el-col>
            <el-col v-if="isFilterSupported('deviceId')" :xs="24" :sm="12" :md="6">
              <el-form-item label="deviceId">
                <el-input v-model="filters.deviceId" placeholder="device-001" />
              </el-form-item>
            </el-col>
            <el-col v-if="isFilterSupported('evidenceReferenceId')" :xs="24" :sm="12" :md="6">
              <el-form-item label="evidenceReferenceId">
                <el-input v-model="filters.evidenceReferenceId" placeholder="ev-0001" />
              </el-form-item>
            </el-col>
            <el-col v-if="isFilterSupported('aggregationLevel')" :xs="24" :sm="12" :md="6">
              <el-form-item label="aggregationLevel">
                <el-select
                  v-model="filters.aggregationLevel"
                  placeholder="Select aggregation level"
                  clearable
                  filterable
                >
                  <el-option
                    v-for="level in selectedReport?.aggregationLevels ?? []"
                    :key="level"
                    :label="level"
                    :value="level"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col v-if="isFilterSupported('limit')" :xs="24" :sm="12" :md="6">
              <el-form-item label="limit">
                <el-input-number v-model="filters.limit" :min="1" :max="100" :step="1" controls-position="right" />
                <div class="field-helper-text">Allowed range: 1-100</div>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>

        <el-card shadow="never" class="block-space">
          <template #header>Active Filters</template>
          <el-empty
            v-if="activeFilterEntries.length <= 2"
            description="No active filter values yet. Defaults will apply on query."
          />
          <el-space v-else wrap>
            <el-tag v-for="entry in activeFilterEntries" :key="`${entry.key}:${entry.value}`" size="small">
              {{ entry.key }}: {{ entry.value }}
            </el-tag>
          </el-space>
        </el-card>
      </template>

      <el-button type="primary" :loading="querying" :disabled="!selectedReportId" @click="runQuery">
        Run Query
      </el-button>
    </el-card>

    <el-card shadow="never">
      <template #header>
        <div class="section-title">Query Result</div>
      </template>

      <el-alert
        v-if="queryError"
        type="error"
        show-icon
        :closable="false"
        :title="queryError"
        class="block-space"
      />

      <el-skeleton v-if="querying" :rows="4" animated />
      <el-empty
        v-else-if="!queryExecuted"
        description="Run a report query to preview result rows and metadata."
      />
      <el-empty
        v-else-if="queryRowsEmpty"
        description="Query completed but returned no rows for current filters."
      />

      <template v-else-if="queryResult">
        <el-descriptions :column="2" border class="block-space">
          <el-descriptions-item label="queryId">{{ queryResult.queryId }}</el-descriptions-item>
          <el-descriptions-item label="generatedAt">{{ queryResult.generatedAt }}</el-descriptions-item>
          <el-descriptions-item label="provider">
            <el-tag>{{ queryResult.provider }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="mockData">
            <el-tag :type="queryResult.mockData ? 'warning' : 'success'">{{ queryResult.mockData }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="runtimeMode">{{ queryResult.runtimeMode }}</el-descriptions-item>
          <el-descriptions-item label="sourceSemantics">{{ queryResult.sourceSemantics }}</el-descriptions-item>
          <el-descriptions-item label="queryHash">
            {{ queryResult.integrity?.queryHash || 'not-available' }}
          </el-descriptions-item>
          <el-descriptions-item label="payloadHash">
            {{ queryResult.integrity?.payloadHash || 'not-available' }}
          </el-descriptions-item>
          <el-descriptions-item label="exportHash">
            {{ exportManifest?.exportHash || queryResult.integrity?.exportHash || 'not-exported' }}
          </el-descriptions-item>
          <el-descriptions-item label="tamperEvidenceMode">
            {{ exportManifest?.tamperEvidenceMode || queryResult.integrity?.tamperEvidenceMode || 'hash-only' }}
          </el-descriptions-item>
          <el-descriptions-item label="certified">
            {{ exportManifest?.certified ?? queryResult.integrity?.certified ?? false }}
          </el-descriptions-item>
          <el-descriptions-item label="IEC62443 Readiness Flag">
            {{ exportManifest?.iec62443Certified ?? queryResult.integrity?.iec62443Certified ?? false }}
          </el-descriptions-item>
          <el-descriptions-item label="exportMode">browser-local</el-descriptions-item>
          <el-descriptions-item label="exportScope">current-result</el-descriptions-item>
          <el-descriptions-item label="exportFormat">csv</el-descriptions-item>
        </el-descriptions>

        <el-alert
          type="info"
          show-icon
          :closable="false"
          title="Hash-only manifest supports audit readiness."
          description="This is not a formal immutable proof chain and not certification proof."
          class="block-space"
        />

        <el-card shadow="never" class="block-space">
          <template #header>Traceability</template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="sourceReferences">
              {{ queryResult.traceability?.sourceReferences?.length ?? 0 }}
            </el-descriptions-item>
            <el-descriptions-item label="evidenceReferences">
              {{ queryResult.traceability?.evidenceReferences?.length ?? 0 }}
            </el-descriptions-item>
            <el-descriptions-item label="sourceReferenceTypes">
              <el-space wrap>
                <el-tag
                  v-for="typeName in queryResult.traceability?.sourceReferenceTypes ?? []"
                  :key="typeName"
                  size="small"
                >
                  {{ typeName }}
                </el-tag>
              </el-space>
            </el-descriptions-item>
            <el-descriptions-item label="evidenceLinked">
              {{ queryResult.traceability?.evidenceLinked ?? false }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <div class="export-row block-space">
          <el-tooltip :disabled="canExportCsv" content="Run a report query before exporting CSV." placement="top">
            <el-button
              type="success"
              plain
              :loading="exportingCsv"
              :disabled="!canExportCsv"
              @click="exportCurrentResultCsv"
            >
              Export CSV
            </el-button>
          </el-tooltip>
          <span class="field-helper-text">{{ exportButtonHelperText }}</span>
        </div>

        <el-card shadow="never" class="block-space">
          <template #header>Summary</template>
          <pre class="summary-block">{{ JSON.stringify(queryResult.summary, null, 2) }}</pre>
        </el-card>

        <el-table :data="queryRows" row-key="recordId" empty-text="No rows returned">
          <el-table-column
            v-for="column in queryColumns"
            :key="column"
            :prop="column"
            :label="column"
            min-width="140"
            show-overflow-tooltip
          >
            <template #default="{ row }">
              {{ renderCellValue(row[column]) }}
            </template>
          </el-table-column>
        </el-table>
      </template>
    </el-card>

    <el-card shadow="never" class="block-space top-space">
      <template #header>
        <div class="section-title">Audit Trail</div>
      </template>
      <el-alert
        type="info"
        show-icon
        :closable="false"
        title="Local JSONL audit store is an audit readiness foundation."
        description="Local hash-chain verification supports audit readiness. It is not a formal certified evidence protocol or certification proof."
        class="block-space"
      />
      <el-alert
        v-if="auditError"
        type="warning"
        show-icon
        :closable="false"
        :title="auditError"
        class="block-space"
      />
      <el-skeleton v-if="loadingAudit" :rows="3" animated />
      <template v-else>
        <div class="audit-filter-row block-space">
          <el-select v-model="auditFilters.eventType" placeholder="Filter Event Type" clearable class="audit-filter-input">
            <el-option label="report.query" value="report.query" />
            <el-option label="report.export_manifest" value="report.export_manifest" />
          </el-select>
          <el-input v-model="auditFilters.reportId" placeholder="Filter Report ID" clearable class="audit-filter-input" />
          <el-input-number v-model="auditFilters.limit" :min="1" :max="200" controls-position="right" />
          <el-button plain @click="refreshAuditTrail">Refresh Audit</el-button>
          <el-button type="primary" plain :loading="verifyingAudit" @click="verifyAuditChainNow">
            Verify Audit Chain
          </el-button>
        </div>

        <div class="audit-filter-row block-space">
          <el-tooltip
            :disabled="canExportAuditRecords"
            content="Load audit records before exporting."
            placement="top"
          >
            <el-button plain :disabled="!canExportAuditRecords" @click="exportCurrentAuditJson">
              Export Audit JSON
            </el-button>
          </el-tooltip>
          <el-tooltip
            :disabled="canExportAuditRecords"
            content="Load audit records before exporting."
            placement="top"
          >
            <el-button plain :disabled="!canExportAuditRecords" @click="exportCurrentAuditCsv">
              Export Audit CSV
            </el-button>
          </el-tooltip>
          <span class="field-helper-text">{{ auditExportHelperText }}</span>
        </div>

        <el-descriptions :column="3" border class="block-space">
          <el-descriptions-item label="storageMode">{{ auditStorageMode }}</el-descriptions-item>
          <el-descriptions-item label="permissionMode">{{ auditPermissionMode }}</el-descriptions-item>
          <el-descriptions-item label="verificationStatus">
            {{ auditVerification?.verified === false ? 'failed' : auditVerification?.verified ? 'verified' : 'not-run' }}
          </el-descriptions-item>
          <el-descriptions-item label="auditExportMode">browser-local</el-descriptions-item>
          <el-descriptions-item label="auditExportScope">current-audit-records</el-descriptions-item>
          <el-descriptions-item label="formats">json/csv</el-descriptions-item>
          <el-descriptions-item label="totalLines">{{ auditReadStats.totalLines }}</el-descriptions-item>
          <el-descriptions-item label="validRecords">{{ auditReadStats.validRecords }}</el-descriptions-item>
          <el-descriptions-item label="corruptedLines">{{ auditReadStats.corruptedLines }}</el-descriptions-item>
          <el-descriptions-item label="skippedLines">{{ auditReadStats.skippedLines }}</el-descriptions-item>
          <el-descriptions-item label="storePathMode">{{ auditReadStats.storePathMode }}</el-descriptions-item>
          <el-descriptions-item label="retentionClass">
            {{ auditRetentionPolicy?.retentionClass ?? 'audit-readiness-local' }}
          </el-descriptions-item>
          <el-descriptions-item label="retentionPolicy" :span="2">
            {{ auditRetentionPolicy?.defaultRetention ?? 'manual-cleanup' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-card v-if="auditVerification" shadow="never" class="block-space">
          <template #header>Audit Verification</template>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="verified">{{ auditVerification.verified }}</el-descriptions-item>
            <el-descriptions-item label="verificationMode">{{ auditVerification.verificationMode }}</el-descriptions-item>
            <el-descriptions-item label="failedRecords">{{ auditVerification.failedRecords }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card v-if="auditRetentionPolicy" shadow="never" class="block-space">
          <template #header>Retention Policy</template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="retentionMode">{{ auditRetentionPolicy.retentionMode }}</el-descriptions-item>
            <el-descriptions-item label="defaultRetention">{{ auditRetentionPolicy.defaultRetention }}</el-descriptions-item>
            <el-descriptions-item label="dbRetentionIntegrated">
              {{ auditRetentionPolicy.dbRetentionIntegrated }}
            </el-descriptions-item>
            <el-descriptions-item label="legalHoldIntegrated">
              {{ auditRetentionPolicy.legalHoldIntegrated }}
            </el-descriptions-item>
            <el-descriptions-item label="redactionIntegrated">
              {{ auditRetentionPolicy.redactionIntegrated }}
            </el-descriptions-item>
            <el-descriptions-item label="notes">{{ auditRetentionPolicy.notes }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
        <el-empty
          v-if="auditRecords.length === 0"
          description="No audit records found yet. Run query or export manifest to create records."
        />
        <el-table
          v-else
          :data="auditRecords"
          row-key="auditId"
          empty-text="No audit records"
          @row-click="openAuditDetail"
        >
          <el-table-column prop="auditEventType" label="Event" min-width="170" />
          <el-table-column prop="reportId" label="Report" min-width="150" />
          <el-table-column prop="queryId" label="Query ID" min-width="230" show-overflow-tooltip />
          <el-table-column prop="exportId" label="Export ID" min-width="230" show-overflow-tooltip />
          <el-table-column prop="queryHash" label="queryHash" min-width="220" show-overflow-tooltip />
          <el-table-column prop="payloadHash" label="payloadHash" min-width="220" show-overflow-tooltip />
          <el-table-column prop="exportHash" label="exportHash" min-width="220" show-overflow-tooltip />
          <el-table-column prop="persistedAt" label="persistedAt" min-width="210" />
          <el-table-column prop="storageMode" label="storageMode" min-width="130" />
          <el-table-column prop="permissionMode" label="permissionMode" min-width="150" />
          <el-table-column prop="verificationStatus" label="verificationStatus" min-width="150" />
          <el-table-column label="certified" min-width="100">
            <template #default="{ row }">
              {{ row.certified }}
            </template>
          </el-table-column>
          <el-table-column label="iec62443Certified" min-width="150">
            <template #default="{ row }">
              {{ row.iec62443Certified }}
            </template>
          </el-table-column>
        </el-table>
      </template>
    </el-card>

    <el-drawer v-model="showAuditDetailDrawer" title="Audit Detail" size="45%">
      <el-skeleton v-if="loadingAuditDetail" :rows="8" animated />
      <el-empty v-else-if="!selectedAuditDetail" description="No audit detail selected." />
      <el-descriptions v-else :column="1" border>
        <el-descriptions-item label="auditId">{{ selectedAuditDetail.auditId }}</el-descriptions-item>
        <el-descriptions-item label="auditEventType">{{ selectedAuditDetail.auditEventType }}</el-descriptions-item>
        <el-descriptions-item label="reportId">{{ selectedAuditDetail.reportId }}</el-descriptions-item>
        <el-descriptions-item label="queryId">{{ selectedAuditDetail.queryId }}</el-descriptions-item>
        <el-descriptions-item label="exportId">{{ selectedAuditDetail.exportId || '-' }}</el-descriptions-item>
        <el-descriptions-item label="queryHash">{{ selectedAuditDetail.queryHash }}</el-descriptions-item>
        <el-descriptions-item label="payloadHash">{{ selectedAuditDetail.payloadHash }}</el-descriptions-item>
        <el-descriptions-item label="exportHash">{{ selectedAuditDetail.exportHash || '-' }}</el-descriptions-item>
        <el-descriptions-item label="previousAuditHash">
          {{ selectedAuditDetail.previousAuditHash || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="auditRecordHash">
          {{ selectedAuditDetail.auditRecordHash || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="storageMode">{{ selectedAuditDetail.storageMode }}</el-descriptions-item>
        <el-descriptions-item label="retentionClass">
          {{ selectedAuditDetail.retentionClass || 'audit-readiness-local' }}
        </el-descriptions-item>
        <el-descriptions-item label="retentionPolicy">
          {{ selectedAuditDetail.retentionPolicy || 'local-jsonl-retain-until-manual-cleanup' }}
        </el-descriptions-item>
        <el-descriptions-item label="permissionMode">{{ selectedAuditDetail.permissionMode }}</el-descriptions-item>
        <el-descriptions-item label="certified">{{ selectedAuditDetail.certified }}</el-descriptions-item>
        <el-descriptions-item label="iec62443Certified">{{ selectedAuditDetail.iec62443Certified }}</el-descriptions-item>
        <el-descriptions-item label="notes">{{ selectedAuditDetail.notes }}</el-descriptions-item>
      </el-descriptions>
    </el-drawer>
  </div>
</template>

<style scoped>
.reports-page {
  padding: 16px;
}

.page-header h1 {
  margin: 0 0 4px;
  font-size: 1.25rem;
  font-weight: 600;
}

.page-header p {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 0.875rem;
}

.page-card {
  min-height: calc(100vh - 64px);
}

.page-hero {
  border-left: 4px solid var(--el-color-primary);
}

.block-space {
  margin-bottom: 16px;
}

.top-space {
  margin-top: 16px;
}

.section-title {
  font-weight: 600;
}

.field-helper-text {
  margin-top: 6px;
  font-size: 0.75rem;
  color: var(--el-text-color-secondary);
}

.export-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.audit-filter-row {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.audit-filter-input {
  width: 220px;
}

:deep(.catalog-row-selected) {
  --el-table-tr-bg-color: #ecf5ff;
}

.summary-block {
  margin: 0;
  font-size: 0.8125rem;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>

