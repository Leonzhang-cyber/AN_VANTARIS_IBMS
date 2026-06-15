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
  EditPen, Tickets, Filter, SuccessFilled,
  List, Download as DownloadIcon,
  Printer, Link, Files
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Loading API documentation...',
  'Building documentation index...',
  'Preparing code examples...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedCategory = ref('all')
const selectedVersion = ref('all')
const detailsVisible = ref(false)
const selectedApiDoc = ref<any>(null)
const chartRef = ref(null)

let usageChart: echarts.ECharts | null = null

// Category filters
const categoryOptions = [
  { value: 'all', label: 'All Categories' },
  { value: 'system', label: 'System APIs', icon: '🖥️' },
  { value: 'data', label: 'Data APIs', icon: '📊' },
  { value: 'control', label: 'Control APIs', icon: '🎮' },
  { value: 'analytics', label: 'Analytics APIs', icon: '📈' },
  { value: 'auth', label: 'Authentication', icon: '🔐' }
]

// Version filters
const versionOptions = [
  { value: 'all', label: 'All Versions' },
  { value: 'v3', label: 'v3.0' },
  { value: 'v2', label: 'v2.0' },
  { value: 'v1', label: 'v1.0' }
]

// API documentation data
const apiDocs = ref([
  {
    id: 'DOC001', name: 'System Health API', category: 'system', version: 'v2.1',
    endpoint: '/api/v2/health', method: 'GET', deprecated: false,
    lastUpdated: '2024-01-15', popularity: 95, usageCount: 125430,
    description: 'Retrieves real-time system health metrics and component status',
    parameters: [
      { name: 'format', type: 'string', required: false, description: 'Response format (json/xml)' },
      { name: 'detailed', type: 'boolean', required: false, description: 'Include detailed metrics' }
    ],
    responses: [
      { code: 200, description: 'Successful response', example: '{"status": "healthy", "uptime": "99.95%"}' },
      { code: 503, description: 'Service unavailable' }
    ],
    authentication: 'API Key',
    rateLimit: '1000 requests/hour'
  },
  {
    id: 'DOC002', name: 'Device Management API', category: 'system', version: 'v3.0',
    endpoint: '/api/v3/devices', method: 'GET,POST,PUT', deprecated: false,
    lastUpdated: '2024-01-14', popularity: 98, usageCount: 89450,
    description: 'CRUD operations for managing IoT devices and equipment',
    parameters: [
      { name: 'limit', type: 'integer', required: false, description: 'Number of results per page' },
      { name: 'offset', type: 'integer', required: false, description: 'Pagination offset' },
      { name: 'type', type: 'string', required: false, description: 'Filter by device type' }
    ],
    responses: [
      { code: 200, description: 'Successful response', example: '{"devices": [], "total": 100}' },
      { code: 400, description: 'Bad request' },
      { code: 401, description: 'Unauthorized' }
    ],
    authentication: 'OAuth 2.0',
    rateLimit: '500 requests/hour'
  },
  {
    id: 'DOC003', name: 'Energy Data API', category: 'data', version: 'v1.8',
    endpoint: '/api/v1/energy', method: 'GET', deprecated: false,
    lastUpdated: '2024-01-13', popularity: 99, usageCount: 245670,
    description: 'Provides energy consumption and analytics data',
    parameters: [
      { name: 'start_date', type: 'string', required: true, description: 'Start date (YYYY-MM-DD)' },
      { name: 'end_date', type: 'string', required: true, description: 'End date (YYYY-MM-DD)' },
      { name: 'interval', type: 'string', required: false, description: 'Data interval (hour/day/month)' }
    ],
    responses: [
      { code: 200, description: 'Successful response', example: '{"consumption": 12450, "unit": "kWh"}' },
      { code: 400, description: 'Invalid date range' }
    ],
    authentication: 'API Key',
    rateLimit: '2000 requests/hour'
  },
  {
    id: 'DOC004', name: 'Control Commands API', category: 'control', version: 'v2.2',
    endpoint: '/api/v2/control', method: 'POST', deprecated: false,
    lastUpdated: '2024-01-12', popularity: 88, usageCount: 45230,
    description: 'Send control commands to building systems',
    parameters: [
      { name: 'device_id', type: 'string', required: true, description: 'Target device ID' },
      { name: 'command', type: 'string', required: true, description: 'Command to execute' },
      { name: 'parameters', type: 'object', required: false, description: 'Command parameters' }
    ],
    responses: [
      { code: 200, description: 'Command accepted', example: '{"status": "success", "command_id": "cmd123"}' },
      { code: 403, description: 'Forbidden - Insufficient permissions' }
    ],
    authentication: 'OAuth 2.0',
    rateLimit: '100 requests/hour'
  },
  {
    id: 'DOC005', name: 'Alerts Webhook', category: 'system', version: 'v1.5',
    endpoint: '/webhook/alerts', method: 'POST', deprecated: false,
    lastUpdated: '2024-01-11', popularity: 85, usageCount: 32450,
    description: 'Webhook endpoint for receiving alert notifications',
    parameters: [
      { name: 'callback_url', type: 'string', required: true, description: 'URL to send alerts to' },
      { name: 'severity', type: 'string', required: false, description: 'Minimum severity level' }
    ],
    responses: [
      { code: 200, description: 'Webhook registered', example: '{"webhook_id": "wh_123"}' },
      { code: 400, description: 'Invalid callback URL' }
    ],
    authentication: 'API Key',
    rateLimit: '50 requests/hour'
  },
  {
    id: 'DOC006', name: 'Historical Data API', category: 'data', version: 'v2.0',
    endpoint: '/api/v2/history', method: 'GET', deprecated: false,
    lastUpdated: '2024-01-10', popularity: 92, usageCount: 156780,
    description: 'Retrieves historical telemetry and event data',
    parameters: [
      { name: 'metric', type: 'string', required: true, description: 'Metric name' },
      { name: 'from', type: 'timestamp', required: true, description: 'Start timestamp' },
      { name: 'to', type: 'timestamp', required: true, description: 'End timestamp' },
      { name: 'aggregation', type: 'string', required: false, description: 'Aggregation method' }
    ],
    responses: [
      { code: 200, description: 'Successful response', example: '{"data": [], "count": 1000}' },
      { code: 404, description: 'Metric not found' }
    ],
    authentication: 'API Key',
    rateLimit: '1000 requests/hour'
  },
  {
    id: 'DOC007', name: 'Predictive Analytics API', category: 'analytics', version: 'v0.9',
    endpoint: '/api/v1/predict', method: 'POST', deprecated: true,
    lastUpdated: '2024-01-09', popularity: 45, usageCount: 5670,
    description: 'Machine learning prediction endpoints (deprecated - use v2.0)',
    parameters: [
      { name: 'model_id', type: 'string', required: true, description: 'Model identifier' },
      { name: 'features', type: 'object', required: true, description: 'Input features' }
    ],
    responses: [
      { code: 200, description: 'Prediction result', example: '{"prediction": 0.85, "confidence": 0.92}' }
    ],
    authentication: 'API Key',
    rateLimit: '100 requests/hour'
  },
  {
    id: 'DOC008', name: 'Authentication API', category: 'auth', version: 'v3.1',
    endpoint: '/api/v3/auth', method: 'POST', deprecated: false,
    lastUpdated: '2024-01-08', popularity: 100, usageCount: 345670,
    description: 'Authentication and token management endpoints',
    parameters: [
      { name: 'username', type: 'string', required: true, description: 'User username' },
      { name: 'password', type: 'string', required: true, description: 'User password' },
      { name: 'grant_type', type: 'string', required: true, description: 'OAuth grant type' }
    ],
    responses: [
      { code: 200, description: 'Authentication successful', example: '{"access_token": "eyJ...", "expires_in": 3600}' },
      { code: 401, description: 'Invalid credentials' }
    ],
    authentication: 'None',
    rateLimit: '10 requests/minute'
  }
])

