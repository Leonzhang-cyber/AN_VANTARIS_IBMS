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
          <span class="loading-title">Benchmark Comparison</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Data Center Performance Benchmarking</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="benchmark-comparison-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Histogram /></el-icon>
          Benchmark Comparison
        </h1>
        <div class="page-subtitle">Compare your data center performance against industry standards</div>
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
          <div class="stat-value">{{ stats.topQuartile }}</div>
          <div class="stat-label">Top Quartile Metrics</div>
          <div class="stat-trend up">{{ stats.topPercent }}% of total</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Loading /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.midQuartile }}</div>
          <div class="stat-label">Mid Quartile Metrics</div>
          <div class="stat-trend">{{ stats.midPercent }}% of total</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><Bottom /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.bottomQuartile }}</div>
          <div class="stat-label">Bottom Quartile Metrics</div>
          <div class="stat-trend down">{{ stats.bottomPercent }}% of total</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">PUE Benchmark</div>
        <div class="metric-value">{{ metrics.pue }}</div>
        <div class="metric-trend" :class="metrics.pueTrend < 0 ? 'positive' : 'negative'">
          {{ metrics.pueTrend < 0 ? '↓' : '↑' }} {{ Math.abs(metrics.pueTrend) }} vs industry avg
        </div>
        <div class="metric-target">Industry Avg: 1.52</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">CUE Benchmark</div>
        <div class="metric-value">{{ metrics.cue }}</div>
        <div class="metric-trend" :class="metrics.cueTrend < 0 ? 'positive' : 'negative'">
          {{ metrics.cueTrend < 0 ? '↓' : '↑' }} {{ Math.abs(metrics.cueTrend) }} vs industry avg
        </div>
        <div class="metric-target">Industry Avg: 0.35</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">WUE Benchmark</div>
        <div class="metric-value">{{ metrics.wue }}<span class="stat-unit">L/kWh</span></div>
        <div class="metric-trend" :class="metrics.wueTrend < 0 ? 'positive' : 'negative'">
          {{ metrics.wueTrend < 0 ? '↓' : '↑' }} {{ Math.abs(metrics.wueTrend) }} vs industry avg
        </div>
        <div class="metric-target">Industry Avg: 1.75</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">IT Efficiency</div>
        <div class="metric-value">{{ metrics.itEfficiency }}<span class="stat-unit">%</span></div>
        <div class="metric-trend" :class="metrics.itTrend > 0 ? 'positive' : 'negative'">
          {{ metrics.itTrend > 0 ? '↑' : '↓' }} {{ Math.abs(metrics.itTrend) }} vs industry avg
        </div>
      </div>
    </div>

    <!-- Charts Row 1 -->
    <div class="charts-row">
      <div class="chart-card large">
        <div class="chart-header">
          <span class="chart-title">Performance vs Industry Benchmark</span>
          <span class="chart-subtitle">Key metrics comparison</span>
        </div>
        <div class="chart-container" ref="performanceChartEl"></div>
      </div>
    </div>

    <!-- Charts Row 2 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">PUE Distribution</span>
          <span class="chart-subtitle">Industry PUE comparison</span>
        </div>
        <div class="chart-container" ref="pueDistChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">CUE Distribution</span>
          <span class="chart-subtitle">Carbon efficiency comparison</span>
        </div>
        <div class="chart-container" ref="cueDistChartEl"></div>
      </div>
    </div>

    <!-- Charts Row 3 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">WUE Distribution</span>
          <span class="chart-subtitle">Water efficiency comparison</span>
        </div>
        <div class="chart-container" ref="wueDistChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Energy Intensity</span>
          <span class="chart-subtitle">Facility vs peers</span>
        </div>
        <div class="chart-container" ref="intensityChartEl"></div>
      </div>
    </div>

    <!-- Charts Row 4 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">RE Ratio Benchmark</span>
          <span class="chart-subtitle">Renewable energy comparison</span>
        </div>
        <div class="chart-container" ref="reChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Cooling Efficiency</span>
          <span class="chart-subtitle">COP comparison</span>
        </div>
        <div class="chart-container" ref="coolingChartEl"></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-select v-model="peerGroupFilter" placeholder="Peer Group" clearable style="width: 180px">
          <el-option label="Global Data Centers" value="global" />
          <el-option label="Asia Pacific" value="apac" />
          <el-option label="North America" value="na" />
          <el-option label="Europe" value="eur" />
        </el-select>
        <el-select v-model="facilityTypeFilter" placeholder="Facility Type" clearable style="width: 150px">
          <el-option label="Hyperscale" value="hyperscale" />
          <el-option label="Colocation" value="colo" />
          <el-option label="Enterprise" value="enterprise" />
          <el-option label="Edge" value="edge" />
        </el-select>
        <el-select v-model="metricFilter" placeholder="Metric" clearable style="width: 150px">
          <el-option label="PUE" value="pue" />
          <el-option label="CUE" value="cue" />
          <el-option label="WUE" value="wue" />
          <el-option label="RE Ratio" value="re" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Benchmark Data Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Benchmark Details</span>
        <el-button size="small" @click="viewAllData">View All →</el-button>
      </div>
      <el-table :data="paginatedData" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="metric" label="Metric" min-width="200" />
        <el-table-column prop="ourValue" label="Our Value" width="130" />
        <el-table-column prop="industryAvg" label="Industry Avg" width="130" />
        <el-table-column prop="bestInClass" label="Best in Class" width="130" />
        <el-table-column prop="gap" label="Gap" width="100">
          <template #default="{ row }">
            <span :class="getGapClass(row.gap, row.direction)">
              {{ row.gap > 0 ? '+' : '' }}{{ row.gap }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="percentile" label="Percentile" width="140">
          <template #default="{ row }">
            <el-progress :percentage="row.percentile" :stroke-width="8" :color="getPercentileColor(row.percentile)" />
          </template>
        </el-table-column>
        <el-table-column prop="ranking" label="Ranking" width="120">
          <template #default="{ row }">
            <el-tag :type="getRankingTagType(row.ranking)" size="small">{{ row.ranking }}</el-tag>
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
          <el-descriptions-item label="Metric">{{ selectedMetric.metric }}</el-descriptions-item>
          <el-descriptions-item label="Our Value">{{ selectedMetric.ourValue }}</el-descriptions-item>
          <el-descriptions-item label="Industry Average">{{ selectedMetric.industryAvg }}</el-descriptions-item>
          <el-descriptions-item label="Best in Class">{{ selectedMetric.bestInClass }}</el-descriptions-item>
          <el-descriptions-item label="Percentile">{{ selectedMetric.percentile }}%</el-descriptions-item>
          <el-descriptions-item label="Ranking">
            <el-tag :type="getRankingTagType(selectedMetric.ranking)" size="small">{{ selectedMetric.ranking }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Gap to Best" :span="2">
            <span :class="getGapClass(selectedMetric.gapToBest, selectedMetric.direction)">
              {{ selectedMetric.gapToBest > 0 ? '+' : '' }}{{ selectedMetric.gapToBest }}
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
        <el-button type="primary" @click="exportMetricReport(selectedMetric)">Export Report</el-button>
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
  ourValue: string
  industryAvg: string
  bestInClass: string
  unit: string
  gap: number
  gapToBest: number
  direction: string
  percentile: number
  ranking: string
  recommendation: {
    title: string
    type: 'success' | 'warning' | 'info' | 'error'
    description: string
  }
}

// ==================== Mock Data ====================
const benchmarkMetrics: BenchmarkMetric[] = [
  { id: 1, metric: 'Power Usage Effectiveness (PUE)', ourValue: '1.42', industryAvg: '1.52', bestInClass: '1.25', unit: '', gap: -0.10, gapToBest: 0.17, direction: 'lower', percentile: 75, ranking: 'Good',
    recommendation: { title: 'Above Average Performance', type: 'success', description: 'Your PUE is better than 75% of industry peers. Continue optimization efforts.' } },
  { id: 2, metric: 'Carbon Usage Effectiveness (CUE)', ourValue: '0.298', industryAvg: '0.35', bestInClass: '0.18', unit: '', gap: -0.052, gapToBest: 0.118, direction: 'lower', percentile: 68, ranking: 'Good',
    recommendation: { title: 'Moderate Performance', type: 'info', description: 'Carbon efficiency is above average. Explore renewable energy options.' } },
  { id: 3, metric: 'Water Usage Effectiveness (WUE)', ourValue: '1.48', industryAvg: '1.75', bestInClass: '1.05', unit: 'L/kWh', gap: -0.27, gapToBest: 0.43, direction: 'lower', percentile: 62, ranking: 'Average',
    recommendation: { title: 'Opportunity for Improvement', type: 'warning', description: 'Water efficiency can be improved with cooling optimization.' } },
  { id: 4, metric: 'IT Equipment Efficiency', ourValue: '72%', industryAvg: '68%', bestInClass: '85%', unit: '%', gap: 4, gapToBest: 13, direction: 'higher', percentile: 55, ranking: 'Average',
    recommendation: { title: 'Room for Improvement', type: 'warning', description: 'Consider hardware refresh and virtualization.' } },
  { id: 5, metric: 'Renewable Energy Ratio', ourValue: '42%', industryAvg: '35%', bestInClass: '75%', unit: '%', gap: 7, gapToBest: 33, direction: 'higher', percentile: 65, ranking: 'Good',
    recommendation: { title: 'Above Average', type: 'success', description: 'Continue expanding renewable energy procurement.' } },
  { id: 6, metric: 'Cooling COP', ourValue: '4.3', industryAvg: '3.8', bestInClass: '5.5', unit: '', gap: 0.5, gapToBest: 1.2, direction: 'higher', percentile: 58, ranking: 'Average',
    recommendation: { title: 'Moderate Performance', type: 'info', description: 'Cooling efficiency can be improved with economizer usage.' } },
  { id: 7, metric: 'Server Utilization', ourValue: '65%', industryAvg: '55%', bestInClass: '80%', unit: '%', gap: 10, gapToBest: 15, direction: 'higher', percentile: 70, ranking: 'Good',
    recommendation: { title: 'Good Performance', type: 'success', description: 'Server utilization is above industry average.' } },
  { id: 8, metric: 'Energy Cost per kW', ourValue: '$0.12', industryAvg: '$0.14', bestInClass: '$0.09', unit: '/kWh', gap: -0.02, gapToBest: 0.03, direction: 'lower', percentile: 60, ranking: 'Average',
    recommendation: { title: 'Cost Competitive', type: 'info', description: 'Energy costs are below industry average.' } }
]

// ==================== State ====================
const peerGroupFilter = ref('')
const facilityTypeFilter = ref('')
const metricFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const selectedMetric = ref<BenchmarkMetric | null>(null)

// Chart refs
let performanceChart: echarts.ECharts | null = null
let pueDistChart: echarts.ECharts | null = null
let cueDistChart: echarts.ECharts | null = null
let wueDistChart: echarts.ECharts | null = null
let intensityChart: echarts.ECharts | null = null
let reChart: echarts.ECharts | null = null
let coolingChart: echarts.ECharts | null = null
let distributionChart: echarts.ECharts | null = null

const performanceChartEl = ref<HTMLElement | null>(null)
const pueDistChartEl = ref<HTMLElement | null>(null)
const cueDistChartEl = ref<HTMLElement | null>(null)
const wueDistChartEl = ref<HTMLElement | null>(null)
const intensityChartEl = ref<HTMLElement | null>(null)
const reChartEl = ref<HTMLElement | null>(null)
const coolingChartEl = ref<HTMLElement | null>(null)
const distributionChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  const totalMetrics = benchmarkMetrics.length
  const topQuartile = benchmarkMetrics.filter(m => m.percentile >= 75).length
  const midQuartile = benchmarkMetrics.filter(m => m.percentile >= 25 && m.percentile < 75).length
  const bottomQuartile = benchmarkMetrics.filter(m => m.percentile < 25).length
  const overallScore = Math.round(benchmarkMetrics.reduce((sum, m) => sum + m.percentile, 0) / totalMetrics)

  return {
    overallScore: overallScore,
    scoreTrend: 3,
    topQuartile: topQuartile,
    topPercent: Math.round((topQuartile / totalMetrics) * 100),
    midQuartile: midQuartile,
    midPercent: Math.round((midQuartile / totalMetrics) * 100),
    bottomQuartile: bottomQuartile,
    bottomPercent: Math.round((bottomQuartile / totalMetrics) * 100)
  }
})

