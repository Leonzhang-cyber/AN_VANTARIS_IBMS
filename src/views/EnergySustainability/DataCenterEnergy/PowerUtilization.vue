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
          <span class="loading-title">Power Utilization</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Data Center Power Distribution & Utilization Analytics</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="power-utilization-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Lightning /></el-icon>
          Power Utilization
        </h1>
        <div class="page-subtitle">Monitor power distribution, capacity planning, and utilization efficiency</div>
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
          <div class="stat-value">{{ stats.totalPower }}<span class="stat-unit">MW</span></div>
          <div class="stat-label">Total Facility Power</div>
          <div class="stat-trend" :class="stats.powerTrend > 0 ? 'up' : 'down'">
            {{ stats.powerTrend > 0 ? '↑' : '↓' }} {{ Math.abs(stats.powerTrend) }}% vs last month
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.itLoad }}<span class="stat-unit">MW</span></div>
          <div class="stat-label">IT Load</div>
          <div class="stat-trend">{{ stats.itPercent }}% of total</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.utilization }}<span class="stat-unit">%</span></div>
          <div class="stat-label">Overall Utilization</div>
          <div class="stat-trend" :class="stats.utilTrend > 0 ? 'up' : 'down'">
            {{ stats.utilTrend > 0 ? '↑' : '↓' }} {{ Math.abs(stats.utilTrend) }}% vs last month
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">${{ stats.powerCost }}<span class="stat-unit">M</span></div>
          <div class="stat-label">Monthly Power Cost</div>
          <div class="stat-trend down">↓ {{ stats.costReduction }}% YoY</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Power Capacity</div>
        <div class="metric-value">{{ metrics.capacity }}<span class="stat-unit">MW</span></div>
        <div class="metric-sub">Available: {{ metrics.availableCapacity }} MW</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Peak Demand</div>
        <div class="metric-value">{{ metrics.peakDemand }}<span class="stat-unit">MW</span></div>
        <div class="metric-trend positive">{{ metrics.peakTime }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Power Factor</div>
        <div class="metric-value">{{ metrics.powerFactor }}<span class="stat-unit">%</span></div>
        <el-progress :percentage="metrics.powerFactor" :stroke-width="8" :color="metrics.powerFactor > 95 ? '#22c55e' : (metrics.powerFactor > 90 ? '#f59e0b' : '#ef4444')" />
      </div>
      <div class="metric-card">
        <div class="metric-title">Reserve Capacity</div>
        <div class="metric-value">{{ metrics.reserveCapacity }}<span class="stat-unit">MW</span></div>
        <div class="metric-sub">{{ metrics.reservePercent }}% of total</div>
      </div>
    </div>

    <!-- Charts Row 1 -->
    <div class="charts-row">
      <div class="chart-card large">
        <div class="chart-header">
          <span class="chart-title">Power Consumption Trend</span>
          <span class="chart-subtitle">Daily power usage</span>
          <el-select v-model="trendPeriod" size="small" style="width: 100px" @change="updateConsumptionTrend">
            <el-option label="7 Days" value="7" />
            <el-option label="30 Days" value="30" />
            <el-option label="90 Days" value="90" />
          </el-select>
        </div>
        <div class="chart-container" ref="consumptionTrendChartEl"></div>
      </div>
    </div>

    <!-- Charts Row 2 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Power Distribution by Zone</span>
          <span class="chart-subtitle">Load breakdown</span>
        </div>
        <div class="chart-container" ref="distributionChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Hourly Load Profile</span>
          <span class="chart-subtitle">Daily variation pattern</span>
        </div>
        <div class="chart-container" ref="hourlyProfileChartEl"></div>
      </div>
    </div>

    <!-- Charts Row 3 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">PDU Utilization</span>
          <span class="chart-subtitle">Per rack distribution</span>
        </div>
        <div class="chart-container" ref="pduUtilizationChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Power Factor Trend</span>
          <span class="chart-subtitle">Monthly performance</span>
        </div>
        <div class="chart-container" ref="powerFactorChartEl"></div>
      </div>
    </div>

    <!-- Charts Row 4 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">UPS Load Distribution</span>
          <span class="chart-subtitle">Per UPS unit</span>
        </div>
        <div class="chart-container" ref="upsLoadChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Capacity Planning</span>
          <span class="chart-subtitle">Current vs forecast</span>
        </div>
        <div class="chart-container" ref="capacityChartEl"></div>
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
        <el-select v-model="zoneFilter" placeholder="Zone" clearable style="width: 150px">
          <el-option v-for="z in zones" :key="z" :label="z" :value="z" />
        </el-select>
        <el-select v-model="pduFilter" placeholder="PDU" clearable style="width: 150px">
          <el-option v-for="p in pdus" :key="p" :label="p" :value="p" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- PDU Data Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">PDU Load Summary</span>
        <el-button size="small" @click="viewAllData">View All →</el-button>
      </div>
      <el-table :data="paginatedData" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="pduId" label="PDU ID" width="120" />
        <el-table-column prop="zone" label="Zone" width="150" />
        <el-table-column prop="rackCount" label="Racks" width="80" />
        <el-table-column prop="currentLoad" label="Current Load (kW)" width="150">
          <template #default="{ row }">
            <span :class="getLoadClass(row.currentLoad, row.capacity)">{{ row.currentLoad }} / {{ row.capacity }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="utilization" label="Utilization" width="140">
          <template #default="{ row }">
            <el-progress :percentage="row.utilization" :stroke-width="8" :color="getUtilizationColor(row.utilization)" />
          </template>
        </el-table-column>
        <el-table-column prop="peakLoad" label="Peak Load (kW)" width="130">
          <template #default="{ row }">
            {{ row.peakLoad }}
          </template>
        </el-table-column>
        <el-table-column prop="powerFactor" label="Power Factor" width="110">
          <template #default="{ row }">
            <span :class="getPFPositive(row.powerFactor)">{{ row.powerFactor }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="efficiency" label="Efficiency" width="100">
          <template #default="{ row }">
            {{ row.efficiency }}%
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Normal' ? 'success' : (row.status === 'Warning' ? 'warning' : 'danger')" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewPduDetail(row)">Details</el-button>
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

    <!-- PDU Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedPdu?.pduId" width="900px">
      <div v-if="selectedPdu" class="pdu-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="PDU ID">{{ selectedPdu.pduId }}</el-descriptions-item>
          <el-descriptions-item label="Zone">{{ selectedPdu.zone }}</el-descriptions-item>
          <el-descriptions-item label="Racks Served">{{ selectedPdu.rackCount }}</el-descriptions-item>
          <el-descriptions-item label="Capacity">{{ selectedPdu.capacity }} kW</el-descriptions-item>
          <el-descriptions-item label="Current Load">{{ selectedPdu.currentLoad }} kW</el-descriptions-item>
          <el-descriptions-item label="Utilization">{{ selectedPdu.utilization }}%</el-descriptions-item>
          <el-descriptions-item label="Peak Load">{{ selectedPdu.peakLoad }} kW</el-descriptions-item>
          <el-descriptions-item label="Power Factor">{{ selectedPdu.powerFactor }}%</el-descriptions-item>
          <el-descriptions-item label="Efficiency">{{ selectedPdu.efficiency }}%</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="selectedPdu.status === 'Normal' ? 'success' : (selectedPdu.status === 'Warning' ? 'warning' : 'danger')" size="small">
              {{ selectedPdu.status }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <div class="section-title">Load Distribution by Rack</div>
          <div class="trend-chart" ref="rackLoadChartEl"></div>
        </div>

        <div class="detail-section">
          <div class="section-title">Hourly Load Profile</div>
          <div class="trend-chart" ref="pduHourlyChartEl"></div>
        </div>

        <div class="detail-section">
          <div class="section-title">Recommendations</div>
          <el-alert
              :title="selectedPdu.recommendation.title"
              :type="selectedPdu.recommendation.type"
              :description="selectedPdu.recommendation.description"
              :closable="false"
              show-icon
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="exportPduReport(selectedPdu)">Export Report</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Lightning, DataLine, Timer, Money, Download, Refresh,
  RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading power utilization data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading PDU data...',
  'Calculating utilization metrics...',
  'Analyzing load distribution...',
  'Preparing capacity insights...',
  'Almost ready...'
]

// ==================== Types ====================
interface PduUnit {
  id: number
  pduId: string
  zone: string
  rackCount: number
  currentLoad: number
  capacity: number
  utilization: number
  peakLoad: number
  powerFactor: number
  efficiency: number
  status: string
  recommendation: {
    title: string
    type: 'success' | 'warning' | 'info' | 'error'
    description: string
  }
}

// ==================== Mock Data ====================
const zones = ['Zone A', 'Zone B', 'Zone C', 'Zone D']
const pdus = ['PDU-A1', 'PDU-A2', 'PDU-B1', 'PDU-B2', 'PDU-C1', 'PDU-C2', 'PDU-D1', 'PDU-D2']

const generatePduData = (): PduUnit[] => {
  const pduData: PduUnit[] = [
    { id: 1, pduId: 'PDU-A1', zone: 'Zone A', rackCount: 24, currentLoad: 185, capacity: 300, utilization: 62, peakLoad: 210, powerFactor: 96, efficiency: 94, status: 'Normal',
      recommendation: { title: 'Load Balancing', type: 'info', description: 'Consider redistributing load to optimize capacity utilization.' } },
    { id: 2, pduId: 'PDU-A2', zone: 'Zone A', rackCount: 24, currentLoad: 225, capacity: 300, utilization: 75, peakLoad: 245, powerFactor: 94, efficiency: 92, status: 'Normal',
      recommendation: { title: 'Monitor Peak Loads', type: 'info', description: 'Peak loads approaching capacity. Plan for upgrade or load shifting.' } },
    { id: 3, pduId: 'PDU-B1', zone: 'Zone B', rackCount: 20, currentLoad: 165, capacity: 250, utilization: 66, peakLoad: 180, powerFactor: 95, efficiency: 93, status: 'Normal',
      recommendation: { title: 'Optimize Power Factor', type: 'success', description: 'Power factor is good. Maintain current practices.' } },
    { id: 4, pduId: 'PDU-B2', zone: 'Zone B', rackCount: 20, currentLoad: 205, capacity: 250, utilization: 82, peakLoad: 225, powerFactor: 92, efficiency: 90, status: 'Warning',
      recommendation: { title: 'Capacity Alert', type: 'warning', description: 'Utilization above 80%. Plan capacity expansion within 6 months.' } },
    { id: 5, pduId: 'PDU-C1', zone: 'Zone C', rackCount: 18, currentLoad: 98, capacity: 200, utilization: 49, peakLoad: 120, powerFactor: 97, efficiency: 95, status: 'Normal',
      recommendation: { title: 'Consolidation Opportunity', type: 'info', description: 'Low utilization suggests consolidation or redeployment possible.' } },
    { id: 6, pduId: 'PDU-C2', zone: 'Zone C', rackCount: 18, currentLoad: 145, capacity: 200, utilization: 73, peakLoad: 160, powerFactor: 94, efficiency: 92, status: 'Normal',
      recommendation: { title: 'Balanced Load', type: 'success', description: 'Load distribution is well balanced across phases.' } },
    { id: 7, pduId: 'PDU-D1', zone: 'Zone D', rackCount: 16, currentLoad: 175, capacity: 200, utilization: 88, peakLoad: 190, powerFactor: 91, efficiency: 88, status: 'Warning',
      recommendation: { title: 'Immediate Attention', type: 'error', description: 'Critical capacity threshold. Immediate load reduction or capacity upgrade required.' } },
    { id: 8, pduId: 'PDU-D2', zone: 'Zone D', rackCount: 16, currentLoad: 155, capacity: 200, utilization: 78, peakLoad: 170, powerFactor: 93, efficiency: 91, status: 'Normal',
      recommendation: { title: 'Monitor Trend', type: 'info', description: 'Load growing steadily. Review capacity plan quarterly.' } }
  ]
  return pduData
}

const pduData = ref<PduUnit[]>(generatePduData())

// ==================== State ====================
const dateRange = ref<Date[] | null>(null)
const zoneFilter = ref('')
const pduFilter = ref('')
const trendPeriod = ref('30')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const selectedPdu = ref<PduUnit | null>(null)

// Chart refs
let consumptionTrendChart: echarts.ECharts | null = null
let distributionChart: echarts.ECharts | null = null
let hourlyProfileChart: echarts.ECharts | null = null
let pduUtilizationChart: echarts.ECharts | null = null
let powerFactorChart: echarts.ECharts | null = null
let upsLoadChart: echarts.ECharts | null = null
let capacityChart: echarts.ECharts | null = null
let rackLoadChart: echarts.ECharts | null = null
let pduHourlyChart: echarts.ECharts | null = null

const consumptionTrendChartEl = ref<HTMLElement | null>(null)
const distributionChartEl = ref<HTMLElement | null>(null)
const hourlyProfileChartEl = ref<HTMLElement | null>(null)
const pduUtilizationChartEl = ref<HTMLElement | null>(null)
const powerFactorChartEl = ref<HTMLElement | null>(null)
const upsLoadChartEl = ref<HTMLElement | null>(null)
const capacityChartEl = ref<HTMLElement | null>(null)
const rackLoadChartEl = ref<HTMLElement | null>(null)
const pduHourlyChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  const totalPower = pduData.value.reduce((sum, d) => sum + d.currentLoad, 0) / 1000
  const totalCapacity = pduData.value.reduce((sum, d) => sum + d.capacity, 0) / 1000
  const itLoad = totalPower * 0.65
  const utilization = (totalPower / totalCapacity) * 100
  const powerCost = 385
  const costReduction = 8.5

  return {
    totalPower: totalPower.toFixed(1),
    powerTrend: 3.2,
    itLoad: itLoad.toFixed(1),
    itPercent: 65,
    utilization: utilization.toFixed(0),
    utilTrend: 2.5,
    powerCost: powerCost,
    costReduction: costReduction
  }
})

const metrics = computed(() => {
  const totalCapacity = pduData.value.reduce((sum, d) => sum + d.capacity, 0) / 1000
  const currentLoad = pduData.value.reduce((sum, d) => sum + d.currentLoad, 0) / 1000
  const availableCapacity = totalCapacity - currentLoad
  const peakDemand = 4.2
  const avgPowerFactor = (pduData.value.reduce((sum, d) => sum + d.powerFactor, 0) / pduData.value.length).toFixed(0)

  return {
    capacity: totalCapacity.toFixed(1),
    availableCapacity: availableCapacity.toFixed(1),
    peakDemand: peakDemand,
    peakTime: '14:30-15:30',
    powerFactor: parseInt(avgPowerFactor),
    reserveCapacity: (totalCapacity * 0.15).toFixed(1),
    reservePercent: 15
  }
})

const filteredData = computed(() => {
  let filtered = [...pduData.value]

  if (zoneFilter.value) {
    filtered = filtered.filter(d => d.zone === zoneFilter.value)
  }

  if (pduFilter.value) {
    filtered = filtered.filter(d => d.pduId === pduFilter.value)
  }

  if (dateRange.value && dateRange.value.length === 2) {
    // Filter logic would go here
  }

  return filtered
})

const totalRecords = computed(() => filteredData.value.length)

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getLoadClass = (current: number, capacity: number): string => {
  const ratio = current / capacity
  if (ratio <= 0.6) return 'metric-good'
  if (ratio <= 0.8) return 'metric-warning'
  return 'metric-bad'
}

const getUtilizationColor = (util: number): string => {
  if (util <= 60) return '#22c55e'
  if (util <= 80) return '#f59e0b'
  return '#ef4444'
}

const getPFPositive = (pf: number): string => {
  if (pf >= 95) return 'metric-good'
  if (pf >= 90) return 'metric-warning'
  return 'metric-bad'
}

const resetFilters = () => {
  zoneFilter.value = ''
  pduFilter.value = ''
  dateRange.value = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

// ==================== Chart Functions ====================
const initConsumptionTrendChart = () => {
  if (!consumptionTrendChartEl.value) return
  if (consumptionTrendChart) {
    consumptionTrendChart.dispose()
    consumptionTrendChart = null
  }

  const days = parseInt(trendPeriod.value)
  const labels = Array.from({ length: days }, (_, i) => `Day ${i + 1}`)
  const powerData = labels.map(() => 3.2 + Math.random() * 0.8)

  consumptionTrendChart = echarts.init(consumptionTrendChartEl.value)
  consumptionTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 60, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: labels, axisLabel: { rotate: 45, interval: Math.floor(days / 10) } },
    yAxis: { type: 'value', name: 'Power (MW)' },
    series: [{
      type: 'line',
      data: powerData,
      smooth: true,
      lineStyle: { color: '#3b82f6', width: 2 },
      symbol: 'circle',
      symbolSize: 4,
      areaStyle: { opacity: 0.1 }
    }]
  })
}

