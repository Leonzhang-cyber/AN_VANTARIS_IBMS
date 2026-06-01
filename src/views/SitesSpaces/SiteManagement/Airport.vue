<template>
  <div v-if="isBackgroundLoaded" class="dashboard">
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
        <div class="main-title">SMART AIRPORT<br></div>
      </div>
      <div class="datetime" v-if="isFullscreen">{{ currentTime }}</div>
      <div class="datetimeview1" v-if="!isFullscreen"></div>
    </div>

    <div class="content-area">
      <div class="left-panel">

        <!-- 厕所占用卡片 -->
        <div class="glass-card restroom-card">
          <div class="card-title">🚻 Restroom Availability</div>
          <div class="restroom-table">
            <div class="restroom-row-header">
              <span>Location</span>
              <span>Status</span>
              <span>Available</span>
            </div>
            <div v-for="r in computedRestrooms" :key="r.floor" class="restroom-row">
              <span class="floor-name">{{ r.floor }}</span>
              <span class="status-badge" :class="r.statusClass">{{ r.statusText }}</span>
              <span class="available-count">
                <span class="count-number">{{ r.free }}</span>
                <span class="count-total">/{{ r.total }}</span>
              </span>
            </div>
          </div>
        </div>

        <!-- Airport Energy 卡片 -->
        <div class="glass-card resources">
          <div class="card-title">⚡🛫🌡️ Airport Energy</div>
          <div class="resource-grid">
            <div class="resource-item">
              <el-progress type="circle" :percentage="elecPercent" :width="80" :stroke-width="8" color="#f59e0b" />
              <div class="resource-label">Electricity</div>
              <div class="resource-value">{{ elecUsage }} MWh</div>
              <div class="resource-cost">💰 ${{ elecCost }}</div>
            </div>
            <div class="resource-item">
              <el-progress type="circle" :percentage="fuelPercent" :width="80" :stroke-width="8" color="#ef4444" />
              <div class="resource-label">Jet Fuel</div>
              <div class="resource-value">{{ fuelUsage }} kL</div>
              <div class="resource-cost">💰 ${{ fuelCost }}</div>
            </div>
            <div class="resource-item">
              <el-progress type="circle" :percentage="waterPercent" :width="80" :stroke-width="8" color="#3b82f6" />
              <div class="resource-label">Water</div>
              <div class="resource-value">{{ waterUsage }} m³</div>
              <div class="resource-cost">💰 ${{ waterCost }}</div>
            </div>
          </div>
        </div>

        <!-- 候机区域拥挤度监测卡片 -->
        <div class="glass-card waiting-area-card">
          <div class="card-title">🪑 Gate Area Congestion</div>
          <div class="waiting-list">
            <div v-for="gate in gateCongestion" :key="gate.name" class="waiting-row">
              <span class="waiting-name">{{ gate.name }}</span>
              <div class="waiting-progress-wrapper">
                <div class="waiting-progress-bg">
                  <div class="waiting-progress-fill" :style="{ width: gate.congestion + '%', background: gate.color }"></div>
                </div>
              </div>
              <span class="waiting-count">🧑‍🤝‍🧑 {{ gate.passengers }}</span>
              <span class="waiting-status" :style="{ color: gate.color }">{{ gate.status }}</span>
            </div>
          </div>
        </div>

      </div>

      <div class="center-void"></div>

      <div class="right-panel">

        <!-- 航班信息卡片 -->
        <div class="glass-card elevator-card">
          <div class="card-title">✈️ Flight Status</div>
          <div class="elevator-list">
            <div v-for="f in flights" :key="f.id" class="elevator-row">
              <span class="lift-name">{{ f.flight }}</span>
              <span class="lift-floor">{{ f.destination }}</span>
              <span class="lift-status" :class="f.statusClass">{{ f.statusText }}</span>
              <span class="lift-call">{{ f.time }}</span>
            </div>
          </div>
          <div class="elevator-footer">
            <span>🚀 {{ todayFlights }} flights today</span>
            <span>⏱️ {{ avgDelay }} min delay</span>
          </div>
        </div>

        <!-- Airport Services 卡片 -->
        <div class="glass-card services">
          <div class="card-title">🛍️ Airport Services</div>
          <div class="resource-grid">
            <div class="resource-item">
              <el-progress type="circle" :percentage="retailPercent" :width="80" :stroke-width="8" color="#8b5cf6" />
              <div class="resource-label">Retail Occupancy</div>
              <div class="resource-value">{{ retailOccupancy }}%</div>
              <div class="resource-cost">🛒 {{ retailShops }} shops</div>
            </div>
            <div class="resource-item">
              <el-progress type="circle" :percentage="diningPercent" :width="80" :stroke-width="8" color="#ec489a" />
              <div class="resource-label">Dining Capacity</div>
              <div class="resource-value">{{ diningCapacity }}%</div>
              <div class="resource-cost">🍽️ {{ diningVenues }} venues</div>
            </div>
            <div class="resource-item">
              <el-progress type="circle" :percentage="loungePercent" :width="80" :stroke-width="8" color="#06b6d4" />
              <div class="resource-label">Lounge Usage</div>
              <div class="resource-value">{{ loungeUsage }}%</div>
              <div class="resource-cost">💺 VIP lounges</div>
            </div>
          </div>
        </div>

        <!-- 安检通道状态卡片 -->
        <div class="glass-card security-card">
          <div class="card-title">🛂 Security Checkpoint Status</div>
          <div class="security-list">
            <div v-for="lane in securityLanes" :key="lane.name" class="security-row">
              <div class="lane-name">{{ lane.name }}</div>
              <div class="lane-queue">
                <span class="queue-count">🧑‍🤝‍🧑 {{ lane.queueLength }}</span>
                <span class="queue-time">⏱️ {{ lane.waitTime }}min</span>
              </div>
              <div class="lane-status" :class="lane.statusClass">{{ lane.statusText }}</div>
            </div>
          </div>
          <div class="security-footer">
            <span>🚪 {{ totalOpenLanes }} lanes open</span>
            <span>📊 Avg wait: {{ avgWaitTime }} min</span>
          </div>
        </div>

      </div>
    </div>

    <!-- KPI 栏 -->
    <div class="glass-card kpi-strip">
      <div class="kpi-item">
        <span class="kpi-label">🛫 Terminals</span>
        <span class="kpi-value">{{ terminals }}</span>
      </div>
      <div class="kpi-item">
        <span class="kpi-label">🧑‍🤝‍🧑 Pax Today</span>
        <span class="kpi-value">{{ passengersToday }}</span>
      </div>
      <div class="kpi-item">
        <span class="kpi-label">✈️ Flights</span>
        <span class="kpi-value">{{ flightsCount }}</span>
      </div>
      <div class="kpi-item">
        <span class="kpi-label">💰 Total Cost</span>
        <span class="kpi-value">{{ totalCostDisplay }}</span>
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

    <!-- Energy Savings Report Drawer - Airport Edition -->
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
            <span class="drawer-icon">🛫</span>
            <div class="drawer-title-wrapper">
              <span class="drawer-title">Airport Energy Savings Report</span>
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
              <div class="stat-value">{{ airportSavedEnergy }} MWh</div>
            </div>
          </div>
          <div class="core-stat-card">
            <div class="stat-icon">💰</div>
            <div class="stat-info">
              <div class="stat-label">Cost Saved</div>
              <div class="stat-value">${{ airportSavedCost }}</div>
              <div class="stat-rate">@ $0.238/kWh</div>
            </div>
          </div>
        </div>

        <!-- Carbon & Revenue Section -->
        <div class="carbon-section">
          <div class="section-title">🌍 Carbon Reduction & Revenue</div>
          <div class="carbon-grid">
            <div class="carbon-item">
              <div class="carbon-icon">🛫</div>
              <div class="carbon-info">
                <div class="carbon-label">CO₂ Reduction</div>
                <div class="carbon-value">{{ airportCarbonReduction }} tonnes</div>
                <div class="carbon-sub">≈ {{ airportTreesOffset }} trees/year</div>
              </div>
            </div>
            <div class="carbon-item">
              <div class="carbon-icon">💵</div>
              <div class="carbon-info">
                <div class="carbon-label">Carbon Credit Revenue</div>
                <div class="carbon-value">${{ airportCarbonRevenue }}</div>
                <div class="carbon-sub">@ $50/ton CO₂</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Annual Goal Progress -->
        <div class="goal-section">
          <div class="goal-header">
            <span>🎯 Annual Savings Target</span>
            <span class="goal-percent">{{ airportSavingPercent }}%</span>
          </div>
          <el-progress :percentage="airportSavingPercent" :stroke-width="10" color="#10b981" :show-text="false" />
          <div class="goal-detail">
            <span>Achieved: {{ airportSavedEnergy }} / {{ airportAnnualTarget }} MWh</span>
            <span>Remaining: {{ airportRemainingTarget }} MWh</span>
          </div>
          <div class="goal-days-info">Continuous operation: {{ airportContinuousDays }} days</div>
        </div>

        <!-- Monthly Trend Chart -->
        <div class="trend-chart">
          <div class="trend-header">📈 Monthly Savings Trend</div>
          <div ref="airportReportChartRef" style="height: 200px; width: 100%"></div>
        </div>

        <!-- Airport System Contribution Ranking -->
        <div class="ranking-section">
          <div class="ranking-header">🏆 Top Energy Saving Systems</div>
          <div class="ranking-list">
            <div v-for="(item, idx) in airportDeviceRanking" :key="idx" class="ranking-item">
              <div class="ranking-rank" :class="{ 'top-three': idx < 3 }">{{ idx + 1 }}</div>
              <div class="ranking-name">{{ item.name }}</div>
              <div class="ranking-bar-wrap">
                <div class="ranking-bar" :style="{ width: item.percent + '%', background: idx < 3 ? '#10b981' : '#3b82f6' }"></div>
              </div>
              <div class="ranking-value">{{ item.saved }} MWh</div>
            </div>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>

  <!-- Loading 页面 -->
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
          <span class="loading-dots">...</span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Initializing Smart Airport System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
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

