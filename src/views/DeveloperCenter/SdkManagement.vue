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
  'Initializing SDK registry...',
  'Loading SDK packages...',
  'Checking version compatibility...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedLanguage = ref('all')
const selectedStatus = ref('all')
const detailsVisible = ref(false)
const createSdkVisible = ref(false)
const editSdkVisible = ref(false)
const chartRef = ref(null)

let downloadChart: echarts.ECharts | null = null

// Language filters
const languageOptions = [
  { value: 'all', label: 'All Languages' },
  { value: 'javascript', label: 'JavaScript', icon: 'JS' },
  { value: 'python', label: 'Python', icon: 'PY' },
  { value: 'java', label: 'Java', icon: 'JV' },
  { value: 'go', label: 'Go', icon: 'GO' },
  { value: 'dotnet', label: '.NET', icon: 'NT' }
]

// Status filters
const statusOptions = [
  { value: 'all', label: 'All Status' },
  { value: 'stable', label: 'Stable', color: '#67C23A' },
  { value: 'beta', label: 'Beta', color: '#E6A23C' },
  { value: 'deprecated', label: 'Deprecated', color: '#909399' }
]

// SDK packages data
const sdks = ref([
  {
    id: 'SDK001', name: 'IBMS JavaScript SDK', language: 'javascript', version: '2.1.0',
    status: 'stable', downloads: 12450, stars: 345, lastUpdated: '2024-01-15',
    description: 'Complete JavaScript SDK for IBMS API integration',
    features: ['Full API coverage', 'TypeScript support', 'Promise-based', 'WebSocket support'],
    dependencies: ['axios', 'ws'],
    minNodeVersion: '14.0.0',
    createdBy: 'SDK Team'
  },
  {
    id: 'SDK002', name: 'IBMS Python SDK', language: 'python', version: '3.0.0',
    status: 'stable', downloads: 8970, stars: 278, lastUpdated: '2024-01-14',
    description: 'Python SDK for building IBMS applications',
    features: ['Async support', 'Type hints', 'Comprehensive docs', 'CLI tool'],
    dependencies: ['httpx', 'pydantic'],
    minPythonVersion: '3.8',
    createdBy: 'Python Team'
  },
  {
    id: 'SDK003', name: 'IBMS Java SDK', language: 'java', version: '1.8.0',
    status: 'stable', downloads: 5670, stars: 189, lastUpdated: '2024-01-13',
    description: 'Java SDK for enterprise IBMS integration',
    features: ['Reactive streams', 'Spring Boot integration', 'Connection pooling'],
    dependencies: ['reactor-core', 'jackson'],
    minJavaVersion: '11',
    createdBy: 'Java Team'
  },
  {
    id: 'SDK004', name: 'IBMS Go SDK', language: 'go', version: '1.5.0',
    status: 'beta', downloads: 2340, stars: 98, lastUpdated: '2024-01-12',
    description: 'Go SDK for high-performance IBMS applications',
    features: ['High concurrency', 'Context support', 'Middleware support'],
    dependencies: [],
    minGoVersion: '1.18',
    createdBy: 'Go Team'
  },
  {
    id: 'SDK005', name: 'IBMS .NET SDK', language: 'dotnet', version: '2.0.0',
    status: 'stable', downloads: 3450, stars: 145, lastUpdated: '2024-01-11',
    description: '.NET SDK for Windows-based IBMS integration',
    features: ['Async/await', 'LINQ support', 'JSON serialization'],
    dependencies: ['Newtonsoft.Json', 'Microsoft.Extensions.Http'],
    minDotNetVersion: '6.0',
    createdBy: '.NET Team'
  },
  {
    id: 'SDK006', name: 'IBMS TypeScript SDK', language: 'javascript', version: '1.2.0',
    status: 'beta', downloads: 1890, stars: 67, lastUpdated: '2024-01-10',
    description: 'TypeScript-first SDK with full type safety',
    features: ['Full type definitions', 'Tree-shakeable', 'React hooks'],
    dependencies: ['axios'],
    minNodeVersion: '16.0.0',
    createdBy: 'Frontend Team'
  },
  {
    id: 'SDK007', name: 'IBMS Async Python SDK', language: 'python', version: '2.0.0',
    status: 'deprecated', downloads: 890, stars: 34, lastUpdated: '2024-01-09',
    description: 'Deprecated - Use main Python SDK v3.0+',
    features: ['Async support', 'WebSocket client'],
    dependencies: ['aiohttp'],
    minPythonVersion: '3.7',
    createdBy: 'Python Team'
  },
  {
    id: 'SDK008', name: 'IBMS Micro SDK', language: 'javascript', version: '1.0.0',
    status: 'beta', downloads: 560, stars: 23, lastUpdated: '2024-01-08',
    description: 'Lightweight SDK for browser applications',
    features: ['Small bundle size (<10KB)', 'Core APIs only', 'No dependencies'],
    dependencies: [],
    minNodeVersion: '12.0.0',
    createdBy: 'SDK Team'
  }
])

