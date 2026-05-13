<!-- DeviceLighting.vue -->
<template>
  <div v-if="isPageLoaded" class="hvac-page">
    <div class="main-view">
      <div class="three-columns">
        <!-- Left Column: Key Metrics + Lighting Mode + Recent Events + System Health -->
        <div class="col-left">
          <div class="title-row" v-if="isMobile">
            <h1 class="page-title">Lighting Control</h1>
            <span class="live-time">{{ currentTime }}</span>
          </div>
          <div class="card-img" v-if="isMobile">
            <img :src="lightingImageUrl" alt="Lighting 3D View" />
          </div>
          <!-- Key Metrics -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📈 Key Metrics</div>
            <div class="metrics-list">
              <div class="metric-row">
                <div class="metric-icon">💡</div>
                <div class="metric-label">Total Luminaires</div>
                <div class="metric-value">{{ totalLuminaires }}</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">✅</div>
                <div class="metric-label">Online Rate</div>
                <div class="metric-value">{{ onlineRate }}%</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">⚡</div>
                <div class="metric-label">Active Power</div>
                <div class="metric-value">{{ activePower }} kW</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">🌿</div>
                <div class="metric-label">Energy Saved Today</div>
                <div class="metric-value">{{ energySaved }} kWh</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">🔆</div>
                <div class="metric-label">Avg. Dim Level</div>
                <div class="metric-value">{{ avgDimLevel }}%</div>
              </div>
            </div>
          </el-card>

          <!-- Lighting Mode Distribution -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🔄 Lighting Mode</div>
            <div class="mode-list">
              <div class="mode-row" v-for="item in lightingModes" :key="item.name">
                <div class="mode-name">{{ item.name }}</div>
                <div class="mode-bar-bg">
                  <div class="mode-bar-fill" :style="{ width: item.loadPercent + '%', background: item.color }"></div>
                </div>
                <div class="mode-value">{{ item.loadPercent }}%</div>
                <div class="mode-power">{{ item.power }}kW</div>
              </div>
            </div>
          </el-card>

          <!-- Recent Events -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📋 Recent Events</div>
            <div class="alert-list">
              <div class="alert-item" v-for="event in recentEvents" :key="event.id">
                <div class="alert-header">
                  <span class="alert-tag" :class="event.severity">{{ event.severity }}</span>
                  <span class="alert-device">{{ event.zone }}</span>
                </div>
                <div class="alert-msg">{{ event.description }}</div>
                <div class="alert-time">{{ event.timestamp }}</div>
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
          <div class="title-row" v-if="!isMobile">
            <h1 class="page-title">Lighting Control</h1>
            <span class="live-time" v-if="isFullscreen">{{ currentTime }}</span>
          </div>
          <div class="card-img" v-if="!isMobile">
            <img :src="lightingImageUrl" alt="Lighting 3D View" />
          </div>
          <div class="cart-view">
            <!-- Zone Illuminance Chart -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <div class="card-header">📊 Zone Illuminance (Lux)</div>
              <div ref="illuminanceChartRef" class="chart-box"></div>
            </el-card>
            <!-- Real-time Power Consumption -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <div class="card-header">⚡ Power Consumption Trend (Last 10 min)</div>
              <div ref="powerChartRef" class="chart-box"></div>
            </el-card>
          </div>
        </div>

        <!-- Right Column: KPIs + Environmental + Dimming Status + Tips -->
        <div class="col-right">
          <!-- Lighting KPIs -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📊 Lighting KPIs</div>
            <div class="kpi-row">
              <span class="kpi-row-left">Daylight Harvesting</span>
              <strong>{{ daylightHarvesting }}%</strong>
              <span class="trend up">Active</span>
            </div>
            <div class="kpi-row">
              <span class="kpi-row-left">Occupancy Savings</span>
              <strong>{{ occupancySavings }}%</strong>
              <span class="trend up">↑3.2%</span>
            </div>
            <div class="kpi-row">
              <span class="kpi-row-left">Scheduled Zones</span>
              <strong>{{ scheduledZones }}</strong>
              <span class="trend stable">On Time</span>
            </div>
            <div class="kpi-row">
              <span class="kpi-row-left">System Efficiency</span>
              <strong>{{ systemEfficiency }}%</strong>
              <span class="trend up">Target > 85%</span>
            </div>
          </el-card>

          <!-- Zone Light Level Gauges -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🌞 Zone Light Levels</div>
            <div class="gauges-grid">
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="officeLuxPercent" :color="luxColor" :width="90" :stroke-width="4">
                  <template #default>
                    <span class="percentage-label">{{ officeLux }} lux</span>
                  </template>
                </el-progress>
                <div class="gauge-label">Office Area</div>
              </div>
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="lobbyLuxPercent" :color="luxColor" :width="90" :stroke-width="4">
                  <template #default>
                    <span class="percentage-label">{{ lobbyLux }} lux</span>
                  </template>
                </el-progress>
                <div class="gauge-label">Main Lobby</div>
              </div>
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="parkingLuxPercent" :color="luxColorLow" :width="90" :stroke-width="4">
                  <template #default>
                    <span class="percentage-label">{{ parkingLux }} lux</span>
                  </template>
                </el-progress>
                <div class="gauge-label">Parking</div>
              </div>
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="corridorLuxPercent" :color="luxColorLow" :width="90" :stroke-width="4">
                  <template #default>
                    <span class="percentage-label">{{ corridorLux }} lux</span>
                  </template>
                </el-progress>
                <div class="gauge-label">Corridor</div>
              </div>
            </div>
          </el-card>

          <!-- Dimming Zone Status -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🎯 Dimming Zone Status</div>
            <div class="setpoint-list">
              <div class="setpoint-row" v-for="item in dimmingZones" :key="item.label">
                <div class="sp-label">{{ item.label }}</div>
                <div class="sp-values">
                  <span class="sp-set">Target: {{ item.target }}%</span>
                  <span class="sp-actual">Actual: {{ item.actual }}%</span>
                </div>
                <div class="sp-deviation" :class="item.status">
                  {{ item.deviation }}
                </div>
              </div>
            </div>
          </el-card>

          <!-- Energy Saving Tips -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">💡 Energy Saving Tips</div>
            <div class="tips-list">
              <div class="tip-item" v-for="(tip, idx) in lightingTips" :key="idx">
                <div class="tip-icon">{{ tip.icon }}</div>
                <div class="tip-content">
                  <div class="tip-title">{{ tip.title }}</div>
                  <div class="tip-desc">{{ tip.desc }}</div>
                  <div class="tip-saving">{{ tip.saving }}</div>
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
        <div class="loading-tip">Initializing Lighting Control System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, watch,computed } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { useCounterStore } from '@/stores/counter'
