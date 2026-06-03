<template>
  <div v-if="isPageLoaded" class="hvac-page">
    <div class="main-view">
      <div class="three-columns">
        <!-- Left Column: Key Metrics + System Status + Recent Events + Device Health -->
        <div class="col-left">
          <div class="title-row" v-if="isMobile">
            <h1 class="page-title">ENV</h1>
            <span class="live-time">{{ currentTime }}</span>
          </div>
          <div class="card-img" v-if="isMobile">
            <img :src="securityImageUrl" alt="Environmental Sensors 3D View" />
          </div>

          <!-- Key Metrics -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📈 Key Metrics</div>
            <div class="metrics-list">
              <div class="metric-row"><div class="metric-icon">🌡️</div><div class="metric-label">Total Sensors</div><div class="metric-value">{{ totalSensors }}</div></div>
              <div class="metric-row"><div class="metric-icon">🌡️</div><div class="metric-label">Avg Temperature</div><div class="metric-value">{{ avgTemp }}°C</div></div>
              <div class="metric-row"><div class="metric-icon">💧</div><div class="metric-label">Avg Humidity</div><div class="metric-value">{{ avgHumidity }}%</div></div>
              <div class="metric-row"><div class="metric-icon">💨</div><div class="metric-label">Airflow</div><div class="metric-value">{{ airflow }} m/s</div></div>
              <div class="metric-row"><div class="metric-icon">🚨</div><div class="metric-label">Active Alarms</div><div class="metric-value">{{ activeAlarms }}</div></div>
            </div>
          </el-card>

          <!-- Zone Status -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🗺️ Zone Status</div>
            <div class="mode-list">
              <div class="mode-row" v-for="item in zoneStatus" :key="item.name">
                <div class="mode-name">{{ item.name }}</div>
                <div class="mode-bar-bg"><div class="mode-bar-fill" :style="{ width: item.health + '%', background: item.color }"></div></div>
                <div class="mode-value">{{ item.health }}%</div>
                <div class="mode-power">{{ item.status }}</div>
              </div>
            </div>
          </el-card>

          <!-- Recent Events -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📋 Recent Events</div>
            <div class="alert-list">
              <div class="alert-item" v-for="event in recentEvents" :key="event.id">
                <div class="alert-header"><span class="alert-tag" :class="event.severity">{{ event.severity }}</span><span class="alert-device">{{ event.location }}</span></div>
                <div class="alert-msg">{{ event.description }}</div>
                <div class="alert-time">{{ event.timestamp }}</div>
              </div>
            </div>
          </el-card>

          <!-- Device Health -->
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
            <h1 class="page-title">ENV</h1>
            <span class="live-time" v-if="isFullscreen">{{ currentTime }}</span>
          </div>
          <div class="card-img" v-if="!isMobile">
            <img :src="securityImageUrl" alt="Environmental Sensors 3D View" />
          </div>
          <div class="cart-view">
            <!-- Temperature & Humidity Trend -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <div class="card-header">📊 Temp & Humidity Trend (24h)</div>
              <div ref="tempChartRef" class="chart-box"></div>
            </el-card>
            <!-- Zone Heatmap -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <div class="card-header">🗺️ Zone Temperature Map</div>
              <div ref="heatmapChartRef" class="chart-box"></div>
            </el-card>
          </div>
        </div>

        <!-- Right Column: KPIs + Sensor Readings + Threshold Status + Tips -->
        <div class="col-right">
          <!-- Environmental KPIs -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📊 Environmental KPIs</div>
            <div class="kpi-row"><span class="kpi-row-left">Max Temperature</span><strong>{{ maxTemp }}°C</strong><span class="trend" :class="maxTemp > 27 ? 'up' : 'stable'">{{ maxTemp > 27 ? 'Alert' : 'Normal' }}</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Min Temperature</span><strong>{{ minTemp }}°C</strong><span class="trend stable">Range: {{ tempRange }}°C</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Max Humidity</span><strong>{{ maxHumidity }}%</strong><span class="trend" :class="maxHumidity > 60 ? 'up' : 'stable'">{{ maxHumidity > 60 ? 'High' : 'Normal' }}</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Min Humidity</span><strong>{{ minHumidity }}%</strong><span class="trend stable">Range: {{ humidityRange }}%</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Dew Point</span><strong>{{ dewPoint }}°C</strong><span class="trend stable">Risk: {{ dewPointRisk }}</span></div>
          </el-card>

          <!-- Sensor Readings Gauges -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📡 Sensor Readings</div>
            <div class="gauges-grid">
              <div class="gauge-item"><el-progress type="dashboard" :percentage="coldAisleTemp" :color="tempColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ coldAisleTemp }}°C</span></template></el-progress><div class="gauge-label">Cold Aisle</div></div>
              <div class="gauge-item"><el-progress type="dashboard" :percentage="hotAisleTemp" :color="tempColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ hotAisleTemp }}°C</span></template></el-progress><div class="gauge-label">Hot Aisle</div></div>
              <div class="gauge-item"><el-progress type="dashboard" :percentage="returnAirTemp" :color="tempColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ returnAirTemp }}°C</span></template></el-progress><div class="gauge-label">Return Air</div></div>
              <div class="gauge-item"><el-progress type="dashboard" :percentage="outsideTemp" :color="outsideColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ outsideTemp }}°C</span></template></el-progress><div class="gauge-label">Outside</div></div>
            </div>
          </el-card>

          <!-- Threshold Status -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">⚠️ Threshold Status</div>
            <div class="setpoint-list">
              <div class="setpoint-row" v-for="item in thresholdStatus" :key="item.label">
                <div class="sp-label">{{ item.label }}</div>
                <div class="sp-values"><span class="sp-set">Current: {{ item.current }}</span><span class="sp-actual">Limit: {{ item.limit }}</span></div>
                <div class="sp-deviation" :class="item.statusClass">{{ item.status }}</div>
              </div>
            </div>
          </el-card>

          <!-- Environmental Tips -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">💡 Environmental Tips</div>
            <div class="tips-list">
              <div class="tip-item" v-for="(tip, idx) in envTips" :key="idx">
                <div class="tip-icon">{{ tip.icon }}</div>
                <div class="tip-content"><div class="tip-title">{{ tip.title }}</div><div class="tip-desc">{{ tip.desc }}</div><div class="tip-saving">{{ tip.priority }}</div></div>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="loading-container">
    <div class="loading-overlay"><div class="loading-content"><div class="loading-spinner"><div class="spinner-ring"></div><div class="spinner-ring"></div><div class="spinner-ring"></div></div>
      <div class="loading-text"><span class="loading-title">Loading</span><span class="loading-dots"><span>.</span><span>.</span><span>.</span></span></div>
      <div class="loading-progress"><div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div></div>
      <div class="loading-tip">Initializing Environmental Sensors</div>
      <div class="loading-subtip">{{ loadingMessage }}</div>
    </div></div>
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
  if (!instance) throw new Error('useStore() must be called within a setup function')
  const pinia = instance.appContext.config.globalProperties.$pinia
  if (!pinia) throw new Error('Pinia instance not found')
  return useCounterStore(pinia)
}
const counterStore = getStore()
const isFullscreen = computed(() => counterStore.isFullscreen)
const route = useRoute()

