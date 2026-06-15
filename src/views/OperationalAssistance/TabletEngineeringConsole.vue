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
          <span class="loading-title">Loading Tablet Engineering Console</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">IBMS Mobile Engineering & Field Operations Platform</div>
      </div>
    </div>
  </div>

  <!-- Main Content - Optimized for Tablet (1024x768) -->
  <div v-else class="tablet-console-container">
    <!-- Top Status Bar -->
    <div class="status-bar">
      <div class="status-left">
        <el-icon class="brand-icon"><Cpu /></el-icon>
        <span class="brand-name">IBMS Engineering Console</span>
        <el-badge :value="syncStatus" :type="syncStatus === 'Synced' ? 'success' : 'warning'" class="sync-badge">
          <el-icon><Connection /></el-icon>
          <span>{{ syncStatus }}</span>
        </el-badge>
      </div>
      <div class="status-right">
        <span class="time">{{ currentTime }}</span>
        <span class="date">{{ currentDate }}</span>
        <el-avatar :size="32" :icon="UserFilled" class="user-avatar" />
        <span class="user-name">{{ engineerName }}</span>
        <el-dropdown @command="handleMenuCommand">
          <el-icon class="menu-icon"><MoreFilled /></el-icon>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">Profile</el-dropdown-item>
              <el-dropdown-item command="settings">Settings</el-dropdown-item>
              <el-dropdown-item command="help">Help</el-dropdown-item>
              <el-dropdown-item divided command="logout">Logout</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- Main Grid - Tablet Optimized Layout -->
    <div class="console-grid">
      <!-- Left Column - Site Overview & Maps -->
      <div class="left-column">
        <!-- Site Selector -->
        <el-card class="site-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Location /></el-icon> Current Site</span>
              <el-select v-model="currentSite" size="small" @change="onSiteChange">
                <el-option label="Data Center A - Singapore" value="dc_sg" />
                <el-option label="Data Center B - London" value="dc_ldn" />
                <el-option label="Office Tower - New York" value="office_ny" />
                <el-option label="Industrial Park - Shanghai" value="industrial_sh" />
              </el-select>
            </div>
          </template>
          <div class="site-info">
            <div class="site-stats">
              <div class="stat-item">
                <div class="stat-value">{{ siteStats.devicesOnline }}</div>
                <div class="stat-label">Devices Online</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ siteStats.activeAlarms }}</div>
                <div class="stat-label">Active Alarms</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ siteStats.openWorkOrders }}</div>
                <div class="stat-label">Work Orders</div>
              </div>
            </div>
            <div class="site-map">
              <div ref="mapChartRef" class="map-chart"></div>
            </div>
          </div>
        </el-card>

        <!-- Device List -->
        <el-card class="device-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Monitor /></el-icon> Nearby Devices</span>
              <el-input v-model="deviceSearch" placeholder="Search devices..." size="small" style="width: 180px">
                <template #prefix><el-icon><Search /></el-icon></template>
              </el-input>
            </div>
          </template>
          <div class="device-list">
            <div v-for="device in filteredDevices" :key="device.id" class="device-item" @click="selectDevice(device)">
              <div class="device-icon" :class="device.status">
                <el-icon><Cpu /></el-icon>
              </div>
              <div class="device-info">
                <div class="device-name">{{ device.name }}</div>
                <div class="device-location">{{ device.location }}</div>
              </div>
              <div class="device-status">
                <el-tag :type="device.status === 'online' ? 'success' : device.status === 'warning' ? 'warning' : 'danger'" size="small">
                  {{ device.status }}
                </el-tag>
              </div>
              <el-button type="primary" size="small" plain @click.stop="viewDeviceDetails(device)">
                Details
              </el-button>
            </div>
          </div>
        </el-card>
      </div>

      <!-- Center Column - Engineering Dashboard -->
      <div class="center-column">
        <!-- Quick Actions Toolbar -->
        <el-card class="actions-card" shadow="hover">
          <div class="quick-actions">
            <div class="action-btn" @click="scanQRCode">
              <el-icon><Camera /></el-icon>
              <span>Scan QR</span>
            </div>
            <div class="action-btn" @click="quickDiagnostics">
              <el-icon><DataAnalysis /></el-icon>
              <span>Diagnostics</span>
            </div>
            <div class="action-btn" @click="createWorkOrder">
              <el-icon><Document /></el-icon>
              <span>Work Order</span>
            </div>
            <div class="action-btn" @click="viewMaintenanceSchedule">
              <el-icon><Calendar /></el-icon>
              <span>Schedule</span>
            </div>
            <div class="action-btn" @click="emergencyMode">
              <el-icon><Warning /></el-icon>
              <span>Emergency</span>
            </div>
            <div class="action-btn" @click="callSupport">
              <el-icon><Headset /></el-icon>
              <span>Support</span>
            </div>
          </div>
        </el-card>

        <!-- Real-time Telemetry Chart -->
        <el-card class="telemetry-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><TrendCharts /></el-icon> Real-time Telemetry</span>
              <div class="telemetry-controls">
                <el-radio-group v-model="telemetryMetric" size="small" @change="updateTelemetryChart">
                  <el-radio-button label="temperature">Temperature</el-radio-button>
                  <el-radio-button label="humidity">Humidity</el-radio-button>
                  <el-radio-button label="power">Power (kW)</el-radio-button>
                </el-radio-group>
                <el-select v-model="selectedDevice" size="small" placeholder="Select device" style="width: 140px">
                  <el-option label="Chiller 1" value="chiller_1" />
                  <el-option label="Chiller 2" value="chiller_2" />
                  <el-option label="AHU 1" value="ahu_1" />
                  <el-option label="UPS 1" value="ups_1" />
                </el-select>
              </div>
            </div>
          </template>
          <div ref="telemetryChartRef" class="telemetry-chart"></div>
        </el-card>

        <!-- Active Alerts -->
        <el-card class="alerts-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><BellFilled /></el-icon> Active Alerts</span>
              <el-button text type="primary" @click="viewAllAlerts">View All</el-button>
            </div>
          </template>
          <div class="alerts-list">
            <div v-for="alert in activeAlerts" :key="alert.id" :class="['alert-item', alert.severity]">
              <div class="alert-icon">
                <el-icon><WarningFilled /></el-icon>
              </div>
              <div class="alert-info">
                <div class="alert-title">{{ alert.title }}</div>
                <div class="alert-detail">{{ alert.detail }}</div>
                <div class="alert-time">{{ alert.time }}</div>
              </div>
              <el-button size="small" type="primary" plain @click="acknowledgeAlert(alert)">
                Acknowledge
              </el-button>
            </div>
          </div>
        </el-card>
      </div>

      <!-- Right Column - Engineering Tools -->
      <div class="right-column">
        <!-- Active Work Orders -->
        <el-card class="workorders-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Document /></el-icon> My Work Orders</span>
              <el-badge :value="pendingWorkOrders.length" type="danger">
                <el-button text type="primary" @click="viewAllWorkOrders">View All</el-button>
              </el-badge>
            </div>
          </template>
          <div class="workorders-list">
            <div v-for="wo in pendingWorkOrders" :key="wo.id" class="workorder-item" @click="viewWorkOrder(wo)">
              <div class="wo-priority" :class="wo.priority">
                {{ wo.priority }}
              </div>
              <div class="wo-info">
                <div class="wo-title">{{ wo.title }}</div>
                <div class="wo-location">{{ wo.location }}</div>
              </div>
              <div class="wo-status">
                <el-progress :percentage="wo.progress" :stroke-width="4" :show-text="false" />
                <span class="wo-progress">{{ wo.progress }}%</span>
              </div>
            </div>
          </div>
        </el-card>

        <!-- Equipment Status -->
        <el-card class="equipment-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><DataBoard /></el-icon> Equipment Health</span>
              <el-button text type="primary" size="small" @click="refreshEquipmentStatus">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="equipment-stats">
            <div v-for="eq in equipmentHealth" :key="eq.name" class="equipment-item">
              <div class="eq-name">{{ eq.name }}</div>
              <el-progress :percentage="eq.health" :color="getHealthColor(eq.health)" :stroke-width="8" />
              <div class="eq-status">{{ eq.status }}</div>
            </div>
          </div>
        </el-card>

        <!-- Engineering Notes -->
        <el-card class="notes-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Edit /></el-icon> Engineering Notes</span>
              <el-button text type="primary" @click="addNote">+ Add</el-button>
            </div>
          </template>
          <div class="notes-list">
            <div v-for="note in engineeringNotes" :key="note.id" class="note-item">
              <div class="note-text">{{ note.text }}</div>
              <div class="note-meta">{{ note.author }} · {{ note.time }}</div>
            </div>
          </div>
        </el-card>

        <!-- Battery Level & Device Info -->
        <el-card class="device-info-card" shadow="hover">
          <div class="device-info-content">
            <div class="battery-section">
              <el-icon><Menu /></el-icon>
              <span>Tablet Battery: {{ batteryLevel }}%</span>
              <el-progress :percentage="batteryLevel" :stroke-width="6" :color="getBatteryColor(batteryLevel)" />
            </div>
            <div class="connection-info">
              <el-icon><Connection /></el-icon>
              <span>Signal: {{ signalStrength }}</span>
              <el-progress :percentage="signalStrength" :stroke-width="6" :show-text="false" />
            </div>
            <div class="last-sync">
              <el-icon><Timer /></el-icon>
              <span>Last Sync: {{ lastSyncTime }}</span>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Cpu, Connection, UserFilled, MoreFilled, Location, Monitor, Search, Camera,
  DataAnalysis, Document, Calendar, Warning, Headset, TrendCharts, BellFilled,
  WarningFilled, DataBoard, Refresh, Edit, Timer, ArrowRight, Menu,
  Tools, Setting, InfoFilled
} from '@element-plus/icons-vue'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Initializing Tablet Console...')

