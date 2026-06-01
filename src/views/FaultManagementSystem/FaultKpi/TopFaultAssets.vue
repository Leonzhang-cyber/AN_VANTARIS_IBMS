<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted, computed } from 'vue'
import {
  Search, RefreshRight, Warning, CircleCheck, Clock,
  TrendCharts, Monitor, Connection, DataAnalysis,
  Document, Setting, More, ArrowUp, ArrowDown,
  VideoCamera, Histogram, Grid, Platform, Link,
  Tickets, Timer, PieChart, Medal, Rank
} from "@element-plus/icons-vue"
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading asset fault data...',
  'Analyzing top offenders...',
  'Calculating criticality scores...'
]

// Date range
const dateRange = ref<[Date, Date]>([
  new Date(new Date().setDate(new Date().getDate() - 365)),
  new Date()
])

// Top Fault Assets Data
const topFaultAssets = ref([
  {
    rank: 1,
    assetId: 'CH-01',
    assetName: 'Chiller Unit 1',
    assetType: 'Chiller',
    location: 'Central Plant',
    faultCount: 28,
    totalDowntime: 124.5,
    mtbf: 312,
    mttr: 4.45,
    criticality: 'Critical',
    trend: 'up',
    status: 'critical',
    lastFault: '2025-01-15',
    topFaults: ['Compressor failure', 'Low refrigerant', 'High pressure']
  },
  {
    rank: 2,
    assetId: 'UPS-02',
    assetName: 'UPS Unit 2',
    assetType: 'UPS',
    location: 'Data Center A',
    faultCount: 24,
    totalDowntime: 98.2,
    mtbf: 425,
    mttr: 4.09,
    criticality: 'Critical',
    trend: 'up',
    status: 'critical',
    lastFault: '2025-01-14',
    topFaults: ['Battery failure', 'Input anomaly', 'Overload']
  },
  {
    rank: 3,
    assetId: 'AHU-03',
    assetName: 'AHU Unit 3',
    assetType: 'AHU',
    location: 'Data Center A',
    faultCount: 22,
    totalDowntime: 78.5,
    mtbf: 495,
    mttr: 3.57,
    criticality: 'High',
    trend: 'up',
    status: 'warning',
    lastFault: '2025-01-13',
    topFaults: ['Fan belt failure', 'Temperature sensor drift', 'Filter clogged']
  },
  {
    rank: 4,
    assetId: 'VFD-04',
    assetName: 'VFD Pump 4',
    assetType: 'VFD',
    location: 'Central Plant',
    faultCount: 20,
    totalDowntime: 65.3,
    mtbf: 545,
    mttr: 3.27,
    criticality: 'High',
    trend: 'stable',
    status: 'warning',
    lastFault: '2025-01-12',
    topFaults: ['Overheating', 'Communication loss', 'Parameter corruption']
  },
  {
    rank: 5,
    assetId: 'CRAC-02',
    assetName: 'CRAC Unit 2',
    assetType: 'CRAC',
    location: 'Data Center B',
    faultCount: 18,
    totalDowntime: 72.0,
    mtbf: 606,
    mttr: 4.00,
    criticality: 'High',
    trend: 'down',
    status: 'warning',
    lastFault: '2025-01-11',
    topFaults: ['Compressor fault', 'High humidity', 'Fan failure']
  },
  {
    rank: 6,
    assetId: 'SENSOR-T-12',
    assetName: 'Temperature Sensor 12',
    assetType: 'Sensor',
    location: 'Data Center A',
    faultCount: 16,
    totalDowntime: 12.0,
    mtbf: 680,
    mttr: 0.75,
    criticality: 'Medium',
    trend: 'stable',
    status: 'good',
    lastFault: '2025-01-10',
    topFaults: ['Calibration drift', 'Communication error']
  },
  {
    rank: 7,
    assetId: 'PMP-02',
    assetName: 'Chilled Water Pump 2',
    assetType: 'Pump',
    location: 'Central Plant',
    faultCount: 15,
    totalDowntime: 52.5,
    mtbf: 725,
    mttr: 3.50,
    criticality: 'High',
    trend: 'down',
    status: 'good',
    lastFault: '2025-01-09',
    topFaults: ['Mechanical seal leak', 'Bearing wear', 'Cavitation']
  },
  {
    rank: 8,
    assetId: 'CT-01',
    assetName: 'Cooling Tower 1',
    assetType: 'Cooling Tower',
    location: 'Roof',
    faultCount: 14,
    totalDowntime: 56.0,
    mtbf: 778,
    mttr: 4.00,
    criticality: 'Medium',
    trend: 'stable',
    status: 'good',
    lastFault: '2025-01-08',
    topFaults: ['Fan motor failure', 'Water level sensor fault']
  },
  {
    rank: 9,
    assetId: 'SW-AGG-01',
    assetName: 'Aggregation Switch',
    assetType: 'Network',
    location: 'Data Center A',
    faultCount: 12,
    totalDowntime: 8.5,
    mtbf: 908,
    mttr: 0.71,
    criticality: 'Critical',
    trend: 'up',
    status: 'warning',
    lastFault: '2025-01-07',
    topFaults: ['High CPU', 'Packet loss', 'Link flapping']
  },
  {
    rank: 10,
    assetId: 'TX-01',
    assetName: 'Main Transformer',
    assetType: 'Transformer',
    location: 'Electrical Room',
    faultCount: 10,
    totalDowntime: 35.0,
    mtbf: 1090,
    mttr: 3.50,
    criticality: 'Critical',
    trend: 'down',
    status: 'good',
    lastFault: '2025-01-05',
    topFaults: ['Oil temperature high', 'Bushing leakage']
  }
])

