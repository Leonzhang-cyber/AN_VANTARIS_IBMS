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

  <!-- Major Alarms Page Content -->
  <div v-else class="major-alarms-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>Major Alarms</h1>
        <p class="subtitle">Monitor and manage high-priority system alarms requiring prompt attention</p>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="refreshData">Refresh</el-button>
        <el-button type="primary" :icon="Download" @click="exportReport">Export Report</el-button>
        <el-button :icon="Bell" @click="configureNotifications">Notifications</el-button>
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="kpi-cards">
      <div class="kpi-card major">
        <div class="kpi-icon">
          <el-icon :size="32"><WarningFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ majorCount }}</div>
          <div class="kpi-label">Major Alarms</div>
        </div>
        <div class="kpi-trend" :class="majorTrend >= 0 ? 'negative' : 'positive'">
          <el-icon><CaretBottom v-if="majorTrend >= 0" /><CaretTop v-else /></el-icon>
          {{ Math.abs(majorTrend) }}%
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
      <div class="kpi-card resolved">
        <div class="kpi-icon">
          <el-icon :size="32"><CircleCheckFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ resolvedToday }}</div>
          <div class="kpi-label">Resolved Today</div>
        </div>
        <div class="kpi-sub">{{ resolutionRate }}% resolution rate</div>
      </div>
      <div class="kpi-card mtbf">
        <div class="kpi-icon">
          <el-icon :size="32"><Timer /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ avgResolutionTime }}</div>
          <div class="kpi-label">Avg Resolution Time</div>
        </div>
        <div class="kpi-trend" :class="resolutionTrend <= 0 ? 'positive' : 'negative'">
          <el-icon><CaretBottom v-if="resolutionTrend <= 0" /><CaretTop v-else /></el-icon>
          {{ Math.abs(resolutionTrend) }}%
        </div>
      </div>
    </div>

    <!-- Alarm Trend Chart -->
    <div class="chart-card">
      <div class="card-header">
        <h3>Major Alarms Trend</h3>
        <el-radio-group v-model="trendPeriod" size="small" @change="fetchTrendData">
          <el-radio-button label="day">Last 24 Hours</el-radio-button>
          <el-radio-button label="week">Last 7 Days</el-radio-button>
          <el-radio-button label="month">Last 30 Days</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-container" ref="trendChartRef"></div>
    </div>

    <!-- Alarms by Category and System -->
    <div class="two-columns">
      <div class="chart-card">
        <div class="card-header">
          <h3>Alarms by Category</h3>
        </div>
        <div class="chart-container" ref="categoryChartRef"></div>
      </div>
      <div class="chart-card">
        <div class="card-header">
          <h3>Top Affected Systems</h3>
        </div>
        <div class="chart-container" ref="systemChartRef"></div>
      </div>
    </div>

    <!-- Major Alarms Table -->
    <div class="table-card">
      <div class="card-header">
        <h3>Active Major Alarms</h3>
        <div class="header-filters">
          <el-select v-model="categoryFilter" placeholder="All Categories" clearable size="default" style="width: 140px">
            <el-option label="All Categories" value="all" />
            <el-option label="HVAC" value="HVAC" />
            <el-option label="Electrical" value="Electrical" />
            <el-option label="Plumbing" value="Plumbing" />
            <el-option label="Security" value="Security" />
            <el-option label="IT/Network" value="IT/Network" />
            <el-option label="Lighting" value="Lighting" />
          </el-select>
          <el-select v-model="statusFilter" placeholder="All Status" clearable size="default" style="width: 130px">
            <el-option label="All Status" value="all" />
            <el-option label="Active" value="active" />
            <el-option label="Acknowledged" value="acknowledged" />
            <el-option label="In Progress" value="in-progress" />
            <el-option label="Resolved" value="resolved" />
          </el-select>
          <el-input
              v-model="searchText"
              placeholder="Search alarms..."
              :prefix-icon="Search"
              style="width: 200px"
              clearable
          />
        </div>
      </div>
      <el-table :data="paginatedAlarms" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="severity" label="Severity" width="100">
          <template #default="{ row }">
            <el-tag type="warning" size="small" effect="dark">MAJOR</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="alarmCode" label="Code" width="100" />
        <el-table-column prop="title" label="Alarm Title" min-width="200" show-overflow-tooltip />
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
        <el-table-column prop="duration" label="Duration" width="100" sortable>
          <template #default="{ row }">
            <span>{{ row.duration }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="140" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'active'" link type="primary" size="small" @click="acknowledgeAlarm(row)">Acknowledge</el-button>
            <el-button link type="success" size="small" @click="viewDetails(row)">Details</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredAlarms.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Escalation Rules -->
    <div class="escalation-section">
      <div class="section-header">
        <h2>
          <el-icon><Connection /></el-icon>
          Escalation Rules - Major Alarms
        </h2>
        <el-button link type="primary" @click="editEscalationRules">Edit Rules</el-button>
      </div>
      <div class="escalation-list">
        <div v-for="rule in escalationRules" :key="rule.id" class="escalation-item">
          <div class="rule-severity" :class="rule.severity">
            {{ rule.severity.toUpperCase() }}
          </div>
          <div class="rule-content">
            <div class="rule-title">{{ rule.title }}</div>
            <div class="rule-description">{{ rule.description }}</div>
            <div class="rule-meta">
              <span><el-icon><Timer /></el-icon> Escalate after: {{ rule.escalateAfter }}</span>
              <span><el-icon><User /></el-icon> Notify: {{ rule.notifyTeam }}</span>
            </div>
          </div>
          <div class="rule-status">
            <el-tag :type="rule.enabled ? 'success' : 'info'" size="small">
              {{ rule.enabled ? 'Enabled' : 'Disabled' }}
            </el-tag>
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
  WarningFilled,
  UserFilled,
  CircleCheckFilled,
  Timer,
  Connection,
  Search,
  Cpu,
  Clock,
  User,
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
interface MajorAlarm {
  id: number
  alarmCode: string
  title: string
  category: string
  source: string
  severity: string
  occurredAt: string
  duration: string
  durationMinutes: number
  status: 'active' | 'acknowledged' | 'in-progress' | 'resolved'
}

interface EscalationRule {
  id: number
  severity: string
  title: string
  description: string
  escalateAfter: string
  notifyTeam: string
  enabled: boolean
}

// ==================== State ====================
const trendPeriod = ref<'day' | 'week' | 'month'>('week')
const categoryFilter = ref('all')
const statusFilter = ref('all')
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const trendChartRef = ref<HTMLElement | null>(null)
const categoryChartRef = ref<HTMLElement | null>(null)
const systemChartRef = ref<HTMLElement | null>(null)
let trendChart: echarts.ECharts | null = null
let categoryChart: echarts.ECharts | null = null
let systemChart: echarts.ECharts | null = null

// ==================== Mock Data ====================
const majorAlarms = ref<MajorAlarm[]>([
  { id: 1, alarmCode: 'ALM-2001', title: 'AHU-201 Filter Clogged - High Pressure Differential', category: 'HVAC', source: 'AHU-201', severity: 'major', occurredAt: '2025-05-29 09:15:22', duration: '35 min', durationMinutes: 35, status: 'active' },
  { id: 2, alarmCode: 'ALM-2002', title: 'Lighting Control Panel Communication Error', category: 'Lighting', source: 'LCP-01', severity: 'major', occurredAt: '2025-05-29 08:45:10', duration: '65 min', durationMinutes: 65, status: 'acknowledged' },
  { id: 3, alarmCode: 'ALM-2003', title: 'Water Pressure Low - Building B', category: 'Plumbing', source: 'Pump-02', severity: 'major', occurredAt: '2025-05-29 07:30:05', duration: '140 min', durationMinutes: 140, status: 'in-progress' },
  { id: 4, alarmCode: 'ALM-2004', title: 'Camera Feed Loss - North Entrance', category: 'Security', source: 'CAM-12', severity: 'major', occurredAt: '2025-05-28 22:10:30', duration: '9 hours', durationMinutes: 540, status: 'active' },
  { id: 5, alarmCode: 'ALM-2005', title: 'Switch Port Utilization High', category: 'IT/Network', source: 'Switch-01', severity: 'major', occurredAt: '2025-05-28 18:30:00', duration: '14.5 hours', durationMinutes: 870, status: 'acknowledged' },
  { id: 6, alarmCode: 'ALM-2006', title: 'VFD Overcurrent Warning', category: 'Electrical', source: 'VFD-03', severity: 'major', occurredAt: '2025-05-28 15:20:15', duration: '18 hours', durationMinutes: 1080, status: 'in-progress' },
  { id: 7, alarmCode: 'ALM-2007', title: 'FCU-105 Not Responding', category: 'HVAC', source: 'FCU-105', severity: 'major', occurredAt: '2025-05-28 11:45:00', duration: '21.5 hours', durationMinutes: 1290, status: 'resolved' },
  { id: 8, alarmCode: 'ALM-2008', title: 'Emergency Lighting Test Failed', category: 'Lighting', source: 'ELP-01', severity: 'major', occurredAt: '2025-05-28 08:00:00', duration: '1 day', durationMinutes: 1440, status: 'active' },
  { id: 9, alarmCode: 'ALM-2009', title: 'Chilled Water Flow Low', category: 'HVAC', source: 'Chiller-02', severity: 'major', occurredAt: '2025-05-27 23:30:00', duration: '1 day 2 hours', durationMinutes: 1560, status: 'acknowledged' },
  { id: 10, alarmCode: 'ALM-2010', title: 'Generator Exercise Failed', category: 'Electrical', source: 'GEN-02', severity: 'major', occurredAt: '2025-05-27 14:00:00', duration: '1 day 8 hours', durationMinutes: 1920, status: 'in-progress' },
  { id: 11, alarmCode: 'ALM-2011', title: 'Access Card Reader Offline', category: 'Security', source: 'Reader-05', severity: 'major', occurredAt: '2025-05-27 10:15:00', duration: '1 day 12 hours', durationMinutes: 2160, status: 'active' },
  { id: 12, alarmCode: 'ALM-2012', title: 'Server Room Humidity High', category: 'IT/Network', source: 'Sensor-H-02', severity: 'major', occurredAt: '2025-05-27 06:45:00', duration: '1 day 15 hours', durationMinutes: 2340, status: 'resolved' }
])

const escalationRules = ref<EscalationRule[]>([
  { id: 1, severity: 'major', title: 'Major Alarm Escalation', description: 'Notify Shift Supervisor after 45 minutes of no acknowledgment', escalateAfter: '45 minutes', notifyTeam: 'Shift Supervisor', enabled: true },
  { id: 2, severity: 'major', title: 'Second Level Escalation', description: 'Escalate to Facilities Manager after 3 hours', escalateAfter: '3 hours', notifyTeam: 'Facilities Manager', enabled: true },
  { id: 3, severity: 'major', title: 'Maintenance Dispatch', description: 'Dispatch maintenance team for unresolved major alarms after 6 hours', escalateAfter: '6 hours', notifyTeam: 'Maintenance Team', enabled: true }
])

// ==================== Computed Values ====================
const majorCount = computed(() => majorAlarms.value.length)
const acknowledgedCount = computed(() => majorAlarms.value.filter(a => a.status === 'acknowledged' || a.status === 'in-progress').length)
const unacknowledgedCount = computed(() => majorAlarms.value.filter(a => a.status === 'active').length)
const resolvedToday = computed(() => majorAlarms.value.filter(a => a.status === 'resolved').length)
const resolutionRate = computed(() => Math.round((resolvedToday.value / majorCount.value) * 100))
const avgResolutionTime = computed(() => '4.2 hours')
const majorTrend = computed(() => 8.2)
const resolutionTrend = computed(() => -5.6)

const filteredAlarms = computed(() => {
  let result = [...majorAlarms.value]
  if (categoryFilter.value !== 'all') {
    result = result.filter(a => a.category === categoryFilter.value)
  }
  if (statusFilter.value !== 'all') {
    result = result.filter(a => a.status === statusFilter.value)
  }
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(a =>
        a.title.toLowerCase().includes(search) ||
        a.alarmCode.toLowerCase().includes(search) ||
        a.source.toLowerCase().includes(search)
    )
  }
  return result
})

