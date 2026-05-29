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

  <!-- Carbon Intensity Page Content -->
  <div v-else class="carbon-intensity-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>Carbon Intensity</h1>
        <p class="subtitle">Monitor carbon emissions intensity and track decarbonization progress</p>
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
      <div class="kpi-card current-ci">
        <div class="kpi-icon">
          <el-icon :size="32"><Cloudy /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ currentCarbonIntensity }}<span class="unit"> kg CO₂/m²</span></div>
          <div class="kpi-label">Current Carbon Intensity</div>
        </div>
        <div class="kpi-trend" :class="ciTrend >= 0 ? 'negative' : 'positive'">
          <el-icon><CaretBottom v-if="ciTrend >= 0" /><CaretTop v-else /></el-icon>
          {{ Math.abs(ciTrend) }}%
        </div>
      </div>
      <div class="kpi-card baseline">
        <div class="kpi-icon">
          <el-icon :size="32"><Flag /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ baselineIntensity }}<span class="unit"> kg CO₂/m²</span></div>
          <div class="kpi-label">Baseline Intensity</div>
        </div>
        <div class="kpi-sub">Baseline Year: 2023</div>
      </div>
      <div class="kpi-card target">
        <div class="kpi-icon">
          <el-icon :size="32"><Medal /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ targetIntensity }}<span class="unit"> kg CO₂/m²</span></div>
          <div class="kpi-label">2030 Target</div>
        </div>
        <div class="kpi-sub">SBTi Approved</div>
      </div>
      <div class="kpi-card reduction">
        <div class="kpi-icon">
          <el-icon :size="32"><TrendCharts /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ reductionProgress }}%</div>
          <div class="kpi-label">Reduction vs Baseline</div>
        </div>
        <el-progress :percentage="reductionProgress" :color="getProgressColor(reductionProgress)" :stroke-width="8" style="margin-top: 8px" />
      </div>
    </div>

    <!-- Carbon Intensity Trend Chart -->
    <div class="chart-card">
      <div class="card-header">
        <h3>Carbon Intensity Trend</h3>
        <el-radio-group v-model="trendPeriod" size="small" @change="fetchTrendData">
          <el-radio-button label="month">Monthly</el-radio-button>
          <el-radio-button label="quarter">Quarterly</el-radio-button>
          <el-radio-button label="year">Yearly</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-container" ref="trendChartRef"></div>
    </div>

    <!-- Carbon Intensity by Building and Scope -->
    <div class="two-columns">
      <div class="chart-card">
        <div class="card-header">
          <h3>Carbon Intensity by Building</h3>
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
          <h3>Emissions by Scope</h3>
        </div>
        <div class="chart-container" ref="scopeChartRef"></div>
      </div>
    </div>

    <!-- Monthly Carbon Data Table -->
    <div class="table-card">
      <div class="card-header">
        <h3>Monthly Carbon Emissions Data</h3>
        <el-input
            v-model="searchText"
            placeholder="Search by building..."
            :prefix-icon="Search"
            style="width: 240px"
            clearable
        />
      </div>
      <el-table :data="paginatedCarbonData" stripe v-loading="tableLoading" style="width: 100%">
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
            {{ formatNumberWithCommas(row.area) }}
          </template>
        </el-table-column>
        <el-table-column prop="energyEmissions" label="Energy Emissions (tCO₂)" width="160" align="right" sortable>
          <template #default="{ row }">
            {{ formatNumberWithCommas(row.energyEmissions) }}
          </template>
        </el-table-column>
        <el-table-column prop="totalEmissions" label="Total Emissions (tCO₂)" width="160" align="right" sortable>
          <template #default="{ row }">
            <span :class="getEmissionsClass(row.carbonIntensity, row.targetIntensity)">
              {{ formatNumberWithCommas(row.totalEmissions) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="carbonIntensity" label="Carbon Intensity" width="140" align="right" sortable>
          <template #default="{ row }">
            <span :class="getEmissionsClass(row.carbonIntensity, row.targetIntensity)">
              {{ row.carbonIntensity.toFixed(1) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="targetIntensity" label="Target" width="120" align="right">
          <template #default="{ row }">
            {{ row.targetIntensity.toFixed(1) }}
          </template>
        </el-table-column>
        <el-table-column label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.carbonIntensity <= row.targetIntensity ? 'success' : 'danger'" size="small" effect="dark">
              {{ row.carbonIntensity <= row.targetIntensity ? 'On Track' : 'Off Track' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredCarbonData.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Decarbonization Initiatives -->
    <div class="initiatives-section">
      <div class="section-header">
        <h2>
          <el-icon><Sunny /></el-icon>
          Decarbonization Initiatives
        </h2>
        <el-button link type="primary" @click="viewAllInitiatives">View All →</el-button>
      </div>
      <div class="initiatives-list">
        <div v-for="initiative in decarbonizationInitiatives" :key="initiative.id" class="initiative-item">
          <div class="initiative-icon" :class="initiative.status">
            <el-icon><Check /></el-icon>
          </div>
          <div class="initiative-content">
            <div class="initiative-title">{{ initiative.title }}</div>
            <div class="initiative-description">{{ initiative.description }}</div>
            <div class="initiative-metrics">
              <span><el-icon><Cloudy /></el-icon> CO₂ Reduction: {{ initiative.co2Reduction }} tCO₂/year</span>
              <span><el-icon><Money /></el-icon> Investment: ${{ formatNumberWithCommas(initiative.investment) }}</span>
              <span><el-icon><Timer /></el-icon> Completion: {{ initiative.completionDate }}</span>
            </div>
          </div>
          <div class="initiative-progress">
            <el-progress type="circle" :percentage="initiative.progress" :width="60" :stroke-width="6" :color="getProgressColor(initiative.progress)" />
          </div>
        </div>
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
          <div class="benchmark-title">Current Intensity</div>
          <div class="benchmark-value">{{ currentCarbonIntensity }} <span>kg CO₂/m²</span></div>
        </div>
        <div class="benchmark-card">
          <div class="benchmark-title">Industry Average</div>
          <div class="benchmark-value">{{ industryAvg }} <span>kg CO₂/m²</span></div>
          <div class="benchmark-compare" :class="currentCarbonIntensity <= industryAvg ? 'text-success' : 'text-danger'">
            {{ currentCarbonIntensity <= industryAvg ? 'Below Average ✓' : 'Above Average ⚠' }}
          </div>
        </div>
        <div class="benchmark-card">
          <div class="benchmark-title">Top Quartile</div>
          <div class="benchmark-value">{{ topQuartile }} <span>kg CO₂/m²</span></div>
        </div>
        <div class="benchmark-card">
          <div class="benchmark-title">Gap to Top Quartile</div>
          <div class="benchmark-value">{{ gapToTopQuartile }}%</div>
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
  Cloudy,
  Flag,
  Medal,
  TrendCharts,
  Search,
  OfficeBuilding,
  Sunny,
  Money,
  Timer,
  DataAnalysis,
  Check,
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
interface CarbonData {
  id: number
  month: string
  building: string
  area: number
  energyEmissions: number
  totalEmissions: number
  carbonIntensity: number
  targetIntensity: number
}

interface DecarbonizationInitiative {
  id: number
  title: string
  description: string
  status: 'completed' | 'in-progress' | 'planned'
  co2Reduction: number
  investment: number
  completionDate: string
  progress: number
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
const scopeChartRef = ref<HTMLElement | null>(null)
let trendChart: echarts.ECharts | null = null
let buildingChart: echarts.ECharts | null = null
let scopeChart: echarts.ECharts | null = null

// ==================== Mock Data ====================
const carbonData = ref<CarbonData[]>([
  { id: 1, month: '2025-01', building: 'Building A', area: 15000, energyEmissions: 85, totalEmissions: 95, carbonIntensity: 6.3, targetIntensity: 7.0 },
  { id: 2, month: '2025-01', building: 'Building B', area: 12000, energyEmissions: 72, totalEmissions: 82, carbonIntensity: 6.8, targetIntensity: 7.2 },
  { id: 3, month: '2025-01', building: 'Data Center', area: 5000, energyEmissions: 280, totalEmissions: 310, carbonIntensity: 62.0, targetIntensity: 58.0 },
  { id: 4, month: '2025-02', building: 'Building A', area: 15000, energyEmissions: 82, totalEmissions: 92, carbonIntensity: 6.1, targetIntensity: 7.0 },
  { id: 5, month: '2025-02', building: 'Building B', area: 12000, energyEmissions: 70, totalEmissions: 80, carbonIntensity: 6.7, targetIntensity: 7.2 },
  { id: 6, month: '2025-02', building: 'Data Center', area: 5000, energyEmissions: 275, totalEmissions: 305, carbonIntensity: 61.0, targetIntensity: 58.0 },
  { id: 7, month: '2025-03', building: 'Building A', area: 15000, energyEmissions: 80, totalEmissions: 90, carbonIntensity: 6.0, targetIntensity: 7.0 },
  { id: 8, month: '2025-03', building: 'Building B', area: 12000, energyEmissions: 68, totalEmissions: 78, carbonIntensity: 6.5, targetIntensity: 7.2 },
  { id: 9, month: '2025-03', building: 'Data Center', area: 5000, energyEmissions: 272, totalEmissions: 302, carbonIntensity: 60.4, targetIntensity: 58.0 },
  { id: 10, month: '2025-04', building: 'Building A', area: 15000, energyEmissions: 83, totalEmissions: 93, carbonIntensity: 6.2, targetIntensity: 7.0 },
  { id: 11, month: '2025-04', building: 'Building B', area: 12000, energyEmissions: 71, totalEmissions: 81, carbonIntensity: 6.8, targetIntensity: 7.2 },
  { id: 12, month: '2025-04', building: 'Data Center', area: 5000, energyEmissions: 278, totalEmissions: 308, carbonIntensity: 61.6, targetIntensity: 58.0 }
])

const decarbonizationInitiatives = ref<DecarbonizationInitiative[]>([
  { id: 1, title: 'LED Lighting Retrofit', description: 'Replaced all fluorescent lighting with energy-efficient LED fixtures across Building A and B.', status: 'completed', co2Reduction: 125, investment: 45000, completionDate: '2024-12-15', progress: 100 },
  { id: 2, title: 'Solar Panel Installation', description: 'Installed 500kW rooftop solar PV system on Building A.', status: 'completed', co2Reduction: 210, investment: 250000, completionDate: '2025-01-20', progress: 100 },
  { id: 3, title: 'HVAC Chiller Upgrade', description: 'Replaced old chillers with high-efficiency variable speed models.', status: 'in-progress', co2Reduction: 185, investment: 320000, completionDate: '2025-08-30', progress: 65 },
  { id: 4, title: 'Data Center Cooling Optimization', description: 'Implement hot aisle containment and optimize cooling setpoints.', status: 'in-progress', co2Reduction: 95, investment: 180000, completionDate: '2025-10-15', progress: 40 },
  { id: 5, title: 'EV Fleet Transition', description: 'Replace 20 diesel vehicles with electric alternatives.', status: 'planned', co2Reduction: 150, investment: 600000, completionDate: '2026-06-30', progress: 0 }
])

// ==================== Helper Functions ====================
const formatNumberWithCommas = (value: number): string => {
  if (value === undefined || value === null) return '0'
  return value.toLocaleString()
}

// ==================== Computed Values ====================
const currentCarbonIntensity = computed(() => 32.5)
const baselineIntensity = computed(() => 42.8)
const targetIntensity = computed(() => 25.0)
const reductionProgress = computed(() => {
  const reduction = baselineIntensity.value - currentCarbonIntensity.value
  return Math.round((reduction / baselineIntensity.value) * 100)
})
const ciTrend = computed(() => -4.2)

const industryAvg = computed(() => 38.5)
const topQuartile = computed(() => 28.0)
const gapToTopQuartile = computed(() => {
  const gap = currentCarbonIntensity.value - topQuartile.value
  return Math.round((gap / topQuartile.value) * 100)
})

const filteredCarbonData = computed(() => {
  let result = [...carbonData.value]
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

const paginatedCarbonData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredCarbonData.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getEmissionsClass = (intensity: number, target: number) => {
  return intensity <= target ? 'text-success' : 'text-danger'
}

const getProgressColor = (percentage: number) => {
  if (percentage >= 100) return '#67c23a'
  if (percentage >= 70) return '#409eff'
  if (percentage >= 40) return '#e6a23c'
  return '#f56c6c'
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
      actual: [42.5, 41.8, 40.2, 39.5, 38.2, 37.5, 36.8, 35.5, 34.2, 33.5, 32.8, 32.5],
      target: [42.0, 41.0, 40.0, 39.0, 38.0, 37.0, 36.0, 35.0, 34.0, 33.0, 32.0, 31.5],
      baseline: [42.8, 42.8, 42.8, 42.8, 42.8, 42.8, 42.8, 42.8, 42.8, 42.8, 42.8, 42.8]
    }
  }
  if (trendPeriod.value === 'quarter') {
    return {
      labels: ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024', 'Q1 2025'],
      actual: [41.5, 39.8, 37.5, 35.2, 32.5],
      target: [41.0, 39.5, 37.5, 35.0, 32.5],
      baseline: [42.8, 42.8, 42.8, 42.8, 42.8]
    }
  }
  return {
    labels: ['2021', '2022', '2023', '2024', '2025'],
    actual: [45.2, 43.8, 42.5, 38.5, 32.5],
    target: [44.0, 42.5, 41.0, 36.0, 31.0],
    baseline: [42.8, 42.8, 42.8, 42.8, 42.8]
  }
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)
  const data = generateTrendData()

  trendChart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: (value: number) => value + ' kg CO₂/m²' },
    legend: { data: ['Actual Intensity', 'Target Intensity', 'Baseline'], bottom: 0 },
    grid: { left: '3%', right: '4%', top: '10%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', data: data.labels },
    yAxis: { type: 'value', name: 'Carbon Intensity (kg CO₂/m²)' },
    series: [
      { name: 'Actual Intensity', type: 'line', data: data.actual, smooth: true, symbol: 'circle', lineStyle: { width: 3, color: '#409eff' }, areaStyle: { opacity: 0.1, color: '#409eff' } },
      { name: 'Target Intensity', type: 'line', data: data.target, smooth: true, symbol: 'diamond', lineStyle: { width: 2, color: '#67c23a', type: 'dashed' } },
      { name: 'Baseline', type: 'line', data: data.baseline, smooth: true, symbol: 'none', lineStyle: { width: 2, color: '#909399', type: 'dotted' } }
    ]
  })
}

const initBuildingChart = () => {
  if (!buildingChartRef.value) return
  if (buildingChart) buildingChart.dispose()

  buildingChart = echarts.init(buildingChartRef.value)

  const buildings = ['Building A', 'Building B', 'Data Center']
  const current = [6.2, 6.8, 61.5]
  const target = [7.0, 7.2, 58.0]
  const industryAvgBuilding = [7.5, 8.0, 65.0]

  buildingChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: (value: number) => value + ' kg CO₂/m²' },
    legend: { data: ['Current', 'Target', 'Industry Avg'], bottom: 0 },
    grid: { left: '10%', right: '5%', top: '5%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: buildings },
    yAxis: { type: 'value', name: 'Carbon Intensity (kg CO₂/m²)' },
    series: [
      { name: 'Current', type: 'bar', data: current, itemStyle: { borderRadius: [4, 4, 0, 0], color: (params: any) => params.data <= target[params.dataIndex] ? '#67c23a' : '#f56c6c' }, label: { show: true, position: 'top', formatter: '{c}' } },
      { name: 'Target', type: 'line', data: target, symbol: 'none', lineStyle: { width: 2, color: '#e6a23c', type: 'dashed' } },
      { name: 'Industry Avg', type: 'line', data: industryAvgBuilding, symbol: 'none', lineStyle: { width: 2, color: '#909399', type: 'dotted' } }
    ]
  })
}

const initScopeChart = () => {
  if (!scopeChartRef.value) return
  if (scopeChart) scopeChart.dispose()

  scopeChart = echarts.init(scopeChartRef.value)

  scopeChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} tCO₂ ({d}%)' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      type: 'pie', radius: '55%', center: ['50%', '50%'],
      data: [
        { name: 'Scope 1 (Direct)', value: 1850, itemStyle: { color: '#f56c6c' } },
        { name: 'Scope 2 (Energy)', value: 3200, itemStyle: { color: '#e6a23c' } },
        { name: 'Scope 3 (Indirect)', value: 1200, itemStyle: { color: '#909399' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 }
    }]
  })
}

