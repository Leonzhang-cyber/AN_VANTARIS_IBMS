<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Search, Refresh, Connection, Setting, DataLine,
  Document, CircleCheck, CircleClose, Loading,
  TrendCharts, Monitor, Aim, Clock, Timer,
  Warning, Upload, Download, Filter, Cpu, Link, Check, Close, QuestionFilled,
  Share, Expand, Fold, Tickets, Sunny, Finished, SuccessFilled, Clock as ClockIcon
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing rollback center...',
  'Loading version history...',
  'Analyzing rollback points...',
  'Checking compatibility...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedStatus = ref('all')
const selectedType = ref('all')
const detailsVisible = ref(false)
const rollbackConfirmVisible = ref(false)
const compareVisible = ref(false)
const chartRef = ref(null)
const timelineRef = ref(null)

let statusChart: echarts.ECharts | null = null
let timelineChart: echarts.ECharts | null = null

// Rollback types
const rollbackTypes = [
  { value: 'all', label: 'All Types' },
  { value: 'firmware', label: 'Firmware' },
  { value: 'driver', label: 'Driver' },
  { value: 'protocol', label: 'Protocol' },
  { value: 'configuration', label: 'Configuration' }
]

// Status filters
const statusFilters = [
  { value: 'all', label: 'All Status' },
  { value: 'available', label: 'Available' },
  { value: 'executed', label: 'Executed' },
  { value: 'failed', label: 'Failed' },
  { value: 'partial', label: 'Partial' }
]

// Rollback history data
const rollbackHistory = ref([
  {
    id: 'RB001', name: 'BACnet Controller Firmware', type: 'firmware', device: 'Building A - BMS Controller',
    fromVersion: '4.3.0', toVersion: '4.2.0', status: 'success', date: '2024-01-20',
    reason: 'Compatibility issues with legacy devices', duration: '8 min', performedBy: 'admin@system.com',
    rollbackPoint: 'RBPT001', preCheck: 'passed', postCheck: 'passed'
  },
  {
    id: 'RB002', name: 'Modbus TCP Driver', type: 'driver', device: 'Power Meter - Main',
    fromVersion: '2.2.0', toVersion: '2.1.0', status: 'success', date: '2024-01-18',
    reason: 'Performance degradation', duration: '3 min', performedBy: 'admin@system.com',
    rollbackPoint: 'RBPT002', preCheck: 'passed', postCheck: 'passed'
  },
  {
    id: 'RB003', name: 'OPC-UA Server', type: 'protocol', device: 'OPC-UA Gateway',
    fromVersion: '1.5.0', toVersion: '1.4.0', status: 'partial', date: '2024-01-15',
    reason: 'Connection instability', duration: '25 min', performedBy: 'engineer@system.com',
    rollbackPoint: 'RBPT003', preCheck: 'warning', postCheck: 'partial'
  },
  {
    id: 'RB004', name: 'MQTT Client', type: 'driver', device: 'Temperature Sensors Hub',
    fromVersion: '5.2.0', toVersion: '5.1.0', status: 'success', date: '2024-01-22',
    reason: 'Data loss issues', duration: '2 min', performedBy: 'admin@system.com',
    rollbackPoint: 'RBPT004', preCheck: 'passed', postCheck: 'passed'
  },
  {
    id: 'RB005', name: 'KNX/IP Gateway', type: 'firmware', device: 'KNX Router',
    fromVersion: '2.0.0', toVersion: '1.9.0', status: 'failed', date: '2024-01-25',
    reason: 'Communication errors', duration: 'N/A', performedBy: 'system@system.com',
    rollbackPoint: 'RBPT005', preCheck: 'passed', postCheck: 'failed'
  },
  {
    id: 'RB006', name: 'Lighting Controller', type: 'firmware', device: 'Lighting Panel - L1',
    fromVersion: '4.6.0', toVersion: '4.5.0', status: 'available', date: null,
    reason: 'Ready for rollback', duration: null, performedBy: null,
    rollbackPoint: 'RBPT006', preCheck: 'pending', postCheck: null
  },
  {
    id: 'RB007', name: 'BACnet Router', type: 'firmware', device: 'BACnet Router',
    fromVersion: '4.0.0', toVersion: '3.8.0', status: 'available', date: null,
    reason: 'Ready for rollback', duration: null, performedBy: null,
    rollbackPoint: 'RBPT007', preCheck: 'pending', postCheck: null
  },
  {
    id: 'RB008', name: 'SNMP Agent', type: 'protocol', device: 'Network Switch',
    fromVersion: '3.1.0', toVersion: '3.0.0', status: 'available', date: null,
    reason: 'Ready for rollback', duration: null, performedBy: null,
    rollbackPoint: 'RBPT008', preCheck: 'pending', postCheck: null
  }
])

