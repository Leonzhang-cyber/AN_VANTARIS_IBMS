<template>
  <div v-if="isBackgroundLoaded" class="dashboard">
    <div class="top-header">
      <div class="header-left">
        <div class="button-group">
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
        <div class="main-title">HOSPITAL<br></div>
      </div>
      <div class="datetime" v-if="isFullscreen">{{ currentTime }}</div>
      <div class="datetimeview1" v-if="!isFullscreen"></div>
    </div>

    <div class="content-area">
      <div class="left-panel">

        <!-- 急诊数据统计 -->
        <div class="glass-card emergency-card">
          <div class="card-title">🚨 Emergency Dept. Stats</div>
          <div class="emergency-grid">
            <div class="emergency-item">
              <div class="emergency-icon">👨‍⚕️</div>
              <div class="emergency-info">
                <span class="emergency-label">Doctors</span>
                <span class="emergency-value">{{ doctorsOnDuty }}</span>
                <span class="emergency-sub">on duty</span>
              </div>
            </div>
            <div class="emergency-item">
              <div class="emergency-icon">👩‍⚕️</div>
              <div class="emergency-info">
                <span class="emergency-label">Nurses</span>
                <span class="emergency-value">{{ nursesOnDuty }}</span>
                <span class="emergency-sub">on duty</span>
              </div>
            </div>
            <div class="emergency-item">
              <div class="emergency-icon">🩺</div>
              <div class="emergency-info">
                <span class="emergency-label">Patients</span>
                <span class="emergency-value">{{ emergencyPatients }}</span>
                <span class="emergency-sub">waiting</span>
              </div>
            </div>
            <div class="emergency-item">
              <div class="emergency-icon">🛏️</div>
              <div class="emergency-info">
                <span class="emergency-label">Beds Avail</span>
                <span class="emergency-value">{{ availableBeds }}</span>
                <span class="emergency-sub">/ {{ totalBeds }}</span>
              </div>
            </div>
          </div>
          <div class="emergency-footer">
            <span>⏱️ Avg wait: {{ avgWaitTime }} min</span>
            <span>🚑 {{ ambulancesToday }} arrivals today</span>
          </div>
        </div>

        <!-- 救护车状态 -->
        <div class="glass-card ambulance-card">
          <div class="card-title">🚑 Ambulance Status</div>
          <div class="ambulance-list">
            <div v-for="amb in ambulances" :key="amb.id" class="ambulance-row">
              <span class="ambulance-name">{{ amb.name }}</span>
              <span class="ambulance-location">{{ amb.location }}</span>
              <span class="ambulance-status" :class="amb.statusClass">{{ amb.statusText }}</span>
            </div>
          </div>
          <div class="ambulance-footer">
            <span>🚨 {{ activeAmbulances }} active</span>
            <span>📞 {{ callsToday }} calls today</span>
          </div>
        </div>

        <!-- 抽血检查数据统计 -->
        <div class="glass-card blood-test-card">
          <div class="card-title">🩸 Blood Test Analytics</div>
          <div class="blood-stats">
            <div class="blood-row">
              <span class="blood-label">📋 Tests Today</span>
              <span class="blood-value">{{ testsToday }}</span>
              <span class="blood-trend up">↑ {{ testIncrease }}%</span>
            </div>
            <div class="blood-row">
              <span class="blood-label">⏱️ Avg Wait Time</span>
              <span class="blood-value">{{ bloodWaitTime }} min</span>
              <span class="blood-trend down">↓ {{ waitDecrease }}%</span>
            </div>
            <div class="blood-row">
              <span class="blood-label">🩸 Samples Processing</span>
              <span class="blood-value">{{ samplesProcessing }}</span>
              <span class="blood-status">in lab</span>
            </div>
            <div class="blood-row">
              <span class="blood-label">✅ Completed Today</span>
              <span class="blood-value">{{ completedTests }}</span>
              <span class="blood-status">done</span>
            </div>
          </div>
          <div class="blood-footer">
            <span>📊 {{ completionRate }}% completion rate</span>
            <span>⏰ {{ peakTestHour }}</span>
          </div>
          <div ref="bloodTestChart" style="height: 100px; width: 100%; margin-top: 12px"></div>
        </div>

      </div>

      <div class="center-void"></div>

      <div class="right-panel">

        <!-- 医院人流/车流统计 -->
        <div class="glass-card traffic-card">
          <div class="card-title">👥🚗 Hospital Traffic</div>
          <div class="traffic-stats">
            <div class="traffic-row">
              <span class="traffic-label">🚶 Visitors Today</span>
              <span class="traffic-value">{{ visitorsToday }}</span>
            </div>
            <div class="traffic-row">
              <span class="traffic-label">🩺 Outpatients</span>
              <span class="traffic-value">{{ outpatientsToday }}</span>
            </div>
            <div class="traffic-row">
              <span class="traffic-label">🏥 Inpatients</span>
              <span class="traffic-value">{{ inpatientsNow }}</span>
            </div>
            <div class="traffic-row">
              <span class="traffic-label">🚗 Parking Occupancy</span>
              <div class="parking-progress">
                <div class="parking-fill" :style="{ width: parkingOccupancy + '%' }"></div>
                <span class="parking-percent">{{ parkingOccupancy }}%</span>
              </div>
            </div>
          </div>
          <div class="traffic-footer">
            <span>📊 {{ totalDailyVisitors }} total visits</span>
            <span>🚑 {{ ambulancesToday }} ambulances</span>
          </div>
        </div>

        <!-- 医院能耗与环境数据（仪表盘形式） -->
        <div class="glass-card environment-dashboard">
          <div class="card-title">💧⚡🌡️ Hospital Energy & Environment</div>
          <div class="env-dashboard-grid">
            <div class="env-dashboard-row">
              <div class="env-item">
                <el-progress type="circle" :percentage="waterPercent" :width="70" :stroke-width="7" color="#3b82f6" />
                <div class="env-label">Water</div>
                <div class="env-value">{{ waterUsage }} L</div>
                <div class="env-cost">💰 ${{ waterCost }}</div>
              </div>
              <div class="env-item">
                <el-progress type="circle" :percentage="elecPercent" :width="70" :stroke-width="7" color="#f59e0b" />
                <div class="env-label">Electricity</div>
                <div class="env-value">{{ elecUsage }} kWh</div>
                <div class="env-cost">💰 ${{ elecCost }}</div>
              </div>
              <div class="env-item">
                <el-progress type="circle" :percentage="hvacPercent" :width="70" :stroke-width="7" color="#10b981" />
                <div class="env-label">HVAC</div>
                <div class="env-value">{{ hvacUsage }} kWh</div>
                <div class="env-cost">💰 ${{ hvacCost }}</div>
              </div>
            </div>
            <div class="env-dashboard-row second-row">
              <div class="env-item">
                <el-progress type="circle" :percentage="tempPercent" :width="70" :stroke-width="7" color="#f97316" />
                <div class="env-label">Temperature</div>
                <div class="env-value">{{ avgTemp }} ℃</div>
                <div class="env-status" :class="tempStatusClass">{{ tempStatus }}</div>
              </div>
              <div class="env-item">
                <el-progress type="circle" :percentage="humidityPercent" :width="70" :stroke-width="7" color="#06b6d4" />
                <div class="env-label">Humidity</div>
                <div class="env-value">{{ currentHumidity }} %</div>
                <div class="env-status" :class="humidityStatusClass">{{ humidityStatus }}</div>
              </div>
              <div class="env-item">
                <el-progress type="circle" :percentage="co2Percent" :width="70" :stroke-width="7" color="#a855f7" />
                <div class="env-label">CO₂ Level</div>
                <div class="env-value">{{ currentCo2 }} ppm</div>
                <div class="env-status" :class="co2StatusClass">{{ co2Status }}</div>
              </div>
            </div>
          </div>
          <div class="env-footer">
            <span>🌡️ Target Temp: 22-24℃</span>
            <span>💨 Air Quality: {{ airQuality }}</span>
          </div>
        </div>

        <!-- 区域电梯占用数据 -->
        <div class="glass-card elevator-card">
          <div class="card-title">🚪 Elevator Occupancy</div>
          <div class="elevator-list">
            <div v-for="e in elevators" :key="e.id" class="elevator-row-simple">
              <span class="lift-name-simple">{{ e.name }}</span>
              <div class="lift-progress-wrapper">
                <div class="lift-progress-bg">
                  <div class="lift-progress-fill" :style="{ width: e.occupancy + '%', background: e.color }"></div>
                </div>
              </div>
              <span class="lift-occupancy">{{ e.occupancy }}%</span>
            </div>
          </div>
          <div class="elevator-footer-simple">
            <span>📊 {{ totalElevatorTrips }} trips today</span>
          </div>
        </div>

      </div>
    </div>

    <!-- KPI 栏 -->
    <div class="glass-card kpi-strip">
      <div class="kpi-item">
        <span class="kpi-label">🏥 Total Beds</span>
        <span class="kpi-value">{{ totalBeds }}</span>
      </div>
      <div class="kpi-item">
        <span class="kpi-label">📶 Equipment Online</span>
        <span class="kpi-value">{{ onlineRate }}%</span>
      </div>
      <div class="kpi-item">
        <span class="kpi-label">🌡️ Avg Temp</span>
        <span class="kpi-value">{{ avgTemp }}℃</span>
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

    <!-- Energy Savings Report Drawer - Hospital Edition -->
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
            <span class="drawer-icon">🏥</span>
            <div class="drawer-title-wrapper">
              <span class="drawer-title">Hospital Energy Savings Report</span>
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
              <div class="stat-value">{{ hospitalSavedEnergy }} kWh</div>
            </div>
          </div>
          <div class="core-stat-card">
            <div class="stat-icon">💰</div>
            <div class="stat-info">
              <div class="stat-label">Cost Saved</div>
              <div class="stat-value">${{ hospitalSavedCost }}</div>
              <div class="stat-rate">@ $0.238/kWh</div>
            </div>
          </div>
        </div>

        <!-- Carbon & Revenue Section -->
        <div class="carbon-section">
          <div class="section-title">🌍 Carbon Reduction & Revenue</div>
          <div class="carbon-grid">
            <div class="carbon-item">
              <div class="carbon-icon">🏥</div>
              <div class="carbon-info">
                <div class="carbon-label">CO₂ Reduction</div>
                <div class="carbon-value">{{ hospitalCarbonReduction }} kg</div>
                <div class="carbon-sub">≈ {{ hospitalTreesOffset }} trees/year</div>
              </div>
            </div>
            <div class="carbon-item">
              <div class="carbon-icon">💵</div>
              <div class="carbon-info">
                <div class="carbon-label">Carbon Credit Revenue</div>
                <div class="carbon-value">${{ hospitalCarbonRevenue }}</div>
                <div class="carbon-sub">@ $50/ton CO₂</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Annual Goal Progress -->
        <div class="goal-section">
          <div class="goal-header">
            <span>🎯 Annual Savings Target</span>
            <span class="goal-percent">{{ hospitalSavingPercent }}%</span>
          </div>
          <el-progress :percentage="hospitalSavingPercent" :stroke-width="10" color="#10b981" :show-text="false" />
          <div class="goal-detail">
            <span>Achieved: {{ hospitalSavedEnergy }} / {{ hospitalAnnualTarget }} kWh</span>
            <span>Remaining: {{ hospitalRemainingTarget }} kWh</span>
          </div>
          <div class="goal-days-info">Continuous operation: {{ hospitalContinuousDays }} days</div>
        </div>

        <!-- Monthly Trend Chart -->
        <div class="trend-chart">
          <div class="trend-header">📈 Monthly Savings Trend</div>
          <div ref="hospitalReportChartRef" style="height: 200px; width: 100%"></div>
        </div>

        <!-- Hospital System Contribution Ranking -->
        <div class="ranking-section">
          <div class="ranking-header">🏆 Top Energy Saving Systems</div>
          <div class="ranking-list">
            <div v-for="(item, idx) in hospitalDeviceRanking" :key="idx" class="ranking-item">
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
        <div class="loading-tip">Initializing Hospital IBMS System</div>
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
const isEnergySavingActive = ref(true)
const showEnergyReport = ref(false)

