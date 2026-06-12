<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Search, Refresh, Document, Download, Printer,
  Share, Star, Clock, Warning, CircleCheck,
  TrendCharts, DataLine, Calendar, Setting,
  Plus, Upload, Filter, ArrowUp, ArrowDown,
  View, User, Trophy, Medal, Edit, Delete,
  CopyDocument,
  Lock, Unlock, Link
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Loading PDF export service...',
  'Preparing templates...',
  'Loading export history...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedFormat = ref('all')
const selectedStatus = ref('all')
const exportDialogVisible = ref(false)
const scheduledVisible = ref(false)
const historyVisible = ref(false)
const previewVisible = ref(false)
const chartRef = ref(null)

let exportChart: echarts.ECharts | null = null

// Format filters
const formatOptions = [
  { value: 'all', label: 'All Formats', icon: '📄' },
  { value: 'pdf', label: 'PDF', icon: '📕' },
  { value: 'excel', label: 'Excel', icon: '📗' },
  { value: 'image', label: 'Image', icon: '🖼️' },
  { value: 'csv', label: 'CSV', icon: '📊' }
]

// Status filters
const statusOptions = [
  { value: 'all', label: 'All' },
  { value: 'ready', label: 'Ready' },
  { value: 'processing', label: 'Processing' },
  { value: 'completed', label: 'Completed' },
  { value: 'failed', label: 'Failed' }
]

// PDF Export items
const exportItems = ref([
  {
    id: 'EXP001', name: 'Executive Dashboard Q1', format: 'pdf', size: '2.4 MB',
    pages: 12, createdBy: 'admin@system.com', createdAt: '2024-01-15 10:30:00',
    status: 'ready', downloads: 45, views: 128, scheduled: false,
    template: 'Executive Summary', description: 'Quarterly executive dashboard with key KPIs'
  },
  {
    id: 'EXP002', name: 'Energy Consumption Report', format: 'pdf', size: '3.1 MB',
    pages: 18, createdBy: 'energy@system.com', createdAt: '2024-01-14 14:20:00',
    status: 'ready', downloads: 32, views: 89, scheduled: false,
    template: 'Energy Analysis', description: 'Detailed energy consumption analysis by zone'
  },
  {
    id: 'EXP003', name: 'Financial Summary - January', format: 'excel', size: '1.8 MB',
    pages: 6, createdBy: 'finance@system.com', createdAt: '2024-01-13 09:15:00',
    status: 'ready', downloads: 67, views: 156, scheduled: true,
    template: 'Financial Report', description: 'Monthly financial summary with P&L'
  },
  {
    id: 'EXP004', name: 'Alarms Analysis Report', format: 'pdf', size: '4.2 MB',
    pages: 24, createdBy: 'security@system.com', createdAt: '2024-01-12 16:45:00',
    status: 'processing', downloads: 12, views: 45, scheduled: false,
    template: 'Alarms Analysis', description: 'Comprehensive alarms and incidents analysis'
  },
  {
    id: 'EXP005', name: 'Maintenance Dashboard', format: 'image', size: '0.8 MB',
    pages: 1, createdBy: 'maintenance@system.com', createdAt: '2024-01-11 11:30:00',
    status: 'completed', downloads: 89, views: 234, scheduled: true,
    template: 'Dashboard', description: 'Maintenance dashboard snapshot'
  },
  {
    id: 'EXP006', name: 'Sustainability Report', format: 'pdf', size: '5.6 MB',
    pages: 32, createdBy: 'sustainability@system.com', createdAt: '2024-01-10 13:00:00',
    status: 'failed', downloads: 8, views: 23, scheduled: false,
    template: 'Sustainability', description: 'Annual sustainability metrics report'
  },
  {
    id: 'EXP007', name: 'Performance Metrics', format: 'excel', size: '2.1 MB',
    pages: 8, createdBy: 'ops@system.com', createdAt: '2024-01-09 10:00:00',
    status: 'ready', downloads: 56, views: 145, scheduled: true,
    template: 'Performance', description: 'System performance metrics and KPIs'
  },
  {
    id: 'EXP008', name: 'Security Audit Log', format: 'csv', size: '0.5 MB',
    pages: 15, createdBy: 'audit@system.com', createdAt: '2024-01-08 15:30:00',
    status: 'completed', downloads: 34, views: 78, scheduled: false,
    template: 'Audit Log', description: 'Security audit log export'
  }
])

