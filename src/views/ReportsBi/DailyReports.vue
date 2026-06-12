<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Search, Refresh, Document, Download, Printer,
  Share, Star, Clock, Warning, CircleCheck,
  TrendCharts, DataLine, Calendar, Setting,
  Plus, Upload, Filter, ArrowUp, ArrowDown
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Loading report templates...',
  'Fetching daily data...',
  'Generating reports...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedDate = ref('')
const selectedCategory = ref('all')
const reportPreviewVisible = ref(false)
const generateReportVisible = ref(false)
const chartRef = ref(null)

let trendChart: echarts.ECharts | null = null

// Date range presets
const datePresets = [
  { label: 'Today', value: 'today' },
  { label: 'Yesterday', value: 'yesterday' },
  { label: 'This Week', value: 'week' },
  { label: 'This Month', value: 'month' }
]

// Report categories
const reportCategories = [
  { value: 'all', label: 'All Reports', icon: '📊' },
  { value: 'system', label: 'System Health', icon: '🏥' },
  { value: 'energy', label: 'Energy', icon: '⚡' },
  { value: 'alarms', label: 'Alarms', icon: '🔔' },
  { value: 'maintenance', label: 'Maintenance', icon: '🔧' }
]

// Daily reports data
const dailyReports = ref([
  {
    id: 'RPT001', title: 'System Health Report', category: 'system', date: '2024-01-15',
    summary: 'All systems operational. 2 devices in warning state.',
    metrics: { healthScore: 98.5, uptime: 99.9, incidents: 2 },
    status: 'good', author: 'System', downloads: 45, views: 128,
    tags: ['health', 'monitoring', 'overview']
  },
  {
    id: 'RPT002', title: 'Energy Consumption Analysis', category: 'energy', date: '2024-01-15',
    summary: 'Total consumption: 12,450 kWh. 5.2% reduction from yesterday.',
    metrics: { consumption: 12450, savings: 5.2, peak: 1450 },
    status: 'good', author: 'Energy Team', downloads: 32, views: 89,
    tags: ['energy', 'sustainability', 'cost']
  },
  {
    id: 'RPT003', title: 'Alarms Summary', category: 'alarms', date: '2024-01-15',
    summary: '8 active alarms. 2 critical, 3 high priority.',
    metrics: { active: 8, critical: 2, resolved: 15 },
    status: 'warning', author: 'Security Team', downloads: 28, views: 76,
    tags: ['alarms', 'incidents', 'security']
  },
  {
    id: 'RPT004', title: 'Maintenance Activity Log', category: 'maintenance', date: '2024-01-15',
    summary: '5 work orders completed. Average response time: 45 min.',
    metrics: { completed: 5, avgResponse: 45, pending: 3 },
    status: 'good', author: 'Maintenance Team', downloads: 18, views: 52,
    tags: ['maintenance', 'work-orders', 'service']
  },
  {
    id: 'RPT005', title: 'Device Performance Report', category: 'system', date: '2024-01-14',
    summary: '156 devices online. 98.7% overall reliability.',
    metrics: { online: 156, reliability: 98.7, offline: 2 },
    status: 'good', author: 'System', downloads: 38, views: 95,
    tags: ['devices', 'performance', 'reliability']
  },
  {
    id: 'RPT006', title: 'Carbon Footprint Report', category: 'energy', date: '2024-01-14',
    summary: 'CO2 emissions: 2,450 kg. 3.1% decrease vs target.',
    metrics: { co2: 2450, target: 2530, reduction: 3.1 },
    status: 'good', author: 'Sustainability', downloads: 42, views: 112,
    tags: ['carbon', 'esg', 'sustainability']
  },
  {
    id: 'RPT007', title: 'Security Audit Log', category: 'alarms', date: '2024-01-14',
    summary: '3 security events. 0 critical. All resolved.',
    metrics: { events: 3, critical: 0, resolved: 3 },
    status: 'excellent', author: 'Security Team', downloads: 25, views: 68,
    tags: ['security', 'audit', 'compliance']
  },
  {
    id: 'RPT008', title: 'Preventive Maintenance', category: 'maintenance', date: '2024-01-14',
    summary: '12 inspections completed. 98% compliance rate.',
    metrics: { inspections: 12, compliance: 98, overdue: 0 },
    status: 'excellent', author: 'Maintenance Team', downloads: 22, views: 61,
    tags: ['preventive', 'inspections', 'compliance']
  }
])

