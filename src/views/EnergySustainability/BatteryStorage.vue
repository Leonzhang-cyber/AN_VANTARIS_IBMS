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
          <span class="loading-title">Battery Storage</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">BESS Performance & Energy Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="battery-storage-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Iphone /></el-icon>
          Battery Storage
        </h1>
        <div class="page-subtitle">Real-time BESS monitoring, state of charge, and energy management</div>
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
          <el-icon><Iphone /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.soc }}<span class="stat-unit">%</span></div>
          <div class="stat-label">State of Charge</div>
          <div class="stat-trend" :class="stats.socTrend > 0 ? 'up' : 'down'">
            {{ stats.socTrend > 0 ? '↑' : '↓' }} {{ Math.abs(stats.socTrend) }}% vs last hour
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.currentPower }}<span class="stat-unit">kW</span></div>
          <div class="stat-label">Power</div>
          <div class="stat-trend" :class="stats.powerTrend > 0 ? 'up' : 'down'">
            {{ stats.powerTrend > 0 ? '↑' : '↓' }} {{ Math.abs(stats.powerTrend) }}% vs last hour
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.todayEnergy }}<span class="stat-unit">kWh</span></div>
          <div class="stat-label">Today's Throughput</div>
          <div class="stat-trend" :class="stats.energyTrend > 0 ? 'up' : 'down'">
            {{ stats.energyTrend > 0 ? '↑' : '↓' }} {{ Math.abs(stats.energyTrend) }}% vs yesterday
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">${{ stats.savings }}<span class="stat-unit">k</span></div>
          <div class="stat-label">Cost Savings</div>
          <div class="stat-trend up">YTD</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Capacity</div>
        <div class="metric-value">{{ metrics.capacity }}<span class="metric-unit">kWh</span></div>
        <div class="metric-sub">Usable: {{ metrics.usableCapacity }} kWh</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Charge/Discharge</div>
        <div class="metric-value">{{ metrics.chargeRate }}<span class="metric-unit">kW</span></div>
        <div class="metric-sub">Discharge: {{ metrics.dischargeRate }} kW</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Round Trip Efficiency</div>
        <div class="metric-value">{{ metrics.efficiency }}<span class="metric-unit">%</span></div>
        <el-progress :percentage="metrics.efficiency" :stroke-width="8" :color="metrics.efficiency > 85 ? '#22c55e' : (metrics.efficiency > 75 ? '#f59e0b' : '#ef4444')" />
      </div>
      <div class="metric-card">
        <div class="metric-title">Battery Health</div>
        <div class="metric-value">{{ metrics.health }}<span class="metric-unit">%</span></div>
        <div class="metric-trend" :class="metrics.healthTrend > 0 ? 'positive' : 'negative'">
          {{ metrics.healthTrend > 0 ? '↑' : '↓' }} {{ Math.abs(metrics.healthTrend) }}% vs last month
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card large">
        <div class="chart-header">
          <span class="chart-title">Power & SOC Trend</span>
          <span class="chart-subtitle">Real-time charge/discharge</span>
          <el-select v-model="timeRange" size="small" style="width: 100px" @change="updateRealTimeChart">
            <el-option label="6 Hours" value="6" />
            <el-option label="12 Hours" value="12" />
            <el-option label="24 Hours" value="24" />
          </el-select>
        </div>
        <div class="chart-container" ref="realtimeChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">SOC Distribution</span>
          <span class="chart-subtitle">By battery rack</span>
        </div>
        <div class="chart-container" ref="socChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Charge/Discharge Cycles</span>
          <span class="chart-subtitle">Daily pattern</span>
        </div>
        <div class="chart-container" ref="cyclesChartEl"></div>
      </div>
    </div>

    <!-- Third Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Temperature Monitoring</span>
          <span class="chart-subtitle">Battery thermal status</span>
        </div>
        <div class="chart-container" ref="tempChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Energy Arbitrage</span>
          <span class="chart-subtitle">Grid vs Battery cost</span>
        </div>
        <div class="chart-container" ref="arbitrageChartEl"></div>
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
        <el-select v-model="rackFilter" placeholder="Battery Rack" clearable style="width: 150px">
          <el-option v-for="r in racksList" :key="r" :label="r" :value="r" />
        </el-select>
        <el-select v-model="modeFilter" placeholder="Operation Mode" clearable style="width: 140px">
          <el-option label="Charging" value="charging" />
          <el-option label="Discharging" value="discharging" />
          <el-option label="Idle" value="idle" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Battery Racks Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Battery Racks</span>
        <el-button size="small" @click="viewAllRacks">View All →</el-button>
      </div>
      <el-table :data="paginatedRacks" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="name" label="Rack Name" min-width="150" />
        <el-table-column prop="location" label="Location" width="150" />
        <el-table-column prop="soc" label="SoC" width="140">
          <template #default="{ row }">
            <el-progress :percentage="row.soc" :stroke-width="8" :color="getSocColor(row.soc)" :format="() => `${row.soc.toFixed(1)}%`" />
          </template>
        </el-table-column>
        <el-table-column prop="power" label="Power (kW)" width="120">
          <template #default="{ row }">
            <span :class="row.power > 0 ? 'metric-good' : (row.power < 0 ? 'metric-warning' : 'metric')">
              {{ row.power > 0 ? '+' : '' }}{{ row.power.toFixed(1) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="voltage" label="Voltage (V)" width="110">
          <template #default="{ row }">
            {{ row.voltage.toFixed(1) }}
          </template>
        </el-table-column>
        <el-table-column prop="current" label="Current (A)" width="110">
          <template #default="{ row }">
            {{ row.current.toFixed(1) }}
          </template>
        </el-table-column>
        <el-table-column prop="temperature" label="Temp (°C)" width="100">
          <template #default="{ row }">
            <span :class="row.temperature > 35 ? 'metric-warning' : (row.temperature > 45 ? 'metric-bad' : 'metric-good')">
              {{ row.temperature.toFixed(1) }}°C
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="health" label="Health" width="100">
          <template #default="{ row }">
            <el-progress :percentage="row.health" :stroke-width="6" :color="row.health > 85 ? '#22c55e' : (row.health > 70 ? '#f59e0b' : '#ef4444')" :format="() => `${row.health.toFixed(0)}%`" />
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Charging' ? 'success' : (row.status === 'Discharging' ? 'warning' : 'info')" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewRackDetail(row)">Details</el-button>
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

    <!-- Rack Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedRack?.name" width="1000px" class="rack-dialog">
      <div v-if="selectedRack" class="rack-detail">
        <div class="detail-header-stats">
          <div class="detail-stat">
            <div class="detail-stat-value" :style="{ color: getSocColor(selectedRack.soc) }">
              {{ selectedRack.soc.toFixed(1) }}%
            </div>
            <div class="detail-stat-label">State of Charge</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedRack.power > 0 ? '+' : '' }}{{ selectedRack.power.toFixed(1) }}<span class="stat-unit">kW</span></div>
            <div class="detail-stat-label">Power</div>
            <div class="detail-stat-sub">{{ selectedRack.status }}</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedRack.health.toFixed(0) }}<span class="stat-unit">%</span></div>
            <div class="detail-stat-label">Health</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedRack.cycleCount }}</div>
            <div class="detail-stat-label">Cycles</div>
          </div>
        </div>

        <el-descriptions :column="3" border>
          <el-descriptions-item label="Rack ID">{{ selectedRack.id }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedRack.location }}</el-descriptions-item>
          <el-descriptions-item label="Manufacturer">{{ selectedRack.manufacturer }}</el-descriptions-item>
          <el-descriptions-item label="Capacity">{{ selectedRack.capacity }} kWh</el-descriptions-item>
          <el-descriptions-item label="Usable Capacity">{{ selectedRack.usableCapacity }} kWh</el-descriptions-item>
          <el-descriptions-item label="Voltage">{{ selectedRack.voltage.toFixed(1) }} V</el-descriptions-item>
          <el-descriptions-item label="Current">{{ selectedRack.current.toFixed(1) }} A</el-descriptions-item>
          <el-descriptions-item label="Temperature">{{ selectedRack.temperature.toFixed(1) }} °C</el-descriptions-item>
          <el-descriptions-item label="Install Date">{{ selectedRack.installDate }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <div class="section-title">Cell Voltage Distribution</div>
          <div class="trend-chart" ref="cellDetailChartEl"></div>
        </div>

        <div class="detail-section" v-if="selectedRack.alerts.length > 0">
          <div class="section-title">Recent Alerts</div>
          <el-table :data="selectedRack.alerts" border stripe>
            <el-table-column prop="date" label="Date" width="150" />
            <el-table-column prop="type" label="Type" width="120" />
            <el-table-column prop="description" label="Description" min-width="300" />
            <el-table-column prop="severity" label="Severity" width="100">
              <template #default="{ row }">
                <el-tag :type="row.severity === 'High' ? 'danger' : (row.severity === 'Medium' ? 'warning' : 'info')" size="small">
                  {{ row.severity }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="exportRackReport(selectedRack)">Export Report</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Iphone, DataLine, Calendar, Money, Download, Refresh,
  RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading battery storage data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading BESS data...',
  'Fetching SOC metrics...',
  'Calculating efficiency...',
  'Analyzing cycle data...',
  'Almost ready...'
]

// ==================== Types ====================
interface RackAlert {
  date: string
  type: string
  description: string
  severity: string
}

interface BatteryRack {
  id: string
  name: string
  location: string
  manufacturer: string
  capacity: number
  usableCapacity: number
  soc: number
  power: number
  voltage: number
  current: number
  temperature: number
  health: number
  cycleCount: number
  status: string
  installDate: string
  alerts: RackAlert[]
}

// ==================== Mock Data ====================
const racksList = ['Rack A', 'Rack B', 'Rack C', 'Rack D', 'Rack E', 'Rack F']
const locations = ['BESS Room 1', 'BESS Room 2', 'Container 1', 'Container 2', 'Basement', 'Ground Floor']
const manufacturers = ['Tesla', 'BYD', 'LG Chem', 'Samsung SDI', 'CATL', 'Panasonic']

const generateRackData = (): BatteryRack[] => {
  const racks: BatteryRack[] = []

  for (let i = 1; i <= 12; i++) {
    const capacity = [100, 150, 200, 250, 300, 500][Math.floor(Math.random() * 6)]
    const usableCapacity = capacity * 0.9
    const soc = parseFloat((30 + Math.random() * 60).toFixed(1))
    const power = parseFloat((Math.random() * 100 - 50).toFixed(1))
    const voltage = parseFloat((400 + Math.random() * 200).toFixed(1))
    const current = power > 0 ? parseFloat((power * 1000 / voltage).toFixed(1)) : parseFloat((-power * 1000 / voltage).toFixed(1))
    const temperature = parseFloat((22 + Math.random() * 15).toFixed(1))
    const health = parseFloat((80 + Math.random() * 15).toFixed(1))
    const cycleCount = Math.floor(Math.random() * 500)

    let status = 'Idle'
    if (power > 5) status = 'Charging'
    else if (power < -5) status = 'Discharging'

    const alerts: RackAlert[] = []
    if (temperature > 40) {
      alerts.push({
        date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
        type: 'High Temperature',
        description: `Battery temperature reached ${temperature.toFixed(1)}°C, above threshold`,
        severity: 'High'
      })
    }
    if (health < 85) {
      alerts.push({
        date: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
        type: 'Degradation Warning',
        description: `Battery health degraded to ${health.toFixed(0)}%, capacity loss detected`,
        severity: 'Medium'
      })
    }
    if (soc < 15) {
      alerts.push({
        date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
        type: 'Low SOC',
        description: `State of charge dropped to ${soc.toFixed(1)}%, recharge recommended`,
        severity: 'Medium'
      })
    }

    racks.push({
      id: `BESS-${String(i).padStart(4, '0')}`,
      name: racksList[(i - 1) % racksList.length] + (Math.floor((i - 1) / racksList.length) + 1),
      location: locations[(i - 1) % locations.length],
      manufacturer: manufacturers[Math.floor(Math.random() * manufacturers.length)],
      capacity: capacity,
      usableCapacity: usableCapacity,
      soc: soc,
      power: power,
      voltage: voltage,
      current: current,
      temperature: temperature,
      health: health,
      cycleCount: cycleCount,
      status: status,
      installDate: new Date(Date.now() - Math.random() * 730 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
      alerts: alerts
    })
  }

  return racks
}

const racks = ref<BatteryRack[]>(generateRackData())

// ==================== State ====================
const rackFilter = ref('')
const modeFilter = ref('')
const dateRange = ref<Date[] | null>(null)
const timeRange = ref('24')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const selectedRack = ref<BatteryRack | null>(null)

// Chart refs
let realtimeChart: echarts.ECharts | null = null
let socChart: echarts.ECharts | null = null
let cyclesChart: echarts.ECharts | null = null
let tempChart: echarts.ECharts | null = null
let arbitrageChart: echarts.ECharts | null = null
let cellDetailChart: echarts.ECharts | null = null

const realtimeChartEl = ref<HTMLElement | null>(null)
const socChartEl = ref<HTMLElement | null>(null)
const cyclesChartEl = ref<HTMLElement | null>(null)
const tempChartEl = ref<HTMLElement | null>(null)
const arbitrageChartEl = ref<HTMLElement | null>(null)
const cellDetailChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  const avgSoc = racks.value.reduce((sum, r) => sum + r.soc, 0) / racks.value.length
  const totalPower = racks.value.reduce((sum, r) => sum + r.power, 0)
  const todayEnergy = Math.abs(totalPower) * 12
  const savings = Math.round(todayEnergy * 0.15 / 1000)

  return {
    soc: parseFloat(avgSoc.toFixed(1)),
    socTrend: 2.5,
    currentPower: parseFloat(Math.abs(totalPower).toFixed(1)),
    powerTrend: 5.2,
    todayEnergy: Math.round(Math.abs(todayEnergy)),
    energyTrend: 8.3,
    savings: savings
  }
})

