<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, Refresh, View, Edit, Delete, Monitor, Connection,
  User, Warning, Clock, Cpu, DataLine, Message, Upload, Download,
  Setting, Document, Checked, Bell, TrendCharts,
  List, Odometer, Location, Link, Share, VideoCamera, Lock,
  CopyDocument, Switch, Filter, MagicStick, Tickets, Right,
  Sort, FolderOpened, Files, DocumentAdd, Timer, Aim, DataAnalysis,
  Key, Grid, Collection, Platform, Service,
  Notification, Guide
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing webhook engine...',
  'Loading subscriptions...',
  'Almost ready...'
]

// ==================== Chart Refs ====================
const deliveryChart = ref<HTMLElement | null>(null)
const statusChart = ref<HTMLElement | null>(null)
const latencyChart = ref<HTMLElement | null>(null)

// ==================== State ====================
const activeTab = ref('webhooks')
const searchKeyword = ref('')
const statusFilter = ref('')
const eventTypeFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(15)
const webhookDialogVisible = ref(false)
const deliveryDialogVisible = ref(false)
const logDialogVisible = ref(false)
const testDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const selectedWebhook = ref<any>(null)
const webhookFormRef = ref()
const testing = ref(false)
const testResult = ref<any>(null)
const testPayload = ref('')

// ==================== Statistics ====================
const statistics = reactive({
  totalWebhooks: 18,
  activeWebhooks: 14,
  totalDeliveries: 12580,
  successRate: 96.8,
  avgResponseTime: 245,
  failedDeliveries: 402
})

// ==================== Webhook Data ====================
interface WebhookEndpoint {
  id: number
  name: string
  url: string
  description: string
  events: string[]
  status: 'active' | 'inactive' | 'error'
  format: 'json' | 'xml' | 'form'
  headers: Record<string, string>
  retryCount: number
  timeout: number
  createdAt: string
  updatedAt: string
  lastTriggered: string
  successCount: number
  failureCount: number
  secret?: string
}

const webhooks = ref<WebhookEndpoint[]>([
  {
    id: 1,
    name: 'Slack Alert Webhook',
    url: 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXX',
    description: 'Send alerts and notifications to Slack channel',
    events: ['alert.created', 'alert.acknowledged', 'alert.resolved'],
    status: 'active',
    format: 'json',
    headers: { 'Content-Type': 'application/json' },
    retryCount: 3,
    timeout: 5,
    createdAt: '2024-01-10',
    updatedAt: '2024-01-15',
    lastTriggered: '2024-01-15 10:23:45',
    successCount: 1256,
    failureCount: 23,
    secret: 'whsec_abc123def456'
  },
  {
    id: 2,
    name: 'Device Status Callback',
    url: 'https://api.example.com/webhooks/device-status',
    description: 'Receive device status change notifications',
    events: ['device.online', 'device.offline', 'device.error'],
    status: 'active',
    format: 'json',
    headers: { 'Content-Type': 'application/json', 'X-API-Key': '***' },
    retryCount: 5,
    timeout: 10,
    createdAt: '2024-01-12',
    updatedAt: '2024-01-14',
    lastTriggered: '2024-01-15 09:15:22',
    successCount: 3421,
    failureCount: 89,
    secret: 'whsec_xyz789ghi012'
  },
  {
    id: 3,
    name: 'Telemetry Data Forwarder',
    url: 'https://data-collector.example.com/ingest',
    description: 'Forward telemetry data to external analytics platform',
    events: ['telemetry.received', 'telemetry.batch'],
    status: 'active',
    format: 'json',
    headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ***' },
    retryCount: 3,
    timeout: 30,
    createdAt: '2024-01-08',
    updatedAt: '2024-01-13',
    lastTriggered: '2024-01-15 10:30:18',
    successCount: 5234,
    failureCount: 156,
    secret: 'whsec_jkl345mno678'
  },
  {
    id: 4,
    name: 'Maintenance Workflow',
    url: 'https://workflow.example.com/trigger',
    description: 'Trigger maintenance workflows for alerts',
    events: ['alert.critical', 'maintenance.required'],
    status: 'inactive',
    format: 'json',
    headers: { 'Content-Type': 'application/json' },
    retryCount: 2,
    timeout: 15,
    createdAt: '2024-01-05',
    updatedAt: '2024-01-10',
    lastTriggered: '2024-01-14 14:20:33',
    successCount: 89,
    failureCount: 12,
    secret: 'whsec_pqr901stu234'
  },
  {
    id: 5,
    name: 'Email Notification Service',
    url: 'https://email-api.example.com/send',
    description: 'Send email notifications for important events',
    events: ['user.action', 'report.generated', 'alert.warning'],
    status: 'active',
    format: 'json',
    headers: { 'Content-Type': 'application/json', 'X-Service-ID': 'webhook-01' },
    retryCount: 3,
    timeout: 8,
    createdAt: '2024-01-15',
    updatedAt: '2024-01-15',
    lastTriggered: '2024-01-15 10:15:45',
    successCount: 234,
    failureCount: 8,
    secret: 'whsec_vwx678yza901'
  },
  {
    id: 6,
    name: 'SIEM Integration',
    url: 'https://siem.company.com/webhook',
    description: 'Forward security events to SIEM platform',
    events: ['security.intrusion', 'security.anomaly', 'audit.log'],
    status: 'error',
    format: 'json',
    headers: { 'Content-Type': 'application/json' },
    retryCount: 5,
    timeout: 20,
    createdAt: '2024-01-03',
    updatedAt: '2024-01-09',
    lastTriggered: '2024-01-14 08:45:12',
    successCount: 567,
    failureCount: 234,
    secret: 'whsec_bcd234efg567'
  }
])

