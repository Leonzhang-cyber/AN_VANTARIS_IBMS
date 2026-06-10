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
  Key, Grid, Collection, Platform, Service
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing API gateway...',
  'Loading endpoints...',
  'Almost ready...'
]

// ==================== Chart Refs ====================
const apiUsageChart = ref<HTMLElement | null>(null)
const responseTimeChart = ref<HTMLElement | null>(null)
const statusCodeChart = ref<HTMLElement | null>(null)

// ==================== State ====================
const activeTab = ref('apis')
const searchKeyword = ref('')
const methodFilter = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(15)
const apiDialogVisible = ref(false)
const keyDialogVisible = ref(false)
const docsDialogVisible = ref(false)
const testDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const selectedApi = ref<any>(null)
const apiFormRef = ref()
const testing = ref(false)
const testResult = ref<any>(null)
const testPayload = ref('')
const activeApiTab = ref('info')

// ==================== Statistics ====================
const statistics = reactive({
  totalApis: 24,
  activeApis: 18,
  totalRequests: 156800,
  avgResponseTime: 124,
  successRate: 99.2,
  totalApiKeys: 32
})

// ==================== API Data ====================
interface ApiEndpoint {
  id: number
  name: string
  path: string
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  description: string
  version: string
  status: 'active' | 'inactive' | 'deprecated'
  authentication: 'none' | 'api_key' | 'oauth2' | 'jwt'
  rateLimit: number
  rateLimitPeriod: 'minute' | 'hour' | 'day'
  tags: string[]
  createdAt: string
  updatedAt: string
  documentationUrl?: string
  exampleRequest?: string
  exampleResponse?: string
}