const metrics = computed(() => {
  const totalCapacity = racks.value.reduce((sum, r) => sum + r.capacity, 0)
  const totalUsable = racks.value.reduce((sum, r) => sum + r.usableCapacity, 0)
  const avgEfficiency = (racks.value.reduce((sum, r) => sum + r.health, 0) / racks.value.length).toFixed(1)
  const avgHealth = (racks.value.reduce((sum, r) => sum + r.health, 0) / racks.value.length).toFixed(1)

  return {
    capacity: totalCapacity,
    usableCapacity: Math.round(totalUsable),
    chargeRate: 85,
    dischargeRate: 82,
    efficiency: parseFloat(avgEfficiency),
    health: parseFloat(avgHealth),
    healthTrend: -1.2
  }
})

const filteredRacks = computed(() => {
  let filtered = [...racks.value]

  if (rackFilter.value) {
    filtered = filtered.filter(r => r.name === rackFilter.value)
  }

  if (modeFilter.value === 'charging') {
    filtered = filtered.filter(r => r.power > 5)
  } else if (modeFilter.value === 'discharging') {
    filtered = filtered.filter(r => r.power < -5)
  } else if (modeFilter.value === 'idle') {
    filtered = filtered.filter(r => Math.abs(r.power) <= 5)
  }

  return filtered
})