// Report statistics
const reportStats = reactive({
  total: 0,
  good: 0,
  warning: 0,
  excellent: 0,
  totalDownloads: 0,
  totalViews: 0,
  avgHealthScore: 0
})

// Generate report form
const generateForm = reactive({
  title: '',
  category: 'system',
  dateRange: 'today',
  includeCharts: true,
  includeRecommendations: true,
  format: 'pdf'
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 9,
  total: dailyReports.value.length
})

// Filtered reports
const filteredReports = computed(() => {
  let filtered = dailyReports.value
  if (searchKeyword.value) {
    filtered = filtered.filter(r =>
        r.title.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        r.summary.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        r.tags.some(t => t.includes(searchKeyword.value.toLowerCase()))
    )
  }
  if (selectedDate.value) {
    filtered = filtered.filter(r => r.date === selectedDate.value)
  }
  if (selectedCategory.value !== 'all') {
    filtered = filtered.filter(r => r.category === selectedCategory.value)
  }
  pagination.total = filtered.length
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// Available dates for filter
const availableDates = computed(() => {
  const dates = [...new Set(dailyReports.value.map(r => r.date))]
  return dates.sort().reverse()
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
        updateStats()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  trendChart = echarts.init(chartRef.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
    yAxis: { type: 'value', name: 'Reports Generated' },
    series: [{
      type: 'line',
      data: [12, 15, 18, 14, 22, 8, 6],
      smooth: true,
      lineStyle: { color: '#409EFF', width: 3 },
      areaStyle: { opacity: 0.1, color: '#409EFF' },
      symbol: 'circle',
      symbolSize: 10,
      label: { show: true, position: 'top' }
    }]
  })
}

const updateStats = () => {
  reportStats.total = dailyReports.value.length
  reportStats.good = dailyReports.value.filter(r => r.status === 'good').length
  reportStats.warning = dailyReports.value.filter(r => r.status === 'warning').length
  reportStats.excellent = dailyReports.value.filter(r => r.status === 'excellent').length
  reportStats.totalDownloads = dailyReports.value.reduce((sum, r) => sum + r.downloads, 0)
  reportStats.totalViews = dailyReports.value.reduce((sum, r) => sum + r.views, 0)

  const healthScores = dailyReports.value.map(r => r.metrics.healthScore).filter(s => s)
  if (healthScores.length > 0) {
    reportStats.avgHealthScore = Math.round(healthScores.reduce((a, b) => a + b, 0) / healthScores.length)
  }
}

const handleResize = () => {
  trendChart?.resize()
}

// ==================== Report Functions ====================
const refreshReports = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  loading.value = false
  ElMessage.success('Reports refreshed successfully')
}

const viewReport = (report: any) => {
  selectedReport.value = report
  reportPreviewVisible.value = true
}

const downloadReport = async (report: any) => {
  ElMessage.info(`Downloading ${report.title}...`)
  await new Promise(resolve => setTimeout(resolve, 1000))
  report.downloads++
  ElMessage.success(`${report.title} downloaded successfully`)
}

const shareReport = (report: any) => {
  ElMessage.success(`Share link generated for ${report.title}`)
}

const favoriteReport = (report: any) => {
  ElMessage.success(`${report.title} added to favorites`)
}

const openGenerateReport = () => {
  generateReportVisible.value = true
}

const generateReport = async () => {
  if (!generateForm.title) {
    ElMessage.warning('Please enter a report title')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1500))

  const newReport = {
    id: `RPT${String(dailyReports.value.length + 1).padStart(3, '0')}`,
    title: generateForm.title,
    category: generateForm.category,
    date: new Date().toISOString().slice(0, 10),
    summary: 'Report generated successfully',
    metrics: { healthScore: 98, uptime: 99.5, incidents: 0 },
    status: 'good',
    author: 'Current User',
    downloads: 0,
    views: 0,
    tags: ['generated', generateForm.category]
  }

  dailyReports.value.unshift(newReport)
  updateStats()
  generateReportVisible.value = false
  generateForm.title = ''
  ElMessage.success('Report generated successfully')
}

