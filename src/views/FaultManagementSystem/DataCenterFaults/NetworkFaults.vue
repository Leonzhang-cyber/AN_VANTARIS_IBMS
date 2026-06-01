<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted, computed } from 'vue'
import {
  Search, RefreshRight, Warning, CircleCheck, Clock,
  TrendCharts, Monitor, Connection, DataAnalysis,
  Document, Setting, More, ArrowUp, ArrowDown,
  VideoCamera, Histogram, Grid, Platform, Link
} from "@element-plus/icons-vue"
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Connecting to network monitoring system...',
  'Loading switch and router status...',
  'Analyzing network traffic...'
]

// Network Devices Data
const networkDevices = ref([
  {
    id: 'SW-CORE-01',
    name: 'Core Switch 1',
    location: 'Data Center A - Network Room',
    type: 'Core Switch',
    status: 'healthy',
    uptime: 245,
    cpuLoad: 32,
    memoryUsage: 45,
    temperature: 42,
    throughput: 12500,
    packetLoss: 0.02,
    latency: 0.8,
    portCount: 48,
    activePorts: 42,
    alerts: [],
    lastMaintenance: '2025-01-10',
    nextMaintenance: '2025-04-10'
  },
  {
    id: 'SW-CORE-02',
    name: 'Core Switch 2',
    location: 'Data Center A - Network Room',
    type: 'Core Switch',
    status: 'healthy',
    uptime: 245,
    cpuLoad: 35,
    memoryUsage: 48,
    temperature: 43,
    throughput: 11800,
    packetLoss: 0.01,
    latency: 0.9,
    portCount: 48,
    activePorts: 44,
    alerts: [],
    lastMaintenance: '2025-01-10',
    nextMaintenance: '2025-04-10'
  },
  {
    id: 'SW-AGG-01',
    name: 'Aggregation Switch 1',
    location: 'Data Center A - Row 1',
    type: 'Aggregation Switch',
    status: 'warning',
    uptime: 180,
    cpuLoad: 68,
    memoryUsage: 72,
    temperature: 48,
    throughput: 8200,
    packetLoss: 0.15,
    latency: 2.1,
    portCount: 24,
    activePorts: 22,
    alerts: [
      { severity: 'warning', message: 'High CPU usage detected', timestamp: '2025-01-16 09:30:00' },
      { severity: 'warning', message: 'Packet loss above threshold', timestamp: '2025-01-16 08:15:00' }
    ],
    lastMaintenance: '2024-12-15',
    nextMaintenance: '2025-03-15'
  },
  {
    id: 'SW-AGG-02',
    name: 'Aggregation Switch 2',
    location: 'Data Center A - Row 2',
    type: 'Aggregation Switch',
    status: 'critical',
    uptime: 45,
    cpuLoad: 92,
    memoryUsage: 88,
    temperature: 55,
    throughput: 3500,
    packetLoss: 2.5,
    latency: 8.5,
    portCount: 24,
    activePorts: 18,
    alerts: [
      { severity: 'critical', message: 'CPU overload - packet drops occurring', timestamp: '2025-01-16 10:00:00' },
      { severity: 'critical', message: 'High temperature - fan failure risk', timestamp: '2025-01-16 09:45:00' },
      { severity: 'warning', message: 'Link flapping detected on port 12', timestamp: '2025-01-16 09:20:00' }
    ],
    lastMaintenance: '2024-11-20',
    nextMaintenance: '2025-02-20'
  },
  {
    id: 'SW-ACC-01',
    name: 'Access Switch Row1',
    location: 'Data Center A - Row 1',
    type: 'Access Switch',
    status: 'warning',
    uptime: 120,
    cpuLoad: 55,
    memoryUsage: 58,
    temperature: 44,
    throughput: 3200,
    packetLoss: 0.08,
    latency: 1.5,
    portCount: 48,
    activePorts: 35,
    alerts: [
      { severity: 'warning', message: 'Multiple CRC errors on uplink', timestamp: '2025-01-15 14:30:00' }
    ],
    lastMaintenance: '2024-12-28',
    nextMaintenance: '2025-03-28'
  },
  {
    id: 'FW-01',
    name: 'Firewall Cluster Primary',
    location: 'Data Center A - Security Zone',
    type: 'Firewall',
    status: 'healthy',
    uptime: 245,
    cpuLoad: 28,
    memoryUsage: 52,
    temperature: 38,
    throughput: 4500,
    connections: 12500,
    sessions: 8500,
    alerts: [],
    lastMaintenance: '2025-01-05',
    nextMaintenance: '2025-04-05'
  },
  {
    id: 'LB-01',
    name: 'Load Balancer 1',
    location: 'Data Center A - DMZ',
    type: 'Load Balancer',
    status: 'healthy',
    uptime: 200,
    cpuLoad: 42,
    memoryUsage: 55,
    temperature: 40,
    throughput: 3800,
    activeConnections: 5200,
    requestsPerSec: 1250,
    alerts: [],
    lastMaintenance: '2025-01-08',
    nextMaintenance: '2025-04-08'
  },
  {
    id: 'RTR-01',
    name: 'Edge Router 1',
    location: 'Data Center A - Network Edge',
    type: 'Router',
    status: 'warning',
    uptime: 300,
    cpuLoad: 65,
    memoryUsage: 70,
    temperature: 46,
    throughput: 8500,
    bgpPeers: 4,
    prefixCount: 125000,
    alerts: [
      { severity: 'warning', message: 'BGP route flapping detected', timestamp: '2025-01-15 16:20:00' }
    ],
    lastMaintenance: '2024-12-18',
    nextMaintenance: '2025-03-18'
  }
])

