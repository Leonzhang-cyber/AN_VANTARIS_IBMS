<template>
  <div v-if="isPageLoaded" class="hvac-page">
    <div class="main-view">
      <div class="three-columns">
        <!-- Left Column: Key Metrics + System Status + Recent Events + Device Health -->
        <div class="col-left">
          <div class="title-row" v-if="isMobile">
            <h1 class="page-title">LEAK</h1>
            <span class="live-time">{{ currentTime }}</span>
          </div>
          <div class="card-img" v-if="isMobile">
            <img :src="securityImageUrl" alt="Leak Detection 3D View" />
          </div>

          <!-- Key Metrics -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📈 Key Metrics</div>
            <div class="metrics-list">
              <div class="metric-row"><div class="metric-icon">💧</div><div class="metric-label">Total Sensors</div><div class="metric-value">{{ totalSensors }}</div></div>
              <div class="metric-row"><div class="metric-icon">✅</div><div class="metric-label">Normal</div><div class="metric-value">{{ stats.normal }}</div></div>
              <div class="metric-row"><div class="metric-icon">⚠️</div><div class="metric-label">Warning</div><div class="metric-value" :class="{ 'has-alert': stats.warning > 0 }">{{ stats.warning }}</div></div>
              <div class="metric-row"><div class="metric-icon">🚨</div><div class="metric-label">Leak Detected</div><div class="metric-value" :class="{ 'has-leak': stats.leak > 0 }">{{ stats.leak }}</div></div>
              <div class="metric-row"><div class="metric-icon">🔧</div><div class="metric-label">Fault</div><div class="metric-value">{{ stats.fault }}</div></div>
            </div>
          </el-card>

          <!-- Leak Status -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">💧 Leak Status</div>
            <div class="mode-list">
              <div class="mode-row" v-for="item in leakStatus" :key="item.name">
                <div class="mode-name">{{ item.name }}</div>
                <div class="mode-bar-bg"><div class="mode-bar-fill" :style="{ width: item.moisture + '%', background: item.color }"></div></div>
                <div class="mode-value">{{ item.moisture }}%</div>
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
            <h1 class="page-title">LEAK</h1>
            <span class="live-time" v-if="isFullscreen">{{ currentTime }}</span>
          </div>
          <div class="card-img" v-if="!isMobile">
            <img :src="securityImageUrl" alt="Leak Detection 3D View" />
          </div>
          <div class="cart-view">
            <!-- Moisture Trend -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <div class="card-header">📊 Moisture Trend (24h)</div>
              <div ref="moistureChartRef" class="chart-box"></div>
            </el-card>
            <!-- Leak Location Map -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <div class="card-header">🗺️ Leak Detection Map</div>
              <div ref="leakMapChartRef" class="chart-box"></div>
            </el-card>
          </div>
        </div>

        <!-- Right Column: KPIs + Sensor Readings + Risk Assessment + Tips -->
        <div class="col-right">
          <!-- Leak KPIs -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📊 Leak KPIs</div>
            <div class="kpi-row"><span class="kpi-row-left">Max Moisture</span><strong>{{ maxMoisture }}%</strong><span class="trend" :class="maxMoisture > 70 ? 'up' : 'stable'">{{ maxMoisture > 70 ? 'Critical' : 'Normal' }}</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Avg Moisture</span><strong>{{ avgMoisture }}%</strong><span class="trend stable">Baseline: 15%</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Total Incidents</span><strong>{{ totalIncidents }}</strong><span class="trend up">This Month</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Avg Response Time</span><strong>{{ avgResponseTime }} min</strong><span class="trend stable">Target: &lt; 15</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Water Damage Risk</span><strong>{{ waterDamageRisk }}%</strong><span class="trend" :class="waterDamageRisk > 30 ? 'up' : 'stable'">{{ waterDamageRisk > 30 ? 'Elevated' : 'Low' }}</span></div>
          </el-card>

          <!-- Sensor Readings Gauges -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📡 Sensor Readings</div>
            <div class="gauges-grid">
              <div class="gauge-item"><el-progress type="dashboard" :percentage="sensor1Moisture" :color="moistureColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ sensor1Moisture }}%</span></template></el-progress><div class="gauge-label">{{ sensor1Name }}</div></div>
              <div class="gauge-item"><el-progress type="dashboard" :percentage="sensor2Moisture" :color="moistureColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ sensor2Moisture }}%</span></template></el-progress><div class="gauge-label">{{ sensor2Name }}</div></div>
              <div class="gauge-item"><el-progress type="dashboard" :percentage="sensor3Moisture" :color="moistureColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ sensor3Moisture }}%</span></template></el-progress><div class="gauge-label">{{ sensor3Name }}</div></div>
              <div class="gauge-item"><el-progress type="dashboard" :percentage="sensor4Moisture" :color="moistureColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ sensor4Moisture }}%</span></template></el-progress><div class="gauge-label">{{ sensor4Name }}</div></div>
            </div>
          </el-card>

          <!-- Risk Assessment -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">⚠️ Risk Assessment</div>
            <div class="setpoint-list">
              <div class="setpoint-row" v-for="item in riskAssessment" :key="item.label">
                <div class="sp-label">{{ item.label }}</div>
                <div class="sp-values"><span class="sp-set">Zone: {{ item.zone }}</span><span class="sp-actual">Risk: {{ item.risk }}</span></div>
                <div class="sp-deviation" :class="item.statusClass">{{ item.status }}</div>
              </div>
            </div>
          </el-card>

          <!-- Leak Tips -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">💡 Leak Prevention Tips</div>
            <div class="tips-list">
              <div class="tip-item" v-for="(tip, idx) in leakTips" :key="idx">
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
      <div class="loading-tip">Initializing Leak Detection System</div>
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
  'Loading leak sensors...',
  'Checking moisture levels...',
  'Initializing detection zones...',
  'Connecting to sensors...',
  'Starting dashboard...',
  'Almost ready...'
]

