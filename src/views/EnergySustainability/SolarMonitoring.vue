<template>
  <!-- Loading Screen -->
  <div v-if="!isLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">
          <span class="loading-title">Solar Monitoring</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Solar PV Generation & Performance Analytics</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="solar-monitoring-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Sunny /></el-icon>
          Solar Monitoring
        </h1>
        <div class="page-subtitle">Real-time solar PV generation, irradiance tracking, and performance analytics</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="exportData">
          <el-icon><Download /></el-icon> Export Report
        </el-button>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><Sunny /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.currentPower }}<span class="stat-unit">kW</span></div>
          <div class="stat-label">Current Generation</div>
          <div class="stat-trend" :class="stats.powerTrend > 0 ? 'up' : 'down'">
            {{ stats.powerTrend > 0 ? '↑' : '↓' }} {{ Math.abs(stats.powerTrend) }}% vs last hour
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.todayGeneration }}<span class="stat-unit">kWh</span></div>
          <div class="stat-label">Today's Generation</div>
          <div class="stat-trend" :class="stats.todayTrend > 0 ? 'up' : 'down'">
            {{ stats.todayTrend > 0 ? '↑' : '↓' }} {{ Math.abs(stats.todayTrend) }}% vs yesterday
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.monthlyGeneration }}<span class="stat-unit">kWh</span></div>
          <div class="stat-label">Month to Date</div>
          <div class="stat-trend" :class="stats.monthlyTrend > 0 ? 'up' : 'down'">
            {{ stats.monthlyTrend > 0 ? '↑' : '↓' }} {{ Math.abs(stats.monthlyTrend) }}% vs last month
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">${{ stats.savings }}<span class="stat-unit">k</span></div>
          <div class="stat-label">CO₂ Savings</div>
          <div class="stat-trend up">{{ stats.co2Saved }} tCO₂e</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Peak Power</div>
        <div class="metric-value">{{ metrics.peakPower }}<span class="metric-unit">kW</span></div>
        <div class="metric-sub">Today at {{ metrics.peakTime }}</div>
        <div class="metric-target">Capacity: {{ metrics.capacity }} kWp</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Performance Ratio</div>
        <div class="metric-value">{{ metrics.performanceRatio }}<span class="metric-unit">%</span></div>
        <el-progress :percentage="metrics.performanceRatio" :stroke-width="8" :color="metrics.performanceRatio > 80 ? '#22c55e' : (metrics.performanceRatio > 65 ? '#f59e0b' : '#ef4444')" />
      </div>
      <div class="metric-card">
        <div class="metric-title">Irradiance</div>
        <div class="metric-value">{{ metrics.irradiance }}<span class="metric-unit">W/m²</span></div>
        <div class="metric-trend" :class="metrics.irradianceTrend > 0 ? 'positive' : 'negative'">
          {{ metrics.irradianceTrend > 0 ? '↑' : '↓' }} {{ Math.abs(metrics.irradianceTrend) }}% vs yesterday
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Grid Export</div>
        <div class="metric-value">{{ metrics.gridExport }}<span class="metric-unit">kW</span></div>
        <div class="metric-sub">Self-consumption: {{ metrics.selfConsumption }}%</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card large">
        <div class="chart-header">
          <span class="chart-title">Solar Generation Trend</span>
          <span class="chart-subtitle">Real-time power output</span>
          <el-select v-model="timeRange" size="small" style="width: 100px" @change="updateRealTimeChart">
            <el-option label="6 Hours" value="6" />
            <el-option label="12 Hours" value="12" />
            <el-option label="24 Hours" value="24" />
          </el-select>
        </div>
        <div class="chart-container" ref="realtimeChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Generation by Inverter</span>
          <span class="chart-subtitle">Power distribution</span>
        </div>
        <div class="chart-container" ref="inverterChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Irradiance vs Power</span>
          <span class="chart-subtitle">Correlation analysis</span>
        </div>
        <div class="chart-container" ref="irradianceChartEl"></div>
      </div>
    </div>

    <!-- Third Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Monthly Generation</span>
          <span class="chart-subtitle">Last 12 months</span>
        </div>
        <div class="chart-container" ref="monthlyChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Energy Balance</span>
          <span class="chart-subtitle">Consumption vs Generation</span>
        </div>
        <div class="chart-container" ref="balanceChartEl"></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            size="default"
            style="width: 260px"
        />
        <el-select v-model="inverterFilter" placeholder="Inverter" clearable style="width: 150px">
          <el-option v-for="i in inverters" :key="i" :label="i" :value="i" />
        </el-select>
        <el-select v-model="arrayFilter" placeholder="PV Array" clearable style="width: 140px">
          <el-option v-for="a in arrays" :key="a" :label="a" :value="a" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Inverters Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Inverter Performance</span>
        <el-button size="small" @click="viewAllInverters">View All →</el-button>
      </div>
      <el-table :data="paginatedInverters" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="name" label="Inverter Name" min-width="180" />
        <el-table-column prop="array" label="PV Array" width="120" />
        <el-table-column prop="currentPower" label="Power (kW)" width="120">
          <template #default="{ row }">
            <span :class="getPowerClass(row.currentPower, row.capacity)">{{ row.currentPower.toFixed(1) }} / {{ row.capacity }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="todayGeneration" label="Today (kWh)" width="120">
          <template #default="{ row }">
            {{ row.todayGeneration.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="monthlyGeneration" label="Month (kWh)" width="130">
          <template #default="{ row }">
            {{ row.monthlyGeneration.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="efficiency" label="Efficiency" width="100">
          <template #default="{ row }">
            <el-progress :percentage="row.efficiency" :stroke-width="6" :color="row.efficiency > 90 ? '#22c55e' : (row.efficiency > 80 ? '#f59e0b' : '#ef4444')" :format="() => `${row.efficiency.toFixed(1)}%`" />
          </template>
        </el-table-column>
        <el-table-column prop="temperature" label="Temp (°C)" width="100">
          <template #default="{ row }">
            <span :class="row.temperature > 45 ? 'metric-warning' : 'metric-good'">{{ row.temperature.toFixed(1) }}°C</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Normal' ? 'success' : (row.status === 'Warning' ? 'warning' : 'danger')" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewInverterDetail(row)">Details</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="totalRecords"
            layout="total, sizes, prev, pager, next"
            background
        />
      </div>
    </div>

    <!-- Inverter Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedInverter?.name" width="1000px" class="inverter-dialog">
      <div v-if="selectedInverter" class="inverter-detail">
        <!-- Header Stats -->
        <div class="detail-header-stats">
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedInverter.currentPower.toFixed(1) }}<span class="stat-unit">kW</span></div>
            <div class="detail-stat-label">Current Power</div>
            <div class="detail-stat-sub">Capacity: {{ selectedInverter.capacity }} kW</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedInverter.todayGeneration.toLocaleString() }}<span class="stat-unit">kWh</span></div>
            <div class="detail-stat-label">Today</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedInverter.efficiency.toFixed(1) }}<span class="stat-unit">%</span></div>
            <div class="detail-stat-label">Efficiency</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedInverter.temperature.toFixed(1) }}<span class="stat-unit">°C</span></div>
            <div class="detail-stat-label">Temperature</div>
          </div>
        </div>

        <!-- Basic Info -->
        <el-descriptions :column="3" border>
          <el-descriptions-item label="Inverter ID">{{ selectedInverter.id }}</el-descriptions-item>
          <el-descriptions-item label="PV Array">{{ selectedInverter.array }}</el-descriptions-item>
          <el-descriptions-item label="Manufacturer">{{ selectedInverter.manufacturer }}</el-descriptions-item>
          <el-descriptions-item label="Model">{{ selectedInverter.model }}</el-descriptions-item>
          <el-descriptions-item label="Install Date">{{ selectedInverter.installDate }}</el-descriptions-item>
          <el-descriptions-item label="DC Voltage">{{ selectedInverter.dcVoltage.toFixed(1) }} V</el-descriptions-item>
          <el-descriptions-item label="AC Voltage">{{ selectedInverter.acVoltage.toFixed(1) }} V</el-descriptions-item>
          <el-descriptions-item label="AC Current">{{ selectedInverter.acCurrent.toFixed(1) }} A</el-descriptions-item>
          <el-descriptions-item label="Frequency">{{ selectedInverter.frequency.toFixed(1) }} Hz</el-descriptions-item>
        </el-descriptions>

        <!-- Hourly Generation Chart -->
        <div class="detail-section">
          <div class="section-title">Hourly Generation Profile</div>
          <div class="trend-chart" ref="inverterDetailChartEl"></div>
        </div>

        <!-- Alerts -->
        <div class="detail-section" v-if="selectedInverter.alerts.length > 0">
          <div class="section-title">Recent Alerts</div>
          <el-table :data="selectedInverter.alerts" border stripe>
            <el-table-column prop="date" label="Date" width="150" />
            <el-table-column prop="type" label="Type" width="120" />
            <el-table-column prop="description" label="Description" min-width="300" />
            <el-table-column prop="severity" label="Severity" width="100">
              <template #default="{ row }">
                <el-tag :type="row.severity === 'High' ? 'danger' : (row.severity === 'Medium' ? 'warning' : 'info')" size="small">
                  {{ row.severity }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="exportInverterReport(selectedInverter)">Export Report</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Sunny, DataLine, Calendar, Money, Download, Refresh,
  RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading solar data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading solar inverter data...',
  'Fetching generation metrics...',
  'Calculating performance ratios...',
  'Analyzing irradiance data...',
  'Almost ready...'
]