// ==================== 节能模式状态 ====================
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

// ==================== 机场节能数据 ====================
let airportSavingStartTime = null
let airportBaselineHourlyConsumption = 0
let airportActualConsumption = 0
let airportLastTrackedElec = 0
const airportStartSavedEnergy = 42500 // 初始节电量 (MWh → 实际用 kWh 计算)
const SGD_ELECTRICITY_RATE = 0.238
const CARBON_FACTOR = 0.4
const CARBON_CREDIT_PRICE_SGD = 50

// Airport 节能响应式数据 (单位: MWh 展示, kWh 计算)
const airportSavedEnergy = ref(42.5)
const airportSavedCost = ref(10115.00)
const airportCarbonReduction = ref(17.0)
const airportCarbonRevenue = ref(850.00)
const airportSavingPercent = ref(5.67)
const airportContinuousDays = ref(15)
const airportAnnualTarget = ref(750)

// KPI 栏格式化
const savedCostDisplay = computed(() => airportSavedCost.value.toFixed(2))
const carbonRevenueDisplay = computed(() => airportCarbonRevenue.value.toFixed(2))
const totalCostDisplay = computed(() => totalCost.value)

// Airport 系统贡献排名 (MWh)
const airportDeviceRanking = ref([
  { name: 'HVAC System', saved: 18.5, percent: 44 },
  { name: 'Lighting System', saved: 12.2, percent: 29 },
  { name: 'Baggage Handling', saved: 5.8, percent: 14 },
  { name: 'APM/Train System', saved: 3.6, percent: 8 },
  { name: 'Other Systems', saved: 2.4, percent: 5 }
])

