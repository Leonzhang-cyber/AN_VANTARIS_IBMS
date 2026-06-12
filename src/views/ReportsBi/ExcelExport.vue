<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Search, Refresh, Document, Download, Printer,
  Share, Star, Clock, Warning, CircleCheck,
  TrendCharts, DataLine, Calendar, Setting,
  Plus, Upload, Filter, ArrowUp, ArrowDown,
  View, User, Trophy, Medal, Edit, Delete,
  CopyDocument, Files, Lock, Unlock,
  Check, Close, EditPen, MagicStick
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Loading report templates...',
  'Loading layout configurations...',
  'Preparing style options...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedCategory = ref('all')
const selectedStatus = ref('all')
const templateDetailsVisible = ref(false)
const createTemplateVisible = ref(false)
const editTemplateVisible = ref(false)
const previewVisible = ref(false)
const chartRef = ref(null)

let usageChart: echarts.ECharts | null = null

// Template categories
const templateCategories = [
  { value: 'all', label: 'All Templates', icon: '📋' },
  { value: 'dashboard', label: 'Dashboards', icon: '📊' },
  { value: 'report', label: 'Reports', icon: '📄' },
  { value: 'analysis', label: 'Analysis', icon: '🔍' },
  { value: 'summary', label: 'Summaries', icon: '📝' }
]

// Status filters
const statusOptions = [
  { value: 'all', label: 'All' },
  { value: 'published', label: 'Published' },
  { value: 'draft', label: 'Draft' },
  { value: 'archived', label: 'Archived' }
]

// Report templates data
const templates = ref([
  {
    id: 'TPL001', name: 'Executive Dashboard Template', category: 'dashboard',
    description: 'Professional dashboard template for executive-level reporting with KPIs and trends',
    createdBy: 'admin@system.com', createdAt: '2024-01-10', lastModified: '2024-01-15',
    usageCount: 234, status: 'published', isPublic: true, version: '2.1.0',
    sections: ['Header', 'KPI Cards', 'Trend Chart', 'Data Table', 'Footer'],
    previewImage: 'dashboard-preview.png'
  },
  {
    id: 'TPL002', name: 'Energy Report Template', category: 'report',
    description: 'Comprehensive energy consumption report template with charts and analysis',
    createdBy: 'energy@system.com', createdAt: '2024-01-08', lastModified: '2024-01-14',
    usageCount: 156, status: 'published', isPublic: true, version: '1.8.0',
    sections: ['Header', 'Energy Overview', 'Consumption Chart', 'Cost Analysis', 'Recommendations'],
    previewImage: 'energy-preview.png'
  },
  {
    id: 'TPL003', name: 'Financial Summary Template', category: 'summary',
    description: 'Financial summary template with P&L, balance sheet, and cash flow sections',
    createdBy: 'finance@system.com', createdAt: '2024-01-05', lastModified: '2024-01-12',
    usageCount: 189, status: 'published', isPublic: false, version: '3.0.0',
    sections: ['Header', 'Executive Summary', 'P&L Statement', 'Balance Sheet', 'Cash Flow', 'Notes'],
    previewImage: 'financial-preview.png'
  },
  {
    id: 'TPL004', name: 'Alarms Analysis Template', category: 'analysis',
    description: 'Template for analyzing alarms and incidents with severity breakdown',
    createdBy: 'security@system.com', createdAt: '2024-01-03', lastModified: '2024-01-11',
    usageCount: 98, status: 'draft', isPublic: true, version: '1.2.0',
    sections: ['Header', 'Alarms Overview', 'Severity Chart', 'Trend Analysis', 'Action Items'],
    previewImage: 'alarms-preview.png'
  },
  {
    id: 'TPL005', name: 'Maintenance Dashboard', category: 'dashboard',
    description: 'Maintenance performance dashboard with work order tracking and SLA compliance',
    createdBy: 'maintenance@system.com', createdAt: '2024-01-01', lastModified: '2024-01-10',
    usageCount: 145, status: 'published', isPublic: true, version: '2.0.0',
    sections: ['Header', 'Work Order Stats', 'SLA Compliance', 'Resource Utilization', 'Pending Tasks'],
    previewImage: 'maintenance-preview.png'
  },
  {
    id: 'TPL006', name: 'Sustainability Report', category: 'report',
    description: 'Environmental sustainability report template with carbon footprint metrics',
    createdBy: 'sustainability@system.com', createdAt: '2023-12-28', lastModified: '2024-01-08',
    usageCount: 67, status: 'published', isPublic: false, version: '1.5.0',
    sections: ['Header', 'Carbon Footprint', 'Energy Usage', 'Water Conservation', 'Waste Management'],
    previewImage: 'sustainability-preview.png'
  },
  {
    id: 'TPL007', name: 'Sales Performance Template', category: 'dashboard',
    description: 'Sales dashboard template with pipeline, quota attainment, and revenue tracking',
    createdBy: 'sales@system.com', createdAt: '2023-12-20', lastModified: '2024-01-05',
    usageCount: 234, status: 'published', isPublic: true, version: '2.2.0',
    sections: ['Header', 'Revenue Overview', 'Pipeline Funnel', 'Quota Attainment', 'Top Performers'],
    previewImage: 'sales-preview.png'
  },
  {
    id: 'TPL008', name: 'Operations Summary', category: 'summary',
    description: 'Daily operations summary template for shift handover and reporting',
    createdBy: 'ops@system.com', createdAt: '2023-12-15', lastModified: '2024-01-03',
    usageCount: 156, status: 'archived', isPublic: true, version: '1.0.0',
    sections: ['Header', 'Shift Summary', 'Key Events', 'Outstanding Issues', 'Action Plan'],
    previewImage: 'ops-preview.png'
  }
])

