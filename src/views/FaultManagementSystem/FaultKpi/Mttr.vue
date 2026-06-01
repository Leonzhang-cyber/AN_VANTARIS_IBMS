<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted, computed } from 'vue'
import {
  Search, RefreshRight, Warning, CircleCheck, Clock,
  TrendCharts, Monitor, Connection, DataAnalysis,
  Document, Setting, More, ArrowUp, ArrowDown,
  VideoCamera, Histogram, Grid, Platform, Link,
  Tickets, Timer, Timer as Stopwatch
} from "@element-plus/icons-vue"
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading MTTR data...',
  'Analyzing repair times...',
  'Calculating resolution metrics...'
]

// Date range
const dateRange = ref<[Date, Date]>([
  new Date(new Date().setDate(new Date().getDate() - 365)),
  new Date()
])

// MTTR Data by Device Type
const mttrData = ref([
  { deviceType: 'UPS', mttr: 4.2, targetMttr: 4.0, trend: 'up', status: 'warning', totalRepairs: 8, avgResponse: 0.8, avgDiagnostic: 1.2, avgRepair: 2.2 },
  { deviceType: 'Chiller', mttr: 6.5, targetMttr: 6.0, trend: 'up', status: 'warning', totalRepairs: 12, avgResponse: 1.0, avgDiagnostic: 2.0, avgRepair: 3.5 },
  { deviceType: 'AHU', mttr: 3.8, targetMttr: 4.0, trend: 'down', status: 'good', totalRepairs: 15, avgResponse: 0.5, avgDiagnostic: 1.0, avgRepair: 2.3 },
  { deviceType: 'CRAC', mttr: 5.2, targetMttr: 5.0, trend: 'up', status: 'warning', totalRepairs: 16, avgResponse: 0.9, avgDiagnostic: 1.5, avgRepair: 2.8 },
  { deviceType: 'VFD', mttr: 3.5, targetMttr: 4.0, trend: 'down', status: 'excellent', totalRepairs: 20, avgResponse: 0.4, avgDiagnostic: 1.0, avgRepair: 2.1 },
  { deviceType: 'Controller', mttr: 2.8, targetMttr: 3.0, trend: 'stable', status: 'good', totalRepairs: 11, avgResponse: 0.3, avgDiagnostic: 0.8, avgRepair: 1.7 },
  { deviceType: 'Sensor', mttr: 1.5, targetMttr: 2.0, trend: 'down', status: 'excellent', totalRepairs: 26, avgResponse: 0.2, avgDiagnostic: 0.5, avgRepair: 0.8 },
  { deviceType: 'Pump', mttr: 4.8, targetMttr: 5.0, trend: 'stable', status: 'good', totalRepairs: 18, avgResponse: 0.7, avgDiagnostic: 1.3, avgRepair: 2.8 },
  { deviceType: 'Transformer', mttr: 8.2, targetMttr: 8.0, trend: 'up', status: 'warning', totalRepairs: 6, avgResponse: 1.5, avgDiagnostic: 2.5, avgRepair: 4.2 },
  { deviceType: 'Generator', mttr: 7.5, targetMttr: 7.0, trend: 'up', status: 'critical', totalRepairs: 7, avgResponse: 1.2, avgDiagnostic: 2.0, avgRepair: 4.3 }
])

// Monthly MTTR trend
const monthlyTrend = ref([
  { month: 'Aug', mttr: 4.8, targetMttr: 4.5, responseTime: 0.9, diagnosticTime: 1.4, repairTime: 2.5 },
  { month: 'Sep', mttr: 4.6, targetMttr: 4.5, responseTime: 0.8, diagnosticTime: 1.3, repairTime: 2.5 },
  { month: 'Oct', mttr: 4.5, targetMttr: 4.5, responseTime: 0.8, diagnosticTime: 1.3, repairTime: 2.4 },
  { month: 'Nov', mttr: 4.4, targetMttr: 4.5, responseTime: 0.7, diagnosticTime: 1.2, repairTime: 2.5 },
  { month: 'Dec', mttr: 4.3, targetMttr: 4.5, responseTime: 0.7, diagnosticTime: 1.2, repairTime: 2.4 },
  { month: 'Jan', mttr: 4.2, targetMttr: 4.5, responseTime: 0.6, diagnosticTime: 1.1, repairTime: 2.5 }
])

