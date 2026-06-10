<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, Refresh, View, Edit, Delete, Monitor, Connection,
  User, Warning, Clock, Cpu, DataLine, Message, Upload, Download,
  Setting, Document, Checked, Bell, TrendCharts,
  List, Odometer, Location, Link, Share, Position, Tools, Guide, Timer
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing BLE Gateway...',
  'Scanning for BLE devices...',
  'Almost ready...'
]

// ==================== Chart Refs ====================
const rssiChart = ref<HTMLElement | null>(null)
const deviceTypeChart = ref<HTMLElement | null>(null)
const scanRateChart = ref<HTMLElement | null>(null)

// ==================== State ====================
const activeTab = ref('devices')
const searchKeyword = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(12)
const deviceDialogVisible = ref(false)
const scanDialogVisible = ref(false)
const logsDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const selectedDevice = ref<any>(null)
const deviceFormRef = ref()
const isScanning = ref(false)
const isConnected = ref(true)

// ==================== Statistics ====================
const statistics = reactive({
  totalGateways: 3,
  activeGateways: 2,
  totalBeacons: 28,
  activeBeacons: 22,
  avgRSSI: -65,
  scanRate: 125,
  totalMessages: 15680
})

// ==================== BLE Gateways Data ====================
interface BLEGateway {
  id: number
  gatewayId: string
  name: string
  location: string
  status: 'online' | 'offline' | 'error'
  firmware: string
  ipAddress: string
  uptime: string
  scanRate: number
  devicesFound: number
  lastActive: string
}

const gateways = ref<BLEGateway[]>([
  {
    id: 1,
    gatewayId: 'BLE_GW_01',
    name: 'Gateway - North Wing',
    location: 'Building A - Floor 1, North Wing',
    status: 'online',
    firmware: 'v2.1.0',
    ipAddress: '192.168.1.50',
    uptime: '12d 4h 23m',
    scanRate: 125,
    devicesFound: 12,
    lastActive: new Date().toISOString()
  },
  {
    id: 2,
    gatewayId: 'BLE_GW_02',
    name: 'Gateway - South Wing',
    location: 'Building A - Floor 1, South Wing',
    status: 'online',
    firmware: 'v2.1.0',
    ipAddress: '192.168.1.51',
    uptime: '8d 12h 45m',
    scanRate: 118,
    devicesFound: 10,
    lastActive: new Date().toISOString()
  },
  {
    id: 3,
    gatewayId: 'BLE_GW_03',
    name: 'Gateway - East Wing',
    location: 'Building A - Floor 2, East Wing',
    status: 'offline',
    firmware: 'v2.0.5',
    ipAddress: '192.168.1.52',
    uptime: '0d 0h 0m',
    scanRate: 0,
    devicesFound: 6,
    lastActive: new Date(Date.now() - 86400000).toISOString()
  }
])

// ==================== BLE Devices/Beacons Data ====================
interface BLEDevice {
  id: number
  deviceId: string
  name: string
  type: string
  location: string
  gateway: string
  status: 'online' | 'offline' | 'low_battery'
  rssi: number
  battery: number
  manufacturer: string
  lastSeen: string
  major: number
  minor: number
  txPower: number
}

