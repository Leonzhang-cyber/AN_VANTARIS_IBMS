<template>
  <div class="capacity-forecast-container">
    <!-- Loading Screen -->
    <div v-if="!isLoaded" class="loading-container">
      <div class="loading-overlay">
        <div class="loading-content">
          <div class="loading-spinner">
            <div class="spinner-ring"></div>
            <div class="spinner-ring"></div>
            <div class="spinner-ring"></div>
          </div>
          <div class="loading-text">
            <span class="loading-title">Loading Capacity Forecast</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Capacity Planning & Forecasting</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="capacity-forecast-main">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Capacity Forecast</h1>
          <p class="page-subtitle">Predictive analysis for space, power and cooling capacity</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="runForecast">
            <el-icon><TrendCharts /></el-icon>
            Run Forecast
          </el-button>
          <el-button @click="exportReport">
            <el-icon><Download /></el-icon>
            Export Report
          </el-button>
        </div>
      </div>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon blue">
                <el-icon><Grid /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Space Capacity</span>
                <span class="card-value">{{ formatOneDecimal(spaceUtilization) }}%</span>
                <el-progress :percentage="spaceUtilization" :stroke-width="6" :color="spaceColor" :show-text="false" />
                <span class="card-hint">{{ formatNumber(spaceRemaining) }} U remaining</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon green">
                <el-icon><Cpu /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Power Capacity</span>
                <span class="card-value">{{ formatOneDecimal(powerUtilization) }}%</span>
                <el-progress :percentage="powerUtilization" :stroke-width="6" color="#10b981" :show-text="false" />
                <span class="card-hint">{{ formatNumber(powerRemaining) }} kW remaining</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon orange">
                <el-icon><Clock /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Cooling Capacity</span>
                <span class="card-value">{{ formatOneDecimal(coolingUtilization) }}%</span>
                <el-progress :percentage="coolingUtilization" :stroke-width="6" color="#f59e0b" :show-text="false" />
                <span class="card-hint">{{ formatNumber(coolingRemaining) }} kW remaining</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon purple">
                <el-icon><Clock /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Forecast Horizon</span>
                <span class="card-value">{{ forecastHorizon }} months</span>
                <el-progress :percentage="75" :stroke-width="6" color="#8b5cf6" :show-text="false" />
                <span class="card-hint">Next capacity review</span>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Capacity Forecast Charts Section -->
      <div class="forecast-section">
        <div class="section-header">
          <h3>Capacity Forecast Trends</h3>
          <el-radio-group v-model="forecastType" size="small">
            <el-radio-button label="space">Space (U)</el-radio-button>
            <el-radio-button label="power">Power (kW)</el-radio-button>
            <el-radio-button label="cooling">Cooling (kW)</el-radio-button>
          </el-radio-group>
        </div>
        <div class="forecast-chart-card">
          <div class="chart-container">
            <canvas id="forecastTrendChart"></canvas>
          </div>
        </div>
      </div>

      <!-- Forecast Summary Cards -->
      <div class="summary-section">
        <div class="section-header">
          <h3>Forecast Summary</h3>
        </div>
        <div class="summary-grid">
          <div class="summary-card">
            <div class="summary-header">
              <span class="summary-title">Space Capacity</span>
              <el-tag :type="spaceRiskLevel" size="small">{{ spaceRiskText }}</el-tag>
            </div>
            <div class="summary-content">
              <div class="summary-item">
                <span>Current Usage</span>
                <strong>{{ formatNumber(currentSpaceUsage) }} U</strong>
              </div>
              <div class="summary-item">
                <span>Forecast (12 months)</span>
                <strong>{{ formatNumber(forecastSpaceUsage) }} U</strong>
              </div>
              <div class="summary-item">
                <span>Remaining Capacity</span>
                <strong>{{ formatNumber(remainingSpaceCapacity) }} U</strong>
              </div>
              <div class="summary-item">
                <span>Months Until Full</span>
                <strong class="warning">{{ spaceMonthsUntilFull }} months</strong>
              </div>
            </div>
            <div class="summary-footer">
              <el-button type="primary" link @click="viewSpaceDetails">View Details →</el-button>
            </div>
          </div>

          <div class="summary-card">
            <div class="summary-header">
              <span class="summary-title">Power Capacity</span>
              <el-tag :type="powerRiskLevel" size="small">{{ powerRiskText }}</el-tag>
            </div>
            <div class="summary-content">
              <div class="summary-item">
                <span>Current Usage</span>
                <strong>{{ formatNumber(currentPowerUsage) }} kW</strong>
              </div>
              <div class="summary-item">
                <span>Forecast (12 months)</span>
                <strong>{{ formatNumber(forecastPowerUsage) }} kW</strong>
              </div>
              <div class="summary-item">
                <span>Remaining Capacity</span>
                <strong>{{ formatNumber(remainingPowerCapacity) }} kW</strong>
              </div>
              <div class="summary-item">
                <span>Months Until Full</span>
                <strong class="warning">{{ powerMonthsUntilFull }} months</strong>
              </div>
            </div>
            <div class="summary-footer">
              <el-button type="primary" link @click="viewPowerDetails">View Details →</el-button>
            </div>
          </div>

          <div class="summary-card">
            <div class="summary-header">
              <span class="summary-title">Cooling Capacity</span>
              <el-tag :type="coolingRiskLevel" size="small">{{ coolingRiskText }}</el-tag>
            </div>
            <div class="summary-content">
              <div class="summary-item">
                <span>Current Usage</span>
                <strong>{{ formatNumber(currentCoolingUsage) }} kW</strong>
              </div>
              <div class="summary-item">
                <span>Forecast (12 months)</span>
                <strong>{{ formatNumber(forecastCoolingUsage) }} kW</strong>
              </div>
              <div class="summary-item">
                <span>Remaining Capacity</span>
                <strong>{{ formatNumber(remainingCoolingCapacity) }} kW</strong>
              </div>
              <div class="summary-item">
                <span>Months Until Full</span>
                <strong class="warning">{{ coolingMonthsUntilFull }} months</strong>
              </div>
            </div>
            <div class="summary-footer">
              <el-button type="primary" link @click="viewCoolingDetails">View Details →</el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- Growth Rate Analysis -->
      <div class="growth-section">
        <div class="section-header">
          <h3>Growth Rate Analysis</h3>
        </div>
        <div class="growth-grid">
          <div class="growth-card">
            <div class="growth-icon">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="growth-info">
              <span class="growth-label">Historical Growth (12M)</span>
              <span class="growth-value">{{ formatOneDecimal(historicalGrowth) }}%</span>
              <el-progress :percentage="historicalGrowth" :stroke-width="6" color="#3b82f6" />
            </div>
          </div>
          <div class="growth-card">
            <div class="growth-icon">
              <el-icon><DataLine /></el-icon>
            </div>
            <div class="growth-info">
              <span class="growth-label">Forecast Growth (12M)</span>
              <span class="growth-value">{{ formatOneDecimal(forecastGrowth) }}%</span>
              <el-progress :percentage="forecastGrowth" :stroke-width="6" color="#f59e0b" />
            </div>
          </div>
          <div class="growth-card">
            <div class="growth-icon">
              <el-icon><Cpu /></el-icon>
            </div>
            <div class="growth-info">
              <span class="growth-label">Power Density Increase</span>
              <span class="growth-value">{{ formatOneDecimal(densityIncrease) }}%</span>
              <el-progress :percentage="densityIncrease" :stroke-width="6" color="#10b981" />
            </div>
          </div>
        </div>
      </div>

      <!-- Monthly Forecast Table -->
      <div class="table-section">
        <div class="section-header">
          <h3>Monthly Forecast Details</h3>
          <el-button type="primary" link @click="downloadForecastData">Download CSV →</el-button>
        </div>
        <el-table :data="monthlyForecast" stripe class="forecast-table">
          <el-table-column prop="month" label="Month" width="100" />
          <el-table-column label="Space (U)" min-width="200">
            <template #default="{ row }">
              <div class="forecast-progress">
                <div class="forecast-value-row">
                  <span class="forecast-value">{{ formatNumber(row.spaceUsed) }}/{{ formatNumber(row.spaceCapacity) }} U</span>
                  <span class="progress-percent">{{ formatOneDecimal((row.spaceUsed / row.spaceCapacity) * 100) }}%</span>
                </div>
                <el-progress :percentage="(row.spaceUsed / row.spaceCapacity) * 100" :stroke-width="8" :color="getProgressColor((row.spaceUsed / row.spaceCapacity) * 100)" :show-text="false" />
              </div>
            </template>
          </el-table-column>
          <el-table-column label="Power (kW)" min-width="200">
            <template #default="{ row }">
              <div class="forecast-progress">
                <div class="forecast-value-row">
                  <span class="forecast-value">{{ formatNumber(row.powerUsed) }}/{{ formatNumber(row.powerCapacity) }} kW</span>
                  <span class="progress-percent">{{ formatOneDecimal((row.powerUsed / row.powerCapacity) * 100) }}%</span>
                </div>
                <el-progress :percentage="(row.powerUsed / row.powerCapacity) * 100" :stroke-width="8" :color="getProgressColor((row.powerUsed / row.powerCapacity) * 100)" :show-text="false" />
              </div>
            </template>
          </el-table-column>
          <el-table-column label="Cooling (kW)" min-width="200">
            <template #default="{ row }">
              <div class="forecast-progress">
                <div class="forecast-value-row">
                  <span class="forecast-value">{{ formatNumber(row.coolingUsed) }}/{{ formatNumber(row.coolingCapacity) }} kW</span>
                  <span class="progress-percent">{{ formatOneDecimal((row.coolingUsed / row.coolingCapacity) * 100) }}%</span>
                </div>
                <el-progress :percentage="(row.coolingUsed / row.coolingCapacity) * 100" :stroke-width="8" :color="getProgressColor((row.coolingUsed / row.coolingCapacity) * 100)" :show-text="false" />
              </div>
            </template>
          </el-table-column>
          <el-table-column label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusTag(row)" size="small">{{ getStatusText(row) }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Recommendations Section -->
      <div class="recommendations-section">
        <div class="section-header">
          <h3>Capacity Recommendations</h3>
        </div>
        <div class="recommendations-grid">
          <div v-for="rec in recommendations" :key="rec.id" class="recommendation-card" :class="rec.priority">
            <div class="rec-icon">
              <el-icon><component :is="rec.icon" /></el-icon>
            </div>
            <div class="rec-content">
              <h4>{{ rec.title }}</h4>
              <p>{{ rec.description }}</p>
              <div class="rec-meta">
                <span class="rec-impact">Impact: {{ rec.impact }}</span>
                <span class="rec-timeline">Timeline: {{ rec.timeline }}</span>
              </div>
            </div>
            <div class="rec-action">
              <el-button type="primary" size="small" @click="applyRecommendation(rec)">Apply</el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="generateActionPlan">
          <el-icon><Document /></el-icon>
          Generate Action Plan
        </el-button>
        <el-button size="large" @click="scheduleReview">
          <el-icon><Calendar /></el-icon>
          Schedule Review Meeting
        </el-button>
        <el-button size="large" @click="setAlertThresholds">
          <el-icon><Bell /></el-icon>
          Set Alert Thresholds
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Grid, Cpu, Clock, TrendCharts, DataLine,
  Download, Calendar, Document, Bell, WarningFilled, Setting
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading capacity forecast data...')

