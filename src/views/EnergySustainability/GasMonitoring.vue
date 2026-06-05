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
          <span class="loading-title">Gas Monitoring</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Natural Gas Consumption & Emission Monitoring</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="gas-monitoring-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><HotWater /></el-icon>
          Gas Monitoring
        </h1>
        <div class="page-subtitle">Real-time natural gas consumption, emission tracking, and efficiency analytics</div>
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
          <el-icon><HotWater /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.currentFlow }}<span class="stat-unit">m³/h</span></div>
          <div class="stat-label">Current Flow Rate</div>
          <div class="stat-trend" :class="stats.flowTrend > 0 ? 'up' : 'down'">
            {{ stats.flowTrend > 0 ? '↑' : '↓' }} {{ Math.abs(stats.flowTrend) }}% vs last hour
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.todayConsumption }}<span class="stat-unit">m³</span></div>
          <div class="stat-label">Today's Consumption</div>
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
          <div class="stat-value">{{ stats.monthlyConsumption }}<span class="stat-unit">m³</span></div>
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
          <div class="stat-value">${{ stats.estimatedCost }}<span class="stat-unit">k</span></div>
          <div class="stat-label">Estimated Cost</div>
          <div class="stat-trend down">MTD</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Peak Flow Rate</div>
        <div class="metric-value">{{ metrics.peakFlow }}<span class="metric-unit">m³/h</span></div>
        <div class="metric-sub">Today at {{ metrics.peakTime }}</div>
        <div class="metric-target">Capacity: {{ metrics.capacity }} m³/h</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Gas Efficiency</div>
        <div class="metric-value">{{ metrics.gasEfficiency }}<span class="metric-unit">%</span></div>
        <el-progress :percentage="metrics.gasEfficiency" :stroke-width="8" :color="metrics.gasEfficiency > 85 ? '#22c55e' : (metrics.gasEfficiency > 70 ? '#f59e0b' : '#ef4444')" />
      </div>
      <div class="metric-card">
        <div class="metric-title">CO₂ Emissions</div>
        <div class="metric-value">{{ metrics.co2Emissions }}<span class="metric-unit">tCO₂e</span></div>
        <div class="metric-trend" :class="metrics.emissionsTrend < 0 ? 'positive' : 'negative'">
          {{ metrics.emissionsTrend < 0 ? '↓' : '↑' }} {{ Math.abs(metrics.emissionsTrend) }}% vs last month
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Energy Content</div>
        <div class="metric-value">{{ metrics.energyContent }}<span class="metric-unit">GJ</span></div>
        <div class="metric-sub">Equivalent thermal energy</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card large">
        <div class="chart-header">
          <span class="chart-title">Real-time Gas Flow Rate</span>
          <span class="chart-subtitle">Last 24 hours</span>
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
          <span class="chart-title">Consumption by Zone</span>
          <span class="chart-subtitle">Gas usage distribution</span>
        </div>
        <div class="chart-container" ref="zoneChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Weekly Consumption Pattern</span>
          <span class="chart-subtitle">Day of week comparison</span>
        </div>
        <div class="chart-container" ref="weeklyChartEl"></div>
      </div>
    </div>

    <!-- Third Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Monthly Trend</span>
          <span class="chart-subtitle">Last 12 months</span>
        </div>
        <div class="chart-container" ref="monthlyChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">CO₂ Emissions Trend</span>
          <span class="chart-subtitle">Carbon footprint by month</span>
        </div>
        <div class="chart-container" ref="emissionsChartEl"></div>
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
        <el-select v-model="zoneFilter" placeholder="Zone" clearable style="width: 150px">
          <el-option v-for="z in zones" :key="z" :label="z" :value="z" />
        </el-select>
        <el-select v-model="meterFilter" placeholder="Meter" clearable style="width: 150px">
          <el-option v-for="m in metersList" :key="m" :label="m" :value="m" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Gas Meters Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Gas Meter Readings</span>
        <el-button size="small" @click="viewAllMeters">View All →</el-button>
      </div>
      <el-table :data="paginatedMeters" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="name" label="Meter Name" min-width="180" />
        <el-table-column prop="zone" label="Zone" width="150" />
        <el-table-column prop="currentFlow" label="Current Flow (m³/h)" width="150">
          <template #default="{ row }">
            <span :class="getFlowClass(row.currentFlow, row.capacity)">{{ row.currentFlow }} / {{ row.capacity }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="todayConsumption" label="Today (m³)" width="120" />
        <el-table-column prop="monthlyConsumption" label="Month (m³)" width="130" />
        <el-table-column prop="yearlyConsumption" label="Year (m³)" width="130" />
        <el-table-column prop="co2Emission" label="CO₂ (t)" width="100" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Normal' ? 'success' : (row.status === 'Warning' ? 'warning' : 'danger')" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewMeterDetail(row)">Details</el-button>
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

    <!-- Meter Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedMeter?.name" width="1000px" class="meter-dialog">
      <div v-if="selectedMeter" class="meter-detail">
        <!-- Header Stats -->
        <div class="detail-header-stats">
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedMeter.currentFlow }}<span class="stat-unit">m³/h</span></div>
            <div class="detail-stat-label">Current Flow</div>
            <div class="detail-stat-sub">Capacity: {{ selectedMeter.capacity }} m³/h</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedMeter.todayConsumption }}<span class="stat-unit">m³</span></div>
            <div class="detail-stat-label">Today</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedMeter.monthlyConsumption }}<span class="stat-unit">m³</span></div>
            <div class="detail-stat-label">Month to Date</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedMeter.co2Emission }}<span class="stat-unit">t</span></div>
            <div class="detail-stat-label">CO₂ Emissions</div>
          </div>
        </div>

        <!-- Basic Info -->
        <el-descriptions :column="3" border>
          <el-descriptions-item label="Meter ID">{{ selectedMeter.id }}</el-descriptions-item>
          <el-descriptions-item label="Zone">{{ selectedMeter.zone }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedMeter.location }}</el-descriptions-item>
          <el-descriptions-item label="Type">{{ selectedMeter.type }}</el-descriptions-item>
          <el-descriptions-item label="Manufacturer">{{ selectedMeter.manufacturer }}</el-descriptions-item>
          <el-descriptions-item label="Install Date">{{ selectedMeter.installDate }}</el-descriptions-item>
          <el-descriptions-item label="Last Reading">{{ selectedMeter.lastReading }}</el-descriptions-item>
          <el-descriptions-item label="Next Reading">{{ selectedMeter.nextReading }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="selectedMeter.status === 'Normal' ? 'success' : (selectedMeter.status === 'Warning' ? 'warning' : 'danger')" size="small">
              {{ selectedMeter.status }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <!-- Hourly Flow Chart -->
        <div class="detail-section">
          <div class="section-title">Hourly Gas Flow Rate Trend</div>
          <div class="trend-chart" ref="meterDetailChartEl"></div>
        </div>

        <!-- Alerts -->
        <div class="detail-section" v-if="selectedMeter.alerts.length > 0">
          <div class="section-title">Recent Alerts</div>
          <el-table :data="selectedMeter.alerts" border stripe>
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
        <el-button type="primary" @click="exportMeterReport(selectedMeter)">Export Report</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  HotWater, DataLine, Calendar, Money, Download, Refresh,
  RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading gas monitoring data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading gas meter data...',
  'Fetching real-time flow rates...',
  'Calculating consumption trends...',
  'Analyzing emission data...',
  'Almost ready...'
]

// ==================== Types ====================
interface MeterAlert {
  date: string
  type: string
  description: string
  severity: string
}

interface GasMeter {
  id: string
  name: string
  zone: string
  location: string
  type: string
  manufacturer: string
  currentFlow: number
  capacity: number
  todayConsumption: number
  monthlyConsumption: number
  yearlyConsumption: number
  co2Emission: number
  gasEfficiency: number
  status: string
  installDate: string
  lastReading: string
  nextReading: string
  alerts: MeterAlert[]
}

// ==================== Mock Data ====================
const zones = ['Boiler Room', 'Generator Room', 'Kitchen', 'Heating Plant', 'Process Heating', 'Laboratory']
const metersList = ['Main Gas Meter', 'Boiler 1', 'Boiler 2', 'Generator 1', 'Generator 2', 'Kitchen Supply', 'Process Heater']

const generateMeterData = (): GasMeter[] => {
  const meters: GasMeter[] = []

  for (let i = 1; i <= 18; i++) {
    const zone = zones[Math.floor(Math.random() * zones.length)]
    const capacity = [50, 100, 150, 200, 300, 500][Math.floor(Math.random() * 6)]
    const currentFlow = parseFloat((capacity * (0.2 + Math.random() * 0.6)).toFixed(1))
    const todayConsumption = Math.round(currentFlow * 12 + Math.random() * 200)
    const monthlyConsumption = Math.round(todayConsumption * 30 + Math.random() * 5000)
    const yearlyConsumption = monthlyConsumption * 12
    const co2Emission = parseFloat((monthlyConsumption * 0.00201).toFixed(1))
    const gasEfficiency = Math.min(100, Math.max(60, 75 + Math.random() * 20))

    let status = 'Normal'
    if (currentFlow > capacity * 0.85) status = 'Critical'
    else if (currentFlow > capacity * 0.7) status = 'Warning'

    const alerts: MeterAlert[] = []
    if (currentFlow > capacity * 0.9) {
      alerts.push({
        date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
        type: 'High Flow Alert',
        description: `Gas flow rate exceeded ${Math.round(currentFlow / capacity * 100)}% of capacity`,
        severity: 'High'
      })
    }
    if (gasEfficiency < 70) {
      alerts.push({
        date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
        type: 'Low Efficiency',
        description: `Gas efficiency dropped to ${gasEfficiency}%, below target`,
        severity: 'Medium'
      })
    }

    meters.push({
      id: `GAS-${String(i).padStart(4, '0')}`,
      name: metersList[(i - 1) % metersList.length] + (Math.floor((i - 1) / metersList.length) + 1),
      zone: zone,
      location: `${zone} - Meter ${i}`,
      type: ['Ultrasonic Flow Meter', 'Thermal Mass Meter', 'Diaphragm Meter'][Math.floor(Math.random() * 3)],
      manufacturer: ['Honeywell', 'Siemens', 'Elster', 'Sensus'][Math.floor(Math.random() * 4)],
      currentFlow: currentFlow,
      capacity: capacity,
      todayConsumption: todayConsumption,
      monthlyConsumption: monthlyConsumption,
      yearlyConsumption: yearlyConsumption,
      co2Emission: co2Emission,
      gasEfficiency: gasEfficiency,
      status: status,
      installDate: new Date(Date.now() - Math.random() * 1095 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
      lastReading: new Date().toISOString().slice(0, 10),
      nextReading: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
      alerts: alerts
    })
  }

  return meters
}

const meters = ref<GasMeter[]>(generateMeterData())

// ==================== State ====================
const zoneFilter = ref('')
const meterFilter = ref('')
const dateRange = ref<Date[] | null>(null)
const timeRange = ref('24')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const selectedMeter = ref<GasMeter | null>(null)

// Chart refs
let realtimeChart: echarts.ECharts | null = null
let zoneChart: echarts.ECharts | null = null
let weeklyChart: echarts.ECharts | null = null
let monthlyChart: echarts.ECharts | null = null
let emissionsChart: echarts.ECharts | null = null
let meterDetailChart: echarts.ECharts | null = null

const realtimeChartEl = ref<HTMLElement | null>(null)
const zoneChartEl = ref<HTMLElement | null>(null)
const weeklyChartEl = ref<HTMLElement | null>(null)
const monthlyChartEl = ref<HTMLElement | null>(null)
const emissionsChartEl = ref<HTMLElement | null>(null)
const meterDetailChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  const currentFlow = meters.value.reduce((sum, m) => sum + m.currentFlow, 0)
  const todayConsumption = meters.value.reduce((sum, m) => sum + m.todayConsumption, 0)
  const monthlyConsumption = meters.value.reduce((sum, m) => sum + m.monthlyConsumption, 0)
  const estimatedCost = Math.round(monthlyConsumption * 0.8 / 1000)

  return {
    currentFlow: parseFloat(currentFlow.toFixed(1)),
    flowTrend: 1.8,
    todayConsumption: Math.round(todayConsumption),
    todayTrend: -2.5,
    monthlyConsumption: Math.round(monthlyConsumption),
    monthlyTrend: 3.5,
    estimatedCost: estimatedCost
  }
})

