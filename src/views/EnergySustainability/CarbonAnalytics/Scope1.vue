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
          <span class="loading-title">Scope 1 Emissions</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Direct GHG Emissions Tracking & Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="scope1-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><OfficeBuilding /></el-icon>
          Scope 1 Emissions
        </h1>
        <div class="page-subtitle">Direct greenhouse gas emissions from owned or controlled sources</div>
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
          <el-icon><OfficeBuilding /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalEmissions }}<span class="stat-unit">tCO₂e</span></div>
          <div class="stat-label">Total Scope 1 Emissions</div>
          <div class="stat-trend" :class="stats.emissionsTrend > 0 ? 'up' : 'down'">
            {{ stats.emissionsTrend > 0 ? '↑' : '↓' }} {{ Math.abs(stats.emissionsTrend) }}% vs last year
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><House /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.stationaryFuel }}<span class="stat-unit">tCO₂e</span></div>
          <div class="stat-label">Stationary Combustion</div>
          <div class="stat-trend">{{ stats.stationaryPercent }}% of total</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Van /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.mobileFuel }}<span class="stat-unit">tCO₂e</span></div>
          <div class="stat-label">Mobile Combustion</div>
          <div class="stat-trend">{{ stats.mobilePercent }}% of total</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.fugitive }}<span class="stat-unit">tCO₂e</span></div>
          <div class="stat-label">Fugitive Emissions</div>
          <div class="stat-trend">{{ stats.fugitivePercent }}% of total</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Emissions Intensity</div>
        <div class="metric-value">{{ metrics.intensity }}<span class="metric-unit">tCO₂e/m²</span></div>
        <div class="metric-trend" :class="metrics.intensityTrend < 0 ? 'positive' : 'negative'">
          {{ metrics.intensityTrend < 0 ? '↓' : '↑' }} {{ Math.abs(metrics.intensityTrend) }}% vs last year
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Natural Gas</div>
        <div class="metric-value">{{ metrics.naturalGas }}<span class="metric-unit">tCO₂e</span></div>
        <div class="metric-sub">{{ metrics.naturalGasUsage }} MWh consumption</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Diesel/Fuel Oil</div>
        <div class="metric-value">{{ metrics.dieselEmissions }}<span class="metric-unit">tCO₂e</span></div>
        <div class="metric-sub">{{ metrics.dieselUsage }} L consumed</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Refrigerant Leakage</div>
        <div class="metric-value">{{ metrics.refrigerantEmissions }}<span class="metric-unit">tCO₂e</span></div>
        <div class="metric-sub">{{ metrics.refrigerantLeak }} kg R-134a equivalent</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card large">
        <div class="chart-header">
          <span class="chart-title">Scope 1 Emissions Trend</span>
          <span class="chart-subtitle">Monthly emissions by source</span>
        </div>
        <div class="chart-container" ref="trendChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Emissions by Source</span>
          <span class="chart-subtitle">Breakdown of Scope 1</span>
        </div>
        <div class="chart-container" ref="sourceChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Monthly Fuel Consumption</span>
          <span class="chart-subtitle">Natural gas vs Diesel</span>
        </div>
        <div class="chart-container" ref="fuelChartEl"></div>
      </div>
    </div>

    <!-- Third Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Emissions by Facility</span>
          <span class="chart-subtitle">Top emitting locations</span>
        </div>
        <div class="chart-container" ref="facilityChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Year-over-Year Comparison</span>
          <span class="chart-subtitle">Monthly YoY change</span>
        </div>
        <div class="chart-container" ref="yoyChartEl"></div>
      </div>
    </div>

    <!-- Fourth Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Emissions vs Target</span>
          <span class="chart-subtitle">Progress toward reduction goals</span>
        </div>
        <div class="chart-container" ref="targetChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Breakdown by Emission Type</span>
          <span class="chart-subtitle">CO₂, CH₄, N₂O, HFCs</span>
        </div>
        <div class="chart-container" ref="gasTypeChartEl"></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            size="default"
            style="width: 260px"
        />
        <el-select v-model="facilityFilter" placeholder="Facility" clearable style="width: 150px">
          <el-option v-for="f in facilities" :key="f" :label="f" :value="f" />
        </el-select>
        <el-select v-model="sourceFilter" placeholder="Emission Source" clearable style="width: 150px">
          <el-option label="Stationary Combustion" value="stationary" />
          <el-option label="Mobile Combustion" value="mobile" />
          <el-option label="Fugitive Emissions" value="fugitive" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Emissions Data Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Monthly Emissions Records</span>
        <el-button size="small" @click="viewAllRecords">View All →</el-button>
      </div>
      <el-table :data="paginatedRecords" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="month" label="Month"  />
        <el-table-column prop="facility" label="Facility"  />
        <el-table-column prop="source" label="Emission Source"  />
        <el-table-column prop="fuelType" label="Fuel Type"  />
        <el-table-column prop="consumption" label="Consumption" >
          <template #default="{ row }">
            {{ row.consumption.toLocaleString() }} {{ row.unit }}
          </template>
        </el-table-column>
        <el-table-column prop="emissions" label="CO₂e (t)" >
          <template #default="{ row }">
            {{ row.emissions.toFixed(1) }}
          </template>
        </el-table-column>
        <el-table-column prop="co2" label="CO₂ (t)" >
          <template #default="{ row }">
            {{ row.co2.toFixed(1) }}
          </template>
        </el-table-column>
        <el-table-column prop="ch4" label="CH₄ (kg)" >
          <template #default="{ row }">
            {{ row.ch4.toFixed(1) }}
          </template>
        </el-table-column>
        <el-table-column prop="n2o" label="N₂O (kg)" >
          <template #default="{ row }">
            {{ row.n2o.toFixed(1) }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewRecordDetail(row)">Details</el-button>
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

    <!-- Record Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Emissions Record - ${selectedRecord?.month} ${selectedRecord?.facility}`" width="700px">
      <div v-if="selectedRecord" class="record-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Month">{{ selectedRecord.month }}</el-descriptions-item>
          <el-descriptions-item label="Facility">{{ selectedRecord.facility }}</el-descriptions-item>
          <el-descriptions-item label="Emission Source">{{ selectedRecord.source }}</el-descriptions-item>
          <el-descriptions-item label="Fuel Type">{{ selectedRecord.fuelType }}</el-descriptions-item>
          <el-descriptions-item label="Consumption">{{ selectedRecord.consumption.toLocaleString() }} {{ selectedRecord.unit }}</el-descriptions-item>
          <el-descriptions-item label="Total CO₂e">{{ selectedRecord.emissions.toFixed(1) }} tCO₂e</el-descriptions-item>
          <el-descriptions-item label="CO₂">{{ selectedRecord.co2.toFixed(1) }} t</el-descriptions-item>
          <el-descriptions-item label="CH₄">{{ selectedRecord.ch4.toFixed(1) }} kg</el-descriptions-item>
          <el-descriptions-item label="N₂O">{{ selectedRecord.n2o.toFixed(1) }} kg</el-descriptions-item>
          <el-descriptions-item label="GWP Used">{{ selectedRecord.gwp }}</el-descriptions-item>
          <el-descriptions-item label="Calculation Method" :span="2">{{ selectedRecord.method }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <div class="section-title">Verification Status</div>
          <el-alert
              :title="selectedRecord.verified ? 'Verified' : 'Pending Verification'"
              :type="selectedRecord.verified ? 'success' : 'warning'"
              :description="selectedRecord.verificationNotes"
              :closable="false"
              show-icon
          />
        </div>

        <div class="detail-section">
          <div class="section-title">Reduction Opportunities</div>
          <ul class="opportunity-list">
            <li v-for="(opp, idx) in selectedRecord.opportunities" :key="idx">
              {{ opp }}
            </li>
          </ul>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="verifyRecord(selectedRecord)">Verify</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  OfficeBuilding, House, Van, Warning, Download, Refresh,
  RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading Scope 1 emissions data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading emissions data...',
  'Calculating carbon equivalents...',
  'Analyzing emission sources...',
  'Generating reports...',
  'Almost ready...'
]

// ==================== Types ====================
interface EmissionRecord {
  id: number
  month: string
  facility: string
  source: string
  fuelType: string
  consumption: number
  unit: string
  emissions: number
  co2: number
  ch4: number
  n2o: number
  gwp: string
  method: string
  verified: boolean
  verificationNotes: string
  opportunities: string[]
}

// ==================== Mock Data ====================
const facilities = ['Data Center A', 'Data Center B', 'Generator Plant', 'Office Building', 'Warehouse']

const generateEmissionData = (): EmissionRecord[] => {
  const records: EmissionRecord[] = []
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const sources = [
    { source: 'Stationary Combustion', fuelType: 'Natural Gas', unit: 'MMBtu' },
    { source: 'Stationary Combustion', fuelType: 'Diesel', unit: 'L' },
    { source: 'Mobile Combustion', fuelType: 'Gasoline', unit: 'L' },
    { source: 'Mobile Combustion', fuelType: 'Diesel', unit: 'L' },
    { source: 'Fugitive Emissions', fuelType: 'Refrigerant R-134a', unit: 'kg' }
  ]

  let id = 1

  for (const facility of facilities) {
    for (const month of months) {
      for (const src of sources) {
        let consumption = 0
        let emissions = 0
        let co2 = 0
        let ch4 = 0
        let n2o = 0

        if (src.fuelType === 'Natural Gas') {
          consumption = Math.round(1000 + Math.random() * 2000)
          emissions = consumption * 0.053
          co2 = consumption * 0.053
          ch4 = consumption * 0.001
          n2o = consumption * 0.0001
        } else if (src.fuelType === 'Diesel' && src.source === 'Stationary Combustion') {
          consumption = Math.round(5000 + Math.random() * 10000)
          emissions = consumption * 0.00268
          co2 = consumption * 0.00268
          ch4 = consumption * 0.00001
          n2o = consumption * 0.00001
        } else if (src.fuelType === 'Gasoline') {
          consumption = Math.round(2000 + Math.random() * 5000)
          emissions = consumption * 0.00231
          co2 = consumption * 0.00231
          ch4 = consumption * 0.000008
          n2o = consumption * 0.000008
        } else if (src.fuelType === 'Diesel' && src.source === 'Mobile Combustion') {
          consumption = Math.round(3000 + Math.random() * 8000)
          emissions = consumption * 0.00268
          co2 = consumption * 0.00268
          ch4 = consumption * 0.000005
          n2o = consumption * 0.00001
        } else {
          // Refrigerant
          consumption = parseFloat((10 + Math.random() * 40).toFixed(1))
          emissions = consumption * 1430 // R-134a GWP
          co2 = 0
          ch4 = 0
          n2o = 0
        }

        emissions = parseFloat(emissions.toFixed(1))
        co2 = parseFloat(co2.toFixed(1))
        ch4 = parseFloat(ch4.toFixed(1))
        n2o = parseFloat(n2o.toFixed(1))

        const verified = Math.random() > 0.3

        records.push({
          id: id++,
          month: month,
          facility: facility,
          source: src.source,
          fuelType: src.fuelType,
          consumption: consumption,
          unit: src.unit,
          emissions: emissions,
          co2: co2,
          ch4: ch4,
          n2o: n2o,
          gwp: src.fuelType === 'Refrigerant R-134a' ? 'AR5' : 'IPCC 2021',
          method: 'Activity-based calculation using emission factors',
          verified: verified,
          verificationNotes: verified ? 'Verified by third-party auditor' : 'Awaiting verification',
          opportunities: [
            'Consider energy efficiency upgrades',
            'Optimize equipment scheduling',
            'Explore renewable alternatives'
          ]
        })
      }
    }
  }

  return records
}

const emissionRecords = ref<EmissionRecord[]>(generateEmissionData())

// ==================== State ====================
const dateRange = ref<Date[] | null>(null)
const facilityFilter = ref('')
const sourceFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const selectedRecord = ref<EmissionRecord | null>(null)

// Chart refs
let trendChart: echarts.ECharts | null = null
let sourceChart: echarts.ECharts | null = null
let fuelChart: echarts.ECharts | null = null
let facilityChart: echarts.ECharts | null = null
let yoyChart: echarts.ECharts | null = null
let targetChart: echarts.ECharts | null = null
let gasTypeChart: echarts.ECharts | null = null

const trendChartEl = ref<HTMLElement | null>(null)
const sourceChartEl = ref<HTMLElement | null>(null)
const fuelChartEl = ref<HTMLElement | null>(null)
const facilityChartEl = ref<HTMLElement | null>(null)
const yoyChartEl = ref<HTMLElement | null>(null)
const targetChartEl = ref<HTMLElement | null>(null)
const gasTypeChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  const currentYearRecords = emissionRecords.value.slice(0, 60)
  const totalEmissions = currentYearRecords.reduce((sum, r) => sum + r.emissions, 0)
  const stationaryEmissions = currentYearRecords.filter(r => r.source === 'Stationary Combustion').reduce((sum, r) => sum + r.emissions, 0)
  const mobileEmissions = currentYearRecords.filter(r => r.source === 'Mobile Combustion').reduce((sum, r) => sum + r.emissions, 0)
  const fugitiveEmissions = currentYearRecords.filter(r => r.source === 'Fugitive Emissions').reduce((sum, r) => sum + r.emissions, 0)

  return {
    totalEmissions: Math.round(totalEmissions),
    emissionsTrend: -5.2,
    stationaryFuel: Math.round(stationaryEmissions),
    stationaryPercent: Math.round((stationaryEmissions / totalEmissions) * 100),
    mobileFuel: Math.round(mobileEmissions),
    mobilePercent: Math.round((mobileEmissions / totalEmissions) * 100),
    fugitive: Math.round(fugitiveEmissions),
    fugitivePercent: Math.round((fugitiveEmissions / totalEmissions) * 100)
  }
})

const metrics = computed(() => {
  const intensity = (stats.value.totalEmissions / 5000).toFixed(1)
  const naturalGasRecords = emissionRecords.value.filter(r => r.fuelType === 'Natural Gas')
  const naturalGasEmissions = naturalGasRecords.reduce((sum, r) => sum + r.emissions, 0)
  const naturalGasConsumption = naturalGasRecords.reduce((sum, r) => sum + r.consumption, 0) / 1000
  const dieselRecords = emissionRecords.value.filter(r => r.fuelType === 'Diesel')
  const dieselEmissions = dieselRecords.reduce((sum, r) => sum + r.emissions, 0)
  const dieselConsumption = dieselRecords.reduce((sum, r) => sum + r.consumption, 0)
  const refrigerantRecords = emissionRecords.value.filter(r => r.fuelType === 'Refrigerant R-134a')
  const refrigerantEmissions = refrigerantRecords.reduce((sum, r) => sum + r.emissions, 0)
  const refrigerantLeak = refrigerantRecords.reduce((sum, r) => sum + r.consumption, 0)

  return {
    intensity: parseFloat(intensity),
    intensityTrend: -3.2,
    naturalGas: Math.round(naturalGasEmissions),
    naturalGasUsage: Math.round(naturalGasConsumption),
    dieselEmissions: Math.round(dieselEmissions),
    dieselUsage: Math.round(dieselConsumption),
    refrigerantEmissions: Math.round(refrigerantEmissions),
    refrigerantLeak: Math.round(refrigerantLeak)
  }
})

const filteredRecords = computed(() => {
  let filtered = [...emissionRecords.value]

  if (facilityFilter.value) {
    filtered = filtered.filter(r => r.facility === facilityFilter.value)
  }

  if (sourceFilter.value === 'stationary') {
    filtered = filtered.filter(r => r.source === 'Stationary Combustion')
  } else if (sourceFilter.value === 'mobile') {
    filtered = filtered.filter(r => r.source === 'Mobile Combustion')
  } else if (sourceFilter.value === 'fugitive') {
    filtered = filtered.filter(r => r.source === 'Fugitive Emissions')
  }

  if (dateRange.value && dateRange.value.length === 2) {
    // Filter logic would go here
  }

  return filtered
})

const totalRecords = computed(() => filteredRecords.value.length)

const paginatedRecords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRecords.value.slice(start, end)
})

// ==================== Helper Functions ====================
const resetFilters = () => {
  facilityFilter.value = ''
  sourceFilter.value = ''
  dateRange.value = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

// ==================== Chart Functions ====================
const initTrendChart = () => {
  if (!trendChartEl.value) return
  if (trendChart) {
    trendChart.dispose()
    trendChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const stationaryData = [85, 82, 78, 75, 72, 70, 68, 72, 75, 78, 80, 82]
  const mobileData = [25, 24, 28, 30, 32, 35, 38, 36, 34, 32, 28, 26]
  const fugitiveData = [12, 11, 10, 9, 8, 7, 6, 7, 8, 9, 10, 11]

  trendChart = echarts.init(trendChartEl.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Stationary', 'Mobile', 'Fugitive'], bottom: 0 },
    grid: { top: 40, left: 60, right: 30, bottom: 40 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Emissions (tCO₂e)' },
    series: [
      { name: 'Stationary', type: 'line', data: stationaryData, lineStyle: { color: '#f59e0b', width: 2 }, symbol: 'circle', areaStyle: { opacity: 0.1 } },
      { name: 'Mobile', type: 'line', data: mobileData, lineStyle: { color: '#3b82f6', width: 2 }, symbol: 'circle', areaStyle: { opacity: 0.1 } },
      { name: 'Fugitive', type: 'line', data: fugitiveData, lineStyle: { color: '#ef4444', width: 2 }, symbol: 'circle', areaStyle: { opacity: 0.1 } }
    ]
  })
}

const initSourceChart = () => {
  if (!sourceChartEl.value) return
  if (sourceChart) {
    sourceChart.dispose()
    sourceChart = null
  }

  sourceChart = echarts.init(sourceChartEl.value)
  sourceChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} tCO₂e)' },
    legend: { orient: 'vertical', left: 'left', data: ['Stationary Combustion', 'Mobile Combustion', 'Fugitive Emissions'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: stats.value.stationaryFuel, name: 'Stationary Combustion', itemStyle: { color: '#f59e0b' } },
        { value: stats.value.mobileFuel, name: 'Mobile Combustion', itemStyle: { color: '#3b82f6' } },
        { value: stats.value.fugitive, name: 'Fugitive Emissions', itemStyle: { color: '#ef4444' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const initFuelChart = () => {
  if (!fuelChartEl.value) return
  if (fuelChart) {
    fuelChart.dispose()
    fuelChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const naturalGasData = [85, 82, 78, 75, 72, 70, 68, 72, 75, 78, 80, 82]
  const dieselData = [45, 44, 48, 50, 52, 55, 58, 56, 54, 52, 48, 46]

  fuelChart = echarts.init(fuelChartEl.value)
  fuelChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Natural Gas', 'Diesel'], bottom: 0 },
    grid: { top: 30, left: 60, right: 30, bottom: 40 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Consumption (tCO₂e)' },
    series: [
      { name: 'Natural Gas', type: 'bar', data: naturalGasData, itemStyle: { color: '#f59e0b', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top' } },
      { name: 'Diesel', type: 'line', data: dieselData, lineStyle: { color: '#3b82f6', width: 2 }, symbol: 'circle' }
    ]
  })
}

const initFacilityChart = () => {
  if (!facilityChartEl.value) return
  if (facilityChart) {
    facilityChart.dispose()
    facilityChart = null
  }

  const facilityEmissions = new Map<string, number>()
  emissionRecords.value.forEach(r => {
    facilityEmissions.set(r.facility, (facilityEmissions.get(r.facility) || 0) + r.emissions)
  })

  const data = Array.from(facilityEmissions.entries()).map(([name, value]) => ({ name, value: Math.round(value) }))

  facilityChart = echarts.init(facilityChartEl.value)
  facilityChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: data.map(d => d.name), axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'Emissions (tCO₂e)' },
    series: [{
      type: 'bar',
      data: data.map(d => d.value),
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#3b82f6' },
      label: { show: true, position: 'top', formatter: '{c} t' }
    }]
  })
}

const initYoyChart = () => {
  if (!yoyChartEl.value) return
  if (yoyChart) {
    yoyChart.dispose()
    yoyChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const thisYear = [122, 117, 116, 114, 112, 112, 112, 115, 117, 119, 118, 119]
  const lastYear = [135, 130, 128, 125, 122, 120, 118, 120, 122, 125, 126, 128]

  yoyChart = echarts.init(yoyChartEl.value)
  yoyChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['This Year', 'Last Year'], bottom: 0 },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Emissions (tCO₂e)' },
    series: [
      { name: 'This Year', type: 'line', data: thisYear, lineStyle: { color: '#22c55e', width: 3 }, symbol: 'circle', areaStyle: { opacity: 0.1 } },
      { name: 'Last Year', type: 'line', data: lastYear, lineStyle: { color: '#94a3b8', width: 2, type: 'dashed' }, symbol: 'diamond' }
    ]
  })
}

const initTargetChart = () => {
  if (!targetChartEl.value) return
  if (targetChart) {
    targetChart.dispose()
    targetChart = null
  }

  const years = ['2024', '2025', '2026', '2027', '2028', '2029', '2030']
  const actual = [1450, 1380, null, null, null, null, null]
  const target = [1450, 1380, 1310, 1240, 1170, 1100, 1030]

  targetChart = echarts.init(targetChartEl.value)
  targetChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Actual', 'Target'], bottom: 0 },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: years },
    yAxis: { type: 'value', name: 'Emissions (tCO₂e)' },
    series: [
      { name: 'Actual', type: 'bar', data: actual, itemStyle: { color: '#3b82f6', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top' } },
      { name: 'Target', type: 'line', data: target, lineStyle: { color: '#ef4444', width: 2, type: 'dashed' }, symbol: 'diamond' }
    ]
  })
}

const initGasTypeChart = () => {
  if (!gasTypeChartEl.value) return
  if (gasTypeChart) {
    gasTypeChart.dispose()
    gasTypeChart = null
  }

  gasTypeChart = echarts.init(gasTypeChartEl.value)
  gasTypeChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} tCO₂e ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: ['CO₂', 'CH₄', 'N₂O', 'HFCs'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: 1350, name: 'CO₂', itemStyle: { color: '#94a3b8' } },
        { value: 45, name: 'CH₄', itemStyle: { color: '#f59e0b' } },
        { value: 25, name: 'N₂O', itemStyle: { color: '#22c55e' } },
        { value: 30, name: 'HFCs', itemStyle: { color: '#ef4444' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initTrendChart()
    initSourceChart()
    initFuelChart()
    initFacilityChart()
    initYoyChart()
    initTargetChart()
    initGasTypeChart()
  })
}

// ==================== Actions ====================
const viewRecordDetail = (record: EmissionRecord) => {
  selectedRecord.value = record
  detailDialogVisible.value = true
}

const viewAllRecords = () => {
  ElMessage.info('Viewing all records')
}

const verifyRecord = (record: EmissionRecord | null) => {
  if (record) {
    ElMessage.success(`Record for ${record.month} ${record.facility} verified`)
  }
}

const exportData = () => {
  ElMessage.success('Exporting Scope 1 emissions data...')
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
    const charts = [trendChart, sourceChart, fuelChart, facilityChart, yoyChart, targetChart, gasTypeChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([facilityFilter, sourceFilter, dateRange], () => {
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
  const charts = [trendChart, sourceChart, fuelChart, facilityChart, yoyChart, targetChart, gasTypeChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.scope1-page {
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

.stat-trend.up { color: #ef4444; }
.stat-trend.down { color: #22c55e; }

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
  height: 300px;
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

/* Record Detail */
.record-detail {
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

.opportunity-list {
  margin: 0;
  padding-left: 20px;
}

.opportunity-list li {
  margin: 8px 0;
  color: #64748b;
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
  max-height: 600px;
  overflow-y: auto;
}
:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}
</style>