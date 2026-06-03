<template>
  <div v-if="isPageLoaded" class="server-page">
    <div class="main-view">
      <div class="three-columns">
        <!-- Left Column: Key Metrics + System Status + Recent Events + Device Health -->
        <div class="col-left">
          <div class="title-row" v-if="isMobile">
            <h1 class="page-title">Servers</h1>
            <span class="live-time">{{ currentTime }}</span>
          </div>
          <div class="card-img" v-if="isMobile">
            <img :src="serverImageUrl" alt="Server Infrastructure 3D View" />
          </div>

          <!-- Key Metrics -->
          <el-card class="card glass-card" shadow="hover">
            <template #header>
              <div class="card-header">📈 Server Metrics</div>
            </template>
            <div class="metrics-list">
              <div class="metric-row"><div class="metric-icon">🖥️</div><div class="metric-label">Total Servers</div><div class="metric-value">{{ totalServers }}</div></div>
              <div class="metric-row"><div class="metric-icon">✅</div><div class="metric-label">Online</div><div class="metric-value">{{ onlineServers }}</div></div>
              <div class="metric-row"><div class="metric-icon">⚠️</div><div class="metric-label">Warning</div><div class="metric-value" :class="{ 'has-warning': warningServers > 0 }">{{ warningServers }}</div></div>
              <div class="metric-row"><div class="metric-icon">🚨</div><div class="metric-label">Critical</div><div class="metric-value" :class="{ 'has-critical': criticalServers > 0 }">{{ criticalServers }}</div></div>
              <div class="metric-row"><div class="metric-icon">📊</div><div class="metric-label">Avg CPU</div><div class="metric-value">{{ avgCpu }}%</div></div>
            </div>
          </el-card>

          <!-- Server Status by Rack -->
          <el-card class="card glass-card" shadow="hover">
            <template #header>
              <div class="card-header">🖥️ Server Status by Rack</div>
            </template>
            <div class="mode-list">
              <div class="mode-row" v-for="rack in rackStatus" :key="rack.name">
                <div class="mode-name">{{ rack.name }}</div>
                <div class="mode-bar-bg">
                  <div class="mode-bar-fill" :style="{ width: rack.health + '%', background: rack.color }"></div>
                </div>
                <div class="mode-value">{{ rack.health }}%</div>
                <div class="mode-power">{{ rack.status }}</div>
              </div>
            </div>
          </el-card>

          <!-- Virtualization Status -->
          <el-card class="card glass-card" shadow="hover">
            <template #header>
              <div class="card-header">☁️ Virtualization</div>
            </template>
            <div class="mode-list">
              <div class="mode-row" v-for="vm in virtualizationStatus" :key="vm.name">
                <div class="mode-name">{{ vm.name }}</div>
                <div class="mode-bar-bg">
                  <div class="mode-bar-fill" :style="{ width: vm.utilization + '%', background: vm.color }"></div>
                </div>
                <div class="mode-value">{{ vm.utilization }}%</div>
                <div class="mode-power">{{ vm.status }}</div>
              </div>
            </div>
          </el-card>

          <!-- Device Health -->
          <el-card class="card glass-card" shadow="hover">
            <template #header>
              <div class="card-header">💚 Device Health</div>
            </template>
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
            <h1 class="page-title">Servers</h1>
            <span class="live-time" v-if="isFullscreen">{{ currentTime }}</span>
          </div>
          <div class="card-img" v-if="!isMobile">
            <img :src="serverImageUrl" alt="Server Infrastructure 3D View" />
          </div>
          <div class="cart-view">
            <!-- CPU & Memory Trend -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <template #header>
                <div class="card-header">📊 CPU & Memory Trend (24h)</div>
              </template>
              <div ref="cpuChartRef" class="chart-box"></div>
            </el-card>
            <!-- Workload Distribution -->
            <el-card class="card glass-card chart-card" shadow="hover">
              <template #header>
                <div class="card-header">🔄 Workload Distribution</div>
              </template>
              <div ref="workloadChartRef" class="chart-box"></div>
            </el-card>
          </div>
        </div>

        <!-- Right Column: KPIs + Top Servers + Alerts + Tips -->
        <div class="col-right">
          <!-- Server KPIs -->
          <el-card class="card glass-card" shadow="hover">
            <template #header>
              <div class="card-header">📊 Server KPIs</div>
            </template>
            <div class="kpi-row"><span class="kpi-row-left">Avg Memory</span><strong>{{ avgMemory }}%</strong><span class="trend" :class="avgMemory > 80 ? 'up' : 'stable'">{{ avgMemory > 80 ? 'High' : 'Normal' }}</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Avg Disk</span><strong>{{ avgDisk }}%</strong><span class="trend" :class="avgDisk > 85 ? 'up' : 'stable'">{{ avgDisk > 85 ? 'High' : 'Normal' }}</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Total VMs</span><strong>{{ totalVms }}</strong><span class="trend up">+{{ vmGrowth }}%</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Uptime</span><strong>{{ uptime }} days</strong><span class="trend stable">Avg per server</span></div>
            <div class="kpi-row"><span class="kpi-row-left">Power Consumption</span><strong>{{ powerConsumption }} kW</strong><span class="trend" :class="powerConsumption > 150 ? 'up' : 'stable'">{{ powerConsumption > 150 ? 'High' : 'Normal' }}</span></div>
          </el-card>

          <!-- Top Servers Gauges -->
          <el-card class="card glass-card" shadow="hover">
            <template #header>
              <div class="card-header">🔥 Top CPU Servers</div>
            </template>
            <div class="gauges-grid">
              <div class="gauge-item"><el-progress type="dashboard" :percentage="topServer1Cpu" :color="cpuColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ topServer1Cpu }}%</span></template></el-progress><div class="gauge-label">{{ topServer1Name }}</div></div>
              <div class="gauge-item"><el-progress type="dashboard" :percentage="topServer2Cpu" :color="cpuColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ topServer2Cpu }}%</span></template></el-progress><div class="gauge-label">{{ topServer2Name }}</div></div>
              <div class="gauge-item"><el-progress type="dashboard" :percentage="topServer3Cpu" :color="cpuColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ topServer3Cpu }}%</span></template></el-progress><div class="gauge-label">{{ topServer3Name }}</div></div>
              <div class="gauge-item"><el-progress type="dashboard" :percentage="topServer4Cpu" :color="cpuColor" :width="90" :stroke-width="4"><template #default><span class="percentage-label">{{ topServer4Cpu }}%</span></template></el-progress><div class="gauge-label">{{ topServer4Name }}</div></div>
            </div>
          </el-card>

          <!-- Recent Alerts -->
          <el-card class="card glass-card" shadow="hover">
            <template #header>
              <div class="card-header">⚠️ Recent Alerts</div>
            </template>
            <div class="events-list">
              <div class="alert-item" v-for="alert in recentAlerts" :key="alert.id">
                <div class="alert-icon">{{ alert.severity === 'critical' ? '🔴' : (alert.severity === 'warning' ? '🟡' : '🔵') }}</div>
                <div class="alert-details">
                  <div class="alert-title">{{ alert.title }}</div>
                  <div class="alert-desc">{{ alert.desc }}</div>
                  <div class="alert-time">{{ alert.time }}</div>
                </div>
              </div>
            </div>
          </el-card>

          <!-- Server Tips -->
          <el-card class="card glass-card" shadow="hover">
            <template #header>
              <div class="card-header">💡 Server Tips</div>
            </template>
            <div class="tips-list">
              <div class="tip-item" v-for="(tip, idx) in serverTips" :key="idx">
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
        <div class="loading-tip">Initializing Server Infrastructure</div>
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
const serverImageUrl = ref('')

