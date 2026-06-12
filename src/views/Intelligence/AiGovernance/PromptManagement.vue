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
  EditPen, Tickets
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Loading prompt templates...',
  'Analyzing prompt performance...',
  'Preparing version history...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedCategory = ref('all')
const selectedStatus = ref('all')
const detailsVisible = ref(false)
const createPromptVisible = ref(false)
const editPromptVisible = ref(false)
const testPromptVisible = ref(false)
const versionHistoryVisible = ref(false)
const chartRef = ref(null)

let usageChart: echarts.ECharts | null = null

// Category filters
const categoryOptions = [
  { value: 'all', label: 'All Categories' },
  { value: 'system', label: 'System Operations' },
  { value: 'analytics', label: 'Analytics' },
  { value: 'reporting', label: 'Reporting' },
  { value: 'alerts', label: 'Alerts & Notifications' },
  { value: 'maintenance', label: 'Maintenance' }
]

// Status filters
const statusOptions = [
  { value: 'all', label: 'All Status' },
  { value: 'active', label: 'Active', color: '#67C23A' },
  { value: 'draft', label: 'Draft', color: '#E6A23C' },
  { value: 'deprecated', label: 'Deprecated', color: '#909399' }
]

// Prompt templates data
const prompts = ref([
  {
    id: 'PR001', name: 'System Health Summary', category: 'system',
    template: 'Generate a comprehensive system health report including:\n- Overall health score\n- Active alarms by severity\n- System uptime\n- Top 5 performance metrics\nFormat as a structured summary.',
    description: 'Generates daily system health summary for operations team',
    status: 'active', version: '2.1.0', usageCount: 1245,
    avgResponseTime: 2.3, successRate: 98.5, lastUpdated: '2024-01-15',
    createdBy: 'AI Team', tokens: 245, model: 'GPT-4'
  },
  {
    id: 'PR002', name: 'Energy Analysis', category: 'analytics',
    template: 'Analyze the energy consumption data for the past week.\nProvide insights on:\n- Peak usage periods\n- Anomaly detection\n- Savings opportunities\n- Comparison with baseline\nInclude actionable recommendations.',
    description: 'Analyzes energy consumption patterns and provides optimization suggestions',
    status: 'active', version: '1.8.0', usageCount: 892,
    avgResponseTime: 3.1, successRate: 96.2, lastUpdated: '2024-01-12',
    createdBy: 'Energy Team', tokens: 312, model: 'GPT-4'
  },
  {
    id: 'PR003', name: 'Alarms Prioritization', category: 'alerts',
    template: 'Review the list of active alarms.\nPrioritize them based on:\n- Severity level\n- Impact on operations\n- Time since first occurrence\n- Historical patterns\nProvide a prioritized action list.',
    description: 'Prioritizes alarms for efficient incident response',
    status: 'active', version: '3.0.0', usageCount: 2156,
    avgResponseTime: 1.8, successRate: 99.1, lastUpdated: '2024-01-14',
    createdBy: 'Security Team', tokens: 178, model: 'GPT-3.5'
  },
  {
    id: 'PR004', name: 'Maintenance Scheduling', category: 'maintenance',
    template: 'Create an optimized maintenance schedule for the next week considering:\n- Equipment criticality\n- Historical failure patterns\n- Resource availability\n- Seasonal factors\nProposed schedule with justifications.',
    description: 'Optimizes maintenance scheduling based on predictive analytics',
    status: 'active', version: '1.5.0', usageCount: 567,
    avgResponseTime: 2.9, successRate: 94.8, lastUpdated: '2024-01-10',
    createdBy: 'Maintenance Team', tokens: 289, model: 'GPT-4'
  },
  {
    id: 'PR005', name: 'Report Generation', category: 'reporting',
    template: 'Generate a weekly operations report including:\n- Key performance indicators\n- Incident summary\n- Energy consumption trends\n- Maintenance activities\n- Recommendations for next week',
    description: 'Generates comprehensive weekly operations report',
    status: 'draft', version: '0.9.0', usageCount: 0,
    avgResponseTime: 0, successRate: 0, lastUpdated: '2024-01-16',
    createdBy: 'Reporting Team', tokens: 267, model: 'GPT-4'
  },
  {
    id: 'PR006', name: 'Anomaly Detection', category: 'analytics',
    template: 'Analyze sensor data for anomalies using statistical methods.\nIdentify:\n- Unusual patterns\n- Potential equipment issues\n- Data quality problems\n- Emerging trends\nFlag any critical findings.',
    description: 'Detects anomalies in real-time sensor data',
    status: 'active', version: '2.2.0', usageCount: 1678,
    avgResponseTime: 2.5, successRate: 97.3, lastUpdated: '2024-01-13',
    createdBy: 'ML Team', tokens: 234, model: 'GPT-4'
  },
  {
    id: 'PR007', name: 'Root Cause Analysis', category: 'system',
    template: 'Given the fault description and sensor data, perform root cause analysis.\nConsider:\n- Potential failure modes\n- Contributing factors\n- Historical patterns\n- Environmental conditions\nProvide likely causes and evidence.',
    description: 'Performs AI-driven root cause analysis for system faults',
    status: 'deprecated', version: '1.0.0', usageCount: 345,
    avgResponseTime: 4.2, successRate: 85.5, lastUpdated: '2023-12-01',
    createdBy: 'AI Research', tokens: 356, model: 'GPT-3.5'
  },
  {
    id: 'PR008', name: 'Cost Optimization', category: 'analytics',
    template: 'Analyze operational costs and identify optimization opportunities.\nFocus on:\n- Energy costs\n- Maintenance expenses\n- Resource utilization\n- Vendor comparisons\nProvide cost-saving recommendations.',
    description: 'Identifies cost optimization opportunities across operations',
    status: 'draft', version: '0.8.0', usageCount: 0,
    avgResponseTime: 0, successRate: 0, lastUpdated: '2024-01-16',
    createdBy: 'Finance Team', tokens: 298, model: 'GPT-4'
  }
])

