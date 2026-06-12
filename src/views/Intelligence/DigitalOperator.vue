<script setup lang="ts">
import { ref, onMounted, computed, reactive, nextTick } from 'vue'
import * as echarts from 'echarts'
import {
  Refresh, Setting, User, Clock,
  Warning, CircleCheck, TrendCharts, DataLine,
  Star, Share, CopyDocument, Delete, Mic,
  Picture, Document, Upload, Download,
  MagicStick, ChatDotRound, Message, Service,
  Search, Edit, Plus, VideoPlay, VideoPause,
  Operation, Headset, Monitor, Cpu
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing Digital Operator...',
  'Loading operational data...',
  'Preparing control interfaces...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const selectedDevice = ref('')
const selectedCommand = ref('')
const commandValue = ref('')
const executeDialogVisible = ref(false)
const scheduleDialogVisible = ref(false)
const historyVisible = ref(false)
const chartRef = ref(null)

let performanceChart: echarts.ECharts | null = null

// Devices list
const devices = ref([
  { id: 'DEV001', name: 'AHU-1 (Air Handling Unit)', type: 'hvac', status: 'online', location: 'Floor 1' },
  { id: 'DEV002', name: 'AHU-2 (Air Handling Unit)', type: 'hvac', status: 'online', location: 'Floor 2' },
  { id: 'DEV003', name: 'Chiller-1', type: 'hvac', status: 'online', location: 'Plant Room' },
  { id: 'DEV004', name: 'Lighting Panel L1', type: 'lighting', status: 'online', location: 'Floor 1' },
  { id: 'DEV005', name: 'Lighting Panel L2', type: 'lighting', status: 'offline', location: 'Floor 2' },
  { id: 'DEV006', name: 'VFD Pump', type: 'pump', status: 'online', location: 'Plant Room' }
])

// Commands by device type
const commands = ref({
  hvac: [
    { value: 'set_temperature', label: 'Set Temperature', type: 'numeric', unit: '°C', range: { min: 18, max: 26 } },
    { value: 'set_fan_speed', label: 'Set Fan Speed', type: 'numeric', unit: '%', range: { min: 0, max: 100 } },
    { value: 'set_mode', label: 'Set Operation Mode', type: 'select', options: ['Auto', 'Cool', 'Heat', 'Fan Only'] },
    { value: 'emergency_stop', label: 'Emergency Stop', type: 'confirm' }
  ],
  lighting: [
    { value: 'set_brightness', label: 'Set Brightness', type: 'numeric', unit: '%', range: { min: 0, max: 100 } },
    { value: 'turn_on', label: 'Turn On', type: 'button' },
    { value: 'turn_off', label: 'Turn Off', type: 'button' },
    { value: 'set_schedule', label: 'Set Schedule', type: 'schedule' }
  ],
  pump: [
    { value: 'set_speed', label: 'Set Pump Speed', type: 'numeric', unit: 'Hz', range: { min: 0, max: 60 } },
    { value: 'start', label: 'Start Pump', type: 'button' },
    { value: 'stop', label: 'Stop Pump', type: 'button' }
  ]
})

// Operation history
const operationHistory = ref([
  { id: 'OP001', command: 'Set Temperature', device: 'AHU-1', value: '22°C', operator: 'John Smith', timestamp: '2024-01-15 10:30:22', status: 'success' },
  { id: 'OP002', command: 'Set Fan Speed', device: 'AHU-2', value: '75%', operator: 'Sarah Johnson', timestamp: '2024-01-15 09:45:12', status: 'success' },
  { id: 'OP003', command: 'Turn On', device: 'Lighting Panel L1', value: 'On', operator: 'Mike Chen', timestamp: '2024-01-15 08:30:00', status: 'success' },
  { id: 'OP004', command: 'Set Brightness', device: 'Lighting Panel L2', value: '50%', operator: 'Emily Wong', timestamp: '2024-01-14 17:20:00', status: 'failed' }
])

// Performance data
const performanceData = ref([
  { time: '00:00', responseTime: 1.2, successRate: 98 },
  { time: '02:00', responseTime: 1.1, successRate: 99 },
  { time: '04:00', responseTime: 1.0, successRate: 99 },
  { time: '06:00', responseTime: 1.3, successRate: 98 },
  { time: '08:00', responseTime: 1.8, successRate: 97 },
  { time: '10:00', responseTime: 2.1, successRate: 96 },
  { time: '12:00', responseTime: 1.9, successRate: 97 },
  { time: '14:00', responseTime: 1.7, successRate: 98 },
  { time: '16:00', responseTime: 1.6, successRate: 98 },
  { time: '18:00', responseTime: 1.5, successRate: 99 },
  { time: '20:00', responseTime: 1.3, successRate: 99 },
  { time: '22:00', responseTime: 1.2, successRate: 99 }
])

// Statistics
const operatorStats = reactive({
  totalCommands: 1245,
  successRate: 97.8,
  avgResponseTime: 1.6,
  activeUsers: 8,
  onlineDevices: 5,
  totalDevices: 6
})

// Schedule form
const scheduleForm = reactive({
  command: '',
  device: '',
  scheduleTime: '',
  recurrence: 'once',
  value: ''
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 8,
  total: operationHistory.value.length
})

// Filtered history
const filteredHistory = computed(() => {
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return operationHistory.value.slice(start, end)
})

// Available commands for selected device
const availableCommands = computed(() => {
  if (!selectedDevice.value) return []
  const device = devices.value.find(d => d.id === selectedDevice.value)
  if (!device) return []
  return commands.value[device.type as keyof typeof commands.value] || []
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
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  performanceChart = echarts.init(chartRef.value)
  performanceChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Response Time (s)', 'Success Rate (%)'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: performanceData.value.map(d => d.time) },
    yAxis: [
      { type: 'value', name: 'Response Time (s)', min: 0, max: 3 },
      { type: 'value', name: 'Success Rate (%)', min: 90, max: 100 }
    ],
    series: [
      { name: 'Response Time (s)', type: 'line', data: performanceData.value.map(d => d.responseTime), smooth: true, lineStyle: { color: '#409EFF', width: 2 }, areaStyle: { opacity: 0.1, color: '#409EFF' }, symbol: 'circle', symbolSize: 6 },
      { name: 'Success Rate (%)', type: 'line', data: performanceData.value.map(d => d.successRate), smooth: true, lineStyle: { color: '#67C23A', width: 2 }, symbol: 'diamond', symbolSize: 6, yAxisIndex: 1 }
    ]
  })
}