// ==================== 格式化函数 ====================
const formatOneDecimal = (value: number) => {
  if (isNaN(value)) return '0'
  return value.toFixed(1)
}

const formatNumber = (value: number) => {
  if (isNaN(value)) return '0'
  // 检查是否为整数（处理浮点数精度问题）
  if (Math.abs(value - Math.round(value)) < 0.000001) {
    return Math.round(value).toString()
  }
  return value.toFixed(1)
}

// ==================== Reactive Data ====================
const forecastType = ref('space')

// Capacity metrics
const totalSpaceCapacity = ref(2520)
const currentSpaceUsage = ref(1680)
const totalPowerCapacity = ref(1500)
const currentPowerUsage = ref(985)
const totalCoolingCapacity = ref(1200)
const currentCoolingUsage = ref(785)

const spaceUtilization = computed(() => (currentSpaceUsage.value / totalSpaceCapacity.value) * 100)
const powerUtilization = computed(() => (currentPowerUsage.value / totalPowerCapacity.value) * 100)
const coolingUtilization = computed(() => (currentCoolingUsage.value / totalCoolingCapacity.value) * 100)

const spaceRemaining = computed(() => totalSpaceCapacity.value - currentSpaceUsage.value)
const powerRemaining = computed(() => totalPowerCapacity.value - currentPowerUsage.value)
const coolingRemaining = computed(() => totalCoolingCapacity.value - currentCoolingUsage.value)

