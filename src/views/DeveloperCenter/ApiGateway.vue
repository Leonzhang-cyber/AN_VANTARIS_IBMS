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
  List, Download as DownloadIcon
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing API Gateway...',
  'Loading API endpoints...',
  'Checking gateway status...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedStatus = ref('all')
const selectedCategory = ref('all')
const detailsVisible = ref(false)
const createApiVisible = ref(false)
const editApiVisible = ref(false)
const chartRef = ref(null)

let trafficChart: echarts.ECharts | null = null

// Status filters
const statusOptions = [
  { value: 'all', label: 'All Status' },
  { value: 'active', label: 'Active', color: '#67C23A' },
  { value: 'inactive', label: 'Inactive', color: '#909399' },
  { value: 'deprecated', label: 'Deprecated', color: '#E6A23C' }
]

// Category filters
const categoryOptions = [
  { value: 'all', label: 'All Categories' },
  { value: 'system', label: 'System APIs' },
  { value: 'data', label: 'Data APIs' },
  { value: 'control', label: 'Control APIs' },
  { value: 'analytics', label: 'Analytics APIs' }
]

// API endpoints data
const apis = ref([
  {
    id: 'API001', name: 'System Health API', endpoint: '/api/v1/health', method: 'GET',
    category: 'system', status: 'active', version: '2.1.0',
    requests: 125430, avgLatency: 45, errorRate: 0.12,
    lastUpdated: '2024-01-15', createdBy: 'System Team',
    description: 'Retrieves real-time system health metrics and status'
  },
  {
    id: 'API002', name: 'Device Management API', endpoint: '/api/v1/devices', method: 'GET,POST,PUT',
    category: 'system', status: 'active', version: '3.0.0',
    requests: 89450, avgLatency: 78, errorRate: 0.24,
    lastUpdated: '2024-01-14', createdBy: 'Device Team',
    description: 'CRUD operations for managing IoT devices and equipment'
  },
  {
    id: 'API003', name: 'Energy Data API', endpoint: '/api/v1/energy', method: 'GET',
    category: 'data', status: 'active', version: '1.8.0',
    requests: 245670, avgLatency: 32, errorRate: 0.08,
    lastUpdated: '2024-01-13', createdBy: 'Energy Team',
    description: 'Provides energy consumption and analytics data'
  },
  {
    id: 'API004', name: 'Control Commands API', endpoint: '/api/v1/control', method: 'POST',
    category: 'control', status: 'active', version: '2.2.0',
    requests: 45230, avgLatency: 125, errorRate: 0.45,
    lastUpdated: '2024-01-12', createdBy: 'Automation Team',
    description: 'Send control commands to building systems'
  },
  {
    id: 'API005', name: 'Alerts Webhook', endpoint: '/webhook/alerts', method: 'POST',
    category: 'system', status: 'active', version: '1.5.0',
    requests: 32450, avgLatency: 28, errorRate: 0.05,
    lastUpdated: '2024-01-11', createdBy: 'Security Team',
    description: 'Webhook endpoint for alert notifications'
  },
  {
    id: 'API006', name: 'Historical Data API', endpoint: '/api/v1/history', method: 'GET',
    category: 'data', status: 'active', version: '2.0.0',
    requests: 156780, avgLatency: 156, errorRate: 0.32,
    lastUpdated: '2024-01-10', createdBy: 'Data Team',
    description: 'Retrieves historical telemetry and event data'
  },
  {
    id: 'API007', name: 'Predictive Analytics API', endpoint: '/api/v1/predict', method: 'POST',
    category: 'analytics', status: 'inactive', version: '0.9.0',
    requests: 5670, avgLatency: 245, errorRate: 1.2,
    lastUpdated: '2024-01-09', createdBy: 'AI Team',
    description: 'Machine learning prediction endpoints'
  },
  {
    id: 'API008', name: 'User Authentication API', endpoint: '/api/v1/auth', method: 'POST',
    category: 'system', status: 'active', version: '3.1.0',
    requests: 345670, avgLatency: 23, errorRate: 0.15,
    lastUpdated: '2024-01-08', createdBy: 'Security Team',
    description: 'Authentication and authorization endpoints'
  }
])

// API statistics
const apiStats = reactive({
  total: 0,
  active: 0,
  inactive: 0,
  deprecated: 0,
  totalRequests: 0,
  avgLatency: 0,
  avgErrorRate: 0,
  uptime: 99.95
})

