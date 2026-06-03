<template>
  <!-- Loading Screen -->
  <div v-if="!isLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
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
        <div class="loading-tip">Rack Alarms Monitoring</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="rack-alarms-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-left">
        <h1 class="dashboard-title">
          <div class="title-icon rack-icon">
            <el-icon><Grid /></el-icon>
          </div>
          Rack Alarms
        </h1>
        <div class="header-stats">
          <div class="stat-badge">
            <el-icon><Grid /></el-icon>
            {{ totalRacks }} Racks
          </div>
          <div class="stat-badge critical">
            <span class="pulse-dot"></span>
            {{ criticalCount }} Critical
          </div>
          <div class="stat-badge warning">
            {{ warningCount }} Warning
          </div>
        </div>
      </div>
      <div class="header-right">
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
        <el-button type="primary" @click="exportReport">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
      </div>
    </div>

    <!-- Rack Overview Cards -->
    <div class="rack-overview">
      <div class="overview-card temp">
        <div class="overview-card-inner">
          <div class="overview-icon">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="overview-stats">
            <div class="overview-label">Average Inlet Temp</div>
            <div class="overview-value">{{ avgInletTemp }}<span class="unit">°C</span></div>
            <div class="overview-status" :class="getTempStatusClass(avgInletTemp)">
              {{ getTempStatusText(avgInletTemp) }}
            </div>
          </div>
          <div class="overview-gauge">
            <el-progress type="circle" :percentage="tempPercent" :color="getTempColor(avgInletTemp)" :width="70" :stroke-width="6">
              <template #default>{{ avgInletTemp }}°C</template>
            </el-progress>
          </div>
        </div>
      </div>

      <div class="overview-card power">
        <div class="overview-card-inner">
          <div class="overview-icon">
            <el-icon><Lightning /></el-icon>
          </div>
          <div class="overview-stats">
            <div class="overview-label">Total Power Consumption</div>
            <div class="overview-value">{{ totalPower }}<span class="unit">kW</span></div>
            <div class="overview-status normal">{{ powerPercent }}% of capacity</div>
          </div>
          <div class="overview-badge">⚡</div>
        </div>
      </div>

      <div class="overview-card load">
        <div class="overview-card-inner">
          <div class="overview-icon">
            <el-icon><DataLine /></el-icon>
          </div>
          <div class="overview-stats">
            <div class="overview-label">Average Rack Load</div>
            <div class="overview-value">{{ avgLoad }}<span class="unit">kW</span></div>
            <div class="overview-status" :class="getLoadStatusClass(avgLoadPercent)">
              {{ avgLoadPercent }}% utilization
            </div>
          </div>
          <div class="overview-badge">📊</div>
        </div>
      </div>

      <div class="overview-card density">
        <div class="overview-card-inner">
          <div class="overview-icon">
            <el-icon><Histogram /></el-icon>
          </div>
          <div class="overview-stats">
            <div class="overview-label">Power Density</div>
            <div class="overview-value">{{ powerDensity }}<span class="unit">kW/rack</span></div>
            <div class="overview-status normal">Average per rack</div>
          </div>
          <div class="overview-badge">📈</div>
        </div>
      </div>
    </div>

    <!-- Rack Grid -->
    <div class="section-title">
      <span class="title-text">🗄️ Rack Status</span>
      <div class="filter-group">
        <el-select v-model="rowFilter" size="small" placeholder="Filter by row" style="width: 120px" clearable>
          <el-option label="All Rows" value="all" />
          <el-option label="Row A" value="Row A" />
          <el-option label="Row B" value="Row B" />
          <el-option label="Row C" value="Row C" />
          <el-option label="Row D" value="Row D" />
        </el-select>
        <el-select v-model="statusFilter" size="small" placeholder="Status" style="width: 120px" clearable>
          <el-option label="All" value="all" />
          <el-option label="Critical" value="critical" />
          <el-option label="Warning" value="warning" />
          <el-option label="Normal" value="normal" />
        </el-select>
      </div>
    </div>

    <div class="rack-grid">
      <div v-for="rack in filteredRacks" :key="rack.id" class="rack-card" :class="rack.status">
        <div class="rack-header">
          <div class="rack-name">
            <span class="rack-icon">🗄️</span>
            {{ rack.name }}
          </div>
          <div class="rack-status-badge" :class="rack.status">
            <span class="status-dot"></span>
            {{ rack.statusText }}
          </div>
        </div>

        <div class="rack-temp-section">
          <div class="temp-readings">
            <div class="temp-reading">
              <div class="reading-label">Inlet Temp</div>
              <div class="reading-value" :class="getTempWarningClass(rack.inletTemp)">{{ rack.inletTemp }}°C</div>
            </div>
            <div class="temp-reading">
              <div class="reading-label">Outlet Temp</div>
              <div class="reading-value" :class="getTempWarningClass(rack.outletTemp)">{{ rack.outletTemp }}°C</div>
            </div>
            <div class="temp-reading">
              <div class="reading-label">ΔT</div>
              <div class="reading-value" :class="getDeltaWarningClass(rack.deltaT)">{{ rack.deltaT }}°C</div>
            </div>
          </div>
        </div>

        <div class="rack-metrics">
          <div class="metric-bar">
            <div class="metric-bar-label">Power Load</div>
            <div class="metric-bar-track">
              <div class="metric-bar-fill" :style="{ width: rack.loadPercent + '%', background: getLoadColor(rack.loadPercent) }"></div>
            </div>
            <div class="metric-bar-value">{{ rack.currentLoad }} / {{ rack.maxLoad }} kW ({{ rack.loadPercent }}%)</div>
          </div>
          <div class="metric-bar">
            <div class="metric-bar-label">Humidity</div>
            <div class="metric-bar-track">
              <div class="metric-bar-fill" :style="{ width: rack.humidity + '%', background: getHumidityColor(rack.humidity) }"></div>
            </div>
            <div class="metric-bar-value">{{ rack.humidity }}%</div>
          </div>
        </div>

        <div class="rack-footer">
          <div class="footer-info">
            <span>📍 {{ rack.row }}</span>
            <span>🖥️ {{ rack.deviceCount }} devices</span>
            <span>⚠️ {{ rack.alarmCount }} alarms</span>
          </div>
          <el-button type="primary" link size="small" @click="viewRackDetails(rack)">
            Details →
          </el-button>
        </div>
      </div>
    </div>

    <!-- Hot Spots Section -->
    <div class="section-title">
      <span class="title-text">🔥 Hot Spots</span>
      <span class="title-badge warning">{{ hotSpots.length }} Hot Spots</span>
    </div>

    <div class="hotspots-grid">
      <div v-for="spot in hotSpots" :key="spot.id" class="hotspot-card" :class="spot.severity">
        <div class="hotspot-header">
          <div class="hotspot-location">
            <span class="hotspot-icon">🔥</span>
            {{ spot.location }}
          </div>
          <div class="hotspot-temp">{{ spot.temp }}°C</div>
        </div>
        <div class="hotspot-details">
          <div class="detail">{{ spot.device }}</div>
          <div class="detail">Threshold: {{ spot.threshold }}°C</div>
          <div class="detail">Duration: {{ spot.duration }}</div>
        </div>
        <div class="hotspot-actions">
          <el-button size="small" type="primary" plain @click="investigateHotspot(spot)">
            Investigate
          </el-button>
        </div>
      </div>
    </div>

    <!-- Rack Alarms Table -->
    <div class="section-title">
      <span class="title-text">🚨 Rack Alarms</span>
      <span class="title-badge critical">{{ activeAlarmsCount }} Active</span>
    </div>

    <div class="alarms-container">
      <div v-for="alarm in activeAlarms" :key="alarm.id" class="alarm-card" :class="alarm.severity">
        <div class="alarm-icon">
          <span v-if="alarm.severity === 'critical'">🔴</span>
          <span v-else-if="alarm.severity === 'major'">🟠</span>
          <span v-else>🟡</span>
        </div>
        <div class="alarm-content">
          <div class="alarm-title">{{ alarm.title }}</div>
          <div class="alarm-description">{{ alarm.description }}</div>
          <div class="alarm-meta">
            <span>🗄️ {{ alarm.rackName }}</span>
            <span>⏱️ {{ alarm.time }}</span>
            <span>📊 {{ alarm.value }}</span>
          </div>
        </div>
        <div class="alarm-actions">
          <el-button size="small" type="primary" plain @click="acknowledgeAlarm(alarm)">
            Acknowledge
          </el-button>
          <el-button size="small" type="danger" plain @click="escalateAlarm(alarm)">
            Escalate
          </el-button>
        </div>
      </div>
      <div v-if="activeAlarms.length === 0" class="empty-alarms">
        <el-empty description="No active rack alarms" :image-size="80" />
      </div>
    </div>

    <!-- Temperature Trend Chart -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><TrendCharts /></el-icon>
          Temperature Trend (Last 24 Hours)
        </div>
        <el-radio-group v-model="trendPeriod" size="small">
          <el-radio-button label="hour">Hourly</el-radio-button>
          <el-radio-button label="day">Daily</el-radio-button>
        </el-radio-group>
      </div>
      <div ref="trendChartRef" class="chart-container"></div>
    </div>

    <!-- Rack Detail Dialog -->
    <el-dialog v-model="rackDetailVisible" :title="`Rack Details - ${selectedRack?.name}`" width="600px">
      <el-descriptions :column="2" border v-if="selectedRack">
        <el-descriptions-item label="Rack Name">{{ selectedRack.name }}</el-descriptions-item>
        <el-descriptions-item label="Row">{{ selectedRack.row }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusTagType(selectedRack.status)">{{ selectedRack.statusText }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Inlet Temp">{{ selectedRack.inletTemp }}°C</el-descriptions-item>
        <el-descriptions-item label="Outlet Temp">{{ selectedRack.outletTemp }}°C</el-descriptions-item>
        <el-descriptions-item label="Delta T">{{ selectedRack.deltaT }}°C</el-descriptions-item>
        <el-descriptions-item label="Current Load">{{ selectedRack.currentLoad }} kW</el-descriptions-item>
        <el-descriptions-item label="Max Load">{{ selectedRack.maxLoad }} kW</el-descriptions-item>
        <el-descriptions-item label="Load Percentage">{{ selectedRack.loadPercent }}%</el-descriptions-item>
        <el-descriptions-item label="Humidity">{{ selectedRack.humidity }}%</el-descriptions-item>
        <el-descriptions-item label="Device Count">{{ selectedRack.deviceCount }}</el-descriptions-item>
        <el-descriptions-item label="Alarm Count">{{ selectedRack.alarmCount }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Grid, Refresh, Download, CircleClose, Clock, Lightning, DataLine, Histogram, TrendCharts } from '@element-plus/icons-vue'
import { useCounterStore } from '@/stores/counter.js'
import { getCurrentInstance } from 'vue'

const getStore = () => {
  const instance = getCurrentInstance()
  if (!instance) throw new Error('useStore() must be called within a setup function')
  const pinia = instance.appContext.config.globalProperties.$pinia
  if (!pinia) throw new Error('Pinia instance not found')
  return useCounterStore(pinia)
}
const counterStore = getStore()
const isFullscreen = computed(() => counterStore.isFullscreen)
const route = useRoute()

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const refreshing = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading rack data...',
  'Analyzing temperature readings...',
  'Checking alarm status...',
  'Almost ready...'
]

