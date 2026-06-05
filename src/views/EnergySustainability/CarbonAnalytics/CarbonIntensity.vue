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
          <span class="loading-title">Carbon Intensity</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Carbon Efficiency Metrics & Performance Tracking</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="carbon-intensity-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><TrendCharts /></el-icon>
          Carbon Intensity
        </h1>
        <div class="page-subtitle">Track carbon efficiency metrics across operations and value chain</div>
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
          <div class="stat-value">{{ stats.revenueIntensity }}<span class="stat-unit">kgCO₂/$M</span></div>
          <div class="stat-label">Revenue Intensity</div>
          <div class="stat-trend" :class="stats.revenueTrend < 0 ? 'down' : 'up'">
            {{ stats.revenueTrend < 0 ? '↓' : '↑' }} {{ Math.abs(stats.revenueTrend) }}% vs last year
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><OfficeBuilding /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.floorAreaIntensity }}<span class="stat-unit">kgCO₂/m²</span></div>
          <div class="stat-label">Floor Area Intensity</div>
          <div class="stat-trend" :class="stats.areaTrend < 0 ? 'down' : 'up'">
            {{ stats.areaTrend < 0 ? '↓' : '↑' }} {{ Math.abs(stats.areaTrend) }}% vs last year
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.perEmployeeIntensity }}<span class="stat-unit">tCO₂/emp</span></div>
          <div class="stat-label">Per Employee</div>
          <div class="stat-trend" :class="stats.employeeTrend < 0 ? 'down' : 'up'">
            {{ stats.employeeTrend < 0 ? '↓' : '↑' }} {{ Math.abs(stats.employeeTrend) }}% vs last year
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><DataBoard /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.energyIntensity }}<span class="stat-unit">kWh/m²</span></div>
          <div class="stat-label">Energy Intensity</div>
          <div class="stat-trend" :class="stats.energyTrend < 0 ? 'down' : 'up'">
            {{ stats.energyTrend < 0 ? '↓' : '↑' }} {{ Math.abs(stats.energyTrend) }}% vs last year
          </div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Scope 1 Intensity</div>
        <div class="metric-value">{{ metrics.scope1Intensity }}<span class="metric-unit">kgCO₂/m²</span></div>
        <div class="metric-sub">{{ metrics.scope1Percent }}% of total intensity</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Scope 2 Intensity</div>
        <div class="metric-value">{{ metrics.scope2Intensity }}<span class="metric-unit">kgCO₂/m²</span></div>
        <div class="metric-sub">{{ metrics.scope2Percent }}% of total intensity</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Scope 3 Intensity</div>
        <div class="metric-value">{{ metrics.scope3Intensity }}<span class="metric-unit">kgCO₂/m²</span></div>
        <div class="metric-sub">{{ metrics.scope3Percent }}% of total intensity</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Global Benchmark</div>
        <div class="metric-value">{{ metrics.globalRank }}<span class="metric-unit">/100</span></div>
        <div class="metric-trend positive">Top {{ metrics.percentile }}%</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card large">
        <div class="chart-header">
          <span class="chart-title">Carbon Intensity Trend</span>
          <span class="chart-subtitle">Revenue vs Floor Area vs Employee</span>
        </div>
        <div class="chart-container" ref="trendChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Intensity by Scope</span>
          <span class="chart-subtitle">Contribution breakdown</span>
        </div>
        <div class="chart-container" ref="scopeChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Intensity by Facility</span>
          <span class="chart-subtitle">Floor area intensity</span>
        </div>
        <div class="chart-container" ref="facilityChartEl"></div>
      </div>
    </div>

    <!-- Third Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Intensity vs Peers</span>
          <span class="chart-subtitle">Industry comparison</span>
        </div>
        <div class="chart-container" ref="peersChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Monthly Intensity by Scope</span>
          <span class="chart-subtitle">2024 monthly trend</span>
        </div>
        <div class="chart-container" ref="monthlyChartEl"></div>
      </div>
    </div>

    <!-- Fourth Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Intensity vs Target</span>
          <span class="chart-subtitle">Progress toward 2030 goals</span>
        </div>
        <div class="chart-container" ref="targetChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Intensity Drivers</span>
          <span class="chart-subtitle">Key influencing factors</span>
        </div>
        <div class="chart-container" ref="driversChartEl"></div>
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
        <el-select v-model="metricTypeFilter" placeholder="Metric Type" clearable style="width: 150px">
          <el-option label="Revenue Intensity" value="revenue" />
          <el-option label="Floor Area Intensity" value="area" />
          <el-option label="Per Employee" value="employee" />
        </el-select>
        <el-select v-model="facilityFilter" placeholder="Facility" clearable style="width: 150px">
          <el-option v-for="f in facilities" :key="f" :label="f" :value="f" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Intensity Data Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Intensity Metrics by Facility</span>
        <el-button size="small" @click="viewAllData">View All →</el-button>
      </div>
      <el-table :data="paginatedData" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="facility" label="Facility" min-width="180" />
        <el-table-column prop="floorArea" label="Floor Area (m²)" width="140">
          <template #default="{ row }">
            {{ row.floorArea.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="revenue" label="Revenue ($M)" width="130">
          <template #default="{ row }">
            ${{ row.revenue.toLocaleString() }}M
          </template>
        </el-table-column>
        <el-table-column prop="employees" label="Employees" width="110">
          <template #default="{ row }">
            {{ row.employees.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="carbonFootprint" label="Carbon (tCO₂e)" width="140">
          <template #default="{ row }">
            {{ row.carbonFootprint.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="intensityArea" label="Area Intensity" width="140">
          <template #default="{ row }">
            <span :class="getIntensityClass(row.intensityArea, 50)">
              {{ row.intensityArea }} kgCO₂/m²
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="intensityRevenue" label="Revenue Intensity" width="150">
          <template #default="{ row }">
            <span :class="getIntensityClass(row.intensityRevenue, 200)">
              {{ row.intensityRevenue }} kgCO₂/$M
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="intensityEmployee" label="Employee Intensity" width="150">
          <template #default="{ row }">
            <span :class="getIntensityClass(row.intensityEmployee, 50)">
              {{ row.intensityEmployee }} tCO₂/emp
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="rating" label="Rating" width="100">
          <template #default="{ row }">
            <el-tag :type="getRatingTagType(row.rating)" size="small">{{ row.rating }}</el-tag>
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
    <el-dialog v-model="detailDialogVisible" :title="selectedFacility?.facility" width="850px">
      <div v-if="selectedFacility" class="facility-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Floor Area">{{ selectedFacility.floorArea.toLocaleString() }} m²</el-descriptions-item>
          <el-descriptions-item label="Revenue">${{ selectedFacility.revenue.toLocaleString() }}M</el-descriptions-item>
          <el-descriptions-item label="Employees">{{ selectedFacility.employees.toLocaleString() }}</el-descriptions-item>
          <el-descriptions-item label="Total Carbon">{{ selectedFacility.carbonFootprint.toLocaleString() }} tCO₂e</el-descriptions-item>
          <el-descriptions-item label="Area Intensity">{{ selectedFacility.intensityArea }} kgCO₂/m²</el-descriptions-item>
          <el-descriptions-item label="Revenue Intensity">{{ selectedFacility.intensityRevenue }} kgCO₂/$M</el-descriptions-item>
          <el-descriptions-item label="Employee Intensity">{{ selectedFacility.intensityEmployee }} tCO₂/emp</el-descriptions-item>
          <el-descriptions-item label="Rating">
            <el-tag :type="getRatingTagType(selectedFacility.rating)" size="small">{{ selectedFacility.rating }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <div class="section-title">Monthly Intensity Trend</div>
          <div class="trend-chart" ref="facilityTrendChartEl"></div>
        </div>

        <div class="detail-section">
          <div class="section-title">Intensity Breakdown by Scope</div>
          <div class="trend-chart" ref="scopeBreakdownChartEl"></div>
        </div>

        <div class="detail-section">
          <div class="section-title">Recommendations</div>
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
  TrendCharts, OfficeBuilding, User, DataBoard, Download, Refresh,
  RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading carbon intensity data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading intensity metrics...',
  'Calculating ratios...',
  'Comparing benchmarks...',
  'Preparing analysis...',
  'Almost ready...'
]

// ==================== Types ====================
interface FacilityIntensity {
  id: number
  facility: string
  floorArea: number
  revenue: number
  employees: number
  carbonFootprint: number
  intensityArea: number
  intensityRevenue: number
  intensityEmployee: number
  rating: string
  recommendation: {
    title: string
    type: 'success' | 'warning' | 'info' | 'error'
    description: string
  }
}

// ==================== Mock Data ====================
const facilities = ['Data Center A', 'Data Center B', 'Office HQ', 'Manufacturing Plant', 'R&D Center', 'Warehouse', 'Retail Store']

const generateIntensityData = (): FacilityIntensity[] => {
  const intensities: FacilityIntensity[] = []

  const facilityData = [
    { facility: 'Data Center A', floorArea: 5000, revenue: 120, employees: 80, carbon: 2850 },
    { facility: 'Data Center B', floorArea: 3500, revenue: 85, employees: 55, carbon: 1950 },
    { facility: 'Office HQ', floorArea: 8000, revenue: 200, employees: 450, carbon: 1850 },
    { facility: 'Manufacturing Plant', floorArea: 15000, revenue: 350, employees: 320, carbon: 5200 },
    { facility: 'R&D Center', floorArea: 3000, revenue: 65, employees: 120, carbon: 580 },
    { facility: 'Warehouse', floorArea: 10000, revenue: 45, employees: 35, carbon: 420 },
    { facility: 'Retail Store', floorArea: 2000, revenue: 25, employees: 15, carbon: 180 }
  ]

  for (let i = 0; i < facilityData.length; i++) {
    const data = facilityData[i]
    const intensityArea = parseFloat((data.carbon / data.floorArea).toFixed(1))
    const intensityRevenue = parseFloat((data.carbon / data.revenue).toFixed(1))
    const intensityEmployee = parseFloat((data.carbon / data.employees).toFixed(1))

    let rating = ''
    let recommendation = { title: '', type: 'info' as const, description: '' }

    if (intensityArea < 0.3) {
      rating = 'Excellent'
      recommendation = {
        title: 'Industry Leading Performance',
        type: 'success',
        description: 'This facility has excellent carbon intensity metrics. Continue best practices and share learnings.'
      }
    } else if (intensityArea < 0.5) {
      rating = 'Good'
      recommendation = {
        title: 'Good Performance',
        type: 'info',
        description: 'Performance is above average. Identify opportunities for further reduction.'
      }
    } else if (intensityArea < 0.7) {
      rating = 'Average'
      recommendation = {
        title: 'Opportunity for Improvement',
        type: 'warning',
        description: 'Intensity metrics are at industry average. Focus on energy efficiency initiatives.'
      }
    } else {
      rating = 'Needs Improvement'
      recommendation = {
        title: 'Action Required',
        type: 'error',
        description: 'Carbon intensity is above industry average. Prioritize reduction strategies.'
      }
    }

    intensities.push({
      id: i + 1,
      facility: data.facility,
      floorArea: data.floorArea,
      revenue: data.revenue,
      employees: data.employees,
      carbonFootprint: data.carbon,
      intensityArea: intensityArea,
      intensityRevenue: intensityRevenue,
      intensityEmployee: intensityEmployee,
      rating: rating,
      recommendation: recommendation
    })
  }

  return intensities
}

const intensityData = ref<FacilityIntensity[]>(generateIntensityData())

// ==================== State ====================
const dateRange = ref<Date[] | null>(null)
const metricTypeFilter = ref('')
const facilityFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const selectedFacility = ref<FacilityIntensity | null>(null)

// Chart refs
let trendChart: echarts.ECharts | null = null
let scopeChart: echarts.ECharts | null = null
let facilityChart: echarts.ECharts | null = null
let peersChart: echarts.ECharts | null = null
let monthlyChart: echarts.ECharts | null = null
let targetChart: echarts.ECharts | null = null
let driversChart: echarts.ECharts | null = null
let facilityTrendChart: echarts.ECharts | null = null
let scopeBreakdownChart: echarts.ECharts | null = null

const trendChartEl = ref<HTMLElement | null>(null)
const scopeChartEl = ref<HTMLElement | null>(null)
const facilityChartEl = ref<HTMLElement | null>(null)
const peersChartEl = ref<HTMLElement | null>(null)
const monthlyChartEl = ref<HTMLElement | null>(null)
const targetChartEl = ref<HTMLElement | null>(null)
const driversChartEl = ref<HTMLElement | null>(null)
const facilityTrendChartEl = ref<HTMLElement | null>(null)
const scopeBreakdownChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  const totalCarbon = intensityData.value.reduce((sum, d) => sum + d.carbonFootprint, 0)
  const totalRevenue = intensityData.value.reduce((sum, d) => sum + d.revenue, 0)
  const totalArea = intensityData.value.reduce((sum, d) => sum + d.floorArea, 0)
  const totalEmployees = intensityData.value.reduce((sum, d) => sum + d.employees, 0)

  const revenueIntensity = totalCarbon / totalRevenue
  const floorAreaIntensity = totalCarbon / totalArea
  const perEmployeeIntensity = totalCarbon / totalEmployees
  const energyIntensity = 185

  return {
    revenueIntensity: Math.round(revenueIntensity),
    revenueTrend: -5.2,
    floorAreaIntensity: parseFloat(floorAreaIntensity.toFixed(1)),
    areaTrend: -4.8,
    perEmployeeIntensity: parseFloat(perEmployeeIntensity.toFixed(1)),
    employeeTrend: -6.5,
    energyIntensity: energyIntensity,
    energyTrend: -3.2
  }
})

const metrics = computed(() => {
  const totalCarbon = intensityData.value.reduce((sum, d) => sum + d.carbonFootprint, 0)
  const totalArea = intensityData.value.reduce((sum, d) => sum + d.floorArea, 0)
  const totalIntensity = totalCarbon / totalArea

  // Mock scope breakdown
  const scope1Intensity = totalIntensity * 0.35
  const scope2Intensity = totalIntensity * 0.45
  const scope3Intensity = totalIntensity * 0.20

  return {
    scope1Intensity: parseFloat(scope1Intensity.toFixed(1)),
    scope1Percent: 35,
    scope2Intensity: parseFloat(scope2Intensity.toFixed(1)),
    scope2Percent: 45,
    scope3Intensity: parseFloat(scope3Intensity.toFixed(1)),
    scope3Percent: 20,
    globalRank: 42,
    percentile: 85
  }
})

const filteredData = computed(() => {
  let filtered = [...intensityData.value]

  if (facilityFilter.value) {
    filtered = filtered.filter(d => d.facility === facilityFilter.value)
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
const getIntensityClass = (intensity: number, threshold: number): string => {
  if (intensity < threshold * 0.6) return 'metric-good'
  if (intensity < threshold) return 'metric-warning'
  return 'metric-bad'
}

const getRatingTagType = (rating: string): string => {
  const map: Record<string, string> = {
    'Excellent': 'success',
    'Good': 'primary',
    'Average': 'warning',
    'Needs Improvement': 'danger'
  }
  return map[rating] || 'info'
}

const resetFilters = () => {
  facilityFilter.value = ''
  metricTypeFilter.value = ''
  dateRange.value = null
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

  const years = ['2020', '2021', '2022', '2023', '2024']
  const revenueData = [95, 88, 82, 76, 72]
  const areaData = [0.68, 0.64, 0.60, 0.56, 0.52]
  const employeeData = [42, 39, 36, 33, 31]

  trendChart = echarts.init(trendChartEl.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Revenue Intensity (kgCO₂/$M)', 'Area Intensity (kgCO₂/m²)', 'Per Employee (tCO₂/emp)'], bottom: 0 },
    grid: { top: 40, left: 60, right: 60, bottom: 50 },
    xAxis: { type: 'category', data: years },
    yAxis: [
      { type: 'value', name: 'Revenue & Employee', position: 'left' },
      { type: 'value', name: 'Area Intensity', position: 'right' }
    ],
    series: [
      { name: 'Revenue Intensity (kgCO₂/$M)', type: 'line', data: revenueData, lineStyle: { color: '#f59e0b', width: 2 }, symbol: 'circle' },
      { name: 'Area Intensity (kgCO₂/m²)', type: 'line', data: areaData, lineStyle: { color: '#3b82f6', width: 2 }, symbol: 'diamond', yAxisIndex: 1 },
      { name: 'Per Employee (tCO₂/emp)', type: 'line', data: employeeData, lineStyle: { color: '#22c55e', width: 2 }, symbol: 'triangle' }
    ]
  })
}

const initScopeChart = () => {
  if (!scopeChartEl.value) return
  if (scopeChart) {
    scopeChart.dispose()
    scopeChart = null
  }

  scopeChart = echarts.init(scopeChartEl.value)
  scopeChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} kgCO₂/m² ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: ['Scope 1', 'Scope 2', 'Scope 3'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: 0.182, name: 'Scope 1', itemStyle: { color: '#f59e0b' } },
        { value: 0.234, name: 'Scope 2', itemStyle: { color: '#3b82f6' } },
        { value: 0.104, name: 'Scope 3', itemStyle: { color: '#22c55e' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const initFacilityChart = () => {
  if (!facilityChartEl.value) return
  if (facilityChart) {
    facilityChart.dispose()
    facilityChart = null
  }

  const names = intensityData.value.map(d => d.facility)
  const intensities = intensityData.value.map(d => d.intensityArea)

  facilityChart = echarts.init(facilityChartEl.value)
  facilityChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 40, containLabel: true },
    xAxis: { type: 'category', data: names, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: 'kgCO₂/m²' },
    series: [{
      type: 'bar',
      data: intensities,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value < 0.4) return '#22c55e'
          if (value < 0.6) return '#f59e0b'
          return '#ef4444'
        }
      },
      label: { show: true, position: 'top', formatter: '{c}' }
    }]
  })
}

const initPeersChart = () => {
  if (!peersChartEl.value) return
  if (peersChart) {
    peersChart.dispose()
    peersChart = null
  }

  const peers = ['Our Company', 'Peer A', 'Peer B', 'Peer C', 'Industry Avg', 'Best in Class']
  const intensities = [0.52, 0.48, 0.55, 0.51, 0.58, 0.35]

  peersChart = echarts.init(peersChartEl.value)
  peersChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: peers, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'kgCO₂/m²' },
    series: [{
      type: 'bar',
      data: intensities,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          return params.name === 'Our Company' ? '#3b82f6' : '#94a3b8'
        }
      },
      label: { show: true, position: 'top', formatter: '{c}' }
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
  const scope1Data = [0.028, 0.026, 0.027, 0.025, 0.024, 0.023, 0.022, 0.023, 0.024, 0.025, 0.026, 0.027]
  const scope2Data = [0.038, 0.036, 0.037, 0.035, 0.034, 0.033, 0.032, 0.033, 0.034, 0.035, 0.036, 0.037]
  const scope3Data = [0.016, 0.015, 0.015, 0.014, 0.014, 0.013, 0.013, 0.014, 0.014, 0.015, 0.015, 0.016]

  monthlyChart = echarts.init(monthlyChartEl.value)
  monthlyChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Scope 1', 'Scope 2', 'Scope 3'], bottom: 0 },
    grid: { top: 30, left: 60, right: 30, bottom: 40 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Intensity (kgCO₂/m²)' },
    series: [
      { name: 'Scope 1', type: 'line', data: scope1Data, lineStyle: { color: '#f59e0b', width: 2 }, symbol: 'circle' },
      { name: 'Scope 2', type: 'line', data: scope2Data, lineStyle: { color: '#3b82f6', width: 2 }, symbol: 'circle' },
      { name: 'Scope 3', type: 'line', data: scope3Data, lineStyle: { color: '#22c55e', width: 2 }, symbol: 'circle' }
    ]
  })
}