// ==================== Loading State ====================
const isPageLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing assets...')
const securityImageUrl = ref('')

const loadingMessages = [
  'Preparing assets...',
  'Loading sensor data...',
  'Reading temperature sensors...',
  'Calculating dew point...',
  'Connecting to all sensors...',
  'Starting dashboard...',
  'Almost ready...'
]

const preloadSecurityImage = () => {
  return new Promise((resolve) => {
    const img = new Image()
    const imageUrl = 'https://aegisnx.com/wp-content/uploads/2026/05/Environment-sensor.jpg'
    img.onload = () => { securityImageUrl.value = imageUrl; resolve() }
    img.onerror = () => { securityImageUrl.value = imageUrl; resolve() }
    img.src = imageUrl
  })
}

const preloadAssets = async () => {
  let progress = 0
  let messageIndex = 0
  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) { messageIndex++; loadingMessage.value = loadingMessages[messageIndex] }
  }, 800)
  const progressInterval = setInterval(() => {
    if (progress < 90) { progress += Math.random() * 10; loadingProgress.value = Math.min(progress, 90) }
  }, 100)
  await preloadSecurityImage()
  clearInterval(messageInterval); clearInterval(progressInterval)
  loadingMessage.value = 'Ready!'; loadingProgress.value = 100
  await new Promise(resolve => setTimeout(resolve, 500))
  isPageLoaded.value = true
}

// ==================== Real-time Clock ====================
const currentTime = ref('')
const updateTime = () => {
  const now = new Date()
  const utc = now.getTime() + (now.getTimezoneOffset() * 60000)
  const sgTime = new Date(utc + (8 * 3600000))
  currentTime.value = `${sgTime.getFullYear()}-${String(sgTime.getMonth() + 1).padStart(2, '0')}-${String(sgTime.getDate()).padStart(2, '0')} ${String(sgTime.getHours()).padStart(2, '0')}:${String(sgTime.getMinutes()).padStart(2, '0')}:${String(sgTime.getSeconds()).padStart(2, '0')}.${String(sgTime.getMilliseconds()).padStart(3, '0')} SGT`
}
let clockTimer = null

// ==================== Core Environmental Data ====================
// Key metrics
const totalSensors = ref(48)
const avgTemp = ref(0)
const avgHumidity = ref(0)
const airflow = ref(0)
const activeAlarms = ref(1)

