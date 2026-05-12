<template>
  <div v-if="isPageLoaded" class="hvac-page">
    <div class="main-view">
      <div class="three-columns">
        <!-- Left Column: Key Metrics + System Status + Recent Events + Device Health -->
        <div class="col-left">
          <!-- Key Metrics -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📈 Key Metrics</div>
            <div class="metrics-list">
              <div class="metric-row">
                <div class="metric-icon">📷</div>
                <div class="metric-label">Total Cameras</div>
                <div class="metric-value">{{ totalCameras }}</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">✅</div>
                <div class="metric-label">Online Rate</div>
                <div class="metric-value">{{ onlineRate }}%</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">🚪</div>
                <div class="metric-label">Access Points</div>
                <div class="metric-value">{{ accessPoints }}</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">📊</div>
                <div class="metric-label">Today Events</div>
                <div class="metric-value">{{ todayEvents }}</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">🚨</div>
                <div class="metric-label">Active Alarms</div>
                <div class="metric-value">{{ activeAlarms }}</div>
              </div>
            </div>
          </el-card>

          <!-- Access Control Status -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🔄 Access Control</div>
            <div class="mode-list">
              <div class="mode-row" v-for="item in accessControl" :key="item.name">
                <div class="mode-name">{{ item.name }}</div>
                <div class="mode-bar-bg">
                  <div class="mode-bar-fill" :style="{ width: item.throughput + '%', background: item.color }"></div>
                </div>
                <div class="mode-value">{{ item.throughput }}%</div>
                <div class="mode-power">{{ item.status }}</div>
              </div>
            </div>
          </el-card>

          <!-- Recent Security Events -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🚨 Recent Events</div>
            <div class="alert-list">
              <div class="alert-item" v-for="event in recentEvents" :key="event.id">
                <div class="alert-header">
                  <span class="alert-tag" :class="event.severity">{{ event.severity }}</span>
                  <span class="alert-device">{{ event.location }}</span>
                </div>
                <div class="alert-msg">{{ event.description }}</div>
                <div class="alert-time">{{ event.timestamp }}</div>
              </div>
            </div>
          </el-card>

          <!-- Device Health Status -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">💚 Device Health</div>
            <div class="health-list">
              <div class="health-row" v-for="item in deviceHealth" :key="item.subsystem">
                <div class="health-dot" :class="item.status"></div>
                <div class="health-name">{{ item.subsystem }}</div>
                <div class="health-status" :class="item.status">{{ item.statusText }}</div>
              </div>
            </div>
          </el-card>
        </div>

        <!-- Center Column: Image + Charts -->
        <div class="col-center">
          <div class="title-row">
            <h1 class="page-title">SAS</h1>
            <span class="live-time">{{ currentTime }}</span>
          </div>
          <div class="card-img">
            <img :src="securityImageUrl" alt="Security 3D View" />
          </div>
          <div class="cart-view">
            <!-- Event Trend Analysis -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <div class="card-header">📊 Event Trend (Hourly)</div>
              <div ref="eventTrendChartRef" class="chart-box"></div>
            </el-card>
            <!-- Access Throughput Monitor -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <div class="card-header">⚡ Access Throughput (Last 10 min)</div>
              <div ref="throughputChartRef" class="chart-box"></div>
            </el-card>
          </div>
        </div>

        <!-- Right Column: KPIs + Zone Status + Door Status + Tips -->
        <div class="col-right">
          <!-- Security KPIs -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📊 Security KPIs</div>
            <div class="kpi-row">
              <span class="kpi-row-left">Avg. Response Time</span>
              <strong>{{ avgResponseTime }}s</strong>
              <span class="trend stable">Target < 30s</span>
            </div>
            <div class="kpi-row">
              <span class="kpi-row-left">Unauthorized Attempts</span>
              <strong>{{ unauthorizedAttempts }}</strong>
              <span class="trend up">{{ unauthorizedTrend }}</span>
            </div>
            <div class="kpi-row">
              <span class="kpi-row-left">Visitor Count</span>
              <strong>{{ visitorCount }}</strong>
              <span class="trend stable">Today</span>
            </div>
            <div class="kpi-row">
              <span class="kpi-row-left">System Uptime</span>
              <strong>{{ systemUptime }}%</strong>
              <span class="trend up">99.9% SLA</span>
            </div>
          </el-card>

          <!-- Zone Status Gauges -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🌡️ Zone Security Status</div>
            <div class="gauges-grid">
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="lobbyOccupancy" :color="zoneColor" :width="90" :stroke-width="4">
                  <template #default>
                    <span class="percentage-label">{{ lobbyCount }} ppl</span>
                  </template>
                </el-progress>
                <div class="gauge-label">Main Lobby</div>
              </div>
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="parkingOccupancy" :color="zoneColor" :width="90" :stroke-width="4">
                  <template #default>
                    <span class="percentage-label">{{ parkingCount }} cars</span>
                  </template>
                </el-progress>
                <div class="gauge-label">Parking</div>
              </div>
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="serverRoomSecurity" :color="serverRoomColor" :width="90" :stroke-width="4">
                  <template #default>
                    <span class="percentage-label">{{ serverRoomStatus }}</span>
                  </template>
                </el-progress>
                <div class="gauge-label">Server Room</div>
              </div>
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="perimeterIntegrity" :color="perimeterColor" :width="90" :stroke-width="4">
                  <template #default>
                    <span class="percentage-label">{{ perimeterStatus }}</span>
                  </template>
                </el-progress>
                <div class="gauge-label">Perimeter</div>
              </div>
            </div>
          </el-card>

          <!-- Door Status -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🎯 Door Status</div>
            <div class="setpoint-list">
              <div class="setpoint-row" v-for="item in doorStatus" :key="item.label">
                <div class="sp-label">{{ item.label }}</div>
                <div class="sp-values">
                  <span class="sp-set">Status: {{ item.status }}</span>
                  <span class="sp-actual">Last: {{ item.lastAccess }}</span>
                </div>
                <div class="sp-deviation" :class="item.alarmClass">
                  {{ item.alarm }}
                </div>
              </div>
            </div>
          </el-card>

          <!-- Security Tips -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">💡 Security Advisory</div>
            <div class="tips-list">
              <div class="tip-item" v-for="(tip, idx) in securityTips" :key="idx">
                <div class="tip-icon">{{ tip.icon }}</div>
                <div class="tip-content">
                  <div class="tip-title">{{ tip.title }}</div>
                  <div class="tip-desc">{{ tip.desc }}</div>
                  <div class="tip-saving">{{ tip.priority }}</div>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="loading-container">
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
        <div class="loading-tip">Initializing Security Access System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'