// Prompt statistics
const promptStats = reactive({
  total: 0,
  active: 0,
  draft: 0,
  deprecated: 0,
  totalUsage: 0,
  avgSuccessRate: 0,
  avgResponseTime: 0
})

// Version history for selected prompt
const versionHistory = ref([
  { version: '2.1.0', date: '2024-01-15', usageCount: 1245, successRate: 98.5, status: 'active' },
  { version: '2.0.0', date: '2023-12-20', usageCount: 890, successRate: 97.2, status: 'archived' },
  { version: '1.5.0', date: '2023-11-15', usageCount: 567, successRate: 95.8, status: 'archived' },
  { version: '1.0.0', date: '2023-10-01', usageCount: 234, successRate: 93.5, status: 'archived' }
])

// Create prompt form
const createPromptForm = reactive({
  name: '',
  category: 'system',
  template: '',
  description: '',
  model: 'GPT-4'
})

// Edit prompt form
const editPromptForm = reactive({
  id: '',
  name: '',
  category: '',
  template: '',
  description: '',
  status: '',
  version: '',
  model: ''
})

// Test prompt form
const testPromptForm = reactive({
  promptId: '',
  input: '',
  response: '',
  loading: false
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 8,
  total: prompts.value.length
})

// Filtered prompts
const filteredPrompts = computed(() => {
  let filtered = prompts.value
  if (searchKeyword.value) {
    filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        p.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        p.description.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedCategory.value !== 'all') {
    filtered = filtered.filter(p => p.category === selectedCategory.value)
  }
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(p => p.status === selectedStatus.value)
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
    legend: { data: ['Usage Count', 'Success Rate (%)'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: prompts.value.map(p => p.name.substring(0, 15)), axisLabel: { rotate: 30, interval: 0 } },
    yAxis: [
      { type: 'value', name: 'Usage Count' },
      { type: 'value', name: 'Success Rate (%)', min: 0, max: 100 }
    ],
    series: [
      { name: 'Usage Count', type: 'bar', data: prompts.value.map(p => p.usageCount), itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top' } },
      { name: 'Success Rate (%)', type: 'line', data: prompts.value.map(p => p.successRate), smooth: true, lineStyle: { color: '#67C23A', width: 2 }, symbol: 'circle', symbolSize: 8, yAxisIndex: 1, label: { show: true, position: 'top', formatter: '{c}%' } }
    ]
  })
}

const updateStats = () => {
  promptStats.total = prompts.value.length
  promptStats.active = prompts.value.filter(p => p.status === 'active').length
  promptStats.draft = prompts.value.filter(p => p.status === 'draft').length
  promptStats.deprecated = prompts.value.filter(p => p.status === 'deprecated').length
  promptStats.totalUsage = prompts.value.reduce((sum, p) => sum + p.usageCount, 0)

  const activePrompts = prompts.value.filter(p => p.status === 'active')
  if (activePrompts.length > 0) {
    promptStats.avgSuccessRate = Math.round(activePrompts.reduce((sum, p) => sum + p.successRate, 0) / activePrompts.length)
    promptStats.avgResponseTime = parseFloat((activePrompts.reduce((sum, p) => sum + p.avgResponseTime, 0) / activePrompts.length).toFixed(1))
  }
}

const handleResize = () => {
  usageChart?.resize()
}

// ==================== Prompt Functions ====================
const refreshPrompts = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  loading.value = false
  ElMessage.success('Prompts refreshed successfully')
}

