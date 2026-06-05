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
          <span class="loading-title">Consumption Analysis</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Energy Consumption Analytics & Insights</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="consumption-analysis-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><DataAnalysis /></el-icon>
          Consumption Analysis
        </h1>
        <div class="page-subtitle">In-depth energy consumption analytics, trend analysis, and efficiency insights</div>
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
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalConsumption }}<span class="stat-unit">kWh</span></div>
          <div class="stat-label">Total Consumption</div>
          <div class="stat-trend" :class="stats.consumptionTrend > 0 ? 'up' : 'down'">
            {{ stats.consumptionTrend > 0 ? '↑' : '↓' }} {{ Math.abs(stats.consumptionTrend) }}% vs last month
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.peakDemand }}<span class="stat-unit">kW</span></div>
          <div class="stat-label">Peak Demand</div>
          <div class="stat-trend up">{{ stats.peakTime }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.avgDaily }}<span class="stat-unit">kWh</span></div>
          <div class="stat-label">Average Daily</div>
          <div class="stat-trend" :class="stats.dailyTrend > 0 ? 'up' : 'down'">
            {{ stats.dailyTrend > 0 ? '↑' : '↓' }} {{ Math.abs(stats.dailyTrend) }}% vs last month
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
          <div class="stat-trend down">{{ stats.costSavings }}% savings</div>
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
        <div class="metric-title">Consumption Intensity</div>
        <div class="metric-value">{{ metrics.intensity }}<span class="metric-unit">kWh/m²</span></div>
        <div class="metric-trend" :class="metrics.intensityTrend < 0 ? 'positive' : 'negative'">
          {{ metrics.intensityTrend < 0 ? '↓' : '↑' }} {{ Math.abs(metrics.intensityTrend) }}% vs last month
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Peak/Off-Peak Ratio</div>
        <div class="metric-value">{{ metrics.peakOffPeakRatio }}<span class="metric-unit">%</span></div>
        <div class="metric-sub">Peak: {{ metrics.peakPercentage }}%</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Weekend vs Weekday</div>
        <div class="metric-value">{{ metrics.weekendDiff }}<span class="metric-unit">%</span></div>
        <div class="metric-trend positive">Lower on weekends</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card large">
        <div class="chart-header">
          <span class="chart-title">Consumption Trend</span>
          <span class="chart-subtitle">Hourly consumption pattern</span>
          <el-select v-model="timeRange" size="small" style="width: 100px" @change="updateTrendChart">
            <el-option label="24 Hours" value="24" />
            <el-option label="7 Days" value="168" />
            <el-option label="30 Days" value="720" />
          </el-select>
        </div>
        <div class="chart-container" ref="trendChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Consumption by Day Type</span>
          <span class="chart-subtitle">Weekday vs Weekend comparison</span>
        </div>
        <div class="chart-container" ref="dayTypeChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Peak Demand Analysis</span>
          <span class="chart-subtitle">Top 10 peak hours</span>
        </div>
        <div class="chart-container" ref="peakChartEl"></div>
      </div>
    </div>

    <!-- Third Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Consumption by Category</span>
          <span class="chart-subtitle">Load breakdown</span>
        </div>
        <div class="chart-container" ref="categoryChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Temperature Correlation</span>
          <span class="chart-subtitle">Consumption vs Temperature</span>
        </div>
        <div class="chart-container" ref="tempCorrelationChartEl"></div>
      </div>
    </div>

    <!-- Fourth Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Year-over-Year Comparison</span>
          <span class="chart-subtitle">Monthly YoY change</span>
        </div>
        <div class="chart-container" ref="yoyChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Anomaly Detection</span>
          <span class="chart-subtitle">Unusual consumption patterns</span>
        </div>
        <div class="chart-container" ref="anomalyChartEl"></div>
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
        <el-select v-model="categoryFilter" placeholder="Category" clearable style="width: 140px">
          <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
        </el-select>
        <el-select v-model="intervalFilter" placeholder="Interval" clearable style="width: 120px">
          <el-option label="Hourly" value="hourly" />
          <el-option label="Daily" value="daily" />
          <el-option label="Weekly" value="weekly" />
          <el-option label="Monthly" value="monthly" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Consumption Data Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Consumption Data</span>
        <el-button size="small" @click="viewAllData">View All →</el-button>
      </div>
      <el-table :data="paginatedData" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="dateTime" label="Date/Time"  />
        <el-table-column prop="consumption" label="Consumption (kWh)" >
          <template #default="{ row }">
            {{ row.consumption.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="cost" label="Cost ($)" >
          <template #default="{ row }">
            ${{ row.cost.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="temperature" label="Temperature (°C)"  />
        <el-table-column prop="category" label="Category" >
          <template #default="{ row }">
            <el-tag :type="getCategoryTagType(row.category)" size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="anomaly" label="Anomaly" >
          <template #default="{ row }">
            <el-tag :type="row.anomaly ? 'danger' : 'success'" size="small">
              {{ row.anomaly ? 'Detected' : 'Normal' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetail(row)">Details</el-button>
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

    <!-- Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Consumption Detail - ${selectedItem?.dateTime}`" width="800px">
      <div v-if="selectedItem" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Date/Time">{{ selectedItem.dateTime }}</el-descriptions-item>
          <el-descriptions-item label="Category">
            <el-tag :type="getCategoryTagType(selectedItem.category)" size="small">{{ selectedItem.category }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Consumption">{{ selectedItem.consumption.toLocaleString() }} kWh</el-descriptions-item>
          <el-descriptions-item label="Cost">${{ selectedItem.cost.toLocaleString() }}</el-descriptions-item>
          <el-descriptions-item label="Temperature">{{ selectedItem.temperature }} °C</el-descriptions-item>
          <el-descriptions-item label="Anomaly">
            <el-tag :type="selectedItem.anomaly ? 'danger' : 'success'" size="small">
              {{ selectedItem.anomaly ? 'Anomaly Detected' : 'Normal' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Expected Range">{{ selectedItem.expectedMin }} - {{ selectedItem.expectedMax }} kWh</el-descriptions-item>
          <el-descriptions-item label="Deviation">{{ selectedItem.deviation }}%</el-descriptions-item>
        </el-descriptions>

        <div class="detail-section" v-if="selectedItem.anomaly">
          <div class="section-title">Anomaly Explanation</div>
          <el-alert
              :title="selectedItem.anomalyReason"
              type="warning"
              :description="selectedItem.anomalyRecommendation"
              :closable="false"
              show-icon
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="exportDetail(selectedItem)">Export</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  DataAnalysis, DataLine, TrendCharts, Timer, Money, Download, Refresh,
  RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading consumption data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading consumption data...',
  'Analyzing consumption patterns...',
  'Calculating metrics...',
  'Detecting anomalies...',
  'Almost ready...'
]

// ==================== Types ====================
interface ConsumptionItem {
  id: number
  dateTime: string
  consumption: number
  cost: number
  temperature: number
  category: string
  anomaly: boolean
  expectedMin: number
  expectedMax: number
  deviation: number
  anomalyReason: string
  anomalyRecommendation: string
}

// ==================== Mock Data ====================
const categories = ['HVAC', 'Lighting', 'IT Equipment', 'Other']

const generateConsumptionData = (): ConsumptionItem[] => {
  const data: ConsumptionItem[] = []
  let id = 1

  // Generate last 30 days of hourly data (720 records)
  for (let day = 29; day >= 0; day--) {
    const date = new Date()
    date.setDate(date.getDate() - day)
    const isWeekend = date.getDay() === 0 || date.getDay() === 6

    for (let hour = 0; hour < 24; hour++) {
      let baseConsumption = 0

      // HVAC consumption (higher during business hours, influenced by temperature)
      if (hour >= 8 && hour <= 18) {
        baseConsumption += 150 + Math.random() * 50
      } else {
        baseConsumption += 50 + Math.random() * 30
      }

      // Lighting consumption
      if (hour >= 7 && hour <= 19) {
        baseConsumption += 40 + Math.random() * 20
      } else {
        baseConsumption += 10 + Math.random() * 10
      }

      // IT Equipment (relatively constant)
      baseConsumption += 120 + Math.random() * 40

      // Weekend reduction
      if (isWeekend) {
        baseConsumption *= 0.6
      }

      // Temperature effect (higher temp = more cooling)
      const temp = 18 + Math.sin(hour / 24 * Math.PI * 2) * 5 + Math.random() * 5
      if (temp > 25) {
        baseConsumption += (temp - 25) * 10
      } else if (temp < 18) {
        baseConsumption += (18 - temp) * 8
      }

      const consumption = Math.round(baseConsumption)
      const cost = Math.round(consumption * 0.12)

      // Random anomaly (5% chance)
      const isAnomaly = Math.random() < 0.05
      let anomalyConsumption = consumption
      let anomalyReason = ''
      let anomalyRecommendation = ''

      if (isAnomaly) {
        anomalyConsumption = Math.round(consumption * (1.5 + Math.random()))
        anomalyReason = 'Unusual consumption spike detected compared to historical pattern'
        anomalyRecommendation = 'Check for equipment malfunction, schedule maintenance, or verify meter readings'
      }

      const dateTimeStr = `${date.toISOString().slice(0, 10)} ${String(hour).padStart(2, '0')}:00`

      // Determine category
      let category = ''
      if (hour >= 8 && hour <= 18 && !isWeekend) {
        category = categories[Math.floor(Math.random() * categories.length)]
      } else {
        category = categories[Math.floor(Math.random() * 3)]
      }

      data.push({
        id: id++,
        dateTime: dateTimeStr,
        consumption: isAnomaly ? anomalyConsumption : consumption,
        cost: isAnomaly ? Math.round(anomalyConsumption * 0.12) : cost,
        temperature: parseFloat(temp.toFixed(1)),
        category: category,
        anomaly: isAnomaly,
        expectedMin: Math.round(consumption * 0.8),
        expectedMax: Math.round(consumption * 1.2),
        deviation: isAnomaly ? Math.round((anomalyConsumption - consumption) / consumption * 100) : 0,
        anomalyReason: anomalyReason,
        anomalyRecommendation: anomalyRecommendation
      })
    }
  }

  return data
}

const consumptionData = ref<ConsumptionItem[]>(generateConsumptionData())

// ==================== State ====================
const dateRange = ref<Date[] | null>(null)
const categoryFilter = ref('')
const intervalFilter = ref('daily')
const timeRange = ref('168')
const currentPage = ref(1)
const pageSize = ref(15)
const detailDialogVisible = ref(false)
const selectedItem = ref<ConsumptionItem | null>(null)

// Chart refs
let trendChart: echarts.ECharts | null = null
let dayTypeChart: echarts.ECharts | null = null
let peakChart: echarts.ECharts | null = null
let categoryChart: echarts.ECharts | null = null
let tempCorrelationChart: echarts.ECharts | null = null
let yoyChart: echarts.ECharts | null = null
let anomalyChart: echarts.ECharts | null = null

const trendChartEl = ref<HTMLElement | null>(null)
const dayTypeChartEl = ref<HTMLElement | null>(null)
const peakChartEl = ref<HTMLElement | null>(null)
const categoryChartEl = ref<HTMLElement | null>(null)
const tempCorrelationChartEl = ref<HTMLElement | null>(null)
const yoyChartEl = ref<HTMLElement | null>(null)
const anomalyChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  const last30Days = consumptionData.value.slice(-720)
  const totalConsumption = last30Days.reduce((sum, d) => sum + d.consumption, 0)
  const peakDemand = Math.max(...last30Days.map(d => d.consumption))
  const peakHour = last30Days.find(d => d.consumption === peakDemand)?.dateTime || 'N/A'
  const avgDaily = Math.round(totalConsumption / 30)
  const estimatedCost = Math.round(totalConsumption * 0.12 / 1000)
  const costSavings = 8

  return {
    totalConsumption: Math.round(totalConsumption),
    consumptionTrend: 3.2,
    peakDemand: peakDemand,
    peakTime: peakHour.split(' ')[1] + ' ' + peakHour.split(' ')[0],
    avgDaily: avgDaily,
    dailyTrend: -1.5,
    estimatedCost: estimatedCost,
    costSavings: costSavings
  }
})

const metrics = computed(() => {
  const last30Days = consumptionData.value.slice(-720)
  const avgConsumption = last30Days.reduce((sum, d) => sum + d.consumption, 0) / last30Days.length
  const peakConsumption = Math.max(...last30Days.map(d => d.consumption))
  const loadFactor = Math.round((avgConsumption / peakConsumption) * 100)
  const intensity = (stats.value.totalConsumption / 5000).toFixed(1)
  const weekdayAvg = last30Days.filter(d => {
    const hour = parseInt(d.dateTime.split(' ')[1])
    return hour >= 9 && hour <= 17
  }).reduce((sum, d) => sum + d.consumption, 0) / 30
  const weekendAvg = last30Days.filter(d => {
    const hour = parseInt(d.dateTime.split(' ')[1])
    return (hour < 9 || hour > 17)
  }).reduce((sum, d) => sum + d.consumption, 0) / 30
  const weekendDiff = Math.round(((weekendAvg - weekdayAvg) / weekdayAvg) * 100)

  return {
    loadFactor: loadFactor,
    intensity: parseFloat(intensity),
    intensityTrend: -2.3,
    peakOffPeakRatio: 65,
    peakPercentage: 35,
    weekendDiff: Math.abs(weekendDiff)
  }
})

const filteredData = computed(() => {
  let filtered = [...consumptionData.value]

  if (categoryFilter.value) {
    filtered = filtered.filter(d => d.category === categoryFilter.value)
  }

  if (dateRange.value && dateRange.value.length === 2) {
    const [start, end] = dateRange.value
    filtered = filtered.filter(d => {
      const itemDate = new Date(d.dateTime.split(' ')[0])
      return itemDate >= start && itemDate <= end
    })
  }

  return filtered
})

const totalRecords = computed(() => filteredData.value.length)

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getCategoryTagType = (category: string): string => {
  const map: Record<string, string> = { HVAC: 'danger', Lighting: 'warning', 'IT Equipment': 'primary', Other: 'info' }
  return map[category] || 'info'
}

const resetFilters = () => {
  categoryFilter.value = ''
  dateRange.value = null
  intervalFilter.value = 'daily'
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

// ==================== Chart Functions ====================
const initTrendChart = () => {
  if (!trendChartEl.value) return
  if (trendChart) {
    trendChart.dispose()
    trendChart = null
  }

  const hours = timeRange.value === '24' ? 24 : (timeRange.value === '168' ? 168 : 720)
  const data = consumptionData.value.slice(-hours)
  const labels = data.map(d => d.dateTime.split(' ')[1] || d.dateTime.split(' ')[0])
  const values = data.map(d => d.consumption)

  trendChart = echarts.init(trendChartEl.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: labels, axisLabel: { rotate: 45, interval: Math.floor(hours / 24) } },
    yAxis: { type: 'value', name: 'Consumption (kWh)' },
    series: [{
      type: 'line',
      data: values,
      smooth: true,
      lineStyle: { color: '#3b82f6', width: 2 },
      symbol: 'circle',
      symbolSize: 4,
      areaStyle: { opacity: 0.1 },
      markPoint: {
        data: [
          { type: 'max', name: 'Peak' },
          { type: 'min', name: 'Lowest' }
        ]
      }
    }]
  })
}

const initDayTypeChart = () => {
  if (!dayTypeChartEl.value) return
  if (dayTypeChart) {
    dayTypeChart.dispose()
    dayTypeChart = null
  }

  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const weekdayData = hours.map(() => 180 + Math.random() * 100)
  const weekendData = hours.map(() => 100 + Math.random() * 80)

  dayTypeChart = echarts.init(dayTypeChartEl.value)
  dayTypeChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Weekday', 'Weekend'], bottom: 0 },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: hours, axisLabel: { rotate: 45, interval: 3 } },
    yAxis: { type: 'value', name: 'Consumption (kWh)' },
    series: [
      { name: 'Weekday', type: 'line', data: weekdayData, lineStyle: { color: '#3b82f6', width: 2 }, symbol: 'circle' },
      { name: 'Weekend', type: 'line', data: weekendData, lineStyle: { color: '#22c55e', width: 2 }, symbol: 'diamond' }
    ]
  })
}

const initPeakChart = () => {
  if (!peakChartEl.value) return
  if (peakChart) {
    peakChart.dispose()
    peakChart = null
  }

  const topPeaks = [...consumptionData.value]
      .sort((a, b) => b.consumption - a.consumption)
      .slice(0, 10)
  const labels = topPeaks.map(p => p.dateTime)
  const values = topPeaks.map(p => p.consumption)

  peakChart = echarts.init(peakChartEl.value)
  peakChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 40, containLabel: true },
    xAxis: { type: 'category', data: labels, axisLabel: { rotate: 30, fontSize: 10 } },
    yAxis: { type: 'value', name: 'Consumption (kWh)' },
    series: [{
      type: 'bar',
      data: values,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#ef4444' },
      label: { show: true, position: 'top', formatter: '{c} kWh' }
    }]
  })
}

const initCategoryChart = () => {
  if (!categoryChartEl.value) return
  if (categoryChart) {
    categoryChart.dispose()
    categoryChart = null
  }

  const categoryMap = new Map<string, number>()
  consumptionData.value.forEach(d => {
    categoryMap.set(d.category, (categoryMap.get(d.category) || 0) + d.consumption)
  })

  const data = Array.from(categoryMap.entries()).map(([name, value]) => ({ name, value: Math.round(value / 1000) }))

  categoryChart = echarts.init(categoryChartEl.value)
  categoryChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c}K kWh ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: data.map(d => d.name) },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: data,
      label: { show: true, formatter: '{b}: {c}K kWh' },
      emphasis: { scale: true }
    }]
  })
}

const initTempCorrelationChart = () => {
  if (!tempCorrelationChartEl.value) return
  if (tempCorrelationChart) {
    tempCorrelationChart.dispose()
    tempCorrelationChart = null
  }

  const scatterData = consumptionData.value.slice(-500).map(d => [d.temperature, d.consumption])

  tempCorrelationChart = echarts.init(tempCorrelationChartEl.value)
  tempCorrelationChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'value', name: 'Temperature (°C)' },
    yAxis: { type: 'value', name: 'Consumption (kWh)' },
    series: [{
      type: 'scatter',
      data: scatterData,
      symbolSize: 8,
      itemStyle: { color: '#3b82f6' }
    }]
  })
}

const initYoyChart = () => {
  if (!yoyChartEl.value) return
  if (yoyChart) {
    yoyChart.dispose()
    yoyChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const thisYear = [385, 362, 398, 425, 465, 495, 535, 565, 505, 445, 385, 405]
  const lastYear = [395, 375, 405, 435, 475, 505, 545, 575, 515, 455, 395, 415]

  yoyChart = echarts.init(yoyChartEl.value)
  yoyChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['This Year', 'Last Year'], bottom: 0 },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Consumption (kWh)' },
    series: [
      { name: 'This Year', type: 'line', data: thisYear, lineStyle: { color: '#3b82f6', width: 2 }, symbol: 'circle' },
      { name: 'Last Year', type: 'line', data: lastYear, lineStyle: { color: '#94a3b8', width: 2, type: 'dashed' }, symbol: 'diamond' }
    ]
  })
}

const initAnomalyChart = () => {
  if (!anomalyChartEl.value) return
  if (anomalyChart) {
    anomalyChart.dispose()
    anomalyChart = null
  }

  const anomalies = consumptionData.value.filter(d => d.anomaly).slice(-20)
  const labels = anomalies.map(a => a.dateTime)
  const values = anomalies.map(a => a.consumption)
  const expected = anomalies.map(a => (a.expectedMin + a.expectedMax) / 2)

  anomalyChart = echarts.init(anomalyChartEl.value)
  anomalyChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Actual', 'Expected Range'], bottom: 0 },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: labels, axisLabel: { rotate: 45, fontSize: 10 } },
    yAxis: { type: 'value', name: 'Consumption (kWh)' },
    series: [
      { name: 'Actual', type: 'bar', data: values, itemStyle: { color: '#ef4444', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top' } },
      { name: 'Expected Range', type: 'line', data: expected, lineStyle: { color: '#22c55e', width: 2, type: 'dashed' } }
    ]
  })
}

const updateTrendChart = () => {
  initTrendChart()
}

const refreshCharts = () => {
  nextTick(() => {
    initTrendChart()
    initDayTypeChart()
    initPeakChart()
    initCategoryChart()
    initTempCorrelationChart()
    initYoyChart()
    initAnomalyChart()
  })
}

// ==================== Actions ====================
const viewDetail = (item: ConsumptionItem) => {
  selectedItem.value = item
  detailDialogVisible.value = true
}

const viewAllData = () => {
  ElMessage.info('Viewing all consumption data')
}

const exportDetail = (item: ConsumptionItem | null) => {
  if (item) {
    ElMessage.success(`Exporting detail for ${item.dateTime}`)
  }
}

const exportData = () => {
  ElMessage.success('Exporting consumption analysis data...')
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
    const charts = [trendChart, dayTypeChart, peakChart, categoryChart, tempCorrelationChart, yoyChart, anomalyChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([categoryFilter, dateRange, intervalFilter], () => {
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
  const charts = [trendChart, dayTypeChart, peakChart, categoryChart, tempCorrelationChart, yoyChart, anomalyChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.consumption-analysis-page {
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

/* Loading Screen - same as previous */
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

/* Detail Content */
.detail-content {
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