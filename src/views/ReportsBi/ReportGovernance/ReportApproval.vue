<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Search, Refresh, Document, Download, Printer,
  Share, Star, Clock, Warning, CircleCheck,
  TrendCharts, DataLine, Calendar, Setting,
  Plus, Upload, Filter, ArrowUp, ArrowDown,
  View, User, Trophy, Medal, Edit, Delete,
  CopyDocument, Check, Close, Select, List,
  Timer, Message, Notification
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Loading approval requests...',
  'Loading review queue...',
  'Preparing approval workflow...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedPriority = ref('all')
const selectedStatus = ref('all')
const approvalDetailsVisible = ref(false)
const reviewDialogVisible = ref(false)
const historyVisible = ref(false)
const chartRef = ref(null)

let approvalChart: echarts.ECharts | null = null

// Priority filters
const priorityOptions = [
  { value: 'all', label: 'All Priorities' },
  { value: 'high', label: 'High', color: '#F56C6C' },
  { value: 'medium', label: 'Medium', color: '#E6A23C' },
  { value: 'low', label: 'Low', color: '#67C23A' }
]

// Status filters
const statusOptions = [
  { value: 'all', label: 'All' },
  { value: 'pending', label: 'Pending Review' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'revision', label: 'Revision Required' }
]

// Approval requests data
const approvalRequests = ref([
  {
    id: 'APP001', name: 'Executive Dashboard Report', type: 'dashboard',
    requester: 'john.smith@system.com', requestedAt: '2024-01-15 09:30:00',
    priority: 'high', status: 'pending', department: 'Executive',
    description: 'New executive dashboard with real-time KPIs and trend analysis',
    reviewer: null, reviewedAt: null, comments: null,
    dueDate: '2024-01-18', attachments: 3, pages: 12
  },
  {
    id: 'APP002', name: 'Energy Consumption Analysis', type: 'report',
    requester: 'sarah.j@system.com', requestedAt: '2024-01-14 14:20:00',
    priority: 'medium', status: 'pending', department: 'Energy',
    description: 'Monthly energy consumption report with carbon footprint analysis',
    reviewer: null, reviewedAt: null, comments: null,
    dueDate: '2024-01-17', attachments: 5, pages: 18
  },
  {
    id: 'APP003', name: 'Financial Q1 Summary', type: 'summary',
    requester: 'mike.chen@system.com', requestedAt: '2024-01-13 11:15:00',
    priority: 'high', status: 'approved', department: 'Finance',
    description: 'Quarterly financial summary with P&L and cash flow',
    reviewer: 'finance@system.com', reviewedAt: '2024-01-14 10:00:00', comments: 'Approved with minor adjustments',
    dueDate: '2024-01-16', attachments: 8, pages: 24
  },
  {
    id: 'APP004', name: 'Security Audit Report', type: 'report',
    requester: 'david.lee@system.com', requestedAt: '2024-01-12 10:45:00',
    priority: 'high', status: 'rejected', department: 'Security',
    description: 'Weekly security audit and compliance report',
    reviewer: 'security@system.com', reviewedAt: '2024-01-13 15:30:00', comments: 'Missing critical metrics, please revise',
    dueDate: '2024-01-15', attachments: 4, pages: 15
  },
  {
    id: 'APP005', name: 'Maintenance Dashboard', type: 'dashboard',
    requester: 'robert.w@system.com', requestedAt: '2024-01-11 09:00:00',
    priority: 'medium', status: 'revision', department: 'Operations',
    description: 'Maintenance performance dashboard with SLA tracking',
    reviewer: 'ops@system.com', reviewedAt: '2024-01-12 14:00:00', comments: 'Please add MTTR and MTBF metrics',
    dueDate: '2024-01-14', attachments: 6, pages: 10
  },
  {
    id: 'APP006', name: 'Sustainability Report', type: 'report',
    requester: 'emily.w@system.com', requestedAt: '2024-01-10 13:30:00',
    priority: 'low', status: 'approved', department: 'Sustainability',
    description: 'Monthly sustainability metrics and ESG compliance',
    reviewer: 'esg@system.com', reviewedAt: '2024-01-11 11:00:00', comments: 'Great work, approved',
    dueDate: '2024-01-13', attachments: 7, pages: 20
  },
  {
    id: 'APP007', name: 'Sales Performance Dashboard', type: 'dashboard',
    requester: 'lisa.tan@system.com', requestedAt: '2024-01-09 15:00:00',
    priority: 'high', status: 'pending', department: 'Sales',
    description: 'Sales performance tracking with quota attainment',
    reviewer: null, reviewedAt: null, comments: null,
    dueDate: '2024-01-12', attachments: 4, pages: 8
  },
  {
    id: 'APP008', name: 'Inventory Analysis', type: 'analysis',
    requester: 'james.w@system.com', requestedAt: '2024-01-08 11:00:00',
    priority: 'low', status: 'revision', department: 'Supply Chain',
    description: 'Inventory turnover and optimization analysis',
    reviewer: 'scm@system.com', reviewedAt: '2024-01-09 16:00:00', comments: 'Need more details on slow-moving items',
    dueDate: '2024-01-11', attachments: 3, pages: 14
  }
])

