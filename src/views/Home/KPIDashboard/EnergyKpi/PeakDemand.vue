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
        <div class="loading-tip">Not Developed Yet</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Peak Demand Page Content -->
  <div v-else class="peak-demand-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>Peak Demand</h1>
        <p class="subtitle">Monitor peak electricity demand, capacity planning, and demand response opportunities</p>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="refreshData">Refresh</el-button>
        <el-button type="primary" :icon="Download" @click="exportReport">Export Report</el-button>
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            :shortcuts="dateShortcuts"
            size="default"
            style="width: 260px"
            @change="handleDateChange"
        />
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="kpi-cards">
      <div class="kpi-card current-peak">
        <div class="kpi-icon">
          <el-icon :size="32"><Lightning /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ currentPeakDemand }}<span class="unit"> kW</span></div>
          <div class="kpi-label">Current Peak Demand</div>
        </div>
        <div class="kpi-trend" :class="peakTrend >= 0 ? 'negative' : 'positive'">
          <el-icon><CaretBottom v-if="peakTrend >= 0" /><CaretTop v-else /></el-icon>
          {{ Math.abs(peakTrend) }}%
        </div>
      </div>
      <div class="kpi-card capacity">
        <div class="kpi-icon">
          <el-icon :size="32"><Connection /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ availableCapacity }}<span class="unit"> kW</span></div>
          <div class="kpi-label">Available Capacity</div>
        </div>
        <div class="kpi-sub">Total: {{ totalCapacity }} kW</div>
      </div>
      <div class="kpi-card utilization">
        <div class="kpi-icon">
          <el-icon :size="32"><PieChart /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ capacityUtilization }}%</div>
          <div class="kpi-label">Capacity Utilization</div>
        </div>
        <el-progress :percentage="capacityUtilization" :color="getUtilizationColor(capacityUtilization)" :stroke-width="8" style="margin-top: 8px" />
      </div>
      <div class="kpi-card demand-charge">
        <div class="kpi-icon">
          <el-icon :size="32"><Money /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">${{ estimatedDemandCharge }}<span class="unit">k</span></div>
          <div class="kpi-label">Est. Monthly Demand Charge</div>
        </div>
        <div class="kpi-sub">Rate: ${{ demandRate }}/kW</div>
      </div>
    </div>

    <!-- Peak Demand Trend Chart -->
    <div class="chart-card">
      <div class="card-header">
        <h3>Peak Demand Trend</h3>
        <el-radio-group v-model="trendPeriod" size="small" @change="fetchTrendData">
          <el-radio-button label="week">Last 7 Days</el-radio-button>
          <el-radio-button label="month">Last 30 Days</el-radio-button>
          <el-radio-button label="quarter">Last 90 Days</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-container" ref="trendChartRef"></div>
    </div>

    <!-- Peak Demand by Building and Time -->
    <div class="two-columns">
      <div class="chart-card">
        <div class="card-header">
          <h3>Peak Demand by Building</h3>
          <el-select v-model="buildingFilter" placeholder="Filter by building" clearable size="small" style="width: 140px">
            <el-option label="All Buildings" value="all" />
            <el-option label="Building A" value="building-a" />
            <el-option label="Building B" value="building-b" />
            <el-option label="Data Center" value="datacenter" />
          </el-select>
        </div>
        <div class="chart-container" ref="buildingChartRef"></div>
      </div>
      <div class="chart-card">
        <div class="card-header">
          <h3>Peak Demand by Hour (Typical Day)</h3>
        </div>
        <div class="chart-container" ref="hourlyChartRef"></div>
      </div>
    </div>

    <!-- Daily Peak Demand Table -->
    <div class="table-card">
      <div class="card-header">
        <h3>Daily Peak Demand Records</h3>
        <el-input
            v-model="searchText"
            placeholder="Search by building..."
            :prefix-icon="Search"
            style="width: 240px"
            clearable
        />
      </div>
      <el-table :data="filteredDailyPeaks" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="date" label="Date" width="110" sortable />
        <el-table-column prop="building" label="Building" min-width="140">
          <template #default="{ row }">
            <div class="building-cell">
              <el-icon><OfficeBuilding /></el-icon>
              <span>{{ row.building }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="peakTime" label="Peak Time" width="140">
          <template #default="{ row }">
            <span class="time-cell">
              <el-icon><Clock /></el-icon>
              {{ row.peakTime }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="peakDemand" label="Peak Demand (kW)" width="140" align="right" sortable>
          <template #default="{ row }">
            <span :class="getPeakClass(row.peakDemand, row.threshold)">
              {{ row.peakDemand.toFixed(1) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="threshold" label="Threshold (kW)" width="130" align="right">
          <template #default="{ row }">
            {{ row.threshold }}
          </template>
        </el-table-column>
        <el-table-column prop="margin" label="Margin (kW)" width="120" align="right" sortable>
          <template #default="{ row }">
            <span :class="row.margin > 0 ? 'text-warning' : 'text-success'">
              {{ row.margin > 0 ? '-' : '+' }}{{ Math.abs(row.margin).toFixed(1) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.peakDemand <= row.threshold ? 'success' : 'danger'" size="small" effect="dark">
              {{ row.peakDemand <= row.threshold ? 'Normal' : 'Alert' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredDailyPeaks.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Demand Response Opportunities -->
    <div class="opportunities-section">
      <div class="section-header">
        <h2>
          <el-icon><Notification /></el-icon>
          Demand Response Opportunities
        </h2>
        <el-button link type="primary" @click="viewAllOpportunities">View All →</el-button>
      </div>
      <div class="opportunities-list">
        <div v-for="opp in demandResponseOpportunities" :key="opp.id" class="opportunity-item">
          <div class="opp-icon" :class="opp.severity">
            <el-icon><WarningFilled /></el-icon>
          </div>
          <div class="opp-content">
            <div class="opp-title">{{ opp.title }}</div>
            <div class="opp-description">{{ opp.description }}</div>
            <div class="opp-metrics">
              <span><el-icon><Lightning /></el-icon> Peak Reduction Potential: {{ opp.potentialReduction }} kW</span>
              <span><el-icon><Money /></el-icon> Est. Savings: ${{ opp.estimatedSavings }}</span>
              <span><el-icon><Timer /></el-icon> Optimal Window: {{ opp.optimalWindow }}</span>
            </div>
          </div>
          <div class="opp-actions">
            <el-button size="small" type="primary" plain @click="viewOpportunity(opp)">Review</el-button>
            <el-button size="small" type="success" plain @click="applyRecommendation(opp)">Apply</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Peak Demand Alerts -->
    <div class="alerts-section">
      <div class="section-header">
        <h2>
          <el-icon><BellFilled /></el-icon>
          Recent Peak Alerts
        </h2>
        <el-button link type="primary" @click="viewAllAlerts">View All Alerts →</el-button>
      </div>
      <div class="alerts-list">
        <div v-for="alert in recentAlerts" :key="alert.id" class="alert-item" :class="alert.severity">
          <div class="alert-icon">
            <el-icon><WarningFilled /></el-icon>
          </div>
          <div class="alert-content">
            <div class="alert-title">{{ alert.title }}</div>
            <div class="alert-desc">{{ alert.description }}</div>
            <div class="alert-time">{{ formatRelativeTime(alert.timestamp) }}</div>
          </div>
          <div class="alert-actions">
            <el-button size="small" type="primary" link @click="acknowledgeAlert(alert)">Acknowledge</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Refresh,
  Download,
  Lightning,
  Connection,
  PieChart,
  Money,
  Search,
  OfficeBuilding,
  Clock,
  Notification,
  WarningFilled,
  BellFilled,
  Timer,
  CaretTop,
  CaretBottom
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing...',
  'Almost ready...'
]

// ==================== Data Structures ====================
interface DailyPeak {
  id: number
  date: string
  building: string
  peakTime: string
  peakDemand: number
  threshold: number
  margin: number
}

interface DemandResponseOpp {
  id: number
  title: string
  description: string
  severity: 'high' | 'medium' | 'low'
  potentialReduction: number
  estimatedSavings: number
  optimalWindow: string
}

interface PeakAlert {
  id: number
  title: string
  description: string
  severity: 'critical' | 'warning' | 'info'
  timestamp: string
}

// ==================== State ====================
const dateRange = ref<[Date, Date] | null>(null)
const trendPeriod = ref<'week' | 'month' | 'quarter'>('month')
const buildingFilter = ref('all')
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const trendChartRef = ref<HTMLElement | null>(null)
const buildingChartRef = ref<HTMLElement | null>(null)
const hourlyChartRef = ref<HTMLElement | null>(null)
let trendChart: echarts.ECharts | null = null
let buildingChart: echarts.ECharts | null = null
let hourlyChart: echarts.ECharts | null = null

// ==================== Mock Data ====================
const dailyPeaks = ref<DailyPeak[]>([
  { id: 1, date: '2025-05-20', building: 'Building A', peakTime: '14:30', peakDemand: 245.5, threshold: 280, margin: 34.5 },
  { id: 2, date: '2025-05-20', building: 'Building B', peakTime: '15:15', peakDemand: 198.2, threshold: 220, margin: 21.8 },
  { id: 3, date: '2025-05-20', building: 'Data Center', peakTime: '13:45', peakDemand: 520.0, threshold: 500, margin: -20.0 },
  { id: 4, date: '2025-05-19', building: 'Building A', peakTime: '14:15', peakDemand: 252.3, threshold: 280, margin: 27.7 },
  { id: 5, date: '2025-05-19', building: 'Building B', peakTime: '16:00', peakDemand: 205.6, threshold: 220, margin: 14.4 },
  { id: 6, date: '2025-05-19', building: 'Data Center', peakTime: '14:00', peakDemand: 535.2, threshold: 500, margin: -35.2 },
  { id: 7, date: '2025-05-18', building: 'Building A', peakTime: '15:00', peakDemand: 248.7, threshold: 280, margin: 31.3 },
  { id: 8, date: '2025-05-18', building: 'Building B', peakTime: '14:30', peakDemand: 195.4, threshold: 220, margin: 24.6 },
  { id: 9, date: '2025-05-18', building: 'Data Center', peakTime: '13:30', peakDemand: 528.5, threshold: 500, margin: -28.5 },
  { id: 10, date: '2025-05-17', building: 'Building A', peakTime: '13:45', peakDemand: 238.9, threshold: 280, margin: 41.1 },
  { id: 11, date: '2025-05-17', building: 'Building B', peakTime: '15:30', peakDemand: 202.1, threshold: 220, margin: 17.9 },
  { id: 12, date: '2025-05-17', building: 'Data Center', peakTime: '14:15', peakDemand: 542.0, threshold: 500, margin: -42.0 }
])

const demandResponseOpportunities = ref<DemandResponseOpp[]>([
  { id: 1, title: 'HVAC Setpoint Adjustment', description: 'Increase cooling setpoint by 2°C during peak hours to reduce load.', severity: 'high', potentialReduction: 45, estimatedSavings: 5400, optimalWindow: '13:00 - 16:00' },
  { id: 2, title: 'Lighting Load Shedding', description: 'Dim non-critical lighting by 30% during peak demand period.', severity: 'high', potentialReduction: 28, estimatedSavings: 3360, optimalWindow: '14:00 - 17:00' },
  { id: 3, title: 'UPS Battery Contribution', description: 'Utilize UPS batteries to supplement power during peak periods.', severity: 'medium', potentialReduction: 35, estimatedSavings: 4200, optimalWindow: '13:30 - 15:30' },
  { id: 4, title: 'Chiller Pre-cooling', description: 'Pre-cool building before peak hours to reduce afternoon load.', severity: 'medium', potentialReduction: 52, estimatedSavings: 6240, optimalWindow: '06:00 - 09:00' }
])

const recentAlerts = ref<PeakAlert[]>([
  { id: 1, title: 'Data Center Exceeds Peak Threshold', description: 'Data Center peak demand reached 542 kW, exceeding 500 kW threshold.', severity: 'critical', timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString() },
  { id: 2, title: 'Building A Peak Approaching Limit', description: 'Building A peak demand at 252 kW, 90% of 280 kW threshold.', severity: 'warning', timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString() },
  { id: 3, title: 'Peak Demand Period Forecast', description: 'High temperatures expected tomorrow between 13:00-16:00. Prepare for potential peak.', severity: 'info', timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString() }
])

// ==================== Computed Values ====================
const currentPeakDemand = computed(() => 542.0)
const totalCapacity = computed(() => 1200)
const availableCapacity = computed(() => totalCapacity.value - currentPeakDemand.value)
const capacityUtilization = computed(() => (currentPeakDemand.value / totalCapacity.value * 100).toFixed(1))
const peakTrend = computed(() => 3.5)
const estimatedDemandCharge = computed(() => ((currentPeakDemand.value * 15) / 1000).toFixed(0))
const demandRate = computed(() => 15.00)

const filteredDailyPeaks = computed(() => {
  let result = [...dailyPeaks.value]
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(d => d.building.toLowerCase().includes(search))
  }
  if (buildingFilter.value !== 'all') {
    const filterMap: Record<string, string> = {
      'building-a': 'Building A',
      'building-b': 'Building B',
      'datacenter': 'Data Center'
    }
    result = result.filter(d => d.building === filterMap[buildingFilter.value])
  }
  if (dateRange.value && dateRange.value[0] && dateRange.value[1]) {
    const [start, end] = dateRange.value
    result = result.filter(d => {
      const date = new Date(d.date)
      return date >= start && date <= end
    })
  }
  return result
})

// ==================== Helper Functions ====================
const getPeakClass = (peak: number, threshold: number) => {
  return peak <= threshold ? 'text-success' : 'text-danger'
}

const getUtilizationColor = (percentage: number) => {
  if (percentage < 70) return '#67c23a'
  if (percentage < 85) return '#e6a23c'
  return '#f56c6c'
}

const formatRelativeTime = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMins = Math.floor((now.getTime() - date.getTime()) / 60000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins} min ago`
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)} hours ago`
  return `${Math.floor(diffMins / 1440)} days ago`
}

const dateShortcuts = [
  { text: 'Last 7 Days', value: () => { const end = new Date(); const start = new Date(); start.setDate(start.getDate() - 7); return [start, end] } },
  { text: 'Last 30 Days', value: () => { const end = new Date(); const start = new Date(); start.setDate(start.getDate() - 30); return [start, end] } },
  { text: 'This Month', value: () => { const end = new Date(); const start = new Date(); start.setDate(1); return [start, end] } }
]

// ==================== Chart Functions ====================
const generateTrendData = () => {
  const days = trendPeriod.value === 'week' ? 7 : trendPeriod.value === 'month' ? 30 : 90
  const dates: string[] = []
  const buildingA: number[] = []
  const buildingB: number[] = []
  const dataCenter: number[] = []
  const threshold: number[] = []

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    dates.push(`${date.getMonth() + 1}/${date.getDate()}`)

    buildingA.push(Number((240 + Math.sin(i * 0.3) * 15 + Math.random() * 10).toFixed(1)))
    buildingB.push(Number((195 + Math.cos(i * 0.25) * 12 + Math.random() * 8).toFixed(1)))
    dataCenter.push(Number((515 + Math.sin(i * 0.4) * 25 + Math.random() * 15).toFixed(1)))
    threshold.push(500)
  }

  return { dates, buildingA, buildingB, dataCenter, threshold }
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)
  const data = generateTrendData()

  trendChart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: (value: number) => value + ' kW' },
    legend: { data: ['Building A', 'Building B', 'Data Center', 'Threshold (500 kW)'], bottom: 0 },
    grid: { left: '3%', right: '4%', top: '10%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: data.dates },
    yAxis: { type: 'value', name: 'Peak Demand (kW)' },
    series: [
      { name: 'Building A', type: 'line', data: data.buildingA, smooth: true, symbol: 'circle', lineStyle: { width: 2, color: '#409eff' } },
      { name: 'Building B', type: 'line', data: data.buildingB, smooth: true, symbol: 'diamond', lineStyle: { width: 2, color: '#67c23a' } },
      { name: 'Data Center', type: 'line', data: data.dataCenter, smooth: true, symbol: 'triangle', lineStyle: { width: 2, color: '#e6a23c' }, areaStyle: { opacity: 0.1 } },
      { name: 'Threshold (500 kW)', type: 'line', data: data.threshold, smooth: false, symbol: 'none', lineStyle: { width: 2, color: '#f56c6c', type: 'dashed' } }
    ]
  })
}

const initBuildingChart = () => {
  if (!buildingChartRef.value) return
  if (buildingChart) buildingChart.dispose()

  buildingChart = echarts.init(buildingChartRef.value)

  const buildings = ['Building A', 'Building B', 'Data Center']
  const peakDemand = [252.3, 205.6, 542.0]
  const threshold = [280, 220, 500]

  buildingChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: (value: number) => value + ' kW' },
    legend: { data: ['Peak Demand', 'Threshold'], bottom: 0 },
    grid: { left: '10%', right: '5%', top: '5%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: buildings },
    yAxis: { type: 'value', name: 'Peak Demand (kW)' },
    series: [
      { name: 'Peak Demand', type: 'bar', data: peakDemand, itemStyle: { borderRadius: [4, 4, 0, 0], color: (params: any) => params.data <= threshold[params.dataIndex] ? '#67c23a' : '#f56c6c' }, label: { show: true, position: 'top', formatter: '{c} kW' } },
      { name: 'Threshold', type: 'line', data: threshold, symbol: 'none', lineStyle: { width: 2, color: '#e6a23c', type: 'dashed' } }
    ]
  })
}

