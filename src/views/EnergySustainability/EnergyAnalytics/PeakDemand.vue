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
          <span class="loading-title">Peak Demand Analysis</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Peak Load Management & Demand Optimization</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="peak-demand-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><TrendCharts /></el-icon>
          Peak Demand Analysis
        </h1>
        <div class="page-subtitle">Monitor and analyze peak demand patterns, forecast trends, and optimize load management</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="optimizeDemand">
          <el-icon><SetUp /></el-icon> Optimize Demand
        </el-button>
        <el-button @click="exportData">
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
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.currentPeak }}<span class="stat-unit">kW</span></div>
          <div class="stat-label">Current Peak Demand</div>
          <div class="stat-trend" :class="stats.peakTrend > 0 ? 'up' : 'down'">
            {{ stats.peakTrend > 0 ? '↑' : '↓' }} {{ Math.abs(stats.peakTrend) }}% vs last month
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.monthlyPeak }}<span class="stat-unit">kW</span></div>
          <div class="stat-label">Monthly Peak</div>
          <div class="stat-trend up">{{ stats.peakDate }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.avgPeakDuration }}<span class="stat-unit">min</span></div>
          <div class="stat-label">Avg Peak Duration</div>
          <div class="stat-trend down">↓ {{ stats.durationReduction }}% vs target</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">${{ stats.demandCharge }}<span class="stat-unit">k</span></div>
          <div class="stat-label">Demand Charges</div>
          <div class="stat-trend up">Based on peak demand</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Load Factor</div>
        <div class="metric-value">{{ metrics.loadFactor }}<span class="metric-unit">%</span></div>
        <el-progress :percentage="metrics.loadFactor" :stroke-width="8" :color="metrics.loadFactor > 70 ? '#22c55e' : (metrics.loadFactor > 50 ? '#f59e0b' : '#ef4444')" />
        <div class="metric-target">Target: >75%</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Peak Reduction Potential</div>
        <div class="metric-value">{{ metrics.peakReduction }}<span class="metric-unit">kW</span></div>
        <div class="metric-trend positive">Potential savings: ${{ metrics.potentialSavings }}K/year</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Peak Occurrence</div>
        <div class="metric-value">{{ metrics.peakTimeOfDay }}</div>
        <div class="metric-sub">Most common peak hour</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Demand Response Capacity</div>
        <div class="metric-value">{{ metrics.drCapacity }}<span class="metric-unit">kW</span></div>
        <div class="metric-trend positive">Available for load shedding</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card large">
        <div class="chart-header">
          <span class="chart-title">Daily Peak Demand Profile</span>
          <span class="chart-subtitle">Last 30 days peak values</span>
          <el-select v-model="periodFilter" size="small" style="width: 100px" @change="updateDailyPeakChart">
            <el-option label="30 Days" value="30" />
            <el-option label="60 Days" value="60" />
            <el-option label="90 Days" value="90" />
          </el-select>
        </div>
        <div class="chart-container" ref="dailyPeakChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Hourly Load Profile</span>
          <span class="chart-subtitle">Average demand by hour</span>
        </div>
        <div class="chart-container" ref="hourlyProfileChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Peak Demand by Season</span>
          <span class="chart-subtitle">Seasonal peak comparison</span>
        </div>
        <div class="chart-container" ref="seasonalChartEl"></div>
      </div>
    </div>

    <!-- Third Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Peak Demand Forecast</span>
          <span class="chart-subtitle">Next 12 months prediction</span>
        </div>
        <div class="chart-container" ref="forecastChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Top Contributing Factors</span>
          <span class="chart-subtitle">Peak demand drivers</span>
        </div>
        <div class="chart-container" ref="factorsChartEl"></div>
      </div>
    </div>

    <!-- Fourth Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Peak vs Baseline Comparison</span>
          <span class="chart-subtitle">Actual vs expected peak</span>
        </div>
        <div class="chart-container" ref="comparisonChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Temperature Impact</span>
          <span class="chart-subtitle">Peak vs temperature correlation</span>
        </div>
        <div class="chart-container" ref="tempImpactChartEl"></div>
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
        <el-select v-model="seasonFilter" placeholder="Season" clearable style="width: 120px">
          <el-option label="Summer" value="summer" />
          <el-option label="Winter" value="winter" />
          <el-option label="Spring" value="spring" />
          <el-option label="Fall" value="fall" />
        </el-select>
        <el-select v-model="dayTypeFilter" placeholder="Day Type" clearable style="width: 130px">
          <el-option label="Weekday" value="weekday" />
          <el-option label="Weekend" value="weekend" />
          <el-option label="Holiday" value="holiday" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Peak Events Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Peak Demand Events</span>
        <el-button size="small" @click="viewAllEvents">View All →</el-button>
      </div>
      <el-table :data="paginatedEvents" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="date" label="Date"  />
        <el-table-column prop="time" label="Time" />
        <el-table-column prop="peakDemand" label="Peak Demand (kW)" >
          <template #default="{ row }">
            <span :class="getPeakClass(row.peakDemand, row.threshold)">{{ row.peakDemand.toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="temperature" label="Temp (°C)"  />
        <el-table-column prop="dayType" label="Day Type">
          <template #default="{ row }">
            <el-tag :type="row.dayType === 'Weekday' ? 'primary' : (row.dayType === 'Weekend' ? 'info' : 'warning')" size="small">
              {{ row.dayType }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="Duration (min)"  />
        <el-table-column prop="exceedance" label="vs Threshold" >
          <template #default="{ row }">
            <span :class="row.exceedance > 0 ? 'metric-bad' : 'metric-good'">
              {{ row.exceedance > 0 ? '+' : '' }}{{ row.exceedance }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="primaryDriver" label="Primary Driver" />
        <el-table-column label="Actions" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewEventDetail(row)">Details</el-button>
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

    <!-- Event Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Peak Event - ${selectedEvent?.date} ${selectedEvent?.time}`" width="800px">
      <div v-if="selectedEvent" class="event-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Date">{{ selectedEvent.date }}</el-descriptions-item>
          <el-descriptions-item label="Time">{{ selectedEvent.time }}</el-descriptions-item>
          <el-descriptions-item label="Peak Demand">{{ selectedEvent.peakDemand.toLocaleString() }} kW</el-descriptions-item>
          <el-descriptions-item label="Temperature">{{ selectedEvent.temperature }} °C</el-descriptions-item>
          <el-descriptions-item label="Day Type">{{ selectedEvent.dayType }}</el-descriptions-item>
          <el-descriptions-item label="Duration">{{ selectedEvent.duration }} minutes</el-descriptions-item>
          <el-descriptions-item label="vs Threshold">
            <span :class="selectedEvent.exceedance > 0 ? 'metric-bad' : 'metric-good'">
              {{ selectedEvent.exceedance > 0 ? '+' : '' }}{{ selectedEvent.exceedance }}%
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="Primary Driver">{{ selectedEvent.primaryDriver }}</el-descriptions-item>
          <el-descriptions-item label="Contributing Factors" :span="2">{{ selectedEvent.contributingFactors.join(', ') }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <div class="section-title">Load Composition During Peak</div>
          <div class="trend-chart" ref="compositionChartEl"></div>
        </div>

        <div class="detail-section">
          <div class="section-title">Recommendations</div>
          <el-alert
              :title="selectedEvent.recommendation.title"
              :type="selectedEvent.recommendation.type"
              :description="selectedEvent.recommendation.description"
              :closable="false"
              show-icon
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="applyRecommendation(selectedEvent)">Apply Recommendation</el-button>
      </template>
    </el-dialog>

    <!-- Optimize Demand Dialog -->
    <el-dialog v-model="optimizeDialogVisible" title="Demand Optimization Strategies" width="600px">
      <div class="optimize-content">
        <h3>Recommended Strategies</h3>
        <el-table :data="optimizationStrategies" border stripe>
          <el-table-column prop="strategy" label="Strategy" min-width="200" />
          <el-table-column prop="impact" label="Impact (kW)"  />
          <el-table-column prop="savings" label="Annual Savings" width="140">
            <template #default="{ row }">
              ${{ row.savings.toLocaleString() }}
            </template>
          </el-table-column>
          <el-table-column prop="priority" label="Priority">
            <template #default="{ row }">
              <el-tag :type="row.priority === 'High' ? 'danger' : (row.priority === 'Medium' ? 'warning' : 'info')" size="small">
                {{ row.priority }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <div class="optimize-summary">
          <h4>Total Potential Impact</h4>
          <div class="summary-stats">
            <div class="summary-stat">
              <span class="summary-label">Peak Reduction</span>
              <span class="summary-value">{{ totalOptimizationImpact }} kW</span>
            </div>
            <div class="summary-stat">
              <span class="summary-label">Annual Savings</span>
              <span class="summary-value">${{ totalOptimizationSavings.toLocaleString() }}</span>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="optimizeDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="implementStrategies">Implement Selected</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  TrendCharts, Calendar, Timer, Money, SetUp, Download, Refresh,
  RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading peak demand data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading peak demand data...',
  'Analyzing load profiles...',
  'Calculating demand metrics...',
  'Generating forecasts...',
  'Almost ready...'
]

// ==================== Types ====================
interface PeakEvent {
  id: number
  date: string
  time: string
  peakDemand: number
  temperature: number
  dayType: string
  duration: number
  exceedance: number
  threshold: number
  primaryDriver: string
  contributingFactors: string[]
  loadComposition: { name: string; value: number }[]
  recommendation: {
    title: string
    type: 'success' | 'warning' | 'info' | 'error'
    description: string
  }
}

// ==================== Mock Data ====================
const generatePeakEvents = (): PeakEvent[] => {
  const events: PeakEvent[] = []
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - 90)

  const drivers = ['HVAC System', 'IT Equipment', 'Lighting', 'Production Equipment', 'Chiller Plant']
  const dayTypes = ['Weekday', 'Weekday', 'Weekday', 'Weekend', 'Holiday']

  for (let i = 0; i < 60; i++) {
    const date = new Date(startDate)
    date.setDate(startDate.getDate() + i)
    const isWeekend = date.getDay() === 0 || date.getDay() === 6
    const dayType = isWeekend ? 'Weekend' : 'Weekday'
    const temp = 20 + Math.sin(i / 30 * Math.PI) * 8 + Math.random() * 5
    const basePeak = 350 + Math.sin(i / 30 * Math.PI) * 80 + Math.random() * 60
    const peakDemand = Math.round(basePeak)
    const threshold = 400
    const exceedance = Math.round((peakDemand - threshold) / threshold * 100)
    const duration = 30 + Math.random() * 60
    const primaryDriver = drivers[Math.floor(Math.random() * drivers.length)]
    const contributingFactors = [
      'High ambient temperature',
      'Post-lunch occupancy peak',
      'Equipment startup sequence'
    ].slice(0, Math.floor(Math.random() * 3) + 1)

    const loadComposition = [
      { name: 'HVAC', value: Math.round(peakDemand * 0.4) },
      { name: 'IT Equipment', value: Math.round(peakDemand * 0.3) },
      { name: 'Lighting', value: Math.round(peakDemand * 0.15) },
      { name: 'Other', value: Math.round(peakDemand * 0.15) }
    ]

    let recommendation = {
      title: '',
      type: 'warning' as const,
      description: ''
    }

    if (primaryDriver === 'HVAC System') {
      recommendation = {
        title: 'HVAC Optimization',
        type: 'warning',
        description: 'Implement temperature setpoint adjustment and pre-cooling strategy to reduce peak demand.'
      }
    } else if (primaryDriver === 'IT Equipment') {
      recommendation = {
        title: 'IT Load Shifting',
        type: 'info',
        description: 'Schedule non-critical IT workloads outside peak hours.'
      }
    } else {
      recommendation = {
        title: 'Load Shedding Opportunity',
        type: 'success',
        description: 'Temporarily reduce non-essential loads during peak periods.'
      }
    }

    events.push({
      id: i + 1,
      date: date.toISOString().slice(0, 10),
      time: `${13 + Math.floor(Math.random() * 5)}:${Math.random() > 0.5 ? '00' : '30'}`,
      peakDemand: peakDemand,
      temperature: parseFloat(temp.toFixed(1)),
      dayType: dayType,
      duration: Math.round(duration),
      exceedance: exceedance,
      threshold: threshold,
      primaryDriver: primaryDriver,
      contributingFactors: contributingFactors,
      loadComposition: loadComposition,
      recommendation: recommendation
    })
  }

  return events.sort((a, b) => b.peakDemand - a.peakDemand)
}

const peakEvents = ref<PeakEvent[]>(generatePeakEvents())

// ==================== State ====================
const dateRange = ref<Date[] | null>(null)
const seasonFilter = ref('')
const dayTypeFilter = ref('')
const periodFilter = ref('30')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const optimizeDialogVisible = ref(false)
const selectedEvent = ref<PeakEvent | null>(null)

// Chart refs
let dailyPeakChart: echarts.ECharts | null = null
let hourlyProfileChart: echarts.ECharts | null = null
let seasonalChart: echarts.ECharts | null = null
let forecastChart: echarts.ECharts | null = null
let factorsChart: echarts.ECharts | null = null
let comparisonChart: echarts.ECharts | null = null
let tempImpactChart: echarts.ECharts | null = null
let compositionChart: echarts.ECharts | null = null

const dailyPeakChartEl = ref<HTMLElement | null>(null)
const hourlyProfileChartEl = ref<HTMLElement | null>(null)
const seasonalChartEl = ref<HTMLElement | null>(null)
const forecastChartEl = ref<HTMLElement | null>(null)
const factorsChartEl = ref<HTMLElement | null>(null)
const comparisonChartEl = ref<HTMLElement | null>(null)
const tempImpactChartEl = ref<HTMLElement | null>(null)
const compositionChartEl = ref<HTMLElement | null>(null)

const optimizationStrategies = ref([
  { strategy: 'HVAC Setpoint Adjustment', impact: 85, savings: 18500, priority: 'High' },
  { strategy: 'Lighting Schedule Optimization', impact: 35, savings: 7500, priority: 'Medium' },
  { strategy: 'IT Workload Shifting', impact: 65, savings: 14200, priority: 'High' },
  { strategy: 'Battery Storage Dispatch', impact: 120, savings: 26200, priority: 'High' },
  { strategy: 'Demand Response Participation', impact: 95, savings: 20800, priority: 'Medium' }
])

// ==================== Computed ====================
const stats = computed(() => {
  const last30Days = peakEvents.value.slice(0, 30)
  const currentPeak = last30Days[0]?.peakDemand || 0
  const monthlyPeak = Math.max(...peakEvents.value.slice(0, 30).map(e => e.peakDemand))
  const peakEvent = peakEvents.value.find(e => e.peakDemand === monthlyPeak)
  const avgPeakDuration = Math.round(peakEvents.value.slice(0, 30).reduce((sum, e) => sum + e.duration, 0) / 30)
  const demandCharge = Math.round(monthlyPeak * 15 / 1000)

  return {
    currentPeak: currentPeak,
    peakTrend: 3.2,
    monthlyPeak: monthlyPeak,
    peakDate: peakEvent?.date || 'N/A',
    avgPeakDuration: avgPeakDuration,
    durationReduction: 8,
    demandCharge: demandCharge
  }
})

const metrics = computed(() => {
  const avgLoad = peakEvents.value.slice(0, 30).reduce((sum, e) => sum + e.peakDemand, 0) / 30
  const loadFactor = Math.round((avgLoad / stats.value.monthlyPeak) * 100)
  const peakReduction = Math.round(stats.value.monthlyPeak * 0.15)
  const potentialSavings = Math.round(peakReduction * 15 * 12 / 1000)
  const peakTimeOfDay = '14:00 - 16:00'
  const drCapacity = Math.round(peakReduction * 1.2)

  return {
    loadFactor: loadFactor,
    peakReduction: peakReduction,
    potentialSavings: potentialSavings,
    peakTimeOfDay: peakTimeOfDay,
    drCapacity: drCapacity
  }
})

const totalOptimizationImpact = computed(() => {
  return optimizationStrategies.value.reduce((sum, s) => sum + s.impact, 0)
})

const totalOptimizationSavings = computed(() => {
  return optimizationStrategies.value.reduce((sum, s) => sum + s.savings, 0)
})

const filteredEvents = computed(() => {
  let filtered = [...peakEvents.value]

  if (seasonFilter.value) {
    // Filter logic would go here based on season
  }

  if (dayTypeFilter.value) {
    filtered = filtered.filter(e => e.dayType.toLowerCase() === dayTypeFilter.value)
  }

  if (dateRange.value && dateRange.value.length === 2) {
    const [start, end] = dateRange.value
    filtered = filtered.filter(e => {
      const eventDate = new Date(e.date)
      return eventDate >= start && eventDate <= end
    })
  }

  return filtered
})

const totalRecords = computed(() => filteredEvents.value.length)

const paginatedEvents = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredEvents.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getPeakClass = (peak: number, threshold: number): string => {
  if (peak > threshold * 1.1) return 'metric-bad'
  if (peak > threshold) return 'metric-warning'
  return 'metric-good'
}

const resetFilters = () => {
  seasonFilter.value = ''
  dayTypeFilter.value = ''
  dateRange.value = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

// ==================== Chart Functions ====================
const initDailyPeakChart = () => {
  if (!dailyPeakChartEl.value) return
  if (dailyPeakChart) {
    dailyPeakChart.dispose()
    dailyPeakChart = null
  }

  const days = parseInt(periodFilter.value)
  const data = peakEvents.value.slice(0, days).reverse()
  const labels = data.map(d => d.date.slice(5))
  const values = data.map(d => d.peakDemand)
  const threshold = 400

  dailyPeakChart = echarts.init(dailyPeakChartEl.value)
  dailyPeakChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: labels, axisLabel: { rotate: 45, interval: Math.floor(days / 15) } },
    yAxis: { type: 'value', name: 'Peak Demand (kW)' },
    series: [
      {
        type: 'line',
        data: values,
        smooth: true,
        lineStyle: { color: '#ef4444', width: 2 },
        symbol: 'circle',
        symbolSize: 6,
        areaStyle: { opacity: 0.1 },
        markLine: {
          data: [{ yAxis: threshold, name: 'Threshold' }],
          lineStyle: { color: '#22c55e', type: 'dashed' },
          label: { formatter: 'Threshold: {c} kW' }
        }
      }
    ]
  })
}

const initHourlyProfileChart = () => {
  if (!hourlyProfileChartEl.value) return
  if (hourlyProfileChart) {
    hourlyProfileChart.dispose()
    hourlyProfileChart = null
  }

  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const weekdayData = [180, 160, 150, 145, 155, 180, 220, 280, 340, 380, 400, 390, 370, 360, 365, 370, 385, 410, 395, 360, 310, 260, 210, 190]
  const weekendData = [150, 140, 135, 130, 135, 150, 170, 200, 230, 250, 260, 255, 250, 245, 250, 255, 265, 280, 270, 250, 220, 190, 170, 160]

  hourlyProfileChart = echarts.init(hourlyProfileChartEl.value)
  hourlyProfileChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Weekday', 'Weekend'], bottom: 0 },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: hours, axisLabel: { rotate: 45, interval: 3 } },
    yAxis: { type: 'value', name: 'Demand (kW)' },
    series: [
      { name: 'Weekday', type: 'line', data: weekdayData, lineStyle: { color: '#3b82f6', width: 2 }, symbol: 'circle', areaStyle: { opacity: 0.1 } },
      { name: 'Weekend', type: 'line', data: weekendData, lineStyle: { color: '#22c55e', width: 2 }, symbol: 'diamond' }
    ]
  })
}

const initSeasonalChart = () => {
  if (!seasonalChartEl.value) return
  if (seasonalChart) {
    seasonalChart.dispose()
    seasonalChart = null
  }

  const seasons = ['Spring', 'Summer', 'Fall', 'Winter']
  const peaks = [420, 485, 410, 395]

  seasonalChart = echarts.init(seasonalChartEl.value)
  seasonalChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: seasons },
    yAxis: { type: 'value', name: 'Peak Demand (kW)' },
    series: [{
      type: 'bar',
      data: peaks,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value > 450) return '#ef4444'
          if (value > 400) return '#f59e0b'
          return '#22c55e'
        }
      },
      label: { show: true, position: 'top', formatter: '{c} kW' }
    }]
  })
}

const initForecastChart = () => {
  if (!forecastChartEl.value) return
  if (forecastChart) {
    forecastChart.dispose()
    forecastChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const forecast = [420, 435, 445, 430, 450, 475, 495, 510, 480, 455, 430, 425]

  forecastChart = echarts.init(forecastChartEl.value)
  forecastChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Peak Demand (kW)' },
    series: [{
      type: 'line',
      data: forecast,
      smooth: true,
      lineStyle: { color: '#3b82f6', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 },
      label: { show: true, position: 'top', formatter: '{c} kW' }
    }]
  })
}

const initFactorsChart = () => {
  if (!factorsChartEl.value) return
  if (factorsChart) {
    factorsChart.dispose()
    factorsChart = null
  }

  const factors = ['HVAC System', 'IT Equipment', 'Lighting', 'Production', 'Other']
  const contributions = [42, 28, 15, 10, 5]

  factorsChart = echarts.init(factorsChartEl.value)
  factorsChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
    legend: { orient: 'vertical', left: 'left', data: factors },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: factors.map((f, i) => ({ name: f, value: contributions[i] })),
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const initComparisonChart = () => {
  if (!comparisonChartEl.value) return
  if (comparisonChart) {
    comparisonChart.dispose()
    comparisonChart = null
  }

  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  const actual = [385, 395, 410, 420, 405, 320, 295]
  const baseline = [360, 365, 370, 375, 370, 310, 290]

  comparisonChart = echarts.init(comparisonChartEl.value)
  comparisonChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Actual Peak', 'Baseline'], bottom: 0 },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: days },
    yAxis: { type: 'value', name: 'Demand (kW)' },
    series: [
      { name: 'Actual Peak', type: 'bar', data: actual, itemStyle: { color: '#ef4444', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top' } },
      { name: 'Baseline', type: 'line', data: baseline, lineStyle: { color: '#3b82f6', width: 2, type: 'dashed' }, symbol: 'diamond' }
    ]
  })
}

const initTempImpactChart = () => {
  if (!tempImpactChartEl.value) return
  if (tempImpactChart) {
    tempImpactChart.dispose()
    tempImpactChart = null
  }

  const temps = [22, 24, 26, 28, 30, 32, 34, 36]
  const peakDemands = [380, 395, 415, 440, 460, 485, 505, 520]

  tempImpactChart = echarts.init(tempImpactChartEl.value)
  tempImpactChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: temps, name: 'Temperature (°C)' },
    yAxis: { type: 'value', name: 'Peak Demand (kW)' },
    series: [{
      type: 'line',
      data: peakDemands,
      smooth: true,
      lineStyle: { color: '#f59e0b', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 },
      label: { show: true, position: 'top', formatter: '{c} kW' }
    }]
  })
}

const initCompositionChart = () => {
  if (!compositionChartEl.value || !selectedEvent.value) return
  if (compositionChart) {
    compositionChart.dispose()
    compositionChart = null
  }

  const data = selectedEvent.value.loadComposition

  compositionChart = echarts.init(compositionChartEl.value)
  compositionChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} kW ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: data.map(d => d.name) },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: data,
      label: { show: true, formatter: '{b}: {c} kW' },
      emphasis: { scale: true }
    }]
  })
}

const updateDailyPeakChart = () => {
  initDailyPeakChart()
}

const refreshCharts = () => {
  nextTick(() => {
    initDailyPeakChart()
    initHourlyProfileChart()
    initSeasonalChart()
    initForecastChart()
    initFactorsChart()
    initComparisonChart()
    initTempImpactChart()
  })
}

// ==================== Actions ====================
const viewEventDetail = (event: PeakEvent) => {
  selectedEvent.value = event
  detailDialogVisible.value = true
  nextTick(() => initCompositionChart())
}

const viewAllEvents = () => {
  ElMessage.info('Viewing all peak events')
}

const optimizeDemand = () => {
  optimizeDialogVisible.value = true
}

const implementStrategies = () => {
  ElMessage.success('Optimization strategies implemented successfully')
  optimizeDialogVisible.value = false
}

const applyRecommendation = (event: PeakEvent | null) => {
  if (event) {
    ElMessage.success(`Recommendation applied for peak event on ${event.date}`)
  }
}

const exportData = () => {
  ElMessage.success('Exporting peak demand data...')
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
    const charts = [dailyPeakChart, hourlyProfileChart, seasonalChart, forecastChart, factorsChart, comparisonChart, tempImpactChart, compositionChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([seasonFilter, dayTypeFilter, dateRange], () => {
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
  const charts = [dailyPeakChart, hourlyProfileChart, seasonalChart, forecastChart, factorsChart, comparisonChart, tempImpactChart, compositionChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.peak-demand-page {
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

/* Loading Screen - same as previous pages */
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

.stat-icon.blue { background: #eef2ff; color: #3b82f6; }
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

/* Event Detail */
.event-detail {
  padding: 8px;
}

.detail-section {
  margin-top: 24px;
}

.section-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 16px;
  padding-left: 10px;
  border-left: 3px solid #3b82f6;
}

.trend-chart {
  height: 280px;
  width: 100%;
}

/* Optimize Dialog */
.optimize-content {
  padding: 8px;
}

.optimize-content h3 {
  margin: 0 0 16px 0;
  color: #1e293b;
}

.optimize-summary {
  margin-top: 20px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
}

.optimize-summary h4 {
  margin: 0 0 12px 0;
  color: #1e293b;
}

.summary-stats {
  display: flex;
  gap: 24px;
}

.summary-stat {
  flex: 1;
}

.summary-label {
  display: block;
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.summary-value {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
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
  .summary-stats {
    flex-direction: column;
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
  background: #3b82f6;
  border-color: #3b82f6;
}
:deep(.el-button--primary:hover) {
  background: #2563eb;
}
:deep(.el-pagination.is-background .el-pager li.is-active) {
  background-color: #3b82f6;
}
:deep(.el-dialog__body) {
  max-height: 600px;
  overflow-y: auto;
}
:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}
</style>