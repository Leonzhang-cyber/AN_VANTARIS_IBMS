<template>
  <div v-if="isBackgroundLoaded" class="dashboard">
    <!-- Top Header - with switch buttons -->
    <div class="top-header">
      <div class="header-left">
        <div class="button-group1" v-if="!isMobile"></div>
        <div class="button-group" v-if="isMobile">
          <!-- 节能模式 -->
          <div class="switch-item">
            <span class="switch-label">Energy Saving</span>
            <el-switch
                v-model="isEnergySavingActive"
                size="large"
                :active-value="true"
                :inactive-value="false"
                @change="handleEnergySavingToggle"
                class="energy-saving-switch"
                active-color="#10b981"
                inactive-color="#475569"
            />
          </div>

          <!-- 报告 -->
          <div class="switch-item">
            <span class="switch-label">Report</span>
            <el-switch
                v-model="showEnergyReport"
                size="large"
                :active-value="true"
                :inactive-value="false"
                :disabled="!isEnergySavingActive"
                class="report-switch"
                active-color="#3b82f6"
                inactive-color="#475569"
            />
          </div>
        </div>
      </div>
      <div class="header-title">
        <div class="main-title">SMART FACTORY<br></div>
      </div>
      <div class="datetime" v-if="isFullscreen">{{ currentTime }}</div>
      <div class="datetimeview1" v-if="!isFullscreen"></div>
    </div>

    <!-- Main Content -->
    <div class="content-area">
      <!-- Left Panel -->
      <div class="left-panel">
        <div class="glass-card resources">
          <div class="card-title">💧⚡🔥 Resource Consumption</div>
          <div class="resource-grid">
            <div class="resource-item">
              <el-progress type="circle" :percentage="waterPercent" :width="80" :stroke-width="8" color="#3b82f6" />
              <div class="resource-label">Water</div>
              <div class="resource-value">{{ waterUsage }} L</div>
              <div class="resource-cost">💰 ${{ waterCost }}</div>
            </div>
            <div class="resource-item">
              <el-progress type="circle" :percentage="elecPercent" :width="80" :stroke-width="8" color="#f59e0b" />
              <div class="resource-label">Electricity</div>
              <div class="resource-value">{{ elecUsage }} kWh</div>
              <div class="resource-cost">💰 ${{ elecCost }}</div>
            </div>
            <div class="resource-item">
              <el-progress type="circle" :percentage="gasPercent" :width="80" :stroke-width="8" color="#10b981" />
              <div class="resource-label">Gas</div>
              <div class="resource-value">{{ gasUsage }} m³</div>
              <div class="resource-cost">💰 ${{ gasCost }}</div>
            </div>
          </div>
        </div>

        <div class="glass-card parking">
          <div class="card-title">🅿️ Parking Occupancy</div>
          <div class="parking-stats">
            <div class="parking-info">
              <span>Occupied: <strong>{{ parkingOccupied }}</strong> / {{ parkingTotal }}</span>
              <span>Free: <strong>{{ parkingFree }}</strong></span>
            </div>
            <el-progress :percentage="parkingPercent" :stroke-width="12" color="#8b5cf6" />
          </div>
        </div>

        <div class="glass-card device-list">
          <div class="card-title">📊 Equipment by Type</div>
          <div class="device-items">
            <div v-for="dev in deviceTypes" :key="dev.type" class="device-item">
              <div class="device-info">
                <span class="device-name">{{ dev.type }}</span>
                <span class="device-count">{{ dev.count }}</span>
              </div>
              <div class="device-bar-container">
                <div class="device-bar" :style="{ width: (dev.count / maxDeviceCount) * 100 + '%', backgroundColor: dev.color }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="center-void"></div>

      <!-- Right Panel -->
      <div class="right-panel">
        <div class="glass-card alert-list-fixed">
          <div class="card-header-line">
            <span class="card-title">🔔 Active Alerts</span>
            <el-tag type="danger" size="small" effect="dark">{{ alerts.length }} unresolved</el-tag>
          </div>
          <div class="alert-items-fixed">
            <div v-for="(alert, idx) in alerts" :key="idx" class="alert-item">
              <div class="alert-device">{{ alert.device }}</div>
              <div class="alert-content">{{ alert.content }}</div>
              <div class="alert-time">{{ alert.time }}</div>
            </div>
          </div>
        </div>

        <div class="glass-card employee-dashboard">
          <div class="card-title">🧑‍🤝‍🧑 Workforce Dashboard</div>
          <div ref="employeeGauge" style="height: 110px; width: 100%"></div>
          <div class="role-breakdown">
            <div v-for="emp in employeeStats" :key="emp.role" class="role-item">
              <span class="role-name">{{ emp.role }}</span>
              <span class="role-count">{{ emp.count }}</span>
              <div class="role-bar">
                <div class="role-bar-fill" :style="{ width: emp.percent + '%', backgroundColor: emp.color }"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="glass-card energy-report">
          <div class="card-title">📈 Energy Trend</div>
          <div class="energy-timeline">
            <div v-for="(item, idx) in energyReportData" :key="idx" class="energy-item">
              <div class="time-badge">{{ item.period }}</div>
              <div class="energy-value">{{ item.value }} kWh</div>
              <div class="energy-change" :class="{ positive: item.change >= 0, negative: item.change < 0 }">
                <span class="arrow">{{ item.change >= 0 ? '↑' : '↓' }}</span>
                {{ Math.abs(item.change) }}%
              </div>
              <div class="energy-bar-container">
                <div class="energy-bar" :style="{ width: (item.value / 1000) * 100 + '%', background: getEnergyColor(item.change) }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- KPI Strip - with cost savings and carbon revenue -->
    <div class="glass-card kpi-strip">
      <div class="kpi-item">
        <span class="kpi-label">🏭 Total Devices</span>
        <span class="kpi-value">{{ deviceTotal }}</span>
      </div>
      <div class="kpi-item">
        <span class="kpi-label">📈 Online Rate</span>
        <span class="kpi-value">{{ onlineRate }}%</span>
      </div>
      <div class="kpi-item">
        <span class="kpi-label">⚡ Total Energy</span>
        <span class="kpi-value">{{ totalEnergy }} kWh</span>
      </div>
      <div class="kpi-item">
        <span class="kpi-label">💰 Total Cost</span>
        <span class="kpi-value">{{ totalCost }}</span>
      </div>
      <div class="kpi-item">
        <span class="kpi-label">🌿 Saved Cost</span>
        <span class="kpi-value">${{ savedCostDisplay }}</span>
      </div>
      <div class="kpi-item">
        <span class="kpi-label">💵 Carbon Revenue</span>
        <span class="kpi-value">${{ carbonRevenueDisplay }}</span>
      </div>
    </div>

    <!-- Energy Savings Report Drawer - All English -->
    <el-drawer
        v-model="showEnergyReport"
        direction="rtl"
        size="400px"
        :with-header="true"
        class="energy-report-drawer"
        :close-on-click-modal="true"
    >
      <template #header>
        <div class="drawer-header">
          <div class="drawer-title-section">
            <span class="drawer-icon">🌿</span>
            <div class="drawer-title-wrapper">
              <span class="drawer-title">Energy Savings Report</span>
            </div>
          </div>
          <div class="drawer-location-wrapper">
            <div class="drawer-location">
              <el-tag type="success" size="small" effect="plain" round style="margin-right: 10px">Live Data</el-tag>
              <el-icon><Location /></el-icon>
              <span>Singapore</span>
            </div>
          </div>
        </div>
      </template>
      <div class="report-content">
        <!-- Core Stats -->
        <div class="report-core-stats">
          <div class="core-stat-card">
            <div class="stat-icon">⚡</div>
            <div class="stat-info">
              <div class="stat-label">Total Energy Saved</div>
              <div class="stat-value">{{ savedEnergyTotal }} kWh</div>
            </div>
          </div>
          <div class="core-stat-card">
            <div class="stat-icon">💰</div>
            <div class="stat-info">
              <div class="stat-label">Cost Saved</div>
              <div class="stat-value">${{ savedCostTotal }}</div>
              <div class="stat-rate">@ $0.238/kWh</div>
            </div>
          </div>
        </div>

        <!-- Carbon & Revenue Section -->
        <div class="carbon-section">
          <div class="section-title">🌍 Carbon Reduction & Revenue</div>
          <div class="carbon-grid">
            <div class="carbon-item">
              <div class="carbon-icon">🏭</div>
              <div class="carbon-info">
                <div class="carbon-label">CO₂ Reduction</div>
                <div class="carbon-value">{{ carbonReductionTotal }} kg</div>
                <div class="carbon-sub">≈ {{ treesOffset }} trees/year</div>
              </div>
            </div>
            <div class="carbon-item">
              <div class="carbon-icon">💵</div>
              <div class="carbon-info">
                <div class="carbon-label">Carbon Credit Revenue</div>
                <div class="carbon-value">${{ carbonRevenueTotal }}</div>
                <div class="carbon-sub">@ $50/ton CO₂</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Annual Goal Progress -->
        <div class="goal-section">
          <div class="goal-header">
            <span>🎯 Annual Savings Target</span>
            <span class="goal-percent">{{ savingProgressPercent }}%</span>
          </div>
          <el-progress :percentage="savingProgressPercent" :stroke-width="10" color="#10b981" :show-text="false" />
          <div class="goal-detail">
            <span>Achieved: {{ savedEnergyTotal }} / {{ annualTargetKwh }} kWh</span>
            <span>Remaining: {{ remainingTarget }} kWh</span>
          </div>
          <div class="goal-days-info">Continuous operation: {{ continuousDays }} days</div>
        </div>

        <!-- Monthly Trend Chart -->
        <div class="trend-chart">
          <div class="trend-header">📈 Monthly Savings Trend</div>
          <div ref="reportChartRef" style="height: 200px; width: 100%"></div>
        </div>

        <!-- Equipment Contribution Ranking -->
        <div class="ranking-section">
          <div class="ranking-header">🏆 Top Energy Saving Contributors</div>
          <div class="ranking-list">
            <div v-for="(item, idx) in deviceRanking" :key="idx" class="ranking-item">
              <div class="ranking-rank" :class="{ 'top-three': idx < 3 }">{{ idx + 1 }}</div>
              <div class="ranking-name">{{ item.name }}</div>
              <div class="ranking-bar-wrap">
                <div class="ranking-bar" :style="{ width: item.percent + '%', background: idx < 3 ? '#10b981' : '#3b82f6' }"></div>
              </div>
              <div class="ranking-value">{{ item.saved }} kWh</div>
            </div>
          </div>
        </div>
      </div>
    </el-drawer>
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
        <div class="loading-tip">Initializing Smart Factory System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { Location } from '@element-plus/icons-vue'