const paginatedAlarms = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredAlarms.value.slice(start, end)
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
    'in-progress': 'In Progress',
    resolved: 'Resolved'
  }
  return map[status] || status
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    active: 'danger',
    acknowledged: 'warning',
    'in-progress': 'primary',
    resolved: 'success'
  }
  return map[status] || 'info'
}

// ==================== Chart Functions ====================
const generateTrendData = () => {
  if (trendPeriod.value === 'day') {
    return {
      labels: ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'],
      counts: [3, 2, 1, 4, 8, 10, 12, 15, 11, 9, 6, 4]
    }
  }
  if (trendPeriod.value === 'week') {
    return {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      counts: [18, 22, 25, 20, 24, 12, 8]
    }
  }
  return {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    counts: [68, 75, 82, 62]
  }
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)
  const data = generateTrendData()

  trendChart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: (value: number) => value + ' alarms' },
    xAxis: { type: 'category', data: data.labels, axisLabel: { rotate: trendPeriod.value === 'day' ? 45 : 0 } },
    yAxis: { type: 'value', name: 'Number of Alarms' },
    series: [{
      type: 'line', data: data.counts, smooth: true, symbol: 'circle',
      lineStyle: { width: 3, color: '#e6a23c' }, areaStyle: { opacity: 0.1, color: '#e6a23c' }
    }]
  })
}