// Rollback points
const rollbackPoints = ref([
  { id: 'RBPT001', name: 'Before BACnet Upgrade', timestamp: '2024-01-19 22:00:00', type: 'firmware', device: 'BMS Controller', status: 'verified' },
  { id: 'RBPT002', name: 'Before Modbus Driver Update', timestamp: '2024-01-17 23:30:00', type: 'driver', device: 'Power Meter', status: 'verified' },
  { id: 'RBPT003', name: 'OPC-UA Stable State', timestamp: '2024-01-14 20:00:00', type: 'protocol', device: 'Gateway', status: 'partial' },
  { id: 'RBPT004', name: 'MQTT Working Configuration', timestamp: '2024-01-21 18:45:00', type: 'driver', device: 'Sensors Hub', status: 'verified' },
  { id: 'RBPT005', name: 'KNX Stable Version', timestamp: '2024-01-24 15:30:00', type: 'firmware', device: 'KNX Router', status: 'corrupt' },
  { id: 'RBPT006', name: 'Lighting Controller Backup', timestamp: '2024-01-30 14:00:00', type: 'firmware', device: 'Lighting Panel', status: 'verified' }
])

// Rollback statistics
const rollbackStats = reactive({
  total: 0,
  available: 0,
  executed: 0,
  failed: 0,
  partial: 0,
  successRate: 0,
  avgRollbackTime: 0,
  totalRollbacks: 0
})

// Selected rollback for details/confirm
const selectedRollback = ref<any>(null)
const compareRollbacks = ref<any[]>([])

// Rollback form
const rollbackForm = reactive({
  reason: '',
  confirmCheck: false,
  backupBefore: true,
  notifyUsers: true
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: rollbackHistory.value.length
})

// Filtered rollbacks
const filteredRollbacks = computed(() => {
  let filtered = rollbackHistory.value
  if (searchKeyword.value) {
    filtered = filtered.filter(r =>
        r.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        r.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        r.device.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        r.type.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(r => r.status === selectedStatus.value)
  }
  if (selectedType.value !== 'all') {
    filtered = filtered.filter(r => r.type === selectedType.value)
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

  statusChart = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  const statusData = statusFilters.filter(s => s.value !== 'all').map(status => {
    const entries = rollbackHistory.value.filter(r => r.status === status.value)
    return { status: status.label, count: entries.length }
  })

  statusChart?.setOption({
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
            'Available': '#67C23A',
            'Executed': '#409EFF',
            'Failed': '#F56C6C',
            'Partial': '#E6A23C'
          }
          return colors[params.name] || '#909399'
        }
      }
    }]
  })
}

