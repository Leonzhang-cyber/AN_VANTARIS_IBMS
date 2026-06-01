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
        <div class="loading-tip">Network Room Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="network-room">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Network Room Management</h2>
        <p class="subtitle">Monitor and manage network equipment, switches, routers, and connectivity infrastructure</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddDeviceDialog">
          <el-icon><Plus /></el-icon> Add Device
        </el-button>
        <el-button @click="exportData">
          <el-icon><Download /></el-icon> Export
        </el-button>
        <el-button @click="refreshData">
          <el-icon><RefreshRight /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">🖧</div>
        <div class="stat-info">
          <div class="stat-value">{{ networkDevices.length }}</div>
          <div class="stat-label">Total Devices</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🟢</div>
        <div class="stat-info">
          <div class="stat-value">{{ onlineCount }}</div>
          <div class="stat-label">Online</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-info">
          <div class="stat-value">{{ avgCpuLoad }}%</div>
          <div class="stat-label">Avg CPU Load</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⚠️</div>
        <div class="stat-info">
          <div class="stat-value">{{ alertCount }}</div>
          <div class="stat-label">Active Alerts</div>
        </div>
      </div>
    </div>

    <!-- Search and Filter Bar -->
    <div class="filter-section">
      <div class="search-wrapper">
        <el-input v-model="searchText" placeholder="Search by device name, model or IP..." clearable :prefix-icon="Search" />
      </div>
      <div class="filter-wrapper">
        <el-select v-model="filterType" placeholder="Device Type" clearable style="width: 150px">
          <el-option label="All Types" value="all" />
          <el-option label="Core Switch" value="core" />
          <el-option label="Aggregation Switch" value="aggregation" />
          <el-option label="Access Switch" value="access" />
          <el-option label="Router" value="router" />
          <el-option label="Firewall" value="firewall" />
          <el-option label="Load Balancer" value="loadbalancer" />
        </el-select>
        <el-select v-model="filterBuilding" placeholder="Building" clearable style="width: 160px">
          <el-option label="All Buildings" value="all" />
          <el-option v-for="b in uniqueBuildings" :key="b" :label="b" :value="b" />
        </el-select>
      </div>
    </div>

    <!-- Network Devices Grid -->
    <div class="devices-grid">
      <div v-for="device in filteredDevices" :key="device.id" class="device-card" :class="device.status">
        <div class="device-header">
          <div class="device-icon">{{ getDeviceIcon(device.type) }}</div>
          <div class="device-info">
            <div class="device-name">{{ device.name }}</div>
            <div class="device-model">{{ device.model }}</div>
          </div>
          <div class="device-status">
            <span class="status-badge" :class="device.status">{{ getStatusText(device.status) }}</span>
          </div>
        </div>

        <div class="device-location">
          <el-icon><Location /></el-icon>
          <span>{{ device.buildingName }} - {{ device.roomName }} (Rack {{ device.rackPosition }})</span>
        </div>

        <!-- Key Metrics -->
        <div class="device-metrics">
          <div class="metric-item">
            <div class="metric-value">{{ device.cpuLoad }}%</div>
            <div class="metric-label">CPU Load</div>
          </div>
          <div class="metric-item">
            <div class="metric-value">{{ device.memoryUsage }}%</div>
            <div class="metric-label">Memory</div>
          </div>
          <div class="metric-item">
            <div class="metric-value">{{ device.temperature }}°C</div>
            <div class="metric-label">Temp</div>
          </div>
          <div class="metric-item">
            <div class="metric-value">{{ device.uptime }}</div>
            <div class="metric-label">Uptime (days)</div>
          </div>
        </div>

        <!-- Port Utilization -->
        <div class="port-section">
          <div class="port-header">
            <span class="port-title">Port Utilization</span>
            <span class="port-stats">{{ device.activePorts }}/{{ device.totalPorts }} active</span>
          </div>
          <div class="port-bar">
            <el-progress :percentage="device.portUtilization" :stroke-width="8" :color="getUtilizationColor(device.portUtilization)" />
          </div>
        </div>

        <!-- Traffic Info -->
        <div class="traffic-info">
          <div class="traffic-item">
            <span class="traffic-label">Inbound</span>
            <span class="traffic-value">{{ device.inboundTraffic }} Gbps</span>
          </div>
          <div class="traffic-item">
            <span class="traffic-label">Outbound</span>
            <span class="traffic-value">{{ device.outboundTraffic }} Gbps</span>
          </div>
          <div class="traffic-item">
            <span class="traffic-label">Packet Loss</span>
            <span class="traffic-value" :class="getPacketLossClass(device.packetLoss)">{{ device.packetLoss }}%</span>
          </div>
        </div>

        <div class="device-alerts" v-if="device.alerts && device.alerts.length > 0">
          <div v-for="alert in device.alerts.slice(0, 2)" :key="alert.time" class="alert-item">
            <el-icon><Warning /></el-icon>
            <span>{{ alert.message }}</span>
          </div>
          <div v-if="device.alerts.length > 2" class="alert-more">+{{ device.alerts.length - 2 }} more alerts</div>
        </div>

        <div class="device-actions">
          <el-button size="small" type="primary" plain @click="viewDevice(device)">
            <el-icon><View /></el-icon> Details
          </el-button>
          <el-button size="small" type="info" plain @click="editDevice(device)">
            <el-icon><Edit /></el-icon> Edit
          </el-button>
          <el-button size="small" type="danger" plain @click="deleteDevice(device)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredDevices.length === 0" class="empty-state">
      <div class="empty-icon">🖧</div>
      <div class="empty-title">No network devices found</div>
      <div class="empty-desc">Add a network device to start managing your infrastructure</div>
      <el-button type="primary" @click="openAddDeviceDialog">Add Device</el-button>
    </div>

    <!-- Add/Edit Device Dialog -->
    <el-dialog v-model="showDeviceDialog" :title="dialogTitle" width="650px">
      <el-form :model="deviceForm" label-width="130px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Device Name" required>
              <el-input v-model="deviceForm.name" placeholder="e.g., Core-SW-01" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Model">
              <el-input v-model="deviceForm.model" placeholder="e.g., Cisco 9300" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Device Type" required>
          <el-select v-model="deviceForm.type" style="width: 100%">
            <el-option label="Core Switch" value="core" />
            <el-option label="Aggregation Switch" value="aggregation" />
            <el-option label="Access Switch" value="access" />
            <el-option label="Router" value="router" />
            <el-option label="Firewall" value="firewall" />
            <el-option label="Load Balancer" value="loadbalancer" />
          </el-select>
        </el-form-item>
        <el-form-item label="Building" required>
          <el-select v-model="deviceForm.buildingId" style="width: 100%">
            <el-option v-for="b in buildings" :key="b.id" :label="b.name" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Room Name">
          <el-input v-model="deviceForm.roomName" placeholder="e.g., Network Room A" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Rack Position">
              <el-input v-model="deviceForm.rackPosition" placeholder="e.g., Rack 1, U10" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="IP Address">
              <el-input v-model="deviceForm.ipAddress" placeholder="e.g., 192.168.1.1" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Total Ports">
              <el-input-number v-model="deviceForm.totalPorts" :min="0" :step="8" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Installation Date">
              <el-date-picker v-model="deviceForm.installationDate" type="date" placeholder="Select date" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Status">
          <el-radio-group v-model="deviceForm.status">
            <el-radio label="online">Online</el-radio>
            <el-radio label="offline">Offline</el-radio>
            <el-radio label="maintenance">Maintenance</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="deviceForm.description" type="textarea" :rows="2" placeholder="Additional notes" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDeviceDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveDevice">Save Device</el-button>
      </template>
    </el-dialog>

    <!-- Device Detail Dialog -->
    <el-dialog v-model="showDetailDialog" :title="selectedDevice?.name" width="750px">
      <div v-if="selectedDevice">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Device ID">{{ selectedDevice.id }}</el-descriptions-item>
          <el-descriptions-item label="Model">{{ selectedDevice.model }}</el-descriptions-item>
          <el-descriptions-item label="Type">{{ getDeviceTypeLabel(selectedDevice.type) }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <span :class="['status-badge', selectedDevice.status]">{{ getStatusText(selectedDevice.status) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="Building">{{ selectedDevice.buildingName }}</el-descriptions-item>
          <el-descriptions-item label="Room">{{ selectedDevice.roomName }}</el-descriptions-item>
          <el-descriptions-item label="Rack Position">{{ selectedDevice.rackPosition }}</el-descriptions-item>
          <el-descriptions-item label="IP Address">{{ selectedDevice.ipAddress }}</el-descriptions-item>
          <el-descriptions-item label="CPU Load">{{ selectedDevice.cpuLoad }}%</el-descriptions-item>
          <el-descriptions-item label="Memory Usage">{{ selectedDevice.memoryUsage }}%</el-descriptions-item>
          <el-descriptions-item label="Temperature">{{ selectedDevice.temperature }}°C</el-descriptions-item>
          <el-descriptions-item label="Uptime">{{ selectedDevice.uptime }} days</el-descriptions-item>
          <el-descriptions-item label="Ports">{{ selectedDevice.activePorts }}/{{ selectedDevice.totalPorts }}</el-descriptions-item>
          <el-descriptions-item label="Installation Date">{{ selectedDevice.installationDate }}</el-descriptions-item>
          <el-descriptions-item label="Last Firmware Update">{{ selectedDevice.lastFirmwareUpdate }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedDevice.description || 'No description' }}</el-descriptions-item>
        </el-descriptions>

        <div v-if="selectedDevice.alerts && selectedDevice.alerts.length > 0" class="detail-alerts">
          <h4>Active Alerts</h4>
          <el-table :data="selectedDevice.alerts" size="small">
            <el-table-column label="Severity" width="100">
              <template #default="{ row }">
                <el-tag :type="row.severity === 'critical' ? 'danger' : row.severity === 'warning' ? 'warning' : 'info'" size="small">
                  {{ row.severity }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="message" label="Message" />
            <el-table-column prop="time" label="Time" width="140" />
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">Close</el-button>
        <el-button type="primary" @click="editDevice(selectedDevice); showDetailDialog = false">Edit</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus, RefreshRight, Search, Download, View, Edit, Delete, Location, Warning } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Loading network room data...',
  'Fetching device information...',
  'Checking connectivity status...',
  'Almost ready...'
]

// Building interface
interface Building {
  id: number
  name: string
}

// Network Device interface
interface NetworkDevice {
  id: number
  name: string
  model: string
  type: string
  buildingId: number
  buildingName: string
  roomName: string
  rackPosition: string
  ipAddress: string
  cpuLoad: number
  memoryUsage: number
  temperature: number
  uptime: number
  totalPorts: number
  activePorts: number
  portUtilization: number
  inboundTraffic: number
  outboundTraffic: number
  packetLoss: number
  status: string
  installationDate: string
  lastFirmwareUpdate: string
  alerts: { severity: string; message: string; time: string }[]
  description: string
}

// Sample buildings data
const buildings = ref<Building[]>([
  { id: 1, name: 'Data Center A' },
  { id: 2, name: 'Data Center B' }
])

// Sample network devices data
const networkDevices = ref<NetworkDevice[]>([
  {
    id: 1,
    name: 'Core-SW-01',
    model: 'Cisco Nexus 9508',
    type: 'core',
    buildingId: 1,
    buildingName: 'Data Center A',
    roomName: 'Network Room - Floor 1',
    rackPosition: 'Rack A1, U1-8',
    ipAddress: '10.1.1.1',
    cpuLoad: 32,
    memoryUsage: 45,
    temperature: 42,
    uptime: 245,
    totalPorts: 48,
    activePorts: 38,
    portUtilization: 79,
    inboundTraffic: 12.5,
    outboundTraffic: 10.8,
    packetLoss: 0.02,
    status: 'online',
    installationDate: '2023-06-15',
    lastFirmwareUpdate: '2024-12-10',
    alerts: [],
    description: 'Core switch for Data Center A'
  },
  {
    id: 2,
    name: 'Core-SW-02',
    model: 'Cisco Nexus 9508',
    type: 'core',
    buildingId: 1,
    buildingName: 'Data Center A',
    roomName: 'Network Room - Floor 1',
    rackPosition: 'Rack A2, U1-8',
    ipAddress: '10.1.1.2',
    cpuLoad: 35,
    memoryUsage: 48,
    temperature: 43,
    uptime: 245,
    totalPorts: 48,
    activePorts: 42,
    portUtilization: 87,
    inboundTraffic: 14.2,
    outboundTraffic: 11.5,
    packetLoss: 0.01,
    status: 'online',
    installationDate: '2023-06-15',
    lastFirmwareUpdate: '2024-12-10',
    alerts: [],
    description: 'Redundant core switch'
  },
  {
    id: 3,
    name: 'Agg-SW-01',
    model: 'Cisco Catalyst 9300',
    type: 'aggregation',
    buildingId: 1,
    buildingName: 'Data Center A',
    roomName: 'Network Room - Floor 2',
    rackPosition: 'Rack B1, U10-20',
    ipAddress: '10.1.2.1',
    cpuLoad: 55,
    memoryUsage: 62,
    temperature: 48,
    uptime: 180,
    totalPorts: 24,
    activePorts: 20,
    portUtilization: 83,
    inboundTraffic: 8.2,
    outboundTraffic: 7.5,
    packetLoss: 0.08,
    status: 'online',
    installationDate: '2023-08-20',
    lastFirmwareUpdate: '2024-11-15',
    alerts: [
      { severity: 'warning', message: 'High CPU usage detected', time: '2025-01-16 09:30:00' }
    ],
    description: 'Aggregation switch for server racks'
  },
  {
    id: 4,
    name: 'Agg-SW-02',
    model: 'Cisco Catalyst 9300',
    type: 'aggregation',
    buildingId: 1,
    buildingName: 'Data Center A',
    roomName: 'Network Room - Floor 2',
    rackPosition: 'Rack B2, U10-20',
    ipAddress: '10.1.2.2',
    cpuLoad: 48,
    memoryUsage: 55,
    temperature: 46,
    uptime: 180,
    totalPorts: 24,
    activePorts: 18,
    portUtilization: 75,
    inboundTraffic: 7.2,
    outboundTraffic: 6.8,
    packetLoss: 0.05,
    status: 'online',
    installationDate: '2023-08-20',
    lastFirmwareUpdate: '2024-11-15',
    alerts: [],
    description: 'Redundant aggregation switch'
  },
  {
    id: 5,
    name: 'FW-01',
    model: 'Palo Alto PA-5260',
    type: 'firewall',
    buildingId: 1,
    buildingName: 'Data Center A',
    roomName: 'Network Room - Floor 1',
    rackPosition: 'Rack A3, U1-4',
    ipAddress: '10.1.1.254',
    cpuLoad: 28,
    memoryUsage: 52,
    temperature: 38,
    uptime: 200,
    totalPorts: 16,
    activePorts: 12,
    portUtilization: 75,
    inboundTraffic: 5.5,
    outboundTraffic: 4.2,
    packetLoss: 0.01,
    status: 'online',
    installationDate: '2023-09-10',
    lastFirmwareUpdate: '2024-12-01',
    alerts: [],
    description: 'Perimeter firewall'
  },
  {
    id: 6,
    name: 'Router-01',
    model: 'Cisco ASR 1001-X',
    type: 'router',
    buildingId: 2,
    buildingName: 'Data Center B',
    roomName: 'Network Room - Floor 1',
    rackPosition: 'Rack C1, U1-2',
    ipAddress: '203.0.113.1',
    cpuLoad: 42,
    memoryUsage: 58,
    temperature: 45,
    uptime: 120,
    totalPorts: 8,
    activePorts: 6,
    portUtilization: 75,
    inboundTraffic: 4.5,
    outboundTraffic: 3.8,
    packetLoss: 0.03,
    status: 'online',
    installationDate: '2024-02-15',
    lastFirmwareUpdate: '2024-11-20',
    alerts: [
      { severity: 'warning', message: 'High memory usage', time: '2025-01-15 14:00:00' }
    ],
    description: 'Edge router'
  },
  {
    id: 7,
    name: 'LB-01',
    model: 'F5 BIG-IP i5800',
    type: 'loadbalancer',
    buildingId: 2,
    buildingName: 'Data Center B',
    roomName: 'Network Room - Floor 2',
    rackPosition: 'Rack D1, U5-8',
    ipAddress: '10.2.1.100',
    cpuLoad: 35,
    memoryUsage: 48,
    temperature: 40,
    uptime: 90,
    totalPorts: 16,
    activePorts: 14,
    portUtilization: 87,
    inboundTraffic: 6.2,
    outboundTraffic: 5.8,
    packetLoss: 0.02,
    status: 'online',
    installationDate: '2024-05-20',
    lastFirmwareUpdate: '2024-12-05',
    alerts: [],
    description: 'Application load balancer'
  }
])

// UI State
const searchText = ref('')
const filterType = ref('all')
const filterBuilding = ref('all')
const showDeviceDialog = ref(false)
const showDetailDialog = ref(false)
const isEditing = ref(false)
const selectedDevice = ref<NetworkDevice | null>(null)

const deviceForm = ref({
  name: '',
  model: '',
  type: 'core',
  buildingId: 1,
  roomName: '',
  rackPosition: '',
  ipAddress: '',
  totalPorts: 0,
  installationDate: null,
  status: 'online',
  description: ''
})

// Computed
const dialogTitle = computed(() => isEditing.value ? 'Edit Network Device' : 'Add Network Device')

const onlineCount = computed(() => networkDevices.value.filter(d => d.status === 'online').length)
const avgCpuLoad = computed(() => Math.round(networkDevices.value.reduce((sum, d) => sum + d.cpuLoad, 0) / networkDevices.value.length))
const alertCount = computed(() => networkDevices.value.reduce((sum, d) => sum + (d.alerts?.length || 0), 0))

const uniqueBuildings = computed(() => {
  return Array.from(new Set(networkDevices.value.map(d => d.buildingName)))
})

const filteredDevices = computed(() => {
  let filtered = [...networkDevices.value]

  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    filtered = filtered.filter(d =>
        d.name.toLowerCase().includes(keyword) ||
        d.model.toLowerCase().includes(keyword) ||
        d.ipAddress.toLowerCase().includes(keyword)
    )
  }

  if (filterType.value !== 'all') {
    filtered = filtered.filter(d => d.type === filterType.value)
  }

  if (filterBuilding.value !== 'all') {
    filtered = filtered.filter(d => d.buildingName === filterBuilding.value)
  }

  return filtered
})

