<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Search, Refresh, Document, Download, Printer,
  Share, Star, Clock, Warning, CircleCheck,
  TrendCharts, DataLine, Calendar, Setting,
  Plus, Upload, Filter, ArrowUp, ArrowDown,
  View, User, Trophy, Medal, Edit, Delete,
  CopyDocument, More, Grid, List, Filter as FilterIcon,
  MagicStick, PieChart
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Loading custom reports...',
  'Preparing templates...',
  'Loading saved queries...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedCategory = ref('all')
const selectedSort = ref('date')
const createReportVisible = ref(false)
const reportDetailsVisible = ref(false)
const editReportVisible = ref(false)
const chartRef = ref(null)

let usageChart: echarts.ECharts | null = null

// Category filters
const categoryOptions = [
  { value: 'all', label: 'All Categories', icon: '📊' },
  { value: 'system', label: 'System', icon: '🏥' },
  { value: 'energy', label: 'Energy', icon: '⚡' },
  { value: 'financial', label: 'Financial', icon: '💰' },
  { value: 'operations', label: 'Operations', icon: '🔧' },
  { value: 'security', label: 'Security', icon: '🔒' }
]

// Sort options
const sortOptions = [
  { value: 'date', label: 'Last Modified' },
  { value: 'name', label: 'Name' },
  { value: 'views', label: 'Most Viewed' },
  { value: 'runs', label: 'Most Run' }
]

// Custom reports data
const customReports = ref([
  {
    id: 'CR001', name: 'System Performance Dashboard', category: 'system',
    description: 'Custom dashboard showing key system performance metrics including CPU, memory, and response times',
    createdBy: 'admin@system.com', createdAt: '2024-01-10', lastModified: '2024-01-15',
    views: 245, runs: 89, status: 'active', isPublic: true,
    metrics: ['CPU Usage', 'Memory Usage', 'Response Time', 'Error Rate'],
    chartTypes: ['line', 'bar', 'gauge'],
    tags: ['performance', 'monitoring', 'real-time']
  },
  {
    id: 'CR002', name: 'Energy Consumption Analysis', category: 'energy',
    description: 'Custom report for analyzing energy consumption patterns across different zones and time periods',
    createdBy: 'energy@system.com', createdAt: '2024-01-05', lastModified: '2024-01-14',
    views: 189, runs: 67, status: 'active', isPublic: true,
    metrics: ['kWh Consumption', 'Peak Demand', 'Cost', 'Carbon Footprint'],
    chartTypes: ['line', 'bar', 'area'],
    tags: ['energy', 'sustainability', 'cost']
  },
  {
    id: 'CR003', name: 'Financial Overview Q1', category: 'financial',
    description: 'Quarterly financial report with revenue, expenses, and profit margin analysis',
    createdBy: 'finance@system.com', createdAt: '2024-01-01', lastModified: '2024-01-12',
    views: 312, runs: 124, status: 'active', isPublic: false,
    metrics: ['Revenue', 'Expenses', 'Profit Margin', 'ROI'],
    chartTypes: ['bar', 'pie', 'table'],
    tags: ['financial', 'quarterly', 'budget']
  },
  {
    id: 'CR004', name: 'Maintenance Cost Tracker', category: 'operations',
    description: 'Track maintenance costs, work order completion rates, and SLA compliance',
    createdBy: 'maintenance@system.com', createdAt: '2024-01-08', lastModified: '2024-01-13',
    views: 156, runs: 45, status: 'draft', isPublic: false,
    metrics: ['Total Cost', 'Work Orders', 'SLA Compliance', 'MTTR'],
    chartTypes: ['bar', 'line', 'gauge'],
    tags: ['maintenance', 'cost', 'sla']
  },
  {
    id: 'CR005', name: 'Security Incident Report', category: 'security',
    description: 'Custom report for tracking security incidents, response times, and resolution rates',
    createdBy: 'security@system.com', createdAt: '2024-01-03', lastModified: '2024-01-11',
    views: 223, runs: 78, status: 'active', isPublic: true,
    metrics: ['Incidents', 'Response Time', 'Resolution Rate', 'Severity'],
    chartTypes: ['bar', 'pie', 'table'],
    tags: ['security', 'incidents', 'compliance']
  },
  {
    id: 'CR006', name: 'Zone Efficiency Report', category: 'operations',
    description: 'Compare efficiency metrics across different building zones and departments',
    createdBy: 'ops@system.com', createdAt: '2024-01-06', lastModified: '2024-01-10',
    views: 98, runs: 34, status: 'active', isPublic: true,
    metrics: ['Efficiency Score', 'Utilization', 'Cost per Zone', 'Savings'],
    chartTypes: ['bar', 'radar', 'table'],
    tags: ['efficiency', 'zones', 'comparison']
  },
  {
    id: 'CR007', name: 'Executive Dashboard', category: 'system',
    description: 'High-level dashboard for executives with key KPIs and trends',
    createdBy: 'executive@system.com', createdAt: '2024-01-15', lastModified: '2024-01-15',
    views: 456, runs: 234, status: 'active', isPublic: true,
    metrics: ['Overall Health', 'Revenue', 'Efficiency', 'Satisfaction'],
    chartTypes: ['gauge', 'line', 'bar', 'pie'],
    tags: ['executive', 'kpi', 'dashboard']
  },
  {
    id: 'CR008', name: 'Sustainability Report - Draft', category: 'energy',
    description: 'Draft report for sustainability metrics including carbon reduction and renewable energy usage',
    createdBy: 'sustainability@system.com', createdAt: '2024-01-14', lastModified: '2024-01-14',
    views: 45, runs: 12, status: 'draft', isPublic: false,
    metrics: ['Carbon Reduction', 'Renewable %', 'Water Saved', 'Waste Recycled'],
    chartTypes: ['area', 'bar', 'gauge'],
    tags: ['sustainability', 'carbon', 'draft']
  }
])