// Approval statistics
const approvalStats = reactive({
  total: 0,
  pending: 0,
  approved: 0,
  rejected: 0,
  revision: 0,
  high: 0,
  medium: 0,
  low: 0,
  avgApprovalTime: 0,
  onTimeRate: 0
})

// Review form
const reviewForm = reactive({
  action: 'approve',
  comments: '',
  attachments: [] as string[]
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 8,
  total: approvalRequests.value.length
})

// Filtered requests
const filteredRequests = computed(() => {
  let filtered = approvalRequests.value
  if (searchKeyword.value) {
    filtered = filtered.filter(r =>
        r.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        r.description.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        r.requester.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedPriority.value !== 'all') {
    filtered = filtered.filter(r => r.priority === selectedPriority.value)
  }
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(r => r.status === selectedStatus.value)
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

  approvalChart = echarts.init(chartRef.value)
  approvalChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Pending', 'Approved', 'Rejected', 'Revision'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: ['Executive', 'Finance', 'Operations', 'Sales', 'Security', 'Energy', 'Supply Chain', 'Sustainability'] },
    yAxis: { type: 'value', name: 'Number of Requests' },
    series: [
      { name: 'Pending', type: 'bar', data: [2, 0, 0, 1, 0, 0, 0, 0], stack: 'total', itemStyle: { color: '#E6A23C', borderRadius: [4, 4, 0, 0] } },
      { name: 'Approved', type: 'bar', data: [0, 1, 0, 0, 0, 1, 0, 0], stack: 'total', itemStyle: { color: '#67C23A', borderRadius: [4, 4, 0, 0] } },
      { name: 'Rejected', type: 'bar', data: [0, 0, 0, 0, 1, 0, 0, 0], stack: 'total', itemStyle: { color: '#F56C6C', borderRadius: [4, 4, 0, 0] } },
      { name: 'Revision', type: 'bar', data: [0, 0, 1, 0, 0, 0, 1, 0], stack: 'total', itemStyle: { color: '#909399', borderRadius: [4, 4, 0, 0] } }
    ]
  })
}

const updateStats = () => {
  approvalStats.total = approvalRequests.value.length
  approvalStats.pending = approvalRequests.value.filter(r => r.status === 'pending').length
  approvalStats.approved = approvalRequests.value.filter(r => r.status === 'approved').length
  approvalStats.rejected = approvalRequests.value.filter(r => r.status === 'rejected').length
  approvalStats.revision = approvalRequests.value.filter(r => r.status === 'revision').length
  approvalStats.high = approvalRequests.value.filter(r => r.priority === 'high').length
  approvalStats.medium = approvalRequests.value.filter(r => r.priority === 'medium').length
  approvalStats.low = approvalRequests.value.filter(r => r.priority === 'low').length

  // Calculate average approval time (simplified)
  const approvedItems = approvalRequests.value.filter(r => r.status === 'approved' && r.reviewedAt)
  if (approvedItems.length > 0) {
    // Simplified calculation
    approvalStats.avgApprovalTime = 2.5
  } else {
    approvalStats.avgApprovalTime = 0
  }

  approvalStats.onTimeRate = 85
}

const handleResize = () => {
  approvalChart?.resize()
}

// ==================== Approval Functions ====================
const refreshApprovals = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  loading.value = false
  ElMessage.success('Approval requests refreshed successfully')
}

const viewApprovalDetails = (request: any) => {
  selectedRequest.value = request
  approvalDetailsVisible.value = true
}

const openReviewDialog = (request: any) => {
  selectedRequest.value = request
  reviewForm.action = 'approve'
  reviewForm.comments = ''
  reviewDialogVisible.value = true
}

