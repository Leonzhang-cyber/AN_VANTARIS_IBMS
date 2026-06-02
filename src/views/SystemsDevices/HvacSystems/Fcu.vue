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
        <div class="loading-tip">FCU SYSTEMS</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Page Content -->
  <div v-else class="fcu-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/systems-devices/device-inventory' }">
            Systems & Devices
          </el-breadcrumb-item>
          <el-breadcrumb-item>HVAC Systems</el-breadcrumb-item>
          <el-breadcrumb-item>Fan Coil Units</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button :icon="Refresh" @click="refreshData" :loading="refreshing">Refresh</el-button>
        <el-button type="primary" :icon="Download" @click="exportReport">Export Report</el-button>
      </div>
    </div>

    <!-- Plant Overview Cards -->
    <div class="plant-overview">
      <div class="overview-card">
        <div class="overview-icon"><el-icon><WindPower /></el-icon></div>
        <div class="overview-info">
          <span class="overview-value">{{ fcUs.length }}</span>
          <span class="overview-label">Total FCUs</span>
        </div>
      </div>
      <div class="overview-card">
        <div class="overview-icon running"><el-icon><CircleCheckFilled /></el-icon></div>
        <div class="overview-info">
          <span class="overview-value">{{ runningCount }}</span>
          <span class="overview-label">Running</span>
        </div>
        <div class="overview-trend up">{{ runningPercent }}%</div>
      </div>
      <div class="overview-card">
        <div class="overview-icon"><el-icon><DataLine /></el-icon></div>
        <div class="overview-info">
          <span class="overview-value">{{ avgRoomTemp.toFixed(1) }}</span>
          <span class="overview-label">Avg Room Temp (°C)</span>
        </div>
      </div>
      <div class="overview-card">
        <div class="overview-icon"><el-icon><TrendCharts /></el-icon></div>
        <div class="overview-info">
          <span class="overview-value">{{ totalEnergy.toLocaleString() }}</span>
          <span class="overview-label">Total Energy (kWh)</span>
        </div>
      </div>
    </div>

    <!-- FCU Visualization Grid -->
    <div class="fcu-visualization">
      <div class="fcu-title">
        <h3><el-icon><OfficeBuilding /></el-icon> Fan Coil Units - Overview</h3>
        <div class="fcu-legend">
          <span><span class="legend-dot running"></span> Running</span>
          <span><span class="legend-dot standby"></span> Standby</span>
          <span><span class="legend-dot maintenance"></span> Maintenance</span>
          <span><span class="legend-dot offline"></span> Offline</span>
        </div>
      </div>

      <div class="fcu-grid">
        <div v-for="fcu in fcUs" :key="fcu.id" class="fcu-unit" :class="fcu.status" @click="selectFCU(fcu)">
          <div class="fcu-image">
            <img :src="fcuImages[fcu.status]" :alt="fcu.name" class="fcu-img" @error="handleImageError">
            <div class="status-badge" :class="fcu.status"></div>
          </div>
          <div class="fcu-info">
            <h4 class="fcu-name">{{ fcu.name }}</h4>
            <p class="fcu-location"><el-icon><Location /></el-icon> {{ fcu.location }}</p>
            <p class="fcu-model">{{ fcu.manufacturer }} {{ fcu.model }}</p>
          </div>
          <div class="fcu-metrics">
            <div class="metric">
              <span class="metric-label">Room Temp</span>
              <span class="metric-value">{{ fcu.roomTemp }}°C</span>
            </div>
            <div class="metric">
              <span class="metric-label">Setpoint</span>
              <span class="metric-value">{{ fcu.setpoint }}°C</span>
            </div>
            <div class="metric">
              <span class="metric-label">Fan Speed</span>
              <span class="metric-value">{{ fcu.fanSpeed }}%</span>
            </div>
          </div>
          <div class="fcu-footer">
            <el-progress :percentage="fcu.load" :stroke-width="6" :color="getLoadColor(fcu.load)" :show-text="false" />
            <div class="fcu-actions">
              <el-button size="small" text @click.stop="viewDetail(fcu)">Details</el-button>
              <el-button size="small" text type="primary" @click.stop="controlFCU(fcu)">Control</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Charts -->
    <div class="charts-section">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header-title">
            <span><el-icon><TrendCharts /></el-icon> Temperature Trend</span>
            <el-select v-model="trendFCUId" placeholder="Select FCU" size="small" style="width: 180px" filterable @change="updateTempChart">
              <el-option v-for="fcu in fcUs" :key="fcu.id" :label="fcu.name" :value="fcu.id" />
            </el-select>
          </div>
        </template>
        <div ref="tempChartRef" class="temp-chart"></div>
      </el-card>

      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header-title">
            <span><el-icon><DataAnalysis /></el-icon> Fan Speed Distribution</span>
          </div>
        </template>
        <div ref="fanChartRef" class="fan-chart"></div>
      </el-card>
    </div>

    <!-- FCU List -->
    <el-card shadow="hover">
      <template #header>
        <div class="card-header-title">Fan Coil Units List</div>
      </template>
      <el-table :data="paginatedTableData" border stripe height="350" v-loading="tableLoading">
        <el-table-column label="Name" prop="name"  />
        <el-table-column label="Manufacturer" prop="manufacturer"  />
        <el-table-column label="Model" prop="model"  />
        <el-table-column label="Type" prop="fcuType" >
          <template #default="scope">
            <el-tag size="small">{{ scope.row.fcuType }}</el-tag>
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
        <el-table-column label="Room Temp" prop="roomTemp" >
          <template #default="scope">{{ scope.row.roomTemp }}°C</template>
        </el-table-column>
        <el-table-column label="Setpoint" prop="setpoint" >
          <template #default="scope">{{ scope.row.setpoint }}°C</template>
        </el-table-column>
        <el-table-column label="Fan Speed" prop="fanSpeed" >
          <template #default="scope">
            <el-progress :percentage="scope.row.fanSpeed" :stroke-width="6" :color="getLoadColor(scope.row.fanSpeed)" :show-text="false" style="width: 80px" />
            <span style="margin-left: 8px">{{ scope.row.fanSpeed }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="Valve" prop="valvePosition" >
          <template #default="scope">{{ scope.row.valvePosition }}%</template>
        </el-table-column>
        <el-table-column label="Energy" prop="energyToday" width="110">
          <template #default="scope">{{ scope.row.energyToday.toLocaleString() }} kWh</template>
        </el-table-column>
        <el-table-column label="Operation" width="160" fixed="right">
          <template #default="scope">
            <el-button text type="primary" size="small" @click="viewDetail(scope.row)">Detail</el-button>
            <el-button text type="warning" size="small" @click="controlFCU(scope.row)">Control</el-button>
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

    <!-- FCU Details Drawer -->
    <el-drawer v-model="detailDrawerVisible" :title="selectedFCU?.name" size="40%" direction="rtl">
      <div v-if="selectedFCU" class="fcu-detail">
        <div class="detail-header">
          <div class="detail-status" :class="selectedFCU.status">
            <span class="status-dot-large"></span>
            <span>{{ selectedFCU.status.toUpperCase() }}</span>
          </div>
          <h2>{{ selectedFCU.name }}</h2>
          <p>{{ selectedFCU.manufacturer }} {{ selectedFCU.model }}</p>
        </div>

        <el-divider />

        <div class="detail-metrics">
          <div class="metric-row">
            <div class="metric-card">
              <span class="metric-label">Room Temp</span>
              <span class="metric-value">{{ selectedFCU.roomTemp }} <span class="metric-unit">°C</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Setpoint</span>
              <span class="metric-value">{{ selectedFCU.setpoint }} <span class="metric-unit">°C</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Delta T</span>
              <span class="metric-value">{{ Math.abs(selectedFCU.roomTemp - selectedFCU.setpoint).toFixed(1) }} <span class="metric-unit">°C</span></span>
            </div>
          </div>
          <div class="metric-row">
            <div class="metric-card">
              <span class="metric-label">Fan Speed</span>
              <span class="metric-value">{{ selectedFCU.fanSpeed }}<span class="metric-unit">%</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Valve Position</span>
              <span class="metric-value">{{ selectedFCU.valvePosition }}<span class="metric-unit">%</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Energy Today</span>
              <span class="metric-value">{{ selectedFCU.energyToday.toLocaleString() }}<span class="metric-unit">kWh</span></span>
            </div>
          </div>
          <div class="metric-row">
            <div class="metric-card">
              <span class="metric-label">Mode</span>
              <span class="metric-value">{{ selectedFCU.mode }}</span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Filter Status</span>
              <span class="metric-value">{{ selectedFCU.filterStatus }}</span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Runtime</span>
              <span class="metric-value">{{ selectedFCU.runtime }} hours</span>
            </div>
          </div>
        </div>

        <el-divider />

        <div class="detail-chart">
          <h4>Performance Trend (Last 24 Hours)</h4>
          <div ref="detailChartRef" class="detail-chart-container"></div>
        </div>

        <el-divider />

        <div class="detail-actions">
          <el-button type="primary" @click="controlFCU(selectedFCU)">Control FCU</el-button>
          <el-button @click="viewAlarms(selectedFCU)">View Alarms</el-button>
          <el-button @click="exportFCUData(selectedFCU)">Export Data</el-button>
        </div>
      </div>
    </el-drawer>

    <!-- Control Dialog -->
    <el-dialog v-model="controlDialogVisible" :title="`Control - ${selectedFCU?.name}`" width="450px">
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
          <el-slider v-model="controlForm.fanSpeed" :min="0" :max="100" :step="5" />
        </el-form-item>
        <el-form-item label="Commands">
          <el-button-group>
            <el-button type="success" @click="sendCommand('start')" :disabled="selectedFCU?.status === 'running'">Start</el-button>
            <el-button type="warning" @click="sendCommand('stop')" :disabled="selectedFCU?.status !== 'running'">Stop</el-button>
            <el-button type="primary" @click="sendCommand('reset')">Reset</el-button>
          </el-button-group>
        </el-form-item>
      </el-form>
    </el-dialog>

    <!-- Alarms Dialog -->
    <el-dialog v-model="alarmDialogVisible" :title="`Alarms - ${selectedFCU?.name}`" width="600px">
      <el-table :data="selectedFCU?.alarms || []" stripe border>
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
  Refresh, Download, WindPower, CircleCheckFilled, DataLine,
  TrendCharts, OfficeBuilding, Location, DataAnalysis
} from '@element-plus/icons-vue'

