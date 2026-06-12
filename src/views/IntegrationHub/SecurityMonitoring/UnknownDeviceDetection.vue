<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Search, Refresh, Connection, Setting, DataLine,
  Document, CircleCheck, CircleClose, Loading,
  TrendCharts, Monitor, Aim, Clock, Timer,
  Warning, Upload, Download, Filter, Cpu, Link, Check, Close, QuestionFilled,
  Share, Expand, Fold, Tickets, Sunny,
  Finished, SuccessFilled, Clock as ClockIcon,
  Lock, Key, Cellphone, Share as ShareIcon
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing network scanner...',
  'Analyzing connected devices...',
  'Building device database...',
  'Detecting unknown devices...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedRisk = ref('all')
const selectedStatus = ref('all')
const detailsVisible = ref(false)
const blockConfirmVisible = ref(false)
const whitelistVisible = ref(false)
const chartRef = ref(null)
const networkMapRef = ref(null)

let riskChart: echarts.ECharts | null = null
let networkMapChart: echarts.ECharts | null = null

// Risk levels
const riskLevels = [
  { value: 'all', label: 'All Risks' },
  { value: 'critical', label: 'Critical' },
  { value: 'high', label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low', label: 'Low' }
]

// Status filters
const statusFilters = [
  { value: 'all', label: 'All Status' },
  { value: 'detected', label: 'Detected' },
  { value: 'investigating', label: 'Investigating' },
  { value: 'blocked', label: 'Blocked' },
  { value: 'whitelisted', label: 'Whitelisted' }
]

// Unknown devices data
const unknownDevices = ref([
  {
    id: 'UD001', mac: 'AA:BB:CC:DD:EE:01', ip: '192.168.1.245', hostname: 'unknown-device-01',
    firstSeen: '2024-01-15 08:23:45', lastSeen: '2024-01-15 10:23:45', risk: 'high',
    status: 'detected', manufacturer: 'Unknown', os: 'Unknown', ports: ['22', '80', '443'],
    traffic: 245.6, packets: 12450, confidence: 85, reason: 'New MAC address not in whitelist'
  },
  {
    id: 'UD002', mac: 'BB:CC:DD:EE:FF:02', ip: '192.168.1.198', hostname: 'raspberry-pi-7f3a',
    firstSeen: '2024-01-15 09:15:30', lastSeen: '2024-01-15 10:15:30', risk: 'medium',
    status: 'investigating', manufacturer: 'Raspberry Pi', os: 'Linux', ports: ['22', '8080'],
    traffic: 89.3, packets: 3420, confidence: 65, reason: 'Unrecognized device type'
  },
  {
    id: 'UD003', mac: 'CC:DD:EE:FF:00:03', ip: '192.168.1.156', hostname: 'ESP32-Device',
    firstSeen: '2024-01-14 14:20:00', lastSeen: '2024-01-15 10:20:00', risk: 'low',
    status: 'detected', manufacturer: 'Espressif', os: 'FreeRTOS', ports: ['80'],
    traffic: 12.5, packets: 890, confidence: 45, reason: 'IoT device pattern detected'
  },
  {
    id: 'UD004', mac: 'DD:EE:FF:00:11:04', ip: '192.168.1.234', hostname: 'HIKVISION-Camera',
    firstSeen: '2024-01-15 07:30:15', lastSeen: '2024-01-15 10:30:15', risk: 'critical',
    status: 'blocked', manufacturer: 'Hikvision', os: 'Embedded', ports: ['554', '8000', '8080'],
    traffic: 456.8, packets: 23450, confidence: 95, reason: 'Unauthorized camera access'
  },
  {
    id: 'UD005', mac: 'EE:FF:00:11:22:05', ip: '192.168.1.189', hostname: 'Unknown-Windows',
    firstSeen: '2024-01-15 08:45:22', lastSeen: '2024-01-15 09:45:22', risk: 'high',
    status: 'investigating', manufacturer: 'Unknown', os: 'Windows', ports: ['135', '445', '3389'],
    traffic: 678.2, packets: 34560, confidence: 90, reason: 'Suspicious port activity'
  },
  {
    id: 'UD006', mac: 'FF:00:11:22:33:06', ip: '192.168.1.167', hostname: 'Android-Device',
    firstSeen: '2024-01-15 10:00:00', lastSeen: '2024-01-15 10:00:00', risk: 'low',
    status: 'detected', manufacturer: 'Samsung', os: 'Android', ports: ['5353'],
    traffic: 5.2, packets: 340, confidence: 30, reason: 'Personal device detected'
  },
  {
    id: 'UD007', mac: '00:11:22:33:44:07', ip: '192.168.1.145', hostname: 'Unknown',
    firstSeen: '2024-01-14 22:30:00', lastSeen: '2024-01-15 05:30:00', risk: 'critical',
    status: 'blocked', manufacturer: 'Unknown', os: 'Unknown', ports: ['23', '2323'],
    traffic: 1234.5, packets: 67890, confidence: 98, reason: 'Potential telnet attack'
  },
  {
    id: 'UD008', mac: '11:22:33:44:55:08', ip: '192.168.1.212', hostname: 'ESP8266-Sensor',
    firstSeen: '2024-01-15 06:15:00', lastSeen: '2024-01-15 10:15:00', risk: 'low',
    status: 'whitelisted', manufacturer: 'Espressif', os: 'ESP8266', ports: ['80'],
    traffic: 8.9, packets: 678, confidence: 25, reason: 'Approved IoT sensor'
  }
])

// Risk distribution data
const riskDistribution = ref([
  { risk: 'Critical', count: 2, color: '#F56C6C' },
  { risk: 'High', count: 2, color: '#E6A23C' },
  { risk: 'Medium', count: 1, color: '#409EFF' },
  { risk: 'Low', count: 3, color: '#67C23A' }
])

// Detection statistics
const detectionStats = reactive({
  total: 0,
  critical: 0,
  high: 0,
  medium: 0,
  low: 0,
  blocked: 0,
  investigating: 0,
  whitelisted: 0,
  activeThreats: 0,
  avgConfidence: 0
})

// Whitelist form
const whitelistForm = reactive({
  mac: '',
  ip: '',
  hostname: '',
  reason: '',
  permanent: true
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: unknownDevices.value.length
})

// Filtered devices
const filteredDevices = computed(() => {
  let filtered = unknownDevices.value
  if (searchKeyword.value) {
    filtered = filtered.filter(d =>
        d.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        d.ip.includes(searchKeyword.value) ||
        d.mac.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        d.hostname.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedRisk.value !== 'all') {
    filtered = filtered.filter(d => d.risk === selectedRisk.value)
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
        initNetworkMap()
        updateStats()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  riskChart = echarts.init(chartRef.value)
  riskChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c})' },
    legend: { orient: 'vertical', left: 'left', data: riskDistribution.value.map(r => r.risk) },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: riskDistribution.value.map(r => ({ name: r.risk, value: r.count })),
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: {d}%' },
      itemStyle: {
        color: (params: any) => {
          const colors: Record<string, string> = {
            'Critical': '#F56C6C',
            'High': '#E6A23C',
            'Medium': '#409EFF',
            'Low': '#67C23A'
          }
          return colors[params.name] || '#909399'
        }
      }
    }]
  })
}

