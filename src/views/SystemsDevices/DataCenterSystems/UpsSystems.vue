<template>
  <div v-if="isPageLoaded" class="hvac-page">
    <div class="main-view">
      <div class="three-columns">
        <!-- Left Column: Key Metrics + System Status + Recent Events + Device Health -->
        <div class="col-left">
          <div class="title-row" v-if="isMobile">
            <h1 class="page-title">UPS</h1>
            <span class="live-time">{{ currentTime }}</span>
          </div>
          <div class="card-img" v-if="isMobile">
            <img :src="securityImageUrl" alt="UPS 3D View" />
          </div>

          <!-- Key Metrics -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📈 Key Metrics</div>
            <div class="metrics-list">
              <div class="metric-row"><div class="metric-icon">🔋</div><div class="metric-label">Total Units</div><div class="metric-value">{{ totalUnits }}</div></div>
              <div class="metric-row"><div class="metric-icon">⚡</div><div class="metric-label">Total Capacity</div><div class="metric-value">{{ totalCapacity }} kVA</div></div>
              <div class="metric-row"><div class="metric-icon">📊</div><div class="metric-label">Current Load</div><div class="metric-value">{{ currentLoad }} kW</div></div>
              <div class="metric-row"><div class="metric-icon">✅</div><div class="metric-label">Efficiency</div><div class="metric-value">{{ efficiency }}%</div></div>
              <div class="metric-row"><div class="metric-icon">🚨</div><div class="metric-label">Active Alarms</div><div class="metric-value">{{ activeAlarms }}</div></div>
            </div>
          </el-card>

          <!-- UPS Status -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">⚡ UPS Status</div>
            <div class="mode-list">
              <div class="mode-row" v-for="item in upsStatus" :key="item.name">
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
            <h1 class="page-title">UPS</h1>
            <span class="live-time" v-if="isFullscreen">{{ currentTime }}</span>
          </div>
          <div class="card-img" v-if="!isMobile">
            <img :src="securityImageUrl" alt="UPS 3D View" />
          </div>
          <div class="cart-view">
            <!-- Load & Battery Trend -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <div class="card-header">📊 Load & Battery Trend (24h)</div>
              <div ref="loadChartRef" class="chart-box"></div>
            </el-card>
            <!-- Battery Health -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <div class="card-header">🔋 Battery Health</div>
              <div ref="batteryChartRef" class="chart-box"></div>
            </el-card>
          </div>
        </div>

        <!-- Right Column: KPIs + Battery Status + Runtime + Tips -->
        <div class="col-right">
          <!-- UPS KPIs -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📊 UPS KPIs</div>
            <div class="kpi-row"><span class="kpi-row-left">Input Voltage</span><strong>{{ inputVoltage }} V</strong><span class="trend stable">Normal</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Output Voltage</span><strong>{{ outputVoltage }} V</strong><span class="trend stable">Stable</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Frequency</span><strong>{{ frequency }} Hz</strong><span class="trend up">50 Hz Target</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Power Factor</span><strong>{{ powerFactor }}</strong><span class="trend stable">0.95 Target</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Battery Temp</span><strong>{{ batteryTemp }} °C</strong><span class="trend" :class="batteryTemp > 30 ? 'up' : 'stable'">{{ batteryTemp > 30 ? 'High' : 'Normal' }}</span></div>
          </el-card>

          <!-- Battery Status Gauges -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🔋 Battery Status</div>
            <div class="gauges-grid">
              <div class="gauge-item"><el-progress type="dashboard" :percentage="batterySoC" :color="batterySoCColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ batterySoC }}%</span></template></el-progress><div class="gauge-label">State of Charge</div></div>
              <div class="gauge-item"><el-progress type="dashboard" :percentage="batteryHealth" :color="batteryHealthColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ batteryHealth }}%</span></template></el-progress><div class="gauge-label">State of Health</div></div>
              <div class="gauge-item"><el-progress type="dashboard" :percentage="estimatedRuntime" :color="runtimeColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ estimatedRuntime }} min</span></template></el-progress><div class="gauge-label">Est. Runtime</div></div>
              <div class="gauge-item"><el-progress type="dashboard" :percentage="loadPercent" :color="loadColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ loadPercent }}%</span></template></el-progress><div class="gauge-label">Load Level</div></div>
            </div>
          </el-card>

          <!-- Runtime Details -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">⏱️ Runtime Details</div>
            <div class="setpoint-list">
              <div class="setpoint-row" v-for="item in runtimeDetails" :key="item.label">
                <div class="sp-label">{{ item.label }}</div>
                <div class="sp-values"><span class="sp-set">Current: {{ item.current }}</span><span class="sp-actual">Full: {{ item.full }}</span></div>
                <div class="sp-deviation" :class="item.statusClass">{{ item.status }}</div>
              </div>
            </div>
          </el-card>

          <!-- UPS Tips -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">💡 UPS Tips</div>
            <div class="tips-list">
              <div class="tip-item" v-for="(tip, idx) in upsTips" :key="idx">
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
      <div class="loading-tip">Initializing UPS System</div>
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
  'Loading UPS data...',
  'Checking battery banks...',
  'Initializing modules...',
  'Connecting to UPS controllers...',
  'Starting dashboard...',
  'Almost ready...'
]

