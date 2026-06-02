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
        <div class="loading-tip">AHU SYSTEMS</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Page Content -->
  <div v-else class="ahu-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/systems-devices/device-inventory' }">
            Systems & Devices
          </el-breadcrumb-item>
          <el-breadcrumb-item>HVAC Systems</el-breadcrumb-item>
          <el-breadcrumb-item>Air Handling Units</el-breadcrumb-item>
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
          <span class="overview-value">12</span>
          <span class="overview-label">Total AHUs</span>
        </div>
      </div>
      <div class="overview-card">
        <div class="overview-icon running"><el-icon><CircleCheckFilled /></el-icon></div>
        <div class="overview-info">
          <span class="overview-value">8</span>
          <span class="overview-label">Running</span>
        </div>
        <div class="overview-trend up">67%</div>
      </div>
      <div class="overview-card">
        <div class="overview-icon"><el-icon><DataLine /></el-icon></div>
        <div class="overview-info">
          <span class="overview-value">124,500</span>
          <span class="overview-label">Total Airflow (m³/h)</span>
        </div>
      </div>
      <div class="overview-card">
        <div class="overview-icon"><el-icon><TrendCharts /></el-icon></div>
        <div class="overview-info">
          <span class="overview-value">76.5</span>
          <span class="overview-label">Avg Efficiency (%)</span>
        </div>
      </div>
    </div>

    <!-- AHU Visualization Grid -->
    <div class="ahu-visualization">
      <div class="ahu-title">
        <h3><el-icon><OfficeBuilding /></el-icon> AHU Systems - Overview</h3>
        <div class="ahu-legend">
          <span><span class="legend-dot running"></span> Running</span>
          <span><span class="legend-dot standby"></span> Standby</span>
          <span><span class="legend-dot maintenance"></span> Maintenance</span>
          <span><span class="legend-dot offline"></span> Offline</span>
        </div>
      </div>

      <div class="ahu-grid">
        <div v-for="ahu in ahus" :key="ahu.id" class="ahu-unit" :class="ahu.status" @click="selectAHU(ahu)">
          <div class="ahu-image">
            <!-- 图片URL请在这里填写 -->
            <img :src="ahuImages[ahu.status]" :alt="ahu.name" class="ahu-img" @error="handleImageError">
            <div class="status-badge" :class="ahu.status"></div>
          </div>
          <div class="ahu-info">
            <h4 class="ahu-name">{{ ahu.name }}</h4>
            <p class="ahu-location"><el-icon><Location /></el-icon> {{ ahu.location }}</p>
            <p class="ahu-model">{{ ahu.manufacturer }} {{ ahu.model }}</p>
          </div>
          <div class="ahu-metrics">
            <div class="metric">
              <span class="metric-label">Supply Temp</span>
              <span class="metric-value">{{ ahu.supplyTemp }}°C</span>
            </div>
            <div class="metric">
              <span class="metric-label">Return Temp</span>
              <span class="metric-value">{{ ahu.returnTemp }}°C</span>
            </div>
            <div class="metric">
              <span class="metric-label">Airflow</span>
              <span class="metric-value">{{ ahu.airflow }} m³/h</span>
            </div>
          </div>
          <div class="ahu-footer">
            <el-progress :percentage="ahu.load" :stroke-width="6" :color="getLoadColor(ahu.load)" :show-text="false" />
            <div class="ahu-actions">
              <el-button size="small" text @click.stop="viewDetail(ahu)">Details</el-button>
              <el-button size="small" text type="primary" @click.stop="controlAHU(ahu)">Control</el-button>
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
            <el-select v-model="trendAHUId" placeholder="Select AHU" size="small" style="width: 180px" filterable @change="updateTempChart">
              <el-option v-for="ahu in ahus" :key="ahu.id" :label="ahu.name" :value="ahu.id" />
            </el-select>
          </div>
        </template>
        <div ref="tempChartRef" class="temp-chart"></div>
      </el-card>

      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header-title">
            <span><el-icon><DataAnalysis /></el-icon> Supply vs Return Airflow</span>
          </div>
        </template>
        <div ref="airflowChartRef" class="airflow-chart"></div>
      </el-card>
    </div>

    <!-- AHU List -->
    <el-card shadow="hover">
      <template #header>
        <div class="card-header-title">AHU Systems List</div>
      </template>
      <el-table :data="paginatedTableData" border stripe height="350" v-loading="tableLoading">
        <el-table-column label="Name" prop="name" width="160" />
        <el-table-column label="Manufacturer" prop="manufacturer"  />
        <el-table-column label="Model" prop="model" width="150" />
        <el-table-column label="Type" prop="ahuType" >
          <template #default="scope">
            <el-tag size="small">{{ scope.row.ahuType }}</el-tag>
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
        <el-table-column label="Supply Temp" prop="supplyTemp" >
          <template #default="scope">{{ scope.row.supplyTemp }}°C</template>
        </el-table-column>
        <el-table-column label="Return Temp" prop="returnTemp" >
          <template #default="scope">{{ scope.row.returnTemp }}°C</template>
        </el-table-column>
        <el-table-column label="Airflow (m³/h)" prop="airflow"  />
        <el-table-column label="Fan Speed" prop="fanSpeed" >
          <template #default="scope">
            <el-progress :percentage="scope.row.fanSpeed" :stroke-width="6" :color="getLoadColor(scope.row.fanSpeed)" :show-text="false" style="width: 80px" />
            <span style="margin-left: 8px">{{ scope.row.fanSpeed }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="Energy (kWh)" prop="energyToday" >
          <template #default="scope">{{ scope.row.energyToday.toLocaleString() }} kWh</template>
        </el-table-column>
        <el-table-column label="Operation" width="160" fixed="right">
          <template #default="scope">
            <el-button text type="primary" size="small" @click="viewDetail(scope.row)">Detail</el-button>
            <el-button text type="warning" size="small" @click="controlAHU(scope.row)">Control</el-button>
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

    <!-- AHU Details Drawer -->
    <el-drawer v-model="detailDrawerVisible" :title="selectedAHU?.name" size="40%" direction="rtl">
      <div v-if="selectedAHU" class="ahu-detail">
        <div class="detail-header">
          <div class="detail-status" :class="selectedAHU.status">
            <span class="status-dot-large"></span>
            <span>{{ selectedAHU.status.toUpperCase() }}</span>
          </div>
          <h2>{{ selectedAHU.name }}</h2>
          <p>{{ selectedAHU.manufacturer }} {{ selectedAHU.model }}</p>
        </div>

        <el-divider />

        <div class="detail-metrics">
          <div class="metric-row">
            <div class="metric-card">
              <span class="metric-label">Supply Temp</span>
              <span class="metric-value">{{ selectedAHU.supplyTemp }} <span class="metric-unit">°C</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Return Temp</span>
              <span class="metric-value">{{ selectedAHU.returnTemp }} <span class="metric-unit">°C</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Delta T</span>
              <span class="metric-value">{{ (selectedAHU.returnTemp - selectedAHU.supplyTemp).toFixed(1) }} <span class="metric-unit">°C</span></span>
            </div>
          </div>
          <div class="metric-row">
            <div class="metric-card">
              <span class="metric-label">Airflow</span>
              <span class="metric-value">{{ selectedAHU.airflow }} <span class="metric-unit">m³/h</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Fan Speed</span>
              <span class="metric-value">{{ selectedAHU.fanSpeed }}<span class="metric-unit">%</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Static Pressure</span>
              <span class="metric-value">{{ selectedAHU.staticPressure }}<span class="metric-unit">Pa</span></span>
            </div>
          </div>
          <div class="metric-row">
            <div class="metric-card">
              <span class="metric-label">Filter Status</span>
              <span class="metric-value">{{ selectedAHU.filterStatus }}</span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Energy Today</span>
              <span class="metric-value">{{ selectedAHU.energyToday.toLocaleString() }}<span class="metric-unit">kWh</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">CO₂ Level</span>
              <span class="metric-value">{{ selectedAHU.co2Level }}<span class="metric-unit">ppm</span></span>
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
          <el-button type="primary" @click="controlAHU(selectedAHU)">Control AHU</el-button>
          <el-button @click="viewAlarms(selectedAHU)">View Alarms</el-button>
          <el-button @click="exportAHUData(selectedAHU)">Export Data</el-button>
        </div>
      </div>
    </el-drawer>

    <!-- Control Dialog -->
    <el-dialog v-model="controlDialogVisible" :title="`Control - ${selectedAHU?.name}`" width="450px">
      <el-form :model="controlForm" label-width="120px">
        <el-form-item label="Operation Mode">
          <el-radio-group v-model="controlForm.mode">
            <el-radio label="auto">Auto</el-radio>
            <el-radio label="manual">Manual</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Supply Temp Setpoint">
          <el-input-number v-model="controlForm.tempSetpoint" :min="18" :max="26" :step="0.5" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Fan Speed Setpoint">
          <el-slider v-model="controlForm.fanSpeed" :min="0" :max="100" :step="5" />
        </el-form-item>
        <el-form-item label="Commands">
          <el-button-group>
            <el-button type="success" @click="sendCommand('start')" :disabled="selectedAHU?.status === 'running'">Start</el-button>
            <el-button type="warning" @click="sendCommand('stop')" :disabled="selectedAHU?.status !== 'running'">Stop</el-button>
            <el-button type="primary" @click="sendCommand('reset')">Reset</el-button>
          </el-button-group>
        </el-form-item>
      </el-form>
    </el-dialog>

    <!-- Alarms Dialog -->
    <el-dialog v-model="alarmDialogVisible" :title="`Alarms - ${selectedAHU?.name}`" width="600px">
      <el-table :data="selectedAHU?.alarms || []" stripe border>
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
const loadingMessage = ref('Loading AHU systems...')
const loadingMessages = [
  'Initializing AHU systems...',
  'Loading unit data...',
  'Connecting to controllers...',
  'Rendering system layout...',
  'Almost ready...'
]

// ========== Chart References ==========
const tempChartRef = ref<HTMLDivElement | null>(null)
const airflowChartRef = ref<HTMLDivElement | null>(null)
const detailChartRef = ref<HTMLDivElement | null>(null)
let tempChart: echarts.ECharts | null = null
let airflowChart: echarts.ECharts | null = null
let detailChart: echarts.ECharts | null = null
let refreshTimer: number | null = null
const refreshing = ref(false)
const tableLoading = ref(false)
const trendAHUId = ref('')

// ========== AHU Images ==========
// 请在这里填写您的AHU图片URL
const ahuImages = {
  running: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567.webp',
  standby: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567.webp',
  maintenance: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567.webp',
  offline: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567.webp',
  default: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567.webp'
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  if (ahuImages.default) {
    img.src = ahuImages.default
  }
}

// ========== Dialog State ==========
const detailDrawerVisible = ref(false)
const controlDialogVisible = ref(false)
const alarmDialogVisible = ref(false)
const selectedAHU = ref<any>(null)
const controlForm = reactive({
  mode: 'auto',
  tempSetpoint: 22,
  fanSpeed: 70
})

// ========== AHU Data ==========
interface AHU {
  id: string
  name: string
  manufacturer: string
  model: string
  ahuType: string
  status: 'running' | 'standby' | 'maintenance' | 'offline'
  supplyTemp: number
  returnTemp: number
  airflow: number
  fanSpeed: number
  staticPressure: number
  filterStatus: string
  co2Level: number
  load: number
  energyToday: number
  energyMonth: number
  location: string
  alarms: any[]
}

const ahus = ref<AHU[]>([
  { id: '1', name: 'AHU-B2-01', manufacturer: 'Carrier', model: '39G', ahuType: 'VAV', status: 'running', supplyTemp: 13.2, returnTemp: 22.5, airflow: 12500, fanSpeed: 78, staticPressure: 650, filterStatus: 'Clean', co2Level: 420, load: 72, energyToday: 18500, energyMonth: 555000, location: 'Basement B2', alarms: [] },
  { id: '2', name: 'AHU-B2-02', manufacturer: 'Carrier', model: '39G', ahuType: 'VAV', status: 'running', supplyTemp: 13.5, returnTemp: 22.8, airflow: 11800, fanSpeed: 75, staticPressure: 630, filterStatus: 'Clean', co2Level: 415, load: 68, energyToday: 17200, energyMonth: 516000, location: 'Basement B2', alarms: [] },
  { id: '3', name: 'AHU-1F-01', manufacturer: 'Trane', model: 'IntelliPak', ahuType: 'CAV', status: 'running', supplyTemp: 14.0, returnTemp: 23.5, airflow: 15800, fanSpeed: 82, staticPressure: 720, filterStatus: 'Clean', co2Level: 430, load: 78, energyToday: 22500, energyMonth: 675000, location: 'Lobby 1F', alarms: [] },
  { id: '4', name: 'AHU-2F-01', manufacturer: 'Daikin', model: 'SkyAir', ahuType: 'VAV', status: 'running', supplyTemp: 13.8, returnTemp: 23.2, airflow: 9800, fanSpeed: 68, staticPressure: 580, filterStatus: 'Clean', co2Level: 425, load: 62, energyToday: 14500, energyMonth: 435000, location: 'Office 2F', alarms: [] },
  { id: '5', name: 'AHU-3F-01', manufacturer: 'Johnson Controls', model: 'York', ahuType: 'CAV', status: 'standby', supplyTemp: 15.0, returnTemp: 24.0, airflow: 0, fanSpeed: 0, staticPressure: 0, filterStatus: 'Clean', co2Level: 400, load: 0, energyToday: 0, energyMonth: 0, location: 'Executive 3F', alarms: [] },
  { id: '6', name: 'AHU-RF-01', manufacturer: 'Carrier', model: 'WeatherMaker', ahuType: 'VAV', status: 'maintenance', supplyTemp: 16.5, returnTemp: 25.5, airflow: 0, fanSpeed: 0, staticPressure: 0, filterStatus: 'Dirty', co2Level: 450, load: 0, energyToday: 0, energyMonth: 0, location: 'Roof', alarms: [{ timestamp: '2026-06-01 10:00:00', severity: 'critical', code: 'E-301', message: 'Filter clogged', status: 'active' }] }
])

const runningCount = computed(() => ahus.value.filter(a => a.status === 'running').length)
const totalAirflow = computed(() => ahus.value.reduce((sum, a) => sum + a.airflow, 0))
const avgEfficiency = 76.5

const paginatedTableData = computed(() => {
  const start = (pageInfo.pageNum - 1) * pageInfo.pageSize
  return ahus.value.slice(start, start + pageInfo.pageSize)
})

const pageInfo = reactive({
  pageNum: 1,
  pageSize: 10,
  total: ahus.value.length
})

const getLoadColor = (load: number) => {
  if (load < 30) return '#67c23a'
  if (load < 70) return '#409eff'
  return '#e6a23c'
}

// 生成温度趋势数据
const generateTempData = (ahuId: string) => {
  const ahu = ahus.value.find(a => a.id === ahuId)
  if (!ahu) return { timestamps: [], supplyTemp: [], returnTemp: [] }

  const timestamps = []
  const supplyTemp = []
  const returnTemp = []
  const now = new Date()

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    timestamps.push(`${String(time.getHours()).padStart(2, '0')}:00`)

    const supplyVar = ahu.supplyTemp + Math.sin(i * 0.3) * 1.2 + (Math.random() - 0.5) * 0.5
    const returnVar = ahu.returnTemp + Math.sin(i * 0.3) * 1.5 + (Math.random() - 0.5) * 0.6

    supplyTemp.push(Number(supplyVar.toFixed(1)))
    returnTemp.push(Number(returnVar.toFixed(1)))
  }

  return { timestamps, supplyTemp, returnTemp }
}

