<template>
  <div v-if="isPageLoaded" class="hvac-page">
    <div class="main-view">
      <div class="three-columns">
        <!-- Left Column: Key Metrics + System Status + Recent Events + Device Health -->
        <div class="col-left">
          <div class="title-row" v-if="isMobile">
            <h1 class="page-title">CRAC</h1>
            <span class="live-time">{{ currentTime }}</span>
          </div>
          <div class="card-img" v-if="isMobile">
            <img :src="securityImageUrl" alt="CRAC 3D View" />
          </div>

          <!-- Key Metrics -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📈 Key Metrics</div>
            <div class="metrics-list">
              <div class="metric-row"><div class="metric-icon">❄️</div><div class="metric-label">Total Units</div><div class="metric-value">{{ totalUnits }}</div></div>
              <div class="metric-row"><div class="metric-icon">🌡️</div><div class="metric-label">Avg Supply Temp</div><div class="metric-value">{{ avgSupplyTemp }}°C</div></div>
              <div class="metric-row"><div class="metric-icon">💨</div><div class="metric-label">Total Airflow</div><div class="metric-value">{{ totalAirflow }} m³/h</div></div>
              <div class="metric-row"><div class="metric-icon">⚡</div><div class="metric-label">Total Power</div><div class="metric-value">{{ totalPower }} kW</div></div>
              <div class="metric-row"><div class="metric-icon">🚨</div><div class="metric-label">Active Alarms</div><div class="metric-value">{{ activeAlarms }}</div></div>
            </div>
          </el-card>

          <!-- CRAC Status -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">❄️ CRAC Status</div>
            <div class="mode-list">
              <div class="mode-row" v-for="item in cracStatus" :key="item.name">
                <div class="mode-name">{{ item.name }}</div>
                <div class="mode-bar-bg"><div class="mode-bar-fill" :style="{ width: item.capacity + '%', background: item.color }"></div></div>
                <div class="mode-value">{{ item.capacity }}%</div>
                <div class="mode-power">{{ item.mode }}</div>
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
            <h1 class="page-title">CRAC</h1>
            <span class="live-time" v-if="isFullscreen">{{ currentTime }}</span>
          </div>
          <div class="card-img" v-if="!isMobile">
            <img :src="securityImageUrl" alt="CRAC 3D View" />
          </div>
          <div class="cart-view">
            <!-- Temperature & Humidity Trend -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <div class="card-header">📊 Temperature & Humidity Trend (24h)</div>
              <div ref="tempChartRef" class="chart-box"></div>
            </el-card>
            <!-- Cooling Capacity Distribution -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <div class="card-header">❄️ Cooling Capacity Distribution</div>
              <div ref="capacityChartRef" class="chart-box"></div>
            </el-card>
          </div>
        </div>

        <!-- Right Column: KPIs + Zone Status + Fan Status + Tips -->
        <div class="col-right">
          <!-- CRAC KPIs -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📊 CRAC KPIs</div>
            <div class="kpi-row"><span class="kpi-row-left">Return Temp</span><strong>{{ returnTemp }}°C</strong><span class="trend stable">Target: 24°C</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Supply Temp</span><strong>{{ supplyTemp }}°C</strong><span class="trend" :class="supplyTemp > 18 ? 'up' : 'stable'">{{ supplyTemp > 18 ? 'High' : 'Normal' }}</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Humidity</span><strong>{{ humidity }}%</strong><span class="trend" :class="humidity > 55 ? 'up' : (humidity < 45 ? 'down' : 'stable')">{{ humidity > 55 ? 'High' : (humidity < 45 ? 'Low' : 'Optimal') }}</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Cooling Capacity</span><strong>{{ coolingCapacity }} kW</strong><span class="trend stable">Available</span></div>
            <div class="kpi-row"><span class="kpi-row-left">COP</span><strong>{{ cop }}</strong><span class="trend" :class="cop < 3 ? 'up' : 'stable'">{{ cop < 3 ? 'Low' : 'Efficient' }}</span></div>
          </el-card>

          <!-- Zone Status Gauges -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🌡️ Zone Status</div>
            <div class="gauges-grid">
              <div class="gauge-item"><el-progress type="dashboard" :percentage="coldAisleTemp" :color="tempColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ coldAisleTemp }}°C</span></template></el-progress><div class="gauge-label">Cold Aisle</div></div>
              <div class="gauge-item"><el-progress type="dashboard" :percentage="hotAisleTemp" :color="tempColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ hotAisleTemp }}°C</span></template></el-progress><div class="gauge-label">Hot Aisle</div></div>
              <div class="gauge-item"><el-progress type="dashboard" :percentage="supplyTemp" :color="tempColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ supplyTemp }}°C</span></template></el-progress><div class="gauge-label">Supply Air</div></div>
              <div class="gauge-item"><el-progress type="dashboard" :percentage="deltaT" :color="deltaTColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ deltaT }}°C</span></template></el-progress><div class="gauge-label">ΔT (Return-Supply)</div></div>
            </div>
          </el-card>

          <!-- Fan Status -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">💨 Fan Status</div>
            <div class="setpoint-list">
              <div class="setpoint-row" v-for="item in fanStatus" :key="item.label">
                <div class="sp-label">{{ item.label }}</div>
                <div class="sp-values"><span class="sp-set">Speed: {{ item.speed }}%</span><span class="sp-actual">Airflow: {{ item.airflow }} m³/h</span></div>
                <div class="sp-deviation" :class="item.statusClass">{{ item.status }}</div>
              </div>
            </div>
          </el-card>

          <!-- CRAC Tips -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">💡 CRAC Tips</div>
            <div class="tips-list">
              <div class="tip-item" v-for="(tip, idx) in cracTips" :key="idx">
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
      <div class="loading-tip">Initializing CRAC System</div>
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
  'Loading CRAC data...',
  'Checking temperature sensors...',
  'Initializing cooling circuits...',
  'Connecting to controllers...',
  'Starting dashboard...',
  'Almost ready...'
]

