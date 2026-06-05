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
          <span class="loading-title">Cooling Efficiency</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Data Center Cooling System Performance Analytics</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="cooling-efficiency-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><ColdDrink /></el-icon>
          Cooling Efficiency
        </h1>
        <div class="page-subtitle">Monitor and optimize cooling system performance across data center facilities</div>
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
          <el-icon><ColdDrink /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.avgCCOP }}</div>
          <div class="stat-label">Avg Cooling COP</div>
          <div class="stat-trend" :class="stats.copTrend > 0 ? 'up' : 'down'">
            {{ stats.copTrend > 0 ? '↑' : '↓' }} {{ Math.abs(stats.copTrend) }} vs last month
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.coolingPower }}<span class="stat-unit">MW</span></div>
          <div class="stat-label">Cooling Power</div>
          <div class="stat-trend down">{{ stats.coolingPercent }}% of IT load</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.freeCooling }}<span class="stat-unit">hrs</span></div>
          <div class="stat-label">Free Cooling Hours</div>
          <div class="stat-trend up">YTD</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">${{ stats.savings }}<span class="stat-unit">M</span></div>
          <div class="stat-label">Energy Savings</div>
          <div class="stat-trend up">vs baseline</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Average Supply Temp</div>
        <div class="metric-value">{{ metrics.supplyTemp }}<span class="stat-unit">°C</span></div>
        <div class="metric-trend" :class="metrics.supplyTrend < 0 ? 'positive' : 'negative'">
          {{ metrics.supplyTrend < 0 ? '↓' : '↑' }} {{ Math.abs(metrics.supplyTrend) }}°C vs target
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Average Return Temp</div>
        <div class="metric-value">{{ metrics.returnTemp }}<span class="stat-unit">°C</span></div>
        <div class="metric-sub">Delta T: {{ metrics.deltaT }}°C</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Economizer Utilization</div>
        <div class="metric-value">{{ metrics.economizerUtil }}<span class="stat-unit">%</span></div>
        <el-progress :percentage="metrics.economizerUtil" :stroke-width="8" :color="metrics.economizerUtil > 60 ? '#22c55e' : (metrics.economizerUtil > 30 ? '#f59e0b' : '#ef4444')" />
      </div>
      <div class="metric-card">
        <div class="metric-title">Free Cooling Potential</div>
        <div class="metric-value">{{ metrics.freeCoolingPotential }}<span class="stat-unit">%</span></div>
        <div class="metric-trend positive">↑ {{ metrics.potentialGrowth }}% YoY</div>
      </div>
    </div>

    <!-- Charts Row 1 -->
    <div class="charts-row">
      <div class="chart-card large">
        <div class="chart-header">
          <span class="chart-title">Cooling COP Trend</span>
          <span class="chart-subtitle">Monthly efficiency performance</span>
          <el-select v-model="yearFilter" size="small" style="width: 100px" @change="updateCopTrend">
            <el-option label="2024" value="2024" />
            <el-option label="2023" value="2023" />
            <el-option label="2022" value="2022" />
          </el-select>
        </div>
        <div class="chart-container" ref="copTrendChartEl"></div>
      </div>
    </div>

    <!-- Charts Row 2 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">COP by Facility</span>
          <span class="chart-subtitle">Cooling efficiency comparison</span>
        </div>
        <div class="chart-container" ref="facilityChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Cooling Power Breakdown</span>
          <span class="chart-subtitle">Energy consumption by component</span>
        </div>
        <div class="chart-container" ref="breakdownChartEl"></div>
      </div>
    </div>

    <!-- Charts Row 3 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Economizer Hours</span>
          <span class="chart-subtitle">Monthly utilization</span>
        </div>
        <div class="chart-container" ref="economizerChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Temperature Profile</span>
          <span class="chart-subtitle">Supply vs Return trends</span>
        </div>
        <div class="chart-container" ref="tempProfileChartEl"></div>
      </div>
    </div>

    <!-- Charts Row 4 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Cooling Efficiency vs IT Load</span>
          <span class="chart-subtitle">Correlation analysis</span>
        </div>
        <div class="chart-container" ref="loadChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">COP Improvement</span>
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
        <el-select v-model="coolingTypeFilter" placeholder="Cooling Type" clearable style="width: 140px">
          <el-option label="Chilled Water" value="chilled_water" />
          <el-option label="DX Units" value="dx" />
          <el-option label="Evaporative" value="evaporative" />
          <el-option label="Liquid Cooling" value="liquid" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Cooling Systems Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Cooling Systems Performance</span>
        <el-button size="small" @click="viewAllData">View All →</el-button>
      </div>
      <el-table :data="paginatedData" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="facility" label="Facility" min-width="180" />
        <el-table-column prop="coolingType" label="Cooling Type" width="140">
          <template #default="{ row }">
            <el-tag :type="getCoolingTagType(row.coolingType)" size="small">{{ row.coolingType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="cop" label="COP" width="100">
          <template #default="{ row }">
            <span :class="getCopClass(row.cop)">{{ row.cop.toFixed(1) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="coolingPower" label="Cooling Power (kW)" width="150">
          <template #default="{ row }">
            {{ row.coolingPower.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="itPower" label="IT Power (kW)" width="140">
          <template #default="{ row }">
            {{ row.itPower.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="coolingRatio" label="Cooling/IT Ratio" width="140">
          <template #default="{ row }">
            <span :class="getRatioClass(row.coolingRatio)">{{ (row.coolingRatio * 100).toFixed(1) }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="supplyTemp" label="Supply Temp" width="110">
          <template #default="{ row }">
            {{ row.supplyTemp }}°C
          </template>
        </el-table-column>
        <el-table-column prop="returnTemp" label="Return Temp" width="110">
          <template #default="{ row }">
            {{ row.returnTemp }}°C
          </template>
        </el-table-column>
        <el-table-column prop="economizerHours" label="Economizer (hrs)" width="130">
          <template #default="{ row }">
            {{ row.economizerHours.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="trend" label="Trend" width="100">
          <template #default="{ row }">
            <el-tag :type="row.trend === 'improving' ? 'success' : (row.trend === 'stable' ? 'info' : 'danger')" size="small">
              {{ row.trend === 'improving' ? '↑ Improving' : (row.trend === 'stable' ? '→ Stable' : '↓ Worsening') }}
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
          <el-descriptions-item label="Cooling Type">{{ selectedFacility.coolingType }}</el-descriptions-item>
          <el-descriptions-item label="COP">{{ selectedFacility.cop.toFixed(1) }}</el-descriptions-item>
          <el-descriptions-item label="Cooling Power">{{ selectedFacility.coolingPower.toLocaleString() }} kW</el-descriptions-item>
          <el-descriptions-item label="IT Power">{{ selectedFacility.itPower.toLocaleString() }} kW</el-descriptions-item>
          <el-descriptions-item label="Cooling/IT Ratio">{{ (selectedFacility.coolingRatio * 100).toFixed(1) }}%</el-descriptions-item>
          <el-descriptions-item label="Supply Temp">{{ selectedFacility.supplyTemp }}°C</el-descriptions-item>
          <el-descriptions-item label="Return Temp">{{ selectedFacility.returnTemp }}°C</el-descriptions-item>
          <el-descriptions-item label="Delta T">{{ selectedFacility.deltaT }}°C</el-descriptions-item>
          <el-descriptions-item label="Economizer Hours">{{ selectedFacility.economizerHours.toLocaleString() }} hours</el-descriptions-item>
          <el-descriptions-item label="Free Cooling">{{ selectedFacility.freeCooling }}% of year</el-descriptions-item>
          <el-descriptions-item label="Chiller Efficiency" :span="2">{{ selectedFacility.chillerEfficiency }} kW/ton</el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <div class="section-title">Monthly COP Trend</div>
          <div class="trend-chart" ref="facilityTrendChartEl"></div>
        </div>

        <div class="detail-section">
          <div class="section-title">Temperature Distribution</div>
          <div class="trend-chart" ref="tempDistChartEl"></div>
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
  ColdDrink, Calendar, Timer, Money, Download, Refresh,
  RefreshLeft, TrendCharts
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading cooling efficiency data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading cooling system data...',
  'Calculating COP metrics...',
  'Analyzing economizer usage...',
  'Preparing optimization insights...',
  'Almost ready...'
]

// ==================== Types ====================
interface CoolingSystem {
  id: number
  facility: string
  coolingType: string
  cop: number
  coolingPower: number
  itPower: number
  coolingRatio: number
  supplyTemp: number
  returnTemp: number
  deltaT: number
  economizerHours: number
  freeCooling: number
  chillerEfficiency: string
  trend: string
  recommendation: {
    title: string
    type: 'success' | 'warning' | 'info' | 'error'
    description: string
  }
}

// ==================== Mock Data ====================
const facilities = ['Data Center A', 'Data Center B', 'Data Center C', 'Data Center D', 'Data Center E', 'Edge Facility 1', 'Edge Facility 2']

const generateCoolingData = (): CoolingSystem[] => {
  const systemsData: CoolingSystem[] = [
    { id: 1, facility: 'Data Center A', coolingType: 'Chilled Water', cop: 4.2, coolingPower: 1850, itPower: 5200, coolingRatio: 0.356, supplyTemp: 18, returnTemp: 24, deltaT: 6, economizerHours: 1850, freeCooling: 21, chillerEfficiency: '0.65', trend: 'improving',
      recommendation: { title: 'Optimize Chiller Sequencing', type: 'info', description: 'Implement load-based chiller sequencing to improve COP at partial loads.' } },
    { id: 2, facility: 'Data Center B', coolingType: 'Evaporative', cop: 5.8, coolingPower: 950, itPower: 3800, coolingRatio: 0.250, supplyTemp: 21, returnTemp: 28, deltaT: 7, economizerHours: 3200, freeCooling: 37, chillerEfficiency: 'N/A', trend: 'improving',
      recommendation: { title: 'Increase Economizer Usage', type: 'success', description: 'Excellent COP. Maintain and explore additional water-side economizer opportunities.' } },
    { id: 3, facility: 'Data Center C', coolingType: 'DX Units', cop: 3.2, coolingPower: 2850, itPower: 6800, coolingRatio: 0.419, supplyTemp: 16, returnTemp: 20, deltaT: 4, economizerHours: 520, freeCooling: 6, chillerEfficiency: 'N/A', trend: 'worsening',
      recommendation: { title: 'Urgent: Upgrade Cooling System', type: 'error', description: 'Low COP indicates inefficient DX units. Consider chiller or evaporative cooling retrofit.' } },
    { id: 4, facility: 'Data Center D', coolingType: 'Chilled Water', cop: 3.8, coolingPower: 1650, itPower: 4200, coolingRatio: 0.393, supplyTemp: 17, returnTemp: 22, deltaT: 5, economizerHours: 1250, freeCooling: 14, chillerEfficiency: '0.72', trend: 'stable',
      recommendation: { title: 'Increase Supply Temperature', type: 'warning', description: 'Raise chilled water supply temperature from 17°C to 19°C to improve COP.' } },
    { id: 5, facility: 'Data Center E', coolingType: 'Liquid Cooling', cop: 6.5, coolingPower: 520, itPower: 3200, coolingRatio: 0.163, supplyTemp: 25, returnTemp: 32, deltaT: 7, economizerHours: 4200, freeCooling: 48, chillerEfficiency: 'N/A', trend: 'improving',
      recommendation: { title: 'Expand Liquid Cooling', type: 'success', description: 'Industry-leading COP. Expand liquid cooling to high-density racks.' } },
    { id: 6, facility: 'Edge Facility 1', coolingType: 'DX Units', cop: 2.9, coolingPower: 420, itPower: 1200, coolingRatio: 0.350, supplyTemp: 15, returnTemp: 19, deltaT: 4, economizerHours: 380, freeCooling: 4, chillerEfficiency: 'N/A', trend: 'stable',
      recommendation: { title: 'Right-size Cooling Capacity', type: 'warning', description: 'Consider smaller, more efficient units matched to actual load.' } },
    { id: 7, facility: 'Edge Facility 2', coolingType: 'AHU', cop: 3.5, coolingPower: 280, itPower: 850, coolingRatio: 0.329, supplyTemp: 19, returnTemp: 24, deltaT: 5, economizerHours: 680, freeCooling: 8, chillerEfficiency: 'N/A', trend: 'improving',
      recommendation: { title: 'Implement Variable Speed Drives', type: 'info', description: 'Install VFDs on AHU fans to reduce part-load energy consumption.' } }
  ]
  return systemsData
}

const coolingData = ref<CoolingSystem[]>(generateCoolingData())

// ==================== State ====================
const dateRange = ref<Date[] | null>(null)
const facilityFilter = ref('')
const coolingTypeFilter = ref('')
const yearFilter = ref('2024')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const selectedFacility = ref<CoolingSystem | null>(null)

// Chart refs
let copTrendChart: echarts.ECharts | null = null
let facilityChart: echarts.ECharts | null = null
let breakdownChart: echarts.ECharts | null = null
let economizerChart: echarts.ECharts | null = null
let tempProfileChart: echarts.ECharts | null = null
let loadChart: echarts.ECharts | null = null
let improvementChart: echarts.ECharts | null = null
let facilityTrendChart: echarts.ECharts | null = null
let tempDistChart: echarts.ECharts | null = null

const copTrendChartEl = ref<HTMLElement | null>(null)
const facilityChartEl = ref<HTMLElement | null>(null)
const breakdownChartEl = ref<HTMLElement | null>(null)
const economizerChartEl = ref<HTMLElement | null>(null)
const tempProfileChartEl = ref<HTMLElement | null>(null)
const loadChartEl = ref<HTMLElement | null>(null)
const improvementChartEl = ref<HTMLElement | null>(null)
const facilityTrendChartEl = ref<HTMLElement | null>(null)
const tempDistChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  const avgCOP = (coolingData.value.reduce((sum, d) => sum + d.cop, 0) / coolingData.value.length).toFixed(1)
  const totalCoolingPower = coolingData.value.reduce((sum, d) => sum + d.coolingPower, 0)
  const totalITPower = coolingData.value.reduce((sum, d) => sum + d.itPower, 0)
  const coolingPercent = ((totalCoolingPower / totalITPower) * 100).toFixed(0)
  const totalEconomizer = coolingData.value.reduce((sum, d) => sum + d.economizerHours, 0)
  const totalSavings = 2.8

  return {
    avgCCOP: avgCOP,
    copTrend: 0.15,
    coolingPower: (totalCoolingPower / 1000).toFixed(1),
    coolingPercent: coolingPercent,
    freeCooling: Math.round(totalEconomizer / 8760 * 100),
    savings: totalSavings
  }
})

const metrics = computed(() => {
  const avgSupplyTemp = (coolingData.value.reduce((sum, d) => sum + d.supplyTemp, 0) / coolingData.value.length).toFixed(1)
  const avgReturnTemp = (coolingData.value.reduce((sum, d) => sum + d.returnTemp, 0) / coolingData.value.length).toFixed(1)
  const avgDeltaT = (coolingData.value.reduce((sum, d) => sum + d.deltaT, 0) / coolingData.value.length).toFixed(1)
  const avgEconomizer = (coolingData.value.reduce((sum, d) => sum + d.freeCooling, 0) / coolingData.value.length).toFixed(0)
  const freeCoolingPotential = 45

  return {
    supplyTemp: parseFloat(avgSupplyTemp),
    supplyTrend: -0.5,
    returnTemp: parseFloat(avgReturnTemp),
    deltaT: parseFloat(avgDeltaT),
    economizerUtil: parseFloat(avgEconomizer),
    freeCoolingPotential: freeCoolingPotential,
    potentialGrowth: 8
  }
})

const filteredData = computed(() => {
  let filtered = [...coolingData.value]

  if (facilityFilter.value) {
    filtered = filtered.filter(d => d.facility === facilityFilter.value)
  }

  if (coolingTypeFilter.value === 'chilled_water') {
    filtered = filtered.filter(d => d.coolingType === 'Chilled Water')
  } else if (coolingTypeFilter.value === 'dx') {
    filtered = filtered.filter(d => d.coolingType === 'DX Units')
  } else if (coolingTypeFilter.value === 'evaporative') {
    filtered = filtered.filter(d => d.coolingType === 'Evaporative')
  } else if (coolingTypeFilter.value === 'liquid') {
    filtered = filtered.filter(d => d.coolingType === 'Liquid Cooling')
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
const getCopClass = (cop: number): string => {
  if (cop >= 5.5) return 'metric-good'
  if (cop >= 4.0) return 'metric-warning'
  return 'metric-bad'
}

const getRatioClass = (ratio: number): string => {
  if (ratio <= 0.25) return 'metric-good'
  if (ratio <= 0.35) return 'metric-warning'
  return 'metric-bad'
}

const getCoolingTagType = (coolingType: string): string => {
  const map: Record<string, string> = {
    'Chilled Water': 'primary',
    'Evaporative': 'success',
    'DX Units': 'danger',
    'Liquid Cooling': 'success',
    'AHU': 'info'
  }
  return map[coolingType] || 'info'
}

const resetFilters = () => {
  facilityFilter.value = ''
  coolingTypeFilter.value = ''
  dateRange.value = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

// ==================== Chart Functions ====================
const initCopTrendChart = () => {
  if (!copTrendChartEl.value) return
  if (copTrendChart) {
    copTrendChart.dispose()
    copTrendChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const cop2024 = [3.8, 3.9, 4.0, 4.1, 4.0, 3.9, 3.8, 3.9, 4.1, 4.2, 4.3, 4.4]
  const cop2023 = [3.5, 3.6, 3.7, 3.8, 3.7, 3.6, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0]
  const cop2022 = [3.2, 3.3, 3.4, 3.5, 3.4, 3.3, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7]

  let dataToShow = cop2024
  if (yearFilter.value === '2023') dataToShow = cop2023
  if (yearFilter.value === '2022') dataToShow = cop2022

  copTrendChart = echarts.init(copTrendChartEl.value)
  copTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'COP', min: 3.0, max: 4.8 },
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

  const names = coolingData.value.map(d => d.facility)
  const copValues = coolingData.value.map(d => d.cop)

  facilityChart = echarts.init(facilityChartEl.value)
  facilityChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 40, containLabel: true },
    xAxis: { type: 'category', data: names, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: 'COP', min: 2.5, max: 7.0 },
    series: [{
      type: 'bar',
      data: copValues,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value >= 5.5) return '#22c55e'
          if (value >= 4.0) return '#3b82f6'
          return '#ef4444'
        }
      },
      label: { show: true, position: 'top', formatter: (params: any) => params.value.toFixed(1) },
      markLine: {
        data: [{ yAxis: 4.0, name: 'Good' }, { yAxis: 5.5, name: 'Excellent' }],
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
    tooltip: { trigger: 'item', formatter: '{b}: {c} kW ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: ['Chillers', 'Pumps', 'Cooling Towers', 'CRAC/CRAH'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: 3200, name: 'Chillers', itemStyle: { color: '#3b82f6' } },
        { value: 850, name: 'Pumps', itemStyle: { color: '#22c55e' } },
        { value: 620, name: 'Cooling Towers', itemStyle: { color: '#f59e0b' } },
        { value: 1800, name: 'CRAC/CRAH', itemStyle: { color: '#8b5cf6' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const initEconomizerChart = () => {
  if (!economizerChartEl.value) return
  if (economizerChart) {
    economizerChart.dispose()
    economizerChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const hours = [280, 250, 310, 180, 120, 80, 50, 60, 110, 200, 290, 320]

  economizerChart = echarts.init(economizerChartEl.value)
  economizerChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 60, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Economizer Hours' },
    series: [{
      type: 'bar',
      data: hours,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#22c55e' },
      label: { show: true, position: 'top', formatter: '{c}' }
    }]
  })
}

const initTempProfileChart = () => {
  if (!tempProfileChartEl.value) return
  if (tempProfileChart) {
    tempProfileChart.dispose()
    tempProfileChart = null
  }

  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const supplyTemp = [18, 17, 17, 16, 16, 17, 18, 19, 20, 21, 22, 22, 23, 23, 22, 22, 21, 20, 19, 18, 17, 17, 17, 18]
  const returnTemp = [24, 23, 23, 22, 22, 23, 24, 25, 26, 27, 28, 28, 29, 29, 28, 28, 27, 26, 25, 24, 23, 23, 23, 24]

  tempProfileChart = echarts.init(tempProfileChartEl.value)
  tempProfileChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Supply Temp', 'Return Temp'], bottom: 0 },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: hours, axisLabel: { rotate: 45, interval: 3 } },
    yAxis: { type: 'value', name: 'Temperature (°C)' },
    series: [
      { name: 'Supply Temp', type: 'line', data: supplyTemp, lineStyle: { color: '#3b82f6', width: 2 }, symbol: 'circle' },
      { name: 'Return Temp', type: 'line', data: returnTemp, lineStyle: { color: '#ef4444', width: 2 }, symbol: 'circle' }
    ]
  })
}

const initLoadChart = () => {
  if (!loadChartEl.value) return
  if (loadChart) {
    loadChart.dispose()
    loadChart = null
  }

  const loadPercent = [20, 30, 40, 50, 60, 70, 80, 90, 100]
  const copValues = [3.2, 3.5, 3.8, 4.1, 4.3, 4.5, 4.6, 4.7, 4.7]

  loadChart = echarts.init(loadChartEl.value)
  loadChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: loadPercent, name: 'IT Load (%)' },
    yAxis: { type: 'value', name: 'COP', min: 3.0, max: 5.0 },
    series: [{
      type: 'line',
      data: copValues,
      smooth: true,
      lineStyle: { color: '#f59e0b', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 },
      label: { show: true, position: 'top', formatter: '{c}' }
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
  const copValues = [3.2, 3.5, 3.7, 4.0, 4.3]

  improvementChart = echarts.init(improvementChartEl.value)
  improvementChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: years },
    yAxis: { type: 'value', name: 'Average COP', min: 3.0, max: 4.6 },
    series: [{
      type: 'line',
      data: copValues,
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
  const copValues = [4.0, 4.1, 4.2, 4.3, 4.2, 4.1, 4.0, 4.1, 4.3, 4.4, 4.5, 4.6]

  facilityTrendChart = echarts.init(facilityTrendChartEl.value)
  facilityTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'COP' },
    series: [{
      type: 'line',
      data: copValues,
      smooth: true,
      lineStyle: { color: '#3b82f6', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 },
      label: { show: true, position: 'top', formatter: '{c}' }
    }]
  })
}

const initTempDistChart = () => {
  if (!tempDistChartEl.value || !selectedFacility.value) return
  if (tempDistChart) {
    tempDistChart.dispose()
    tempDistChart = null
  }

  const zones = ['Cold Aisle 1', 'Cold Aisle 2', 'Cold Aisle 3', 'Hot Aisle 1', 'Hot Aisle 2', 'Hot Aisle 3', 'Return Air', 'Supply Air']
  const temps = [22, 23, 21, 32, 33, 31, 28, 18]

  tempDistChart = echarts.init(tempDistChartEl.value)
  tempDistChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 40, containLabel: true },
    xAxis: { type: 'category', data: zones, axisLabel: { rotate: 30, fontSize: 10 } },
    yAxis: { type: 'value', name: 'Temperature (°C)' },
    series: [{
      type: 'bar',
      data: temps,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value >= 26) return '#ef4444'
          if (value >= 24) return '#f59e0b'
          return '#22c55e'
        }
      },
      label: { show: true, position: 'top', formatter: '{c}°C' }
    }]
  })
}

const updateCopTrend = () => {
  initCopTrendChart()
}

const refreshCharts = () => {
  nextTick(() => {
    initCopTrendChart()
    initFacilityChart()
    initBreakdownChart()
    initEconomizerChart()
    initTempProfileChart()
    initLoadChart()
    initImprovementChart()
  })
}

// ==================== Actions ====================
const viewFacilityDetail = (facility: CoolingSystem) => {
  selectedFacility.value = facility
  detailDialogVisible.value = true
  nextTick(() => {
    initFacilityTrendChart()
    initTempDistChart()
  })
}

const viewAllData = () => {
  ElMessage.info('Viewing all cooling systems')
}

const exportFacilityReport = (facility: CoolingSystem | null) => {
  if (facility) {
    ElMessage.success(`Exporting report for ${facility.facility}...`)
    setTimeout(() => {
      ElMessage.success('Report generated successfully')
    }, 1500)
  }
}

const exportData = () => {
  ElMessage.success('Exporting cooling efficiency data...')
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
    const charts = [copTrendChart, facilityChart, breakdownChart, economizerChart, tempProfileChart, loadChart, improvementChart, facilityTrendChart, tempDistChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([facilityFilter, coolingTypeFilter, dateRange], () => {
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
  const charts = [copTrendChart, facilityChart, breakdownChart, economizerChart, tempProfileChart, loadChart, improvementChart, facilityTrendChart, tempDistChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.cooling-efficiency-page {
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
  max-height: 550px;
  overflow-y: auto;
}
:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}
</style>