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
  Lock, Key, Cellphone,
  Edit
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing command analyzer...',
  'Loading command baseline...',
  'Analyzing command patterns...',
  'Detecting anomalies...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedSeverity = ref('all')
const selectedProtocol = ref('all')
const detailsVisible = ref(false)
const blockConfirmVisible = ref(false)
const chartRef = ref(null)
const trendChartRef = ref(null)

let anomalyChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null

// Severity levels
const severityLevels = [
  { value: 'all', label: 'All Severities' },
  { value: 'critical', label: 'Critical' },
  { value: 'high', label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low', label: 'Low' }
]

// Protocol filters
const protocolFilters = [
  { value: 'all', label: 'All Protocols' },
  { value: 'bacnet', label: 'BACnet' },
  { value: 'modbus', label: 'Modbus' },
  { value: 'mqtt', label: 'MQTT' },
  { value: 'opcua', label: 'OPC-UA' },
  { value: 'snmp', label: 'SNMP' }
]

// Abnormal command events data
const abnormalCommands = ref([
  {
    id: 'AC001', command: 'WriteProperty - Setpoint=55°C', protocol: 'bacnet', severity: 'critical',
    device: 'AHU-1 Controller', source: '192.168.1.150', timestamp: '2024-01-15 10:23:45',
    status: 'blocked', description: 'Attempt to write temperature setpoint beyond safe range (55°C vs max 30°C)',
    normalRange: '18-26°C', attemptedValue: '55°C', impact: 'Equipment damage risk',
    action: 'Command blocked, source IP quarantined', confidence: 98
  },
  {
    id: 'AC002', command: 'Modbus Write - Coil 0xFF', protocol: 'modbus', severity: 'high',
    device: 'Power Meter - Main', source: '192.168.2.200', timestamp: '2024-01-15 10:15:30',
    status: 'blocked', description: 'Write to invalid coil address (255 vs max 100)',
    normalRange: '0-100', attemptedValue: '255', impact: 'Device configuration corruption',
    action: 'Command rejected, alert triggered', confidence: 92
  },
  {
    id: 'AC003', command: 'MQTT Publish - factory/reset', protocol: 'mqtt', severity: 'critical',
    device: 'Temperature Sensors Hub', source: '192.168.3.180', timestamp: '2024-01-15 09:45:22',
    status: 'investigating', description: 'Factory reset command to critical sensors',
    normalRange: 'config/update', attemptedValue: 'factory/reset', impact: 'Loss of sensor data',
    action: 'Command quarantined, investigating source', confidence: 95
  },
  {
    id: 'AC004', command: 'OPC-UA Write - Max Value Exceeded', protocol: 'opcua', severity: 'high',
    device: 'OPC-UA Gateway', source: '192.168.4.100', timestamp: '2024-01-15 08:30:15',
    status: 'blocked', description: 'Write value exceeds maximum allowed limit',
    normalRange: '0-1000', attemptedValue: '9999', impact: 'Data corruption possible',
    action: 'Command blocked, user notified', confidence: 88
  },
  {
    id: 'AC005', command: 'BACnet Device Restart', protocol: 'bacnet', severity: 'critical',
    device: 'Building A - BMS Controller', source: '192.168.1.50', timestamp: '2024-01-15 07:55:10',
    status: 'blocked', description: 'Unauthorized device restart command',
    normalRange: 'N/A', attemptedValue: 'Restart', impact: 'System downtime',
    action: 'Command blocked, immediate alert', confidence: 99
  },
  {
    id: 'AC006', command: 'Modbus Write Multiple Registers', protocol: 'modbus', severity: 'medium',
    device: 'VFD Pump Controller', source: '192.168.2.75', timestamp: '2024-01-15 06:20:33',
    status: 'investigating', description: 'Bulk write to 50 registers at once (unusual pattern)',
    normalRange: '1-10 registers', attemptedValue: '50 registers', impact: 'Potential DoS',
    action: 'Rate limiting applied', confidence: 75
  },
  {
    id: 'AC007', command: 'SNMP Set - Private OID', protocol: 'snmp', severity: 'high',
    device: 'Network Switch - Core', source: '192.168.5.33', timestamp: '2024-01-14 23:45:18',
    status: 'blocked', description: 'Write to restricted private OID',
    normalRange: 'Public OIDs only', attemptedValue: '1.3.6.1.4.1.9.9.999', impact: 'Security breach',
    action: 'SNMP write disabled, IP blocked', confidence: 96
  },
  {
    id: 'AC008', command: 'MQTT Large Payload', protocol: 'mqtt', severity: 'low',
    device: 'IoT Gateway', source: '192.168.3.250', timestamp: '2024-01-14 22:10:05',
    status: 'resolved', description: 'Command payload exceeds normal size',
    normalRange: '< 1KB', attemptedValue: '15KB', impact: 'Network congestion',
    action: 'Payload truncated, warning issued', confidence: 65
  }
])

// Command statistics
const cmdStats = reactive({
  total: 0,
  blocked: 0,
  investigating: 0,
  resolved: 0,
  critical: 0,
  high: 0,
  medium: 0,
  low: 0,
  byProtocol: {} as Record<string, number>,
  topDevices: [] as Array<{name: string, count: number}>
})

// Command baseline data for chart
const baselineData = ref([
  { hour: '00:00', normal: 45, abnormal: 2 },
  { hour: '02:00', normal: 38, abnormal: 1 },
  { hour: '04:00', normal: 32, abnormal: 3 },
  { hour: '06:00', normal: 56, abnormal: 5 },
  { hour: '08:00', normal: 245, abnormal: 12 },
  { hour: '10:00', normal: 320, abnormal: 8 },
  { hour: '12:00', normal: 280, abnormal: 6 },
  { hour: '14:00', normal: 265, abnormal: 4 },
  { hour: '16:00', normal: 290, abnormal: 7 },
  { hour: '18:00', normal: 210, abnormal: 3 },
  { hour: '20:00', normal: 98, abnormal: 2 },
  { hour: '22:00', normal: 52, abnormal: 1 }
])

// Block form
const blockForm = reactive({
  action: 'block_source',
  duration: 3600,
  reason: '',
  applyPattern: false
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: abnormalCommands.value.length
})

// Filtered commands
const filteredCommands = computed(() => {
  let filtered = abnormalCommands.value
  if (searchKeyword.value) {
    filtered = filtered.filter(c =>
        c.command.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        c.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        c.device.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        c.source.includes(searchKeyword.value)
    )
  }
  if (selectedSeverity.value !== 'all') {
    filtered = filtered.filter(c => c.severity === selectedSeverity.value)
  }
  if (selectedProtocol.value !== 'all') {
    filtered = filtered.filter(c => c.protocol === selectedProtocol.value)
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

  anomalyChart = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  const severityData = severityLevels.filter(s => s.value !== 'all').map(severity => {
    const commands = abnormalCommands.value.filter(c => c.severity === severity.value)
    return { severity: severity.label, count: commands.length }
  })

  anomalyChart?.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c})' },
    legend: { orient: 'vertical', left: 'left', data: severityData.map(s => s.severity) },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: severityData.map(s => ({ name: s.severity, value: s.count })),
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

const initTrendChart = () => {
  if (!trendChartRef.value) return

  trendChart = echarts.init(trendChartRef.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Normal Commands', 'Abnormal Commands'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: baselineData.value.map(d => d.hour) },
    yAxis: { type: 'value', name: 'Command Count' },
    series: [
      { name: 'Normal Commands', type: 'bar', data: baselineData.value.map(d => d.normal), stack: 'total', itemStyle: { color: '#67C23A', borderRadius: [4, 4, 0, 0] } },
      { name: 'Abnormal Commands', type: 'bar', data: baselineData.value.map(d => d.abnormal), stack: 'total', itemStyle: { color: '#F56C6C', borderRadius: [4, 4, 0, 0] } }
    ]
  })
}

const updateStats = () => {
  cmdStats.total = abnormalCommands.value.length
  cmdStats.blocked = abnormalCommands.value.filter(c => c.status === 'blocked').length
  cmdStats.investigating = abnormalCommands.value.filter(c => c.status === 'investigating').length
  cmdStats.resolved = abnormalCommands.value.filter(c => c.status === 'resolved').length
  cmdStats.critical = abnormalCommands.value.filter(c => c.severity === 'critical').length
  cmdStats.high = abnormalCommands.value.filter(c => c.severity === 'high').length
  cmdStats.medium = abnormalCommands.value.filter(c => c.severity === 'medium').length
  cmdStats.low = abnormalCommands.value.filter(c => c.severity === 'low').length

  protocolFilters.forEach(protocol => {
    if (protocol.value !== 'all') {
      const count = abnormalCommands.value.filter(c => c.protocol === protocol.value).length
      cmdStats.byProtocol[protocol.value] = count
    }
  })

  // Calculate top affected devices
  const deviceMap = new Map<string, number>()
  abnormalCommands.value.forEach(c => {
    deviceMap.set(c.device, (deviceMap.get(c.device) || 0) + 1)
  })
  cmdStats.topDevices = Array.from(deviceMap.entries())
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5)
}

