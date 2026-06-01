<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted, computed } from 'vue'
import {
  Search, RefreshRight, Warning, CircleCheck, Clock,
  TrendCharts, Monitor, Connection, DataAnalysis,
  Document, Setting, More, ArrowUp, ArrowDown,
  VideoCamera, Histogram
} from "@element-plus/icons-vue"
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Connecting to battery monitoring system...',
  'Loading battery health data...',
  'Analyzing battery performance...'
]

// Battery Units Data
const batteryUnits = ref([
  {
    id: 'BAT-01-DC-A-1',
    name: 'UPS Battery String A1',
    location: 'Data Center A - UPS Room',
    type: 'VRLA',
    voltage: 432,
    current: 125,
    temperature: 28,
    stateOfHealth: 92,
    stateOfCharge: 88,
    resistance: 4.2,
    cycleCount: 342,
    status: 'warning',
    manufacturer: 'EnerSys',
    installDate: '2023-06-15',
    expectedLife: 60,
    alerts: [
      { severity: 'warning', message: 'Internal resistance increasing', timestamp: '2025-01-16 08:30:00' },
      { severity: 'info', message: 'Temperature above optimal', timestamp: '2025-01-15 14:20:00' }
    ],
    cells: [
      { id: 1, voltage: 12.8, temperature: 28, resistance: 4.1, status: 'good' },
      { id: 2, voltage: 12.7, temperature: 28, resistance: 4.2, status: 'good' },
      { id: 3, voltage: 12.6, temperature: 29, resistance: 4.4, status: 'warning' },
      { id: 4, voltage: 12.8, temperature: 28, resistance: 4.1, status: 'good' }
    ]
  },
  {
    id: 'BAT-01-DC-A-2',
    name: 'UPS Battery String A2',
    location: 'Data Center A - UPS Room',
    type: 'VRLA',
    voltage: 428,
    current: 118,
    temperature: 31,
    stateOfHealth: 78,
    stateOfCharge: 82,
    resistance: 6.8,
    cycleCount: 456,
    status: 'critical',
    manufacturer: 'EnerSys',
    installDate: '2023-06-15',
    expectedLife: 60,
    alerts: [
      { severity: 'critical', message: 'Battery health critical - replace soon', timestamp: '2025-01-14 10:15:00' },
      { severity: 'warning', message: 'High internal resistance detected', timestamp: '2025-01-13 09:45:00' },
      { severity: 'warning', message: 'Cell voltage imbalance', timestamp: '2025-01-12 16:30:00' }
    ],
    cells: [
      { id: 1, voltage: 12.5, temperature: 31, resistance: 6.5, status: 'warning' },
      { id: 2, voltage: 12.3, temperature: 32, resistance: 7.2, status: 'critical' },
      { id: 3, voltage: 12.6, temperature: 31, resistance: 6.6, status: 'warning' },
      { id: 4, voltage: 12.4, temperature: 31, resistance: 6.9, status: 'warning' }
    ]
  },
  {
    id: 'BAT-02-DC-B-1',
    name: 'UPS Battery String B1',
    location: 'Data Center B - UPS Room',
    type: 'Lithium-Ion',
    voltage: 438,
    current: 98,
    temperature: 25,
    stateOfHealth: 96,
    stateOfCharge: 94,
    resistance: 2.8,
    cycleCount: 128,
    status: 'healthy',
    manufacturer: 'Tesla',
    installDate: '2024-03-10',
    expectedLife: 120,
    alerts: [],
    cells: [
      { id: 1, voltage: 13.2, temperature: 25, resistance: 2.7, status: 'good' },
      { id: 2, voltage: 13.1, temperature: 25, resistance: 2.8, status: 'good' },
      { id: 3, voltage: 13.2, temperature: 25, resistance: 2.7, status: 'good' },
      { id: 4, voltage: 13.1, temperature: 25, resistance: 2.8, status: 'good' }
    ]
  },
  {
    id: 'BAT-03-DC-C-1',
    name: 'UPS Battery String C1',
    location: 'Data Center C - Power Room',
    type: 'VRLA',
    voltage: 435,
    current: 142,
    temperature: 29,
    stateOfHealth: 85,
    stateOfCharge: 86,
    resistance: 5.2,
    cycleCount: 278,
    status: 'warning',
    manufacturer: 'C&D Technologies',
    installDate: '2023-11-20',
    expectedLife: 60,
    alerts: [
      { severity: 'warning', message: 'SOH below 90%', timestamp: '2025-01-15 11:00:00' }
    ],
    cells: [
      { id: 1, voltage: 12.7, temperature: 29, resistance: 5.1, status: 'good' },
      { id: 2, voltage: 12.6, temperature: 29, resistance: 5.3, status: 'warning' },
      { id: 3, voltage: 12.7, temperature: 29, resistance: 5.2, status: 'good' },
      { id: 4, voltage: 12.6, temperature: 30, resistance: 5.4, status: 'warning' }
    ]
  },
  {
    id: 'BAT-04-DC-A-3',
    name: 'Stationary Battery A3',
    location: 'Data Center A - Battery Room',
    type: 'VRLA',
    voltage: 440,
    current: 88,
    temperature: 27,
    stateOfHealth: 98,
    stateOfCharge: 97,
    resistance: 3.1,
    cycleCount: 56,
    status: 'healthy',
    manufacturer: 'East Penn',
    installDate: '2024-08-01',
    expectedLife: 60,
    alerts: [],
    cells: [
      { id: 1, voltage: 12.9, temperature: 27, resistance: 3.0, status: 'good' },
      { id: 2, voltage: 12.9, temperature: 27, resistance: 3.1, status: 'good' },
      { id: 3, voltage: 12.8, temperature: 27, resistance: 3.1, status: 'good' },
      { id: 4, voltage: 12.9, temperature: 27, resistance: 3.0, status: 'good' }
    ]
  }
])