// Temperature stats
const maxTemp = ref(0)
const minTemp = ref(0)
const tempRange = ref(0)
const maxHumidity = ref(0)
const minHumidity = ref(0)
const humidityRange = ref(0)

// Dew point
const dewPoint = ref(0)
const dewPointRisk = ref('Low')

// Zone readings
const coldAisleTemp = ref(0)
const hotAisleTemp = ref(0)
const returnAirTemp = ref(0)
const outsideTemp = ref(0)

// Zone Status
const zoneStatus = ref([
  { name: 'Cold Aisle A', health: 0, status: 'Optimal', color: '#34d399' },
  { name: 'Hot Aisle A', health: 0, status: 'Optimal', color: '#34d399' },
  { name: 'Cold Aisle B', health: 0, status: 'Optimal', color: '#34d399' },
  { name: 'Hot Aisle B', health: 0, status: 'Warning', color: '#f59e0b' }
])

// Recent events
const recentEvents = ref([
  { id: 1, severity: 'Warning', location: 'Cold Aisle A', description: 'Temperature above 24°C', timestamp: '2 hours ago' },
  { id: 2, severity: 'Info', location: 'Humidity Sensor', description: 'RH dropped below 45%', timestamp: '4 hours ago' },
  { id: 3, severity: 'Success', location: 'Cold Aisle B', description: 'Temperature normalized', timestamp: '8 hours ago' }
])

// Device health
const deviceHealth = ref([
  { subsystem: 'Temperature Sensors', status: 'normal', statusText: 'All Online' },
  { subsystem: 'Humidity Sensors', status: 'normal', statusText: 'All Online' },
  { subsystem: 'Airflow Sensors', status: 'normal', statusText: 'Active' },
  { subsystem: 'Pressure Sensors', status: 'normal', statusText: 'Normal' },
  { subsystem: 'Communication', status: 'normal', statusText: 'Connected' }
])

// Threshold status
const thresholdStatus = ref([
  { label: 'Temperature ASHRAE', current: '0°C', limit: '18-27°C', status: 'Normal', statusClass: 'normal' },
  { label: 'Humidity ASHRAE', current: '0%', limit: '40-60%', status: 'Normal', statusClass: 'normal' },
  { label: 'Airflow Minimum', current: '0 m/s', limit: '> 0.5 m/s', status: 'Normal', statusClass: 'normal' }
])

// Environmental Tips
const envTips = ref([
  { icon: '🌡️', title: 'ASHRAE Compliance', desc: 'All zones within recommended range', priority: 'Good' },
  { icon: '💧', title: 'Humidity Control', desc: 'RH stable at optimal level', priority: 'Optimal' }
])

// Color configurations
const tempColor = [{ color: '#34d399', percentage: 22 }, { color: '#f59e0b', percentage: 25 }, { color: '#ef4444', percentage: 28 }]
const outsideColor = [{ color: '#60a5fa', percentage: 20 }, { color: '#34d399', percentage: 25 }, { color: '#f59e0b', percentage: 30 }]

// ==================== Charts ====================
const tempChartRef = ref(null)
const heatmapChartRef = ref(null)
let tempChart = null
let heatmapChart = null

// Temperature history (24 hours)
const historyLength = 24
const tempHistory = ref([])
const humidityHistory = ref([])
const hourLabels = ref([])

const initTempHistory = () => {
  tempHistory.value = []
  humidityHistory.value = []
  hourLabels.value = []
  const now = new Date()
  for (let i = historyLength - 1; i >= 0; i--) {
    const t = new Date(now - i * 3600000)
    hourLabels.value.push(t.toTimeString().slice(0, 5))
    tempHistory.value.push(parseFloat((22 + Math.random() * 4).toFixed(1)))
    humidityHistory.value.push(parseFloat((45 + Math.random() * 12).toFixed(1)))
  }
}

// Heatmap data (6x8 grid representing racks)
const generateHeatmapData = () => {
  const data = []
  for (let i = 0; i < 8; i++) {
    for (let j = 0; j < 6; j++) {
      const baseTemp = 22 + (i / 8) * 6
      const variation = Math.sin(j) * 1.5
      data.push([j, i, parseFloat((baseTemp + variation + Math.random() * 1.5).toFixed(1))])
    }
  }
  return data
}

const heatmapData = ref(generateHeatmapData())