const metrics = computed(() => {
  const pueMetric = benchmarkMetrics.find(m => m.metric === 'Power Usage Effectiveness (PUE)')
  const cueMetric = benchmarkMetrics.find(m => m.metric === 'Carbon Usage Effectiveness (CUE)')
  const wueMetric = benchmarkMetrics.find(m => m.metric === 'Water Usage Effectiveness (WUE)')
  const itMetric = benchmarkMetrics.find(m => m.metric === 'IT Equipment Efficiency')

  return {
    pue: pueMetric?.ourValue || '0',
    pueTrend: -0.10,
    cue: cueMetric?.ourValue || '0',
    cueTrend: -0.052,
    wue: wueMetric?.ourValue || '0',
    wueTrend: -0.27,
    itEfficiency: itMetric?.ourValue || '0',
    itTrend: 4
  }
})

const filteredData = computed(() => {
  let filtered = [...benchmarkMetrics]

  if (metricFilter.value === 'pue') {
    filtered = filtered.filter(m => m.metric.includes('PUE'))
  } else if (metricFilter.value === 'cue') {
    filtered = filtered.filter(m => m.metric.includes('CUE'))
  } else if (metricFilter.value === 'wue') {
    filtered = filtered.filter(m => m.metric.includes('WUE'))
  } else if (metricFilter.value === 're') {
    filtered = filtered.filter(m => m.metric.includes('Renewable'))
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

const getRankingTagType = (ranking: string): string => {
  const map: Record<string, string> = { 'Excellent': 'success', 'Good': 'primary', 'Average': 'info', 'Poor': 'danger' }
  return map[ranking] || 'info'
}

const resetFilters = () => {
  peerGroupFilter.value = ''
  facilityTypeFilter.value = ''
  metricFilter.value = ''
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

  const metrics = ['PUE', 'CUE', 'WUE', 'IT Efficiency', 'RE Ratio', 'Cooling COP']
  const ourValues = [1.42, 0.298, 1.48, 72, 42, 4.3]
  const industryValues = [1.52, 0.35, 1.75, 68, 35, 3.8]

  performanceChart = echarts.init(performanceChartEl.value)
  performanceChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Our Performance', 'Industry Average'], bottom: 0 },
    grid: { top: 40, left: 60, right: 30, bottom: 50, containLabel: true },
    xAxis: { type: 'category', data: metrics, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: 'Value' },
    series: [
      { name: 'Our Performance', type: 'bar', data: ourValues, itemStyle: { color: '#3b82f6', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top' } },
      { name: 'Industry Average', type: 'bar', data: industryValues, itemStyle: { color: '#94a3b8', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top' } }
    ]
  })
}

const initPueDistChart = () => {
  if (!pueDistChartEl.value) return
  if (pueDistChart) {
    pueDistChart.dispose()
    pueDistChart = null
  }

  const ranges = ['1.0-1.2', '1.2-1.4', '1.4-1.6', '1.6-1.8', '1.8-2.0', '>2.0']
  const percentages = [5, 15, 35, 28, 12, 5]
  const ourPUE = 1.42

  pueDistChart = echarts.init(pueDistChartEl.value)
  pueDistChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: ranges },
    yAxis: { type: 'value', name: 'Percentage of Facilities (%)' },
    series: [{
      type: 'bar',
      data: percentages,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#3b82f6' },
      label: { show: true, position: 'top', formatter: '{c}%' },
      markLine: {
        data: [{ xAxis: 1, name: 'Our PUE' }],
        lineStyle: { color: '#ef4444', type: 'dashed', width: 2 },
        label: { formatter: 'Our PUE: 1.42' }
      }
    }]
  })
}

const initCueDistChart = () => {
  if (!cueDistChartEl.value) return
  if (cueDistChart) {
    cueDistChart.dispose()
    cueDistChart = null
  }

  const ranges = ['<0.2', '0.2-0.3', '0.3-0.4', '0.4-0.5', '>0.5']
  const percentages = [8, 22, 40, 20, 10]
  const ourCUE = 0.298

  cueDistChart = echarts.init(cueDistChartEl.value)
  cueDistChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: ranges },
    yAxis: { type: 'value', name: 'Percentage of Facilities (%)' },
    series: [{
      type: 'bar',
      data: percentages,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#22c55e' },
      label: { show: true, position: 'top', formatter: '{c}%' },
      markLine: {
        data: [{ xAxis: 1, name: 'Our CUE' }],
        lineStyle: { color: '#ef4444', type: 'dashed', width: 2 },
        label: { formatter: 'Our CUE: 0.298' }
      }
    }]
  })
}