const loadingMessages = [
  'Preparing assets...',
  'Loading server data...',
  'Checking CPU metrics...',
  'Initializing virtualization...',
  'Connecting to monitoring...',
  'Starting dashboard...',
  'Almost ready...'
]

// ==================== Preload Assets ====================
const preloadServerImage = () => {
  return new Promise((resolve) => {
    const img = new Image()
    const imageUrl = 'https://aegisnx.com/wp-content/uploads/2026/05/5998b812-5898-11e7-8fc1-1866daf0eb58.jpg'
    img.onload = () => { serverImageUrl.value = imageUrl; resolve() }
    img.onerror = () => { serverImageUrl.value = imageUrl; resolve() }
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
  await preloadServerImage()
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

// ==================== Core Server Data ====================
const totalServers = ref(128)
const onlineServers = ref(0)
const warningServers = ref(0)
const criticalServers = ref(0)
const avgCpu = ref(0)
const avgMemory = ref(0)
const avgDisk = ref(0)
const totalVms = ref(0)
const vmGrowth = ref(8)
const uptime = ref(0)
const powerConsumption = ref(0)

// Top servers
const topServer1Name = ref('DB-SRV-01')
const topServer1Cpu = ref(0)
const topServer2Name = ref('APP-SRV-05')
const topServer2Cpu = ref(0)
const topServer3Name = ref('WEB-SRV-12')
const topServer3Cpu = ref(0)
const topServer4Name = ref('VM-HOST-03')
const topServer4Cpu = ref(0)

// Rack status
const rackStatus = ref([
  { name: 'Rack A', health: 0, status: 'Optimal', color: '#34d399' },
  { name: 'Rack B', health: 0, status: 'Optimal', color: '#34d399' },
  { name: 'Rack C', health: 0, status: 'Optimal', color: '#34d399' },
  { name: 'Rack D', health: 0, status: 'Warning', color: '#f59e0b' }
])

// Virtualization status
const virtualizationStatus = ref([
  { name: 'VMware Cluster', utilization: 0, status: 'Normal', color: '#34d399' },
  { name: 'Hyper-V Pool', utilization: 0, status: 'Normal', color: '#34d399' },
  { name: 'KVM Cluster', utilization: 0, status: 'Normal', color: '#34d399' }
])

// Recent alerts
const recentAlerts = ref([
  { id: 1, severity: 'warning', title: 'High CPU Usage', desc: 'DB-SRV-01 CPU at 92% for 10 min', time: '5 min ago' },
  { id: 2, severity: 'critical', title: 'Disk Space Critical', desc: 'APP-SRV-05 disk usage 95%', time: '12 min ago' },
  { id: 3, severity: 'info', title: 'Memory Leak Detected', desc: 'WEB-SRV-12 memory usage increasing', time: '28 min ago' }
])

// Device health
const deviceHealth = ref([
  { subsystem: 'Physical Servers', status: 'normal', statusText: 'Online' },
  { subsystem: 'Virtual Machines', status: 'normal', statusText: 'Running' },
  { subsystem: 'Storage', status: 'normal', statusText: 'Healthy' },
  { subsystem: 'Network', status: 'normal', statusText: 'Connected' },
  { subsystem: 'Power Supplies', status: 'normal', statusText: 'Redundant' }
])

// Server Tips
const serverTips = ref([
  { icon: '🖥️', title: 'Load Balancing', desc: 'Consider redistributing VMs across hosts', priority: 'Recommendation' },
  { icon: '💾', title: 'Storage Optimization', desc: 'Deduplication ratio at 2.5x', priority: 'Good' }
])

// Color configurations
const cpuColor = [{ color: '#34d399', percentage: 50 }, { color: '#f59e0b', percentage: 70 }, { color: '#ef4444', percentage: 85 }]

// ==================== Charts ====================
const cpuChartRef = ref(null)
const workloadChartRef = ref(null)
let cpuChart = null
let workloadChart = null

// CPU & Memory history (24 hours)
const historyLength = 24
const cpuHistory = ref([])
const memoryHistory = ref([])
const hourLabels = ref([])

const initCpuHistory = () => {
  cpuHistory.value = []
  memoryHistory.value = []
  hourLabels.value = []
  const now = new Date()
  for (let i = historyLength - 1; i >= 0; i--) {
    const t = new Date(now - i * 3600000)
    hourLabels.value.push(t.toTimeString().slice(0, 5))
    cpuHistory.value.push(parseFloat((35 + Math.random() * 30).toFixed(1)))
    memoryHistory.value.push(parseFloat((45 + Math.random() * 25).toFixed(1)))
  }
}

// Workload distribution data
const workloadDistribution = ref([
  { name: 'Web Servers', value: 35 },
  { name: 'App Servers', value: 28 },
  { name: 'Database', value: 22 },
  { name: 'Storage', value: 10 },
  { name: 'Management', value: 5 }
])

// CPU chart option
const getCpuChartOption = () => {
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(15,25,45,0.9)', borderColor: '#3b82f6', textStyle: { color: '#e2e8f0' } },
    legend: { data: ['CPU Usage (%)', 'Memory Usage (%)'], textStyle: { color: '#94a3b8', fontSize: 9 }, top: 0 },
    grid: { left: '8%', right: '8%', bottom: '5%', top: '15%', containLabel: true },
    xAxis: { type: 'category', data: hourLabels.value, axisLabel: { color: '#94a3b8', fontSize: 9, rotate: 30, interval: 3 }, axisLine: { lineStyle: { color: '#334155' } } },
    yAxis: { type: 'value', name: 'Usage (%)', nameTextStyle: { color: '#64748b', fontSize: 10 }, axisLabel: { color: '#94a3b8', fontSize: 10 }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } }, min: 0, max: 100 },
    series: [
      { name: 'CPU Usage (%)', type: 'line', data: cpuHistory.value, smooth: true, symbol: 'circle', symbolSize: 4, lineStyle: { width: 2, color: '#60a5fa' }, areaStyle: { opacity: 0.3, color: '#60a5fa' }, markLine: { data: [{ yAxis: 80, name: 'Warning', lineStyle: { color: '#f59e0b', type: 'dashed' } }] } },
      { name: 'Memory Usage (%)', type: 'line', data: memoryHistory.value, smooth: true, symbol: 'circle', symbolSize: 4, lineStyle: { width: 2, color: '#ef4444' }, areaStyle: { opacity: 0.3, color: '#ef4444' } }
    ]
  }
}