const metrics = computed(() => {
  const peakFlow = Math.max(...meters.value.map(m => m.currentFlow))
  const peakTime = '09:45'
  const capacity = meters.value.reduce((sum, m) => sum + m.capacity, 0)
  const avgGasEfficiency = Math.round(meters.value.reduce((sum, m) => sum + m.gasEfficiency, 0) / meters.value.length)
  const totalCO2 = meters.value.reduce((sum, m) => sum + m.co2Emission, 0)
  const energyContent = Math.round(stats.value.monthlyConsumption * 0.0389)

  return {
    peakFlow: peakFlow,
    peakTime: peakTime,
    capacity: Math.round(capacity),
    gasEfficiency: avgGasEfficiency,
    co2Emissions: parseFloat(totalCO2.toFixed(1)),
    emissionsTrend: 2.8,
    energyContent: energyContent
  }
})

const filteredMeters = computed(() => {
  let filtered = [...meters.value]

  if (zoneFilter.value) {
    filtered = filtered.filter(m => m.zone === zoneFilter.value)
  }

  if (meterFilter.value) {
    filtered = filtered.filter(m => m.name === meterFilter.value)
  }

  if (dateRange.value && dateRange.value.length === 2) {
    // Filter logic would go here for date-based filtering
  }

  return filtered
})