// Traffic data for chart
const trafficData = ref([
  { time: '00:00', requests: 12450, latency: 45 },
  { time: '04:00', requests: 8970, latency: 42 },
  { time: '08:00', requests: 23450, latency: 58 },
  { time: '12:00', requests: 34560, latency: 62 },
  { time: '16:00', requests: 28760, latency: 55 },
  { time: '20:00', requests: 18940, latency: 48 },
  { time: '23:00', requests: 12560, latency: 44 }
])

// Create API form
const createApiForm = reactive({
  name: '',
  endpoint: '',
  method: 'GET',
  category: 'system',
  description: '',
  version: '1.0.0'
})

// Edit API form
const editApiForm = reactive({
  id: '',
  name: '',
  endpoint: '',
  method: '',
  category: '',
  status: '',
  version: '',
  description: ''
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 8,
  total: apis.value.length
})

// Filtered APIs
const filteredApis = computed(() => {
  let filtered = apis.value
  if (searchKeyword.value) {
    filtered = filtered.filter(a =>
        a.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        a.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        a.endpoint.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(a => a.status === selectedStatus.value)
  }
  if (selectedCategory.value !== 'all') {
    filtered = filtered.filter(a => a.category === selectedCategory.value)
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

  trafficChart = echarts.init(chartRef.value)
  trafficChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Requests (K)', 'Latency (ms)'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: trafficData.value.map(t => t.time) },
    yAxis: [
      { type: 'value', name: 'Requests (K)' },
      { type: 'value', name: 'Latency (ms)' }
    ],
    series: [
      { name: 'Requests (K)', type: 'bar', data: trafficData.value.map(t => t.requests / 1000), itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top', formatter: '{c}K' } },
      { name: 'Latency (ms)', type: 'line', data: trafficData.value.map(t => t.latency), smooth: true, lineStyle: { color: '#E6A23C', width: 2 }, symbol: 'circle', symbolSize: 8, yAxisIndex: 1 }
    ]
  })
}

const updateStats = () => {
  apiStats.total = apis.value.length
  apiStats.active = apis.value.filter(a => a.status === 'active').length
  apiStats.inactive = apis.value.filter(a => a.status === 'inactive').length
  apiStats.deprecated = apis.value.filter(a => a.status === 'deprecated').length
  apiStats.totalRequests = apis.value.reduce((sum, a) => sum + a.requests, 0)
  apiStats.avgLatency = Math.round(apis.value.reduce((sum, a) => sum + a.avgLatency, 0) / apis.value.length)
  apiStats.avgErrorRate = parseFloat((apis.value.reduce((sum, a) => sum + a.errorRate, 0) / apis.value.length).toFixed(2))
}

const handleResize = () => {
  trafficChart?.resize()
}

// ==================== API Functions ====================
const refreshApis = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  loading.value = false
  ElMessage.success('API Gateway refreshed successfully')
}

const viewApiDetails = (api: any) => {
  selectedApi.value = api
  detailsVisible.value = true
}

const editApi = (api: any) => {
  editApiForm.id = api.id
  editApiForm.name = api.name
  editApiForm.endpoint = api.endpoint
  editApiForm.method = api.method
  editApiForm.category = api.category
  editApiForm.status = api.status
  editApiForm.version = api.version
  editApiForm.description = api.description
  editApiVisible.value = true
}

const saveApiEdit = async () => {
  if (!editApiForm.name) {
    ElMessage.warning('Please enter an API name')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1000))

  const index = apis.value.findIndex(a => a.id === editApiForm.id)
  if (index !== -1) {
    apis.value[index] = {
      ...apis.value[index],
      name: editApiForm.name,
      endpoint: editApiForm.endpoint,
      method: editApiForm.method,
      category: editApiForm.category,
      status: editApiForm.status,
      version: editApiForm.version,
      description: editApiForm.description,
      lastUpdated: new Date().toISOString().split('T')[0]
    }
  }

  updateStats()
  editApiVisible.value = false
  ElMessage.success('API updated successfully')
}

const deleteApi = async (api: any) => {
  await ElMessageBox.confirm(
      `Delete API "${api.name}"? This action cannot be undone.`,
      'Confirm Delete',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'danger'
      }
  )

  const index = apis.value.findIndex(a => a.id === api.id)
  if (index !== -1) {
    apis.value.splice(index, 1)
  }

  updateStats()
  initChart()
  ElMessage.success('API deleted successfully')
}