const initTargetChart = () => {
  if (!targetChartEl.value) return
  if (targetChart) {
    targetChart.dispose()
    targetChart = null
  }

  const years = ['2024', '2025', '2026', '2027', '2028', '2029', '2030']
  const actual = [0.52, null, null, null, null, null, null]
  const target = [0.52, 0.49, 0.46, 0.43, 0.40, 0.37, 0.34]

  targetChart = echarts.init(targetChartEl.value)
  targetChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Actual', 'Target'], bottom: 0 },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: years },
    yAxis: { type: 'value', name: 'kgCO₂/m²' },
    series: [
      { name: 'Actual', type: 'bar', data: actual, itemStyle: { color: '#3b82f6', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top' } },
      { name: 'Target', type: 'line', data: target, lineStyle: { color: '#ef4444', width: 2, type: 'dashed' }, symbol: 'diamond' }
    ]
  })
}

const initDriversChart = () => {
  if (!driversChartEl.value) return
  if (driversChart) {
    driversChart.dispose()
    driversChart = null
  }

  const drivers = ['Energy Efficiency', 'Renewable Energy', 'Process Optimization', 'Supply Chain', 'Transportation']
  const impacts = [35, 28, 18, 12, 7]

  driversChart = echarts.init(driversChartEl.value)
  driversChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: drivers },
    yAxis: { type: 'value', name: 'Impact (%)' },
    series: [{
      type: 'bar',
      data: impacts,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#f59e0b' },
      label: { show: true, position: 'top', formatter: '{c}%' }
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
  const intensities = [0.55, 0.54, 0.53, 0.52, 0.51, 0.50, 0.49, 0.48, 0.47, 0.46, 0.45, 0.44].map(v => v + (selectedFacility.value!.intensityArea - 0.52))

  facilityTrendChart = echarts.init(facilityTrendChartEl.value)
  facilityTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'kgCO₂/m²' },
    series: [{
      type: 'line',
      data: intensities,
      smooth: true,
      lineStyle: { color: '#3b82f6', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 },
      label: { show: true, position: 'top', formatter: '{c}' }
    }]
  })
}