const handleResize = () => {
  performanceChart?.resize()
}

// ==================== Operator Functions ====================
const refreshData = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  loading.value = false
  ElMessage.success('Data refreshed successfully')
}

const openExecuteDialog = () => {
  if (!selectedDevice.value) {
    ElMessage.warning('Please select a device first')
    return
  }
  if (!selectedCommand.value) {
    ElMessage.warning('Please select a command')
    return
  }
  executeDialogVisible.value = true
}

const executeCommand = async () => {
  const device = devices.value.find(d => d.id === selectedDevice.value)
  const command = availableCommands.value.find(c => c.value === selectedCommand.value)

  if (!device || !command) return

  // Validate command value
  if (command.type === 'numeric') {
    const numValue = parseFloat(commandValue.value)
    if (isNaN(numValue) || numValue < command.range.min || numValue > command.range.max) {
      ElMessage.warning(`Please enter a value between ${command.range.min} and ${command.range.max}`)
      return
    }
  }

  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))

  // Add to history
  operationHistory.value.unshift({
    id: `OP${String(operationHistory.value.length + 1).padStart(3, '0')}`,
    command: command.label,
    device: device.name,
    value: command.type === 'numeric' ? `${commandValue.value}${command.unit}` : (command.type === 'select' ? commandValue.value : 'Executed'),
    operator: 'Current User',
    timestamp: new Date().toLocaleString(),
    status: Math.random() > 0.1 ? 'success' : 'failed'
  })

  loading.value = false
  executeDialogVisible.value = false
  commandValue.value = ''
  ElMessage.success(`Command "${command.label}" executed successfully on ${device.name}`)
}

