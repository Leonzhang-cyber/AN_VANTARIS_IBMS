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
          <span class="loading-title">PUE Analytics</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Power Usage Effectiveness Monitoring & Optimization</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="pue-analytics-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><DataAnalysis /></el-icon>
          PUE Analytics
        </h1>
        <div class="page-subtitle">Monitor and optimize Power Usage Effectiveness across data center facilities</div>
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
          <div class="stat-value">{{ stats.currentPUE }}</div>
          <div class="stat-label">Current PUE</div>
          <div class="stat-trend" :class="stats.pueTrend < 0 ? 'down' : 'up'">
            {{ stats.pueTrend < 0 ? '↓' : '↑' }} {{ Math.abs(stats.pueTrend) }} vs last month
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.averagePUE }}</div>
          <div class="stat-label">Average PUE (YTD)</div>
          <div class="stat-trend down">vs {{ stats.industryAvg }} industry avg</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.bestPUE }}</div>
          <div class="stat-label">Best PUE</div>
          <div class="stat-trend up">{{ stats.bestDate }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.annualSavings }}<span class="stat-unit">M</span></div>
          <div class="stat-label">Annual Energy Savings</div>
          <div class="stat-trend up">vs baseline</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">IT Power Load</div>
        <div class="metric-value">{{ metrics.itPower }}<span class="metric-unit">MW</span></div>
        <div class="metric-trend" :class="metrics.itTrend < 0 ? 'positive' : 'negative'">
          {{ metrics.itTrend < 0 ? '↓' : '↑' }} {{ Math.abs(metrics.itTrend) }}% vs last month
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Cooling Power</div>
        <div class="metric-value">{{ metrics.coolingPower }}<span class="metric-unit">MW</span></div>
        <div class="metric-sub">{{ metrics.coolingPercent }}% of total</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Power Distribution Loss</div>
        <div class="metric-value">{{ metrics.pduLoss }}<span class="metric-unit">MW</span></div>
        <div class="metric-trend negative">{{ metrics.pduEfficiency }}% efficiency</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Lighting & Other</div>
        <div class="metric-value">{{ metrics.otherPower }}<span class="metric-unit">MW</span></div>
        <div class="metric-sub">{{ metrics.otherPercent }}% of total</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card large">
        <div class="chart-header">
          <span class="chart-title">PUE Trend</span>
          <span class="chart-subtitle">Monthly PUE performance</span>
          <el-select v-model="yearFilter" size="small" style="width: 100px" @change="updatePueTrend">
            <el-option label="2024" value="2024" />
            <el-option label="2023" value="2023" />
            <el-option label="2022" value="2022" />
          </el-select>
        </div>
        <div class="chart-container" ref="pueTrendChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">PUE by Facility</span>
          <span class="chart-subtitle">Data center comparison</span>
        </div>
        <div class="chart-container" ref="facilityChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Power Breakdown</span>
          <span class="chart-subtitle">Energy consumption distribution</span>
        </div>
        <div class="chart-container" ref="breakdownChartEl"></div>
      </div>
    </div>

    <!-- Third Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">PUE vs Temperature</span>
          <span class="chart-subtitle">Correlation analysis</span>
        </div>
        <div class="chart-container" ref="correlationChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Hourly PUE Profile</span>
          <span class="chart-subtitle">Daily variation</span>
        </div>
        <div class="chart-container" ref="hourlyChartEl"></div>
      </div>
    </div>

    <!-- Fourth Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">PUE by IT Load</span>
          <span class="chart-subtitle">Efficiency curve</span>
        </div>
        <div class="chart-container" ref="loadChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">PUE Improvement</span>
          <span class="chart-subtitle">Year-over-year comparison</span>
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
        <el-select v-model="pueRangeFilter" placeholder="PUE Range" clearable style="width: 140px">
          <el-option label="Excellent (<1.3)" value="excellent" />
          <el-option label="Good (1.3-1.4)" value="good" />
          <el-option label="Average (1.4-1.5)" value="average" />
          <el-option label="Poor (>1.5)" value="poor" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- PUE Data Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Data Center PUE Metrics</span>
        <el-button size="small" @click="viewAllData">View All →</el-button>
      </div>
      <el-table :data="paginatedData" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="facility" label="Facility" min-width="180" />
        <el-table-column prop="pue" label="PUE" width="100">
          <template #default="{ row }">
            <span :class="getPueClass(row.pue)">{{ row.pue.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="itPower" label="IT Power (MW)" width="130">
          <template #default="{ row }">
            {{ row.itPower.toFixed(1) }}
          </template>
        </el-table-column>
        <el-table-column prop="coolingPower" label="Cooling (MW)" width="130">
          <template #default="{ row }">
            {{ row.coolingPower.toFixed(1) }}
          </template>
        </el-table-column>
        <el-table-column prop="pduLoss" label="PDU Loss (MW)" width="130">
          <template #default="{ row }">
            {{ row.pduLoss.toFixed(1) }}
          </template>
        </el-table-column>
        <el-table-column prop="totalPower" label="Total Power (MW)" width="140">
          <template #default="{ row }">
            {{ row.totalPower.toFixed(1) }}
          </template>
        </el-table-column>
        <el-table-column prop="efficiency" label="Efficiency" width="120">
          <template #default="{ row }">
            <el-progress :percentage="row.efficiency" :stroke-width="8" :color="getEfficiencyColor(row.efficiency)" :format="() => `${row.efficiency}%`" />
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
          <el-descriptions-item label="PUE">{{ selectedFacility.pue.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="IT Power">{{ selectedFacility.itPower.toFixed(1) }} MW</el-descriptions-item>
          <el-descriptions-item label="Cooling Power">{{ selectedFacility.coolingPower.toFixed(1) }} MW</el-descriptions-item>
          <el-descriptions-item label="PDU Loss">{{ selectedFacility.pduLoss.toFixed(1) }} MW</el-descriptions-item>
          <el-descriptions-item label="Total Power">{{ selectedFacility.totalPower.toFixed(1) }} MW</el-descriptions-item>
          <el-descriptions-item label="Efficiency">{{ selectedFacility.efficiency }}%</el-descriptions-item>
          <el-descriptions-item label="Cooling Type">{{ selectedFacility.coolingType }}</el-descriptions-item>
          <el-descriptions-item label="IT Load">{{ selectedFacility.itLoad }} MW</el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <div class="section-title">Monthly PUE Trend</div>
          <div class="trend-chart" ref="facilityTrendChartEl"></div>
        </div>

        <div class="detail-section">
          <div class="section-title">Power Breakdown</div>
          <div class="trend-chart" ref="facilityBreakdownChartEl"></div>
        </div>

        <div class="detail-section">
          <div class="section-title">Optimization Recommendations</div>
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
  DataAnalysis, TrendCharts, Calendar, Timer, Money, Download, Refresh,
  RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading PUE analytics data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading facility data...',
  'Calculating PUE metrics...',
  'Analyzing efficiency trends...',
  'Preparing optimization insights...',
  'Almost ready...'
]

// ==================== Types ====================
interface PueFacility {
  id: number
  facility: string
  pue: number
  itPower: number
  coolingPower: number
  pduLoss: number
  totalPower: number
  efficiency: number
  trend: string
  coolingType: string
  itLoad: number
  recommendation: {
    title: string
    type: 'success' | 'warning' | 'info' | 'error'
    description: string
  }
}

// ==================== Mock Data ====================
const facilities = ['Data Center A', 'Data Center B', 'Data Center C', 'Data Center D', 'Data Center E', 'Edge Facility 1', 'Edge Facility 2']

const generatePueData = (): PueFacility[] => {
  const facilitiesData: PueFacility[] = [
    { id: 1, facility: 'Data Center A', pue: 1.42, itPower: 12.5, coolingPower: 3.8, pduLoss: 0.9, totalPower: 17.2, efficiency: 72, trend: 'improving', coolingType: 'Chilled Water', itLoad: 12.5,
      recommendation: { title: 'Optimize Cooling Setpoints', type: 'info', description: 'Adjust chilled water temperature setpoints to reduce compressor work while maintaining IT inlet temperatures.' } },
    { id: 2, facility: 'Data Center B', pue: 1.38, itPower: 8.2, coolingPower: 2.1, pduLoss: 0.6, totalPower: 10.9, efficiency: 75, trend: 'improving', coolingType: 'In-Row Cooling', itLoad: 8.2,
      recommendation: { title: 'Implement Free Cooling', type: 'success', description: 'Increase economizer usage during cooler months to reduce mechanical cooling demand.' } },
    { id: 3, facility: 'Data Center C', pue: 1.52, itPower: 15.0, coolingPower: 5.5, pduLoss: 1.2, totalPower: 21.7, efficiency: 68, trend: 'worsening', coolingType: 'CRAC Units', itLoad: 15.0,
      recommendation: { title: 'CRAC Unit Upgrade', type: 'warning', description: 'Replace aging CRAC units with variable speed drives and high-efficiency components.' } },
    { id: 4, facility: 'Data Center D', pue: 1.45, itPower: 6.5, coolingPower: 2.1, pduLoss: 0.5, totalPower: 9.1, efficiency: 71, trend: 'stable', coolingType: 'AHU', itLoad: 6.5,
      recommendation: { title: 'Containment Improvement', type: 'info', description: 'Implement hot aisle containment to improve cooling efficiency and reduce bypass air.' } },
    { id: 5, facility: 'Data Center E', pue: 1.35, itPower: 10.0, coolingPower: 2.4, pduLoss: 0.7, totalPower: 13.1, efficiency: 76, trend: 'improving', coolingType: 'Liquid Cooling', itLoad: 10.0,
      recommendation: { title: 'Expanding Liquid Cooling', type: 'success', description: 'Deploy additional liquid cooling for high-density racks to further reduce PUE.' } },
    { id: 6, facility: 'Edge Facility 1', pue: 1.48, itPower: 1.2, coolingPower: 0.42, pduLoss: 0.1, totalPower: 1.72, efficiency: 69, trend: 'stable', coolingType: 'DX Units', itLoad: 1.2,
      recommendation: { title: 'Right-size Cooling', type: 'warning', description: 'Evaluate cooling capacity vs actual load; consider smaller, more efficient units.' } },
    { id: 7, facility: 'Edge Facility 2', pue: 1.44, itPower: 0.8, coolingPower: 0.28, pduLoss: 0.07, totalPower: 1.15, efficiency: 70, trend: 'improving', coolingType: 'DX Units', itLoad: 0.8,
      recommendation: { title: 'Smart Thermostat Installation', type: 'info', description: 'Install smart thermostats to optimize cooling based on actual occupancy and load.' } }
  ]
  return facilitiesData
}

const pueData = ref<PueFacility[]>(generatePueData())

// ==================== State ====================
const dateRange = ref<Date[] | null>(null)
const facilityFilter = ref('')
const pueRangeFilter = ref('')
const yearFilter = ref('2024')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const selectedFacility = ref<PueFacility | null>(null)

// Chart refs
let pueTrendChart: echarts.ECharts | null = null
let facilityChart: echarts.ECharts | null = null
let breakdownChart: echarts.ECharts | null = null
let correlationChart: echarts.ECharts | null = null
let hourlyChart: echarts.ECharts | null = null
let loadChart: echarts.ECharts | null = null
let improvementChart: echarts.ECharts | null = null
let facilityTrendChart: echarts.ECharts | null = null
let facilityBreakdownChart: echarts.ECharts | null = null

const pueTrendChartEl = ref<HTMLElement | null>(null)
const facilityChartEl = ref<HTMLElement | null>(null)
const breakdownChartEl = ref<HTMLElement | null>(null)
const correlationChartEl = ref<HTMLElement | null>(null)
const hourlyChartEl = ref<HTMLElement | null>(null)
const loadChartEl = ref<HTMLElement | null>(null)
const improvementChartEl = ref<HTMLElement | null>(null)
const facilityTrendChartEl = ref<HTMLElement | null>(null)
const facilityBreakdownChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  const currentPUE = 1.41
  const averagePUE = pueData.value.reduce((sum, d) => sum + d.pue, 0) / pueData.value.length
  const bestPUE = Math.min(...pueData.value.map(d => d.pue))
  const annualSavings = 2.8

  return {
    currentPUE: currentPUE.toFixed(2),
    pueTrend: -0.03,
    averagePUE: averagePUE.toFixed(2),
    industryAvg: 1.52,
    bestPUE: bestPUE.toFixed(2),
    bestDate: 'Data Center E',
    annualSavings: annualSavings
  }
})

const metrics = computed(() => {
  const totalIT = pueData.value.reduce((sum, d) => sum + d.itPower, 0)
  const totalCooling = pueData.value.reduce((sum, d) => sum + d.coolingPower, 0)
  const totalPDU = pueData.value.reduce((sum, d) => sum + d.pduLoss, 0)
  const totalOther = pueData.value.reduce((sum, d) => sum + d.totalPower, 0) - totalIT - totalCooling - totalPDU
  const coolingPercent = (totalCooling / (totalCooling + totalIT + totalPDU + totalOther) * 100).toFixed(1)
  const otherPercent = (totalOther / (totalCooling + totalIT + totalPDU + totalOther) * 100).toFixed(1)

  return {
    itPower: totalIT.toFixed(1),
    itTrend: 2.5,
    coolingPower: totalCooling.toFixed(1),
    coolingPercent: parseFloat(coolingPercent),
    pduLoss: totalPDU.toFixed(1),
    pduEfficiency: 94,
    otherPower: totalOther.toFixed(1),
    otherPercent: parseFloat(otherPercent)
  }
})

const filteredData = computed(() => {
  let filtered = [...pueData.value]

  if (facilityFilter.value) {
    filtered = filtered.filter(d => d.facility === facilityFilter.value)
  }

  if (pueRangeFilter.value === 'excellent') {
    filtered = filtered.filter(d => d.pue < 1.3)
  } else if (pueRangeFilter.value === 'good') {
    filtered = filtered.filter(d => d.pue >= 1.3 && d.pue < 1.4)
  } else if (pueRangeFilter.value === 'average') {
    filtered = filtered.filter(d => d.pue >= 1.4 && d.pue < 1.5)
  } else if (pueRangeFilter.value === 'poor') {
    filtered = filtered.filter(d => d.pue >= 1.5)
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
const getPueClass = (pue: number): string => {
  if (pue < 1.3) return 'metric-good'
  if (pue < 1.4) return 'metric-warning'
  return 'metric-bad'
}

const getEfficiencyColor = (efficiency: number): string => {
  if (efficiency >= 75) return '#22c55e'
  if (efficiency >= 68) return '#f59e0b'
  return '#ef4444'
}

const resetFilters = () => {
  facilityFilter.value = ''
  pueRangeFilter.value = ''
  dateRange.value = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

// ==================== Chart Functions ====================
const initPueTrendChart = () => {
  if (!pueTrendChartEl.value) return
  if (pueTrendChart) {
    pueTrendChart.dispose()
    pueTrendChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const pueData2024 = [1.48, 1.47, 1.45, 1.44, 1.43, 1.42, 1.42, 1.41, 1.40, 1.39, 1.38, 1.37]
  const pueData2023 = [1.52, 1.51, 1.50, 1.50, 1.49, 1.48, 1.48, 1.47, 1.46, 1.45, 1.44, 1.43]
  const pueData2022 = [1.56, 1.55, 1.54, 1.53, 1.53, 1.52, 1.52, 1.51, 1.50, 1.49, 1.48, 1.47]

  let dataToShow = pueData2024
  if (yearFilter.value === '2023') dataToShow = pueData2023
  if (yearFilter.value === '2022') dataToShow = pueData2022

  pueTrendChart = echarts.init(pueTrendChartEl.value)
  pueTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'PUE', min: 1.3, max: 1.6 },
    series: [{
      type: 'line',
      data: dataToShow,
      smooth: true,
      lineStyle: { color: '#3b82f6', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 },
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

  const names = pueData.value.map(d => d.facility)
  const pueValues = pueData.value.map(d => d.pue)

  facilityChart = echarts.init(facilityChartEl.value)
  facilityChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 40, containLabel: true },
    xAxis: { type: 'category', data: names, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: 'PUE', min: 1.2, max: 1.6 },
    series: [{
      type: 'bar',
      data: pueValues,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value < 1.3) return '#22c55e'
          if (value < 1.4) return '#3b82f6'
          if (value < 1.5) return '#f59e0b'
          return '#ef4444'
        }
      },
      label: { show: true, position: 'top', formatter: '{c}' },
      markLine: {
        data: [{ yAxis: 1.3, name: 'Excellent' }, { yAxis: 1.4, name: 'Good' }, { yAxis: 1.5, name: 'Average' }],
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

  breakdownChart = echarts.init(breakdownChartEl.value)
  breakdownChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
    legend: { orient: 'vertical', left: 'left', data: ['IT Equipment', 'Cooling', 'Power Distribution', 'Lighting & Other'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: 65, name: 'IT Equipment', itemStyle: { color: '#3b82f6' } },
        { value: 22, name: 'Cooling', itemStyle: { color: '#22c55e' } },
        { value: 8, name: 'Power Distribution', itemStyle: { color: '#f59e0b' } },
        { value: 5, name: 'Lighting & Other', itemStyle: { color: '#8b5cf6' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const initCorrelationChart = () => {
  if (!correlationChartEl.value) return
  if (correlationChart) {
    correlationChart.dispose()
    correlationChart = null
  }

  const temps = [18, 20, 22, 24, 26, 28, 30, 32, 34, 36]
  const pueValues = [1.32, 1.34, 1.36, 1.38, 1.41, 1.44, 1.48, 1.52, 1.56, 1.60]

  correlationChart = echarts.init(correlationChartEl.value)
  correlationChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'value', name: 'Outside Temperature (°C)' },
    yAxis: { type: 'value', name: 'PUE', min: 1.3, max: 1.65 },
    series: [{
      type: 'line',
      data: pueValues.map((v, i) => [temps[i], v]),
      smooth: true,
      lineStyle: { color: '#f59e0b', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 }
    }]
  })
}

const initHourlyChart = () => {
  if (!hourlyChartEl.value) return
  if (hourlyChart) {
    hourlyChart.dispose()
    hourlyChart = null
  }

  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const pueValues = [1.39, 1.38, 1.38, 1.37, 1.37, 1.36, 1.37, 1.39, 1.42, 1.44, 1.45, 1.44, 1.43, 1.42, 1.41, 1.40, 1.39, 1.38, 1.38, 1.39, 1.40, 1.41, 1.40, 1.39]

  hourlyChart = echarts.init(hourlyChartEl.value)
  hourlyChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: hours, axisLabel: { rotate: 45, interval: 3 } },
    yAxis: { type: 'value', name: 'PUE', min: 1.35, max: 1.48 },
    series: [{
      type: 'line',
      data: pueValues,
      smooth: true,
      lineStyle: { color: '#3b82f6', width: 2 },
      symbol: 'circle',
      symbolSize: 4,
      areaStyle: { opacity: 0.1 }
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
  const pueValues = [1.55, 1.48, 1.42, 1.38, 1.35, 1.34, 1.33, 1.33, 1.34]

  loadChart = echarts.init(loadChartEl.value)
  loadChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: loadPercent, name: 'IT Load (%)' },
    yAxis: { type: 'value', name: 'PUE', min: 1.3, max: 1.6 },
    series: [{
      type: 'line',
      data: pueValues,
      smooth: true,
      lineStyle: { color: '#22c55e', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 }
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
  const pueValues = [1.58, 1.54, 1.50, 1.45, 1.41]

  improvementChart = echarts.init(improvementChartEl.value)
  improvementChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: years },
    yAxis: { type: 'value', name: 'PUE', min: 1.35, max: 1.65 },
    series: [{
      type: 'line',
      data: pueValues,
      smooth: true,
      lineStyle: { color: '#22c55e', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 },
      label: { show: true, position: 'top', formatter: '{c}' }
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
  const pueValues = [1.48, 1.47, 1.46, 1.45, 1.44, 1.43, 1.42, 1.41, 1.40, 1.39, 1.38, 1.37]

  facilityTrendChart = echarts.init(facilityTrendChartEl.value)
  facilityTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'PUE' },
    series: [{
      type: 'line',
      data: pueValues,
      smooth: true,
      lineStyle: { color: '#3b82f6', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 },
      label: { show: true, position: 'top', formatter: '{c}' }
    }]
  })
}

const initFacilityBreakdownChart = () => {
  if (!facilityBreakdownChartEl.value || !selectedFacility.value) return
  if (facilityBreakdownChart) {
    facilityBreakdownChart.dispose()
    facilityBreakdownChart = null
  }

  const itPower = selectedFacility.value.itPower
  const coolingPower = selectedFacility.value.coolingPower
  const pduLoss = selectedFacility.value.pduLoss
  const other = selectedFacility.value.totalPower - itPower - coolingPower - pduLoss

  facilityBreakdownChart = echarts.init(facilityBreakdownChartEl.value)
  facilityBreakdownChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} MW ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: ['IT Equipment', 'Cooling', 'Power Distribution', 'Other'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: itPower, name: 'IT Equipment', itemStyle: { color: '#3b82f6' } },
        { value: coolingPower, name: 'Cooling', itemStyle: { color: '#22c55e' } },
        { value: pduLoss, name: 'Power Distribution', itemStyle: { color: '#f59e0b' } },
        { value: other, name: 'Other', itemStyle: { color: '#8b5cf6' } }
      ],
      label: { show: true, formatter: '{b}: {c} MW' },
      emphasis: { scale: true }
    }]
  })
}

const updatePueTrend = () => {
  initPueTrendChart()
}

const refreshCharts = () => {
  nextTick(() => {
    initPueTrendChart()
    initFacilityChart()
    initBreakdownChart()
    initCorrelationChart()
    initHourlyChart()
    initLoadChart()
    initImprovementChart()
  })
}

// ==================== Actions ====================
const viewFacilityDetail = (facility: PueFacility) => {
  selectedFacility.value = facility
  detailDialogVisible.value = true
  nextTick(() => {
    initFacilityTrendChart()
    initFacilityBreakdownChart()
  })
}

const viewAllData = () => {
  ElMessage.info('Viewing all facilities')
}

const exportFacilityReport = (facility: PueFacility | null) => {
  if (facility) {
    ElMessage.success(`Exporting report for ${facility.facility}...`)
    setTimeout(() => {
      ElMessage.success('Report generated successfully')
    }, 1500)
  }
}

const exportData = () => {
  ElMessage.success('Exporting PUE analytics data...')
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
    const charts = [pueTrendChart, facilityChart, breakdownChart, correlationChart, hourlyChart, loadChart, improvementChart, facilityTrendChart, facilityBreakdownChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([facilityFilter, pueRangeFilter, dateRange], () => {
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
  const charts = [pueTrendChart, facilityChart, breakdownChart, correlationChart, hourlyChart, loadChart, improvementChart, facilityTrendChart, facilityBreakdownChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.pue-analytics-page {
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