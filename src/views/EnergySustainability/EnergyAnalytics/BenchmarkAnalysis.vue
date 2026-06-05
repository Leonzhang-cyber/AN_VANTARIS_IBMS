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
          <span class="loading-title">Benchmark Analysis</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Energy Performance Benchmarking & Industry Comparison</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="benchmark-analysis-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Histogram /></el-icon>
          Benchmark Analysis
        </h1>
        <div class="page-subtitle">Compare energy performance against industry standards and best practices</div>
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
          <div class="stat-value">{{ stats.overallScore }}<span class="stat-unit">/100</span></div>
          <div class="stat-label">Overall Benchmark Score</div>
          <div class="stat-trend" :class="stats.scoreTrend > 0 ? 'up' : 'down'">
            {{ stats.scoreTrend > 0 ? '↑' : '↓' }} {{ Math.abs(stats.scoreTrend) }} vs last year
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.aboveAverage }}</div>
          <div class="stat-label">Above Industry Avg</div>
          <div class="stat-trend up">{{ stats.abovePercent }}% of metrics</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Loading /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.atAverage }}</div>
          <div class="stat-label">At Industry Avg</div>
          <div class="stat-trend">{{ stats.atPercent }}% of metrics</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><Bottom /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.belowAverage }}</div>
          <div class="stat-label">Below Industry Avg</div>
          <div class="stat-trend down">{{ stats.belowPercent }}% of metrics</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">PUE Benchmark</div>
        <div class="metric-value">{{ metrics.pue }}<span class="metric-unit"></span></div>
        <div class="metric-trend" :class="metrics.pueTrend < 0 ? 'positive' : 'negative'">
          {{ metrics.pueTrend < 0 ? '↓' : '↑' }} {{ Math.abs(metrics.pueTrend) }} vs industry avg
        </div>
        <div class="metric-target">Industry Avg: 1.52</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Energy Intensity</div>
        <div class="metric-value">{{ metrics.energyIntensity }}<span class="metric-unit">kWh/m²</span></div>
        <div class="metric-trend" :class="metrics.intensityTrend < 0 ? 'positive' : 'negative'">
          {{ metrics.intensityTrend < 0 ? '↓' : '↑' }} {{ Math.abs(metrics.intensityTrend) }}% vs peers
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Carbon Intensity</div>
        <div class="metric-value">{{ metrics.carbonIntensity }}<span class="metric-unit">kgCO₂/m²</span></div>
        <div class="metric-trend positive">{{ metrics.carbonRank }} percentile</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Cost Benchmark</div>
        <div class="metric-value">${{ metrics.costBenchmark }}<span class="metric-unit">/m²</span></div>
        <div class="metric-sub">vs ${{ metrics.industryCost }}/m² industry</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card large">
        <div class="chart-header">
          <span class="chart-title">Performance vs Industry Benchmark</span>
          <span class="chart-subtitle">By energy metric</span>
        </div>
        <div class="chart-container" ref="performanceChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">PUE Distribution</span>
          <span class="chart-subtitle">Industry PUE comparison</span>
        </div>
        <div class="chart-container" ref="pueDistributionChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Energy Intensity by Category</span>
          <span class="chart-subtitle">Comparison across asset types</span>
        </div>
        <div class="chart-container" ref="intensityChartEl"></div>
      </div>
    </div>

    <!-- Third Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Percentile Ranking</span>
          <span class="chart-subtitle">Where we stand</span>
        </div>
        <div class="chart-container" ref="percentileChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Peer Comparison</span>
          <span class="chart-subtitle">Top 5 peers vs our performance</span>
        </div>
        <div class="chart-container" ref="peerChartEl"></div>
      </div>
    </div>

    <!-- Fourth Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Improvement Opportunities</span>
          <span class="chart-subtitle">Gap to best in class</span>
        </div>
        <div class="chart-container" ref="opportunityChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Historical Benchmark Trend</span>
          <span class="chart-subtitle">Performance evolution</span>
        </div>
        <div class="chart-container" ref="trendChartEl"></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-select v-model="categoryFilter" placeholder="Category" clearable style="width: 150px">
          <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
        </el-select>
        <el-select v-model="metricTypeFilter" placeholder="Metric Type" clearable style="width: 150px">
          <el-option label="Efficiency" value="efficiency" />
          <el-option label="Intensity" value="intensity" />
          <el-option label="Cost" value="cost" />
          <el-option label="Carbon" value="carbon" />
        </el-select>
        <el-select v-model="peerGroupFilter" placeholder="Peer Group" clearable style="width: 150px">
          <el-option label="Data Center" value="datacenter" />
          <el-option label="Office Building" value="office" />
          <el-option label="Industrial" value="industrial" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Benchmark Metrics Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Benchmark Metrics</span>
        <el-button size="small" @click="viewAllMetrics">View All →</el-button>
      </div>
      <el-table :data="paginatedMetrics" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="metric" label="Metric" min-width="200" />
        <el-table-column prop="category" label="Category" width="140">
          <template #default="{ row }">
            <el-tag :type="getCategoryTagType(row.category)" size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ourValue" label="Our Value" width="130">
          <template #default="{ row }">
            {{ row.ourValue }} {{ row.unit }}
          </template>
        </el-table-column>
        <el-table-column prop="industryAvg" label="Industry Avg" width="130">
          <template #default="{ row }">
            {{ row.industryAvg }} {{ row.unit }}
          </template>
        </el-table-column>
        <el-table-column prop="bestInClass" label="Best in Class" width="130">
          <template #default="{ row }">
            {{ row.bestInClass }} {{ row.unit }}
          </template>
        </el-table-column>
        <el-table-column prop="gap" label="Gap" width="100">
          <template #default="{ row }">
            <span :class="getGapClass(row.gap, row.direction)">
              {{ row.gap > 0 ? '+' : '' }}{{ row.gap }}{{ row.unit }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="percentile" label="Percentile" width="140">
          <template #default="{ row }">
            <el-progress :percentage="row.percentile" :stroke-width="8" :color="getPercentileColor(row.percentile)" />
          </template>
        </el-table-column>
        <el-table-column prop="rating" label="Rating" width="100">
          <template #default="{ row }">
            <el-tag :type="getRatingTagType(row.rating)" size="small">{{ row.rating }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewMetricDetail(row)">Details</el-button>
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

    <!-- Metric Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedMetric?.metric" width="800px">
      <div v-if="selectedMetric" class="metric-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Category">{{ selectedMetric.category }}</el-descriptions-item>
          <el-descriptions-item label="Metric Type">{{ selectedMetric.metricType }}</el-descriptions-item>
          <el-descriptions-item label="Our Value">{{ selectedMetric.ourValue }} {{ selectedMetric.unit }}</el-descriptions-item>
          <el-descriptions-item label="Industry Average">{{ selectedMetric.industryAvg }} {{ selectedMetric.unit }}</el-descriptions-item>
          <el-descriptions-item label="Best in Class">{{ selectedMetric.bestInClass }} {{ selectedMetric.unit }}</el-descriptions-item>
          <el-descriptions-item label="Percentile Rank">{{ selectedMetric.percentile }}%</el-descriptions-item>
          <el-descriptions-item label="Rating">
            <el-tag :type="getRatingTagType(selectedMetric.rating)" size="small">{{ selectedMetric.rating }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Gap to Best">
            <span :class="getGapClass(selectedMetric.gapToBest, selectedMetric.direction)">
              {{ selectedMetric.gapToBest > 0 ? '+' : '' }}{{ selectedMetric.gapToBest }}{{ selectedMetric.unit }}
            </span>
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <div class="section-title">Distribution Analysis</div>
          <div class="trend-chart" ref="distributionChartEl"></div>
        </div>

        <div class="detail-section">
          <div class="section-title">Recommendations</div>
          <el-alert
              :title="selectedMetric.recommendation.title"
              :type="selectedMetric.recommendation.type"
              :description="selectedMetric.recommendation.description"
              :closable="false"
              show-icon
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="generateReport(selectedMetric)">Generate Report</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Histogram, TrendCharts, CircleCheck, Loading, Bottom, Download, Refresh,
  RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading benchmark data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading benchmark data...',
  'Comparing industry standards...',
  'Analyzing performance gaps...',
  'Calculating percentiles...',
  'Almost ready...'
]

// ==================== Types ====================
interface BenchmarkMetric {
  id: number
  metric: string
  category: string
  metricType: string
  ourValue: number
  industryAvg: number
  bestInClass: number
  unit: string
  gap: number
  gapToBest: number
  direction: 'higher' | 'lower'
  percentile: number
  rating: string
  recommendation: {
    title: string
    type: 'success' | 'warning' | 'info' | 'error'
    description: string
  }
}

// ==================== Mock Data ====================
const categories = ['PUE', 'Energy Intensity', 'Carbon', 'Cost', 'Water', 'Waste']

const generateBenchmarkData = (): BenchmarkMetric[] => {
  const metrics: BenchmarkMetric[] = [
    { id: 1, metric: 'Power Usage Effectiveness (PUE)', category: 'PUE', metricType: 'efficiency', ourValue: 1.42, industryAvg: 1.52, bestInClass: 1.25, unit: '', gap: -0.10, gapToBest: 0.17, direction: 'lower', percentile: 75, rating: 'Good', recommendation: { title: 'Above Average Performance', type: 'success', description: 'Your PUE is better than 75% of industry peers. Continue optimization efforts.' } },
    { id: 2, metric: 'Energy Intensity (EUI)', category: 'Energy Intensity', metricType: 'intensity', ourValue: 185, industryAvg: 220, bestInClass: 120, unit: 'kWh/m²', gap: -35, gapToBest: 65, direction: 'lower', percentile: 68, rating: 'Good', recommendation: { title: 'Moderate Performance', type: 'info', description: 'Energy intensity is below industry average. Focus on high-intensity areas.' } },
    { id: 3, metric: 'Carbon Emissions Intensity', category: 'Carbon', metricType: 'carbon', ourValue: 85, industryAvg: 110, bestInClass: 45, unit: 'kgCO₂/m²', gap: -25, gapToBest: 40, direction: 'lower', percentile: 72, rating: 'Good', recommendation: { title: 'Good Performance', type: 'success', description: 'Carbon intensity is 23% below industry average.' } },
    { id: 4, metric: 'Energy Cost per Area', category: 'Cost', metricType: 'cost', ourValue: 28, industryAvg: 35, bestInClass: 18, unit: '$/m²', gap: -7, gapToBest: 10, direction: 'lower', percentile: 65, rating: 'Good', recommendation: { title: 'Cost Competitive', type: 'info', description: 'Energy costs are 20% below industry average.' } },
    { id: 5, metric: 'Water Usage Effectiveness (WUE)', category: 'Water', metricType: 'efficiency', ourValue: 1.8, industryAvg: 2.1, bestInClass: 1.2, unit: 'L/kWh', gap: -0.3, gapToBest: 0.6, direction: 'lower', percentile: 60, rating: 'Average', recommendation: { title: 'Opportunity for Improvement', type: 'warning', description: 'Water efficiency can be improved by optimizing cooling systems.' } },
    { id: 6, metric: 'IT Equipment Efficiency', category: 'Energy Intensity', metricType: 'efficiency', ourValue: 72, industryAvg: 68, bestInClass: 85, unit: '%', gap: 4, gapToBest: 13, direction: 'higher', percentile: 55, rating: 'Average', recommendation: { title: 'Room for Improvement', type: 'warning', description: 'IT equipment efficiency is near industry average. Consider hardware refresh.' } },
    { id: 7, metric: 'Renewable Energy Ratio', category: 'Carbon', metricType: 'carbon', ourValue: 35, industryAvg: 28, bestInClass: 65, unit: '%', gap: 7, gapToBest: 30, direction: 'higher', percentile: 62, rating: 'Good', recommendation: { title: 'Above Average', type: 'success', description: 'Renewable energy adoption exceeds industry average.' } },
    { id: 8, metric: 'Cooling Efficiency (COP)', category: 'PUE', metricType: 'efficiency', ourValue: 4.2, industryAvg: 3.8, bestInClass: 5.5, unit: '', gap: 0.4, gapToBest: 1.3, direction: 'higher', percentile: 58, rating: 'Average', recommendation: { title: 'Moderate Performance', type: 'info', description: 'Cooling efficiency is above average but below best in class.' } },
    { id: 9, metric: 'Lighting Power Density', category: 'Energy Intensity', metricType: 'intensity', ourValue: 8.5, industryAvg: 10.2, bestInClass: 5.5, unit: 'W/m²', gap: -1.7, gapToBest: 3.0, direction: 'lower', percentile: 70, rating: 'Good', recommendation: { title: 'Good Performance', type: 'success', description: 'Lighting efficiency is significantly above industry average.' } },
    { id: 10, metric: 'Waste Diversion Rate', category: 'Waste', metricType: 'sustainability', ourValue: 45, industryAvg: 38, bestInClass: 75, unit: '%', gap: 7, gapToBest: 30, direction: 'higher', percentile: 55, rating: 'Average', recommendation: { title: 'Improvement Opportunity', type: 'warning', description: 'Waste diversion can be improved with better recycling programs.' } }
  ]

  return metrics
}

const benchmarkMetrics = ref<BenchmarkMetric[]>(generateBenchmarkData())

// ==================== State ====================
const categoryFilter = ref('')
const metricTypeFilter = ref('')
const peerGroupFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const selectedMetric = ref<BenchmarkMetric | null>(null)

// Chart refs
let performanceChart: echarts.ECharts | null = null
let pueDistributionChart: echarts.ECharts | null = null
let intensityChart: echarts.ECharts | null = null
let percentileChart: echarts.ECharts | null = null
let peerChart: echarts.ECharts | null = null
let opportunityChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null
let distributionChart: echarts.ECharts | null = null

const performanceChartEl = ref<HTMLElement | null>(null)
const pueDistributionChartEl = ref<HTMLElement | null>(null)
const intensityChartEl = ref<HTMLElement | null>(null)
const percentileChartEl = ref<HTMLElement | null>(null)
const peerChartEl = ref<HTMLElement | null>(null)
const opportunityChartEl = ref<HTMLElement | null>(null)
const trendChartEl = ref<HTMLElement | null>(null)
const distributionChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  const totalMetrics = benchmarkMetrics.value.length
  const aboveAverage = benchmarkMetrics.value.filter(m => m.percentile >= 75).length
  const atAverage = benchmarkMetrics.value.filter(m => m.percentile >= 25 && m.percentile < 75).length
  const belowAverage = benchmarkMetrics.value.filter(m => m.percentile < 25).length
  const overallScore = Math.round(benchmarkMetrics.value.reduce((sum, m) => sum + m.percentile, 0) / totalMetrics)

  return {
    overallScore: overallScore,
    scoreTrend: 3,
    aboveAverage: aboveAverage,
    abovePercent: Math.round((aboveAverage / totalMetrics) * 100),
    atAverage: atAverage,
    atPercent: Math.round((atAverage / totalMetrics) * 100),
    belowAverage: belowAverage,
    belowPercent: Math.round((belowAverage / totalMetrics) * 100)
  }
})

