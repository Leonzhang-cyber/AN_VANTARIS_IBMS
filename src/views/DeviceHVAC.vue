<template>
  <div v-if="isPageLoaded" class="hvac-page">
    <div class="main-view">
      <div class="three-columns">
        <!-- Left Column: Key Metrics + Operation Modes + Alerts + System Health -->
        <div class="col-left">
          <!-- Key Metrics -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📈 Key Metrics</div>
            <div class="metrics-list">
              <div class="metric-row">
                <div class="metric-icon">❄️</div>
                <div class="metric-label">Chilled Water ΔT</div>
                <div class="metric-value">{{ chwDeltaT }}°C</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">🌡️</div>
                <div class="metric-label">Cooling Load</div>
                <div class="metric-value">{{ coolingLoad }} RT</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">⚡</div>
                <div class="metric-label">System kW/Ton</div>
                <div class="metric-value">{{ kwPerTon }}</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">📊</div>
                <div class="metric-label">Total Energy</div>
                <div class="metric-value">{{ totalEnergy }} kWh</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">⚠️</div>
                <div class="metric-label">Active Alarms</div>
                <div class="metric-value">{{ activeAlerts }}</div>
              </div>
            </div>
          </el-card>

          <!-- Operation Modes Distribution -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🔄 Operating Strategy</div>
            <div class="mode-list">
              <div class="mode-row" v-for="mode in operationModes" :key="mode.name">
                <div class="mode-name">{{ mode.name }}</div>
                <div class="mode-bar-bg">
                  <div class="mode-bar-fill" :style="{ width: mode.loadPercent + '%', background: mode.color }"></div>
                </div>
                <div class="mode-value">{{ mode.loadPercent }}%</div>
                <div class="mode-power">{{ mode.status }}</div>
              </div>
            </div>
          </el-card>

          <!-- Recent Alerts -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🚨 Active Alarms</div>
            <div class="alert-list">
              <div class="alert-item" v-for="alert in recentAlerts" :key="alert.id">
                <div class="alert-header">
                  <span class="alert-tag" :class="alert.severity">{{ alert.severity }}</span>
                  <span class="alert-device">{{ alert.equipment }}</span>
                </div>
                <div class="alert-msg">{{ alert.description }}</div>
                <div class="alert-time">{{ alert.timestamp }}</div>
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
            <h1 class="page-title">HVAC</h1>
            <span class="live-time">{{ currentTime }}</span>
          </div>
          <div class="card-img">
            <img :src="hvacImageUrl" alt="HVAC 3D View" />
          </div>
          <div class="cart-view">
            <!-- Chiller Plant COP Comparison -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <div class="card-header">📊 Equipment Efficiency</div>
              <div ref="efficiencyChartRef" class="chart-box"></div>
            </el-card>
            <!-- System Power Trend -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <div class="card-header">⚡ System Power Distribution (Last 10 min)</div>
              <div ref="energyChartRef" class="chart-box"></div>
            </el-card>
          </div>
        </div>

        <!-- Right Column: KPI + Environment + Setpoints + Optimization -->
        <div class="col-right">
          <!-- KPI Dashboard -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📊 Plant KPIs</div>
            <div class="kpi-row">
              <span>Avg. CHW Supply Temp</span>
              <strong>{{ chwSupplyTemp }}°C</strong>
              <span class="trend stable">Set 7.0°C</span>
            </div>
            <div class="kpi-row">
              <span>Avg. CHW Return Temp</span>
              <strong>{{ chwReturnTemp }}°C</strong>
              <span class="trend up">ΔT {{ chwDeltaT }}°C</span>
            </div>
            <div class="kpi-row">
              <span>Condenser Water Temp</span>
              <strong>{{ cwTemp }}°C</strong>
              <span class="trend stable">Approach {{ approachTemp }}°C</span>
            </div>
            <div class="kpi-row">
              <span>System Efficiency</span>
              <strong>{{ kwPerTon }} kW/Ton</strong>
              <span class="trend up">Target < 0.6</span>
            </div>
          </el-card>

          <!-- Environmental Gauges -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🌡️ Zone Conditions</div>
            <div class="gauges-grid">
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="tempPercent" :color="tempColor" :width="90" :stroke-width="4">
                  <template #default="{ percentage }">
                    <span class="percentage-label">{{ indoorTemp }} °C</span>
                  </template>
                </el-progress>
                <div class="gauge-label">Indoor Temp</div>
              </div>
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="humPercent" :color="humColor" :width="90" :stroke-width="4">
                  <template #default="{ percentage }">
                    <span class="percentage-label">{{ indoorHum }} %</span>
                  </template>
                </el-progress>
                <div class="gauge-label">Indoor RH</div>
              </div>
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="co2Percent" :color="co2Color" :width="90" :stroke-width="4">
                  <template #default="{ percentage }">
                    <span class="percentage-label">{{ co2Value }} ppm</span>
                  </template>
                </el-progress>
                <div class="gauge-label">CO₂ Level</div>
              </div>
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="outdoorTempPercent" :color="outdoorTempColor" :width="90" :stroke-width="4">
                  <template #default="{ percentage }">
                    <span class="percentage-label">{{ outdoorTemp }} °C</span>
                  </template>
                </el-progress>
                <div class="gauge-label">Outdoor Temp</div>
              </div>
            </div>
          </el-card>

          <!-- Setpoint Deviation -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🎯 Control Parameters</div>
            <div class="setpoint-list">
              <div class="setpoint-row" v-for="item in controlParams" :key="item.label">
                <div class="sp-label">{{ item.label }}</div>
                <div class="sp-values">
                  <span class="sp-set">SP: {{ item.setpoint }}{{ item.unit }}</span>
                  <span class="sp-actual">PV: {{ item.actual }}{{ item.unit }}</span>
                </div>
                <div class="sp-deviation" :class="item.status">
                  {{ item.deviation }}
                </div>
              </div>
            </div>
          </el-card>

          <!-- Optimization Suggestions -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">💡 Energy Saving Tips</div>
            <div class="tips-list">
              <div class="tip-item" v-for="(tip, idx) in optimizationTips" :key="idx">
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
        <div class="loading-tip">Initializing HVAC Control System</div>
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
const hvacImageUrl = ref('')