const exportAllReports = () => {
  const data = dailyReports.value.map(r => ({
    ID: r.id,
    Title: r.title,
    Category: r.category,
    Date: r.date,
    Status: r.status,
    Downloads: r.downloads,
    Views: r.views
  }))

  const csv = convertToCSV(data)
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `daily_reports_${new Date().toISOString()}.csv`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('All reports exported successfully')
}

const convertToCSV = (data: any[]) => {
  const headers = Object.keys(data[0])
  const rows = data.map(obj => headers.map(header => JSON.stringify(obj[header])).join(','))
  return [headers.join(','), ...rows].join('\n')
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
    default: return Clock
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

const getCategoryColor = (category: string) => {
  switch (category) {
    case 'system': return '#409EFF'
    case 'energy': return '#67C23A'
    case 'alarms': return '#F56C6C'
    case 'maintenance': return '#E6A23C'
    default: return '#909399'
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
          <span class="loading-title">Loading Daily Reports</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Reports & BI - Daily Reports</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="daily-reports-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Daily Reports</h1>
        <p class="page-subtitle">Monitor your system performance with daily insights</p>
      </div>
      <div class="header-right">
        <el-button type="primary" size="large" @click="openGenerateReport">
          <el-icon><Plus /></el-icon>
          Generate Report
        </el-button>
        <el-button size="large" @click="exportAllReports">
          <el-icon><Download /></el-icon>
          Export All
        </el-button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total-icon">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ reportStats.total }}</div>
          <div class="stat-label">Total Reports</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+12%</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon excellent-icon">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ reportStats.excellent }}</div>
          <div class="stat-label">Excellent</div>
        </div>
        <div class="stat-progress">
          <el-progress :percentage="(reportStats.excellent / reportStats.total) * 100" :stroke-width="4" :show-text="false" />
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon views-icon">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ reportStats.totalViews.toLocaleString() }}</div>
          <div class="stat-label">Total Views</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">↑ 8%</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon downloads-icon">
          <el-icon><Download /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ reportStats.totalDownloads.toLocaleString() }}</div>
          <div class="stat-label">Downloads</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">↑ 15%</span>
        </div>
      </div>
    </div>

    <!-- Chart Section -->
    <div class="chart-section">
      <div class="section-header">
        <h3>Report Generation Trend</h3>
        <el-button text type="primary" @click="initChart">Refresh</el-button>
      </div>
      <div ref="chartRef" class="trend-chart" style="height: 280px"></div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-bar">
      <div class="filters-left">
        <div class="search-box">
          <el-input
              v-model="searchKeyword"
              placeholder="Search reports..."
              :prefix-icon="Search"
              clearable
              style="width: 260px"
          />
        </div>
        <div class="category-filters">
          <button
              v-for="cat in reportCategories"
              :key="cat.value"
              class="category-chip"
              :class="{ active: selectedCategory === cat.value }"
              @click="selectedCategory = cat.value"
          >
            <span class="chip-icon">{{ cat.icon }}</span>
            <span>{{ cat.label }}</span>
          </button>
        </div>
      </div>
      <div class="filters-right">
        <el-select v-model="selectedDate" placeholder="Filter by date" clearable style="width: 160px">
          <el-option v-for="date in availableDates" :key="date" :label="date" :value="date" />
        </el-select>
        <el-button @click="refreshReports" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Reports Grid - Card Style -->
    <div class="reports-grid">
      <div
          v-for="report in filteredReports"
          :key="report.id"
          class="report-card"
          @click="viewReport(report)"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="card-category" :style="{ background: getCategoryColor(report.category) }">
            {{ report.category === 'system' ? '🏥' : report.category === 'energy' ? '⚡' : report.category === 'alarms' ? '🔔' : '🔧' }}
          </div>
          <div class="card-status">
            <el-tag :type="getStatusType(report.status)" size="small" effect="light">
              <el-icon><component :is="getStatusIcon(report.status)" /></el-icon>
              {{ getStatusText(report.status) }}
            </el-tag>
          </div>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <h4 class="card-title">{{ report.title }}</h4>
          <p class="card-summary">{{ report.summary }}</p>

          <!-- Metrics -->
          <div class="card-metrics">
            <div v-for="(value, key) in report.metrics" :key="key" class="metric-item">
              <span class="metric-label">{{ key }}:</span>
              <span class="metric-value">
                {{ typeof value === 'number' ? (key === 'healthScore' || key === 'reliability' || key === 'compliance' ? value + '%' : value.toLocaleString()) : value }}
              </span>
            </div>
          </div>

          <!-- Tags -->
          <div class="card-tags">
            <span v-for="tag in report.tags.slice(0, 3)" :key="tag" class="tag">{{ tag }}</span>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="footer-info">
            <span class="info-item">
              <el-icon><Calendar /></el-icon>
              {{ report.date }}
            </span>
            <span class="info-item">
              <el-icon><User /></el-icon>
              {{ report.author }}
            </span>
          </div>
          <div class="footer-stats">
            <span class="stat-item">
              <el-icon><View /></el-icon>
              {{ report.views }}
            </span>
            <span class="stat-item">
              <el-icon><Download /></el-icon>
              {{ report.downloads }}
            </span>
          </div>
        </div>

        <!-- Action Buttons (appear on hover) -->
        <div class="card-actions">
          <el-button circle size="small" @click.stop="viewReport(report)">
            <el-icon><View /></el-icon>
          </el-button>
          <el-button circle size="small" type="primary" @click.stop="downloadReport(report)">
            <el-icon><Download /></el-icon>
          </el-button>
          <el-button circle size="small" @click.stop="shareReport(report)">
            <el-icon><Share /></el-icon>
          </el-button>
          <el-button circle size="small" @click.stop="favoriteReport(report)">
            <el-icon><Star /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination-wrapper">
      <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[6, 9, 12, 18]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
      />
    </div>

    <!-- Report Preview Dialog -->
    <el-dialog v-model="reportPreviewVisible" :title="selectedReport?.title" width="800px" top="5vh">
      <div class="report-preview">
        <div class="preview-header">
          <div class="preview-meta">
            <span><el-icon><Calendar /></el-icon> {{ selectedReport?.date }}</span>
            <span><el-icon><User /></el-icon> {{ selectedReport?.author }}</span>
            <el-tag :type="getStatusType(selectedReport?.status)" size="small">
              {{ getStatusText(selectedReport?.status) }}
            </el-tag>
          </div>
          <h2>{{ selectedReport?.title }}</h2>
          <p class="preview-summary">{{ selectedReport?.summary }}</p>
        </div>

        <el-divider />

        <div class="preview-metrics">
          <h4>Key Metrics</h4>
          <div class="metrics-grid">
            <div v-for="(value, key) in selectedReport?.metrics" :key="key" class="preview-metric">
              <div class="metric-label">{{ key }}</div>
              <div class="metric-value">{{ typeof value === 'number' ? (key === 'healthScore' || key === 'reliability' ? value + '%' : value) : value }}</div>
            </div>
          </div>
        </div>

        <div class="preview-tags">
          <h4>Tags</h4>
          <div class="tags-list">
            <span v-for="tag in selectedReport?.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="reportPreviewVisible = false">Close</el-button>
        <el-button type="primary" @click="downloadReport(selectedReport)">
          <el-icon><Download /></el-icon> Download PDF
        </el-button>
        <el-button @click="shareReport(selectedReport)">
          <el-icon><Share /></el-icon> Share
        </el-button>
      </template>
    </el-dialog>

    <!-- Generate Report Dialog -->
    <el-dialog v-model="generateReportVisible" title="Generate New Report" width="500px">
      <el-form :model="generateForm" label-width="120px">
        <el-form-item label="Report Title" required>
          <el-input v-model="generateForm.title" placeholder="Enter report title" />
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="generateForm.category" style="width: 100%">
            <el-option v-for="cat in reportCategories.slice(1)" :key="cat.value" :label="cat.label" :value="cat.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Date Range">
          <el-select v-model="generateForm.dateRange" style="width: 100%">
            <el-option v-for="p in datePresets" :key="p.value" :label="p.label" :value="p.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Include Charts">
          <el-switch v-model="generateForm.includeCharts" />
        </el-form-item>
        <el-form-item label="Include Recommendations">
          <el-switch v-model="generateForm.includeRecommendations" />
        </el-form-item>
        <el-form-item label="Output Format">
          <el-radio-group v-model="generateForm.format">
            <el-radio value="pdf">PDF</el-radio>
            <el-radio value="excel">Excel</el-radio>
            <el-radio value="csv">CSV</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="generateReportVisible = false">Cancel</el-button>
        <el-button type="primary" @click="generateReport">Generate Report</el-button>
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
.daily-reports-container {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #eef2f6 100%);
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #1e293b 0%, #2d3a4e 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.header-right {
  display: flex;
  gap: 12px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 28px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.total-icon {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #409eff;
}

.excellent-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.views-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.downloads-icon {
  background: linear-gradient(135deg, #fef0f0 0%, #fcd9d9 100%);
  color: #f56c6c;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  margin-top: 4px;
}

.stat-trend {
  position: absolute;
  top: 16px;
  right: 16px;
}

.trend-up {
  font-size: 12px;
  color: #67c23a;
  background: #f0f9ff;
  padding: 4px 8px;
  border-radius: 20px;
}

.stat-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
}

/* Chart Section */
.chart-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 28px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.trend-chart {
  width: 100%;
}

/* Filters Bar */
.filters-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 24px;
}

.filters-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.category-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.category-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 40px;
  font-size: 13px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s ease;
}

