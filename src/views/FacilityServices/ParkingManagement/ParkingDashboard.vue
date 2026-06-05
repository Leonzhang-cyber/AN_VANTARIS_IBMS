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
          <span class="loading-title">Parking Dashboard</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Smart Parking Management System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="parking-dashboard-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Place /></el-icon>
          Parking Dashboard
        </h1>
        <div class="page-subtitle">Real-time parking occupancy monitoring and management</div>
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
          <el-icon><Place /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalSpots }}</div>
          <div class="stat-label">Total Parking Spots</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.availableSpots }}</div>
          <div class="stat-label">Available Spots</div>
          <div class="stat-trend up">↑ {{ stats.availableChange }} since last hour</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Loading /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.occupiedSpots }}</div>
          <div class="stat-label">Occupied Spots</div>
          <div class="stat-trend up">Occupancy: {{ stats.occupancyRate }}%</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.avgParkingDuration }}<span class="stat-unit">min</span></div>
          <div class="stat-label">Avg Parking Duration</div>
          <div class="stat-trend down">↓ {{ stats.durationChange }}% vs yesterday</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Peak Occupancy</div>
        <div class="metric-value">{{ metrics.peakOccupancy }}<span class="stat-unit">%</span></div>
        <div class="metric-sub">Today at {{ metrics.peakTime }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Turnover Rate</div>
        <div class="metric-value">{{ metrics.turnoverRate }}<span class="stat-unit">/day</span></div>
        <div class="metric-trend positive">↑ {{ metrics.turnoverGrowth }}% vs yesterday</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">EV Charging Usage</div>
        <div class="metric-value">{{ metrics.evChargingUsage }}<span class="stat-unit">%</span></div>
        <el-progress :percentage="metrics.evChargingUsage" :stroke-width="8" :color="metrics.evChargingUsage > 70 ? '#22c55e' : (metrics.evChargingUsage > 40 ? '#f59e0b' : '#ef4444')" />
      </div>
      <div class="metric-card">
        <div class="metric-title">Revenue Today</div>
        <div class="metric-value">${{ metrics.dailyRevenue }}<span class="stat-unit">k</span></div>
        <div class="metric-trend positive">↑ {{ metrics.revenueGrowth }}% vs yesterday</div>
      </div>
    </div>

    <!-- Zone Map Visualization -->
    <div class="zone-map-section">
      <div class="zone-map-header">
        <span class="section-title">Parking Zone Map</span>
        <div class="zone-legend">
          <span><span class="legend-dot available"></span> Available</span>
          <span><span class="legend-dot occupied"></span> Occupied</span>
          <span><span class="legend-dot reserved"></span> Reserved</span>
          <span><span class="legend-dot ev"></span> EV Charging</span>
          <span><span class="legend-dot disabled"></span> Disabled</span>
        </div>
      </div>
      <div class="zone-map">
        <div class="zone-row" v-for="row in zoneMap" :key="row.row">
          <div class="zone-label">{{ row.row }}</div>
          <div class="zone-spots">
            <div
                v-for="spot in row.spots"
                :key="spot.id"
                class="parking-spot"
                :class="spot.status"
                @click="showSpotDetail(spot)"
            >
              <span class="spot-number">{{ spot.number }}</span>
              <span class="spot-icon" v-if="spot.status === 'ev'">⚡</span>
              <span class="spot-icon" v-if="spot.status === 'disabled'">♿</span>
              <span class="spot-icon" v-if="spot.status === 'reserved'">🔒</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Occupancy Trend</span>
          <span class="chart-subtitle">Last 24 hours</span>
        </div>
        <div class="chart-container" ref="occupancyChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Zone Occupancy Distribution</span>
          <span class="chart-subtitle">By parking zone</span>
        </div>
        <div class="chart-container" ref="zoneChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Hourly Entry/Exit Pattern</span>
          <span class="chart-subtitle">Traffic flow analysis</span>
        </div>
        <div class="chart-container" ref="trafficChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Parking Duration Distribution</span>
          <span class="chart-subtitle">Stay length analysis</span>
        </div>
        <div class="chart-container" ref="durationChartEl"></div>
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
        <el-select v-model="zoneFilter" placeholder="Zone" clearable style="width: 120px">
          <el-option v-for="z in zones" :key="z" :label="z" :value="z" />
        </el-select>
        <el-select v-model="spotTypeFilter" placeholder="Spot Type" clearable style="width: 140px">
          <el-option label="Regular" value="regular" />
          <el-option label="EV Charging" value="ev" />
          <el-option label="Disabled" value="disabled" />
          <el-option label="Reserved" value="reserved" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Parking Transactions Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Recent Parking Transactions</span>
        <el-button size="small" @click="viewAllTransactions">View All →</el-button>
      </div>
      <el-table :data="paginatedTransactions" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="id" label="ID" width="100" />
        <el-table-column prop="vehicleNumber" label="Vehicle Number" min-width="140" />
        <el-table-column prop="spotId" label="Spot ID" width="100" />
        <el-table-column prop="zone" label="Zone" width="100" />
        <el-table-column prop="entryTime" label="Entry Time" width="160" />
        <el-table-column prop="exitTime" label="Exit Time" width="160" />
        <el-table-column prop="duration" label="Duration" width="100" />
        <el-table-column prop="amount" label="Amount" width="100">
          <template #default="{ row }">
            ${{ row.amount }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
              {{ row.status === 'active' ? 'Active' : 'Completed' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewTransactionDetail(row)">Details</el-button>
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

    <!-- Spot Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Parking Spot ${selectedSpot?.number}`" width="500px">
      <div v-if="selectedSpot" class="spot-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Spot ID">{{ selectedSpot.id }}</el-descriptions-item>
          <el-descriptions-item label="Zone">{{ selectedSpot.zone }}</el-descriptions-item>
          <el-descriptions-item label="Type">
            <el-tag :type="getSpotTypeTag(selectedSpot.status)" size="small">{{ getSpotTypeLabel(selectedSpot.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="selectedSpot.status === 'available' ? 'success' : (selectedSpot.status === 'occupied' ? 'danger' : 'warning')" size="small">
              {{ selectedSpot.status === 'available' ? 'Available' : (selectedSpot.status === 'occupied' ? 'Occupied' : selectedSpot.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Current Vehicle" v-if="selectedSpot.currentVehicle">{{ selectedSpot.currentVehicle }}</el-descriptions-item>
          <el-descriptions-item label="Parked Since" v-if="selectedSpot.parkedSince">{{ selectedSpot.parkedSince }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Transaction Detail Dialog -->
    <el-dialog v-model="transDetailDialogVisible" :title="`Transaction ${selectedTransaction?.id}`" width="600px">
      <div v-if="selectedTransaction" class="transaction-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Vehicle Number">{{ selectedTransaction.vehicleNumber }}</el-descriptions-item>
          <el-descriptions-item label="Spot ID">{{ selectedTransaction.spotId }}</el-descriptions-item>
          <el-descriptions-item label="Zone">{{ selectedTransaction.zone }}</el-descriptions-item>
          <el-descriptions-item label="Entry Time">{{ selectedTransaction.entryTime }}</el-descriptions-item>
          <el-descriptions-item label="Exit Time">{{ selectedTransaction.exitTime || 'In progress' }}</el-descriptions-item>
          <el-descriptions-item label="Duration">{{ selectedTransaction.duration }}</el-descriptions-item>
          <el-descriptions-item label="Amount">${{ selectedTransaction.amount }}</el-descriptions-item>
          <el-descriptions-item label="Payment Method">{{ selectedTransaction.paymentMethod }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="selectedTransaction.status === 'active' ? 'success' : 'info'" size="small">
              {{ selectedTransaction.status === 'active' ? 'Active' : 'Completed' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="transDetailDialogVisible = false">Close</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Place, CircleCheck, Loading, Timer, Download, Refresh,
  RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading parking data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading parking data...',
  'Fetching occupancy metrics...',
  'Loading zone map...',
  'Analyzing traffic patterns...',
  'Almost ready...'
]

// ==================== Types ====================
interface ParkingSpot {
  id: string
  number: string
  zone: string
  status: 'available' | 'occupied' | 'reserved' | 'ev' | 'disabled'
  currentVehicle?: string
  parkedSince?: string
}

interface ParkingTransaction {
  id: string
  vehicleNumber: string
  spotId: string
  zone: string
  entryTime: string
  exitTime: string | null
  duration: string
  amount: number
  paymentMethod: string
  status: string
}

// ==================== Mock Data ====================
const zones = ['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E']

// Generate zone map
const generateZoneMap = (): { row: string; spots: ParkingSpot[] }[] => {
  const rows = ['A', 'B', 'C', 'D', 'E']
  const zoneMap = []
  let spotCounter = 1

  for (const row of rows) {
    const spots = []
    for (let i = 1; i <= 12; i++) {
      const spotNumber = `${row}${String(i).padStart(2, '0')}`
      let status: ParkingSpot['status'] = 'available'
      const random = Math.random()
      if (random < 0.55) status = 'available'
      else if (random < 0.8) status = 'occupied'
      else if (random < 0.88) status = 'ev'
      else if (random < 0.94) status = 'disabled'
      else status = 'reserved'

      spots.push({
        id: `SPOT-${String(spotCounter).padStart(4, '0')}`,
        number: spotNumber,
        zone: `Zone ${row}`,
        status: status,
        currentVehicle: status === 'occupied' ? `SGD${Math.floor(Math.random() * 9000 + 1000)}` : undefined,
        parkedSince: status === 'occupied' ? `${Math.floor(Math.random() * 3) + 1} hours ago` : undefined
      })
      spotCounter++
    }
    zoneMap.push({ row: `Zone ${row}`, spots })
  }
  return zoneMap
}

const zoneMap = ref(generateZoneMap())

// Generate transactions
const generateTransactions = (): ParkingTransaction[] => {
  const transactions = []
  const vehicles = ['SGD1234', 'SGD5678', 'SGA9876', 'SGB5432', 'SGC1111', 'SGD2222', 'SGE3333', 'SGF4444', 'SGG5555', 'SGH6666']
  const paymentMethods = ['Credit Card', 'PayNow', 'Cash', 'Season Pass', 'Mobile App']

  for (let i = 0; i < 50; i++) {
    const date = new Date()
    date.setDate(date.getDate() - Math.floor(Math.random() * 7))
    date.setHours(Math.floor(Math.random() * 24), Math.floor(Math.random() * 60))
    const entryTime = date.toISOString().replace('T', ' ').slice(0, 16)

    const isActive = Math.random() < 0.15
    let exitTime = null
    let duration = ''
    let amount = 0

    if (!isActive) {
      const exitDate = new Date(date)
      exitDate.setHours(date.getHours() + Math.floor(Math.random() * 4) + 1)
      exitTime = exitDate.toISOString().replace('T', ' ').slice(0, 16)
      const hoursDiff = Math.ceil((exitDate.getTime() - date.getTime()) / (1000 * 60 * 60))
      duration = `${hoursDiff}h ${Math.floor(Math.random() * 60)}m`
      amount = hoursDiff * 1.5 + Math.random() * 2
    } else {
      const hoursElapsed = Math.floor(Math.random() * 3) + 1
      duration = `${hoursElapsed}h ${Math.floor(Math.random() * 60)}m (ongoing)`
      amount = 0
    }

    transactions.push({
      id: `TXN-${String(i + 1).padStart(6, '0')}`,
      vehicleNumber: vehicles[Math.floor(Math.random() * vehicles.length)] + (Math.random() > 0.5 ? `-${Math.floor(Math.random() * 9)}` : ''),
      spotId: `SPOT-${String(Math.floor(Math.random() * 60) + 1).padStart(4, '0')}`,
      zone: zones[Math.floor(Math.random() * zones.length)],
      entryTime: entryTime,
      exitTime: exitTime,
      duration: duration,
      amount: parseFloat(amount.toFixed(2)),
      paymentMethod: paymentMethods[Math.floor(Math.random() * paymentMethods.length)],
      status: isActive ? 'active' : 'completed'
    })
  }

  return transactions.sort((a, b) => b.entryTime.localeCompare(a.entryTime))
}

const transactions = ref<ParkingTransaction[]>(generateTransactions())

// ==================== State ====================
const dateRange = ref<Date[] | null>(null)
const zoneFilter = ref('')
const spotTypeFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const transDetailDialogVisible = ref(false)
const selectedSpot = ref<ParkingSpot | null>(null)
const selectedTransaction = ref<ParkingTransaction | null>(null)

// Chart refs
let occupancyChart: echarts.ECharts | null = null
let zoneChart: echarts.ECharts | null = null
let trafficChart: echarts.ECharts | null = null
let durationChart: echarts.ECharts | null = null

const occupancyChartEl = ref<HTMLElement | null>(null)
const zoneChartEl = ref<HTMLElement | null>(null)
const trafficChartEl = ref<HTMLElement | null>(null)
const durationChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  let totalSpots = 0
  let availableSpots = 0
  let occupiedSpots = 0

  zoneMap.value.forEach(row => {
    row.spots.forEach(spot => {
      totalSpots++
      if (spot.status === 'available') availableSpots++
      else if (spot.status === 'occupied') occupiedSpots++
    })
  })

  const occupancyRate = Math.round((occupiedSpots / totalSpots) * 100)
  const avgParkingDuration = 78

  return {
    totalSpots,
    availableSpots,
    occupiedSpots,
    occupancyRate,
    availableChange: 5,
    avgParkingDuration,
    durationChange: 8
  }
})

const metrics = computed(() => {
  const peakOccupancy = 92
  const turnoverRate = 3.2
  const evChargingUsage = 45
  const dailyRevenue = 2.8

  return {
    peakOccupancy,
    peakTime: '10:30',
    turnoverRate,
    turnoverGrowth: 12,
    evChargingUsage,
    dailyRevenue,
    revenueGrowth: 8
  }
})

const filteredTransactions = computed(() => {
  let filtered = [...transactions.value]

  if (zoneFilter.value) {
    filtered = filtered.filter(t => t.zone === zoneFilter.value)
  }

  if (dateRange.value && dateRange.value.length === 2) {
    const [start, end] = dateRange.value
    filtered = filtered.filter(t => {
      const entryDate = new Date(t.entryTime)
      return entryDate >= start && entryDate <= end
    })
  }

  return filtered
})

const totalRecords = computed(() => filteredTransactions.value.length)

const paginatedTransactions = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredTransactions.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getSpotTypeLabel = (type: string): string => {
  const map: Record<string, string> = {
    available: 'Regular', occupied: 'Regular', reserved: 'Reserved',
    ev: 'EV Charging', disabled: 'Disabled'
  }
  return map[type] || type
}

const getSpotTypeTag = (type: string): string => {
  const map: Record<string, string> = {
    available: 'success', occupied: 'danger', reserved: 'warning',
    ev: 'primary', disabled: 'info'
  }
  return map[type] || 'info'
}

const resetFilters = () => {
  zoneFilter.value = ''
  spotTypeFilter.value = ''
  dateRange.value = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const showSpotDetail = (spot: ParkingSpot) => {
  selectedSpot.value = spot
  detailDialogVisible.value = true
}

const viewTransactionDetail = (transaction: ParkingTransaction) => {
  selectedTransaction.value = transaction
  transDetailDialogVisible.value = true
}

const viewAllTransactions = () => {
  ElMessage.info('Viewing all transactions')
}

// ==================== Chart Functions ====================
const initOccupancyChart = () => {
  if (!occupancyChartEl.value) return
  if (occupancyChart) {
    occupancyChart.dispose()
    occupancyChart = null
  }

  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const occupancyData = [35, 30, 28, 25, 22, 20, 25, 45, 68, 82, 88, 85, 78, 75, 72, 70, 75, 80, 78, 72, 65, 55, 45, 38]

  occupancyChart = echarts.init(occupancyChartEl.value)
  occupancyChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: hours, axisLabel: { rotate: 45, interval: 3 } },
    yAxis: { type: 'value', name: 'Occupancy (%)', max: 100 },
    series: [{
      type: 'line',
      data: occupancyData,
      smooth: true,
      lineStyle: { color: '#3b82f6', width: 3 },
      symbol: 'circle',
      symbolSize: 4,
      areaStyle: { opacity: 0.1 },
      label: { show: true, position: 'top', formatter: '{c}%', fontSize: 10, interval: 3 }
    }]
  })
}

const initZoneChart = () => {
  if (!zoneChartEl.value) return
  if (zoneChart) {
    zoneChart.dispose()
    zoneChart = null
  }

  const zoneOccupancy = zones.map(zone => {
    let total = 0
    let occupied = 0
    zoneMap.value.forEach(row => {
      if (row.row === zone) {
        row.spots.forEach(spot => {
          total++
          if (spot.status === 'occupied') occupied++
        })
      }
    })
    return Math.round((occupied / total) * 100)
  })

  zoneChart = echarts.init(zoneChartEl.value)
  zoneChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: zones },
    yAxis: { type: 'value', name: 'Occupancy (%)', max: 100 },
    series: [{
      type: 'bar',
      data: zoneOccupancy,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value < 50) return '#22c55e'
          if (value < 75) return '#f59e0b'
          return '#ef4444'
        }
      },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initTrafficChart = () => {
  if (!trafficChartEl.value) return
  if (trafficChart) {
    trafficChart.dispose()
    trafficChart = null
  }

  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const entries = [12, 8, 5, 3, 2, 5, 25, 65, 85, 72, 58, 45, 38, 35, 42, 55, 68, 75, 62, 48, 35, 28, 18, 10]
  const exits = [5, 3, 2, 2, 3, 8, 18, 35, 55, 68, 62, 55, 48, 42, 38, 45, 58, 72, 68, 55, 42, 32, 22, 15]

  trafficChart = echarts.init(trafficChartEl.value)
  trafficChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Entries', 'Exits'], bottom: 0 },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: hours, axisLabel: { rotate: 45, interval: 3 } },
    yAxis: { type: 'value', name: 'Number of Vehicles' },
    series: [
      { name: 'Entries', type: 'line', data: entries, lineStyle: { color: '#22c55e', width: 2 }, symbol: 'circle', areaStyle: { opacity: 0.1 } },
      { name: 'Exits', type: 'line', data: exits, lineStyle: { color: '#ef4444', width: 2 }, symbol: 'circle', areaStyle: { opacity: 0.1 } }
    ]
  })
}

const initDurationChart = () => {
  if (!durationChartEl.value) return
  if (durationChart) {
    durationChart.dispose()
    durationChart = null
  }

  const ranges = ['<30 min', '30-60 min', '1-2 hrs', '2-4 hrs', '4-8 hrs', '>8 hrs']
  const percentages = [15, 25, 30, 18, 8, 4]

  durationChart = echarts.init(durationChartEl.value)
  durationChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
    legend: { orient: 'vertical', left: 'left', data: ranges },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: ranges.map((r, i) => ({ name: r, value: percentages[i] })),
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initOccupancyChart()
    initZoneChart()
    initTrafficChart()
    initDurationChart()
  })
}

// ==================== Actions ====================
const exportData = () => {
  ElMessage.success('Exporting parking data...')
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
  zoneMap.value = generateZoneMap()
  transactions.value = generateTransactions()
  refreshCharts()
  ElMessage.success('Data refreshed')
}

// 窗口缩放处理
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    const charts = [occupancyChart, zoneChart, trafficChart, durationChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([zoneFilter, spotTypeFilter, dateRange], () => {
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
  const charts = [occupancyChart, zoneChart, trafficChart, durationChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.parking-dashboard-page {
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

/* Zone Map Section */
.zone-map-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.zone-map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.section-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.zone-legend {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #64748b;
}

.legend-dot {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 3px;
  margin-right: 6px;
}

.legend-dot.available { background: #22c55e; }
.legend-dot.occupied { background: #ef4444; }
.legend-dot.reserved { background: #f59e0b; }
.legend-dot.ev { background: #3b82f6; }
.legend-dot.disabled { background: #8b5cf6; }

.zone-map {
  overflow-x: auto;
}

.zone-row {
  display: flex;
  margin-bottom: 16px;
  align-items: center;
}

.zone-label {
  width: 70px;
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
}

.zone-spots {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  flex: 1;
}

.parking-spot {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.parking-spot:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.parking-spot.available { background: #dcfce7; border: 2px solid #22c55e; color: #166534; }
.parking-spot.occupied { background: #fee2e2; border: 2px solid #ef4444; color: #991b1b; }
.parking-spot.reserved { background: #fef3c7; border: 2px solid #f59e0b; color: #92400e; }
.parking-spot.ev { background: #eef2ff; border: 2px solid #3b82f6; color: #1e40af; }
.parking-spot.disabled { background: #f3e8ff; border: 2px solid #8b5cf6; color: #5b21b6; }

.spot-number {
  font-size: 12px;
  font-weight: 600;
}

.spot-icon {
  font-size: 14px;
  margin-top: 2px;
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

/* Spot Detail */
.spot-detail {
  padding: 8px;
}

/* Responsive */
@media (max-width: 1000px) {
  .stats-grid, .metrics-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-row {
    flex-direction: column;
  }
  .parking-spot {
    width: 50px;
    height: 50px;
  }
  .spot-number {
    font-size: 10px;
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
  .zone-legend {
    flex-wrap: wrap;
  }
  .parking-spot {
    width: 45px;
    height: 45px;
  }
  .zone-label {
    width: 55px;
    font-size: 12px;
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
  padding: 20px;
}
:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}
</style>