// Loading messages sequence
const loadingMessages = [
  'Preparing assets...',
  'Loading background...',
  'Loading HVAC model...',
  'Initializing modules...',
  'Connecting to sensors...',
  'Starting dashboard...',
  'Almost ready...'
]

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

// ==================== Preload Assets ====================
const preloadHVACImage = () => {
  return new Promise((resolve) => {
    const img = new Image()
    const imageUrl = 'https://aegisnx.com/wp-content/uploads/2026/05/1778147036078.png'

    img.onload = () => {
      hvacImageUrl.value = imageUrl
      resolve()
    }

    img.onerror = () => {
      console.warn('HVAC image load failed, using fallback')
      hvacImageUrl.value = imageUrl // Still try to show it
      resolve()
    }

    img.src = imageUrl
  })
}

const preloadAssets = async () => {
  let progress = 0
  let messageIndex = 0

  // Update loading message periodically
  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 800)

  // Simulate progress update
  const progressInterval = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 10
      loadingProgress.value = Math.min(progress, 90)

      // Update message based on progress
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

  // Preload HVAC image
  await preloadHVACImage()

  clearInterval(messageInterval)
  clearInterval(progressInterval)
  loadingMessage.value = 'Ready!'
  loadingProgress.value = 100

  await new Promise(resolve => setTimeout(resolve, 500))
  isPageLoaded.value = true
}

// ==================== Core HVAC Data ====================
// Chilled water system
const chwSupplyTemp = ref(6.8)
const chwReturnTemp = ref(12.3)
const chwDeltaT = ref(5.5)
const cwTemp = ref(29.5)
const approachTemp = ref(3.2)

// Load & Efficiency
const coolingLoad = ref(850)
const kwPerTon = ref(0.62)
const totalEnergy = ref(12480)
const activeAlerts = ref(3)

// Zone conditions
const indoorTemp = ref(23.8)
const indoorHum = ref(55)
const outdoorTemp = ref(32.5)
const co2Value = ref(520)

// Gauge percentages
const tempPercent = ref(60)
const humPercent = ref(55)
const co2Percent = ref(44)
const outdoorTempPercent = ref(65)

