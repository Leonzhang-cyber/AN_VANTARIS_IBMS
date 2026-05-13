<!-- DeviceHVAC.vue -->
<template>
  <div v-if="isPageLoaded" class="hvac-page">
    <div class="main-view">
      <div class="three-columns">
        <!-- Left Column: Key Metrics + Pump Status + Recent Alerts + System Health -->
        <div class="col-left">
          <div class="title-row" v-if="isMobile">
            <h1 class="page-title">Plumbing</h1>
            <span class="live-time">{{ currentTime }}</span>
          </div>
          <div class="card-img" v-if="isMobile">
            <img :src="plumbingImageUrl" alt="Plumbing 3D View" />
          </div>
          <!-- Key Metrics -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📈 Key Metrics</div>
            <div class="metrics-list">
              <div class="metric-row">
                <div class="metric-icon">💧</div>
                <div class="metric-label">Water Pressure</div>
                <div class="metric-value">{{ waterPressure }} bar</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">🔄</div>
                <div class="metric-label">Flow Rate</div>
                <div class="metric-value">{{ flowRate }} m³/h</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">📊</div>
                <div class="metric-label">Daily Consumption</div>
                <div class="metric-value">{{ dailyConsumption }} m³</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">🌡️</div>
                <div class="metric-label">Hot Water Temp</div>
                <div class="metric-value">{{ hotWaterTemp }}°C</div>
              </div>
              <div class="metric-row">
                <div class="metric-icon">⚠️</div>
                <div class="metric-label">Active Alarms</div>
                <div class="metric-value">{{ activeAlarms }}</div>
              </div>
            </div>
          </el-card>

          <!-- Pump Operation Status -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🔄 Pump Status</div>
            <div class="mode-list">
              <div class="mode-row" v-for="item in pumpStatus" :key="item.name">
                <div class="mode-name">{{ item.name }}</div>
                <div class="mode-bar-bg">
                  <div class="mode-bar-fill" :style="{ width: item.loadPercent + '%', background: item.color }"></div>
                </div>
                <div class="mode-value">{{ item.loadPercent }}%</div>
                <div class="mode-power">{{ item.status }}</div>
              </div>
            </div>
          </el-card>

          <!-- Recent Alarms -->
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
          <div class="title-row" v-if="!isMobile">
            <h1 class="page-title">Plumbing</h1>
            <span class="live-time" v-if="isFullscreen">{{ currentTime }}</span>
          </div>
          <div class="card-img" v-if="!isMobile">
            <img :src="plumbingImageUrl" alt="Plumbing 3D View" />
          </div>
          <div class="cart-view">
            <!-- Water Pressure Trend -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <div class="card-header">📊 Water Pressure Trend (Hourly)</div>
              <div ref="pressureChartRef" class="chart-box"></div>
            </el-card>
            <!-- Flow Rate Monitor -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <div class="card-header">💧 Flow Rate Monitor (Last 10 min)</div>
              <div ref="flowChartRef" class="chart-box"></div>
            </el-card>
          </div>
        </div>

        <!-- Right Column: KPIs + Tank Levels + Valve Status + Tips -->
        <div class="col-right">
          <!-- Plumbing KPIs -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📊 Plumbing KPIs</div>
            <div class="kpi-row">
              <span>Water Pressure</span>
              <strong>{{ waterPressure }} bar</strong>
              <span class="trend stable">Target > 4.5</span>
            </div>
            <div class="kpi-row">
              <span>Leak Detection</span>
              <strong>{{ leakStatus }}</strong>
              <span class="trend up">Normal</span>
            </div>
            <div class="kpi-row">
              <span>Pump Efficiency</span>
              <strong>{{ pumpEfficiency }}%</strong>
              <span class="trend up">Target > 80%</span>
            </div>
            <div class="kpi-row">
              <span>System Uptime</span>
              <strong>{{ systemUptime }}%</strong>
              <span class="trend up">99.9% SLA</span>
            </div>
          </el-card>

          <!-- Tank Level Gauges -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🪣 Tank Levels</div>
            <div class="gauges-grid">
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="freshWaterLevel" :color="tankColor" :width="90" :stroke-width="4">
                  <template #default>
                    <span class="percentage-label">{{ freshWaterPercent }}%</span>
                  </template>
                </el-progress>
                <div class="gauge-label">Fresh Water</div>
              </div>
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="hotWaterLevel" :color="tankColorHot" :width="90" :stroke-width="4">
                  <template #default>
                    <span class="percentage-label">{{ hotWaterPercent }}%</span>
                  </template>
                </el-progress>
                <div class="gauge-label">Hot Water</div>
              </div>
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="greyWaterLevel" :color="tankColorLow" :width="90" :stroke-width="4">
                  <template #default>
                    <span class="percentage-label">{{ greyWaterPercent }}%</span>
                  </template>
                </el-progress>
                <div class="gauge-label">Grey Water</div>
              </div>
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="fireReserveLevel" :color="fireTankColor" :width="90" :stroke-width="4">
                  <template #default>
                    <span class="percentage-label">{{ fireReservePercent }}%</span>
                  </template>
                </el-progress>
                <div class="gauge-label">Fire Reserve</div>
              </div>
            </div>
          </el-card>

          <!-- Valve Status -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🎯 Valve Status</div>
            <div class="setpoint-list">
              <div class="setpoint-row" v-for="item in valveStatus" :key="item.label">
                <div class="sp-label">{{ item.label }}</div>
                <div class="sp-values">
                  <span class="sp-set">Position: {{ item.position }}%</span>
                  <span class="sp-actual">Flow: {{ item.flow }} m³/h</span>
                </div>
                <div class="sp-deviation" :class="item.alarmClass">
                  {{ item.status }}
                </div>
              </div>
            </div>
          </el-card>

          <!-- Plumbing Tips -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">💡 Water Saving Tips</div>
            <div class="tips-list">
              <div class="tip-item" v-for="(tip, idx) in plumbingTips" :key="idx">
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
        <div class="loading-tip">Initializing Plumbing System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, watch, computed  } from 'vue'
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
const plumbingImageUrl = ref('')

