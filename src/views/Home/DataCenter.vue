<template>
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
          <span class="loading-title">Loading</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Not Developed Yet</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Data Center Dashboard Page Content -->
  <div v-else class="data-center-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>Data Center Dashboard</h1>
        <p class="subtitle">Real-time monitoring of DCIM metrics including PUE, cooling efficiency, and capacity utilization</p>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="refreshData">Refresh</el-button>
        <el-button type="primary" :icon="Download" @click="exportReport">Export Report</el-button>
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            :shortcuts="dateShortcuts"
            size="default"
            style="width: 260px"
            @change="handleDateChange"
        />
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="kpi-cards">
      <div class="kpi-card pue">
        <div class="kpi-icon">
          <el-icon :size="32"><Lightning /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ pue }}<span class="unit"> PUE</span></div>
          <div class="kpi-label">Power Usage Effectiveness</div>
        </div>
        <div class="kpi-trend" :class="pueTrend <= 0 ? 'positive' : 'negative'">
          <el-icon><CaretBottom v-if="pueTrend <= 0" /><CaretTop v-else /></el-icon>
          {{ Math.abs(pueTrend) }}%
        </div>
      </div>
      <div class="kpi-card it-power">
        <div class="kpi-icon">
          <el-icon :size="32"><Cpu /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ itPower }}<span class="unit"> kW</span></div>
          <div class="kpi-label">IT Equipment Power</div>
        </div>
      </div>
      <div class="kpi-card total-power">
        <div class="kpi-icon">
          <el-icon :size="32"><Connection /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ totalPower }}<span class="unit"> kW</span></div>
          <div class="kpi-label">Total Facility Power</div>
        </div>
      </div>
      <div class="kpi-card cooling">
        <div class="kpi-icon">
          <el-icon :size="32"><WindPower /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ coolingEfficiency }}<span class="unit">%</span></div>
          <div class="kpi-label">Cooling Efficiency</div>
        </div>
        <el-progress :percentage="coolingEfficiency" :color="getEfficiencyColor(coolingEfficiency)" :stroke-width="8" style="margin-top: 8px" />
      </div>
    </div>

    <!-- DCIM Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-header">
          <span class="metric-title">Temperature</span>
          <span class="metric-value">{{ temperature }}°C</span>
        </div>
        <div class="metric-range">
          <span class="range-label">Normal Range: 18-27°C</span>
          <span class="range-status" :class="getTemperatureClass(temperature)">{{ getTemperatureStatus(temperature) }}</span>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-header">
          <span class="metric-title">Humidity</span>
          <span class="metric-value">{{ humidity }}%</span>
        </div>
        <div class="metric-range">
          <span class="range-label">Normal Range: 40-60%</span>
          <span class="range-status" :class="getHumidityClass(humidity)">{{ getHumidityStatus(humidity) }}</span>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-header">
          <span class="metric-title">DCiE</span>
          <span class="metric-value">{{ dcie }}%</span>
        </div>
        <div class="metric-range">
          <span class="range-label">Data Center Infrastructure Efficiency</span>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-header">
          <span class="metric-title">Rack Capacity</span>
          <span class="metric-value">{{ rackUtilization }}%</span>
        </div>
        <el-progress :percentage="rackUtilization" :color="getUtilizationColor(rackUtilization)" :stroke-width="8" />
      </div>
    </div>

    <!-- PUE Trend Chart -->
    <div class="chart-card">
      <div class="card-header">
        <h3>PUE Trend (Last 12 Months)</h3>
        <el-radio-group v-model="puePeriod" size="small" @change="fetchPueData">
          <el-radio-button label="month">Monthly</el-radio-button>
          <el-radio-button label="quarter">Quarterly</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-container" ref="pueChartRef"></div>
    </div>

    <!-- Power Distribution and Cooling Breakdown -->
    <div class="two-columns">
      <div class="chart-card">
        <div class="card-header">
          <h3>Power Distribution Breakdown</h3>
        </div>
        <div class="chart-container" ref="powerChartRef"></div>
      </div>
      <div class="chart-card">
        <div class="card-header">
          <h3>Cooling System Performance</h3>
        </div>
        <div class="chart-container" ref="coolingChartRef"></div>
      </div>
    </div>

    <!-- Rack and Infrastructure Tables -->
    <div class="two-columns">
      <div class="table-card">
        <div class="card-header">
          <h3>Top Racks by Power Consumption</h3>
          <el-button link type="primary" size="small">View All</el-button>
        </div>
        <el-table :data="topRacks" stripe size="small" style="width: 100%">
          <el-table-column prop="name" label="Rack Name" width="100" />
          <el-table-column prop="power" label="Power (kW)" width="90" align="right" />
          <el-table-column prop="utilization" label="Utilization" width="120">
            <template #default="{ row }">
              <el-progress :percentage="row.utilization" :stroke-width="6" :show-text="true" :format="(p) => p + '%'" />
            </template>
          </el-table-column>
          <el-table-column prop="temperature" label="Temp" width="70" align="center">
            <template #default="{ row }">
              <span :class="getTemperatureClass(row.temperature)">{{ row.temperature }}°C</span>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="table-card">
        <div class="card-header">
          <h3>Active Alarms</h3>
          <el-button link type="primary" size="small">View All</el-button>
        </div>
        <el-table :data="activeAlarms" stripe size="small" style="width: 100%">
          <el-table-column prop="severity" label="Severity" width="90">
            <template #default="{ row }">
              <el-tag :type="row.severity === 'critical' ? 'danger' : 'warning'" size="small">{{ row.severity }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="message" label="Message" min-width="180" show-overflow-tooltip />
          <el-table-column prop="time" label="Time" width="100" />
        </el-table>
      </div>
    </div>

    <!-- Capacity Planning -->
    <div class="chart-card">
      <div class="card-header">
        <h3>Capacity Planning Forecast</h3>
      </div>
      <div class="chart-container" ref="capacityChartRef"></div>
    </div>

    <!-- Efficiency Recommendations -->
    <div class="recommendations-section">
      <div class="section-header">
        <h2>
          <el-icon><EditPen /></el-icon>
          Efficiency Recommendations
        </h2>
        <el-button link type="primary" @click="viewAllRecommendations">View All →</el-button>
      </div>
      <div class="recommendations-list">
        <div v-for="rec in recommendations" :key="rec.id" class="recommendation-item">
          <div class="rec-icon" :class="rec.priority">
            <el-icon><Check /></el-icon>
          </div>
          <div class="rec-content">
            <div class="rec-title">{{ rec.title }}</div>
            <div class="rec-description">{{ rec.description }}</div>
            <div class="rec-metrics">
              <span><el-icon><TrendCharts /></el-icon> Potential PUE Reduction: {{ rec.pueReduction }}</span>
              <span><el-icon><Money /></el-icon> Est. Savings: ${{ rec.savings }}/year</span>
            </div>
          </div>
          <div class="rec-actions">
            <el-button size="small" type="primary" plain @click="viewRecommendation(rec)">Details</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Refresh,
  Download,
  Lightning,
  Cpu,
  Connection,
  WindPower,
  EditPen,
  Check,
  TrendCharts,
  Money,
  CaretTop,
  CaretBottom
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing...',
  'Almost ready...'
]

