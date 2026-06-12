<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Search, Refresh, Connection, Setting, DataLine,
  Document, CircleCheck, CircleClose, Loading,
  TrendCharts, Monitor, Aim, Clock, Timer,
  Warning, DataAnalysis, Histogram, Download,
  Printer, Share, Star, Tickets
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing report generator...',
  'Collecting health data...',
  'Generating report templates...',
  'Compiling statistics...',
  'Almost ready...'
]

// ==================== Component State ====================
const generating = ref(false)
const searchKeyword = ref('')
const selectedReportType = ref('all')
const selectedSeverity = ref('all')
const reportPreviewVisible = ref(false)
const scheduleReportVisible = ref(false)
const chartRef = ref(null)
const trendChartRef = ref(null)

let healthChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null

// Report types
const reportTypes = [
  { value: 'all', label: 'All Reports' },
  { value: 'daily', label: 'Daily Reports' },
  { value: 'weekly', label: 'Weekly Reports' },
  { value: 'monthly', label: 'Monthly Reports' },
  { value: 'quarterly', label: 'Quarterly Reports' }
]

// Health reports
const reports = ref([
  {
    id: 'RPT001', name: 'Daily Health Report - 2024-01-15', type: 'daily', date: '2024-01-15',
    summary: 'System health at 98.2%, 2 critical issues found', status: 'good',
    totalDevices: 12, healthyDevices: 10, warningDevices: 1, criticalDevices: 1,
    avgLatency: 24.5, avgReliability: 98.2, generatedBy: 'System',
    recommendations: ['Check Lighting Panel L1 latency', 'Investigate Fire Alarm Panel']
  },
  {
    id: 'RPT002', name: 'Daily Health Report - 2024-01-14', type: 'daily', date: '2024-01-14',
    summary: 'System health at 98.5%, 1 critical issue found', status: 'good',
    totalDevices: 12, healthyDevices: 11, warningDevices: 0, criticalDevices: 1,
    avgLatency: 23.8, avgReliability: 98.5, generatedBy: 'System',
    recommendations: ['Monitor Fire Alarm Panel performance']
  },
  {
    id: 'RPT003', name: 'Weekly Health Report - Week 2', type: 'weekly', date: '2024-01-08/2024-01-14',
    summary: 'Overall system stable, slight performance degradation', status: 'warning',
    totalDevices: 12, healthyDevices: 10, warningDevices: 1, criticalDevices: 1,
    avgLatency: 25.2, avgReliability: 98.0, generatedBy: 'System',
    recommendations: ['Schedule maintenance for Lighting Panel', 'Review network configuration']
  },
  {
    id: 'RPT004', name: 'Monthly Health Report - December 2024', type: 'monthly', date: '2024-12-01/2024-12-31',
    summary: 'Monthly performance within acceptable range', status: 'good',
    totalDevices: 12, healthyDevices: 11, warningDevices: 0, criticalDevices: 1,
    avgLatency: 24.0, avgReliability: 98.3, generatedBy: 'System',
    recommendations: ['Plan for preventive maintenance in January']
  },
  {
    id: 'RPT005', name: 'Quarterly Health Report - Q4 2024', type: 'quarterly', date: '2024-10-01/2024-12-31',
    summary: 'Quarterly report shows 2.5% improvement in overall reliability', status: 'good',
    totalDevices: 12, healthyDevices: 11, warningDevices: 0, criticalDevices: 1,
    avgLatency: 23.5, avgReliability: 98.7, generatedBy: 'System',
    recommendations: ['Continue current maintenance schedule']
  },
  {
    id: 'RPT006', name: 'Daily Health Report - 2024-01-13', type: 'daily', date: '2024-01-13',
    summary: 'All systems operational, no critical issues', status: 'excellent',
    totalDevices: 12, healthyDevices: 12, warningDevices: 0, criticalDevices: 0,
    avgLatency: 22.8, avgReliability: 99.1, generatedBy: 'System',
    recommendations: []
  },
  {
    id: 'RPT007', name: 'Weekly Health Report - Week 1', type: 'weekly', date: '2024-01-01/2024-01-07',
    summary: 'Good week with 99%+ reliability', status: 'excellent',
    totalDevices: 12, healthyDevices: 12, warningDevices: 0, criticalDevices: 0,
    avgLatency: 22.5, avgReliability: 99.2, generatedBy: 'System',
    recommendations: []
  }
])

