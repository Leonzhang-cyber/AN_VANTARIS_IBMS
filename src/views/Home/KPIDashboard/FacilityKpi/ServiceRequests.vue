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
        <div class="loading-tip">Not Developed Yet</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Service Requests Page Content -->
  <div v-else class="service-requests-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>Service Requests</h1>
        <p class="subtitle">Track and manage facility service requests, response times, and resolution metrics</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" :icon="Plus" @click="createRequest">New Request</el-button>
        <el-button :icon="Refresh" @click="refreshData">Refresh</el-button>
        <el-button :icon="Download" @click="exportReport">Export</el-button>
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            :shortcuts="dateShortcuts"
            size="default"
            style="width: 260px"
            @change="handleDateChange"
        />
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="kpi-cards">
      <div class="kpi-card total">
        <div class="kpi-icon">
          <el-icon :size="32"><Document /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ totalRequests }}</div>
          <div class="kpi-label">Total Requests</div>
        </div>
        <div class="kpi-trend" :class="requestTrend >= 0 ? 'positive' : 'negative'">
          <el-icon><CaretTop v-if="requestTrend >= 0" /><CaretBottom v-else /></el-icon>
          {{ Math.abs(requestTrend) }}%
        </div>
      </div>
      <div class="kpi-card open">
        <div class="kpi-icon">
          <el-icon :size="32"><WarningFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ openRequests }}</div>
          <div class="kpi-label">Open Requests</div>
        </div>
        <div class="kpi-sub">Critical: {{ criticalRequests }}</div>
      </div>
      <div class="kpi-card resolved">
        <div class="kpi-icon">
          <el-icon :size="32"><CircleCheckFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ resolvedRequests }}</div>
          <div class="kpi-label">Resolved (MTD)</div>
        </div>
        <div class="kpi-sub">Resolution Rate: {{ resolutionRate }}%</div>
      </div>
      <div class="kpi-card response">
        <div class="kpi-icon">
          <el-icon :size="32"><Timer /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ avgResponseTime }}</div>
          <div class="kpi-label">Avg Response Time</div>
        </div>
        <div class="kpi-trend" :class="responseTrend <= 0 ? 'positive' : 'negative'">
          <el-icon><CaretBottom v-if="responseTrend <= 0" /><CaretTop v-else /></el-icon>
          {{ Math.abs(responseTrend) }}%
        </div>
      </div>
    </div>

    <!-- Request Trends Chart -->
    <div class="chart-card">
      <div class="card-header">
        <h3>Request Trends</h3>
        <el-radio-group v-model="trendPeriod" size="small" @change="fetchTrendData">
          <el-radio-button label="week">Last 7 Days</el-radio-button>
          <el-radio-button label="month">Last 30 Days</el-radio-button>
          <el-radio-button label="quarter">Last 90 Days</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-container" ref="trendChartRef"></div>
    </div>

    <!-- Requests by Category and Priority -->
    <div class="two-columns">
      <div class="chart-card">
        <div class="card-header">
          <h3>Requests by Category</h3>
        </div>
        <div class="chart-container" ref="categoryChartRef"></div>
      </div>
      <div class="chart-card">
        <div class="card-header">
          <h3>Requests by Priority</h3>
        </div>
        <div class="chart-container" ref="priorityChartRef"></div>
      </div>
    </div>

    <!-- Service Requests Table -->
    <div class="table-card">
      <div class="card-header">
        <h3>Service Requests List</h3>
        <div class="header-filters">
          <el-select v-model="categoryFilter" placeholder="All Categories" clearable size="default" style="width: 140px">
            <el-option label="All Categories" value="all" />
            <el-option label="HVAC" value="HVAC" />
            <el-option label="Electrical" value="Electrical" />
            <el-option label="Plumbing" value="Plumbing" />
            <el-option label="Cleaning" value="Cleaning" />
            <el-option label="Security" value="Security" />
            <el-option label="IT" value="IT" />
          </el-select>
          <el-select v-model="priorityFilter" placeholder="All Priorities" clearable size="default" style="width: 130px">
            <el-option label="All Priorities" value="all" />
            <el-option label="Critical" value="critical" />
            <el-option label="High" value="high" />
            <el-option label="Medium" value="medium" />
            <el-option label="Low" value="low" />
          </el-select>
          <el-select v-model="statusFilter" placeholder="All Status" clearable size="default" style="width: 130px">
            <el-option label="All Status" value="all" />
            <el-option label="Open" value="open" />
            <el-option label="In Progress" value="in-progress" />
            <el-option label="Resolved" value="resolved" />
            <el-option label="Closed" value="closed" />
          </el-select>
          <el-input
              v-model="searchText"
              placeholder="Search..."
              :prefix-icon="Search"
              style="width: 200px"
              clearable
          />
        </div>
      </div>
      <el-table :data="paginatedRequests" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="Title" min-width="200" show-overflow-tooltip />
        <el-table-column prop="category" label="Category" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="Priority" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityTagType(row.priority)" size="small" effect="dark">
              {{ getPriorityLabel(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reportedBy" label="Reported By" width="140" />
        <el-table-column prop="assignedTo" label="Assigned To" width="140">
          <template #default="{ row }">
            <span :class="{ 'text-muted': !row.assignedTo }">
              {{ row.assignedTo || 'Unassigned' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="reportedDate" label="Reported Date" width="110" sortable />
        <el-table-column prop="responseTime" label="Response Time" width="110" sortable>
          <template #default="{ row }">
            <span :class="getResponseTimeClass(row.responseTime, row.targetTime)">
              {{ row.responseTime }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewRequest(row)">View</el-button>
            <el-button link type="success" size="small" @click="updateRequest(row)">Update</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredRequests.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- SLA Performance -->
    <div class="sla-section">
      <div class="section-header">
        <h2>
          <el-icon><Medal /></el-icon>
          SLA Performance by Category
        </h2>
      </div>
      <div class="sla-grid">
        <div v-for="sla in slaPerformance" :key="sla.category" class="sla-card">
          <div class="sla-header">
            <span class="sla-category">{{ sla.category }}</span>
            <span class="sla-rate" :class="sla.complianceRate >= 95 ? 'text-success' : 'text-danger'">
              {{ sla.complianceRate }}%
            </span>
          </div>
          <div class="sla-metrics">
            <div class="metric">
              <span class="metric-label">Target</span>
              <span class="metric-value">{{ sla.targetTime }}</span>
            </div>
            <div class="metric">
              <span class="metric-label">Actual</span>
              <span class="metric-value" :class="sla.avgResponseTime <= sla.targetMinutes ? 'text-success' : 'text-danger'">
                {{ sla.avgResponseTime }}
              </span>
            </div>
            <div class="metric">
              <span class="metric-label">Requests</span>
              <span class="metric-value">{{ sla.requestCount }}</span>
            </div>
          </div>
          <el-progress :percentage="sla.complianceRate" :color="sla.complianceRate >= 95 ? '#67c23a' : '#f56c6c'" :stroke-width="6" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Plus,
  Refresh,
  Download,
  Document,
  WarningFilled,
  CircleCheckFilled,
  Timer,
  Search,
  Medal,
  CaretTop,
  CaretBottom
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing...',
  'Almost ready...'
]

// ==================== Data Structures ====================
interface ServiceRequest {
  id: number
  title: string
  category: string
  priority: 'critical' | 'high' | 'medium' | 'low'
  status: 'open' | 'in-progress' | 'resolved' | 'closed'
  reportedBy: string
  assignedTo: string | null
  reportedDate: string
  responseTime: string
  targetTime: string
}

interface SLAPerformance {
  category: string
  targetTime: string
  targetMinutes: number
  avgResponseTime: string
  avgMinutes: number
  requestCount: number
  complianceRate: number
}

// ==================== State ====================
const dateRange = ref<[Date, Date] | null>(null)
const trendPeriod = ref<'week' | 'month' | 'quarter'>('week')
const categoryFilter = ref('all')
const priorityFilter = ref('all')
const statusFilter = ref('all')
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const trendChartRef = ref<HTMLElement | null>(null)
const categoryChartRef = ref<HTMLElement | null>(null)
const priorityChartRef = ref<HTMLElement | null>(null)
let trendChart: echarts.ECharts | null = null
let categoryChart: echarts.ECharts | null = null
let priorityChart: echarts.ECharts | null = null

// ==================== Mock Data ====================
const serviceRequests = ref<ServiceRequest[]>([
  { id: 1001, title: 'AHU-101 Not responding', category: 'HVAC', priority: 'critical', status: 'in-progress', reportedBy: 'John Smith', assignedTo: 'Mike Johnson', reportedDate: '2025-05-28', responseTime: '8 min', targetTime: '15 min' },
  { id: 1002, title: 'Lighting flickering on Floor 2', category: 'Electrical', priority: 'medium', status: 'open', reportedBy: 'Sarah Chen', assignedTo: null, reportedDate: '2025-05-28', responseTime: 'N/A', targetTime: '60 min' },
  { id: 1003, title: 'Water leak in restroom', category: 'Plumbing', priority: 'high', status: 'in-progress', reportedBy: 'Lisa Wong', assignedTo: 'Tom Davis', reportedDate: '2025-05-27', responseTime: '22 min', targetTime: '30 min' },
  { id: 1004, title: 'Restroom cleaning needed', category: 'Cleaning', priority: 'low', status: 'resolved', reportedBy: 'Mike Johnson', assignedTo: 'Jane Lee', reportedDate: '2025-05-27', responseTime: '95 min', targetTime: '120 min' },
  { id: 1005, title: 'Access card not working', category: 'Security', priority: 'high', status: 'resolved', reportedBy: 'John Smith', assignedTo: 'Security Team', reportedDate: '2025-05-26', responseTime: '18 min', targetTime: '30 min' },
  { id: 1006, title: 'Printer offline - IT Room', category: 'IT', priority: 'medium', status: 'closed', reportedBy: 'Sarah Chen', assignedTo: 'IT Support', reportedDate: '2025-05-26', responseTime: '45 min', targetTime: '60 min' },
  { id: 1007, title: 'Chiller high temperature alarm', category: 'HVAC', priority: 'critical', status: 'open', reportedBy: 'Mike Johnson', assignedTo: null, reportedDate: '2025-05-28', responseTime: 'N/A', targetTime: '15 min' },
  { id: 1008, title: 'CCTV camera offline - North Entrance', category: 'Security', priority: 'high', status: 'in-progress', reportedBy: 'Security Team', assignedTo: 'Camera Tech', reportedDate: '2025-05-27', responseTime: '25 min', targetTime: '30 min' },
  { id: 1009, title: 'Meeting room AC not cooling', category: 'HVAC', priority: 'high', status: 'open', reportedBy: 'Lisa Wong', assignedTo: null, reportedDate: '2025-05-28', responseTime: 'N/A', targetTime: '30 min' },
  { id: 1010, title: 'Floor waxing requested', category: 'Cleaning', priority: 'low', status: 'resolved', reportedBy: 'John Smith', assignedTo: 'Cleaning Crew', reportedDate: '2025-05-25', responseTime: '180 min', targetTime: '240 min' },
  { id: 1011, title: 'UPS battery warning', category: 'Electrical', priority: 'critical', status: 'in-progress', reportedBy: 'Facilities', assignedTo: 'Electrical Team', reportedDate: '2025-05-28', responseTime: '5 min', targetTime: '15 min' },
  { id: 1012, title: 'Network switch replacement', category: 'IT', priority: 'medium', status: 'open', reportedBy: 'IT Dept', assignedTo: null, reportedDate: '2025-05-28', responseTime: 'N/A', targetTime: '60 min' }
])

const slaPerformance = ref<SLAPerformance[]>([
  { category: 'HVAC', targetTime: '15 min', targetMinutes: 15, avgResponseTime: '12 min', avgMinutes: 12, requestCount: 28, complianceRate: 92 },
  { category: 'Electrical', targetTime: '30 min', targetMinutes: 30, avgResponseTime: '18 min', avgMinutes: 18, requestCount: 22, complianceRate: 95 },
  { category: 'Plumbing', targetTime: '30 min', targetMinutes: 30, avgResponseTime: '25 min', avgMinutes: 25, requestCount: 15, complianceRate: 88 },
  { category: 'Cleaning', targetTime: '120 min', targetMinutes: 120, avgResponseTime: '95 min', avgMinutes: 95, requestCount: 18, complianceRate: 96 },
  { category: 'Security', targetTime: '30 min', targetMinutes: 30, avgResponseTime: '22 min', avgMinutes: 22, requestCount: 20, complianceRate: 91 },
  { category: 'IT', targetTime: '60 min', targetMinutes: 60, avgResponseTime: '48 min', avgMinutes: 48, requestCount: 12, complianceRate: 94 }
])

// ==================== Computed Values ====================
const totalRequests = computed(() => serviceRequests.value.length)
const openRequests = computed(() => serviceRequests.value.filter(r => r.status === 'open' || r.status === 'in-progress').length)
const resolvedRequests = computed(() => serviceRequests.value.filter(r => r.status === 'resolved' || r.status === 'closed').length)
const criticalRequests = computed(() => serviceRequests.value.filter(r => r.priority === 'critical' && r.status !== 'closed' && r.status !== 'resolved').length)
const resolutionRate = computed(() => Math.round((resolvedRequests.value / totalRequests.value) * 100))
const avgResponseTime = computed(() => '18 min')
const requestTrend = computed(() => 8.5)
const responseTrend = computed(() => -5.2)

const filteredRequests = computed(() => {
  let result = [...serviceRequests.value]
  if (categoryFilter.value !== 'all') {
    result = result.filter(r => r.category === categoryFilter.value)
  }
  if (priorityFilter.value !== 'all') {
    result = result.filter(r => r.priority === priorityFilter.value)
  }
  if (statusFilter.value !== 'all') {
    result = result.filter(r => r.status === statusFilter.value)
  }
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(r =>
        r.title.toLowerCase().includes(search) ||
        r.reportedBy.toLowerCase().includes(search) ||
        r.assignedTo?.toLowerCase().includes(search)
    )
  }
  if (dateRange.value && dateRange.value[0] && dateRange.value[1]) {
    const [start, end] = dateRange.value
    result = result.filter(r => {
      const date = new Date(r.reportedDate)
      return date >= start && date <= end
    })
  }
  return result
})

const paginatedRequests = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRequests.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getPriorityLabel = (priority: string) => {
  const map: Record<string, string> = {
    critical: 'Critical',
    high: 'High',
    medium: 'Medium',
    low: 'Low'
  }
  return map[priority] || priority
}

const getPriorityTagType = (priority: string) => {
  const map: Record<string, string> = {
    critical: 'danger',
    high: 'warning',
    medium: 'primary',
    low: 'info'
  }
  return map[priority] || 'info'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    open: 'Open',
    'in-progress': 'In Progress',
    resolved: 'Resolved',
    closed: 'Closed'
  }
  return map[status] || status
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    open: 'danger',
    'in-progress': 'warning',
    resolved: 'success',
    closed: 'info'
  }
  return map[status] || 'info'
}

const getResponseTimeClass = (responseTime: string, targetTime: string) => {
  if (responseTime === 'N/A') return 'text-muted'
  const response = parseInt(responseTime)
  const target = parseInt(targetTime)
  return response <= target ? 'text-success' : 'text-danger'
}

const dateShortcuts = [
  { text: 'Last 7 Days', value: () => { const end = new Date(); const start = new Date(); start.setDate(start.getDate() - 7); return [start, end] } },
  { text: 'Last 30 Days', value: () => { const end = new Date(); const start = new Date(); start.setDate(start.getDate() - 30); return [start, end] } },
  { text: 'This Month', value: () => { const end = new Date(); const start = new Date(); start.setDate(1); return [start, end] } }
]

// ==================== Chart Functions ====================
const generateTrendData = () => {
  if (trendPeriod.value === 'week') {
    return {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      created: [8, 12, 10, 14, 9, 3, 2],
      resolved: [7, 10, 11, 12, 8, 4, 1]
    }
  }
  if (trendPeriod.value === 'month') {
    const days = Array.from({ length: 30 }, (_, i) => `${i + 1}`)
    const created = days.map(() => Math.floor(5 + Math.random() * 15))
    const resolved = days.map((_, i) => Math.floor(created[i] * 0.85))
    return { labels: days, created, resolved }
  }
  return {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    created: [45, 52, 48, 55, 58, 52],
    resolved: [42, 48, 45, 50, 54, 48]
  }
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)
  const data = generateTrendData()

  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Requests Created', 'Requests Resolved'], bottom: 0 },
    grid: { left: '3%', right: '4%', top: '10%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', data: data.labels, axisLabel: { rotate: trendPeriod.value === 'month' ? 45 : 0, interval: trendPeriod.value === 'month' ? 5 : 0 } },
    yAxis: { type: 'value', name: 'Number of Requests' },
    series: [
      { name: 'Requests Created', type: 'line', data: data.created, smooth: true, symbol: 'circle', lineStyle: { width: 3, color: '#409eff' }, areaStyle: { opacity: 0.1, color: '#409eff' } },
      { name: 'Requests Resolved', type: 'line', data: data.resolved, smooth: true, symbol: 'diamond', lineStyle: { width: 2, color: '#67c23a' }, areaStyle: { opacity: 0.1, color: '#67c23a' } }
    ]
  })
}