// ==================== Data Structures ====================
interface RackPower {
  name: string
  power: number
  utilization: number
  temperature: number
}

interface Alarm {
  id: number
  severity: string
  message: string
  time: string
}

interface Recommendation {
  id: number
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
  pueReduction: string
  savings: number
}

// ==================== State ====================
const dateRange = ref<[Date, Date] | null>(null)
const puePeriod = ref<'month' | 'quarter'>('month')

// Chart refs
const pueChartRef = ref<HTMLElement | null>(null)
const powerChartRef = ref<HTMLElement | null>(null)
const coolingChartRef = ref<HTMLElement | null>(null)
const capacityChartRef = ref<HTMLElement | null>(null)
let pueChart: echarts.ECharts | null = null
let powerChart: echarts.ECharts | null = null
let coolingChart: echarts.ECharts | null = null
let capacityChart: echarts.ECharts | null = null

// ==================== Mock Data ====================
const pue = ref(1.42)
const itPower = ref(1850)
const totalPower = ref(2627)
const coolingEfficiency = ref(78)
const temperature = ref(23.5)
const humidity = ref(48)
const dcie = ref(70.4)
const rackUtilization = ref(72)
const pueTrend = ref(-3.2)

const topRacks = ref<RackPower[]>([
  { name: 'Rack A01', power: 28.5, utilization: 95, temperature: 24.2 },
  { name: 'Rack B03', power: 24.2, utilization: 81, temperature: 23.8 },
  { name: 'Rack C02', power: 22.8, utilization: 76, temperature: 23.5 },
  { name: 'Rack D05', power: 21.5, utilization: 72, temperature: 23.2 },
  { name: 'Rack E01', power: 19.8, utilization: 66, temperature: 22.9 }
])

