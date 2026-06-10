<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, Refresh, View, Edit, Delete, Monitor, Connection,
  CircleCheck, DataLine, Message, Cpu, Setting
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing...',
  'Almost ready...'
]

// ==================== Chart Refs ====================
const messageRateChart = ref<HTMLElement | null>(null)
const deviceStatusChart = ref<HTMLElement | null>(null)
const throughputChart = ref<HTMLElement | null>(null)

// ==================== State ====================
const activeTab = ref('adapters')
const searchKeyword = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const deviceSearch = ref('')
const selectedAdapterForMapping = ref<number | null>(null)
const adapterDialogVisible = ref(false)
const testDialogVisible = ref(false)
const mappingDialogVisible = ref(false)
const commandDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const testing = ref(false)
const adapterFormRef = ref()
const testPayload = ref('')
const testResult = ref<any>(null)

// ==================== Statistics ====================
const statistics = reactive({
  totalAdapters: 12,
  activeAdapters: 8,
  totalDevices: 156,
  totalMessages: 28430
})

// ==================== Types ====================
interface Adapter {
  id: number
  name: string
  type: string
  protocol: string
  endpoint: string
  deviceCount: number
  status: 'active' | 'inactive' | 'error'
  messageRate: number
  lastActive: string
  description: string
  config: string
}

interface PayloadMapping {
  id: number
  sourceField: string
  targetField: string
  dataType: string
  transformation: string
}

interface Device {
  id: number
  deviceId: string
  name: string
  adapter: string
  status: 'online' | 'offline' | 'error'
  lastData: string
}

// ==================== Adapters Data ====================
const adapters = ref<Adapter[]>([
  {
    id: 1,
    name: 'ESP32 Gateway Adapter',
    type: 'esp32',
    protocol: 'MQTT',
    endpoint: 'mqtt://iot.eclipse.org:1883',
    deviceCount: 45,
    status: 'active',
    messageRate: 142,
    lastActive: new Date().toISOString(),
    description: 'Adapter for ESP32-based sensor networks',
    config: '{"keepAlive": 60, "qos": 1}'
  },
  {
    id: 2,
    name: 'BLE Beacon Scanner',
    type: 'ble',
    protocol: 'BLE',
    endpoint: 'ble://hci0',
    deviceCount: 23,
    status: 'active',
    messageRate: 89,
    lastActive: new Date().toISOString(),
    description: 'Bluetooth Low Energy beacon scanner',
    config: '{"scanDuration": 5, "activeScan": true}'
  },
  {
    id: 3,
    name: 'LoRaWAN Network Server',
    type: 'lorawan',
    protocol: 'LoRaWAN',
    endpoint: 'https://lorawan.example.com/api',
    deviceCount: 67,
    status: 'active',
    messageRate: 234,
    lastActive: new Date().toISOString(),
    description: 'LoRaWAN gateway integration',
    config: '{"band": "EU868", "confirmed": false}'
  },
  {
    id: 4,
    name: 'Smart Toilet Monitor',
    type: 'generic',
    protocol: 'HTTP',
    endpoint: 'https://api.toilet.example.com/webhook',
    deviceCount: 12,
    status: 'error',
    messageRate: 0,
    lastActive: new Date(Date.now() - 3600000).toISOString(),
    description: 'Smart toilet occupancy and consumables monitoring',
    config: '{"timeout": 30, "retries": 3}'
  },
  {
    id: 5,
    name: 'Custom TCP Sensor Hub',
    type: 'generic',
    protocol: 'TCP',
    endpoint: 'tcp://192.168.1.100:5020',
    deviceCount: 9,
    status: 'inactive',
    messageRate: 0,
    lastActive: new Date(Date.now() - 86400000).toISOString(),
    description: 'Custom TCP protocol for legacy sensors',
    config: '{"bufferSize": 1024, "delimiter": "\\r\\n"}'
  }
])

