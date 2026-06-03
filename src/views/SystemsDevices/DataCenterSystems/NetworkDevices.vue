<template>
  <div v-if="isPageLoaded" class="hvac-page">
    <div class="main-view">
      <div class="three-columns">
        <!-- Left Column: Key Metrics + System Status + Recent Events + Device Health -->
        <div class="col-left">
          <div class="title-row" v-if="isMobile">
            <h1 class="page-title">NET</h1>
            <span class="live-time">{{ currentTime }}</span>
          </div>
          <div class="card-img" v-if="isMobile">
            <img :src="securityImageUrl" alt="Network Devices 3D View" />
          </div>

          <!-- Key Metrics -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📈 Key Metrics</div>
            <div class="metrics-list">
              <div class="metric-row"><div class="metric-icon">🖧</div><div class="metric-label">Total Devices</div><div class="metric-value">{{ totalDevices }}</div></div>
              <div class="metric-row"><div class="metric-icon">✅</div><div class="metric-label">Online Rate</div><div class="metric-value">{{ onlineRate }}%</div></div>
              <div class="metric-row"><div class="metric-icon">📊</div><div class="metric-label">Avg Throughput</div><div class="metric-value">{{ avgThroughput }} Gbps</div></div>
              <div class="metric-row"><div class="metric-icon">📦</div><div class="metric-label">Total Ports</div><div class="metric-value">{{ totalPorts }}</div></div>
              <div class="metric-row"><div class="metric-icon">🚨</div><div class="metric-label">Active Alarms</div><div class="metric-value">{{ activeAlarms }}</div></div>
            </div>
          </el-card>

          <!-- Network Status -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🖧 Network Status</div>
            <div class="mode-list">
              <div class="mode-row" v-for="item in networkStatus" :key="item.name">
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
            <h1 class="page-title">NET</h1>
            <span class="live-time" v-if="isFullscreen">{{ currentTime }}</span>
          </div>
          <div class="card-img" v-if="!isMobile">
            <img :src="securityImageUrl" alt="Network Devices 3D View" />
          </div>
