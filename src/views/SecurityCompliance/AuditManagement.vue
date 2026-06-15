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
  Lock, Key, Shield, Medal, Flag, DataAnalysis,
  EditPen, Tickets, Filter, SuccessFilled,
  Command, Terminal, List, Download as DownloadIcon
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing audit engine...',
  'Loading audit logs...',
  'Analyzing compliance data...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedSeverity = ref('all')
const selectedAction = ref('all')
const detailsVisible = ref(false)
const exportDialogVisible = ref(false)
const chartRef = ref(null)

let auditChart: echarts.ECharts | null = null

// Severity filters
const severityOptions = [
  { value: 'all', label: 'All Severities' },
  { value: 'critical', label: 'Critical', color: '#F56C6C' },
  { value: 'high', label: 'High', color: '#F56C6C' },
  { value: 'medium', label: 'Medium', color: '#E6A23C' },
  { value: 'low', label: 'Low', color: '#67C23A' }
]

// Action filters
const actionOptions = [
  { value: 'all', label: 'All Actions' },
  { value: 'login', label: 'Login' },
  { value: 'logout', label: 'Logout' },
  { value: 'command', label: 'Command Execution' },
  { value: 'config', label: 'Configuration Change' },
  { value: 'access', label: 'Access Control' }
]

// Audit logs data
const auditLogs = ref([
  {
    id: 'AUD001', timestamp: '2024-01-15 10:23:45', user: 'john.smith@system.com', userName: 'John Smith',
    action: 'login', severity: 'low', status: 'success',
    details: 'User logged in successfully', ip: '192.168.1.105', device: 'Desktop - Chrome',
    module: 'Authentication', changes: null
  },
  {
    id: 'AUD002', timestamp: '2024-01-15 09:45:12', user: 'sarah.j@system.com', userName: 'Sarah Johnson',
    action: 'command', severity: 'high', status: 'success',
    details: 'Executed emergency stop command on Chiller-1', ip: '192.168.1.108', device: 'Laptop - Firefox',
    module: 'HVAC Control', changes: 'Command: Emergency Stop, Target: Chiller-1'
  },
  {
    id: 'AUD003', timestamp: '2024-01-15 09:30:22', user: 'mike.chen@system.com', userName: 'Mike Chen',
    action: 'config', severity: 'medium', status: 'success',
    details: 'Modified temperature setpoint for AHU-2', ip: '192.168.1.110', device: 'Mobile - Safari',
    module: 'HVAC Configuration', changes: 'Setpoint changed from 22°C to 23°C'
  },
  {
    id: 'AUD004', timestamp: '2024-01-15 08:15:33', user: 'emily.w@system.com', userName: 'Emily Wong',
    action: 'access', severity: 'high', status: 'failed',
    details: 'Unauthorized access attempt to restricted zone', ip: '192.168.1.112', device: 'Desktop - Edge',
    module: 'Access Control', changes: 'Zone: Server Room (Access Denied)'
  },
  {
    id: 'AUD005', timestamp: '2024-01-14 16:20:45', user: 'david.lee@system.com', userName: 'David Lee',
    action: 'logout', severity: 'low', status: 'success',
    details: 'User logged out', ip: '192.168.1.115', device: 'Laptop - Chrome',
    module: 'Authentication', changes: null
  },
  {
    id: 'AUD006', timestamp: '2024-01-14 14:50:18', user: 'lisa.tan@system.com', userName: 'Lisa Tan',
    action: 'command', severity: 'critical', status: 'success',
    details: 'Executed system reset command', ip: '192.168.1.118', device: 'Desktop - Firefox',
    module: 'System Administration', changes: 'Command: Reset System Configuration'
  },
  {
    id: 'AUD007', timestamp: '2024-01-14 11:30:55', user: 'robert.w@system.com', userName: 'Robert Wilson',
    action: 'config', severity: 'medium', status: 'failed',
    details: 'Failed to update firmware', ip: '192.168.1.120', device: 'Laptop - Chrome',
    module: 'Device Management', changes: 'Firmware update timeout'
  },
  {
    id: 'AUD008', timestamp: '2024-01-14 09:25:30', user: 'james.w@system.com', userName: 'James Wilson',
    action: 'login', severity: 'low', status: 'failed',
    details: 'Failed login attempt', ip: '192.168.1.122', device: 'Tablet - Safari',
    module: 'Authentication', changes: 'Invalid password'
  },
  {
    id: 'AUD009', timestamp: '2024-01-13 15:40:12', user: 'admin@system.com', userName: 'System Admin',
    action: 'command', severity: 'high', status: 'success',
    details: 'Modified user permissions', ip: '192.168.1.1', device: 'Desktop - Chrome',
    module: 'User Management', changes: 'Added Admin role to john.smith'
  },
  {
    id: 'AUD010', timestamp: '2024-01-13 13:15:22', user: 'auditor@system.com', userName: 'System Auditor',
    action: 'access', severity: 'low', status: 'success',
    details: 'Audit log export', ip: '192.168.1.2', device: 'Desktop - Chrome',
    module: 'Audit', changes: 'Exported logs for Jan 1-13, 2024'
  },
  {
    id: 'AUD011', timestamp: '2024-01-13 10:55:33', user: 'operator@system.com', userName: 'System Operator',
    action: 'command', severity: 'medium', status: 'success',
    details: 'Adjusted lighting schedule', ip: '192.168.1.3', device: 'Laptop - Firefox',
    module: 'Lighting Control', changes: 'Schedule updated for Zone B'
  },
  {
    id: 'AUD012', timestamp: '2024-01-12 16:30:18', user: 'security@system.com', userName: 'Security Officer',
    action: 'access', severity: 'high', status: 'failed',
    details: 'Access to restricted area denied', ip: '192.168.1.4', device: 'Desktop - Edge',
    module: 'Access Control', changes: 'Zone: Control Room (Unauthorized)'
  }
])

