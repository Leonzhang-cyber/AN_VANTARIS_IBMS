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
        <div class="loading-tip">Main Switchboard Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="main-switchboard-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Main Switchboard</h2>
        <p class="header-subtitle">LV Main Distribution Panel | 400V / 50Hz</p>
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

    <!-- Main Metrics Row -->
    <el-row :gutter="20" class="metrics-row">
      <el-col :xs="24" :sm="12" :md="6">
        <div class="metric-card total-power">
          <div class="metric-icon">
            <el-icon :size="32"><Lightning /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-label">Total Load</div>
            <div class="metric-value">{{ formatNumber(stats.totalPower) }} <span class="metric-unit">kW</span></div>
            <div class="metric-trend" :class="stats.powerTrend > 0 ? 'up' : 'down'">
              <el-icon><ArrowUp v-if="stats.powerTrend > 0" /><ArrowDown v-else /></el-icon>
              {{ Math.abs(stats.powerTrend) }}% vs last hour
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="metric-card current">
          <div class="metric-icon">
            <el-icon :size="32"><Connection /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-label">Total Current</div>
            <div class="metric-value">{{ formatNumber(stats.totalCurrent) }} <span class="metric-unit">A</span></div>
            <div class="metric-sub">R: {{ stats.currentR }}A | Y: {{ stats.currentY }}A | B: {{ stats.currentB }}A</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="metric-card voltage">
          <div class="metric-icon">
            <el-icon :size="32"><Histogram /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-label">Voltage (Avg)</div>
            <div class="metric-value">{{ stats.avgVoltage }} <span class="metric-unit">V</span></div>
            <div class="metric-sub">RY: {{ stats.voltageRY }}V | YB: {{ stats.voltageYB }}V | BR: {{ stats.voltageBR }}V</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="metric-card power-factor">
          <div class="metric-icon">
            <el-icon :size="32"><DataAnalysis /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-label">Power Factor</div>
            <div class="metric-value">{{ stats.powerFactor }} <span class="metric-unit">pf</span></div>
            <div class="metric-sub">THD: {{ stats.thd }}%</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Energy & Frequency Row -->
    <el-row :gutter="20" class="secondary-metrics">
      <el-col :xs="24" :sm="12" :md="8">
        <div class="info-card">
          <div class="info-header">
            <span class="info-title">Energy Consumption</span>
            <el-tag type="primary" size="small">Today</el-tag>
          </div>
          <div class="info-content">
            <div class="energy-value">{{ stats.energyToday }} <span class="unit">kWh</span></div>
            <div class="energy-stats">
              <span>This Month: {{ stats.energyMonth }} kWh</span>
              <span>This Year: {{ stats.energyYear }} kWh</span>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <div class="info-card">
          <div class="info-header">
            <span class="info-title">Frequency</span>
            <el-tag :type="stats.frequency >= 49.5 && stats.frequency <= 50.5 ? 'success' : 'danger'" size="small">
              {{ stats.frequency >= 49.5 && stats.frequency <= 50.5 ? 'Normal' : 'Abnormal' }}
            </el-tag>
          </div>
          <div class="info-content">
            <div class="frequency-value">{{ stats.frequency }} <span class="unit">Hz</span></div>
            <div class="frequency-range">Range: 49.5 - 50.5 Hz</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="8">
        <div class="info-card">
          <div class="info-header">
            <span class="info-title">Temperature</span>
            <el-tag :type="stats.temperature <= 40 ? 'success' : 'warning'" size="small">
              {{ stats.temperature <= 40 ? 'Normal' : 'High' }}
            </el-tag>
          </div>
          <div class="info-content">
            <div class="temp-value">{{ stats.temperature }} <span class="unit">°C</span></div>
            <div class="temp-range">Max Rating: 50°C</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Main Chart Row -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :md="16">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Power Consumption Trend (Last 24 Hours)</span>
              <el-radio-group v-model="chartPeriod" size="small" @change="updateChartPeriod">
                <el-radio-button label="hour">Hourly</el-radio-button>
                <el-radio-button label="day">Daily</el-radio-button>
                <el-radio-button label="week">Weekly</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="powerChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="8">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Load Distribution</span>
            </div>
          </template>
          <div ref="loadChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Feeder Breakers Section -->
    <el-card shadow="hover" class="breakers-card">
      <template #header>
        <div class="card-header">
          <span>Feeder Breakers</span>
          <el-tag type="info">{{ feederBreakers.length }} Feeders</el-tag>
        </div>
      </template>

      <el-row :gutter="16">
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="breaker in feederBreakers" :key="breaker.id">
          <div class="breaker-card" :class="breaker.status">
            <div class="breaker-header">
              <span class="breaker-name">{{ breaker.name }}</span>
              <el-tag :type="getBreakerStatusType(breaker.status)" size="small">
                {{ getBreakerStatusText(breaker.status) }}
              </el-tag>
            </div>
            <div class="breaker-details">
              <div class="breaker-detail">
                <span class="label">Load:</span>
                <span class="value">{{ breaker.load }} kW</span>
              </div>
              <div class="breaker-detail">
                <span class="label">Current:</span>
                <span class="value">{{ breaker.current }} A</span>
              </div>
              <div class="breaker-detail">
                <span class="label">Rating:</span>
                <span class="value">{{ breaker.rating }} A</span>
              </div>
            </div>
            <div class="breaker-progress">
              <el-progress
                  :percentage="breaker.loadPercent"
                  :color="getBreakerProgressColor(breaker.loadPercent)"
                  :stroke-width="8"
              />
            </div>
            <div class="breaker-actions">
              <el-switch
                  v-model="breaker.status"
                  active-value="closed"
                  inactive-value="open"
                  active-text="ON"
                  inactive-text="OFF"
                  @change="toggleBreaker(breaker)"
              />
              <el-button type="primary" link size="small" @click="viewBreakerDetails(breaker)">
                Details
              </el-button>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- Power Quality & Alarms -->
    <el-row :gutter="20">
      <el-col :xs="24" :md="14">
        <el-card shadow="hover" class="quality-card">
          <template #header>
            <div class="card-header">
              <span>Power Quality Metrics</span>
              <el-button text @click="refreshQuality">Refresh</el-button>
            </div>
          </template>
          <el-table :data="qualityMetrics" stripe border style="width: 100%">
            <el-table-column prop="phase" label="Phase" width="80" />
            <el-table-column prop="voltage" label="Voltage (V)" sortable>
              <template #default="{ row }">
                <span :class="getVoltageClass(row.voltage)">{{ row.voltage }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="current" label="Current (A)" sortable />
            <el-table-column prop="load" label="Load (kW)" sortable />
            <el-table-column prop="powerFactor" label="PF" sortable />
            <el-table-column prop="thd" label="THD (%)" sortable>
              <template #default="{ row }">
                <span :class="getThdClass(row.thd)">{{ row.thd }}%</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="10">
        <el-card shadow="hover" class="alarms-card">
          <template #header>
            <div class="card-header">
              <span>Active Alarms</span>
              <el-badge :value="activeAlarms.length" type="danger" v-if="activeAlarms.length > 0" />
            </div>
          </template>
          <div v-if="activeAlarms.length === 0" class="no-alarms">
            <el-icon :size="48"><SuccessFilled /></el-icon>
            <p>No active alarms</p>
          </div>
          <div v-else class="alarms-list">
            <div v-for="alarm in activeAlarms" :key="alarm.id" class="alarm-item" :class="alarm.severity">
              <div class="alarm-icon">
                <el-icon><WarningFilled /></el-icon>
              </div>
              <div class="alarm-info">
                <div class="alarm-title">{{ alarm.title }}</div>
                <div class="alarm-desc">{{ alarm.description }}</div>
                <div class="alarm-time">{{ alarm.time }}</div>
              </div>
              <div class="alarm-ack">
                <el-button type="primary" size="small" @click="acknowledgeAlarm(alarm)">Acknowledge</el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Breaker Detail Dialog -->
    <el-dialog v-model="breakerDialogVisible" :title="`Breaker Details - ${selectedBreaker?.name}`" width="500px">
      <el-descriptions :column="2" border v-if="selectedBreaker">
        <el-descriptions-item label="Breaker Name">{{ selectedBreaker.name }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getBreakerStatusType(selectedBreaker.status)">{{ getBreakerStatusText(selectedBreaker.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Load">{{ selectedBreaker.load }} kW</el-descriptions-item>
        <el-descriptions-item label="Current">{{ selectedBreaker.current }} A</el-descriptions-item>
        <el-descriptions-item label="Rated Current">{{ selectedBreaker.rating }} A</el-descriptions-item>
        <el-descriptions-item label="Load Percentage">{{ selectedBreaker.loadPercent }}%</el-descriptions-item>
        <el-descriptions-item label="Voltage">{{ selectedBreaker.voltage || 400 }} V</el-descriptions-item>
        <el-descriptions-item label="Power Factor">{{ selectedBreaker.powerFactor || 0.95 }}</el-descriptions-item>
        <el-descriptions-item label="Energy Today">{{ selectedBreaker.energyToday || 0 }} kWh</el-descriptions-item>
        <el-descriptions-item label="Last Trip">{{ selectedBreaker.lastTrip || 'Never' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Download,
  Refresh,
  Lightning,
  Connection,
  Histogram,
  DataAnalysis,
  ArrowUp,
  ArrowDown,
  WarningFilled,
  SuccessFilled
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Initializing switchboard...',
  'Loading feeder data...',
  'Almost ready...'
]

// ==================== Data State ====================
const chartPeriod = ref('hour')

const stats = ref({
  totalPower: 0,
  totalCurrent: 0,
  currentR: 0,
  currentY: 0,
  currentB: 0,
  avgVoltage: 0,
  voltageRY: 0,
  voltageYB: 0,
  voltageBR: 0,
  powerFactor: 0,
  thd: 0,
  powerTrend: 0,
  energyToday: 0,
  energyMonth: 0,
  energyYear: 0,
  frequency: 0,
  temperature: 0
})

interface FeederBreaker {
  id: number
  name: string
  status: 'closed' | 'open' | 'tripped'
  load: number
  current: number
  rating: number
  loadPercent: number
  voltage?: number
  powerFactor?: number
  energyToday?: number
  lastTrip?: string
}

const feederBreakers = ref<FeederBreaker[]>([])

const qualityMetrics = ref([
  { phase: 'R', voltage: 0, current: 0, load: 0, powerFactor: 0, thd: 0 },
  { phase: 'Y', voltage: 0, current: 0, load: 0, powerFactor: 0, thd: 0 },
  { phase: 'B', voltage: 0, current: 0, load: 0, powerFactor: 0, thd: 0 }
])

interface Alarm {
  id: number
  title: string
  description: string
  severity: 'critical' | 'major' | 'warning'
  time: string
}

const activeAlarms = ref<Alarm[]>([])

// Generate mock feeder breakers
const generateFeederBreakers = (): FeederBreaker[] => {
  const feeders = [
    'Main Incomer-1', 'Main Incomer-2', 'Lighting Panel', 'HVAC-1', 'HVAC-2',
    'Elevator-1', 'Elevator-2', 'Fire Pump', 'Data Center', 'Kitchen Equipment',
    'Workshop-1', 'Workshop-2', 'Office Lighting', 'Emergency Lighting', 'Chiller-1'
  ]

  return feeders.map((name, idx) => {
    const rating = [400, 400, 200, 250, 250, 160, 160, 250, 315, 200, 250, 250, 100, 100, 315][idx]
    const current = parseFloat((Math.random() * rating * 0.7 + rating * 0.1).toFixed(1))
    const loadPercent = parseFloat(((current / rating) * 100).toFixed(1))
    const statuses: ('closed' | 'open' | 'tripped')[] = ['closed', 'closed', 'closed', 'closed', 'closed', 'closed', 'open', 'closed', 'closed', 'closed', 'closed', 'tripped', 'closed', 'closed', 'closed']

    return {
      id: idx + 1,
      name: name,
      status: statuses[idx],
      load: parseFloat((current * 0.4).toFixed(1)),
      current: current,
      rating: rating,
      loadPercent: loadPercent,
      voltage: 400,
      powerFactor: parseFloat((0.85 + Math.random() * 0.1).toFixed(2)),
      energyToday: parseFloat((Math.random() * 500).toFixed(1)),
      lastTrip: idx === 11 ? '2024-01-15 14:30:22' : undefined
    }
  })
}

// Generate mock quality metrics
const generateQualityMetrics = () => {
  const baseVoltage = 400
  return [
    { phase: 'R', voltage: baseVoltage + (Math.random() - 0.5) * 10, current: parseFloat((250 + Math.random() * 100).toFixed(1)), load: parseFloat((80 + Math.random() * 40).toFixed(1)), powerFactor: parseFloat((0.85 + Math.random() * 0.1).toFixed(2)), thd: parseFloat((2 + Math.random() * 3).toFixed(1)) },
    { phase: 'Y', voltage: baseVoltage + (Math.random() - 0.5) * 10, current: parseFloat((240 + Math.random() * 100).toFixed(1)), load: parseFloat((78 + Math.random() * 38).toFixed(1)), powerFactor: parseFloat((0.85 + Math.random() * 0.1).toFixed(2)), thd: parseFloat((2 + Math.random() * 3).toFixed(1)) },
    { phase: 'B', voltage: baseVoltage + (Math.random() - 0.5) * 10, current: parseFloat((245 + Math.random() * 100).toFixed(1)), load: parseFloat((79 + Math.random() * 39).toFixed(1)), powerFactor: parseFloat((0.85 + Math.random() * 0.1).toFixed(2)), thd: parseFloat((2 + Math.random() * 3).toFixed(1)) }
  ]
}

// Generate mock alarms
const generateAlarms = (): Alarm[] => {
  return [
    { id: 1, title: 'Over Current Detected', description: 'Feeder HVACK-2 current exceeds threshold', severity: 'warning', time: '2 minutes ago' },
    { id: 2, title: 'Voltage Imbalance', description: 'Phase voltage deviation > 5%', severity: 'major', time: '15 minutes ago' },
    { id: 3, title: 'Temperature High', description: 'Switchboard temperature at 48°C', severity: 'critical', time: '32 minutes ago' }
  ]
}

// Update all stats
const updateStats = () => {
  const totalLoad = feederBreakers.value.reduce((sum, b) => sum + (b.status === 'closed' ? b.load : 0), 0)
  const totalCurrent = feederBreakers.value.reduce((sum, b) => sum + (b.status === 'closed' ? b.current : 0), 0)

  stats.value.totalPower = parseFloat(totalLoad.toFixed(1))
  stats.value.totalCurrent = parseFloat(totalCurrent.toFixed(1))

  // Per phase current (simulated distribution)
  stats.value.currentR = parseFloat((totalCurrent * 0.34).toFixed(1))
  stats.value.currentY = parseFloat((totalCurrent * 0.33).toFixed(1))
  stats.value.currentB = parseFloat((totalCurrent * 0.33).toFixed(1))

  // Voltages
  stats.value.avgVoltage = 400
  stats.value.voltageRY = 400
  stats.value.voltageYB = 399
  stats.value.voltageBR = 401

  stats.value.powerFactor = parseFloat((0.89 + Math.random() * 0.05).toFixed(2))
  stats.value.thd = parseFloat((2.5 + Math.random() * 2).toFixed(1))
  stats.value.powerTrend = parseFloat((Math.random() * 10 - 5).toFixed(1))

  stats.value.energyToday = parseFloat((Math.random() * 2000 + 1000).toFixed(1))
  stats.value.energyMonth = parseFloat((Math.random() * 50000 + 30000).toFixed(1))
  stats.value.energyYear = parseFloat((Math.random() * 500000 + 300000).toFixed(1))

  stats.value.frequency = parseFloat((49.8 + Math.random() * 0.8).toFixed(1))
  stats.value.temperature = parseFloat((35 + Math.random() * 15).toFixed(1))
}

// ==================== Chart Functions ====================
const powerChartRef = ref<HTMLElement>()
const loadChartRef = ref<HTMLElement>()
let powerChart: echarts.ECharts | null = null
let loadChart: echarts.ECharts | null = null

const initCharts = () => {
  nextTick(() => {
    if (powerChartRef.value) {
      if (powerChart) powerChart.dispose()
      powerChart = echarts.init(powerChartRef.value)
      updatePowerChart()
    }

    if (loadChartRef.value) {
      if (loadChart) loadChart.dispose()
      loadChart = echarts.init(loadChartRef.value)
      updateLoadChart()
    }
  })
}

const updatePowerChart = () => {
  let data: number[] = []
  let xAxisData: string[] = []

  if (chartPeriod.value === 'hour') {
    xAxisData = Array.from({ length: 24 }, (_, i) => `${i}:00`)
    data = Array.from({ length: 24 }, () => parseFloat((Math.random() * 100 + 50).toFixed(1)))
  } else if (chartPeriod.value === 'day') {
    xAxisData = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    data = [120, 135, 128, 142, 158, 135, 112]
  } else {
    xAxisData = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    data = [980, 1020, 1050, 1120]
  }

  powerChart?.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: { type: 'value', name: 'Power (kW)' },
    series: [{
      type: 'line',
      data: data,
      smooth: true,
      lineStyle: { color: '#409EFF', width: 3 },
      areaStyle: { opacity: 0.1 },
      symbol: 'circle',
      symbolSize: 6
    }]
  })
}

const updateLoadChart = () => {
  const categorySum = feederBreakers.value.reduce((sum, b) => sum + (b.status === 'closed' ? b.load : 0), 0)
  const lighting = feederBreakers.value.filter(b => b.name.includes('Lighting')).reduce((sum, b) => sum + (b.status === 'closed' ? b.load : 0), 0)
  const hvac = feederBreakers.value.filter(b => b.name.includes('HVAC')).reduce((sum, b) => sum + (b.status === 'closed' ? b.load : 0), 0)
  const elevators = feederBreakers.value.filter(b => b.name.includes('Elevator')).reduce((sum, b) => sum + (b.status === 'closed' ? b.load : 0), 0)
  const others = categorySum - lighting - hvac - elevators

  loadChart?.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: lighting, name: 'Lighting', itemStyle: { color: '#67C23A' } },
        { value: hvac, name: 'HVAC', itemStyle: { color: '#409EFF' } },
        { value: elevators, name: 'Elevators', itemStyle: { color: '#E6A23C' } },
        { value: others, name: 'Others', itemStyle: { color: '#909399' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })
}