const loadingMessages = [
  'Initializing Tablet Console...',
  'Connecting to IBMS server...',
  'Loading site data...',
  'Ready for field operations!'
]

// Time and user
const currentTime = ref('')
const currentDate = ref('')
const engineerName = ref('Michael Chen')
const syncStatus = ref('Synced')
let timeInterval: number

// Site data
const currentSite = ref('dc_sg')
const siteStats = ref({
  devicesOnline: 124,
  activeAlarms: 8,
  openWorkOrders: 12
})

// Devices
const deviceSearch = ref('')
const devices = ref([
  { id: 1, name: 'Chiller System A', location: 'Basement Mechanical Room', status: 'online' },
  { id: 2, name: 'AHU-101', location: 'Floor 1 Air Handler Room', status: 'online' },
  { id: 3, name: 'UPS System #2', location: 'Data Hall A', status: 'warning' },
  { id: 4, name: 'Fire Alarm Panel', location: 'Security Center', status: 'online' },
  { id: 5, name: 'Cooling Tower CT-1', location: 'Rooftop', status: 'offline' },
  { id: 6, name: 'Lighting Controller L-12', location: 'Office Area', status: 'online' },
  { id: 7, name: 'VFD-202', location: 'HVAC Plant Room', status: 'warning' },
  { id: 8, name: 'BACnet Router', location: 'Server Room', status: 'online' }
])

