<template>
  <div v-if="isPageLoaded" class="ev-charging-page">
    <div class="main-view">
      <div class="three-columns">
        <!-- Left Column: Key Metrics + System Status + Recent Events + Device Health -->
        <div class="col-left">
          <div class="title-row" v-if="isMobile">
            <h1 class="page-title">EVCS</h1>
            <span class="live-time">{{ currentTime }}</span>
          </div>
          <div class="card-img" v-if="isMobile">
            <img :src="evImageUrl" alt="EV Charging 3D View" />
          </div>
          <!-- Key Metrics -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">⚡ Key Metrics</div>
            <div class="metrics-list">
              <div class="metric-row">
                <div class="metric-icon">🔌</div>
                <div class="metric-label">Total Chargers</div>
                <div class="metric-value">{{ totalChargers }}</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">✅</div>
                <div class="metric-label">Online Rate</div>
                <div class="metric-value">{{ onlineRate }}%</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">⚡</div>
                <div class="metric-label">Active Sessions</div>
                <div class="metric-value">{{ activeSessions }}</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">📊</div>
                <div class="metric-label">Today Energy</div>
                <div class="metric-value">{{ todayEnergy }} kWh</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">🚨</div>
                <div class="metric-label">Active Alarms</div>
                <div class="metric-value">{{ activeAlarms }}</div>
              </div>
            </div>
          </el-card>

          <!-- Charging Status -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🔋 Charging Status</div>
            <div class="mode-list">
              <div class="mode-row" v-for="item in chargingStatus" :key="item.name">
                <div class="mode-name">{{ item.name }}</div>
                <div class="mode-bar-bg">
                  <div class="mode-bar-fill" :style="{ width: item.load + '%', background: item.color }"></div>
                </div>
                <div class="mode-value">{{ item.load }}%</div>
                <div class="mode-power">{{ item.status }}</div>
              </div>
            </div>
          </el-card>

          <!-- Recent Charging Events -->
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
          <div class="title-row" v-if="!isMobile">
            <h1 class="page-title">EVCS</h1>
            <span class="live-time" v-if="isFullscreen">{{ currentTime }}</span>
          </div>
          <div class="card-img" v-if="!isMobile">
            <img :src="evImageUrl" alt="EV Charging 3D View" />
          </div>
          <div class="cart-view">
            <!-- Energy Consumption Trend -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <div class="card-header">📊 Energy Consumption (Hourly)</div>
              <div ref="energyTrendChartRef" class="chart-box"></div>
            </el-card>
            <!-- Charging Power Monitor -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <div class="card-header">⚡ Charging Power (Last 10 min)</div>
              <div ref="powerChartRef" class="chart-box"></div>
            </el-card>
          </div>
        </div>

        <!-- Right Column: KPIs + Zone Status + Charger Status + Tips -->
        <div class="col-right">
          <!-- EV Charging KPIs -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📊 EV KPIs</div>
            <div class="kpi-row">
              <span class="kpi-row-left">Avg. Charging Power</span>
              <strong>{{ avgPower }} kW</strong>
              <span class="trend stable">Target > 50kW</span>
            </div>
            <div class="kpi-row">
              <span class="kpi-row-left">Total Energy MTD</span>
              <strong>{{ totalEnergyMTD }} kWh</strong>
              <span class="trend up">{{ energyTrend }}</span>
            </div>
            <div class="kpi-row">
              <span class="kpi-row-left">Total Sessions</span>
              <strong>{{ totalSessions }}</strong>
              <span class="trend stable">Today</span>
            </div>
            <div class="kpi-row">
              <span class="kpi-row-left">Avg. Session Duration</span>
              <strong>{{ avgSessionDuration }} min</strong>
              <span class="trend up">+5%</span>
            </div>
            <div class="kpi-row">
              <span class="kpi-row-left">CO₂ Saved</span>
              <strong>{{ co2Saved }} kg</strong>
              <span class="trend up">MTD</span>
            </div>
          </el-card>

          <!-- Zone Charging Status Gauges -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🌡️ Zone Charging Status</div>
            <div class="gauges-grid">
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="stationAUtilization" :color="zoneColor" :width="90" :stroke-width="4">
                  <template #default>
                    <span class="percentage-label">{{ stationABusy }}/{{ stationATotal }}</span>
                  </template>
                </el-progress>
                <div class="gauge-label">Station A</div>
              </div>
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="stationBUtilization" :color="zoneColor" :width="90" :stroke-width="4">
                  <template #default>
                    <span class="percentage-label">{{ stationBBusy }}/{{ stationBTotal }}</span>
                  </template>
                </el-progress>
                <div class="gauge-label">Station B</div>
              </div>
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="stationCUtilization" :color="zoneColor" :width="90" :stroke-width="4">
                  <template #default>
                    <span class="percentage-label">{{ stationCBusy }}/{{ stationCTotal }}</span>
                  </template>
                </el-progress>
                <div class="gauge-label">Station C</div>
              </div>
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="fastChargerUtilization" :color="fastChargerColor" :width="90" :stroke-width="4">
                  <template #default>
                    <span class="percentage-label">{{ fastChargerBusy }}/{{ fastChargerTotal }}</span>
                  </template>
                </el-progress>
                <div class="gauge-label">Fast Chargers</div>
              </div>
            </div>
          </el-card>

          <!-- Charger Status -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🎯 Charger Status</div>
            <div class="setpoint-list">
              <div class="setpoint-row" v-for="item in chargerStatus" :key="item.label">
                <div class="sp-label">{{ item.label }}</div>
                <div class="sp-values">
                  <span class="sp-set">Status: {{ item.status }}</span>
                  <span class="sp-actual">Power: {{ item.power }} kW</span>
                </div>
                <div class="sp-deviation" :class="item.alarmClass">
                  {{ item.alarm }}
                </div>
              </div>
            </div>
          </el-card>

          <!-- Energy Saving Tips -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">💡 Energy Advisory</div>
            <div class="tips-list">
              <div class="tip-item" v-for="(tip, idx) in energyTips" :key="idx">
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
        <div class="loading-tip">Initializing EV Charging System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, watch, computed } from 'vue'
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
const evImageUrl = ref('')

