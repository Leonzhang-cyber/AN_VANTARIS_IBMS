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
          <span class="loading-title">Scope 3 Emissions</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Value Chain GHG Emissions Tracking & Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="scope3-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Connection /></el-icon>
          Scope 3 Emissions
        </h1>
        <div class="page-subtitle">Other indirect emissions across the value chain</div>
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
          <el-icon><Connection /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalEmissions }}<span class="stat-unit">tCO₂e</span></div>
          <div class="stat-label">Total Scope 3 Emissions</div>
          <div class="stat-trend" :class="stats.emissionsTrend > 0 ? 'up' : 'down'">
            {{ stats.emissionsTrend > 0 ? '↑' : '↓' }} {{ Math.abs(stats.emissionsTrend) }}% vs last year
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><ShoppingCart /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.purchasedGoods }}<span class="stat-unit">tCO₂e</span></div>
          <div class="stat-label">Purchased Goods</div>
          <div class="stat-trend">{{ stats.purchasedPercent }}% of total</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Van /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.transportation }}<span class="stat-unit">tCO₂e</span></div>
          <div class="stat-label">Transportation</div>
          <div class="stat-trend">{{ stats.transportPercent }}% of total</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><Suitcase /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.businessTravel }}<span class="stat-unit">tCO₂e</span></div>
          <div class="stat-label">Business Travel</div>
          <div class="stat-trend">{{ stats.travelPercent }}% of total</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Top Category</div>
        <div class="metric-value">{{ metrics.topCategory }}</div>
        <div class="metric-sub">{{ metrics.topPercentage }}% of total emissions</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Data Completeness</div>
        <div class="metric-value">{{ metrics.dataCompleteness }}<span class="metric-unit">%</span></div>
        <el-progress :percentage="metrics.dataCompleteness" :stroke-width="8" :color="metrics.dataCompleteness > 80 ? '#22c55e' : (metrics.dataCompleteness > 50 ? '#f59e0b' : '#ef4444')" />
      </div>
      <div class="metric-card">
        <div class="metric-title">Supplier Engagement</div>
        <div class="metric-value">{{ metrics.supplierEngagement }}<span class="metric-unit">%</span></div>
        <div class="metric-sub">{{ metrics.activeSuppliers }} suppliers reporting</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Employee Commute</div>
        <div class="metric-value">{{ metrics.commuteEmissions }}<span class="metric-unit">tCO₂e</span></div>
        <div class="metric-sub">{{ metrics.commutePerEmployee }} t/employee</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card large">
        <div class="chart-header">
          <span class="chart-title">Scope 3 Emissions by Category</span>
          <span class="chart-subtitle">15 categories breakdown</span>
        </div>
        <div class="chart-container" ref="categoryChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Emissions by Category</span>
          <span class="chart-subtitle">Top 8 categories</span>
        </div>
        <div class="chart-container" ref="topCategoriesChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Supplier Emissions</span>
          <span class="chart-subtitle">Top 10 suppliers</span>
        </div>
        <div class="chart-container" ref="supplierChartEl"></div>
      </div>
    </div>

    <!-- Third Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Business Travel Breakdown</span>
          <span class="chart-subtitle">Air vs Rail vs Car</span>
        </div>
        <div class="chart-container" ref="travelChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Waste Disposal</span>
          <span class="chart-subtitle">Waste by type</span>
        </div>
        <div class="chart-container" ref="wasteChartEl"></div>
      </div>
    </div>

    <!-- Fourth Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Emissions Trend by Category</span>
          <span class="chart-subtitle">Year-over-year comparison</span>
        </div>
        <div class="chart-container" ref="trendChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Reduction Opportunities</span>
          <span class="chart-subtitle">Potential savings by category</span>
        </div>
        <div class="chart-container" ref="reductionChartEl"></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by category or supplier..."
            style="width: 220px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="categoryFilter" placeholder="Category" clearable style="width: 180px">
          <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
        </el-select>
        <el-select v-model="yearFilter" placeholder="Year" clearable style="width: 100px">
          <el-option label="2024" value="2024" />
          <el-option label="2023" value="2023" />
          <el-option label="2022" value="2022" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Scope 3 Data Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Scope 3 Categories Details</span>
        <el-button size="small" @click="viewAllCategories">View All →</el-button>
      </div>
      <el-table :data="paginatedCategories" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="category" label="Category" min-width="250" />
        <el-table-column prop="emissions" label="Emissions (tCO₂e)" width="150">
          <template #default="{ row }">
            {{ row.emissions.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="percentage" label="Percentage" width="120">
          <template #default="{ row }">
            <el-progress :percentage="row.percentage" :stroke-width="8" :color="getPercentColor(row.percentage)" />
          </template>
        </el-table-column>
        <el-table-column prop="yearOverYear" label="YoY Change" width="110">
          <template #default="{ row }">
            <span :class="row.yearOverYear < 0 ? 'metric-good' : 'metric-bad'">
              {{ row.yearOverYear > 0 ? '+' : '' }}{{ row.yearOverYear }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="dataQuality" label="Data Quality" width="120">
          <template #default="{ row }">
            <el-tag :type="getQualityTagType(row.dataQuality)" size="small">{{ row.dataQuality }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="calculationMethod" label="Method" width="150">
          <template #default="{ row }">
            <span>{{ row.calculationMethod }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewCategoryDetail(row)">Details</el-button>
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

    <!-- Category Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedCategory?.category" width="850px">
      <div v-if="selectedCategory" class="category-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Category">{{ selectedCategory.category }}</el-descriptions-item>
          <el-descriptions-item label="Emissions">{{ selectedCategory.emissions.toLocaleString() }} tCO₂e</el-descriptions-item>
          <el-descriptions-item label="Percentage">{{ selectedCategory.percentage }}% of total</el-descriptions-item>
          <el-descriptions-item label="YoY Change">
            <span :class="selectedCategory.yearOverYear < 0 ? 'metric-good' : 'metric-bad'">
              {{ selectedCategory.yearOverYear > 0 ? '+' : '' }}{{ selectedCategory.yearOverYear }}%
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="Data Quality">
            <el-tag :type="getQualityTagType(selectedCategory.dataQuality)" size="small">{{ selectedCategory.dataQuality }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Calculation Method">{{ selectedCategory.calculationMethod }}</el-descriptions-item>
          <el-descriptions-item label="Primary Data Sources" :span="2">{{ selectedCategory.dataSources }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedCategory.description }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <div class="section-title">Breakdown Details</div>
          <div class="trend-chart" ref="breakdownChartEl"></div>
        </div>

        <div class="detail-section">
          <div class="section-title">Reduction Initiatives</div>
          <el-timeline>
            <el-timeline-item
                v-for="init in selectedCategory.initiatives"
                :key="init.id"
                :timestamp="init.status"
                :type="init.status === 'Completed' ? 'success' : (init.status === 'In Progress' ? 'primary' : 'info')"
                placement="top"
            >
              <div class="initiative-content">
                <div class="initiative-title">{{ init.title }}</div>
                <div class="initiative-impact">Expected reduction: {{ init.expectedReduction }} tCO₂e</div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>

        <div class="detail-section">
          <div class="section-title">Recommendations</div>
          <el-alert
              :title="selectedCategory.recommendation.title"
              :type="selectedCategory.recommendation.type"
              :description="selectedCategory.recommendation.description"
              :closable="false"
              show-icon
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="exportCategoryReport(selectedCategory)">Export Report</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Connection, ShoppingCart, Van, Suitcase, Download, Refresh,
  Search, RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading Scope 3 emissions data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading supply chain data...',
  'Analyzing value chain emissions...',
  'Calculating category impacts...',
  'Preparing insights...',
  'Almost ready...'
]

// ==================== Types ====================
interface ReductionInitiative {
  id: number
  title: string
  expectedReduction: number
  status: string
}

interface Recommendation {
  title: string
  type: 'success' | 'warning' | 'info' | 'error'
  description: string
}

interface Scope3Category {
  id: number
  category: string
  emissions: number
  percentage: number
  yearOverYear: number
  dataQuality: string
  calculationMethod: string
  dataSources: string
  description: string
  subCategories?: { name: string; value: number }[]
  initiatives: ReductionInitiative[]
  recommendation: Recommendation
}

// ==================== Mock Data ====================
const categories = [
  'Purchased Goods and Services',
  'Capital Goods',
  'Fuel and Energy Related Activities',
  'Upstream Transportation and Distribution',
  'Waste Generated in Operations',
  'Business Travel',
  'Employee Commuting',
  'Upstream Leased Assets',
  'Downstream Transportation and Distribution',
  'Processing of Sold Products',
  'Use of Sold Products',
  'End-of-Life Treatment of Sold Products',
  'Downstream Leased Assets',
  'Franchises',
  'Investments'
]

const generateScope3Data = (): Scope3Category[] => {
  const emissionsBase = [8500, 3200, 2800, 2100, 950, 780, 650, 420, 380, 290, 240, 180, 150, 120, 95]
  const percentages = emissionsBase.map(e => parseFloat((e / 22000 * 100).toFixed(1)))

  const dataQualityList = ['High', 'Medium', 'Low', 'Medium', 'High', 'High', 'Medium', 'Low', 'Medium', 'Low', 'Low', 'Medium', 'Low', 'Low', 'Medium']
  const methods = [
    'Spend-based', 'Spend-based', 'Hybrid', 'Distance-based', 'Mass-based',
    'Distance-based', 'Survey-based', 'Average-data', 'Spend-based', 'Average-data',
    'Average-data', 'Mass-based', 'Average-data', 'Average-data', 'Average-data'
  ]

  const sources = [
    'Procurement data, Supplier surveys', 'Fixed asset register, Supplier data', 'Energy bills, Utility data', 'Freight invoices, Logistics data',
    'Waste manifests, Disposal records', 'Travel records, Expense reports', 'Employee surveys, Commute data', 'Lease agreements, Utility data',
    'Sales data, Customer surveys', 'Product specifications, Industry data', 'Product energy ratings, Usage data', 'Product lifecycle data',
    'Lease agreements', 'Franchise agreements', 'Investment portfolio data'
  ]

  const descriptions = [
    'Emissions from the production of products and services purchased',
    'Emissions from the production of capital goods purchased',
    'Emissions from the production of fuels and energy purchased',
    'Emissions from transportation of products by third parties',
    'Emissions from disposal of waste from operations',
    'Emissions from employee business travel',
    'Emissions from employee commuting',
    'Emissions from operation of leased assets',
    'Emissions from downstream transportation',
    'Emissions from processing of sold products',
    'Emissions from customer use of sold products',
    'Emissions from disposal of sold products',
    'Emissions from operation of leased assets (lessor)',
    'Emissions from franchise operations',
    'Emissions from investments'
  ]

  const categoriesData: Scope3Category[] = []

  for (let i = 0; i < categories.length; i++) {
    const subCategories = []
    if (i === 0) {
      subCategories.push({ name: 'Electronics', value: 3200 }, { name: 'IT Equipment', value: 2100 }, { name: 'Facilities', value: 1800 }, { name: 'Services', value: 1400 })
    } else if (i === 5) {
      subCategories.push({ name: 'Air Travel', value: 450 }, { name: 'Rail Travel', value: 180 }, { name: 'Car Rental', value: 150 })
    } else if (i === 6) {
      subCategories.push({ name: 'Car', value: 350 }, { name: 'Public Transit', value: 180 }, { name: 'Bicycle/Walk', value: 70 }, { name: 'Remote Work', value: 50 })
    } else if (i === 4) {
      subCategories.push({ name: 'General Waste', value: 450 }, { name: 'Recyclables', value: 280 }, { name: 'Hazardous Waste', value: 220 })
    } else {
      subCategories.push({ name: 'Other', value: emissionsBase[i] })
    }

    const initiatives: ReductionInitiative[] = [
      { id: 1, title: 'Supplier engagement program', expectedReduction: Math.round(emissionsBase[i] * 0.15), status: 'In Progress' },
      { id: 2, title: 'Efficiency improvement', expectedReduction: Math.round(emissionsBase[i] * 0.08), status: 'Planned' },
      { id: 3, title: 'Alternative sourcing', expectedReduction: Math.round(emissionsBase[i] * 0.1), status: 'In Progress' }
    ]

    let recommendation: Recommendation
    if (percentages[i] > 15) {
      recommendation = {
        title: 'Priority Reduction Category',
        type: 'error',
        description: `This category represents ${percentages[i]}% of Scope 3 emissions. Prioritize supplier engagement and procurement strategy changes.`
      }
    } else if (dataQualityList[i] === 'Low') {
      recommendation = {
        title: 'Data Quality Improvement',
        type: 'warning',
        description: 'Data quality is currently Low. Implement better tracking and data collection methods for more accurate reporting.'
      }
    } else {
      recommendation = {
        title: 'Monitor Progress',
        type: 'info',
        description: 'Current reduction strategies are effective. Continue monitoring and look for additional opportunities.'
      }
    }

    categoriesData.push({
      id: i + 1,
      category: categories[i],
      emissions: emissionsBase[i],
      percentage: percentages[i],
      yearOverYear: parseFloat((Math.random() * 20 - 10).toFixed(1)),
      dataQuality: dataQualityList[i],
      calculationMethod: methods[i],
      dataSources: sources[i],
      description: descriptions[i],
      subCategories: subCategories,
      initiatives: initiatives,
      recommendation: recommendation
    })
  }

  return categoriesData
}

const scope3Data = ref<Scope3Category[]>(generateScope3Data())

// ==================== State ====================
const searchText = ref('')
const categoryFilter = ref('')
const yearFilter = ref('2024')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const selectedCategory = ref<Scope3Category | null>(null)

// Chart refs
let categoryChart: echarts.ECharts | null = null
let topCategoriesChart: echarts.ECharts | null = null
let supplierChart: echarts.ECharts | null = null
let travelChart: echarts.ECharts | null = null
let wasteChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null
let reductionChart: echarts.ECharts | null = null
let breakdownChart: echarts.ECharts | null = null

const categoryChartEl = ref<HTMLElement | null>(null)
const topCategoriesChartEl = ref<HTMLElement | null>(null)
const supplierChartEl = ref<HTMLElement | null>(null)
const travelChartEl = ref<HTMLElement | null>(null)
const wasteChartEl = ref<HTMLElement | null>(null)
const trendChartEl = ref<HTMLElement | null>(null)
const reductionChartEl = ref<HTMLElement | null>(null)
const breakdownChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  const totalEmissions = scope3Data.value.reduce((sum, c) => sum + c.emissions, 0)
  const purchasedGoods = scope3Data.value[0]?.emissions || 0
  const transportation = scope3Data.value[3]?.emissions || 0
  const businessTravel = scope3Data.value[5]?.emissions || 0

  return {
    totalEmissions: totalEmissions,
    emissionsTrend: -3.8,
    purchasedGoods: purchasedGoods,
    purchasedPercent: Math.round((purchasedGoods / totalEmissions) * 100),
    transportation: transportation,
    transportPercent: Math.round((transportation / totalEmissions) * 100),
    businessTravel: businessTravel,
    travelPercent: Math.round((businessTravel / totalEmissions) * 100)
  }
})

const metrics = computed(() => {
  const topCategory = scope3Data.value[0]?.category || ''
  const topPercentage = scope3Data.value[0]?.percentage || 0
  const avgDataQuality = scope3Data.value.filter(c => c.dataQuality === 'High').length / scope3Data.value.length
  const supplierEngagement = 65
  const activeSuppliers = 42
  const commuteCategory = scope3Data.value[6]
  const commuteEmissions = commuteCategory?.emissions || 0
  const commutePerEmployee = (commuteEmissions / 250).toFixed(1)

  return {
    topCategory: topCategory,
    topPercentage: topPercentage,
    dataCompleteness: Math.round(avgDataQuality * 100),
    supplierEngagement: supplierEngagement,
    activeSuppliers: activeSuppliers,
    commuteEmissions: commuteEmissions,
    commutePerEmployee: parseFloat(commutePerEmployee)
  }
})

const filteredCategories = computed(() => {
  let filtered = [...scope3Data.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(c =>
        c.category.toLowerCase().includes(search)
    )
  }

  if (categoryFilter.value) {
    filtered = filtered.filter(c => c.category === categoryFilter.value)
  }

  return filtered
})

const totalRecords = computed(() => filteredCategories.value.length)

const paginatedCategories = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredCategories.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getPercentColor = (percent: number): string => {
  if (percent > 20) return '#ef4444'
  if (percent > 10) return '#f59e0b'
  return '#22c55e'
}

const getQualityTagType = (quality: string): string => {
  const map: Record<string, string> = { High: 'success', Medium: 'warning', Low: 'danger' }
  return map[quality] || 'info'
}

const resetFilters = () => {
  searchText.value = ''
  categoryFilter.value = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

// ==================== Chart Functions ====================
const initCategoryChart = () => {
  if (!categoryChartEl.value) return
  if (categoryChart) {
    categoryChart.dispose()
    categoryChart = null
  }

  const data = scope3Data.value.map(c => ({ name: c.category, value: c.emissions }))

  categoryChart = echarts.init(categoryChartEl.value)
  categoryChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} tCO₂e ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: data.map(d => d.name), type: 'scroll' },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: data,
      label: { show: true, formatter: '{b}: {d}%', fontSize: 10 },
      emphasis: { scale: true }
    }]
  })
}