// ==================== Data State ====================
const rowFilter = ref('all')
const statusFilter = ref('all')
const trendPeriod = ref('hour')
const rackDetailVisible = ref(false)
const selectedRack = ref<any>(null)

// Rack Statistics
const totalRacks = ref(48)
const criticalCount = ref(4)
const warningCount = ref(7)
const avgInletTemp = ref(24.5)
const tempPercent = computed(() => Math.min(100, (avgInletTemp.value / 35) * 100))
const totalPower = ref(328)
const powerPercent = ref(65)
const avgLoad = ref(6.8)
const avgLoadPercent = ref(56)
const powerDensity = ref(6.8)

// Racks Data
interface Rack {
  id: number
  name: string
  row: string
  status: string
  statusText: string
  inletTemp: number
  outletTemp: number
  deltaT: number
  currentLoad: number
  maxLoad: number
  loadPercent: number
  humidity: number
  deviceCount: number
  alarmCount: number
}

const racks = ref<Rack[]>([
  { id: 1, name: 'Rack A01', row: 'Row A', status: 'critical', statusText: 'Critical', inletTemp: 28.5, outletTemp: 32.5, deltaT: 4.0, currentLoad: 8.5, maxLoad: 12, loadPercent: 71, humidity: 48, deviceCount: 12, alarmCount: 2 },
  { id: 2, name: 'Rack A02', row: 'Row A', status: 'warning', statusText: 'Warning', inletTemp: 26.8, outletTemp: 31.2, deltaT: 4.4, currentLoad: 7.8, maxLoad: 12, loadPercent: 65, humidity: 52, deviceCount: 10, alarmCount: 1 },
  { id: 3, name: 'Rack A03', row: 'Row A', status: 'normal', statusText: 'Normal', inletTemp: 23.5, outletTemp: 28.5, deltaT: 5.0, currentLoad: 5.2, maxLoad: 12, loadPercent: 43, humidity: 45, deviceCount: 8, alarmCount: 0 },
  { id: 4, name: 'Rack B01', row: 'Row B', status: 'critical', statusText: 'Critical', inletTemp: 29.2, outletTemp: 33.8, deltaT: 4.6, currentLoad: 9.2, maxLoad: 12, loadPercent: 77, humidity: 55, deviceCount: 14, alarmCount: 3 },
  { id: 5, name: 'Rack B02', row: 'Row B', status: 'warning', statusText: 'Warning', inletTemp: 27.2, outletTemp: 31.5, deltaT: 4.3, currentLoad: 7.5, maxLoad: 12, loadPercent: 63, humidity: 50, deviceCount: 11, alarmCount: 1 },
  { id: 6, name: 'Rack B03', row: 'Row B', status: 'normal', statusText: 'Normal', inletTemp: 24.2, outletTemp: 29.2, deltaT: 5.0, currentLoad: 5.8, maxLoad: 12, loadPercent: 48, humidity: 46, deviceCount: 9, alarmCount: 0 },
  { id: 7, name: 'Rack C01', row: 'Row C', status: 'critical', statusText: 'Critical', inletTemp: 27.5, outletTemp: 31.8, deltaT: 4.3, currentLoad: 8.2, maxLoad: 12, loadPercent: 68, humidity: 49, deviceCount: 12, alarmCount: 1 },
  { id: 8, name: 'Rack C02', row: 'Row C', status: 'normal', statusText: 'Normal', inletTemp: 23.8, outletTemp: 28.5, deltaT: 4.7, currentLoad: 5.5, maxLoad: 12, loadPercent: 46, humidity: 44, deviceCount: 8, alarmCount: 0 },
  { id: 9, name: 'Rack C03', row: 'Row C', status: 'normal', statusText: 'Normal', inletTemp: 24.5, outletTemp: 29.5, deltaT: 5.0, currentLoad: 6.2, maxLoad: 12, loadPercent: 52, humidity: 47, deviceCount: 10, alarmCount: 0 },
  { id: 10, name: 'Rack D01', row: 'Row D', status: 'warning', statusText: 'Warning', inletTemp: 26.5, outletTemp: 30.8, deltaT: 4.3, currentLoad: 7.2, maxLoad: 12, loadPercent: 60, humidity: 51, deviceCount: 10, alarmCount: 1 },
  { id: 11, name: 'Rack D02', row: 'Row D', status: 'normal', statusText: 'Normal', inletTemp: 23.2, outletTemp: 28.2, deltaT: 5.0, currentLoad: 5.0, maxLoad: 12, loadPercent: 42, humidity: 43, deviceCount: 7, alarmCount: 0 },
  { id: 12, name: 'Rack D03', row: 'Row D', status: 'normal', statusText: 'Normal', inletTemp: 24.0, outletTemp: 29.0, deltaT: 5.0, currentLoad: 5.6, maxLoad: 12, loadPercent: 47, humidity: 45, deviceCount: 8, alarmCount: 0 }
])

