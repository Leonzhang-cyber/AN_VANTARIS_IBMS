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
          <span class="loading-title">Asset Benchmark</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Industry Benchmarking & Performance Comparison</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="asset-benchmark-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Histogram /></el-icon>
          Asset Benchmark
        </h1>
        <div class="page-subtitle">Compare asset performance against industry standards and best practices</div>
      </div>
      <div class="header-actions">
        <el-button @click="exportData">
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
          <el-icon><Histogram /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalBenchmarks }}</div>
          <div class="stat-label">Benchmark Categories</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><TrendCharts /></el-icon>
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
        <div class="metric-title">Overall Performance Score</div>
        <div class="metric-value">{{ metrics.overallScore }}<span class="metric-unit">/100</span></div>
        <div class="metric-trend" :class="metrics.scoreTrend > 0 ? 'positive' : 'negative'">
          {{ metrics.scoreTrend > 0 ? '↑' : '↓' }} {{ Math.abs(metrics.scoreTrend) }} pts vs last year
        </div>
        <div class="metric-sub">Industry Average: 72</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Top Performing Category</div>
        <div class="metric-value">{{ metrics.topCategory }}</div>
        <div class="metric-sub">{{ metrics.topScore }}% above industry avg</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Improvement Opportunity</div>
        <div class="metric-value">{{ metrics.improvementCategory }}</div>
        <div class="metric-trend negative">Needs {{ metrics.improvementGap }}% improvement</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Rank vs Peers</div>
        <div class="metric-value">#{{ metrics.rank }}</div>
        <div class="metric-trend positive">Top {{ metrics.percentile }} percentile</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Performance vs Industry Benchmark</span>
          <span class="chart-subtitle">By asset category</span>
        </div>
        <div class="chart-container" ref="performanceChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Benchmark Scorecard</span>
          <span class="chart-subtitle">Overall metrics comparison</span>
        </div>
        <div class="chart-container" ref="scorecardChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Efficiency Benchmark</span>
          <span class="chart-subtitle">PUE vs Industry Standard</span>
        </div>
        <div class="chart-container" ref="efficiencyChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Cost Benchmark</span>
          <span class="chart-subtitle">O&M cost per asset</span>
        </div>
        <div class="chart-container" ref="costChartEl"></div>
      </div>
    </div>

    <!-- Third Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Reliability Benchmark</span>
          <span class="chart-subtitle">MTBF & MTTR comparison</span>
        </div>
        <div class="chart-container" ref="reliabilityChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Sustainability Benchmark</span>
          <span class="chart-subtitle">Carbon intensity comparison</span>
        </div>
        <div class="chart-container" ref="sustainabilityChartEl"></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by category or metric..."
            style="width: 240px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="categoryFilter" placeholder="Category" clearable style="width: 140px">
          <el-option v-for="c in uniqueCategories" :key="c" :label="c" :value="c" />
        </el-select>
        <el-select v-model="benchmarkTypeFilter" placeholder="Benchmark Type" clearable style="width: 140px">
          <el-option label="Performance" value="performance" />
          <el-option label="Efficiency" value="efficiency" />
          <el-option label="Cost" value="cost" />
          <el-option label="Reliability" value="reliability" />
          <el-option label="Sustainability" value="sustainability" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 130px">
          <el-option label="Above Average" value="above" />
          <el-option label="At Average" value="at" />
          <el-option label="Below Average" value="below" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Benchmark Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Benchmark Metrics</span>
        <el-button size="small" @click="viewAllMetrics">View All →</el-button>
      </div>
      <el-table :data="paginatedMetrics" stripe style="width: 100%" v-loading="tableLoading"
                @row-click="viewMetricDetail">
        <el-table-column prop="category" label="Category" width="160">
          <template #default="{ row }">
            <el-tag :type="getCategoryTagType(row.category)" size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="metric" label="Metric" min-width="200" />
        <el-table-column prop="ourValue" label="Our Performance" width="140" />
        <el-table-column prop="industryAvg" label="Industry Avg" width="140" />
        <el-table-column prop="bestInClass" label="Best in Class" width="140" />
        <el-table-column prop="gap" label="Gap" width="100">
          <template #default="{ row }">
            <span :class="getGapClass(row.gap, row.direction)">
              {{ row.gap > 0 ? '+' : '' }}{{ row.gap }}{{ row.unit }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="percentile" label="Percentile" width="120">
          <template #default="{ row }">
            <el-progress :percentage="row.percentile" :stroke-width="8" :color="getPercentileColor(row.percentile)" />
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click.stop="viewMetricDetail(row)">Details</el-button>
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
    <el-dialog v-model="detailDialogVisible" :title="selectedMetric?.metric" width="800px" class="metric-dialog">
      <div v-if="selectedMetric" class="metric-detail">
        <!-- Header Stats -->
        <div class="detail-header-stats">
          <div class="detail-stat">
            <div class="detail-stat-value" :style="{ color: getPercentileColor(selectedMetric.percentile) }">
              {{ selectedMetric.percentile }}%
            </div>
            <div class="detail-stat-label">Percentile Rank</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedMetric.ourValue }} {{ selectedMetric.unit }}</div>
            <div class="detail-stat-label">Our Performance</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedMetric.industryAvg }} {{ selectedMetric.unit }}</div>
            <div class="detail-stat-label">Industry Average</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedMetric.bestInClass }} {{ selectedMetric.unit }}</div>
            <div class="detail-stat-label">Best in Class</div>
          </div>
        </div>

        <!-- Basic Info -->
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Category">{{ selectedMetric.category }}</el-descriptions-item>
          <el-descriptions-item label="Metric Type">{{ selectedMetric.type }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(selectedMetric.status)" size="small">{{ getStatusText(selectedMetric.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Gap to Industry">
            <span :class="getGapClass(selectedMetric.gap, selectedMetric.direction)">
              {{ selectedMetric.gap > 0 ? '+' : '' }}{{ selectedMetric.gap }}{{ selectedMetric.unit }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="Gap to Best in Class" :span="2">
            <span :class="getGapClass(selectedMetric.gapToBest, selectedMetric.direction)">
              {{ selectedMetric.gapToBest > 0 ? '+' : '' }}{{ selectedMetric.gapToBest }}{{ selectedMetric.unit }}
            </span>
          </el-descriptions-item>
        </el-descriptions>

        <!-- Distribution Chart -->
        <div class="detail-section">
          <div class="section-title">Industry Distribution</div>
          <div class="distribution-chart" ref="distributionChartEl"></div>
        </div>

        <!-- Trend Chart -->
        <div class="detail-section">
          <div class="section-title">Performance Trend</div>
          <div class="trend-chart" ref="metricTrendChartEl"></div>
        </div>

        <!-- Recommendations -->
        <div class="detail-section">
          <div class="section-title">Recommendations</div>
          <el-alert
              :title="selectedMetric.recommendations.title"
              :type="selectedMetric.recommendations.type"
              :description="selectedMetric.recommendations.description"
              :closable="false"
              show-icon
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="generateBenchmarkReport(selectedMetric)">Generate Report</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Histogram, TrendCharts, Loading, Bottom, Download, Refresh,
  Search, RefreshLeft
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
  category: string
  metric: string
  type: string
  ourValue: number
  industryAvg: number
  bestInClass: number
  unit: string
  gap: number
  gapToBest: number
  direction: 'higher' | 'lower'
  percentile: number
  status: string
  distributionData: number[]
  trendData: { year: number; value: number }[]
  recommendations: {
    title: string
    type: 'success' | 'warning' | 'info' | 'error'
    description: string
  }
}

// ==================== Mock Data (45 benchmark metrics) ====================
const generateBenchmarkData = (): BenchmarkMetric[] => {
  const categories = ['UPS', 'Generator', 'CRAC', 'Chiller', 'Power Distribution', 'Cooling', 'Battery', 'Network']
  const metricsByCategory: Record<string, { metric: string; type: string; unit: string; direction: 'higher' | 'lower' }[]> = {
    'UPS': [
      { metric: 'UPS Efficiency', type: 'performance', unit: '%', direction: 'higher' },
      { metric: 'Battery Health', type: 'performance', unit: '%', direction: 'higher' },
      { metric: 'Mean Time Between Failures (MTBF)', type: 'reliability', unit: 'hrs', direction: 'higher' },
      { metric: 'Mean Time To Repair (MTTR)', type: 'reliability', unit: 'hrs', direction: 'lower' }
    ],
    'Generator': [
      { metric: 'Fuel Efficiency', type: 'efficiency', unit: 'L/kWh', direction: 'lower' },
      { metric: 'Start Reliability', type: 'reliability', unit: '%', direction: 'higher' },
      { metric: 'MTBF', type: 'reliability', unit: 'hrs', direction: 'higher' },
      { metric: 'Annual Maintenance Cost', type: 'cost', unit: '$', direction: 'lower' }
    ],
    'CRAC': [
      { metric: 'Cooling Efficiency (EER)', type: 'efficiency', unit: 'W/W', direction: 'higher' },
      { metric: 'Temperature Stability', type: 'performance', unit: '°C', direction: 'lower' },
      { metric: 'Fan Energy Consumption', type: 'cost', unit: 'kWh', direction: 'lower' },
      { metric: 'MTBF', type: 'reliability', unit: 'hrs', direction: 'higher' }
    ],
    'Chiller': [
      { metric: 'Coefficient of Performance (COP)', type: 'efficiency', unit: '', direction: 'higher' },
      { metric: 'kW per Ton', type: 'efficiency', unit: 'kW/ton', direction: 'lower' },
      { metric: 'Refrigerant Leak Rate', type: 'sustainability', unit: '%/year', direction: 'lower' },
      { metric: 'Maintenance Cost per Ton', type: 'cost', unit: '$', direction: 'lower' }
    ],
    'Power Distribution': [
      { metric: 'Power Quality (THD)', type: 'performance', unit: '%', direction: 'lower' },
      { metric: 'Switchgear Reliability', type: 'reliability', unit: '%', direction: 'higher' },
      { metric: 'Energy Losses', type: 'efficiency', unit: '%', direction: 'lower' },
      { metric: 'MTBF', type: 'reliability', unit: 'hrs', direction: 'higher' }
    ],
    'Cooling': [
      { metric: 'PUE', type: 'efficiency', unit: '', direction: 'lower' },
      { metric: 'Free Cooling Utilization', type: 'sustainability', unit: '%', direction: 'higher' },
      { metric: 'Water Usage Effectiveness (WUE)', type: 'sustainability', unit: 'L/kWh', direction: 'lower' },
      { metric: 'Cooling System Efficiency', type: 'performance', unit: '%', direction: 'higher' }
    ],
    'Battery': [
      { metric: 'Cycle Life', type: 'performance', unit: 'cycles', direction: 'higher' },
      { metric: 'Self-Discharge Rate', type: 'performance', unit: '%/month', direction: 'lower' },
      { metric: 'Replacement Frequency', type: 'cost', unit: 'years', direction: 'higher' },
      { metric: 'Energy Density', type: 'efficiency', unit: 'Wh/kg', direction: 'higher' }
    ],
    'Network': [
      { metric: 'Uptime', type: 'reliability', unit: '%', direction: 'higher' },
      { metric: 'Latency', type: 'performance', unit: 'ms', direction: 'lower' },
      { metric: 'Bandwidth Utilization', type: 'efficiency', unit: '%', direction: 'higher' },
      { metric: 'Packet Loss', type: 'performance', unit: '%', direction: 'lower' }
    ]
  }

  const metrics: BenchmarkMetric[] = []
  let id = 1

  for (const category of categories) {
    const categoryMetrics = metricsByCategory[category] || []
    for (const metricDef of categoryMetrics) {
      // Generate realistic values based on metric type
      let ourValue = 0
      let industryAvg = 0
      let bestInClass = 0

      if (metricDef.unit === '%' && metricDef.direction === 'higher') {
        industryAvg = 75 + Math.random() * 15
        ourValue = industryAvg + (Math.random() * 20 - 10)
        bestInClass = 98 + Math.random() * 2
      } else if (metricDef.unit === '%' && metricDef.direction === 'lower') {
        industryAvg = 5 + Math.random() * 10
        ourValue = industryAvg + (Math.random() * 15 - 7.5)
        bestInClass = 1 + Math.random() * 2
      } else if (metricDef.unit === 'hrs' || metricDef.metric.includes('MTBF')) {
        industryAvg = 50000 + Math.random() * 50000
        ourValue = industryAvg + (Math.random() * 40000 - 20000)
        bestInClass = 150000 + Math.random() * 50000
      } else if (metricDef.unit === '$') {
        industryAvg = 5000 + Math.random() * 10000
        ourValue = industryAvg + (Math.random() * 8000 - 4000)
        bestInClass = 2000 + Math.random() * 3000
      } else if (metricDef.metric === 'PUE') {
        industryAvg = 1.45 + Math.random() * 0.15
        ourValue = industryAvg + (Math.random() * 0.2 - 0.1)
        bestInClass = 1.15 + Math.random() * 0.05
      } else {
        industryAvg = 50 + Math.random() * 40
        ourValue = industryAvg + (Math.random() * 30 - 15)
        bestInClass = 85 + Math.random() * 10
      }

      ourValue = Math.round(ourValue * 10) / 10
      industryAvg = Math.round(industryAvg * 10) / 10
      bestInClass = Math.round(bestInClass * 10) / 10

      const gap = metricDef.direction === 'higher'
          ? ourValue - industryAvg
          : industryAvg - ourValue
      const gapToBest = metricDef.direction === 'higher'
          ? bestInClass - ourValue
          : ourValue - bestInClass

      // Calculate percentile (0-100)
      let percentile = 50
      if (metricDef.direction === 'higher') {
        percentile = Math.min(99, Math.max(1, 50 + (ourValue - industryAvg) / (bestInClass - industryAvg) * 25))
      } else {
        percentile = Math.min(99, Math.max(1, 50 + (industryAvg - ourValue) / (industryAvg - bestInClass) * 25))
      }
      percentile = Math.round(percentile)

      let status = ''
      if (percentile >= 75) status = 'above'
      else if (percentile >= 25) status = 'at'
      else status = 'below'

      // Generate distribution data (bell curve)
      const distributionData = []
      for (let i = -3; i <= 3; i += 0.5) {
        const x = industryAvg + i * (Math.abs(industryAvg - bestInClass) / 2)
        const y = Math.exp(-Math.pow(i, 2) / 2) / Math.sqrt(2 * Math.PI)
        distributionData.push({ x: Math.round(x * 10) / 10, y: Math.round(y * 100) / 100 })
      }

      // Generate trend data (last 5 years)
      const trendData = []
      for (let year = 2020; year <= 2024; year++) {
        let trendValue = ourValue - (2024 - year) * (gap / 5) + (Math.random() * 10 - 5)
        if (metricDef.direction === 'higher') {
          trendValue = Math.min(bestInClass, Math.max(industryAvg - 20, trendValue))
        } else {
          trendValue = Math.max(bestInClass, Math.min(industryAvg + 20, trendValue))
        }
        trendData.push({ year, value: Math.round(trendValue * 10) / 10 })
      }

      // Generate recommendations
      let recommendations = { title: '', type: 'info' as const, description: '' }
      if (status === 'below') {
        recommendations = {
          title: 'Improvement Opportunity Identified',
          type: 'error',
          description: `Performance is below industry average. Focus on ${metricDef.metric} improvement initiatives to close the ${Math.abs(gap)}${metricDef.unit} gap.`
        }
      } else if (status === 'at') {
        recommendations = {
          title: 'Maintain Current Performance',
          type: 'warning',
          description: `Performance is at industry average. Consider targeted improvements to reach best-in-class level (${bestInClass}${metricDef.unit}).`
        }
      } else {
        recommendations = {
          title: 'Industry Leader Performance',
          type: 'success',
          description: `Performance exceeds industry average by ${Math.abs(gap)}${metricDef.unit}. Continue best practices and share learnings across the organization.`
        }
      }

      metrics.push({
        id: id++,
        category: category,
        metric: metricDef.metric,
        type: metricDef.type,
        ourValue: ourValue,
        industryAvg: industryAvg,
        bestInClass: bestInClass,
        unit: metricDef.unit,
        gap: Math.abs(Math.round(gap * 10) / 10),
        gapToBest: Math.abs(Math.round(gapToBest * 10) / 10),
        direction: metricDef.direction,
        percentile: percentile,
        status: status,
        distributionData: distributionData.map(d => d.x),
        trendData: trendData,
        recommendations: recommendations
      })
    }
  }

  return metrics
}

const benchmarkMetrics = ref<BenchmarkMetric[]>(generateBenchmarkData())

// ==================== State ====================
const searchText = ref('')
const categoryFilter = ref('')
const benchmarkTypeFilter = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const selectedMetric = ref<BenchmarkMetric | null>(null)

// Chart refs
let performanceChart: echarts.ECharts | null = null
let scorecardChart: echarts.ECharts | null = null
let efficiencyChart: echarts.ECharts | null = null
let costChart: echarts.ECharts | null = null
let reliabilityChart: echarts.ECharts | null = null
let sustainabilityChart: echarts.ECharts | null = null
let distributionChart: echarts.ECharts | null = null
let metricTrendChart: echarts.ECharts | null = null

const performanceChartEl = ref<HTMLElement | null>(null)
const scorecardChartEl = ref<HTMLElement | null>(null)
const efficiencyChartEl = ref<HTMLElement | null>(null)
const costChartEl = ref<HTMLElement | null>(null)
const reliabilityChartEl = ref<HTMLElement | null>(null)
const sustainabilityChartEl = ref<HTMLElement | null>(null)
const distributionChartEl = ref<HTMLElement | null>(null)
const metricTrendChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  const totalBenchmarks = benchmarkMetrics.value.length
  const aboveAverage = benchmarkMetrics.value.filter(m => m.status === 'above').length
  const atAverage = benchmarkMetrics.value.filter(m => m.status === 'at').length
  const belowAverage = benchmarkMetrics.value.filter(m => m.status === 'below').length

  return {
    totalBenchmarks,
    aboveAverage,
    atAverage,
    belowAverage,
    abovePercent: Math.round((aboveAverage / totalBenchmarks) * 100),
    atPercent: Math.round((atAverage / totalBenchmarks) * 100),
    belowPercent: Math.round((belowAverage / totalBenchmarks) * 100)
  }
})