const initTopCategoriesChart = () => {
  if (!topCategoriesChartEl.value) return
  if (topCategoriesChart) {
    topCategoriesChart.dispose()
    topCategoriesChart = null
  }

  const top8 = scope3Data.value.slice(0, 8)
  const names = top8.map(c => c.category.length > 20 ? c.category.slice(0, 20) + '...' : c.category)
  const values = top8.map(c => c.emissions)

  topCategoriesChart = echarts.init(topCategoriesChartEl.value)
  topCategoriesChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 40, containLabel: true },
    xAxis: { type: 'category', data: names, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: 'Emissions (tCO₂e)' },
    series: [{
      type: 'bar',
      data: values,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#3b82f6' },
      label: { show: true, position: 'top', formatter: '{c} t' }
    }]
  })
}

const initSupplierChart = () => {
  if (!supplierChartEl.value) return
  if (supplierChart) {
    supplierChart.dispose()
    supplierChart = null
  }

  const suppliers = ['Supplier A', 'Supplier B', 'Supplier C', 'Supplier D', 'Supplier E', 'Supplier F', 'Supplier G', 'Supplier H', 'Supplier I', 'Supplier J']
  const emissions = [1250, 980, 850, 720, 680, 550, 480, 420, 380, 320]

  supplierChart = echarts.init(supplierChartEl.value)
  supplierChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: suppliers, axisLabel: { rotate: 45, fontSize: 10 } },
    yAxis: { type: 'value', name: 'Emissions (tCO₂e)' },
    series: [{
      type: 'bar',
      data: emissions,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#f59e0b' },
      label: { show: true, position: 'top', formatter: '{c} t' }
    }]
  })
}

