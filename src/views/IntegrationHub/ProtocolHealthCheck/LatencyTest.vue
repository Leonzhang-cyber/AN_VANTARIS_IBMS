<script setup lang="ts">
import { ref, onMounted, computed, reactive, watch } from 'vue'
import * as echarts from 'echarts'
import {
  Search, Refresh, Connection, Setting, VideoPlay,
  DataLine, Document, CircleCheck, CircleClose,
  Loading, Clock, TrendCharts, Monitor, Timer,
  Lightning, Aim, Stopwatch
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing latency analyzer...',
  'Preparing ping utility...',
  'Loading device database...',
  'Setting up metrics collector...',
  'Almost ready...'
]

// ==================== Component State ====================
const testing = ref(false)
const continuousTest = ref(false)
const searchKeyword = ref('')
const selectedProtocol = ref('all')
const selectedStatus = ref('all')
const testResultsVisible = ref(false)
const detailsVisible = ref(false)
const continuousTestVisible = ref(false)
const chartRef = ref(null)

let latencyChart: echarts.ECharts | null = null
let continuousChart: echarts.ECharts | null = null
let continuousTimer: number | null = null
let latencyDataPoints: { time: string; latency: number }[] = []

// Protocols
const protocols = [
  { value: 'all', label: 'All Protocols' },
  { value: 'bacnet', label: 'BACnet/IP', baseLatency: 15 },
  { value: 'modbus', label: 'Modbus TCP', baseLatency: 12 },
  { value: 'mqtt', label: 'MQTT', baseLatency: 8 },
  { value: 'opcua', label: 'OPC-UA', baseLatency: 25 },
  { value: 'snmp', label: 'SNMP', baseLatency: 20 },
  { value: 'http', label: 'HTTP', baseLatency: 30 },
  { value: 'https', label: 'HTTPS', baseLatency: 35 }
]

// Devices for latency testing
const devices = ref([
  { id: 'DEV001', name: 'Building A - BMS Controller', ip: '192.168.1.100', protocol: 'bacnet', port: 47808, status: 'online', avgLatency: 12, minLatency: 8, maxLatency: 18, jitter: 2.5, packetLoss: 0, lastTest: '2024-01-15 10:23:45', reliability: 99.8 },
  { id: 'DEV002', name: 'Chiller Plant Controller', ip: '192.168.1.101', protocol: 'bacnet', port: 47808, status: 'online', avgLatency: 15, minLatency: 10, maxLatency: 22, jitter: 3.2, packetLoss: 0, lastTest: '2024-01-15 10:22:30', reliability: 99.5 },
  { id: 'DEV003', name: 'AHU-1 Controller', ip: '192.168.1.102', protocol: 'bacnet', port: 47808, status: 'online', avgLatency: 8, minLatency: 5, maxLatency: 14, jitter: 1.8, packetLoss: 0, lastTest: '2024-01-15 10:24:12', reliability: 99.9 },
  { id: 'DEV004', name: 'Power Meter - Main', ip: '192.168.2.100', protocol: 'modbus', port: 502, status: 'online', avgLatency: 25, minLatency: 18, maxLatency: 35, jitter: 4.5, packetLoss: 0, lastTest: '2024-01-15 10:20:00', reliability: 99.2 },
  { id: 'DEV005', name: 'Lighting Panel - L1', ip: '192.168.2.101', protocol: 'modbus', port: 502, status: 'warning', avgLatency: 85, minLatency: 45, maxLatency: 120, jitter: 15.2, packetLoss: 2, lastTest: '2024-01-14 18:30:00', reliability: 92.5 },
  { id: 'DEV006', name: 'Temperature Sensors Hub', ip: '192.168.3.100', protocol: 'mqtt', port: 1883, status: 'online', avgLatency: 18, minLatency: 12, maxLatency: 28, jitter: 3.8, packetLoss: 0, lastTest: '2024-01-15 10:23:00', reliability: 99.7 },
  { id: 'DEV007', name: 'VFD Pump Controller', ip: '192.168.2.102', protocol: 'modbus', port: 502, status: 'online', avgLatency: 22, minLatency: 15, maxLatency: 32, jitter: 4.2, packetLoss: 1, lastTest: '2024-01-15 10:22:15', reliability: 98.8 },
  { id: 'DEV008', name: 'OPC-UA Gateway', ip: '192.168.4.100', protocol: 'opcua', port: 4840, status: 'online', avgLatency: 35, minLatency: 28, maxLatency: 48, jitter: 5.5, packetLoss: 0, lastTest: '2024-01-15 10:21:30', reliability: 99.4 },
  { id: 'DEV009', name: 'Network Switch - Core', ip: '192.168.0.1', protocol: 'snmp', port: 161, status: 'online', avgLatency: 5, minLatency: 3, maxLatency: 9, jitter: 1.2, packetLoss: 0, lastTest: '2024-01-15 10:24:30', reliability: 99.9 },
  { id: 'DEV010', name: 'Fire Alarm Panel', ip: '192.168.5.100', protocol: 'bacnet', port: 47808, status: 'warning', avgLatency: 55, minLatency: 40, maxLatency: 78, jitter: 8.5, packetLoss: 1.5, lastTest: '2024-01-15 10:19:45', reliability: 96.2 },
  { id: 'DEV011', name: 'Access Controller - Main', ip: '192.168.6.100', protocol: 'modbus', port: 502, status: 'online', avgLatency: 28, minLatency: 20, maxLatency: 42, jitter: 5.8, packetLoss: 0, lastTest: '2024-01-15 10:23:20', reliability: 99.1 },
  { id: 'DEV012', name: 'Weather Station', ip: '192.168.7.100', protocol: 'mqtt', port: 1883, status: 'offline', avgLatency: null, minLatency: null, maxLatency: null, jitter: null, packetLoss: 100, lastTest: '2024-01-14 15:45:00', reliability: 0 }
])

