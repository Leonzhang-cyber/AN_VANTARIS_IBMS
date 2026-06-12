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
        <div class="loading-tip">Digital Twin - Real-Time Twin</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="real-time-twin-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Real-Time Twin</h1>
        <p>Live synchronization between physical assets and digital twin with real-time telemetry data</p>
      </div>
      <div class="header-actions">
        <div class="connection-status" :class="connectionStatus">
          <span class="status-dot"></span>
          <span>{{ connectionStatus === 'connected' ? 'Connected' : connectionStatus === 'connecting' ? 'Connecting...' : 'Disconnected' }}</span>
        </div>
        <el-button type="primary" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          Sync Now
        </el-button>
        <el-button @click="exportData">
          <el-icon><Download /></el-icon>
          Export Data
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon primary-bg">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.activeDevices }}</div>
            <div class="stat-label">Active Devices</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><DataLine /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.dataPointsPerSecond }}</div>
            <div class="stat-label">Data Points/sec</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.latestUpdate }}s</div>
            <div class="stat-label">Last Update</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon info-bg">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.syncAccuracy }}%</div>
            <div class="stat-label">Sync Accuracy</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Main Content Row -->
    <el-row :gutter="20">
      <!-- 3D Viewer with Real-time Overlays -->
      <el-col :xs="24" :lg="14">
        <div class="viewer-card">
          <div class="card-header">
            <h3>Digital Twin Environment</h3>
            <div class="viewer-controls">
              <el-switch
                  v-model="showHeatmap"
                  active-text="Heatmap"
                  inactive-text="Heatmap"
                  size="small"
              />
              <el-switch
                  v-model="showAlerts"
                  active-text="Alerts"
                  inactive-text="Alerts"
                  size="small"
              />
              <el-button size="small" @click="resetCamera">
                <el-icon><RefreshRight /></el-icon>
                Reset
              </el-button>
            </div>
          </div>
          <div class="viewer-container" ref="viewerContainerRef">
            <canvas ref="viewerCanvasRef" class="viewer-canvas"></canvas>
            <!-- Real-time Alert Overlay -->
            <div v-if="activeAlert" class="alert-overlay" :class="activeAlert.severity">
              <div class="alert-icon">
                <el-icon><WarningFilled /></el-icon>
              </div>
              <div class="alert-content">
                <div class="alert-title">{{ activeAlert.title }}</div>
                <div class="alert-message">{{ activeAlert.message }}</div>
              </div>
              <el-button size="small" @click="dismissAlert">Dismiss</el-button>
            </div>
          </div>
          <div class="viewer-footer">
            <div class="twin-status">
              <span class="label">Twin Status:</span>
              <span class="value synchronized">Synchronized</span>
            </div>
            <div class="sync-timestamp">
              Last sync: {{ lastSyncTime }}
            </div>
          </div>
        </div>
      </el-col>

      <!-- Real-time Data Stream -->
      <el-col :xs="24" :lg="10">
        <div class="data-stream-card">
          <div class="card-header">
            <h3>Live Data Stream</h3>
            <el-tag type="danger" size="small" v-if="unreadAlerts > 0">
              {{ unreadAlerts }} alerts
            </el-tag>
          </div>
          <div class="data-stream">
            <div
                v-for="data in dataStream.slice(0, 12)"
                :key="data.id"
                class="data-item"
                :class="{ alert: data.severity === 'warning' || data.severity === 'critical' }"
            >
              <div class="data-icon" :class="getDataIconClass(data.type)">
                <el-icon><component :is="getDataIcon(data.type)" /></el-icon>
              </div>
              <div class="data-content">
                <div class="data-header">
                  <span class="data-device">{{ data.device }}</span>
                  <span class="data-time">{{ formatTime(data.timestamp) }}</span>
                </div>
                <div class="data-value">
                  <span class="value">{{ data.value }}{{ data.unit }}</span>
                  <span class="threshold" v-if="data.threshold">
                    (Threshold: {{ data.threshold }})
                  </span>
                </div>
                <div class="data-location">{{ data.location }}</div>
              </div>
              <div class="data-status" :class="data.status">
                <span class="status-dot"></span>
              </div>
            </div>
            <div v-if="dataStream.length === 0" class="no-data">
              <el-empty description="Waiting for data stream..." :image-size="60" />
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Charts Row -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="card-header">
            <h3>Temperature Trends</h3>
            <el-select v-model="tempMetric" size="small" style="width: 100px">
              <el-option label="Zone A" value="zoneA" />
              <el-option label="Zone B" value="zoneB" />
              <el-option label="Zone C" value="zoneC" />
            </el-select>
          </div>
          <div ref="tempChartRef" class="chart-container"></div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="card-header">
            <h3>Energy Consumption</h3>
            <el-select v-model="energyMetric" size="small" style="width: 100px">
              <el-option label="kW" value="kW" />
              <el-option label="kWh" value="kWh" />
            </el-select>
          </div>
          <div ref="energyChartRef" class="chart-container"></div>
        </div>
      </el-col>
    </el-row>

    <!-- Device Status Table -->
    <div class="device-table-wrapper">
      <div class="table-header">
        <h3>Connected Devices</h3>
        <el-input
            v-model="deviceSearch"
            placeholder="Search devices..."
            clearable
            style="width: 200px"
            :prefix-icon="Search"
        />
      </div>
      <el-table :data="filteredDevices" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="name" label="Device Name" min-width="180">
          <template #default="{ row }">
            <div class="device-name-cell">
              <el-icon><component :is="getDeviceIcon(row.type)" /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="Type" width="120" />
        <el-table-column prop="location" label="Location" width="150" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              <span class="status-dot" :class="row.status.toLowerCase()"></span>
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastValue" label="Last Reading" width="120">
          <template #default="{ row }">
            {{ row.lastValue }}{{ row.unit }}
          </template>
        </el-table-column>
        <el-table-column prop="lastUpdate" label="Last Update" width="160">
          <template #default="{ row }">
            {{ formatRelativeTime(row.lastUpdate) }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDeviceDetails(row)">
              Details
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Device Detail Dialog -->
    <el-dialog v-model="detailDialog.visible" :title="detailDialog.device?.name" width="650px">
      <div v-if="detailDialog.device" class="device-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Device ID">{{ detailDialog.device.id }}</el-descriptions-item>
          <el-descriptions-item label="Type">{{ detailDialog.device.type }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ detailDialog.device.location }}</el-descriptions-item>
          <el-descriptions-item label="IP Address">{{ detailDialog.device.ipAddress }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(detailDialog.device.status)">{{ detailDialog.device.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Last Value">
            {{ detailDialog.device.lastValue }}{{ detailDialog.device.unit }}
          </el-descriptions-item>
          <el-descriptions-item label="Threshold Min">{{ detailDialog.device.thresholdMin }}</el-descriptions-item>
          <el-descriptions-item label="Threshold Max">{{ detailDialog.device.thresholdMax }}</el-descriptions-item>
          <el-descriptions-item label="Last Update">{{ formatFullTimestamp(detailDialog.device.lastUpdate) }}</el-descriptions-item>
          <el-descriptions-item label="Firmware">{{ detailDialog.device.firmware }}</el-descriptions-item>
        </el-descriptions>
        <div class="detail-chart" ref="detailChartRef"></div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Refresh,
  Download,
  Connection,
  DataLine,
  Clock,
  DataAnalysis,
  RefreshRight,
  WarningFilled,
  Search,
  Tools,
  Monitor,
  Guide,
  Warning
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Connecting to IoT gateway...',
  'Synchronizing digital twin...',
  'Almost ready...'
]