const filteredDevices = computed(() => {
  if (!deviceSearch.value) return devices.value
  return devices.value.filter(d =>
      d.name.toLowerCase().includes(deviceSearch.value.toLowerCase()) ||
      d.location.toLowerCase().includes(deviceSearch.value.toLowerCase())
  )
})

// Telemetry
const telemetryMetric = ref('temperature')
const selectedDevice = ref('chiller_1')
let telemetryChart: echarts.ECharts | null = null
let telemetryInterval: number

// Alerts
const activeAlerts = ref([
  { id: 1, severity: 'critical', title: 'High Temperature Alert', detail: 'Data Hall A temperature exceeded 28°C', time: '2 min ago' },
  { id: 2, severity: 'warning', title: 'UPS Battery Low', detail: 'UPS #2 battery capacity below 20%', time: '15 min ago' },
  { id: 3, severity: 'info', title: 'Scheduled Maintenance', detail: 'Chiller maintenance due in 2 hours', time: '1 hour ago' },
  { id: 4, severity: 'warning', title: 'Network Latency', detail: 'BACnet response time increased', time: '2 hours ago' }
])

// Work orders
const pendingWorkOrders = ref([
  { id: 101, title: 'Chiller #1 Inspection', location: 'Chiller Plant Room', priority: 'high', progress: 75 },
  { id: 102, title: 'AHU Filter Replacement', location: 'Floor 3 AHU Room', priority: 'medium', progress: 30 },
  { id: 103, title: 'UPS Diagnostic Test', location: 'Data Hall B', priority: 'high', progress: 10 },
  { id: 104, title: 'Fire Alarm System Check', location: 'All Floors', priority: 'low', progress: 50 }
])