const initTravelChart = () => {
  if (!travelChartEl.value) return
  if (travelChart) {
    travelChart.dispose()
    travelChart = null
  }

  travelChart = echarts.init(travelChartEl.value)
  travelChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} tCO₂e ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: ['Air Travel', 'Rail Travel', 'Car Rental'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: 450, name: 'Air Travel', itemStyle: { color: '#ef4444' } },
        { value: 180, name: 'Rail Travel', itemStyle: { color: '#22c55e' } },
        { value: 150, name: 'Car Rental', itemStyle: { color: '#f59e0b' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const initWasteChart = () => {
  if (!wasteChartEl.value) return
  if (wasteChart) {
    wasteChart.dispose()
    wasteChart = null
  }

  wasteChart = echarts.init(wasteChartEl.value)
  wasteChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} tCO₂e ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: ['General Waste', 'Recyclables', 'Hazardous Waste'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: 450, name: 'General Waste', itemStyle: { color: '#f59e0b' } },
        { value: 280, name: 'Recyclables', itemStyle: { color: '#22c55e' } },
        { value: 220, name: 'Hazardous Waste', itemStyle: { color: '#ef4444' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const initTrendChart = () => {
  if (!trendChartEl.value) return
  if (trendChart) {
    trendChart.dispose()
    trendChart = null
  }

  const categories = ['Purchased Goods', 'Capital Goods', 'Upstream Transport', 'Business Travel', 'Employee Commute']
  const thisYear = [8500, 3200, 2100, 780, 650]
  const lastYear = [8800, 3350, 2250, 850, 700]

  trendChart = echarts.init(trendChartEl.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['2024', '2023'], bottom: 0 },
    grid: { top: 30, left: 60, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: categories, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'Emissions (tCO₂e)' },
    series: [
      { name: '2024', type: 'bar', data: thisYear, itemStyle: { color: '#3b82f6', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top' } },
      { name: '2023', type: 'bar', data: lastYear, itemStyle: { color: '#94a3b8', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top' } }
    ]
  })
}

const initReductionChart = () => {
  if (!reductionChartEl.value) return
  if (reductionChart) {
    reductionChart.dispose()
    reductionChart = null
  }

  const categories = ['Purchased Goods', 'Capital Goods', 'Transportation', 'Business Travel', 'Waste']
  const potentials = [1200, 450, 300, 150, 180]

  reductionChart = echarts.init(reductionChartEl.value)
  reductionChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: categories },
    yAxis: { type: 'value', name: 'Reduction Potential (tCO₂e)' },
    series: [{
      type: 'bar',
      data: potentials,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#22c55e' },
      label: { show: true, position: 'top', formatter: '{c} t' }
    }]
  })
}

const initBreakdownChart = () => {
  if (!breakdownChartEl.value || !selectedCategory.value) return
  if (breakdownChart) {
    breakdownChart.dispose()
    breakdownChart = null
  }

  const data = selectedCategory.value.subCategories || []

  breakdownChart = echarts.init(breakdownChartEl.value)
  breakdownChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} tCO₂e ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: data.map(d => d.name) },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: data,
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initCategoryChart()
    initTopCategoriesChart()
    initSupplierChart()
    initTravelChart()
    initWasteChart()
    initTrendChart()
    initReductionChart()
  })
}

// ==================== Actions ====================
const viewCategoryDetail = (category: Scope3Category) => {
  selectedCategory.value = category
  detailDialogVisible.value = true
  nextTick(() => initBreakdownChart())
}

const viewAllCategories = () => {
  ElMessage.info('Viewing all categories')
}

const exportCategoryReport = (category: Scope3Category | null) => {
  if (category) {
    ElMessage.success(`Exporting report for ${category.category}...`)
    setTimeout(() => {
      ElMessage.success('Report generated successfully')
    }, 1500)
  }
}

const exportData = () => {
  ElMessage.success('Exporting Scope 3 emissions data...')
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
    const charts = [categoryChart, topCategoriesChart, supplierChart, travelChart, wasteChart, trendChart, reductionChart, breakdownChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([searchText, categoryFilter, yearFilter], () => {
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
  const charts = [categoryChart, topCategoriesChart, supplierChart, travelChart, wasteChart, trendChart, reductionChart, breakdownChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.scope3-page {
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

/* Category Detail */
.category-detail {
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

.initiative-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.initiative-title {
  font-weight: 500;
}

.initiative-impact {
  font-size: 12px;
  color: #64748b;
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