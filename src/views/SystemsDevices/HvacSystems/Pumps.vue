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
        <div class="loading-tip">PUMP SYSTEMS</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Page Content -->
  <div v-else class="pumps-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/systems-devices/device-inventory' }">
            Systems & Devices
          </el-breadcrumb-item>
          <el-breadcrumb-item>HVAC Systems</el-breadcrumb-item>
          <el-breadcrumb-item>Pumps</el-breadcrumb-item>
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
        <div class="overview-icon"><el-icon><MagicStick /></el-icon></div>
        <div class="overview-info">
          <span class="overview-value">{{ pumps.length }}</span>
          <span class="overview-label">Total Pumps</span>
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
          <span class="overview-value">{{ totalFlowRate.toFixed(0) }}</span>
          <span class="overview-label">Total Flow (m³/h)</span>
        </div>
      </div>
      <div class="overview-card">
        <div class="overview-icon"><el-icon><TrendCharts /></el-icon></div>
        <div class="overview-info">
          <span class="overview-value">{{ avgEfficiency.toFixed(1) }}</span>
          <span class="overview-label">Avg Efficiency (%)</span>
        </div>
      </div>
    </div>

    <!-- Pump Visualization -->
    <div class="pump-visualization">
      <div class="pump-title">
        <h3><el-icon><OfficeBuilding /></el-icon> Pump Station - Overview</h3>
        <div class="pump-legend">
          <span><span class="legend-dot running"></span> Running</span>
          <span><span class="legend-dot standby"></span> Standby</span>
          <span><span class="legend-dot maintenance"></span> Maintenance</span>
          <span><span class="legend-dot offline"></span> Offline</span>
        </div>
      </div>

      <div class="pump-grid">
        <div v-for="pump in pumps" :key="pump.id" class="pump-unit" :class="pump.status" @click="selectPump(pump)">
          <div class="pump-image">
            <img :src="pumpImages[pump.status]" :alt="pump.name" class="pump-img" @error="handleImageError">
            <div class="status-badge" :class="pump.status"></div>
          </div>
          <div class="pump-info">
            <h4 class="pump-name">{{ pump.name }}</h4>
            <p class="pump-location"><el-icon><Location /></el-icon> {{ pump.location }}</p>
            <p class="pump-model">{{ pump.manufacturer }} {{ pump.model }}</p>
          </div>
          <div class="pump-metrics">
            <div class="metric">
              <span class="metric-label">Flow Rate</span>
              <span class="metric-value">{{ pump.flowRate }} m³/h</span>
            </div>
            <div class="metric">
              <span class="metric-label">Head</span>
              <span class="metric-value">{{ pump.head }} m</span>
            </div>
            <div class="metric">
              <span class="metric-label">Power</span>
              <span class="metric-value">{{ pump.power }} kW</span>
            </div>
          </div>
          <div class="pump-footer">
            <el-progress :percentage="pump.load" :stroke-width="6" :color="getLoadColor(pump.load)" :show-text="false" />
            <div class="pump-actions">
              <el-button size="small" text @click.stop="viewDetail(pump)">Details</el-button>
              <el-button size="small" text type="primary" @click.stop="controlPump(pump)">Control</el-button>
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
            <span><el-icon><TrendCharts /></el-icon> Flow Rate & Pressure Trend</span>
            <el-select v-model="trendPumpId" placeholder="Select Pump" size="small" style="width: 180px" filterable @change="updateFlowChart">
              <el-option v-for="pump in pumps" :key="pump.id" :label="pump.name" :value="pump.id" />
            </el-select>
          </div>
        </template>
        <div ref="flowChartRef" class="flow-chart"></div>
      </el-card>

      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header-title">
            <span><el-icon><DataAnalysis /></el-icon> Pump Efficiency & Speed</span>
          </div>
        </template>
        <div ref="efficiencyChartRef" class="efficiency-chart"></div>
      </el-card>
    </div>

    <!-- Pump List -->
    <el-card shadow="hover">
      <template #header>
        <div class="card-header-title">Pumps List</div>
      </template>
      <el-table :data="paginatedTableData" border stripe height="350" v-loading="tableLoading">
        <el-table-column label="Name" prop="name" width="160" />
        <el-table-column label="Manufacturer" prop="manufacturer" width="140" />
        <el-table-column label="Model" prop="model" width="150" />
        <el-table-column label="Type" prop="pumpType" width="120">
          <template #default="scope">
            <el-tag size="small">{{ scope.row.pumpType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Status" prop="status" width="110">
          <template #default="scope">
            <div class="status-cell">
              <span class="status-dot" :class="scope.row.status"></span>
              <span>{{ scope.row.status.toUpperCase() }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Flow (m³/h)" prop="flowRate" width="120" />
        <el-table-column label="Head (m)" prop="head" width="100" />
        <el-table-column label="Power (kW)" prop="power" width="110" />
        <el-table-column label="Speed (%)" prop="speed" width="100">
          <template #default="scope">
            <el-progress :percentage="scope.row.speed" :stroke-width="6" :color="getLoadColor(scope.row.speed)" :show-text="false" style="width: 80px" />
            <span style="margin-left: 8px">{{ scope.row.speed }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="Efficiency" prop="efficiency" width="100">
          <template #default="scope">{{ scope.row.efficiency }}%</template>
        </el-table-column>
        <el-table-column label="Energy (kWh)" prop="energyToday" width="120">
          <template #default="scope">{{ scope.row.energyToday.toLocaleString() }} kWh</template>
        </el-table-column>
        <el-table-column label="Operation" width="160" fixed="right">
          <template #default="scope">
            <el-button text type="primary" size="small" @click="viewDetail(scope.row)">Detail</el-button>
            <el-button text type="warning" size="small" @click="controlPump(scope.row)">Control</el-button>
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

    <!-- Pump Details Drawer -->
    <el-drawer v-model="detailDrawerVisible" :title="selectedPump?.name" size="40%" direction="rtl">
      <div v-if="selectedPump" class="pump-detail">
        <div class="detail-header">
          <div class="detail-status" :class="selectedPump.status">
            <span class="status-dot-large"></span>
            <span>{{ selectedPump.status.toUpperCase() }}</span>
          </div>
          <h2>{{ selectedPump.name }}</h2>
          <p>{{ selectedPump.manufacturer }} {{ selectedPump.model }}</p>
        </div>

        <el-divider />

        <div class="detail-metrics">
          <div class="metric-row">
            <div class="metric-card">
              <span class="metric-label">Flow Rate</span>
              <span class="metric-value">{{ selectedPump.flowRate }} <span class="metric-unit">m³/h</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Head</span>
              <span class="metric-value">{{ selectedPump.head }} <span class="metric-unit">m</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Power</span>
              <span class="metric-value">{{ selectedPump.power }} <span class="metric-unit">kW</span></span>
            </div>
          </div>
          <div class="metric-row">
            <div class="metric-card">
              <span class="metric-label">Speed</span>
              <span class="metric-value">{{ selectedPump.speed }}<span class="metric-unit">%</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Efficiency</span>
              <span class="metric-value">{{ selectedPump.efficiency }}<span class="metric-unit">%</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Energy Today</span>
              <span class="metric-value">{{ selectedPump.energyToday.toLocaleString() }}<span class="metric-unit">kWh</span></span>
            </div>
          </div>
          <div class="metric-row">
            <div class="metric-card">
              <span class="metric-label">Inlet Pressure</span>
              <span class="metric-value">{{ selectedPump.inletPressure }}<span class="metric-unit">kPa</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Outlet Pressure</span>
              <span class="metric-value">{{ selectedPump.outletPressure }}<span class="metric-unit">kPa</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Differential</span>
              <span class="metric-value">{{ selectedPump.outletPressure - selectedPump.inletPressure }}<span class="metric-unit">kPa</span></span>
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
          <el-button type="primary" @click="controlPump(selectedPump)">Control Pump</el-button>
          <el-button @click="viewAlarms(selectedPump)">View Alarms</el-button>
          <el-button @click="exportPumpData(selectedPump)">Export Data</el-button>
        </div>
      </div>
    </el-drawer>

    <!-- Control Dialog -->
    <el-dialog v-model="controlDialogVisible" :title="`Control - ${selectedPump?.name}`" width="450px">
      <el-form :model="controlForm" label-width="120px">
        <el-form-item label="Operation Mode">
          <el-radio-group v-model="controlForm.mode">
            <el-radio label="auto">Auto</el-radio>
            <el-radio label="manual">Manual</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Speed Setpoint">
          <el-slider v-model="controlForm.speed" :min="0" :max="100" :step="5" />
        </el-form-item>
        <el-form-item label="Flow Setpoint">
          <el-input-number v-model="controlForm.flowSetpoint" :min="0" :max="500" :step="10" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Commands">
          <el-button-group>
            <el-button type="success" @click="sendCommand('start')" :disabled="selectedPump?.status === 'running'">Start</el-button>
            <el-button type="warning" @click="sendCommand('stop')" :disabled="selectedPump?.status !== 'running'">Stop</el-button>
            <el-button type="primary" @click="sendCommand('reset')">Reset</el-button>
          </el-button-group>
        </el-form-item>
      </el-form>
    </el-dialog>

    <!-- Alarms Dialog -->
    <el-dialog v-model="alarmDialogVisible" :title="`Alarms - ${selectedPump?.name}`" width="600px">
      <el-table :data="selectedPump?.alarms || []" stripe border>
        <el-table-column prop="timestamp" label="Time" width="160" />
        <el-table-column prop="severity" label="Severity" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.severity === 'critical' ? 'danger' : 'warning'" size="small">{{ scope.row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="code" label="Code" width="100" />
        <el-table-column prop="message" label="Message" min-width="200" />
        <el-table-column prop="status" label="Status" width="100">
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
  Refresh, Download, MagicStick, CircleCheckFilled, DataLine,
  TrendCharts, OfficeBuilding, Location, DataAnalysis
} from '@element-plus/icons-vue'

// ========== Loading State ==========
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading pump systems...')
const loadingMessages = [
  'Initializing pump systems...',
  'Loading pump data...',
  'Connecting to controllers...',
  'Rendering pump layout...',
  'Almost ready...'
]

// ========== Chart References ==========
const flowChartRef = ref<HTMLDivElement | null>(null)
const efficiencyChartRef = ref<HTMLDivElement | null>(null)
const detailChartRef = ref<HTMLDivElement | null>(null)
let flowChart: echarts.ECharts | null = null
let efficiencyChart: echarts.ECharts | null = null
let detailChart: echarts.ECharts | null = null
let refreshTimer: number | null = null
const refreshing = ref(false)
const tableLoading = ref(false)
const trendPumpId = ref('')

// ========== Pump Images ==========
const pumpImages = {
  running: 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png',
  standby: 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png',
  maintenance: 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png',
  offline: 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png',
  default: 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png'
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  if (pumpImages.default) {
    img.src = pumpImages.default
  }
}

// ========== Dialog State ==========
const detailDrawerVisible = ref(false)
const controlDialogVisible = ref(false)
const alarmDialogVisible = ref(false)
const selectedPump = ref<any>(null)
const controlForm = reactive({
  mode: 'auto',
  speed: 70,
  flowSetpoint: 200
})

// ========== Pump Data ==========
interface Pump {
  id: string
  name: string
  manufacturer: string
  model: string
  pumpType: string
  status: 'running' | 'standby' | 'maintenance' | 'offline'
  flowRate: number
  head: number
  power: number
  speed: number
  efficiency: number
  inletPressure: number
  outletPressure: number
  energyToday: number
  energyMonth: number
  location: string
  alarms: any[]
}

const pumps = ref<Pump[]>([
  { id: '1', name: 'Chilled Water Pump-01', manufacturer: 'Grundfos', model: 'CRN 90', pumpType: 'Centrifugal', status: 'running', flowRate: 450, head: 32, power: 55, speed: 85, efficiency: 78, inletPressure: 220, outletPressure: 540, energyToday: 8500, energyMonth: 255000, location: 'Basement B2', alarms: [] },
  { id: '2', name: 'Chilled Water Pump-02', manufacturer: 'Grundfos', model: 'CRN 90', pumpType: 'Centrifugal', status: 'running', flowRate: 420, head: 31, power: 52, speed: 82, efficiency: 76, inletPressure: 230, outletPressure: 530, energyToday: 7800, energyMonth: 234000, location: 'Basement B2', alarms: [] },
  { id: '3', name: 'Condenser Water Pump-01', manufacturer: 'Armstrong', model: '4300', pumpType: 'Axial', status: 'running', flowRate: 580, head: 28, power: 68, speed: 88, efficiency: 82, inletPressure: 200, outletPressure: 480, energyToday: 10200, energyMonth: 306000, location: 'Basement B2', alarms: [] },
  { id: '4', name: 'Condenser Water Pump-02', manufacturer: 'Armstrong', model: '4300', pumpType: 'Axial', status: 'standby', flowRate: 0, head: 0, power: 0, speed: 0, efficiency: 0, inletPressure: 210, outletPressure: 490, energyToday: 0, energyMonth: 0, location: 'Basement B2', alarms: [] },
  { id: '5', name: 'Hot Water Pump-01', manufacturer: 'Bell & Gossett', model: 'Series 1510', pumpType: 'Centrifugal', status: 'running', flowRate: 320, head: 25, power: 35, speed: 75, efficiency: 74, inletPressure: 250, outletPressure: 500, energyToday: 5200, energyMonth: 156000, location: 'Mechanical Room', alarms: [] },
  { id: '6', name: 'Hot Water Pump-02', manufacturer: 'Bell & Gossett', model: 'Series 1510', pumpType: 'Centrifugal', status: 'maintenance', flowRate: 0, head: 0, power: 0, speed: 0, efficiency: 0, inletPressure: 240, outletPressure: 490, energyToday: 0, energyMonth: 0, location: 'Mechanical Room', alarms: [{ timestamp: '2026-06-01 14:30:00', severity: 'critical', code: 'E-201', message: 'Bearing failure', status: 'active' }] },
  { id: '7', name: 'Booster Pump', manufacturer: 'Wilo', model: 'Stratos GIGA', pumpType: 'Variable', status: 'running', flowRate: 180, head: 45, power: 28, speed: 65, efficiency: 71, inletPressure: 300, outletPressure: 750, energyToday: 3800, energyMonth: 114000, location: 'Roof', alarms: [] }
])

const runningCount = computed(() => pumps.value.filter(p => p.status === 'running').length)
const runningPercent = computed(() => pumps.value.length ? Math.round(runningCount.value / pumps.value.length * 100) : 0)
const totalFlowRate = computed(() => pumps.value.reduce((sum, p) => sum + p.flowRate, 0))
const avgEfficiency = computed(() => {
  const running = pumps.value.filter(p => p.status === 'running')
  if (running.length === 0) return 0
  return running.reduce((sum, p) => sum + p.efficiency, 0) / running.length
})

const paginatedTableData = computed(() => {
  const start = (pageInfo.pageNum - 1) * pageInfo.pageSize
  return pumps.value.slice(start, start + pageInfo.pageSize)
})

const pageInfo = reactive({
  pageNum: 1,
  pageSize: 10,
  total: pumps.value.length
})

const getLoadColor = (load: number) => {
  if (load < 30) return '#67c23a'
  if (load < 70) return '#409eff'
  return '#e6a23c'
}

// 生成流量和压力趋势数据
const generateFlowData = (pumpId: string) => {
  const pump = pumps.value.find(p => p.id === pumpId)
  if (!pump) return { timestamps: [], flowRate: [], pressure: [] }

  const timestamps = []
  const flowRate = []
  const pressure = []
  const now = new Date()

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    timestamps.push(`${String(time.getHours()).padStart(2, '0')}:00`)

    const flowVariation = pump.flowRate + Math.sin(i * 0.3) * (pump.flowRate * 0.15) + (Math.random() - 0.5) * 20
    flowRate.push(Math.max(0, Number(flowVariation.toFixed(0))))

    const pressureDiff = pump.outletPressure - pump.inletPressure
    const pressureVariation = pressureDiff + Math.sin(i * 0.3) * 15 + (Math.random() - 0.5) * 10
    pressure.push(Math.max(0, Number(pressureVariation.toFixed(0))))
  }

  return { timestamps, flowRate, pressure }
}

// 生成效率和速度趋势数据
const generateEfficiencyData = () => {
  const timestamps = []
  const efficiencies = []
  const speeds = []
  const now = new Date()

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    timestamps.push(`${String(time.getHours()).padStart(2, '0')}:00`)

    const effVariation = 75 + Math.sin(i * 0.3) * 8 + (Math.random() - 0.5) * 4
    efficiencies.push(Math.min(95, Math.max(50, Number(effVariation.toFixed(0)))))

    const speedVariation = 70 + Math.sin(i * 0.3) * 12 + (Math.random() - 0.5) * 5
    speeds.push(Math.min(100, Math.max(20, Number(speedVariation.toFixed(0)))))
  }

  return { timestamps, efficiencies, speeds }
}

// 初始化流量图表
const initFlowChart = async () => {
  await nextTick()
  if (!flowChartRef.value) {
    setTimeout(() => initFlowChart(), 100)
    return
  }

  if (flowChart) flowChart.dispose()

  if (pumps.value.length > 0 && !trendPumpId.value) {
    trendPumpId.value = pumps.value[0].id
  }

  flowChart = echarts.init(flowChartRef.value)
  updateFlowChart()
}

const updateFlowChart = () => {
  if (!flowChart || !trendPumpId.value) return

  const data = generateFlowData(trendPumpId.value)

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Flow Rate (m³/h)', 'Differential Pressure (kPa)'], bottom: 0 },
    grid: { top: 30, right: 20, bottom: 40, left: 50, containLabel: true },
    xAxis: { type: 'category', data: data.timestamps, axisLabel: { rotate: 45, interval: 4, fontSize: 10 } },
    yAxis: [
      { type: 'value', name: 'Flow Rate (m³/h)', position: 'left' },
      { type: 'value', name: 'Pressure (kPa)', position: 'right' }
    ],
    series: [
      { name: 'Flow Rate (m³/h)', type: 'line', data: data.flowRate, smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Differential Pressure (kPa)', type: 'line', yAxisIndex: 1, data: data.pressure, smooth: true, lineStyle: { color: '#f56c6c', width: 2 }, areaStyle: { opacity: 0.1 } }
    ]
  }
  flowChart.setOption(option, true)
}

// 初始化效率图表
const initEfficiencyChart = async () => {
  await nextTick()
  if (!efficiencyChartRef.value) {
    setTimeout(() => initEfficiencyChart(), 100)
    return
  }

  if (efficiencyChart) efficiencyChart.dispose()
  efficiencyChart = echarts.init(efficiencyChartRef.value)

  const data = generateEfficiencyData()

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Efficiency (%)', 'Speed (%)'], bottom: 0 },
    grid: { top: 30, right: 20, bottom: 40, left: 50, containLabel: true },
    xAxis: { type: 'category', data: data.timestamps, axisLabel: { rotate: 45, interval: 4, fontSize: 10 } },
    yAxis: { type: 'value', name: 'Percentage (%)', min: 0, max: 100 },
    series: [
      { name: 'Efficiency (%)', type: 'line', data: data.efficiencies, smooth: true, lineStyle: { color: '#67c23a', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Speed (%)', type: 'line', data: data.speeds, smooth: true, lineStyle: { color: '#e6a23c', width: 2 }, areaStyle: { opacity: 0.1 } }
    ]
  }
  efficiencyChart.setOption(option)
}

const updateEfficiencyChart = () => {
  if (!efficiencyChart) return
  const data = generateEfficiencyData()
  efficiencyChart.setOption({
    xAxis: { data: data.timestamps },
    series: [{ data: data.efficiencies }, { data: data.speeds }]
  })
}

// 生成单个水泵趋势数据
const generatePumpTrendData = (pump: Pump) => {
  const timestamps = []
  const flowRate = []
  const speed = []
  const now = new Date()

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    timestamps.push(`${String(time.getHours()).padStart(2, '0')}:00`)

    const flowVariation = pump.flowRate + Math.sin(i * 0.3) * (pump.flowRate * 0.15) + (Math.random() - 0.5) * 15
    flowRate.push(Math.max(0, Number(flowVariation.toFixed(0))))

    const speedVariation = pump.speed + Math.sin(i * 0.3) * 10 + (Math.random() - 0.5) * 5
    speed.push(Math.min(100, Math.max(0, Number(speedVariation.toFixed(0)))))
  }

  return { timestamps, flowRate, speed }
}

// 初始化详情图表
const initDetailChart = () => {
  if (!detailChartRef.value || !selectedPump.value) return
  if (detailChart) detailChart.dispose()

  detailChart = echarts.init(detailChartRef.value)
  const data = generatePumpTrendData(selectedPump.value)

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Flow Rate (m³/h)', 'Speed (%)'], bottom: 0 },
    grid: { top: 30, right: 20, bottom: 40, left: 50, containLabel: true },
    xAxis: { type: 'category', data: data.timestamps, axisLabel: { rotate: 45, interval: 4, fontSize: 10 } },
    yAxis: [
      { type: 'value', name: 'Flow Rate (m³/h)', position: 'left' },
      { type: 'value', name: 'Speed (%)', position: 'right', min: 0, max: 100 }
    ],
    series: [
      { name: 'Flow Rate (m³/h)', type: 'line', data: data.flowRate, smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Speed (%)', type: 'line', yAxisIndex: 1, data: data.speed, smooth: true, lineStyle: { color: '#e6a23c', width: 2 } }
    ]
  }
  detailChart.setOption(option)
}

// 更新实时数据
const updateRealtimeData = () => {
  for (const pump of pumps.value) {
    if (pump.status === 'running') {
      const flowChange = (Math.random() - 0.5) * 20
      let newFlow = pump.flowRate + flowChange
      newFlow = Math.max(50, Math.min(pump.pumpType === 'Axial' ? 700 : 500, newFlow))
      pump.flowRate = Number(newFlow.toFixed(0))

      const speedChange = (Math.random() - 0.5) * 3
      let newSpeed = pump.speed + speedChange
      newSpeed = Math.max(30, Math.min(100, newSpeed))
      pump.speed = Number(newSpeed.toFixed(0))

      const powerChange = (Math.random() - 0.5) * 3
      let newPower = pump.power + powerChange
      newPower = Math.max(10, Math.min(100, newPower))
      pump.power = Number(newPower.toFixed(0))

      const effChange = (Math.random() - 0.5) * 2
      let newEff = pump.efficiency + effChange
      newEff = Math.max(60, Math.min(90, newEff))
      pump.efficiency = Number(newEff.toFixed(0))

      pump.energyToday += pump.power * 0.25
      pump.energyMonth += pump.power * 0.25
    }
  }
}

// 刷新图表
const updateCharts = () => {
  updateFlowChart()
  updateEfficiencyChart()
}

// 窗口大小适配
const handleResize = () => {
  if (flowChart) flowChart.resize()
  if (efficiencyChart) efficiencyChart.resize()
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

const selectPump = (pump: Pump) => {
  selectedPump.value = pump
  detailDrawerVisible.value = true
  setTimeout(() => initDetailChart(), 100)
}

const viewDetail = (pump: Pump) => {
  selectPump(pump)
}

const controlPump = (pump: Pump) => {
  selectedPump.value = pump
  controlForm.speed = pump.speed
  controlForm.flowSetpoint = pump.flowRate
  controlDialogVisible.value = true
}

const sendCommand = (command: string) => {
  ElMessage.success(`${command.toUpperCase()} command sent to ${selectedPump.value.name}`)
  if (command === 'start') {
    selectedPump.value.status = 'running'
    selectedPump.value.speed = 40
    selectedPump.value.flowRate = 150
    selectedPump.value.power = 25
  } else if (command === 'stop') {
    selectedPump.value.status = 'standby'
    selectedPump.value.speed = 0
    selectedPump.value.flowRate = 0
    selectedPump.value.power = 0
  }
  controlDialogVisible.value = false
  updateCharts()
}

const showAlarms = (pump: Pump) => {
  selectedPump.value = pump
  alarmDialogVisible.value = true
}

const viewAlarms = (pump: Pump) => {
  showAlarms(pump)
}

const exportPumpData = (pump: Pump) => {
  ElMessage.success(`Exporting data for ${pump.name}`)
}

const exportReport = () => {
  ElMessage.success('Exporting pump report')
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
        initFlowChart()
        initEfficiencyChart()
        startAutoRefresh()
        window.addEventListener('resize', handleResize)
      }, 200)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
  if (flowChart) flowChart.dispose()
  if (efficiencyChart) efficiencyChart.dispose()
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
.pumps-container { padding: 20px; background: #f5f7fa; min-height: 100%; }

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

/* Pump Visualization */
.pump-visualization { background: white; border-radius: 20px; padding: 20px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.pump-title { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.pump-title h3 { display: flex; align-items: center; gap: 8px; margin: 0; font-size: 18px; }
.pump-legend { display: flex; gap: 20px; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 6px; }
.legend-dot.running { background: #67c23a; box-shadow: 0 0 4px #67c23a; }
.legend-dot.standby { background: #409eff; }
.legend-dot.maintenance { background: #e6a23c; }
.legend-dot.offline { background: #f56c6c; }

.pump-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; }
.pump-unit { background: #f8fafc; border-radius: 16px; padding: 16px; cursor: pointer; transition: all 0.3s ease; border-left: 4px solid; }
.pump-unit.running { border-left-color: #67c23a; background: linear-gradient(135deg, #f8fafc, #f0fdf4); }
.pump-unit.standby { border-left-color: #409eff; }
.pump-unit.maintenance { border-left-color: #e6a23c; background: linear-gradient(135deg, #f8fafc, #fefce8); }
.pump-unit.offline { border-left-color: #f56c6c; background: linear-gradient(135deg, #f8fafc, #fef2f2); opacity: 0.8; }
.pump-unit:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); }

.pump-image { position: relative; display: flex; justify-content: center; margin-bottom: 12px; }
.pump-img { width: 100px; height: 100px; object-fit: contain; }
.status-badge { position: absolute; top: 0; right: 0; width: 12px; height: 12px; border-radius: 50%; }
.status-badge.running { background: #67c23a; box-shadow: 0 0 8px #67c23a; animation: pulse 2s infinite; }
.status-badge.standby { background: #409eff; }
.status-badge.maintenance { background: #e6a23c; }
.status-badge.offline { background: #f56c6c; }

.pump-info { text-align: center; margin-bottom: 12px; }
.pump-name { margin: 0 0 4px 0; font-size: 16px; font-weight: 600; color: #1e293b; }
.pump-location { margin: 0; font-size: 11px; color: #64748b; display: flex; align-items: center; justify-content: center; gap: 4px; }
.pump-model { margin: 4px 0 0 0; font-size: 11px; color: #94a3b8; }

.pump-metrics { display: flex; justify-content: space-around; margin-bottom: 12px; padding: 8px 0; border-top: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; }
.metric { text-align: center; }
.metric-label { display: block; font-size: 10px; color: #64748b; }
.metric-value { font-size: 14px; font-weight: 600; color: #1e293b; }

.pump-footer { margin-top: 8px; }
.pump-actions { display: flex; justify-content: center; gap: 8px; margin-top: 8px; }

/* Charts Section */
.charts-section { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }
.chart-card { border-radius: 16px; }
.card-header-title { display: flex; justify-content: space-between; align-items: center; font-weight: 600; color: #1e293b; font-size: 16px; flex-wrap: wrap; gap: 12px; }
.flow-chart, .efficiency-chart { width: 100%; height: 320px; }

/* Status Cell */
.status-cell { display: flex; align-items: center; gap: 6px; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; }
.status-dot.running { background: #67c23a; box-shadow: 0 0 4px #67c23a; animation: pulse 2s infinite; }
.status-dot.standby { background: #409eff; }
.status-dot.maintenance { background: #e6a23c; }
.status-dot.offline { background: #f56c6c; }

/* Drawer Styles */
.pump-detail { padding: 8px; }
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
  .pumps-container { padding: 12px; }
  .plant-overview { grid-template-columns: 1fr; }
  .pump-grid { grid-template-columns: 1fr; }
  .pump-title { flex-direction: column; align-items: flex-start; }
  .metric-row { flex-wrap: wrap; }
  .flow-chart, .efficiency-chart { height: 250px; }
}
</style>