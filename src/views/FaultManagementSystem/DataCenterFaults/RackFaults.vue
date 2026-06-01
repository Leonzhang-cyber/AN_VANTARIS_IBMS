<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted, computed } from 'vue'
import {
  Search, RefreshRight, Warning, CircleCheck, Clock,
  TrendCharts, Monitor, Connection, DataAnalysis,
  Document, Setting, More, ArrowUp, ArrowDown,
  VideoCamera, Histogram, Grid, Platform
} from "@element-plus/icons-vue"
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Connecting to rack monitoring system...',
  'Loading environmental sensors...',
  'Analyzing rack health data...'
]

// Rack Units Data
const rackUnits = ref([
  {
    id: 'RACK-A01',
    name: 'Compute Rack A01',
    location: 'Data Center A - Row 1',
    status: 'warning',
    inletTemp: 24.5,
    outletTemp: 28.2,
    humidity: 52,
    powerConsumption: 12.8,
    airflow: 850,
    cpuLoad: 68,
    serverCount: 12,
    alerts: [
      { severity: 'warning', message: 'Inlet temperature above 24°C', timestamp: '2025-01-16 08:30:00' },
      { severity: 'info', message: 'Humidity approaching threshold', timestamp: '2025-01-15 14:20:00' }
    ],
    servers: [
      { id: 'SRV-A01-01', name: 'DB Server 1', status: 'healthy', cpu: 45, temp: 72 },
      { id: 'SRV-A01-02', name: 'DB Server 2', status: 'healthy', cpu: 52, temp: 74 },
      { id: 'SRV-A01-03', name: 'App Server 1', status: 'warning', cpu: 78, temp: 78 },
      { id: 'SRV-A01-04', name: 'Web Server 1', status: 'healthy', cpu: 38, temp: 70 }
    ],
    lastMaintenance: '2024-12-10',
    nextMaintenance: '2025-03-10'
  },
  {
    id: 'RACK-A02',
    name: 'Storage Rack A02',
    location: 'Data Center A - Row 1',
    status: 'critical',
    inletTemp: 27.8,
    outletTemp: 32.5,
    humidity: 58,
    powerConsumption: 8.5,
    airflow: 620,
    cpuLoad: 42,
    serverCount: 8,
    alerts: [
      { severity: 'critical', message: 'High inlet temperature - cooling failure risk', timestamp: '2025-01-16 09:15:00' },
      { severity: 'warning', message: 'Airflow below recommended level', timestamp: '2025-01-16 08:45:00' }
    ],
    servers: [
      { id: 'SRV-A02-01', name: 'Storage Node 1', status: 'warning', cpu: 35, temp: 82 },
      { id: 'SRV-A02-02', name: 'Storage Node 2', status: 'critical', cpu: 38, temp: 85 },
      { id: 'SRV-A02-03', name: 'Backup Server', status: 'healthy', cpu: 28, temp: 76 }
    ],
    lastMaintenance: '2024-11-15',
    nextMaintenance: '2025-02-15'
  },
  {
    id: 'RACK-B01',
    name: 'Compute Rack B01',
    location: 'Data Center B - Row 2',
    status: 'healthy',
    inletTemp: 21.2,
    outletTemp: 24.5,
    humidity: 45,
    powerConsumption: 15.2,
    airflow: 1100,
    cpuLoad: 72,
    serverCount: 16,
    alerts: [],
    servers: [
      { id: 'SRV-B01-01', name: 'HPC Node 1', status: 'healthy', cpu: 85, temp: 68 },
      { id: 'SRV-B01-02', name: 'HPC Node 2', status: 'healthy', cpu: 82, temp: 67 },
      { id: 'SRV-B01-03', name: 'HPC Node 3', status: 'healthy', cpu: 88, temp: 69 }
    ],
    lastMaintenance: '2025-01-05',
    nextMaintenance: '2025-04-05'
  },
  {
    id: 'RACK-B02',
    name: 'Network Rack B02',
    location: 'Data Center B - Row 2',
    status: 'warning',
    inletTemp: 23.8,
    outletTemp: 27.1,
    humidity: 48,
    powerConsumption: 4.2,
    airflow: 450,
    cpuLoad: 25,
    serverCount: 6,
    alerts: [
      { severity: 'warning', message: 'Network switch temperature high', timestamp: '2025-01-15 13:30:00' }
    ],
    servers: [
      { id: 'SW-B02-01', name: 'Core Switch 1', status: 'warning', temp: 72 },
      { id: 'SW-B02-02', name: 'Core Switch 2', status: 'healthy', temp: 68 },
      { id: 'FW-B02-01', name: 'Firewall Cluster', status: 'healthy', cpu: 45 }
    ],
    lastMaintenance: '2024-12-20',
    nextMaintenance: '2025-03-20'
  },
  {
    id: 'RACK-C01',
    name: 'Database Rack C01',
    location: 'Data Center C - Row 3',
    status: 'critical',
    inletTemp: 26.5,
    outletTemp: 31.2,
    humidity: 55,
    powerConsumption: 18.5,
    airflow: 980,
    cpuLoad: 85,
    serverCount: 10,
    alerts: [
      { severity: 'critical', message: 'CPU overheating on multiple servers', timestamp: '2025-01-16 10:00:00' },
      { severity: 'critical', message: 'Power consumption spike detected', timestamp: '2025-01-16 09:30:00' }
    ],
    servers: [
      { id: 'SRV-C01-01', name: 'Primary DB', status: 'critical', cpu: 92, temp: 88 },
      { id: 'SRV-C01-02', name: 'Secondary DB', status: 'warning', cpu: 78, temp: 82 },
      { id: 'SRV-C01-03', name: 'Analytics DB', status: 'warning', cpu: 85, temp: 80 }
    ],
    lastMaintenance: '2024-10-10',
    nextMaintenance: '2025-01-10'
  }
])

