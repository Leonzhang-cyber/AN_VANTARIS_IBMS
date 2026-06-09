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
        <div class="loading-tip">Delegation Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="delegation-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Decision & Evidence</el-breadcrumb-item>
            <el-breadcrumb-item>Workflow Management</el-breadcrumb-item>
            <el-breadcrumb-item>Delegation</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Delegation Management</h1>
        <p class="description">Configure temporary approval authority delegation for absences, leaves, or workload redistribution</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
        <el-button type="primary" @click="handleCreateDelegation">
          <el-icon><Plus /></el-icon>
          New Delegation
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

    <!-- Active Delegations Overview -->
    <el-row :gutter="20" class="overview-row">
      <el-col :xs="24" :lg="16">
        <el-card class="delegation-calendar-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Active Delegations Timeline</span>
              <el-button size="small" @click="handleRefreshCalendar">
                <el-icon><Refresh /></el-icon>
                Refresh
              </el-button>
            </div>
          </template>
          <div ref="timelineChartRef" class="timeline-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card class="delegation-stats-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Delegation by Type</span>
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
              placeholder="Search by delegator or delegatee"
              prefix-icon="Search"
              clearable
              style="width: 220px"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
          />
          <el-select v-model="filters.status" placeholder="Status" clearable style="width: 130px">
            <el-option label="Active" value="Active" />
            <el-option label="Expired" value="Expired" />
            <el-option label="Upcoming" value="Upcoming" />
            <el-option label="Cancelled" value="Cancelled" />
          </el-select>
          <el-select v-model="filters.delegationType" placeholder="Delegation Type" clearable style="width: 150px">
            <el-option label="Full Authority" value="Full Authority" />
            <el-option label="Limited" value="Limited" />
            <el-option label="Conditional" value="Conditional" />
          </el-select>
          <el-date-picker
              v-model="filters.dateRange"
              type="daterange"
              range-separator="to"
              start-placeholder="Start Date"
              end-placeholder="End Date"
              style="width: 260px"
          />
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="handleResetFilters">Reset</el-button>
        </div>
      </div>
    </el-card>

    <!-- Main Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Delegation Rules</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchDelegations" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedDelegations" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="delegator" label="Delegator" min-width="150" show-overflow-tooltip />
        <el-table-column prop="delegatorRole" label="Delegator Role" width="150" />
        <el-table-column prop="delegatee" label="Delegatee" min-width="150" show-overflow-tooltip />
        <el-table-column prop="delegateeRole" label="Delegatee Role" width="150" />
        <el-table-column prop="delegationType" label="Type" width="120">
          <template #default="{ row }">
            <el-tag :type="getDelegationTypeTag(row.delegationType)" size="small">{{ row.delegationType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="startDate" label="Start Date" width="110" />
        <el-table-column prop="endDate" label="End Date" width="110" />
        <el-table-column prop="reason" label="Reason" min-width="160" show-overflow-tooltip />
        <el-table-column label="Actions" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDelegation(row)">View</el-button>
            <el-button link type="success" size="small" @click="editDelegation(row)">Edit</el-button>
            <el-button v-if="row.status === 'Active'" link type="warning" size="small" @click="cancelDelegation(row)">Cancel</el-button>
            <el-button link type="danger" size="small" @click="deleteDelegation(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredDelegations.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Create/Edit Delegation Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? 'Create Delegation' : (dialogMode === 'edit' ? 'Edit Delegation' : 'Delegation Details')" width="700px" destroy-on-close>
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="130px" :disabled="dialogMode === 'view'">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Delegator" prop="delegatorId">
              <el-select v-model="formData.delegatorId" placeholder="Select delegator" filterable style="width: 100%">
                <el-option
                    v-for="user in availableUsers"
                    :key="user.id"
                    :label="`${user.name} (${user.role})`"
                    :value="user.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Delegatee" prop="delegateeId">
              <el-select v-model="formData.delegateeId" placeholder="Select delegatee" filterable style="width: 100%">
                <el-option
                    v-for="user in availableUsers"
                    :key="user.id"
                    :label="`${user.name} (${user.role})`"
                    :value="user.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Delegation Type" prop="delegationType">
              <el-select v-model="formData.delegationType" placeholder="Select type" style="width: 100%">
                <el-option label="Full Authority" value="Full Authority" />
                <el-option label="Limited" value="Limited" />
                <el-option label="Conditional" value="Conditional" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Status" prop="status">
              <el-select v-model="formData.status" placeholder="Select status" style="width: 100%">
                <el-option label="Active" value="Active" />
                <el-option label="Upcoming" value="Upcoming" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Start Date" prop="startDate">
              <el-date-picker v-model="formData.startDate" type="date" placeholder="Select start date" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="End Date" prop="endDate">
              <el-date-picker v-model="formData.endDate" type="date" placeholder="Select end date" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="24" v-if="formData.delegationType === 'Limited'">
            <el-form-item label="Limited To" prop="limitedTo">
              <el-select v-model="formData.limitedTo" multiple placeholder="Select decision types" style="width: 100%">
                <el-option label="Fault Decisions" value="Fault Decisions" />
                <el-option label="Maintenance Decisions" value="Maintenance Decisions" />
                <el-option label="ESG Decisions" value="ESG Decisions" />
                <el-option label="Energy Decisions" value="Energy Decisions" />
                <el-option label="AI Recommendations" value="AI Recommendations" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24" v-if="formData.delegationType === 'Conditional'">
            <el-form-item label="Condition" prop="condition">
              <el-input v-model="formData.condition" type="textarea" :rows="2" placeholder="e.g., Only for approvals under $10,000, Only for urgent matters" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Reason" prop="reason">
              <el-input v-model="formData.reason" type="textarea" :rows="2" placeholder="Enter reason for delegation (e.g., Vacation, Medical Leave, Training)" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Close</el-button>
        <el-button v-if="dialogMode !== 'view'" type="primary" @click="submitForm">Save Delegation</el-button>
      </template>
    </el-dialog>

    <!-- Cancel Confirmation Dialog -->
    <el-dialog v-model="cancelDialogVisible" title="Cancel Delegation" width="400px">
      <p>Are you sure you want to cancel this delegation?</p>
      <p style="color: #e6a23c; font-size: 12px; margin-top: 8px">
        Delegator: {{ cancelTarget?.delegator }}<br>
        Delegatee: {{ cancelTarget?.delegatee }}
      </p>
      <template #footer>
        <el-button @click="cancelDialogVisible = false">No, Keep Active</el-button>
        <el-button type="warning" @click="confirmCancel">Yes, Cancel</el-button>
      </template>
    </el-dialog>

    <!-- Delete Confirmation Dialog -->
    <el-dialog v-model="deleteDialogVisible" title="Confirm Delete" width="400px">
      <p>Are you sure you want to delete this delegation record?</p>
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
  'Loading delegation data...',
  'Fetching user permissions...',
  'Almost ready...'
]

// ==================== Interfaces ====================
interface User {
  id: number
  name: string
  role: string
  department: string
  email: string
  avatar?: string
}

interface Delegation {
  id: number
  delegatorId: number
  delegator: string
  delegatorRole: string
  delegateeId: number
  delegatee: string
  delegateeRole: string
  delegationType: string
  status: string
  startDate: string
  endDate: string
  reason: string
  limitedTo?: string[]
  condition?: string
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
const timelineChartRef = ref<HTMLElement>()
const typeChartRef = ref<HTMLElement>()
let timelineChart: echarts.ECharts | null = null
let typeChart: echarts.ECharts | null = null

// ==================== Mock Data ====================
const statsCards = ref<StatCard[]>([
  { title: 'Active Delegations', value: 12, trend: 8, icon: 'Document', bgColor: '#409eff', key: 'active' },
  { title: 'Upcoming Delegations', value: 5, trend: -2, icon: 'Clock', bgColor: '#e6a23c', key: 'upcoming' },
  { title: 'Total Delegations', value: 48, trend: 15, icon: 'TrendCharts', bgColor: '#67c23a', key: 'total' },
  { title: 'Avg Delegation Days', value: '14.5', trend: -5, icon: 'Checked', bgColor: '#f56c6c', key: 'avgDays' }
])

const availableUsers = ref<User[]>([
  { id: 1, name: 'John Smith', role: 'Facility Manager', department: 'Facilities', email: 'john.smith@ibms.com' },
  { id: 2, name: 'Sarah Chen', role: 'Operations Director', department: 'Operations', email: 'sarah.chen@ibms.com' },
  { id: 3, name: 'David Wang', role: 'Chief Engineer', department: 'Engineering', email: 'david.wang@ibms.com' },
  { id: 4, name: 'Lisa Zhang', role: 'Energy Manager', department: 'Energy', email: 'lisa.zhang@ibms.com' },
  { id: 5, name: 'Mike Johnson', role: 'Maintenance Supervisor', department: 'Maintenance', email: 'mike.johnson@ibms.com' },
  { id: 6, name: 'Emily Zhao', role: 'ESG Manager', department: 'ESG', email: 'emily.zhao@ibms.com' },
  { id: 7, name: 'Robert Liu', role: 'Safety Officer', department: 'Safety', email: 'robert.liu@ibms.com' },
  { id: 8, name: 'Tom Harris', role: 'IT Director', department: 'IT', email: 'tom.harris@ibms.com' },
  { id: 9, name: 'Anna Kim', role: 'Finance Controller', department: 'Finance', email: 'anna.kim@ibms.com' },
  { id: 10, name: 'James Wu', role: 'VP of Operations', department: 'Executive', email: 'james.wu@ibms.com' },
  { id: 11, name: 'Maria Garcia', role: 'Legal Counsel', department: 'Legal', email: 'maria.garcia@ibms.com' },
  { id: 12, name: 'Chris Lee', role: 'Procurement Manager', department: 'Procurement', email: 'chris.lee@ibms.com' }
])

const delegations = ref<Delegation[]>([
  {
    id: 1,
    delegatorId: 1,
    delegator: 'John Smith',
    delegatorRole: 'Facility Manager',
    delegateeId: 5,
    delegatee: 'Mike Johnson',
    delegateeRole: 'Maintenance Supervisor',
    delegationType: 'Full Authority',
    status: 'Active',
    startDate: '2024-01-10',
    endDate: '2024-01-25',
    reason: 'Annual leave - vacation',
    createdAt: '2024-01-05',
    updatedAt: '2024-01-10'
  },
  {
    id: 2,
    delegatorId: 2,
    delegator: 'Sarah Chen',
    delegatorRole: 'Operations Director',
    delegateeId: 1,
    delegatee: 'John Smith',
    delegateeRole: 'Facility Manager',
    delegationType: 'Limited',
    status: 'Active',
    startDate: '2024-01-15',
    endDate: '2024-02-15',
    reason: 'Medical leave - surgery',
    limitedTo: ['Maintenance Decisions', 'Fault Decisions'],
    createdAt: '2024-01-10',
    updatedAt: '2024-01-15'
  },
  {
    id: 3,
    delegatorId: 3,
    delegator: 'David Wang',
    delegatorRole: 'Chief Engineer',
    delegateeId: 5,
    delegatee: 'Mike Johnson',
    delegateeRole: 'Maintenance Supervisor',
    delegationType: 'Conditional',
    status: 'Active',
    startDate: '2024-01-05',
    endDate: '2024-01-20',
    reason: 'Business trip - overseas',
    condition: 'Only for approvals under $5,000',
    createdAt: '2024-01-03',
    updatedAt: '2024-01-05'
  },
  {
    id: 4,
    delegatorId: 4,
    delegator: 'Lisa Zhang',
    delegatorRole: 'Energy Manager',
    delegateeId: 2,
    delegatee: 'Sarah Chen',
    delegateeRole: 'Operations Director',
    delegationType: 'Full Authority',
    status: 'Upcoming',
    startDate: '2024-02-01',
    endDate: '2024-02-14',
    reason: 'Maternity leave',
    createdAt: '2024-01-15',
    updatedAt: '2024-01-15'
  },
  {
    id: 5,
    delegatorId: 6,
    delegator: 'Emily Zhao',
    delegatorRole: 'ESG Manager',
    delegateeId: 4,
    delegatee: 'Lisa Zhang',
    delegateeRole: 'Energy Manager',
    delegationType: 'Limited',
    status: 'Active',
    startDate: '2024-01-08',
    endDate: '2024-01-22',
    reason: 'Conference attendance',
    limitedTo: ['ESG Decisions'],
    createdAt: '2024-01-06',
    updatedAt: '2024-01-08'
  },
  {
    id: 6,
    delegatorId: 8,
    delegator: 'Tom Harris',
    delegatorRole: 'IT Director',
    delegateeId: 3,
    delegatee: 'David Wang',
    delegateeRole: 'Chief Engineer',
    delegationType: 'Conditional',
    status: 'Expired',
    startDate: '2023-12-10',
    endDate: '2023-12-20',
    reason: 'Training course',
    condition: 'Only for IT infrastructure approvals',
    createdAt: '2023-12-05',
    updatedAt: '2023-12-10'
  },
  {
    id: 7,
    delegatorId: 9,
    delegator: 'Anna Kim',
    delegatorRole: 'Finance Controller',
    delegateeId: 2,
    delegatee: 'Sarah Chen',
    delegateeRole: 'Operations Director',
    delegationType: 'Full Authority',
    status: 'Upcoming',
    startDate: '2024-02-10',
    endDate: '2024-02-28',
    reason: 'Annual audit leave',
    createdAt: '2024-01-12',
    updatedAt: '2024-01-12'
  },
  {
    id: 8,
    delegatorId: 5,
    delegator: 'Mike Johnson',
    delegatorRole: 'Maintenance Supervisor',
    delegateeId: 3,
    delegatee: 'David Wang',
    delegateeRole: 'Chief Engineer',
    delegationType: 'Limited',
    status: 'Active',
    startDate: '2024-01-12',
    endDate: '2024-01-19',
    reason: 'Sick leave',
    limitedTo: ['Maintenance Decisions', 'Fault Decisions'],
    createdAt: '2024-01-11',
    updatedAt: '2024-01-12'
  },
  {
    id: 9,
    delegatorId: 7,
    delegator: 'Robert Liu',
    delegatorRole: 'Safety Officer',
    delegateeId: 1,
    delegatee: 'John Smith',
    delegateeRole: 'Facility Manager',
    delegationType: 'Full Authority',
    status: 'Cancelled',
    startDate: '2024-01-20',
    endDate: '2024-01-27',
    reason: 'Planned vacation (cancelled)',
    createdAt: '2024-01-10',
    updatedAt: '2024-01-14'
  },
  {
    id: 10,
    delegatorId: 10,
    delegator: 'James Wu',
    delegatorRole: 'VP of Operations',
    delegateeId: 2,
    delegatee: 'Sarah Chen',
    delegateeRole: 'Operations Director',
    delegationType: 'Full Authority',
    status: 'Active',
    startDate: '2024-01-05',
    endDate: '2024-02-05',
    reason: 'Executive retreat and travel',
    createdAt: '2024-01-02',
    updatedAt: '2024-01-05'
  },
  {
    id: 11,
    delegatorId: 11,
    delegator: 'Maria Garcia',
    delegatorRole: 'Legal Counsel',
    delegateeId: 10,
    delegatee: 'James Wu',
    delegateeRole: 'VP of Operations',
    delegationType: 'Conditional',
    status: 'Upcoming',
    startDate: '2024-02-15',
    endDate: '2024-03-01',
    reason: 'Legal conference',
    condition: 'Only for contracts under $50,000',
    createdAt: '2024-01-10',
    updatedAt: '2024-01-10'
  },
  {
    id: 12,
    delegatorId: 12,
    delegator: 'Chris Lee',
    delegatorRole: 'Procurement Manager',
    delegateeId: 9,
    delegatee: 'Anna Kim',
    delegateeRole: 'Finance Controller',
    delegationType: 'Limited',
    status: 'Expired',
    startDate: '2023-12-01',
    endDate: '2023-12-15',
    reason: 'Year-end vacation',
    limitedTo: ['Maintenance Decisions'],
    createdAt: '2023-11-25',
    updatedAt: '2023-12-01'
  }
])

// ==================== Reactive Variables ====================
const tableLoading = ref(false)
const dialogVisible = ref(false)
const cancelDialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit' | 'view'>('view')
const cancelTarget = ref<Delegation | null>(null)
const deleteTarget = ref<Delegation | null>(null)
const formRef = ref()
const currentPage = ref(1)
const pageSize = ref(10)

const filters = reactive({
  keyword: '',
  status: '',
  delegationType: '',
  dateRange: null as [Date, Date] | null
})

const formData = reactive<Delegation>({
  id: 0,
  delegatorId: 0,
  delegator: '',
  delegatorRole: '',
  delegateeId: 0,
  delegatee: '',
  delegateeRole: '',
  delegationType: 'Full Authority',
  status: 'Upcoming',
  startDate: '',
  endDate: '',
  reason: '',
  limitedTo: [],
  condition: '',
  createdAt: '',
  updatedAt: ''
})

const formRules = {
  delegatorId: [{ required: true, message: 'Please select delegator', trigger: 'change' }],
  delegateeId: [{ required: true, message: 'Please select delegatee', trigger: 'change' }],
  delegationType: [{ required: true, message: 'Please select delegation type', trigger: 'change' }],
  startDate: [{ required: true, message: 'Please select start date', trigger: 'change' }],
  endDate: [{ required: true, message: 'Please select end date', trigger: 'change' }],
  reason: [{ required: true, message: 'Please enter reason', trigger: 'blur' }]
}

// ==================== Computed ====================
const filteredDelegations = computed(() => {
  let filtered = [...delegations.value]

  if (filters.keyword) {
    filtered = filtered.filter(d =>
        d.delegator.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        d.delegatee.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        d.reason.toLowerCase().includes(filters.keyword.toLowerCase())
    )
  }

  if (filters.status) {
    filtered = filtered.filter(d => d.status === filters.status)
  }

  if (filters.delegationType) {
    filtered = filtered.filter(d => d.delegationType === filters.delegationType)
  }

  if (filters.dateRange && filters.dateRange[0] && filters.dateRange[1]) {
    filtered = filtered.filter(d => {
      const start = new Date(d.startDate)
      const end = new Date(d.endDate)
      const filterStart = filters.dateRange![0]
      const filterEnd = filters.dateRange![1]
      return (start >= filterStart && start <= filterEnd) || (end >= filterStart && end <= filterEnd)
    })
  }

  return filtered
})

const paginatedDelegations = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredDelegations.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getDelegationTypeTag = (type: string): string => {
  const map: Record<string, string> = {
    'Full Authority': 'success',
    'Limited': 'warning',
    'Conditional': 'info'
  }
  return map[type] || 'info'
}

const getStatusTag = (status: string): string => {
  const map: Record<string, string> = {
    'Active': 'success',
    'Expired': 'info',
    'Upcoming': 'warning',
    'Cancelled': 'danger'
  }
  return map[status] || 'info'
}

const getUserById = (userId: number): User | undefined => {
  return availableUsers.value.find(u => u.id === userId)
}

// ==================== Chart Initialization ====================
const initTimelineChart = () => {
  if (!timelineChartRef.value) return
  if (timelineChart) timelineChart.dispose()

  timelineChart = echarts.init(timelineChartRef.value)

  const activeDelegations = delegations.value.filter(d => d.status === 'Active')

  const data = activeDelegations.map(d => ({
    name: `${d.delegator} → ${d.delegatee}`,
    value: [new Date(d.startDate).getTime(), new Date(d.endDate).getTime()],
    itemStyle: { color: '#409eff' }
  }))

  const option: echarts.EChartsOption = {
    title: {
      show: false
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const data = params[0]
        const delegation = activeDelegations[data.dataIndex]
        return `<strong>${delegation.delegator} → ${delegation.delegatee}</strong><br/>
                Type: ${delegation.delegationType}<br/>
                Period: ${delegation.startDate} to ${delegation.endDate}<br/>
                Reason: ${delegation.reason}`
      }
    },
    xAxis: {
      type: 'time',
      name: 'Date',
      axisLabel: {
        formatter: (value: number) => {
          return new Date(value).toLocaleDateString()
        }
      }
    },
    yAxis: {
      type: 'category',
      data: activeDelegations.map((_, index) => `Delegation ${index + 1}`),
      axisLabel: {
        show: false
      }
    },
    grid: {
      left: '10%',
      right: '5%',
      containLabel: true
    },
    series: [{
      type: 'custom',
      renderItem: (params: any, api: any) => {
        const categoryIndex = api.value(0)
        const start = api.coord([api.value(1), categoryIndex])
        const end = api.coord([api.value(2), categoryIndex])
        const height = api.size([0, 1])[1] * 0.6
        return {
          type: 'rect',
          shape: {
            x: start[0],
            y: start[1] - height / 2,
            width: end[0] - start[0],
            height: height
          },
          style: api.style()
        }
      },
      data: data,
      itemStyle: {
        borderRadius: [4, 4, 4, 4]
      }
    }]
  }

  timelineChart.setOption(option)
  window.addEventListener('resize', () => timelineChart?.resize())
}

const initTypeChart = () => {
  if (!typeChartRef.value) return
  if (typeChart) typeChart.dispose()

  typeChart = echarts.init(typeChartRef.value)

  const typeCount = {
    'Full Authority': delegations.value.filter(d => d.delegationType === 'Full Authority').length,
    'Limited': delegations.value.filter(d => d.delegationType === 'Limited').length,
    'Conditional': delegations.value.filter(d => d.delegationType === 'Conditional').length
  }

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {d}% ({c} delegations)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: ['Full Authority', 'Limited', 'Conditional']
    },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: typeCount['Full Authority'], name: 'Full Authority', itemStyle: { color: '#67c23a' } },
        { value: typeCount['Limited'], name: 'Limited', itemStyle: { color: '#e6a23c' } },
        { value: typeCount['Conditional'], name: 'Conditional', itemStyle: { color: '#409eff' } }
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
  filters.status = ''
  filters.delegationType = ''
  filters.dateRange = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleRefreshCalendar = () => {
  initTimelineChart()
  ElMessage.success('Calendar refreshed')
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredDelegations.value.length} delegation records...`)
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const fetchDelegations = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Data refreshed')
  }, 500)
}

const handleCreateDelegation = () => {
  dialogMode.value = 'create'
  Object.assign(formData, {
    id: 0,
    delegatorId: 0,
    delegator: '',
    delegatorRole: '',
    delegateeId: 0,
    delegatee: '',
    delegateeRole: '',
    delegationType: 'Full Authority',
    status: 'Upcoming',
    startDate: '',
    endDate: '',
    reason: '',
    limitedTo: [],
    condition: '',
    createdAt: new Date().toISOString().split('T')[0],
    updatedAt: new Date().toISOString().split('T')[0]
  })
  dialogVisible.value = true
}

const viewDelegation = (row: Delegation) => {
  dialogMode.value = 'view'
  Object.assign(formData, JSON.parse(JSON.stringify(row)))
  dialogVisible.value = true
}

const editDelegation = (row: Delegation) => {
  dialogMode.value = 'edit'
  Object.assign(formData, JSON.parse(JSON.stringify(row)))
  dialogVisible.value = true
}

const cancelDelegation = (row: Delegation) => {
  cancelTarget.value = row
  cancelDialogVisible.value = true
}

const deleteDelegation = (row: Delegation) => {
  deleteTarget.value = row
  deleteDialogVisible.value = true
}

const confirmCancel = () => {
  if (cancelTarget.value) {
    const index = delegations.value.findIndex(d => d.id === cancelTarget.value!.id)
    if (index !== -1) {
      delegations.value[index].status = 'Cancelled'
      delegations.value[index].updatedAt = new Date().toISOString().split('T')[0]
      ElMessage.warning(`Cancelled delegation: ${cancelTarget.value.delegator} → ${cancelTarget.value.delegatee}`)
      initTimelineChart()
      initTypeChart()
    }
  }
  cancelDialogVisible.value = false
  cancelTarget.value = null
}

const confirmDelete = () => {
  if (deleteTarget.value) {
    const index = delegations.value.findIndex(d => d.id === deleteTarget.value!.id)
    if (index !== -1) {
      delegations.value.splice(index, 1)
      ElMessage.success(`Deleted delegation record`)
      initTimelineChart()
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
      const delegator = getUserById(formData.delegatorId)
      const delegatee = getUserById(formData.delegateeId)

      if (!delegator || !delegatee) {
        ElMessage.error('Invalid user selection')
        return
      }

      const newDelegation: Delegation = {
        id: formData.id || Date.now(),
        delegatorId: formData.delegatorId,
        delegator: delegator.name,
        delegatorRole: delegator.role,
        delegateeId: formData.delegateeId,
        delegatee: delegatee.name,
        delegateeRole: delegatee.role,
        delegationType: formData.delegationType,
        status: formData.status,
        startDate: formData.startDate,
        endDate: formData.endDate,
        reason: formData.reason,
        limitedTo: formData.limitedTo,
        condition: formData.condition,
        createdAt: formData.createdAt || new Date().toISOString().split('T')[0],
        updatedAt: new Date().toISOString().split('T')[0]
      }

      if (dialogMode.value === 'create') {
        delegations.value.unshift(newDelegation)
        ElMessage.success('Delegation created successfully')
      } else if (dialogMode.value === 'edit') {
        const index = delegations.value.findIndex(d => d.id === formData.id)
        if (index !== -1) {
          delegations.value[index] = newDelegation
          ElMessage.success('Delegation updated successfully')
        }
      }

      initTimelineChart()
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
    initTimelineChart()
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
      fetchDelegations()
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
.delegation-page {
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

.delegation-calendar-card, .delegation-stats-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}

.timeline-container {
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