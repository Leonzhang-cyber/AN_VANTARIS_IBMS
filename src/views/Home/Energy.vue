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

  <!-- Energy Overview Page Content -->
  <div v-else class="energy-overview-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>Energy Overview</h1>
        <p class="subtitle">Monitor real-time energy consumption, costs, and efficiency metrics across your facilities</p>
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
      <div class="kpi-card consumption">
        <div class="kpi-icon">
          <el-icon :size="32"><Lightning /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ totalConsumption }}<span class="unit"> kWh</span></div>
          <div class="kpi-label">Total Energy Consumption</div>
        </div>
        <div class="kpi-trend" :class="consumptionTrend >= 0 ? 'negative' : 'positive'">
          <el-icon><CaretTop v-if="consumptionTrend >= 0" /><CaretBottom v-else /></el-icon>
          {{ Math.abs(consumptionTrend) }}%
        </div>
      </div>
      <div class="kpi-card cost">
        <div class="kpi-icon">
          <el-icon :size="32"><Money /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">${{ totalCost }}<span class="unit">k</span></div>
          <div class="kpi-label">Energy Cost</div>
        </div>
        <div class="kpi-trend" :class="costTrend >= 0 ? 'negative' : 'positive'">
          <el-icon><CaretTop v-if="costTrend >= 0" /><CaretBottom v-else /></el-icon>
          {{ Math.abs(costTrend) }}%
        </div>
      </div>
      <div class="kpi-card carbon">
        <div class="kpi-icon">
          <el-icon :size="32"><Cloudy /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ carbonEmissions }}<span class="unit"> tCO₂</span></div>
          <div class="kpi-label">Carbon Emissions</div>
        </div>
        <div class="kpi-trend positive">
          <el-icon><CaretBottom /></el-icon>
          {{ carbonReduction }}%
        </div>
      </div>
      <div class="kpi-card intensity">
        <div class="kpi-icon">
          <el-icon :size="32"><TrendCharts /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ energyIntensity }}<span class="unit"> kWh/m²</span></div>
          <div class="kpi-label">Energy Intensity</div>
        </div>
        <div class="kpi-trend positive">
          <el-icon><CaretBottom /></el-icon>
          {{ intensityReduction }}%
        </div>
      </div>
    </div>

    <!-- Energy Consumption Trend Chart -->
    <div class="chart-card">
      <div class="card-header">
        <h3>Energy Consumption Trend</h3>
        <el-radio-group v-model="trendPeriod" size="small" @change="fetchTrendData">
          <el-radio-button label="day">Daily</el-radio-button>
          <el-radio-button label="week">Weekly</el-radio-button>
          <el-radio-button label="month">Monthly</el-radio-button>
          <el-radio-button label="year">Yearly</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-container" ref="trendChartRef"></div>
    </div>

    <!-- Energy by Building and Source -->
    <div class="two-columns">
      <div class="chart-card">
        <div class="card-header">
          <h3>Energy Consumption by Building</h3>
          <el-select v-model="buildingFilter" placeholder="All Buildings" clearable size="small" style="width: 140px">
            <el-option label="All Buildings" value="all" />
            <el-option label="Building A" value="building-a" />
            <el-option label="Building B" value="building-b" />
            <el-option label="Data Center" value="datacenter" />
          </el-select>
        </div>
        <div class="chart-container" ref="buildingChartRef"></div>
      </div>
      <div class="chart-card">
        <div class="card-header">
          <h3>Energy Mix by Source</h3>
        </div>
        <div class="chart-container" ref="sourceChartRef"></div>
      </div>
    </div>

    <!-- Hourly Consumption Heatmap -->
    <div class="chart-card">
      <div class="card-header">
        <h3>Hourly Consumption Heatmap (kWh)</h3>
        <el-select v-model="heatmapBuilding" placeholder="Select Building" size="small" style="width: 140px">
          <el-option label="All Buildings" value="all" />
          <el-option label="Building A" value="building-a" />
          <el-option label="Building B" value="building-b" />
          <el-option label="Data Center" value="datacenter" />
        </el-select>
      </div>
      <div class="chart-container" ref="heatmapChartRef"></div>
    </div>

    <!-- Monthly Energy Data Table -->
    <div class="table-card">
      <div class="card-header">
        <h3>Monthly Energy Consumption Details</h3>
        <el-input
            v-model="searchText"
            placeholder="Search by building..."
            :prefix-icon="Search"
            style="width: 240px"
            clearable
        />
      </div>
      <el-table :data="paginatedMonthlyData" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="month" label="Month" width="100" sortable />
        <el-table-column prop="building" label="Building" min-width="140">
          <template #default="{ row }">
            <div class="building-cell">
              <el-icon><OfficeBuilding /></el-icon>
              <span>{{ row.building }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="consumption" label="Consumption (kWh)" width="160" align="right" sortable>
          <template #default="{ row }">
            {{ formatNumber(row.consumption) }}
          </template>
        </el-table-column>
        <el-table-column prop="cost" label="Cost ($)" width="130" align="right" sortable>
          <template #default="{ row }">
            ${{ formatNumber(row.cost) }}
          </template>
        </el-table-column>
        <el-table-column prop="carbon" label="Carbon (tCO₂)" width="140" align="right" sortable>
          <template #default="{ row }">
            {{ row.carbon.toFixed(1) }}
          </template>
        </el-table-column>
        <el-table-column prop="intensity" label="Intensity (kWh/m²)" width="150" align="right" sortable>
          <template #default="{ row }">
            <span :class="getIntensityClass(row.intensity)">
              {{ row.intensity.toFixed(1) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="vsPrevious" label="vs Previous" width="110" align="right" sortable>
          <template #default="{ row }">
            <span :class="row.vsPrevious <= 0 ? 'text-success' : 'text-danger'">
              {{ row.vsPrevious > 0 ? '+' : '' }}{{ row.vsPrevious }}%
            </span>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredMonthlyData.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Peak Demand Alerts -->
    <div class="alerts-section">
      <div class="section-header">
        <h2>
          <el-icon><WarningFilled /></el-icon>
          Peak Demand Alerts
        </h2>
        <el-button link type="primary" @click="viewAllAlerts">View All →</el-button>
      </div>
      <div class="alerts-list">
        <div v-for="alert in peakAlerts" :key="alert.id" class="alert-item" :class="alert.severity">
          <div class="alert-icon">
            <el-icon><WarningFilled /></el-icon>
          </div>
          <div class="alert-content">
            <div class="alert-title">{{ alert.title }}</div>
            <div class="alert-desc">{{ alert.description }}</div>
            <div class="alert-time">{{ formatRelativeTime(alert.timestamp) }}</div>
          </div>
          <div class="alert-actions">
            <el-button size="small" type="primary" link @click="acknowledgeAlert(alert)">Acknowledge</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Energy Saving Recommendations -->
    <div class="recommendations-section">
      <div class="section-header">
        <h2>
          <el-icon><EditPen /></el-icon>
          Energy Saving Recommendations
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
              <span><el-icon><Lightning /></el-icon> Potential Savings: {{ rec.savings }} kWh/year</span>
              <span><el-icon><Money /></el-icon> Cost Reduction: ${{ rec.costReduction }}/year</span>
              <span><el-icon><Timer /></el-icon> Payback: {{ rec.payback }}</span>
            </div>
          </div>
          <div class="rec-actions">
            <el-button size="small" type="primary" plain @click="viewRecommendation(rec)">View Details</el-button>
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
  Money,
  Cloudy,
  TrendCharts,
  Search,
  OfficeBuilding,
  WarningFilled,
  EditPen,
  Check,
  Timer,
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
interface MonthlyEnergyData {
  id: number
  month: string
  building: string
  consumption: number
  cost: number
  carbon: number
  intensity: number
  vsPrevious: number
}

interface PeakAlert {
  id: number
  title: string
  description: string
  severity: 'critical' | 'warning' | 'info'
  timestamp: string
}

interface Recommendation {
  id: number
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
  savings: string
  costReduction: number
  payback: string
}

// ==================== State ====================
const dateRange = ref<[Date, Date] | null>(null)
const trendPeriod = ref<'day' | 'week' | 'month' | 'year'>('month')
const buildingFilter = ref('all')
const heatmapBuilding = ref('all')
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const trendChartRef = ref<HTMLElement | null>(null)
const buildingChartRef = ref<HTMLElement | null>(null)
const sourceChartRef = ref<HTMLElement | null>(null)
const heatmapChartRef = ref<HTMLElement | null>(null)
let trendChart: echarts.ECharts | null = null
let buildingChart: echarts.ECharts | null = null
let sourceChart: echarts.ECharts | null = null
let heatmapChart: echarts.ECharts | null = null

// ==================== Mock Data ====================
const monthlyData = ref<MonthlyEnergyData[]>([
  { id: 1, month: '2025-01', building: 'Building A', consumption: 97500, cost: 14625, carbon: 42.5, intensity: 6.5, vsPrevious: -2.5 },
  { id: 2, month: '2025-01', building: 'Building B', consumption: 81600, cost: 12240, carbon: 35.2, intensity: 6.8, vsPrevious: -1.8 },
  { id: 3, month: '2025-01', building: 'Data Center', consumption: 275000, cost: 41250, carbon: 118.5, intensity: 55.0, vsPrevious: 2.5 },
  { id: 4, month: '2025-02', building: 'Building A', consumption: 94500, cost: 14175, carbon: 41.2, intensity: 6.3, vsPrevious: -3.1 },
  { id: 5, month: '2025-02', building: 'Building B', consumption: 79200, cost: 11880, carbon: 34.1, intensity: 6.6, vsPrevious: -2.9 },
  { id: 6, month: '2025-02', building: 'Data Center', consumption: 270000, cost: 40500, carbon: 116.8, intensity: 54.0, vsPrevious: -1.8 },
  { id: 7, month: '2025-03', building: 'Building A', consumption: 93000, cost: 13950, carbon: 40.5, intensity: 6.2, vsPrevious: -1.6 },
  { id: 8, month: '2025-03', building: 'Building B', consumption: 78000, cost: 11700, carbon: 33.6, intensity: 6.5, vsPrevious: -1.5 },
  { id: 9, month: '2025-03', building: 'Data Center', consumption: 268000, cost: 40200, carbon: 115.2, intensity: 53.6, vsPrevious: -0.7 },
  { id: 10, month: '2025-04', building: 'Building A', consumption: 96000, cost: 14400, carbon: 41.8, intensity: 6.4, vsPrevious: 3.2 },
  { id: 11, month: '2025-04', building: 'Building B', consumption: 80400, cost: 12060, carbon: 34.6, intensity: 6.7, vsPrevious: 3.1 },
  { id: 12, month: '2025-04', building: 'Data Center', consumption: 275000, cost: 41250, carbon: 118.5, intensity: 55.0, vsPrevious: 2.6 }
])

const peakAlerts = ref<PeakAlert[]>([
  { id: 1, title: 'Data Center Peak Demand Alert', description: 'Data Center power demand reached 545 kW, approaching capacity limit of 550 kW.', severity: 'warning', timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString() },
  { id: 2, title: 'Building A Peak Hour Detected', description: 'Peak demand of 258 kW recorded at 14:30, 8% above daily average.', severity: 'info', timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString() }
])

const recommendations = ref<Recommendation[]>([
  { id: 1, title: 'LED Lighting Retrofit', description: 'Replace remaining fluorescent fixtures with LED in Building B.', priority: 'high', savings: '85,000', costReduction: 12750, payback: '1.5 years' },
  { id: 2, title: 'HVAC Schedule Optimization', description: 'Adjust AHU operating hours to match occupancy patterns.', priority: 'high', savings: '45,000', costReduction: 6750, payback: '0.5 years' },
  { id: 3, title: 'Data Center Cooling Efficiency', description: 'Implement hot aisle containment to improve cooling efficiency.', priority: 'medium', savings: '65,000', costReduction: 9750, payback: '2.8 years' },
  { id: 4, title: 'Solar Panel Expansion', description: 'Expand existing solar array by 100kW capacity.', priority: 'medium', savings: '52,000', costReduction: 7800, payback: '5.2 years' }
])

// ==================== Computed Values ====================
const totalConsumption = computed(() => 1250000)
const totalCost = computed(() => 187500)
const carbonEmissions = computed(() => 542)
const carbonReduction = computed(() => 8.5)
const energyIntensity = computed(() => 42.5)
const intensityReduction = computed(() => 5.2)
const consumptionTrend = computed(() => 3.5)
const costTrend = computed(() => 2.8)

const filteredMonthlyData = computed(() => {
  let result = [...monthlyData.value]
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(d => d.building.toLowerCase().includes(search))
  }
  if (buildingFilter.value !== 'all') {
    const filterMap: Record<string, string> = {
      'building-a': 'Building A',
      'building-b': 'Building B',
      'datacenter': 'Data Center'
    }
    result = result.filter(d => d.building === filterMap[buildingFilter.value])
  }
  if (dateRange.value && dateRange.value[0] && dateRange.value[1]) {
    const [start, end] = dateRange.value
    result = result.filter(d => {
      const date = new Date(d.month + '-01')
      return date >= start && date <= end
    })
  }
  return result
})

const paginatedMonthlyData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredMonthlyData.value.slice(start, end)
})

