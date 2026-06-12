<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Search, Refresh, Connection, Setting, VideoPlay,
  DataLine, Document, CircleCheck, CircleClose,
  Loading, Clock, TrendCharts, Monitor, Edit,
  Warning, SuccessFilled, Upload, Key
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing write utilities...',
  'Preparing command queue...',
  'Loading device database...',
  'Setting up security checks...',
  'Almost ready...'
]

// ==================== Component State ====================
const testing = ref(false)
const searchKeyword = ref('')
const selectedProtocol = ref('all')
const selectedStatus = ref('all')
const commandHistoryVisible = ref(false)
const detailsVisible = ref(false)
const bulkCommandVisible = ref(false)
const chartRef = ref(null)

let successChart: echarts.ECharts | null = null

// Protocols
const protocols = [
  { value: 'all', label: 'All Protocols' },
  { value: 'bacnet', label: 'BACnet/IP' },
  { value: 'modbus', label: 'Modbus TCP' },
  { value: 'mqtt', label: 'MQTT' },
  { value: 'opcua', label: 'OPC-UA' },
  { value: 'snmp', label: 'SNMP' }
]

// Commands for testing
const commands = ref([
  { id: 'CMD001', name: 'Set Temperature Setpoint', device: 'AHU-1 Controller', protocol: 'bacnet', address: 'AV:1', command: 'write', value: 22.5, unit: '°C', status: 'pending', responseTime: null, lastExecuted: null, success: null },
  { id: 'CMD002', name: 'Fan Speed Control', device: 'AHU-1 Controller', protocol: 'bacnet', address: 'AV:2', command: 'write', value: 75, unit: '%', status: 'pending', responseTime: null, lastExecuted: null, success: null },
  { id: 'CMD003', name: 'Chiller Enable/Disable', device: 'Chiller Plant Controller', protocol: 'bacnet', address: 'BV:1', command: 'write', value: 1, unit: 'ON/OFF', status: 'pending', responseTime: null, lastExecuted: null, success: null },
  { id: 'CMD004', name: 'Lighting Level Control', device: 'Lighting Panel - L1', protocol: 'modbus', address: '40001', command: 'write', value: 80, unit: '%', status: 'pending', responseTime: null, lastExecuted: null, success: null },
  { id: 'CMD005', name: 'VFD Pump Speed', device: 'VFD Pump Controller', protocol: 'modbus', address: '40010', command: 'write', value: 60, unit: 'Hz', status: 'pending', responseTime: null, lastExecuted: null, success: null },
  { id: 'CMD006', name: 'MQTT Publish Command', device: 'Temperature Sensors Hub', protocol: 'mqtt', address: 'commands/setpoint', command: 'publish', value: 23.0, unit: '°C', status: 'pending', responseTime: null, lastExecuted: null, success: null },
  { id: 'CMD007', name: 'OPC-UA Write Value', device: 'OPC-UA Gateway', protocol: 'opcua', address: 'ns=2;s=Temperature', command: 'write', value: 22.0, unit: '°C', status: 'pending', responseTime: null, lastExecuted: null, success: null },
  { id: 'CMD008', name: 'SNMP Set OID', device: 'Network Switch - Core', protocol: 'snmp', address: '1.3.6.1.2.1.1.7.0', command: 'set', value: 1, unit: '', status: 'pending', responseTime: null, lastExecuted: null, success: null }
])

// Command history
const commandHistory = ref([
  { id: 'H001', timestamp: '2024-01-15 10:23:45', command: 'Set Temperature Setpoint', device: 'AHU-1 Controller', status: 'success', responseTime: 45, value: 22.5, user: 'admin' },
  { id: 'H002', timestamp: '2024-01-15 10:22:30', command: 'Fan Speed Control', device: 'AHU-1 Controller', status: 'success', responseTime: 52, value: 75, user: 'admin' },
  { id: 'H003', timestamp: '2024-01-15 10:20:00', command: 'Lighting Level Control', device: 'Lighting Panel - L1', status: 'failed', responseTime: 5000, value: 80, user: 'operator', error: 'Timeout' },
  { id: 'H004', timestamp: '2024-01-15 10:15:30', command: 'VFD Pump Speed', device: 'VFD Pump Controller', status: 'success', responseTime: 38, value: 60, user: 'admin' },
  { id: 'H005', timestamp: '2024-01-15 10:10:00', command: 'Chiller Enable/Disable', device: 'Chiller Plant Controller', status: 'success', responseTime: 42, value: 1, user: 'admin' }
])

