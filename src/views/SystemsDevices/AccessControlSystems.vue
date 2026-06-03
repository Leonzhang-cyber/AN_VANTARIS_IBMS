<template>
  <div v-if="isPageLoaded" class="access-page">
    <div class="main-view">
      <div class="three-columns">
        <!-- Left Column: Key Metrics + Door Status + Access Events + System Health -->
        <div class="col-left">
          <div class="title-row" v-if="isMobile">
            <h1 class="page-title">Access Control</h1>
            <span class="live-time">{{ currentTime }}</span>
          </div>
          <div class="card-img" v-if="isMobile">
            <img :src="accessImageUrl" alt="Access Control 3D View" />
          </div>

          <!-- Key Metrics -->
          <el-card class="card glass-card" shadow="hover" body-style="padding: 16px;">
            <template #header>
              <div class="card-header">🔐 Access Metrics</div>
            </template>
            <div class="metrics-list">
              <div class="metric-row">
                <div class="metric-icon">🚪</div>
                <div class="metric-label">Total Doors</div>
                <div class="metric-value">{{ totalDoors }}</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">🔓</div>
                <div class="metric-label">Online Doors</div>
                <div class="metric-value">{{ onlineDoors }}</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">⚠️</div>
                <div class="metric-label">Offline Doors</div>
                <div class="metric-value">{{ offlineDoors }}</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">👥</div>
                <div class="metric-label">Active Credentials</div>
                <div class="metric-value">{{ activeCredentials }}</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">📊</div>
                <div class="metric-label">Today's Accesses</div>
                <div class="metric-value">{{ todayAccesses }}</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">🚫</div>
                <div class="metric-label">Denied Attempts</div>
                <div class="metric-value">{{ deniedAttempts }}</div>
              </div>
            </div>
          </el-card>

          <!-- Door Status Distribution -->
          <el-card class="card glass-card" shadow="hover" body-style="padding: 16px;">
            <template #header>
              <div class="card-header">🚪 Door Status by Zone</div>
            </template>
            <div class="mode-list">
              <div class="mode-row" v-for="zone in doorZones" :key="zone.name">
                <div class="mode-name">{{ zone.name }}</div>
                <div class="mode-bar-bg">
                  <div class="mode-bar-fill" :style="{ width: zone.onlinePercent + '%', background: zone.color }"></div>
                </div>
                <div class="mode-value">{{ zone.onlinePercent }}%</div>
                <div class="mode-power">{{ zone.onlineCount }}/{{ zone.totalCount }}</div>
              </div>
            </div>
          </el-card>

          <!-- Access Methods Distribution -->
          <el-card class="card glass-card" shadow="hover" body-style="padding: 16px;">
            <template #header>
              <div class="card-header">🆔 Access Methods (Today)</div>
            </template>
            <div class="mode-list">
              <div class="mode-row" v-for="method in accessMethods" :key="method.name">
                <div class="mode-name">{{ method.name }}</div>
                <div class="mode-bar-bg">
                  <div class="mode-bar-fill" :style="{ width: method.percent + '%', background: method.color }"></div>
                </div>
                <div class="mode-value">{{ method.count }}</div>
                <div class="mode-power">{{ method.percent }}%</div>
              </div>
            </div>
          </el-card>

          <!-- System Health -->
          <el-card class="card glass-card" shadow="hover" body-style="padding: 16px;">
            <template #header>
              <div class="card-header">💚 System Health</div>
            </template>
            <div class="health-list">
              <div class="health-row" v-for="item in systemHealth" :key="item.subsystem">
                <div class="health-dot" :class="item.status"></div>
                <div class="health-name">{{ item.subsystem }}</div>
                <div class="health-status" :class="item.status">{{ item.statusText }}</div>
              </div>
            </div>
          </el-card>
        </div>

        <!-- Center Column: Image + Charts -->
        <div class="col-center">
          <div class="title-row" v-if="!isMobile">
            <h1 class="page-title">Access Control</h1>
            <span class="live-time" v-if="isFullscreen">{{ currentTime }}</span>
          </div>
          <div class="card-img" v-if="!isMobile">
            <img :src="accessImageUrl" alt="Access Control 3D View" />
          </div>
          <div class="cart-view">
            <el-card class="card glass-card chart-card" shadow="hover" body-style="padding: 8px; height: 100%;">
              <template #header>
                <div class="card-header">📊 Access Traffic (Last 24h)</div>
              </template>
              <div ref="trafficChartRef" class="chart-box"></div>
            </el-card>
            <el-card class="card glass-card chart-card" shadow="hover" body-style="padding: 8px; height: 100%;">
              <template #header>
                <div class="card-header">⏰ Access Method Distribution</div>
              </template>
              <div ref="patternChartRef" class="chart-box"></div>
            </el-card>
          </div>
        </div>

        <!-- Right Column: Recent Events + Personnel Status + Security Alerts -->
        <div class="col-right">
          <!-- Zone KPIs -->
          <el-card class="card glass-card" shadow="hover" body-style="padding: 16px;">
            <template #header>
              <div class="card-header">🏢 Zone Activity</div>
            </template>
            <div class="kpi-row" v-for="zone in zoneActivity" :key="zone.name">
              <span>{{ zone.name }}</span>
              <strong>{{ zone.accessCount }}</strong>
              <span class="trend" :class="zone.trend">{{ zone.trend === 'up' ? '↑' : '↓' }} {{ zone.change }}%</span>
            </div>
          </el-card>

          <!-- Recent Access Events -->
          <el-card class="card glass-card" shadow="hover" body-style="padding: 16px;">
            <template #header>
              <div class="card-header">🕐 Recent Access Events</div>
            </template>
            <div class="events-list">
              <div
                  v-for="event in recentEvents"
                  :key="event.id"
                  class="event-item"
                  :class="event.type"
              >
                <div class="event-icon">
                  <span v-if="event.type === 'granted'">✅</span>
                  <span v-else-if="event.type === 'denied'">❌</span>
                  <span v-else>⚠️</span>
                </div>
                <div class="event-details">
                  <div class="event-title">{{ event.user }} - {{ event.door }}</div>
                  <div class="event-meta">{{ event.method }} • {{ event.time }}</div>
                </div>
                <div class="event-status" :class="event.type">
                  <span v-if="event.type === 'granted'">Granted</span>
                  <span v-else-if="event.type === 'denied'">Denied</span>
                  <span v-else>Alert</span>
                </div>
              </div>
            </div>
          </el-card>

          <!-- Personnel Status -->
          <el-card class="card glass-card" shadow="hover" body-style="padding: 16px;">
            <template #header>
              <div class="card-header">👥 Personnel Status</div>
            </template>
            <div class="kpi-row">
              <span>Total Personnel</span>
              <strong>{{ totalPersonnel }}</strong>
              <span class="trend stable">+{{ newToday }} today</span>
            </div>
            <div class="kpi-row">
              <span>Currently Inside</span>
              <strong>{{ currentlyInside }}</strong>
              <span class="trend up">{{ occupancyRate }}% occupancy</span>
            </div>
            <div class="kpi-row">
              <span>Visitors Today</span>
              <strong>{{ visitorCount }}</strong>
              <span class="trend up">+{{ visitorChange }}%</span>
            </div>
            <div class="kpi-row">
              <span>Contractors</span>
              <strong>{{ contractorCount }}</strong>
              <span class="trend stable">Active</span>
            </div>
          </el-card>

          <!-- Security Alerts -->
          <el-card class="card glass-card" shadow="hover" body-style="padding: 16px;">
            <template #header>
              <div class="card-header">⚠️ Security Alerts</div>
            </template>
            <div class="tips-list">
              <div class="tip-item" v-for="(alert, idx) in securityAlerts" :key="idx">
                <div class="tip-icon">{{ alert.icon }}</div>
                <div class="tip-content">
                  <div class="tip-title">{{ alert.title }}</div>
                  <div class="tip-desc">{{ alert.desc }}</div>
                  <div class="tip-saving">{{ alert.severity }} • {{ alert.time }}</div>
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
        <div class="loading-tip">Initializing Access Control System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'