const loadingMessages = [
  'Preparing assets...',
  'Loading background...',
  'Loading charging model...',
  'Initializing modules...',
  'Connecting to chargers...',
  'Starting dashboard...',
  'Almost ready...'
]

// ==================== Preload Assets ====================
const preloadEvImage = () => {
  return new Promise((resolve) => {
    const img = new Image()
    const imageUrl = 'https://aegisnx.com/wp-content/uploads/2026/05/1778228250340.png'

    img.onload = () => {
      evImageUrl.value = imageUrl
      resolve()
    }

    img.onerror = () => {
      console.warn('EV image load failed, using fallback')
      evImageUrl.value = imageUrl
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

  await preloadEvImage()

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

// ==================== Core EV Charging Data ====================
// Key metrics
const totalChargers = ref(48)
const onlineRate = ref(97.2)
const activeSessions = ref(12)
const todayEnergy = ref(2450)
const activeAlarms = ref(1)

// EV KPIs
const avgPower = ref(42.5)
const totalEnergyMTD = ref(45600)
const energyTrend = ref('+12% vs Last Month')
const totalSessions = ref(156)
const avgSessionDuration = ref(35)
const co2Saved = ref(18500)

// Zone charging status
const stationATotal = ref(12)
const stationABusy = ref(7)
const stationBTotal = ref(10)
const stationBBusy = ref(4)
const stationCTotal = ref(8)
const stationCBusy = ref(3)
const fastChargerTotal = ref(4)
const fastChargerBusy = ref(2)

const stationAUtilization = ref(58)
const stationBUtilization = ref(40)
const stationCUtilization = ref(38)
const fastChargerUtilization = ref(50)

// Zone colors
const zoneColor = [
  { color: '#10b981', percentage: 50 },
  { color: '#f59e0b', percentage: 80 },
  { color: '#ef4444', percentage: 100 }
]
const fastChargerColor = [
  { color: '#10b981', percentage: 50 },
  { color: '#f59e0b', percentage: 70 },
  { color: '#ef4444', percentage: 100 }
]

// Charging status throughput
const chargingStatus = ref([
  { name: 'Station A', load: 58, status: 'Active', color: '#fbbf24' },
  { name: 'Station B', load: 40, status: 'Normal', color: '#3b82f6' },
  { name: 'Station C', load: 38, status: 'Normal', color: '#60a5fa' },
  { name: 'Fast Chargers', load: 50, status: 'Busy', color: '#34d399' }
])

// Recent charging events
const recentEvents = ref([
  { id: 1, severity: 'Warning', location: 'Station A - Charger 3', description: 'Charging session interrupted due to connection issue', timestamp: '5 min ago' },
  { id: 2, severity: 'Critical', location: 'Fast Charger 2', description: 'Temperature high on charging cable', timestamp: '12 min ago' },
  { id: 3, severity: 'Warning', location: 'Station B - Charger 7', description: 'Communication timeout with vehicle', timestamp: '28 min ago' }
])

// Device health
const deviceHealth = ref([
  { subsystem: 'Charging Stations', status: 'normal', statusText: 'Online' },
  { subsystem: 'Power Controllers', status: 'normal', statusText: 'Normal' },
  { subsystem: 'Communication Network', status: 'warning', statusText: '2 Offline' },
  { subsystem: 'Payment System', status: 'normal', statusText: 'Operational' },
  { subsystem: 'Load Balancer', status: 'normal', statusText: 'Active' }
])

// Charger status
const chargerStatus = ref([
  { label: 'Station A - DC', status: 'Charging', power: 42, lastAccess: '08:45:22', alarm: 'Normal', alarmClass: 'normal' },
  { label: 'Station A - AC', status: 'Available', power: 0, lastAccess: '07:30:15', alarm: 'Normal', alarmClass: 'normal' },
  { label: 'Fast Charger 1', status: 'Charging', power: 85, lastAccess: '09:12:08', alarm: 'High Load', alarmClass: 'low' },
  { label: 'Fast Charger 2', status: 'Fault', power: 0, lastAccess: '06:20:30', alarm: 'Alert', alarmClass: 'high' }
])

// Energy tips
const energyTips = ref([
  { icon: '⚡', title: 'Peak Load Management', desc: 'Consider shifting charging to off-peak hours (22:00-06:00)', priority: 'High Priority' },
  { icon: '🔋', title: 'Battery Storage Integration', desc: 'BESS available: 500kWh capacity for peak shaving', priority: 'Medium Priority' }
])

// ==================== Charts ====================
const energyTrendChartRef = ref(null)
const powerChartRef = ref(null)
let energyTrendChart = null
let powerChart = null

// 12-hour energy history
const energyHistoryLength = 12
const energyHistory = ref([])
const energyHourLabels = ref([])

const initEnergyHistory = () => {
  energyHistory.value = []
  energyHourLabels.value = []
  const now = new Date()
  for (let i = energyHistoryLength - 1; i >= 0; i--) {
    const t = new Date(now - i * 3600000)
    energyHourLabels.value.push(t.toTimeString().slice(0, 5))
    energyHistory.value.push({
      'Energy (kWh)': 180 + Math.random() * 100,
      'Sessions': 8 + Math.random() * 10
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
      'Station A': 35 + Math.random() * 30,
      'Station B': 20 + Math.random() * 25,
      'Station C': 15 + Math.random() * 20,
      'Fast Chargers': 40 + Math.random() * 50
    })
  }
}

// Energy trend bar chart option
const getEnergyTrendOption = () => {
  return {
    backgroundColor: 'transparent',
    grid: { left: '0%', right: '0%', bottom: 0, top: 48, containLabel: true },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15,25,45,0.9)',
      borderColor: '#3b82f6',
      textStyle: { color: '#e2e8f0' }
    },
    legend: { textStyle: { color: '#94a3b8', fontSize: 9 }, top: 0 },
    xAxis: {
      type: 'category',
      data: energyHourLabels.value,
      axisLabel: { color: '#94a3b8', fontSize: 9, rotate: 15 },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    yAxis: {
      type: 'value',
      name: 'Energy (kWh)',
      nameTextStyle: { color: '#64748b', fontSize: 10 },
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } }
    },
    series: [{
      name: 'Energy (kWh)',
      type: 'bar',
      data: energyHistory.value.map(d => d['Energy (kWh)']),
      itemStyle: {
        color: '#fbbf24',
        borderRadius: [6, 6, 0, 0]
      },
      label: { show: true, position: 'top', formatter: '{c} kWh', fontSize: 9, color: '#fbbf24' }
    }]
  }
}

// Charging power line chart option
const getPowerOption = () => {
  const categories = ['Station A', 'Station B', 'Station C', 'Fast Chargers']
  const colors = ['#60a5fa', '#34d399', '#fbbf24', '#f97316']

  const seriesData = categories.map((name, i) => ({
    name,
    type: 'line',
    data: powerHistory.value.map(d => d[name]),
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
      valueFormatter: (value) => value + ' kW'
    },
    legend: { textStyle: { color: '#94a3b8', fontSize: 9 }, top: 0 },
    grid: { left: '0%', right: '0%', bottom: 0, top: 25, containLabel: true },
    xAxis: {
      type: 'category',
      data: powerTimeLabels.value,
      axisLabel: { color: '#94a3b8', fontSize: 9 },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    yAxis: {
      type: 'value',
      name: 'Power (kW)',
      nameTextStyle: { color: '#64748b', fontSize: 10 },
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } }
    },
    series: seriesData
  }
}

// ==================== Chart Lifecycle ====================
const disposeCharts = () => {
  if (energyTrendChart) {
    energyTrendChart.dispose()
    energyTrendChart = null
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

    const energyDom = energyTrendChartRef.value
    const powerDom = powerChartRef.value

    if (!energyDom || !powerDom) continue
    if (energyDom.clientWidth === 0 || energyDom.clientHeight === 0) continue
    if (powerDom.clientWidth === 0 || powerDom.clientHeight === 0) continue

    disposeCharts()

    try {
      energyTrendChart = echarts.init(energyDom)
      powerChart = echarts.init(powerDom)

      energyTrendChart.setOption(getEnergyTrendOption())
      powerChart.setOption(getPowerOption())

      return
    } catch (e) {
      console.error('[initCharts] Error:', e)
    }
  }
}

const handleResize = () => {
  energyTrendChart?.resize()
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
  // Update key metrics
  totalChargers.value = 46 + Math.floor(Math.random() * 5)
  onlineRate.value = parseFloat((96.5 + Math.random() * 2.5).toFixed(1))
  activeSessions.value = Math.floor(8 + Math.random() * 10)
  todayEnergy.value = todayEnergy.value + Math.floor(Math.random() * 50)
  activeAlarms.value = Math.floor(Math.random() * 3)

  // Update KPIs
  avgPower.value = parseFloat((38 + Math.random() * 12).toFixed(1))
  totalEnergyMTD.value = totalEnergyMTD.value + Math.floor(Math.random() * 200)
  totalSessions.value = totalSessions.value + Math.floor(Math.random() * 5)
  avgSessionDuration.value = Math.floor(28 + Math.random() * 15)
  co2Saved.value = co2Saved.value + Math.floor(Math.random() * 100)

  // Update zone occupancy
  stationABusy.value = Math.floor(4 + Math.random() * 8)
  stationBBusy.value = Math.floor(2 + Math.random() * 6)
  stationCBusy.value = Math.floor(1 + Math.random() * 5)
  fastChargerBusy.value = Math.floor(1 + Math.random() * 3)

  stationAUtilization.value = Math.round((stationABusy.value / stationATotal.value) * 100)
  stationBUtilization.value = Math.round((stationBBusy.value / stationBTotal.value) * 100)
  stationCUtilization.value = Math.round((stationCBusy.value / stationCTotal.value) * 100)
  fastChargerUtilization.value = Math.round((fastChargerBusy.value / fastChargerTotal.value) * 100)

  // Update charging status
  chargingStatus.value = [
    { name: 'Station A', load: stationAUtilization.value, status: stationAUtilization.value > 50 ? 'Active' : 'Normal', color: '#fbbf24' },
    { name: 'Station B', load: stationBUtilization.value, status: stationBUtilization.value > 50 ? 'Busy' : 'Normal', color: '#3b82f6' },
    { name: 'Station C', load: stationCUtilization.value, status: stationCUtilization.value > 50 ? 'Busy' : 'Normal', color: '#60a5fa' },
    { name: 'Fast Chargers', load: fastChargerUtilization.value, status: fastChargerUtilization.value > 60 ? 'Peak' : 'Normal', color: '#34d399' }
  ]

  // Update device health
  deviceHealth.value = [
    { subsystem: 'Charging Stations', status: 'normal', statusText: 'Online' },
    { subsystem: 'Power Controllers', status: Math.random() > 0.95 ? 'warning' : 'normal', statusText: Math.random() > 0.95 ? '1 Offline' : 'Normal' },
    { subsystem: 'Communication Network', status: Math.random() > 0.85 ? 'warning' : 'normal', statusText: Math.random() > 0.85 ? '2 Offline' : 'Active' },
    { subsystem: 'Payment System', status: 'normal', statusText: 'Operational' },
    { subsystem: 'Load Balancer', status: 'normal', statusText: 'Active' }
  ]

  // Update charger status
  chargerStatus.value = [
    { label: 'Station A - DC', status: Math.random() > 0.3 ? 'Charging' : 'Available', power: Math.random() > 0.3 ? Math.floor(30 + Math.random() * 30) : 0, lastAccess: new Date().toTimeString().slice(0, 8), alarm: 'Normal', alarmClass: 'normal' },
    { label: 'Station A - AC', status: Math.random() > 0.6 ? 'Available' : 'Charging', power: Math.random() > 0.6 ? 0 : Math.floor(10 + Math.random() * 15), lastAccess: '07:30:15', alarm: 'Normal', alarmClass: 'normal' },
    { label: 'Fast Charger 1', status: Math.random() > 0.2 ? 'Charging' : 'Available', power: Math.random() > 0.2 ? Math.floor(60 + Math.random() * 40) : 0, lastAccess: '09:12:08', alarm: Math.random() > 0.8 ? 'High Load' : 'Normal', alarmClass: Math.random() > 0.8 ? 'low' : 'normal' },
    { label: 'Fast Charger 2', status: Math.random() > 0.9 ? 'Fault' : (Math.random() > 0.3 ? 'Charging' : 'Available'), power: Math.random() > 0.9 ? 0 : (Math.random() > 0.3 ? Math.floor(50 + Math.random() * 50) : 0), lastAccess: '06:20:30', alarm: Math.random() > 0.9 ? 'Alert' : 'Normal', alarmClass: Math.random() > 0.9 ? 'high' : 'normal' }
  ]

  // Update tips
  const tipPool = [
    { icon: '⚡', title: 'Peak Load Management', desc: 'Consider shifting charging to off-peak hours (22:00-06:00)', priority: 'High Priority' },
    { icon: '🔋', title: 'Battery Storage Integration', desc: 'BESS available: 500kWh capacity for peak shaving', priority: 'Medium Priority' },
    { icon: '🌞', title: 'Solar Integration', desc: 'Solar generation peak: 11AM-2PM, ideal for EV charging', priority: 'Medium Priority' },
    { icon: '📊', title: 'Load Balancing', desc: 'Dynamic load balancing active across all stations', priority: 'Low Priority' }
  ]
  energyTips.value = tipPool.sort(() => Math.random() - 0.5).slice(0, 2)

  // Update charts
  if (energyTrendChart && powerChart) {
    const now = new Date()

    // Update energy chart
    energyHourLabels.value.push(now.toTimeString().slice(0, 5))
    if (energyHourLabels.value.length > energyHistoryLength) energyHourLabels.value.shift()

    energyHistory.value.push({
      'Energy (kWh)': 160 + Math.random() * 120
    })
    if (energyHistory.value.length > energyHistoryLength) energyHistory.value.shift()

    energyTrendChart.setOption({
      xAxis: { data: energyHourLabels.value },
      series: [{ data: energyHistory.value.map(d => d['Energy (kWh)']) }]
    })

    // Update power chart
    powerTimeLabels.value.push(now.toTimeString().slice(0, 5))
    if (powerTimeLabels.value.length > powerHistoryLength) powerTimeLabels.value.shift()

    powerHistory.value.push({
      'Station A': 30 + Math.random() * 35,
      'Station B': 18 + Math.random() * 28,
      'Station C': 12 + Math.random() * 22,
      'Fast Chargers': 35 + Math.random() * 55
    })
    if (powerHistory.value.length > powerHistoryLength) powerHistory.value.shift()

    powerChart.setOption({
      xAxis: { data: powerTimeLabels.value },
      series: [
        { data: powerHistory.value.map(d => d['Station A']) },
        { data: powerHistory.value.map(d => d['Station B']) },
        { data: powerHistory.value.map(d => d['Station C']) },
        { data: powerHistory.value.map(d => d['Fast Chargers']) }
      ]
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

  initEnergyHistory()
  initPowerHistory()
  await initCharts()

  if (energyTrendChart && powerChart) {
    updateTimer = setInterval(updateAllData, 5000)
  }

  window.addEventListener('resize', handleResize)
  document.addEventListener('fullscreenchange', onFullscreenChange)

  routeWatch = watch(() => route.fullPath, async () => {
    initEnergyHistory()
    initPowerHistory()
    await initCharts()
    if (energyTrendChart && powerChart && !updateTimer) {
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

/* Main EV Charging Page Styles */
.ev-charging-page {
  height: 100%;
  background: radial-gradient(circle at 10% 20%, #0a1620, #03060c);
  padding: 24px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  animation: fadeIn 0.5s ease-out;
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

/* Mobile Responsive */
@media (max-width: 768px) {
  .ev-charging-page {
    padding: 16px;
    overflow-y: auto;
    height: auto;
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
    flex: none;
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
  :deep(.el-progress-circle) {
    width: 80px !important;
    height: 80px !important;
  }
  :deep(.el-progress__text) {
    font-size: 10px !important;
  }
  .card-img img {
    width: 100%;
    height: auto;
    max-height: 160px;
    object-fit: cover;
  }
}

/* Global card body overflow */
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