// ========== Loading State ==========
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading FCU systems...')
const loadingMessages = [
  'Initializing FCU systems...',
  'Loading unit data...',
  'Connecting to controllers...',
  'Rendering system layout...',
  'Almost ready...'
]

// ========== Chart References ==========
const tempChartRef = ref<HTMLDivElement | null>(null)
const fanChartRef = ref<HTMLDivElement | null>(null)
const detailChartRef = ref<HTMLDivElement | null>(null)
let tempChart: echarts.ECharts | null = null
let fanChart: echarts.ECharts | null = null
let detailChart: echarts.ECharts | null = null
let refreshTimer: number | null = null
const refreshing = ref(false)
const tableLoading = ref(false)
const trendFCUId = ref('')

// ========== FCU Images ==========
const fcuImages = {
  running: 'https://aegisnx.com/wp-content/uploads/2026/05/52013141234431.webp',
  standby: 'https://aegisnx.com/wp-content/uploads/2026/05/52013141234431.webp',
  maintenance: 'https://aegisnx.com/wp-content/uploads/2026/05/52013141234431.webp',
  offline: 'https://aegisnx.com/wp-content/uploads/2026/05/52013141234431.webp',
  default: 'https://aegisnx.com/wp-content/uploads/2026/05/52013141234431.webp'
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  if (fcuImages.default) {
    img.src = fcuImages.default
  }
}