const initCategoryChart = () => {
  if (!categoryChartRef.value) return
  if (categoryChart) categoryChart.dispose()

  categoryChart = echarts.init(categoryChartRef.value)

  const categories = ['HVAC', 'Electrical', 'IT/Network', 'Security', 'Plumbing', 'Lighting']
  const counts = [32, 18, 15, 12, 10, 8]

  categoryChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '10%', right: '5%', top: '5%', bottom: '5%', containLabel: true },
    xAxis: { type: 'value', name: 'Number of Alarms' },
    yAxis: { type: 'category', data: categories },
    series: [{
      type: 'bar', data: counts,
      itemStyle: { borderRadius: [0, 4, 4, 0], color: '#e6a23c' },
      label: { show: true, position: 'right' }
    }]
  })
}

const initSystemChart = () => {
  if (!systemChartRef.value) return
  if (systemChart) systemChart.dispose()

  systemChart = echarts.init(systemChartRef.value)

  systemChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} alarms ({d}%)' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      type: 'pie', radius: '55%', center: ['50%', '50%'],
      data: [
        { name: 'AHU Systems', value: 18, itemStyle: { color: '#e6a23c' } },
        { name: 'FCU Network', value: 14, itemStyle: { color: '#f56c6c' } },
        { name: 'Lighting Panels', value: 10, itemStyle: { color: '#409eff' } },
        { name: 'Network Switches', value: 8, itemStyle: { color: '#67c23a' } },
        { name: 'Pumping Systems', value: 7, itemStyle: { color: '#909399' } }
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
  ElMessage.success('Major alarms data refreshed')
  initTrendChart()
  initCategoryChart()
  initSystemChart()
  tableLoading.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting major alarms report...')
}