const preloadSecurityImage = () => {
  return new Promise((resolve) => {
    const img = new Image()
    const imageUrl = 'https://aegisnx.com/wp-content/uploads/2026/05/5230123123.png'
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

// ==================== Core UPS Data ====================
// Key metrics
const totalUnits = ref(4)
const totalCapacity = ref(800)
const currentLoad = ref(0)
const efficiency = ref(0)
const activeAlarms = ref(1)

// UPS electrical parameters
const inputVoltage = ref(0)
const outputVoltage = ref(0)
const frequency = ref(0)
const powerFactor = ref(0)
const batteryTemp = ref(0)

// Battery status
const batterySoC = ref(0)
const batteryHealth = ref(0)
const estimatedRuntime = ref(0)
const loadPercent = ref(0)

// UPS Status
const upsStatus = ref([
  { name: 'UPS Unit 1', load: 0, status: 'Online', color: '#34d399' },
  { name: 'UPS Unit 2', load: 0, status: 'Online', color: '#34d399' },
  { name: 'UPS Unit 3', load: 0, status: 'Standby', color: '#60a5fa' },
  { name: 'UPS Unit 4', load: 0, status: 'Online', color: '#34d399' }
])

// Recent events
const recentEvents = ref([
  { id: 1, severity: 'Success', location: 'UPS Unit 1', description: 'Automatic self-test completed', timestamp: '2 hours ago' },
  { id: 2, severity: 'Warning', location: 'UPS Unit 2', description: 'Battery temperature elevated', timestamp: '4 hours ago' },
  { id: 3, severity: 'Info', location: 'UPS Unit 3', description: 'Input voltage fluctuation detected', timestamp: '8 hours ago' }
])

// Device health
const deviceHealth = ref([
  { subsystem: 'UPS Controllers', status: 'normal', statusText: 'Online' },
  { subsystem: 'Battery Banks', status: 'normal', statusText: 'Healthy' },
  { subsystem: 'Cooling Fans', status: 'normal', statusText: 'Running' },
  { subsystem: 'Input Breakers', status: 'normal', statusText: 'Closed' },
  { subsystem: 'Output Breakers', status: 'normal', statusText: 'Closed' }
])

// Runtime details
const runtimeDetails = ref([
  { label: 'Current Load', current: '0 kW', full: '200 kW', status: 'Normal', statusClass: 'normal' },
  { label: 'Est. Runtime (Full Load)', current: '12 min', full: '12 min', status: 'Normal', statusClass: 'normal' },
  { label: 'Est. Runtime (Half Load)', current: '28 min', full: '28 min', status: 'Normal', statusClass: 'normal' }
])

// UPS Tips
const upsTips = ref([
  { icon: '🔋', title: 'Battery Health', desc: 'Annual capacity test recommended next month', priority: 'Scheduled' },
  { icon: '🌡️', title: 'Thermal Management', desc: 'Ambient temperature within optimal range', priority: 'Optimal' }
])

// Color configurations
const batterySoCColor = [{ color: '#34d399', percentage: 50 }, { color: '#f59e0b', percentage: 30 }, { color: '#ef4444', percentage: 20 }]
const batteryHealthColor = [{ color: '#34d399', percentage: 80 }, { color: '#f59e0b', percentage: 60 }, { color: '#ef4444', percentage: 50 }]
const runtimeColor = [{ color: '#34d399', percentage: 50 }, { color: '#f59e0b', percentage: 30 }, { color: '#ef4444', percentage: 15 }]
const loadColor = [{ color: '#34d399', percentage: 60 }, { color: '#f59e0b', percentage: 80 }, { color: '#ef4444', percentage: 90 }]

// ==================== Charts ====================
const loadChartRef = ref(null)
const batteryChartRef = ref(null)
let loadChart = null
let batteryChart = null

// Load history (24 hours)
const loadHistoryLength = 24
const loadHistory = ref([])
const batteryHistory = ref([])
const hourLabels = ref([])

const initLoadHistory = () => {
  loadHistory.value = []
  batteryHistory.value = []
  hourLabels.value = []
  const now = new Date()
  for (let i = loadHistoryLength - 1; i >= 0; i--) {
    const t = new Date(now - i * 3600000)
    hourLabels.value.push(t.toTimeString().slice(0, 5))
    loadHistory.value.push(parseFloat((60 + Math.random() * 80).toFixed(1)))
    batteryHistory.value.push(parseFloat((70 + Math.random() * 25).toFixed(1)))
  }
}

// Load chart option
const getLoadChartOption = () => {
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(15,25,45,0.9)', borderColor: '#3b82f6', textStyle: { color: '#e2e8f0' } },
    legend: { data: ['Load (kW)', 'Battery SoC (%)'], textStyle: { color: '#94a3b8', fontSize: 9 }, top: 0 },
    grid: { left: '0%', right: '0%', bottom: 0, top: 48, containLabel: true },
    xAxis: { type: 'category', data: hourLabels.value, axisLabel: { color: '#94a3b8', fontSize: 9, rotate: 30, interval: 3 }, axisLine: { lineStyle: { color: '#334155' } } },
    yAxis: [{ type: 'value', name: 'Load (kW)', nameTextStyle: { color: '#64748b', fontSize: 10 }, axisLabel: { color: '#94a3b8', fontSize: 10 }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } } },
      { type: 'value', name: 'Battery SoC (%)', nameTextStyle: { color: '#64748b', fontSize: 10 }, axisLabel: { color: '#94a3b8', fontSize: 10 }, splitLine: { show: false }, min: 0, max: 100 }],
    series: [
      { name: 'Load (kW)', type: 'line', data: loadHistory.value, smooth: true, symbol: 'circle', symbolSize: 4, lineStyle: { width: 2, color: '#fbbf24' }, areaStyle: { opacity: 0.3, color: '#fbbf24' } },
      { name: 'Battery SoC (%)', type: 'line', data: batteryHistory.value, smooth: true, symbol: 'circle', symbolSize: 4, lineStyle: { width: 2, color: '#34d399' }, areaStyle: { opacity: 0.3, color: '#34d399' }, yAxisIndex: 1 }
    ]
  }
}