// Temperature chart option
const getTempChartOption = () => {
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(15,25,45,0.9)', borderColor: '#3b82f6', textStyle: { color: '#e2e8f0' } },
    legend: { data: ['Temperature (°C)', 'Humidity (%)'], textStyle: { color: '#94a3b8', fontSize: 9 }, top: 0 },
    grid: { left: '0%', right: '0%', bottom: 0, top: 48, containLabel: true },
    xAxis: { type: 'category', data: hourLabels.value, axisLabel: { color: '#94a3b8', fontSize: 9, rotate: 30, interval: 3 }, axisLine: { lineStyle: { color: '#334155' } } },
    yAxis: [{ type: 'value', name: 'Temperature (°C)', nameTextStyle: { color: '#64748b', fontSize: 10 }, axisLabel: { color: '#94a3b8', fontSize: 10 }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } } },
      { type: 'value', name: 'Humidity (%)', nameTextStyle: { color: '#64748b', fontSize: 10 }, axisLabel: { color: '#94a3b8', fontSize: 10 }, splitLine: { show: false }, min: 20, max: 80 }],
    series: [
      { name: 'Temperature (°C)', type: 'line', data: tempHistory.value, smooth: true, symbol: 'circle', symbolSize: 4, lineStyle: { width: 2, color: '#ef4444' }, areaStyle: { opacity: 0.3, color: '#ef4444' }, markLine: { data: [{ yAxis: 18, name: 'Min', lineStyle: { color: '#60a5fa', type: 'dashed' } }, { yAxis: 27, name: 'Max', lineStyle: { color: '#f59e0b', type: 'dashed' } }] } },
      { name: 'Humidity (%)', type: 'line', data: humidityHistory.value, smooth: true, symbol: 'circle', symbolSize: 4, lineStyle: { width: 2, color: '#34d399' }, areaStyle: { opacity: 0.3, color: '#34d399' }, yAxisIndex: 1, markLine: { data: [{ yAxis: 40, name: 'Min', lineStyle: { color: '#60a5fa', type: 'dashed' } }, { yAxis: 60, name: 'Max', lineStyle: { color: '#f59e0b', type: 'dashed' } }] } }
    ]
  }
}

// Heatmap chart option
const getHeatmapOption = () => {
  return {
    backgroundColor: 'transparent',
    tooltip: { position: 'top', formatter: (params) => {
        const value = params.value[2]
        return `Rack: ${params.value[0] + 1}, Row: ${String.fromCharCode(65 + params.value[1])}<br/>Temperature: ${value}°C`
      } },
    xAxis: { type: 'category', data: ['R1', 'R2', 'R3', 'R4', 'R5', 'R6'], axisLabel: { color: '#94a3b8', fontSize: 10 }, axisLine: { lineStyle: { color: '#334155' } } },
    yAxis: { type: 'category', data: ['Row H', 'Row G', 'Row F', 'Row E', 'Row D', 'Row C', 'Row B', 'Row A'], axisLabel: { color: '#94a3b8', fontSize: 10 }, axisLine: { lineStyle: { color: '#334155' } } },
    visualMap: { min: 18, max: 30, calculable: true, orient: 'vertical', left: 'right', inRange: { color: ['#60a5fa', '#34d399', '#fbbf24', '#f97316', '#ef4444'] }, textStyle: { color: '#94a3b8' } },
    series: [{
      type: 'heatmap', data: heatmapData.value,
      label: { show: true, formatter: (params) => `${params.value[2]}°C`, fontSize: 9, color: '#e2e8f0' },
      emphasis: { scale: true }
    }]
  }
}

// ==================== Chart Lifecycle ====================
const disposeCharts = () => {
  if (tempChart) { tempChart.dispose(); tempChart = null }
  if (heatmapChart) { heatmapChart.dispose(); heatmapChart = null }
}

const initCharts = async () => {
  await nextTick()
  for (let attempt = 0; attempt < 5; attempt++) {
    await new Promise(resolve => setTimeout(resolve, 100))
    const tempDom = tempChartRef.value
    const heatmapDom = heatmapChartRef.value
    if (!tempDom || !heatmapDom) continue
    if (tempDom.clientWidth === 0 || tempDom.clientHeight === 0) continue
    if (heatmapDom.clientWidth === 0 || heatmapDom.clientHeight === 0) continue
    disposeCharts()
    try {
      tempChart = echarts.init(tempDom)
      heatmapChart = echarts.init(heatmapDom)
      tempChart.setOption(getTempChartOption())
      heatmapChart.setOption(getHeatmapOption())
      return
    } catch (e) { console.error('[initCharts] Error:', e) }
  }
}

const handleResize = () => {
  tempChart?.resize()
  heatmapChart?.resize()
}

let fullscreenTimer = null
const onFullscreenChange = () => {
  clearTimeout(fullscreenTimer)
  fullscreenTimer = setTimeout(handleResize, 350)
}

// ==================== Live Update ====================
let updateTimer = null