// ==================== Event Types ====================
const eventTypes = [
  'alert.created', 'alert.acknowledged', 'alert.resolved', 'alert.critical',
  'device.online', 'device.offline', 'device.error', 'device.created',
  'telemetry.received', 'telemetry.batch', 'telemetry.threshold',
  'maintenance.required', 'maintenance.completed',
  'user.action', 'user.login', 'user.logout',
  'report.generated', 'report.scheduled',
  'security.intrusion', 'security.anomaly', 'audit.log',
  'system.startup', 'system.shutdown', 'system.error'
]

// ==================== Delivery History ====================
const deliveryHistory = ref([
  { id: 1, timestamp: '2024-01-15 10:23:45', webhookName: 'Slack Alert', event: 'alert.created', status: 'success', responseTime: 234, statusCode: 200, retryCount: 0 },
  { id: 2, timestamp: '2024-01-15 10:20:12', webhookName: 'Device Status', event: 'device.online', status: 'success', responseTime: 156, statusCode: 200, retryCount: 0 },
  { id: 3, timestamp: '2024-01-15 10:15:33', webhookName: 'Telemetry Forward', event: 'telemetry.received', status: 'failed', responseTime: 0, statusCode: 500, retryCount: 3 },
  { id: 4, timestamp: '2024-01-15 10:10:22', webhookName: 'Email Service', event: 'alert.warning', status: 'success', responseTime: 345, statusCode: 200, retryCount: 0 },
  { id: 5, timestamp: '2024-01-15 10:05:18', webhookName: 'SIEM Integration', event: 'security.anomaly', status: 'failed', responseTime: 0, statusCode: 404, retryCount: 5 }
])

// ==================== Webhook Logs ====================
const webhookLogs = ref([
  { id: 1, timestamp: '2024-01-15 10:23:45', webhookId: 1, level: 'INFO', message: 'Webhook delivered successfully', details: 'Response time: 234ms' },
  { id: 2, timestamp: '2024-01-15 10:20:12', webhookId: 2, level: 'INFO', message: 'Webhook delivered successfully', details: 'Response time: 156ms' },
  { id: 3, timestamp: '2024-01-15 10:15:33', webhookId: 3, level: 'ERROR', message: 'Delivery failed after 3 retries', details: 'Status code: 500 - Internal Server Error' },
  { id: 4, timestamp: '2024-01-15 10:10:22', webhookId: 5, level: 'WARN', message: 'High response time detected', details: 'Response time: 2345ms (exceeds threshold)' },
  { id: 5, timestamp: '2024-01-15 10:05:18', webhookId: 6, level: 'ERROR', message: 'Endpoint unreachable', details: 'Connection timeout after 30s' }
])

// ==================== Form Models ====================
const newWebhook = ref({
  name: '',
  url: '',
  description: '',
  events: [] as string[],
  format: 'json',
  retryCount: 3,
  timeout: 10,
  secret: ''
})