import { getCurrentInstance } from 'vue'
const getStore = () => {
  const instance = getCurrentInstance()
  if (!instance) {
    throw new Error('useStore() must be called within a setup function')
  }
  // 尝试获取根组件上的 pinia 实例
  const pinia = instance.appContext.config.globalProperties.$pinia
  if (!pinia) {
    throw new Error('Pinia instance not found. Did you forget to call app.use(pinia)?')
  }
  return useCounterStore(pinia) // 手动传入 pinia 实例
}
const counterStore = getStore()
const isFullscreen = computed(() => counterStore.isFullscreen)

const route = useRoute()

// ==================== Loading State ====================
const isPageLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing assets...')
const lightingImageUrl = ref('')

// Loading messages sequence
const loadingMessages = [
  'Preparing assets...',
  'Loading background...',
  'Loading lighting model...',
  'Initializing modules...',
  'Connecting to DALI buses...',
  'Starting dashboard...',
  'Almost ready...'
]

// ==================== Preload Assets ====================
const preloadLightingImage = () => {
  return new Promise((resolve) => {
    const img = new Image()
    const imageUrl = 'https://aegisnx.com/wp-content/uploads/2026/05/1778229518177.png'

    img.onload = () => {
      lightingImageUrl.value = imageUrl
      resolve()
    }

    img.onerror = () => {
      console.warn('Lighting image load failed, using fallback')
      lightingImageUrl.value = imageUrl
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

  await preloadLightingImage()

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

// ==================== Core Lighting Data ====================
// Key metrics
const totalLuminaires = ref(1248)
const onlineRate = ref(97.8)
const activePower = ref(86.5)
const energySaved = ref(342)
const avgDimLevel = ref(68)

// Lighting KPIs
const daylightHarvesting = ref(42)
const occupancySavings = ref(28)
const scheduledZones = ref(18)
const systemEfficiency = ref(89.5)

// Zone light levels
const officeLux = ref(520)
const lobbyLux = ref(380)
const parkingLux = ref(120)
const corridorLux = ref(180)

const officeLuxPercent = ref(65)
const lobbyLuxPercent = ref(48)
const parkingLuxPercent = ref(15)
const corridorLuxPercent = ref(23)

// Gauge colors
const luxColor = [
  { color: '#10b981', percentage: 40 },
  { color: '#60a5fa', percentage: 70 },
  { color: '#facc15', percentage: 100 }
]
const luxColorLow = [
  { color: '#10b981', percentage: 20 },
  { color: '#60a5fa', percentage: 40 },
  { color: '#facc15', percentage: 100 }
]

// Lighting modes
const lightingModes = ref([
  { name: 'Daylighting', loadPercent: 42, power: 36.3, color: '#facc15' },
  { name: 'Scheduled', loadPercent: 35, power: 30.3, color: '#3b82f6' },
  { name: 'Occupancy', loadPercent: 18, power: 15.6, color: '#34d399' },
  { name: 'Manual', loadPercent: 5, power: 4.3, color: '#f97316' }
])

// Recent events
const recentEvents = ref([
  { id: 1, severity: 'Info', zone: 'Office 3F East', description: 'Schedule activated - Evening dimming to 30%', timestamp: '2 min ago' },
  { id: 2, severity: 'Warning', zone: 'Parking B1', description: 'Motion sensor #P12 no response for 15 min', timestamp: '8 min ago' },
  { id: 3, severity: 'Info', zone: 'Main Lobby', description: 'Daylight harvesting increased to 65%', timestamp: '15 min ago' }
])

// System health
const systemHealth = ref([
  { subsystem: 'DALI Bus A', status: 'normal', statusText: 'Online' },
  { subsystem: 'DALI Bus B', status: 'normal', statusText: 'Online' },
  { subsystem: 'Motion Sensors', status: 'warning', statusText: '1 Fault' },
  { subsystem: 'Light Sensors', status: 'normal', statusText: 'Normal' },
  { subsystem: 'Control Panel', status: 'normal', statusText: 'Online' }
])

// Dimming zones
const dimmingZones = ref([
  { label: 'Office 3F East', target: '60', actual: '58', deviation: '-2% ✓', status: 'normal' },
  { label: 'Office 3F West', target: '70', actual: '72', deviation: '+2% ⚠', status: 'low' },
  { label: 'Main Lobby', target: '45', actual: '42', deviation: '-3% ✓', status: 'normal' },
  { label: 'Parking B1', target: '30', actual: '28', deviation: '-2% ✓', status: 'low' }
])

// Lighting tips
const lightingTips = ref([
  { icon: '🌞', title: 'Optimize Daylight Zones', desc: 'Raise blinds in office 3F East to increase daylight harvesting', saving: '~12% energy savings' },
])

// ==================== Charts ====================
const illuminanceChartRef = ref(null)
const powerChartRef = ref(null)
let illuminanceChart = null
let powerChart = null

// 12-hour illuminance history
const illuminanceHistoryLength = 12
const illuminanceHistory = ref([])
const illuminanceHourLabels = ref([])

const initIlluminanceHistory = () => {
  illuminanceHistory.value = []
  illuminanceHourLabels.value = []
  const now = new Date()
  for (let i = illuminanceHistoryLength - 1; i >= 0; i--) {
    const t = new Date(now - i * 3600000)
    illuminanceHourLabels.value.push(t.toTimeString().slice(0, 5))
    illuminanceHistory.value.push({
      'Office Area': 450 + Math.random() * 100,
      'Main Lobby': 320 + Math.random() * 80,
      'Parking': 100 + Math.random() * 40,
      'Corridor': 150 + Math.random() * 50
    })
  }
}

// 10-minute power history
const powerHistoryLength = 10
const powerHistory = ref([])
const powerTimeLabels = ref([])

const initPowerHistory = () => {
  const now = new Date()
  powerHistory.value = []
  powerTimeLabels.value = []
  for (let i = powerHistoryLength - 1; i >= 0; i--) {
    const t = new Date(now - i * 60000)
    powerTimeLabels.value.push(t.toTimeString().slice(0, 5))
    powerHistory.value.push({
      'Office Lighting': 35 + Math.random() * 10,
      'Lobby Lighting': 18 + Math.random() * 5,
      'Parking Lighting': 12 + Math.random() * 4,
      'Corridor Lighting': 8 + Math.random() * 3,
      'Emergency Lighting': 5 + Math.random() * 1
    })
  }
}

// Illuminance bar chart option
const getIlluminanceOption = () => {
  const categories = ['Office Area', 'Main Lobby', 'Parking', 'Corridor']
  const colors = ['#60a5fa', '#facc15', '#34d399', '#f97316']

  return {
    backgroundColor: 'transparent',
    grid: { left: '0%', right: '0%', bottom: 0, top: 25, containLabel: true },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15,25,45,0.9)',
      borderColor: '#3b82f6',
      textStyle: { color: '#e2e8f0' },
      valueFormatter: (value) => value + ' lux'
    },
    legend: { textStyle: { color: '#94a3b8', fontSize: 9 }, top: 0 },
    xAxis: {
      type: 'category',
      data: illuminanceHourLabels.value,
      axisLabel: { color: '#94a3b8', fontSize: 9, rotate: 15 },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    yAxis: {
      type: 'value',
      name: 'Lux',
      nameTextStyle: { color: '#64748b', fontSize: 10 },
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } }
    },
    series: categories.map((name, i) => ({
      name,
      type: 'line',
      data: illuminanceHistory.value.map(d => d[name]),
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
  }
}

// Power consumption area chart option
const getPowerOption = () => {
  const categories = ['Office Lighting', 'Lobby Lighting', 'Parking Lighting', 'Corridor Lighting', 'Emergency Lighting']
  const colors = ['#3b82f6', '#facc15', '#34d399', '#f97316', '#94a3b8']

  const seriesData = categories.map((name, i) => ({
    name,
    type: 'line',
    data: powerHistory.value.map(d => d[name]),
    smooth: true,
    symbol: 'circle',
    symbolSize: 4,
    lineStyle: { width: 2, color: colors[i] },
    itemStyle: { color: colors[i] },
    areaStyle: {
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: colors[i] + '40' },
        { offset: 1, color: colors[i] + '00' }
      ])
    },
    stack: 'total'
  }))

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15,25,45,0.9)',
      borderColor: '#3b82f6',
      textStyle: { color: '#e2e8f0' },
      valueFormatter: (value) => value + ' kW'
    },
    legend: { textStyle: { color: '#94a3b8', fontSize: 8 }, top: 0 },
    grid: { left: '0%', right: '0%', bottom: 0, top: 45, containLabel: true },
    xAxis: {
      type: 'category',
      data: powerTimeLabels.value,
      axisLabel: { color: '#94a3b8', fontSize: 9 },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    yAxis: {
      type: 'value',
      name: 'kW',
      nameTextStyle: { color: '#64748b', fontSize: 10 },
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } }
    },
    series: seriesData
  }
}