const forecastHorizon = ref(12)
const historicalGrowth = ref(8.5)
const forecastGrowth = ref(9.2)
const densityIncrease = ref(6.8)

// Forecast values
const forecastSpaceUsage = ref(1980)
const remainingSpaceCapacity = computed(() => totalSpaceCapacity.value - forecastSpaceUsage.value)
const spaceMonthsUntilFull = ref(8)

const forecastPowerUsage = ref(1280)
const remainingPowerCapacity = computed(() => totalPowerCapacity.value - forecastPowerUsage.value)
const powerMonthsUntilFull = ref(10)

const forecastCoolingUsage = ref(1020)
const remainingCoolingCapacity = computed(() => totalCoolingCapacity.value - forecastCoolingUsage.value)
const coolingMonthsUntilFull = ref(9)

// Risk levels
const spaceRiskLevel = computed(() => {
  if (spaceMonthsUntilFull.value <= 6) return 'danger'
  if (spaceMonthsUntilFull.value <= 12) return 'warning'
  return 'success'
})
const spaceRiskText = computed(() => {
  if (spaceMonthsUntilFull.value <= 6) return 'Critical'
  if (spaceMonthsUntilFull.value <= 12) return 'Warning'
  return 'Good'
})

const powerRiskLevel = computed(() => {
  if (powerMonthsUntilFull.value <= 6) return 'danger'
  if (powerMonthsUntilFull.value <= 12) return 'warning'
  return 'success'
})
const powerRiskText = computed(() => {
  if (powerMonthsUntilFull.value <= 6) return 'Critical'
  if (powerMonthsUntilFull.value <= 12) return 'Warning'
  return 'Good'
})

