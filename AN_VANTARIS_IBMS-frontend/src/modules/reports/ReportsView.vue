<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { ApiError } from '@/services/api/errors'
import {
  getReportCatalogItem,
  getReportsCatalog,
  getReportsHealth,
  queryReport,
  type QueryReportPayload,
  type QueryReportResult,
  type ReportsCatalogItem,
  type ReportsHealth,
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
const querying = ref(false)
const exportingCsv = ref(false)
const queryExecuted = ref(false)
const fallbackMode = ref(false)
const apiUnavailable = ref(false)

const healthError = ref('')
const catalogError = ref('')
const queryError = ref('')

const selectedReportId = ref('')
const catalogItems = ref<ReportsCatalogItem[]>([])
const health = ref<ReportsHealth>({
  module: 'reports',
  status: 'unknown',
  runtimeMode: 'skeleton',
  provider: 'local-mock-provider',
  sourceSemantics: 'ibms-neutral',
})

const queryResult = ref<QueryReportResult | null>(null)

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

function normalizeError(error: unknown, fallback: string): string {
  return error instanceof ApiError ? error.message : fallback
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
      return
    }
    queryResult.value = await queryReport(payload)
  } catch (error) {
    const message = normalizeError(error, 'Failed to query report.')
    if (apiUnavailable.value) {
      queryResult.value = buildLocalFallbackQueryResult(payload)
      queryError.value = `${message} Switched to fallback mock mode.`
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

async function exportCurrentResultCsv(): Promise<void> {
  if (!queryResult.value || !canExportCsv.value) {
    return
  }

  exportingCsv.value = true
  try {
    const csv = buildCsv(queryResult.value.columns as unknown[], queryResult.value.rows)
    if (!csv) {
      ElMessage.error('No exportable data in current result.')
      return
    }
    const filename = buildCsvFilename(queryResult.value.reportId || selectedReportId.value || 'report')
    downloadCsv(filename, csv)
    ElMessage.success('CSV export completed.')
  } catch {
    ElMessage.error('CSV export failed.')
  } finally {
    exportingCsv.value = false
  }
}

onMounted(() => {
  void loadHealth()
  void loadCatalog()
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
          <el-descriptions-item label="exportMode">browser-local</el-descriptions-item>
          <el-descriptions-item label="exportScope">current-result</el-descriptions-item>
          <el-descriptions-item label="exportFormat">csv</el-descriptions-item>
        </el-descriptions>

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