// Network traffic trends
const trafficTrends = ref([
  { time: '00:00', inbound: 3200, outbound: 2800, packetLoss: 0.02 },
  { time: '02:00', inbound: 2800, outbound: 2500, packetLoss: 0.01 },
  { time: '04:00', inbound: 2500, outbound: 2200, packetLoss: 0.01 },
  { time: '06:00', inbound: 3000, outbound: 2600, packetLoss: 0.02 },
  { time: '08:00', inbound: 5800, outbound: 5200, packetLoss: 0.03 },
  { time: '10:00', inbound: 8500, outbound: 7800, packetLoss: 0.05 },
  { time: '12:00', inbound: 9200, outbound: 8500, packetLoss: 0.04 },
  { time: '14:00', inbound: 10500, outbound: 9600, packetLoss: 0.06 },
  { time: '16:00', inbound: 9800, outbound: 8900, packetLoss: 0.05 },
  { time: '18:00', inbound: 7800, outbound: 7200, packetLoss: 0.04 },
  { time: '20:00', inbound: 6200, outbound: 5800, packetLoss: 0.03 },
  { time: '22:00', inbound: 4800, outbound: 4200, packetLoss: 0.02 }
])

// Top talkers data
const topTalkers = ref([
  { ip: '10.1.1.100', hostname: 'web-server-01', bytes: 1250000, percentage: 15.2 },
  { ip: '10.1.1.101', hostname: 'web-server-02', bytes: 1180000, percentage: 14.3 },
  { ip: '10.1.2.50', hostname: 'db-server-01', bytes: 980000, percentage: 11.9 },
  { ip: '10.1.3.20', hostname: 'storage-node-01', bytes: 850000, percentage: 10.3 },
  { ip: '10.1.1.200', hostname: 'cache-server-01', bytes: 720000, percentage: 8.7 }
])

// Protocol distribution
const protocolDistribution = ref([
  { protocol: 'HTTP/HTTPS', percentage: 45, bytes: 3250000 },
  { protocol: 'Database', percentage: 22, bytes: 1580000 },
  { protocol: 'Storage', percentage: 15, bytes: 1080000 },
  { protocol: 'DNS', percentage: 8, bytes: 580000 },
  { protocol: 'Other', percentage: 10, bytes: 720000 }
])

