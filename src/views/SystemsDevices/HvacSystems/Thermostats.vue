<template>
  <!-- Global Pre Loading Screen -->
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
        <div class="loading-tip">THERMOSTAT SYSTEMS</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Page Content -->
  <div v-else class="thermostats-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/systems-devices/device-inventory' }">
            Systems & Devices
          </el-breadcrumb-item>
          <el-breadcrumb-item>HVAC Systems</el-breadcrumb-item>
          <el-breadcrumb-item>Thermostats</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button :icon="Refresh" @click="refreshData" :loading="refreshing">Refresh</el-button>
        <el-button type="primary" :icon="Download" @click="exportReport">Export Report</el-button>
      </div>
    </div>

    <!-- Overview Cards -->
    <div class="plant-overview">
      <div class="overview-card">
        <div class="overview-icon"><el-icon><Sunny /></el-icon></div>
        <div class="overview-info">
          <span class="overview-value">{{ thermostats.length }}</span>
          <span class="overview-label">Total Thermostats</span>
        </div>
      </div>
      <div class="overview-card">
        <div class="overview-icon running"><el-icon><CircleCheckFilled /></el-icon></div>
        <div class="overview-info">
          <span class="overview-value">{{ runningCount }}</span>
          <span class="overview-label">Active</span>
        </div>
        <div class="overview-trend up">{{ activePercent }}%</div>
      </div>
      <div class="overview-card">
        <div class="overview-icon"><el-icon><DataLine /></el-icon></div>
        <div class="overview-info">
          <span class="overview-value">{{ avgTemp.toFixed(1) }}</span>
          <span class="overview-label">Avg Room Temp (°C)</span>
        </div>
      </div>
      <div class="overview-card">
        <div class="overview-icon"><el-icon><TrendCharts /></el-icon></div>
        <div class="overview-info">
          <span class="overview-value">{{ energySaving.toFixed(0) }}</span>
          <span class="overview-label">Energy Saved (%)</span>
        </div>
      </div>
    </div>

    <!-- Thermostat Visualization Grid -->
    <div class="thermostats-visualization">
      <div class="thermostats-title">
        <h3><el-icon><OfficeBuilding /></el-icon> Thermostats - Overview</h3>
        <div class="thermostats-legend">
          <span><span class="legend-dot running"></span> Active</span>
          <span><span class="legend-dot standby"></span> Standby</span>
          <span><span class="legend-dot maintenance"></span> Maintenance</span>
          <span><span class="legend-dot offline"></span> Offline</span>
        </div>
      </div>

      <div class="thermostats-grid">
        <div v-for="thermostat in thermostats" :key="thermostat.id" class="thermostat-unit" :class="thermostat.status" @click="selectThermostat(thermostat)">
          <div class="thermostat-image">
            <img :src="thermostatImages[thermostat.status]" :alt="thermostat.name" class="thermostat-img" @error="handleImageError">
            <div class="status-badge" :class="thermostat.status"></div>
          </div>
          <div class="thermostat-info">
            <h4 class="thermostat-name">{{ thermostat.name }}</h4>
            <p class="thermostat-location"><el-icon><Location /></el-icon> {{ thermostat.location }}</p>
            <p class="thermostat-model">{{ thermostat.manufacturer }} {{ thermostat.model }}</p>
          </div>
          <div class="thermostat-metrics">
            <div class="metric">
              <span class="metric-label">Current</span>
              <span class="metric-value">{{ thermostat.currentTemp }}°C</span>
            </div>
            <div class="metric">
              <span class="metric-label">Setpoint</span>
              <span class="metric-value">{{ thermostat.setpoint }}°C</span>
            </div>
            <div class="metric">
              <span class="metric-label">Humidity</span>
              <span class="metric-value">{{ thermostat.humidity }}%</span>
            </div>
          </div>
          <div class="thermostat-footer">
            <div class="temp-indicator" :style="{ width: getTempPercent(thermostat) + '%' }"></div>
            <div class="thermostat-actions">
              <el-button size="small" text @click.stop="viewDetail(thermostat)">Details</el-button>
              <el-button size="small" text type="primary" @click.stop="controlThermostat(thermostat)">Control</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-section">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header-title">
            <span><el-icon><TrendCharts /></el-icon> Temperature Trend</span>
            <el-select v-model="trendThermostatId" placeholder="Select Thermostat" size="small" style="width: 180px" filterable @change="updateTempChart">
              <el-option v-for="thermostat in thermostats" :key="thermostat.id" :label="thermostat.name" :value="thermostat.id" />
            </el-select>
          </div>
        </template>
        <div ref="tempChartRef" class="temp-chart"></div>
      </el-card>

      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header-title">
            <span><el-icon><DataAnalysis /></el-icon> Temperature Distribution</span>
          </div>
        </template>
        <div ref="distChartRef" class="dist-chart"></div>
      </el-card>
    </div>

    <!-- Thermostats List -->
    <el-card shadow="hover">
      <template #header>
        <div class="card-header-title">Thermostats List</div>
      </template>
      <el-table :data="paginatedTableData" border stripe height="350" v-loading="tableLoading">
        <el-table-column label="Name" prop="name"  />
        <el-table-column label="Manufacturer" prop="manufacturer"  />
        <el-table-column label="Model" prop="model" />
        <el-table-column label="Type" prop="thermostatType" >
          <template #default="scope">
            <el-tag size="small">{{ scope.row.thermostatType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Status" prop="status" >
          <template #default="scope">
            <div class="status-cell">
              <span class="status-dot" :class="scope.row.status"></span>
              <span>{{ scope.row.status.toUpperCase() }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Current" prop="currentTemp" >
          <template #default="scope">{{ scope.row.currentTemp }}°C</template>
        </el-table-column>
        <el-table-column label="Setpoint" prop="setpoint" >
          <template #default="scope">{{ scope.row.setpoint }}°C</template>
        </el-table-column>
        <el-table-column label="Humidity" prop="humidity" >
          <template #default="scope">{{ scope.row.humidity }}%</template>
        </el-table-column>
        <el-table-column label="Mode" prop="mode" >
          <template #default="scope">
            <el-tag :type="scope.row.mode === 'Cool' ? 'primary' : 'warning'" size="small">{{ scope.row.mode }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Fan" prop="fanStatus" >
          <template #default="scope">{{ scope.row.fanStatus }}</template>
        </el-table-column>
        <el-table-column label="Energy" prop="energyToday" >
          <template #default="scope">{{ scope.row.energyToday.toLocaleString() }} kWh</template>
        </el-table-column>
        <el-table-column label="Operation" width="160" fixed="right" align="center">
          <template #default="scope">
            <el-button text type="primary" size="small" @click="viewDetail(scope.row)">Detail</el-button>
            <el-button text type="warning" size="small" @click="controlThermostat(scope.row)">Control</el-button>
            <el-button text type="danger" size="small" @click="showAlarms(scope.row)">Alarms</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap">
        <el-pagination
            v-model:current-page="pageInfo.pageNum"
            v-model:page-size="pageInfo.pageSize"
            :page-sizes="[10, 20, 30, 50]"
            :total="pageInfo.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handlePageSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- Thermostat Details Drawer -->
    <el-drawer v-model="detailDrawerVisible" :title="selectedThermostat?.name" size="40%" direction="rtl">
      <div v-if="selectedThermostat" class="thermostat-detail">
        <div class="detail-header">
          <div class="detail-status" :class="selectedThermostat.status">
            <span class="status-dot-large"></span>
            <span>{{ selectedThermostat.status.toUpperCase() }}</span>
          </div>
          <h2>{{ selectedThermostat.name }}</h2>
          <p>{{ selectedThermostat.manufacturer }} {{ selectedThermostat.model }}</p>
        </div>

        <el-divider />

        <div class="detail-metrics">
          <div class="metric-row">
            <div class="metric-card">
              <span class="metric-label">Current Temp</span>
              <span class="metric-value">{{ selectedThermostat.currentTemp }} <span class="metric-unit">°C</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Setpoint</span>
              <span class="metric-value">{{ selectedThermostat.setpoint }} <span class="metric-unit">°C</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Temperature Delta</span>
              <span class="metric-value">{{ Math.abs(selectedThermostat.currentTemp - selectedThermostat.setpoint).toFixed(1) }} <span class="metric-unit">°C</span></span>
            </div>
          </div>
          <div class="metric-row">
            <div class="metric-card">
              <span class="metric-label">Humidity</span>
              <span class="metric-value">{{ selectedThermostat.humidity }}<span class="metric-unit">%</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Mode</span>
              <span class="metric-value">{{ selectedThermostat.mode }}</span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Fan Status</span>
              <span class="metric-value">{{ selectedThermostat.fanStatus }}</span>
            </div>
          </div>
          <div class="metric-row">
            <div class="metric-card">
              <span class="metric-label">Schedule</span>
              <span class="metric-value">{{ selectedThermostat.schedule }}</span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Energy Today</span>
              <span class="metric-value">{{ selectedThermostat.energyToday.toLocaleString() }}<span class="metric-unit">kWh</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Battery</span>
              <span class="metric-value">{{ selectedThermostat.battery }}<span class="metric-unit">%</span></span>
            </div>
          </div>
        </div>

        <el-divider />

        <div class="detail-chart">
          <h4>Temperature Trend (Last 24 Hours)</h4>
          <div ref="detailChartRef" class="detail-chart-container"></div>
        </div>

        <el-divider />

        <div class="detail-actions">
          <el-button type="primary" @click="controlThermostat(selectedThermostat)">Control Thermostat</el-button>
          <el-button @click="viewAlarms(selectedThermostat)">View Alarms</el-button>
          <el-button @click="exportThermostatData(selectedThermostat)">Export Data</el-button>
        </div>
      </div>
    </el-drawer>

    <!-- Control Dialog -->
    <el-dialog v-model="controlDialogVisible" :title="`Control - ${selectedThermostat?.name}`" width="450px">
      <el-form :model="controlForm" label-width="120px">
        <el-form-item label="Operation Mode">
          <el-radio-group v-model="controlForm.mode">
            <el-radio label="auto">Auto</el-radio>
            <el-radio label="manual">Manual</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Temperature Setpoint">
          <el-input-number v-model="controlForm.setpoint" :min="16" :max="30" :step="0.5" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Fan Speed">
          <el-select v-model="controlForm.fanSpeed" style="width: 100%">
            <el-option label="Auto" value="auto" />
            <el-option label="Low" value="low" />
            <el-option label="Medium" value="medium" />
            <el-option label="High" value="high" />
          </el-select>
        </el-form-item>
        <el-form-item label="System Mode">
          <el-radio-group v-model="controlForm.systemMode">
            <el-radio label="heat">Heat</el-radio>
            <el-radio label="cool">Cool</el-radio>
            <el-radio label="auto">Auto</el-radio>
            <el-radio label="off">Off</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Commands">
          <el-button-group>
            <el-button type="success" @click="sendCommand('start')" :disabled="selectedThermostat?.status === 'running'">Turn On</el-button>
            <el-button type="warning" @click="sendCommand('stop')" :disabled="selectedThermostat?.status !== 'running'">Turn Off</el-button>
          </el-button-group>
        </el-form-item>
      </el-form>
    </el-dialog>

    <!-- Alarms Dialog -->
    <el-dialog v-model="alarmDialogVisible" :title="`Alarms - ${selectedThermostat?.name}`" width="600px">
      <el-table :data="selectedThermostat?.alarms || []" stripe border>
        <el-table-column prop="timestamp" label="Time" width="160" />
        <el-table-column prop="severity" label="Severity" >
          <template #default="scope">
            <el-tag :type="scope.row.severity === 'critical' ? 'danger' : 'warning'" size="small">{{ scope.row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="code" label="Code"  />
        <el-table-column prop="message" label="Message" min-width="200" />
        <el-table-column prop="status" label="Status" >
          <template #default="scope">
            <span :class="scope.row.status === 'active' ? 'text-danger' : 'text-success'">{{ scope.row.status }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Refresh, Download, Sunny, CircleCheckFilled, DataLine,
  TrendCharts, OfficeBuilding, Location, DataAnalysis
} from '@element-plus/icons-vue'

// ========== Loading State ==========
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading thermostat systems...')
const loadingMessages = [
  'Initializing thermostats...',
  'Loading device data...',
  'Connecting to controllers...',
  'Rendering system layout...',
  'Almost ready...'
]

// ========== Chart References ==========
const tempChartRef = ref<HTMLDivElement | null>(null)
const distChartRef = ref<HTMLDivElement | null>(null)
const detailChartRef = ref<HTMLDivElement | null>(null)
let tempChart: echarts.ECharts | null = null
let distChart: echarts.ECharts | null = null
let detailChart: echarts.ECharts | null = null
let refreshTimer: number | null = null
const refreshing = ref(false)
const tableLoading = ref(false)
const trendThermostatId = ref('')

// ========== Thermostat Images ==========
const thermostatImages = {
  running: 'https://aegisnx.com/wp-content/uploads/2026/05/52013144312.webp',
  standby: 'https://aegisnx.com/wp-content/uploads/2026/05/52013144312.webp',
  maintenance: 'https://aegisnx.com/wp-content/uploads/2026/05/52013144312.webp',
  offline: 'https://aegisnx.com/wp-content/uploads/2026/05/52013144312.webp',
  default: 'https://aegisnx.com/wp-content/uploads/2026/05/52013144312.webp'
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  if (thermostatImages.default) {
    img.src = thermostatImages.default
  }
}

// ========== Dialog State ==========
const detailDrawerVisible = ref(false)
const controlDialogVisible = ref(false)
const alarmDialogVisible = ref(false)
const selectedThermostat = ref<any>(null)
const controlForm = reactive({
  mode: 'auto',
  setpoint: 22,
  fanSpeed: 'auto',
  systemMode: 'auto'
})

// ========== Thermostat Data ==========
interface Thermostat {
  id: string
  name: string
  manufacturer: string
  model: string
  thermostatType: string
  status: 'running' | 'standby' | 'maintenance' | 'offline'
  currentTemp: number
  setpoint: number
  humidity: number
  mode: string
  fanStatus: string
  schedule: string
  battery: number
  energyToday: number
  energyMonth: number
  location: string
  alarms: any[]
}

const thermostats = ref<Thermostat[]>([
  { id: '1', name: 'Office-201 Thermostat', manufacturer: 'Honeywell', model: 'T9', thermostatType: 'Smart', status: 'running', currentTemp: 22.5, setpoint: 22.0, humidity: 52, mode: 'Cool', fanStatus: 'Auto', schedule: 'Business Hours', battery: 85, energyToday: 12.5, energyMonth: 375, location: 'Office 2F', alarms: [] },
  { id: '2', name: 'Conference Room A', manufacturer: 'Nest', model: 'Learning', thermostatType: 'Smart', status: 'running', currentTemp: 21.8, setpoint: 22.0, humidity: 48, mode: 'Cool', fanStatus: 'Auto', schedule: 'Meeting Schedule', battery: 92, energyToday: 10.2, energyMonth: 306, location: 'Office 2F', alarms: [] },
  { id: '3', name: 'Lobby Thermostat', manufacturer: 'Ecobee', model: 'SmartThermostat', thermostatType: 'Smart', status: 'running', currentTemp: 23.2, setpoint: 22.5, humidity: 55, mode: 'Cool', fanStatus: 'On', schedule: '24/7', battery: 78, energyToday: 18.5, energyMonth: 555, location: 'Lobby 1F', alarms: [] },
  { id: '4', name: 'Executive Office', manufacturer: 'Honeywell', model: 'Lyric', thermostatType: 'Smart', status: 'running', currentTemp: 22.0, setpoint: 22.0, humidity: 50, mode: 'Auto', fanStatus: 'Auto', schedule: 'Flex', battery: 95, energyToday: 8.5, energyMonth: 255, location: 'Executive 3F', alarms: [] },
  { id: '5', name: 'Break Room', manufacturer: 'Nest', model: 'E', thermostatType: 'Smart', status: 'running', currentTemp: 23.5, setpoint: 23.0, humidity: 58, mode: 'Cool', fanStatus: 'Auto', schedule: 'Business Hours', battery: 88, energyToday: 15.2, energyMonth: 456, location: 'Office 2F', alarms: [] },
  { id: '6', name: 'Server Room', manufacturer: 'Ecobee', model: 'SmartSensor', thermostatType: 'Commercial', status: 'running', currentTemp: 19.5, setpoint: 20.0, humidity: 45, mode: 'Cool', fanStatus: 'On', schedule: '24/7', battery: 100, energyToday: 25.0, energyMonth: 750, location: 'Basement B2', alarms: [] },
  { id: '7', name: 'Waiting Area', manufacturer: 'Honeywell', model: 'T5', thermostatType: 'Standard', status: 'standby', currentTemp: 24.0, setpoint: 22.0, humidity: 60, mode: 'Off', fanStatus: 'Auto', schedule: 'Occasional', battery: 65, energyToday: 0, energyMonth: 0, location: 'Lobby 1F', alarms: [] },
  { id: '8', name: 'Storage Room', manufacturer: 'Nest', model: 'Thermostat E', thermostatType: 'Standard', status: 'maintenance', currentTemp: 18.0, setpoint: 20.0, humidity: 62, mode: 'Off', fanStatus: 'Off', schedule: 'None', battery: 45, energyToday: 0, energyMonth: 0, location: 'Basement B2', alarms: [{ timestamp: '2026-06-01 08:00:00', severity: 'critical', code: 'E-701', message: 'Low battery - replace', status: 'active' }] }
])

const runningCount = computed(() => thermostats.value.filter(t => t.status === 'running').length)
const activePercent = computed(() => thermostats.value.length ? Math.round(runningCount.value / thermostats.value.length * 100) : 0)
const avgTemp = computed(() => {
  const running = thermostats.value.filter(t => t.status === 'running')
  if (running.length === 0) return 0
  return running.reduce((sum, t) => sum + t.currentTemp, 0) / running.length
})
const energySaving = computed(() => {
  // 模拟节能计算
  return 15 + Math.random() * 10
})

const paginatedTableData = computed(() => {
  const start = (pageInfo.pageNum - 1) * pageInfo.pageSize
  return thermostats.value.slice(start, start + pageInfo.pageSize)
})

const pageInfo = reactive({
  pageNum: 1,
  pageSize: 10,
  total: thermostats.value.length
})

const getTempPercent = (thermostat: Thermostat) => {
  // 将温度转换为进度百分比 (假设温度范围 10-35°C)
  const percent = ((thermostat.currentTemp - 10) / 25) * 100
  return Math.min(100, Math.max(0, percent))
}

const getLoadColor = (load: number) => {
  if (load < 30) return '#67c23a'
  if (load < 70) return '#409eff'
  return '#e6a23c'
}

// 生成温度趋势数据
const generateTempData = (thermostatId: string) => {
  const thermostat = thermostats.value.find(t => t.id === thermostatId)
  if (!thermostat) return { timestamps: [], currentTemp: [], setpoint: [], humidity: [] }

  const timestamps = []
  const currentTemp = []
  const setpoint = []
  const humidity = []
  const now = new Date()

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    timestamps.push(`${String(time.getHours()).padStart(2, '0')}:00`)

    const tempVar = thermostat.currentTemp + Math.sin(i * 0.3) * 1.2 + (Math.random() - 0.5) * 0.5
    const setVar = thermostat.setpoint + Math.sin(i * 0.2) * 0.3
    const humVar = thermostat.humidity + Math.sin(i * 0.3) * 3 + (Math.random() - 0.5) * 2

    currentTemp.push(Number(tempVar.toFixed(1)))
    setpoint.push(Number(setVar.toFixed(1)))
    humidity.push(Math.min(80, Math.max(30, Number(humVar.toFixed(0)))))
  }

  return { timestamps, currentTemp, setpoint, humidity }
}

// 生成温度分布数据
const generateTempDistribution = () => {
  const running = thermostats.value.filter(t => t.status === 'running')
  const ranges = [
    { name: '< 18°C', value: running.filter(t => t.currentTemp < 18).length },
    { name: '18-20°C', value: running.filter(t => t.currentTemp >= 18 && t.currentTemp < 20).length },
    { name: '20-22°C', value: running.filter(t => t.currentTemp >= 20 && t.currentTemp < 22).length },
    { name: '22-24°C', value: running.filter(t => t.currentTemp >= 22 && t.currentTemp < 24).length },
    { name: '24-26°C', value: running.filter(t => t.currentTemp >= 24 && t.currentTemp < 26).length },
    { name: '≥ 26°C', value: running.filter(t => t.currentTemp >= 26).length }
  ]
  return ranges.filter(r => r.value > 0)
}

// 初始化温度图表
const initTempChart = async () => {
  await nextTick()
  if (!tempChartRef.value) {
    setTimeout(() => initTempChart(), 100)
    return
  }

  if (tempChart) tempChart.dispose()

  if (thermostats.value.length > 0 && !trendThermostatId.value) {
    trendThermostatId.value = thermostats.value[0].id
  }

  tempChart = echarts.init(tempChartRef.value)
  updateTempChart()
}

const updateTempChart = () => {
  if (!tempChart || !trendThermostatId.value) return

  const data = generateTempData(trendThermostatId.value)

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Room Temp (°C)', 'Setpoint (°C)', 'Humidity (%)'], bottom: 0 },
    grid: { top: 30, right: 20, bottom: 40, left: 50, containLabel: true },
    xAxis: { type: 'category', data: data.timestamps, axisLabel: { rotate: 45, interval: 4, fontSize: 10 } },
    yAxis: [
      { type: 'value', name: 'Temperature (°C)', position: 'left', min: 0, max: 40 },
      { type: 'value', name: 'Humidity (%)', position: 'right', min: 0, max: 100 }
    ],
    series: [
      { name: 'Room Temp (°C)', type: 'line', data: data.currentTemp, smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Setpoint (°C)', type: 'line', data: data.setpoint, smooth: true, lineStyle: { color: '#f56c6c', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Humidity (%)', type: 'line', yAxisIndex: 1, data: data.humidity, smooth: true, lineStyle: { color: '#67c23a', width: 2 }, areaStyle: { opacity: 0.1 } }
    ]
  }
  tempChart.setOption(option, true)
}

// 初始化分布图表（条形图）
const initDistChart = async () => {
  await nextTick()
  if (!distChartRef.value) {
    setTimeout(() => initDistChart(), 100)
    return
  }

  if (distChart) distChart.dispose()
  distChart = echarts.init(distChartRef.value)

  const data = generateTempDistribution()

  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, right: 20, bottom: 30, left: 50, containLabel: true },
    xAxis: { type: 'category', data: data.map(d => d.name), axisLabel: { rotate: 45, fontSize: 11 } },
    yAxis: { type: 'value', name: 'Number of Thermostats' },
    series: [{
      name: 'Thermostats',
      type: 'bar',
      data: data.map(d => d.value),
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#409eff' },
      label: { show: true, position: 'top' }
    }]
  }
  distChart.setOption(option)
}

const updateDistChart = () => {
  if (!distChart) return
  const data = generateTempDistribution()
  distChart.setOption({
    xAxis: { data: data.map(d => d.name) },
    series: [{ data: data.map(d => d.value) }]
  })
}

// 生成单个恒温器趋势数据
const generateThermostatTrendData = (thermostat: Thermostat) => {
  const timestamps = []
  const currentTemp = []
  const setpoint = []
  const now = new Date()

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    timestamps.push(`${String(time.getHours()).padStart(2, '0')}:00`)

    const tempVar = thermostat.currentTemp + Math.sin(i * 0.3) * 1 + (Math.random() - 0.5) * 0.4
    const setVar = thermostat.setpoint + Math.sin(i * 0.2) * 0.2

    currentTemp.push(Number(tempVar.toFixed(1)))
    setpoint.push(Number(setVar.toFixed(1)))
  }

  return { timestamps, currentTemp, setpoint }
}

// 初始化详情图表
const initDetailChart = () => {
  if (!detailChartRef.value || !selectedThermostat.value) return
  if (detailChart) detailChart.dispose()

  detailChart = echarts.init(detailChartRef.value)
  const data = generateThermostatTrendData(selectedThermostat.value)

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Room Temp (°C)', 'Setpoint (°C)'], bottom: 0 },
    grid: { top: 30, right: 20, bottom: 40, left: 50, containLabel: true },
    xAxis: { type: 'category', data: data.timestamps, axisLabel: { rotate: 45, interval: 4, fontSize: 10 } },
    yAxis: { type: 'value', name: 'Temperature (°C)', min: 10, max: 30 },
    series: [
      { name: 'Room Temp (°C)', type: 'line', data: data.currentTemp, smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Setpoint (°C)', type: 'line', data: data.setpoint, smooth: true, lineStyle: { color: '#f56c6c', width: 2 }, areaStyle: { opacity: 0.1 } }
    ]
  }
  detailChart.setOption(option)
}

// 更新实时数据
const updateRealtimeData = () => {
  for (const thermostat of thermostats.value) {
    if (thermostat.status === 'running') {
      const tempChange = (Math.random() - 0.5) * 0.3
      thermostat.currentTemp = Number((thermostat.currentTemp + tempChange).toFixed(1))

      const humChange = (Math.random() - 0.5) * 2
      thermostat.humidity = Math.min(80, Math.max(30, thermostat.humidity + humChange))

      // 模拟节能计算
      const energyDelta = 0.1 + Math.random() * 0.2
      thermostat.energyToday += energyDelta
      thermostat.energyMonth += energyDelta

      // 模拟电池消耗
      thermostat.battery = Math.max(0, thermostat.battery - 0.01)
    }
  }
}

// 刷新图表
const updateCharts = () => {
  updateTempChart()
  updateDistChart()
}

// 窗口大小适配
const handleResize = () => {
  if (tempChart) tempChart.resize()
  if (distChart) distChart.resize()
  if (detailChart) detailChart.resize()
}

// Actions
const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 500))
  updateRealtimeData()
  updateCharts()
  tableLoading.value = false
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

