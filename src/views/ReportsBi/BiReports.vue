<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Search, Refresh, Document, Download, Printer,
  Share, Star, Clock, Warning, CircleCheck,
  TrendCharts, DataLine, Calendar, Setting,
  Plus, Upload, Filter, ArrowUp, ArrowDown,
  View, User, Trophy, Medal, Edit, Delete,
  CopyDocument, PieChart,
  Histogram, DataAnalysis, Connection
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Loading BI dashboards...',
  'Loading data sources...',
  'Preparing visualizations...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedType = ref('all')
const selectedDepartment = ref('all')
const dashboardVisible = ref(false)
const chartRef = ref(null)

let biChart: echarts.ECharts | null = null

// BI Report types
const reportTypes = [
  { value: 'all', label: 'All Types', icon: '📊' },
  { value: 'dashboard', label: 'Dashboards', icon: '📈' },
  { value: 'report', label: 'Reports', icon: '📋' },
  { value: 'scorecard', label: 'Scorecards', icon: '🎯' },
  { value: 'analysis', label: 'Analysis', icon: '🔍' }
]

// Departments
const departments = [
  { value: 'all', label: 'All Departments' },
  { value: 'executive', label: 'Executive' },
  { value: 'operations', label: 'Operations' },
  { value: 'finance', label: 'Finance' },
  { value: 'sales', label: 'Sales' },
  { value: 'marketing', label: 'Marketing' }
]

// BI Reports data
const biReports = ref([
  {
    id: 'BI001', name: 'Executive Dashboard', type: 'dashboard', department: 'executive',
    description: 'High-level KPIs for executive leadership including revenue, growth, and operational efficiency',
    metrics: ['Revenue', 'Profit Margin', 'Customer Satisfaction', 'Employee Engagement'],
    charts: ['line', 'gauge', 'bar'], dataSources: ['ERP', 'CRM', 'HRIS'],
    lastUpdated: '2024-01-15', views: 1234, favorites: 89, shared: 45,
    status: 'published', owner: 'BI Team', size: '2.4 MB'
  },
  {
    id: 'BI002', name: 'Operations Analytics', type: 'dashboard', department: 'operations',
    description: 'Real-time operations monitoring with production efficiency and quality metrics',
    metrics: ['Production Volume', 'Quality Rate', 'Downtime', 'Efficiency'],
    charts: ['line', 'bar', 'gauge'], dataSources: ['MES', 'SCADA', 'IoT'],
    lastUpdated: '2024-01-15', views: 892, favorites: 67, shared: 32,
    status: 'published', owner: 'Ops Team', size: '3.1 MB'
  },
  {
    id: 'BI003', name: 'Financial Performance', type: 'report', department: 'finance',
    description: 'Comprehensive financial report with P&L, balance sheet, and cash flow analysis',
    metrics: ['Revenue', 'COGS', 'Operating Expenses', 'Net Income', 'EBITDA'],
    charts: ['bar', 'line', 'area'], dataSources: ['ERP', 'Accounting'],
    lastUpdated: '2024-01-14', views: 1567, favorites: 234, shared: 78,
    status: 'published', owner: 'Finance Team', size: '4.2 MB'
  },
  {
    id: 'BI004', name: 'Sales Scorecard', type: 'scorecard', department: 'sales',
    description: 'Sales team performance scorecard with quota attainment and pipeline metrics',
    metrics: ['Quota Attainment', 'Win Rate', 'Pipeline Value', 'Avg Deal Size'],
    charts: ['gauge', 'bar', 'table'], dataSources: ['CRM', 'Sales DB'],
    lastUpdated: '2024-01-15', views: 2345, favorites: 456, shared: 123,
    status: 'published', owner: 'Sales Team', size: '1.8 MB'
  },
  {
    id: 'BI005', name: 'Marketing Analytics', type: 'analysis', department: 'marketing',
    description: 'Campaign performance analysis with ROI and engagement metrics',
    metrics: ['Campaign ROI', 'Conversion Rate', 'Cost per Lead', 'Engagement'],
    charts: ['line', 'pie', 'bar'], dataSources: ['Google Analytics', 'CRM', 'Social Media'],
    lastUpdated: '2024-01-13', views: 678, favorites: 89, shared: 34,
    status: 'published', owner: 'Marketing Team', size: '2.9 MB'
  },
  {
    id: 'BI006', name: 'Supply Chain Dashboard', type: 'dashboard', department: 'operations',
    description: 'Supply chain visibility dashboard with inventory, logistics, and supplier metrics',
    metrics: ['Inventory Turnover', 'Order Fulfillment', 'Supplier Performance', 'Logistics Cost'],
    charts: ['bar', 'line', 'map'], dataSources: ['SCM', 'WMS', 'TMS'],
    lastUpdated: '2024-01-12', views: 456, favorites: 45, shared: 23,
    status: 'draft', owner: 'Supply Chain Team', size: '3.5 MB'
  },
  {
    id: 'BI007', name: 'Customer Analytics', type: 'analysis', department: 'marketing',
    description: 'Customer segmentation and behavior analysis with retention metrics',
    metrics: ['Customer Lifetime Value', 'Churn Rate', 'NPS', 'Retention Rate'],
    charts: ['pie', 'bar', 'radar'], dataSources: ['CRM', 'Support DB'],
    lastUpdated: '2024-01-11', views: 789, favorites: 123, shared: 56,
    status: 'published', owner: 'Customer Success', size: '2.1 MB'
  },
  {
    id: 'BI008', name: 'HR Analytics', type: 'report', department: 'executive',
    description: 'Workforce analytics including headcount, turnover, and diversity metrics',
    metrics: ['Headcount', 'Turnover Rate', 'Diversity Index', 'Time to Hire'],
    charts: ['bar', 'pie', 'line'], dataSources: ['HRIS', 'ATS'],
    lastUpdated: '2024-01-10', views: 567, favorites: 78, shared: 45,
    status: 'published', owner: 'HR Team', size: '1.5 MB'
  }
])

