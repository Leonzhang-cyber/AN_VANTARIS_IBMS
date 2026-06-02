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
        <div class="loading-tip">COOLING TOWER SYSTEMS</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Page Content -->
  <div v-else class="cooling-towers-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/systems-devices/device-inventory' }">
            Systems & Devices
          </el-breadcrumb-item>
          <el-breadcrumb-item>HVAC Systems</el-breadcrumb-item>
          <el-breadcrumb-item>Cooling Towers</el-breadcrumb-item>
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
          <span class="overview-value">{{ towers.length }}</span>
          <span class="overview-label">Total Towers</span>
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
          <span class="overview-value">{{ totalHeatRejection.toFixed(0) }}</span>
          <span class="overview-label">Heat Rejection (kW)</span>
        </div>
      </div>
      <div class="overview-card">
        <div class="overview-icon"><el-icon><TrendCharts /></el-icon></div>
        <div class="overview-info">
          <span class="overview-value">{{ avgApproachTemp.toFixed(1) }}</span>
          <span class="overview-label">Avg Approach (°C)</span>
        </div>
      </div>
    </div>

    <!-- Cooling Tower Visualization -->
    <div class="tower-visualization">
      <div class="tower-title">
        <h3><el-icon><OfficeBuilding /></el-icon> Cooling Tower Plant - Overview</h3>
        <div class="tower-legend">
          <span><span class="legend-dot running"></span> Running</span>
          <span><span class="legend-dot standby"></span> Standby</span>
          <span><span class="legend-dot maintenance"></span> Maintenance</span>
          <span><span class="legend-dot offline"></span> Offline</span>
        </div>
      </div>

      <div class="tower-grid">
        <div v-for="tower in towers" :key="tower.id" class="tower-unit" :class="tower.status" @click="selectTower(tower)">
          <div class="tower-image">
            <img :src="towerImages[tower.status]" :alt="tower.name" class="tower-img" @error="handleImageError">
            <div class="status-badge" :class="tower.status"></div>
          </div>
          <div class="tower-info">
            <h4 class="tower-name">{{ tower.name }}</h4>
            <p class="tower-location"><el-icon><Location /></el-icon> {{ tower.location }}</p>
            <p class="tower-model">{{ tower.manufacturer }} {{ tower.model }}</p>
          </div>
          <div class="tower-metrics">
            <div class="metric">
              <span class="metric-label">Capacity</span>
              <span class="metric-value">{{ tower.capacity }} RT</span>
            </div>
            <div class="metric">
              <span class="metric-label">Load</span>
              <span class="metric-value" :class="getLoadClass(tower.currentLoad)">{{ tower.currentLoad }}%</span>
            </div>
            <div class="metric">
              <span class="metric-label">Fan Speed</span>
              <span class="metric-value">{{ tower.fanSpeed }}%</span>
            </div>
          </div>
          <div class="tower-footer">
            <el-progress :percentage="tower.currentLoad" :stroke-width="6" :color="getLoadColor(tower.currentLoad)" :show-text="false" />
            <div class="tower-actions">
              <el-button size="small" text @click.stop="viewDetail(tower)">Details</el-button>
              <el-button size="small" text type="primary" @click.stop="controlTower(tower)">Control</el-button>
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
            <span><el-icon><TrendCharts /></el-icon> Water Temperature Trend</span>
            <el-select v-model="trendTowerId" placeholder="Select Tower" size="small" style="width: 180px" filterable @change="updateTemperatureChart">
              <el-option v-for="tower in towers" :key="tower.id" :label="tower.name" :value="tower.id" />
            </el-select>
          </div>
        </template>
        <div ref="tempChartRef" class="temp-chart"></div>
      </el-card>

      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header-title">
            <span><el-icon><DataAnalysis /></el-icon> Fan Speed & Approach Temperature</span>
          </div>
        </template>
        <div ref="fanChartRef" class="fan-chart"></div>
      </el-card>
    </div>

    <!-- Cooling Tower List -->
    <el-card shadow="hover">
      <template #header>
        <div class="card-header-title">Cooling Towers List</div>
      </template>
      <el-table :data="paginatedTableData" border stripe height="350" v-loading="tableLoading">
        <el-table-column label="Name" prop="name" width="160" />
        <el-table-column label="Manufacturer" prop="manufacturer" width="140" />
        <el-table-column label="Model" prop="model" width="150" />
        <el-table-column label="Status" prop="status" width="110">
          <template #default="scope">
            <div class="status-cell">
              <span class="status-dot" :class="scope.row.status"></span>
              <span>{{ scope.row.status.toUpperCase() }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Capacity (RT)" prop="capacity" width="120" />
        <el-table-column label="Load (%)" prop="currentLoad" width="100">
          <template #default="scope">
            <el-progress :percentage="scope.row.currentLoad" :stroke-width="6" :color="getLoadColor(scope.row.currentLoad)" :show-text="false" style="width: 80px" />
            <span style="margin-left: 8px">{{ scope.row.currentLoad }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="Supply Temp" prop="supplyTemp" width="110">
          <template #default="scope">{{ scope.row.supplyTemp }}°C</template>
        </el-table-column>
        <el-table-column label="Return Temp" prop="returnTemp" width="110">
          <template #default="scope">{{ scope.row.returnTemp }}°C</template>
        </el-table-column>
        <el-table-column label="Approach" prop="approachTemp" width="100">
          <template #default="scope">{{ scope.row.approachTemp }}°C</template>
        </el-table-column>
        <el-table-column label="Fan Speed" prop="fanSpeed" width="100">
          <template #default="scope">{{ scope.row.fanSpeed }}%</template>
        </el-table-column>
        <el-table-column label="Water Flow" prop="waterFlow" width="120">
          <template #default="scope">{{ scope.row.waterFlow }} m³/h</template>
        </el-table-column>
        <el-table-column label="Operation" width="160" fixed="right">
          <template #default="scope">
            <el-button text type="primary" size="small" @click="viewDetail(scope.row)">Detail</el-button>
            <el-button text type="warning" size="small" @click="controlTower(scope.row)">Control</el-button>
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

    <!-- Tower Details Drawer -->
    <el-drawer v-model="detailDrawerVisible" :title="selectedTower?.name" size="40%" direction="rtl">
      <div v-if="selectedTower" class="tower-detail">
        <div class="detail-header">
          <div class="detail-status" :class="selectedTower.status">
            <span class="status-dot-large"></span>
            <span>{{ selectedTower.status.toUpperCase() }}</span>
          </div>
          <h2>{{ selectedTower.name }}</h2>
          <p>{{ selectedTower.manufacturer }} {{ selectedTower.model }}</p>
        </div>

        <el-divider />

        <div class="detail-metrics">
          <div class="metric-row">
            <div class="metric-card">
              <span class="metric-label">Heat Rejection</span>
              <span class="metric-value">{{ selectedTower.capacity }} <span class="metric-unit">RT</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Current Load</span>
              <span class="metric-value" :class="getLoadClass(selectedTower.currentLoad)">{{ selectedTower.currentLoad }}<span class="metric-unit">%</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Fan Speed</span>
              <span class="metric-value">{{ selectedTower.fanSpeed }}<span class="metric-unit">%</span></span>
            </div>
          </div>
          <div class="metric-row">
            <div class="metric-card">
              <span class="metric-label">Supply Temp</span>
              <span class="metric-value">{{ selectedTower.supplyTemp }}<span class="metric-unit">°C</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Return Temp</span>
              <span class="metric-value">{{ selectedTower.returnTemp }}<span class="metric-unit">°C</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Approach Temp</span>
              <span class="metric-value">{{ selectedTower.approachTemp }}<span class="metric-unit">°C</span></span>
            </div>
          </div>
          <div class="metric-row">
            <div class="metric-card">
              <span class="metric-label">Water Flow</span>
              <span class="metric-value">{{ selectedTower.waterFlow }}<span class="metric-unit">m³/h</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Energy Today</span>
              <span class="metric-value">{{ selectedTower.energyToday.toLocaleString() }}<span class="metric-unit">kWh</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Wet Bulb Temp</span>
              <span class="metric-value">{{ selectedTower.wetBulbTemp }}<span class="metric-unit">°C</span></span>
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
          <el-button type="primary" @click="controlTower(selectedTower)">Control Tower</el-button>
          <el-button @click="viewAlarms(selectedTower)">View Alarms</el-button>
          <el-button @click="exportTowerData(selectedTower)">Export Data</el-button>
        </div>
      </div>
    </el-drawer>

    <!-- Control Dialog -->
    <el-dialog v-model="controlDialogVisible" :title="`Control - ${selectedTower?.name}`" width="450px">
      <el-form :model="controlForm" label-width="120px">
        <el-form-item label="Operation Mode">
          <el-radio-group v-model="controlForm.mode">
            <el-radio label="auto">Auto</el-radio>
            <el-radio label="manual">Manual</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Fan Speed Setpoint">
          <el-slider v-model="controlForm.fanSpeed" :min="0" :max="100" :step="5" />
        </el-form-item>
        <el-form-item label="Supply Temp Setpoint">
          <el-input-number v-model="controlForm.setpoint" :min="20" :max="35" :step="0.5" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Commands">
          <el-button-group>
            <el-button type="success" @click="sendCommand('start')" :disabled="selectedTower?.status === 'running'">Start</el-button>
            <el-button type="warning" @click="sendCommand('stop')" :disabled="selectedTower?.status !== 'running'">Stop</el-button>
            <el-button type="primary" @click="sendCommand('reset')">Reset</el-button>
          </el-button-group>
        </el-form-item>
      </el-form>
    </el-dialog>

    <!-- Alarms Dialog -->
    <el-dialog v-model="alarmDialogVisible" :title="`Alarms - ${selectedTower?.name}`" width="600px">
      <el-table :data="selectedTower?.alarms || []" stripe border>
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
  Refresh, Download, WindPower, CircleCheckFilled, DataLine,
  TrendCharts, OfficeBuilding, Location, DataAnalysis
} from '@element-plus/icons-vue'

// ========== Loading State ==========
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading cooling tower systems...')
const loadingMessages = [
  'Initializing cooling tower systems...',
  'Loading tower data...',
  'Connecting to BMS...',
  'Rendering tower layout...',
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
const trendTowerId = ref('')

// ========== Tower Images ==========
const towerImages = {
  running: 'https://aegisnx.com/wp-content/uploads/2026/05/52013145678.jpg',
  standby: 'https://aegisnx.com/wp-content/uploads/2026/05/52013145678.jpg',
  maintenance: 'https://aegisnx.com/wp-content/uploads/2026/05/52013145678.jpg',
  offline: 'https://aegisnx.com/wp-content/uploads/2026/05/52013145678.jpg',
  default: 'https://aegisnx.com/wp-content/uploads/2026/05/52013145678.jpg'
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  if (towerImages.default) {
    img.src = towerImages.default
  }
}

// ========== Dialog State ==========
const detailDrawerVisible = ref(false)
const controlDialogVisible = ref(false)
const alarmDialogVisible = ref(false)
const selectedTower = ref<any>(null)
const controlForm = reactive({
  mode: 'auto',
  fanSpeed: 70,
  setpoint: 28
})

// ========== Cooling Tower Data ==========
interface CoolingTower {
  id: string
  name: string
  manufacturer: string
  model: string
  status: 'running' | 'standby' | 'maintenance' | 'offline'
  capacity: number
  currentLoad: number
  fanSpeed: number
  supplyTemp: number
  returnTemp: number
  approachTemp: number
  waterFlow: number
  wetBulbTemp: number
  energyToday: number
  energyMonth: number
  location: string
  alarms: any[]
}

const towers = ref<CoolingTower[]>([
  { id: '1', name: 'Cooling Tower-01', manufacturer: 'BAC', model: 'Series 3000', status: 'running', capacity: 1200, currentLoad: 68, fanSpeed: 72, supplyTemp: 29.5, returnTemp: 35.2, approachTemp: 3.8, waterFlow: 850, wetBulbTemp: 25.7, energyToday: 8500, energyMonth: 255000, location: 'Roof', alarms: [] },
  { id: '2', name: 'Cooling Tower-02', manufacturer: 'Marley', model: 'NC8400', status: 'running', capacity: 1000, currentLoad: 55, fanSpeed: 58, supplyTemp: 28.8, returnTemp: 34.5, approachTemp: 3.5, waterFlow: 720, wetBulbTemp: 25.3, energyToday: 6200, energyMonth: 186000, location: 'Roof', alarms: [] },
  { id: '3', name: 'Cooling Tower-03', manufacturer: 'Evapco', model: 'ATW', status: 'standby', capacity: 800, currentLoad: 0, fanSpeed: 0, supplyTemp: 30.2, returnTemp: 36.0, approachTemp: 4.0, waterFlow: 0, wetBulbTemp: 26.0, energyToday: 0, energyMonth: 0, location: 'Roof', alarms: [] },
  { id: '4', name: 'Cooling Tower-04', manufacturer: 'BAC', model: 'Series 1500', status: 'maintenance', capacity: 600, currentLoad: 0, fanSpeed: 0, supplyTemp: 31.0, returnTemp: 37.5, approachTemp: 4.5, waterFlow: 0, wetBulbTemp: 26.5, energyToday: 0, energyMonth: 0, location: 'Roof', alarms: [{ timestamp: '2026-06-01 09:30:00', severity: 'critical', code: 'E-101', message: 'Fan motor failure', status: 'active' }] },
  { id: '5', name: 'CT-Mechanical Room', manufacturer: 'Marley', model: 'NC5400', status: 'offline', capacity: 500, currentLoad: 0, fanSpeed: 0, supplyTemp: 32.0, returnTemp: 38.0, approachTemp: 5.0, waterFlow: 0, wetBulbTemp: 27.0, energyToday: 0, energyMonth: 0, location: 'Mechanical Room', alarms: [] }
])

const runningCount = computed(() => towers.value.filter(t => t.status === 'running').length)
const runningPercent = computed(() => towers.value.length ? Math.round(runningCount.value / towers.value.length * 100) : 0)
const totalHeatRejection = computed(() => towers.value.reduce((sum, t) => sum + t.capacity * (t.currentLoad / 100), 0))
const avgApproachTemp = computed(() => {
  const running = towers.value.filter(t => t.status === 'running')
  if (running.length === 0) return 0
  return running.reduce((sum, t) => sum + t.approachTemp, 0) / running.length
})

const paginatedTableData = computed(() => {
  const start = (pageInfo.pageNum - 1) * pageInfo.pageSize
  return towers.value.slice(start, start + pageInfo.pageSize)
})

const pageInfo = reactive({
  pageNum: 1,
  pageSize: 10,
  total: towers.value.length
})

const getLoadClass = (load: number) => {
  if (load < 30) return 'load-low'
  if (load < 70) return 'load-medium'
  return 'load-high'
}

const getLoadColor = (load: number) => {
  if (load < 30) return '#67c23a'
  if (load < 70) return '#409eff'
  return '#e6a23c'
}

// 生成温度趋势数据
const generateTemperatureData = (towerId: string) => {
  const tower = towers.value.find(t => t.id === towerId)
  if (!tower) return { timestamps: [], supplyTemp: [], returnTemp: [], approachTemp: [] }

  const timestamps = []
  const supplyTemp = []
  const returnTemp = []
  const approachTemp = []
  const now = new Date()

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    timestamps.push(`${String(time.getHours()).padStart(2, '0')}:00`)

    const supplyVariation = tower.supplyTemp + Math.sin(i * 0.3) * 1.5 + (Math.random() - 0.5) * 0.5
    const returnVariation = tower.returnTemp + Math.sin(i * 0.3) * 1.8 + (Math.random() - 0.5) * 0.6
    const approach = returnVariation - supplyVariation

    supplyTemp.push(Number(supplyVariation.toFixed(1)))
    returnTemp.push(Number(returnVariation.toFixed(1)))
    approachTemp.push(Number(approach.toFixed(1)))
  }

  return { timestamps, supplyTemp, returnTemp, approachTemp }
}

// 生成风扇和趋近温度数据
const generateFanAndApproachData = () => {
  const timestamps = []
  const fanSpeeds = []
  const approachTemps = []
  const now = new Date()

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    timestamps.push(`${String(time.getHours()).padStart(2, '0')}:00`)

    // 模拟风扇速度变化 (日间高，夜间低)
    const hour = time.getHours()
    const baseSpeed = hour >= 8 && hour <= 18 ? 75 : 45
    const speedVariation = baseSpeed + (Math.sin(i * 0.3) * 10) + (Math.random() - 0.5) * 5
    fanSpeeds.push(Math.min(100, Math.max(20, Number(speedVariation.toFixed(0)))))

    // 模拟趋近温度变化 (与风扇速度负相关)
    const approachBase = 4.5 - (baseSpeed - 45) / 60
    const approachVariation = approachBase + Math.sin(i * 0.2) * 0.5 + (Math.random() - 0.5) * 0.3
    approachTemps.push(Number(approachVariation.toFixed(1)))
  }

  return { timestamps, fanSpeeds, approachTemps }
}