// Latency test results
const latencyResults = ref([
  { id: 'L001', timestamp: '2024-01-15 10:23:45', device: 'Building A - BMS Controller', avgLatency: 12, minLatency: 8, maxLatency: 18, jitter: 2.5, status: 'good' },
  { id: 'L002', timestamp: '2024-01-15 10:22:30', device: 'Chiller Plant Controller', avgLatency: 15, minLatency: 10, maxLatency: 22, jitter: 3.2, status: 'good' },
  { id: 'L003', timestamp: '2024-01-15 10:20:00', device: 'Lighting Panel - L1', avgLatency: 85, minLatency: 45, maxLatency: 120, jitter: 15.2, status: 'poor' },
  { id: 'L004', timestamp: '2024-01-15 10:15:30', device: 'OPC-UA Gateway', avgLatency: 35, minLatency: 28, maxLatency: 48, jitter: 5.5, status: 'fair' }
])

// Latency statistics
const latencyStats = reactive({
  total: 0,
  online: 0,
  warning: 0,
  offline: 0,
  overallAvgLatency: 0,
  overallMinLatency: 0,
  overallMaxLatency: 0,
  overallJitter: 0,
  p95Latency: 0,
  p99Latency: 0
})

// Continuous test config
const continuousConfig = reactive({
  deviceId: '',
  interval: 1000,
  duration: 60,
  packetsPerTest: 10
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

  latencyChart = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  const protocolStats = protocols.filter(p => p.value !== 'all').map(protocol => {
    const deviceList = devices.value.filter(d => d.protocol === protocol.value && d.avgLatency !== null)
    const avgLatency = deviceList.length > 0
        ? deviceList.reduce((a, b) => a + (b.avgLatency || 0), 0) / deviceList.length
        : 0
    return { protocol: protocol.label, avgLatency: Math.round(avgLatency) }
  })

  latencyChart?.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: protocolStats.map(p => p.protocol) },
    yAxis: { type: 'value', name: 'Latency (ms)' },
    series: [{
      name: 'Average Latency',
      type: 'bar',
      data: protocolStats.map(p => p.avgLatency),
      itemStyle: {
        color: (params: any) => {
          const value = params.value
          if (value < 20) return '#67C23A'
          if (value < 50) return '#E6A23C'
          return '#F56C6C'
        },
        borderRadius: [4, 4, 0, 0]
      },
      label: { show: true, position: 'top', formatter: '{c}ms' }
    }]
  })
}