// Battery health chart option
const getBatteryChartOption = () => {
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(15,25,45,0.9)', borderColor: '#3b82f6', textStyle: { color: '#e2e8f0' } },
    grid: { left: '0%', right: '0%', bottom: 0, top: 25, containLabel: true },
    xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'], axisLabel: { color: '#94a3b8', fontSize: 10 }, axisLine: { lineStyle: { color: '#334155' } } },
    yAxis: { type: 'value', name: 'Capacity (%)', nameTextStyle: { color: '#64748b', fontSize: 10 }, axisLabel: { color: '#94a3b8', fontSize: 10 }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } }, min: 70, max: 100 },
    series: [{
      type: 'line', data: [98, 97, 96, 95, 94, 93], smooth: true,
      lineStyle: { width: 2, color: '#60a5fa' }, areaStyle: { opacity: 0.3, color: '#60a5fa' },
      markLine: { data: [{ yAxis: 80, name: 'Replacement Threshold', lineStyle: { color: '#ef4444', type: 'dashed' } }] }
    }]
  }
}

// ==================== Chart Lifecycle ====================
const disposeCharts = () => {
  if (loadChart) { loadChart.dispose(); loadChart = null }
  if (batteryChart) { batteryChart.dispose(); batteryChart = null }
}

const initCharts = async () => {
  await nextTick()
  for (let attempt = 0; attempt < 5; attempt++) {
    await new Promise(resolve => setTimeout(resolve, 100))
    const loadDom = loadChartRef.value
    const batteryDom = batteryChartRef.value
    if (!loadDom || !batteryDom) continue
    if (loadDom.clientWidth === 0 || loadDom.clientHeight === 0) continue
    if (batteryDom.clientWidth === 0 || batteryDom.clientHeight === 0) continue
    disposeCharts()
    try {
      loadChart = echarts.init(loadDom)
      batteryChart = echarts.init(batteryDom)
      loadChart.setOption(getLoadChartOption())
      batteryChart.setOption(getBatteryChartOption())
      return
    } catch (e) { console.error('[initCharts] Error:', e) }
  }
}