const configureNotifications = () => {
  ElMessage.info('Configuring notification settings')
}

const acknowledgeAlarm = (row: MajorAlarm) => {
  row.status = 'acknowledged'
  ElMessage.success(`Alarm ${row.alarmCode} acknowledged`)
}

const viewDetails = (row: MajorAlarm) => {
  ElMessage.info(`Viewing details for alarm ${row.alarmCode}`)
}

const editEscalationRules = () => {
  ElMessage.info('Editing escalation rules')
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
  systemChart?.resize()
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
        initSystemChart()
      }, 100)
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  categoryChart?.dispose()
  systemChart?.dispose()
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
.major-alarms-page {
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

.kpi-card.major .kpi-icon { background: #fff7e8; color: #e6a23c; }
.kpi-card.acknowledged .kpi-icon { background: #e8f4ff; color: #409eff; }
.kpi-card.resolved .kpi-icon { background: #e8f8f0; color: #67c23a; }
.kpi-card.mtbf .kpi-icon { background: #f0e8ff; color: #8b5cf6; }

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

.text-danger {
  color: #f56c6c;
  font-weight: 500;
}

.pagination-wrapper {
  padding: 20px 0 0;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
  margin-top: 16px;
}

/* Escalation Section */
.escalation-section {
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

.escalation-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.escalation-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 14px;
  transition: all 0.2s;
}

.escalation-item:hover {
  background: #f5f7fa;
}

.rule-severity {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  background: #fff7e8;
  color: #e6a23c;
}

.rule-content {
  flex: 1;
}

.rule-title {
  font-weight: 600;
  color: #1f2f3d;
  margin-bottom: 6px;
}

.rule-description {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.rule-meta {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #909399;
}

.rule-meta .el-icon {
  vertical-align: middle;
  margin-right: 4px;
}

.rule-status {
  flex-shrink: 0;
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