const initContinuousChart = () => {
  if (!continuousChartRef.value) return

  continuousChart = echarts.init(continuousChartRef.value)
  continuousChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: [] },
    yAxis: { type: 'value', name: 'Latency (ms)', min: 0 },
    series: [{
      name: 'Latency',
      type: 'line',
      data: [],
      smooth: true,
      lineStyle: { color: '#409EFF', width: 2 },
      areaStyle: { opacity: 0.1, color: '#409EFF' },
      symbol: 'circle',
      symbolSize: 6
    }]
  })
}

const updateContinuousChart = () => {
  if (!continuousChart) return
  continuousChart.setOption({
    xAxis: { data: latencyDataPoints.map(p => p.time) },
    series: [{ data: latencyDataPoints.map(p => p.latency) }]
  })
}

const updateStats = () => {
  const onlineDevices = devices.value.filter(d => d.status === 'online' && d.avgLatency !== null)
  const warningDevices = devices.value.filter(d => d.status === 'warning')
  const offlineDevices = devices.value.filter(d => d.status === 'offline')

  latencyStats.total = devices.value.length
  latencyStats.online = onlineDevices.length
  latencyStats.warning = warningDevices.length
  latencyStats.offline = offlineDevices.length

  const latencies = onlineDevices.map(d => d.avgLatency).filter(l => l !== null)
  if (latencies.length > 0) {
    const sorted = [...latencies].sort((a, b) => a - b)
    latencyStats.overallAvgLatency = Math.round(latencies.reduce((a, b) => a + b, 0) / latencies.length)
    latencyStats.overallMinLatency = Math.min(...latencies)
    latencyStats.overallMaxLatency = Math.max(...latencies)
    latencyStats.overallJitter = parseFloat((latencyStats.overallMaxLatency - latencyStats.overallMinLatency).toFixed(1))
    latencyStats.p95Latency = sorted[Math.floor(sorted.length * 0.95)]
    latencyStats.p99Latency = sorted[Math.floor(sorted.length * 0.99)]
  }
}

const handleResize = () => {
  latencyChart?.resize()
  continuousChart?.resize()
}

// ==================== Test Functions ====================
const simulateLatencyTest = async (device: any): Promise<{ avgLatency: number; minLatency: number; maxLatency: number; jitter: number; packetLoss: number; status: string }> => {
  const protocolInfo = protocols.find(p => p.value === device.protocol)
  const baseLatency = protocolInfo?.baseLatency || 20

  // Simulate multiple pings
  const pingCount = 10
  const latencies: number[] = []
  let packetLoss = 0

  for (let i = 0; i < pingCount; i++) {
    // Simulate network variation
    const variation = (Math.random() - 0.5) * (baseLatency * 0.3)
    let latency = baseLatency + variation + Math.random() * 10

    // Simulate occasional spikes or packet loss
    if (Math.random() < 0.05) { // 5% chance of spike
      latency = latency + Math.random() * 50
    }
    if (Math.random() < 0.02) { // 2% chance of packet loss
      packetLoss++
      latency = 0
    } else {
      latencies.push(Math.max(1, Math.round(latency)))
    }

    await new Promise(resolve => setTimeout(resolve, 50))
  }

  const validLatencies = latencies.filter(l => l > 0)
  const avgLatency = validLatencies.length > 0 ? Math.round(validLatencies.reduce((a, b) => a + b, 0) / validLatencies.length) : 0
  const minLatency = validLatencies.length > 0 ? Math.min(...validLatencies) : 0
  const maxLatency = validLatencies.length > 0 ? Math.max(...validLatencies) : 0
  const jitter = validLatencies.length > 1 ? parseFloat((maxLatency - minLatency).toFixed(1)) : 0
  const lossPercent = (packetLoss / pingCount) * 100

  let status = 'online'
  if (lossPercent >= 50) {
    status = 'offline'
  } else if (avgLatency > 50 || lossPercent > 5) {
    status = 'warning'
  }

  return { avgLatency, minLatency, maxLatency, jitter, packetLoss: lossPercent, status }
}