const preloadSecurityImage = () => {
  return new Promise((resolve) => {
    const img = new Image()
    const imageUrl = 'https://aegisnx.com/wp-content/uploads/2026/05/zgp123456520.png'
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

// ==================== Core CRAC Data ====================
// Key metrics
const totalUnits = ref(6)
const avgSupplyTemp = ref(0)
const totalAirflow = ref(0)
const totalPower = ref(0)
const activeAlarms = ref(1)

// CRAC electrical parameters
const returnTemp = ref(0)
const supplyTemp = ref(0)
const humidity = ref(0)
const coolingCapacity = ref(0)
const cop = ref(0)

// Zone temperatures
const coldAisleTemp = ref(0)
const hotAisleTemp = ref(0)
const deltaT = ref(0)

// CRAC Status
const cracStatus = ref([
  { name: 'CRAC 1', capacity: 0, mode: 'Auto', color: '#34d399' },
  { name: 'CRAC 2', capacity: 0, mode: 'Auto', color: '#34d399' },
  { name: 'CRAC 3', capacity: 0, mode: 'Auto', color: '#34d399' },
  { name: 'CRAC 4', capacity: 0, mode: 'Standby', color: '#60a5fa' }
])

// Recent events
const recentEvents = ref([
  { id: 1, severity: 'Success', location: 'CRAC 1', description: 'Temperature stabilized at setpoint', timestamp: '2 hours ago' },
  { id: 2, severity: 'Warning', location: 'CRAC 3', description: 'Humidity below threshold', timestamp: '4 hours ago' },
  { id: 3, severity: 'Info', location: 'CRAC 2', description: 'Filter cleaning recommended', timestamp: '8 hours ago' }
])

// Device health
const deviceHealth = ref([
  { subsystem: 'Compressors', status: 'normal', statusText: 'All Running' },
  { subsystem: 'Fans', status: 'normal', statusText: 'Normal' },
  { subsystem: 'Refrigerant Circuit', status: 'normal', statusText: 'OK' },
  { subsystem: 'Humidifiers', status: 'normal', statusText: 'Standby' },
  { subsystem: 'Controllers', status: 'normal', statusText: 'Online' }
])

// Fan status
const fanStatus = ref([
  { label: 'Supply Fan 1', speed: 0, airflow: 0, status: 'Normal', statusClass: 'normal' },
  { label: 'Supply Fan 2', speed: 0, airflow: 0, status: 'Normal', statusClass: 'normal' },
  { label: 'Return Fan', speed: 0, airflow: 0, status: 'Normal', statusClass: 'normal' }
])

// CRAC Tips
const cracTips = ref([
  { icon: '❄️', title: 'Cooling Efficiency', desc: 'Delta T optimal range 10-14°C', priority: 'Optimal' },
  { icon: '💧', title: 'Humidity Control', desc: 'RH within ASHRAE recommended range', priority: 'Good' }
])

// Color configurations
const tempColor = [{ color: '#34d399', percentage: 22 }, { color: '#f59e0b', percentage: 25 }, { color: '#ef4444', percentage: 28 }]
const deltaTColor = [{ color: '#ef4444', percentage: 8 }, { color: '#f59e0b', percentage: 10 }, { color: '#34d399', percentage: 14 }]

// ==================== Charts ====================
const tempChartRef = ref(null)
const capacityChartRef = ref(null)
let tempChart = null
let capacityChart = null

// Temperature history (24 hours)
const historyLength = 24
const supplyTempHistory = ref([])
const returnTempHistory = ref([])
const humidityHistory = ref([])
const hourLabels = ref([])

const initTempHistory = () => {
  supplyTempHistory.value = []
  returnTempHistory.value = []
  humidityHistory.value = []
  hourLabels.value = []
  const now = new Date()
  for (let i = historyLength - 1; i >= 0; i--) {
    const t = new Date(now - i * 3600000)
    hourLabels.value.push(t.toTimeString().slice(0, 5))
    supplyTempHistory.value.push(parseFloat((16 + Math.random() * 4).toFixed(1)))
    returnTempHistory.value.push(parseFloat((24 + Math.random() * 3).toFixed(1)))
    humidityHistory.value.push(parseFloat((45 + Math.random() * 15).toFixed(1)))
  }
}

// Capacity distribution data
const capacityDistribution = ref([35, 28, 22, 15])

// Temperature chart option
const getTempChartOption = () => {
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(15,25,45,0.9)', borderColor: '#3b82f6', textStyle: { color: '#e2e8f0' } },
    legend: { data: ['Supply Temp (°C)', 'Return Temp (°C)', 'Humidity (%)'], textStyle: { color: '#94a3b8', fontSize: 9 }, top: 0 },
    grid: { left: '0%', right: '0%', bottom: 0, top: 48, containLabel: true },
    xAxis: { type: 'category', data: hourLabels.value, axisLabel: { color: '#94a3b8', fontSize: 9, rotate: 30, interval: 3 }, axisLine: { lineStyle: { color: '#334155' } } },
    yAxis: [{ type: 'value', name: 'Temperature (°C)', nameTextStyle: { color: '#64748b', fontSize: 10 }, axisLabel: { color: '#94a3b8', fontSize: 10 }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } } },
      { type: 'value', name: 'Humidity (%)', nameTextStyle: { color: '#64748b', fontSize: 10 }, axisLabel: { color: '#94a3b8', fontSize: 10 }, splitLine: { show: false }, min: 20, max: 80 }],
    series: [
      { name: 'Supply Temp (°C)', type: 'line', data: supplyTempHistory.value, smooth: true, symbol: 'circle', symbolSize: 4, lineStyle: { width: 2, color: '#60a5fa' }, areaStyle: { opacity: 0.3, color: '#60a5fa' } },
      { name: 'Return Temp (°C)', type: 'line', data: returnTempHistory.value, smooth: true, symbol: 'circle', symbolSize: 4, lineStyle: { width: 2, color: '#ef4444' }, areaStyle: { opacity: 0.3, color: '#ef4444' } },
      { name: 'Humidity (%)', type: 'line', data: humidityHistory.value, smooth: true, symbol: 'circle', symbolSize: 4, lineStyle: { width: 2, color: '#34d399' }, areaStyle: { opacity: 0.3, color: '#34d399' }, yAxisIndex: 1 }
    ]
  }
}