const updateChartPeriod = () => {
  updatePowerChart()
}

// ==================== Breaker Functions ====================
const breakerDialogVisible = ref(false)
const selectedBreaker = ref<FeederBreaker | null>(null)

const getBreakerStatusType = (status: string) => {
  const map: Record<string, string> = { closed: 'success', open: 'info', tripped: 'danger' }
  return map[status] || 'info'
}

const getBreakerStatusText = (status: string) => {
  const map: Record<string, string> = { closed: 'ON', open: 'OFF', tripped: 'TRIPPED' }
  return map[status] || status
}

const getBreakerProgressColor = (percent: number) => {
  if (percent < 60) return '#67C23A'
  if (percent < 85) return '#E6A23C'
  return '#F56C6C'
}

const toggleBreaker = (breaker: FeederBreaker) => {
  ElMessage.success(`Breaker "${breaker.name}" turned ${breaker.status === 'closed' ? 'ON' : 'OFF'}`)
  updateStats()
  updateLoadChart()
}

const viewBreakerDetails = (breaker: FeederBreaker) => {
  selectedBreaker.value = breaker
  breakerDialogVisible.value = true
}

// ==================== Quality Metrics ====================
const getVoltageClass = (voltage: number) => {
  if (voltage >= 380 && voltage <= 420) return ''
  return 'warning-text'
}