// Template statistics
const templateStats = reactive({
  total: 0,
  published: 0,
  draft: 0,
  archived: 0,
  public: 0,
  private: 0,
  dashboard: 0,
  report: 0,
  analysis: 0,
  summary: 0,
  totalUsage: 0,
  avgUsage: 0
})

// New template form
const newTemplateForm = reactive({
  name: '',
  category: 'dashboard',
  description: '',
  isPublic: true,
  sections: [] as string[],
  version: '1.0.0'
})

// Edit template form
const editTemplateForm = reactive({
  id: '',
  name: '',
  category: '',
  description: '',
  isPublic: true,
  status: '',
  sections: [] as string[],
  version: ''
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
        t.description.toLowerCase().includes(searchKeyword.value.toLowerCase())
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

// Available sections
const availableSections = [
  'Header', 'Footer', 'Executive Summary', 'KPI Cards', 'Trend Chart',
  'Data Table', 'Pie Chart', 'Bar Chart', 'Line Chart', 'Gauge Chart',
  'Heat Map', 'Geography Map', 'Filters Panel', 'Export Button', 'Share Button'
]

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
    legend: { data: ['Usage Count'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: templates.value.map(t => t.name.substring(0, 15)), axisLabel: { rotate: 30, interval: 0 } },
    yAxis: { type: 'value', name: 'Usage Count' },
    series: [
      { name: 'Usage Count', type: 'bar', data: templates.value.map(t => t.usageCount), itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top' } }
    ]
  })
}

const updateStats = () => {
  templateStats.total = templates.value.length
  templateStats.published = templates.value.filter(t => t.status === 'published').length
  templateStats.draft = templates.value.filter(t => t.status === 'draft').length
  templateStats.archived = templates.value.filter(t => t.status === 'archived').length
  templateStats.public = templates.value.filter(t => t.isPublic).length
  templateStats.private = templates.value.filter(t => !t.isPublic).length
  templateStats.dashboard = templates.value.filter(t => t.category === 'dashboard').length
  templateStats.report = templates.value.filter(t => t.category === 'report').length
  templateStats.analysis = templates.value.filter(t => t.category === 'analysis').length
  templateStats.summary = templates.value.filter(t => t.category === 'summary').length
  templateStats.totalUsage = templates.value.reduce((sum, t) => sum + t.usageCount, 0)
  templateStats.avgUsage = Math.round(templateStats.totalUsage / templateStats.total)
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
  ElMessage.success('Templates refreshed successfully')
}

const viewTemplate = (template: any) => {
  selectedTemplate.value = template
  templateDetailsVisible.value = true
}

const editTemplate = (template: any) => {
  editTemplateForm.id = template.id
  editTemplateForm.name = template.name
  editTemplateForm.category = template.category
  editTemplateForm.description = template.description
  editTemplateForm.isPublic = template.isPublic
  editTemplateForm.status = template.status
  editTemplateForm.sections = [...template.sections]
  editTemplateForm.version = template.version
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
      description: editTemplateForm.description,
      isPublic: editTemplateForm.isPublic,
      status: editTemplateForm.status,
      sections: editTemplateForm.sections,
      version: editTemplateForm.version,
      lastModified: new Date().toISOString().split('T')[0]
    }
  }

  updateStats()
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
    createdBy: 'current@user.com',
    createdAt: new Date().toISOString().split('T')[0],
    lastModified: new Date().toISOString().split('T')[0],
    usageCount: 0,
    status: 'draft'
  }

  templates.value.unshift(newTemplate)
  updateStats()
  initChart()
  ElMessage.success(`Template duplicated successfully`)
}