// Command statistics
const commandStats = reactive({
  total: 0,
  success: 0,
  failed: 0,
  pending: 0,
  avgResponseTime: 0,
  minResponseTime: 0,
  maxResponseTime: 0,
  successRate: 0
})

// Bulk command configuration
const bulkConfig = reactive({
  protocol: 'bacnet',
  deviceId: '',
  commandType: 'write',
  delayBetween: 500,
  timeout: 5000
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: commands.value.length
})

// Filtered commands
const filteredCommands = computed(() => {
  let filtered = commands.value
  if (searchKeyword.value) {
    filtered = filtered.filter(c =>
        c.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        c.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        c.device.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        c.address.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedProtocol.value !== 'all') {
    filtered = filtered.filter(c => c.protocol === selectedProtocol.value)
  }
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(c => c.status === selectedStatus.value)
  }
  pagination.total = filtered.length
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// Unique devices for filter
const uniqueDevices = computed(() => {
  return [...new Set(commands.value.map(c => c.device))]
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
    const cmdList = commands.value.filter(c => c.protocol === protocol.value)
    const success = cmdList.filter(c => c.status === 'success').length
    const failed = cmdList.filter(c => c.status === 'failed').length
    const pending = cmdList.filter(c => c.status === 'pending').length
    return { protocol: protocol.label, success, failed, pending }
  })

  successChart?.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['Success', 'Failed', 'Pending'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: protocolStats.map(p => p.protocol) },
    yAxis: { type: 'value', name: 'Command Count' },
    series: [
      { name: 'Success', type: 'bar', data: protocolStats.map(p => p.success), stack: 'total', itemStyle: { color: '#67C23A', borderRadius: [4, 4, 0, 0] } },
      { name: 'Failed', type: 'bar', data: protocolStats.map(p => p.failed), stack: 'total', itemStyle: { color: '#F56C6C', borderRadius: [4, 4, 0, 0] } },
      { name: 'Pending', type: 'bar', data: protocolStats.map(p => p.pending), stack: 'total', itemStyle: { color: '#E6A23C', borderRadius: [4, 4, 0, 0] } }
    ]
  })
}

const updateStats = () => {
  const successCmds = commands.value.filter(c => c.status === 'success')
  const failedCmds = commands.value.filter(c => c.status === 'failed')
  const pendingCmds = commands.value.filter(c => c.status === 'pending')

  commandStats.total = commands.value.length
  commandStats.success = successCmds.length
  commandStats.failed = failedCmds.length
  commandStats.pending = pendingCmds.length
  commandStats.successRate = (successCmds.length / (successCmds.length + failedCmds.length)) * 100 || 0

  const responseTimes = successCmds.map(c => c.responseTime).filter(t => t !== null)
  if (responseTimes.length > 0) {
    commandStats.avgResponseTime = Math.round(responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length)
    commandStats.minResponseTime = Math.min(...responseTimes)
    commandStats.maxResponseTime = Math.max(...responseTimes)
  }
}

const handleResize = () => {
  successChart?.resize()
}

// ==================== Test Functions ====================
const simulateCommandWrite = async (command: any): Promise<{ success: boolean; responseTime: number; error?: string }> => {
  const startTime = performance.now()

  // Simulate network and processing delay based on protocol
  let delay = 0
  let successRate = 0.9 // 90% success rate

  switch (command.protocol) {
    case 'bacnet':
      delay = Math.random() * 100 + 30
      successRate = 0.92
      break
    case 'modbus':
      delay = Math.random() * 80 + 20
      successRate = 0.88
      break
    case 'mqtt':
      delay = Math.random() * 60 + 15
      successRate = 0.95
      break
    case 'opcua':
      delay = Math.random() * 150 + 50
      successRate = 0.85
      break
    case 'snmp':
      delay = Math.random() * 120 + 40
      successRate = 0.9
      break
    default:
      delay = Math.random() * 100 + 30
  }

  await new Promise(resolve => setTimeout(resolve, delay))

  const success = Math.random() < successRate
  const endTime = performance.now()
  const responseTime = Math.round(endTime - startTime)

  if (success) {
    return { success: true, responseTime }
  } else {
    const errors = ['Timeout', 'Invalid address', 'Access denied', 'Device not responding', 'Value out of range']
    return { success: false, responseTime, error: errors[Math.floor(Math.random() * errors.length)] }
  }
}