// Environmental trends
const envTrends = ref([
  { time: '00:00', avgTemp: 23.2, maxTemp: 24.5, avgHumidity: 46 },
  { time: '02:00', avgTemp: 23.0, maxTemp: 24.2, avgHumidity: 45 },
  { time: '04:00', avgTemp: 22.8, maxTemp: 24.0, avgHumidity: 45 },
  { time: '06:00', avgTemp: 22.5, maxTemp: 23.8, avgHumidity: 44 },
  { time: '08:00', avgTemp: 23.0, maxTemp: 24.5, avgHumidity: 46 },
  { time: '10:00', avgTemp: 23.8, maxTemp: 25.5, avgHumidity: 48 },
  { time: '12:00', avgTemp: 24.5, maxTemp: 26.5, avgHumidity: 50 },
  { time: '14:00', avgTemp: 25.0, maxTemp: 27.2, avgHumidity: 52 },
  { time: '16:00', avgTemp: 24.8, maxTemp: 27.0, avgHumidity: 51 },
  { time: '18:00', avgTemp: 24.2, maxTemp: 26.2, avgHumidity: 49 },
  { time: '20:00', avgTemp: 23.8, maxTemp: 25.5, avgHumidity: 48 },
  { time: '22:00', avgTemp: 23.5, maxTemp: 25.0, avgHumidity: 47 }
])

// Power consumption by rack
const powerByRack = ref([
  { rack: 'RACK-A01', power: 12.8, trend: 'up' },
  { rack: 'RACK-A02', power: 8.5, trend: 'stable' },
  { rack: 'RACK-B01', power: 15.2, trend: 'up' },
  { rack: 'RACK-B02', power: 4.2, trend: 'stable' },
  { rack: 'RACK-C01', power: 18.5, trend: 'up' }
])

// Server distribution by status
const serverDistribution = ref([
  { status: 'Healthy', count: 32, percentage: 64 },
  { status: 'Warning', count: 12, percentage: 24 },
  { status: 'Critical', count: 6, percentage: 12 }
])

// Historical fault data
const faultHistory = ref([
  { id: 'RFLT-001', rackId: 'RACK-C01', serverId: 'SRV-C01-01', type: 'CPU Overheat', severity: 'critical', timestamp: '2025-01-16 10:00:00', resolved: '', description: 'CPU temperature exceeded 85°C threshold' },
  { id: 'RFLT-002', rackId: 'RACK-A02', type: 'Temperature High', severity: 'critical', timestamp: '2025-01-16 09:15:00', resolved: '', description: 'Rack inlet temperature exceeded 27°C' },
  { id: 'RFLT-003', rackId: 'RACK-A01', type: 'High Humidity', severity: 'warning', timestamp: '2025-01-15 08:30:00', resolved: '2025-01-15 11:20:00', description: 'Rack humidity exceeded 50%' },
  { id: 'RFLT-004', rackId: 'RACK-B02', type: 'Switch Temperature', severity: 'warning', timestamp: '2025-01-14 14:45:00', resolved: '2025-01-14 16:30:00', description: 'Core switch temperature reached 72°C' }
])