// ========== Dialog State ==========
const detailDrawerVisible = ref(false)
const controlDialogVisible = ref(false)
const alarmDialogVisible = ref(false)
const selectedFCU = ref<any>(null)
const controlForm = reactive({
  mode: 'auto',
  setpoint: 22,
  fanSpeed: 60
})

// ========== FCU Data ==========
interface FCU {
  id: string
  name: string
  manufacturer: string
  model: string
  fcuType: string
  status: 'running' | 'standby' | 'maintenance' | 'offline'
  roomTemp: number
  setpoint: number
  fanSpeed: number
  valvePosition: number
  mode: string
  filterStatus: string
  runtime: number
  load: number
  energyToday: number
  energyMonth: number
  location: string
  alarms: any[]
}

const fcUs = ref<FCU[]>([
  { id: '1', name: 'FCU-B2-01', manufacturer: 'Daikin', model: 'FXMQ', fcuType: 'Cassette', status: 'running', roomTemp: 22.5, setpoint: 22.0, fanSpeed: 65, valvePosition: 72, mode: 'Cool', filterStatus: 'Clean', runtime: 3650, load: 68, energyToday: 42, energyMonth: 1260, location: 'Basement B2', alarms: [] },
  { id: '2', name: 'FCU-B2-02', manufacturer: 'Daikin', model: 'FXMQ', fcuType: 'Cassette', status: 'running', roomTemp: 22.8, setpoint: 22.0, fanSpeed: 58, valvePosition: 68, mode: 'Cool', filterStatus: 'Clean', runtime: 3580, load: 62, energyToday: 38, energyMonth: 1140, location: 'Basement B2', alarms: [] },
  { id: '3', name: 'FCU-1F-01', manufacturer: 'Carrier', model: '42Q', fcuType: 'Ceiling', status: 'running', roomTemp: 23.2, setpoint: 22.5, fanSpeed: 72, valvePosition: 78, mode: 'Cool', filterStatus: 'Clean', runtime: 4120, load: 75, energyToday: 56, energyMonth: 1680, location: 'Lobby 1F', alarms: [] },
  { id: '4', name: 'FCU-1F-02', manufacturer: 'Carrier', model: '42Q', fcuType: 'Ceiling', status: 'running', roomTemp: 23.0, setpoint: 22.5, fanSpeed: 68, valvePosition: 75, mode: 'Cool', filterStatus: 'Clean', runtime: 3980, load: 71, energyToday: 52, energyMonth: 1560, location: 'Lobby 1F', alarms: [] },
  { id: '5', name: 'FCU-2F-01', manufacturer: 'Trane', model: 'GEHB', fcuType: 'Vertical', status: 'running', roomTemp: 22.2, setpoint: 22.0, fanSpeed: 55, valvePosition: 62, mode: 'Cool', filterStatus: 'Clean', runtime: 2850, load: 58, energyToday: 35, energyMonth: 1050, location: 'Office 2F', alarms: [] },
  { id: '6', name: 'FCU-2F-02', manufacturer: 'Trane', model: 'GEHB', fcuType: 'Vertical', status: 'standby', roomTemp: 23.5, setpoint: 22.0, fanSpeed: 0, valvePosition: 0, mode: 'Off', filterStatus: 'Clean', runtime: 2750, load: 0, energyToday: 0, energyMonth: 0, location: 'Office 2F', alarms: [] },
  { id: '7', name: 'FCU-3F-01', manufacturer: 'Daikin', model: 'FXMQ', fcuType: 'Cassette', status: 'maintenance', roomTemp: 24.5, setpoint: 22.5, fanSpeed: 0, valvePosition: 0, mode: 'Off', filterStatus: 'Dirty', runtime: 5200, load: 0, energyToday: 0, energyMonth: 0, location: 'Executive 3F', alarms: [{ timestamp: '2026-06-01 11:00:00', severity: 'critical', code: 'E-401', message: 'Filter clogged - replace immediately', status: 'active' }] },
  { id: '8', name: 'FCU-3F-02', manufacturer: 'Daikin', model: 'FXMQ', fcuType: 'Cassette', status: 'running', roomTemp: 21.8, setpoint: 22.0, fanSpeed: 62, valvePosition: 58, mode: 'Heat', filterStatus: 'Clean', runtime: 2450, load: 65, energyToday: 48, energyMonth: 1440, location: 'Executive 3F', alarms: [] }
])