// Documentation statistics
const docStats = reactive({
  total: 0,
  active: 0,
  deprecated: 0,
  totalEndpoints: 0,
  totalMethods: 0,
  avgPopularity: 0,
  totalUsage: 0
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 8,
  total: apiDocs.value.length
})

// Filtered docs
const filteredDocs = computed(() => {
  let filtered = apiDocs.value
  if (searchKeyword.value) {
    filtered = filtered.filter(d =>
        d.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        d.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        d.description.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        d.endpoint.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedCategory.value !== 'all') {
    filtered = filtered.filter(d => d.category === selectedCategory.value)
  }
  if (selectedVersion.value !== 'all') {
    filtered = filtered.filter(d => d.version.startsWith(selectedVersion.value))
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

  usageChart = echarts.init(chartRef.value)
  usageChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Usage Count (K)', 'Popularity Score'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: apiDocs.value.map(d => d.name.substring(0, 15)), axisLabel: { rotate: 30, interval: 0 } },
    yAxis: [
      { type: 'value', name: 'Usage (K)' },
      { type: 'value', name: 'Popularity Score', min: 0, max: 100 }
    ],
    series: [
      { name: 'Usage Count (K)', type: 'bar', data: apiDocs.value.map(d => d.usageCount / 1000), itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top', formatter: '{c}K' } },
      { name: 'Popularity Score', type: 'line', data: apiDocs.value.map(d => d.popularity), smooth: true, lineStyle: { color: '#E6A23C', width: 2 }, symbol: 'circle', symbolSize: 8, yAxisIndex: 1 }
    ]
  })
}

const updateStats = () => {
  docStats.total = apiDocs.value.length
  docStats.active = apiDocs.value.filter(d => !d.deprecated).length
  docStats.deprecated = apiDocs.value.filter(d => d.deprecated).length
  docStats.totalEndpoints = apiDocs.value.length
  docStats.totalMethods = apiDocs.value.reduce((sum, d) => sum + d.method.split(',').length, 0)
  docStats.avgPopularity = Math.round(apiDocs.value.reduce((sum, d) => sum + d.popularity, 0) / apiDocs.value.length)
  docStats.totalUsage = apiDocs.value.reduce((sum, d) => sum + d.usageCount, 0)
}

const handleResize = () => {
  usageChart?.resize()
}

// ==================== Documentation Functions ====================
const refreshDocs = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  loading.value = false
  ElMessage.success('Documentation refreshed successfully')
}

const viewDocDetails = (doc: any) => {
  selectedApiDoc.value = doc
  detailsVisible.value = true
}

const downloadDocs = () => {
  ElMessage.info('Preparing documentation download...')
  setTimeout(() => {
    ElMessage.success('Documentation downloaded successfully')
  }, 1000)
}

const copyEndpoint = (endpoint: string) => {
  navigator.clipboard.writeText(endpoint)
  ElMessage.success('Endpoint copied to clipboard')
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getMethodType = (method: string) => {
  const methods = method.split(',')
  const firstMethod = methods[0].trim()
  switch (firstMethod) {
    case 'GET': return 'primary'
    case 'POST': return 'success'
    case 'PUT': return 'warning'
    case 'DELETE': return 'danger'
    default: return 'info'
  }
}

const getCategoryIcon = (category: string) => {
  switch (category) {
    case 'system': return '🖥️'
    case 'data': return '📊'
    case 'control': return '🎮'
    case 'analytics': return '📈'
    case 'auth': return '🔐'
    default: return '🔌'
  }
}

const getPopularityClass = (score: number) => {
  if (score >= 90) return 'popularity-high'
  if (score >= 70) return 'popularity-medium'
  return 'popularity-low'
}

const formatNumber = (num: number) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
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
          <span class="loading-title">Loading API Documentation</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Developer Center - API Documentation</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="api-documentation-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">API Documentation</h1>
        <p class="page-subtitle">Complete reference for all available API endpoints</p>
      </div>
      <div class="header-right">
        <el-button type="primary" size="large" @click="downloadDocs">
          <el-icon><DownloadIcon /></el-icon>
          Download Docs
        </el-button>
        <el-button size="large" @click="refreshDocs" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon endpoints-icon">
          <el-icon><Api /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ docStats.totalEndpoints }}</div>
          <div class="stat-label">Total Endpoints</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ docStats.active }} Active</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon methods-icon">
          <el-icon><Command /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ docStats.totalMethods }}</div>
          <div class="stat-label">HTTP Methods</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+3 this month</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon usage-icon">
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ formatNumber(docStats.totalUsage) }}</div>
          <div class="stat-label">Total Requests</div>
        </div>
        <div class="stat-trend">
          <el-progress :percentage="docStats.avgPopularity" :stroke-width="4" :show-text="false" />
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon popularity-icon">
          <el-icon><Star /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ docStats.avgPopularity }}%</div>
          <div class="stat-label">Avg Popularity</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ docStats.deprecated }} Deprecated</span>
        </div>
      </div>
    </div>

    <!-- Usage Chart -->
    <div class="chart-section">
      <div class="section-header">
        <h3>API Usage & Popularity Trends</h3>
        <el-button text type="primary" @click="initChart">Refresh</el-button>
      </div>
      <div ref="chartRef" class="usage-chart" style="height: 320px"></div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-bar">
      <div class="filters-left">
        <div class="search-box">
          <el-input
              v-model="searchKeyword"
              placeholder="Search APIs..."
              :prefix-icon="Search"
              clearable
              style="width: 240px"
          />
        </div>
        <div class="category-filters">
          <span class="filter-label">Category:</span>
          <button
              v-for="c in categoryOptions"
              :key="c.value"
              class="category-chip"
              :class="{ active: selectedCategory === c.value }"
              @click="selectedCategory = c.value"
          >
            <span class="chip-icon">{{ c.icon }}</span>
            <span>{{ c.label }}</span>
          </button>
        </div>
        <div class="version-filters">
          <span class="filter-label">Version:</span>
          <button
              v-for="v in versionOptions"
              :key="v.value"
              class="version-chip"
              :class="{ active: selectedVersion === v.value }"
              @click="selectedVersion = v.value"
          >
            {{ v.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- Documentation Grid -->
    <div class="docs-grid">
      <div
          v-for="doc in filteredDocs"
          :key="doc.id"
          class="doc-card"
          :class="{ deprecated: doc.deprecated }"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="api-category">
            <span class="category-icon">{{ getCategoryIcon(doc.category) }}</span>
            <span class="category-name">{{ doc.category.toUpperCase() }}</span>
          </div>
          <div class="api-version">
            <el-tag size="small" type="info">{{ doc.version }}</el-tag>
          </div>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <h4 class="api-name">{{ doc.name }}</h4>
          <p class="api-description">{{ doc.description }}</p>

          <!-- Endpoint -->
          <div class="api-endpoint">
            <el-tag :type="getMethodType(doc.method)" size="small">{{ doc.method }}</el-tag>
            <code class="endpoint-text">{{ doc.endpoint }}</code>
            <el-button link size="small" @click="copyEndpoint(doc.endpoint)">
              <el-icon><CopyDocument /></el-icon>
            </el-button>
          </div>

          <!-- Quick Info -->
          <div class="quick-info">
            <div class="info-item">
              <span class="info-label">Auth:</span>
              <span class="info-value">{{ doc.authentication }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Rate Limit:</span>
              <span class="info-value">{{ doc.rateLimit }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Updated:</span>
              <span class="info-value">{{ doc.lastUpdated }}</span>
            </div>
          </div>

          <!-- Popularity Score -->
          <div class="popularity-section">
            <div class="popularity-header">
              <span>Popularity Score</span>
              <span class="popularity-value" :class="getPopularityClass(doc.popularity)">
                {{ doc.popularity }}%
              </span>
            </div>
            <div class="popularity-bar">
              <div class="bar-fill" :style="{ width: doc.popularity + '%', background: doc.popularity >= 90 ? '#67C23A' : doc.popularity >= 70 ? '#E6A23C' : '#F56C6C' }"></div>
            </div>
          </div>

          <!-- Usage Count -->
          <div class="usage-count">
            <el-icon><DataLine /></el-icon>
            <span>{{ formatNumber(doc.usageCount) }} requests</span>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="deprecated-badge" v-if="doc.deprecated">
            <el-tag type="danger" size="small">Deprecated</el-tag>
          </div>
          <div class="card-actions">
            <el-button size="small" type="primary" @click="viewDocDetails(doc)">
              <el-icon><Eye /></el-icon> View Docs
            </el-button>
            <el-button size="small" @click="copyEndpoint(doc.endpoint)">
              <el-icon><CopyDocument /></el-icon> Copy
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredDocs.length === 0" class="empty-state">
      <el-empty description="No API documentation found">
        <el-button type="primary">Browse All</el-button>
      </el-empty>
    </div>

    <!-- Pagination -->
    <div v-if="filteredDocs.length > 0" class="pagination-wrapper">
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

    <!-- API Documentation Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="selectedApiDoc?.name" width="750px" top="5vh">
      <div class="doc-details">
        <div class="doc-header">
          <div class="doc-meta">
            <el-tag :type="getMethodType(selectedApiDoc?.method)" size="large">{{ selectedApiDoc?.method }}</el-tag>
            <code class="doc-endpoint">{{ selectedApiDoc?.endpoint }}</code>
            <el-button link size="small" @click="copyEndpoint(selectedApiDoc?.endpoint)">
              <el-icon><CopyDocument /></el-icon>
            </el-button>
          </div>
          <div class="doc-badges">
            <el-tag type="info" size="small">Version: {{ selectedApiDoc?.version }}</el-tag>
            <el-tag v-if="selectedApiDoc?.deprecated" type="danger" size="small">Deprecated</el-tag>
          </div>
        </div>

        <el-divider />

        <div class="doc-section">
          <h4>Description</h4>
          <p>{{ selectedApiDoc?.description }}</p>
        </div>

        <div class="doc-section">
          <h4>Authentication</h4>
          <p><strong>{{ selectedApiDoc?.authentication }}</strong> - {{ selectedApiDoc?.authentication === 'None' ? 'No authentication required' : 'API key or token required' }}</p>
          <p><strong>Rate Limit:</strong> {{ selectedApiDoc?.rateLimit }}</p>
        </div>

        <div class="doc-section">
          <h4>Parameters</h4>
          <el-table :data="selectedApiDoc?.parameters" border stripe size="small">
            <el-table-column prop="name" label="Name" width="150" />
            <el-table-column prop="type" label="Type" width="100" />
            <el-table-column label="Required" width="80" align="center">
              <template #default="{ row }">
                <el-tag :type="row.required ? 'danger' : 'info'" size="small">
                  {{ row.required ? 'Yes' : 'No' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="Description" min-width="250" />
          </el-table>
        </div>

        <div class="doc-section">
          <h4>Responses</h4>
          <el-table :data="selectedApiDoc?.responses" border stripe size="small">
            <el-table-column prop="code" label="Status Code" width="100" />
            <el-table-column prop="description" label="Description" min-width="200" />
            <el-table-column prop="example" label="Example" min-width="250">
              <template #default="{ row }">
                <code v-if="row.example" class="example-code">{{ row.example }}</code>
                <span v-else>-</span>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="doc-section">
          <h4>Usage Statistics</h4>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="Total Requests">{{ formatNumber(selectedApiDoc?.usageCount) }}</el-descriptions-item>
            <el-descriptions-item label="Popularity Score">{{ selectedApiDoc?.popularity }}%</el-descriptions-item>
            <el-descriptions-item label="Last Updated">{{ selectedApiDoc?.lastUpdated }}</el-descriptions-item>
            <el-descriptions-item label="Deprecated">{{ selectedApiDoc?.deprecated ? 'Yes' : 'No' }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="doc-section">
          <h4>Try it out</h4>
          <el-alert
              title="Test this API endpoint"
              type="info"
              show-icon
              :closable="false"
          >
            <template #default>
              <p>Use the API test console in the API Gateway to test this endpoint with real data.</p>
              <el-button type="primary" size="small" style="margin-top: 8px">Go to API Gateway</el-button>
            </template>
          </el-alert>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
        <el-button type="primary" @click="copyEndpoint(selectedApiDoc?.endpoint)">Copy Endpoint</el-button>
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
.api-documentation-container {
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

.endpoints-icon {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #409eff;
}

.methods-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.usage-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.popularity-icon {
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
  font-size: 11px;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 20px;
}

.trend-up {
  color: #67c23a;
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

.usage-chart {
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

.category-filters,
.version-filters {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.category-chip,
.version-chip {
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

.category-chip:hover,
.version-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.category-chip.active,
.version-chip.active {
  background: #409eff;
  border-color: #409eff;
  color: white;
}

.chip-icon {
  font-size: 14px;
}

/* Documentation Grid */
.docs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.doc-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
}

.doc-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.doc-card.deprecated {
  opacity: 0.7;
  background: #fafbfc;
}

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 0 20px;
}

.api-category {
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-icon {
  font-size: 18px;
}

.category-name {
  font-size: 12px;
  font-weight: 600;
  color: #409eff;
  background: #e6f7ff;
  padding: 4px 8px;
  border-radius: 12px;
}

/* Card Body */
.card-body {
  padding: 16px 20px;
}

.api-name {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 10px 0;
  line-height: 1.4;
}

.api-description {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.api-endpoint {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
  background: #f8f9fa;
  padding: 8px 12px;
  border-radius: 8px;
}

.endpoint-text {
  font-size: 12px;
  font-family: monospace;
  color: #606266;
  flex: 1;
}

.quick-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 8px;
}

.info-item {
  display: flex;
  gap: 8px;
  font-size: 12px;
}

.info-label {
  color: #909399;
  font-weight: 500;
  min-width: 70px;
}

.info-value {
  color: #1e293b;
}

.popularity-section {
  margin-bottom: 12px;
}

.popularity-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 12px;
  color: #606266;
}

.popularity-value {
  font-weight: 600;
}

.popularity-high {
  color: #67c23a;
}

.popularity-medium {
  color: #e6a23c;
}

.popularity-low {
  color: #f56c6c;
}

.popularity-bar {
  height: 6px;
  background: #e4e7ed;
  border-radius: 3px;
  overflow: hidden;
}

.popularity-bar .bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.usage-count {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
}

/* Card Footer */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px 16px 20px;
  border-top: 1px solid #f0f0f0;
  background: #fafbfc;
}

.deprecated-badge {
  flex: 1;
}

.card-actions {
  display: flex;
  gap: 8px;
}

/* Empty State */
.empty-state {
  padding: 60px 0;
  text-align: center;
}

/* Pagination */
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
}

/* Dialog Styles */
.doc-details {
  max-height: 60vh;
  overflow-y: auto;
}

.doc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.doc-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.doc-endpoint {
  font-size: 14px;
  font-family: monospace;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 4px;
}

.doc-badges {
  display: flex;
  gap: 8px;
}

.doc-section {
  margin-bottom: 24px;
}

.doc-section h4 {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 12px 0;
  color: #1e293b;
}

.example-code {
  font-family: monospace;
  font-size: 11px;
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .docs-grid {
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  }
}

@media (max-width: 768px) {
  .api-documentation-container {
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

  .category-filters,
  .version-filters {
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
    flex-wrap: wrap;
  }

  .docs-grid {
    grid-template-columns: 1fr;
  }

  .api-endpoint {
    flex-wrap: wrap;
  }

  .card-actions {
    flex-direction: column;
  }

  .card-actions .el-button {
    width: 100%;
  }

  .doc-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>