// Helper functions
const formatNumber = (num: number) => {
  return num.toLocaleString()
}

const getDeviceIcon = (type: string) => {
  const map: Record<string, string> = {
    core: '🖧',
    aggregation: '🖥️',
    access: '🔌',
    router: '🌐',
    firewall: '🛡️',
    loadbalancer: '⚖️'
  }
  return map[type] || '🖧'
}

const getDeviceTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    core: 'Core Switch',
    aggregation: 'Aggregation Switch',
    access: 'Access Switch',
    router: 'Router',
    firewall: 'Firewall',
    loadbalancer: 'Load Balancer'
  }
  return map[type] || type
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    online: 'Online',
    offline: 'Offline',
    maintenance: 'Maintenance'
  }
  return map[status] || status
}

const getUtilizationColor = (percentage: number) => {
  if (percentage >= 85) return '#f56c6c'
  if (percentage >= 70) return '#e6a23c'
  return '#67c23a'
}

const getPacketLossClass = (loss: number) => {
  if (loss > 0.5) return 'packet-loss-high'
  if (loss > 0.1) return 'packet-loss-warning'
  return 'packet-loss-normal'
}

// Device CRUD operations
const openAddDeviceDialog = () => {
  isEditing.value = false
  deviceForm.value = {
    name: '',
    model: '',
    type: 'core',
    buildingId: buildings.value[0]?.id || 1,
    roomName: '',
    rackPosition: '',
    ipAddress: '',
    totalPorts: 0,
    installationDate: null,
    status: 'online',
    description: ''
  }
  showDeviceDialog.value = true
}