const coolingRiskLevel = computed(() => {
  if (coolingMonthsUntilFull.value <= 6) return 'danger'
  if (coolingMonthsUntilFull.value <= 12) return 'warning'
  return 'success'
})
const coolingRiskText = computed(() => {
  if (coolingMonthsUntilFull.value <= 6) return 'Critical'
  if (coolingMonthsUntilFull.value <= 12) return 'Warning'
  return 'Good'
})

const spaceColor = computed(() => {
  if (spaceUtilization.value < 70) return '#10b981'
  if (spaceUtilization.value < 85) return '#f59e0b'
  return '#ef4444'
})

// Monthly forecast data
const monthlyForecast = ref([
  { month: 'Jan 2024', spaceUsed: 1680, spaceCapacity: 2520, powerUsed: 985, powerCapacity: 1500, coolingUsed: 785, coolingCapacity: 1200 },
  { month: 'Feb 2024', spaceUsed: 1700, spaceCapacity: 2520, powerUsed: 1000, powerCapacity: 1500, coolingUsed: 795, coolingCapacity: 1200 },
  { month: 'Mar 2024', spaceUsed: 1720, spaceCapacity: 2520, powerUsed: 1015, powerCapacity: 1500, coolingUsed: 805, coolingCapacity: 1200 },
  { month: 'Apr 2024', spaceUsed: 1745, spaceCapacity: 2520, powerUsed: 1030, powerCapacity: 1500, coolingUsed: 815, coolingCapacity: 1200 },
  { month: 'May 2024', spaceUsed: 1770, spaceCapacity: 2520, powerUsed: 1045, powerCapacity: 1500, coolingUsed: 825, coolingCapacity: 1200 },
  { month: 'Jun 2024', spaceUsed: 1795, spaceCapacity: 2520, powerUsed: 1060, powerCapacity: 1500, coolingUsed: 835, coolingCapacity: 1200 },
  { month: 'Jul 2024', spaceUsed: 1820, spaceCapacity: 2520, powerUsed: 1080, powerCapacity: 1500, coolingUsed: 850, coolingCapacity: 1200 },
  { month: 'Aug 2024', spaceUsed: 1845, spaceCapacity: 2520, powerUsed: 1100, powerCapacity: 1500, coolingUsed: 865, coolingCapacity: 1200 },
  { month: 'Sep 2024', spaceUsed: 1870, spaceCapacity: 2520, powerUsed: 1120, powerCapacity: 1500, coolingUsed: 880, coolingCapacity: 1200 },
  { month: 'Oct 2024', spaceUsed: 1895, spaceCapacity: 2520, powerUsed: 1140, powerCapacity: 1500, coolingUsed: 895, coolingCapacity: 1200 },
  { month: 'Nov 2024', spaceUsed: 1920, spaceCapacity: 2520, powerUsed: 1160, powerCapacity: 1500, coolingUsed: 910, coolingCapacity: 1200 },
  { month: 'Dec 2024', spaceUsed: 1945, spaceCapacity: 2520, powerUsed: 1180, powerCapacity: 1500, coolingUsed: 925, coolingCapacity: 1200 }
])