// ==================== 医院节能数据 ====================
let hospitalSavingStartTime = null
let hospitalBaselineHourlyConsumption = 0
let hospitalActualConsumption = 0
let hospitalLastTrackedElec = 0
const hospitalStartSavedEnergy = 51300 // 初始节电量 (kWh) — 医院能耗最高
const SGD_ELECTRICITY_RATE = 0.238
const CARBON_FACTOR = 0.4
const CARBON_CREDIT_PRICE_SGD = 50

// Hospital 节能响应式数据
const hospitalSavedEnergy = ref(51300)
const hospitalSavedCost = ref(12209.40)
const hospitalCarbonReduction = ref(20520)
const hospitalCarbonRevenue = ref(1026.00)
const hospitalSavingPercent = ref(8.55)
const hospitalContinuousDays = ref(16)
const hospitalAnnualTarget = ref(600000)

// KPI 栏格式化
const savedCostDisplay = computed(() => hospitalSavedCost.value.toFixed(2))
const carbonRevenueDisplay = computed(() => hospitalCarbonRevenue.value.toFixed(2))
const totalCostDisplay = computed(() => totalCost.value)

// Hospital 系统贡献排名
const hospitalDeviceRanking = ref([
  { name: 'HVAC System', saved: 22850, percent: 45 },
  { name: 'Medical Equipment', saved: 14680, percent: 29 },
  { name: 'Lighting System', saved: 7280, percent: 14 },
  { name: 'Water Heating', saved: 3850, percent: 8 },
  { name: 'Other Systems', saved: 2640, percent: 4 }
])