// MTTR by team/shift
const teamPerformance = ref([
  { team: 'Morning Shift', mttr: 3.8, incidents: 45, slaAchieved: 91, trend: 'up' },
  { team: 'Afternoon Shift', mttr: 4.2, incidents: 38, slaAchieved: 87, trend: 'stable' },
  { team: 'Night Shift', mttr: 4.5, incidents: 32, slaAchieved: 84, trend: 'down' },
  { team: 'Weekend Team', mttr: 5.1, incidents: 22, slaAchieved: 78, trend: 'stable' },
  { team: 'Emergency Response', mttr: 3.2, incidents: 28, slaAchieved: 94, trend: 'up' }
])

// MTTR by severity
const severityMttr = ref([
  { severity: 'Critical', mttr: 2.5, target: 2.0, incidents: 18, slaAchieved: 72 },
  { severity: 'Major', mttr: 3.8, target: 4.0, incidents: 42, slaAchieved: 88 },
  { severity: 'Warning', mttr: 5.2, target: 6.0, incidents: 68, slaAchieved: 94 },
  { severity: 'Minor', mttr: 6.5, target: 8.0, incidents: 55, slaAchieved: 96 },
  { severity: 'Info', mttr: 8.5, target: 12.0, incidents: 32, slaAchieved: 98 }
])

// Top factors affecting MTTR
const affectingFactors = ref([
  { factor: 'Parts Availability', impact: 28, mttrIncrease: 2.5, trend: 'up' },
  { factor: 'Technician Expertise', impact: 22, mttrIncrease: 1.8, trend: 'down' },
  { factor: 'Diagnostic Time', impact: 18, mttrIncrease: 1.5, trend: 'stable' },
  { factor: 'Documentation', impact: 15, mttrIncrease: 1.2, trend: 'down' },
  { factor: 'Tool Availability', impact: 12, mttrIncrease: 1.0, trend: 'stable' },
  { factor: 'Remote Access', impact: 5, mttrIncrease: 0.4, trend: 'up' }
])

// Summary statistics
const summaryStats = ref({
  overallMttr: 4.2,
  targetMttr: 4.5,
  slaAchievement: 86.5,
  bestPerformer: 'Sensor',
  bestMttr: 1.5,
  needsImprovement: 'Transformer',
  worstMttr: 8.2,
  averageResponseTime: 0.75,
  averageDiagnosticTime: 1.35,
  averageRepairTime: 2.45
})

// Chart refs
const mttrChartRef = ref<HTMLElement | null>(null)
const trendChartRef = ref<HTMLElement | null>(null)
const severityChartRef = ref<HTMLElement | null>(null)
let mttrChart: echarts.ECharts | null = null
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

const getTrendClass = (trend: string) => {
  if (trend === 'up') return 'trend-up'
  if (trend === 'down') return 'trend-down'
  return 'trend-stable'
}

const refreshData = () => {
  ElMessage.info('Refreshing MTTR data...')
  setTimeout(() => {
    ElMessage.success('Data refreshed successfully')
  }, 1000)
}

const exportReport = () => {
  ElMessage.success('Exporting MTTR report...')
}