import { useCounterStore } from '@/stores/counter.js'
import { getCurrentInstance } from 'vue'

const getStore = () => {
  const instance = getCurrentInstance()
  if (!instance) {
    throw new Error('useStore() must be called within a setup function')
  }
  const pinia = instance.appContext.config.globalProperties.$pinia
  if (!pinia) {
    throw new Error('Pinia instance not found. Did you forget to call app.use(pinia)?')
  }
  return useCounterStore(pinia)
}
const counterStore = getStore()
const isFullscreen = computed(() => counterStore.isFullscreen)

const route = useRoute()

// ==================== Loading State ====================
const isPageLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing assets...')
const accessImageUrl = ref('')

const loadingMessages = [
  'Preparing assets...',
  'Loading background...',
  'Loading door controllers...',
  'Initializing modules...',
  'Connecting to sensors...',
  'Starting dashboard...',
  'Almost ready...'
]

// ==================== Real-time Clock ====================
const currentTime = ref('')

const updateTime = () => {
  const now = new Date()
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

// ==================== Preload Assets ====================
const preloadAccessImage = () => {
  return new Promise((resolve) => {
    const img = new Image()
    const imageUrl = 'https://aegisnx.com/wp-content/uploads/2026/05/1779335433399.png'
    img.onload = () => {
      accessImageUrl.value = imageUrl
      resolve()
    }
    img.onerror = () => {
      console.warn('Access image load failed, using fallback')
      accessImageUrl.value = imageUrl
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
      if (progress > 80) loadingMessage.value = loadingMessages[5]
      else if (progress > 60) loadingMessage.value = loadingMessages[4]
      else if (progress > 40) loadingMessage.value = loadingMessages[3]
      else if (progress > 20) loadingMessage.value = loadingMessages[2]
      else if (progress > 10) loadingMessage.value = loadingMessages[1]
    }
  }, 100)
  await preloadAccessImage()
  clearInterval(messageInterval)
  clearInterval(progressInterval)
  loadingMessage.value = 'Ready!'
  loadingProgress.value = 100
  await new Promise(resolve => setTimeout(resolve, 500))
  isPageLoaded.value = true
}

// ==================== Core Access Data ====================
const totalDoors = ref(156)
const onlineDoors = ref(152)
const offlineDoors = ref(4)
const activeCredentials = ref(2847)
const todayAccesses = ref(1248)
const deniedAttempts = ref(23)

const totalPersonnel = ref(1850)
const currentlyInside = ref(623)
const visitorCount = ref(87)
const contractorCount = ref(42)
const visitorChange = ref(12)
const newToday = ref(8)
const occupancyRate = computed(() => Math.round((currentlyInside.value / totalPersonnel.value) * 100))

const doorZones = ref([
  { name: 'Lobby Area', onlinePercent: 100, onlineCount: 8, totalCount: 8, color: '#34d399' },
  { name: 'Office Floors', onlinePercent: 97, onlineCount: 29, totalCount: 30, color: '#3b82f6' },
  { name: 'Parking Area', onlinePercent: 95, onlineCount: 19, totalCount: 20, color: '#fbbf24' },
  { name: 'Server Room', onlinePercent: 100, onlineCount: 6, totalCount: 6, color: '#ef4444' },
  { name: 'Warehouse', onlinePercent: 92, onlineCount: 11, totalCount: 12, color: '#8b5cf6' },
  { name: 'Restricted Areas', onlinePercent: 100, onlineCount: 15, totalCount: 15, color: '#ec489a' }
])

const accessMethods = ref([
  { name: 'RFID Card', count: 845, percent: 68, color: '#3b82f6' },
  { name: 'Biometric', count: 212, percent: 17, color: '#10b981' },
  { name: 'Mobile App', count: 125, percent: 10, color: '#f59e0b' },
  { name: 'Keypad PIN', count: 48, percent: 4, color: '#8b5cf6' },
  { name: 'Intercom', count: 18, percent: 1, color: '#ec489a' }
])

const zoneActivity = ref([
  { name: 'Lobby', accessCount: 342, trend: 'up', change: 8 },
  { name: 'Office Floors', accessCount: 567, trend: 'up', change: 5 },
  { name: 'Parking', accessCount: 189, trend: 'down', change: 3 },
  { name: 'Server Room', accessCount: 45, trend: 'up', change: 2 },
  { name: 'Warehouse', accessCount: 78, trend: 'down', change: 4 }
])

const recentEvents = ref([
  { id: 1, type: 'granted', user: 'John Chen', door: 'Main Lobby - Gate A', method: 'RFID Card', time: '2 min ago' },
  { id: 2, type: 'granted', user: 'Sarah Wong', door: 'Office 3F - East', method: 'Biometric', time: '5 min ago' },
  { id: 3, type: 'denied', user: 'Unknown', door: 'Server Room', method: 'Invalid Card', time: '8 min ago' },
  { id: 4, type: 'granted', user: 'Mike Lim', door: 'Parking B1', method: 'Mobile App', time: '12 min ago' },
  { id: 5, type: 'alert', user: 'Door Forced', door: 'Emergency Exit - West', method: 'Alarm', time: '18 min ago' },
  { id: 6, type: 'granted', user: 'Lisa Tan', door: 'Executive Suite', method: 'Biometric', time: '25 min ago' }
])

const systemHealth = ref([
  { subsystem: 'Door Controllers', status: 'normal', statusText: 'Online' },
  { subsystem: 'Network Gateways', status: 'normal', statusText: 'Connected' },
  { subsystem: 'Biometric Readers', status: 'warning', statusText: '2 Offline' },
  { subsystem: 'Database Server', status: 'normal', statusText: 'Synced' },
  { subsystem: 'Backup System', status: 'normal', statusText: 'Ready' }
])

const securityAlerts = ref([
  { icon: '🚪', title: 'Door Ajar Detected', desc: 'Fire Exit - East Wing door left open', severity: 'Medium', time: '5 min ago' },
  { icon: '🔑', title: 'Repeated Access Denied', desc: '3 failed attempts at Server Room door', severity: 'High', time: '15 min ago' },
  { icon: '📹', title: 'Camera Offline', desc: 'Lobby camera disconnected', severity: 'Low', time: '32 min ago' }
])

// ==================== Charts ====================
const trafficChartRef = ref(null)
const patternChartRef = ref(null)
let trafficChart = null
let patternChart = null

const generateTrafficData = () => {
  const hours = []
  const accesses = []
  for (let i = 0; i < 24; i++) {
    hours.push(`${i}:00`)
    let baseAccess = 30
    if (i >= 8 && i <= 10) baseAccess = 120
    else if (i >= 12 && i <= 14) baseAccess = 80
    else if (i >= 17 && i <= 19) baseAccess = 150
    else if (i >= 22 || i <= 6) baseAccess = 15
    accesses.push(Math.floor(baseAccess + Math.random() * 30))
  }
  return { hours, accesses }
}

let trafficData = generateTrafficData()
const patternData = {
  methods: ['RFID Card', 'Biometric', 'Mobile App', 'Keypad PIN', 'Intercom'],
  data: [68, 17, 10, 4, 1]
}

const getTrafficOption = () => {
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15,25,45,0.9)',
      borderColor: '#3b82f6',
      textStyle: { color: '#e2e8f0' },
      formatter: '{b}<br/>Access Count: {c}'
    },
    grid: { left: '10%', right: '10%', bottom: '0%', top: '20%', containLabel: true },
    xAxis: {
      type: 'category',
      data: trafficData.hours,
      axisLabel: { color: '#94a3b8', fontSize: 10, rotate: 45, interval: 5 },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    yAxis: {
      type: 'value',
      name: 'Access Count',
      nameTextStyle: { color: '#64748b', fontSize: 11 },
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } }
    },
    series: [
      {
        name: 'Access Events',
        type: 'bar',
        data: trafficData.accesses,
        itemStyle: {
          borderRadius: [6, 6, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#3b82f6' },
            { offset: 1, color: '#3b82f660' }
          ])
        },
        barWidth: '50%',
        label: {
          show: false
        }
      }
    ]
  }
}

