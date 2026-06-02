<template>
  <!-- ==================== Loading Screen ==================== -->
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
        <div class="loading-tip">Real-Time Device Monitoring</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- ==================== Main Content ==================== -->
  <div v-else class="real-time-status-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/systems-devices/device-inventory' }">
            Systems & Devices
          </el-breadcrumb-item>
          <el-breadcrumb-item>Device Monitoring</el-breadcrumb-item>
          <el-breadcrumb-item>Real-Time Status</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <div class="connection-status">
          <span class="status-dot" :class="{ online: wsConnected, offline: !wsConnected }"></span>
          <span>{{ wsConnected ? 'Connected' : 'Reconnecting...' }}</span>
        </div>
        <el-button :icon="Refresh" @click="refreshData" :loading="refreshing">Refresh</el-button>
        <el-button type="primary" :icon="BellFilled" @click="openAlertSettings">Alert Settings</el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card online" @click="filterStatus = 'online'">
        <div class="stat-icon"><el-icon><CircleCheckFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.online }}</span>
          <span class="stat-label">Online</span>
        </div>
        <div class="stat-trend">↑ {{ stats.onlineChange }}</div>
      </div>
      <div class="stat-card warning" @click="filterStatus = 'warning'">
        <div class="stat-icon"><el-icon><WarningFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.warning }}</span>
          <span class="stat-label">Warning</span>
        </div>
        <div class="stat-trend">⚠ {{ stats.warningChange }}</div>
      </div>
      <div class="stat-card error" @click="filterStatus = 'error'">
        <div class="stat-icon"><el-icon><CircleCloseFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.error }}</span>
          <span class="stat-label">Error</span>
        </div>
        <div class="stat-trend">! {{ stats.errorChange }}</div>
      </div>
      <div class="stat-card offline" @click="filterStatus = 'offline'">
        <div class="stat-icon"><el-icon><RemoveFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.offline }}</span>
          <span class="stat-label">Offline</span>
        </div>
        <div class="stat-trend">↓ {{ stats.offlineChange }}</div>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchKeyword"
            placeholder="Search by device name, model, or ID"
            clearable
            :prefix-icon="Search"
            style="width: 260px"
            @clear="loadDevices"
            @keyup.enter="loadDevices"
        />
        <el-select v-model="filterSystem" placeholder="System Type" clearable style="width: 140px" @change="loadDevices">
          <el-option label="All Systems" value="" />
          <el-option label="HVAC" value="hvac" />
          <el-option label="Lighting" value="lighting" />
          <el-option label="Security" value="sas" />
          <el-option label="Fire Alarm" value="fas" />
          <el-option label="Plumbing" value="plumbing" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="Status" clearable style="width: 120px" @change="loadDevices">
          <el-option label="All Status" value="" />
          <el-option label="Online" value="online" />
          <el-option label="Warning" value="warning" />
          <el-option label="Error" value="error" />
          <el-option label="Offline" value="offline" />
        </el-select>
        <el-select v-model="filterArea" placeholder="Area" clearable style="width: 140px" @change="loadDevices">
          <el-option label="All Areas" value="" />
          <el-option v-for="area in areas" :key="area" :label="area" :value="area" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-radio-group v-model="viewMode" size="small">
          <el-radio-button value="grid"><el-icon><Grid /></el-icon> Grid</el-radio-button>
          <el-radio-button value="list"><el-icon><List /></el-icon> List</el-radio-button>
        </el-radio-group>
        <el-tooltip content="Auto-refresh every 5 seconds">
          <el-switch v-model="autoRefresh" active-text="Auto" />
        </el-tooltip>
      </div>
    </div>

    <!-- 设备网格视图 -->
    <div v-if="viewMode === 'grid'" class="device-grid">
      <div v-if="filteredDevices.length === 0" class="empty-state">
        <el-empty description="No devices found" />
      </div>
      <div v-else class="grid-container">
        <div
            v-for="device in filteredDevices"
            :key="device.id"
            class="device-card"
            :class="[`status-${device.status}`, { selected: selectedDevice?.id === device.id }]"
            @click="selectDevice(device)"
        >
          <div class="card-header">
            <div class="device-icon">
              <el-icon><component :is="getSystemIcon(device.systemType)" /></el-icon>
            </div>
            <div class="device-status">
              <span class="status-dot" :class="device.status"></span>
              <span class="status-text">{{ device.status.toUpperCase() }}</span>
            </div>
          </div>
          <div class="card-body">
            <h4 class="device-name">{{ device.name }}</h4>
            <p class="device-model">{{ device.model }}</p>
            <p class="device-location">{{ device.area }} | {{ device.floor }}</p>
          </div>
          <div class="card-metrics">
            <div class="metric">
              <span class="metric-label">Temp</span>
              <span class="metric-value" :class="{ warning: device.metrics.temperature > 28 }">
                {{ device.metrics.temperature }}°C
              </span>
            </div>
            <div class="metric">
              <span class="metric-label">Power</span>
              <span class="metric-value" :class="{ warning: device.metrics.power > 20 }">
                {{ device.metrics.power }} kW
              </span>
            </div>
            <div class="metric">
              <span class="metric-label">Efficiency</span>
              <span class="metric-value" :class="{ warning: device.metrics.efficiency < 80 }">
                {{ device.metrics.efficiency }}%
              </span>
            </div>
          </div>
          <div class="card-footer">
            <span class="last-update">Last: {{ formatTime(device.lastUpdate) }}</span>
            <el-button size="small" text @click.stop="viewDetails(device)">Details</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 设备列表视图 -->
    <div v-else class="device-list">
      <el-table :data="filteredDevices" stripe border style="width: 100%" @row-click="selectDevice" highlight-current-row>
        <el-table-column type="index" label="#" width="50" />
        <el-table-column label="Device" min-width="220">
          <template #default="{ row }">
            <div class="device-cell">
              <el-avatar :src="row.imageUrl" :size="36" shape="square" fit="cover">
                <template #error><el-icon><Cpu /></el-icon></template>
              </el-avatar>
              <div class="device-info">
                <span class="device-name">{{ row.name }}</span>
                <span class="device-model">{{ row.model }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="serialNumber" label="Serial No" width="150" />
        <el-table-column label="System" width="120">
          <template #default="{ row }">
            <el-tag :type="getSystemTagType(row.systemType)" size="small">{{ getSystemLabel(row.systemType) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="110">
          <template #default="{ row }">
            <div class="status-cell">
              <span class="status-dot" :class="row.status"></span>
              <span>{{ row.status.toUpperCase() }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Temperature" width="120">
          <template #default="{ row }">
            <span :class="{ 'text-warning': row.metrics.temperature > 28 }">{{ row.metrics.temperature }}°C</span>
          </template>
        </el-table-column>
        <el-table-column label="Power" width="120">
          <template #default="{ row }">
            <span :class="{ 'text-warning': row.metrics.power > 20 }">{{ row.metrics.power }} kW</span>
          </template>
        </el-table-column>
        <el-table-column label="Efficiency" width="120">
          <template #default="{ row }">
            <el-progress :percentage="row.metrics.efficiency" :stroke-width="6" :show-text="false" style="width: 80px" />
            <span :class="{ 'text-danger': row.metrics.efficiency < 80 }">{{ row.metrics.efficiency }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="Last Update" width="160">
          <template #default="{ row }">{{ formatDateTime(row.lastUpdate) }}</template>
        </el-table-column>
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text @click.stop="viewDetails(row)">View</el-button>
            <el-button size="small" text type="primary" @click.stop="controlDevice(row)">Control</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 设备详情抽屉 -->
    <el-drawer v-model="detailDrawerVisible" :title="selectedDevice?.name || 'Device Details'" size="40%" direction="rtl">
      <div v-if="selectedDevice" class="device-detail">
        <div class="detail-header">
          <el-avatar :src="selectedDevice.imageUrl" :size="80" shape="square" fit="cover">
            <template #error><el-icon :size="40"><Cpu /></el-icon></template>
          </el-avatar>
          <div class="detail-title">
            <h2>{{ selectedDevice.name }}</h2>
            <p>{{ selectedDevice.model }} | {{ selectedDevice.manufacturer }}</p>
            <el-tag :type="getStatusType(selectedDevice.status)" size="large">{{ selectedDevice.status.toUpperCase() }}</el-tag>
          </div>
        </div>

        <el-divider />

        <div class="detail-metrics">
          <h3>Real-Time Metrics</h3>
          <div class="metrics-grid">
            <div class="metric-card-detail">
              <span class="metric-label">Temperature</span>
              <span class="metric-value" :class="{ warning: selectedDevice.metrics.temperature > 28 }">
                {{ selectedDevice.metrics.temperature }}°C
              </span>
              <div class="metric-trend" :class="getTrendClass(selectedDevice.metrics.temperature, 28)">
                {{ getTrendIcon(selectedDevice.metrics.temperature, 28) }}
              </div>
            </div>
            <div class="metric-card-detail">
              <span class="metric-label">Humidity</span>
              <span class="metric-value" :class="{ warning: selectedDevice.metrics.humidity > 65 }">
                {{ selectedDevice.metrics.humidity }}%
              </span>
            </div>
            <div class="metric-card-detail">
              <span class="metric-label">Power</span>
              <span class="metric-value" :class="{ warning: selectedDevice.metrics.power > 20 }">
                {{ selectedDevice.metrics.power }} kW
              </span>
            </div>
            <div class="metric-card-detail">
              <span class="metric-label">Efficiency</span>
              <span class="metric-value" :class="{ warning: selectedDevice.metrics.efficiency < 80 }">
                {{ selectedDevice.metrics.efficiency }}%
              </span>
            </div>
          </div>
        </div>

        <el-divider />

        <div class="detail-info">
          <h3>Device Information</h3>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="Serial Number">{{ selectedDevice.serialNumber }}</el-descriptions-item>
            <el-descriptions-item label="System Type">{{ getSystemLabel(selectedDevice.systemType) }}</el-descriptions-item>
            <el-descriptions-item label="Area">{{ selectedDevice.area }}</el-descriptions-item>
            <el-descriptions-item label="Floor">{{ selectedDevice.floor }}</el-descriptions-item>
            <el-descriptions-item label="Installation Date">{{ formatDate(selectedDevice.installationDate) }}</el-descriptions-item>
            <el-descriptions-item label="Last Maintenance">{{ formatDate(selectedDevice.lastMaintenance) }}</el-descriptions-item>
            <el-descriptions-item label="Next Maintenance">{{ formatDate(selectedDevice.nextMaintenance) }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="detail-actions">
          <el-button type="primary" :icon="Switch" @click="controlDevice(selectedDevice)">Control Device</el-button>
          <el-button :icon="Tools" @click="createWorkOrder(selectedDevice)">Work Order</el-button>
        </div>
      </div>
    </el-drawer>

    <!-- 实时告警列表 -->
    <div class="alerts-panel" v-if="activeAlerts.length > 0">
      <div class="alerts-header">
        <h3><el-icon><BellFilled /></el-icon> Active Alerts ({{ activeAlerts.length }})</h3>
        <el-button size="small" text @click="clearAlerts">Clear All</el-button>
      </div>
      <div class="alerts-list">
        <div v-for="alert in activeAlerts" :key="alert.id" class="alert-item" :class="alert.severity">
          <div class="alert-icon">
            <el-icon v-if="alert.severity === 'critical'"><CircleCloseFilled /></el-icon>
            <el-icon v-else-if="alert.severity === 'warning'"><WarningFilled /></el-icon>
            <el-icon v-else><InfoFilled /></el-icon>
          </div>
          <div class="alert-content">
            <div class="alert-title">{{ alert.title }}</div>
            <div class="alert-message">{{ alert.message }}</div>
            <div class="alert-time">{{ formatTime(alert.timestamp) }}</div>
          </div>
          <div class="alert-actions">
            <el-button size="small" text @click="acknowledgeAlert(alert)">Acknowledge</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Search, Refresh, BellFilled, Grid, List, CircleCheckFilled,
  WarningFilled, CircleCloseFilled, RemoveFilled, Cpu, Switch, Tools,
  ColdDrink, Sunny, Odometer, MagicStick, Lock, Bell, InfoFilled
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Connecting to data stream...')
const router = useRouter()
const loadingMessages = ['Initializing...', 'Connecting to devices...', 'Loading real-time data...', 'Almost ready...']

// ==================== State ====================
const refreshing = ref(false)
const searchKeyword = ref('')
const filterSystem = ref('')
const filterStatus = ref('')
const filterArea = ref('')
const viewMode = ref<'grid' | 'list'>('grid')
const autoRefresh = ref(true)
const wsConnected = ref(true)
const selectedDevice = ref<any>(null)
const detailDrawerVisible = ref(false)
let refreshTimer: number
let ws: WebSocket | null = null

// ==================== Data ====================
interface Device {
  id: string
  name: string
  model: string
  manufacturer: string
  serialNumber: string
  systemType: string
  area: string
  floor: string
  status: 'online' | 'offline' | 'warning' | 'error'
  imageUrl: string
  metrics: {
    temperature: number
    humidity: number
    power: number
    energy: number
    efficiency: number
  }
  lastUpdate: string
  lastMaintenance: string
  nextMaintenance: string
  installationDate: string
}

interface Alert {
  id: string
  deviceId: string
  deviceName: string
  severity: 'critical' | 'warning' | 'info'
  title: string
  message: string
  timestamp: string
}

const devices = ref<Device[]>([])
const activeAlerts = ref<Alert[]>([])

// 统计数据
const stats = computed(() => {
  const online = devices.value.filter(d => d.status === 'online').length
  const warning = devices.value.filter(d => d.status === 'warning').length
  const error = devices.value.filter(d => d.status === 'error').length
  const offline = devices.value.filter(d => d.status === 'offline').length
  return { online, warning, error, offline, onlineChange: '+2', warningChange: '+1', errorChange: '-1', offlineChange: '-2' }
})

const areas = computed(() => {
  const areaSet = new Set<string>()
  devices.value.forEach(d => areaSet.add(d.area))
  return Array.from(areaSet).sort()
})

const filteredDevices = computed(() => {
  let result = [...devices.value]
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    result = result.filter(d => d.name.toLowerCase().includes(kw) || d.model.toLowerCase().includes(kw) || d.serialNumber.toLowerCase().includes(kw))
  }
  if (filterSystem.value) result = result.filter(d => d.systemType === filterSystem.value)
  if (filterStatus.value) result = result.filter(d => d.status === filterStatus.value)
  if (filterArea.value) result = result.filter(d => d.area === filterArea.value)
  return result
})

// ==================== Mock Data ====================
const generateMockDevices = (): Device[] => {
  const now = new Date()
  return [
    { id: '1', name: 'AHU-B2-01 Air Handler', model: 'Carrier 39G', manufacturer: 'Carrier', serialNumber: 'CA-2024-B201', systemType: 'hvac', area: 'Basement B2', floor: 'B2', status: 'online', imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567.webp', metrics: { temperature: 23.5, humidity: 55, power: 18.5, energy: 15200, efficiency: 94 }, lastUpdate: now.toISOString(), lastMaintenance: '2026-04-15', nextMaintenance: '2026-07-15', installationDate: '2024-01-10' },
    { id: '2', name: 'FCU-B2-01 Fan Coil', model: 'Daikin FXMQ', manufacturer: 'Daikin', serialNumber: 'DK-2024-B201', systemType: 'hvac', area: 'Basement B2', floor: 'B2', status: 'online', imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/52013141234431.webp', metrics: { temperature: 22.8, humidity: 48, power: 6.8, energy: 5400, efficiency: 91 }, lastUpdate: now.toISOString(), lastMaintenance: '2026-05-01', nextMaintenance: '2026-08-01', installationDate: '2024-02-15' },
    { id: '3', name: 'CH-B2-01 Chiller', model: 'Carrier AquaEdge', manufacturer: 'Carrier', serialNumber: 'CA-2024-B202', systemType: 'hvac', area: 'Basement B2', floor: 'B2', status: 'warning', imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/52013145678.jpg', metrics: { temperature: 28.5, humidity: 65, power: 85.0, energy: 68000, efficiency: 88 }, lastUpdate: now.toISOString(), lastMaintenance: '2026-04-10', nextMaintenance: '2026-07-10', installationDate: '2024-01-05' },
    { id: '4', name: 'EF-B2-02 Exhaust Fan', model: 'Greenheck CUBE', manufacturer: 'Greenheck', serialNumber: 'GH-2024-B202', systemType: 'hvac', area: 'Basement B2', floor: 'B2', status: 'error', imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/520131452044.webp', metrics: { temperature: 32.0, humidity: 58, power: 8.2, energy: 6560, efficiency: 76 }, lastUpdate: now.toISOString(), lastMaintenance: '2026-03-15', nextMaintenance: '2026-06-15', installationDate: '2024-01-25' },
    { id: '5', name: 'AHU-2F-01 Air Handler', model: 'Trane IntelliPak', manufacturer: 'Trane', serialNumber: 'TR-2024-2F01', systemType: 'hvac', area: 'Office 2F', floor: '2F', status: 'error', imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567.webp', metrics: { temperature: 31.2, humidity: 72, power: 22.5, energy: 18500, efficiency: 72 }, lastUpdate: now.toISOString(), lastMaintenance: '2024-02-28', nextMaintenance: '2026-04-28', installationDate: '2023-08-10' },
    { id: '6', name: 'LIGHT-B2-01 Controller', model: 'Philips Dynalite', manufacturer: 'Philips', serialNumber: 'PH-2024-B201', systemType: 'lighting', area: 'Basement B2', floor: 'B2', status: 'online', imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp', metrics: { temperature: 26.5, humidity: 42, power: 4.2, energy: 3200, efficiency: 96 }, lastUpdate: now.toISOString(), lastMaintenance: '2026-05-15', nextMaintenance: '2026-08-15', installationDate: '2024-01-20' },
    { id: '7', name: 'ACS-1F-01 Entrance', model: 'HID VertX', manufacturer: 'HID Global', serialNumber: 'HD-2024-1F01', systemType: 'sas', area: 'Lobby 1F', floor: '1F', status: 'online', imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/52013147643.jpg', metrics: { temperature: 35.0, humidity: 40, power: 0.5, energy: 400, efficiency: 99 }, lastUpdate: now.toISOString(), lastMaintenance: '2026-06-01', nextMaintenance: '2026-09-01', installationDate: '2024-01-05' },
    { id: '8', name: 'SD-1F-01 Smoke Detector', model: 'Honeywell XLS', manufacturer: 'Honeywell', serialNumber: 'HW-2024-1F01', systemType: 'fas', area: 'Lobby 1F', floor: '1F', status: 'online', imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567123.jpg', metrics: { temperature: 22.0, humidity: 55, power: 0.3, energy: 240, efficiency: 99 }, lastUpdate: now.toISOString(), lastMaintenance: '2026-04-10', nextMaintenance: '2026-07-10', installationDate: '2024-01-01' },
    { id: '9', name: 'PUMP-B2-02 Booster', model: 'Grundfos CR', manufacturer: 'Grundfos', serialNumber: 'GF-2024-B202', systemType: 'plumbing', area: 'Basement B2', floor: 'B2', status: 'warning', imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png', metrics: { temperature: 38.0, humidity: 72, power: 9.5, energy: 7600, efficiency: 76 }, lastUpdate: now.toISOString(), lastMaintenance: '2024-02-28', nextMaintenance: '2026-04-28', installationDate: '2023-11-20' }
  ]
}

const generateMockAlerts = (): Alert[] => {
  return [
    { id: '1', deviceId: '4', deviceName: 'EF-B2-02 Exhaust Fan', severity: 'critical', title: 'High Temperature', message: 'Temperature has exceeded 30°C threshold', timestamp: new Date().toISOString() },
    { id: '2', deviceId: '9', deviceName: 'PUMP-B2-02 Booster', severity: 'warning', title: 'Efficiency Drop', message: 'Efficiency dropped below 80%', timestamp: new Date(Date.now() - 5 * 60000).toISOString() },
    { id: '3', deviceId: '5', deviceName: 'AHU-2F-01 Air Handler', severity: 'critical', title: 'Device Error', message: 'Device reported critical error state', timestamp: new Date(Date.now() - 15 * 60000).toISOString() }
  ]
}

// ==================== Helper Functions ====================
const getSystemIcon = (type: string) => {
  const icons: Record<string, any> = { hvac: ColdDrink, lighting: Sunny, sas: Lock, fas: Bell, plumbing: MagicStick }
  return icons[type] || Cpu
}

const getSystemLabel = (type: string) => {
  const labels: Record<string, string> = { hvac: 'HVAC', lighting: 'Lighting', sas: 'Security', fas: 'Fire Alarm', plumbing: 'Plumbing' }
  return labels[type] || type
}

const getSystemTagType = (type: string) => {
  const types: Record<string, string> = { hvac: 'primary', lighting: 'success', sas: 'danger', fas: 'warning', plumbing: 'info' }
  return types[type] || 'info'
}

const getStatusType = (status: string) => {
  const types: Record<string, string> = { online: 'success', offline: 'info', warning: 'warning', error: 'danger' }
  return types[status] || 'info'
}

const getTrendClass = (value: number, threshold: number) => value > threshold ? 'trend-up' : 'trend-down'
const getTrendIcon = (value: number, threshold: number) => value > threshold ? '↑' : '↓'

const formatTime = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

const formatDateTime = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

// ==================== Data Functions ====================
const loadDevices = () => {
  devices.value = generateMockDevices()
}

const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 500))
  devices.value = generateMockDevices()
  activeAlerts.value = generateMockAlerts()
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

const startRealtimeUpdates = () => {
  if (refreshTimer) clearInterval(refreshTimer)
  refreshTimer = window.setInterval(() => {
    if (autoRefresh.value) {
      devices.value = devices.value.map(device => ({
        ...device,
        metrics: {
          ...device.metrics,
          temperature: +(device.metrics.temperature + (Math.random() - 0.5) * 0.3).toFixed(1),
          power: +(device.metrics.power + (Math.random() - 0.5) * 0.5).toFixed(1)
        },
        lastUpdate: new Date().toISOString()
      }))

      // Randomly generate alerts
      if (Math.random() < 0.1) {
        const randomDevice = devices.value[Math.floor(Math.random() * devices.value.length)]
        activeAlerts.value.unshift({
          id: Date.now().toString(),
          deviceId: randomDevice.id,
          deviceName: randomDevice.name,
          severity: Math.random() > 0.7 ? 'critical' : 'warning',
          title: 'Abnormal Reading',
          message: `${randomDevice.name} reported unusual metrics`,
          timestamp: new Date().toISOString()
        })
        if (activeAlerts.value.length > 20) activeAlerts.value.pop()
      }
    }
  }, 5000)
}

// ==================== Actions ====================
const selectDevice = (device: Device) => {
  selectedDevice.value = device
  detailDrawerVisible.value = true
}

const viewDetails = (device: Device) => {
  router.push(`/systems-devices/device-inventory/device-details/${device.id}`)
}

const controlDevice = (device: Device) => {
  ElMessage.info(`Opening control panel for ${device.name}`)
}

const createWorkOrder = (device: Device) => {
  ElMessage.info(`Creating work order for ${device.name}`)
}

const openAlertSettings = () => {
  ElMessage.info('Opening alert settings')
}

const acknowledgeAlert = (alert: Alert) => {
  activeAlerts.value = activeAlerts.value.filter(a => a.id !== alert.id)
  ElMessage.success(`Alert acknowledged: ${alert.title}`)
}

const clearAlerts = () => {
  activeAlerts.value = []
  ElMessage.success('All alerts cleared')
}

// ==================== Lifecycle ====================
onMounted(() => {
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

  setTimeout(() => {
    clearInterval(msgInt)
    clearInterval(progInt)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      loadDevices()
      activeAlerts.value = generateMockAlerts()
      startRealtimeUpdates()
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
})

watch(autoRefresh, (val) => {
  if (val && !refreshTimer) startRealtimeUpdates()
})
</script>

<style scoped>
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
.loading-overlay { position: relative; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; backdrop-filter: blur(2px); }
.loading-content { text-align: center; padding: 40px; border-radius: 32px; background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(20px); border: 1px solid rgba(59, 130, 246, 0.3); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); animation: fadeInUp 0.6s ease-out; }
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

.real-time-status-page { padding: 20px; background: #f5f7fa; min-height: 100%; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }
.header-right { display: flex; align-items: center; gap: 16px; }
.connection-status { display: flex; align-items: center; gap: 8px; font-size: 13px; padding: 6px 12px; background: white; border-radius: 20px; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; }
.status-dot.online { background: #10b981; box-shadow: 0 0 6px #10b981; }
.status-dot.offline { background: #ef4444; animation: pulse 1s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }

.stats-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 24px; }
.stat-card { background: white; border-radius: 16px; padding: 20px; display: flex; align-items: center; justify-content: space-between; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
.stat-card.online .stat-icon .el-icon { color: #10b981; }
.stat-card.warning .stat-icon .el-icon { color: #f59e0b; }
.stat-card.error .stat-icon .el-icon { color: #ef4444; }
.stat-card.offline .stat-icon .el-icon { color: #6b7280; }
.stat-icon .el-icon { font-size: 32px; }
.stat-info { text-align: center; }
.stat-value { font-size: 28px; font-weight: 700; color: #1e293b; }
.stat-label { font-size: 13px; color: #64748b; }
.stat-trend { font-size: 13px; font-weight: 500; }

.filter-bar { display: flex; justify-content: space-between; align-items: center; background: white; padding: 16px 20px; border-radius: 12px; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.filter-left { display: flex; gap: 12px; flex-wrap: wrap; }
.filter-right { display: flex; gap: 16px; align-items: center; }

.device-grid { min-height: 400px; }
.grid-container { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }
.device-card { background: white; border-radius: 16px; overflow: hidden; cursor: pointer; transition: all 0.3s ease; border: 2px solid transparent; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.device-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); }
.device-card.selected { border-color: #3b82f6; background: #eff6ff; }
.device-card.status-online { border-left: 4px solid #10b981; }
.device-card.status-warning { border-left: 4px solid #f59e0b; }
.device-card.status-error { border-left: 4px solid #ef4444; background: #fef2f2; }
.device-card.status-offline { border-left: 4px solid #6b7280; opacity: 0.7; }
.card-header { display: flex; justify-content: space-between; align-items: center; padding: 16px; background: #f8fafc; }
.device-icon .el-icon { font-size: 24px; color: #3b82f6; }
.device-status { display: flex; align-items: center; gap: 6px; }
.status-dot.online { background: #10b981; width: 8px; height: 8px; border-radius: 50%; }
.status-dot.warning { background: #f59e0b; width: 8px; height: 8px; border-radius: 50%; animation: pulse 2s infinite; }
.status-dot.error { background: #ef4444; width: 8px; height: 8px; border-radius: 50%; animation: pulse 1s infinite; }
.status-dot.offline { background: #6b7280; width: 8px; height: 8px; border-radius: 50%; }
.status-text { font-size: 11px; font-weight: 600; }
.card-body { padding: 16px; }
.device-name { margin: 0 0 4px 0; font-size: 16px; font-weight: 600; color: #1e293b; }
.device-model { font-size: 12px; color: #64748b; margin: 0 0 4px 0; }
.device-location { font-size: 11px; color: #94a3b8; margin: 0; }
.card-metrics { display: flex; justify-content: space-around; padding: 12px 16px; background: #f8fafc; border-top: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; }
.metric { text-align: center; }
.metric-label { display: block; font-size: 10px; color: #64748b; }
.metric-value { font-size: 14px; font-weight: 600; color: #1e293b; }
.metric-value.warning { color: #f59e0b; }
.card-footer { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; }
.last-update { font-size: 10px; color: #94a3b8; }

.device-list { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.device-cell { display: flex; align-items: center; gap: 12px; }
.device-info { display: flex; flex-direction: column; }
.device-name { font-weight: 600; color: #1e293b; }
.device-model { font-size: 11px; color: #64748b; }
.status-cell { display: flex; align-items: center; gap: 6px; }
.text-warning { color: #f59e0b; font-weight: 500; }
.text-danger { color: #ef4444; font-weight: 500; }

.empty-state { padding: 60px; text-align: center; }

.alerts-panel { position: fixed; bottom: 20px; right: 20px; width: 380px; background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); z-index: 100; overflow: hidden; }
.alerts-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; }
.alerts-header h3 { display: flex; align-items: center; gap: 8px; margin: 0; font-size: 14px; }
.alerts-list { max-height: 300px; overflow-y: auto; }
.alert-item { display: flex; align-items: flex-start; gap: 12px; padding: 12px 16px; border-bottom: 1px solid #e2e8f0; transition: background 0.2s; }
.alert-item:hover { background: #f8fafc; }
.alert-item.critical { border-left: 3px solid #ef4444; }
.alert-item.warning { border-left: 3px solid #f59e0b; }
.alert-item.info { border-left: 3px solid #3b82f6; }
.alert-icon .el-icon { font-size: 18px; }
.alert-item.critical .alert-icon .el-icon { color: #ef4444; }
.alert-item.warning .alert-icon .el-icon { color: #f59e0b; }
.alert-content { flex: 1; }
.alert-title { font-size: 13px; font-weight: 600; color: #1e293b; }
.alert-message { font-size: 12px; color: #64748b; margin-top: 2px; }
.alert-time { font-size: 10px; color: #94a3b8; margin-top: 4px; }
.alert-actions { display: flex; gap: 8px; }

.device-detail { padding: 8px; }
.detail-header { display: flex; gap: 20px; margin-bottom: 20px; }
.detail-title h2 { margin: 0 0 4px 0; font-size: 20px; }
.detail-title p { margin: 0 0 8px 0; color: #64748b; font-size: 13px; }
.metrics-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.metric-card-detail { background: #f8fafc; border-radius: 12px; padding: 16px; text-align: center; }
.metric-card-detail .metric-label { font-size: 12px; color: #64748b; display: block; margin-bottom: 8px; }
.metric-card-detail .metric-value { font-size: 24px; font-weight: 700; }
.metric-card-detail .metric-value.warning { color: #f59e0b; }
.metric-trend { font-size: 16px; margin-top: 4px; }
.metric-trend.trend-up { color: #ef4444; }
.metric-trend.trend-down { color: #10b981; }
.detail-actions { display: flex; gap: 12px; margin-top: 24px; }

@media (max-width: 1024px) { .stats-cards { grid-template-columns: repeat(2, 1fr); } .alerts-panel { width: 320px; } }
@media (max-width: 768px) { .stats-cards { grid-template-columns: 1fr; } .filter-bar { flex-direction: column; } .filter-left { width: 100%; } .filter-left .el-input, .filter-left .el-select { flex: 1; } .grid-container { grid-template-columns: 1fr; } .alerts-panel { left: 20px; right: 20px; width: auto; } }
</style>