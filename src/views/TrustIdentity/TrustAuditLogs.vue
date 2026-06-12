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
        <div class="loading-tip">Trust & Identity - Trust Audit Logs</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="trust-audit-logs-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Trust Audit Logs</h1>
        <p>Complete audit trail of all trust operations, credential events, and blockchain transactions</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="exportLogs">
          <el-icon><Download /></el-icon>
          Export Logs
        </el-button>
        <el-button @click="refreshLogs">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon primary-bg">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalEvents }}</div>
            <div class="stat-label">Total Events</div>
            <div class="stat-trend">+{{ stats.newThisWeek }} this week</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.successEvents }}%</div>
            <div class="stat-label">Success Rate</div>
            <div class="stat-trend">↑ 2.3% from last month</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.criticalEvents }}</div>
            <div class="stat-label">Critical Events</div>
            <div class="stat-trend">↓ 15% reduction</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon info-bg">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.retentionDays }}d</div>
            <div class="stat-label">Retention Period</div>
            <div class="stat-trend">Compliant with policy</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Event Distribution Chart -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="card-header">
            <h3>Event Distribution by Type</h3>
            <el-select v-model="eventPeriod" size="small" style="width: 120px">
              <el-option label="Last 7 Days" value="7" />
              <el-option label="Last 30 Days" value="30" />
              <el-option label="Last 90 Days" value="90" />
            </el-select>
          </div>
          <div ref="distributionChartRef" class="chart-container"></div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="card-header">
            <h3>Event Trend Over Time</h3>
          </div>
          <div ref="trendChartRef" class="chart-container"></div>
        </div>
      </el-col>
    </el-row>

    <!-- Search & Filter -->
    <div class="filter-bar">
      <el-input
          v-model="filters.search"
          placeholder="Search by event ID, user, or description..."
          clearable
          style="width: 260px"
          :prefix-icon="Search"
      />
      <el-select v-model="filters.eventType" placeholder="Event Type" clearable style="width: 160px">
        <el-option label="All Types" value="" />
        <el-option label="Credential Issuance" value="credential_issue" />
        <el-option label="Credential Revocation" value="credential_revoke" />
        <el-option label="Certificate Upload" value="certificate_upload" />
        <el-option label="Certificate Verification" value="certificate_verify" />
        <el-option label="Blockchain Anchor" value="blockchain_anchor" />
        <el-option label="Smart Contract" value="smart_contract" />
        <el-option label="Access Control" value="access_control" />
      </el-select>
      <el-select v-model="filters.severity" placeholder="Severity" clearable style="width: 130px">
        <el-option label="All Severities" value="" />
        <el-option label="Critical" value="critical" />
        <el-option label="High" value="high" />
        <el-option label="Medium" value="medium" />
        <el-option label="Low" value="low" />
        <el-option label="Info" value="info" />
      </el-select>
      <el-select v-model="filters.status" placeholder="Status" clearable style="width: 120px">
        <el-option label="All" value="" />
        <el-option label="Success" value="success" />
        <el-option label="Failed" value="failed" />
        <el-option label="Pending" value="pending" />
      </el-select>
      <el-date-picker
          v-model="filters.dateRange"
          type="datetimerange"
          range-separator="to"
          start-placeholder="Start Date"
          end-placeholder="End Date"
          style="width: 360px"
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

    <!-- Audit Logs Table -->
    <div class="audit-table-wrapper">
      <el-table :data="filteredLogs" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="timestamp" label="Timestamp" width="180">
          <template #default="{ row }">
            <div class="timestamp-cell">
              <el-icon><Clock /></el-icon>
              <span>{{ row.timestamp }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="eventId" label="Event ID" width="140" />
        <el-table-column prop="eventType" label="Event Type" width="160">
          <template #default="{ row }">
            <el-tag :type="getEventTagType(row.eventType)" size="small">
              {{ formatEventType(row.eventType) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityTagType(row.severity)" size="small">
              {{ row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="user" label="User / Actor" width="160" />
        <el-table-column prop="action" label="Action" min-width="200" show-overflow-tooltip />
        <el-table-column prop="resource" label="Resource" min-width="180" show-overflow-tooltip />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : row.status === 'failed' ? 'danger' : 'warning'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Details" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewLogDetail(row)">
              View
            </el-button>
          </template>
        </el-table-column>
      </el-table>

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

    <!-- Log Detail Dialog -->
    <el-dialog v-model="detailDialog.visible" title="Audit Log Details" width="700px">
      <div v-if="detailDialog.log" class="log-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Event ID">{{ detailDialog.log.eventId }}</el-descriptions-item>
          <el-descriptions-item label="Timestamp">{{ detailDialog.log.timestamp }}</el-descriptions-item>
          <el-descriptions-item label="Event Type">{{ formatEventType(detailDialog.log.eventType) }}</el-descriptions-item>
          <el-descriptions-item label="Severity">
            <el-tag :type="getSeverityTagType(detailDialog.log.severity)">{{ detailDialog.log.severity }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="detailDialog.log.status === 'success' ? 'success' : 'danger'">{{ detailDialog.log.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="User / Actor">{{ detailDialog.log.user }}</el-descriptions-item>
          <el-descriptions-item label="Source IP">{{ detailDialog.log.sourceIp || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Action">{{ detailDialog.log.action }}</el-descriptions-item>
          <el-descriptions-item label="Resource">{{ detailDialog.log.resource }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ detailDialog.log.description }}</el-descriptions-item>
          <el-descriptions-item label="Blockchain Reference" :span="2" v-if="detailDialog.log.txHash">
            <code>{{ detailDialog.log.txHash }}</code>
            <el-button link size="small" @click="viewOnExplorer(detailDialog.log.txHash)">View on Explorer</el-button>
          </el-descriptions-item>
          <el-descriptions-item label="Additional Data" :span="2" v-if="detailDialog.log.metadata">
            <pre class="metadata-preview">{{ JSON.stringify(detailDialog.log.metadata, null, 2) }}</pre>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- Compliance Status Card -->
    <div class="compliance-card">
      <div class="card-header">
        <h3>Audit Compliance Status</h3>
        <el-tag type="success">Compliant</el-tag>
      </div>
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="compliance-item">
            <div class="compliance-label">Log Integrity</div>
            <el-progress :percentage="100" :stroke-width="8" color="#67c23a" />
            <div class="compliance-detail">All logs cryptographically signed</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="compliance-item">
            <div class="compliance-label">Retention Compliance</div>
            <el-progress :percentage="100" :stroke-width="8" color="#67c23a" />
            <div class="compliance-detail">7 years retention policy enforced</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="compliance-item">
            <div class="compliance-label">Audit Trail</div>
            <el-progress :percentage="98" :stroke-width="8" color="#67c23a" />
            <div class="compliance-detail">Complete chain of custody</div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Download,
  Refresh,
  Document,
  CircleCheck,
  Warning,
  DataAnalysis,
  Search,
  RefreshLeft,
  Clock
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading audit logs...',
  'Verifying log integrity...',
  'Almost ready...'
]

// ==================== 类型定义 ====================
interface AuditLog {
  eventId: string
  timestamp: string
  eventType: string
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info'
  user: string
  action: string
  resource: string
  status: 'success' | 'failed' | 'pending'
  description: string
  sourceIp?: string
  txHash?: string
  metadata?: Record<string, any>
}

// ==================== 模拟数据生成 ====================
const generateMockLogs = (count: number = 150): AuditLog[] => {
  const eventTypes = [
    'credential_issue', 'credential_revoke', 'certificate_upload',
    'certificate_verify', 'blockchain_anchor', 'smart_contract', 'access_control'
  ]
  const severities = ['critical', 'high', 'medium', 'low', 'info']
  const users = ['john.smith@ibms.com', 'sarah.lee@ibms.com', 'mike.chen@ibms.com', 'admin@ibms.com', 'system@ibms.com']
  const actions = {
    credential_issue: ['Issued new verifiable credential', 'Bulk credential issuance', 'Credential renewal'],
    credential_revoke: ['Revoked credential', 'Bulk revocation', 'Credential suspension'],
    certificate_upload: ['Uploaded compliance certificate', 'Certificate renewal', 'Certificate update'],
    certificate_verify: ['Verified certificate', 'Chain verification', 'Hash comparison'],
    blockchain_anchor: ['Anchored hash to blockchain', 'Transaction confirmed', 'Anchor verification'],
    smart_contract: ['Deployed contract', 'Contract interaction', 'Contract upgrade'],
    access_control: ['Role assigned', 'Permission granted', 'Access request approved']
  }

  const logs: AuditLog[] = []
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - 90)

  for (let i = 0; i < count; i++) {
    const eventType = eventTypes[Math.floor(Math.random() * eventTypes.length)]
    const severity = severities[Math.floor(Math.random() * severities.length)]
    const timestamp = new Date(startDate.getTime() + Math.random() * 90 * 24 * 60 * 60 * 1000)
    const status = Math.random() > 0.1 ? 'success' : (Math.random() > 0.5 ? 'failed' : 'pending')

    logs.push({
      eventId: `EVT-${String(i + 1).padStart(6, '0')}`,
      timestamp: timestamp.toLocaleString(),
      eventType,
      severity: severity as any,
      user: users[Math.floor(Math.random() * users.length)],
      action: actions[eventType][Math.floor(Math.random() * actions[eventType].length)],
      resource: `/trust/${eventType}/${Math.random().toString(36).substring(2, 10)}`,
      status: status as any,
      description: `${actions[eventType][Math.floor(Math.random() * actions[eventType].length)]} operation completed`,
      sourceIp: `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
      txHash: Math.random() > 0.7 ? `0x${Math.random().toString(36).substring(2, 15)}` : undefined,
      metadata: {
        requestId: `req_${Math.random().toString(36).substring(2, 10)}`,
        durationMs: Math.floor(Math.random() * 500),
        details: { key: 'value' }
      }
    })
  }

  return logs.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
}

// ==================== 响应式状态 ====================
const allLogs = ref<AuditLog[]>([])
const eventPeriod = ref('30')
const distributionChartRef = ref<HTMLElement | null>(null)
const trendChartRef = ref<HTMLElement | null>(null)

let distributionChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null

const filters = reactive({
  search: '',
  eventType: '',
  severity: '',
  status: '',
  dateRange: null as Date[] | null
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

const stats = reactive({
  totalEvents: 0,
  newThisWeek: 0,
  successEvents: 0,
  criticalEvents: 0,
  retentionDays: 2555
})

const detailDialog = reactive({
  visible: false,
  log: null as AuditLog | null
})

// ==================== 计算属性 ====================
const filteredLogs = computed(() => {
  let filtered = [...allLogs.value]

  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    filtered = filtered.filter(log =>
        log.eventId.toLowerCase().includes(searchLower) ||
        log.user.toLowerCase().includes(searchLower) ||
        log.action.toLowerCase().includes(searchLower) ||
        log.description.toLowerCase().includes(searchLower)
    )
  }

  if (filters.eventType) {
    filtered = filtered.filter(log => log.eventType === filters.eventType)
  }

  if (filters.severity) {
    filtered = filtered.filter(log => log.severity === filters.severity)
  }

  if (filters.status) {
    filtered = filtered.filter(log => log.status === filters.status)
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
const formatEventType = (type: string) => {
  const map: Record<string, string> = {
    'credential_issue': 'Credential Issuance',
    'credential_revoke': 'Credential Revocation',
    'certificate_upload': 'Certificate Upload',
    'certificate_verify': 'Certificate Verification',
    'blockchain_anchor': 'Blockchain Anchor',
    'smart_contract': 'Smart Contract',
    'access_control': 'Access Control'
  }
  return map[type] || type
}

const getEventTagType = (type: string) => {
  const map: Record<string, string> = {
    'credential_issue': 'success',
    'credential_revoke': 'danger',
    'certificate_upload': 'primary',
    'certificate_verify': 'success',
    'blockchain_anchor': 'info',
    'smart_contract': 'warning',
    'access_control': 'primary'
  }
  return map[type] || 'info'
}

const getSeverityTagType = (severity: string) => {
  const map: Record<string, string> = {
    'critical': 'danger',
    'high': 'danger',
    'medium': 'warning',
    'low': 'info',
    'info': ''
  }
  return map[severity] || 'info'
}

const updateStats = () => {
  stats.totalEvents = allLogs.value.length
  const successCount = allLogs.value.filter(l => l.status === 'success').length
  stats.successEvents = Math.round((successCount / stats.totalEvents) * 100)
  stats.criticalEvents = allLogs.value.filter(l => l.severity === 'critical').length

  const oneWeekAgo = new Date()
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)
  stats.newThisWeek = allLogs.value.filter(l => new Date(l.timestamp) >= oneWeekAgo).length
}

// ==================== 图表渲染 ====================
const renderDistributionChart = () => {
  if (!distributionChartRef.value) return
  if (distributionChart) distributionChart.dispose()

  distributionChart = echarts.init(distributionChartRef.value)

  const typeCount: Record<string, number> = {}
  allLogs.value.forEach(log => {
    const formatted = formatEventType(log.eventType)
    typeCount[formatted] = (typeCount[formatted] || 0) + 1
  })

  distributionChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} events)' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '55%'],
      data: Object.entries(typeCount).map(([name, value]) => ({ name, value })),
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })
}

const renderTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)

  const days = parseInt(eventPeriod.value)
  const dates: string[] = []
  const successData: number[] = []
  const failedData: number[] = []

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    dates.push(dateStr)

    const dayStart = new Date(date)
    dayStart.setHours(0, 0, 0, 0)
    const dayEnd = new Date(date)
    dayEnd.setHours(23, 59, 59, 999)

    const dayLogs = allLogs.value.filter(l => {
      const logDate = new Date(l.timestamp)
      return logDate >= dayStart && logDate <= dayEnd
    })

    successData.push(dayLogs.filter(l => l.status === 'success').length)
    failedData.push(dayLogs.filter(l => l.status === 'failed').length)
  }

  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Success', 'Failed'], bottom: 0 },
    grid: { left: '3%', right: '4%', top: '10%', bottom: '12%', containLabel: true },
    xAxis: { type: 'category', data: dates, axisLabel: { rotate: 45 } },
    yAxis: { type: 'value', name: 'Event Count' },
    series: [
      { name: 'Success', type: 'line', smooth: true, data: successData, lineStyle: { color: '#67c23a', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Failed', type: 'line', smooth: true, data: failedData, lineStyle: { color: '#f56c6c', width: 2 }, areaStyle: { opacity: 0.1 } }
    ]
  })
}

// ==================== 交互事件 ====================
const handleSearch = () => {
  pagination.currentPage = 1
  ElMessage.success('Filters applied')
}

const resetFilters = () => {
  filters.search = ''
  filters.eventType = ''
  filters.severity = ''
  filters.status = ''
  filters.dateRange = null
  pagination.currentPage = 1
  ElMessage.info('Filters reset')
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.currentPage = 1
}

const handleCurrentChange = (page: number) => {
  pagination.currentPage = page
}

const viewLogDetail = (log: AuditLog) => {
  detailDialog.log = log
  detailDialog.visible = true
}

const viewOnExplorer = (txHash: string) => {
  window.open(`https://etherscan.io/tx/${txHash}`, '_blank')
}

const exportLogs = () => {
  const exportData = {
    generatedAt: new Date().toISOString(),
    summary: stats,
    logs: filteredLogs.value
  }
  const data = JSON.stringify(exportData, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `trust-audit-logs-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Logs exported successfully')
}

const refreshLogs = () => {
  tableLoading.value = true
  setTimeout(() => {
    allLogs.value = generateMockLogs(180)
    updateStats()
    renderDistributionChart()
    renderTrendChart()
    tableLoading.value = false
    ElMessage.success('Logs refreshed')
  }, 500)
}

// ==================== 数据加载 ====================
const loadData = () => {
  allLogs.value = generateMockLogs(180)
  updateStats()
  nextTick(() => {
    renderDistributionChart()
    renderTrendChart()
  })
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

onUnmounted(() => {
  window.removeEventListener('resize', () => {
    distributionChart?.resize()
    trendChart?.resize()
  })
})

watch(eventPeriod, () => renderTrendChart())
</script>

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

/* ==================== Main Content Styles ==================== */
.trust-audit-logs-page {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
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

.header-actions {
  display: flex;
  gap: 12px;
}

/* Stats Cards */
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

.primary-bg { background-color: #ecf5ff; color: #409eff; }
.success-bg { background-color: #f0f9eb; color: #67c23a; }
.warning-bg { background-color: #fff3e0; color: #e6a23c; }
.info-bg { background-color: #f5f7fa; color: #8c9aab; }

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

.stat-trend {
  font-size: 11px;
  color: #8c9aab;
  margin-top: 2px;
}

/* Charts */
.charts-row {
  margin-bottom: 24px;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

.chart-container {
  height: 280px;
  width: 100%;
}

/* Filter Bar */
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

/* Audit Table */
.audit-table-wrapper {
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
  font-size: 12px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 16px 20px;
  border-top: 1px solid #ebeef5;
}

/* Log Detail */
.log-detail {
  padding: 8px 0;
}

.metadata-preview {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 8px;
  font-size: 12px;
  overflow-x: auto;
  max-height: 200px;
  margin: 0;
}

/* Compliance Card */
.compliance-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-top: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.compliance-item {
  padding: 8px;
}

.compliance-label {
  font-weight: 500;
  margin-bottom: 8px;
  font-size: 13px;
}

.compliance-detail {
  font-size: 11px;
  color: #8c9aab;
  margin-top: 6px;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
  color: #1f2f3d;
}

:deep(.el-table td) {
  font-size: 13px;
}
</style>