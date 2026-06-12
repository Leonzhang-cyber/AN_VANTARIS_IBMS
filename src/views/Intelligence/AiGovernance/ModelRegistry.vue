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
  Lock, Key, Shield, Medal, Flag, DataAnalysis
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Loading model registry...',
  'Analyzing model performance...',
  'Preparing version history...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedStatus = ref('all')
const selectedType = ref('all')
const detailsVisible = ref(false)
const registerModelVisible = ref(false)
const editModelVisible = ref(false)
const versionHistoryVisible = ref(false)
const chartRef = ref(null)

let performanceChart: echarts.ECharts | null = null

// Status filters
const statusOptions = [
  { value: 'all', label: 'All Status' },
  { value: 'production', label: 'Production', color: '#67C23A' },
  { value: 'staging', label: 'Staging', color: '#E6A23C' },
  { value: 'development', label: 'Development', color: '#409EFF' },
  { value: 'archived', label: 'Archived', color: '#909399' }
]

// Type filters
const typeOptions = [
  { value: 'all', label: 'All Types' },
  { value: 'classification', label: 'Classification' },
  { value: 'regression', label: 'Regression' },
  { value: 'forecasting', label: 'Forecasting' },
  { value: 'anomaly', label: 'Anomaly Detection' },
  { value: 'nlp', label: 'NLP' }
]

// Model registry data
const models = ref([
  {
    id: 'MOD001', name: 'Energy Consumption Predictor', type: 'forecasting',
    description: 'Predicts building energy consumption based on weather and occupancy',
    status: 'production', version: '2.1.0', accuracy: 94.2, latency: 45,
    createdBy: 'Data Science Team', createdAt: '2024-01-10', lastUpdated: '2024-01-15',
    framework: 'TensorFlow', inputFeatures: 24, outputFeatures: 1,
    trainingData: '2023-01-01 to 2023-12-31', deploymentDate: '2024-01-15'
  },
  {
    id: 'MOD002', name: 'Equipment Failure Classifier', type: 'classification',
    description: 'Classifies equipment failure types based on sensor readings',
    status: 'production', version: '3.0.0', accuracy: 96.8, latency: 32,
    createdBy: 'ML Engineering', createdAt: '2023-12-15', lastUpdated: '2024-01-08',
    framework: 'PyTorch', inputFeatures: 56, outputFeatures: 8,
    trainingData: '2022-06-01 to 2023-11-30', deploymentDate: '2024-01-08'
  },
  {
    id: 'MOD003', name: 'Occupancy Anomaly Detector', type: 'anomaly',
    description: 'Detects abnormal occupancy patterns for security and safety',
    status: 'staging', version: '1.2.0', accuracy: 89.5, latency: 28,
    createdBy: 'AI Research', createdAt: '2024-01-05', lastUpdated: '2024-01-12',
    framework: 'Scikit-learn', inputFeatures: 12, outputFeatures: 2,
    trainingData: '2023-07-01 to 2023-12-31', deploymentDate: null
  },
  {
    id: 'MOD004', name: 'Temperature Forecasting', type: 'forecasting',
    description: 'Predicts zone temperatures for HVAC optimization',
    status: 'development', version: '0.9.0', accuracy: 87.3, latency: 38,
    createdBy: 'HVAC Analytics', createdAt: '2024-01-12', lastUpdated: '2024-01-14',
    framework: 'XGBoost', inputFeatures: 18, outputFeatures: 6,
    trainingData: '2023-10-01 to 2024-01-10', deploymentDate: null
  },
  {
    id: 'MOD005', name: 'Energy Theft Detection', type: 'anomaly',
    description: 'Identifies potential energy theft or meter tampering',
    status: 'production', version: '1.5.0', accuracy: 92.4, latency: 52,
    createdBy: 'Security Analytics', createdAt: '2023-12-01', lastUpdated: '2024-01-05',
    framework: 'LightGBM', inputFeatures: 32, outputFeatures: 2,
    trainingData: '2022-01-01 to 2023-11-30', deploymentDate: '2024-01-05'
  },
  {
    id: 'MOD006', name: 'NLP Maintenance Log Analyzer', type: 'nlp',
    description: 'Extracts insights from maintenance work order text',
    status: 'staging', version: '1.0.0', accuracy: 85.7, latency: 120,
    createdBy: 'NLP Team', createdAt: '2024-01-08', lastUpdated: '2024-01-13',
    framework: 'BERT', inputFeatures: 512, outputFeatures: 15,
    trainingData: '2022-01-01 to 2023-12-31', deploymentDate: null
  },
  {
    id: 'MOD007', name: 'HVAC Efficiency Regression', type: 'regression',
    description: 'Predicts HVAC system efficiency scores',
    status: 'development', version: '0.8.5', accuracy: 88.9, latency: 42,
    createdBy: 'Energy Team', createdAt: '2024-01-14', lastUpdated: '2024-01-16',
    framework: 'Random Forest', inputFeatures: 28, outputFeatures: 1,
    trainingData: '2023-08-01 to 2024-01-15', deploymentDate: null
  },
  {
    id: 'MOD008', name: 'Maintenance Priority Predictor', type: 'classification',
    description: 'Predicts maintenance request priority levels',
    status: 'archived', version: '0.5.0', accuracy: 78.2, latency: 25,
    createdBy: 'Operations', createdAt: '2023-11-01', lastUpdated: '2023-12-01',
    framework: 'Logistic Regression', inputFeatures: 15, outputFeatures: 3,
    trainingData: '2022-01-01 to 2023-10-31', deploymentDate: '2023-12-01'
  }
])

