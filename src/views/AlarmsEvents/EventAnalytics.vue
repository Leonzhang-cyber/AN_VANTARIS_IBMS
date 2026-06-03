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
        <div class="loading-tip">Event Analytics</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="event-analytics-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-left">
        <h1 class="dashboard-title">
          <el-icon><DataAnalysis /></el-icon>
          Event Analytics
        </h1>
        <div class="header-stats">
          <div class="stat-badge">
            <el-icon><Calendar /></el-icon>
            {{ dateRangeLabel }}
          </div>
          <div class="stat-badge">
            <el-icon><TrendCharts /></el-icon>
            {{ totalEvents }} Total Events
          </div>
        </div>
      </div>
      <div class="header-right">
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            :shortcuts="dateShortcuts"
            size="default"
            style="width: 280px"
        />
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
        <el-button type="primary" @click="exportReport">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-icon" style="background: #fef0f0; color: #f56c6c;">🔴</div>
        <div class="kpi-info">
          <div class="kpi-value">{{ criticalCount }}</div>
          <div class="kpi-label">Critical Events</div>
          <div class="kpi-trend" :class="criticalTrend > 0 ? 'up' : 'down'">{{ criticalTrend > 0 ? '+' : '' }}{{ criticalTrend }}%</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon" style="background: #fdf6ec; color: #e6a23c;">🟠</div>
        <div class="kpi-info">
          <div class="kpi-value">{{ majorCount }}</div>
          <div class="kpi-label">Major Events</div>
          <div class="kpi-trend" :class="majorTrend > 0 ? 'up' : 'down'">{{ majorTrend > 0 ? '+' : '' }}{{ majorTrend }}%</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon" style="background: #fdf6ec; color: #fbbf24;">🟡</div>
        <div class="kpi-info">
          <div class="kpi-value">{{ warningCount }}</div>
          <div class="kpi-label">Warning Events</div>
          <div class="kpi-trend" :class="warningTrend > 0 ? 'up' : 'down'">{{ warningTrend > 0 ? '+' : '' }}{{ warningTrend }}%</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon" style="background: #ecf5ff; color: #409eff;">🔵</div>
        <div class="kpi-info">
          <div class="kpi-value">{{ infoCount }}</div>
          <div class="kpi-label">Info Events</div>
          <div class="kpi-trend" :class="infoTrend > 0 ? 'up' : 'down'">{{ infoTrend > 0 ? '+' : '' }}{{ infoTrend }}%</div>
        </div>
      </div>
    </div>

    <!-- Main Two-Column Layout -->
    <div class="dashboard-main">
      <!-- Left Column -->
      <div class="main-left">
        <!-- Event Trend Chart -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><TrendCharts /></el-icon>
              Event Trend Analysis
            </div>
            <el-radio-group v-model="trendPeriod" size="small" @change="updateTrendChart">
              <el-radio-button label="day">Daily</el-radio-button>
              <el-radio-button label="week">Weekly</el-radio-button>
              <el-radio-button label="month">Monthly</el-radio-button>
            </el-radio-group>
          </div>
          <div ref="trendChartRef" class="chart-container"></div>
        </div>

        <!-- Top Categories Chart -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><PieChart /></el-icon>
              Events by Category
            </div>
          </div>
          <div ref="categoryChartRef" class="chart-container-small"></div>
        </div>

        <!-- Top Locations Chart -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Location /></el-icon>
              Top Locations by Event Count
            </div>
          </div>
          <div ref="locationChartRef" class="chart-container-small"></div>
        </div>
      </div>

      <!-- Right Column -->
      <div class="main-right">
        <!-- Severity Distribution -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Histogram /></el-icon>
              Severity Distribution
            </div>
          </div>
          <div ref="severityChartRef" class="chart-container-small"></div>
        </div>

        <!-- Top Devices by Events -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Monitor /></el-icon>
              Top Devices by Event Count
            </div>
          </div>
          <div class="top-devices-list">
            <div v-for="device in topDevices" :key="device.name" class="device-item">
              <div class="device-rank">{{ device.rank }}</div>
              <div class="device-info">
                <div class="device-name">{{ device.name }}</div>
                <div class="device-type">{{ device.type }}</div>
              </div>
              <div class="device-stats">
                <div class="device-count">{{ device.count }} events</div>
                <div class="device-percent">{{ device.percent }}%</div>
              </div>
              <el-progress :percentage="device.percent" :stroke-width="6" :show-text="false" />
            </div>
          </div>
        </div>

        <!-- Time Pattern Analysis -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Clock /></el-icon>
              Time Pattern Analysis
            </div>
          </div>
          <div class="time-patterns">
            <div class="pattern-item">
              <div class="pattern-label">Peak Hour</div>
              <div class="pattern-value">{{ peakHour }}:00</div>
              <div class="pattern-desc">{{ peakHourCount }} events</div>
            </div>
            <div class="pattern-item">
              <div class="pattern-label">Peak Day</div>
              <div class="pattern-value">{{ peakDay }}</div>
              <div class="pattern-desc">{{ peakDayCount }} events</div>
            </div>
            <div class="pattern-item">
              <div class="pattern-label">Avg MTTR</div>
              <div class="pattern-value">{{ avgMttr }}<span class="unit">min</span></div>
              <div class="pattern-desc">{{ mttrTrend }} vs last period</div>
            </div>
            <div class="pattern-item">
              <div class="pattern-label">Peak Month</div>
              <div class="pattern-value">{{ peakMonth }}</div>
              <div class="pattern-desc">{{ peakMonthCount }} events</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Events Data Table -->
    <div class="card table-card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><List /></el-icon>
          Events Data
        </div>
        <div class="table-controls">
          <el-input v-model="searchText" placeholder="Search events..." size="small" style="width: 200px" clearable>
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-select v-model="severityTableFilter" placeholder="Severity" size="small" style="width: 120px" clearable>
            <el-option label="All" value="all" />
            <el-option label="Critical" value="critical" />
            <el-option label="Major" value="major" />
            <el-option label="Warning" value="warning" />
            <el-option label="Info" value="info" />
          </el-select>
        </div>
      </div>
      <el-table :data="paginatedEvents" stripe border style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="time" label="Time" width="160" sortable />
        <el-table-column prop="title" label="Event Title" min-width="200" />
        <el-table-column prop="severity" label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityTag(row.severity)" size="small">{{ row.severity.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="Category" width="120" />
        <el-table-column prop="location" label="Location" min-width="140" />
        <el-table-column prop="device" label="Device" min-width="140" />
        <el-table-column prop="resolutionTime" label="Resolution (min)" width="110" sortable />
        <el-table-column label="Actions" width="80">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewEventDetails(row)">
              Details
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="card-footer">
        <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="filteredEvents.length"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handlePageSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- Event Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Event Details - ${selectedEvent?.title}`" width="600px">
      <el-descriptions :column="2" border v-if="selectedEvent">
        <el-descriptions-item label="Event ID">{{ selectedEvent.id }}</el-descriptions-item>
        <el-descriptions-item label="Severity">
          <el-tag :type="getSeverityTag(selectedEvent.severity)">{{ selectedEvent.severity.toUpperCase() }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Title" :span="2">{{ selectedEvent.title }}</el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedEvent.description }}</el-descriptions-item>
        <el-descriptions-item label="Location">{{ selectedEvent.location }}</el-descriptions-item>
        <el-descriptions-item label="Device">{{ selectedEvent.device }}</el-descriptions-item>
        <el-descriptions-item label="Category">{{ selectedEvent.category }}</el-descriptions-item>
        <el-descriptions-item label="Occurred At">{{ selectedEvent.time }}</el-descriptions-item>
        <el-descriptions-item label="Resolved At">{{ selectedEvent.resolvedAt || '-' }}</el-descriptions-item>
        <el-descriptions-item label="Resolution Time">{{ selectedEvent.resolutionTime }} minutes</el-descriptions-item>
        <el-descriptions-item label="Resolved By">{{ selectedEvent.resolvedBy || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { DataAnalysis, Calendar, TrendCharts, Refresh, Download, PieChart, Location, Histogram, Monitor, Clock, List, Search } from '@element-plus/icons-vue'
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
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading event data...',
  'Analyzing patterns...',
  'Building charts...',
  'Almost ready...'
]

// ==================== Data State ====================
const dateRange = ref<[Date, Date] | null>(null)
const searchText = ref('')
const severityTableFilter = ref('all')
const trendPeriod = ref('day')
const detailDialogVisible = ref(false)
const selectedEvent = ref<any>(null)

const pagination = ref({ page: 1, pageSize: 10 })

// Date shortcuts
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

const dateRangeLabel = computed(() => {
  if (dateRange.value && dateRange.value[0] && dateRange.value[1]) {
    const start = dateRange.value[0].toLocaleDateString()
    const end = dateRange.value[1].toLocaleDateString()
    return `${start} - ${end}`
  }
  return 'Last 30 Days'
})

// KPI Data
const totalEvents = ref(1247)
const criticalCount = ref(156)
const majorCount = ref(289)
const warningCount = ref(423)
const infoCount = ref(379)
const criticalTrend = ref(12)
const majorTrend = ref(-5)
const warningTrend = ref(8)
const infoTrend = ref(3)

// Time Pattern Data
const peakHour = ref(14)
const peakHourCount = ref(127)
const peakDay = ref('Wednesday')
const peakDayCount = ref(245)
const avgMttr = ref(28)
const mttrTrend = ref('-12%')
const peakMonth = ref('March')
const peakMonthCount = ref(412)

// Top Devices
const topDevices = ref([
  { rank: 1, name: 'UPS-01', type: 'UPS', count: 89, percent: 7.1 },
  { rank: 2, name: 'CRAC-03', type: 'CRAC', count: 76, percent: 6.1 },
  { rank: 3, name: 'Switch-01', type: 'Network', count: 54, percent: 4.3 },
  { rank: 4, name: 'Server-DB01', type: 'Server', count: 48, percent: 3.8 },
  { rank: 5, name: 'Router-Core', type: 'Network', count: 42, percent: 3.4 }
])

// Events Data
interface Event {
  id: number
  time: string
  title: string
  description: string
  severity: string
  category: string
  location: string
  device: string
  resolutionTime: number
  resolvedAt: string | null
  resolvedBy: string | null
}

const events = ref<Event[]>([])

// Generate mock events
const generateEvents = (): Event[] => {
  const severities = ['critical', 'major', 'warning', 'info']
  const categories = ['Environmental', 'Power', 'Cooling', 'Network', 'Security', 'Storage', 'Hardware']
  const locations = ['Data Center', 'Server Room A', 'Server Room B', 'Network Room', 'Electrical Room']
  const devices = ['UPS-01', 'UPS-02', 'CRAC-01', 'CRAC-02', 'Switch-01', 'Router-Core', 'Server-DB01', 'Server-APP01', 'Storage-01', 'PDU-01']

  const eventsList: Event[] = []
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - 30)

  for (let i = 1; i <= 150; i++) {
    const randomDays = Math.floor(Math.random() * 30)
    const eventDate = new Date(startDate)
    eventDate.setDate(startDate.getDate() + randomDays)

    const severity = severities[Math.floor(Math.random() * severities.length)]
    const category = categories[Math.floor(Math.random() * categories.length)]
    const resolutionTime = severity === 'critical' ? Math.floor(15 + Math.random() * 30) :
        severity === 'major' ? Math.floor(20 + Math.random() * 40) :
            Math.floor(30 + Math.random() * 60)

    const titles: Record<string, string[]> = {
      critical: ['UPS Overload', 'Temperature Critical', 'Chiller Failure', 'Network Core Down', 'Power Outage'],
      major: ['High CPU Usage', 'Memory Threshold', 'Disk Space Warning', 'Network Latency', 'Cooling Inefficiency'],
      warning: ['Humidity High', 'Fan Speed High', 'Failed Login Attempts', 'Certificate Expiring', 'Memory Usage Warning'],
      info: ['System Startup', 'Backup Completed', 'User Login', 'Configuration Change', 'Maintenance Started']
    }

    const titleList = titles[severity] || titles.info
    const title = titleList[Math.floor(Math.random() * titleList.length)]

    eventsList.push({
      id: i,
      time: eventDate.toISOString().slice(0, 19).replace('T', ' '),
      title: title,
      description: `${title} detected in ${locations[Math.floor(Math.random() * locations.length)]}`,
      severity: severity,
      category: category,
      location: locations[Math.floor(Math.random() * locations.length)],
      device: devices[Math.floor(Math.random() * devices.length)],
      resolutionTime: resolutionTime,
      resolvedAt: resolutionTime > 0 ? new Date(eventDate.getTime() + resolutionTime * 60 * 1000).toISOString().slice(0, 19).replace('T', ' ') : null,
      resolvedBy: Math.random() > 0.3 ? 'System' : 'Admin'
    })
  }

  return eventsList.sort((a, b) => new Date(b.time).getTime() - new Date(a.time).getTime())
}

const filteredEvents = computed(() => {
  let filtered = events.value

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(e => e.title.toLowerCase().includes(search) || e.description.toLowerCase().includes(search))
  }

  if (severityTableFilter.value !== 'all') {
    filtered = filtered.filter(e => e.severity === severityTableFilter.value)
  }

  if (dateRange.value && dateRange.value[0] && dateRange.value[1]) {
    const [start, end] = dateRange.value
    filtered = filtered.filter(e => {
      const eventDate = new Date(e.time)
      return eventDate >= start && eventDate <= end
    })
  }

  return filtered
})

const paginatedEvents = computed(() => {
  const start = (pagination.value.page - 1) * pagination.value.pageSize
  return filteredEvents.value.slice(start, start + pagination.value.pageSize)
})

// ==================== Chart Data ====================
const dailyTrendData = ref<number[]>([])
const weeklyTrendData = ref<number[]>([])
const monthlyTrendData = ref<number[]>([])
const weekLabels = ref<string[]>([])
const monthLabels = ref<string[]>([])

const categoryData = ref([
  { name: 'Environmental', value: 28, color: '#34d399' },
  { name: 'Power', value: 22, color: '#f97316' },
  { name: 'Cooling', value: 18, color: '#60a5fa' },
  { name: 'Network', value: 16, color: '#fbbf24' },
  { name: 'Security', value: 10, color: '#ef4444' },
  { name: 'Storage', value: 6, color: '#8b5cf6' }
])

const locationData = ref([
  { name: 'Data Center', value: 35, color: '#409eff' },
  { name: 'Server Room A', value: 25, color: '#67c23a' },
  { name: 'Server Room B', value: 20, color: '#e6a23c' },
  { name: 'Network Room', value: 12, color: '#f56c6c' },
  { name: 'Electrical Room', value: 8, color: '#909399' }
])

const initTrendData = () => {
  // Weekly data (7 days)
  weekLabels.value = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  weeklyTrendData.value = [45, 52, 48, 58, 62, 38, 32]

  // Monthly data (30 days aggregated weekly)
  monthLabels.value = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
  monthlyTrendData.value = [185, 210, 198, 165]

  // Daily data (24 hours)
  dailyTrendData.value = Array.from({ length: 24 }, () => Math.floor(20 + Math.random() * 60))
}

// ==================== Chart Refs ====================
const trendChartRef = ref<HTMLElement>()
const categoryChartRef = ref<HTMLElement>()
const locationChartRef = ref<HTMLElement>()
const severityChartRef = ref<HTMLElement>()

let trendChart: echarts.ECharts | null = null
let categoryChart: echarts.ECharts | null = null
let locationChart: echarts.ECharts | null = null
let severityChart: echarts.ECharts | null = null

const initCharts = () => {
  nextTick(() => {
    // Trend Chart
    if (trendChartRef.value) {
      if (trendChart) trendChart.dispose()
      trendChart = echarts.init(trendChartRef.value)
      updateTrendChart()
    }

    // Category Pie Chart
    if (categoryChartRef.value) {
      if (categoryChart) categoryChart.dispose()
      categoryChart = echarts.init(categoryChartRef.value)
      categoryChart.setOption({
        backgroundColor: 'transparent',
        tooltip: { trigger: 'item' },
        legend: { orient: 'vertical', left: 'left', textStyle: { color: '#606266' } },
        series: [{
          type: 'pie', radius: '55%', center: ['50%', '50%'],
          data: categoryData.value.map(item => ({ name: item.name, value: item.value, itemStyle: { color: item.color } })),
          label: { show: true, formatter: '{b}: {d}%', color: '#606266' }
        }]
      })
    }

    // Location Bar Chart
    if (locationChartRef.value) {
      if (locationChart) locationChart.dispose()
      locationChart = echarts.init(locationChartRef.value)
      locationChart.setOption({
        backgroundColor: 'transparent',
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '10%', right: '5%', top: '10%', bottom: '5%', containLabel: true },
        xAxis: { type: 'category', data: locationData.value.map(l => l.name), axisLabel: { rotate: 30, color: '#606266' }, axisLine: { lineStyle: { color: '#dcdfe6' } } },
        yAxis: { type: 'value', name: 'Event Count', axisLabel: { color: '#606266' }, splitLine: { lineStyle: { color: '#ebeef5' } } },
        series: [{
          type: 'bar', data: locationData.value.map(l => l.value),
          itemStyle: { borderRadius: [4, 4, 0, 0], color: '#409eff' },
          label: { show: true, position: 'top' }
        }]
      })
    }

    // Severity Pie Chart
    if (severityChartRef.value) {
      if (severityChart) severityChart.dispose()
      severityChart = echarts.init(severityChartRef.value)
      severityChart.setOption({
        backgroundColor: 'transparent',
        tooltip: { trigger: 'item' },
        legend: { orient: 'vertical', left: 'left', textStyle: { color: '#606266' } },
        series: [{
          type: 'pie', radius: ['40%', '60%'], center: ['50%', '50%'],
          data: [
            { value: criticalCount.value, name: 'Critical', itemStyle: { color: '#f56c6c' } },
            { value: majorCount.value, name: 'Major', itemStyle: { color: '#e6a23c' } },
            { value: warningCount.value, name: 'Warning', itemStyle: { color: '#fbbf24' } },
            { value: infoCount.value, name: 'Info', itemStyle: { color: '#409eff' } }
          ],
          label: { show: true, formatter: '{b}: {d}%', color: '#606266' }
        }]
      })
    }

    window.addEventListener('resize', handleResize)
  })
}

const updateTrendChart = () => {
  if (!trendChart) return

  let data: number[]
  let labels: string[]

  if (trendPeriod.value === 'day') {
    labels = Array.from({ length: 24 }, (_, i) => `${i}:00`)
    data = dailyTrendData.value
  } else if (trendPeriod.value === 'week') {
    labels = weekLabels.value
    data = weeklyTrendData.value
  } else {
    labels = monthLabels.value
    data = monthlyTrendData.value
  }

  trendChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: '8%', right: '5%', top: '10%', bottom: '5%', containLabel: true },
    xAxis: { type: 'category', data: labels, axisLabel: { rotate: trendPeriod.value === 'day' ? 45 : 0, color: '#606266' }, axisLine: { lineStyle: { color: '#dcdfe6' } } },
    yAxis: { type: 'value', name: 'Event Count', axisLabel: { color: '#606266' }, splitLine: { lineStyle: { color: '#ebeef5' } } },
    series: [{
      type: 'line', data: data, smooth: true,
      lineStyle: { color: '#409eff', width: 3 },
      areaStyle: { opacity: 0.1, color: '#409eff' },
      symbol: 'circle', symbolSize: 6, itemStyle: { color: '#409eff' }
    }]
  })
}

const handleResize = () => {
  trendChart?.resize()
  categoryChart?.resize()
  locationChart?.resize()
  severityChart?.resize()
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

const viewEventDetails = (event: Event) => {
  selectedEvent.value = event
  detailDialogVisible.value = true
}

const exportReport = () => {
  ElMessage.success('Exporting report...')
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  events.value = generateEvents()
  tableLoading.value = false
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

const handlePageSizeChange = () => { pagination.value.page = 1 }
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
      events.value = generateEvents()
      initTrendData()
      nextTick(() => {
        setTimeout(() => {
          initCharts()
        }, 100)
      })
    }, 500)
  }, 2500)
}

watch(trendPeriod, () => {
  updateTrendChart()
})

// ==================== Lifecycle ====================
onMounted(() => {
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

/* ==================== Main Dashboard Styles ==================== */
.event-analytics-dashboard {
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

/* KPI Cards */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.kpi-card {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.kpi-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.kpi-value {
  font-size: 32px;
  font-weight: 700;
  color: #1f2f3d;
}

.kpi-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.kpi-trend {
  font-size: 11px;
  margin-top: 4px;
  display: block;
}

.kpi-trend.up { color: #f56c6c; }
.kpi-trend.down { color: #67c23a; }

/* Dashboard Main */
.dashboard-main {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.main-left {
  flex: 1.5;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.main-right {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Card */
.card {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  overflow: hidden;
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

/* Charts */
.chart-container {
  width: 100%;
  height: 320px;
  padding: 8px;
}

.chart-container-small {
  width: 100%;
  height: 280px;
  padding: 8px;
}

/* Top Devices List */
.top-devices-list {
  padding: 16px;
}

.device-item {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.device-rank {
  width: 30px;
  height: 30px;
  background: #f5f7fa;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: #409eff;
}

.device-info {
  flex: 1;
  min-width: 120px;
}

.device-name {
  font-weight: 500;
  color: #1f2f3d;
  font-size: 13px;
}

.device-type {
  font-size: 11px;
  color: #909399;
}

.device-stats {
  text-align: right;
  min-width: 80px;
}

.device-count {
  font-weight: 600;
  color: #1f2f3d;
  font-size: 13px;
}

.device-percent {
  font-size: 11px;
  color: #909399;
}

.device-item .el-progress {
  width: 100%;
  margin-top: 4px;
}

/* Time Patterns */
.time-patterns {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  padding: 16px;
}

.pattern-item {
  text-align: center;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 12px;
}

.pattern-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.pattern-value {
  font-size: 24px;
  font-weight: 700;
  color: #409eff;
}

.pattern-value .unit {
  font-size: 12px;
  font-weight: normal;
  color: #909399;
}

.pattern-desc {
  font-size: 11px;
  color: #909399;
  margin-top: 4px;
}

/* Table */
.table-card {
  overflow-x: auto;
}

.table-controls {
  display: flex;
  gap: 12px;
}

.card-footer {
  padding: 16px 20px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  justify-content: flex-end;
  background: #fafafa;
}

/* Responsive */
@media (max-width: 1000px) {
  .dashboard-main {
    flex-direction: column;
  }
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .event-analytics-dashboard {
    padding: 16px;
  }
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  .time-patterns {
    grid-template-columns: 1fr;
  }
  .table-controls {
    flex-direction: column;
    width: 100%;
  }
}

/* Element Plus 样式覆盖 */
:deep(.el-table) {
  background: transparent;
  --el-table-header-bg-color: #fafafa;
  --el-table-row-hover-bg-color: #f5f7fa;
  --el-table-border-color: #e4e7ed;
}

:deep(.el-table th.el-table__cell) {
  background-color: #fafafa;
  color: #1f2f3d;
}

:deep(.el-table td.el-table__cell) {
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
</style>