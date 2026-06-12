<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Search, Refresh, Connection, Setting, VideoPlay,
  DataLine, Document, CircleCheck, CircleClose,
  Loading, Clock, TrendCharts, Monitor, Link, Cellphone, Share, Warning
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing network scanner...',
  'Preparing ping utility...',
  'Loading device database...',
  'Setting up protocols...',
  'Almost ready...'
]

// ==================== Component State ====================
const testing = ref(false)
const searchKeyword = ref('')
const selectedProtocol = ref('all')
const selectedStatus = ref('all')
const testResultsVisible = ref(false)
const detailsVisible = ref(false)
const chartRef = ref(null)

let successChart: echarts.ECharts | null = null

// Protocols
const protocols = [
  { value: 'all', label: 'All Protocols' },
  { value: 'bacnet', label: 'BACnet/IP', port: 47808 },
  { value: 'modbus', label: 'Modbus TCP', port: 502 },
  { value: 'mqtt', label: 'MQTT', port: 1883 },
  { value: 'opcua', label: 'OPC-UA', port: 4840 },
  { value: 'snmp', label: 'SNMP', port: 161 },
  { value: 'http', label: 'HTTP', port: 80 },
  { value: 'https', label: 'HTTPS', port: 443 }
]

// Devices for connectivity testing
const devices = ref([
  { id: 'DEV001', name: 'Building A - BMS Controller', ip: '192.168.1.100', protocol: 'bacnet', port: 47808, status: 'online', latency: 12, lastTest: '2024-01-15 10:23:45', packetLoss: 0, firmware: 'v2.1.0' },
  { id: 'DEV002', name: 'Chiller Plant Controller', ip: '192.168.1.101', protocol: 'bacnet', port: 47808, status: 'online', latency: 15, lastTest: '2024-01-15 10:22:30', packetLoss: 0, firmware: 'v1.8.2' },
  { id: 'DEV003', name: 'AHU-1 Controller', ip: '192.168.1.102', protocol: 'bacnet', port: 47808, status: 'online', latency: 8, lastTest: '2024-01-15 10:24:12', packetLoss: 0, firmware: 'v2.0.5' },
  { id: 'DEV004', name: 'Power Meter - Main', ip: '192.168.2.100', protocol: 'modbus', port: 502, status: 'online', latency: 25, lastTest: '2024-01-15 10:20:00', packetLoss: 0, firmware: 'v1.2.0' },
  { id: 'DEV005', name: 'Lighting Panel - L1', ip: '192.168.2.101', protocol: 'modbus', port: 502, status: 'offline', latency: null, lastTest: '2024-01-14 18:30:00', packetLoss: 100, firmware: 'v1.0.0' },
  { id: 'DEV006', name: 'Temperature Sensors Hub', ip: '192.168.3.100', protocol: 'mqtt', port: 1883, status: 'online', latency: 18, lastTest: '2024-01-15 10:23:00', packetLoss: 0, firmware: 'v3.2.1' },
  { id: 'DEV007', name: 'VFD Pump Controller', ip: '192.168.2.102', protocol: 'modbus', port: 502, status: 'online', latency: 22, lastTest: '2024-01-15 10:22:15', packetLoss: 2, firmware: 'v2.1.0' },
  { id: 'DEV008', name: 'OPC-UA Gateway', ip: '192.168.4.100', protocol: 'opcua', port: 4840, status: 'online', latency: 35, lastTest: '2024-01-15 10:21:30', packetLoss: 0, firmware: 'v1.5.0' },
  { id: 'DEV009', name: 'Network Switch - Core', ip: '192.168.0.1', protocol: 'snmp', port: 161, status: 'online', latency: 5, lastTest: '2024-01-15 10:24:30', packetLoss: 0, firmware: 'v12.0.1' },
  { id: 'DEV010', name: 'Fire Alarm Panel', ip: '192.168.5.100', protocol: 'bacnet', port: 47808, status: 'warning', latency: 45, lastTest: '2024-01-15 10:19:45', packetLoss: 5, firmware: 'v2.2.0' },
  { id: 'DEV011', name: 'Access Controller - Main', ip: '192.168.6.100', protocol: 'modbus', port: 502, status: 'online', latency: 28, lastTest: '2024-01-15 10:23:20', packetLoss: 0, firmware: 'v3.0.0' },
  { id: 'DEV012', name: 'Weather Station', ip: '192.168.7.100', protocol: 'mqtt', port: 1883, status: 'offline', latency: null, lastTest: '2024-01-14 15:45:00', packetLoss: 100, firmware: 'v1.1.0' }
])