const openScheduleDialog = () => {
  if (!selectedDevice.value || !selectedCommand.value) {
    ElMessage.warning('Please select a device and command first')
    return
  }
  scheduleDialogVisible.value = true
}

const scheduleCommand = async () => {
  if (!scheduleForm.scheduleTime) {
    ElMessage.warning('Please select a schedule time')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1000))
  ElMessage.success(`Command scheduled at ${scheduleForm.scheduleTime}`)
  scheduleDialogVisible.value = false
}

const viewHistory = () => {
  historyVisible.value = true
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getStatusType = (status: string) => {
  return status === 'success' ? 'success' : 'danger'
}

const getDeviceIcon = (type: string) => {
  switch (type) {
    case 'hvac': return '❄️'
    case 'lighting': return '💡'
    case 'pump': return '💧'
    default: return '🔧'
  }
}

const getDeviceStatus = (status: string) => {
  return status === 'online' ? 'success' : 'danger'
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
          <span class="loading-title">Loading Digital Operator</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Intelligence - Digital Operator</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="digital-operator-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Digital Operator</h1>
        <p class="page-subtitle">Remote command and control interface for building systems</p>
      </div>
      <div class="header-right">
        <el-button size="large" @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
        <el-button size="large" @click="viewHistory">
          <el-icon><Mic /></el-icon>
          History
        </el-button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon commands-icon">
          <el-icon><Operation /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ operatorStats.totalCommands.toLocaleString() }}</div>
          <div class="stat-label">Total Commands</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+12% this week</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon success-icon">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ operatorStats.successRate }}%</div>
          <div class="stat-label">Success Rate</div>
        </div>
        <div class="stat-trend">
          <el-progress :percentage="operatorStats.successRate" :stroke-width="4" :show-text="false" />
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon response-icon">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ operatorStats.avgResponseTime }}s</div>
          <div class="stat-label">Avg Response Time</div>
        </div>
        <div class="stat-trend">
          <span class="trend-down">-0.2s</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon devices-icon">
          <el-icon><Monitor /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ operatorStats.onlineDevices }}/{{ operatorStats.totalDevices }}</div>
          <div class="stat-label">Devices Online</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ operatorStats.activeUsers }} Active Users</span>
        </div>
      </div>
    </div>

    <!-- Main Control Panel -->
    <div class="control-panel">
      <!-- Device Selection -->
      <div class="panel-section">
        <h3>Device Selection</h3>
        <div class="device-grid">
          <div
              v-for="device in devices"
              :key="device.id"
              class="device-card"
              :class="{ active: selectedDevice === device.id, offline: device.status === 'offline' }"
              @click="selectedDevice = device.id"
          >
            <div class="device-icon">{{ getDeviceIcon(device.type) }}</div>
            <div class="device-info">
              <div class="device-name">{{ device.name }}</div>
              <div class="device-location">{{ device.location }}</div>
            </div>
            <div class="device-status">
              <el-tag :type="getDeviceStatus(device.status)" size="small">
                {{ device.status }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>

      <!-- Command Selection -->
      <div class="panel-section">
        <h3>Command Selection</h3>
        <div class="command-grid">
          <div
              v-for="cmd in availableCommands"
              :key="cmd.value"
              class="command-card"
              :class="{ active: selectedCommand === cmd.value }"
              @click="selectedCommand = cmd.value"
          >
            <div class="command-icon">{{ cmd.type === 'numeric' ? '🔢' : cmd.type === 'select' ? '📋' : cmd.type === 'button' ? '🔘' : '📅' }}</div>
            <div class="command-info">
              <div class="command-name">{{ cmd.label }}</div>
              <div class="command-type">{{ cmd.type === 'numeric' ? cmd.unit : cmd.type }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Command Input & Actions -->
      <div class="panel-section actions-section">
        <h3>Command Execution</h3>
        <div class="actions-container">
          <div v-if="selectedCommand && availableCommands.find(c => c.value === selectedCommand)?.type === 'numeric'" class="value-input">
            <el-input
                v-model="commandValue"
                :placeholder="`Enter value (${availableCommands.find(c => c.value === selectedCommand)?.range.min} - ${availableCommands.find(c => c.value === selectedCommand)?.range.max})`"
                type="number"
            />
            <span class="unit">{{ availableCommands.find(c => c.value === selectedCommand)?.unit }}</span>
          </div>

          <div v-if="selectedCommand && availableCommands.find(c => c.value === selectedCommand)?.type === 'select'" class="value-input">
            <el-select v-model="commandValue" placeholder="Select value" style="width: 100%">
              <el-option
                  v-for="opt in availableCommands.find(c => c.value === selectedCommand)?.options"
                  :key="opt"
                  :label="opt"
                  :value="opt"
              />
            </el-select>
          </div>

          <div class="action-buttons">
            <el-button type="primary" size="large" @click="openExecuteDialog" :disabled="!selectedDevice || !selectedCommand">
              <el-icon><VideoPlay /></el-icon>
              Execute Now
            </el-button>
            <el-button size="large" @click="openScheduleDialog" :disabled="!selectedDevice || !selectedCommand">
              <el-icon><Calendar /></el-icon>
              Schedule
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Chart -->
    <div class="chart-section">
      <div class="section-header">
        <h3>System Performance</h3>
        <el-button text type="primary" @click="initChart">Refresh</el-button>
      </div>
      <div ref="chartRef" class="performance-chart" style="height: 300px"></div>
    </div>

    <!-- Execute Command Dialog -->
    <el-dialog v-model="executeDialogVisible" title="Execute Command" width="450px">
      <div class="execute-confirm">
        <div class="confirm-info">
          <p><strong>Device:</strong> {{ devices.find(d => d.id === selectedDevice)?.name }}</p>
          <p><strong>Command:</strong> {{ availableCommands.find(c => c.value === selectedCommand)?.label }}</p>
          <p v-if="commandValue"><strong>Value:</strong> {{ commandValue }} {{ availableCommands.find(c => c.value === selectedCommand)?.unit }}</p>
        </div>
        <el-alert
            title="Confirm Command Execution"
            type="warning"
            show-icon
            :closable="false"
        >
          <template #default>
            <p>This action will be logged and may affect building operations.</p>
          </template>
        </el-alert>
      </div>
      <template #footer>
        <el-button @click="executeDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="executeCommand">Execute Command</el-button>
      </template>
    </el-dialog>

    <!-- Schedule Command Dialog -->
    <el-dialog v-model="scheduleDialogVisible" title="Schedule Command" width="500px">
      <el-form :model="scheduleForm" label-width="100px">
        <el-form-item label="Device">
          <span>{{ devices.find(d => d.id === selectedDevice)?.name }}</span>
        </el-form-item>
        <el-form-item label="Command">
          <span>{{ availableCommands.find(c => c.value === selectedCommand)?.label }}</span>
        </el-form-item>
        <el-form-item label="Value" v-if="commandValue">
          <span>{{ commandValue }}</span>
        </el-form-item>
        <el-form-item label="Schedule Time" required>
          <el-date-picker
              v-model="scheduleForm.scheduleTime"
              type="datetime"
              placeholder="Select date and time"
              style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="Recurrence">
          <el-select v-model="scheduleForm.recurrence" style="width: 100%">
            <el-option label="Once" value="once" />
            <el-option label="Daily" value="daily" />
            <el-option label="Weekly" value="weekly" />
            <el-option label="Monthly" value="monthly" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="scheduleDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="scheduleCommand">Schedule</el-button>
      </template>
    </el-dialog>

    <!-- History Dialog -->
    <el-dialog v-model="historyVisible" title="Command History" width="800px">
      <el-table :data="operationHistory" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="command" label="Command" width="120" />
        <el-table-column prop="device" label="Device" min-width="150" />
        <el-table-column prop="value" label="Value" width="100" />
        <el-table-column prop="operator" label="Operator" width="130" />
        <el-table-column prop="timestamp" label="Timestamp" width="160" />
        <el-table-column label="Status" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button type="primary" @click="historyVisible = false">Close</el-button>
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
.digital-operator-container {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #eef2f6 100%);
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #1e293b 0%, #2d3a4e 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.header-right {
  display: flex;
  gap: 12px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.commands-icon {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #409eff;
}

.success-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.response-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.devices-icon {
  background: linear-gradient(135deg, #fef0f0 0%, #fcd9d9 100%);
  color: #f56c6c;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  margin-top: 4px;
}

.stat-trend {
  position: absolute;
  top: 16px;
  right: 16px;
}

.trend-up {
  font-size: 11px;
  color: #67c23a;
  background: #f0f9ff;
  padding: 4px 8px;
  border-radius: 20px;
}

.trend-down {
  font-size: 11px;
  color: #f56c6c;
  background: #fef0f0;
  padding: 4px 8px;
  border-radius: 20px;
}

/* Control Panel */
.control-panel {
  background: white;
  border-radius: 24px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.panel-section {
  margin-bottom: 28px;
}

.panel-section:last-child {
  margin-bottom: 0;
}

.panel-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 16px 0;
}

/* Device Grid */
.device-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.device-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #fafbfc;
  border: 2px solid transparent;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.device-card:hover {
  background: #f0f9ff;
  transform: translateX(4px);
}

.device-card.active {
  border-color: #409eff;
  background: #f0f9ff;
}

.device-card.offline {
  opacity: 0.6;
}

.device-icon {
  font-size: 28px;
}

.device-info {
  flex: 1;
}

.device-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.device-location {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

/* Command Grid */
.command-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.command-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #fafbfc;
  border: 2px solid transparent;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.command-card:hover {
  background: #f0f9ff;
  transform: translateX(4px);
}

.command-card.active {
  border-color: #409eff;
  background: #f0f9ff;
}

.command-icon {
  font-size: 20px;
}

.command-info {
  flex: 1;
}

.command-name {
  font-size: 13px;
  font-weight: 500;
  color: #1e293b;
}

.command-type {
  font-size: 11px;
  color: #909399;
  margin-top: 2px;
}

/* Actions Section */
.actions-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.value-input {
  display: flex;
  align-items: center;
  gap: 12px;
}

.value-input .el-input {
  flex: 1;
}

.unit {
  font-size: 14px;
  color: #909399;
  min-width: 40px;
}

.action-buttons {
  display: flex;
  gap: 16px;
}

.action-buttons .el-button {
  flex: 1;
}

/* Chart Section */
.chart-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.performance-chart {
  width: 100%;
}

/* Execute Dialog */
.execute-confirm {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.confirm-info {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 12px;
}

.confirm-info p {
  margin: 8px 0;
  font-size: 14px;
}

.confirm-info p:first-child {
  margin-top: 0;
}

.confirm-info p:last-child {
  margin-bottom: 0;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .device-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
}

@media (max-width: 768px) {
  .digital-operator-container {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    flex-direction: column;
  }

  .page-header {
    flex-direction: column;
    text-align: center;
  }

  .header-right {
    width: 100%;
    justify-content: center;
  }

  .command-grid {
    grid-template-columns: 1fr;
  }
}
</style>