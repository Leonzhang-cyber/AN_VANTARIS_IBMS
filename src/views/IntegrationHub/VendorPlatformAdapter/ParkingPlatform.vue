<script setup lang="ts">
import { ref, onMounted, computed, watch, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  OfficeBuilding, Monitor, Van, BellFilled,
  Refresh, Connection, Setting, VideoPlay, Search,
  DataLine, Clock, Ticket, Wallet, User
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing Parking SDK...',
  'Connecting to parking system...',
  'Syncing gate controllers...',
  'Loading occupancy data...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const gateControlVisible = ref(false)
const configDrawerVisible = ref(false)
const vehicleDetailsVisible = ref(false)
const occupancyChartRef = ref(null)
const revenueChartRef = ref(null)
const durationChartRef = ref(null)

let occupancyChart: echarts.ECharts | null = null
let revenueChart: echarts.ECharts | null = null
let durationChart: echarts.ECharts | null = null

const selectedGate = ref<any>(null)
const selectedVehicle = ref<any>(null)
const currentChartPeriod = ref('week')

// Statistics data
const stats = reactive({
  totalSpaces: 1250,
  occupiedSpaces: 847,
  availableSpaces: 403,
  occupancyRate: 67.8,
  totalGates: 8,
  activeGates: 7,
  todayVehicles: 342,
  todayRevenue: 2840.50,
  monthlyVehicles: 8950,
  monthlyRevenue: 72450.00,
  vipSpaces: 50,
  evSpaces: 30,
  disabledSpaces: 25
})

// Gate devices
const gates = ref([
  { id: 'G001', name: 'Main Entrance - In', location: 'Main Gate', ip: '192.168.5.101', status: 'online', type: 'Entry', lastHeartbeat: '2024-01-15 10:23:45', todayVehicles: 142, firmware: 'v2.1.0' },
  { id: 'G002', name: 'Main Entrance - Out', location: 'Main Gate', ip: '192.168.5.102', status: 'online', type: 'Exit', lastHeartbeat: '2024-01-15 10:22:30', todayVehicles: 138, firmware: 'v2.1.0' },
  { id: 'G003', name: 'North Entrance - In', location: 'North Gate', ip: '192.168.5.103', status: 'online', type: 'Entry', lastHeartbeat: '2024-01-15 10:24:12', todayVehicles: 89, firmware: 'v2.0.5' },
  { id: 'G004', name: 'North Entrance - Out', location: 'North Gate', ip: '192.168.5.104', status: 'online', type: 'Exit', lastHeartbeat: '2024-01-15 10:20:00', todayVehicles: 87, firmware: 'v2.0.5' },
  { id: 'G005', name: 'South Entrance - In', location: 'South Gate', ip: '192.168.5.105', status: 'online', type: 'Entry', lastHeartbeat: '2024-01-15 10:23:00', todayVehicles: 76, firmware: 'v2.1.0' },
  { id: 'G006', name: 'South Entrance - Out', location: 'South Gate', ip: '192.168.5.106', status: 'offline', type: 'Exit', lastHeartbeat: '2024-01-14 18:30:00', todayVehicles: 0, firmware: 'v2.0.5' },
  { id: 'G007', name: 'VIP Entrance', location: 'VIP Area', ip: '192.168.5.107', status: 'online', type: 'Entry/Exit', lastHeartbeat: '2024-01-15 10:22:15', todayVehicles: 35, firmware: 'v2.1.2' },
  { id: 'G008', name: 'Truck Entrance', location: 'Loading Dock', ip: '192.168.5.108', status: 'online', type: 'Entry/Exit', lastHeartbeat: '2024-01-15 10:21:30', todayVehicles: 28, firmware: 'v2.0.8' }
])

// Recent vehicles
const recentVehicles = ref([
  { plate: 'SBA1234', type: 'Car', entryTime: '2024-01-15 10:23:45', exitTime: '', status: 'Parked', gate: 'Main Entrance - In', space: 'A-124', duration: '1h 23m', amount: 0 },
  { plate: 'SBB5678', type: 'SUV', entryTime: '2024-01-15 10:15:30', exitTime: '', status: 'Parked', gate: 'North Entrance - In', space: 'B-056', duration: '1h 31m', amount: 0 },
  { plate: 'SBC9012', type: 'Motorcycle', entryTime: '2024-01-15 10:08:12', exitTime: '2024-01-15 10:45:23', status: 'Exited', gate: 'South Entrance - In', space: 'M-012', duration: '37m', amount: 2.50 },
  { plate: 'SBD3456', type: 'Car', entryTime: '2024-01-15 09:45:00', exitTime: '', status: 'Parked', gate: 'Main Entrance - In', space: 'A-089', duration: '2h 1m', amount: 0 },
  { plate: 'SBE7890', type: 'Truck', entryTime: '2024-01-15 09:30:22', exitTime: '2024-01-15 11:15:45', status: 'Exited', gate: 'Truck Entrance', space: 'T-003', duration: '1h 45m', amount: 15.00 },
  { plate: 'SBF2345', type: 'EV', entryTime: '2024-01-15 08:55:33', exitTime: '', status: 'Parked', gate: 'VIP Entrance', space: 'E-008', duration: '2h 51m', amount: 0 },
  { plate: 'SBG6789', type: 'Car', entryTime: '2024-01-15 08:30:15', exitTime: '2024-01-15 11:00:00', status: 'Exited', gate: 'Main Entrance - In', space: 'A-045', duration: '2h 30m', amount: 5.00 },
  { plate: 'SBH0123', type: 'SUV', entryTime: '2024-01-15 07:45:00', exitTime: '', status: 'Parked', gate: 'North Entrance - In', space: 'B-112', duration: '4h 1m', amount: 0 },
  { plate: 'SBI4567', type: 'Car', entryTime: '2024-01-15 07:20:30', exitTime: '2024-01-15 10:30:00', status: 'Exited', gate: 'South Entrance - In', space: 'A-234', duration: '3h 10m', amount: 6.00 },
  { plate: 'SBJ8901', type: 'Motorcycle', entryTime: '2024-01-15 07:00:00', exitTime: '', status: 'Parked', gate: 'Main Entrance - In', space: 'M-045', duration: '4h 46m', amount: 0 }
])

// Parking spaces by zone
const zones = ref([
  { name: 'Zone A', total: 350, occupied: 245, available: 105, rate: 70 },
  { name: 'Zone B', total: 300, occupied: 198, available: 102, rate: 66 },
  { name: 'Zone C', total: 280, occupied: 167, available: 113, rate: 59.6 },
  { name: 'Zone D', total: 220, occupied: 156, available: 64, rate: 70.9 },
  { name: 'VIP Zone', total: 50, occupied: 42, available: 8, rate: 84 },
  { name: 'EV Zone', total: 30, occupied: 22, available: 8, rate: 73.3 },
  { name: 'Motorcycle', total: 20, occupied: 17, available: 3, rate: 85 }
])

// Platform configuration
const platformConfig = ref({
  host: 'https://parking-platform.example.com',
  apiKey: '',
  databaseUrl: '',
  syncInterval: 900,
  rates: {
    car: 2.50,
    suv: 3.00,
    truck: 8.00,
    motorcycle: 1.00,
    ev: 2.00
  },
  freeMinutes: 15,
  maxDailyCharge: 20.00
})

// Gate control form
const gateControlForm = ref({
  operation: 'open',
  duration: 10,
  message: ''
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: recentVehicles.value.length
})

// Filtered vehicles
const filteredVehicles = computed(() => {
  let filtered = recentVehicles.value
  if (searchKeyword.value) {
    filtered = filtered.filter(v =>
        v.plate.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        v.type.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        v.gate.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  pagination.total = filtered.length
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// Watch for search keyword to reset pagination
watch(searchKeyword, () => {
  pagination.page = 1
})

// ==================== Loading Simulation ====================
onMounted(() => {
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 12 + 4
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
        initOccupancyChart()
        initRevenueChart()
        initDurationChart()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initOccupancyChart = () => {
  if (!occupancyChartRef.value) return

  occupancyChart = echarts.init(occupancyChartRef.value)
  occupancyChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['Occupied', 'Available'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: zones.value.map(z => z.name) },
    yAxis: { type: 'value', name: 'Spaces' },
    series: [
      { name: 'Occupied', type: 'bar', data: zones.value.map(z => z.occupied), itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] } },
      { name: 'Available', type: 'bar', data: zones.value.map(z => z.available), itemStyle: { color: '#67C23A', borderRadius: [4, 4, 0, 0] } }
    ]
  })
}

const initRevenueChart = () => {
  if (!revenueChartRef.value) return

  revenueChart = echarts.init(revenueChartRef.value)
  updateRevenueChart()
}

const updateRevenueChart = () => {
  const weekData = {
    xAxis: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    revenue: [1850, 1920, 2100, 2250, 2840, 3250, 2980],
    vehicles: [245, 258, 275, 290, 342, 385, 362]
  }

  const monthData = {
    xAxis: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    revenue: [14500, 15800, 17200, 18950],
    vehicles: [1980, 2150, 2350, 2470]
  }

  const data = currentChartPeriod.value === 'week' ? weekData : monthData

  revenueChart?.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Revenue ($)', 'Vehicles'], bottom: 0 },
    xAxis: { type: 'category', data: data.xAxis },
    yAxis: [{ type: 'value', name: 'Revenue ($)' }, { type: 'value', name: 'Vehicles' }],
    series: [
      { name: 'Revenue ($)', type: 'line', data: data.revenue, smooth: true, lineStyle: { color: '#E6A23C', width: 2 }, symbol: 'circle', symbolSize: 8, yAxisIndex: 0 },
      { name: 'Vehicles', type: 'line', data: data.vehicles, smooth: true, lineStyle: { color: '#67C23A', width: 2 }, symbol: 'diamond', symbolSize: 8, yAxisIndex: 1 }
    ]
  })
}

const initDurationChart = () => {
  if (!durationChartRef.value) return

  durationChart = echarts.init(durationChartRef.value)
  durationChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c})' },
    legend: { orient: 'vertical', left: 'left', data: ['< 30 min', '30 min - 1h', '1h - 2h', '2h - 4h', '> 4h'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { name: '< 30 min', value: 45, itemStyle: { color: '#67C23A' } },
        { name: '30 min - 1h', value: 89, itemStyle: { color: '#409EFF' } },
        { name: '1h - 2h', value: 156, itemStyle: { color: '#E6A23C' } },
        { name: '2h - 4h', value: 98, itemStyle: { color: '#F56C6C' } },
        { name: '> 4h', value: 67, itemStyle: { color: '#909399' } }
      ],
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })
}