const initMttrChart = () => {
  if (mttrChartRef.value) {
    if (mttrChart) mttrChart.dispose()

    mttrChart = echarts.init(mttrChartRef.value)
    mttrChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['MTTR (hours)', 'Target MTTR (hours)'], left: 'left' },
      grid: { left: '10%', right: '8%', top: '10%', bottom: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: mttrData.value.map(d => d.deviceType),
        axisLabel: { rotate: 45, fontWeight: 500 }
      },
      yAxis: { type: 'value', name: 'Hours' },
      series: [
        {
          name: 'MTTR (hours)',
          type: 'bar',
          data: mttrData.value.map(d => d.mttr),
          itemStyle: {
            color: (params: any) => {
              const status = mttrData.value[params.dataIndex].status
              return getStatusColor(status)
            },
            borderRadius: [4, 4, 0, 0]
          },
          label: { show: true, position: 'top', formatter: '{c}h' }
        },
        {
          name: 'Target MTTR (hours)',
          type: 'line',
          data: mttrData.value.map(d => d.targetMttr),
          lineStyle: { color: '#909399', width: 2, type: 'dashed' },
          symbol: 'diamond',
          symbolSize: 6,
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
        data: ['MTTR (hours)', 'Target MTTR', 'Response Time', 'Diagnostic Time', 'Repair Time'],
        left: 'left'
      },
      grid: { left: '8%', right: '8%', top: '15%', bottom: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: monthlyTrend.value.map(d => d.month),
        axisLabel: { fontWeight: 500 }
      },
      yAxis: { type: 'value', name: 'Hours' },
      series: [
        {
          name: 'MTTR (hours)',
          type: 'line',
          data: monthlyTrend.value.map(d => d.mttr),
          smooth: true,
          lineStyle: { color: '#409EFF', width: 3 },
          areaStyle: { opacity: 0.1, color: '#409EFF' },
          symbol: 'circle',
          symbolSize: 8,
          label: { show: true, position: 'top', formatter: '{c}h' }
        },
        {
          name: 'Target MTTR',
          type: 'line',
          data: monthlyTrend.value.map(d => d.targetMttr),
          lineStyle: { color: '#909399', width: 2, type: 'dashed' },
          symbol: 'diamond',
          symbolSize: 6,
          label: { show: true, position: 'top', formatter: '{c}h' }
        },
        {
          name: 'Response Time',
          type: 'bar',
          data: monthlyTrend.value.map(d => d.responseTime),
          barWidth: '15%',
          itemStyle: { color: '#67C23A', borderRadius: [4, 4, 0, 0] },
          label: { show: true, position: 'top', formatter: '{c}h' }
        },
        {
          name: 'Diagnostic Time',
          type: 'bar',
          data: monthlyTrend.value.map(d => d.diagnosticTime),
          barWidth: '15%',
          itemStyle: { color: '#E6A23C', borderRadius: [4, 4, 0, 0] },
          label: { show: true, position: 'top', formatter: '{c}h' }
        },
        {
          name: 'Repair Time',
          type: 'bar',
          data: monthlyTrend.value.map(d => d.repairTime),
          barWidth: '15%',
          itemStyle: { color: '#F56C6C', borderRadius: [4, 4, 0, 0] },
          label: { show: true, position: 'top', formatter: '{c}h' }
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
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['MTTR (hours)', 'Target MTTR (hours)'], left: 'left' },
      grid: { left: '10%', right: '8%', top: '10%', bottom: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: severityMttr.value.map(s => s.severity),
        axisLabel: { fontWeight: 500 }
      },
      yAxis: { type: 'value', name: 'Hours' },
      series: [
        {
          name: 'MTTR (hours)',
          type: 'bar',
          data: severityMttr.value.map(s => s.mttr),
          itemStyle: {
            color: (params: any) => {
              const severity = severityMttr.value[params.dataIndex].severity
              if (severity === 'Critical') return '#F56C6C'
              if (severity === 'Major') return '#E6A23C'
              if (severity === 'Warning') return '#409EFF'
              return '#67C23A'
            },
            borderRadius: [4, 4, 0, 0]
          },
          label: { show: true, position: 'top', formatter: '{c}h' }
        },
        {
          name: 'Target MTTR (hours)',
          type: 'line',
          data: severityMttr.value.map(s => s.target),
          lineStyle: { color: '#909399', width: 2, type: 'dashed' },
          symbol: 'diamond',
          symbolSize: 6,
          label: { show: true, position: 'top', formatter: '{c}h' }
        }
      ]
    })
  }
}

const handleResize = () => {
  mttrChart?.resize()
  trendChart?.resize()
  severityChart?.resize()
}