// Loading messages sequence
const loadingMessages = [
  'Preparing assets...',
  'Loading background...',
  'Loading plumbing model...',
  'Initializing modules...',
  'Connecting to sensors...',
  'Starting dashboard...',
  'Almost ready...'
]

// ==================== Preload Assets ====================
const preloadPlumbingImage = () => {
  return new Promise((resolve) => {
    const img = new Image()
    const imageUrl = 'https://aegisnx.com/wp-content/uploads/2026/05/1778554341809.png'

    img.onload = () => {
      plumbingImageUrl.value = imageUrl
      resolve()
    }

    img.onerror = () => {
      console.warn('Plumbing image load failed, using fallback')
      plumbingImageUrl.value = imageUrl
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

  await preloadPlumbingImage()

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

// ==================== Core Plumbing Data ====================
// Key metrics
const waterPressure = ref(5.2)
const flowRate = ref(42.8)
const dailyConsumption = ref(185)
const hotWaterTemp = ref(62)
const activeAlarms = ref(2)

// Plumbing KPIs
const leakStatus = ref('No Leak')
const pumpEfficiency = ref(87.5)
const systemUptime = ref(99.95)

// Tank levels
const freshWaterPercent = ref(78)
const hotWaterPercent = ref(65)
const greyWaterPercent = ref(32)
const fireReservePercent = ref(95)

const freshWaterLevel = ref(78)
const hotWaterLevel = ref(65)
const greyWaterLevel = ref(32)
const fireReserveLevel = ref(95)

// Tank colors
const tankColor = [
  { color: '#10b981', percentage: 30 },
  { color: '#60a5fa', percentage: 70 },
  { color: '#facc15', percentage: 100 }
]
const tankColorHot = [
  { color: '#f97316', percentage: 30 },
  { color: '#ef4444', percentage: 70 },
  { color: '#dc2626', percentage: 100 }
]
const tankColorLow = [
  { color: '#94a3b8', percentage: 50 },
  { color: '#64748b', percentage: 100 }
]
const fireTankColor = [
  { color: '#10b981', percentage: 80 },
  { color: '#ef4444', percentage: 100 }
]

// Pump status
const pumpStatus = ref([
  { name: 'Booster #1', loadPercent: 72, status: 'Running', color: '#3b82f6' },
  { name: 'Booster #2', loadPercent: 0, status: 'Standby', color: '#60a5fa' },
  { name: 'Hot Water Circ', loadPercent: 58, status: 'Running', color: '#f97316' },
  { name: 'Sump Pump', loadPercent: 15, status: 'Idle', color: '#34d399' }
])

// Recent alarms
const recentAlarms = ref([
  { id: 1, severity: 'Warning', location: 'Booster Pump #1', description: 'Pressure fluctuation detected (±0.3 bar)', timestamp: '4 min ago' },
  { id: 2, severity: 'Critical', location: 'Hot Water Tank', description: 'Temperature dropped below 55°C threshold', timestamp: '12 min ago' },
  { id: 3, severity: 'Warning', location: 'Grey Water Tank', description: 'Level approaching overflow (78% capacity)', timestamp: '25 min ago' }
])

// System health
const systemHealth = ref([
  { subsystem: 'Booster Pumps', status: 'warning', statusText: 'Check #1' },
  { subsystem: 'Hot Water System', status: 'normal', statusText: 'Normal' },
  { subsystem: 'Cold Water Supply', status: 'normal', statusText: 'Normal' },
  { subsystem: 'Drainage System', status: 'normal', statusText: 'Normal' },
  { subsystem: 'Leak Detection', status: 'normal', statusText: 'Active' }
])

// Valve status
const valveStatus = ref([
  { label: 'Main Supply Valve', position: '85', flow: '36.5', status: 'Open', alarmClass: 'normal' },
  { label: 'Hot Water Supply', position: '70', flow: '12.8', status: 'Open', alarmClass: 'normal' },
  { label: 'Grey Water Inlet', position: '45', flow: '5.2', status: 'Open', alarmClass: 'low' },
  { label: 'Bypass Valve', position: '0', flow: '0.0', status: 'Closed', alarmClass: 'normal' }
])

// Plumbing tips
const plumbingTips = ref([
  { icon: '💧', title: 'Pressure Optimization', desc: 'Reduce booster pump setpoint from 5.5 to 5.0 bar during off-peak', saving: '~10% pump energy' },
])

// ==================== Charts ====================
const pressureChartRef = ref(null)
const flowChartRef = ref(null)
let pressureChart = null
let flowChart = null

// 12-hour pressure history
const pressureHistoryLength = 12
const pressureHistory = ref([])
const pressureHourLabels = ref([])

const initPressureHistory = () => {
  pressureHistory.value = []
  pressureHourLabels.value = []
  const now = new Date()
  for (let i = pressureHistoryLength - 1; i >= 0; i--) {
    const t = new Date(now - i * 3600000)
    pressureHourLabels.value.push(t.toTimeString().slice(0, 5))
    pressureHistory.value.push({
      'Supply Main': 5.0 + Math.random() * 0.6,
      'Hot Water': 4.5 + Math.random() * 0.8,
      'Grey Water': 2.0 + Math.random() * 0.5,
      'Fire Line': 6.5 + Math.random() * 0.3
    })
  }
}

// 10-minute flow history
const flowHistoryLength = 10
const flowHistory = ref([])
const flowTimeLabels = ref([])

const initFlowHistory = () => {
  const now = new Date()
  flowHistory.value = []
  flowTimeLabels.value = []
  for (let i = flowHistoryLength - 1; i >= 0; i--) {
    const t = new Date(now - i * 60000)
    flowTimeLabels.value.push(t.toTimeString().slice(0, 5))
    flowHistory.value.push({
      'Cold Water': 30 + Math.random() * 10,
      'Hot Water': 10 + Math.random() * 5,
      'Grey Water': 4 + Math.random() * 3,
      'Irrigation': 2 + Math.random() * 2
    })
  }
}

// Water pressure line chart option (hourly)
const getPressureOption = () => {
  const categories = ['Supply Main', 'Hot Water', 'Grey Water', 'Fire Line']
  const colors = ['#3b82f6', '#f97316', '#94a3b8', '#ef4444']

  const seriesData = categories.map((name, i) => ({
    name,
    type: 'line',
    data: pressureHistory.value.map(d => d[name]),
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
    },
    markLine: i === 0 ? {
      silent: true,
      lineStyle: { color: '#94a3b8', type: 'dashed', width: 1 },
      label: { show: true, position: 'end', color: '#94a3b8', fontSize: 8, formatter: 'Min 4.5' },
      data: [{ yAxis: 4.5 }]
    } : undefined
  }))

  return {
    backgroundColor: 'transparent',
    grid: { left: '0%', right: '0%', bottom: 0, top: 25, containLabel: true },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15,25,45,0.9)',
      borderColor: '#3b82f6',
      textStyle: { color: '#e2e8f0' },
      valueFormatter: (value) => value + ' bar'
    },
    legend: { textStyle: { color: '#94a3b8', fontSize: 9 }, top: 0 },
    xAxis: {
      type: 'category',
      data: pressureHourLabels.value,
      axisLabel: { color: '#94a3b8', fontSize: 9, rotate: 15 },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    yAxis: {
      type: 'value',
      name: 'bar',
      nameTextStyle: { color: '#64748b', fontSize: 10 },
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } },
      min: 1,
      max: 7.5
    },
    series: seriesData
  }
}