// Historical fault data
const faultHistory = ref([
  { id: 'BFLT-001', batteryId: 'BAT-01-DC-A-2', type: 'High Resistance', severity: 'critical', timestamp: '2025-01-10 14:23:00', resolved: '2025-01-11 09:30:00', description: 'Internal resistance exceeded 7mΩ threshold' },
  { id: 'BFLT-002', batteryId: 'BAT-01-DC-A-1', type: 'Temperature High', severity: 'warning', timestamp: '2025-01-08 09:15:00', resolved: '2025-01-08 14:20:00', description: 'Battery temperature reached 35°C' },
  { id: 'BFLT-003', batteryId: 'BAT-03-DC-C-1', type: 'Voltage Imbalance', severity: 'warning', timestamp: '2025-01-05 22:45:00', resolved: '2025-01-06 11:00:00', description: 'Cell voltage variance > 0.3V' },
  { id: 'BFLT-004', batteryId: 'BAT-01-DC-A-2', type: 'Low SOH', severity: 'critical', timestamp: '2025-01-03 15:30:00', resolved: '2025-01-04 10:15:00', description: 'State of Health dropped below 80%' }
])

// Trending data
const sohTrendData = ref([
  { month: 'Aug', soh: 98, temp: 26, resistance: 3.2 },
  { month: 'Sep', soh: 96, temp: 27, resistance: 3.5 },
  { month: 'Oct', soh: 94, temp: 28, resistance: 3.9 },
  { month: 'Nov', soh: 91, temp: 28, resistance: 4.3 },
  { month: 'Dec', soh: 88, temp: 29, resistance: 4.8 },
  { month: 'Jan', soh: 85, temp: 31, resistance: 5.2 }
])

// Performance metrics
const performanceMetrics = ref({
  avgSoh: 89.8,
  avgTemp: 28.5,
  criticalCount: 1,
  warningCount: 2,
  healthyCount: 2,
  totalBatteries: 5
})

// Selected battery for detail view
const selectedBattery = ref<any>(null)
const detailVisible = ref(false)
const historyVisible = ref(false)
const cellDetailVisible = ref(false)

// Filters
const searchKeyword = ref('')
const statusFilter = ref('all')
const typeFilter = ref('all')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const sohChartRef = ref<HTMLElement | null>(null)
const resistanceChartRef = ref<HTMLElement | null>(null)
let sohChart: echarts.ECharts | null = null
let resistanceChart: echarts.ECharts | null = null