watch(isLoaded, (loaded) => {
  if (loaded) {
    nextTick(() => {
      initMttrChart()
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
  mttrChart?.dispose()
  trendChart?.dispose()
  severityChart?.dispose()
})

// Helper computed
const slaColor = computed(() => {
  return summaryStats.value.slaAchievement >= 90 ? '#67C23A' : summaryStats.value.slaAchievement >= 80 ? '#E6A23C' : '#F56C6C'
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
        <div class="loading-tip">MTTR Analytics</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="mttr-analytics">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>MTTR Analytics</h2>
        <p class="subtitle">Mean Time To Repair - Resolution Performance Metrics</p>
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
            <div class="kpi-value">{{ summaryStats.overallMttr }}h</div>
            <div class="kpi-label">Overall MTTR</div>
            <div class="kpi-sub">Target: {{ summaryStats.targetMttr }}h</div>
          </div>
        </div>
      </el-card>
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-content">
          <div class="kpi-icon sla">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value" :style="{ color: slaColor }">{{ summaryStats.slaAchievement }}%</div>
            <div class="kpi-label">SLA Achievement</div>
            <div class="kpi-sub">Target: 90%</div>
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
            <div class="kpi-sub">{{ summaryStats.bestMttr }}h MTTR</div>
          </div>
        </div>
      </el-card>
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-content">
          <div class="kpi-icon attention">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ summaryStats.needsImprovement }}</div>
            <div class="kpi-label">Needs Improvement</div>
            <div class="kpi-sub">{{ summaryStats.worstMttr }}h MTTR</div>
          </div>
        </div>
      </el-card>
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-content">
          <div class="kpi-icon breakdown">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ summaryStats.averageResponseTime }}h</div>
            <div class="kpi-label">Avg Response</div>
            <div class="kpi-sub">+ {{ summaryStats.averageDiagnosticTime }}h / {{ summaryStats.averageRepairTime }}h</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- MTTR by Device Type Chart -->
    <el-card class="chart-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>MTTR by Device Type</span>
          <el-tag type="info" size="small">vs Target</el-tag>
        </div>
      </template>
      <div ref="mttrChartRef" class="chart"></div>
    </el-card>

    <!-- Two Column Charts -->
    <div class="charts-row">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>MTTR Trend & Breakdown</span>
            <el-tag type="success" size="small">Improving</el-tag>
          </div>
        </template>
        <div ref="trendChartRef" class="chart"></div>
      </el-card>

      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>MTTR by Severity</span>
            <el-tag type="warning" size="small">Critical Priority</el-tag>
          </div>
        </template>
        <div ref="severityChartRef" class="chart"></div>
      </el-card>
    </div>

    <!-- Team Performance Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Team Performance</span>
          <el-tag type="primary" size="small">By Shift/Team</el-tag>
        </div>
      </template>
      <el-table :data="teamPerformance" stripe style="width: 100%">
        <el-table-column prop="team" label="Team/Shift" align="center" />
        <el-table-column label="MTTR" align="center" >
          <template #default="{ row }">
            <div class="metric-cell">
              <span class="mttr-value">{{ row.mttr }}h</span>
              <el-icon v-if="row.trend === 'up'" class="trend-up"><ArrowUp /></el-icon>
              <el-icon v-else-if="row.trend === 'down'" class="trend-down"><ArrowDown /></el-icon>
              <span v-else class="trend-stable">→</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="incidents" label="Incidents" align="center" />
        <el-table-column label="SLA Achieved" align="center" >
          <template #default="{ row }">
            <div class="sla-progress">
              <el-progress :percentage="row.slaAchieved" :stroke-width="8" :color="row.slaAchieved >= 90 ? '#67C23A' : row.slaAchieved >= 80 ? '#E6A23C' : '#F56C6C'" />
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Performance vs Team Avg" align="center" >
          <template #default="{ row }">
            <div class="performance-bar">
              <div
                  class="bar-fill"
                  :style="{
                  width: (summaryStats.overallMttr / row.mttr * 100) + '%',
                  background: row.mttr <= summaryStats.overallMttr ? '#67C23A' : '#F56C6C'
                }"
              ></div>
              <span class="bar-label">
                {{ ((summaryStats.overallMttr / row.mttr - 1) * 100).toFixed(1) }}% vs avg
              </span>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Factors Affecting MTTR -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Factors Affecting MTTR</span>
          <el-tag type="warning" size="small">Root Cause Analysis</el-tag>
        </div>
      </template>
      <el-table :data="affectingFactors" stripe style="width: 100%">
        <el-table-column prop="factor" label="Factor" align="center" />
        <el-table-column label="Impact"  align="center">
          <template #default="{ row }">
            <span class="impact-value">{{ row.impact }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="MTTR Increase" align="center">
          <template #default="{ row }">
            <span :style="{ color: row.mttrIncrease > 1.5 ? '#F56C6C' : '#E6A23C' }">
              +{{ row.mttrIncrease }}h
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Trend"  align="center">
          <template #default="{ row }">
            <div class="trend-cell">
              <el-icon v-if="row.trend === 'up'" class="trend-up"><ArrowUp /></el-icon>
              <el-icon v-else-if="row.trend === 'down'" class="trend-down"><ArrowDown /></el-icon>
              <span v-else class="trend-stable">→</span>
              <span>{{ row.trend }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Recommendation"  align="center">
          <template #default="{ row }">
            <span v-if="row.factor === 'Parts Availability'">Increase spare parts inventory</span>
            <span v-else-if="row.factor === 'Technician Expertise'">Provide additional training</span>
            <span v-else-if="row.factor === 'Diagnostic Time'">Implement AI diagnostic tools</span>
            <span v-else-if="row.factor === 'Documentation'">Improve knowledge base</span>
            <span v-else-if="row.factor === 'Tool Availability'">Upgrade tool inventory</span>
            <span v-else>Enhance remote monitoring</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Detailed MTTR Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Detailed MTTR Analysis by Device Type</span>
          <el-tag type="info" size="small">Full Breakdown</el-tag>
        </div>
      </template>
      <el-table :data="mttrData" stripe style="width: 100%">
        <el-table-column prop="deviceType" label="Device Type" align="center" />
        <el-table-column label="MTTR" align="center" >
          <template #default="{ row }">
            <span class="mttr-value" :style="{ color: getStatusColor(row.status) }">{{ row.mttr }}h</span>
          </template>
        </el-table-column>
        <el-table-column label="Target" align="center" >
          <template #default="{ row }">
            {{ row.targetMttr }}h
          </template>
        </el-table-column>
        <el-table-column label="Gap"  align="center" >
          <template #default="{ row }">
            <span :class="row.mttr <= row.targetMttr ? 'trend-down' : 'trend-up'">
              {{ ((row.mttr / row.targetMttr - 1) * 100).toFixed(1) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Response" align="center" >
          <template #default="{ row }">
            {{ row.avgResponse }}h
          </template>
        </el-table-column>
        <el-table-column label="Diagnostic" align="center" >
          <template #default="{ row }">
            {{ row.avgDiagnostic }}h
          </template>
        </el-table-column>
        <el-table-column label="Repair" align="center" >
          <template #default="{ row }">
            {{ row.avgRepair }}h
          </template>
        </el-table-column>
        <el-table-column prop="totalRepairs" label="Repairs"  align="center"  />
        <el-table-column label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="row.status === 'excellent' ? 'success' : row.status === 'good' ? 'primary' : row.status === 'warning' ? 'warning' : 'danger'" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
/* Loading Screen - Same as previous */
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
.mttr-analytics {
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
.kpi-icon.sla { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; }
.kpi-icon.best { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; }
.kpi-icon.attention { background: linear-gradient(135deg, #f6d365 0%, #fda085 100%); color: white; }
.kpi-icon.breakdown { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #333; }

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

.metric-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
}

.mttr-value {
  font-weight: 600;
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

.impact-value {
  font-weight: 600;
  color: #E6A23C;
}

.sla-progress {
  padding: 4px 0;
}

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
  .mttr-analytics {
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