// Monthly fault trend for top assets
const monthlyTrend = ref([
  { month: 'Aug', faultCount: 32, affectedAssets: 8, downtime: 145 },
  { month: 'Sep', faultCount: 35, affectedAssets: 9, downtime: 158 },
  { month: 'Oct', faultCount: 38, affectedAssets: 10, downtime: 172 },
  { month: 'Nov', faultCount: 42, affectedAssets: 12, downtime: 189 },
  { month: 'Dec', faultCount: 45, affectedAssets: 14, downtime: 203 },
  { month: 'Jan', faultCount: 48, affectedAssets: 15, downtime: 218 }
])

// Fault distribution by asset type
const assetTypeDistribution = ref([
  { type: 'HVAC', faultCount: 85, percentage: 38.6, assets: 12 },
  { type: 'Electrical/Power', faultCount: 62, percentage: 28.2, assets: 8 },
  { type: 'Controls', faultCount: 35, percentage: 15.9, assets: 15 },
  { type: 'Network/IT', faultCount: 22, percentage: 10.0, assets: 10 },
  { type: 'Sensors', faultCount: 16, percentage: 7.3, assets: 25 }
])

// Fault by location summary
const locationSummary = ref([
  { location: 'Data Center A', faultCount: 86, assetsAffected: 18, criticalAssets: 5, downtime: 398 },
  { location: 'Central Plant', faultCount: 62, assetsAffected: 22, criticalAssets: 3, downtime: 312 },
  { location: 'Data Center B', faultCount: 48, assetsAffected: 15, criticalAssets: 2, downtime: 198 },
  { location: 'Electrical Room', faultCount: 24, assetsAffected: 8, criticalAssets: 4, downtime: 86 }
])

// Criticality impact matrix
const criticalityImpact = ref([
  { criticality: 'Critical', faultCount: 62, totalDowntime: 86.5, assetsCount: 8, slaImpact: 94 },
  { criticality: 'High', faultCount: 55, totalDowntime: 65.3, assetsCount: 12, slaImpact: 88 },
  { criticality: 'Medium', faultCount: 48, totalDowntime: 34.2, assetsCount: 20, slaImpact: 96 },
  { criticality: 'Low', faultCount: 25, totalDowntime: 12.5, assetsCount: 18, slaImpact: 99 }
])