import { useCounterStore } from '@/stores/counter.js'
import { getCurrentInstance } from 'vue'

const getStore = () => {
  const instance = getCurrentInstance()
  if (!instance) {
    throw new Error('useStore() must be called within a setup function')
  }
  const pinia = instance.appContext.config.globalProperties.$pinia
  if (!pinia) {
    throw new Error('Pinia instance not found. Did you forget to call app.use(pinia)?')
  }
  return useCounterStore(pinia)
}
const counterStore = getStore()
const isFullscreen = computed(() => counterStore.isFullscreen)

// ==================== Real-time Data ====================
const currentTime = ref('')
const isBackgroundLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing assets...')

// Energy saving mode state - default ON
const isEnergySavingActive = computed({
  get: () => counterStore.isEnergySavingActive,
  set: (val) => counterStore.setEnergySavingActive(val)
})
// Report drawer visibility - default OFF
const showEnergyReport = computed({
  get: () => counterStore.showEnergyReport,
  set: (val) => counterStore.setShowEnergyReport(val)
})

// Energy saving accumulation data
let savingStartTime = null
let baselineHourlyConsumption = 0
let window_actualConsumption = 0
let window_lastTrackedElec = 0
const startSavedEnergy = 28560 // 初始节电量 (kWh) - 对应大约连续运行18天