// Workload distribution pie chart option
const getWorkloadChartOption = () => {
  const colors = ['#fbbf24', '#60a5fa', '#34d399', '#f97316', '#94a3b8']
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', backgroundColor: 'rgba(15,25,45,0.9)', borderColor: '#3b82f6', textStyle: { color: '#e2e8f0' } },
    legend: { orient: 'vertical', left: 'left', textStyle: { color: '#94a3b8', fontSize: 10 } },
    series: [{
      type: 'pie', radius: '55%', center: ['55%', '55%'],
      data: workloadDistribution.value.map((item, idx) => ({
        value: item.value,
        name: item.name,
        itemStyle: { color: colors[idx % colors.length] }
      })),
      label: { show: true, formatter: '{b}: {d}%', fontSize: 10, color: '#cbd5e1' },
      emphasis: { scale: true, label: { show: true, fontSize: 12 } }
    }]
  }
}

// ==================== Data Update Functions ====================
const updateStatsFromServers = () => {
  // Simulate server metrics
  const hour = new Date().getHours()
  const loadVariation = Math.sin(hour / 24 * Math.PI * 2) * 15

  const newAvgCpu = parseFloat((35 + loadVariation + Math.random() * 15).toFixed(1))
  avgCpu.value = newAvgCpu
  avgMemory.value = parseFloat((55 + loadVariation * 0.5 + Math.random() * 10).toFixed(1))
  avgDisk.value = parseFloat((60 + Math.random() * 15).toFixed(1))

  // Server counts
  const totalOnline = Math.floor(110 + Math.random() * 15)
  onlineServers.value = totalOnline
  warningServers.value = Math.floor(5 + Math.random() * 8)
  criticalServers.value = Math.floor(1 + Math.random() * 3)

  // Virtual machines
  totalVms.value = Math.floor(400 + Math.random() * 100)
  vmGrowth.value = Math.floor(5 + Math.random() * 10)
  uptime.value = Math.floor(90 + Math.random() * 30)
  powerConsumption.value = parseFloat((120 + loadVariation * 2 + Math.random() * 20).toFixed(1))

  // Top servers CPU
  topServer1Cpu.value = Math.min(98, Math.floor(75 + Math.random() * 20))
  topServer2Cpu.value = Math.min(95, Math.floor(70 + Math.random() * 20))
  topServer3Cpu.value = Math.min(92, Math.floor(65 + Math.random() * 20))
  topServer4Cpu.value = Math.min(90, Math.floor(60 + Math.random() * 20))

  // Rack status
  rackStatus.value = [
    { name: 'Rack A', health: Math.min(100, Math.floor(85 + Math.random() * 10)), status: 'Optimal', color: '#34d399' },
    { name: 'Rack B', health: Math.min(100, Math.floor(80 + Math.random() * 15)), status: 'Optimal', color: '#34d399' },
    { name: 'Rack C', health: Math.min(100, Math.floor(75 + Math.random() * 15)), status: avgCpu.value > 70 ? 'Warning' : 'Optimal', color: avgCpu.value > 70 ? '#f59e0b' : '#34d399' },
    { name: 'Rack D', health: Math.min(100, Math.floor(70 + Math.random() * 15)), status: 'Warning', color: '#f59e0b' }
  ]

  // Virtualization status
  virtualizationStatus.value = [
    { name: 'VMware Cluster', utilization: Math.min(100, Math.floor(65 + Math.random() * 20)), status: 'Normal', color: '#34d399' },
    { name: 'Hyper-V Pool', utilization: Math.min(100, Math.floor(55 + Math.random() * 20)), status: 'Normal', color: '#34d399' },
    { name: 'KVM Cluster', utilization: Math.min(100, Math.floor(45 + Math.random() * 20)), status: 'Normal', color: '#34d399' }
  ]

  // Update device health occasionally
  if (Math.random() > 0.95) {
    deviceHealth.value = [
      { subsystem: 'Physical Servers', status: criticalServers.value > 2 ? 'warning' : 'normal', statusText: criticalServers.value > 2 ? `${criticalServers.value} Critical` : 'Online' },
      { subsystem: 'Virtual Machines', status: 'normal', statusText: `${totalVms.value} Running` },
      { subsystem: 'Storage', status: avgDisk.value > 85 ? 'warning' : 'normal', statusText: avgDisk.value > 85 ? 'High Usage' : 'Healthy' },
      { subsystem: 'Network', status: 'normal', statusText: 'Connected' },
      { subsystem: 'Power Supplies', status: 'normal', statusText: 'Redundant' }
    ]
  }

  // Update tips occasionally
  if (Math.random() > 0.7) {
    const tipPool = [
      { icon: '🖥️', title: 'Load Balancing', desc: `CPU avg: ${avgCpu.value}%`, priority: avgCpu.value > 70 ? 'Action Needed' : 'Good' },
      { icon: '💾', title: 'Storage Optimization', desc: `Disk usage: ${avgDisk.value}%`, priority: avgDisk.value > 85 ? 'Critical' : 'Normal' },
      { icon: '🔧', title: 'Maintenance', desc: `${criticalServers.value} servers need attention`, priority: criticalServers.value > 0 ? 'Alert' : 'OK' }
    ]
    serverTips.value = tipPool.sort(() => Math.random() - 0.5).slice(0, 2)
  }
}