// Model statistics
const modelStats = reactive({
  total: 0,
  production: 0,
  staging: 0,
  development: 0,
  archived: 0,
  avgAccuracy: 0,
  avgLatency: 0,
  totalDeployments: 0
})

// Version history for selected model
const versionHistory = ref([
  { version: '3.0.0', date: '2024-01-15', accuracy: 96.8, latency: 32, status: 'production' },
  { version: '2.5.0', date: '2023-12-20', accuracy: 95.2, latency: 35, status: 'archived' },
  { version: '2.0.0', date: '2023-11-15', accuracy: 93.5, latency: 38, status: 'archived' },
  { version: '1.0.0', date: '2023-10-01', accuracy: 90.1, latency: 42, status: 'archived' }
])

// Register model form
const registerModelForm = reactive({
  name: '',
  type: 'classification',
  description: '',
  framework: '',
  version: '1.0.0',
  createdBy: ''
})

// Edit model form
const editModelForm = reactive({
  id: '',
  name: '',
  type: '',
  description: '',
  status: '',
  version: '',
  framework: '',
  accuracy: 0,
  latency: 0
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 8,
  total: models.value.length
})

// Filtered models
const filteredModels = computed(() => {
  let filtered = models.value
  if (searchKeyword.value) {
    filtered = filtered.filter(m =>
        m.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        m.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        m.description.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(m => m.status === selectedStatus.value)
  }
  if (selectedType.value !== 'all') {
    filtered = filtered.filter(m => m.type === selectedType.value)
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

  performanceChart = echarts.init(chartRef.value)
  performanceChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Accuracy (%)', 'Latency (ms)'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: models.value.map(m => m.name.substring(0, 15)), axisLabel: { rotate: 30, interval: 0 } },
    yAxis: [
      { type: 'value', name: 'Accuracy (%)', min: 0, max: 100 },
      { type: 'value', name: 'Latency (ms)', min: 0, max: 150 }
    ],
    series: [
      { name: 'Accuracy (%)', type: 'bar', data: models.value.map(m => m.accuracy), itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top', formatter: '{c}%' } },
      { name: 'Latency (ms)', type: 'line', data: models.value.map(m => m.latency), smooth: true, lineStyle: { color: '#67C23A', width: 2 }, symbol: 'circle', symbolSize: 8, yAxisIndex: 1 }
    ]
  })
}

const updateStats = () => {
  modelStats.total = models.value.length
  modelStats.production = models.value.filter(m => m.status === 'production').length
  modelStats.staging = models.value.filter(m => m.status === 'staging').length
  modelStats.development = models.value.filter(m => m.status === 'development').length
  modelStats.archived = models.value.filter(m => m.status === 'archived').length
  modelStats.avgAccuracy = Math.round(models.value.reduce((sum, m) => sum + m.accuracy, 0) / models.value.length)
  modelStats.avgLatency = Math.round(models.value.reduce((sum, m) => sum + m.latency, 0) / models.value.length)
  modelStats.totalDeployments = models.value.filter(m => m.status === 'production' || m.status === 'staging').length
}

const handleResize = () => {
  performanceChart?.resize()
}

// ==================== Model Functions ====================
const refreshModels = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  loading.value = false
  ElMessage.success('Model registry refreshed successfully')
}

const viewModelDetails = (model: any) => {
  selectedModel.value = model
  detailsVisible.value = true
}

const viewVersionHistory = (model: any) => {
  selectedModel.value = model
  versionHistoryVisible.value = true
}

const editModel = (model: any) => {
  editModelForm.id = model.id
  editModelForm.name = model.name
  editModelForm.type = model.type
  editModelForm.description = model.description
  editModelForm.status = model.status
  editModelForm.version = model.version
  editModelForm.framework = model.framework
  editModelForm.accuracy = model.accuracy
  editModelForm.latency = model.latency
  editModelVisible.value = true
}

const saveModelEdit = async () => {
  if (!editModelForm.name) {
    ElMessage.warning('Please enter a model name')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1000))

  const index = models.value.findIndex(m => m.id === editModelForm.id)
  if (index !== -1) {
    models.value[index] = {
      ...models.value[index],
      name: editModelForm.name,
      type: editModelForm.type,
      description: editModelForm.description,
      status: editModelForm.status,
      version: editModelForm.version,
      framework: editModelForm.framework,
      accuracy: editModelForm.accuracy,
      latency: editModelForm.latency,
      lastUpdated: new Date().toISOString().split('T')[0]
    }
  }

  updateStats()
  initChart()
  editModelVisible.value = false
  ElMessage.success('Model updated successfully')
}