const getThdClass = (thd: number) => {
  if (thd < 3) return ''
  if (thd < 5) return 'warning-text'
  return 'danger-text'
}

// ==================== Alarm Functions ====================
const acknowledgeAlarm = (alarm: Alarm) => {
  const index = activeAlarms.value.findIndex(a => a.id === alarm.id)
  if (index > -1) {
    activeAlarms.value.splice(index, 1)
    ElMessage.success(`Alarm "${alarm.title}" acknowledged`)
  }
}

// ==================== Actions ====================
const refreshQuality = () => {
  qualityMetrics.value = generateQualityMetrics()
  ElMessage.success('Quality metrics refreshed')
}

const refreshData = () => {
  feederBreakers.value = generateFeederBreakers()
  qualityMetrics.value = generateQualityMetrics()
  activeAlarms.value = generateAlarms()
  updateStats()
  updateLoadChart()
  updatePowerChart()
  ElMessage.success('Data refreshed')
}

const handleExport = () => {
  ElMessage.success('Report export started')
}

const formatNumber = (num: number) => {
  return num.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })
}

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
      feederBreakers.value = generateFeederBreakers()
      qualityMetrics.value = generateQualityMetrics()
      activeAlarms.value = generateAlarms()
      updateStats()
      initCharts()
    }, 400)
  }, 2000)
})