// 生成风量趋势数据
const generateAirflowData = () => {
  const timestamps = []
  const supplyAirflow = []
  const returnAirflow = []
  const now = new Date()

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    timestamps.push(`${String(time.getHours()).padStart(2, '0')}:00`)

    const supplyVar = 12000 + Math.sin(i * 0.3) * 2000 + (Math.random() - 0.5) * 500
    const returnVar = 11800 + Math.sin(i * 0.3) * 1800 + (Math.random() - 0.5) * 450

    supplyAirflow.push(Math.max(0, Number(supplyVar.toFixed(0))))
    returnAirflow.push(Math.max(0, Number(returnVar.toFixed(0))))
  }

  return { timestamps, supplyAirflow, returnAirflow }
}

// 初始化温度图表
const initTempChart = async () => {
  await nextTick()
  if (!tempChartRef.value) {
    setTimeout(() => initTempChart(), 100)
    return
  }

  if (tempChart) tempChart.dispose()

  if (ahus.value.length > 0 && !trendAHUId.value) {
    trendAHUId.value = ahus.value[0].id
  }

  tempChart = echarts.init(tempChartRef.value)
  updateTempChart()
}

const updateTempChart = () => {
  if (!tempChart || !trendAHUId.value) return

  const data = generateTempData(trendAHUId.value)

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Supply Temp (°C)', 'Return Temp (°C)'], bottom: 0 },
    grid: { top: 30, right: 20, bottom: 40, left: 50, containLabel: true },
    xAxis: { type: 'category', data: data.timestamps, axisLabel: { rotate: 45, interval: 4, fontSize: 10 } },
    yAxis: { type: 'value', name: 'Temperature (°C)' },
    series: [
      { name: 'Supply Temp (°C)', type: 'line', data: data.supplyTemp, smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Return Temp (°C)', type: 'line', data: data.returnTemp, smooth: true, lineStyle: { color: '#f56c6c', width: 2 }, areaStyle: { opacity: 0.1 } }
    ]
  }
  tempChart.setOption(option, true)
}

