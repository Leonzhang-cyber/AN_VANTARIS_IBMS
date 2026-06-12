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
        <div class="loading-tip">AI Audit Logs</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="ai-audit-logs-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div>
        <h1>AI Audit Logs</h1>
        <p>Track and monitor all AI system activities, decisions, and governance events</p>
      </div>
      <el-button type="primary" @click="handleExport">
        <el-icon><Download /></el-icon>
        Export Logs
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalEvents }}</div>
            <div class="stat-label">Total Events</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon danger-bg">
            <el-icon><CircleClose /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.criticalAlerts }}</div>
            <div class="stat-label">Critical Alerts</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><SuccessFilled /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.approvedActions }}</div>
            <div class="stat-label">Approved Actions</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon info-bg">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.activeAgents }}</div>
            <div class="stat-label">Active Agents</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表行 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="card-header">
            <h3>Event Trend (Last 7 Days)</h3>
            <el-select v-model="eventTrendPeriod" size="small" style="width: 120px">
              <el-option label="Last 7 Days" value="7" />
              <el-option label="Last 14 Days" value="14" />
              <el-option label="Last 30 Days" value="30" />
            </el-select>
          </div>
          <div ref="trendChartRef" class="chart-container"></div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="card-header">
            <h3>Event Distribution by Type</h3>
          </div>
          <div ref="distributionChartRef" class="chart-container"></div>
        </div>
      </el-col>
    </el-row>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-input
          v-model="filters.search"
          placeholder="Search by user, action, or resource..."
          clearable
          style="width: 280px"
          :prefix-icon="Search"
      />
      <el-select v-model="filters.eventType" placeholder="Event Type" clearable style="width: 160px">
        <el-option label="All Types" value="" />
        <el-option label="AI Decision" value="AI_DECISION" />
        <el-option label="Model Invocation" value="MODEL_INVOCATION" />
        <el-option label="Data Access" value="DATA_ACCESS" />
        <el-option label="Policy Change" value="POLICY_CHANGE" />
        <el-option label="Approval" value="APPROVAL" />
        <el-option label="Alert" value="ALERT" />
      </el-select>
      <el-select v-model="filters.severity" placeholder="Severity" clearable style="width: 140px">
        <el-option label="All Severities" value="" />
        <el-option label="Critical" value="CRITICAL" />
        <el-option label="High" value="HIGH" />
        <el-option label="Medium" value="MEDIUM" />
        <el-option label="Low" value="LOW" />
        <el-option label="Info" value="INFO" />
      </el-select>
      <el-date-picker
          v-model="filters.dateRange"
          type="daterange"
          range-separator="to"
          start-placeholder="Start Date"
          end-placeholder="End Date"
          style="width: 280px"
      />
      <el-button type="primary" @click="handleSearch">
        <el-icon><Search /></el-icon>
        Apply Filters
      </el-button>
      <el-button @click="resetFilters">
        <el-icon><RefreshLeft /></el-icon>
        Reset
      </el-button>
    </div>

    <!-- 日志表格 -->
    <div class="logs-table-wrapper">
      <el-table :data="filteredLogs" v-loading="tableLoading" stripe style="width: 100%">
        <el-table-column prop="timestamp" label="Timestamp" width="180">
          <template #default="{ row }">
            <div class="timestamp-cell">
              <el-icon><Clock /></el-icon>
              <span>{{ formatTimestamp(row.timestamp) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="eventType" label="Event Type" width="150">
          <template #default="{ row }">
            <el-tag :type="getEventTypeTagType(row.eventType)" size="small">
              {{ formatEventType(row.eventType) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="Severity" width="120">
          <template #default="{ row }">
            <el-tag :type="getSeverityTagType(row.severity)" size="small">
              {{ row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="user" label="User" width="160" />
        <el-table-column prop="action" label="Action" min-width="200" show-overflow-tooltip />
        <el-table-column prop="resource" label="Resource" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-icon v-if="row.status === 'SUCCESS'" color="#67c23a"><CircleCheck /></el-icon>
            <el-icon v-else-if="row.status === 'FAILED'" color="#f56c6c"><CircleClose /></el-icon>
            <el-icon v-else color="#e6a23c"><Loading /></el-icon>
            <span style="margin-left: 4px">{{ row.status }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Details" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="showDetail(row)">
              View
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailDialog.visible" title="Audit Log Details" width="600px">
      <el-descriptions :column="1" border v-if="detailDialog.data">
        <el-descriptions-item label="Event ID">{{ detailDialog.data.id }}</el-descriptions-item>
        <el-descriptions-item label="Timestamp">{{ formatTimestamp(detailDialog.data.timestamp) }}</el-descriptions-item>
        <el-descriptions-item label="Event Type">{{ formatEventType(detailDialog.data.eventType) }}</el-descriptions-item>
        <el-descriptions-item label="Severity">
          <el-tag :type="getSeverityTagType(detailDialog.data.severity)" size="small">
            {{ detailDialog.data.severity }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="User">{{ detailDialog.data.user }}</el-descriptions-item>
        <el-descriptions-item label="User IP">{{ detailDialog.data.userIp || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="Action">{{ detailDialog.data.action }}</el-descriptions-item>
        <el-descriptions-item label="Resource">{{ detailDialog.data.resource }}</el-descriptions-item>
        <el-descriptions-item label="Status">{{ detailDialog.data.status }}</el-descriptions-item>
        <el-descriptions-item label="Details">
          <pre class="detail-payload">{{ JSON.stringify(detailDialog.data.details, null, 2) }}</pre>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailDialog.visible = false">Close</el-button>
        <el-button type="primary" @click="copyToClipboard">Copy to Clipboard</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Download,
  Warning,
  CircleClose,
  SuccessFilled,
  Connection,
  Search,
  RefreshLeft,
  Clock,
  CircleCheck,
  Loading
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing...',
  'Almost ready...'
]

// ==================== 模拟数据生成 ====================
const generateMockLogs = (count = 150) => {
  const eventTypes = ['AI_DECISION', 'MODEL_INVOCATION', 'DATA_ACCESS', 'POLICY_CHANGE', 'APPROVAL', 'ALERT']
  const severities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']
  const users = ['john.doe@ibms.com', 'jane.smith@ibms.com', 'alex.chen@ibms.com', 'sarah.wang@ibms.com', 'system.agent@ibms.com', 'admin@ibms.com']
  const actions = {
    AI_DECISION: ['Generated recommendation', 'Executed autonomous action', 'Flagged anomaly', 'Created insight'],
    MODEL_INVOCATION: ['Invoked predictive maintenance model', 'Called energy optimization model', 'Ran fault diagnosis model', 'Executed occupancy prediction'],
    DATA_ACCESS: ['Retrieved device telemetry', 'Accessed historical alarms', 'Queried energy consumption data', 'Fetched asset registry'],
    POLICY_CHANGE: ['Updated AI approval threshold', 'Modified model version policy', 'Changed data retention rule', 'Updated governance policy'],
    APPROVAL: ['Approved AI recommendation', 'Rejected autonomous action', 'Requested review', 'Overrode AI decision'],
    ALERT: ['Model drift detected', 'Data quality issue', 'API rate limit exceeded', 'Model latency spike']
  }
  const resources = [
    '/models/predictive-maintenance/v2', '/models/energy-optimization/v1', '/data/telemetry/hvac',
    '/policies/ai-governance', '/workflows/approval-matrix', '/agents/digital-operator',
    '/api/decisions/recommendation', '/alerts/model-drift', '/audit/decision-trace'
  ]

  const logs = []
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - 30)

  for (let i = 0; i < count; i++) {
    const eventType = eventTypes[Math.floor(Math.random() * eventTypes.length)]
    const severity = severities[Math.floor(Math.random() * severities.length)]
    const timestamp = new Date(startDate.getTime() + Math.random() * 30 * 24 * 60 * 60 * 1000)
    const status = Math.random() > 0.1 ? 'SUCCESS' : (Math.random() > 0.5 ? 'FAILED' : 'PENDING')

    logs.push({
      id: `LOG-${String(i + 1).padStart(6, '0')}`,
      timestamp,
      eventType,
      severity,
      user: users[Math.floor(Math.random() * users.length)],
      action: actions[eventType][Math.floor(Math.random() * actions[eventType].length)],
      resource: resources[Math.floor(Math.random() * resources.length)],
      status,
      userIp: `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
      details: {
        requestId: `req_${Math.random().toString(36).substring(2, 10)}`,
        modelVersion: `v${Math.floor(Math.random() * 5) + 1}.${Math.floor(Math.random() * 10)}`,
        executionTimeMs: Math.floor(Math.random() * 500),
        confidenceScore: Math.random().toFixed(2),
        inputTokens: Math.floor(Math.random() * 1000),
        outputTokens: Math.floor(Math.random() * 500)
      }
    })
  }

  return logs.sort((a, b) => b.timestamp - a.timestamp)
}

// ==================== 响应式状态 ====================
const allLogs = ref<any[]>([])
const trendChartRef = ref<HTMLElement | null>(null)
const distributionChartRef = ref<HTMLElement | null>(null)
let trendChart: echarts.ECharts | null = null
let distributionChart: echarts.ECharts | null = null

const eventTrendPeriod = ref('7')

const filters = reactive({
  search: '',
  eventType: '',
  severity: '',
  dateRange: null as Date[] | null
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

const detailDialog = reactive({
  visible: false,
  data: null as any
})

// 统计数据
const stats = reactive({
  totalEvents: 0,
  criticalAlerts: 0,
  approvedActions: 0,
  activeAgents: 0
})

// ==================== 计算属性 ====================
const filteredLogs = computed(() => {
  let filtered = [...allLogs.value]

  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    filtered = filtered.filter(log =>
        log.user.toLowerCase().includes(searchLower) ||
        log.action.toLowerCase().includes(searchLower) ||
        log.resource.toLowerCase().includes(searchLower)
    )
  }

  if (filters.eventType) {
    filtered = filtered.filter(log => log.eventType === filters.eventType)
  }

  if (filters.severity) {
    filtered = filtered.filter(log => log.severity === filters.severity)
  }

  if (filters.dateRange && filters.dateRange.length === 2) {
    const [start, end] = filters.dateRange
    filtered = filtered.filter(log => {
      const logDate = new Date(log.timestamp)
      return logDate >= start && logDate <= end
    })
  }

  pagination.total = filtered.length

  const start = (pagination.currentPage - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// ==================== 辅助函数 ====================
const formatTimestamp = (timestamp: Date) => {
  return new Date(timestamp).toLocaleString('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const formatEventType = (type: string) => {
  const map: Record<string, string> = {
    'AI_DECISION': 'AI Decision',
    'MODEL_INVOCATION': 'Model Invocation',
    'DATA_ACCESS': 'Data Access',
    'POLICY_CHANGE': 'Policy Change',
    'APPROVAL': 'Approval',
    'ALERT': 'Alert'
  }
  return map[type] || type
}

const getEventTypeTagType = (type: string) => {
  const map: Record<string, string> = {
    'AI_DECISION': 'primary',
    'MODEL_INVOCATION': 'success',
    'DATA_ACCESS': 'info',
    'POLICY_CHANGE': 'warning',
    'APPROVAL': 'success',
    'ALERT': 'danger'
  }
  return map[type] || 'info'
}

const getSeverityTagType = (severity: string) => {
  const map: Record<string, string> = {
    'CRITICAL': 'danger',
    'HIGH': 'danger',
    'MEDIUM': 'warning',
    'LOW': 'info',
    'INFO': ''
  }
  return map[severity] || 'info'
}

const updateStats = () => {
  const logs = allLogs.value
  stats.totalEvents = logs.length
  stats.criticalAlerts = logs.filter(l => l.severity === 'CRITICAL').length
  stats.approvedActions = logs.filter(l => l.eventType === 'APPROVAL' && l.action.includes('Approved')).length
  stats.activeAgents = 8
}

// ==================== 图表渲染 ====================
const renderTrendChart = () => {
  if (!trendChartRef.value) return

  if (trendChart) {
    trendChart.dispose()
  }

  trendChart = echarts.init(trendChartRef.value)

  const days = parseInt(eventTrendPeriod.value)
  const dates = []
  const decisionData = []
  const invocationData = []
  const alertData = []

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    dates.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }))

    decisionData.push(Math.floor(Math.random() * 30) + 10)
    invocationData.push(Math.floor(Math.random() * 25) + 5)
    alertData.push(Math.floor(Math.random() * 15) + 2)
  }

  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['AI Decisions', 'Model Invocations', 'Alerts'], bottom: 0 },
    grid: { left: '3%', right: '4%', top: '10%', bottom: '12%', containLabel: true },
    xAxis: { type: 'category', data: dates, axisLabel: { rotate: 45 } },
    yAxis: { type: 'value', name: 'Event Count' },
    series: [
      { name: 'AI Decisions', type: 'line', smooth: true, data: decisionData, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Model Invocations', type: 'line', smooth: true, data: invocationData, lineStyle: { color: '#67c23a', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Alerts', type: 'line', smooth: true, data: alertData, lineStyle: { color: '#e6a23c', width: 2 }, areaStyle: { opacity: 0.1 } }
    ]
  })
}

const renderDistributionChart = () => {
  if (!distributionChartRef.value) return

  if (distributionChart) {
    distributionChart.dispose()
  }

  distributionChart = echarts.init(distributionChartRef.value)

  const distribution = {
    'AI Decision': allLogs.value.filter(l => l.eventType === 'AI_DECISION').length,
    'Model Invocation': allLogs.value.filter(l => l.eventType === 'MODEL_INVOCATION').length,
    'Data Access': allLogs.value.filter(l => l.eventType === 'DATA_ACCESS').length,
    'Policy Change': allLogs.value.filter(l => l.eventType === 'POLICY_CHANGE').length,
    'Approval': allLogs.value.filter(l => l.eventType === 'APPROVAL').length,
    'Alert': allLogs.value.filter(l => l.eventType === 'ALERT').length
  }

  distributionChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} events)' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '55%'],
      data: Object.entries(distribution).map(([name, value]) => ({ name, value })),
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })
}

// ==================== 交互事件 ====================
const handleSearch = () => {
  pagination.currentPage = 1
  ElMessage.success('Filters applied successfully')
}

const resetFilters = () => {
  filters.search = ''
  filters.eventType = ''
  filters.severity = ''
  filters.dateRange = null
  pagination.currentPage = 1
  ElMessage.info('All filters have been reset')
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.currentPage = 1
}

const handleCurrentChange = (page: number) => {
  pagination.currentPage = page
}

const showDetail = (row: any) => {
  detailDialog.data = row
  detailDialog.visible = true
}

const copyToClipboard = async () => {
  if (!detailDialog.data) return
  try {
    await navigator.clipboard.writeText(JSON.stringify(detailDialog.data, null, 2))
    ElMessage.success('Event details copied to clipboard')
  } catch {
    ElMessage.error('Failed to copy to clipboard')
  }
}

const handleExport = () => {
  const data = JSON.stringify(filteredLogs.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `ai-audit-logs-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Logs exported successfully')
}

// ==================== 数据加载 ====================
const loadData = () => {
  tableLoading.value = true
  setTimeout(() => {
    allLogs.value = generateMockLogs(180)
    updateStats()
    tableLoading.value = false
    renderTrendChart()
    renderDistributionChart()
  }, 300)
}

// ==================== 生命周期 ====================
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
      loadData()
    }, 400)
  }, 2000)
})

// 监听周期变化刷新图表
watch(eventTrendPeriod, () => {
  renderTrendChart()
})

// 监听数据变化刷新分布图
watch(allLogs, () => {
  renderDistributionChart()
  updateStats()
}, { deep: true })

// 响应窗口大小变化
const handleResize = () => {
  trendChart?.resize()
  distributionChart?.resize()
}

watch(isLoaded, (loaded) => {
  if (loaded) {
    window.addEventListener('resize', handleResize)
  }
})
</script>

<style scoped>
/* ==================== Loading Screen (from user) ==================== */
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

/* ==================== Main Content Styles ==================== */
.ai-audit-logs-page {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #1f2f3d;
}

.page-header p {
  margin: 0;
  color: #5e6e82;
  font-size: 14px;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
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

.warning-bg { background-color: #fff3e0; color: #e6a23c; }
.danger-bg { background-color: #fef0f0; color: #f56c6c; }
.success-bg { background-color: #f0f9eb; color: #67c23a; }
.info-bg { background-color: #ecf5ff; color: #409eff; }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #8c9aab;
  margin-top: 4px;
}

.charts-row {
  margin-bottom: 24px;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.chart-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-card h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

.chart-container {
  height: 300px;
  width: 100%;
}

.filter-bar {
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.logs-table-wrapper {
  background: white;
  border-radius: 12px;
  padding: 0;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.timestamp-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #5e6e82;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 16px 20px;
  border-top: 1px solid #ebeef5;
}

.detail-payload {
  background-color: #f5f7fa;
  padding: 12px;
  border-radius: 8px;
  font-size: 12px;
  overflow-x: auto;
  max-height: 300px;
  margin: 0;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
  color: #1f2f3d;
}

:deep(.el-table td) {
  font-size: 13px;
}

:deep(.el-dialog__body) {
  padding-top: 0;
}
</style>