const toggleApiStatus = async (api: any) => {
  const newStatus = api.status === 'active' ? 'inactive' : 'active'
  const action = newStatus === 'active' ? 'activate' : 'deactivate'

  await ElMessageBox.confirm(
      `${action === 'activate' ? 'Activate' : 'Deactivate'} API "${api.name}"?`,
      'Confirm',
      {
        confirmButtonText: action === 'activate' ? 'Activate' : 'Deactivate',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  )

  const index = apis.value.findIndex(a => a.id === api.id)
  if (index !== -1) {
    apis.value[index].status = newStatus
  }

  updateStats()
  ElMessage.success(`API ${action}d successfully`)
}

const openCreateApi = () => {
  createApiForm.name = ''
  createApiForm.endpoint = ''
  createApiForm.method = 'GET'
  createApiForm.category = 'system'
  createApiForm.description = ''
  createApiForm.version = '1.0.0'
  createApiVisible.value = true
}

const createApi = async () => {
  if (!createApiForm.name) {
    ElMessage.warning('Please enter an API name')
    return
  }

  if (!createApiForm.endpoint) {
    ElMessage.warning('Please enter an endpoint')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1000))

  const newApi = {
    id: `API${String(apis.value.length + 1).padStart(3, '0')}`,
    name: createApiForm.name,
    endpoint: createApiForm.endpoint,
    method: createApiForm.method,
    category: createApiForm.category,
    status: 'inactive',
    version: createApiForm.version,
    requests: 0,
    avgLatency: 0,
    errorRate: 0,
    lastUpdated: new Date().toISOString().split('T')[0],
    createdBy: 'Current User',
    description: createApiForm.description || 'New API endpoint'
  }

  apis.value.unshift(newApi)
  updateStats()
  initChart()
  createApiVisible.value = false
  ElMessage.success('API created successfully')
}