const deleteModel = async (model: any) => {
  await ElMessageBox.confirm(
      `Delete model "${model.name}"? This action cannot be undone.`,
      'Confirm Delete',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'danger'
      }
  )

  const index = models.value.findIndex(m => m.id === model.id)
  if (index !== -1) {
    models.value.splice(index, 1)
  }

  updateStats()
  initChart()
  ElMessage.success('Model deleted successfully')
}

const openRegisterModel = () => {
  registerModelForm.name = ''
  registerModelForm.type = 'classification'
  registerModelForm.description = ''
  registerModelForm.framework = ''
  registerModelForm.version = '1.0.0'
  registerModelForm.createdBy = ''
  registerModelVisible.value = true
}

const registerModel = async () => {
  if (!registerModelForm.name) {
    ElMessage.warning('Please enter a model name')
    return
  }

  if (!registerModelForm.createdBy) {
    ElMessage.warning('Please enter creator name')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1000))

  const newModel = {
    id: `MOD${String(models.value.length + 1).padStart(3, '0')}`,
    name: registerModelForm.name,
    type: registerModelForm.type,
    description: registerModelForm.description || 'New model',
    status: 'development',
    version: registerModelForm.version,
    accuracy: 0,
    latency: 0,
    createdBy: registerModelForm.createdBy,
    createdAt: new Date().toISOString().split('T')[0],
    lastUpdated: new Date().toISOString().split('T')[0],
    framework: registerModelForm.framework || 'Unknown',
    inputFeatures: 0,
    outputFeatures: 0,
    trainingData: null,
    deploymentDate: null
  }

  models.value.unshift(newModel)
  updateStats()
  initChart()
  registerModelVisible.value = false
  ElMessage.success('Model registered successfully')
}

const deployModel = async (model: any) => {
  await ElMessageBox.confirm(
      `Deploy model "${model.name}" to production?`,
      'Confirm Deployment',
      {
        confirmButtonText: 'Deploy',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  )

  const index = models.value.findIndex(m => m.id === model.id)
  if (index !== -1) {
    models.value[index].status = 'production'
    models.value[index].deploymentDate = new Date().toISOString().split('T')[0]
  }

  updateStats()
  initChart()
  ElMessage.success('Model deployed to production successfully')
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'production': return 'success'
    case 'staging': return 'warning'
    case 'development': return 'primary'
    case 'archived': return 'info'
    default: return 'info'
  }
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'production': return CircleCheck
    case 'staging': return Edit
    case 'development': return MagicStick
    case 'archived': return Delete
    default: return Clock
  }
}