// ==================== Form Rules ====================
const webhookRules = {
  name: [{ required: true, message: 'Please enter webhook name', trigger: 'blur' }],
  url: [
    { required: true, message: 'Please enter webhook URL', trigger: 'blur' },
    { type: 'url', message: 'Please enter a valid URL', trigger: 'blur' }
  ],
  events: [{ required: true, message: 'Please select at least one event', trigger: 'change' }]
}

// ==================== Computed ====================
const filteredWebhooks = computed(() => {
  let filtered = webhooks.value
  if (searchKeyword.value) {
    filtered = filtered.filter(w =>
        w.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        w.url.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        w.description.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (statusFilter.value) {
    filtered = filtered.filter(w => w.status === statusFilter.value)
  }
  if (eventTypeFilter.value) {
    filtered = filtered.filter(w => w.events.includes(eventTypeFilter.value))
  }
  return filtered
})

const paginatedWebhooks = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredWebhooks.value.slice(start, end)
})

// ==================== Methods ====================
const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    active: 'success',
    inactive: 'info',
    error: 'danger'
  }
  return types[status] || 'info'
}

const getFormatType = (format: string) => {
  const types: Record<string, string> = {
    json: 'primary',
    xml: 'warning',
    form: 'info'
  }
  return types[format] || 'info'
}

const formatDateTime = (datetime: string) => {
  if (!datetime) return 'Never'
  return datetime
}

const handleCreateWebhook = () => {
  dialogMode.value = 'create'
  newWebhook.value = {
    name: '',
    url: '',
    description: '',
    events: [],
    format: 'json',
    retryCount: 3,
    timeout: 10,
    secret: ''
  }
  webhookDialogVisible.value = true
}

const handleEditWebhook = (webhook: WebhookEndpoint) => {
  dialogMode.value = 'edit'
  newWebhook.value = { ...webhook }
  selectedWebhook.value = webhook
  webhookDialogVisible.value = true
}

const handleSaveWebhook = async () => {
  await webhookFormRef.value?.validate()
  if (dialogMode.value === 'create') {
    const webhook: WebhookEndpoint = {
      id: Math.max(...webhooks.value.map(w => w.id)) + 1,
      name: newWebhook.value.name,
      url: newWebhook.value.url,
      description: newWebhook.value.description,
      events: newWebhook.value.events,
      status: 'inactive',
      format: newWebhook.value.format as any,
      headers: { 'Content-Type': 'application/json' },
      retryCount: newWebhook.value.retryCount,
      timeout: newWebhook.value.timeout,
      createdAt: new Date().toISOString().split('T')[0],
      updatedAt: new Date().toISOString().split('T')[0],
      lastTriggered: '',
      successCount: 0,
      failureCount: 0,
      secret: newWebhook.value.secret
    }
    webhooks.value.push(webhook)
    statistics.totalWebhooks++
    ElMessage.success('Webhook created successfully')
  } else if (selectedWebhook.value) {
    const index = webhooks.value.findIndex(w => w.id === selectedWebhook.value.id)
    if (index !== -1) {
      webhooks.value[index] = { ...webhooks.value[index], ...newWebhook.value, updatedAt: new Date().toISOString().split('T')[0] }
      ElMessage.success('Webhook updated successfully')
    }
  }
  webhookDialogVisible.value = false
}

const handleDeleteWebhook = (webhook: WebhookEndpoint) => {
  ElMessageBox.confirm(
      `Are you sure you want to delete webhook "${webhook.name}"? This action cannot be undone.`,
      'Confirm Delete',
      { type: 'warning' }
  ).then(() => {
    const index = webhooks.value.findIndex(w => w.id === webhook.id)
    if (index !== -1) {
      webhooks.value.splice(index, 1)
      if (webhook.status === 'active') statistics.activeWebhooks--
      statistics.totalWebhooks--
      ElMessage.success('Webhook deleted successfully')
    }
  }).catch(() => {})
}

const handleToggleStatus = (webhook: WebhookEndpoint) => {
  const index = webhooks.value.findIndex(w => w.id === webhook.id)
  if (index !== -1) {
    const newStatus = webhooks.value[index].status === 'active' ? 'inactive' : 'active'
    webhooks.value[index].status = newStatus
    if (newStatus === 'active') {
      statistics.activeWebhooks++
    } else {
      statistics.activeWebhooks--
    }
    ElMessage.success(`Webhook ${newStatus === 'active' ? 'activated' : 'deactivated'}`)
  }
}