const preloadSecurityImage = () => {
  return new Promise((resolve) => {
    const img = new Image()
    const imageUrl = 'https://aegisnx.com/wp-content/uploads/2026/05/ScreenShot_2026-06-03_134325_444.png'
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

// ==================== Core Leak Detection Data ====================
// Key metrics
const totalSensors = ref(32)

// Sensor data
const sensors = ref([])

// KPIs
const maxMoisture = ref(0)
const avgMoisture = ref(0)
const totalIncidents = ref(0)
const avgResponseTime = ref(0)
const waterDamageRisk = ref(0)

// Top sensors for gauges
const sensor1Name = ref('CRAC 1')
const sensor1Moisture = ref(0)
const sensor2Name = ref('CRAC 2')
const sensor2Moisture = ref(0)
const sensor3Name = ref('Pipe Joint')
const sensor3Moisture = ref(0)
const sensor4Name = ref('Floor Drain')
const sensor4Moisture = ref(0)

// Leak Status by zone
const leakStatus = ref([
  { name: 'CRAC Row A', moisture: 0, status: 'Normal', color: '#34d399' },
  { name: 'CRAC Row B', moisture: 0, status: 'Normal', color: '#34d399' },
  { name: 'Underfloor', moisture: 0, status: 'Normal', color: '#34d399' },
  { name: 'Pipe Gallery', moisture: 0, status: 'Normal', color: '#34d399' }
])

// Recent events
const recentEvents = ref([
  { id: 1, severity: 'Warning', location: 'CRAC 1', description: 'Moisture level elevated near unit', timestamp: '2 hours ago' },
  { id: 2, severity: 'Critical', location: 'Pipe Gallery', description: 'Leak detected under raised floor', timestamp: '4 hours ago' },
  { id: 3, severity: 'Info', location: 'Sensor 12', description: 'Battery low notification', timestamp: '8 hours ago' }
])

// Device health
const deviceHealth = ref([
  { subsystem: 'Leak Sensors', status: 'normal', statusText: 'All Online' },
  { subsystem: 'Cable Sensors', status: 'normal', statusText: 'Active' },
  { subsystem: 'Point Sensors', status: 'normal', statusText: 'Operational' },
  { subsystem: 'Alarm Panel', status: 'normal', statusText: 'Armed' },
  { subsystem: 'Communication', status: 'normal', statusText: 'Connected' }
])

// Risk assessment
const riskAssessment = ref([
  { label: 'Zone A - CRAC', zone: 'Row A', risk: 'Low', status: 'Normal', statusClass: 'normal' },
  { label: 'Zone B - CRAC', zone: 'Row B', risk: 'Medium', status: 'Monitor', statusClass: 'low' },
  { label: 'Underfloor', zone: 'Whole Room', risk: 'Low', status: 'Normal', statusClass: 'normal' },
  { label: 'Pipe Gallery', zone: 'South Side', risk: 'High', status: 'Alert', statusClass: 'high' }
])

// Leak Tips
const leakTips = ref([
  { icon: '💧', title: 'Preventive Maintenance', desc: 'Monthly sensor calibration recommended', priority: 'Scheduled' },
  { icon: '🔧', title: 'Check Drainage', desc: 'CRAC condensate drains inspected', priority: 'Completed' }
])

// Color configurations
const moistureColor = [{ color: '#34d399', percentage: 30 }, { color: '#f59e0b', percentage: 60 }, { color: '#ef4444', percentage: 80 }]

// ==================== Generate Sensors ====================
const generateSensors = () => {
  const locations = [
    'CRAC 1 - Under', 'CRAC 2 - Under', 'CRAC 3 - Under', 'CRAC 4 - Under',
    'Pipe Joint A1', 'Pipe Joint A2', 'Pipe Joint B1', 'Pipe Joint B2',
    'Floor Drain 1', 'Floor Drain 2', 'Floor Drain 3', 'Floor Drain 4',
    'Chiller 1 Base', 'Chiller 2 Base', 'Pump Area', 'Storage Tank Base'
  ]
  const zones = ['CRAC Row A', 'CRAC Row B', 'Underfloor', 'Pipe Gallery']

  return locations.map((location, idx) => {
    const statuses = ['normal', 'normal', 'normal', 'normal', 'normal', 'normal', 'warning', 'leak', 'normal', 'normal', 'normal', 'normal', 'normal', 'normal', 'fault', 'normal']
    const moisture = statuses[idx % statuses.length] === 'normal' ? 5 + Math.random() * 15 :
        (statuses[idx % statuses.length] === 'warning' ? 30 + Math.random() * 30 :
            (statuses[idx % statuses.length] === 'leak' ? 70 + Math.random() * 25 : 0))

    return {
      id: idx + 1,
      name: `LDS-${String(idx + 1).padStart(3, '0')}`,
      location: location,
      zone: zones[idx % zones.length],
      status: statuses[idx % statuses.length],
      moisture: parseFloat(moisture.toFixed(1)),
      battery: Math.floor(60 + Math.random() * 40),
      lastReading: new Date(Date.now() - Math.random() * 60 * 60 * 1000).toLocaleString()
    }
  })
}

// Update statistics from sensors
const stats = computed(() => ({
  normal: sensors.value.filter(s => s.status === 'normal').length,
  warning: sensors.value.filter(s => s.status === 'warning').length,
  leak: sensors.value.filter(s => s.status === 'leak').length,
  fault: sensors.value.filter(s => s.status === 'fault').length
}))

const updateStatsFromSensors = () => {
  const moistureValues = sensors.value.map(s => s.moisture)
  maxMoisture.value = Math.max(...moistureValues)
  avgMoisture.value = parseFloat((moistureValues.reduce((a, b) => a + b, 0) / moistureValues.length).toFixed(1))

  // Update zone status
  const cracRowASensors = sensors.value.filter(s => s.zone === 'CRAC Row A')
  const cracRowBSensors = sensors.value.filter(s => s.zone === 'CRAC Row B')
  const underfloorSensors = sensors.value.filter(s => s.zone === 'Underfloor')
  const pipeGallerySensors = sensors.value.filter(s => s.zone === 'Pipe Gallery')

  const getZoneStatus = (zoneSensors) => {
    if (zoneSensors.length === 0) return { status: 'Normal', color: '#34d399' }
    const maxMoist = Math.max(...zoneSensors.map(s => s.moisture))
    if (maxMoist > 70) return { status: 'Leak', color: '#ef4444' }
    if (maxMoist > 30) return { status: 'Warning', color: '#f59e0b' }
    return { status: 'Normal', color: '#34d399' }
  }

  const avgMoistZone = (zoneSensors) => {
    if (zoneSensors.length === 0) return 0
    const sum = zoneSensors.reduce((a, b) => a + b.moisture, 0)
    return parseFloat((sum / zoneSensors.length).toFixed(1))
  }

  leakStatus.value = [
    { name: 'CRAC Row A', moisture: avgMoistZone(cracRowASensors), status: getZoneStatus(cracRowASensors).status, color: getZoneStatus(cracRowASensors).color },
    { name: 'CRAC Row B', moisture: avgMoistZone(cracRowBSensors), status: getZoneStatus(cracRowBSensors).status, color: getZoneStatus(cracRowBSensors).color },
    { name: 'Underfloor', moisture: avgMoistZone(underfloorSensors), status: getZoneStatus(underfloorSensors).status, color: getZoneStatus(underfloorSensors).color },
    { name: 'Pipe Gallery', moisture: avgMoistZone(pipeGallerySensors), status: getZoneStatus(pipeGallerySensors).status, color: getZoneStatus(pipeGallerySensors).color }
  ]

  // Update top sensors for gauges
  const sortedByMoisture = [...sensors.value].sort((a, b) => b.moisture - a.moisture)
  if (sortedByMoisture[0]) { sensor1Name.value = sortedByMoisture[0].location; sensor1Moisture.value = sortedByMoisture[0].moisture }
  if (sortedByMoisture[1]) { sensor2Name.value = sortedByMoisture[1].location; sensor2Moisture.value = sortedByMoisture[1].moisture }
  if (sortedByMoisture[2]) { sensor3Name.value = sortedByMoisture[2].location; sensor3Moisture.value = sortedByMoisture[2].moisture }
  if (sortedByMoisture[3]) { sensor4Name.value = sortedByMoisture[3].location; sensor4Moisture.value = sortedByMoisture[3].moisture }

  // Update risk assessment based on moisture
  riskAssessment.value = [
    { label: 'Zone A - CRAC', zone: 'Row A', risk: leakStatus.value[0].moisture > 50 ? 'High' : (leakStatus.value[0].moisture > 30 ? 'Medium' : 'Low'), status: leakStatus.value[0].status, statusClass: leakStatus.value[0].moisture > 70 ? 'high' : (leakStatus.value[0].moisture > 30 ? 'low' : 'normal') },
    { label: 'Zone B - CRAC', zone: 'Row B', risk: leakStatus.value[1].moisture > 50 ? 'High' : (leakStatus.value[1].moisture > 30 ? 'Medium' : 'Low'), status: leakStatus.value[1].status, statusClass: leakStatus.value[1].moisture > 70 ? 'high' : (leakStatus.value[1].moisture > 30 ? 'low' : 'normal') },
    { label: 'Underfloor', zone: 'Whole Room', risk: leakStatus.value[2].moisture > 50 ? 'High' : (leakStatus.value[2].moisture > 30 ? 'Medium' : 'Low'), status: leakStatus.value[2].status, statusClass: leakStatus.value[2].moisture > 70 ? 'high' : (leakStatus.value[2].moisture > 30 ? 'low' : 'normal') },
    { label: 'Pipe Gallery', zone: 'South Side', risk: leakStatus.value[3].moisture > 50 ? 'High' : (leakStatus.value[3].moisture > 30 ? 'Medium' : 'Low'), status: leakStatus.value[3].status, statusClass: leakStatus.value[3].moisture > 70 ? 'high' : (leakStatus.value[3].moisture > 30 ? 'low' : 'normal') }
  ]

  // Update water damage risk (percentage based on max moisture)
  waterDamageRisk.value = Math.min(100, Math.floor(maxMoisture.value * 1.2))

  // Random incidents and response time
  totalIncidents.value = Math.floor(2 + Math.random() * 10)
  avgResponseTime.value = Math.floor(8 + Math.random() * 15)
}

// ==================== Charts ====================
const moistureChartRef = ref(null)
const leakMapChartRef = ref(null)
let moistureChart = null
let leakMapChart = null

// Moisture history (24 hours)
const historyLength = 24
const moistureHistory = ref([])
const hourLabels = ref([])

const initMoistureHistory = () => {
  moistureHistory.value = []
  hourLabels.value = []
  const now = new Date()
  for (let i = historyLength - 1; i >= 0; i--) {
    const t = new Date(now - i * 3600000)
    hourLabels.value.push(t.toTimeString().slice(0, 5))
    moistureHistory.value.push(parseFloat((10 + Math.random() * 20).toFixed(1)))
  }
}

// Moisture chart option
const getMoistureChartOption = () => {
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(15,25,45,0.9)', borderColor: '#3b82f6', textStyle: { color: '#e2e8f0' } },
    grid: { left: '0%', right: '0%', bottom: 0, top: 25, containLabel: true },
    xAxis: { type: 'category', data: hourLabels.value, axisLabel: { color: '#94a3b8', fontSize: 9, rotate: 30, interval: 3 }, axisLine: { lineStyle: { color: '#334155' } } },
    yAxis: { type: 'value', name: 'Moisture Level (%)', nameTextStyle: { color: '#64748b', fontSize: 10 }, axisLabel: { color: '#94a3b8', fontSize: 10 }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } }, min: 0, max: 100 },
    series: [{
      type: 'line', data: moistureHistory.value, smooth: true, symbol: 'circle', symbolSize: 4,
      lineStyle: { width: 2, color: '#60a5fa' }, areaStyle: { opacity: 0.3, color: '#60a5fa' },
      markLine: { data: [{ yAxis: 30, name: 'Warning', lineStyle: { color: '#f59e0b', type: 'dashed' } }, { yAxis: 70, name: 'Critical', lineStyle: { color: '#ef4444', type: 'dashed' } }] }
    }]
  }
}