// ==================== Chart Lifecycle ====================
const disposeCharts = () => {
  if (illuminanceChart) {
    illuminanceChart.dispose()
    illuminanceChart = null
  }
  if (powerChart) {
    powerChart.dispose()
    powerChart = null
  }
}

const initCharts = async () => {
  await nextTick()

  for (let attempt = 0; attempt < 5; attempt++) {
    await new Promise(resolve => setTimeout(resolve, 100))

    const illDom = illuminanceChartRef.value
    const pwrDom = powerChartRef.value

    if (!illDom || !pwrDom) continue
    if (illDom.clientWidth === 0 || illDom.clientHeight === 0) continue
    if (pwrDom.clientWidth === 0 || pwrDom.clientHeight === 0) continue

    disposeCharts()

    try {
      illuminanceChart = echarts.init(illDom)
      powerChart = echarts.init(pwrDom)

      illuminanceChart.setOption(getIlluminanceOption())
      powerChart.setOption(getPowerOption())

      return
    } catch (e) {
      console.error('[initCharts] Error:', e)
    }
  }
}

const handleResize = () => {
  illuminanceChart?.resize()
  powerChart?.resize()
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
  totalLuminaires.value = 1245 + Math.floor(Math.random() * 8)
  onlineRate.value = parseFloat((97.2 + Math.random() * 1.8).toFixed(1))
  activePower.value = parseFloat((82 + Math.random() * 12).toFixed(1))
  energySaved.value = energySaved.value + Math.floor(Math.random() * 3)
  avgDimLevel.value = Math.floor(65 + Math.random() * 10)
  daylightHarvesting.value = Math.floor(38 + Math.random() * 10)
  occupancySavings.value = Math.floor(25 + Math.random() * 8)
  systemEfficiency.value = parseFloat((87 + Math.random() * 5).toFixed(1))

  // Zone lux levels
  officeLux.value = Math.floor(480 + Math.random() * 80)
  lobbyLux.value = Math.floor(350 + Math.random() * 60)
  parkingLux.value = Math.floor(100 + Math.random() * 40)
  corridorLux.value = Math.floor(160 + Math.random() * 40)

  officeLuxPercent.value = Math.round((officeLux.value / 800) * 100)
  lobbyLuxPercent.value = Math.round((lobbyLux.value / 800) * 100)
  parkingLuxPercent.value = Math.round((parkingLux.value / 800) * 100)
  corridorLuxPercent.value = Math.round((corridorLux.value / 800) * 100)

  // Lighting modes
  lightingModes.value = [
    { name: 'Daylighting', loadPercent: 38 + Math.floor(Math.random() * 10), power: parseFloat((32 + Math.random() * 8).toFixed(1)), color: '#facc15' },
    { name: 'Scheduled', loadPercent: 30 + Math.floor(Math.random() * 10), power: parseFloat((28 + Math.random() * 6).toFixed(1)), color: '#3b82f6' },
    { name: 'Occupancy', loadPercent: 15 + Math.floor(Math.random() * 8), power: parseFloat((13 + Math.random() * 5).toFixed(1)), color: '#34d399' },
    { name: 'Manual', loadPercent: 3 + Math.floor(Math.random() * 5), power: parseFloat((3 + Math.random() * 3).toFixed(1)), color: '#f97316' }
  ]
  const sum = lightingModes.value.reduce((a, b) => a + b.loadPercent, 0)
  lightingModes.value[0].loadPercent += (100 - sum)

  // System health
  systemHealth.value = [
    { subsystem: 'DALI Bus A', status: 'normal', statusText: 'Online' },
    { subsystem: 'DALI Bus B', status: Math.random() > 0.96 ? 'warning' : 'normal', statusText: Math.random() > 0.96 ? 'Lag' : 'Online' },
    { subsystem: 'Motion Sensors', status: Math.random() > 0.88 ? 'warning' : 'normal', statusText: Math.random() > 0.88 ? '1 Fault' : 'Normal' },
    { subsystem: 'Light Sensors', status: 'normal', statusText: 'Normal' },
    { subsystem: 'Control Panel', status: 'normal', statusText: 'Online' }
  ]

  // Dimming zones
  dimmingZones.value = [
    { label: 'Office 3F East', target: '60', actual: String(56 + Math.floor(Math.random() * 8)), deviation: (Math.random() > 0.5 ? '-' : '+') + Math.floor(Math.random() * 3) + '% ✓', status: 'normal' },
    { label: 'Office 3F West', target: '70', actual: String(68 + Math.floor(Math.random() * 8)), deviation: (Math.random() > 0.5 ? '-' : '+') + Math.floor(Math.random() * 3) + '% ⚠', status: 'low' },
    { label: 'Main Lobby', target: '45', actual: String(40 + Math.floor(Math.random() * 8)), deviation: (Math.random() > 0.5 ? '-' : '+') + Math.floor(Math.random() * 3) + '% ✓', status: 'normal' },
    { label: 'Parking B1', target: '30', actual: String(26 + Math.floor(Math.random() * 8)), deviation: (Math.random() > 0.5 ? '-' : '+') + Math.floor(Math.random() * 3) + '% ✓', status: 'low' }
  ]

  // Tips
  const tipPool = [
    { icon: '🌞', title: 'Optimize Daylight Zones', desc: 'Raise blinds in office 3F East to increase daylight harvesting', saving: '~12% energy savings' },
    { icon: '⏰', title: 'Adjust Evening Schedule', desc: 'Extend dimming schedule to include weekend after-hours', saving: '~8% energy savings' },
    { icon: '🔌', title: 'Motion Sensor Calibration', desc: 'Reduce timeout from 15min to 10min in low-traffic corridors', saving: '~6% energy savings' },
    { icon: '📊', title: 'LED Retrofit Analysis', desc: 'Parking B2 still has 45 fluorescent fixtures, consider LED upgrade', saving: '~15% energy savings' }
  ]
  lightingTips.value = tipPool.sort(() => Math.random() - 0.5).slice(0, 1)

  // Update charts
  if (illuminanceChart && powerChart) {
    // Update illuminance history
    const now = new Date()
    illuminanceHourLabels.value.push(now.toTimeString().slice(0, 5))
    if (illuminanceHourLabels.value.length > illuminanceHistoryLength) illuminanceHourLabels.value.shift()

    illuminanceHistory.value.push({
      'Office Area': 450 + Math.random() * 100,
      'Main Lobby': 320 + Math.random() * 80,
      'Parking': 100 + Math.random() * 40,
      'Corridor': 150 + Math.random() * 50
    })
    if (illuminanceHistory.value.length > illuminanceHistoryLength) illuminanceHistory.value.shift()

    illuminanceChart.setOption({
      xAxis: { data: illuminanceHourLabels.value },
      series: ['Office Area', 'Main Lobby', 'Parking', 'Corridor'].map(name => ({
        data: illuminanceHistory.value.map(d => d[name])
      }))
    })

    // Update power history
    powerTimeLabels.value.push(now.toTimeString().slice(0, 5))
    if (powerTimeLabels.value.length > powerHistoryLength) powerTimeLabels.value.shift()

    powerHistory.value.push({
      'Office Lighting': 35 + Math.random() * 10,
      'Lobby Lighting': 18 + Math.random() * 5,
      'Parking Lighting': 12 + Math.random() * 4,
      'Corridor Lighting': 8 + Math.random() * 3,
      'Emergency Lighting': 5 + Math.random() * 1
    })
    if (powerHistory.value.length > powerHistoryLength) powerHistory.value.shift()

    powerChart.setOption({
      xAxis: { data: powerTimeLabels.value },
      series: ['Office Lighting', 'Lobby Lighting', 'Parking Lighting', 'Corridor Lighting', 'Emergency Lighting'].map(name => ({
        data: powerHistory.value.map(d => d[name])
      }))
    })
  }
}