// ==================== Helper Functions ====================
const formatNumber = (value: number): string => {
  if (value === undefined || value === null) return '0'
  return value.toLocaleString()
}

const getIntensityClass = (intensity: number) => {
  if (intensity <= 6.5) return 'text-success'
  if (intensity <= 7.0) return 'text-warning'
  return 'text-danger'
}

const formatRelativeTime = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMins = Math.floor((now.getTime() - date.getTime()) / 60000)
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins} min ago`
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)} hours ago`
  return `${Math.floor(diffMins / 1440)} days ago`
}

const dateShortcuts = [
  { text: 'Last 7 Days', value: () => { const end = new Date(); const start = new Date(); start.setDate(start.getDate() - 7); return [start, end] } },
  { text: 'Last 30 Days', value: () => { const end = new Date(); const start = new Date(); start.setDate(start.getDate() - 30); return [start, end] } },
  { text: 'This Year', value: () => { const end = new Date(); const start = new Date(); start.setMonth(0, 1); return [start, end] } }
]

// ==================== Chart Functions ====================
const generateTrendData = () => {
  if (trendPeriod.value === 'day') {
    return {
      labels: ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'],
      consumption: [320, 280, 250, 260, 480, 620, 680, 720, 690, 580, 420, 350]
    }
  }
  if (trendPeriod.value === 'week') {
    return {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      consumption: [28500, 29200, 29800, 30500, 31200, 18500, 16800]
    }
  }
  if (trendPeriod.value === 'month') {
    return {
      labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
      consumption: [185000, 192000, 188000, 178000]
    }
  }
  return {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    consumption: [452000, 432000, 438000, 445000, 468000, 485000, 512000, 528000, 495000, 468000, 442000, 428000]
  }
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)
  const data = generateTrendData()

  trendChart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: (value: number) => value.toLocaleString() + ' kWh' },
    xAxis: { type: 'category', data: data.labels, axisLabel: { rotate: trendPeriod.value === 'month' ? 0 : 0 } },
    yAxis: { type: 'value', name: 'Energy Consumption (kWh)' },
    series: [{
      type: 'line', data: data.consumption, smooth: true, symbol: 'circle',
      lineStyle: { width: 3, color: '#409eff' }, areaStyle: { opacity: 0.1, color: '#409eff' }
    }]
  })
}