const updateAllData = () => {
  // Simulate temperature variations based on hour
  const hour = new Date().getHours()
  const loadVariation = Math.sin(hour / 24 * Math.PI * 2) * 2.5

  // Generate random temperatures across zones
  const baseTemp = 23 + loadVariation
  const newColdAisle = parseFloat((baseTemp - 1 + Math.random() * 2).toFixed(1))
  const newHotAisle = parseFloat((baseTemp + 6 + Math.random() * 2).toFixed(1))
  const newReturnAir = parseFloat((baseTemp + 3 + Math.random() * 1.5).toFixed(1))
  const newOutsideTemp = parseFloat((28 + loadVariation + Math.random() * 3).toFixed(1))

  coldAisleTemp.value = newColdAisle
  hotAisleTemp.value = newHotAisle
  returnAirTemp.value = newReturnAir
  outsideTemp.value = newOutsideTemp

  // Calculate averages
  const allTemps = [newColdAisle, newHotAisle, newReturnAir]
  avgTemp.value = parseFloat((allTemps.reduce((a, b) => a + b, 0) / 3).toFixed(1))
  maxTemp.value = parseFloat(Math.max(...allTemps, newOutsideTemp).toFixed(1))
  minTemp.value = parseFloat(Math.min(...allTemps, newOutsideTemp).toFixed(1))
  tempRange.value = parseFloat((maxTemp.value - minTemp.value).toFixed(1))

  // Humidity (inversely related to temperature)
  const newHumidity = parseFloat((50 - loadVariation * 2 + (Math.random() - 0.5) * 5).toFixed(1))
  avgHumidity.value = Math.min(65, Math.max(35, newHumidity))
  maxHumidity.value = parseFloat((avgHumidity.value + 8 + Math.random() * 5).toFixed(1))
  minHumidity.value = parseFloat((avgHumidity.value - 6 - Math.random() * 4).toFixed(1))
  humidityRange.value = parseFloat((maxHumidity.value - minHumidity.value).toFixed(1))

  // Airflow (varies with temperature load)
  airflow.value = parseFloat((0.8 + loadVariation * 0.1 + Math.random() * 0.2).toFixed(2))

  // Dew point calculation (approximate)
  const dewPointCalc = newHumidity - (100 - newHumidity) / 5
  dewPoint.value = parseFloat(dewPointCalc.toFixed(1))
  if (dewPoint.value > 15) dewPointRisk.value = 'Medium'
  else if (dewPoint.value > 18) dewPointRisk.value = 'High'
  else dewPointRisk.value = 'Low'

  // Zone health status
  const coldAisleHealth = Math.max(0, Math.min(100, 100 - Math.abs(newColdAisle - 22) * 10))
  const hotAisleHealth = Math.max(0, Math.min(100, 100 - Math.abs(newHotAisle - 28) * 8))
  zoneStatus.value = [
    { name: 'Cold Aisle A', health: parseFloat(coldAisleHealth.toFixed(1)), status: coldAisleHealth > 70 ? 'Optimal' : 'Warning', color: coldAisleHealth > 70 ? '#34d399' : '#f59e0b' },
    { name: 'Hot Aisle A', health: parseFloat(hotAisleHealth.toFixed(1)), status: hotAisleHealth > 70 ? 'Optimal' : 'Warning', color: hotAisleHealth > 70 ? '#34d399' : '#f59e0b' },
    { name: 'Cold Aisle B', health: parseFloat((coldAisleHealth - 5 + Math.random() * 10).toFixed(1)), status: 'Optimal', color: '#34d399' },
    { name: 'Hot Aisle B', health: parseFloat((hotAisleHealth - 10 + Math.random() * 10).toFixed(1)), status: coldAisleHealth < 60 ? 'Warning' : 'Optimal', color: coldAisleHealth < 60 ? '#f59e0b' : '#34d399' }
  ]

  // Threshold status
  thresholdStatus.value = [
    { label: 'Temperature ASHRAE', current: `${avgTemp.value}°C`, limit: '18-27°C', status: avgTemp.value >= 18 && avgTemp.value <= 27 ? 'Normal' : 'Alert', statusClass: avgTemp.value >= 18 && avgTemp.value <= 27 ? 'normal' : 'high' },
    { label: 'Humidity ASHRAE', current: `${avgHumidity.value}%`, limit: '40-60%', status: avgHumidity.value >= 40 && avgHumidity.value <= 60 ? 'Normal' : 'Alert', statusClass: avgHumidity.value >= 40 && avgHumidity.value <= 60 ? 'normal' : 'high' },
    { label: 'Airflow Minimum', current: `${airflow.value} m/s`, limit: '> 0.5 m/s', status: airflow.value >= 0.5 ? 'Normal' : 'Alert', statusClass: airflow.value >= 0.5 ? 'normal' : 'high' }
  ]

  // Update device health occasionally
  if (Math.random() > 0.95) {
    deviceHealth.value = [
      { subsystem: 'Temperature Sensors', status: 'normal', statusText: 'All Online' },
      { subsystem: 'Humidity Sensors', status: 'normal', statusText: 'All Online' },
      { subsystem: 'Airflow Sensors', status: airflow.value < 0.4 ? 'warning' : 'normal', statusText: airflow.value < 0.4 ? 'Low Flow' : 'Active' },
      { subsystem: 'Pressure Sensors', status: 'normal', statusText: 'Normal' },
      { subsystem: 'Communication', status: 'normal', statusText: 'Connected' }
    ]
  }

  // Update tips occasionally
  if (Math.random() > 0.7) {
    const tipPool = [
      { icon: '🌡️', title: 'ASHRAE Compliance', desc: `Temp: ${avgTemp.value}°C`, priority: avgTemp.value > 27 ? 'Alert' : 'Good' },
      { icon: '💧', title: 'Humidity Control', desc: `RH: ${avgHumidity.value}%`, priority: avgHumidity.value > 60 ? 'High' : (avgHumidity.value < 40 ? 'Low' : 'Optimal') },
      { icon: '💨', title: 'Airflow Warning', desc: `Cold aisle airflow: ${airflow.value} m/s`, priority: airflow.value < 0.5 ? 'Low' : 'Normal' }
    ]
    envTips.value = tipPool.sort(() => Math.random() - 0.5).slice(0, 2)
  }

  // Update charts
  if (tempChart && heatmapChart) {
    const now = new Date()
    const timeLabel = now.toTimeString().slice(0, 5)
    const lastHour = hourLabels.value[hourLabels.value.length - 1]

    if (lastHour !== timeLabel) {
      hourLabels.value.push(timeLabel)
      if (hourLabels.value.length > historyLength) hourLabels.value.shift()
      tempHistory.value.push(avgTemp.value)
      humidityHistory.value.push(avgHumidity.value)
      if (tempHistory.value.length > historyLength) tempHistory.value.shift()
      if (humidityHistory.value.length > historyLength) humidityHistory.value.shift()

      tempChart.setOption({
        xAxis: { data: hourLabels.value },
        series: [{ data: tempHistory.value }, { data: humidityHistory.value }]
      })
    }

    // Update heatmap with new data
    heatmapData.value = generateHeatmapData()
    heatmapChart.setOption({ series: [{ data: heatmapData.value }] })
  }
}