// 剩余目标 (MWh)
const airportRemainingTarget = computed(() => Math.max(0, (airportAnnualTarget.value - airportSavedEnergy.value).toFixed(1)))
const airportTreesOffset = computed(() => Math.round(airportCarbonReduction.value * 1000 / 22))

// 报告图表
let airportReportChart = null
const airportReportChartRef = ref(null)

// ==================== 响应式数据 ====================
const currentTime = ref('')
const isBackgroundLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing assets...')

// 机场 KPI 数据
const terminals = ref(4)
const passengersToday = ref(128500)
const flightsCount = ref(486)

// 能耗数据
const elecUsage = ref(18500)
const fuelUsage = ref(1250)
const waterUsage = ref(3850)

const elecTarget = 25000
const fuelTarget = 2000
const waterTarget = 6000

const elecPercent = ref(74.0)
const fuelPercent = ref(62.5)
const waterPercent = ref(64.2)

const elecCost = ref(0)
const fuelCost = ref(0)
const waterCost = ref(0)
const totalCost = ref(0)

// Airport Services 数据
const retailOccupancy = ref(78)
const retailPercent = ref(78)
const retailShops = ref(42)
const diningCapacity = ref(65)
const diningPercent = ref(65)
const diningVenues = ref(28)
const loungeUsage = ref(52)
const loungePercent = ref(52)

// ========== 厕所数据 ==========
const restrooms = ref([
  { floor: 'T1 Departure', total: 12, occupied: 5, statusText: 'Available', statusClass: 'available' },
  { floor: 'T1 Arrival', total: 10, occupied: 8, statusText: 'Limited', statusClass: 'limited' },
  { floor: 'T2 Arrival', total: 10, occupied: 3, statusText: 'Available', statusClass: 'available' },
  { floor: 'T3 International', total: 15, occupied: 11, statusText: 'Limited', statusClass: 'limited' }
])

const computedRestrooms = computed(() => {
  return restrooms.value.map(r => ({
    ...r,
    free: r.total - r.occupied,
    percent: (r.occupied / r.total) * 100
  }))
})

// ========== 航班数据 ==========
const flights = ref([
  { id: 1, flight: 'CA1835', destination: 'PEK', statusText: 'Boarding', statusClass: 'moving', time: '14:30' },
  { id: 3, flight: 'CZ3102', destination: 'CAN', statusText: 'On Time', statusClass: 'idle', time: '15:15' },
  { id: 4, flight: 'HU7182', destination: 'HAK', statusText: 'Boarding', statusClass: 'moving', time: '14:45' },
  { id: 5, flight: '3U8882', destination: 'CTU', statusText: 'On Time', statusClass: 'idle', time: '15:30' },
  { id: 6, flight: 'MF8132', destination: 'XMN', statusText: 'Departed', statusClass: 'normal', time: '14:00' }
])

const todayFlights = ref(486)
const avgDelay = ref(12)

// ========== 候机区域拥挤度数据 ==========
const gateCongestion = ref([
  { name: 'Gate A1', passengers: 85, congestion: 75, status: 'Busy', color: '#f59e0b' },
  { name: 'Gate A2', passengers: 42, congestion: 38, status: 'Moderate', color: '#3b82f6' },
  { name: 'Gate B1', passengers: 156, congestion: 92, status: 'Critical', color: '#ef4444' },
  { name: 'Gate B2', passengers: 28, congestion: 25, status: 'Quiet', color: '#10b981' },
  { name: 'Gate C1', passengers: 98, congestion: 82, status: 'Very Busy', color: '#f97316' },
  { name: 'Gate C2', passengers: 35, congestion: 31, status: 'Moderate', color: '#3b82f6' }
])

// ========== 安检通道数据 ==========
const securityLanes = ref([
  { name: 'Lane 1', queueLength: 23, waitTime: 12, statusText: 'Busy', statusClass: 'security-busy' },
  { name: 'Lane 2', queueLength: 8, waitTime: 4, statusText: 'Fast', statusClass: 'security-fast' },
  { name: 'Lane 3', queueLength: 31, waitTime: 16, statusText: 'Critical', statusClass: 'security-critical' },
  { name: 'Lane 4', queueLength: 5, waitTime: 3, statusText: 'Fast', statusClass: 'security-fast' }
])

const totalOpenLanes = computed(() => securityLanes.value.length)
const avgWaitTime = computed(() => {
  const total = securityLanes.value.reduce((sum, lane) => sum + lane.waitTime, 0)
  return Math.floor(total / securityLanes.value.length)
})

let timeTimer = null, dataInterval = null

// ==================== 节能模式逻辑 ====================
function handleEnergySavingToggle(val) {
  if (val) {
    startAirportEnergySavingModel()
    ElMessage.success({
      message: '🛫 Airport energy saving mode activated',
      duration: 2000,
      type: 'success'
    })
  } else {
    stopAirportEnergySavingModel()
    showEnergyReport.value = false
    ElMessage.info({
      message: 'Airport energy saving mode deactivated',
      duration: 2000,
      type: 'info'
    })
  }
}