// Export statistics
const exportStats = reactive({
  total: 0,
  pdf: 0,
  excel: 0,
  image: 0,
  csv: 0,
  ready: 0,
  processing: 0,
  completed: 0,
  failed: 0,
  totalDownloads: 0,
  totalPages: 0
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 8,
  total: exportItems.value.length
})

// Filtered items
const filteredItems = computed(() => {
  let filtered = exportItems.value
  if (searchKeyword.value) {
    filtered = filtered.filter(i =>
        i.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        i.description.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        i.template.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedFormat.value !== 'all') {
    filtered = filtered.filter(i => i.format === selectedFormat.value)
  }
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(i => i.status === selectedStatus.value)
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

  exportChart = echarts.init(chartRef.value)
  exportChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Downloads', 'Views'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: exportItems.value.map(i => i.name.substring(0, 15)), axisLabel: { rotate: 30, interval: 0 } },
    yAxis: { type: 'value', name: 'Count' },
    series: [
      { name: 'Downloads', type: 'bar', data: exportItems.value.map(i => i.downloads), itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] } },
      { name: 'Views', type: 'line', data: exportItems.value.map(i => i.views), smooth: true, lineStyle: { color: '#67C23A', width: 2 }, symbol: 'circle', symbolSize: 8 }
    ]
  })
}

const updateStats = () => {
  exportStats.total = exportItems.value.length
  exportStats.pdf = exportItems.value.filter(i => i.format === 'pdf').length
  exportStats.excel = exportItems.value.filter(i => i.format === 'excel').length
  exportStats.image = exportItems.value.filter(i => i.format === 'image').length
  exportStats.csv = exportItems.value.filter(i => i.format === 'csv').length
  exportStats.ready = exportItems.value.filter(i => i.status === 'ready').length
  exportStats.processing = exportItems.value.filter(i => i.status === 'processing').length
  exportStats.completed = exportItems.value.filter(i => i.status === 'completed').length
  exportStats.failed = exportItems.value.filter(i => i.status === 'failed').length
  exportStats.totalDownloads = exportItems.value.reduce((sum, i) => sum + i.downloads, 0)
  exportStats.totalPages = exportItems.value.reduce((sum, i) => sum + i.pages, 0)
}

const handleResize = () => {
  exportChart?.resize()
}

// ==================== Export Functions ====================
const refreshExports = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  loading.value = false
  ElMessage.success('Export list refreshed successfully')
}

const downloadFile = async (item: any) => {
  ElMessage.info(`Downloading ${item.name}...`)
  await new Promise(resolve => setTimeout(resolve, 1000))
  item.downloads++
  updateStats()
  ElMessage.success(`${item.name} downloaded successfully`)
}

const previewFile = (item: any) => {
  selectedItem.value = item
  previewVisible.value = true
}

const shareFile = (item: any) => {
  ElMessage.success(`Share link generated for ${item.name}`)
}

const deleteFile = async (item: any) => {
  await ElMessageBox.confirm(
      `Delete "${item.name}"? This action cannot be undone.`,
      'Confirm Delete',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'danger'
      }
  )

  const index = exportItems.value.findIndex(i => i.id === item.id)
  if (index !== -1) {
    exportItems.value.splice(index, 1)
  }
  updateStats()
  initChart()
  ElMessage.success('File deleted successfully')
}

const openExportDialog = () => {
  exportDialogVisible.value = true
}

const openScheduleDialog = () => {
  scheduledVisible.value = true
}