const testLatency = async (device: any) => {
  device.status = 'testing'

  try {
    const result = await simulateLatencyTest(device)
    device.avgLatency = result.avgLatency
    device.minLatency = result.minLatency
    device.maxLatency = result.maxLatency
    device.jitter = result.jitter
    device.packetLoss = result.packetLoss
    device.status = result.status
    device.lastTest = new Date().toLocaleString()
    device.reliability = 100 - result.packetLoss

    // Add to results
    latencyResults.value.unshift({
      id: `L${Date.now()}`,
      timestamp: new Date().toLocaleString(),
      device: device.name,
      avgLatency: result.avgLatency,
      minLatency: result.minLatency,
      maxLatency: result.maxLatency,
      jitter: result.jitter,
      status: result.status
    })

    updateStats()
    updateChart()

    if (result.status === 'online') {
      ElMessage.success(`${device.name} - Avg: ${result.avgLatency}ms, Jitter: ${result.jitter}ms`)
    } else if (result.status === 'warning') {
      ElMessage.warning(`${device.name} - High latency: ${result.avgLatency}ms, Loss: ${result.packetLoss}%`)
    } else {
      ElMessage.error(`${device.name} - Offline (${result.packetLoss}% packet loss)`)
    }
  } catch (error) {
    device.status = 'offline'
    ElMessage.error(`${device.name} latency test failed`)
  }
}

const testAllLatency = async () => {
  testing.value = true
  let goodCount = 0
  let warningCount = 0
  let offlineCount = 0

  for (const device of filteredDevices.value) {
    device.status = 'testing'
    const result = await simulateLatencyTest(device)
    device.avgLatency = result.avgLatency
    device.minLatency = result.minLatency
    device.maxLatency = result.maxLatency
    device.jitter = result.jitter
    device.packetLoss = result.packetLoss
    device.status = result.status
    device.lastTest = new Date().toLocaleString()

    if (result.status === 'online') goodCount++
    else if (result.status === 'warning') warningCount++
    else offlineCount++

    await new Promise(resolve => setTimeout(resolve, 100))
  }

  updateStats()
  updateChart()
  testing.value = false
  ElMessage.success(`Test completed: ${goodCount} good, ${warningCount} warning, ${offlineCount} offline`)
}

const testByProtocol = async (protocol: string) => {
  testing.value = true
  const devicesToTest = devices.value.filter(d => d.protocol === protocol)

  let goodCount = 0
  let warningCount = 0
  let offlineCount = 0

  for (const device of devicesToTest) {
    const result = await simulateLatencyTest(device)
    device.avgLatency = result.avgLatency
    device.minLatency = result.minLatency
    device.maxLatency = result.maxLatency
    device.jitter = result.jitter
    device.packetLoss = result.packetLoss
    device.status = result.status
    device.lastTest = new Date().toLocaleString()

    if (result.status === 'online') goodCount++
    else if (result.status === 'warning') warningCount++
    else offlineCount++

    await new Promise(resolve => setTimeout(resolve, 80))
  }

  updateStats()
  updateChart()
  testing.value = false
  ElMessage.success(`${protocol.toUpperCase()} - ${goodCount} good, ${warningCount} warning, ${offlineCount} offline`)
}