const totalRecords = computed(() => filteredRacks.value.length)

const paginatedRacks = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRacks.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getSocColor = (soc: number): string => {
  if (soc >= 70) return '#22c55e'
  if (soc >= 30) return '#f59e0b'
  return '#ef4444'
}

const resetFilters = () => {
  rackFilter.value = ''
  modeFilter.value = ''
  dateRange.value = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

// ==================== Chart Functions ====================
const initRealtimeChart = () => {
  if (!realtimeChartEl.value) return
  if (realtimeChart) {
    realtimeChart.dispose()
    realtimeChart = null
  }

  const hours = timeRange.value === '6' ? 6 : (timeRange.value === '12' ? 12 : 24)
  const labels = Array.from({ length: hours }, (_, i) => `${i}:00`)
  const powerData = labels.map(() => parseFloat((20 + Math.random() * 80 - 40).toFixed(1)))
  const socData = labels.map(() => parseFloat((40 + Math.random() * 40).toFixed(1)))

  realtimeChart = echarts.init(realtimeChartEl.value)
  realtimeChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Power (kW)', 'SoC (%)'], bottom: 0 },
    grid: { top: 40, left: 60, right: 60, bottom: 40 },
    xAxis: { type: 'category', data: labels, axisLabel: { rotate: 45, interval: Math.floor(hours / 12) } },
    yAxis: [
      { type: 'value', name: 'Power (kW)', position: 'left' },
      { type: 'value', name: 'SoC (%)', position: 'right', min: 0, max: 100 }
    ],
    series: [
      { name: 'Power (kW)', type: 'line', data: powerData, lineStyle: { color: '#3b82f6', width: 2 }, symbol: 'circle', areaStyle: { opacity: 0.1 } },
      { name: 'SoC (%)', type: 'line', data: socData, lineStyle: { color: '#22c55e', width: 2 }, symbol: 'diamond', yAxisIndex: 1, areaStyle: { opacity: 0.1 } }
    ]
  })
}