// Test logs
const testLogs = ref([
  { id: 'L001', timestamp: '2024-01-15 10:23:45', device: 'Building A - BMS Controller', status: 'success', message: 'Connection successful, latency: 12ms' },
  { id: 'L002', timestamp: '2024-01-15 10:22:30', device: 'Chiller Plant Controller', status: 'success', message: 'Connection successful, latency: 15ms' },
  { id: 'L003', timestamp: '2024-01-15 10:20:00', device: 'Lighting Panel - L1', status: 'failed', message: 'Connection timeout after 5000ms' },
  { id: 'L004', timestamp: '2024-01-15 10:19:45', device: 'Fire Alarm Panel', status: 'warning', message: 'High latency detected: 45ms, packet loss: 5%' },
  { id: 'L005', timestamp: '2024-01-15 10:15:00', device: 'Weather Station', status: 'failed', message: 'Device unreachable' }
])

// Connectivity statistics
const connectivityStats = reactive({
  total: 0,
  online: 0,
  offline: 0,
  warning: 0,
  avgLatency: 0,
  minLatency: 0,
  maxLatency: 0,
  successRate: 0,
  lastScanTime: ''
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: devices.value.length
})

// Filtered devices
const filteredDevices = computed(() => {
  let filtered = devices.value
  if (searchKeyword.value) {
    filtered = filtered.filter(d =>
        d.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        d.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        d.ip.includes(searchKeyword.value) ||
        d.protocol.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedProtocol.value !== 'all') {
    filtered = filtered.filter(d => d.protocol === selectedProtocol.value)
  }
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(d => d.status === selectedStatus.value)
  }
  pagination.total = filtered.length
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// ==================== Loading Simulation ====================
onMounted(() => {
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 12 + 4
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
        initChart()
        updateStats()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  successChart = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  const protocolStats = protocols.filter(p => p.value !== 'all').map(protocol => {
    const deviceList = devices.value.filter(d => d.protocol === protocol.value)
    const online = deviceList.filter(d => d.status === 'online').length
    const warning = deviceList.filter(d => d.status === 'warning').length
    const offline = deviceList.filter(d => d.status === 'offline').length
    return { protocol: protocol.label, online, warning, offline }
  })

  successChart?.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['Online', 'Warning', 'Offline'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: protocolStats.map(p => p.protocol) },
    yAxis: { type: 'value', name: 'Device Count' },
    series: [
      { name: 'Online', type: 'bar', data: protocolStats.map(p => p.online), stack: 'total', itemStyle: { color: '#67C23A', borderRadius: [4, 4, 0, 0] } },
      { name: 'Warning', type: 'bar', data: protocolStats.map(p => p.warning), stack: 'total', itemStyle: { color: '#E6A23C', borderRadius: [4, 4, 0, 0] } },
      { name: 'Offline', type: 'bar', data: protocolStats.map(p => p.offline), stack: 'total', itemStyle: { color: '#F56C6C', borderRadius: [4, 4, 0, 0] } }
    ]
  })
}

const updateStats = () => {
  const onlineDevices = devices.value.filter(d => d.status === 'online')
  const warningDevices = devices.value.filter(d => d.status === 'warning')
  const offlineDevices = devices.value.filter(d => d.status === 'offline')

  connectivityStats.total = devices.value.length
  connectivityStats.online = onlineDevices.length
  connectivityStats.warning = warningDevices.length
  connectivityStats.offline = offlineDevices.length
  connectivityStats.successRate = (onlineDevices.length / devices.value.length) * 100

  const latencies = onlineDevices.map(d => d.latency).filter(l => l !== null)
  if (latencies.length > 0) {
    connectivityStats.avgLatency = Math.round(latencies.reduce((a, b) => a + b, 0) / latencies.length)
    connectivityStats.minLatency = Math.min(...latencies)
    connectivityStats.maxLatency = Math.max(...latencies)
  }

  connectivityStats.lastScanTime = new Date().toLocaleString()
}

const handleResize = () => {
  successChart?.resize()
}

// ==================== Test Functions ====================
const simulateConnectivityTest = async (device: any): Promise<{ status: string; latency: number; packetLoss: number }> => {
  // Simulate network conditions
  const isOnline = Math.random() > 0.1 // 90% success rate
  const latency = isOnline ? Math.floor(Math.random() * 100) + 1 : null
  const packetLoss = isOnline ? Math.random() * 3 : 100

  let status = 'offline'
  if (isOnline) {
    status = latency && latency > 40 ? 'warning' : 'online'
  }

  await new Promise(resolve => setTimeout(resolve, latency || 1000))

  return { status, latency: latency || 0, packetLoss }
}

const testConnectivity = async (device: any) => {
  const result = await simulateConnectivityTest(device)
  device.status = result.status
  device.latency = result.latency
  device.packetLoss = result.packetLoss
  device.lastTest = new Date().toLocaleString()

  // Add to logs
  testLogs.value.unshift({
    id: `L${Date.now()}`,
    timestamp: new Date().toLocaleString(),
    device: device.name,
    status: result.status === 'online' ? 'success' : result.status === 'warning' ? 'warning' : 'failed',
    message: result.status === 'online'
        ? `Connection successful, latency: ${result.latency}ms, packet loss: ${result.packetLoss}%`
        : result.status === 'warning'
            ? `High latency detected: ${result.latency}ms, packet loss: ${result.packetLoss}%`
            : `Connection timeout after 5000ms`
  })

  updateStats()
  updateChart()

  if (result.status === 'online') {
    ElMessage.success(`${device.name} is online (${result.latency}ms)`)
  } else if (result.status === 'warning') {
    ElMessage.warning(`${device.name} has high latency (${result.latency}ms)`)
  } else {
    ElMessage.error(`${device.name} is offline`)
  }
}

const testAllConnectivity = async () => {
  testing.value = true
  let successCount = 0
  let warningCount = 0
  let failedCount = 0

  for (const device of devices.value) {
    const result = await simulateConnectivityTest(device)
    device.status = result.status
    device.latency = result.latency
    device.packetLoss = result.packetLoss
    device.lastTest = new Date().toLocaleString()

    if (result.status === 'online') successCount++
    else if (result.status === 'warning') warningCount++
    else failedCount++

    // Small delay between tests
    await new Promise(resolve => setTimeout(resolve, 100))
  }

  updateStats()
  updateChart()

  testing.value = false
  ElMessage.success(`Test completed: ${successCount} online, ${warningCount} warning, ${failedCount} offline`)
}

const testByProtocol = async (protocol: string) => {
  testing.value = true
  const devicesToTest = devices.value.filter(d => d.protocol === protocol)

  for (const device of devicesToTest) {
    const result = await simulateConnectivityTest(device)
    device.status = result.status
    device.latency = result.latency
    device.packetLoss = result.packetLoss
    device.lastTest = new Date().toLocaleString()
    await new Promise(resolve => setTimeout(resolve, 50))
  }

  updateStats()
  updateChart()
  testing.value = false
  ElMessage.success(`Protocol ${protocol.toUpperCase()} connectivity test completed`)
}

const refreshDevice = async (device: any) => {
  await testConnectivity(device)
}

const viewDetails = (device: any) => {
  selectedDevice.value = device
  detailsVisible.value = true
}

const viewTestResults = () => {
  testResultsVisible.value = true
}

const exportResults = () => {
  const results = devices.value.map(d => ({
    DeviceID: d.id,
    DeviceName: d.name,
    IP: d.ip,
    Protocol: d.protocol,
    Port: d.port,
    Status: d.status,
    Latency: d.latency,
    PacketLoss: d.packetLoss,
    LastTest: d.lastTest
  }))

  const csv = convertToCSV(results)
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `connectivity_test_${new Date().toISOString()}.csv`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Results exported successfully')
}

const convertToCSV = (data: any[]) => {
  const headers = Object.keys(data[0])
  const rows = data.map(obj => headers.map(header => JSON.stringify(obj[header])).join(','))
  return [headers.join(','), ...rows].join('\n')
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'online': return CircleCheck
    case 'offline': return CircleClose
    case 'warning': return Warning
    default: return Clock
  }
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'online': return 'success'
    case 'offline': return 'danger'
    case 'warning': return 'warning'
    default: return 'info'
  }
}