const initDistributionChart = () => {
  if (!distributionChartEl.value) return
  if (distributionChart) {
    distributionChart.dispose()
    distributionChart = null
  }

  const zoneMap = new Map<string, number>()
  pduData.value.forEach(d => {
    zoneMap.set(d.zone, (zoneMap.get(d.zone) || 0) + d.currentLoad)
  })

  const data = Array.from(zoneMap.entries()).map(([name, value]) => ({ name, value: (value / 1000).toFixed(1) }))

  distributionChart = echarts.init(distributionChartEl.value)
  distributionChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} MW' },
    legend: { orient: 'vertical', left: 'left', data: data.map(d => d.name) },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: data.map(d => ({ name: d.name, value: parseFloat(d.value) })),
      label: { show: true, formatter: '{b}: {c} MW' },
      emphasis: { scale: true }
    }]
  })
}

const initHourlyProfileChart = () => {
  if (!hourlyProfileChartEl.value) return
  if (hourlyProfileChart) {
    hourlyProfileChart.dispose()
    hourlyProfileChart = null
  }

  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const powerData = [3.2, 3.1, 3.0, 2.9, 2.8, 2.9, 3.1, 3.4, 3.6, 3.8, 3.9, 3.9, 3.8, 3.7, 3.8, 3.9, 4.0, 4.1, 4.0, 3.8, 3.6, 3.4, 3.3, 3.2]

  hourlyProfileChart = echarts.init(hourlyProfileChartEl.value)
  hourlyProfileChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 60, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: hours, axisLabel: { rotate: 45, interval: 3 } },
    yAxis: { type: 'value', name: 'Power (MW)' },
    series: [{
      type: 'line',
      data: powerData,
      smooth: true,
      lineStyle: { color: '#f59e0b', width: 2 },
      symbol: 'circle',
      symbolSize: 4,
      areaStyle: { opacity: 0.1 }
    }]
  })
}