// Selected rack
const selectedRack = ref<any>(null)
const detailVisible = ref(false)
const historyVisible = ref(false)
const serverDetailVisible = ref(false)
const selectedServer = ref<any>(null)

// Filters
const searchKeyword = ref('')
const statusFilter = ref('all')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const envChartRef = ref<HTMLElement | null>(null)
const powerChartRef = ref<HTMLElement | null>(null)
const serverChartRef = ref<HTMLElement | null>(null)
let envChart: echarts.ECharts | null = null
let powerChart: echarts.ECharts | null = null
let serverChart: echarts.ECharts | null = null

const filteredRacks = computed(() => {
  let filtered = rackUnits.value

  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(r => r.status === statusFilter.value)
  }

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(r =>
        r.id.toLowerCase().includes(keyword) ||
        r.name.toLowerCase().includes(keyword) ||
        r.location.toLowerCase().includes(keyword)
    )
  }

  return filtered
})

const paginatedRacks = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRacks.value.slice(start, end)
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

const getTempColor = (temp: number) => {
  if (temp > 27) return '#F56C6C'
  if (temp > 24) return '#E6A23C'
  return '#67C23A'
}

const viewDetails = (rack: any) => {
  selectedRack.value = rack
  detailVisible.value = true
}

const viewServerDetails = (rack: any, server: any) => {
  selectedRack.value = rack
  selectedServer.value = server
  serverDetailVisible.value = true
}

const viewHistory = (rack: any) => {
  selectedRack.value = rack
  historyVisible.value = true
}

const resetRack = (rack: any) => {
  ElMessageBox.confirm(
      `Reset rack monitoring for ${rack.id}? This will clear temporary alerts.`,
      'Confirm Reset',
      {
        confirmButtonText: 'Reset',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    ElMessage.success(`${rack.id} monitoring reset`)
  }).catch(() => {})
}

const scheduleMaintenance = (rack: any) => {
  ElMessageBox.confirm(
      `Schedule maintenance for ${rack.id}?`,
      'Schedule Maintenance',
      {
        confirmButtonText: 'Schedule',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    ElMessage.success(`Maintenance scheduled for ${rack.id}`)
  }).catch(() => {})
}

const clearAlerts = (rack: any) => {
  rack.alerts = []
  ElMessage.success(`Alerts cleared for ${rack.id}`)
}

const refreshData = () => {
  ElMessage.info('Refreshing rack data...')
  setTimeout(() => {
    ElMessage.success('Data refreshed successfully')
  }, 1000)
}

const initEnvChart = () => {
  if (envChartRef.value) {
    if (envChart) envChart.dispose()

    envChart = echarts.init(envChartRef.value)
    envChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: {
        data: ['Average Temp (°C)', 'Max Temp (°C)', 'Average Humidity (%)'],
        left: 'left',
        textStyle: { color: '#606266' }
      },
      grid: { left: '8%', right: '8%', top: '15%', bottom: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: envTrends.value.map(d => d.time),
        axisLabel: { rotate: 45 }
      },
      yAxis: [
        { type: 'value', name: 'Temperature (°C)', min: 20, max: 30 },
        { type: 'value', name: 'Humidity (%)', min: 40, max: 60 }
      ],
      series: [
        {
          name: 'Average Temp (°C)',
          type: 'line',
          data: envTrends.value.map(d => d.avgTemp),
          smooth: true,
          lineStyle: { color: '#409EFF', width: 3 },
          areaStyle: { opacity: 0.1, color: '#409EFF' },
          symbol: 'circle',
          symbolSize: 6,
          label: { show: true, position: 'top', formatter: '{c}°C' }
        },
        {
          name: 'Max Temp (°C)',
          type: 'line',
          data: envTrends.value.map(d => d.maxTemp),
          smooth: true,
          lineStyle: { color: '#F56C6C', width: 3 },
          symbol: 'diamond',
          symbolSize: 6,
          label: { show: true, position: 'top', formatter: '{c}°C' }
        },
        {
          name: 'Average Humidity (%)',
          type: 'line',
          yAxisIndex: 1,
          data: envTrends.value.map(d => d.avgHumidity),
          smooth: true,
          lineStyle: { color: '#67C23A', width: 2, type: 'dashed' },
          symbol: 'triangle',
          symbolSize: 6,
          label: { show: true, position: 'top', formatter: '{c}%' }
        }
      ]
    })
  }
}