<!--          <div class="cart-view">-->
<!--            &lt;!&ndash; Throughput Trend &ndash;&gt;-->
<!--            <el-card class="card glass-card chart-card" shadow="hover">-->
<!--              <div class="card-header">📊 Throughput Trend (24h)</div>-->
<!--              <div ref="throughputChartRef" class="chart-box"></div>-->
<!--            </el-card>-->
<!--            &lt;!&ndash; Traffic Distribution &ndash;&gt;-->
<!--            <el-card class="card glass-card chart-card" shadow="hover">-->
<!--              <div class="card-header">📡 Traffic Distribution</div>-->
<!--              <div ref="trafficChartRef" class="chart-box"></div>-->
<!--            </el-card>-->
<!--          </div>-->
        </div>

        <!-- Right Column: KPIs + Device Status + Port Status + Tips -->
        <div class="col-right">
          <!-- Network KPIs -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📊 Network KPIs</div>
            <div class="kpi-row"><span class="kpi-row-left">Latency</span><strong>{{ latency }} ms</strong><span class="trend" :class="latency > 10 ? 'up' : 'stable'">{{ latency > 10 ? 'High' : 'Normal' }}</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Packet Loss</span><strong>{{ packetLoss }}%</strong><span class="trend" :class="packetLoss > 1 ? 'up' : 'stable'">{{ packetLoss > 1 ? 'High' : 'Normal' }}</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Jitter</span><strong>{{ jitter }} ms</strong><span class="trend stable">Target < 5ms</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Bandwidth Util</span><strong>{{ bandwidthUtil }}%</strong><span class="trend" :class="bandwidthUtil > 80 ? 'up' : 'stable'">{{ bandwidthUtil > 80 ? 'High' : 'Normal' }}</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Error Rate</span><strong>{{ errorRate }}%</strong><span class="trend" :class="errorRate > 0.1 ? 'up' : 'stable'">{{ errorRate > 0.1 ? 'Elevated' : 'Normal' }}</span></div>
          </el-card>

          <!-- Device Status Gauges -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🖧 Device Status</div>
            <div class="gauges-grid">
              <div class="gauge-item"><el-progress type="dashboard" :percentage="switchHealth" :color="healthColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ switchHealth }}%</span></template></el-progress><div class="gauge-label">Core Switches</div></div>
              <div class="gauge-item"><el-progress type="dashboard" :percentage="routerHealth" :color="healthColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ routerHealth }}%</span></template></el-progress><div class="gauge-label">Routers</div></div>
              <div class="gauge-item"><el-progress type="dashboard" :percentage="firewallHealth" :color="healthColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ firewallHealth }}%</span></template></el-progress><div class="gauge-label">Firewalls</div></div>
              <div class="gauge-item"><el-progress type="dashboard" :percentage="loadBalancerHealth" :color="healthColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ loadBalancerHealth }}%</span></template></el-progress><div class="gauge-label">Load Balancers</div></div>
            </div>
          </el-card>

          <!-- Port Status -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🔌 Port Status</div>
            <div class="setpoint-list">
              <div class="setpoint-row" v-for="item in portStatus" :key="item.label">
                <div class="sp-label">{{ item.label }}</div>
                <div class="sp-values"><span class="sp-set">Util: {{ item.util }}%</span><span class="sp-actual">Errors: {{ item.errors }}</span></div>
                <div class="sp-deviation" :class="item.statusClass">{{ item.status }}</div>
              </div>
            </div>
          </el-card>

          <!-- Network Tips -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">💡 Network Tips</div>
            <div class="tips-list">
              <div class="tip-item" v-for="(tip, idx) in networkTips" :key="idx">
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
      <div class="loading-tip">Initializing Network Devices</div>
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
  'Loading network data...',
  'Checking switch status...',
  'Monitoring traffic flows...',
  'Connecting to devices...',
  'Starting dashboard...',
  'Almost ready...'
]

