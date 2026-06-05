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
          <span class="loading-title">Industry Benchmark</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Data Center Performance Analytics</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="industry-benchmark-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <div class="title-icon">
            <el-icon><TrendCharts /></el-icon>
          </div>
          Industry Benchmark
        </h1>
        <div class="page-subtitle">Compare your data center performance against industry standards</div>
      </div>
      <div class="header-right">
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 260px"
        />
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
        <el-button type="primary" @click="exportReport">
          <el-icon><Download /></el-icon> Export Report
        </el-button>
      </div>
    </div>

    <!-- Hero Score Card -->
    <div class="hero-score-card">
      <div class="hero-bg"></div>
      <div class="hero-content">
        <div class="hero-left">
          <div class="hero-badge">
            <span class="badge-icon">🏆</span>
            Overall Performance Score
          </div>
          <div class="hero-score">
            <span class="score-value">{{ overallScore }}</span>
            <span class="score-total">/100</span>
          </div>
          <div class="hero-rank">
            <span class="rank-label">Global Ranking</span>
            <span class="rank-value">Top {{ globalRank }}%</span>
            <span class="rank-trend up">↑ 5% vs last quarter</span>
          </div>
          <div class="hero-metrics">
            <div class="hero-metric">
              <span class="metric-label">Peer Comparison</span>
              <span class="metric-value">Better than {{ peerPercent }}% of peers</span>
            </div>
            <div class="hero-metric">
              <span class="metric-label">Improvement Rate</span>
              <span class="metric-value up">+{{ improvementRate }}% YoY</span>
            </div>
          </div>
        </div>
        <div class="hero-right">
          <div class="gauge-container">
            <div class="gauge-ring">
              <svg width="160" height="160" viewBox="0 0 160 160">
                <circle cx="80" cy="80" r="68" fill="none" stroke="#e2e8f0" stroke-width="12"/>
                <circle cx="80" cy="80" r="68" fill="none"
                        stroke="url(#gaugeGradient)"
                        stroke-width="12"
                        stroke-dasharray="427"
                        :stroke-dashoffset="427 - (overallScore / 100) * 427"
                        stroke-linecap="round"
                        transform="rotate(-90 80 80)"/>
                <defs>
                  <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:#3b82f6"/>
                    <stop offset="50%" style="stop-color:#8b5cf6"/>
                    <stop offset="100%" style="stop-color:#06b6d4"/>
                  </linearGradient>
                </defs>
              </svg>
              <div class="gauge-label">Excellent</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card" v-for="stat in benchmarkStats" :key="stat.name">
        <div class="stat-icon" :class="stat.iconClass">
          <el-icon><component :is="stat.icon" /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stat.value }}<span class="unit">{{ stat.unit }}</span></div>
          <div class="stat-label">{{ stat.label }}</div>
          <div class="stat-compare">
            <span class="compare-label">Industry Avg:</span>
            <span class="compare-value">{{ stat.industryAvg }}{{ stat.unit }}</span>
            <span class="compare-diff" :class="stat.diffClass">
              <el-icon><Top v-if="stat.diff > 0" /><Bottom v-else-if="stat.diff < 0" /><Right v-else /></el-icon>
              {{ Math.abs(stat.diff) }}%
            </span>
          </div>
        </div>
        <div class="stat-progress">
          <div class="progress-bar-bg">
            <div class="progress-bar-fill" :style="{ width: stat.percentile + '%', background: stat.barColor }"></div>
          </div>
          <span class="progress-label">Top {{ 100 - stat.percentile }}%</span>
        </div>
      </div>
    </div>

    <!-- Charts Row 1 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot"></span>
            PUE Benchmark Comparison
          </div>
          <el-tooltip content="Power Usage Effectiveness" placement="top">
            <el-icon><InfoFilled /></el-icon>
          </el-tooltip>
        </div>
        <div class="chart-container" ref="pueChart"></div>
        <div class="chart-footer">
          <div class="footer-note">
            <span class="note-dot own"></span> Your Facility
            <span class="note-dot industry"></span> Industry Average
            <span class="note-dot best"></span> Best-in-Class
          </div>
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot orange"></span>
            WUE Benchmark (L/kWh)
          </div>
          <el-tooltip content="Water Usage Effectiveness" placement="top">
            <el-icon><InfoFilled /></el-icon>
          </el-tooltip>
        </div>
        <div class="chart-container" ref="wueChart"></div>
        <div class="chart-footer">
          <div class="footer-note">
            <span class="note-dot own"></span> Your Facility
            <span class="note-dot industry"></span> Industry Average
            <span class="note-dot best"></span> Best-in-Class
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row 2 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot green"></span>
            CUE Benchmark (gCO2/kWh)
          </div>
          <el-tooltip content="Carbon Usage Effectiveness" placement="top">
            <el-icon><InfoFilled /></el-icon>
          </el-tooltip>
        </div>
        <div class="chart-container" ref="cueChart"></div>
        <div class="chart-footer">
          <div class="footer-note">
            <span class="note-dot own"></span> Your Facility
            <span class="note-dot industry"></span> Industry Average
            <span class="note-dot best"></span> Best-in-Class
          </div>
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot purple"></span>
            Renewable Energy Ratio (%)
          </div>
          <el-tooltip content="Percentage of energy from renewable sources" placement="top">
            <el-icon><InfoFilled /></el-icon>
          </el-tooltip>
        </div>
        <div class="chart-container" ref="renewableChart"></div>
        <div class="chart-footer">
          <div class="footer-note">
            <span class="note-dot own"></span> Your Facility
            <span class="note-dot industry"></span> Industry Average
            <span class="note-dot best"></span> Best-in-Class
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row 3 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot blue"></span>
            IT Equipment Efficiency
          </div>
        </div>
        <div class="chart-container" ref="iteeChart"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot teal"></span>
            Data Center Infrastructure Efficiency
          </div>
        </div>
        <div class="chart-container" ref="dcieChart"></div>
      </div>
    </div>

    <!-- Benchmark Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Detailed Benchmark Comparison</span>
        <div class="table-actions">
          <el-input
              v-model="searchText"
              placeholder="Search metrics..."
              style="width: 200px"
              clearable
              :prefix-icon="Search"
              size="small"
          />
          <el-button size="small" @click="exportTableData">
            <el-icon><Download /></el-icon> Export
          </el-button>
        </div>
      </div>
      <el-table :data="filteredBenchmarkData" stripe border style="width: 100%">
        <el-table-column prop="metric" label="Metric" />
        <el-table-column prop="yourValue" label="Your Facility">
          <template #default="{ row }">
            <strong>{{ row.yourValue }}{{ row.unit }}</strong>
          </template>
        </el-table-column>
        <el-table-column prop="industryAvg" label="Industry Average">
          <template #default="{ row }">{{ row.industryAvg }}{{ row.unit }}</template>
        </el-table-column>
        <el-table-column prop="bestInClass" label="Best-in-Class">
          <template #default="{ row }">{{ row.bestInClass }}{{ row.unit }}</template>
        </el-table-column>
        <el-table-column prop="percentile" label="Percentile">
          <template #default="{ row }">
            <el-progress
                :percentage="row.percentile"
                :stroke-width="8"
                :color="getPercentileColor(row.percentile)"
                :show-text="true"
                :format="() => `${row.percentile}%`"
            />
          </template>
        </el-table-column>
        <el-table-column label="Status">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.percentile)" size="small">
              {{ getStatusText(row.percentile) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Trend">
          <template #default="{ row }">
      <span :class="row.trend === 'up' ? 'trend-up' : (row.trend === 'down' ? 'trend-down' : 'trend-stable')">
        {{ row.trend === 'up' ? '↑ Improving' : (row.trend === 'down' ? '↓ Declining' : '→ Stable') }}
      </span>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  TrendCharts, Download, Refresh, InfoFilled, Top, Bottom, Right,
  DataLine, PieChart, Monitor, Cpu, Search
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading benchmark data...')
const refreshing = ref(false)

const loadingMessages = [
  'Loading benchmark data...',
  'Analyzing industry standards...',
  'Calculating performance metrics...',
  'Generating comparison charts...',
  'Almost ready...'
]

// ==================== State ====================
const dateRange = ref<string[]>([])
const searchText = ref('')
const overallScore = ref(87)
const globalRank = ref(12)
const peerPercent = ref(85)
const improvementRate = ref(8.5)

// Chart refs
const pueChart = ref<HTMLElement | null>(null)
const wueChart = ref<HTMLElement | null>(null)
const cueChart = ref<HTMLElement | null>(null)
const renewableChart = ref<HTMLElement | null>(null)
const iteeChart = ref<HTMLElement | null>(null)
const dcieChart = ref<HTMLElement | null>(null)

let pueChartInstance: echarts.ECharts | null = null
let wueChartInstance: echarts.ECharts | null = null
let cueChartInstance: echarts.ECharts | null = null
let renewableChartInstance: echarts.ECharts | null = null
let iteeChartInstance: echarts.ECharts | null = null
let dcieChartInstance: echarts.ECharts | null = null

// Benchmark stats
const benchmarkStats = ref([
  { name: 'PUE', label: 'Power Usage Effectiveness', value: '1.35', unit: '', industryAvg: '1.58', diff: -14.6, diffClass: 'up', percentile: 92, barColor: '#3b82f6', icon: 'DataLine', iconClass: 'blue' },
  { name: 'WUE', label: 'Water Usage Effectiveness', value: '1.25', unit: ' L/kWh', industryAvg: '1.82', diff: -31.3, diffClass: 'up', percentile: 88, barColor: '#22c55e', icon: 'DataLine', iconClass: 'green' },
  { name: 'CUE', label: 'Carbon Usage Effectiveness', value: '0.28', unit: ' gCO2/kWh', industryAvg: '0.42', diff: -33.3, diffClass: 'up', percentile: 90, barColor: '#10b981', icon: 'DataLine', iconClass: 'green' },
  { name: 'Renewable', label: 'Renewable Energy Ratio', value: '65', unit: '%', industryAvg: '42', diff: +54.8, diffClass: 'up', percentile: 85, barColor: '#f59e0b', icon: 'DataLine', iconClass: 'orange' }
])

// Benchmark data table
const benchmarkData = ref([
  { metric: 'Power Usage Effectiveness (PUE)', yourValue: '1.35', industryAvg: '1.58', bestInClass: '1.12', unit: '', percentile: 92, trend: 'down' },
  { metric: 'Water Usage Effectiveness (WUE)', yourValue: '1.25', industryAvg: '1.82', bestInClass: '0.95', unit: ' L/kWh', percentile: 88, trend: 'down' },
  { metric: 'Carbon Usage Effectiveness (CUE)', yourValue: '0.28', industryAvg: '0.42', bestInClass: '0.15', unit: ' gCO2/kWh', percentile: 90, trend: 'down' },
  { metric: 'Renewable Energy Ratio', yourValue: '65', industryAvg: '42', bestInClass: '100', unit: '%', percentile: 85, trend: 'up' },
  { metric: 'IT Equipment Efficiency (ITEE)', yourValue: '72', industryAvg: '65', bestInClass: '85', unit: '%', percentile: 78, trend: 'up' },
  { metric: 'Data Center Infrastructure Efficiency (DCIE)', yourValue: '85', industryAvg: '78', bestInClass: '92', unit: '%', percentile: 82, trend: 'up' },
  { metric: 'Server Utilization Rate', yourValue: '68', industryAvg: '55', bestInClass: '82', unit: '%', percentile: 84, trend: 'up' },
  { metric: 'Cooling Efficiency Ratio (CER)', yourValue: '1.8', industryAvg: '2.2', bestInClass: '1.4', unit: '', percentile: 86, trend: 'down' },
  { metric: 'Power Distribution Loss', yourValue: '5.2', industryAvg: '7.5', bestInClass: '3.8', unit: '%', percentile: 88, trend: 'down' },
  { metric: 'Annualized PUE', yourValue: '1.38', industryAvg: '1.62', bestInClass: '1.15', unit: '', percentile: 85, trend: 'down' }
])

const filteredBenchmarkData = computed(() => {
  if (!searchText.value) return benchmarkData.value
  const search = searchText.value.toLowerCase()
  return benchmarkData.value.filter(item =>
      item.metric.toLowerCase().includes(search)
  )
})

// ==================== Helper Functions ====================
const getPercentileColor = (percentile: number): string => {
  if (percentile >= 85) return '#22c55e'
  if (percentile >= 70) return '#f59e0b'
  return '#ef4444'
}

const getStatusType = (percentile: number): string => {
  if (percentile >= 85) return 'success'
  if (percentile >= 70) return 'warning'
  return 'danger'
}

const getStatusText = (percentile: number): string => {
  if (percentile >= 85) return 'Excellent'
  if (percentile >= 70) return 'Good'
  return 'Needs Improvement'
}

const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

const exportReport = () => {
  ElMessage.success('Export started')
  setTimeout(() => {
    ElMessage.success('Benchmark report exported')
  }, 1500)
}

const exportTableData = () => {
  ElMessage.success('Table data exported')
}

// ==================== Charts ====================
const initPUEChart = () => {
  if (!pueChart.value) return
  if (pueChartInstance) pueChartInstance.dispose()

  pueChartInstance = echarts.init(pueChart.value)
  pueChartInstance.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 30, bottom: 20 },
    xAxis: { type: 'category', data: ['Your Facility', 'Industry Avg', 'Best-in-Class'] },
    yAxis: { type: 'value', name: 'PUE', min: 1.0, max: 1.8 },
    series: [{
      type: 'bar',
      data: [1.35, 1.58, 1.12],
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const colors = ['#3b82f6', '#94a3b8', '#22c55e']
          return colors[params.dataIndex]
        }
      },
      label: { show: true, position: 'top', formatter: '{c}' }
    }]
  })
}