const initCategoryChart = () => {
  if (!categoryChartRef.value) return
  if (categoryChart) categoryChart.dispose()

  categoryChart = echarts.init(categoryChartRef.value)

  const categories = ['HVAC', 'Electrical', 'Plumbing', 'Cleaning', 'Security', 'IT']
  const counts = [28, 22, 15, 18, 20, 12]

  categoryChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '10%', right: '5%', top: '5%', bottom: '5%', containLabel: true },
    xAxis: { type: 'value', name: 'Number of Requests' },
    yAxis: { type: 'category', data: categories },
    series: [{
      type: 'bar', data: counts,
      itemStyle: { borderRadius: [0, 4, 4, 0], color: '#409eff' },
      label: { show: true, position: 'right' }
    }]
  })
}

const initPriorityChart = () => {
  if (!priorityChartRef.value) return
  if (priorityChart) priorityChart.dispose()

  priorityChart = echarts.init(priorityChartRef.value)

  priorityChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} requests ({d}%)' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      type: 'pie', radius: '55%', center: ['50%', '50%'],
      data: [
        { name: 'Critical', value: 8, itemStyle: { color: '#f56c6c' } },
        { name: 'High', value: 14, itemStyle: { color: '#e6a23c' } },
        { name: 'Medium', value: 22, itemStyle: { color: '#409eff' } },
        { name: 'Low', value: 14, itemStyle: { color: '#67c23a' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 }
    }]
  })
}