// 初始化温度图表
const initTempChart = async () => {
  await nextTick()
  if (!tempChartRef.value) {
    setTimeout(() => initTempChart(), 100)
    return
  }

  if (tempChart) tempChart.dispose()

  if (towers.value.length > 0 && !trendTowerId.value) {
    trendTowerId.value = towers.value[0].id
  }

  tempChart = echarts.init(tempChartRef.value)
  updateTemperatureChart()
}

const updateTemperatureChart = () => {
  if (!tempChart || !trendTowerId.value) return

  const data = generateTemperatureData(trendTowerId.value)

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Supply Temp (°C)', 'Return Temp (°C)', 'Approach Temp (°C)'], bottom: 0 },
    grid: { top: 30, right: 20, bottom: 40, left: 50, containLabel: true },
    xAxis: { type: 'category', data: data.timestamps, axisLabel: { rotate: 45, interval: 4, fontSize: 10 } },
    yAxis: { type: 'value', name: 'Temperature (°C)' },
    series: [
      { name: 'Supply Temp (°C)', type: 'line', data: data.supplyTemp, smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Return Temp (°C)', type: 'line', data: data.returnTemp, smooth: true, lineStyle: { color: '#f56c6c', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Approach Temp (°C)', type: 'line', data: data.approachTemp, smooth: true, lineStyle: { color: '#67c23a', width: 2 } }
    ]
  }
  tempChart.setOption(option, true)
}