const bleDevices = ref<BLEDevice[]>([
  {
    id: 1,
    deviceId: 'BEACON_001',
    name: 'Occupancy Beacon - Room 101',
    type: 'Occupancy',
    location: 'Building A - Floor 1, Room 101',
    gateway: 'BLE_GW_01',
    status: 'online',
    rssi: -55,
    battery: 92,
    manufacturer: 'iBeacon',
    lastSeen: new Date().toISOString(),
    major: 100,
    minor: 1,
    txPower: -59
  },
  {
    id: 2,
    deviceId: 'BEACON_002',
    name: 'Occupancy Beacon - Room 102',
    type: 'Occupancy',
    location: 'Building A - Floor 1, Room 102',
    gateway: 'BLE_GW_01',
    status: 'online',
    rssi: -62,
    battery: 85,
    manufacturer: 'iBeacon',
    lastSeen: new Date().toISOString(),
    major: 100,
    minor: 2,
    txPower: -59
  },
  {
    id: 3,
    deviceId: 'BEACON_003',
    name: 'Asset Tracker - Cart A',
    type: 'Asset',
    location: 'Building A - Floor 1, Hallway',
    gateway: 'BLE_GW_01',
    status: 'online',
    rssi: -72,
    battery: 68,
    manufacturer: 'Eddystone',
    lastSeen: new Date().toISOString(),
    major: 200,
    minor: 1,
    txPower: -59
  },
  {
    id: 4,
    deviceId: 'BEACON_004',
    name: 'Temperature Sensor - Server Room',
    type: 'Environment',
    location: 'Building A - Floor 2, Server Room',
    gateway: 'BLE_GW_02',
    status: 'online',
    rssi: -48,
    battery: 95,
    manufacturer: 'iBeacon',
    lastSeen: new Date().toISOString(),
    major: 300,
    minor: 1,
    txPower: -59
  },
  {
    id: 5,
    deviceId: 'BEACON_005',
    name: 'Personnel Badge - John Smith',
    type: 'Personnel',
    location: 'Building A - Floor 1, Office 101',
    gateway: 'BLE_GW_01',
    status: 'online',
    rssi: -58,
    battery: 45,
    manufacturer: 'Eddystone',
    lastSeen: new Date().toISOString(),
    major: 400,
    minor: 1,
    txPower: -59
  },
  {
    id: 6,
    deviceId: 'BEACON_006',
    name: 'Lighting Controller',
    type: 'Lighting',
    location: 'Building A - Floor 2, Conference Room',
    gateway: 'BLE_GW_02',
    status: 'offline',
    rssi: 0,
    battery: 12,
    manufacturer: 'Custom',
    lastSeen: new Date(Date.now() - 7200000).toISOString(),
    major: 500,
    minor: 1,
    txPower: -59
  },
  {
    id: 7,
    deviceId: 'BEACON_007',
    name: 'Emergency Pull Cord',
    type: 'Safety',
    location: 'Building A - Floor 1, Restroom',
    gateway: 'BLE_GW_01',
    status: 'low_battery',
    rssi: -78,
    battery: 18,
    manufacturer: 'iBeacon',
    lastSeen: new Date(Date.now() - 1800000).toISOString(),
    major: 600,
    minor: 1,
    txPower: -59
  },
  {
    id: 8,
    deviceId: 'BEACON_008',
    name: 'Smart Shelf Sensor',
    type: 'Inventory',
    location: 'Building A - Floor 1, Storage',
    gateway: 'BLE_GW_03',
    status: 'online',
    rssi: -65,
    battery: 78,
    manufacturer: 'Eddystone',
    lastSeen: new Date().toISOString(),
    major: 700,
    minor: 1,
    txPower: -59
  }
])

// ==================== Scan History ====================
const scanHistory = ref([
  { time: '10:00', devices: 22 },
  { time: '10:05', devices: 24 },
  { time: '10:10', devices: 21 },
  { time: '10:15', devices: 25 },
  { time: '10:20', devices: 23 },
  { time: '10:25', devices: 26 },
  { time: '10:30', devices: 24 }
])

// ==================== Device Logs ====================
const deviceLogs = ref([
  { id: 1, time: '2024-01-15 10:23:45', deviceId: 'BEACON_001', level: 'INFO', message: 'Beacon detected, RSSI: -55 dBm' },
  { id: 2, time: '2024-01-15 10:20:12', deviceId: 'BEACON_007', level: 'WARN', message: 'Low battery alert: 18% remaining' },
  { id: 3, time: '2024-01-15 10:15:33', deviceId: 'BLE_GW_03', level: 'ERROR', message: 'Gateway connection lost' },
  { id: 4, time: '2024-01-15 10:10:22', deviceId: 'BEACON_005', level: 'INFO', message: 'Personnel detected in zone' },
  { id: 5, time: '2024-01-15 10:05:18', deviceId: 'BEACON_003', level: 'INFO', message: 'Asset moved to new location' }
])

