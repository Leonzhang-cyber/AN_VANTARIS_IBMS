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
        <div class="loading-tip">Aggregated Data</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="aggregated-data-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Data Platform</el-breadcrumb-item>
            <el-breadcrumb-item>Historian</el-breadcrumb-item>
            <el-breadcrumb-item>Aggregated Data</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Aggregated Data</h1>
        <p class="description">Roll-up summaries of telemetry data for trend analysis and reporting</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Data
        </el-button>
        <el-button @click="handleRefreshAggregation">
          <el-icon><Refresh /></el-icon>
          Refresh Aggregates
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6" v-for="stat in statsCards" :key="stat.title">
        <el-card class="stat-card" shadow="hover" @click="handleCardClick(stat)">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">{{ stat.title }}</div>
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
                <el-icon><component :is="stat.trend > 0 ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
                {{ Math.abs(stat.trend) }}%
                <span class="trend-label">vs last period</span>
              </div>
            </div>
            <div class="stat-icon" :style="{ background: stat.bgColor }">
              <el-icon :size="28" color="white">
                <component :is="stat.icon" />
              </el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Aggregation Controls -->
    <el-card class="controls-card" shadow="hover">
      <div class="controls-container">
        <div class="control-group">
          <span class="control-label">Aggregation Level:</span>
          <el-radio-group v-model="aggregationLevel" @change="handleAggregationChange">
            <el-radio-button value="hour">Hourly</el-radio-button>
            <el-radio-button value="day">Daily</el-radio-button>
            <el-radio-button value="week">Weekly</el-radio-button>
            <el-radio-button value="month">Monthly</el-radio-button>
            <el-radio-button value="quarter">Quarterly</el-radio-button>
            <el-radio-button value="year">Yearly</el-radio-button>
          </el-radio-group>
        </div>
        <div class="control-group">
          <span class="control-label">Aggregation Function:</span>
          <el-radio-group v-model="aggFunction" @change="handleAggregationChange">
            <el-radio-button value="avg">Average</el-radio-button>
            <el-radio-button value="sum">Sum</el-radio-button>
            <el-radio-button value="min">Minimum</el-radio-button>
            <el-radio-button value="max">Maximum</el-radio-button>
            <el-radio-button value="count">Count</el-radio-button>
          </el-radio-group>
        </div>
      </div>
    </el-card>

    <!-- Aggregated Trend Chart -->
    <el-card class="chart-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Aggregated Trend</span>
          <div class="chart-controls">
            <el-select v-model="selectedMetric" size="small" style="width: 150px" @change="initTrendChart">
              <el-option label="Energy Consumption" value="energy" />
              <el-option label="Temperature" value="temperature" />
              <el-option label="Power Demand" value="power" />
              <el-option label="Water Usage" value="water" />
            </el-select>
            <el-select v-model="selectedDevice" size="small" style="width: 160px" @change="initTrendChart">
              <el-option label="All Devices" value="all" />
              <el-option label="Chiller-01" value="chiller_01" />
              <el-option label="AHU-03" value="ahu_03" />
              <el-option label="Cooling Tower-02" value="ct_02" />
            </el-select>
          </div>
        </div>
      </template>
      <div ref="trendChartRef" class="chart-container"></div>
    </el-card>

    <!-- Comparison Chart -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Period-over-Period Comparison</span>
            </div>
          </template>
          <div ref="comparisonChartRef" class="comparison-chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Top Contributors</span>
            </div>
          </template>
          <div ref="contributorsChartRef" class="horizontal-bar-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Filters -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-container">
        <div class="filter-row">
          <el-select v-model="filters.deviceGroup" placeholder="Device Group" clearable style="width: 150px" @change="handleSearch">
            <el-option label="HVAC" value="hvac" />
            <el-option label="Lighting" value="lighting" />
            <el-option label="Power" value="power" />
            <el-option label="Water" value="water" />
          </el-select>
          <el-select v-model="filters.building" placeholder="Building" clearable style="width: 140px" @change="handleSearch">
            <el-option label="Building A" value="A" />
            <el-option label="Building B" value="B" />
            <el-option label="Building C" value="C" />
          </el-select>
          <el-date-picker
              v-model="filters.dateRange"
              type="daterange"
              range-separator="to"
              start-placeholder="Start Date"
              end-placeholder="End Date"
              style="width: 280px"
              @change="handleSearch"
          />
          <el-button type="primary" @click="handleSearch">Apply</el-button>
          <el-button @click="handleResetFilters">Reset</el-button>
        </div>
      </div>
    </el-card>

    <!-- Aggregated Data Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Aggregated Data ({{ aggregationLevel }}ly {{ getFunctionName() }})</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchData" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedData" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="period" label="Period"  />
        <el-table-column prop="startDate" label="Start Date"  />
        <el-table-column prop="endDate" label="End Date"  />
        <el-table-column prop="energyConsumption" label="Energy (kWh)"  align="right">
          <template #default="{ row }">
            {{ row.energyConsumption.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="avgTemperature" label="Avg Temp (°C)"  align="right">
          <template #default="{ row }">
            {{ row.avgTemperature.toFixed(1) }}
          </template>
        </el-table-column>
        <el-table-column prop="peakPower" label="Peak Power (kW)"  align="right">
          <template #default="{ row }">
            {{ row.peakPower.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="waterUsage" label="Water (m³)"  align="right">
          <template #default="{ row }">
            {{ row.waterUsage.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="recordCount" label="Records"  align="center" />
        <el-table-column label="Actions"  fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">Details</el-button>
            <el-button link type="info" size="small" @click="drillDown(row)">Drill Down</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[15, 30, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredData.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Drill Down Dialog -->
    <el-dialog v-model="drillDialogVisible" :title="`Drill Down - ${drillTarget?.period}`" width="900px" destroy-on-close>
      <div class="drill-container">
        <div class="drill-controls">
          <el-select v-model="drillMetric" placeholder="Select Metric" style="width: 150px" @change="initDrillChart">
            <el-option label="Energy" value="energy" />
            <el-option label="Temperature" value="temperature" />
            <el-option label="Power" value="power" />
          </el-select>
          <el-select v-model="drillDevice" placeholder="Select Device" clearable style="width: 160px" @change="initDrillChart">
            <el-option label="All Devices" value="all" />
            <el-option label="Chiller-01" value="chiller_01" />
            <el-option label="AHU-03" value="ahu_03" />
            <el-option label="CT-02" value="ct_02" />
          </el-select>
        </div>
        <div ref="drillChartRef" class="drill-chart-container"></div>
        <div class="drill-stats">
          <el-descriptions :column="4" border size="small">
            <el-descriptions-item label="Total">{{ drillStats.total }}</el-descriptions-item>
            <el-descriptions-item label="Average">{{ drillStats.avg }}</el-descriptions-item>
            <el-descriptions-item label="Maximum">{{ drillStats.max }}</el-descriptions-item>
            <el-descriptions-item label="Minimum">{{ drillStats.min }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      <template #footer>
        <el-button @click="drillDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="exportDrillData">Export</el-button>
      </template>
    </el-dialog>

    <!-- Details Dialog -->
    <el-dialog v-model="detailsDialogVisible" :title="`Aggregation Details - ${detailsTarget?.period}`" width="600px" destroy-on-close>
      <div class="details-container" v-if="detailsTarget">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Period">{{ detailsTarget.period }}</el-descriptions-item>
          <el-descriptions-item label="Date Range">{{ detailsTarget.startDate }} - {{ detailsTarget.endDate }}</el-descriptions-item>
          <el-descriptions-item label="Aggregation Level">{{ aggregationLevel }}ly</el-descriptions-item>
          <el-descriptions-item label="Function">{{ getFunctionName() }}</el-descriptions-item>
          <el-descriptions-item label="Energy Consumption">{{ detailsTarget.energyConsumption.toLocaleString() }} kWh</el-descriptions-item>
          <el-descriptions-item label="Avg Temperature">{{ detailsTarget.avgTemperature.toFixed(1) }} °C</el-descriptions-item>
          <el-descriptions-item label="Peak Power">{{ detailsTarget.peakPower.toLocaleString() }} kW</el-descriptions-item>
          <el-descriptions-item label="Water Usage">{{ detailsTarget.waterUsage.toLocaleString() }} m³</el-descriptions-item>
          <el-descriptions-item label="Source Records">{{ detailsTarget.recordCount.toLocaleString() }}</el-descriptions-item>
          <el-descriptions-item label="Data Completeness">{{ detailsTarget.completeness }}%</el-descriptions-item>
          <el-descriptions-item label="Aggregation Time" :span="2">{{ detailsTarget.aggregationTime }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="detailsDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="drillDown(detailsTarget)">Drill Down</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  DataAnalysis
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading aggregated data...',
  'Computing statistics...',
  'Almost ready...'
]

// ==================== Chart References ====================
const trendChartRef = ref<HTMLElement>()
const comparisonChartRef = ref<HTMLElement>()
const contributorsChartRef = ref<HTMLElement>()
const drillChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null
let comparisonChart: echarts.ECharts | null = null
let contributorsChart: echarts.ECharts | null = null
let drillChart: echarts.ECharts | null = null

// ==================== State ====================
const tableLoading = ref(false)
const detailsDialogVisible = ref(false)
const drillDialogVisible = ref(false)
const detailsTarget = ref<any>(null)
const drillTarget = ref<any>(null)
const currentPage = ref(1)
const pageSize = ref(15)
const aggregationLevel = ref('day')
const aggFunction = ref('avg')
const selectedMetric = ref('energy')
const selectedDevice = ref('all')
const drillMetric = ref('energy')
const drillDevice = ref('all')

const filters = reactive({
  deviceGroup: '',
  building: '',
  dateRange: null as [Date, Date] | null
})

const drillStats = reactive({
  total: '--',
  avg: '--',
  max: '--',
  min: '--'
})

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'Total Energy', value: '2.45M kWh', trend: -8, icon: 'TrendCharts', bgColor: '#409eff', key: 'energy' },
  { title: 'Avg Temperature', value: '22.4°C', trend: 1.2, icon: 'DataAnalysis', bgColor: '#67c23a', key: 'temp' },
  { title: 'Peak Power', value: '1,850 kW', trend: -5, icon: 'Clock', bgColor: '#e6a23c', key: 'power' },
  { title: 'Water Usage', value: '125K m³', trend: -12, icon: 'Document', bgColor: '#f56c6c', key: 'water' }
])

// Generate aggregated data - Monthly data
const monthlyData = [
  { period: 'Jan 2024', startDate: '2024-01-01', endDate: '2024-01-31', energyConsumption: 245000, avgTemperature: 18.5, peakPower: 1650, waterUsage: 12500, recordCount: 744, completeness: 99.2, aggregationTime: '2024-02-01 01:00:00' },
  { period: 'Feb 2024', startDate: '2024-02-01', endDate: '2024-02-29', energyConsumption: 238000, avgTemperature: 19.2, peakPower: 1620, waterUsage: 11800, recordCount: 696, completeness: 98.8, aggregationTime: '2024-03-01 01:00:00' },
  { period: 'Mar 2024', startDate: '2024-03-01', endDate: '2024-03-31', energyConsumption: 252000, avgTemperature: 20.5, peakPower: 1680, waterUsage: 13200, recordCount: 744, completeness: 99.5, aggregationTime: '2024-04-01 01:00:00' },
  { period: 'Apr 2024', startDate: '2024-04-01', endDate: '2024-04-30', energyConsumption: 268000, avgTemperature: 22.5, peakPower: 1720, waterUsage: 14500, recordCount: 720, completeness: 99.1, aggregationTime: '2024-05-01 01:00:00' },
  { period: 'May 2024', startDate: '2024-05-01', endDate: '2024-05-31', energyConsumption: 285000, avgTemperature: 24.5, peakPower: 1780, waterUsage: 15800, recordCount: 744, completeness: 99.3, aggregationTime: '2024-06-01 01:00:00' },
  { period: 'Jun 2024', startDate: '2024-06-01', endDate: '2024-06-30', energyConsumption: 312000, avgTemperature: 26.5, peakPower: 1850, waterUsage: 17200, recordCount: 720, completeness: 98.9, aggregationTime: '2024-07-01 01:00:00' },
  { period: 'Jul 2024', startDate: '2024-07-01', endDate: '2024-07-31', energyConsumption: 335000, avgTemperature: 28.5, peakPower: 1920, waterUsage: 18500, recordCount: 744, completeness: 99.4, aggregationTime: '2024-08-01 01:00:00' },
  { period: 'Aug 2024', startDate: '2024-08-01', endDate: '2024-08-31', energyConsumption: 328000, avgTemperature: 28.0, peakPower: 1900, waterUsage: 18200, recordCount: 744, completeness: 99.0, aggregationTime: '2024-09-01 01:00:00' }
]

// Daily data for drill down
const dailyDataMap = new Map()

// Generate daily data for each month
monthlyData.forEach(month => {
  const daysInMonth = parseInt(month.endDate.split('-')[2])
  const dailyRecords = []
  for (let i = 1; i <= daysInMonth; i++) {
    const date = `${month.startDate.substring(0, 8)}${String(i).padStart(2, '0')}`
    dailyRecords.push({
      period: date,
      startDate: date,
      endDate: date,
      energyConsumption: Math.floor(Math.random() * 15000) + 5000,
      avgTemperature: month.avgTemperature + (Math.random() - 0.5) * 5,
      peakPower: Math.floor(Math.random() * 500) + 1000,
      waterUsage: Math.floor(Math.random() * 800) + 200,
      recordCount: 24,
      completeness: Math.random() * 5 + 95,
      aggregationTime: new Date().toISOString()
    })
  }
  dailyDataMap.set(month.period, dailyRecords)
})

const aggregatedData = ref(monthlyData)

// ==================== Computed ====================
const filteredData = computed(() => {
  let filtered = [...aggregatedData.value]

  if (filters.deviceGroup) {
    // Filter logic for device group
    filtered = filtered.filter(() => true)
  }

  if (filters.building) {
    filtered = filtered.filter(() => true)
  }

  if (filters.dateRange && filters.dateRange[0] && filters.dateRange[1]) {
    filtered = filtered.filter(d => {
      const date = new Date(d.startDate)
      return date >= filters.dateRange![0] && date <= filters.dateRange![1]
    })
  }

  return filtered
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getFunctionName = () => {
  const map: Record<string, string> = {
    'avg': 'Average',
    'sum': 'Sum',
    'min': 'Minimum',
    'max': 'Maximum',
    'count': 'Count'
  }
  return map[aggFunction.value] || 'Average'
}

// ==================== Chart Initializations ====================
const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)

  const periods = aggregatedData.value.slice(-30).map(d => d.period)
  const values = aggregatedData.value.slice(-30).map(d => {
    if (selectedMetric.value === 'energy') return d.energyConsumption / 1000
    if (selectedMetric.value === 'temperature') return d.avgTemperature
    if (selectedMetric.value === 'power') return d.peakPower
    return d.waterUsage
  })

  const yAxisName = selectedMetric.value === 'energy' ? 'Energy (kWh)' :
      selectedMetric.value === 'temperature' ? 'Temperature (°C)' :
          selectedMetric.value === 'power' ? 'Power (kW)' : 'Water (m³)'

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: periods,
      axisLabel: { rotate: 45, interval: Math.floor(periods.length / 10) }
    },
    yAxis: { type: 'value', name: yAxisName },
    series: [{
      type: 'line',
      data: values,
      smooth: true,
      lineStyle: { width: 3, color: '#409eff' },
      areaStyle: { opacity: 0.1, color: '#409eff' },
      symbolSize: 8
    }]
  }

  trendChart.setOption(option)
  window.addEventListener('resize', () => trendChart?.resize())
}

const initComparisonChart = () => {
  if (!comparisonChartRef.value) return
  if (comparisonChart) comparisonChart.dispose()

  comparisonChart = echarts.init(comparisonChartRef.value)

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug']
  const currentYear = [245, 238, 252, 268, 285, 312, 335, 328]
  const lastYear = [230, 225, 240, 255, 270, 295, 315, 310]

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['2024', '2023'], bottom: 0 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Energy (kWh)' },
    series: [
      { name: '2024', type: 'bar', data: currentYear, itemStyle: { borderRadius: [4, 4, 0, 0], color: '#409eff' } },
      { name: '2023', type: 'bar', data: lastYear, itemStyle: { borderRadius: [4, 4, 0, 0], color: '#c0c4cc' } }
    ]
  }

  comparisonChart.setOption(option)
  window.addEventListener('resize', () => comparisonChart?.resize())
}

const initContributorsChart = () => {
  if (!contributorsChartRef.value) return
  if (contributorsChart) contributorsChart.dispose()

  contributorsChart = echarts.init(contributorsChartRef.value)

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '15%', containLabel: true },
    xAxis: { type: 'value', name: 'Energy (kWh)' },
    yAxis: { type: 'category', data: ['Chiller-01', 'AHU-03', 'CT-02', 'Pump-04', 'Lighting'], axisLabel: { fontSize: 11 } },
    series: [{
      type: 'bar',
      data: [125000, 89000, 67000, 45000, 32000],
      itemStyle: { borderRadius: [0, 4, 4, 0], color: '#67c23a' },
      label: { show: true, position: 'right', formatter: '{c} kWh' }
    }]
  }

  contributorsChart.setOption(option)
  window.addEventListener('resize', () => contributorsChart?.resize())
}