const apis = ref<ApiEndpoint[]>([
  {
    id: 1,
    name: 'Get Device Status',
    path: '/api/v1/devices/{deviceId}/status',
    method: 'GET',
    description: 'Retrieve the current status and telemetry of a specific device',
    version: 'v1',
    status: 'active',
    authentication: 'api_key',
    rateLimit: 100,
    rateLimitPeriod: 'minute',
    tags: ['devices', 'telemetry'],
    createdAt: '2024-01-10',
    updatedAt: '2024-01-15',
    exampleRequest: 'GET /api/v1/devices/ESP32_001/status',
    exampleResponse: '{"deviceId":"ESP32_001","status":"online","temperature":22.5,"humidity":55,"lastSeen":"2024-01-15T10:30:00Z"}'
  },
  {
    id: 2,
    name: 'Update Device Configuration',
    path: '/api/v1/devices/{deviceId}/config',
    method: 'PUT',
    description: 'Update configuration parameters for a device',
    version: 'v1',
    status: 'active',
    authentication: 'oauth2',
    rateLimit: 50,
    rateLimitPeriod: 'minute',
    tags: ['devices', 'configuration'],
    createdAt: '2024-01-10',
    updatedAt: '2024-01-14',
    exampleRequest: 'PUT /api/v1/devices/ESP32_001/config\nBody: {"samplingRate":10,"threshold":25.5}',
    exampleResponse: '{"success":true,"message":"Configuration updated","deviceId":"ESP32_001"}'
  },
  {
    id: 3,
    name: 'Get Telemetry Data',
    path: '/api/v1/telemetry',
    method: 'GET',
    description: 'Retrieve historical telemetry data with filtering',
    version: 'v1',
    status: 'active',
    authentication: 'api_key',
    rateLimit: 200,
    rateLimitPeriod: 'hour',
    tags: ['telemetry', 'data'],
    createdAt: '2024-01-09',
    updatedAt: '2024-01-13',
    exampleRequest: 'GET /api/v1/telemetry?deviceId=ESP32_001&from=2024-01-01&to=2024-01-15',
    exampleResponse: '{"data":[{"timestamp":"2024-01-15T10:00:00Z","temperature":22.3},{"timestamp":"2024-01-15T11:00:00Z","temperature":22.8}]}'
  },
  {
    id: 4,
    name: 'Create Alert Rule',
    path: '/api/v1/alerts/rules',
    method: 'POST',
    description: 'Create a new alert rule for monitoring',
    version: 'v1',
    status: 'active',
    authentication: 'oauth2',
    rateLimit: 20,
    rateLimitPeriod: 'minute',
    tags: ['alerts', 'rules'],
    createdAt: '2024-01-08',
    updatedAt: '2024-01-12',
    exampleRequest: 'POST /api/v1/alerts/rules\nBody: {"name":"High Temperature","condition":"temp > 30","severity":"warning"}',
    exampleResponse: '{"id":"rule_001","name":"High Temperature","createdAt":"2024-01-15T10:30:00Z"}'
  },
  {
    id: 5,
    name: 'Get All Devices',
    path: '/api/v1/devices',
    method: 'GET',
    description: 'List all registered devices with pagination',
    version: 'v1',
    status: 'active',
    authentication: 'api_key',
    rateLimit: 300,
    rateLimitPeriod: 'hour',
    tags: ['devices', 'list'],
    createdAt: '2024-01-07',
    updatedAt: '2024-01-11',
    exampleRequest: 'GET /api/v1/devices?page=1&limit=50',
    exampleResponse: '{"devices":[{"id":"ESP32_001","name":"Temperature Sensor","status":"online"}],"total":156,"page":1,"limit":50}'
  },
  {
    id: 6,
    name: 'Delete Device',
    path: '/api/v1/devices/{deviceId}',
    method: 'DELETE',
    description: 'Remove a device from the system',
    version: 'v1',
    status: 'deprecated',
    authentication: 'oauth2',
    rateLimit: 10,
    rateLimitPeriod: 'minute',
    tags: ['devices', 'delete'],
    createdAt: '2024-01-06',
    updatedAt: '2024-01-10',
    exampleRequest: 'DELETE /api/v1/devices/ESP32_001',
    exampleResponse: '{"success":true,"message":"Device deleted"}'
  },
  {
    id: 7,
    name: 'Bulk Device Import',
    path: '/api/v1/devices/import',
    method: 'POST',
    description: 'Import multiple devices from CSV or JSON',
    version: 'v2',
    status: 'inactive',
    authentication: 'oauth2',
    rateLimit: 5,
    rateLimitPeriod: 'minute',
    tags: ['devices', 'import'],
    createdAt: '2024-01-05',
    updatedAt: '2024-01-09',
    exampleRequest: 'POST /api/v1/devices/import\nBody: {"devices":[{"id":"NEW_001","name":"New Sensor"}]}',
    exampleResponse: '{"imported":10,"failed":0,"errors":[]}'
  },
  {
    id: 8,
    name: 'Get Dashboard Metrics',
    path: '/api/v1/dashboard/metrics',
    method: 'GET',
    description: 'Retrieve dashboard summary metrics',
    version: 'v2',
    status: 'active',
    authentication: 'api_key',
    rateLimit: 60,
    rateLimitPeriod: 'minute',
    tags: ['dashboard', 'metrics'],
    createdAt: '2024-01-04',
    updatedAt: '2024-01-08',
    exampleRequest: 'GET /api/v1/dashboard/metrics',
    exampleResponse: '{"totalDevices":156,"onlineDevices":142,"activeAlerts":23,"energyConsumption":1250}'
  }
])

// ==================== API Keys Data ====================
const apiKeys = ref([
  { id: 1, name: 'Production Key', key: 'pk_live_abc123def456ghi789', createdAt: '2024-01-01', lastUsed: '2024-01-15', permissions: ['read', 'write'], status: 'active' },
  { id: 2, name: 'Development Key', key: 'pk_dev_xyz789uvw456rst', createdAt: '2024-01-05', lastUsed: '2024-01-14', permissions: ['read'], status: 'active' },
  { id: 3, name: 'Service Account', key: 'svc_jkl012mno345pqr', createdAt: '2024-01-10', lastUsed: '2024-01-15', permissions: ['read', 'write', 'admin'], status: 'active' },
  { id: 4, name: 'Testing Key', key: 'pk_test_abc123def456ghi', createdAt: '2024-01-12', lastUsed: '2024-01-13', permissions: ['read'], status: 'inactive' }
])