const initSocChart = () => {
  if (!socChartEl.value) return
  if (socChart) {
    socChart.dispose()
    socChart = null
  }

  const rackData = racks.value.map(r => ({ name: r.name, value: r.soc }))

  socChart = echarts.init(socChartEl.value)
  socChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 40, containLabel: true },
    xAxis: { type: 'category', data: rackData.map(d => d.name), axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'SoC (%)', min: 0, max: 100 },
    series: [{
      type: 'bar',
      data: rackData.map(d => d.value),
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value >= 70) return '#22c55e'
          if (value >= 30) return '#f59e0b'
          return '#ef4444'
        }
      },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initCyclesChart = () => {
  if (!cyclesChartEl.value) return
  if (cyclesChart) {
    cyclesChart.dispose()
    cyclesChart = null
  }

  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const chargeData = hours.map(() => parseFloat((5 + Math.random() * 40).toFixed(1)))
  const dischargeData = hours.map(() => parseFloat((5 + Math.random() * 40).toFixed(1)))

  cyclesChart = echarts.init(cyclesChartEl.value)
  cyclesChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Charge', 'Discharge'], bottom: 0 },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: hours, axisLabel: { rotate: 45, interval: 3 } },
    yAxis: { type: 'value', name: 'Power (kW)' },
    series: [
      { name: 'Charge', type: 'bar', data: chargeData, itemStyle: { color: '#22c55e', borderRadius: [4, 4, 0, 0] }, label: { show: false } },
      { name: 'Discharge', type: 'bar', data: dischargeData, itemStyle: { color: '#ef4444', borderRadius: [4, 4, 0, 0] }, label: { show: false } }
    ]
  })
}

