<template>
  <!-- Loading Screen -->
  <div v-if="!isLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
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
        <div class="loading-tip">Alarm History</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="alarm-history-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-left">
        <h1 class="dashboard-title">
          <el-icon><Clock /></el-icon>
          Alarm History
        </h1>
        <div class="header-stats">
          <div class="stat-badge">
            <el-icon><Document /></el-icon>
            {{ totalAlarms }} Total Records
          </div>
          <div class="stat-badge">
            <el-icon><Calendar /></el-icon>
            Last 30 Days
          </div>
        </div>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="exportReport" :loading="exporting">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-group">
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            :shortcuts="dateShortcuts"
            size="default"
            style="width: 300px"
        />
        <el-select v-model="severityFilter" placeholder="Severity" size="default" style="width: 130px" clearable>
          <el-option label="All" value="all" />
          <el-option label="Critical" value="critical" />
          <el-option label="Major" value="major" />
          <el-option label="Warning" value="warning" />
          <el-option label="Info" value="info" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" size="default" style="width: 130px" clearable>
          <el-option label="All" value="all" />
          <el-option label="Resolved" value="resolved" />
          <el-option label="Acknowledged" value="acknowledged" />
          <el-option label="Escalated" value="escalated" />
        </el-select>
        <el-input v-model="searchText" placeholder="Search alarms..." size="default" style="width: 220px" clearable>
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <div class="stat-card critical">
        <div class="stat-icon">🔴</div>
        <div class="stat-info">
          <div class="stat-value">{{ criticalCount }}</div>
          <div class="stat-label">Critical</div>
        </div>
      </div>
      <div class="stat-card major">
        <div class="stat-icon">🟠</div>
        <div class="stat-info">
          <div class="stat-value">{{ majorCount }}</div>
          <div class="stat-label">Major</div>
        </div>
      </div>
      <div class="stat-card warning">
        <div class="stat-icon">🟡</div>
        <div class="stat-info">
          <div class="stat-value">{{ warningCount }}</div>
          <div class="stat-label">Warning</div>
        </div>
      </div>
      <div class="stat-card info">
        <div class="stat-icon">🔵</div>
        <div class="stat-info">
          <div class="stat-value">{{ infoCount }}</div>
          <div class="stat-label">Info</div>
        </div>
      </div>
      <div class="stat-card resolved">
        <div class="stat-icon">✅</div>
        <div class="stat-info">
          <div class="stat-value">{{ resolvedCount }}</div>
          <div class="stat-label">Resolved</div>
        </div>
      </div>
      <div class="stat-card avg">
        <div class="stat-icon">⏱️</div>
        <div class="stat-info">
          <div class="stat-value">{{ avgResolutionTime }}<span class="unit">min</span></div>
          <div class="stat-label">Avg Resolution</div>
        </div>
      </div>
    </div>

    <!-- Trend Chart -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><TrendCharts /></el-icon>
          Alarm Trend (Last 30 Days)
        </div>
        <el-radio-group v-model="trendPeriod" size="small">
          <el-radio-button label="week">Weekly</el-radio-button>
          <el-radio-button label="month">Monthly</el-radio-button>
        </el-radio-group>
      </div>
      <div ref="trendChartRef" class="trend-chart"></div>
    </div>

    <!-- Alarm History Table -->
    <div class="card table-card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><List /></el-icon>
          Alarm History Records
        </div>
        <div class="table-info">
          Showing {{ paginatedAlarms.length }} of {{ filteredAlarms.length }} records
        </div>
      </div>
      <el-table :data="paginatedAlarms" stripe border style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="id" label="ID" width="80" sortable />
        <el-table-column prop="time" label="Date & Time" width="160" sortable />
        <el-table-column prop="title" label="Alarm Title" min-width="200" />
        <el-table-column prop="severity" label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityTag(row.severity)" size="small">
              {{ row.severity.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="Category" width="120" />
        <el-table-column prop="location" label="Location" min-width="150" />
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resolutionTime" label="Resolution Time" width="120" sortable>
          <template #default="{ row }">
            {{ row.resolutionTime }} min
          </template>
        </el-table-column>
        <el-table-column prop="resolvedBy" label="Resolved By" width="120" />
        <el-table-column label="Actions" fixed="right" width="100">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetails(row)">
              Details
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="card-footer">
        <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="filteredAlarms.length"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handlePageSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Alarm Details - ${selectedAlarm?.title}`" width="600px">
      <el-descriptions :column="2" border v-if="selectedAlarm">
        <el-descriptions-item label="Alarm ID">#{{ selectedAlarm.id }}</el-descriptions-item>
        <el-descriptions-item label="Severity">
          <el-tag :type="getSeverityTag(selectedAlarm.severity)">{{ selectedAlarm.severity.toUpperCase() }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Title" :span="2">{{ selectedAlarm.title }}</el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedAlarm.description }}</el-descriptions-item>
        <el-descriptions-item label="Location">{{ selectedAlarm.location }}</el-descriptions-item>
        <el-descriptions-item label="Category">{{ selectedAlarm.category }}</el-descriptions-item>
        <el-descriptions-item label="Occurred At">{{ selectedAlarm.time }}</el-descriptions-item>
        <el-descriptions-item label="Resolved At">{{ selectedAlarm.resolvedAt || '-' }}</el-descriptions-item>
        <el-descriptions-item label="Resolution Time">{{ selectedAlarm.resolutionTime }} minutes</el-descriptions-item>
        <el-descriptions-item label="Status">{{ selectedAlarm.status }}</el-descriptions-item>
        <el-descriptions-item label="Resolved By">{{ selectedAlarm.resolvedBy || '-' }}</el-descriptions-item>
        <el-descriptions-item label="Resolution Notes" :span="2">{{ selectedAlarm.resolutionNotes || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { Clock, Document, Calendar, Download, Refresh, Search, TrendCharts, List } from '@element-plus/icons-vue'
import { useCounterStore } from '@/stores/counter.js'
import { getCurrentInstance } from 'vue'

const getStore = () => {
  const instance = getCurrentInstance()
  if (!instance) throw new Error('useStore() must be called within a setup function')
  const pinia = instance.appContext.config.globalProperties.$pinia
  if (!pinia) throw new Error('Pinia instance not found')
  return useCounterStore(pinia)
}
const counterStore = getStore()
const isFullscreen = computed(() => counterStore.isFullscreen)
const route = useRoute()

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const refreshing = ref(false)
const exporting = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading alarm history...',
  'Analyzing data...',
  'Initializing dashboard...',
  'Almost ready...'
]

// ==================== Date Shortcuts ====================
const dateShortcuts = [
  { text: 'Last 7 days', value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 7 * 24 * 60 * 60 * 1000)
      return [start, end]
    }},
  { text: 'Last 30 days', value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 30 * 24 * 60 * 60 * 1000)
      return [start, end]
    }},
  { text: 'Last 90 days', value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 90 * 24 * 60 * 60 * 1000)
      return [start, end]
    }}
]

// ==================== Data State ====================
const dateRange = ref<[Date, Date] | null>(null)
const severityFilter = ref('all')
const statusFilter = ref('all')
const searchText = ref('')
const trendPeriod = ref('month')
const detailDialogVisible = ref(false)
const selectedAlarm = ref<any>(null)

const pagination = ref({ page: 1, pageSize: 20 })

// Alarm History Data
interface AlarmHistory {
  id: number
  time: string
  title: string
  description: string
  severity: string
  category: string
  location: string
  status: string
  resolutionTime: number
  resolvedAt: string | null
  resolvedBy: string | null
  resolutionNotes: string | null
}

const alarmHistory = ref<AlarmHistory[]>([])

// Generate mock alarm history data
const generateAlarmHistory = (): AlarmHistory[] => {
  const severities = ['critical', 'major', 'warning', 'info']
  const categories = ['Environmental', 'Power', 'Cooling', 'Network', 'Security', 'Performance', 'Storage']
  const locations = ['Data Center', 'Server Room A', 'Server Room B', 'Electrical Room', 'HVAC Room', 'Network Rack', 'Storage Room']
  const statuses = ['Resolved', 'Acknowledged', 'Escalated']
  const resolvedBy = ['John Doe', 'Sarah Chen', 'Mike Lim', 'System Auto', 'David Wong', 'Lisa Tan']

  const alarms: AlarmHistory[] = []
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - 90)

  for (let i = 1; i <= 156; i++) {
    const randomDays = Math.floor(Math.random() * 90)
    const alarmDate = new Date(startDate)
    alarmDate.setDate(startDate.getDate() + randomDays)

    const severity = severities[Math.floor(Math.random() * severities.length)]
    const category = categories[Math.floor(Math.random() * categories.length)]
    const status = statuses[Math.floor(Math.random() * statuses.length)]
    const resolutionTime = severity === 'critical' ? Math.floor(15 + Math.random() * 30) :
        severity === 'major' ? Math.floor(20 + Math.random() * 40) :
            severity === 'warning' ? Math.floor(30 + Math.random() * 60) :
                Math.floor(10 + Math.random() * 30)

    const titles: Record<string, string[]> = {
      critical: ['Temperature Critical', 'UPS Overload', 'Chiller Failure', 'Fire Alarm', 'Network Core Down'],
      major: ['High CPU Usage', 'Memory Threshold', 'Disk Space Warning', 'Network Latency Spike', 'Cooling Inefficiency'],
      warning: ['Humidity High', 'Fan Speed High', 'Failed Login Attempts', 'Certificate Expiring', 'Memory Usage Warning'],
      info: ['System Startup', 'Backup Completed', 'User Login', 'Configuration Change', 'Maintenance Started']
    }

    const titleList = titles[severity] || titles.info
    const title = titleList[Math.floor(Math.random() * titleList.length)]

    const resolvedAt = status !== 'Resolved' ? null : new Date(alarmDate.getTime() + resolutionTime * 60 * 1000).toISOString().slice(0, 19).replace('T', ' ')

    alarms.push({
      id: i,
      time: alarmDate.toISOString().slice(0, 19).replace('T', ' '),
      title: title,
      description: `${title} occurred in ${locations[Math.floor(Math.random() * locations.length)]}. Requires attention.`,
      severity: severity,
      category: category,
      location: locations[Math.floor(Math.random() * locations.length)],
      status: status,
      resolutionTime: resolutionTime,
      resolvedAt: resolvedAt,
      resolvedBy: status === 'Resolved' ? resolvedBy[Math.floor(Math.random() * resolvedBy.length)] : null,
      resolutionNotes: status === 'Resolved' ? 'Issue resolved and system恢复正常.' : null
    })
  }

  return alarms.sort((a, b) => new Date(b.time).getTime() - new Date(a.time).getTime())
}

// Statistics
const totalAlarms = computed(() => alarmHistory.value.length)
const criticalCount = computed(() => alarmHistory.value.filter(a => a.severity === 'critical').length)
const majorCount = computed(() => alarmHistory.value.filter(a => a.severity === 'major').length)
const warningCount = computed(() => alarmHistory.value.filter(a => a.severity === 'warning').length)
const infoCount = computed(() => alarmHistory.value.filter(a => a.severity === 'info').length)
const resolvedCount = computed(() => alarmHistory.value.filter(a => a.status === 'Resolved').length)
const avgResolutionTime = computed(() => {
  const resolved = alarmHistory.value.filter(a => a.status === 'Resolved')
  if (resolved.length === 0) return 0
  const avg = resolved.reduce((sum, a) => sum + a.resolutionTime, 0) / resolved.length
  return Math.round(avg)
})

// Filtered alarms
const filteredAlarms = computed(() => {
  let filtered = alarmHistory.value

  if (dateRange.value) {
    const [start, end] = dateRange.value
    filtered = filtered.filter(a => {
      const alarmDate = new Date(a.time)
      return alarmDate >= start && alarmDate <= end
    })
  }

  if (severityFilter.value !== 'all') {
    filtered = filtered.filter(a => a.severity === severityFilter.value)
  }

  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(a => a.status === statusFilter.value)
  }

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(a =>
        a.title.toLowerCase().includes(search) ||
        a.description.toLowerCase().includes(search) ||
        a.location.toLowerCase().includes(search)
    )
  }

  return filtered
})

// Paginated alarms
const paginatedAlarms = computed(() => {
  const start = (pagination.value.page - 1) * pagination.value.pageSize
  return filteredAlarms.value.slice(start, start + pagination.value.pageSize)
})

// Trend data
const weeklyData = ref<number[]>([])
const monthlyData = ref<number[]>([])
const weekLabels = ref<string[]>([])
const monthLabels = ref<string[]>([])

const initTrendData = () => {
  // Weekly data (last 7 days)
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  weekLabels.value = days
  weeklyData.value = [12, 15, 18, 22, 25, 18, 10]

  // Monthly data (last 30 days - aggregated weekly)
  monthLabels.value = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
  monthlyData.value = [45, 52, 48, 38]
}

// ==================== Chart Refs ====================
const trendChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null

const initCharts = () => {
  nextTick(() => {
    if (!trendChartRef.value) {
      setTimeout(initCharts, 200)
      return
    }

    if (trendChart) trendChart.dispose()
    trendChart = echarts.init(trendChartRef.value)
    updateChart()

    window.addEventListener('resize', () => {
      trendChart?.resize()
    })
  })
}

const updateChart = () => {
  if (!trendChart) return

  const isWeekly = trendPeriod.value === 'week'
  const labels = isWeekly ? weekLabels.value : monthLabels.value
  const data = isWeekly ? weeklyData.value : monthlyData.value

  trendChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '8%', right: '5%', top: '10%', bottom: '5%', containLabel: true },
    xAxis: {
      type: 'category',
      data: labels,
      axisLabel: { color: '#606266', fontSize: 11 },
      axisLine: { lineStyle: { color: '#dcdfe6' } }
    },
    yAxis: {
      type: 'value',
      name: 'Alarm Count',
      nameTextStyle: { color: '#909399' },
      axisLabel: { color: '#606266' },
      splitLine: { lineStyle: { color: '#ebeef5' } }
    },
    series: [{
      name: 'Alarms',
      type: 'line',
      data: data,
      smooth: true,
      lineStyle: { color: '#409eff', width: 3 },
      areaStyle: { opacity: 0.1, color: '#409eff' },
      symbol: 'circle',
      symbolSize: 8,
      itemStyle: { color: '#409eff' },
      label: { show: true, position: 'top', color: '#409eff', fontWeight: 'bold' }
    }]
  })
}

// ==================== Helper Functions ====================
const getSeverityTag = (severity: string) => {
  const map: Record<string, string> = {
    critical: 'danger',
    major: 'warning',
    warning: 'warning',
    info: 'info'
  }
  return map[severity] || 'info'
}

const getStatusTag = (status: string) => {
  const map: Record<string, string> = {
    Resolved: 'success',
    Acknowledged: 'primary',
    Escalated: 'danger'
  }
  return map[status] || 'info'
}

// ==================== Actions ====================
const viewDetails = (alarm: AlarmHistory) => {
  selectedAlarm.value = alarm
  detailDialogVisible.value = true
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  alarmHistory.value = generateAlarmHistory()
  tableLoading.value = false
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

const exportReport = async () => {
  exporting.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))
  exporting.value = false
  ElMessage.success('Export completed')
}

const handlePageSizeChange = () => {
  pagination.value.page = 1
}

const handlePageChange = () => {}

// ==================== Loading Animation ====================
const startLoading = () => {
  let progress = 0
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 12
      loadingProgress.value = Math.min(progress, 90)
    }
  }, 100)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => {
        setTimeout(() => {
          initCharts()
        }, 100)
      })
    }, 500)
  }, 2500)
}

watch(trendPeriod, () => {
  updateChart()
})

// ==================== Lifecycle ====================
onMounted(() => {
  alarmHistory.value = generateAlarmHistory()
  initTrendData()
  startLoading()
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
.spinner-ring:nth-child(4) { border-left-color: #ec489a; animation-delay: 0.6s; width: 20%; height: 20%; top: 40%; left: 40%; }

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

/* ==================== Main Dashboard Styles - 白色背景 ==================== */
.alarm-history-dashboard {
  min-height: 100vh;
  background: #ffffff;
  padding: 24px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.dashboard-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 600;
  color: #1f2f3d;
  margin: 0;
}

.dashboard-title .el-icon {
  color: #409eff;
}

.header-stats {
  display: flex;
  gap: 16px;
  margin-top: 8px;
}

.stat-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  background: #f5f7fa;
  border-radius: 20px;
  font-size: 13px;
  color: #606266;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Filter Bar */
.filter-bar {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.filter-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-card.critical .stat-icon { background: #fef0f0; }
.stat-card.major .stat-icon { background: #fdf6ec; }
.stat-card.warning .stat-icon { background: #fdf6ec; }
.stat-card.info .stat-icon { background: #ecf5ff; }
.stat-card.resolved .stat-icon { background: #f0f9eb; }
.stat-card.avg .stat-icon { background: #f4f4f5; }

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #1f2f3d;
}

.stat-value .unit {
  font-size: 12px;
  font-weight: normal;
  color: #909399;
  margin-left: 2px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* Card */
.card {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  flex-wrap: wrap;
  gap: 12px;
  background: #fafafa;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1f2f3d;
}

.card-title .el-icon {
  color: #409eff;
}

.table-info {
  font-size: 13px;
  color: #909399;
}

.trend-chart {
  width: 100%;
  height: 320px;
  padding: 16px;
}

.card-footer {
  padding: 16px 20px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  justify-content: flex-end;
  background: #fafafa;
}

.table-card {
  overflow-x: auto;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .alarm-history-dashboard {
    padding: 16px;
  }
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .filter-group {
    flex-direction: column;
    width: 100%;
  }
  .filter-group .el-date-picker,
  .filter-group .el-select,
  .filter-group .el-input {
    width: 100% !important;
  }
}

/* Element Plus 样式覆盖 - 白色主题 */
:deep(.el-table) {
  background: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: #fafafa;
  --el-table-row-hover-bg-color: #f5f7fa;
  --el-table-border-color: #e4e7ed;
}

:deep(.el-table th.el-table__cell) {
  background-color: #fafafa;
  color: #1f2f3d;
  border-bottom-color: #e4e7ed;
}

:deep(.el-table td.el-table__cell) {
  border-bottom-color: #ebeef5;
  color: #606266;
}

:deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
  --el-pagination-button-bg-color: #f5f7fa;
  --el-pagination-hover-color: #409eff;
}

:deep(.el-dialog) {
  background: #ffffff;
  border-radius: 12px;
}

:deep(.el-dialog__title) {
  color: #1f2f3d;
}

:deep(.el-descriptions__label) {
  background: #fafafa;
}

:deep(.el-radio-button__inner) {
  background: #ffffff;
  border-color: #dcdfe6;
  color: #606266;
}

:deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background-color: #409eff;
  border-color: #409eff;
  color: #ffffff;
}
</style>