// Health metrics over time
const healthMetrics = ref([
  { date: '2024-01-01', healthScore: 98.5, latency: 22, reliability: 98.5, incidents: 0 },
  { date: '2024-01-02', healthScore: 98.8, latency: 21, reliability: 98.8, incidents: 0 },
  { date: '2024-01-03', healthScore: 99.0, latency: 21, reliability: 99.0, incidents: 0 },
  { date: '2024-01-04', healthScore: 98.9, latency: 22, reliability: 98.9, incidents: 0 },
  { date: '2024-01-05', healthScore: 98.7, latency: 22, reliability: 98.7, incidents: 0 },
  { date: '2024-01-06', healthScore: 98.5, latency: 23, reliability: 98.5, incidents: 1 },
  { date: '2024-01-07', healthScore: 98.4, latency: 24, reliability: 98.4, incidents: 0 },
  { date: '2024-01-08', healthScore: 98.2, latency: 24, reliability: 98.2, incidents: 1 },
  { date: '2024-01-09', healthScore: 98.3, latency: 23, reliability: 98.3, incidents: 0 },
  { date: '2024-01-10', healthScore: 98.1, latency: 25, reliability: 98.1, incidents: 0 },
  { date: '2024-01-11', healthScore: 97.9, latency: 26, reliability: 97.9, incidents: 1 },
  { date: '2024-01-12', healthScore: 98.0, latency: 25, reliability: 98.0, incidents: 0 },
  { date: '2024-01-13', healthScore: 99.1, latency: 22, reliability: 99.1, incidents: 0 },
  { date: '2024-01-14', healthScore: 98.5, latency: 24, reliability: 98.5, incidents: 1 },
  { date: '2024-01-15', healthScore: 98.2, latency: 25, reliability: 98.2, incidents: 2 }
])

// Report statistics
const reportStats = reactive({
  total: 0,
  daily: 0,
  weekly: 0,
  monthly: 0,
  quarterly: 0,
  avgHealthScore: 0,
  totalIncidents: 0,
  criticalIssues: 0
})

// Scheduled report config
const scheduleConfig = reactive({
  name: '',
  type: 'daily',
  format: 'pdf',
  recipients: '',
  scheduleTime: '08:00',
  includeCharts: true,
  includeRecommendations: true
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: reports.value.length
})