const useTemplate = (template: any) => {
  template.usageCount++
  updateStats()
  ElMessage.success(`Template "${template.name}" applied successfully`)
}

const openCreateTemplate = () => {
  newTemplateForm.name = ''
  newTemplateForm.category = 'dashboard'
  newTemplateForm.description = ''
  newTemplateForm.isPublic = true
  newTemplateForm.sections = []
  newTemplateForm.version = '1.0.0'
  createTemplateVisible.value = true
}

const createTemplate = async () => {
  if (!newTemplateForm.name) {
    ElMessage.warning('Please enter a template name')
    return
  }

  if (newTemplateForm.sections.length === 0) {
    ElMessage.warning('Please select at least one section')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1000))

  const newTemplate = {
    id: `TPL${String(templates.value.length + 1).padStart(3, '0')}`,
    name: newTemplateForm.name,
    category: newTemplateForm.category,
    description: newTemplateForm.description || 'New template',
    createdBy: 'current@user.com',
    createdAt: new Date().toISOString().split('T')[0],
    lastModified: new Date().toISOString().split('T')[0],
    usageCount: 0,
    status: 'draft',
    isPublic: newTemplateForm.isPublic,
    sections: newTemplateForm.sections,
    version: newTemplateForm.version,
    previewImage: null
  }

  templates.value.unshift(newTemplate)
  updateStats()
  initChart()
  createTemplateVisible.value = false
  ElMessage.success('Template created successfully')
}