// ==================== Types ====================
interface InverterAlert {
  date: string
  type: string
  description: string
  severity: string
}

interface SolarInverter {
  id: string
  name: string
  array: string
  manufacturer: string
  model: string
  capacity: number
  currentPower: number
  todayGeneration: number
  monthlyGeneration: number
  yearlyGeneration: number
  efficiency: number
  temperature: number
  dcVoltage: number
  acVoltage: number
  acCurrent: number
  frequency: number
  status: string
  installDate: string
  alerts: InverterAlert[]
}

// ==================== Mock Data ====================
const invertersList = ['Inverter 1', 'Inverter 2', 'Inverter 3', 'Inverter 4', 'Inverter 5', 'Inverter 6']
const arrays = ['Roof South', 'Roof East', 'Roof West', 'Ground East', 'Ground West', 'Carport']
const manufacturers = ['Huawei', 'Sungrow', 'Growatt', 'SMA', 'Fronius', 'ABB']

const generateInverterData = (): SolarInverter[] => {
  const inverters: SolarInverter[] = []

  for (let i = 1; i <= 12; i++) {
    const capacity = [20, 30, 40, 50, 60, 75, 100][Math.floor(Math.random() * 7)]
    const currentPower = parseFloat((capacity * (0.2 + Math.random() * 0.7)).toFixed(1))
    const todayGeneration = Math.round(currentPower * 6 + Math.random() * 50)
    const monthlyGeneration = Math.round(todayGeneration * 30 + Math.random() * 2000)
    const yearlyGeneration = monthlyGeneration * 12
    const efficiency = parseFloat((92 + Math.random() * 6).toFixed(1))
    const temperature = parseFloat((25 + Math.random() * 25).toFixed(1))
    const dcVoltage = parseFloat((600 + Math.random() * 200).toFixed(1))
    const acVoltage = parseFloat((380 + Math.random() * 20).toFixed(1))
    const acCurrent = parseFloat((currentPower * 1000 / 380 / 1.732).toFixed(1))
    const frequency = parseFloat((50 + (Math.random() - 0.5) * 0.5).toFixed(1))

    let status = 'Normal'
    if (temperature > 55) status = 'Critical'
    else if (temperature > 45) status = 'Warning'

    const alerts: InverterAlert[] = []
    if (temperature > 55) {
      alerts.push({
        date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
        type: 'Over Temperature',
        description: `Inverter temperature reached ${temperature.toFixed(1)}°C, above threshold`,
        severity: 'High'
      })
    } else if (temperature > 45) {
      alerts.push({
        date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
        type: 'High Temperature',
        description: `Inverter temperature at ${temperature.toFixed(1)}°C, efficiency impacted`,
        severity: 'Medium'
      })
    }
    if (efficiency < 94) {
      alerts.push({
        date: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
        type: 'Low Efficiency',
        description: `Inverter efficiency dropped to ${efficiency.toFixed(1)}%, below target`,
        severity: 'Medium'
      })
    }

    inverters.push({
      id: `INV-${String(i).padStart(4, '0')}`,
      name: invertersList[(i - 1) % invertersList.length] + (Math.floor((i - 1) / invertersList.length) + 1),
      array: arrays[(i - 1) % arrays.length],
      manufacturer: manufacturers[Math.floor(Math.random() * manufacturers.length)],
      model: `${['GT', 'SG', 'GW'][Math.floor(Math.random() * 3)]}-${Math.floor(Math.random() * 100)}`,
      capacity: capacity,
      currentPower: currentPower,
      todayGeneration: todayGeneration,
      monthlyGeneration: monthlyGeneration,
      yearlyGeneration: yearlyGeneration,
      efficiency: efficiency,
      temperature: temperature,
      dcVoltage: dcVoltage,
      acVoltage: acVoltage,
      acCurrent: acCurrent,
      frequency: frequency,
      status: status,
      installDate: new Date(Date.now() - Math.random() * 730 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
      alerts: alerts
    })
  }

  return inverters
}

const inverters = ref<SolarInverter[]>(generateInverterData())

// ==================== State ====================
const inverterFilter = ref('')
const arrayFilter = ref('')
const dateRange = ref<Date[] | null>(null)
const timeRange = ref('24')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const selectedInverter = ref<SolarInverter | null>(null)

// Chart refs
let realtimeChart: echarts.ECharts | null = null
let inverterChart: echarts.ECharts | null = null
let irradianceChart: echarts.ECharts | null = null
let monthlyChart: echarts.ECharts | null = null
let balanceChart: echarts.ECharts | null = null
let inverterDetailChart: echarts.ECharts | null = null

const realtimeChartEl = ref<HTMLElement | null>(null)
const inverterChartEl = ref<HTMLElement | null>(null)
const irradianceChartEl = ref<HTMLElement | null>(null)
const monthlyChartEl = ref<HTMLElement | null>(null)
const balanceChartEl = ref<HTMLElement | null>(null)
const inverterDetailChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  const currentPower = inverters.value.reduce((sum, i) => sum + i.currentPower, 0)
  const todayGeneration = inverters.value.reduce((sum, i) => sum + i.todayGeneration, 0)
  const monthlyGeneration = inverters.value.reduce((sum, i) => sum + i.monthlyGeneration, 0)
  const co2Saved = Math.round(monthlyGeneration * 0.0004)
  const savings = Math.round(monthlyGeneration * 0.12 / 1000)

  return {
    currentPower: parseFloat(currentPower.toFixed(1)),
    powerTrend: 5.2,
    todayGeneration: Math.round(todayGeneration),
    todayTrend: 8.5,
    monthlyGeneration: Math.round(monthlyGeneration),
    monthlyTrend: 12.3,
    savings: savings,
    co2Saved: co2Saved
  }
})