const handlePageSizeChange = () => {
  pageInfo.pageNum = 1
}

const handlePageChange = () => {}

const selectThermostat = (thermostat: Thermostat) => {
  selectedThermostat.value = thermostat
  detailDrawerVisible.value = true
  setTimeout(() => initDetailChart(), 100)
}

const viewDetail = (thermostat: Thermostat) => {
  selectThermostat(thermostat)
}

const controlThermostat = (thermostat: Thermostat) => {
  selectedThermostat.value = thermostat
  controlForm.setpoint = thermostat.setpoint
  controlForm.systemMode = thermostat.mode.toLowerCase()
  controlDialogVisible.value = true
}

const sendCommand = (command: string) => {
  ElMessage.success(`${command.toUpperCase()} command sent to ${selectedThermostat.value.name}`)
  if (command === 'start') {
    selectedThermostat.value.status = 'running'
    selectedThermostat.value.mode = 'Auto'
    selectedThermostat.value.fanStatus = 'Auto'
  } else if (command === 'stop') {
    selectedThermostat.value.status = 'standby'
    selectedThermostat.value.mode = 'Off'
    selectedThermostat.value.fanStatus = 'Off'
  }
  controlDialogVisible.value = false
  updateCharts()
}

const showAlarms = (thermostat: Thermostat) => {
  selectedThermostat.value = thermostat
  alarmDialogVisible.value = true
}

