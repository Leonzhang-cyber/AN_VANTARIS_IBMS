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
          <span class="loading-title">Renewable Energy Ratio</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Renewable Energy Mix & Decarbonization Progress</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="renewable-energy-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Sunny /></el-icon>
          Renewable Energy Ratio
        </h1>
        <div class="page-subtitle">Track renewable energy procurement, carbon reduction, and 100% RE progress</div>
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
        <div class="stat-icon green">
          <el-icon><Sunny /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.renewableRatio }}<span class="stat-unit">%</span></div>
          <div class="stat-label">Renewable Energy Ratio</div>
          <div class="stat-trend up">↑ {{ stats.ratioGrowth }}% vs last year</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.renewableEnergy }}<span class="stat-unit">GWh</span></div>
          <div class="stat-label">Renewable Energy</div>
          <div class="stat-trend up">YTD</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.carbonAvoided }}<span class="stat-unit">kt</span></div>
          <div class="stat-label">CO₂ Avoided</div>
          <div class="stat-trend up">↑ {{ stats.carbonGrowth }}% YoY</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.reProgress }}<span class="stat-unit">%</span></div>
          <div class="stat-label">100% RE Progress</div>
          <div class="stat-trend up">Target: 2030</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Total Energy Consumption</div>
        <div class="metric-value">{{ metrics.totalEnergy }}<span class="stat-unit">GWh</span></div>
        <div class="metric-trend" :class="metrics.energyTrend < 0 ? 'positive' : 'negative'">
          {{ metrics.energyTrend < 0 ? '↓' : '↑' }} {{ Math.abs(metrics.energyTrend) }}% vs last month
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-title">RE Procurement Cost</div>
        <div class="metric-value">${{ metrics.reCost }}<span class="stat-unit">M</span></div>
        <div class="metric-sub">${{ metrics.costPerMWh }}/MWh average</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">RE Certificates (RECs)</div>
        <div class="metric-value">{{ metrics.recs }}<span class="stat-unit">k</span></div>
        <div class="metric-trend positive">Retired this year</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">PPA Capacity</div>
        <div class="metric-value">{{ metrics.ppaCapacity }}<span class="stat-unit">MW</span></div>
        <div class="metric-sub">Under contract</div>
      </div>
    </div>

    <!-- Charts Row 1 -->
    <div class="charts-row">
      <div class="chart-card large">
        <div class="chart-header">
          <span class="chart-title">Renewable Energy Ratio Trend</span>
          <span class="chart-subtitle">Monthly RE percentage</span>
          <el-select v-model="yearFilter" size="small" style="width: 100px" @change="updateRatioTrend">
            <el-option label="2024" value="2024" />
            <el-option label="2023" value="2023" />
            <el-option label="2022" value="2022" />
          </el-select>
        </div>
        <div class="chart-container" ref="ratioTrendChartEl"></div>
      </div>
    </div>

    <!-- Charts Row 2 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Energy Mix</span>
          <span class="chart-subtitle">Renewable vs Non-renewable</span>
        </div>
        <div class="chart-container" ref="energyMixChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">RE by Facility</span>
          <span class="chart-subtitle">Facility renewable ratio</span>
        </div>
        <div class="chart-container" ref="facilityChartEl"></div>
      </div>
    </div>

    <!-- Charts Row 3 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Renewable Energy Sources</span>
          <span class="chart-subtitle">Breakdown by type</span>
        </div>
        <div class="chart-container" ref="sourceChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Carbon Avoided Trend</span>
          <span class="chart-subtitle">Monthly CO₂ reduction</span>
        </div>
        <div class="chart-container" ref="carbonChartEl"></div>
      </div>
    </div>

    <!-- Charts Row 4 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Progress to 100% RE</span>
          <span class="chart-subtitle">Milestone tracking</span>
        </div>
        <div class="chart-container" ref="progressChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">PPA vs RECs Contribution</span>
          <span class="chart-subtitle">Procurement methods</span>
        </div>
        <div class="chart-container" ref="procurementChartEl"></div>
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
        <el-select v-model="reTypeFilter" placeholder="RE Type" clearable style="width: 140px">
          <el-option label="Solar" value="solar" />
          <el-option label="Wind" value="wind" />
          <el-option label="Hydro" value="hydro" />
          <el-option label="Biomass" value="biomass" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- RE Data Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Renewable Energy by Facility</span>
        <el-button size="small" @click="viewAllData">View All →</el-button>
      </div>
      <el-table :data="paginatedData" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="facility" label="Facility" min-width="180" />
        <el-table-column prop="reRatio" label="RE Ratio" width="140">
          <template #default="{ row }">
            <el-progress :percentage="row.reRatio" :stroke-width="10" :color="getRatioColor(row.reRatio)" :format="() => `${row.reRatio}%`" />
          </template>
        </el-table-column>
        <el-table-column prop="reEnergy" label="RE Energy (MWh)" width="140">
          <template #default="{ row }">
            {{ row.reEnergy.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="totalEnergy" label="Total Energy (MWh)" width="150">
          <template #default="{ row }">
            {{ row.totalEnergy.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="reType" label="RE Type" width="120">
          <template #default="{ row }">
            <el-tag :type="getReTypeTag(row.reType)" size="small">{{ row.reType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="procurementMethod" label="Procurement" width="130">
          <template #default="{ row }">
            <el-tag :type="row.procurementMethod === 'PPA' ? 'success' : 'warning'" size="small">{{ row.procurementMethod }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="carbonAvoided" label="CO₂ Avoided (t)" width="140">
          <template #default="{ row }">
            {{ row.carbonAvoided.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="targetStatus" label="Target" width="120">
          <template #default="{ row }">
            <span :class="row.targetStatus === 'On Track' ? 'metric-good' : (row.targetStatus === 'Ahead' ? 'metric-good' : 'metric-bad')">
              {{ row.targetStatus }}
            </span>
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
          <el-descriptions-item label="RE Ratio">{{ selectedFacility.reRatio }}%</el-descriptions-item>
          <el-descriptions-item label="RE Energy">{{ selectedFacility.reEnergy.toLocaleString() }} MWh</el-descriptions-item>
          <el-descriptions-item label="Total Energy">{{ selectedFacility.totalEnergy.toLocaleString() }} MWh</el-descriptions-item>
          <el-descriptions-item label="RE Type">{{ selectedFacility.reType }}</el-descriptions-item>
          <el-descriptions-item label="Procurement Method">{{ selectedFacility.procurementMethod }}</el-descriptions-item>
          <el-descriptions-item label="CO₂ Avoided">{{ selectedFacility.carbonAvoided.toLocaleString() }} t</el-descriptions-item>
          <el-descriptions-item label="Target Status">{{ selectedFacility.targetStatus }}</el-descriptions-item>
          <el-descriptions-item label="PPA Contract">{{ selectedFacility.ppaContract || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Contract Term" :span="2">{{ selectedFacility.contractTerm || 'N/A' }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <div class="section-title">Monthly RE Performance</div>
          <div class="trend-chart" ref="facilityTrendChartEl"></div>
        </div>

        <div class="detail-section">
          <div class="section-title">RE Source Breakdown</div>
          <div class="trend-chart" ref="sourceBreakdownChartEl"></div>
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
  Sunny, DataLine, TrendCharts, Timer, Download, Refresh,
  RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading renewable energy data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading renewable energy data...',
  'Calculating RE ratios...',
  'Analyzing carbon reduction...',
  'Preparing procurement insights...',
  'Almost ready...'
]

// ==================== Types ====================
interface ReFacility {
  id: number
  facility: string
  reRatio: number
  reEnergy: number
  totalEnergy: number
  reType: string
  procurementMethod: string
  carbonAvoided: number
  targetStatus: string
  ppaContract: string
  contractTerm: string
  recommendation: {
    title: string
    type: 'success' | 'warning' | 'info' | 'error'
    description: string
  }
}

// ==================== Mock Data ====================
const facilities = ['Data Center A', 'Data Center B', 'Data Center C', 'Data Center D', 'Data Center E', 'Office HQ', 'R&D Center']

const generateReData = (): ReFacility[] => {
  const facilitiesData: ReFacility[] = [
    { id: 1, facility: 'Data Center A', reRatio: 42, reEnergy: 18500, totalEnergy: 44000, reType: 'Solar + Wind', procurementMethod: 'PPA', carbonAvoided: 7850, targetStatus: 'On Track', ppaContract: 'Solar PPA - 50MW', contractTerm: '2023-2033',
      recommendation: { title: 'Expand Solar Capacity', type: 'info', description: 'Consider additional solar PPA to increase RE ratio to 50% by 2026.' } },
    { id: 2, facility: 'Data Center B', reRatio: 68, reEnergy: 22500, totalEnergy: 33100, reType: 'Wind + Solar', procurementMethod: 'PPA + RECs', carbonAvoided: 9550, targetStatus: 'Ahead', ppaContract: 'Wind PPA - 75MW', contractTerm: '2022-2032',
      recommendation: { title: 'Industry Leader', type: 'success', description: 'Excellent progress. Share best practices across other facilities.' } },
    { id: 3, facility: 'Data Center C', reRatio: 18, reEnergy: 8500, totalEnergy: 47200, reType: 'RECs only', procurementMethod: 'RECs', carbonAvoided: 3610, targetStatus: 'Behind', ppaContract: 'N/A', contractTerm: 'N/A',
      recommendation: { title: 'Immediate Action Required', type: 'error', description: 'Low RE ratio. Urgently explore PPA or on-site generation options.' } },
    { id: 4, facility: 'Data Center D', reRatio: 35, reEnergy: 11200, totalEnergy: 32000, reType: 'Solar', procurementMethod: 'PPA', carbonAvoided: 4760, targetStatus: 'On Track', ppaContract: 'Solar PPA - 35MW', contractTerm: '2024-2034',
      recommendation: { title: 'Increase Procurement', type: 'warning', description: 'Consider additional RECs to bridge gap to 50% target.' } },
    { id: 5, facility: 'Data Center E', reRatio: 55, reEnergy: 16500, totalEnergy: 30000, reType: 'Wind', procurementMethod: 'PPA', carbonAvoided: 7010, targetStatus: 'On Track', ppaContract: 'Wind PPA - 60MW', contractTerm: '2023-2033',
      recommendation: { title: 'Diversify Sources', type: 'info', description: 'Add solar to diversify renewable portfolio.' } },
    { id: 6, facility: 'Office HQ', reRatio: 85, reEnergy: 6800, totalEnergy: 8000, reType: 'Solar + Wind', procurementMethod: 'On-site + PPA', carbonAvoided: 2890, targetStatus: 'Ahead', ppaContract: 'On-site Solar + PPA', contractTerm: 'N/A',
      recommendation: { title: 'Carbon Neutral Goal', type: 'success', description: 'Near 100% renewable. Explore remaining 15% options.' } },
    { id: 7, facility: 'R&D Center', reRatio: 28, reEnergy: 4200, totalEnergy: 15000, reType: 'RECs', procurementMethod: 'RECs', carbonAvoided: 1785, targetStatus: 'Behind', ppaContract: 'N/A', contractTerm: 'N/A',
      recommendation: { title: 'On-site Assessment', type: 'warning', description: 'Evaluate rooftop solar potential for this facility.' } }
  ]
  return facilitiesData
}

const reData = ref<ReFacility[]>(generateReData())

// ==================== State ====================
const dateRange = ref<Date[] | null>(null)
const facilityFilter = ref('')
const reTypeFilter = ref('')
const yearFilter = ref('2024')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const selectedFacility = ref<ReFacility | null>(null)

// Chart refs
let ratioTrendChart: echarts.ECharts | null = null
let energyMixChart: echarts.ECharts | null = null
let facilityChart: echarts.ECharts | null = null
let sourceChart: echarts.ECharts | null = null
let carbonChart: echarts.ECharts | null = null
let progressChart: echarts.ECharts | null = null
let procurementChart: echarts.ECharts | null = null
let facilityTrendChart: echarts.ECharts | null = null
let sourceBreakdownChart: echarts.ECharts | null = null

const ratioTrendChartEl = ref<HTMLElement | null>(null)
const energyMixChartEl = ref<HTMLElement | null>(null)
const facilityChartEl = ref<HTMLElement | null>(null)
const sourceChartEl = ref<HTMLElement | null>(null)
const carbonChartEl = ref<HTMLElement | null>(null)
const progressChartEl = ref<HTMLElement | null>(null)
const procurementChartEl = ref<HTMLElement | null>(null)
const facilityTrendChartEl = ref<HTMLElement | null>(null)
const sourceBreakdownChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  const totalReEnergy = reData.value.reduce((sum, d) => sum + d.reEnergy, 0)
  const totalEnergy = reData.value.reduce((sum, d) => sum + d.totalEnergy, 0)
  const renewableRatio = (totalReEnergy / totalEnergy * 100).toFixed(0)
  const totalCarbonAvoided = reData.value.reduce((sum, d) => sum + d.carbonAvoided, 0) / 1000
  const avgRatio = parseFloat(renewableRatio)

  return {
    renewableRatio: avgRatio,
    ratioGrowth: 8.5,
    renewableEnergy: (totalReEnergy / 1000).toFixed(0),
    carbonAvoided: totalCarbonAvoided.toFixed(0),
    carbonGrowth: 12.3,
    reProgress: Math.round(avgRatio / 100 * 100)
  }
})

const metrics = computed(() => {
  const totalEnergy = reData.value.reduce((sum, d) => sum + d.totalEnergy, 0) / 1000
  const totalReCost = 18.5
  const totalRecs = 125
  const ppaCapacity = 185

  return {
    totalEnergy: totalEnergy.toFixed(0),
    energyTrend: 3.2,
    reCost: totalReCost,
    costPerMWh: 45,
    recs: totalRecs,
    ppaCapacity: ppaCapacity
  }
})

const filteredData = computed(() => {
  let filtered = [...reData.value]

  if (facilityFilter.value) {
    filtered = filtered.filter(d => d.facility === facilityFilter.value)
  }

  if (reTypeFilter.value === 'solar') {
    filtered = filtered.filter(d => d.reType.toLowerCase().includes('solar'))
  } else if (reTypeFilter.value === 'wind') {
    filtered = filtered.filter(d => d.reType.toLowerCase().includes('wind'))
  } else if (reTypeFilter.value === 'hydro') {
    filtered = filtered.filter(d => d.reType.toLowerCase().includes('hydro'))
  } else if (reTypeFilter.value === 'biomass') {
    filtered = filtered.filter(d => d.reType.toLowerCase().includes('biomass'))
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
const getRatioColor = (ratio: number): string => {
  if (ratio >= 50) return '#22c55e'
  if (ratio >= 30) return '#f59e0b'
  return '#ef4444'
}

const getReTypeTag = (type: string): string => {
  if (type.includes('Solar')) return 'warning'
  if (type.includes('Wind')) return 'info'
  if (type.includes('Hydro')) return 'primary'
  return 'success'
}

const resetFilters = () => {
  facilityFilter.value = ''
  reTypeFilter.value = ''
  dateRange.value = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

// ==================== Chart Functions ====================
const initRatioTrendChart = () => {
  if (!ratioTrendChartEl.value) return
  if (ratioTrendChart) {
    ratioTrendChart.dispose()
    ratioTrendChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const ratio2024 = [38, 39, 41, 42, 43, 44, 46, 47, 48, 49, 50, 51]
  const ratio2023 = [32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43]
  const ratio2022 = [26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37]

  let dataToShow = ratio2024
  if (yearFilter.value === '2023') dataToShow = ratio2023
  if (yearFilter.value === '2022') dataToShow = ratio2022

  ratioTrendChart = echarts.init(ratioTrendChartEl.value)
  ratioTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 60, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Renewable Ratio (%)', min: 20, max: 60 },
    series: [{
      type: 'line',
      data: dataToShow,
      smooth: true,
      lineStyle: { color: '#22c55e', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initEnergyMixChart = () => {
  if (!energyMixChartEl.value) return
  if (energyMixChart) {
    energyMixChart.dispose()
    energyMixChart = null
  }

  const totalRe = reData.value.reduce((sum, d) => sum + d.reEnergy, 0)
  const totalNonRe = reData.value.reduce((sum, d) => sum + d.totalEnergy, 0) - totalRe

  energyMixChart = echarts.init(energyMixChartEl.value)
  energyMixChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} MWh ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: ['Renewable Energy', 'Non-renewable'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: totalRe, name: 'Renewable Energy', itemStyle: { color: '#22c55e' } },
        { value: totalNonRe, name: 'Non-renewable', itemStyle: { color: '#94a3b8' } }
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

  const names = reData.value.map(d => d.facility)
  const ratios = reData.value.map(d => d.reRatio)

  facilityChart = echarts.init(facilityChartEl.value)
  facilityChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 40, containLabel: true },
    xAxis: { type: 'category', data: names, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: 'RE Ratio (%)', max: 100 },
    series: [{
      type: 'bar',
      data: ratios,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value >= 50) return '#22c55e'
          if (value >= 30) return '#f59e0b'
          return '#ef4444'
        }
      },
      label: { show: true, position: 'top', formatter: '{c}%' },
      markLine: {
        data: [{ yAxis: 50, name: '50% Target' }, { yAxis: 100, name: '100% Target' }],
        lineStyle: { type: 'dashed' },
        label: { show: true }
      }
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
    tooltip: { trigger: 'item', formatter: '{b}: {c} MWh ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: ['Solar', 'Wind', 'Hydro', 'Biomass', 'RECs'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: 18500, name: 'Solar', itemStyle: { color: '#f59e0b' } },
        { value: 22500, name: 'Wind', itemStyle: { color: '#3b82f6' } },
        { value: 8500, name: 'Hydro', itemStyle: { color: '#22c55e' } },
        { value: 3200, name: 'Biomass', itemStyle: { color: '#8b5cf6' } },
        { value: 6800, name: 'RECs', itemStyle: { color: '#0ea5e9' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const initCarbonChart = () => {
  if (!carbonChartEl.value) return
  if (carbonChart) {
    carbonChart.dispose()
    carbonChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const carbonData = [1850, 1920, 2100, 2250, 2400, 2580, 2720, 2850, 2980, 3120, 3250, 3400]

  carbonChart = echarts.init(carbonChartEl.value)
  carbonChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 60, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'CO₂ Avoided (t)' },
    series: [{
      type: 'line',
      data: carbonData,
      smooth: true,
      lineStyle: { color: '#22c55e', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 },
      label: { show: true, position: 'top', formatter: '{c} t' }
    }]
  })
}

const initProgressChart = () => {
  if (!progressChartEl.value) return
  if (progressChart) {
    progressChart.dispose()
    progressChart = null
  }

  const years = ['2024', '2025', '2026', '2027', '2028', '2029', '2030']
  const actual = [42, null, null, null, null, null, null]
  const target = [42, 50, 58, 66, 74, 82, 100]

  progressChart = echarts.init(progressChartEl.value)
  progressChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Actual', 'Target'], bottom: 0 },
    grid: { top: 30, left: 60, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: years },
    yAxis: { type: 'value', name: 'RE Ratio (%)', max: 100 },
    series: [
      { name: 'Actual', type: 'bar', data: actual, itemStyle: { color: '#22c55e', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top', formatter: '{c}%' } },
      { name: 'Target', type: 'line', data: target, lineStyle: { color: '#3b82f6', width: 3, type: 'dashed' }, symbol: 'diamond' }
    ]
  })
}

const initProcurementChart = () => {
  if (!procurementChartEl.value) return
  if (procurementChart) {
    procurementChart.dispose()
    procurementChart = null
  }

  procurementChart = echarts.init(procurementChartEl.value)
  procurementChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} MWh ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: ['PPA (Direct)', 'RECs', 'On-site Generation'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: 48500, name: 'PPA (Direct)', itemStyle: { color: '#3b82f6' } },
        { value: 12500, name: 'RECs', itemStyle: { color: '#f59e0b' } },
        { value: 8500, name: 'On-site Generation', itemStyle: { color: '#22c55e' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
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
  const ratios = [38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49]

  facilityTrendChart = echarts.init(facilityTrendChartEl.value)
  facilityTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 60, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'RE Ratio (%)' },
    series: [{
      type: 'line',
      data: ratios,
      smooth: true,
      lineStyle: { color: '#22c55e', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initSourceBreakdownChart = () => {
  if (!sourceBreakdownChartEl.value || !selectedFacility.value) return
  if (sourceBreakdownChart) {
    sourceBreakdownChart.dispose()
    sourceBreakdownChart = null
  }

  const sources = ['Solar', 'Wind', 'Hydro', 'RECs']
  const values = [45, 35, 10, 10]

  sourceBreakdownChart = echarts.init(sourceBreakdownChartEl.value)
  sourceBreakdownChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
    legend: { orient: 'vertical', left: 'left', data: sources },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: sources.map((s, i) => ({ name: s, value: values[i] })),
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const updateRatioTrend = () => {
  initRatioTrendChart()
}

const refreshCharts = () => {
  nextTick(() => {
    initRatioTrendChart()
    initEnergyMixChart()
    initFacilityChart()
    initSourceChart()
    initCarbonChart()
    initProgressChart()
    initProcurementChart()
  })
}

// ==================== Actions ====================
const viewFacilityDetail = (facility: ReFacility) => {
  selectedFacility.value = facility
  detailDialogVisible.value = true
  nextTick(() => {
    initFacilityTrendChart()
    initSourceBreakdownChart()
  })
}

const viewAllData = () => {
  ElMessage.info('Viewing all facilities')
}

const exportFacilityReport = (facility: ReFacility | null) => {
  if (facility) {
    ElMessage.success(`Exporting report for ${facility.facility}...`)
    setTimeout(() => {
      ElMessage.success('Report generated successfully')
    }, 1500)
  }
}

const exportData = () => {
  ElMessage.success('Exporting renewable energy data...')
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
    const charts = [ratioTrendChart, energyMixChart, facilityChart, sourceChart, carbonChart, progressChart, procurementChart, facilityTrendChart, sourceBreakdownChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([facilityFilter, reTypeFilter, dateRange], () => {
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
  const charts = [ratioTrendChart, energyMixChart, facilityChart, sourceChart, carbonChart, progressChart, procurementChart, facilityTrendChart, sourceBreakdownChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.renewable-energy-page {
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

.stat-icon.green { background: #dcfce7; color: #22c55e; }
.stat-icon.blue { background: #eef2ff; color: #3b82f6; }
.stat-icon.orange { background: #fef3c7; color: #f59e0b; }
.stat-icon.purple { background: #f3e8ff; color: #8b5cf6; }

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
  height: 280px;
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
  border-left: 3px solid #22c55e;
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
  background: #22c55e;
  border-color: #22c55e;
}
:deep(.el-button--primary:hover) {
  background: #16a34a;
}
:deep(.el-pagination.is-background .el-pager li.is-active) {
  background-color: #22c55e;
}
:deep(.el-dialog__body) {
  max-height: 550px;
  overflow-y: auto;
}
:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}
</style>