// ==================== Payload Mappings ====================
const payloadMappings = ref<PayloadMapping[]>([
  {
    id: 1,
    sourceField: 'payload.temperature',
    targetField: 'temp_celsius',
    dataType: 'number',
    transformation: 'value => value'
  },
  {
    id: 2,
    sourceField: 'payload.humidity',
    targetField: 'relative_humidity',
    dataType: 'number',
    transformation: 'value => value'
  },
  {
    id: 3,
    sourceField: 'payload.battery',
    targetField: 'battery_level',
    dataType: 'number',
    transformation: 'value => value * 100'
  }
])

// ==================== Devices Data ====================
const devices = ref<Device[]>([
  { id: 1, deviceId: 'esp32_001', name: 'Temperature Sensor - Lobby', adapter: 'ESP32 Gateway', status: 'online', lastData: new Date().toISOString() },
  { id: 2, deviceId: 'esp32_002', name: 'Temperature Sensor - Office', adapter: 'ESP32 Gateway', status: 'online', lastData: new Date().toISOString() },
  { id: 3, deviceId: 'ble_beacon_001', name: 'Occupancy Beacon - Room 101', adapter: 'BLE Beacon Scanner', status: 'online', lastData: new Date().toISOString() },
  { id: 4, deviceId: 'lorawan_001', name: 'Water Meter', adapter: 'LoRaWAN Network', status: 'offline', lastData: new Date(Date.now() - 7200000).toISOString() },
  { id: 5, deviceId: 'toilet_001', name: 'Smart Toilet - Floor 1', adapter: 'Smart Toilet Monitor', status: 'error', lastData: new Date(Date.now() - 3600000).toISOString() }
])

// ==================== Current Adapter for Editing ====================
const currentAdapter = ref({
  id: 0,
  name: '',
  protocol: '',
  type: '',
  endpoint: '',
  description: '',
  config: ''
})

// ==================== Form Rules ====================
const adapterRules = {
  name: [{ required: true, message: 'Please enter adapter name', trigger: 'blur' }],
  protocol: [{ required: true, message: 'Please select protocol', trigger: 'change' }],
  endpoint: [{ required: true, message: 'Please enter endpoint', trigger: 'blur' }]
}

// ==================== Command Data ====================
const commandData = ref({
  commandType: 'read',
  payload: ''
})

// ==================== New Mapping ====================
const newMapping = ref({
  sourceField: '',
  targetField: '',
  dataType: 'number',
  transformation: ''
})

// ==================== Computed ====================
const filteredAdapters = computed(() => {
  let filtered = adapters.value
  if (searchKeyword.value) {
    filtered = filtered.filter(a =>
        a.name.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (statusFilter.value) {
    filtered = filtered.filter(a => a.status === statusFilter.value)
  }
  return filtered
})

const filteredDevices = computed(() => {
  if (!deviceSearch.value) return devices.value
  return devices.value.filter(d =>
      d.name.toLowerCase().includes(deviceSearch.value.toLowerCase()) ||
      d.deviceId.toLowerCase().includes(deviceSearch.value.toLowerCase())
  )
})

// ==================== Methods ====================
const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    active: 'success',
    inactive: 'info',
    error: 'danger'
  }
  return types[status] || 'info'
}

const getAdapterTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    esp32: 'primary',
    arduino: 'success',
    raspberry: 'warning',
    generic: 'info',
    ble: 'danger',
    lorawan: ''
  }
  return colors[type] || 'info'
}

const formatTime = (timestamp: string) => {
  if (!timestamp) return 'Never'
  const date = new Date(timestamp)
  return date.toLocaleString()
}

const handleCreateAdapter = () => {
  dialogMode.value = 'create'
  currentAdapter.value = {
    id: 0,
    name: '',
    protocol: '',
    type: '',
    endpoint: '',
    description: '',
    config: ''
  }
  adapterDialogVisible.value = true
}

