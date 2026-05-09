<!-- DeviceFAS.vue -->
<template>
  <div v-if="isPageLoaded" class="hvac-page">
    <div class="main-view">
      <div class="three-columns">
        <!-- Left Column: Key Metrics + Detector Status + Recent Alarms + System Health -->
        <div class="col-left">
          <!-- Key Metrics -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📈 Key Metrics</div>
            <div class="metrics-list">
              <div class="metric-row">
                <div class="metric-icon">🔥</div>
                <div class="metric-label">Smoke Detectors</div>
                <div class="metric-value">{{ totalDetectors }}</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">✅</div>
                <div class="metric-label">Online Rate</div>
                <div class="metric-value">{{ onlineRate }}%</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">🧯</div>
                <div class="metric-label">Fire Zones</div>
                <div class="metric-value">{{ fireZones }}</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">💧</div>
                <div class="metric-label">Sprinkler Pressure</div>
                <div class="metric-value">{{ sprinklerPressure }} bar</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">🚨</div>
                <div class="metric-label">Active Alarms</div>
                <div class="metric-value">{{ activeAlarms }}</div>
              </div>
            </div>
          </el-card>

          <!-- Detector Status Distribution -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🔄 Detector Status</div>
            <div class="mode-list">
              <div class="mode-row" v-for="item in detectorStatus" :key="item.name">
                <div class="mode-name">{{ item.name }}</div>
                <div class="mode-bar-bg">
                  <div class="mode-bar-fill" :style="{ width: item.percentage + '%', background: item.color }"></div>
                </div>
                <div class="mode-value">{{ item.percentage }}%</div>
                <div class="mode-power">{{ item.count }}</div>
              </div>
            </div>
          </el-card>

          <!-- Recent Fire Alarms -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🚨 Recent Alarms</div>
            <div class="alert-list">
              <div class="alert-item" v-for="alarm in recentAlarms" :key="alarm.id">
                <div class="alert-header">
                  <span class="alert-tag" :class="alarm.severity">{{ alarm.severity }}</span>
                  <span class="alert-device">{{ alarm.location }}</span>
                </div>
                <div class="alert-msg">{{ alarm.description }}</div>
                <div class="alert-time">{{ alarm.timestamp }}</div>
              </div>
            </div>
          </el-card>

          <!-- System Health Status -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">💚 System Health</div>
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
          <div class="title-row">
            <h1 class="page-title">FAS</h1>
            <span class="live-time">{{ currentTime }}</span>
          </div>
          <div class="card-img">
            <img :src="fasImageUrl" alt="Fire Alarm 3D View" />
          </div>
          <div class="cart-view">
            <!-- Smoke Level Trend -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <div class="card-header">📊 Smoke Level Trend (Hourly)</div>
              <div ref="smokeTrendChartRef" class="chart-box"></div>
            </el-card>
            <!-- Zone Temperature Monitor -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <div class="card-header">🌡️ Zone Temperature Monitor (Last 10 min)</div>
              <div ref="tempMonitorChartRef" class="chart-box"></div>
            </el-card>
          </div>
        </div>

        <!-- Right Column: KPIs + Zone Conditions + Control Status + Tips -->
        <div class="col-right">
          <!-- Fire Safety KPIs -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📊 Fire Safety KPIs</div>
            <div class="kpi-row">
              <span>Sprinkler Pressure</span>
              <strong>{{ sprinklerPressure }} bar</strong>
              <span class="trend stable">Target > 4.5</span>
            </div>
            <div class="kpi-row">
              <span>Evacuation Routes</span>
              <strong>{{ evacuationRoutes }}</strong>
              <span class="trend up">All Clear</span>
            </div>
            <div class="kpi-row">
              <span>Fire Dampers</span>
              <strong>{{ fireDampers }}</strong>
              <span class="trend stable">Operational</span>
            </div>
            <div class="kpi-row">
              <span>System Uptime</span>
              <strong>{{ systemUptime }}%</strong>
              <span class="trend up">99.95% SLA</span>
            </div>
          </el-card>

          <!-- Zone Conditions Gauges -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🌡️ Zone Conditions</div>
            <div class="gauges-grid">
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="lobbyTempPercent" :color="tempColorLow" :width="90" :stroke-width="4">
                  <template #default>
                    <span class="percentage-label">{{ lobbyTemp }} °C</span>
                  </template>
                </el-progress>
                <div class="gauge-label">Lobby Temp</div>
              </div>
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="kitchenTempPercent" :color="tempColorHigh" :width="90" :stroke-width="4">
                  <template #default>
                    <span class="percentage-label">{{ kitchenTemp }} °C</span>
                  </template>
                </el-progress>
                <div class="gauge-label">Kitchen Temp</div>
              </div>
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="electricalRoomSmokePercent" :color="smokeColor" :width="90" :stroke-width="4">
                  <template #default>
                    <span class="percentage-label">{{ electricalRoomSmoke }}%</span>
                  </template>
                </el-progress>
                <div class="gauge-label">Elec. Room Smoke</div>
              </div>
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="coLevelPercent" :color="coColor" :width="90" :stroke-width="4">
                  <template #default>
                    <span class="percentage-label">{{ coLevel }} ppm</span>
                  </template>
                </el-progress>
                <div class="gauge-label">CO Level</div>
              </div>
            </div>
          </el-card>

          <!-- Fire Equipment Status -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🎯 Equipment Status</div>
            <div class="setpoint-list">
              <div class="setpoint-row" v-for="item in equipmentStatus" :key="item.label">
                <div class="sp-label">{{ item.label }}</div>
                <div class="sp-values">
                  <span class="sp-set">Pressure: {{ item.pressure }}</span>
                  <span class="sp-actual">Status: {{ item.status }}</span>
                </div>
                <div class="sp-deviation" :class="item.alarmClass">
                  {{ item.alarm }}
                </div>
              </div>
            </div>
          </el-card>

          <!-- Fire Safety Tips -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">💡 Fire Safety Advisory</div>
            <div class="tips-list">
              <div class="tip-item" v-for="(tip, idx) in fireTips" :key="idx">
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
        <div class="loading-tip">Initializing Fire Alarm System</div>
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
const fasImageUrl = ref('')