const initTimelineChart = () => {
  if (!timelineRef.value) return

  const timelineData = rollbackPoints.value.map(point => ({
    name: point.name,
    date: point.timestamp,
    status: point.status
  }))

  const statusColors: Record<string, string> = {
    'verified': '#67C23A',
    'partial': '#E6A23C',
    'corrupt': '#F56C6C'
  }

  timelineChart = echarts.init(timelineRef.value)
  timelineChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: timelineData.map(t => t.name), axisLabel: { rotate: 30, interval: 0 } },
    yAxis: { type: 'value', name: 'Status' },
    series: [{
      type: 'bar',
      data: timelineData.map(t => t.status === 'verified' ? 3 : t.status === 'partial' ? 2 : 1),
      itemStyle: {
        color: (params: any) => statusColors[timelineData[params.dataIndex].status] || '#909399',
        borderRadius: [4, 4, 0, 0]
      },
      label: {
        show: true,
        position: 'top',
        formatter: (params: any) => timelineData[params.dataIndex].status.toUpperCase(),
        color: (params: any) => statusColors[timelineData[params.dataIndex].status] || '#909399'
      }
    }]
  })
}

const updateStats = () => {
  rollbackStats.total = rollbackHistory.value.length
  rollbackStats.available = rollbackHistory.value.filter(r => r.status === 'available').length
  rollbackStats.executed = rollbackHistory.value.filter(r => r.status === 'success').length
  rollbackStats.failed = rollbackHistory.value.filter(r => r.status === 'failed').length
  rollbackStats.partial = rollbackHistory.value.filter(r => r.status === 'partial').length

  const executedRollbacks = rollbackHistory.value.filter(r => r.status === 'success')
  rollbackStats.successRate = executedRollbacks.length > 0
      ? Math.round((executedRollbacks.length / (executedRollbacks.length + rollbackStats.failed)) * 100)
      : 0

  const rollbackTimes = executedRollbacks.map(r => {
    const time = r.duration?.match(/\d+/)
    return time ? parseInt(time[0]) : 0
  }).filter(t => t > 0)

  rollbackStats.avgRollbackTime = rollbackTimes.length > 0
      ? Math.round(rollbackTimes.reduce((a, b) => a + b, 0) / rollbackTimes.length)
      : 0
  rollbackStats.totalRollbacks = executedRollbacks.length
}

const handleResize = () => {
  statusChart?.resize()
  timelineChart?.resize()
}

// ==================== Rollback Functions ====================
const refreshRollbacks = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))
  updateStats()
  updateChart()
  loading.value = false
  ElMessage.success('Rollback center refreshed successfully')
}

const viewDetails = (rollback: any) => {
  selectedRollback.value = rollback
  detailsVisible.value = true
}

const openRollbackConfirm = (rollback: any) => {
  selectedRollback.value = rollback
  rollbackForm.reason = ''
  rollbackForm.confirmCheck = false
  rollbackForm.backupBefore = true
  rollbackForm.notifyUsers = true
  rollbackConfirmVisible.value = true
}

const executeRollback = async () => {
  if (!rollbackForm.reason) {
    ElMessage.warning('Please provide a reason for rollback')
    return
  }
  if (!rollbackForm.confirmCheck) {
    ElMessage.warning('Please confirm that you understand the risks')
    return
  }

  await ElMessageBox.confirm(
      `Execute rollback for ${selectedRollback.value.name} from ${selectedRollback.value.fromVersion} to ${selectedRollback.value.toVersion}?`,
      'Confirm Rollback',
      {
        confirmButtonText: 'Execute Rollback',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  )

  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 3000))

  // Update rollback status
  const index = rollbackHistory.value.findIndex(r => r.id === selectedRollback.value.id)
  if (index !== -1) {
    rollbackHistory.value[index].status = 'success'
    rollbackHistory.value[index].date = new Date().toISOString().slice(0, 10)
    rollbackHistory.value[index].duration = `${Math.floor(Math.random() * 15) + 2} min`
    rollbackHistory.value[index].performedBy = 'current_user'
    rollbackHistory.value[index].postCheck = 'passed'
  }

  updateStats()
  updateChart()
  loading.value = false
  rollbackConfirmVisible.value = false
  ElMessage.success(`Rollback executed successfully for ${selectedRollback.value.name}`)
}