const getPatternOption = () => {
  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec489a']
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15,25,45,0.9)',
      borderColor: '#3b82f6',
      textStyle: { color: '#e2e8f0' },
      formatter: '{b}<br/>Count: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      textStyle: { color: '#94a3b8', fontSize: 11 },
      itemWidth: 12,
      itemHeight: 12
    },
    series: [
      {
        name: 'Access Methods',
        type: 'pie',
        radius: ['40%', '65%'],
        center: ['65%', '55%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: 'rgba(15,25,45,0.8)',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {d}%',
          color: '#e2e8f0',
          fontSize: 10
        },
        emphasis: {
          label: { show: true, fontSize: 12, fontWeight: 'bold' }
        },
        data: patternData.methods.map((name, idx) => ({
          name,
          value: patternData.data[idx],
          itemStyle: { color: colors[idx % colors.length] }
        }))
      }
    ]
  }
}

const disposeCharts = () => {
  if (trafficChart) {
    trafficChart.dispose()
    trafficChart = null
  }
  if (patternChart) {
    patternChart.dispose()
    patternChart = null
  }
}

const resizeCharts = () => {
  if (trafficChart) {
    trafficChart.resize()
  }
  if (patternChart) {
    patternChart.resize()
  }
}

const initCharts = async () => {
  await nextTick()
  for (let attempt = 0; attempt < 5; attempt++) {
    await new Promise(resolve => setTimeout(resolve, 150))
    const trafficDom = trafficChartRef.value
    const patternDom = patternChartRef.value
    if (!trafficDom || !patternDom) {
      continue
    }
    if (trafficDom.clientWidth === 0 || trafficDom.clientHeight === 0) {
      continue
    }
    disposeCharts()
    try {
      trafficChart = echarts.init(trafficDom)
      patternChart = echarts.init(patternDom)
      trafficChart.setOption(getTrafficOption())
      patternChart.setOption(getPatternOption())

      // 监听图表容器大小变化
      window.addEventListener('resize', resizeCharts)
      document.addEventListener('fullscreenchange', () => {
        setTimeout(resizeCharts, 200)
      })

      return
    } catch (e) {
      console.error('[initCharts] Error during init:', e)
    }
  }
  console.error('[initCharts] Failed after 5 attempts')
}