const viewHistory = () => {
  historyVisible.value = true
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getFormatIcon = (format: string) => {
  switch (format) {
    case 'pdf': return Filter
    case 'excel': return Filter
    case 'image': return ArrowDown
    case 'csv': return Document
    default: return Document
  }
}

const getFormatColor = (format: string) => {
  switch (format) {
    case 'pdf': return '#F56C6C'
    case 'excel': return '#67C23A'
    case 'image': return '#409EFF'
    case 'csv': return '#E6A23C'
    default: return '#909399'
  }
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'ready': return '#67C23A'
    case 'processing': return '#E6A23C'
    case 'completed': return '#409EFF'
    case 'failed': return '#F56C6C'
    default: return '#909399'
  }
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'ready': return CircleCheck
    case 'processing': return CircleCheck
    case 'completed': return CircleCheck
    case 'failed': return Warning
    default: return Clock
  }
}

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const selectedItem = ref<any>(null)
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
          <span class="loading-title">Loading PDF Export</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Reports & BI - PDF Export</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="pdf-export-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">PDF Export</h1>
        <p class="page-subtitle">Export and manage your reports in various formats</p>
      </div>
      <div class="header-right">
        <el-button type="primary" size="large" @click="openExportDialog">
          <el-icon><Plus /></el-icon>
          New Export
        </el-button>
        <el-button size="large" @click="openScheduleDialog">
          <el-icon><Calendar /></el-icon>
          Schedule Export
        </el-button>
        <el-button size="large" @click="refreshExports" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total-icon">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ exportStats.total }}</div>
          <div class="stat-label">Total Exports</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ exportStats.ready }} Ready</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon pdf-icon">
          <el-icon><Filter /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ exportStats.pdf }}</div>
          <div class="stat-label">PDF Files</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ exportStats.excel }} Excel</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon downloads-icon">
          <el-icon><Download /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ exportStats.totalDownloads.toLocaleString() }}</div>
          <div class="stat-label">Total Downloads</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ exportStats.totalPages.toLocaleString() }} pages</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon scheduled-icon">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ exportItems.filter(i => i.scheduled).length }}</div>
          <div class="stat-label">Scheduled</div>
        </div>
        <div class="stat-trend">
          <span class="trend-neutral">{{ exportStats.completed }} Completed</span>
        </div>
      </div>
    </div>

    <!-- Stats Breakdown Row -->
    <div class="stats-breakdown">
      <div class="breakdown-item">
        <span class="breakdown-label">Ready</span>
        <span class="breakdown-value">{{ exportStats.ready }}</span>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: (exportStats.ready / exportStats.total) * 100 + '%', background: '#67C23A' }"></div>
        </div>
      </div>
      <div class="breakdown-item">
        <span class="breakdown-label">Processing</span>
        <span class="breakdown-value">{{ exportStats.processing }}</span>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: (exportStats.processing / exportStats.total) * 100 + '%', background: '#E6A23C' }"></div>
        </div>
      </div>
      <div class="breakdown-item">
        <span class="breakdown-label">Completed</span>
        <span class="breakdown-value">{{ exportStats.completed }}</span>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: (exportStats.completed / exportStats.total) * 100 + '%', background: '#409EFF' }"></div>
        </div>
      </div>
      <div class="breakdown-item">
        <span class="breakdown-label">Failed</span>
        <span class="breakdown-value">{{ exportStats.failed }}</span>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: (exportStats.failed / exportStats.total) * 100 + '%', background: '#F56C6C' }"></div>
        </div>
      </div>
    </div>

    <!-- Chart Section -->
    <div class="chart-section">
      <div class="section-header">
        <h3>Export Engagement Metrics</h3>
        <el-button text type="primary" @click="initChart">Refresh</el-button>
      </div>
      <div ref="chartRef" class="export-chart" style="height: 320px"></div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-bar">
      <div class="filters-left">
        <div class="search-box">
          <el-input
              v-model="searchKeyword"
              placeholder="Search exports..."
              :prefix-icon="Search"
              clearable
              style="width: 260px"
          />
        </div>
        <div class="format-filters">
          <button
              v-for="fmt in formatOptions"
              :key="fmt.value"
              class="format-chip"
              :class="{ active: selectedFormat === fmt.value }"
              @click="selectedFormat = fmt.value"
          >
            <span class="chip-icon">{{ fmt.icon }}</span>
            <span>{{ fmt.label }}</span>
          </button>
        </div>
      </div>
      <div class="filters-right">
        <el-select v-model="selectedStatus" placeholder="Status" clearable style="width: 140px">
          <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
        </el-select>
        <el-button @click="viewHistory">
          <el-icon><Link /></el-icon>
          History
        </el-button>
      </div>
    </div>

    <!-- Export Items Grid - Card Style -->
    <div class="exports-grid">
      <div
          v-for="item in filteredItems"
          :key="item.id"
          class="export-card"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="card-format" :style="{ background: getFormatColor(item.format) }">
            <el-icon><component :is="getFormatIcon(item.format)" /></el-icon>
          </div>
          <div class="card-status">
            <el-tag :type="item.status === 'ready' ? 'success' : item.status === 'processing' ? 'warning' : item.status === 'completed' ? 'info' : 'danger'" size="small">
              <el-icon><component :is="getStatusIcon(item.status)" /></el-icon>
              {{ item.status.toUpperCase() }}
            </el-tag>
          </div>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <h4 class="card-title">{{ item.name }}</h4>
          <p class="card-description">{{ item.description }}</p>

          <!-- File Info -->
          <div class="file-info">
            <div class="info-row">
              <span class="info-label">Template:</span>
              <span class="info-value">{{ item.template }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Size:</span>
              <span class="info-value">{{ item.size }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Pages:</span>
              <span class="info-value">{{ item.pages }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Created:</span>
              <span class="info-value">{{ item.createdAt }}</span>
            </div>
          </div>

          <!-- Stats -->
          <div class="item-stats">
            <div class="stat">
              <el-icon><View /></el-icon>
              <span>{{ item.views }} views</span>
            </div>
            <div class="stat">
              <el-icon><Download /></el-icon>
              <span>{{ item.downloads }} downloads</span>
            </div>
            <div v-if="item.scheduled" class="stat scheduled">
              <el-icon><Calendar /></el-icon>
              <span>Scheduled</span>
            </div>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="footer-author">
            <el-icon><User /></el-icon>
            <span>{{ item.createdBy?.split('@')[0] }}</span>
          </div>
          <div class="card-actions">
            <el-button circle size="small" @click="previewFile(item)">
              <el-icon><View /></el-icon>
            </el-button>
            <el-button circle size="small" type="primary" @click="downloadFile(item)">
              <el-icon><Download /></el-icon>
            </el-button>
            <el-button circle size="small" @click="shareFile(item)">
              <el-icon><Share /></el-icon>
            </el-button>
            <el-button circle size="small" type="danger" @click="deleteFile(item)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredItems.length === 0" class="empty-state">
      <el-empty description="No exports found">
        <el-button type="primary" @click="openExportDialog">Create Export</el-button>
      </el-empty>
    </div>

    <!-- Pagination -->
    <div v-if="filteredItems.length > 0" class="pagination-wrapper">
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

    <!-- Export Dialog -->
    <el-dialog v-model="exportDialogVisible" title="New Export" width="550px">
      <el-form :model="{}" label-width="120px">
        <el-form-item label="Report Type" required>
          <el-select style="width: 100%" placeholder="Select report type">
            <el-option label="System Health Report" value="system" />
            <el-option label="Energy Report" value="energy" />
            <el-option label="Financial Report" value="financial" />
            <el-option label="Alarms Report" value="alarms" />
            <el-option label="Maintenance Report" value="maintenance" />
          </el-select>
        </el-form-item>
        <el-form-item label="Export Format" required>
          <el-radio-group>
            <el-radio value="pdf">PDF Document</el-radio>
            <el-radio value="excel">Excel Spreadsheet</el-radio>
            <el-radio value="csv">CSV File</el-radio>
            <el-radio value="image">Image</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Date Range">
          <el-date-picker
              type="daterange"
              range-separator="to"
              start-placeholder="Start date"
              end-placeholder="End date"
              style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="Include Charts">
          <el-switch />
        </el-form-item>
        <el-form-item label="Include Data Tables">
          <el-switch />
        </el-form-item>
        <el-form-item label="Watermark">
          <el-input placeholder="Optional watermark text" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="exportDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="exportDialogVisible = false">Generate Export</el-button>
      </template>
    </el-dialog>

    <!-- Schedule Export Dialog -->
    <el-dialog v-model="scheduledVisible" title="Schedule Export" width="500px">
      <el-form :model="{}" label-width="120px">
        <el-form-item label="Report Name" required>
          <el-input placeholder="Enter report name" />
        </el-form-item>
        <el-form-item label="Frequency">
          <el-select style="width: 100%">
            <el-option label="Daily" value="daily" />
            <el-option label="Weekly" value="weekly" />
            <el-option label="Monthly" value="monthly" />
          </el-select>
        </el-form-item>
        <el-form-item label="Time">
          <el-time-picker format="HH:mm" placeholder="Select time" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Format">
          <el-select style="width: 100%">
            <el-option label="PDF" value="pdf" />
            <el-option label="Excel" value="excel" />
            <el-option label="CSV" value="csv" />
          </el-select>
        </el-form-item>
        <el-form-item label="Recipients">
          <el-input placeholder="email@example.com, another@example.com" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="scheduledVisible = false">Cancel</el-button>
        <el-button type="primary" @click="scheduledVisible = false">Schedule Export</el-button>
      </template>
    </el-dialog>

    <!-- Export History Dialog -->
    <el-dialog v-model="historyVisible" title="Export History" width="800px">
      <el-table :data="exportItems.slice(0, 10)" stripe>
        <el-table-column prop="name" label="File Name" min-width="200" />
        <el-table-column label="Format" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.format === 'pdf' ? 'danger' : row.format === 'excel' ? 'success' : 'info'" size="small">
              {{ row.format.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="Created At" width="160" />
        <el-table-column prop="downloads" label="Downloads" width="80" align="center" />
        <el-table-column label="Status" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'ready' ? 'success' : row.status === 'failed' ? 'danger' : 'warning'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Action" width="100" align="center">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="downloadFile(row)">
              <el-icon><Download /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button type="primary" @click="historyVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Preview Dialog -->
    <el-dialog v-model="previewVisible" :title="selectedItem?.name" width="800px" top="5vh">
      <div class="preview-container">
        <div class="preview-header">
          <div class="preview-info">
            <div class="preview-meta">
              <span><el-icon><Document /></el-icon> {{ selectedItem?.format?.toUpperCase() }}</span>
              <span><el-icon><Files /></el-icon> {{ selectedItem?.size }}</span>
              <span><el-icon><Calendar /></el-icon> {{ selectedItem?.createdAt }}</span>
            </div>
            <h3>{{ selectedItem?.name }}</h3>
            <p>{{ selectedItem?.description }}</p>
          </div>
        </div>
        <div class="preview-content">
          <el-empty description="Document preview will appear here" :image-size="150" />
        </div>
      </div>
      <template #footer>
        <el-button @click="previewVisible = false">Close</el-button>
        <el-button type="primary" @click="downloadFile(selectedItem)">
          <el-icon><Download /></el-icon> Download
        </el-button>
        <el-button @click="shareFile(selectedItem)">
          <el-icon><Share /></el-icon> Share
        </el-button>
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
.pdf-export-container {
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

.pdf-icon {
  background: linear-gradient(135deg, #fef0f0 0%, #fcd9d9 100%);
  color: #f56c6c;
}

.downloads-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.scheduled-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
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

.export-chart {
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

.format-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.format-chip {
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

.format-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.format-chip.active {
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

/* Exports Grid */
.exports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.export-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
}

.export-card:hover {
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

.card-format {
  width: 44px;
  height: 44px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: white;
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

.file-info {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 12px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  color: #909399;
}

.info-value {
  color: #1e293b;
  font-weight: 500;
}

.item-stats {
  display: flex;
  gap: 16px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.stat {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
}

.stat.scheduled {
  color: #e6a23c;
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

.footer-author {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
}

.card-actions {
  display: flex;
  gap: 6px;
}

.card-actions .el-button {
  background: white;
  border: 1px solid #e4e7ed;
}

.card-actions .el-button:hover {
  transform: scale(1.05);
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
  margin-bottom: 12px;
  font-size: 12px;
  color: #909399;
}

.preview-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.preview-header h3 {
  font-size: 20px;
  margin: 0 0 8px 0;
}

.preview-header p {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.preview-content {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-breakdown {
    grid-template-columns: repeat(2, 1fr);
  }

  .exports-grid {
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  }
}

@media (max-width: 768px) {
  .pdf-export-container {
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

  .format-filters {
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

  .exports-grid {
    grid-template-columns: 1fr;
  }
}
</style>