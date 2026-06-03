<template>
  <div v-if="isPageLoaded" class="hvac-page">
    <div class="main-view">
      <div class="three-columns">
        <!-- Left Column: Key Metrics + System Status + Recent Events + Device Health -->
        <div class="col-left">
          <div class="title-row" v-if="isMobile">
            <h1 class="page-title">CHILLER</h1>
            <span class="live-time">{{ currentTime }}</span>
          </div>
          <div class="card-img" v-if="isMobile">
            <img :src="securityImageUrl" alt="Chiller 3D View" />
          </div>

          <!-- Key Metrics -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📈 Key Metrics</div>
            <div class="metrics-list">
              <div class="metric-row"><div class="metric-icon">❄️</div><div class="metric-label">Total Units</div><div class="metric-value">{{ totalUnits }}</div></div>
              <div class="metric-row"><div class="metric-icon">⚡</div><div class="metric-label">Total Capacity</div><div class="metric-value">{{ totalCapacity }} kW</div></div>
              <div class="metric-row"><div class="metric-icon">📊</div><div class="metric-label">Current Load</div><div class="metric-value">{{ currentLoad }} kW</div></div>
              <div class="metric-row"><div class="metric-icon">💧</div><div class="metric-label">COP</div><div class="metric-value">{{ cop }}</div></div>
              <div class="metric-row"><div class="metric-icon">🚨</div><div class="metric-label">Active Alarms</div><div class="metric-value">{{ activeAlarms }}</div></div>
            </div>
          </el-card>

          <!-- Chiller Status -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">❄️ Chiller Status</div>
            <div class="mode-list">
              <div class="mode-row" v-for="item in chillerStatus" :key="item.name">
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
            <h1 class="page-title">CHILLER</h1>
            <span class="live-time" v-if="isFullscreen">{{ currentTime }}</span>
          </div>
          <div class="card-img" v-if="!isMobile">
            <img :src="securityImageUrl" alt="Chiller 3D View" />
          </div>
          <div class="cart-view">
            <!-- Load & COP Trend -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <div class="card-header">📊 Load & COP Trend (24h)</div>
              <div ref="loadChartRef" class="chart-box"></div>
            </el-card>
            <!-- Capacity Distribution -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <div class="card-header">❄️ Capacity Distribution</div>
              <div ref="capacityChartRef" class="chart-box"></div>
            </el-card>
          </div>
        </div>

        <!-- Right Column: KPIs + Water Temps + Compressor Status + Tips -->
        <div class="col-right">
          <!-- Chiller KPIs -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📊 Chiller KPIs</div>
            <div class="kpi-row"><span class="kpi-row-left">Chilled Water Supply</span><strong>{{ chilledWaterSupply }}°C</strong><span class="trend stable">Setpoint: 7°C</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Chilled Water Return</span><strong>{{ chilledWaterReturn }}°C</strong><span class="trend" :class="deltaChilled > 6 ? 'up' : 'stable'">{{ deltaChilled }}°C Δ</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Condenser Water Supply</span><strong>{{ condenserWaterSupply }}°C</strong><span class="trend stable">Ambient +5°C</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Condenser Water Return</span><strong>{{ condenserWaterReturn }}°C</strong><span class="trend" :class="deltaCondenser > 5 ? 'up' : 'stable'">{{ deltaCondenser }}°C Δ</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Power Consumption</span><strong>{{ powerConsumption }} kW</strong><span class="trend" :class="powerConsumption > 300 ? 'up' : 'stable'">{{ ((powerConsumption / currentLoad) * 100).toFixed(1) }}% of load</span></div>
          </el-card>

          <!-- Water Temperature Gauges -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">💧 Water Temperatures</div>
            <div class="gauges-grid">
              <div class="gauge-item"><el-progress type="dashboard" :percentage="chilledWaterSupply" :color="waterTempColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ chilledWaterSupply }}°C</span></template></el-progress><div class="gauge-label">CHW Supply</div></div>
              <div class="gauge-item"><el-progress type="dashboard" :percentage="chilledWaterReturn" :color="waterTempColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ chilledWaterReturn }}°C</span></template></el-progress><div class="gauge-label">CHW Return</div></div>
              <div class="gauge-item"><el-progress type="dashboard" :percentage="condenserWaterSupply" :color="condenserColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ condenserWaterSupply }}°C</span></template></el-progress><div class="gauge-label">CDW Supply</div></div>
              <div class="gauge-item"><el-progress type="dashboard" :percentage="condenserWaterReturn" :color="condenserColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ condenserWaterReturn }}°C</span></template></el-progress><div class="gauge-label">CDW Return</div></div>
            </div>
          </el-card>

          <!-- Compressor Status -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🔧 Compressor Status</div>
            <div class="setpoint-list">
              <div class="setpoint-row" v-for="item in compressorStatus" :key="item.label">
                <div class="sp-label">{{ item.label }}</div>
                <div class="sp-values"><span class="sp-set">Load: {{ item.load }}%</span><span class="sp-actual">Current: {{ item.current }} A</span></div>
                <div class="sp-deviation" :class="item.statusClass">{{ item.status }}</div>
              </div>
            </div>
          </el-card>

          <!-- Chiller Tips -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">💡 Chiller Tips</div>
            <div class="tips-list">
              <div class="tip-item" v-for="(tip, idx) in chillerTips" :key="idx">
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
      <div class="loading-tip">Initializing Chiller System</div>
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
  'Loading chiller data...',
  'Checking refrigerant circuits...',
  'Initializing compressors...',
  'Connecting to controllers...',
  'Starting dashboard...',
  'Almost ready...'
]