const handleTestWebhook = (webhook: WebhookEndpoint) => {
  selectedWebhook.value = webhook
  testPayload.value = JSON.stringify({
    event: 'test.webhook',
    timestamp: new Date().toISOString(),
    data: { message: 'This is a test payload' }
  }, null, 2)
  testResult.value = null
  testDialogVisible.value = true
}

const handleRunTest = async () => {
  testing.value = true
  setTimeout(() => {
    const success = Math.random() > 0.3
    testResult.value = {
      success: success,
      statusCode: success ? 200 : 500,
      responseTime: Math.floor(Math.random() * 300) + 50,
      response: success ? { status: 'ok', message: 'Webhook received' } : { error: 'Server error' }
    }
    ElMessage.success(success ? 'Test completed successfully' : 'Test failed')
    testing.value = false
  }, 1500)
}

const handleViewDeliveries = (webhook: WebhookEndpoint) => {
  selectedWebhook.value = webhook
  deliveryDialogVisible.value = true
}

const handleViewLogs = (webhook: WebhookEndpoint) => {
  selectedWebhook.value = webhook
  logDialogVisible.value = true
}

const handleCopyUrl = (url: string) => {
  navigator.clipboard.writeText(url)
  ElMessage.success('URL copied to clipboard')
}

const handleCopySecret = (secret: string) => {
  if (secret) {
    navigator.clipboard.writeText(secret)
    ElMessage.success('Secret copied to clipboard')
  }
}

const handleRefresh = () => {
  ElMessage.info('Refreshing data...')
  setTimeout(() => {
    statistics.totalDeliveries += Math.floor(Math.random() * 100)
    ElMessage.success('Data refreshed')
  }, 1000)
}