const runningCount = computed(() => fcUs.value.filter(f => f.status === 'running').length)
const runningPercent = computed(() => fcUs.value.length ? Math.round(runningCount.value / fcUs.value.length * 100) : 0)
const avgRoomTemp = computed(() => {
  const running = fcUs.value.filter(f => f.status === 'running')
  if (running.length === 0) return 0
  return running.reduce((sum, f) => sum + f.roomTemp, 0) / running.length
})
const totalEnergy = computed(() => fcUs.value.reduce((sum, f) => sum + f.energyToday, 0))

const paginatedTableData = computed(() => {
  const start = (pageInfo.pageNum - 1) * pageInfo.pageSize
  return fcUs.value.slice(start, start + pageInfo.pageSize)
})

const pageInfo = reactive({
  pageNum: 1,
  pageSize: 10,
  total: fcUs.value.length
})

const getLoadColor = (load: number) => {
  if (load < 30) return '#67c23a'
  if (load < 70) return '#409eff'
  return '#e6a23c'
}

// 生成温度趋势数据
const generateTempData = (fcuId: string) => {
  const fcu = fcUs.value.find(f => f.id === fcuId)
  if (!fcu) return { timestamps: [], roomTemp: [], setpoint: [] }

  const timestamps = []
  const roomTemp = []
  const setpoint = []
  const now = new Date()

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    timestamps.push(`${String(time.getHours()).padStart(2, '0')}:00`)

    const roomVar = fcu.roomTemp + Math.sin(i * 0.3) * 0.8 + (Math.random() - 0.5) * 0.4
    const setVar = fcu.setpoint + Math.sin(i * 0.2) * 0.3

    roomTemp.push(Number(roomVar.toFixed(1)))
    setpoint.push(Number(setVar.toFixed(1)))
  }

  return { timestamps, roomTemp, setpoint }
}