const activeAlarms = ref<Alarm[]>([
  { id: 1, severity: 'warning', message: 'UPS Battery Temperature High', time: '10:32 AM' },
  { id: 2, severity: 'warning', message: 'Rack A01 Power Utilization > 90%', time: '09:15 AM' },
  { id: 3, severity: 'critical', message: 'Cooling Tower Fan Vibration', time: '08:00 AM' },
  { id: 4, severity: 'info', message: 'Scheduled Maintenance in 24h', time: 'Yesterday' }
])

const recommendations = ref<Recommendation[]>([
  { id: 1, title: 'Hot Aisle Containment Implementation', description: 'Install hot aisle containment to improve cooling efficiency and reduce mixing.', priority: 'high', pueReduction: '0.08 - 0.12', savings: 45000 },
  { id: 2, title: 'UPS Efficiency Optimization', description: 'Enable ECO mode on UPS systems during low load periods.', priority: 'medium', pueReduction: '0.03 - 0.05', savings: 18000 },
  { id: 3, title: 'Server Virtualization', description: 'Consolidate underutilized servers to reduce IT power load.', priority: 'high', pueReduction: '0.05 - 0.08', savings: 32000 },
  { id: 4, title: 'Variable Speed Fan Control', description: 'Implement VFD control on CRAC units for better cooling modulation.', priority: 'medium', pueReduction: '0.04 - 0.06', savings: 25000 }
])

// ==================== Helper Functions ====================
const getEfficiencyColor = (percentage: number) => {
  if (percentage >= 80) return '#67c23a'
  if (percentage >= 70) return '#409eff'
  if (percentage >= 60) return '#e6a23c'
  return '#f56c6c'
}

const getUtilizationColor = (percentage: number) => {
  if (percentage >= 85) return '#f56c6c'
  if (percentage >= 70) return '#e6a23c'
  if (percentage >= 50) return '#409eff'
  return '#67c23a'
}

const getTemperatureClass = (temp: number) => {
  if (temp > 27) return 'text-danger'
  if (temp > 25) return 'text-warning'
  return 'text-success'
}

const getTemperatureStatus = (temp: number) => {
  if (temp > 27) return 'Critical'
  if (temp > 25) return 'Warning'
  return 'Normal'
}

const getHumidityClass = (humidity: number) => {
  if (humidity > 60) return 'text-danger'
  if (humidity > 55) return 'text-warning'
  if (humidity < 40) return 'text-warning'
  return 'text-success'
}

const getHumidityStatus = (humidity: number) => {
  if (humidity > 60) return 'High'
  if (humidity < 40) return 'Low'
  return 'Normal'
}

const dateShortcuts = [
  { text: 'Last 7 Days', value: () => { const end = new Date(); const start = new Date(); start.setDate(start.getDate() - 7); return [start, end] } },
  { text: 'Last 30 Days', value: () => { const end = new Date(); const start = new Date(); start.setDate(start.getDate() - 30); return [start, end] } },
  { text: 'This Month', value: () => { const end = new Date(); const start = new Date(); start.setDate(1); return [start, end] } }
]