// Flow rate monitor option
const getFlowOption = () => {
  const categories = ['Cold Water', 'Hot Water', 'Grey Water', 'Irrigation']
  const colors = ['#3b82f6', '#f97316', '#94a3b8', '#34d399']

  const seriesData = categories.map((name, i) => ({
    name,
    type: 'line',
    data: flowHistory.value.map(d => d[name]),
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
    }
  }))

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15,25,45,0.9)',
      borderColor: '#3b82f6',
      textStyle: { color: '#e2e8f0' },
      valueFormatter: (value) => value + ' m³/h'
    },
    legend: { textStyle: { color: '#94a3b8', fontSize: 9 }, top: 0 },
    grid: { left: '0%', right: '0%', bottom: 0, top: 25, containLabel: true },
    xAxis: {
      type: 'category',
      data: flowTimeLabels.value,
      axisLabel: { color: '#94a3b8', fontSize: 9 },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    yAxis: {
      type: 'value',
      name: 'm³/h',
      nameTextStyle: { color: '#64748b', fontSize: 10 },
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } }
    },
    series: seriesData
  }
}

// ==================== Chart Lifecycle ====================
const disposeCharts = () => {
  if (pressureChart) {
    pressureChart.dispose()
    pressureChart = null
  }
  if (flowChart) {
    flowChart.dispose()
    flowChart = null
  }
}

