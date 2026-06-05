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
          <span class="loading-title">Scope 2 Emissions</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Indirect GHG Emissions from Purchased Energy</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="scope2-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Lightning /></el-icon>
          Scope 2 Emissions
        </h1>
        <div class="page-subtitle">Indirect greenhouse gas emissions from purchased electricity, steam, heating, and cooling</div>
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
          <el-icon><Lightning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalEmissions }}<span class="stat-unit">tCO₂e</span></div>
          <div class="stat-label">Total Scope 2 Emissions</div>
          <div class="stat-trend" :class="stats.emissionsTrend > 0 ? 'up' : 'down'">
            {{ stats.emissionsTrend > 0 ? '↑' : '↓' }} {{ Math.abs(stats.emissionsTrend) }}% vs last year
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.electricityEmissions }}<span class="stat-unit">tCO₂e</span></div>
          <div class="stat-label">Electricity</div>
          <div class="stat-trend">{{ stats.electricityPercent }}% of total</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><HotWater /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.steamEmissions }}<span class="stat-unit">tCO₂e</span></div>
          <div class="stat-label">Steam / Heating</div>
          <div class="stat-trend">{{ stats.steamPercent }}% of total</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><Iphone /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.coolingEmissions }}<span class="stat-unit">tCO₂e</span></div>
          <div class="stat-label">Chilled Water</div>
          <div class="stat-trend">{{ stats.coolingPercent }}% of total</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Market-Based Emissions</div>
        <div class="metric-value">{{ metrics.marketBased }}<span class="metric-unit">tCO₂e</span></div>
        <div class="metric-trend positive">With renewable credits</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Location-Based Emissions</div>
        <div class="metric-value">{{ metrics.locationBased }}<span class="metric-unit">tCO₂e</span></div>
        <div class="metric-trend negative">Grid average</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Renewable Energy Ratio</div>
        <div class="metric-value">{{ metrics.renewableRatio }}<span class="metric-unit">%</span></div>
        <el-progress :percentage="metrics.renewableRatio" :stroke-width="8" :color="metrics.renewableRatio > 50 ? '#22c55e' : (metrics.renewableRatio > 30 ? '#f59e0b' : '#ef4444')" />
      </div>
      <div class="metric-card">
        <div class="metric-title">Grid Emission Factor</div>
        <div class="metric-value">{{ metrics.gridFactor }}<span class="metric-unit">kgCO₂/kWh</span></div>
        <div class="metric-trend positive">↓ {{ metrics.factorReduction }}% vs last year</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card large">
        <div class="chart-header">
          <span class="chart-title">Scope 2 Emissions Trend</span>
          <span class="chart-subtitle">Monthly emissions by source</span>
        </div>
        <div class="chart-container" ref="trendChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Emissions by Energy Type</span>
          <span class="chart-subtitle">Breakdown of Scope 2</span>
        </div>
        <div class="chart-container" ref="sourceChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Monthly Electricity Consumption</span>
          <span class="chart-subtitle">kWh usage trend</span>
        </div>
        <div class="chart-container" ref="consumptionChartEl"></div>
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
          <span class="chart-title">Market vs Location-Based</span>
          <span class="chart-subtitle">Emission comparison</span>
        </div>
        <div class="chart-container" ref="comparisonChartEl"></div>
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
          <span class="chart-title">Renewable Energy Mix</span>
          <span class="chart-subtitle">RE procurement sources</span>
        </div>
        <div class="chart-container" ref="renewableChartEl"></div>
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
        <el-select v-model="energyTypeFilter" placeholder="Energy Type" clearable style="width: 150px">
          <el-option label="Electricity" value="electricity" />
          <el-option label="Steam/Heating" value="steam" />
          <el-option label="Chilled Water" value="cooling" />
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
        <span class="table-title">Monthly Energy & Emissions Records</span>
        <el-button size="small" @click="viewAllRecords">View All →</el-button>
      </div>
      <el-table :data="paginatedRecords" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="month" label="Month" />
        <el-table-column prop="facility" label="Facility"  />
        <el-table-column prop="energyType" label="Energy Type"  />
        <el-table-column prop="consumption" label="Consumption" >
          <template #default="{ row }">
            {{ row.consumption.toLocaleString() }} {{ row.unit }}
          </template>
        </el-table-column>
        <el-table-column prop="emissionsMarket" label="Emissions (Market)" >
          <template #default="{ row }">
            {{ row.emissionsMarket.toFixed(1) }} tCO₂e
          </template>
        </el-table-column>
        <el-table-column prop="emissionsLocation" label="Emissions (Location)" >
          <template #default="{ row }">
            {{ row.emissionsLocation.toFixed(1) }} tCO₂e
          </template>
        </el-table-column>
        <el-table-column prop="renewablePercentage" label="Renewable %" >
          <template #default="{ row }">
            <el-progress :percentage="row.renewablePercentage" :stroke-width="6" :color="row.renewablePercentage > 50 ? '#22c55e' : (row.renewablePercentage > 25 ? '#f59e0b' : '#ef4444')" />
          </template>
        </el-table-column>
        <el-table-column prop="verified" label="Status">
          <template #default="{ row }">
            <el-tag :type="row.verified ? 'success' : 'warning'" size="small">
              {{ row.verified ? 'Verified' : 'Pending' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" fixed="right">
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
    <el-dialog v-model="detailDialogVisible" :title="`Energy Record - ${selectedRecord?.month} ${selectedRecord?.facility}`" width="750px">
      <div v-if="selectedRecord" class="record-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Month">{{ selectedRecord.month }}</el-descriptions-item>
          <el-descriptions-item label="Facility">{{ selectedRecord.facility }}</el-descriptions-item>
          <el-descriptions-item label="Energy Type">{{ selectedRecord.energyType }}</el-descriptions-item>
          <el-descriptions-item label="Consumption">{{ selectedRecord.consumption.toLocaleString() }} {{ selectedRecord.unit }}</el-descriptions-item>
          <el-descriptions-item label="Market-Based Emissions">{{ selectedRecord.emissionsMarket.toFixed(1) }} tCO₂e</el-descriptions-item>
          <el-descriptions-item label="Location-Based Emissions">{{ selectedRecord.emissionsLocation.toFixed(1) }} tCO₂e</el-descriptions-item>
          <el-descriptions-item label="Grid Emission Factor">{{ selectedRecord.gridFactor }} kgCO₂/kWh</el-descriptions-item>
          <el-descriptions-item label="Renewable Energy">{{ selectedRecord.renewablePercentage }}%</el-descriptions-item>
          <el-descriptions-item label="RECs/Offsets">{{ selectedRecord.renewableCertificates }} MWh</el-descriptions-item>
          <el-descriptions-item label="Calculation Method" :span="2">{{ selectedRecord.calculationMethod }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <div class="section-title">Monthly Energy Mix</div>
          <div class="trend-chart" ref="mixChartEl"></div>
        </div>

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
  Lightning, DataLine, HotWater, Iphone, Download, Refresh,
  RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading Scope 2 emissions data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading energy data...',
  'Calculating emissions...',
  'Analyzing renewable energy...',
  'Preparing reports...',
  'Almost ready...'
]

// ==================== Types ====================
interface EnergyRecord {
  id: number
  month: string
  facility: string
  energyType: string
  consumption: number
  unit: string
  emissionsMarket: number
  emissionsLocation: number
  gridFactor: number
  renewablePercentage: number
  renewableCertificates: number
  calculationMethod: string
  verified: boolean
  verificationNotes: string
  opportunities: string[]
  energyMix: { name: string; value: number }[]
}

// ==================== Mock Data ====================
const facilities = ['Data Center A', 'Data Center B', 'Office Building', 'Warehouse', 'Research Lab']

const generateEnergyData = (): EnergyRecord[] => {
  const records: EnergyRecord[] = []
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const energyTypes = [
    { type: 'Electricity', unit: 'kWh', baseEmission: 0.35 },
    { type: 'Steam/Heating', unit: 'MMBtu', baseEmission: 0.06 },
    { type: 'Chilled Water', unit: 'ton-hr', baseEmission: 0.05 }
  ]

  let id = 1

  for (const facility of facilities) {
    for (const month of months) {
      for (const energy of energyTypes) {
        let consumption = 0
        if (energy.type === 'Electricity') {
          consumption = Math.round(50000 + Math.random() * 150000)
        } else if (energy.type === 'Steam/Heating') {
          consumption = Math.round(5000 + Math.random() * 15000)
        } else {
          consumption = Math.round(3000 + Math.random() * 10000)
        }

        const emissionsLocation = consumption * energy.baseEmission / 1000
        const renewablePercentage = facility === 'Data Center A' ? 65 : (facility === 'Data Center B' ? 45 : 25 + Math.random() * 20)
        const emissionsMarket = emissionsLocation * (1 - renewablePercentage / 100)
        const renewableCertificates = Math.round(consumption * (renewablePercentage / 100) / 1000)
        const gridFactor = parseFloat((energy.baseEmission * (0.9 + Math.random() * 0.2)).toFixed(3))

        const verified = Math.random() > 0.2

        const energyMix = [
          { name: 'Renewable', value: renewablePercentage },
          { name: 'Nuclear', value: 20 + Math.random() * 10 },
          { name: 'Natural Gas', value: 15 + Math.random() * 15 },
          { name: 'Coal', value: 5 + Math.random() * 10 }
        ]

        records.push({
          id: id++,
          month: month,
          facility: facility,
          energyType: energy.type,
          consumption: consumption,
          unit: energy.unit,
          emissionsMarket: parseFloat(emissionsMarket.toFixed(1)),
          emissionsLocation: parseFloat(emissionsLocation.toFixed(1)),
          gridFactor: gridFactor,
          renewablePercentage: Math.round(renewablePercentage),
          renewableCertificates: renewableCertificates,
          calculationMethod: 'Activity-based using grid emission factors',
          verified: verified,
          verificationNotes: verified ? 'Verified by utility data' : 'Awaiting invoice verification',
          opportunities: [
            'Increase renewable energy procurement',
            'Implement energy efficiency measures',
            'Explore on-site solar generation'
          ],
          energyMix: energyMix
        })
      }
    }
  }

  return records
}

const energyRecords = ref<EnergyRecord[]>(generateEnergyData())

// ==================== State ====================
const dateRange = ref<Date[] | null>(null)
const facilityFilter = ref('')
const energyTypeFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const selectedRecord = ref<EnergyRecord | null>(null)

// Chart refs
let trendChart: echarts.ECharts | null = null
let sourceChart: echarts.ECharts | null = null
let consumptionChart: echarts.ECharts | null = null
let facilityChart: echarts.ECharts | null = null
let comparisonChart: echarts.ECharts | null = null
let targetChart: echarts.ECharts | null = null
let renewableChart: echarts.ECharts | null = null
let mixChart: echarts.ECharts | null = null

const trendChartEl = ref<HTMLElement | null>(null)
const sourceChartEl = ref<HTMLElement | null>(null)
const consumptionChartEl = ref<HTMLElement | null>(null)
const facilityChartEl = ref<HTMLElement | null>(null)
const comparisonChartEl = ref<HTMLElement | null>(null)
const targetChartEl = ref<HTMLElement | null>(null)
const renewableChartEl = ref<HTMLElement | null>(null)
const mixChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  const currentYearRecords = energyRecords.value.slice(0, 36)
  const totalEmissions = currentYearRecords.reduce((sum, r) => sum + r.emissionsMarket, 0)
  const electricityEmissions = currentYearRecords.filter(r => r.energyType === 'Electricity').reduce((sum, r) => sum + r.emissionsMarket, 0)
  const steamEmissions = currentYearRecords.filter(r => r.energyType === 'Steam/Heating').reduce((sum, r) => sum + r.emissionsMarket, 0)
  const coolingEmissions = currentYearRecords.filter(r => r.energyType === 'Chilled Water').reduce((sum, r) => sum + r.emissionsMarket, 0)

  return {
    totalEmissions: Math.round(totalEmissions),
    emissionsTrend: -6.5,
    electricityEmissions: Math.round(electricityEmissions),
    electricityPercent: Math.round((electricityEmissions / totalEmissions) * 100),
    steamEmissions: Math.round(steamEmissions),
    steamPercent: Math.round((steamEmissions / totalEmissions) * 100),
    coolingEmissions: Math.round(coolingEmissions),
    coolingPercent: Math.round((coolingEmissions / totalEmissions) * 100)
  }
})