// Loading messages sequence
const loadingMessages = [
  'Preparing assets...',
  'Loading background...',
  'Loading fire alarm model...',
  'Initializing modules...',
  'Connecting to detectors...',
  'Starting dashboard...',
  'Almost ready...'
]

// ==================== Preload Assets ====================
const preloadFASImage = () => {
  return new Promise((resolve) => {
    const img = new Image()
    const imageUrl = 'https://aegisnx.com/wp-content/uploads/2026/05/1778229198321.png'

    img.onload = () => {
      fasImageUrl.value = imageUrl
      resolve()
    }

    img.onerror = () => {
      console.warn('FAS image load failed, using fallback')
      fasImageUrl.value = imageUrl
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

  await preloadFASImage()

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
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  const milliseconds = String(now.getMilliseconds()).padStart(3, '0')
  currentTime.value = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}.${milliseconds}`
}

let clockTimer = null

// ==================== Core Fire Safety Data ====================
// Key metrics
const totalDetectors = ref(512)
const onlineRate = ref(99.2)
const fireZones = ref(24)
const sprinklerPressure = ref(5.2)
const activeAlarms = ref(1)

// Fire Safety KPIs
const evacuationRoutes = ref(8)
const fireDampers = ref(36)
const systemUptime = ref(99.98)

// Zone conditions
const lobbyTemp = ref(23.5)
const kitchenTemp = ref(31.2)
const electricalRoomSmoke = ref(2.1)
const coLevel = ref(12)

const lobbyTempPercent = ref(35)
const kitchenTempPercent = ref(52)
const electricalRoomSmokePercent = ref(14)
const coLevelPercent = ref(12)

// Gauge colors
const tempColorLow = [
  { color: '#10b981', percentage: 40 },
  { color: '#f59e0b', percentage: 60 },
  { color: '#ef4444', percentage: 100 }
]
const tempColorHigh = [
  { color: '#f59e0b', percentage: 40 },
  { color: '#ef4444', percentage: 70 },
  { color: '#dc2626', percentage: 100 }
]
const smokeColor = [
  { color: '#10b981', percentage: 15 },
  { color: '#f59e0b', percentage: 30 },
  { color: '#ef4444', percentage: 100 }
]
const coColor = [
  { color: '#10b981', percentage: 20 },
  { color: '#f59e0b', percentage: 50 },
  { color: '#ef4444', percentage: 100 }
]

// Detector status distribution
const detectorStatus = ref([
  { name: 'Normal', percentage: 94, count: '481 units', color: '#34d399' },
  { name: 'Maintenance', percentage: 4, count: '21 units', color: '#fbbf24' },
  { name: 'Fault', percentage: 1.5, count: '8 units', color: '#f97316' },
  { name: 'Alarm', percentage: 0.5, count: '2 units', color: '#ef4444' }
])

// Recent fire alarms
const recentAlarms = ref([
  { id: 1, severity: 'Warning', location: 'Kitchen Exhaust Duct', description: 'Temperature threshold exceeded (68°C)', timestamp: '5 min ago' },
  { id: 2, severity: 'Critical', location: 'Electrical Room B1', description: 'Smoke detector activation (3.8% obscuration)', timestamp: '18 min ago' },
  { id: 3, severity: 'Warning', location: 'Parking Level P2', description: 'CO level elevated (45 ppm)', timestamp: '32 min ago' }
])

// System health
const systemHealth = ref([
  { subsystem: 'Smoke Detectors', status: 'normal', statusText: 'Online' },
  { subsystem: 'Sprinkler System', status: 'normal', statusText: 'Pressurized' },
  { subsystem: 'Fire Pumps', status: 'normal', statusText: 'Standby' },
  { subsystem: 'Alarm Panels', status: 'warning', statusText: '1 Offline' },
  { subsystem: 'Emergency Lighting', status: 'normal', statusText: 'Battery OK' }
])

// Equipment status
const equipmentStatus = ref([
  { label: 'Fire Pump #1', pressure: '7.2 bar', status: 'Standby', alarm: 'Normal', alarmClass: 'normal' },
  { label: 'Fire Pump #2', pressure: '7.1 bar', status: 'Standby', alarm: 'Normal', alarmClass: 'normal' },
  { label: 'Jockey Pump', pressure: '5.5 bar', status: 'Running', alarm: 'Alert', alarmClass: 'low' },
  { label: 'Sprinkler Main', pressure: '5.2 bar', status: 'Pressurized', alarm: 'Normal', alarmClass: 'normal' }
])

// Fire tips
const fireTips = ref([
  { icon: '🔥', title: 'Kitchen Hood Inspection', desc: 'Grease buildup detected in exhaust duct, schedule cleaning', priority: 'High Priority' },
])

// ==================== Charts ====================
const smokeTrendChartRef = ref(null)
const tempMonitorChartRef = ref(null)
let smokeTrendChart = null
let tempMonitorChart = null

// 12-hour smoke level history
const smokeHistoryLength = 12
const smokeHistory = ref([])
const smokeHourLabels = ref([])

const initSmokeHistory = () => {
  smokeHistory.value = []
  smokeHourLabels.value = []
  const now = new Date()
  for (let i = smokeHistoryLength - 1; i >= 0; i--) {
    const t = new Date(now - i * 3600000)
    smokeHourLabels.value.push(t.toTimeString().slice(0, 5))
    smokeHistory.value.push({
      'Lobby': 0.5 + Math.random() * 0.5,
      'Kitchen': 1.5 + Math.random() * 2.5,
      'Electrical Room': 2.0 + Math.random() * 1.5
    })
  }
}

// 10-minute zone temperature history
const tempHistoryLength = 10
const tempHistory = ref([])
const tempTimeLabels = ref([])

const initTempHistory = () => {
  const now = new Date()
  tempHistory.value = []
  tempTimeLabels.value = []
  for (let i = tempHistoryLength - 1; i >= 0; i--) {
    const t = new Date(now - i * 60000)
    tempTimeLabels.value.push(t.toTimeString().slice(0, 5))
    tempHistory.value.push({
      'Lobby': 23 + Math.random() * 1.5,
      'Kitchen': 30 + Math.random() * 3,
      'Electrical Room': 27 + Math.random() * 2,
      'Parking': 25 + Math.random() * 2
    })
  }
}

// Smoke level area chart option (hourly)
const getSmokeTrendOption = () => {
  const categories = ['Lobby', 'Kitchen', 'Electrical Room']
  const colors = ['#60a5fa', '#f97316', '#ef4444']

  const seriesData = categories.map((name, i) => ({
    name,
    type: 'line',
    data: smokeHistory.value.map(d => d[name]),
    smooth: true,
    symbol: 'circle',
    symbolSize: 5,
    lineStyle: { width: 2, color: colors[i] },
    itemStyle: { color: colors[i] },
    areaStyle: {
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: colors[i] + '50' },
        { offset: 1, color: colors[i] + '00' }
      ])
    },
    markLine: {
      silent: true,
      lineStyle: { color: colors[i], type: 'dashed', width: 1, opacity: 0.5 },
      data: i === 0 ? [{ yAxis: 1.0, label: { formatter: 'Alert', fontSize: 8, color: colors[i] } }] :
          i === 1 ? [{ yAxis: 3.0, label: { formatter: 'Alert', fontSize: 8, color: colors[i] } }] :
              [{ yAxis: 3.0, label: { formatter: 'Alert', fontSize: 8, color: colors[i] } }]
    }
  }))

  return {
    backgroundColor: 'transparent',
    grid: { left: '3%', right: '4%', bottom: '0%', top: '20%', containLabel: true },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15,25,45,0.9)',
      borderColor: '#3b82f6',
      textStyle: { color: '#e2e8f0' },
      valueFormatter: (value) => value + '%'
    },
    legend: { textStyle: { color: '#94a3b8', fontSize: 9 }, top: 0 },
    xAxis: {
      type: 'category',
      data: smokeHourLabels.value,
      axisLabel: { color: '#94a3b8', fontSize: 9, rotate: 15 },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    yAxis: {
      type: 'value',
      name: 'Obscuration %',
      nameTextStyle: { color: '#64748b', fontSize: 10 },
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } },
      max: 6
    },
    series: seriesData
  }
}

// Zone temperature monitor line chart option
const getTempMonitorOption = () => {
  const categories = ['Lobby', 'Kitchen', 'Electrical Room', 'Parking']
  const colors = ['#60a5fa', '#f97316', '#fbbf24', '#34d399']

  const seriesData = categories.map((name, i) => ({
    name,
    type: 'line',
    data: tempHistory.value.map(d => d[name]),
    smooth: true,
    symbol: 'circle',
    symbolSize: 5,
    lineStyle: { width: 2, color: colors[i] },
    itemStyle: { color: colors[i] },
    areaStyle: {
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: colors[i] + '25' },
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
      valueFormatter: (value) => value + ' °C'
    },
    legend: { textStyle: { color: '#94a3b8', fontSize: 9 }, top: 0 },
    grid: { left: '3%', right: '4%', bottom: '0%', top: '20%', containLabel: true },
    xAxis: {
      type: 'category',
      data: tempTimeLabels.value,
      axisLabel: { color: '#94a3b8', fontSize: 9 },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    yAxis: {
      type: 'value',
      name: '°C',
      nameTextStyle: { color: '#64748b', fontSize: 10 },
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } }
    },
    series: seriesData
  }
}

// ==================== Chart Lifecycle ====================
const disposeCharts = () => {
  if (smokeTrendChart) {
    smokeTrendChart.dispose()
    smokeTrendChart = null
  }
  if (tempMonitorChart) {
    tempMonitorChart.dispose()
    tempMonitorChart = null
  }
}

const initCharts = async () => {
  await nextTick()

  for (let attempt = 0; attempt < 5; attempt++) {
    await new Promise(resolve => setTimeout(resolve, 100))

    const smokeDom = smokeTrendChartRef.value
    const tempDom = tempMonitorChartRef.value

    if (!smokeDom || !tempDom) continue
    if (smokeDom.clientWidth === 0 || smokeDom.clientHeight === 0) continue
    if (tempDom.clientWidth === 0 || tempDom.clientHeight === 0) continue

    disposeCharts()

    try {
      smokeTrendChart = echarts.init(smokeDom)
      tempMonitorChart = echarts.init(tempDom)

      smokeTrendChart.setOption(getSmokeTrendOption())
      tempMonitorChart.setOption(getTempMonitorOption())

      return
    } catch (e) {
      console.error('[initCharts] Error:', e)
    }
  }
}

const handleResize = () => {
  smokeTrendChart?.resize()
  tempMonitorChart?.resize()
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
  totalDetectors.value = 510 + Math.floor(Math.random() * 5)
  onlineRate.value = parseFloat((98.8 + Math.random() * 1.0).toFixed(1))
  sprinklerPressure.value = parseFloat((4.8 + Math.random() * 0.8).toFixed(1))
  activeAlarms.value = Math.floor(Math.random() * 3)

  // Zone conditions
  lobbyTemp.value = parseFloat((23.0 + Math.random() * 1.5).toFixed(1))
  kitchenTemp.value = parseFloat((30.5 + Math.random() * 2.5).toFixed(1))
  electricalRoomSmoke.value = parseFloat((1.5 + Math.random() * 2.0).toFixed(1))
  coLevel.value = Math.floor(10 + Math.random() * 15)

  // Gauge percentages
  lobbyTempPercent.value = Math.round((lobbyTemp.value / 40) * 100)
  kitchenTempPercent.value = Math.round((kitchenTemp.value / 60) * 100)
  electricalRoomSmokePercent.value = Math.round((electricalRoomSmoke.value / 15) * 100)
  coLevelPercent.value = Math.round((coLevel.value / 100) * 100)

  // Detector status
  detectorStatus.value = [
    { name: 'Normal', percentage: 92 + Math.floor(Math.random() * 4), count: (475 + Math.floor(Math.random() * 10)) + ' units', color: '#34d399' },
    { name: 'Maintenance', percentage: 3 + Math.floor(Math.random() * 3), count: (18 + Math.floor(Math.random() * 8)) + ' units', color: '#fbbf24' },
    { name: 'Fault', percentage: 1 + Math.floor(Math.random() * 2), count: (6 + Math.floor(Math.random() * 5)) + ' units', color: '#f97316' },
    { name: 'Alarm', percentage: Math.floor(Math.random() * 2), count: (1 + Math.floor(Math.random() * 2)) + ' units', color: '#ef4444' }
  ]
  // Normalize to 100
  const sum = detectorStatus.value.reduce((a, b) => a + b.percentage, 0)
  detectorStatus.value[0].percentage += (100 - sum)

  // System health
  systemHealth.value = [
    { subsystem: 'Smoke Detectors', status: Math.random() > 0.98 ? 'warning' : 'normal', statusText: Math.random() > 0.98 ? 'Fault' : 'Online' },
    { subsystem: 'Sprinkler System', status: 'normal', statusText: 'Pressurized' },
    { subsystem: 'Fire Pumps', status: 'normal', statusText: 'Standby' },
    { subsystem: 'Alarm Panels', status: Math.random() > 0.88 ? 'warning' : 'normal', statusText: Math.random() > 0.88 ? '1 Offline' : 'Normal' },
    { subsystem: 'Emergency Lighting', status: 'normal', statusText: 'Battery OK' }
  ]

  // Equipment status
  equipmentStatus.value = [
    { label: 'Fire Pump #1', pressure: (7.0 + Math.random() * 0.4).toFixed(1) + ' bar', status: 'Standby', alarm: 'Normal', alarmClass: 'normal' },
    { label: 'Fire Pump #2', pressure: (7.0 + Math.random() * 0.4).toFixed(1) + ' bar', status: 'Standby', alarm: 'Normal', alarmClass: 'normal' },
    { label: 'Jockey Pump', pressure: (5.2 + Math.random() * 0.8).toFixed(1) + ' bar', status: Math.random() > 0.3 ? 'Running' : 'Standby', alarm: Math.random() > 0.3 ? 'Alert' : 'Normal', alarmClass: Math.random() > 0.3 ? 'low' : 'normal' },
    { label: 'Sprinkler Main', pressure: sprinklerPressure.value + ' bar', status: 'Pressurized', alarm: 'Normal', alarmClass: 'normal' }
  ]

  // Tips
  const tipPool = [
    { icon: '🔥', title: 'Kitchen Hood Inspection', desc: 'Grease buildup detected in exhaust duct, schedule cleaning', priority: 'High Priority' },
    { icon: '🧯', title: 'Extinguisher Check', desc: '3 extinguishers due for annual inspection this week', priority: 'Medium Priority' },
    { icon: '🚪', title: 'Fire Door Audit', desc: 'Fire door on 3F reported not fully closing', priority: 'High Priority' },
    { icon: '📋', title: 'Evacuation Drill', desc: 'Quarterly drill scheduled for next Tuesday 10:00', priority: 'Low Priority' }
  ]
  fireTips.value = tipPool.sort(() => Math.random() - 0.5).slice(0, 1)

  // Update charts
  if (smokeTrendChart && tempMonitorChart) {
    // Update smoke history
    const now = new Date()
    smokeHourLabels.value.push(now.toTimeString().slice(0, 5))
    if (smokeHourLabels.value.length > smokeHistoryLength) smokeHourLabels.value.shift()

    smokeHistory.value.push({
      'Lobby': 0.5 + Math.random() * 0.5,
      'Kitchen': 1.5 + Math.random() * 2.5,
      'Electrical Room': 2.0 + Math.random() * 1.5
    })
    if (smokeHistory.value.length > smokeHistoryLength) smokeHistory.value.shift()

    smokeTrendChart.setOption({
      xAxis: { data: smokeHourLabels.value },
      series: ['Lobby', 'Kitchen', 'Electrical Room'].map(name => ({
        data: smokeHistory.value.map(d => d[name])
      }))
    })

    // Update temperature history
    tempTimeLabels.value.push(now.toTimeString().slice(0, 5))
    if (tempTimeLabels.value.length > tempHistoryLength) tempTimeLabels.value.shift()

    tempHistory.value.push({
      'Lobby': 23 + Math.random() * 1.5,
      'Kitchen': 30 + Math.random() * 3,
      'Electrical Room': 27 + Math.random() * 2,
      'Parking': 25 + Math.random() * 2
    })
    if (tempHistory.value.length > tempHistoryLength) tempHistory.value.shift()

    tempMonitorChart.setOption({
      xAxis: { data: tempTimeLabels.value },
      series: ['Lobby', 'Kitchen', 'Electrical Room', 'Parking'].map(name => ({
        data: tempHistory.value.map(d => d[name])
      }))
    })
  }
}

let routeWatch = null

onMounted(async () => {
  updateTime()
  clockTimer = setInterval(updateTime, 1000)

  await preloadAssets()

  initSmokeHistory()
  initTempHistory()
  await initCharts()

  if (smokeTrendChart && tempMonitorChart) {
    updateTimer = setInterval(updateAllData, 5000)
  }

  window.addEventListener('resize', handleResize)
  document.addEventListener('fullscreenchange', onFullscreenChange)

  routeWatch = watch(() => route.fullPath, async () => {
    initSmokeHistory()
    initTempHistory()
    await initCharts()
    if (smokeTrendChart && tempMonitorChart && !updateTimer) {
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

/* Main FAS Page Styles */
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
  width: 50%;
  text-align: left;
}
.kpi-row strong {
  font-size: 16px;
  color: #facc15;
  text-align: center;
}
.trend {
  width: 20%;
  font-size: 11px;
  margin-left: 8px;
  text-align: right;
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
}
.sp-values {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
  margin-right: 8px;
}
.sp-set {
  font-size: 10px;
  color: #cbd5e1;
}
.sp-actual {
  font-weight: 600;
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