// Report statistics
const reportStats = reactive({
  total: 0,
  active: 0,
  draft: 0,
  public: 0,
  private: 0,
  totalViews: 0,
  totalRuns: 0,
  avgViews: 0,
  topCategory: ''
})

// New report form
const newReportForm = reactive({
  name: '',
  category: 'system',
  description: '',
  isPublic: true,
  metrics: [] as string[],
  chartTypes: [] as string[],
  tags: [] as string[]
})

// Edit report form
const editReportForm = reactive({
  id: '',
  name: '',
  category: '',
  description: '',
  isPublic: true,
  status: '',
  metrics: [] as string[],
  chartTypes: [] as string[],
  tags: [] as string[]
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 9,
  total: customReports.value.length
})

// Filtered reports
const filteredReports = computed(() => {
  let filtered = customReports.value
  if (searchKeyword.value) {
    filtered = filtered.filter(r =>
        r.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        r.description.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        r.tags.some(t => t.includes(searchKeyword.value.toLowerCase()))
    )
  }
  if (selectedCategory.value !== 'all') {
    filtered = filtered.filter(r => r.category === selectedCategory.value)
  }

  // Sort
  switch (selectedSort.value) {
    case 'name':
      filtered.sort((a, b) => a.name.localeCompare(b.name))
      break
    case 'views':
      filtered.sort((a, b) => b.views - a.views)
      break
    case 'runs':
      filtered.sort((a, b) => b.runs - a.runs)
      break
    default:
      filtered.sort((a, b) => new Date(b.lastModified).getTime() - new Date(a.lastModified).getTime())
  }

  pagination.total = filtered.length
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// Available metrics options
const availableMetrics = [
  'CPU Usage', 'Memory Usage', 'Response Time', 'Error Rate',
  'kWh Consumption', 'Peak Demand', 'Cost', 'Carbon Footprint',
  'Revenue', 'Expenses', 'Profit Margin', 'ROI',
  'Work Orders', 'SLA Compliance', 'MTTR', 'Incidents',
  'Efficiency Score', 'Utilization', 'Overall Health', 'Satisfaction'
]

// Available chart types
const availableChartTypes = ['line', 'bar', 'pie', 'area', 'gauge', 'radar', 'table']

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

  usageChart = echarts.init(chartRef.value)
  usageChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Views', 'Runs'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: customReports.value.map(r => r.name.substring(0, 15)) },
    yAxis: { type: 'value', name: 'Count' },
    series: [
      { name: 'Views', type: 'bar', data: customReports.value.map(r => r.views), itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] } },
      { name: 'Runs', type: 'line', data: customReports.value.map(r => r.runs), smooth: true, lineStyle: { color: '#67C23A', width: 2 }, symbol: 'circle', symbolSize: 8 }
    ]
  })
}

