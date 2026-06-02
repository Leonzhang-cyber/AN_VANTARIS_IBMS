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
        <div class="loading-tip">VENTILATION SYSTEMS</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Page Content -->
  <div v-else class="ventilation-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/systems-devices/device-inventory' }">
            Systems & Devices
          </el-breadcrumb-item>
          <el-breadcrumb-item>HVAC Systems</el-breadcrumb-item>
          <el-breadcrumb-item>Ventilation Systems</el-breadcrumb-item>
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
        <div class="overview-icon"><el-icon><WindPower /></el-icon></div>
        <div class="overview-info">
          <span class="overview-value">{{ fans.length }}</span>
          <span class="overview-label">Total Fans</span>
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
          <span class="overview-value">{{ totalAirflow.toFixed(0) }}</span>
          <span class="overview-label">Total Airflow (m³/h)</span>
        </div>
      </div>
      <div class="overview-card">
        <div class="overview-icon"><el-icon><TrendCharts /></el-icon></div>
        <div class="overview-info">
          <span class="overview-value">{{ avgAirQuality.toFixed(0) }}</span>
          <span class="overview-label">Avg Air Quality (%)</span>
        </div>
      </div>
    </div>

    <!-- Ventilation Visualization Grid -->
    <div class="ventilation-visualization">
      <div class="ventilation-title">
        <h3><el-icon><OfficeBuilding /></el-icon> Ventilation Systems - Overview</h3>
        <div class="ventilation-legend">
          <span><span class="legend-dot running"></span> Running</span>
          <span><span class="legend-dot standby"></span> Standby</span>
          <span><span class="legend-dot maintenance"></span> Maintenance</span>
          <span><span class="legend-dot offline"></span> Offline</span>
        </div>
      </div>

      <div class="fans-grid">
        <div v-for="fan in fans" :key="fan.id" class="fan-unit" :class="fan.status" @click="selectFan(fan)">
          <div class="fan-image">
            <img :src="fanImages[fan.status]" :alt="fan.name" class="fan-img" @error="handleImageError">
            <div class="status-badge" :class="fan.status"></div>
          </div>
          <div class="fan-info">
            <h4 class="fan-name">{{ fan.name }}</h4>
            <p class="fan-location"><el-icon><Location /></el-icon> {{ fan.location }}</p>
            <p class="fan-model">{{ fan.manufacturer }} {{ fan.model }}</p>
          </div>
          <div class="fan-metrics">
            <div class="metric">
              <span class="metric-label">Airflow</span>
              <span class="metric-value">{{ fan.airflow }} m³/h</span>
            </div>
            <div class="metric">
              <span class="metric-label">Speed</span>
              <span class="metric-value">{{ fan.speed }}%</span>
            </div>
            <div class="metric">
              <span class="metric-label">CO₂</span>
              <span class="metric-value">{{ fan.co2Level }} ppm</span>
            </div>
          </div>
          <div class="fan-footer">
            <el-progress :percentage="fan.load" :stroke-width="6" :color="getLoadColor(fan.load)" :show-text="false" />
            <div class="fan-actions">
              <el-button size="small" text @click.stop="viewDetail(fan)">Details</el-button>
              <el-button size="small" text type="primary" @click.stop="controlFan(fan)">Control</el-button>
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
            <span><el-icon><TrendCharts /></el-icon> Airflow & Speed Trend</span>
            <el-select v-model="trendFanId" placeholder="Select Fan" size="small" style="width: 180px" filterable @change="updateAirflowChart">
              <el-option v-for="fan in fans" :key="fan.id" :label="fan.name" :value="fan.id" />
            </el-select>
          </div>
        </template>
        <div ref="airflowChartRef" class="airflow-chart"></div>
      </el-card>

      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header-title">
            <span><el-icon><DataAnalysis /></el-icon> Air Quality Distribution</span>
          </div>
        </template>
        <div ref="qualityChartRef" class="quality-chart"></div>
      </el-card>
    </div>

    <!-- Fans List -->
    <el-card shadow="hover">
      <template #header>
        <div class="card-header-title">Ventilation Systems List</div>
      </template>
      <el-table :data="paginatedTableData" border stripe height="350" v-loading="tableLoading">
        <el-table-column label="Name" prop="name"  />
        <el-table-column label="Manufacturer" prop="manufacturer"  />
        <el-table-column label="Model" prop="model"  />
        <el-table-column label="Type" prop="fanType" >
          <template #default="scope">
            <el-tag size="small">{{ scope.row.fanType }}</el-tag>
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
        <el-table-column label="Airflow" prop="airflow" >
          <template #default="scope">{{ scope.row.airflow }} m³/h</template>
        </el-table-column>
        <el-table-column label="Speed" prop="speed" >
          <template #default="scope">
            <el-progress :percentage="scope.row.speed" :stroke-width="6" :color="getLoadColor(scope.row.speed)" :show-text="false" style="width: 80px" />
            <span style="margin-left: 8px">{{ scope.row.speed }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="CO₂" prop="co2Level" >
          <template #default="scope">{{ scope.row.co2Level }} ppm</template>
        </el-table-column>
        <el-table-column label="Temp" prop="temperature" >
          <template #default="scope">{{ scope.row.temperature }}°C</template>
        </el-table-column>
        <el-table-column label="Humidity" prop="humidity" >
          <template #default="scope">{{ scope.row.humidity }}%</template>
        </el-table-column>
        <el-table-column label="Energy" prop="energyToday" >
          <template #default="scope">{{ scope.row.energyToday.toLocaleString() }} kWh</template>
        </el-table-column>
        <el-table-column label="Operation" width="160" fixed="right">
          <template #default="scope">
            <el-button text type="primary" size="small" @click="viewDetail(scope.row)">Detail</el-button>
            <el-button text type="warning" size="small" @click="controlFan(scope.row)">Control</el-button>
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

    <!-- Fan Details Drawer -->
    <el-drawer v-model="detailDrawerVisible" :title="selectedFan?.name" size="40%" direction="rtl">
      <div v-if="selectedFan" class="fan-detail">
        <div class="detail-header">
          <div class="detail-status" :class="selectedFan.status">
            <span class="status-dot-large"></span>
            <span>{{ selectedFan.status.toUpperCase() }}</span>
          </div>
          <h2>{{ selectedFan.name }}</h2>
          <p>{{ selectedFan.manufacturer }} {{ selectedFan.model }}</p>
        </div>

        <el-divider />

        <div class="detail-metrics">
          <div class="metric-row">
            <div class="metric-card">
              <span class="metric-label">Airflow</span>
              <span class="metric-value">{{ selectedFan.airflow }} <span class="metric-unit">m³/h</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Fan Speed</span>
              <span class="metric-value">{{ selectedFan.speed }}<span class="metric-unit">%</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Static Pressure</span>
              <span class="metric-value">{{ selectedFan.staticPressure }}<span class="metric-unit">Pa</span></span>
            </div>
          </div>
          <div class="metric-row">
            <div class="metric-card">
              <span class="metric-label">CO₂ Level</span>
              <span class="metric-value">{{ selectedFan.co2Level }}<span class="metric-unit">ppm</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Temperature</span>
              <span class="metric-value">{{ selectedFan.temperature }}<span class="metric-unit">°C</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Humidity</span>
              <span class="metric-value">{{ selectedFan.humidity }}<span class="metric-unit">%</span></span>
            </div>
          </div>
          <div class="metric-row">
            <div class="metric-card">
              <span class="metric-label">Air Quality</span>
              <span class="metric-value">{{ selectedFan.airQuality }}<span class="metric-unit">%</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Filter Status</span>
              <span class="metric-value">{{ selectedFan.filterStatus }}</span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Energy Today</span>
              <span class="metric-value">{{ selectedFan.energyToday.toLocaleString() }}<span class="metric-unit">kWh</span></span>
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
          <el-button type="primary" @click="controlFan(selectedFan)">Control Fan</el-button>
          <el-button @click="viewAlarms(selectedFan)">View Alarms</el-button>
          <el-button @click="exportFanData(selectedFan)">Export Data</el-button>
        </div>
      </div>
    </el-drawer>

    <!-- Control Dialog -->
    <el-dialog v-model="controlDialogVisible" :title="`Control - ${selectedFan?.name}`" width="450px">
      <el-form :model="controlForm" label-width="120px">
        <el-form-item label="Operation Mode">
          <el-radio-group v-model="controlForm.mode">
            <el-radio label="auto">Auto</el-radio>
            <el-radio label="manual">Manual</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Fan Speed">
          <el-slider v-model="controlForm.speed" :min="0" :max="100" :step="5" />
        </el-form-item>
        <el-form-item label="Airflow Setpoint">
          <el-input-number v-model="controlForm.airflowSetpoint" :min="0" :max="50000" :step="500" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Commands">
          <el-button-group>
            <el-button type="success" @click="sendCommand('start')" :disabled="selectedFan?.status === 'running'">Start</el-button>
            <el-button type="warning" @click="sendCommand('stop')" :disabled="selectedFan?.status !== 'running'">Stop</el-button>
            <el-button type="primary" @click="sendCommand('reset')">Reset</el-button>
          </el-button-group>
        </el-form-item>
      </el-form>
    </el-dialog>

    <!-- Alarms Dialog -->
    <el-dialog v-model="alarmDialogVisible" :title="`Alarms - ${selectedFan?.name}`" width="600px">
      <el-table :data="selectedFan?.alarms || []" stripe border>
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
const loadingMessage = ref('Loading ventilation systems...')
const loadingMessages = [
  'Initializing ventilation systems...',
  'Loading fan data...',
  'Connecting to controllers...',
  'Rendering system layout...',
  'Almost ready...'
]

// ========== Chart References ==========
const airflowChartRef = ref<HTMLDivElement | null>(null)
const qualityChartRef = ref<HTMLDivElement | null>(null)
const detailChartRef = ref<HTMLDivElement | null>(null)
let airflowChart: echarts.ECharts | null = null
let qualityChart: echarts.ECharts | null = null
let detailChart: echarts.ECharts | null = null
let refreshTimer: number | null = null
const refreshing = ref(false)
const tableLoading = ref(false)
const trendFanId = ref('')

// ========== Fan Images ==========
const fanImages = {
  running: 'https://aegisnx.com/wp-content/uploads/2026/05/520131452044.webp',
  standby: 'https://aegisnx.com/wp-content/uploads/2026/05/520131452044.webp',
  maintenance: 'https://aegisnx.com/wp-content/uploads/2026/05/520131452044.webp',
  offline: 'https://aegisnx.com/wp-content/uploads/2026/05/520131452044.webp',
  default: 'https://aegisnx.com/wp-content/uploads/2026/05/520131452044.webp'
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  if (fanImages.default) {
    img.src = fanImages.default
  }
}

// ========== Dialog State ==========
const detailDrawerVisible = ref(false)
const controlDialogVisible = ref(false)
const alarmDialogVisible = ref(false)
const selectedFan = ref<any>(null)
const controlForm = reactive({
  mode: 'auto',
  speed: 70,
  airflowSetpoint: 10000
})

// ========== Fan Data ==========
interface Fan {
  id: string
  name: string
  manufacturer: string
  model: string
  fanType: string
  status: 'running' | 'standby' | 'maintenance' | 'offline'
  airflow: number
  speed: number
  staticPressure: number
  co2Level: number
  temperature: number
  humidity: number
  airQuality: number
  filterStatus: string
  load: number
  energyToday: number
  energyMonth: number
  location: string
  alarms: any[]
}

const fans = ref<Fan[]>([
  { id: '1', name: 'Supply Fan-B2-01', manufacturer: 'Greenheck', model: 'CUBE 100', fanType: 'Centrifugal', status: 'running', airflow: 12500, speed: 78, staticPressure: 450, co2Level: 420, temperature: 22.5, humidity: 55, airQuality: 94, filterStatus: 'Clean', load: 78, energyToday: 1560, energyMonth: 46800, location: 'Basement B2', alarms: [] },
  { id: '2', name: 'Return Fan-B2-01', manufacturer: 'Greenheck', model: 'CUBE 80', fanType: 'Centrifugal', status: 'running', airflow: 11800, speed: 72, staticPressure: 420, co2Level: 415, temperature: 23.0, humidity: 54, airQuality: 95, filterStatus: 'Clean', load: 72, energyToday: 1420, energyMonth: 42600, location: 'Basement B2', alarms: [] },
  { id: '3', name: 'Exhaust Fan-B1-01', manufacturer: 'Twin City', model: 'BI-120', fanType: 'Axial', status: 'running', airflow: 8500, speed: 68, staticPressure: 380, co2Level: 450, temperature: 24.0, humidity: 58, airQuality: 88, filterStatus: 'Clean', load: 68, energyToday: 980, energyMonth: 29400, location: 'Parking B1', alarms: [] },
  { id: '4', name: 'Exhaust Fan-B1-02', manufacturer: 'Twin City', model: 'BI-100', fanType: 'Axial', status: 'running', airflow: 7800, speed: 65, staticPressure: 360, co2Level: 460, temperature: 24.5, humidity: 59, airQuality: 86, filterStatus: 'Clean', load: 65, energyToday: 890, energyMonth: 26700, location: 'Parking B1', alarms: [] },
  { id: '5', name: 'Supply Fan-1F-01', manufacturer: 'Greenheck', model: 'CUBE 150', fanType: 'Centrifugal', status: 'running', airflow: 15800, speed: 82, staticPressure: 520, co2Level: 410, temperature: 21.5, humidity: 52, airQuality: 96, filterStatus: 'Clean', load: 82, energyToday: 2450, energyMonth: 73500, location: 'Lobby 1F', alarms: [] },
  { id: '6', name: 'Return Fan-1F-01', manufacturer: 'Greenheck', model: 'CUBE 120', fanType: 'Centrifugal', status: 'running', airflow: 14200, speed: 75, staticPressure: 490, co2Level: 405, temperature: 22.0, humidity: 53, airQuality: 96, filterStatus: 'Clean', load: 75, energyToday: 2180, energyMonth: 65400, location: 'Lobby 1F', alarms: [] },
  { id: '7', name: 'Exhaust Fan-2F-01', manufacturer: 'Twin City', model: 'BI-80', fanType: 'Axial', status: 'standby', airflow: 0, speed: 0, staticPressure: 0, co2Level: 430, temperature: 23.5, humidity: 56, airQuality: 90, filterStatus: 'Clean', load: 0, energyToday: 0, energyMonth: 0, location: 'Office 2F', alarms: [] },
  { id: '8', name: 'Supply Fan-RF-01', manufacturer: 'Greenheck', model: 'CUBE 200', fanType: 'Centrifugal', status: 'maintenance', airflow: 0, speed: 0, staticPressure: 0, co2Level: 480, temperature: 26.0, humidity: 62, airQuality: 72, filterStatus: 'Dirty', load: 0, energyToday: 0, energyMonth: 0, location: 'Roof', alarms: [{ timestamp: '2026-06-01 09:00:00', severity: 'critical', code: 'E-601', message: 'Filter clogged - replace immediately', status: 'active' }] }
])

const runningCount = computed(() => fans.value.filter(f => f.status === 'running').length)
const runningPercent = computed(() => fans.value.length ? Math.round(runningCount.value / fans.value.length * 100) : 0)
const totalAirflow = computed(() => fans.value.reduce((sum, f) => sum + f.airflow, 0))
const avgAirQuality = computed(() => {
  const running = fans.value.filter(f => f.status === 'running')
  if (running.length === 0) return 0
  return running.reduce((sum, f) => sum + f.airQuality, 0) / running.length
})

const paginatedTableData = computed(() => {
  const start = (pageInfo.pageNum - 1) * pageInfo.pageSize
  return fans.value.slice(start, start + pageInfo.pageSize)
})

const pageInfo = reactive({
  pageNum: 1,
  pageSize: 10,
  total: fans.value.length
})

const getLoadColor = (load: number) => {
  if (load < 30) return '#67c23a'
  if (load < 70) return '#409eff'
  return '#e6a23c'
}

// 生成风量和速度趋势数据
const generateAirflowData = (fanId: string) => {
  const fan = fans.value.find(f => f.id === fanId)
  if (!fan) return { timestamps: [], airflow: [], speed: [] }

  const timestamps = []
  const airflow = []
  const speed = []
  const now = new Date()

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    timestamps.push(`${String(time.getHours()).padStart(2, '0')}:00`)

    const airflowVar = fan.airflow + Math.sin(i * 0.3) * (fan.airflow * 0.12) + (Math.random() - 0.5) * 200
    const speedVar = fan.speed + Math.sin(i * 0.3) * 6 + (Math.random() - 0.5) * 3

    airflow.push(Math.max(0, Number(airflowVar.toFixed(0))))
    speed.push(Math.min(100, Math.max(0, Number(speedVar.toFixed(0)))))
  }

  return { timestamps, airflow, speed }
}

