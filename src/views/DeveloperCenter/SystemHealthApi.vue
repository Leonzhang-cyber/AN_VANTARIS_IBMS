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
          <span class="loading-title">Loading System Health API</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Monitor System Health and API Status</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="system-health-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">System Health API</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
          <el-breadcrumb-item>Developer Center</el-breadcrumb-item>
          <el-breadcrumb-item>System Health API</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="testEndpoint">
          <el-icon><MagicStick /></el-icon>
          Test Endpoint
        </el-button>
        <el-button type="success" plain @click="generateApiKey">
          <el-icon><Key /></el-icon>
          Generate API Key
        </el-button>
        <el-button type="info" plain @click="viewDocumentation">
          <el-icon><Document /></el-icon>
          Documentation
        </el-button>
      </div>
    </div>

    <!-- Overall System Status -->
    <div class="status-section">
      <el-card class="status-card" shadow="hover">
        <div class="status-header">
          <div class="status-indicator" :class="systemStatus"></div>
          <div class="status-text">
            <div class="status-title">System Status</div>
            <div class="status-value">{{ systemStatusText }}</div>
          </div>
          <div class="uptime-text">Uptime: {{ uptime }} days</div>
        </div>
        <div class="status-grid">
          <div class="status-item">
            <div class="status-label">API Version</div>
            <div class="status-value">{{ apiVersion }}</div>
          </div>
          <div class="status-item">
            <div class="status-label">Environment</div>
            <div class="status-value">{{ environment }}</div>
          </div>
          <div class="status-item">
            <div class="status-label">Region</div>
            <div class="status-value">{{ region }}</div>
          </div>
          <div class="status-item">
            <div class="status-label">Last Incident</div>
            <div class="status-value">{{ lastIncident }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Service Health Cards -->
    <div class="services-section">
      <h3 class="section-title">Service Health Status</h3>
      <div class="services-grid">
        <el-card v-for="service in services" :key="service.name" class="service-card" shadow="hover">
          <div class="service-header">
            <div class="service-icon" :style="{ backgroundColor: getServiceColor(service.status) }">
              <el-icon :size="24"><component :is="service.icon" /></el-icon>
            </div>
            <div class="service-status">
              <el-tag :type="getStatusTagType(service.status)" size="large">{{ service.status }}</el-tag>
            </div>
          </div>
          <div class="service-info">
            <div class="service-name">{{ service.name }}</div>
            <div class="service-meta">
              <span><el-icon><Clock /></el-icon> Latency: {{ service.latency }}ms</span>
              <span><el-icon><CircleCheck /></el-icon> Uptime: {{ service.uptime }}%</span>
            </div>
            <div class="service-description">{{ service.description }}</div>
          </div>
          <el-progress :percentage="service.health" :stroke-width="6" :color="getHealthColor(service.health)" :format="(p) => `${p}% Health`" />
        </el-card>
      </div>
    </div>

    <!-- API Endpoints -->
    <div class="endpoints-section">
      <el-card class="endpoints-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Connection /></el-icon> API Endpoints</span>
            <el-button text type="primary" @click="refreshEndpoints">Refresh Status</el-button>
          </div>
        </template>
        <el-table :data="apiEndpoints" stripe style="width: 100%">
          <el-table-column prop="method" label="Method" width="80">
            <template #default="{ row }">
              <el-tag :type="getMethodTagType(row.method)" size="small">{{ row.method }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="endpoint" label="Endpoint" min-width="250" />
          <el-table-column prop="description" label="Description" min-width="200" />
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <div class="status-dot" :class="row.status"></div>
              <span>{{ row.status === 'up' ? 'Healthy' : row.status === 'degraded' ? 'Degraded' : 'Down' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="latency" label="Latency" width="80">
            <template #default="{ row }">
              <span :class="getLatencyClass(row.latency)">{{ row.latency }}ms</span>
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="100">
            <template #default="{ row }">
              <el-button size="small" text type="primary" @click="testEndpointUrl(row)">Test</el-button>
              <el-button size="small" text type="info" @click="viewEndpointDocs(row)">Docs</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- API Response Time Charts -->
    <div class="charts-section">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><TrendCharts /></el-icon> API Response Time Trend</span>
            <el-select v-model="chartTimeRange" size="small" style="width: 100px">
              <el-option label="Last Hour" value="hour" />
              <el-option label="Last Day" value="day" />
              <el-option label="Last Week" value="week" />
            </el-select>
          </div>
        </template>
        <div ref="responseChartRef" class="response-chart"></div>
      </el-card>

      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><DataLine /></el-icon> Requests per Minute</span>
            <el-button text type="primary" @click="refreshRequestChart">Refresh</el-button>
          </div>
        </template>
        <div ref="requestChartRef" class="request-chart"></div>
      </el-card>
    </div>

    <!-- Recent Alerts -->
    <div class="alerts-section">
      <el-card class="alerts-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Warning /></el-icon> Recent Alerts</span>
            <el-button text type="primary" @click="viewAllAlerts">View All</el-button>
          </div>
        </template>
        <el-table :data="recentAlerts" stripe style="width: 100%">
          <el-table-column prop="timestamp" label="Time" width="160" />
          <el-table-column prop="severity" label="Severity" width="100">
            <template #default="{ row }">
              <el-tag :type="getSeverityTagType(row.severity)" size="small">{{ row.severity }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="service" label="Service" width="150" />
          <el-table-column prop="message" label="Message" min-width="300" />
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'resolved' ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- API Key Management -->
    <div class="apikey-section">
      <el-card class="apikey-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Key /></el-icon> API Key Management</span>
            <el-button text type="primary" @click="createApiKey">Create New Key</el-button>
          </div>
        </template>
        <el-table :data="apiKeys" stripe style="width: 100%">
          <el-table-column prop="name" label="Name" width="200" />
          <el-table-column prop="key" label="API Key" min-width="300">
            <template #default="{ row }">
              <div class="key-display">
                <span v-if="!row.showKey">••••••••••••••••••••••••</span>
                <span v-else>{{ row.key }}</span>
                <el-button size="small" text @click="toggleKeyVisibility(row)">
                  <el-icon><Search /></el-icon>
                </el-button>
                <el-button size="small" text @click="copyApiKey(row)">
                  <el-icon><CopyDocument /></el-icon>
                </el-button>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="createdAt" label="Created" width="140" />
          <el-table-column prop="lastUsed" label="Last Used" width="140" />
          <el-table-column label="Actions" width="100">
            <template #default="{ row }">
              <el-button size="small" text type="danger" @click="revokeApiKey(row)">Revoke</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- Health Check Configuration -->
    <div class="health-config-section">
      <el-card class="health-config-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Setting /></el-icon> Health Check Configuration</span>
            <el-button text type="primary" @click="editHealthConfig">Edit Configuration</el-button>
          </div>
        </template>
        <div class="config-grid">
          <div class="config-item">
            <div class="config-label">Check Interval</div>
            <div class="config-value">{{ healthCheckInterval }} seconds</div>
          </div>
          <div class="config-item">
            <div class="config-label">Timeout Threshold</div>
            <div class="config-value">{{ timeoutThreshold }} ms</div>
          </div>
          <div class="config-item">
            <div class="config-label">Alert Webhook</div>
            <div class="config-value">{{ alertWebhook || 'Not configured' }}</div>
          </div>
          <div class="config-item">
            <div class="config-label">Slack Notifications</div>
            <div class="config-value">{{ slackEnabled ? 'Enabled' : 'Disabled' }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- SLI/SLO Metrics -->
    <div class="slo-section">
      <el-card class="slo-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Medal /></el-icon> SLI / SLO Metrics (30 Days)</span>
            <el-button text type="primary" @click="refreshSLOMetrics">Refresh</el-button>
          </div>
        </template>
        <div class="slo-grid">
          <div class="slo-item">
            <div class="slo-label">Availability</div>
            <div class="slo-value">{{ availabilitySLO }}%</div>
            <el-progress :percentage="availabilitySLO" :stroke-width="8" :color="availabilitySLO >= 99.9 ? '#10b981' : availabilitySLO >= 99 ? '#f59e0b' : '#ef4444'" />
            <div class="slo-target">Target: 99.9%</div>
          </div>
          <div class="slo-item">
            <div class="slo-label">Latency (p99)</div>
            <div class="slo-value">{{ latencySLO }} ms</div>
            <el-progress :percentage="Math.max(0, 100 - (latencySLO / 500) * 100)" :stroke-width="8" :color="latencySLO <= 200 ? '#10b981' : latencySLO <= 500 ? '#f59e0b' : '#ef4444'" />
            <div class="slo-target">Target: &lt;200ms</div>
          </div>
          <div class="slo-item">
            <div class="slo-label">Error Rate</div>
            <div class="slo-value">{{ errorRateSLO }}%</div>
            <el-progress :percentage="100 - errorRateSLO" :stroke-width="8" :color="errorRateSLO <= 0.1 ? '#10b981' : errorRateSLO <= 0.5 ? '#f59e0b' : '#ef4444'" />
            <div class="slo-target">Target: &lt;0.1%</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Quick Actions Footer -->
    <div class="footer-actions">
      <div class="action-group">
        <el-button type="primary" plain @click="runHealthCheck">
          <el-icon><Refresh /></el-icon>
          Run Health Check
        </el-button>
        <el-button type="success" plain @click="downloadHealthReport">
          <el-icon><Download /></el-icon>
          Download Report
        </el-button>
        <el-button type="warning" plain @click="configureAlerts">
          <el-icon><Bell /></el-icon>
          Configure Alerts
        </el-button>
        <el-button type="info" plain @click="viewIncidentHistory">
          <el-icon><Calendar /></el-icon>
          Incident History
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Refresh, Setting, User, Clock, Warning, CircleCheck, TrendCharts, DataLine,
  Star, Share, CopyDocument, Delete, Mic, Picture, Document, Upload, Download,
  MagicStick, ChatDotRound, Message, Service, Search, Edit, Plus, VideoPlay,
  VideoPause, Operation, Headset, Monitor, Cpu, Connection, Lock, Key, Medal,
  Flag, DataAnalysis, EditPen, Tickets, Filter, SuccessFilled, List, Grid, Calendar, Bell,
} from '@element-plus/icons-vue'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading System Health API...')

const loadingMessages = [
  'Loading System Health API...',
  'Checking service status...',
  'Fetching metrics...',
  'System health dashboard ready!'
]

// System status
const systemStatus = ref('healthy')
const systemStatusText = ref('All Systems Operational')
const uptime = ref(99)
const apiVersion = ref('v2.1.0')
const environment = ref('Production')
const region = ref('us-east-1')
const lastIncident = ref('2024-01-10')

// Services
const services = ref([
  { name: 'API Gateway', icon: 'Connection', status: 'healthy', latency: 45, uptime: 99.99, health: 99, description: 'Main API Gateway and routing' },
  { name: 'Authentication Service', icon: 'Lock', status: 'healthy', latency: 32, uptime: 99.99, health: 100, description: 'User auth and token management' },
  { name: 'Database Cluster', icon: 'DataLine', status: 'healthy', latency: 28, uptime: 99.98, health: 98, description: 'Primary database cluster' },
  { name: 'Cache Service', icon: 'Cpu', status: 'healthy', latency: 12, uptime: 99.99, health: 100, description: 'Redis cache layer' },
  { name: 'Message Queue', icon: 'Message', status: 'degraded', latency: 89, uptime: 99.95, health: 85, description: 'RabbitMQ message broker' },
  { name: 'Storage Service', icon: 'Document', status: 'healthy', latency: 56, uptime: 99.97, health: 96, description: 'Object storage and CDN' }
])

// API Endpoints
const apiEndpoints = ref([
  { method: 'GET', endpoint: '/api/v1/health', description: 'System health check endpoint', status: 'up', latency: 24 },
  { method: 'GET', endpoint: '/api/v1/health/services', description: 'Detailed service health status', status: 'up', latency: 56 },
  { method: 'GET', endpoint: '/api/v1/health/metrics', description: 'Prometheus metrics endpoint', status: 'up', latency: 34 },
  { method: 'GET', endpoint: '/api/v1/health/readiness', description: 'Readiness probe for K8s', status: 'up', latency: 12 },
  { method: 'GET', endpoint: '/api/v1/health/liveness', description: 'Liveness probe for K8s', status: 'up', latency: 8 },
  { method: 'POST', endpoint: '/api/v1/health/webhook', description: 'Webhook configuration endpoint', status: 'degraded', latency: 234 }
])

// Recent alerts
const recentAlerts = ref([
  { timestamp: '2024-01-15 09:45:32', severity: 'warning', service: 'Message Queue', message: 'High message queue depth detected', status: 'resolved' },
  { timestamp: '2024-01-14 23:22:15', severity: 'critical', service: 'Database Cluster', message: 'Replication lag > 10 seconds', status: 'resolved' },
  { timestamp: '2024-01-14 14:30:22', severity: 'info', service: 'API Gateway', message: 'Rate limit threshold reached for tenant A', status: 'resolved' },
  { timestamp: '2024-01-13 08:15:44', severity: 'warning', service: 'Storage Service', message: 'CDN edge node latency spike', status: 'resolved' }
])

// API Keys
const apiKeys = ref([
  { id: 1, name: 'Production API Key', key: 'ibms_live_sk_abc123xyz789', showKey: false, createdAt: '2024-01-01', lastUsed: '2024-01-15' },
  { id: 2, name: 'Development Key', key: 'ibms_dev_sk_def456uvw012', showKey: false, createdAt: '2024-01-05', lastUsed: '2024-01-14' },
  { id: 3, name: 'CI/CD Pipeline', key: 'ibms_ci_sk_ghi789rst345', showKey: false, createdAt: '2024-01-10', lastUsed: '2024-01-15' }
])

// Health config
const healthCheckInterval = ref(30)
const timeoutThreshold = ref(5000)
const alertWebhook = ref('https://alerts.ibms.com/webhook')
const slackEnabled = ref(true)

// SLO Metrics
const availabilitySLO = ref(99.95)
const latencySLO = ref(156)
const errorRateSLO = ref(0.08)

// Chart variables
const chartTimeRange = ref('day')
const responseChartRef = ref<HTMLElement>()
const requestChartRef = ref<HTMLElement>()
let responseChart: echarts.ECharts | null = null
let requestChart: echarts.ECharts | null = null

// Helper functions
const getServiceColor = (status: string) => {
  switch (status) {
    case 'healthy': return '#10b981'
    case 'degraded': return '#f59e0b'
    case 'down': return '#ef4444'
    default: return '#64748b'
  }
}

const getStatusTagType = (status: string) => {
  switch (status) {
    case 'healthy': return 'success'
    case 'degraded': return 'warning'
    case 'down': return 'danger'
    default: return 'info'
  }
}

const getHealthColor = (health: number) => {
  if (health >= 95) return '#10b981'
  if (health >= 80) return '#3b82f6'
  if (health >= 70) return '#f59e0b'
  return '#ef4444'
}

const getMethodTagType = (method: string) => {
  switch (method) {
    case 'GET': return 'success'
    case 'POST': return 'primary'
    case 'PUT': return 'warning'
    case 'DELETE': return 'danger'
    default: return 'info'
  }
}

const getLatencyClass = (latency: number) => {
  if (latency <= 50) return 'latency-good'
  if (latency <= 200) return 'latency-warning'
  return 'latency-bad'
}

const getSeverityTagType = (severity: string) => {
  switch (severity) {
    case 'critical': return 'danger'
    case 'warning': return 'warning'
    case 'info': return 'info'
    default: return 'info'
  }
}

// Initialize response time chart
const initResponseChart = () => {
  if (!responseChartRef.value) return
  responseChart = echarts.init(responseChartRef.value)
  updateResponseChart()
}

const updateResponseChart = () => {
  if (!responseChart) return
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['API Gateway', 'Auth Service', 'Database', 'Message Queue'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: getTimeLabels() },
    yAxis: { type: 'value', name: 'Response Time (ms)' },
    series: [
      { name: 'API Gateway', type: 'line', data: [45, 52, 48, 55, 62, 58, 51], lineStyle: { color: '#3b82f6', width: 2 }, smooth: true },
      { name: 'Auth Service', type: 'line', data: [32, 35, 38, 42, 45, 40, 36], lineStyle: { color: '#10b981', width: 2 }, smooth: true },
      { name: 'Database', type: 'line', data: [28, 45, 52, 48, 55, 42, 35], lineStyle: { color: '#f59e0b', width: 2 }, smooth: true },
      { name: 'Message Queue', type: 'line', data: [89, 95, 102, 110, 98, 85, 78], lineStyle: { color: '#ef4444', width: 2 }, smooth: true }
    ]
  }
  responseChart.setOption(option)
}

// Initialize request chart
const initRequestChart = () => {
  if (!requestChartRef.value) return
  requestChart = echarts.init(requestChartRef.value)
  updateRequestChart()
}

const updateRequestChart = () => {
  if (!requestChart) return
  const option = {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: getTimeLabels() },
    yAxis: { type: 'value', name: 'Requests per Minute' },
    series: [{
      type: 'line',
      data: [1240, 1320, 1450, 1680, 1520, 1380, 1250],
      lineStyle: { color: '#8b5cf6', width: 2 },
      areaStyle: { opacity: 0.3, color: '#8b5cf6' },
      smooth: true
    }]
  }
  requestChart.setOption(option)
}

const getTimeLabels = () => {
  if (chartTimeRange.value === 'hour') {
    return ['13:00', '13:10', '13:20', '13:30', '13:40', '13:50', '14:00']
  }
  if (chartTimeRange.value === 'day') {
    return ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00']
  }
  return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
}

// Event handlers
const testEndpoint = () => {
  ElMessage.info('Testing API endpoint...')
  setTimeout(() => {
    ElMessage.success('Endpoint responded with status 200')
  }, 1000)
}

const generateApiKey = () => {
  ElMessageBox.prompt('Enter API key name', 'Generate API Key', {
    confirmButtonText: 'Generate',
    cancelButtonText: 'Cancel',
    inputPlaceholder: 'e.g., Production Key'
  }).then(({ value }) => {
    if (value) {
      const newKey = 'ibms_live_sk_' + Math.random().toString(36).substring(2, 15)
      apiKeys.value.unshift({
        id: Date.now(),
        name: value,
        key: newKey,
        showKey: false,
        createdAt: new Date().toISOString().split('T')[0],
        lastUsed: 'Never'
      })
      ElMessage.success(`API Key generated: ${newKey}`)
    }
  }).catch(() => {})
}

const viewDocumentation = () => {
  ElMessage.info('Opening API documentation')
}

const refreshEndpoints = () => {
  ElMessage.info('Refreshing endpoint status...')
  setTimeout(() => {
    ElMessage.success('Endpoints refreshed')
  }, 800)
}

const testEndpointUrl = (endpoint: any) => {
  ElMessage.info(`Testing ${endpoint.method} ${endpoint.endpoint}...`)
  setTimeout(() => {
    ElMessage.success(`Response: ${endpoint.status === 'up' ? '200 OK' : '503 Service Unavailable'} - ${endpoint.latency}ms`)
  }, 800)
}

const viewEndpointDocs = (endpoint: any) => {
  ElMessage.info(`Viewing documentation for ${endpoint.endpoint}`)
}

const refreshRequestChart = () => {
  if (requestChart) {
    requestChart.setOption({ series: [] })
    updateRequestChart()
    ElMessage.success('Chart refreshed')
  }
}

const viewAllAlerts = () => {
  ElMessage.info('Viewing all alerts')
}

const createApiKey = () => {
  generateApiKey()
}

const toggleKeyVisibility = (key: any) => {
  key.showKey = !key.showKey
}

const copyApiKey = (key: any) => {
  navigator.clipboard.writeText(key.key)
  ElMessage.success('API Key copied to clipboard')
}

const revokeApiKey = (key: any) => {
  ElMessageBox.confirm(`Revoke API key "${key.name}"? This action cannot be undone.`, 'Confirm Revoke', {
    confirmButtonText: 'Revoke',
    cancelButtonText: 'Cancel',
    type: 'danger'
  }).then(() => {
    apiKeys.value = apiKeys.value.filter(k => k.id !== key.id)
    ElMessage.success(`API key "${key.name}" revoked`)
  }).catch(() => {})
}

const editHealthConfig = () => {
  ElMessage.info('Edit health check configuration')
}

const refreshSLOMetrics = () => {
  ElMessage.info('Refreshing SLO metrics...')
  setTimeout(() => {
    ElMessage.success('Metrics refreshed')
  }, 800)
}

const runHealthCheck = () => {
  ElMessage.info('Running health check on all services...')
  setTimeout(() => {
    ElMessage.success('Health check completed - All services operational')
  }, 2000)
}

const downloadHealthReport = () => {
  ElMessage.info('Downloading health report...')
  setTimeout(() => {
    ElMessage.success('Report downloaded')
  }, 1000)
}

const configureAlerts = () => {
  ElMessage.info('Alert configuration dialog opened')
}

const viewIncidentHistory = () => {
  ElMessage.info('Viewing incident history')
}

// Loading animation
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
      setTimeout(() => {
        initResponseChart()
        initRequestChart()
      }, 100)
    }, 400)
  }, 2500)
})

