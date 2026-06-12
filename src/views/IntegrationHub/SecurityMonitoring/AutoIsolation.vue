<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Search, Refresh, Connection, Setting, DataLine,
  Document, CircleCheck, CircleClose, Loading,
  TrendCharts, Monitor, Aim, Clock, Timer,
  Warning, Upload, Download, Filter, Cpu,
   Link, Check, Close, QuestionFilled,
  Share, Expand, Fold, Tickets, Sunny,
  Finished, SuccessFilled, Clock as ClockIcon,
  Lock, Key, Cellphone, Edit, 
  Scissor, Connection as ConnectionIcon
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing isolation engine...',
  'Loading security policies...',
  'Analyzing threat patterns...',
  'Preparing quarantine zones...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedStatus = ref('all')
const selectedRisk = ref('all')
const detailsVisible = ref(false)
const releaseConfirmVisible = ref(false)
const policyVisible = ref(false)
const chartRef = ref(null)
const timelineRef = ref(null)

let isolationChart: echarts.ECharts | null = null
let timelineChart: echarts.ECharts | null = null

// Status filters
const statusFilters = [
  { value: 'all', label: 'All Status' },
  { value: 'isolated', label: 'Isolated' },
  { value: 'monitoring', label: 'Monitoring' },
  { value: 'released', label: 'Released' },
  { value: 'pending', label: 'Pending Review' }
]