// Cooling capacity distribution pie chart option
const getCapacityChartOption = () => {
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', backgroundColor: 'rgba(15,25,45,0.9)', borderColor: '#3b82f6', textStyle: { color: '#e2e8f0' } },
    legend: { orient: 'vertical', left: 'left', textStyle: { color: '#94a3b8', fontSize: 10 } },
    series: [{
      type: 'pie', radius: '55%', center: ['50%', '50%'],
      data: [
        { value: 35, name: 'CRAC 1', itemStyle: { color: '#fbbf24' } },
        { value: 28, name: 'CRAC 2', itemStyle: { color: '#60a5fa' } },
        { value: 22, name: 'CRAC 3', itemStyle: { color: '#34d399' } },
        { value: 15, name: 'CRAC 4', itemStyle: { color: '#f97316' } }
      ],
      label: { show: true, formatter: '{b}: {d}%', fontSize: 10, color: '#cbd5e1' }
    }]
  }
}

// ==================== Chart Lifecycle ====================
const disposeCharts = () => {
  if (tempChart) { tempChart.dispose(); tempChart = null }
  if (capacityChart) { capacityChart.dispose(); capacityChart = null }
}

const initCharts = async () => {
  await nextTick()
  for (let attempt = 0; attempt < 5; attempt++) {
    await new Promise(resolve => setTimeout(resolve, 100))
    const tempDom = tempChartRef.value
    const capacityDom = capacityChartRef.value
    if (!tempDom || !capacityDom) continue
    if (tempDom.clientWidth === 0 || tempDom.clientHeight === 0) continue
    if (capacityDom.clientWidth === 0 || capacityDom.clientHeight === 0) continue
    disposeCharts()
    try {
      tempChart = echarts.init(tempDom)
      capacityChart = echarts.init(capacityDom)
      tempChart.setOption(getTempChartOption())
      capacityChart.setOption(getCapacityChartOption())
      return
    } catch (e) { console.error('[initCharts] Error:', e) }
  }
}