const handleResize = () => {
  occupancyChart?.resize()
  revenueChart?.resize()
  durationChart?.resize()
}

// ==================== Actions ====================
const formatTime = (time: string) => {
  return time
}

const formatCurrency = (amount: number) => {
  return `$${amount.toFixed(2)}`
}

const toggleChartPeriod = () => {
  currentChartPeriod.value = currentChartPeriod.value === 'week' ? 'month' : 'week'
  updateRevenueChart()
}

const syncDevices = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1500))
    ElMessage.success('Gate synchronization completed successfully')
  } catch (error) {
    ElMessage.error('Sync failed')
  } finally {
    loading.value = false
  }
}

const testConnection = async () => {
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('Parking platform connection successful')
  } catch (error) {
    ElMessage.error('Connection failed')
  }
}

const openConfigDrawer = () => {
  configDrawerVisible.value = true
}

const saveConfig = async () => {
  try {
    await new Promise(resolve => setTimeout(resolve, 800))
    ElMessage.success('Configuration saved successfully')
    configDrawerVisible.value = false
  } catch (error) {
    ElMessage.error('Failed to save configuration')
  }
}

const openGateControl = (gate: any) => {
  selectedGate.value = gate
  gateControlForm.value = { operation: 'open', duration: 10, message: '' }
  gateControlVisible.value = true
}