// 初始化风量图表
const initAirflowChart = async () => {
  await nextTick()
  if (!airflowChartRef.value) {
    setTimeout(() => initAirflowChart(), 100)
    return
  }

  if (airflowChart) airflowChart.dispose()
  airflowChart = echarts.init(airflowChartRef.value)

  const data = generateAirflowData()

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Supply Airflow (m³/h)', 'Return Airflow (m³/h)'], bottom: 0 },
    grid: { top: 30, right: 20, bottom: 40, left: 50, containLabel: true },
    xAxis: { type: 'category', data: data.timestamps, axisLabel: { rotate: 45, interval: 4, fontSize: 10 } },
    yAxis: { type: 'value', name: 'Airflow (m³/h)' },
    series: [
      { name: 'Supply Airflow (m³/h)', type: 'line', data: data.supplyAirflow, smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Return Airflow (m³/h)', type: 'line', data: data.returnAirflow, smooth: true, lineStyle: { color: '#67c23a', width: 2 }, areaStyle: { opacity: 0.1 } }
    ]
  }
  airflowChart.setOption(option)
}

const updateAirflowChart = () => {
  if (!airflowChart) return
  const data = generateAirflowData()
  airflowChart.setOption({
    xAxis: { data: data.timestamps },
    series: [{ data: data.supplyAirflow }, { data: data.returnAirflow }]
  })
}

