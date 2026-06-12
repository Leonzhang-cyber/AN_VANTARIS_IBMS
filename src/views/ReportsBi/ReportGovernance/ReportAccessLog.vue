<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Search, Refresh, Document, Download,
  Share, Star, Clock, Warning, CircleCheck,
  TrendCharts, DataLine, Calendar, Setting,
  Plus, Upload, Filter, ArrowUp, ArrowDown,
  View, User, Trophy, Medal, Edit, Delete,
  CopyDocument,
  Iphone, DataAnalysis, List
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Loading access logs...',
  'Analyzing user activity...',
  'Preparing audit trail...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedAction = ref('all')
const selectedUser = ref('all')
const logDetailsVisible = ref(false)
const userStatsVisible = ref(false)
const chartRef = ref<HTMLElement | null>(null)
const trendChartRef = ref<HTMLElement | null>(null)

let actionChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null

// Action filters
const actionOptions = [
  { value: 'all', label: 'All Actions' },
  { value: 'view', label: 'View', icon: '👁️' },
  { value: 'download', label: 'Download', icon: '📥' },
  { value: 'share', label: 'Share', icon: '🔗' },
  { value: 'export', label: 'Export', icon: '📤' },
  { value: 'print', label: 'Print', icon: '🖨️' }
]

// User options
const userOptions = [
  { value: 'all', label: 'All Users' },
  { value: 'john.smith', label: 'John Smith' },
  { value: 'sarah.j', label: 'Sarah Johnson' },
  { value: 'mike.chen', label: 'Mike Chen' },
  { value: 'emily.w', label: 'Emily Wong' },
  { value: 'david.lee', label: 'David Lee' }
]

// Access logs data
interface AccessLog {
  id: string
  user: string
  userName: string
  action: string
  report: string
  timestamp: string
  ip: string
  device: string
  duration: string | null
  status: string
  reportId: string
  department: string
}

const accessLogs = ref<AccessLog[]>([
  {
    id: 'LOG001', user: 'john.smith@system.com', userName: 'John Smith',
    action: 'view', report: 'Executive Dashboard Q1', timestamp: '2024-01-15 10:30:22',
    ip: '192.168.1.105', device: 'Desktop - Chrome', duration: '5m 23s',
    status: 'success', reportId: 'RPT001', department: 'Executive'
  },
  {
    id: 'LOG002', user: 'sarah.j@system.com', userName: 'Sarah Johnson',
    action: 'download', report: 'Energy Consumption Report', timestamp: '2024-01-15 09:45:12',
    ip: '192.168.1.108', device: 'Laptop - Firefox', duration: null,
    status: 'success', reportId: 'RPT002', department: 'Energy'
  },
  {
    id: 'LOG003', user: 'mike.chen@system.com', userName: 'Mike Chen',
    action: 'share', report: 'Financial Summary January', timestamp: '2024-01-15 09:15:33',
    ip: '192.168.1.110', device: 'Mobile - Safari', duration: null,
    status: 'success', reportId: 'RPT003', department: 'Finance'
  },
  {
    id: 'LOG004', user: 'emily.w@system.com', userName: 'Emily Wong',
    action: 'export', report: 'Sustainability Report', timestamp: '2024-01-14 16:20:45',
    ip: '192.168.1.112', device: 'Desktop - Edge', duration: null,
    status: 'success', reportId: 'RPT006', department: 'Sustainability'
  },
  {
    id: 'LOG005', user: 'david.lee@system.com', userName: 'David Lee',
    action: 'view', report: 'Security Audit Log', timestamp: '2024-01-14 14:50:18',
    ip: '192.168.1.115', device: 'Laptop - Chrome', duration: '12m 05s',
    status: 'success', reportId: 'RPT004', department: 'Security'
  },
  {
    id: 'LOG006', user: 'lisa.tan@system.com', userName: 'Lisa Tan',
    action: 'download', report: 'Sales Performance Dashboard', timestamp: '2024-01-14 11:30:55',
    ip: '192.168.1.118', device: 'Desktop - Firefox', duration: null,
    status: 'failed', reportId: 'RPT007', department: 'Sales'
  },
  {
    id: 'LOG007', user: 'robert.w@system.com', userName: 'Robert Wilson',
    action: 'print', report: 'Maintenance Dashboard', timestamp: '2024-01-14 09:25:30',
    ip: '192.168.1.120', device: 'Laptop - Chrome', duration: null,
    status: 'success', reportId: 'RPT005', department: 'Operations'
  },
  {
    id: 'LOG008', user: 'james.w@system.com', userName: 'James Wilson',
    action: 'view', report: 'Inventory Analysis', timestamp: '2024-01-13 15:40:12',
    ip: '192.168.1.122', device: 'Tablet - Safari', duration: '8m 45s',
    status: 'success', reportId: 'RPT008', department: 'Supply Chain'
  },
  {
    id: 'LOG009', user: 'john.smith@system.com', userName: 'John Smith',
    action: 'share', report: 'Executive Dashboard Q1', timestamp: '2024-01-13 13:15:22',
    ip: '192.168.1.105', device: 'Desktop - Chrome', duration: null,
    status: 'success', reportId: 'RPT001', department: 'Executive'
  },
  {
    id: 'LOG010', user: 'sarah.j@system.com', userName: 'Sarah Johnson',
    action: 'view', report: 'Energy Consumption Report', timestamp: '2024-01-13 10:55:33',
    ip: '192.168.1.108', device: 'Laptop - Firefox', duration: '3m 12s',
    status: 'success', reportId: 'RPT002', department: 'Energy'
  },
  {
    id: 'LOG011', user: 'mike.chen@system.com', userName: 'Mike Chen',
    action: 'export', report: 'Financial Summary January', timestamp: '2024-01-12 09:30:45',
    ip: '192.168.1.110', device: 'Mobile - Safari', duration: null,
    status: 'success', reportId: 'RPT003', department: 'Finance'
  },
  {
    id: 'LOG012', user: 'emily.w@system.com', userName: 'Emily Wong',
    action: 'view', report: 'Sustainability Report', timestamp: '2024-01-12 14:20:18',
    ip: '192.168.1.112', device: 'Desktop - Edge', duration: '6m 50s',
    status: 'success', reportId: 'RPT006', department: 'Sustainability'
  }
])