const filteredRacks = computed(() => {
  let filtered = racks.value
  if (rowFilter.value !== 'all') {
    filtered = filtered.filter(r => r.row === rowFilter.value)
  }
  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(r => r.status === statusFilter.value)
  }
  return filtered
})

// Hot Spots
interface HotSpot {
  id: number
  location: string
  device: string
  temp: number
  threshold: number
  duration: string
  severity: string
}

const hotSpots = ref<HotSpot[]>([
  { id: 1, location: 'Rack A01 - Top', device: 'Server-01', temp: 32.5, threshold: 30, duration: '15 min', severity: 'critical' },
  { id: 2, location: 'Rack B01 - Middle', device: 'Storage Array', temp: 31.2, threshold: 30, duration: '8 min', severity: 'critical' },
  { id: 3, location: 'Rack C01 - Bottom', device: 'Network Switch', temp: 29.5, threshold: 28, duration: '22 min', severity: 'warning' },
  { id: 4, location: 'Rack A02 - Top', device: 'Server-05', temp: 28.8, threshold: 28, duration: '10 min', severity: 'warning' }
])

// Active Alarms
interface RackAlarm {
  id: number
  rackName: string
  title: string
  description: string
  severity: string
  value: string
  time: string
}

const activeAlarms = ref<RackAlarm[]>([
  { id: 1, rackName: 'Rack A01', title: 'High Inlet Temperature', description: 'Inlet temperature exceeded 28°C threshold', severity: 'critical', value: '28.5°C', time: '8 min ago' },
  { id: 2, rackName: 'Rack B01', title: 'High Outlet Temperature', description: 'Outlet temperature critical', severity: 'critical', value: '33.8°C', time: '12 min ago' },
  { id: 3, rackName: 'Rack A02', title: 'Power Overload Warning', description: 'Power consumption near capacity', severity: 'warning', value: '7.8 kW / 12 kW', time: '20 min ago' },
  { id: 4, rackName: 'Rack B02', title: 'High Delta T', description: 'Temperature differential below optimal', severity: 'warning', value: '4.3°C', time: '25 min ago' },
  { id: 5, rackName: 'Rack C01', title: 'High Humidity', description: 'Humidity above 50%', severity: 'warning', value: '55%', time: '35 min ago' }
])