// ==================== Actions ====================
const refreshData = async () => {
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  ElMessage.success('Service requests data refreshed')
  initTrendChart()
  initCategoryChart()
  initPriorityChart()
  tableLoading.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting service requests report...')
}

const createRequest = () => {
  ElMessage.info('Create new service request')
}

const viewRequest = (row: ServiceRequest) => {
  ElMessage.info(`Viewing request #${row.id}`)
}

const updateRequest = (row: ServiceRequest) => {
  ElMessage.info(`Updating request #${row.id}`)
}

const fetchTrendData = () => {
  initTrendChart()
}

const handleDateChange = () => {
  currentPage.value = 1
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Window Resize Handler ====================
const handleResize = () => {
  trendChart?.resize()
  categoryChart?.resize()
  priorityChart?.resize()
}

// ==================== Lifecycle ====================
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
      setTimeout(() => {
        initTrendChart()
        initCategoryChart()
        initPriorityChart()
      }, 100)
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  categoryChart?.dispose()
  priorityChart?.dispose()
})
</script>

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

.spinner-ring:nth-child(1) { border-top-color: #3b82f6; animation-delay: 0s; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }

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
.service-requests-page {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-title h1 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2f3d;
  margin: 0 0 4px 0;
}

.header-title .subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* KPI Cards */
.kpi-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.kpi-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s, box-shadow 0.2s;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.kpi-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.kpi-card.total .kpi-icon { background: #e8f4ff; color: #409eff; }
.kpi-card.open .kpi-icon { background: #ffe8e8; color: #f56c6c; }
.kpi-card.resolved .kpi-icon { background: #e8f8f0; color: #67c23a; }
.kpi-card.response .kpi-icon { background: #fff7e8; color: #e6a23c; }

.kpi-info {
  flex: 1;
}

.kpi-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
  line-height: 1.2;
}

.kpi-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.kpi-sub {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 2px;
}

.kpi-trend {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 13px;
  font-weight: 500;
}

.kpi-trend.positive { color: #67c23a; }
.kpi-trend.negative { color: #f56c6c; }

/* Chart Cards */
.chart-card, .table-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.card-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: #1f2f3d;
}

.header-filters {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.chart-container {
  height: 320px;
  width: 100%;
}

.two-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

/* Table Styles */
.text-success {
  color: #67c23a;
  font-weight: 500;
}

.text-danger {
  color: #f56c6c;
  font-weight: 500;
}

.text-muted {
  color: #c0c4cc;
  font-style: italic;
}

.pagination-wrapper {
  padding: 20px 0 0;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
  margin-top: 16px;
}

/* SLA Section */
.sla-section {
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1f2f3d;
}

.sla-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.sla-card {
  background: #fafafa;
  border-radius: 14px;
  padding: 16px;
  transition: all 0.2s;
}

.sla-card:hover {
  background: #f5f7fa;
  transform: translateY(-2px);
}

.sla-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.sla-category {
  font-weight: 600;
  font-size: 15px;
  color: #1f2f3d;
}

.sla-rate {
  font-weight: 700;
  font-size: 18px;
}

.sla-metrics {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  gap: 12px;
}

.sla-metrics .metric {
  flex: 1;
  text-align: center;
}

.sla-metrics .metric-label {
  display: block;
  font-size: 11px;
  color: #909399;
  margin-bottom: 4px;
}

.sla-metrics .metric-value {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #1f2f3d;
}

:deep(.el-table) {
  border-radius: 12px;
}

:deep(.el-table th.el-table__cell) {
  background-color: #fafafa;
  font-weight: 600;
  color: #1f2f3d;
}
</style>