// Leak map scatter chart (simulated floor layout)
// Leak map scatter chart (simulated floor layout)
const getLeakMapOption = () => {
  if (!sensors.value || sensors.value.length === 0) {
    return {
      backgroundColor: 'transparent',
      title: {
        show: true,
        text: 'Loading sensor data...',
        textStyle: { color: '#94a3b8', fontSize: 12 }
      },
      xAxis: { show: false },
      yAxis: { show: false },
      series: []
    }
  }

  // 为每个传感器分配固定坐标
  const data = sensors.value.map(s => {
    let x, y
    // 使用传感器ID生成稳定的坐标
    const idHash = (s.id * 7) % 100

    if (s.zone === 'CRAC Row A') {
      x = 2 + (idHash % 4)
      y = 7 + Math.floor(idHash / 20) % 2
    }
    else if (s.zone === 'CRAC Row B') {
      x = 2 + (idHash % 4)
      y = 4 + Math.floor(idHash / 20) % 2
    }
    else if (s.zone === 'Underfloor') {
      x = 5 + (idHash % 5)
      y = 4 + Math.floor(idHash / 15) % 4
    }
    else {
      x = 9 + (idHash % 3)
      y = 2 + Math.floor(idHash / 25) % 5
    }

    return {
      value: [x, y, s.moisture],
      name: s.name,
      location: s.location,
      zone: s.zone,
      status: s.status
    }
  })

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        const dataItem = params.data
        return `<strong>${dataItem.location}</strong><br/>
                Moisture: ${dataItem.value[2]}%<br/>
                Zone: ${dataItem.zone}<br/>
                Status: ${dataItem.status}`
      },
      backgroundColor: 'rgba(15,25,45,0.95)',
      borderColor: '#3b82f6',
      borderWidth: 1,
      textStyle: { color: '#e2e8f0', fontSize: 12 }
    },
    grid: {
      left: '8%',
      right: '5%',
      top: '10%',
      bottom: '5%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: 'Room Position (m)',
      nameTextStyle: { color: '#64748b', fontSize: 10 },
      min: 0,
      max: 12,
      splitLine: { show: false },
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    yAxis: {
      type: 'value',
      name: 'Room Position (m)',
      nameTextStyle: { color: '#64748b', fontSize: 10 },
      min: 0,
      max: 10,
      splitLine: { show: false },
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    series: [{
      type: 'scatter',
      data: data,
      symbolSize: (value) => {
        // value 是单个数据点的值数组 [x, y, moisture]
        if (value && value.value) {
          return 18 + (value.value[2] / 100) * 30
        }
        return 20
      },
      itemStyle: {
        color: (value) => {
          if (value && value.value) {
            const moisture = value.value[2]
            if (moisture > 70) return '#ef4444'
            if (moisture > 30) return '#f59e0b'
          }
          return '#34d399'
        },
        borderColor: '#ffffff',
        borderWidth: 1,
        shadowBlur: 10,
        shadowColor: 'rgba(0,0,0,0.3)'
      },
      label: {
        show: true,
        formatter: (params) => {
          if (params.data && params.data.value) {
            return `${params.data.value[2]}%`
          }
          return ''
        },
        position: 'inside',
        fontSize: 10,
        fontWeight: 'bold',
        color: '#ffffff',
        textShadowBlur: 2,
        textShadowColor: 'rgba(0,0,0,0.5)'
      },
      emphasis: {
        scale: 1.2,
        label: {
          show: true,
          formatter: (params) => {
            if (params.data) {
              return `${params.data.location}\n${params.data.value[2]}%`
            }
            return ''
          },
          position: 'top',
          fontSize: 11
        }
      }
    }]
  }
}