const executeCommand = async (command: any) => {
  command.status = 'executing'

  try {
    const result = await simulateCommandWrite(command)
    command.status = result.success ? 'success' : 'failed'
    command.responseTime = result.responseTime
    command.lastExecuted = new Date().toLocaleString()

    // Add to history
    commandHistory.value.unshift({
      id: `H${Date.now()}`,
      timestamp: new Date().toLocaleString(),
      command: command.name,
      device: command.device,
      status: result.success ? 'success' : 'failed',
      responseTime: result.responseTime,
      value: command.value,
      user: 'current_user',
      error: result.error
    })

    updateStats()
    updateChart()

    if (result.success) {
      ElMessage.success(`${command.name} executed successfully (${result.responseTime}ms)`)
    } else {
      ElMessage.error(`${command.name} failed: ${result.error}`)
    }
  } catch (error) {
    command.status = 'failed'
    ElMessage.error(`${command.name} execution failed`)
  }
}

const executeAllCommands = async () => {
  testing.value = true
  let successCount = 0
  let failedCount = 0

  for (const command of filteredCommands.value) {
    command.status = 'executing'
    const result = await simulateCommandWrite(command)
    command.status = result.success ? 'success' : 'failed'
    command.responseTime = result.responseTime
    command.lastExecuted = new Date().toLocaleString()

    if (result.success) successCount++
    else failedCount++

    // Add delay between commands
    await new Promise(resolve => setTimeout(resolve, 200))
  }

  updateStats()
  updateChart()
  testing.value = false
  ElMessage.success(`Batch execution completed: ${successCount} success, ${failedCount} failed`)
}

const executeBulkCommands = async () => {
  bulkCommandVisible.value = false
  testing.value = true

  let commandsToExecute = commands.value
  if (bulkConfig.protocol !== 'all') {
    commandsToExecute = commandsToExecute.filter(c => c.protocol === bulkConfig.protocol)
  }
  if (bulkConfig.deviceId) {
    commandsToExecute = commandsToExecute.filter(c => c.device === bulkConfig.deviceId)
  }

  let successCount = 0
  let failedCount = 0

  for (const command of commandsToExecute) {
    command.status = 'executing'
    const result = await simulateCommandWrite(command)
    command.status = result.success ? 'success' : 'failed'
    command.responseTime = result.responseTime
    command.lastExecuted = new Date().toLocaleString()

    if (result.success) successCount++
    else failedCount++

    await new Promise(resolve => setTimeout(resolve, bulkConfig.delayBetween))
  }

  updateStats()
  updateChart()
  testing.value = false
  ElMessage.success(`Bulk execution completed: ${successCount} success, ${failedCount} failed`)
}

const executeByProtocol = async (protocol: string) => {
  testing.value = true
  const commandsToTest = commands.value.filter(c => c.protocol === protocol)

  let successCount = 0
  let failedCount = 0

  for (const command of commandsToTest) {
    command.status = 'executing'
    const result = await simulateCommandWrite(command)
    command.status = result.success ? 'success' : 'failed'
    command.responseTime = result.responseTime
    command.lastExecuted = new Date().toLocaleString()

    if (result.success) successCount++
    else failedCount++

    await new Promise(resolve => setTimeout(resolve, 100))
  }

  updateStats()
  updateChart()
  testing.value = false
  ElMessage.success(`${protocol.toUpperCase()} commands: ${successCount} success, ${failedCount} failed`)
}

const viewCommandHistory = () => {
  commandHistoryVisible.value = true
}

const viewDetails = (command: any) => {
  selectedCommand.value = command
  detailsVisible.value = true
}

const exportResults = () => {
  const results = commands.value.map(c => ({
    CommandID: c.id,
    CommandName: c.name,
    Device: c.device,
    Protocol: c.protocol,
    Address: c.address,
    Value: c.value,
    Unit: c.unit,
    Status: c.status,
    ResponseTime: c.responseTime,
    LastExecuted: c.lastExecuted
  }))

  const csv = convertToCSV(results)
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `command_write_test_${new Date().toISOString()}.csv`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Results exported successfully')
}

const convertToCSV = (data: any[]) => {
  const headers = Object.keys(data[0])
  const rows = data.map(obj => headers.map(header => JSON.stringify(obj[header])).join(','))
  return [headers.join(','), ...rows].join('\n')
}