const metrics = computed(() => {
  const pueMetric = benchmarkMetrics.value.find(m => m.metric === 'Power Usage Effectiveness (PUE)')
  const energyIntensity = benchmarkMetrics.value.find(m => m.metric === 'Energy Intensity (EUI)')
  const carbonMetric = benchmarkMetrics.value.find(m => m.metric === 'Carbon Emissions Intensity')
  const costMetric = benchmarkMetrics.value.find(m => m.metric === 'Energy Cost per Area')

  return {
    pue: pueMetric?.ourValue || 0,
    pueTrend: ((pueMetric?.industryAvg || 0) - (pueMetric?.ourValue || 0)).toFixed(2),
    energyIntensity: energyIntensity?.ourValue || 0,
    intensityTrend: -8,
    carbonIntensity: carbonMetric?.ourValue || 0,
    carbonRank: 72,
    costBenchmark: costMetric?.ourValue || 0,
    industryCost: costMetric?.industryAvg || 0
  }
})

const filteredMetrics = computed(() => {
  let filtered = [...benchmarkMetrics.value]

  if (categoryFilter.value) {
    filtered = filtered.filter(m => m.category === categoryFilter.value)
  }

  if (metricTypeFilter.value) {
    filtered = filtered.filter(m => m.metricType === metricTypeFilter.value)
  }

  return filtered
})