// Energy saving display data - 设置非零初始值
const savedEnergyTotal = ref(28560)
const savedCostTotal = ref(6797.28)
const carbonReductionTotal = ref(11424)
const carbonRevenueTotal = ref(571.20)
const savingProgressPercent = ref(5.71)
const continuousDays = ref(18) // 连续开启天数
const annualTargetKwh = ref(571200) // 年目标基于日均节能 * 360天

// KPI display formatted values
const savedCostDisplay = computed(() => savedCostTotal.value.toFixed(2))
const carbonRevenueDisplay = computed(() => carbonRevenueTotal.value.toFixed(2))

// Singapore parameters
const SGD_ELECTRICITY_RATE = 0.238
const CARBON_FACTOR = 0.4
const CARBON_CREDIT_PRICE_SGD = 50

// Static device ranking data
const deviceRanking = ref([
  { name: 'HVAC System', saved: 12450, percent: 44 },
  { name: 'Lighting System', saved: 8320, percent: 29 },
  { name: 'Air Compressor', saved: 4580, percent: 16 },
  { name: 'Production Motors', saved: 2110, percent: 7 },
  { name: 'Other Equipment', saved: 1000, percent: 4 }
])

// Chart instance
let reportChart = null
const reportChartRef = ref(null)

// KPI Data
const deviceTotal = ref(246)
const onlineRate = ref(94.7)
const totalEnergy = ref(6882)
const activeAlertsCount = ref(12)

// Utilities
const waterUsage = ref(1240)
const elecUsage = ref(6882)
const gasUsage = ref(320)
const waterTarget = 2000
const elecTarget = 10000
const gasTarget = 500
const waterPercent = ref(62)
const elecPercent = ref(68.8)
const gasPercent = ref(64)

const waterCost = ref(620.00)
const elecCost = ref(825.84)
const gasCost = ref(256.00)
const totalCost = ref(1701.84)
const costBreakdown = ref([
  { item: 'Water', cost: 0, trend: 0 },
  { item: 'Electricity', cost: 0, trend: 0 },
  { item: 'Gas', cost: 0, trend: 0 }
])

// Loading messages
const loadingMessages = [
  'Preparing assets...',
  'Loading background...',
  'Initializing modules...',
  'Connecting to sensors...',
  'Starting dashboard...',
  'Almost ready...'
]

function updateCosts() {
  waterCost.value = (waterUsage.value * 0.5).toFixed(2)
  elecCost.value = (elecUsage.value * 0.12).toFixed(2)
  gasCost.value = (gasUsage.value * 0.8).toFixed(2)
  totalCost.value = (parseFloat(waterCost.value) + parseFloat(elecCost.value) + parseFloat(gasCost.value)).toFixed(2)
}

// Parking
const parkingTotal = 200
const parkingOccupied = ref(145)
const parkingFree = ref(55)
const parkingPercent = ref(72.5)

// Employee data
const employeeStats = ref([
  { role: 'Operators', count: 38, percent: 44, color: '#a78bfa' },
  { role: 'Technicians', count: 22, percent: 26, color: '#f472b6' },
  { role: 'Managers', count: 8, percent: 9, color: '#facc15' },
  { role: 'Others', count: 5, percent: 6, color: '#3b82f6' }
])
const employeeSaturation = ref(85.9)

// Device types
const deviceTypes = ref([
  { type: 'HVAC', count: 35, color: '#3b82f6' },
  { type: 'Lighting', count: 48, color: '#f59e0b' },
  { type: 'Security', count: 22, color: '#10b981' },
  { type: 'Plumbing', count: 18, color: '#8b5cf6' },
  { type: 'Others', count: 10, color: '#ef4444' }
])
const maxDeviceCount = ref(60)

// Energy report data
const energyReportData = ref([
  { period: '00:00-04:00', value: 320, change: -5.2 },
  { period: '04:00-08:00', value: 540, change: 68.8 },
  { period: '08:00-12:00', value: 890, change: 64.8 },
  { period: '12:00-16:00', value: 760, change: -14.6 },
  { period: '16:00-20:00', value: 430, change: -43.4 },
  { period: '20:00-24:00', value: 380, change: -11.6 }
])

// Alerts
const alerts = ref([
  { device: 'Compressor A', content: 'Exhaust temp too high', time: '09:32' },
  { device: 'Panel B', content: 'Current imbalance', time: '09:15' },
  { device: 'HVAC Unit', content: 'Low chilled water flow', time: '08:50' },
  { device: 'Lighting Loop', content: 'Communication lost', time: '08:20' },
])

let employeeGaugeIns = null
const employeeGauge = ref(null)

// ==================== Energy Saving Model Logic ====================

function handleEnergySavingToggle(val) {
  if (val) {
    startEnergySavingModel()
    ElMessage.success({
      message: '🌿 Energy saving mode activated',
      duration: 2000,
      type: 'success'
    })
  } else {
    stopEnergySavingModel()
    showEnergyReport.value = false
    ElMessage.info({
      message: 'Energy saving mode deactivated',
      duration: 2000,
      type: 'info'
    })
  }
}

function startEnergySavingModel() {
  baselineHourlyConsumption = elecUsage.value
  savingStartTime = Date.now()
  window_actualConsumption = 0
  window_lastTrackedElec = elecUsage.value
  window._energySavingBoost = 0.85
  // 设置初始节能数据非零 - 基于连续开启天数
  savedEnergyTotal.value = startSavedEnergy
  savedCostTotal.value = startSavedEnergy * SGD_ELECTRICITY_RATE
  carbonReductionTotal.value = Math.round(startSavedEnergy * CARBON_FACTOR)
  carbonRevenueTotal.value = parseFloat(((carbonReductionTotal.value / 1000) * CARBON_CREDIT_PRICE_SGD).toFixed(2))
  // 节能进度 = 已节能 / (日平均节能 * 360天)
  const dailyAvgSaving = startSavedEnergy / continuousDays.value
  annualTargetKwh.value = dailyAvgSaving * 360
  savingProgressPercent.value = Math.min(100, Math.round((startSavedEnergy / annualTargetKwh.value) * 100 * 10) / 10)
}

