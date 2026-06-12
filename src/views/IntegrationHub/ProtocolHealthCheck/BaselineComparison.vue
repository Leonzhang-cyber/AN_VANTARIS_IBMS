<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Search, Refresh, Connection, Setting, DataLine,
  Document, CircleCheck, CircleClose, Loading,
  TrendCharts, Monitor, Aim, Clock, Timer,
  Warning, DataAnalysis, Histogram
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing baseline analyzer...',
  'Loading historical data...',
  'Calculating baselines...',
  'Comparing current metrics...',
  'Almost ready...'
]

// ==================== Component State ====================
const testing = ref(false)
const searchKeyword = ref('')
const selectedProtocol = ref('all')
const selectedDeviation = ref('all')
const baselineHistoryVisible = ref(false)
const detailsVisible = ref(false)
const chartRef = ref(null)
const trendChartRef = ref(null)

let comparisonChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null

// Protocols
const protocols = [
  { value: 'all', label: 'All Protocols' },
  { value: 'bacnet', label: 'BACnet/IP' },
  { value: 'modbus', label: 'Modbus TCP' },
  { value: 'mqtt', label: 'MQTT' },
  { value: 'opcua', label: 'OPC-UA' },
  { value: 'snmp', label: 'SNMP' }
]

// Devices with baseline comparison
const devices = ref([
  {
    id: 'DEV001', name: 'Building A - BMS Controller', ip: '192.168.1.100', protocol: 'bacnet',
    baselineLatency: 12, currentLatency: 14, latencyDeviation: 16.7, status: 'warning',
    baselineJitter: 2.5, currentJitter: 3.2, jitterDeviation: 28,
    baselineReliability: 99.8, currentReliability: 99.5, reliabilityDeviation: -0.3,
    lastComparison: '2024-01-15 10:23:45', trend: 'increasing'
  },
  {
    id: 'DEV002', name: 'Chiller Plant Controller', ip: '192.168.1.101', protocol: 'bacnet',
    baselineLatency: 15, currentLatency: 16, latencyDeviation: 6.7, status: 'good',
    baselineJitter: 3.2, currentJitter: 3.5, jitterDeviation: 9.4,
    baselineReliability: 99.5, currentReliability: 99.4, reliabilityDeviation: -0.1,
    lastComparison: '2024-01-15 10:22:30', trend: 'stable'
  },
  {
    id: 'DEV003', name: 'AHU-1 Controller', ip: '192.168.1.102', protocol: 'bacnet',
    baselineLatency: 8, currentLatency: 9, latencyDeviation: 12.5, status: 'good',
    baselineJitter: 1.8, currentJitter: 2.0, jitterDeviation: 11.1,
    baselineReliability: 99.9, currentReliability: 99.8, reliabilityDeviation: -0.1,
    lastComparison: '2024-01-15 10:24:12', trend: 'stable'
  },
  {
    id: 'DEV004', name: 'Power Meter - Main', ip: '192.168.2.100', protocol: 'modbus',
    baselineLatency: 25, currentLatency: 26, latencyDeviation: 4, status: 'good',
    baselineJitter: 4.5, currentJitter: 4.8, jitterDeviation: 6.7,
    baselineReliability: 99.2, currentReliability: 99.1, reliabilityDeviation: -0.1,
    lastComparison: '2024-01-15 10:20:00', trend: 'stable'
  },
  {
    id: 'DEV005', name: 'Lighting Panel - L1', ip: '192.168.2.101', protocol: 'modbus',
    baselineLatency: 85, currentLatency: 120, latencyDeviation: 41.2, status: 'critical',
    baselineJitter: 15.2, currentJitter: 22.5, jitterDeviation: 48,
    baselineReliability: 92.5, currentReliability: 88.2, reliabilityDeviation: -4.7,
    lastComparison: '2024-01-14 18:30:00', trend: 'increasing'
  },
  {
    id: 'DEV006', name: 'Temperature Sensors Hub', ip: '192.168.3.100', protocol: 'mqtt',
    baselineLatency: 18, currentLatency: 19, latencyDeviation: 5.6, status: 'good',
    baselineJitter: 3.8, currentJitter: 4.0, jitterDeviation: 5.3,
    baselineReliability: 99.7, currentReliability: 99.6, reliabilityDeviation: -0.1,
    lastComparison: '2024-01-15 10:23:00', trend: 'stable'
  },
  {
    id: 'DEV007', name: 'VFD Pump Controller', ip: '192.168.2.102', protocol: 'modbus',
    baselineLatency: 22, currentLatency: 28, latencyDeviation: 27.3, status: 'warning',
    baselineJitter: 4.2, currentJitter: 6.8, jitterDeviation: 61.9,
    baselineReliability: 98.8, currentReliability: 97.5, reliabilityDeviation: -1.3,
    lastComparison: '2024-01-15 10:22:15', trend: 'increasing'
  },
  {
    id: 'DEV008', name: 'OPC-UA Gateway', ip: '192.168.4.100', protocol: 'opcua',
    baselineLatency: 35, currentLatency: 38, latencyDeviation: 8.6, status: 'good',
    baselineJitter: 5.5, currentJitter: 6.0, jitterDeviation: 9.1,
    baselineReliability: 99.4, currentReliability: 99.2, reliabilityDeviation: -0.2,
    lastComparison: '2024-01-15 10:21:30', trend: 'stable'
  },
  {
    id: 'DEV009', name: 'Network Switch - Core', ip: '192.168.0.1', protocol: 'snmp',
    baselineLatency: 5, currentLatency: 6, latencyDeviation: 20, status: 'warning',
    baselineJitter: 1.2, currentJitter: 1.5, jitterDeviation: 25,
    baselineReliability: 99.9, currentReliability: 99.8, reliabilityDeviation: -0.1,
    lastComparison: '2024-01-15 10:24:30', trend: 'stable'
  },
  {
    id: 'DEV010', name: 'Fire Alarm Panel', ip: '192.168.5.100', protocol: 'bacnet',
    baselineLatency: 55, currentLatency: 78, latencyDeviation: 41.8, status: 'critical',
    baselineJitter: 8.5, currentJitter: 14.2, jitterDeviation: 67.1,
    baselineReliability: 96.2, currentReliability: 93.5, reliabilityDeviation: -2.8,
    lastComparison: '2024-01-15 10:19:45', trend: 'increasing'
  },
  {
    id: 'DEV011', name: 'Access Controller - Main', ip: '192.168.6.100', protocol: 'modbus',
    baselineLatency: 28, currentLatency: 30, latencyDeviation: 7.1, status: 'good',
    baselineJitter: 5.8, currentJitter: 6.1, jitterDeviation: 5.2,
    baselineReliability: 99.1, currentReliability: 99.0, reliabilityDeviation: -0.1,
    lastComparison: '2024-01-15 10:23:20', trend: 'stable'
  },
  {
    id: 'DEV012', name: 'Weather Station', ip: '192.168.7.100', protocol: 'mqtt',
    baselineLatency: 25, currentLatency: 45, latencyDeviation: 80, status: 'critical',
    baselineJitter: 5.0, currentJitter: 12.5, jitterDeviation: 150,
    baselineReliability: 99.5, currentReliability: 95.0, reliabilityDeviation: -4.5,
    lastComparison: '2024-01-14 15:45:00', trend: 'increasing'
  }
])