// Audit statistics
const auditStats = reactive({
  total: 0,
  critical: 0,
  high: 0,
  medium: 0,
  low: 0,
  success: 0,
  failed: 0,
  uniqueUsers: 0,
  topAction: ''
})

// Export form
const exportForm = reactive({
  dateRange: 'month',
  format: 'csv',
  includeDetails: true,
  includeIp: true
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: auditLogs.value.length
})

// Filtered logs
const filteredLogs = computed(() => {
  let filtered = auditLogs.value
  if (searchKeyword.value) {
    filtered = filtered.filter(l =>
        l.userName.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        l.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        l.details.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        l.ip.includes(searchKeyword.value)
    )
  }
  if (selectedSeverity.value !== 'all') {
    filtered = filtered.filter(l => l.severity === selectedSeverity.value)
  }
  if (selectedAction.value !== 'all') {
    filtered = filtered.filter(l => l.action === selectedAction.value)
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

  auditChart = echarts.init(chartRef.value)
  auditChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c})' },
    legend: { orient: 'vertical', left: 'left', data: ['Critical', 'High', 'Medium', 'Low'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { name: 'Critical', value: auditStats.critical, itemStyle: { color: '#F56C6C' } },
        { name: 'High', value: auditStats.high, itemStyle: { color: '#F56C6C' } },
        { name: 'Medium', value: auditStats.medium, itemStyle: { color: '#E6A23C' } },
        { name: 'Low', value: auditStats.low, itemStyle: { color: '#67C23A' } }
      ],
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })
}

const updateStats = () => {
  auditStats.total = auditLogs.value.length
  auditStats.critical = auditLogs.value.filter(l => l.severity === 'critical').length
  auditStats.high = auditLogs.value.filter(l => l.severity === 'high').length
  auditStats.medium = auditLogs.value.filter(l => l.severity === 'medium').length
  auditStats.low = auditLogs.value.filter(l => l.severity === 'low').length
  auditStats.success = auditLogs.value.filter(l => l.status === 'success').length
  auditStats.failed = auditLogs.value.filter(l => l.status === 'failed').length

  const uniqueUsers = new Set(auditLogs.value.map(l => l.user)).size
  auditStats.uniqueUsers = uniqueUsers

  // Find top action
  const actionCount: Record<string, number> = {}
  auditLogs.value.forEach(l => {
    actionCount[l.action] = (actionCount[l.action] || 0) + 1
  })
  const top = Object.entries(actionCount).reduce((a, b) => a[1] > b[1] ? a : b, ['', 0])
  auditStats.topAction = top[0].charAt(0).toUpperCase() + top[0].slice(1)
}

