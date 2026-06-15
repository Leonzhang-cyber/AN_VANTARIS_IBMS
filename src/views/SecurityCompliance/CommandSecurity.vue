<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Refresh, Setting, User, Clock,
  Warning, CircleCheck, TrendCharts, DataLine,
  Star, Share, CopyDocument, Delete, Mic,
  Picture, Document, Upload, Download,
  MagicStick, ChatDotRound, Message, Service,
  Search, Edit, Plus, VideoPlay, VideoPause,
  Operation, Headset, Monitor, Cpu, Connection,
  Lock, Key, Medal, Flag, DataAnalysis,
  EditPen, Tickets, Filter, SuccessFilled
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing command security engine...',
  'Loading command permissions...',
  'Analyzing command patterns...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedRisk = ref('all')
const selectedType = ref('all')
const detailsVisible = ref(false)
const whitelistVisible = ref(false)
const chartRef = ref(null)

let securityChart: echarts.ECharts | null = null

// Risk filters
const riskOptions = [
  { value: 'all', label: 'All Risks' },
  { value: 'critical', label: 'Critical', color: '#F56C6C' },
  { value: 'high', label: 'High', color: '#F56C6C' },
  { value: 'medium', label: 'Medium', color: '#E6A23C' },
  { value: 'low', label: 'Low', color: '#67C23A' }
]

// Type filters
const typeOptions = [
  { value: 'all', label: 'All Types' },
  { value: 'write', label: 'Write Commands' },
  { value: 'read', label: 'Read Commands' },
  { value: 'delete', label: 'Delete Commands' },
  { value: 'config', label: 'Configuration Changes' }
]

// Command security data
const commands = ref([
  {
    id: 'CMD001', command: 'Set Temperature Setpoint', protocol: 'bacnet', risk: 'medium',
    description: 'Write operation to HVAC temperature setpoint',
    lastUsed: '2024-01-15 10:23:45', usageCount: 1245, requiresApproval: true,
    allowedRoles: ['Admin', 'HVAC Engineer'], blockedRoles: ['Operator', 'Viewer'],
    permissions: ['write', 'modify'], status: 'monitored'
  },
  {
    id: 'CMD002', command: 'Emergency Stop', protocol: 'bacnet', risk: 'critical',
    description: 'Emergency stop command for HVAC equipment',
    lastUsed: '2024-01-14 15:30:22', usageCount: 23, requiresApproval: true,
    allowedRoles: ['Admin', 'Safety Officer'], blockedRoles: ['Operator', 'Viewer', 'Engineer'],
    permissions: ['write', 'emergency'], status: 'restricted'
  },
  {
    id: 'CMD003', command: 'Read Energy Meter', protocol: 'modbus', risk: 'low',
    description: 'Read energy consumption data from meters',
    lastUsed: '2024-01-15 09:15:33', usageCount: 5678, requiresApproval: false,
    allowedRoles: ['Admin', 'Energy Analyst', 'Operator', 'Viewer'], blockedRoles: [],
    permissions: ['read'], status: 'allowed'
  },
  {
    id: 'CMD004', command: 'Modify Access Control Rules', protocol: 'bacnet', risk: 'critical',
    description: 'Modify access control permissions and rules',
    lastUsed: '2024-01-13 11:20:45', usageCount: 45, requiresApproval: true,
    allowedRoles: ['Admin', 'Security Admin'], blockedRoles: ['Operator', 'Viewer', 'Engineer'],
    permissions: ['write', 'security'], status: 'restricted'
  },
  {
    id: 'CMD005', command: 'Reset Device Configuration', protocol: 'modbus', risk: 'high',
    description: 'Reset device to factory default settings',
    lastUsed: '2024-01-12 08:45:12', usageCount: 12, requiresApproval: true,
    allowedRoles: ['Admin'], blockedRoles: ['Operator', 'Viewer', 'Engineer', 'Analyst'],
    permissions: ['delete', 'write'], status: 'restricted'
  },
  {
    id: 'CMD006', command: 'Update Firmware', protocol: 'mqtt', risk: 'high',
    description: 'Remote firmware update for IoT devices',
    lastUsed: '2024-01-11 14:20:33', usageCount: 8, requiresApproval: true,
    allowedRoles: ['Admin', 'Firmware Engineer'], blockedRoles: ['Operator', 'Viewer'],
    permissions: ['write', 'system'], status: 'restricted'
  },
  {
    id: 'CMD007', command: 'Export System Logs', protocol: 'snmp', risk: 'medium',
    description: 'Export system logs and audit trails',
    lastUsed: '2024-01-10 16:30:18', usageCount: 234, requiresApproval: false,
    allowedRoles: ['Admin', 'Security Auditor', 'Operator'], blockedRoles: ['Viewer'],
    permissions: ['read', 'export'], status: 'monitored'
  },
  {
    id: 'CMD008', command: 'Change Password', protocol: 'http', risk: 'high',
    description: 'Change user account passwords',
    lastUsed: '2024-01-15 08:20:15', usageCount: 567, requiresApproval: false,
    allowedRoles: ['Admin', 'User'], blockedRoles: [],
    permissions: ['write', 'security'], status: 'allowed'
  },
  {
    id: 'CMD009', command: 'Stop Pump', protocol: 'modbus', risk: 'high',
    description: 'Emergency stop command for pump systems',
    lastUsed: '2024-01-09 09:45:22', usageCount: 34, requiresApproval: true,
    allowedRoles: ['Admin', 'Maintenance Engineer'], blockedRoles: ['Operator', 'Viewer'],
    permissions: ['write'], status: 'restricted'
  },
  {
    id: 'CMD010', command: 'Adjust Lighting Level', protocol: 'bacnet', risk: 'low',
    description: 'Adjust brightness level for lighting zones',
    lastUsed: '2024-01-15 11:30:45', usageCount: 3456, requiresApproval: false,
    allowedRoles: ['Admin', 'Operator', 'Building Manager'], blockedRoles: ['Viewer'],
    permissions: ['write'], status: 'allowed'
  }
])