// Equipment health
const equipmentHealth = ref([
  { name: 'Chiller System', health: 92, status: 'Good' },
  { name: 'UPS Units', health: 78, status: 'Warning' },
  { name: 'HVAC System', health: 85, status: 'Good' },
  { name: 'Fire Safety', health: 96, status: 'Excellent' },
  { name: 'Lighting Control', health: 88, status: 'Good' },
  { name: 'Security System', health: 94, status: 'Good' }
])

// Engineering notes
const engineeringNotes = ref([
  { id: 1, text: 'Replaced faulty temperature sensor on Chiller #2', author: 'Michael C.', time: '10:30 AM' },
  { id: 2, text: 'Schedule UPS battery replacement for next week', author: 'Sarah L.', time: 'Yesterday' },
  { id: 3, text: 'AHU-101 airflow calibration completed', author: 'James W.', time: 'Yesterday' }
])

// Device info
const batteryLevel = ref(87)
const signalStrength = ref(94)
const lastSyncTime = ref('Just now')

// Chart refs
const mapChartRef = ref<HTMLElement>()
const telemetryChartRef = ref<HTMLElement>()
let mapChart: echarts.ECharts | null = null

// Update time
const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
  currentDate.value = now.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

// Initialize map chart
const initMapChart = () => {
  if (!mapChartRef.value) return
  mapChart = echarts.init(mapChartRef.value)
  const option = {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'scatter',
      symbolSize: 12,
      data: [
        { value: [20, 30], name: 'Chiller Plant', itemStyle: { color: '#3b82f6' } },
        { value: [50, 25], name: 'Data Hall A', itemStyle: { color: '#10b981' } },
        { value: [70, 60], name: 'UPS Room', itemStyle: { color: '#f59e0b' } },
        { value: [30, 70], name: 'Security Center', itemStyle: { color: '#8b5cf6' } },
        { value: [80, 85], name: 'Office Area', itemStyle: { color: '#ec489a' } },
        { value: [45, 90], name: 'Generator Room', itemStyle: { color: '#ef4444' } }
      ],
      label: { show: true, formatter: '{b}', position: 'right', offset: [5, 0] }
    }],
    xAxis: { show: false, min: 0, max: 100 },
    yAxis: { show: false, min: 0, max: 100 },
    grid: { left: 0, top: 0, right: 0, bottom: 0, containLabel: true },
    backgroundColor: 'transparent'
  }
  mapChart.setOption(option)
}

// Initialize telemetry chart
const initTelemetryChart = () => {
  if (!telemetryChartRef.value) return
  telemetryChart = echarts.init(telemetryChartRef.value)
  updateTelemetryChart()
}

const updateTelemetryChart = () => {
  if (!telemetryChart) return

  const data = generateTelemetryData()
  const option = {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: data.times, name: 'Time' },
    yAxis: { type: 'value', name: getMetricUnit() },
    series: [{
      name: telemetryMetric.value,
      type: 'line',
      smooth: true,
      data: data.values,
      lineStyle: { width: 3, color: '#3b82f6' },
      areaStyle: { opacity: 0.3, color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#3b82f6' }, { offset: 1, color: '#93c5fd' }
        ]) },
      symbol: 'circle',
      symbolSize: 6
    }]
  }
  telemetryChart.setOption(option)
}

const generateTelemetryData = () => {
  const times = ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00']
  let values: number[] = []

  if (telemetryMetric.value === 'temperature') {
    values = [22.5, 22.8, 23.0, 23.2, 23.5, 24.0, 24.2, 24.5, 24.3, 23.8, 23.2, 22.8]
  } else if (telemetryMetric.value === 'humidity') {
    values = [55, 54, 53, 52, 51, 50, 49, 48, 49, 50, 52, 54]
  } else {
    values = [120, 118, 125, 135, 145, 142, 138, 140, 145, 150, 148, 135]
  }

  return { times, values }
}

const getMetricUnit = () => {
  switch (telemetryMetric.value) {
    case 'temperature': return 'Temperature (°C)'
    case 'humidity': return 'Humidity (%)'
    case 'power': return 'Power (kW)'
    default: return ''
  }
}

const simulateTelemetryUpdate = () => {
  if (!telemetryChart) return
  const data = generateTelemetryData()
  telemetryChart.setOption({ series: [{ data: data.values }] })
}