const metrics = computed(() => {
  const avgPercentile = benchmarkMetrics.value.reduce((sum, m) => sum + m.percentile, 0) / benchmarkMetrics.value.length
  const overallScore = Math.round(avgPercentile)

  // Find top and bottom categories
  const categoryScores = new Map<string, { total: number; count: number }>()
  benchmarkMetrics.value.forEach(m => {
    const existing = categoryScores.get(m.category) || { total: 0, count: 0 }
    existing.total += m.percentile
    existing.count++
    categoryScores.set(m.category, existing)
  })

  let topCategory = ''
  let topScore = 0
  let improvementCategory = ''
  let improvementGap = 0

  for (const [cat, data] of categoryScores) {
    const avgScore = data.total / data.count
    if (avgScore > topScore) {
      topScore = avgScore
      topCategory = cat
    }
  }

  for (const [cat, data] of categoryScores) {
    const avgScore = data.total / data.count
    if (avgScore < 100 && (100 - avgScore) > improvementGap) {
      improvementGap = 100 - avgScore
      improvementCategory = cat
    }
  }

  return {
    overallScore,
    scoreTrend: 3.5,
    topCategory,
    topScore: Math.round(topScore - 50),
    improvementCategory,
    improvementGap: Math.round(improvementGap),
    rank: 15,
    percentile: 87
  }
})