const preloadSecurityImage = () => {
  return new Promise((resolve) => {
    const img = new Image()
    const imageUrl = 'https://aegisnx.com/wp-content/uploads/2026/05/Figure-1-chiller-cooling-system.png'
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

// ==================== Core Chiller Data ====================
// Key metrics
const totalUnits = ref(4)
const totalCapacity = ref(1200)
const currentLoad = ref(0)
const cop = ref(0)
const activeAlarms = ref(1)

// Water temperatures
const chilledWaterSupply = ref(0)
const chilledWaterReturn = ref(0)
const deltaChilled = ref(0)
const condenserWaterSupply = ref(0)
const condenserWaterReturn = ref(0)
const deltaCondenser = ref(0)

// Power
const powerConsumption = ref(0)

// Chiller Status
const chillerStatus = ref([
  { name: 'Chiller 1', load: 0, status: 'Running', color: '#34d399' },
  { name: 'Chiller 2', load: 0, status: 'Running', color: '#34d399' },
  { name: 'Chiller 3', load: 0, status: 'Standby', color: '#60a5fa' },
  { name: 'Chiller 4', load: 0, status: 'Offline', color: '#94a3b8' }
])

// Recent events
const recentEvents = ref([
  { id: 1, severity: 'Success', location: 'Chiller 1', description: 'Capacity modulation optimized', timestamp: '2 hours ago' },
  { id: 2, severity: 'Warning', location: 'Chiller 3', description: 'High refrigerant pressure', timestamp: '4 hours ago' },
  { id: 3, severity: 'Info', location: 'Chiller 2', description: 'Scheduled maintenance due', timestamp: '8 hours ago' }
])

// Device health
const deviceHealth = ref([
  { subsystem: 'Compressors', status: 'normal', statusText: 'All Running' },
  { subsystem: 'Evaporators', status: 'normal', statusText: 'Clean' },
  { subsystem: 'Condensers', status: 'normal', statusText: 'Optimal' },
  { subsystem: 'Refrigerant Circuit', status: 'normal', statusText: 'Sealed' },
  { subsystem: 'Controllers', status: 'normal', statusText: 'Online' }
])

// Compressor status
const compressorStatus = ref([
  { label: 'Compressor A1', load: 0, current: 0, status: 'Normal', statusClass: 'normal' },
  { label: 'Compressor A2', load: 0, current: 0, status: 'Normal', statusClass: 'normal' },
  { label: 'Compressor B1', load: 0, current: 0, status: 'Standby', statusClass: 'normal' }
])

// Chiller Tips
const chillerTips = ref([
  { icon: '❄️', title: 'COP Performance', desc: 'Current COP: 5.2 - Optimal range', priority: 'Good' },
  { icon: '💧', title: 'Delta T', desc: 'Chilled water ΔT within design', priority: 'Optimal' }
])

// Color configurations
const waterTempColor = [{ color: '#60a5fa', percentage: 7 }, { color: '#f59e0b', percentage: 9 }, { color: '#ef4444', percentage: 12 }]
const condenserColor = [{ color: '#34d399', percentage: 30 }, { color: '#f59e0b', percentage: 35 }, { color: '#ef4444', percentage: 40 }]

// ==================== Charts ====================
const loadChartRef = ref(null)
const capacityChartRef = ref(null)
let loadChart = null
let capacityChart = null

// Load history (24 hours)
const historyLength = 24
const loadHistory = ref([])
const copHistory = ref([])
const hourLabels = ref([])

const initLoadHistory = () => {
  loadHistory.value = []
  copHistory.value = []
  hourLabels.value = []
  const now = new Date()
  for (let i = historyLength - 1; i >= 0; i--) {
    const t = new Date(now - i * 3600000)
    hourLabels.value.push(t.toTimeString().slice(0, 5))
    loadHistory.value.push(parseFloat((300 + Math.random() * 400).toFixed(1)))
    copHistory.value.push(parseFloat((4.8 + Math.random() * 1).toFixed(2)))
  }
}

// Capacity distribution data
const capacityDistribution = ref([35, 30, 20, 15])

// Load chart option
const getLoadChartOption = () => {
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(15,25,45,0.9)', borderColor: '#3b82f6', textStyle: { color: '#e2e8f0' } },
    legend: { data: ['Cooling Load (kW)', 'COP'], textStyle: { color: '#94a3b8', fontSize: 9 }, top: 0 },
    grid: { left: '0%', right: '0%', bottom: 0, top: 48, containLabel: true },
    xAxis: { type: 'category', data: hourLabels.value, axisLabel: { color: '#94a3b8', fontSize: 9, rotate: 30, interval: 3 }, axisLine: { lineStyle: { color: '#334155' } } },
    yAxis: [{ type: 'value', name: 'Load (kW)', nameTextStyle: { color: '#64748b', fontSize: 10 }, axisLabel: { color: '#94a3b8', fontSize: 10 }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } } },
      { type: 'value', name: 'COP', nameTextStyle: { color: '#64748b', fontSize: 10 }, axisLabel: { color: '#94a3b8', fontSize: 10 }, splitLine: { show: false }, min: 3, max: 7 }],
    series: [
      { name: 'Cooling Load (kW)', type: 'line', data: loadHistory.value, smooth: true, symbol: 'circle', symbolSize: 4, lineStyle: { width: 2, color: '#fbbf24' }, areaStyle: { opacity: 0.3, color: '#fbbf24' } },
      { name: 'COP', type: 'line', data: copHistory.value, smooth: true, symbol: 'circle', symbolSize: 4, lineStyle: { width: 2, color: '#34d399' }, areaStyle: { opacity: 0.3, color: '#34d399' }, yAxisIndex: 1 }
    ]
  }
}

