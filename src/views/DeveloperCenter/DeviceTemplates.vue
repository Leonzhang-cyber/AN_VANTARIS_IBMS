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
  'Initializing device template registry...',
  'Loading template definitions...',
  'Checking compatibility...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedCategory = ref('all')
const selectedStatus = ref('all')
const detailsVisible = ref(false)
const createTemplateVisible = ref(false)
const editTemplateVisible = ref(false)
const chartRef = ref(null)

let usageChart: echarts.ECharts | null = null

// Category filters
const categoryOptions = [
  { value: 'all', label: 'All Categories' },
  { value: 'hvac', label: 'HVAC', color: '#409EFF' },
  { value: 'electrical', label: 'Electrical', color: '#67C23A' },
  { value: 'lighting', label: 'Lighting', color: '#E6A23C' },
  { value: 'security', label: 'Security', color: '#F56C6C' },
  { value: 'sensor', label: 'Sensors', color: '#9B59B6' }
]

// Status filters
const statusOptions = [
  { value: 'all', label: 'All Status' },
  { value: 'published', label: 'Published', color: '#67C23A' },
  { value: 'draft', label: 'Draft', color: '#E6A23C' },
  { value: 'deprecated', label: 'Deprecated', color: '#909399' }
]

// Device templates data
const templates = ref([
  {
    id: 'TPL001', name: 'BACnet AHU Controller', category: 'hvac', version: '2.0',
    status: 'published', manufacturer: 'Siemens', model: 'PXC4.ED16',
    description: 'Template for BACnet-based Air Handling Unit controller',
    points: ['Supply Air Temp', 'Return Air Temp', 'Fan Speed', 'Valve Position', 'Filter Status'],
    protocols: ['BACnet/IP', 'BACnet MS/TP'],
    usageCount: 245, rating: 4.8, lastUpdated: '2024-01-15',
    createdBy: 'HVAC Team'
  },
  {
    id: 'TPL002', name: 'Modbus Power Meter', category: 'electrical', version: '3.1',
    status: 'published', manufacturer: 'Schneider', model: 'PM8000',
    description: 'Template for Modbus power meter with energy monitoring',
    points: ['Voltage L1-L3', 'Current L1-L3', 'Power Factor', 'Active Power', 'Energy Total'],
    protocols: ['Modbus TCP', 'Modbus RTU'],
    usageCount: 189, rating: 4.9, lastUpdated: '2024-01-14',
    createdBy: 'Electrical Team'
  },
  {
    id: 'TPL003', name: 'DALI Lighting Controller', category: 'lighting', version: '1.5',
    status: 'published', manufacturer: 'Philips', model: 'DALI-2',
    description: 'Template for DALI lighting control systems',
    points: ['Brightness', 'Color Temp', 'Scene Control', 'Power Status', 'Lamp Hours'],
    protocols: ['DALI', 'DALI-2'],
    usageCount: 156, rating: 4.7, lastUpdated: '2024-01-13',
    createdBy: 'Lighting Team'
  },
  {
    id: 'TPL004', name: 'IP Camera Template', category: 'security', version: '2.2',
    status: 'published', manufacturer: 'Hikvision', model: 'DS-2CD2xxx',
    description: 'Template for ONVIF-compliant IP cameras',
    points: ['Video Stream', 'Motion Detection', 'PTZ Control', 'Recording Status', 'SD Card Usage'],
    protocols: ['ONVIF', 'RTSP'],
    usageCount: 312, rating: 4.6, lastUpdated: '2024-01-12',
    createdBy: 'Security Team'
  },
  {
    id: 'TPL005', name: 'Temperature/Humidity Sensor', category: 'sensor', version: '1.0',
    status: 'published', manufacturer: 'Sensirion', model: 'SHT30',
    description: 'Template for environmental sensors',
    points: ['Temperature', 'Humidity', 'Dew Point', 'Battery Level', 'Signal Strength'],
    protocols: ['MQTT', 'Modbus'],
    usageCount: 278, rating: 4.8, lastUpdated: '2024-01-11',
    createdBy: 'Sensor Team'
  },
  {
    id: 'TPL006', name: 'VFD Pump Controller', category: 'hvac', version: '2.0',
    status: 'draft', manufacturer: 'ABB', model: 'ACH580',
    description: 'Template for variable frequency drive pump control',
    points: ['Speed Reference', 'Actual Speed', 'Current', 'Torque', 'Fault Code'],
    protocols: ['Modbus TCP', 'BACnet'],
    usageCount: 0, rating: 0, lastUpdated: '2024-01-10',
    createdBy: 'HVAC Team'
  },
  {
    id: 'TPL007', name: 'Access Control Reader', category: 'security', version: '1.2',
    status: 'published', manufacturer: 'HID', model: 'RP40',
    description: 'Template for access control card readers',
    points: ['Card UID', 'Access Granted', 'Door Status', 'Tamper Alert', 'Beeper Control'],
    protocols: ['Wiegand', 'OSDP'],
    usageCount: 134, rating: 4.5, lastUpdated: '2024-01-09',
    createdBy: 'Security Team'
  },
  {
    id: 'TPL008', name: 'CO2 Sensor Template', category: 'sensor', version: '1.1',
    status: 'deprecated', manufacturer: 'Senseair', model: 'S8',
    description: 'Deprecated - Use new S85 template instead',
    points: ['CO2 Level', 'Temperature', 'Humidity', 'ABC Logic Status'],
    protocols: ['Modbus', 'UART'],
    usageCount: 45, rating: 3.8, lastUpdated: '2024-01-08',
    createdBy: 'Sensor Team'
  }
])