// 剩余目标
const hospitalRemainingTarget = computed(() => Math.max(0, Math.round(hospitalAnnualTarget.value - hospitalSavedEnergy.value)))
const hospitalTreesOffset = computed(() => Math.round(hospitalCarbonReduction.value / 22))

// 报告图表
let hospitalReportChart = null
const hospitalReportChartRef = ref(null)

// ==================== 响应式数据 ====================
const currentTime = ref('')
const isBackgroundLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing assets...')

const onlineRate = ref(99.2)
const avgTemp = ref(23.5)
const currentHumidity = ref(52)
const currentCo2 = ref(520)
const waterUsage = ref(5200)
const elecUsage = ref(22000)
const hvacUsage = ref(12000)
const waterTarget = 8000
const elecTarget = 32000
const hvacTarget = 18000
const waterPercent = ref(65.0)
const elecPercent = ref(68.8)
const hvacPercent = ref(66.7)
const waterCost = ref(0)
const elecCost = ref(0)
const hvacCost = ref(0)
const totalCost = ref(0)

const tempPercent = ref(58)
const humidityPercent = ref(52)
const co2Percent = ref(52)
const tempStatus = ref('Normal')
const tempStatusClass = ref('status-normal')
const humidityStatus = ref('Normal')
const humidityStatusClass = ref('status-normal')
const co2Status = ref('Normal')
const co2StatusClass = ref('status-normal')
const airQuality = ref('Good')

const doctorsOnDuty = ref(18)
const nursesOnDuty = ref(32)
const emergencyPatients = ref(24)
const totalBeds = ref(520)
const availableBeds = ref(186)
const avgWaitTime = ref(28)
const ambulancesToday = ref(47)

const ambulances = ref([
  { id: 1, name: 'AMB-01', location: 'Garage', statusText: 'Available', statusClass: 'available' },
  { id: 2, name: 'AMB-02', location: 'En Route', statusText: 'On Mission', statusClass: 'mission' },
  { id: 3, name: 'AMB-03', location: 'Hospital', statusText: 'Returning', statusClass: 'returning' },
  { id: 4, name: 'AMB-04', location: 'Garage', statusText: 'Available', statusClass: 'available' },
  { id: 5, name: 'AMB-05', location: 'Scene', statusText: 'On Mission', statusClass: 'mission' }
])
const activeAmbulances = computed(() => ambulances.value.filter(a => a.statusText === 'On Mission').length)
const callsToday = ref(86)