const getLatencyClass = (latency: number) => {
  if (!latency) return ''
  if (latency < 20) return 'latency-good'
  if (latency < 50) return 'latency-fair'
  return 'latency-poor'
}

const selectedDevice = ref<any>(null)
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
          <span class="loading-title">Loading Connectivity Test</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Protocol Health Check - Connectivity Test</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="connectivity-test-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h2>Connectivity Test</h2>
        <el-tag type="warning" effect="dark">Protocol Health Check</el-tag>
      </div>
      <div class="header-stats">
        <el-tag type="info" effect="plain">ICMP | TCP | UDP</el-tag>
      </div>
    </div>

    <!-- Control Panel -->
    <el-card shadow="never" class="control-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="5">
          <el-select v-model="selectedProtocol" placeholder="Protocol" style="width: 100%" @change="updateChart">
            <el-option v-for="p in protocols" :key="p.value" :label="p.label" :value="p.value" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-select v-model="selectedStatus" placeholder="Status" clearable style="width: 100%">
            <el-option label="All" value="all" />
            <el-option label="Online" value="online" />
            <el-option label="Warning" value="warning" />
            <el-option label="Offline" value="offline" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-input v-model="searchKeyword" placeholder="Search devices..." :prefix-icon="Search" clearable />
        </el-col>
        <el-col :span="6">
          <div class="control-buttons">
            <el-button type="primary" @click="testAllConnectivity" :loading="testing">
              <el-icon><VideoPlay /></el-icon> Test All
            </el-button>
            <el-button @click="exportResults">
              <el-icon><Document /></el-icon> Export
            </el-button>
            <el-button @click="viewTestResults">
              <el-icon><DataLine /></el-icon> Logs
            </el-button>
          </div>
        </el-col>
      </el-row>

      <!-- Quick Protocol Tests -->
      <el-row :gutter="10" class="protocol-buttons" style="margin-top: 15px">
        <el-col :span="2" v-for="p in protocols.slice(1)" :key="p.value">
          <el-button size="small" @click="testByProtocol(p.value)" :loading="testing" style="width: 100%">
            {{ p.label }}
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- Statistics Cards -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon total-icon">
            <el-icon><Share /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ connectivityStats.total }}</div>
            <div class="stat-label">Total Devices</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon online-icon">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ connectivityStats.online }}</div>
            <div class="stat-label">Online</div>
            <el-progress :percentage="connectivityStats.successRate" :color="'#67C23A'" :stroke-width="6" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon warning-icon">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ connectivityStats.warning }}</div>
            <div class="stat-label">Warning</div>
            <div class="stat-sub-value">High Latency</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon latency-icon">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ connectivityStats.avgLatency }}ms</div>
            <div class="stat-label">Avg Latency</div>
            <div class="stat-sub-value">Min: {{ connectivityStats.minLatency }}ms | Max: {{ connectivityStats.maxLatency }}ms</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Connectivity Chart -->
    <el-card shadow="never" class="chart-card">
      <template #header>
        <div class="card-header">
          <span>Connectivity Status by Protocol</span>
          <el-button text type="primary" @click="updateChart">Refresh Chart</el-button>
        </div>
      </template>
      <div ref="chartRef" class="chart" style="height: 320px"></div>
    </el-card>

    <!-- Devices Table -->
    <el-card shadow="never" class="devices-card">
      <template #header>
        <div class="table-header">
          <span>Devices & Connectivity Status</span>
          <div class="table-actions">
            <el-button type="primary" size="small" @click="testAllConnectivity" :loading="testing">
              Test All Devices
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredDevices" stripe style="width: 100%">
        <el-table-column prop="id" label="Device ID" width="90" />
        <el-table-column prop="name" label="Device Name" min-width="180" />
        <el-table-column prop="ip" label="IP Address" width="130" />
        <el-table-column label="Protocol" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.protocol.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="port" label="Port" width="70" align="center" />
        <el-table-column label="Status" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              <el-icon style="margin-right: 4px"><component :is="getStatusIcon(row.status)" /></el-icon>
              {{ row.status === 'online' ? 'Online' : row.status === 'warning' ? 'Warning' : 'Offline' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Latency" width="90" align="center">
          <template #default="{ row }">
            <span v-if="row.latency !== null" :class="getLatencyClass(row.latency)">
              {{ row.latency }}ms
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="Packet Loss" width="100" align="center">
          <template #default="{ row }">
            <span v-if="row.packetLoss !== null" :class="{ 'high-loss': row.packetLoss > 5 }">
              {{ row.packetLoss }}%
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="lastTest" label="Last Test" width="160" />
        <el-table-column label="Actions" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="refreshDevice(row)" :disabled="testing">
              Test
            </el-button>
            <el-button link type="info" size="small" @click="viewDetails(row)">
              Details
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- Test Results Dialog -->
    <el-dialog v-model="testResultsVisible" title="Test Logs" width="800px">
      <el-table :data="testLogs" stripe max-height="400">
        <el-table-column prop="timestamp" label="Timestamp" width="160" />
        <el-table-column prop="device" label="Device" min-width="200" />
        <el-table-column label="Status" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : row.status === 'warning' ? 'warning' : 'danger'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="Message" min-width="250" />
      </el-table>
      <template #footer>
        <el-button type="primary" @click="testResultsVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Device Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="`Device Details - ${selectedDevice?.name}`" width="550px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Device ID">{{ selectedDevice?.id }}</el-descriptions-item>
        <el-descriptions-item label="Device Name">{{ selectedDevice?.name }}</el-descriptions-item>
        <el-descriptions-item label="IP Address">{{ selectedDevice?.ip }}</el-descriptions-item>
        <el-descriptions-item label="Protocol">{{ selectedDevice?.protocol?.toUpperCase() }}</el-descriptions-item>
        <el-descriptions-item label="Port">{{ selectedDevice?.port }}</el-descriptions-item>
        <el-descriptions-item label="Firmware">{{ selectedDevice?.firmware || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusType(selectedDevice?.status)" size="small">
            {{ selectedDevice?.status === 'online' ? 'Online' : selectedDevice?.status === 'warning' ? 'Warning' : 'Offline' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Latency">
          <span v-if="selectedDevice?.latency !== null">{{ selectedDevice?.latency }}ms</span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="Packet Loss">
          <span v-if="selectedDevice?.packetLoss !== null">{{ selectedDevice?.packetLoss }}%</span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="Last Test">{{ selectedDevice?.lastTest || 'Never' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button type="primary" @click="refreshDevice(selectedDevice)" :disabled="testing">Test Again</el-button>
        <el-button @click="detailsVisible = false">Close</el-button>
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

/* ==================== Main Content ==================== */
.connectivity-test-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e4e7ed;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  color: #303133;
}

.control-card {
  margin-bottom: 20px;
}

.control-buttons {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.protocol-buttons {
  margin-top: 15px;
}

.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 10px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
}

.total-icon {
  background-color: #e6f7ff;
  color: #409eff;
}

.online-icon {
  background-color: #f0f9ff;
  color: #67c23a;
}

.warning-icon {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.latency-icon {
  background-color: #fef0f0;
  color: #f56c6c;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.stat-sub-value {
  font-size: 12px;
  color: #67c23a;
  margin-top: 2px;
}

.chart-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.devices-card {
  margin-top: 0;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.table-actions {
  display: flex;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.chart {
  width: 100%;
}

.latency-good {
  color: #67c23a;
  font-weight: bold;
}

.latency-fair {
  color: #e6a23c;
  font-weight: bold;
}

.latency-poor {
  color: #f56c6c;
  font-weight: bold;
}

.high-loss {
  color: #f56c6c;
  font-weight: bold;
}

:deep(.el-card__header) {
  border-bottom: 1px solid #ebeef5;
  padding: 15px 20px;
}

:deep(.el-card__body) {
  padding: 20px;
}

@media (max-width: 1200px) {
  .table-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .control-buttons {
    justify-content: flex-start;
    margin-top: 10px;
  }

  .protocol-buttons .el-col {
    margin-bottom: 10px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>