const initPduUtilizationChart = () => {
  if (!pduUtilizationChartEl.value) return
  if (pduUtilizationChart) {
    pduUtilizationChart.dispose()
    pduUtilizationChart = null
  }

  const names = pduData.value.map(d => d.pduId)
  const utils = pduData.value.map(d => d.utilization)

  pduUtilizationChart = echarts.init(pduUtilizationChartEl.value)
  pduUtilizationChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 40, containLabel: true },
    xAxis: { type: 'category', data: names, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: 'Utilization (%)', max: 100 },
    series: [{
      type: 'bar',
      data: utils,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value <= 60) return '#22c55e'
          if (value <= 80) return '#f59e0b'
          return '#ef4444'
        }
      },
      label: { show: true, position: 'top', formatter: '{c}%' },
      markLine: {
        data: [{ yAxis: 60, name: 'Optimal' }, { yAxis: 80, name: 'Warning' }],
        lineStyle: { type: 'dashed' },
        label: { show: true }
      }
    }]
  })
}

const initPowerFactorChart = () => {
  if (!powerFactorChartEl.value) return
  if (powerFactorChart) {
    powerFactorChart.dispose()
    powerFactorChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const pfData = [94, 94, 95, 95, 94, 93, 92, 93, 94, 95, 95, 96]

  powerFactorChart = echarts.init(powerFactorChartEl.value)
  powerFactorChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 60, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Power Factor (%)', min: 90, max: 100 },
    series: [{
      type: 'line',
      data: pfData,
      smooth: true,
      lineStyle: { color: '#22c55e', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initUpsLoadChart = () => {
  if (!upsLoadChartEl.value) return
  if (upsLoadChart) {
    upsLoadChart.dispose()
    upsLoadChart = null
  }

  const upsNames = ['UPS 1', 'UPS 2', 'UPS 3', 'UPS 4']
  const loads = [65, 72, 58, 81]

  upsLoadChart = echarts.init(upsLoadChartEl.value)
  upsLoadChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: upsNames },
    yAxis: { type: 'value', name: 'Load (%)', max: 100 },
    series: [{
      type: 'bar',
      data: loads,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value <= 60) return '#22c55e'
          if (value <= 80) return '#f59e0b'
          return '#ef4444'
        }
      },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initCapacityChart = () => {
  if (!capacityChartEl.value) return
  if (capacityChart) {
    capacityChart.dispose()
    capacityChart = null
  }

  const quarters = ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024', 'Q1 2025', 'Q2 2025']
  const current = [3.8, 3.9, 4.0, 4.1, 4.2, 4.3]
  const capacity = [5.0, 5.0, 5.0, 5.5, 5.5, 5.5]

  capacityChart = echarts.init(capacityChartEl.value)
  capacityChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Current Load', 'Capacity'], bottom: 0 },
    grid: { top: 30, left: 60, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: quarters },
    yAxis: { type: 'value', name: 'Power (MW)' },
    series: [
      { name: 'Current Load', type: 'line', data: current, lineStyle: { color: '#f59e0b', width: 3 }, symbol: 'circle', areaStyle: { opacity: 0.1 } },
      { name: 'Capacity', type: 'line', data: capacity, lineStyle: { color: '#22c55e', width: 3, type: 'dashed' }, symbol: 'diamond' }
    ]
  })
}

const initRackLoadChart = () => {
  if (!rackLoadChartEl.value || !selectedPdu.value) return
  if (rackLoadChart) {
    rackLoadChart.dispose()
    rackLoadChart = null
  }

  const racks = Array.from({ length: selectedPdu.value.rackCount }, (_, i) => `Rack ${i + 1}`)
  const loads = racks.map(() => 5 + Math.random() * 10)

  rackLoadChart = echarts.init(rackLoadChartEl.value)
  rackLoadChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 40, containLabel: true },
    xAxis: { type: 'category', data: racks, axisLabel: { rotate: 45, interval: 5 } },
    yAxis: { type: 'value', name: 'Load (kW)' },
    series: [{
      type: 'bar',
      data: loads,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value <= 8) return '#22c55e'
          if (value <= 12) return '#f59e0b'
          return '#ef4444'
        }
      },
      label: { show: true, position: 'top', formatter: '{c} kW' }
    }]
  })
}