const initBuildingChart = () => {
  if (!buildingChartRef.value) return
  if (buildingChart) buildingChart.dispose()

  buildingChart = echarts.init(buildingChartRef.value)

  const buildings = ['Building A', 'Building B', 'Data Center']
  const consumption = [380000, 320000, 1100000]

  buildingChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: (value: number) => value.toLocaleString() + ' kWh' },
    grid: { left: '10%', right: '5%', top: '5%', bottom: '5%', containLabel: true },
    xAxis: { type: 'value', name: 'Consumption (kWh)' },
    yAxis: { type: 'category', data: buildings },
    series: [{
      type: 'bar', data: consumption,
      itemStyle: { borderRadius: [0, 4, 4, 0], color: '#409eff' },
      label: { show: true, position: 'right', formatter: (params: any) => params.value.toLocaleString() + ' kWh' }
    }]
  })
}

const initSourceChart = () => {
  if (!sourceChartRef.value) return
  if (sourceChart) sourceChart.dispose()

  sourceChart = echarts.init(sourceChartRef.value)

  sourceChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} kWh ({d}%)' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      type: 'pie', radius: '55%', center: ['50%', '50%'],
      data: [
        { name: 'Grid Electricity', value: 1520000, itemStyle: { color: '#f56c6c' } },
        { name: 'Solar PV', value: 280000, itemStyle: { color: '#e6a23c' } },
        { name: 'Battery Storage', value: 45000, itemStyle: { color: '#67c23a' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 }
    }]
  })
}