// 生成单个AHU趋势数据
const generateAHUTrendData = (ahu: AHU) => {
  const timestamps = []
  const supplyTemp = []
  const fanSpeed = []
  const now = new Date()

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    timestamps.push(`${String(time.getHours()).padStart(2, '0')}:00`)

    const tempVar = ahu.supplyTemp + Math.sin(i * 0.3) * 1.2 + (Math.random() - 0.5) * 0.4
    const speedVar = ahu.fanSpeed + Math.sin(i * 0.3) * 8 + (Math.random() - 0.5) * 3

    supplyTemp.push(Number(tempVar.toFixed(1)))
    fanSpeed.push(Math.min(100, Math.max(0, Number(speedVar.toFixed(0)))))
  }

  return { timestamps, supplyTemp, fanSpeed }
}

// 初始化详情图表
const initDetailChart = () => {
  if (!detailChartRef.value || !selectedAHU.value) return
  if (detailChart) detailChart.dispose()

  detailChart = echarts.init(detailChartRef.value)
  const data = generateAHUTrendData(selectedAHU.value)

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
  for (const ahu of ahus.value) {
    if (ahu.status === 'running') {
      const tempChange = (Math.random() - 0.5) * 0.3
      ahu.supplyTemp = Number((ahu.supplyTemp + tempChange).toFixed(1))
      ahu.returnTemp = Number((ahu.returnTemp + tempChange * 0.8).toFixed(1))

      const speedChange = (Math.random() - 0.5) * 2
      ahu.fanSpeed = Math.min(100, Math.max(30, ahu.fanSpeed + speedChange))
      ahu.fanSpeed = Number(ahu.fanSpeed.toFixed(0))

      ahu.load = ahu.fanSpeed
      ahu.airflow = Math.floor(ahu.airflow + (Math.random() - 0.5) * 100)
      ahu.energyToday += ahu.load * 0.25
      ahu.energyMonth += ahu.load * 0.25
    }
  }
}