const totalRecords = computed(() => filteredMetrics.value.length)

const paginatedMetrics = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredMetrics.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getCategoryTagType = (category: string): string => {
  const map: Record<string, string> = {
    'PUE': 'primary',
    'Energy Intensity': 'warning',
    'Carbon': 'danger',
    'Cost': 'success',
    'Water': 'info',
    'Waste': ''
  }
  return map[category] || 'info'
}

const getGapClass = (gap: number, direction: string): string => {
  if (direction === 'higher') {
    if (gap > 0) return 'metric-good'
    if (gap < 0) return 'metric-bad'
  } else {
    if (gap < 0) return 'metric-good'
    if (gap > 0) return 'metric-bad'
  }
  return 'metric-warning'
}

const getPercentileColor = (percentile: number): string => {
  if (percentile >= 75) return '#22c55e'
  if (percentile >= 25) return '#f59e0b'
  return '#ef4444'
}

const getRatingTagType = (rating: string): string => {
  const map: Record<string, string> = { 'Excellent': 'success', 'Good': 'primary', 'Average': 'info', 'Poor': 'danger' }
  return map[rating] || 'info'
}

const resetFilters = () => {
  categoryFilter.value = ''
  metricTypeFilter.value = ''
  peerGroupFilter.value = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

// ==================== Chart Functions ====================
const initPerformanceChart = () => {
  if (!performanceChartEl.value) return
  if (performanceChart) {
    performanceChart.dispose()
    performanceChart = null
  }

  const metricNames = benchmarkMetrics.value.slice(0, 8).map(m => m.metric.length > 20 ? m.metric.slice(0, 20) + '...' : m.metric)
  const ourValues = benchmarkMetrics.value.slice(0, 8).map(m => m.ourValue)
  const industryValues = benchmarkMetrics.value.slice(0, 8).map(m => m.industryAvg)

  performanceChart = echarts.init(performanceChartEl.value)
  performanceChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Our Performance', 'Industry Average'], bottom: 0 },
    grid: { top: 40, left: 60, right: 30, bottom: 60, containLabel: true },
    xAxis: { type: 'category', data: metricNames, axisLabel: { rotate: 30, fontSize: 10 } },
    yAxis: { type: 'value', name: 'Value' },
    series: [
      { name: 'Our Performance', type: 'bar', data: ourValues, itemStyle: { color: '#3b82f6', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top' } },
      { name: 'Industry Average', type: 'bar', data: industryValues, itemStyle: { color: '#94a3b8', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top' } }
    ]
  })
}

const initPueDistributionChart = () => {
  if (!pueDistributionChartEl.value) return
  if (pueDistributionChart) {
    pueDistributionChart.dispose()
    pueDistributionChart = null
  }

  const ranges = ['1.0-1.2', '1.2-1.4', '1.4-1.6', '1.6-1.8', '1.8-2.0', '>2.0']
  const percentages = [5, 15, 35, 28, 12, 5]
  const ourPUE = 1.42

  pueDistributionChart = echarts.init(pueDistributionChartEl.value)
  pueDistributionChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: ranges },
    yAxis: { type: 'value', name: 'Percentage of Facilities (%)' },
    series: [{
      type: 'bar',
      data: percentages,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#3b82f6' },
      label: { show: true, position: 'top', formatter: '{c}%' },
      markLine: {
        data: [{ xAxis: ourPUE < 1.4 ? 1 : (ourPUE < 1.6 ? 2 : 3), name: 'Our PUE' }],
        lineStyle: { color: '#ef4444', type: 'dashed', width: 2 },
        label: { formatter: 'Our PUE: {c}' }
      }
    }]
  })
}

