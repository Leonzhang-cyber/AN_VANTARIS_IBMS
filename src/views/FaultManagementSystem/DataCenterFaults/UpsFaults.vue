<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted, computed } from 'vue'
import {
  Search, RefreshRight, Warning, CircleCheck, Clock,
  TrendCharts, Monitor, Connection,
  Document, Setting, More, ArrowUp, ArrowDown,
  VideoCamera, DataAnalysis
} from "@element-plus/icons-vue"
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Connecting to UPS monitoring system...',
  'Loading real-time data...',
  'Analyzing power quality...'
]

// UPS Units Data
const upsUnits = ref([
  {
    id: 'UPS-01-DC-A',
    name: 'Main UPS Unit 1',
    location: 'Data Center A - Room 101',
    status: 'critical',
    load: 78.5,
    loadTrend: 'up',
    inputVoltage: 408,
    outputVoltage: 415,
    batteryCharge: 92,
    batteryHealth: 'good',
    temperature: 32,
    runtime: 18.5,
    efficiency: 94.2,
    alerts: [
      { severity: 'warning', message: 'Load approaching threshold (80%)', timestamp: '2025-01-16 08:30:00' },
      { severity: 'info', message: 'Battery test completed successfully', timestamp: '2025-01-15 02:00:00' }
    ],
    lastMaintenance: '2024-12-10',
    nextMaintenance: '2025-03-10'
  },
  {
    id: 'UPS-02-DC-A',
    name: 'Main UPS Unit 2',
    location: 'Data Center A - Room 101',
    status: 'warning',
    load: 65.2,
    loadTrend: 'stable',
    inputVoltage: 412,
    outputVoltage: 414,
    batteryCharge: 88,
    batteryHealth: 'warning',
    temperature: 35,
    runtime: 22.3,
    efficiency: 93.8,
    alerts: [
      { severity: 'warning', message: 'Battery health degraded - schedule maintenance', timestamp: '2025-01-14 10:15:00' },
      { severity: 'info', message: 'Temperature above optimal range', timestamp: '2025-01-14 09:45:00' }
    ],
    lastMaintenance: '2024-11-15',
    nextMaintenance: '2025-02-15'
  },
  {
    id: 'UPS-03-DC-B',
    name: 'Backup UPS Unit',
    location: 'Data Center B - Room 202',
    status: 'healthy',
    load: 42.3,
    loadTrend: 'down',
    inputVoltage: 410,
    outputVoltage: 409,
    batteryCharge: 96,
    batteryHealth: 'good',
    temperature: 28,
    runtime: 35.2,
    efficiency: 95.6,
    alerts: [],
    lastMaintenance: '2025-01-05',
    nextMaintenance: '2025-04-05'
  },
  {
    id: 'UPS-04-DC-C',
    name: 'Critical Load UPS',
    location: 'Data Center C - Server Hall',
    status: 'healthy',
    load: 55.8,
    loadTrend: 'stable',
    inputVoltage: 414,
    outputVoltage: 413,
    batteryCharge: 94,
    batteryHealth: 'good',
    temperature: 30,
    runtime: 28.7,
    efficiency: 94.5,
    alerts: [],
    lastMaintenance: '2024-12-20',
    nextMaintenance: '2025-03-20'
  }
])

// Historical fault data
const faultHistory = ref([
  { id: 'FLT-001', upsId: 'UPS-01-DC-A', type: 'Overload', severity: 'critical', timestamp: '2025-01-10 14:23:00', resolved: '2025-01-10 14:45:00', description: 'Load exceeded 90% capacity for 5 minutes' },
  { id: 'FLT-002', upsId: 'UPS-02-DC-A', type: 'Battery Low', severity: 'warning', timestamp: '2025-01-08 09:15:00', resolved: '2025-01-08 11:30:00', description: 'Battery charge dropped below 50%' },
  { id: 'FLT-003', upsId: 'UPS-01-DC-A', type: 'Input Anomaly', severity: 'major', timestamp: '2025-01-05 22:45:00', resolved: '2025-01-05 23:20:00', description: 'Input voltage fluctuation detected' },
  { id: 'FLT-004', upsId: 'UPS-03-DC-B', type: 'Temperature High', severity: 'warning', timestamp: '2025-01-03 15:30:00', resolved: '2025-01-03 16:00:00', description: 'UPS temperature exceeded 38°C' }
])

