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
        <div class="loading-tip">Missing Data Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="missing-data-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Data Platform</el-breadcrumb-item>
            <el-breadcrumb-item>Data Quality</el-breadcrumb-item>
            <el-breadcrumb-item>Missing Data</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Missing Data Management</h1>
        <p class="description">Identify, analyze, and resolve missing data issues across data assets</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
        <el-button type="primary" @click="handleScan">
          <el-icon><Search /></el-icon>
          Run Scan
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
                <span class="trend-label">vs last month</span>
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

    <!-- Missing Data Overview Charts -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="14">
        <el-card class="trend-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Missing Data Trend</span>
              <el-radio-group v-model="trendPeriod" size="small">
                <el-radio-button value="weekly">Weekly</el-radio-button>
                <el-radio-button value="monthly">Monthly</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="10">
        <el-card class="distribution-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Missing Rate by Table</span>
            </div>
          </template>
          <div ref="tableChartRef" class="bar-chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Filters -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-container">
        <div class="filter-row">
          <el-input
              v-model="filters.keyword"
              placeholder="Search by table or column"
              prefix-icon="Search"
              clearable
              style="width: 220px"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
          />
          <el-select v-model="filters.table" placeholder="Table" clearable style="width: 160px">
            <el-option label="device_master" value="device_master" />
            <el-option label="energy_consumption" value="energy_consumption" />
            <el-option label="customer_contract" value="customer_contract" />
            <el-option label="maintenance_work_orders" value="maintenance_work_orders" />
          </el-select>
          <el-select v-model="filters.severity" placeholder="Severity" clearable style="width: 120px">
            <el-option label="Critical" value="Critical" />
            <el-option label="High" value="High" />
            <el-option label="Medium" value="Medium" />
            <el-option label="Low" value="Low" />
          </el-select>
          <el-select v-model="filters.status" placeholder="Status" clearable style="width: 120px">
            <el-option label="Open" value="Open" />
            <el-option label="In Progress" value="In Progress" />
            <el-option label="Resolved" value="Resolved" />
          </el-select>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="handleResetFilters">Reset</el-button>
        </div>
      </div>
    </el-card>

    <!-- Missing Data Issues Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Missing Data Issues ({{ filteredIssues.length }} issues)</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchIssues" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedIssues" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="table" label="Table"  show-overflow-tooltip />
        <el-table-column prop="column" label="Column"  show-overflow-tooltip />
        <el-table-column prop="missingCount" label="Missing Count"  align="right">
          <template #default="{ row }">
            {{ row.missingCount.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="totalRows" label="Total Rows"  align="right">
          <template #default="{ row }">
            {{ row.totalRows.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="missingRate" label="Missing Rate" >
          <template #default="{ row }">
            <el-progress :percentage="row.missingRate" :stroke-width="8" :color="getMissingRateColor(row.missingRate)" />
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="Severity" >
          <template #default="{ row }">
            <el-tag :type="getSeverityTag(row.severity)" size="small">{{ row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" >
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detectedAt" label="Detected"  />
        <el-table-column label="Actions"  fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">Details</el-button>
            <el-button link type="success" size="small" @click="handleIssue(row)">Handle</el-button>
            <el-button link type="info" size="small" @click="viewRecords(row)">View Records</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[15, 30, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredIssues.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Issue Details Dialog -->
    <el-dialog v-model="detailsDialogVisible" :title="`Missing Data Issue - ${currentIssue?.table}.${currentIssue?.column}`" width="700px" destroy-on-close>
      <div class="issue-details" v-if="currentIssue">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Table">{{ currentIssue.table }}</el-descriptions-item>
          <el-descriptions-item label="Column">{{ currentIssue.column }}</el-descriptions-item>
          <el-descriptions-item label="Missing Count">{{ currentIssue.missingCount.toLocaleString() }}</el-descriptions-item>
          <el-descriptions-item label="Total Rows">{{ currentIssue.totalRows.toLocaleString() }}</el-descriptions-item>
          <el-descriptions-item label="Missing Rate">
            <el-progress :percentage="currentIssue.missingRate" :stroke-width="10" :color="getMissingRateColor(currentIssue.missingRate)" />
          </el-descriptions-item>
          <el-descriptions-item label="Severity">
            <el-tag :type="getSeverityTag(currentIssue.severity)" size="small">{{ currentIssue.severity }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTag(currentIssue.status)" size="small">{{ currentIssue.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Detected At">{{ currentIssue.detectedAt }}</el-descriptions-item>
          <el-descriptions-item label="Last Updated">{{ currentIssue.lastUpdated }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ currentIssue.description }}</el-descriptions-item>
          <el-descriptions-item label="Suggested Action" :span="2">{{ currentIssue.suggestedAction }}</el-descriptions-item>
        </el-descriptions>

        <!-- Sample Missing Records -->
        <div class="sample-records">
          <h4>Sample Missing Records</h4>
          <el-table :data="currentIssue.sampleRecords || []" size="small" border>
            <el-table-column prop="id" label="Record ID" width="150" />
            <el-table-column prop="value" label="Current Value" min-width="150" />
            <el-table-column prop="expected" label="Expected Value" min-width="150" />
            <el-table-column label="Action" width="100">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="fillMissing(row)">Fill</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailsDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="handleIssue(currentIssue)">Handle Issue</el-button>
      </template>
    </el-dialog>

    <!-- Handle Issue Dialog -->
    <el-dialog v-model="handleDialogVisible" title="Handle Missing Data" width="500px">
      <el-form :model="handleForm" label-width="120px">
        <el-form-item label="Action" prop="action">
          <el-select v-model="handleForm.action" placeholder="Select action" style="width: 100%">
            <el-option label="Fill with Default Value" value="fill_default" />
            <el-option label="Fill with Mean/Median" value="fill_statistical" />
            <el-option label="Fill from Source" value="fill_source" />
            <el-option label="Mark as Null (Accept)" value="mark_null" />
            <el-option label="Delete Records" value="delete_records" />
          </el-select>
        </el-form-item>
        <el-form-item label="Default Value" v-if="handleForm.action === 'fill_default'">
          <el-input v-model="handleForm.defaultValue" placeholder="Enter default value" />
        </el-form-item>
        <el-form-item label="Source Query" v-if="handleForm.action === 'fill_source'">
          <el-input v-model="handleForm.sourceQuery" type="textarea" :rows="2" placeholder="Enter source query" />
        </el-form-item>
        <el-form-item label="Comment">
          <el-input v-model="handleForm.comment" type="textarea" :rows="2" placeholder="Add comment" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitHandle">Apply Fix</el-button>
      </template>
    </el-dialog>

    <!-- Missing Records Dialog -->
    <el-dialog v-model="recordsDialogVisible" title="Missing Records" width="800px" destroy-on-close>
      <el-table :data="missingRecords" border stripe v-loading="recordsLoading" max-height="400">
        <el-table-column v-for="col in recordColumns" :key="col" :prop="col" :label="col" min- />
      </el-table>
      <div class="pagination-container" style="margin-top: 16px">
        <el-pagination
            v-model:current-page="recordsPage"
            v-model:page-size="recordsPageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            :total="missingRecordsTotal"
            @size-change="recordsPage = 1"
            @current-change="loadMissingRecords"
        />
      </div>
      <template #footer>
        <el-button @click="recordsDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="exportMissingRecords">Export</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  DataAnalysis, Filter, Warning, Delete
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Analyzing missing data patterns...',
  'Scanning data assets...',
  'Almost ready...'
]

// ==================== Chart References ====================
const trendChartRef = ref<HTMLElement>()
const tableChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null
let tableChart: echarts.ECharts | null = null

// ==================== State ====================
const tableLoading = ref(false)
const recordsLoading = ref(false)
const detailsDialogVisible = ref(false)
const handleDialogVisible = ref(false)
const recordsDialogVisible = ref(false)
const currentIssue = ref<any>(null)
const missingRecords = ref<any[]>([])
const recordColumns = ref<string[]>([])
const missingRecordsTotal = ref(0)
const recordsPage = ref(1)
const recordsPageSize = ref(20)
const currentPage = ref(1)
const pageSize = ref(15)
const trendPeriod = ref('weekly')

const filters = reactive({
  keyword: '',
  table: '',
  severity: '',
  status: ''
})

const handleForm = reactive({
  action: 'fill_default',
  defaultValue: '',
  sourceQuery: '',
  comment: ''
})

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'Total Missing Issues', value: 24, trend: -8, icon: 'Warning', bgColor: '#f56c6c', key: 'total' },
  { title: 'Open Issues', value: 12, trend: -15, icon: 'Clock', bgColor: '#e6a23c', key: 'open' },
  { title: 'Resolved', value: 8, trend: 20, icon: 'Checked', bgColor: '#67c23a', key: 'resolved' },
  { title: 'Avg Missing Rate', value: '4.2%', trend: -1.5, icon: 'TrendCharts', bgColor: '#409eff', key: 'rate' }
])

const missingIssues = ref([
  {
    id: 1,
    table: 'device_master',
    column: 'location',
    missingCount: 12450,
    totalRows: 125000,
    missingRate: 9.96,
    severity: 'High',
    status: 'Open',
    detectedAt: '2024-01-15',
    lastUpdated: '2024-01-15',
    description: 'Location field missing for 10% of devices, affecting asset tracking and maintenance scheduling',
    suggestedAction: 'Populate location data from installation records or default to "Unknown"',
    sampleRecords: [
      { id: 'DEV-001', value: 'NULL', expected: 'Building A - Floor 3' },
      { id: 'DEV-045', value: 'NULL', expected: 'Building B - Server Room' },
      { id: 'DEV-078', value: 'NULL', expected: 'Building C - Cooling Tower' }
    ]
  },
  {
    id: 2,
    table: 'energy_consumption',
    column: 'cost_usd',
    missingCount: 5678,
    totalRows: 89000,
    missingRate: 6.38,
    severity: 'High',
    status: 'In Progress',
    detectedAt: '2024-01-10',
    lastUpdated: '2024-01-18',
    description: 'Cost field missing for energy consumption records, impacting financial reporting',
    suggestedAction: 'Calculate cost based on consumption and rate tables',
    sampleRecords: [
      { id: 'REC-1023', value: 'NULL', expected: '45.50' },
      { id: 'REC-2045', value: 'NULL', expected: '123.75' }
    ]
  },
  {
    id: 3,
    table: 'customer_contract',
    column: 'signature_date',
    missingCount: 345,
    totalRows: 12500,
    missingRate: 2.76,
    severity: 'Medium',
    status: 'Open',
    detectedAt: '2024-01-05',
    lastUpdated: '2024-01-12',
    description: 'Signature date missing for some contracts, affecting legal compliance',
    suggestedAction: 'Flag as incomplete and require update from sales team',
    sampleRecords: [
      { id: 'CT-089', value: 'NULL', expected: '2024-01-01' }
    ]
  },
  {
    id: 4,
    table: 'maintenance_work_orders',
    column: 'completion_date',
    missingCount: 2345,
    totalRows: 45678,
    missingRate: 5.13,
    severity: 'Medium',
    status: 'Open',
    detectedAt: '2024-01-08',
    lastUpdated: '2024-01-15',
    description: 'Completion date missing for open work orders, affecting SLA tracking',
    suggestedAction: 'Set to estimated completion date or leave as NULL',
    sampleRecords: [
      { id: 'WO-0456', value: 'NULL', expected: '2024-01-20' }
    ]
  },
  {
    id: 5,
    table: 'device_master',
    column: 'install_date',
    missingCount: 23400,
    totalRows: 125000,
    missingRate: 18.72,
    severity: 'Critical',
    status: 'Open',
    detectedAt: '2024-01-12',
    lastUpdated: '2024-01-16',
    description: 'Install date missing for 19% of devices, affecting warranty and lifecycle management',
    suggestedAction: 'Backfill from purchase records or flag as unknown',
    sampleRecords: [
      { id: 'DEV-112', value: 'NULL', expected: '2022-06-15' },
      { id: 'DEV-234', value: 'NULL', expected: '2023-01-10' }
    ]
  },
  {
    id: 6,
    table: 'energy_consumption',
    column: 'building_id',
    missingCount: 8900,
    totalRows: 89000,
    missingRate: 10.0,
    severity: 'High',
    status: 'Resolved',
    detectedAt: '2024-01-02',
    lastUpdated: '2024-01-14',
    description: 'Building ID missing for consumption records',
    suggestedAction: 'Mapped from device location data',
    sampleRecords: []
  }
])

// ==================== Computed ====================
const filteredIssues = computed(() => {
  let filtered = [...missingIssues.value]

  if (filters.keyword) {
    filtered = filtered.filter(i =>
        i.table.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        i.column.toLowerCase().includes(filters.keyword.toLowerCase())
    )
  }

  if (filters.table) {
    filtered = filtered.filter(i => i.table === filters.table)
  }

  if (filters.severity) {
    filtered = filtered.filter(i => i.severity === filters.severity)
  }

  if (filters.status) {
    filtered = filtered.filter(i => i.status === filters.status)
  }

  return filtered
})

const paginatedIssues = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredIssues.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getMissingRateColor = (rate: number) => {
  if (rate <= 5) return '#67c23a'
  if (rate <= 10) return '#e6a23c'
  return '#f56c6c'
}

const getSeverityTag = (severity: string) => {
  const map: Record<string, string> = {
    'Critical': 'danger',
    'High': 'warning',
    'Medium': 'info',
    'Low': 'success'
  }
  return map[severity] || 'info'
}

const getStatusTag = (status: string) => {
  const map: Record<string, string> = {
    'Open': 'danger',
    'In Progress': 'warning',
    'Resolved': 'success'
  }
  return map[status] || 'info'
}

// ==================== Chart Initializations ====================
const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)

  const weeklyData = [345, 378, 412, 398, 445, 467, 423, 456, 489, 467, 445, 423]
  const monthlyData = [1456, 1678, 1890, 1756, 1987, 2109, 2056, 1987]
  const data = trendPeriod.value === 'weekly' ? weeklyData : monthlyData
  const xAxisData = trendPeriod.value === 'weekly'
      ? ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8', 'Week 9', 'Week 10', 'Week 11', 'Week 12']
      : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug']

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: { type: 'value', name: 'Missing Records' },
    series: [{
      type: 'line',
      data: data,
      smooth: true,
      lineStyle: { width: 3, color: '#f56c6c' },
      areaStyle: { opacity: 0.1, color: '#f56c6c' },
      symbolSize: 8
    }]
  }

  trendChart.setOption(option)
  window.addEventListener('resize', () => trendChart?.resize())
}

