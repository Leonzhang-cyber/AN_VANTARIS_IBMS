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
          <span class="loading-title">Loading</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Exception Handling Configuration</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="exception-handling-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Decision & Evidence</el-breadcrumb-item>
            <el-breadcrumb-item>Workflow Management</el-breadcrumb-item>
            <el-breadcrumb-item>Exception Handling</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Exception Handling</h1>
        <p class="description">Configure rules for handling approval workflow exceptions including timeouts, rejections, withdrawals, and escalations</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
        <el-button type="primary" @click="handleCreateRule">
          <el-icon><Plus /></el-icon>
          New Exception Rule
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6" v-for="stat in statsCards" :key="stat.title">
        <el-card class="stat-card" shadow="hover" @click="handleCardClick(stat)">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">{{ stat.title }}</div>
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
                <el-icon><component :is="stat.trend > 0 ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
                {{ Math.abs(stat.trend) }}%
                <span class="trend-label">vs last month</span>
              </div>
            </div>
            <div class="stat-icon" :style="{ background: stat.bgColor }">
              <el-icon :size="28" color="white">
                <component :is="stat.icon" />
              </el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Exception Type Overview Charts -->
    <el-row :gutter="20" class="overview-row">
      <el-col :xs="24" :lg="14">
        <el-card class="trend-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Exception Trends (Last 6 Months)</span>
              <el-radio-group v-model="trendPeriod" size="small">
                <el-radio-button value="monthly">Monthly</el-radio-button>
                <el-radio-button value="quarterly">Quarterly</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="10">
        <el-card class="distribution-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Exception by Type</span>
            </div>
          </template>
          <div ref="typeChartRef" class="pie-chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Filters -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-container">
        <div class="filter-row">
          <el-input
              v-model="filters.keyword"
              placeholder="Search by rule name"
              prefix-icon="Search"
              clearable
              style="width: 220px"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
          />
          <el-select v-model="filters.exceptionType" placeholder="Exception Type" clearable style="width: 150px">
            <el-option label="Timeout" value="Timeout" />
            <el-option label="Rejection" value="Rejection" />
            <el-option label="Withdrawal" value="Withdrawal" />
            <el-option label="Escalation" value="Escalation" />
            <el-option label="Auto-approve" value="Auto-approve" />
          </el-select>
          <el-select v-model="filters.severity" placeholder="Severity" clearable style="width: 120px">
            <el-option label="Critical" value="Critical" />
            <el-option label="High" value="High" />
            <el-option label="Medium" value="Medium" />
            <el-option label="Low" value="Low" />
          </el-select>
          <el-select v-model="filters.status" placeholder="Status" clearable style="width: 120px">
            <el-option label="Active" value="Active" />
            <el-option label="Inactive" value="Inactive" />
            <el-option label="Draft" value="Draft" />
          </el-select>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="handleResetFilters">Reset</el-button>
        </div>
      </div>
    </el-card>

    <!-- Main Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Exception Handling Rules</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchRules" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedRules" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="ruleName" label="Rule Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="exceptionType" label="Exception Type" width="130">
          <template #default="{ row }">
            <el-tag :type="getExceptionTypeTag(row.exceptionType)" size="small">{{ row.exceptionType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityTag(row.severity)" size="small">{{ row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="triggerCondition" label="Trigger Condition" min-width="200" show-overflow-tooltip />
        <el-table-column prop="action" label="Action" min-width="180" show-overflow-tooltip />
        <el-table-column prop="notifyRoles" label="Notify Roles" width="150">
          <template #default="{ row }">
            <el-popover placement="top" :width="200" trigger="hover">
              <template #reference>
                <el-tag type="info" size="small" style="cursor: pointer">
                  {{ row.notifyRoles.length }} roles
                </el-tag>
              </template>
              <div v-for="role in row.notifyRoles" :key="role" class="notify-role-item">
                {{ role }}
              </div>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updatedAt" label="Last Updated" width="110" />
        <el-table-column label="Actions" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewRule(row)">View</el-button>
            <el-button link type="success" size="small" @click="editRule(row)">Edit</el-button>
            <el-button link type="danger" size="small" @click="deleteRule(row)">Delete</el-button>
            <el-button v-if="row.status === 'Inactive'" link type="primary" size="small" @click="activateRule(row)">Activate</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredRules.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Create/Edit Rule Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? 'Create Exception Rule' : (dialogMode === 'edit' ? 'Edit Exception Rule' : 'Exception Rule Details')" width="750px" destroy-on-close>
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="140px" :disabled="dialogMode === 'view'">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="Rule Name" prop="ruleName">
              <el-input v-model="formData.ruleName" placeholder="Enter rule name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Exception Type" prop="exceptionType">
              <el-select v-model="formData.exceptionType" placeholder="Select exception type" style="width: 100%">
                <el-option label="Timeout" value="Timeout" />
                <el-option label="Rejection" value="Rejection" />
                <el-option label="Withdrawal" value="Withdrawal" />
                <el-option label="Escalation" value="Escalation" />
                <el-option label="Auto-approve" value="Auto-approve" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Severity" prop="severity">
              <el-select v-model="formData.severity" placeholder="Select severity" style="width: 100%">
                <el-option label="Critical" value="Critical" />
                <el-option label="High" value="High" />
                <el-option label="Medium" value="Medium" />
                <el-option label="Low" value="Low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Status" prop="status">
              <el-select v-model="formData.status" placeholder="Select status" style="width: 100%">
                <el-option label="Active" value="Active" />
                <el-option label="Inactive" value="Inactive" />
                <el-option label="Draft" value="Draft" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Priority" prop="priority">
              <el-select v-model="formData.priority" placeholder="Select priority" style="width: 100%">
                <el-option label="Highest" value="Highest" />
                <el-option label="High" value="High" />
                <el-option label="Normal" value="Normal" />
                <el-option label="Low" value="Low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Trigger Condition" prop="triggerCondition">
              <el-input v-model="formData.triggerCondition" type="textarea" :rows="2" placeholder="Describe when this rule should trigger" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Action" prop="action">
              <el-input v-model="formData.action" type="textarea" :rows="2" placeholder="Describe the action to take when exception occurs" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Escalate To" prop="escalateTo">
              <el-select v-model="formData.escalateTo" multiple placeholder="Select roles to escalate to" style="width: 100%">
                <el-option label="Facility Manager" value="Facility Manager" />
                <el-option label="Operations Director" value="Operations Director" />
                <el-option label="Chief Engineer" value="Chief Engineer" />
                <el-option label="VP of Operations" value="VP of Operations" />
                <el-option label="Department Head" value="Department Head" />
                <el-option label="Legal Counsel" value="Legal Counsel" />
                <el-option label="Finance Controller" value="Finance Controller" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Notify Roles" prop="notifyRoles">
              <el-select v-model="formData.notifyRoles" multiple placeholder="Select roles to notify" style="width: 100%">
                <el-option label="Facility Manager" value="Facility Manager" />
                <el-option label="Operations Director" value="Operations Director" />
                <el-option label="Chief Engineer" value="Chief Engineer" />
                <el-option label="VP of Operations" value="VP of Operations" />
                <el-option label="Department Head" value="Department Head" />
                <el-option label="Legal Counsel" value="Legal Counsel" />
                <el-option label="Finance Controller" value="Finance Controller" />
                <el-option label="Safety Officer" value="Safety Officer" />
                <el-option label="IT Director" value="IT Director" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Timeout Threshold (hours)" prop="timeoutThreshold" v-if="formData.exceptionType === 'Timeout'">
              <el-input-number v-model="formData.timeoutThreshold" :min="0" :max="168" :step="1" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Retry Count" prop="retryCount" v-if="formData.exceptionType === 'Auto-approve'">
              <el-input-number v-model="formData.retryCount" :min="0" :max="10" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Description" prop="description">
              <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="Enter rule description" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Close</el-button>
        <el-button v-if="dialogMode !== 'view'" type="primary" @click="submitForm">Save Rule</el-button>
      </template>
    </el-dialog>

    <!-- Delete Confirmation Dialog -->
    <el-dialog v-model="deleteDialogVisible" title="Confirm Delete" width="400px">
      <p>Are you sure you want to delete exception rule "{{ deleteTarget?.ruleName }}"?</p>
      <p style="color: #f56c6c; font-size: 12px; margin-top: 8px">This action cannot be undone.</p>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">Cancel</el-button>
        <el-button type="danger" @click="confirmDelete">Delete</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting, Delete
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading exception rules...',
  'Configuring handlers...',
  'Almost ready...'
]

// ==================== Interfaces ====================
interface ExceptionRule {
  id: number
  ruleName: string
  exceptionType: string
  severity: string
  priority: string
  triggerCondition: string
  action: string
  escalateTo: string[]
  notifyRoles: string[]
  timeoutThreshold?: number
  retryCount?: number
  status: string
  description: string
  createdAt: string
  updatedAt: string
}

interface StatCard {
  title: string
  value: string | number
  trend: number
  icon: string
  bgColor: string
  key: string
}

// ==================== Chart References ====================
const trendChartRef = ref<HTMLElement>()
const typeChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null
let typeChart: echarts.ECharts | null = null

const trendPeriod = ref<'monthly' | 'quarterly'>('monthly')

// ==================== Mock Data ====================
const statsCards = ref<StatCard[]>([
  { title: 'Active Rules', value: 18, trend: 12, icon: 'Document', bgColor: '#409eff', key: 'active' },
  { title: 'Total Exceptions', value: 156, trend: -8, icon: 'TrendCharts', bgColor: '#f56c6c', key: 'exceptions' },
  { title: 'Avg Resolution Time', value: '2.4 hrs', trend: -15, icon: 'Clock', bgColor: '#e6a23c', key: 'resolution' },
  { title: 'Auto-resolved', value: '68%', trend: 10, icon: 'Checked', bgColor: '#67c23a', key: 'autoResolved' }
])

const exceptionRules = ref<ExceptionRule[]>([
  {
    id: 1,
    ruleName: 'Approval Timeout - 48 Hours',
    exceptionType: 'Timeout',
    severity: 'High',
    priority: 'High',
    triggerCondition: 'Approval step exceeds 48 hours without response',
    action: 'Escalate to next level approver and send reminder notification',
    escalateTo: ['Operations Director', 'Department Head'],
    notifyRoles: ['Facility Manager', 'Chief Engineer'],
    timeoutThreshold: 48,
    status: 'Active',
    description: 'Automatically escalates approval when pending for more than 48 hours',
    createdAt: '2024-01-05',
    updatedAt: '2024-01-15'
  },
  {
    id: 2,
    ruleName: 'Rejection Handling - Major Faults',
    exceptionType: 'Rejection',
    severity: 'Critical',
    priority: 'Highest',
    triggerCondition: 'Critical or High priority fault decision is rejected',
    action: 'Trigger management review meeting and auto-create escalation ticket',
    escalateTo: ['VP of Operations', 'Chief Engineer'],
    notifyRoles: ['Facility Manager', 'Operations Director', 'Safety Officer'],
    status: 'Active',
    description: 'Handles rejection of critical fault decisions with management escalation',
    createdAt: '2024-01-03',
    updatedAt: '2024-01-12'
  },
  {
    id: 3,
    ruleName: 'Withdrawal Processing',
    exceptionType: 'Withdrawal',
    severity: 'Medium',
    priority: 'Normal',
    triggerCondition: 'User withdraws their approval request',
    action: 'Notify original approvers and archive the request with reason',
    escalateTo: [],
    notifyRoles: ['Facility Manager', 'Department Head'],
    status: 'Active',
    description: 'Processes withdrawal requests and notifies affected parties',
    createdAt: '2024-01-08',
    updatedAt: '2024-01-18'
  },
  {
    id: 4,
    ruleName: 'Emergency Escalation',
    exceptionType: 'Escalation',
    severity: 'Critical',
    priority: 'Highest',
    triggerCondition: 'Emergency response required or system critical failure',
    action: 'Immediate escalation to on-call executive and emergency team activation',
    escalateTo: ['VP of Operations', 'Facility Manager', 'Safety Officer'],
    notifyRoles: ['Operations Director', 'Chief Engineer', 'Legal Counsel'],
    status: 'Active',
    description: 'Handles emergency situations requiring immediate executive attention',
    createdAt: '2024-01-01',
    updatedAt: '2024-01-10'
  },
  {
    id: 5,
    ruleName: 'Auto-approve - Low Risk',
    exceptionType: 'Auto-approve',
    severity: 'Low',
    priority: 'Low',
    triggerCondition: 'Low priority decision with high confidence score (>90%)',
    action: 'Auto-approve with notification to manager',
    escalateTo: [],
    notifyRoles: ['Facility Manager', 'Department Head'],
    retryCount: 0,
    status: 'Active',
    description: 'Automatically approves low-risk decisions based on AI confidence',
    createdAt: '2024-01-10',
    updatedAt: '2024-01-20'
  },
  {
    id: 6,
    ruleName: 'Timeout - 24 Hours Fast Track',
    exceptionType: 'Timeout',
    severity: 'High',
    priority: 'High',
    triggerCondition: 'Urgent approval step exceeds 24 hours',
    action: 'Auto-escalate to VP and send urgent alert',
    escalateTo: ['VP of Operations', 'Operations Director'],
    notifyRoles: ['Facility Manager', 'Chief Engineer'],
    timeoutThreshold: 24,
    status: 'Active',
    description: 'Fast-track escalation for time-sensitive approvals',
    createdAt: '2024-01-06',
    updatedAt: '2024-01-14'
  },
  {
    id: 7,
    ruleName: 'Rejection - ESG Decisions',
    exceptionType: 'Rejection',
    severity: 'High',
    priority: 'High',
    triggerCondition: 'ESG decision rejected by initial approver',
    action: 'Route to ESG committee for review and decision reversal consideration',
    escalateTo: ['VP of Operations', 'Operations Director'],
    notifyRoles: ['ESG Manager', 'Facility Manager', 'Legal Counsel'],
    status: 'Active',
    description: 'Special handling for rejected ESG initiatives',
    createdAt: '2024-01-07',
    updatedAt: '2024-01-16'
  },
  {
    id: 8,
    ruleName: 'Auto-approve - Budget Under $1k',
    exceptionType: 'Auto-approve',
    severity: 'Low',
    priority: 'Low',
    triggerCondition: 'Budget approval request under $1,000',
    action: 'Auto-approve with monthly report to finance',
    escalateTo: [],
    notifyRoles: ['Finance Controller', 'Department Head'],
    retryCount: 0,
    status: 'Active',
    description: 'Streamlines low-value purchase approvals',
    createdAt: '2024-01-09',
    updatedAt: '2024-01-17'
  },
  {
    id: 9,
    ruleName: 'Timeout - Weekend Exception',
    exceptionType: 'Timeout',
    severity: 'Medium',
    priority: 'Normal',
    triggerCondition: 'Approval pending over weekend (Friday 5pm to Monday 9am)',
    action: 'Extend deadline by 48 hours and send reminder',
    escalateTo: [],
    notifyRoles: ['Facility Manager', 'Department Head'],
    timeoutThreshold: 72,
    status: 'Active',
    description: 'Handles approvals that span weekends',
    createdAt: '2024-01-11',
    updatedAt: '2024-01-19'
  },
  {
    id: 10,
    ruleName: 'Escalation - Chain Approval Failure',
    exceptionType: 'Escalation',
    severity: 'High',
    priority: 'High',
    triggerCondition: 'Primary approver unavailable (out of office)',
    action: 'Skip to next available approver in chain',
    escalateTo: ['Operations Director', 'Department Head'],
    notifyRoles: ['Facility Manager', 'Chief Engineer'],
    status: 'Inactive',
    description: 'Handles scenarios where primary approver is unavailable',
    createdAt: '2023-12-15',
    updatedAt: '2024-01-05'
  }
])

// ==================== Reactive Variables ====================
const tableLoading = ref(false)
const dialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit' | 'view'>('view')
const deleteTarget = ref<ExceptionRule | null>(null)
const formRef = ref()
const currentPage = ref(1)
const pageSize = ref(10)

const filters = reactive({
  keyword: '',
  exceptionType: '',
  severity: '',
  status: ''
})

const formData = reactive<ExceptionRule>({
  id: 0,
  ruleName: '',
  exceptionType: 'Timeout',
  severity: 'Medium',
  priority: 'Normal',
  triggerCondition: '',
  action: '',
  escalateTo: [],
  notifyRoles: [],
  timeoutThreshold: 48,
  retryCount: 0,
  status: 'Draft',
  description: '',
  createdAt: '',
  updatedAt: ''
})

const formRules = {
  ruleName: [{ required: true, message: 'Please enter rule name', trigger: 'blur' }],
  exceptionType: [{ required: true, message: 'Please select exception type', trigger: 'change' }],
  severity: [{ required: true, message: 'Please select severity', trigger: 'change' }],
  triggerCondition: [{ required: true, message: 'Please enter trigger condition', trigger: 'blur' }],
  action: [{ required: true, message: 'Please enter action', trigger: 'blur' }]
}

// ==================== Computed ====================
const filteredRules = computed(() => {
  let filtered = [...exceptionRules.value]

  if (filters.keyword) {
    filtered = filtered.filter(r =>
        r.ruleName.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        r.description.toLowerCase().includes(filters.keyword.toLowerCase())
    )
  }

  if (filters.exceptionType) {
    filtered = filtered.filter(r => r.exceptionType === filters.exceptionType)
  }

  if (filters.severity) {
    filtered = filtered.filter(r => r.severity === filters.severity)
  }

  if (filters.status) {
    filtered = filtered.filter(r => r.status === filters.status)
  }

  return filtered
})

const paginatedRules = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRules.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getExceptionTypeTag = (type: string): string => {
  const map: Record<string, string> = {
    'Timeout': 'warning',
    'Rejection': 'danger',
    'Withdrawal': 'info',
    'Escalation': 'danger',
    'Auto-approve': 'success'
  }
  return map[type] || 'info'
}

const getSeverityTag = (severity: string): string => {
  const map: Record<string, string> = {
    'Critical': 'danger',
    'High': 'warning',
    'Medium': 'info',
    'Low': 'success'
  }
  return map[severity] || 'info'
}

const getStatusTag = (status: string): string => {
  const map: Record<string, string> = {
    'Active': 'success',
    'Inactive': 'info',
    'Draft': 'warning'
  }
  return map[status] || 'info'
}

// ==================== Chart Initialization ====================
const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: ['Timeout', 'Rejection', 'Withdrawal', 'Escalation', 'Auto-approve'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '12%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    },
    yAxis: {
      type: 'value',
      name: 'Exception Count'
    },
    series: [
      { name: 'Timeout', type: 'bar', data: [8, 7, 9, 6, 10, 8], stack: 'total' },
      { name: 'Rejection', type: 'bar', data: [5, 4, 6, 5, 7, 4], stack: 'total' },
      { name: 'Withdrawal', type: 'bar', data: [3, 2, 4, 3, 2, 3], stack: 'total' },
      { name: 'Escalation', type: 'bar', data: [4, 5, 3, 4, 6, 5], stack: 'total' },
      { name: 'Auto-approve', type: 'bar', data: [12, 14, 16, 18, 20, 22], stack: 'total' }
    ]
  }

  trendChart.setOption(option)
  window.addEventListener('resize', () => trendChart?.resize())
}