// 生成空气质量分布数据
const generateQualityData = () => {
  const ranges = [
    { name: 'Excellent (>90%)', value: fans.value.filter(f => f.airQuality > 90 && f.status === 'running').length },
    { name: 'Good (75-90%)', value: fans.value.filter(f => f.airQuality >= 75 && f.airQuality <= 90 && f.status === 'running').length },
    { name: 'Fair (60-74%)', value: fans.value.filter(f => f.airQuality >= 60 && f.airQuality < 75 && f.status === 'running').length },
    { name: 'Poor (<60%)', value: fans.value.filter(f => f.airQuality < 60 && f.status === 'running').length }
  ]
  return ranges.filter(r => r.value > 0)
}

// 初始化风量图表
const initAirflowChart = async () => {
  await nextTick()
  if (!airflowChartRef.value) {
    setTimeout(() => initAirflowChart(), 100)
    return
  }

  if (airflowChart) airflowChart.dispose()

  if (fans.value.length > 0 && !trendFanId.value) {
    trendFanId.value = fans.value[0].id
  }

  airflowChart = echarts.init(airflowChartRef.value)
  updateAirflowChart()
}

const updateAirflowChart = () => {
  if (!airflowChart || !trendFanId.value) return

  const data = generateAirflowData(trendFanId.value)

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Airflow (m³/h)', 'Fan Speed (%)'], bottom: 0 },
    grid: { top: 30, right: 20, bottom: 40, left: 50, containLabel: true },
    xAxis: { type: 'category', data: data.timestamps, axisLabel: { rotate: 45, interval: 4, fontSize: 10 } },
    yAxis: [
      { type: 'value', name: 'Airflow (m³/h)', position: 'left' },
      { type: 'value', name: 'Fan Speed (%)', position: 'right', min: 0, max: 100 }
    ],
    series: [
      { name: 'Airflow (m³/h)', type: 'line', data: data.airflow, smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Fan Speed (%)', type: 'line', yAxisIndex: 1, data: data.speed, smooth: true, lineStyle: { color: '#e6a23c', width: 2 }, areaStyle: { opacity: 0.1 } }
    ]
  }
  airflowChart.setOption(option, true)
}