const viewPromptDetails = (prompt: any) => {
  selectedPrompt.value = prompt
  detailsVisible.value = true
}

const viewVersionHistory = (prompt: any) => {
  selectedPrompt.value = prompt
  versionHistoryVisible.value = true
}

const editPrompt = (prompt: any) => {
  editPromptForm.id = prompt.id
  editPromptForm.name = prompt.name
  editPromptForm.category = prompt.category
  editPromptForm.template = prompt.template
  editPromptForm.description = prompt.description
  editPromptForm.status = prompt.status
  editPromptForm.version = prompt.version
  editPromptForm.model = prompt.model
  editPromptVisible.value = true
}

const savePromptEdit = async () => {
  if (!editPromptForm.name) {
    ElMessage.warning('Please enter a prompt name')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1000))

  const index = prompts.value.findIndex(p => p.id === editPromptForm.id)
  if (index !== -1) {
    prompts.value[index] = {
      ...prompts.value[index],
      name: editPromptForm.name,
      category: editPromptForm.category,
      template: editPromptForm.template,
      description: editPromptForm.description,
      status: editPromptForm.status,
      version: editPromptForm.version,
      model: editPromptForm.model,
      lastUpdated: new Date().toISOString().split('T')[0]
    }
  }

  updateStats()
  initChart()
  editPromptVisible.value = false
  ElMessage.success('Prompt updated successfully')
}

const deletePrompt = async (prompt: any) => {
  await ElMessageBox.confirm(
      `Delete prompt "${prompt.name}"? This action cannot be undone.`,
      'Confirm Delete',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'danger'
      }
  )

  const index = prompts.value.findIndex(p => p.id === prompt.id)
  if (index !== -1) {
    prompts.value.splice(index, 1)
  }

  updateStats()
  initChart()
  ElMessage.success('Prompt deleted successfully')
}

const openCreatePrompt = () => {
  createPromptForm.name = ''
  createPromptForm.category = 'system'
  createPromptForm.template = ''
  createPromptForm.description = ''
  createPromptForm.model = 'GPT-4'
  createPromptVisible.value = true
}