const initDrillChart = () => {
  if (!drillChartRef.value || !drillTarget.value) return
  if (drillChart) drillChart.dispose()

  drillChart = echarts.init(drillChartRef.value)

  const dailyData = dailyDataMap.get(drillTarget.value.period) || []
  const values = dailyData.map(d => {
    if (drillMetric.value === 'energy') return d.energyConsumption
    if (drillMetric.value === 'temperature') return d.avgTemperature
    return d.peakPower
  })
  const labels = dailyData.map(d => d.period.split('-')[2])

  const yAxisName = drillMetric.value === 'energy' ? 'Energy (kWh)' :
      drillMetric.value === 'temperature' ? 'Temperature (°C)' : 'Power (kW)'

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: labels, axisLabel: { rotate: 45, interval: 5 } },
    yAxis: { type: 'value', name: yAxisName },
    series: [{
      type: 'line',
      data: values,
      smooth: true,
      lineStyle: { width: 2, color: '#f56c6c' },
      areaStyle: { opacity: 0.1 },
      symbolSize: 6
    }]
  }

  drillChart.setOption(option)
  window.addEventListener('resize', () => drillChart?.resize())

  // Update stats
  if (values.length > 0) {
    drillStats.total = values.reduce((a, b) => a + b, 0).toFixed(0)
    drillStats.avg = (values.reduce((a, b) => a + b, 0) / values.length).toFixed(1)
    drillStats.max = Math.max(...values).toFixed(1)
    drillStats.min = Math.min(...values).toFixed(1)
  }
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleAggregationChange = () => {
  initTrendChart()
  ElMessage.success(`Switched to ${aggregationLevel}ly ${getFunctionName()}`)
}