const metrics = computed(() => {
  const peakPower = Math.max(...inverters.value.map(i => i.currentPower))
  const peakTime = '12:30'
  const totalCapacity = inverters.value.reduce((sum, i) => sum + i.capacity, 0)
  const avgEfficiency = (inverters.value.reduce((sum, i) => sum + i.efficiency, 0) / inverters.value.length).toFixed(1)
  const avgIrradiance = 680
  const gridExport = parseFloat((stats.value.currentPower * 0.35).toFixed(1))
  const selfConsumption = 65

  return {
    peakPower: peakPower,
    peakTime: peakTime,
    capacity: totalCapacity,
    performanceRatio: parseFloat(avgEfficiency),
    irradiance: avgIrradiance,
    irradianceTrend: 3.2,
    gridExport: gridExport,
    selfConsumption: selfConsumption
  }
})

const filteredInverters = computed(() => {
  let filtered = [...inverters.value]

  if (inverterFilter.value) {
    filtered = filtered.filter(i => i.name === inverterFilter.value)
  }

  if (arrayFilter.value) {
    filtered = filtered.filter(i => i.array === arrayFilter.value)
  }

  if (dateRange.value && dateRange.value.length === 2) {
    // Filter logic would go here
  }

  return filtered
})

const totalRecords = computed(() => filteredInverters.value.length)