// Baseline history
const baselineHistory = ref([
  { date: '2024-01-01', avgLatency: 15, avgJitter: 3.2, avgReliability: 99.2 },
  { date: '2024-01-02', avgLatency: 16, avgJitter: 3.3, avgReliability: 99.1 },
  { date: '2024-01-03', avgLatency: 15, avgJitter: 3.1, avgReliability: 99.3 },
  { date: '2024-01-04', avgLatency: 17, avgJitter: 3.4, avgReliability: 99.0 },
  { date: '2024-01-05', avgLatency: 16, avgJitter: 3.2, avgReliability: 99.2 },
  { date: '2024-01-06', avgLatency: 18, avgJitter: 3.6, avgReliability: 98.9 },
  { date: '2024-01-07', avgLatency: 19, avgJitter: 3.8, avgReliability: 98.8 },
  { date: '2024-01-08', avgLatency: 20, avgJitter: 4.0, avgReliability: 98.7 },
  { date: '2024-01-09', avgLatency: 19, avgJitter: 3.9, avgReliability: 98.8 },
  { date: '2024-01-10', avgLatency: 21, avgJitter: 4.2, avgReliability: 98.6 },
  { date: '2024-01-11', avgLatency: 22, avgJitter: 4.4, avgReliability: 98.5 },
  { date: '2024-01-12', avgLatency: 23, avgJitter: 4.5, avgReliability: 98.4 },
  { date: '2024-01-13', avgLatency: 24, avgJitter: 4.7, avgReliability: 98.3 },
  { date: '2024-01-14', avgLatency: 25, avgJitter: 4.8, avgReliability: 98.2 },
  { date: '2024-01-15', avgLatency: 27, avgJitter: 5.2, avgReliability: 97.9 }
])