function stopEnergySavingModel() {
  savingStartTime = null
  window._energySavingBoost = null
  window_actualConsumption = 0
  window_lastTrackedElec = 0
  savedEnergyTotal.value = 0
  savedCostTotal.value = 0
  carbonReductionTotal.value = 0
  carbonRevenueTotal.value = 0
  savingProgressPercent.value = 0
  continuousDays.value = 0
  annualTargetKwh.value = 0
}

function updateEnergySavings() {
  if (!isEnergySavingActive.value || !savingStartTime) return

  const hoursElapsed = (Date.now() - savingStartTime) / (1000 * 60 * 60)
  const baselineTotal = baselineHourlyConsumption * hoursElapsed
  const actualTotal = window_actualConsumption || 0

  // 更新连续运行天数
  continuousDays.value = Math.max(continuousDays.value, Math.floor(hoursElapsed / 24) + 18)

  const newSavedEnergy = startSavedEnergy + Math.max(0, baselineTotal - actualTotal)
  savedEnergyTotal.value = Math.round(newSavedEnergy * 10) / 10
  savedCostTotal.value = savedEnergyTotal.value * SGD_ELECTRICITY_RATE
  carbonReductionTotal.value = Math.round(savedEnergyTotal.value * CARBON_FACTOR * 10) / 10
  const carbonReductionTonnes = carbonReductionTotal.value / 1000
  carbonRevenueTotal.value = parseFloat((carbonReductionTonnes * CARBON_CREDIT_PRICE_SGD).toFixed(2))

  // 基于日平均节能计算进度 (基准360天)
  const dailyAvgSaving = savedEnergyTotal.value / continuousDays.value
  annualTargetKwh.value = dailyAvgSaving * 360
  savingProgressPercent.value = Math.min(100, Math.round((savedEnergyTotal.value / annualTargetKwh.value) * 100 * 10) / 10)
}

function trackEnergyConsumption() {
  if (!isEnergySavingActive.value || !savingStartTime) return

  if (window_lastTrackedElec === 0) {
    window_lastTrackedElec = elecUsage.value
    window_actualConsumption = 0
    return
  }

  const currentElec = elecUsage.value
  const delta = Math.max(0, currentElec - window_lastTrackedElec)
  if (delta > 0) {
    window_actualConsumption += delta
  }
  window_lastTrackedElec = currentElec
}

// Initialize report chart
function initReportChart() {
  if (reportChartRef.value) {
    if (reportChart) reportChart.dispose()
    reportChart = echarts.init(reportChartRef.value)
    // 计算本周节能量 (本周累计增加的量)
    const currentWeekSaving = Math.max(0, Math.round(savedEnergyTotal.value - startSavedEnergy))
    reportChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { top: 20, left: 45, right: 10, bottom: 20 },
      xAxis: {
        type: 'category',
        data: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'This Week'],
        axisLabel: { color: '#3a3e45', fontSize: 10 }
      },
      yAxis: {
        type: 'value',
        name: 'Saved Energy (kWh)',
        nameTextStyle: { color: '#3a3e45', fontSize: 10 },
        axisLabel: { color: '#3a3e45' }
      },
      series: [{
        type: 'bar',
        data: [4520, 6180, 7250, 8340, currentWeekSaving > 0 ? currentWeekSaving : 1580],
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#10b981' }, { offset: 1, color: '#34d399' }] }
        },
        label: { show: true, position: 'top', color: '#3e3e3e', fontSize: 10 }
      }]
    })
  }
}

// Computed values
const remainingTarget = computed(() => Math.max(0, Math.round(annualTargetKwh.value - savedEnergyTotal.value)))
const treesOffset = computed(() => Math.round(carbonReductionTotal.value / 22))

// ==================== Utility Functions ====================
let timeTimer = null
let dataInterval = null

const updateTime = () => {
  const now = new Date()
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

function randomVariation(base, rangePercent = 0.05, isEnergySaving = false) {
  let change = (Math.random() - 0.5) * rangePercent * 2
  if (isEnergySaving && window._energySavingBoost && isEnergySavingActive.value) {
    change = change - 0.04
  }
  let result = base * (1 + change)
  return Math.max(0, Math.round(result * 10) / 10)
}

function getEnergyColor(change) {
  return change >= 0 ? '#f59e0b' : '#10b981'
}

// Preload background
const preloadBackground = () => {
  return new Promise((resolve) => {
    const img = new Image()
    const backgroundUrl = 'https://aegisnx.com/wp-content/uploads/2026/05/1778117712687.png'

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

        if (progress > 80 && loadingMessage.value !== loadingMessages[4]) {
          loadingMessage.value = loadingMessages[4]
        } else if (progress > 60 && loadingMessage.value !== loadingMessages[3]) {
          loadingMessage.value = loadingMessages[3]
        } else if (progress > 40 && loadingMessage.value !== loadingMessages[2]) {
          loadingMessage.value = loadingMessages[2]
        } else if (progress > 20 && loadingMessage.value !== loadingMessages[1]) {
          loadingMessage.value = loadingMessages[1]
        }
      }
    }, 100)

    img.onload = () => {
      clearInterval(messageInterval)
      clearInterval(progressInterval)
      loadingMessage.value = 'Ready!'
      loadingProgress.value = 100
      setTimeout(() => {
        resolve()
      }, 500)
    }

    img.onerror = () => {
      console.warn('Background image load failed, using fallback')
      clearInterval(messageInterval)
      clearInterval(progressInterval)
      loadingMessage.value = 'Loading complete'
      loadingProgress.value = 100
      setTimeout(() => {
        resolve()
      }, 300)
    }

    img.src = backgroundUrl
  })
}