// 生成风扇速度分布数据
const generateFanSpeedData = () => {
  const speedRanges = [
    { name: '0-20%', value: fcUs.value.filter(f => f.fanSpeed <= 20 && f.status === 'running').length },
    { name: '21-40%', value: fcUs.value.filter(f => f.fanSpeed > 20 && f.fanSpeed <= 40 && f.status === 'running').length },
    { name: '41-60%', value: fcUs.value.filter(f => f.fanSpeed > 40 && f.fanSpeed <= 60 && f.status === 'running').length },
    { name: '61-80%', value: fcUs.value.filter(f => f.fanSpeed > 60 && f.fanSpeed <= 80 && f.status === 'running').length },
    { name: '81-100%', value: fcUs.value.filter(f => f.fanSpeed > 80 && f.status === 'running').length }
  ]
  return speedRanges.filter(r => r.value > 0)
}

// 初始化温度图表
const initTempChart = async () => {
  await nextTick()
  if (!tempChartRef.value) {
    setTimeout(() => initTempChart(), 100)
    return
  }

  if (tempChart) tempChart.dispose()

  if (fcUs.value.length > 0 && !trendFCUId.value) {
    trendFCUId.value = fcUs.value[0].id
  }

  tempChart = echarts.init(tempChartRef.value)
  updateTempChart()
}

const updateTempChart = () => {
  if (!tempChart || !trendFCUId.value) return

  const data = generateTempData(trendFCUId.value)

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Room Temp (°C)', 'Setpoint (°C)'], bottom: 0 },
    grid: { top: 30, right: 20, bottom: 40, left: 50, containLabel: true },
    xAxis: { type: 'category', data: data.timestamps, axisLabel: { rotate: 45, interval: 4, fontSize: 10 } },
    yAxis: { type: 'value', name: 'Temperature (°C)' },
    series: [
      { name: 'Room Temp (°C)', type: 'line', data: data.roomTemp, smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Setpoint (°C)', type: 'line', data: data.setpoint, smooth: true, lineStyle: { color: '#f56c6c', width: 2 }, areaStyle: { opacity: 0.1 } }
    ]
  }
  tempChart.setOption(option, true)
}

// 初始化风扇速度分布图表（饼图）
const initFanChart = async () => {
  await nextTick()
  if (!fanChartRef.value) {
    setTimeout(() => initFanChart(), 100)
    return
  }

  if (fanChart) fanChart.dispose()
  fanChart = echarts.init(fanChartRef.value)

  const data = generateFanSpeedData()

  const option = {
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c})' },
    legend: { orient: 'vertical', left: 'left', data: data.map(d => d.name) },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: data,
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}', position: 'outside' }
    }]
  }
  fanChart.setOption(option)
}

const updateFanChart = () => {
  if (!fanChart) return
  const data = generateFanSpeedData()
  fanChart.setOption({
    series: [{ data: data }],
    legend: { data: data.map(d => d.name) }
  })
}

