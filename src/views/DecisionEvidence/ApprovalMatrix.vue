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
        <div class="loading-tip">Approval Matrix</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="approval-matrix-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Decision & Evidence</el-breadcrumb-item>
            <el-breadcrumb-item>Approval Matrix</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Approval Matrix</h1>
        <p class="description">Define and manage approval workflows, authority levels, and decision escalation rules</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
        <el-button type="primary" @click="handleCreateRule">
          <el-icon><Plus /></el-icon>
          New Approval Rule
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

    <!-- Approval Matrix Heatmap -->
    <el-card class="heatmap-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Approval Authority Matrix</span>
          <el-button size="small" @click="handleRefreshMatrix">
            <el-icon><Refresh /></el-icon>
            Refresh
          </el-button>
        </div>
      </template>
      <div ref="heatmapChartRef" class="heatmap-container"></div>
    </el-card>

    <!-- Filters -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-container">
        <div class="filter-row">
          <el-input
              v-model="filters.keyword"
              placeholder="Search by rule name or description"
              prefix-icon="Search"
              clearable
              style="width: 250px"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
          />
          <el-select v-model="filters.decisionType" placeholder="Decision Type" clearable style="width: 150px">
            <el-option label="Fault Decision" value="Fault Decision" />
            <el-option label="Maintenance Decision" value="Maintenance Decision" />
            <el-option label="ESG Decision" value="ESG Decision" />
            <el-option label="Energy Decision" value="Energy Decision" />
            <el-option label="AI Recommendation" value="AI Recommendation" />
          </el-select>
          <el-select v-model="filters.priority" placeholder="Priority" clearable style="width: 120px">
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
          <span>Approval Rules</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchRules" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedRules" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="ruleName" label="Rule Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="decisionType" label="Decision Type" width="150">
          <template #default="{ row }">
            <el-tag :type="getDecisionTypeTag(row.decisionType)" size="small">{{ row.decisionType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="Priority" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityTag(row.priority)" size="small">{{ row.priority }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="approvalLevels" label="Approval Levels" width="120">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.approvalLevels.length }} levels</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="requiredApprovers" label="Required Approvers" width="140">
          <template #default="{ row }">
            <el-popover placement="top" :width="300" trigger="hover">
              <template #reference>
                <el-tag type="primary" size="small" style="cursor: pointer">
                  {{ row.requiredApprovers.length }} approvers
                </el-tag>
              </template>
              <div v-for="(approver, idx) in row.requiredApprovers" :key="idx" class="approver-item">
                <strong>{{ approver.role }}</strong>: {{ approver.name }}
              </div>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column prop="escalationTime" label="Escalation Time" width="130">
          <template #default="{ row }">
            <span v-if="row.escalationTime">{{ row.escalationTime }} hours</span>
            <span v-else class="na-text">N/A</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updatedAt" label="Last Updated" width="120" />
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
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? 'Create Approval Rule' : (dialogMode === 'edit' ? 'Edit Approval Rule' : 'Approval Rule Details')" width="800px" destroy-on-close>
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="140px" :disabled="dialogMode === 'view'">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="Rule Name" prop="ruleName">
              <el-input v-model="formData.ruleName" placeholder="Enter rule name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Decision Type" prop="decisionType">
              <el-select v-model="formData.decisionType" placeholder="Select decision type" style="width: 100%">
                <el-option label="Fault Decision" value="Fault Decision" />
                <el-option label="Maintenance Decision" value="Maintenance Decision" />
                <el-option label="ESG Decision" value="ESG Decision" />
                <el-option label="Energy Decision" value="Energy Decision" />
                <el-option label="AI Recommendation" value="AI Recommendation" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Priority" prop="priority">
              <el-select v-model="formData.priority" placeholder="Select priority" style="width: 100%">
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
            <el-form-item label="Escalation Time (hours)" prop="escalationTime">
              <el-input-number v-model="formData.escalationTime" :min="0" :max="168" :step="1" style="width: 100%" />
              <span style="margin-left: 8px; color: #909399">0 = no escalation</span>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Description" prop="description">
              <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="Enter rule description" />
            </el-form-item>
          </el-col>

          <!-- Approval Levels Section -->
          <el-col :span="24">
            <el-divider content-position="left">Approval Levels</el-divider>
            <div class="approval-levels-section">
              <div v-for="(level, index) in formData.approvalLevels" :key="index" class="approval-level-item">
                <el-card shadow="never" class="level-card">
                  <div class="level-header">
                    <span class="level-name">Level {{ index + 1 }}: {{ level.name }}</span>
                    <el-button v-if="dialogMode !== 'view'" link type="danger" @click="removeApprovalLevel(index)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                  <div class="level-content">
                    <div class="level-field">
                      <span class="field-label">Minimum Approvers:</span>
                      <el-input-number v-model="level.minApprovers" :min="1" :max="level.approvers.length" :disabled="dialogMode === 'view'" size="small" />
                    </div>
                    <div class="level-field">
                      <span class="field-label">Approvers:</span>
                      <el-select v-model="level.approvers" multiple placeholder="Select approvers" :disabled="dialogMode === 'view'" size="small" style="width: 400px">
                        <el-option v-for="user in availableApprovers" :key="user.id" :label="`${user.name} (${user.role})`" :value="user.id" />
                      </el-select>
                    </div>
                  </div>
                </el-card>
              </div>
              <el-button v-if="dialogMode !== 'view'" type="dashed" @click="addApprovalLevel" style="width: 100%; margin-top: 12px">
                <el-icon><Plus /></el-icon>
                Add Approval Level
              </el-button>
            </div>
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
      <p>Are you sure you want to delete approval rule "{{ deleteTarget?.ruleName }}"?</p>
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
  'Loading approval matrix...',
  'Fetching workflow data...',
  'Almost ready...'
]

// ==================== Interfaces ====================
interface Approver {
  id: number
  name: string
  role: string
  email: string
  department: string
}

interface ApprovalLevel {
  name: string
  minApprovers: number
  approvers: number[]
}

interface ApprovalRule {
  id: number
  ruleName: string
  decisionType: string
  priority: string
  approvalLevels: ApprovalLevel[]
  requiredApprovers: Approver[]
  escalationTime: number
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
const heatmapChartRef = ref<HTMLElement>()
let heatmapChart: echarts.ECharts | null = null

// ==================== Mock Data ====================
const statsCards = ref<StatCard[]>([
  { title: 'Active Rules', value: 24, trend: 8, icon: 'Document', bgColor: '#409eff', key: 'active' },
  { title: 'Total Approvers', value: 36, trend: 5, icon: 'Checked', bgColor: '#67c23a', key: 'approvers' },
  { title: 'Avg Approval Time', value: '2.4 days', trend: -12, icon: 'Clock', bgColor: '#e6a23c', key: 'time' },
  { title: 'Escalations', value: 8, trend: 15, icon: 'TrendCharts', bgColor: '#f56c6c', key: 'escalations' }
])

const availableApprovers = ref<Approver[]>([
  { id: 1, name: 'John Smith', role: 'Facility Manager', email: 'john.smith@ibms.com', department: 'Facilities' },
  { id: 2, name: 'Sarah Chen', role: 'Operations Director', email: 'sarah.chen@ibms.com', department: 'Operations' },
  { id: 3, name: 'David Wang', role: 'Chief Engineer', email: 'david.wang@ibms.com', department: 'Engineering' },
  { id: 4, name: 'Lisa Zhang', role: 'Energy Manager', email: 'lisa.zhang@ibms.com', department: 'Energy' },
  { id: 5, name: 'Mike Johnson', role: 'Maintenance Supervisor', email: 'mike.johnson@ibms.com', department: 'Maintenance' },
  { id: 6, name: 'Emily Zhao', role: 'ESG Manager', email: 'emily.zhao@ibms.com', department: 'ESG' },
  { id: 7, name: 'Robert Liu', role: 'Safety Officer', email: 'robert.liu@ibms.com', department: 'Safety' },
  { id: 8, name: 'Tom Harris', role: 'IT Director', email: 'tom.harris@ibms.com', department: 'IT' },
  { id: 9, name: 'Anna Kim', role: 'Finance Controller', email: 'anna.kim@ibms.com', department: 'Finance' },
  { id: 10, name: 'James Wu', role: 'VP of Operations', email: 'james.wu@ibms.com', department: 'Executive' },
  { id: 11, name: 'Maria Garcia', role: 'Legal Counsel', email: 'maria.garcia@ibms.com', department: 'Legal' },
  { id: 12, name: 'Chris Lee', role: 'Procurement Manager', email: 'chris.lee@ibms.com', department: 'Procurement' }
])

const approvalRules = ref<ApprovalRule[]>([
  {
    id: 1,
    ruleName: 'Critical Fault Resolution',
    decisionType: 'Fault Decision',
    priority: 'Critical',
    approvalLevels: [
      { name: 'Technical Review', minApprovers: 1, approvers: [3, 5] },
      { name: 'Management Approval', minApprovers: 1, approvers: [1, 2] },
      { name: 'Executive Sign-off', minApprovers: 1, approvers: [10] }
    ],
    requiredApprovers: [availableApprovers.value[2], availableApprovers.value[1], availableApprovers.value[9]],
    escalationTime: 48,
    status: 'Active',
    description: 'Approval workflow for critical fault decisions requiring technical, management and executive approval',
    createdAt: '2024-01-01',
    updatedAt: '2024-01-15'
  },
  {
    id: 2,
    ruleName: 'Major Maintenance Decision',
    decisionType: 'Maintenance Decision',
    priority: 'High',
    approvalLevels: [
      { name: 'Technical Assessment', minApprovers: 1, approvers: [5, 3] },
      { name: 'Manager Approval', minApprovers: 1, approvers: [1] },
      { name: 'Ops Director', minApprovers: 1, approvers: [2] }
    ],
    requiredApprovers: [availableApprovers.value[4], availableApprovers.value[0], availableApprovers.value[1]],
    escalationTime: 72,
    status: 'Active',
    description: 'Approval workflow for major maintenance decisions over $10,000',
    createdAt: '2024-01-02',
    updatedAt: '2024-01-10'
  },
  {
    id: 3,
    ruleName: 'ESG Initiative Approval',
    decisionType: 'ESG Decision',
    priority: 'High',
    approvalLevels: [
      { name: 'ESG Review', minApprovers: 1, approvers: [6] },
      { name: 'Sustainability Committee', minApprovers: 2, approvers: [2, 4, 6] },
      { name: 'Executive Approval', minApprovers: 1, approvers: [10, 2] }
    ],
    requiredApprovers: [availableApprovers.value[5], availableApprovers.value[3], availableApprovers.value[9]],
    escalationTime: 96,
    status: 'Active',
    description: 'Approval workflow for ESG-related decisions and sustainability initiatives',
    createdAt: '2024-01-03',
    updatedAt: '2024-01-12'
  },
  {
    id: 4,
    ruleName: 'Energy Project - Medium',
    decisionType: 'Energy Decision',
    priority: 'Medium',
    approvalLevels: [
      { name: 'Energy Team Review', minApprovers: 1, approvers: [4] },
      { name: 'Manager Approval', minApprovers: 1, approvers: [1] }
    ],
    requiredApprovers: [availableApprovers.value[3], availableApprovers.value[0]],
    escalationTime: 48,
    status: 'Active',
    description: 'Approval workflow for medium-scale energy efficiency projects ($25k - $100k)',
    createdAt: '2024-01-04',
    updatedAt: '2024-01-08'
  },
  {
    id: 5,
    ruleName: 'AI Recommendation - Low Risk',
    decisionType: 'AI Recommendation',
    priority: 'Low',
    approvalLevels: [
      { name: 'Technical Review', minApprovers: 1, approvers: [3, 5] },
      { name: 'Manager Approval', minApprovers: 1, approvers: [1] }
    ],
    requiredApprovers: [availableApprovers.value[2], availableApprovers.value[0]],
    escalationTime: 24,
    status: 'Active',
    description: 'Lightweight approval for low-risk AI-generated recommendations',
    createdAt: '2024-01-05',
    updatedAt: '2024-01-09'
  },
  {
    id: 6,
    ruleName: 'Emergency Response Protocol',
    decisionType: 'Fault Decision',
    priority: 'Critical',
    approvalLevels: [
      { name: 'Emergency Response', minApprovers: 1, approvers: [7, 1] },
      { name: 'Ops Director', minApprovers: 1, approvers: [2] },
      { name: 'Executive Notification', minApprovers: 1, approvers: [10] }
    ],
    requiredApprovers: [availableApprovers.value[6], availableApprovers.value[1], availableApprovers.value[9]],
    escalationTime: 2,
    status: 'Active',
    description: 'Emergency approval workflow with fast escalation for critical incidents',
    createdAt: '2024-01-06',
    updatedAt: '2024-01-14'
  },
  {
    id: 7,
    ruleName: 'Budget Override Approval',
    decisionType: 'Maintenance Decision',
    priority: 'High',
    approvalLevels: [
      { name: 'Finance Review', minApprovers: 1, approvers: [9] },
      { name: 'Department Head', minApprovers: 1, approvers: [1, 2] },
      { name: 'VP Approval', minApprovers: 1, approvers: [10] }
    ],
    requiredApprovers: [availableApprovers.value[8], availableApprovers.value[0], availableApprovers.value[9]],
    escalationTime: 48,
    status: 'Draft',
    description: 'Special approval for maintenance decisions exceeding budget',
    createdAt: '2024-01-07',
    updatedAt: '2024-01-11'
  },
  {
    id: 8,
    ruleName: 'Routine Maintenance',
    decisionType: 'Maintenance Decision',
    priority: 'Low',
    approvalLevels: [
      { name: 'Supervisor Review', minApprovers: 1, approvers: [5] },
      { name: 'Manager Approval', minApprovers: 1, approvers: [1] }
    ],
    requiredApprovers: [availableApprovers.value[4], availableApprovers.value[0]],
    escalationTime: 0,
    status: 'Inactive',
    description: 'Simple approval for routine maintenance (<$5,000)',
    createdAt: '2024-01-08',
    updatedAt: '2024-01-08'
  }
])

// ==================== Reactive Variables ====================
const tableLoading = ref(false)
const dialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit' | 'view'>('view')
const deleteTarget = ref<ApprovalRule | null>(null)
const formRef = ref()
const currentPage = ref(1)
const pageSize = ref(10)

const filters = reactive({
  keyword: '',
  decisionType: '',
  priority: '',
  status: ''
})

const formData = reactive<ApprovalRule>({
  id: 0,
  ruleName: '',
  decisionType: '',
  priority: 'Medium',
  approvalLevels: [],
  requiredApprovers: [],
  escalationTime: 48,
  status: 'Draft',
  description: '',
  createdAt: '',
  updatedAt: ''
})

const formRules = {
  ruleName: [{ required: true, message: 'Please enter rule name', trigger: 'blur' }],
  decisionType: [{ required: true, message: 'Please select decision type', trigger: 'change' }],
  priority: [{ required: true, message: 'Please select priority', trigger: 'change' }],
  approvalLevels: [{ required: true, message: 'Please add at least one approval level', trigger: 'change' }]
}

// ==================== Computed ====================
const filteredRules = computed(() => {
  let filtered = [...approvalRules.value]

  if (filters.keyword) {
    filtered = filtered.filter(r =>
        r.ruleName.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        r.description.toLowerCase().includes(filters.keyword.toLowerCase())
    )
  }

  if (filters.decisionType) {
    filtered = filtered.filter(r => r.decisionType === filters.decisionType)
  }

  if (filters.priority) {
    filtered = filtered.filter(r => r.priority === filters.priority)
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
const getDecisionTypeTag = (type: string): string => {
  const map: Record<string, string> = {
    'Fault Decision': 'danger',
    'Maintenance Decision': 'warning',
    'ESG Decision': 'success',
    'Energy Decision': 'primary',
    'AI Recommendation': 'info'
  }
  return map[type] || 'info'
}

const getPriorityTag = (priority: string): string => {
  const map: Record<string, string> = {
    'Critical': 'danger',
    'High': 'warning',
    'Medium': 'info',
    'Low': 'success'
  }
  return map[priority] || 'info'
}

const getStatusTag = (status: string): string => {
  const map: Record<string, string> = {
    'Active': 'success',
    'Inactive': 'info',
    'Draft': 'warning'
  }
  return map[status] || 'info'
}

const getApproverNames = (approverIds: number[]): string => {
  return approverIds.map(id => {
    const approver = availableApprovers.value.find(a => a.id === id)
    return approver ? `${approver.name} (${approver.role})` : ''
  }).join(', ')
}

// ==================== Chart Initialization ====================
const initHeatmapChart = () => {
  if (!heatmapChartRef.value) return
  if (heatmapChart) heatmapChart.dispose()

  heatmapChart = echarts.init(heatmapChartRef.value)

  const decisionTypes = ['Fault Decision', 'Maintenance Decision', 'ESG Decision', 'Energy Decision', 'AI Recommendation']
  const priorities = ['Critical', 'High', 'Medium', 'Low']
  const heatmapData: [number, number, number][] = []

  const levelMatrix = [
    [3, 3, 2, 1], // Fault Decision
    [3, 2, 2, 1], // Maintenance Decision
    [3, 3, 2, 1], // ESG Decision
    [2, 2, 2, 1], // Energy Decision
    [2, 2, 1, 1]  // AI Recommendation
  ]

  for (let i = 0; i < decisionTypes.length; i++) {
    for (let j = 0; j < priorities.length; j++) {
      heatmapData.push([i, j, levelMatrix[i][j]])
    }
  }

  const option: echarts.EChartsOption = {
    tooltip: {
      position: 'top',
      formatter: (params: any) => {
        const data = params.data
        return `${decisionTypes[data[0]]}<br/>Priority: ${priorities[data[1]]}<br/>Approval Levels Required: ${data[2]}`
      }
    },
    xAxis: {
      type: 'category',
      data: decisionTypes,
      name: 'Decision Type',
      axisLabel: { rotate: 30, interval: 0 }
    },
    yAxis: {
      type: 'category',
      data: priorities,
      name: 'Priority',
      axisLabel: { interval: 0 }
    },
    visualMap: {
      min: 1,
      max: 3,
      calculable: true,
      orient: 'vertical',
      left: 'left',
      inRange: {
        color: ['#67c23a', '#e6a23c', '#f56c6c']
      },
      text: ['3 Levels', '1 Level']
    },
    series: [{
      name: 'Approval Levels',
      type: 'heatmap',
      data: heatmapData,
      label: {
        show: true,
        formatter: (params: any) => {
          return `${params.value[2]} level${params.value[2] > 1 ? 's' : ''}`
        }
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }

  heatmapChart.setOption(option)
  window.addEventListener('resize', () => heatmapChart?.resize())
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
  filters.decisionType = ''
  filters.priority = ''
  filters.status = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleRefreshMatrix = () => {
  initHeatmapChart()
  ElMessage.success('Matrix refreshed')
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredRules.value.length} approval rules...`)
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
    id: Date.now(),
    ruleName: '',
    decisionType: '',
    priority: 'Medium',
    approvalLevels: [{ name: 'Level 1', minApprovers: 1, approvers: [] }],
    requiredApprovers: [],
    escalationTime: 48,
    status: 'Draft',
    description: '',
    createdAt: new Date().toISOString().split('T')[0],
    updatedAt: new Date().toISOString().split('T')[0]
  })
  dialogVisible.value = true
}

const viewRule = (row: ApprovalRule) => {
  dialogMode.value = 'view'
  Object.assign(formData, JSON.parse(JSON.stringify(row)))
  dialogVisible.value = true
}

const editRule = (row: ApprovalRule) => {
  dialogMode.value = 'edit'
  Object.assign(formData, JSON.parse(JSON.stringify(row)))
  dialogVisible.value = true
}

const deleteRule = (row: ApprovalRule) => {
  deleteTarget.value = row
  deleteDialogVisible.value = true
}

const activateRule = (row: ApprovalRule) => {
  ElMessageBox.confirm(`Activate approval rule "${row.ruleName}"?`, 'Activate Confirmation', {
    confirmButtonText: 'Activate',
    cancelButtonText: 'Cancel',
    type: 'success'
  }).then(() => {
    const index = approvalRules.value.findIndex(r => r.id === row.id)
    if (index !== -1) {
      approvalRules.value[index].status = 'Active'
      approvalRules.value[index].updatedAt = new Date().toISOString().split('T')[0]
      ElMessage.success(`Activated: ${row.ruleName}`)
    }
  }).catch(() => {})
}

const confirmDelete = () => {
  if (deleteTarget.value) {
    const index = approvalRules.value.findIndex(r => r.id === deleteTarget.value!.id)
    if (index !== -1) {
      approvalRules.value.splice(index, 1)
      ElMessage.success(`Deleted: ${deleteTarget.value.ruleName}`)
    }
  }
  deleteDialogVisible.value = false
  deleteTarget.value = null
}

const addApprovalLevel = () => {
  formData.approvalLevels.push({
    name: `Level ${formData.approvalLevels.length + 1}`,
    minApprovers: 1,
    approvers: []
  })
}

const removeApprovalLevel = (index: number) => {
  formData.approvalLevels.splice(index, 1)
  formData.approvalLevels.forEach((level, idx) => {
    level.name = `Level ${idx + 1}`
  })
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      const allApproverIds = formData.approvalLevels.flatMap(level => level.approvers)
      const uniqueApproverIds = [...new Set(allApproverIds)]
      formData.requiredApprovers = uniqueApproverIds.map(id => {
        return availableApprovers.value.find(a => a.id === id)!
      }).filter(a => a)

      formData.updatedAt = new Date().toISOString().split('T')[0]

      if (dialogMode.value === 'create') {
        formData.createdAt = new Date().toISOString().split('T')[0]
        approvalRules.value.unshift({ ...formData, id: Date.now() })
        ElMessage.success('Approval rule created successfully')
      } else if (dialogMode.value === 'edit') {
        const index = approvalRules.value.findIndex(r => r.id === formData.id)
        if (index !== -1) {
          approvalRules.value[index] = { ...formData }
          ElMessage.success('Approval rule updated successfully')
        }
      }
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
    initHeatmapChart()
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
.approval-matrix-page {
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

.heatmap-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}

.heatmap-container {
  width: 100%;
  height: 420px;
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

.approval-levels-section {
  width: 100%;

  .approval-level-item {
    margin-bottom: 16px;

    .level-card {
      .level-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid #ebeef5;

        .level-name {
          font-weight: 600;
          color: #303133;
        }
      }

      .level-content {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        align-items: center;

        .level-field {
          display: flex;
          align-items: center;
          gap: 12px;

          .field-label {
            font-size: 13px;
            color: #606266;
            white-space: nowrap;
          }
        }
      }
    }
  }
}

.approver-item {
  padding: 4px 0;
  font-size: 13px;

  strong {
    color: #303133;
  }
}

.na-text {
  color: #c0c4cc;
  font-style: italic;
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

:deep(.el-divider__text) {
  font-weight: 600;
  color: #409eff;
}
</style>