const handleResize = () => {
  resizeCharts()
}

let fullscreenTimer = null
const onFullscreenChange = () => {
  clearTimeout(fullscreenTimer)
  fullscreenTimer = setTimeout(() => {
    resizeCharts()
  }, 300)
}

// ==================== Live Update ====================
let updateTimer = null

const updateAllData = () => {
  onlineDoors.value = Math.floor(150 + Math.random() * 10)
  offlineDoors.value = totalDoors.value - onlineDoors.value
  todayAccesses.value += Math.floor(Math.random() * 8)
  deniedAttempts.value += Math.random() > 0.7 ? 1 : 0

  // 修复：onlinePercent 保留一位小数
  doorZones.value = doorZones.value.map(zone => {
    let newPercent = zone.onlinePercent + (Math.random() - 0.5) * 3
    newPercent = Math.min(100, Math.max(90, newPercent))
    // 保留一位小数
    newPercent = Math.round(newPercent * 10) / 10
    return {
      ...zone,
      onlinePercent: newPercent,
      onlineCount: Math.floor(zone.totalCount * (Math.random() > 0.9 ? 0.95 : 1))
    }
  })

  const totalToday = todayAccesses.value
  accessMethods.value.forEach(method => {
    const randomDelta = Math.floor(Math.random() * 5)
    method.count += randomDelta
  })
  const newTotal = accessMethods.value.reduce((sum, m) => sum + m.count, 0)
  accessMethods.value.forEach(method => {
    // 百分比保留一位小数
    method.percent = Math.round((method.count / newTotal) * 1000) / 10
  })

  zoneActivity.value = zoneActivity.value.map(zone => ({
    ...zone,
    accessCount: zone.accessCount + Math.floor(Math.random() * 10),
    change: Math.floor(Math.random() * 15) - 5,
    trend: Math.random() > 0.5 ? 'up' : 'down'
  }))

  currentlyInside.value = Math.floor(550 + Math.random() * 150)
  visitorCount.value = Math.floor(70 + Math.random() * 40)

  if (Math.random() > 0.6) {
    const eventTypes = ['granted', 'denied', 'alert']
    const eventType = eventTypes[Math.floor(Math.random() * eventTypes.length)]
    const users = ['James Lee', 'Anna Zhang', 'David Koh']
    const doors = ['Main Lobby', 'Office Floor', 'Parking']
    const methods = ['RFID Card', 'Biometric', 'Mobile App']

    recentEvents.value.unshift({
      id: Date.now(),
      type: eventType,
      user: eventType === 'denied' ? 'Unknown' : users[Math.floor(Math.random() * users.length)],
      door: doors[Math.floor(Math.random() * doors.length)],
      method: eventType === 'alert' ? 'Alarm' : methods[Math.floor(Math.random() * methods.length)],
      time: 'Just now'
    })
    if (recentEvents.value.length > 10) recentEvents.value.pop()

    recentEvents.value.forEach((event, idx) => {
      if (idx > 0 && event.time !== 'Just now') {
        const minutes = (parseInt(event.time) || 1) + 1
        event.time = `${minutes} min ago`
      }
    })
  }

  systemHealth.value = systemHealth.value.map(item => ({
    ...item,
    status: Math.random() > 0.9 ? 'warning' : 'normal',
    statusText: Math.random() > 0.9 ? (item.status === 'warning' ? 'Check' : 'Online') : item.statusText
  }))

  if (Math.random() > 0.85) {
    const alertPool = [
      { icon: '🚪', title: 'Door Ajar Detected', desc: 'Fire Exit door left open', severity: 'Medium' },
      { icon: '🔑', title: 'Repeated Access Denied', desc: 'Multiple failed attempts detected', severity: 'High' },
      { icon: '📹', title: 'Camera Offline', desc: 'Security camera disconnected', severity: 'Low' }
    ]
    const newAlert = alertPool[Math.floor(Math.random() * alertPool.length)]
    securityAlerts.value.unshift({
      ...newAlert,
      time: 'Just now'
    })
    if (securityAlerts.value.length > 5) securityAlerts.value.pop()
  }

  const newHourValue = Math.floor(30 + Math.random() * 150)
  trafficData.accesses.push(newHourValue)
  trafficData.accesses.shift()

  if (trafficChart) {
    trafficChart.setOption({
      series: [{ data: trafficData.accesses }]
    })
  }

  if (patternChart) {
    const newTotalMethods = accessMethods.value.reduce((sum, m) => sum + m.count, 0)
    const newPercentData = accessMethods.value.map(m =>
        Math.round(((m.count / newTotalMethods) * 1000)) / 10
    )
    patternChart.setOption({
      series: [{
        data: patternData.methods.map((name, idx) => ({
          name,
          value: newPercentData[idx]
        }))
      }]
    })
  }
}