// 初始化空气质量分布图表（饼图）
const initQualityChart = async () => {
  await nextTick()
  if (!qualityChartRef.value) {
    setTimeout(() => initQualityChart(), 100)
    return
  }

  if (qualityChart) qualityChart.dispose()
  qualityChart = echarts.init(qualityChartRef.value)

  const data = generateQualityData()

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
  qualityChart.setOption(option)
}

const updateQualityChart = () => {
  if (!qualityChart) return
  const data = generateQualityData()
  qualityChart.setOption({
    series: [{ data: data }],
    legend: { data: data.map(d => d.name) }
  })
}

// 生成单个风扇趋势数据
const generateFanTrendData = (fan: Fan) => {
  const timestamps = []
  const airflow = []
  const speed = []
  const now = new Date()

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    timestamps.push(`${String(time.getHours()).padStart(2, '0')}:00`)

    const airflowVar = fan.airflow + Math.sin(i * 0.3) * (fan.airflow * 0.1) + (Math.random() - 0.5) * 150
    const speedVar = fan.speed + Math.sin(i * 0.3) * 5 + (Math.random() - 0.5) * 2

    airflow.push(Math.max(0, Number(airflowVar.toFixed(0))))
    speed.push(Math.min(100, Math.max(0, Number(speedVar.toFixed(0)))))
  }

  return { timestamps, airflow, speed }
}