const viewAlarms = (thermostat: Thermostat) => {
  showAlarms(thermostat)
}

const exportThermostatData = (thermostat: Thermostat) => {
  ElMessage.success(`Exporting data for ${thermostat.name}`)
}

const exportReport = () => {
  ElMessage.success('Exporting thermostats report')
}

// 自动刷新
const startAutoRefresh = () => {
  refreshTimer = window.setInterval(() => {
    updateRealtimeData()
    updateCharts()
  }, 5000)
}

// ========== Lifecycle ==========
onMounted(async () => {
  let msgIdx = 0
  const msgInt = setInterval(() => {
    if (msgIdx < loadingMessages.length - 1) {
      msgIdx++
      loadingMessage.value = loadingMessages[msgIdx]
    }
  }, 400)

  const progInt = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)

  setTimeout(async () => {
    clearInterval(msgInt)
    clearInterval(progInt)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(async () => {
      isLoaded.value = true
      await nextTick()
      setTimeout(() => {
        initTempChart()
        initDistChart()
        startAutoRefresh()
        window.addEventListener('resize', handleResize)
      }, 200)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
  if (tempChart) tempChart.dispose()
  if (distChart) distChart.dispose()
  if (detailChart) detailChart.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped lang="scss">
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

.loading-spinner { position: relative; width: 80px; height: 80px; margin: 0 auto 24px; }
.spinner-ring { position: absolute; width: 100%; height: 100%; border-radius: 50%; border: 3px solid transparent; animation: spin 1.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite; }
.spinner-ring:nth-child(1) { border-top-color: #3b82f6; animation-delay: 0s; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

.loading-text { margin-bottom: 24px; font-size: 28px; font-weight: 700; color: #e2e8f0; display: flex; justify-content: center; align-items: baseline; gap: 4px; }
.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce { 0%, 80%, 100% { transform: scale(0); opacity: 0.3; } 40% { transform: scale(1); opacity: 1; } }

.loading-progress { width: 280px; height: 4px; background: rgba(255, 255, 255, 0.1); border-radius: 4px; overflow: hidden; margin: 0 auto 16px; }
.progress-bar { height: 100%; background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec489a); border-radius: 4px; transition: width 0.3s ease; background-size: 200% auto; animation: shimmer 2s linear infinite; }
@keyframes shimmer { 0% { background-position: 0% 0%; } 100% { background-position: 200% 0%; } }

.loading-tip { font-size: 13px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 8px; font-weight: 500; }
.loading-subtip { font-size: 11px; color: #64748b; letter-spacing: 0.5px; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

/* Page Content */
.thermostats-container { padding: 20px; background: #f5f7fa; min-height: 100%; }

.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }

.plant-overview { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 24px; }
.overview-card { background: white; border-radius: 16px; padding: 20px; display: flex; align-items: center; gap: 16px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); transition: all 0.3s ease; }
.overview-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
.overview-icon .el-icon { font-size: 36px; color: #409eff; }
.overview-icon.running .el-icon { color: #67c23a; }
.overview-info { flex: 1; }
.overview-value { font-size: 28px; font-weight: 700; color: #1e293b; }
.overview-label { font-size: 13px; color: #64748b; display: block; }
.overview-trend { font-size: 14px; font-weight: 600; }
.overview-trend.up { color: #67c23a; }

/* Thermostats Visualization */
.thermostats-visualization { background: white; border-radius: 20px; padding: 20px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.thermostats-title { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.thermostats-title h3 { display: flex; align-items: center; gap: 8px; margin: 0; font-size: 18px; }
.thermostats-legend { display: flex; gap: 20px; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 6px; }
.legend-dot.running { background: #67c23a; box-shadow: 0 0 4px #67c23a; }
.legend-dot.standby { background: #409eff; }
.legend-dot.maintenance { background: #e6a23c; }
.legend-dot.offline { background: #f56c6c; }

.thermostats-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
.thermostat-unit { background: #f8fafc; border-radius: 16px; padding: 16px; cursor: pointer; transition: all 0.3s ease; border-left: 4px solid; position: relative; overflow: hidden; }
.thermostat-unit.running { border-left-color: #67c23a; background: linear-gradient(135deg, #f8fafc, #f0fdf4); }
.thermostat-unit.standby { border-left-color: #409eff; }
.thermostat-unit.maintenance { border-left-color: #e6a23c; background: linear-gradient(135deg, #f8fafc, #fefce8); }
.thermostat-unit.offline { border-left-color: #f56c6c; background: linear-gradient(135deg, #f8fafc, #fef2f2); opacity: 0.8; }
.thermostat-unit:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); }

.thermostat-image { position: relative; display: flex; justify-content: center; margin-bottom: 12px; }
.thermostat-img { width: 100px; height: 100px; object-fit: contain; }
.status-badge { position: absolute; top: 0; right: 0; width: 12px; height: 12px; border-radius: 50%; }
.status-badge.running { background: #67c23a; box-shadow: 0 0 8px #67c23a; animation: pulse 2s infinite; }
.status-badge.standby { background: #409eff; }
.status-badge.maintenance { background: #e6a23c; }
.status-badge.offline { background: #f56c6c; }

.thermostat-info { text-align: center; margin-bottom: 12px; }
.thermostat-name { margin: 0 0 4px 0; font-size: 16px; font-weight: 600; color: #1e293b; }
.thermostat-location { margin: 0; font-size: 11px; color: #64748b; display: flex; align-items: center; justify-content: center; gap: 4px; }
.thermostat-model { margin: 4px 0 0 0; font-size: 11px; color: #94a3b8; }

.thermostat-metrics { display: flex; justify-content: space-around; margin-bottom: 12px; padding: 8px 0; border-top: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; }
.metric { text-align: center; }
.metric-label { display: block; font-size: 10px; color: #64748b; }
.metric-value { font-size: 14px; font-weight: 600; color: #1e293b; }

.thermostat-footer { margin-top: 8px; }
.temp-indicator { height: 3px; background: linear-gradient(90deg, #409eff, #67c23a); border-radius: 3px; transition: width 0.3s ease; }
.thermostat-actions { display: flex; justify-content: center; gap: 8px; margin-top: 8px; }

/* Charts Section */
.charts-section { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }
.chart-card { border-radius: 16px; }
.card-header-title { display: flex; justify-content: space-between; align-items: center; font-weight: 600; color: #1e293b; font-size: 16px; flex-wrap: wrap; gap: 12px; }
.temp-chart, .dist-chart { width: 100%; height: 320px; }

/* Status Cell */
.status-cell { display: flex; align-items: center; gap: 6px; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; }
.status-dot.running { background: #67c23a; box-shadow: 0 0 4px #67c23a; animation: pulse 2s infinite; }
.status-dot.standby { background: #409eff; }
.status-dot.maintenance { background: #e6a23c; }
.status-dot.offline { background: #f56c6c; }

/* Drawer Styles */
.thermostat-detail { padding: 8px; }
.detail-header { text-align: center; margin-bottom: 16px; }
.detail-status { display: inline-flex; align-items: center; gap: 8px; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; margin-bottom: 12px; }
.detail-status.running { background: #f0fdf4; color: #67c23a; }
.detail-status.standby { background: #eff6ff; color: #409eff; }
.detail-status.maintenance { background: #fefce8; color: #e6a23c; }
.detail-status.offline { background: #fef2f2; color: #f56c6c; }
.status-dot-large { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.detail-header h2 { margin: 8px 0 4px 0; font-size: 20px; }
.detail-header p { margin: 0; color: #64748b; font-size: 13px; }

.detail-metrics { display: flex; flex-direction: column; gap: 12px; }
.metric-row { display: flex; gap: 12px; }
.metric-card { flex: 1; background: #f8fafc; border-radius: 12px; padding: 12px; text-align: center; }
.metric-card .metric-label { font-size: 11px; color: #64748b; display: block; margin-bottom: 4px; }
.metric-card .metric-value { font-size: 18px; font-weight: 700; color: #1e293b; }
.metric-unit { font-size: 12px; font-weight: normal; color: #64748b; }

.detail-chart { margin-top: 16px; }
.detail-chart h4 { margin: 0 0 12px 0; font-size: 14px; }
.detail-chart-container { width: 100%; height: 200px; }

.detail-actions { display: flex; gap: 12px; margin-top: 16px; flex-wrap: wrap; }

.pagination-wrap { margin-top: 16px; display: flex; justify-content: flex-end; }

.text-danger { color: #f56c6c; }
.text-success { color: #67c23a; }

@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

@media (max-width: 1200px) {
  .plant-overview { grid-template-columns: repeat(2, 1fr); }
  .charts-section { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .thermostats-container { padding: 12px; }
  .plant-overview { grid-template-columns: 1fr; }
  .thermostats-grid { grid-template-columns: 1fr; }
  .thermostats-title { flex-direction: column; align-items: flex-start; }
  .metric-row { flex-wrap: wrap; }
  .temp-chart, .dist-chart { height: 250px; }
}
</style>