<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted, computed } from 'vue'
import {
  Search, RefreshRight, Warning, CircleCheck, Clock,
  TrendCharts, Monitor, Connection, DataAnalysis,
  Document, Setting, More, ArrowUp, ArrowDown,
  VideoCamera, Histogram, Grid, Platform, Link,
  Tickets, Timer
} from "@element-plus/icons-vue"
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading MTBF data...',
  'Analyzing equipment reliability...',
  'Calculating failure rates...'
]

// Date range
const dateRange = ref<[Date, Date]>([
  new Date(new Date().setDate(new Date().getDate() - 365)),
  new Date()
])

// MTBF Data by Device Type
const mtbfData = ref([
  { deviceType: 'UPS', mtbf: 12500, mttr: 4.2, failures: 8, operatingHours: 100000, trend: 'up', status: 'excellent' },
  { deviceType: 'Chiller', mtbf: 8900, mttr: 6.5, failures: 12, operatingHours: 106800, trend: 'down', status: 'good' },
  { deviceType: 'AHU', mtbf: 7200, mttr: 3.8, failures: 15, operatingHours: 108000, trend: 'stable', status: 'good' },
  { deviceType: 'CRAC', mtbf: 6800, mttr: 5.2, failures: 16, operatingHours: 108800, trend: 'down', status: 'warning' },
  { deviceType: 'VFD', mtbf: 5500, mttr: 3.5, failures: 20, operatingHours: 110000, trend: 'up', status: 'warning' },
  { deviceType: 'Controller', mtbf: 9800, mttr: 2.8, failures: 11, operatingHours: 107800, trend: 'stable', status: 'good' },
  { deviceType: 'Sensor', mtbf: 4200, mttr: 1.5, failures: 26, operatingHours: 109200, trend: 'down', status: 'critical' },
  { deviceType: 'Pump', mtbf: 6100, mttr: 4.8, failures: 18, operatingHours: 109800, trend: 'stable', status: 'warning' },
  { deviceType: 'Transformer', mtbf: 18500, mttr: 8.2, failures: 6, operatingHours: 111000, trend: 'up', status: 'excellent' },
  { deviceType: 'Generator', mtbf: 15000, mttr: 7.5, failures: 7, operatingHours: 105000, trend: 'stable', status: 'excellent' }
])

// Monthly MTBF trend
const monthlyTrend = ref([
  { month: 'Aug', mtbf: 6850, failures: 14, availability: 99.82 },
  { month: 'Sep', mtbf: 6920, failures: 13, availability: 99.84 },
  { month: 'Oct', mtbf: 7050, failures: 12, availability: 99.86 },
  { month: 'Nov', mtbf: 7180, failures: 11, availability: 99.87 },
  { month: 'Dec', mtbf: 7250, failures: 10, availability: 99.88 },
  { month: 'Jan', mtbf: 7350, failures: 9, availability: 99.90 }
])

// Top failure causes
const failureCauses = ref([
  { cause: 'Component Aging', count: 28, percentage: 22.4, trend: 'up' },
  { cause: 'Electrical Issues', count: 24, percentage: 19.2, trend: 'stable' },
  { cause: 'Mechanical Wear', count: 22, percentage: 17.6, trend: 'up' },
  { cause: 'Sensor Failure', count: 18, percentage: 14.4, trend: 'down' },
  { cause: 'Software/Config', count: 16, percentage: 12.8, trend: 'stable' },
  { cause: 'Environmental', count: 10, percentage: 8.0, trend: 'down' },
  { cause: 'Human Error', count: 7, percentage: 5.6, trend: 'down' }
])

// MTBF by location
const locationMtbf = ref([
  { location: 'Data Center A', mtbf: 7250, devices: 45, trend: 'up' },
  { location: 'Data Center B', mtbf: 6980, devices: 38, trend: 'stable' },
  { location: 'Central Plant', mtbf: 6350, devices: 52, trend: 'down' },
  { location: 'Office Building', mtbf: 7820, devices: 28, trend: 'up' },
  { location: 'Warehouse', mtbf: 8450, devices: 22, trend: 'stable' }
])