const filteredBatteries = computed(() => {
  let filtered = batteryUnits.value

  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(b => b.status === statusFilter.value)
  }

  if (typeFilter.value !== 'all') {
    filtered = filtered.filter(b => b.type === typeFilter.value)
  }

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(b =>
        b.id.toLowerCase().includes(keyword) ||
        b.name.toLowerCase().includes(keyword) ||
        b.location.toLowerCase().includes(keyword)
    )
  }

  return filtered
})

const paginatedBatteries = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredBatteries.value.slice(start, end)
})

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
}

const getStatusColor = (status: string) => {
  switch(status) {
    case 'critical': return '#F56C6C'
    case 'warning': return '#E6A23C'
    case 'healthy': return '#67C23A'
    default: return '#909399'
  }
}

const getStatusText = (status: string) => {
  switch(status) {
    case 'critical': return 'Critical'
    case 'warning': return 'Warning'
    case 'healthy': return 'Healthy'
    default: return 'Unknown'
  }
}

const getSohColor = (soh: number) => {
  if (soh < 80) return '#F56C6C'
  if (soh < 90) return '#E6A23C'
  return '#67C23A'
}

const viewDetails = (battery: any) => {
  selectedBattery.value = battery
  detailVisible.value = true
}

const viewHistory = (battery: any) => {
  selectedBattery.value = battery
  historyVisible.value = true
}

const viewCellDetails = (battery: any) => {
  selectedBattery.value = battery
  cellDetailVisible.value = true
}

const performCapacityTest = (battery: any) => {
  ElMessageBox.confirm(
      `Initiate capacity test for ${battery.id}? This may take several hours.`,
      'Confirm Capacity Test',
      {
        confirmButtonText: 'Start Test',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    ElMessage.success(`Capacity test initiated for ${battery.id}`)
  }).catch(() => {})
}

const scheduleReplacement = (battery: any) => {
  ElMessageBox.confirm(
      `Schedule replacement for ${battery.id}? This will create a work order.`,
      'Schedule Replacement',
      {
        confirmButtonText: 'Schedule',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    ElMessage.success(`Replacement scheduled for ${battery.id}`)
  }).catch(() => {})
}

const clearAlerts = (battery: any) => {
  battery.alerts = []
  ElMessage.success(`Alerts cleared for ${battery.id}`)
}

const refreshData = () => {
  ElMessage.info('Refreshing battery data...')
  setTimeout(() => {
    ElMessage.success('Data refreshed successfully')
  }, 1000)
}

const initSohChart = () => {
  if (sohChartRef.value) {
    if (sohChart) sohChart.dispose()

    sohChart = echarts.init(sohChartRef.value)
    sohChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: {
        data: ['State of Health (%)', 'Temperature (°C)'],
        left: 'left',
        textStyle: { color: '#606266' }
      },
      grid: { left: '8%', right: '8%', top: '15%', bottom: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: sohTrendData.value.map(d => d.month),
        axisLabel: { fontWeight: 500 }
      },
      yAxis: [
        { type: 'value', name: 'SOH (%)', min: 50, max: 100 },
        { type: 'value', name: 'Temperature (°C)', min: 20, max: 40 }
      ],
      series: [
        {
          name: 'State of Health (%)',
          type: 'line',
          data: sohTrendData.value.map(d => d.soh),
          smooth: true,
          lineStyle: { color: '#409EFF', width: 3 },
          areaStyle: { opacity: 0.1, color: '#409EFF' },
          symbol: 'circle',
          symbolSize: 8,
          label: { show: true, position: 'top', formatter: '{c}%' }
        },
        {
          name: 'Temperature (°C)',
          type: 'line',
          yAxisIndex: 1,
          data: sohTrendData.value.map(d => d.temp),
          smooth: true,
          lineStyle: { color: '#F56C6C', width: 2 },
          symbol: 'diamond',
          symbolSize: 8,
          label: { show: true, position: 'top', formatter: '{c}°C' }
        }
      ]
    })
  }
}