// ==================== Chart Functions ====================
const generatePueData = () => {
  if (puePeriod.value === 'month') {
    return {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
      pue: [1.48, 1.47, 1.46, 1.45, 1.44, 1.44, 1.43, 1.43, 1.42, 1.42, 1.41, 1.41],
      target: [1.45, 1.45, 1.45, 1.45, 1.45, 1.45, 1.45, 1.45, 1.45, 1.45, 1.45, 1.45]
    }
  }
  return {
    labels: ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024', 'Q1 2025'],
    pue: [1.48, 1.46, 1.44, 1.43, 1.41],
    target: [1.45, 1.45, 1.45, 1.45, 1.45]
  }
}

const initPueChart = () => {
  if (!pueChartRef.value) return
  if (pueChart) pueChart.dispose()

  pueChart = echarts.init(pueChartRef.value)
  const data = generatePueData()

  pueChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Actual PUE', 'Target PUE'], bottom: 0 },
    grid: { left: '3%', right: '4%', top: '10%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', data: data.labels },
    yAxis: { type: 'value', name: 'PUE', min: 1.35, max: 1.55 },
    series: [
      { name: 'Actual PUE', type: 'line', data: data.pue, smooth: true, symbol: 'circle', lineStyle: { width: 3, color: '#409eff' }, areaStyle: { opacity: 0.1, color: '#409eff' } },
      { name: 'Target PUE', type: 'line', data: data.target, smooth: false, symbol: 'none', lineStyle: { width: 2, color: '#f56c6c', type: 'dashed' } }
    ]
  })
}

const initPowerChart = () => {
  if (!powerChartRef.value) return
  if (powerChart) powerChart.dispose()

  powerChart = echarts.init(powerChartRef.value)

  powerChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} kW ({d}%)' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      type: 'pie', radius: '55%', center: ['50%', '50%'],
      data: [
        { name: 'IT Equipment', value: 1850, itemStyle: { color: '#409eff' } },
        { name: 'Cooling', value: 520, itemStyle: { color: '#67c23a' } },
        { name: 'UPS Losses', value: 157, itemStyle: { color: '#e6a23c' } },
        { name: 'Lighting & Other', value: 100, itemStyle: { color: '#8b5cf6' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 }
    }]
  })
}

const initCoolingChart = () => {
  if (!coolingChartRef.value) return
  if (coolingChart) coolingChart.dispose()

  coolingChart = echarts.init(coolingChartRef.value)

  const metrics = ['CRAC Supply Temp', 'Return Temp', 'Setpoint', 'Outside Temp']
  const values = [18.5, 24.2, 21.0, 28.5]

  coolingChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: (value: number) => value + '°C' },
    grid: { left: '12%', right: '5%', top: '5%', bottom: '5%', containLabel: true },
    xAxis: { type: 'category', data: metrics },
    yAxis: { type: 'value', name: 'Temperature (°C)' },
    series: [{
      type: 'bar', data: values,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: (params: any) => {
          if (params.name === 'Return Temp') return '#409eff'
          if (params.name === 'Setpoint') return '#e6a23c'
          if (params.name === 'Outside Temp') return '#f56c6c'
          return '#67c23a'
        }},
      label: { show: true, position: 'top', formatter: '{c}°C' }
    }]
  })
}

const initCapacityChart = () => {
  if (!capacityChartRef.value) return
  if (capacityChart) capacityChart.dispose()

  capacityChart = echarts.init(capacityChartRef.value)

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const current = [65, 67, 69, 71, 72, 74, 75, 77, 78, 80, 81, 83]
  const forecast = [85, 87, 89, 91, 93, 95, null, null, null, null, null, null]
  const capacity = [95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95]

  capacityChart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: (value: number) => value + '%' },
    legend: { data: ['Current Utilization', 'Forecast', 'Max Capacity'], bottom: 0 },
    grid: { left: '3%', right: '4%', top: '10%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Capacity (%)', max: 100 },
    series: [
      { name: 'Current Utilization', type: 'line', data: current, smooth: true, symbol: 'circle', lineStyle: { width: 2, color: '#409eff' } },
      { name: 'Forecast', type: 'line', data: forecast, smooth: true, symbol: 'diamond', lineStyle: { width: 2, color: '#e6a23c', type: 'dashed' } },
      { name: 'Max Capacity', type: 'line', data: capacity, smooth: false, symbol: 'none', lineStyle: { width: 2, color: '#f56c6c', type: 'dashed' } }
    ]
  })
}