let routeWatch = null
const isMobile = ref(false)
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}
onMounted(async () => {
  checkMobile()
  updateTime()
  clockTimer = setInterval(updateTime, 1000)

  await preloadAssets()

  initIlluminanceHistory()
  initPowerHistory()
  await initCharts()

  if (illuminanceChart && powerChart) {
    updateTimer = setInterval(updateAllData, 5000)
  }

  window.addEventListener('resize', handleResize)
  document.addEventListener('fullscreenchange', onFullscreenChange)

  routeWatch = watch(() => route.fullPath, async () => {
    initIlluminanceHistory()
    initPowerHistory()
    await initCharts()
    if (illuminanceChart && powerChart && !updateTimer) {
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

/* Main Lighting Page Styles */
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
  border-left: 3px solid #60a5fa;
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
.alert-tag.Info {
  background: rgba(96, 165, 250, 0.2);
  color: #60a5fa;
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

.kpi-row-left {
  min-width: 100px;
  max-width: 110px;
  text-align: left;
}
.kpi-row strong {
  font-size: 16px;
  color: #facc15;
  text-align: center;
  min-width: 80px;
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

/* ========== 移动端适配 (屏幕宽度 ≤ 768px) ========== */
@media (max-width: 768px) {
  .hvac-page {
    padding: 16px;
    overflow-y: auto;   /* 关键：让整个页面可以滚动 */
    height: 100%;       /* 改为自动，以适应内容高度 */
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
    flex: none;         /* 取消 flex 伸缩，由滚动决定 */
  }
  .col-left, .col-right {
    width: 100%;
    overflow-y: visible;   /* 取消内部滚动，让整体滚动 */
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
  .card-header {
    font-size: 15px;
    margin-bottom: 10px;
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
  .env-grid {
    gap: 8px;
  }
  .env-item {
    padding: 6px 8px;
  }
  .env-icon-box {
    width: 28px;
    height: 28px;
    font-size: 14px;
  }
  .env-label {
    font-size: 8px;
  }
  .env-value {
    font-size: 12px;
  }
  .env-value small {
    font-size: 9px;
  }
  .health-row {
    font-size: 11px;
  }
  .health-name {
    font-size: 11px;
  }
  .health-status {
    font-size: 10px;
  }
  .cart-view {
    flex-direction: column;
    gap: 16px;
  }
  .chart-card {
    min-height: 220px;
  }
  .chart-box {
    height: 180px;
    min-height: 0;
  }
  .gauges-grid {
    gap: 8px;
  }
  .gauge-item {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .gauge-label {
    font-size: 11px;
    margin-top: 2px;
  }
  :deep(.el-progress-circle) {
    width: 80px !important;
    height: 80px !important;
  }
  :deep(.el-progress__text) {
    font-size: 10px !important;
  }
  .kpi-row {
    font-size: 12px;
  }
  .kpi-row strong {
    font-size: 14px;
  }
  .trend {
    font-size: 10px;
    min-width: 55px;
  }
  .setpoint-row {
    font-size: 11px;
  }
  .sp-label {
    font-size: 11px;
  }
  .sp-set, .sp-actual {
    font-size: 9px;
  }
  .sp-deviation {
    font-size: 10px;
    width: 50px;
  }
  .tip-title {
    font-size: 11px;
  }
  .tip-desc {
    font-size: 10px;
  }
  .tip-saving {
    font-size: 9px;
  }
  .card-img img {
    width: 100%;
    height: auto;
    max-height: 160px;
    object-fit: cover;
  }
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