// Template statistics
const templateStats = reactive({
  total: 0,
  published: 0,
  draft: 0,
  deprecated: 0,
  hvac: 0,
  electrical: 0,
  lighting: 0,
  security: 0,
  sensor: 0,
  totalUsage: 0,
  avgRating: 0
})

// Create template form
const createTemplateForm = reactive({
  name: '',
  category: 'hvac',
  manufacturer: '',
  model: '',
  description: '',
  protocols: [''],
  points: ['']
})

// Edit template form
const editTemplateForm = reactive({
  id: '',
  name: '',
  category: '',
  version: '',
  status: '',
  manufacturer: '',
  model: '',
  description: '',
  protocols: [] as string[],
  points: [] as string[]
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 8,
  total: templates.value.length
})

// Filtered templates
const filteredTemplates = computed(() => {
  let filtered = templates.value
  if (searchKeyword.value) {
    filtered = filtered.filter(t =>
        t.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        t.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        t.description.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        t.manufacturer.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedCategory.value !== 'all') {
    filtered = filtered.filter(t => t.category === selectedCategory.value)
  }
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(t => t.status === selectedStatus.value)
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
    legend: { data: ['Usage Count', 'Rating Score'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: templates.value.map(t => t.name.substring(0, 15)), axisLabel: { rotate: 30, interval: 0 } },
    yAxis: [
      { type: 'value', name: 'Usage Count' },
      { type: 'value', name: 'Rating', min: 0, max: 5 }
    ],
    series: [
      { name: 'Usage Count', type: 'bar', data: templates.value.map(t => t.usageCount), itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top' } },
      { name: 'Rating Score', type: 'line', data: templates.value.map(t => t.rating), smooth: true, lineStyle: { color: '#E6A23C', width: 2 }, symbol: 'circle', symbolSize: 8, yAxisIndex: 1 }
    ]
  })
}

const updateStats = () => {
  templateStats.total = templates.value.length
  templateStats.published = templates.value.filter(t => t.status === 'published').length
  templateStats.draft = templates.value.filter(t => t.status === 'draft').length
  templateStats.deprecated = templates.value.filter(t => t.status === 'deprecated').length
  templateStats.hvac = templates.value.filter(t => t.category === 'hvac').length
  templateStats.electrical = templates.value.filter(t => t.category === 'electrical').length
  templateStats.lighting = templates.value.filter(t => t.category === 'lighting').length
  templateStats.security = templates.value.filter(t => t.category === 'security').length
  templateStats.sensor = templates.value.filter(t => t.category === 'sensor').length
  templateStats.totalUsage = templates.value.reduce((sum, t) => sum + t.usageCount, 0)

  const ratedTemplates = templates.value.filter(t => t.rating > 0)
  if (ratedTemplates.length > 0) {
    templateStats.avgRating = parseFloat((ratedTemplates.reduce((sum, t) => sum + t.rating, 0) / ratedTemplates.length).toFixed(1))
  }
}

const handleResize = () => {
  usageChart?.resize()
}

// ==================== Template Functions ====================
const refreshTemplates = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  loading.value = false
  ElMessage.success('Device templates refreshed successfully')
}

const viewTemplateDetails = (template: any) => {
  selectedTemplate.value = template
  detailsVisible.value = true
}

const editTemplate = (template: any) => {
  editTemplateForm.id = template.id
  editTemplateForm.name = template.name
  editTemplateForm.category = template.category
  editTemplateForm.version = template.version
  editTemplateForm.status = template.status
  editTemplateForm.manufacturer = template.manufacturer
  editTemplateForm.model = template.model
  editTemplateForm.description = template.description
  editTemplateForm.protocols = [...template.protocols]
  editTemplateForm.points = [...template.points]
  editTemplateVisible.value = true
}

const saveTemplateEdit = async () => {
  if (!editTemplateForm.name) {
    ElMessage.warning('Please enter a template name')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1000))

  const index = templates.value.findIndex(t => t.id === editTemplateForm.id)
  if (index !== -1) {
    templates.value[index] = {
      ...templates.value[index],
      name: editTemplateForm.name,
      category: editTemplateForm.category,
      version: editTemplateForm.version,
      status: editTemplateForm.status,
      manufacturer: editTemplateForm.manufacturer,
      model: editTemplateForm.model,
      description: editTemplateForm.description,
      protocols: editTemplateForm.protocols.filter(p => p.trim()),
      points: editTemplateForm.points.filter(p => p.trim()),
      lastUpdated: new Date().toISOString().split('T')[0]
    }
  }

  updateStats()
  initChart()
  editTemplateVisible.value = false
  ElMessage.success('Template updated successfully')
}