const testApi = (api: any) => {
  ElMessage.info(`Testing connection to ${api.name}...`)
  setTimeout(() => {
    ElMessage.success(`${api.name} is responding normally`)
  }, 1000)
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

const getStatusType = (status: string) => {
  switch (status) {
    case 'active': return 'success'
    case 'inactive': return 'info'
    case 'deprecated': return 'warning'
    default: return 'info'
  }
}

const getCategoryIcon = (category: string) => {
  switch (category) {
    case 'system': return '🖥️'
    case 'data': return '📊'
    case 'control': return '🎮'
    case 'analytics': return '📈'
    default: return '🔌'
  }
}

const formatNumber = (num: number) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const selectedApi = ref<any>(null)
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
          <span class="loading-title">Loading API Gateway</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Developer Center - API Gateway</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="api-gateway-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">API Gateway</h1>
        <p class="page-subtitle">Centralized API management and monitoring platform</p>
      </div>
      <div class="header-right">
        <el-button type="primary" size="large" @click="openCreateApi">
          <el-icon><Plus /></el-icon>
          Create API
        </el-button>
        <el-button size="large" @click="refreshApis" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total-icon">
          <el-icon><SuccessFilled /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ apiStats.total }}</div>
          <div class="stat-label">Total APIs</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ apiStats.active }} Active</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon requests-icon">
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ formatNumber(apiStats.totalRequests) }}</div>
          <div class="stat-label">Total Requests</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+18% this month</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon latency-icon">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ apiStats.avgLatency }}ms</div>
          <div class="stat-label">Avg Latency</div>
        </div>
        <div class="stat-trend">
          <el-progress :percentage="100 - apiStats.avgErrorRate" :stroke-width="4" :show-text="false" />
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon uptime-icon">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ apiStats.uptime }}%</div>
          <div class="stat-label">Uptime</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">99.99% SLA</span>
        </div>
      </div>
    </div>

    <!-- Traffic Chart -->
    <div class="chart-section">
      <div class="section-header">
        <h3>API Traffic & Latency Trends</h3>
        <el-button text type="primary" @click="initChart">Refresh</el-button>
      </div>
      <div ref="chartRef" class="traffic-chart" style="height: 320px"></div>
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
        <div class="status-filters">
          <span class="filter-label">Status:</span>
          <button
              v-for="s in statusOptions"
              :key="s.value"
              class="status-chip"
              :class="{ active: selectedStatus === s.value }"
              @click="selectedStatus = s.value"
          >
            <span class="chip-dot" :style="{ background: s.color }"></span>
            <span>{{ s.label }}</span>
          </button>
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
            <span class="chip-icon">{{ getCategoryIcon(c.value) }}</span>
            <span>{{ c.label }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- APIs Grid -->
    <div class="apis-grid">
      <div
          v-for="api in filteredApis"
          :key="api.id"
          class="api-card"
          :class="api.status"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="api-category">
            <span class="category-icon">{{ getCategoryIcon(api.category) }}</span>
            <span class="category-name">{{ api.category.toUpperCase() }}</span>
          </div>
          <div class="api-status">
            <el-tag :type="getStatusType(api.status)" size="small" effect="light">
              {{ api.status.toUpperCase() }}
            </el-tag>
          </div>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <h4 class="api-name">{{ api.name }}</h4>
          <div class="api-endpoint">
            <el-tag :type="getMethodType(api.method)" size="small">{{ api.method }}</el-tag>
            <code class="endpoint-text">{{ api.endpoint }}</code>
          </div>
          <p class="api-description">{{ api.description }}</p>

          <!-- Metrics -->
          <div class="api-metrics">
            <div class="metric">
              <span class="metric-label">Requests</span>
              <span class="metric-value">{{ formatNumber(api.requests) }}</span>
            </div>
            <div class="metric">
              <span class="metric-label">Latency</span>
              <span class="metric-value">{{ api.avgLatency }}ms</span>
            </div>
            <div class="metric">
              <span class="metric-label">Error Rate</span>
              <span class="metric-value" :class="{ 'high-error': api.errorRate > 0.5 }">
                {{ api.errorRate }}%
              </span>
            </div>
            <div class="metric">
              <span class="metric-label">Version</span>
              <span class="metric-value">v{{ api.version }}</span>
            </div>
          </div>

          <!-- Meta Info -->
          <div class="meta-info">
            <div class="meta-item">
              <span class="meta-label">Last Updated:</span>
              <span class="meta-value">{{ api.lastUpdated }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Created By:</span>
              <span class="meta-value">{{ api.createdBy }}</span>
            </div>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="card-actions">
            <el-button size="small" @click="viewApiDetails(api)">
              <el-icon><Eye /></el-icon> Details
            </el-button>
            <el-button size="small" @click="testApi(api)">
              <el-icon><Link /></el-icon> Test
            </el-button>
            <el-button size="small" type="primary" @click="editApi(api)">
              <el-icon><Edit /></el-icon> Edit
            </el-button>
            <el-button
                size="small"
                :type="api.status === 'active' ? 'warning' : 'success'"
                @click="toggleApiStatus(api)"
            >
              {{ api.status === 'active' ? 'Deactivate' : 'Activate' }}
            </el-button>
            <el-button size="small" type="danger" @click="deleteApi(api)">
              <el-icon><Delete /></el-icon> Delete
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredApis.length === 0" class="empty-state">
      <el-empty description="No APIs found">
        <el-button type="primary" @click="openCreateApi">Create API</el-button>
      </el-empty>
    </div>

    <!-- Pagination -->
    <div v-if="filteredApis.length > 0" class="pagination-wrapper">
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

    <!-- API Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="selectedApi?.name" width="650px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="API ID">{{ selectedApi?.id }}</el-descriptions-item>
        <el-descriptions-item label="Version">{{ selectedApi?.version }}</el-descriptions-item>
        <el-descriptions-item label="Endpoint">{{ selectedApi?.endpoint }}</el-descriptions-item>
        <el-descriptions-item label="Method">
          <el-tag :type="getMethodType(selectedApi?.method)" size="small">{{ selectedApi?.method }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Category">{{ selectedApi?.category?.toUpperCase() }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusType(selectedApi?.status)" size="small">
            {{ selectedApi?.status?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Total Requests">{{ formatNumber(selectedApi?.requests) }}</el-descriptions-item>
        <el-descriptions-item label="Avg Latency">{{ selectedApi?.avgLatency }}ms</el-descriptions-item>
        <el-descriptions-item label="Error Rate">{{ selectedApi?.errorRate }}%</el-descriptions-item>
        <el-descriptions-item label="Last Updated">{{ selectedApi?.lastUpdated }}</el-descriptions-item>
        <el-descriptions-item label="Created By">{{ selectedApi?.createdBy }}</el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedApi?.description }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
        <el-button type="primary" @click="testApi(selectedApi)">Test API</el-button>
      </template>
    </el-dialog>

    <!-- Create API Dialog -->
    <el-dialog v-model="createApiVisible" title="Create New API" width="550px">
      <el-form :model="createApiForm" label-width="100px">
        <el-form-item label="API Name" required>
          <el-input v-model="createApiForm.name" placeholder="Enter API name" />
        </el-form-item>
        <el-form-item label="Endpoint" required>
          <el-input v-model="createApiForm.endpoint" placeholder="/api/v1/endpoint" />
        </el-form-item>
        <el-form-item label="HTTP Method">
          <el-select v-model="createApiForm.method" style="width: 100%">
            <el-option label="GET" value="GET" />
            <el-option label="POST" value="POST" />
            <el-option label="PUT" value="PUT" />
            <el-option label="DELETE" value="DELETE" />
          </el-select>
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="createApiForm.category" style="width: 100%">
            <el-option v-for="c in categoryOptions.slice(1)" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Version">
          <el-input v-model="createApiForm.version" placeholder="1.0.0" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="createApiForm.description" type="textarea" rows="2" placeholder="API description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createApiVisible = false">Cancel</el-button>
        <el-button type="primary" @click="createApi">Create API</el-button>
      </template>
    </el-dialog>

    <!-- Edit API Dialog -->
    <el-dialog v-model="editApiVisible" title="Edit API" width="550px">
      <el-form :model="editApiForm" label-width="100px">
        <el-form-item label="API Name" required>
          <el-input v-model="editApiForm.name" placeholder="Enter API name" />
        </el-form-item>
        <el-form-item label="Endpoint">
          <el-input v-model="editApiForm.endpoint" placeholder="/api/v1/endpoint" />
        </el-form-item>
        <el-form-item label="HTTP Method">
          <el-select v-model="editApiForm.method" style="width: 100%">
            <el-option label="GET" value="GET" />
            <el-option label="POST" value="POST" />
            <el-option label="PUT" value="PUT" />
            <el-option label="DELETE" value="DELETE" />
          </el-select>
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="editApiForm.category" style="width: 100%">
            <el-option v-for="c in categoryOptions.slice(1)" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Status">
          <el-select v-model="editApiForm.status" style="width: 100%">
            <el-option label="Active" value="active" />
            <el-option label="Inactive" value="inactive" />
            <el-option label="Deprecated" value="deprecated" />
          </el-select>
        </el-form-item>
        <el-form-item label="Version">
          <el-input v-model="editApiForm.version" placeholder="1.0.0" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="editApiForm.description" type="textarea" rows="2" placeholder="API description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editApiVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveApiEdit">Save Changes</el-button>
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
.api-gateway-container {
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

.requests-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.latency-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.uptime-icon {
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

.traffic-chart {
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

.status-filters,
.category-filters {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.status-chip,
.category-chip {
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

.status-chip:hover,
.category-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.status-chip.active,
.category-chip.active {
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

.chip-icon {
  font-size: 14px;
}

/* APIs Grid */
.apis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.api-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
}

.api-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.api-card.active {
  border-left: 4px solid #67c23a;
}

.api-card.inactive {
  border-left: 4px solid #909399;
}

.api-card.deprecated {
  border-left: 4px solid #e6a23c;
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
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.api-endpoint {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.endpoint-text {
  font-size: 12px;
  font-family: monospace;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 4px;
  color: #606266;
}

.api-description {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.api-metrics {
  display: flex;
  justify-content: space-around;
  margin-bottom: 16px;
  padding: 12px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.metric {
  text-align: center;
}

.metric-label {
  font-size: 11px;
  color: #909399;
  display: block;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.metric-value.high-error {
  color: #f56c6c;
}

.meta-info {
  margin-bottom: 8px;
}

.meta-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  margin-bottom: 4px;
}

.meta-label {
  color: #909399;
}

.meta-value {
  color: #1e293b;
  font-weight: 500;
}

/* Card Footer */
.card-footer {
  padding: 12px 20px 16px 20px;
  border-top: 1px solid #f0f0f0;
  background: #fafbfc;
}

.card-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
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

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .apis-grid {
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  }
}

@media (max-width: 768px) {
  .api-gateway-container {
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

  .status-filters,
  .category-filters {
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

  .apis-grid {
    grid-template-columns: 1fr;
  }

  .api-metrics {
    flex-direction: column;
    gap: 8px;
  }

  .card-actions {
    flex-direction: column;
  }

  .card-actions .el-button {
    width: 100%;
  }

  .api-endpoint {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>