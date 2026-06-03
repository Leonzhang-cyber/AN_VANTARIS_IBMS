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
        <div class="loading-tip">Fire Pump System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="fire-pumps-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Fire Pumps</h2>
        <p class="header-subtitle">Fire Protection System | NFPA 20 Compliant</p>
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
        <div class="overview-card">
          <div class="overview-icon total">
            <el-icon :size="28"><Grid /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Total Pumps</div>
            <div class="overview-value">{{ stats.total }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon running">
            <el-icon :size="28"><VideoPlay /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Running</div>
            <div class="overview-value">{{ stats.running }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon auto">
            <el-icon :size="28"><Refresh /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Auto Mode</div>
            <div class="overview-value">{{ stats.autoMode }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon fault">
            <el-icon :size="28"><WarningFilled /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Fault / Alarm</div>
            <div class="overview-value" :class="{ 'has-alarm': stats.fault > 0 }">{{ stats.fault }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- System Pressure & Flow -->
    <el-row :gutter="20" class="pressure-row">
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="pressure-card">
          <template #header>
            <div class="card-header">
              <span>System Pressure</span>
              <el-tag :type="getPressureStatus" size="small">{{ getPressureStatusText }}</el-tag>
            </div>
          </template>
          <div class="pressure-gauge">
            <div class="gauge-container">
              <div ref="pressureGaugeRef" class="gauge-chart"></div>
            </div>
            <div class="pressure-info">
              <div class="pressure-value">{{ systemData.pressure }} <span class="unit">bar</span></div>
              <div class="pressure-range">
                <span>Low: {{ systemData.lowPressure }} bar</span>
                <span>High: {{ systemData.highPressure }} bar</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="flow-card">
          <template #header>
            <div class="card-header">
              <span>Total Flow Rate</span>
              <el-tag type="info" size="small">Design: {{ systemData.designFlow }} L/s</el-tag>
            </div>
          </template>
          <div class="flow-stats">
            <div class="flow-value">{{ systemData.flowRate }} <span class="unit">L/s</span></div>
            <el-progress
                :percentage="systemData.flowPercent"
                :color="getFlowColor(systemData.flowPercent)"
                :stroke-width="16"
            />
            <div class="flow-details">
              <div class="flow-detail">
                <span>Demand Flow:</span>
                <span>{{ systemData.demandFlow }} L/s</span>
              </div>
              <div class="flow-detail">
                <span>Available Flow:</span>
                <span>{{ systemData.availableFlow }} L/s</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Active Alarms Section -->
    <div v-if="activeAlarms.length > 0" class="alarm-section">
      <div class="section-title">
        <span class="alarm-title">
          <el-icon><WarningFilled /></el-icon>
          Active Alarms
        </span>
        <el-badge :value="activeAlarms.length" type="danger" />
      </div>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" v-for="alarm in activeAlarms" :key="alarm.id">
          <div class="alarm-card" :class="alarm.severity">
            <div class="alarm-header">
              <span class="alarm-title-text">{{ alarm.title }}</span>
              <el-tag :type="alarm.severity === 'critical' ? 'danger' : 'warning'" size="small">
                {{ alarm.severity.toUpperCase() }}
              </el-tag>
            </div>
            <div class="alarm-message">{{ alarm.message }}</div>
            <div class="alarm-time">{{ alarm.time }}</div>
            <div class="alarm-actions">
              <el-button type="primary" size="small" @click="acknowledgeAlarm(alarm)">
                <el-icon><CircleCheck /></el-icon>
                Acknowledge
              </el-button>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- Fire Pump Cards -->
    <div class="section-title">
      <span>Fire Pump Units</span>
      <div class="filter-group">
        <el-radio-group v-model="pumpFilter" size="small">
          <el-radio-button label="all">All</el-radio-button>
          <el-radio-button label="running">Running</el-radio-button>
          <el-radio-button label="stopped">Stopped</el-radio-button>
          <el-radio-button label="fault">Fault</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <el-row :gutter="20" class="pumps-row">
      <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="pump in filteredPumps" :key="pump.id">
        <div class="pump-card" :class="pump.status">
          <div class="pump-header">
            <span class="pump-name">{{ pump.name }}</span>
            <div class="pump-status" :class="pump.status">
              <span class="status-dot"></span>
              {{ getPumpStatusText(pump.status) }}
            </div>
          </div>
          <div class="pump-icon">
            <el-icon :size="48" v-if="pump.status === 'running'"><VideoPlay /></el-icon>
            <el-icon :size="48" v-else-if="pump.status === 'stopped'"><VideoPause /></el-icon>
            <el-icon :size="48" v-else><WarningFilled /></el-icon>
          </div>
          <div class="pump-parameters">
            <div class="param">
              <span class="label">Type:</span>
              <span class="value">{{ pump.pumpType }}</span>
            </div>
            <div class="param">
              <span class="label">Flow:</span>
              <span class="value">{{ pump.flow }} L/s</span>
            </div>
            <div class="param">
              <span class="label">Pressure:</span>
              <span class="value">{{ pump.pressure }} bar</span>
            </div>
            <div class="param">
              <span class="label">Power:</span>
              <span class="value">{{ pump.power }} kW</span>
            </div>
            <div class="param">
              <span class="label">Speed:</span>
              <span class="value">{{ pump.speed }} rpm</span>
            </div>
          </div>
          <div class="pump-controls">
            <div class="mode-selector">
              <span>Mode:</span>
              <el-radio-group v-model="pump.mode" size="small" @change="changeMode(pump)">
                <el-radio-button label="auto">Auto</el-radio-button>
                <el-radio-button label="manual">Manual</el-radio-button>
              </el-radio-group>
            </div>
            <div class="control-buttons" v-if="pump.mode === 'manual'">
              <el-button
                  type="success"
                  size="small"
                  @click="controlPump(pump, 'start')"
                  :disabled="pump.status === 'running'"
              >
                <el-icon><VideoPlay /></el-icon>
                Start
              </el-button>
              <el-button
                  type="danger"
                  size="small"
                  @click="controlPump(pump, 'stop')"
                  :disabled="pump.status === 'stopped'"
              >
                <el-icon><VideoPause /></el-icon>
                Stop
              </el-button>
            </div>
            <div class="auto-status" v-else>
              <span>Auto-controlled by system</span>
            </div>
          </div>
          <div class="pump-footer">
            <span class="last-test">Last Test: {{ pump.lastTestDate }}</span>
            <el-button type="primary" link size="small" @click="viewPumpDetails(pump)">
              Details
            </el-button>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Weekly Test Schedule -->
    <el-card shadow="hover" class="schedule-card">
      <template #header>
        <div class="card-header">
          <span>Weekly Pump Test Schedule (NFPA 25 Compliance)</span>
          <el-tag type="success">Auto-Test Enabled</el-tag>
        </div>
      </template>
      <el-table :data="testSchedule" stripe border style="width: 100%">
        <el-table-column prop="day" label="Day" width="100" />
        <el-table-column prop="time" label="Time" width="100" />
        <el-table-column prop="pump" label="Pump" width="180" />
        <el-table-column prop="duration" label="Duration" width="100" />
        <el-table-column prop="lastResult" label="Last Result" width="120">
          <template #default="{ row }">
            <el-tag :type="row.lastResult === 'Pass' ? 'success' : 'danger'" size="small">
              {{ row.lastResult }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="nextTest" label="Next Test" width="160" />
        <el-table-column label="Action" width="100">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="runTest(row)">
              Run Test
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Performance Charts -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :md="14">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Pressure & Flow Trend (Last 24 Hours)</span>
              <el-radio-group v-model="chartPeriod" size="small" @change="updateTrendChart">
                <el-radio-button label="hour">Hourly</el-radio-button>
                <el-radio-button label="day">Daily</el-radio-button>
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
              <span>Pump Status Distribution</span>
            </div>
          </template>
          <div ref="statusChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Pump Details Table -->
    <el-card shadow="hover" class="table-card">
      <template #header>
        <div class="card-header">
          <span>Fire Pump Details</span>
          <el-input v-model="searchText" placeholder="Search pump..." style="width: 200px" clearable>
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </template>
      <el-table :data="paginatedPumps" stripe border style="width: 100%">
        <el-table-column prop="name" label="Pump Name" min-width="150" />
        <el-table-column prop="pumpType" label="Type" width="120" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getPumpStatusTag(row.status)" size="small">
              {{ getPumpStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="mode" label="Mode" width="80">
          <template #default="{ row }">
            <el-tag :type="row.mode === 'auto' ? 'primary' : 'warning'" size="small">
              {{ row.mode.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="flow" label="Flow (L/s)" width="100" sortable />
        <el-table-column prop="pressure" label="Pressure (bar)" width="110" sortable />
        <el-table-column prop="power" label="Power (kW)" width="100" sortable />
        <el-table-column prop="speed" label="Speed (rpm)" width="100" sortable />
        <el-table-column prop="runningHours" label="Run Hours" width="100" sortable />
        <el-table-column prop="lastTestDate" label="Last Test" width="120" />
        <el-table-column label="Actions" width="100">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewPumpDetails(row)">
              Details
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredTablePumps.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Pump Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Pump Details - ${selectedPump?.name}`" width="650px">
      <el-descriptions :column="2" border v-if="selectedPump">
        <el-descriptions-item label="Pump Name">{{ selectedPump.name }}</el-descriptions-item>
        <el-descriptions-item label="Pump Type">{{ selectedPump.pumpType }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getPumpStatusTag(selectedPump.status)">{{ getPumpStatusText(selectedPump.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Mode">
          <el-tag :type="selectedPump.mode === 'auto' ? 'primary' : 'warning'">{{ selectedPump.mode.toUpperCase() }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Flow Rate">{{ selectedPump.flow }} L/s</el-descriptions-item>
        <el-descriptions-item label="Pressure">{{ selectedPump.pressure }} bar</el-descriptions-item>
        <el-descriptions-item label="Power">{{ selectedPump.power }} kW</el-descriptions-item>
        <el-descriptions-item label="Speed">{{ selectedPump.speed }} rpm</el-descriptions-item>
        <el-descriptions-item label="Driver">{{ selectedPump.driver }}</el-descriptions-item>
        <el-descriptions-item label="Controller">{{ selectedPump.controller }}</el-descriptions-item>
        <el-descriptions-item label="Running Hours">{{ selectedPump.runningHours }} hrs</el-descriptions-item>
        <el-descriptions-item label="Start Count">{{ selectedPump.startCount }}</el-descriptions-item>
        <el-descriptions-item label="Last Test">{{ selectedPump.lastTestDate }}</el-descriptions-item>
        <el-descriptions-item label="Installation Date">{{ selectedPump.installDate }}</el-descriptions-item>
      </el-descriptions>
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
  Grid,
  VideoPlay,
  VideoPause,
  WarningFilled,
  CircleCheck,
  Search
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Initializing fire pump system...',
  'Checking pressure sensors...',
  'Almost ready...'
]

// ==================== Data State ====================
const chartPeriod = ref('hour')
const pumpFilter = ref('all')
const searchText = ref('')

interface FirePump {
  id: number
  name: string
  pumpType: string
  status: 'running' | 'stopped' | 'fault'
  mode: 'auto' | 'manual'
  flow: number
  pressure: number
  power: number
  speed: number
  driver: string
  controller: string
  runningHours: number
  startCount: number
  lastTestDate: string
  installDate: string
}

interface Alarm {
  id: number
  title: string
  message: string
  severity: 'critical' | 'warning'
  time: string
}

interface TestSchedule {
  day: string
  time: string
  pump: string
  duration: string
  lastResult: string
  nextTest: string
}

const pumps = ref<FirePump[]>([])
const activeAlarms = ref<Alarm[]>([])
const testSchedule = ref<TestSchedule[]>([])

const systemData = ref({
  pressure: 0,
  lowPressure: 5,
  highPressure: 12,
  flowRate: 0,
  designFlow: 150,
  demandFlow: 0,
  availableFlow: 0,
  flowPercent: 0
})

const stats = computed(() => ({
  total: pumps.value.length,
  running: pumps.value.filter(p => p.status === 'running').length,
  autoMode: pumps.value.filter(p => p.mode === 'auto').length,
  fault: pumps.value.filter(p => p.status === 'fault').length
}))

const filteredPumps = computed(() => {
  if (pumpFilter.value === 'all') return pumps.value
  return pumps.value.filter(p => p.status === pumpFilter.value)
})

const filteredTablePumps = computed(() => {
  if (!searchText.value) return pumps.value
  return pumps.value.filter(p =>
      p.name.toLowerCase().includes(searchText.value.toLowerCase()) ||
      p.pumpType.toLowerCase().includes(searchText.value.toLowerCase())
  )
})

const pagination = ref({ currentPage: 1, pageSize: 10 })
const paginatedPumps = computed(() => {
  const start = (pagination.value.currentPage - 1) * pagination.value.pageSize
  return filteredTablePumps.value.slice(start, start + pagination.value.pageSize)
})

// Generate mock pumps
const generatePumps = (): FirePump[] => {
  const pumpData = [
    { name: 'Main Electric Fire Pump', type: 'Electric Centrifugal', driver: 'Electric Motor', controller: 'Soft Starter' },
    { name: 'Diesel Engine Fire Pump', type: 'Diesel Engine', driver: 'Diesel Engine', controller: 'Diesel Controller' },
    { name: 'Jockey Pump', type: 'Centrifugal', driver: 'Electric Motor', controller: 'VFD' }
  ]

  return pumpData.map((p, idx) => {
    const statuses: ('running' | 'stopped' | 'fault')[] = ['stopped', 'stopped', 'running']
    const modes: ('auto' | 'manual')[] = ['auto', 'auto', 'auto']

    return {
      id: idx + 1,
      name: p.name,
      pumpType: p.type,
      status: statuses[idx],
      mode: modes[idx],
      flow: idx === 0 ? 120 : (idx === 1 ? 150 : 15),
      pressure: idx === 0 ? 8.5 : (idx === 1 ? 9.2 : 7.8),
      power: idx === 0 ? 110 : (idx === 1 ? 185 : 11),
      speed: idx === 0 ? 1480 : (idx === 1 ? 1500 : 1450),
      driver: p.driver,
      controller: p.controller,
      runningHours: Math.floor(100 + Math.random() * 500),
      startCount: Math.floor(50 + Math.random() * 200),
      lastTestDate: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      installDate: '2022-06-15'
    }
  })
}

// Generate system data
const updateSystemData = () => {
  const runningPumps = pumps.value.filter(p => p.status === 'running')
  const totalFlow = runningPumps.reduce((sum, p) => sum + p.flow, 0)

  systemData.value.pressure = parseFloat((7.5 + Math.random() * 2).toFixed(1))
  systemData.value.flowRate = totalFlow
  systemData.value.flowPercent = Math.min(100, Math.floor((totalFlow / systemData.value.designFlow) * 100))
  systemData.value.demandFlow = Math.floor(80 + Math.random() * 40)
  systemData.value.availableFlow = Math.floor(120 + Math.random() * 50)
}

// Generate alarms
const generateAlarms = (): Alarm[] => {
  const alarmsList = []

  // Check for low pressure
  if (systemData.value.pressure < systemData.value.lowPressure) {
    alarmsList.push({
      id: 1,
      title: 'Low System Pressure',
      message: `System pressure dropped to ${systemData.value.pressure} bar below minimum ${systemData.value.lowPressure} bar`,
      severity: 'critical',
      time: new Date().toLocaleString()
    })
  }

  // Random alarm for demo
  if (Math.random() > 0.7) {
    alarmsList.push({
      id: 2,
      title: 'Pump Controller Communication Error',
      message: 'Loss of communication with main fire pump controller',
      severity: 'warning',
      time: new Date().toLocaleString()
    })
  }

  return alarmsList
}

// Generate test schedule
const generateTestSchedule = (): TestSchedule[] => {
  const pumps_list = pumps.value
  return [
    { day: 'Monday', time: '09:00', pump: pumps_list[0]?.name || 'Main Pump', duration: '10 min', lastResult: 'Pass', nextTest: '2024-01-22 09:00' },
    { day: 'Wednesday', time: '14:00', pump: pumps_list[1]?.name || 'Diesel Pump', duration: '15 min', lastResult: 'Pass', nextTest: '2024-01-24 14:00' },
    { day: 'Friday', time: '11:00', pump: pumps_list[2]?.name || 'Jockey Pump', duration: '5 min', lastResult: 'Pass', nextTest: '2024-01-26 11:00' }
  ]
}

// Helper functions
const getPumpStatusText = (status: string) => {
  const map: Record<string, string> = { running: 'Running', stopped: 'Stopped', fault: 'Fault' }
  return map[status] || status
}

const getPumpStatusTag = (status: string) => {
  const map: Record<string, string> = { running: 'success', stopped: 'info', fault: 'danger' }
  return map[status] || 'info'
}

const getPressureStatus = computed(() => {
  const p = systemData.value.pressure
  if (p >= systemData.value.lowPressure && p <= systemData.value.highPressure) return 'success'
  if (p < systemData.value.lowPressure) return 'danger'
  return 'warning'
})

const getPressureStatusText = computed(() => {
  const p = systemData.value.pressure
  if (p >= systemData.value.lowPressure && p <= systemData.value.highPressure) return 'Normal'
  if (p < systemData.value.lowPressure) return 'Low Pressure'
  return 'High Pressure'
})

const getFlowColor = (percent: number) => {
  if (percent < 60) return '#E6A23C'
  if (percent < 90) return '#67C23A'
  return '#F56C6C'
}

// Actions
const detailDialogVisible = ref(false)
const selectedPump = ref<FirePump | null>(null)

const viewPumpDetails = (pump: FirePump) => {
  selectedPump.value = pump
  detailDialogVisible.value = true
}

const changeMode = (pump: FirePump) => {
  ElMessage.info(`Pump "${pump.name}" mode changed to ${pump.mode.toUpperCase()}`)
}

const controlPump = (pump: FirePump, action: 'start' | 'stop') => {
  const newStatus = action === 'start' ? 'running' : 'stopped'

  ElMessageBox.confirm(`${action === 'start' ? 'Start' : 'Stop'} pump "${pump.name}"?`, 'Confirm Control', {
    confirmButtonText: 'Confirm',
    cancelButtonText: 'Cancel',
    type: 'info'
  }).then(() => {
    pump.status = newStatus
    updateSystemData()
    updateStatusChart()
    updateTrendChart()
    ElMessage.success(`Pump "${pump.name}" ${action}ed successfully`)
  }).catch(() => {})
}

const acknowledgeAlarm = (alarm: Alarm) => {
  ElMessageBox.confirm(`Acknowledge alarm "${alarm.title}"?`, 'Confirm', {
    confirmButtonText: 'Acknowledge',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    activeAlarms.value = activeAlarms.value.filter(a => a.id !== alarm.id)
    ElMessage.success('Alarm acknowledged')
  }).catch(() => {})
}

const runTest = (schedule: TestSchedule) => {
  ElMessage.info(`Running test for ${schedule.pump}...`)
  setTimeout(() => {
    schedule.lastResult = Math.random() > 0.9 ? 'Fail' : 'Pass'
    const nextDate = new Date()
    nextDate.setDate(nextDate.getDate() + 7)
    schedule.nextTest = `${nextDate.toISOString().split('T')[0]} ${schedule.time}`
    ElMessage.success(`Test completed for ${schedule.pump}: ${schedule.lastResult}`)
  }, 2000)
}

// ==================== Chart Functions ====================
const pressureGaugeRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()
const statusChartRef = ref<HTMLElement>()

let pressureGauge: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null
let statusChart: echarts.ECharts | null = null

const initCharts = () => {
  nextTick(() => {
    if (pressureGaugeRef.value) {
      if (pressureGauge) pressureGauge.dispose()
      pressureGauge = echarts.init(pressureGaugeRef.value)
      updatePressureGauge()
    }

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

const updatePressureGauge = () => {
  pressureGauge?.setOption({
    series: [{
      type: 'gauge',
      center: ['50%', '50%'],
      radius: '70%',
      min: 0,
      max: 16,
      endAngle: 270,
      progress: { show: true, width: 15, itemStyle: { color: '#409EFF' } },
      axisLine: { lineStyle: { width: 15, color: [[0.3125, '#E6A23C'], [0.75, '#67C23A'], [1, '#F56C6C']] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      pointer: { show: true, length: '60%', width: 8, itemStyle: { color: '#1f2f3d' } },
      detail: { show: false },
      title: { show: false },
      data: [{ value: systemData.value.pressure, name: 'Pressure' }]
    }]
  })
}

const updateTrendChart = () => {
  let pressureData: number[] = []
  let flowData: number[] = []
  let xAxisData: string[] = []

  if (chartPeriod.value === 'hour') {
    xAxisData = Array.from({ length: 24 }, (_, i) => `${i}:00`)
    pressureData = Array.from({ length: 24 }, () => parseFloat((7 + Math.random() * 3).toFixed(1)))
    flowData = Array.from({ length: 24 }, () => Math.floor(50 + Math.random() * 80))
  } else {
    xAxisData = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    pressureData = [7.2, 7.5, 7.8, 8.0, 8.2, 7.6, 7.3]
    flowData = [65, 72, 78, 85, 90, 75, 68]
  }

  trendChart?.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['System Pressure (bar)', 'Flow Rate (L/s)'] },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: [
      { type: 'value', name: 'Pressure (bar)', min: 0, max: 16 },
      { type: 'value', name: 'Flow Rate (L/s)' }
    ],
    series: [
      {
        name: 'System Pressure (bar)',
        type: 'line',
        data: pressureData,
        smooth: true,
        lineStyle: { color: '#409EFF', width: 3 },
        yAxisIndex: 0,
        markLine: { data: [{ yAxis: systemData.value.lowPressure, name: 'Low', lineStyle: { color: '#E6A23C' } }] }
      },
      {
        name: 'Flow Rate (L/s)',
        type: 'bar',
        data: flowData,
        itemStyle: { borderRadius: [4, 4, 0, 0], color: '#67C23A' },
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
        { value: stats.value.running, name: 'Running', itemStyle: { color: '#67C23A' } },
        { value: stats.value.autoMode - stats.value.running, name: 'Stopped', itemStyle: { color: '#909399' } },
        { value: stats.value.fault, name: 'Fault', itemStyle: { color: '#F56C6C' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })
}

// ==================== Actions ====================
const refreshData = () => {
  pumps.value = generatePumps()
  updateSystemData()
  activeAlarms.value = generateAlarms()
  testSchedule.value = generateTestSchedule()
  updatePressureGauge()
  updateStatusChart()
  updateTrendChart()
  ElMessage.success('Data refreshed')
}

const handleExport = () => {
  ElMessage.success('Report export started')
}

const handleSizeChange = () => { pagination.value.currentPage = 1 }
const handleCurrentChange = () => {}

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
      pumps.value = generatePumps()
      updateSystemData()
      activeAlarms.value = generateAlarms()
      testSchedule.value = generateTestSchedule()
      initCharts()
    }, 400)
  }, 2000)
})

watch([trendChartRef, statusChartRef, pressureGaugeRef], () => {
  window.addEventListener('resize', () => {
    trendChart?.resize()
    statusChart?.resize()
    pressureGauge?.resize()
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
.fire-pumps-container {
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

.overview-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.overview-icon.total { background: rgba(64, 158, 255, 0.1); color: #409EFF; }
.overview-icon.running { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
.overview-icon.auto { background: rgba(230, 162, 60, 0.1); color: #E6A23C; }
.overview-icon.fault { background: rgba(245, 108, 108, 0.1); color: #F56C6C; }

.overview-info {
  flex: 1;
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

.overview-value.has-alarm { color: #F56C6C; }

/* Pressure & Flow Cards */
.pressure-row {
  margin-bottom: 24px;
}

.pressure-card, .flow-card {
  border-radius: 16px;
}

.pressure-gauge {
  display: flex;
  align-items: center;
  gap: 24px;
}

.gauge-container {
  flex: 1;
}

.gauge-chart {
  width: 100%;
  height: 180px;
}

.pressure-info {
  text-align: center;
  min-width: 120px;
}

.pressure-value {
  font-size: 36px;
  font-weight: 700;
  color: #409EFF;
}

.pressure-value .unit {
  font-size: 14px;
  font-weight: normal;
  color: #909399;
}

.pressure-range {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.pressure-range span {
  display: block;
}

.flow-stats {
  text-align: center;
}

.flow-value {
  font-size: 42px;
  font-weight: 700;
  color: #67C23A;
  margin-bottom: 16px;
}

.flow-value .unit {
  font-size: 14px;
  font-weight: normal;
  color: #909399;
}

.flow-details {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 16px;
  font-size: 13px;
  color: #606266;
}

.flow-detail span:first-child {
  color: #909399;
}

/* Alarm Section */
.alarm-section {
  margin-bottom: 24px;
}

.alarm-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #F56C6C;
  font-weight: 600;
}

.alarm-card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 20px;
  border-left: 4px solid #E6A23C;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.alarm-card.critical { border-left-color: #F56C6C; background: rgba(245, 108, 108, 0.02); }

.alarm-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.alarm-title-text {
  font-weight: 600;
  font-size: 15px;
}

.alarm-message {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.alarm-time {
  font-size: 11px;
  color: #c0c4cc;
  margin-bottom: 12px;
}

.alarm-actions {
  display: flex;
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

.filter-group {
  display: flex;
  gap: 12px;
}

/* Pump Cards */
.pumps-row {
  margin-bottom: 20px;
}

.pump-card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.3s ease;
  border-top: 3px solid #909399;
}

.pump-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(0,0,0,0.12);
}

.pump-card.running { border-top-color: #67C23A; }
.pump-card.stopped { border-top-color: #909399; }
.pump-card.fault { border-top-color: #F56C6C; background: rgba(245, 108, 108, 0.02); }

.pump-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.pump-name {
  font-weight: 600;
  font-size: 16px;
  color: #1f2f3d;
}

.pump-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 20px;
}

.pump-status.running { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
.pump-status.stopped { background: rgba(144, 147, 153, 0.1); color: #909399; }
.pump-status.fault { background: rgba(245, 108, 108, 0.1); color: #F56C6C; }

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.pump-icon {
  text-align: center;
  margin: 12px 0;
  color: #409EFF;
}

.pump-card.running .pump-icon { color: #67C23A; }
.pump-card.fault .pump-icon { color: #F56C6C; }

.pump-parameters {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 16px;
}

.param {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  font-size: 13px;
}

.param .label { color: #909399; }
.param .value { font-weight: 500; color: #606266; }

.pump-controls {
  margin-bottom: 12px;
}

.mode-selector {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
  font-size: 13px;
  color: #909399;
}

.control-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.auto-status {
  text-align: center;
  font-size: 12px;
  color: #909399;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 8px;
}

.pump-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: #c0c4cc;
  margin-top: 8px;
}

/* Schedule Card */
.schedule-card {
  border-radius: 16px;
  margin-bottom: 20px;
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

/* Table */
.table-card {
  border-radius: 16px;
}

.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>