const updateStats = () => {
  reportStats.total = customReports.value.length
  reportStats.active = customReports.value.filter(r => r.status === 'active').length
  reportStats.draft = customReports.value.filter(r => r.status === 'draft').length
  reportStats.public = customReports.value.filter(r => r.isPublic).length
  reportStats.private = customReports.value.filter(r => !r.isPublic).length
  reportStats.totalViews = customReports.value.reduce((sum, r) => sum + r.views, 0)
  reportStats.totalRuns = customReports.value.reduce((sum, r) => sum + r.runs, 0)
  reportStats.avgViews = Math.round(reportStats.totalViews / reportStats.total)

  // Find top category
  const categoryCount: Record<string, number> = {}
  customReports.value.forEach(r => {
    categoryCount[r.category] = (categoryCount[r.category] || 0) + 1
  })
  const top = Object.entries(categoryCount).reduce((a, b) => a[1] > b[1] ? a : b, ['', 0])
  reportStats.topCategory = top[0].charAt(0).toUpperCase() + top[0].slice(1)
}

const handleResize = () => {
  usageChart?.resize()
}

// ==================== Report Functions ====================
const refreshReports = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  loading.value = false
  ElMessage.success('Custom reports refreshed successfully')
}

const viewReport = (report: any) => {
  selectedReport.value = report
  reportDetailsVisible.value = true
}

const runReport = async (report: any) => {
  ElMessage.info(`Running ${report.name}...`)
  await new Promise(resolve => setTimeout(resolve, 1500))
  report.runs++
  updateStats()
  ElMessage.success(`${report.name} executed successfully`)
}

const editReport = (report: any) => {
  editReportForm.id = report.id
  editReportForm.name = report.name
  editReportForm.category = report.category
  editReportForm.description = report.description
  editReportForm.isPublic = report.isPublic
  editReportForm.status = report.status
  editReportForm.metrics = [...report.metrics]
  editReportForm.chartTypes = [...report.chartTypes]
  editReportForm.tags = [...report.tags]
  editReportVisible.value = true
}

const saveEditReport = async () => {
  if (!editReportForm.name) {
    ElMessage.warning('Please enter a report name')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1000))

  const index = customReports.value.findIndex(r => r.id === editReportForm.id)
  if (index !== -1) {
    customReports.value[index] = {
      ...customReports.value[index],
      name: editReportForm.name,
      category: editReportForm.category,
      description: editReportForm.description,
      isPublic: editReportForm.isPublic,
      status: editReportForm.status,
      metrics: editReportForm.metrics,
      chartTypes: editReportForm.chartTypes,
      tags: editReportForm.tags,
      lastModified: new Date().toISOString().split('T')[0]
    }
  }

  updateStats()
  editReportVisible.value = false
  ElMessage.success('Report updated successfully')
}

const deleteReport = async (report: any) => {
  await ElMessageBox.confirm(
      `Delete report "${report.name}"? This action cannot be undone.`,
      'Confirm Delete',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'danger'
      }
  )

  const index = customReports.value.findIndex(r => r.id === report.id)
  if (index !== -1) {
    customReports.value.splice(index, 1)
  }

  updateStats()
  initChart()
  ElMessage.success('Report deleted successfully')
}

const duplicateReport = async (report: any) => {
  const newReport = {
    ...report,
    id: `CR${String(customReports.value.length + 1).padStart(3, '0')}`,
    name: `${report.name} (Copy)`,
    createdBy: 'current@user.com',
    createdAt: new Date().toISOString().split('T')[0],
    lastModified: new Date().toISOString().split('T')[0],
    views: 0,
    runs: 0,
    status: 'draft'
  }

  customReports.value.unshift(newReport)
  updateStats()
  initChart()
  ElMessage.success(`Report duplicated successfully`)
}

const openCreateReport = () => {
  newReportForm.name = ''
  newReportForm.category = 'system'
  newReportForm.description = ''
  newReportForm.isPublic = true
  newReportForm.metrics = []
  newReportForm.chartTypes = []
  newReportForm.tags = []
  createReportVisible.value = true
}