const startContinuousTest = () => {
  const device = devices.value.find(d => d.id === continuousConfig.deviceId)
  if (!device) {
    ElMessage.warning('Please select a device')
    return
  }

  continuousTest.value = true
  continuousTestVisible.value = true
  latencyDataPoints = []

  setTimeout(() => {
    initContinuousChart()
  }, 100)

  const durationMs = continuousConfig.duration * 1000
  const intervalMs = continuousConfig.interval
  let packetsSent = 0
  const startTime = Date.now()

  const runTest = async () => {
    if (!continuousTest.value) return

    const elapsed = Date.now() - startTime
    if (elapsed >= durationMs) {
      stopContinuousTest()
      return
    }

    const result = await simulateLatencyTest(device)
    const timeLabel = new Date().toLocaleTimeString()
    latencyDataPoints.push({ time: timeLabel, latency: result.avgLatency })

    if (latencyDataPoints.length > 60) {
      latencyDataPoints.shift()
    }

    updateContinuousChart()
    packetsSent++

    continuousTimer = setTimeout(runTest, intervalMs) as unknown as number
  }

  runTest()
}

const stopContinuousTest = () => {
  if (continuousTimer) {
    clearTimeout(continuousTimer)
    continuousTimer = null
  }
  continuousTest.value = false
  ElMessage.success(`Continuous test completed. ${latencyDataPoints.length} samples collected.`)
}

const viewTestResults = () => {
  testResultsVisible.value = true
}

const viewDetails = (device: any) => {
  selectedDevice.value = device
  detailsVisible.value = true
}