const initHourlyChart = () => {
  if (!hourlyChartRef.value) return
  if (hourlyChart) hourlyChart.dispose()

  hourlyChart = echarts.init(hourlyChartRef.value)

  const hours = ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00']
  const buildingA = [120, 115, 110, 108, 105, 110, 130, 160, 200, 220, 235, 240, 245, 248, 252, 250, 240, 225, 200, 180, 160, 145, 130, 122]
  const buildingB = [95, 92, 88, 85, 82, 88, 105, 130, 165, 180, 190, 195, 198, 200, 205, 202, 195, 180, 160, 145, 130, 118, 105, 98]
  const dataCenter = [450, 445, 440, 435, 430, 440, 460, 480, 500, 510, 515, 520, 525, 530, 542, 538, 530, 520, 510, 500, 490, 475, 460, 452]

  hourlyChart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: (value: number) => value + ' kW' },
    legend: { data: ['Building A', 'Building B', 'Data Center'], bottom: 0 },
    grid: { left: '3%', right: '4%', top: '10%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', data: hours, axisLabel: { rotate: 45, interval: 3 } },
    yAxis: { type: 'value', name: 'Power Demand (kW)' },
    series: [
      { name: 'Building A', type: 'line', data: buildingA, smooth: true, lineStyle: { width: 2, color: '#409eff' }, areaStyle: { opacity: 0.3 } },
      { name: 'Building B', type: 'line', data: buildingB, smooth: true, lineStyle: { width: 2, color: '#67c23a' }, areaStyle: { opacity: 0.3 } },
      { name: 'Data Center', type: 'line', data: dataCenter, smooth: true, lineStyle: { width: 2, color: '#e6a23c' }, areaStyle: { opacity: 0.3 } }
    ]
  })
}