function startAirportEnergySavingModel() {
  // 机场基线 = 电力消耗 (MWh → kWh)
  airportBaselineHourlyConsumption = elecUsage.value * 1000
  airportSavingStartTime = Date.now()
  airportActualConsumption = 0
  airportLastTrackedElec = elecUsage.value * 1000
  window._airportEnergySavingBoost = 0.88

  airportSavedEnergy.value = airportStartSavedEnergy / 1000
  airportSavedCost.value = parseFloat((airportStartSavedEnergy * SGD_ELECTRICITY_RATE).toFixed(2))
  airportCarbonReduction.value = parseFloat(((airportStartSavedEnergy * CARBON_FACTOR) / 1000).toFixed(1))
  airportCarbonRevenue.value = parseFloat((airportCarbonReduction.value * CARBON_CREDIT_PRICE_SGD).toFixed(2))

  const dailyAvgSaving = airportStartSavedEnergy / airportContinuousDays.value
  airportAnnualTarget.value = Math.round((dailyAvgSaving * 360) / 1000)
  airportSavingPercent.value = Math.min(100, Math.round((airportStartSavedEnergy / 1000 / airportAnnualTarget.value) * 100 * 10) / 10)
}

function stopAirportEnergySavingModel() {
  airportSavingStartTime = null
  window._airportEnergySavingBoost = null
  airportActualConsumption = 0
  airportLastTrackedElec = 0
  airportSavedEnergy.value = 0
  airportSavedCost.value = 0
  airportCarbonReduction.value = 0
  airportCarbonRevenue.value = 0
  airportSavingPercent.value = 0
  airportContinuousDays.value = 0
  airportAnnualTarget.value = 0
}

function updateAirportEnergySavings() {
  if (!isEnergySavingActive.value || !airportSavingStartTime) return

  const hoursElapsed = (Date.now() - airportSavingStartTime) / (1000 * 60 * 60)
  const baselineTotal = airportBaselineHourlyConsumption * hoursElapsed
  const actualTotal = airportActualConsumption || 0

  airportContinuousDays.value = Math.max(airportContinuousDays.value, Math.floor(hoursElapsed / 24) + 15)

  const newSavedEnergyKwh = airportStartSavedEnergy + Math.max(0, baselineTotal - actualTotal)
  airportSavedEnergy.value = parseFloat((newSavedEnergyKwh / 1000).toFixed(1))
  airportSavedCost.value = parseFloat((newSavedEnergyKwh * SGD_ELECTRICITY_RATE).toFixed(2))
  airportCarbonReduction.value = parseFloat(((newSavedEnergyKwh * CARBON_FACTOR) / 1000).toFixed(1))
  airportCarbonRevenue.value = parseFloat((airportCarbonReduction.value * CARBON_CREDIT_PRICE_SGD).toFixed(2))

  const dailyAvgSaving = newSavedEnergyKwh / airportContinuousDays.value
  airportAnnualTarget.value = Math.round((dailyAvgSaving * 360) / 1000)
  airportSavingPercent.value = Math.min(100, Math.round((airportSavedEnergy.value / airportAnnualTarget.value) * 100 * 10) / 10)
}

function trackAirportEnergyConsumption() {
  if (!isEnergySavingActive.value || !airportSavingStartTime) return

  const currentElecKwh = elecUsage.value * 1000
  if (airportLastTrackedElec === 0) {
    airportLastTrackedElec = currentElecKwh
    airportActualConsumption = 0
    return
  }

  const delta = Math.max(0, currentElecKwh - airportLastTrackedElec)
  if (delta > 0) {
    airportActualConsumption += delta
  }
  airportLastTrackedElec = currentElecKwh
}

// 初始化报告图表
function initAirportReportChart() {
  if (airportReportChartRef.value) {
    if (airportReportChart) airportReportChart.dispose()
    airportReportChart = echarts.init(airportReportChartRef.value)
    const currentWeekSaving = Math.max(0, Math.round((airportSavedEnergy.value * 1000 - airportStartSavedEnergy) / 1000 * 10) / 10)
    airportReportChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { top: 20, left: 50, right: 10, bottom: 20 },
      xAxis: {
        type: 'category',
        data: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'This Week'],
        axisLabel: { color: '#94a3b8', fontSize: 10 }
      },
      yAxis: {
        type: 'value',
        name: 'Saved Energy (MWh)',
        nameTextStyle: { color: '#94a3b8', fontSize: 10 },
        axisLabel: { color: '#94a3b8' }
      },
      series: [{
        type: 'bar',
        data: [7.8, 10.5, 12.3, 14.8, currentWeekSaving > 0 ? currentWeekSaving : 2.5],
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#10b981' }, { offset: 1, color: '#34d399' }] }
        },
        label: { show: true, position: 'top', color: '#94a3b8', fontSize: 10 }
      }]
    })
  }
}

// Watch report drawer
watch(showEnergyReport, (newVal) => {
  if (newVal) {
    nextTick(() => {
      initAirportReportChart()
    })
  } else if (airportReportChart) {
    airportReportChart.dispose()
    airportReportChart = null
  }
})

// ==================== 辅助函数 ====================
const loadingMessages = ['Preparing assets...', 'Loading background...', 'Initializing modules...', 'Establishing connection...', 'Starting dashboard...', 'Almost ready...']

const preloadBackground = () => new Promise((resolve) => {
  const img = new Image()
  img.src = 'https://aegisnx.com/wp-content/uploads/2026/05/1778306317503.png'
  let progress = 0, msgIdx = 0
  const msgInterval = setInterval(() => { if (msgIdx < loadingMessages.length - 1) loadingMessage.value = loadingMessages[++msgIdx] }, 800)
  const progInterval = setInterval(() => { if (progress < 90) loadingProgress.value = Math.min(progress += Math.random() * 10, 90) }, 100)
  img.onload = () => {
    clearInterval(msgInterval); clearInterval(progInterval)
    loadingMessage.value = 'Ready!'; loadingProgress.value = 100
    setTimeout(resolve, 500)
  }
  img.onerror = () => { clearInterval(msgInterval); clearInterval(progInterval); loadingProgress.value = 100; setTimeout(resolve, 300) }
})

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

function randomVariation(base, range = 0.05) {
  const change = base * (Math.random() - 0.5) * range * 2
  return Math.max(0, base + change)
}

