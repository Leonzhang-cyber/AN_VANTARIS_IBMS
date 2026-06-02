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
        <div class="loading-tip">Leak Detection System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="leak-detection-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Leak Detection</h2>
        <p class="header-subtitle">Real-time Leak Monitoring | Acoustic & Moisture Sensors</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- System Status Overview -->
    <el-row :gutter="20" class="overview-row">
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card safe">
          <div class="overview-icon">
            <el-icon :size="28"><SuccessFilled /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">System Status</div>
            <div class="overview-value">{{ systemStatus }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon">
            <el-icon :size="28"><Grid /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Total Sensors</div>
            <div class="overview-value">{{ stats.total }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon normal">
            <el-icon :size="28"><CircleCheck /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Normal</div>
            <div class="overview-value">{{ stats.normal }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon alert">
            <el-icon :size="28"><WarningFilled /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Alert / Leak</div>
            <div class="overview-value" :class="{ 'has-alert': stats.alert > 0 }">{{ stats.alert }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Active Leaks Section -->
    <div v-if="activeLeaks.length > 0" class="alert-section">
      <div class="section-title">
        <span class="alert-title">
          <el-icon><WarningFilled /></el-icon>
          Active Leaks Detected
        </span>
        <el-badge :value="activeLeaks.length" type="danger" />
      </div>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" v-for="leak in activeLeaks" :key="leak.id">
          <div class="leak-alert-card" :class="leak.severity">
            <div class="leak-alert-header">
              <span class="leak-location">{{ leak.location }}</span>
              <el-tag :type="leak.severity === 'critical' ? 'danger' : 'warning'" size="small">
                {{ leak.severity === 'critical' ? 'CRITICAL' : 'WARNING' }}
              </el-tag>
            </div>
            <div class="leak-details">
              <div class="leak-detail">
                <span class="label">Sensor:</span>
                <span class="value">{{ leak.sensorName }}</span>
              </div>
              <div class="leak-detail">
                <span class="label">Moisture:</span>
                <span class="value warning">{{ leak.moisture }}%</span>
              </div>
              <div class="leak-detail">
                <span class="label">Flow Rate:</span>
                <span class="value">{{ leak.flowRate }} L/min</span>
              </div>
              <div class="leak-detail">
                <span class="label">Detected:</span>
                <span class="value">{{ leak.detectedAt }}</span>
              </div>
            </div>
            <div class="leak-actions">
              <el-button type="primary" size="small" @click="viewLeakDetails(leak)">
                <el-icon><View /></el-icon>
                Investigate
              </el-button>
              <el-button type="success" size="small" @click="acknowledgeLeak(leak)">
                <el-icon><CircleCheck /></el-icon>
                Acknowledge
              </el-button>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- Key Metrics Row -->
    <el-row :gutter="20" class="metrics-row">
      <el-col :xs="24" :sm="12" :md="6">
        <div class="metric-card">
          <div class="metric-icon">
            <el-icon :size="24"><Histogram /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-label">Estimated Leak Loss</div>
            <div class="metric-value">{{ metrics.estimatedLoss }} <span class="unit">L/day</span></div>
            <div class="metric-trend" :class="metrics.lossTrend > 0 ? 'up' : 'down'">
              {{ metrics.lossTrend > 0 ? '+' : '' }}{{ metrics.lossTrend }}% vs yesterday
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="metric-card">
          <div class="metric-icon">
            <el-icon :size="24"><DataLine /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-label">Water Saved (MTD)</div>
            <div class="metric-value">{{ metrics.waterSaved }} <span class="unit">m³</span></div>
            <div class="metric-sub">From leak detection</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="metric-card">
          <div class="metric-icon">
            <el-icon :size="24"><Timer /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-label">Avg Response Time</div>
            <div class="metric-value">{{ metrics.avgResponseTime }} <span class="unit">min</span></div>
            <div class="metric-sub">Target: < 15 min</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="metric-card">
          <div class="metric-icon">
            <el-icon :size="24"><TrendCharts /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-label">Detection Accuracy</div>
            <div class="metric-value">{{ metrics.accuracy }}<span class="unit">%</span></div>
            <div class="metric-sub">Last 30 days</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Sensor Grid -->
    <div class="section-title">
      <span>Leak Detection Sensors</span>
      <el-select v-model="zoneFilter" size="small" style="width: 150px" placeholder="Filter by zone" clearable>
        <el-option label="All Zones" value="all" />
        <el-option label="Building A" value="Building A" />
        <el-option label="Building B" value="Building B" />
        <el-option label="Building C" value="Building C" />
        <el-option label="Parking" value="Parking" />
        <el-option label="Basement" value="Basement" />
      </el-select>
    </div>

    <el-row :gutter="20" class="sensors-row">
      <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="sensor in filteredSensors" :key="sensor.id">
        <div class="sensor-card" :class="sensor.status">
          <div class="sensor-header">
            <span class="sensor-name">{{ sensor.name }}</span>
            <div class="sensor-status" :class="sensor.status">
              <span class="status-dot"></span>
              {{ getStatusText(sensor.status) }}
            </div>
          </div>
          <div class="sensor-icon">
            <el-icon :size="40" v-if="sensor.status === 'normal'"><Connection /></el-icon>
            <el-icon :size="40" v-else-if="sensor.status === 'warning'"><Warning /></el-icon>
            <el-icon :size="40" v-else><WarningFilled /></el-icon>
          </div>
          <div class="sensor-readings">
            <div class="reading">
              <span class="label">Moisture Level:</span>
              <div class="reading-value">
                <el-progress
                    :percentage="sensor.moisture"
                    :color="getMoistureColor(sensor.moisture)"
                    :stroke-width="8"
                />
                <span class="percentage">{{ sensor.moisture }}%</span>
              </div>
            </div>
            <div class="reading">
              <span class="label">Flow Rate:</span>
              <span class="value" :class="{ 'warning': sensor.flowRate > 50 }">{{ sensor.flowRate }} L/min</span>
            </div>
            <div class="reading">
              <span class="label">Pressure:</span>
              <span class="value" :class="{ 'warning': sensor.pressure < 2 }">{{ sensor.pressure }} bar</span>
            </div>
            <div class="reading">
              <span class="label">Battery:</span>
              <el-progress :percentage="sensor.battery" :stroke-width="6" :show-text="false" />
              <span class="percentage small">{{ sensor.battery }}%</span>
            </div>
          </div>
          <div class="sensor-location">
            <el-icon><Location /></el-icon>
            {{ sensor.location }} - {{ sensor.zone }}
          </div>
          <div class="sensor-actions" v-if="sensor.status !== 'normal'">
            <el-button type="primary" size="small" @click="openInvestigateDialog(sensor)">
              <el-icon><Search /></el-icon>
              Investigate
            </el-button>
            <el-button type="success" size="small" @click="resetSensor(sensor)">
              <el-icon><RefreshRight /></el-icon>
              Reset
            </el-button>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Charts Row -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :md="14">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Moisture & Flow Trend (Last 24 Hours)</span>
              <el-radio-group v-model="chartPeriod" size="small" @change="updateTrendChart">
                <el-radio-button label="hour">Hourly</el-radio-button>
                <el-radio-button label="day">Daily</el-radio-button>
                <el-radio-button label="week">Weekly</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="10">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Sensor Status Distribution</span>
            </div>
          </template>
          <div ref="statusChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Leak History Table -->
    <el-card shadow="hover" class="history-card">
      <template #header>
        <div class="card-header">
          <span>Leak Event History</span>
          <el-date-picker
              v-model="dateRange"
              type="daterange"
              size="small"
              range-separator="to"
              start-placeholder="Start"
              end-placeholder="End"
              :shortcuts="dateShortcuts"
          />
        </div>
      </template>
      <el-table :data="paginatedHistory" stripe border style="width: 100%">
        <el-table-column prop="time" label="Time" width="160" sortable />
        <el-table-column prop="location" label="Location" min-width="150" />
        <el-table-column prop="sensorName" label="Sensor" min-width="130" />
        <el-table-column prop="severity" label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="row.severity === 'critical' ? 'danger' : 'warning'" size="small">
              {{ row.severity.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="moisture" label="Moisture (%)" width="120" sortable>
          <template #default="{ row }">{{ row.moisture }}%</template>
        </el-table-column>
        <el-table-column prop="estimatedLoss" label="Loss (L)" width="120" sortable />
        <el-table-column prop="responseTime" label="Response (min)" width="120" sortable />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Resolved' ? 'success' : 'warning'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="historyPagination.currentPage"
            v-model:page-size="historyPagination.pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredHistory.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleHistorySizeChange"
            @current-change="handleHistoryCurrentChange"
        />
      </div>
    </el-card>

    <!-- Leak Investigation Dialog -->
    <el-dialog v-model="investigateDialogVisible" :title="`Leak Investigation - ${selectedInvestigateSensor?.name}`" width="500px">
      <div class="investigation-content">
        <el-alert
            :title="`Leak detected at ${selectedInvestigateSensor?.location}`"
            type="warning"
            :closable="false"
            show-icon
        >
          <template #default>
            <p>Moisture level: {{ selectedInvestigateSensor?.moisture }}%</p>
            <p>Flow rate: {{ selectedInvestigateSensor?.flowRate }} L/min</p>
            <p>Please check the area immediately.</p>
          </template>
        </el-alert>
        <div class="investigation-actions">
          <el-button type="primary" @click="startInvestigation">Start Investigation</el-button>
          <el-button @click="investigateDialogVisible = false">Close</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Download,
  Refresh,
  SuccessFilled,
  Grid,
  CircleCheck,
  WarningFilled,
  Warning,
  View,
  Histogram,
  DataLine,
  Timer,
  TrendCharts,
  Connection,
  Location,
  Search,
  RefreshRight
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Initializing leak sensors...',
  'Analyzing moisture data...',
  'Almost ready...'
]

// ==================== Data State ====================
const chartPeriod = ref('hour')
const zoneFilter = ref('all')
const dateRange = ref<[Date, Date] | null>(null)

const dateShortcuts = [
  { text: 'Last 7 days', value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 7 * 24 * 60 * 60 * 1000)
      return [start, end]
    }},
  { text: 'Last 30 days', value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 30 * 24 * 60 * 60 * 1000)
      return [start, end]
    }}
]

interface LeakSensor {
  id: number
  name: string
  location: string
  zone: string
  status: 'normal' | 'warning' | 'leak'
  moisture: number
  flowRate: number
  pressure: number
  battery: number
  lastReading: string
}

interface LeakEvent {
  id: number
  time: string
  location: string
  sensorName: string
  severity: 'warning' | 'critical'
  moisture: number
  flowRate: number
  estimatedLoss: number
  responseTime: number
  status: 'Active' | 'Resolved'
  detectedAt: string
}

const sensors = ref<LeakSensor[]>([])
const leakHistory = ref<LeakEvent[]>([])
const activeLeaks = ref<LeakEvent[]>([])

const systemStatus = computed(() => {
  if (activeLeaks.value.length > 0) return 'ALERT'
  return 'Normal'
})

const stats = computed(() => ({
  total: sensors.value.length,
  normal: sensors.value.filter(s => s.status === 'normal').length,
  alert: sensors.value.filter(s => s.status !== 'normal').length
}))

const metrics = ref({
  estimatedLoss: 0,
  lossTrend: 0,
  waterSaved: 0,
  avgResponseTime: 0,
  accuracy: 0
})

const filteredSensors = computed(() => {
  if (zoneFilter.value === 'all') return sensors.value
  return sensors.value.filter(s => s.zone === zoneFilter.value)
})

const filteredHistory = computed(() => {
  let filtered = leakHistory.value
  if (dateRange.value) {
    const [start, end] = dateRange.value
    filtered = filtered.filter(h => {
      const time = new Date(h.time)
      return time >= start && time <= end
    })
  }
  return filtered
})

const historyPagination = ref({ currentPage: 1, pageSize: 10 })
const paginatedHistory = computed(() => {
  const start = (historyPagination.value.currentPage - 1) * historyPagination.value.pageSize
  return filteredHistory.value.slice(start, start + historyPagination.value.pageSize)
})

// Generate mock sensors
const generateSensors = (): LeakSensor[] => {
  const locations = ['Main Pipe Room', 'Kitchen Area', 'Bathroom Level 1', 'Bathroom Level 2', 'Data Center', 'HVAC Room', 'Storage Room', 'Parking Level 1', 'Parking Level 2', 'Basement']
  const zones = ['Building A', 'Building B', 'Building C', 'Parking', 'Basement']

  return locations.map((name, idx) => {
    const statuses: ('normal' | 'warning' | 'leak')[] = ['normal', 'normal', 'normal', 'normal', 'normal', 'warning', 'normal', 'leak', 'normal', 'normal']
    const moisture = statuses[idx % statuses.length] === 'normal' ? 5 + Math.random() * 15 : (statuses[idx % statuses.length] === 'warning' ? 30 + Math.random() * 30 : 70 + Math.random() * 25)

    return {
      id: idx + 1,
      name: `LDS-${String(idx + 1).padStart(3, '0')}`,
      location: name,
      zone: zones[idx % zones.length],
      status: statuses[idx % statuses.length],
      moisture: parseFloat(moisture.toFixed(1)),
      flowRate: parseFloat((2 + Math.random() * 30).toFixed(1)),
      pressure: parseFloat((1 + Math.random() * 4).toFixed(1)),
      battery: Math.floor(60 + Math.random() * 40),
      lastReading: new Date(Date.now() - Math.random() * 60 * 60 * 1000).toLocaleString()
    }
  })
}

// Generate leak history
const generateLeakHistory = (): LeakEvent[] => {
  const events = [
    { time: '2024-01-15 08:23:15', location: 'Main Pipe Room', sensor: 'LDS-001', severity: 'critical', moisture: 85, flowRate: 45, loss: 1250, response: 8 },
    { time: '2024-01-14 14:30:22', location: 'Kitchen Area', sensor: 'LDS-002', severity: 'warning', moisture: 45, flowRate: 28, loss: 380, response: 12 },
    { time: '2024-01-13 22:15:03', location: 'Data Center', sensor: 'LDS-006', severity: 'critical', moisture: 92, flowRate: 52, loss: 2100, response: 5 },
    { time: '2024-01-12 09:45:30', location: 'Parking Level 1', sensor: 'LDS-008', severity: 'warning', moisture: 52, flowRate: 32, loss: 450, response: 15 },
    { time: '2024-01-11 16:20:45', location: 'Basement', sensor: 'LDS-010', severity: 'warning', moisture: 38, flowRate: 25, loss: 280, response: 10 }
  ]

  return events.map((e, idx) => ({
    id: idx + 1,
    time: e.time,
    location: e.location,
    sensorName: e.sensor,
    severity: e.severity as 'warning' | 'critical',
    moisture: e.moisture,
    flowRate: e.flowRate,
    estimatedLoss: e.loss,
    responseTime: e.response,
    status: idx < 2 ? 'Active' : 'Resolved',
    detectedAt: e.time
  }))
}

// Update active leaks
const updateActiveLeaks = () => {
  activeLeaks.value = leakHistory.value.filter(h => h.status === 'Active')

  const leakSensors = sensors.value.filter(s => s.status === 'leak')
  leakSensors.forEach(sensor => {
    if (!activeLeaks.value.find(l => l.sensorName === sensor.name)) {
      activeLeaks.value.push({
        id: activeLeaks.value.length + 100,
        time: new Date().toLocaleString(),
        location: sensor.location,
        sensorName: sensor.name,
        severity: sensor.moisture > 80 ? 'critical' : 'warning',
        moisture: sensor.moisture,
        flowRate: sensor.flowRate,
        estimatedLoss: Math.round(sensor.flowRate * 60),
        responseTime: 0,
        status: 'Active',
        detectedAt: new Date().toLocaleString()
      })
    }
  })
}

// Update metrics
const updateMetrics = () => {
  const totalLoss = activeLeaks.value.reduce((sum, l) => sum + l.estimatedLoss, 0)
  metrics.value.estimatedLoss = totalLoss
  metrics.value.lossTrend = parseFloat((Math.random() * 20 - 5).toFixed(1))
  metrics.value.waterSaved = Math.floor(5000 + Math.random() * 3000)
  metrics.value.avgResponseTime = parseFloat((8 + Math.random() * 7).toFixed(1))
  metrics.value.accuracy = parseFloat((92 + Math.random() * 6).toFixed(1))
}

// Helper functions
const getStatusText = (status: string) => {
  const map: Record<string, string> = { normal: 'Normal', warning: 'Warning', leak: 'LEAK' }
  return map[status] || status
}

const getMoistureColor = (moisture: number) => {
  if (moisture < 30) return '#67C23A'
  if (moisture < 60) return '#E6A23C'
  return '#F56C6C'
}

// Actions
const investigateDialogVisible = ref(false)
const selectedInvestigateSensor = ref<LeakSensor | null>(null)

const viewLeakDetails = (leak: LeakEvent) => {
  ElMessage.info(`Investigating leak at ${leak.location}`)
}

const acknowledgeLeak = (leak: LeakEvent) => {
  ElMessageBox.confirm(`Acknowledge leak at ${leak.location}?`, 'Confirm', {
    confirmButtonText: 'Acknowledge',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    leak.status = 'Resolved'
    activeLeaks.value = activeLeaks.value.filter(l => l.id !== leak.id)

    const sensor = sensors.value.find(s => s.name === leak.sensorName)
    if (sensor && sensor.status !== 'normal') {
      sensor.status = 'normal'
      sensor.moisture = 5 + Math.random() * 10
    }

    updateMetrics()
    updateStatusChart()
    ElMessage.success('Leak acknowledged')
  }).catch(() => {})
}

const openInvestigateDialog = (sensor: LeakSensor) => {
  selectedInvestigateSensor.value = sensor
  investigateDialogVisible.value = true
}

const startInvestigation = () => {
  investigateDialogVisible.value = false
  ElMessage.info('Investigation team dispatched')
}

const resetSensor = (sensor: LeakSensor) => {
  ElMessageBox.confirm(`Reset sensor "${sensor.name}"?`, 'Confirm', {
    confirmButtonText: 'Reset',
    cancelButtonText: 'Cancel',
    type: 'info'
  }).then(() => {
    sensor.status = 'normal'
    sensor.moisture = 5 + Math.random() * 10
    sensor.flowRate = 2 + Math.random() * 10
    updateMetrics()
    updateStatusChart()
    ElMessage.success('Sensor reset successfully')
  }).catch(() => {})
}

// ==================== Chart Functions ====================
const trendChartRef = ref<HTMLElement>()
const statusChartRef = ref<HTMLElement>()

let trendChart: echarts.ECharts | null = null
let statusChart: echarts.ECharts | null = null

const initCharts = () => {
  nextTick(() => {
    if (trendChartRef.value) {
      if (trendChart) trendChart.dispose()
      trendChart = echarts.init(trendChartRef.value)
      updateTrendChart()
    }

    if (statusChartRef.value) {
      if (statusChart) statusChart.dispose()
      statusChart = echarts.init(statusChartRef.value)
      updateStatusChart()
    }
  })
}

const updateTrendChart = () => {
  let moistureData: number[] = []
  let flowData: number[] = []
  let xAxisData: string[] = []

  if (chartPeriod.value === 'hour') {
    xAxisData = Array.from({ length: 24 }, (_, i) => `${i}:00`)
    moistureData = Array.from({ length: 24 }, () => parseFloat((15 + Math.random() * 40).toFixed(1)))
    flowData = Array.from({ length: 24 }, () => parseFloat((10 + Math.random() * 30).toFixed(1)))
  } else if (chartPeriod.value === 'day') {
    xAxisData = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    moistureData = [22, 25, 28, 45, 52, 30, 20]
    flowData = [15, 18, 20, 35, 42, 22, 12]
  } else {
    xAxisData = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    moistureData = [25, 30, 35, 28]
    flowData = [18, 22, 25, 20]
  }

  trendChart?.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Average Moisture (%)', 'Flow Rate (L/min)'] },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: [
      { type: 'value', name: 'Moisture (%)', min: 0, max: 100 },
      { type: 'value', name: 'Flow Rate (L/min)' }
    ],
    series: [
      {
        name: 'Average Moisture (%)',
        type: 'line',
        data: moistureData,
        smooth: true,
        lineStyle: { color: '#409EFF', width: 3 },
        areaStyle: { opacity: 0.1 },
        yAxisIndex: 0,
        markLine: { data: [{ yAxis: 30, name: 'Warning', lineStyle: { color: '#E6A23C' } }, { yAxis: 60, name: 'Critical', lineStyle: { color: '#F56C6C' } }] }
      },
      {
        name: 'Flow Rate (L/min)',
        type: 'line',
        data: flowData,
        smooth: true,
        lineStyle: { color: '#67C23A', width: 2 },
        yAxisIndex: 1
      }
    ]
  })
}

