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
  Lock, Key, Cellphone
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing protocol analyzer...',
  'Loading attack signatures...',
  'Analyzing network traffic...',
  'Detecting anomalies...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedSeverity = ref('all')
const selectedProtocol = ref('all')
const detailsVisible = ref(false)
const mitigateVisible = ref(false)
const chartRef = ref(null)
const timelineRef = ref(null)

let attackChart: echarts.ECharts | null = null
let timelineChart: echarts.ECharts | null = null

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
  { value: 'snmp', label: 'SNMP' },
  { value: 'http', label: 'HTTP' }
]

// Attack events data
const attackEvents = ref([
  {
    id: 'ATK001', name: 'BACnet Broadcast Flood', protocol: 'bacnet', severity: 'critical',
    source: '192.168.1.105', target: '192.168.1.100', timestamp: '2024-01-15 10:23:45',
    status: 'active', description: 'Excessive BACnet broadcast messages detected',
    impact: 'Network congestion, device unresponsive', mitigation: 'Block source IP, rate limiting',
    signature: 'BACNET_BROADCAST_FLOOD', count: 12450, confidence: 95
  },
  {
    id: 'ATK002', name: 'Modbus Function Code Scan', protocol: 'modbus', severity: 'high',
    source: '192.168.2.50', target: '192.168.2.100', timestamp: '2024-01-15 10:15:30',
    status: 'mitigated', description: 'Scanner attempting to enumerate Modbus functions',
    impact: 'Potential device mapping', mitigation: 'Block scanning IP', signature: 'MODBUS_SCAN',
    count: 3450, confidence: 88
  },
  {
    id: 'ATK003', name: 'MQTT Malformed Packet', protocol: 'mqtt', severity: 'medium',
    source: '192.168.3.200', target: '192.168.3.100', timestamp: '2024-01-15 09:45:22',
    status: 'active', description: 'Malformed MQTT packets causing broker issues',
    impact: 'Broker performance degradation', mitigation: 'Validate packet structure',
    signature: 'MQTT_MALFORMED', count: 890, confidence: 72
  },
  {
    id: 'ATK004', name: 'OPC-UA Authentication Bypass', protocol: 'opcua', severity: 'critical',
    source: '192.168.4.75', target: '192.168.4.100', timestamp: '2024-01-15 08:30:15',
    status: 'mitigated', description: 'Attempt to bypass authentication mechanism',
    impact: 'Unauthorized access to OPC-UA server', mitigation: 'Enforce strong authentication',
    signature: 'OPCUA_AUTH_BYPASS', count: 256, confidence: 98
  },
  {
    id: 'ATK005', name: 'SNMP Community String Attack', protocol: 'snmp', severity: 'high',
    source: '192.168.5.120', target: '192.168.5.1', timestamp: '2024-01-15 07:55:10',
    status: 'active', description: 'Brute force attempt on SNMP community strings',
    impact: 'Potential device configuration access', mitigation: 'Change default community strings',
    signature: 'SNMP_COMMUNITY_BRUTE', count: 5670, confidence: 91
  },
  {
    id: 'ATK006', name: 'BACnet Write Property Attack', protocol: 'bacnet', severity: 'high',
    source: '192.168.1.200', target: '192.168.1.101', timestamp: '2024-01-15 06:20:33',
    status: 'mitigated', description: 'Unauthorized write property attempts',
    impact: 'Device configuration changes', mitigation: 'Restrict write access', signature: 'BACNET_WRITE_ATTACK',
    count: 1234, confidence: 85
  },
  {
    id: 'ATK007', name: 'Modbus Memory Read', protocol: 'modbus', severity: 'medium',
    source: '192.168.2.88', target: '192.168.2.101', timestamp: '2024-01-14 23:45:18',
    status: 'active', description: 'Reading from unauthorized memory addresses',
    impact: 'Information disclosure', mitigation: 'Address range validation', signature: 'MODBUS_MEMORY_READ',
    count: 2340, confidence: 68
  },
  {
    id: 'ATK008', name: 'MQTT Topic Subscription Flood', protocol: 'mqtt', severity: 'low',
    source: '192.168.3.150', target: '192.168.3.100', timestamp: '2024-01-14 22:10:05',
    status: 'resolved', description: 'Excessive topic subscription attempts',
    impact: 'Broker resource exhaustion', mitigation: 'Limit subscriptions per client',
    signature: 'MQTT_SUBSCRIBE_FLOOD', count: 567, confidence: 55
  }
])