const totalRecords = computed(() => filteredMeters.value.length)

const paginatedMeters = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredMeters.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getFlowClass = (current: number, capacity: number): string => {
  const ratio = current / capacity
  if (ratio <= 0.6) return 'metric-good'
  if (ratio <= 0.8) return 'metric-warning'
  return 'metric-bad'
}

const resetFilters = () => {
  zoneFilter.value = ''
  meterFilter.value = ''
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
  const flowData = labels.map(() => parseFloat((80 + Math.random() * 120).toFixed(1)))

  realtimeChart = echarts.init(realtimeChartEl.value)
  realtimeChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: labels, axisLabel: { rotate: 45, interval: Math.floor(hours / 12) } },
    yAxis: { type: 'value', name: 'Flow Rate (m³/h)' },
    series: [{
      type: 'line',
      data: flowData,
      smooth: true,
      lineStyle: { color: '#f59e0b', width: 3 },
      symbol: 'circle',
      symbolSize: 6,
      areaStyle: { opacity: 0.1, color: '#f59e0b' },
      label: { show: false }
    }]
  })
}

const initZoneChart = () => {
  if (!zoneChartEl.value) return
  if (zoneChart) {
    zoneChart.dispose()
    zoneChart = null
  }

  const zoneMap = new Map<string, number>()
  meters.value.forEach(m => {
    zoneMap.set(m.zone, (zoneMap.get(m.zone) || 0) + m.currentFlow)
  })

  const data = Array.from(zoneMap.entries()).map(([name, value]) => ({ name, value: parseFloat(value.toFixed(1)) }))

  zoneChart = echarts.init(zoneChartEl.value)
  zoneChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}<br/>Flow Rate: {c} m³/h' },
    legend: { orient: 'vertical', left: 'left', data: data.map(d => d.name), type: 'scroll' },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: data,
      label: { show: true, formatter: '{b}: {c} m³/h', fontSize: 10 },
      emphasis: { scale: true }
    }]
  })
}

