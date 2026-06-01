<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted, computed } from 'vue'
import {
  Search, RefreshRight, Warning, CircleCheck, Clock,
  TrendCharts, Monitor, Connection, DataAnalysis,
  Document, Setting, More, ArrowUp, ArrowDown,
  VideoCamera, Histogram, Grid, Platform, Link,
  Tickets, Timer, Timer as Stopwatch, PieChart
} from "@element-plus/icons-vue"
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading failure rate data...',
  'Analyzing failure patterns...',
  'Calculating reliability metrics...'
]

// Date range
const dateRange = ref<[Date, Date]>([
  new Date(new Date().setDate(new Date().getDate() - 365)),
  new Date()
])

// Failure Rate Data by Device Type
const failureRateData = ref([
  { deviceType: 'UPS', failureRate: 0.82, targetRate: 1.0, totalFailures: 8, operatingHours: 975000, trend: 'down', status: 'excellent', mtbf: 12187 },
  { deviceType: 'Chiller', failureRate: 1.35, targetRate: 1.2, totalFailures: 12, operatingHours: 888000, trend: 'up', status: 'warning', mtbf: 7400 },
  { deviceType: 'AHU', failureRate: 1.67, targetRate: 1.5, totalFailures: 15, operatingHours: 900000, trend: 'stable', status: 'good', mtbf: 6000 },
  { deviceType: 'CRAC', failureRate: 1.76, targetRate: 1.5, totalFailures: 16, operatingHours: 909000, trend: 'up', status: 'warning', mtbf: 5681 },
  { deviceType: 'VFD', failureRate: 2.18, targetRate: 2.0, totalFailures: 20, operatingHours: 917000, trend: 'down', status: 'good', mtbf: 4585 },
  { deviceType: 'Controller', failureRate: 1.22, targetRate: 1.2, totalFailures: 11, operatingHours: 900000, trend: 'stable', status: 'good', mtbf: 8182 },
  { deviceType: 'Sensor', failureRate: 2.85, targetRate: 2.5, totalFailures: 26, operatingHours: 912000, trend: 'up', status: 'critical', mtbf: 3508 },
  { deviceType: 'Pump', failureRate: 1.97, targetRate: 2.0, totalFailures: 18, operatingHours: 915000, trend: 'stable', status: 'good', mtbf: 5083 },
  { deviceType: 'Transformer', failureRate: 0.65, targetRate: 0.8, totalFailures: 6, operatingHours: 925000, trend: 'down', status: 'excellent', mtbf: 15417 },
  { deviceType: 'Generator', failureRate: 0.80, targetRate: 0.9, totalFailures: 7, operatingHours: 875000, trend: 'stable', status: 'excellent', mtbf: 12500 }
])

// Monthly failure rate trend
const monthlyTrend = ref([
  { month: 'Aug', failureRate: 1.62, targetRate: 1.55, failures: 14, operatingHours: 76500 },
  { month: 'Sep', failureRate: 1.58, targetRate: 1.55, failures: 13, operatingHours: 77200 },
  { month: 'Oct', failureRate: 1.54, targetRate: 1.55, failures: 12, operatingHours: 77800 },
  { month: 'Nov', failureRate: 1.49, targetRate: 1.55, failures: 11, operatingHours: 78500 },
  { month: 'Dec', failureRate: 1.45, targetRate: 1.55, failures: 10, operatingHours: 79200 },
  { month: 'Jan', failureRate: 1.42, targetRate: 1.55, failures: 9, operatingHours: 79800 }
])

// Failure rate by location
const locationFailureRate = ref([
  { location: 'Data Center A', failureRate: 1.52, devices: 45, trend: 'down', severity: 'good' },
  { location: 'Data Center B', failureRate: 1.48, devices: 38, trend: 'stable', severity: 'good' },
  { location: 'Central Plant', failureRate: 1.85, devices: 52, trend: 'up', severity: 'warning' },
  { location: 'Office Building', failureRate: 1.25, devices: 28, trend: 'down', severity: 'excellent' },
  { location: 'Warehouse', failureRate: 1.08, devices: 22, trend: 'stable', severity: 'excellent' }
])