let routeWatch = null
const isMobile = ref(false)
const checkMobile = () => { isMobile.value = window.innerWidth < 768 }

onMounted(async () => {
  checkMobile()
  updateTime()
  clockTimer = setInterval(updateTime, 1000)

  await preloadAssets()

  // Initialize values
  avgTemp.value = 23.5
  avgHumidity.value = 52
  airflow.value = 0.85
  coldAisleTemp.value = 22.5
  hotAisleTemp.value = 28.5
  returnAirTemp.value = 26.0
  outsideTemp.value = 29.5
  maxTemp.value = 29.5
  minTemp.value = 22.5
  tempRange.value = 7.0
  maxHumidity.value = 58
  minHumidity.value = 46
  humidityRange.value = 12
  dewPoint.value = 12.5

  initTempHistory()
  await initCharts()

  if (tempChart && heatmapChart) {
    updateTimer = setInterval(updateAllData, 5000)
  }

  window.addEventListener('resize', handleResize)
  document.addEventListener('fullscreenchange', onFullscreenChange)

  routeWatch = watch(() => route.fullPath, async () => {
    initTempHistory()
    await initCharts()
    if (tempChart && heatmapChart && !updateTimer) {
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
/* Loading Screen */
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
.loading-overlay { position: relative; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; backdrop-filter: blur(2px); }
.loading-content { text-align: center; padding: 40px; border-radius: 32px; background: rgba(15, 25, 45, 0.6); backdrop-filter: blur(20px); border: 1px solid rgba(59, 130, 246, 0.3); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); animation: fadeInUp 0.6s ease-out; }
.loading-spinner { position: relative; width: 80px; height: 80px; margin: 0 auto 24px; }
.spinner-ring { position: absolute; width: 100%; height: 100%; border-radius: 50%; border: 3px solid transparent; animation: spin 1.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite; }
.spinner-ring:nth-child(1) { border-top-color: #3b82f6; animation-delay: 0s; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.loading-text { margin-bottom: 24px; font-size: 28px; font-weight: 700; color: #e2e8f0; display: flex; justify-content: center; align-items: baseline; gap: 4px; }
.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce { 0%, 80%, 100% { transform: scale(0); opacity: 0.3; } 40% { transform: scale(1); opacity: 1; } }
.loading-progress { width: 280px; height: 4px; background: rgba(255, 255, 255, 0.1); border-radius: 4px; overflow: hidden; margin: 0 auto 16px; }
.progress-bar { height: 100%; background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec489a); border-radius: 4px; transition: width 0.3s ease; background-size: 200% auto; animation: shimmer 2s linear infinite; }
@keyframes shimmer { 0% { background-position: 0% 0%; } 100% { background-position: 200% 0%; } }
.loading-tip { font-size: 13px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 8px; font-weight: 500; }
.loading-subtip { font-size: 11px; color: #64748b; letter-spacing: 0.5px; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

.hvac-page {
  height: 100%;
  background: radial-gradient(circle at 10% 20%, #0a1620, #03060c);
  padding: 24px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  animation: fadeIn 0.5s ease-out;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.title-row { display: flex; align-items: center; justify-content: center; position: relative; flex-shrink: 0; }
.page-title { font-size: 32px; font-weight: 800; background: linear-gradient(135deg, #e2e8f0, #60a5fa); -webkit-background-clip: text; background-clip: text; color: transparent; letter-spacing: 1px; text-shadow: 0 0 8px rgba(96,165,250,0.4); margin: 0; }
.live-time { position: absolute; right: 0; font-size: 14px; font-weight: 600; color: #facc15; font-family: monospace; letter-spacing: 1px; text-shadow: 0 0 6px rgba(250,204,21,0.3); padding: 6px 14px; background: rgba(15,25,45,0.6); border: 1px solid rgba(59,130,246,0.3); border-radius: 10px; backdrop-filter: blur(8px); }
.main-view { flex: 1; display: flex; flex-direction: column; min-height: 0; }
.three-columns { flex: 1; display: flex; gap: 20px; align-items: stretch; min-height: 0; }
.col-left, .col-right { width: 300px; flex-shrink: 0; display: flex; flex-direction: column; gap: 20px; overflow-y: auto; scrollbar-width: none; -ms-overflow-style: none; min-height: 0; }
.col-left::-webkit-scrollbar, .col-right::-webkit-scrollbar { display: none; }
.col-center { flex: 1; display: flex; flex-direction: column; gap: 20px; min-height: 0; }
.glass-card, .card-img { background: rgba(15,25,45,0.6); backdrop-filter: blur(12px); border: 1px solid rgba(59,130,246,0.3); border-radius: 20px; transition: all 0.3s; }
.glass-card:hover { background: rgba(15,25,45,0.8); border-color: rgba(59,130,246,0.6); transform: translateY(-3px); }
.card { background: transparent; }
.card-img { overflow: hidden; background: rgba(0,0,0,0.3); }
.card-img img { width: 100%; display: block; height: auto; border-radius: 10px; }
.card-header { font-weight: 600; margin-bottom: 10px; font-size: 16px; color: #e2e8f0; border-left: 4px solid #3b82f6; padding-left: 10px; }
.metrics-list { display: flex; flex-direction: column; }
.metric-row { display: flex; align-items: center; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid rgba(148,163,184,0.2); }
.metric-row .metric-icon { font-size: 24px; width: 36px; opacity: 0.9; }
.metric-row .metric-label { flex: 1; font-size: 14px; color: #94a3b8; padding-left: 12px; letter-spacing: 0.3px; }
.metric-row .metric-value { font-size: 18px; font-weight: 600; color: #facc15; text-align: right; font-family: monospace; }
.mode-list { display: flex; flex-direction: column; gap: 12px; }
.mode-row { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #cbd5e1; }
.mode-name { width: 80px; flex-shrink: 0; }
.mode-bar-bg { flex: 1; height: 6px; background: rgba(148,163,184,0.15); border-radius: 3px; overflow: hidden; }
.mode-bar-fill { height: 100%; border-radius: 3px; transition: width 0.5s; }
.mode-value { width: 35px; text-align: right; color: #facc15; }
.mode-power { width: 55px; text-align: right; color: #94a3b8; }
.alert-list { display: flex; flex-direction: column; gap: 12px; }
.alert-item { background: rgba(239,68,68,0.05); border-radius: 8px; padding: 4px 10px; border-left: 3px solid #ef4444; }
.alert-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.alert-tag { font-size: 10px; font-weight: 700; text-transform: uppercase; padding: 2px 6px; border-radius: 4px; }
.alert-tag.Warning { background: rgba(251,191,36,0.2); color: #fbbf24; }
.alert-tag.Critical { background: rgba(239,68,68,0.2); color: #ef4444; }
.alert-tag.Info { background: rgba(59,130,246,0.2); color: #60a5fa; }
.alert-tag.Success { background: rgba(52,211,153,0.2); color: #34d399; }
.alert-device { font-size: 12px; font-weight: 600; color: #e2e8f0; }
.alert-msg { font-size: 11px; color: #94a3b8; margin-bottom: 2px; }
.alert-time { font-size: 10px; color: #64748b; }
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
.cart-view { width: 100%; display: flex; flex: 1; background: transparent; overflow-y: auto; gap: 10px; min-height: 0; }
.chart-card { flex: 1; display: flex; flex-direction: column; min-height: 0; }
.chart-card .card-header { flex-shrink: 0; }
.chart-box { flex: 1; width: 100%; min-height: 0; overflow: hidden; padding: 8px; box-sizing: border-box; }
.gauges-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.gauge-item { text-align: center; }
.gauge-label { font-size: 13px; color: #cbd5e1; margin-top: 0px; height: 20px; text-align: center; align-items: center; }
.kpi-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; font-size: 13px; color: #cbd5e6; }
.kpi-row span { text-align: left; }
.kpi-row-left { min-width: 100px; max-width: 100px; text-align: left; }
.kpi-row strong { font-size: 16px; color: #facc15; text-align: center; }
.trend { width: 70px; font-size: 11px; margin-left: 8px; text-align: right; font-weight: bold; }
.trend.up { color: #34d399; text-align: right; }
.trend.stable { color: #fbbf24; text-align: right; }
.setpoint-list { display: flex; flex-direction: column; gap: 12px; }
.setpoint-row { display: flex; align-items: center; justify-content: space-between; font-size: 12px; }
.sp-label { flex: 1; color: #94a3b8; font-size: 13px; font-weight: bold; }
.sp-values { display: flex; flex-direction: column; align-items: flex-end; justify-content: center; align-items: center; gap: 2px; margin-right: 8px; }
.sp-set { font-size: 10px; color: #cbd5e1; font-weight: bold; }
.sp-actual { font-weight: 600; text-align: center; color: #fbbf24; }
.sp-deviation { width: 60px; text-align: right; font-weight: 700; font-size: 12px; }
.sp-deviation.high { color: #ef4444; }
.sp-deviation.low { color: #3b82f6; }
.sp-deviation.normal { color: #34d399; }
.tips-list { display: flex; flex-direction: column; gap: 12px; }
.tip-item { display: flex; gap: 10px; padding: 8px 10px; background: rgba(59,130,246,0.08); border-radius: 8px; border-left: 3px solid #3b82f6; margin-top: 5px; }
.tip-icon { font-size: 18px; flex-shrink: 0; margin-top: 2px; }
.tip-content { flex: 1; }
.tip-title { font-size: 12px; font-weight: 600; color: #e2e8f0; margin-bottom: 2px; }
.tip-desc { font-size: 11px; color: #94a3b8; line-height: 1.4; margin-bottom: 2px; }
.tip-saving { font-size: 10px; color: #facc15; font-weight: 600; }
.percentage-value { display: block; margin-top: 10px; font-size: 18px; }
.percentage-label { display: block; margin-top: 10px; font-size: 12px; color: #facc15; font-weight: bold; }

@media (max-width: 768px) {
  .hvac-page { padding: 16px; overflow-y: auto; height: auto; }
  .title-row { flex-direction: column; align-items: stretch; gap: 10px; margin-bottom: 10px; flex-shrink: 0; }
  .page-title { font-size: 26px; text-align: center; }
  .live-time { position: static; text-align: center; width: fit-content; margin: 0 auto; font-size: 12px; padding: 4px 12px; }
  .three-columns { flex-direction: column; gap: 16px; flex: none; }
  .col-left, .col-right { width: 100%; overflow-y: visible; gap: 16px; }
  .col-center { gap: 16px; }
  .glass-card, .card-img { border-radius: 16px; }
  .glass-card:hover { transform: none; }
  .card-header { font-size: 15px; margin-bottom: 10px; }
  .metric-row .metric-icon { font-size: 20px; width: 28px; }
  .metric-row .metric-label { font-size: 12px; padding-left: 8px; }
  .metric-row .metric-value { font-size: 16px; }
  .mode-name { width: 70px; font-size: 11px; }
  .mode-value { width: 30px; font-size: 11px; }
  .mode-power { width: 50px; font-size: 10px; }
  .health-row { font-size: 11px; }
  .health-name { font-size: 11px; }
  .health-status { font-size: 10px; }
  .cart-view { flex-direction: column; gap: 16px; }
  .chart-card { min-height: 220px; }
  .chart-box { height: 180px; min-height: 0; }
  .gauges-grid { gap: 8px; }
  .gauge-item { display: flex; flex-direction: column; align-items: center; }
  .gauge-label { font-size: 11px; margin-top: 2px; }
  :deep(.el-progress-circle) { width: 80px !important; height: 80px !important; }
  :deep(.el-progress__text) { font-size: 10px !important; }
  .kpi-row { font-size: 12px; }
  .kpi-row strong { font-size: 14px; }
  .trend { font-size: 10px; min-width: 55px; }
  .setpoint-row { font-size: 11px; }
  .sp-label { font-size: 11px; }
  .sp-set, .sp-actual { font-size: 9px; }
  .sp-deviation { font-size: 10px; width: 50px; }
  .tip-title { font-size: 11px; }
  .tip-desc { font-size: 10px; }
  .tip-saving { font-size: 9px; }
  .card-img img { width: 100%; height: auto; max-height: 160px; object-fit: cover; }
}
</style>

<style>
.el-card__body { scrollbar-width: none; -ms-overflow-style: none; overflow: visible !important; }
.col-left .el-card, .col-right .el-card { overflow: visible; height: auto; flex-shrink: 0; }
.chart-card .el-card__body { height: 100%; display: flex; flex-direction: column; }
</style>