const initNetworkMap = () => {
  if (!networkMapRef.value) return

  // Simulate network topology data
  const nodes = unknownDevices.value.map((d, idx) => ({
    name: d.hostname,
    category: d.risk === 'critical' ? 0 : d.risk === 'high' ? 1 : d.risk === 'medium' ? 2 : 3,
    symbolSize: d.risk === 'critical' ? 40 : d.risk === 'high' ? 30 : 20,
    itemStyle: {
      color: d.risk === 'critical' ? '#F56C6C' : d.risk === 'high' ? '#E6A23C' : d.risk === 'medium' ? '#409EFF' : '#67C23A'
    }
  }))

  const categories = [
    { name: 'Critical Risk' },
    { name: 'High Risk' },
    { name: 'Medium Risk' },
    { name: 'Low Risk' }
  ]

  const links = []
  for (let i = 0; i < nodes.length - 1; i++) {
    if (Math.random() > 0.5) {
      links.push({ source: i, target: i + 1 })
    }
  }

  networkMapChart = echarts.init(networkMapRef.value)
  networkMapChart.setOption({
    tooltip: { formatter: (params: any) => `${params.name}<br/>Risk: ${categories[params.data.category]?.name || 'Unknown'}` },
    legend: { data: categories.map(c => c.name), bottom: 0 },
    series: [{
      type: 'graph',
      layout: 'force',
      data: nodes,
      links: links,
      categories: categories,
      roam: true,
      label: { show: true, position: 'right', formatter: '{b}' },
      force: { repulsion: 300, edgeLength: 150 },
      edgeSymbol: ['none', 'arrow'],
      edgeSymbolSize: [0, 10],
      lineStyle: { color: '#ccc', curveness: 0.3, width: 2 },
      emphasis: { focus: 'adjacency' }
    }]
  })
}