const submitReview = async () => {
  if (!reviewForm.comments && reviewForm.action !== 'approve') {
    ElMessage.warning('Please provide comments for this decision')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1000))

  const index = approvalRequests.value.findIndex(r => r.id === selectedRequest.value.id)
  if (index !== -1) {
    approvalRequests.value[index].status = reviewForm.action === 'approve' ? 'approved' : reviewForm.action === 'reject' ? 'rejected' : 'revision'
    approvalRequests.value[index].reviewer = 'current@approver.com'
    approvalRequests.value[index].reviewedAt = new Date().toLocaleString()
    approvalRequests.value[index].comments = reviewForm.comments
  }

  updateStats()
  reviewDialogVisible.value = false
  ElMessage.success(`Request ${reviewForm.action === 'approve' ? 'approved' : reviewForm.action === 'reject' ? 'rejected' : 'sent for revision'} successfully`)
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

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'high': return '#F56C6C'
    case 'medium': return '#E6A23C'
    case 'low': return '#67C23A'
    default: return '#909399'
  }
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'pending': return '#E6A23C'
    case 'approved': return '#67C23A'
    case 'rejected': return '#F56C6C'
    case 'revision': return '#909399'
    default: return '#909399'
  }
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'pending': return Timer
    case 'approved': return CircleCheck
    case 'rejected': return Timer
    case 'revision': return Edit
    default: return Clock
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'pending': return 'Pending Review'
    case 'approved': return 'Approved'
    case 'rejected': return 'Rejected'
    case 'revision': return 'Revision Required'
    default: return 'Unknown'
  }
}

const formatDate = (date: string) => {
  if (!date) return 'Not yet'
  return date
}