const initWueDistChart = () => {
  if (!wueDistChartEl.value) return
  if (wueDistChart) {
    wueDistChart.dispose()
    wueDistChart = null
  }

  const ranges = ['<1.2', '1.2-1.5', '1.5-1.8', '1.8-2.1', '>2.1']
  const percentages = [10, 25, 35, 20, 10]
  const ourWUE = 1.48

  wueDistChart = echarts.init(wueDistChartEl.value)
  wueDistChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: ranges },
    yAxis: { type: 'value', name: 'Percentage of Facilities (%)' },
    series: [{
      type: 'bar',
      data: percentages,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#0ea5e9' },
      label: { show: true, position: 'top', formatter: '{c}%' },
      markLine: {
        data: [{ xAxis: 1, name: 'Our WUE' }],
        lineStyle: { color: '#ef4444', type: 'dashed', width: 2 },
        label: { formatter: 'Our WUE: 1.48' }
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

  const facilities = ['Our Facility', 'Peer A', 'Peer B', 'Peer C', 'Industry Avg']
  const intensities = [185, 210, 195, 225, 220]

  intensityChart = echarts.init(intensityChartEl.value)
  intensityChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: facilities, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'Energy Intensity (kWh/m²)' },
    series: [{
      type: 'bar',
      data: intensities,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          return params.name === 'Our Facility' ? '#3b82f6' : '#94a3b8'
        }
      },
      label: { show: true, position: 'top' }
    }]
  })
}