const handleSearch = () => {
  currentPage.value = 1
  initTrendChart()
}

const handleResetFilters = () => {
  filters.deviceGroup = ''
  filters.building = ''
  filters.dateRange = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
  initTrendChart()
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredData.value.length} aggregated records...`)
}

const handleRefreshAggregation = () => {
  ElMessage.info('Refreshing aggregated data...')
  setTimeout(() => {
    ElMessage.success('Aggregates refreshed')
    initTrendChart()
    initComparisonChart()
    initContributorsChart()
  }, 2000)
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const fetchData = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Data refreshed')
  }, 500)
}

const viewDetails = (row: any) => {
  detailsTarget.value = row
  detailsDialogVisible.value = true
}

const drillDown = (row: any) => {
  drillTarget.value = row
  drillDialogVisible.value = true
  nextTick(() => {
    initDrillChart()
  })
}

const exportDrillData = () => {
  ElMessage.success('Drill down data exported')
}

const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {}

// ==================== Loading Simulation ====================
const initCharts = async () => {
  await nextTick()
  setTimeout(() => {
    initTrendChart()
    initComparisonChart()
    initContributorsChart()
  }, 100)
}

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
      initCharts()
      fetchData()
    }, 400)
  }, 2000)
})
</script>

<style scoped lang="scss">
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

/* ==================== Main Page Styles ==================== */
.aggregated-data-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;

  .breadcrumb {
    margin-bottom: 8px;
  }

  h1 {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 8px 0;
  }

  .description {
    color: #909399;
    font-size: 14px;
    margin: 0;
  }

  .header-actions {
    display: flex;
    gap: 12px;
  }
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
  }

  .stat-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .stat-info {
    flex: 1;
  }

  .stat-title {
    font-size: 14px;
    color: #909399;
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }

  .stat-trend {
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 4px;

    &.up { color: #67c23a; }
    &.down { color: #f56c6c; }

    .trend-label {
      color: #909399;
      margin-left: 4px;
    }
  }

  .stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.controls-card {
  margin-bottom: 20px;

  .controls-container {
    display: flex;
    flex-wrap: wrap;
    gap: 24px;
    align-items: center;

    .control-group {
      display: flex;
      align-items: center;
      gap: 12px;

      .control-label {
        font-weight: 600;
        color: #303133;
      }
    }
  }
}

.chart-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;

    .chart-controls {
      display: flex;
      gap: 12px;
      align-items: center;
    }
  }
}

.chart-container {
  width: 100%;
  height: 350px;
}

.chart-row {
  margin-bottom: 20px;
}

.comparison-chart-container, .horizontal-bar-container {
  width: 100%;
  height: 320px;
}

.filter-card {
  margin-bottom: 20px;

  .filter-container {
    .filter-row {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
    }
  }
}

.table-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .table-actions {
    display: flex;
    gap: 8px;
    align-items: center;
  }
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.drill-container {
  .drill-controls {
    display: flex;
    gap: 16px;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid #ebeef5;
  }

  .drill-chart-container {
    width: 100%;
    height: 400px;
  }

  .drill-stats {
    margin-top: 16px;
  }
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
}
</style>