// Summary statistics
const summaryStats = ref({
  totalFaults: 189,
  totalAssetsAffected: 45,
  totalDowntime: 854.5,
  avgMttr: 3.45,
  topOffender: 'CH-01',
  topFaultCount: 28,
  highestImpactAsset: 'CH-01',
  highestDowntime: 124.5
})

// Chart refs
const faultChartRef = ref<HTMLElement | null>(null)
const trendChartRef = ref<HTMLElement | null>(null)
const distributionChartRef = ref<HTMLElement | null>(null)
let faultChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null
let distributionChart: echarts.ECharts | null = null

const getCriticalityColor = (criticality: string) => {
  switch(criticality) {
    case 'Critical': return '#F56C6C'
    case 'High': return '#E6A23C'
    case 'Medium': return '#409EFF'
    case 'Low': return '#67C23A'
    default: return '#909399'
  }
}

const getTrendIcon = (trend: string) => {
  if (trend === 'up') return ArrowUp
  if (trend === 'down') return ArrowDown
  return null
}

const getRankColor = (rank: number) => {
  if (rank === 1) return '#FFD700'
  if (rank === 2) return '#C0C0C0'
  if (rank === 3) return '#CD7F32'
  return '#909399'
}

const refreshData = () => {
  ElMessage.info('Refreshing asset fault data...')
  setTimeout(() => {
    ElMessage.success('Data refreshed successfully')
  }, 1000)
}

const exportReport = () => {
  ElMessage.success('Exporting top fault assets report...')
}

const initFaultChart = () => {
  if (faultChartRef.value) {
    if (faultChart) faultChart.dispose()

    faultChart = echarts.init(faultChartRef.value)
    faultChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['Fault Count', 'Downtime (hours)'], left: 'left', textStyle: { color: '#606266' } },
      grid: { left: '8%', right: '8%', top: '10%', bottom: '12%', containLabel: true },
      xAxis: {
        type: 'category',
        data: topFaultAssets.value.map(a => a.assetId),
        axisLabel: { rotate: 45, fontWeight: 500, interval: 0 }
      },
      yAxis: [
        { type: 'value', name: 'Fault Count', min: 0 },
        { type: 'value', name: 'Downtime (hours)', min: 0 }
      ],
      series: [
        {
          name: 'Fault Count',
          type: 'bar',
          data: topFaultAssets.value.map(a => a.faultCount),
          itemStyle: {
            color: (params: any) => {
              const status = topFaultAssets.value[params.dataIndex].status
              if (status === 'critical') return '#F56C6C'
              if (status === 'warning') return '#E6A23C'
              return '#67C23A'
            },
            borderRadius: [4, 4, 0, 0]
          },
          label: { show: true, position: 'top', formatter: '{c}' }
        },
        {
          name: 'Downtime (hours)',
          type: 'line',
          yAxisIndex: 1,
          data: topFaultAssets.value.map(a => a.totalDowntime),
          lineStyle: { color: '#409EFF', width: 3 },
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
      legend: { data: ['Fault Count', 'Assets Affected', 'Downtime (hours)'], left: 'left', textStyle: { color: '#606266' } },
      grid: { left: '8%', right: '8%', top: '15%', bottom: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: monthlyTrend.value.map(d => d.month),
        axisLabel: { fontWeight: 500 }
      },
      yAxis: [
        { type: 'value', name: 'Fault Count / Assets', min: 0 },
        { type: 'value', name: 'Downtime (hours)', min: 0 }
      ],
      series: [
        {
          name: 'Fault Count',
          type: 'line',
          data: monthlyTrend.value.map(d => d.faultCount),
          smooth: true,
          lineStyle: { color: '#F56C6C', width: 3 },
          areaStyle: { opacity: 0.1, color: '#F56C6C' },
          symbol: 'circle',
          symbolSize: 8,
          label: { show: true, position: 'top' }
        },
        {
          name: 'Assets Affected',
          type: 'bar',
          data: monthlyTrend.value.map(d => d.affectedAssets),
          itemStyle: { color: '#E6A23C', borderRadius: [4, 4, 0, 0] },
          label: { show: true, position: 'top' }
        },
        {
          name: 'Downtime (hours)',
          type: 'line',
          yAxisIndex: 1,
          data: monthlyTrend.value.map(d => d.downtime),
          lineStyle: { color: '#409EFF', width: 2, type: 'dashed' },
          symbol: 'diamond',
          symbolSize: 6,
          label: { show: true, position: 'top', formatter: '{c}h' }
        }
      ]
    })
  }
}