const getTypeIcon = (type: string) => {
  switch (type) {
    case 'classification': return '📊'
    case 'regression': return '📈'
    case 'forecasting': return '🔮'
    case 'anomaly': return '⚠️'
    case 'nlp': return '💬'
    default: return '🤖'
  }
}

const getAccuracyColor = (accuracy: number) => {
  if (accuracy >= 90) return '#67C23A'
  if (accuracy >= 80) return '#E6A23C'
  return '#F56C6C'
}

const selectedModel = ref<any>(null)
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
          <span class="loading-title">Loading Model Registry</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">AI Governance - Model Registry</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="model-registry-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Model Registry</h1>
        <p class="page-subtitle">Central repository for AI model lifecycle management</p>
      </div>
      <div class="header-right">
        <el-button type="primary" size="large" @click="openRegisterModel">
          <el-icon><Plus /></el-icon>
          Register Model
        </el-button>
        <el-button size="large" @click="refreshModels" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total-icon">
          <el-icon><Cpu /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ modelStats.total }}</div>
          <div class="stat-label">Total Models</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ modelStats.production }} Production</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon accuracy-icon">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ modelStats.avgAccuracy }}%</div>
          <div class="stat-label">Avg Accuracy</div>
        </div>
        <div class="stat-trend">
          <el-progress :percentage="modelStats.avgAccuracy" :stroke-width="4" :show-text="false" />
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon latency-icon">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ modelStats.avgLatency }}ms</div>
          <div class="stat-label">Avg Inference Latency</div>
        </div>
        <div class="stat-trend">
          <span class="trend-down">-5ms from last month</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon deployments-icon">
          <el-icon><VideoPlay /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ modelStats.totalDeployments }}</div>
          <div class="stat-label">Active Deployments</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+2 this quarter</span>
        </div>
      </div>
    </div>

    <!-- Performance Chart -->
    <div class="chart-section">
      <div class="section-header">
        <h3>Model Performance Metrics</h3>
        <el-button text type="primary" @click="initChart">Refresh</el-button>
      </div>
      <div ref="chartRef" class="performance-chart" style="height: 320px"></div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-bar">
      <div class="filters-left">
        <div class="search-box">
          <el-input
              v-model="searchKeyword"
              placeholder="Search models..."
              :prefix-icon="Search"
              clearable
              style="width: 240px"
          />
        </div>
        <div class="status-filters">
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
      <div class="filters-right">
        <el-select v-model="selectedType" placeholder="Model Type" clearable style="width: 160px">
          <el-option v-for="t in typeOptions.slice(1)" :key="t.value" :label="t.label" :value="t.value" />
        </el-select>
      </div>
    </div>

    <!-- Models Grid -->
    <div class="models-grid">
      <div
          v-for="model in filteredModels"
          :key="model.id"
          class="model-card"
          :class="model.status"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="model-type">
            <span class="type-icon">{{ getTypeIcon(model.type) }}</span>
            <span class="type-name">{{ model.type.toUpperCase() }}</span>
          </div>
          <div class="model-status">
            <el-tag :type="getStatusType(model.status)" size="small" effect="light">
              <el-icon><component :is="getStatusIcon(model.status)" /></el-icon>
              {{ model.status.toUpperCase() }}
            </el-tag>
          </div>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <h4 class="model-name">{{ model.name }}</h4>
          <p class="model-description">{{ model.description }}</p>

          <!-- Performance Metrics -->
          <div class="performance-metrics">
            <div class="metric">
              <span class="metric-label">Accuracy</span>
              <span class="metric-value" :style="{ color: getAccuracyColor(model.accuracy) }">
                {{ model.accuracy }}%
              </span>
            </div>
            <div class="metric">
              <span class="metric-label">Latency</span>
              <span class="metric-value">{{ model.latency }}ms</span>
            </div>
            <div class="metric">
              <span class="metric-label">Version</span>
              <span class="metric-value">v{{ model.version }}</span>
            </div>
          </div>

          <!-- Framework & Features -->
          <div class="model-details">
            <div class="detail-item">
              <span class="detail-label">Framework:</span>
              <span class="detail-value">{{ model.framework }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Features:</span>
              <span class="detail-value">{{ model.inputFeatures }} in → {{ model.outputFeatures }} out</span>
            </div>
          </div>

          <!-- Dates -->
          <div class="dates">
            <div class="date-item">
              <span class="date-label">Created:</span>
              <span class="date-value">{{ model.createdAt }}</span>
            </div>
            <div class="date-item">
              <span class="date-label">Updated:</span>
              <span class="date-value">{{ model.lastUpdated }}</span>
            </div>
          </div>

          <!-- Creator -->
          <div class="creator">
            <el-icon><User /></el-icon>
            <span>{{ model.createdBy }}</span>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="card-actions">
            <el-button size="small" @click="viewModelDetails(model)">Details</el-button>
            <el-button size="small" @click="viewVersionHistory(model)">Versions</el-button>
            <el-button size="small" type="primary" @click="editModel(model)">Edit</el-button>
            <el-button
                v-if="model.status !== 'production'"
                size="small"
                type="success"
                @click="deployModel(model)"
            >
              Deploy
            </el-button>
            <el-button size="small" type="danger" @click="deleteModel(model)">Delete</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredModels.length === 0" class="empty-state">
      <el-empty description="No models found">
        <el-button type="primary" @click="openRegisterModel">Register Model</el-button>
      </el-empty>
    </div>

    <!-- Pagination -->
    <div v-if="filteredModels.length > 0" class="pagination-wrapper">
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

    <!-- Model Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="selectedModel?.name" width="650px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Model ID">{{ selectedModel?.id }}</el-descriptions-item>
        <el-descriptions-item label="Version">{{ selectedModel?.version }}</el-descriptions-item>
        <el-descriptions-item label="Type">{{ selectedModel?.type?.toUpperCase() }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusType(selectedModel?.status)" size="small">
            {{ selectedModel?.status?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Framework">{{ selectedModel?.framework }}</el-descriptions-item>
        <el-descriptions-item label="Creator">{{ selectedModel?.createdBy }}</el-descriptions-item>
        <el-descriptions-item label="Accuracy">{{ selectedModel?.accuracy }}%</el-descriptions-item>
        <el-descriptions-item label="Latency">{{ selectedModel?.latency }}ms</el-descriptions-item>
        <el-descriptions-item label="Input Features">{{ selectedModel?.inputFeatures }}</el-descriptions-item>
        <el-descriptions-item label="Output Features">{{ selectedModel?.outputFeatures }}</el-descriptions-item>
        <el-descriptions-item label="Created At">{{ selectedModel?.createdAt }}</el-descriptions-item>
        <el-descriptions-item label="Last Updated">{{ selectedModel?.lastUpdated }}</el-descriptions-item>
        <el-descriptions-item label="Deployment Date" v-if="selectedModel?.deploymentDate">
          {{ selectedModel?.deploymentDate }}
        </el-descriptions-item>
        <el-descriptions-item label="Training Data" :span="2">{{ selectedModel?.trainingData || 'Not specified' }}</el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedModel?.description }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
        <el-button type="primary" @click="editModel(selectedModel)">Edit Model</el-button>
      </template>
    </el-dialog>

    <!-- Version History Dialog -->
    <el-dialog v-model="versionHistoryVisible" :title="`Version History - ${selectedModel?.name}`" width="700px">
      <el-table :data="versionHistory" stripe>
        <el-table-column prop="version" label="Version" width="100" />
        <el-table-column prop="date" label="Release Date" width="120" />
        <el-table-column label="Accuracy" width="120" align="center">
          <template #default="{ row }">
            <span :style="{ color: getAccuracyColor(row.accuracy) }">{{ row.accuracy }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="Latency" width="100" align="center">
          {{ row.latency }}ms
        </el-table-column>
        <el-table-column label="Status" width="120" align="center">
          <el-tag :type="getStatusType(row.status)" size="small">
            {{ row.status.toUpperCase() }}
          </el-tag>
        </el-table-column>
        <el-table-column label="Actions" width="100" align="center">
          <el-button link type="primary" size="small">Compare</el-button>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="versionHistoryVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Register Model Dialog -->
    <el-dialog v-model="registerModelVisible" title="Register New Model" width="550px">
      <el-form :model="registerModelForm" label-width="120px">
        <el-form-item label="Model Name" required>
          <el-input v-model="registerModelForm.name" placeholder="Enter model name" />
        </el-form-item>
        <el-form-item label="Model Type">
          <el-select v-model="registerModelForm.type" style="width: 100%">
            <el-option v-for="t in typeOptions.slice(1)" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Framework">
          <el-input v-model="registerModelForm.framework" placeholder="e.g., TensorFlow, PyTorch" />
        </el-form-item>
        <el-form-item label="Version">
          <el-input v-model="registerModelForm.version" placeholder="1.0.0" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="registerModelForm.description" type="textarea" rows="2" placeholder="Model description" />
        </el-form-item>
        <el-form-item label="Created By" required>
          <el-input v-model="registerModelForm.createdBy" placeholder="Team or individual name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="registerModelVisible = false">Cancel</el-button>
        <el-button type="primary" @click="registerModel">Register Model</el-button>
      </template>
    </el-dialog>

    <!-- Edit Model Dialog -->
    <el-dialog v-model="editModelVisible" title="Edit Model" width="550px">
      <el-form :model="editModelForm" label-width="120px">
        <el-form-item label="Model Name" required>
          <el-input v-model="editModelForm.name" placeholder="Enter model name" />
        </el-form-item>
        <el-form-item label="Model Type">
          <el-select v-model="editModelForm.type" style="width: 100%">
            <el-option v-for="t in typeOptions.slice(1)" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Status">
          <el-select v-model="editModelForm.status" style="width: 100%">
            <el-option label="Production" value="production" />
            <el-option label="Staging" value="staging" />
            <el-option label="Development" value="development" />
            <el-option label="Archived" value="archived" />
          </el-select>
        </el-form-item>
        <el-form-item label="Version">
          <el-input v-model="editModelForm.version" placeholder="1.0.0" />
        </el-form-item>
        <el-form-item label="Framework">
          <el-input v-model="editModelForm.framework" placeholder="Framework name" />
        </el-form-item>
        <el-form-item label="Accuracy (%)">
          <el-input-number v-model="editModelForm.accuracy" :min="0" :max="100" :step="0.1" />
        </el-form-item>
        <el-form-item label="Latency (ms)">
          <el-input-number v-model="editModelForm.latency" :min="0" :max="1000" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="editModelForm.description" type="textarea" rows="2" placeholder="Model description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editModelVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveModelEdit">Save Changes</el-button>
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
.model-registry-container {
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

.accuracy-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.latency-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.deployments-icon {
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

.trend-down {
  color: #f56c6c;
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

.performance-chart {
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

.status-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.status-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 40px;
  font-size: 13px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s ease;
}

.status-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.status-chip.active {
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

.filters-right {
  display: flex;
  gap: 12px;
}

/* Models Grid */
.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.model-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
}

.model-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.model-card.production {
  border-left: 4px solid #67c23a;
}

.model-card.staging {
  border-left: 4px solid #e6a23c;
}

.model-card.development {
  border-left: 4px solid #409eff;
}

.model-card.archived {
  border-left: 4px solid #909399;
}

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 0 20px;
}

.model-type {
  display: flex;
  align-items: center;
  gap: 8px;
}

.type-icon {
  font-size: 18px;
}

.type-name {
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

.model-name {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 10px 0;
  line-height: 1.4;
}

.model-description {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.performance-metrics {
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

.model-details {
  margin-bottom: 12px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  margin-bottom: 6px;
}

.detail-label {
  color: #909399;
}

.detail-value {
  color: #1e293b;
  font-weight: 500;
}

.dates {
  margin-bottom: 12px;
}

.date-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  margin-bottom: 4px;
}

.date-label {
  color: #909399;
}

.date-value {
  color: #1e293b;
  font-weight: 500;
}

.creator {
  display: flex;
  align-items: center;
  gap: 6px;
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

  .models-grid {
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  }
}

@media (max-width: 768px) {
  .model-registry-container {
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
  }

  .status-filters {
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

  .models-grid {
    grid-template-columns: 1fr;
  }

  .card-actions {
    justify-content: center;
  }
}
</style>