const paginatedInverters = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredInverters.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getPowerClass = (current: number, capacity: number): string => {
  const ratio = current / capacity
  if (ratio >= 0.7) return 'metric-good'
  if (ratio >= 0.4) return 'metric-warning'
  return 'metric-bad'
}

const resetFilters = () => {
  inverterFilter.value = ''
  arrayFilter.value = ''
  dateRange.value = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

// ==================== Chart Functions ====================
const initRealtimeChart = () => {
  if (!realtimeChartEl.value) return
  if (realtimeChart) {
    realtimeChart.dispose()
    realtimeChart = null
  }

  const hours = timeRange.value === '6' ? 6 : (timeRange.value === '12' ? 12 : 24)
  const labels = Array.from({ length: hours }, (_, i) => `${i}:00`)
  const powerData = labels.map(() => parseFloat((30 + Math.random() * 70).toFixed(1)))

  realtimeChart = echarts.init(realtimeChartEl.value)
  realtimeChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: labels, axisLabel: { rotate: 45, interval: Math.floor(hours / 12) } },
    yAxis: { type: 'value', name: 'Power (kW)' },
    series: [{
      type: 'line',
      data: powerData,
      smooth: true,
      lineStyle: { color: '#f59e0b', width: 3 },
      symbol: 'circle',
      symbolSize: 6,
      areaStyle: { opacity: 0.1, color: '#f59e0b' }
    }]
  })
}

