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
        <div class="loading-tip">AI Governance - Approval Rules</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="approval-rules-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Approval Rules</h1>
        <p>Define and manage approval workflows for AI decisions, autonomous actions, and governance events</p>
      </div>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        Create Rule
      </el-button>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon primary-bg">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalRules }}</div>
            <div class="stat-label">Total Rules</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.activeRules }}</div>
            <div class="stat-label">Active Rules</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.pendingApprovals }}</div>
            <div class="stat-label">Pending Approvals</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon info-bg">
            <el-icon><DataLine /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.avgApprovalTime }}</div>
            <div class="stat-label">Avg Approval Time</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <el-input
          v-model="filters.search"
          placeholder="Search by rule name or description..."
          clearable
          style="width: 280px"
          :prefix-icon="Search"
      />
      <el-select v-model="filters.status" placeholder="Status" clearable style="width: 140px">
        <el-option label="All Status" value="" />
        <el-option label="Active" value="ACTIVE" />
        <el-option label="Inactive" value="INACTIVE" />
        <el-option label="Draft" value="DRAFT" />
      </el-select>
      <el-select v-model="filters.priority" placeholder="Priority" clearable style="width: 140px">
        <el-option label="All Priorities" value="" />
        <el-option label="Critical" value="CRITICAL" />
        <el-option label="High" value="HIGH" />
        <el-option label="Medium" value="MEDIUM" />
        <el-option label="Low" value="LOW" />
      </el-select>
      <el-button type="primary" @click="handleSearch">
        <el-icon><Search /></el-icon>
        Apply Filters
      </el-button>
      <el-button @click="resetFilters">
        <el-icon><RefreshLeft /></el-icon>
        Reset
      </el-button>
    </div>

    <!-- Rules Table -->
    <div class="rules-table-wrapper">
      <el-table :data="filteredRules" v-loading="tableLoading" stripe style="width: 100%">
        <el-table-column prop="name" label="Rule Name" min-width="200">
          <template #default="{ row }">
            <div class="rule-name-cell">
              <span class="rule-name">{{ row.name }}</span>
              <el-tag v-if="row.isDefault" type="info" size="small" class="default-badge">Default</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="Description" min-width="250" show-overflow-tooltip />
        <el-table-column prop="eventType" label="Event Type" width="160">
          <template #default="{ row }">
            <el-tag :type="getEventTypeTagType(row.eventType)" size="small">
              {{ formatEventType(row.eventType) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="Priority" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityTagType(row.priority)" size="small">
              {{ row.priority }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-switch
                v-model="row.status"
                active-value="ACTIVE"
                inactive-value="INACTIVE"
                active-text="Active"
                inactive-text="Inactive"
                @change="toggleRuleStatus(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="approvers" label="Approvers" width="180">
          <template #default="{ row }">
            <el-popover placement="bottom" :width="200" trigger="hover">
              <template #reference>
                <div class="approvers-preview">
                  <el-avatar-group :size="28" :max="3">
                    <el-avatar v-for="(approver, idx) in row.approvers.slice(0, 3)" :key="idx">
                      {{ getAvatarInitial(approver) }}
                    </el-avatar>
                  </el-avatar-group>
                  <span v-if="row.approvers.length > 3" class="more-count">+{{ row.approvers.length - 3 }}</span>
                </div>
              </template>
              <div class="approvers-list">
                <div v-for="approver in row.approvers" :key="approver" class="approver-item">
                  <el-icon><User /></el-icon>
                  <span>{{ approver }}</span>
                </div>
              </div>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column prop="threshold" label="Threshold" width="120">
          <template #default="{ row }">
            <span v-if="row.threshold">{{ row.threshold.type }} ≥ {{ row.threshold.value }}</span>
            <span v-else class="text-muted">No threshold</span>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="Created" width="160">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="editRule(row)">
              <el-icon><Edit /></el-icon>
              Edit
            </el-button>
            <el-button link type="danger" size="small" @click="deleteRule(row)">
              <el-icon><Delete /></el-icon>
              Delete
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Create/Edit Rule Dialog -->
    <el-dialog
        v-model="dialog.visible"
        :title="dialog.isEdit ? 'Edit Approval Rule' : 'Create Approval Rule'"
        width="700px"
        @close="resetForm"
    >
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="140px">
        <el-form-item label="Rule Name" prop="name">
          <el-input v-model="form.name" placeholder="Enter rule name" />
        </el-form-item>

        <el-form-item label="Description" prop="description">
          <el-input
              v-model="form.description"
              type="textarea"
              :rows="2"
              placeholder="Enter rule description"
          />
        </el-form-item>

        <el-form-item label="Event Type" prop="eventType">
          <el-select v-model="form.eventType" placeholder="Select event type" style="width: 100%">
            <el-option label="AI Decision" value="AI_DECISION" />
            <el-option label="Model Invocation" value="MODEL_INVOCATION" />
            <el-option label="Data Access" value="DATA_ACCESS" />
            <el-option label="Policy Change" value="POLICY_CHANGE" />
            <el-option label="Autonomous Action" value="AUTONOMOUS_ACTION" />
          </el-select>
        </el-form-item>

        <el-form-item label="Priority" prop="priority">
          <el-select v-model="form.priority" placeholder="Select priority" style="width: 100%">
            <el-option label="Critical" value="CRITICAL" />
            <el-option label="High" value="HIGH" />
            <el-option label="Medium" value="MEDIUM" />
            <el-option label="Low" value="LOW" />
          </el-select>
        </el-form-item>

        <el-form-item label="Approval Threshold" prop="threshold">
          <el-row :gutter="12">
            <el-col :span="12">
              <el-select v-model="form.threshold.type" placeholder="Threshold type">
                <el-option label="Confidence Score" value="CONFIDENCE" />
                <el-option label="Impact Score" value="IMPACT" />
                <el-option label="Risk Score" value="RISK" />
                <el-option label="Cost Impact" value="COST" />
              </el-select>
            </el-col>
            <el-col :span="12">
              <el-input-number
                  v-model="form.threshold.value"
                  :min="0"
                  :max="100"
                  placeholder="Value"
                  style="width: 100%"
              />
            </el-col>
          </el-row>
          <div class="form-hint">Approval is required when the selected metric reaches or exceeds this value</div>
        </el-form-item>

        <el-form-item label="Required Approvers" prop="approvers">
          <el-select
              v-model="form.approvers"
              multiple
              filterable
              allow-create
              default-first-option
              placeholder="Select or enter approver email"
              style="width: 100%"
          >
            <el-option
                v-for="user in availableApprovers"
                :key="user.email"
                :label="user.name"
                :value="user.email"
            >
              <span>{{ user.name }}</span>
              <span style="float: right; color: #8c9aab; font-size: 12px">{{ user.role }}</span>
            </el-option>
          </el-select>
          <div class="form-hint">At least one approver is required</div>
        </el-form-item>

        <el-form-item label="Approval Method" prop="approvalMethod">
          <el-radio-group v-model="form.approvalMethod">
            <el-radio value="ANY">Any Approver</el-radio>
            <el-radio value="ALL">All Approvers</el-radio>
            <el-radio value="MAJORITY">Majority Vote</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="Escalation" prop="escalationMinutes">
          <el-input-number
              v-model="form.escalationMinutes"
              :min="0"
              :step="30"
              placeholder="Minutes"
          />
          <span style="margin-left: 8px; color: #8c9aab">minutes (0 = no escalation)</span>
        </el-form-item>

        <el-form-item label="Auto-Approval" prop="autoApproval">
          <el-switch v-model="form.autoApproval" />
          <span style="margin-left: 8px; color: #8c9aab">Automatically approve when confidence > 95%</span>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialog.visible = false">Cancel</el-button>
        <el-button type="primary" @click="saveRule">Save Rule</el-button>
      </template>
    </el-dialog>

    <!-- Delete Confirmation -->
    <el-dialog v-model="deleteDialog.visible" title="Delete Rule" width="400px">
      <p>Are you sure you want to delete the rule <strong>{{ deleteDialog.rule?.name }}</strong>?</p>
      <p class="delete-warning">This action cannot be undone.</p>
      <template #footer>
        <el-button @click="deleteDialog.visible = false">Cancel</el-button>
        <el-button type="danger" @click="confirmDelete">Delete</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import {
  Plus,
  Search,
  RefreshLeft,
  Document,
  CircleCheck,
  Clock,
  DataLine,
  Edit,
  Delete,
  User
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading approval rules...',
  'Initializing workflow engine...',
  'Almost ready...'
]

// ==================== Type Definitions ====================
interface ApprovalRule {
  id: string
  name: string
  description: string
  eventType: string
  priority: string
  status: string
  approvers: string[]
  threshold: {
    type: string
    value: number
  } | null
  approvalMethod: string
  escalationMinutes: number
  autoApproval: boolean
  isDefault: boolean
  createdAt: Date
  updatedAt: Date
  createdBy: string
}

interface ApprovalForm {
  name: string
  description: string
  eventType: string
  priority: string
  threshold: {
    type: string
    value: number
  }
  approvers: string[]
  approvalMethod: string
  escalationMinutes: number
  autoApproval: boolean
}

// ==================== 模拟数据生成 ====================
const generateMockRules = (): ApprovalRule[] => {
  const rules: ApprovalRule[] = [
    {
      id: 'RUL-001',
      name: 'Critical AI Decision Approval',
      description: 'Requires approval for any AI decision with high business impact',
      eventType: 'AI_DECISION',
      priority: 'CRITICAL',
      status: 'ACTIVE',
      approvers: ['head-ai@ibms.com', 'chief-architect@ibms.com'],
      threshold: { type: 'IMPACT', value: 80 },
      approvalMethod: 'ALL',
      escalationMinutes: 60,
      autoApproval: false,
      isDefault: true,
      createdAt: new Date('2024-01-15'),
      updatedAt: new Date('2024-01-15'),
      createdBy: 'system'
    },
    {
      id: 'RUL-002',
      name: 'Model Deployment Approval',
      description: 'Approval required for deploying new or updated AI models to production',
      eventType: 'MODEL_INVOCATION',
      priority: 'HIGH',
      status: 'ACTIVE',
      approvers: ['ml-ops@ibms.com', 'security@ibms.com'],
      threshold: null,
      approvalMethod: 'ANY',
      escalationMinutes: 120,
      autoApproval: false,
      isDefault: true,
      createdAt: new Date('2024-01-20'),
      updatedAt: new Date('2024-01-20'),
      createdBy: 'system'
    },
    {
      id: 'RUL-003',
      name: 'Sensitive Data Access',
      description: 'Approval needed for accessing PII or sensitive operational data',
      eventType: 'DATA_ACCESS',
      priority: 'HIGH',
      status: 'ACTIVE',
      approvers: ['data-governance@ibms.com', 'compliance@ibms.com'],
      threshold: { type: 'RISK', value: 70 },
      approvalMethod: 'ALL',
      escalationMinutes: 30,
      autoApproval: false,
      isDefault: true,
      createdAt: new Date('2024-02-01'),
      updatedAt: new Date('2024-02-01'),
      createdBy: 'system'
    },
    {
      id: 'RUL-004',
      name: 'Policy Change Authorization',
      description: 'Changes to AI governance policies require leadership approval',
      eventType: 'POLICY_CHANGE',
      priority: 'CRITICAL',
      status: 'ACTIVE',
      approvers: ['cpo@ibms.com', 'legal@ibms.com', 'cto@ibms.com'],
      threshold: null,
      approvalMethod: 'ALL',
      escalationMinutes: 240,
      autoApproval: false,
      isDefault: true,
      createdAt: new Date('2024-02-10'),
      updatedAt: new Date('2024-02-10'),
      createdBy: 'system'
    },
    {
      id: 'RUL-005',
      name: 'Low Confidence Decisions',
      description: 'AI decisions with confidence below threshold require human review',
      eventType: 'AI_DECISION',
      priority: 'MEDIUM',
      status: 'ACTIVE',
      approvers: ['ops-lead@ibms.com'],
      threshold: { type: 'CONFIDENCE', value: 85 },
      approvalMethod: 'ANY',
      escalationMinutes: 90,
      autoApproval: true,
      isDefault: false,
      createdAt: new Date('2024-02-20'),
      updatedAt: new Date('2024-02-20'),
      createdBy: 'john.doe@ibms.com'
    },
    {
      id: 'RUL-006',
      name: 'Autonomous Action Review',
      description: 'Review required for autonomous actions with cost impact',
      eventType: 'AUTONOMOUS_ACTION',
      priority: 'HIGH',
      status: 'ACTIVE',
      approvers: ['finance@ibms.com', 'ops-manager@ibms.com'],
      threshold: { type: 'COST', value: 5000 },
      approvalMethod: 'MAJORITY',
      escalationMinutes: 60,
      autoApproval: false,
      isDefault: false,
      createdAt: new Date('2024-03-01'),
      updatedAt: new Date('2024-03-01'),
      createdBy: 'jane.smith@ibms.com'
    },
    {
      id: 'RUL-007',
      name: 'Experimental Model Testing',
      description: 'Approval for testing experimental models in staging environment',
      eventType: 'MODEL_INVOCATION',
      priority: 'LOW',
      status: 'INACTIVE',
      approvers: ['ml-ops@ibms.com'],
      threshold: null,
      approvalMethod: 'ANY',
      escalationMinutes: 0,
      autoApproval: true,
      isDefault: false,
      createdAt: new Date('2024-03-10'),
      updatedAt: new Date('2024-03-10'),
      createdBy: 'alex.chen@ibms.com'
    },
    {
      id: 'RUL-008',
      name: 'Emergency Override',
      description: 'Special rule for emergency situations requiring quick action',
      eventType: 'AI_DECISION',
      priority: 'CRITICAL',
      status: 'ACTIVE',
      approvers: ['oncall-engineer@ibms.com', 'duty-manager@ibms.com'],
      threshold: null,
      approvalMethod: 'ANY',
      escalationMinutes: 15,
      autoApproval: false,
      isDefault: false,
      createdAt: new Date('2024-03-15'),
      updatedAt: new Date('2024-03-15'),
      createdBy: 'admin@ibms.com'
    }
  ]
  return rules
}

// Available approvers for dropdown
const availableApprovers = [
  { name: 'John Doe', email: 'john.doe@ibms.com', role: 'AI Architect' },
  { name: 'Jane Smith', email: 'jane.smith@ibms.com', role: 'ML Ops Lead' },
  { name: 'Alex Chen', email: 'alex.chen@ibms.com', role: 'Data Scientist' },
  { name: 'Sarah Wang', email: 'sarah.wang@ibms.com', role: 'Product Manager' },
  { name: 'Mike Johnson', email: 'mike.johnson@ibms.com', role: 'Security Analyst' },
  { name: 'Lisa Zhang', email: 'lisa.zhang@ibms.com', role: 'Compliance Officer' },
  { name: 'head-ai@ibms.com', email: 'head-ai@ibms.com', role: 'Head of AI' },
  { name: 'chief-architect@ibms.com', email: 'chief-architect@ibms.com', role: 'Chief Architect' },
  { name: 'ml-ops@ibms.com', email: 'ml-ops@ibms.com', role: 'ML Ops' },
  { name: 'security@ibms.com', email: 'security@ibms.com', role: 'Security' },
  { name: 'data-governance@ibms.com', email: 'data-governance@ibms.com', role: 'Data Governance' },
  { name: 'compliance@ibms.com', email: 'compliance@ibms.com', role: 'Compliance' },
  { name: 'cpo@ibms.com', email: 'cpo@ibms.com', role: 'CPO' },
  { name: 'legal@ibms.com', email: 'legal@ibms.com', role: 'Legal' },
  { name: 'cto@ibms.com', email: 'cto@ibms.com', role: 'CTO' },
  { name: 'ops-lead@ibms.com', email: 'ops-lead@ibms.com', role: 'Ops Lead' },
  { name: 'finance@ibms.com', email: 'finance@ibms.com', role: 'Finance' },
  { name: 'ops-manager@ibms.com', email: 'ops-manager@ibms.com', role: 'Ops Manager' }
]

// ==================== 响应式状态 ====================
const allRules = ref<ApprovalRule[]>([])
const formRef = ref<FormInstance>()

const filters = reactive({
  search: '',
  status: '',
  priority: ''
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

const dialog = reactive({
  visible: false,
  isEdit: false,
  editId: ''
})

const deleteDialog = reactive({
  visible: false,
  rule: null as ApprovalRule | null
})

const form = reactive<ApprovalForm>({
  name: '',
  description: '',
  eventType: 'AI_DECISION',
  priority: 'MEDIUM',
  threshold: { type: 'CONFIDENCE', value: 80 },
  approvers: [],
  approvalMethod: 'ANY',
  escalationMinutes: 60,
  autoApproval: false
})

const formRules: FormRules = {
  name: [{ required: true, message: 'Rule name is required', trigger: 'blur' }],
  description: [{ required: true, message: 'Description is required', trigger: 'blur' }],
  eventType: [{ required: true, message: 'Event type is required', trigger: 'change' }],
  priority: [{ required: true, message: 'Priority is required', trigger: 'change' }],
  approvers: [{ required: true, message: 'At least one approver is required', trigger: 'change', type: 'array', min: 1 }]
}

// 统计数据
const stats = reactive({
  totalRules: 0,
  activeRules: 0,
  pendingApprovals: 0,
  avgApprovalTime: '2.4 hrs'
})

// ==================== 计算属性 ====================
const filteredRules = computed(() => {
  let filtered = [...allRules.value]

  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    filtered = filtered.filter(rule =>
        rule.name.toLowerCase().includes(searchLower) ||
        rule.description.toLowerCase().includes(searchLower)
    )
  }

  if (filters.status) {
    filtered = filtered.filter(rule => rule.status === filters.status)
  }

  if (filters.priority) {
    filtered = filtered.filter(rule => rule.priority === filters.priority)
  }

  pagination.total = filtered.length

  const start = (pagination.currentPage - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// ==================== 辅助函数 ====================
const formatEventType = (type: string) => {
  const map: Record<string, string> = {
    'AI_DECISION': 'AI Decision',
    'MODEL_INVOCATION': 'Model Invocation',
    'DATA_ACCESS': 'Data Access',
    'POLICY_CHANGE': 'Policy Change',
    'AUTONOMOUS_ACTION': 'Autonomous Action'
  }
  return map[type] || type
}

const getEventTypeTagType = (type: string) => {
  const map: Record<string, string> = {
    'AI_DECISION': 'primary',
    'MODEL_INVOCATION': 'success',
    'DATA_ACCESS': 'info',
    'POLICY_CHANGE': 'warning',
    'AUTONOMOUS_ACTION': 'danger'
  }
  return map[type] || 'info'
}

const getPriorityTagType = (priority: string) => {
  const map: Record<string, string> = {
    'CRITICAL': 'danger',
    'HIGH': 'danger',
    'MEDIUM': 'warning',
    'LOW': 'info'
  }
  return map[priority] || 'info'
}

const formatDate = (date: Date) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const getAvatarInitial = (email: string) => {
  const name = email.split('@')[0]
  return name.substring(0, 2).toUpperCase()
}

const updateStats = () => {
  const rules = allRules.value
  stats.totalRules = rules.length
  stats.activeRules = rules.filter(r => r.status === 'ACTIVE').length
  stats.pendingApprovals = Math.floor(Math.random() * 15) + 5 // Simulated
}

// ==================== 交互事件 ====================
const handleSearch = () => {
  pagination.currentPage = 1
  ElMessage.success('Filters applied successfully')
}

const resetFilters = () => {
  filters.search = ''
  filters.status = ''
  filters.priority = ''
  pagination.currentPage = 1
  ElMessage.info('All filters have been reset')
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.currentPage = 1
}

const handleCurrentChange = (page: number) => {
  pagination.currentPage = page
}

const toggleRuleStatus = (rule: ApprovalRule) => {
  const newStatus = rule.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE'
  rule.status = newStatus
  rule.updatedAt = new Date()
  ElMessage.success(`Rule "${rule.name}" is now ${newStatus.toLowerCase()}`)
  updateStats()
}

const openCreateDialog = () => {
  dialog.isEdit = false
  dialog.editId = ''
  resetForm()
  dialog.visible = true
}

const editRule = (rule: ApprovalRule) => {
  dialog.isEdit = true
  dialog.editId = rule.id
  form.name = rule.name
  form.description = rule.description
  form.eventType = rule.eventType
  form.priority = rule.priority
  form.threshold = rule.threshold || { type: 'CONFIDENCE', value: 80 }
  form.approvers = [...rule.approvers]
  form.approvalMethod = rule.approvalMethod
  form.escalationMinutes = rule.escalationMinutes
  form.autoApproval = rule.autoApproval
  dialog.visible = true
}

const deleteRule = (rule: ApprovalRule) => {
  deleteDialog.rule = rule
  deleteDialog.visible = true
}

const confirmDelete = () => {
  if (deleteDialog.rule) {
    const index = allRules.value.findIndex(r => r.id === deleteDialog.rule!.id)
    if (index !== -1) {
      allRules.value.splice(index, 1)
      ElMessage.success(`Rule "${deleteDialog.rule.name}" deleted successfully`)
      updateStats()
    }
  }
  deleteDialog.visible = false
  deleteDialog.rule = null
}

const resetForm = () => {
  form.name = ''
  form.description = ''
  form.eventType = 'AI_DECISION'
  form.priority = 'MEDIUM'
  form.threshold = { type: 'CONFIDENCE', value: 80 }
  form.approvers = []
  form.approvalMethod = 'ANY'
  form.escalationMinutes = 60
  form.autoApproval = false
  formRef.value?.clearValidate()
}

const saveRule = async () => {
  if (!formRef.value) return

  await formRef.value.validate((valid) => {
    if (valid) {
      if (dialog.isEdit) {
        // Update existing rule
        const index = allRules.value.findIndex(r => r.id === dialog.editId)
        if (index !== -1) {
          allRules.value[index] = {
            ...allRules.value[index],
            name: form.name,
            description: form.description,
            eventType: form.eventType,
            priority: form.priority,
            threshold: form.threshold,
            approvers: form.approvers,
            approvalMethod: form.approvalMethod,
            escalationMinutes: form.escalationMinutes,
            autoApproval: form.autoApproval,
            updatedAt: new Date()
          }
          ElMessage.success('Rule updated successfully')
        }
      } else {
        // Create new rule
        const newRule: ApprovalRule = {
          id: `RUL-${String(allRules.value.length + 1).padStart(3, '0')}`,
          name: form.name,
          description: form.description,
          eventType: form.eventType,
          priority: form.priority,
          status: 'ACTIVE',
          approvers: form.approvers,
          threshold: form.threshold,
          approvalMethod: form.approvalMethod,
          escalationMinutes: form.escalationMinutes,
          autoApproval: form.autoApproval,
          isDefault: false,
          createdAt: new Date(),
          updatedAt: new Date(),
          createdBy: 'admin@ibms.com'
        }
        allRules.value.unshift(newRule)
        ElMessage.success('Rule created successfully')
      }
      dialog.visible = false
      updateStats()
      resetForm()
    }
  })
}

// ==================== 数据加载 ====================
const loadData = () => {
  tableLoading.value = true
  setTimeout(() => {
    allRules.value = generateMockRules()
    updateStats()
    tableLoading.value = false
  }, 300)
}

// ==================== 生命周期 ====================
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
      loadData()
    }, 400)
  }, 2000)
})
</script>

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

/* ==================== Main Content Styles ==================== */
.approval-rules-page {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #1f2f3d;
}

.page-header p {
  margin: 0;
  color: #5e6e82;
  font-size: 14px;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.primary-bg { background-color: #ecf5ff; color: #409eff; }
.success-bg { background-color: #f0f9eb; color: #67c23a; }
.warning-bg { background-color: #fff3e0; color: #e6a23c; }
.info-bg { background-color: #f5f7fa; color: #8c9aab; }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #8c9aab;
  margin-top: 4px;
}

.filter-bar {
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.rules-table-wrapper {
  background: white;
  border-radius: 12px;
  padding: 0;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.rule-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rule-name {
  font-weight: 500;
  color: #1f2f3d;
}

.default-badge {
  font-size: 10px;
}

.approvers-preview {
  display: flex;
  align-items: center;
  gap: 4px;
}

.more-count {
  font-size: 12px;
  color: #8c9aab;
  margin-left: 4px;
}

.approvers-list {
  max-height: 200px;
  overflow-y: auto;
}

.approver-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  font-size: 13px;
}

.text-muted {
  color: #c0c4cc;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 16px 20px;
  border-top: 1px solid #ebeef5;
}

.form-hint {
  font-size: 12px;
  color: #8c9aab;
  margin-top: 4px;
}

.delete-warning {
  color: #f56c6c;
  font-size: 13px;
  margin-top: 8px;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
  color: #1f2f3d;
}

:deep(.el-table td) {
  font-size: 13px;
}

:deep(.el-dialog__body) {
  padding-top: 0;
  max-height: 60vh;
  overflow-y: auto;
}
</style>