const activeAlarmsCount = computed(() => activeAlarms.value.length)

// Trend data
const hourlyTempData = ref<number[]>([23.5, 23.8, 24.2, 24.5, 25.0, 25.5, 26.0, 26.5, 27.0, 27.5, 27.8, 27.5, 27.0, 26.5, 26.0, 25.5, 25.0, 24.8, 24.5, 24.2, 24.0, 23.8, 23.5, 23.2])
const dailyTempData = ref<number[]>([24.2, 24.5, 24.8, 25.2, 25.5, 25.8, 25.2])
const hourLabels = Array.from({ length: 24 }, (_, i) => `${i}:00`)
const dayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

// ==================== Helper Functions ====================
const getTempStatusClass = (temp: number) => {
  if (temp > 27) return 'high'
  if (temp < 18) return 'low'
  return 'normal'
}

const getTempStatusText = (temp: number) => {
  if (temp > 27) return '⚠️ Above ASHRAE'
  if (temp < 18) return '⚠️ Below ASHRAE'
  return '✅ Within Range'
}

const getTempColor = (temp: number) => {
  if (temp <= 27) return '#67c23a'
  if (temp <= 30) return '#e6a23c'
  return '#f56c6c'
}

const getTempWarningClass = (temp: number) => {
  if (temp > 27) return 'warning'
  return ''
}