const preloadSecurityImage = () => {
  return new Promise((resolve) => {
    const img = new Image()
    const imageUrl = 'https://aegisnx.com/wp-content/uploads/2026/05/NodeDevices.png'
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

// ==================== Core Network Data ====================
// Key metrics
const totalDevices = ref(156)
const onlineRate = ref(99.2)
const avgThroughput = ref(0)
const totalPorts = ref(1248)
const activeAlarms = ref(2)

// Network KPIs
const latency = ref(0)
const packetLoss = ref(0)
const jitter = ref(0)
const bandwidthUtil = ref(0)
const errorRate = ref(0)

// Device health scores
const switchHealth = ref(0)
const routerHealth = ref(0)
const firewallHealth = ref(0)
const loadBalancerHealth = ref(0)

// Network Status
const networkStatus = ref([
  { name: 'Core Switch', load: 0, status: 'Normal', color: '#34d399' },
  { name: 'Distribution', load: 0, status: 'Normal', color: '#34d399' },
  { name: 'Access Switch', load: 0, status: 'Normal', color: '#34d399' },
  { name: 'WAN Router', load: 0, status: 'Normal', color: '#34d399' }
])

// Recent events
const recentEvents = ref([
  { id: 1, severity: 'Warning', location: 'Core Switch 1', description: 'High CPU utilization (85%)', timestamp: '2 hours ago' },
  { id: 2, severity: 'Critical', location: 'WAN Router', description: 'Link flapping detected', timestamp: '4 hours ago' },
  { id: 3, severity: 'Info', location: 'Firewall Cluster', description: 'Firmware update available', timestamp: '8 hours ago' }
])

// Device health
const deviceHealth = ref([
  { subsystem: 'Switches', status: 'normal', statusText: '48 Online' },
  { subsystem: 'Routers', status: 'normal', statusText: '12 Online' },
  { subsystem: 'Firewalls', status: 'normal', statusText: 'Active' },
  { subsystem: 'Load Balancers', status: 'normal', statusText: 'Operational' },
  { subsystem: 'Management', status: 'normal', statusText: 'Connected' }
])

// Port status
const portStatus = ref([
  { label: 'Uplink Port 1', util: 0, errors: 0, status: 'Normal', statusClass: 'normal' },
  { label: 'Uplink Port 2', util: 0, errors: 0, status: 'Normal', statusClass: 'normal' },
  { label: 'Downlink Port', util: 0, errors: 2, status: 'Warning', statusClass: 'low' },
  { label: 'Management Port', util: 0, errors: 0, status: 'Normal', statusClass: 'normal' }
])

// Network Tips
const networkTips = ref([
  { icon: '🖧', title: 'Bandwidth Management', desc: 'QoS policies active for critical traffic', priority: 'Active' },
  { icon: '🔒', title: 'Security Update', desc: 'Firewall signatures updated', priority: 'Completed' }
])

// Color configurations
const healthColor = [{ color: '#34d399', percentage: 90 }, { color: '#f59e0b', percentage: 75 }, { color: '#ef4444', percentage: 60 }]

// ==================== Charts ====================
const throughputChartRef = ref(null)
const trafficChartRef = ref(null)
let throughputChart = null
let trafficChart = null

// Throughput history (24 hours)
const historyLength = 24
const throughputHistory = ref([])
const hourLabels = ref([])

const initThroughputHistory = () => {
  throughputHistory.value = []
  hourLabels.value = []
  const now = new Date()
  for (let i = historyLength - 1; i >= 0; i--) {
    const t = new Date(now - i * 3600000)
    hourLabels.value.push(t.toTimeString().slice(0, 5))
    throughputHistory.value.push(parseFloat((20 + Math.random() * 60).toFixed(1)))
  }
}

// Traffic distribution data
const trafficDistribution = ref([
  { name: 'Data Center', value: 45 },
  { name: 'User Traffic', value: 28 },
  { name: 'Backup', value: 15 },
  { name: 'Management', value: 7 },
  { name: 'Other', value: 5 }
])

// Throughput chart option
const getThroughputChartOption = () => {
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(15,25,45,0.9)', borderColor: '#3b82f6', textStyle: { color: '#e2e8f0' } },
    grid: { left: '0%', right: '0%', bottom: 0, top: 25, containLabel: true },
    xAxis: { type: 'category', data: hourLabels.value, axisLabel: { color: '#94a3b8', fontSize: 9, rotate: 30, interval: 3 }, axisLine: { lineStyle: { color: '#334155' } } },
    yAxis: { type: 'value', name: 'Throughput (Gbps)', nameTextStyle: { color: '#64748b', fontSize: 10 }, axisLabel: { color: '#94a3b8', fontSize: 10 }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } } },
    series: [{
      type: 'line', data: throughputHistory.value, smooth: true, symbol: 'circle', symbolSize: 4,
      lineStyle: { width: 2, color: '#60a5fa' }, areaStyle: { opacity: 0.3, color: '#60a5fa' },
      markLine: { data: [{ yAxis: 80, name: 'Threshold', lineStyle: { color: '#f59e0b', type: 'dashed' } }] }
    }]
  }
}

// Traffic distribution pie chart option
const getTrafficChartOption = () => {
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', backgroundColor: 'rgba(15,25,45,0.9)', borderColor: '#3b82f6', textStyle: { color: '#e2e8f0' } },
    legend: { orient: 'vertical', left: 'left', textStyle: { color: '#94a3b8', fontSize: 10 } },
    series: [{
      type: 'pie', radius: '55%', center: ['50%', '50%'],
      data: trafficDistribution.value.map(item => ({
        value: item.value,
        name: item.name,
        itemStyle: { color: ['#fbbf24', '#60a5fa', '#34d399', '#f97316', '#94a3b8'][trafficDistribution.value.indexOf(item)] }
      })),
      label: { show: true, formatter: '{b}: {d}%', fontSize: 10, color: '#cbd5e1' }
    }]
  }
}