const initWUEChart = () => {
  if (!wueChart.value) return
  if (wueChartInstance) wueChartInstance.dispose()

  wueChartInstance = echarts.init(wueChart.value)
  wueChartInstance.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 30, bottom: 20 },
    xAxis: { type: 'category', data: ['Your Facility', 'Industry Avg', 'Best-in-Class'] },
    yAxis: { type: 'value', name: 'WUE (L/kWh)' },
    series: [{
      type: 'bar',
      data: [1.25, 1.82, 0.95],
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const colors = ['#22c55e', '#94a3b8', '#10b981']
          return colors[params.dataIndex]
        }
      },
      label: { show: true, position: 'top', formatter: '{c}' }
    }]
  })
}

const initCUEChart = () => {
  if (!cueChart.value) return
  if (cueChartInstance) cueChartInstance.dispose()

  cueChartInstance = echarts.init(cueChart.value)
  cueChartInstance.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 30, bottom: 20 },
    xAxis: { type: 'category', data: ['Your Facility', 'Industry Avg', 'Best-in-Class'] },
    yAxis: { type: 'value', name: 'CUE (gCO2/kWh)' },
    series: [{
      type: 'bar',
      data: [0.28, 0.42, 0.15],
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const colors = ['#10b981', '#94a3b8', '#059669']
          return colors[params.dataIndex]
        }
      },
      label: { show: true, position: 'top', formatter: '{c}' }
    }]
  })
}