const initHeatmapChart = () => {
  if (!heatmapChartRef.value) return
  if (heatmapChart) heatmapChart.dispose()

  heatmapChart = echarts.init(heatmapChartRef.value)

  const hours = ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00']
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

  const data: [number, number, number][] = []
  for (let i = 0; i < days.length; i++) {
    for (let j = 0; j < hours.length; j++) {
      let value = 20 + Math.random() * 30
      if (j >= 8 && j <= 18) value = 50 + Math.random() * 40
      if (i >= 5) value = value * 0.6
      data.push([j, i, Math.round(value)])
    }
  }

  heatmapChart.setOption({
    tooltip: { position: 'top', formatter: (params: any) => `${days[params.value[1]]} ${hours[params.value[0]]}<br/>Consumption: ${params.value[2]} kWh` },
    grid: { left: '8%', right: '5%', top: '10%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', data: hours, axisLabel: { rotate: 45, interval: 4 } },
    yAxis: { type: 'category', data: days },
    visualMap: { min: 0, max: 100, calculable: true, orient: 'horizontal', left: 'center', bottom: 0, inRange: { color: ['#67c23a', '#409eff', '#e6a23c', '#f56c6c'] } },
    series: [{
      type: 'heatmap', data: data, label: { show: true, fontSize: 10 },
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.5)' } }
    }]
  })
}