// 刷新图表
const updateCharts = () => {
  updateTempChart()
  updateAirflowChart()
}

// 窗口大小适配
const handleResize = () => {
  if (tempChart) tempChart.resize()
  if (airflowChart) airflowChart.resize()
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

const selectAHU = (ahu: AHU) => {
  selectedAHU.value = ahu
  detailDrawerVisible.value = true
  setTimeout(() => initDetailChart(), 100)
}

const viewDetail = (ahu: AHU) => {
  selectAHU(ahu)
}

const controlAHU = (ahu: AHU) => {
  selectedAHU.value = ahu
  controlForm.tempSetpoint = ahu.supplyTemp + 1
  controlForm.fanSpeed = ahu.fanSpeed
  controlDialogVisible.value = true
}

const sendCommand = (command: string) => {
  ElMessage.success(`${command.toUpperCase()} command sent to ${selectedAHU.value.name}`)
  if (command === 'start') {
    selectedAHU.value.status = 'running'
    selectedAHU.value.fanSpeed = 40
    selectedAHU.value.load = 40
    selectedAHU.value.airflow = 8000
  } else if (command === 'stop') {
    selectedAHU.value.status = 'standby'
    selectedAHU.value.fanSpeed = 0
    selectedAHU.value.load = 0
    selectedAHU.value.airflow = 0
  }
  controlDialogVisible.value = false
  updateCharts()
}

const showAlarms = (ahu: AHU) => {
  selectedAHU.value = ahu
  alarmDialogVisible.value = true
}

const viewAlarms = (ahu: AHU) => {
  showAlarms(ahu)
}

const exportAHUData = (ahu: AHU) => {
  ElMessage.success(`Exporting data for ${ahu.name}`)
}

const exportReport = () => {
  ElMessage.success('Exporting AHU report')
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
        initAirflowChart()
        startAutoRefresh()
        window.addEventListener('resize', handleResize)
      }, 200)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
  if (tempChart) tempChart.dispose()
  if (airflowChart) airflowChart.dispose()
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
.ahu-container { padding: 20px; background: #f5f7fa; min-height: 100%; }

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

/* AHU Visualization */
.ahu-visualization { background: white; border-radius: 20px; padding: 20px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.ahu-title { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.ahu-title h3 { display: flex; align-items: center; gap: 8px; margin: 0; font-size: 18px; }
.ahu-legend { display: flex; gap: 20px; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 6px; }
.legend-dot.running { background: #67c23a; box-shadow: 0 0 4px #67c23a; }
.legend-dot.standby { background: #409eff; }
.legend-dot.maintenance { background: #e6a23c; }
.legend-dot.offline { background: #f56c6c; }

.ahu-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; }
.ahu-unit { background: #f8fafc; border-radius: 16px; padding: 16px; cursor: pointer; transition: all 0.3s ease; border-left: 4px solid; }
.ahu-unit.running { border-left-color: #67c23a; background: linear-gradient(135deg, #f8fafc, #f0fdf4); }
.ahu-unit.standby { border-left-color: #409eff; }
.ahu-unit.maintenance { border-left-color: #e6a23c; background: linear-gradient(135deg, #f8fafc, #fefce8); }
.ahu-unit.offline { border-left-color: #f56c6c; background: linear-gradient(135deg, #f8fafc, #fef2f2); opacity: 0.8; }
.ahu-unit:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); }

.ahu-image { position: relative; display: flex; justify-content: center; margin-bottom: 12px; }
.ahu-img { width: 100px; height: 100px; object-fit: contain; }
.status-badge { position: absolute; top: 0; right: 0; width: 12px; height: 12px; border-radius: 50%; }
.status-badge.running { background: #67c23a; box-shadow: 0 0 8px #67c23a; animation: pulse 2s infinite; }
.status-badge.standby { background: #409eff; }
.status-badge.maintenance { background: #e6a23c; }
.status-badge.offline { background: #f56c6c; }

.ahu-info { text-align: center; margin-bottom: 12px; }
.ahu-name { margin: 0 0 4px 0; font-size: 16px; font-weight: 600; color: #1e293b; }
.ahu-location { margin: 0; font-size: 11px; color: #64748b; display: flex; align-items: center; justify-content: center; gap: 4px; }
.ahu-model { margin: 4px 0 0 0; font-size: 11px; color: #94a3b8; }

.ahu-metrics { display: flex; justify-content: space-around; margin-bottom: 12px; padding: 8px 0; border-top: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; }
.metric { text-align: center; }
.metric-label { display: block; font-size: 10px; color: #64748b; }
.metric-value { font-size: 14px; font-weight: 600; color: #1e293b; }

.ahu-footer { margin-top: 8px; }
.ahu-actions { display: flex; justify-content: center; gap: 8px; margin-top: 8px; }

/* Charts Section */
.charts-section { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }
.chart-card { border-radius: 16px; }
.card-header-title { display: flex; justify-content: space-between; align-items: center; font-weight: 600; color: #1e293b; font-size: 16px; flex-wrap: wrap; gap: 12px; }
.temp-chart, .airflow-chart { width: 100%; height: 320px; }

/* Status Cell */
.status-cell { display: flex; align-items: center; gap: 6px; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; }
.status-dot.running { background: #67c23a; box-shadow: 0 0 4px #67c23a; animation: pulse 2s infinite; }
.status-dot.standby { background: #409eff; }
.status-dot.maintenance { background: #e6a23c; }
.status-dot.offline { background: #f56c6c; }

/* Drawer Styles */
.ahu-detail { padding: 8px; }
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
  .ahu-container { padding: 12px; }
  .plant-overview { grid-template-columns: 1fr; }
  .ahu-grid { grid-template-columns: 1fr; }
  .ahu-title { flex-direction: column; align-items: flex-start; }
  .metric-row { flex-wrap: wrap; }
  .temp-chart, .airflow-chart { height: 250px; }
}
</style>