// Failure rate by severity
const severityFailureRate = ref([
  { severity: 'Critical', failureRate: 0.85, totalFailures: 18, percentage: 12 },
  { severity: 'Major', failureRate: 1.45, totalFailures: 42, percentage: 28 },
  { severity: 'Warning', failureRate: 2.15, totalFailures: 68, percentage: 45 },
  { severity: 'Minor', failureRate: 0.65, totalFailures: 22, percentage: 15 }
])

// Top failure modes
const failureModes = ref([
  { mode: 'Component Aging', failureRate: 2.85, percentage: 22.4, trend: 'up', deviceType: 'Sensor' },
  { mode: 'Electrical Fault', failureRate: 2.45, percentage: 19.2, trend: 'stable', deviceType: 'VFD' },
  { mode: 'Mechanical Wear', failureRate: 2.25, percentage: 17.6, trend: 'up', deviceType: 'Pump' },
  { mode: 'Calibration Drift', failureRate: 1.85, percentage: 14.4, trend: 'down', deviceType: 'Controller' },
  { mode: 'Communication Loss', failureRate: 1.65, percentage: 12.8, trend: 'stable', deviceType: 'Network' },
  { mode: 'Environmental', failureRate: 1.05, percentage: 8.0, trend: 'down', deviceType: 'CRAC' }
])

// Year-over-year comparison
const yoyComparison = ref([
  { year: '2023', failureRate: 1.82, totalFailures: 142, operatingHours: 920000 },
  { year: '2024', failureRate: 1.58, totalFailures: 125, operatingHours: 925000 }
])

// Summary statistics
const summaryStats = ref({
  overallFailureRate: 1.48,
  targetFailureRate: 1.55,
  totalFailures: 139,
  totalOperatingHours: 9250000,
  annualImprovement: 13.2,
  bestPerformer: 'Transformer',
  bestRate: 0.65,
  needsAttention: 'Sensor',
  worstRate: 2.85
})

// Chart refs
const failureChartRef = ref<HTMLElement | null>(null)
const trendChartRef = ref<HTMLElement | null>(null)
const severityChartRef = ref<HTMLElement | null>(null)
let failureChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null
let severityChart: echarts.ECharts | null = null

const getStatusColor = (status: string) => {
  switch(status) {
    case 'excellent': return '#67C23A'
    case 'good': return '#409EFF'
    case 'warning': return '#E6A23C'
    case 'critical': return '#F56C6C'
    default: return '#909399'
  }
}

const getStatusText = (status: string) => {
  switch(status) {
    case 'excellent': return 'Excellent'
    case 'good': return 'Good'
    case 'warning': return 'Warning'
    case 'critical': return 'Critical'
    default: return 'Unknown'
  }
}

const getTrendIcon = (trend: string) => {
  if (trend === 'up') return ArrowUp
  if (trend === 'down') return ArrowDown
  return null
}

const refreshData = () => {
  ElMessage.info('Refreshing failure rate data...')
  setTimeout(() => {
    ElMessage.success('Data refreshed successfully')
  }, 1000)
}

const exportReport = () => {
  ElMessage.success('Exporting failure rate report...')
}