function updateCosts() {
  elecCost.value = (elecUsage.value * 0.12).toFixed(2)
  fuelCost.value = (fuelUsage.value * 0.85).toFixed(2)
  waterCost.value = (waterUsage.value * 0.45).toFixed(2)
  totalCost.value = (parseFloat(elecCost.value) + parseFloat(fuelCost.value) + parseFloat(waterCost.value)).toFixed(2)
}

function updateServicesData() {
  retailOccupancy.value = Math.floor(randomVariation(78, 0.1))
  retailPercent.value = Math.min(100, Math.max(0, retailOccupancy.value))
  retailShops.value = Math.floor(randomVariation(42, 0.05))

  diningCapacity.value = Math.floor(randomVariation(65, 0.12))
  diningPercent.value = Math.min(100, Math.max(0, diningCapacity.value))
  diningVenues.value = Math.floor(randomVariation(28, 0.05))

  loungeUsage.value = Math.floor(randomVariation(52, 0.08))
  loungePercent.value = Math.min(100, Math.max(0, loungeUsage.value))
}

function updateRestroomData() {
  restrooms.value.forEach(r => {
    let delta = (Math.random() > 0.65 ? (Math.random() > 0.5 ? 1 : -1) : 0)
    r.occupied = Math.min(r.total, Math.max(0, r.occupied + delta))
    const percent = (r.occupied / r.total) * 100
    if (percent > 70) { r.statusText = 'Limited'; r.statusClass = 'limited' }
    else if (percent > 40) { r.statusText = 'Moderate'; r.statusClass = 'moderate' }
    else { r.statusText = 'Available'; r.statusClass = 'available' }
  })
}

function updateFlightData() {
  const statuses = [
    { text: 'Boarding', class: 'moving' },
    { text: 'On Time', class: 'idle' },
    { text: 'Delayed', class: 'warning' },
    { text: 'Departed', class: 'normal' }
  ]
  flights.value.forEach(f => {
    if (Math.random() > 0.7) {
      const newStatus = statuses[Math.floor(Math.random() * statuses.length)]
      f.statusText = newStatus.text
      f.statusClass = newStatus.class
    }
  })
  todayFlights.value = Math.floor(randomVariation(486, 0.03))
  avgDelay.value = Math.floor(randomVariation(12, 0.15))
}

function updateGateCongestion() {
  gateCongestion.value.forEach(gate => {
    let variation = (Math.random() - 0.5) * 0.15
    let newPassengers = Math.floor(gate.passengers * (1 + variation))
    newPassengers = Math.max(5, Math.min(200, newPassengers))
    gate.passengers = newPassengers
    gate.congestion = Math.floor((newPassengers / 180) * 100)

    if (gate.congestion >= 80) { gate.status = 'Critical'; gate.color = '#ef4444' }
    else if (gate.congestion >= 60) { gate.status = 'Very Busy'; gate.color = '#f97316' }
    else if (gate.congestion >= 40) { gate.status = 'Busy'; gate.color = '#f59e0b' }
    else if (gate.congestion >= 20) { gate.status = 'Moderate'; gate.color = '#3b82f6' }
    else { gate.status = 'Quiet'; gate.color = '#10b981' }
  })
}

function updateSecurityLanes() {
  securityLanes.value.forEach(lane => {
    let variation = (Math.random() - 0.5) * 0.2
    let newQueue = Math.floor(lane.queueLength * (1 + variation))
    newQueue = Math.max(2, Math.min(50, newQueue))
    lane.queueLength = newQueue
    lane.waitTime = Math.floor(newQueue / 2) + Math.floor(Math.random() * 3)

    if (lane.queueLength >= 30) { lane.statusText = 'Critical'; lane.statusClass = 'security-critical' }
    else if (lane.queueLength >= 20) { lane.statusText = 'Busy'; lane.statusClass = 'security-busy' }
    else if (lane.queueLength >= 10) { lane.statusText = 'Moderate'; lane.statusClass = 'security-moderate' }
    else { lane.statusText = 'Fast'; lane.statusClass = 'security-fast' }
  })
}

function refreshData() {
  passengersToday.value = Math.floor(randomVariation(128500, 0.05))
  flightsCount.value = Math.floor(randomVariation(486, 0.03))

  elecUsage.value = Math.floor(randomVariation(18500, 0.06))
  elecPercent.value = parseFloat(((elecUsage.value / elecTarget) * 100).toFixed(1))
  fuelUsage.value = Math.floor(randomVariation(1250, 0.07))
  fuelPercent.value = parseFloat(((fuelUsage.value / fuelTarget) * 100).toFixed(1))
  waterUsage.value = Math.floor(randomVariation(3850, 0.05))
  waterPercent.value = parseFloat(((waterUsage.value / waterTarget) * 100).toFixed(1))
  updateCosts()

  // 节能追踪
  if (isEnergySavingActive.value) {
    trackAirportEnergyConsumption()
    updateAirportEnergySavings()
  }

  updateServicesData()
  updateRestroomData()
  updateFlightData()
  updateGateCongestion()
  updateSecurityLanes()
}

function resizeCharts() {
  if (airportReportChart) airportReportChart.resize()
}

const isMobile = ref(false)
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}
onMounted(async () => {
  checkMobile();
  updateTime()
  timeTimer = setInterval(updateTime, 1000)
  await preloadBackground()
  isBackgroundLoaded.value = true
  await nextTick()
  setTimeout(() => {
    refreshData()

    // 启动节能模式
    if (isEnergySavingActive.value) {
      startAirportEnergySavingModel()
    }

    dataInterval = setInterval(refreshData, 5000)
  }, 100)
  window.addEventListener('resize', resizeCharts)
})

onBeforeUnmount(() => {
  clearInterval(timeTimer)
  clearInterval(dataInterval)
  window.removeEventListener('resize', resizeCharts)
  if (airportReportChart) airportReportChart.dispose()
})
</script>