// Comparison with industry benchmarks
const benchmarks = ref([
  { deviceType: 'UPS', currentMtbf: 12500, industryAvg: 11000, bestInClass: 18000 },
  { deviceType: 'Chiller', currentMtbf: 8900, industryAvg: 8500, bestInClass: 14000 },
  { deviceType: 'CRAC', currentMtbf: 6800, industryAvg: 7200, bestInClass: 12000 },
  { deviceType: 'Sensor', currentMtbf: 4200, industryAvg: 5000, bestInClass: 8000 },
  { deviceType: 'Controller', currentMtbf: 9800, industryAvg: 9500, bestInClass: 15000 }
])

// Summary statistics
const summaryStats = ref({
  overallMtbf: 7620,
  mttrOverall: 4.5,
  availability: 99.94,
  topPerformer: 'Transformer',
  topMtbf: 18500,
  needsAttention: 'Sensor',
  lowestMtbf: 4200
})

// Chart refs
const mtbfChartRef = ref<HTMLElement | null>(null)
const trendChartRef = ref<HTMLElement | null>(null)
const causeChartRef = ref<HTMLElement | null>(null)
let mtbfChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null
let causeChart: echarts.ECharts | null = null

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

const getTrendClass = (trend: string) => {
  if (trend === 'up') return 'trend-up'
  if (trend === 'down') return 'trend-down'
  return 'trend-stable'
}

const refreshData = () => {
  ElMessage.info('Refreshing MTBF data...')
  setTimeout(() => {
    ElMessage.success('Data refreshed successfully')
  }, 1000)
}

const exportReport = () => {
  ElMessage.success('Exporting MTBF report...')
}

const initMtbfChart = () => {
  if (mtbfChartRef.value) {
    if (mtbfChart) mtbfChart.dispose()

    mtbfChart = echarts.init(mtbfChartRef.value)
    mtbfChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['MTBF (hours)', 'MTTR (hours)'], left: 'left' },
      grid: { left: '10%', right: '8%', top: '10%', bottom: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: mtbfData.value.map(d => d.deviceType),
        axisLabel: { rotate: 45, fontWeight: 500 }
      },
      yAxis: [
        { type: 'value', name: 'MTBF (hours)', min: 0 },
        { type: 'value', name: 'MTTR (hours)', min: 0 }
      ],
      series: [
        {
          name: 'MTBF (hours)',
          type: 'bar',
          data: mtbfData.value.map(d => d.mtbf),
          itemStyle: {
            color: (params: any) => {
              const status = mtbfData.value[params.dataIndex].status
              return getStatusColor(status)
            },
            borderRadius: [4, 4, 0, 0]
          },
          label: { show: true, position: 'top', formatter: '{c}h' }
        },
        {
          name: 'MTTR (hours)',
          type: 'line',
          yAxisIndex: 1,
          data: mtbfData.value.map(d => d.mttr),
          lineStyle: { color: '#F56C6C', width: 3 },
          symbol: 'diamond',
          symbolSize: 8,
          label: { show: true, position: 'top', formatter: '{c}h' }
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
      legend: {
        data: ['MTBF (hours)', 'Number of Failures', 'Availability (%)'],
        left: 'left'
      },
      grid: { left: '8%', right: '8%', top: '15%', bottom: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: monthlyTrend.value.map(d => d.month),
        axisLabel: { fontWeight: 500 }
      },
      yAxis: [
        { type: 'value', name: 'MTBF (hours)', min: 6500, max: 8000 },
        { type: 'value', name: 'Failures', min: 0, max: 20 },
        { type: 'value', name: 'Availability (%)', min: 99.7, max: 100 }
      ],
      series: [
        {
          name: 'MTBF (hours)',
          type: 'line',
          data: monthlyTrend.value.map(d => d.mtbf),
          smooth: true,
          lineStyle: { color: '#409EFF', width: 3 },
          areaStyle: { opacity: 0.1, color: '#409EFF' },
          symbol: 'circle',
          symbolSize: 8,
          label: { show: true, position: 'top', formatter: '{c}h' }
        },
        {
          name: 'Number of Failures',
          type: 'bar',
          yAxisIndex: 1,
          data: monthlyTrend.value.map(d => d.failures),
          itemStyle: { color: '#F56C6C', borderRadius: [4, 4, 0, 0] },
          label: { show: true, position: 'top' }
        },
        {
          name: 'Availability (%)',
          type: 'line',
          yAxisIndex: 2,
          data: monthlyTrend.value.map(d => d.availability),
          smooth: true,
          lineStyle: { color: '#67C23A', width: 2, type: 'dashed' },
          symbol: 'diamond',
          symbolSize: 6,
          label: { show: true, position: 'top', formatter: '{c}%' }
        }
      ]
    })
  }
}

