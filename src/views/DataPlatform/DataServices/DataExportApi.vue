<template>
  <!-- Loading Screen -->
  <div v-if="!isLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">
          <span class="loading-title">Loading</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Data Export API</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="export-api-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Data Platform</el-breadcrumb-item>
            <el-breadcrumb-item>Data Services</el-breadcrumb-item>
            <el-breadcrumb-item>Data Export API</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Data Export API</h1>
        <p class="description">Configure and manage data export jobs, API endpoints, and export history</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExportLogs">
          <el-icon><Download /></el-icon>
          Export Logs
        </el-button>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          Create Export Job
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6" v-for="stat in statsCards" :key="stat.title">
        <el-card class="stat-card" shadow="hover" @click="handleCardClick(stat)">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">{{ stat.title }}</div>
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
                <el-icon><component :is="stat.trend > 0 ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
                {{ Math.abs(stat.trend) }}%
                <span class="trend-label">vs last week</span>
              </div>
            </div>
            <div class="stat-icon" :style="{ background: stat.bgColor }">
              <el-icon :size="28" color="white">
                <component :is="stat.icon" />
              </el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Export Volume Chart -->
    <el-card class="chart-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Export Volume (Last 30 Days)</span>
          <el-radio-group v-model="chartPeriod" size="small">
            <el-radio-button value="daily">Daily</el-radio-button>
            <el-radio-button value="weekly">Weekly</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <div ref="volumeChartRef" class="chart-container"></div>
    </el-card>

    <!-- Export Jobs Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Export Jobs ({{ filteredJobs.length }})</span>
          <div class="table-actions">
            <el-input
                v-model="searchKeyword"
                placeholder="Search by name or dataset"
                prefix-icon="Search"
                clearable
                style="width: 220px"
            />
            <el-button :icon="Refresh" @click="fetchJobs" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedJobs" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="name" label="Job Name" min- show-overflow-tooltip />
        <el-table-column prop="dataset" label="Dataset"  show-overflow-tooltip />
        <el-table-column prop="format" label="Format" width="90">
          <template #default="{ row }">
            <el-tag :type="getFormatTag(row.format)" size="small">{{ row.format }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="schedule" label="Schedule" width="130" />
        <el-table-column prop="totalRecords" label="Records"  align="right">
          <template #default="{ row }">
            {{ row.totalRecords?.toLocaleString() || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" >
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastRun" label="Last Run"  />
        <el-table-column label="Actions" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="runNow(row)">Run Now</el-button>
            <el-button link type="success" size="small" @click="viewHistory(row)">History</el-button>
            <el-button link type="info" size="small" @click="getAPIEndpoint(row)">API Endpoint</el-button>
            <el-button link type="danger" size="small" @click="deleteJob(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredJobs.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Export History Table -->
    <el-card class="history-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Recent Export History</span>
          <el-button size="small" @click="clearHistoryFilter">Clear Filter</el-button>
        </div>
      </template>

      <el-table :data="paginatedHistory" stripe style="width: 100%" v-loading="historyLoading">
        <el-table-column prop="jobName" label="Job Name"  show-overflow-tooltip />
        <el-table-column prop="startTime" label="Start Time"  />
        <el-table-column prop="endTime" label="End Time"  />
        <el-table-column prop="recordsExported" label="Records"  align="right" />
        <el-table-column prop="fileSize" label="File Size"  />
        <el-table-column prop="status" label="Status" >
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions"  fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="downloadFile(row)">Download</el-button>
            <el-button link type="info" size="small" @click="viewDetails(row)">Details</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="historyPage"
            v-model:page-size="historyPageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            :total="filteredHistory.length"
            @size-change="historyPage = 1"
        />
      </div>
    </el-card>

    <!-- Create/Edit Export Job Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? 'Create Export Job' : 'Edit Export Job'" width="650px" destroy-on-close>
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
        <el-form-item label="Job Name" prop="name">
          <el-input v-model="formData.name" placeholder="Enter job name" />
        </el-form-item>
        <el-form-item label="Dataset" prop="dataset">
          <el-select v-model="formData.dataset" placeholder="Select dataset" style="width: 100%">
            <el-option label="Device Master" value="device_master" />
            <el-option label="Energy Consumption" value="energy_consumption" />
            <el-option label="Telemetry Data" value="telemetry" />
            <el-option label="Maintenance Records" value="maintenance_records" />
            <el-option label="ESG Metrics" value="esg_metrics" />
          </el-select>
        </el-form-item>
        <el-form-item label="Export Format" prop="format">
          <el-radio-group v-model="formData.format">
            <el-radio label="CSV">CSV</el-radio>
            <el-radio label="JSON">JSON</el-radio>
            <el-radio label="Parquet">Parquet</el-radio>
            <el-radio label="Excel">Excel</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Schedule" prop="schedule">
          <el-select v-model="formData.schedule" placeholder="Select schedule" style="width: 100%">
            <el-option label="Manual Only" value="manual" />
            <el-option label="Every Hour" value="hourly" />
            <el-option label="Daily at 1 AM" value="daily" />
            <el-option label="Weekly on Monday" value="weekly" />
            <el-option label="Monthly on 1st" value="monthly" />
          </el-select>
        </el-form-item>
        <el-form-item label="Date Range" prop="dateRange">
          <el-date-picker
              v-model="formData.dateRange"
              type="daterange"
              range-separator="to"
              start-placeholder="Start Date"
              end-placeholder="End Date"
              style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="Filters (JSON)" prop="filters">
          <el-input
              v-model="formData.filters"
              type="textarea"
              :rows="2"
              placeholder='{"status": "active", "device_type": "HVAC"}'
          />
        </el-form-item>
        <el-form-item label="Columns" prop="columns">
          <el-select
              v-model="formData.columns"
              multiple
              filterable
              allow-create
              default-first-option
              placeholder="Select columns to export (leave empty for all)"
              style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="Compression" prop="compression">
          <el-switch v-model="formData.compression" active-text="GZIP" inactive-text="None" />
        </el-form-item>
        <el-form-item label="Notification Email" prop="notifyEmail">
          <el-input v-model="formData.notifyEmail" placeholder="user@example.com" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="testExport">Test Export</el-button>
        <el-button type="success" @click="submitForm">Save Job</el-button>
      </template>
    </el-dialog>

    <!-- API Endpoint Dialog -->
    <el-dialog v-model="apiDialogVisible" title="API Endpoint Details" width="600px" destroy-on-close>
      <div class="api-endpoint" v-if="currentJob">
        <el-alert title="API Information" type="info" :closable="false" show-icon>
          <p>Use this endpoint to trigger exports programmatically</p>
        </el-alert>

        <div class="endpoint-section">
          <h4>Endpoint URL</h4>
          <div class="endpoint-url">
            <code>{{ apiEndpoint }}</code>
            <el-button size="small" @click="copyEndpoint">Copy</el-button>
          </div>
        </div>

        <div class="endpoint-section">
          <h4>Authentication</h4>
          <p>Bearer Token required in Authorization header</p>
          <code>Authorization: Bearer YOUR_API_TOKEN</code>
        </div>

        <div class="endpoint-section">
          <h4>Example Request (cURL)</h4>
          <pre class="example-code">{{ curlExample }}</pre>
          <el-button size="small" @click="copyCurl">Copy</el-button>
        </div>

        <div class="endpoint-section">
          <h4>Example Response</h4>
          <pre class="example-code">{{ responseExample }}</pre>
        </div>

        <div class="endpoint-section">
          <h4>Query Parameters</h4>
          <el-table :data="queryParams" size="small" border>
            <el-table-column prop="name" label="Parameter" width="120" />
            <el-table-column prop="type" label="Type" width="80" />
            <el-table-column prop="required" label="Required" width="80">
              <template #default="{ row }">
                <el-tag :type="row.required ? 'danger' : 'info'" size="small">{{ row.required ? 'Yes' : 'No' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="Description" min-width="200" />
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="apiDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="testAPI">Test API</el-button>
      </template>
    </el-dialog>

    <!-- Export History Details Dialog -->
    <el-dialog v-model="detailsDialogVisible" :title="`Export Details - ${currentHistory?.jobName}`" width="700px" destroy-on-close>
      <div class="export-details" v-if="currentHistory">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Job Name">{{ currentHistory.jobName }}</el-descriptions-item>
          <el-descriptions-item label="Job ID">{{ currentHistory.jobId }}</el-descriptions-item>
          <el-descriptions-item label="Start Time">{{ currentHistory.startTime }}</el-descriptions-item>
          <el-descriptions-item label="End Time">{{ currentHistory.endTime }}</el-descriptions-item>
          <el-descriptions-item label="Duration">{{ currentHistory.duration }}</el-descriptions-item>
          <el-descriptions-item label="Records Exported">{{ currentHistory.recordsExported.toLocaleString() }}</el-descriptions-item>
          <el-descriptions-item label="File Size">{{ currentHistory.fileSize }}</el-descriptions-item>
          <el-descriptions-item label="Format">{{ currentHistory.format }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTag(currentHistory.status)" size="small">{{ currentHistory.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="File Location">{{ currentHistory.fileLocation }}</el-descriptions-item>
          <el-descriptions-item label="Error Message" :span="2" v-if="currentHistory.errorMessage">{{ currentHistory.errorMessage }}</el-descriptions-item>
        </el-descriptions>

        <div class="export-stats" v-if="currentHistory.stats">
          <h4>Export Statistics</h4>
          <el-row :gutter="16">
            <el-col :span="8">
              <div class="stat-mini">
                <div class="stat-mini-value">{{ currentHistory.stats.avgSpeed }}</div>
                <div class="stat-mini-label">Avg Speed (records/s)</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-mini">
                <div class="stat-mini-value">{{ currentHistory.stats.compressionRatio }}%</div>
                <div class="stat-mini-label">Compression Ratio</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-mini">
                <div class="stat-mini-value">{{ currentHistory.stats.cpuUsage }}%</div>
                <div class="stat-mini-label">CPU Usage</div>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailsDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="downloadFile(currentHistory)">Download File</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  Delete, CopyDocument, Link
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading export jobs...',
  'Fetching history...',
  'Almost ready...'
]

// ==================== Chart References ====================
const volumeChartRef = ref<HTMLElement>()
let volumeChart: echarts.ECharts | null = null

// ==================== State ====================
const tableLoading = ref(false)
const historyLoading = ref(false)
const dialogVisible = ref(false)
const apiDialogVisible = ref(false)
const detailsDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const currentJob = ref<any>(null)
const currentHistory = ref<any>(null)
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const historyPage = ref(1)
const historyPageSize = ref(10)
const chartPeriod = ref('daily')
const formRef = ref()

const formData = reactive({
  name: '',
  dataset: '',
  format: 'CSV',
  schedule: 'manual',
  dateRange: null as [Date, Date] | null,
  filters: '',
  columns: [] as string[],
  compression: false,
  notifyEmail: ''
})

const formRules = {
  name: [{ required: true, message: 'Please enter job name', trigger: 'blur' }],
  dataset: [{ required: true, message: 'Please select dataset', trigger: 'change' }],
  dateRange: [{ required: true, message: 'Please select date range', trigger: 'change' }]
}

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'Active Jobs', value: 24, trend: 8, icon: 'Document', bgColor: '#409eff', key: 'active' },
  { title: 'Total Exports', value: '1,245', trend: 15, icon: 'TrendCharts', bgColor: '#67c23a', key: 'exports' },
  { title: 'Data Exported', value: '2.4 TB', trend: 22, icon: 'Download', bgColor: '#e6a23c', key: 'volume' },
  { title: 'API Calls (24h)', value: '3,421', trend: 12, icon: 'Link', bgColor: '#f56c6c', key: 'apiCalls' }
])

const exportJobs = ref([
  {
    id: 1,
    name: 'Daily Device Export',
    dataset: 'device_master',
    format: 'CSV',
    schedule: 'daily',
    totalRecords: 12450,
    status: 'Active',
    lastRun: '2024-01-20 01:00:00'
  },
  {
    id: 2,
    name: 'Energy Consumption Weekly',
    dataset: 'energy_consumption',
    format: 'Parquet',
    schedule: 'weekly',
    totalRecords: 89000,
    status: 'Active',
    lastRun: '2024-01-15 02:00:00'
  },
  {
    id: 3,
    name: 'ESG Metrics Monthly',
    dataset: 'esg_metrics',
    format: 'Excel',
    schedule: 'monthly',
    totalRecords: 1250,
    status: 'Active',
    lastRun: '2024-01-01 03:00:00'
  },
  {
    id: 4,
    name: 'Telemetry Export',
    dataset: 'telemetry',
    format: 'JSON',
    schedule: 'hourly',
    totalRecords: 1450000,
    status: 'Paused',
    lastRun: '2024-01-20 09:00:00'
  }
])

const exportHistory = ref([
  {
    id: 1,
    jobId: 1,
    jobName: 'Daily Device Export',
    startTime: '2024-01-20 01:00:00',
    endTime: '2024-01-20 01:15:23',
    duration: '15 min 23 sec',
    recordsExported: 12450,
    fileSize: '45 MB',
    format: 'CSV',
    status: 'Success',
    fileLocation: '/exports/device_master_2024-01-20.csv.gz',
    stats: { avgSpeed: 1350, compressionRatio: 75, cpuUsage: 12 }
  },
  {
    id: 2,
    jobId: 1,
    jobName: 'Daily Device Export',
    startTime: '2024-01-19 01:00:00',
    endTime: '2024-01-19 01:14:56',
    duration: '14 min 56 sec',
    recordsExported: 12340,
    fileSize: '44 MB',
    format: 'CSV',
    status: 'Success',
    fileLocation: '/exports/device_master_2024-01-19.csv.gz',
    stats: { avgSpeed: 1375, compressionRatio: 74, cpuUsage: 11 }
  },
  {
    id: 3,
    jobId: 2,
    jobName: 'Energy Consumption Weekly',
    startTime: '2024-01-15 02:00:00',
    endTime: '2024-01-15 02:08:30',
    duration: '8 min 30 sec',
    recordsExported: 89000,
    fileSize: '12 MB',
    format: 'Parquet',
    status: 'Success',
    fileLocation: '/exports/energy_weekly_2024-01-15.parquet'
  },
  {
    id: 4,
    jobId: 4,
    jobName: 'Telemetry Export',
    startTime: '2024-01-20 09:00:00',
    endTime: '2024-01-20 09:00:00',
    duration: '0 sec',
    recordsExported: 0,
    fileSize: '0 MB',
    format: 'JSON',
    status: 'Failed',
    errorMessage: 'Connection timeout to data source'
  }
])

// ==================== Computed ====================
const filteredJobs = computed(() => {
  if (!searchKeyword.value) return exportJobs.value
  return exportJobs.value.filter(j =>
      j.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      j.dataset.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

const paginatedJobs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredJobs.value.slice(start, end)
})

const filteredHistory = computed(() => {
  return exportHistory.value
})

const paginatedHistory = computed(() => {
  const start = (historyPage.value - 1) * historyPageSize.value
  const end = start + historyPageSize.value
  return filteredHistory.value.slice(start, end)
})

// API Endpoint
const apiEndpoint = computed(() => {
  if (!currentJob.value) return ''
  return `https://api.ibms.com/v1/export/${currentJob.value.id}/trigger`
})

const curlExample = computed(() => {
  return `curl -X POST ${apiEndpoint.value} \\
  -H "Authorization: Bearer YOUR_API_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"format": "CSV", "date_range": {"start": "2024-01-01", "end": "2024-01-31"}}'`
})

const responseExample = `{
  "success": true,
  "job_id": "exp_12345",
  "status": "queued",
  "estimated_completion": "2024-01-20T10:15:00Z",
  "download_url": "https://api.ibms.com/v1/export/download/exp_12345"
}`

const queryParams = [
  { name: 'format', type: 'string', required: false, description: 'CSV, JSON, Parquet, Excel' },
  { name: 'date_range.start', type: 'string', required: true, description: 'Start date (ISO 8601)' },
  { name: 'date_range.end', type: 'string', required: true, description: 'End date (ISO 8601)' },
  { name: 'filters', type: 'object', required: false, description: 'Additional filters as JSON' },
  { name: 'columns', type: 'array', required: false, description: 'Specific columns to export' },
  { name: 'compression', type: 'boolean', required: false, description: 'Enable GZIP compression' }
]

// ==================== Helper Methods ====================
const getFormatTag = (format: string) => {
  const map: Record<string, string> = {
    'CSV': 'success',
    'JSON': 'primary',
    'Parquet': 'warning',
    'Excel': 'info'
  }
  return map[format] || 'info'
}

const getStatusTag = (status: string) => {
  const map: Record<string, string> = {
    'Active': 'success',
    'Paused': 'warning',
    'Success': 'success',
    'Failed': 'danger',
    'Processing': 'warning',
    'Queued': 'info'
  }
  return map[status] || 'info'
}

// ==================== Chart Initialization ====================
const initVolumeChart = () => {
  if (!volumeChartRef.value) return
  if (volumeChart) volumeChart.dispose()

  volumeChart = echarts.init(volumeChartRef.value)

  const dailyData = [2.4, 2.8, 3.1, 2.9, 3.4, 3.8, 4.2, 4.5, 4.8, 5.2, 5.6, 5.9, 6.2, 6.5, 6.8, 7.1, 7.4, 7.8, 8.2, 8.5, 8.9, 9.2, 9.5, 9.8, 10.2, 10.5, 10.8, 11.2, 11.5, 11.8]
  const weeklyData = [15.2, 18.5, 22.3, 25.8, 29.4]

  const data = chartPeriod.value === 'daily' ? dailyData : weeklyData
  const xAxisData = chartPeriod.value === 'daily'
      ? Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`)
      : ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5']

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: xAxisData, axisLabel: { rotate: chartPeriod.value === 'daily' ? 45 : 0 } },
    yAxis: { type: 'value', name: 'Volume (GB)' },
    series: [{
      type: 'bar',
      data: data,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#409eff' },
      label: { show: true, position: 'top', formatter: '{c} GB' }
    }]
  }

  volumeChart.setOption(option)
  window.addEventListener('resize', () => volumeChart?.resize())
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleExportLogs = () => {
  ElMessage.success('Exporting logs...')
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const openCreateDialog = () => {
  dialogMode.value = 'create'
  Object.assign(formData, {
    name: '',
    dataset: '',
    format: 'CSV',
    schedule: 'manual',
    dateRange: null,
    filters: '',
    columns: [],
    compression: false,
    notifyEmail: ''
  })
  dialogVisible.value = true
}

const fetchJobs = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Jobs refreshed')
  }, 500)
}

const runNow = (job: any) => {
  ElMessage.info(`Starting export job "${job.name}"...`)
  setTimeout(() => {
    ElMessage.success(`Export job "${job.name}" completed`)
  }, 3000)
}

const viewHistory = (job: any) => {
  currentJob.value = job
  // Filter history by job
  ElMessage.info(`Viewing history for ${job.name}`)
}

const getAPIEndpoint = (job: any) => {
  currentJob.value = job
  apiDialogVisible.value = true
}

const deleteJob = (job: any) => {
  ElMessageBox.confirm(`Delete export job "${job.name}"?`, 'Confirm Delete', {
    confirmButtonText: 'Delete',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = exportJobs.value.findIndex(j => j.id === job.id)
    if (index !== -1) {
      exportJobs.value.splice(index, 1)
      ElMessage.success(`Deleted: ${job.name}`)
    }
  }).catch(() => {})
}

const downloadFile = (history: any) => {
  ElMessage.success(`Downloading ${history.fileLocation}`)
}

const viewDetails = (history: any) => {
  currentHistory.value = history
  detailsDialogVisible.value = true
}

const testExport = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.info('Testing export configuration...')
      setTimeout(() => {
        ElMessage.success('Test export successful. Ready to create job.')
      }, 2000)
    }
  })
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success(dialogMode.value === 'create' ? 'Export job created successfully' : 'Export job updated successfully')
      dialogVisible.value = false
    }
  })
}

const clearHistoryFilter = () => {
  historyPage.value = 1
  ElMessage.success('Filter cleared')
}

const copyEndpoint = () => {
  navigator.clipboard.writeText(apiEndpoint.value)
  ElMessage.success('Endpoint copied')
}

const copyCurl = () => {
  navigator.clipboard.writeText(curlExample.value)
  ElMessage.success('cURL command copied')
}

const testAPI = () => {
  ElMessage.info('Testing API endpoint...')
  setTimeout(() => {
    ElMessage.success('API test successful')
  }, 1500)
}

const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {}

// ==================== Loading Simulation ====================
const initCharts = async () => {
  await nextTick()
  setTimeout(() => {
    initVolumeChart()
  }, 100)
}

onMounted(() => {
  let messageIndex = 0
  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 400)

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      initCharts()
      fetchJobs()
    }, 400)
  }, 2000)
})
</script>

<style scoped lang="scss">
/* ==================== Loading Screen ==================== */
.loading-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: center;
}

.loading-overlay {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  backdrop-filter: blur(2px);
}

.loading-content {
  text-align: center;
  padding: 40px;
  border-radius: 32px;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(59, 130, 246, 0.3);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  animation: fadeInUp 0.6s ease-out;
}

.loading-spinner {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
}

.spinner-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 3px solid transparent;
  animation: spin 1.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
}

.spinner-ring:nth-child(1) {
  border-top-color: #3b82f6;
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  border-right-color: #f59e0b;
  animation-delay: 0.2s;
  width: 70%;
  height: 70%;
  top: 15%;
  left: 15%;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #10b981;
  animation-delay: 0.4s;
  width: 40%;
  height: 40%;
  top: 30%;
  left: 30%;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-bottom: 24px;
  font-size: 28px;
  font-weight: 700;
  color: #e2e8f0;
  display: flex;
  justify-content: center;
  align-items: baseline;
  gap: 4px;
}

.loading-dots {
  display: inline-flex;
  gap: 2px;
}

.loading-dots span {
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
  40% { transform: scale(1); opacity: 1; }
}

.loading-progress {
  width: 280px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin: 0 auto 16px;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec489a);
  border-radius: 4px;
  transition: width 0.3s ease;
  background-size: 200% auto;
  animation: shimmer 2s linear infinite;
}

@keyframes shimmer {
  0% { background-position: 0% 0%; }
  100% { background-position: 200% 0%; }
}

.loading-tip {
  font-size: 13px;
  color: #94a3b8;
  letter-spacing: 1px;
  margin-bottom: 8px;
  font-weight: 500;
}

.loading-subtip {
  font-size: 11px;
  color: #64748b;
  letter-spacing: 0.5px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ==================== Main Page Styles ==================== */
.export-api-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;

  .breadcrumb {
    margin-bottom: 8px;
  }

  h1 {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 8px 0;
  }

  .description {
    color: #909399;
    font-size: 14px;
    margin: 0;
  }

  .header-actions {
    display: flex;
    gap: 12px;
  }
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
  }

  .stat-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .stat-info {
    flex: 1;
  }

  .stat-title {
    font-size: 14px;
    color: #909399;
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }

  .stat-trend {
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 4px;

    &.up { color: #67c23a; }
    &.down { color: #f56c6c; }

    .trend-label {
      color: #909399;
      margin-left: 4px;
    }
  }

  .stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.chart-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}

.chart-container {
  width: 100%;
  height: 320px;
}

.table-card, .history-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .table-actions {
    display: flex;
    gap: 12px;
    align-items: center;
  }
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.api-endpoint {
  .endpoint-section {
    margin-top: 20px;

    h4 {
      margin-bottom: 8px;
      color: #303133;
    }

    .endpoint-url {
      display: flex;
      align-items: center;
      gap: 12px;
      background: #f5f7fa;
      padding: 8px 12px;
      border-radius: 4px;

      code {
        flex: 1;
        font-family: monospace;
        font-size: 13px;
        word-break: break-all;
      }
    }

    .example-code {
      background: #1e1e1e;
      color: #d4d4d4;
      padding: 12px;
      border-radius: 4px;
      font-family: monospace;
      font-size: 12px;
      overflow-x: auto;
      margin: 8px 0;
    }
  }
}

.export-details {
  .export-stats {
    margin-top: 20px;

    h4 {
      margin-bottom: 12px;
      color: #303133;
    }

    .stat-mini {
      text-align: center;
      padding: 12px;
      background: #f5f7fa;
      border-radius: 8px;

      .stat-mini-value {
        font-size: 24px;
        font-weight: 600;
        color: #303133;
      }

      .stat-mini-label {
        font-size: 12px;
        color: #909399;
        margin-top: 4px;
      }
    }
  }
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
}
</style>