const initDistributionChart = () => {
  if (distributionChartRef.value) {
    if (distributionChart) distributionChart.dispose()

    distributionChart = echarts.init(distributionChartRef.value)
    distributionChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} faults)' },
      legend: { orient: 'vertical', left: 'left', top: 'center', textStyle: { color: '#606266' } },
      series: [
        {
          name: 'Faults by Asset Type',
          type: 'pie',
          radius: ['40%', '65%'],
          data: assetTypeDistribution.value.map(t => ({ name: t.type, value: t.faultCount })),
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
  faultChart?.resize()
  trendChart?.resize()
  distributionChart?.resize()
}

watch(isLoaded, (loaded) => {
  if (loaded) {
    nextTick(() => {
      initFaultChart()
      initTrendChart()
      initDistributionChart()
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
  faultChart?.dispose()
  trendChart?.dispose()
  distributionChart?.dispose()
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
        <div class="loading-tip">Top Fault Assets Analysis</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="top-fault-assets">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Top Fault Assets</h2>
        <p class="subtitle">Highest impact equipment by failure frequency and downtime</p>
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
          <div class="kpi-icon total">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ summaryStats.totalFaults }}</div>
            <div class="kpi-label">Total Faults</div>
            <div class="kpi-sub">Last 12 Months</div>
          </div>
        </div>
      </el-card>
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-content">
          <div class="kpi-icon assets">
            <el-icon><Monitor /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ summaryStats.totalAssetsAffected }}</div>
            <div class="kpi-label">Assets Affected</div>
            <div class="kpi-sub">With faults</div>
          </div>
        </div>
      </el-card>
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-content">
          <div class="kpi-icon downtime">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ summaryStats.totalDowntime }}h</div>
            <div class="kpi-label">Total Downtime</div>
            <div class="kpi-sub">Across all assets</div>
          </div>
        </div>
      </el-card>
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-content">
          <div class="kpi-icon top">
            <el-icon><Medal /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ summaryStats.topOffender }}</div>
            <div class="kpi-label">Top Offender</div>
            <div class="kpi-sub">{{ summaryStats.topFaultCount }} faults</div>
          </div>
        </div>
      </el-card>
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-content">
          <div class="kpi-icon impact">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ summaryStats.highestImpactAsset }}</div>
            <div class="kpi-label">Highest Impact</div>
            <div class="kpi-sub">{{ summaryStats.highestDowntime }}h downtime</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Top Fault Assets Chart -->
    <el-card class="chart-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Top 10 Fault-Prone Assets</span>
          <el-tag type="info" size="small">Fault Count & Downtime</el-tag>
        </div>
      </template>
      <div ref="faultChartRef" class="chart"></div>
    </el-card>

    <!-- Two Column Charts -->
    <div class="charts-row">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Monthly Fault Trend Analysis</span>
            <el-tag type="warning" size="small">Increasing Trend</el-tag>
          </div>
        </template>
        <div ref="trendChartRef" class="chart"></div>
      </el-card>

      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Faults by Asset Type</span>
            <el-tag type="success" size="small">Distribution</el-tag>
          </div>
        </template>
        <div ref="distributionChartRef" class="chart"></div>
      </el-card>
    </div>

    <!-- Top Fault Assets Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Top Fault Assets - Detailed Analysis</span>
          <el-tag type="danger" size="small">Priority Assets</el-tag>
        </div>
      </template>
      <el-table :data="topFaultAssets" stripe>
        <el-table-column label="Rank" align="center" width="70">
          <template #default="{ row }">
            <div class="rank-badge" :style="{ background: getRankColor(row.rank) }">
              #{{ row.rank }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="assetId" label="Asset ID" align="center" min-width="100" />
        <el-table-column prop="assetName" label="Asset Name" align="center" min-width="150" />
        <el-table-column prop="assetType" label="Type" align="center" min-width="100" />
        <el-table-column prop="location" label="Location" align="center" min-width="130" />
        <el-table-column label="Fault Count" align="center" min-width="100">
          <template #default="{ row }">
            <span class="fault-count" :style="{ color: row.faultCount > 20 ? '#F56C6C' : '#E6A23C' }">
              {{ row.faultCount }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Total Downtime" align="center" min-width="120">
          <template #default="{ row }">
            {{ row.totalDowntime }}h
          </template>
        </el-table-column>
        <el-table-column label="MTBF" align="center" min-width="100">
          <template #default="{ row }">
            {{ row.mtbf }}h
          </template>
        </el-table-column>
        <el-table-column label="MTTR" align="center" min-width="80">
          <template #default="{ row }">
            {{ row.mttr }}h
          </template>
        </el-table-column>
        <el-table-column label="Criticality" align="center" min-width="100">
          <template #default="{ row }">
            <el-tag :type="row.criticality === 'Critical' ? 'danger' : row.criticality === 'High' ? 'warning' : 'info'" size="small">
              {{ row.criticality }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Trend" align="center" min-width="80">
          <template #default="{ row }">
            <div class="trend-cell">
              <el-icon v-if="row.trend === 'up'" class="trend-up"><ArrowUp /></el-icon>
              <el-icon v-else-if="row.trend === 'down'" class="trend-down"><ArrowDown /></el-icon>
              <span v-else class="trend-stable">→</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Top Faults" align="center" min-width="200">
          <template #default="{ row }">
            <div class="top-faults-tags">
              <el-tag v-for="(fault, idx) in row.topFaults.slice(0, 2)" :key="idx" size="small" type="info" effect="plain">
                {{ fault }}
              </el-tag>
              <el-tooltip v-if="row.topFaults.length > 2" :content="row.topFaults.slice(2).join(', ')" placement="top">
                <el-tag size="small" type="info">+{{ row.topFaults.length - 2 }}</el-tag>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Fault Summary by Location -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Fault Summary by Location</span>
          <el-tag type="info" size="small">Site Analysis</el-tag>
        </div>
      </template>
      <el-table :data="locationSummary" stripe>
        <el-table-column prop="location" label="Location" align="center" min-width="150" />
        <el-table-column label="Total Faults" align="center" min-width="120">
          <template #default="{ row }">
            <span :style="{ color: row.faultCount > 60 ? '#F56C6C' : '#E6A23C' }">
              {{ row.faultCount }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="assetsAffected" label="Assets Affected" align="center" min-width="130" />
        <el-table-column prop="criticalAssets" label="Critical Assets" align="center" min-width="120">
          <template #default="{ row }">
            <span :style="{ color: row.criticalAssets > 4 ? '#F56C6C' : '#E6A23C' }">
              {{ row.criticalAssets }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Total Downtime" align="center" min-width="120">
          <template #default="{ row }">
            {{ row.downtime }}h
          </template>
        </el-table-column>
        <el-table-column label="Fault Density" align="center" min-width="130">
          <template #default="{ row }">
            {{ (row.faultCount / row.assetsAffected).toFixed(1) }} faults/asset
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Criticality Impact Matrix -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Criticality Impact Matrix</span>
          <el-tag type="danger" size="small">Risk Assessment</el-tag>
        </div>
      </template>
      <el-table :data="criticalityImpact" stripe>
        <el-table-column prop="criticality" label="Criticality Level" align="center" min-width="120">
          <template #default="{ row }">
            <el-tag :type="row.criticality === 'Critical' ? 'danger' : row.criticality === 'High' ? 'warning' : row.criticality === 'Medium' ? 'primary' : 'success'" size="small">
              {{ row.criticality }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Fault Count" align="center" min-width="100">
          <template #default="{ row }">
            {{ row.faultCount }}
          </template>
        </el-table-column>
        <el-table-column label="Avg Downtime" align="center" min-width="120">
          <template #default="{ row }">
            {{ (row.totalDowntime / row.faultCount).toFixed(1) }}h
          </template>
        </el-table-column>
        <el-table-column prop="assetsCount" label="Assets Count" align="center" min-width="110" />
        <el-table-column label="SLA Impact" align="center" min-width="150">
          <template #default="{ row }">
            <el-progress :percentage="row.slaImpact" :stroke-width="8" :color="row.slaImpact < 90 ? '#F56C6C' : '#67C23A'" />
          </template>
        </el-table-column>
        <el-table-column label="Priority" align="center" min-width="130">
          <template #default="{ row }">
            <span v-if="row.criticality === 'Critical'" class="priority-high">Immediate Action</span>
            <span v-else-if="row.criticality === 'High'" class="priority-med">Schedule Review</span>
            <span v-else class="priority-low">Monitor Only</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
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

/* ==================== Main Content ==================== */
.top-fault-assets {
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

/* ==================== KPI Cards ==================== */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.kpi-card {
  border-radius: 20px;
  transition: all 0.3s ease;
  border: none;
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

.kpi-icon.total { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
.kpi-icon.assets { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; }
.kpi-icon.downtime { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; }
.kpi-icon.top { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; }
.kpi-icon.impact { background: linear-gradient(135deg, #f6d365 0%, #fda085 100%); color: white; }

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

/* ==================== Charts ==================== */
.chart-card {
  border-radius: 20px;
  margin-bottom: 24px;
  border: none;
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
  font-size: 15px;
}

.chart {
  width: 100%;
  height: 380px;
}

/* ==================== Tables ==================== */
.table-card {
  border-radius: 20px;
  margin-bottom: 24px;
  border: none;
}

.table-card :deep(.el-card__body) {
  padding: 0;
}

.table-card :deep(.el-table__header-wrapper th) {
  text-align: center;
  background-color: #fafafa;
  font-weight: 600;
}

.table-card :deep(.el-table td) {
  text-align: center;
}

/* ==================== Rank Badge ==================== */
.rank-badge {
  display: inline-block;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  color: #333;
  font-weight: bold;
  font-size: 14px;
  line-height: 36px;
  text-align: center;
}

/* ==================== Fault Count ==================== */
.fault-count {
  font-weight: 600;
  font-size: 16px;
}

/* ==================== Trend Cell ==================== */
.trend-cell {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.trend-up {
  color: #F56C6C;
}

.trend-down {
  color: #67C23A;
}

.trend-stable {
  color: #909399;
}

/* ==================== Top Faults Tags ==================== */
.top-faults-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: center;
}

/* ==================== Priority Labels ==================== */
.priority-high {
  color: #F56C6C;
  font-weight: 600;
}

.priority-med {
  color: #E6A23C;
  font-weight: 500;
}

.priority-low {
  color: #67C23A;
}

/* ==================== Progress Bar in Table ==================== */
.table-card :deep(.el-progress-bar__outer) {
  background-color: #ebeef5;
}

/* ==================== Responsive Design ==================== */
@media (max-width: 1400px) {
  .kpi-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
}

@media (max-width: 1200px) {
  .charts-row {
    grid-template-columns: 1fr;
  }

  .chart {
    height: 350px;
  }
}

@media (max-width: 768px) {
  .top-fault-assets {
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

  .kpi-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .chart {
    height: 280px;
  }

  .top-faults-tags {
    flex-direction: column;
    align-items: center;
  }

  .table-card :deep(.el-table__body-wrapper) {
    overflow-x: auto;
  }

  .table-card :deep(.el-table) {
    min-width: 1000px;
  }
}

@media (max-width: 480px) {
  .kpi-card :deep(.el-card__body) {
    padding: 12px;
  }

  .kpi-icon {
    width: 44px;
    height: 44px;
    font-size: 22px;
  }

  .kpi-value {
    font-size: 18px;
  }
}
</style>