const previewTemplate = (template: any) => {
  selectedTemplate.value = template
  previewVisible.value = true
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getCategoryIcon = (category: string) => {
  switch (category) {
    case 'dashboard': return '📊'
    case 'report': return '📄'
    case 'analysis': return '🔍'
    case 'summary': return '📝'
    default: return '📋'
  }
}

const getCategoryColor = (category: string) => {
  switch (category) {
    case 'dashboard': return '#409EFF'
    case 'report': return '#67C23A'
    case 'analysis': return '#9B59B6'
    case 'summary': return '#E6A23C'
    default: return '#909399'
  }
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'published': return '#67C23A'
    case 'draft': return '#E6A23C'
    case 'archived': return '#909399'
    default: return '#909399'
  }
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
          <span class="loading-title">Loading Report Templates</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Report Governance - Report Templates</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="report-templates-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Report Templates</h1>
        <p class="page-subtitle">Manage and customize report templates for consistent branding</p>
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
          <el-icon><Files /></el-icon>
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
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ templateStats.totalUsage.toLocaleString() }}</div>
          <div class="stat-label">Total Usage</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ templateStats.avgUsage }} avg per template</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon public-icon">
          <el-icon><Unlock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ templateStats.public }}</div>
          <div class="stat-label">Public Templates</div>
        </div>
        <div class="stat-trend">
          <span class="trend-neutral">{{ templateStats.private }} Private</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon draft-icon">
          <el-icon><EditPen /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ templateStats.draft }}</div>
          <div class="stat-label">In Progress</div>
        </div>
        <div class="stat-trend">
          <span class="trend-neutral">{{ templateStats.archived }} Archived</span>
        </div>
      </div>
    </div>

    <!-- Stats Breakdown Row -->
    <div class="stats-breakdown">
      <div class="breakdown-item">
        <span class="breakdown-label">Dashboards</span>
        <span class="breakdown-value">{{ templateStats.dashboard }}</span>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: (templateStats.dashboard / templateStats.total) * 100 + '%', background: '#409EFF' }"></div>
        </div>
      </div>
      <div class="breakdown-item">
        <span class="breakdown-label">Reports</span>
        <span class="breakdown-value">{{ templateStats.report }}</span>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: (templateStats.report / templateStats.total) * 100 + '%', background: '#67C23A' }"></div>
        </div>
      </div>
      <div class="breakdown-item">
        <span class="breakdown-label">Analysis</span>
        <span class="breakdown-value">{{ templateStats.analysis }}</span>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: (templateStats.analysis / templateStats.total) * 100 + '%', background: '#9B59B6' }"></div>
        </div>
      </div>
      <div class="breakdown-item">
        <span class="breakdown-label">Summaries</span>
        <span class="breakdown-value">{{ templateStats.summary }}</span>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: (templateStats.summary / templateStats.total) * 100 + '%', background: '#E6A23C' }"></div>
        </div>
      </div>
    </div>

    <!-- Chart Section -->
    <div class="chart-section">
      <div class="section-header">
        <h3>Template Usage Statistics</h3>
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
              style="width: 260px"
          />
        </div>
        <div class="category-filters">
          <button
              v-for="cat in templateCategories"
              :key="cat.value"
              class="category-chip"
              :class="{ active: selectedCategory === cat.value }"
              @click="selectedCategory = cat.value"
          >
            <span class="chip-icon">{{ cat.icon }}</span>
            <span>{{ cat.label }}</span>
          </button>
        </div>
      </div>
      <div class="filters-right">
        <el-select v-model="selectedStatus" placeholder="Status" clearable style="width: 140px">
          <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
        </el-select>
      </div>
    </div>

    <!-- Templates Grid - Card Style -->
    <div class="templates-grid">
      <div
          v-for="template in filteredTemplates"
          :key="template.id"
          class="template-card"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="card-category" :style="{ background: getCategoryColor(template.category) }">
            <span class="category-icon">{{ getCategoryIcon(template.category) }}</span>
          </div>
          <div class="card-badges">
            <span class="version-badge">v{{ template.version }}</span>
            <span v-if="template.isPublic" class="public-badge">Public</span>
            <span v-else class="private-badge">Private</span>
          </div>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <h4 class="card-title">{{ template.name }}</h4>
          <p class="card-description">{{ template.description }}</p>

          <!-- Sections -->
          <div class="sections-section">
            <div class="section-label">Sections</div>
            <div class="sections-list">
              <span v-for="section in template.sections.slice(0, 4)" :key="section" class="section-tag">
                {{ section }}
              </span>
              <span v-if="template.sections.length > 4" class="section-more">+{{ template.sections.length - 4 }}</span>
            </div>
          </div>

          <!-- Meta Info -->
          <div class="template-meta">
            <div class="meta-item">
              <el-icon><User /></el-icon>
              <span>{{ template.createdBy?.split('@')[0] }}</span>
            </div>
            <div class="meta-item">
              <el-icon><Calendar /></el-icon>
              <span>{{ template.lastModified }}</span>
            </div>
            <div class="meta-item">
              <el-icon><TrendCharts /></el-icon>
              <span>{{ template.usageCount }} uses</span>
            </div>
          </div>

          <!-- Status -->
          <div class="template-status">
            <el-tag :type="template.status === 'published' ? 'success' : template.status === 'draft' ? 'warning' : 'info'" size="small">
              {{ template.status.toUpperCase() }}
            </el-tag>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="card-actions">
            <el-button size="small" type="primary" @click="useTemplate(template)">
              Use Template
            </el-button>
            <el-button size="small" @click="previewTemplate(template)">
              Preview
            </el-button>
            <el-button size="small" @click="editTemplate(template)">
              Edit
            </el-button>
            <el-button size="small" @click="duplicateTemplate(template)">
              Duplicate
            </el-button>
            <el-button size="small" type="danger" @click="deleteTemplate(template)">
              Delete
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredTemplates.length === 0" class="empty-state">
      <el-empty description="No templates found">
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
    <el-dialog v-model="templateDetailsVisible" :title="selectedTemplate?.name" width="650px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Template ID">{{ selectedTemplate?.id }}</el-descriptions-item>
        <el-descriptions-item label="Version">{{ selectedTemplate?.version }}</el-descriptions-item>
        <el-descriptions-item label="Category">
          <el-tag :type="selectedTemplate?.category === 'dashboard' ? 'primary' : 'success'" size="small">
            {{ selectedTemplate?.category?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="selectedTemplate?.status === 'published' ? 'success' : 'warning'" size="small">
            {{ selectedTemplate?.status?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Visibility">
          <el-tag :type="selectedTemplate?.isPublic ? 'success' : 'info'" size="small">
            {{ selectedTemplate?.isPublic ? 'Public' : 'Private' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Usage Count">{{ selectedTemplate?.usageCount }}</el-descriptions-item>
        <el-descriptions-item label="Created By">{{ selectedTemplate?.createdBy }}</el-descriptions-item>
        <el-descriptions-item label="Created At">{{ selectedTemplate?.createdAt }}</el-descriptions-item>
        <el-descriptions-item label="Last Modified">{{ selectedTemplate?.lastModified }}</el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedTemplate?.description }}</el-descriptions-item>
        <el-descriptions-item label="Sections" :span="2">
          <div class="sections-list">
            <el-tag v-for="s in selectedTemplate?.sections" :key="s" size="small" style="margin: 2px">
              {{ s }}
            </el-tag>
          </div>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="templateDetailsVisible = false">Close</el-button>
        <el-button type="primary" @click="useTemplate(selectedTemplate)">Use Template</el-button>
      </template>
    </el-dialog>

    <!-- Create Template Dialog -->
    <el-dialog v-model="createTemplateVisible" title="Create Template" width="550px">
      <el-form :model="newTemplateForm" label-width="120px">
        <el-form-item label="Template Name" required>
          <el-input v-model="newTemplateForm.name" placeholder="Enter template name" />
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="newTemplateForm.category" style="width: 100%">
            <el-option v-for="c in templateCategories.slice(1)" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="newTemplateForm.description" type="textarea" rows="2" placeholder="Enter description" />
        </el-form-item>
        <el-form-item label="Visibility">
          <el-radio-group v-model="newTemplateForm.isPublic">
            <el-radio :label="true">Public</el-radio>
            <el-radio :label="false">Private</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Version">
          <el-input v-model="newTemplateForm.version" placeholder="1.0.0" />
        </el-form-item>
        <el-form-item label="Sections" required>
          <el-select v-model="newTemplateForm.sections" multiple filterable style="width: 100%">
            <el-option v-for="s in availableSections" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createTemplateVisible = false">Cancel</el-button>
        <el-button type="primary" @click="createTemplate">Create Template</el-button>
      </template>
    </el-dialog>

    <!-- Edit Template Dialog -->
    <el-dialog v-model="editTemplateVisible" title="Edit Template" width="550px">
      <el-form :model="editTemplateForm" label-width="120px">
        <el-form-item label="Template Name" required>
          <el-input v-model="editTemplateForm.name" placeholder="Enter template name" />
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="editTemplateForm.category" style="width: 100%">
            <el-option v-for="c in templateCategories.slice(1)" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="editTemplateForm.description" type="textarea" rows="2" placeholder="Enter description" />
        </el-form-item>
        <el-form-item label="Status">
          <el-select v-model="editTemplateForm.status" style="width: 100%">
            <el-option label="Published" value="published" />
            <el-option label="Draft" value="draft" />
            <el-option label="Archived" value="archived" />
          </el-select>
        </el-form-item>
        <el-form-item label="Visibility">
          <el-radio-group v-model="editTemplateForm.isPublic">
            <el-radio :label="true">Public</el-radio>
            <el-radio :label="false">Private</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Version">
          <el-input v-model="editTemplateForm.version" placeholder="1.0.0" />
        </el-form-item>
        <el-form-item label="Sections" required>
          <el-select v-model="editTemplateForm.sections" multiple filterable style="width: 100%">
            <el-option v-for="s in availableSections" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editTemplateVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveTemplateEdit">Save Changes</el-button>
      </template>
    </el-dialog>

    <!-- Preview Dialog -->
    <el-dialog v-model="previewVisible" :title="selectedTemplate?.name" width="800px" top="5vh">
      <div class="preview-container">
        <div class="preview-header">
          <div class="preview-meta">
            <span><el-icon><Files /></el-icon> {{ selectedTemplate?.category?.toUpperCase() }}</span>
            <span><el-icon><Document /></el-icon> v{{ selectedTemplate?.version }}</span>
            <span><el-icon><User /></el-icon> {{ selectedTemplate?.createdBy?.split('@')[0] }}</span>
          </div>
          <div class="preview-layout">
            <div class="layout-preview">
              <div class="layout-header">
                <div class="header-placeholder">Report Header</div>
              </div>
              <div class="layout-sections">
                <div v-for="section in selectedTemplate?.sections" :key="section" class="section-placeholder">
                  {{ section }}
                </div>
              </div>
              <div class="layout-footer">
                <div class="footer-placeholder">Report Footer</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="previewVisible = false">Close</el-button>
        <el-button type="primary" @click="useTemplate(selectedTemplate)">Use Template</el-button>
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
.report-templates-container {
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
  margin-bottom: 20px;
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

.public-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.draft-icon {
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
}

.trend-up {
  font-size: 11px;
  color: #67c23a;
  background: #f0f9ff;
  padding: 4px 8px;
  border-radius: 20px;
}

.trend-neutral {
  font-size: 11px;
  color: #909399;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 20px;
}

/* Stats Breakdown */
.stats-breakdown {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.breakdown-item {
  background: white;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.breakdown-label {
  font-size: 12px;
  color: #909399;
  display: block;
  margin-bottom: 8px;
}

.breakdown-value {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  display: block;
  margin-bottom: 12px;
}

.breakdown-bar {
  height: 6px;
  background: #e4e7ed;
  border-radius: 3px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
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

/* Templates Grid */
.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
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

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 0 20px;
}

.card-category {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.card-badges {
  display: flex;
  gap: 8px;
}

.version-badge {
  padding: 4px 10px;
  background: #f5f7fa;
  border-radius: 12px;
  font-size: 11px;
  color: #606266;
}

.public-badge {
  padding: 4px 10px;
  background: #f0f9ff;
  border-radius: 12px;
  font-size: 11px;
  color: #67c23a;
}

.private-badge {
  padding: 4px 10px;
  background: #fef0f0;
  border-radius: 12px;
  font-size: 11px;
  color: #f56c6c;
}

/* Card Body */
.card-body {
  padding: 16px 20px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 10px 0;
  line-height: 1.4;
}

.card-description {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.sections-section {
  margin-bottom: 16px;
}

.section-label {
  font-size: 11px;
  color: #909399;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sections-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.section-tag {
  font-size: 11px;
  padding: 3px 8px;
  background: #f0f9ff;
  color: #409eff;
  border-radius: 12px;
}

.section-more {
  font-size: 11px;
  padding: 3px 8px;
  background: #f5f7fa;
  color: #909399;
  border-radius: 12px;
}

.template-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
}

.template-status {
  position: absolute;
  top: 16px;
  right: 20px;
}

/* Card Footer */
.card-footer {
  padding: 16px 20px;
  border-top: 1px solid #f0f0f0;
  background: #fafbfc;
}

.card-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.card-actions .el-button {
  flex: 1;
  min-width: 70px;
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

/* Preview Dialog */
.preview-container {
  max-height: 60vh;
  overflow-y: auto;
}

.preview-header {
  margin-bottom: 20px;
}

.preview-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  font-size: 12px;
  color: #909399;
}

.preview-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.layout-preview {
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  overflow: hidden;
}

.layout-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  text-align: center;
}

.header-placeholder {
  color: white;
  font-weight: 500;
}

.layout-sections {
  padding: 16px;
  background: #fafbfc;
}

.section-placeholder {
  padding: 12px;
  margin-bottom: 8px;
  background: white;
  border: 1px dashed #e4e7ed;
  border-radius: 8px;
  text-align: center;
  font-size: 13px;
  color: #606266;
}

.section-placeholder:last-child {
  margin-bottom: 0;
}

.layout-footer {
  background: #f5f7fa;
  padding: 16px;
  text-align: center;
  border-top: 1px solid #e4e7ed;
}

.footer-placeholder {
  color: #909399;
  font-size: 12px;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-breakdown {
    grid-template-columns: repeat(2, 1fr);
  }

  .templates-grid {
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  }
}

@media (max-width: 768px) {
  .report-templates-container {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stats-breakdown {
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

  .templates-grid {
    grid-template-columns: 1fr;
  }

  .card-actions {
    flex-direction: column;
  }

  .card-actions .el-button {
    width: 100%;
  }
}
</style>