watch([powerChartRef, loadChartRef], () => {
  window.addEventListener('resize', () => {
    powerChart?.resize()
    loadChart?.resize()
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
.main-switchboard-container {
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

/* Metric Cards */
.metrics-row {
  margin-bottom: 20px;
}

.metric-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.metric-card.total-power { border-left: 4px solid #409EFF; }
.metric-card.current { border-left: 4px solid #67C23A; }
.metric-card.voltage { border-left: 4px solid #E6A23C; }
.metric-card.power-factor { border-left: 4px solid #909399; }

.metric-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(64, 158, 255, 0.1);
  color: #409EFF;
}

.metric-card.current .metric-icon {
  background: rgba(103, 194, 58, 0.1);
  color: #67C23A;
}

.metric-card.voltage .metric-icon {
  background: rgba(230, 162, 60, 0.1);
  color: #E6A23C;
}

.metric-card.power-factor .metric-icon {
  background: rgba(144, 147, 153, 0.1);
  color: #909399;
}

.metric-info { flex: 1; }
.metric-label { font-size: 13px; color: #909399; margin-bottom: 4px; }
.metric-value { font-size: 28px; font-weight: 700; color: #1f2f3d; }
.metric-unit { font-size: 14px; font-weight: normal; color: #909399; }
.metric-trend { font-size: 12px; margin-top: 6px; display: flex; align-items: center; gap: 4px; }
.metric-trend.up { color: #F56C6C; }
.metric-trend.down { color: #67C23A; }
.metric-sub { font-size: 11px; color: #909399; margin-top: 6px; }

/* Secondary Metrics */
.secondary-metrics { margin-bottom: 20px; }

.info-card {
  background: white;
  border-radius: 16px;
  padding: 16px 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.info-title { font-size: 14px; font-weight: 600; color: #606266; }
.energy-value, .frequency-value, .temp-value { font-size: 32px; font-weight: 700; color: #409EFF; }
.energy-value .unit, .frequency-value .unit, .temp-value .unit { font-size: 14px; font-weight: normal; color: #909399; }
.energy-stats, .frequency-range, .temp-range { font-size: 12px; color: #909399; margin-top: 8px; display: flex; gap: 16px; }

/* Charts */
.chart-row { margin-bottom: 20px; }
.chart-card { border-radius: 16px; }
.chart-container { width: 100%; height: 350px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }

/* Breakers Card */
.breakers-card { border-radius: 16px; margin-bottom: 20px; }

.breaker-card {
  background: #fafafa;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  transition: all 0.3s ease;
  border: 1px solid #e4e7ed;
}

.breaker-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.breaker-card.closed { border-left: 3px solid #67C23A; }
.breaker-card.open { border-left: 3px solid #909399; opacity: 0.7; }
.breaker-card.tripped { border-left: 3px solid #F56C6C; background: rgba(245, 108, 108, 0.05); }

.breaker-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.breaker-name { font-weight: 600; font-size: 14px; color: #1f2f3d; }
.breaker-details { margin-bottom: 12px; }
.breaker-detail { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px; }
.breaker-detail .label { color: #909399; }
.breaker-detail .value { font-weight: 500; color: #606266; }
.breaker-progress { margin-bottom: 12px; }
.breaker-actions { display: flex; justify-content: space-between; align-items: center; }

/* Quality & Alarms */
.quality-card, .alarms-card { border-radius: 16px; }

.warning-text { color: #E6A23C; font-weight: 500; }
.danger-text { color: #F56C6C; font-weight: 500; }

.no-alarms { text-align: center; padding: 40px; color: #909399; }
.no-alarms .el-icon { color: #67C23A; margin-bottom: 12px; }

.alarms-list { max-height: 400px; overflow-y: auto; }
.alarm-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  background: #fafafa;
  transition: all 0.2s;
}

.alarm-item:hover { background: #f5f5f5; }
.alarm-item.critical { border-left: 3px solid #F56C6C; }
.alarm-item.major { border-left: 3px solid #E6A23C; }
.alarm-item.warning { border-left: 3px solid #409EFF; }

.alarm-icon { color: #F56C6C; }
.alarm-item.major .alarm-icon { color: #E6A23C; }
.alarm-item.warning .alarm-icon { color: #409EFF; }

.alarm-info { flex: 1; }
.alarm-title { font-weight: 600; font-size: 14px; margin-bottom: 4px; }
.alarm-desc { font-size: 12px; color: #909399; margin-bottom: 4px; }
.alarm-time { font-size: 11px; color: #c0c4cc; }
.alarm-ack { display: flex; align-items: center; }
</style>