// ==================== Actions ====================
const refreshData = async () => {
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  ElMessage.success('Data center data refreshed')
  initPueChart()
  initPowerChart()
  initCoolingChart()
  initCapacityChart()
  tableLoading.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting data center report...')
}

const fetchPueData = () => {
  initPueChart()
}

const handleDateChange = () => {
  ElMessage.info('Date range updated')
}

const viewAllRecommendations = () => {
  ElMessage.info('Viewing all recommendations')
}

const viewRecommendation = (rec: Recommendation) => {
  ElMessage.info(`Viewing recommendation: ${rec.title}`)
}

// ==================== Window Resize Handler ====================
const handleResize = () => {
  pueChart?.resize()
  powerChart?.resize()
  coolingChart?.resize()
  capacityChart?.resize()
}

// ==================== Lifecycle ====================
onMounted(() => {
  let messageIndex = 0
  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 400)

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      setTimeout(() => {
        initPueChart()
        initPowerChart()
        initCoolingChart()
        initCapacityChart()
      }, 100)
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  pueChart?.dispose()
  powerChart?.dispose()
  coolingChart?.dispose()
  capacityChart?.dispose()
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
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
.data-center-page {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-title h1 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2f3d;
  margin: 0 0 4px 0;
}

.header-title .subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* KPI Cards */
.kpi-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.kpi-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s, box-shadow 0.2s;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.kpi-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.kpi-card.pue .kpi-icon { background: #e8f4ff; color: #409eff; }
.kpi-card.it-power .kpi-icon { background: #f0e8ff; color: #8b5cf6; }
.kpi-card.total-power .kpi-icon { background: #e8f8f0; color: #67c23a; }
.kpi-card.cooling .kpi-icon { background: #fff7e8; color: #e6a23c; }

.kpi-info {
  flex: 1;
}

.kpi-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
  line-height: 1.2;
}

.kpi-value .unit {
  font-size: 14px;
  font-weight: 400;
  color: #909399;
}

.kpi-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.kpi-trend {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 13px;
  font-weight: 500;
}

.kpi-trend.positive { color: #67c23a; }
.kpi-trend.negative { color: #f56c6c; }

/* Metrics Row */
.metrics-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.metric-card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.metric-title {
  font-size: 14px;
  color: #909399;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
}

.metric-range {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.range-label {
  color: #909399;
}

.range-status {
  font-weight: 500;
}

.range-status.text-success { color: #67c23a; }
.range-status.text-warning { color: #e6a23c; }
.range-status.text-danger { color: #f56c6c; }

/* Chart Cards */
.chart-card, .table-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.card-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: #1f2f3d;
}

.chart-container {
  height: 320px;
  width: 100%;
}

.two-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

/* Table Styles */
.text-success {
  color: #67c23a;
  font-weight: 500;
}

.text-warning {
  color: #e6a23c;
  font-weight: 500;
}

.text-danger {
  color: #f56c6c;
  font-weight: 500;
}

/* Recommendations Section */
.recommendations-section {
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1f2f3d;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recommendation-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 14px;
  transition: all 0.2s;
}

.recommendation-item:hover {
  background: #f5f7fa;
  transform: translateX(4px);
}

.rec-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rec-icon.high { background: #ffe8e8; color: #f56c6c; }
.rec-icon.medium { background: #fff7e8; color: #e6a23c; }
.rec-icon.low { background: #e8f8f0; color: #67c23a; }

.rec-content {
  flex: 1;
}

.rec-title {
  font-weight: 600;
  color: #1f2f3d;
  margin-bottom: 6px;
}

.rec-description {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.rec-metrics {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #909399;
}

.rec-metrics .el-icon {
  vertical-align: middle;
  margin-right: 4px;
}

.rec-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.recommendation-item:hover .rec-actions {
  opacity: 1;
}

:deep(.el-table) {
  border-radius: 12px;
}

:deep(.el-table th.el-table__cell) {
  background-color: #fafafa;
  font-weight: 600;
  color: #1f2f3d;
}
</style>