// Recommendations
const recommendations = ref([
  { id: 1, title: 'Add 2 New Racks to Row E', description: 'Space utilization projected to reach 85% in 6 months', impact: '+84 U capacity', timeline: 'Q1 2025', priority: 'high', icon: 'Grid' },
  { id: 2, title: 'Upgrade Power Distribution', description: 'Power capacity will reach 80% utilization in 8 months', impact: '+300 kW capacity', timeline: 'Q2 2025', priority: 'high', icon: 'Cpu' },
  { id: 3, title: 'Install Additional Cooling Units', description: 'Cooling capacity forecast to hit 85% within 9 months', impact: '+200 kW cooling', timeline: 'Q2 2025', priority: 'medium', icon: 'Clock' },
  { id: 4, title: 'Optimize Power Usage Effectiveness', description: 'Current PUE can be improved by 0.05', impact: 'Save 8% energy', timeline: 'Q1 2025', priority: 'medium', icon: 'Setting' }
])

// Helper functions
const getProgressColor = (percentage: number) => {
  if (percentage < 70) return '#10b981'
  if (percentage < 85) return '#f59e0b'
  return '#ef4444'
}

const getStatusTag = (row: any) => {
  const spacePct = (row.spaceUsed / row.spaceCapacity) * 100
  const powerPct = (row.powerUsed / row.powerCapacity) * 100
  const coolingPct = (row.coolingUsed / row.coolingCapacity) * 100
  const maxPct = Math.max(spacePct, powerPct, coolingPct)
  if (maxPct >= 90) return 'danger'
  if (maxPct >= 80) return 'warning'
  return 'success'
}

const getStatusText = (row: any) => {
  const spacePct = (row.spaceUsed / row.spaceCapacity) * 100
  const powerPct = (row.powerUsed / row.powerCapacity) * 100
  const coolingPct = (row.coolingUsed / row.coolingCapacity) * 100
  const maxPct = Math.max(spacePct, powerPct, coolingPct)
  if (maxPct >= 90) return 'Critical'
  if (maxPct >= 80) return 'Warning'
  return 'Normal'
}

// Actions
const runForecast = () => {
  ElMessage.success('Forecast recalculated with latest data')
}

const exportReport = () => {
  ElMessage.success('Forecast report export started')
}

const viewSpaceDetails = () => {
  forecastType.value = 'space'
  ElMessage.info('Viewing space capacity details')
}

const viewPowerDetails = () => {
  forecastType.value = 'power'
  ElMessage.info('Viewing power capacity details')
}

const viewCoolingDetails = () => {
  forecastType.value = 'cooling'
  ElMessage.info('Viewing cooling capacity details')
}

const downloadForecastData = () => {
  ElMessage.success('Forecast data CSV downloaded')
}

const applyRecommendation = (rec: any) => {
  ElMessage.success(`Applied: ${rec.title}`)
}

const generateActionPlan = () => {
  ElMessage.success('Action plan generated')
}

const scheduleReview = () => {
  ElMessage.info('Review meeting scheduling interface will open')
}

const setAlertThresholds = () => {
  ElMessage.info('Alert threshold configuration interface will open')
}