// Security statistics
const securityStats = reactive({
  total: 0,
  restricted: 0,
  monitored: 0,
  allowed: 0,
  critical: 0,
  high: 0,
  medium: 0,
  low: 0,
  totalUsage: 0
})

// Whitelist form
const whitelistForm = reactive({
  command: '',
  role: '',
  reason: '',
  duration: 'permanent'
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 8,
  total: commands.value.length
})

// Filtered commands
const filteredCommands = computed(() => {
  let filtered = commands.value
  if (searchKeyword.value) {
    filtered = filtered.filter(c =>
        c.command.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        c.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        c.description.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedRisk.value !== 'all') {
    filtered = filtered.filter(c => c.risk === selectedRisk.value)
  }
  if (selectedType.value !== 'all') {
    if (selectedType.value === 'write') {
      filtered = filtered.filter(c => c.permissions.includes('write'))
    } else if (selectedType.value === 'read') {
      filtered = filtered.filter(c => c.permissions.includes('read'))
    } else if (selectedType.value === 'delete') {
      filtered = filtered.filter(c => c.permissions.includes('delete'))
    } else if (selectedType.value === 'config') {
      filtered = filtered.filter(c => c.command.toLowerCase().includes('config') || c.command.toLowerCase().includes('set'))
    }
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
        updateStats()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  securityChart = echarts.init(chartRef.value)
  securityChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c})' },
    legend: { orient: 'vertical', left: 'left', data: ['Restricted', 'Monitored', 'Allowed'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { name: 'Restricted', value: commands.value.filter(c => c.status === 'restricted').length, itemStyle: { color: '#F56C6C' } },
        { name: 'Monitored', value: commands.value.filter(c => c.status === 'monitored').length, itemStyle: { color: '#E6A23C' } },
        { name: 'Allowed', value: commands.value.filter(c => c.status === 'allowed').length, itemStyle: { color: '#67C23A' } }
      ],
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })
}