// ==================== Chart Lifecycle ====================
const disposeCharts = () => {
  if (moistureChart) { moistureChart.dispose(); moistureChart = null }
  if (leakMapChart) { leakMapChart.dispose(); leakMapChart = null }
}

const initCharts = async () => {
  await nextTick()

  // 等待DOM元素准备好
  for (let attempt = 0; attempt < 10; attempt++) {
    const moistureDom = moistureChartRef.value
    const mapDom = leakMapChartRef.value

    if (moistureDom && mapDom &&
        moistureDom.clientWidth > 0 && moistureDom.clientHeight > 0 &&
        mapDom.clientWidth > 0 && mapDom.clientHeight > 0) {
      break
    }
    await new Promise(resolve => setTimeout(resolve, 200))
  }

  const moistureDom = moistureChartRef.value
  const mapDom = leakMapChartRef.value

  if (!moistureDom || !mapDom) {
    console.error('[initCharts] DOM elements not found')
    return
  }

  // 确保传感器数据已加载
  if (!sensors.value || sensors.value.length === 0) {
    console.log('[initCharts] Waiting for sensor data...')
    setTimeout(() => initCharts(), 500)
    return
  }

  disposeCharts()

  try {
    moistureChart = echarts.init(moistureDom)
    leakMapChart = echarts.init(mapDom)
    moistureChart.setOption(getMoistureChartOption())
    leakMapChart.setOption(getLeakMapOption())
    console.log('[initCharts] Charts initialized successfully with', sensors.value.length, 'sensors')
  } catch (e) {
    console.error('[initCharts] Error:', e)
  }
}