const initFailureChart = () => {
  if (failureChartRef.value) {
    if (failureChart) failureChart.dispose()

    failureChart = echarts.init(failureChartRef.value)
    failureChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['Failure Rate (%)', 'Target Rate (%)'], left: 'left' },
      grid: { left: '8%', right: '5%', top: '10%', bottom: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: failureRateData.value.map(d => d.deviceType),
        axisLabel: { rotate: 45, fontWeight: 500 }
      },
      yAxis: { type: 'value', name: 'Failure Rate (%)', min: 0, max: 3.5 },
      series: [
        {
          name: 'Failure Rate (%)',
          type: 'bar',
          data: failureRateData.value.map(d => d.failureRate),
          itemStyle: {
            color: (params: any) => {
              const status = failureRateData.value[params.dataIndex].status
              return getStatusColor(status)
            },
            borderRadius: [4, 4, 0, 0]
          },
          label: { show: true, position: 'top', formatter: '{c}%' }
        },
        {
          name: 'Target Rate (%)',
          type: 'line',
          data: failureRateData.value.map(d => d.targetRate),
          lineStyle: { color: '#909399', width: 2, type: 'dashed' },
          symbol: 'diamond',
          symbolSize: 6,
          label: { show: true, position: 'top', formatter: '{c}%' }
        }
      ]
    })
  }
}

const initTrendChart = () => {
  if (trendChartRef.value) {
    if (trendChart) trendChart.dispose()

    trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Failure Rate (%)', 'Target Rate (%)', 'Number of Failures'], left: 'left' },
      grid: { left: '8%', right: '8%', top: '15%', bottom: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: monthlyTrend.value.map(d => d.month),
        axisLabel: { fontWeight: 500 }
      },
      yAxis: [
        { type: 'value', name: 'Failure Rate (%)', min: 1.2, max: 1.8 },
        { type: 'value', name: 'Number of Failures', min: 0, max: 20 }
      ],
      series: [
        {
          name: 'Failure Rate (%)',
          type: 'line',
          data: monthlyTrend.value.map(d => d.failureRate),
          smooth: true,
          lineStyle: { color: '#F56C6C', width: 3 },
          areaStyle: { opacity: 0.1, color: '#F56C6C' },
          symbol: 'circle',
          symbolSize: 8,
          label: { show: true, position: 'top', formatter: '{c}%' }
        },
        {
          name: 'Target Rate (%)',
          type: 'line',
          data: monthlyTrend.value.map(d => d.targetRate),
          lineStyle: { color: '#909399', width: 2, type: 'dashed' },
          symbol: 'diamond',
          symbolSize: 6,
          label: { show: true, position: 'top', formatter: '{c}%' }
        },
        {
          name: 'Number of Failures',
          type: 'bar',
          yAxisIndex: 1,
          data: monthlyTrend.value.map(d => d.failures),
          itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] },
          label: { show: true, position: 'top' }
        }
      ]
    })
  }
}

const initSeverityChart = () => {
  if (severityChartRef.value) {
    if (severityChart) severityChart.dispose()

    severityChart = echarts.init(severityChartRef.value)
    severityChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} failures)' },
      legend: { orient: 'vertical', left: 'left', top: 'center' },
      series: [
        {
          name: 'Failures by Severity',
          type: 'pie',
          radius: ['40%', '65%'],
          data: severityFailureRate.value.map(s => ({ name: s.severity, value: s.totalFailures })),
          label: { show: true, formatter: '{b}: {d}%' },
          emphasis: { scale: true },
          itemStyle: {
            borderRadius: 8,
            borderColor: '#fff',
            borderWidth: 2,
            color: (params: any) => {
              const severity = severityFailureRate.value[params.dataIndex].severity
              if (severity === 'Critical') return '#F56C6C'
              if (severity === 'Major') return '#E6A23C'
              if (severity === 'Warning') return '#409EFF'
              return '#67C23A'
            }
          }
        }
      ]
    })
  }
}

const handleResize = () => {
  failureChart?.resize()
  trendChart?.resize()
  severityChart?.resize()
}

watch(isLoaded, (loaded) => {
  if (loaded) {
    nextTick(() => {
      initFailureChart()
      initTrendChart()
      initSeverityChart()
      window.addEventListener('resize', handleResize)
    })
  }
})