const elevators = ref([
  { id: 1, name: 'Inpatient Bldg', occupancy: 68, color: '#f59e0b' },
  { id: 2, name: 'Outpatient Bldg', occupancy: 42, color: '#3b82f6' },
  { id: 3, name: 'Diagnostic Center', occupancy: 35, color: '#10b981' },
  { id: 4, name: 'Emergency Wing', occupancy: 85, color: '#ef4444' },
  { id: 5, name: 'Admin Building', occupancy: 23, color: '#8b5cf6' }
])
const totalElevatorTrips = ref(1250)

const visitorsToday = ref(2850)
const outpatientsToday = ref(620)
const inpatientsNow = ref(334)
const parkingOccupancy = ref(76)
const totalDailyVisitors = ref(3850)

const testsToday = ref(342)
const testIncrease = ref(12)
const bloodWaitTime = ref(18)
const waitDecrease = ref(8)
const samplesProcessing = ref(56)
const completedTests = ref(286)
const completionRate = ref(83.6)
const peakTestHour = ref('09:00-11:00')

const bloodTestChart = ref(null)
let bloodTestIns = null
const bloodTestData = ref([18, 22, 45, 62, 58, 42, 35])

let timeTimer = null, dataInterval = null

// ==================== 节能模式逻辑 ====================
function handleEnergySavingToggle(val) {
  if (val) {
    startHospitalEnergySavingModel()
    ElMessage.success({
      message: '🏥 Hospital energy saving mode activated',
      duration: 2000,
      type: 'success'
    })
  } else {
    stopHospitalEnergySavingModel()
    showEnergyReport.value = false
    ElMessage.info({
      message: 'Hospital energy saving mode deactivated',
      duration: 2000,
      type: 'info'
    })
  }
}

function startHospitalEnergySavingModel() {
  hospitalBaselineHourlyConsumption = elecUsage.value + hvacUsage.value + waterUsage.value * 0.5
  hospitalSavingStartTime = Date.now()
  hospitalActualConsumption = 0
  hospitalLastTrackedElec = elecUsage.value + hvacUsage.value + waterUsage.value * 0.5
  window._hospitalEnergySavingBoost = 0.86

  hospitalSavedEnergy.value = hospitalStartSavedEnergy
  hospitalSavedCost.value = parseFloat((hospitalStartSavedEnergy * SGD_ELECTRICITY_RATE).toFixed(2))
  hospitalCarbonReduction.value = Math.round(hospitalStartSavedEnergy * CARBON_FACTOR)
  hospitalCarbonRevenue.value = parseFloat(((hospitalCarbonReduction.value / 1000) * CARBON_CREDIT_PRICE_SGD).toFixed(2))

  const dailyAvgSaving = hospitalStartSavedEnergy / hospitalContinuousDays.value
  hospitalAnnualTarget.value = Math.round(dailyAvgSaving * 360)
  hospitalSavingPercent.value = Math.min(100, Math.round((hospitalStartSavedEnergy / hospitalAnnualTarget.value) * 100 * 10) / 10)
}

function stopHospitalEnergySavingModel() {
  hospitalSavingStartTime = null
  window._hospitalEnergySavingBoost = null
  hospitalActualConsumption = 0
  hospitalLastTrackedElec = 0
  hospitalSavedEnergy.value = 0
  hospitalSavedCost.value = 0
  hospitalCarbonReduction.value = 0
  hospitalCarbonRevenue.value = 0
  hospitalSavingPercent.value = 0
  hospitalContinuousDays.value = 0
  hospitalAnnualTarget.value = 0
}

function updateHospitalEnergySavings() {
  if (!isEnergySavingActive.value || !hospitalSavingStartTime) return

  const hoursElapsed = (Date.now() - hospitalSavingStartTime) / (1000 * 60 * 60)
  const baselineTotal = hospitalBaselineHourlyConsumption * hoursElapsed
  const actualTotal = hospitalActualConsumption || 0

  hospitalContinuousDays.value = Math.max(hospitalContinuousDays.value, Math.floor(hoursElapsed / 24) + 16)

  const newSavedEnergy = hospitalStartSavedEnergy + Math.max(0, baselineTotal - actualTotal)
  hospitalSavedEnergy.value = Math.round(newSavedEnergy * 10) / 10
  hospitalSavedCost.value = parseFloat((hospitalSavedEnergy.value * SGD_ELECTRICITY_RATE).toFixed(2))
  hospitalCarbonReduction.value = Math.round(hospitalSavedEnergy.value * CARBON_FACTOR * 10) / 10
  const carbonReductionTonnes = hospitalCarbonReduction.value / 1000
  hospitalCarbonRevenue.value = parseFloat((carbonReductionTonnes * CARBON_CREDIT_PRICE_SGD).toFixed(2))

  const dailyAvgSaving = hospitalSavedEnergy.value / hospitalContinuousDays.value
  hospitalAnnualTarget.value = Math.round(dailyAvgSaving * 360)
  hospitalSavingPercent.value = Math.min(100, Math.round((hospitalSavedEnergy.value / hospitalAnnualTarget.value) * 100 * 10) / 10)
}

function trackHospitalEnergyConsumption() {
  if (!isEnergySavingActive.value || !hospitalSavingStartTime) return

  const currentTotal = elecUsage.value + hvacUsage.value + waterUsage.value * 0.5
  if (hospitalLastTrackedElec === 0) {
    hospitalLastTrackedElec = currentTotal
    hospitalActualConsumption = 0
    return
  }

  const delta = Math.max(0, currentTotal - hospitalLastTrackedElec)
  if (delta > 0) {
    hospitalActualConsumption += delta
  }
  hospitalLastTrackedElec = currentTotal
}