// Capacity distribution pie chart option
const getCapacityChartOption = () => {
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', backgroundColor: 'rgba(15,25,45,0.9)', borderColor: '#3b82f6', textStyle: { color: '#e2e8f0' } },
    legend: { orient: 'vertical', left: 'left', textStyle: { color: '#94a3b8', fontSize: 10 } },
    series: [{
      type: 'pie', radius: '55%', center: ['50%', '50%'],
      data: [
        { value: 35, name: 'Chiller 1', itemStyle: { color: '#fbbf24' } },
        { value: 30, name: 'Chiller 2', itemStyle: { color: '#60a5fa' } },
        { value: 20, name: 'Chiller 3', itemStyle: { color: '#34d399' } },
        { value: 15, name: 'Chiller 4', itemStyle: { color: '#f97316' } }
      ],
      label: { show: true, formatter: '{b}: {d}%', fontSize: 10, color: '#cbd5e1' }
    }]
  }
}

// ==================== Chart Lifecycle ====================
const disposeCharts = () => {
  if (loadChart) { loadChart.dispose(); loadChart = null }
  if (capacityChart) { capacityChart.dispose(); capacityChart = null }
}

const initCharts = async () => {
  await nextTick()
  for (let attempt = 0; attempt < 5; attempt++) {
    await new Promise(resolve => setTimeout(resolve, 100))
    const loadDom = loadChartRef.value
    const capacityDom = capacityChartRef.value
    if (!loadDom || !capacityDom) continue
    if (loadDom.clientWidth === 0 || loadDom.clientHeight === 0) continue
    if (capacityDom.clientWidth === 0 || capacityDom.clientHeight === 0) continue
    disposeCharts()
    try {
      loadChart = echarts.init(loadDom)
      capacityChart = echarts.init(capacityDom)
      loadChart.setOption(getLoadChartOption())
      capacityChart.setOption(getCapacityChartOption())
      return
    } catch (e) { console.error('[initCharts] Error:', e) }
  }
}