const updateStats = () => {
  securityStats.total = commands.value.length
  securityStats.restricted = commands.value.filter(c => c.status === 'restricted').length
  securityStats.monitored = commands.value.filter(c => c.status === 'monitored').length
  securityStats.allowed = commands.value.filter(c => c.status === 'allowed').length
  securityStats.critical = commands.value.filter(c => c.risk === 'critical').length
  securityStats.high = commands.value.filter(c => c.risk === 'high').length
  securityStats.medium = commands.value.filter(c => c.risk === 'medium').length
  securityStats.low = commands.value.filter(c => c.risk === 'low').length
  securityStats.totalUsage = commands.value.reduce((sum, c) => sum + c.usageCount, 0)
}

const handleResize = () => {
  securityChart?.resize()
}

// ==================== Security Functions ====================
const refreshData = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  loading.value = false
  ElMessage.success('Command security data refreshed successfully')
}

const viewDetails = (command: any) => {
  selectedCommand.value = command
  detailsVisible.value = true
}

const openWhitelist = () => {
  whitelistForm.command = ''
  whitelistForm.role = ''
  whitelistForm.reason = ''
  whitelistForm.duration = 'permanent'
  whitelistVisible.value = true
}

const addToWhitelist = async () => {
  if (!whitelistForm.command) {
    ElMessage.warning('Please select a command')
    return
  }

  if (!whitelistForm.role) {
    ElMessage.warning('Please select a role')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1000))

  const command = commands.value.find(c => c.id === whitelistForm.command || c.command === whitelistForm.command)
  if (command) {
    const index = commands.value.findIndex(c => c.id === command.id)
    if (index !== -1) {
      commands.value[index].status = 'allowed'
      commands.value[index].allowedRoles.push(whitelistForm.role)
    }
  }

  updateStats()
  initChart()
  whitelistVisible.value = false
  ElMessage.success('Command added to whitelist successfully')
}

const restrictCommand = async (command: any) => {
  await ElMessageBox.confirm(
      `Restrict command "${command.command}"? This will require approval for future executions.`,
      'Confirm Restriction',
      {
        confirmButtonText: 'Restrict',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  )

  const index = commands.value.findIndex(c => c.id === command.id)
  if (index !== -1) {
    commands.value[index].status = 'restricted'
    commands.value[index].requiresApproval = true
  }

  updateStats()
  initChart()
  ElMessage.success('Command restricted successfully')
}

const allowCommand = async (command: any) => {
  await ElMessageBox.confirm(
      `Allow command "${command.command}" without restrictions?`,
      'Confirm Allow',
      {
        confirmButtonText: 'Allow',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  )

  const index = commands.value.findIndex(c => c.id === command.id)
  if (index !== -1) {
    commands.value[index].status = 'allowed'
    commands.value[index].requiresApproval = false
  }

  updateStats()
  initChart()
  ElMessage.success('Command allowed successfully')
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
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'success'
    default: return 'info'
  }
}

const getRiskIcon = (risk: string) => {
  switch (risk) {
    case 'critical': return '🔴'
    case 'high': return '🟠'
    case 'medium': return '🟡'
    case 'low': return '🟢'
    default: return '⚪'
  }
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'restricted': return 'danger'
    case 'monitored': return 'warning'
    case 'allowed': return 'success'
    default: return 'info'
  }
}