// SDK statistics
const sdkStats = reactive({
  total: 0,
  stable: 0,
  beta: 0,
  deprecated: 0,
  totalDownloads: 0,
  totalStars: 0,
  avgDownloads: 0
})

// Download data for chart
const downloadData = ref([
  { month: 'Jul', downloads: 2450 },
  { month: 'Aug', downloads: 2780 },
  { month: 'Sep', downloads: 3120 },
  { month: 'Oct', downloads: 3450 },
  { month: 'Nov', downloads: 3890 },
  { month: 'Dec', downloads: 4230 },
  { month: 'Jan', downloads: 4670 }
])

// Create SDK form
const createSdkForm = reactive({
  name: '',
  language: 'javascript',
  version: '1.0.0',
  description: '',
  features: [''],
  dependencies: ['']
})

// Edit SDK form
const editSdkForm = reactive({
  id: '',
  name: '',
  language: '',
  version: '',
  status: '',
  description: '',
  features: [] as string[],
  dependencies: [] as string[]
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 8,
  total: sdks.value.length
})

// Filtered SDKs
const filteredSdks = computed(() => {
  let filtered = sdks.value
  if (searchKeyword.value) {
    filtered = filtered.filter(s =>
        s.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        s.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        s.description.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedLanguage.value !== 'all') {
    filtered = filtered.filter(s => s.language === selectedLanguage.value)
  }
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(s => s.status === selectedStatus.value)
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

  downloadChart = echarts.init(chartRef.value)
  downloadChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: downloadData.value.map(d => d.month) },
    yAxis: { type: 'value', name: 'Downloads' },
    series: [{
      type: 'line',
      data: downloadData.value.map(d => d.downloads),
      smooth: true,
      lineStyle: { color: '#409EFF', width: 3 },
      areaStyle: { opacity: 0.1, color: '#409EFF' },
      symbol: 'circle',
      symbolSize: 8,
      label: { show: true, position: 'top' }
    }]
  })
}

const updateStats = () => {
  sdkStats.total = sdks.value.length
  sdkStats.stable = sdks.value.filter(s => s.status === 'stable').length
  sdkStats.beta = sdks.value.filter(s => s.status === 'beta').length
  sdkStats.deprecated = sdks.value.filter(s => s.status === 'deprecated').length
  sdkStats.totalDownloads = sdks.value.reduce((sum, s) => sum + s.downloads, 0)
  sdkStats.totalStars = sdks.value.reduce((sum, s) => sum + s.stars, 0)
  sdkStats.avgDownloads = Math.round(sdkStats.totalDownloads / sdkStats.total)
}

const handleResize = () => {
  downloadChart?.resize()
}

// ==================== SDK Functions ====================
const refreshSdks = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  loading.value = false
  ElMessage.success('SDK registry refreshed successfully')
}

const viewSdkDetails = (sdk: any) => {
  selectedSdk.value = sdk
  detailsVisible.value = true
}

const editSdk = (sdk: any) => {
  editSdkForm.id = sdk.id
  editSdkForm.name = sdk.name
  editSdkForm.language = sdk.language
  editSdkForm.version = sdk.version
  editSdkForm.status = sdk.status
  editSdkForm.description = sdk.description
  editSdkForm.features = [...sdk.features]
  editSdkForm.dependencies = [...sdk.dependencies]
  editSdkVisible.value = true
}

