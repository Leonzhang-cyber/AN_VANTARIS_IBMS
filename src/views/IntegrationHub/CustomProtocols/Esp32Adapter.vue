<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, Refresh, View, Edit, Delete, Monitor, Connection,
  User, Warning, Clock, Cpu, DataLine, Message, Upload, Download,
  Setting, Document, Checked, Bell, TrendCharts,
  List, Odometer, Location, Link, Share, VideoCamera, Lock
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing ESP32 adapters...',
  'Almost ready...'
]

// ==================== Chart Refs ====================
const telemetryChart = ref<HTMLElement | null>(null)
const deviceStatusChart = ref<HTMLElement | null>(null)
const throughputChart = ref<HTMLElement | null>(null)

// ==================== State ====================
const activeTab = ref('devices')
const searchKeyword = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(12)
const deviceDialogVisible = ref(false)
const firmwareDialogVisible = ref(false)
const otaDialogVisible = ref(false)
const logsDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const selectedDevice = ref<any>(null)
const deviceFormRef = ref()
const isConnected = ref(true)

// ==================== Statistics ====================
const statistics = reactive({
  totalDevices: 24,
  activeDevices: 18,
  onlineDevices: 15,
  offlineDevices: 6,
  errorDevices: 3,
  avgSignalStrength: 76,
  totalMessages: 28430,
  firmwareVersion: 'v2.1.0'
})

// ==================== ESP32 Devices Data ====================
interface ESP32Device {
  id: number
  deviceId: string
  name: string
  location: string
  type: string
  status: 'online' | 'offline' | 'error'
  signalStrength: number
  battery: number
  temperature: number
  humidity: number
  lastSeen: string
  firmware: string
  ipAddress: string
  macAddress: string
  uptime: string
  memoryUsage: number
  heapSize: number
}

const devices = ref<ESP32Device[]>([
  {
    id: 1,
    deviceId: 'ESP32_001',
    name: 'Temperature Sensor - Lobby',
    location: 'Building A - Floor 1',
    type: 'Temperature/Humidity',
    status: 'online',
    signalStrength: 92,
    battery: 85,
    temperature: 22.5,
    humidity: 55,
    lastSeen: new Date().toISOString(),
    firmware: 'v2.1.0',
    ipAddress: '192.168.1.101',
    macAddress: 'AA:BB:CC:DD:EE:01',
    uptime: '12d 4h 23m',
    memoryUsage: 45,
    heapSize: 320
  },
  {
    id: 2,
    deviceId: 'ESP32_002',
    name: 'Motion Sensor - Hallway',
    location: 'Building A - Floor 1',
    type: 'Motion',
    status: 'online',
    signalStrength: 88,
    battery: 72,
    temperature: 21.8,
    humidity: 52,
    lastSeen: new Date().toISOString(),
    firmware: 'v2.1.0',
    ipAddress: '192.168.1.102',
    macAddress: 'AA:BB:CC:DD:EE:02',
    uptime: '8d 12h 45m',
    memoryUsage: 38,
    heapSize: 320
  },
  {
    id: 3,
    deviceId: 'ESP32_003',
    name: 'Air Quality Monitor',
    location: 'Building A - Floor 2',
    type: 'Air Quality',
    status: 'online',
    signalStrength: 76,
    battery: 45,
    temperature: 23.2,
    humidity: 58,
    lastSeen: new Date().toISOString(),
    firmware: 'v2.0.5',
    ipAddress: '192.168.1.103',
    macAddress: 'AA:BB:CC:DD:EE:03',
    uptime: '3d 8h 12m',
    memoryUsage: 52,
    heapSize: 320
  },
  {
    id: 4,
    deviceId: 'ESP32_004',
    name: 'Light Controller',
    location: 'Building B - Floor 1',
    type: 'Lighting',
    status: 'offline',
    signalStrength: 0,
    battery: 15,
    temperature: 0,
    humidity: 0,
    lastSeen: new Date(Date.now() - 7200000).toISOString(),
    firmware: 'v2.0.2',
    ipAddress: '192.168.1.104',
    macAddress: 'AA:BB:CC:DD:EE:04',
    uptime: '0d 0h 0m',
    memoryUsage: 0,
    heapSize: 320
  },
  {
    id: 5,
    deviceId: 'ESP32_005',
    name: 'Water Leak Sensor',
    location: 'Building B - Floor 2',
    type: 'Leak Detection',
    status: 'error',
    signalStrength: 34,
    battery: 28,
    temperature: 19.5,
    humidity: 65,
    lastSeen: new Date(Date.now() - 3600000).toISOString(),
    firmware: 'v2.0.8',
    ipAddress: '192.168.1.105',
    macAddress: 'AA:BB:CC:DD:EE:05',
    uptime: '1d 2h 34m',
    memoryUsage: 62,
    heapSize: 320
  },
  {
    id: 6,
    deviceId: 'ESP32_006',
    name: 'HVAC Controller',
    location: 'Building B - Floor 2',
    type: 'HVAC',
    status: 'online',
    signalStrength: 95,
    battery: 92,
    temperature: 22.0,
    humidity: 50,
    lastSeen: new Date().toISOString(),
    firmware: 'v2.1.0',
    ipAddress: '192.168.1.106',
    macAddress: 'AA:BB:CC:DD:EE:06',
    uptime: '15d 6h 18m',
    memoryUsage: 41,
    heapSize: 320
  }
])