const getProtocolIcon = (protocol: string) => {
  switch (protocol) {
    case 'bacnet': return '🔷'
    case 'modbus': return '🔶'
    case 'mqtt': return '📡'
    case 'snmp': return '🔄'
    case 'http': return '🌐'
    default: return '📡'
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
          <span class="loading-title">Loading Command Security</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Security & Compliance - Command Security</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="command-security-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Command Security</h1>
        <p class="page-subtitle">Secure command execution with role-based access control</p>
      </div>
      <div class="header-right">
        <el-button type="primary" size="large" @click="openWhitelist">
          <el-icon><Plus /></el-icon>
          Add to Whitelist
        </el-button>
        <el-button size="large" @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total-icon">
          <el-icon><Command /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ securityStats.total }}</div>
          <div class="stat-label">Total Commands</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ securityStats.restricted }} Restricted</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon usage-icon">
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ securityStats.totalUsage.toLocaleString() }}</div>
          <div class="stat-label">Total Executions</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+18% this month</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon risk-icon">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ securityStats.critical + securityStats.high }}</div>
          <div class="stat-label">High Risk Commands</div>
        </div>
        <div class="stat-trend">
          <span class="trend-neutral">{{ securityStats.medium }} Medium | {{ securityStats.low }} Low</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon allowed-icon">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ securityStats.allowed }}</div>
          <div class="stat-label">Allowed</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ securityStats.monitored }} Monitored</span>
        </div>
      </div>
    </div>

    <!-- Command Security Chart -->
    <div class="chart-section">
      <div class="section-header">
        <h3>Command Security Status Distribution</h3>
        <el-button text type="primary" @click="initChart">Refresh</el-button>
      </div>
      <div ref="chartRef" class="security-chart" style="height: 320px"></div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-bar">
      <div class="filters-left">
        <div class="search-box">
          <el-input
              v-model="searchKeyword"
              placeholder="Search commands..."
              :prefix-icon="Search"
              clearable
              style="width: 240px"
          />
        </div>
        <div class="risk-filters">
          <span class="filter-label">Risk Level:</span>
          <button
              v-for="r in riskOptions"
              :key="r.value"
              class="risk-chip"
              :class="{ active: selectedRisk === r.value }"
              @click="selectedRisk = r.value"
          >
            <span class="chip-dot" :style="{ background: r.color }"></span>
            <span>{{ r.label }}</span>
          </button>
        </div>
        <div class="type-filters">
          <span class="filter-label">Command Type:</span>
          <button
              v-for="t in typeOptions"
              :key="t.value"
              class="type-chip"
              :class="{ active: selectedType === t.value }"
              @click="selectedType = t.value"
          >
            {{ t.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- Commands Table -->
    <el-card shadow="never" class="commands-card">
      <template #header>
        <div class="table-header">
          <span>Command Security Matrix</span>
          <div class="table-actions">
            <el-tag type="info" size="small">{{ filteredCommands.length }} commands</el-tag>
          </div>
        </div>
      </template>

      <el-table :data="filteredCommands" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="command" label="Command" min-width="200" />
        <el-table-column label="Protocol" width="100" align="center">
          <template #default="{ row }">
            <span class="protocol-icon">{{ getProtocolIcon(row.protocol) }}</span>
            {{ row.protocol.toUpperCase() }}
          </template>
        </el-table-column>
        <el-table-column label="Risk" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getRiskType(row.risk)" size="small">
              {{ getRiskIcon(row.risk) }} {{ row.risk.toUpperCase() }}
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
        <el-table-column label="Requires Approval" width="130" align="center">
          <template #default="{ row }">
            <el-tag :type="row.requiresApproval ? 'warning' : 'success'" size="small">
              {{ row.requiresApproval ? 'Yes' : 'No' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="usageCount" label="Usage Count" width="100" align="center" />
        <el-table-column prop="lastUsed" label="Last Used" width="160" />
        <el-table-column label="Actions" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">
              Details
            </el-button>
            <el-button
                v-if="row.status !== 'restricted'"
                link type="danger"
                size="small"
                @click="restrictCommand(row)"
            >
              Restrict
            </el-button>
            <el-button
                v-if="row.status === 'restricted'"
                link type="success"
                size="small"
                @click="allowCommand(row)"
            >
              Allow
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
            :page-sizes="[8, 12, 16, 24]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- Command Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="selectedCommand?.command" width="650px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Command ID">{{ selectedCommand?.id }}</el-descriptions-item>
        <el-descriptions-item label="Protocol">{{ selectedCommand?.protocol?.toUpperCase() }}</el-descriptions-item>
        <el-descriptions-item label="Risk Level">
          <el-tag :type="getRiskType(selectedCommand?.risk)" size="small">
            {{ selectedCommand?.risk?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Security Status">
          <el-tag :type="getStatusType(selectedCommand?.status)" size="small">
            {{ selectedCommand?.status?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Requires Approval">
          <el-tag :type="selectedCommand?.requiresApproval ? 'warning' : 'success'" size="small">
            {{ selectedCommand?.requiresApproval ? 'Yes' : 'No' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Usage Count">{{ selectedCommand?.usageCount.toLocaleString() }}</el-descriptions-item>
        <el-descriptions-item label="Last Used">{{ selectedCommand?.lastUsed }}</el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedCommand?.description }}</el-descriptions-item>
        <el-descriptions-item label="Allowed Roles" :span="2">
          <div class="roles-list">
            <el-tag v-for="role in selectedCommand?.allowedRoles" :key="role" size="small" style="margin: 2px" type="success">
              {{ role }}
            </el-tag>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="Blocked Roles" :span="2">
          <div class="roles-list">
            <el-tag v-for="role in selectedCommand?.blockedRoles" :key="role" size="small" style="margin: 2px" type="danger">
              {{ role }}
            </el-tag>
            <span v-if="!selectedCommand?.blockedRoles.length" class="no-roles">None</span>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="Permissions" :span="2">
          <div class="permissions-list">
            <el-tag v-for="perm in selectedCommand?.permissions" :key="perm" size="small" style="margin: 2px" type="primary">
              {{ perm.toUpperCase() }}
            </el-tag>
          </div>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
        <el-button
            v-if="selectedCommand?.status !== 'restricted'"
            type="danger"
            @click="restrictCommand(selectedCommand)"
        >
          Restrict Command
        </el-button>
        <el-button
            v-if="selectedCommand?.status === 'restricted'"
            type="success"
            @click="allowCommand(selectedCommand)"
        >
          Allow Command
        </el-button>
      </template>
    </el-dialog>

    <!-- Add to Whitelist Dialog -->
    <el-dialog v-model="whitelistVisible" title="Add Command to Whitelist" width="500px">
      <el-form :model="whitelistForm" label-width="120px">
        <el-form-item label="Command" required>
          <el-select v-model="whitelistForm.command" placeholder="Select command" style="width: 100%">
            <el-option
                v-for="cmd in commands.filter(c => c.status !== 'allowed')"
                :key="cmd.id"
                :label="cmd.command"
                :value="cmd.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Role" required>
          <el-select v-model="whitelistForm.role" placeholder="Select role" style="width: 100%">
            <el-option label="Admin" value="Admin" />
            <el-option label="Operator" value="Operator" />
            <el-option label="Engineer" value="Engineer" />
            <el-option label="Auditor" value="Auditor" />
            <el-option label="Viewer" value="Viewer" />
          </el-select>
        </el-form-item>
        <el-form-item label="Duration">
          <el-select v-model="whitelistForm.duration" style="width: 100%">
            <el-option label="Permanent" value="permanent" />
            <el-option label="24 Hours" value="24h" />
            <el-option label="7 Days" value="7d" />
            <el-option label="30 Days" value="30d" />
          </el-select>
        </el-form-item>
        <el-form-item label="Reason">
          <el-input v-model="whitelistForm.reason" type="textarea" rows="2" placeholder="Reason for whitelisting" />
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
.command-security-container {
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

.total-icon {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #409eff;
}

.usage-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.risk-icon {
  background: linear-gradient(135deg, #fef0f0 0%, #fcd9d9 100%);
  color: #f56c6c;
}

.allowed-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
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
  font-size: 11px;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 20px;
}

.trend-up {
  color: #67c23a;
}

.trend-neutral {
  color: #909399;
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

.security-chart {
  width: 100%;
}

/* Filters Bar */
.filters-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 24px;
}

.filters-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-label {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
  margin-right: 8px;
}

.risk-filters,
.type-filters {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.risk-chip,
.type-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 20px;
  font-size: 12px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s ease;
}

.risk-chip:hover,
.type-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.risk-chip.active,
.type-chip.active {
  background: #409eff;
  border-color: #409eff;
  color: white;
}

.chip-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

/* Commands Card */
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

/* Table Cell Styles */
.protocol-icon {
  font-size: 14px;
  margin-right: 4px;
}

/* Dialog Styles */
.roles-list,
.permissions-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.no-roles {
  color: #909399;
  font-style: italic;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .command-security-container {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filters-left {
    flex-direction: column;
    align-items: stretch;
  }

  .risk-filters,
  .type-filters {
    flex-wrap: wrap;
    justify-content: center;
  }

  .page-header {
    flex-direction: column;
    text-align: center;
  }

  .header-right {
    width: 100%;
    justify-content: center;
  }

  .table-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>