const handleResize = () => {
  anomalyChart?.resize()
  trendChart?.resize()
}

// ==================== Command Security Functions ====================
const refreshDetection = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))
  updateStats()
  updateChart()
  loading.value = false
  ElMessage.success('Command detection refreshed successfully')
}

const viewDetails = (command: any) => {
  selectedCommand.value = command
  detailsVisible.value = true
}

const openBlockConfirm = (command: any) => {
  selectedCommand.value = command
  blockForm.action = 'block_source'
  blockForm.duration = 3600
  blockForm.reason = ''
  blockForm.applyPattern = false
  blockConfirmVisible.value = true
}

const executeBlock = async () => {
  await ElMessageBox.confirm(
      `Block ${selectedCommand.value.command} from ${selectedCommand.value.source}?`,
      'Confirm Block',
      {
        confirmButtonText: 'Block',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  )

  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))

  const index = abnormalCommands.value.findIndex(c => c.id === selectedCommand.value.id)
  if (index !== -1) {
    abnormalCommands.value[index].status = 'blocked'
  }

  updateStats()
  updateChart()
  loading.value = false
  blockConfirmVisible.value = false
  ElMessage.success(`Command pattern blocked successfully`)
}

const whitelistCommand = async (command: any) => {
  await ElMessageBox.confirm(
      `Add ${command.command} to whitelist?`,
      'Confirm Whitelist',
      {
        confirmButtonText: 'Add to Whitelist',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  )

  const index = abnormalCommands.value.findIndex(c => c.id === command.id)
  if (index !== -1) {
    abnormalCommands.value[index].status = 'resolved'
  }

  updateStats()
  ElMessage.success(`Command added to whitelist`)
}

const exportCommandData = () => {
  const data = abnormalCommands.value.map(c => ({
    ID: c.id,
    Command: c.command,
    Protocol: c.protocol.toUpperCase(),
    Severity: c.severity,
    Status: c.status,
    Device: c.device,
    Source: c.source,
    Timestamp: c.timestamp,
    NormalRange: c.normalRange,
    AttemptedValue: c.attemptedValue,
    Impact: c.impact,
    Confidence: `${c.confidence}%`
  }))

  const csv = convertToCSV(data)
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `abnormal_commands_${new Date().toISOString()}.csv`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Command data exported successfully')
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

const getSeverityType = (severity: string) => {
  switch (severity) {
    case 'critical': return 'danger'
    case 'high': return 'warning'
    case 'medium': return 'primary'
    default: return 'info'
  }
}

const getSeverityIcon = (severity: string) => {
  switch (severity) {
    case 'critical': return Warning
    case 'high': return Warning
    case 'medium': return QuestionFilled
    default: return SuccessFilled
  }
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'blocked': return 'danger'
    case 'investigating': return 'warning'
    case 'resolved': return 'success'
    default: return 'info'
  }
}

const getProtocolTagType = (protocol: string) => {
  switch (protocol) {
    case 'bacnet': return 'primary'
    case 'modbus': return 'success'
    case 'mqtt': return 'warning'
    case 'opcua': return 'info'
    default: return ''
  }
}

const selectedCommand = ref<any>(null)
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
          <span class="loading-title">Loading Abnormal Command Detection</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Security Monitoring - Abnormal Command Detection</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="abnormal-command-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h2>Abnormal Command Detection</h2>
        <el-tag type="warning" effect="dark">Security Monitoring</el-tag>
      </div>
      <div class="header-stats">
        <el-tag type="danger" effect="plain">{{ cmdStats.investigating }} Under Investigation</el-tag>
      </div>
    </div>

    <!-- Control Panel -->
    <el-card shadow="never" class="control-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="5">
          <el-select v-model="selectedSeverity" placeholder="Severity" style="width: 100%" @change="updateChart">
            <el-option v-for="s in severityLevels" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-select v-model="selectedProtocol" placeholder="Protocol" clearable style="width: 100%">
            <el-option v-for="p in protocolFilters" :key="p.value" :label="p.label" :value="p.value" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-input v-model="searchKeyword" placeholder="Search by command, device, or source..." :prefix-icon="Search" clearable />
        </el-col>
        <el-col :span="6">
          <div class="control-buttons">
            <el-button type="primary" @click="refreshDetection" :loading="loading">
              <el-icon><Refresh /></el-icon> Analyze Now
            </el-button>
            <el-button @click="exportCommandData">
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
            <el-icon><Edit /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ cmdStats.total }}</div>
            <div class="stat-label">Total Anomalies</div>
            <div class="stat-sub-value">{{ cmdStats.blocked }} Blocked | {{ cmdStats.resolved }} Resolved</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon critical-icon">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ cmdStats.critical }}</div>
            <div class="stat-label">Critical</div>
            <el-progress :percentage="(cmdStats.critical / cmdStats.total) * 100" :color="'#F56C6C'" :stroke-width="6" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon high-icon">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ cmdStats.high }}</div>
            <div class="stat-label">High Severity</div>
            <div class="stat-sub-value">{{ cmdStats.medium }} Medium | {{ cmdStats.low }} Low</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon device-icon">
            <el-icon><Monitor /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ cmdStats.topDevices.length }}</div>
            <div class="stat-label">Affected Devices</div>
            <div class="stat-sub-value">Top: {{ cmdStats.topDevices[0]?.name || 'N/A' }}</div>
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
              <span>Anomaly Severity Distribution</span>
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
              <span>Command Baseline vs Anomalies (24 Hours)</span>
              <el-button text type="primary" @click="initTrendChart">Refresh</el-button>
            </div>
          </template>
          <div ref="trendChartRef" class="trend-chart" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Top Affected Devices -->
    <el-row :gutter="20" class="top-devices-row">
      <el-col :span="24">
        <el-card shadow="never" class="top-devices-card">
          <template #header>
            <div class="card-header">
              <span>Top Affected Devices</span>
              <el-tag type="info" size="small">Based on anomaly count</el-tag>
            </div>
          </template>
          <div class="device-list">
            <div v-for="device in cmdStats.topDevices" :key="device.name" class="device-item">
              <span class="device-name">{{ device.name }}</span>
              <el-progress :percentage="(device.count / cmdStats.total) * 100" :stroke-width="8" />
              <span class="device-count">{{ device.count }} anomalies</span>
            </div>
            <div v-if="cmdStats.topDevices.length === 0" class="no-data">No data available</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Abnormal Commands Table -->
    <el-card shadow="never" class="commands-card">
      <template #header>
        <div class="table-header">
          <span>Detected Abnormal Commands</span>
          <div class="table-actions">
            <el-tag type="info" size="small">{{ filteredCommands.length }} events found</el-tag>
          </div>
        </div>
      </template>

      <el-table :data="filteredCommands" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="command" label="Command" min-width="250" />
        <el-table-column label="Protocol" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="getProtocolTagType(row.protocol)" size="small">
              {{ row.protocol.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Severity" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getSeverityType(row.severity)" size="small">
              <el-icon style="margin-right: 4px"><component :is="getSeverityIcon(row.severity)" /></el-icon>
              {{ row.severity.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ row.status.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="device" label="Device" width="160" />
        <el-table-column prop="source" label="Source" width="130" />
        <el-table-column prop="timestamp" label="Timestamp" width="160" />
        <el-table-column label="Confidence" width="100" align="center">
          <template #default="{ row }">
            <el-progress :percentage="row.confidence" :stroke-width="6" :show-text="false" />
            <span style="font-size: 12px">{{ row.confidence }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">
              Details
            </el-button>
            <el-button
                v-if="row.status === 'investigating'"
                link type="danger"
                size="small"
                @click="openBlockConfirm(row)"
            >
              Block
            </el-button>
            <el-button
                v-if="row.status === 'investigating'"
                link type="success"
                size="small"
                @click="whitelistCommand(row)"
            >
              Whitelist
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

    <!-- Command Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="`Command Details - ${selectedCommand?.id}`" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Command">{{ selectedCommand?.command }}</el-descriptions-item>
        <el-descriptions-item label="Protocol">{{ selectedCommand?.protocol?.toUpperCase() }}</el-descriptions-item>
        <el-descriptions-item label="Severity">
          <el-tag :type="getSeverityType(selectedCommand?.severity)" size="small">
            {{ selectedCommand?.severity?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusType(selectedCommand?.status)" size="small">
            {{ selectedCommand?.status?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Device">{{ selectedCommand?.device }}</el-descriptions-item>
        <el-descriptions-item label="Source IP">{{ selectedCommand?.source }}</el-descriptions-item>
        <el-descriptions-item label="Timestamp">{{ selectedCommand?.timestamp }}</el-descriptions-item>
        <el-descriptions-item label="Detection Confidence">{{ selectedCommand?.confidence }}%</el-descriptions-item>
        <el-descriptions-item label="Normal Range">{{ selectedCommand?.normalRange }}</el-descriptions-item>
        <el-descriptions-item label="Attempted Value">{{ selectedCommand?.attemptedValue }}</el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedCommand?.description }}</el-descriptions-item>
        <el-descriptions-item label="Impact" :span="2">{{ selectedCommand?.impact }}</el-descriptions-item>
        <el-descriptions-item label="Action Taken" :span="2">{{ selectedCommand?.action }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button v-if="selectedCommand?.status === 'investigating'" type="danger" @click="openBlockConfirm(selectedCommand)">
          Block Command
        </el-button>
        <el-button v-if="selectedCommand?.status === 'investigating'" type="success" @click="whitelistCommand(selectedCommand)">
          Add to Whitelist
        </el-button>
        <el-button @click="detailsVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Block Confirmation Dialog -->
    <el-dialog v-model="blockConfirmVisible" title="Block Command Pattern" width="500px">
      <div class="block-warning">
        <el-alert
            title="Block Command Pattern"
            type="warning"
            show-icon
            :closable="false"
        >
          <template #default>
            <p>Command: <strong>{{ selectedCommand?.command }}</strong></p>
            <p>Source: {{ selectedCommand?.source }} → Device: {{ selectedCommand?.device }}</p>
          </template>
        </el-alert>
      </div>

      <el-form :model="blockForm" label-width="120px" style="margin-top: 20px">
        <el-form-item label="Action">
          <el-select v-model="blockForm.action" style="width: 100%">
            <el-option label="Block Source IP" value="block_source" />
            <el-option label="Block Command Pattern" value="block_pattern" />
            <el-option label="Rate Limit Source" value="rate_limit" />
          </el-select>
        </el-form-item>
        <el-form-item label="Duration">
          <el-select v-model="blockForm.duration" style="width: 100%">
            <el-option label="1 Hour" :value="3600" />
            <el-option label="6 Hours" :value="21600" />
            <el-option label="24 Hours" :value="86400" />
            <el-option label="Permanent" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item label="Apply to Similar">
          <el-switch v-model="blockForm.applyPattern" />
          <span class="apply-hint" v-if="blockForm.applyPattern">Apply to all similar command patterns</span>
        </el-form-item>
        <el-form-item label="Reason">
          <el-input v-model="blockForm.reason" type="textarea" rows="2" placeholder="Reason for blocking" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="blockConfirmVisible = false">Cancel</el-button>
        <el-button type="danger" @click="executeBlock">Execute Block</el-button>
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
.abnormal-command-container {
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

.critical-icon {
  background-color: #fef0f0;
  color: #f56c6c;
}

.high-icon {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.device-icon {
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

.top-devices-row {
  margin-bottom: 20px;
}

.top-devices-card {
  height: auto;
}

.device-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.device-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.device-name {
  width: 200px;
  font-weight: 500;
  color: #303133;
}

.device-count {
  width: 120px;
  font-size: 13px;
  color: #909399;
}

.no-data {
  text-align: center;
  color: #909399;
  padding: 20px;
}

.commands-card {
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
.trend-chart {
  width: 100%;
}

.block-warning {
  margin-bottom: 15px;
}

.apply-hint {
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

  .device-item {
    flex-wrap: wrap;
  }

  .device-name {
    width: 100%;
  }
}
</style>