const handleResize = () => {
  moistureChart?.resize()
  leakMapChart?.resize()
}

let fullscreenTimer = null
const onFullscreenChange = () => {
  clearTimeout(fullscreenTimer)
  fullscreenTimer = setTimeout(handleResize, 350)
}

// ==================== Live Update ====================
let updateTimer = null

const updateAllData = () => {
  // Update sensors with random moisture changes
  sensors.value.forEach(sensor => {
    if (sensor.status === 'leak') {
      sensor.moisture = Math.min(100, sensor.moisture + (Math.random() - 0.3) * 2)
    } else if (sensor.status === 'warning') {
      sensor.moisture = Math.min(70, Math.max(30, sensor.moisture + (Math.random() - 0.5) * 1.5))
    } else {
      sensor.moisture = Math.min(29, Math.max(0, sensor.moisture + (Math.random() - 0.5) * 1))
    }
    sensor.moisture = parseFloat(sensor.moisture.toFixed(1))

    // Update status based on moisture
    if (sensor.moisture > 70) sensor.status = 'leak'
    else if (sensor.moisture > 30) sensor.status = 'warning'
    else sensor.status = 'normal'
  })

  updateStatsFromSensors()

  // Update device health occasionally
  if (Math.random() > 0.95) {
    deviceHealth.value = [
      { subsystem: 'Leak Sensors', status: stats.value.fault > 0 ? 'warning' : 'normal', statusText: stats.value.fault > 0 ? `${stats.value.fault} Offline` : 'All Online' },
      { subsystem: 'Cable Sensors', status: 'normal', statusText: 'Active' },
      { subsystem: 'Point Sensors', status: 'normal', statusText: 'Operational' },
      { subsystem: 'Alarm Panel', status: stats.value.leak > 0 ? 'warning' : 'normal', statusText: stats.value.leak > 0 ? 'Alert Active' : 'Armed' },
      { subsystem: 'Communication', status: 'normal', statusText: 'Connected' }
    ]
  }

  // Update tips occasionally
  if (Math.random() > 0.7) {
    const tipPool = [
      { icon: '💧', title: 'Leak Detected', desc: `${stats.value.leak} active leak sensor(s)`, priority: stats.value.leak > 0 ? 'Critical' : 'Normal' },
      { icon: '🔧', title: 'Preventive Maintenance', desc: 'Monthly sensor calibration recommended', priority: 'Scheduled' },
      { icon: '⚠️', title: 'High Moisture Area', desc: `Pipe Gallery at ${leakStatus.value[3].moisture}%`, priority: leakStatus.value[3].moisture > 50 ? 'Alert' : 'Monitor' }
    ]
    leakTips.value = tipPool.sort(() => Math.random() - 0.5).slice(0, 2)
  }

  // Update charts
  if (moistureChart && leakMapChart) {
    const now = new Date()
    const timeLabel = now.toTimeString().slice(0, 5)
    const lastHour = hourLabels.value[hourLabels.value.length - 1]

    if (lastHour !== timeLabel) {
      hourLabels.value.push(timeLabel)
      if (hourLabels.value.length > historyLength) hourLabels.value.shift()
      moistureHistory.value.push(avgMoisture.value)
      if (moistureHistory.value.length > historyLength) moistureHistory.value.shift()

      moistureChart.setOption({
        xAxis: { data: hourLabels.value },
        series: [{ data: moistureHistory.value }]
      })
    }

    // Update leak map - 使用 notMerge: false 来保留配置
    leakMapChart.setOption(getLeakMapOption(), { notMerge: false })
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

  // Initialize sensors
  sensors.value = generateSensors()
  updateStatsFromSensors()
  initMoistureHistory()

  // 等待一小段时间确保DOM完全渲染
  await nextTick()

  // Initialize charts
  await initCharts()

  if (moistureChart && leakMapChart) {
    if (updateTimer) clearInterval(updateTimer)
    updateTimer = setInterval(() => {
      updateAllData()
    }, 5000)
  }

  window.addEventListener('resize', handleResize)
  document.addEventListener('fullscreenchange', onFullscreenChange)

  routeWatch = watch(() => route.fullPath, async () => {
    initMoistureHistory()
    await initCharts()
    if (moistureChart && leakMapChart && !updateTimer) {
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
.metric-value.has-alert { color: #f59e0b; }
.metric-value.has-leak { color: #ef4444; }
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