onUnmounted(() => {
  if (responseChart) responseChart.dispose()
  if (requestChart) requestChart.dispose()
})
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
  font-size: 24px;
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
.system-health-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.header-right {
  display: flex;
  gap: 12px;
}

/* Status Section */
.status-section {
  margin-bottom: 24px;
}

.status-card {
  border-radius: 12px;
  background: white;
}

.status-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-bottom: 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.status-indicator {
  width: 16px;
  height: 16px;
  border-radius: 50%;
}

.status-indicator.healthy { background: #10b981; box-shadow: 0 0 8px #10b981; }
.status-indicator.degraded { background: #f59e0b; box-shadow: 0 0 8px #f59e0b; }
.status-indicator.down { background: #ef4444; box-shadow: 0 0 8px #ef4444; }

.status-text {
  flex: 1;
}

.status-title {
  font-size: 12px;
  color: #64748b;
}

.status-value {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.uptime-text {
  font-size: 13px;
  color: #64748b;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.status-item {
  text-align: center;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
}

.status-label {
  font-size: 11px;
  color: #64748b;
  margin-bottom: 4px;
}

/* Services Section */
.services-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.service-card {
  border-radius: 12px;
  background: white;
}

.service-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.service-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.service-name {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.service-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 8px;
}

.service-meta span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.service-description {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 12px;
}

/* Endpoints Section */
.endpoints-section {
  margin-bottom: 24px;
}

.endpoints-card {
  border-radius: 12px;
  background: white;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #1e293b;
}

.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}

.status-dot.up { background: #10b981; }
.status-dot.degraded { background: #f59e0b; }
.status-dot.down { background: #ef4444; }

.latency-good { color: #10b981; font-weight: 500; }
.latency-warning { color: #f59e0b; font-weight: 500; }
.latency-bad { color: #ef4444; font-weight: 500; }

/* Charts Section */
.charts-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  border-radius: 12px;
  background: white;
}

.response-chart,
.request-chart {
  height: 300px;
  width: 100%;
}

/* Alerts Section */
.alerts-section {
  margin-bottom: 24px;
}

.alerts-card {
  border-radius: 12px;
  background: white;
}

/* API Key Section */
.apikey-section {
  margin-bottom: 24px;
}

.apikey-card {
  border-radius: 12px;
  background: white;
}

.key-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Health Config Section */
.health-config-section {
  margin-bottom: 24px;
}

.health-config-card {
  border-radius: 12px;
  background: white;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.config-item {
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
}

.config-label {
  font-size: 11px;
  color: #64748b;
  margin-bottom: 4px;
}

.config-value {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

/* SLO Section */
.slo-section {
  margin-bottom: 24px;
}

.slo-card {
  border-radius: 12px;
  background: white;
}

.slo-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.slo-item {
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
  text-align: center;
}

.slo-label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.slo-value {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.slo-target {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 6px;
}

/* Footer Actions */
.footer-actions {
  margin-top: 8px;
}

.action-group {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Responsive */
@media (max-width: 1200px) {
  .services-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-section {
    grid-template-columns: 1fr;
  }

  .status-grid,
  .config-grid,
  .slo-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .services-grid {
    grid-template-columns: 1fr;
  }

  .status-grid,
  .config-grid,
  .slo-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .header-right {
    flex-wrap: wrap;
  }

  .status-header {
    flex-wrap: wrap;
  }

  .action-group {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>