const initRenewableChart = () => {
  if (!renewableChart.value) return
  if (renewableChartInstance) renewableChartInstance.dispose()

  renewableChartInstance = echarts.init(renewableChart.value)
  renewableChartInstance.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 30, bottom: 20 },
    xAxis: { type: 'category', data: ['Your Facility', 'Industry Avg', 'Best-in-Class'] },
    yAxis: { type: 'value', name: 'Renewable Energy (%)', max: 100 },
    series: [{
      type: 'bar',
      data: [65, 42, 100],
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const colors = ['#f59e0b', '#94a3b8', '#8b5cf6']
          return colors[params.dataIndex]
        }
      },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initITEEChart = () => {
  if (!iteeChart.value) return
  if (iteeChartInstance) iteeChartInstance.dispose()

  iteeChartInstance = echarts.init(iteeChart.value)
  iteeChartInstance.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 30, bottom: 20 },
    xAxis: { type: 'category', data: ['Your Facility', 'Industry Avg', 'Best-in-Class'] },
    yAxis: { type: 'value', name: 'Efficiency (%)', max: 100 },
    series: [{
      type: 'bar',
      data: [72, 65, 85],
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const colors = ['#06b6d4', '#94a3b8', '#3b82f6']
          return colors[params.dataIndex]
        }
      },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initDCIEChart = () => {
  if (!dcieChart.value) return
  if (dcieChartInstance) dcieChartInstance.dispose()

  dcieChartInstance = echarts.init(dcieChart.value)
  dcieChartInstance.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 30, bottom: 20 },
    xAxis: { type: 'category', data: ['Your Facility', 'Industry Avg', 'Best-in-Class'] },
    yAxis: { type: 'value', name: 'DCIE (%)', max: 100 },
    series: [{
      type: 'bar',
      data: [85, 78, 92],
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const colors = ['#8b5cf6', '#94a3b8', '#ec489a']
          return colors[params.dataIndex]
        }
      },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