// 初始化详情图表
const initDetailChart = () => {
  if (!detailChartRef.value || !selectedFan.value) return
  if (detailChart) detailChart.dispose()

  detailChart = echarts.init(detailChartRef.value)
  const data = generateFanTrendData(selectedFan.value)

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Airflow (m³/h)', 'Fan Speed (%)'], bottom: 0 },
    grid: { top: 30, right: 20, bottom: 40, left: 50, containLabel: true },
    xAxis: { type: 'category', data: data.timestamps, axisLabel: { rotate: 45, interval: 4, fontSize: 10 } },
    yAxis: [
      { type: 'value', name: 'Airflow (m³/h)', position: 'left' },
      { type: 'value', name: 'Fan Speed (%)', position: 'right', min: 0, max: 100 }
    ],
    series: [
      { name: 'Airflow (m³/h)', type: 'line', data: data.airflow, smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Fan Speed (%)', type: 'line', yAxisIndex: 1, data: data.speed, smooth: true, lineStyle: { color: '#e6a23c', width: 2 } }
    ]
  }
  detailChart.setOption(option)
}

// 更新实时数据
const updateRealtimeData = () => {
  for (const fan of fans.value) {
    if (fan.status === 'running') {
      const airflowChange = (Math.random() - 0.5) * 200
      let newAirflow = fan.airflow + airflowChange
      newAirflow = Math.max(1000, Math.min(20000, newAirflow))
      fan.airflow = Number(newAirflow.toFixed(0))

      const speedChange = (Math.random() - 0.5) * 3
      let newSpeed = fan.speed + speedChange
      newSpeed = Math.min(100, Math.max(30, newSpeed))
      fan.speed = Number(newSpeed.toFixed(0))

      const co2Change = (Math.random() - 0.5) * 10
      fan.co2Level = Math.min(600, Math.max(350, fan.co2Level + co2Change))

      const tempChange = (Math.random() - 0.5) * 0.3
      fan.temperature = Number((fan.temperature + tempChange).toFixed(1))

      const humidityChange = (Math.random() - 0.5) * 2
      fan.humidity = Math.min(80, Math.max(40, fan.humidity + humidityChange))

      fan.airQuality = Math.min(100, Math.max(50, 100 - (fan.co2Level - 400) / 4))

      fan.load = fan.speed
      fan.energyToday += fan.load * 1.2
      fan.energyMonth += fan.load * 1.2
    }
  }
}