// Attack statistics
const attackStats = reactive({
  total: 0,
  active: 0,
  mitigated: 0,
  resolved: 0,
  critical: 0,
  high: 0,
  medium: 0,
  low: 0,
  byProtocol: {} as Record<string, number>
})

// Timeline data
const timelineData = ref([
  { time: '00:00', count: 5, severity: 'low' },
  { time: '02:00', count: 3, severity: 'low' },
  { time: '04:00', count: 8, severity: 'medium' },
  { time: '06:00', count: 15, severity: 'high' },
  { time: '08:00', count: 25, severity: 'critical' },
  { time: '10:00', count: 18, severity: 'high' },
  { time: '12:00', count: 12, severity: 'medium' },
  { time: '14:00', count: 8, severity: 'medium' },
  { time: '16:00', count: 6, severity: 'low' },
  { time: '18:00', count: 4, severity: 'low' },
  { time: '20:00', count: 7, severity: 'medium' },
  { time: '22:00', count: 10, severity: 'high' }
])

// Mitigation form
const mitigationForm = reactive({
  action: 'block_ip',
  duration: 3600,
  notes: '',
  applyToAll: false
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: attackEvents.value.length
})

// Filtered attacks
const filteredAttacks = computed(() => {
  let filtered = attackEvents.value
  if (searchKeyword.value) {
    filtered = filtered.filter(a =>
        a.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        a.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        a.source.includes(searchKeyword.value) ||
        a.target.includes(searchKeyword.value)
    )
  }
  if (selectedSeverity.value !== 'all') {
    filtered = filtered.filter(a => a.severity === selectedSeverity.value)
  }
  if (selectedProtocol.value !== 'all') {
    filtered = filtered.filter(a => a.protocol === selectedProtocol.value)
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

  attackChart = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  const severityData = severityLevels.filter(s => s.value !== 'all').map(severity => {
    const attacks = attackEvents.value.filter(a => a.severity === severity.value)
    return { severity: severity.label, count: attacks.length }
  })

  attackChart?.setOption({
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

const initTimelineChart = () => {
  if (!timelineRef.value) return

  timelineChart = echarts.init(timelineRef.value)
  timelineChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['Attack Count', 'Severity'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: timelineData.value.map(t => t.time) },
    yAxis: [{ type: 'value', name: 'Attack Count' }, { type: 'category', name: 'Severity' }],
    series: [{
      name: 'Attack Count',
      type: 'line',
      data: timelineData.value.map(t => t.count),
      smooth: true,
      lineStyle: { color: '#F56C6C', width: 2 },
      areaStyle: { opacity: 0.1, color: '#F56C6C' },
      symbol: 'circle',
      symbolSize: 8,
      yAxisIndex: 0
    }]
  })
}

const updateStats = () => {
  attackStats.total = attackEvents.value.length
  attackStats.active = attackEvents.value.filter(a => a.status === 'active').length
  attackStats.mitigated = attackEvents.value.filter(a => a.status === 'mitigated').length
  attackStats.resolved = attackEvents.value.filter(a => a.status === 'resolved').length
  attackStats.critical = attackEvents.value.filter(a => a.severity === 'critical').length
  attackStats.high = attackEvents.value.filter(a => a.severity === 'high').length
  attackStats.medium = attackEvents.value.filter(a => a.severity === 'medium').length
  attackStats.low = attackEvents.value.filter(a => a.severity === 'low').length

  protocolFilters.forEach(protocol => {
    if (protocol.value !== 'all') {
      const count = attackEvents.value.filter(a => a.protocol === protocol.value).length
      attackStats.byProtocol[protocol.value] = count
    }
  })
}

const handleResize = () => {
  attackChart?.resize()
  timelineChart?.resize()
}

// ==================== Security Functions ====================
const refreshDetection = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))
  updateStats()
  updateChart()
  loading.value = false
  ElMessage.success('Attack detection refreshed successfully')
}