// Access statistics
const accessStats = reactive({
  total: 0,
  views: 0,
  downloads: 0,
  shares: 0,
  exports: 0,
  prints: 0,
  success: 0,
  failed: 0,
  uniqueUsers: 0,
  uniqueReports: 0
})

// User activity stats
const userActivityStats = ref<Array<{name: string, count: number}>>([])

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: accessLogs.value.length
})

// Filtered logs
const filteredLogs = computed(() => {
  let filtered = accessLogs.value
  if (searchKeyword.value) {
    filtered = filtered.filter(l =>
        l.report.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        l.userName.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        l.ip.includes(searchKeyword.value)
    )
  }
  if (selectedAction.value !== 'all') {
    filtered = filtered.filter(l => l.action === selectedAction.value)
  }
  if (selectedUser.value !== 'all') {
    filtered = filtered.filter(l => l.user.split('@')[0] === selectedUser.value)
  }
  pagination.total = filtered.length
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// ==================== Helper Functions ====================
const getLast7Days = () => {
  const days = []
  for (let i = 6; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    days.push(date.toISOString().split('T')[0])
  }
  return days
}

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

  actionChart = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  const views = accessLogs.value.filter(l => l.action === 'view').length
  const downloads = accessLogs.value.filter(l => l.action === 'download').length
  const shares = accessLogs.value.filter(l => l.action === 'share').length
  const exports = accessLogs.value.filter(l => l.action === 'export').length
  const prints = accessLogs.value.filter(l => l.action === 'print').length

  actionChart?.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c})' },
    legend: { orient: 'vertical', left: 'left', data: ['View', 'Download', 'Share', 'Export', 'Print'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { name: 'View', value: views, itemStyle: { color: '#409EFF' } },
        { name: 'Download', value: downloads, itemStyle: { color: '#67C23A' } },
        { name: 'Share', value: shares, itemStyle: { color: '#E6A23C' } },
        { name: 'Export', value: exports, itemStyle: { color: '#9B59B6' } },
        { name: 'Print', value: prints, itemStyle: { color: '#F56C6C' } }
      ],
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })
}

const initTrendChart = () => {
  if (!trendChartRef.value) return

  const last7Days = getLast7Days()
  const dailyData = last7Days.map(day => ({
    date: day,
    count: accessLogs.value.filter(l => l.timestamp.startsWith(day)).length
  }))

  trendChart = echarts.init(trendChartRef.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: dailyData.map(d => d.date.substring(5)) },
    yAxis: { type: 'value', name: 'Access Count' },
    series: [{
      type: 'line',
      data: dailyData.map(d => d.count),
      smooth: true,
      lineStyle: { color: '#409EFF', width: 3 },
      areaStyle: { opacity: 0.1, color: '#409EFF' },
      symbol: 'circle',
      symbolSize: 8,
      label: { show: true, position: 'top' }
    }]
  })
}