const deleteTemplate = async (template: any) => {
  await ElMessageBox.confirm(
      `Delete template "${template.name}"? This action cannot be undone.`,
      'Confirm Delete',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'danger'
      }
  )

  const index = templates.value.findIndex(t => t.id === template.id)
  if (index !== -1) {
    templates.value.splice(index, 1)
  }

  updateStats()
  initChart()
  ElMessage.success('Template deleted successfully')
}

const duplicateTemplate = async (template: any) => {
  const newTemplate = {
    ...template,
    id: `TPL${String(templates.value.length + 1).padStart(3, '0')}`,
    name: `${template.name} (Copy)`,
    status: 'draft',
    usageCount: 0,
    rating: 0,
    lastUpdated: new Date().toISOString().split('T')[0]
  }

  templates.value.unshift(newTemplate)
  updateStats()
  initChart()
  ElMessage.success('Template duplicated successfully')
}

const openCreateTemplate = () => {
  createTemplateForm.name = ''
  createTemplateForm.category = 'hvac'
  createTemplateForm.manufacturer = ''
  createTemplateForm.model = ''
  createTemplateForm.description = ''
  createTemplateForm.protocols = ['']
  createTemplateForm.points = ['']
  createTemplateVisible.value = true
}

const addArrayItem = (array: string[]) => {
  array.push('')
}

const removeArrayItem = (array: string[], index: number) => {
  if (array.length > 1) {
    array.splice(index, 1)
  }
}

const createTemplate = async () => {
  if (!createTemplateForm.name) {
    ElMessage.warning('Please enter a template name')
    return
  }

  if (!createTemplateForm.manufacturer) {
    ElMessage.warning('Please enter a manufacturer')
    return
  }

  const protocols = createTemplateForm.protocols.filter(p => p.trim())
  const points = createTemplateForm.points.filter(p => p.trim())

  if (protocols.length === 0) {
    ElMessage.warning('Please add at least one protocol')
    return
  }

  if (points.length === 0) {
    ElMessage.warning('Please add at least one data point')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1000))

  const newTemplate = {
    id: `TPL${String(templates.value.length + 1).padStart(3, '0')}`,
    name: createTemplateForm.name,
    category: createTemplateForm.category,
    version: '1.0',
    status: 'draft',
    manufacturer: createTemplateForm.manufacturer,
    model: createTemplateForm.model || 'Generic',
    description: createTemplateForm.description || 'New device template',
    points,
    protocols,
    usageCount: 0,
    rating: 0,
    lastUpdated: new Date().toISOString().split('T')[0],
    createdBy: 'Current User'
  }

  templates.value.unshift(newTemplate)
  updateStats()
  initChart()
  createTemplateVisible.value = false
  ElMessage.success('Template created successfully')
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getCategoryColor = (category: string) => {
  switch (category) {
    case 'hvac': return '#409EFF'
    case 'electrical': return '#67C23A'
    case 'lighting': return '#E6A23C'
    case 'security': return '#F56C6C'
    case 'sensor': return '#9B59B6'
    default: return '#909399'
  }
}