// Historical fault data
const faultHistory = ref([
  { id: 'NFLT-001', deviceId: 'SW-AGG-02', type: 'CPU Overload', severity: 'critical', timestamp: '2025-01-16 10:00:00', resolved: '', description: 'CPU usage exceeded 90% - packet drops' },
  { id: 'NFLT-002', deviceId: 'SW-AGG-02', type: 'High Temperature', severity: 'critical', timestamp: '2025-01-16 09:45:00', resolved: '', description: 'Switch temperature exceeded 55°C' },
  { id: 'NFLT-003', deviceId: 'SW-AGG-01', type: 'High CPU', severity: 'warning', timestamp: '2025-01-16 09:30:00', resolved: '2025-01-16 10:15:00', description: 'CPU usage at 68% - needs investigation' },
  { id: 'NFLT-004', deviceId: 'SW-ACC-01', type: 'CRC Errors', severity: 'warning', timestamp: '2025-01-15 14:30:00', resolved: '2025-01-15 16:45:00', description: 'CRC errors detected on uplink port' },
  { id: 'NFLT-005', deviceId: 'RTR-01', type: 'BGP Flapping', severity: 'warning', timestamp: '2025-01-15 16:20:00', resolved: '2025-01-15 17:30:00', description: 'BGP route flapping detected' }
])

// Selected device
const selectedDevice = ref<any>(null)
const detailVisible = ref(false)
const historyVisible = ref(false)

// Filters
const searchKeyword = ref('')
const statusFilter = ref('all')
const typeFilter = ref('all')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const trafficChartRef = ref<HTMLElement | null>(null)
const protocolChartRef = ref<HTMLElement | null>(null)
let trafficChart: echarts.ECharts | null = null
let protocolChart: echarts.ECharts | null = null

const filteredDevices = computed(() => {
  let filtered = networkDevices.value

  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(d => d.status === statusFilter.value)
  }

  if (typeFilter.value !== 'all') {
    filtered = filtered.filter(d => d.type === typeFilter.value)
  }

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(d =>
        d.id.toLowerCase().includes(keyword) ||
        d.name.toLowerCase().includes(keyword) ||
        d.location.toLowerCase().includes(keyword)
    )
  }

  return filtered
})

const paginatedDevices = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredDevices.value.slice(start, end)
})

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
}

const getStatusColor = (status: string) => {
  switch(status) {
    case 'critical': return '#F56C6C'
    case 'warning': return '#E6A23C'
    case 'healthy': return '#67C23A'
    default: return '#909399'
  }
}

const getStatusText = (status: string) => {
  switch(status) {
    case 'critical': return 'Critical'
    case 'warning': return 'Warning'
    case 'healthy': return 'Healthy'
    default: return 'Unknown'
  }
}

const getCpuColor = (cpu: number) => {
  if (cpu > 85) return '#F56C6C'
  if (cpu > 65) return '#E6A23C'
  return '#67C23A'
}

const viewDetails = (device: any) => {
  selectedDevice.value = device
  detailVisible.value = true
}

const viewHistory = (device: any) => {
  selectedDevice.value = device
  historyVisible.value = true
}

const resetDevice = (device: any) => {
  ElMessageBox.confirm(
      `Reset ${device.id}? This will restart the network device.`,
      'Confirm Reset',
      {
        confirmButtonText: 'Reset',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    ElMessage.success(`${device.id} reset initiated`)
  }).catch(() => {})
}

const scheduleMaintenance = (device: any) => {
  ElMessageBox.confirm(
      `Schedule maintenance for ${device.id}?`,
      'Schedule Maintenance',
      {
        confirmButtonText: 'Schedule',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    ElMessage.success(`Maintenance scheduled for ${device.id}`)
  }).catch(() => {})
}