const compareRollback = () => {
  if (compareRollbacks.value.length < 2) {
    ElMessage.warning('Please select at least 2 rollbacks to compare')
    return
  }
  compareVisible.value = true
}

const toggleCompare = (rollback: any) => {
  const index = compareRollbacks.value.findIndex(r => r.id === rollback.id)
  if (index === -1) {
    if (compareRollbacks.value.length >= 3) {
      ElMessage.warning('Maximum 3 rollbacks can be compared')
      return
    }
    compareRollbacks.value.push(rollback)
  } else {
    compareRollbacks.value.splice(index, 1)
  }
}

const exportRollbackData = () => {
  const data = rollbackHistory.value.map(r => ({
    ID: r.id,
    Name: r.name,
    Type: r.type,
    Device: r.device,
    FromVersion: r.fromVersion,
    ToVersion: r.toVersion,
    Status: r.status,
    Date: r.date || 'Pending',
    Reason: r.reason,
    Duration: r.duration || 'N/A',
    PerformedBy: r.performedBy || 'N/A'
  }))

  const csv = convertToCSV(data)
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `rollback_center_${new Date().toISOString()}.csv`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Rollback data exported successfully')
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
    case 'success': return 'success'
    case 'available': return 'success'
    case 'failed': return 'danger'
    case 'partial': return 'warning'
    default: return 'info'
  }
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'success': return SuccessFilled
    case 'available': return SuccessFilled
    case 'failed': return CircleClose
    case 'partial': return Warning
    default: return ClockIcon
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'success': return 'Executed'
    case 'available': return 'Available'
    case 'failed': return 'Failed'
    case 'partial': return 'Partial'
    default: return 'Pending'
  }
}