// 初始化风扇和趋近温度图表
const initFanChart = async () => {
  await nextTick()
  if (!fanChartRef.value) {
    setTimeout(() => initFanChart(), 100)
    return
  }

  if (fanChart) fanChart.dispose()
  fanChart = echarts.init(fanChartRef.value)

  const data = generateFanAndApproachData()

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Fan Speed (%)', 'Approach Temperature (°C)'], bottom: 0 },
    grid: { top: 30, right: 20, bottom: 40, left: 50, containLabel: true },
    xAxis: { type: 'category', data: data.timestamps, axisLabel: { rotate: 45, interval: 4, fontSize: 10 } },
    yAxis: [
      { type: 'value', name: 'Fan Speed (%)', min: 0, max: 100, position: 'left' },
      { type: 'value', name: 'Approach Temp (°C)', position: 'right', min: 0, max: 10 }
    ],
    series: [
      { name: 'Fan Speed (%)', type: 'line', data: data.fanSpeeds, smooth: true, lineStyle: { color: '#e6a23c', width: 2 }, areaStyle: { opacity: 0.1 }, symbol: 'circle', symbolSize: 4 },
      { name: 'Approach Temperature (°C)', type: 'line', yAxisIndex: 1, data: data.approachTemps, smooth: true, lineStyle: { color: '#67c23a', width: 2 }, areaStyle: { opacity: 0.1 }, symbol: 'diamond', symbolSize: 4 }
    ]
  }
  fanChart.setOption(option)
}