.category-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.category-chip.active {
  background: #409eff;
  border-color: #409eff;
  color: white;
}

.chip-icon {
  font-size: 14px;
}

.filters-right {
  display: flex;
  gap: 12px;
}

/* Reports Grid */
.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.report-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.report-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 30px -12px rgba(0, 0, 0, 0.15);
}

.report-card:hover .card-actions {
  opacity: 1;
}

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 0 20px;
}

.card-category {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
}

/* Card Body */
.card-body {
  padding: 16px 20px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 10px 0;
  line-height: 1.4;
}

.card-summary {
  font-size: 14px;
  color: #64748b;
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.card-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
  padding: 12px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.metric-item {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.metric-label {
  font-size: 12px;
  color: #909399;
  text-transform: capitalize;
}

.metric-value {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  font-size: 11px;
  padding: 4px 10px;
  background: #f5f7fa;
  border-radius: 20px;
  color: #606266;
}

/* Card Footer */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px 16px 20px;
  border-top: 1px solid #f0f0f0;
  background: #fafbfc;
}

.footer-info {
  display: flex;
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
}

.footer-stats {
  display: flex;
  gap: 12px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #606266;
}

/* Card Actions (Hover) */
.card-actions {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  gap: 12px;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  padding: 12px 20px;
  border-radius: 60px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.card-actions .el-button {
  background: white;
  border: none;
}

.card-actions .el-button:hover {
  transform: scale(1.1);
}

/* Pagination */
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
}

/* Report Preview */
.report-preview {
  max-height: 60vh;
  overflow-y: auto;
}

.preview-header {
  text-align: center;
  margin-bottom: 24px;
}

.preview-meta {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #909399;
}

.preview-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.preview-header h2 {
  font-size: 24px;
  margin: 0 0 12px 0;
}

.preview-summary {
  font-size: 14px;
  color: #64748b;
  line-height: 1.6;
}

.preview-metrics h4,
.preview-tags h4 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px 0;
  color: #1e293b;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.preview-metric {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 12px;
  text-align: center;
}

.preview-metric .metric-label {
  font-size: 12px;
  color: #909399;
  text-transform: capitalize;
  margin-bottom: 4px;
}

.preview-metric .metric-value {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .reports-grid {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }
}

@media (max-width: 768px) {
  .daily-reports-container {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filters-left {
    flex-direction: column;
  }

  .category-filters {
    justify-content: center;
  }

  .page-header {
    flex-direction: column;
    text-align: center;
  }

  .header-right {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .reports-grid {
    grid-template-columns: 1fr;
  }
}
</style>