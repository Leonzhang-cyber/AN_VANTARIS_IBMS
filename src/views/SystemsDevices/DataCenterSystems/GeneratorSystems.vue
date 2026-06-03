<template>
  <div v-if="isPageLoaded" class="hvac-page">
    <div class="main-view">
      <div class="three-columns">
        <!-- Left Column: Key Metrics + System Status + Recent Events + Device Health -->
        <div class="col-left">
          <div class="title-row" v-if="isMobile">
            <h1 class="page-title">GENSET</h1>
            <span class="live-time">{{ currentTime }}</span>
          </div>
          <div class="card-img" v-if="isMobile">
            <img :src="securityImageUrl" alt="Generator 3D View" />
          </div>

          <!-- Key Metrics -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📈 Key Metrics</div>
            <div class="metrics-list">
              <div class="metric-row"><div class="metric-icon">⚡</div><div class="metric-label">Total Units</div><div class="metric-value">{{ totalUnits }}</div></div>
              <div class="metric-row"><div class="metric-icon">🔋</div><div class="metric-label">Total Capacity</div><div class="metric-value">{{ totalCapacity }} kVA</div></div>
              <div class="metric-row"><div class="metric-icon">📊</div><div class="metric-label">Current Load</div><div class="metric-value">{{ currentLoad }} kW</div></div>
              <div class="metric-row"><div class="metric-icon">🛢️</div><div class="metric-label">Fuel Level</div><div class="metric-value">{{ fuelLevel }}%</div></div>
              <div class="metric-row"><div class="metric-icon">🚨</div><div class="metric-label">Active Alarms</div><div class="metric-value">{{ activeAlarms }}</div></div>
            </div>
          </el-card>

          <!-- Generator Status -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">⚡ Generator Status</div>
            <div class="mode-list">
              <div class="mode-row" v-for="item in generatorStatus" :key="item.name">
                <div class="mode-name">{{ item.name }}</div>
                <div class="mode-bar-bg"><div class="mode-bar-fill" :style="{ width: item.load + '%', background: item.color }"></div></div>
                <div class="mode-value">{{ item.load }}%</div>
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
            <h1 class="page-title">GENSET</h1>
            <span class="live-time" v-if="isFullscreen">{{ currentTime }}</span>
          </div>
          <div class="card-img" v-if="!isMobile">
            <img :src="securityImageUrl" alt="Generator 3D View" />
          </div>
          <div class="cart-view">
            <!-- Power & Frequency Trend -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <div class="card-header">📊 Power & Frequency Trend (24h)</div>
              <div ref="powerChartRef" class="chart-box"></div>
            </el-card>
            <!-- Fuel Consumption -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <div class="card-header">🛢️ Fuel Consumption Trend</div>
              <div ref="fuelChartRef" class="chart-box"></div>
            </el-card>
          </div>
        </div>

        <!-- Right Column: KPIs + Engine Status + Fuel Status + Tips -->
        <div class="col-right">
          <!-- Generator KPIs -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📊 Generator KPIs</div>
            <div class="kpi-row"><span class="kpi-row-left">Output Voltage</span><strong>{{ outputVoltage }} V</strong><span class="trend stable">Normal</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Frequency</span><strong>{{ frequency }} Hz</strong><span class="trend" :class="Math.abs(frequency - 50) > 1 ? 'up' : 'stable'">{{ Math.abs(frequency - 50) > 1 ? 'Unstable' : 'Stable' }}</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Oil Pressure</span><strong>{{ oilPressure }} bar</strong><span class="trend" :class="oilPressure < 2 ? 'up' : 'stable'">{{ oilPressure < 2 ? 'Low' : 'Normal' }}</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Coolant Temp</span><strong>{{ coolantTemp }} °C</strong><span class="trend" :class="coolantTemp > 95 ? 'up' : 'stable'">{{ coolantTemp > 95 ? 'High' : 'Normal' }}</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Runtime Hours</span><strong>{{ runtimeHours }} hrs</strong><span class="trend stable">Since Last Service</span></div>
          </el-card>

          <!-- Engine Status Gauges -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🔧 Engine Status</div>
            <div class="gauges-grid">
              <div class="gauge-item"><el-progress type="dashboard" :percentage="engineLoad" :color="engineLoadColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ engineLoad }}%</span></template></el-progress><div class="gauge-label">Engine Load</div></div>
              <div class="gauge-item"><el-progress type="dashboard" :percentage="fuelEfficiency" :color="fuelEfficiencyColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ fuelEfficiency }}%</span></template></el-progress><div class="gauge-label">Fuel Efficiency</div></div>
              <div class="gauge-item"><el-progress type="dashboard" :percentage="batteryVoltage" :color="batteryVoltageColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ batteryVoltage }}V</span></template></el-progress><div class="gauge-label">Starter Battery</div></div>
              <div class="gauge-item"><el-progress type="dashboard" :percentage="coolingEfficiency" :color="coolingEfficiencyColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ coolingEfficiency }}%</span></template></el-progress><div class="gauge-label">Cooling Efficiency</div></div>
            </div>
          </el-card>

          <!-- Fuel Status -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🛢️ Fuel Status</div>
            <div class="setpoint-list">
              <div class="setpoint-row" v-for="item in fuelStatus" :key="item.label">
                <div class="sp-label">{{ item.label }}</div>
                <div class="sp-values"><span class="sp-set">Level: {{ item.level }}%</span><span class="sp-actual">Est. Runtime: {{ item.runtime }} hrs</span></div>
                <div class="sp-deviation" :class="item.statusClass">{{ item.status }}</div>
              </div>
            </div>
          </el-card>

          <!-- Generator Tips -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">💡 Generator Tips</div>
            <div class="tips-list">
              <div class="tip-item" v-for="(tip, idx) in generatorTips" :key="idx">
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
      <div class="loading-tip">Initializing Generator System</div>
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
  'Loading generator data...',
  'Checking fuel levels...',
  'Initializing engine sensors...',
  'Connecting to controllers...',
  'Starting dashboard...',
  'Almost ready...'
]