const handleEditAdapter = (adapter: Adapter) => {
  dialogMode.value = 'edit'
  let formattedConfig = adapter.config
  try {
    formattedConfig = JSON.stringify(JSON.parse(adapter.config), null, 2)
  } catch (e) {
    formattedConfig = adapter.config
  }
  currentAdapter.value = { ...adapter, config: formattedConfig }
  adapterDialogVisible.value = true
}

const handleSaveAdapter = async () => {
  await adapterFormRef.value?.validate()
  if (dialogMode.value === 'create') {
    const newAdapter: Adapter = {
      id: Math.max(...adapters.value.map(a => a.id)) + 1,
      name: currentAdapter.value.name,
      type: currentAdapter.value.type,
      protocol: currentAdapter.value.protocol,
      endpoint: currentAdapter.value.endpoint,
      deviceCount: 0,
      status: 'inactive',
      messageRate: 0,
      lastActive: new Date().toISOString(),
      description: currentAdapter.value.description,
      config: currentAdapter.value.config
    }
    adapters.value.push(newAdapter)
    ElMessage.success('Adapter created successfully')
  } else {
    const index = adapters.value.findIndex(a => a.id === currentAdapter.value.id)
    if (index !== -1) {
      adapters.value[index] = { ...adapters.value[index], ...currentAdapter.value }
      ElMessage.success('Adapter updated successfully')
    }
  }
  adapterDialogVisible.value = false
}

const handleDeleteAdapter = (adapter: Adapter) => {
  ElMessageBox.confirm(
      `Are you sure you want to delete adapter "${adapter.name}"? This action cannot be undone.`,
      'Confirm Delete',
      { type: 'warning' }
  ).then(() => {
    const index = adapters.value.findIndex(a => a.id === adapter.id)
    if (index !== -1) {
      adapters.value.splice(index, 1)
      ElMessage.success('Adapter deleted successfully')
    }
  }).catch(() => {})
}

const handleViewAdapter = (adapter: Adapter) => {
  ElMessage.info(`Viewing adapter: ${adapter.name}`)
}

const handleTestAdapter = (adapter: Adapter) => {
  selectedAdapterForMapping.value = adapter.id
  testPayload.value = ''
  testResult.value = null
  testDialogVisible.value = true
}

const handleRunTest = async () => {
  testing.value = true
  setTimeout(() => {
    try {
      const payload = JSON.parse(testPayload.value || '{"test": "data"}')
      testResult.value = {
        success: true,
        message: 'Test completed successfully',
        mappedData: {
          device_id: 'test_device',
          timestamp: new Date().toISOString(),
          ...payload
        },
        processingTime: Math.floor(Math.random() * 50) + 10
      }
      ElMessage.success('Test completed successfully')
    } catch (e) {
      testResult.value = {
        success: false,
        error: 'Invalid JSON payload',
        details: (e as Error).message
      }
      ElMessage.error('Invalid JSON payload')
    }
    testing.value = false
  }, 1500)
}

const handleRefresh = () => {
  ElMessage.info('Refreshing data...')
  setTimeout(() => {
    statistics.totalMessages += Math.floor(Math.random() * 100)
    ElMessage.success('Data refreshed')
  }, 500)
}

const handleAddMapping = () => {
  if (!selectedAdapterForMapping.value) {
    ElMessage.warning('Please select an adapter first')
    return
  }
  newMapping.value = {
    sourceField: '',
    targetField: '',
    dataType: 'number',
    transformation: ''
  }
  mappingDialogVisible.value = true
}

const handleSaveMapping = () => {
  if (!newMapping.value.sourceField || !newMapping.value.targetField) {
    ElMessage.warning('Please fill in source and target fields')
    return
  }
  payloadMappings.value.push({
    id: Math.max(...payloadMappings.value.map(m => m.id), 0) + 1,
    ...newMapping.value
  })
  mappingDialogVisible.value = false
  ElMessage.success('Mapping added successfully')
}

const handleEditMapping = (mapping: PayloadMapping) => {
  newMapping.value = { ...mapping }
  mappingDialogVisible.value = true
}