const handleResize = () => {
  tempChart?.resize()
  capacityChart?.resize()
}

let fullscreenTimer = null
const onFullscreenChange = () => {
  clearTimeout(fullscreenTimer)
  fullscreenTimer = setTimeout(handleResize, 350)
}

// ==================== Live Update ====================
let updateTimer = null

const updateAllData = () => {
  // Simulate temperature variations based on load
  const loadVariation = Math.sin(Date.now() / 3600000) * 2
  const newSupplyTemp = parseFloat((16 + loadVariation + Math.random() * 2).toFixed(1))
  const newReturnTemp = parseFloat((newSupplyTemp + 10 + Math.random() * 3).toFixed(1))

  supplyTemp.value = newSupplyTemp
  returnTemp.value = newReturnTemp
  avgSupplyTemp.value = parseFloat(((avgSupplyTemp.value * 5 + newSupplyTemp) / 6).toFixed(1))
  deltaT.value = parseFloat((newReturnTemp - newSupplyTemp).toFixed(1))

  // Humidity varies with temperature
  const newHumidity = parseFloat((45 + loadVariation * 5 + (Math.random() - 0.5) * 5).toFixed(1))
  humidity.value = Math.min(65, Math.max(35, newHumidity))

  // Zone temperatures
  coldAisleTemp.value = parseFloat((newSupplyTemp + 1 + Math.random() * 2).toFixed(1))
  hotAisleTemp.value = parseFloat((newReturnTemp - 2 + Math.random() * 3).toFixed(1))

  // Cooling capacity and COP
  const totalCapacity = 200
  const usedCapacity = Math.min(totalCapacity, (24 - newSupplyTemp) * 30)
  coolingCapacity.value = parseFloat(usedCapacity.toFixed(1))
  const powerUsed = parseFloat((usedCapacity / 3.5 + Math.random() * 5).toFixed(1))
  totalPower.value = parseFloat((totalPower.value * 0.9 + powerUsed * 0.1).toFixed(1))
  cop.value = parseFloat((usedCapacity / powerUsed).toFixed(2))

  // CRAC status based on load
  cracStatus.value = [
    { name: 'CRAC 1', capacity: Math.min(100, Math.floor(usedCapacity / 2 + Math.random() * 10)), mode: usedCapacity > 100 ? 'Active' : 'Auto', color: '#34d399' },
    { name: 'CRAC 2', capacity: Math.min(100, Math.floor(usedCapacity / 3 + Math.random() * 10)), mode: usedCapacity > 80 ? 'Active' : 'Auto', color: '#34d399' },
    { name: 'CRAC 3', capacity: Math.min(100, Math.floor(usedCapacity / 4 + Math.random() * 10)), mode: usedCapacity > 120 ? 'Active' : 'Standby', color: '#60a5fa' },
    { name: 'CRAC 4', capacity: 0, mode: 'Standby', color: '#94a3b8' }
  ]

  // Fan speeds (roughly proportional to cooling demand)
  const fanSpeed = Math.min(100, Math.floor(40 + (usedCapacity / totalCapacity) * 60))
  const airflowPerFan = Math.floor(5000 + fanSpeed * 50)
  totalAirflow.value = fanStatus.value.reduce((sum, f) => sum + f.airflow, 0)

  fanStatus.value = [
    { label: 'Supply Fan 1', speed: fanSpeed, airflow: airflowPerFan, status: fanSpeed > 80 ? 'High' : 'Normal', statusClass: fanSpeed > 80 ? 'low' : 'normal' },
    { label: 'Supply Fan 2', speed: fanSpeed - 5, airflow: airflowPerFan - 250, status: fanSpeed > 80 ? 'High' : 'Normal', statusClass: fanSpeed > 80 ? 'low' : 'normal' },
    { label: 'Return Fan', speed: fanSpeed - 10, airflow: airflowPerFan - 500, status: 'Normal', statusClass: 'normal' }
  ]
  totalAirflow.value = fanStatus.value.reduce((sum, f) => sum + f.airflow, 0)

  // Update device health occasionally
  if (Math.random() > 0.95) {
    deviceHealth.value = [
      { subsystem: 'Compressors', status: usedCapacity > 180 ? 'warning' : 'normal', statusText: usedCapacity > 180 ? 'High Load' : 'All Running' },
      { subsystem: 'Fans', status: fanSpeed > 90 ? 'warning' : 'normal', statusText: fanSpeed > 90 ? 'High Speed' : 'Normal' },
      { subsystem: 'Refrigerant Circuit', status: 'normal', statusText: 'OK' },
      { subsystem: 'Humidifiers', status: humidity.value < 40 ? 'warning' : 'normal', statusText: humidity.value < 40 ? 'Low RH' : 'Standby' },
      { subsystem: 'Controllers', status: 'normal', statusText: 'Online' }
    ]
  }

  // Update tips occasionally
  if (Math.random() > 0.7) {
    const tipPool = [
      { icon: '❄️', title: 'Cooling Efficiency', desc: `Delta T: ${deltaT.value}°C`, priority: deltaT.value < 8 ? 'Low' : (deltaT.value > 14 ? 'High' : 'Optimal') },
      { icon: '💧', title: 'Humidity Control', desc: `RH: ${humidity.value}%`, priority: humidity.value < 40 ? 'Low' : (humidity.value > 60 ? 'High' : 'Optimal') },
      { icon: '🔧', title: 'Filter Status', desc: 'Check air filters regularly', priority: 'Info' }
    ]
    cracTips.value = tipPool.sort(() => Math.random() - 0.5).slice(0, 2)
  }

  // Update charts
  if (tempChart && capacityChart) {
    const now = new Date()
    const timeLabel = now.toTimeString().slice(0, 5)
    const lastHour = hourLabels.value[hourLabels.value.length - 1]

    if (lastHour !== timeLabel) {
      hourLabels.value.push(timeLabel)
      if (hourLabels.value.length > historyLength) hourLabels.value.shift()
      supplyTempHistory.value.push(supplyTemp.value)
      returnTempHistory.value.push(returnTemp.value)
      humidityHistory.value.push(humidity.value)
      if (supplyTempHistory.value.length > historyLength) supplyTempHistory.value.shift()
      if (returnTempHistory.value.length > historyLength) returnTempHistory.value.shift()
      if (humidityHistory.value.length > historyLength) humidityHistory.value.shift()

      tempChart.setOption({
        xAxis: { data: hourLabels.value },
        series: [{ data: supplyTempHistory.value }, { data: returnTempHistory.value }, { data: humidityHistory.value }]
      })
    }

    // Update capacity distribution
    const newDistribution = cracStatus.value.map(c => c.capacity)
    capacityChart.setOption({
      series: [{ data: newDistribution.map((v, i) => ({ value: v, name: `CRAC ${i + 1}` })) }]
    })
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
  supplyTemp.value = 17.5
  returnTemp.value = 27.8
  avgSupplyTemp.value = 17.2
  humidity.value = 52
  coolingCapacity.value = 85
  cop.value = 3.8
  coldAisleTemp.value = 19.2
  hotAisleTemp.value = 25.5
  deltaT.value = 10.3
  totalPower.value = 42.5

  initTempHistory()
  await initCharts()

  if (tempChart && capacityChart) {
    updateTimer = setInterval(updateAllData, 5000)
  }

  window.addEventListener('resize', handleResize)
  document.addEventListener('fullscreenchange', onFullscreenChange)

  routeWatch = watch(() => route.fullPath, async () => {
    initTempHistory()
    await initCharts()
    if (tempChart && capacityChart && !updateTimer) {
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