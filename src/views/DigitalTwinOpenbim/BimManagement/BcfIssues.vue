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
        <div class="loading-tip">BIM Management - BCF Issues</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="bcf-issues-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>BCF Issues</h1>
        <p>BIM Collaboration Format (BCF) issue tracking and resolution management</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          Create Issue
        </el-button>
        <el-button @click="exportIssues">
          <el-icon><Download /></el-icon>
          Export BCF
        </el-button>
        <el-button @click="importBCF">
          <el-icon><Upload /></el-icon>
          Import BCF
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon primary-bg">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalIssues }}</div>
            <div class="stat-label">Total Issues</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.openIssues }}</div>
            <div class="stat-label">Open Issues</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.closedIssues }}</div>
            <div class="stat-label">Closed Issues</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon info-bg">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.avgResolutionTime }}d</div>
            <div class="stat-label">Avg Resolution Time</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <el-input
          v-model="filters.search"
          placeholder="Search by title, ID, or description..."
          clearable
          style="width: 260px"
          :prefix-icon="Search"
      />
      <el-select v-model="filters.status" placeholder="Status" clearable style="width: 130px">
        <el-option label="All" value="" />
        <el-option label="Open" value="open" />
        <el-option label="In Progress" value="in-progress" />
        <el-option label="Closed" value="closed" />
      </el-select>
      <el-select v-model="filters.priority" placeholder="Priority" clearable style="width: 130px">
        <el-option label="All" value="" />
        <el-option label="Critical" value="critical" />
        <el-option label="High" value="high" />
        <el-option label="Medium" value="medium" />
        <el-option label="Low" value="low" />
      </el-select>
      <el-select v-model="filters.assignedTo" placeholder="Assigned To" clearable style="width: 160px">
        <el-option label="All" value="" />
        <el-option v-for="user in teamMembers" :key="user" :label="user" :value="user" />
      </el-select>
      <el-date-picker
          v-model="filters.dateRange"
          type="daterange"
          range-separator="to"
          start-placeholder="Start Date"
          end-placeholder="End Date"
          style="width: 280px"
      />
      <el-button type="primary" @click="handleSearch">
        <el-icon><Search /></el-icon>
        Apply
      </el-button>
      <el-button @click="resetFilters">
        <el-icon><RefreshLeft /></el-icon>
        Reset
      </el-button>
    </div>

    <!-- Issues Table -->
    <div class="issues-table-wrapper">
      <el-table :data="filteredIssues" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="id" label="Issue ID" width="100" />
        <el-table-column prop="title" label="Title" min-width="250" show-overflow-tooltip />
        <el-table-column prop="priority" label="Priority" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityTagType(row.priority)" size="small">
              {{ row.priority }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assignedTo" label="Assigned To" width="140" />
        <el-table-column prop="createdDate" label="Created" width="110" />
        <el-table-column prop="dueDate" label="Due Date" width="110">
          <template #default="{ row }">
            <span :class="{ overdue: isOverdue(row.dueDate) && row.status !== 'closed' }">
              {{ row.dueDate }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewIssue(row)">
              View
            </el-button>
            <el-button link type="success" size="small" @click="editIssue(row)">
              Edit
            </el-button>
            <el-button link type="danger" size="small" @click="deleteIssue(row)">
              Delete
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Create/Edit Issue Dialog -->
    <el-dialog
        v-model="dialog.visible"
        :title="dialog.isEdit ? 'Edit Issue' : 'Create New Issue'"
        width="650px"
        @close="resetForm"
    >
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="110px">
        <el-form-item label="Title" prop="title">
          <el-input v-model="form.title" placeholder="Enter issue title" />
        </el-form-item>

        <el-form-item label="Description" prop="description">
          <el-input
              v-model="form.description"
              type="textarea"
              :rows="3"
              placeholder="Describe the issue in detail..."
          />
        </el-form-item>

        <el-form-item label="Priority" prop="priority">
          <el-select v-model="form.priority" placeholder="Select priority" style="width: 100%">
            <el-option label="Critical" value="critical" />
            <el-option label="High" value="high" />
            <el-option label="Medium" value="medium" />
            <el-option label="Low" value="low" />
          </el-select>
        </el-form-item>

        <el-form-item label="Status" prop="status">
          <el-select v-model="form.status" placeholder="Select status" style="width: 100%">
            <el-option label="Open" value="open" />
            <el-option label="In Progress" value="in-progress" />
            <el-option label="Closed" value="closed" />
          </el-select>
        </el-form-item>

        <el-form-item label="Assigned To" prop="assignedTo">
          <el-select v-model="form.assignedTo" placeholder="Select assignee" style="width: 100%">
            <el-option v-for="user in teamMembers" :key="user" :label="user" :value="user" />
          </el-select>
        </el-form-item>

        <el-form-item label="Due Date" prop="dueDate">
          <el-date-picker v-model="form.dueDate" type="date" placeholder="Select due date" style="width: 100%" />
        </el-form-item>

        <el-form-item label="Related IFC Element">
          <el-select v-model="form.relatedElement" placeholder="Select IFC element" clearable style="width: 100%">
            <el-option label="Wall - W-101" value="W-101" />
            <el-option label="Column - C-205" value="C-205" />
            <el-option label="Door - D-102" value="D-102" />
            <el-option label="HVAC - AHU-05" value="AHU-05" />
            <el-option label="Electrical Panel - EP-01" value="EP-01" />
          </el-select>
        </el-form-item>

        <el-form-item label="Comments">
          <el-input
              v-model="form.comments"
              type="textarea"
              :rows="2"
              placeholder="Add comments..."
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialog.visible = false">Cancel</el-button>
        <el-button type="primary" @click="saveIssue">Save Issue</el-button>
      </template>
    </el-dialog>

    <!-- View Issue Dialog -->
    <el-dialog v-model="viewDialog.visible" :title="`Issue ${viewDialog.issue?.id}: ${viewDialog.issue?.title}`" width="700px">
      <div v-if="viewDialog.issue" class="issue-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Issue ID">{{ viewDialog.issue.id }}</el-descriptions-item>
          <el-descriptions-item label="Priority">
            <el-tag :type="getPriorityTagType(viewDialog.issue.priority)" size="small">
              {{ viewDialog.issue.priority }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(viewDialog.issue.status)" size="small">
              {{ getStatusLabel(viewDialog.issue.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Assigned To">{{ viewDialog.issue.assignedTo }}</el-descriptions-item>
          <el-descriptions-item label="Created By">{{ viewDialog.issue.createdBy }}</el-descriptions-item>
          <el-descriptions-item label="Created Date">{{ viewDialog.issue.createdDate }}</el-descriptions-item>
          <el-descriptions-item label="Due Date">{{ viewDialog.issue.dueDate }}</el-descriptions-item>
          <el-descriptions-item label="Closed Date">{{ viewDialog.issue.closedDate || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">
            <div class="description-text">{{ viewDialog.issue.description }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="Related Element" :span="2">
            <el-tag v-if="viewDialog.issue.relatedElement" type="info" size="small">
              {{ viewDialog.issue.relatedElement }}
            </el-tag>
            <span v-else>None</span>
          </el-descriptions-item>
          <el-descriptions-item label="Comments" :span="2">
            <div class="comments-section">
              <div v-for="(comment, idx) in viewDialog.issue.commentsHistory" :key="idx" class="comment-item">
                <strong>{{ comment.user }}</strong>
                <span class="comment-time">{{ comment.date }}</span>
                <p>{{ comment.text }}</p>
              </div>
              <el-input v-model="newComment" type="textarea" :rows="2" placeholder="Add a comment..." />
              <el-button type="primary" size="small" @click="addComment" style="margin-top: 8px">Add Comment</el-button>
            </div>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <template #footer>
        <el-button @click="viewDialog.visible = false">Close</el-button>
        <el-button v-if="viewDialog.issue?.status !== 'closed'" type="primary" @click="updateStatus('in-progress')">
          Start Progress
        </el-button>
        <el-button v-if="viewDialog.issue?.status === 'in-progress'" type="success" @click="updateStatus('closed')">
          Close Issue
        </el-button>
      </template>
    </el-dialog>

    <!-- Delete Confirmation -->
    <el-dialog v-model="deleteDialog.visible" title="Delete Issue" width="400px">
      <p>Are you sure you want to delete issue <strong>{{ deleteDialog.issue?.title }}</strong>?</p>
      <p class="delete-warning">This action cannot be undone.</p>
      <template #footer>
        <el-button @click="deleteDialog.visible = false">Cancel</el-button>
        <el-button type="danger" @click="confirmDelete">Delete</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import {
  Plus,
  Download,
  Upload,
  Document,
  Warning,
  CircleCheck,
  Clock,
  Search,
  RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading BCF issues...',
  'Initializing issue tracker...',
  'Almost ready...'
]

// ==================== Type Definitions ====================
interface BCFIssue {
  id: string
  title: string
  description: string
  priority: 'critical' | 'high' | 'medium' | 'low'
  status: 'open' | 'in-progress' | 'closed'
  assignedTo: string
  createdBy: string
  createdDate: string
  dueDate: string
  closedDate: string | null
  relatedElement: string | null
  commentsHistory: Array<{ user: string; date: string; text: string }>
}

// ==================== 模拟数据 ====================
const teamMembers = ['John Smith', 'Sarah Lee', 'Mike Chen', 'Anna Zhang', 'David Kim']

const generateMockIssues = (): BCFIssue[] => {
  const now = new Date()
  return [
    {
      id: 'BCF-101',
      title: 'Wall penetration missing fire stop',
      description: 'The wall penetration at grid B-2 does not have proper fire stopping material installed.',
      priority: 'critical',
      status: 'open',
      assignedTo: 'John Smith',
      createdBy: 'Sarah Lee',
      createdDate: '2024-06-10',
      dueDate: '2024-06-20',
      closedDate: null,
      relatedElement: 'W-101',
      commentsHistory: [{ user: 'Sarah Lee', date: '2024-06-10 09:30', text: 'Issue identified during site inspection.' }]
    },
    {
      id: 'BCF-102',
      title: 'HVAC duct clashes with structural beam',
      description: 'The main supply duct interferes with the steel beam at elevation +4.5m.',
      priority: 'high',
      status: 'in-progress',
      assignedTo: 'Mike Chen',
      createdBy: 'Anna Zhang',
      createdDate: '2024-06-08',
      dueDate: '2024-06-18',
      closedDate: null,
      relatedElement: 'AHU-05',
      commentsHistory: [
        { user: 'Anna Zhang', date: '2024-06-08 14:15', text: 'Clash detected in coordination review.' },
        { user: 'Mike Chen', date: '2024-06-09 10:00', text: 'Working on rerouting solution.' }
      ]
    },
    {
      id: 'BCF-103',
      title: 'Electrical panel clearance insufficient',
      description: 'Working clearance in front of panel EP-01 does not meet code requirements (36" required).',
      priority: 'high',
      status: 'open',
      assignedTo: 'David Kim',
      createdBy: 'John Smith',
      createdDate: '2024-06-05',
      dueDate: '2024-06-15',
      closedDate: null,
      relatedElement: 'EP-01',
      commentsHistory: [{ user: 'John Smith', date: '2024-06-05 11:20', text: 'Code violation identified.' }]
    },
    {
      id: 'BCF-104',
      title: 'Missing coordination between plumbing and structural',
      description: 'Plumbing chase conflicts with column reinforcement at grid C-3.',
      priority: 'medium',
      status: 'open',
      assignedTo: 'Sarah Lee',
      createdBy: 'Mike Chen',
      createdDate: '2024-06-12',
      dueDate: '2024-06-22',
      closedDate: null,
      relatedElement: null,
      commentsHistory: [{ user: 'Mike Chen', date: '2024-06-12 08:45', text: 'Need structural team review.' }]
    },
    {
      id: 'BCF-105',
      title: 'Fire alarm device placement issue',
      description: 'Smoke detector location is within 4ft of air diffuser, violates NFPA 72.',
      priority: 'medium',
      status: 'closed',
      assignedTo: 'Anna Zhang',
      createdBy: 'John Smith',
      createdDate: '2024-05-28',
      dueDate: '2024-06-05',
      closedDate: '2024-06-04',
      relatedElement: null,
      commentsHistory: [
        { user: 'John Smith', date: '2024-05-28 13:00', text: 'Code compliance issue.' },
        { user: 'Anna Zhang', date: '2024-06-03 15:30', text: 'Relocated device per specification.' },
        { user: 'John Smith', date: '2024-06-04 09:00', text: 'Issue verified and closed.' }
      ]
    },
    {
      id: 'BCF-106',
      title: 'Door swing direction incorrect',
      description: 'Door D-102 should swing into the room per egress requirements.',
      priority: 'low',
      status: 'open',
      assignedTo: 'David Kim',
      createdBy: 'Sarah Lee',
      createdDate: '2024-06-11',
      dueDate: '2024-06-25',
      closedDate: null,
      relatedElement: 'D-102',
      commentsHistory: [{ user: 'Sarah Lee', date: '2024-06-11 10:30', text: 'Flagged in plan review.' }]
    }
  ]
}

// ==================== 响应式状态 ====================
const allIssues = ref<BCFIssue[]>([])
const formRef = ref<FormInstance>()

const filters = reactive({
  search: '',
  status: '',
  priority: '',
  assignedTo: '',
  dateRange: null as Date[] | null
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

const stats = reactive({
  totalIssues: 0,
  openIssues: 0,
  closedIssues: 0,
  avgResolutionTime: 7
})

const dialog = reactive({
  visible: false,
  isEdit: false,
  editId: ''
})

const viewDialog = reactive({
  visible: false,
  issue: null as BCFIssue | null
})

const deleteDialog = reactive({
  visible: false,
  issue: null as BCFIssue | null
})

const form = reactive({
  title: '',
  description: '',
  priority: 'medium',
  status: 'open',
  assignedTo: '',
  dueDate: '',
  relatedElement: '',
  comments: ''
})

const newComment = ref('')

const formRules: FormRules = {
  title: [{ required: true, message: 'Title is required', trigger: 'blur' }],
  description: [{ required: true, message: 'Description is required', trigger: 'blur' }],
  priority: [{ required: true, message: 'Priority is required', trigger: 'change' }],
  assignedTo: [{ required: true, message: 'Assignee is required', trigger: 'change' }],
  dueDate: [{ required: true, message: 'Due date is required', trigger: 'change' }]
}

// ==================== 计算属性 ====================
const filteredIssues = computed(() => {
  let filtered = [...allIssues.value]

  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    filtered = filtered.filter(i =>
        i.id.toLowerCase().includes(searchLower) ||
        i.title.toLowerCase().includes(searchLower) ||
        i.description.toLowerCase().includes(searchLower)
    )
  }

  if (filters.status) {
    filtered = filtered.filter(i => i.status === filters.status)
  }

  if (filters.priority) {
    filtered = filtered.filter(i => i.priority === filters.priority)
  }

  if (filters.assignedTo) {
    filtered = filtered.filter(i => i.assignedTo === filters.assignedTo)
  }

  if (filters.dateRange && filters.dateRange.length === 2) {
    const [start, end] = filters.dateRange
    filtered = filtered.filter(i => {
      const date = new Date(i.createdDate)
      return date >= start && date <= end
    })
  }

  pagination.total = filtered.length
  const start = (pagination.currentPage - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// ==================== 辅助函数 ====================
const getPriorityTagType = (priority: string) => {
  const map: Record<string, string> = {
    'critical': 'danger',
    'high': 'danger',
    'medium': 'warning',
    'low': 'info'
  }
  return map[priority] || 'info'
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    'open': 'danger',
    'in-progress': 'warning',
    'closed': 'success'
  }
  return map[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    'open': 'Open',
    'in-progress': 'In Progress',
    'closed': 'Closed'
  }
  return map[status] || status
}

const isOverdue = (dueDate: string) => {
  return new Date(dueDate) < new Date() && new Date(dueDate).setHours(0, 0, 0, 0) !== new Date().setHours(0, 0, 0, 0)
}

const updateStats = () => {
  stats.totalIssues = allIssues.value.length
  stats.openIssues = allIssues.value.filter(i => i.status !== 'closed').length
  stats.closedIssues = allIssues.value.filter(i => i.status === 'closed').length
}

// ==================== 交互事件 ====================
const handleSearch = () => {
  pagination.currentPage = 1
  ElMessage.success('Filters applied')
}

const resetFilters = () => {
  filters.search = ''
  filters.status = ''
  filters.priority = ''
  filters.assignedTo = ''
  filters.dateRange = null
  pagination.currentPage = 1
  ElMessage.info('Filters reset')
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.currentPage = 1
}

const handleCurrentChange = (page: number) => {
  pagination.currentPage = page
}

const openCreateDialog = () => {
  dialog.isEdit = false
  dialog.editId = ''
  resetForm()
  dialog.visible = true
}

const editIssue = (issue: BCFIssue) => {
  dialog.isEdit = true
  dialog.editId = issue.id
  form.title = issue.title
  form.description = issue.description
  form.priority = issue.priority
  form.status = issue.status
  form.assignedTo = issue.assignedTo
  form.dueDate = issue.dueDate
  form.relatedElement = issue.relatedElement || ''
  form.comments = ''
  dialog.visible = true
}

const viewIssue = (issue: BCFIssue) => {
  viewDialog.issue = { ...issue, commentsHistory: [...issue.commentsHistory] }
  viewDialog.visible = true
  newComment.value = ''
}

const deleteIssue = (issue: BCFIssue) => {
  deleteDialog.issue = issue
  deleteDialog.visible = true
}

const confirmDelete = () => {
  if (deleteDialog.issue) {
    const index = allIssues.value.findIndex(i => i.id === deleteDialog.issue!.id)
    if (index !== -1) {
      allIssues.value.splice(index, 1)
      updateStats()
      ElMessage.success(`Issue ${deleteDialog.issue.id} deleted`)
    }
  }
  deleteDialog.visible = false
  deleteDialog.issue = null
}

const resetForm = () => {
  form.title = ''
  form.description = ''
  form.priority = 'medium'
  form.status = 'open'
  form.assignedTo = ''
  form.dueDate = ''
  form.relatedElement = ''
  form.comments = ''
  formRef.value?.clearValidate()
}

const saveIssue = async () => {
  if (!formRef.value) return

  await formRef.value.validate((valid) => {
    if (valid) {
      if (dialog.isEdit) {
        const index = allIssues.value.findIndex(i => i.id === dialog.editId)
        if (index !== -1) {
          allIssues.value[index] = {
            ...allIssues.value[index],
            title: form.title,
            description: form.description,
            priority: form.priority as any,
            status: form.status as any,
            assignedTo: form.assignedTo,
            dueDate: form.dueDate,
            relatedElement: form.relatedElement || null,
            commentsHistory: form.comments
                ? [...allIssues.value[index].commentsHistory, { user: 'Current User', date: new Date().toLocaleString(), text: form.comments }]
                : allIssues.value[index].commentsHistory
          }
          ElMessage.success('Issue updated')
        }
      } else {
        const newIssue: BCFIssue = {
          id: `BCF-${Math.floor(Math.random() * 900) + 200}`,
          title: form.title,
          description: form.description,
          priority: form.priority as any,
          status: 'open',
          assignedTo: form.assignedTo,
          createdBy: 'Current User',
          createdDate: new Date().toISOString().slice(0, 10),
          dueDate: form.dueDate,
          closedDate: null,
          relatedElement: form.relatedElement || null,
          commentsHistory: form.comments ? [{ user: 'Current User', date: new Date().toLocaleString(), text: form.comments }] : []
        }
        allIssues.value.unshift(newIssue)
        ElMessage.success('Issue created')
      }
      dialog.visible = false
      updateStats()
      resetForm()
    }
  })
}

const updateStatus = (newStatus: string) => {
  if (viewDialog.issue) {
    const index = allIssues.value.findIndex(i => i.id === viewDialog.issue!.id)
    if (index !== -1) {
      allIssues.value[index].status = newStatus as any
      if (newStatus === 'closed') {
        allIssues.value[index].closedDate = new Date().toISOString().slice(0, 10)
      }
      viewDialog.issue = allIssues.value[index]
      updateStats()
      ElMessage.success(`Status updated to ${getStatusLabel(newStatus)}`)
    }
  }
}

const addComment = () => {
  if (newComment.value.trim() && viewDialog.issue) {
    const comment = {
      user: 'Current User',
      date: new Date().toLocaleString(),
      text: newComment.value
    }
    viewDialog.issue.commentsHistory.push(comment)

    const index = allIssues.value.findIndex(i => i.id === viewDialog.issue!.id)
    if (index !== -1) {
      allIssues.value[index].commentsHistory.push(comment)
    }

    newComment.value = ''
    ElMessage.success('Comment added')
  }
}

const exportIssues = () => {
  const exportData = {
    generatedAt: new Date().toISOString(),
    issues: filteredIssues.value
  }
  const data = JSON.stringify(exportData, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `bcf-issues-${new Date().toISOString().slice(0, 19)}.bcf`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Issues exported')
}

const importBCF = () => {
  ElMessage.info('BCF import functionality - select a .bcf file')
  // Simulate file input click
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.bcf,.xml'
  input.onchange = (e: any) => {
    if (e.target.files?.[0]) {
      ElMessage.success(`Importing ${e.target.files[0].name}`)
    }
  }
  input.click()
}

// ==================== 数据加载 ====================
const loadData = () => {
  tableLoading.value = true
  setTimeout(() => {
    allIssues.value = generateMockIssues()
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
.bcf-issues-page {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
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

.header-actions {
  display: flex;
  gap: 12px;
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
.warning-bg { background-color: #fff3e0; color: #e6a23c; }
.success-bg { background-color: #f0f9eb; color: #67c23a; }
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

.issues-table-wrapper {
  background: white;
  border-radius: 12px;
  padding: 0;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 16px 20px;
  border-top: 1px solid #ebeef5;
}

.overdue {
  color: #f56c6c;
  font-weight: 500;
}

.delete-warning {
  color: #f56c6c;
  font-size: 13px;
  margin-top: 8px;
}

.issue-detail {
  padding: 8px 0;
}

.description-text {
  white-space: pre-wrap;
  line-height: 1.5;
}

.comments-section {
  max-height: 300px;
  overflow-y: auto;
}

.comment-item {
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.comment-item strong {
  color: #409eff;
}

.comment-time {
  font-size: 11px;
  color: #8c9aab;
  margin-left: 12px;
}

.comment-item p {
  margin: 4px 0 0 0;
  font-size: 13px;
  color: #5e6e82;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
  color: #1f2f3d;
}

:deep(.el-table td) {
  font-size: 13px;
}
</style>