// ==================== Type Definitions ====================
interface Device {
  id: string
  name: string
  type: string
  location: string
  status: 'Online' | 'Offline' | 'Warning' | 'Alert'
  lastValue: number
  unit: string
  thresholdMin: number
  thresholdMax: number
  lastUpdate: Date
  ipAddress: string
  firmware: string
}

interface DataPoint {
  id: string
  device: string
  type: string
  value: number
  unit: string
  location: string
  timestamp: Date
  status: 'normal' | 'warning' | 'critical'
  severity?: string
  threshold?: number
}

interface Alert {
  id: string
  title: string
  message: string
  severity: 'critical' | 'warning' | 'info'
  timestamp: Date
  acknowledged: boolean
}

// ==================== 模拟数据生成 ====================
const generateMockDevices = (): Device[] => {
  const deviceTypes = [
    { type: 'Temperature Sensor', unit: '°C', min: 15, max: 30 },
    { type: 'Humidity Sensor', unit: '%', min: 30, max: 70 },
    { type: 'Power Meter', unit: 'kW', min: 0, max: 100 },
    { type: 'HVAC Controller', unit: '°C', min: 18, max: 26 },
    { type: 'Vibration Sensor', unit: 'mm/s', min: 0, max: 10 }
  ]

  const locations = ['Server Room A', 'Server Room B', 'Data Hall', 'HVAC Room', 'Electrical Room', 'UPS Room', 'Battery Room']
  const statuses: ('Online' | 'Offline' | 'Warning' | 'Alert')[] = ['Online', 'Online', 'Online', 'Online', 'Online', 'Warning', 'Alert']

  const devices: Device[] = []

  for (let i = 1; i <= 24; i++) {
    const deviceType = deviceTypes[Math.floor(Math.random() * deviceTypes.length)]
    const status = statuses[Math.floor(Math.random() * statuses.length)]
    const lastValue = status === 'Online'
        ? deviceType.min + Math.random() * (deviceType.max - deviceType.min)
        : status === 'Warning'
            ? deviceType.max + Math.random() * 10
            : 0

    devices.push({
      id: `DEV-${String(i).padStart(4, '0')}`,
      name: `${deviceType.type} ${i}`,
      type: deviceType.type,
      location: locations[Math.floor(Math.random() * locations.length)],
      status: status,
      lastValue: parseFloat(lastValue.toFixed(1)),
      unit: deviceType.unit,
      thresholdMin: deviceType.min,
      thresholdMax: deviceType.max,
      lastUpdate: new Date(Date.now() - Math.random() * 60000),
      ipAddress: `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
      firmware: `v${Math.floor(Math.random() * 3) + 1}.${Math.floor(Math.random() * 10)}.${Math.floor(Math.random() * 10)}`
    })
  }

  return devices
}

// Generate real-time data stream
let dataInterval: number | null = null
const generateDataPoint = (): DataPoint => {
  const devices = allDevices.value
  if (devices.length === 0) return {} as DataPoint

  const device = devices[Math.floor(Math.random() * devices.length)]
  const isAlert = Math.random() > 0.85
  let value = device.lastValue + (Math.random() - 0.5) * 2

  let status: 'normal' | 'warning' | 'critical' = 'normal'
  let severity: string | undefined = undefined

  if (value > device.thresholdMax) {
    status = value > device.thresholdMax + 5 ? 'critical' : 'warning'
    severity = status === 'critical' ? 'critical' : 'warning'
  } else if (value < device.thresholdMin) {
    status = value < device.thresholdMin - 5 ? 'critical' : 'warning'
    severity = status === 'critical' ? 'critical' : 'warning'
  }

  // Update device last value
  device.lastValue = parseFloat(value.toFixed(1))
  device.lastUpdate = new Date()
  if (status !== 'normal') {
    device.status = status === 'critical' ? 'Alert' : 'Warning'
  } else {
    device.status = 'Online'
  }

  return {
    id: `dp-${Date.now()}-${Math.random()}`,
    device: device.name,
    type: device.type,
    value: parseFloat(value.toFixed(1)),
    unit: device.unit,
    location: device.location,
    timestamp: new Date(),
    status: status,
    severity: severity,
    threshold: status !== 'normal' ? device.thresholdMax : undefined
  }
}

// Generate alert from data point
const generateAlertFromData = (dataPoint: DataPoint): Alert | null => {
  if (dataPoint.status === 'normal') return null

  return {
    id: `alt-${Date.now()}`,
    title: `${dataPoint.type} Alert`,
    message: `${dataPoint.device} at ${dataPoint.location} reading ${dataPoint.value}${dataPoint.unit} exceeds threshold ${dataPoint.threshold}${dataPoint.unit}`,
    severity: dataPoint.status === 'critical' ? 'critical' : 'warning',
    timestamp: new Date(),
    acknowledged: false
  }
}

// ==================== 响应式状态 ====================
const allDevices = ref<Device[]>([])
const dataStream = ref<DataPoint[]>([])
const alerts = ref<Alert[]>([])
const connectionStatus = ref<'connected' | 'connecting' | 'disconnected'>('connecting')
const showHeatmap = ref(false)
const showAlerts = ref(true)
const tempMetric = ref('zoneA')
const energyMetric = ref('kW')
const deviceSearch = ref('')
const lastSyncTime = ref('')
const unreadAlerts = computed(() => alerts.value.filter(a => !a.acknowledged).length)
const activeAlert = ref<Alert | null>(null)

const viewerCanvasRef = ref<HTMLCanvasElement | null>(null)
const viewerContainerRef = ref<HTMLDivElement | null>(null)
const tempChartRef = ref<HTMLElement | null>(null)
const energyChartRef = ref<HTMLElement | null>(null)
const detailChartRef = ref<HTMLElement | null>(null)

let animationFrameId: number | null = null
let tempChart: echarts.ECharts | null = null
let energyChart: echarts.ECharts | null = null
let detailChart: echarts.ECharts | null = null

const stats = reactive({
  activeDevices: 0,
  dataPointsPerSecond: 0,
  latestUpdate: 0,
  syncAccuracy: 99.2
})

const detailDialog = reactive({
  visible: false,
  device: null as Device | null
})

// ==================== 计算属性 ====================
const filteredDevices = computed(() => {
  let filtered = [...allDevices.value]
  if (deviceSearch.value) {
    const searchLower = deviceSearch.value.toLowerCase()
    filtered = filtered.filter(d =>
        d.name.toLowerCase().includes(searchLower) ||
        d.id.toLowerCase().includes(searchLower) ||
        d.location.toLowerCase().includes(searchLower)
    )
  }
  return filtered
})

// ==================== 辅助函数 ====================
const formatTime = (date: Date) => {
  return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

const formatRelativeTime = (date: Date) => {
  const diffMs = Date.now() - date.getTime()
  const diffSecs = Math.floor(diffMs / 1000)
  if (diffSecs < 60) return `${diffSecs} sec ago`
  if (diffSecs < 3600) return `${Math.floor(diffSecs / 60)} min ago`
  return `${Math.floor(diffSecs / 3600)} hr ago`
}

const formatFullTimestamp = (date: Date) => {
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const getDataIcon = (type: string) => {
  if (type.includes('Temperature')) return Guide
  if (type.includes('Humidity')) return Guide
  if (type.includes('Power')) return DataLine
  if (type.includes('HVAC')) return Tools
  return Monitor
}

const getDataIconClass = (type: string) => {
  if (type.includes('Temperature')) return 'temp'
  if (type.includes('Humidity')) return 'humidity'
  if (type.includes('Power')) return 'power'
  if (type.includes('HVAC')) return 'hvac'
  return 'default'
}

const getDeviceIcon = (type: string) => {
  if (type.includes('Temperature')) return Guide
  if (type.includes('Humidity')) return Guide
  if (type.includes('Power')) return DataLine
  if (type.includes('HVAC')) return Tools
  return Monitor
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    'Online': 'success',
    'Offline': 'info',
    'Warning': 'warning',
    'Alert': 'danger'
  }
  return map[status] || 'info'
}

const updateStats = () => {
  stats.activeDevices = allDevices.value.filter(d => d.status === 'Online').length
  stats.dataPointsPerSecond = Math.floor(Math.random() * 50) + 120
  const latestUpdate = Math.max(...allDevices.value.map(d => d.lastUpdate.getTime()))
  stats.latestUpdate = Math.floor((Date.now() - latestUpdate) / 1000)
}

// ==================== 3D 场景绘制 ====================
const draw3DScene = () => {
  const canvas = viewerCanvasRef.value
  const container = viewerContainerRef.value
  if (!canvas || !container) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const width = container.clientWidth
  const height = 450
  canvas.width = width
  canvas.height = height

  // Background
  const gradient = ctx.createLinearGradient(0, 0, 0, height)
  gradient.addColorStop(0, '#1a1a2e')
  gradient.addColorStop(1, '#16213e')
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, width, height)

  // Draw floor grid
  const centerX = width / 2
  const centerY = height / 2
  const scale = 6

  ctx.strokeStyle = 'rgba(100, 150, 255, 0.2)'
  ctx.lineWidth = 1
  for (let i = -15; i <= 15; i += 2) {
    const x1 = centerX + i * scale
    const y1 = centerY - 15 * scale
    const x2 = centerX + i * scale
    const y2 = centerY + 15 * scale
    ctx.beginPath()
    ctx.moveTo(x1, y1)
    ctx.lineTo(x2, y2)
    ctx.stroke()

    const x3 = centerX - 15 * scale
    const y3 = centerY + i * scale
    const x4 = centerX + 15 * scale
    const y4 = centerY + i * scale
    ctx.beginPath()
    ctx.moveTo(x3, y3)
    ctx.lineTo(x4, y4)
    ctx.stroke()
  }

  // Draw rooms
  const rooms = [
    { name: 'Server Room', x: -80, y: -60, w: 70, h: 50, color: '#409eff' },
    { name: 'HVAC Room', x: 10, y: -60, w: 70, h: 50, color: '#e6a23c' },
    { name: 'Electrical', x: -80, y: 10, w: 70, h: 50, color: '#f56c6c' },
    { name: 'Battery Room', x: 10, y: 10, w: 70, h: 50, color: '#67c23a' }
  ]

  rooms.forEach(room => {
    ctx.fillStyle = `rgba(${room.color === '#409eff' ? '64,158,255' : room.color === '#e6a23c' ? '230,162,60' : room.color === '#f56c6c' ? '245,108,108' : '103,194,58'}, 0.15)`
    ctx.fillRect(centerX + room.x, centerY + room.y, room.w, room.h)
    ctx.strokeStyle = room.color
    ctx.lineWidth = 2
    ctx.strokeRect(centerX + room.x, centerY + room.y, room.w, room.h)
    ctx.fillStyle = room.color
    ctx.font = '10px Arial'
    ctx.fillText(room.name, centerX + room.x + 5, centerY + room.y + 15)
  })

  // Draw devices on map
  allDevices.value.slice(0, 20).forEach((device, idx) => {
    let color = '#67c23a'
    if (device.status === 'Warning') color = '#e6a23c'
    if (device.status === 'Alert') color = '#f56c6c'
    if (device.status === 'Offline') color = '#909399'

    const angle = (idx * 0.5) % (Math.PI * 2)
    const radius = 60 + Math.sin(idx) * 20
    const x = centerX + Math.cos(angle) * radius
    const y = centerY + Math.sin(angle) * radius

    ctx.beginPath()
    ctx.arc(x, y, 8, 0, Math.PI * 2)
    ctx.fillStyle = color
    ctx.fill()
    ctx.strokeStyle = 'white'
    ctx.lineWidth = 2
    ctx.stroke()

    ctx.fillStyle = 'white'
    ctx.font = '9px Arial'
    ctx.fillText(device.name.substring(0, 10), x - 15, y - 10)

    // Add pulsing effect for alerts
    if (device.status === 'Alert' && Date.now() % 1000 < 500) {
      ctx.beginPath()
      ctx.arc(x, y, 14, 0, Math.PI * 2)
      ctx.strokeStyle = '#f56c6c'
      ctx.lineWidth = 2
      ctx.stroke()
    }
  })

  // Draw heatmap overlay if enabled
  if (showHeatmap.value) {
    const gradientHeat = ctx.createLinearGradient(centerX - 100, centerY - 80, centerX + 100, centerY + 80)
    gradientHeat.addColorStop(0, 'rgba(103, 194, 58, 0.3)')
    gradientHeat.addColorStop(0.5, 'rgba(230, 162, 60, 0.3)')
    gradientHeat.addColorStop(1, 'rgba(245, 108, 108, 0.3)')
    ctx.fillStyle = gradientHeat
    ctx.fillRect(centerX - 150, centerY - 120, 300, 240)
  }
}

const startRenderLoop = () => {
  const render = () => {
    draw3DScene()
    animationFrameId = requestAnimationFrame(render)
  }
  render()
}

const resetCamera = () => {
  draw3DScene()
}

// ==================== 图表渲染 ====================
const renderTempChart = () => {
  if (!tempChartRef.value) return
  if (tempChart) tempChart.dispose()

  tempChart = echarts.init(tempChartRef.value)

  const times = Array.from({ length: 20 }, (_, i) => {
    const d = new Date()
    d.setMinutes(d.getMinutes() - (19 - i))
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  })

  const zoneData = {
    zoneA: Array.from({ length: 20 }, () => 22 + Math.random() * 4),
    zoneB: Array.from({ length: 20 }, () => 23 + Math.random() * 5),
    zoneC: Array.from({ length: 20 }, () => 21 + Math.random() * 3)
  }

  tempChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Zone A', 'Zone B', 'Zone C'], bottom: 0 },
    xAxis: { type: 'category', data: times, axisLabel: { rotate: 45 } },
    yAxis: { type: 'value', name: 'Temperature (°C)' },
    series: [
      { name: 'Zone A', type: 'line', smooth: true, data: zoneData.zoneA, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Zone B', type: 'line', smooth: true, data: zoneData.zoneB, lineStyle: { color: '#e6a23c', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Zone C', type: 'line', smooth: true, data: zoneData.zoneC, lineStyle: { color: '#67c23a', width: 2 }, areaStyle: { opacity: 0.1 } }
    ]
  })
}

const renderEnergyChart = () => {
  if (!energyChartRef.value) return
  if (energyChart) energyChart.dispose()

  energyChart = echarts.init(energyChartRef.value)

  const times = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const data = Array.from({ length: 24 }, () => Math.floor(50 + Math.random() * 80))

  energyChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: times, axisLabel: { rotate: 45 } },
    yAxis: { type: 'value', name: energyMetric.value === 'kW' ? 'Power (kW)' : 'Energy (kWh)' },
    series: [{
      type: 'bar',
      data: data,
      itemStyle: { color: '#409eff', borderRadius: [4, 4, 0, 0] }
    }]
  })
}

// ==================== 实时数据流 ====================
const startDataStream = () => {
  if (dataInterval) clearInterval(dataInterval)

  dataInterval = window.setInterval(() => {
    const newData = generateDataPoint()
    dataStream.value.unshift(newData)
    if (dataStream.value.length > 50) dataStream.value.pop()

    // Generate alert if needed
    const alert = generateAlertFromData(newData)
    if (alert && showAlerts.value) {
      alerts.value.unshift(alert)
      if (alerts.value.length > 20) alerts.value.pop()
      if (!activeAlert.value && alert.severity === 'critical') {
        activeAlert.value = alert
        setTimeout(() => {
          if (activeAlert.value === alert) activeAlert.value = null
        }, 8000)
      }
    }

    updateStats()
    draw3DScene()
    lastSyncTime.value = new Date().toLocaleTimeString()
  }, 800)
}

// ==================== 交互事件 ====================
const refreshData = () => {
  tableLoading.value = true
  setTimeout(() => {
    allDevices.value = generateMockDevices()
    updateStats()
    tableLoading.value = false
    ElMessage.success('Data synchronized with digital twin')
  }, 800)
}

const exportData = () => {
  const exportData = {
    generatedAt: new Date().toISOString(),
    summary: stats,
    devices: allDevices.value,
    recentData: dataStream.value.slice(0, 30),
    alerts: alerts.value
  }
  const data = JSON.stringify(exportData, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `real-time-twin-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Data exported')
}

const viewDeviceDetails = (device: Device) => {
  detailDialog.device = device
  detailDialog.visible = true
  nextTick(() => {
    if (detailChartRef.value) {
      if (detailChart) detailChart.dispose()
      detailChart = echarts.init(detailChartRef.value)
      detailChart.setOption({
        title: { text: 'Historical Data', left: 'center' },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: Array.from({ length: 12 }, (_, i) => `${12 - i} hours ago`) },
        yAxis: { type: 'value', name: device.unit },
        series: [{
          type: 'line',
          data: Array.from({ length: 12 }, () => device.thresholdMin + Math.random() * (device.thresholdMax - device.thresholdMin)),
          smooth: true,
          areaStyle: { opacity: 0.3 }
        }]
      })
    }
  })
}

const dismissAlert = () => {
  if (activeAlert.value) {
    activeAlert.value.acknowledged = true
    activeAlert.value = null
  }
}

// ==================== 数据加载 ====================
const loadData = () => {
  allDevices.value = generateMockDevices()
  updateStats()
  connectionStatus.value = 'connected'
  lastSyncTime.value = new Date().toLocaleTimeString()

  nextTick(() => {
    renderTempChart()
    renderEnergyChart()
    startRenderLoop()
    startDataStream()
  })
}

// ==================== 生命周期 ====================
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
      loadData()
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
  if (dataInterval) clearInterval(dataInterval)
  window.removeEventListener('resize', () => {
    tempChart?.resize()
    energyChart?.resize()
    detailChart?.resize()
  })
})