// 初始化报告图表
function initHospitalReportChart() {
  if (hospitalReportChartRef.value) {
    if (hospitalReportChart) hospitalReportChart.dispose()
    hospitalReportChart = echarts.init(hospitalReportChartRef.value)
    const currentWeekSaving = Math.max(0, Math.round(hospitalSavedEnergy.value - hospitalStartSavedEnergy))
    hospitalReportChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { top: 20, left: 45, right: 10, bottom: 20 },
      xAxis: {
        type: 'category',
        data: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'This Week'],
        axisLabel: { color: '#94a3b8', fontSize: 10 }
      },
      yAxis: {
        type: 'value',
        name: 'Saved Energy (kWh)',
        nameTextStyle: { color: '#94a3b8', fontSize: 10 },
        axisLabel: { color: '#94a3b8' }
      },
      series: [{
        type: 'bar',
        data: [9120, 12580, 14850, 16520, currentWeekSaving > 0 ? currentWeekSaving : 2180],
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
      initHospitalReportChart()
    })
  } else if (hospitalReportChart) {
    hospitalReportChart.dispose()
    hospitalReportChart = null
  }
})

// ==================== 辅助函数 ====================
const loadingMessages = ['Preparing assets...', 'Loading background...', 'Initializing modules...', 'Establishing connection...', 'Starting dashboard...', 'Almost ready...']

const preloadBackground = () => new Promise((resolve) => {
  const img = new Image()
  img.src = 'https://aegisnx.com/wp-content/uploads/2026/05/1778312977636.png'
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
  waterCost.value = (waterUsage.value * 0.5).toFixed(2)
  elecCost.value = (elecUsage.value * 0.13).toFixed(2)
  hvacCost.value = (hvacUsage.value * 0.15).toFixed(2)
  totalCost.value = (parseFloat(waterCost.value) + parseFloat(elecCost.value) + parseFloat(hvacCost.value)).toFixed(2)
}

function updateEnvironmentStatus() {
  if (avgTemp.value < 20) { tempStatus.value = 'Too Low'; tempStatusClass.value = 'status-warning'; tempPercent.value = 20 }
  else if (avgTemp.value > 26) { tempStatus.value = 'Too High'; tempStatusClass.value = 'status-warning'; tempPercent.value = 80 }
  else if (avgTemp.value >= 22 && avgTemp.value <= 24) { tempStatus.value = 'Ideal'; tempStatusClass.value = 'status-ideal'; tempPercent.value = parseFloat(50 + (avgTemp.value - 22) * 25).toFixed(1) }
  else { tempStatus.value = 'Normal'; tempStatusClass.value = 'status-normal'; tempPercent.value = parseFloat(50 + (avgTemp.value - 22) * 25).toFixed(1) }
  tempPercent.value = Math.min(100, Math.max(0, tempPercent.value))

  if (currentHumidity.value < 35) { humidityStatus.value = 'Too Dry'; humidityStatusClass.value = 'status-warning' }
  else if (currentHumidity.value > 65) { humidityStatus.value = 'Too Humid'; humidityStatusClass.value = 'status-warning' }
  else if (currentHumidity.value >= 45 && currentHumidity.value <= 55) { humidityStatus.value = 'Ideal'; humidityStatusClass.value = 'status-ideal' }
  else { humidityStatus.value = 'Normal'; humidityStatusClass.value = 'status-normal' }
  humidityPercent.value = currentHumidity.value

  if (currentCo2.value > 600) { co2Status.value = 'Poor'; co2StatusClass.value = 'status-warning'; airQuality.value = 'Poor' }
  else if (currentCo2.value > 500) { co2Status.value = 'Moderate'; co2StatusClass.value = 'status-moderate'; airQuality.value = 'Moderate' }
  else { co2Status.value = 'Good'; co2StatusClass.value = 'status-ideal'; airQuality.value = 'Good' }
  co2Percent.value = Math.min(100, Math.max(0, ((currentCo2.value - 400) / 400) * 100))
}

function updateEmergencyData() {
  doctorsOnDuty.value = Math.floor(randomVariation(18, 0.08))
  nursesOnDuty.value = Math.floor(randomVariation(32, 0.06))
  emergencyPatients.value = Math.floor(randomVariation(24, 0.15))
  availableBeds.value = Math.floor(randomVariation(186, 0.1))
  avgWaitTime.value = Math.floor(randomVariation(28, 0.12))
  ambulancesToday.value = Math.floor(randomVariation(47, 0.08))
}

function updateAmbulanceData() {
  const statuses = [
    { text: 'Available', class: 'available', locations: ['Garage', 'Standby'] },
    { text: 'On Mission', class: 'mission', locations: ['En Route', 'Scene'] },
    { text: 'Returning', class: 'returning', locations: ['Hospital', 'Nearby'] }
  ]
  ambulances.value.forEach(amb => {
    if (Math.random() > 0.7) {
      const newStatus = statuses[Math.floor(Math.random() * statuses.length)]
      amb.statusText = newStatus.text
      amb.statusClass = newStatus.class
      amb.location = newStatus.locations[Math.floor(Math.random() * newStatus.locations.length)]
    }
  })
  callsToday.value = Math.floor(randomVariation(86, 0.08))
}

function updateElevatorData() {
  elevators.value.forEach(e => {
    let variation = (Math.random() - 0.5) * 0.12
    let newOcc = e.occupancy * (1 + variation)
    newOcc = Math.min(95, Math.max(10, newOcc))
    e.occupancy = Math.floor(newOcc)
    if (e.occupancy >= 75) e.color = '#ef4444'
    else if (e.occupancy >= 50) e.color = '#f59e0b'
    else if (e.occupancy >= 25) e.color = '#3b82f6'
    else e.color = '#10b981'
  })
  totalElevatorTrips.value = Math.floor(randomVariation(1250, 0.05))
}

function updateTrafficData() {
  visitorsToday.value = Math.floor(randomVariation(2850, 0.08))
  outpatientsToday.value = Math.floor(randomVariation(620, 0.1))
  inpatientsNow.value = Math.floor(randomVariation(334, 0.05))
  parkingOccupancy.value = Math.floor(randomVariation(76, 0.1))
  totalDailyVisitors.value = Math.floor(randomVariation(3850, 0.06))
}

function updateBloodTestData() {
  testsToday.value = Math.floor(randomVariation(342, 0.08))
  testIncrease.value = Math.floor(randomVariation(12, 0.2))
  bloodWaitTime.value = Math.floor(randomVariation(18, 0.1))
  waitDecrease.value = Math.floor(randomVariation(8, 0.15))
  samplesProcessing.value = Math.floor(randomVariation(56, 0.12))
  completedTests.value = testsToday.value - samplesProcessing.value
  completionRate.value = parseFloat(((completedTests.value / testsToday.value) * 100).toFixed(1))
  const newData = bloodTestData.value.map(v => Math.floor(randomVariation(v, 0.12)))
  bloodTestData.value = newData
  if (bloodTestIns) { bloodTestIns.setOption({ series: [{ data: bloodTestData.value }] }) }
}

function refreshData() {
  onlineRate.value = randomVariation(99.2, 0.01).toFixed(1)
  waterUsage.value = Math.floor(randomVariation(5200, 0.05))
  waterPercent.value = parseFloat(((waterUsage.value / waterTarget) * 100).toFixed(1))
  elecUsage.value = Math.floor(randomVariation(22000, 0.05))
  elecPercent.value = parseFloat(((elecUsage.value / elecTarget) * 100).toFixed(1))
  hvacUsage.value = Math.floor(randomVariation(12000, 0.05))
  hvacPercent.value = parseFloat(((hvacUsage.value / hvacTarget) * 100).toFixed(1))
  avgTemp.value = parseFloat((21 + Math.random() * 4).toFixed(1))
  currentHumidity.value = Math.floor(40 + Math.random() * 30)
  currentCo2.value = Math.floor(420 + Math.random() * 200)

  updateCosts()

  // 节能追踪
  if (isEnergySavingActive.value) {
    trackHospitalEnergyConsumption()
    updateHospitalEnergySavings()
  }

  updateEnvironmentStatus()
  updateEmergencyData()
  updateAmbulanceData()
  updateElevatorData()
  updateTrafficData()
  updateBloodTestData()
}

function initCharts() {
  if (bloodTestChart.value) {
    if (bloodTestIns) bloodTestIns.dispose()
    bloodTestIns = echarts.init(bloodTestChart.value)
    bloodTestIns.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '5%', right: '5%', top: 10, bottom: 5, containLabel: true },
      xAxis: { type: 'category', data: ['00-04', '04-08', '08-12', '12-16', '16-20', '20-24'], axisLabel: { color: '#94a3b8', fontSize: 9 } },
      yAxis: { type: 'value', name: 'Tests', nameTextStyle: { color: '#64748b' }, axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: '#1e293b' } } },
      series: [{ type: 'line', data: bloodTestData.value, smooth: true, color: '#ec489a', areaStyle: { color: 'rgba(236,72,153,0.2)' }, lineStyle: { width: 2 }, symbol: 'circle', symbolSize: 4 }]
    })
  }
}