// ==================== Chart Lifecycle ====================
const disposeCharts = () => {
  if (cpuChart) { cpuChart.dispose(); cpuChart = null }
  if (workloadChart) { workloadChart.dispose(); workloadChart = null }
}

const resizeCharts = () => {
  cpuChart?.resize()
  workloadChart?.resize()
}

const initCharts = async () => {
  await nextTick()
  for (let attempt = 0; attempt < 5; attempt++) {
    await new Promise(resolve => setTimeout(resolve, 150))
    const cpuDom = cpuChartRef.value
    const workloadDom = workloadChartRef.value
    if (!cpuDom || !workloadDom) continue
    if (cpuDom.clientWidth === 0 || cpuDom.clientHeight === 0) continue
    if (workloadDom.clientWidth === 0 || workloadDom.clientHeight === 0) continue
    disposeCharts()
    try {
      cpuChart = echarts.init(cpuDom)
      workloadChart = echarts.init(workloadDom)
      cpuChart.setOption(getCpuChartOption())
      workloadChart.setOption(getWorkloadChartOption())
      return
    } catch (e) { console.error('[initCharts] Error:', e) }
  }
}

const handleResize = () => { resizeCharts() }

let fullscreenTimer = null
const onFullscreenChange = () => {
  clearTimeout(fullscreenTimer)
  fullscreenTimer = setTimeout(resizeCharts, 300)
}