// ==================== Telemetry Data ====================
const telemetryData = ref([
  { time: '00:00', temp: 21.5, humidity: 55, signal: 85 },
  { time: '04:00', temp: 20.8, humidity: 58, signal: 82 },
  { time: '08:00', temp: 22.1, humidity: 52, signal: 88 },
  { time: '12:00', temp: 24.3, humidity: 48, signal: 92 },
  { time: '16:00', temp: 25.1, humidity: 45, signal: 90 },
  { time: '20:00', temp: 23.2, humidity: 50, signal: 86 }
])

// ==================== OTA Updates ====================
const otaUpdates = ref([
  { version: 'v2.1.0', released: '2024-01-10', size: '1.2 MB', devices: 12, status: 'stable' },
  { version: 'v2.0.9', released: '2024-01-05', size: '1.1 MB', devices: 8, status: 'beta' },
  { version: 'v2.0.8', released: '2023-12-28', size: '1.1 MB', devices: 4, status: 'deprecated' }
])

// ==================== Device Logs ====================
const deviceLogs = ref([
  { id: 1, time: '2024-01-15 10:23:45', deviceId: 'ESP32_001', level: 'INFO', message: 'Device connected successfully' },
  { id: 2, time: '2024-01-15 10:20:12', deviceId: 'ESP32_003', level: 'WARN', message: 'Signal strength below 80%' },
  { id: 3, time: '2024-01-15 09:45:33', deviceId: 'ESP32_005', level: 'ERROR', message: 'Sensor reading timeout' },
  { id: 4, time: '2024-01-15 09:30:22', deviceId: 'ESP32_002', level: 'INFO', message: 'Motion detected' },
  { id: 5, time: '2024-01-15 08:15:18', deviceId: 'ESP32_004', level: 'WARN', message: 'Battery low (15%)' }
])

// ==================== New Device Form ====================
const newDevice = ref({
  deviceId: '',
  name: '',
  location: '',
  type: '',
  firmware: 'v2.1.0'
})

// ==================== Form Rules ====================
const deviceRules = {
  deviceId: [{ required: true, message: 'Please enter device ID', trigger: 'blur' }],
  name: [{ required: true, message: 'Please enter device name', trigger: 'blur' }],
  location: [{ required: true, message: 'Please enter location', trigger: 'blur' }],
  type: [{ required: true, message: 'Please select device type', trigger: 'change' }]
}

// ==================== OTA Update Form ====================
const otaForm = ref({
  deviceId: '',
  version: '',
  scheduledTime: ''
})

// ==================== Computed ====================
const filteredDevices = computed(() => {
  let filtered = devices.value
  if (searchKeyword.value) {
    filtered = filtered.filter(d =>
        d.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        d.deviceId.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        d.location.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (statusFilter.value) {
    filtered = filtered.filter(d => d.status === statusFilter.value)
  }
  return filtered
})

const paginatedDevices = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredDevices.value.slice(start, end)
})