// Gauge colors
const tempColor = [
  { color: '#10b981', percentage: 60 },
  { color: '#f59e0b', percentage: 80 },
  { color: '#ef4444', percentage: 100 }
]
const humColor = '#60a5fa'
const co2Color = [
  { color: '#10b981', percentage: 50 },
  { color: '#f59e0b', percentage: 75 },
  { color: '#ef4444', percentage: 100 }
]
const outdoorTempColor = [
  { color: '#f59e0b', percentage: 60 },
  { color: '#ef4444', percentage: 80 },
  { color: '#dc2626', percentage: 100 }
]

// Operation modes
const operationModes = ref([
  { name: 'Chiller #1', loadPercent: 78, status: 'Running', color: '#3b82f6' },
  { name: 'Chiller #2', loadPercent: 65, status: 'Running', color: '#60a5fa' },
  { name: 'Cooling Tower', loadPercent: 82, status: 'Running', color: '#34d399' },
  { name: 'CHW Pump Set', loadPercent: 72, status: 'Running', color: '#fbbf24' }
])

// Recent alarms
const recentAlerts = ref([
  { id: 1, severity: 'Critical', equipment: 'CHWP-02', description: 'High bearing temperature (78°C)', timestamp: '3 min ago' },
  { id: 2, severity: 'Warning', equipment: 'CT-01 Fan', description: 'Vibration level exceeds 4.5 mm/s', timestamp: '15 min ago' },
  { id: 3, severity: 'Warning', equipment: 'AHU-05', description: 'Filter differential pressure high', timestamp: '28 min ago' }
])

// System health
const systemHealth = ref([
  { subsystem: 'Chiller Plant', status: 'normal', statusText: 'Optimal' },
  { subsystem: 'Cooling Tower', status: 'warning', statusText: 'Check' },
  { subsystem: 'CHW Distribution', status: 'normal', statusText: 'Normal' },
  { subsystem: 'AHU Systems', status: 'normal', statusText: 'Normal' },
  { subsystem: 'BAS Network', status: 'normal', statusText: 'Online' }
])

// Control parameters
const controlParams = ref([
  { label: 'CHW Supply Temp', setpoint: '7.0', actual: '6.8', unit: '°C', deviation: '-0.2 ✓', status: 'normal' },
  { label: 'CHW Return Temp', setpoint: '12.0', actual: '12.3', unit: '°C', deviation: '+0.3 ⚠', status: 'high' },
  { label: 'Condenser Water', setpoint: '30.0', actual: '29.5', unit: '°C', deviation: '-0.5 ✓', status: 'low' },
  { label: 'CHW Diff Pressure', setpoint: '150', actual: '142', unit: 'kPa', deviation: '-8 ⚠', status: 'low' }
])

// Optimization tips
const optimizationTips = ref([
  { icon: '🔧', title: 'Raise CHW Setpoint', desc: 'Increase to 8°C to improve chiller efficiency', saving: '~8% energy savings' },
])

// ==================== Charts ====================
const efficiencyChartRef = ref(null)
const energyChartRef = ref(null)
let efficiencyChart = null
let energyChart = null

// 10-minute history
const historyLength = 10
const powerHistory = ref([])
const timeLabels = ref([])

const initPowerHistory = () => {
  const now = new Date()
  powerHistory.value = []
  timeLabels.value = []
  for (let i = historyLength - 1; i >= 0; i--) {
    const t = new Date(now - i * 60000)
    timeLabels.value.push(t.toTimeString().slice(0, 5))
    powerHistory.value.push({
      'Chillers': 420 + Math.random() * 40,
      'Pumps': 85 + Math.random() * 15,
      'Cooling Towers': 45 + Math.random() * 10,
      'AHUs': 120 + Math.random() * 20,
      'Others': 55 + Math.random() * 10
    })
  }
}

// Chiller efficiency data
const getChillerData = () => {
  return [
    { name: 'CH-01', cop: 5.8, load: 78, type: 'Chiller', status: 'normal' },
    { name: 'CH-02', cop: 5.2, load: 65, type: 'Chiller', status: 'normal' },
    { name: 'CH-03', cop: 4.1, load: 45, type: 'Chiller', status: 'warning' },
    { name: 'CT System', cop: 3.8, load: 82, type: 'Tower', status: 'normal' },
    { name: 'Pump Set', cop: 2.5, load: 72, type: 'Pump', status: 'warning' },
    { name: 'AHU Array', cop: 3.2, load: 68, type: 'AHU', status: 'normal' }
  ]
}