const handleResize = () => {
  auditChart?.resize()
}

// ==================== Audit Functions ====================
const refreshAudit = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  loading.value = false
  ElMessage.success('Audit logs refreshed successfully')
}

const viewDetails = (log: any) => {
  selectedLog.value = log
  detailsVisible.value = true
}

const openExportDialog = () => {
  exportDialogVisible.value = true
}

const exportLogs = async () => {
  await new Promise(resolve => setTimeout(resolve, 1000))
  ElMessage.success(`Audit logs exported successfully in ${exportForm.format.toUpperCase()} format`)
  exportDialogVisible.value = false
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
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'success'
    default: return 'info'
  }
}

const getSeverityIcon = (severity: string) => {
  switch (severity) {
    case 'critical': return '🔴'
    case 'high': return '🟠'
    case 'medium': return '🟡'
    case 'low': return '🟢'
    default: return '⚪'
  }
}

const getActionIcon = (action: string) => {
  switch (action) {
    case 'login': return '🔐'
    case 'logout': return '🚪'
    case 'command': return '💻'
    case 'config': return '⚙️'
    case 'access': return '🚫'
    default: return '📝'
  }
}

const getStatusType = (status: string) => {
  return status === 'success' ? 'success' : 'danger'
}

const selectedLog = ref<any>(null)
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
          <span class="loading-title">Loading Audit Management</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Security & Compliance - Audit Management</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="audit-management-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Audit Management</h1>
        <p class="page-subtitle">Comprehensive audit trail for security and compliance monitoring</p>
      </div>
      <div class="header-right">
        <el-button type="primary" size="large" @click="openExportDialog">
          <el-icon><DownloadIcon /></el-icon>
          Export Logs
        </el-button>
        <el-button size="large" @click="refreshAudit" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total-icon">
          <el-icon><List /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ auditStats.total }}</div>
          <div class="stat-label">Total Events</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ auditStats.success }} Successful</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon severity-icon">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ auditStats.critical + auditStats.high }}</div>
          <div class="stat-label">High Severity</div>
        </div>
        <div class="stat-trend">
          <el-progress :percentage="((auditStats.critical + auditStats.high) / auditStats.total) * 100" :stroke-width="4" :show-text="false" color="#F56C6C" />
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon users-icon">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ auditStats.uniqueUsers }}</div>
          <div class="stat-label">Active Users</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ auditStats.failed }} Failed Attempts</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon actions-icon">
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ auditStats.topAction }}</div>
          <div class="stat-label">Most Common Action</div>
        </div>
        <div class="stat-trend">
          <span class="trend-neutral">{{ auditStats.medium }} Medium Severity</span>
        </div>
      </div>
    </div>

    <!-- Audit Chart -->
    <div class="chart-section">
      <div class="section-header">
        <h3>Audit Events by Severity</h3>
        <el-button text type="primary" @click="initChart">Refresh</el-button>
      </div>
      <div ref="chartRef" class="audit-chart" style="height: 320px"></div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-bar">
      <div class="filters-left">
        <div class="search-box">
          <el-input
              v-model="searchKeyword"
              placeholder="Search by user, IP, or details..."
              :prefix-icon="Search"
              clearable
              style="width: 260px"
          />
        </div>
        <div class="severity-filters">
          <span class="filter-label">Severity:</span>
          <button
              v-for="s in severityOptions"
              :key="s.value"
              class="severity-chip"
              :class="{ active: selectedSeverity === s.value }"
              @click="selectedSeverity = s.value"
          >
            <span class="chip-dot" :style="{ background: s.color }"></span>
            <span>{{ s.label }}</span>
          </button>
        </div>
        <div class="action-filters">
          <span class="filter-label">Action:</span>
          <button
              v-for="a in actionOptions"
              :key="a.value"
              class="action-chip"
              :class="{ active: selectedAction === a.value }"
              @click="selectedAction = a.value"
          >
            {{ a.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- Audit Logs Table -->
    <el-card shadow="never" class="audit-card">
      <template #header>
        <div class="table-header">
          <span>Audit Trail</span>
          <div class="table-actions">
            <el-tag type="info" size="small">{{ filteredLogs.length }} records found</el-tag>
          </div>
        </div>
      </template>

      <el-table :data="filteredLogs" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="timestamp" label="Timestamp" width="160" />
        <el-table-column prop="userName" label="User" width="140" />
        <el-table-column label="Action" width="110" align="center">
          <template #default="{ row }">
            <div class="action-badge">
              <span class="action-icon">{{ getActionIcon(row.action) }}</span>
              <span>{{ row.action.toUpperCase() }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Severity" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getSeverityType(row.severity)" size="small">
              {{ getSeverityIcon(row.severity) }} {{ row.severity.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ row.status.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="details" label="Details" min-width="250" />
        <el-table-column prop="ip" label="IP Address" width="130" />
        <el-table-column label="Actions" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">
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

    <!-- Audit Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="`Audit Log Details - ${selectedLog?.id}`" width="650px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Event ID">{{ selectedLog?.id }}</el-descriptions-item>
        <el-descriptions-item label="Timestamp">{{ selectedLog?.timestamp }}</el-descriptions-item>
        <el-descriptions-item label="User">{{ selectedLog?.userName }}</el-descriptions-item>
        <el-descriptions-item label="Email">{{ selectedLog?.user }}</el-descriptions-item>
        <el-descriptions-item label="Action">
          <span class="action-icon">{{ getActionIcon(selectedLog?.action) }}</span>
          {{ selectedLog?.action?.toUpperCase() }}
        </el-descriptions-item>
        <el-descriptions-item label="Severity">
          <el-tag :type="getSeverityType(selectedLog?.severity)" size="small">
            {{ selectedLog?.severity?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusType(selectedLog?.status)" size="small">
            {{ selectedLog?.status?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="IP Address">{{ selectedLog?.ip }}</el-descriptions-item>
        <el-descriptions-item label="Device">{{ selectedLog?.device }}</el-descriptions-item>
        <el-descriptions-item label="Module">{{ selectedLog?.module }}</el-descriptions-item>
        <el-descriptions-item label="Details" :span="2">{{ selectedLog?.details }}</el-descriptions-item>
        <el-descriptions-item label="Changes" :span="2">{{ selectedLog?.changes || 'No changes recorded' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Export Dialog -->
    <el-dialog v-model="exportDialogVisible" title="Export Audit Logs" width="500px">
      <el-form :model="exportForm" label-width="120px">
        <el-form-item label="Date Range">
          <el-select v-model="exportForm.dateRange" style="width: 100%">
            <el-option label="Last 24 Hours" value="day" />
            <el-option label="Last 7 Days" value="week" />
            <el-option label="Last 30 Days" value="month" />
            <el-option label="Custom Range" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="Export Format">
          <el-radio-group v-model="exportForm.format">
            <el-radio value="csv">CSV</el-radio>
            <el-radio value="json">JSON</el-radio>
            <el-radio value="pdf">PDF</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Include Details">
          <el-switch v-model="exportForm.includeDetails" />
        </el-form-item>
        <el-form-item label="Include IP Address">
          <el-switch v-model="exportForm.includeIp" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="exportDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="exportLogs">Export</el-button>
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
.audit-management-container {
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

.severity-icon {
  background: linear-gradient(135deg, #fef0f0 0%, #fcd9d9 100%);
  color: #f56c6c;
}

.users-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.actions-icon {
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

.audit-chart {
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

.severity-filters,
.action-filters {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.severity-chip,
.action-chip {
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

.severity-chip:hover,
.action-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.severity-chip.active,
.action-chip.active {
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

/* Audit Card */
.audit-card {
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
.action-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.action-icon {
  font-size: 14px;
}

/* Dialog Styles */
.roles-list,
.permissions-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .audit-management-container {
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

  .severity-filters,
  .action-filters {
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