const initTempChart = () => {
  if (!tempChartEl.value) return
  if (tempChart) {
    tempChart.dispose()
    tempChart = null
  }

  const rackData = racks.value.map(r => ({ name: r.name, temperature: r.temperature }))

  tempChart = echarts.init(tempChartEl.value)
  tempChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 40, containLabel: true },
    xAxis: { type: 'category', data: rackData.map(d => d.name), axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'Temperature (°C)', min: 20, max: 50 },
    series: [{
      type: 'bar',
      data: rackData.map(d => d.temperature),
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value <= 30) return '#22c55e'
          if (value <= 40) return '#f59e0b'
          return '#ef4444'
        }
      },
      label: { show: true, position: 'top', formatter: '{c}°C' }
    }]
  })
}

const initArbitrageChart = () => {
  if (!arbitrageChartEl.value) return
  if (arbitrageChart) {
    arbitrageChart.dispose()
    arbitrageChart = null
  }

  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const gridPrice = [0.12, 0.11, 0.10, 0.09, 0.09, 0.10, 0.14, 0.18, 0.22, 0.25, 0.28, 0.30, 0.32, 0.31, 0.28, 0.26, 0.28, 0.30, 0.32, 0.28, 0.22, 0.18, 0.14, 0.12]
  const batteryPrice = hours.map(() => 0.15)

  arbitrageChart = echarts.init(arbitrageChartEl.value)
  arbitrageChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Grid Price', 'Battery LCOE'], bottom: 0 },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: hours, axisLabel: { rotate: 45, interval: 3 } },
    yAxis: { type: 'value', name: 'Price ($/kWh)', min: 0.05, max: 0.35 },
    series: [
      { name: 'Grid Price', type: 'line', data: gridPrice, lineStyle: { color: '#ef4444', width: 2 }, symbol: 'circle', areaStyle: { opacity: 0.1 } },
      { name: 'Battery LCOE', type: 'line', data: batteryPrice, lineStyle: { color: '#22c55e', width: 2, type: 'dashed' }, symbol: 'diamond' }
    ]
  })
}