const handleResize = () => {
  loadChart?.resize()
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
  // Simulate cooling load based on outdoor temperature (simulated)
  const hour = new Date().getHours()
  const outdoorTemp = 22 + Math.sin(hour / 24 * Math.PI * 2) * 8
  const baseLoad = 300 + (outdoorTemp - 22) * 30
  const newLoad = Math.min(900, Math.max(200, baseLoad + (Math.random() - 0.5) * 50))

  currentLoad.value = parseFloat(newLoad.toFixed(1))

  // COP varies with load (optimal at 60-80% load)
  const loadPercent = newLoad / 900 * 100
  let newCOP = 5.2
  if (loadPercent < 40) newCOP = 4.2 + (loadPercent / 40) * 1
  else if (loadPercent > 90) newCOP = 5.5 - (loadPercent - 90) / 10 * 1
  else newCOP = 5.2 + (loadPercent - 60) / 20 * 0.3
  cop.value = parseFloat(newCOP.toFixed(2))

  // Chilled water temperatures
  const newChilledSupply = parseFloat((6.5 + Math.random() * 1).toFixed(1))
  const newChilledReturn = parseFloat((newChilledSupply + 5 + newLoad / 200 + Math.random() * 1).toFixed(1))
  chilledWaterSupply.value = newChilledSupply
  chilledWaterReturn.value = newChilledReturn
  deltaChilled.value = parseFloat((newChilledReturn - newChilledSupply).toFixed(1))

  // Condenser water temperatures (affected by outdoor temp)
  const newCondenserSupply = parseFloat((outdoorTemp + 3 + Math.random() * 2).toFixed(1))
  const newCondenserReturn = parseFloat((newCondenserSupply + 4 + newLoad / 300 + Math.random() * 1).toFixed(1))
  condenserWaterSupply.value = newCondenserSupply
  condenserWaterReturn.value = newCondenserReturn
  deltaCondenser.value = parseFloat((newCondenserReturn - newCondenserSupply).toFixed(1))

  // Power consumption
  powerConsumption.value = parseFloat((newLoad / newCOP + Math.random() * 10).toFixed(1))

  // Chiller status based on load
  const chillerCount = Math.ceil(newLoad / 300)
  chillerStatus.value = [
    { name: 'Chiller 1', load: Math.min(100, Math.floor((newLoad / 300) * 100)), status: chillerCount >= 1 ? 'Running' : 'Standby', color: chillerCount >= 1 ? '#34d399' : '#60a5fa' },
    { name: 'Chiller 2', load: Math.min(100, Math.floor((Math.max(0, newLoad - 300) / 300) * 100)), status: chillerCount >= 2 ? 'Running' : 'Standby', color: chillerCount >= 2 ? '#34d399' : '#60a5fa' },
    { name: 'Chiller 3', load: Math.min(100, Math.floor((Math.max(0, newLoad - 600) / 300) * 100)), status: chillerCount >= 3 ? 'Running' : 'Standby', color: chillerCount >= 3 ? '#34d399' : '#60a5fa' },
    { name: 'Chiller 4', load: 0, status: 'Offline', color: '#94a3b8' }
  ]

  // Compressor status
  compressorStatus.value = [
    { label: 'Compressor A1', load: Math.min(100, Math.floor(newLoad / 450 * 100)), current: parseFloat((100 + newLoad / 9 + Math.random() * 20).toFixed(1)), status: newLoad > 200 ? 'Running' : 'Stopped', statusClass: newLoad > 200 ? 'normal' : 'low' },
    { label: 'Compressor A2', load: Math.min(100, Math.floor(Math.max(0, newLoad - 450) / 450 * 100)), current: parseFloat((50 + Math.max(0, newLoad - 450) / 9 + Math.random() * 10).toFixed(1)), status: newLoad > 450 ? 'Running' : 'Stopped', statusClass: newLoad > 450 ? 'normal' : 'low' },
    { label: 'Compressor B1', load: 0, current: 0, status: 'Standby', statusClass: 'normal' }
  ]

  // Update device health occasionally
  if (Math.random() > 0.95) {
    deviceHealth.value = [
      { subsystem: 'Compressors', status: newLoad > 800 ? 'warning' : 'normal', statusText: newLoad > 800 ? 'High Load' : 'All Running' },
      { subsystem: 'Evaporators', status: 'normal', statusText: 'Clean' },
      { subsystem: 'Condensers', status: deltaCondenser.value < 3 ? 'warning' : 'normal', statusText: deltaCondenser.value < 3 ? 'Low ΔT' : 'Optimal' },
      { subsystem: 'Refrigerant Circuit', status: 'normal', statusText: 'Sealed' },
      { subsystem: 'Controllers', status: 'normal', statusText: 'Online' }
    ]
  }

  // Update tips occasionally
  if (Math.random() > 0.7) {
    const tipPool = [
      { icon: '❄️', title: 'COP Performance', desc: `Current COP: ${cop.value}`, priority: cop.value < 4.5 ? 'Low' : 'Good' },
      { icon: '💧', title: 'Delta T', desc: `Chilled water ΔT: ${deltaChilled.value}°C`, priority: deltaChilled.value < 4 ? 'Low' : (deltaChilled.value > 7 ? 'High' : 'Optimal') },
      { icon: '🔧', title: 'Load Distribution', desc: `${chillerCount} chillers active`, priority: chillerCount === 4 ? 'High Load' : 'Normal' }
    ]
    chillerTips.value = tipPool.sort(() => Math.random() - 0.5).slice(0, 2)
  }

  // Update charts
  if (loadChart && capacityChart) {
    const now = new Date()
    const timeLabel = now.toTimeString().slice(0, 5)
    const lastHour = hourLabels.value[hourLabels.value.length - 1]

    if (lastHour !== timeLabel) {
      hourLabels.value.push(timeLabel)
      if (hourLabels.value.length > historyLength) hourLabels.value.shift()
      loadHistory.value.push(currentLoad.value)
      copHistory.value.push(cop.value)
      if (loadHistory.value.length > historyLength) loadHistory.value.shift()
      if (copHistory.value.length > historyLength) copHistory.value.shift()

      loadChart.setOption({
        xAxis: { data: hourLabels.value },
        series: [{ data: loadHistory.value }, { data: copHistory.value }]
      })
    }

    // Update capacity distribution
    const newDistribution = chillerStatus.value.map(c => c.load)
    capacityChart.setOption({
      series: [{ data: newDistribution.map((v, i) => ({ value: v, name: `Chiller ${i + 1}` })) }]
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
  currentLoad.value = 550
  cop.value = 5.1
  chilledWaterSupply.value = 7.2
  chilledWaterReturn.value = 12.8
  deltaChilled.value = 5.6
  condenserWaterSupply.value = 29.5
  condenserWaterReturn.value = 34.2
  deltaCondenser.value = 4.7
  powerConsumption.value = 108

  initLoadHistory()
  await initCharts()

  if (loadChart && capacityChart) {
    updateTimer = setInterval(updateAllData, 5000)
  }

  window.addEventListener('resize', handleResize)
  document.addEventListener('fullscreenchange', onFullscreenChange)

  routeWatch = watch(() => route.fullPath, async () => {
    initLoadHistory()
    await initCharts()
    if (loadChart && capacityChart && !updateTimer) {
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