// ==================== Chart Lifecycle ====================
const disposeCharts = () => {
  if (throughputChart) { throughputChart.dispose(); throughputChart = null }
  if (trafficChart) { trafficChart.dispose(); trafficChart = null }
}

const initCharts = async () => {
  await nextTick()
  for (let attempt = 0; attempt < 5; attempt++) {
    await new Promise(resolve => setTimeout(resolve, 100))
    const throughputDom = throughputChartRef.value
    const trafficDom = trafficChartRef.value
    if (!throughputDom || !trafficDom) continue
    if (throughputDom.clientWidth === 0 || throughputDom.clientHeight === 0) continue
    if (trafficDom.clientWidth === 0 || trafficDom.clientHeight === 0) continue
    disposeCharts()
    try {
      throughputChart = echarts.init(throughputDom)
      trafficChart = echarts.init(trafficDom)
      throughputChart.setOption(getThroughputChartOption())
      trafficChart.setOption(getTrafficChartOption())
      return
    } catch (e) { console.error('[initCharts] Error:', e) }
  }
}

const handleResize = () => {
  throughputChart?.resize()
  trafficChart?.resize()
}

let fullscreenTimer = null
const onFullscreenChange = () => {
  clearTimeout(fullscreenTimer)
  fullscreenTimer = setTimeout(handleResize, 350)
}

// ==================== Live Update ====================
let updateTimer = null