// Performance metrics over time
const performanceData = ref([
  { time: '00:00', load: 45, efficiency: 94, temp: 28 },
  { time: '02:00', load: 42, efficiency: 94, temp: 27 },
  { time: '04:00', load: 40, efficiency: 94, temp: 27 },
  { time: '06:00', load: 38, efficiency: 93, temp: 26 },
  { time: '08:00', load: 52, efficiency: 94, temp: 28 },
  { time: '10:00', load: 68, efficiency: 95, temp: 30 },
  { time: '12:00', load: 72, efficiency: 95, temp: 32 },
  { time: '14:00', load: 78, efficiency: 96, temp: 34 },
  { time: '16:00', load: 75, efficiency: 95, temp: 33 },
  { time: '18:00', load: 65, efficiency: 95, temp: 31 },
  { time: '20:00', load: 58, efficiency: 94, temp: 30 },
  { time: '22:00', load: 50, efficiency: 94, temp: 29 }
])

// Battery health data
const batteryHealthData = ref([
  { upsId: 'UPS-01-DC-A', batteryAge: 18, capacity: 92, stringVoltage: 432, cellTemp: 31 },
  { upsId: 'UPS-02-DC-A', batteryAge: 24, capacity: 88, stringVoltage: 428, cellTemp: 34 },
  { upsId: 'UPS-03-DC-B', batteryAge: 12, capacity: 96, stringVoltage: 438, cellTemp: 28 },
  { upsId: 'UPS-04-DC-C', batteryAge: 15, capacity: 94, stringVoltage: 435, cellTemp: 29 }
])

// Selected UPS for detail view
const selectedUPS = ref<any>(null)
const detailVisible = ref(false)
const historyVisible = ref(false)

// Filters
const searchKeyword = ref('')
const statusFilter = ref('all')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const loadChartRef = ref<HTMLElement | null>(null)
const batteryChartRef = ref<HTMLElement | null>(null)
let loadChart: echarts.ECharts | null = null
let batteryChart: echarts.ECharts | null = null

const filteredUPS = computed(() => {
  let filtered = upsUnits.value

  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(u => u.status === statusFilter.value)
  }

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(u =>
        u.id.toLowerCase().includes(keyword) ||
        u.name.toLowerCase().includes(keyword) ||
        u.location.toLowerCase().includes(keyword)
    )
  }

  return filtered
})

const paginatedUPS = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredUPS.value.slice(start, end)
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

const getBatteryHealthColor = (health: string) => {
  switch(health) {
    case 'good': return '#67C23A'
    case 'warning': return '#E6A23C'
    case 'critical': return '#F56C6C'
    default: return '#909399'
  }
}

const viewDetails = (ups: any) => {
  selectedUPS.value = ups
  detailVisible.value = true
}

const viewHistory = (ups: any) => {
  selectedUPS.value = ups
  historyVisible.value = true
}

const performTest = (ups: any) => {
  ElMessageBox.confirm(
      `Initiate battery test for ${ups.id}? This may take 10-15 minutes.`,
      'Confirm Battery Test',
      {
        confirmButtonText: 'Start Test',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    ElMessage.success(`Battery test initiated for ${ups.id}`)
  }).catch(() => {})
}

const clearAlerts = (ups: any) => {
  ups.alerts = []
  ElMessage.success(`Alerts cleared for ${ups.id}`)
}

const refreshData = () => {
  ElMessage.info('Refreshing UPS data...')
  setTimeout(() => {
    ElMessage.success('Data refreshed successfully')
  }, 1000)
}

const initLoadChart = () => {
  if (loadChartRef.value) {
    if (loadChart) loadChart.dispose()

    loadChart = echarts.init(loadChartRef.value)
    loadChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: {
        data: ['Load (%)', 'Efficiency (%)', 'Temperature (°C)'],
        left: 'left',
        textStyle: { color: '#606266' }
      },
      grid: { left: '8%', right: '8%', top: '15%', bottom: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: performanceData.value.map(d => d.time),
        axisLabel: { rotate: 45 }
      },
      yAxis: [
        { type: 'value', name: 'Percentage (%)', min: 0, max: 100 },
        { type: 'value', name: 'Temperature (°C)', min: 0, max: 50 }
      ],
      series: [
        {
          name: 'Load (%)',
          type: 'line',
          data: performanceData.value.map(d => d.load),
          smooth: true,
          lineStyle: { color: '#409EFF', width: 3 },
          areaStyle: { opacity: 0.1, color: '#409EFF' },
          symbol: 'circle',
          symbolSize: 6
        },
        {
          name: 'Efficiency (%)',
          type: 'line',
          data: performanceData.value.map(d => d.efficiency),
          smooth: true,
          lineStyle: { color: '#67C23A', width: 2 },
          symbol: 'diamond',
          symbolSize: 6
        },
        {
          name: 'Temperature (°C)',
          type: 'line',
          yAxisIndex: 1,
          data: performanceData.value.map(d => d.temp),
          smooth: true,
          lineStyle: { color: '#F56C6C', width: 2 },
          symbol: 'triangle',
          symbolSize: 6
        }
      ]
    })
  }
}