const editDevice = (device: NetworkDevice) => {
  isEditing.value = true
  selectedDevice.value = device
  deviceForm.value = {
    name: device.name,
    model: device.model,
    type: device.type,
    buildingId: device.buildingId,
    roomName: device.roomName,
    rackPosition: device.rackPosition,
    ipAddress: device.ipAddress,
    totalPorts: device.totalPorts,
    installationDate: device.installationDate,
    status: device.status,
    description: device.description || ''
  }
  showDeviceDialog.value = true
}

const saveDevice = () => {
  if (!deviceForm.value.name.trim()) {
    ElMessage.warning('Please enter device name')
    return
  }

  const building = buildings.value.find(b => b.id === deviceForm.value.buildingId)

  if (!building) {
    ElMessage.warning('Please select a building')
    return
  }

  if (isEditing.value && selectedDevice.value) {
    const index = networkDevices.value.findIndex(d => d.id === selectedDevice.value!.id)
    if (index !== -1) {
      networkDevices.value[index] = {
        ...networkDevices.value[index],
        name: deviceForm.value.name,
        model: deviceForm.value.model,
        type: deviceForm.value.type,
        buildingId: deviceForm.value.buildingId,
        buildingName: building.name,
        roomName: deviceForm.value.roomName,
        rackPosition: deviceForm.value.rackPosition,
        ipAddress: deviceForm.value.ipAddress,
        totalPorts: deviceForm.value.totalPorts,
        status: deviceForm.value.status,
        description: deviceForm.value.description
      }
      ElMessage.success('Network device updated successfully')
    }
  } else {
    const newDevice: NetworkDevice = {
      id: Date.now(),
      name: deviceForm.value.name,
      model: deviceForm.value.model,
      type: deviceForm.value.type,
      buildingId: deviceForm.value.buildingId,
      buildingName: building.name,
      roomName: deviceForm.value.roomName,
      rackPosition: deviceForm.value.rackPosition,
      ipAddress: deviceForm.value.ipAddress,
      cpuLoad: 0,
      memoryUsage: 0,
      temperature: 35,
      uptime: 0,
      totalPorts: deviceForm.value.totalPorts,
      activePorts: 0,
      portUtilization: 0,
      inboundTraffic: 0,
      outboundTraffic: 0,
      packetLoss: 0,
      status: deviceForm.value.status,
      installationDate: deviceForm.value.installationDate as string || new Date().toISOString().split('T')[0],
      lastFirmwareUpdate: new Date().toISOString().split('T')[0],
      alerts: [],
      description: deviceForm.value.description
    }
    networkDevices.value.push(newDevice)
    ElMessage.success('Network device added successfully')
  }

  showDeviceDialog.value = false
}