const exportResults = () => {
  const results = devices.value.map(d => ({
    DeviceID: d.id,
    DeviceName: d.name,
    IP: d.ip,
    Protocol: d.protocol,
    Status: d.status,
    AvgLatency: d.avgLatency,
    MinLatency: d.minLatency,
    MaxLatency: d.maxLatency,
    Jitter: d.jitter,
    PacketLoss: d.packetLoss,
    Reliability: d.reliability,
    LastTest: d.lastTest
  }))

  const csv = convertToCSV(results)
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `latency_test_${new Date().toISOString()}.csv`
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

const getLatencyStatus = (latency: number) => {
  if (!latency) return 'unknown'
  if (latency < 20) return 'good'
  if (latency < 50) return 'fair'
  return 'poor'
}

const getLatencyClass = (latency: number) => {
  if (!latency) return ''
  if (latency < 20) return 'latency-good'
  if (latency < 50) return 'latency-fair'
  return 'latency-poor'
}

const getJitterClass = (jitter: number) => {
  if (!jitter) return ''
  if (jitter < 5) return 'jitter-good'
  if (jitter < 15) return 'jitter-fair'
  return 'jitter-poor'
}

const selectedDevice = ref<any>(null)
const continuousChartRef = ref(null)
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
          <span class="loading-title">Loading Latency Test</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Protocol Health Check - Latency Test</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="latency-test-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h2>Latency Test</h2>
        <el-tag type="warning" effect="dark">Protocol Health Check</el-tag>
      </div>
      <div class="header-stats">
        <el-tag type="info" effect="plain">ICMP | TCP | Response Time | Jitter</el-tag>
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
            <el-button type="primary" @click="testAllLatency" :loading="testing">
              <el-icon><VideoPlay /></el-icon> Test All
            </el-button>
            <el-button @click="continuousTestVisible = true">
              <el-icon><Timer /></el-icon> Continuous Test
            </el-button>
            <el-button @click="exportResults">
              <el-icon><Document /></el-icon> Export
            </el-button>
          </div>
        </el-col>
      </el-row>

      <!-- Quick Protocol Tests -->
      <el-row :gutter="10" class="protocol-buttons" style="margin-top: 15px">
        <el-col :span="3" v-for="p in protocols.slice(1)" :key="p.value">
          <el-button size="small" @click="testByProtocol(p.value)" :loading="testing" style="width: 100%">
            {{ p.label }}
          </el-button>
        </el-col>
        <el-col :span="3">
          <el-button size="small" @click="viewTestResults">
            <el-icon><DataLine /></el-icon> History
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- Statistics Cards -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon total-icon">
            <el-icon><Monitor /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ latencyStats.total }}</div>
            <div class="stat-label">Total Devices</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon latency-icon">
            <el-icon><Stopwatch /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ latencyStats.overallAvgLatency }}ms</div>
            <div class="stat-label">Avg Latency</div>
            <div class="stat-sub-value">Min: {{ latencyStats.overallMinLatency }}ms | Max: {{ latencyStats.overallMaxLatency }}ms</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon jitter-icon">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ latencyStats.overallJitter }}ms</div>
            <div class="stat-label">Overall Jitter</div>
            <div class="stat-sub-value">P95: {{ latencyStats.p95Latency }}ms | P99: {{ latencyStats.p99Latency }}ms</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon health-icon">
            <el-icon><Aim /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ latencyStats.online }}</div>
            <div class="stat-label">Healthy Devices</div>
            <div class="stat-sub-value">{{ latencyStats.warning }} Warning | {{ latencyStats.offline }} Offline</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Latency Chart -->
    <el-card shadow="never" class="chart-card">
      <template #header>
        <div class="card-header">
          <span>Average Latency by Protocol</span>
          <el-button text type="primary" @click="updateChart">Refresh Chart</el-button>
        </div>
      </template>
      <div ref="chartRef" class="chart" style="height: 320px"></div>
    </el-card>

    <!-- Devices Table -->
    <el-card shadow="never" class="devices-card">
      <template #header>
        <div class="table-header">
          <span>Network Latency Test Results</span>
          <div class="table-actions">
            <el-button type="primary" size="small" @click="testAllLatency" :loading="testing">
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
        <el-table-column label="Avg Latency" width="110" align="center">
          <template #default="{ row }">
            <span v-if="row.avgLatency !== null" :class="getLatencyClass(row.avgLatency)">
              {{ row.avgLatency }}ms
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="Min/Max" width="100" align="center">
          <template #default="{ row }">
            <span v-if="row.minLatency !== null">
              {{ row.minLatency }}/{{ row.maxLatency }}ms
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="Jitter" width="80" align="center">
          <template #default="{ row }">
            <span v-if="row.jitter !== null" :class="getJitterClass(row.jitter)">
              {{ row.jitter }}ms
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
        <el-table-column label="Status" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'online' ? 'success' : row.status === 'warning' ? 'warning' : 'danger'" size="small">
              {{ row.status === 'online' ? 'Good' : row.status === 'warning' ? 'Warning' : 'Offline' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastTest" label="Last Test" width="160" />
        <el-table-column label="Actions" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="testLatency(row)" :disabled="testing">
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
    <el-dialog v-model="testResultsVisible" title="Latency Test History" width="900px">
      <el-table :data="latencyResults" stripe max-height="400">
        <el-table-column prop="timestamp" label="Timestamp" width="160" />
        <el-table-column prop="device" label="Device" min-width="200" />
        <el-table-column label="Avg Latency" width="100" align="center">
          <template #default="{ row }">
            <span :class="getLatencyClass(row.avgLatency)">{{ row.avgLatency }}ms</span>
          </template>
        </el-table-column>
        <el-table-column label="Min/Max" width="100" align="center">
          <template #default="{ row }">
            {{ row.minLatency }}/{{ row.maxLatency }}ms
          </template>
        </el-table-column>
        <el-table-column label="Jitter" width="80" align="center">
          <template #default="{ row }">
            {{ row.jitter }}ms
          </template>
        </el-table-column>
        <el-table-column label="Status" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'good' ? 'success' : row.status === 'fair' ? 'warning' : 'danger'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button type="primary" @click="testResultsVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Device Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="`Device Details - ${selectedDevice?.name}`" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Device ID">{{ selectedDevice?.id }}</el-descriptions-item>
        <el-descriptions-item label="Device Name">{{ selectedDevice?.name }}</el-descriptions-item>
        <el-descriptions-item label="IP Address">{{ selectedDevice?.ip }}</el-descriptions-item>
        <el-descriptions-item label="Protocol">{{ selectedDevice?.protocol?.toUpperCase() }}</el-descriptions-item>
        <el-descriptions-item label="Port">{{ selectedDevice?.port }}</el-descriptions-item>
        <el-descriptions-item label="Avg Latency">
          <span v-if="selectedDevice?.avgLatency !== null" :class="getLatencyClass(selectedDevice?.avgLatency)">
            {{ selectedDevice?.avgLatency }}ms
          </span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="Min/Max Latency">
          <span v-if="selectedDevice?.minLatency !== null">
            {{ selectedDevice?.minLatency }}ms / {{ selectedDevice?.maxLatency }}ms
          </span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="Jitter">
          <span v-if="selectedDevice?.jitter !== null" :class="getJitterClass(selectedDevice?.jitter)">
            {{ selectedDevice?.jitter }}ms
          </span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="Packet Loss">
          <span v-if="selectedDevice?.packetLoss !== null" :class="{ 'high-loss': selectedDevice?.packetLoss > 5 }">
            {{ selectedDevice?.packetLoss }}%
          </span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="Reliability">
          <span v-if="selectedDevice?.reliability !== null">{{ selectedDevice?.reliability }}%</span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="selectedDevice?.status === 'online' ? 'success' : selectedDevice?.status === 'warning' ? 'warning' : 'danger'" size="small">
            {{ selectedDevice?.status === 'online' ? 'Good' : selectedDevice?.status === 'warning' ? 'Warning' : 'Offline' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Last Test" :span="2">{{ selectedDevice?.lastTest || 'Never' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button type="primary" @click="testLatency(selectedDevice)" :disabled="testing">Test Again</el-button>
        <el-button @click="detailsVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Continuous Test Dialog -->
    <el-dialog v-model="continuousTestVisible" title="Continuous Latency Test" width="800px" @close="stopContinuousTest">
      <el-form :model="continuousConfig" label-width="140px" v-if="!continuousTest">
        <el-form-item label="Select Device">
          <el-select v-model="continuousConfig.deviceId" placeholder="Select device" style="width: 100%">
            <el-option v-for="d in devices.filter(d => d.status !== 'offline')" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Test Interval (ms)">
          <el-input-number v-model="continuousConfig.interval" :min="500" :max="5000" :step="500" />
        </el-form-item>
        <el-form-item label="Test Duration (s)">
          <el-input-number v-model="continuousConfig.duration" :min="10" :max="300" :step="10" />
        </el-form-item>
        <el-form-item label="Packets per Test">
          <el-input-number v-model="continuousConfig.packetsPerTest" :min="5" :max="50" />
        </el-form-item>
      </el-form>

      <div v-if="continuousTest" class="continuous-chart-container">
        <div ref="continuousChartRef" class="continuous-chart" style="height: 350px"></div>
        <div class="continuous-stats">
          <el-statistic title="Samples Collected" :value="latencyDataPoints.length" />
          <el-statistic title="Current Latency" :value="latencyDataPoints[latencyDataPoints.length - 1]?.latency || 0" suffix="ms" />
          <el-statistic title="Avg Latency" :value="Math.round(latencyDataPoints.reduce((a, b) => a + b.latency, 0) / latencyDataPoints.length) || 0" suffix="ms" />
        </div>
      </div>

      <template #footer>
        <el-button v-if="!continuousTest" @click="continuousTestVisible = false">Cancel</el-button>
        <el-button v-if="!continuousTest" type="primary" @click="startContinuousTest">Start Test</el-button>
        <el-button v-if="continuousTest" type="danger" @click="stopContinuousTest">Stop Test</el-button>
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
.latency-test-container {
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

.latency-icon {
  background-color: #f0f9ff;
  color: #67c23a;
}

.jitter-icon {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.health-icon {
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

.continuous-chart-container {
  padding: 10px;
}

.continuous-chart {
  width: 100%;
}

.continuous-stats {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 8px;
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

.jitter-good {
  color: #67c23a;
}

.jitter-fair {
  color: #e6a23c;
}

.jitter-poor {
  color: #f56c6c;
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