const saveSdkEdit = async () => {
  if (!editSdkForm.name) {
    ElMessage.warning('Please enter an SDK name')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1000))

  const index = sdks.value.findIndex(s => s.id === editSdkForm.id)
  if (index !== -1) {
    sdks.value[index] = {
      ...sdks.value[index],
      name: editSdkForm.name,
      language: editSdkForm.language,
      version: editSdkForm.version,
      status: editSdkForm.status,
      description: editSdkForm.description,
      features: editSdkForm.features.filter(f => f.trim()),
      dependencies: editSdkForm.dependencies.filter(d => d.trim()),
      lastUpdated: new Date().toISOString().split('T')[0]
    }
  }

  updateStats()
  editSdkVisible.value = false
  ElMessage.success('SDK updated successfully')
}

const deleteSdk = async (sdk: any) => {
  await ElMessageBox.confirm(
      `Delete SDK "${sdk.name}"? This action cannot be undone.`,
      'Confirm Delete',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'danger'
      }
  )

  const index = sdks.value.findIndex(s => s.id === sdk.id)
  if (index !== -1) {
    sdks.value.splice(index, 1)
  }

  updateStats()
  initChart()
  ElMessage.success('SDK deleted successfully')
}

const openCreateSdk = () => {
  createSdkForm.name = ''
  createSdkForm.language = 'javascript'
  createSdkForm.version = '1.0.0'
  createSdkForm.description = ''
  createSdkForm.features = ['']
  createSdkForm.dependencies = ['']
  createSdkVisible.value = true
}

const addArrayItem = (array: string[]) => {
  array.push('')
}

const removeArrayItem = (array: string[], index: number) => {
  if (array.length > 1) {
    array.splice(index, 1)
  }
}

const createSdk = async () => {
  if (!createSdkForm.name) {
    ElMessage.warning('Please enter an SDK name')
    return
  }

  const features = createSdkForm.features.filter(f => f.trim())
  const dependencies = createSdkForm.dependencies.filter(d => d.trim())

  await new Promise(resolve => setTimeout(resolve, 1000))

  const newSdk = {
    id: `SDK${String(sdks.value.length + 1).padStart(3, '0')}`,
    name: createSdkForm.name,
    language: createSdkForm.language,
    version: createSdkForm.version,
    status: 'beta',
    downloads: 0,
    stars: 0,
    lastUpdated: new Date().toISOString().split('T')[0],
    description: createSdkForm.description || 'New SDK package',
    features,
    dependencies,
    minNodeVersion: '14.0.0',
    createdBy: 'Current User'
  }

  sdks.value.unshift(newSdk)
  updateStats()
  initChart()
  createSdkVisible.value = false
  ElMessage.success('SDK created successfully')
}

const downloadSdk = (sdk: any) => {
  ElMessage.info(`Downloading ${sdk.name}...`)
  setTimeout(() => {
    sdk.downloads++
    updateStats()
    ElMessage.success(`${sdk.name} downloaded successfully`)
  }, 1000)
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getLanguageBadge = (language: string) => {
  switch (language) {
    case 'javascript': return { color: '#E6A23C', text: 'JS' }
    case 'python': return { color: '#409EFF', text: 'PY' }
    case 'java': return { color: '#F56C6C', text: 'JV' }
    case 'go': return { color: '#67C23A', text: 'GO' }
    case 'dotnet': return { color: '#9B59B6', text: 'NT' }
    default: return { color: '#909399', text: 'SDK' }
  }
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'stable': return 'success'
    case 'beta': return 'warning'
    case 'deprecated': return 'info'
    default: return 'info'
  }
}