const initCellDetailChart = () => {
  if (!cellDetailChartEl.value || !selectedRack.value) return
  if (cellDetailChart) {
    cellDetailChart.dispose()
    cellDetailChart = null
  }

  const cells = Array.from({ length: 16 }, (_, i) => `Cell ${i + 1}`)
  const voltages = cells.map(() => parseFloat((3.2 + Math.random() * 0.4).toFixed(2)))

  cellDetailChart = echarts.init(cellDetailChartEl.value)
  cellDetailChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: cells, axisLabel: { rotate: 45, interval: 3 } },
    yAxis: { type: 'value', name: 'Voltage (V)', min: 3.0, max: 3.6 },
    series: [{
      type: 'bar',
      data: voltages,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value >= 3.3) return '#22c55e'
          if (value >= 3.1) return '#f59e0b'
          return '#ef4444'
        }
      },
      label: { show: true, position: 'top', formatter: '{c}V' }
    }]
  })
}

const updateRealTimeChart = () => {
  initRealtimeChart()
}

const refreshCharts = () => {
  nextTick(() => {
    initRealtimeChart()
    initSocChart()
    initCyclesChart()
    initTempChart()
    initArbitrageChart()
  })
}

// ==================== Actions ====================
const viewRackDetail = (rack: BatteryRack) => {
  selectedRack.value = rack
  detailDialogVisible.value = true
  nextTick(() => initCellDetailChart())
}

const viewAllRacks = () => {
  ElMessage.info('Viewing all racks')
}

const exportRackReport = (rack: BatteryRack | null) => {
  if (!rack) return
  ElMessage.success(`Exporting report for ${rack.name}...`)
  setTimeout(() => {
    ElMessage.success('Report generated successfully')
  }, 1500)
}

const exportData = () => {
  ElMessage.success('Exporting battery storage data...')
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
    const charts = [realtimeChart, socChart, cyclesChart, tempChart, arbitrageChart, cellDetailChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([rackFilter, modeFilter, dateRange], () => {
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
  const charts = [realtimeChart, socChart, cyclesChart, tempChart, arbitrageChart, cellDetailChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.battery-storage-page {
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

/* Header, Stats Grid, Metrics Row, Charts Row, Filter Bar, Table Container - similar to previous */
.page-header, .stats-grid, .stat-card, .metrics-row, .metric-card, .charts-row, .chart-card, .filter-bar, .table-container {
  /* Same styles as previous pages */
}

/* Additional styles for battery storage */
.stat-icon.blue { background: #eef2ff; color: #3b82f6; }
.stat-icon.green { background: #dcfce7; color: #22c55e; }
.stat-icon.orange { background: #fef3c7; color: #f59e0b; }
.stat-icon.red { background: #fee2e2; color: #ef4444; }

.metric-good { color: #22c55e; font-weight: 600; }
.metric-warning { color: #f59e0b; font-weight: 600; }
.metric-bad { color: #ef4444; font-weight: 600; }
.metric { color: #64748b; font-weight: 600; }

.rack-detail {
  padding: 8px;
}

.detail-header-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 16px;
}

.detail-stat {
  text-align: center;
}

.detail-stat-value {
  font-size: 28px;
  font-weight: 700;
}

.detail-stat-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

.detail-stat-sub {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 2px;
}

.detail-section {
  margin-bottom: 24px;
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

@media (max-width: 1000px) {
  .stats-grid, .metrics-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-row {
    flex-direction: column;
  }
  .detail-header-stats {
    grid-template-columns: repeat(2, 1fr);
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
}

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

<style scoped>
.battery-storage-page {
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

.stat-trend.up { color: #22c55e; }
.stat-trend.down { color: #ef4444; }

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

/* Rack Detail */
.rack-detail {
  padding: 8px;
}

.detail-header-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 16px;
}

.detail-stat {
  text-align: center;
}

.detail-stat-value {
  font-size: 28px;
  font-weight: 700;
}

.detail-stat-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

.detail-stat-sub {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 2px;
}

.detail-section {
  margin-bottom: 24px;
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
.metric { color: #64748b; font-weight: 600; }

/* Responsive */
@media (max-width: 1000px) {
  .stats-grid, .metrics-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-row {
    flex-direction: column;
  }
  .detail-header-stats {
    grid-template-columns: repeat(2, 1fr);
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