const updateStats = () => {
  detectionStats.total = unknownDevices.value.length
  detectionStats.critical = unknownDevices.value.filter(d => d.risk === 'critical').length
  detectionStats.high = unknownDevices.value.filter(d => d.risk === 'high').length
  detectionStats.medium = unknownDevices.value.filter(d => d.risk === 'medium').length
  detectionStats.low = unknownDevices.value.filter(d => d.risk === 'low').length
  detectionStats.blocked = unknownDevices.value.filter(d => d.status === 'blocked').length
  detectionStats.investigating = unknownDevices.value.filter(d => d.status === 'investigating').length
  detectionStats.whitelisted = unknownDevices.value.filter(d => d.status === 'whitelisted').length

  const activeThreats = unknownDevices.value.filter(d =>
      d.status !== 'blocked' && d.status !== 'whitelisted' && (d.risk === 'critical' || d.risk === 'high')
  ).length
  detectionStats.activeThreats = activeThreats

  const avgConf = unknownDevices.value.reduce((sum, d) => sum + d.confidence, 0) / unknownDevices.value.length
  detectionStats.avgConfidence = Math.round(avgConf)
}

const handleResize = () => {
  riskChart?.resize()
  networkMapChart?.resize()
}

// ==================== Security Functions ====================
const refreshDetection = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))
  updateStats()
  initNetworkMap()
  loading.value = false
  ElMessage.success('Device detection refreshed successfully')
}

const viewDetails = (device: any) => {
  selectedDevice.value = device
  detailsVisible.value = true
}

const blockDevice = async (device: any) => {
  await ElMessageBox.confirm(
      `Block device ${device.hostname} (${device.ip})? This will prevent all network access.`,
      'Confirm Block',
      {
        confirmButtonText: 'Block',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  )

  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))

  const index = unknownDevices.value.findIndex(d => d.id === device.id)
  if (index !== -1) {
    unknownDevices.value[index].status = 'blocked'
  }

  updateStats()
  initNetworkMap()
  loading.value = false
  ElMessage.success(`Device ${device.hostname} has been blocked`)
}

const openWhitelist = () => {
  whitelistForm.mac = ''
  whitelistForm.ip = ''
  whitelistForm.hostname = ''
  whitelistForm.reason = ''
  whitelistForm.permanent = true
  whitelistVisible.value = true
}

const addToWhitelist = async () => {
  if (!whitelistForm.mac && !whitelistForm.ip) {
    ElMessage.warning('Please provide MAC address or IP address')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1000))

  // Find and update device if exists
  const device = unknownDevices.value.find(d =>
      d.mac === whitelistForm.mac || d.ip === whitelistForm.ip
  )

  if (device) {
    const index = unknownDevices.value.findIndex(d => d.id === device.id)
    if (index !== -1) {
      unknownDevices.value[index].status = 'whitelisted'
      unknownDevices.value[index].risk = 'low'
    }
  } else {
    // Add new whitelisted device
    const newDevice = {
      id: `UD${String(unknownDevices.value.length + 1).padStart(3, '0')}`,
      mac: whitelistForm.mac || 'Unknown',
      ip: whitelistForm.ip || 'Unknown',
      hostname: whitelistForm.hostname || 'Whitelisted Device',
      firstSeen: new Date().toLocaleString(),
      lastSeen: new Date().toLocaleString(),
      risk: 'low',
      status: 'whitelisted',
      manufacturer: 'Approved',
      os: 'Unknown',
      ports: [],
      traffic: 0,
      packets: 0,
      confidence: 0,
      reason: whitelistForm.reason || 'Manually added to whitelist'
    }
    unknownDevices.value.push(newDevice)
  }

  updateStats()
  initNetworkMap()
  whitelistVisible.value = false
  ElMessage.success('Device added to whitelist successfully')
}

const startInvestigation = async (device: any) => {
  const index = unknownDevices.value.findIndex(d => d.id === device.id)
  if (index !== -1) {
    unknownDevices.value[index].status = 'investigating'
  }
  ElMessage.info(`Investigation started for ${device.hostname}`)
}

