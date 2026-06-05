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
          <span class="loading-title">Green Finance Metrics</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Sustainable Finance & Green Investment Tracking</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="green-finance-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Money /></el-icon>
          Green Finance Metrics
        </h1>
        <div class="page-subtitle">Track green bonds, sustainability-linked loans, and ESG investment performance</div>
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
          <el-icon><Connection /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">${{ stats.greenBonds }}<span class="stat-unit">B</span></div>
          <div class="stat-label">Green Bonds Issued</div>
          <div class="stat-trend up">↑ {{ stats.bondsGrowth }}% YoY</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">${{ stats.sustainabilityLoans }}<span class="stat-unit">B</span></div>
          <div class="stat-label">Sustainability Loans</div>
          <div class="stat-trend up">↑ {{ stats.loansGrowth }}% YoY</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.esgFunds }}<span class="stat-unit">B</span></div>
          <div class="stat-label">ESG Funds Under Management</div>
          <div class="stat-trend up">↑ {{ stats.fundsGrowth }}% YoY</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.greenProjects }}<span class="stat-unit"></span></div>
          <div class="stat-label">Green Projects Funded</div>
          <div class="stat-trend up">+{{ stats.projectsGrowth }} this year</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Average Green Bond Yield</div>
        <div class="metric-value">{{ metrics.bondYield }}<span class="metric-unit">%</span></div>
        <div class="metric-trend positive">vs {{ metrics.conventionalYield }}% conventional</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">ESG Fund Performance</div>
        <div class="metric-value">{{ metrics.esgPerformance }}<span class="metric-unit">%</span></div>
        <el-progress :percentage="metrics.esgPerformance" :stroke-width="8" :color="metrics.esgPerformance > 12 ? '#22c55e' : (metrics.esgPerformance > 8 ? '#f59e0b' : '#ef4444')" />
      </div>
      <div class="metric-card">
        <div class="metric-title">Carbon Price Impact</div>
        <div class="metric-value">${{ metrics.carbonPrice }}<span class="metric-unit">/t</span></div>
        <div class="metric-trend up">↑ {{ metrics.carbonPriceGrowth }}% YoY</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Taxononomy Alignment</div>
        <div class="metric-value">{{ metrics.taxonomyAlignment }}<span class="metric-unit">%</span></div>
        <el-progress :percentage="metrics.taxonomyAlignment" :stroke-width="8" :color="metrics.taxonomyAlignment > 80 ? '#22c55e' : (metrics.taxonomyAlignment > 60 ? '#f59e0b' : '#ef4444')" />
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card large">
        <div class="chart-header">
          <span class="chart-title">Green Finance Portfolio</span>
          <span class="chart-subtitle">Allocation by instrument</span>
        </div>
        <div class="chart-container" ref="portfolioChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Green Bond Allocation</span>
          <span class="chart-subtitle">Use of proceeds</span>
        </div>
        <div class="chart-container" ref="allocationChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">ESG Fund Performance Trend</span>
          <span class="chart-subtitle">Last 12 months</span>
        </div>
        <div class="chart-container" ref="performanceChartEl"></div>
      </div>
    </div>

    <!-- Third Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Emissions Reduction by Project</span>
          <span class="chart-subtitle">Funded initiatives</span>
        </div>
        <div class="chart-container" ref="emissionsChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Impact Metrics</span>
          <span class="chart-subtitle">KPIs by category</span>
        </div>
        <div class="chart-container" ref="impactChartEl"></div>
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
        <el-select v-model="instrumentFilter" placeholder="Instrument" clearable style="width: 150px">
          <el-option label="Green Bond" value="bond" />
          <el-option label="Sustainability Loan" value="loan" />
          <el-option label="ESG Fund" value="fund" />
        </el-select>
        <el-select v-model="sectorFilter" placeholder="Sector" clearable style="width: 140px">
          <el-option label="Renewable Energy" value="renewable" />
          <el-option label="Energy Efficiency" value="efficiency" />
          <el-option label="Transport" value="transport" />
          <el-option label="Water" value="water" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Green Finance Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Green Finance Instruments</span>
        <el-button size="small" @click="viewAllInstruments">View All →</el-button>
      </div>
      <el-table :data="paginatedInstruments" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="name" label="Instrument Name" min-width="200" />
        <el-table-column prop="type" label="Type" width="140">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.type)" size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="Amount" width="140">
          <template #default="{ row }">
            ${{ row.amount.toLocaleString() }}M
          </template>
        </el-table-column>
        <el-table-column prop="issueDate" label="Issue Date" width="120" />
        <el-table-column prop="maturityDate" label="Maturity" width="120" />
        <el-table-column prop="coupon" label="Coupon/Rate" width="100">
          <template #default="{ row }">
            {{ row.coupon }}%
          </template>
        </el-table-column>
        <el-table-column prop="useOfProceeds" label="Use of Proceeds" min-width="200" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Active' ? 'success' : 'info'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewInstrumentDetail(row)">Details</el-button>
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
    <el-dialog v-model="detailDialogVisible" :title="selectedInstrument?.name" width="800px">
      <div v-if="selectedInstrument" class="instrument-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Instrument Type">{{ selectedInstrument.type }}</el-descriptions-item>
          <el-descriptions-item label="Amount">${{ selectedInstrument.amount.toLocaleString() }}M</el-descriptions-item>
          <el-descriptions-item label="Issue Date">{{ selectedInstrument.issueDate }}</el-descriptions-item>
          <el-descriptions-item label="Maturity Date">{{ selectedInstrument.maturityDate }}</el-descriptions-item>
          <el-descriptions-item label="Coupon/Rate">{{ selectedInstrument.coupon }}%</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="selectedInstrument.status === 'Active' ? 'success' : 'info'" size="small">{{ selectedInstrument.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Use of Proceeds" :span="2">{{ selectedInstrument.useOfProceeds }}</el-descriptions-item>
          <el-descriptions-item label="Framework" :span="2">{{ selectedInstrument.framework }}</el-descriptions-item>
          <el-descriptions-item label="External Review" :span="2">{{ selectedInstrument.externalReview }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <div class="section-title">Impact Metrics</div>
          <el-table :data="selectedInstrument.impactMetrics" border stripe>
            <el-table-column prop="metric" label="Metric" width="250" />
            <el-table-column prop="value" label="Value" width="150" />
            <el-table-column prop="unit" label="Unit" width="100" />
            <el-table-column prop="description" label="Description" min-width="200" />
          </el-table>
        </div>

        <div class="detail-section">
          <div class="section-title">Allocation Status</div>
          <div class="trend-chart" ref="allocationDetailChartEl"></div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="exportReport(selectedInstrument)">Export Report</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Money, Connection, Document, TrendCharts, Timer, Download, Refresh,
  RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading green finance metrics...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading finance data...',
  'Calculating impact metrics...',
  'Analyzing portfolio performance...',
  'Preparing report...',
  'Almost ready...'
]

// ==================== Types ====================
interface ImpactMetric {
  metric: string
  value: number
  unit: string
  description: string
}

interface FinanceInstrument {
  id: number
  name: string
  type: string
  amount: number
  issueDate: string
  maturityDate: string
  coupon: number
  useOfProceeds: string
  framework: string
  externalReview: string
  status: string
  impactMetrics: ImpactMetric[]
}

// ==================== Mock Data ====================
const stats = {
  greenBonds: 2.5,
  bondsGrowth: 15,
  sustainabilityLoans: 1.8,
  loansGrowth: 22,
  esgFunds: 3.2,
  fundsGrowth: 18,
  greenProjects: 47,
  projectsGrowth: 12
}

const metrics = {
  bondYield: 4.2,
  conventionalYield: 4.8,
  esgPerformance: 14.5,
  carbonPrice: 85,
  carbonPriceGrowth: 12,
  taxonomyAlignment: 76
}

const instruments: FinanceInstrument[] = [
  {
    id: 1, name: 'Green Bond 2024-A', type: 'Green Bond', amount: 500, issueDate: '2024-01-15',
    maturityDate: '2034-01-15', coupon: 4.25, useOfProceeds: 'Renewable energy projects including solar and wind farms',
    framework: 'ICMA Green Bond Principles', externalReview: 'Sustainalytics Second Party Opinion', status: 'Active',
    impactMetrics: [
      { metric: 'Renewable Energy Capacity', value: 250, unit: 'MW', description: 'Solar and wind projects' },
      { metric: 'Annual CO₂ Reduction', value: 125000, unit: 'tCO₂e', description: 'Estimated annual emissions reduction' },
      { metric: 'Homes Powered', value: 75000, unit: 'homes', description: 'Equivalent households powered' }
    ]
  },
  {
    id: 2, name: 'Sustainability-Linked Loan - Facility A', type: 'Sustainability Loan', amount: 350, issueDate: '2023-06-01',
    maturityDate: '2028-06-01', coupon: 3.75, useOfProceeds: 'General corporate purposes with KPI-linked margin adjustment',
    framework: 'Sustainability-Linked Loan Principles', externalReview: 'EcoVadis Assessment', status: 'Active',
    impactMetrics: [
      { metric: 'Emission Reduction Target', value: 35, unit: '%', description: 'Reduction by 2028 vs 2022 baseline' },
      { metric: 'Renewable Energy Usage', value: 60, unit: '%', description: 'Target for 2028' },
      { metric: 'Water Intensity Reduction', value: 25, unit: '%', description: 'Reduction by 2028 vs 2022 baseline' }
    ]
  },
  {
    id: 3, name: 'ESG Infrastructure Fund', type: 'ESG Fund', amount: 1200, issueDate: '2022-09-01',
    maturityDate: '2032-09-01', coupon: 0, useOfProceeds: 'Infrastructure investments with ESG criteria',
    framework: 'SFDR Article 9', externalReview: 'PRI Signatory', status: 'Active',
    impactMetrics: [
      { metric: 'AUM Growth', value: 18, unit: '%', description: 'Year-over-year growth' },
      { metric: 'Portfolio Companies', value: 24, unit: 'companies', description: 'Active investments' },
      { metric: 'Average ESG Score', value: 82, unit: 'points', description: 'Portfolio average' }
    ]
  },
  {
    id: 4, name: 'Green Bond 2023-B', type: 'Green Bond', amount: 750, issueDate: '2023-03-10',
    maturityDate: '2033-03-10', coupon: 4.5, useOfProceeds: 'Energy efficiency retrofits and sustainable buildings',
    framework: 'ICMA Green Bond Principles', externalReview: 'CICERO Shades of Green', status: 'Active',
    impactMetrics: [
      { metric: 'Building Retrofits', value: 45, unit: 'buildings', description: 'Energy efficiency upgrades' },
      { metric: 'Energy Savings', value: 185000, unit: 'MWh/year', description: 'Annual energy reduction' },
      { metric: 'CO₂ Reduction', value: 78000, unit: 'tCO₂e', description: 'Annual emissions reduction' }
    ]
  },
  {
    id: 5, name: 'Water Conservation Bond', type: 'Green Bond', amount: 300, issueDate: '2024-02-20',
    maturityDate: '2029-02-20', coupon: 4.0, useOfProceeds: 'Water treatment and conservation projects',
    framework: 'ICMA Green Bond Principles', externalReview: 'Vigeo Eiris', status: 'Active',
    impactMetrics: [
      { metric: 'Water Savings', value: 5000, unit: 'm³/day', description: 'Daily water conservation' },
      { metric: 'Population Served', value: 250000, unit: 'people', description: 'Beneficiaries' },
      { metric: 'Treatment Capacity', value: 50, unit: 'ML/day', description: 'New capacity added' }
    ]
  },
  {
    id: 6, name: 'Clean Transport Loan', type: 'Sustainability Loan', amount: 280, issueDate: '2023-11-15',
    maturityDate: '2028-11-15', coupon: 4.1, useOfProceeds: 'Electric vehicle fleet expansion',
    framework: 'Green Loan Principles', externalReview: 'DNV GL', status: 'Active',
    impactMetrics: [
      { metric: 'EV Fleet Size', value: 350, unit: 'vehicles', description: 'New EV additions' },
      { metric: 'Emissions Reduction', value: 8500, unit: 'tCO₂e', description: 'Annual reduction' },
      { metric: 'Fuel Savings', value: 250000, unit: 'liters/year', description: 'Diesel displaced' }
    ]
  },
  {
    id: 7, name: 'Renewable Energy Fund II', type: 'ESG Fund', amount: 850, issueDate: '2023-07-01',
    maturityDate: '2033-07-01', coupon: 0, useOfProceeds: 'Solar and wind project development',
    framework: 'SFDR Article 8', externalReview: 'UN PRI', status: 'Active',
    impactMetrics: [
      { metric: 'Projects Funded', value: 18, unit: 'projects', description: 'Active investments' },
      { metric: 'Capacity Added', value: 420, unit: 'MW', description: 'Renewable capacity' },
      { metric: 'Emissions Avoided', value: 210000, unit: 'tCO₂e', description: 'Annual reduction' }
    ]
  },
  {
    id: 8, name: 'Circular Economy Bond', type: 'Green Bond', amount: 200, issueDate: '2024-04-05',
    maturityDate: '2029-04-05', coupon: 4.35, useOfProceeds: 'Waste reduction and recycling facilities',
    framework: 'ICMA Green Bond Principles', externalReview: 'Sustainalytics', status: 'Active',
    impactMetrics: [
      { metric: 'Waste Diverted', value: 120000, unit: 'tons/year', description: 'From landfill' },
      { metric: 'Recycling Capacity', value: 80000, unit: 'tons/year', description: 'New capacity' },
      { metric: 'Jobs Created', value: 85, unit: 'jobs', description: 'Direct employment' }
    ]
  }
]

// ==================== State ====================
const dateRange = ref<Date[] | null>(null)
const instrumentFilter = ref('')
const sectorFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const selectedInstrument = ref<FinanceInstrument | null>(null)

// Chart refs
let portfolioChart: echarts.ECharts | null = null
let allocationChart: echarts.ECharts | null = null
let performanceChart: echarts.ECharts | null = null
let emissionsChart: echarts.ECharts | null = null
let impactChart: echarts.ECharts | null = null
let allocationDetailChart: echarts.ECharts | null = null

const portfolioChartEl = ref<HTMLElement | null>(null)
const allocationChartEl = ref<HTMLElement | null>(null)
const performanceChartEl = ref<HTMLElement | null>(null)
const emissionsChartEl = ref<HTMLElement | null>(null)
const impactChartEl = ref<HTMLElement | null>(null)
const allocationDetailChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const filteredInstruments = computed(() => {
  let filtered = [...instruments]

  if (instrumentFilter.value === 'bond') {
    filtered = filtered.filter(i => i.type === 'Green Bond')
  } else if (instrumentFilter.value === 'loan') {
    filtered = filtered.filter(i => i.type === 'Sustainability Loan')
  } else if (instrumentFilter.value === 'fund') {
    filtered = filtered.filter(i => i.type === 'ESG Fund')
  }

  if (sectorFilter.value) {
    // Filter logic would go here
  }

  if (dateRange.value && dateRange.value.length === 2) {
    // Filter logic would go here
  }

  return filtered
})

const totalRecords = computed(() => filteredInstruments.value.length)

const paginatedInstruments = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredInstruments.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getTypeTagType = (type: string): string => {
  const map: Record<string, string> = { 'Green Bond': 'success', 'Sustainability Loan': 'primary', 'ESG Fund': 'warning' }
  return map[type] || 'info'
}

const resetFilters = () => {
  instrumentFilter.value = ''
  sectorFilter.value = ''
  dateRange.value = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

// ==================== Chart Functions ====================
const initPortfolioChart = () => {
  if (!portfolioChartEl.value) return
  if (portfolioChart) {
    portfolioChart.dispose()
    portfolioChart = null
  }

  portfolioChart = echarts.init(portfolioChartEl.value)
  portfolioChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: ${c}M ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: ['Green Bonds', 'Sustainability Loans', 'ESG Funds'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: 1750, name: 'Green Bonds', itemStyle: { color: '#22c55e' } },
        { value: 630, name: 'Sustainability Loans', itemStyle: { color: '#3b82f6' } },
        { value: 2050, name: 'ESG Funds', itemStyle: { color: '#f59e0b' } }
      ],
      label: { show: true, formatter: '{b}: ${c}M' },
      emphasis: { scale: true }
    }]
  })
}