const onlineCount = computed(() => devices.value.filter(d => d.status === 'online').length)
const offlineCount = computed(() => devices.value.filter(d => d.status === 'offline').length)
const errorCount = computed(() => devices.value.filter(d => d.status === 'error').length)

// ==================== Methods ====================
const getStatusTagType = (status: string) => {
  const types: Record<string, string> = {
    online: 'success',
    offline: 'info',
    error: 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    online: 'Online',
    offline: 'Offline',
    error: 'Error'
  }
  return texts[status] || status
}

const getDeviceTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    'Temperature/Humidity': '',
    'Motion': 'warning',
    'Air Quality': 'danger',
    'Lighting': 'success',
    'Leak Detection': 'info',
    'HVAC': 'primary'
  }
  return colors[type] || ''
}

const getSignalStrengthColor = (strength: number) => {
  if (strength >= 70) return '#52c41a'
  if (strength >= 40) return '#faad14'
  return '#ff4d4f'
}

const getBatteryColor = (battery: number) => {
  if (battery >= 50) return '#52c41a'
  if (battery >= 20) return '#faad14'
  return '#ff4d4f'
}

const formatTime = (timestamp: string) => {
  if (!timestamp) return 'Never'
  const date = new Date(timestamp)
  return date.toLocaleString()
}

const handleAddDevice = () => {
  dialogMode.value = 'create'
  newDevice.value = {
    deviceId: '',
    name: '',
    location: '',
    type: '',
    firmware: 'v2.1.0'
  }
  deviceDialogVisible.value = true
}

const handleEditDevice = (device: ESP32Device) => {
  dialogMode.value = 'edit'
  newDevice.value = {
    deviceId: device.deviceId,
    name: device.name,
    location: device.location,
    type: device.type,
    firmware: device.firmware
  }
  selectedDevice.value = device
  deviceDialogVisible.value = true
}

const handleSaveDevice = async () => {
  await deviceFormRef.value?.validate()
  if (dialogMode.value === 'create') {
    const device: ESP32Device = {
      id: Math.max(...devices.value.map(d => d.id)) + 1,
      deviceId: newDevice.value.deviceId,
      name: newDevice.value.name,
      location: newDevice.value.location,
      type: newDevice.value.type,
      status: 'offline',
      signalStrength: 0,
      battery: 100,
      temperature: 0,
      humidity: 0,
      lastSeen: new Date().toISOString(),
      firmware: newDevice.value.firmware,
      ipAddress: '0.0.0.0',
      macAddress: '00:00:00:00:00:00',
      uptime: '0d 0h 0m',
      memoryUsage: 0,
      heapSize: 320
    }
    devices.value.push(device)
    ElMessage.success('ESP32 device added successfully')
  } else if (selectedDevice.value) {
    const index = devices.value.findIndex(d => d.id === selectedDevice.value.id)
    if (index !== -1) {
      devices.value[index] = { ...devices.value[index], ...newDevice.value }
      ElMessage.success('ESP32 device updated successfully')
    }
  }
  deviceDialogVisible.value = false
}

const handleDeleteDevice = (device: ESP32Device) => {
  ElMessageBox.confirm(
      `Are you sure you want to delete device "${device.name}"? This action cannot be undone.`,
      'Confirm Delete',
      { type: 'warning' }
  ).then(() => {
    const index = devices.value.findIndex(d => d.id === device.id)
    if (index !== -1) {
      devices.value.splice(index, 1)
      ElMessage.success('Device deleted successfully')
    }
  }).catch(() => {})
}

const handleViewDevice = (device: ESP32Device) => {
  selectedDevice.value = device
  ElMessage.info(`Viewing device: ${device.name}`)
}

const handleSendCommand = (device: ESP32Device) => {
  ElMessage.info(`Sending command to ${device.name}`)
}

const handleViewLogs = (device: ESP32Device) => {
  selectedDevice.value = device
  logsDialogVisible.value = true
}

const handleFlashFirmware = (device: ESP32Device) => {
  selectedDevice.value = device
  firmwareDialogVisible.value = true
}