watch([tempMetric, energyMetric], () => {
  renderTempChart()
  renderEnergyChart()
})

watch(isLoaded, (loaded) => {
  if (loaded) {
    window.addEventListener('resize', () => {
      tempChart?.resize()
      energyChart?.resize()
      detailChart?.resize()
    })
  }
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

.spinner-ring:nth-child(1) {
  border-top-color: #3b82f6;
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  border-right-color: #f59e0b;
  animation-delay: 0.2s;
  width: 70%;
  height: 70%;
  top: 15%;
  left: 15%;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #10b981;
  animation-delay: 0.4s;
  width: 40%;
  height: 40%;
  top: 30%;
  left: 30%;
}

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

/* ==================== Main Content Styles ==================== */
.real-time-twin-page {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #1f2f3d;
}

.page-header p {
  margin: 0;
  color: #5e6e82;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.connection-status.connected {
  background-color: #f0f9eb;
  color: #67c23a;
}

.connection-status.connecting {
  background-color: #fff3e0;
  color: #e6a23c;
}

.connection-status.disconnected {
  background-color: #fef0f0;
  color: #f56c6c;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.connection-status.connected .status-dot { background-color: #67c23a; }
.connection-status.connecting .status-dot { background-color: #e6a23c; animation: pulse 1.5s infinite; }
.connection-status.disconnected .status-dot { background-color: #f56c6c; }

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.primary-bg { background-color: #ecf5ff; color: #409eff; }
.success-bg { background-color: #f0f9eb; color: #67c23a; }
.warning-bg { background-color: #fff3e0; color: #e6a23c; }
.info-bg { background-color: #f5f7fa; color: #8c9aab; }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #8c9aab;
  margin-top: 4px;
}

/* Viewer Card */
.viewer-card, .data-stream-card, .chart-card, .device-table-wrapper {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

.viewer-container {
  position: relative;
  background-color: #1a1a2e;
  border-radius: 8px;
  overflow: hidden;
}

.viewer-canvas {
  width: 100%;
  height: 450px;
  display: block;
}

.viewer-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.twin-status .label {
  font-size: 12px;
  color: #8c9aab;
}

.twin-status .value.synchronized {
  color: #67c23a;
  font-weight: 500;
}

.sync-timestamp {
  font-size: 11px;
  color: #8c9aab;
  font-family: monospace;
}

/* Alert Overlay */
.alert-overlay {
  position: absolute;
  top: 20px;
  left: 20px;
  right: 20px;
  background: rgba(0, 0, 0, 0.9);
  border-radius: 8px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 100;
  animation: slideDown 0.3s ease;
}

.alert-overlay.critical {
  border-left: 4px solid #f56c6c;
}

.alert-overlay.warning {
  border-left: 4px solid #e6a23c;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

.alert-icon {
  font-size: 24px;
}

.alert-overlay.critical .alert-icon { color: #f56c6c; }
.alert-overlay.warning .alert-icon { color: #e6a23c; }

.alert-content {
  flex: 1;
}

.alert-title {
  font-weight: 600;
  color: white;
  margin-bottom: 4px;
}

.alert-message {
  font-size: 12px;
  color: #c0c4cc;
}

/* Data Stream */
.data-stream {
  max-height: 450px;
  overflow-y: auto;
}

.data-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
  transition: background-color 0.2s;
}

.data-item.alert {
  background-color: #fef0f0;
}

.data-item:hover {
  background-color: #f5f7fa;
}

.data-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.data-icon.temp { background-color: #ecf5ff; color: #409eff; }
.data-icon.humidity { background-color: #f0f9eb; color: #67c23a; }
.data-icon.power { background-color: #fff3e0; color: #e6a23c; }
.data-icon.hvac { background-color: #fef0f0; color: #f56c6c; }

.data-content {
  flex: 1;
}

.data-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.data-device {
  font-weight: 600;
  font-size: 13px;
  color: #1f2f3d;
}

.data-time {
  font-size: 10px;
  color: #c0c4cc;
}

.data-value {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 2px;
}

.data-value .value {
  color: #1f2f3d;
}

.data-value .threshold {
  font-size: 11px;
  color: #f56c6c;
  margin-left: 8px;
}

.data-location {
  font-size: 10px;
  color: #8c9aab;
}

.data-status {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.data-status.normal { background-color: #67c23a; }
.data-status.warning { background-color: #e6a23c; }
.data-status.critical { background-color: #f56c6c; animation: pulse 1s infinite; }

.no-data {
  padding: 40px 0;
}

/* Charts */
.charts-row {
  margin-bottom: 0;
}

.chart-container {
  height: 280px;
  width: 100%;
}

/* Device Table */
.device-table-wrapper {
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.table-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

.device-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Detail Chart */
.detail-chart {
  height: 200px;
  margin-top: 16px;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
}

:deep(.el-progress__text) {
  font-size: 11px !important;
}
</style>