// Bar chart option
const getEfficiencyOption = (data) => {
  const typeColors = {
    'Chiller': '#3b82f6',
    'Tower': '#34d399',
    'Pump': '#fbbf24',
    'AHU': '#f97316'
  }
  const colors = data.map(d => d.status === 'warning' ? '#ef4444' : typeColors[d.type] || '#3b82f6')

  return {
    backgroundColor: 'transparent',
    grid: { left: '3%', right: '4%', bottom: '0%', top: '20%', containLabel: true },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(15,25,45,0.9)',
      borderColor: '#3b82f6',
      textStyle: { color: '#e2e8f0' },
      formatter: (params) => {
        const d = params[0]
        const item = data[d.dataIndex]
        return `<div style="padding:4px 8px">
          <b>${d.name}</b> (${item.type})<br/>
          Efficiency: <span style="color:#facc15;font-weight:bold">${d.value}</span><br/>
          Load: <span style="color:#60a5fa">${item.load}%</span><br/>
          ${item.status === 'warning' ? '<span style="color:#ef4444">⚠ Below target</span>' : '<span style="color:#34d399">✓ Normal</span>'}
        </div>`
      }
    },
    xAxis: {
      type: 'category',
      data: data.map(d => d.name),
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    yAxis: {
      type: 'value',
      name: 'COP / EER',
      nameTextStyle: { color: '#64748b', fontSize: 10 },
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } },
      min: 1,
      max: 7
    },
    series: [
      {
        name: 'Efficiency',
        type: 'bar',
        data: data.map((d, i) => ({
          value: d.cop,
          itemStyle: {
            borderRadius: [6, 6, 0, 0],
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: colors[i] },
              { offset: 1, color: colors[i] + '60' }
            ]),
            shadowBlur: 8,
            shadowColor: colors[i]
          }
        })),
        barWidth: '38%',
        label: {
          show: true,
          position: 'top',
          color: '#facc15',
          fontSize: 11,
          fontWeight: 'bold'
        },
        markPoint: {
          silent: true,
          symbol: 'circle',
          symbolSize: 8,
          label: { show: false },
          data: data.map((d, i) => ({
            coord: [d.name, d.cop],
            itemStyle: { color: colors[i], shadowBlur: 10, shadowColor: colors[i] }
          }))
        }
      },
      {
        type: 'line',
        data: [],
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: { color: '#94a3b8', type: 'dashed', width: 1 },
          label: { show: true, position: 'end', color: '#94a3b8', fontSize: 9, formatter: 'Target 4.5' },
          data: [
            { yAxis: 4.5, name: 'Minimum COP Target' }
          ]
        }
      }
    ]
  }
}