// BI Statistics
const biStats = reactive({
  total: 0,
  dashboards: 0,
  reports: 0,
  scorecards: 0,
  analysis: 0,
  totalViews: 0,
  totalFavorites: 0,
  totalShares: 0,
  topDepartment: ''
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 8,
  total: biReports.value.length
})

// Filtered reports
const filteredReports = computed(() => {
  let filtered = biReports.value
  if (searchKeyword.value) {
    filtered = filtered.filter(r =>
        r.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        r.description.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        r.metrics.some(m => m.toLowerCase().includes(searchKeyword.value.toLowerCase()))
    )
  }
  if (selectedType.value !== 'all') {
    filtered = filtered.filter(r => r.type === selectedType.value)
  }
  if (selectedDepartment.value !== 'all') {
    filtered = filtered.filter(r => r.department === selectedDepartment.value)
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
        updateStats()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  biChart = echarts.init(chartRef.value)
  biChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Views', 'Favorites', 'Shares'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: biReports.value.map(r => r.name.substring(0, 12)), axisLabel: { rotate: 30, interval: 0 } },
    yAxis: { type: 'value', name: 'Count' },
    series: [
      { name: 'Views', type: 'bar', data: biReports.value.map(r => r.views), itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] } },
      { name: 'Favorites', type: 'line', data: biReports.value.map(r => r.favorites), smooth: true, lineStyle: { color: '#E6A23C', width: 2 }, symbol: 'circle', symbolSize: 8 },
      { name: 'Shares', type: 'line', data: biReports.value.map(r => r.shared), smooth: true, lineStyle: { color: '#67C23A', width: 2 }, symbol: 'diamond', symbolSize: 8 }
    ]
  })
}

const updateStats = () => {
  biStats.total = biReports.value.length
  biStats.dashboards = biReports.value.filter(r => r.type === 'dashboard').length
  biStats.reports = biReports.value.filter(r => r.type === 'report').length
  biStats.scorecards = biReports.value.filter(r => r.type === 'scorecard').length
  biStats.analysis = biReports.value.filter(r => r.type === 'analysis').length
  biStats.totalViews = biReports.value.reduce((sum, r) => sum + r.views, 0)
  biStats.totalFavorites = biReports.value.reduce((sum, r) => sum + r.favorites, 0)
  biStats.totalShares = biReports.value.reduce((sum, r) => sum + r.shared, 0)

  // Find top department
  const deptCount: Record<string, number> = {}
  biReports.value.forEach(r => {
    deptCount[r.department] = (deptCount[r.department] || 0) + 1
  })
  const top = Object.entries(deptCount).reduce((a, b) => a[1] > b[1] ? a : b, ['', 0])
  biStats.topDepartment = top[0].charAt(0).toUpperCase() + top[0].slice(1)
}

const handleResize = () => {
  biChart?.resize()
}

// ==================== Report Functions ====================
const refreshReports = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  loading.value = false
  ElMessage.success('BI reports refreshed successfully')
}