// Refresh all real-time data
function refreshRealTimeData() {
  let newTotal = randomVariation(246, 0.03)
  deviceTotal.value = Math.floor(newTotal)
  let newOnlineRate = randomVariation(94.7, 0.02)
  onlineRate.value = newOnlineRate.toFixed(1)

  let newWater = randomVariation(1240, 0.07)
  waterUsage.value = Math.floor(newWater)
  waterPercent.value = Math.min(100, Number(((newWater / waterTarget) * 100).toFixed(1)))

  let newElec2 = randomVariation(6882, 0.07, true)
  elecUsage.value = Math.floor(newElec2)
  elecPercent.value = Math.min(100, Number(((newElec2 / elecTarget) * 100).toFixed(1)))

  let newGas = randomVariation(320, 0.07)
  gasUsage.value = Math.floor(newGas)
  gasPercent.value = Math.min(100, Number(((newGas / gasTarget) * 100).toFixed(1)))

  totalEnergy.value = elecUsage.value + Math.floor(randomVariation(1240, 0.05)) + Math.floor(randomVariation(320, 0.05))
  updateCosts()

  if (isEnergySavingActive.value) {
    trackEnergyConsumption()
    updateEnergySavings()
  }

  let newOccupied = randomVariation(145, 0.05)
  newOccupied = Math.min(parkingTotal, Math.max(80, Math.floor(newOccupied)))
  parkingOccupied.value = newOccupied
  parkingFree.value = parkingTotal - newOccupied
  parkingPercent.value = Number(((newOccupied / parkingTotal) * 100).toFixed(1))

  let totalEmp = 70 + Math.floor(Math.random() * 15)
  let target = 85
  employeeSaturation.value = Number(((totalEmp / target) * 100).toFixed(1))
  let op = Math.floor(totalEmp * (0.4 + Math.random() * 0.1))
  let tech = Math.floor(totalEmp * (0.25 + Math.random() * 0.08))
  let mgr = Math.floor(totalEmp * (0.1 + Math.random() * 0.05))
  let other = totalEmp - op - tech - mgr
  employeeStats.value[0].count = op
  employeeStats.value[1].count = tech
  employeeStats.value[2].count = mgr
  employeeStats.value[3].count = other
  employeeStats.value.forEach(emp => {
    emp.percent = Number(((emp.count / totalEmp) * 100).toFixed(1))
  })
  if (employeeGaugeIns) {
    employeeGaugeIns.setOption({ series: [{ data: [{ value: employeeSaturation.value, name: 'Saturation' }] }] })
  }

  let totalDev = 120 + Math.floor(Math.random() * 50)
  let hvac = Math.floor(totalDev * (0.25 + Math.random() * 0.1))
  let light = Math.floor(totalDev * (0.3 + Math.random() * 0.1))
  let sec = Math.floor(totalDev * (0.15 + Math.random() * 0.05))
  let plumb = Math.floor(totalDev * (0.12 + Math.random() * 0.05))
  let otherDev = totalDev - hvac - light - sec - plumb
  deviceTypes.value[0].count = hvac
  deviceTypes.value[1].count = light
  deviceTypes.value[2].count = sec
  deviceTypes.value[3].count = plumb
  deviceTypes.value[4].count = otherDev
  maxDeviceCount.value = Math.max(...deviceTypes.value.map(d => d.count)) * 1.1

  const newLen = Math.min(6, Math.max(4, alerts.value.length + (Math.random() > 0.65 ? 1 : Math.random() > 0.5 ? -1 : 0)))
  if (newLen > alerts.value.length) {
    const fakeDevices = ['Chiller', 'Pump Station', 'VFD', 'UPS', 'Fire Alarm']
    const fakeContents = ['Over temperature', 'Low pressure', 'Phase loss', 'Battery low', 'Sensor fault']
    const newAlert = {
      device: fakeDevices[Math.floor(Math.random() * fakeDevices.length)],
      content: fakeContents[Math.floor(Math.random() * fakeContents.length)],
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
    alerts.value.unshift(newAlert)
    if (alerts.value.length > 6) alerts.value.pop()
  } else if (newLen < alerts.value.length) {
    alerts.value.pop()
  }
  activeAlertsCount.value = alerts.value.length

  energyReportData.value.forEach(item => {
    let newVal = Math.max(50, item.value + (Math.random() - 0.5) * 100)
    let change = ((newVal - item.value) / item.value * 100).toFixed(1)
    item.value = Math.floor(newVal)
    item.change = parseFloat(change)
  })
}

// Initialize charts
const initCharts = () => {
  if (employeeGauge.value) {
    employeeGaugeIns = echarts.init(employeeGauge.value)
    employeeGaugeIns.setOption({
      tooltip: { formatter: '{b}: {c}%' },
      series: [{
        type: 'gauge',
        center: ['50%', '45%'],
        radius: '80%',
        min: 0,
        max: 100,
        splitNumber: 5,
        axisLine: { lineStyle: { width: 12, color: [[0.7, '#2dd4bf'],[1, '#ef4444']] } },
        pointer: { show: true, length: '60%', width: 8, itemStyle: { color: '#facc15' } },
        detail: { show: true, offsetCenter: [0, 25], valueAnimation: true, fontSize: 16, color: '#fff' },
        title: { show: true, offsetCenter: [0, -10], fontSize: 12, color: '#cbd5e1' },
        data: [{ value: employeeSaturation.value, name: 'Workforce Saturation' }]
      }]
    })
  }
}

// Watch for report drawer open to initialize chart
watch(showEnergyReport, (newVal) => {
  if (newVal) {
    nextTick(() => {
      initReportChart()
    })
  } else if (reportChart) {
    reportChart.dispose()
    reportChart = null
  }
})
const isMobile = ref(false)
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}
onMounted(async () => {
  checkMobile()
  updateTime()
  timeTimer = setInterval(updateTime, 1000)

  await preloadBackground()
  isBackgroundLoaded.value = true
  await new Promise(resolve => setTimeout(resolve, 50))

  initCharts()
  refreshRealTimeData()

  // Start energy saving mode by default
  if (isEnergySavingActive.value) {
    startEnergySavingModel()
  }

  dataInterval = setInterval(refreshRealTimeData, 3000)
  window.addEventListener('resize', () => {
    employeeGaugeIns?.resize()
    if (reportChart) reportChart.resize()
  })
})