// Risk levels
const riskLevels = [
  { value: 'all', label: 'All Risks' },
  { value: 'critical', label: 'Critical' },
  { value: 'high', label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low', label: 'Low' }
]

// Isolated devices data
const isolatedDevices = ref([
  {
    id: 'ISO001', device: 'BACnet Controller - AHU-1', ip: '192.168.1.101', mac: 'AA:BB:CC:DD:EE:01',
    status: 'isolated', risk: 'critical', reason: 'Multiple command anomalies detected',
    isolatedAt: '2024-01-15 10:23:45', isolatedBy: 'Auto-Isolation Policy #001',
    duration: '2h 15m', trafficBlocked: '15.2 MB', alertsCount: 23,
    autoRelease: '2024-01-15 18:23:45', actions: ['Blocked all traffic', 'Quarantined VLAN']
  },
  {
    id: 'ISO002', device: 'Modbus Gateway - Plant Room', ip: '192.168.2.105', mac: 'BB:CC:DD:EE:FF:02',
    status: 'isolated', risk: 'high', reason: 'Unauthorized Modbus write attempts',
    isolatedAt: '2024-01-15 09:30:12', isolatedBy: 'Auto-Isolation Policy #003',
    duration: '4h 45m', trafficBlocked: '8.7 MB', alertsCount: 12,
    autoRelease: '2024-01-15 22:30:12', actions: ['Blocked Modbus traffic', 'Rate limiting applied']
  },
  {
    id: 'ISO003', device: 'MQTT Broker - IoT Hub', ip: '192.168.3.100', mac: 'CC:DD:EE:FF:00:03',
    status: 'monitoring', risk: 'medium', reason: 'Abnormal subscription patterns',
    isolatedAt: null, isolatedBy: null, duration: null, trafficBlocked: null, alertsCount: 5,
    autoRelease: null, actions: ['Under observation']
  },
  {
    id: 'ISO004', device: 'OPC-UA Server - Gateway', ip: '192.168.4.50', mac: 'DD:EE:FF:00:11:04',
    status: 'released', risk: 'high', reason: 'Authentication bypass attempt (resolved)',
    isolatedAt: '2024-01-14 22:15:30', isolatedBy: 'Auto-Isolation Policy #002',
    duration: '3h 20m', trafficBlocked: '22.1 MB', alertsCount: 8,
    autoRelease: '2024-01-15 01:35:30', actions: ['Blocked source IP', 'Reset authentication']
  },
  {
    id: 'ISO005', device: 'SNMP Agent - Core Switch', ip: '192.168.5.1', mac: 'EE:FF:00:11:22:05',
    status: 'isolated', risk: 'critical', reason: 'SNMP community string brute force',
    isolatedAt: '2024-01-15 08:45:22', isolatedBy: 'Auto-Isolation Policy #004',
    duration: '5h 30m', trafficBlocked: '45.3 MB', alertsCount: 156,
    autoRelease: '2024-01-15 22:15:22', actions: ['Blocked SNMP access', 'Isolated VLAN']
  },
  {
    id: 'ISO006', device: 'BACnet Router - Building B', ip: '192.168.1.200', mac: 'FF:00:11:22:33:06',
    status: 'pending', risk: 'medium', reason: 'Potential device spoofing detected',
    isolatedAt: null, isolatedBy: null, duration: null, trafficBlocked: null, alertsCount: 3,
    autoRelease: null, actions: ['Pending admin review']
  },
  {
    id: 'ISO007', device: 'Lighting Controller - Floor 3', ip: '192.168.6.50', mac: '00:11:22:33:44:07',
    status: 'isolated', risk: 'high', reason: 'Unauthorized configuration changes',
    isolatedAt: '2024-01-15 07:20:15', isolatedBy: 'Auto-Isolation Policy #005',
    duration: '6h 55m', trafficBlocked: '5.2 MB', alertsCount: 7,
    autoRelease: '2024-01-15 18:15:15', actions: ['Blocked write commands', 'Read-only mode']
  },
  {
    id: 'ISO008', device: 'VFD Pump - Plant', ip: '192.168.2.80', mac: '11:22:33:44:55:08',
    status: 'monitoring', risk: 'low', reason: 'Unusual command frequency',
    isolatedAt: null, isolatedBy: null, duration: null, trafficBlocked: null, alertsCount: 2,
    autoRelease: null, actions: ['Increased monitoring']
  }
])

// Auto-isolation policies
const isolationPolicies = ref([
  { id: 'POL001', name: 'Command Anomaly Detection', trigger: '5 anomalies in 5 minutes', action: 'Isolate device', duration: '4 hours', enabled: true, severity: 'critical' },
  { id: 'POL002', name: 'Authentication Failure', trigger: '10 failed attempts in 1 minute', action: 'Block source IP', duration: '2 hours', enabled: true, severity: 'high' },
  { id: 'POL003', name: 'Traffic Spike', trigger: '500% above baseline', action: 'Rate limit', duration: '1 hour', enabled: true, severity: 'medium' },
  { id: 'POL004', name: 'Protocol Violation', trigger: 'Malformed packets', action: 'Quarantine VLAN', duration: '8 hours', enabled: false, severity: 'critical' }
])

// Isolation statistics
const isolationStats = reactive({
  total: 0,
  isolated: 0,
  monitoring: 0,
  released: 0,
  pending: 0,
  critical: 0,
  high: 0,
  medium: 0,
  low: 0,
  totalTrafficBlocked: 0,
  avgIsolationTime: 0
})

// Timeline data
const timelineData = ref([
  { time: '00:00', isolated: 2, released: 0 },
  { time: '02:00', isolated: 3, released: 0 },
  { time: '04:00', isolated: 4, released: 0 },
  { time: '06:00', isolated: 5, released: 1 },
  { time: '08:00', isolated: 7, released: 1 },
  { time: '10:00', isolated: 6, released: 2 },
  { time: '12:00', isolated: 5, released: 1 },
  { time: '14:00', isolated: 4, released: 1 },
  { time: '16:00', isolated: 3, released: 0 },
  { time: '18:00', isolated: 2, released: 1 },
  { time: '20:00', isolated: 1, released: 0 },
  { time: '22:00', isolated: 1, released: 0 }
])

// Release form
const releaseForm = reactive({
  reason: '',
  confirmSecurity: false,
  permanentWhitelist: false,
  notes: ''
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: isolatedDevices.value.length
})

// Filtered devices
const filteredDevices = computed(() => {
  let filtered = isolatedDevices.value
  if (searchKeyword.value) {
    filtered = filtered.filter(d =>
        d.device.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        d.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        d.ip.includes(searchKeyword.value) ||
        d.mac.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(d => d.status === selectedStatus.value)
  }
  if (selectedRisk.value !== 'all') {
    filtered = filtered.filter(d => d.risk === selectedRisk.value)
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
        initTimelineChart()
        updateStats()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  isolationChart = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  const statusData = statusFilters.filter(s => s.value !== 'all').map(status => {
    const devices = isolatedDevices.value.filter(d => d.status === status.value)
    return { status: status.label, count: devices.length }
  })

  isolationChart?.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c})' },
    legend: { orient: 'vertical', left: 'left', data: statusData.map(s => s.status) },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: statusData.map(s => ({ name: s.status, value: s.count })),
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: {d}%' },
      itemStyle: {
        color: (params: any) => {
          const colors: Record<string, string> = {
            'Isolated': '#F56C6C',
            'Monitoring': '#E6A23C',
            'Released': '#67C23A',
            'Pending Review': '#909399'
          }
          return colors[params.name] || '#409EFF'
        }
      }
    }]
  })
}