const initTypeChart = () => {
  if (!typeChartRef.value) return
  if (typeChart) typeChart.dispose()

  typeChart = echarts.init(typeChartRef.value)

  const typeCount = {
    'Timeout': exceptionRules.value.filter(r => r.exceptionType === 'Timeout').length,
    'Rejection': exceptionRules.value.filter(r => r.exceptionType === 'Rejection').length,
    'Withdrawal': exceptionRules.value.filter(r => r.exceptionType === 'Withdrawal').length,
    'Escalation': exceptionRules.value.filter(r => r.exceptionType === 'Escalation').length,
    'Auto-approve': exceptionRules.value.filter(r => r.exceptionType === 'Auto-approve').length
  }

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {d}% ({c} rules)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: ['Timeout', 'Rejection', 'Withdrawal', 'Escalation', 'Auto-approve']
    },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: typeCount['Timeout'], name: 'Timeout', itemStyle: { color: '#e6a23c' } },
        { value: typeCount['Rejection'], name: 'Rejection', itemStyle: { color: '#f56c6c' } },
        { value: typeCount['Withdrawal'], name: 'Withdrawal', itemStyle: { color: '#909399' } },
        { value: typeCount['Escalation'], name: 'Escalation', itemStyle: { color: '#f56c6c' } },
        { value: typeCount['Auto-approve'], name: 'Auto-approve', itemStyle: { color: '#67c23a' } }
      ],
      emphasis: {
        scale: true,
        label: {
          show: true,
          formatter: '{b}: {d}%'
        }
      },
      label: {
        show: true,
        formatter: '{b}: {d}%'
      }
    }]
  }

  typeChart.setOption(option)
  window.addEventListener('resize', () => typeChart?.resize())
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: StatCard) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleResetFilters = () => {
  filters.keyword = ''
  filters.exceptionType = ''
  filters.severity = ''
  filters.status = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredRules.value.length} exception rules...`)
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const fetchRules = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Data refreshed')
  }, 500)
}

const handleCreateRule = () => {
  dialogMode.value = 'create'
  Object.assign(formData, {
    id: 0,
    ruleName: '',
    exceptionType: 'Timeout',
    severity: 'Medium',
    priority: 'Normal',
    triggerCondition: '',
    action: '',
    escalateTo: [],
    notifyRoles: [],
    timeoutThreshold: 48,
    retryCount: 0,
    status: 'Draft',
    description: '',
    createdAt: new Date().toISOString().split('T')[0],
    updatedAt: new Date().toISOString().split('T')[0]
  })
  dialogVisible.value = true
}

const viewRule = (row: ExceptionRule) => {
  dialogMode.value = 'view'
  Object.assign(formData, JSON.parse(JSON.stringify(row)))
  dialogVisible.value = true
}

const editRule = (row: ExceptionRule) => {
  dialogMode.value = 'edit'
  Object.assign(formData, JSON.parse(JSON.stringify(row)))
  dialogVisible.value = true
}

const deleteRule = (row: ExceptionRule) => {
  deleteTarget.value = row
  deleteDialogVisible.value = true
}

const activateRule = (row: ExceptionRule) => {
  ElMessageBox.confirm(`Activate exception rule "${row.ruleName}"?`, 'Activate Confirmation', {
    confirmButtonText: 'Activate',
    cancelButtonText: 'Cancel',
    type: 'success'
  }).then(() => {
    const index = exceptionRules.value.findIndex(r => r.id === row.id)
    if (index !== -1) {
      exceptionRules.value[index].status = 'Active'
      exceptionRules.value[index].updatedAt = new Date().toISOString().split('T')[0]
      ElMessage.success(`Activated: ${row.ruleName}`)
      initTypeChart()
    }
  }).catch(() => {})
}

const confirmDelete = () => {
  if (deleteTarget.value) {
    const index = exceptionRules.value.findIndex(r => r.id === deleteTarget.value!.id)
    if (index !== -1) {
      exceptionRules.value.splice(index, 1)
      ElMessage.success(`Deleted: ${deleteTarget.value.ruleName}`)
      initTypeChart()
    }
  }
  deleteDialogVisible.value = false
  deleteTarget.value = null
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      const newRule: ExceptionRule = {
        id: formData.id || Date.now(),
        ruleName: formData.ruleName,
        exceptionType: formData.exceptionType,
        severity: formData.severity,
        priority: formData.priority,
        triggerCondition: formData.triggerCondition,
        action: formData.action,
        escalateTo: formData.escalateTo,
        notifyRoles: formData.notifyRoles,
        timeoutThreshold: formData.timeoutThreshold,
        retryCount: formData.retryCount,
        status: formData.status,
        description: formData.description,
        createdAt: formData.createdAt || new Date().toISOString().split('T')[0],
        updatedAt: new Date().toISOString().split('T')[0]
      }

      if (dialogMode.value === 'create') {
        exceptionRules.value.unshift(newRule)
        ElMessage.success('Exception rule created successfully')
      } else if (dialogMode.value === 'edit') {
        const index = exceptionRules.value.findIndex(r => r.id === formData.id)
        if (index !== -1) {
          exceptionRules.value[index] = newRule
          ElMessage.success('Exception rule updated successfully')
        }
      }

      initTypeChart()
      dialogVisible.value = false
      currentPage.value = 1
    }
  })
}

const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {}

// ==================== Loading Simulation ====================
const initCharts = async () => {
  await nextTick()
  setTimeout(() => {
    initTrendChart()
    initTypeChart()
  }, 100)
}

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
      initCharts()
      fetchRules()
    }, 400)
  }, 2000)
})
</script>

<style scoped lang="scss">
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

/* ==================== Main Page Styles ==================== */
.exception-handling-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;

  .breadcrumb {
    margin-bottom: 8px;
  }

  h1 {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 8px 0;
  }

  .description {
    color: #909399;
    font-size: 14px;
    margin: 0;
  }

  .header-actions {
    display: flex;
    gap: 12px;
  }
}

.stats-row {
  margin-bottom: 20px;
}

.overview-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
  }

  .stat-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .stat-info {
    flex: 1;
  }

  .stat-title {
    font-size: 14px;
    color: #909399;
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }

  .stat-trend {
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 4px;

    &.up { color: #67c23a; }
    &.down { color: #f56c6c; }

    .trend-label {
      color: #909399;
      margin-left: 4px;
    }
  }

  .stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.trend-card, .distribution-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}

.chart-container {
  width: 100%;
  height: 320px;
}

.pie-chart-container {
  width: 100%;
  height: 300px;
}

.filter-card {
  margin-bottom: 20px;

  .filter-container {
    .filter-row {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
    }
  }
}

.table-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .table-actions {
    display: flex;
    gap: 8px;
    align-items: center;
  }
}

.notify-role-item {
  padding: 4px 0;
  font-size: 13px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-dialog__body) {
  padding-top: 20px;
  max-height: 60vh;
  overflow-y: auto;
}
</style>