// Resize all charts
const resizeCharts = () => {
  [pueChartInstance, wueChartInstance, cueChartInstance, renewableChartInstance, iteeChartInstance, dcieChartInstance].forEach(chart => {
    if (chart) chart.resize()
  })
}

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
      nextTick(() => {
        initPUEChart()
        initWUEChart()
        initCUEChart()
        initRenewableChart()
        initITEEChart()
        initDCIEChart()
      })
      window.addEventListener('resize', resizeCharts)
    }, 500)
  }, 2200)
}

onMounted(() => {
  startLoading()
})
</script>

<style scoped>
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
*::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* ==================== Loading Screen ==================== */
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

/* ==================== Main Page ==================== */
.industry-benchmark-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 24px;
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

.header-left {
  flex: 1;
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

.title-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
}

.header-right {
  display: flex;
  gap: 12px;
}

/* Hero Score Card */
.hero-score-card {
  position: relative;
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-radius: 28px;
  margin-bottom: 24px;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  top: 0;
  right: 0;
  width: 50%;
  height: 100%;
  background: radial-gradient(ellipse at center, rgba(59, 130, 246, 0.15) 0%, transparent 70%);
}

.hero-content {
  position: relative;
  padding: 32px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 30px;
}

.hero-left {
  flex: 1;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 6px 14px;
  border-radius: 30px;
  font-size: 13px;
  color: #94a3b8;
  margin-bottom: 20px;
}

