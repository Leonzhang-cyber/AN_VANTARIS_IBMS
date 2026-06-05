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
          <span class="loading-title">WUE Analytics</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Water Usage Effectiveness Monitoring & Optimization</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="wue-analytics-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><HotWater /></el-icon>
          WUE Analytics
        </h1>
        <div class="page-subtitle">Monitor and optimize water efficiency across data center facilities</div>
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
          <div class="stat-value">{{ stats.currentWUE }}</div>
          <div class="stat-label">Current WUE</div>
          <div class="stat-trend" :class="stats.wueTrend < 0 ? 'down' : 'up'">
            {{ stats.wueTrend < 0 ? '↓' : '↑' }} {{ Math.abs(stats.wueTrend) }} vs last month
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalWater }}<span class="stat-unit">m³</span></div>
          <div class="stat-label">Total Water Consumption</div>
          <div class="stat-trend down">YTD</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.bestWUE }}</div>
          <div class="stat-label">Best WUE</div>
          <div class="stat-trend up">{{ stats.bestDate }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.waterSavings }}<span class="stat-unit">%</span></div>
          <div class="stat-label">Water Savings</div>
          <div class="stat-trend up">vs baseline</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Cooling Water Usage</div>
        <div class="metric-value">{{ metrics.coolingWater }}<span class="stat-unit">m³</span></div>
        <div class="metric-trend" :class="metrics.coolingTrend < 0 ? 'positive' : 'negative'">
          {{ metrics.coolingTrend < 0 ? '↓' : '↑' }} {{ Math.abs(metrics.coolingTrend) }}% vs last month
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Humidification Water</div>
        <div class="metric-value">{{ metrics.humidWater }}<span class="stat-unit">m³</span></div>
        <div class="metric-sub">{{ metrics.humidPercent }}% of total</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Water Reuse Rate</div>
        <div class="metric-value">{{ metrics.reuseRate }}<span class="stat-unit">%</span></div>
        <el-progress :percentage="metrics.reuseRate" :stroke-width="8" :color="metrics.reuseRate > 50 ? '#22c55e' : (metrics.reuseRate > 30 ? '#f59e0b' : '#ef4444')" />
      </div>
      <div class="metric-card">
        <div class="metric-title">Water Intensity</div>
        <div class="metric-value">{{ metrics.waterIntensity }}<span class="stat-unit">L/kWh</span></div>
        <div class="metric-trend positive">↓ {{ metrics.intensityReduction }}% YoY</div>
      </div>
    </div>

    <!-- Charts Row 1 -->
    <div class="charts-row">
      <div class="chart-card large">
        <div class="chart-header">
          <span class="chart-title">WUE Trend</span>
          <span class="chart-subtitle">Monthly water efficiency performance</span>
          <el-select v-model="yearFilter" size="small" style="width: 100px" @change="updateWueTrend">
            <el-option label="2024" value="2024" />
            <el-option label="2023" value="2023" />
            <el-option label="2022" value="2022" />
          </el-select>
        </div>
        <div class="chart-container" ref="wueTrendChartEl"></div>
      </div>
    </div>

    <!-- Charts Row 2 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">WUE by Facility</span>
          <span class="chart-subtitle">Data center comparison</span>
        </div>
        <div class="chart-container" ref="facilityChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Water Consumption by Use</span>
          <span class="chart-subtitle">Breakdown of water usage</span>
        </div>
        <div class="chart-container" ref="breakdownChartEl"></div>
      </div>
    </div>

    <!-- Charts Row 3 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">WUE vs Outdoor Temperature</span>
          <span class="chart-subtitle">Correlation analysis</span>
        </div>
        <div class="chart-container" ref="temperatureChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Monthly Water Consumption</span>
          <span class="chart-subtitle">Usage trend</span>
        </div>
        <div class="chart-container" ref="monthlyWaterChartEl"></div>
      </div>
    </div>

    <!-- Charts Row 4 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Water Source Breakdown</span>
          <span class="chart-subtitle">Supply sources</span>
        </div>
        <div class="chart-container" ref="sourceChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">WUE Improvement</span>
          <span class="chart-subtitle">Year-over-year progress</span>
        </div>
        <div class="chart-container" ref="improvementChartEl"></div>
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
        <el-select v-model="facilityFilter" placeholder="Facility" clearable style="width: 150px">
          <el-option v-for="f in facilities" :key="f" :label="f" :value="f" />
        </el-select>
        <el-select v-model="wueRangeFilter" placeholder="WUE Range" clearable style="width: 140px">
          <el-option label="Excellent (<1.2)" value="excellent" />
          <el-option label="Good (1.2-1.5)" value="good" />
          <el-option label="Average (1.5-1.8)" value="average" />
          <el-option label="Poor (>1.8)" value="poor" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- WUE Data Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Data Center WUE Metrics</span>
        <el-button size="small" @click="viewAllData">View All →</el-button>
      </div>
      <el-table :data="paginatedData" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="facility" label="Facility" min-width="180" />
        <el-table-column prop="wue" label="WUE" width="100">
          <template #default="{ row }">
            <span :class="getWueClass(row.wue)">{{ row.wue.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="totalWater" label="Total Water (m³)" width="140">
          <template #default="{ row }">
            {{ row.totalWater.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="coolingWater" label="Cooling Water (m³)" width="150">
          <template #default="{ row }">
            {{ row.coolingWater.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="humidWater" label="Humidification (m³)" width="150">
          <template #default="{ row }">
            {{ row.humidWater.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="reuseRate" label="Water Reuse %" width="130">
          <template #default="{ row }">
            <el-progress :percentage="row.reuseRate" :stroke-width="8" :color="getReuseColor(row.reuseRate)" :format="() => `${row.reuseRate}%`" />
          </template>
        </el-table-column>
        <el-table-column prop="coolingType" label="Cooling Type" width="130">
          <template #default="{ row }">
            <el-tag :type="getCoolingTagType(row.coolingType)" size="small">{{ row.coolingType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="trend" label="Trend" width="100">
          <template #default="{ row }">
            <el-tag :type="row.trend === 'improving' ? 'success' : (row.trend === 'stable' ? 'info' : 'danger')" size="small">
              {{ row.trend === 'improving' ? '↓ Improving' : (row.trend === 'stable' ? '→ Stable' : '↑ Worsening') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewFacilityDetail(row)">Details</el-button>
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

    <!-- Facility Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedFacility?.facility" width="900px">
      <div v-if="selectedFacility" class="facility-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="WUE">{{ selectedFacility.wue.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="Total Water">{{ selectedFacility.totalWater.toLocaleString() }} m³</el-descriptions-item>
          <el-descriptions-item label="Cooling Water">{{ selectedFacility.coolingWater.toLocaleString() }} m³</el-descriptions-item>
          <el-descriptions-item label="Humidification">{{ selectedFacility.humidWater.toLocaleString() }} m³</el-descriptions-item>
          <el-descriptions-item label="Water Reuse Rate">{{ selectedFacility.reuseRate }}%</el-descriptions-item>
          <el-descriptions-item label="Cooling Type">{{ selectedFacility.coolingType }}</el-descriptions-item>
          <el-descriptions-item label="Cooling Tower Cycles">{{ selectedFacility.coolingCycles }} cycles</el-descriptions-item>
          <el-descriptions-item label="Water Source">{{ selectedFacility.waterSource }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <div class="section-title">Monthly WUE Trend</div>
          <div class="trend-chart" ref="facilityTrendChartEl"></div>
        </div>

        <div class="detail-section">
          <div class="section-title">Water Usage Breakdown</div>
          <div class="trend-chart" ref="waterBreakdownChartEl"></div>
        </div>

        <div class="detail-section">
          <div class="section-title">Water Conservation Recommendations</div>
          <el-alert
              :title="selectedFacility.recommendation.title"
              :type="selectedFacility.recommendation.type"
              :description="selectedFacility.recommendation.description"
              :closable="false"
              show-icon
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="exportFacilityReport(selectedFacility)">Export Report</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  HotWater, Calendar, Timer, Money, Download, Refresh,
  RefreshLeft, TrendCharts
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading WUE analytics data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading water usage data...',
  'Calculating WUE metrics...',
  'Analyzing cooling efficiency...',
  'Preparing conservation insights...',
  'Almost ready...'
]

// ==================== Types ====================
interface WueFacility {
  id: number
  facility: string
  wue: number
  totalWater: number
  coolingWater: number
  humidWater: number
  reuseRate: number
  coolingType: string
  coolingCycles: number
  waterSource: string
  trend: string
  recommendation: {
    title: string
    type: 'success' | 'warning' | 'info' | 'error'
    description: string
  }
}

// ==================== Mock Data ====================
const facilities = ['Data Center A', 'Data Center B', 'Data Center C', 'Data Center D', 'Data Center E', 'Edge Facility 1', 'Edge Facility 2']

const generateWueData = (): WueFacility[] => {
  const facilitiesData: WueFacility[] = [
    { id: 1, facility: 'Data Center A', wue: 1.42, totalWater: 18500, coolingWater: 14800, humidWater: 3700, reuseRate: 35, coolingType: 'Chilled Water', coolingCycles: 4.5, waterSource: 'Municipal', trend: 'improving',
      recommendation: { title: 'Increase Cooling Tower Cycles', type: 'info', description: 'Increase cycles of concentration from 4.5 to 6 to reduce blowdown water consumption.' } },
    { id: 2, facility: 'Data Center B', wue: 1.18, totalWater: 12500, coolingWater: 9500, humidWater: 3000, reuseRate: 52, coolingType: 'Evaporative Cooling', coolingCycles: 6.0, waterSource: 'Reclaimed Water', trend: 'improving',
      recommendation: { title: 'Maintain Best Practices', type: 'success', description: 'Excellent WUE performance. Continue water reuse initiatives and share best practices.' } },
    { id: 3, facility: 'Data Center C', wue: 1.85, totalWater: 28500, coolingWater: 23500, humidWater: 5000, reuseRate: 18, coolingType: 'CRAC Units', coolingCycles: 3.0, waterSource: 'Municipal', trend: 'worsening',
      recommendation: { title: 'Urgent: Cooling System Upgrade', type: 'error', description: 'High WUE due to inefficient cooling. Consider retrofit with high-efficiency units.' } },
    { id: 4, facility: 'Data Center D', wue: 1.55, totalWater: 16500, coolingWater: 13200, humidWater: 3300, reuseRate: 28, coolingType: 'Chilled Water', coolingCycles: 4.0, waterSource: 'Municipal', trend: 'stable',
      recommendation: { title: 'Optimize Cooling Tower Operation', type: 'warning', description: 'Implement automatic blowdown control and conductivity sensors.' } },
    { id: 5, facility: 'Data Center E', wue: 1.25, totalWater: 10800, coolingWater: 8200, humidWater: 2600, reuseRate: 48, coolingType: 'Liquid Cooling', coolingCycles: 5.5, waterSource: 'Municipal + Rainwater', trend: 'improving',
      recommendation: { title: 'Expand Rainwater Harvesting', type: 'info', description: 'Increase rainwater collection capacity to further reduce municipal water usage.' } },
    { id: 6, facility: 'Edge Facility 1', wue: 1.62, totalWater: 4200, coolingWater: 3350, humidWater: 850, reuseRate: 22, coolingType: 'DX Units', coolingCycles: 3.5, waterSource: 'Municipal', trend: 'stable',
      recommendation: { title: 'Air-Cooled Conversion', type: 'warning', description: 'Consider converting to air-cooled systems where water conservation is priority.' } },
    { id: 7, facility: 'Edge Facility 2', wue: 1.48, totalWater: 2800, coolingWater: 2200, humidWater: 600, reuseRate: 30, coolingType: 'AHU', coolingCycles: 4.2, waterSource: 'Municipal', trend: 'improving',
      recommendation: { title: 'Implement Leak Detection', type: 'info', description: 'Install water leak detection system to identify and reduce water loss.' } }
  ]
  return facilitiesData
}

const wueData = ref<WueFacility[]>(generateWueData())

// ==================== State ====================
const dateRange = ref<Date[] | null>(null)
const facilityFilter = ref('')
const wueRangeFilter = ref('')
const yearFilter = ref('2024')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const selectedFacility = ref<WueFacility | null>(null)

// Chart refs
let wueTrendChart: echarts.ECharts | null = null
let facilityChart: echarts.ECharts | null = null
let breakdownChart: echarts.ECharts | null = null
let temperatureChart: echarts.ECharts | null = null
let monthlyWaterChart: echarts.ECharts | null = null
let sourceChart: echarts.ECharts | null = null
let improvementChart: echarts.ECharts | null = null
let facilityTrendChart: echarts.ECharts | null = null
let waterBreakdownChart: echarts.ECharts | null = null

const wueTrendChartEl = ref<HTMLElement | null>(null)
const facilityChartEl = ref<HTMLElement | null>(null)
const breakdownChartEl = ref<HTMLElement | null>(null)
const temperatureChartEl = ref<HTMLElement | null>(null)
const monthlyWaterChartEl = ref<HTMLElement | null>(null)
const sourceChartEl = ref<HTMLElement | null>(null)
const improvementChartEl = ref<HTMLElement | null>(null)
const facilityTrendChartEl = ref<HTMLElement | null>(null)
const waterBreakdownChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  const currentWUE = 1.48
  const totalWater = wueData.value.reduce((sum, d) => sum + d.totalWater, 0)
  const bestWUE = Math.min(...wueData.value.map(d => d.wue))
  const bestFacility = wueData.value.find(d => d.wue === bestWUE)?.facility || 'N/A'
  const waterSavings = 22.5

  return {
    currentWUE: currentWUE.toFixed(2),
    wueTrend: -0.05,
    totalWater: totalWater.toLocaleString(),
    bestWUE: bestWUE.toFixed(2),
    bestDate: bestFacility,
    waterSavings: waterSavings
  }
})

const metrics = computed(() => {
  const totalCooling = wueData.value.reduce((sum, d) => sum + d.coolingWater, 0)
  const totalHumid = wueData.value.reduce((sum, d) => sum + d.humidWater, 0)
  const totalWater = wueData.value.reduce((sum, d) => sum + d.totalWater, 0)
  const avgReuse = (wueData.value.reduce((sum, d) => sum + d.reuseRate, 0) / wueData.value.length).toFixed(1)
  const totalITPower = 48500 // MWh
  const waterIntensity = (totalWater / totalITPower).toFixed(2)

  return {
    coolingWater: totalCooling.toLocaleString(),
    coolingTrend: -3.2,
    humidWater: totalHumid.toLocaleString(),
    humidPercent: ((totalHumid / totalWater) * 100).toFixed(1),
    reuseRate: parseFloat(avgReuse),
    waterIntensity: parseFloat(waterIntensity),
    intensityReduction: 8.5
  }
})

const filteredData = computed(() => {
  let filtered = [...wueData.value]

  if (facilityFilter.value) {
    filtered = filtered.filter(d => d.facility === facilityFilter.value)
  }

  if (wueRangeFilter.value === 'excellent') {
    filtered = filtered.filter(d => d.wue < 1.2)
  } else if (wueRangeFilter.value === 'good') {
    filtered = filtered.filter(d => d.wue >= 1.2 && d.wue < 1.5)
  } else if (wueRangeFilter.value === 'average') {
    filtered = filtered.filter(d => d.wue >= 1.5 && d.wue < 1.8)
  } else if (wueRangeFilter.value === 'poor') {
    filtered = filtered.filter(d => d.wue >= 1.8)
  }

  if (dateRange.value && dateRange.value.length === 2) {
    // Filter logic would go here
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
const getWueClass = (wue: number): string => {
  if (wue < 1.2) return 'metric-good'
  if (wue < 1.5) return 'metric-warning'
  if (wue < 1.8) return 'metric-average'
  return 'metric-bad'
}

const getReuseColor = (reuse: number): string => {
  if (reuse >= 50) return '#22c55e'
  if (reuse >= 25) return '#f59e0b'
  return '#ef4444'
}

const getCoolingTagType = (coolingType: string): string => {
  const map: Record<string, string> = {
    'Chilled Water': 'primary',
    'Evaporative Cooling': 'success',
    'CRAC Units': 'danger',
    'Liquid Cooling': 'success',
    'DX Units': 'warning',
    'AHU': 'info'
  }
  return map[coolingType] || 'info'
}

const resetFilters = () => {
  facilityFilter.value = ''
  wueRangeFilter.value = ''
  dateRange.value = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

// ==================== Chart Functions ====================
const initWueTrendChart = () => {
  if (!wueTrendChartEl.value) return
  if (wueTrendChart) {
    wueTrendChart.dispose()
    wueTrendChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const wue2024 = [1.58, 1.55, 1.52, 1.50, 1.48, 1.47, 1.45, 1.44, 1.42, 1.41, 1.40, 1.38]
  const wue2023 = [1.68, 1.66, 1.64, 1.62, 1.60, 1.58, 1.57, 1.55, 1.54, 1.52, 1.51, 1.50]
  const wue2022 = [1.78, 1.76, 1.74, 1.72, 1.70, 1.68, 1.67, 1.65, 1.64, 1.62, 1.61, 1.60]

  let dataToShow = wue2024
  if (yearFilter.value === '2023') dataToShow = wue2023
  if (yearFilter.value === '2022') dataToShow = wue2022

  wueTrendChart = echarts.init(wueTrendChartEl.value)
  wueTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'WUE (L/kWh)', min: 1.3, max: 1.85 },
    series: [{
      type: 'line',
      data: dataToShow,
      smooth: true,
      lineStyle: { color: '#0ea5e9', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1, color: '#0ea5e9' },
      label: { show: true, position: 'top', formatter: '{c}' }
    }]
  })
}

const initFacilityChart = () => {
  if (!facilityChartEl.value) return
  if (facilityChart) {
    facilityChart.dispose()
    facilityChart = null
  }

  const names = wueData.value.map(d => d.facility)
  const wueValues = wueData.value.map(d => d.wue)

  facilityChart = echarts.init(facilityChartEl.value)
  facilityChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 40, containLabel: true },
    xAxis: { type: 'category', data: names, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: 'WUE (L/kWh)', min: 1.0, max: 2.0 },
    series: [{
      type: 'bar',
      data: wueValues,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value < 1.2) return '#22c55e'
          if (value < 1.5) return '#3b82f6'
          if (value < 1.8) return '#f59e0b'
          return '#ef4444'
        }
      },
      label: { show: true, position: 'top', formatter: (params: any) => params.value.toFixed(2) },
      markLine: {
        data: [{ yAxis: 1.2, name: 'Excellent' }, { yAxis: 1.5, name: 'Good' }, { yAxis: 1.8, name: 'Average' }],
        lineStyle: { type: 'dashed' },
        label: { show: true }
      }
    }]
  })
}

const initBreakdownChart = () => {
  if (!breakdownChartEl.value) return
  if (breakdownChart) {
    breakdownChart.dispose()
    breakdownChart = null
  }

  const totalCooling = wueData.value.reduce((sum, d) => sum + d.coolingWater, 0)
  const totalHumid = wueData.value.reduce((sum, d) => sum + d.humidWater, 0)
  const totalOther = wueData.value.reduce((sum, d) => sum + d.totalWater, 0) - totalCooling - totalHumid

  breakdownChart = echarts.init(breakdownChartEl.value)
  breakdownChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} m³ ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: ['Cooling Tower', 'Humidification', 'Other'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: totalCooling, name: 'Cooling Tower', itemStyle: { color: '#3b82f6' } },
        { value: totalHumid, name: 'Humidification', itemStyle: { color: '#22c55e' } },
        { value: totalOther, name: 'Other', itemStyle: { color: '#f59e0b' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const initTemperatureChart = () => {
  if (!temperatureChartEl.value) return
  if (temperatureChart) {
    temperatureChart.dispose()
    temperatureChart = null
  }

  const temps = [15, 20, 25, 30, 32, 35, 38, 40]
  const wueValues = [1.25, 1.32, 1.42, 1.55, 1.62, 1.72, 1.82, 1.88]

  temperatureChart = echarts.init(temperatureChartEl.value)
  temperatureChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'value', name: 'Outdoor Temperature (°C)' },
    yAxis: { type: 'value', name: 'WUE (L/kWh)', min: 1.1, max: 2.0 },
    series: [{
      type: 'line',
      data: wueValues.map((v, i) => [temps[i], v]),
      smooth: true,
      lineStyle: { color: '#f59e0b', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 }
    }]
  })
}

const initMonthlyWaterChart = () => {
  if (!monthlyWaterChartEl.value) return
  if (monthlyWaterChart) {
    monthlyWaterChart.dispose()
    monthlyWaterChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const waterData = [1850, 1720, 1680, 1650, 1720, 1850, 1950, 2020, 1980, 1820, 1680, 1620]

  monthlyWaterChart = echarts.init(monthlyWaterChartEl.value)
  monthlyWaterChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 60, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Water Consumption (m³)' },
    series: [{
      type: 'bar',
      data: waterData,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#0ea5e9' },
      label: { show: true, position: 'top', formatter: '{c}' }
    }]
  })
}

const initSourceChart = () => {
  if (!sourceChartEl.value) return
  if (sourceChart) {
    sourceChart.dispose()
    sourceChart = null
  }

  sourceChart = echarts.init(sourceChartEl.value)
  sourceChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
    legend: { orient: 'vertical', left: 'left', data: ['Municipal', 'Reclaimed Water', 'Rainwater', 'Groundwater'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: 65, name: 'Municipal', itemStyle: { color: '#3b82f6' } },
        { value: 20, name: 'Reclaimed Water', itemStyle: { color: '#22c55e' } },
        { value: 10, name: 'Rainwater', itemStyle: { color: '#0ea5e9' } },
        { value: 5, name: 'Groundwater', itemStyle: { color: '#f59e0b' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const initImprovementChart = () => {
  if (!improvementChartEl.value) return
  if (improvementChart) {
    improvementChart.dispose()
    improvementChart = null
  }

  const years = ['2020', '2021', '2022', '2023', '2024']
  const wueValues = [1.85, 1.75, 1.65, 1.55, 1.48]

  improvementChart = echarts.init(improvementChartEl.value)
  improvementChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: years },
    yAxis: { type: 'value', name: 'WUE (L/kWh)', min: 1.4, max: 1.95 },
    series: [{
      type: 'line',
      data: wueValues,
      smooth: true,
      lineStyle: { color: '#22c55e', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 },
      label: { show: true, position: 'top', formatter: (params: any) => params.value.toFixed(2) }
    }]
  })
}

const initFacilityTrendChart = () => {
  if (!facilityTrendChartEl.value || !selectedFacility.value) return
  if (facilityTrendChart) {
    facilityTrendChart.dispose()
    facilityTrendChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const wueValues = [1.58, 1.55, 1.52, 1.50, 1.48, 1.47, 1.45, 1.44, 1.42, 1.41, 1.40, 1.38]

  facilityTrendChart = echarts.init(facilityTrendChartEl.value)
  facilityTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'WUE (L/kWh)' },
    series: [{
      type: 'line',
      data: wueValues,
      smooth: true,
      lineStyle: { color: '#3b82f6', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 },
      label: { show: true, position: 'top', formatter: (params: any) => params.value.toFixed(2) }
    }]
  })
}

const initWaterBreakdownChart = () => {
  if (!waterBreakdownChartEl.value || !selectedFacility.value) return
  if (waterBreakdownChart) {
    waterBreakdownChart.dispose()
    waterBreakdownChart = null
  }

  waterBreakdownChart = echarts.init(waterBreakdownChartEl.value)
  waterBreakdownChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} m³ ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: ['Cooling Tower', 'Humidification', 'Sanitary', 'Landscaping'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: selectedFacility.value.coolingWater, name: 'Cooling Tower', itemStyle: { color: '#3b82f6' } },
        { value: selectedFacility.value.humidWater, name: 'Humidification', itemStyle: { color: '#22c55e' } },
        { value: selectedFacility.value.totalWater * 0.08, name: 'Sanitary', itemStyle: { color: '#f59e0b' } },
        { value: selectedFacility.value.totalWater * 0.04, name: 'Landscaping', itemStyle: { color: '#0ea5e9' } }
      ],
      label: { show: true, formatter: '{b}: {c} m³' },
      emphasis: { scale: true }
    }]
  })
}