const resetAllCommands = () => {
  commands.value.forEach(c => {
    c.status = 'pending'
    c.responseTime = null
    c.lastExecuted = null
    c.success = null
  })
  updateStats()
  updateChart()
  ElMessage.info('All command statuses reset')
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
    case 'success': return CircleCheck
    case 'failed': return CircleClose
    case 'executing': return Loading
    default: return Clock
  }
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'success': return 'success'
    case 'failed': return 'danger'
    case 'executing': return 'warning'
    default: return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'success': return 'Success'
    case 'failed': return 'Failed'
    case 'executing': return 'Executing...'
    default: return 'Pending'
  }
}

const getResponseTimeClass = (time: number) => {
  if (!time) return ''
  if (time < 100) return 'response-good'
  if (time < 300) return 'response-fair'
  return 'response-poor'
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
          <span class="loading-title">Loading Command Write Test</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Protocol Health Check - Command Write Test</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="command-write-test-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h2>Command Write Test</h2>
        <el-tag type="warning" effect="dark">Protocol Health Check</el-tag>
      </div>
      <div class="header-stats">
        <el-tag type="info" effect="plain">Write | Set | Publish | Control</el-tag>
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
            <el-option label="Success" value="success" />
            <el-option label="Failed" value="failed" />
            <el-option label="Pending" value="pending" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-input v-model="searchKeyword" placeholder="Search commands..." :prefix-icon="Search" clearable />
        </el-col>
        <el-col :span="6">
          <div class="control-buttons">
            <el-button type="primary" @click="executeAllCommands" :loading="testing">
              <el-icon><VideoPlay /></el-icon> Execute All
            </el-button>
            <el-button @click="bulkCommandVisible = true">
              <el-icon><Upload /></el-icon> Bulk Test
            </el-button>
            <el-button @click="resetAllCommands">
              <el-icon><Refresh /></el-icon> Reset
            </el-button>
          </div>
        </el-col>
      </el-row>

      <!-- Quick Protocol Tests -->
      <el-row :gutter="10" class="protocol-buttons" style="margin-top: 15px">
        <el-col :span="4" v-for="p in protocols.slice(1)" :key="p.value">
          <el-button size="small" @click="executeByProtocol(p.value)" :loading="testing" style="width: 100%">
            {{ p.label }}
          </el-button>
        </el-col>
        <el-col :span="4">
          <el-button size="small" @click="viewCommandHistory">
            <el-icon><Document /></el-icon> History
          </el-button>
        </el-col>
        <el-col :span="4">
          <el-button size="small" @click="exportResults">
            <el-icon><DataLine /></el-icon> Export
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
            <div class="stat-value">{{ commandStats.total }}</div>
            <div class="stat-label">Total Commands</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon success-icon">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ commandStats.success }}</div>
            <div class="stat-label">Successful</div>
            <el-progress :percentage="commandStats.successRate" :color="'#67C23A'" :stroke-width="6" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon failed-icon">
            <el-icon><CircleClose /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ commandStats.failed }}</div>
            <div class="stat-label">Failed</div>
            <div class="stat-sub-value">{{ commandStats.pending }} Pending</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon response-icon">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ commandStats.avgResponseTime }}ms</div>
            <div class="stat-label">Avg Response</div>
            <div class="stat-sub-value">Min: {{ commandStats.minResponseTime }}ms | Max: {{ commandStats.maxResponseTime }}ms</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Command Chart -->
    <el-card shadow="never" class="chart-card">
      <template #header>
        <div class="card-header">
          <span>Command Execution Status by Protocol</span>
          <el-button text type="primary" @click="updateChart">Refresh Chart</el-button>
        </div>
      </template>
      <div ref="chartRef" class="chart" style="height: 320px"></div>
    </el-card>

    <!-- Commands Table -->
    <el-card shadow="never" class="commands-card">
      <template #header>
        <div class="table-header">
          <span>Command List</span>
          <div class="table-actions">
            <el-button type="primary" size="small" @click="executeAllCommands" :loading="testing">
              Execute All Commands
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredCommands" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="Command Name" min-width="180" />
        <el-table-column prop="device" label="Device" width="180" />
        <el-table-column label="Protocol" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.protocol.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="address" label="Address" width="130" />
        <el-table-column label="Value" width="100" align="center">
          <template #default="{ row }">
            <span class="value-text">{{ row.value }} {{ row.unit }}</span>
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
        <el-table-column label="Response Time" width="110" align="center">
          <template #default="{ row }">
            <span v-if="row.responseTime !== null" :class="getResponseTimeClass(row.responseTime)">
              {{ row.responseTime }}ms
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="lastExecuted" label="Last Executed" width="160" />
        <el-table-column label="Actions" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="executeCommand(row)" :disabled="testing || row.status === 'executing'">
              Execute
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

    <!-- Command History Dialog -->
    <el-dialog v-model="commandHistoryVisible" title="Command History" width="900px">
      <el-table :data="commandHistory" stripe max-height="400">
        <el-table-column prop="timestamp" label="Timestamp" width="160" />
        <el-table-column prop="command" label="Command" min-width="180" />
        <el-table-column prop="device" label="Device" width="160" />
        <el-table-column label="Status" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="responseTime" label="Response" width="100" align="center">
          <template #default="{ row }">
            {{ row.responseTime }}ms
          </template>
        </el-table-column>
        <el-table-column prop="value" label="Value" width="80" />
        <el-table-column prop="user" label="User" width="100" />
        <el-table-column prop="error" label="Error" min-width="150">
          <template #default="{ row }">
            <span class="error-text">{{ row.error || '-' }}</span>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button type="primary" @click="commandHistoryVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Command Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="`Command Details - ${selectedCommand?.name}`" width="550px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Command ID">{{ selectedCommand?.id }}</el-descriptions-item>
        <el-descriptions-item label="Command Name">{{ selectedCommand?.name }}</el-descriptions-item>
        <el-descriptions-item label="Device">{{ selectedCommand?.device }}</el-descriptions-item>
        <el-descriptions-item label="Protocol">{{ selectedCommand?.protocol?.toUpperCase() }}</el-descriptions-item>
        <el-descriptions-item label="Address">{{ selectedCommand?.address }}</el-descriptions-item>
        <el-descriptions-item label="Command Type">{{ selectedCommand?.command }}</el-descriptions-item>
        <el-descriptions-item label="Value">{{ selectedCommand?.value }} {{ selectedCommand?.unit }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusType(selectedCommand?.status)" size="small">
            {{ getStatusText(selectedCommand?.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Response Time">
          <span v-if="selectedCommand?.responseTime !== null">{{ selectedCommand?.responseTime }}ms</span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="Last Executed">{{ selectedCommand?.lastExecuted || 'Never' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button type="primary" @click="executeCommand(selectedCommand)" :disabled="testing">Execute Now</el-button>
        <el-button @click="detailsVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Bulk Command Dialog -->
    <el-dialog v-model="bulkCommandVisible" title="Bulk Command Test" width="500px">
      <el-form :model="bulkConfig" label-width="120px">
        <el-form-item label="Protocol">
          <el-select v-model="bulkConfig.protocol" style="width: 100%">
            <el-option label="All Protocols" value="all" />
            <el-option v-for="p in protocols.slice(1)" :key="p.value" :label="p.label" :value="p.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Device">
          <el-select v-model="bulkConfig.deviceId" clearable placeholder="All Devices" style="width: 100%">
            <el-option v-for="d in uniqueDevices" :key="d" :label="d" :value="d" />
          </el-select>
        </el-form-item>
        <el-form-item label="Command Type">
          <el-select v-model="bulkConfig.commandType" style="width: 100%">
            <el-option label="Write Commands" value="write" />
            <el-option label="All Commands" value="all" />
          </el-select>
        </el-form-item>
        <el-form-item label="Delay Between (ms)">
          <el-input-number v-model="bulkConfig.delayBetween" :min="100" :max="5000" :step="100" />
        </el-form-item>
        <el-form-item label="Timeout (ms)">
          <el-input-number v-model="bulkConfig.timeout" :min="1000" :max="30000" :step="1000" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bulkCommandVisible = false">Cancel</el-button>
        <el-button type="primary" @click="executeBulkCommands">Start Bulk Test</el-button>
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
.command-write-test-container {
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

.success-icon {
  background-color: #f0f9ff;
  color: #67c23a;
}

.failed-icon {
  background-color: #fef0f0;
  color: #f56c6c;
}

.response-icon {
  background-color: #fdf6ec;
  color: #e6a23c;
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

.chart {
  width: 100%;
}

.value-text {
  font-weight: 500;
  color: #409eff;
}

.response-good {
  color: #67c23a;
  font-weight: bold;
}

.response-fair {
  color: #e6a23c;
  font-weight: bold;
}

.response-poor {
  color: #f56c6c;
  font-weight: bold;
}

.error-text {
  color: #f56c6c;
  font-size: 12px;
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