// ==================== Actions ====================
const refreshData = async () => {
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  ElMessage.success('Peak demand data refreshed')
  initTrendChart()
  initBuildingChart()
  initHourlyChart()
  tableLoading.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting peak demand report...')
}

const fetchTrendData = () => {
  initTrendChart()
}

const handleDateChange = () => {
  currentPage.value = 1
}

const viewAllOpportunities = () => {
  ElMessage.info('Viewing all demand response opportunities')
}

const viewOpportunity = (opp: DemandResponseOpp) => {
  ElMessage.info(`Reviewing: ${opp.title}`)
}

const applyRecommendation = (opp: DemandResponseOpp) => {
  ElMessage.success(`Applied recommendation: ${opp.title}`)
}

const viewAllAlerts = () => {
  ElMessage.info('Viewing all peak alerts')
}

const acknowledgeAlert = (alert: PeakAlert) => {
  ElMessage.success(`Alert acknowledged: ${alert.title}`)
  recentAlerts.value = recentAlerts.value.filter(a => a.id !== alert.id)
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Window Resize Handler ====================
const handleResize = () => {
  trendChart?.resize()
  buildingChart?.resize()
  hourlyChart?.resize()
}

// ==================== Lifecycle ====================
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
      setTimeout(() => {
        initTrendChart()
        initBuildingChart()
        initHourlyChart()
      }, 100)
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  buildingChart?.dispose()
  hourlyChart?.dispose()
})
</script>

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