const createPrompt = async () => {
  if (!createPromptForm.name) {
    ElMessage.warning('Please enter a prompt name')
    return
  }

  if (!createPromptForm.template) {
    ElMessage.warning('Please enter a prompt template')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1000))

  const newPrompt = {
    id: `PR${String(prompts.value.length + 1).padStart(3, '0')}`,
    name: createPromptForm.name,
    category: createPromptForm.category,
    template: createPromptForm.template,
    description: createPromptForm.description || 'New prompt',
    status: 'draft',
    version: '1.0.0',
    usageCount: 0,
    avgResponseTime: 0,
    successRate: 0,
    lastUpdated: new Date().toISOString().split('T')[0],
    createdBy: 'Current User',
    tokens: createPromptForm.template.split(' ').length,
    model: createPromptForm.model
  }

  prompts.value.unshift(newPrompt)
  updateStats()
  initChart()
  createPromptVisible.value = false
  ElMessage.success('Prompt created successfully')
}

const openTestPrompt = (prompt: any) => {
  testPromptForm.promptId = prompt.id
  testPromptForm.input = ''
  testPromptForm.response = ''
  testPromptVisible.value = true
}

const runTest = async () => {
  if (!testPromptForm.input) {
    ElMessage.warning('Please enter test input')
    return
  }

  testPromptForm.loading = true
  await new Promise(resolve => setTimeout(resolve, 2000))

  const prompt = prompts.value.find(p => p.id === testPromptForm.promptId)
  testPromptForm.response = `Based on the prompt "${prompt?.name}", analyzing your input: "${testPromptForm.input}"\n\n` +
      `[AI Response Simulation]\n\n` +
      `Analysis complete. Here are the key findings:\n` +
      `• System health score: 98.5%\n` +
      `• Active alarms: 3 (2 critical, 1 warning)\n` +
      `• Energy efficiency: 94.2%\n` +
      `• Recommended actions: Schedule preventive maintenance for HVAC system\n\n` +
      `Would you like to refine this analysis with additional parameters?`

  testPromptForm.loading = false
  ElMessage.success('Test completed')
}

const copyToClipboard = (text: string) => {
  navigator.clipboard.writeText(text)
  ElMessage.success('Copied to clipboard')
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
    case 'active': return 'success'
    case 'draft': return 'warning'
    case 'deprecated': return 'info'
    default: return 'info'
  }
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'active': return CircleCheck
    case 'draft': return Edit
    case 'deprecated': return Delete
    default: return Clock
  }
}

const getCategoryIcon = (category: string) => {
  switch (category) {
    case 'system': return '🖥️'
    case 'analytics': return '📊'
    case 'reporting': return '📄'
    case 'alerts': return '🔔'
    case 'maintenance': return '🔧'
    default: return '📋'
  }
}

const getSuccessRateColor = (rate: number) => {
  if (rate >= 95) return '#67C23A'
  if (rate >= 85) return '#E6A23C'
  return '#F56C6C'
}