const uniqueCategories = computed(() => {
  return [...new Set(benchmarkMetrics.value.map(m => m.category))]
})

const filteredMetrics = computed(() => {
  let filtered = [...benchmarkMetrics.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(m =>
        m.metric.toLowerCase().includes(search) ||
        m.category.toLowerCase().includes(search)
    )
  }

  if (categoryFilter.value) {
    filtered = filtered.filter(m => m.category === categoryFilter.value)
  }

  if (benchmarkTypeFilter.value) {
    filtered = filtered.filter(m => m.type === benchmarkTypeFilter.value)
  }

  if (statusFilter.value) {
    filtered = filtered.filter(m => m.status === statusFilter.value)
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
    'UPS': 'primary', 'Generator': 'warning', 'CRAC': 'info', 'Chiller': 'danger',
    'Power Distribution': 'success', 'Cooling': 'info', 'Battery': 'warning', 'Network': ''
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

const getStatusText = (status: string): string => {
  const map: Record<string, string> = { above: 'Above Average', at: 'At Average', below: 'Below Average' }
  return map[status] || status
}

const getStatusTagType = (status: string): string => {
  const map: Record<string, string> = { above: 'success', at: 'info', below: 'danger' }
  return map[status] || 'info'
}

const resetFilters = () => {
  searchText.value = ''
  categoryFilter.value = ''
  benchmarkTypeFilter.value = ''
  statusFilter.value = ''
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

  const categories = ['UPS', 'Generator', 'CRAC', 'Chiller', 'Power Distribution', 'Cooling']
  const ourScores = [82, 78, 85, 72, 88, 76]
  const industryScores = [75, 74, 80, 78, 82, 79]
  const bestScores = [95, 92, 94, 91, 96, 93]

  performanceChart = echarts.init(performanceChartEl.value)
  performanceChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Our Performance', 'Industry Average', 'Best in Class'], bottom: 0 },
    grid: { top: 40, left: 60, right: 30, bottom: 40, containLabel: true },
    xAxis: { type: 'category', data: categories, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: 'Performance Score', min: 60, max: 100 },
    series: [
      { name: 'Our Performance', type: 'line', data: ourScores, lineStyle: { color: '#3b82f6', width: 3 }, symbol: 'circle', symbolSize: 8, label: { show: true, position: 'top' } },
      { name: 'Industry Average', type: 'line', data: industryScores, lineStyle: { color: '#94a3b8', width: 2, type: 'dashed' }, symbol: 'diamond', symbolSize: 8 },
      { name: 'Best in Class', type: 'line', data: bestScores, lineStyle: { color: '#22c55e', width: 2 }, symbol: 'triangle', symbolSize: 8 }
    ]
  })
}

const initScorecardChart = () => {
  if (!scorecardChartEl.value) return
  if (scorecardChart) {
    scorecardChart.dispose()
    scorecardChart = null
  }

  scorecardChart = echarts.init(scorecardChartEl.value)
  scorecardChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: ['Efficiency', 'Reliability', 'Cost', 'Sustainability', 'Performance'] },
    yAxis: { type: 'value', name: 'Score', min: 60, max: 100 },
    series: [{
      type: 'bar',
      data: [82, 78, 75, 80, 79],
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value >= 85) return '#22c55e'
          if (value >= 75) return '#3b82f6'
          return '#f59e0b'
        }
      },
      label: { show: true, position: 'top' }
    }]
  })
}