const initIntensityChart = () => {
  if (!intensityChartEl.value) return
  if (intensityChart) {
    intensityChart.dispose()
    intensityChart = null
  }

  const categories = ['UPS', 'Generator', 'CRAC', 'Chiller', 'IT Equipment']
  const ourIntensity = [185, 220, 165, 250, 195]
  const industryIntensity = [210, 245, 190, 275, 220]

  intensityChart = echarts.init(intensityChartEl.value)
  intensityChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['Our Facility', 'Industry Average'], bottom: 0 },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: categories },
    yAxis: { type: 'value', name: 'Energy Intensity (kWh/m²)' },
    series: [
      { name: 'Our Facility', type: 'bar', data: ourIntensity, itemStyle: { color: '#3b82f6', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top' } },
      { name: 'Industry Average', type: 'bar', data: industryIntensity, itemStyle: { color: '#94a3b8', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top' } }
    ]
  })
}

const initPercentileChart = () => {
  if (!percentileChartEl.value) return
  if (percentileChart) {
    percentileChart.dispose()
    percentileChart = null
  }

  const metrics = ['PUE', 'EUI', 'Carbon', 'Cost', 'Water']
  const percentiles = [75, 68, 72, 65, 60]

  percentileChart = echarts.init(percentileChartEl.value)
  percentileChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: metrics },
    yAxis: { type: 'value', name: 'Percentile (%)', min: 0, max: 100 },
    series: [{
      type: 'bar',
      data: percentiles,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value >= 75) return '#22c55e'
          if (value >= 50) return '#3b82f6'
          return '#f59e0b'
        }
      },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initPeerChart = () => {
  if (!peerChartEl.value) return
  if (peerChart) {
    peerChart.dispose()
    peerChart = null
  }

  const peers = ['Peer A', 'Peer B', 'Peer C', 'Peer D', 'Peer E', 'Our Facility']
  const pueValues = [1.48, 1.45, 1.51, 1.44, 1.53, 1.42]

  peerChart = echarts.init(peerChartEl.value)
  peerChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: peers },
    yAxis: { type: 'value', name: 'PUE', min: 1.35, max: 1.6 },
    series: [{
      type: 'bar',
      data: pueValues,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          return params.name === 'Our Facility' ? '#ef4444' : '#3b82f6'
        }
      },
      label: { show: true, position: 'top', formatter: '{c}' }
    }]
  })
}