const viewDetails = (attack: any) => {
  selectedAttack.value = attack
  detailsVisible.value = true
}

const openMitigate = (attack: any) => {
  selectedAttack.value = attack
  mitigationForm.action = 'block_ip'
  mitigationForm.duration = 3600
  mitigationForm.notes = ''
  mitigationForm.applyToAll = false
  mitigateVisible.value = true
}

const executeMitigation = async () => {
  await ElMessageBox.confirm(
      `Apply mitigation for attack ${selectedAttack.value.name}?`,
      'Confirm Mitigation',
      {
        confirmButtonText: 'Apply',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  )

  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 2000))

  const index = attackEvents.value.findIndex(a => a.id === selectedAttack.value.id)
  if (index !== -1) {
    attackEvents.value[index].status = 'mitigated'
  }

  updateStats()
  updateChart()
  loading.value = false
  mitigateVisible.value = false
  ElMessage.success(`Mitigation applied successfully for ${selectedAttack.value.name}`)
}

const exportAttackData = () => {
  const data = attackEvents.value.map(a => ({
    ID: a.id,
    AttackName: a.name,
    Protocol: a.protocol.toUpperCase(),
    Severity: a.severity,
    Status: a.status,
    Source: a.source,
    Target: a.target,
    Timestamp: a.timestamp,
    Count: a.count,
    Confidence: `${a.confidence}%`,
    Description: a.description,
    Mitigation: a.mitigation
  }))

  const csv = convertToCSV(data)
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `protocol_attacks_${new Date().toISOString()}.csv`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Attack data exported successfully')
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
    case 'active': return 'danger'
    case 'mitigated': return 'success'
    case 'resolved': return 'info'
    default: return 'warning'
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

const selectedAttack = ref<any>(null)
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
          <span class="loading-title">Loading Protocol Attack Detection</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Security Monitoring - Protocol Attack Detection</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="attack-detection-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h2>Protocol Attack Detection</h2>
        <el-tag type="warning" effect="dark">Security Monitoring</el-tag>
      </div>
      <div class="header-stats">
        <el-tag type="danger" effect="plain">{{ attackStats.active }} Active Attacks</el-tag>
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
          <el-input v-model="searchKeyword" placeholder="Search by name, source, or target..." :prefix-icon="Search" clearable />
        </el-col>
        <el-col :span="6">
          <div class="control-buttons">
            <el-button type="primary" @click="refreshDetection" :loading="loading">
              <el-icon><Refresh /></el-icon> Scan Now
            </el-button>
            <el-button @click="exportAttackData">
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
            <el-icon><Cellphone /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ attackStats.total }}</div>
            <div class="stat-label">Total Attacks</div>
            <div class="stat-sub-value">{{ attackStats.active }} Active | {{ attackStats.mitigated }} Mitigated</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon critical-icon">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ attackStats.critical }}</div>
            <div class="stat-label">Critical Severity</div>
            <el-progress :percentage="(attackStats.critical / attackStats.total) * 100" :color="'#F56C6C'" :stroke-width="6" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon high-icon">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ attackStats.high }}</div>
            <div class="stat-label">High Severity</div>
            <div class="stat-sub-value">{{ attackStats.medium }} Medium | {{ attackStats.low }} Low</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon protocol-icon">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ Object.keys(attackStats.byProtocol).length }}</div>
            <div class="stat-label">Protocols Affected</div>
            <div class="stat-sub-value">BACnet: {{ attackStats.byProtocol.bacnet || 0 }} | Modbus: {{ attackStats.byProtocol.modbus || 0 }}</div>
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
              <span>Attack Severity Distribution</span>
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
              <span>Attack Timeline (24 Hours)</span>
              <el-button text type="primary" @click="initTimelineChart">Refresh</el-button>
            </div>
          </template>
          <div ref="timelineRef" class="timeline-chart" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Attacks Table -->
    <el-card shadow="never" class="attacks-card">
      <template #header>
        <div class="table-header">
          <span>Detected Protocol Attacks</span>
          <div class="table-actions">
            <el-tag type="info" size="small">{{ filteredAttacks.length }} events found</el-tag>
          </div>
        </div>
      </template>

      <el-table :data="filteredAttacks" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="Attack Name" min-width="200" />
        <el-table-column label="Protocol" width="100" align="center">
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
        <el-table-column prop="source" label="Source" width="130" />
        <el-table-column prop="target" label="Target" width="130" />
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
                v-if="row.status === 'active'"
                link type="warning"
                size="small"
                @click="openMitigate(row)"
            >
              Mitigate
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

    <!-- Attack Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="`Attack Details - ${selectedAttack?.name}`" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Attack ID">{{ selectedAttack?.id }}</el-descriptions-item>
        <el-descriptions-item label="Attack Name">{{ selectedAttack?.name }}</el-descriptions-item>
        <el-descriptions-item label="Protocol">{{ selectedAttack?.protocol?.toUpperCase() }}</el-descriptions-item>
        <el-descriptions-item label="Severity">
          <el-tag :type="getSeverityType(selectedAttack?.severity)" size="small">
            {{ selectedAttack?.severity?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusType(selectedAttack?.status)" size="small">
            {{ selectedAttack?.status?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Detection Confidence">{{ selectedAttack?.confidence }}%</el-descriptions-item>
        <el-descriptions-item label="Source IP">{{ selectedAttack?.source }}</el-descriptions-item>
        <el-descriptions-item label="Target IP">{{ selectedAttack?.target }}</el-descriptions-item>
        <el-descriptions-item label="Timestamp">{{ selectedAttack?.timestamp }}</el-descriptions-item>
        <el-descriptions-item label="Event Count">{{ selectedAttack?.count?.toLocaleString() }}</el-descriptions-item>
        <el-descriptions-item label="Signature">{{ selectedAttack?.signature }}</el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedAttack?.description }}</el-descriptions-item>
        <el-descriptions-item label="Impact" :span="2">{{ selectedAttack?.impact }}</el-descriptions-item>
        <el-descriptions-item label="Recommended Mitigation" :span="2">{{ selectedAttack?.mitigation }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button v-if="selectedAttack?.status === 'active'" type="warning" @click="openMitigate(selectedAttack)">
          Apply Mitigation
        </el-button>
        <el-button @click="detailsVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Mitigation Dialog -->
    <el-dialog v-model="mitigateVisible" title="Apply Mitigation" width="500px">
      <div class="mitigation-warning">
        <el-alert
            title="Active Attack Detected"
            type="warning"
            show-icon
            :closable="false"
        >
          <template #default>
            <p>Attack: <strong>{{ selectedAttack?.name }}</strong></p>
            <p>Source: {{ selectedAttack?.source }} → Target: {{ selectedAttack?.target }}</p>
          </template>
        </el-alert>
      </div>

      <el-form :model="mitigationForm" label-width="120px" style="margin-top: 20px">
        <el-form-item label="Mitigation Action">
          <el-select v-model="mitigationForm.action" style="width: 100%">
            <el-option label="Block Source IP" value="block_ip" />
            <el-option label="Rate Limit" value="rate_limit" />
            <el-option label="Drop Packets" value="drop_packets" />
            <el-option label="Alert Only" value="alert_only" />
          </el-select>
        </el-form-item>
        <el-form-item label="Duration" v-if="mitigationForm.action !== 'alert_only'">
          <el-select v-model="mitigationForm.duration" style="width: 100%">
            <el-option label="1 Hour" :value="3600" />
            <el-option label="6 Hours" :value="21600" />
            <el-option label="24 Hours" :value="86400" />
            <el-option label="Permanent" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item label="Apply to All">
          <el-switch v-model="mitigationForm.applyToAll" />
          <span class="apply-hint" v-if="mitigationForm.applyToAll">Apply to all similar attacks</span>
        </el-form-item>
        <el-form-item label="Notes">
          <el-input v-model="mitigationForm.notes" type="textarea" rows="2" placeholder="Additional notes" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="mitigateVisible = false">Cancel</el-button>
        <el-button type="danger" @click="executeMitigation">Apply Mitigation</el-button>
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
.attack-detection-container {
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

.protocol-icon {
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

.attacks-card {
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

.mitigation-warning {
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
}
</style>