.spinner-ring:nth-child(1) { border-top-color: #3b82f6; animation-delay: 0s; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }

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
.peak-demand-page {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-title h1 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2f3d;
  margin: 0 0 4px 0;
}

.header-title .subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* KPI Cards */
.kpi-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.kpi-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s, box-shadow 0.2s;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.kpi-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.kpi-card.current-peak .kpi-icon { background: #e8f4ff; color: #409eff; }
.kpi-card.capacity .kpi-icon { background: #e8f8f0; color: #67c23a; }
.kpi-card.utilization .kpi-icon { background: #fff7e8; color: #e6a23c; }
.kpi-card.demand-charge .kpi-icon { background: #ffe8e8; color: #f56c6c; }

.kpi-info {
  flex: 1;
}

.kpi-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
  line-height: 1.2;
}

.kpi-value .unit {
  font-size: 14px;
  font-weight: 400;
  color: #909399;
}

.kpi-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.kpi-sub {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 2px;
}

.kpi-trend {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 13px;
  font-weight: 500;
}

.kpi-trend.positive { color: #67c23a; }
.kpi-trend.negative { color: #f56c6c; }

/* Chart Cards */
.chart-card, .table-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.card-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: #1f2f3d;
}

.chart-container {
  height: 320px;
  width: 100%;
}

.two-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

/* Table Styles */
.building-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.time-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.text-success {
  color: #67c23a;
  font-weight: 500;
}

.text-danger {
  color: #f56c6c;
  font-weight: 500;
}

.text-warning {
  color: #e6a23c;
  font-weight: 500;
}

.pagination-wrapper {
  padding: 20px 0 0;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
  margin-top: 16px;
}

/* Opportunities Section */
.opportunities-section, .alerts-section {
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1f2f3d;
}

.opportunities-list, .alerts-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.opportunity-item, .alert-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 14px;
  transition: all 0.2s;
}

.opportunity-item:hover, .alert-item:hover {
  background: #f5f7fa;
  transform: translateX(4px);
}

.opp-icon, .alert-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.opp-icon.high, .alert-item.critical .alert-icon {
  background: #ffe8e8;
  color: #f56c6c;
}

.opp-icon.medium, .alert-item.warning .alert-icon {
  background: #fff7e8;
  color: #e6a23c;
}

.opp-icon.low, .alert-item.info .alert-icon {
  background: #e8f4ff;
  color: #409eff;
}

.opp-content, .alert-content {
  flex: 1;
}

.opp-title, .alert-title {
  font-weight: 600;
  color: #1f2f3d;
  margin-bottom: 6px;
}

.opp-description, .alert-desc {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.opp-metrics {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #909399;
}

.opp-metrics .el-icon, .alert-time .el-icon {
  vertical-align: middle;
  margin-right: 4px;
}

.alert-time {
  font-size: 11px;
  color: #c0c4cc;
}

.opp-actions, .alert-actions {
  opacity: 0;
  transition: opacity 0.2s;
  display: flex;
  gap: 8px;
}

.opportunity-item:hover .opp-actions,
.alert-item:hover .alert-actions {
  opacity: 1;
}

:deep(.el-table) {
  border-radius: 12px;
}

:deep(.el-table th.el-table__cell) {
  background-color: #fafafa;
  font-weight: 600;
  color: #1f2f3d;
}
</style>