const metrics = computed(() => {
  const currentYearRecords = energyRecords.value.slice(0, 36)
  const marketTotal = currentYearRecords.reduce((sum, r) => sum + r.emissionsMarket, 0)
  const locationTotal = currentYearRecords.reduce((sum, r) => sum + r.emissionsLocation, 0)
  const avgRenewable = currentYearRecords.reduce((sum, r) => sum + r.renewablePercentage, 0) / currentYearRecords.length
  const avgGridFactor = currentYearRecords.reduce((sum, r) => sum + r.gridFactor, 0) / currentYearRecords.length

  return {
    marketBased: Math.round(marketTotal),
    locationBased: Math.round(locationTotal),
    renewableRatio: Math.round(avgRenewable),
    gridFactor: avgGridFactor.toFixed(3),
    factorReduction: 8.2
  }
})

const filteredRecords = computed(() => {
  let filtered = [...energyRecords.value]

  if (facilityFilter.value) {
    filtered = filtered.filter(r => r.facility === facilityFilter.value)
  }

  if (energyTypeFilter.value === 'electricity') {
    filtered = filtered.filter(r => r.energyType === 'Electricity')
  } else if (energyTypeFilter.value === 'steam') {
    filtered = filtered.filter(r => r.energyType === 'Steam/Heating')
  } else if (energyTypeFilter.value === 'cooling') {
    filtered = filtered.filter(r => r.energyType === 'Chilled Water')
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
  energyTypeFilter.value = ''
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
  const electricityData = [85, 82, 88, 92, 95, 98, 105, 102, 95, 88, 82, 78]
  const steamData = [12, 11, 10, 9, 8, 7, 6, 7, 8, 9, 10, 11]
  const coolingData = [8, 9, 10, 12, 14, 16, 18, 17, 15, 12, 10, 8]

  trendChart = echarts.init(trendChartEl.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Electricity', 'Steam/Heating', 'Chilled Water'], bottom: 0 },
    grid: { top: 40, left: 60, right: 30, bottom: 40 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Emissions (tCO₂e)' },
    series: [
      { name: 'Electricity', type: 'line', data: electricityData, lineStyle: { color: '#f59e0b', width: 2 }, symbol: 'circle', areaStyle: { opacity: 0.1 } },
      { name: 'Steam/Heating', type: 'line', data: steamData, lineStyle: { color: '#3b82f6', width: 2 }, symbol: 'circle', areaStyle: { opacity: 0.1 } },
      { name: 'Chilled Water', type: 'line', data: coolingData, lineStyle: { color: '#22c55e', width: 2 }, symbol: 'circle', areaStyle: { opacity: 0.1 } }
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
    legend: { orient: 'vertical', left: 'left', data: ['Electricity', 'Steam/Heating', 'Chilled Water'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: stats.value.electricityEmissions, name: 'Electricity', itemStyle: { color: '#f59e0b' } },
        { value: stats.value.steamEmissions, name: 'Steam/Heating', itemStyle: { color: '#3b82f6' } },
        { value: stats.value.coolingEmissions, name: 'Chilled Water', itemStyle: { color: '#22c55e' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const initConsumptionChart = () => {
  if (!consumptionChartEl.value) return
  if (consumptionChart) {
    consumptionChart.dispose()
    consumptionChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const consumption = [125, 130, 140, 145, 150, 155, 160, 158, 150, 142, 135, 128]

  consumptionChart = echarts.init(consumptionChartEl.value)
  consumptionChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Electricity (MWh)' },
    series: [{
      type: 'bar',
      data: consumption,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#f59e0b' },
      label: { show: true, position: 'top', formatter: '{c} MWh' }
    }]
  })
}

const initFacilityChart = () => {
  if (!facilityChartEl.value) return
  if (facilityChart) {
    facilityChart.dispose()
    facilityChart = null
  }

  const facilityEmissions = new Map<string, number>()
  energyRecords.value.forEach(r => {
    facilityEmissions.set(r.facility, (facilityEmissions.get(r.facility) || 0) + r.emissionsMarket)
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

const initComparisonChart = () => {
  if (!comparisonChartEl.value) return
  if (comparisonChart) {
    comparisonChart.dispose()
    comparisonChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const marketData = [85, 82, 88, 92, 95, 98, 105, 102, 95, 88, 82, 78]
  const locationData = [95, 93, 98, 103, 106, 110, 118, 115, 106, 98, 92, 88]

  comparisonChart = echarts.init(comparisonChartEl.value)
  comparisonChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Market-Based', 'Location-Based'], bottom: 0 },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Emissions (tCO₂e)' },
    series: [
      { name: 'Market-Based', type: 'line', data: marketData, lineStyle: { color: '#22c55e', width: 3 }, symbol: 'circle', areaStyle: { opacity: 0.1 } },
      { name: 'Location-Based', type: 'line', data: locationData, lineStyle: { color: '#94a3b8', width: 2, type: 'dashed' }, symbol: 'diamond' }
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
  const actual = [1450, 1350, null, null, null, null, null]
  const target = [1450, 1350, 1250, 1150, 1050, 950, 850]

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

const initRenewableChart = () => {
  if (!renewableChartEl.value) return
  if (renewableChart) {
    renewableChart.dispose()
    renewableChart = null
  }

  renewableChart = echarts.init(renewableChartEl.value)
  renewableChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
    legend: { orient: 'vertical', left: 'left', data: ['Solar', 'Wind', 'Hydro', 'RECs Purchased'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: 35, name: 'Solar', itemStyle: { color: '#f59e0b' } },
        { value: 30, name: 'Wind', itemStyle: { color: '#3b82f6' } },
        { value: 15, name: 'Hydro', itemStyle: { color: '#22c55e' } },
        { value: 20, name: 'RECs Purchased', itemStyle: { color: '#8b5cf6' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const initMixChart = () => {
  if (!mixChartEl.value || !selectedRecord.value) return
  if (mixChart) {
    mixChart.dispose()
    mixChart = null
  }

  const data = selectedRecord.value.energyMix

  mixChart = echarts.init(mixChartEl.value)
  mixChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
    legend: { orient: 'vertical', left: 'left', data: data.map(d => d.name) },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: data,
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initTrendChart()
    initSourceChart()
    initConsumptionChart()
    initFacilityChart()
    initComparisonChart()
    initTargetChart()
    initRenewableChart()
  })
}

// ==================== Actions ====================
const viewRecordDetail = (record: EnergyRecord) => {
  selectedRecord.value = record
  detailDialogVisible.value = true
  nextTick(() => initMixChart())
}

const viewAllRecords = () => {
  ElMessage.info('Viewing all records')
}

const verifyRecord = (record: EnergyRecord | null) => {
  if (record) {
    ElMessage.success(`Record for ${record.month} ${record.facility} verified`)
  }
}

const exportData = () => {
  ElMessage.success('Exporting Scope 2 emissions data...')
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
    const charts = [trendChart, sourceChart, consumptionChart, facilityChart, comparisonChart, targetChart, renewableChart, mixChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([facilityFilter, energyTypeFilter, dateRange], () => {
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
  const charts = [trendChart, sourceChart, consumptionChart, facilityChart, comparisonChart, targetChart, renewableChart, mixChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.scope2-page {
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

.trend-chart {
  height: 280px;
  width: 100%;
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