const initResistanceChart = () => {
  if (resistanceChartRef.value) {
    if (resistanceChart) resistanceChart.dispose()

    resistanceChart = echarts.init(resistanceChartRef.value)
    resistanceChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: {
        data: ['Internal Resistance (mΩ)'],
        left: 'left',
        textStyle: { color: '#606266' }
      },
      grid: { left: '8%', right: '8%', top: '15%', bottom: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: sohTrendData.value.map(d => d.month),
        axisLabel: { fontWeight: 500 }
      },
      yAxis: {
        type: 'value',
        name: 'Resistance (mΩ)',
        min: 0,
        max: 10
      },
      series: [
        {
          name: 'Internal Resistance (mΩ)',
          type: 'line',
          data: sohTrendData.value.map(d => d.resistance),
          smooth: true,
          lineStyle: { color: '#E6A23C', width: 3 },
          areaStyle: { opacity: 0.1, color: '#E6A23C' },
          symbol: 'circle',
          symbolSize: 8,
          label: { show: true, position: 'top', formatter: '{c} mΩ' }
        }
      ]
    })
  }
}

const handleResize = () => {
  sohChart?.resize()
  resistanceChart?.resize()
}

watch(isLoaded, (loaded) => {
  if (loaded) {
    nextTick(() => {
      initSohChart()
      initResistanceChart()
      window.addEventListener('resize', handleResize)
    })
  }
})

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
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  sohChart?.dispose()
  resistanceChart?.dispose()
})

// Helper computed values
const avgSoh = computed(() => {
  const sum = batteryUnits.value.reduce((acc, b) => acc + b.stateOfHealth, 0)
  return (sum / batteryUnits.value.length).toFixed(1)
})