// ==================== Actions ====================
const refreshData = async () => {
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  ElMessage.success('Energy data refreshed')
  initTrendChart()
  initBuildingChart()
  initSourceChart()
  initHeatmapChart()
  tableLoading.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting energy overview report...')
}

const fetchTrendData = () => {
  initTrendChart()
}

const handleDateChange = () => {
  currentPage.value = 1
}

const viewAllAlerts = () => {
  ElMessage.info('Viewing all peak demand alerts')
}

const acknowledgeAlert = (alert: PeakAlert) => {
  ElMessage.success(`Alert acknowledged: ${alert.title}`)
  peakAlerts.value = peakAlerts.value.filter(a => a.id !== alert.id)
}

const viewAllRecommendations = () => {
  ElMessage.info('Viewing all recommendations')
}

const viewRecommendation = (rec: Recommendation) => {
  ElMessage.info(`Viewing recommendation: ${rec.title}`)
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Window Resize Handler ====================
const handleResize = () => {
  trendChart?.resize()
  buildingChart?.resize()
  sourceChart?.resize()
  heatmapChart?.resize()
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
        initTrendChart()
        initBuildingChart()
        initSourceChart()
        initHeatmapChart()
      }, 100)
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  buildingChart?.dispose()
  sourceChart?.dispose()
  heatmapChart?.dispose()
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
.energy-overview-page {
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

.kpi-card.consumption .kpi-icon { background: #e8f4ff; color: #409eff; }
.kpi-card.cost .kpi-icon { background: #e8f8f0; color: #67c23a; }
.kpi-card.carbon .kpi-icon { background: #f0e8ff; color: #8b5cf6; }
.kpi-card.intensity .kpi-icon { background: #fff7e8; color: #e6a23c; }

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
  height: 350px;
  width: 100%;
}

.two-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

/* Table Styles */
.building-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

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

.pagination-wrapper {
  padding: 20px 0 0;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
  margin-top: 16px;
}

/* Alerts Section */
.alerts-section {
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  margin-bottom: 24px;
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

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alert-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 14px 16px;
  background: #fafafa;
  border-radius: 12px;
  transition: all 0.2s;
}

.alert-item:hover {
  background: #f5f7fa;
}

.alert-item.critical .alert-icon { color: #f56c6c; }
.alert-item.warning .alert-icon { color: #e6a23c; }
.alert-item.info .alert-icon { color: #409eff; }

.alert-icon .el-icon {
  font-size: 20px;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-weight: 600;
  color: #1f2f3d;
  margin-bottom: 4px;
}

.alert-desc {
  font-size: 13px;
  color: #606266;
  margin-bottom: 6px;
}

.alert-time {
  font-size: 11px;
  color: #c0c4cc;
}

.alert-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.alert-item:hover .alert-actions {
  opacity: 1;
}

/* Recommendations Section */
.recommendations-section {
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
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