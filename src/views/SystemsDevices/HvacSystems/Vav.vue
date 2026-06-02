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
        <div class="loading-tip">VAV SYSTEMS</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Page Content -->
  <div v-else class="vav-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/systems-devices/device-inventory' }">
            Systems & Devices
          </el-breadcrumb-item>
          <el-breadcrumb-item>HVAC Systems</el-breadcrumb-item>
          <el-breadcrumb-item>VAV Boxes</el-breadcrumb-item>
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
          <span class="overview-value">{{ vavs.length }}</span>
          <span class="overview-label">Total VAVs</span>
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
          <span class="overview-value">{{ avgDamperPosition.toFixed(0) }}</span>
          <span class="overview-label">Avg Damper (%)</span>
        </div>
      </div>
    </div>

    <!-- VAV Visualization Grid -->
    <div class="vav-visualization">
      <div class="vav-title">
        <h3><el-icon><OfficeBuilding /></el-icon> VAV Systems - Overview</h3>
        <div class="vav-legend">
          <span><span class="legend-dot running"></span> Running</span>
          <span><span class="legend-dot standby"></span> Standby</span>
          <span><span class="legend-dot maintenance"></span> Maintenance</span>
          <span><span class="legend-dot offline"></span> Offline</span>
        </div>
      </div>

      <div class="vav-grid">
        <div v-for="vav in vavs" :key="vav.id" class="vav-unit" :class="vav.status" @click="selectVAV(vav)">
          <div class="vav-image">
            <img :src="vavImages[vav.status]" :alt="vav.name" class="vav-img" @error="handleImageError">
            <div class="status-badge" :class="vav.status"></div>
          </div>
          <div class="vav-info">
            <h4 class="vav-name">{{ vav.name }}</h4>
            <p class="vav-location"><el-icon><Location /></el-icon> {{ vav.location }}</p>
            <p class="vav-model">{{ vav.manufacturer }} {{ vav.model }}</p>
          </div>
          <div class="vav-metrics">
            <div class="metric">
              <span class="metric-label">Airflow</span>
              <span class="metric-value">{{ vav.airflow }} m³/h</span>
            </div>
            <div class="metric">
              <span class="metric-label">Damper</span>
              <span class="metric-value">{{ vav.damperPosition }}%</span>
            </div>
            <div class="metric">
              <span class="metric-label">Zone Temp</span>
              <span class="metric-value">{{ vav.zoneTemp }}°C</span>
            </div>
          </div>
          <div class="vav-footer">
            <el-progress :percentage="vav.load" :stroke-width="6" :color="getLoadColor(vav.load)" :show-text="false" />
            <div class="vav-actions">
              <el-button size="small" text @click.stop="viewDetail(vav)">Details</el-button>
              <el-button size="small" text type="primary" @click.stop="controlVAV(vav)">Control</el-button>
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
            <span><el-icon><TrendCharts /></el-icon> Airflow & Damper Trend</span>
            <el-select v-model="trendVAVId" placeholder="Select VAV" size="small" style="width: 180px" filterable @change="updateAirflowChart">
              <el-option v-for="vav in vavs" :key="vav.id" :label="vav.name" :value="vav.id" />
            </el-select>
          </div>
        </template>
        <div ref="airflowChartRef" class="airflow-chart"></div>
      </el-card>

      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header-title">
            <span><el-icon><DataAnalysis /></el-icon> Zone Temperature Distribution</span>
          </div>
        </template>
        <div ref="tempDistChartRef" class="temp-dist-chart"></div>
      </el-card>
    </div>

    <!-- VAV List -->
    <el-card shadow="hover">
      <template #header>
        <div class="card-header-title">VAV Boxes List</div>
      </template>
      <el-table :data="paginatedTableData" border stripe height="350" v-loading="tableLoading">
        <el-table-column label="Name" prop="name"  />
        <el-table-column label="Manufacturer" prop="manufacturer"  />
        <el-table-column label="Model" prop="model"  />
        <el-table-column label="Type" prop="vavType" >
          <template #default="scope">
            <el-tag size="small">{{ scope.row.vavType }}</el-tag>
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
        <el-table-column label="Airflow" prop="airflow" width="110">
          <template #default="scope">{{ scope.row.airflow }} m³/h</template>
        </el-table-column>
        <el-table-column label="Damper" prop="damperPosition" >
          <template #default="scope">
            <el-progress :percentage="scope.row.damperPosition" :stroke-width="6" :color="getLoadColor(scope.row.damperPosition)" :show-text="false" style="width: 80px" />
            <span style="margin-left: 8px">{{ scope.row.damperPosition }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="Zone Temp" prop="zoneTemp" >
          <template #default="scope">{{ scope.row.zoneTemp }}°C</template>
        </el-table-column>
        <el-table-column label="Setpoint" prop="setpoint" >
          <template #default="scope">{{ scope.row.setpoint }}°C</template>
        </el-table-column>
        <el-table-column label="Reheat Valve" prop="reheatValve" width="110">
          <template #default="scope">{{ scope.row.reheatValve }}%</template>
        </el-table-column>
        <el-table-column label="Heating" prop="heatingActive" >
          <template #default="scope">
            <el-tag :type="scope.row.heatingActive ? 'warning' : 'info'" size="small">{{ scope.row.heatingActive ? 'Active' : 'Off' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Operation" width="160" fixed="right">
          <template #default="scope">
            <el-button text type="primary" size="small" @click="viewDetail(scope.row)">Detail</el-button>
            <el-button text type="warning" size="small" @click="controlVAV(scope.row)">Control</el-button>
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

    <!-- VAV Details Drawer -->
    <el-drawer v-model="detailDrawerVisible" :title="selectedVAV?.name" size="40%" direction="rtl">
      <div v-if="selectedVAV" class="vav-detail">
        <div class="detail-header">
          <div class="detail-status" :class="selectedVAV.status">
            <span class="status-dot-large"></span>
            <span>{{ selectedVAV.status.toUpperCase() }}</span>
          </div>
          <h2>{{ selectedVAV.name }}</h2>
          <p>{{ selectedVAV.manufacturer }} {{ selectedVAV.model }}</p>
        </div>

        <el-divider />

        <div class="detail-metrics">
          <div class="metric-row">
            <div class="metric-card">
              <span class="metric-label">Airflow</span>
              <span class="metric-value">{{ selectedVAV.airflow }} <span class="metric-unit">m³/h</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Damper Position</span>
              <span class="metric-value">{{ selectedVAV.damperPosition }}<span class="metric-unit">%</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Static Pressure</span>
              <span class="metric-value">{{ selectedVAV.staticPressure }}<span class="metric-unit">Pa</span></span>
            </div>
          </div>
          <div class="metric-row">
            <div class="metric-card">
              <span class="metric-label">Zone Temp</span>
              <span class="metric-value">{{ selectedVAV.zoneTemp }}<span class="metric-unit">°C</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Setpoint</span>
              <span class="metric-value">{{ selectedVAV.setpoint }}<span class="metric-unit">°C</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Delta T</span>
              <span class="metric-value">{{ Math.abs(selectedVAV.zoneTemp - selectedVAV.setpoint).toFixed(1) }}<span class="metric-unit">°C</span></span>
            </div>
          </div>
          <div class="metric-row">
            <div class="metric-card">
              <span class="metric-label">Reheat Valve</span>
              <span class="metric-value">{{ selectedVAV.reheatValve }}<span class="metric-unit">%</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Heating Active</span>
              <span class="metric-value">{{ selectedVAV.heatingActive ? 'Yes' : 'No' }}</span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Cooling Active</span>
              <span class="metric-value">{{ selectedVAV.coolingActive ? 'Yes' : 'No' }}</span>
            </div>
          </div>
          <div class="metric-row">
            <div class="metric-card">
              <span class="metric-label">Min Airflow</span>
              <span class="metric-value">{{ selectedVAV.minAirflow }} <span class="metric-unit">m³/h</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Max Airflow</span>
              <span class="metric-value">{{ selectedVAV.maxAirflow }} <span class="metric-unit">m³/h</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Energy Today</span>
              <span class="metric-value">{{ selectedVAV.energyToday.toLocaleString() }}<span class="metric-unit">kWh</span></span>
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
          <el-button type="primary" @click="controlVAV(selectedVAV)">Control VAV</el-button>
          <el-button @click="viewAlarms(selectedVAV)">View Alarms</el-button>
          <el-button @click="exportVAVData(selectedVAV)">Export Data</el-button>
        </div>
      </div>
    </el-drawer>

    <!-- Control Dialog -->
    <el-dialog v-model="controlDialogVisible" :title="`Control - ${selectedVAV?.name}`" width="450px">
      <el-form :model="controlForm" label-width="120px">
        <el-form-item label="Operation Mode">
          <el-radio-group v-model="controlForm.mode">
            <el-radio label="auto">Auto</el-radio>
            <el-radio label="manual">Manual</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Zone Temp Setpoint">
          <el-input-number v-model="controlForm.setpoint" :min="18" :max="26" :step="0.5" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Damper Position">
          <el-slider v-model="controlForm.damperPosition" :min="0" :max="100" :step="5" />
        </el-form-item>
        <el-form-item label="Commands">
          <el-button-group>
            <el-button type="success" @click="sendCommand('start')" :disabled="selectedVAV?.status === 'running'">Start</el-button>
            <el-button type="warning" @click="sendCommand('stop')" :disabled="selectedVAV?.status !== 'running'">Stop</el-button>
            <el-button type="primary" @click="sendCommand('reset')">Reset</el-button>
          </el-button-group>
        </el-form-item>
      </el-form>
    </el-dialog>

    <!-- Alarms Dialog -->
    <el-dialog v-model="alarmDialogVisible" :title="`Alarms - ${selectedVAV?.name}`" width="600px">
      <el-table :data="selectedVAV?.alarms || []" stripe border>
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
const loadingMessage = ref('Loading VAV systems...')
const loadingMessages = [
  'Initializing VAV systems...',
  'Loading unit data...',
  'Connecting to controllers...',
  'Rendering system layout...',
  'Almost ready...'
]

// ========== Chart References ==========
const airflowChartRef = ref<HTMLDivElement | null>(null)
const tempDistChartRef = ref<HTMLDivElement | null>(null)
const detailChartRef = ref<HTMLDivElement | null>(null)
let airflowChart: echarts.ECharts | null = null
let tempDistChart: echarts.ECharts | null = null
let detailChart: echarts.ECharts | null = null
let refreshTimer: number | null = null
const refreshing = ref(false)
const tableLoading = ref(false)
const trendVAVId = ref('')

// ========== VAV Images ==========
const vavImages = {
  running: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314643.webp',
  standby: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314643.webp',
  maintenance: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314643.webp',
  offline: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314643.webp',
  default: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314643.webp'
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  if (vavImages.default) {
    img.src = vavImages.default
  }
}

// ========== Dialog State ==========
const detailDrawerVisible = ref(false)
const controlDialogVisible = ref(false)
const alarmDialogVisible = ref(false)
const selectedVAV = ref<any>(null)
const controlForm = reactive({
  mode: 'auto',
  setpoint: 22,
  damperPosition: 60
})

// ========== VAV Data ==========
interface VAV {
  id: string
  name: string
  manufacturer: string
  model: string
  vavType: string
  status: 'running' | 'standby' | 'maintenance' | 'offline'
  airflow: number
  damperPosition: number
  staticPressure: number
  zoneTemp: number
  setpoint: number
  reheatValve: number
  heatingActive: boolean
  coolingActive: boolean
  minAirflow: number
  maxAirflow: number
  load: number
  energyToday: number
  energyMonth: number
  location: string
  alarms: any[]
}

const vavs = ref<VAV[]>([
  { id: '1', name: 'VAV-B2-01', manufacturer: 'Johnson Controls', model: 'VAV-100', vavType: 'Single Duct', status: 'running', airflow: 850, damperPosition: 68, staticPressure: 320, zoneTemp: 22.5, setpoint: 22.0, reheatValve: 0, heatingActive: false, coolingActive: true, minAirflow: 200, maxAirflow: 1200, load: 68, energyToday: 85, energyMonth: 2550, location: 'Basement B2', alarms: [] },
  { id: '2', name: 'VAV-B2-02', manufacturer: 'Johnson Controls', model: 'VAV-100', vavType: 'Single Duct', status: 'running', airflow: 780, damperPosition: 62, staticPressure: 305, zoneTemp: 22.8, setpoint: 22.0, reheatValve: 0, heatingActive: false, coolingActive: true, minAirflow: 200, maxAirflow: 1200, load: 62, energyToday: 78, energyMonth: 2340, location: 'Basement B2', alarms: [] },
  { id: '3', name: 'VAV-1F-01', manufacturer: 'Trane', model: 'VAV-200', vavType: 'Single Duct', status: 'running', airflow: 1250, damperPosition: 75, staticPressure: 380, zoneTemp: 23.2, setpoint: 22.5, reheatValve: 0, heatingActive: false, coolingActive: true, minAirflow: 300, maxAirflow: 1800, load: 75, energyToday: 125, energyMonth: 3750, location: 'Lobby 1F', alarms: [] },
  { id: '4', name: 'VAV-1F-02', manufacturer: 'Trane', model: 'VAV-200', vavType: 'Single Duct', status: 'running', airflow: 1180, damperPosition: 72, staticPressure: 365, zoneTemp: 23.0, setpoint: 22.5, reheatValve: 0, heatingActive: false, coolingActive: true, minAirflow: 300, maxAirflow: 1800, load: 72, energyToday: 118, energyMonth: 3540, location: 'Lobby 1F', alarms: [] },
  { id: '5', name: 'VAV-2F-01', manufacturer: 'Siemens', model: 'VAV-150', vavType: 'Single Duct', status: 'running', airflow: 620, damperPosition: 55, staticPressure: 285, zoneTemp: 22.2, setpoint: 22.0, reheatValve: 0, heatingActive: false, coolingActive: true, minAirflow: 150, maxAirflow: 1000, load: 55, energyToday: 62, energyMonth: 1860, location: 'Office 2F', alarms: [] },
  { id: '6', name: 'VAV-2F-02', manufacturer: 'Siemens', model: 'VAV-150', vavType: 'Single Duct', status: 'standby', airflow: 0, damperPosition: 0, staticPressure: 0, zoneTemp: 23.5, setpoint: 22.0, reheatValve: 0, heatingActive: false, coolingActive: false, minAirflow: 150, maxAirflow: 1000, load: 0, energyToday: 0, energyMonth: 0, location: 'Office 2F', alarms: [] },
  { id: '7', name: 'VAV-3F-01', manufacturer: 'Johnson Controls', model: 'VAV-150', vavType: 'Single Duct', status: 'running', airflow: 580, damperPosition: 52, staticPressure: 278, zoneTemp: 21.8, setpoint: 22.0, reheatValve: 25, heatingActive: true, coolingActive: false, minAirflow: 150, maxAirflow: 1000, load: 52, energyToday: 58, energyMonth: 1740, location: 'Executive 3F', alarms: [] },
  { id: '8', name: 'VAV-3F-02', manufacturer: 'Johnson Controls', model: 'VAV-150', vavType: 'Single Duct', status: 'maintenance', airflow: 0, damperPosition: 0, staticPressure: 0, zoneTemp: 24.5, setpoint: 22.0, reheatValve: 0, heatingActive: false, coolingActive: false, minAirflow: 150, maxAirflow: 1000, load: 0, energyToday: 0, energyMonth: 0, location: 'Executive 3F', alarms: [{ timestamp: '2026-06-01 13:00:00', severity: 'critical', code: 'E-501', message: 'Damper actuator failure', status: 'active' }] }
])

const runningCount = computed(() => vavs.value.filter(v => v.status === 'running').length)
const runningPercent = computed(() => vavs.value.length ? Math.round(runningCount.value / vavs.value.length * 100) : 0)
const totalAirflow = computed(() => vavs.value.reduce((sum, v) => sum + v.airflow, 0))
const avgDamperPosition = computed(() => {
  const running = vavs.value.filter(v => v.status === 'running')
  if (running.length === 0) return 0
  return running.reduce((sum, v) => sum + v.damperPosition, 0) / running.length
})

const paginatedTableData = computed(() => {
  const start = (pageInfo.pageNum - 1) * pageInfo.pageSize
  return vavs.value.slice(start, start + pageInfo.pageSize)
})

const pageInfo = reactive({
  pageNum: 1,
  pageSize: 10,
  total: vavs.value.length
})

const getLoadColor = (load: number) => {
  if (load < 30) return '#67c23a'
  if (load < 70) return '#409eff'
  return '#e6a23c'
}

// 生成风量和风阀趋势数据
const generateAirflowData = (vavId: string) => {
  const vav = vavs.value.find(v => v.id === vavId)
  if (!vav) return { timestamps: [], airflow: [], damper: [] }

  const timestamps = []
  const airflow = []
  const damper = []
  const now = new Date()

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    timestamps.push(`${String(time.getHours()).padStart(2, '0')}:00`)

    const airflowVar = vav.airflow + Math.sin(i * 0.3) * (vav.airflow * 0.15) + (Math.random() - 0.5) * 50
    const damperVar = vav.damperPosition + Math.sin(i * 0.3) * 8 + (Math.random() - 0.5) * 4

    airflow.push(Math.max(0, Number(airflowVar.toFixed(0))))
    damper.push(Math.min(100, Math.max(0, Number(damperVar.toFixed(0)))))
  }

  return { timestamps, airflow, damper }
}

// 生成区域温度分布数据（用于饼图/条形图）
const generateZoneTempData = () => {
  const ranges = [
    { name: '< 20°C', value: vavs.value.filter(v => v.zoneTemp < 20 && v.status === 'running').length },
    { name: '20-22°C', value: vavs.value.filter(v => v.zoneTemp >= 20 && v.zoneTemp < 22 && v.status === 'running').length },
    { name: '22-24°C', value: vavs.value.filter(v => v.zoneTemp >= 22 && v.zoneTemp < 24 && v.status === 'running').length },
    { name: '24-26°C', value: vavs.value.filter(v => v.zoneTemp >= 24 && v.zoneTemp < 26 && v.status === 'running').length },
    { name: '≥ 26°C', value: vavs.value.filter(v => v.zoneTemp >= 26 && v.status === 'running').length }
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

  if (vavs.value.length > 0 && !trendVAVId.value) {
    trendVAVId.value = vavs.value[0].id
  }

  airflowChart = echarts.init(airflowChartRef.value)
  updateAirflowChart()
}

const updateAirflowChart = () => {
  if (!airflowChart || !trendVAVId.value) return

  const data = generateAirflowData(trendVAVId.value)

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Airflow (m³/h)', 'Damper Position (%)'], bottom: 0 },
    grid: { top: 30, right: 20, bottom: 40, left: 50, containLabel: true },
    xAxis: { type: 'category', data: data.timestamps, axisLabel: { rotate: 45, interval: 4, fontSize: 10 } },
    yAxis: [
      { type: 'value', name: 'Airflow (m³/h)', position: 'left' },
      { type: 'value', name: 'Damper Position (%)', position: 'right', min: 0, max: 100 }
    ],
    series: [
      { name: 'Airflow (m³/h)', type: 'line', data: data.airflow, smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Damper Position (%)', type: 'line', yAxisIndex: 1, data: data.damper, smooth: true, lineStyle: { color: '#e6a23c', width: 2 }, areaStyle: { opacity: 0.1 } }
    ]
  }
  airflowChart.setOption(option, true)
}

// 初始化区域温度分布图表（饼图）
const initTempDistChart = async () => {
  await nextTick()
  if (!tempDistChartRef.value) {
    setTimeout(() => initTempDistChart(), 100)
    return
  }

  if (tempDistChart) tempDistChart.dispose()
  tempDistChart = echarts.init(tempDistChartRef.value)

  const data = generateZoneTempData()

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
  tempDistChart.setOption(option)
}

const updateTempDistChart = () => {
  if (!tempDistChart) return
  const data = generateZoneTempData()
  tempDistChart.setOption({
    series: [{ data: data }],
    legend: { data: data.map(d => d.name) }
  })
}

// 生成单个VAV趋势数据
const generateVAVTrendData = (vav: VAV) => {
  const timestamps = []
  const airflow = []
  const damper = []
  const now = new Date()

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    timestamps.push(`${String(time.getHours()).padStart(2, '0')}:00`)

    const airflowVar = vav.airflow + Math.sin(i * 0.3) * (vav.airflow * 0.12) + (Math.random() - 0.5) * 40
    const damperVar = vav.damperPosition + Math.sin(i * 0.3) * 6 + (Math.random() - 0.5) * 3

    airflow.push(Math.max(0, Number(airflowVar.toFixed(0))))
    damper.push(Math.min(100, Math.max(0, Number(damperVar.toFixed(0)))))
  }

  return { timestamps, airflow, damper }
}

// 初始化详情图表
const initDetailChart = () => {
  if (!detailChartRef.value || !selectedVAV.value) return
  if (detailChart) detailChart.dispose()

  detailChart = echarts.init(detailChartRef.value)
  const data = generateVAVTrendData(selectedVAV.value)

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Airflow (m³/h)', 'Damper Position (%)'], bottom: 0 },
    grid: { top: 30, right: 20, bottom: 40, left: 50, containLabel: true },
    xAxis: { type: 'category', data: data.timestamps, axisLabel: { rotate: 45, interval: 4, fontSize: 10 } },
    yAxis: [
      { type: 'value', name: 'Airflow (m³/h)', position: 'left' },
      { type: 'value', name: 'Damper Position (%)', position: 'right', min: 0, max: 100 }
    ],
    series: [
      { name: 'Airflow (m³/h)', type: 'line', data: data.airflow, smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Damper Position (%)', type: 'line', yAxisIndex: 1, data: data.damper, smooth: true, lineStyle: { color: '#e6a23c', width: 2 } }
    ]
  }
  detailChart.setOption(option)
}

// 更新实时数据
const updateRealtimeData = () => {
  for (const vav of vavs.value) {
    if (vav.status === 'running') {
      const airflowChange = (Math.random() - 0.5) * 40
      let newAirflow = vav.airflow + airflowChange
      newAirflow = Math.max(vav.minAirflow, Math.min(vav.maxAirflow, newAirflow))
      vav.airflow = Number(newAirflow.toFixed(0))

      const damperChange = (Math.random() - 0.5) * 4
      let newDamper = vav.damperPosition + damperChange
      newDamper = Math.min(100, Math.max(0, newDamper))
      vav.damperPosition = Number(newDamper.toFixed(0))

      const tempChange = (Math.random() - 0.5) * 0.3
      vav.zoneTemp = Number((vav.zoneTemp + tempChange).toFixed(1))

      vav.load = vav.damperPosition
      vav.energyToday += vav.load * 0.12
      vav.energyMonth += vav.load * 0.12

      // 控制逻辑：根据温度偏差调节
      const tempDiff = vav.zoneTemp - vav.setpoint
      if (tempDiff > 1.5) {
        vav.coolingActive = true
        vav.heatingActive = false
        vav.reheatValve = 0
      } else if (tempDiff < -1.5) {
        vav.coolingActive = false
        vav.heatingActive = true
        vav.reheatValve = Math.min(100, Math.abs(tempDiff) * 20)
      } else {
        vav.coolingActive = tempDiff > 0.5
        vav.heatingActive = tempDiff < -0.5
        vav.reheatValve = vav.heatingActive ? Math.abs(tempDiff) * 15 : 0
      }
    }
  }
}

// 刷新图表
const updateCharts = () => {
  updateAirflowChart()
  updateTempDistChart()
}

// 窗口大小适配
const handleResize = () => {
  if (airflowChart) airflowChart.resize()
  if (tempDistChart) tempDistChart.resize()
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

const selectVAV = (vav: VAV) => {
  selectedVAV.value = vav
  detailDrawerVisible.value = true
  setTimeout(() => initDetailChart(), 100)
}

const viewDetail = (vav: VAV) => {
  selectVAV(vav)
}

const controlVAV = (vav: VAV) => {
  selectedVAV.value = vav
  controlForm.setpoint = vav.setpoint
  controlForm.damperPosition = vav.damperPosition
  controlDialogVisible.value = true
}

const sendCommand = (command: string) => {
  ElMessage.success(`${command.toUpperCase()} command sent to ${selectedVAV.value.name}`)
  if (command === 'start') {
    selectedVAV.value.status = 'running'
    selectedVAV.value.damperPosition = 30
    selectedVAV.value.airflow = selectedVAV.value.minAirflow + 100
    selectedVAV.value.load = 30
  } else if (command === 'stop') {
    selectedVAV.value.status = 'standby'
    selectedVAV.value.damperPosition = 0
    selectedVAV.value.airflow = 0
    selectedVAV.value.load = 0
  }
  controlDialogVisible.value = false
  updateCharts()
}

const showAlarms = (vav: VAV) => {
  selectedVAV.value = vav
  alarmDialogVisible.value = true
}

const viewAlarms = (vav: VAV) => {
  showAlarms(vav)
}

const exportVAVData = (vav: VAV) => {
  ElMessage.success(`Exporting data for ${vav.name}`)
}

const exportReport = () => {
  ElMessage.success('Exporting VAV report')
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
        initTempDistChart()
        startAutoRefresh()
        window.addEventListener('resize', handleResize)
      }, 200)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
  if (airflowChart) airflowChart.dispose()
  if (tempDistChart) tempDistChart.dispose()
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
.vav-container { padding: 20px; background: #f5f7fa; min-height: 100%; }

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

/* VAV Visualization */
.vav-visualization { background: white; border-radius: 20px; padding: 20px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.vav-title { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.vav-title h3 { display: flex; align-items: center; gap: 8px; margin: 0; font-size: 18px; }
.vav-legend { display: flex; gap: 20px; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 6px; }
.legend-dot.running { background: #67c23a; box-shadow: 0 0 4px #67c23a; }
.legend-dot.standby { background: #409eff; }
.legend-dot.maintenance { background: #e6a23c; }
.legend-dot.offline { background: #f56c6c; }

.vav-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; }
.vav-unit { background: #f8fafc; border-radius: 16px; padding: 16px; cursor: pointer; transition: all 0.3s ease; border-left: 4px solid; }
.vav-unit.running { border-left-color: #67c23a; background: linear-gradient(135deg, #f8fafc, #f0fdf4); }
.vav-unit.standby { border-left-color: #409eff; }
.vav-unit.maintenance { border-left-color: #e6a23c; background: linear-gradient(135deg, #f8fafc, #fefce8); }
.vav-unit.offline { border-left-color: #f56c6c; background: linear-gradient(135deg, #f8fafc, #fef2f2); opacity: 0.8; }
.vav-unit:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); }

.vav-image { position: relative; display: flex; justify-content: center; margin-bottom: 12px; }
.vav-img { width: 100px; height: 100px; object-fit: contain; }
.status-badge { position: absolute; top: 0; right: 0; width: 12px; height: 12px; border-radius: 50%; }
.status-badge.running { background: #67c23a; box-shadow: 0 0 8px #67c23a; animation: pulse 2s infinite; }
.status-badge.standby { background: #409eff; }
.status-badge.maintenance { background: #e6a23c; }
.status-badge.offline { background: #f56c6c; }

.vav-info { text-align: center; margin-bottom: 12px; }
.vav-name { margin: 0 0 4px 0; font-size: 16px; font-weight: 600; color: #1e293b; }
.vav-location { margin: 0; font-size: 11px; color: #64748b; display: flex; align-items: center; justify-content: center; gap: 4px; }
.vav-model { margin: 4px 0 0 0; font-size: 11px; color: #94a3b8; }

.vav-metrics { display: flex; justify-content: space-around; margin-bottom: 12px; padding: 8px 0; border-top: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; }
.metric { text-align: center; }
.metric-label { display: block; font-size: 10px; color: #64748b; }
.metric-value { font-size: 14px; font-weight: 600; color: #1e293b; }

.vav-footer { margin-top: 8px; }
.vav-actions { display: flex; justify-content: center; gap: 8px; margin-top: 8px; }

/* Charts Section */
.charts-section { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }
.chart-card { border-radius: 16px; }
.card-header-title { display: flex; justify-content: space-between; align-items: center; font-weight: 600; color: #1e293b; font-size: 16px; flex-wrap: wrap; gap: 12px; }
.airflow-chart, .temp-dist-chart { width: 100%; height: 320px; }

/* Status Cell */
.status-cell { display: flex; align-items: center; gap: 6px; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; }
.status-dot.running { background: #67c23a; box-shadow: 0 0 4px #67c23a; animation: pulse 2s infinite; }
.status-dot.standby { background: #409eff; }
.status-dot.maintenance { background: #e6a23c; }
.status-dot.offline { background: #f56c6c; }

/* Drawer Styles */
.vav-detail { padding: 8px; }
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
  .vav-container { padding: 12px; }
  .plant-overview { grid-template-columns: 1fr; }
  .vav-grid { grid-template-columns: 1fr; }
  .vav-title { flex-direction: column; align-items: flex-start; }
  .metric-row { flex-wrap: wrap; }
  .airflow-chart, .temp-dist-chart { height: 250px; }
}
</style>