const handleResize = () => {
  loadChart?.resize()
  batteryChart?.resize()
}

let fullscreenTimer = null
const onFullscreenChange = () => {
  clearTimeout(fullscreenTimer)
  fullscreenTimer = setTimeout(handleResize, 350)
}

// ==================== Live Update ====================
let updateTimer = null

const updateAllData = () => {
  // Generate random load between 40% and 85%
  const newLoadPercent = parseFloat((40 + Math.random() * 45).toFixed(1))
  loadPercent.value = newLoadPercent
  currentLoad.value = parseFloat((newLoadPercent * 2).toFixed(1))
  efficiency.value = parseFloat((92 + Math.random() * 4).toFixed(1))

  // Update UPS electrical parameters
  inputVoltage.value = parseFloat((215 + Math.random() * 10).toFixed(1))
  outputVoltage.value = parseFloat((218 + Math.random() * 6).toFixed(1))
  frequency.value = parseFloat((49.8 + Math.random() * 0.6).toFixed(1))
  powerFactor.value = parseFloat((0.92 + Math.random() * 0.05).toFixed(2))
  batteryTemp.value = parseFloat((25 + Math.random() * 8).toFixed(1))

  // Update battery parameters
  batterySoC.value = Math.min(100, Math.max(20, batterySoC.value + (Math.random() - 0.5) * 3))
  batterySoC.value = parseFloat(batterySoC.value.toFixed(1))
  batteryHealth.value = parseFloat((85 + Math.random() * 10).toFixed(1))
  estimatedRuntime.value = Math.floor(10 + (batterySoC.value / 100) * 20)

  // Update UPS status based on load
  upsStatus.value = [
    { name: 'UPS Unit 1', load: loadPercent.value, status: loadPercent.value > 70 ? 'High Load' : 'Online', color: loadPercent.value > 70 ? '#f59e0b' : '#34d399' },
    { name: 'UPS Unit 2', load: parseFloat((loadPercent.value - 5 + Math.random() * 10).toFixed(1)), status: 'Online', color: '#34d399' },
    { name: 'UPS Unit 3', load: parseFloat((30 + Math.random() * 30).toFixed(1)), status: loadPercent.value > 80 ? 'Standby' : 'Online', color: '#60a5fa' },
    { name: 'UPS Unit 4', load: parseFloat((loadPercent.value - 10 + Math.random() * 10).toFixed(1)), status: 'Online', color: '#34d399' }
  ]

  // Update runtime details
  runtimeDetails.value = [
    { label: 'Current Load', current: `${currentLoad.value} kW`, full: '200 kW', status: loadPercent.value > 85 ? 'High' : 'Normal', statusClass: loadPercent.value > 85 ? 'high' : 'normal' },
    { label: 'Est. Runtime (Full Load)', current: `${estimatedRuntime.value} min`, full: '12 min', status: 'Normal', statusClass: 'normal' },
    { label: 'Est. Runtime (Half Load)', current: `${Math.floor(estimatedRuntime.value * 2.2)} min`, full: '28 min', status: 'Normal', statusClass: 'normal' }
  ]

  // Update device health occasionally
  if (Math.random() > 0.95) {
    deviceHealth.value = [
      { subsystem: 'UPS Controllers', status: 'normal', statusText: 'Online' },
      { subsystem: 'Battery Banks', status: batteryHealth.value < 80 ? 'warning' : 'normal', statusText: batteryHealth.value < 80 ? 'Check' : 'Healthy' },
      { subsystem: 'Cooling Fans', status: 'normal', statusText: 'Running' },
      { subsystem: 'Input Breakers', status: 'normal', statusText: 'Closed' },
      { subsystem: 'Output Breakers', status: 'normal', statusText: 'Closed' }
    ]
  }

  // Update tips occasionally
  if (Math.random() > 0.7) {
    const tipPool = [
      { icon: '🔋', title: 'Battery Health', desc: `Current capacity: ${batteryHealth.value}%`, priority: batteryHealth.value < 80 ? 'Attention' : 'Good' },
      { icon: '🌡️', title: 'Thermal Management', desc: `Battery temp: ${batteryTemp.value}°C`, priority: batteryTemp.value > 32 ? 'Warning' : 'Normal' },
      { icon: '⚡', title: 'Load Distribution', desc: `Total load: ${currentLoad.value} kW`, priority: loadPercent.value > 85 ? 'High Load' : 'Optimal' }
    ]
    upsTips.value = tipPool.sort(() => Math.random() - 0.5).slice(0, 2)
  }

  // Update charts
  if (loadChart && batteryChart) {
    const now = new Date()
    const timeLabel = now.toTimeString().slice(0, 5)
    const lastHour = hourLabels.value[hourLabels.value.length - 1]

    if (lastHour !== timeLabel) {
      hourLabels.value.push(timeLabel)
      if (hourLabels.value.length > loadHistoryLength) hourLabels.value.shift()
      loadHistory.value.push(parseFloat((60 + Math.random() * 80).toFixed(1)))
      batteryHistory.value.push(batterySoC.value)
      if (loadHistory.value.length > loadHistoryLength) loadHistory.value.shift()
      if (batteryHistory.value.length > loadHistoryLength) batteryHistory.value.shift()

      loadChart.setOption({
        xAxis: { data: hourLabels.value },
        series: [{ data: loadHistory.value }, { data: batteryHistory.value }]
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
  batterySoC.value = 85
  batteryHealth.value = 92
  loadPercent.value = 65
  currentLoad.value = 130
  efficiency.value = 94.5
  inputVoltage.value = 220
  outputVoltage.value = 220
  frequency.value = 50.0
  powerFactor.value = 0.95
  batteryTemp.value = 28
  estimatedRuntime.value = 18

  initLoadHistory()
  await initCharts()

  if (loadChart && batteryChart) {
    updateTimer = setInterval(updateAllData, 5000)
  }

  window.addEventListener('resize', handleResize)
  document.addEventListener('fullscreenchange', onFullscreenChange)

  routeWatch = watch(() => route.fullPath, async () => {
    initLoadHistory()
    await initCharts()
    if (loadChart && batteryChart && !updateTimer) {
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