const getCategoryIcon = (category: string) => {
  switch (category) {
    case 'hvac': return '❄️'
    case 'electrical': return '⚡'
    case 'lighting': return '💡'
    case 'security': return '🔒'
    case 'sensor': return '📡'
    default: return '🔧'
  }
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'published': return 'success'
    case 'draft': return 'warning'
    case 'deprecated': return 'info'
    default: return 'info'
  }
}

const getRatingStars = (rating: number) => {
  const fullStars = Math.floor(rating)
  const hasHalfStar = rating % 1 >= 0.5
  let stars = ''
  for (let i = 0; i < fullStars; i++) stars += '★'
  if (hasHalfStar) stars += '½'
  for (let i = stars.length; i < 5; i++) stars += '☆'
  return stars
}

const formatNumber = (num: number) => {
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const selectedTemplate = ref<any>(null)
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
          <span class="loading-title">Loading Device Templates</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Developer Center - Device Templates</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="device-templates-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Device Templates</h1>
        <p class="page-subtitle">Pre-configured device templates for quick device onboarding</p>
      </div>
      <div class="header-right">
        <el-button type="primary" size="large" @click="openCreateTemplate">
          <el-icon><Plus /></el-icon>
          Create Template
        </el-button>
        <el-button size="large" @click="refreshTemplates" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total-icon">
          <el-icon><Monitor /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ templateStats.total }}</div>
          <div class="stat-label">Total Templates</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ templateStats.published }} Published</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon usage-icon">
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ formatNumber(templateStats.totalUsage) }}</div>
          <div class="stat-label">Total Usage</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+28% this month</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon rating-icon">
          <el-icon><Star /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ templateStats.avgRating }}</div>
          <div class="stat-label">Avg Rating</div>
        </div>
        <div class="stat-trend">
          <el-progress :percentage="(templateStats.avgRating / 5) * 100" :stroke-width="4" :show-text="false" />
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon categories-icon">
          <el-icon><Tickets /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ categoryOptions.length - 1 }}</div>
          <div class="stat-label">Categories</div>
        </div>
        <div class="stat-trend">
          <span class="trend-neutral">{{ templateStats.draft }} Draft</span>
        </div>
      </div>
    </div>

    <!-- Usage Chart -->
    <div class="chart-section">
      <div class="section-header">
        <h3>Template Usage & Ratings</h3>
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
              placeholder="Search templates..."
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
            <span class="chip-dot" :style="{ background: c.color }"></span>
            <span>{{ c.label }}</span>
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

    <!-- Templates Grid -->
    <div class="templates-grid">
      <div
          v-for="template in filteredTemplates"
          :key="template.id"
          class="template-card"
          :class="template.status"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="template-category">
            <span class="category-icon">{{ getCategoryIcon(template.category) }}</span>
            <span class="category-name" :style="{ background: getCategoryColor(template.category) + '20', color: getCategoryColor(template.category) }">
              {{ template.category.toUpperCase() }}
            </span>
          </div>
          <div class="template-status">
            <el-tag :type="getStatusType(template.status)" size="small" effect="light">
              {{ template.status.toUpperCase() }}
            </el-tag>
          </div>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <h4 class="template-name">{{ template.name }}</h4>
          <p class="template-description">{{ template.description }}</p>

          <!-- Manufacturer & Model -->
          <div class="template-meta">
            <div class="meta-item">
              <span class="meta-label">Manufacturer:</span>
              <span class="meta-value">{{ template.manufacturer }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Model:</span>
              <span class="meta-value">{{ template.model }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Version:</span>
              <span class="meta-value">v{{ template.version }}</span>
            </div>
          </div>

          <!-- Protocols -->
          <div class="protocols-preview">
            <div class="protocols-label">Protocols:</div>
            <div class="protocols-list">
              <span v-for="proto in template.protocols.slice(0, 2)" :key="proto" class="protocol-tag">
                {{ proto }}
              </span>
              <span v-if="template.protocols.length > 2" class="more">+{{ template.protocols.length - 2 }}</span>
            </div>
          </div>

          <!-- Points Preview -->
          <div class="points-preview">
            <div class="points-label">Data Points:</div>
            <div class="points-list">
              <span v-for="point in template.points.slice(0, 3)" :key="point" class="point-tag">
                {{ point }}
              </span>
              <span v-if="template.points.length > 3" class="more">+{{ template.points.length - 3 }}</span>
            </div>
          </div>

          <!-- Stats -->
          <div class="template-stats">
            <div class="stat">
              <el-icon><DataLine /></el-icon>
              <span>{{ formatNumber(template.usageCount) }} uses</span>
            </div>
            <div class="stat">
              <el-icon><Star /></el-icon>
              <span>{{ getRatingStars(template.rating) }}</span>
            </div>
            <div class="stat">
              <el-icon><Clock /></el-icon>
              <span>{{ template.lastUpdated }}</span>
            </div>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="card-actions">
            <el-button size="small" @click="viewTemplateDetails(template)">
              <el-icon><Eye /></el-icon> Details
            </el-button>
            <el-button size="small" type="primary" @click="editTemplate(template)">
              <el-icon><Edit /></el-icon> Edit
            </el-button>
            <el-button size="small" @click="duplicateTemplate(template)">
              <el-icon><CopyDocument /></el-icon> Duplicate
            </el-button>
            <el-button size="small" type="danger" @click="deleteTemplate(template)">
              <el-icon><Delete /></el-icon> Delete
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredTemplates.length === 0" class="empty-state">
      <el-empty description="No device templates found">
        <el-button type="primary" @click="openCreateTemplate">Create Template</el-button>
      </el-empty>
    </div>

    <!-- Pagination -->
    <div v-if="filteredTemplates.length > 0" class="pagination-wrapper">
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

    <!-- Template Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="selectedTemplate?.name" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Template ID">{{ selectedTemplate?.id }}</el-descriptions-item>
        <el-descriptions-item label="Version">{{ selectedTemplate?.version }}</el-descriptions-item>
        <el-descriptions-item label="Category">{{ selectedTemplate?.category?.toUpperCase() }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusType(selectedTemplate?.status)" size="small">
            {{ selectedTemplate?.status?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Manufacturer">{{ selectedTemplate?.manufacturer }}</el-descriptions-item>
        <el-descriptions-item label="Model">{{ selectedTemplate?.model }}</el-descriptions-item>
        <el-descriptions-item label="Usage Count">{{ formatNumber(selectedTemplate?.usageCount) }}</el-descriptions-item>
        <el-descriptions-item label="Rating">{{ selectedTemplate?.rating }} ★</el-descriptions-item>
        <el-descriptions-item label="Last Updated">{{ selectedTemplate?.lastUpdated }}</el-descriptions-item>
        <el-descriptions-item label="Created By">{{ selectedTemplate?.createdBy }}</el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedTemplate?.description }}</el-descriptions-item>
        <el-descriptions-item label="Protocols" :span="2">
          <div class="protocols-list-detail">
            <el-tag v-for="p in selectedTemplate?.protocols" :key="p" size="small" style="margin: 2px">
              {{ p }}
            </el-tag>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="Data Points" :span="2">
          <div class="points-list-detail">
            <div v-for="point in selectedTemplate?.points" :key="point" class="point-item">• {{ point }}</div>
          </div>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
        <el-button type="primary" @click="editTemplate(selectedTemplate)">Edit Template</el-button>
      </template>
    </el-dialog>

    <!-- Create Template Dialog -->
    <el-dialog v-model="createTemplateVisible" title="Create Device Template" width="600px">
      <el-form :model="createTemplateForm" label-width="110px">
        <el-form-item label="Template Name" required>
          <el-input v-model="createTemplateForm.name" placeholder="Enter template name" />
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="createTemplateForm.category" style="width: 100%">
            <el-option v-for="c in categoryOptions.slice(1)" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Manufacturer" required>
          <el-input v-model="createTemplateForm.manufacturer" placeholder="Device manufacturer" />
        </el-form-item>
        <el-form-item label="Model">
          <el-input v-model="createTemplateForm.model" placeholder="Device model number" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="createTemplateForm.description" type="textarea" rows="2" placeholder="Template description" />
        </el-form-item>
        <el-form-item label="Protocols" required>
          <div v-for="(proto, idx) in createTemplateForm.protocols" :key="idx" class="array-item">
            <el-input v-model="createTemplateForm.protocols[idx]" placeholder="e.g., BACnet, Modbus" />
            <el-button type="danger" link @click="removeArrayItem(createTemplateForm.protocols, idx)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          <el-button type="primary" link @click="addArrayItem(createTemplateForm.protocols)">
            <el-icon><Plus /></el-icon> Add Protocol
          </el-button>
        </el-form-item>
        <el-form-item label="Data Points" required>
          <div v-for="(point, idx) in createTemplateForm.points" :key="idx" class="array-item">
            <el-input v-model="createTemplateForm.points[idx]" placeholder="Data point name" />
            <el-button type="danger" link @click="removeArrayItem(createTemplateForm.points, idx)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          <el-button type="primary" link @click="addArrayItem(createTemplateForm.points)">
            <el-icon><Plus /></el-icon> Add Data Point
          </el-button>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createTemplateVisible = false">Cancel</el-button>
        <el-button type="primary" @click="createTemplate">Create Template</el-button>
      </template>
    </el-dialog>

    <!-- Edit Template Dialog -->
    <el-dialog v-model="editTemplateVisible" title="Edit Device Template" width="600px">
      <el-form :model="editTemplateForm" label-width="110px">
        <el-form-item label="Template Name" required>
          <el-input v-model="editTemplateForm.name" placeholder="Enter template name" />
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="editTemplateForm.category" style="width: 100%">
            <el-option v-for="c in categoryOptions.slice(1)" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Version">
          <el-input v-model="editTemplateForm.version" placeholder="1.0" />
        </el-form-item>
        <el-form-item label="Status">
          <el-select v-model="editTemplateForm.status" style="width: 100%">
            <el-option label="Published" value="published" />
            <el-option label="Draft" value="draft" />
            <el-option label="Deprecated" value="deprecated" />
          </el-select>
        </el-form-item>
        <el-form-item label="Manufacturer">
          <el-input v-model="editTemplateForm.manufacturer" placeholder="Device manufacturer" />
        </el-form-item>
        <el-form-item label="Model">
          <el-input v-model="editTemplateForm.model" placeholder="Device model number" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="editTemplateForm.description" type="textarea" rows="2" placeholder="Template description" />
        </el-form-item>
        <el-form-item label="Protocols">
          <div v-for="(proto, idx) in editTemplateForm.protocols" :key="idx" class="array-item">
            <el-input v-model="editTemplateForm.protocols[idx]" placeholder="e.g., BACnet, Modbus" />
            <el-button type="danger" link @click="removeArrayItem(editTemplateForm.protocols, idx)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          <el-button type="primary" link @click="addArrayItem(editTemplateForm.protocols)">
            <el-icon><Plus /></el-icon> Add Protocol
          </el-button>
        </el-form-item>
        <el-form-item label="Data Points">
          <div v-for="(point, idx) in editTemplateForm.points" :key="idx" class="array-item">
            <el-input v-model="editTemplateForm.points[idx]" placeholder="Data point name" />
            <el-button type="danger" link @click="removeArrayItem(editTemplateForm.points, idx)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          <el-button type="primary" link @click="addArrayItem(editTemplateForm.points)">
            <el-icon><Plus /></el-icon> Add Data Point
          </el-button>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editTemplateVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveTemplateEdit">Save Changes</el-button>
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
.device-templates-container {
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

.rating-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.categories-icon {
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

.trend-neutral {
  color: #909399;
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
.status-filters {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.category-chip,
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

.category-chip:hover,
.status-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.category-chip.active,
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

/* Templates Grid */
.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.template-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
}

.template-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.template-card.published {
  border-left: 4px solid #67c23a;
}

.template-card.draft {
  border-left: 4px solid #e6a23c;
}

.template-card.deprecated {
  border-left: 4px solid #909399;
}

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 0 20px;
}

.template-category {
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
  padding: 4px 8px;
  border-radius: 12px;
}

/* Card Body */
.card-body {
  padding: 16px 20px;
}

.template-name {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 10px 0;
  line-height: 1.4;
}

.template-description {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.template-meta {
  display: flex;
  gap: 12px;
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

.protocols-preview,
.points-preview {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.protocols-label,
.points-label {
  font-size: 11px;
  color: #909399;
}

.protocols-list,
.points-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.protocol-tag,
.point-tag {
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

.template-stats {
  display: flex;
  gap: 16px;
  margin-top: 12px;
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

.protocols-list-detail {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.points-list-detail {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.point-item {
  font-size: 13px;
  color: #606266;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .templates-grid {
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  }
}

@media (max-width: 768px) {
  .device-templates-container {
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

  .templates-grid {
    grid-template-columns: 1fr;
  }

  .card-actions {
    flex-direction: column;
  }

  .card-actions .el-button {
    width: 100%;
  }

  .template-meta {
    flex-direction: column;
    gap: 4px;
  }
}
</style>