const getPreCheckType = (check: string) => {
  switch (check) {
    case 'passed': return 'success'
    case 'warning': return 'warning'
    case 'failed': return 'danger'
    default: return 'info'
  }
}
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
          <span class="loading-title">Loading Rollback Center</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Compatibility Center - Rollback Center</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="rollback-center-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h2>Rollback Center</h2>
        <el-tag type="warning" effect="dark">Compatibility Center</el-tag>
      </div>
      <div class="header-stats">
        <el-tag type="info" effect="plain">Version Rollback | Recovery Management</el-tag>
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
          <el-select v-model="selectedType" placeholder="Type" clearable style="width: 100%">
            <el-option v-for="t in rollbackTypes" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-input v-model="searchKeyword" placeholder="Search by name, device, or ID..." :prefix-icon="Search" clearable />
        </el-col>
        <el-col :span="6">
          <div class="control-buttons">
            <el-button type="primary" @click="refreshRollbacks" :loading="loading">
              <el-icon><Refresh /></el-icon> Refresh
            </el-button>
            <el-button @click="exportRollbackData">
              <el-icon><Download /></el-icon> Export
            </el-button>
          </div>
        </el-col>
      </el-row>

      <!-- Quick Actions -->
      <el-row :gutter="10" class="action-buttons" style="margin-top: 15px">
        <el-col :span="4">
          <el-button size="small" @click="compareRollback" :disabled="compareRollbacks.length < 2">
            <el-icon><Link /></el-icon> Compare ({{ compareRollbacks.length }})
          </el-button>
        </el-col>
        <el-col :span="4">
          <el-button size="small" @click="compareRollbacks = []">
            <el-icon><Close /></el-icon> Clear Selection
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- Statistics Cards -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon available-icon">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ rollbackStats.available }}</div>
            <div class="stat-label">Available Rollbacks</div>
            <div class="stat-sub-value">Ready to execute</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon executed-icon">
            <el-icon><Finished /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ rollbackStats.totalRollbacks }}</div>
            <div class="stat-label">Total Rollbacks</div>
            <el-progress :percentage="rollbackStats.successRate" :color="'#67C23A'" :stroke-width="6" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon time-icon">
            <el-icon><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ rollbackStats.avgRollbackTime }} min</div>
            <div class="stat-label">Avg Rollback Time</div>
            <div class="stat-sub-value">Success rate: {{ rollbackStats.successRate }}%</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon failed-icon">
            <el-icon><CircleClose /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ rollbackStats.failed }}</div>
            <div class="stat-label">Failed Rollbacks</div>
            <div class="stat-sub-value">{{ rollbackStats.partial }} Partial success</div>
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
              <span>Rollback Status Distribution</span>
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
              <span>Rollback Points Status</span>
              <el-button text type="primary" @click="initTimelineChart">Refresh</el-button>
            </div>
          </template>
          <div ref="timelineRef" class="timeline-chart" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Rollback History Table -->
    <el-card shadow="never" class="rollback-card">
      <template #header>
        <div class="table-header">
          <span>Rollback History & Available Rollbacks</span>
          <div class="table-actions">
            <el-checkbox
                :model-value="compareRollbacks.length === filteredRollbacks.length && filteredRollbacks.length > 0"
                :indeterminate="compareRollbacks.length > 0 && compareRollbacks.length < filteredRollbacks.length"
                @change="(val) => compareRollbacks = val ? [...filteredRollbacks] : []"
            >
              Select All
            </el-checkbox>
          </div>
        </div>
      </template>

      <el-table :data="filteredRollbacks" stripe style="width: 100%">
        <el-table-column type="selection" width="55" :selectable="() => true" @selection-change="(val) => compareRollbacks = val" />
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="Rollback Name" min-width="200" />
        <el-table-column prop="device" label="Device" width="180" />
        <el-table-column label="Type" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.type === 'firmware' ? 'primary' : row.type === 'driver' ? 'success' : 'warning'">
              {{ row.type.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Version" width="150" align="center">
          <template #default="{ row }">
            <span class="version-old">{{ row.fromVersion }}</span>
            <el-icon><Right /></el-icon>
            <span class="version-new">{{ row.toVersion }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              <el-icon style="margin-right: 4px"><component :is="getStatusIcon(row.status)" /></el-icon>
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Pre-Check" width="90" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.preCheck" :type="getPreCheckType(row.preCheck)" size="small">
              {{ row.preCheck?.toUpperCase() }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="date" label="Date" width="110" align="center">
          <template #default="{ row }">
            {{ row.date || 'Pending' }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="170" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">
              Details
            </el-button>
            <el-button
                v-if="row.status === 'available'"
                link type="warning"
                size="small"
                @click="openRollbackConfirm(row)"
            >
              Rollback
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

    <!-- Rollback Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="`Rollback Details - ${selectedRollback?.name}`" width="650px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Rollback ID">{{ selectedRollback?.id }}</el-descriptions-item>
        <el-descriptions-item label="Rollback Name">{{ selectedRollback?.name }}</el-descriptions-item>
        <el-descriptions-item label="Type">{{ selectedRollback?.type?.toUpperCase() }}</el-descriptions-item>
        <el-descriptions-item label="Device">{{ selectedRollback?.device }}</el-descriptions-item>
        <el-descriptions-item label="From Version">{{ selectedRollback?.fromVersion }}</el-descriptions-item>
        <el-descriptions-item label="To Version">{{ selectedRollback?.toVersion }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusType(selectedRollback?.status)" size="small">
            {{ getStatusText(selectedRollback?.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Rollback Point">{{ selectedRollback?.rollbackPoint }}</el-descriptions-item>
        <el-descriptions-item label="Reason">{{ selectedRollback?.reason || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="Duration">{{ selectedRollback?.duration || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="Performed By">{{ selectedRollback?.performedBy || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="Date">{{ selectedRollback?.date || 'Not executed' }}</el-descriptions-item>
        <el-descriptions-item label="Pre-Check">
          <el-tag v-if="selectedRollback?.preCheck" :type="getPreCheckType(selectedRollback.preCheck)" size="small">
            {{ selectedRollback.preCheck?.toUpperCase() }}
          </el-tag>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="Post-Check">
          <el-tag v-if="selectedRollback?.postCheck" :type="getPreCheckType(selectedRollback.postCheck)" size="small">
            {{ selectedRollback.postCheck?.toUpperCase() }}
          </el-tag>
          <span v-else>-</span>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button v-if="selectedRollback?.status === 'available'" type="warning" @click="openRollbackConfirm(selectedRollback)">
          Execute Rollback
        </el-button>
        <el-button @click="detailsVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Rollback Confirmation Dialog -->
    <el-dialog v-model="rollbackConfirmVisible" title="Confirm Rollback" width="500px">
      <div class="rollback-warning">
        <el-alert
            title="Warning: This action will revert the device to a previous version"
            type="warning"
            show-icon
            :closable="false"
        />
      </div>

      <el-form :model="rollbackForm" label-width="120px" style="margin-top: 20px">
        <el-form-item label="Rollback Point">
          <el-tag type="info">{{ selectedRollback?.rollbackPoint }}</el-tag>
        </el-form-item>
        <el-form-item label="From Version">
          <span class="version-old">{{ selectedRollback?.fromVersion }}</span>
          <el-icon><Right /></el-icon>
          <span class="version-new">{{ selectedRollback?.toVersion }}</span>
        </el-form-item>
        <el-form-item label="Reason for Rollback">
          <el-input v-model="rollbackForm.reason" type="textarea" rows="2" placeholder="Please provide a reason" />
        </el-form-item>
        <el-form-item label="Backup Before">
          <el-switch v-model="rollbackForm.backupBefore" />
        </el-form-item>
        <el-form-item label="Notify Users">
          <el-switch v-model="rollbackForm.notifyUsers" />
        </el-form-item>
        <el-form-item label="Confirmation">
          <el-checkbox v-model="rollbackForm.confirmCheck">
            I understand this action may cause temporary service interruption
          </el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rollbackConfirmVisible = false">Cancel</el-button>
        <el-button type="danger" @click="executeRollback">Execute Rollback</el-button>
      </template>
    </el-dialog>

    <!-- Compare Rollbacks Dialog -->
    <el-dialog v-model="compareVisible" title="Compare Rollbacks" width="900px">
      <el-table :data="compareRollbacks" border stripe>
        <el-table-column prop="name" label="Rollback Name" width="200" />
        <el-table-column prop="type" label="Type" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ row.type.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="device" label="Device" width="150" />
        <el-table-column label="Version Change" width="150" align="center">
          <template #default="{ row }">
            <span class="version-old">{{ row.fromVersion }}</span>
            <el-icon><Right /></el-icon>
            <span class="version-new">{{ row.toVersion }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Pre-Check" width="90" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.preCheck" :type="getPreCheckType(row.preCheck)" size="small">
              {{ row.preCheck?.toUpperCase() }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="Reason" min-width="150">
          <template #default="{ row }">
            {{ row.reason || 'N/A' }}
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="compareVisible = false">Close</el-button>
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
.rollback-center-container {
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

.action-buttons {
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

.available-icon {
  background-color: #f0f9ff;
  color: #67c23a;
}

.executed-icon {
  background-color: #e6f7ff;
  color: #409eff;
}

.time-icon {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.failed-icon {
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

.rollback-card {
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

.version-old {
  color: #909399;
  text-decoration: line-through;
  font-size: 12px;
  margin-right: 4px;
}

.version-new {
  color: #67c23a;
  font-weight: bold;
  margin-left: 4px;
}

.rollback-warning {
  margin-bottom: 15px;
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

  .action-buttons .el-col {
    margin-bottom: 10px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>