// 更新风扇图表
const updateFanChart = () => {
  if (!fanChart) return
  const data = generateFanAndApproachData()
  fanChart.setOption({
    xAxis: { data: data.timestamps },
    series: [{ data: data.fanSpeeds }, { data: data.approachTemps }]
  })
}

// 生成单个冷却塔趋势数据
const generateTowerTrendData = (tower: CoolingTower) => {
  const timestamps = []
  const supplyTemp = []
  const fanSpeed = []
  const now = new Date()

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    timestamps.push(`${String(time.getHours()).padStart(2, '0')}:00`)

    const supplyVariation = tower.supplyTemp + Math.sin(i * 0.3) * 1.5 + (Math.random() - 0.5) * 0.5
    const speedVariation = tower.fanSpeed + Math.sin(i * 0.3) * 10 + (Math.random() - 0.5) * 3

    supplyTemp.push(Number(supplyVariation.toFixed(1)))
    fanSpeed.push(Math.min(100, Math.max(0, Number(speedVariation.toFixed(0)))))
  }

  return { timestamps, supplyTemp, fanSpeed }
}

// 初始化详情图表
const initDetailChart = () => {
  if (!detailChartRef.value || !selectedTower.value) return
  if (detailChart) detailChart.dispose()

  detailChart = echarts.init(detailChartRef.value)
  const data = generateTowerTrendData(selectedTower.value)

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Supply Temp (°C)', 'Fan Speed (%)'], bottom: 0 },
    grid: { top: 30, right: 20, bottom: 40, left: 50, containLabel: true },
    xAxis: { type: 'category', data: data.timestamps, axisLabel: { rotate: 45, interval: 4, fontSize: 10 } },
    yAxis: [
      { type: 'value', name: 'Supply Temp (°C)', position: 'left' },
      { type: 'value', name: 'Fan Speed (%)', position: 'right', min: 0, max: 100 }
    ],
    series: [
      { name: 'Supply Temp (°C)', type: 'line', data: data.supplyTemp, smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Fan Speed (%)', type: 'line', yAxisIndex: 1, data: data.fanSpeed, smooth: true, lineStyle: { color: '#e6a23c', width: 2 } }
    ]
  }
  detailChart.setOption(option)
}