const handleDeleteMapping = (mapping: PayloadMapping) => {
  const index = payloadMappings.value.findIndex(m => m.id === mapping.id)
  if (index !== -1) {
    payloadMappings.value.splice(index, 1)
    ElMessage.success('Mapping deleted successfully')
  }
}

const handleTestMapping = () => {
  ElMessage.info('Testing mapping configuration...')
}

const handleAddDevice = () => {
  ElMessage.info('Add device functionality coming soon')
}

const handleViewDevice = (device: Device) => {
  ElMessage.info(`Viewing device: ${device.name}`)
}

const handleSendCommand = (device: Device) => {
  commandData.value = { commandType: 'read', payload: '' }
  commandDialogVisible.value = true
}

const handleExecuteCommand = () => {
  ElMessage.success(`Command ${commandData.value.commandType} sent successfully`)
  commandDialogVisible.value = false
}

const handleDeleteDevice = (device: Device) => {
  ElMessageBox.confirm(
      `Are you sure you want to delete device "${device.name}"?`,
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

// ==================== Initialize Charts ====================
const initCharts = () => {
  if (!messageRateChart.value) return

  // Message Rate Chart (Line)
  const rateChart = echarts.init(messageRateChart.value)
  rateChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'] },
    yAxis: { type: 'value', name: 'Messages/s' },
    series: [{
      data: [82, 45, 123, 267, 298, 156],
      type: 'line',
      smooth: true,
      areaStyle: { opacity: 0.3 },
      lineStyle: { color: '#1890ff', width: 2 },
      itemStyle: { color: '#1890ff' }
    }]
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
        { value: 89, name: 'Online', itemStyle: { color: '#52c41a' } },
        { value: 45, name: 'Offline', itemStyle: { color: '#ff4d4f' } },
        { value: 22, name: 'Error', itemStyle: { color: '#faad14' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })

  // Throughput Chart (Bar)
  const throughput = echarts.init(throughputChart.value)
  throughput.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'category', data: ['ESP32', 'BLE', 'LoRaWAN', 'HTTP', 'TCP'] },
    yAxis: { type: 'value', name: 'Messages/hour' },
    series: [{
      data: [12500, 8900, 21400, 3400, 2100],
      type: 'bar',
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#1890ff' }
    }]
  })

  // Handle resize
  window.addEventListener('resize', () => {
    rateChart.resize()
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
          <span class="loading-title">Loading Custom IoT Adapter</span>
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
  <div v-else class="custom-iot-adapter">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2>Custom IoT Adapter</h2>
        <p>Configure and manage custom protocol adapters for IoT devices, supporting device integration, data mapping, and command forwarding</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleCreateAdapter">
          <el-icon><Plus /></el-icon>
          New Adapter
        </el-button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-cards">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #e8f4ff">
            <el-icon color="#1890ff" size="28"><Connection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.totalAdapters }}</div>
            <div class="stat-label">Total Adapters</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #e6f7e6">
            <el-icon color="#52c41a" size="28"><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.activeAdapters }}</div>
            <div class="stat-label">Active Adapters</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #fff7e6">
            <el-icon color="#faad14" size="28"><DataLine /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.totalDevices }}</div>
            <div class="stat-label">Connected Devices</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #fdf0e8">
            <el-icon color="#ff7a45" size="28"><Message /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.totalMessages }}</div>
            <div class="stat-label">Messages Today</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Tabs -->
    <el-tabs v-model="activeTab" class="adapter-tabs">
      <!-- Adapters List Tab -->
      <el-tab-pane label="Adapters" name="adapters">
        <div class="toolbar">
          <div class="toolbar-left">
            <el-input
                v-model="searchKeyword"
                placeholder="Search adapters..."
                clearable
                style="width: 260px"
                :prefix-icon="Search"
            />
            <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
              <el-option label="All" value="" />
              <el-option label="Active" value="active" />
              <el-option label="Inactive" value="inactive" />
              <el-option label="Error" value="error" />
            </el-select>
            <el-button @click="handleRefresh">
              <el-icon><Refresh /></el-icon>
              Refresh
            </el-button>
          </div>
        </div>

        <el-table :data="filteredAdapters" style="width: 100%; margin-top: 16px" stripe>
          <el-table-column prop="name" label="Adapter Name" min-width="180">
            <template #default="{ row }">
              <div class="adapter-name">
                <el-tag :type="getAdapterTypeColor(row.type)" size="small">{{ row.type }}</el-tag>
                <span style="margin-left: 8px">{{ row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="protocol" label="Protocol" width="120">
            <template #default="{ row }">
              <el-tag effect="plain">{{ row.protocol }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="deviceCount" label="Devices" width="100" align="center" />
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">
                {{ row.status.toUpperCase() }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="messageRate" label="Msg Rate" width="100">
            <template #default="{ row }">
              <span>{{ row.messageRate }}/s</span>
            </template>
          </el-table-column>
          <el-table-column prop="lastActive" label="Last Active" width="180">
            <template #default="{ row }">
              {{ formatTime(row.lastActive) }}
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="280" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="handleViewAdapter(row)">
                <el-icon><View /></el-icon>
                View
              </el-button>
              <el-button link type="primary" size="small" @click="handleEditAdapter(row)">
                <el-icon><Edit /></el-icon>
                Edit
              </el-button>
              <el-button link type="primary" size="small" @click="handleTestAdapter(row)">
                <el-icon><Monitor /></el-icon>
                Test
              </el-button>
              <el-button link type="danger" size="small" @click="handleDeleteAdapter(row)">
                <el-icon><Delete /></el-icon>
                Delete
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- Pagination -->
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="filteredAdapters.length"
            layout="total, sizes, prev, pager, next, jumper"
            style="margin-top: 20px; justify-content: flex-end"
        />
      </el-tab-pane>

      <!-- Payload Mapping Tab -->
      <el-tab-pane label="Payload Mapping" name="mapping">
        <div class="mapping-container">
          <div class="mapping-header">
            <div class="mapping-header-left">
              <el-select v-model="selectedAdapterForMapping" placeholder="Select Adapter" style="width: 240px">
                <el-option
                    v-for="adapter in adapters"
                    :key="adapter.id"
                    :label="adapter.name"
                    :value="adapter.id"
                />
              </el-select>
              <el-button type="primary" @click="handleAddMapping" :disabled="!selectedAdapterForMapping">
                <el-icon><Plus /></el-icon>
                Add Mapping
              </el-button>
            </div>
            <el-button @click="handleTestMapping">
              <el-icon><Cpu /></el-icon>
              Test Mapping
            </el-button>
          </div>

          <el-table :data="payloadMappings" style="width: 100%; margin-top: 16px" stripe>
            <el-table-column prop="sourceField" label="Source Field" min-width="150">
              <template #default="{ row }">
                <code>{{ row.sourceField }}</code>
              </template>
            </el-table-column>
            <el-table-column prop="targetField" label="Target Field" min-width="150">
              <template #default="{ row }">
                <code>{{ row.targetField }}</code>
              </template>
            </el-table-column>
            <el-table-column prop="dataType" label="Data Type" width="120">
              <template #default="{ row }">
                <el-tag size="small">{{ row.dataType }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="transformation" label="Transformation" width="180">
              <template #default="{ row }">
                <code v-if="row.transformation" class="transformation-code">{{ row.transformation }}</code>
                <span v-else class="text-muted">None</span>
              </template>
            </el-table-column>
            <el-table-column label="Actions" width="150">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="handleEditMapping(row)">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button link type="danger" size="small" @click="handleDeleteMapping(row)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- Device Management Tab -->
      <el-tab-pane label="Devices" name="devices">
        <div class="toolbar">
          <el-input
              v-model="deviceSearch"
              placeholder="Search devices..."
              clearable
              style="width: 260px"
              :prefix-icon="Search"
          />
          <el-button type="primary" @click="handleAddDevice">
            <el-icon><Plus /></el-icon>
            Add Device
          </el-button>
        </div>

        <el-table :data="filteredDevices" style="width: 100%; margin-top: 16px" stripe>
          <el-table-column prop="deviceId" label="Device ID" width="180">
            <template #default="{ row }">
              <code>{{ row.deviceId }}</code>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="Device Name" min-width="150" />
          <el-table-column prop="adapter" label="Adapter" width="150">
            <template #default="{ row }">
              {{ row.adapter }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'online' ? 'success' : 'danger'" size="small">
                {{ row.status.toUpperCase() }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="lastData" label="Last Data" width="180">
            <template #default="{ row }">
              {{ formatTime(row.lastData) }}
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="180">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="handleViewDevice(row)">
                <el-icon><View /></el-icon>
              </el-button>
              <el-button link type="primary" size="small" @click="handleSendCommand(row)">
                <el-icon><Message /></el-icon>
              </el-button>
              <el-button link type="danger" size="small" @click="handleDeleteDevice(row)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Monitoring Tab -->
      <el-tab-pane label="Monitoring" name="monitoring">
        <div class="monitoring-container">
          <!-- Charts Row -->
          <el-row :gutter="16">
            <el-col :xs="24" :sm="12">
              <el-card class="chart-card" header="Message Rate (msg/s)">
                <div ref="messageRateChart" style="height: 300px"></div>
              </el-card>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-card class="chart-card" header="Device Status Distribution">
                <div ref="deviceStatusChart" style="height: 300px"></div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="16" style="margin-top: 16px">
            <el-col :span="24">
              <el-card class="chart-card" header="Throughput by Adapter (messages/hour)">
                <div ref="throughputChart" style="height: 300px"></div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Create/Edit Adapter Dialog -->
    <el-dialog
        v-model="adapterDialogVisible"
        :title="dialogMode === 'create' ? 'New Adapter' : 'Edit Adapter'"
        width="600px"
    >
      <el-form :model="currentAdapter" :rules="adapterRules" ref="adapterFormRef" label-width="120px">
        <el-form-item label="Adapter Name" prop="name">
          <el-input v-model="currentAdapter.name" placeholder="Enter adapter name" />
        </el-form-item>
        <el-form-item label="Protocol Type" prop="protocol">
          <el-select v-model="currentAdapter.protocol" placeholder="Select protocol" style="width: 100%">
            <el-option label="MQTT" value="MQTT" />
            <el-option label="CoAP" value="CoAP" />
            <el-option label="HTTP/Webhook" value="HTTP" />
            <el-option label="WebSocket" value="WebSocket" />
            <el-option label="TCP Custom" value="TCP" />
            <el-option label="UDP Custom" value="UDP" />
          </el-select>
        </el-form-item>
        <el-form-item label="Adapter Type" prop="type">
          <el-select v-model="currentAdapter.type" placeholder="Select type" style="width: 100%">
            <el-option label="ESP32 Adapter" value="esp32" />
            <el-option label="Arduino Adapter" value="arduino" />
            <el-option label="Raspberry Pi" value="raspberry" />
            <el-option label="Generic IoT" value="generic" />
            <el-option label="BLE Gateway" value="ble" />
            <el-option label="LoRaWAN" value="lorawan" />
          </el-select>
        </el-form-item>
        <el-form-item label="Endpoint" prop="endpoint">
          <el-input v-model="currentAdapter.endpoint" placeholder="e.g., mqtt://localhost:1883" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input
              v-model="currentAdapter.description"
              type="textarea"
              :rows="3"
              placeholder="Enter description"
          />
        </el-form-item>
        <el-form-item label="Configuration" prop="config">
          <el-input
              v-model="currentAdapter.config"
              type="textarea"
              :rows="4"
              placeholder='{"keepAlive": 60, "qos": 1}'
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="adapterDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleSaveAdapter">Save</el-button>
      </template>
    </el-dialog>

    <!-- Test Adapter Dialog -->
    <el-dialog v-model="testDialogVisible" title="Test Adapter" width="700px">
      <div class="test-container">
        <el-input
            v-model="testPayload"
            type="textarea"
            :rows="6"
            placeholder='{"device_id": "sensor_001", "temperature": 25.5, "humidity": 65}'
        />
        <div class="test-actions" style="margin-top: 16px">
          <el-button type="primary" @click="handleRunTest" :loading="testing">
            <el-icon><Cpu /></el-icon>
            Run Test
          </el-button>
          <el-button @click="testDialogVisible = false">Close</el-button>
        </div>
        <div v-if="testResult" class="test-result" style="margin-top: 16px">
          <h4>Test Result:</h4>
          <pre>{{ JSON.stringify(testResult, null, 2) }}</pre>
        </div>
      </div>
    </el-dialog>

    <!-- Send Command Dialog -->
    <el-dialog v-model="commandDialogVisible" title="Send Command to Device" width="500px">
      <el-form :model="commandData" label-width="100px">
        <el-form-item label="Command Type">
          <el-select v-model="commandData.commandType" placeholder="Select command" style="width: 100%">
            <el-option label="Read Data" value="read" />
            <el-option label="Write Value" value="write" />
            <el-option label="Set Parameter" value="set" />
            <el-option label="Reboot Device" value="reboot" />
            <el-option label="Update Firmware" value="update" />
          </el-select>
        </el-form-item>
        <el-form-item label="Command Payload">
          <el-input
              v-model="commandData.payload"
              type="textarea"
              :rows="4"
              placeholder='{"param": "value"}'
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="commandDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleExecuteCommand">Send</el-button>
      </template>
    </el-dialog>

    <!-- Add Mapping Dialog -->
    <el-dialog v-model="mappingDialogVisible" title="Add Payload Mapping" width="550px">
      <el-form :model="newMapping" label-width="120px">
        <el-form-item label="Source Field">
          <el-input v-model="newMapping.sourceField" placeholder="e.g., payload.temp" />
        </el-form-item>
        <el-form-item label="Target Field">
          <el-input v-model="newMapping.targetField" placeholder="e.g., temperature" />
        </el-form-item>
        <el-form-item label="Data Type">
          <el-select v-model="newMapping.dataType" placeholder="Select data type">
            <el-option label="Number" value="number" />
            <el-option label="String" value="string" />
            <el-option label="Boolean" value="boolean" />
            <el-option label="Object" value="object" />
            <el-option label="Array" value="array" />
          </el-select>
        </el-form-item>
        <el-form-item label="Transformation (JS)">
          <el-input
              v-model="newMapping.transformation"
              type="textarea"
              :rows="3"
              placeholder="value => value * 1.8 + 32"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="mappingDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleSaveMapping">Save</el-button>
      </template>
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
.custom-iot-adapter {
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

.adapter-tabs {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.toolbar-left {
  display: flex;
  gap: 12px;
  align-items: center;
}

.adapter-name {
  display: flex;
  align-items: center;
}

.mapping-container {
  padding: 16px 0;
}

.mapping-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.mapping-header-left {
  display: flex;
  gap: 16px;
}

.text-muted {
  color: #999;
  font-style: italic;
}

.transformation-code {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.monitoring-container {
  padding: 16px 0;
}

.chart-card {
  margin-bottom: 0;
}

.test-container pre {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
  margin: 0;
}

.test-result h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
}

:deep(.el-card__header) {
  font-weight: 600;
  background-color: #fafafa;
  border-bottom: 1px solid #f0f0f0;
}

:deep(.el-tabs__header) {
  margin-bottom: 20px;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-button--link) {
  padding: 0 4px;
}

@media (max-width: 1200px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
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
  }

  .toolbar {
    flex-direction: column;
    gap: 12px;
  }

  .toolbar-left {
    width: 100%;
  }
}
</style>