const getDeltaWarningClass = (delta: number) => {
  if (delta < 5) return 'warning'
  return ''
}

const getLoadStatusClass = (percent: number) => {
  if (percent > 80) return 'high'
  if (percent > 60) return 'medium'
  return 'normal'
}

const getLoadColor = (percent: number) => {
  if (percent <= 60) return '#67c23a'
  if (percent <= 80) return '#e6a23c'
  return '#f56c6c'
}

const getHumidityColor = (humidity: number) => {
  if (humidity >= 40 && humidity <= 60) return '#67c23a'
  return '#e6a23c'
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    critical: 'danger',
    warning: 'warning',
    normal: 'success'
  }
  return map[status] || 'info'
}

const viewRackDetails = (rack: Rack) => {
  selectedRack.value = rack
  rackDetailVisible.value = true
}

const investigateHotspot = (spot: HotSpot) => {
  ElMessage.info(`Investigating hotspot at ${spot.location}`)
}

const acknowledgeAlarm = (alarm: RackAlarm) => {
  ElMessageBox.confirm(`Acknowledge alarm "${alarm.title}"?`, 'Confirm', {
    confirmButtonText: 'Acknowledge',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = activeAlarms.value.findIndex(a => a.id === alarm.id)
    if (index > -1) {
      activeAlarms.value.splice(index, 1)
      ElMessage.success(`Alarm "${alarm.title}" acknowledged`)
    }
  }).catch(() => {})
}