// ==================== Live Update ====================
let updateTimer = null

const updateAllData = () => {
  updateStatsFromServers()

  // Update charts
  if (cpuChart && workloadChart) {
    const now = new Date()
    const timeLabel = now.toTimeString().slice(0, 5)
    const lastHour = hourLabels.value[hourLabels.value.length - 1]

    if (lastHour !== timeLabel) {
      hourLabels.value.push(timeLabel)
      if (hourLabels.value.length > historyLength) hourLabels.value.shift()
      cpuHistory.value.push(avgCpu.value)
      memoryHistory.value.push(avgMemory.value)
      if (cpuHistory.value.length > historyLength) cpuHistory.value.shift()
      if (memoryHistory.value.length > historyLength) memoryHistory.value.shift()

      cpuChart.setOption({
        xAxis: { data: hourLabels.value },
        series: [{ data: cpuHistory.value }, { data: memoryHistory.value }]
      })
    }
  }
}

let routeWatch = null
let resizeObserver = null

const setupResizeObserver = () => {
  if (cpuChartRef.value && workloadChartRef.value) {
    resizeObserver = new ResizeObserver(() => resizeCharts())
    resizeObserver.observe(cpuChartRef.value)
    resizeObserver.observe(workloadChartRef.value)
  }
}

const isMobile = ref(false)
const checkMobile = () => { isMobile.value = window.innerWidth < 768 }