const preloadSecurityImage = () => {
  return new Promise((resolve) => {
    const img = new Image()
    const imageUrl = 'https://aegisnx.com/wp-content/uploads/2026/05/52013143424.png'
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

// ==================== Core Generator Data ====================
// Key metrics
const totalUnits = ref(3)
const totalCapacity = ref(1500)
const currentLoad = ref(0)
const fuelLevel = ref(0)
const activeAlarms = ref(1)

// Generator electrical parameters
const outputVoltage = ref(0)
const frequency = ref(0)
const oilPressure = ref(0)
const coolantTemp = ref(0)
const runtimeHours = ref(0)

// Engine status
const engineLoad = ref(0)
const fuelEfficiency = ref(0)
const batteryVoltage = ref(0)
const coolingEfficiency = ref(0)

// Generator Status
const generatorStatus = ref([
  { name: 'Gen 1 (Primary)', load: 0, status: 'Standby', color: '#34d399' },
  { name: 'Gen 2 (Backup)', load: 0, status: 'Standby', color: '#60a5fa' },
  { name: 'Gen 3 (Portable)', load: 0, status: 'Offline', color: '#94a3b8' }
])

// Recent events
const recentEvents = ref([
  { id: 1, severity: 'Success', location: 'Gen 1', description: 'Weekly self-test completed', timestamp: '2 hours ago' },
  { id: 2, severity: 'Warning', location: 'Gen 2', description: 'Low fuel level detected', timestamp: '4 hours ago' },
  { id: 3, severity: 'Info', location: 'Gen 1', description: 'Scheduled maintenance due in 50 hrs', timestamp: '8 hours ago' }
])

// Device health
const deviceHealth = ref([
  { subsystem: 'Engine Controller', status: 'normal', statusText: 'Online' },
  { subsystem: 'Fuel System', status: 'normal', statusText: 'OK' },
  { subsystem: 'Cooling System', status: 'normal', statusText: 'Active' },
  { subsystem: 'Exhaust System', status: 'normal', statusText: 'Normal' },
  { subsystem: 'ATS Controller', status: 'normal', statusText: 'Ready' }
])

// Fuel status
const fuelStatus = ref([
  { label: 'Main Tank', level: 0, runtime: 0, status: 'Normal', statusClass: 'normal' },
  { label: 'Day Tank', level: 0, runtime: 0, status: 'Normal', statusClass: 'normal' }
])

// Generator Tips
const generatorTips = ref([
  { icon: '🛢️', title: 'Fuel Level', desc: 'Main tank at optimal level', priority: 'Good' },
  { icon: '🔧', title: 'Maintenance', desc: 'Next service due in 100 hours', priority: 'Scheduled' }
])

// Color configurations
const engineLoadColor = [{ color: '#34d399', percentage: 60 }, { color: '#f59e0b', percentage: 80 }, { color: '#ef4444', percentage: 90 }]
const fuelEfficiencyColor = [{ color: '#34d399', percentage: 85 }, { color: '#f59e0b', percentage: 75 }, { color: '#ef4444', percentage: 65 }]
const batteryVoltageColor = [{ color: '#ef4444', percentage: 70 }, { color: '#f59e0b', percentage: 80 }, { color: '#34d399', percentage: 90 }]
const coolingEfficiencyColor = [{ color: '#ef4444', percentage: 70 }, { color: '#f59e0b', percentage: 80 }, { color: '#34d399', percentage: 90 }]

// ==================== Charts ====================
const powerChartRef = ref(null)
const fuelChartRef = ref(null)
let powerChart = null
let fuelChart = null

// Power history (24 hours)
const powerHistoryLength = 24
const powerHistory = ref([])
const freqHistory = ref([])
const hourLabels = ref([])

const initPowerHistory = () => {
  powerHistory.value = []
  freqHistory.value = []
  hourLabels.value = []
  const now = new Date()
  for (let i = powerHistoryLength - 1; i >= 0; i--) {
    const t = new Date(now - i * 3600000)
    hourLabels.value.push(t.toTimeString().slice(0, 5))
    powerHistory.value.push(parseFloat((200 + Math.random() * 600).toFixed(1)))
    freqHistory.value.push(parseFloat((49.8 + Math.random() * 0.6).toFixed(1)))
  }
}

// Fuel consumption history (30 days)
const fuelHistory = ref([850, 820, 790, 840, 810, 780, 830, 800, 770, 820, 790, 760, 810, 780, 750, 800, 770, 740, 790, 760, 730, 780, 750, 720, 770, 740, 710, 760, 730, 700])
const dayLabels = ref(Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`))

// Power chart option
const getPowerChartOption = () => {
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(15,25,45,0.9)', borderColor: '#3b82f6', textStyle: { color: '#e2e8f0' } },
    legend: { data: ['Power Output (kW)', 'Frequency (Hz)'], textStyle: { color: '#94a3b8', fontSize: 9 }, top: 0 },
    grid: { left: '0%', right: '0%', bottom: 0, top: 48, containLabel: true },
    xAxis: { type: 'category', data: hourLabels.value, axisLabel: { color: '#94a3b8', fontSize: 9, rotate: 30, interval: 3 }, axisLine: { lineStyle: { color: '#334155' } } },
    yAxis: [{ type: 'value', name: 'Power (kW)', nameTextStyle: { color: '#64748b', fontSize: 10 }, axisLabel: { color: '#94a3b8', fontSize: 10 }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } } },
      { type: 'value', name: 'Frequency (Hz)', nameTextStyle: { color: '#64748b', fontSize: 10 }, axisLabel: { color: '#94a3b8', fontSize: 10 }, splitLine: { show: false }, min: 49, max: 51 }],
    series: [
      { name: 'Power Output (kW)', type: 'line', data: powerHistory.value, smooth: true, symbol: 'circle', symbolSize: 4, lineStyle: { width: 2, color: '#fbbf24' }, areaStyle: { opacity: 0.3, color: '#fbbf24' } },
      { name: 'Frequency (Hz)', type: 'line', data: freqHistory.value, smooth: true, symbol: 'circle', symbolSize: 4, lineStyle: { width: 2, color: '#ef4444' }, areaStyle: { opacity: 0.3, color: '#ef4444' }, yAxisIndex: 1, markLine: { data: [{ yAxis: 49.5, name: 'Low', lineStyle: { color: '#f59e0b', type: 'dashed' } }, { yAxis: 50.5, name: 'High', lineStyle: { color: '#f59e0b', type: 'dashed' } }] } }
    ]
  }
}

// Fuel consumption chart option
const getFuelChartOption = () => {
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(15,25,45,0.9)', borderColor: '#3b82f6', textStyle: { color: '#e2e8f0' } },
    grid: { left: '0%', right: '0%', bottom: 0, top: 25, containLabel: true },
    xAxis: { type: 'category', data: dayLabels.value, axisLabel: { color: '#94a3b8', fontSize: 8, rotate: 45, interval: 5 }, axisLine: { lineStyle: { color: '#334155' } } },
    yAxis: { type: 'value', name: 'Fuel Consumption (L)', nameTextStyle: { color: '#64748b', fontSize: 10 }, axisLabel: { color: '#94a3b8', fontSize: 10 }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } } },
    series: [{
      type: 'bar', data: fuelHistory.value,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#60a5fa' },
      label: { show: false }
    }]
  }
}

// ==================== Chart Lifecycle ====================
const disposeCharts = () => {
  if (powerChart) { powerChart.dispose(); powerChart = null }
  if (fuelChart) { fuelChart.dispose(); fuelChart = null }
}

const initCharts = async () => {
  await nextTick()
  for (let attempt = 0; attempt < 5; attempt++) {
    await new Promise(resolve => setTimeout(resolve, 100))
    const powerDom = powerChartRef.value
    const fuelDom = fuelChartRef.value
    if (!powerDom || !fuelDom) continue
    if (powerDom.clientWidth === 0 || powerDom.clientHeight === 0) continue
    if (fuelDom.clientWidth === 0 || fuelDom.clientHeight === 0) continue
    disposeCharts()
    try {
      powerChart = echarts.init(powerDom)
      fuelChart = echarts.init(fuelDom)
      powerChart.setOption(getPowerChartOption())
      fuelChart.setOption(getFuelChartOption())
      return
    } catch (e) { console.error('[initCharts] Error:', e) }
  }
}

const handleResize = () => {
  powerChart?.resize()
  fuelChart?.resize()
}

let fullscreenTimer = null
const onFullscreenChange = () => {
  clearTimeout(fullscreenTimer)
  fullscreenTimer = setTimeout(handleResize, 350)
}

// ==================== Live Update ====================
let updateTimer = null

const updateAllData = () => {
  // Simulate load changes
  const newLoad = parseFloat((200 + Math.random() * 600).toFixed(1))
  currentLoad.value = newLoad
  engineLoad.value = Math.min(100, Math.floor((newLoad / 500) * 100))

  // Update generator status based on load
  generatorStatus.value = [
    { name: 'Gen 1 (Primary)', load: engineLoad.value, status: engineLoad.value > 0 ? 'Running' : 'Standby', color: engineLoad.value > 0 ? '#34d399' : '#60a5fa' },
    { name: 'Gen 2 (Backup)', load: engineLoad.value > 500 ? Math.floor(engineLoad.value * 0.6) : 0, status: engineLoad.value > 500 ? 'Running' : 'Standby', color: '#60a5fa' },
    { name: 'Gen 3 (Portable)', load: 0, status: 'Offline', color: '#94a3b8' }
  ]

  // Update electrical parameters (slight variations with load)
  outputVoltage.value = parseFloat((400 + (Math.random() - 0.5) * 5).toFixed(1))
  frequency.value = parseFloat((49.8 + Math.random() * 0.6 - (engineLoad.value / 1000) * 0.3).toFixed(1))
  oilPressure.value = parseFloat((3.5 + (engineLoad.value / 1000) * 1.5 + (Math.random() - 0.5) * 0.3).toFixed(1))
  coolantTemp.value = parseFloat((75 + (engineLoad.value / 500) * 15 + Math.random() * 3).toFixed(1))

  // Gradually increase runtime hours
  if (engineLoad.value > 0) {
    runtimeHours.value = parseFloat((runtimeHours.value + 0.2).toFixed(1))
  }

  // Update fuel efficiency (inversely related to load)
  fuelEfficiency.value = Math.min(95, Math.max(65, 85 - (engineLoad.value / 100) * 15 + (Math.random() - 0.5) * 3))
  fuelEfficiency.value = parseFloat(fuelEfficiency.value.toFixed(1))

  // Update battery voltage (should be around 12-14V for starter battery)
  batteryVoltage.value = parseFloat((12 + Math.random() * 2).toFixed(1))

  // Update cooling efficiency
  coolingEfficiency.value = Math.min(100, Math.max(60, 90 - (coolantTemp.value - 75) / 2))
  coolingEfficiency.value = parseFloat(coolingEfficiency.value.toFixed(1))

  // Update fuel level (slowly decreases when running)
  if (engineLoad.value > 0) {
    fuelLevel.value = Math.max(5, fuelLevel.value - Math.random() * 0.3)
    fuelLevel.value = parseFloat(fuelLevel.value.toFixed(1))
  }

  // Update fuel status
  const estimatedRuntimeMain = Math.floor((fuelLevel.value / 100) * 24)
  fuelStatus.value = [
    { label: 'Main Tank', level: fuelLevel.value, runtime: estimatedRuntimeMain, status: fuelLevel.value < 20 ? 'Low' : 'Normal', statusClass: fuelLevel.value < 20 ? 'low' : 'normal' },
    { label: 'Day Tank', level: parseFloat((85 + Math.random() * 10).toFixed(1)), runtime: Math.floor(8 + Math.random() * 4), status: 'Normal', statusClass: 'normal' }
  ]

  // Update device health occasionally
  if (Math.random() > 0.95) {
    deviceHealth.value = [
      { subsystem: 'Engine Controller', status: 'normal', statusText: 'Online' },
      { subsystem: 'Fuel System', status: fuelLevel.value < 15 ? 'warning' : 'normal', statusText: fuelLevel.value < 15 ? 'Low Fuel' : 'OK' },
      { subsystem: 'Cooling System', status: coolantTemp.value > 100 ? 'warning' : 'normal', statusText: coolantTemp.value > 100 ? 'Overheat' : 'Active' },
      { subsystem: 'Exhaust System', status: 'normal', statusText: 'Normal' },
      { subsystem: 'ATS Controller', status: 'normal', statusText: 'Ready' }
    ]
  }

  // Update tips occasionally
  if (Math.random() > 0.7) {
    const tipPool = [
      { icon: '🛢️', title: 'Fuel Level', desc: `Main tank: ${fuelLevel.value}% remaining`, priority: fuelLevel.value < 20 ? 'Critical' : 'Good' },
      { icon: '🌡️', title: 'Engine Temperature', desc: `Coolant: ${coolantTemp.value}°C`, priority: coolantTemp.value > 100 ? 'Warning' : 'Normal' },
      { icon: '🔧', title: 'Maintenance', desc: `Service due in ${Math.max(0, 500 - runtimeHours.value).toFixed(0)} hours`, priority: runtimeHours.value > 450 ? 'Due Soon' : 'OK' }
    ]
    generatorTips.value = tipPool.sort(() => Math.random() - 0.5).slice(0, 2)
  }

  // Update charts
  if (powerChart && fuelChart) {
    const now = new Date()
    const timeLabel = now.toTimeString().slice(0, 5)
    const lastHour = hourLabels.value[hourLabels.value.length - 1]

    if (lastHour !== timeLabel) {
      hourLabels.value.push(timeLabel)
      if (hourLabels.value.length > powerHistoryLength) hourLabels.value.shift()
      powerHistory.value.push(newLoad)
      freqHistory.value.push(frequency.value)
      if (powerHistory.value.length > powerHistoryLength) powerHistory.value.shift()
      if (freqHistory.value.length > powerHistoryLength) freqHistory.value.shift()

      powerChart.setOption({
        xAxis: { data: hourLabels.value },
        series: [{ data: powerHistory.value }, { data: freqHistory.value }]
      })
    }
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
  currentLoad.value = 350
  fuelLevel.value = 78
  engineLoad.value = 65
  fuelEfficiency.value = 82
  batteryVoltage.value = 12.8
  coolingEfficiency.value = 88
  outputVoltage.value = 401
  frequency.value = 50.1
  oilPressure.value = 4.2
  coolantTemp.value = 82
  runtimeHours.value = 125

  initPowerHistory()
  await initCharts()

  if (powerChart && fuelChart) {
    updateTimer = setInterval(updateAllData, 5000)
  }

  window.addEventListener('resize', handleResize)
  document.addEventListener('fullscreenchange', onFullscreenChange)

  routeWatch = watch(() => route.fullPath, async () => {
    initPowerHistory()
    await initCharts()
    if (powerChart && fuelChart && !updateTimer) {
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