// ==================== New Device Form ====================
const newDevice = ref({
  deviceId: '',
  name: '',
  type: '',
  location: '',
  gateway: '',
  manufacturer: 'iBeacon'
})

// ==================== Form Rules ====================
const deviceRules = {
  deviceId: [{ required: true, message: 'Please enter device ID', trigger: 'blur' }],
  name: [{ required: true, message: 'Please enter device name', trigger: 'blur' }],
  type: [{ required: true, message: 'Please select device type', trigger: 'change' }],
  location: [{ required: true, message: 'Please enter location', trigger: 'blur' }]
}

// ==================== Computed ====================
const filteredDevices = computed(() => {
  let filtered = bleDevices.value
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

const onlineCount = computed(() => bleDevices.value.filter(d => d.status === 'online').length)
const offlineCount = computed(() => bleDevices.value.filter(d => d.status === 'offline').length)
const lowBatteryCount = computed(() => bleDevices.value.filter(d => d.status === 'low_battery').length)

// ==================== Methods ====================
const getStatusTagType = (status: string) => {
  const types: Record<string, string> = {
    online: 'success',
    offline: 'info',
    low_battery: 'warning'
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    online: 'Online',
    offline: 'Offline',
    low_battery: 'Low Battery'
  }
  return texts[status] || status
}

const getDeviceTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    Occupancy: '',
    Asset: 'warning',
    Personnel: 'success',
    Environment: 'danger',
    Lighting: 'primary',
    Safety: 'info',
    Inventory: ''
  }
  return colors[type] || ''
}

const getRSSIColor = (rssi: number) => {
  if (rssi >= -60) return '#52c41a'
  if (rssi >= -75) return '#faad14'
  return '#ff4d4f'
}

const getRSSIStatus = (rssi: number) => {
  if (rssi >= -60) return 'Excellent'
  if (rssi >= -75) return 'Good'
  if (rssi >= -85) return 'Fair'
  return 'Poor'
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
    type: '',
    location: '',
    gateway: gateways.value[0]?.gatewayId || '',
    manufacturer: 'iBeacon'
  }
  deviceDialogVisible.value = true
}

const handleEditDevice = (device: BLEDevice) => {
  dialogMode.value = 'edit'
  newDevice.value = {
    deviceId: device.deviceId,
    name: device.name,
    type: device.type,
    location: device.location,
    gateway: device.gateway,
    manufacturer: device.manufacturer
  }
  selectedDevice.value = device
  deviceDialogVisible.value = true
}

const handleSaveDevice = async () => {
  await deviceFormRef.value?.validate()
  if (dialogMode.value === 'create') {
    const device: BLEDevice = {
      id: Math.max(...bleDevices.value.map(d => d.id)) + 1,
      deviceId: newDevice.value.deviceId,
      name: newDevice.value.name,
      type: newDevice.value.type,
      location: newDevice.value.location,
      gateway: newDevice.value.gateway,
      status: 'offline',
      rssi: 0,
      battery: 100,
      manufacturer: newDevice.value.manufacturer,
      lastSeen: new Date().toISOString(),
      major: Math.floor(Math.random() * 1000),
      minor: 1,
      txPower: -59
    }
    bleDevices.value.push(device)
    ElMessage.success('BLE device added successfully')
  } else if (selectedDevice.value) {
    const index = bleDevices.value.findIndex(d => d.id === selectedDevice.value.id)
    if (index !== -1) {
      bleDevices.value[index] = { ...bleDevices.value[index], ...newDevice.value }
      ElMessage.success('BLE device updated successfully')
    }
  }
  deviceDialogVisible.value = false
}