const initBatteryChart = () => {
  if (batteryChartRef.value) {
    if (batteryChart) batteryChart.dispose()

    batteryChart = echarts.init(batteryChartRef.value)
    batteryChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['Capacity (%)', 'String Voltage (V)'], left: 'left' },
      grid: { left: '10%', right: '8%', top: '15%', bottom: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: batteryHealthData.value.map(b => b.upsId),
        axisLabel: { rotate: 30, fontWeight: 500 }
      },
      yAxis: [
        { type: 'value', name: 'Capacity (%)', min: 0, max: 100 },
        { type: 'value', name: 'Voltage (V)', min: 400, max: 460 }
      ],
      series: [
        {
          name: 'Capacity (%)',
          type: 'bar',
          data: batteryHealthData.value.map(b => b.capacity),
          itemStyle: { color: '#67C23A', borderRadius: [4, 4, 0, 0] },
          label: { show: true, position: 'top', formatter: '{c}%' }
        },
        {
          name: 'String Voltage (V)',
          type: 'line',
          yAxisIndex: 1,
          data: batteryHealthData.value.map(b => b.stringVoltage),
          lineStyle: { color: '#E6A23C', width: 3 },
          symbol: 'circle',
          symbolSize: 8,
          label: { show: true, position: 'top', formatter: '{c}V' }
        }
      ]
    })
  }
}

const handleResize = () => {
  loadChart?.resize()
  batteryChart?.resize()
}