const formatNumber = (num: number) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const selectedSdk = ref<any>(null)
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
          <span class="loading-title">Loading SDK Management</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Developer Center - SDK Management</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="sdk-management-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">SDK Management</h1>
        <p class="page-subtitle">Manage SDK packages for multiple programming languages</p>
      </div>
      <div class="header-right">
        <el-button type="primary" size="large" @click="openCreateSdk">
          <el-icon><Plus /></el-icon>
          Create SDK
        </el-button>
        <el-button size="large" @click="refreshSdks" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total-icon">
          <el-icon><Tickets /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ sdkStats.total }}</div>
          <div class="stat-label">Total SDKs</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ sdkStats.stable }} Stable</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon downloads-icon">
          <el-icon><DownloadIcon /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ formatNumber(sdkStats.totalDownloads) }}</div>
          <div class="stat-label">Total Downloads</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+23% this month</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon stars-icon">
          <el-icon><Star /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ formatNumber(sdkStats.totalStars) }}</div>
          <div class="stat-label">GitHub Stars</div>
        </div>
        <div class="stat-trend">
          <el-progress :percentage="(sdkStats.stable / sdkStats.total) * 100" :stroke-width="4" :show-text="false" />
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon languages-icon">
          <el-icon><Connection /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ languageOptions.length - 1 }}</div>
          <div class="stat-label">Languages</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ sdkStats.beta }} Beta</span>
        </div>
      </div>
    </div>

    <!-- Download Trend Chart -->
    <div class="chart-section">
      <div class="section-header">
        <h3>Download Trends</h3>
        <el-button text type="primary" @click="initChart">Refresh</el-button>
      </div>
      <div ref="chartRef" class="download-chart" style="height: 320px"></div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-bar">
      <div class="filters-left">
        <div class="search-box">
          <el-input
              v-model="searchKeyword"
              placeholder="Search SDKs..."
              :prefix-icon="Search"
              clearable
              style="width: 240px"
          />
        </div>
        <div class="language-filters">
          <span class="filter-label">Language:</span>
          <button
              v-for="l in languageOptions"
              :key="l.value"
              class="language-chip"
              :class="{ active: selectedLanguage === l.value }"
              @click="selectedLanguage = l.value"
          >
            <span class="lang-badge" :style="{ background: getLanguageBadge(l.value).color }">
              {{ getLanguageBadge(l.value).text }}
            </span>
            <span>{{ l.label }}</span>
          </button>
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
      </div>
    </div>

    <!-- SDKs Grid -->
    <div class="sdks-grid">
      <div
          v-for="sdk in filteredSdks"
          :key="sdk.id"
          class="sdk-card"
          :class="sdk.status"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="sdk-language">
            <span class="lang-badge-large" :style="{ background: getLanguageBadge(sdk.language).color }">
              {{ getLanguageBadge(sdk.language).text }}
            </span>
            <span class="language-name">{{ sdk.language.toUpperCase() }}</span>
          </div>
          <div class="sdk-status">
            <el-tag :type="getStatusType(sdk.status)" size="small" effect="light">
              {{ sdk.status.toUpperCase() }}
            </el-tag>
          </div>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <h4 class="sdk-name">{{ sdk.name }}</h4>
          <p class="sdk-description">{{ sdk.description }}</p>

          <!-- Version and Meta -->
          <div class="sdk-meta">
            <div class="meta-item">
              <span class="meta-label">Version:</span>
              <span class="meta-value">v{{ sdk.version }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Updated:</span>
              <span class="meta-value">{{ sdk.lastUpdated }}</span>
            </div>
          </div>

          <!-- Features Preview -->
          <div class="features-preview">
            <div class="features-label">Features:</div>
            <div class="features-list">
              <span v-for="feature in sdk.features.slice(0, 2)" :key="feature" class="feature-tag">
                {{ feature }}
              </span>
              <span v-if="sdk.features.length > 2" class="more">+{{ sdk.features.length - 2 }}</span>
            </div>
          </div>

          <!-- Stats -->
          <div class="sdk-stats">
            <div class="stat">
              <el-icon><DownloadIcon /></el-icon>
              <span>{{ formatNumber(sdk.downloads) }}</span>
            </div>
            <div class="stat">
              <el-icon><Star /></el-icon>
              <span>{{ formatNumber(sdk.stars) }}</span>
            </div>
            <div class="stat">
              <el-icon><User /></el-icon>
              <span>{{ sdk.createdBy }}</span>
            </div>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="card-actions">
            <el-button size="small" @click="viewSdkDetails(sdk)">
              <el-icon><Eye /></el-icon> Details
            </el-button>
            <el-button size="small" type="primary" @click="downloadSdk(sdk)">
              <el-icon><DownloadIcon /></el-icon> Download
            </el-button>
            <el-button size="small" type="primary" @click="editSdk(sdk)">
              <el-icon><Edit /></el-icon> Edit
            </el-button>
            <el-button size="small" type="danger" @click="deleteSdk(sdk)">
              <el-icon><Delete /></el-icon> Delete
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredSdks.length === 0" class="empty-state">
      <el-empty description="No SDK packages found">
        <el-button type="primary" @click="openCreateSdk">Create SDK</el-button>
      </el-empty>
    </div>

    <!-- Pagination -->
    <div v-if="filteredSdks.length > 0" class="pagination-wrapper">
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

    <!-- SDK Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="selectedSdk?.name" width="650px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="SDK ID">{{ selectedSdk?.id }}</el-descriptions-item>
        <el-descriptions-item label="Language">{{ selectedSdk?.language?.toUpperCase() }}</el-descriptions-item>
        <el-descriptions-item label="Version">{{ selectedSdk?.version }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusType(selectedSdk?.status)" size="small">
            {{ selectedSdk?.status?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Total Downloads">{{ formatNumber(selectedSdk?.downloads) }}</el-descriptions-item>
        <el-descriptions-item label="GitHub Stars">{{ formatNumber(selectedSdk?.stars) }}</el-descriptions-item>
        <el-descriptions-item label="Last Updated">{{ selectedSdk?.lastUpdated }}</el-descriptions-item>
        <el-descriptions-item label="Created By">{{ selectedSdk?.createdBy }}</el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedSdk?.description }}</el-descriptions-item>
        <el-descriptions-item label="Features" :span="2">
          <div class="features-list-detail">
            <div v-for="f in selectedSdk?.features" :key="f" class="feature-item">• {{ f }}</div>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="Dependencies" :span="2">
          <div class="dependencies-list">
            <el-tag v-for="d in selectedSdk?.dependencies" :key="d" size="small" style="margin: 2px">
              {{ d }}
            </el-tag>
            <span v-if="!selectedSdk?.dependencies.length" class="no-deps">No external dependencies</span>
          </div>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
        <el-button type="primary" @click="downloadSdk(selectedSdk)">Download SDK</el-button>
      </template>
    </el-dialog>

    <!-- Create SDK Dialog -->
    <el-dialog v-model="createSdkVisible" title="Create New SDK" width="600px">
      <el-form :model="createSdkForm" label-width="100px">
        <el-form-item label="SDK Name" required>
          <el-input v-model="createSdkForm.name" placeholder="Enter SDK name" />
        </el-form-item>
        <el-form-item label="Language">
          <el-select v-model="createSdkForm.language" style="width: 100%">
            <el-option v-for="l in languageOptions.slice(1)" :key="l.value" :label="l.label" :value="l.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Version">
          <el-input v-model="createSdkForm.version" placeholder="1.0.0" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="createSdkForm.description" type="textarea" rows="2" placeholder="SDK description" />
        </el-form-item>
        <el-form-item label="Features">
          <div v-for="(feature, idx) in createSdkForm.features" :key="idx" class="array-item">
            <el-input v-model="createSdkForm.features[idx]" placeholder="Feature description" />
            <el-button type="danger" link @click="removeArrayItem(createSdkForm.features, idx)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          <el-button type="primary" link @click="addArrayItem(createSdkForm.features)">
            <el-icon><Plus /></el-icon> Add Feature
          </el-button>
        </el-form-item>
        <el-form-item label="Dependencies">
          <div v-for="(dep, idx) in createSdkForm.dependencies" :key="idx" class="array-item">
            <el-input v-model="createSdkForm.dependencies[idx]" placeholder="Package name" />
            <el-button type="danger" link @click="removeArrayItem(createSdkForm.dependencies, idx)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          <el-button type="primary" link @click="addArrayItem(createSdkForm.dependencies)">
            <el-icon><Plus /></el-icon> Add Dependency
          </el-button>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createSdkVisible = false">Cancel</el-button>
        <el-button type="primary" @click="createSdk">Create SDK</el-button>
      </template>
    </el-dialog>

    <!-- Edit SDK Dialog -->
    <el-dialog v-model="editSdkVisible" title="Edit SDK" width="600px">
      <el-form :model="editSdkForm" label-width="100px">
        <el-form-item label="SDK Name" required>
          <el-input v-model="editSdkForm.name" placeholder="Enter SDK name" />
        </el-form-item>
        <el-form-item label="Language">
          <el-select v-model="editSdkForm.language" style="width: 100%">
            <el-option v-for="l in languageOptions.slice(1)" :key="l.value" :label="l.label" :value="l.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Version">
          <el-input v-model="editSdkForm.version" placeholder="1.0.0" />
        </el-form-item>
        <el-form-item label="Status">
          <el-select v-model="editSdkForm.status" style="width: 100%">
            <el-option label="Stable" value="stable" />
            <el-option label="Beta" value="beta" />
            <el-option label="Deprecated" value="deprecated" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="editSdkForm.description" type="textarea" rows="2" placeholder="SDK description" />
        </el-form-item>
        <el-form-item label="Features">
          <div v-for="(feature, idx) in editSdkForm.features" :key="idx" class="array-item">
            <el-input v-model="editSdkForm.features[idx]" placeholder="Feature description" />
            <el-button type="danger" link @click="removeArrayItem(editSdkForm.features, idx)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          <el-button type="primary" link @click="addArrayItem(editSdkForm.features)">
            <el-icon><Plus /></el-icon> Add Feature
          </el-button>
        </el-form-item>
        <el-form-item label="Dependencies">
          <div v-for="(dep, idx) in editSdkForm.dependencies" :key="idx" class="array-item">
            <el-input v-model="editSdkForm.dependencies[idx]" placeholder="Package name" />
            <el-button type="danger" link @click="removeArrayItem(editSdkForm.dependencies, idx)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          <el-button type="primary" link @click="addArrayItem(editSdkForm.dependencies)">
            <el-icon><Plus /></el-icon> Add Dependency
          </el-button>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editSdkVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveSdkEdit">Save Changes</el-button>
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
.sdk-management-container {
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

.downloads-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.stars-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.languages-icon {
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

.download-chart {
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

.language-filters,
.status-filters {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.language-chip,
.status-chip {
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

.language-chip:hover,
.status-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.language-chip.active,
.status-chip.active {
  background: #409eff;
  border-color: #409eff;
  color: white;
}

.lang-badge {
  display: inline-block;
  width: 28px;
  height: 20px;
  border-radius: 4px;
  color: white;
  font-size: 10px;
  font-weight: 600;
  text-align: center;
  line-height: 20px;
}

.chip-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

/* SDKs Grid */
.sdks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.sdk-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
}

.sdk-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.sdk-card.stable {
  border-left: 4px solid #67c23a;
}

.sdk-card.beta {
  border-left: 4px solid #e6a23c;
}

.sdk-card.deprecated {
  border-left: 4px solid #909399;
}

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 0 20px;
}

.sdk-language {
  display: flex;
  align-items: center;
  gap: 8px;
}

.lang-badge-large {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 14px;
}

.language-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

/* Card Body */
.card-body {
  padding: 16px 20px;
}

.sdk-name {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 10px 0;
  line-height: 1.4;
}

.sdk-description {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.sdk-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.meta-item {
  display: flex;
  gap: 4px;
  font-size: 12px;
}

.meta-label {
  color: #909399;
}

.meta-value {
  color: #1e293b;
  font-weight: 500;
}

.features-preview {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.features-label {
  font-size: 11px;
  color: #909399;
}

.features-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.feature-tag {
  font-size: 11px;
  padding: 2px 8px;
  background: #f0f9ff;
  color: #409eff;
  border-radius: 12px;
}

.more {
  font-size: 11px;
  color: #909399;
}

.sdk-stats {
  display: flex;
  gap: 16px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.stat {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
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

/* Dialog Styles */
.array-item {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.array-item .el-input {
  flex: 1;
}

.features-list-detail {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.feature-item {
  font-size: 13px;
  color: #606266;
}

.dependencies-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.no-deps {
  font-size: 12px;
  color: #909399;
  font-style: italic;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .sdks-grid {
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  }
}

@media (max-width: 768px) {
  .sdk-management-container {
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

  .language-filters,
  .status-filters {
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

  .sdks-grid {
    grid-template-columns: 1fr;
  }

  .card-actions {
    flex-direction: column;
  }

  .card-actions .el-button {
    width: 100%;
  }

  .sdk-meta {
    flex-direction: column;
    gap: 4px;
  }
}
</style>