const initCharts = async () => {
  await nextTick()

  for (let attempt = 0; attempt < 5; attempt++) {
    await new Promise(resolve => setTimeout(resolve, 100))

    const presDom = pressureChartRef.value
    const flowDom = flowChartRef.value

    if (!presDom || !flowDom) continue
    if (presDom.clientWidth === 0 || presDom.clientHeight === 0) continue
    if (flowDom.clientWidth === 0 || flowDom.clientHeight === 0) continue

    disposeCharts()

    try {
      pressureChart = echarts.init(presDom)
      flowChart = echarts.init(flowDom)

      pressureChart.setOption(getPressureOption())
      flowChart.setOption(getFlowOption())

      return
    } catch (e) {
      console.error('[initCharts] Error:', e)
    }
  }
}

const handleResize = () => {
  pressureChart?.resize()
  flowChart?.resize()
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
  waterPressure.value = parseFloat((4.8 + Math.random() * 0.8).toFixed(1))
  flowRate.value = parseFloat((38 + Math.random() * 12).toFixed(1))
  dailyConsumption.value = dailyConsumption.value + Math.floor(Math.random() * 1)
  hotWaterTemp.value = Math.floor(60 + Math.random() * 5)
  activeAlarms.value = Math.floor(Math.random() * 3)
  pumpEfficiency.value = parseFloat((85 + Math.random() * 6).toFixed(1))
  leakStatus.value = Math.random() > 0.95 ? 'Suspected' : 'No Leak'

  // Tank levels
  freshWaterPercent.value = Math.floor(75 + Math.random() * 8)
  hotWaterPercent.value = Math.floor(62 + Math.random() * 8)
  greyWaterPercent.value = Math.floor(28 + Math.random() * 10)
  fireReservePercent.value = Math.floor(93 + Math.random() * 4)

  freshWaterLevel.value = freshWaterPercent.value
  hotWaterLevel.value = hotWaterPercent.value
  greyWaterLevel.value = greyWaterPercent.value
  fireReserveLevel.value = fireReservePercent.value

  // Pump status
  pumpStatus.value = [
    { name: 'Booster #1', loadPercent: 65 + Math.floor(Math.random() * 15), status: 'Running', color: '#3b82f6' },
    { name: 'Booster #2', loadPercent: Math.random() > 0.8 ? 30 + Math.floor(Math.random() * 20) : 0, status: Math.random() > 0.8 ? 'Running' : 'Standby', color: '#60a5fa' },
    { name: 'Hot Water Circ', loadPercent: 50 + Math.floor(Math.random() * 15), status: 'Running', color: '#f97316' },
    { name: 'Sump Pump', loadPercent: 10 + Math.floor(Math.random() * 15), status: Math.random() > 0.3 ? 'Idle' : 'Running', color: '#34d399' }
  ]

  // System health
  systemHealth.value = [
    { subsystem: 'Booster Pumps', status: Math.random() > 0.9 ? 'warning' : 'normal', statusText: Math.random() > 0.9 ? 'Check #1' : 'Normal' },
    { subsystem: 'Hot Water System', status: 'normal', statusText: 'Normal' },
    { subsystem: 'Cold Water Supply', status: 'normal', statusText: 'Normal' },
    { subsystem: 'Drainage System', status: Math.random() > 0.95 ? 'warning' : 'normal', statusText: Math.random() > 0.95 ? 'Clog Risk' : 'Normal' },
    { subsystem: 'Leak Detection', status: 'normal', statusText: 'Active' }
  ]

  // Valve status
  valveStatus.value = [
    { label: 'Main Supply Valve', position: String(80 + Math.floor(Math.random() * 15)), flow: (34 + Math.random() * 6).toFixed(1), status: 'Open', alarmClass: 'normal' },
    { label: 'Hot Water Supply', position: String(65 + Math.floor(Math.random() * 15)), flow: (11 + Math.random() * 4).toFixed(1), status: 'Open', alarmClass: 'normal' },
    { label: 'Grey Water Inlet', position: String(40 + Math.floor(Math.random() * 15)), flow: (4 + Math.random() * 3).toFixed(1), status: 'Open', alarmClass: 'low' },
    { label: 'Bypass Valve', position: '0', flow: '0.0', status: 'Closed', alarmClass: 'normal' }
  ]

  // Tips
  const tipPool = [
    { icon: '💧', title: 'Pressure Optimization', desc: 'Reduce booster pump setpoint from 5.5 to 5.0 bar during off-peak', saving: '~10% pump energy' },
    { icon: '🌡️', title: 'Hot Water Schedule', desc: 'Lower hot water temp to 55°C during weekend low occupancy', saving: '~15% heating energy' },
    { icon: '🔍', title: 'Leak Inspection', desc: 'Minor flow anomaly detected in 3F restroom, schedule inspection', saving: 'Prevent water waste' },
    { icon: '🌧️', title: 'Rainwater Harvesting', desc: 'Connect rainwater tank to irrigation system for additional savings', saving: '~20% outdoor water' }
  ]
  plumbingTips.value = tipPool.sort(() => Math.random() - 0.5).slice(0, 1)

  // Update charts
  if (pressureChart && flowChart) {
    // Update pressure history
    const now = new Date()
    pressureHourLabels.value.push(now.toTimeString().slice(0, 5))
    if (pressureHourLabels.value.length > pressureHistoryLength) pressureHourLabels.value.shift()

    pressureHistory.value.push({
      'Supply Main': 5.0 + Math.random() * 0.6,
      'Hot Water': 4.5 + Math.random() * 0.8,
      'Grey Water': 2.0 + Math.random() * 0.5,
      'Fire Line': 6.5 + Math.random() * 0.3
    })
    if (pressureHistory.value.length > pressureHistoryLength) pressureHistory.value.shift()

    pressureChart.setOption({
      xAxis: { data: pressureHourLabels.value },
      series: ['Supply Main', 'Hot Water', 'Grey Water', 'Fire Line'].map(name => ({
        data: pressureHistory.value.map(d => d[name])
      }))
    })

    // Update flow history
    flowTimeLabels.value.push(now.toTimeString().slice(0, 5))
    if (flowTimeLabels.value.length > flowHistoryLength) flowTimeLabels.value.shift()

    flowHistory.value.push({
      'Cold Water': 30 + Math.random() * 10,
      'Hot Water': 10 + Math.random() * 5,
      'Grey Water': 4 + Math.random() * 3,
      'Irrigation': 2 + Math.random() * 2
    })
    if (flowHistory.value.length > flowHistoryLength) flowHistory.value.shift()

    flowChart.setOption({
      xAxis: { data: flowTimeLabels.value },
      series: ['Cold Water', 'Hot Water', 'Grey Water', 'Irrigation'].map(name => ({
        data: flowHistory.value.map(d => d[name])
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

  initPressureHistory()
  initFlowHistory()
  await initCharts()

  if (pressureChart && flowChart) {
    updateTimer = setInterval(updateAllData, 5000)
  }

  window.addEventListener('resize', handleResize)
  document.addEventListener('fullscreenchange', onFullscreenChange)

  routeWatch = watch(() => route.fullPath, async () => {
    initPressureHistory()
    initFlowHistory()
    await initCharts()
    if (pressureChart && flowChart && !updateTimer) {
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

/* Main Plumbing Page Styles */
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