const updateAllData = () => {
  // Simulate network load variations
  const hour = new Date().getHours()
  const loadVariation = Math.sin(hour / 24 * Math.PI * 2) * 0.3

  // Update throughput
  const newThroughput = parseFloat((25 + loadVariation * 20 + Math.random() * 15).toFixed(1))
  avgThroughput.value = newThroughput

  // Update KPIs
  latency.value = Math.floor(2 + loadVariation * 5 + Math.random() * 3)
  packetLoss.value = parseFloat((0.05 + Math.random() * 0.2).toFixed(2))
  jitter.value = Math.floor(1 + Math.random() * 4)
  bandwidthUtil.value = Math.min(95, Math.floor(30 + loadVariation * 30 + Math.random() * 15))
  errorRate.value = parseFloat((0.02 + Math.random() * 0.15).toFixed(2))

  // Update device health scores
  switchHealth.value = Math.min(100, Math.max(85, 95 - Math.random() * 10))
  routerHealth.value = Math.min(100, Math.max(80, 92 - Math.random() * 12))
  firewallHealth.value = Math.min(100, Math.max(88, 96 - Math.random() * 8))
  loadBalancerHealth.value = Math.min(100, Math.max(82, 90 - Math.random() * 10))

  // Update network status based on load
  networkStatus.value = [
    { name: 'Core Switch', load: Math.min(100, Math.floor(40 + bandwidthUtil.value * 0.6)), status: bandwidthUtil.value > 80 ? 'High Load' : 'Normal', color: bandwidthUtil.value > 80 ? '#f59e0b' : '#34d399' },
    { name: 'Distribution', load: Math.min(100, Math.floor(35 + bandwidthUtil.value * 0.55)), status: bandwidthUtil.value > 80 ? 'High Load' : 'Normal', color: bandwidthUtil.value > 80 ? '#f59e0b' : '#34d399' },
    { name: 'Access Switch', load: Math.min(100, Math.floor(30 + bandwidthUtil.value * 0.5)), status: 'Normal', color: '#34d399' },
    { name: 'WAN Router', load: Math.min(100, Math.floor(45 + bandwidthUtil.value * 0.65)), status: bandwidthUtil.value > 75 ? 'Busy' : 'Normal', color: bandwidthUtil.value > 75 ? '#f59e0b' : '#34d399' }
  ]

  // Update port status
  portStatus.value = [
    { label: 'Uplink Port 1', util: Math.min(100, Math.floor(40 + bandwidthUtil.value * 0.5)), errors: Math.floor(Math.random() * 5), status: bandwidthUtil.value > 85 ? 'High Util' : 'Normal', statusClass: bandwidthUtil.value > 85 ? 'low' : 'normal' },
    { label: 'Uplink Port 2', util: Math.min(100, Math.floor(35 + bandwidthUtil.value * 0.45)), errors: Math.floor(Math.random() * 3), status: 'Normal', statusClass: 'normal' },
    { label: 'Downlink Port', util: Math.min(100, Math.floor(50 + bandwidthUtil.value * 0.4)), errors: Math.floor(2 + Math.random() * 3), status: packetLoss.value > 0.5 ? 'High Errors' : 'Normal', statusClass: packetLoss.value > 0.5 ? 'low' : 'normal' },
    { label: 'Management Port', util: Math.min(100, Math.floor(5 + Math.random() * 10)), errors: 0, status: 'Normal', statusClass: 'normal' }
  ]

  // Update device health occasionally
  if (Math.random() > 0.95) {
    deviceHealth.value = [
      { subsystem: 'Switches', status: switchHealth.value < 85 ? 'warning' : 'normal', statusText: `${Math.floor(48 * switchHealth.value / 100)} Online` },
      { subsystem: 'Routers', status: routerHealth.value < 80 ? 'warning' : 'normal', statusText: `${Math.floor(12 * routerHealth.value / 100)} Online` },
      { subsystem: 'Firewalls', status: firewallHealth.value < 85 ? 'warning' : 'normal', statusText: firewallHealth.value < 85 ? 'Degraded' : 'Active' },
      { subsystem: 'Load Balancers', status: loadBalancerHealth.value < 80 ? 'warning' : 'normal', statusText: loadBalancerHealth.value < 80 ? 'Check' : 'Operational' },
      { subsystem: 'Management', status: 'normal', statusText: 'Connected' }
    ]
  }

  // Update tips occasionally
  if (Math.random() > 0.7) {
    const tipPool = [
      { icon: '🖧', title: 'Bandwidth Management', desc: `Current util: ${bandwidthUtil.value}%`, priority: bandwidthUtil.value > 85 ? 'High Load' : 'Normal' },
      { icon: '⚠️', title: 'Latency Alert', desc: `Latency: ${latency.value}ms`, priority: latency.value > 15 ? 'High' : 'Normal' },
      { icon: '🔧', title: 'Switch Health', desc: `Core switch health: ${switchHealth.value}%`, priority: switchHealth.value < 85 ? 'Check' : 'Good' }
    ]
    networkTips.value = tipPool.sort(() => Math.random() - 0.5).slice(0, 2)
  }

  // Update charts
  if (throughputChart && trafficChart) {
    const now = new Date()
    const timeLabel = now.toTimeString().slice(0, 5)
    const lastHour = hourLabels.value[hourLabels.value.length - 1]

    if (lastHour !== timeLabel) {
      hourLabels.value.push(timeLabel)
      if (hourLabels.value.length > historyLength) hourLabels.value.shift()
      throughputHistory.value.push(avgThroughput.value)
      if (throughputHistory.value.length > historyLength) throughputHistory.value.shift()

      throughputChart.setOption({
        xAxis: { data: hourLabels.value },
        series: [{ data: throughputHistory.value }]
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
  avgThroughput.value = 42.5
  latency.value = 4
  packetLoss.value = 0.08
  jitter.value = 2
  bandwidthUtil.value = 55
  errorRate.value = 0.05
  switchHealth.value = 94
  routerHealth.value = 91
  firewallHealth.value = 96
  loadBalancerHealth.value = 88

  initThroughputHistory()
  await initCharts()

  if (throughputChart && trafficChart) {
    updateTimer = setInterval(updateAllData, 5000)
  }

  window.addEventListener('resize', handleResize)
  document.addEventListener('fullscreenchange', onFullscreenChange)

  routeWatch = watch(() => route.fullPath, async () => {
    initThroughputHistory()
    await initCharts()
    if (throughputChart && trafficChart && !updateTimer) {
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