const handleOtaUpdate = () => {
  otaDialogVisible.value = true
}

const handleScheduleOTA = () => {
  if (!otaForm.value.deviceId || !otaForm.value.version) {
    ElMessage.warning('Please select device and version')
    return
  }
  ElMessage.success(`OTA update scheduled for ${otaForm.value.deviceId} to version ${otaForm.value.version}`)
  otaDialogVisible.value = false
  otaForm.value = { deviceId: '', version: '', scheduledTime: '' }
}

const handleRefresh = () => {
  ElMessage.info('Refreshing data...')
  setTimeout(() => {
    statistics.totalMessages += Math.floor(Math.random() * 100)
    ElMessage.success('Data refreshed')
  }, 500)
}

const handleExportData = () => {
  ElMessage.success('Export started...')
}

const handleResetDevice = (device: ESP32Device) => {
  ElMessageBox.confirm(
      `Are you sure you want to reset "${device.name}"?`,
      'Confirm Reset',
      { type: 'warning' }
  ).then(() => {
    ElMessage.success(`Reset command sent to ${device.name}`)
  }).catch(() => {})
}

const handleTestConnection = () => {
  ElMessage.info('Testing connection to all devices...')
  setTimeout(() => {
    ElMessage.success('Connection test completed')
  }, 1500)
}

// ==================== Initialize Charts ====================
const initCharts = () => {
  if (!telemetryChart.value) return

  // Telemetry Chart (Line)
  const telemetry = echarts.init(telemetryChart.value)
  telemetry.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Temperature (°C)', 'Humidity (%)', 'Signal Strength (%)'] },
    xAxis: { type: 'category', data: telemetryData.value.map(d => d.time) },
    yAxis: { type: 'value', name: 'Value' },
    series: [
      {
        name: 'Temperature (°C)',
        type: 'line',
        data: telemetryData.value.map(d => d.temp),
        smooth: true,
        lineStyle: { color: '#ff4d4f', width: 2 },
        itemStyle: { color: '#ff4d4f' }
      },
      {
        name: 'Humidity (%)',
        type: 'line',
        data: telemetryData.value.map(d => d.humidity),
        smooth: true,
        lineStyle: { color: '#1890ff', width: 2 },
        itemStyle: { color: '#1890ff' }
      },
      {
        name: 'Signal Strength (%)',
        type: 'line',
        data: telemetryData.value.map(d => d.signal),
        smooth: true,
        lineStyle: { color: '#52c41a', width: 2 },
        itemStyle: { color: '#52c41a' }
      }
    ]
  })

  // Device Status Chart (Pie)
  const statusChart = echarts.init(deviceStatusChart.value)
  statusChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { top: 'bottom' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: onlineCount.value, name: 'Online', itemStyle: { color: '#52c41a' } },
        { value: offlineCount.value, name: 'Offline', itemStyle: { color: '#8c8c8c' } },
        { value: errorCount.value, name: 'Error', itemStyle: { color: '#ff4d4f' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })

  // Throughput Chart (Bar)
  const throughput = echarts.init(throughputChart.value)
  throughput.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'category', data: devices.value.slice(0, 6).map(d => d.deviceId) },
    yAxis: { type: 'value', name: 'Messages/hour' },
    series: [{
      data: [125, 89, 156, 34, 67, 98],
      type: 'bar',
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#1890ff' }
    }]
  })

  // Handle resize
  window.addEventListener('resize', () => {
    telemetry.resize()
    statusChart.resize()
    throughput.resize()
  })
}

// ==================== Watch for Tab Changes ====================
watch(activeTab, (newTab) => {
  if (newTab === 'monitoring') {
    nextTick(() => {
      initCharts()
    })
  }
})