// Chart initialization
let forecastChart: echarts.ECharts | null = null
const initForecastChart = () => {
  const canvas = document.getElementById('forecastTrendChart') as HTMLCanvasElement
  if (!canvas) return

  const container = canvas.parentElement
  if (!container) return

  const rect = container.getBoundingClientRect()
  const width = rect.width
  const height = 400

  const pixelRatio = window.devicePixelRatio || 1
  canvas.width = width * pixelRatio
  canvas.height = height * pixelRatio
  canvas.style.width = `${width}px`
  canvas.style.height = `${height}px`

  if (forecastChart) forecastChart.dispose()
  forecastChart = echarts.init(canvas, null, {
    width: width,
    height: height,
    devicePixelRatio: pixelRatio
  })

  let seriesData
  if (forecastType.value === 'space') {
    seriesData = {
      tooltip: { trigger: 'axis' },
      legend: { data: ['Usage', 'Capacity'], bottom: 0, left: 'center' },
      grid: { top: 40, left: 60, right: 40, bottom: 50, containLabel: true },
      xAxis: { type: 'category', data: monthlyForecast.value.map(m => m.month), axisLabel: { rotate: 45, fontSize: 11 } },
      yAxis: { type: 'value', name: 'U Space' },
      series: [
        { name: 'Usage', type: 'line', data: monthlyForecast.value.map(m => m.spaceUsed), smooth: true, lineStyle: { color: '#3b82f6', width: 3 }, areaStyle: { opacity: 0.1 }, symbol: 'circle', symbolSize: 8 },
        { name: 'Capacity', type: 'line', data: monthlyForecast.value.map(m => m.spaceCapacity), lineStyle: { color: '#ef4444', width: 2, type: 'dashed' }, symbol: 'none' }
      ]
    }
  } else if (forecastType.value === 'power') {
    seriesData = {
      tooltip: { trigger: 'axis' },
      legend: { data: ['Usage', 'Capacity'], bottom: 0, left: 'center' },
      grid: { top: 40, left: 60, right: 40, bottom: 50, containLabel: true },
      xAxis: { type: 'category', data: monthlyForecast.value.map(m => m.month), axisLabel: { rotate: 45, fontSize: 11 } },
      yAxis: { type: 'value', name: 'Power (kW)' },
      series: [
        { name: 'Usage', type: 'line', data: monthlyForecast.value.map(m => m.powerUsed), smooth: true, lineStyle: { color: '#10b981', width: 3 }, areaStyle: { opacity: 0.1 }, symbol: 'circle', symbolSize: 8 },
        { name: 'Capacity', type: 'line', data: monthlyForecast.value.map(m => m.powerCapacity), lineStyle: { color: '#ef4444', width: 2, type: 'dashed' }, symbol: 'none' }
      ]
    }
  } else {
    seriesData = {
      tooltip: { trigger: 'axis' },
      legend: { data: ['Usage', 'Capacity'], bottom: 0, left: 'center' },
      grid: { top: 40, left: 60, right: 40, bottom: 50, containLabel: true },
      xAxis: { type: 'category', data: monthlyForecast.value.map(m => m.month), axisLabel: { rotate: 45, fontSize: 11 } },
      yAxis: { type: 'value', name: 'Cooling (kW)' },
      series: [
        { name: 'Usage', type: 'line', data: monthlyForecast.value.map(m => m.coolingUsed), smooth: true, lineStyle: { color: '#f59e0b', width: 3 }, areaStyle: { opacity: 0.1 }, symbol: 'circle', symbolSize: 8 },
        { name: 'Capacity', type: 'line', data: monthlyForecast.value.map(m => m.coolingCapacity), lineStyle: { color: '#ef4444', width: 2, type: 'dashed' }, symbol: 'none' }
      ]
    }
  }
  forecastChart.setOption(seriesData)
}

// 窗口大小变化处理
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    initForecastChart()
  }, 200)
}

// 监听 forecastType 变化
const refreshChart = () => {
  setTimeout(() => initForecastChart(), 100)
}

// Loading simulation
const startLoading = () => {
  const interval = setInterval(() => {
    if (loadingProgress.value < 90) loadingProgress.value += Math.random() * 10
  }, 200)
  return interval
}