// ==================== Actions ====================
const refreshData = async () => {
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  ElMessage.success('Carbon intensity data refreshed')
  initTrendChart()
  initBuildingChart()
  initScopeChart()
  tableLoading.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting carbon intensity report...')
}

const fetchTrendData = () => {
  initTrendChart()
}

const handleDateChange = () => {
  currentPage.value = 1
}

const viewAllInitiatives = () => {
  ElMessage.info('Viewing all decarbonization initiatives')
}

const viewBenchmarkDetails = () => {
  ElMessage.info('Viewing benchmark details')
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Window Resize Handler ====================
const handleResize = () => {
  trendChart?.resize()
  buildingChart?.resize()
  scopeChart?.resize()
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
        initScopeChart()
      }, 100)
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  buildingChart?.dispose()
  scopeChart?.dispose()
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
.carbon-intensity-page {
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

.kpi-card.current-ci .kpi-icon { background: #e8f4ff; color: #409eff; }
.kpi-card.baseline .kpi-icon { background: #f0f0f0; color: #909399; }
.kpi-card.target .kpi-icon { background: #e8f8f0; color: #67c23a; }
.kpi-card.reduction .kpi-icon { background: #fff7e8; color: #e6a23c; }

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

/* Initiatives Section */
.initiatives-section {
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

.initiatives-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.initiative-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px;
  background: #fafafa;
  border-radius: 14px;
  transition: all 0.2s;
}

.initiative-item:hover {
  background: #f5f7fa;
  transform: translateX(4px);
}

.initiative-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.initiative-icon.completed {
  background: #e8f8f0;
  color: #67c23a;
}

.initiative-icon.in-progress {
  background: #e8f4ff;
  color: #409eff;
}

.initiative-icon.planned {
  background: #fff7e8;
  color: #e6a23c;
}

.initiative-content {
  flex: 1;
}

.initiative-title {
  font-weight: 600;
  color: #1f2f3d;
  margin-bottom: 6px;
}

.initiative-description {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.initiative-metrics {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #909399;
}

.initiative-metrics .el-icon {
  vertical-align: middle;
  margin-right: 4px;
}

.initiative-progress {
  flex-shrink: 0;
}

/* Benchmark Section */
.benchmark-section {
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
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
  font-size: 13px;
  font-weight: 500;
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