// Event handlers
const onSiteChange = () => {
  ElMessage.info(`Switched to site: ${currentSite.value}`)
  // Simulate site data refresh
  siteStats.value = {
    devicesOnline: Math.floor(Math.random() * 100) + 80,
    activeAlarms: Math.floor(Math.random() * 15),
    openWorkOrders: Math.floor(Math.random() * 20) + 5
  }
}

const selectDevice = (device: any) => {
  ElMessage.info(`Selected device: ${device.name}`)
}

const viewDeviceDetails = (device: any) => {
  ElMessageBox.alert(`Device: ${device.name}\nLocation: ${device.location}\nStatus: ${device.status}\nLast Maintenance: 2024-01-15\nFirmware Version: 2.1.0`, 'Device Details', {
    confirmButtonText: 'OK',
    type: 'info'
  })
}

const scanQRCode = () => {
  ElMessage.info('QR Code scanner ready - point camera at device QR code')
}

const quickDiagnostics = () => {
  ElMessage.info('Running system diagnostics...')
  setTimeout(() => {
    ElMessage.success('Diagnostics complete - All systems operational')
  }, 2000)
}

const createWorkOrder = () => {
  ElMessage.info('Create work order form will open')
}

const viewMaintenanceSchedule = () => {
  ElMessage.info('Maintenance schedule calendar')
}

const emergencyMode = () => {
  ElMessageBox.confirm('Emergency mode will activate all emergency protocols. Continue?', 'Emergency Mode', {
    confirmButtonText: 'Activate',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    ElMessage.warning('Emergency mode activated - All emergency systems online')
  }).catch(() => {})
}

const callSupport = () => {
  ElMessage.info('Connecting to support hotline...')
}

const acknowledgeAlert = (alert: any) => {
  activeAlerts.value = activeAlerts.value.filter(a => a.id !== alert.id)
  ElMessage.success(`Alert acknowledged: ${alert.title}`)
}

const viewAllAlerts = () => {
  ElMessage.info('Viewing all alerts')
}

const viewWorkOrder = (wo: any) => {
  ElMessage.info(`Opening work order: ${wo.title}`)
}

const viewAllWorkOrders = () => {
  ElMessage.info('Viewing all work orders')
}

const refreshEquipmentStatus = () => {
  ElMessage.info('Refreshing equipment status...')
  equipmentHealth.value.forEach(eq => {
    eq.health = Math.floor(Math.random() * 30) + 70
  })
}

const addNote = () => {
  ElMessageBox.prompt('Enter your engineering note', 'Add Note', {
    confirmButtonText: 'Add',
    cancelButtonText: 'Cancel'
  }).then(({ value }) => {
    if (value) {
      engineeringNotes.value.unshift({
        id: Date.now(),
        text: value,
        author: engineerName.value,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      })
      ElMessage.success('Note added')
    }
  }).catch(() => {})
}

const getHealthColor = (health: number) => {
  if (health >= 90) return '#10b981'
  if (health >= 70) return '#f59e0b'
  return '#ef4444'
}

const getBatteryColor = (level: number) => {
  if (level >= 50) return '#10b981'
  if (level >= 20) return '#f59e0b'
  return '#ef4444'
}

const handleMenuCommand = (cmd: string) => {
  ElMessage.info(`${cmd} menu clicked`)
}

// Loading animation
onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)

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
      setTimeout(() => {
        initMapChart()
        initTelemetryChart()
        telemetryInterval = setInterval(simulateTelemetryUpdate, 5000)
      }, 100)
    }, 400)
  }, 2500)
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
  if (telemetryInterval) clearInterval(telemetryInterval)
  if (telemetryChart) telemetryChart.dispose()
  if (mapChart) mapChart.dispose()
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
  font-size: 24px;
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

/* ==================== Main Content - Tablet Optimized ==================== */
.tablet-console-container {
  padding: 0;
  background: #f0f2f5;
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}