// 更新实时数据
const updateRealtimeData = () => {
  for (const tower of towers.value) {
    if (tower.status === 'running') {
      const loadChange = (Math.random() - 0.5) * 4
      let newLoad = tower.currentLoad + loadChange
      newLoad = Math.max(20, Math.min(95, newLoad))
      tower.currentLoad = Number(newLoad.toFixed(1))

      const speedChange = (Math.random() - 0.5) * 3
      let newSpeed = tower.fanSpeed + speedChange
      newSpeed = Math.max(30, Math.min(100, newSpeed))
      tower.fanSpeed = Number(newSpeed.toFixed(0))

      const supplyChange = (Math.random() - 0.5) * 0.3
      let newSupply = tower.supplyTemp + supplyChange
      newSupply = Math.max(25, Math.min(35, newSupply))
      tower.supplyTemp = Number(newSupply.toFixed(1))

      const returnChange = (Math.random() - 0.5) * 0.4
      let newReturn = tower.returnTemp + returnChange
      newReturn = Math.max(30, Math.min(40, newReturn))
      tower.returnTemp = Number(newReturn.toFixed(1))

      tower.approachTemp = Number((tower.returnTemp - tower.supplyTemp).toFixed(1))

      const energyIncrement = tower.capacity * (tower.currentLoad / 100) * 0.2
      tower.energyToday += energyIncrement
      tower.energyMonth += energyIncrement
    }
  }
}