const executeGateControl = async () => {
  if (selectedGate.value) {
    const action = gateControlForm.value.operation === 'open' ? 'Opening' : 'Closing'
    ElMessage.info(`${action} gate ${selectedGate.value.name}...`)
    await new Promise(resolve => setTimeout(resolve, 1500))
    ElMessage.success(`Gate ${selectedGate.value.name} ${gateControlForm.value.operation}ed successfully`)
    gateControlVisible.value = false
  }
}

const viewVehicleDetails = (vehicle: any) => {
  selectedVehicle.value = vehicle
  vehicleDetailsVisible.value = true
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const refreshGates = () => {
  syncDevices()
}

const getOccupancyColor = (rate: number) => {
  if (rate < 50) return '#67C23A'
  if (rate < 80) return '#E6A23C'
  return '#F56C6C'
}
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
          <span class="loading-title">Loading Parking Platform</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Parking Management System Adapter</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="parking-platform-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h2>Parking Platform Adapter</h2>
        <el-tag type="success" effect="dark">Connected</el-tag>
      </div>
      <div class="header-stats">
        <el-tag type="info" effect="plain">System Version: v3.2.1</el-tag>
      </div>
    </div>

    <!-- Stat Cards Row 1 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon parking-icon">
            <el-icon><OfficeBuilding /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalSpaces }}</div>
            <div class="stat-label">Total Spaces</div>
            <div class="stat-trend">
              <el-progress :percentage="stats.occupancyRate" :color="getOccupancyColor(stats.occupancyRate)" :stroke-width="6" />
              <span class="occupancy-text">{{ stats.occupancyRate }}% Occupied</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon available-icon">
            <el-icon><Monitor /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.availableSpaces }}</div>
            <div class="stat-label">Available Spaces</div>
            <div class="stat-sub-value">{{ stats.occupiedSpaces }} Occupied</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon gate-icon">
            <el-icon><Van /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.activeGates }}/{{ stats.totalGates }}</div>
            <div class="stat-label">Active Gates</div>
            <div class="stat-trend">
              <span class="gate-text">{{ stats.activeGates === stats.totalGates ? 'All operational' : `${stats.totalGates - stats.activeGates} offline` }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon vehicle-icon">
            <el-icon><Ticket /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.todayVehicles }}</div>
            <div class="stat-label">Today's Vehicles</div>
            <div class="stat-trend">
              <span class="revenue-text">Revenue: {{ formatCurrency(stats.todayRevenue) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Stat Cards Row 2 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon vip-icon">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.vipSpaces }}</div>
            <div class="stat-label">VIP Spaces</div>
            <div class="stat-sub-value">{{ stats.vipSpaces - 8 }} Available</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon ev-icon">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.evSpaces }}</div>
            <div class="stat-label">EV Charging</div>
            <div class="stat-sub-value">{{ stats.evSpaces - 8 }} Available</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon disabled-icon">
            <el-icon><Setting /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.disabledSpaces }}</div>
            <div class="stat-label">Disabled Spaces</div>
            <div class="stat-sub-value">{{ stats.disabledSpaces - 3 }} Available</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon monthly-icon">
            <el-icon><Wallet /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.monthlyVehicles.toLocaleString() }}</div>
            <div class="stat-label">Monthly Vehicles</div>
            <div class="stat-trend">
              <span class="monthly-revenue">{{ formatCurrency(stats.monthlyRevenue) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Chart Section -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Parking Occupancy by Zone</span>
              <el-button text type="primary" @click="syncDevices">Refresh</el-button>
            </div>
          </template>
          <div ref="occupancyChartRef" class="chart" style="height: 300px"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Revenue & Vehicle Trend</span>
              <el-button text type="primary" @click="toggleChartPeriod">
                {{ currentChartPeriod === 'week' ? 'This Week' : 'This Month' }}
              </el-button>
            </div>
          </template>
          <div ref="revenueChartRef" class="chart" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Parking Duration Distribution</span>
              <el-button text type="primary">Details</el-button>
            </div>
          </template>
          <div ref="durationChartRef" class="chart" style="height: 280px"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="never" class="gate-list-card">
          <template #header>
            <div class="card-header">
              <span>Gate Status</span>
              <el-button text type="primary" @click="refreshGates">Sync Gates</el-button>
            </div>
          </template>
          <div class="gate-list">
            <div v-for="gate in gates" :key="gate.id" class="gate-item">
              <div class="gate-info">
                <span class="gate-name">{{ gate.name }}</span>
                <span class="gate-location">{{ gate.location }}</span>
                <el-tag :type="gate.status === 'online' ? 'success' : 'danger'" size="small">
                  {{ gate.status === 'online' ? 'Online' : 'Offline' }}
                </el-tag>
              </div>
              <div class="gate-stats">
                <span class="gate-vehicles">{{ gate.todayVehicles }} vehicles today</span>
                <el-button size="small" type="primary" link @click="openGateControl(gate)">
                  <el-icon><VideoPlay /></el-icon> Control
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Recent Vehicles Table -->
    <el-card shadow="never" class="vehicle-table-card">
      <template #header>
        <div class="table-header">
          <span>Recent Vehicles</span>
          <div class="table-actions">
            <el-input
                v-model="searchKeyword"
                placeholder="Search by plate, type or gate..."
                :prefix-icon="Search"
                style="width: 250px"
                clearable
            />
            <el-button type="primary" @click="syncDevices" :loading="loading">
              <el-icon><Refresh /></el-icon>
              Refresh
            </el-button>
            <el-button @click="openConfigDrawer">
              <el-icon><Setting /></el-icon>
              Platform Settings
            </el-button>
            <el-button @click="testConnection">
              <el-icon><Connection /></el-icon>
              Test Connection
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredVehicles" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="plate" label="License Plate" width="130" />
        <el-table-column prop="type" label="Vehicle Type" width="110" />
        <el-table-column prop="entryTime" label="Entry Time" width="160" />
        <el-table-column prop="exitTime" label="Exit Time" width="160">
          <template #default="{ row }">
            {{ row.exitTime || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="Status" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Parked' ? 'primary' : 'info'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="gate" label="Gate" width="150" />
        <el-table-column prop="space" label="Space" width="80" />
        <el-table-column prop="duration" label="Duration" width="90" />
        <el-table-column prop="amount" label="Amount" width="80">
          <template #default="{ row }">
            {{ row.amount > 0 ? formatCurrency(row.amount) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewVehicleDetails(row)">
              <el-icon><DataLine /></el-icon> Details
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- Gate Control Dialog -->
    <el-dialog v-model="gateControlVisible" :title="`Gate Control - ${selectedGate?.name}`" width="450px">
      <el-form :model="gateControlForm" label-width="100px">
        <el-form-item label="Operation">
          <el-radio-group v-model="gateControlForm.operation">
            <el-radio value="open">Open Gate</el-radio>
            <el-radio value="close">Close Gate</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Duration (s)" v-if="gateControlForm.operation === 'open'">
          <el-input-number v-model="gateControlForm.duration" :min="5" :max="60" />
        </el-form-item>
        <el-form-item label="Message">
          <el-input v-model="gateControlForm.message" placeholder="Optional message to display" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="gateControlVisible = false">Cancel</el-button>
        <el-button type="primary" @click="executeGateControl">Execute</el-button>
      </template>
    </el-dialog>

    <!-- Vehicle Details Dialog -->
    <el-dialog v-model="vehicleDetailsVisible" :title="`Vehicle Details - ${selectedVehicle?.plate}`" width="500px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="License Plate">{{ selectedVehicle?.plate }}</el-descriptions-item>
        <el-descriptions-item label="Vehicle Type">{{ selectedVehicle?.type }}</el-descriptions-item>
        <el-descriptions-item label="Entry Time">{{ selectedVehicle?.entryTime }}</el-descriptions-item>
        <el-descriptions-item label="Exit Time">{{ selectedVehicle?.exitTime || 'Not exited' }}</el-descriptions-item>
        <el-descriptions-item label="Gate">{{ selectedVehicle?.gate }}</el-descriptions-item>
        <el-descriptions-item label="Parking Space">{{ selectedVehicle?.space || '-' }}</el-descriptions-item>
        <el-descriptions-item label="Duration">{{ selectedVehicle?.duration }}</el-descriptions-item>
        <el-descriptions-item label="Amount">{{ selectedVehicle?.amount > 0 ? formatCurrency(selectedVehicle?.amount) : '-' }}</el-descriptions-item>
        <el-descriptions-item label="Status" :span="2">
          <el-tag :type="selectedVehicle?.status === 'Parked' ? 'primary' : 'info'">
            {{ selectedVehicle?.status }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- Platform Configuration Drawer -->
    <el-drawer v-model="configDrawerVisible" title="Platform Configuration" direction="rtl" size="500px">
      <el-form :model="platformConfig" label-width="140px">
        <el-form-item label="Platform URL">
          <el-input v-model="platformConfig.host" placeholder="https://your-parking-platform.com" />
        </el-form-item>
        <el-form-item label="API Key">
          <el-input v-model="platformConfig.apiKey" placeholder="Enter API key" />
        </el-form-item>
        <el-form-item label="Database URL">
          <el-input v-model="platformConfig.databaseUrl" placeholder="Database connection string" />
        </el-form-item>
        <el-form-item label="Sync Interval">
          <el-select v-model="platformConfig.syncInterval">
            <el-option label="5 minutes" :value="300" />
            <el-option label="15 minutes" :value="900" />
            <el-option label="30 minutes" :value="1800" />
            <el-option label="1 hour" :value="3600" />
          </el-select>
        </el-form-item>
        <el-form-item label="Free Minutes">
          <el-input-number v-model="platformConfig.freeMinutes" :min="0" :max="60" />
        </el-form-item>
        <el-form-item label="Max Daily Charge">
          <el-input-number v-model="platformConfig.maxDailyCharge" :min="5" :max="50" :step="0.5" />
        </el-form-item>
        <el-divider>Rate Settings</el-divider>
        <el-form-item label="Car (per hour)">
          <el-input-number v-model="platformConfig.rates.car" :min="0.5" :max="10" :step="0.5" />
        </el-form-item>
        <el-form-item label="SUV (per hour)">
          <el-input-number v-model="platformConfig.rates.suv" :min="0.5" :max="10" :step="0.5" />
        </el-form-item>
        <el-form-item label="Truck (per hour)">
          <el-input-number v-model="platformConfig.rates.truck" :min="1" :max="20" :step="1" />
        </el-form-item>
        <el-form-item label="Motorcycle">
          <el-input-number v-model="platformConfig.rates.motorcycle" :min="0.5" :max="5" :step="0.5" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveConfig">Save Configuration</el-button>
          <el-button @click="testConnection">Test Connection</el-button>
        </el-form-item>
      </el-form>
    </el-drawer>
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
.parking-platform-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e4e7ed;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  color: #303133;
}

.stat-cards {
  margin: 20px 0;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 10px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
}

.parking-icon {
  background-color: #e6f7ff;
  color: #409eff;
}

.available-icon {
  background-color: #f0f9ff;
  color: #67c23a;
}

.gate-icon {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.vehicle-icon {
  background-color: #fef0f0;
  color: #f56c6c;
}

.vip-icon {
  background-color: #f3e8ff;
  color: #9b59b6;
}

.ev-icon {
  background-color: #e8f8f5;
  color: #1abc9c;
}

.disabled-icon {
  background-color: #fdeded;
  color: #e74c3c;
}

.monthly-icon {
  background-color: #e8f4fd;
  color: #3498db;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.stat-sub-value {
  font-size: 12px;
  color: #67c23a;
  margin-top: 2px;
}

.stat-trend {
  margin-top: 8px;
}

.occupancy-text {
  font-size: 12px;
  color: #409eff;
  margin-left: 8px;
}

.gate-text {
  font-size: 12px;
  color: #e6a23c;
}

.revenue-text {
  font-size: 12px;
  color: #67c23a;
}

.monthly-revenue {
  font-size: 12px;
  color: #409eff;
}

.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  height: 370px;
}

.gate-list-card {
  height: 370px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.gate-list {
  max-height: 300px;
  overflow-y: auto;
}

.gate-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 10px;
  border-bottom: 1px solid #ebeef5;
}

.gate-item:last-child {
  border-bottom: none;
}

.gate-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.gate-name {
  font-weight: 500;
  color: #303133;
}

.gate-location {
  font-size: 12px;
  color: #909399;
}

.gate-stats {
  display: flex;
  align-items: center;
  gap: 12px;
}

.gate-vehicles {
  font-size: 12px;
  color: #606266;
}

.vehicle-table-card {
  margin-top: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.table-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.chart {
  width: 100%;
}

:deep(.el-card__header) {
  border-bottom: 1px solid #ebeef5;
  padding: 15px 20px;
}

:deep(.el-card__body) {
  padding: 20px;
}

@media (max-width: 1200px) {
  .table-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .table-actions {
    width: 100%;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .gate-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>