const viewDashboard = (report: any) => {
  selectedReport.value = report
  dashboardVisible.value = true
}

const downloadReport = async (report: any) => {
  ElMessage.info(`Downloading ${report.name}...`)
  await new Promise(resolve => setTimeout(resolve, 1000))
  ElMessage.success(`${report.name} downloaded successfully`)
}

const shareReport = (report: any) => {
  ElMessage.success(`Share link generated for ${report.name}`)
}

const favoriteReport = (report: any) => {
  report.favorites++
  ElMessage.success(`${report.name} added to favorites`)
}

const duplicateReport = async (report: any) => {
  const newReport = {
    ...report,
    id: `BI${String(biReports.value.length + 1).padStart(3, '0')}`,
    name: `${report.name} (Copy)`,
    views: 0,
    favorites: 0,
    shared: 0,
    status: 'draft'
  }
  biReports.value.unshift(newReport)
  updateStats()
  initChart()
  ElMessage.success(`Report duplicated successfully`)
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getTypeIcon = (type: string) => {
  switch (type) {
    case 'dashboard': return '📈'
    case 'report': return '📋'
    case 'scorecard': return '🎯'
    case 'analysis': return '🔍'
    default: return '📊'
  }
}

const getTypeColor = (type: string) => {
  switch (type) {
    case 'dashboard': return '#409EFF'
    case 'report': return '#67C23A'
    case 'scorecard': return '#E6A23C'
    case 'analysis': return '#9B59B6'
    default: return '#909399'
  }
}

const getDepartmentColor = (department: string) => {
  switch (department) {
    case 'executive': return '#F56C6C'
    case 'operations': return '#409EFF'
    case 'finance': return '#67C23A'
    case 'sales': return '#E6A23C'
    case 'marketing': return '#9B59B6'
    default: return '#909399'
  }
}

const formatNumber = (num: number) => {
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
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
          <span class="loading-title">Loading BI Reports</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Reports & BI - BI Reports</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="bi-reports-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">BI Reports</h1>
        <p class="page-subtitle">Business Intelligence dashboards and analytics</p>
      </div>
      <div class="header-right">
        <el-button type="primary" size="large">
          <el-icon><Plus /></el-icon>
          Create Report
        </el-button>
        <el-button size="large" @click="refreshReports" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
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
          <div class="stat-value">{{ biStats.total }}</div>
          <div class="stat-label">Total Assets</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+2 this month</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon views-icon">
          <el-icon><View /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ formatNumber(biStats.totalViews) }}</div>
          <div class="stat-label">Total Views</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ formatNumber(biStats.totalFavorites) }} favorites</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon shares-icon">
          <el-icon><Share /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ formatNumber(biStats.totalShares) }}</div>
          <div class="stat-label">Total Shares</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">↑ 23%</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon dept-icon">
          <el-icon><DataAnalysis /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ biStats.topDepartment }}</div>
          <div class="stat-label">Top Department</div>
        </div>
        <div class="stat-trend">
          <span class="trend-neutral">{{ biStats.dashboards }} Dashboards</span>
        </div>
      </div>
    </div>

    <!-- Stats Breakdown Row -->
    <div class="stats-breakdown">
      <div class="breakdown-item">
        <span class="breakdown-label">Dashboards</span>
        <span class="breakdown-value">{{ biStats.dashboards }}</span>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: (biStats.dashboards / biStats.total) * 100 + '%', background: '#409EFF' }"></div>
        </div>
      </div>
      <div class="breakdown-item">
        <span class="breakdown-label">Reports</span>
        <span class="breakdown-value">{{ biStats.reports }}</span>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: (biStats.reports / biStats.total) * 100 + '%', background: '#67C23A' }"></div>
        </div>
      </div>
      <div class="breakdown-item">
        <span class="breakdown-label">Scorecards</span>
        <span class="breakdown-value">{{ biStats.scorecards }}</span>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: (biStats.scorecards / biStats.total) * 100 + '%', background: '#E6A23C' }"></div>
        </div>
      </div>
      <div class="breakdown-item">
        <span class="breakdown-label">Analysis</span>
        <span class="breakdown-value">{{ biStats.analysis }}</span>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: (biStats.analysis / biStats.total) * 100 + '%', background: '#9B59B6' }"></div>
        </div>
      </div>
    </div>

    <!-- Chart Section -->
    <div class="chart-section">
      <div class="section-header">
        <h3>Report Engagement Metrics</h3>
        <el-button text type="primary" @click="initChart">Refresh</el-button>
      </div>
      <div ref="chartRef" class="engagement-chart" style="height: 320px"></div>
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
        <div class="type-filters">
          <button
              v-for="type in reportTypes"
              :key="type.value"
              class="type-chip"
              :class="{ active: selectedType === type.value }"
              @click="selectedType = type.value"
          >
            <span class="chip-icon">{{ type.icon }}</span>
            <span>{{ type.label }}</span>
          </button>
        </div>
      </div>
      <div class="filters-right">
        <el-select v-model="selectedDepartment" placeholder="Department" clearable style="width: 150px">
          <el-option v-for="d in departments" :key="d.value" :label="d.label" :value="d.value" />
        </el-select>
      </div>
    </div>

    <!-- BI Reports Grid - Card Style -->
    <div class="reports-grid">
      <div
          v-for="report in filteredReports"
          :key="report.id"
          class="report-card"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="card-type" :style="{ background: getTypeColor(report.type) }">
            {{ getTypeIcon(report.type) }}
          </div>
          <div class="card-badges">
            <span class="dept-badge" :style="{ background: getDepartmentColor(report.department) + '20', color: getDepartmentColor(report.department) }">
              {{ report.department }}
            </span>
            <span class="status-badge" :class="report.status">
              {{ report.status }}
            </span>
          </div>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <h4 class="card-title">{{ report.name }}</h4>
          <p class="card-description">{{ report.description }}</p>

          <!-- Metrics -->
          <div class="metrics-section">
            <div class="section-label">Key Metrics</div>
            <div class="metrics-list">
              <span v-for="metric in report.metrics.slice(0, 3)" :key="metric" class="metric-tag">
                {{ metric }}
              </span>
              <span v-if="report.metrics.length > 3" class="metric-more">+{{ report.metrics.length - 3 }}</span>
            </div>
          </div>

          <!-- Data Sources -->
          <div class="sources-section">
            <div class="section-label">Data Sources</div>
            <div class="sources-list">
              <span v-for="source in report.dataSources.slice(0, 2)" :key="source" class="source-tag">
                {{ source }}
              </span>
              <span v-if="report.dataSources.length > 2" class="source-more">+{{ report.dataSources.length - 2 }}</span>
            </div>
          </div>

          <!-- Stats -->
          <div class="report-stats">
            <div class="stat">
              <el-icon><View /></el-icon>
              <span>{{ formatNumber(report.views) }} views</span>
            </div>
            <div class="stat">
              <el-icon><Star /></el-icon>
              <span>{{ formatNumber(report.favorites) }}</span>
            </div>
            <div class="stat">
              <el-icon><Share /></el-icon>
              <span>{{ formatNumber(report.shared) }}</span>
            </div>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="footer-info">
            <span class="info-item">
              <el-icon><Calendar /></el-icon>
              {{ report.lastUpdated }}
            </span>
            <span class="info-item">
              <el-icon><User /></el-icon>
              {{ report.owner }}
            </span>
            <span class="info-item">
              <el-icon><Document /></el-icon>
              {{ report.size }}
            </span>
          </div>
          <div class="card-actions">
            <el-button circle size="small" @click="viewDashboard(report)">
              <el-icon><View /></el-icon>
            </el-button>
            <el-button circle size="small" type="primary" @click="downloadReport(report)">
              <el-icon><Download /></el-icon>
            </el-button>
            <el-button circle size="small" @click="shareReport(report)">
              <el-icon><Share /></el-icon>
            </el-button>
            <el-button circle size="small" @click="favoriteReport(report)">
              <el-icon><Star /></el-icon>
            </el-button>
            <el-button circle size="small" @click="duplicateReport(report)">
              <el-icon><CopyDocument /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredReports.length === 0" class="empty-state">
      <el-empty description="No BI reports found">
        <el-button type="primary">Create Report</el-button>
      </el-empty>
    </div>

    <!-- Pagination -->
    <div v-if="filteredReports.length > 0" class="pagination-wrapper">
      <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[8, 12, 16, 24]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
      />
    </div>

    <!-- Dashboard Preview Dialog -->
    <el-dialog v-model="dashboardVisible" :title="selectedReport?.name" width="80%" top="5vh" class="dashboard-dialog">
      <div class="dashboard-preview">
        <div class="dashboard-header">
          <div class="dashboard-info">
            <h3>{{ selectedReport?.name }}</h3>
            <p>{{ selectedReport?.description }}</p>
          </div>
          <div class="dashboard-meta">
            <span><el-icon><Calendar /></el-icon> {{ selectedReport?.lastUpdated }}</span>
            <span><el-icon><User /></el-icon> {{ selectedReport?.owner }}</span>
            <span class="dept-badge" :style="{ background: getDepartmentColor(selectedReport?.department) + '20', color: getDepartmentColor(selectedReport?.department) }">
              {{ selectedReport?.department }}
            </span>
          </div>
        </div>

        <el-divider />

        <div class="dashboard-metrics">
          <h4>Key Metrics</h4>
          <div class="metrics-grid">
            <div v-for="metric in selectedReport?.metrics" :key="metric" class="metric-card">
              <div class="metric-name">{{ metric }}</div>
              <div class="metric-value">--</div>
              <div class="metric-trend">Trend data not available</div>
            </div>
          </div>
        </div>

        <div class="dashboard-charts">
          <h4>Visualizations</h4>
          <div class="chart-placeholder">
            <el-empty description="Chart preview will appear here" :image-size="100" />
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="dashboardVisible = false">Close</el-button>
        <el-button type="primary" @click="downloadReport(selectedReport)">Download</el-button>
        <el-button @click="shareReport(selectedReport)">Share</el-button>
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
.bi-reports-container {
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
  margin-bottom: 20px;
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

.views-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.shares-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.dept-icon {
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
  font-size: 11px;
  color: #67c23a;
  background: #f0f9ff;
  padding: 4px 8px;
  border-radius: 20px;
}

.trend-neutral {
  font-size: 11px;
  color: #909399;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 20px;
}

/* Stats Breakdown */
.stats-breakdown {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.breakdown-item {
  background: white;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.breakdown-label {
  font-size: 12px;
  color: #909399;
  display: block;
  margin-bottom: 8px;
}

.breakdown-value {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  display: block;
  margin-bottom: 12px;
}

.breakdown-bar {
  height: 6px;
  background: #e4e7ed;
  border-radius: 3px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

/* Chart Section */
.chart-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
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

.engagement-chart {
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

.type-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.type-chip {
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

.type-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.type-chip.active {
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
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.report-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
}

.report-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 0 20px;
}

.card-type {
  width: 44px;
  height: 44px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: white;
}

.card-badges {
  display: flex;
  gap: 8px;
}

.dept-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.status-badge.published {
  background: #f0f9ff;
  color: #67c23a;
}

.status-badge.draft {
  background: #fdf6ec;
  color: #e6a23c;
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

.card-description {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.metrics-section,
.sources-section {
  margin-bottom: 12px;
}

.section-label {
  font-size: 11px;
  color: #909399;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metrics-list,
.sources-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.metric-tag,
.source-tag {
  font-size: 11px;
  padding: 3px 8px;
  background: #f0f9ff;
  color: #409eff;
  border-radius: 12px;
}

.metric-more,
.source-more {
  font-size: 11px;
  padding: 3px 8px;
  background: #f5f7fa;
  color: #909399;
  border-radius: 12px;
}

.report-stats {
  display: flex;
  gap: 16px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.stat {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
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
  font-size: 11px;
  color: #909399;
}

.card-actions {
  display: flex;
  gap: 6px;
}

.card-actions .el-button {
  background: white;
  border: 1px solid #e4e7ed;
}

.card-actions .el-button:hover {
  transform: scale(1.05);
}

/* Empty State */
.empty-state {
  padding: 60px 0;
  text-align: center;
}

/* Pagination */
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
}

/* Dashboard Dialog */
.dashboard-dialog :deep(.el-dialog__body) {
  padding: 20px;
  max-height: 70vh;
  overflow-y: auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 16px;
}

.dashboard-info h3 {
  font-size: 20px;
  margin: 0 0 8px 0;
}

.dashboard-info p {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.dashboard-meta {
  display: flex;
  gap: 16px;
  align-items: center;
  font-size: 13px;
  color: #909399;
}

.dashboard-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.metric-card {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 16px;
  text-align: center;
}

.metric-name {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.metric-trend {
  font-size: 11px;
  color: #67c23a;
}

.chart-placeholder {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-breakdown {
    grid-template-columns: repeat(2, 1fr);
  }

  .reports-grid {
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  }
}

@media (max-width: 768px) {
  .bi-reports-container {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stats-breakdown {
    grid-template-columns: 1fr;
  }

  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filters-left {
    flex-direction: column;
  }

  .type-filters {
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

  .reports-grid {
    grid-template-columns: 1fr;
  }

  .dashboard-header {
    flex-direction: column;
  }
}
</style>