// Comparison statistics
const comparisonStats = reactive({
  total: 0,
  good: 0,
  warning: 0,
  critical: 0,
  avgLatencyDeviation: 0,
  avgJitterDeviation: 0,
  avgReliabilityDeviation: 0,
  worstLatencyDeviation: 0,
  worstJitterDeviation: 0
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
  if (selectedDeviation.value !== 'all') {
    filtered = filtered.filter(d => d.status === selectedDeviation.value)
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
        initTrendChart()
        updateStats()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  comparisonChart = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  const protocolStats = protocols.filter(p => p.value !== 'all').map(protocol => {
    const deviceList = devices.value.filter(d => d.protocol === protocol.value)
    const avgDeviation = deviceList.length > 0
        ? deviceList.reduce((a, b) => a + b.latencyDeviation, 0) / deviceList.length
        : 0
    return { protocol: protocol.label, deviation: Math.round(avgDeviation) }
  })

  comparisonChart?.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}<br/>Deviation: {c}%' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: protocolStats.map(p => p.protocol) },
    yAxis: { type: 'value', name: 'Latency Deviation (%)' },
    series: [{
      name: 'Deviation from Baseline',
      type: 'bar',
      data: protocolStats.map(p => p.deviation),
      itemStyle: {
        color: (params: any) => {
          const value = params.value
          if (value < 10) return '#67C23A'
          if (value < 30) return '#E6A23C'
          return '#F56C6C'
        },
        borderRadius: [4, 4, 0, 0]
      },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initTrendChart = () => {
  if (!trendChartRef.value) return

  trendChart = echarts.init(trendChartRef.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Average Latency (ms)', 'Jitter (ms)', 'Reliability (%)'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: baselineHistory.value.map(h => h.date) },
    yAxis: [
      { type: 'value', name: 'Latency / Jitter (ms)' },
      { type: 'value', name: 'Reliability (%)', min: 95, max: 100 }
    ],
    series: [
      { name: 'Average Latency (ms)', type: 'line', data: baselineHistory.value.map(h => h.avgLatency), smooth: true, lineStyle: { color: '#409EFF', width: 2 }, symbol: 'circle', symbolSize: 6 },
      { name: 'Jitter (ms)', type: 'line', data: baselineHistory.value.map(h => h.avgJitter), smooth: true, lineStyle: { color: '#E6A23C', width: 2 }, symbol: 'diamond', symbolSize: 6 },
      { name: 'Reliability (%)', type: 'line', data: baselineHistory.value.map(h => h.avgReliability), smooth: true, lineStyle: { color: '#67C23A', width: 2 }, symbol: 'triangle', symbolSize: 6, yAxisIndex: 1 }
    ]
  })
}

const updateStats = () => {
  const goodDevices = devices.value.filter(d => d.status === 'good')
  const warningDevices = devices.value.filter(d => d.status === 'warning')
  const criticalDevices = devices.value.filter(d => d.status === 'critical')

  comparisonStats.total = devices.value.length
  comparisonStats.good = goodDevices.length
  comparisonStats.warning = warningDevices.length
  comparisonStats.critical = criticalDevices.length

  const latencyDeviations = devices.value.map(d => d.latencyDeviation)
  const jitterDeviations = devices.value.map(d => d.jitterDeviation)
  const reliabilityDeviations = devices.value.map(d => Math.abs(d.reliabilityDeviation))

  comparisonStats.avgLatencyDeviation = parseFloat((latencyDeviations.reduce((a, b) => a + b, 0) / devices.value.length).toFixed(1))
  comparisonStats.avgJitterDeviation = parseFloat((jitterDeviations.reduce((a, b) => a + b, 0) / devices.value.length).toFixed(1))
  comparisonStats.avgReliabilityDeviation = parseFloat((reliabilityDeviations.reduce((a, b) => a + b, 0) / devices.value.length).toFixed(1))
  comparisonStats.worstLatencyDeviation = Math.max(...latencyDeviations)
  comparisonStats.worstJitterDeviation = Math.max(...jitterDeviations)
}

const handleResize = () => {
  comparisonChart?.resize()
  trendChart?.resize()
}

// ==================== Comparison Functions ====================
const refreshComparison = async () => {
  testing.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))

  // Simulate refreshing baseline comparison
  devices.value.forEach(device => {
    const variation = (Math.random() - 0.5) * 20
    device.currentLatency = Math.max(1, Math.round(device.baselineLatency * (1 + variation / 100)))
    device.latencyDeviation = parseFloat((((device.currentLatency - device.baselineLatency) / device.baselineLatency) * 100).toFixed(1))

    if (device.latencyDeviation > 30) device.status = 'critical'
    else if (device.latencyDeviation > 15) device.status = 'warning'
    else device.status = 'good'

    device.lastComparison = new Date().toLocaleString()
  })

  updateStats()
  updateChart()
  testing.value = false
  ElMessage.success('Baseline comparison refreshed')
}

const updateBaseline = async (device: any) => {
  ElMessage.info(`Updating baseline for ${device.name}...`)
  await new Promise(resolve => setTimeout(resolve, 1000))
  device.baselineLatency = device.currentLatency
  device.baselineJitter = device.currentJitter
  device.baselineReliability = device.currentReliability
  device.latencyDeviation = 0
  device.jitterDeviation = 0
  device.reliabilityDeviation = 0
  device.status = 'good'
  ElMessage.success(`Baseline updated for ${device.name}`)
  updateStats()
  updateChart()
}

const resetAllBaselines = async () => {
  await ElMessageBox.confirm('This will reset all baselines to current values. Continue?', 'Confirm Reset', {
    confirmButtonText: 'Reset',
    cancelButtonText: 'Cancel',
    type: 'warning'
  })

  devices.value.forEach(device => {
    device.baselineLatency = device.currentLatency
    device.baselineJitter = device.currentJitter
    device.baselineReliability = device.currentReliability
    device.latencyDeviation = 0
    device.jitterDeviation = 0
    device.reliabilityDeviation = 0
    device.status = 'good'
  })

  updateStats()
  updateChart()
  ElMessage.success('All baselines reset successfully')
}

const viewHistory = () => {
  baselineHistoryVisible.value = true
}

const viewDetails = (device: any) => {
  selectedDevice.value = device
  detailsVisible.value = true
}

const exportResults = () => {
  const results = devices.value.map(d => ({
    DeviceID: d.id,
    DeviceName: d.name,
    Protocol: d.protocol,
    BaselineLatency: d.baselineLatency,
    CurrentLatency: d.currentLatency,
    LatencyDeviation: `${d.latencyDeviation}%`,
    BaselineJitter: d.baselineJitter,
    CurrentJitter: d.currentJitter,
    JitterDeviation: `${d.jitterDeviation}%`,
    BaselineReliability: `${d.baselineReliability}%`,
    CurrentReliability: `${d.currentReliability}%`,
    Status: d.status,
    LastComparison: d.lastComparison
  }))

  const csv = convertToCSV(results)
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `baseline_comparison_${new Date().toISOString()}.csv`
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

const getDeviationClass = (deviation: number) => {
  if (deviation < 10) return 'deviation-good'
  if (deviation < 30) return 'deviation-warning'
  return 'deviation-critical'
}

const getTrendIcon = (trend: string) => {
  if (trend === 'increasing') return '📈'
  if (trend === 'decreasing') return '📉'
  return '➡️'
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
          <span class="loading-title">Loading Baseline Comparison</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Protocol Health Check - Baseline Comparison</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="baseline-comparison-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h2>Baseline Comparison</h2>
        <el-tag type="warning" effect="dark">Protocol Health Check</el-tag>
      </div>
      <div class="header-stats">
        <el-tag type="info" effect="plain">Historical vs Current Performance</el-tag>
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
          <el-select v-model="selectedDeviation" placeholder="Deviation Status" clearable style="width: 100%">
            <el-option label="All" value="all" />
            <el-option label="Good (<15%)" value="good" />
            <el-option label="Warning (15-30%)" value="warning" />
            <el-option label="Critical (>30%)" value="critical" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-input v-model="searchKeyword" placeholder="Search devices..." :prefix-icon="Search" clearable />
        </el-col>
        <el-col :span="6">
          <div class="control-buttons">
            <el-button type="primary" @click="refreshComparison" :loading="testing">
              <el-icon><Refresh /></el-icon> Refresh
            </el-button>
            <el-button @click="resetAllBaselines">
              <el-icon><Setting /></el-icon> Reset Baselines
            </el-button>
            <el-button @click="exportResults">
              <el-icon><Document /></el-icon> Export
            </el-button>
          </div>
        </el-col>
      </el-row>

      <!-- Quick Actions -->
      <el-row :gutter="10" class="protocol-buttons" style="margin-top: 15px">
        <el-col :span="4">
          <el-button size="small" @click="viewHistory">
            <el-icon><DataLine /></el-icon> View History
          </el-button>
        </el-col>
        <el-col :span="4">
          <el-button size="small" @click="refreshComparison">
            <el-icon><Aim /></el-icon> Recalculate
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
            <div class="stat-value">{{ comparisonStats.total }}</div>
            <div class="stat-label">Total Devices</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon good-icon">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ comparisonStats.good }}</div>
            <div class="stat-label">Within Baseline (±15%)</div>
            <el-progress :percentage="(comparisonStats.good / comparisonStats.total) * 100" :color="'#67C23A'" :stroke-width="6" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon warning-icon">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ comparisonStats.warning }}</div>
            <div class="stat-label">Moderate Deviation (15-30%)</div>
            <div class="stat-sub-value">Avg Latency Deviation: {{ comparisonStats.avgLatencyDeviation }}%</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon critical-icon">
            <el-icon><CircleClose /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ comparisonStats.critical }}</div>
            <div class="stat-label">Critical Deviation (>30%)</div>
            <div class="stat-sub-value">Worst: {{ comparisonStats.worstLatencyDeviation }}%</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Comparison Chart -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Latency Deviation by Protocol</span>
              <el-button text type="primary" @click="updateChart">Refresh Chart</el-button>
            </div>
          </template>
          <div ref="chartRef" class="chart" style="height: 320px"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Performance Trend (15 Days)</span>
              <el-button text type="primary" @click="viewHistory">Details</el-button>
            </div>
          </template>
          <div ref="trendChartRef" class="chart" style="height: 320px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Devices Table -->
    <el-card shadow="never" class="devices-card">
      <template #header>
        <div class="table-header">
          <span>Baseline Comparison Results</span>
          <div class="table-actions">
            <el-button type="primary" size="small" @click="refreshComparison" :loading="testing">
              Refresh Comparison
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
        <el-table-column label="Latency" width="130" align="center">
          <template #default="{ row }">
            <div class="metric-compare">
              <span class="baseline">{{ row.baselineLatency }}ms</span>
              <el-icon><Right /></el-icon>
              <span :class="getDeviationClass(row.latencyDeviation)">{{ row.currentLatency }}ms</span>
              <span :class="getDeviationClass(row.latencyDeviation)" class="deviation-badge">
                ({{ row.latencyDeviation > 0 ? '+' : '' }}{{ row.latencyDeviation }}%)
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Jitter" width="130" align="center">
          <template #default="{ row }">
            <div class="metric-compare">
              <span class="baseline">{{ row.baselineJitter }}ms</span>
              <el-icon><Right /></el-icon>
              <span :class="getDeviationClass(row.jitterDeviation)">{{ row.currentJitter }}ms</span>
              <span :class="getDeviationClass(row.jitterDeviation)" class="deviation-badge">
                ({{ row.jitterDeviation > 0 ? '+' : '' }}{{ row.jitterDeviation }}%)
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Reliability" width="130" align="center">
          <template #default="{ row }">
            <div class="metric-compare">
              <span class="baseline">{{ row.baselineReliability }}%</span>
              <el-icon><Right /></el-icon>
              <span :class="row.reliabilityDeviation < -5 ? 'deviation-critical' : ''">
                {{ row.currentReliability }}%
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'good' ? 'success' : row.status === 'warning' ? 'warning' : 'danger'" size="small">
              {{ row.status === 'good' ? 'Good' : row.status === 'warning' ? 'Warning' : 'Critical' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Trend" width="80" align="center">
          <template #default="{ row }">
            <span class="trend-icon">{{ getTrendIcon(row.trend) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="lastComparison" label="Last Comparison" width="160" />
        <el-table-column label="Actions" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">
              Details
            </el-button>
            <el-button link type="warning" size="small" @click="updateBaseline(row)">
              Set Baseline
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

    <!-- Baseline History Dialog -->
    <el-dialog v-model="baselineHistoryVisible" title="Baseline History (15 Days)" width="900px">
      <el-table :data="baselineHistory" stripe max-height="400">
        <el-table-column prop="date" label="Date" width="120" />
        <el-table-column label="Average Latency" width="150" align="center">
          <template #default="{ row }">
            <span :class="row.avgLatency > 20 ? 'deviation-warning' : ''">{{ row.avgLatency }}ms</span>
          </template>
        </el-table-column>
        <el-table-column label="Average Jitter" width="140" align="center">
          <template #default="{ row }">
            <span :class="row.avgJitter > 4 ? 'deviation-warning' : ''">{{ row.avgJitter }}ms</span>
          </template>
        </el-table-column>
        <el-table-column label="Average Reliability" width="150" align="center">
          <template #default="{ row }">
            <span :class="row.avgReliability < 98.5 ? 'deviation-critical' : ''">{{ row.avgReliability }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="Change from Previous" width="150" align="center">
          <template #default="{ row, $index }">
            <span v-if="$index > 0">
              <span v-if="row.avgLatency > baselineHistory[$index - 1].avgLatency" class="deviation-warning">▲</span>
              <span v-else-if="row.avgLatency < baselineHistory[$index - 1].avgLatency" class="deviation-good">▼</span>
              <span v-else>●</span>
              {{ Math.abs(row.avgLatency - baselineHistory[$index - 1].avgLatency) }}ms
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button type="primary" @click="baselineHistoryVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Device Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="`Device Details - ${selectedDevice?.name}`" width="650px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Device ID">{{ selectedDevice?.id }}</el-descriptions-item>
        <el-descriptions-item label="Device Name">{{ selectedDevice?.name }}</el-descriptions-item>
        <el-descriptions-item label="IP Address">{{ selectedDevice?.ip }}</el-descriptions-item>
        <el-descriptions-item label="Protocol">{{ selectedDevice?.protocol?.toUpperCase() }}</el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left">Latency Comparison</el-divider>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Baseline Latency">{{ selectedDevice?.baselineLatency }}ms</el-descriptions-item>
        <el-descriptions-item label="Current Latency">{{ selectedDevice?.currentLatency }}ms</el-descriptions-item>
        <el-descriptions-item label="Deviation" :span="2">
          <span :class="getDeviationClass(selectedDevice?.latencyDeviation)">
            {{ selectedDevice?.latencyDeviation > 0 ? '+' : '' }}{{ selectedDevice?.latencyDeviation }}%
          </span>
        </el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left">Jitter Comparison</el-divider>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Baseline Jitter">{{ selectedDevice?.baselineJitter }}ms</el-descriptions-item>
        <el-descriptions-item label="Current Jitter">{{ selectedDevice?.currentJitter }}ms</el-descriptions-item>
        <el-descriptions-item label="Deviation" :span="2">
          <span :class="getDeviationClass(selectedDevice?.jitterDeviation)">
            {{ selectedDevice?.jitterDeviation > 0 ? '+' : '' }}{{ selectedDevice?.jitterDeviation }}%
          </span>
        </el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left">Reliability Comparison</el-divider>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Baseline Reliability">{{ selectedDevice?.baselineReliability }}%</el-descriptions-item>
        <el-descriptions-item label="Current Reliability">{{ selectedDevice?.currentReliability }}%</el-descriptions-item>
        <el-descriptions-item label="Change" :span="2">
          <span :class="selectedDevice?.reliabilityDeviation < -5 ? 'deviation-critical' : ''">
            {{ selectedDevice?.reliabilityDeviation > 0 ? '+' : '' }}{{ selectedDevice?.reliabilityDeviation }}%
          </span>
        </el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left">Summary</el-divider>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Status">
          <el-tag :type="selectedDevice?.status === 'good' ? 'success' : selectedDevice?.status === 'warning' ? 'warning' : 'danger'" size="small">
            {{ selectedDevice?.status === 'good' ? 'Good' : selectedDevice?.status === 'warning' ? 'Warning' : 'Critical' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Trend">{{ getTrendIcon(selectedDevice?.trend) }} {{ selectedDevice?.trend }}</el-descriptions-item>
        <el-descriptions-item label="Last Comparison" :span="2">{{ selectedDevice?.lastComparison }}</el-descriptions-item>
      </el-descriptions>

      <template #footer>
        <el-button type="primary" @click="updateBaseline(selectedDevice)">Set as New Baseline</el-button>
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
.baseline-comparison-container {
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

.good-icon {
  background-color: #f0f9ff;
  color: #67c23a;
}

.warning-icon {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.critical-icon {
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
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.stat-sub-value {
  font-size: 11px;
  color: #67c23a;
  margin-top: 2px;
}

.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  height: 390px;
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

.metric-compare {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 13px;
}

.baseline {
  color: #909399;
  text-decoration: line-through;
  font-size: 12px;
}

.deviation-badge {
  font-size: 11px;
  margin-left: 4px;
}

.deviation-good {
  color: #67c23a;
  font-weight: bold;
}

.deviation-warning {
  color: #e6a23c;
  font-weight: bold;
}

.deviation-critical {
  color: #f56c6c;
  font-weight: bold;
}

.trend-icon {
  font-size: 18px;
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

  .metric-compare {
    flex-wrap: wrap;
  }
}
</style>