const initWeeklyChart = () => {
  if (!weeklyChartEl.value) return
  if (weeklyChart) {
    weeklyChart.dispose()
    weeklyChart = null
  }

  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  const consumption = [1250, 1320, 1280, 1350, 1410, 1100, 980]

  weeklyChart = echarts.init(weeklyChartEl.value)
  weeklyChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: days },
    yAxis: { type: 'value', name: 'Consumption (m³)' },
    series: [{
      type: 'bar',
      data: consumption,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const day = params.name
          if (day === 'Sat' || day === 'Sun') return '#22c55e'
          return '#f59e0b'
        }
      },
      label: { show: true, position: 'top', formatter: '{c} m³' }
    }]
  })
}

const initMonthlyChart = () => {
  if (!monthlyChartEl.value) return
  if (monthlyChart) {
    monthlyChart.dispose()
    monthlyChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const consumption = [38500, 36200, 34800, 32500, 29800, 27500, 26800, 27200, 28500, 31200, 34500, 36800]

  monthlyChart = echarts.init(monthlyChartEl.value)
  monthlyChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Consumption (m³)' },
    series: [{
      type: 'line',
      data: consumption,
      smooth: true,
      lineStyle: { color: '#f59e0b', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 },
      label: { show: true, position: 'top', formatter: '{c} m³' }
    }]
  })
}