onMounted(() => {
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 400)

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(() => {
      isLoaded.value = true
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  failureChart?.dispose()
  trendChart?.dispose()
  severityChart?.dispose()
})

// Helper computed
const targetAchieved = computed(() => {
  return summaryStats.value.overallFailureRate <= summaryStats.value.targetFailureRate
})
</script>

<template>
  <!-- Loading Screen -->
  <div v-if="!isLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">
          <span class="loading-title">Loading</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Failure Rate Analytics</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="failure-rate-analytics">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Failure Rate Analytics</h2>
        <p class="subtitle">Equipment reliability and failure frequency metrics</p>
      </div>
      <div class="header-actions">
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            size="default"
            style="width: 260px"
        />
        <el-button type="primary" @click="refreshData">
          <el-icon><RefreshRight /></el-icon> Refresh
        </el-button>
        <el-button @click="exportReport">
          <el-icon><Document /></el-icon> Export
        </el-button>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="kpi-grid">
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-content">
          <div class="kpi-icon overall">
            <el-icon><PieChart /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value" :style="{ color: targetAchieved ? '#67C23A' : '#F56C6C' }">
              {{ summaryStats.overallFailureRate }}%
            </div>
            <div class="kpi-label">Overall Failure Rate</div>
            <div class="kpi-sub">Target: {{ summaryStats.targetFailureRate }}%</div>
          </div>
        </div>
      </el-card>
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-content">
          <div class="kpi-icon failures">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ summaryStats.totalFailures }}</div>
            <div class="kpi-label">Total Failures</div>
            <div class="kpi-sub">Last 12 Months</div>
          </div>
        </div>
      </el-card>
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-content">
          <div class="kpi-icon improvement">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ summaryStats.annualImprovement }}%</div>
            <div class="kpi-label">Year-over-Year</div>
            <div class="kpi-sub">Improvement</div>
          </div>
        </div>
      </el-card>
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-content">
          <div class="kpi-icon best">
            <el-icon><Trophy /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ summaryStats.bestPerformer }}</div>
            <div class="kpi-label">Best Performer</div>
            <div class="kpi-sub">{{ summaryStats.bestRate }}% Failure Rate</div>
          </div>
        </div>
      </el-card>
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-content">
          <div class="kpi-icon attention">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ summaryStats.needsAttention }}</div>
            <div class="kpi-label">Needs Attention</div>
            <div class="kpi-sub">{{ summaryStats.worstRate }}% Failure Rate</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Failure Rate by Device Type Chart -->
    <el-card class="chart-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Failure Rate by Device Type</span>
          <el-tag type="info" size="small">vs Target</el-tag>
        </div>
      </template>
      <div ref="failureChartRef" class="chart"></div>
    </el-card>

    <!-- Two Column Charts -->
    <div class="charts-row">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Failure Rate Trend & Analysis</span>
            <el-tag type="success" size="small">Improving</el-tag>
          </div>
        </template>
        <div ref="trendChartRef" class="chart"></div>
      </el-card>

      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Failures by Severity Distribution</span>
            <el-tag type="warning" size="small">Impact Analysis</el-tag>
          </div>
        </template>
        <div ref="severityChartRef" class="chart"></div>
      </el-card>
    </div>

    <!-- Failure Rate by Location -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Failure Rate by Location</span>
          <el-tag type="info" size="small">Facility Comparison</el-tag>
        </div>
      </template>
      <el-table :data="locationFailureRate" stripe>
        <el-table-column prop="location" label="Location" />
        <el-table-column label="Failure Rate" align="center">
          <template #default="{ row }">
            <div class="metric-cell">
              <span class="rate-value" :style="{ color: getStatusColor(row.severity) }">{{ row.failureRate }}%</span>
              <el-icon v-if="row.trend === 'up'" class="trend-up"><ArrowUp /></el-icon>
              <el-icon v-else-if="row.trend === 'down'" class="trend-down"><ArrowDown /></el-icon>
              <span v-else class="trend-stable">→</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="devices" label="Number of Devices" align="center" />
        <el-table-column label="Status" align="center">
          <template #default="{ row }">
            <el-tag :type="row.severity === 'excellent' ? 'success' : row.severity === 'good' ? 'primary' : row.severity === 'warning' ? 'warning' : 'danger'" size="small">
              {{ getStatusText(row.severity) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Performance vs Average" align="center">
          <template #default="{ row }">
            <div class="performance-badge" :class="row.failureRate <= summaryStats.overallFailureRate ? 'good-badge' : 'bad-badge'">
              {{ ((row.failureRate / summaryStats.overallFailureRate - 1) * 100).toFixed(1) }}% vs avg
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Failure Modes Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Top Failure Modes & Root Causes</span>
          <el-tag type="warning" size="small">Action Required</el-tag>
        </div>
      </template>
      <el-table :data="failureModes" stripe>
        <el-table-column prop="mode" label="Failure Mode" />
        <el-table-column prop="deviceType" label="Affected Device" align="center" />
        <el-table-column label="Failure Rate" align="center">
          <template #default="{ row }">
            <span :style="{ color: row.failureRate > 2.5 ? '#F56C6C' : row.failureRate > 1.8 ? '#E6A23C' : '#67C23A' }">
              {{ row.failureRate }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Percentage" align="center">
          <template #default="{ row }">
            {{ row.percentage }}%
          </template>
        </el-table-column>
        <el-table-column label="Trend" align="center">
          <template #default="{ row }">
            <div class="trend-cell">
              <el-icon v-if="row.trend === 'up'" class="trend-up"><ArrowUp /></el-icon>
              <el-icon v-else-if="row.trend === 'down'" class="trend-down"><ArrowDown /></el-icon>
              <span v-else class="trend-stable">→</span>
              <span>{{ row.trend }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Recommendation" align="center">
          <template #default="{ row }">
            <span v-if="row.mode === 'Component Aging'">Implement predictive maintenance</span>
            <span v-else-if="row.mode === 'Electrical Fault'">Upgrade protection systems</span>
            <span v-else-if="row.mode === 'Mechanical Wear'">Increase lubrication frequency</span>
            <span v-else-if="row.mode === 'Calibration Drift'">Schedule quarterly calibration</span>
            <span v-else-if="row.mode === 'Communication Loss'">Check network infrastructure</span>
            <span v-else>Improve environmental controls</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Year-over-Year Comparison -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Year-over-Year Comparison</span>
          <el-tag type="success" size="small">Performance Trend</el-tag>
        </div>
      </template>
      <el-table :data="yoyComparison" stripe>
        <el-table-column prop="year" label="Year" align="center" />
        <el-table-column label="Failure Rate" align="center">
          <template #default="{ row }">
            <span :style="{ color: row.year === '2024' ? '#67C23A' : '#E6A23C' }">
              {{ row.failureRate }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Total Failures" align="center">
          <template #default="{ row }">
            {{ row.totalFailures }}
          </template>
        </el-table-column>
        <el-table-column label="Operating Hours" align="center">
          <template #default="{ row }">
            {{ (row.operatingHours / 1000).toFixed(0) }}k hours
          </template>
        </el-table-column>
        <el-table-column label="Improvement" align="center">
          <template #default="{ row }">
            <span v-if="row.year === '2024'" class="trend-down">
              {{ summaryStats.annualImprovement }}% ↓
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Detailed Failure Rate Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Detailed Failure Rate Analysis by Device Type</span>
          <el-tag type="info" size="small">Full Breakdown</el-tag>
        </div>
      </template>
      <el-table :data="failureRateData" stripe>
        <el-table-column prop="deviceType" label="Device Type" />
        <el-table-column label="Failure Rate" align="center">
          <template #default="{ row }">
            <span class="rate-value" :style="{ color: getStatusColor(row.status) }">{{ row.failureRate }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="Target Rate" align="center">
          <template #default="{ row }">
            {{ row.targetRate }}%
          </template>
        </el-table-column>
        <el-table-column label="Gap" align="center">
          <template #default="{ row }">
            <span :class="row.failureRate <= row.targetRate ? 'trend-down' : 'trend-up'">
              {{ ((row.failureRate / row.targetRate - 1) * 100).toFixed(1) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Total Failures" align="center">
          <template #default="{ row }">
            {{ row.totalFailures }}
          </template>
        </el-table-column>
        <el-table-column label="Operating Hours" align="center">
          <template #default="{ row }">
            {{ (row.operatingHours / 1000).toFixed(0) }}k hrs
          </template>
        </el-table-column>
        <el-table-column label="MTBF" align="center">
          <template #default="{ row }">
            {{ row.mtbf.toLocaleString() }}h
          </template>
        </el-table-column>
        <el-table-column label="Status" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'excellent' ? 'success' : row.status === 'good' ? 'primary' : row.status === 'warning' ? 'warning' : 'danger'" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Trend" align="center">
          <template #default="{ row }">
            <div class="trend-cell">
              <el-icon v-if="row.trend === 'up'" class="trend-up"><ArrowUp /></el-icon>
              <el-icon v-else-if="row.trend === 'down'" class="trend-down"><ArrowDown /></el-icon>
              <span v-else class="trend-stable">→</span>
              <span>{{ row.trend }}</span>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
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

.spinner-ring:nth-child(1) {
  border-top-color: #3b82f6;
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  border-right-color: #f59e0b;
  animation-delay: 0.2s;
  width: 70%;
  height: 70%;
  top: 15%;
  left: 15%;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #10b981;
  animation-delay: 0.4s;
  width: 40%;
  height: 40%;
  top: 30%;
  left: 30%;
}

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

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Main Content */
.failure-rate-analytics {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h2 {
  margin: 0 0 4px 0;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #303133, #606266);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

/* KPI Cards */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.kpi-card {
  border-radius: 20px;
  transition: all 0.3s ease;
}

.kpi-card:hover {
  transform: translateY(-4px);
}

.kpi-card :deep(.el-card__body) {
  padding: 20px;
}

.kpi-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.kpi-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.kpi-icon.overall { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
.kpi-icon.failures { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; }
.kpi-icon.improvement { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; }
.kpi-icon.best { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; }
.kpi-icon.attention { background: linear-gradient(135deg, #f6d365 0%, #fda085 100%); color: white; }

.kpi-info {
  flex: 1;
}

.kpi-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.kpi-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.kpi-sub {
  font-size: 11px;
  color: #c0c4cc;
  margin-top: 2px;
}

/* Charts */
.chart-card {
  border-radius: 20px;
  margin-bottom: 24px;
}

.chart-card :deep(.el-card__body) {
  padding: 16px;
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.chart {
  width: 100%;
  height: 360px;
}

/* Tables */
.table-card {
  border-radius: 20px;
  margin-bottom: 24px;
}

.table-card :deep(.el-card__body) {
  padding: 0;
}

.table-card :deep(.el-table__header-wrapper th) {
  text-align: center;
}

.el-table :deep(td) {
  text-align: center;
}

.metric-cell {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.rate-value {
  font-weight: 600;
}

.trend-cell {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.trend-up { color: #F56C6C; }
.trend-down { color: #67C23A; }
.trend-stable { color: #909399; }

.performance-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.performance-badge.good-badge {
  background: rgba(103, 194, 58, 0.1);
  color: #67C23A;
}

.performance-badge.bad-badge {
  background: rgba(245, 108, 108, 0.1);
  color: #F56C6C;
}

/* Responsive */
@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }

  .charts-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .failure-rate-analytics {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions {
    flex-direction: column;
  }

  .header-actions .el-date-picker,
  .header-actions .el-button {
    width: 100%;
  }

  .chart {
    height: 280px;
  }
}
</style>