const handleExportWebhooks = () => {
  const exportData = {
    webhooks: webhooks.value,
    exportDate: new Date().toISOString(),
    version: '1.0'
  }
  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `webhooks_export_${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Webhooks exported successfully')
}

const handleResendDelivery = (delivery: any) => {
  ElMessage.success(`Resending webhook delivery for ${delivery.webhookName}`)
}

// ==================== Initialize Charts ====================
const initCharts = () => {
  if (!deliveryChart.value) return

  // Delivery Success Rate Chart (Line)
  const delivery = echarts.init(deliveryChart.value)
  delivery.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Successful Deliveries', 'Failed Deliveries'] },
    xAxis: { type: 'category', data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'] },
    yAxis: { type: 'value', name: 'Deliveries' },
    series: [
      { name: 'Successful Deliveries', type: 'line', data: [125, 98, 245, 423, 389, 234], smooth: true, lineStyle: { color: '#52c41a', width: 2 } },
      { name: 'Failed Deliveries', type: 'line', data: [12, 8, 23, 34, 28, 15], smooth: true, lineStyle: { color: '#ff4d4f', width: 2 } }
    ]
  })

  // Webhook Status Chart (Pie)
  const status = echarts.init(statusChart.value)
  status.setOption({
    tooltip: { trigger: 'item' },
    legend: { top: 'bottom' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: statistics.activeWebhooks, name: 'Active', itemStyle: { color: '#52c41a' } },
        { value: statistics.totalWebhooks - statistics.activeWebhooks, name: 'Inactive', itemStyle: { color: '#8c8c8c' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })

  // Response Time Chart (Bar)
  const latency = echarts.init(latencyChart.value)
  latency.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'category', data: webhooks.value.slice(0, 6).map(w => w.name.substring(0, 15)) },
    yAxis: { type: 'value', name: 'Response Time (ms)' },
    series: [{
      data: webhooks.value.slice(0, 6).map(w => w.status === 'active' ? Math.floor(Math.random() * 400) + 100 : 0),
      type: 'bar',
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#faad14' }
    }]
  })

  // Handle resize
  window.addEventListener('resize', () => {
    delivery.resize()
    status.resize()
    latency.resize()
  })
}

// ==================== Watch for Tab Changes ====================
watch(activeTab, (newTab) => {
  if (newTab === 'analytics') {
    nextTick(() => {
      initCharts()
    })
  }
})

// ==================== Loading on Mount ====================
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
      if (activeTab.value === 'analytics') {
        initCharts()
      }
    }, 400)
  }, 2000)
})
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
          <span class="loading-title">Loading Webhook Services</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="webhook-services">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2>Webhook Services</h2>
        <p>Configure and manage webhook endpoints for real-time event notifications, data delivery, and third-party integrations</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleCreateWebhook">
          <el-icon><Plus /></el-icon>
          New Webhook
        </el-button>
        <el-button @click="handleExportWebhooks">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
        <el-button @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-cards">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #e8f4ff">
            <el-icon color="#1890ff" size="28"><Connection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.totalWebhooks }}</div>
            <div class="stat-label">Total Webhooks</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #e6f7e6">
            <el-icon color="#52c41a" size="28"><Checked /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.activeWebhooks }}</div>
            <div class="stat-label">Active Webhooks</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #fff7e6">
            <el-icon color="#faad14" size="28"><Message /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ (statistics.totalDeliveries / 1000).toFixed(1) }}k</div>
            <div class="stat-label">Total Deliveries</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #fdf0e8">
            <el-icon color="#ff7a45" size="28"><DataLine /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.successRate }}%</div>
            <div class="stat-label">Success Rate</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Main Tabs -->
    <el-tabs v-model="activeTab" class="webhook-tabs">
      <!-- Webhooks Tab -->
      <el-tab-pane label="Webhooks" name="webhooks">
        <div class="toolbar">
          <div class="toolbar-left">
            <el-input
                v-model="searchKeyword"
                placeholder="Search by name or URL..."
                clearable
                style="width: 260px"
                :prefix-icon="Search"
            />
            <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
              <el-option label="All" value="" />
              <el-option label="Active" value="active" />
              <el-option label="Inactive" value="inactive" />
              <el-option label="Error" value="error" />
            </el-select>
            <el-select v-model="eventTypeFilter" placeholder="Event Type" clearable filterable style="width: 180px">
              <el-option label="All Events" value="" />
              <el-option v-for="event in eventTypes.slice(0, 10)" :key="event" :label="event" :value="event" />
            </el-select>
          </div>
          <div class="toolbar-right">
            <el-button type="info" @click="handleRefresh">
              <el-icon><Refresh /></el-icon>
              Refresh
            </el-button>
          </div>
        </div>

        <el-table :data="paginatedWebhooks" style="width: 100%; margin-top: 16px" stripe>
          <el-table-column prop="name" label="Webhook Name" min-width="180">
            <template #default="{ row }">
              <div>
                <div class="webhook-name">{{ row.name }}</div>
                <div class="webhook-url">
                  <code>{{ row.url.substring(0, 50) }}{{ row.url.length > 50 ? '...' : '' }}</code>
                  <el-button link size="small" @click="handleCopyUrl(row.url)">
                    <el-icon><CopyDocument /></el-icon>
                  </el-button>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="Description" min-width="180" show-overflow-tooltip />
          <el-table-column label="Events" width="150">
            <template #default="{ row }">
              <el-popover placement="top" :width="300" trigger="hover">
                <template #reference>
                  <el-tag size="small">{{ row.events.length }} events</el-tag>
                </template>
                <div class="event-list">
                  <el-tag v-for="event in row.events" :key="event" size="small" style="margin: 2px">
                    {{ event }}
                  </el-tag>
                </div>
              </el-popover>
            </template>
          </el-table-column>
          <el-table-column prop="format" label="Format" width="80">
            <template #default="{ row }">
              <el-tag :type="getFormatType(row.format)" size="small">{{ row.format.toUpperCase() }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">{{ row.status.toUpperCase() }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Stats" width="120">
            <template #default="{ row }">
              <div class="stats-mini">
                <span class="success">✓ {{ row.successCount }}</span>
                <span class="failure">✗ {{ row.failureCount }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="lastTriggered" label="Last Triggered" width="160">
            <template #default="{ row }">
              {{ formatDateTime(row.lastTriggered) }}
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="320" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="handleTestWebhook(row)">
                <el-icon><Monitor /></el-icon>
                Test
              </el-button>
              <el-button link type="primary" size="small" @click="handleViewDeliveries(row)">
                <el-icon><List /></el-icon>
                Deliveries
              </el-button>
              <el-button link type="primary" size="small" @click="handleViewLogs(row)">
                <el-icon><Document /></el-icon>
                Logs
              </el-button>
              <el-button link type="primary" size="small" @click="handleEditWebhook(row)">
                <el-icon><Edit /></el-icon>
                Edit
              </el-button>
              <el-button link type="warning" size="small" @click="handleToggleStatus(row)">
                <el-icon><Switch /></el-icon>
                {{ row.status === 'active' ? 'Disable' : 'Enable' }}
              </el-button>
              <el-button link type="danger" size="small" @click="handleDeleteWebhook(row)">
                <el-icon><Delete /></el-icon>
                Delete
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- Pagination -->
        <div class="pagination-wrapper">
          <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[15, 30, 50, 100]"
              :total="filteredWebhooks.length"
              layout="total, sizes, prev, pager, next, jumper"
          />
        </div>
      </el-tab-pane>

      <!-- Analytics Tab -->
      <el-tab-pane label="Analytics" name="analytics">
        <div class="analytics-container">
          <el-row :gutter="16">
            <el-col :span="16">
              <el-card class="analytics-card" header="Delivery Trends">
                <div ref="deliveryChart" style="height: 350px"></div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card class="analytics-card" header="Webhook Status">
                <div ref="statusChart" style="height: 350px"></div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="16" style="margin-top: 16px">
            <el-col :span="24">
              <el-card class="analytics-card" header="Response Time by Webhook">
                <div ref="latencyChart" style="height: 300px"></div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="16" style="margin-top: 16px">
            <el-col :span="24">
              <el-card class="analytics-card" header="Recent Deliveries">
                <el-table :data="deliveryHistory" style="width: 100%" stripe>
                  <el-table-column prop="timestamp" label="Timestamp" width="180" />
                  <el-table-column prop="webhookName" label="Webhook" min-width="150" />
                  <el-table-column prop="event" label="Event" min-width="180" />
                  <el-table-column prop="status" label="Status" width="100">
                    <template #default="{ row }">
                      <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
                        {{ row.status.toUpperCase() }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="responseTime" label="Response" width="120">
                    <template #default="{ row }">
                      {{ row.responseTime > 0 ? row.responseTime + 'ms' : '-' }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="statusCode" label="Status Code" width="100">
                    <template #default="{ row }">
                      <el-tag :type="row.statusCode === 200 ? 'success' : 'danger'" size="small">
                        {{ row.statusCode || '-' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="Actions" width="100">
                    <template #default="{ row }">
                      <el-button v-if="row.status === 'failed'" link type="primary" size="small" @click="handleResendDelivery(row)">
                        <el-icon><Refresh /></el-icon>
                        Resend
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>

      <!-- Events Reference Tab -->
      <el-tab-pane label="Events Reference" name="events">
        <div class="events-container">
          <h3>Available Webhook Events</h3>
          <p class="events-description">Subscribe to any of these events to receive real-time notifications via webhook</p>

          <div class="event-categories">
            <el-collapse v-model="activeCollapse">
              <el-collapse-item title="Alert Events" name="alerts">
                <div class="event-grid">
                  <div v-for="event in eventTypes.filter(e => e.startsWith('alert'))" :key="event" class="event-item">
                    <code>{{ event }}</code>
                    <span class="event-desc">{{ getEventDescription(event) }}</span>
                  </div>
                </div>
              </el-collapse-item>

              <el-collapse-item title="Device Events" name="devices">
                <div class="event-grid">
                  <div v-for="event in eventTypes.filter(e => e.startsWith('device'))" :key="event" class="event-item">
                    <code>{{ event }}</code>
                    <span class="event-desc">{{ getEventDescription(event) }}</span>
                  </div>
                </div>
              </el-collapse-item>

              <el-collapse-item title="Telemetry Events" name="telemetry">
                <div class="event-grid">
                  <div v-for="event in eventTypes.filter(e => e.startsWith('telemetry'))" :key="event" class="event-item">
                    <code>{{ event }}</code>
                    <span class="event-desc">{{ getEventDescription(event) }}</span>
                  </div>
                </div>
              </el-collapse-item>

              <el-collapse-item title="Security Events" name="security">
                <div class="event-grid">
                  <div v-for="event in eventTypes.filter(e => e.startsWith('security'))" :key="event" class="event-item">
                    <code>{{ event }}</code>
                    <span class="event-desc">{{ getEventDescription(event) }}</span>
                  </div>
                </div>
              </el-collapse-item>

              <el-collapse-item title="System Events" name="system">
                <div class="event-grid">
                  <div v-for="event in eventTypes.filter(e => e.startsWith('system'))" :key="event" class="event-item">
                    <code>{{ event }}</code>
                    <span class="event-desc">{{ getEventDescription(event) }}</span>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Create/Edit Webhook Dialog -->
    <el-dialog
        v-model="webhookDialogVisible"
        :title="dialogMode === 'create' ? 'Create Webhook' : 'Edit Webhook'"
        width="700px"
    >
      <el-form :model="newWebhook" :rules="webhookRules" ref="webhookFormRef" label-width="120px">
        <el-form-item label="Webhook Name" prop="name">
          <el-input v-model="newWebhook.name" placeholder="e.g., Slack Alert Webhook" />
        </el-form-item>
        <el-form-item label="Endpoint URL" prop="url">
          <el-input v-model="newWebhook.url" placeholder="https://example.com/webhook" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="newWebhook.description" type="textarea" :rows="2" placeholder="Describe the webhook purpose" />
        </el-form-item>
        <el-form-item label="Events" prop="events">
          <el-select v-model="newWebhook.events" multiple filterable collapse-tags placeholder="Select events" style="width: 100%">
            <el-option v-for="event in eventTypes" :key="event" :label="event" :value="event" />
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Format">
              <el-select v-model="newWebhook.format" style="width: 100%">
                <el-option label="JSON" value="json" />
                <el-option label="XML" value="xml" />
                <el-option label="Form Data" value="form" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Retry Count">
              <el-input-number v-model="newWebhook.retryCount" :min="0" :max="10" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Timeout (seconds)">
              <el-input-number v-model="newWebhook.timeout" :min="1" :max="60" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Secret (optional)">
              <el-input v-model="newWebhook.secret" placeholder="Used for signature verification" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="webhookDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleSaveWebhook">Save</el-button>
      </template>
    </el-dialog>

    <!-- Test Webhook Dialog -->
    <el-dialog v-model="testDialogVisible" :title="`Test Webhook - ${selectedWebhook?.name}`" width="700px">
      <div class="test-container">
        <div class="test-info">
          <el-tag type="primary" size="small">POST</el-tag>
          <code class="test-endpoint">{{ selectedWebhook?.url }}</code>
        </div>
        <div class="test-input">
          <h4>Payload:</h4>
          <el-input
              v-model="testPayload"
              type="textarea"
              :rows="6"
              placeholder='{"event": "test.webhook", "data": {}}'
          />
        </div>
        <div class="test-actions" style="margin: 16px 0">
          <el-button type="primary" @click="handleRunTest" :loading="testing">
            <el-icon><Service /></el-icon>
            Send Test
          </el-button>
        </div>
        <div v-if="testResult" class="test-result">
          <h4>Response:</h4>
          <div class="result-status">
            <el-tag :type="testResult.statusCode === 200 ? 'success' : 'danger'">
              Status: {{ testResult.statusCode }}
            </el-tag>
            <span class="response-time">Response Time: {{ testResult.responseTime }}ms</span>
          </div>
          <pre class="code-block">{{ JSON.stringify(testResult.response, null, 2) }}</pre>
        </div>
      </div>
    </el-dialog>

    <!-- Delivery History Dialog -->
    <el-dialog v-model="deliveryDialogVisible" :title="`Delivery History - ${selectedWebhook?.name}`" width="900px">
      <el-table :data="deliveryHistory" style="width: 100%" stripe>
        <el-table-column prop="timestamp" label="Timestamp" width="180" />
        <el-table-column prop="event" label="Event" min-width="200" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
              {{ row.status.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="responseTime" label="Response Time" width="120">
          <template #default="{ row }">
            {{ row.responseTime > 0 ? row.responseTime + 'ms' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="statusCode" label="Status Code" width="100" />
        <el-table-column prop="retryCount" label="Retries" width="80" align="center" />
        <el-table-column label="Actions" width="100">
          <template #default="{ row }">
            <el-button v-if="row.status === 'failed'" link type="primary" size="small" @click="handleResendDelivery(row)">
              Resend
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- Webhook Logs Dialog -->
    <el-dialog v-model="logDialogVisible" :title="`Webhook Logs - ${selectedWebhook?.name}`" width="800px">
      <el-table :data="webhookLogs.filter(l => l.webhookId === selectedWebhook?.id)" style="width: 100%" stripe>
        <el-table-column prop="timestamp" label="Timestamp" width="180" />
        <el-table-column prop="level" label="Level" width="100">
          <template #default="{ row }">
            <el-tag :type="row.level === 'INFO' ? 'success' : row.level === 'WARN' ? 'warning' : 'danger'" size="small">
              {{ row.level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="Message" min-width="250" />
        <el-table-column prop="details" label="Details" min-width="200" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script lang="ts">
// Helper function for event descriptions
const getEventDescription = (event: string) => {
  const descriptions: Record<string, string> = {
    'alert.created': 'Triggered when a new alert is created',
    'alert.acknowledged': 'Triggered when an alert is acknowledged',
    'alert.resolved': 'Triggered when an alert is resolved',
    'alert.critical': 'Triggered for critical severity alerts',
    'device.online': 'Triggered when a device comes online',
    'device.offline': 'Triggered when a device goes offline',
    'device.error': 'Triggered when a device reports an error',
    'device.created': 'Triggered when a new device is registered',
    'telemetry.received': 'Triggered when telemetry data is received',
    'telemetry.batch': 'Triggered for batched telemetry data',
    'telemetry.threshold': 'Triggered when telemetry exceeds threshold',
    'maintenance.required': 'Triggered when maintenance is needed',
    'maintenance.completed': 'Triggered when maintenance is completed',
    'user.action': 'Triggered on user actions',
    'user.login': 'Triggered on user login',
    'user.logout': 'Triggered on user logout',
    'report.generated': 'Triggered when a report is generated',
    'report.scheduled': 'Triggered for scheduled reports',
    'security.intrusion': 'Triggered on security intrusion detection',
    'security.anomaly': 'Triggered on security anomaly detection',
    'audit.log': 'Triggered for audit log entries',
    'system.startup': 'Triggered on system startup',
    'system.shutdown': 'Triggered on system shutdown',
    'system.error': 'Triggered on system errors'
  }
  return descriptions[event] || 'Event description not available'
}

// Add to component
export default {
  setup() {
    return {
      getEventDescription
    }
  }
}
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
  font-size: 20px;
  font-weight: 600;
  color: #e2e8f0;
  display: flex;
  justify-content: center;
  align-items: baseline;
  gap: 4px;
}

.loading-title {
  font-size: 20px;
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
  font-weight: 500;
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
.webhook-services {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: calc(100vh - 60px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.header-left h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.header-left p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
}

.stat-label {
  font-size: 14px;
  color: #8c8c8c;
  margin-top: 4px;
}

.webhook-tabs {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.toolbar-left {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.toolbar-right {
  display: flex;
  gap: 12px;
}

/* Webhook Table */
.webhook-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.webhook-url {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #999;
  font-family: monospace;
}

.stats-mini {
  display: flex;
  gap: 8px;
  font-size: 13px;
}

.stats-mini .success {
  color: #52c41a;
}

.stats-mini .failure {
  color: #ff4d4f;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

/* Analytics */
.analytics-container {
  padding: 16px 0;
}

.analytics-card {
  height: 100%;
}

/* Events Reference */
.events-container {
  padding: 16px 0;
}

.events-container h3 {
  margin: 0 0 8px 0;
}

.events-description {
  color: #666;
  margin-bottom: 24px;
}

.event-categories {
  margin-top: 16px;
}

.event-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 12px;
  padding: 8px 0;
}

.event-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  background: #f9f9f9;
  border-radius: 6px;
}

.event-item code {
  font-size: 12px;
  background: white;
  padding: 2px 6px;
  border-radius: 4px;
  color: #1890ff;
}

.event-desc {
  font-size: 12px;
  color: #666;
}

/* Test Dialog */
.test-container {
  padding: 8px 0;
}

.test-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 8px;
}

.test-endpoint {
  font-family: monospace;
  font-size: 13px;
  color: #1890ff;
  word-break: break-all;
}

.test-input h4, .test-result h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
}

.result-status {
  display: flex;
  align-items: center;
  gap: 16px;
  margin: 12px 0;
}

.response-time {
  font-size: 13px;
  color: #666;
}

.code-block {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 12px;
  font-family: monospace;
  margin: 0;
}

.event-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  max-width: 300px;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
  }

  .header-right {
    margin-top: 16px;
    width: 100%;
  }

  .toolbar {
    flex-direction: column;
    gap: 12px;
  }

  .toolbar-left {
    width: 100%;
  }

  .toolbar-right {
    width: 100%;
  }

  .event-grid {
    grid-template-columns: 1fr;
  }
}

:deep(.el-card__header) {
  font-weight: 600;
  background-color: #fafafa;
  border-bottom: 1px solid #f0f0f0;
}

:deep(.el-tabs__header) {
  margin-bottom: 20px;
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-collapse-item__header) {
  font-weight: 600;
}
</style>