const initEmissionsChart = () => {
  if (!emissionsChartEl.value) return
  if (emissionsChart) {
    emissionsChart.dispose()
    emissionsChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const emissions = [77.4, 72.8, 70.0, 65.3, 59.9, 55.3, 53.9, 54.7, 57.3, 62.7, 69.3, 74.0]

  emissionsChart = echarts.init(emissionsChartEl.value)
  emissionsChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'CO₂ Emissions (tCO₂e)' },
    series: [{
      type: 'line',
      data: emissions,
      smooth: true,
      lineStyle: { color: '#ef4444', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1, color: '#ef4444' },
      label: { show: true, position: 'top', formatter: '{c} t' }
    }]
  })
}

const initMeterDetailChart = () => {
  if (!meterDetailChartEl.value || !selectedMeter.value) return
  if (meterDetailChart) {
    meterDetailChart.dispose()
    meterDetailChart = null
  }

  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const flowData = hours.map(() => parseFloat((selectedMeter.value!.currentFlow * (0.5 + Math.random() * 1)).toFixed(1)))

  meterDetailChart = echarts.init(meterDetailChartEl.value)
  meterDetailChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: hours, axisLabel: { rotate: 45, interval: 3 } },
    yAxis: { type: 'value', name: 'Flow Rate (m³/h)' },
    series: [{
      type: 'line',
      data: flowData,
      smooth: true,
      lineStyle: { color: '#f59e0b', width: 3 },
      areaStyle: { opacity: 0.1 },
      label: { show: false }
    }]
  })
}

const updateRealTimeChart = () => {
  initRealtimeChart()
}

const refreshCharts = () => {
  nextTick(() => {
    initRealtimeChart()
    initZoneChart()
    initWeeklyChart()
    initMonthlyChart()
    initEmissionsChart()
  })
}

// ==================== Actions ====================
const viewMeterDetail = (meter: GasMeter) => {
  selectedMeter.value = meter
  detailDialogVisible.value = true
  nextTick(() => initMeterDetailChart())
}

const viewAllMeters = () => {
  ElMessage.info('Viewing all gas meters')
}

const exportMeterReport = (meter: GasMeter | null) => {
  if (!meter) return
  ElMessage.success(`Exporting report for ${meter.name}...`)
  setTimeout(() => {
    ElMessage.success('Report generated successfully')
  }, 1500)
}

const exportData = () => {
  ElMessage.success('Exporting gas monitoring data...')
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
    const charts = [realtimeChart, zoneChart, weeklyChart, monthlyChart, emissionsChart, meterDetailChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([zoneFilter, meterFilter, dateRange], () => {
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
  const charts = [realtimeChart, zoneChart, weeklyChart, monthlyChart, emissionsChart, meterDetailChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.gas-monitoring-page {
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

.stat-trend.up { color: #ef4444; }
.stat-trend.down { color: #22c55e; }

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

/* Meter Detail */
.meter-detail {
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