function resizeCharts() {
  bloodTestIns?.resize()
  if (hospitalReportChart) hospitalReportChart.resize()
}

onMounted(async () => {
  updateTime()
  timeTimer = setInterval(updateTime, 1000)
  await preloadBackground()
  isBackgroundLoaded.value = true
  await nextTick()
  setTimeout(() => {
    initCharts()
    refreshData()
    if (isEnergySavingActive.value) {
      startHospitalEnergySavingModel()
    }
    dataInterval = setInterval(refreshData, 4000)
  }, 100)
  window.addEventListener('resize', resizeCharts)
})

onBeforeUnmount(() => {
  clearInterval(timeTimer)
  clearInterval(dataInterval)
  window.removeEventListener('resize', resizeCharts)
  bloodTestIns?.dispose()
  if (hospitalReportChart) hospitalReportChart.dispose()
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
.dashboard { height: 100%; width: 100%; display: flex; flex-direction: column; background-image: url('https://aegisnx.com/wp-content/uploads/2026/05/1778312977636.png'); background-size: cover; background-position: center; background-attachment: fixed; animation: fadeIn 0.5s; font-family: 'Inter', 'Segoe UI', system-ui, sans-serif; }
.top-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 28px 8px; margin: 0 24px; }
.header-left { width: auto; display: flex; align-items: center; }
.header-title { text-align: center; flex: 1; }
.main-title { font-size: 44px; font-weight: 800; background: linear-gradient(135deg, #e0f2fe, #bae6fd); -webkit-background-clip: text; background-clip: text; color: transparent; letter-spacing: 3px; }
.datetime { font-size: 15px; color: #a5f3fc; font-weight: 600; background: transparent; backdrop-filter: blur(8px); padding: 8px 20px; border-radius: 12px; min-width: 280px; text-align: center; font-family: monospace; border: 1px solid rgba(165,243,252,0.3); text-shadow: 0 0 5px #a5f3fc; }
.kpi-strip { display: flex; justify-content: space-around; gap: 20px; margin: 10px 24px 20px; padding: 12px 20px; flex-wrap: wrap; }
.kpi-item { display: flex; gap: 12px; align-items: baseline; font-size: 15px; }
.kpi-label { color: #ffffff; font-weight: 500; }
.kpi-value { font-size: 24px; font-weight: 800; color: #facc15; font-family: monospace; text-shadow: 0 0 5px rgba(250,204,21,0.5); }
.content-area { flex: 1; display: flex; padding: 0 24px 24px; gap: 32px; overflow-y: auto; }
.left-panel { width: 340px; flex-shrink: 0; }
.right-panel { width: 420px; flex-shrink: 0; }
.center-void { flex: 1; }

/* 开关组 */
.button-group { display: flex; align-items: center; justify-content: center;gap: 10px; }
.switch-item { display: flex; align-items: center; gap: 5px; }
.switch-label { font-size: 14px; font-weight: 600; color: #fff; white-space: nowrap; font-weight: bold; }
.energy-saving-switch { --el-switch-on-color: #10b981; --el-switch-off-color: #475569; }
.report-switch { --el-switch-on-color: #3b82f6; --el-switch-off-color: #475569; }
:deep(.el-switch__label) { display: none !important; }

.glass-card { background: transparent; border-radius: 28px; border: 1px solid rgba(59,130,246,0.4); box-shadow: 0 20px 35px -12px rgba(0,0,0,0.6); padding: 16px; transition: all 0.3s; margin-bottom: 20px; }
.glass-card:hover { background: rgba(8,16,28,0.5); backdrop-filter: blur(8px); transform: translateY(-3px); border-color: rgba(59,130,246,0.6); }
.card-title { font-size: 16px; font-weight: 800; color: #f0f9ff; margin-bottom: 12px; padding-left: 10px; border-left: 4px solid #3b82f6; text-shadow: 0 0 4px rgba(59,130,246,0.5); }

/* 急诊 */
.emergency-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.emergency-item { display: flex; align-items: center; gap: 10px; background: rgba(255,255,255,0.05); border-radius: 12px; padding: 10px; }
.emergency-icon { font-size: 28px; }
.emergency-info { display: flex; flex-direction: column; font-weight: bold; }
.emergency-label { font-size: 11px; color: #f0f9ff; }
.emergency-value { font-size: 22px; font-weight: 800; color: #facc15; line-height: 1.2; }
.emergency-sub { font-size: 10px; color: #f0f9ff; }
.emergency-footer { display: flex; justify-content: space-between; margin-top: 12px; padding-top: 10px; border-top: 1px solid rgba(59,130,246,0.35); font-size: 11px; font-weight: 600; color: #94a3b8; }

/* 救护车 */
.ambulance-list { display: flex; flex-direction: column; gap: 8px; }
.ambulance-row { display: flex; align-items: center; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
.ambulance-name { width: 55px; font-weight: 700; color: #e2e8f0; font-size: 12px; }
.ambulance-location { flex: 1; font-size: 11px; color: #94a3b8; }
.ambulance-status { font-size: 11px; font-weight: 800; padding: 3px 10px; border-radius: 20px; }
.ambulance-status.available { background: rgba(16,185,129,0.2); color: #34d399; }
.ambulance-status.mission { background: rgba(239,68,68,0.2); color: #f87171; }
.ambulance-status.returning { background: rgba(245,158,11,0.2); color: #fbbf24; }
.ambulance-footer { display: flex; justify-content: space-between; margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(59,130,246,0.35); font-size: 11px; font-weight: 600; color: #94a3b8; }

/* 电梯 */
.elevator-list { display: flex; flex-direction: column; gap: 10px; }
.elevator-row-simple { display: flex; align-items: center; gap: 10px; padding: 6px 0; }
.lift-name-simple { width: 110px; font-size: 12px; font-weight: 600; color: #cbd5e1; }
.lift-progress-wrapper { flex: 1; }
.lift-progress-bg { height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden; }
.lift-progress-fill { height: 100%; border-radius: 3px; transition: width 0.3s; }
.lift-occupancy { width: 40px; font-size: 11px; font-weight: 700; color: #facc15; text-align: right; font-family: monospace; }
.elevator-footer-simple { margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(59,130,246,0.35); font-size: 11px; font-weight: 600; color: #94a3b8; text-align: center; }

/* 人流/车流 */
.traffic-stats { display: flex; flex-direction: column; gap: 12px; }
.traffic-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
.traffic-label { font-size: 12px; font-weight: 600; color: #cbd5e1; }
.traffic-value { font-size: 18px; font-weight: 800; color: #facc15; font-family: monospace; }
.parking-progress { display: flex; align-items: center; gap: 10px; width: 150px; }
.parking-progress .parking-fill { height: 6px; background: linear-gradient(90deg, #f59e0b, #ef4444); border-radius: 3px; transition: width 0.3s; flex: 1; }
.parking-percent { font-size: 12px; font-weight: 700; color: #f59e0b; width: 40px; text-align: right; }
.traffic-footer { display: flex; justify-content: space-between; margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(59,130,246,0.35); font-size: 11px; font-weight: 600; color: #94a3b8; }

/* 抽血检查 */
.blood-stats { display: flex; flex-direction: column; gap: 10px; }
.blood-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
.blood-label { font-size: 12px; font-weight: 600; color: #cbd5e1; width: 140px; }
.blood-value { font-size: 18px; font-weight: 800; color: #facc15; font-family: monospace; text-align: center; width: 60px; }
.blood-trend { font-size: 11px; font-weight: 700; padding: 2px 6px; border-radius: 12px; }
.blood-trend.up { background: rgba(16,185,129,0.2); color: #34d399; }
.blood-trend.down { background: rgba(239,68,68,0.2); color: #f87171; }
.blood-status { font-size: 11px; font-weight: 600; color: #64748b; }
.blood-footer { display: flex; justify-content: space-between; margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(59,130,246,0.35); font-size: 11px; font-weight: 600; color: #94a3b8; }

/* 环境仪表盘 */
.env-dashboard-grid { display: flex; flex-direction: column; gap: 16px; }
.env-dashboard-row { display: flex; justify-content: space-around; text-align: center; }
.second-row { margin-top: 4px; padding-top: 12px; border-top: 1px solid rgba(59,130,246,0.3); }
.env-item { text-align: center; }
.env-label { margin-top: 8px; font-size: 11px; font-weight: 600; color: #cbd5e1; }
.env-value { font-size: 13px; font-weight: 800; color: #facc15; font-family: monospace; }
.env-cost { font-size: 10px; font-weight: 600; color: #a5f3fc; margin-top: 4px; }
.env-status { font-size: 10px; font-weight: 700; margin-top: 4px; padding: 2px 6px; border-radius: 12px; display: inline-block; }
.status-ideal { background: rgba(16,185,129,0.2); color: #34d399; }
.status-normal { background: rgba(59,130,246,0.2); color: #60a5fa; }
.status-warning { background: rgba(239,68,68,0.2); color: #f87171; }
.status-moderate { background: rgba(245,158,11,0.2); color: #fbbf24; }
.env-footer { display: flex; justify-content: space-between; margin-top: 14px; padding-top: 10px; border-top: 1px solid rgba(59,130,246,0.35); font-size: 11px; font-weight: 600; color: #94a3b8; }

.content-area::-webkit-scrollbar { width: 5px; }
.content-area::-webkit-scrollbar-track { background: rgba(15,23,42,0.5); border-radius: 4px; }
.content-area::-webkit-scrollbar-thumb { background: #3b82f6; border-radius: 4px; }
:deep(.el-progress-circle__track) { stroke: rgba(255,255,255,0.2); }
:deep(.el-progress__text) { color: #fff !important; font-weight: 700 !important; font-size: 12px !important; }

/* Drawer 样式 */
.energy-report-drawer :deep(.el-drawer__header) {
  margin-bottom: 0; padding: 16px 20px;
  border-bottom: 1px solid rgba(16, 185, 129, 0.2);
  background: rgba(8, 16, 28, 0.95);
}
.energy-report-drawer :deep(.el-drawer__body) {
  padding: 0; background: linear-gradient(180deg, #0f172a 0%, #0a0f1a 100%);
  overflow: hidden; scrollbar-width: none;
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
/* 移动端 */
@media (max-width: 768px) {
  .top-header { flex-direction: column; padding: 12px 16px 8px; margin: 0 12px; gap: 8px; }
  .header-left { width: 100%; justify-content: center; }
  .main-title { font-size: 28px; letter-spacing: 1px; }
  .datetime { font-size: 11px; padding: 4px 12px; min-width: auto; width: auto; border-radius: 20px; }
  .kpi-strip { flex-wrap: wrap; gap: 12px; margin: 8px 16px 16px; padding: 12px; justify-content: center; }
  .kpi-item { flex: 1 1 40%; justify-content: space-between; gap: 8px; }
  .kpi-label { font-size: 12px; }
  .kpi-value { font-size: 18px; }
  .content-area { flex-direction: column; padding: 0 16px 16px; gap: 0; }
  .left-panel, .right-panel { width: 100%; flex-shrink: 1; }
  .center-void { display: none; }
  .glass-card { border-radius: 20px; padding: 14px; margin-bottom: 16px; }
  .glass-card:hover { transform: none; }
  .card-title { font-size: 15px; }
  .emergency-grid { gap: 8px; }
  .emergency-item { padding: 6px; gap: 6px; }
  .emergency-icon { font-size: 22px; }
  .emergency-value { font-size: 18px; }
  .ambulance-name { font-size: 11px; }
  .ambulance-location { font-size: 10px; }
  .ambulance-status { font-size: 10px; padding: 2px 6px; }
  .lift-name-simple { width: 90px; font-size: 11px; }
  .lift-occupancy { font-size: 10px; }
  .traffic-label { font-size: 11px; }
  .traffic-value { font-size: 16px; }
  .parking-progress { width: 110px; }
  .parking-percent { font-size: 11px; }
  .blood-label { width: 110px; font-size: 11px; }
  .blood-value { font-size: 16px; width: 50px; }
  .blood-trend { font-size: 10px; }
  .blood-status { font-size: 10px; }
  .env-dashboard-row { flex-wrap: wrap; gap: 12px; justify-content: center; }
  .env-item { flex: 1 1 30%; min-width: 90px; }
  :deep(.el-progress-circle) { width: 70px !important; height: 70px !important; }
  :deep(.el-progress__text) { font-size: 10px !important; }
  .env-label { font-size: 10px; }
  .env-value { font-size: 12px; }
  .env-cost { font-size: 9px; }
  .env-status { font-size: 9px; }
  [ref="bloodTestChart"] { height: 90px !important; }
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