const selectedRequest = ref<any>(null)
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
          <span class="loading-title">Loading Report Approval</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Report Governance - Report Approval</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="report-approval-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Report Approval</h1>
        <p class="page-subtitle">Review and approve report requests before publication</p>
      </div>
      <div class="header-right">
        <el-button size="large" @click="refreshApprovals" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
        <el-button size="large" @click="viewHistory">
          <el-icon><Close /></el-icon>
          History
        </el-button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon pending-icon">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ approvalStats.pending }}</div>
          <div class="stat-label">Pending Review</div>
        </div>
        <div class="stat-trend">
          <span class="trend-warning">{{ approvalStats.high }} High Priority</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon approved-icon">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ approvalStats.approved }}</div>
          <div class="stat-label">Approved</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">This month</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon rejected-icon">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ approvalStats.rejected }}</div>
          <div class="stat-label">Rejected</div>
        </div>
        <div class="stat-trend">
          <span class="trend-neutral">{{ approvalStats.revision }} Revision Required</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon metrics-icon">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ approvalStats.onTimeRate }}%</div>
          <div class="stat-label">On-Time Rate</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">Avg {{ approvalStats.avgApprovalTime }} days</span>
        </div>
      </div>
    </div>

    <!-- Stats Breakdown Row -->
    <div class="stats-breakdown">
      <div class="breakdown-item">
        <span class="breakdown-label">High Priority</span>
        <span class="breakdown-value">{{ approvalStats.high }}</span>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: (approvalStats.high / approvalStats.total) * 100 + '%', background: '#F56C6C' }"></div>
        </div>
      </div>
      <div class="breakdown-item">
        <span class="breakdown-label">Medium Priority</span>
        <span class="breakdown-value">{{ approvalStats.medium }}</span>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: (approvalStats.medium / approvalStats.total) * 100 + '%', background: '#E6A23C' }"></div>
        </div>
      </div>
      <div class="breakdown-item">
        <span class="breakdown-label">Low Priority</span>
        <span class="breakdown-value">{{ approvalStats.low }}</span>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: (approvalStats.low / approvalStats.total) * 100 + '%', background: '#67C23A' }"></div>
        </div>
      </div>
      <div class="breakdown-item">
        <span class="breakdown-label">Total Requests</span>
        <span class="breakdown-value">{{ approvalStats.total }}</span>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: '100%', background: '#409EFF' }"></div>
        </div>
      </div>
    </div>

    <!-- Chart Section -->
    <div class="chart-section">
      <div class="section-header">
        <h3>Approval Status by Department</h3>
        <el-button text type="primary" @click="initChart">Refresh</el-button>
      </div>
      <div ref="chartRef" class="approval-chart" style="height: 320px"></div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-bar">
      <div class="filters-left">
        <div class="search-box">
          <el-input
              v-model="searchKeyword"
              placeholder="Search requests..."
              :prefix-icon="Search"
              clearable
              style="width: 260px"
          />
        </div>
        <div class="priority-filters">
          <button
              v-for="p in priorityOptions"
              :key="p.value"
              class="priority-chip"
              :class="{ active: selectedPriority === p.value }"
              @click="selectedPriority = p.value"
          >
            <span class="chip-dot" :style="{ background: p.color }"></span>
            <span>{{ p.label }}</span>
          </button>
        </div>
      </div>
      <div class="filters-right">
        <el-select v-model="selectedStatus" placeholder="Status" clearable style="width: 160px">
          <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
        </el-select>
      </div>
    </div>

    <!-- Approval Requests Grid - Card Style -->
    <div class="requests-grid">
      <div
          v-for="request in filteredRequests"
          :key="request.id"
          class="request-card"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="card-type">
            <span class="type-icon">{{ request.type === 'dashboard' ? '📊' : request.type === 'report' ? '📄' : request.type === 'analysis' ? '🔍' : '📝' }}</span>
          </div>
          <div class="card-priority">
            <span class="priority-badge" :style="{ background: getPriorityColor(request.priority) + '20', color: getPriorityColor(request.priority) }">
              {{ request.priority.toUpperCase() }}
            </span>
          </div>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <h4 class="card-title">{{ request.name }}</h4>
          <p class="card-description">{{ request.description }}</p>

          <!-- Request Info -->
          <div class="request-info">
            <div class="info-row">
              <span class="info-label">Department:</span>
              <span class="info-value">{{ request.department }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Requester:</span>
              <span class="info-value">{{ request.requester?.split('@')[0] }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Requested:</span>
              <span class="info-value">{{ request.requestedAt }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Due Date:</span>
              <span class="info-value" :class="{ 'overdue': new Date(request.dueDate) < new Date() && request.status === 'pending' }">
                {{ request.dueDate }}
              </span>
            </div>
            <div class="info-row">
              <span class="info-label">Attachments:</span>
              <span class="info-value">{{ request.attachments }} files</span>
            </div>
            <div class="info-row">
              <span class="info-label">Pages:</span>
              <span class="info-value">{{ request.pages }}</span>
            </div>
          </div>

          <!-- Status -->
          <div class="request-status">
            <el-tag :type="request.status === 'pending' ? 'warning' : request.status === 'approved' ? 'success' : request.status === 'rejected' ? 'danger' : 'info'" size="small">
              <el-icon><component :is="getStatusIcon(request.status)" /></el-icon>
              {{ getStatusText(request.status) }}
            </el-tag>
          </div>

          <!-- Reviewer Info -->
          <div v-if="request.reviewer" class="reviewer-info">
            <div class="reviewer-row">
              <span class="reviewer-label">Reviewed by:</span>
              <span class="reviewer-value">{{ request.reviewer?.split('@')[0] }}</span>
            </div>
            <div class="reviewer-row">
              <span class="reviewer-label">Reviewed at:</span>
              <span class="reviewer-value">{{ request.reviewedAt }}</span>
            </div>
            <div v-if="request.comments" class="reviewer-comments">
              <span class="comments-label">Comments:</span>
              <span class="comments-value">{{ request.comments }}</span>
            </div>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="card-actions">
            <el-button size="small" @click="viewApprovalDetails(request)">
              View Details
            </el-button>
            <el-button
                v-if="request.status === 'pending'"
                size="small"
                type="primary"
                @click="openReviewDialog(request)"
            >
              Review
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredRequests.length === 0" class="empty-state">
      <el-empty description="No approval requests found">
        <el-button type="primary">Create Request</el-button>
      </el-empty>
    </div>

    <!-- Pagination -->
    <div v-if="filteredRequests.length > 0" class="pagination-wrapper">
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

    <!-- Approval Details Dialog -->
    <el-dialog v-model="approvalDetailsVisible" :title="selectedRequest?.name" width="650px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Request ID">{{ selectedRequest?.id }}</el-descriptions-item>
        <el-descriptions-item label="Type">{{ selectedRequest?.type?.toUpperCase() }}</el-descriptions-item>
        <el-descriptions-item label="Priority">
          <span class="priority-badge-small" :style="{ background: getPriorityColor(selectedRequest?.priority) + '20', color: getPriorityColor(selectedRequest?.priority) }">
            {{ selectedRequest?.priority?.toUpperCase() }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="selectedRequest?.status === 'pending' ? 'warning' : selectedRequest?.status === 'approved' ? 'success' : 'danger'" size="small">
            {{ getStatusText(selectedRequest?.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Department">{{ selectedRequest?.department }}</el-descriptions-item>
        <el-descriptions-item label="Requester">{{ selectedRequest?.requester }}</el-descriptions-item>
        <el-descriptions-item label="Requested At">{{ selectedRequest?.requestedAt }}</el-descriptions-item>
        <el-descriptions-item label="Due Date">{{ selectedRequest?.dueDate }}</el-descriptions-item>
        <el-descriptions-item label="Attachments">{{ selectedRequest?.attachments }} files</el-descriptions-item>
        <el-descriptions-item label="Pages">{{ selectedRequest?.pages }}</el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedRequest?.description }}</el-descriptions-item>
        <el-descriptions-item v-if="selectedRequest?.reviewer" label="Reviewer">{{ selectedRequest?.reviewer }}</el-descriptions-item>
        <el-descriptions-item v-if="selectedRequest?.reviewedAt" label="Reviewed At">{{ selectedRequest?.reviewedAt }}</el-descriptions-item>
        <el-descriptions-item v-if="selectedRequest?.comments" label="Comments" :span="2">{{ selectedRequest?.comments }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="approvalDetailsVisible = false">Close</el-button>
        <el-button v-if="selectedRequest?.status === 'pending'" type="primary" @click="openReviewDialog(selectedRequest)">
          Review Request
        </el-button>
      </template>
    </el-dialog>

    <!-- Review Dialog -->
    <el-dialog v-model="reviewDialogVisible" :title="`Review: ${selectedRequest?.name}`" width="550px">
      <div class="review-warning">
        <el-alert
            title="Please review the report carefully before making a decision"
            type="info"
            show-icon
            :closable="false"
        />
      </div>

      <el-form :model="reviewForm" label-width="100px" style="margin-top: 20px">
        <el-form-item label="Decision" required>
          <el-radio-group v-model="reviewForm.action">
            <el-radio value="approve">
              <el-icon><CircleCheck /></el-icon>
              Approve
            </el-radio>
            <el-radio value="reject">
              <el-icon><Timer /></el-icon>
              Reject
            </el-radio>
            <el-radio value="revision">
              <el-icon><Edit /></el-icon>
              Request Revision
            </el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Comments" :required="reviewForm.action !== 'approve'">
          <el-input
              v-model="reviewForm.comments"
              type="textarea"
              rows="4"
              placeholder="Please provide feedback or reason for decision..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitReview">Submit Decision</el-button>
      </template>
    </el-dialog>

    <!-- History Dialog -->
    <el-dialog v-model="historyVisible" title="Approval History" width="800px">
      <el-table :data="approvalRequests.filter(r => r.status !== 'pending').slice(0, 10)" stripe>
        <el-table-column prop="name" label="Report Name" min-width="200" />
        <el-table-column prop="requester" label="Requester" width="180" />
        <el-table-column label="Status" width="140" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'approved' ? 'success' : row.status === 'rejected' ? 'danger' : 'info'" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reviewedAt" label="Reviewed At" width="160" />
        <el-table-column prop="reviewer" label="Reviewer" width="150" />
        <el-table-column label="Action" width="100" align="center">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewApprovalDetails(row)">
              View
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button type="primary" @click="historyVisible = false">Close</el-button>
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
.report-approval-container {
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

.pending-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.approved-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.rejected-icon {
  background: linear-gradient(135deg, #fef0f0 0%, #fcd9d9 100%);
  color: #f56c6c;
}

.metrics-icon {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #409eff;
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

.trend-warning {
  font-size: 11px;
  color: #e6a23c;
  background: #fdf6ec;
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

.approval-chart {
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

.priority-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.priority-chip {
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

.priority-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.priority-chip.active {
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

/* Requests Grid */
.requests-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.request-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
}

.request-card:hover {
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

.card-type {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}

.type-icon {
  font-size: 24px;
}

.priority-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
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

.request-info {
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

.info-value.overdue {
  color: #f56c6c;
}

.request-status {
  margin-bottom: 12px;
}

.reviewer-info {
  background: #f0f9ff;
  border-radius: 12px;
  padding: 12px;
  margin-top: 12px;
}

.reviewer-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 12px;
}

.reviewer-label {
  color: #909399;
}

.reviewer-value {
  color: #409eff;
  font-weight: 500;
}

.reviewer-comments {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #e0e0e0;
}

.comments-label {
  font-size: 11px;
  color: #909399;
  display: block;
  margin-bottom: 4px;
}

.comments-value {
  font-size: 12px;
  color: #606266;
  line-height: 1.4;
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
}

.card-actions .el-button {
  flex: 1;
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
.review-warning {
  margin-bottom: 15px;
}

.priority-badge-small {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-breakdown {
    grid-template-columns: repeat(2, 1fr);
  }

  .requests-grid {
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  }
}

@media (max-width: 768px) {
  .report-approval-container {
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

  .priority-filters {
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

  .requests-grid {
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