const initPduHourlyChart = () => {
  if (!pduHourlyChartEl.value || !selectedPdu.value) return
  if (pduHourlyChart) {
    pduHourlyChart.dispose()
    pduHourlyChart = null
  }

  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const baseLoad = selectedPdu.value.currentLoad / 24
  const loads = hours.map(() => baseLoad * (0.7 + Math.random() * 0.6))

  pduHourlyChart = echarts.init(pduHourlyChartEl.value)
  pduHourlyChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 60, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: hours, axisLabel: { rotate: 45, interval: 3 } },
    yAxis: { type: 'value', name: 'Load (kW)' },
    series: [{
      type: 'line',
      data: loads,
      smooth: true,
      lineStyle: { color: '#3b82f6', width: 2 },
      areaStyle: { opacity: 0.1 }
    }]
  })
}

const updateConsumptionTrend = () => {
  initConsumptionTrendChart()
}

const refreshCharts = () => {
  nextTick(() => {
    initConsumptionTrendChart()
    initDistributionChart()
    initHourlyProfileChart()
    initPduUtilizationChart()
    initPowerFactorChart()
    initUpsLoadChart()
    initCapacityChart()
  })
}

// ==================== Actions ====================
const viewPduDetail = (pdu: PduUnit) => {
  selectedPdu.value = pdu
  detailDialogVisible.value = true
  nextTick(() => {
    initRackLoadChart()
    initPduHourlyChart()
  })
}

const viewAllData = () => {
  ElMessage.info('Viewing all PDUs')
}

const exportPduReport = (pdu: PduUnit | null) => {
  if (pdu) {
    ElMessage.success(`Exporting report for ${pdu.pduId}...`)
    setTimeout(() => {
      ElMessage.success('Report generated successfully')
    }, 1500)
  }
}

const exportData = () => {
  ElMessage.success('Exporting power utilization data...')
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
    const charts = [consumptionTrendChart, distributionChart, hourlyProfileChart, pduUtilizationChart, powerFactorChart, upsLoadChart, capacityChart, rackLoadChart, pduHourlyChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([zoneFilter, pduFilter, dateRange], () => {
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
  const charts = [consumptionTrendChart, distributionChart, hourlyProfileChart, pduUtilizationChart, powerFactorChart, upsLoadChart, capacityChart, rackLoadChart, pduHourlyChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.power-utilization-page {
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

/* Loading Screen - same as previous */
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
  height: 280px;
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

/* PDU Detail */
.pdu-detail {
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
  max-height: 550px;
  overflow-y: auto;
}
:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}
</style>