const createReport = async () => {
  if (!newReportForm.name) {
    ElMessage.warning('Please enter a report name')
    return
  }

  if (newReportForm.metrics.length === 0) {
    ElMessage.warning('Please select at least one metric')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1000))

  const newReport = {
    id: `CR${String(customReports.value.length + 1).padStart(3, '0')}`,
    name: newReportForm.name,
    category: newReportForm.category,
    description: newReportForm.description || 'New custom report',
    createdBy: 'current@user.com',
    createdAt: new Date().toISOString().split('T')[0],
    lastModified: new Date().toISOString().split('T')[0],
    views: 0,
    runs: 0,
    status: 'draft',
    isPublic: newReportForm.isPublic,
    metrics: newReportForm.metrics,
    chartTypes: newReportForm.chartTypes.length ? newReportForm.chartTypes : ['bar', 'line'],
    tags: newReportForm.tags
  }

  customReports.value.unshift(newReport)
  updateStats()
  initChart()
  createReportVisible.value = false
  ElMessage.success('Custom report created successfully')
}

const exportReport = (report: any) => {
  ElMessage.info(`Exporting ${report.name}...`)
  setTimeout(() => {
    ElMessage.success(`${report.name} exported successfully`)
  }, 1000)
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getStatusType = (status: string) => {
  return status === 'active' ? 'success' : 'info'
}

const getCategoryIcon = (category: string) => {
  switch (category) {
    case 'system': return '🏥'
    case 'energy': return '⚡'
    case 'financial': return '💰'
    case 'operations': return '🔧'
    case 'security': return '🔒'
    default: return '📊'
  }
}

const getCategoryColor = (category: string) => {
  switch (category) {
    case 'system': return '#409EFF'
    case 'energy': return '#67C23A'
    case 'financial': return '#E6A23C'
    case 'operations': return '#F56C6C'
    case 'security': return '#9B59B6'
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
          <span class="loading-title">Loading Custom Reports</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Reports & BI - Custom Reports</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="custom-reports-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Custom Reports</h1>
        <p class="page-subtitle">Create and manage your custom reports and dashboards</p>
      </div>
      <div class="header-right">
        <el-button type="primary" size="large" @click="openCreateReport">
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
          <div class="stat-value">{{ reportStats.total }}</div>
          <div class="stat-label">Total Reports</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ reportStats.active }} Active</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon views-icon">
          <el-icon><View /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ reportStats.totalViews.toLocaleString() }}</div>
          <div class="stat-label">Total Views</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ reportStats.avgViews }} avg per report</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon runs-icon">
          <el-icon><VideoPlay /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ reportStats.totalRuns.toLocaleString() }}</div>
          <div class="stat-label">Total Runs</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">↑ 23% this month</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon visibility-icon">
          <el-icon><Share /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ reportStats.public }}</div>
          <div class="stat-label">Public Reports</div>
        </div>
        <div class="stat-trend">
          <span class="trend-neutral">{{ reportStats.private }} Private</span>
        </div>
      </div>
    </div>

    <!-- Chart Section -->
    <div class="chart-section">
      <div class="section-header">
        <h3>Report Usage Statistics</h3>
        <el-button text type="primary" @click="initChart">Refresh</el-button>
      </div>
      <div ref="chartRef" class="usage-chart" style="height: 320px"></div>
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
              v-for="cat in categoryOptions"
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
        <el-select v-model="selectedSort" placeholder="Sort by" style="width: 140px">
          <el-option v-for="s in sortOptions" :key="s.value" :label="s.label" :value="s.value" />
        </el-select>
      </div>
    </div>

    <!-- Reports Grid - Card Style -->
    <div class="reports-grid">
      <div
          v-for="report in filteredReports"
          :key="report.id"
          class="report-card"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="card-category" :style="{ background: getCategoryColor(report.category) }">
            {{ getCategoryIcon(report.category) }}
          </div>
          <div class="card-status">
            <el-tag :type="getStatusType(report.status)" size="small" effect="light">
              {{ report.status.toUpperCase() }}
            </el-tag>
            <el-tag v-if="report.isPublic" size="small" type="info" effect="plain">Public</el-tag>
          </div>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <h4 class="card-title">{{ report.name }}</h4>
          <p class="card-description">{{ report.description }}</p>

          <!-- Metrics -->
          <div class="metrics-section">
            <div class="section-label">Metrics</div>
            <div class="metrics-list">
              <span v-for="metric in report.metrics.slice(0, 3)" :key="metric" class="metric-tag">
                {{ metric }}
              </span>
              <span v-if="report.metrics.length > 3" class="metric-more">+{{ report.metrics.length - 3 }}</span>
            </div>
          </div>

          <!-- Chart Types -->
          <div class="chart-types">
            <div class="section-label">Chart Types</div>
            <div class="chart-icons">
              <span v-for="type in report.chartTypes" :key="type" class="chart-icon">
                {{ type === 'line' ? '📈' : type === 'bar' ? '📊' : type === 'pie' ? '🥧' : type === 'gauge' ? '📏' : '📋' }}
              </span>
            </div>
          </div>

          <!-- Tags -->
          <div class="card-tags">
            <span v-for="tag in report.tags.slice(0, 3)" :key="tag" class="tag">{{ tag }}</span>
          </div>

          <!-- Stats -->
          <div class="report-stats">
            <div class="stat">
              <el-icon><View /></el-icon>
              <span>{{ report.views }} views</span>
            </div>
            <div class="stat">
              <el-icon><VideoPlay /></el-icon>
              <span>{{ report.runs }} runs</span>
            </div>
            <div class="stat">
              <el-icon><Calendar /></el-icon>
              <span>{{ report.lastModified }}</span>
            </div>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="footer-author">
            <el-icon><User /></el-icon>
            <span>{{ report.createdBy?.split('@')[0] }}</span>
          </div>
          <div class="card-actions">
            <el-button circle size="small" @click="runReport(report)">
              <el-icon><VideoPlay /></el-icon>
            </el-button>
            <el-button circle size="small" type="primary" @click="editReport(report)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button circle size="small" @click="viewReport(report)">
              <el-icon><View /></el-icon>
            </el-button>
            <el-button circle size="small" @click="duplicateReport(report)">
              <el-icon><CopyDocument /></el-icon>
            </el-button>
            <el-button circle size="small" @click="exportReport(report)">
              <el-icon><Download /></el-icon>
            </el-button>
            <el-button circle size="small" type="danger" @click="deleteReport(report)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredReports.length === 0" class="empty-state">
      <el-empty description="No custom reports found">
        <el-button type="primary" @click="openCreateReport">Create Report</el-button>
      </el-empty>
    </div>

    <!-- Pagination -->
    <div v-if="filteredReports.length > 0" class="pagination-wrapper">
      <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[9, 12, 18, 24]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
      />
    </div>

    <!-- Report Details Dialog -->
    <el-dialog v-model="reportDetailsVisible" :title="selectedReport?.name" width="650px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Report ID">{{ selectedReport?.id }}</el-descriptions-item>
        <el-descriptions-item label="Category">
          <el-tag :type="getStatusType(selectedReport?.status)" size="small">
            {{ selectedReport?.category?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusType(selectedReport?.status)" size="small">
            {{ selectedReport?.status?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Visibility">
          <el-tag :type="selectedReport?.isPublic ? 'success' : 'info'" size="small">
            {{ selectedReport?.isPublic ? 'Public' : 'Private' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Created By">{{ selectedReport?.createdBy }}</el-descriptions-item>
        <el-descriptions-item label="Created At">{{ selectedReport?.createdAt }}</el-descriptions-item>
        <el-descriptions-item label="Last Modified">{{ selectedReport?.lastModified }}</el-descriptions-item>
        <el-descriptions-item label="Total Views">{{ selectedReport?.views }}</el-descriptions-item>
        <el-descriptions-item label="Total Runs">{{ selectedReport?.runs }}</el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedReport?.description }}</el-descriptions-item>
        <el-descriptions-item label="Metrics" :span="2">
          <div class="metrics-list">
            <el-tag v-for="m in selectedReport?.metrics" :key="m" size="small" style="margin: 2px">
              {{ m }}
            </el-tag>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="Chart Types" :span="2">
          <div class="chart-types-list">
            <el-tag v-for="c in selectedReport?.chartTypes" :key="c" size="small" style="margin: 2px">
              {{ c.toUpperCase() }}
            </el-tag>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="Tags" :span="2">
          <div class="tags-list">
            <el-tag v-for="t in selectedReport?.tags" :key="t" size="small" style="margin: 2px">
              {{ t }}
            </el-tag>
          </div>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="reportDetailsVisible = false">Close</el-button>
        <el-button type="primary" @click="runReport(selectedReport)">Run Report</el-button>
        <el-button @click="exportReport(selectedReport)">Export</el-button>
      </template>
    </el-dialog>

    <!-- Create Report Dialog -->
    <el-dialog v-model="createReportVisible" title="Create Custom Report" width="600px">
      <el-form :model="newReportForm" label-width="120px">
        <el-form-item label="Report Name" required>
          <el-input v-model="newReportForm.name" placeholder="Enter report name" />
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="newReportForm.category" style="width: 100%">
            <el-option v-for="c in categoryOptions.slice(1)" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="newReportForm.description" type="textarea" rows="2" placeholder="Enter description" />
        </el-form-item>
        <el-form-item label="Visibility">
          <el-radio-group v-model="newReportForm.isPublic">
            <el-radio :label="true">Public</el-radio>
            <el-radio :label="false">Private</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Metrics" required>
          <el-select v-model="newReportForm.metrics" multiple filterable allow-create default-first-option style="width: 100%">
            <el-option v-for="m in availableMetrics" :key="m" :label="m" :value="m" />
          </el-select>
        </el-form-item>
        <el-form-item label="Chart Types">
          <el-select v-model="newReportForm.chartTypes" multiple style="width: 100%">
            <el-option v-for="c in availableChartTypes" :key="c" :label="c.toUpperCase()" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item label="Tags">
          <el-select v-model="newReportForm.tags" multiple filterable allow-create default-first-option style="width: 100%">
            <el-option v-for="r in customReports.flatMap(r => r.tags)" :key="r" :label="r" :value="r" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createReportVisible = false">Cancel</el-button>
        <el-button type="primary" @click="createReport">Create Report</el-button>
      </template>
    </el-dialog>

    <!-- Edit Report Dialog -->
    <el-dialog v-model="editReportVisible" title="Edit Custom Report" width="600px">
      <el-form :model="editReportForm" label-width="120px">
        <el-form-item label="Report Name" required>
          <el-input v-model="editReportForm.name" placeholder="Enter report name" />
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="editReportForm.category" style="width: 100%">
            <el-option v-for="c in categoryOptions.slice(1)" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="editReportForm.description" type="textarea" rows="2" placeholder="Enter description" />
        </el-form-item>
        <el-form-item label="Status">
          <el-select v-model="editReportForm.status" style="width: 100%">
            <el-option label="Active" value="active" />
            <el-option label="Draft" value="draft" />
          </el-select>
        </el-form-item>
        <el-form-item label="Visibility">
          <el-radio-group v-model="editReportForm.isPublic">
            <el-radio :label="true">Public</el-radio>
            <el-radio :label="false">Private</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Metrics" required>
          <el-select v-model="editReportForm.metrics" multiple filterable allow-create default-first-option style="width: 100%">
            <el-option v-for="m in availableMetrics" :key="m" :label="m" :value="m" />
          </el-select>
        </el-form-item>
        <el-form-item label="Chart Types">
          <el-select v-model="editReportForm.chartTypes" multiple style="width: 100%">
            <el-option v-for="c in availableChartTypes" :key="c" :label="c.toUpperCase()" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item label="Tags">
          <el-select v-model="editReportForm.tags" multiple filterable allow-create default-first-option style="width: 100%">
            <el-option v-for="r in customReports.flatMap(r => r.tags)" :key="r" :label="r" :value="r" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editReportVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveEditReport">Save Changes</el-button>
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
.custom-reports-container {
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

.views-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.runs-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.visibility-icon {
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

.usage-chart {
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

.card-category {
  width: 44px;
  height: 44px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: white;
}

.card-status {
  display: flex;
  gap: 8px;
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

.metrics-section {
  margin-bottom: 12px;
}

.section-label {
  font-size: 11px;
  color: #909399;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metrics-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.metric-tag {
  font-size: 11px;
  padding: 3px 8px;
  background: #f0f9ff;
  color: #409eff;
  border-radius: 12px;
}

.metric-more {
  font-size: 11px;
  padding: 3px 8px;
  background: #f5f7fa;
  color: #909399;
  border-radius: 12px;
}

.chart-types {
  margin-bottom: 12px;
}

.chart-icons {
  display: flex;
  gap: 8px;
}

.chart-icon {
  font-size: 16px;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.tag {
  font-size: 10px;
  padding: 3px 8px;
  background: #f5f7fa;
  border-radius: 12px;
  color: #606266;
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

.footer-author {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
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

/* Dialog Lists */
.metrics-list,
.chart-types-list,
.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .reports-grid {
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  }
}

@media (max-width: 768px) {
  .custom-reports-container {
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

  .reports-grid {
    grid-template-columns: 1fr;
  }

  .card-actions {
    flex-wrap: wrap;
  }
}
</style>