const updateStatusChart = () => {
  statusChart?.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: stats.value.normal, name: 'Normal', itemStyle: { color: '#67C23A' } },
        { value: stats.value.alert, name: 'Alert / Leak', itemStyle: { color: '#F56C6C' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })
}

// ==================== Actions ====================
const refreshData = () => {
  sensors.value = generateSensors()
  leakHistory.value = generateLeakHistory()
  updateActiveLeaks()
  updateMetrics()
  updateStatusChart()
  updateTrendChart()
  ElMessage.success('Data refreshed')
}

const handleExport = () => {
  ElMessage.success('Report export started')
}

const handleHistorySizeChange = () => { historyPagination.value.currentPage = 1 }
const handleHistoryCurrentChange = () => {}

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
      sensors.value = generateSensors()
      leakHistory.value = generateLeakHistory()
      updateActiveLeaks()
      updateMetrics()
      initCharts()
    }, 400)
  }, 2000)
})

watch([trendChartRef, statusChartRef], () => {
  window.addEventListener('resize', () => {
    trendChart?.resize()
    statusChart?.resize()
  })
})
</script>

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

.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
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

.loading-tip { font-size: 13px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 8px; font-weight: 500; }
.loading-subtip { font-size: 11px; color: #64748b; letter-spacing: 0.5px; animation: pulse 2s ease-in-out infinite; }

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Main Container */
.leak-detection-container {
  padding: 20px;
  background: #f0f2f5;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  background: white;
  padding: 20px 24px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.page-header h2 {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 600;
  color: #1f2f3d;
}

.header-subtitle {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Overview Cards */
.overview-row {
  margin-bottom: 24px;
}

.overview-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.overview-card.safe .overview-icon { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
.overview-card .overview-icon { background: rgba(64, 158, 255, 0.1); color: #409EFF; }
.overview-card .overview-icon.normal { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
.overview-card .overview-icon.alert { background: rgba(245, 108, 108, 0.1); color: #F56C6C; }

.overview-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.overview-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.overview-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
}

.overview-value.has-alert { color: #F56C6C; }

/* Alert Section */
.alert-section {
  margin-bottom: 24px;
}

.alert-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #F56C6C;
  font-weight: 600;
}

.leak-alert-card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 20px;
  border-left: 4px solid #E6A23C;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.leak-alert-card.critical { border-left-color: #F56C6C; background: rgba(245, 108, 108, 0.02); }

.leak-alert-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.leak-location {
  font-weight: 600;
  font-size: 16px;
}

.leak-details {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 16px;
}

.leak-detail {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 13px;
}

.leak-detail .label { color: #909399; }
.leak-detail .value { font-weight: 500; }
.leak-detail .value.warning { color: #F56C6C; font-weight: 600; }

.leak-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* Section Title */
.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title span {
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

/* Metric Cards */
.metrics-row {
  margin-bottom: 24px;
}

.metric-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(64, 158, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409EFF;
}

.metric-info { flex: 1; }
.metric-label { font-size: 13px; color: #909399; margin-bottom: 4px; }
.metric-value { font-size: 28px; font-weight: 700; color: #1f2f3d; }
.metric-value .unit { font-size: 12px; font-weight: normal; color: #909399; }
.metric-trend { font-size: 12px; margin-top: 4px; }
.metric-trend.up { color: #F56C6C; }
.metric-trend.down { color: #67C23A; }
.metric-sub { font-size: 11px; color: #909399; margin-top: 4px; }

/* Sensor Cards */
.sensors-row {
  margin-bottom: 20px;
}

.sensor-card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.3s ease;
  border-top: 3px solid #67C23A;
}

.sensor-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(0,0,0,0.12);
}

.sensor-card.warning { border-top-color: #E6A23C; }
.sensor-card.leak { border-top-color: #F56C6C; }

.sensor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.sensor-name {
  font-weight: 600;
  font-size: 16px;
  color: #1f2f3d;
}

.sensor-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 20px;
}

.sensor-status.normal { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
.sensor-status.warning { background: rgba(230, 162, 60, 0.1); color: #E6A23C; }
.sensor-status.leak { background: rgba(245, 108, 108, 0.1); color: #F56C6C; }

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.sensor-icon {
  text-align: center;
  margin: 12px 0;
  color: #409EFF;
}

.sensor-card.warning .sensor-icon { color: #E6A23C; }
.sensor-card.leak .sensor-icon { color: #F56C6C; }

.sensor-readings {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 12px;
}

.reading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  font-size: 13px;
}

.reading .label { color: #909399; }
.reading .value { font-weight: 500; }
.reading .value.warning { color: #F56C6C; }

.reading-value {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  justify-content: flex-end;
}

.reading-value .el-progress { width: 100px; }
.percentage { font-size: 12px; font-weight: 500; min-width: 40px; text-align: right; }
.percentage.small { font-size: 11px; }

.sensor-location {
  font-size: 12px;
  color: #909399;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.sensor-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* Charts */
.charts-row {
  margin-bottom: 20px;
}

.chart-card {
  border-radius: 16px;
}

.chart-container {
  width: 100%;
  height: 350px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

/* History Card */
.history-card {
  border-radius: 16px;
}

.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

/* Investigation Dialog */
.investigation-content {
  text-align: center;
}

.investigation-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 20px;
}
</style>