const initScopeBreakdownChart = () => {
  if (!scopeBreakdownChartEl.value || !selectedFacility.value) return
  if (scopeBreakdownChart) {
    scopeBreakdownChart.dispose()
    scopeBreakdownChart = null
  }

  scopeBreakdownChart = echarts.init(scopeBreakdownChartEl.value)
  scopeBreakdownChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} tCO₂e ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: ['Scope 1', 'Scope 2', 'Scope 3'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: Math.round(selectedFacility.value.carbonFootprint * 0.35), name: 'Scope 1', itemStyle: { color: '#f59e0b' } },
        { value: Math.round(selectedFacility.value.carbonFootprint * 0.45), name: 'Scope 2', itemStyle: { color: '#3b82f6' } },
        { value: Math.round(selectedFacility.value.carbonFootprint * 0.20), name: 'Scope 3', itemStyle: { color: '#22c55e' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initTrendChart()
    initScopeChart()
    initFacilityChart()
    initPeersChart()
    initMonthlyChart()
    initTargetChart()
    initDriversChart()
  })
}

// ==================== Actions ====================
const viewFacilityDetail = (facility: FacilityIntensity) => {
  selectedFacility.value = facility
  detailDialogVisible.value = true
  nextTick(() => {
    initFacilityTrendChart()
    initScopeBreakdownChart()
  })
}

const viewAllData = () => {
  ElMessage.info('Viewing all facilities')
}

const exportFacilityReport = (facility: FacilityIntensity | null) => {
  if (facility) {
    ElMessage.success(`Exporting report for ${facility.facility}...`)
    setTimeout(() => {
      ElMessage.success('Report generated successfully')
    }, 1500)
  }
}

const exportData = () => {
  ElMessage.success('Exporting carbon intensity data...')
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
    const charts = [trendChart, scopeChart, facilityChart, peersChart, monthlyChart, targetChart, driversChart, facilityTrendChart, scopeBreakdownChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([facilityFilter, metricTypeFilter, dateRange], () => {
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
  const charts = [trendChart, scopeChart, facilityChart, peersChart, monthlyChart, targetChart, driversChart, facilityTrendChart, scopeBreakdownChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.carbon-intensity-page {
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