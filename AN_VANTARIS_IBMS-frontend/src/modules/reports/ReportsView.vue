<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { ApiError } from '@/services/api/errors'
import {
  getReportCatalogItem,
  getReportsCatalog,
  getReportsHealth,
  queryReport,
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
  limit: number
}

const loadingHealth = ref(false)
const loadingCatalog = ref(false)
const querying = ref(false)
const exportingCsv = ref(false)
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
    supportedFilters: ['timeRange', 'siteId', 'moduleId', 'status', 'severity', 'category'],
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
    supportedFilters: ['timeRange', 'siteId', 'moduleId', 'severity', 'category'],
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

function normalizeError(error: unknown, fallback: string): string {
  return error instanceof ApiError ? error.message : fallback
}

function buildQueryPayload() {
  return {
    reportId: selectedReportId.value,
    limit: Math.min(Math.max(Number(filters.limit) || 20, 1), 100),
    filters: {
      timeRange: filters.timeRange,
      siteId: filters.siteId,
      moduleId: filters.moduleId,
      status: filters.status,
      severity: filters.severity,
      category: filters.category,
    },
  }
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
    }
    loadingCatalog.value = false
  }
}

async function selectReport(report: ReportsCatalogItem): Promise<void> {
  selectedReportId.value = report.reportId
  queryError.value = ''
  if (fallbackMode.value) {
    return
  }
  try {
    const detail = await getReportCatalogItem(report.reportId)
    selectedReportId.value = detail.reportId
  } catch (error) {
    const message = normalizeError(error, 'Failed to load report catalog detail.')
    queryError.value = message
    ElMessage.warning(message)
  }
}

function buildLocalFallbackQueryResult(payload: ReturnType<typeof buildQueryPayload>): QueryReportResult {
  const rows = Array.from({ length: payload.limit }, (_, index) => ({
    recordId: `${payload.reportId}-fallback-${index + 1}`,
    sourceType: 'reference',
    sourceReferenceId: `fallback-ref-${index + 1}`,
    sourceModuleId: payload.filters.moduleId || 'source-reference',
    status: payload.filters.status || 'open',
    severity: payload.filters.severity || 'medium',
    category: payload.filters.category || 'general',
    timestamp: new Date().toISOString(),
    evidenceReferenceId: `fallback-ev-${index + 1}`,
    summary: `Fallback mock row ${index + 1} for ${payload.reportId}`,
    count: index + 1,
    trendValue: Number(((index + 1) * 1.2).toFixed(2)),
    aggregationLevel: 'raw',
  }))
  const columns = Object.keys(rows[0] ?? {})
  return {
    reportId: payload.reportId,
    reportName:
      catalogItems.value.find((item) => item.reportId === payload.reportId)?.reportName ??
      'Fallback Report',
    queryId: `fallback-${Date.now()}`,
    generatedAt: new Date().toISOString(),
    filters: payload.filters,
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
  const payload = buildQueryPayload()
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
    <el-card shadow="never" class="page-card">
      <template #header>
        <div class="page-header">
          <div>
            <h1>Reports / 报表工作台</h1>
            <p>IBMS-neutral reporting UI skeleton with local/mock query execution.</p>
          </div>
        </div>
      </template>

      <el-alert
        v-if="apiUnavailable"
        type="warning"
        show-icon
        :closable="false"
        title="API unavailable. Running in fallback mode."
        description="fallbackMode: true, sourceSemantics: ibms-neutral, mockData: true"
        class="block-space"
      />

      <el-alert
        v-if="healthError || catalogError || queryError"
        type="error"
        show-icon
        :closable="false"
        :title="healthError || catalogError || queryError"
        class="block-space"
      />

      <el-descriptions :column="2" border class="block-space" v-loading="loadingHealth">
        <el-descriptions-item label="status">{{ health.status }}</el-descriptions-item>
        <el-descriptions-item label="runtimeMode">{{ health.runtimeMode }}</el-descriptions-item>
        <el-descriptions-item label="provider">{{ health.provider }}</el-descriptions-item>
        <el-descriptions-item label="sourceSemantics">{{ health.sourceSemantics }}</el-descriptions-item>
        <el-descriptions-item label="fallbackMode">
          <el-tag :type="fallbackMode ? 'warning' : 'success'" size="small">{{ fallbackMode }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <el-card shadow="never" class="block-space">
        <template #header>
          <div class="section-title">Report Catalog</div>
        </template>
        <el-table
          v-loading="loadingCatalog"
          :data="catalogItems"
          row-key="reportId"
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
              <el-button
                link
                type="primary"
                :disabled="querying"
                @click="selectReport(row)"
              >
                {{ selectedReportId === row.reportId ? 'Selected' : 'Select' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <el-card shadow="never" class="block-space">
        <template #header>
          <div class="section-title">Query Filters</div>
        </template>
        <el-form label-position="top">
          <el-row :gutter="12">
            <el-col :xs="24" :sm="12" :md="6">
              <el-form-item label="Selected Report">
                <el-input :model-value="selectedReportId" disabled placeholder="Select from catalog" />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-form-item label="timeRange">
                <el-input v-model="filters.timeRange" placeholder="last_24h" />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-form-item label="siteId">
                <el-input v-model="filters.siteId" placeholder="site-001" />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-form-item label="moduleId">
                <el-input v-model="filters.moduleId" placeholder="source-reference" />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-form-item label="status">
                <el-input v-model="filters.status" placeholder="open" />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-form-item label="severity">
                <el-input v-model="filters.severity" placeholder="medium" />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-form-item label="category">
                <el-input v-model="filters.category" placeholder="general" />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-form-item label="limit">
                <el-input-number v-model="filters.limit" :min="1" :max="100" :step="1" controls-position="right" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>

        <el-button type="primary" :loading="querying" :disabled="!selectedReportId" @click="runQuery">
          Run Query
        </el-button>
      </el-card>

      <el-card shadow="never">
        <template #header>
          <div class="section-title">Query Result</div>
        </template>

        <el-empty v-if="!queryResult" description="Run query to view mock/local result" />

        <template v-else>
          <el-descriptions :column="2" border class="block-space">
            <el-descriptions-item label="queryId">{{ queryResult.queryId }}</el-descriptions-item>
            <el-descriptions-item label="generatedAt">{{ queryResult.generatedAt }}</el-descriptions-item>
            <el-descriptions-item label="mockData">{{ queryResult.mockData }}</el-descriptions-item>
            <el-descriptions-item label="provider">{{ queryResult.provider }}</el-descriptions-item>
            <el-descriptions-item label="runtimeMode">{{ queryResult.runtimeMode }}</el-descriptions-item>
            <el-descriptions-item label="sourceSemantics">{{ queryResult.sourceSemantics }}</el-descriptions-item>
            <el-descriptions-item label="exportMode">browser-local</el-descriptions-item>
            <el-descriptions-item label="exportScope">current-result</el-descriptions-item>
            <el-descriptions-item label="exportFormat">csv</el-descriptions-item>
          </el-descriptions>

          <el-button
            type="success"
            plain
            class="block-space"
            :loading="exportingCsv"
            :disabled="!canExportCsv"
            @click="exportCurrentResultCsv"
          >
            Export CSV
          </el-button>

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

.block-space {
  margin-bottom: 16px;
}

.section-title {
  font-weight: 600;
}

.summary-block {
  margin: 0;
  font-size: 0.8125rem;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>