const selectedPrompt = ref<any>(null)
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
          <span class="loading-title">Loading Prompt Management</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">AI Governance - Prompt Management</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="prompt-management-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Prompt Management</h1>
        <p class="page-subtitle">Manage and optimize AI prompt templates for consistent outputs</p>
      </div>
      <div class="header-right">
        <el-button type="primary" size="large" @click="openCreatePrompt">
          <el-icon><Plus /></el-icon>
          Create Prompt
        </el-button>
        <el-button size="large" @click="refreshPrompts" :loading="loading">
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
          <div class="stat-value">{{ promptStats.total }}</div>
          <div class="stat-label">Total Prompts</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ promptStats.active }} Active</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon usage-icon">
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ promptStats.totalUsage.toLocaleString() }}</div>
          <div class="stat-label">Total Usage</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+23% this month</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon success-icon">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ promptStats.avgSuccessRate }}%</div>
          <div class="stat-label">Avg Success Rate</div>
        </div>
        <div class="stat-trend">
          <el-progress :percentage="promptStats.avgSuccessRate" :stroke-width="4" :show-text="false" />
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon response-icon">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ promptStats.avgResponseTime }}s</div>
          <div class="stat-label">Avg Response Time</div>
        </div>
        <div class="stat-trend">
          <span class="trend-down">-0.3s</span>
        </div>
      </div>
    </div>

    <!-- Performance Chart -->
    <div class="chart-section">
      <div class="section-header">
        <h3>Prompt Performance Metrics</h3>
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
              placeholder="Search prompts..."
              :prefix-icon="Search"
              clearable
              style="width: 240px"
          />
        </div>
        <div class="category-filters">
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
      <div class="filters-right">
        <el-select v-model="selectedStatus" placeholder="Status" clearable style="width: 120px">
          <el-option v-for="s in statusOptions.slice(1)" :key="s.value" :label="s.label" :value="s.value" />
        </el-select>
      </div>
    </div>

    <!-- Prompts Grid -->
    <div class="prompts-grid">
      <div
          v-for="prompt in filteredPrompts"
          :key="prompt.id"
          class="prompt-card"
          :class="prompt.status"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="prompt-category">
            <span class="category-icon">{{ getCategoryIcon(prompt.category) }}</span>
            <span class="category-name">{{ prompt.category.toUpperCase() }}</span>
          </div>
          <div class="prompt-status">
            <el-tag :type="getStatusType(prompt.status)" size="small" effect="light">
              <el-icon><component :is="getStatusIcon(prompt.status)" /></el-icon>
              {{ prompt.status.toUpperCase() }}
            </el-tag>
          </div>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <h4 class="prompt-name">{{ prompt.name }}</h4>
          <p class="prompt-description">{{ prompt.description }}</p>

          <!-- Performance Metrics -->
          <div class="performance-metrics">
            <div class="metric">
              <span class="metric-label">Usage</span>
              <span class="metric-value">{{ prompt.usageCount.toLocaleString() }}</span>
            </div>
            <div class="metric">
              <span class="metric-label">Success Rate</span>
              <span class="metric-value" :style="{ color: getSuccessRateColor(prompt.successRate) }">
                {{ prompt.successRate }}%
              </span>
            </div>
            <div class="metric">
              <span class="metric-label">Response</span>
              <span class="metric-value">{{ prompt.avgResponseTime }}s</span>
            </div>
          </div>

          <!-- Template Preview -->
          <div class="template-preview">
            <div class="template-label">Template:</div>
            <div class="template-text">{{ prompt.template.substring(0, 100) }}...</div>
          </div>

          <!-- Meta Info -->
          <div class="meta-info">
            <div class="meta-item">
              <span class="meta-label">Version:</span>
              <span class="meta-value">v{{ prompt.version }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Model:</span>
              <span class="meta-value">{{ prompt.model }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Tokens:</span>
              <span class="meta-value">{{ prompt.tokens }}</span>
            </div>
          </div>

          <!-- Last Updated -->
          <div class="last-updated">
            <el-icon><Clock /></el-icon>
            <span>Updated: {{ prompt.lastUpdated }}</span>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="created-by">
            <el-icon><User /></el-icon>
            <span>{{ prompt.createdBy }}</span>
          </div>
          <div class="card-actions">
            <el-button size="small" @click="viewPromptDetails(prompt)">Details</el-button>
            <el-button size="small" @click="openTestPrompt(prompt)">Test</el-button>
            <el-button size="small" @click="viewVersionHistory(prompt)">Versions</el-button>
            <el-button size="small" type="primary" @click="editPrompt(prompt)">Edit</el-button>
            <el-button size="small" type="danger" @click="deletePrompt(prompt)">Delete</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredPrompts.length === 0" class="empty-state">
      <el-empty description="No prompts found">
        <el-button type="primary" @click="openCreatePrompt">Create Prompt</el-button>
      </el-empty>
    </div>

    <!-- Pagination -->
    <div v-if="filteredPrompts.length > 0" class="pagination-wrapper">
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

    <!-- Prompt Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="selectedPrompt?.name" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Prompt ID">{{ selectedPrompt?.id }}</el-descriptions-item>
        <el-descriptions-item label="Version">{{ selectedPrompt?.version }}</el-descriptions-item>
        <el-descriptions-item label="Category">{{ selectedPrompt?.category?.toUpperCase() }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusType(selectedPrompt?.status)" size="small">
            {{ selectedPrompt?.status?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Model">{{ selectedPrompt?.model }}</el-descriptions-item>
        <el-descriptions-item label="Created By">{{ selectedPrompt?.createdBy }}</el-descriptions-item>
        <el-descriptions-item label="Usage Count">{{ selectedPrompt?.usageCount.toLocaleString() }}</el-descriptions-item>
        <el-descriptions-item label="Success Rate">{{ selectedPrompt?.successRate }}%</el-descriptions-item>
        <el-descriptions-item label="Avg Response">{{ selectedPrompt?.avgResponseTime }}s</el-descriptions-item>
        <el-descriptions-item label="Tokens">{{ selectedPrompt?.tokens }}</el-descriptions-item>
        <el-descriptions-item label="Last Updated">{{ selectedPrompt?.lastUpdated }}</el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedPrompt?.description }}</el-descriptions-item>
        <el-descriptions-item label="Template" :span="2">
          <div class="template-full">
            <pre>{{ selectedPrompt?.template }}</pre>
            <el-button size="small" @click="copyToClipboard(selectedPrompt?.template)">Copy</el-button>
          </div>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
        <el-button type="primary" @click="openTestPrompt(selectedPrompt)">Test Prompt</el-button>
      </template>
    </el-dialog>

    <!-- Version History Dialog -->
    <el-dialog v-model="versionHistoryVisible" :title="`Version History - ${selectedPrompt?.name}`" width="700px">
      <el-table :data="versionHistory" stripe>
        <el-table-column prop="version" label="Version" width="100" />
        <el-table-column prop="date" label="Release Date" width="120" />
        <el-table-column label="Usage Count" width="120" align="center">
          <template #default="{ row }">
            {{ row.usageCount.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="Success Rate" width="120" align="center">
          <template #default="{ row }">
            <span :style="{ color: getSuccessRateColor(row.successRate) }">{{ row.successRate }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="120" align="center">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
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

    <!-- Create Prompt Dialog -->
    <el-dialog v-model="createPromptVisible" title="Create New Prompt" width="600px">
      <el-form :model="createPromptForm" label-width="100px">
        <el-form-item label="Prompt Name" required>
          <el-input v-model="createPromptForm.name" placeholder="Enter prompt name" />
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="createPromptForm.category" style="width: 100%">
            <el-option v-for="c in categoryOptions.slice(1)" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Model">
          <el-select v-model="createPromptForm.model" style="width: 100%">
            <el-option label="GPT-4" value="GPT-4" />
            <el-option label="GPT-3.5" value="GPT-3.5" />
            <el-option label="Claude-2" value="Claude-2" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="createPromptForm.description" type="textarea" rows="2" placeholder="Brief description" />
        </el-form-item>
        <el-form-item label="Template" required>
          <el-input v-model="createPromptForm.template" type="textarea" rows="6" placeholder="Enter the prompt template..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createPromptVisible = false">Cancel</el-button>
        <el-button type="primary" @click="createPrompt">Create Prompt</el-button>
      </template>
    </el-dialog>

    <!-- Edit Prompt Dialog -->
    <el-dialog v-model="editPromptVisible" title="Edit Prompt" width="600px">
      <el-form :model="editPromptForm" label-width="100px">
        <el-form-item label="Prompt Name" required>
          <el-input v-model="editPromptForm.name" placeholder="Enter prompt name" />
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="editPromptForm.category" style="width: 100%">
            <el-option v-for="c in categoryOptions.slice(1)" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Status">
          <el-select v-model="editPromptForm.status" style="width: 100%">
            <el-option label="Active" value="active" />
            <el-option label="Draft" value="draft" />
            <el-option label="Deprecated" value="deprecated" />
          </el-select>
        </el-form-item>
        <el-form-item label="Version">
          <el-input v-model="editPromptForm.version" placeholder="1.0.0" />
        </el-form-item>
        <el-form-item label="Model">
          <el-select v-model="editPromptForm.model" style="width: 100%">
            <el-option label="GPT-4" value="GPT-4" />
            <el-option label="GPT-3.5" value="GPT-3.5" />
            <el-option label="Claude-2" value="Claude-2" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="editPromptForm.description" type="textarea" rows="2" placeholder="Brief description" />
        </el-form-item>
        <el-form-item label="Template" required>
          <el-input v-model="editPromptForm.template" type="textarea" rows="6" placeholder="Enter the prompt template..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editPromptVisible = false">Cancel</el-button>
        <el-button type="primary" @click="savePromptEdit">Save Changes</el-button>
      </template>
    </el-dialog>

    <!-- Test Prompt Dialog -->
    <el-dialog v-model="testPromptVisible" title="Test Prompt" width="700px" top="5vh">
      <div class="test-container">
        <div class="test-prompt-info">
          <el-tag type="primary">Prompt: {{ prompts.find(p => p.id === testPromptForm.promptId)?.name }}</el-tag>
        </div>

        <el-form :model="testPromptForm" label-width="100px">
          <el-form-item label="Input">
            <el-input
                v-model="testPromptForm.input"
                type="textarea"
                rows="4"
                placeholder="Enter test input data..."
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="runTest" :loading="testPromptForm.loading">
              Run Test
            </el-button>
          </el-form-item>
          <el-form-item label="Response" v-if="testPromptForm.response">
            <div class="test-response">
              <div class="response-content">{{ testPromptForm.response }}</div>
              <el-button size="small" @click="copyToClipboard(testPromptForm.response)">Copy</el-button>
            </div>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="testPromptVisible = false">Close</el-button>
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
.prompt-management-container {
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

.usage-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.success-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.response-icon {
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

.category-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.category-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 40px;
  font-size: 13px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s ease;
}

.category-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.category-chip.active {
  background: #409eff;
  border-color: #409eff;
  color: white;
}

.chip-icon {
  font-size: 14px;
}

.filters-right {
  display: flex;
  gap: 12px;
}

/* Prompts Grid */
.prompts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.prompt-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
}

.prompt-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.prompt-card.active {
  border-left: 4px solid #67c23a;
}

.prompt-card.draft {
  border-left: 4px solid #e6a23c;
}

.prompt-card.deprecated {
  border-left: 4px solid #909399;
}

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 0 20px;
}

.prompt-category {
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

.prompt-name {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.prompt-description {
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

.template-preview {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 12px;
}

.template-label {
  font-size: 11px;
  color: #909399;
  margin-bottom: 4px;
}

.template-text {
  font-size: 12px;
  color: #606266;
  font-family: monospace;
  line-height: 1.4;
}

.meta-info {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  flex-wrap: wrap;
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

.last-updated {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
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

.created-by {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
}

.card-actions {
  display: flex;
  gap: 6px;
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

/* Dialog Styles */
.template-full {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.template-full pre {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 8px;
  font-family: monospace;
  font-size: 12px;
  white-space: pre-wrap;
  margin: 0;
}

.test-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.test-prompt-info {
  margin-bottom: 8px;
}

.test-response {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 8px;
  position: relative;
}

.response-content {
  font-size: 13px;
  line-height: 1.5;
  margin-bottom: 10px;
  white-space: pre-wrap;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .prompts-grid {
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  }
}

@media (max-width: 768px) {
  .prompt-management-container {
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

  .category-filters {
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

  .prompts-grid {
    grid-template-columns: 1fr;
  }

  .card-footer {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }

  .card-actions {
    justify-content: center;
    width: 100%;
  }

  .meta-info {
    flex-direction: column;
    gap: 8px;
  }
}
</style>