// ==================== API Logs ====================
const apiLogs = ref([
  { id: 1, timestamp: '2024-01-15 10:23:45', apiName: 'Get Device Status', endpoint: '/api/v1/devices/ESP32_001/status', method: 'GET', statusCode: 200, responseTime: 45, ipAddress: '192.168.1.100' },
  { id: 2, timestamp: '2024-01-15 10:20:12', apiName: 'Get Telemetry Data', endpoint: '/api/v1/telemetry', method: 'GET', statusCode: 200, responseTime: 89, ipAddress: '192.168.1.101' },
  { id: 3, timestamp: '2024-01-15 10:15:33', apiName: 'Update Device Config', endpoint: '/api/v1/devices/ESP32_001/config', method: 'PUT', statusCode: 401, responseTime: 12, ipAddress: '192.168.1.102' },
  { id: 4, timestamp: '2024-01-15 10:10:22', apiName: 'Create Alert Rule', endpoint: '/api/v1/alerts/rules', method: 'POST', statusCode: 201, responseTime: 156, ipAddress: '192.168.1.103' },
  { id: 5, timestamp: '2024-01-15 10:05:18', apiName: 'Get All Devices', endpoint: '/api/v1/devices', method: 'GET', statusCode: 200, responseTime: 234, ipAddress: '192.168.1.104' }
])

// ==================== Form Models ====================
const newApi = ref({
  name: '',
  path: '',
  method: 'GET',
  description: '',
  version: 'v1',
  authentication: 'api_key',
  rateLimit: 100,
  rateLimitPeriod: 'minute',
  tags: []
})

const newApiKey = ref({
  name: '',
  permissions: ['read']
})

// ==================== Form Rules ====================
const apiRules = {
  name: [{ required: true, message: 'Please enter API name', trigger: 'blur' }],
  path: [{ required: true, message: 'Please enter API path', trigger: 'blur' }],
  method: [{ required: true, message: 'Please select HTTP method', trigger: 'change' }]
}

// ==================== Computed ====================
const filteredApis = computed(() => {
  let filtered = apis.value
  if (searchKeyword.value) {
    filtered = filtered.filter(api =>
        api.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        api.path.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        api.description.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (methodFilter.value) {
    filtered = filtered.filter(api => api.method === methodFilter.value)
  }
  if (statusFilter.value) {
    filtered = filtered.filter(api => api.status === statusFilter.value)
  }
  return filtered
})

const paginatedApis = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredApis.value.slice(start, end)
})

// ==================== Methods ====================
const getMethodType = (method: string) => {
  const types: Record<string, string> = {
    GET: 'success',
    POST: 'primary',
    PUT: 'warning',
    DELETE: 'danger',
    PATCH: 'info'
  }
  return types[method] || 'info'
}

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    active: 'success',
    inactive: 'info',
    deprecated: 'danger'
  }
  return types[status] || 'info'
}

const getAuthType = (auth: string) => {
  const types: Record<string, string> = {
    none: 'info',
    api_key: 'warning',
    oauth2: 'primary',
    jwt: 'success'
  }
  return types[auth] || 'info'
}

const formatDateTime = (datetime: string) => {
  if (!datetime) return 'N/A'
  return datetime
}

const handleCreateApi = () => {
  dialogMode.value = 'create'
  newApi.value = {
    name: '',
    path: '',
    method: 'GET',
    description: '',
    version: 'v1',
    authentication: 'api_key',
    rateLimit: 100,
    rateLimitPeriod: 'minute',
    tags: []
  }
  apiDialogVisible.value = true
}

const handleEditApi = (api: ApiEndpoint) => {
  dialogMode.value = 'edit'
  newApi.value = { ...api }
  selectedApi.value = api
  apiDialogVisible.value = true
}