const initReChart = () => {
  if (!reChartEl.value) return
  if (reChart) {
    reChart.dispose()
    reChart = null
  }

  const facilities = ['Our Facility', 'Peer A', 'Peer B', 'Peer C', 'Industry Avg']
  const ratios = [42, 38, 45, 32, 35]

  reChart = echarts.init(reChartEl.value)
  reChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: facilities, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'Renewable Energy Ratio (%)', max: 100 },
    series: [{
      type: 'bar',
      data: ratios,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          return params.name === 'Our Facility' ? '#22c55e' : '#94a3b8'
        }
      },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initCoolingChart = () => {
  if (!coolingChartEl.value) return
  if (coolingChart) {
    coolingChart.dispose()
    coolingChart = null
  }

  const facilities = ['Our Facility', 'Peer A', 'Peer B', 'Peer C', 'Industry Avg']
  const cops = [4.3, 4.0, 4.5, 3.8, 3.8]

  coolingChart = echarts.init(coolingChartEl.value)
  coolingChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: facilities, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'Cooling COP' },
    series: [{
      type: 'bar',
      data: cops,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          return params.name === 'Our Facility' ? '#f59e0b' : '#94a3b8'
        }
      },
      label: { show: true, position: 'top' }
    }]
  })
}

const initDistributionChart = () => {
  if (!distributionChartEl.value || !selectedMetric.value) return
  if (distributionChart) {
    distributionChart.dispose()
    distributionChart = null
  }

  const values = []
  const baseValue = parseFloat(selectedMetric.value.industryAvg)
  for (let i = 0; i < 50; i++) {
    values.push(baseValue + (Math.random() - 0.5) * baseValue * 0.4)
  }

  const ourValue = parseFloat(selectedMetric.value.ourValue)

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
        data: [{ xAxis: ourValue, name: 'Our Value' }],
        lineStyle: { color: '#ef4444', width: 2 },
        label: { formatter: 'Our Value: ' + selectedMetric.value.ourValue }
      }
    }]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initPerformanceChart()
    initPueDistChart()
    initCueDistChart()
    initWueDistChart()
    initIntensityChart()
    initReChart()
    initCoolingChart()
  })
}

// ==================== Actions ====================
const viewMetricDetail = (metric: BenchmarkMetric) => {
  selectedMetric.value = metric
  detailDialogVisible.value = true
  nextTick(() => initDistributionChart())
}

const viewAllData = () => {
  ElMessage.info('Viewing all metrics')
}

const exportMetricReport = (metric: BenchmarkMetric | null) => {
  if (metric) {
    ElMessage.success(`Exporting report for ${metric.metric}...`)
    setTimeout(() => {
      ElMessage.success('Report generated successfully')
    }, 1500)
  }
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
    const charts = [performanceChart, pueDistChart, cueDistChart, wueDistChart, intensityChart, reChart, coolingChart, distributionChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([peerGroupFilter, facilityTypeFilter, metricFilter], () => {
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
  const charts = [performanceChart, pueDistChart, cueDistChart, wueDistChart, intensityChart, reChart, coolingChart, distributionChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.benchmark-comparison-page {
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
  max-height: 550px;
  overflow-y: auto;
}
:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}
</style>