const initOpportunityChart = () => {
  if (!opportunityChartEl.value) return
  if (opportunityChart) {
    opportunityChart.dispose()
    opportunityChart = null
  }

  const opportunities = ['Cooling Optimization', 'IT Efficiency', 'Lighting Upgrade', 'Renewable Energy', 'Water Conservation']
  const gaps = [15, 12, 8, 25, 10]

  opportunityChart = echarts.init(opportunityChartEl.value)
  opportunityChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: opportunities, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'Improvement Potential (%)' },
    series: [{
      type: 'bar',
      data: gaps,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#f59e0b' },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initTrendChart = () => {
  if (!trendChartEl.value) return
  if (trendChart) {
    trendChart.dispose()
    trendChart = null
  }

  const years = ['2019', '2020', '2021', '2022', '2023', '2024']
  const ourScore = [65, 68, 71, 74, 77, 80]
  const industryScore = [62, 64, 66, 68, 70, 72]

  trendChart = echarts.init(trendChartEl.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Our Benchmark Score', 'Industry Average'], bottom: 0 },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: years },
    yAxis: { type: 'value', name: 'Score', min: 50, max: 90 },
    series: [
      { name: 'Our Benchmark Score', type: 'line', data: ourScore, lineStyle: { color: '#3b82f6', width: 3 }, symbol: 'circle', symbolSize: 8, areaStyle: { opacity: 0.1 } },
      { name: 'Industry Average', type: 'line', data: industryScore, lineStyle: { color: '#94a3b8', width: 2, type: 'dashed' }, symbol: 'diamond' }
    ]
  })
}