onMounted(async () => {
  checkMobile()
  updateTime()
  clockTimer = setInterval(updateTime, 1000)

  await preloadAssets()

  // Initialize values
  avgCpu.value = 48.5
  avgMemory.value = 62.3
  avgDisk.value = 58.7
  onlineServers.value = 118
  warningServers.value = 7
  criticalServers.value = 3
  totalVms.value = 487
  uptime.value = 112
  powerConsumption.value = 138
  topServer1Cpu.value = 88
  topServer2Cpu.value = 82
  topServer3Cpu.value = 76
  topServer4Cpu.value = 71

  updateStatsFromServers()
  initCpuHistory()
  await initCharts()
  setupResizeObserver()

  if (cpuChart && workloadChart) {
    updateTimer = setInterval(updateAllData, 5000)
  }

  window.addEventListener('resize', handleResize)
  document.addEventListener('fullscreenchange', onFullscreenChange)

  routeWatch = watch(() => route.fullPath, async () => {
    initCpuHistory()
    await initCharts()
    if (cpuChart && workloadChart && !updateTimer) {
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
  if (resizeObserver) resizeObserver.disconnect()
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

/* Main Server Page Styles */
.server-page {
  height: 100%;
  background: radial-gradient(circle at 10% 20%, #0a1620, #03060c);
  padding: 24px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  animation: fadeIn 0.5s ease-out;
  overflow: hidden;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.title-row { display: flex; align-items: center; justify-content: center; position: relative; flex-shrink: 0; }
.page-title { font-size: 32px; font-weight: 800; background: linear-gradient(135deg, #e2e8f0, #60a5fa); -webkit-background-clip: text; background-clip: text; color: transparent; letter-spacing: 1px; text-shadow: 0 0 8px rgba(96,165,250,0.4); margin: 0; }
.live-time { position: absolute; right: 0; font-size: 14px; font-weight: 600; color: #facc15; font-family: monospace; letter-spacing: 1px; text-shadow: 0 0 6px rgba(250,204,21,0.3); padding: 6px 14px; background: rgba(15,25,45,0.6); border: 1px solid rgba(59,130,246,0.3); border-radius: 10px; backdrop-filter: blur(8px); }
.main-view { flex: 1; display: flex; flex-direction: column; min-height: 0; overflow: hidden; }
.three-columns { flex: 1; display: flex; gap: 20px; align-items: stretch; min-height: 0; overflow: hidden; }
.col-left, .col-right { width: 300px; flex-shrink: 0; display: flex; flex-direction: column; gap: 20px; overflow-y: auto; min-height: 0; scrollbar-width: none; -ms-overflow-style: none; }
.col-left::-webkit-scrollbar, .col-right::-webkit-scrollbar { width: 0; background: transparent; display: none; }
.col-center { flex: 1; display: flex; flex-direction: column; gap: 20px; min-height: 0; overflow: hidden; }
.glass-card, .card-img { background: rgba(15,25,45,0.6); backdrop-filter: blur(12px); border: 1px solid rgba(59,130,246,0.3); border-radius: 20px; transition: all 0.3s; }
.glass-card:hover { background: rgba(15,25,45,0.8); border-color: rgba(59,130,246,0.6); transform: translateY(-3px); }
.card { background: transparent; }
.card-img { overflow: hidden; background: rgba(0,0,0,0.3); flex-shrink: 0; }
.card-img img { width: 100%; display: block; height: auto; border-radius: 10px; }
.card-header { font-weight: 600; font-size: 16px; color: #e2e8f0; border-left: 4px solid #3b82f6; padding-left: 10px; }

/* Metrics List */
.metrics-list { display: flex; flex-direction: column; }
.metric-row { display: flex; align-items: center; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid rgba(148,163,184,0.2); }
.metric-row .metric-icon { font-size: 24px; width: 36px; opacity: 0.9; }
.metric-row .metric-label { flex: 1; font-size: 14px; color: #94a3b8; padding-left: 12px; font-weight: bold; }
.metric-row .metric-value { font-size: 18px; font-weight: 600; color: #facc15; text-align: right; font-family: monospace; }
.metric-value.has-warning { color: #f59e0b; }
.metric-value.has-critical { color: #ef4444; }

/* Mode List */
.mode-list { display: flex; flex-direction: column; gap: 12px; }
.mode-row { display: flex; align-items: center; gap: 8px; font-size: 12px; color: #cbd5e1; }
.mode-name { width: 100px; flex-shrink: 0; font-weight: bold; }
.mode-bar-bg { flex: 1; height: 6px; background: rgba(148,163,184,0.15); border-radius: 3px; overflow: hidden; }
.mode-bar-fill { height: 100%; border-radius: 3px; transition: width 0.5s; }
.mode-value { width: 35px; text-align: right; color: #facc15; }
.mode-power { width: 55px; text-align: right; color: #94a3b8; font-weight: bold; }

/* Health List */
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

/* Center Charts */
.cart-view { flex: 1; display: flex; background: transparent; gap: 20px; min-height: 0; overflow: hidden; }
.chart-card { flex: 1; display: flex; flex-direction: column; min-height: 0; overflow: hidden; }
.chart-card .card-header { flex-shrink: 0; }
.chart-box { flex: 1; width: 100%; min-height: 0; overflow: hidden; }

/* KPI rows */
.kpi-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; font-size: 13px; color: #cbd5e6; }
.kpi-row-left { min-width: 100px; max-width: 100px; text-align: left; }
.kpi-row strong { font-size: 16px; color: #facc15; text-align: center; }
.trend { width: 70px; font-size: 11px; margin-left: 8px; text-align: right; font-weight: bold; }
.trend.up { color: #34d399; }
.trend.stable { color: #fbbf24; }

/* Gauges Grid */
.gauges-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.gauge-item { text-align: center; }
.gauge-label { font-size: 13px; color: #cbd5e1; margin-top: 0px; height: 20px; text-align: center; }
.percentage-label { display: block; margin-top: 10px; font-size: 12px; color: #facc15; font-weight: bold; }

/* Alert Items */
.events-list { display: flex; flex-direction: column; gap: 10px; max-height: 280px; overflow-y: auto; scrollbar-width: none; }
.events-list::-webkit-scrollbar { display: none; }
.alert-item { display: flex; gap: 10px; padding: 8px 10px; background: rgba(255,255,255,0.03); border-radius: 8px; border-left: 3px solid #f59e0b; }
.alert-icon { font-size: 16px; flex-shrink: 0; }
.alert-details { flex: 1; }
.alert-title { font-size: 12px; font-weight: 600; color: #e2e8f0; }
.alert-desc { font-size: 11px; color: #94a3b8; margin-top: 2px; }
.alert-time { font-size: 10px; color: #64748b; margin-top: 2px; }

/* Tips List */
.tips-list { display: flex; flex-direction: column; gap: 12px; max-height: 180px; overflow-y: auto; scrollbar-width: none; }
.tips-list::-webkit-scrollbar { display: none; }
.tip-item { display: flex; gap: 10px; padding: 8px 10px; background: rgba(59,130,246,0.08); border-radius: 8px; border-left: 3px solid #3b82f6; }
.tip-icon { font-size: 18px; flex-shrink: 0; margin-top: 2px; }
.tip-content { flex: 1; }
.tip-title { font-size: 12px; font-weight: 600; color: #e2e8f0; margin-bottom: 2px; }
.tip-desc { font-size: 11px; color: #94a3b8; line-height: 1.4; margin-bottom: 2px; }
.tip-saving { font-size: 10px; color: #facc15; font-weight: 600; }

/* Mobile Responsive */
@media (max-width: 768px) {
  .server-page { padding: 16px; overflow-y: auto; }
  .title-row { flex-direction: column; align-items: stretch; gap: 10px; margin-bottom: 10px; }
  .page-title { font-size: 26px; text-align: center; }
  .live-time { position: static; text-align: center; width: fit-content; margin: 0 auto; font-size: 12px; padding: 4px 12px; }
  .three-columns { flex-direction: column; gap: 16px; overflow: visible; }
  .col-left, .col-right { width: 100%; overflow-y: visible; gap: 16px; }
  .col-center { gap: 16px; }
  .cart-view { flex-direction: column; gap: 16px; min-height: 400px; }
  .chart-card { min-height: 280px; }
  .mode-name { width: 90px; font-size: 11px; }
  .mode-value { width: 30px; font-size: 11px; }
  .mode-power { width: 50px; font-size: 10px; }
  .metric-row .metric-icon { font-size: 20px; width: 28px; }
  .metric-row .metric-label { font-size: 12px; padding-left: 8px; }
  .metric-row .metric-value { font-size: 16px; }
  .gauges-grid { gap: 8px; }
  :deep(.el-progress-circle) { width: 80px !important; height: 80px !important; }
  :deep(.el-progress__text) { font-size: 10px !important; }
  .card-img img { max-height: 160px; object-fit: cover; }
}

/* Global styles */
:deep(.el-card__body) { scrollbar-width: none; -ms-overflow-style: none; overflow: visible !important; padding: 16px; }
:deep(.el-card__body::-webkit-scrollbar) { display: none; }
:deep(.col-left .el-card), :deep(.col-right .el-card) { overflow: visible; height: auto; flex-shrink: 0; }
:deep(.chart-card .el-card__body) { height: 100%; display: flex; flex-direction: column; overflow: hidden; padding: 12px; }
:deep(.el-card__header) { border-bottom: none; padding-bottom: 0; }
</style>