const route = useRoute()

// ==================== Loading State ====================
const isPageLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing assets...')
const securityImageUrl = ref('')

// Loading messages sequence
const loadingMessages = [
  'Preparing assets...',
  'Loading background...',
  'Loading security model...',
  'Initializing modules...',
  'Connecting to cameras...',
  'Starting dashboard...',
  'Almost ready...'
]

// ==================== Preload Assets ====================
const preloadSecurityImage = () => {
  return new Promise((resolve) => {
    const img = new Image()
    const imageUrl = 'https://aegisnx.com/wp-content/uploads/2026/05/1778228250340.png'

    img.onload = () => {
      securityImageUrl.value = imageUrl
      resolve()
    }

    img.onerror = () => {
      console.warn('Security image load failed, using fallback')
      securityImageUrl.value = imageUrl
      resolve()
    }

    img.src = imageUrl
  })
}

const preloadAssets = async () => {
  let progress = 0
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 800)

  const progressInterval = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 10
      loadingProgress.value = Math.min(progress, 90)

      if (progress > 80 && loadingMessage.value !== loadingMessages[5]) {
        loadingMessage.value = loadingMessages[5]
      } else if (progress > 60 && loadingMessage.value !== loadingMessages[4]) {
        loadingMessage.value = loadingMessages[4]
      } else if (progress > 40 && loadingMessage.value !== loadingMessages[3]) {
        loadingMessage.value = loadingMessages[3]
      } else if (progress > 20 && loadingMessage.value !== loadingMessages[2]) {
        loadingMessage.value = loadingMessages[2]
      } else if (progress > 10 && loadingMessage.value !== loadingMessages[1]) {
        loadingMessage.value = loadingMessages[1]
      }
    }
  }, 100)

  await preloadSecurityImage()

  clearInterval(messageInterval)
  clearInterval(progressInterval)
  loadingMessage.value = 'Ready!'
  loadingProgress.value = 100

  await new Promise(resolve => setTimeout(resolve, 500))
  isPageLoaded.value = true
}