const updateWueTrend = () => {
  initWueTrendChart()
}

const refreshCharts = () => {
  nextTick(() => {
    initWueTrendChart()
    initFacilityChart()
    initBreakdownChart()
    initTemperatureChart()
    initMonthlyWaterChart()
    initSourceChart()
    initImprovementChart()
  })
}

// ==================== Actions ====================
const viewFacilityDetail = (facility: WueFacility) => {
  selectedFacility.value = facility
  detailDialogVisible.value = true
  nextTick(() => {
    initFacilityTrendChart()
    initWaterBreakdownChart()
  })
}

const viewAllData = () => {
  ElMessage.info('Viewing all facilities')
}

const exportFacilityReport = (facility: WueFacility | null) => {
  if (facility) {
    ElMessage.success(`Exporting report for ${facility.facility}...`)
    setTimeout(() => {
      ElMessage.success('Report generated successfully')
    }, 1500)
  }
}

const exportData = () => {
  ElMessage.success('Exporting WUE analytics data...')
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
    const charts = [wueTrendChart, facilityChart, breakdownChart, temperatureChart, monthlyWaterChart, sourceChart, improvementChart, facilityTrendChart, waterBreakdownChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([facilityFilter, wueRangeFilter, dateRange], () => {
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
  const charts = [wueTrendChart, facilityChart, breakdownChart, temperatureChart, monthlyWaterChart, sourceChart, improvementChart, facilityTrendChart, waterBreakdownChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.wue-analytics-page {
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

.stat-icon.blue { background: #eef2ff; color: #0ea5e9; }
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

/* Facility Detail */
.facility-detail {
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
  border-left: 3px solid #0ea5e9;
}

.trend-chart {
  height: 280px;
  width: 100%;
}

.metric-good { color: #22c55e; font-weight: 600; }
.metric-warning { color: #f59e0b; font-weight: 600; }
.metric-average { color: #f59e0b; font-weight: 600; }
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
  background: #0ea5e9;
  border-color: #0ea5e9;
}
:deep(.el-button--primary:hover) {
  background: #0284c7;
}
:deep(.el-pagination.is-background .el-pager li.is-active) {
  background-color: #0ea5e9;
}
:deep(.el-dialog__body) {
  max-height: 550px;
  overflow-y: auto;
}
:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}
</style>