const initAllocationChart = () => {
  if (!allocationChartEl.value) return
  if (allocationChart) {
    allocationChart.dispose()
    allocationChart = null
  }

  allocationChart = echarts.init(allocationChartEl.value)
  allocationChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
    legend: { orient: 'vertical', left: 'left', data: ['Renewable Energy', 'Energy Efficiency', 'Clean Transport', 'Water', 'Circular Economy'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: 45, name: 'Renewable Energy', itemStyle: { color: '#22c55e' } },
        { value: 20, name: 'Energy Efficiency', itemStyle: { color: '#3b82f6' } },
        { value: 15, name: 'Clean Transport', itemStyle: { color: '#f59e0b' } },
        { value: 10, name: 'Water', itemStyle: { color: '#0ea5e9' } },
        { value: 10, name: 'Circular Economy', itemStyle: { color: '#8b5cf6' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const initPerformanceChart = () => {
  if (!performanceChartEl.value) return
  if (performanceChart) {
    performanceChart.dispose()
    performanceChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const esgFundData = [8.2, 7.8, 9.1, 10.5, 11.2, 12.8, 13.5, 12.9, 13.2, 14.1, 14.8, 14.5]
  const benchmarkData = [7.5, 7.2, 8.0, 8.8, 9.2, 10.1, 10.5, 10.2, 10.5, 11.2, 11.8, 11.5]

  performanceChart = echarts.init(performanceChartEl.value)
  performanceChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['ESG Fund Performance', 'Benchmark'], bottom: 0 },
    grid: { top: 40, left: 60, right: 30, bottom: 40 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Return (%)' },
    series: [
      { name: 'ESG Fund Performance', type: 'line', data: esgFundData, lineStyle: { color: '#22c55e', width: 3 }, symbol: 'circle', areaStyle: { opacity: 0.1 } },
      { name: 'Benchmark', type: 'line', data: benchmarkData, lineStyle: { color: '#94a3b8', width: 2, type: 'dashed' }, symbol: 'diamond' }
    ]
  })
}

const initEmissionsChart = () => {
  if (!emissionsChartEl.value) return
  if (emissionsChart) {
    emissionsChart.dispose()
    emissionsChart = null
  }

  const projects = ['Solar Farm', 'Wind Project', 'EV Fleet', 'Building Retrofit', 'Recycling Facility']
  const emissions = [85000, 65000, 8500, 78000, 45000]

  emissionsChart = echarts.init(emissionsChartEl.value)
  emissionsChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: projects, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'CO₂ Reduction (tCO₂e/year)' },
    series: [{
      type: 'bar',
      data: emissions,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#22c55e' },
      label: { show: true, position: 'top', formatter: '{c} t' }
    }]
  })
}