const exportDetectionData = () => {
  const data = unknownDevices.value.map(d => ({
    ID: d.id,
    MAC: d.mac,
    IP: d.ip,
    Hostname: d.hostname,
    FirstSeen: d.firstSeen,
    LastSeen: d.lastSeen,
    Risk: d.risk,
    Status: d.status,
    Manufacturer: d.manufacturer,
    OS: d.os,
    OpenPorts: d.ports.join(', '),
    Traffic: `${d.traffic} MB`,
    Packets: d.packets,
    Confidence: `${d.confidence}%`,
    Reason: d.reason
  }))

  const csv = convertToCSV(data)
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `unknown_devices_${new Date().toISOString()}.csv`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Detection data exported successfully')
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

const getRiskType = (risk: string) => {
  switch (risk) {
    case 'critical': return 'danger'
    case 'high': return 'warning'
    case 'medium': return 'primary'
    default: return 'success'
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

const getStatusType = (status: string) => {
  switch (status) {
    case 'detected': return 'warning'
    case 'investigating': return 'primary'
    case 'blocked': return 'danger'
    case 'whitelisted': return 'success'
    default: return 'info'
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
          <span class="loading-title">Loading Unknown Device Detection</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Security Monitoring - Unknown Device Detection</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="unknown-device-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h2>Unknown Device Detection</h2>
        <el-tag type="warning" effect="dark">Security Monitoring</el-tag>
      </div>
      <div class="header-stats">
        <el-tag type="danger" effect="plain">{{ detectionStats.activeThreats }} Active Threats</el-tag>
      </div>
    </div>

    <!-- Control Panel -->
    <el-card shadow="never" class="control-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="5">
          <el-select v-model="selectedRisk" placeholder="Risk Level" style="width: 100%">
            <el-option v-for="r in riskLevels" :key="r.value" :label="r.label" :value="r.value" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-select v-model="selectedStatus" placeholder="Status" clearable style="width: 100%">
            <el-option v-for="s in statusFilters" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-input v-model="searchKeyword" placeholder="Search by MAC, IP, or hostname..." :prefix-icon="Search" clearable />
        </el-col>
        <el-col :span="6">
          <div class="control-buttons">
            <el-button type="primary" @click="refreshDetection" :loading="loading">
              <el-icon><Refresh /></el-icon> Scan Network
            </el-button>
            <el-button @click="openWhitelist">
              <el-icon><Lock /></el-icon> Add to Whitelist
            </el-button>
            <el-button @click="exportDetectionData">
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
            <div class="stat-value">{{ detectionStats.total }}</div>
            <div class="stat-label">Unknown Devices</div>
            <div class="stat-sub-value">{{ detectionStats.avgConfidence }}% Avg Confidence</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon threat-icon">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ detectionStats.activeThreats }}</div>
            <div class="stat-label">Active Threats</div>
            <el-progress :percentage="(detectionStats.activeThreats / detectionStats.total) * 100" :color="'#F56C6C'" :stroke-width="6" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon blocked-icon">
            <el-icon><Lock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ detectionStats.blocked }}</div>
            <div class="stat-label">Blocked Devices</div>
            <div class="stat-sub-value">{{ detectionStats.whitelisted }} Whitelisted</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon risk-icon">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ detectionStats.critical }}/{{ detectionStats.high }}</div>
            <div class="stat-label">Critical/High Risk</div>
            <div class="stat-sub-value">{{ detectionStats.medium }} Medium | {{ detectionStats.low }} Low</div>
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
              <span>Risk Distribution</span>
              <el-button text type="primary" @click="initChart">Refresh</el-button>
            </div>
          </template>
          <div ref="chartRef" class="chart" style="height: 300px"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Network Topology - Unknown Devices</span>
              <el-button text type="primary" @click="initNetworkMap">Refresh Map</el-button>
            </div>
          </template>
          <div ref="networkMapRef" class="network-map" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Unknown Devices Table -->
    <el-card shadow="never" class="devices-card">
      <template #header>
        <div class="table-header">
          <span>Detected Unknown Devices</span>
          <div class="table-actions">
            <el-tag type="info" size="small">{{ filteredDevices.length }} devices found</el-tag>
          </div>
        </div>
      </template>

      <el-table :data="filteredDevices" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="mac" label="MAC Address" width="140" />
        <el-table-column prop="ip" label="IP Address" width="130" />
        <el-table-column prop="hostname" label="Hostname" min-width="150" />
        <el-table-column label="Risk" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getRiskType(row.risk)" size="small">
              <el-icon style="margin-right: 4px"><component :is="getRiskIcon(row.risk)" /></el-icon>
              {{ row.risk.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ row.status.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="manufacturer" label="Manufacturer" width="120" />
        <el-table-column prop="firstSeen" label="First Seen" width="160" />
        <el-table-column label="Confidence" width="100" align="center">
          <template #default="{ row }">
            <el-progress :percentage="row.confidence" :stroke-width="6" :show-text="false" />
            <span style="font-size: 12px">{{ row.confidence }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">
              Details
            </el-button>
            <el-button
                v-if="row.status !== 'blocked' && row.status !== 'whitelisted'"
                link type="danger"
                size="small"
                @click="blockDevice(row)"
            >
              Block
            </el-button>
            <el-button
                v-if="row.status === 'detected'"
                link type="warning"
                size="small"
                @click="startInvestigation(row)"
            >
              Investigate
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
    <el-dialog v-model="detailsVisible" :title="`Device Details - ${selectedDevice?.hostname}`" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Device ID">{{ selectedDevice?.id }}</el-descriptions-item>
        <el-descriptions-item label="MAC Address">{{ selectedDevice?.mac }}</el-descriptions-item>
        <el-descriptions-item label="IP Address">{{ selectedDevice?.ip }}</el-descriptions-item>
        <el-descriptions-item label="Hostname">{{ selectedDevice?.hostname }}</el-descriptions-item>
        <el-descriptions-item label="Manufacturer">{{ selectedDevice?.manufacturer }}</el-descriptions-item>
        <el-descriptions-item label="Operating System">{{ selectedDevice?.os }}</el-descriptions-item>
        <el-descriptions-item label="Risk Level">
          <el-tag :type="getRiskType(selectedDevice?.risk)" size="small">
            {{ selectedDevice?.risk?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusType(selectedDevice?.status)" size="small">
            {{ selectedDevice?.status?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="First Seen">{{ selectedDevice?.firstSeen }}</el-descriptions-item>
        <el-descriptions-item label="Last Seen">{{ selectedDevice?.lastSeen }}</el-descriptions-item>
        <el-descriptions-item label="Open Ports" :span="2">
          <div class="ports-list">
            <el-tag v-for="port in selectedDevice?.ports" :key="port" size="small" style="margin: 2px">
              Port {{ port }}
            </el-tag>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="Traffic">{{ selectedDevice?.traffic }} MB</el-descriptions-item>
        <el-descriptions-item label="Packets">{{ selectedDevice?.packets?.toLocaleString() }}</el-descriptions-item>
        <el-descriptions-item label="Detection Confidence">{{ selectedDevice?.confidence }}%</el-descriptions-item>
        <el-descriptions-item label="Detection Reason">{{ selectedDevice?.reason }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button v-if="selectedDevice?.status !== 'blocked'" type="danger" @click="blockDevice(selectedDevice)">
          Block Device
        </el-button>
        <el-button @click="detailsVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Whitelist Dialog -->
    <el-dialog v-model="whitelistVisible" title="Add to Whitelist" width="500px">
      <el-form :model="whitelistForm" label-width="100px">
        <el-form-item label="MAC Address">
          <el-input v-model="whitelistForm.mac" placeholder="AA:BB:CC:DD:EE:FF" />
        </el-form-item>
        <el-form-item label="IP Address">
          <el-input v-model="whitelistForm.ip" placeholder="192.168.1.100" />
        </el-form-item>
        <el-form-item label="Hostname">
          <el-input v-model="whitelistForm.hostname" placeholder="Device hostname" />
        </el-form-item>
        <el-form-item label="Reason">
          <el-input v-model="whitelistForm.reason" type="textarea" rows="2" placeholder="Why should this device be whitelisted?" />
        </el-form-item>
        <el-form-item label="Permanent">
          <el-switch v-model="whitelistForm.permanent" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="whitelistVisible = false">Cancel</el-button>
        <el-button type="primary" @click="addToWhitelist">Add to Whitelist</el-button>
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
.unknown-device-container {
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

.threat-icon {
  background-color: #fef0f0;
  color: #f56c6c;
}

.blocked-icon {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.risk-icon {
  background-color: #f0f9ff;
  color: #67c23a;
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
.network-map {
  width: 100%;
}

.ports-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
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