watch(isLoaded, (loaded) => {
  if (loaded) {
    nextTick(() => {
      initLoadChart()
      initBatteryChart()
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
  loadChart?.dispose()
  batteryChart?.dispose()
})

// Helper function for average
const avgBatteryHealth = computed(() => {
  const sum = upsUnits.value.reduce((acc, u) => acc + u.batteryCharge, 0)
  return Math.round(sum / upsUnits.value.length)
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
        <div class="loading-tip">UPS Fault Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="ups-faults">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>UPS Fault Management</h2>
        <p class="subtitle">Real-time monitoring and fault analysis for UPS systems</p>
      </div>
      <div class="header-actions">
        <el-input
            v-model="searchKeyword"
            placeholder="Search UPS by ID or Location..."
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
            <div class="stat-value">{{ upsUnits.length }}</div>
            <div class="stat-label">Total UPS Units</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon healthy">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ upsUnits.filter(u => u.status === 'healthy').length }}</div>
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
            <div class="stat-value">{{ upsUnits.filter(u => u.status === 'warning').length }}</div>
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
            <div class="stat-value">{{ upsUnits.filter(u => u.status === 'critical').length }}</div>
            <div class="stat-label">Critical</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon battery">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ avgBatteryHealth }}%</div>
            <div class="stat-label">Avg Battery Health</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Performance Trends (24 Hours)</span>
            <el-tag type="info" size="small">Live Data</el-tag>
          </div>
        </template>
        <div ref="loadChartRef" class="chart"></div>
      </el-card>

      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Battery Health Status</span>
            <el-tag type="warning" size="small">Maintenance Required</el-tag>
          </div>
        </template>
        <div ref="batteryChartRef" class="chart"></div>
      </el-card>
    </div>

    <!-- UPS Units Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="table-header">
          <span class="table-title">UPS Units Overview</span>
          <span class="table-subtitle">{{ filteredUPS.length }} units displayed</span>
        </div>
      </template>
      <el-table :data="paginatedUPS" stripe style="width: 100%">
        <el-table-column prop="id" label="UPS ID" width="130" align="center"  />
        <el-table-column prop="name" label="Name" min-width="150" align="center"  />
        <el-table-column prop="location" label="Location" min-width="180" align="center"  show-overflow-tooltip />
        <el-table-column label="Status" align="center" >
          <template #default="{ row }">
            <div class="status-indicator">
              <span class="status-dot" :style="{ background: getStatusColor(row.status) }"></span>
              <span>{{ getStatusText(row.status) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Load"  align="center" >
          <template #default="{ row }">
            <div class="metric-cell">
              <span :class="row.loadTrend === 'up' ? 'trend-up' : row.loadTrend === 'down' ? 'trend-down' : ''">
                {{ row.load }}%
              </span>
              <el-icon v-if="row.loadTrend === 'up'" class="trend-up"><ArrowUp /></el-icon>
              <el-icon v-else-if="row.loadTrend === 'down'" class="trend-down"><ArrowDown /></el-icon>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Battery"  align="center" >
          <template #default="{ row }">
            <el-progress :percentage="row.batteryCharge" :stroke-width="6" :show-text="true" />
          </template>
        </el-table-column>
        <el-table-column prop="temperature" label="Temp" align="center" >
          <template #default="{ row }">
            <span :style="{ color: row.temperature > 35 ? '#F56C6C' : row.temperature > 30 ? '#E6A23C' : '#67C23A' }">
              {{ row.temperature }}°C
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="efficiency" label="Efficiency"  align="center" >
          <template #default="{ row }">
            <span>{{ row.efficiency }}%</span>
          </template>
        </el-table-column>
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
            <el-button type="info" link size="small" @click="viewHistory(row)">History</el-button>
            <el-button type="warning" link size="small" @click="performTest(row)">Test</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredUPS.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- UPS Detail Dialog -->
    <el-dialog v-model="detailVisible" :title="selectedUPS?.name" width="700px">
      <div v-if="selectedUPS" class="ups-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="UPS ID">{{ selectedUPS.id }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedUPS.location }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <span class="status-indicator">
              <span class="status-dot" :style="{ background: getStatusColor(selectedUPS.status) }"></span>
              {{ getStatusText(selectedUPS.status) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="Last Maintenance">{{ selectedUPS.lastMaintenance }}</el-descriptions-item>
          <el-descriptions-item label="Next Maintenance">{{ selectedUPS.nextMaintenance }}</el-descriptions-item>
          <el-descriptions-item label="Runtime Remaining">{{ selectedUPS.runtime }} minutes</el-descriptions-item>
          <el-descriptions-item label="Load">{{ selectedUPS.load }}%</el-descriptions-item>
          <el-descriptions-item label="Efficiency">{{ selectedUPS.efficiency }}%</el-descriptions-item>
          <el-descriptions-item label="Input Voltage">{{ selectedUPS.inputVoltage }}V</el-descriptions-item>
          <el-descriptions-item label="Output Voltage">{{ selectedUPS.outputVoltage }}V</el-descriptions-item>
          <el-descriptions-item label="Battery Charge">{{ selectedUPS.batteryCharge }}%</el-descriptions-item>
          <el-descriptions-item label="Battery Health">
            <span :style="{ color: getBatteryHealthColor(selectedUPS.batteryHealth) }">
              {{ selectedUPS.batteryHealth.toUpperCase() }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="Temperature">{{ selectedUPS.temperature }}°C</el-descriptions-item>
        </el-descriptions>

        <div v-if="selectedUPS.alerts.length > 0" class="alerts-section">
          <h4>Active Alerts</h4>
          <el-table :data="selectedUPS.alerts" size="small">
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
            <el-button type="primary" size="small" @click="clearAlerts(selectedUPS)">Clear Alerts</el-button>
          </div>
        </div>

        <div class="detail-actions">
          <el-button type="warning" @click="performTest(selectedUPS)">Run Battery Test</el-button>
          <el-button type="primary" @click="viewHistory(selectedUPS)">View Fault History</el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Fault History Dialog -->
    <el-dialog v-model="historyVisible" :title="`Fault History - ${selectedUPS?.id}`" width="800px">
      <el-table :data="faultHistory.filter(f => f.upsId === selectedUPS?.id)" stripe>
        <el-table-column prop="id" label="Fault ID" width="100" />
        <el-table-column prop="type" label="Fault Type" width="130" />
        <el-table-column label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="row.severity === 'critical' ? 'danger' : row.severity === 'major' ? 'warning' : 'info'" size="small">
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
.ups-faults {
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
.stat-icon.battery { background: rgba(144, 147, 153, 0.1); color: #909399; }

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
  justify-content: center;
  gap: 6px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.metric-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.trend-up { color: #F56C6C; }
.trend-down { color: #67C23A; }

.pagination-wrapper {
  padding: 16px 20px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
}

/* Detail Dialog */
.ups-detail {
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
  .ups-faults {
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