const clearAlerts = (device: any) => {
  device.alerts = []
  ElMessage.success(`Alerts cleared for ${device.id}`)
}

const refreshData = () => {
  ElMessage.info('Refreshing network data...')
  setTimeout(() => {
    ElMessage.success('Data refreshed successfully')
  }, 1000)
}

const initTrafficChart = () => {
  if (trafficChartRef.value) {
    if (trafficChart) trafficChart.dispose()

    trafficChart = echarts.init(trafficChartRef.value)
    trafficChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: {
        data: ['Inbound Traffic (Mbps)', 'Outbound Traffic (Mbps)', 'Packet Loss (%)'],
        left: 'left',
        textStyle: { color: '#606266' }
      },
      grid: { left: '8%', right: '8%', top: '15%', bottom: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: trafficTrends.value.map(d => d.time),
        axisLabel: { rotate: 45 }
      },
      yAxis: [
        { type: 'value', name: 'Traffic (Mbps)', min: 0, max: 12000 },
        { type: 'value', name: 'Packet Loss (%)', min: 0, max: 1 }
      ],
      series: [
        {
          name: 'Inbound Traffic (Mbps)',
          type: 'line',
          data: trafficTrends.value.map(d => d.inbound),
          smooth: true,
          lineStyle: { color: '#409EFF', width: 3 },
          areaStyle: { opacity: 0.1, color: '#409EFF' },
          symbol: 'circle',
          symbolSize: 6,
          label: { show: true, position: 'top', formatter: '{c} Mbps' }
        },
        {
          name: 'Outbound Traffic (Mbps)',
          type: 'line',
          data: trafficTrends.value.map(d => d.outbound),
          smooth: true,
          lineStyle: { color: '#67C23A', width: 3 },
          areaStyle: { opacity: 0.1, color: '#67C23A' },
          symbol: 'diamond',
          symbolSize: 6,
          label: { show: true, position: 'top', formatter: '{c} Mbps' }
        },
        {
          name: 'Packet Loss (%)',
          type: 'line',
          yAxisIndex: 1,
          data: trafficTrends.value.map(d => d.packetLoss),
          smooth: true,
          lineStyle: { color: '#F56C6C', width: 2, type: 'dashed' },
          symbol: 'triangle',
          symbolSize: 6,
          label: { show: true, position: 'top', formatter: '{c}%' }
        }
      ]
    })
  }
}

const initProtocolChart = () => {
  if (protocolChartRef.value) {
    if (protocolChart) protocolChart.dispose()

    protocolChart = echarts.init(protocolChartRef.value)
    protocolChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} MB)' },
      legend: {
        orient: 'vertical',
        left: 'left',
        textStyle: { color: '#606266' }
      },
      series: [
        {
          name: 'Protocol Distribution',
          type: 'pie',
          radius: ['40%', '65%'],
          data: protocolDistribution.value.map(p => ({ name: p.protocol, value: p.bytes / 1000000 })),
          label: { show: true, formatter: '{b}: {d}%' },
          emphasis: { scale: true },
          itemStyle: {
            borderRadius: 8,
            borderColor: '#fff',
            borderWidth: 2
          }
        }
      ]
    })
  }
}

const handleResize = () => {
  trafficChart?.resize()
  protocolChart?.resize()
}

watch(isLoaded, (loaded) => {
  if (loaded) {
    nextTick(() => {
      initTrafficChart()
      initProtocolChart()
      window.addEventListener('resize', handleResize)
    })
  }
})

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

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trafficChart?.dispose()
  protocolChart?.dispose()
})

// Helper computed values
const totalThroughput = computed(() => {
  return networkDevices.value.reduce((sum, d) => sum + (d.throughput || 0), 0)
})

const avgCpuLoad = computed(() => {
  const sum = networkDevices.value.reduce((acc, d) => acc + (d.cpuLoad || 0), 0)
  return (sum / networkDevices.value.filter(d => d.cpuLoad).length).toFixed(1)
})