// 刷新图表
const updateCharts = () => {
  updateTemperatureChart()
  updateFanChart()
}

// 窗口大小适配
const handleResize = () => {
  if (tempChart) tempChart.resize()
  if (fanChart) fanChart.resize()
  if (detailChart) detailChart.resize()
}

// ========== Actions ==========
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

const handlePageChange = () => {
  // page changed
}

const selectTower = (tower: CoolingTower) => {
  selectedTower.value = tower
  detailDrawerVisible.value = true
  setTimeout(() => initDetailChart(), 100)
}

const viewDetail = (tower: CoolingTower) => {
  selectTower(tower)
}

const controlTower = (tower: CoolingTower) => {
  selectedTower.value = tower
  controlForm.fanSpeed = tower.fanSpeed
  controlForm.setpoint = tower.supplyTemp
  controlDialogVisible.value = true
}

const sendCommand = (command: string) => {
  ElMessage.success(`${command.toUpperCase()} command sent to ${selectedTower.value.name}`)
  if (command === 'start') {
    selectedTower.value.status = 'running'
    selectedTower.value.currentLoad = 30
    selectedTower.value.fanSpeed = 40
  } else if (command === 'stop') {
    selectedTower.value.status = 'standby'
    selectedTower.value.currentLoad = 0
    selectedTower.value.fanSpeed = 0
  }
  controlDialogVisible.value = false
  updateCharts()
}