// Line chart option
const getEnergyOption = () => {
  const categories = ['Chillers', 'Pumps', 'Cooling Towers', 'AHUs', 'Others']
  const colors = ['#3b82f6', '#34d399', '#fbbf24', '#f97316', '#94a3b8']

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
    grid: { left: '3%', right: '4%', bottom: '0%', top: '20%', containLabel: true },
    xAxis: {
      type: 'category',
      data: timeLabels.value,
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
const waitForSize = (el, timeout = 5000) => {
  return new Promise((resolve, reject) => {
    if (!el) return reject('el is null')
    const start = Date.now()
    const check = () => {
      const w = el.clientWidth
      const h = el.clientHeight
      if (w > 0 && h > 0) {
        console.log(`[waitForSize] success - w:${w} h:${h}`)
        resolve()
      } else if (Date.now() - start > timeout) {
        console.warn(`[waitForSize] Timeout, force resolve. Current size: ${w}x${h}`)
        resolve()
      } else {
        requestAnimationFrame(check)
      }
    }
    check()
  })
}

const disposeCharts = () => {
  if (efficiencyChart) {
    efficiencyChart.dispose()
    efficiencyChart = null
  }
  if (energyChart) {
    energyChart.dispose()
    energyChart = null
  }
}

const initCharts = async () => {
  await nextTick()

  for (let attempt = 0; attempt < 5; attempt++) {
    await new Promise(resolve => setTimeout(resolve, 100))

    const effDom = efficiencyChartRef.value
    const eneDom = energyChartRef.value

    if (!effDom || !eneDom) {
      console.warn(`[initCharts] attempt ${attempt}: refs not ready`)
      continue
    }

    if (effDom.clientWidth === 0 || effDom.clientHeight === 0) {
      console.warn(`[initCharts] attempt ${attempt}: container size is 0`)
      continue
    }

    disposeCharts()

    try {
      efficiencyChart = echarts.init(effDom)
      energyChart = echarts.init(eneDom)

      efficiencyChart.setOption(getEfficiencyOption(getChillerData()))
      energyChart.setOption(getEnergyOption())

      console.log('[initCharts] Charts rendered successfully')
      return
    } catch (e) {
      console.error('[initCharts] Error during init:', e)
    }
  }

  console.error('[initCharts] Failed after 5 attempts')
}

const handleResize = () => {
  efficiencyChart?.resize()
  energyChart?.resize()
}

let fullscreenTimer = null
const onFullscreenChange = () => {
  clearTimeout(fullscreenTimer)
  fullscreenTimer = setTimeout(handleResize, 350)
}

// ==================== Live Update ====================
let updateTimer = null

const updateAllData = () => {
  // Update chilled water temps
  chwSupplyTemp.value = parseFloat((6.5 + Math.random() * 1.0).toFixed(1))
  chwReturnTemp.value = parseFloat((11.5 + Math.random() * 1.5).toFixed(1))
  chwDeltaT.value = parseFloat((chwReturnTemp.value - chwSupplyTemp.value).toFixed(1))

  // Update cooling load & efficiency
  coolingLoad.value = Math.floor(800 + Math.random() * 100)
  kwPerTon.value = parseFloat((0.58 + Math.random() * 0.12).toFixed(2))
  totalEnergy.value = totalEnergy.value + Math.floor(Math.random() * 5)
  activeAlerts.value = Math.floor(Math.random() * 5)

  // Environmental
  indoorTemp.value = parseFloat((23.3 + Math.random() * 1.2).toFixed(1))
  indoorHum.value = Math.floor(53 + Math.random() * 8)
  outdoorTemp.value = parseFloat((31.5 + Math.random() * 2.5).toFixed(1))
  co2Value.value = Math.floor(480 + Math.random() * 80)

  // Gauge percentages
  tempPercent.value = Math.round((indoorTemp.value / 30) * 100)
  humPercent.value = indoorHum.value
  co2Percent.value = Math.round(((co2Value.value - 400) / 600) * 100)
  outdoorTempPercent.value = Math.round((outdoorTemp.value / 40) * 100)

  // Operation modes
  operationModes.value = [
    { name: 'Chiller #1', loadPercent: 70 + Math.floor(Math.random() * 20), status: 'Running', color: '#3b82f6' },
    { name: 'Chiller #2', loadPercent: 55 + Math.floor(Math.random() * 20), status: 'Running', color: '#60a5fa' },
    { name: 'Cooling Tower', loadPercent: 75 + Math.floor(Math.random() * 15), status: 'Running', color: '#34d399' },
    { name: 'CHW Pump Set', loadPercent: 65 + Math.floor(Math.random() * 15), status: 'Running', color: '#fbbf24' }
  ]

  // System health
  systemHealth.value = [
    { subsystem: 'Chiller Plant', status: Math.random() > 0.95 ? 'warning' : 'normal', statusText: Math.random() > 0.95 ? 'Check' : 'Optimal' },
    { subsystem: 'Cooling Tower', status: Math.random() > 0.85 ? 'warning' : 'normal', statusText: Math.random() > 0.85 ? 'Check' : 'Normal' },
    { subsystem: 'CHW Distribution', status: Math.random() > 0.9 ? 'warning' : 'normal', statusText: Math.random() > 0.9 ? 'Check' : 'Normal' },
    { subsystem: 'AHU Systems', status: 'normal', statusText: 'Normal' },
    { subsystem: 'BAS Network', status: 'normal', statusText: 'Online' }
  ]

  // Control parameters
  controlParams.value = [
    { label: 'CHW Supply Temp', setpoint: '7.0', actual: (6.5 + Math.random()).toFixed(1), unit: '°C', deviation: (Math.random() > 0.5 ? '+' : '-') + (Math.random() * 0.8).toFixed(1) + ' ' + (Math.random() > 0.6 ? '⚠' : '✓'), status: Math.random() > 0.7 ? 'high' : 'normal' },
    { label: 'CHW Return Temp', setpoint: '12.0', actual: (11.5 + Math.random() * 1.5).toFixed(1), unit: '°C', deviation: '+' + (Math.random() * 1).toFixed(1) + ' ⚠', status: 'high' },
    { label: 'Condenser Water', setpoint: '30.0', actual: (29 + Math.random() * 2).toFixed(1), unit: '°C', deviation: (Math.random() > 0.5 ? '-' : '+') + (Math.random() * 1).toFixed(1) + ' ✓', status: 'low' },
    { label: 'CHW Diff Pressure', setpoint: '150', actual: Math.floor(138 + Math.random() * 15), unit: 'kPa', deviation: (Math.random() > 0.5 ? '-' : '+') + Math.floor(Math.random() * 12) + ' ⚠', status: 'low' }
  ]

  // Tips
  const tipPool = [
    { icon: '🔧', title: 'Raise CHW Setpoint', desc: 'Increase from 7°C to 8°C when outdoor temp < 30°C', saving: '~8% energy savings' },
    { icon: '🌬️', title: 'Reset SAT Based on Load', desc: 'Adjust supply air temp by 2°C in low occupancy', saving: '~5% AHU energy' },
    { icon: '📊', title: 'Stagger Chiller Start', desc: 'Delay 2nd chiller start by 15 min to avoid peak', saving: '~12% demand charge' },
    { icon: '⚙️', title: 'Optimize Condenser Water', desc: 'Reset CW setpoint based on wet bulb approach', saving: '~3% chiller savings' }
  ]
  optimizationTips.value = tipPool.sort(() => Math.random() - 0.5).slice(0, 1)

  // Update charts
  if (efficiencyChart && energyChart) {
    efficiencyChart.setOption(getEfficiencyOption(getChillerData()))

    // Update power trend
    const now = new Date()
    timeLabels.value.push(now.toTimeString().slice(0, 5))
    if (timeLabels.value.length > historyLength) timeLabels.value.shift()

    powerHistory.value.push({
      'Chillers': 410 + Math.random() * 50,
      'Pumps': 80 + Math.random() * 20,
      'Cooling Towers': 42 + Math.random() * 12,
      'AHUs': 115 + Math.random() * 25,
      'Others': 52 + Math.random() * 12
    })
    if (powerHistory.value.length > historyLength) powerHistory.value.shift()

    energyChart.setOption({
      xAxis: { data: timeLabels.value },
      series: ['Chillers', 'Pumps', 'Cooling Towers', 'AHUs', 'Others'].map(name => ({
        data: powerHistory.value.map(d => d[name])
      }))
    })
  }
}

let routeWatch = null

onMounted(async () => {
  updateTime()
  clockTimer = setInterval(updateTime, 1000)

  // Preload all assets before showing page
  await preloadAssets()

  initPowerHistory()
  await initCharts()

  if (efficiencyChart && energyChart) {
    updateTimer = setInterval(updateAllData, 5000)
  }

  window.addEventListener('resize', handleResize)
  document.addEventListener('fullscreenchange', onFullscreenChange)

  routeWatch = watch(() => route.fullPath, async () => {
    initPowerHistory()
    await initCharts()
    if (efficiencyChart && energyChart && !updateTimer) {
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

/* Main HVAC Page Styles */
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

/* Left & Right columns */
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

/* Glass card effect */
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

/* Operation Modes */
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

/* Recent Alerts */
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
.alert-tag.Critical {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}
.alert-tag.Warning {
  background: rgba(251, 191, 36, 0.2);
  color: #fbbf24;
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

/* System Health */
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

/* Center Charts */
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

/* Gauges */
.gauges-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}
.gauge-item { text-align: center; }
.gauge-label { font-size: 13px; color: #cbd5e1; margin-top: 0px; height: 20px; text-align: center; align-items: center; }

/* KPI rows */
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
.trend.up { color: #34d399;text-align: right; }
.trend.stable { color: #fbbf24;text-align: right; }

/* Setpoint Deviation */
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
  color: #64748b;
  font-size: 10px;
  color: #cbd5e1;
}
.sp-actual {
  color: #cbd5e1;
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

/* Optimization Tips */
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