const initTimelineChart = () => {
  if (!timelineRef.value) return

  timelineChart = echarts.init(timelineRef.value)
  timelineChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Isolated Devices', 'Released Devices'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: timelineData.value.map(t => t.time) },
    yAxis: { type: 'value', name: 'Device Count' },
    series: [
      { name: 'Isolated Devices', type: 'line', data: timelineData.value.map(t => t.isolated), smooth: true, lineStyle: { color: '#F56C6C', width: 2 }, areaStyle: { opacity: 0.1, color: '#F56C6C' }, symbol: 'circle', symbolSize: 8 },
      { name: 'Released Devices', type: 'line', data: timelineData.value.map(t => t.released), smooth: true, lineStyle: { color: '#67C23A', width: 2 }, symbol: 'diamond', symbolSize: 8 }
    ]
  })
}

const updateStats = () => {
  isolationStats.total = isolatedDevices.value.length
  isolationStats.isolated = isolatedDevices.value.filter(d => d.status === 'isolated').length
  isolationStats.monitoring = isolatedDevices.value.filter(d => d.status === 'monitoring').length
  isolationStats.released = isolatedDevices.value.filter(d => d.status === 'released').length
  isolationStats.pending = isolatedDevices.value.filter(d => d.status === 'pending').length
  isolationStats.critical = isolatedDevices.value.filter(d => d.risk === 'critical').length
  isolationStats.high = isolatedDevices.value.filter(d => d.risk === 'high').length
  isolationStats.medium = isolatedDevices.value.filter(d => d.risk === 'medium').length
  isolationStats.low = isolatedDevices.value.filter(d => d.risk === 'low').length

  // Calculate total blocked traffic
  isolationStats.totalTrafficBlocked = isolatedDevices.value.reduce((sum, d) => {
    const traffic = d.trafficBlocked ? parseFloat(d.trafficBlocked) : 0
    return sum + traffic
  }, 0)

  // Calculate average isolation time
  const isolatedDevs = isolatedDevices.value.filter(d => d.duration)
  if (isolatedDevs.length > 0) {
    const totalMinutes = isolatedDevs.reduce((sum, d) => {
      const duration = d.duration || '0h 0m'
      const hours = parseInt(duration.split('h')[0]) || 0
      const minutes = parseInt(duration.split('h')[1]?.split('m')[0]) || 0
      return sum + (hours * 60 + minutes)
    }, 0)
    isolationStats.avgIsolationTime = Math.round(totalMinutes / isolatedDevs.length)
  }
}

const handleResize = () => {
  isolationChart?.resize()
  timelineChart?.resize()
}

// ==================== Isolation Functions ====================
const refreshIsolation = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))
  updateStats()
  updateChart()
  loading.value = false
  ElMessage.success('Isolation status refreshed successfully')
}

const viewDetails = (device: any) => {
  selectedDevice.value = device
  detailsVisible.value = true
}

const openReleaseConfirm = (device: any) => {
  selectedDevice.value = device
  releaseForm.reason = ''
  releaseForm.confirmSecurity = false
  releaseForm.permanentWhitelist = false
  releaseForm.notes = ''
  releaseConfirmVisible.value = true
}