const initCauseChart = () => {
  if (causeChartRef.value) {
    if (causeChart) causeChart.dispose()

    causeChart = echarts.init(causeChartRef.value)
    causeChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} failures)' },
      legend: { orient: 'vertical', left: 'left', top: 'center' },
      series: [
        {
          name: 'Failure Causes',
          type: 'pie',
          radius: ['40%', '65%'],
          data: failureCauses.value.map(c => ({ name: c.cause, value: c.count })),
          label: { show: true, formatter: '{b}: {d}%' },
          emphasis: { scale: true },
          itemStyle: {
            borderRadius: 8,
            borderColor: '#fff',
            borderWidth: 2
          }
        }
      ]
    })
  }
}

const handleResize = () => {
  mtbfChart?.resize()
  trendChart?.resize()
  causeChart?.resize()
}

watch(isLoaded, (loaded) => {
  if (loaded) {
    nextTick(() => {
      initMtbfChart()
      initTrendChart()
      initCauseChart()
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
  mtbfChart?.dispose()
  trendChart?.dispose()
  causeChart?.dispose()
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
        <div class="loading-tip">MTBF Analytics</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="mtbf-analytics">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>MTBF Analytics</h2>
        <p class="subtitle">Mean Time Between Failures - Reliability Performance Metrics</p>
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
            <el-icon><Timer /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ summaryStats.overallMtbf.toLocaleString() }}h</div>
            <div class="kpi-label">Overall MTBF</div>
          </div>
        </div>
      </el-card>
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-content">
          <div class="kpi-icon mttr">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ summaryStats.mttrOverall }}h</div>
            <div class="kpi-label">Overall MTTR</div>
          </div>
        </div>
      </el-card>
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-content">
          <div class="kpi-icon availability">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ summaryStats.availability }}%</div>
            <div class="kpi-label">Availability</div>
          </div>
        </div>
      </el-card>
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-content">
          <div class="kpi-icon top">
            <el-icon><Trophy /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ summaryStats.topPerformer }}</div>
            <div class="kpi-label">Best Performer</div>
            <div class="kpi-sub">{{ summaryStats.topMtbf.toLocaleString() }}h MTBF</div>
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
            <div class="kpi-sub">{{ summaryStats.lowestMtbf.toLocaleString() }}h MTBF</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- MTBF by Device Type Chart -->
    <el-card class="chart-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>MTBF & MTTR by Device Type</span>
          <el-tag type="info" size="small">Last 12 Months</el-tag>
        </div>
      </template>
      <div ref="mtbfChartRef" class="chart"></div>
    </el-card>

    <!-- Two Column Charts -->
    <div class="charts-row">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>MTBF Trend & Failure Analysis</span>
            <el-tag type="success" size="small">Improving</el-tag>
          </div>
        </template>
        <div ref="trendChartRef" class="chart"></div>
      </el-card>

      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Top Failure Causes</span>
            <el-tag type="warning" size="small">Root Cause Analysis</el-tag>
          </div>
        </template>
        <div ref="causeChartRef" class="chart"></div>
      </el-card>
    </div>

    <!-- MTBF by Location -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>MTBF by Location</span>
          <el-tag type="info" size="small">Facility Comparison</el-tag>
        </div>
      </template>
      <el-table :data="locationMtbf" stripe style="width: 100%">
        <el-table-column prop="location" label="Location" align="center" />
        <el-table-column label="MTBF"  align="center">
          <template #default="{ row }">
            <div class="mtbf-cell">
              <span class="mtbf-value">{{ row.mtbf.toLocaleString() }}h</span>
              <el-icon v-if="row.trend === 'up'" class="trend-up"><ArrowUp /></el-icon>
              <el-icon v-else-if="row.trend === 'down'" class="trend-down"><ArrowDown /></el-icon>
              <span v-else class="trend-stable">→</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="devices" label="Number of Devices"  align="center" />
        <el-table-column label="Performance vs Average" align="center">
          <template #default="{ row }">
            <div class="performance-bar">
              <div
                  class="bar-fill"
                  :style="{
                  width: (row.mtbf / summaryStats.overallMtbf * 100) + '%',
                  background: row.mtbf >= summaryStats.overallMtbf ? '#67C23A' : '#E6A23C'
                }"
              ></div>
              <span class="bar-label">
                {{ ((row.mtbf / summaryStats.overallMtbf - 1) * 100).toFixed(1) }}% vs average
              </span>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Industry Benchmark Comparison -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Industry Benchmark Comparison</span>
          <el-tag type="primary" size="small">vs Industry Standards</el-tag>
        </div>
      </template>
      <el-table :data="benchmarks" stripe style="width: 100%">
        <el-table-column prop="deviceType" label="Device Type" align="center"/>
        <el-table-column label="Current MTBF"  align="center">
          <template #default="{ row }">
            <span :style="{ color: row.currentMtbf >= row.industryAvg ? '#67C23A' : '#F56C6C' }">
              {{ row.currentMtbf.toLocaleString() }}h
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Industry Average"  align="center">
          <template #default="{ row }">
            {{ row.industryAvg.toLocaleString() }}h
          </template>
        </el-table-column>
        <el-table-column label="Best in Class"  align="center">
          <template #default="{ row }">
            {{ row.bestInClass.toLocaleString() }}h
          </template>
        </el-table-column>
        <el-table-column label="Gap to Industry"  align="center">
          <template #default="{ row }">
            <span :class="row.currentMtbf >= row.industryAvg ? 'trend-up' : 'trend-down'">
              {{ ((row.currentMtbf / row.industryAvg - 1) * 100).toFixed(1) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Gap to Best" align="center">
          <template #default="{ row }">
            <span class="trend-down">
              {{ ((row.currentMtbf / row.bestInClass - 1) * 100).toFixed(1) }}%
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Detailed MTBF Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Detailed MTBF by Device Type</span>
          <el-tag type="info" size="small">Full Analysis</el-tag>
        </div>
      </template>
      <el-table :data="mtbfData" stripe style="width: 100%">
        <el-table-column prop="deviceType" label="Device Type"  align="center" />
        <el-table-column label="MTBF"  align="center">
          <template #default="{ row }">
            <span class="mtbf-value">{{ row.mtbf.toLocaleString() }}h</span>
          </template>
        </el-table-column>
        <el-table-column label="MTTR" align="center">
          <template #default="{ row }">
            {{ row.mttr }}h
          </template>
        </el-table-column>
        <el-table-column prop="failures" label="Failures"  align="center" />
        <el-table-column prop="operatingHours" label="Operating Hours" align="center" />
        <el-table-column label="Status" width="110">
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
.mtbf-analytics {
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
.kpi-icon.mttr { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; }
.kpi-icon.availability { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; }
.kpi-icon.top { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; }
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

.mtbf-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
}

.mtbf-value {
  font-weight: 600;
  color: #303133;
}

.trend-cell {
  display: flex;
  align-items: center;
  gap: 4px;
  justify-content: center;
}

.trend-up { color: #F56C6C; }
.trend-down { color: #67C23A; }
.trend-stable { color: #909399; }

.performance-bar {
  position: relative;
  background: #ebeef5;
  border-radius: 10px;
  height: 24px;
  overflow: hidden;
}

.performance-bar .bar-fill {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  border-radius: 10px;
}

.performance-bar .bar-label {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  height: 24px;
  padding-left: 8px;
  font-size: 12px;
  color: #303133;
  z-index: 1;
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
  .mtbf-analytics {
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