const initTableChart = () => {
  if (!tableChartRef.value) return
  if (tableChart) tableChart.dispose()

  tableChart = echarts.init(tableChartRef.value)

  const tableData = [
    { name: 'device_master', rate: 9.96 },
    { name: 'energy_consumption', rate: 6.38 },
    { name: 'customer_contract', rate: 2.76 },
    { name: 'maintenance_wo', rate: 5.13 }
  ]

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}: {c}% missing rate' },
    grid: { left: '15%', containLabel: true },
    xAxis: { type: 'value', name: 'Missing Rate (%)', max: 25 },
    yAxis: { type: 'category', data: tableData.map(d => d.name), axisLabel: { fontSize: 11 } },
    series: [{
      type: 'bar',
      data: tableData.map(d => d.rate),
      itemStyle: {
        borderRadius: [0, 4, 4, 0],
        color: (params: any) => {
          const rate = params.data
          if (rate <= 5) return '#67c23a'
          if (rate <= 10) return '#e6a23c'
          return '#f56c6c'
        }
      },
      label: { show: true, position: 'right', formatter: '{c}%' }
    }]
  }

  tableChart.setOption(option)
  window.addEventListener('resize', () => tableChart?.resize())
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleResetFilters = () => {
  filters.keyword = ''
  filters.table = ''
  filters.severity = ''
  filters.status = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredIssues.value.length} missing data issues...`)
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const handleScan = () => {
  ElMessage.info('Starting comprehensive missing data scan...')
  setTimeout(() => {
    ElMessage.success('Scan completed. Found 3 new missing data issues.')
  }, 3000)
}

const fetchIssues = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Issues refreshed')
  }, 500)
}

const viewDetails = (issue: any) => {
  currentIssue.value = issue
  detailsDialogVisible.value = true
}

const handleIssue = (issue: any) => {
  currentIssue.value = issue
  handleForm.action = 'fill_default'
  handleForm.defaultValue = ''
  handleForm.sourceQuery = ''
  handleForm.comment = ''
  handleDialogVisible.value = true
}

const submitHandle = () => {
  ElMessage.success(`Applying fix for ${currentIssue.value?.table}.${currentIssue.value?.column}`)
  handleDialogVisible.value = false
  // Update issue status
  const index = missingIssues.value.findIndex(i => i.id === currentIssue.value?.id)
  if (index !== -1) {
    missingIssues.value[index].status = 'In Progress'
  }
}

const viewRecords = (issue: any) => {
  currentIssue.value = issue
  recordsDialogVisible.value = true
  loadMissingRecords()
}

const loadMissingRecords = () => {
  recordsLoading.value = true
  setTimeout(() => {
    // Mock data
    recordColumns.value = ['record_id', 'device_id', 'location', 'status', 'created_at']
    missingRecords.value = Array.from({ length: 20 }, (_, i) => ({
      record_id: `REC-${(recordsPage.value - 1) * 20 + i + 1}`,
      device_id: `DEV-${Math.floor(Math.random() * 1000)}`,
      location: 'NULL',
      status: 'active',
      created_at: '2024-01-01'
    }))
    missingRecordsTotal.value = 12450
    recordsLoading.value = false
  }, 500)
}

const exportMissingRecords = () => {
  ElMessage.success('Exporting missing records...')
}

const fillMissing = (record: any) => {
  ElMessage.success(`Filling missing value for record ${record.id}`)
}

const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {}

// ==================== Loading Simulation ====================
const initCharts = async () => {
  await nextTick()
  setTimeout(() => {
    initTrendChart()
    initTableChart()
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
      fetchIssues()
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
.missing-data-page {
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

.chart-row {
  margin-bottom: 20px;
}

.trend-card, .distribution-card {
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

.bar-chart-container {
  width: 100%;
  height: 300px;
}

.filter-card {
  margin-bottom: 20px;

  .filter-container {
    .filter-row {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
    }
  }
}

.table-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .table-actions {
    display: flex;
    gap: 8px;
    align-items: center;
  }
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.issue-details {
  .sample-records {
    margin-top: 20px;

    h4 {
      margin-bottom: 12px;
      color: #303133;
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