const executeRelease = async () => {
  if (!releaseForm.reason) {
    ElMessage.warning('Please provide a reason for release')
    return
  }
  if (!releaseForm.confirmSecurity) {
    ElMessage.warning('Please confirm that the device is secure')
    return
  }

  await ElMessageBox.confirm(
      `Release ${selectedDevice.value.device} from isolation?`,
      'Confirm Release',
      {
        confirmButtonText: 'Release',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  )

  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 2000))

  const index = isolatedDevices.value.findIndex(d => d.id === selectedDevice.value.id)
  if (index !== -1) {
    isolatedDevices.value[index].status = 'released'
    isolatedDevices.value[index].duration = calculateDuration(isolatedDevices.value[index].isolatedAt)
  }

  updateStats()
  updateChart()
  loading.value = false
  releaseConfirmVisible.value = false
  ElMessage.success(`${selectedDevice.value.device} released from isolation`)
}

const calculateDuration = (isolatedAt: string) => {
  if (!isolatedAt) return null
  const isolated = new Date(isolatedAt)
  const now = new Date()
  const diffMinutes = Math.floor((now.getTime() - isolated.getTime()) / 60000)
  const hours = Math.floor(diffMinutes / 60)
  const minutes = diffMinutes % 60
  return `${hours}h ${minutes}m`
}

const manuallyIsolate = async () => {
  await ElMessageBox.prompt('Enter device IP or MAC address to isolate', 'Manual Isolation', {
    confirmButtonText: 'Isolate',
    cancelButtonText: 'Cancel',
    inputPattern: /^(\d{1,3}\.){3}\d{1,3}$|^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/,
    inputErrorMessage: 'Please enter a valid IP address or MAC address'
  }).then(async ({ value }) => {
    loading.value = true
    await new Promise(resolve => setTimeout(resolve, 1500))

    const newDevice = {
      id: `ISO${String(isolatedDevices.value.length + 1).padStart(3, '0')}`,
      device: `Manual Isolation - ${value}`,
      ip: value.includes(':') ? 'N/A' : value,
      mac: value.includes(':') ? value : 'N/A',
      status: 'isolated',
      risk: 'medium',
      reason: 'Manual isolation by administrator',
      isolatedAt: new Date().toLocaleString(),
      isolatedBy: 'Manual - Admin',
      duration: '0h 0m',
      trafficBlocked: '0 MB',
      alertsCount: 0,
      autoRelease: null,
      actions: ['Manual isolation', 'Awaiting review']
    }

    isolatedDevices.value.unshift(newDevice)
    updateStats()
    updateChart()
    loading.value = false
    ElMessage.success(`Device ${value} has been isolated`)
  }).catch(() => {})
}

const viewPolicies = () => {
  policyVisible.value = true
}