const initInverterChart = () => {
  if (!inverterChartEl.value) return
  if (inverterChart) {
    inverterChart.dispose()
    inverterChart = null
  }

  const inverterPower = inverters.value.map(i => ({ name: i.name, value: i.currentPower }))

  inverterChart = echarts.init(inverterChartEl.value)
  inverterChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}<br/>Power: {c} kW' },
    legend: { orient: 'vertical', left: 'left', data: inverterPower.map(d => d.name), type: 'scroll' },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: inverterPower,
      label: { show: true, formatter: '{b}: {c} kW', fontSize: 10 }
    }]
  })
}

const initIrradianceChart = () => {
  if (!irradianceChartEl.value) return
  if (irradianceChart) {
    irradianceChart.dispose()
    irradianceChart = null
  }

  const hours = Array.from({ length: 12 }, (_, i) => `${i + 6}:00`)
  const irradianceData = [150, 320, 520, 680, 780, 820, 800, 720, 580, 380, 200, 80]
  const powerData = irradianceData.map(i => parseFloat((i * 0.12).toFixed(1)))

  irradianceChart = echarts.init(irradianceChartEl.value)
  irradianceChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Irradiance (W/m²)', 'Power (kW)'], bottom: 0 },
    grid: { top: 30, left: 60, right: 60, bottom: 40 },
    xAxis: { type: 'category', data: hours },
    yAxis: [
      { type: 'value', name: 'Irradiance (W/m²)', position: 'left' },
      { type: 'value', name: 'Power (kW)', position: 'right' }
    ],
    series: [
      { name: 'Irradiance (W/m²)', type: 'line', data: irradianceData, lineStyle: { color: '#f59e0b', width: 2 }, symbol: 'circle', areaStyle: { opacity: 0.1 } },
      { name: 'Power (kW)', type: 'line', data: powerData, lineStyle: { color: '#22c55e', width: 2 }, symbol: 'diamond', yAxisIndex: 1 }
    ]
  })
}