const criticalCount = computed(() => {
  return networkDevices.value.filter(d => d.status === 'critical').length
})

const warningCount = computed(() => {
  return networkDevices.value.filter(d => d.status === 'warning').length
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
          <span class="loading-title">Loading</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Network Fault Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="network-faults">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Network Fault Management</h2>
        <p class="subtitle">Real-time network device monitoring and fault analysis</p>
      </div>
      <div class="header-actions">
        <el-input
            v-model="searchKeyword"
            placeholder="Search by Device ID or Location..."
            clearable
            style="width: 260px"
            :prefix-icon="Search"
        />
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 130px">
          <el-option label="All" value="all" />
          <el-option label="Healthy" value="healthy" />
          <el-option label="Warning" value="warning" />
          <el-option label="Critical" value="critical" />
        </el-select>
        <el-select v-model="typeFilter" placeholder="Type" clearable style="width: 150px">
          <el-option label="All" value="all" />
          <el-option label="Core Switch" value="Core Switch" />
          <el-option label="Aggregation Switch" value="Aggregation Switch" />
          <el-option label="Access Switch" value="Access Switch" />
          <el-option label="Firewall" value="Firewall" />
          <el-option label="Router" value="Router" />
          <el-option label="Load Balancer" value="Load Balancer" />
        </el-select>
        <el-button type="primary" @click="refreshData">
          <el-icon><RefreshRight /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Statistics Overview -->
    <div class="stats-grid">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon total">
            <el-icon><Monitor /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ networkDevices.length }}</div>
            <div class="stat-label">Total Devices</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon healthy">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ networkDevices.filter(d => d.status === 'healthy').length }}</div>
            <div class="stat-label">Healthy</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon warning">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ warningCount }}</div>
            <div class="stat-label">Warning</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon critical">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ criticalCount }}</div>
            <div class="stat-label">Critical</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon throughput">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ (totalThroughput / 1000).toFixed(1) }} Gbps</div>
            <div class="stat-label">Total Throughput</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Top Talkers Section -->
    <div class="top-talkers">
      <div class="section-header">
        <span>Top Talkers (Last Hour)</span>
        <el-tag type="info" size="small">High Bandwidth Usage</el-tag>
      </div>
      <el-table :data="topTalkers" size="small" style="width: 100%">
        <el-table-column prop="ip" label="IP Address" />
        <el-table-column prop="hostname" label="Hostname"  />
        <el-table-column label="Traffic" >
          <template #default="{ row }">
            <div class="traffic-bar">
              <div class="bar-fill" :style="{ width: row.percentage + '%' }"></div>
              <span class="bar-label">{{ (row.bytes / 1000000).toFixed(1) }} MB ({{ row.percentage }}%)</span>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Network Traffic Trends (24 Hours)</span>
            <el-tag type="info" size="small">Live Monitoring</el-tag>
          </div>
        </template>
        <div ref="trafficChartRef" class="chart"></div>
      </el-card>

      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Protocol Distribution</span>
            <el-tag type="success" size="small">Traffic Analysis</el-tag>
          </div>
        </template>
        <div ref="protocolChartRef" class="chart"></div>
      </el-card>
    </div>

    <!-- Network Devices Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="table-header">
          <span class="table-title">Network Devices Overview</span>
          <span class="table-subtitle">{{ filteredDevices.length }} devices displayed</span>
        </div>
      </template>
      <el-table :data="paginatedDevices" stripe style="width: 100%">
        <el-table-column prop="id" label="Device ID" width="120" align="center" />
        <el-table-column prop="name" label="Name" align="center"  />
        <el-table-column prop="location" label="Location" width="250px" align="center"  show-overflow-tooltip />
        <el-table-column prop="type" label="Type" align="center" />
        <el-table-column label="Status"  align="center">
          <template #default="{ row }">
            <div class="status-indicator">
              <span class="status-dot" :style="{ background: getStatusColor(row.status) }"></span>
              <span>{{ getStatusText(row.status) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="CPU" align="center" >
          <template #default="{ row }">
            <span :style="{ color: getCpuColor(row.cpuLoad), fontWeight: 500 }">
              {{ row.cpuLoad }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Temp" align="center" >
          <template #default="{ row }">
            <span :style="{ color: row.temperature > 50 ? '#F56C6C' : row.temperature > 45 ? '#E6A23C' : '#67C23A' }">
              {{ row.temperature }}°C
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Throughput"  align="center">
          <template #default="{ row }">
            <span>{{ (row.throughput / 1000).toFixed(1) }} Gbps</span>
          </template>
        </el-table-column>
        <el-table-column label="Packet Loss"  align="center">
          <template #default="{ row }">
            <span :style="{ color: row.packetLoss > 0.5 ? '#F56C6C' : row.packetLoss > 0.1 ? '#E6A23C' : '#67C23A' }">
              {{ row.packetLoss }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Alerts" align="center" class-name="alert-column">
          <template #default="{ row }">
            <div style="position: relative; height: 100%; display: flex; align-items: center; justify-content: center;">
              <el-badge
                  :value="row.alerts.length"
                  :hidden="row.alerts.length === 0"
                  type="danger"
                  :offset="[-2, 8]"
              >
                <el-button size="small" text @click="viewDetails(row)">
                  <el-icon><Warning /></el-icon>
                </el-button>
              </el-badge>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Actions" fixed="right" width="180px"  align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetails(row)">Details</el-button>
            <el-button type="info" link size="small" @click="viewHistory(row)">History</el-button>
            <el-button type="warning" link size="small" @click="resetDevice(row)">Reset</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredDevices.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Device Detail Dialog -->
    <el-dialog v-model="detailVisible" :title="selectedDevice?.name" width="750px">
      <div v-if="selectedDevice" class="device-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Device ID">{{ selectedDevice.id }}</el-descriptions-item>
          <el-descriptions-item label="Type">{{ selectedDevice.type }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedDevice.location }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <span class="status-indicator">
              <span class="status-dot" :style="{ background: getStatusColor(selectedDevice.status) }"></span>
              {{ getStatusText(selectedDevice.status) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="Uptime">{{ selectedDevice.uptime }} days</el-descriptions-item>
          <el-descriptions-item label="Last Maintenance">{{ selectedDevice.lastMaintenance }}</el-descriptions-item>
          <el-descriptions-item label="CPU Usage">{{ selectedDevice.cpuLoad }}%</el-descriptions-item>
          <el-descriptions-item label="Memory Usage">{{ selectedDevice.memoryUsage }}%</el-descriptions-item>
          <el-descriptions-item label="Temperature">{{ selectedDevice.temperature }}°C</el-descriptions-item>
          <el-descriptions-item label="Throughput">{{ (selectedDevice.throughput / 1000).toFixed(1) }} Gbps</el-descriptions-item>
          <el-descriptions-item label="Packet Loss">{{ selectedDevice.packetLoss }}%</el-descriptions-item>
          <el-descriptions-item label="Latency">{{ selectedDevice.latency }} ms</el-descriptions-item>
          <el-descriptions-item label="Ports">{{ selectedDevice.activePorts }}/{{ selectedDevice.portCount }} active</el-descriptions-item>
          <el-descriptions-item v-if="selectedDevice.connections" label="Connections">{{ selectedDevice.connections }}</el-descriptions-item>
          <el-descriptions-item v-if="selectedDevice.bgpPeers" label="BGP Peers">{{ selectedDevice.bgpPeers }}</el-descriptions-item>
        </el-descriptions>

        <div v-if="selectedDevice.alerts.length > 0" class="alerts-section">
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
            <el-table-column prop="timestamp" label="Timestamp" width="160" />
          </el-table>
          <div class="alerts-actions">
            <el-button type="primary" size="small" @click="clearAlerts(selectedDevice)">Clear Alerts</el-button>
          </div>
        </div>

        <div class="detail-actions">
          <el-button type="warning" @click="resetDevice(selectedDevice)">Reset Device</el-button>
          <el-button type="primary" @click="scheduleMaintenance(selectedDevice)">Schedule Maintenance</el-button>
          <el-button type="info" @click="viewHistory(selectedDevice)">View Fault History</el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Fault History Dialog -->
    <el-dialog v-model="historyVisible" :title="`Fault History - ${selectedDevice?.id}`" width="800px">
      <el-table :data="faultHistory.filter(f => f.deviceId === selectedDevice?.id)" stripe>
        <el-table-column prop="id" label="Fault ID" width="100" />
        <el-table-column prop="type" label="Fault Type" width="140" />
        <el-table-column label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="row.severity === 'critical' ? 'danger' : 'warning'" size="small">
              {{ row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="Description" min-width="200" />
        <el-table-column prop="timestamp" label="Occurred" width="160" />
        <el-table-column prop="resolved" label="Resolved" width="160">
          <template #default="{ row }">
            <span v-if="row.resolved">{{ row.resolved }}</span>
            <span v-else class="unresolved">Unresolved</span>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="historyVisible = false">Close</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
/* Loading Screen */
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

/* Main Content */
.network-faults {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
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
  background: linear-gradient(135deg, #303133, #606266);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  margin: 0;
  color: #909399;
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
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 16px;
}

.stat-card :deep(.el-card__body) {
  padding: 16px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 12px;
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

.stat-icon.total { background: rgba(64, 158, 255, 0.1); color: #409EFF; }
.stat-icon.healthy { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
.stat-icon.warning { background: rgba(230, 162, 60, 0.1); color: #E6A23C; }
.stat-icon.critical { background: rgba(245, 108, 108, 0.1); color: #F56C6C; }
.stat-icon.throughput { background: rgba(64, 158, 255, 0.1); color: #409EFF; }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* Top Talkers */
.top-talkers {
  background: white;
  border-radius: 16px;
  padding: 16px 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 600;
  font-size: 15px;
}

.traffic-bar {
  position: relative;
  background: #ebeef5;
  border-radius: 10px;
  height: 24px;
  overflow: hidden;
}

.bar-fill {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  background: linear-gradient(90deg, #409EFF, #67C23A);
  border-radius: 10px;
}

.bar-label {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  height: 24px;
  padding-left: 8px;
  font-size: 12px;
  color: #303133;
  z-index: 1;
}

/* Charts */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  border-radius: 16px;
}

.chart-card :deep(.el-card__body) {
  padding: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.chart {
  width: 100%;
  height: 320px;
}

/* Table */
.table-card {
  border-radius: 16px;
}

.table-card :deep(.el-card__body) {
  padding: 0;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-title {
  font-size: 16px;
  font-weight: 600;
}

.table-subtitle {
  font-size: 12px;
  color: #909399;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.pagination-wrapper {
  padding: 16px 20px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
}

/* Detail Dialog */
.device-detail {
  padding: 0 0 16px 0;
}

.alerts-section {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.alerts-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
}

.alerts-actions {
  margin-top: 12px;
  text-align: right;
}

.detail-actions {
  margin-top: 20px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  flex-wrap: wrap;
}

.unresolved {
  color: #F56C6C;
  font-style: italic;
}

.alert-badge-wrapper {
  position: relative;
  display: inline-block;
  cursor: pointer;
}

.custom-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #F56C6C;
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  border: 1px solid white;
}

.alert-column {
  height: 100%;
  display: flex;
  background-color: #0f4c81;
  align-items: center;
  justify-content: center;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  }

  .charts-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .network-faults {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions {
    flex-direction: column;
  }

  .header-actions .el-input,
  .header-actions .el-select,
  .header-actions .el-button {
    width: 100%;
  }

  .chart {
    height: 260px;
  }

  .traffic-bar {
    min-width: 150px;
  }
}
</style>