const viewDevice = (device: NetworkDevice) => {
  selectedDevice.value = device
  showDetailDialog.value = true
}

const deleteDevice = (device: NetworkDevice) => {
  ElMessageBox.confirm(
      `Delete network device "${device.name}"? This will remove all associated configuration data.`,
      'Delete Device',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    const index = networkDevices.value.findIndex(d => d.id === device.id)
    if (index !== -1) {
      networkDevices.value.splice(index, 1)
      ElMessage.success('Network device deleted successfully')
    }
  }).catch(() => {})
}

const exportData = () => {
  const data = JSON.stringify(filteredDevices.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `network_devices_${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Export completed')
}

const refreshData = () => {
  ElMessage.success('Data refreshed')
}

// Loading animation
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
    }, 400)
  }, 2000)
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

.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
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

.loading-tip { font-size: 13px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 8px; font-weight: 500; }
.loading-subtip { font-size: 11px; color: #64748b; letter-spacing: 0.5px; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

/* Main Content */
.network-room {
  padding: 24px;
  background: linear-gradient(135deg, #f0f5ff 0%, #e8f0fe 100%);
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h2 {
  margin: 0 0 4px 0;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #1565c0, #1976d2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  margin: 0;
  color: #1565c0;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 36px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

/* Filter Section */
.filter-section {
  background: white;
  border-radius: 20px;
  padding: 16px 20px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.search-wrapper {
  flex: 1;
  min-width: 250px;
}

.filter-wrapper {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

/* Devices Grid */
.devices-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 20px;
}

.device-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #67c23a;
}

.device-card.offline { border-left-color: #f56c6c; }
.device-card.maintenance { border-left-color: #e6a23c; }
.device-card.online { border-left-color: #67c23a; }

.device-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
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
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.device-info {
  flex: 1;
}

.device-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.device-model {
  font-size: 11px;
  color: #909399;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.status-badge.online { background: #e8f5e9; color: #67c23a; }
.status-badge.offline { background: #ffefef; color: #f56c6c; }
.status-badge.maintenance { background: #fff7e6; color: #e6a23c; }

.device-location {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.device-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.metric-item {
  text-align: center;
}

.metric-value {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: #409eff;
}

.metric-label {
  font-size: 10px;
  color: #909399;
  margin-top: 2px;
}

.port-section {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.port-header {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  margin-bottom: 6px;
}

.port-title {
  font-weight: 600;
  color: #909399;
}

.port-stats {
  color: #409eff;
}

.port-bar {
  margin-top: 4px;
}

.traffic-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 12px;
}

.traffic-item {
  text-align: center;
  font-size: 11px;
}

.traffic-label {
  display: block;
  color: #909399;
  margin-bottom: 4px;
}

.traffic-value {
  font-weight: 600;
  color: #303133;
}

.packet-loss-normal { color: #67c23a; }
.packet-loss-warning { color: #e6a23c; }
.packet-loss-high { color: #f56c6c; }

.device-alerts {
  background: #fff7e6;
  border-radius: 12px;
  padding: 10px;
  margin-bottom: 16px;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: #e6a23c;
  margin-bottom: 4px;
}

.alert-more {
  font-size: 10px;
  color: #909399;
  margin-top: 4px;
  text-align: right;
}

.device-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 60px;
  background: white;
  border-radius: 20px;
  margin-top: 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: #909399;
  margin-bottom: 24px;
}

/* Detail Dialog */
.detail-alerts {
  margin-top: 20px;
}

.detail-alerts h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
}

:deep(.el-dialog__body) {
  padding: 20px;
}

/* Responsive */
@media (max-width: 768px) {
  .network-room { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .filter-section { flex-direction: column; }
  .search-wrapper { width: 100%; }
  .filter-wrapper { width: 100%; justify-content: space-between; }
  .devices-grid { grid-template-columns: 1fr; }
  .device-metrics { grid-template-columns: repeat(2, 1fr); }
  .traffic-info { flex-wrap: wrap; gap: 8px; }
}
</style>