const initMonthlyChart = () => {
  if (!monthlyChartEl.value) return
  if (monthlyChart) {
    monthlyChart.dispose()
    monthlyChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const generationData = [12500, 11800, 14200, 15800, 16800, 16200, 17200, 17500, 15800, 14200, 12800, 11800]

  monthlyChart = echarts.init(monthlyChartEl.value)
  monthlyChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Generation (kWh)' },
    series: [{
      type: 'bar',
      data: generationData,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#f59e0b' },
      label: { show: true, position: 'top', formatter: '{c} kWh' }
    }]
  })
}

const initBalanceChart = () => {
  if (!balanceChartEl.value) return
  if (balanceChart) {
    balanceChart.dispose()
    balanceChart = null
  }

  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const generationData = hours.map(() => parseFloat((20 + Math.random() * 60).toFixed(1)))
  const consumptionData = hours.map(() => parseFloat((30 + Math.random() * 40).toFixed(1)))

  balanceChart = echarts.init(balanceChartEl.value)
  balanceChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Solar Generation', 'Building Load'], bottom: 0 },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: hours, axisLabel: { rotate: 45, interval: 3 } },
    yAxis: { type: 'value', name: 'Power (kW)' },
    series: [
      { name: 'Solar Generation', type: 'line', data: generationData, lineStyle: { color: '#f59e0b', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Building Load', type: 'line', data: consumptionData, lineStyle: { color: '#3b82f6', width: 2 }, areaStyle: { opacity: 0.1 } }
    ]
  })
}

const initInverterDetailChart = () => {
  if (!inverterDetailChartEl.value || !selectedInverter.value) return
  if (inverterDetailChart) {
    inverterDetailChart.dispose()
    inverterDetailChart = null
  }

  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const powerData = hours.map(() => parseFloat((selectedInverter.value!.currentPower * (0.3 + Math.random() * 1.2)).toFixed(1)))

  inverterDetailChart = echarts.init(inverterDetailChartEl.value)
  inverterDetailChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: hours, axisLabel: { rotate: 45, interval: 3 } },
    yAxis: { type: 'value', name: 'Power (kW)' },
    series: [{
      type: 'line',
      data: powerData,
      smooth: true,
      lineStyle: { color: '#f59e0b', width: 3 },
      areaStyle: { opacity: 0.1 }
    }]
  })
}

const updateRealTimeChart = () => {
  initRealtimeChart()
}

const refreshCharts = () => {
  nextTick(() => {
    initRealtimeChart()
    initInverterChart()
    initIrradianceChart()
    initMonthlyChart()
    initBalanceChart()
  })
}

// ==================== Actions ====================
const viewInverterDetail = (inverter: SolarInverter) => {
  selectedInverter.value = inverter
  detailDialogVisible.value = true
  nextTick(() => initInverterDetailChart())
}

const viewAllInverters = () => {
  ElMessage.info('Viewing all inverters')
}

const exportInverterReport = (inverter: SolarInverter | null) => {
  if (!inverter) return
  ElMessage.success(`Exporting report for ${inverter.name}...`)
  setTimeout(() => {
    ElMessage.success('Report generated successfully')
  }, 1500)
}

const exportData = () => {
  ElMessage.success('Exporting solar data...')
  setTimeout(() => {
    ElMessage.success('Data exported successfully')
  }, 1000)
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  tableLoading.value = false
  refreshCharts()
  ElMessage.success('Data refreshed')
}

// 窗口缩放处理
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    const charts = [realtimeChart, inverterChart, irradianceChart, monthlyChart, balanceChart, inverterDetailChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([inverterFilter, arrayFilter, dateRange], () => {
  currentPage.value = 1
})

// ==================== Loading Animation ====================
const startLoading = () => {
  let progress = 0
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 12
      loadingProgress.value = Math.min(progress, 90)
    }
  }, 100)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => refreshCharts())
    }, 500)
  }, 2200)
}