.badge-icon {
  font-size: 16px;
}

.hero-score {
  margin-bottom: 16px;
}

.score-value {
  font-size: 64px;
  font-weight: 800;
  color: white;
}

.score-total {
  font-size: 24px;
  color: #64748b;
  margin-left: 4px;
}

.hero-rank {
  margin-bottom: 20px;
}

.rank-label {
  font-size: 13px;
  color: #94a3b8;
  margin-right: 12px;
}

.rank-value {
  font-size: 20px;
  font-weight: 700;
  color: #fbbf24;
  margin-right: 12px;
}

.rank-trend {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 20px;
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
}

.rank-trend.up { color: #4ade80; }

.hero-metrics {
  display: flex;
  gap: 30px;
}

.hero-metric {
  display: flex;
  flex-direction: column;
}

.metric-label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 16px;
  font-weight: 600;
  color: white;
}

.metric-value.up { color: #4ade80; }

.hero-right {
  display: flex;
  justify-content: center;
  align-items: center;
}

.gauge-container {
  position: relative;
}

.gauge-ring {
  position: relative;
}

.gauge-label {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 14px;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  padding: 4px 16px;
  border-radius: 30px;
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
  transition: all 0.3s;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-bottom: 16px;
}

.stat-icon.blue { background: #eef2ff; color: #3b82f6; }
.stat-icon.green { background: #dcfce7; color: #22c55e; }
.stat-icon.orange { background: #fef3c7; color: #f59e0b; }

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.stat-value .unit {
  font-size: 12px;
  font-weight: normal;
  color: #64748b;
  margin-left: 2px;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

.stat-compare {
  margin: 12px 0;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.compare-label {
  color: #64748b;
}

.compare-value {
  font-weight: 500;
  color: #1e293b;
}

.compare-diff {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 2px 6px;
  border-radius: 20px;
  font-size: 11px;
}

.compare-diff.up { background: #dcfce7; color: #16a34a; }
.compare-diff.down { background: #fee2e2; color: #dc2626; }

.stat-progress {
  margin-top: 12px;
}

.progress-bar-bg {
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 6px;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s;
}

.progress-label {
  font-size: 11px;
  color: #64748b;
}

/* Charts Row */
.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.title-dot {
  width: 8px;
  height: 8px;
  background: #3b82f6;
  border-radius: 50%;
}

.title-dot.orange { background: #f59e0b; }
.title-dot.green { background: #22c55e; }
.title-dot.purple { background: #8b5cf6; }
.title-dot.blue { background: #3b82f6; }
.title-dot.teal { background: #06b6d4; }

.chart-container {
  height: 300px;
  width: 100%;
}

.chart-footer {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #eef2f8;
}

.footer-note {
  display: flex;
  justify-content: center;
  gap: 24px;
  font-size: 12px;
  color: #64748b;
}

.note-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 6px;
}

.note-dot.own { background: #3b82f6; }
.note-dot.industry { background: #94a3b8; }
.note-dot.best { background: #22c55e; }

/* Table Container */
.table-container {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.table-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.table-actions {
  display: flex;
  gap: 12px;
}

.trend-up { color: #22c55e; }
.trend-down { color: #ef4444; }
.trend-stable { color: #3b82f6; }

/* Responsive */
@media (max-width: 1000px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-row {
    grid-template-columns: 1fr;
  }

  .hero-content {
    flex-direction: column;
    text-align: center;
  }

  .hero-metrics {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-score-card {
    margin-bottom: 16px;
  }

  .hero-content {
    padding: 24px;
  }

  .score-value {
    font-size: 48px;
  }

  .footer-note {
    flex-wrap: wrap;
    gap: 12px;
  }
}
</style>