onMounted(() => {
  const interval = startLoading()
  setTimeout(() => {
    clearInterval(interval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => {
        setTimeout(() => {
          initForecastChart()
          window.addEventListener('resize', handleResize)
        }, 200)
      })
    }, 400)
  }, 2800)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (resizeTimer) clearTimeout(resizeTimer)
  if (forecastChart) forecastChart.dispose()
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.capacity-forecast-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #eef2f6 100%);
}

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

.spinner-ring:nth-child(1) { border-top-color: #3b82f6; animation-delay: 0s; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-bottom: 24px;
  font-size: 24px;
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
  width: 320px;
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
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ==================== Main Content ==================== */
.capacity-forecast-main {
  padding: 24px 32px;
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Overview Section */
.overview-section {
  margin-bottom: 32px;
}

.overview-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  gap: 16px;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.card-icon.blue { background: #eff6ff; color: #3b82f6; }
.card-icon.green { background: #ecfdf5; color: #10b981; }
.card-icon.orange { background: #fffbeb; color: #f59e0b; }
.card-icon.purple { background: #f3e8ff; color: #8b5cf6; }

.card-info {
  flex: 1;
}

.card-label {
  display: block;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 4px;
}

.card-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.card-hint {
  display: block;
  font-size: 11px;
  color: #94a3b8;
  margin-top: 4px;
}

/* Forecast Section */
.forecast-section {
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.forecast-chart-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chart-container {
  width: 100%;
  min-height: 400px;
  position: relative;
}

.chart-container canvas {
  width: 100%;
  height: 100%;
  display: block;
}

/* Summary Section */
.summary-section {
  margin-bottom: 32px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.summary-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.summary-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.summary-content {
  margin-bottom: 16px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 13px;
  color: #64748b;
}

.summary-item strong {
  color: #1e293b;
  font-weight: 600;
}

.summary-item strong.warning {
  color: #f59e0b;
}

.summary-footer {
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
  text-align: right;
}

/* Growth Section */
.growth-section {
  margin-bottom: 32px;
}

.growth-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.growth-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  gap: 16px;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.growth-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: #eff6ff;
  color: #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.growth-info {
  flex: 1;
}

.growth-label {
  display: block;
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.growth-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

/* Table Section */
.table-section {
  margin-bottom: 32px;
}

.forecast-table {
  border-radius: 16px;
  overflow: hidden;
}

.forecast-progress {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.forecast-value-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.forecast-value {
  font-size: 12px;
  color: #64748b;
}

.progress-percent {
  font-size: 12px;
  font-weight: 600;
  color: #1e293b;
}

/* Recommendations Section */
.recommendations-section {
  margin-bottom: 32px;
}

.recommendations-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recommendation-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  gap: 16px;
  align-items: flex-start;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  border-left: 4px solid;
  transition: all 0.2s ease;
}

.recommendation-card:hover {
  transform: translateX(4px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.recommendation-card.high {
  border-left-color: #ef4444;
}

.recommendation-card.medium {
  border-left-color: #f59e0b;
}

.recommendation-card.low {
  border-left-color: #10b981;
}

.rec-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #3b82f6;
}

.rec-content {
  flex: 1;
}

.rec-content h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.rec-content p {
  font-size: 13px;
  color: #64748b;
  margin: 0 0 8px 0;
}

.rec-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
}

.rec-impact {
  color: #10b981;
}

.rec-timeline {
  color: #f59e0b;
}

.rec-action {
  flex-shrink: 0;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 24px;
}

.action-buttons .el-button {
  border-radius: 12px;
  padding: 10px 20px;
}

/* Responsive */
@media (max-width: 1200px) {
  .summary-grid { grid-template-columns: repeat(2, 1fr); }
  .growth-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .capacity-forecast-main { padding: 16px; }
  .page-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .summary-grid { grid-template-columns: 1fr; }
  .growth-grid { grid-template-columns: 1fr; }
  .recommendation-card { flex-direction: column; }
  .rec-action { align-self: flex-end; }
  .action-buttons { flex-direction: column; }
  .action-buttons .el-button { width: 100%; }
}
</style>