const initPowerChart = () => {
  if (powerChartRef.value) {
    if (powerChart) powerChart.dispose()

    powerChart = echarts.init(powerChartRef.value)
    powerChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['Power Consumption (kW)'], left: 'left' },
      grid: { left: '10%', right: '8%', top: '10%', bottom: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: powerByRack.value.map(p => p.rack),
        axisLabel: { fontWeight: 500 }
      },
      yAxis: { type: 'value', name: 'Power (kW)' },
      series: [
        {
          name: 'Power Consumption (kW)',
          type: 'bar',
          data: powerByRack.value.map(p => p.power),
          itemStyle: {
            color: (params: any) => {
              const trend = powerByRack.value[params.dataIndex].trend
              return trend === 'up' ? '#F56C6C' : '#67C23A'
            },
            borderRadius: [4, 4, 0, 0]
          },
          label: { show: true, position: 'top', formatter: '{c} kW' }
        }
      ]
    })
  }
}

const initServerChart = () => {
  if (serverChartRef.value) {
    if (serverChart) serverChart.dispose()

    serverChart = echarts.init(serverChartRef.value)
    serverChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} servers)' },
      legend: { orient: 'vertical', left: 'left', textStyle: { color: '#606266' } },
      series: [
        {
          name: 'Server Status',
          type: 'pie',
          radius: ['40%', '65%'],
          data: serverDistribution.value.map(s => ({ name: s.status, value: s.count })),
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
  envChart?.resize()
  powerChart?.resize()
  serverChart?.resize()
}

watch(isLoaded, (loaded) => {
  if (loaded) {
    nextTick(() => {
      initEnvChart()
      initPowerChart()
      initServerChart()
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
  envChart?.dispose()
  powerChart?.dispose()
  serverChart?.dispose()
})

// Helper computed values
const totalServers = computed(() => {
  return rackUnits.value.reduce((sum, r) => sum + r.serverCount, 0)
})

const avgPower = computed(() => {
  const sum = rackUnits.value.reduce((acc, r) => acc + r.powerConsumption, 0)
  return (sum / rackUnits.value.length).toFixed(1)
})

const avgInletTemp = computed(() => {
  const sum = rackUnits.value.reduce((acc, r) => acc + r.inletTemp, 0)
  return (sum / rackUnits.value.length).toFixed(1)
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
        <div class="loading-tip">Rack Fault Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="rack-faults">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Rack Fault Management</h2>
        <p class="subtitle">Server rack environmental monitoring and health analysis</p>
      </div>
      <div class="header-actions">
        <el-input
            v-model="searchKeyword"
            placeholder="Search by Rack ID or Location..."
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
            <el-icon><Grid /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ rackUnits.length }}</div>
            <div class="stat-label">Total Racks</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon servers">
            <el-icon><Platform /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ totalServers }}</div>
            <div class="stat-label">Total Servers</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon healthy">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ rackUnits.filter(r => r.status === 'healthy').length }}</div>
            <div class="stat-label">Healthy Racks</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon warning">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ rackUnits.filter(r => r.status === 'warning').length }}</div>
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
            <div class="stat-value">{{ rackUnits.filter(r => r.status === 'critical').length }}</div>
            <div class="stat-label">Critical</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Environmental Trends (24 Hours)</span>
            <el-tag type="info" size="small">Live Monitoring</el-tag>
          </div>
        </template>
        <div ref="envChartRef" class="chart"></div>
      </el-card>

      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Power Consumption by Rack</span>
            <el-tag type="warning" size="small">Red = Increasing</el-tag>
          </div>
        </template>
        <div ref="powerChartRef" class="chart"></div>
      </el-card>
    </div>

    <!-- Third Row -->
    <div class="charts-row">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Server Distribution by Status</span>
            <el-tag type="info" size="small">Overall Health</el-tag>
          </div>
        </template>
        <div ref="serverChartRef" class="chart"></div>
      </el-card>

      <el-card class="stats-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Key Metrics</span>
            <el-tag type="success" size="small">Current Values</el-tag>
          </div>
        </template>
        <div class="key-metrics">
          <div class="metric-item">
            <div class="metric-label">Average Inlet Temp</div>
            <div class="metric-value" :style="{ color: getTempColor(Number(avgInletTemp)) }">{{ avgInletTemp }}°C</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">Average Power</div>
            <div class="metric-value">{{ avgPower }} kW</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">Total Power</div>
            <div class="metric-value">{{ rackUnits.reduce((sum, r) => sum + r.powerConsumption, 0).toFixed(1) }} kW</div>
          </div>
          <div class="metric-item">
            <div class="metric-label">Critical Alerts</div>
            <div class="metric-value critical">{{ faultHistory.filter(f => f.severity === 'critical' && !f.resolved).length }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Racks Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="table-header">
          <span class="table-title">Server Racks Overview</span>
          <span class="table-subtitle">{{ filteredRacks.length }} racks displayed</span>
        </div>
      </template>
      <el-table :data="paginatedRacks" stripe style="width: 100%">
        <el-table-column prop="id" label="Rack ID" width="110" />
        <el-table-column prop="name" label="Name" min-width="150"  align="center"  />
        <el-table-column prop="location" label="Location" min-width="180" align="center"  show-overflow-tooltip />
        <el-table-column label="Status" width="100">
          <template #default="{ row }">
            <div class="status-indicator">
              <span class="status-dot" :style="{ background: getStatusColor(row.status) }"></span>
              <span>{{ getStatusText(row.status) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Temp" width="100">
          <template #default="{ row }">
            <div class="temp-cell">
              <span>In: <span :style="{ color: getTempColor(row.inletTemp) }">{{ row.inletTemp }}°C</span></span>
              <span>Out: <span :style="{ color: getTempColor(row.outletTemp) }">{{ row.outletTemp }}°C</span></span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="humidity" label="Humidity" align="center" >
          <template #default="{ row }">
            <span :style="{ color: row.humidity > 55 ? '#F56C6C' : row.humidity > 50 ? '#E6A23C' : '#67C23A' }">
              {{ row.humidity }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="powerConsumption" label="Power" align="center" >
          <template #default="{ row }">
            <span>{{ row.powerConsumption }} kW</span>
          </template>
        </el-table-column>
        <el-table-column prop="serverCount" label="Servers" align="center" />
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
        <el-table-column label="Actions" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetails(row)">Details</el-button>
            <el-button type="info" link size="small" @click="viewHistory(row)">History</el-button>
            <el-button type="warning" link size="small" @click="resetRack(row)">Reset</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredRacks.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Rack Detail Dialog -->
    <el-dialog v-model="detailVisible" :title="selectedRack?.name" width="850px">
      <div v-if="selectedRack" class="rack-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Rack ID">{{ selectedRack.id }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedRack.location }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <span class="status-indicator">
              <span class="status-dot" :style="{ background: getStatusColor(selectedRack.status) }"></span>
              {{ getStatusText(selectedRack.status) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="Servers">{{ selectedRack.serverCount }}</el-descriptions-item>
          <el-descriptions-item label="Inlet Temp">{{ selectedRack.inletTemp }}°C</el-descriptions-item>
          <el-descriptions-item label="Outlet Temp">{{ selectedRack.outletTemp }}°C</el-descriptions-item>
          <el-descriptions-item label="Humidity">{{ selectedRack.humidity }}%</el-descriptions-item>
          <el-descriptions-item label="Power">{{ selectedRack.powerConsumption }} kW</el-descriptions-item>
          <el-descriptions-item label="Airflow">{{ selectedRack.airflow }} CFM</el-descriptions-item>
          <el-descriptions-item label="Avg CPU Load">{{ selectedRack.cpuLoad }}%</el-descriptions-item>
          <el-descriptions-item label="Last Maintenance">{{ selectedRack.lastMaintenance }}</el-descriptions-item>
          <el-descriptions-item label="Next Maintenance">{{ selectedRack.nextMaintenance }}</el-descriptions-item>
        </el-descriptions>

        <!-- Servers in Rack -->
        <div class="servers-section">
          <h4>Servers in Rack</h4>
          <el-table :data="selectedRack.servers" size="small">
            <el-table-column prop="id" label="Server ID" width="120" />
            <el-table-column prop="name" label="Name" min-width="150" />
            <el-table-column label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'critical' ? 'danger' : row.status === 'warning' ? 'warning' : 'success'" size="small">
                  {{ row.status.toUpperCase() }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="CPU" width="80">
              <template #default="{ row }">
                <span v-if="row.cpu">{{ row.cpu }}%</span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="Temp" width="80">
              <template #default="{ row }">
                <span v-if="row.temp" :style="{ color: row.temp > 80 ? '#F56C6C' : row.temp > 75 ? '#E6A23C' : '#67C23A' }">
                  {{ row.temp }}°C
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="Actions" width="80">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="viewServerDetails(selectedRack, row)">Details</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div v-if="selectedRack.alerts.length > 0" class="alerts-section">
          <h4>Active Alerts</h4>
          <el-table :data="selectedRack.alerts" size="small">
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
            <el-button type="primary" size="small" @click="clearAlerts(selectedRack)">Clear Alerts</el-button>
          </div>
        </div>

        <div class="detail-actions">
          <el-button type="warning" @click="scheduleMaintenance(selectedRack)">Schedule Maintenance</el-button>
          <el-button type="primary" @click="viewHistory(selectedRack)">View Fault History</el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Server Detail Dialog -->
    <el-dialog v-model="serverDetailVisible" :title="`Server Details - ${selectedServer?.id}`" width="500px">
      <div v-if="selectedServer">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="Server ID">{{ selectedServer.id }}</el-descriptions-item>
          <el-descriptions-item label="Name">{{ selectedServer.name }}</el-descriptions-item>
          <el-descriptions-item label="Rack">{{ selectedRack?.id }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedRack?.location }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="selectedServer.status === 'critical' ? 'danger' : selectedServer.status === 'warning' ? 'warning' : 'success'" size="small">
              {{ selectedServer.status.toUpperCase() }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedServer.cpu" label="CPU Usage">{{ selectedServer.cpu }}%</el-descriptions-item>
          <el-descriptions-item v-if="selectedServer.temp" label="Temperature">{{ selectedServer.temp }}°C</el-descriptions-item>
          <el-descriptions-item label="Rack Inlet Temp">{{ selectedRack?.inletTemp }}°C</el-descriptions-item>
          <el-descriptions-item label="Rack Outlet Temp">{{ selectedRack?.outletTemp }}°C</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="serverDetailVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Fault History Dialog -->
    <el-dialog v-model="historyVisible" :title="`Fault History - ${selectedRack?.id}`" width="800px">
      <el-table :data="faultHistory.filter(f => f.rackId === selectedRack?.id)" stripe>
        <el-table-column prop="id" label="Fault ID" width="100" />
        <el-table-column prop="type" label="Fault Type" width="140" />
        <el-table-column prop="serverId" label="Server" width="120" />
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
.rack-faults {
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
.stat-icon.servers { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
.stat-icon.healthy { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
.stat-icon.warning { background: rgba(230, 162, 60, 0.1); color: #E6A23C; }
.stat-icon.critical { background: rgba(245, 108, 108, 0.1); color: #F56C6C; }

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

/* Charts */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card, .stats-card {
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
  height: 300px;
}

/* Key Metrics */
.key-metrics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  padding: 8px;
}

.metric-item {
  text-align: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 12px;
}

.metric-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.metric-value.critical {
  color: #F56C6C;
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

.temp-cell {
  display: flex;
  flex-direction: column;
  font-size: 12px;
  gap: 2px;
}

.pagination-wrapper {
  padding: 16px 20px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
}

/* Detail Dialog */
.rack-detail {
  padding: 0 0 16px 0;
}

.servers-section {
  margin-top: 20px;
}

.servers-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
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

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  }

  .charts-row {
    grid-template-columns: 1fr;
  }

  .key-metrics {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .rack-faults {
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

  .key-metrics {
    grid-template-columns: 1fr;
  }
}
</style>