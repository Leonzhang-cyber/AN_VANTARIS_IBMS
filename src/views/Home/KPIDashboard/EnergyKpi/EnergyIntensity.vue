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

  <!-- Energy Intensity Page Content -->
  <div v-else class="energy-intensity-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>Energy Intensity</h1>
        <p class="subtitle">Monitor energy consumption per unit area and track efficiency improvements</p>
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
      <div class="kpi-card current-eui">
        <div class="kpi-icon">
          <el-icon :size="32"><Lightning /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ currentEUI }}<span class="unit"> kWh/m²</span></div>
          <div class="kpi-label">Current Energy Intensity (EUI)</div>
        </div>
        <div class="kpi-trend" :class="euiTrend >= 0 ? 'negative' : 'positive'">
          <el-icon><CaretBottom v-if="euiTrend >= 0" /><CaretTop v-else /></el-icon>
          {{ Math.abs(euiTrend) }}%
        </div>
      </div>
      <div class="kpi-card baseline">
        <div class="kpi-icon">
          <el-icon :size="32"><Flag /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ baselineEUI }}<span class="unit"> kWh/m²</span></div>
          <div class="kpi-label">Baseline EUI</div>
        </div>
        <div class="kpi-sub">Baseline Year: 2023</div>
      </div>
      <div class="kpi-card target">
        <div class="kpi-icon">
          <el-icon :size="32"><Medal /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ targetEUI }}<span class="unit"> kWh/m²</span></div>
          <div class="kpi-label">Target EUI</div>
        </div>
        <div class="kpi-sub">Target Year: 2026</div>
      </div>
      <div class="kpi-card improvement">
        <div class="kpi-icon">
          <el-icon :size="32"><TrendCharts /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ improvementRate }}%</div>
          <div class="kpi-label">Improvement vs Baseline</div>
        </div>
        <div class="kpi-trend positive">
          <el-icon><CaretTop /></el-icon>
          {{ improvementRate }}%
        </div>
      </div>
    </div>

    <!-- Energy Intensity Trend Chart -->
    <div class="chart-card">
      <div class="card-header">
        <h3>Energy Intensity Trend</h3>
        <el-radio-group v-model="trendPeriod" size="small" @change="fetchTrendData">
          <el-radio-button label="month">Monthly</el-radio-button>
          <el-radio-button label="quarter">Quarterly</el-radio-button>
          <el-radio-button label="year">Yearly</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-container" ref="trendChartRef"></div>
    </div>

    <!-- EUI by Building -->
    <div class="two-columns">
      <div class="chart-card">
        <div class="card-header">
          <h3>EUI by Building</h3>
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
          <h3>Energy Breakdown by Source</h3>
        </div>
        <div class="chart-container" ref="sourceChartRef"></div>
      </div>
    </div>

    <!-- Monthly EUI Table -->
    <div class="table-card">
      <div class="card-header">
        <h3>Monthly Energy Intensity Data</h3>
        <el-input
            v-model="searchText"
            placeholder="Search by building..."
            :prefix-icon="Search"
            style="width: 240px"
            clearable
        />
      </div>
      <el-table :data="filteredMonthlyData" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="month" label="Month" width="100" sortable />
        <el-table-column prop="building" label="Building" min-width="140">
          <template #default="{ row }">
            <div class="building-cell">
              <el-icon><OfficeBuilding /></el-icon>
              <span>{{ row.building }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="area" label="Area (m²)" width="120" align="right">
          <template #default="{ row }">
            {{ row.area.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="energyConsumption" label="Energy (kWh)" width="140" align="right">
          <template #default="{ row }">
            {{ row.energyConsumption.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="eui" label="EUI (kWh/m²)" width="130" align="right" sortable>
          <template #default="{ row }">
            <span :class="getEuiClass(row.eui, row.targetEui)">
              {{ row.eui.toFixed(1) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="targetEui" label="Target (kWh/m²)" width="130" align="right">
          <template #default="{ row }">
            {{ row.targetEui.toFixed(1) }}
          </template>
        </el-table-column>
        <el-table-column prop="variance" label="vs Target" width="110" align="right" sortable>
          <template #default="{ row }">
            <span :class="row.variance <= 0 ? 'text-success' : 'text-danger'">
              {{ row.variance > 0 ? '+' : '' }}{{ row.variance.toFixed(1) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.eui <= row.targetEui ? 'success' : 'danger'" size="small" effect="dark">
              {{ row.eui <= row.targetEui ? 'On Track' : 'Exceeded' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredMonthlyData.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Benchmark Comparison -->
    <div class="benchmark-section">
      <div class="section-header">
        <h2>
          <el-icon><DataAnalysis /></el-icon>
          Industry Benchmark Comparison
        </h2>
        <el-button link type="primary" @click="viewBenchmarkDetails">View Details →</el-button>
      </div>
      <div class="benchmark-grid">
        <div class="benchmark-card">
          <div class="benchmark-title">Current EUI</div>
          <div class="benchmark-value">{{ currentEUI }} <span>kWh/m²</span></div>
          <div class="benchmark-compare">
            <span class="label">vs Industry Average</span>
            <span :class="currentEUI <= industryAvg ? 'text-success' : 'text-danger'">
              {{ currentEUI <= industryAvg ? 'Better' : 'Worse' }}
            </span>
            <span class="diff" :class="currentEUI <= industryAvg ? 'text-success' : 'text-danger'">
              ({{ Math.abs(((currentEUI - industryAvg) / industryAvg * 100)).toFixed(1) }}%)
            </span>
          </div>
        </div>
        <div class="benchmark-card">
          <div class="benchmark-title">Industry Average</div>
          <div class="benchmark-value">{{ industryAvg }} <span>kWh/m²</span></div>
          <div class="benchmark-compare">
            <span class="label">Typical Office Building</span>
          </div>
        </div>
        <div class="benchmark-card">
          <div class="benchmark-title">Top Performer</div>
          <div class="benchmark-value">{{ topPerformer }} <span>kWh/m²</span></div>
          <div class="benchmark-compare">
            <span class="label">Industry Best in Class</span>
          </div>
        </div>
        <div class="benchmark-card">
          <div class="benchmark-title">Improvement Needed</div>
          <div class="benchmark-value">{{ improvementNeeded }}%</div>
          <div class="benchmark-compare">
            <span class="label">to reach Top Performer</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Recommendations -->
    <div class="recommendations-section">
      <div class="section-header">
        <h2>
          <el-icon><EditPen /></el-icon>
          Energy Efficiency Recommendations
        </h2>
      </div>
      <div class="recommendations-list">
        <div v-for="rec in recommendations" :key="rec.id" class="recommendation-item">
          <div class="rec-icon" :class="rec.priority">
            <el-icon><Check /></el-icon>
          </div>
          <div class="rec-content">
            <div class="rec-title">{{ rec.title }}</div>
            <div class="rec-description">{{ rec.description }}</div>
            <div class="rec-metrics">
              <span><el-icon><Lightning /></el-icon> Potential Savings: {{ rec.savings }}</span>
              <span><el-icon><Wallet /></el-icon> Est. Payback: {{ rec.payback }}</span>
            </div>
          </div>
          <div class="rec-actions">
            <el-button size="small" type="primary" plain @click="viewRecommendation(rec)">View Details</el-button>
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
  Flag,
  Medal,
  TrendCharts,
  Search,
  OfficeBuilding,
  DataAnalysis,
  EditPen,
  Check,
  Wallet,
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
interface MonthlyEUIData {
  id: number
  month: string
  building: string
  area: number
  energyConsumption: number
  eui: number
  targetEui: number
  variance: number
}

interface Recommendation {
  id: number
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
  savings: string
  payback: string
}

// ==================== State ====================
const dateRange = ref<[Date, Date] | null>(null)
const trendPeriod = ref<'month' | 'quarter' | 'year'>('month')
const buildingFilter = ref('all')
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const trendChartRef = ref<HTMLElement | null>(null)
const buildingChartRef = ref<HTMLElement | null>(null)
const sourceChartRef = ref<HTMLElement | null>(null)
let trendChart: echarts.ECharts | null = null
let buildingChart: echarts.ECharts | null = null
let sourceChart: echarts.ECharts | null = null

// ==================== Mock Data ====================
const monthlyData = ref<MonthlyEUIData[]>([
  { id: 1, month: '2024-01', building: 'Building A', area: 15000, energyConsumption: 97500, eui: 6.5, targetEui: 7.0, variance: -7.1 },
  { id: 2, month: '2024-01', building: 'Building B', area: 12000, energyConsumption: 81600, eui: 6.8, targetEui: 7.2, variance: -5.6 },
  { id: 3, month: '2024-01', building: 'Data Center', area: 5000, energyConsumption: 275000, eui: 55.0, targetEui: 52.0, variance: 5.8 },
  { id: 4, month: '2024-02', building: 'Building A', area: 15000, energyConsumption: 94500, eui: 6.3, targetEui: 7.0, variance: -10.0 },
  { id: 5, month: '2024-02', building: 'Building B', area: 12000, energyConsumption: 79200, eui: 6.6, targetEui: 7.2, variance: -8.3 },
  { id: 6, month: '2024-02', building: 'Data Center', area: 5000, energyConsumption: 270000, eui: 54.0, targetEui: 52.0, variance: 3.8 },
  { id: 7, month: '2024-03', building: 'Building A', area: 15000, energyConsumption: 93000, eui: 6.2, targetEui: 7.0, variance: -11.4 },
  { id: 8, month: '2024-03', building: 'Building B', area: 12000, energyConsumption: 78000, eui: 6.5, targetEui: 7.2, variance: -9.7 },
  { id: 9, month: '2024-03', building: 'Data Center', area: 5000, energyConsumption: 268000, eui: 53.6, targetEui: 52.0, variance: 3.1 },
  { id: 10, month: '2024-04', building: 'Building A', area: 15000, energyConsumption: 96000, eui: 6.4, targetEui: 7.0, variance: -8.6 },
  { id: 11, month: '2024-04', building: 'Building B', area: 12000, energyConsumption: 80400, eui: 6.7, targetEui: 7.2, variance: -6.9 },
  { id: 12, month: '2024-04', building: 'Data Center', area: 5000, energyConsumption: 275000, eui: 55.0, targetEui: 52.0, variance: 5.8 },
  { id: 13, month: '2024-05', building: 'Building A', area: 15000, energyConsumption: 99000, eui: 6.6, targetEui: 7.0, variance: -5.7 },
  { id: 14, month: '2024-05', building: 'Building B', area: 12000, energyConsumption: 82800, eui: 6.9, targetEui: 7.2, variance: -4.2 },
  { id: 15, month: '2024-05', building: 'Data Center', area: 5000, energyConsumption: 280000, eui: 56.0, targetEui: 52.0, variance: 7.7 },
  { id: 16, month: '2024-06', building: 'Building A', area: 15000, energyConsumption: 102000, eui: 6.8, targetEui: 7.0, variance: -2.9 },
  { id: 17, month: '2024-06', building: 'Building B', area: 12000, energyConsumption: 85200, eui: 7.1, targetEui: 7.2, variance: -1.4 },
  { id: 18, month: '2024-06', building: 'Data Center', area: 5000, energyConsumption: 285000, eui: 57.0, targetEui: 52.0, variance: 9.6 }
])

const recommendations = ref<Recommendation[]>([
  { id: 1, title: 'Upgrade HVAC Chiller System', description: 'Replace aging chiller with high-efficiency variable speed model to reduce cooling energy consumption.', priority: 'high', savings: '45,000 kWh/year', payback: '2.5 years' },
  { id: 2, title: 'Install LED Lighting with Occupancy Sensors', description: 'Retrofit existing lighting with LED fixtures and smart controls for better energy management.', priority: 'high', savings: '28,000 kWh/year', payback: '1.8 years' },
  { id: 3, title: 'Optimize Air Handler Schedules', description: 'Adjust AHU operating schedules to match actual occupancy patterns and reduce runtime.', priority: 'medium', savings: '15,000 kWh/year', payback: '0.5 years' },
  { id: 4, title: 'Data Center Hot Aisle Containment', description: 'Implement hot aisle containment to improve cooling efficiency and reduce CRAC load.', priority: 'medium', savings: '32,000 kWh/year', payback: '3.2 years' }
])

// ==================== Computed Values ====================
const currentEUI = computed(() => 6.9)
const baselineEUI = computed(() => 8.2)
const targetEUI = computed(() => 5.8)
const improvementRate = computed(() => ((baselineEUI.value - currentEUI.value) / baselineEUI.value * 100).toFixed(1))
const euiTrend = computed(() => -2.8)

const industryAvg = computed(() => 7.5)
const topPerformer = computed(() => 4.8)
const improvementNeeded = computed(() => ((currentEUI.value - topPerformer.value) / topPerformer.value * 100).toFixed(1))

const filteredMonthlyData = computed(() => {
  let result = [...monthlyData.value]
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
      const date = new Date(d.month + '-01')
      return date >= start && date <= end
    })
  }
  return result
})

// ==================== Helper Functions ====================
const getEuiClass = (eui: number, target: number) => {
  return eui <= target ? 'text-success' : 'text-danger'
}

const dateShortcuts = [
  { text: 'Last 6 Months', value: () => { const end = new Date(); const start = new Date(); start.setMonth(start.getMonth() - 6); return [start, end] } },
  { text: 'Year to Date', value: () => { const end = new Date(); const start = new Date(); start.setMonth(0, 1); return [start, end] } },
  { text: 'Last Year', value: () => { const end = new Date(); const start = new Date(); start.setFullYear(start.getFullYear() - 1); return [start, end] } }
]

// ==================== Chart Functions ====================
const generateTrendData = () => {
  if (trendPeriod.value === 'month') {
    return {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
      values: [7.2, 7.1, 7.0, 6.9, 6.8, 6.9, 7.0, 6.8, 6.7, 6.6, 6.5, 6.4],
      target: [7.5, 7.5, 7.4, 7.3, 7.3, 7.2, 7.2, 7.1, 7.0, 6.9, 6.9, 6.8],
      baseline: [8.2, 8.2, 8.1, 8.1, 8.0, 8.0, 7.9, 7.9, 7.8, 7.8, 7.7, 7.7]
    }
  }
  if (trendPeriod.value === 'quarter') {
    return {
      labels: ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024', 'Q1 2025'],
      values: [7.1, 6.9, 6.8, 6.6, 6.4],
      target: [7.3, 7.2, 7.1, 6.9, 6.8],
      baseline: [8.1, 8.0, 7.9, 7.8, 7.7]
    }
  }
  return {
    labels: ['2021', '2022', '2023', '2024', '2025'],
    values: [8.5, 8.0, 7.6, 7.0, 6.4],
    target: [8.0, 7.6, 7.3, 6.9, 6.6],
    baseline: [8.5, 8.5, 8.5, 8.5, 8.5]
  }
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)
  const data = generateTrendData()

  trendChart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: (value: number) => value + ' kWh/m²' },
    legend: { data: ['Current EUI', 'Target EUI', 'Baseline EUI'], bottom: 0 },
    grid: { left: '3%', right: '4%', top: '10%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', data: data.labels },
    yAxis: { type: 'value', name: 'Energy Intensity (kWh/m²)', min: 5, max: 9 },
    series: [
      { name: 'Current EUI', type: 'line', data: data.values, smooth: true, symbol: 'circle', lineStyle: { width: 3, color: '#409eff' }, areaStyle: { opacity: 0.1, color: '#409eff' } },
      { name: 'Target EUI', type: 'line', data: data.target, smooth: true, symbol: 'diamond', lineStyle: { width: 2, color: '#67c23a', type: 'dashed' } },
      { name: 'Baseline EUI', type: 'line', data: data.baseline, smooth: true, symbol: 'none', lineStyle: { width: 2, color: '#909399', type: 'dotted' } }
    ]
  })
}

const initBuildingChart = () => {
  if (!buildingChartRef.value) return
  if (buildingChart) buildingChart.dispose()

  buildingChart = echarts.init(buildingChartRef.value)

  const buildings = ['Building A', 'Building B', 'Data Center']
  const current = [6.5, 6.8, 54.2]
  const target = [7.0, 7.2, 52.0]

  buildingChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: (value: number) => value + ' kWh/m²' },
    legend: { data: ['Current EUI', 'Target EUI'], bottom: 0 },
    grid: { left: '10%', right: '5%', top: '5%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: buildings },
    yAxis: { type: 'value', name: 'Energy Intensity (kWh/m²)' },
    series: [
      { name: 'Current EUI', type: 'bar', data: current, itemStyle: { borderRadius: [4, 4, 0, 0], color: (params: any) => params.data <= target[params.dataIndex] ? '#67c23a' : '#f56c6c' }, label: { show: true, position: 'top', formatter: '{c} kWh/m²' } },
      { name: 'Target EUI', type: 'line', data: target, symbol: 'none', lineStyle: { width: 2, color: '#e6a23c', type: 'dashed' } }
    ]
  })
}

const initSourceChart = () => {
  if (!sourceChartRef.value) return
  if (sourceChart) sourceChart.dispose()

  sourceChart = echarts.init(sourceChartRef.value)

  sourceChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} kWh)' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      type: 'pie', radius: '55%', center: ['50%', '50%'],
      data: [
        { name: 'HVAC', value: 285000, itemStyle: { color: '#409eff' } },
        { name: 'Lighting', value: 125000, itemStyle: { color: '#67c23a' } },
        { name: 'IT Equipment', value: 180000, itemStyle: { color: '#8b5cf6' } },
        { name: 'Other', value: 45000, itemStyle: { color: '#e6a23c' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })
}

// ==================== Actions ====================
const refreshData = async () => {
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  ElMessage.success('Energy intensity data refreshed')
  initTrendChart()
  initBuildingChart()
  initSourceChart()
  tableLoading.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting energy intensity report...')
}

const fetchTrendData = () => {
  initTrendChart()
}

const handleDateChange = () => {
  currentPage.value = 1
}

const viewBenchmarkDetails = () => {
  ElMessage.info('Viewing benchmark details')
}

const viewRecommendation = (rec: Recommendation) => {
  ElMessage.info(`Viewing recommendation: ${rec.title}`)
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Window Resize Handler ====================
const handleResize = () => {
  trendChart?.resize()
  buildingChart?.resize()
  sourceChart?.resize()
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
        initSourceChart()
      }, 100)
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  buildingChart?.dispose()
  sourceChart?.dispose()
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
.energy-intensity-page {
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

.kpi-card.current-eui .kpi-icon { background: #e8f4ff; color: #409eff; }
.kpi-card.baseline .kpi-icon { background: #f0f0f0; color: #909399; }
.kpi-card.target .kpi-icon { background: #e8f8f0; color: #67c23a; }
.kpi-card.improvement .kpi-icon { background: #fff7e8; color: #e6a23c; }

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

.text-success {
  color: #67c23a;
  font-weight: 500;
}

.text-danger {
  color: #f56c6c;
  font-weight: 500;
}

.pagination-wrapper {
  padding: 20px 0 0;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
  margin-top: 16px;
}

/* Benchmark Section */
.benchmark-section {
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

.benchmark-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.benchmark-card {
  background: #fafafa;
  border-radius: 14px;
  padding: 16px;
  text-align: center;
}

.benchmark-title {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.benchmark-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
}

.benchmark-value span {
  font-size: 14px;
  font-weight: 400;
  color: #909399;
}

.benchmark-compare {
  margin-top: 8px;
  font-size: 12px;
}

.benchmark-compare .label {
  color: #909399;
  margin-right: 6px;
}

.benchmark-compare .diff {
  margin-left: 4px;
}

/* Recommendations Section */
.recommendations-section {
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recommendation-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 14px;
  transition: all 0.2s;
}

.recommendation-item:hover {
  background: #f5f7fa;
  transform: translateX(4px);
}

.rec-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e8f4ff;
  color: #409eff;
}

.rec-icon.high {
  background: #ffe8e8;
  color: #f56c6c;
}

.rec-icon.medium {
  background: #fff7e8;
  color: #e6a23c;
}

.rec-icon.low {
  background: #e8f8f0;
  color: #67c23a;
}

.rec-content {
  flex: 1;
}

.rec-title {
  font-weight: 600;
  color: #1f2f3d;
  margin-bottom: 6px;
}

.rec-description {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.rec-metrics {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #909399;
}

.rec-metrics .el-icon {
  vertical-align: middle;
  margin-right: 4px;
}

.rec-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.recommendation-item:hover .rec-actions {
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