const handleSaveApi = async () => {
  await apiFormRef.value?.validate()
  if (dialogMode.value === 'create') {
    const api: ApiEndpoint = {
      id: Math.max(...apis.value.map(a => a.id)) + 1,
      name: newApi.value.name,
      path: newApi.value.path,
      method: newApi.value.method as any,
      description: newApi.value.description,
      version: newApi.value.version,
      status: 'inactive',
      authentication: newApi.value.authentication as any,
      rateLimit: newApi.value.rateLimit,
      rateLimitPeriod: newApi.value.rateLimitPeriod as any,
      tags: newApi.value.tags,
      createdAt: new Date().toISOString().split('T')[0],
      updatedAt: new Date().toISOString().split('T')[0]
    }
    apis.value.push(api)
    statistics.totalApis++
    ElMessage.success('API created successfully')
  } else if (selectedApi.value) {
    const index = apis.value.findIndex(a => a.id === selectedApi.value.id)
    if (index !== -1) {
      apis.value[index] = { ...apis.value[index], ...newApi.value, updatedAt: new Date().toISOString().split('T')[0] }
      ElMessage.success('API updated successfully')
    }
  }
  apiDialogVisible.value = false
}

const handleDeleteApi = (api: ApiEndpoint) => {
  ElMessageBox.confirm(
      `Are you sure you want to delete API "${api.name}"? This action cannot be undone.`,
      'Confirm Delete',
      { type: 'warning' }
  ).then(() => {
    const index = apis.value.findIndex(a => a.id === api.id)
    if (index !== -1) {
      apis.value.splice(index, 1)
      if (api.status === 'active') statistics.activeApis--
      statistics.totalApis--
      ElMessage.success('API deleted successfully')
    }
  }).catch(() => {})
}

const handleToggleStatus = (api: ApiEndpoint) => {
  const index = apis.value.findIndex(a => a.id === api.id)
  if (index !== -1) {
    const newStatus = apis.value[index].status === 'active' ? 'inactive' : 'active'
    apis.value[index].status = newStatus
    if (newStatus === 'active') {
      statistics.activeApis++
    } else {
      statistics.activeApis--
    }
    ElMessage.success(`API ${newStatus === 'active' ? 'activated' : 'deactivated'}`)
  }
}

const handleTestApi = (api: ApiEndpoint) => {
  selectedApi.value = api
  testPayload.value = api.method === 'GET' ? '' : JSON.stringify({ test: 'data' }, null, 2)
  testResult.value = null
  testDialogVisible.value = true
}

const handleRunTest = async () => {
  testing.value = true
  setTimeout(() => {
    testResult.value = {
      success: true,
      statusCode: 200,
      responseTime: Math.floor(Math.random() * 100) + 20,
      response: {
        success: true,
        data: { message: 'API test successful', timestamp: new Date().toISOString() }
      }
    }
    ElMessage.success('API test completed')
    testing.value = false
  }, 1500)
}

const handleViewDocs = (api: ApiEndpoint) => {
  selectedApi.value = api
  docsDialogVisible.value = true
}

const handleRefresh = () => {
  ElMessage.info('Refreshing data...')
  setTimeout(() => {
    statistics.totalRequests += Math.floor(Math.random() * 1000)
    ElMessage.success('Data refreshed')
  }, 1000)
}