// Filtered reports
const filteredReports = computed(() => {
  let filtered = reports.value
  if (searchKeyword.value) {
    filtered = filtered.filter(r =>
        r.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        r.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        r.summary.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedReportType.value !== 'all') {
    filtered = filtered.filter(r => r.type === selectedReportType.value)
  }
  if (selectedSeverity.value !== 'all') {
    filtered = filtered.filter(r => r.status === selectedSeverity.value)
  }
  pagination.total = filtered.length
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// ==================== Loading Simulation ====================
onMounted(() => {
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 12 + 4
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
      setTimeout(() => {
        initChart()
        initTrendChart()
        updateStats()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  healthChart = echarts.init(chartRef.value)
  healthChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Health Score (%)', 'Reliability (%)'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: healthMetrics.value.map(m => m.date).slice(-7) },
    yAxis: { type: 'value', name: 'Percentage (%)', min: 95, max: 100 },
    series: [
      { name: 'Health Score (%)', type: 'line', data: healthMetrics.value.map(m => m.healthScore).slice(-7), smooth: true, lineStyle: { color: '#409EFF', width: 2 }, areaStyle: { opacity: 0.1, color: '#409EFF' }, symbol: 'circle', symbolSize: 8 },
      { name: 'Reliability (%)', type: 'line', data: healthMetrics.value.map(m => m.reliability).slice(-7), smooth: true, lineStyle: { color: '#67C23A', width: 2 }, symbol: 'diamond', symbolSize: 8 }
    ]
  })
}

const initTrendChart = () => {
  if (!trendChartRef.value) return

  trendChart = echarts.init(trendChartRef.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Health Score', 'Latency (ms)'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: healthMetrics.value.map(m => m.date) },
    yAxis: [
      { type: 'value', name: 'Health Score (%)', min: 95, max: 100 },
      { type: 'value', name: 'Latency (ms)', min: 0, max: 50 }
    ],
    series: [
      { name: 'Health Score', type: 'line', data: healthMetrics.value.map(m => m.healthScore), smooth: true, lineStyle: { color: '#409EFF', width: 2 }, areaStyle: { opacity: 0.1, color: '#409EFF' }, symbol: 'circle', symbolSize: 6 },
      { name: 'Latency (ms)', type: 'line', data: healthMetrics.value.map(m => m.latency), smooth: true, lineStyle: { color: '#E6A23C', width: 2 }, symbol: 'diamond', symbolSize: 6, yAxisIndex: 1 }
    ]
  })
}

const updateStats = () => {
  reportStats.total = reports.value.length
  reportStats.daily = reports.value.filter(r => r.type === 'daily').length
  reportStats.weekly = reports.value.filter(r => r.type === 'weekly').length
  reportStats.monthly = reports.value.filter(r => r.type === 'monthly').length
  reportStats.quarterly = reports.value.filter(r => r.type === 'quarterly').length

  const avgHealth = healthMetrics.value.reduce((a, b) => a + b.healthScore, 0) / healthMetrics.value.length
  reportStats.avgHealthScore = parseFloat(avgHealth.toFixed(1))
  reportStats.totalIncidents = healthMetrics.value.reduce((a, b) => a + b.incidents, 0)
  reportStats.criticalIssues = reports.value.filter(r => r.criticalDevices > 0).length
}

const handleResize = () => {
  healthChart?.resize()
  trendChart?.resize()
}

// ==================== Report Functions ====================
const generateReport = async () => {
  generating.value = true
  await new Promise(resolve => setTimeout(resolve, 2000))

  const newReport = {
    id: `RPT${String(reports.value.length + 1).padStart(3, '0')}`,
    name: `Daily Health Report - ${new Date().toISOString().slice(0, 10)}`,
    type: 'daily',
    date: new Date().toISOString().slice(0, 10),
    summary: 'New health report generated successfully',
    status: 'good',
    totalDevices: 12,
    healthyDevices: 11,
    warningDevices: 1,
    criticalDevices: 0,
    avgLatency: 23.5,
    avgReliability: 98.8,
    generatedBy: 'User',
    recommendations: ['Monitor system performance']
  }

  reports.value.unshift(newReport)
  updateStats()
  generating.value = false
  ElMessage.success('Health report generated successfully')
}

const viewReport = (report: any) => {
  selectedReport.value = report
  reportPreviewVisible.value = true
}

const downloadReport = async (report: any) => {
  ElMessage.info(`Downloading ${report.name}...`)
  await new Promise(resolve => setTimeout(resolve, 1000))
  ElMessage.success(`${report.name} downloaded successfully`)
}

const shareReport = (report: any) => {
  ElMessage.info(`Share link generated for ${report.name}`)
}

const scheduleReport = () => {
  scheduleReportVisible.value = true
}

const saveSchedule = async () => {
  await new Promise(resolve => setTimeout(resolve, 1000))
  ElMessage.success(`Report scheduled: ${scheduleConfig.name} will be sent daily at ${scheduleConfig.scheduleTime}`)
  scheduleReportVisible.value = false
}

const exportAllReports = async () => {
  ElMessage.info('Exporting all reports...')
  await new Promise(resolve => setTimeout(resolve, 1500))
  ElMessage.success('All reports exported successfully')
}

const deleteReport = async (report: any) => {
  await ElMessageBox.confirm(`Delete report ${report.name}?`, 'Confirm Delete', {
    confirmButtonText: 'Delete',
    cancelButtonText: 'Cancel',
    type: 'warning'
  })

  const index = reports.value.findIndex(r => r.id === report.id)
  if (index !== -1) {
    reports.value.splice(index, 1)
    updateStats()
    ElMessage.success('Report deleted successfully')
  }
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'excellent': return CircleCheck
    case 'good': return CircleCheck
    case 'warning': return Warning
    default: return CircleClose
  }
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'excellent': return 'success'
    case 'good': return 'success'
    case 'warning': return 'warning'
    default: return 'danger'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'excellent': return 'Excellent'
    case 'good': return 'Good'
    case 'warning': return 'Warning'
    default: return 'Critical'
  }
}

const selectedReport = ref<any>(null)
</script>

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
          <span class="loading-title">Loading Health Reports</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Protocol Health Check - Health Reports</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="health-reports-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h2>Health Reports</h2>
        <el-tag type="warning" effect="dark">Protocol Health Check</el-tag>
      </div>
      <div class="header-stats">
        <el-tag type="info" effect="plain">Daily | Weekly | Monthly | Quarterly</el-tag>
      </div>
    </div>

    <!-- Control Panel -->
    <el-card shadow="never" class="control-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="5">
          <el-select v-model="selectedReportType" placeholder="Report Type" style="width: 100%">
            <el-option v-for="t in reportTypes" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-select v-model="selectedSeverity" placeholder="Status" clearable style="width: 100%">
            <el-option label="All" value="all" />
            <el-option label="Excellent" value="excellent" />
            <el-option label="Good" value="good" />
            <el-option label="Warning" value="warning" />
            <el-option label="Critical" value="critical" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-input v-model="searchKeyword" placeholder="Search reports..." :prefix-icon="Search" clearable />
        </el-col>
        <el-col :span="6">
          <div class="control-buttons">
            <el-button type="primary" @click="generateReport" :loading="generating">
              <el-icon><Document /></el-icon> Generate Report
            </el-button>
            <el-button @click="scheduleReport">
              <el-icon><Clock /></el-icon> Schedule
            </el-button>
            <el-button @click="exportAllReports">
              <el-icon><Download /></el-icon> Export All
            </el-button>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- Statistics Cards -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon total-icon">
            <el-icon><Tickets /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ reportStats.total }}</div>
            <div class="stat-label">Total Reports</div>
            <div class="stat-sub-value">{{ reportStats.daily }} Daily | {{ reportStats.weekly }} Weekly</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon health-icon">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ reportStats.avgHealthScore }}%</div>
            <div class="stat-label">Avg Health Score</div>
            <el-progress :percentage="reportStats.avgHealthScore" :color="'#67C23A'" :stroke-width="6" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon incident-icon">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ reportStats.totalIncidents }}</div>
            <div class="stat-label">Total Incidents (15d)</div>
            <div class="stat-sub-value">{{ reportStats.criticalIssues }} Critical Issues</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon monthly-icon">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ reportStats.monthly }}</div>
            <div class="stat-label">Monthly Reports</div>
            <div class="stat-sub-value">{{ reportStats.quarterly }} Quarterly</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Chart Section -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Health Score & Reliability (Last 7 Days)</span>
              <el-button text type="primary" @click="initChart">Refresh</el-button>
            </div>
          </template>
          <div ref="chartRef" class="chart" style="height: 300px"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Health Score vs Latency Trend (15 Days)</span>
              <el-button text type="primary" @click="initTrendChart">Refresh</el-button>
            </div>
          </template>
          <div ref="trendChartRef" class="chart" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Reports Table -->
    <el-card shadow="never" class="reports-card">
      <template #header>
        <div class="table-header">
          <span>Generated Reports</span>
          <div class="table-actions">
            <el-button type="primary" size="small" @click="generateReport" :loading="generating">
              New Report
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredReports" stripe style="width: 100%">
        <el-table-column prop="id" label="Report ID" width="90" />
        <el-table-column prop="name" label="Report Name" min-width="220" />
        <el-table-column prop="type" label="Type" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.type === 'daily' ? 'info' : row.type === 'weekly' ? 'primary' : row.type === 'monthly' ? 'success' : 'warning'">
              {{ row.type.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="date" label="Date/Period" width="160" />
        <el-table-column label="Status" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              <el-icon style="margin-right: 4px"><component :is="getStatusIcon(row.status)" /></el-icon>
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Devices" width="140" align="center">
          <template #default="{ row }">
            <div class="device-stats">
              <span class="healthy">{{ row.healthyDevices }}</span> /
              <span class="warning">{{ row.warningDevices }}</span> /
              <span class="critical">{{ row.criticalDevices }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Avg Latency" width="100" align="center">
          <template #default="{ row }">
            {{ row.avgLatency }}ms
          </template>
        </el-table-column>
        <el-table-column label="Reliability" width="100" align="center">
          <template #default="{ row }">
            {{ row.avgReliability }}%
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewReport(row)">
              View
            </el-button>
            <el-button link type="success" size="small" @click="downloadReport(row)">
              <el-icon><Download /></el-icon>
            </el-button>
            <el-button link type="info" size="small" @click="shareReport(row)">
              <el-icon><Share /></el-icon>
            </el-button>
            <el-button link type="danger" size="small" @click="deleteReport(row)">
              Delete
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- Report Preview Dialog -->
    <el-dialog v-model="reportPreviewVisible" :title="selectedReport?.name" width="800px" top="5vh">
      <div class="report-preview">
        <div class="report-header">
          <h3>Protocol Health Check Report</h3>
          <div class="report-meta">
            <span>Report ID: {{ selectedReport?.id }}</span>
            <span>Generated: {{ selectedReport?.date }}</span>
            <span>Type: {{ selectedReport?.type?.toUpperCase() }}</span>
          </div>
        </div>

        <el-divider />

        <div class="report-summary">
          <h4>Executive Summary</h4>
          <p>{{ selectedReport?.summary }}</p>
        </div>

        <el-row :gutter="20" class="report-stats">
          <el-col :span="6">
            <div class="stat-box">
              <div class="stat-value">{{ selectedReport?.totalDevices }}</div>
              <div class="stat-label">Total Devices</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-box">
              <div class="stat-value">{{ selectedReport?.healthyDevices }}</div>
              <div class="stat-label">Healthy</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-box">
              <div class="stat-value">{{ selectedReport?.warningDevices }}</div>
              <div class="stat-label">Warning</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-box">
              <div class="stat-value">{{ selectedReport?.criticalDevices }}</div>
              <div class="stat-label">Critical</div>
            </div>
          </el-col>
        </el-row>

        <el-divider />

        <div class="report-metrics">
          <h4>Key Metrics</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="Average Latency">{{ selectedReport?.avgLatency }}ms</el-descriptions-item>
            <el-descriptions-item label="Average Reliability">{{ selectedReport?.avgReliability }}%</el-descriptions-item>
            <el-descriptions-item label="Generated By">{{ selectedReport?.generatedBy }}</el-descriptions-item>
            <el-descriptions-item label="Status">
              <el-tag :type="getStatusType(selectedReport?.status)" size="small">
                {{ getStatusText(selectedReport?.status) }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div v-if="selectedReport?.recommendations?.length" class="report-recommendations">
          <el-divider />
          <h4>Recommendations</h4>
          <ul>
            <li v-for="rec in selectedReport.recommendations" :key="rec">{{ rec }}</li>
          </ul>
        </div>
      </div>

      <template #footer>
        <el-button @click="reportPreviewVisible = false">Close</el-button>
        <el-button type="primary" @click="downloadReport(selectedReport)">
          <el-icon><Download /></el-icon> Download PDF
        </el-button>
        <el-button type="success" @click="shareReport(selectedReport)">
          <el-icon><Share /></el-icon> Share
        </el-button>
      </template>
    </el-dialog>

    <!-- Schedule Report Dialog -->
    <el-dialog v-model="scheduleReportVisible" title="Schedule Report" width="500px">
      <el-form :model="scheduleConfig" label-width="120px">
        <el-form-item label="Report Name">
          <el-input v-model="scheduleConfig.name" placeholder="Enter report name" />
        </el-form-item>
        <el-form-item label="Report Type">
          <el-select v-model="scheduleConfig.type" style="width: 100%">
            <el-option label="Daily" value="daily" />
            <el-option label="Weekly" value="weekly" />
            <el-option label="Monthly" value="monthly" />
          </el-select>
        </el-form-item>
        <el-form-item label="Format">
          <el-select v-model="scheduleConfig.format" style="width: 100%">
            <el-option label="PDF" value="pdf" />
            <el-option label="Excel" value="excel" />
            <el-option label="CSV" value="csv" />
          </el-select>
        </el-form-item>
        <el-form-item label="Schedule Time">
          <el-time-picker v-model="scheduleConfig.scheduleTime" format="HH:mm" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Recipients">
          <el-input v-model="scheduleConfig.recipients" placeholder="email@example.com (comma separated)" />
        </el-form-item>
        <el-form-item label="Include Charts">
          <el-switch v-model="scheduleConfig.includeCharts" />
        </el-form-item>
        <el-form-item label="Include Recommendations">
          <el-switch v-model="scheduleConfig.includeRecommendations" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="scheduleReportVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveSchedule">Schedule Report</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
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

/* ==================== Main Content ==================== */
.health-reports-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e4e7ed;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  color: #303133;
}

.control-card {
  margin-bottom: 20px;
}

.control-buttons {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 10px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
}

.total-icon {
  background-color: #e6f7ff;
  color: #409eff;
}

.health-icon {
  background-color: #f0f9ff;
  color: #67c23a;
}

.incident-icon {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.monthly-icon {
  background-color: #fef0f0;
  color: #f56c6c;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.stat-sub-value {
  font-size: 12px;
  color: #67c23a;
  margin-top: 2px;
}

.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  height: 370px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.reports-card {
  margin-top: 0;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.table-actions {
  display: flex;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.chart {
  width: 100%;
}

.device-stats {
  font-size: 13px;
}

.device-stats .healthy {
  color: #67c23a;
  font-weight: bold;
}

.device-stats .warning {
  color: #e6a23c;
  font-weight: bold;
}

.device-stats .critical {
  color: #f56c6c;
  font-weight: bold;
}

.report-preview {
  padding: 10px;
}

.report-header {
  text-align: center;
  margin-bottom: 20px;
}

.report-header h3 {
  margin: 0 0 10px 0;
  color: #303133;
}

.report-meta {
  display: flex;
  justify-content: center;
  gap: 20px;
  font-size: 12px;
  color: #909399;
}

.report-summary {
  margin-bottom: 20px;
}

.report-summary h4 {
  margin-bottom: 10px;
  color: #303133;
}

.report-stats {
  margin: 20px 0;
}

.stat-box {
  text-align: center;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.stat-box .stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-box .stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.report-metrics {
  margin-bottom: 20px;
}

.report-metrics h4 {
  margin-bottom: 10px;
  color: #303133;
}

.report-recommendations h4 {
  margin-bottom: 10px;
  color: #303133;
}

.report-recommendations ul {
  margin: 0;
  padding-left: 20px;
}

.report-recommendations li {
  margin: 8px 0;
  color: #606266;
}

:deep(.el-card__header) {
  border-bottom: 1px solid #ebeef5;
  padding: 15px 20px;
}

:deep(.el-card__body) {
  padding: 20px;
}

@media (max-width: 1200px) {
  .table-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .control-buttons {
    justify-content: flex-start;
    margin-top: 10px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .report-meta {
    flex-direction: column;
    align-items: center;
    gap: 5px;
  }
}
</style>