// ==================== Loading on Mount ====================
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
      if (activeTab.value === 'monitoring') {
        initCharts()
      }
    }, 400)
  }, 2000)
})
</script>

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
          <span class="loading-title">Loading ESP32 Adapter</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="esp32-adapter">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2>ESP32 Adapter</h2>
        <p>Manage and monitor ESP32-based IoT devices with real-time telemetry, OTA updates, and remote control capabilities</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleAddDevice">
          <el-icon><Plus /></el-icon>
          Add Device
        </el-button>
        <el-button @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-cards">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #e8f4ff">
            <el-icon color="#1890ff" size="28"><Cpu /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.totalDevices }}</div>
            <div class="stat-label">Total Devices</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #e6f7e6">
            <el-icon color="#52c41a" size="28"><Connection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.onlineDevices }}</div>
            <div class="stat-label">Online</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #fdf0e8">
            <el-icon color="#ff7a45" size="28"><Message /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.totalMessages.toLocaleString() }}</div>
            <div class="stat-label">Messages Today</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #fff7e6">
            <el-icon color="#faad14" size="28"><DataLine /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.avgSignalStrength }}%</div>
            <div class="stat-label">Avg Signal</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Main Tabs -->
    <el-tabs v-model="activeTab" class="esp32-tabs">
      <!-- Devices Tab -->
      <el-tab-pane label="Devices" name="devices">
        <div class="toolbar">
          <div class="toolbar-left">
            <el-input
                v-model="searchKeyword"
                placeholder="Search by name, ID or location..."
                clearable
                style="width: 260px"
                :prefix-icon="Search"
            />
            <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
              <el-option label="All" value="" />
              <el-option label="Online" value="online" />
              <el-option label="Offline" value="offline" />
              <el-option label="Error" value="error" />
            </el-select>
            <el-button @click="handleTestConnection">
              <el-icon><Link /></el-icon>
              Test Connection
            </el-button>
          </div>
          <div class="toolbar-right">
            <el-button type="success" @click="handleExportData">
              <el-icon><Download /></el-icon>
              Export
            </el-button>
            <el-button type="warning" @click="handleOtaUpdate">
              <el-icon><Upload /></el-icon>
              OTA Update
            </el-button>
          </div>
        </div>

        <!-- Devices Grid -->
        <div class="devices-grid">
          <el-card
              v-for="device in paginatedDevices"
              :key="device.id"
              class="device-card"
              :class="`status-${device.status}`"
              shadow="hover"
          >
            <div class="device-header">
              <div class="device-icon">
                <el-icon :size="32" :color="device.status === 'online' ? '#52c41a' : '#8c8c8c'">
                  <Upload />
                </el-icon>
              </div>
              <div class="device-info">
                <div class="device-name">{{ device.name }}</div>
                <div class="device-id">{{ device.deviceId }}</div>
              </div>
              <el-tag :type="getStatusTagType(device.status)" size="small">
                {{ getStatusText(device.status) }}
              </el-tag>
            </div>

            <div class="device-location">
              <el-icon><Location /></el-icon>
              <span>{{ device.location }}</span>
            </div>

            <div class="device-metrics">
              <div class="metric">
                <span class="label">Signal:</span>
                <div class="progress-wrapper">
                  <el-progress
                      :percentage="device.signalStrength"
                      :color="getSignalStrengthColor(device.signalStrength)"
                      :stroke-width="6"
                      :show-text="false"
                  />
                  <span class="value">{{ device.signalStrength }}%</span>
                </div>
              </div>
              <div class="metric">
                <span class="label">Battery:</span>
                <div class="progress-wrapper">
                  <el-progress
                      :percentage="device.battery"
                      :color="getBatteryColor(device.battery)"
                      :stroke-width="6"
                      :show-text="false"
                  />
                  <span class="value">{{ device.battery }}%</span>
                </div>
              </div>
              <div class="metric-row">
                <div class="metric-item">
                  <span class="label">Temp:</span>
                  <span class="value">{{ device.temperature }}°C</span>
                </div>
                <div class="metric-item">
                  <span class="label">Humidity:</span>
                  <span class="value">{{ device.humidity }}%</span>
                </div>
              </div>
            </div>

            <div class="device-footer">
              <div class="last-seen">
                <el-icon><Clock /></el-icon>
                <span>{{ formatTime(device.lastSeen) }}</span>
              </div>
              <div class="device-actions">
                <el-button size="small" @click="handleViewDevice(device)">
                  <el-icon><View /></el-icon>
                </el-button>
                <el-button size="small" @click="handleEditDevice(device)">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button size="small" @click="handleSendCommand(device)">
                  <el-icon><Message /></el-icon>
                </el-button>
                <el-dropdown trigger="click">
                  <el-button size="small">
                    <el-icon><Setting /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item @click="handleViewLogs(device)">
                        <el-icon><Document /></el-icon> View Logs
                      </el-dropdown-item>
                      <el-dropdown-item @click="handleFlashFirmware(device)">
                        <el-icon><Upload /></el-icon> Flash Firmware
                      </el-dropdown-item>
                      <el-dropdown-item divided @click="handleResetDevice(device)">
                        <el-icon><Refresh /></el-icon> Reset Device
                      </el-dropdown-item>
                      <el-dropdown-item @click="handleDeleteDevice(device)">
                        <el-icon><Delete /></el-icon> Delete
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
          </el-card>
        </div>

        <!-- Pagination -->
        <div class="pagination-wrapper">
          <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[12, 24, 48, 96]"
              :total="filteredDevices.length"
              layout="total, sizes, prev, pager, next, jumper"
          />
        </div>
      </el-tab-pane>

      <!-- Monitoring Tab -->
      <el-tab-pane label="Monitoring" name="monitoring">
        <div class="monitoring-container">
          <el-row :gutter="16">
            <el-col :xs="24" :lg="16">
              <el-card class="monitoring-card" header="Telemetry Trends">
                <div ref="telemetryChart" style="height: 350px"></div>
              </el-card>
            </el-col>
            <el-col :xs="24" :lg="8">
              <el-card class="monitoring-card" header="Device Status">
                <div ref="deviceStatusChart" style="height: 350px"></div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="16" style="margin-top: 16px">
            <el-col :span="24">
              <el-card class="monitoring-card" header="Device Throughput (messages/hour)">
                <div ref="throughputChart" style="height: 300px"></div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>

      <!-- Configuration Tab -->
      <el-tab-pane label="Configuration" name="config">
        <el-row :gutter="16">
          <el-col :span="16">
            <el-card class="config-card" header="MQTT Configuration">
              <el-form label-width="140px">
                <el-form-item label="Broker Address">
                  <el-input value="mqtt://mqtt.example.com:1883" />
                </el-form-item>
                <el-form-item label="Client ID Prefix">
                  <el-input value="esp32_device_" />
                </el-form-item>
                <el-form-item label="Username">
                  <el-input value="esp32_user" />
                </el-form-item>
                <el-form-item label="Password">
                  <el-input type="password" value="********" />
                </el-form-item>
                <el-form-item label="Keep Alive">
                  <el-input-number :value="60" :min="10" :max="300" />
                </el-form-item>
                <el-form-item label="QoS Level">
                  <el-radio-group :value="1">
                    <el-radio :label="0">0 - At most once</el-radio>
                    <el-radio :label="1">1 - At least once</el-radio>
                    <el-radio :label="2">2 - Exactly once</el-radio>
                  </el-radio-group>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary">Save Configuration</el-button>
                </el-form-item>
              </el-form>
            </el-card>
          </el-col>

          <el-col :span="8">
            <el-card class="config-card" header="Adapter Status">
              <div class="connection-status">
                <div class="status-indicator">
                  <div class="status-dot" :class="{ connected: isConnected }"></div>
                  <span class="status-text">{{ isConnected ? 'Connected' : 'Disconnected' }}</span>
                </div>
                <div class="connection-details">
                  <div class="detail-item">
                    <span class="label">Connected Devices:</span>
                    <span class="value">{{ statistics.onlineDevices }}/{{ statistics.totalDevices }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">Firmware Version:</span>
                    <span class="value">{{ statistics.firmwareVersion }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">Uptime:</span>
                    <span class="value">14d 6h 32m</span>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- OTA Updates Tab -->
      <el-tab-pane label="OTA Updates" name="ota">
        <div class="ota-container">
          <div class="ota-header">
            <h3>Firmware Versions</h3>
            <el-button type="primary" @click="handleOtaUpdate">
              <el-icon><Upload /></el-icon>
              Upload Firmware
            </el-button>
          </div>

          <el-table :data="otaUpdates" style="width: 100%; margin-top: 16px" stripe>
            <el-table-column prop="version" label="Version" width="120">
              <template #default="{ row }">
                <el-tag :type="row.status === 'stable' ? 'success' : row.status === 'beta' ? 'warning' : 'info'">
                  {{ row.version }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="released" label="Released" width="120" />
            <el-table-column prop="size" label="Size" width="100" />
            <el-table-column prop="devices" label="Devices" width="100" />
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'stable' ? 'success' : row.status === 'beta' ? 'warning' : 'info'" size="small">
                  {{ row.status.toUpperCase() }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Actions" width="180">
              <template #default="{ row }">
                <el-button link type="primary" size="small">Deploy</el-button>
                <el-button link type="primary" size="small">Schedule</el-button>
                <el-button link type="danger" size="small">Delete</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Device Dialog -->
    <el-dialog
        v-model="deviceDialogVisible"
        :title="dialogMode === 'create' ? 'Add ESP32 Device' : 'Edit ESP32 Device'"
        width="550px"
    >
      <el-form :model="newDevice" :rules="deviceRules" ref="deviceFormRef" label-width="120px">
        <el-form-item label="Device ID" prop="deviceId">
          <el-input v-model="newDevice.deviceId" placeholder="e.g., ESP32_001" />
        </el-form-item>
        <el-form-item label="Device Name" prop="name">
          <el-input v-model="newDevice.name" placeholder="e.g., Temperature Sensor" />
        </el-form-item>
        <el-form-item label="Location" prop="location">
          <el-input v-model="newDevice.location" placeholder="e.g., Building A - Floor 1" />
        </el-form-item>
        <el-form-item label="Device Type" prop="type">
          <el-select v-model="newDevice.type" placeholder="Select type" style="width: 100%">
            <el-option label="Temperature/Humidity" value="Temperature/Humidity" />
            <el-option label="Motion Sensor" value="Motion" />
            <el-option label="Air Quality" value="Air Quality" />
            <el-option label="Lighting Control" value="Lighting" />
            <el-option label="Leak Detection" value="Leak Detection" />
            <el-option label="HVAC Control" value="HVAC" />
          </el-select>
        </el-form-item>
        <el-form-item label="Firmware Version">
          <el-select v-model="newDevice.firmware" style="width: 100%">
            <el-option label="v2.1.0 (Stable)" value="v2.1.0" />
            <el-option label="v2.0.9 (Beta)" value="v2.0.9" />
            <el-option label="v2.0.8" value="v2.0.8" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="deviceDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleSaveDevice">Save</el-button>
      </template>
    </el-dialog>

    <!-- OTA Update Dialog -->
    <el-dialog v-model="otaDialogVisible" title="OTA Update" width="500px">
      <el-form :model="otaForm" label-width="120px">
        <el-form-item label="Select Device">
          <el-select v-model="otaForm.deviceId" placeholder="Choose device" style="width: 100%">
            <el-option
                v-for="device in devices"
                :key="device.id"
                :label="`${device.deviceId} - ${device.name}`"
                :value="device.deviceId"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Firmware Version">
          <el-select v-model="otaForm.version" placeholder="Select version" style="width: 100%">
            <el-option label="v2.1.0 (Stable)" value="v2.1.0" />
            <el-option label="v2.0.9 (Beta)" value="v2.0.9" />
          </el-select>
        </el-form-item>
        <el-form-item label="Schedule">
          <el-date-picker
              v-model="otaForm.scheduledTime"
              type="datetime"
              placeholder="Schedule (optional)"
              style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="otaDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleScheduleOTA">Schedule Update</el-button>
      </template>
    </el-dialog>

    <!-- Device Logs Dialog -->
    <el-dialog v-model="logsDialogVisible" :title="`Device Logs - ${selectedDevice?.name}`" width="800px">
      <el-table :data="deviceLogs" style="width: 100%" stripe>
        <el-table-column prop="time" label="Time" width="180" />
        <el-table-column prop="deviceId" label="Device ID" width="120" />
        <el-table-column prop="level" label="Level" width="100">
          <template #default="{ row }">
            <el-tag :type="row.level === 'INFO' ? 'success' : row.level === 'WARN' ? 'warning' : 'danger'" size="small">
              {{ row.level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="Message" />
      </el-table>
    </el-dialog>
  </div>
</template>

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
  font-size: 20px;
  font-weight: 600;
  color: #e2e8f0;
  display: flex;
  justify-content: center;
  align-items: baseline;
  gap: 4px;
}

.loading-title {
  font-size: 20px;
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
  font-weight: 500;
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

/* ==================== Main Content ==================== */
.esp32-adapter {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: calc(100vh - 60px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.header-left h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.header-left p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 12px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
}

.stat-label {
  font-size: 14px;
  color: #8c8c8c;
  margin-top: 4px;
}

.esp32-tabs {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.toolbar-left {
  display: flex;
  gap: 12px;
  align-items: center;
}

.toolbar-right {
  display: flex;
  gap: 12px;
}

/* Devices Grid */
.devices-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.device-card {
  transition: all 0.3s ease;
  border-top: 3px solid #d9d9d9;
}

.device-card.status-online {
  border-top-color: #52c41a;
}

.device-card.status-offline {
  border-top-color: #8c8c8c;
}

.device-card.status-error {
  border-top-color: #ff4d4f;
}

.device-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.device-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  border-radius: 12px;
}

.device-info {
  flex: 1;
}

.device-name {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

.device-id {
  font-size: 12px;
  color: #999;
  font-family: monospace;
}

.device-location {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 13px;
  margin-bottom: 16px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.device-metrics {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.metric {
  display: flex;
  align-items: center;
  gap: 12px;
}

.metric .label {
  width: 50px;
  font-size: 13px;
  color: #666;
}

.progress-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-wrapper :deep(.el-progress) {
  flex: 1;
}

.progress-wrapper .value {
  font-size: 12px;
  font-weight: 500;
  min-width: 40px;
}

.metric-row {
  display: flex;
  gap: 24px;
  padding: 8px 0;
  background: #f9f9f9;
  border-radius: 8px;
}

.metric-item {
  flex: 1;
  text-align: center;
}

.metric-item .label {
  font-size: 12px;
  color: #999;
  display: block;
}

.metric-item .value {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
}

.device-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.last-seen {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #999;
}

.device-actions {
  display: flex;
  gap: 4px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

/* Monitoring */
.monitoring-container {
  padding: 16px 0;
}

.monitoring-card {
  height: 100%;
}

/* Configuration */
.config-card {
  margin-bottom: 0;
}

.connection-status {
  text-align: center;
  padding: 16px;
}

.status-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 20px;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #ff4d4f;
  animation: pulse-red 2s infinite;
}

.status-dot.connected {
  background-color: #52c41a;
  animation: pulse-green 2s infinite;
}

@keyframes pulse-red {
  0% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
  100% { opacity: 1; transform: scale(1); }
}

@keyframes pulse-green {
  0% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
  100% { opacity: 1; transform: scale(1); }
}

.status-text {
  font-size: 16px;
  font-weight: 600;
}

.connection-details {
  text-align: left;
  margin-top: 16px;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 8px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 13px;
  border-bottom: 1px solid #f0f0f0;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-item .label {
  color: #666;
}

.detail-item .value {
  font-weight: 500;
  color: #1a1a1a;
}

/* OTA */
.ota-container {
  padding: 16px 0;
}

.ota-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ota-header h3 {
  margin: 0;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .devices-grid {
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  }
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
  }

  .header-right {
    margin-top: 16px;
    width: 100%;
  }

  .toolbar {
    flex-direction: column;
    gap: 12px;
  }

  .toolbar-left {
    width: 100%;
    flex-wrap: wrap;
  }

  .toolbar-right {
    width: 100%;
  }

  .devices-grid {
    grid-template-columns: 1fr;
  }
}

:deep(.el-card__header) {
  font-weight: 600;
  background-color: #fafafa;
  border-bottom: 1px solid #f0f0f0;
}

:deep(.el-tabs__header) {
  margin-bottom: 20px;
}
</style>