const viewAllEvents = () => {
  console.log('View all events clicked')
}

let routeWatch = null

const isMobile = ref(false)
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

// 添加 ResizeObserver 来监听图表容器尺寸变化
let resizeObserver = null

const setupResizeObserver = () => {
  if (trafficChartRef.value && patternChartRef.value) {
    resizeObserver = new ResizeObserver(() => {
      resizeCharts()
    })
    resizeObserver.observe(trafficChartRef.value)
    resizeObserver.observe(patternChartRef.value)
  }
}

onMounted(async () => {
  checkMobile()
  updateTime()
  clockTimer = setInterval(updateTime, 1000)

  await preloadAssets()
  await initCharts()
  setupResizeObserver()

  if (trafficChart && patternChart) {
    updateTimer = setInterval(updateAllData, 5000)
  }

  window.addEventListener('resize', handleResize)
  document.addEventListener('fullscreenchange', onFullscreenChange)

  routeWatch = watch(() => route.fullPath, async () => {
    await initCharts()
    if (trafficChart && patternChart && !updateTimer) {
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
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
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

/* Main Access Page Styles */
.access-page {
  height: 100%;
  background: radial-gradient(circle at 10% 20%, #0a1620, #03060c);
  padding: 24px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  animation: fadeIn 0.5s ease-out;
  overflow: hidden;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
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
  overflow: hidden;
}
.three-columns {
  flex: 1;
  display: flex;
  gap: 20px;
  align-items: stretch;
  min-height: 0;
  overflow: hidden;
}

.col-left, .col-right {
  width: 300px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
  min-height: 0;
}
/* 隐藏滚动条但保留滚动功能 */
.col-left, .col-right {
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.col-left::-webkit-scrollbar,
.col-right::-webkit-scrollbar {
  width: 0;
  background: transparent;
  display: none;
}
.col-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 0;
  overflow: hidden;
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
  flex-shrink: 0;
}
.card-img img {
  width: 100%;
  display: block;
  height: auto;
  border-radius: 10px;
}

.card-header {
  font-weight: 600;
  font-size: 16px;
  color: #e2e8f0;
  border-left: 4px solid #3b82f6;
  padding-left: 10px;
}
.card-footer {
  margin-top: 12px;
  text-align: center;
  border-top: 1px solid rgba(148, 163, 184, 0.2);
  padding-top: 10px;
}

/* Key Metrics */
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
.metric-row .metric-icon { font-size: 24px; width: 36px; opacity: 0.9; }
.metric-row .metric-label { flex: 1; font-size: 14px; color: #94a3b8; padding-left: 12px; letter-spacing: 0.3px; font-weight: bold; }
.metric-row .metric-value { font-size: 18px; font-weight: 600; color: #facc15; text-align: right; font-family: monospace; }

/* Mode List */
.mode-list { display: flex; flex-direction: column; gap: 12px; }
.mode-row { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #cbd5e1; }
.mode-name { width: 80px; flex-shrink: 0; font-weight: bold; }
.mode-bar-bg { flex: 1; height: 6px; background: rgba(148, 163, 184, 0.15); border-radius: 3px; overflow: hidden; }
.mode-bar-fill { height: 100%; border-radius: 3px; transition: width 0.5s; }
.mode-value { width: 35px; text-align: right; color: #facc15; }
.mode-power { width: 55px; text-align: right; color: #94a3b8; font-weight: bold; }

/* System Health */
.health-list { display: flex; flex-direction: column; gap: 10px; }
.health-row { display: flex; align-items: center; gap: 10px; font-size: 12px; }
.health-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.health-dot.normal { background: #34d399; box-shadow: 0 0 6px #34d399; }
.health-dot.warning { background: #fbbf24; box-shadow: 0 0 6px #fbbf24; }
.health-dot.critical { background: #ef4444; box-shadow: 0 0 6px #ef4444; }
.health-name { flex: 1; color: #cbd5e1; }
.health-status { font-weight: 600; text-transform: uppercase; }
.health-status.normal { color: #34d399; }
.health-status.warning { color: #fbbf24; }
.health-status.critical { color: #ef4444; }

/* Events List */
.events-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 280px;
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.events-list::-webkit-scrollbar {
  display: none;
}
.event-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 10px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
  transition: all 0.2s;
}
.event-item.granted { border-left: 3px solid #10b981; }
.event-item.denied { border-left: 3px solid #ef4444; }
.event-item.alert { border-left: 3px solid #f59e0b; }
.event-icon { font-size: 18px; flex-shrink: 0; }
.event-details { flex: 1; }
.event-title { font-size: 13px; font-weight: 600; color: #e2e8f0; }
.event-meta { font-size: 10px; color: #94a3b8; margin-top: 2px; }
.event-status {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 20px;
  flex-shrink: 0;
}
.event-status.granted { background: rgba(16, 185, 129, 0.15); color: #34d399; }
.event-status.denied { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
.event-status.alert { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }

/* KPI rows */
.kpi-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; font-size: 13px; color: #cbd5e6; }
.kpi-row span { max-width: 100px; text-align: left;width: 200px }
.kpi-row strong { font-size: 16px; color: #facc15; text-align: center; }
.trend { font-size: 11px; margin-left: 8px; min-width: 65px; text-align: right;display: flex;justify-content: center; }
.trend.up { color: #34d399; }
.trend.down { color: #ef4444; }
.trend.stable { color: #fbbf24; }

/* Center Charts */
.cart-view {
  width: 100%;
  flex: 1;
  display: flex;
  background: transparent;
  gap: 20px;
  min-height: 0;
  overflow: hidden;
}
.chart-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}
.chart-card .card-header {
  flex-shrink: 0;
}
.chart-box {
  flex: 1;
  width: 100%;
  min-height: 0;
  overflow: hidden;
}

/* Tips List */
.tips-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 220px;
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.tips-list::-webkit-scrollbar {
  display: none;
}
.tip-item {
  display: flex;
  gap: 10px;
  padding: 8px 10px;
  background: rgba(59,130,246,0.08);
  border-radius: 8px;
  border-left: 3px solid #f59e0b;
}
.tip-icon { font-size: 18px; flex-shrink: 0; margin-top: 2px; }
.tip-content { flex: 1; }
.tip-title { font-size: 12px; font-weight: 600; color: #e2e8f0; margin-bottom: 2px; }
.tip-desc { font-size: 11px; color: #94a3b8; line-height: 1.4; margin-bottom: 2px; }
.tip-saving { font-size: 10px; color: #f59e0b; font-weight: 600; }

/* ========== 移动端适配 ========== */
@media (max-width: 768px) {
  .access-page {
    padding: 16px;
    overflow-y: auto;
  }
  .title-row {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
    margin-bottom: 10px;
    flex-shrink: 0;
  }
  .page-title {
    font-size: 26px;
    text-align: center;
  }
  .live-time {
    position: static;
    text-align: center;
    width: fit-content;
    margin: 0 auto;
    font-size: 12px;
    padding: 4px 12px;
  }
  .three-columns {
    flex-direction: column;
    gap: 16px;
    overflow: visible;
  }
  .col-left, .col-right {
    width: 100%;
    overflow-y: visible;
    gap: 16px;
  }
  .col-center {
    gap: 16px;
  }
  .glass-card, .card-img {
    border-radius: 16px;
  }
  .glass-card:hover {
    transform: none;
  }
  .cart-view {
    flex-direction: column;
    gap: 16px;
    min-height: 400px;
  }
  .chart-card {
    min-height: 280px;
  }
  .mode-name {
    width: 70px;
    font-size: 11px;
  }
  .mode-value {
    width: 30px;
    font-size: 11px;
  }
  .mode-power {
    width: 50px;
    font-size: 10px;
  }
  .metric-row .metric-icon {
    font-size: 20px;
    width: 28px;
  }
  .metric-row .metric-label {
    font-size: 12px;
    padding-left: 8px;
  }
  .metric-row .metric-value {
    font-size: 16px;
  }
  .event-title {
    font-size: 12px;
  }
  .event-meta {
    font-size: 9px;
  }
}

/* 全局隐藏 Element Plus Card 内部滚动条 */
:deep(.el-card__body) {
  scrollbar-width: none;
  -ms-overflow-style: none;
  overflow: visible !important;
  padding: 16px;
}
:deep(.el-card__body::-webkit-scrollbar) {
  display: none;
}
:deep(.col-left .el-card),
:deep(.col-right .el-card) {
  overflow: visible;
  height: auto;
  flex-shrink: 0;
}
:deep(.chart-card .el-card__body) {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 12px;
}
</style>

<style>
.el-card__header {
  border-bottom: none;
  padding-bottom: 0px;

}
</style>