const initEfficiencyChart = () => {
  if (!efficiencyChartEl.value) return
  if (efficiencyChart) {
    efficiencyChart.dispose()
    efficiencyChart = null
  }

  efficiencyChart = echarts.init(efficiencyChartEl.value)
  efficiencyChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Our PUE', 'Industry Average'], bottom: 0 },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: ['2020', '2021', '2022', '2023', '2024'] },
    yAxis: { type: 'value', name: 'PUE', min: 1.2, max: 1.8 },
    series: [
      { name: 'Our PUE', type: 'line', data: [1.62, 1.58, 1.52, 1.47, 1.42], lineStyle: { color: '#3b82f6', width: 3 }, symbol: 'circle', symbolSize: 8, areaStyle: { opacity: 0.1 }, label: { show: true } },
      { name: 'Industry Average', type: 'line', data: [1.58, 1.55, 1.52, 1.48, 1.46], lineStyle: { color: '#94a3b8', width: 2, type: 'dashed' } }
    ]
  })
}

const initCostChart = () => {
  if (!costChartEl.value) return
  if (costChart) {
    costChart.dispose()
    costChart = null
  }

  costChart = echarts.init(costChartEl.value)
  costChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['Our Cost', 'Industry Avg', 'Best in Class'], bottom: 0 },
    grid: { top: 30, left: 60, right: 30, bottom: 40, containLabel: true },
    xAxis: { type: 'category', data: ['UPS', 'Generator', 'CRAC', 'Chiller', 'Cooling'], axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'Annual O&M Cost ($K)' },
    series: [
      { name: 'Our Cost', type: 'bar', data: [45, 120, 35, 180, 28], itemStyle: { color: '#f59e0b', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top', formatter: '${c}K' } },
      { name: 'Industry Avg', type: 'bar', data: [42, 115, 32, 165, 26], itemStyle: { color: '#94a3b8', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top', formatter: '${c}K' } },
      { name: 'Best in Class', type: 'bar', data: [38, 100, 28, 140, 22], itemStyle: { color: '#22c55e', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top', formatter: '${c}K' } }
    ]
  })
}

const initReliabilityChart = () => {
  if (!reliabilityChartEl.value) return
  if (reliabilityChart) {
    reliabilityChart.dispose()
    reliabilityChart = null
  }

  reliabilityChart = echarts.init(reliabilityChartEl.value)
  reliabilityChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['MTBF (K hrs)', 'MTTR (hrs)'], bottom: 0 },
    grid: { top: 30, left: 60, right: 60, bottom: 40 },
    xAxis: { type: 'category', data: ['UPS', 'Generator', 'CRAC', 'Chiller'] },
    yAxis: [
      { type: 'value', name: 'MTBF (K hrs)', position: 'left' },
      { type: 'value', name: 'MTTR (hrs)', position: 'right' }
    ],
    series: [
      { name: 'MTBF (K hrs)', type: 'bar', data: [85, 65, 75, 55], itemStyle: { color: '#22c55e', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top' } },
      { name: 'MTTR (hrs)', type: 'line', data: [4.2, 5.8, 4.5, 6.2], lineStyle: { color: '#ef4444', width: 3 }, symbol: 'circle', symbolSize: 8, label: { show: true, position: 'top' }, yAxisIndex: 1 }
    ]
  })
}

const initSustainabilityChart = () => {
  if (!sustainabilityChartEl.value) return
  if (sustainabilityChart) {
    sustainabilityChart.dispose()
    sustainabilityChart = null
  }

  sustainabilityChart = echarts.init(sustainabilityChartEl.value)
  sustainabilityChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['Our Carbon Intensity', 'Industry Avg'], bottom: 0 },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: ['UPS', 'Generator', 'CRAC', 'Chiller', 'Cooling'] },
    yAxis: { type: 'value', name: 'Carbon Intensity (tCO2e/kWh)' },
    series: [
      { name: 'Our Carbon Intensity', type: 'bar', data: [0.42, 0.58, 0.35, 0.62, 0.38], itemStyle: { color: '#3b82f6', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top' } },
      { name: 'Industry Avg', type: 'bar', data: [0.45, 0.62, 0.38, 0.68, 0.42], itemStyle: { color: '#94a3b8', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top' } }
    ]
  })
}

const initDistributionChart = () => {
  if (!distributionChartEl.value || !selectedMetric.value) return
  if (distributionChart) {
    distributionChart.dispose()
    distributionChart = null
  }

  // Simulate normal distribution around industry average
  const data = []
  for (let i = 0; i < 1000; i++) {
    const value = selectedMetric.value.industryAvg + (Math.random() - 0.5) * (selectedMetric.value.industryAvg * 0.3)
    data.push(value)
  }

  distributionChart = echarts.init(distributionChartEl.value)
  distributionChart.setOption({
    tooltip: { trigger: 'axis' },
    title: { show: false },
    xAxis: { name: 'Value', type: 'value' },
    yAxis: { name: 'Frequency', type: 'value' },
    series: [{
      type: 'histogram',
      data: data,
      itemStyle: { color: '#3b82f6' },
      label: { show: false }
    }],
    toolbox: { show: false }
  })
}

const initMetricTrendChart = () => {
  if (!metricTrendChartEl.value || !selectedMetric.value) return
  if (metricTrendChart) {
    metricTrendChart.dispose()
    metricTrendChart = null
  }

  const years = selectedMetric.value.trendData.map(d => d.year)
  const values = selectedMetric.value.trendData.map(d => d.value)
  const industryValues = [65, 68, 72, 74, 76]

  metricTrendChart = echarts.init(metricTrendChartEl.value)
  metricTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Our Performance', 'Industry Trend'], bottom: 0 },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: years },
    yAxis: { type: 'value', name: 'Score' },
    series: [
      { name: 'Our Performance', type: 'line', data: values, lineStyle: { color: '#3b82f6', width: 3 }, symbol: 'circle', symbolSize: 8, areaStyle: { opacity: 0.1 }, label: { show: true } },
      { name: 'Industry Trend', type: 'line', data: industryValues, lineStyle: { color: '#94a3b8', width: 2, type: 'dashed' } }
    ]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initPerformanceChart()
    initScorecardChart()
    initEfficiencyChart()
    initCostChart()
    initReliabilityChart()
    initSustainabilityChart()
  })
}

