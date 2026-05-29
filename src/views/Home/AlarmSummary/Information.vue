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

  <!-- Information Alarms Page Content -->
  <div v-else class="information-alarms-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>Information Alarms</h1>
        <p class="subtitle">Monitor informational events and system notifications</p>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="refreshData">Refresh</el-button>
        <el-button type="primary" :icon="Download" @click="exportReport">Export Report</el-button>
        <el-button :icon="Bell" @click="configureNotifications">Notifications</el-button>
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="kpi-cards">
      <div class="kpi-card info">
        <div class="kpi-icon">
          <el-icon :size="32"><InfoFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ infoCount }}</div>
          <div class="kpi-label">Information Events</div>
        </div>
        <div class="kpi-trend" :class="infoTrend >= 0 ? 'negative' : 'positive'">
          <el-icon><CaretBottom v-if="infoTrend >= 0" /><CaretTop v-else /></el-icon>
          {{ Math.abs(infoTrend) }}%
        </div>
      </div>
      <div class="kpi-card acknowledged">
        <div class="kpi-icon">
          <el-icon :size="32"><UserFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ acknowledgedCount }}</div>
          <div class="kpi-label">Acknowledged</div>
        </div>
        <div class="kpi-sub">{{ unacknowledgedCount }} unacknowledged</div>
      </div>
      <div class="kpi-card auto-resolved">
        <div class="kpi-icon">
          <el-icon :size="32"><CircleCheckFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ autoResolvedCount }}</div>
          <div class="kpi-label">Auto-Resolved</div>
        </div>
        <div class="kpi-sub">{{ autoResolutionRate }}% auto resolution</div>
      </div>
      <div class="kpi-card avg-duration">
        <div class="kpi-icon">
          <el-icon :size="32"><Timer /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ avgDuration }}</div>
          <div class="kpi-label">Avg Event Duration</div>
        </div>
        <div class="kpi-trend positive">
          <el-icon><CaretBottom /></el-icon>
          {{ durationTrend }}%
        </div>
      </div>
    </div>

    <!-- Event Trend Chart -->
    <div class="chart-card">
      <div class="card-header">
        <h3>Information Events Trend</h3>
        <el-radio-group v-model="trendPeriod" size="small" @change="fetchTrendData">
          <el-radio-button label="day">Last 24 Hours</el-radio-button>
          <el-radio-button label="week">Last 7 Days</el-radio-button>
          <el-radio-button label="month">Last 30 Days</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-container" ref="trendChartRef"></div>
    </div>

    <!-- Events by Category and Type -->
    <div class="two-columns">
      <div class="chart-card">
        <div class="card-header">
          <h3>Events by Category</h3>
        </div>
        <div class="chart-container" ref="categoryChartRef"></div>
      </div>
      <div class="chart-card">
        <div class="card-header">
          <h3>Events by Type</h3>
        </div>
        <div class="chart-container" ref="typeChartRef"></div>
      </div>
    </div>

    <!-- Information Events Table -->
    <div class="table-card">
      <div class="card-header">
        <h3>Information Events</h3>
        <div class="header-filters">
          <el-select v-model="categoryFilter" placeholder="All Categories" clearable size="default" style="width: 140px">
            <el-option label="All Categories" value="all" />
            <el-option label="HVAC" value="HVAC" />
            <el-option label="Electrical" value="Electrical" />
            <el-option label="Security" value="Security" />
            <el-option label="IT/Network" value="IT/Network" />
            <el-option label="System" value="System" />
          </el-select>
          <el-select v-model="eventTypeFilter" placeholder="All Types" clearable size="default" style="width: 130px">
            <el-option label="All Types" value="all" />
            <el-option label="State Change" value="state-change" />
            <el-option label="Scheduled" value="scheduled" />
            <el-option label="User Action" value="user-action" />
            <el-option label="System" value="system" />
          </el-select>
          <el-select v-model="statusFilter" placeholder="All Status" clearable size="default" style="width: 130px">
            <el-option label="All Status" value="all" />
            <el-option label="Active" value="active" />
            <el-option label="Acknowledged" value="acknowledged" />
            <el-option label="Resolved" value="resolved" />
          </el-select>
          <el-input
              v-model="searchText"
              placeholder="Search events..."
              :prefix-icon="Search"
              style="width: 200px"
              clearable
          />
        </div>
      </div>
      <el-table :data="paginatedEvents" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="severity" label="Type" width="100">
          <template #default="{ row }">
            <el-tag type="info" size="small">INFO</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="eventCode" label="Code" width="100" />
        <el-table-column prop="title" label="Event Title" min-width="200" show-overflow-tooltip />
        <el-table-column prop="category" label="Category" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="Source" width="160">
          <template #default="{ row }">
            <div class="source-cell">
              <el-icon><Cpu /></el-icon>
              <span>{{ row.source }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="occurredAt" label="Occurred" width="160" sortable>
          <template #default="{ row }">
            <div class="time-cell">
              <el-icon><Clock /></el-icon>
              <span>{{ formatTime(row.occurredAt) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="eventType" label="Event Type" width="120">
          <template #default="{ row }">
            <el-tag :type="getEventTypeTagType(row.eventType)" size="small" effect="light">
              {{ getEventTypeLabel(row.eventType) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'active'" link type="primary" size="small" @click="acknowledgeEvent(row)">Acknowledge</el-button>
            <el-button link type="info" size="small" @click="viewDetails(row)">View</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredEvents.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Recent System Notifications -->
    <div class="notifications-section">
      <div class="section-header">
        <h2>
          <el-icon><BellFilled /></el-icon>
          Recent System Notifications
        </h2>
        <el-button link type="primary" @click="viewAllNotifications">View All →</el-button>
      </div>
      <div class="notifications-list">
        <div v-for="notif in recentNotifications" :key="notif.id" class="notification-item">
          <div class="notif-icon">
            <el-icon><Message /></el-icon>
          </div>
          <div class="notif-content">
            <div class="notif-title">{{ notif.title }}</div>
            <div class="notif-message">{{ notif.message }}</div>
            <div class="notif-time">{{ formatTime(notif.timestamp) }}</div>
          </div>
          <div class="notif-actions">
            <el-button size="small" link type="primary" @click="dismissNotification(notif)">Dismiss</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Refresh,
  Download,
  Bell,
  InfoFilled,
  UserFilled,
  CircleCheckFilled,
  Timer,
  Connection,
  Search,
  Cpu,
  Clock,
  User,
  BellFilled,
  Message,
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
interface InformationEvent {
  id: number
  eventCode: string
  title: string
  category: string
  source: string
  severity: string
  eventType: 'state-change' | 'scheduled' | 'user-action' | 'system'
  occurredAt: string
  duration: string
  status: 'active' | 'acknowledged' | 'resolved'
}

interface Notification {
  id: number
  title: string
  message: string
  timestamp: string
}

// ==================== State ====================
const trendPeriod = ref<'day' | 'week' | 'month'>('week')
const categoryFilter = ref('all')
const eventTypeFilter = ref('all')
const statusFilter = ref('all')
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const trendChartRef = ref<HTMLElement | null>(null)
const categoryChartRef = ref<HTMLElement | null>(null)
const typeChartRef = ref<HTMLElement | null>(null)
let trendChart: echarts.ECharts | null = null
let categoryChart: echarts.ECharts | null = null
let typeChart: echarts.ECharts | null = null

// ==================== Mock Data ====================
const informationEvents = ref<InformationEvent[]>([
  { id: 1, eventCode: 'INF-4001', title: 'AHU-101 Schedule Change - Night Mode Activated', category: 'HVAC', source: 'AHU-101', severity: 'info', eventType: 'state-change', occurredAt: '2025-05-29 18:00:00', duration: '12 hours', status: 'active' },
  { id: 2, eventCode: 'INF-4002', title: 'User Login - Admin Access Logged', category: 'System', source: 'Auth-System', severity: 'info', eventType: 'user-action', occurredAt: '2025-05-29 09:15:22', duration: 'N/A', status: 'resolved' },
  { id: 3, eventCode: 'INF-4003', title: 'System Backup Completed Successfully', category: 'System', source: 'Backup-Server', severity: 'info', eventType: 'scheduled', occurredAt: '2025-05-29 02:00:00', duration: '45 min', status: 'resolved' },
  { id: 4, eventCode: 'INF-4004', title: 'Lighting Schedule - Daylight Savings Applied', category: 'Lighting', source: 'LCS-Main', severity: 'info', eventType: 'state-change', occurredAt: '2025-05-28 22:00:00', duration: 'Active', status: 'active' },
  { id: 5, eventCode: 'INF-4005', title: 'Energy Report Generated - Monthly Summary', category: 'System', source: 'Analytics-Engine', severity: 'info', eventType: 'scheduled', occurredAt: '2025-05-28 08:00:00', duration: 'N/A', status: 'resolved' },
  { id: 6, eventCode: 'INF-4006', title: 'Access Granted - Maintenance Team Entry', category: 'Security', source: 'ACS-Main', severity: 'info', eventType: 'user-action', occurredAt: '2025-05-28 07:30:00', duration: 'N/A', status: 'resolved' },
  { id: 7, eventCode: 'INF-4007', title: 'Temperature Setpoint Adjusted - Seasonal Change', category: 'HVAC', source: 'BMS-Controller', severity: 'info', eventType: 'state-change', occurredAt: '2025-05-28 06:00:00', duration: 'Seasonal', status: 'acknowledged' },
  { id: 8, eventCode: 'INF-4008', title: 'Firmware Update Available - UPS System', category: 'Electrical', source: 'UPS-01', severity: 'info', eventType: 'system', occurredAt: '2025-05-27 15:00:00', duration: 'Pending', status: 'active' },
  { id: 9, eventCode: 'INF-4009', title: 'Weekly Maintenance Mode Scheduled', category: 'System', source: 'Scheduler', severity: 'info', eventType: 'scheduled', occurredAt: '2025-05-27 10:00:00', duration: 'Upcoming', status: 'acknowledged' },
  { id: 10, eventCode: 'INF-4010', title: 'Configuration Change - Alarm Thresholds Updated', category: 'System', source: 'Config-Mgr', severity: 'info', eventType: 'user-action', occurredAt: '2025-05-27 09:00:00', duration: 'N/A', status: 'resolved' },
  { id: 11, eventCode: 'INF-4011', title: 'Network Device Connected - New Switch Online', category: 'IT/Network', source: 'Switch-05', severity: 'info', eventType: 'state-change', occurredAt: '2025-05-26 14:30:00', duration: 'Active', status: 'resolved' },
  { id: 12, eventCode: 'INF-4012', title: 'Data Export Completed - Compliance Report', category: 'System', source: 'Reporting-Engine', severity: 'info', eventType: 'scheduled', occurredAt: '2025-05-26 11:00:00', duration: 'N/A', status: 'resolved' }
])

const recentNotifications = ref<Notification[]>([
  { id: 1, title: 'System Maintenance', message: 'Scheduled maintenance on June 1st from 02:00-04:00 AM', timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString() },
  { id: 2, title: 'Report Ready', message: 'May 2025 Energy Consumption Report is ready for download', timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString() },
  { id: 3, title: 'Firmware Update', message: 'New firmware version 2.1.0 is available for UPS systems', timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString() }
])

// ==================== Computed Values ====================
const infoCount = computed(() => informationEvents.value.length)
const acknowledgedCount = computed(() => informationEvents.value.filter(e => e.status === 'acknowledged').length)
const unacknowledgedCount = computed(() => informationEvents.value.filter(e => e.status === 'active').length)
const autoResolvedCount = computed(() => informationEvents.value.filter(e => e.status === 'resolved').length)
const autoResolutionRate = computed(() => Math.round((autoResolvedCount.value / infoCount.value) * 100))
const avgDuration = computed(() => '2.5 hours')
const infoTrend = computed(() => 3.5)
const durationTrend = computed(() => -8.2)

const filteredEvents = computed(() => {
  let result = [...informationEvents.value]
  if (categoryFilter.value !== 'all') {
    result = result.filter(e => e.category === categoryFilter.value)
  }
  if (eventTypeFilter.value !== 'all') {
    result = result.filter(e => e.eventType === eventTypeFilter.value)
  }
  if (statusFilter.value !== 'all') {
    result = result.filter(e => e.status === statusFilter.value)
  }
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(e =>
        e.title.toLowerCase().includes(search) ||
        e.eventCode.toLowerCase().includes(search) ||
        e.source.toLowerCase().includes(search)
    )
  }
  return result
})

const paginatedEvents = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredEvents.value.slice(start, end)
})

// ==================== Helper Functions ====================
const formatTime = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 60) return `${diffMins} min ago`
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)} hours ago`
  return `${Math.floor(diffMins / 1440)} days ago`
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    active: 'Active',
    acknowledged: 'Acknowledged',
    resolved: 'Resolved'
  }
  return map[status] || status
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    active: 'warning',
    acknowledged: 'primary',
    resolved: 'success'
  }
  return map[status] || 'info'
}

const getEventTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    'state-change': 'State Change',
    scheduled: 'Scheduled',
    'user-action': 'User Action',
    system: 'System'
  }
  return map[type] || type
}

const getEventTypeTagType = (type: string) => {
  const map: Record<string, string> = {
    'state-change': 'warning',
    scheduled: 'primary',
    'user-action': 'success',
    system: 'info'
  }
  return map[type] || 'info'
}

// ==================== Chart Functions ====================
const generateTrendData = () => {
  if (trendPeriod.value === 'day') {
    return {
      labels: ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'],
      counts: [8, 5, 3, 10, 25, 35, 40, 38, 32, 28, 20, 12]
    }
  }
  if (trendPeriod.value === 'week') {
    return {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      counts: [65, 72, 80, 75, 85, 45, 30]
    }
  }
  return {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    counts: [280, 310, 295, 260]
  }
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)
  const data = generateTrendData()

  trendChart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: (value: number) => value + ' events' },
    xAxis: { type: 'category', data: data.labels, axisLabel: { rotate: trendPeriod.value === 'day' ? 45 : 0 } },
    yAxis: { type: 'value', name: 'Number of Events' },
    series: [{
      type: 'line', data: data.counts, smooth: true, symbol: 'circle',
      lineStyle: { width: 3, color: '#409eff' }, areaStyle: { opacity: 0.1, color: '#409eff' }
    }]
  })
}

const initCategoryChart = () => {
  if (!categoryChartRef.value) return
  if (categoryChart) categoryChart.dispose()

  categoryChart = echarts.init(categoryChartRef.value)

  const categories = ['HVAC', 'System', 'Security', 'Electrical', 'IT/Network', 'Lighting']
  const counts = [35, 42, 18, 22, 15, 10]

  categoryChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '10%', right: '5%', top: '5%', bottom: '5%', containLabel: true },
    xAxis: { type: 'value', name: 'Number of Events' },
    yAxis: { type: 'category', data: categories },
    series: [{
      type: 'bar', data: counts,
      itemStyle: { borderRadius: [0, 4, 4, 0], color: '#409eff' },
      label: { show: true, position: 'right' }
    }]
  })
}

const initTypeChart = () => {
  if (!typeChartRef.value) return
  if (typeChart) typeChart.dispose()

  typeChart = echarts.init(typeChartRef.value)

  typeChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} events ({d}%)' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      type: 'pie', radius: '55%', center: ['50%', '50%'],
      data: [
        { name: 'State Change', value: 45, itemStyle: { color: '#e6a23c' } },
        { name: 'Scheduled', value: 38, itemStyle: { color: '#409eff' } },
        { name: 'User Action', value: 32, itemStyle: { color: '#67c23a' } },
        { name: 'System', value: 25, itemStyle: { color: '#8b5cf6' } }
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
  ElMessage.success('Information events data refreshed')
  initTrendChart()
  initCategoryChart()
  initTypeChart()
  tableLoading.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting information events report...')
}

const configureNotifications = () => {
  ElMessage.info('Configuring notification settings')
}

const acknowledgeEvent = (row: InformationEvent) => {
  row.status = 'acknowledged'
  ElMessage.success(`Event ${row.eventCode} acknowledged`)
}

const viewDetails = (row: InformationEvent) => {
  ElMessage.info(`Viewing details for event ${row.eventCode}`)
}

const viewAllNotifications = () => {
  ElMessage.info('Viewing all notifications')
}

const dismissNotification = (notif: Notification) => {
  ElMessage.success(`Notification dismissed: ${notif.title}`)
  recentNotifications.value = recentNotifications.value.filter(n => n.id !== notif.id)
}

const fetchTrendData = () => {
  initTrendChart()
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Window Resize Handler ====================
const handleResize = () => {
  trendChart?.resize()
  categoryChart?.resize()
  typeChart?.resize()
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
        initTypeChart()
      }, 100)
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  categoryChart?.dispose()
  typeChart?.dispose()
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
.information-alarms-page {
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

.kpi-card.info .kpi-icon { background: #e8f4ff; color: #409eff; }
.kpi-card.acknowledged .kpi-icon { background: #fff7e8; color: #e6a23c; }
.kpi-card.auto-resolved .kpi-icon { background: #e8f8f0; color: #67c23a; }
.kpi-card.avg-duration .kpi-icon { background: #f0e8ff; color: #8b5cf6; }

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
.source-cell, .time-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.pagination-wrapper {
  padding: 20px 0 0;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
  margin-top: 16px;
}

/* Notifications Section */
.notifications-section {
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

.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 14px 16px;
  background: #fafafa;
  border-radius: 12px;
  transition: all 0.2s;
}

.notification-item:hover {
  background: #f5f7fa;
}

.notif-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e8f4ff;
  color: #409eff;
}

.notif-content {
  flex: 1;
}

.notif-title {
  font-weight: 600;
  color: #1f2f3d;
  margin-bottom: 4px;
}

.notif-message {
  font-size: 13px;
  color: #606266;
  margin-bottom: 6px;
}

.notif-time {
  font-size: 11px;
  color: #c0c4cc;
}

.notif-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.notification-item:hover .notif-actions {
  opacity: 1;
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