const updateStats = () => {
  accessStats.total = accessLogs.value.length
  accessStats.views = accessLogs.value.filter(l => l.action === 'view').length
  accessStats.downloads = accessLogs.value.filter(l => l.action === 'download').length
  accessStats.shares = accessLogs.value.filter(l => l.action === 'share').length
  accessStats.exports = accessLogs.value.filter(l => l.action === 'export').length
  accessStats.prints = accessLogs.value.filter(l => l.action === 'print').length
  accessStats.success = accessLogs.value.filter(l => l.status === 'success').length
  accessStats.failed = accessLogs.value.filter(l => l.status === 'failed').length

  const uniqueUsers = new Set(accessLogs.value.map(l => l.user)).size
  const uniqueReports = new Set(accessLogs.value.map(l => l.reportId)).size
  accessStats.uniqueUsers = uniqueUsers
  accessStats.uniqueReports = uniqueReports

  // Calculate user activity
  const userMap = new Map<string, {name: string, count: number}>()
  accessLogs.value.forEach(log => {
    const userName = log.userName
    if (!userMap.has(userName)) {
      userMap.set(userName, { name: userName, count: 0 })
    }
    const entry = userMap.get(userName)!
    entry.count++
  })
  userActivityStats.value = Array.from(userMap.values()).sort((a, b) => b.count - a.count).slice(0, 5)

  updateChart()
}

const handleResize = () => {
  actionChart?.resize()
  trendChart?.resize()
}

// ==================== Log Functions ====================
const refreshLogs = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  loading.value = false
  ElMessage.success('Access logs refreshed successfully')
}

const viewLogDetails = (log: AccessLog) => {
  selectedLog.value = log
  logDetailsVisible.value = true
}

const viewUserStats = () => {
  userStatsVisible.value = true
}