const showAlarms = (tower: CoolingTower) => {
  selectedTower.value = tower
  alarmDialogVisible.value = true
}

const viewAlarms = (tower: CoolingTower) => {
  showAlarms(tower)
}

const exportTowerData = (tower: CoolingTower) => {
  ElMessage.success(`Exporting data for ${tower.name}`)
}

const exportReport = () => {
  ElMessage.success('Exporting cooling tower report')
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
.cooling-towers-container { padding: 20px; background: #f5f7fa; min-height: 100%; }

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

/* Tower Visualization */
.tower-visualization { background: white; border-radius: 20px; padding: 20px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.tower-title { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.tower-title h3 { display: flex; align-items: center; gap: 8px; margin: 0; font-size: 18px; }
.tower-legend { display: flex; gap: 20px; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 6px; }
.legend-dot.running { background: #67c23a; box-shadow: 0 0 4px #67c23a; }
.legend-dot.standby { background: #409eff; }
.legend-dot.maintenance { background: #e6a23c; }
.legend-dot.offline { background: #f56c6c; }

.tower-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; }
.tower-unit { background: #f8fafc; border-radius: 16px; padding: 16px; cursor: pointer; transition: all 0.3s ease; border-left: 4px solid; }
.tower-unit.running { border-left-color: #67c23a; background: linear-gradient(135deg, #f8fafc, #f0fdf4); }
.tower-unit.standby { border-left-color: #409eff; }
.tower-unit.maintenance { border-left-color: #e6a23c; background: linear-gradient(135deg, #f8fafc, #fefce8); }
.tower-unit.offline { border-left-color: #f56c6c; background: linear-gradient(135deg, #f8fafc, #fef2f2); opacity: 0.8; }
.tower-unit:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); }

.tower-image { position: relative; display: flex; justify-content: center; margin-bottom: 12px; }
.tower-img { width: 100px; height: 100px; object-fit: contain; }
.status-badge { position: absolute; top: 0; right: 0; width: 12px; height: 12px; border-radius: 50%; }
.status-badge.running { background: #67c23a; box-shadow: 0 0 8px #67c23a; animation: pulse 2s infinite; }
.status-badge.standby { background: #409eff; }
.status-badge.maintenance { background: #e6a23c; }
.status-badge.offline { background: #f56c6c; }

.tower-info { text-align: center; margin-bottom: 12px; }
.tower-name { margin: 0 0 4px 0; font-size: 16px; font-weight: 600; color: #1e293b; }
.tower-location { margin: 0; font-size: 11px; color: #64748b; display: flex; align-items: center; justify-content: center; gap: 4px; }
.tower-model { margin: 4px 0 0 0; font-size: 11px; color: #94a3b8; }

.tower-metrics { display: flex; justify-content: space-around; margin-bottom: 12px; padding: 8px 0; border-top: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; }
.metric { text-align: center; }
.metric-label { display: block; font-size: 10px; color: #64748b; }
.metric-value { font-size: 14px; font-weight: 600; color: #1e293b; }
.metric-value.load-low { color: #67c23a; }
.metric-value.load-medium { color: #409eff; }
.metric-value.load-high { color: #e6a23c; }

.tower-footer { margin-top: 8px; }
.tower-actions { display: flex; justify-content: center; gap: 8px; margin-top: 8px; }

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
.tower-detail { padding: 8px; }
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
  .cooling-towers-container { padding: 12px; }
  .plant-overview { grid-template-columns: 1fr; }
  .tower-grid { grid-template-columns: 1fr; }
  .tower-title { flex-direction: column; align-items: flex-start; }
  .metric-row { flex-wrap: wrap; }
  .temp-chart, .fan-chart { height: 250px; }
}
</style>