const handleDeleteDevice = (device: BLEDevice) => {
  ElMessageBox.confirm(
      `Are you sure you want to delete device "${device.name}"? This action cannot be undone.`,
      'Confirm Delete',
      { type: 'warning' }
  ).then(() => {
    const index = bleDevices.value.findIndex(d => d.id === device.id)
    if (index !== -1) {
      bleDevices.value.splice(index, 1)
      ElMessage.success('Device deleted successfully')
    }
  }).catch(() => {})
}

const handleViewDevice = (device: BLEDevice) => {
  selectedDevice.value = device
  ElMessage.info(`Viewing device: ${device.name}`)
}

const handleStartScan = () => {
  isScanning.value = true
  ElMessage.info('Starting BLE scan...')
  setTimeout(() => {
    isScanning.value = false
    ElMessage.success('Scan completed. Found 24 BLE devices')
    scanDialogVisible.value = false
  }, 3000)
  scanDialogVisible.value = true
}

const handleViewLogs = (device: any) => {
  selectedDevice.value = device
  logsDialogVisible.value = true
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

const handleGatewayConfig = (gateway: BLEGateway) => {
  ElMessage.info(`Configuring gateway: ${gateway.name}`)
}

const handleResetGateway = (gateway: BLEGateway) => {
  ElMessageBox.confirm(
      `Are you sure you want to reset "${gateway.name}"?`,
      'Confirm Reset',
      { type: 'warning' }
  ).then(() => {
    ElMessage.success(`Reset command sent to ${gateway.name}`)
  }).catch(() => {})
}

const handleLocateDevice = (device: BLEDevice) => {
  ElMessage.info(`Locating device: ${device.name} - Signal strength: ${getRSSIStatus(device.rssi)}`)
}

// ==================== Initialize Charts ====================
const initCharts = () => {
  if (!rssiChart.value) return

  // RSSI Distribution Chart (Bar)
  const rssiDist = echarts.init(rssiChart.value)
  rssiDist.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'category', data: ['Excellent', 'Good', 'Fair', 'Poor'] },
    yAxis: { type: 'value', name: 'Devices' },
    series: [{
      data: [8, 12, 5, 3],
      type: 'bar',
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const colors = ['#52c41a', '#faad14', '#fa8c16', '#ff4d4f']
          return colors[params.dataIndex]
        }
      }
    }]
  })

  // Device Type Chart (Pie)
  const deviceType = echarts.init(deviceTypeChart.value)
  deviceType.setOption({
    tooltip: { trigger: 'item' },
    legend: { top: 'bottom' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: 8, name: 'Occupancy', itemStyle: { color: '#1890ff' } },
        { value: 5, name: 'Asset Tracking', itemStyle: { color: '#faad14' } },
        { value: 4, name: 'Personnel', itemStyle: { color: '#52c41a' } },
        { value: 3, name: 'Environment', itemStyle: { color: '#ff4d4f' } },
        { value: 8, name: 'Other', itemStyle: { color: '#8c8c8c' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })

  // Scan Rate Chart (Line)
  const scanRate = echarts.init(scanRateChart.value)
  scanRate.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: scanHistory.value.map(s => s.time) },
    yAxis: { type: 'value', name: 'Devices Detected' },
    series: [{
      data: scanHistory.value.map(s => s.devices),
      type: 'line',
      smooth: true,
      areaStyle: { opacity: 0.3 },
      lineStyle: { color: '#1890ff', width: 2 },
      itemStyle: { color: '#1890ff' }
    }]
  })

  // Handle resize
  window.addEventListener('resize', () => {
    rssiDist.resize()
    deviceType.resize()
    scanRate.resize()
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
          <span class="loading-title">Loading BLE Gateway Adapter</span>
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
  <div v-else class="ble-gateway-adapter">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2>BLE Gateway Adapter</h2>
        <p>Monitor and manage Bluetooth Low Energy devices, track beacons, asset tags, and personnel badges with real-time location and signal strength analytics</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleAddDevice">
          <el-icon><Plus /></el-icon>
          Add Device
        </el-button>
        <el-button type="success" @click="handleStartScan">
          <el-icon><Guide /></el-icon>
          Start Scan
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
            <el-icon color="#1890ff" size="28"><Position /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.totalGateways }}</div>
            <div class="stat-label">Active Gateways</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #e6f7e6">
            <el-icon color="#52c41a" size="28"><Checked /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.totalBeacons }}</div>
            <div class="stat-label">BLE Devices</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #fff7e6">
            <el-icon color="#faad14" size="28"><Tools /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.avgRSSI }} dBm</div>
            <div class="stat-label">Avg Signal</div>
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
    </div>

    <!-- Main Tabs -->
    <el-tabs v-model="activeTab" class="ble-tabs">
      <!-- BLE Devices Tab -->
      <el-tab-pane label="BLE Devices" name="devices">
        <div class="toolbar">
          <div class="toolbar-left">
            <el-input
                v-model="searchKeyword"
                placeholder="Search by name, ID or location..."
                clearable
                style="width: 260px"
                :prefix-icon="Search"
            />
            <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 140px">
              <el-option label="All" value="" />
              <el-option label="Online" value="online" />
              <el-option label="Offline" value="offline" />
              <el-option label="Low Battery" value="low_battery" />
            </el-select>
          </div>
          <div class="toolbar-right">
            <el-button type="success" @click="handleExportData">
              <el-icon><Download /></el-icon>
              Export
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
                  <Bluetooth />
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
              <div class="metric-row">
                <div class="metric-item">
                  <span class="label">RSSI:</span>
                  <span class="value" :style="{ color: getRSSIColor(device.rssi) }">
                    {{ device.rssi }} dBm
                  </span>
                </div>
                <div class="metric-item">
                  <span class="label">Signal:</span>
                  <span class="value">{{ getRSSIStatus(device.rssi) }}</span>
                </div>
                <div class="metric-item">
                  <span class="label">Battery:</span>
                  <span class="value" :style="{ color: getBatteryColor(device.battery) }">
                    {{ device.battery }}%
                  </span>
                </div>
              </div>
              <div class="metric-details">
                <div class="detail">
                  <span class="label">Gateway:</span>
                  <span class="value">{{ device.gateway }}</span>
                </div>
                <div class="detail">
                  <span class="label">Type:</span>
                  <el-tag :type="getDeviceTypeColor(device.type)" size="small">{{ device.type }}</el-tag>
                </div>
                <div class="detail">
                  <span class="label">Manufacturer:</span>
                  <span class="value">{{ device.manufacturer }}</span>
                </div>
              </div>
            </div>

            <div class="device-footer">
              <div class="last-seen">
                <el-icon><Timer /></el-icon>
                <span>{{ formatTime(device.lastSeen) }}</span>
              </div>
              <div class="device-actions">
                <el-button size="small" @click="handleViewDevice(device)">
                  <el-icon><View /></el-icon>
                </el-button>
                <el-button size="small" @click="handleEditDevice(device)">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button size="small" @click="handleLocateDevice(device)">
                  <el-icon><Position /></el-icon>
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
                      <el-dropdown-item divided @click="handleDeleteDevice(device)">
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

      <!-- Gateways Tab -->
      <el-tab-pane label="Gateways" name="gateways">
        <el-table :data="gateways" style="width: 100%" stripe>
          <el-table-column prop="gatewayId" label="Gateway ID" width="120" />
          <el-table-column prop="name" label="Name" min-width="180" />
          <el-table-column prop="location" label="Location" min-width="200" />
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'online' ? 'success' : 'danger'" size="small">
                {{ row.status.toUpperCase() }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="devicesFound" label="Devices" width="100" align="center" />
          <el-table-column prop="scanRate" label="Scan Rate" width="100">
            <template #default="{ row }">
              {{ row.scanRate }}/min
            </template>
          </el-table-column>
          <el-table-column prop="uptime" label="Uptime" width="140" />
          <el-table-column label="Actions" width="150">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="handleGatewayConfig(row)">
                Configure
              </el-button>
              <el-button link type="danger" size="small" @click="handleResetGateway(row)">
                Reset
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Monitoring Tab -->
      <el-tab-pane label="Monitoring" name="monitoring">
        <div class="monitoring-container">
          <el-row :gutter="16">
            <el-col :xs="24" :lg="12">
              <el-card class="monitoring-card" header="RSSI Signal Distribution">
                <div ref="rssiChart" style="height: 300px"></div>
              </el-card>
            </el-col>
            <el-col :xs="24" :lg="12">
              <el-card class="monitoring-card" header="Device Type Distribution">
                <div ref="deviceTypeChart" style="height: 300px"></div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="16" style="margin-top: 16px">
            <el-col :span="24">
              <el-card class="monitoring-card" header="Scan Rate Trend (Devices per scan)">
                <div ref="scanRateChart" style="height: 300px"></div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="16" style="margin-top: 16px">
            <el-col :span="24">
              <el-card class="monitoring-card" header="Recent Alerts">
                <el-table :data="deviceLogs.slice(0, 5)" style="width: 100%" stripe>
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
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>

      <!-- Configuration Tab -->
      <el-tab-pane label="Configuration" name="config">
        <el-row :gutter="16">
          <el-col :span="16">
            <el-card class="config-card" header="BLE Scanner Configuration">
              <el-form label-width="160px">
                <el-form-item label="Scan Duration (ms)">
                  <el-input-number :value="5000" :min="1000" :max="30000" :step="1000" />
                  <span class="form-hint">Duration of each BLE scan cycle</span>
                </el-form-item>
                <el-form-item label="Scan Interval (ms)">
                  <el-input-number :value="10000" :min="5000" :max="60000" :step="5000" />
                  <span class="form-hint">Time between scan cycles</span>
                </el-form-item>
                <el-form-item label="RSSI Threshold">
                  <el-slider :value="-90" :min="-100" :max="-40" :step="1" />
                  <span class="form-hint">Minimum signal strength to report</span>
                </el-form-item>
                <el-form-item label="Duplicate Filter">
                  <el-switch :value="true" />
                  <span class="form-hint">Filter duplicate BLE advertisements</span>
                </el-form-item>
                <el-form-item label="Active Scanning">
                  <el-switch :value="false" />
                  <span class="form-hint">Send scan requests to get more data</span>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary">Save Configuration</el-button>
                </el-form-item>
              </el-form>
            </el-card>
          </el-col>

          <el-col :span="8">
            <el-card class="config-card" header="Connection Status">
              <div class="connection-status">
                <div class="status-indicator">
                  <div class="status-dot" :class="{ connected: isConnected }"></div>
                  <span class="status-text">{{ isConnected ? 'Connected' : 'Disconnected' }}</span>
                </div>
                <div class="connection-details">
                  <div class="detail-item">
                    <span class="label">Active Gateways:</span>
                    <span class="value">{{ statistics.activeGateways }}/{{ statistics.totalGateways }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">Online Devices:</span>
                    <span class="value">{{ onlineCount }}/{{ statistics.totalBeacons }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">Low Battery:</span>
                    <span class="value">{{ lowBatteryCount }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">Scan Rate:</span>
                    <span class="value">{{ statistics.scanRate }} devices/min</span>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>
    </el-tabs>

    <!-- Device Dialog -->
    <el-dialog
        v-model="deviceDialogVisible"
        :title="dialogMode === 'create' ? 'Add BLE Device' : 'Edit BLE Device'"
        width="550px"
    >
      <el-form :model="newDevice" :rules="deviceRules" ref="deviceFormRef" label-width="120px">
        <el-form-item label="Device ID" prop="deviceId">
          <el-input v-model="newDevice.deviceId" placeholder="e.g., BEACON_001" />
        </el-form-item>
        <el-form-item label="Device Name" prop="name">
          <el-input v-model="newDevice.name" placeholder="e.g., Occupancy Beacon - Room 101" />
        </el-form-item>
        <el-form-item label="Device Type" prop="type">
          <el-select v-model="newDevice.type" placeholder="Select type" style="width: 100%">
            <el-option label="Occupancy Beacon" value="Occupancy" />
            <el-option label="Asset Tracker" value="Asset" />
            <el-option label="Personnel Badge" value="Personnel" />
            <el-option label="Environmental Sensor" value="Environment" />
            <el-option label="Lighting Controller" value="Lighting" />
            <el-option label="Safety Device" value="Safety" />
            <el-option label="Inventory Sensor" value="Inventory" />
          </el-select>
        </el-form-item>
        <el-form-item label="Location" prop="location">
          <el-input v-model="newDevice.location" placeholder="e.g., Building A - Floor 1, Room 101" />
        </el-form-item>
        <el-form-item label="Gateway" prop="gateway">
          <el-select v-model="newDevice.gateway" placeholder="Select gateway" style="width: 100%">
            <el-option
                v-for="gateway in gateways"
                :key="gateway.id"
                :label="`${gateway.gatewayId} - ${gateway.name}`"
                :value="gateway.gatewayId"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Manufacturer">
          <el-select v-model="newDevice.manufacturer" style="width: 100%">
            <el-option label="iBeacon" value="iBeacon" />
            <el-option label="Eddystone" value="Eddystone" />
            <el-option label="AltBeacon" value="AltBeacon" />
            <el-option label="Custom" value="Custom" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="deviceDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleSaveDevice">Save</el-button>
      </template>
    </el-dialog>

    <!-- Scan Dialog -->
    <el-dialog v-model="scanDialogVisible" title="BLE Scan" width="500px" :close-on-click-modal="false">
      <div class="scan-container">
        <div class="scan-animation">
          <el-icon :size="64" color="#1890ff"><Guide /></el-icon>
          <div class="scan-wave"></div>
        </div>
        <div class="scan-status">
          <p v-if="isScanning">Scanning for BLE devices...</p>
          <p v-else>Scan completed!</p>
        </div>
        <div v-if="!isScanning" class="scan-results">
          <el-tag type="success">Found 24 devices</el-tag>
        </div>
      </div>
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
.ble-gateway-adapter {
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

.ble-tabs {
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

.device-card.status-low_battery {
  border-top-color: #faad14;
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

.metric-row {
  display: flex;
  gap: 16px;
  padding: 8px;
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
}

.metric-details {
  display: flex;
  justify-content: space-between;
  padding: 8px;
  background: #fafafa;
  border-radius: 8px;
  font-size: 12px;
}

.metric-details .detail {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.metric-details .label {
  color: #999;
}

.metric-details .value {
  font-weight: 500;
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

.form-hint {
  margin-left: 12px;
  font-size: 12px;
  color: #999;
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

/* Scan Dialog */
.scan-container {
  text-align: center;
  padding: 20px;
}

.scan-animation {
  position: relative;
  display: inline-block;
}

.scan-wave {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 120px;
  height: 120px;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  background: rgba(24, 144, 255, 0.2);
  animation: ripple 1.5s infinite;
}

@keyframes ripple {
  0% {
    width: 0;
    height: 0;
    opacity: 0.5;
  }
  100% {
    width: 120px;
    height: 120px;
    opacity: 0;
  }
}

.scan-status {
  margin-top: 40px;
  font-size: 16px;
  color: #666;
}

.scan-results {
  margin-top: 20px;
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
    flex-wrap: wrap;
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