/* Status Bar */
.status-bar {
  background: white;
  padding: 12px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.status-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.brand-icon {
  font-size: 24px;
  color: #3b82f6;
}

.brand-name {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.sync-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.status-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.time {
  font-size: 18px;
  font-weight: 500;
  color: #1e293b;
}

.date {
  font-size: 14px;
  color: #64748b;
}

.user-avatar {
  background: #3b82f6;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
}

.menu-icon {
  font-size: 20px;
  cursor: pointer;
  color: #64748b;
}

/* Console Grid - Tablet Layout (1024px optimized) */
.console-grid {
  display: grid;
  grid-template-columns: 320px 1fr 320px;
  gap: 16px;
  padding: 20px;
}

/* Cards */
.site-card,
.device-card,
.actions-card,
.telemetry-card,
.alerts-card,
.workorders-card,
.equipment-card,
.notes-card,
.device-info-card {
  border-radius: 12px;
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #1e293b;
}

/* Site Card */
.site-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 16px;
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

.site-map {
  height: 160px;
}

.map-chart {
  width: 100%;
  height: 100%;
}

/* Device List */
.device-list {
  max-height: 320px;
  overflow-y: auto;
}

.device-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.device-item:hover {
  background: #f8fafc;
}

.device-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e2e8f0;
}

.device-icon.online {
  background: #dcfce7;
  color: #10b981;
}

.device-icon.warning {
  background: #fed7aa;
  color: #f59e0b;
}

.device-icon.offline {
  background: #fee2e2;
  color: #ef4444;
}

.device-info {
  flex: 1;
}

.device-name {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
}

.device-location {
  font-size: 11px;
  color: #64748b;
}

/* Quick Actions */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 8px;
  padding: 8px;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 12px 8px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  background: #f8fafc;
}

.action-btn:hover {
  background: #eef2ff;
  transform: translateY(-2px);
}

.action-btn .el-icon {
  font-size: 24px;
  color: #3b82f6;
}

.action-btn span {
  font-size: 11px;
  color: #475569;
}

/* Telemetry Chart */
.telemetry-controls {
  display: flex;
  gap: 12px;
}

.telemetry-chart {
  height: 250px;
  width: 100%;
}

/* Alerts */
.alerts-list {
  max-height: 260px;
  overflow-y: auto;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  background: #f8fafc;
}

.alert-item.critical {
  border-left: 3px solid #ef4444;
}

.alert-item.warning {
  border-left: 3px solid #f59e0b;
}

.alert-item.info {
  border-left: 3px solid #3b82f6;
}

.alert-icon {
  color: #ef4444;
}

.alert-info {
  flex: 1;
}

.alert-title {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
}

.alert-detail {
  font-size: 12px;
  color: #64748b;
}

.alert-time {
  font-size: 10px;
  color: #94a3b8;
  margin-top: 4px;
}

/* Work Orders */
.workorders-list {
  max-height: 280px;
  overflow-y: auto;
}

.workorder-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 8px;
  background: #f8fafc;
}

.workorder-item:hover {
  background: #eef2ff;
}

.wo-priority {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.wo-priority.high {
  background: #ef4444;
}

.wo-priority.medium {
  background: #f59e0b;
}

.wo-priority.low {
  background: #10b981;
}

.wo-info {
  flex: 1;
}

.wo-title {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
}

.wo-location {
  font-size: 11px;
  color: #64748b;
}

.wo-status {
  width: 80px;
  text-align: right;
}

.wo-progress {
  font-size: 11px;
  color: #3b82f6;
}

/* Equipment Health */
.equipment-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.equipment-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.eq-name {
  font-size: 13px;
  font-weight: 500;
  color: #1e293b;
}

.eq-status {
  font-size: 11px;
  color: #64748b;
  text-align: right;
}

/* Notes */
.notes-list {
  max-height: 160px;
  overflow-y: auto;
}

.note-item {
  padding: 10px;
  border-bottom: 1px solid #e2e8f0;
}

.note-text {
  font-size: 13px;
  color: #1e293b;
  margin-bottom: 6px;
}

.note-meta {
  font-size: 10px;
  color: #94a3b8;
}

/* Device Info Card */
.device-info-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 8px;
}

.battery-section,
.connection-info,
.last-sync {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: #475569;
}

.battery-section .el-progress,
.connection-info .el-progress {
  flex: 1;
  max-width: 100px;
}

/* Responsive - Tablet specific */
@media (max-width: 1024px) {
  .console-grid {
    grid-template-columns: 300px 1fr 300px;
    gap: 12px;
    padding: 16px;
  }

  .quick-actions {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 900px) {
  .console-grid {
    grid-template-columns: 1fr;
  }

  .quick-actions {
    grid-template-columns: repeat(6, 1fr);
  }
}

@media (max-width: 640px) {
  .quick-actions {
    grid-template-columns: repeat(3, 1fr);
  }

  .status-bar {
    flex-direction: column;
    gap: 12px;
  }

  .status-right {
    width: 100%;
    justify-content: space-between;
  }
}
</style>