onBeforeUnmount(() => {
  clearInterval(timeTimer)
  clearInterval(dataInterval)
  window.removeEventListener('resize', () => {})
  employeeGaugeIns?.dispose()
  if (reportChart) reportChart.dispose()
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
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
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
  background: rgba(15, 23, 42, 0.6);
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
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
  40% { transform: scale(1); opacity: 1; }
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
  0% { background-position: 0% 0%; }
  100% { background-position: 200% 0%; }
}

.loading-tip {
  font-size: 13px;
  color: #3a3e45;
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
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Dashboard */
.dashboard {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  background-image: url('https://aegisnx.com/wp-content/uploads/2026/05/1778117712687.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
  font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* Top Header */
.top-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 28px 8px 28px;
  background: transparent;
  margin: 0px 24px 0 24px;
}

.header-left {
  width: auto;
  display: flex;
  align-items: center;
}

.button-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.button-group1 {
  width: 160px;
}

.energy-saving-switch {
  --el-switch-on-color: #10b981;
  --el-switch-off-color: #475569;
}

.report-switch {
  --el-switch-on-color: #3b82f6;
  --el-switch-off-color: #475569;
}

.energy-saving-switch :deep(.el-switch__label),
.report-switch :deep(.el-switch__label) {
  color: #e2e8f0;
  font-weight: 500;
  font-size: 12px;
}

.header-title { text-align: center; flex-grow: 1; }
.main-title {
  font-size: 44px;
  font-weight: 800;
  line-height: 1.2;
  background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: #f0f9ff;
  text-shadow: 0 0 15px rgba(186, 230, 253, 0.4);
  letter-spacing: 3px;
}
.datetime {
  font-size: 16px;
  color: #0ff;
  font-weight: 600;
  background: transparent;
  padding: 8px 20px;
  border-radius: 12px;
  backdrop-filter: blur(8px);
  width: auto;
  min-width: 280px;
  text-align: center;
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  letter-spacing: 1px;
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.3), inset 0 0 5px rgba(0, 255, 255, 0.1);
  border: 1px solid rgba(0, 255, 255, 0.5);
  text-shadow: 0 0 5px #0ff;
}

.datetimeview1 {
  font-size: 16px;
  color: #0ff;
  font-weight: 600;
  background: transparent;
  padding: 8px 20px;
  border-radius: 12px;
  backdrop-filter: blur(8px);
  width: auto;
  min-width: 280px;
  text-align: center;
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  letter-spacing: 1px;
}

/* KPI Strip */
.kpi-strip {
  display: flex;
  justify-content: space-around;
  gap: 20px;
  margin: 10px 24px 20px 24px;
  padding: 12px 20px;
  flex-wrap: wrap;
}
.kpi-item {
  display: flex;
  gap: 12px;
  align-items: baseline;
  font-size: 15px;
}
.kpi-label {
  color: #ffffff;
  font-weight: 500;
}
.kpi-value {
  font-size: 24px;
  font-weight: 800;
  color: #facc15;
  font-family: monospace;
  text-shadow: 0 0 5px rgba(250,204,21,0.5);
}

/* Content Area */
.content-area {
  flex: 1;
  display: flex;
  justify-content: space-between;
  padding: 0 24px 24px 24px;
  gap: 32px;
  overflow-y: auto;
}
.left-panel { width: 320px; flex-shrink: 0; }
.right-panel { width: 380px; flex-shrink: 0; }
.center-void { flex: 1; min-width: 40px; }

/* Glass Cards */
.glass-card {
  background: transparent;
  backdrop-filter: none;
  border-radius: 28px;
  border: 1px solid rgba(59, 130, 246, 0.3);
  box-shadow: 0 20px 35px -12px rgba(0, 0, 0, 0.6),
  0 0 0 1px rgba(255, 255, 255, 0.05) inset,
  0 -1px 0 1px rgba(255, 255, 255, 0.02) inset;
  padding: 18px;
  transition: all 0.3s cubic-bezier(0.2, 0.9, 0.4, 1.1);
  margin-bottom: 20px;
}
.glass-card:hover {
  background: rgba(8, 16, 28, 0.6);
  backdrop-filter: blur(8px);
  transform: translateY(-4px);
  border-color: rgba(59, 130, 246, 0.6);
  box-shadow: 0 28px 40px -14px rgba(0, 0, 0, 0.7),
  0 0 0 1px rgba(255, 255, 255, 0.1) inset,
  0 -1px 0 1px rgba(255, 255, 255, 0.04) inset;
}
.card-title {
  font-size: 18px;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 10px;
  padding-left: 8px;
  border-left: 4px solid #3b82f6;
}
.resource-grid {
  display: flex;
  justify-content: space-around;
  text-align: center;
  margin-bottom: 16px;
}
.resource-item .resource-label {
  margin-top: 8px;
  font-size: 16px;
  color: #cbd5e1;
  font-weight: bold;
}
.resource-value {
  font-size: 14px;
  font-weight: bold;
  color: #facc15;
}
.resource-cost {
  font-size: 12px;
  color: #a5f3fc;
  margin-top: 4px;
  font-weight: 500;
}
.parking-stats { margin-top: 5px; }
.parking-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  color: #cbd5e1;
  font-size: 14px;
}
.parking-info strong { color: #facc15; }
.alert-list-fixed {
  display: flex;
  flex-direction: column;
  height: 180px;
}
.alert-items-fixed {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.alert-items-fixed::-webkit-scrollbar { display: none; }
.alert-item {
  background: rgba(0,0,0,0.3);
  border-radius: 16px;
  padding: 10px 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: 0.2s;
}
.alert-item:hover {
  background: rgba(239,68,68,0.2);
  border-left: 2px solid #ef4444;
}
.alert-device {
  font-weight: 600;
  color: #facc15;
  font-size: 12px;
}
.alert-content {
  flex: 1;
  margin: 0 10px;
  font-size: 12px;
  color: #e2e8f0;
}
.alert-time {
  font-size: 11px;
  color: #3a3e45;
  font-family: monospace;
}
.employee-dashboard { display: flex; flex-direction: column; }
.role-breakdown {
  margin-top: 0px;
  padding-top: 12px;
  border-top: 1px dashed rgba(59,130,246,0.4);
}
.role-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  font-size: 13px;
}
.role-name { width: 85px; color: #e2e8f0; }
.role-count { width: 35px; font-weight: bold; color: #facc15; }
.role-bar {
  flex: 1;
  height: 6px;
  background: rgba(255,255,255,0.2);
  border-radius: 3px;
  overflow: hidden;
}
.role-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s;
}

.device-items {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.device-item {
  background: rgba(0,0,0,0.25);
  border-radius: 16px;
  padding: 10px 14px;
  transition: all 0.2s;
}
.device-item:hover {
  background: rgba(255,255,255,0.05);
  transform: translateX(4px);
}
.device-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}
.device-name {
  font-weight: 600;
  color: #e2e8f0;
  font-size: 13px;
}
.device-count {
  font-family: monospace;
  font-weight: bold;
  color: #facc15;
  font-size: 14px;
}
.device-bar-container {
  height: 6px;
  background: rgba(255,255,255,0.2);
  border-radius: 3px;
  overflow: hidden;
}
.device-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s;
}

.energy-timeline {
  display: flex;
  flex-direction: column;
  gap: 0px;
}
.energy-item {
  display: flex;
  align-items: center;
  gap: 12px;
  border-radius: 16px;
  padding: 6px 8px;
  transition: all 0.2s;
}
.energy-item:hover {
  background: rgba(255,255,255,0.05);
  transform: scale(1.01);
}
.time-badge {
  width: 100px;
  font-size: 11px;
  font-weight: 600;
  color: #a5f3fc;
  background: rgba(0,0,0,0.4);
  padding: 4px 8px;
  border-radius: 20px;
  text-align: center;
}
.energy-value {
  width: 80px;
  font-family: monospace;
  font-weight: bold;
  color: #facc15;
  font-size: 14px;
}
.energy-change {
  width: 60px;
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}
.energy-change.positive { color: #f59e0b; }
.energy-change.negative { color: #10b981; }
.energy-bar-container {
  flex: 1;
  height: 6px;
  background: rgba(255,255,255,0.2);
  border-radius: 3px;
  overflow: hidden;
}
.energy-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s;
}
.card-header-line {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 12px;
  border-bottom: 1px dashed rgba(59,130,246,0.4);
  padding-bottom: 6px;
}
:deep(.el-progress-circle__track) {
  stroke: rgba(255,255,255,0.2);
}
:deep(.el-progress__text) {
  color: #fff;
  font-weight: bold;
}
.content-area::-webkit-scrollbar {
  width: 5px;
}
.content-area::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.5);
  border-radius: 4px;
}
.content-area::-webkit-scrollbar-thumb {
  background: #3b82f6;
  border-radius: 4px;
}

/* Energy Report Drawer */
.energy-report-drawer :deep(.el-drawer__header) {
  margin-bottom: 0;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(16, 185, 129, 0.2);
  background: rgba(8, 16, 28, 0.95);
}
.energy-report-drawer :deep(.el-drawer__body) {
  padding: 0;
  background: linear-gradient(180deg, #0f172a 0%, #0a0f1a 100%);
  overflow: hidden;
  /* 隐藏滚动条 */
  scrollbar-width: none; /* Firefox */
}
.drawer-header {
  display: flex;
  flex-direction: column;
  width: 100%;
  flex-wrap: wrap;
  gap: 12px;
}
.drawer-title-section {
  display: flex;
  align-items: center;
  gap: 10px;
}
.drawer-title-wrapper {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.drawer-title-wrapper .drawer-title {
  font-size: 18px;
  font-weight: 700;
  color: green;
  letter-spacing: 1px;
}
.drawer-location-wrapper {
  text-align: right;
}
.drawer-location {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 15px;
  color: #94a3b8;
  font-weight: bold;
}
.drawer-location-sub {
  font-size: 11px;
  color: #64748b;
  margin-top: 2px;
}
.drawer-icon {
  font-size: 22px;
}
.report-content {
  padding: 0px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-height: calc(100vh - 70px);
  overflow-y: auto;
}
.report-content::-webkit-scrollbar {
  width: 4px;
  display: none;
}
.report-content::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}
.report-content::-webkit-scrollbar-thumb {
  background: #10b981;
  border-radius: 4px;
}

/* Report Core Stats */
.report-core-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.core-stat-card {
  background: rgba(16, 185, 129, 0.08);
  border-radius: 20px;
  padding: 6px;
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid rgba(16, 185, 129, 0.2);
}
.stat-icon {
  font-size: 32px;
}
.stat-info {
  flex: 1;
}
.stat-label {
  font-size: 11px;
  color: #3a3e45;
  display: block;
  margin-bottom: 4px;
  font-weight: bold;
}
.stat-value {
  font-size: 22px;
  font-weight: 800;
  color: #facc15;
  font-family: monospace;
}
.stat-rate {
  font-size: 11px;
  color: green;
  margin-top: 4px;
  font-weight: bold;
}

/* Carbon Section */
.carbon-section {
  background: rgba(16, 185, 129, 0.08);
  border-radius: 20px;
  padding: 14px 16px;
  border: 1px solid rgba(59, 130, 246, 0.2);
}
.section-title {
  font-size: 14px;
  color: #48494c;
  font-weight: bold;
  margin-bottom: 12px;
}
.carbon-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.carbon-item {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(16, 185, 129, 0.08);
  border-radius: 16px;
  padding: 5px;
}
.carbon-icon {
  font-size: 24px;
}
.carbon-info {
  flex: 1;
}
.carbon-label {
  font-size: 11px;
  font-weight: bold;
  color: #3a3e45;
  display: block;
}
.carbon-value {
  font-size: 16px;
  font-weight: 700;
  color: #facc15;
  font-family: monospace;
}
.carbon-sub {
  font-size: 9px;
  color: #64748b;
  color: green;
  font-weight: bold;
  font-size: 11px;
}

/* Goal Section */
.goal-section {
  background: rgba(16, 185, 129, 0.08);
  border-radius: 20px;
  padding: 14px 16px;
  border: 1px solid rgba(16, 185, 129, 0.2);
}
.goal-header {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #e2e8f0;
  color: #48494c;
  font-weight: bold;
  margin-bottom: 10px;
}
.goal-percent {
  font-size: 18px;
  font-weight: 700;
  color: #10b981;
}
.goal-detail {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: #3a3e45;
  font-weight: bold;
  margin-top: 8px;
}
.goal-days-info {
  font-size: 11px;
  color: #10b981;
  margin-top: 8px;
  text-align: center;
  font-weight: bold;
}

/* Trend Chart */
.trend-chart {
  background: rgba(16, 185, 129, 0.08);
  border-radius: 20px;
  padding: 12px;
}
.trend-header {
  font-size: 13px;
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 12px;
  color: #48494c;
  font-weight: bold;
}

/* Ranking Section */
.ranking-section {
  background: rgba(16, 185, 129, 0.08);
  border-radius: 20px;
  padding: 14px;
}
.ranking-header {
  font-size: 13px;
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 12px;
  color: #48494c;
  font-weight: bold;
}
.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.ranking-item {
  display: flex;
  align-items: center;
  gap: 10px;
}
.ranking-rank {
  width: 26px;
  height: 26px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  color: #3a3e45;
}
.ranking-rank.top-three {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}
.ranking-name {
  width: 120px;
  font-size: 11px;
  color: #333333;
  font-weight: bold;
}
.ranking-bar-wrap {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  overflow: hidden;
  background-color: #eeeeee;
}
.ranking-bar {
  height: 100%;
  border-radius: 10px;
}
.ranking-value {
  width: 65px;
  font-size: 12px;
  font-family: monospace;
  color: #facc15;
  font-weight: bold;
  text-align: right;
}

/* 开关组容器 */
.button-group {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 单个开关 + 文字 布局 */
.switch-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

/* 文字在左边，样式美化 */
.switch-label {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
  font-weight: bold;
}

/* 开关本身样式 */
.energy-saving-switch,
.report-switch {
  --el-switch-on-color: #10b981;
  --el-switch-off-color: #475569;
}

.report-switch {
  --el-switch-on-color: #3b82f6;
}

/* 开关文字隐藏（因为我们已经放左边了）*/
:deep(.el-switch__label) {
  display: none !important;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .top-header {
    flex-direction: column;
    padding: 12px 16px 8px;
    margin: 0 12px;
    gap: 12px;
  }
  .header-left {
    width: 100%;
    justify-content: center;
  }
  .button-group {
    padding: 6px 12px;
    gap: 12px;
  }
  .energy-saving-switch :deep(.el-switch__label),
  .report-switch :deep(.el-switch__label) {
    font-size: 10px;
  }
  .main-title {
    font-size: 24px;
    letter-spacing: 1px;
  }
  .datetime {
    font-size: 10px;
    padding: 4px 12px;
    min-width: auto;
    width: auto;
    border-radius: 20px;
    box-shadow: 0 0 5px rgba(0,255,255,0.3);
  }
  .kpi-strip {
    flex-wrap: wrap;
    gap: 12px;
    margin: 8px 16px 16px;
    padding: 12px;
    justify-content: center;
  }
  .kpi-item {
    flex: 1 1 40%;
    justify-content: space-between;
    gap: 6px;
  }
  .kpi-value {
    font-size: 16px;
  }
  .content-area {
    flex-direction: column;
    padding: 0 16px 16px;
    gap: 0;
  }
  .left-panel,
  .right-panel {
    width: 100%;
    flex-shrink: 1;
  }
  .center-void {
    display: none;
  }
  .glass-card {
    border-radius: 20px;
    padding: 14px;
    margin-bottom: 16px;
  }
  .card-title {
    font-size: 16px;
    margin-bottom: 12px;
  }
  .resource-grid {
    gap: 12px;
  }
  .resource-item .resource-label {
    font-size: 14px;
  }
  .resource-value {
    font-size: 12px;
  }
  .resource-cost {
    font-size: 11px;
  }
  .parking-info {
    font-size: 12px;
  }
  .alert-list-fixed {
    height: auto;
    max-height: 180px;
  }
  .alert-item {
    padding: 8px 12px;
    flex-wrap: wrap;
  }
  .alert-device {
    width: 70px;
    font-size: 11px;
  }
  .alert-content {
    font-size: 11px;
    margin: 0 6px;
  }
  .alert-time {
    font-size: 10px;
  }
  .employee-dashboard .role-name {
    width: 70px;
    font-size: 12px;
  }
  .employee-dashboard .role-count {
    width: 30px;
    font-size: 12px;
  }
  .role-item {
    gap: 6px;
  }
  .device-item {
    padding: 8px 12px;
  }
  .device-name {
    font-size: 12px;
  }
  .device-count {
    font-size: 12px;
  }
  .energy-item {
    flex-wrap: wrap;
    gap: 6px;
    padding: 8px;
  }
  .time-badge {
    width: 100%;
    text-align: left;
    font-size: 10px;
    background: transparent;
    padding-left: 0;
  }
  .energy-value {
    width: auto;
    flex: 1;
    font-size: 12px;
  }
  .energy-change {
    width: auto;
    font-size: 11px;
  }
  .energy-bar-container {
    width: 100%;
    margin-top: 4px;
  }
  .role-breakdown {
    padding-top: 8px;
  }
  .resource-grid {
    flex-direction: row;
    flex-wrap: wrap;
  }
  .resource-item {
    flex: 1 1 30%;
    min-width: 90px;
  }
  :deep(.el-progress-circle) {
    width: 70px !important;
    height: 70px !important;
  }
  :deep(.el-progress__text) {
    font-size: 12px !important;
  }

  .energy-report-drawer :deep(.el-drawer) {
    width: 100% !important;
  }
  .report-core-stats {
    grid-template-columns: 1fr;
  }
  .carbon-grid {
    grid-template-columns: 1fr;
  }
  .ranking-name {
    width: 100px;
    font-size: 10px;
  }
}
</style>

<style>
.el-drawer__body {
  scrollbar-width: none; /* Firefox */
}
.el-drawer__header {
  margin-bottom: 5px;
}
</style>