const avgTemp = computed(() => {
  const sum = batteryUnits.value.reduce((acc, b) => acc + b.temperature, 0)
  return (sum / batteryUnits.value.length).toFixed(1)
})
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
          <span class="loading-title">Loading</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Battery Fault Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="battery-faults">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Battery Fault Management</h2>
        <p class="subtitle">Real-time monitoring and health analysis for battery systems</p>
      </div>
      <div class="header-actions">
        <el-input
            v-model="searchKeyword"
            placeholder="Search by ID or Location..."
            clearable
            style="width: 260px"
            :prefix-icon="Search"
        />
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 130px">
          <el-option label="All" value="all" />
          <el-option label="Healthy" value="healthy" />
          <el-option label="Warning" value="warning" />
          <el-option label="Critical" value="critical" />
        </el-select>
        <el-select v-model="typeFilter" placeholder="Type" clearable style="width: 140px">
          <el-option label="All" value="all" />
          <el-option label="VRLA" value="VRLA" />
          <el-option label="Lithium-Ion" value="Lithium-Ion" />
        </el-select>
        <el-button type="primary" @click="refreshData">
          <el-icon><RefreshRight /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Statistics Overview -->
    <div class="stats-grid">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon total">
            <el-icon><Monitor /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ batteryUnits.length }}</div>
            <div class="stat-label">Total Batteries</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon healthy">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ batteryUnits.filter(b => b.status === 'healthy').length }}</div>
            <div class="stat-label">Healthy</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon warning">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ batteryUnits.filter(b => b.status === 'warning').length }}</div>
            <div class="stat-label">Warning</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon critical">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ batteryUnits.filter(b => b.status === 'critical').length }}</div>
            <div class="stat-label">Critical</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon soh">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ avgSoh }}%</div>
            <div class="stat-label">Avg SOH</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>State of Health Trend (6 Months)</span>
            <el-tag type="info" size="small">Degradation Analysis</el-tag>
          </div>
        </template>
        <div ref="sohChartRef" class="chart"></div>
      </el-card>

      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Internal Resistance Trend</span>
            <el-tag type="warning" size="small">Health Indicator</el-tag>
          </div>
        </template>
        <div ref="resistanceChartRef" class="chart"></div>
      </el-card>
    </div>

    <!-- Battery Units Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="table-header">
          <span class="table-title">Battery Units Overview</span>
          <span class="table-subtitle">{{ filteredBatteries.length }} units displayed</span>
        </div>
      </template>
      <el-table :data="paginatedBatteries" stripe style="width: 100%">
        <el-table-column prop="id" label="Battery ID" width="140" align="center"  />
        <el-table-column prop="name" label="Name" min-width="160" align="center"  />
        <el-table-column prop="location" label="Location" min-width="180"  align="center"  show-overflow-tooltip />
        <el-table-column prop="type" label="Type"  align="center"  />
        <el-table-column label="Status"  align="center" >
          <template #default="{ row }">
            <div class="status-indicator">
              <span class="status-dot" :style="{ background: getStatusColor(row.status) }"></span>
              <span>{{ getStatusText(row.status) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="SOH"  align="center" >
          <template #default="{ row }">
            <el-progress :percentage="row.stateOfHealth" :stroke-width="8" :color="getSohColor(row.stateOfHealth)" />
          </template>
        </el-table-column>
        <el-table-column label="Temp"  align="center" >
          <template #default="{ row }">
            <span :style="{ color: row.temperature > 30 ? '#F56C6C' : row.temperature > 27 ? '#E6A23C' : '#67C23A' }">
              {{ row.temperature }}°C
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Resistance"  align="center" >
          <template #default="{ row }">
            <span :style="{ color: row.resistance > 6 ? '#F56C6C' : row.resistance > 4 ? '#E6A23C' : '#67C23A' }">
              {{ row.resistance }} mΩ
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="cycleCount" label="Cycles" width="90" />
        <el-table-column label="Alerts" align="center" class-name="alert-column">
          <template #default="{ row }">
            <div style="position: relative; height: 100%; display: flex; align-items: center; justify-content: center;">
              <el-badge
                  :value="row.alerts.length"
                  :hidden="row.alerts.length === 0"
                  type="danger"
                  :offset="[-2, 8]"
              >
                <el-button size="small" text @click="viewDetails(row)">
                  <el-icon><Warning /></el-icon>
                </el-button>
              </el-badge>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Actions"  align="center"  fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetails(row)">Details</el-button>
            <el-button type="info" link size="small" @click="viewCellDetails(row)">Cells</el-button>
            <el-button type="warning" link size="small" @click="performCapacityTest(row)">Test</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredBatteries.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Battery Detail Dialog -->
    <el-dialog v-model="detailVisible" :title="selectedBattery?.name" width="750px">
      <div v-if="selectedBattery" class="battery-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Battery ID">{{ selectedBattery.id }}</el-descriptions-item>
          <el-descriptions-item label="Type">{{ selectedBattery.type }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedBattery.location }}</el-descriptions-item>
          <el-descriptions-item label="Manufacturer">{{ selectedBattery.manufacturer }}</el-descriptions-item>
          <el-descriptions-item label="Install Date">{{ selectedBattery.installDate }}</el-descriptions-item>
          <el-descriptions-item label="Expected Life">{{ selectedBattery.expectedLife }} months</el-descriptions-item>
          <el-descriptions-item label="Status">
            <span class="status-indicator">
              <span class="status-dot" :style="{ background: getStatusColor(selectedBattery.status) }"></span>
              {{ getStatusText(selectedBattery.status) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="Cycle Count">{{ selectedBattery.cycleCount }}</el-descriptions-item>
          <el-descriptions-item label="Voltage">{{ selectedBattery.voltage }}V</el-descriptions-item>
          <el-descriptions-item label="Current">{{ selectedBattery.current }}A</el-descriptions-item>
          <el-descriptions-item label="State of Health">
            <el-progress :percentage="selectedBattery.stateOfHealth" :stroke-width="10" :color="getSohColor(selectedBattery.stateOfHealth)" />
          </el-descriptions-item>
          <el-descriptions-item label="State of Charge">
            <el-progress :percentage="selectedBattery.stateOfCharge" :stroke-width="10" color="#409EFF" />
          </el-descriptions-item>
          <el-descriptions-item label="Temperature">{{ selectedBattery.temperature }}°C</el-descriptions-item>
          <el-descriptions-item label="Internal Resistance">{{ selectedBattery.resistance }} mΩ</el-descriptions-item>
        </el-descriptions>

        <div v-if="selectedBattery.alerts.length > 0" class="alerts-section">
          <h4>Active Alerts</h4>
          <el-table :data="selectedBattery.alerts" size="small">
            <el-table-column label="Severity" width="100">
              <template #default="{ row }">
                <el-tag :type="row.severity === 'critical' ? 'danger' : row.severity === 'warning' ? 'warning' : 'info'" size="small">
                  {{ row.severity }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="message" label="Message" />
            <el-table-column prop="timestamp" label="Timestamp" width="160" />
          </el-table>
          <div class="alerts-actions">
            <el-button type="primary" size="small" @click="clearAlerts(selectedBattery)">Clear Alerts</el-button>
          </div>
        </div>

        <div class="detail-actions">
          <el-button type="warning" @click="performCapacityTest(selectedBattery)">Run Capacity Test</el-button>
          <el-button type="danger" @click="scheduleReplacement(selectedBattery)" v-if="selectedBattery.status === 'critical'">Schedule Replacement</el-button>
          <el-button type="primary" @click="viewHistory(selectedBattery)">View Fault History</el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Cell Detail Dialog -->
    <el-dialog v-model="cellDetailVisible" :title="`Cell Details - ${selectedBattery?.id}`" width="800px">
      <el-table :data="selectedBattery?.cells || []" stripe>
        <el-table-column prop="id" label="Cell #" width="80" />
        <el-table-column label="Voltage" width="120">
          <template #default="{ row }">
            <span :style="{ color: row.voltage < 12.5 ? '#F56C6C' : '#67C23A' }">
              {{ row.voltage }}V
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Temperature" width="120">
          <template #default="{ row }">
            <span :style="{ color: row.temperature > 30 ? '#F56C6C' : '#67C23A' }">
              {{ row.temperature }}°C
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Resistance" width="120">
          <template #default="{ row }">
            <span :style="{ color: row.resistance > 6 ? '#F56C6C' : row.resistance > 4 ? '#E6A23C' : '#67C23A' }">
              {{ row.resistance }} mΩ
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'good' ? 'success' : row.status === 'warning' ? 'warning' : 'danger'" size="small">
              {{ row.status.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="cellDetailVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Fault History Dialog -->
    <el-dialog v-model="historyVisible" :title="`Fault History - ${selectedBattery?.id}`" width="800px">
      <el-table :data="faultHistory.filter(f => f.batteryId === selectedBattery?.id)" stripe>
        <el-table-column prop="id" label="Fault ID" width="100" />
        <el-table-column prop="type" label="Fault Type" width="140" />
        <el-table-column label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="row.severity === 'critical' ? 'danger' : row.severity === 'warning' ? 'warning' : 'info'" size="small">
              {{ row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="Description" min-width="200" />
        <el-table-column prop="timestamp" label="Occurred" width="160" />
        <el-table-column prop="resolved" label="Resolved" width="160" />
      </el-table>
      <template #footer>
        <el-button @click="historyVisible = false">Close</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
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

/* Main Content */
.battery-faults {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h2 {
  margin: 0 0 4px 0;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #303133, #606266);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 16px;
}

.stat-card :deep(.el-card__body) {
  padding: 16px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.total { background: rgba(64, 158, 255, 0.1); color: #409EFF; }
.stat-icon.healthy { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
.stat-icon.warning { background: rgba(230, 162, 60, 0.1); color: #E6A23C; }
.stat-icon.critical { background: rgba(245, 108, 108, 0.1); color: #F56C6C; }
.stat-icon.soh { background: rgba(144, 147, 153, 0.1); color: #909399; }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* Charts */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  border-radius: 16px;
}

.chart-card :deep(.el-card__body) {
  padding: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.chart {
  width: 100%;
  height: 320px;
}

/* Table */
.table-card {
  border-radius: 16px;
}

.table-card :deep(.el-card__body) {
  padding: 0;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-title {
  font-size: 16px;
  font-weight: 600;
}

.table-subtitle {
  font-size: 12px;
  color: #909399;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.pagination-wrapper {
  padding: 16px 20px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
}

/* Detail Dialog */
.battery-detail {
  padding: 0 0 16px 0;
}

.alerts-section {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.alerts-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
}

.alerts-actions {
  margin-top: 12px;
  text-align: right;
}

.detail-actions {
  margin-top: 20px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  flex-wrap: wrap;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  }

  .charts-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .battery-faults {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions {
    flex-direction: column;
  }

  .header-actions .el-input,
  .header-actions .el-select,
  .header-actions .el-button {
    width: 100%;
  }

  .chart {
    height: 260px;
  }
}
</style>