const exportLogs = () => {
  const data = accessLogs.value.map(l => ({
    ID: l.id,
    User: l.userName,
    Action: l.action,
    Report: l.report,
    Timestamp: l.timestamp,
    IP: l.ip,
    Device: l.device,
    Status: l.status,
    Duration: l.duration || 'N/A'
  }))

  const csv = convertToCSV(data)
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `access_logs_${new Date().toISOString()}.csv`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Access logs exported successfully')
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

const getActionIcon = (action: string) => {
  switch (action) {
    case 'view': return '👁️'
    case 'download': return '📥'
    case 'share': return '🔗'
    case 'export': return '📤'
    case 'print': return '🖨️'
    default: return '📄'
  }
}

const getDeviceIcon = (device: string) => {
  if (device.includes('Desktop')) return '🖥️'
  if (device.includes('Laptop')) return '💻'
  if (device.includes('Mobile')) return '📱'
  if (device.includes('Tablet')) return '📟'
  return '💻'
}

const formatDuration = (duration: string | null) => {
  return duration || 'N/A'
}

const selectedLog = ref<AccessLog | null>(null)
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
          <span class="loading-title">Loading Report Access Log</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Report Governance - Access Log</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="access-log-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Report Access Log</h1>
        <p class="page-subtitle">Track and monitor user access to reports and dashboards</p>
      </div>
      <div class="header-right">
        <el-button size="large" @click="exportLogs">
          <el-icon><Download /></el-icon>
          Export Logs
        </el-button>
        <el-button size="large" @click="viewUserStats">
          <el-icon><DataAnalysis /></el-icon>
          User Statistics
        </el-button>
        <el-button size="large" @click="refreshLogs" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total-icon">
          <el-icon><List /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ accessStats.total }}</div>
          <div class="stat-label">Total Accesses</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ accessStats.uniqueUsers }} Active Users</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon views-icon">
          <el-icon><Monitor /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ accessStats.views }}</div>
          <div class="stat-label">Views</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">Most common action</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon downloads-icon">
          <el-icon><Download /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ accessStats.downloads }}</div>
          <div class="stat-label">Downloads</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ accessStats.exports }} Exports</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon success-icon">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ accessStats.success }}</div>
          <div class="stat-label">Successful</div>
        </div>
        <div class="stat-trend">
          <span class="trend-neutral">{{ accessStats.failed }} Failed</span>
        </div>
      </div>
    </div>

    <!-- Stats Breakdown Row -->
    <div class="stats-breakdown">
      <div class="breakdown-item">
        <span class="breakdown-label">Unique Reports</span>
        <span class="breakdown-value">{{ accessStats.uniqueReports }}</span>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: (accessStats.uniqueReports / 20) * 100 + '%', background: '#409EFF' }"></div>
        </div>
      </div>
      <div class="breakdown-item">
        <span class="breakdown-label">Unique Users</span>
        <span class="breakdown-value">{{ accessStats.uniqueUsers }}</span>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: (accessStats.uniqueUsers / 15) * 100 + '%', background: '#67C23A' }"></div>
        </div>
      </div>
      <div class="breakdown-item">
        <span class="breakdown-label">Avg per User</span>
        <span class="breakdown-value">{{ accessStats.uniqueUsers ? Math.round(accessStats.total / accessStats.uniqueUsers) : 0 }}</span>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: (accessStats.uniqueUsers ? (Math.round(accessStats.total / accessStats.uniqueUsers) / 20) * 100 : 0) + '%', background: '#E6A23C' }"></div>
        </div>
      </div>
      <div class="breakdown-item">
        <span class="breakdown-label">Success Rate</span>
        <span class="breakdown-value">{{ accessStats.total ? Math.round((accessStats.success / accessStats.total) * 100) : 0 }}%</span>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: accessStats.total ? (accessStats.success / accessStats.total) * 100 + '%' : '0%', background: '#67C23A' }"></div>
        </div>
      </div>
    </div>

    <!-- Chart Section -->
    <div class="charts-row">
      <div class="chart-section">
        <div class="section-header">
          <h3>Action Distribution</h3>
          <el-button text type="primary" @click="updateChart">Refresh</el-button>
        </div>
        <div ref="chartRef" class="action-chart" style="height: 280px"></div>
      </div>

      <div class="chart-section">
        <div class="section-header">
          <h3>Access Trend (Last 7 Days)</h3>
          <el-button text type="primary" @click="initTrendChart">Refresh</el-button>
        </div>
        <div ref="trendChartRef" class="trend-chart" style="height: 280px"></div>
      </div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-bar">
      <div class="filters-left">
        <div class="search-box">
          <el-input
              v-model="searchKeyword"
              placeholder="Search by report, user, or IP..."
              :prefix-icon="Search"
              clearable
              style="width: 260px"
          />
        </div>
        <div class="action-filters">
          <button
              v-for="action in actionOptions"
              :key="action.value"
              class="action-chip"
              :class="{ active: selectedAction === action.value }"
              @click="selectedAction = action.value"
          >
            <span class="chip-icon">{{ action.icon }}</span>
            <span>{{ action.label }}</span>
          </button>
        </div>
      </div>
      <div class="filters-right">
        <el-select v-model="selectedUser" placeholder="User" clearable style="width: 160px">
          <el-option v-for="u in userOptions.slice(1)" :key="u.value" :label="u.label" :value="u.value" />
        </el-select>
      </div>
    </div>

    <!-- Access Logs Table -->
    <el-card shadow="never" class="logs-card">
      <template #header>
        <div class="table-header">
          <span>Access Logs</span>
          <div class="table-actions">
            <el-tag type="info" size="small">{{ filteredLogs.length }} records found</el-tag>
          </div>
        </div>
      </template>

      <el-table :data="filteredLogs" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="userName" label="User" width="130" />
        <el-table-column label="Action" width="100" align="center">
          <template #default="{ row }">
            <div class="action-badge">
              <span class="action-icon">{{ getActionIcon(row.action) }}</span>
              <span>{{ row.action.toUpperCase() }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="report" label="Report" min-width="200" />
        <el-table-column prop="timestamp" label="Timestamp" width="160" />
        <el-table-column label="Device" width="160">
          <template #default="{ row }">
            <div class="device-info">
              <span class="device-icon">{{ getDeviceIcon(row.device) }}</span>
              <span>{{ row.device }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="ip" label="IP Address" width="130" />
        <el-table-column label="Duration" width="100" align="center">
          <template #default="{ row }">
            {{ formatDuration(row.duration) }}
          </template>
        </el-table-column>
        <el-table-column label="Status" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
              {{ row.status === 'success' ? 'Success' : 'Failed' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewLogDetails(row)">
              Details
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

    <!-- Log Details Dialog -->
    <el-dialog v-model="logDetailsVisible" :title="`Access Log Details - ${selectedLog?.id}`" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Log ID">{{ selectedLog?.id }}</el-descriptions-item>
        <el-descriptions-item label="User">{{ selectedLog?.userName }}</el-descriptions-item>
        <el-descriptions-item label="Email">{{ selectedLog?.user }}</el-descriptions-item>
        <el-descriptions-item label="Department">{{ selectedLog?.department }}</el-descriptions-item>
        <el-descriptions-item label="Action">
          <span class="action-icon">{{ getActionIcon(selectedLog?.action || '') }}</span>
          {{ selectedLog?.action?.toUpperCase() }}
        </el-descriptions-item>
        <el-descriptions-item label="Report">{{ selectedLog?.report }}</el-descriptions-item>
        <el-descriptions-item label="Report ID">{{ selectedLog?.reportId }}</el-descriptions-item>
        <el-descriptions-item label="Timestamp">{{ selectedLog?.timestamp }}</el-descriptions-item>
        <el-descriptions-item label="IP Address">{{ selectedLog?.ip }}</el-descriptions-item>
        <el-descriptions-item label="Device">{{ selectedLog?.device }}</el-descriptions-item>
        <el-descriptions-item label="Duration">{{ selectedLog?.duration || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="selectedLog?.status === 'success' ? 'success' : 'danger'" size="small">
            {{ selectedLog?.status?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="logDetailsVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- User Statistics Dialog -->
    <el-dialog v-model="userStatsVisible" title="User Activity Statistics" width="700px">
      <div class="user-stats">
        <div class="stats-summary">
          <div class="summary-item">
            <span class="summary-label">Total Active Users</span>
            <span class="summary-value">{{ accessStats.uniqueUsers }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Total Actions</span>
            <span class="summary-value">{{ accessStats.total }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Actions per User</span>
            <span class="summary-value">{{ accessStats.uniqueUsers ? Math.round(accessStats.total / accessStats.uniqueUsers) : 0 }}</span>
          </div>
        </div>

        <el-divider />

        <h4>Top Active Users</h4>
        <el-table :data="userActivityStats" stripe>
          <el-table-column prop="name" label="User Name" min-width="200" />
          <el-table-column label="Actions" width="200" align="center">
            <template #default="{ row }">
              <el-progress :percentage="(row.count / accessStats.total) * 100" :stroke-width="8" :show-text="false" />
              <span>{{ row.count }} actions</span>
            </template>
          </el-table-column>
          <el-table-column label="Percentage" width="120" align="center">
            <template #default="{ row }">
              {{ accessStats.total ? Math.round((row.count / accessStats.total) * 100) : 0 }}%
            </template>
          </el-table-column>
        </el-table>

        <el-divider />

        <h4>Activity by Action Type</h4>
        <div class="action-stats">
          <div class="action-stat" v-for="action in actionOptions.slice(1)" :key="action.value">
            <span class="action-icon">{{ action.icon }}</span>
            <span class="action-name">{{ action.label }}</span>
            <span class="action-count">{{ accessStats[action.value + 's' as keyof typeof accessStats] || 0 }}</span>
            <el-progress :percentage="accessStats.total ? ((accessStats[action.value + 's' as keyof typeof accessStats] as number || 0) / accessStats.total) * 100 : 0" :stroke-width="6" />
          </div>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="userStatsVisible = false">Close</el-button>
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
.access-log-container {
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

.downloads-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.success-icon {
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

/* Charts Row */
.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.chart-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
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

.action-chart,
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

.action-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-chip {
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

.action-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.action-chip.active {
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

/* Logs Card */
.logs-card {
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

/* Table Cell Styles */
.action-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.action-icon {
  font-size: 14px;
}

.device-info {
  display: flex;
  align-items: center;
  gap: 6px;
}

.device-icon {
  font-size: 14px;
}

/* Dialog Styles */
.user-stats {
  max-height: 500px;
  overflow-y: auto;
}

.stats-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.summary-item {
  text-align: center;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 12px;
}

.summary-label {
  font-size: 12px;
  color: #909399;
  display: block;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.action-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-stat {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 8px;
}

.action-stat .action-icon {
  font-size: 20px;
  width: 40px;
}

.action-stat .action-name {
  width: 80px;
  font-weight: 500;
}

.action-stat .action-count {
  width: 60px;
  font-weight: 600;
  color: #409eff;
}

.action-stat .el-progress {
  flex: 1;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-breakdown {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .access-log-container {
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

  .action-filters {
    justify-content: center;
  }

  .page-header {
    flex-direction: column;
    text-align: center;
  }

  .header-right {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }

  .stats-summary {
    grid-template-columns: 1fr;
  }

  .action-stat {
    flex-wrap: wrap;
  }
}
</style>