// 生成单个FCU趋势数据
const generateFCUTrendData = (fcu: FCU) => {
  const timestamps = []
  const roomTemp = []
  const fanSpeed = []
  const now = new Date()

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    timestamps.push(`${String(time.getHours()).padStart(2, '0')}:00`)

    const tempVar = fcu.roomTemp + Math.sin(i * 0.3) * 0.8 + (Math.random() - 0.5) * 0.3
    const speedVar = fcu.fanSpeed + Math.sin(i * 0.3) * 8 + (Math.random() - 0.5) * 3

    roomTemp.push(Number(tempVar.toFixed(1)))
    fanSpeed.push(Math.min(100, Math.max(0, Number(speedVar.toFixed(0)))))
  }

  return { timestamps, roomTemp, fanSpeed }
}

// 初始化详情图表
const initDetailChart = () => {
  if (!detailChartRef.value || !selectedFCU.value) return
  if (detailChart) detailChart.dispose()

  detailChart = echarts.init(detailChartRef.value)
  const data = generateFCUTrendData(selectedFCU.value)

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Room Temp (°C)', 'Fan Speed (%)'], bottom: 0 },
    grid: { top: 30, right: 20, bottom: 40, left: 50, containLabel: true },
    xAxis: { type: 'category', data: data.timestamps, axisLabel: { rotate: 45, interval: 4, fontSize: 10 } },
    yAxis: [
      { type: 'value', name: 'Room Temp (°C)', position: 'left' },
      { type: 'value', name: 'Fan Speed (%)', position: 'right', min: 0, max: 100 }
    ],
    series: [
      { name: 'Room Temp (°C)', type: 'line', data: data.roomTemp, smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Fan Speed (%)', type: 'line', yAxisIndex: 1, data: data.fanSpeed, smooth: true, lineStyle: { color: '#e6a23c', width: 2 } }
    ]
  }
  detailChart.setOption(option)
}

// 更新实时数据
const updateRealtimeData = () => {
  for (const fcu of fcUs.value) {
    if (fcu.status === 'running') {
      const tempChange = (Math.random() - 0.5) * 0.3
      fcu.roomTemp = Number((fcu.roomTemp + tempChange).toFixed(1))

      const fanChange = (Math.random() - 0.5) * 2
      fcu.fanSpeed = Math.min(100, Math.max(20, fcu.fanSpeed + fanChange))
      fcu.fanSpeed = Number(fcu.fanSpeed.toFixed(0))

      const valveChange = (Math.random() - 0.5) * 3
      fcu.valvePosition = Math.min(100, Math.max(0, fcu.valvePosition + valveChange))
      fcu.valvePosition = Number(fcu.valvePosition.toFixed(0))

      fcu.load = fcu.fanSpeed
      fcu.energyToday += fcu.load * 0.15
      fcu.energyMonth += fcu.load * 0.15
    }
  }
}

// 刷新图表
const updateCharts = () => {
  updateTempChart()
  updateFanChart()
}