// ==================== Actions ====================
const viewMetricDetail = (metric: BenchmarkMetric) => {
  selectedMetric.value = metric
  detailDialogVisible.value = true
  nextTick(() => {
    initDistributionChart()
    initMetricTrendChart()
  })
}

const viewAllMetrics = () => {
  ElMessage.info('Viewing all benchmark metrics')
}

const generateBenchmarkReport = (metric: BenchmarkMetric | null) => {
  if (!metric) return
  ElMessage.success(`Generating benchmark report for ${metric.metric}...`)
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
    const charts = [performanceChart, scorecardChart, efficiencyChart, costChart, reliabilityChart, sustainabilityChart, distributionChart, metricTrendChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([searchText, categoryFilter, benchmarkTypeFilter, statusFilter], () => {
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
  const charts = [performanceChart, scorecardChart, efficiencyChart, costChart, reliabilityChart, sustainabilityChart, distributionChart, metricTrendChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.asset-benchmark-page {
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

/* Loading Screen - reuse from previous pages */
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
  font-size: 28px;
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
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
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

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
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

.detail-header-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 16px;
}

.detail-stat {
  text-align: center;
}

.detail-stat-value {
  font-size: 24px;
  font-weight: 700;
}

.detail-stat-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

.detail-section {
  margin-bottom: 24px;
}

.section-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 16px;
  padding-left: 10px;
  border-left: 3px solid #3b82f6;
}

.distribution-chart, .trend-chart {
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
  .detail-header-stats {
    grid-template-columns: repeat(2, 1fr);
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
  .filter-left .el-select {
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