// ==================== Real-time Clock ====================
const currentTime = ref('')

const updateTime = () => {
  const now = new Date()
  // 获取 UTC 毫秒数并转换为新加坡时间 (UTC+8，无夏令时)
  const utc = now.getTime() + (now.getTimezoneOffset() * 60000)
  const sgTime = new Date(utc + (8 * 3600000))

  const year = sgTime.getFullYear()
  const month = String(sgTime.getMonth() + 1).padStart(2, '0')
  const day = String(sgTime.getDate()).padStart(2, '0')
  const hours = String(sgTime.getHours()).padStart(2, '0')
  const minutes = String(sgTime.getMinutes()).padStart(2, '0')
  const seconds = String(sgTime.getSeconds()).padStart(2, '0')
  const ms = String(sgTime.getMilliseconds()).padStart(3, '0')

  currentTime.value = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}.${ms} SGT`
}

let clockTimer = null

// ==================== Core Security Data ====================
// Key metrics
const totalCameras = ref(256)
const onlineRate = ref(98.4)
const accessPoints = ref(48)
const todayEvents = ref(1523)
const activeAlarms = ref(2)

// Security KPIs
const avgResponseTime = ref(12)
const unauthorizedAttempts = ref(7)
const unauthorizedTrend = ref('↓15% vs Yesterday')
const visitorCount = ref(89)
const systemUptime = ref(99.97)

// Zone status
const lobbyCount = ref(45)
const parkingCount = ref(128)
const serverRoomStatus = ref('Locked')
const perimeterStatus = ref('Secure')

const lobbyOccupancy = ref(45)
const parkingOccupancy = ref(64)
const serverRoomSecurity = ref(95)
const perimeterIntegrity = ref(98)

// Zone colors
const zoneColor = [
  { color: '#10b981', percentage: 50 },
  { color: '#f59e0b', percentage: 80 },
  { color: '#ef4444', percentage: 100 }
]
const serverRoomColor = [
  { color: '#10b981', percentage: 90 },
  { color: '#ef4444', percentage: 100 }
]
const perimeterColor = [
  { color: '#10b981', percentage: 90 },
  { color: '#ef4444', percentage: 100 }
]

// Access control throughput
const accessControl = ref([
  { name: 'Main Entrance', throughput: 85, status: 'Peak', color: '#fbbf24' },
  { name: 'Staff Gate', throughput: 62, status: 'Normal', color: '#3b82f6' },
  { name: 'Parking Gate', throughput: 78, status: 'Busy', color: '#60a5fa' },
  { name: 'Delivery Bay', throughput: 35, status: 'Low', color: '#34d399' }
])

// Recent security events
const recentEvents = ref([
  { id: 1, severity: 'Warning', location: 'Parking Level B2', description: 'Unauthorized vehicle detected at fire lane', timestamp: '2 min ago' },
  { id: 2, severity: 'Critical', location: 'Server Room Door', description: 'Multiple invalid badge attempts (5x)', timestamp: '8 min ago' },
  { id: 3, severity: 'Warning', location: 'Emergency Exit 3F', description: 'Door held open > 60 seconds', timestamp: '22 min ago' }
])

// Device health
const deviceHealth = ref([
  { subsystem: 'CCTV Network', status: 'normal', statusText: 'Online' },
  { subsystem: 'Access Controllers', status: 'warning', statusText: '1 Offline' },
  { subsystem: 'Alarm System', status: 'normal', statusText: 'Armed' },
  { subsystem: 'Intercom Panels', status: 'normal', statusText: 'Normal' },
  { subsystem: 'Storage (NVR)', status: 'normal', statusText: '72% Free' }
])

// Door status
const doorStatus = ref([
  { label: 'Main Entrance', status: 'Locked', lastAccess: '08:45:22', alarm: 'Normal', alarmClass: 'normal' },
  { label: 'Server Room', status: 'Locked', lastAccess: '07:30:15', alarm: 'Alert', alarmClass: 'high' },
  { label: 'Fire Exit 2F', status: 'Closed', lastAccess: '--', alarm: 'Normal', alarmClass: 'normal' },
  { label: 'Loading Dock', status: 'Open', lastAccess: '09:12:08', alarm: 'Warning', alarmClass: 'low' }
])

// Security tips
const securityTips = ref([
  { icon: '🔐', title: 'Review Badge Access', desc: '3 badges with expired clearance detected today', priority: 'High Priority' },
])

// ==================== Charts ====================
const eventTrendChartRef = ref(null)
const throughputChartRef = ref(null)
let eventTrendChart = null
let throughputChart = null

// 12-hour event history
const eventHistoryLength = 12
const eventHistory = ref([])
const eventHourLabels = ref([])

const initEventHistory = () => {
  eventHistory.value = []
  eventHourLabels.value = []
  const now = new Date()
  for (let i = eventHistoryLength - 1; i >= 0; i--) {
    const t = new Date(now - i * 3600000)
    eventHourLabels.value.push(t.toTimeString().slice(0, 5))
    eventHistory.value.push({
      'Access Granted': 80 + Math.random() * 40,
      'Access Denied': 3 + Math.random() * 8,
      'Alarm Triggered': 1 + Math.random() * 3,
      'Door Forced': Math.random() > 0.7 ? 1 : 0
    })
  }
}

// 10-minute throughput history
const throughputHistoryLength = 10
const throughputHistory = ref([])
const throughputTimeLabels = ref([])

const initThroughputHistory = () => {
  const now = new Date()
  throughputHistory.value = []
  throughputTimeLabels.value = []
  for (let i = throughputHistoryLength - 1; i >= 0; i--) {
    const t = new Date(now - i * 60000)
    throughputTimeLabels.value.push(t.toTimeString().slice(0, 5))
    throughputHistory.value.push({
      'Main Entrance': 25 + Math.random() * 15,
      'Staff Gate': 18 + Math.random() * 12,
      'Parking': 12 + Math.random() * 10,
      'Delivery': 3 + Math.random() * 5
    })
  }
}

// Event trend bar chart option (hourly)
const getEventTrendOption = () => {
  const categories = ['Access Granted', 'Access Denied', 'Alarm Triggered', 'Door Forced']
  const colors = ['#34d399', '#fbbf24', '#f97316', '#ef4444']

  return {
    backgroundColor: 'transparent',
    grid: { left: '3%', right: '4%', bottom: '0%', top: '20%', containLabel: true },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15,25,45,0.9)',
      borderColor: '#3b82f6',
      textStyle: { color: '#e2e8f0' }
    },
    legend: { textStyle: { color: '#94a3b8', fontSize: 9 }, top: 0 },
    xAxis: {
      type: 'category',
      data: eventHourLabels.value,
      axisLabel: { color: '#94a3b8', fontSize: 9, rotate: 15 },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    yAxis: {
      type: 'value',
      name: 'Events',
      nameTextStyle: { color: '#64748b', fontSize: 10 },
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } }
    },
    series: categories.map((name, i) => ({
      name,
      type: 'bar',
      stack: 'total',
      data: eventHistory.value.map(d => d[name]),
      itemStyle: {
        color: colors[i],
        borderRadius: i === categories.length - 1 ? [6, 6, 0, 0] : 0,
        borderWidth: 0
      },
      emphasis: {
        focus: 'series'
      }
    }))
  }
}

// Access throughput line chart option
const getThroughputOption = () => {
  const categories = ['Main Entrance', 'Staff Gate', 'Parking', 'Delivery']
  const colors = ['#60a5fa', '#34d399', '#fbbf24', '#f97316']

  const seriesData = categories.map((name, i) => ({
    name,
    type: 'line',
    data: throughputHistory.value.map(d => d[name]),
    smooth: true,
    symbol: 'circle',
    symbolSize: 5,
    lineStyle: { width: 2, color: colors[i] },
    itemStyle: { color: colors[i] },
    areaStyle: {
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: colors[i] + '30' },
        { offset: 1, color: colors[i] + '00' }
      ])
    }
  }))

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15,25,45,0.9)',
      borderColor: '#3b82f6',
      textStyle: { color: '#e2e8f0' },
      valueFormatter: (value) => value + ' persons'
    },
    legend: { textStyle: { color: '#94a3b8', fontSize: 9 }, top: 0 },
    grid: { left: '3%', right: '4%', bottom: '0%', top: '20%', containLabel: true },
    xAxis: {
      type: 'category',
      data: throughputTimeLabels.value,
      axisLabel: { color: '#94a3b8', fontSize: 9 },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    yAxis: {
      type: 'value',
      name: 'Persons/min',
      nameTextStyle: { color: '#64748b', fontSize: 10 },
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } }
    },
    series: seriesData
  }
}

// ==================== Chart Lifecycle ====================
const disposeCharts = () => {
  if (eventTrendChart) {
    eventTrendChart.dispose()
    eventTrendChart = null
  }
  if (throughputChart) {
    throughputChart.dispose()
    throughputChart = null
  }
}

const initCharts = async () => {
  await nextTick()

  for (let attempt = 0; attempt < 5; attempt++) {
    await new Promise(resolve => setTimeout(resolve, 100))

    const evtDom = eventTrendChartRef.value
    const thrDom = throughputChartRef.value

    if (!evtDom || !thrDom) continue
    if (evtDom.clientWidth === 0 || evtDom.clientHeight === 0) continue
    if (thrDom.clientWidth === 0 || thrDom.clientHeight === 0) continue

    disposeCharts()

    try {
      eventTrendChart = echarts.init(evtDom)
      throughputChart = echarts.init(thrDom)

      eventTrendChart.setOption(getEventTrendOption())
      throughputChart.setOption(getThroughputOption())

      return
    } catch (e) {
      console.error('[initCharts] Error:', e)
    }
  }
}

const handleResize = () => {
  eventTrendChart?.resize()
  throughputChart?.resize()
}

let fullscreenTimer = null
const onFullscreenChange = () => {
  clearTimeout(fullscreenTimer)
  fullscreenTimer = setTimeout(handleResize, 350)
}

// ==================== Live Update ====================
let updateTimer = null

const updateAllData = () => {
  // KPIs
  totalCameras.value = 254 + Math.floor(Math.random() * 5)
  onlineRate.value = parseFloat((97.8 + Math.random() * 1.2).toFixed(1))
  todayEvents.value = todayEvents.value + Math.floor(Math.random() * 3)
  activeAlarms.value = Math.floor(Math.random() * 4)
  avgResponseTime.value = Math.floor(10 + Math.random() * 8)
  unauthorizedAttempts.value = Math.floor(5 + Math.random() * 6)
  visitorCount.value = visitorCount.value + Math.floor(Math.random() * 2)

  // Zone counts
  lobbyCount.value = Math.floor(35 + Math.random() * 20)
  parkingCount.value = Math.floor(110 + Math.random() * 30)
  lobbyOccupancy.value = Math.round((lobbyCount.value / 100) * 100)
  parkingOccupancy.value = Math.round((parkingCount.value / 200) * 100)
  serverRoomSecurity.value = Math.random() > 0.9 ? 85 : 95
  serverRoomStatus.value = serverRoomSecurity.value > 90 ? 'Locked' : 'Alert'
  perimeterIntegrity.value = Math.random() > 0.95 ? 90 : 98
  perimeterStatus.value = perimeterIntegrity.value > 95 ? 'Secure' : 'Breach'

  // Access control
  accessControl.value = [
    { name: 'Main Entrance', throughput: 75 + Math.floor(Math.random() * 20), status: Math.random() > 0.3 ? 'Peak' : 'Busy', color: '#fbbf24' },
    { name: 'Staff Gate', throughput: 55 + Math.floor(Math.random() * 15), status: 'Normal', color: '#3b82f6' },
    { name: 'Parking Gate', throughput: 70 + Math.floor(Math.random() * 15), status: 'Busy', color: '#60a5fa' },
    { name: 'Delivery Bay', throughput: 28 + Math.floor(Math.random() * 12), status: 'Low', color: '#34d399' }
  ]

  // Device health
  deviceHealth.value = [
    { subsystem: 'CCTV Network', status: Math.random() > 0.98 ? 'warning' : 'normal', statusText: Math.random() > 0.98 ? 'Lag' : 'Online' },
    { subsystem: 'Access Controllers', status: Math.random() > 0.85 ? 'warning' : 'normal', statusText: Math.random() > 0.85 ? '1 Offline' : 'Normal' },
    { subsystem: 'Alarm System', status: 'normal', statusText: 'Armed' },
    { subsystem: 'Intercom Panels', status: 'normal', statusText: 'Normal' },
    { subsystem: 'Storage (NVR)', status: 'normal', statusText: '72% Free' }
  ]

  // Door status
  doorStatus.value = [
    { label: 'Main Entrance', status: 'Locked', lastAccess: new Date().toTimeString().slice(0, 8), alarm: 'Normal', alarmClass: 'normal' },
    { label: 'Server Room', status: Math.random() > 0.9 ? 'Unlocked' : 'Locked', lastAccess: '07:30:15', alarm: Math.random() > 0.9 ? 'Alert' : 'Normal', alarmClass: Math.random() > 0.9 ? 'high' : 'normal' },
    { label: 'Fire Exit 2F', status: 'Closed', lastAccess: '--', alarm: 'Normal', alarmClass: 'normal' },
    { label: 'Loading Dock', status: Math.random() > 0.6 ? 'Open' : 'Closed', lastAccess: '09:12:08', alarm: Math.random() > 0.6 ? 'Warning' : 'Normal', alarmClass: Math.random() > 0.6 ? 'low' : 'normal' }
  ]

  // Tips
  const tipPool = [
    { icon: '🔐', title: 'Review Badge Access', desc: '3 badges with expired clearance detected today', priority: 'High Priority' },
    { icon: '📹', title: 'Storage Check', desc: 'NVR retention remaining: 12 days at current bitrate', priority: 'Medium Priority' },
    { icon: '🚪', title: 'Door Audit', desc: 'Loading dock door open 2+ hours today', priority: 'Low Priority' },
    { icon: '📋', title: 'Visitor Log', desc: '5 visitors still checked in after 18:00', priority: 'Medium Priority' }
  ]
  securityTips.value = tipPool.sort(() => Math.random() - 0.5).slice(0, 1)

  // Update charts
  if (eventTrendChart && throughputChart) {
    const now = new Date()
    eventHourLabels.value.push(now.toTimeString().slice(0, 5))
    if (eventHourLabels.value.length > eventHistoryLength) eventHourLabels.value.shift()

    eventHistory.value.push({
      'Access Granted': 80 + Math.random() * 40,
      'Access Denied': 3 + Math.random() * 8,
      'Alarm Triggered': 1 + Math.random() * 3,
      'Door Forced': Math.random() > 0.7 ? 1 : 0
    })
    if (eventHistory.value.length > eventHistoryLength) eventHistory.value.shift()

    eventTrendChart.setOption({
      xAxis: { data: eventHourLabels.value },
      series: ['Access Granted', 'Access Denied', 'Alarm Triggered', 'Door Forced'].map(name => ({
        data: eventHistory.value.map(d => d[name])
      }))
    })

    throughputTimeLabels.value.push(now.toTimeString().slice(0, 5))
    if (throughputTimeLabels.value.length > throughputHistoryLength) throughputTimeLabels.value.shift()

    throughputHistory.value.push({
      'Main Entrance': 25 + Math.random() * 15,
      'Staff Gate': 18 + Math.random() * 12,
      'Parking': 12 + Math.random() * 10,
      'Delivery': 3 + Math.random() * 5
    })
    if (throughputHistory.value.length > throughputHistoryLength) throughputHistory.value.shift()

    throughputChart.setOption({
      xAxis: { data: throughputTimeLabels.value },
      series: ['Main Entrance', 'Staff Gate', 'Parking', 'Delivery'].map(name => ({
        data: throughputHistory.value.map(d => d[name])
      }))
    })
  }
}

let routeWatch = null

onMounted(async () => {
  updateTime()
  clockTimer = setInterval(updateTime, 1000)

  await preloadAssets()

  initEventHistory()
  initThroughputHistory()
  await initCharts()

  if (eventTrendChart && throughputChart) {
    updateTimer = setInterval(updateAllData, 5000)
  }

  window.addEventListener('resize', handleResize)
  document.addEventListener('fullscreenchange', onFullscreenChange)

  routeWatch = watch(() => route.fullPath, async () => {
    initEventHistory()
    initThroughputHistory()
    await initCharts()
    if (eventTrendChart && throughputChart && !updateTimer) {
      updateTimer = setInterval(updateAllData, 5000)
    }
  })
})

onBeforeUnmount(() => {
  clearInterval(clockTimer)
  clearInterval(updateTimer)
  clearTimeout(fullscreenTimer)
  window.removeEventListener('resize', handleResize)
  document.removeEventListener('fullscreenchange', onFullscreenChange)
  if (routeWatch) routeWatch()
  disposeCharts()
})
</script>

<style scoped>
/* Loading Screen Styles */
.loading-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #0a1620 0%, #03060c 100%);
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
  background: rgba(15, 25, 45, 0.6);
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
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
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

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.3;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
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
  0% {
    background-position: 0% 0%;
  }
  100% {
    background-position: 200% 0%;
  }
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
  0%, 100% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Main SAS Page Styles */
.hvac-page {
  height: 100%;
  background: radial-gradient(circle at 10% 20%, #0a1620, #03060c);
  padding: 24px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.title-row {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  flex-shrink: 0;
}

.page-title {
  font-size: 32px;
  font-weight: 800;
  background: linear-gradient(135deg, #e2e8f0, #60a5fa);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  letter-spacing: 1px;
  text-shadow: 0 0 8px rgba(96,165,250,0.4);
  margin: 0;
}

.live-time {
  position: absolute;
  right: 0;
  font-size: 14px;
  font-weight: 600;
  color: #facc15;
  font-family: monospace;
  letter-spacing: 1px;
  text-shadow: 0 0 6px rgba(250, 204, 21, 0.3);
  padding: 6px 14px;
  background: rgba(15, 25, 45, 0.6);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 10px;
  backdrop-filter: blur(8px);
}

.main-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.three-columns {
  flex: 1;
  display: flex;
  gap: 20px;
  align-items: stretch;
  min-height: 0;
}

.col-left, .col-right {
  width: 300px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  min-height: 0;
}
.col-left::-webkit-scrollbar,
.col-right::-webkit-scrollbar {
  display: none;
}

.col-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 0;
}

.glass-card, .card-img {
  background: rgba(15,25,45,0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(59,130,246,0.3);
  border-radius: 20px;
  transition: all 0.3s;
}
.glass-card:hover {
  background: rgba(15,25,45,0.8);
  border-color: rgba(59,130,246,0.6);
  transform: translateY(-3px);
}
.card {
  background: transparent;
}
.card-img {
  overflow: hidden;
  background: rgba(0,0,0,0.3);
}
.card-img img {
  width: 100%;
  display: block;
  height: auto;
  border-radius: 10px;
}

.card-header {
  font-weight: 600;
  margin-bottom: 10px;
  font-size: 16px;
  color: #e2e8f0;
  border-left: 4px solid #3b82f6;
  padding-left: 10px;
}

.metrics-list {
  display: flex;
  flex-direction: column;
}
.metric-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
}
.metric-row .metric-icon {
  font-size: 24px;
  width: 36px;
  opacity: 0.9;
}
.metric-row .metric-label {
  flex: 1;
  font-size: 14px;
  color: #94a3b8;
  padding-left: 12px;
  letter-spacing: 0.3px;
}
.metric-row .metric-value {
  font-size: 18px;
  font-weight: 600;
  color: #facc15;
  text-align: right;
  font-family: monospace;
}

.mode-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.mode-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #cbd5e1;
}
.mode-name {
  width: 80px;
  flex-shrink: 0;
}
.mode-bar-bg {
  flex: 1;
  height: 6px;
  background: rgba(148, 163, 184, 0.15);
  border-radius: 3px;
  overflow: hidden;
}
.mode-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s;
}
.mode-value {
  width: 35px;
  text-align: right;
  color: #facc15;
}
.mode-power {
  width: 55px;
  text-align: right;
  color: #94a3b8;
}

.alert-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.alert-item {
  background: rgba(239, 68, 68, 0.05);
  border-radius: 8px;
  padding: 4px 10px;
  border-left: 3px solid #ef4444;
}
.alert-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}
.alert-tag {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  padding: 2px 6px;
  border-radius: 4px;
}
.alert-tag.Warning {
  background: rgba(251, 191, 36, 0.2);
  color: #fbbf24;
}
.alert-tag.Critical {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}
.alert-device {
  font-size: 12px;
  font-weight: 600;
  color: #e2e8f0;
}
.alert-msg {
  font-size: 11px;
  color: #94a3b8;
  margin-bottom: 2px;
}
.alert-time {
  font-size: 10px;
  color: #64748b;
}

.health-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.health-row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
}
.health-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.health-dot.normal { background: #34d399; box-shadow: 0 0 6px #34d399; }
.health-dot.warning { background: #fbbf24; box-shadow: 0 0 6px #fbbf24; }
.health-dot.critical { background: #ef4444; box-shadow: 0 0 6px #ef4444; }
.health-name {
  flex: 1;
  color: #cbd5e1;
}
.health-status {
  font-weight: 600;
  text-transform: uppercase;
}
.health-status.normal { color: #34d399; }
.health-status.warning { color: #fbbf24; }
.health-status.critical { color: #ef4444; }

.cart-view {
  width: 100%;
  display: flex;
  flex: 1;
  background: transparent;
  overflow-y: auto;
  gap: 10px;
  min-height: 0;
}
.chart-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.chart-card .card-header {
  flex-shrink: 0;
}
.chart-box {
  flex: 1;
  width: 100%;
  min-height: 0;
  overflow: hidden;
  padding: 8px;
  box-sizing: border-box;
}

.gauges-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}
.gauge-item { text-align: center; }
.gauge-label { font-size: 13px; color: #cbd5e1; margin-top: 0px; height: 20px; text-align: center; align-items: center; }

.kpi-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 13px;
  color: #cbd5e6;
}
.kpi-row span {
  text-align: left;
}
.kpi-row-left {
  min-width: 100px;
  max-width: 100px;
  text-align: left;
}
.kpi-row strong {
  font-size: 16px;
  color: #facc15;
  text-align: center;
}
.trend {
  width: 70px;
  font-size: 11px;
  margin-left: 8px;
  text-align: right;
  font-weight: bold;
}
.trend.up { color: #34d399; text-align: right; }
.trend.stable { color: #fbbf24; text-align: right; }

.setpoint-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.setpoint-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
}
.sp-label {
  flex: 1;
  color: #94a3b8;
  font-size: 13px;
  font-weight: bold;
}
.sp-values {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: center;
  align-items: center;
  gap: 2px;
  margin-right: 8px;
}
.sp-set {
  font-size: 10px;
  color: #cbd5e1;
  font-weight: bold;
}
.sp-actual {
  font-weight: 600;
  text-align: center;
  color: #fbbf24;
}
.sp-deviation {
  width: 60px;
  text-align: right;
  font-weight: 700;
  font-size: 12px;
}
.sp-deviation.high { color: #ef4444; }
.sp-deviation.low { color: #3b82f6; }
.sp-deviation.normal { color: #34d399; }

.tips-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.tip-item {
  display: flex;
  gap: 10px;
  padding: 8px 10px;
  background: rgba(59,130,246,0.08);
  border-radius: 8px;
  border-left: 3px solid #3b82f6;
  margin-top: 5px;
}
.tip-icon {
  font-size: 18px;
  flex-shrink: 0;
  margin-top: 2px;
}
.tip-content {
  flex: 1;
}
.tip-title {
  font-size: 12px;
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 2px;
}
.tip-desc {
  font-size: 11px;
  color: #94a3b8;
  line-height: 1.4;
  margin-bottom: 2px;
}
.tip-saving {
  font-size: 10px;
  color: #facc15;
  font-weight: 600;
}

.percentage-value {
  display: block;
  margin-top: 10px;
  font-size: 18px;
}
.percentage-label {
  display: block;
  margin-top: 10px;
  font-size: 12px;
  color: #facc15;
  font-weight: bold;
}
</style>

<style>
.el-card__body {
  scrollbar-width: none;
  -ms-overflow-style: none;
  overflow: visible !important;
}
.col-left .el-card,
.col-right .el-card {
  overflow: visible;
  height: auto;
  flex-shrink: 0;
}
.chart-card .el-card__body {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style>