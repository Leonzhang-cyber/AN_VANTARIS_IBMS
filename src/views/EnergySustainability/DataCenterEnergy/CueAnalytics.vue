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
          <span class="loading-title">CUE Analytics</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Carbon Usage Effectiveness Monitoring & Optimization</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="cue-analytics-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><TrendCharts /></el-icon>
          CUE Analytics
        </h1>
        <div class="page-subtitle">Monitor and optimize carbon emissions across data center facilities</div>
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
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.currentCUE }}</div>
          <div class="stat-label">Current CUE</div>
          <div class="stat-trend" :class="stats.cueTrend < 0 ? 'down' : 'up'">
            {{ stats.cueTrend < 0 ? '↓' : '↑' }} {{ Math.abs(stats.cueTrend) }} vs last month
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalEmissions }}<span class="stat-unit">tCO₂e</span></div>
          <div class="stat-label">Total Carbon Emissions</div>
          <div class="stat-trend down">YTD</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.bestCUE }}</div>
          <div class="stat-label">Best CUE</div>
          <div class="stat-trend up">{{ stats.bestDate }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.carbonReduction }}<span class="stat-unit">%</span></div>
          <div class="stat-label">Carbon Reduction</div>
          <div class="stat-trend up">vs baseline</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">IT Carbon Intensity</div>
        <div class="metric-value">{{ metrics.itCarbonIntensity }}<span class="metric-unit">kgCO₂/kWh</span></div>
        <div class="metric-trend" :class="metrics.itTrend < 0 ? 'positive' : 'negative'">
          {{ metrics.itTrend < 0 ? '↓' : '↑' }} {{ Math.abs(metrics.itTrend) }}% vs last month
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Grid Carbon Factor</div>
        <div class="metric-value">{{ metrics.gridFactor }}<span class="metric-unit">kgCO₂/kWh</span></div>
        <div class="metric-sub">{{ metrics.renewablePercentage }}% renewable</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Scope 2 Emissions</div>
        <div class="metric-value">{{ metrics.scope2Emissions }}<span class="metric-unit">tCO₂e</span></div>
        <div class="metric-trend positive">↓ {{ metrics.scope2Reduction }}% YoY</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Renewable Energy Ratio</div>
        <div class="metric-value">{{ metrics.renewableRatio }}<span class="metric-unit">%</span></div>
        <el-progress :percentage="metrics.renewableRatio" :stroke-width="8" :color="metrics.renewableRatio > 50 ? '#22c55e' : (metrics.renewableRatio > 30 ? '#f59e0b' : '#ef4444')" />
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card large">
        <div class="chart-header">
          <span class="chart-title">CUE Trend</span>
          <span class="chart-subtitle">Monthly carbon efficiency performance</span>
          <el-select v-model="yearFilter" size="small" style="width: 100px" @change="updateCueTrend">
            <el-option label="2024" value="2024" />
            <el-option label="2023" value="2023" />
            <el-option label="2022" value="2022" />
          </el-select>
        </div>
        <div class="chart-container" ref="cueTrendChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">CUE by Facility</span>
          <span class="chart-subtitle">Data center comparison</span>
        </div>
        <div class="chart-container" ref="facilityChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Emissions Breakdown</span>
          <span class="chart-subtitle">Scope 1 vs Scope 2</span>
        </div>
        <div class="chart-container" ref="breakdownChartEl"></div>
      </div>
    </div>

    <!-- Third Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">CUE vs IT Load</span>
          <span class="chart-subtitle">Correlation analysis</span>
        </div>
        <div class="chart-container" ref="loadChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Monthly Emissions Trend</span>
          <span class="chart-subtitle">Scope 1 & 2 emissions</span>
        </div>
        <div class="chart-container" ref="emissionsTrendChartEl"></div>
      </div>
    </div>

    <!-- Fourth Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Renewable Energy Mix</span>
          <span class="chart-subtitle">Green energy sources</span>
        </div>
        <div class="chart-container" ref="renewableChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">CUE Improvement</span>
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
        <el-select v-model="cueRangeFilter" placeholder="CUE Range" clearable style="width: 140px">
          <el-option label="Excellent (<0.2)" value="excellent" />
          <el-option label="Good (0.2-0.3)" value="good" />
          <el-option label="Average (0.3-0.4)" value="average" />
          <el-option label="Poor (>0.4)" value="poor" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- CUE Data Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Data Center CUE Metrics</span>
        <el-button size="small" @click="viewAllData">View All →</el-button>
      </div>
      <el-table :data="paginatedData" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="facility" label="Facility" min-width="180" />
        <el-table-column prop="cue" label="CUE" width="100">
          <template #default="{ row }">
            <span :class="getCueClass(row.cue)">{{ row.cue.toFixed(3) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="totalEmissions" label="Emissions (tCO₂e)" width="150">
          <template #default="{ row }">
            {{ row.totalEmissions.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="itCarbon" label="IT Carbon (tCO₂e)" width="140">
          <template #default="{ row }">
            {{ row.itCarbon.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="facilityCarbon" label="Facility Carbon (tCO₂e)" width="160">
          <template #default="{ row }">
            {{ row.facilityCarbon.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="renewablePercentage" label="Renewable %" width="130">
          <template #default="{ row }">
            <el-progress :percentage="row.renewablePercentage" :stroke-width="8" :color="getRenewableColor(row.renewablePercentage)" :format="() => `${row.renewablePercentage}%`" />
          </template>
        </el-table-column>
        <el-table-column prop="gridFactor" label="Grid Factor" width="120">
          <template #default="{ row }">
            {{ row.gridFactor }} kgCO₂/kWh
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
          <el-descriptions-item label="CUE">{{ selectedFacility.cue.toFixed(3) }}</el-descriptions-item>
          <el-descriptions-item label="Total Emissions">{{ selectedFacility.totalEmissions.toLocaleString() }} tCO₂e</el-descriptions-item>
          <el-descriptions-item label="IT Carbon">{{ selectedFacility.itCarbon.toLocaleString() }} tCO₂e</el-descriptions-item>
          <el-descriptions-item label="Facility Carbon">{{ selectedFacility.facilityCarbon.toLocaleString() }} tCO₂e</el-descriptions-item>
          <el-descriptions-item label="Renewable Energy">{{ selectedFacility.renewablePercentage }}%</el-descriptions-item>
          <el-descriptions-item label="Grid Emission Factor">{{ selectedFacility.gridFactor }} kgCO₂/kWh</el-descriptions-item>
          <el-descriptions-item label="PPA/Offsets">{{ selectedFacility.ppaAmount }} MWh/year</el-descriptions-item>
          <el-descriptions-item label="Renewable Source">{{ selectedFacility.renewableSource }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <div class="section-title">Monthly CUE Trend</div>
          <div class="trend-chart" ref="facilityTrendChartEl"></div>
        </div>

        <div class="detail-section">
          <div class="section-title">Emissions Breakdown by Source</div>
          <div class="trend-chart" ref="emissionsBreakdownChartEl"></div>
        </div>

        <div class="detail-section">
          <div class="section-title">Decarbonization Recommendations</div>
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
  TrendCharts, Calendar, Timer, Money, Download, Refresh,
  RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading CUE analytics data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading carbon data...',
  'Calculating CUE metrics...',
  'Analyzing grid factors...',
  'Preparing decarbonization insights...',
  'Almost ready...'
]

// ==================== Types ====================
interface CueFacility {
  id: number
  facility: string
  cue: number
  totalEmissions: number
  itCarbon: number
  facilityCarbon: number
  renewablePercentage: number
  gridFactor: number
  trend: string
  ppaAmount: number
  renewableSource: string
  recommendation: {
    title: string
    type: 'success' | 'warning' | 'info' | 'error'
    description: string
  }
}

// ==================== Mock Data ====================
const facilities = ['Data Center A', 'Data Center B', 'Data Center C', 'Data Center D', 'Data Center E', 'Edge Facility 1', 'Edge Facility 2']

const generateCueData = (): CueFacility[] => {
  const facilitiesData: CueFacility[] = [
    { id: 1, facility: 'Data Center A', cue: 0.285, totalEmissions: 28500, itCarbon: 22000, facilityCarbon: 6500, renewablePercentage: 35, gridFactor: 0.42, trend: 'improving', ppaAmount: 5000, renewableSource: 'Solar PPA',
      recommendation: { title: 'Increase Renewable Procurement', type: 'warning', description: 'Currently 35% renewable. Target 50% by 2026 through additional PPAs or RECs.' } },
    { id: 2, facility: 'Data Center B', cue: 0.245, totalEmissions: 18500, itCarbon: 14800, facilityCarbon: 3700, renewablePercentage: 52, gridFactor: 0.38, trend: 'improving', ppaAmount: 8000, renewableSource: 'Wind + Solar',
      recommendation: { title: 'Maintain Leadership', type: 'success', description: 'Excellent CUE performance. Focus on remaining Scope 2 reduction opportunities.' } },
    { id: 3, facility: 'Data Center C', cue: 0.385, totalEmissions: 42500, itCarbon: 30500, facilityCarbon: 12000, renewablePercentage: 18, gridFactor: 0.52, trend: 'worsening', ppaAmount: 2000, renewableSource: 'RECs only',
      recommendation: { title: 'Urgent Action Required', type: 'error', description: 'High grid carbon intensity. Prioritize renewable energy procurement and energy efficiency.' } },
    { id: 4, facility: 'Data Center D', cue: 0.312, totalEmissions: 21500, itCarbon: 16400, facilityCarbon: 5100, renewablePercentage: 28, gridFactor: 0.45, trend: 'stable', ppaAmount: 3500, renewableSource: 'Hydro',
      recommendation: { title: 'Explore On-site Generation', type: 'info', description: 'Consider rooftop solar installation to increase renewable percentage and reduce CUE.' } },
    { id: 5, facility: 'Data Center E', cue: 0.218, totalEmissions: 22500, itCarbon: 18400, facilityCarbon: 4100, renewablePercentage: 68, gridFactor: 0.35, trend: 'improving', ppaAmount: 12000, renewableSource: 'Wind PPA + Solar',
      recommendation: { title: 'Industry Leading', type: 'success', description: 'CUE in top quartile. Share best practices across other facilities.' } },
    { id: 6, facility: 'Edge Facility 1', cue: 0.358, totalEmissions: 4200, itCarbon: 3100, facilityCarbon: 1100, renewablePercentage: 15, gridFactor: 0.48, trend: 'stable', ppaAmount: 500, renewableSource: 'Grid mix',
      recommendation: { title: 'Local Renewable Options', type: 'warning', description: 'Evaluate community solar or local renewable tariffs to reduce carbon footprint.' } },
    { id: 7, facility: 'Edge Facility 2', cue: 0.335, totalEmissions: 2900, itCarbon: 2150, facilityCarbon: 750, renewablePercentage: 22, gridFactor: 0.44, trend: 'improving', ppaAmount: 800, renewableSource: 'RECs',
      recommendation: { title: 'Energy Efficiency First', type: 'info', description: 'Focus on IT efficiency before additional renewable procurement.' } }
  ]
  return facilitiesData
}

const cueData = ref<CueFacility[]>(generateCueData())

// ==================== State ====================
const dateRange = ref<Date[] | null>(null)
const facilityFilter = ref('')
const cueRangeFilter = ref('')
const yearFilter = ref('2024')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const selectedFacility = ref<CueFacility | null>(null)

// Chart refs
let cueTrendChart: echarts.ECharts | null = null
let facilityChart: echarts.ECharts | null = null
let breakdownChart: echarts.ECharts | null = null
let loadChart: echarts.ECharts | null = null
let emissionsTrendChart: echarts.ECharts | null = null
let renewableChart: echarts.ECharts | null = null
let improvementChart: echarts.ECharts | null = null
let facilityTrendChart: echarts.ECharts | null = null
let emissionsBreakdownChart: echarts.ECharts | null = null

const cueTrendChartEl = ref<HTMLElement | null>(null)
const facilityChartEl = ref<HTMLElement | null>(null)
const breakdownChartEl = ref<HTMLElement | null>(null)
const loadChartEl = ref<HTMLElement | null>(null)
const emissionsTrendChartEl = ref<HTMLElement | null>(null)
const renewableChartEl = ref<HTMLElement | null>(null)
const improvementChartEl = ref<HTMLElement | null>(null)
const facilityTrendChartEl = ref<HTMLElement | null>(null)
const emissionsBreakdownChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  const currentCUE = 0.298
  const totalEmissions = cueData.value.reduce((sum, d) => sum + d.totalEmissions, 0)
  const bestCUE = Math.min(...cueData.value.map(d => d.cue))
  const bestFacility = cueData.value.find(d => d.cue === bestCUE)?.facility || 'N/A'
  const carbonReduction = 18.5

  return {
    currentCUE: currentCUE.toFixed(3),
    cueTrend: -0.015,
    totalEmissions: totalEmissions.toLocaleString(),
    bestCUE: bestCUE.toFixed(3),
    bestDate: bestFacility,
    carbonReduction: carbonReduction
  }
})

const metrics = computed(() => {
  const totalITCarbon = cueData.value.reduce((sum, d) => sum + d.itCarbon, 0)
  const totalITPower = 48.5 // MW
  const itCarbonIntensity = (totalITCarbon / totalITPower / 8760 * 1000).toFixed(2)
  const avgGridFactor = (cueData.value.reduce((sum, d) => sum + d.gridFactor, 0) / cueData.value.length).toFixed(2)
  const avgRenewable = (cueData.value.reduce((sum, d) => sum + d.renewablePercentage, 0) / cueData.value.length).toFixed(1)
  const totalScope2 = cueData.value.reduce((sum, d) => sum + d.facilityCarbon, 0)

  return {
    itCarbonIntensity: parseFloat(itCarbonIntensity),
    itTrend: -3.2,
    gridFactor: parseFloat(avgGridFactor),
    renewablePercentage: parseFloat(avgRenewable),
    scope2Emissions: totalScope2.toLocaleString(),
    scope2Reduction: 12,
    renewableRatio: parseFloat(avgRenewable)
  }
})

const filteredData = computed(() => {
  let filtered = [...cueData.value]

  if (facilityFilter.value) {
    filtered = filtered.filter(d => d.facility === facilityFilter.value)
  }

  if (cueRangeFilter.value === 'excellent') {
    filtered = filtered.filter(d => d.cue < 0.2)
  } else if (cueRangeFilter.value === 'good') {
    filtered = filtered.filter(d => d.cue >= 0.2 && d.cue < 0.3)
  } else if (cueRangeFilter.value === 'average') {
    filtered = filtered.filter(d => d.cue >= 0.3 && d.cue < 0.4)
  } else if (cueRangeFilter.value === 'poor') {
    filtered = filtered.filter(d => d.cue >= 0.4)
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
const getCueClass = (cue: number): string => {
  if (cue < 0.2) return 'metric-good'
  if (cue < 0.3) return 'metric-warning'
  return 'metric-bad'
}

const getRenewableColor = (percentage: number): string => {
  if (percentage >= 50) return '#22c55e'
  if (percentage >= 25) return '#f59e0b'
  return '#ef4444'
}

const resetFilters = () => {
  facilityFilter.value = ''
  cueRangeFilter.value = ''
  dateRange.value = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

// ==================== Chart Functions ====================
const initCueTrendChart = () => {
  if (!cueTrendChartEl.value) return
  if (cueTrendChart) {
    cueTrendChart.dispose()
    cueTrendChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const cue2024 = [0.325, 0.318, 0.312, 0.308, 0.302, 0.298, 0.295, 0.291, 0.288, 0.284, 0.281, 0.278]
  const cue2023 = [0.348, 0.342, 0.338, 0.335, 0.331, 0.328, 0.325, 0.322, 0.319, 0.316, 0.313, 0.310]
  const cue2022 = [0.372, 0.368, 0.365, 0.362, 0.359, 0.356, 0.353, 0.350, 0.348, 0.345, 0.342, 0.340]

  let dataToShow = cue2024
  if (yearFilter.value === '2023') dataToShow = cue2023
  if (yearFilter.value === '2022') dataToShow = cue2022

  cueTrendChart = echarts.init(cueTrendChartEl.value)
  cueTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'CUE', min: 0.25, max: 0.38 },
    series: [{
      type: 'line',
      data: dataToShow,
      smooth: true,
      lineStyle: { color: '#22c55e', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1, color: '#22c55e' },
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

  const names = cueData.value.map(d => d.facility)
  const cueValues = cueData.value.map(d => d.cue)

  facilityChart = echarts.init(facilityChartEl.value)
  facilityChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 40, containLabel: true },
    xAxis: { type: 'category', data: names, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: 'CUE', min: 0.15, max: 0.45 },
    series: [{
      type: 'bar',
      data: cueValues,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value < 0.2) return '#22c55e'
          if (value < 0.3) return '#3b82f6'
          if (value < 0.4) return '#f59e0b'
          return '#ef4444'
        }
      },
      label: { show: true, position: 'top', formatter: (params: any) => params.value.toFixed(3) },
      markLine: {
        data: [{ yAxis: 0.2, name: 'Excellent' }, { yAxis: 0.3, name: 'Good' }, { yAxis: 0.4, name: 'Average' }],
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

  const totalIT = cueData.value.reduce((sum, d) => sum + d.itCarbon, 0)
  const totalFacility = cueData.value.reduce((sum, d) => sum + d.facilityCarbon, 0)

  breakdownChart = echarts.init(breakdownChartEl.value)
  breakdownChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} tCO₂e ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: ['IT Equipment (Scope 2)', 'Facility Operations (Scope 2)'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: totalIT, name: 'IT Equipment (Scope 2)', itemStyle: { color: '#3b82f6' } },
        { value: totalFacility, name: 'Facility Operations (Scope 2)', itemStyle: { color: '#f59e0b' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const initLoadChart = () => {
  if (!loadChartEl.value) return
  if (loadChart) {
    loadChart.dispose()
    loadChart = null
  }

  const loadPercent = [20, 30, 40, 50, 60, 70, 80, 90, 100]
  const cueValues = [0.385, 0.352, 0.328, 0.312, 0.298, 0.288, 0.282, 0.278, 0.276]

  loadChart = echarts.init(loadChartEl.value)
  loadChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: loadPercent, name: 'IT Load (%)' },
    yAxis: { type: 'value', name: 'CUE', min: 0.25, max: 0.4 },
    series: [{
      type: 'line',
      data: cueValues,
      smooth: true,
      lineStyle: { color: '#f59e0b', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 },
      label: { show: true, position: 'top', formatter: (params: any) => params.value.toFixed(3) }
    }]
  })
}

const initEmissionsTrendChart = () => {
  if (!emissionsTrendChartEl.value) return
  if (emissionsTrendChart) {
    emissionsTrendChart.dispose()
    emissionsTrendChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const scope2Data = [2850, 2750, 2680, 2620, 2550, 2480, 2420, 2380, 2320, 2280, 2220, 2180]

  emissionsTrendChart = echarts.init(emissionsTrendChartEl.value)
  emissionsTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 60, right: 30, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Emissions (tCO₂e)' },
    series: [{
      type: 'line',
      data: scope2Data,
      smooth: true,
      lineStyle: { color: '#ef4444', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 },
      label: { show: true, position: 'top', formatter: '{c}' }
    }]
  })
}

const initRenewableChart = () => {
  if (!renewableChartEl.value) return
  if (renewableChart) {
    renewableChart.dispose()
    renewableChart = null
  }

  renewableChart = echarts.init(renewableChartEl.value)
  renewableChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
    legend: { orient: 'vertical', left: 'left', data: ['Solar PPA', 'Wind PPA', 'Hydro', 'RECs', 'Grid Mix'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: 35, name: 'Solar PPA', itemStyle: { color: '#f59e0b' } },
        { value: 28, name: 'Wind PPA', itemStyle: { color: '#3b82f6' } },
        { value: 12, name: 'Hydro', itemStyle: { color: '#22c55e' } },
        { value: 10, name: 'RECs', itemStyle: { color: '#8b5cf6' } },
        { value: 15, name: 'Grid Mix', itemStyle: { color: '#94a3b8' } }
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
  const cueValues = [0.385, 0.362, 0.340, 0.318, 0.298]

  improvementChart = echarts.init(improvementChartEl.value)
  improvementChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: years },
    yAxis: { type: 'value', name: 'CUE', min: 0.25, max: 0.42 },
    series: [{
      type: 'line',
      data: cueValues,
      smooth: true,
      lineStyle: { color: '#22c55e', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 },
      label: { show: true, position: 'top', formatter: (params: any) => params.value.toFixed(3) }
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
  const cueValues = [0.325, 0.318, 0.312, 0.308, 0.302, 0.298, 0.295, 0.291, 0.288, 0.284, 0.281, 0.278]

  facilityTrendChart = echarts.init(facilityTrendChartEl.value)
  facilityTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'CUE', min: 0.25, max: 0.35 },
    series: [{
      type: 'line',
      data: cueValues,
      smooth: true,
      lineStyle: { color: '#3b82f6', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 },
      label: { show: true, position: 'top', formatter: (params: any) => params.value.toFixed(3) }
    }]
  })
}

const initEmissionsBreakdownChart = () => {
  if (!emissionsBreakdownChartEl.value || !selectedFacility.value) return
  if (emissionsBreakdownChart) {
    emissionsBreakdownChart.dispose()
    emissionsBreakdownChart = null
  }

  emissionsBreakdownChart = echarts.init(emissionsBreakdownChartEl.value)
  emissionsBreakdownChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} tCO₂e ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: ['IT Equipment', 'Cooling', 'Power Distribution', 'Lighting'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: selectedFacility.value.itCarbon * 0.7, name: 'IT Equipment', itemStyle: { color: '#3b82f6' } },
        { value: selectedFacility.value.facilityCarbon * 0.6, name: 'Cooling', itemStyle: { color: '#22c55e' } },
        { value: selectedFacility.value.facilityCarbon * 0.25, name: 'Power Distribution', itemStyle: { color: '#f59e0b' } },
        { value: selectedFacility.value.facilityCarbon * 0.15, name: 'Lighting', itemStyle: { color: '#8b5cf6' } }
      ],
      label: { show: true, formatter: '{b}: {c} t' },
      emphasis: { scale: true }
    }]
  })
}

const updateCueTrend = () => {
  initCueTrendChart()
}

const refreshCharts = () => {
  nextTick(() => {
    initCueTrendChart()
    initFacilityChart()
    initBreakdownChart()
    initLoadChart()
    initEmissionsTrendChart()
    initRenewableChart()
    initImprovementChart()
  })
}

// ==================== Actions ====================
const viewFacilityDetail = (facility: CueFacility) => {
  selectedFacility.value = facility
  detailDialogVisible.value = true
  nextTick(() => {
    initFacilityTrendChart()
    initEmissionsBreakdownChart()
  })
}

const viewAllData = () => {
  ElMessage.info('Viewing all facilities')
}

const exportFacilityReport = (facility: CueFacility | null) => {
  if (facility) {
    ElMessage.success(`Exporting report for ${facility.facility}...`)
    setTimeout(() => {
      ElMessage.success('Report generated successfully')
    }, 1500)
  }
}

const exportData = () => {
  ElMessage.success('Exporting CUE analytics data...')
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
    const charts = [cueTrendChart, facilityChart, breakdownChart, loadChart, emissionsTrendChart, renewableChart, improvementChart, facilityTrendChart, emissionsBreakdownChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([facilityFilter, cueRangeFilter, dateRange], () => {
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
  const charts = [cueTrendChart, facilityChart, breakdownChart, loadChart, emissionsTrendChart, renewableChart, improvementChart, facilityTrendChart, emissionsBreakdownChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.cue-analytics-page {
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
  border-left: 3px solid #3b82f6;
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