<style scoped>
/* Loading 样式 */
.loading-container { position: fixed; inset: 0; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); z-index: 9999; display: flex; justify-content: center; align-items: center; }
.loading-content { text-align: center; padding: 40px; border-radius: 32px; background: rgba(15,23,42,0.6); backdrop-filter: blur(20px); border: 1px solid rgba(59,130,246,0.3); animation: fadeInUp 0.6s; }
.loading-spinner { position: relative; width: 80px; height: 80px; margin: 0 auto 24px; }
.spinner-ring { position: absolute; width: 100%; height: 100%; border-radius: 50%; border: 3px solid transparent; animation: spin 1.5s infinite; }
.spinner-ring:nth-child(1) { border-top-color: #3b82f6; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; width: 70%; height: 70%; top: 15%; left: 15%; animation-delay: 0.2s; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; width: 40%; height: 40%; top: 30%; left: 30%; animation-delay: 0.4s; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.loading-text { font-size: 28px; font-weight: 700; color: #e2e8f0; margin-bottom: 24px; }
.loading-progress { width: 280px; height: 4px; background: rgba(255,255,255,0.1); border-radius: 4px; margin: 0 auto 16px; overflow: hidden; }
.progress-bar { height: 100%; background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec489a); transition: width 0.3s; background-size: 200% auto; animation: shimmer 2s linear infinite; }
@keyframes shimmer { 0% { background-position: 0% 0%; } 100% { background-position: 200% 0%; } }
.loading-tip { font-size: 13px; color: #94a3b8; margin-bottom: 8px; }
.loading-subtip { font-size: 11px; color: #64748b; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

/* 主页面 */
.dashboard { height: 100%; width: 100%; display: flex; flex-direction: column; background-image: url('https://aegisnx.com/wp-content/uploads/2026/05/1778306317503.png'); background-size: cover; background-position: center; background-attachment: fixed; animation: fadeIn 0.5s; font-family: 'Inter', 'Segoe UI', system-ui, sans-serif; }
.top-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 28px 8px; margin: 0 24px; }
.header-left { width: auto; display: flex; align-items: center; }
.header-title { text-align: center; flex: 1; }
.main-title { font-size: 44px; font-weight: 800; background: linear-gradient(135deg, #e0f2fe, #bae6fd); -webkit-background-clip: text; background-clip: text; color: transparent; text-shadow: 0 0 30px rgba(96,165,250,0.5); letter-spacing: 3px; }
.datetime { font-size: 15px; color: #a5f3fc; font-weight: 600; background: transparent; backdrop-filter: blur(8px); padding: 8px 20px; border-radius: 12px; min-width: 280px; text-align: center; font-family: monospace; border: 1px solid rgba(165,243,252,0.3); text-shadow: 0 0 5px #a5f3fc; }
.kpi-strip { display: flex; justify-content: space-around; gap: 20px; margin: 10px 24px 20px; padding: 12px 20px; flex-wrap: wrap; }
.kpi-item { display: flex; gap: 12px; align-items: baseline; font-size: 15px; }
.kpi-label { color: #ffffff; font-weight: 500; }
.kpi-value { font-size: 24px; font-weight: 800; color: #facc15; font-family: monospace; text-shadow: 0 0 5px rgba(250,204,21,0.5); }
.content-area { flex: 1; display: flex; padding: 0 24px 24px; gap: 32px; overflow-y: auto; }
.left-panel { width: 320px; flex-shrink: 0; }
.right-panel { width: 420px; flex-shrink: 0; }
.center-void { flex: 1; }

/* 开关组 */
.button-group { display: flex; align-items: center; justify-content: center;gap: 10px; }
.button-group1 {
  width: 160px;
}
.switch-item { display: flex; align-items: center; gap: 5px; }
.switch-label { font-size: 14px; font-weight: 600; color: #fff; white-space: nowrap; font-weight: bold; }
.energy-saving-switch { --el-switch-on-color: #10b981; --el-switch-off-color: #475569; }
.report-switch { --el-switch-on-color: #3b82f6; --el-switch-off-color: #475569; }
:deep(.el-switch__label) { display: none !important; }

.glass-card { background: transparent !important; border-radius: 24px; border: 1px solid rgba(59, 130, 246, 0.4); box-shadow: 0 8px 28px rgba(0, 0, 0, 0.25); padding: 18px; transition: all 0.3s ease; margin-bottom: 20px; }
.glass-card:hover { backdrop-filter: blur(16px); border-color: rgba(59, 130, 246, 0.7); transform: translateY(-3px); box-shadow: 0 16px 32px rgba(0, 0, 0, 0.35); }
.card-title { font-size: 18px; font-weight: 800; color: #f0f9ff; margin-bottom: 14px; padding-left: 10px; border-left: 4px solid #3b82f6; text-shadow: 0 0 4px rgba(59,130,246,0.5); letter-spacing: 0.5px; }
.resource-grid { display: flex; justify-content: space-around; text-align: center; }
.resource-item .resource-label { margin-top: 8px; font-size: 13px; font-weight: 600; color: #cbd5e1; letter-spacing: 0.5px; }
.resource-value { font-size: 15px; font-weight: 800; color: #facc15; text-shadow: 0 0 4px rgba(250,204,21,0.3); }
.resource-cost { font-size: 12px; font-weight: 600; color: #a5f3fc; margin-top: 4px; }

/* 候机区域 */
.waiting-list { display: flex; flex-direction: column; gap: 10px; }
.waiting-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 6px 0; }
.waiting-name { width: 60px; font-size: 13px; font-weight: 700; color: #cbd5e1; }
.waiting-progress-wrapper { flex: 1; }
.waiting-progress-bg { height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden; }
.waiting-progress-fill { height: 100%; border-radius: 3px; transition: width 0.3s; }
.waiting-count { width: 70px; font-size: 12px; font-weight: 600; color: #a5f3fc; text-align: right; }
.waiting-status { width: 75px; font-size: 11px; font-weight: 700; text-align: right; }

/* 安检 */
.security-list { display: flex; flex-direction: column; }
.security-row { display: flex; align-items: center; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.06); }
.lane-name { width: 100px; font-weight: 700; color: #e2e8f0; font-size: 13px; }
.lane-queue { width: 100px; display: flex; gap: 12px; }
.queue-count, .queue-time { font-size: 12px; font-weight: 600; color: #a5f3fc; width: 20px; text-align: center }
.lane-status { width: 70px; text-align: center; font-size: 12px; font-weight: 800; padding: 4px 10px; border-radius: 20px; }
.security-fast { background: rgba(16,185,129,0.2); color: #34d399; }
.security-moderate { background: rgba(59,130,246,0.2); color: #60a5fa; }
.security-busy { background: rgba(245,158,11,0.2); color: #fbbf24; }
.security-critical { background: rgba(239,68,68,0.2); color: #f87171; }
.security-footer { display: flex; justify-content: space-between; margin-top: 12px; padding-top: 10px; border-top: 1px solid rgba(59,130,246,0.35); font-size: 11px; font-weight: 700; color: #94a3b8; }

/* 厕所 */
.restroom-table { width: 100%; }
.restroom-row-header { display: flex; justify-content: space-between; padding: 8px 4px; font-size: 11px; font-weight: 700; color: #60a5fa; text-transform: uppercase; letter-spacing: 0.8px; border-bottom: 1px solid rgba(59,130,246,0.4); margin-bottom: 8px; }
.restroom-row-header span { flex: 1; }
.restroom-row-header span:first-child { text-align: left; }
.restroom-row-header span:nth-child(2) { text-align: center; }
.restroom-row-header span:last-child { text-align: right; }
.restroom-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 4px; border-bottom: 1px solid rgba(255,255,255,0.06); transition: all 0.2s; }
.restroom-row:hover { background: rgba(59,130,246,0.12); border-radius: 8px; transform: translateX(4px); }
.floor-name { flex: 1; font-size: 13px; font-weight: 700; color: #e2e8f0; }
.status-badge { flex: 1; text-align: center; font-size: 11px; font-weight: 800; padding: 5px 10px; border-radius: 24px; width: fit-content; margin: 0 auto; }
.status-badge.available { background: rgba(16,185,129,0.2); color: #34d399; }
.status-badge.moderate { background: rgba(245,158,11,0.2); color: #fbbf24; }
.status-badge.limited { background: rgba(239,68,68,0.2); color: #f87171; }
.available-count { flex: 1; text-align: right; font-family: monospace; }
.count-number { font-size: 16px; font-weight: 800; color: #facc15; }
.count-total { font-size: 11px; font-weight: 600; color: #94a3b8; margin-left: 2px; }

/* 航班 */
.elevator-list { display: flex; flex-direction: column; }
.elevator-row { display: flex; align-items: center; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.06); }
.lift-name { width: 70px; font-weight: 800; color: #e2e8f0; }
.lift-floor { width: 65px; font-weight: 700; color: #a5f3fc; }
.lift-status { width: 80px; font-size: 12px; font-weight: 800; }
.lift-status.moving { color: #60a5fa; }
.lift-status.idle { color: #94a3b8; }
.lift-status.warning { color: #f87171; }
.lift-status.normal { color: #34d399; }
.lift-call { flex: 1; text-align: right; font-size: 12px; font-weight: 700; color: #facc15; font-family: monospace; }
.elevator-footer { display: flex; justify-content: space-between; margin-top: 12px; padding-top: 10px; border-top: 1px solid rgba(59,130,246,0.35); font-size: 11px; font-weight: 700; color: #94a3b8; }

.content-area::-webkit-scrollbar { width: 5px; }
.content-area::-webkit-scrollbar-track { background: rgba(15,23,42,0.5); border-radius: 4px; }
.content-area::-webkit-scrollbar-thumb { background: #3b82f6; border-radius: 4px; }
:deep(.el-progress-circle__track) { stroke: rgba(255,255,255,0.2); }
:deep(.el-progress__text) { color: #fff !important; font-weight: 700 !important; font-size: 14px !important; }

/* Drawer 样式 */
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
  scrollbar-width: none;
}
.drawer-header { display: flex; flex-direction: column; width: 100%; flex-wrap: wrap; gap: 12px; }
.drawer-title-section { display: flex; align-items: center; gap: 10px; }
.drawer-title-wrapper { display: flex; flex-direction: column; gap: 4px; }
.drawer-title-wrapper .drawer-title { font-size: 18px; font-weight: 700; color: green; letter-spacing: 1px; }
.drawer-location-wrapper { text-align: right; }
.drawer-location { display: flex; align-items: center; gap: 4px; font-size: 15px; color: #94a3b8; font-weight: bold; }
.drawer-icon { font-size: 22px; }
.report-content { padding: 0px; display: flex; flex-direction: column; gap: 20px; max-height: calc(100vh - 70px); overflow-y: auto; }
.report-content::-webkit-scrollbar { width: 4px; display: none; }
.report-content::-webkit-scrollbar-track { background: rgba(255, 255, 255, 0.05); border-radius: 4px; }
.report-content::-webkit-scrollbar-thumb { background: #10b981; border-radius: 4px; }

.report-core-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.core-stat-card { background: rgba(16, 185, 129, 0.08); border-radius: 20px; padding: 6px; display: flex; align-items: center; gap: 12px; border: 1px solid rgba(16, 185, 129, 0.2); }
.stat-icon { font-size: 32px; }
.stat-info { flex: 1; }
.stat-label { font-size: 11px; color: #94a3b8; display: block; margin-bottom: 4px; font-weight: bold; }
.stat-value { font-size: 22px; font-weight: 800; color: #facc15; font-family: monospace; }
.stat-rate { font-size: 11px; color: green; margin-top: 4px; font-weight: bold; }

.carbon-section { background: rgba(16, 185, 129, 0.08); border-radius: 20px; padding: 14px 16px; border: 1px solid rgba(59, 130, 246, 0.2); }
.section-title { font-size: 14px; color: #94a3b8; font-weight: bold; margin-bottom: 12px; }
.carbon-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.carbon-item { display: flex; align-items: center; gap: 10px; background: rgba(16, 185, 129, 0.08); border-radius: 16px; padding: 5px; }
.carbon-icon { font-size: 24px; }
.carbon-info { flex: 1; }
.carbon-label { font-size: 11px; font-weight: bold; color: #94a3b8; display: block; }
.carbon-value { font-size: 16px; font-weight: 700; color: #facc15; font-family: monospace; }
.carbon-sub { font-size: 11px; color: green; font-weight: bold; }

.goal-section { background: rgba(16, 185, 129, 0.08); border-radius: 20px; padding: 14px 16px; border: 1px solid rgba(16, 185, 129, 0.2); }
.goal-header { display: flex; justify-content: space-between; font-size: 13px; color: #94a3b8; font-weight: bold; margin-bottom: 10px; }
.goal-percent { font-size: 18px; font-weight: 700; color: #10b981; }
.goal-detail { display: flex; justify-content: space-between; font-size: 10px; color: #94a3b8; font-weight: bold; margin-top: 8px; }
.goal-days-info { font-size: 11px; color: #10b981; margin-top: 8px; text-align: center; font-weight: bold; }

.trend-chart { background: rgba(16, 185, 129, 0.08); border-radius: 20px; padding: 12px; }
.trend-header { font-size: 13px; font-weight: 600; color: #94a3b8; margin-bottom: 12px; font-weight: bold; }

.ranking-section { background: rgba(16, 185, 129, 0.08); border-radius: 20px; padding: 14px; }
.ranking-header { font-size: 13px; font-weight: 600; color: #94a3b8; margin-bottom: 12px; font-weight: bold; }
.ranking-list { display: flex; flex-direction: column; gap: 10px; }
.ranking-item { display: flex; align-items: center; gap: 10px; }
.ranking-rank { width: 26px; height: 26px; background: rgba(255, 255, 255, 0.08); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 600; color: #94a3b8; }
.ranking-rank.top-three { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.ranking-name { width: 120px; font-size: 11px; color: #cbd5e1; font-weight: bold; }
.ranking-bar-wrap { flex: 1; height: 6px; background: rgba(255, 255, 255, 0.1); border-radius: 10px; overflow: hidden; background-color: #1e293b; }
.ranking-bar { height: 100%; border-radius: 10px; }
.ranking-value { width: 65px; font-size: 12px; font-family: monospace; color: #facc15; font-weight: bold; text-align: right; }
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
/* ========== 移动端适配 ========== */
@media (max-width: 768px) {
  .top-header {
    flex-direction: column;
    padding: 12px 16px 8px;
    margin: 0 12px;
    gap: 10px;
  }
  .header-left { width: 100%; justify-content: center; }
  .main-title {
    font-size: 28px;
    letter-spacing: 1px;
  }
  .datetime {
    font-size: 11px;
    padding: 4px 12px;
    min-width: auto;
    width: auto;
    border-radius: 20px;
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
    gap: 8px;
  }
  .kpi-label { font-size: 12px; }
  .kpi-value { font-size: 18px; }
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
  .center-void { display: none; }
  .glass-card {
    border-radius: 20px;
    padding: 14px;
    margin-bottom: 16px;
  }
  .glass-card:hover { transform: none; backdrop-filter: blur(8px); }
  .card-title { font-size: 16px; margin-bottom: 12px; }
  .resource-grid { gap: 12px; flex-wrap: wrap; }
  .resource-item { flex: 1 1 30%; min-width: 90px; }
  .resource-item .resource-label { font-size: 12px; }
  .resource-value { font-size: 13px; }
  .resource-cost { font-size: 10px; }
  :deep(.el-progress-circle) { width: 70px !important; height: 70px !important; }
  :deep(.el-progress__text) { font-size: 12px !important; }
  .restroom-row { padding: 8px 0; }
  .floor-name { font-size: 12px; }
  .status-badge { font-size: 10px; padding: 3px 6px; }
  .count-number { font-size: 14px; }
  .count-total { font-size: 10px; }
  .waiting-row { gap: 8px; padding: 5px 0; }
  .waiting-name { width: 50px; font-size: 11px; }
  .waiting-count { width: 55px; font-size: 10px; }
  .waiting-status { width: 65px; font-size: 10px; }
  .security-row { padding: 8px 0; }
  .lane-name { width: 70px; font-size: 12px; }
  .lane-queue { width: 70px; gap: 6px; }
  .queue-count, .queue-time { font-size: 11px; width: auto; }
  .lane-status { width: 60px; font-size: 10px; padding: 3px 6px; }
  .security-footer { font-size: 10px; }
  .elevator-row { padding: 8px 0; }
  .lift-name { width: 55px; font-size: 13px; }
  .lift-floor { width: 50px; font-size: 11px; }
  .lift-status { width: 70px; font-size: 11px; }
  .lift-call { font-size: 11px; }
  .elevator-footer { font-size: 10px; }

  .energy-report-drawer :deep(.el-drawer) { width: 100% !important; }
  .report-core-stats { grid-template-columns: 1fr; }
  .carbon-grid { grid-template-columns: 1fr; }
  .ranking-name { width: 100px; font-size: 10px; }
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