onMounted(() => {
  startLoading()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (resizeTimer) clearTimeout(resizeTimer)
  window.removeEventListener('resize', handleResize)
  const charts = [realtimeChart, inverterChart, irradianceChart, monthlyChart, balanceChart, inverterDetailChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.solar-monitoring-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 24px;
}

* {
  scrollbar-width: thin;
}
*::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
*::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}
*::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

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

.spinner-ring:nth-child(1) { border-top-color: #3b82f6; animation-delay: 0s; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }
.spinner-ring:nth-child(4) { border-left-color: #ec489a; animation-delay: 0.6s; width: 20%; height: 20%; top: 40%; left: 40%; }

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

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.blue { background: #eef2ff; color: #f59e0b; }
.stat-icon.green { background: #dcfce7; color: #22c55e; }
.stat-icon.orange { background: #fef3c7; color: #f59e0b; }
.stat-icon.red { background: #fee2e2; color: #ef4444; }

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
}

.stat-unit {
  font-size: 14px;
  font-weight: normal;
  color: #64748b;
  margin-left: 4px;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

.stat-trend {
  font-size: 11px;
  margin-top: 4px;
}

.stat-trend.up { color: #22c55e; }
.stat-trend.down { color: #ef4444; }

/* Metrics Row */
.metrics-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.metric-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.metric-title {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.metric-unit {
  font-size: 14px;
  font-weight: normal;
  color: #64748b;
}

.metric-trend {
  font-size: 12px;
  margin: 8px 0 4px;
}

.metric-trend.positive { color: #22c55e; }
.metric-trend.negative { color: #ef4444; }

.metric-sub {
  font-size: 11px;
  color: #64748b;
  margin-top: 4px;
}

.metric-target {
  font-size: 11px;
  color: #64748b;
  margin-top: 4px;
}

/* Charts Row */
.charts-row {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  flex: 1;
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chart-card.large {
  flex: 2;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.chart-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.chart-subtitle {
  font-size: 12px;
  color: #64748b;
}

.chart-container {
  height: 300px;
  width: 100%;
}

/* Filter Bar */
.filter-bar {
  background: white;
  border-radius: 16px;
  padding: 14px 20px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.filter-left {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Table Container */
.table-container {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

/* Inverter Detail */
.inverter-detail {
  padding: 8px;
}

.detail-header-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 16px;
}

.detail-stat {
  text-align: center;
}

.detail-stat-value {
  font-size: 28px;
  font-weight: 700;
}

.detail-stat-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

.detail-stat-sub {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 2px;
}

.detail-section {
  margin-bottom: 24px;
}

.section-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 16px;
  padding-left: 10px;
  border-left: 3px solid #f59e0b;
}

.trend-chart {
  height: 280px;
  width: 100%;
}

.metric-good { color: #22c55e; font-weight: 600; }
.metric-warning { color: #f59e0b; font-weight: 600; }
.metric-bad { color: #ef4444; font-weight: 600; }

/* Responsive */
@media (max-width: 1000px) {
  .stats-grid, .metrics-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-row {
    flex-direction: column;
  }
  .detail-header-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid, .metrics-row {
    grid-template-columns: 1fr;
  }
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .filter-left {
    flex-direction: column;
    width: 100%;
  }
  .filter-left .el-input,
  .filter-left .el-select,
  .filter-left .el-date-editor {
    width: 100% !important;
  }
}

/* Element Plus Overrides */
:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
}
:deep(.el-table th.el-table__cell) {
  background-color: #f8fafc !important;
  color: #334155;
}
:deep(.el-table .el-table__row:hover > td.el-table__cell) {
  background-color: #f0f7ff;
}
:deep(.el-button--primary) {
  background: #f59e0b;
  border-color: #f59e0b;
}
:deep(.el-button--primary:hover) {
  background: #d97706;
}
:deep(.el-pagination.is-background .el-pager li.is-active) {
  background-color: #f59e0b;
}
:deep(.el-dialog__body) {
  max-height: 600px;
  overflow-y: auto;
}
:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}
</style>