// 刷新图表
const updateCharts = () => {
  updateAirflowChart()
  updateQualityChart()
}

// 窗口大小适配
const handleResize = () => {
  if (airflowChart) airflowChart.resize()
  if (qualityChart) qualityChart.resize()
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

const selectFan = (fan: Fan) => {
  selectedFan.value = fan
  detailDrawerVisible.value = true
  setTimeout(() => initDetailChart(), 100)
}

const viewDetail = (fan: Fan) => {
  selectFan(fan)
}

const controlFan = (fan: Fan) => {
  selectedFan.value = fan
  controlForm.speed = fan.speed
  controlForm.airflowSetpoint = fan.airflow
  controlDialogVisible.value = true
}

const sendCommand = (command: string) => {
  ElMessage.success(`${command.toUpperCase()} command sent to ${selectedFan.value.name}`)
  if (command === 'start') {
    selectedFan.value.status = 'running'
    selectedFan.value.speed = 40
    selectedFan.value.airflow = 4000
    selectedFan.value.load = 40
  } else if (command === 'stop') {
    selectedFan.value.status = 'standby'
    selectedFan.value.speed = 0
    selectedFan.value.airflow = 0
    selectedFan.value.load = 0
  }
  controlDialogVisible.value = false
  updateCharts()
}

const showAlarms = (fan: Fan) => {
  selectedFan.value = fan
  alarmDialogVisible.value = true
}

const viewAlarms = (fan: Fan) => {
  showAlarms(fan)
}

const exportFanData = (fan: Fan) => {
  ElMessage.success(`Exporting data for ${fan.name}`)
}

const exportReport = () => {
  ElMessage.success('Exporting ventilation report')
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
        initAirflowChart()
        initQualityChart()
        startAutoRefresh()
        window.addEventListener('resize', handleResize)
      }, 200)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
  if (airflowChart) airflowChart.dispose()
  if (qualityChart) qualityChart.dispose()
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
.ventilation-container { padding: 20px; background: #f5f7fa; min-height: 100%; }

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

/* Ventilation Visualization */
.ventilation-visualization { background: white; border-radius: 20px; padding: 20px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.ventilation-title { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.ventilation-title h3 { display: flex; align-items: center; gap: 8px; margin: 0; font-size: 18px; }
.ventilation-legend { display: flex; gap: 20px; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 6px; }
.legend-dot.running { background: #67c23a; box-shadow: 0 0 4px #67c23a; }
.legend-dot.standby { background: #409eff; }
.legend-dot.maintenance { background: #e6a23c; }
.legend-dot.offline { background: #f56c6c; }

.fans-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; }
.fan-unit { background: #f8fafc; border-radius: 16px; padding: 16px; cursor: pointer; transition: all 0.3s ease; border-left: 4px solid; }
.fan-unit.running { border-left-color: #67c23a; background: linear-gradient(135deg, #f8fafc, #f0fdf4); }
.fan-unit.standby { border-left-color: #409eff; }
.fan-unit.maintenance { border-left-color: #e6a23c; background: linear-gradient(135deg, #f8fafc, #fefce8); }
.fan-unit.offline { border-left-color: #f56c6c; background: linear-gradient(135deg, #f8fafc, #fef2f2); opacity: 0.8; }
.fan-unit:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); }

.fan-image { position: relative; display: flex; justify-content: center; margin-bottom: 12px; }
.fan-img { width: 100px; height: 100px; object-fit: contain; }
.status-badge { position: absolute; top: 0; right: 0; width: 12px; height: 12px; border-radius: 50%; }
.status-badge.running { background: #67c23a; box-shadow: 0 0 8px #67c23a; animation: pulse 2s infinite; }
.status-badge.standby { background: #409eff; }
.status-badge.maintenance { background: #e6a23c; }
.status-badge.offline { background: #f56c6c; }

.fan-info { text-align: center; margin-bottom: 12px; }
.fan-name { margin: 0 0 4px 0; font-size: 16px; font-weight: 600; color: #1e293b; }
.fan-location { margin: 0; font-size: 11px; color: #64748b; display: flex; align-items: center; justify-content: center; gap: 4px; }
.fan-model { margin: 4px 0 0 0; font-size: 11px; color: #94a3b8; }

.fan-metrics { display: flex; justify-content: space-around; margin-bottom: 12px; padding: 8px 0; border-top: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; }
.metric { text-align: center; }
.metric-label { display: block; font-size: 10px; color: #64748b; }
.metric-value { font-size: 14px; font-weight: 600; color: #1e293b; }

.fan-footer { margin-top: 8px; }
.fan-actions { display: flex; justify-content: center; gap: 8px; margin-top: 8px; }

/* Charts Section */
.charts-section { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }
.chart-card { border-radius: 16px; }
.card-header-title { display: flex; justify-content: space-between; align-items: center; font-weight: 600; color: #1e293b; font-size: 16px; flex-wrap: wrap; gap: 12px; }
.airflow-chart, .quality-chart { width: 100%; height: 320px; }

/* Status Cell */
.status-cell { display: flex; align-items: center; gap: 6px; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; }
.status-dot.running { background: #67c23a; box-shadow: 0 0 4px #67c23a; animation: pulse 2s infinite; }
.status-dot.standby { background: #409eff; }
.status-dot.maintenance { background: #e6a23c; }
.status-dot.offline { background: #f56c6c; }

/* Drawer Styles */
.fan-detail { padding: 8px; }
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
  .ventilation-container { padding: 12px; }
  .plant-overview { grid-template-columns: 1fr; }
  .fans-grid { grid-template-columns: 1fr; }
  .ventilation-title { flex-direction: column; align-items: flex-start; }
  .metric-row { flex-wrap: wrap; }
  .airflow-chart, .quality-chart { height: 250px; }
}
</style>