// 窗口大小适配
const handleResize = () => {
  if (tempChart) tempChart.resize()
  if (fanChart) fanChart.resize()
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

const selectFCU = (fcu: FCU) => {
  selectedFCU.value = fcu
  detailDrawerVisible.value = true
  setTimeout(() => initDetailChart(), 100)
}

const viewDetail = (fcu: FCU) => {
  selectFCU(fcu)
}

const controlFCU = (fcu: FCU) => {
  selectedFCU.value = fcu
  controlForm.setpoint = fcu.setpoint
  controlForm.fanSpeed = fcu.fanSpeed
  controlDialogVisible.value = true
}

const sendCommand = (command: string) => {
  ElMessage.success(`${command.toUpperCase()} command sent to ${selectedFCU.value.name}`)
  if (command === 'start') {
    selectedFCU.value.status = 'running'
    selectedFCU.value.fanSpeed = 40
    selectedFCU.value.valvePosition = 50
    selectedFCU.value.load = 40
  } else if (command === 'stop') {
    selectedFCU.value.status = 'standby'
    selectedFCU.value.fanSpeed = 0
    selectedFCU.value.valvePosition = 0
    selectedFCU.value.load = 0
  }
  controlDialogVisible.value = false
  updateCharts()
}

const showAlarms = (fcu: FCU) => {
  selectedFCU.value = fcu
  alarmDialogVisible.value = true
}

const viewAlarms = (fcu: FCU) => {
  showAlarms(fcu)
}

const exportFCUData = (fcu: FCU) => {
  ElMessage.success(`Exporting data for ${fcu.name}`)
}

const exportReport = () => {
  ElMessage.success('Exporting FCU report')
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
        initFanChart()
        startAutoRefresh()
        window.addEventListener('resize', handleResize)
      }, 200)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
  if (tempChart) tempChart.dispose()
  if (fanChart) fanChart.dispose()
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
.fcu-container { padding: 20px; background: #f5f7fa; min-height: 100%; }

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

/* FCU Visualization */
.fcu-visualization { background: white; border-radius: 20px; padding: 20px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.fcu-title { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.fcu-title h3 { display: flex; align-items: center; gap: 8px; margin: 0; font-size: 18px; }
.fcu-legend { display: flex; gap: 20px; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 6px; }
.legend-dot.running { background: #67c23a; box-shadow: 0 0 4px #67c23a; }
.legend-dot.standby { background: #409eff; }
.legend-dot.maintenance { background: #e6a23c; }
.legend-dot.offline { background: #f56c6c; }

.fcu-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; }
.fcu-unit { background: #f8fafc; border-radius: 16px; padding: 16px; cursor: pointer; transition: all 0.3s ease; border-left: 4px solid; }
.fcu-unit.running { border-left-color: #67c23a; background: linear-gradient(135deg, #f8fafc, #f0fdf4); }
.fcu-unit.standby { border-left-color: #409eff; }
.fcu-unit.maintenance { border-left-color: #e6a23c; background: linear-gradient(135deg, #f8fafc, #fefce8); }
.fcu-unit.offline { border-left-color: #f56c6c; background: linear-gradient(135deg, #f8fafc, #fef2f2); opacity: 0.8; }
.fcu-unit:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); }

.fcu-image { position: relative; display: flex; justify-content: center; margin-bottom: 12px; }
.fcu-img { width: 100px; height: 100px; object-fit: contain; }
.status-badge { position: absolute; top: 0; right: 0; width: 12px; height: 12px; border-radius: 50%; }
.status-badge.running { background: #67c23a; box-shadow: 0 0 8px #67c23a; animation: pulse 2s infinite; }
.status-badge.standby { background: #409eff; }
.status-badge.maintenance { background: #e6a23c; }
.status-badge.offline { background: #f56c6c; }

.fcu-info { text-align: center; margin-bottom: 12px; }
.fcu-name { margin: 0 0 4px 0; font-size: 16px; font-weight: 600; color: #1e293b; }
.fcu-location { margin: 0; font-size: 11px; color: #64748b; display: flex; align-items: center; justify-content: center; gap: 4px; }
.fcu-model { margin: 4px 0 0 0; font-size: 11px; color: #94a3b8; }

.fcu-metrics { display: flex; justify-content: space-around; margin-bottom: 12px; padding: 8px 0; border-top: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; }
.metric { text-align: center; }
.metric-label { display: block; font-size: 10px; color: #64748b; }
.metric-value { font-size: 14px; font-weight: 600; color: #1e293b; }

.fcu-footer { margin-top: 8px; }
.fcu-actions { display: flex; justify-content: center; gap: 8px; margin-top: 8px; }

/* Charts Section */
.charts-section { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }
.chart-card { border-radius: 16px; }
.card-header-title { display: flex; justify-content: space-between; align-items: center; font-weight: 600; color: #1e293b; font-size: 16px; flex-wrap: wrap; gap: 12px; }
.temp-chart, .fan-chart { width: 100%; height: 320px; }

/* Status Cell */
.status-cell { display: flex; align-items: center; gap: 6px; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; }
.status-dot.running { background: #67c23a; box-shadow: 0 0 4px #67c23a; animation: pulse 2s infinite; }
.status-dot.standby { background: #409eff; }
.status-dot.maintenance { background: #e6a23c; }
.status-dot.offline { background: #f56c6c; }

/* Drawer Styles */
.fcu-detail { padding: 8px; }
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
  .fcu-container { padding: 12px; }
  .plant-overview { grid-template-columns: 1fr; }
  .fcu-grid { grid-template-columns: 1fr; }
  .fcu-title { flex-direction: column; align-items: flex-start; }
  .metric-row { flex-wrap: wrap; }
  .temp-chart, .fan-chart { height: 250px; }
}
</style>