const initDistributionChart = () => {
  if (!distributionChartEl.value || !selectedMetric.value) return
  if (distributionChart) {
    distributionChart.dispose()
    distributionChart = null
  }

  const values = []
  for (let i = 0; i < 50; i++) {
    const val = selectedMetric.value.industryAvg + (Math.random() - 0.5) * (selectedMetric.value.industryAvg * 0.4)
    values.push(val)
  }

  distributionChart = echarts.init(distributionChartEl.value)
  distributionChart.setOption({
    tooltip: { trigger: 'axis' },
    title: { show: false },
    xAxis: { name: 'Value', type: 'value' },
    yAxis: { name: 'Frequency', type: 'value' },
    series: [{
      type: 'histogram',
      data: values,
      itemStyle: { color: '#3b82f6' },
      markLine: {
        data: [{ xAxis: selectedMetric.value.ourValue, name: 'Our Value' }],
        lineStyle: { color: '#ef4444', width: 2 },
        label: { formatter: 'Our Value: {c}' }
      }
    }]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initPerformanceChart()
    initPueDistributionChart()
    initIntensityChart()
    initPercentileChart()
    initPeerChart()
    initOpportunityChart()
    initTrendChart()
  })
}

// ==================== Actions ====================
const viewMetricDetail = (metric: BenchmarkMetric) => {
  selectedMetric.value = metric
  detailDialogVisible.value = true
  nextTick(() => initDistributionChart())
}

const viewAllMetrics = () => {
  ElMessage.info('Viewing all metrics')
}

const generateReport = (metric: BenchmarkMetric | null) => {
  if (!metric) return
  ElMessage.success(`Generating report for ${metric.metric}...`)
  setTimeout(() => {
    ElMessage.success('Report generated successfully')
  }, 1500)
}

const exportData = () => {
  ElMessage.success('Exporting benchmark data...')
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
    const charts = [performanceChart, pueDistributionChart, intensityChart, percentileChart, peerChart, opportunityChart, trendChart, distributionChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([categoryFilter, metricTypeFilter, peerGroupFilter], () => {
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
  const charts = [performanceChart, pueDistributionChart, intensityChart, percentileChart, peerChart, opportunityChart, trendChart, distributionChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.benchmark-analysis-page {
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

/* Metric Detail */
.metric-detail {
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