const exportIsolationData = () => {
  const data = isolatedDevices.value.map(d => ({
    ID: d.id,
    Device: d.device,
    IP: d.ip,
    MAC: d.mac,
    Status: d.status,
    Risk: d.risk,
    Reason: d.reason,
    IsolatedAt: d.isolatedAt || 'N/A',
    IsolatedBy: d.isolatedBy || 'N/A',
    Duration: d.duration || 'N/A',
    TrafficBlocked: d.trafficBlocked || 'N/A',
    AlertsCount: d.alertsCount || 0,
    Actions: d.actions.join(', ')
  }))

  const csv = convertToCSV(data)
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `auto_isolation_${new Date().toISOString()}.csv`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Isolation data exported successfully')
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

const getStatusType = (status: string) => {
  switch (status) {
    case 'isolated': return 'danger'
    case 'monitoring': return 'warning'
    case 'released': return 'success'
    case 'pending': return 'info'
    default: return 'info'
  }
}

const getRiskType = (risk: string) => {
  switch (risk) {
    case 'critical': return 'danger'
    case 'high': return 'warning'
    case 'medium': return 'primary'
    default: return 'info'
  }
}

const getRiskIcon = (risk: string) => {
  switch (risk) {
    case 'critical': return Warning
    case 'high': return Warning
    case 'medium': return QuestionFilled
    default: return SuccessFilled
  }
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
          <span class="loading-title">Loading Auto-Isolation</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Security Monitoring - Auto-Isolation</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="auto-isolation-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h2>Auto-Isolation</h2>
        <el-tag type="warning" effect="dark">Security Monitoring</el-tag>
      </div>
      <div class="header-stats">
        <el-tag type="danger" effect="plain">{{ isolationStats.isolated }} Currently Isolated</el-tag>
      </div>
    </div>

    <!-- Control Panel -->
    <el-card shadow="never" class="control-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="5">
          <el-select v-model="selectedStatus" placeholder="Status" style="width: 100%" @change="updateChart">
            <el-option v-for="s in statusFilters" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-select v-model="selectedRisk" placeholder="Risk Level" clearable style="width: 100%">
            <el-option v-for="r in riskLevels" :key="r.value" :label="r.label" :value="r.value" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-input v-model="searchKeyword" placeholder="Search by device, IP, or MAC..." :prefix-icon="Search" clearable />
        </el-col>
        <el-col :span="6">
          <div class="control-buttons">
            <el-button type="primary" @click="refreshIsolation" :loading="loading">
              <el-icon><Refresh /></el-icon> Refresh
            </el-button>
            <el-button @click="manuallyIsolate">
              <el-icon><Lock /></el-icon> Manual Isolate
            </el-button>
            <el-button @click="viewPolicies">
              <el-icon><Setting /></el-icon> Policies
            </el-button>
            <el-button @click="exportIsolationData">
              <el-icon><Download /></el-icon> Export
            </el-button>
          </div>
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
            <div class="stat-value">{{ isolationStats.total }}</div>
            <div class="stat-label">Total Events</div>
            <div class="stat-sub-value">{{ isolationStats.isolated }} Isolated | {{ isolationStats.monitoring }} Monitoring</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon traffic-icon">
            <el-icon><DataLine /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ isolationStats.totalTrafficBlocked.toFixed(1) }} MB</div>
            <div class="stat-label">Traffic Blocked</div>
            <el-progress :percentage="(isolationStats.isolated / isolationStats.total) * 100" :color="'#F56C6C'" :stroke-width="6" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon time-icon">
            <el-icon><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ isolationStats.avgIsolationTime }} min</div>
            <div class="stat-label">Avg Isolation Time</div>
            <div class="stat-sub-value">{{ isolationStats.released }} Released Devices</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon risk-icon">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ isolationStats.critical }}/{{ isolationStats.high }}</div>
            <div class="stat-label">Critical/High Risk</div>
            <div class="stat-sub-value">{{ isolationStats.medium }} Medium | {{ isolationStats.low }} Low</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Chart Section -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Isolation Status Distribution</span>
              <el-button text type="primary" @click="updateChart">Refresh</el-button>
            </div>
          </template>
          <div ref="chartRef" class="chart" style="height: 300px"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Isolation Timeline (24 Hours)</span>
              <el-button text type="primary" @click="initTimelineChart">Refresh</el-button>
            </div>
          </template>
          <div ref="timelineRef" class="timeline-chart" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Isolated Devices Table -->
    <el-card shadow="never" class="devices-card">
      <template #header>
        <div class="table-header">
          <span>Isolated & Monitored Devices</span>
          <div class="table-actions">
            <el-tag type="info" size="small">{{ filteredDevices.length }} devices found</el-tag>
          </div>
        </div>
      </template>

      <el-table :data="filteredDevices" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="device" label="Device" min-width="200" />
        <el-table-column prop="ip" label="IP Address" width="130" />
        <el-table-column label="Status" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ row.status.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Risk" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getRiskType(row.risk)" size="small">
              <el-icon style="margin-right: 4px"><component :is="getRiskIcon(row.risk)" /></el-icon>
              {{ row.risk.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="Reason" min-width="200" />
        <el-table-column prop="isolatedAt" label="Isolated At" width="160" />
        <el-table-column prop="duration" label="Duration" width="100" align="center" />
        <el-table-column label="Actions" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">
              Details
            </el-button>
            <el-button
                v-if="row.status === 'isolated'"
                link type="success"
                size="small"
                @click="openReleaseConfirm(row)"
            >
              Release
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

    <!-- Device Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="`Device Details - ${selectedDevice?.device}`" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Device ID">{{ selectedDevice?.id }}</el-descriptions-item>
        <el-descriptions-item label="Device Name">{{ selectedDevice?.device }}</el-descriptions-item>
        <el-descriptions-item label="IP Address">{{ selectedDevice?.ip }}</el-descriptions-item>
        <el-descriptions-item label="MAC Address">{{ selectedDevice?.mac }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusType(selectedDevice?.status)" size="small">
            {{ selectedDevice?.status?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Risk Level">
          <el-tag :type="getRiskType(selectedDevice?.risk)" size="small">
            {{ selectedDevice?.risk?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Isolated At">{{ selectedDevice?.isolatedAt || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="Isolated By">{{ selectedDevice?.isolatedBy || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="Duration">{{ selectedDevice?.duration || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="Auto-Release">{{ selectedDevice?.autoRelease || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="Traffic Blocked">{{ selectedDevice?.trafficBlocked || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="Alerts Count">{{ selectedDevice?.alertsCount || 0 }}</el-descriptions-item>
        <el-descriptions-item label="Reason" :span="2">{{ selectedDevice?.reason }}</el-descriptions-item>
        <el-descriptions-item label="Actions Taken" :span="2">
          <div class="actions-list">
            <el-tag v-for="action in selectedDevice?.actions" :key="action" size="small" style="margin: 2px">
              {{ action }}
            </el-tag>
          </div>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button v-if="selectedDevice?.status === 'isolated'" type="success" @click="openReleaseConfirm(selectedDevice)">
          Release Device
        </el-button>
        <el-button @click="detailsVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Release Confirmation Dialog -->
    <el-dialog v-model="releaseConfirmVisible" title="Release from Isolation" width="500px">
      <div class="release-warning">
        <el-alert
            title="Confirm Device Security"
            type="warning"
            show-icon
            :closable="false"
        >
          <template #default>
            <p>Device: <strong>{{ selectedDevice?.device }}</strong></p>
            <p>IP: {{ selectedDevice?.ip }} | MAC: {{ selectedDevice?.mac }}</p>
          </template>
        </el-alert>
      </div>

      <el-form :model="releaseForm" label-width="140px" style="margin-top: 20px">
        <el-form-item label="Release Reason" required>
          <el-input v-model="releaseForm.reason" type="textarea" rows="2" placeholder="Why is this device being released?" />
        </el-form-item>
        <el-form-item label="Permanent Whitelist">
          <el-switch v-model="releaseForm.permanentWhitelist" />
          <span class="whitelist-hint" v-if="releaseForm.permanentWhitelist">Add device to permanent whitelist</span>
        </el-form-item>
        <el-form-item label="Confirmation" required>
          <el-checkbox v-model="releaseForm.confirmSecurity">
            I confirm the device has been secured and is safe to release
          </el-checkbox>
        </el-form-item>
        <el-form-item label="Additional Notes">
          <el-input v-model="releaseForm.notes" type="textarea" rows="2" placeholder="Optional notes" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="releaseConfirmVisible = false">Cancel</el-button>
        <el-button type="primary" @click="executeRelease">Release Device</el-button>
      </template>
    </el-dialog>

    <!-- Isolation Policies Dialog -->
    <el-dialog v-model="policyVisible" title="Auto-Isolation Policies" width="800px">
      <el-table :data="isolationPolicies" stripe>
        <el-table-column prop="id" label="Policy ID" width="80" />
        <el-table-column prop="name" label="Policy Name" min-width="180" />
        <el-table-column prop="trigger" label="Trigger Condition" width="200" />
        <el-table-column prop="action" label="Action" width="140" />
        <el-table-column prop="duration" label="Duration" width="100" />
        <el-table-column label="Severity" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.severity === 'critical' ? 'danger' : row.severity === 'high' ? 'warning' : 'info'" size="small">
              {{ row.severity.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Enabled" width="80" align="center">
          <template #default="{ row }">
            <el-switch v-model="row.enabled" />
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button type="primary" @click="policyVisible = false">Close</el-button>
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
.auto-isolation-container {
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
  gap: 8px;
  justify-content: flex-end;
  flex-wrap: wrap;
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

.traffic-icon {
  background-color: #f0f9ff;
  color: #67c23a;
}

.time-icon {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.risk-icon {
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

.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  height: 370px;
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

.chart,
.timeline-chart {
  width: 100%;
}

.actions-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.release-warning {
  margin-bottom: 15px;
}

.whitelist-hint {
  margin-left: 10px;
  font-size: 12px;
  color: #909399;
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

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>