const escalateAlarm = (alarm: RackAlarm) => {
  ElMessageBox.confirm(`Escalate alarm "${alarm.title}" to management?`, 'Confirm', {
    confirmButtonText: 'Escalate',
    cancelButtonText: 'Cancel',
    type: 'error'
  }).then(() => {
    ElMessage.success(`Alarm "${alarm.title}" escalated`)
  }).catch(() => {})
}

const exportReport = () => {
  ElMessage.success('Exporting report...')
}

const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

// ==================== Chart Functions ====================
const trendChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null

const initChart = () => {
  nextTick(() => {
    if (!trendChartRef.value) {
      setTimeout(initChart, 200)
      return
    }

    if (trendChart) trendChart.dispose()
    trendChart = echarts.init(trendChartRef.value)
    updateTrendChart()

    window.addEventListener('resize', () => trendChart?.resize())
  })
}

const updateTrendChart = () => {
  if (!trendChart) return

  const isHourly = trendPeriod.value === 'hour'
  const data = isHourly ? hourlyTempData.value : dailyTempData.value
  const labels = isHourly ? hourLabels : dayLabels

  trendChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: '8%', right: '5%', top: '10%', bottom: '5%', containLabel: true },
    xAxis: { type: 'category', data: labels, axisLabel: { rotate: isHourly ? 45 : 0, color: '#606266' }, axisLine: { lineStyle: { color: '#dcdfe6' } } },
    yAxis: { type: 'value', name: 'Temperature (°C)', min: 20, max: 35, axisLabel: { color: '#606266' }, splitLine: { lineStyle: { color: '#ebeef5' } } },
    series: [{
      type: 'line', data: data, smooth: true,
      lineStyle: { color: '#f56c6c', width: 2 },
      areaStyle: { opacity: 0.1, color: '#f56c6c' },
      symbol: 'circle', symbolSize: 4,
      markLine: { data: [{ yAxis: 27, name: 'Warning', lineStyle: { color: '#e6a23c', type: 'dashed' } }] }
    }]
  })
}