const initImpactChart = () => {
  if (!impactChartEl.value) return
  if (impactChart) {
    impactChart.dispose()
    impactChart = null
  }

  const metrics = ['CO₂ Reduction', 'Energy Saved', 'Water Saved', 'Waste Diverted', 'Jobs Created']
  const values = [685000, 185000, 5000, 120000, 85]
  const units = ['tCO₂e', 'MWh', 'm³/day', 'tons', 'jobs']

  impactChart = echarts.init(impactChartEl.value)
  impactChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: (params: any) => {
        return `${params[0].name}<br/>Value: ${params[0].value.toLocaleString()} ${units[params[0].dataIndex]}`
      } },
    grid: { top: 30, left: 60, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: metrics, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'Impact Value' },
    series: [{
      type: 'bar',
      data: values,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#3b82f6' },
      label: { show: true, position: 'top', formatter: (params: any) => {
          return params.value.toLocaleString() + ' ' + units[params.dataIndex]
        } }
    }]
  })
}

const initAllocationDetailChart = () => {
  if (!allocationDetailChartEl.value || !selectedInstrument.value) return
  if (allocationDetailChart) {
    allocationDetailChart.dispose()
    allocationDetailChart = null
  }

  allocationDetailChart = echarts.init(allocationDetailChartEl.value)
  allocationDetailChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: ['Allocated', 'Unallocated', 'Committed'] },
    yAxis: { type: 'value', name: 'Amount ($M)' },
    series: [{
      type: 'bar',
      data: [selectedInstrument.value.amount * 0.85, selectedInstrument.value.amount * 0.1, selectedInstrument.value.amount * 0.05],
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#22c55e' },
      label: { show: true, position: 'top', formatter: '${c}M' }
    }]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initPortfolioChart()
    initAllocationChart()
    initPerformanceChart()
    initEmissionsChart()
    initImpactChart()
  })
}

// ==================== Actions ====================
const viewInstrumentDetail = (instrument: FinanceInstrument) => {
  selectedInstrument.value = instrument
  detailDialogVisible.value = true
  nextTick(() => initAllocationDetailChart())
}

const viewAllInstruments = () => {
  ElMessage.info('Viewing all instruments')
}

const exportReport = (instrument: FinanceInstrument | null) => {
  if (instrument) {
    ElMessage.success(`Exporting report for ${instrument.name}...`)
    setTimeout(() => {
      ElMessage.success('Report generated successfully')
    }, 1500)
  }
}

const exportData = () => {
  ElMessage.success('Exporting green finance data...')
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
    const charts = [portfolioChart, allocationChart, performanceChart, emissionsChart, impactChart, allocationDetailChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([instrumentFilter, sectorFilter, dateRange], () => {
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
  const charts = [portfolioChart, allocationChart, performanceChart, emissionsChart, impactChart, allocationDetailChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.green-finance-page {
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

/* Instrument Detail */
.instrument-detail {
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