const handleExportApis = () => {
  const exportData = {
    apis: apis.value,
    exportDate: new Date().toISOString(),
    version: '1.0'
  }
  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `apis_export_${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('APIs exported successfully')
}

const handleCreateApiKey = () => {
  keyDialogVisible.value = true
}

const handleSaveApiKey = () => {
  const newKey = {
    id: apiKeys.value.length + 1,
    name: newApiKey.value.name,
    key: `pk_${Math.random().toString(36).substring(2, 15)}`,
    createdAt: new Date().toISOString().split('T')[0],
    lastUsed: 'Never',
    permissions: newApiKey.value.permissions,
    status: 'active'
  }
  apiKeys.value.push(newKey)
  statistics.totalApiKeys++
  ElMessage.success(`API Key created: ${newKey.key}`)
  keyDialogVisible.value = false
  newApiKey.value = { name: '', permissions: ['read'] }
}

const handleRevokeKey = (key: any) => {
  ElMessageBox.confirm(
      `Revoke API key "${key.name}"? This action cannot be undone.`,
      'Confirm Revoke',
      { type: 'warning' }
  ).then(() => {
    const index = apiKeys.value.findIndex(k => k.id === key.id)
    if (index !== -1) {
      apiKeys.value.splice(index, 1)
      statistics.totalApiKeys--
      ElMessage.success('API key revoked')
    }
  }).catch(() => {})
}

// ==================== Initialize Charts ====================
const initCharts = () => {
  if (!apiUsageChart.value) return

  // API Usage Chart (Line)
  const usageChart = echarts.init(apiUsageChart.value)
  usageChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Get Device', 'Post Telemetry', 'Update Config', 'Delete Device'] },
    xAxis: { type: 'category', data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'] },
    yAxis: { type: 'value', name: 'Requests' },
    series: [
      { name: 'Get Device', type: 'line', data: [125, 98, 245, 423, 389, 234], smooth: true, lineStyle: { color: '#1890ff', width: 2 } },
      { name: 'Post Telemetry', type: 'line', data: [89, 67, 178, 312, 298, 167], smooth: true, lineStyle: { color: '#52c41a', width: 2 } },
      { name: 'Update Config', type: 'line', data: [34, 28, 67, 123, 98, 56], smooth: true, lineStyle: { color: '#faad14', width: 2 } },
      { name: 'Delete Device', type: 'line', data: [12, 8, 23, 34, 28, 15], smooth: true, lineStyle: { color: '#ff4d4f', width: 2 } }
    ]
  })

  // Response Time Chart (Line)
  const responseChart = echarts.init(responseTimeChart.value)
  responseChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'] },
    yAxis: { type: 'value', name: 'Response Time (ms)' },
    series: [{
      data: [89, 76, 124, 156, 142, 98],
      type: 'line',
      smooth: true,
      areaStyle: { opacity: 0.3 },
      lineStyle: { color: '#faad14', width: 2 },
      itemStyle: { color: '#faad14' }
    }]
  })

  // Status Code Distribution Chart (Pie)
  const statusChart = echarts.init(statusCodeChart.value)
  statusChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { top: 'bottom' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: 85, name: '2xx Success', itemStyle: { color: '#52c41a' } },
        { value: 8, name: '4xx Client Error', itemStyle: { color: '#faad14' } },
        { value: 5, name: '5xx Server Error', itemStyle: { color: '#ff4d4f' } },
        { value: 2, name: '3xx Redirect', itemStyle: { color: '#1890ff' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })

  // Handle resize
  window.addEventListener('resize', () => {
    usageChart.resize()
    responseChart.resize()
    statusChart.resize()
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
          <span class="loading-title">Loading API Management</span>
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
  <div v-else class="api-management">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2>API Management</h2>
        <p>Manage API endpoints, authentication, rate limiting, and monitor API usage analytics</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleCreateApi">
          <el-icon><Plus /></el-icon>
          New API
        </el-button>
        <el-button @click="handleCreateApiKey">
          <el-icon><Key /></el-icon>
          Create API Key
        </el-button>
        <el-button @click="handleExportApis">
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
            <el-icon color="#1890ff" size="28"><Collection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.totalApis }}</div>
            <div class="stat-label">Total APIs</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #e6f7e6">
            <el-icon color="#52c41a" size="28"><Checked /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.activeApis }}</div>
            <div class="stat-label">Active APIs</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #fff7e6">
            <el-icon color="#faad14" size="28"><Message /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ (statistics.totalRequests / 1000).toFixed(1) }}k</div>
            <div class="stat-label">Total Requests</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #fdf0e8">
            <el-icon color="#ff7a45" size="28"><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.avgResponseTime }}ms</div>
            <div class="stat-label">Avg Response</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Main Tabs -->
    <el-tabs v-model="activeTab" class="api-tabs">
      <!-- APIs Tab -->
      <el-tab-pane label="APIs" name="apis">
        <div class="toolbar">
          <div class="toolbar-left">
            <el-input
                v-model="searchKeyword"
                placeholder="Search by name or path..."
                clearable
                style="width: 260px"
                :prefix-icon="Search"
            />
            <el-select v-model="methodFilter" placeholder="Method" clearable style="width: 100px">
              <el-option label="All" value="" />
              <el-option label="GET" value="GET" />
              <el-option label="POST" value="POST" />
              <el-option label="PUT" value="PUT" />
              <el-option label="DELETE" value="DELETE" />
            </el-select>
            <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
              <el-option label="All" value="" />
              <el-option label="Active" value="active" />
              <el-option label="Inactive" value="inactive" />
              <el-option label="Deprecated" value="deprecated" />
            </el-select>
          </div>
          <div class="toolbar-right">
            <el-button type="info" @click="handleRefresh">
              <el-icon><Refresh /></el-icon>
              Refresh
            </el-button>
          </div>
        </div>

        <el-table :data="paginatedApis" style="width: 100%; margin-top: 16px" stripe>
          <el-table-column prop="name" label="API Name" min-width="180">
            <template #default="{ row }">
              <div>
                <div class="api-name">{{ row.name }}</div>
                <div class="api-path">{{ row.path }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="method" label="Method" width="100">
            <template #default="{ row }">
              <el-tag :type="getMethodType(row.method)" size="small">{{ row.method }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="Description" min-width="200" show-overflow-tooltip />
          <el-table-column prop="version" label="Version" width="80">
            <template #default="{ row }">
              <el-tag size="small" effect="plain">{{ row.version }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">{{ row.status.toUpperCase() }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="rateLimit" label="Rate Limit" width="120">
            <template #default="{ row }">
              {{ row.rateLimit }}/{{ row.rateLimitPeriod }}
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="280" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="handleTestApi(row)">
                <el-icon><Monitor /></el-icon>
                Test
              </el-button>
              <el-button link type="primary" size="small" @click="handleViewDocs(row)">
                <el-icon><Document /></el-icon>
                Docs
              </el-button>
              <el-button link type="primary" size="small" @click="handleEditApi(row)">
                <el-icon><Edit /></el-icon>
                Edit
              </el-button>
              <el-button link type="warning" size="small" @click="handleToggleStatus(row)">
                <el-icon><Switch /></el-icon>
                {{ row.status === 'active' ? 'Disable' : 'Enable' }}
              </el-button>
              <el-button link type="danger" size="small" @click="handleDeleteApi(row)">
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
              :total="filteredApis.length"
              layout="total, sizes, prev, pager, next, jumper"
          />
        </div>
      </el-tab-pane>

      <!-- API Keys Tab -->
      <el-tab-pane label="API Keys" name="keys">
        <div class="keys-header">
          <h3>API Authentication Keys</h3>
          <el-button type="primary" @click="handleCreateApiKey">
            <el-icon><Plus /></el-icon>
            Generate API Key
          </el-button>
        </div>

        <el-table :data="apiKeys" style="width: 100%; margin-top: 16px" stripe>
          <el-table-column prop="name" label="Key Name" min-width="150" />
          <el-table-column prop="key" label="API Key" min-width="250">
            <template #default="{ row }">
              <code class="api-key-code">{{ row.key }}</code>
              <el-button link size="small" @click="copyToClipboard(row.key)">
                <el-icon><CopyDocument /></el-icon>
              </el-button>
            </template>
          </el-table-column>
          <el-table-column prop="permissions" label="Permissions" width="150">
            <template #default="{ row }">
              <el-tag v-for="perm in row.permissions" :key="perm" size="small" style="margin-right: 4px">
                {{ perm }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
                {{ row.status.toUpperCase() }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="lastUsed" label="Last Used" width="160" />
          <el-table-column prop="createdAt" label="Created" width="120" />
          <el-table-column label="Actions" width="120">
            <template #default="{ row }">
              <el-button link type="danger" size="small" @click="handleRevokeKey(row)">
                Revoke
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Analytics Tab -->
      <el-tab-pane label="Analytics" name="analytics">
        <div class="analytics-container">
          <el-row :gutter="16">
            <el-col :span="24">
              <el-card class="analytics-card" header="API Usage Trend">
                <div ref="apiUsageChart" style="height: 350px"></div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="16" style="margin-top: 16px">
            <el-col :span="14">
              <el-card class="analytics-card" header="Response Time Trend">
                <div ref="responseTimeChart" style="height: 300px"></div>
              </el-card>
            </el-col>
            <el-col :span="10">
              <el-card class="analytics-card" header="Status Code Distribution">
                <div ref="statusCodeChart" style="height: 300px"></div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="16" style="margin-top: 16px">
            <el-col :span="24">
              <el-card class="analytics-card" header="Recent API Logs">
                <el-table :data="apiLogs" style="width: 100%" stripe>
                  <el-table-column prop="timestamp" label="Timestamp" width="180" />
                  <el-table-column prop="apiName" label="API Name" min-width="180" />
                  <el-table-column prop="method" label="Method" width="80">
                    <template #default="{ row }">
                      <el-tag :type="getMethodType(row.method)" size="small">{{ row.method }}</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="statusCode" label="Status" width="100">
                    <template #default="{ row }">
                      <el-tag :type="row.statusCode >= 200 && row.statusCode < 300 ? 'success' : 'danger'" size="small">
                        {{ row.statusCode }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="responseTime" label="Response Time" width="120">
                    <template #default="{ row }">
                      {{ row.responseTime }}ms
                    </template>
                  </el-table-column>
                  <el-table-column prop="ipAddress" label="IP Address" width="140" />
                </el-table>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Create/Edit API Dialog -->
    <el-dialog
        v-model="apiDialogVisible"
        :title="dialogMode === 'create' ? 'Create API Endpoint' : 'Edit API Endpoint'"
        width="700px"
    >
      <el-form :model="newApi" :rules="apiRules" ref="apiFormRef" label-width="140px">
        <el-form-item label="API Name" prop="name">
          <el-input v-model="newApi.name" placeholder="e.g., Get Device Status" />
        </el-form-item>
        <el-form-item label="API Path" prop="path">
          <el-input v-model="newApi.path" placeholder="e.g., /api/v1/devices/{deviceId}/status" />
        </el-form-item>
        <el-form-item label="HTTP Method" prop="method">
          <el-select v-model="newApi.method" style="width: 100%">
            <el-option label="GET" value="GET" />
            <el-option label="POST" value="POST" />
            <el-option label="PUT" value="PUT" />
            <el-option label="DELETE" value="DELETE" />
            <el-option label="PATCH" value="PATCH" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="newApi.description" type="textarea" :rows="2" placeholder="Describe the API purpose" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Version">
              <el-input v-model="newApi.version" placeholder="v1" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Authentication">
              <el-select v-model="newApi.authentication" style="width: 100%">
                <el-option label="None" value="none" />
                <el-option label="API Key" value="api_key" />
                <el-option label="OAuth2" value="oauth2" />
                <el-option label="JWT" value="jwt" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Rate Limit">
              <el-input-number v-model="newApi.rateLimit" :min="1" :max="10000" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Rate Limit Period">
              <el-select v-model="newApi.rateLimitPeriod" style="width: 100%">
                <el-option label="Per Minute" value="minute" />
                <el-option label="Per Hour" value="hour" />
                <el-option label="Per Day" value="day" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Tags">
          <el-select v-model="newApi.tags" multiple filterable allow-create placeholder="Add tags" style="width: 100%">
            <el-option label="devices" value="devices" />
            <el-option label="telemetry" value="telemetry" />
            <el-option label="alerts" value="alerts" />
            <el-option label="configuration" value="configuration" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="apiDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleSaveApi">Save</el-button>
      </template>
    </el-dialog>

    <!-- API Key Dialog -->
    <el-dialog v-model="keyDialogVisible" title="Create API Key" width="500px">
      <el-form :model="newApiKey" label-width="120px">
        <el-form-item label="Key Name">
          <el-input v-model="newApiKey.name" placeholder="e.g., Production Key" />
        </el-form-item>
        <el-form-item label="Permissions">
          <el-checkbox-group v-model="newApiKey.permissions">
            <el-checkbox value="read">Read</el-checkbox>
            <el-checkbox value="write">Write</el-checkbox>
            <el-checkbox value="admin">Admin</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="keyDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleSaveApiKey">Generate</el-button>
      </template>
    </el-dialog>

    <!-- API Documentation Dialog -->
    <el-dialog v-model="docsDialogVisible" :title="`API Documentation - ${selectedApi?.name}`" width="750px">
      <div v-if="selectedApi" class="api-docs">
        <el-tabs v-model="activeApiTab">
          <el-tab-pane label="Overview" name="info">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="Name">{{ selectedApi.name }}</el-descriptions-item>
              <el-descriptions-item label="Path">
                <code>{{ selectedApi.path }}</code>
              </el-descriptions-item>
              <el-descriptions-item label="Method">
                <el-tag :type="getMethodType(selectedApi.method)">{{ selectedApi.method }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="Description">{{ selectedApi.description }}</el-descriptions-item>
              <el-descriptions-item label="Authentication">
                <el-tag :type="getAuthType(selectedApi.authentication)">{{ selectedApi.authentication }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="Rate Limit">
                {{ selectedApi.rateLimit }} requests per {{ selectedApi.rateLimitPeriod }}
              </el-descriptions-item>
              <el-descriptions-item label="Version">{{ selectedApi.version }}</el-descriptions-item>
              <el-descriptions-item label="Tags">
                <el-tag v-for="tag in selectedApi.tags" :key="tag" size="small" style="margin-right: 4px">{{ tag }}</el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>

          <el-tab-pane label="Example Request" name="request">
            <el-card shadow="never">
              <pre class="code-block">{{ selectedApi.exampleRequest || 'No example available' }}</pre>
            </el-card>
          </el-tab-pane>

          <el-tab-pane label="Example Response" name="response">
            <el-card shadow="never">
              <pre class="code-block">{{ selectedApi.exampleResponse || 'No example available' }}</pre>
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>

    <!-- Test API Dialog -->
    <el-dialog v-model="testDialogVisible" :title="`Test API - ${selectedApi?.name}`" width="750px">
      <div class="test-container">
        <div class="test-info">
          <el-tag :type="getMethodType(selectedApi?.method || 'GET')" size="small">{{ selectedApi?.method }}</el-tag>
          <code class="test-endpoint">{{ selectedApi?.path }}</code>
        </div>
        <div v-if="selectedApi?.method !== 'GET'" class="test-input">
          <h4>Request Body:</h4>
          <el-input
              v-model="testPayload"
              type="textarea"
              :rows="5"
              placeholder='{"test": "data"}'
          />
        </div>
        <div class="test-actions" style="margin: 16px 0">
          <el-button type="primary" @click="handleRunTest" :loading="testing">
            <el-icon><Play /></el-icon>
            Send Request
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
.api-management {
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

.api-tabs {
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

/* API Table */
.api-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.api-path {
  font-size: 12px;
  color: #999;
  font-family: monospace;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

/* API Keys */
.keys-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.keys-header h3 {
  margin: 0;
}

.api-key-code {
  font-family: monospace;
  font-size: 12px;
  background: #f5f5f5;
  padding: 4px 8px;
  border-radius: 4px;
  margin-right: 8px;
}

/* Analytics */
.analytics-container {
  padding: 16px 0;
}

.analytics-card {
  height: 100%;
}

/* API Docs */
.api-docs {
  padding: 8px 0;
}

.code-block {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 13px;
  font-family: monospace;
  margin: 0;
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
  font-size: 14px;
  color: #1890ff;
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
</style>