// ==================== Loading Animation ====================
const startLoading = () => {
  let progress = 0
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 12
      loadingProgress.value = Math.min(progress, 90)
    }
  }, 100)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => {
        setTimeout(() => {
          initChart()
        }, 100)
      })
    }, 500)
  }, 2500)
}

watch(trendPeriod, () => {
  updateTrendChart()
})

// ==================== Lifecycle ====================
onMounted(() => {
  startLoading()
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
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
.spinner-ring:nth-child(4) { border-left-color: #ec489a; animation-delay: 0.6s; width: 20%; height: 20%; top: 40%; left: 40%; }

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

.loading-dots {
  display: inline-flex;
  gap: 2px;
}

.loading-dots span {
  animation: bounce 1.4s infinite ease-in-out both;
}

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

.loading-tip {
  font-size: 13px;
  color: #94a3b8;
  letter-spacing: 1px;
  margin-bottom: 8px;
  font-weight: 500;
}

.loading-subtip {
  font-size: 11px;
  color: #64748b;
  letter-spacing: 0.5px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ==================== Main Dashboard Styles ==================== */
.rack-alarms-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #eef2f5 100%);
  padding: 24px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
  background: white;
  padding: 16px 24px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.dashboard-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 700;
  color: #1f2f3d;
  margin: 0;
}

.title-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rack-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.header-stats {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.stat-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  background: #f5f7fa;
  border-radius: 20px;
  font-size: 13px;
  color: #606266;
}

.stat-badge.critical {
  background: #fef0f0;
  color: #f56c6c;
}

.stat-badge.warning {
  background: #fdf6ec;
  color: #e6a23c;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background: #f56c6c;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Rack Overview Cards */
.rack-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.overview-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
  cursor: pointer;
}

.overview-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.overview-card.temp {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.overview-card.power {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.overview-card.load {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.overview-card.density {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.overview-card-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.overview-icon {
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.overview-stats {
  flex: 1;
  margin-left: 16px;
}

.overview-label {
  font-size: 13px;
  opacity: 0.85;
  margin-bottom: 4px;
}

.overview-value {
  font-size: 28px;
  font-weight: 700;
}

.overview-value .unit {
  font-size: 12px;
  font-weight: normal;
  margin-left: 4px;
}

.overview-status {
  font-size: 11px;
  margin-top: 4px;
}

.overview-status.high { color: #fbbf24; }
.overview-status.low { color: #60a5fa; }
.overview-status.normal { color: #67c23a; }

.overview-gauge {
  margin-left: 16px;
}

.overview-badge {
  font-size: 32px;
}

/* Section Title */
.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.title-text {
  font-size: 18px;
  font-weight: 600;
  color: #1f2f3d;
}

.title-badge {
  background: #e4e7ed;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  color: #606266;
}

.title-badge.critical {
  background: #fef0f0;
  color: #f56c6c;
}

.title-badge.warning {
  background: #fdf6ec;
  color: #e6a23c;
}

.filter-group {
  display: flex;
  gap: 12px;
}

/* Rack Grid */
.rack-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.rack-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
  border-left: 4px solid #67c23a;
}

.rack-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.rack-card.critical { border-left-color: #f56c6c; }
.rack-card.warning { border-left-color: #e6a23c; }
.rack-card.normal { border-left-color: #67c23a; }

.rack-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fafafa;
  border-bottom: 1px solid #e4e7ed;
}

.rack-name {
  font-weight: 600;
  font-size: 14px;
  color: #1f2f3d;
  display: flex;
  align-items: center;
  gap: 6px;
}

.rack-status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 600;
}

.rack-status-badge.critical { background: #fef0f0; color: #f56c6c; }
.rack-status-badge.warning { background: #fdf6ec; color: #e6a23c; }
.rack-status-badge.normal { background: #f0f9eb; color: #67c23a; }

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.rack-temp-section {
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
}

.temp-readings {
  display: flex;
  justify-content: space-around;
  text-align: center;
}

.temp-reading {
  flex: 1;
}

.reading-label {
  font-size: 10px;
  color: #909399;
  margin-bottom: 4px;
}

.reading-value {
  font-size: 18px;
  font-weight: 600;
  color: #1f2f3d;
}

.reading-value.warning { color: #f56c6c; }

.rack-metrics {
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
}

.metric-bar {
  margin-bottom: 12px;
}

.metric-bar:last-child {
  margin-bottom: 0;
}

.metric-bar-label {
  font-size: 10px;
  color: #909399;
  margin-bottom: 4px;
}

.metric-bar-track {
  height: 6px;
  background: #e4e7ed;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 4px;
}

.metric-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s;
}

.metric-bar-value {
  font-size: 10px;
  color: #606266;
  text-align: right;
}

.rack-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: #fafafa;
  font-size: 10px;
  color: #909399;
}

.footer-info {
  display: flex;
  gap: 12px;
}

/* Hotspots Grid */
.hotspots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.hotspot-card {
  background: white;
  border-radius: 12px;
  padding: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border-left: 4px solid #e6a23c;
  transition: all 0.2s;
}

.hotspot-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.hotspot-card.critical { border-left-color: #f56c6c; }
.hotspot-card.warning { border-left-color: #e6a23c; }

.hotspot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.hotspot-location {
  font-weight: 600;
  font-size: 14px;
  color: #1f2f3d;
  display: flex;
  align-items: center;
  gap: 6px;
}

.hotspot-temp {
  font-size: 20px;
  font-weight: 700;
  color: #f56c6c;
}

.hotspot-details {
  margin-bottom: 12px;
}

.detail {
  font-size: 11px;
  color: #606266;
  margin-bottom: 4px;
}

.hotspot-actions {
  display: flex;
  justify-content: flex-end;
}

/* Alarms Container */
.alarms-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.alarm-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
}

.alarm-card:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.alarm-card.critical { border-left: 4px solid #f56c6c; }
.alarm-card.major { border-left: 4px solid #e6a23c; }
.alarm-card.warning { border-left: 4px solid #fbbf24; }

.alarm-icon {
  font-size: 24px;
}

.alarm-content {
  flex: 1;
}

.alarm-title {
  font-weight: 600;
  font-size: 14px;
  color: #1f2f3d;
  margin-bottom: 4px;
}

.alarm-description {
  font-size: 12px;
  color: #606266;
  margin-bottom: 6px;
}

.alarm-meta {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: #909399;
  flex-wrap: wrap;
}

.alarm-actions {
  display: flex;
  gap: 8px;
}

.empty-alarms {
  padding: 40px;
  text-align: center;
  background: white;
  border-radius: 12px;
}

/* Card */
.card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1f2f3d;
}

.chart-container {
  width: 100%;
  height: 320px;
  padding: 16px;
}

/* Responsive */
@media (max-width: 1200px) {
  .rack-overview {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 900px) {
  .rack-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .rack-alarms-dashboard {
    padding: 16px;
  }
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .rack-overview {
    grid-template-columns: 1fr;
  }
  .hotspots-grid {
    grid-template-columns: 1fr;
  }
  .temp-readings {
    flex-direction: column;
    gap: 8px;
  }
  .alarm-card {
    flex-direction: column;
    text-align: center;
  }
  .alarm-meta {
    justify-content: center;
  }
  .filter-group {
    flex-direction: column;
    width: 100%;
  }
}

/* Element Plus 样式覆盖 */
:deep(.el-progress-circle) {
  --el-progress-circle-width: 70px;
}

:deep(.el-progress__text) {
  font-size: 14px !important;
  font-weight: 600;
}
</style>