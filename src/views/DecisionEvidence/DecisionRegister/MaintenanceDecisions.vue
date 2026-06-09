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
        <div class="loading-tip">Maintenance Decisions Register</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="maintenance-decisions-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Decision & Evidence</el-breadcrumb-item>
            <el-breadcrumb-item>Decision Register</el-breadcrumb-item>
            <el-breadcrumb-item>Maintenance Decisions</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Maintenance Decisions</h1>
        <p class="description">Track and manage preventive, corrective, and predictive maintenance decisions across all assets</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
        <el-button type="primary" @click="handleCreateDecision">
          <el-icon><Plus /></el-icon>
          New Maintenance Decision
        </el-button>
      </div>
    </div>

    <!-- Maintenance Overview Charts -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :lg="14">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Maintenance Trends (Last 12 Months)</span>
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
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Decisions by Priority</span>
            </div>
          </template>
          <div ref="priorityChartRef" class="chart-container-small"></div>
        </el-card>
      </el-col>
    </el-row>

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

    <!-- Filters -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-container">
        <div class="filter-row">
          <el-input
              v-model="filters.keyword"
              placeholder="Search by title or asset"
              prefix-icon="Search"
              clearable
              style="width: 240px"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
          />
          <el-select v-model="filters.type" placeholder="Maintenance Type" clearable style="width: 150px">
            <el-option label="Preventive" value="Preventive" />
            <el-option label="Corrective" value="Corrective" />
            <el-option label="Predictive" value="Predictive" />
            <el-option label="Emergency" value="Emergency" />
          </el-select>
          <el-select v-model="filters.priority" placeholder="Priority" clearable style="width: 120px">
            <el-option label="Critical" value="Critical" />
            <el-option label="High" value="High" />
            <el-option label="Medium" value="Medium" />
            <el-option label="Low" value="Low" />
          </el-select>
          <el-select v-model="filters.status" placeholder="Status" clearable style="width: 130px">
            <el-option label="Draft" value="Draft" />
            <el-option label="Approved" value="Approved" />
            <el-option label="In Progress" value="In Progress" />
            <el-option label="Completed" value="Completed" />
            <el-option label="Cancelled" value="Cancelled" />
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
          <span>Maintenance Decisions List</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchDecisions" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedDecisions" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="title" label="Decision Title" min-width="200" show-overflow-tooltip />
        <el-table-column prop="assetName" label="Asset Name" width="160" show-overflow-tooltip />
        <el-table-column prop="type" label="Type" width="110">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.type)" size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="Priority" width="90">
          <template #default="{ row }">
            <el-tag :type="getPriorityTag(row.priority)" size="small">{{ row.priority }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="estimatedCost" label="Est. Cost (USD)" width="130">
          <template #default="{ row }">
            ${{ row.estimatedCost.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="actualCost" label="Actual Cost (USD)" width="130">
          <template #default="{ row }">
            <span :style="{ color: row.actualCost > row.estimatedCost ? '#f56c6c' : '#67c23a' }">
              ${{ row.actualCost.toLocaleString() }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="scheduledDate" label="Scheduled Date" width="110" />
        <el-table-column prop="completionDate" label="Completion Date" width="110" />
        <el-table-column prop="assignedTo" label="Assigned To" width="120" />
        <el-table-column label="Actions" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetail(row)">View</el-button>
            <el-button link type="success" size="small" @click="editDecision(row)">Edit</el-button>
            <el-button link type="danger" size="small" @click="deleteDecision(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredDecisions.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- View/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? 'New Maintenance Decision' : (dialogMode === 'edit' ? 'Edit Maintenance Decision' : 'Maintenance Decision Details')" width="750px" destroy-on-close>
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="130px" :disabled="dialogMode === 'view'">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="Decision Title" prop="title">
              <el-input v-model="formData.title" placeholder="Enter decision title" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Asset Name" prop="assetName">
              <el-input v-model="formData.assetName" placeholder="Enter asset name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Asset ID" prop="assetId">
              <el-input v-model="formData.assetId" placeholder="Enter asset ID" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Maintenance Type" prop="type">
              <el-select v-model="formData.type" placeholder="Select type" style="width: 100%">
                <el-option label="Preventive" value="Preventive" />
                <el-option label="Corrective" value="Corrective" />
                <el-option label="Predictive" value="Predictive" />
                <el-option label="Emergency" value="Emergency" />
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
                <el-option label="Draft" value="Draft" />
                <el-option label="Approved" value="Approved" />
                <el-option label="In Progress" value="In Progress" />
                <el-option label="Completed" value="Completed" />
                <el-option label="Cancelled" value="Cancelled" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Scheduled Date" prop="scheduledDate">
              <el-date-picker v-model="formData.scheduledDate" type="date" placeholder="Select date" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Completion Date" prop="completionDate">
              <el-date-picker v-model="formData.completionDate" type="date" placeholder="Select date" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Estimated Cost (USD)" prop="estimatedCost">
              <el-input-number v-model="formData.estimatedCost" :min="0" :step="1000" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Actual Cost (USD)" prop="actualCost">
              <el-input-number v-model="formData.actualCost" :min="0" :step="1000" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Assigned To" prop="assignedTo">
              <el-input v-model="formData.assignedTo" placeholder="Enter assignee name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Department" prop="department">
              <el-input v-model="formData.department" placeholder="Enter department" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Description" prop="description">
              <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="Enter decision description" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Justification" prop="justification">
              <el-input v-model="formData.justification" type="textarea" :rows="2" placeholder="Enter justification for this decision" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Close</el-button>
        <el-button v-if="dialogMode !== 'view'" type="primary" @click="submitForm">Submit</el-button>
      </template>
    </el-dialog>

    <!-- Delete Confirmation Dialog -->
    <el-dialog v-model="deleteDialogVisible" title="Confirm Delete" width="400px">
      <p>Are you sure you want to delete maintenance decision "{{ deleteTarget?.title }}"?</p>
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
  Clock, TrendCharts, Refresh, Search, Download, Setting
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading maintenance decisions...',
  'Fetching asset data...',
  'Almost ready...'
]

// ==================== Interfaces ====================
interface MaintenanceDecision {
  id: number
  title: string
  assetName: string
  assetId: string
  type: string
  priority: string
  status: string
  estimatedCost: number
  actualCost: number
  scheduledDate: string
  completionDate: string
  assignedTo: string
  department: string
  description: string
  justification: string
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
const priorityChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null
let priorityChart: echarts.ECharts | null = null

const trendPeriod = ref<'monthly' | 'quarterly'>('monthly')

// ==================== Mock Data ====================
const statsCards = ref<StatCard[]>([
  { title: 'Total Decisions', value: 156, trend: 12, icon: 'Document', bgColor: '#409eff', key: 'total' },
  { title: 'Total Budget', value: '$2.45M', trend: 8, icon: 'TrendCharts', bgColor: '#67c23a', key: 'budget' },
  { title: 'Avg. Response Time', value: '4.2 days', trend: -15, icon: 'Clock', bgColor: '#e6a23c', key: 'response' },
  { title: 'Completion Rate', value: '87%', trend: 5, icon: 'Checked', bgColor: '#f56c6c', key: 'completion' }
])

const maintenanceDecisions = ref<MaintenanceDecision[]>([
  {
    id: 1,
    title: 'Chiller Overhaul Decision',
    assetName: 'Chiller-01',
    assetId: 'CHL-001',
    type: 'Preventive',
    priority: 'High',
    status: 'Completed',
    estimatedCost: 45000,
    actualCost: 42800,
    scheduledDate: '2024-01-05',
    completionDate: '2024-01-12',
    assignedTo: 'John Smith',
    department: 'HVAC Team',
    description: 'Complete overhaul of main chiller including compressor replacement',
    justification: 'Unit showing signs of reduced efficiency and increased vibration'
  },
  {
    id: 2,
    title: 'UPS Battery Replacement',
    assetName: 'UPS-03',
    assetId: 'UPS-003',
    type: 'Corrective',
    priority: 'Critical',
    status: 'In Progress',
    estimatedCost: 28000,
    actualCost: 0,
    scheduledDate: '2024-01-10',
    completionDate: '',
    assignedTo: 'Sarah Chen',
    department: 'Electrical',
    description: 'Replace aging battery bank with lithium-ion units',
    justification: 'Batteries exceeded expected lifecycle, showing capacity degradation'
  },
  {
    id: 3,
    title: 'Cooling Tower Fan Motor Replacement',
    assetName: 'CT-02 Fan Motor',
    assetId: 'CTF-002',
    type: 'Corrective',
    priority: 'High',
    status: 'Completed',
    estimatedCost: 5200,
    actualCost: 4850,
    scheduledDate: '2024-01-03',
    completionDate: '2024-01-05',
    assignedTo: 'Mike Johnson',
    department: 'HVAC Team',
    description: 'Replace faulty fan motor with energy-efficient model',
    justification: 'Motor failure causing reduced cooling capacity'
  },
  {
    id: 4,
    title: 'Air Handler Belt Replacement Program',
    assetName: 'AHU-01 to AHU-08',
    assetId: 'AHU-SYS',
    type: 'Preventive',
    priority: 'Medium',
    status: 'Completed',
    estimatedCost: 3500,
    actualCost: 3200,
    scheduledDate: '2024-01-08',
    completionDate: '2024-01-15',
    assignedTo: 'David Wang',
    department: 'HVAC Team',
    description: 'Quarterly belt replacement for all AHU units',
    justification: 'Preventive maintenance schedule to avoid unexpected failures'
  },
  {
    id: 5,
    title: 'BMS Controller Upgrade',
    assetName: 'BMS Gateway',
    assetId: 'BMS-001',
    type: 'Predictive',
    priority: 'Medium',
    status: 'Approved',
    estimatedCost: 18500,
    actualCost: 0,
    scheduledDate: '2024-02-01',
    completionDate: '',
    assignedTo: 'Lisa Zhang',
    department: 'Controls',
    description: 'Upgrade to latest controller with predictive analytics',
    justification: 'Based on failure prediction models showing increased risk'
  },
  {
    id: 6,
    title: 'Fire Pump Annual Test & Service',
    assetName: 'Fire Pump-01',
    assetId: 'FP-001',
    type: 'Preventive',
    priority: 'High',
    status: 'Completed',
    estimatedCost: 2800,
    actualCost: 2600,
    scheduledDate: '2024-01-02',
    completionDate: '2024-01-02',
    assignedTo: 'Robert Liu',
    department: 'Safety',
    description: 'Annual flow test and pump maintenance',
    justification: 'Regulatory compliance requirement'
  },
  {
    id: 7,
    title: 'Generator Load Bank Test',
    assetName: 'Generator-01',
    assetId: 'GEN-001',
    type: 'Preventive',
    priority: 'Critical',
    status: 'In Progress',
    estimatedCost: 4200,
    actualCost: 3800,
    scheduledDate: '2024-01-14',
    completionDate: '',
    assignedTo: 'Tom Harris',
    department: 'Electrical',
    description: 'Monthly load bank test and fuel system inspection',
    justification: 'Monthly testing protocol for backup power systems'
  },
  {
    id: 8,
    title: 'VFD Programming Optimization',
    assetName: 'VFD-Pump-03',
    assetId: 'VFD-003',
    type: 'Corrective',
    priority: 'Low',
    status: 'Completed',
    estimatedCost: 1200,
    actualCost: 950,
    scheduledDate: '2024-01-06',
    completionDate: '2024-01-07',
    assignedTo: 'Emily Zhao',
    department: 'Controls',
    description: 'Re-program VFD for energy efficiency',
    justification: 'Suboptimal operation causing higher energy consumption'
  },
  {
    id: 9,
    title: 'Emergency Lighting System Upgrade',
    assetName: 'Lighting System',
    assetId: 'ELS-001',
    type: 'Corrective',
    priority: 'High',
    status: 'Approved',
    estimatedCost: 12500,
    actualCost: 0,
    scheduledDate: '2024-02-10',
    completionDate: '',
    assignedTo: 'James Wu',
    department: 'Electrical',
    description: 'Replace outdated emergency lighting with LED units',
    justification: 'Failed compliance inspection, urgent replacement needed'
  },
  {
    id: 10,
    title: 'Compressor Predictive Maintenance',
    assetName: 'Compressor-AH03',
    assetId: 'CMP-003',
    type: 'Predictive',
    priority: 'Medium',
    status: 'In Progress',
    estimatedCost: 6800,
    actualCost: 0,
    scheduledDate: '2024-01-18',
    completionDate: '',
    assignedTo: 'Anna Kim',
    department: 'HVAC Team',
    description: 'AI-driven predictive maintenance based on vibration analysis',
    justification: 'Predictive model indicated potential bearing failure'
  },
  {
    id: 11,
    title: 'Water Treatment System Calibration',
    assetName: 'Water Treatment',
    assetId: 'WTS-001',
    type: 'Preventive',
    priority: 'Medium',
    status: 'Completed',
    estimatedCost: 1800,
    actualCost: 1750,
    scheduledDate: '2024-01-04',
    completionDate: '2024-01-04',
    assignedTo: 'David Wang',
    department: 'Facilities',
    description: 'Quarterly calibration of chemical dosing system',
    justification: 'Preventive maintenance schedule'
  },
  {
    id: 12,
    title: 'Elevator Modernization Decision',
    assetName: 'Elevator-01',
    assetId: 'ELV-001',
    type: 'Corrective',
    priority: 'High',
    status: 'Draft',
    estimatedCost: 75000,
    actualCost: 0,
    scheduledDate: '2024-03-01',
    completionDate: '',
    assignedTo: '',
    department: 'Facilities',
    description: 'Complete elevator control system upgrade',
    justification: 'Frequent breakdowns and outdated components'
  }
])

// ==================== Reactive Variables ====================
const tableLoading = ref(false)
const dialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit' | 'view'>('view')
const deleteTarget = ref<MaintenanceDecision | null>(null)
const formRef = ref()
const currentPage = ref(1)
const pageSize = ref(10)

const filters = reactive({
  keyword: '',
  type: '',
  priority: '',
  status: '',
  dateRange: null as [Date, Date] | null
})

const formData = reactive<MaintenanceDecision>({
  id: 0,
  title: '',
  assetName: '',
  assetId: '',
  type: 'Preventive',
  priority: 'Medium',
  status: 'Draft',
  estimatedCost: 0,
  actualCost: 0,
  scheduledDate: '',
  completionDate: '',
  assignedTo: '',
  department: '',
  description: '',
  justification: ''
})

const formRules = {
  title: [{ required: true, message: 'Please enter decision title', trigger: 'blur' }],
  assetName: [{ required: true, message: 'Please enter asset name', trigger: 'blur' }],
  type: [{ required: true, message: 'Please select maintenance type', trigger: 'change' }],
  priority: [{ required: true, message: 'Please select priority', trigger: 'change' }],
  scheduledDate: [{ required: true, message: 'Please select scheduled date', trigger: 'change' }]
}

// ==================== Computed ====================
const filteredDecisions = computed(() => {
  let filtered = [...maintenanceDecisions.value]

  if (filters.keyword) {
    filtered = filtered.filter(d =>
        d.title.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        d.assetName.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        d.description.toLowerCase().includes(filters.keyword.toLowerCase())
    )
  }

  if (filters.type) {
    filtered = filtered.filter(d => d.type === filters.type)
  }

  if (filters.priority) {
    filtered = filtered.filter(d => d.priority === filters.priority)
  }

  if (filters.status) {
    filtered = filtered.filter(d => d.status === filters.status)
  }

  if (filters.dateRange && filters.dateRange[0] && filters.dateRange[1]) {
    filtered = filtered.filter(d => {
      const date = new Date(d.scheduledDate)
      return date >= filters.dateRange![0] && date <= filters.dateRange![1]
    })
  }

  return filtered
})

const paginatedDecisions = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredDecisions.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getTypeTag = (type: string): string => {
  const map: Record<string, string> = {
    'Preventive': 'success',
    'Corrective': 'warning',
    'Predictive': 'primary',
    'Emergency': 'danger'
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
    'Draft': 'info',
    'Approved': 'primary',
    'In Progress': 'warning',
    'Completed': 'success',
    'Cancelled': 'danger'
  }
  return map[status] || 'info'
}

// ==================== Chart Initialization ====================
const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)
  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Preventive', 'Corrective', 'Predictive', 'Emergency'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
    xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
    yAxis: { type: 'value', name: 'Number of Decisions' },
    series: [
      { name: 'Preventive', type: 'bar', data: [8, 7, 9, 8, 10, 9, 7, 8, 9, 10, 8, 9], itemStyle: { borderRadius: [0, 0, 0, 0] } },
      { name: 'Corrective', type: 'bar', data: [5, 6, 4, 5, 7, 6, 8, 5, 4, 6, 5, 4] },
      { name: 'Predictive', type: 'bar', data: [2, 3, 2, 4, 3, 5, 4, 6, 5, 7, 6, 8] },
      { name: 'Emergency', type: 'bar', data: [1, 2, 1, 2, 1, 3, 2, 1, 2, 1, 2, 1] }
    ]
  }
  trendChart.setOption(option)
  window.addEventListener('resize', () => trendChart?.resize())
}

const initPriorityChart = () => {
  if (!priorityChartRef.value) return
  if (priorityChart) priorityChart.dispose()

  priorityChart = echarts.init(priorityChartRef.value)
  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [
      {
        name: 'Priority Distribution',
        type: 'pie',
        radius: '55%',
        data: [
          { value: 28, name: 'Critical', itemStyle: { color: '#f56c6c' } },
          { value: 42, name: 'High', itemStyle: { color: '#e6a23c' } },
          { value: 38, name: 'Medium', itemStyle: { color: '#409eff' } },
          { value: 22, name: 'Low', itemStyle: { color: '#67c23a' } }
        ],
        emphasis: { scale: true },
        label: { show: true, formatter: '{b}: {d}%' }
      }
    ]
  }
  priorityChart.setOption(option)
  window.addEventListener('resize', () => priorityChart?.resize())
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
  filters.type = ''
  filters.priority = ''
  filters.status = ''
  filters.dateRange = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredDecisions.value.length} maintenance decisions...`)
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const fetchDecisions = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Data refreshed')
  }, 500)
}

const handleCreateDecision = () => {
  dialogMode.value = 'create'
  Object.assign(formData, {
    id: Date.now(),
    title: '',
    assetName: '',
    assetId: '',
    type: 'Preventive',
    priority: 'Medium',
    status: 'Draft',
    estimatedCost: 0,
    actualCost: 0,
    scheduledDate: '',
    completionDate: '',
    assignedTo: '',
    department: '',
    description: '',
    justification: ''
  })
  dialogVisible.value = true
}

const viewDetail = (row: MaintenanceDecision) => {
  dialogMode.value = 'view'
  Object.assign(formData, row)
  dialogVisible.value = true
}

const editDecision = (row: MaintenanceDecision) => {
  dialogMode.value = 'edit'
  Object.assign(formData, row)
  dialogVisible.value = true
}

const deleteDecision = (row: MaintenanceDecision) => {
  deleteTarget.value = row
  deleteDialogVisible.value = true
}

const confirmDelete = () => {
  if (deleteTarget.value) {
    const index = maintenanceDecisions.value.findIndex(d => d.id === deleteTarget.value!.id)
    if (index !== -1) {
      maintenanceDecisions.value.splice(index, 1)
      ElMessage.success(`Deleted: ${deleteTarget.value.title}`)
    }
  }
  deleteDialogVisible.value = false
  deleteTarget.value = null
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      if (dialogMode.value === 'create') {
        maintenanceDecisions.value.unshift({ ...formData, id: Date.now() })
        ElMessage.success('Maintenance decision created successfully')
      } else if (dialogMode.value === 'edit') {
        const index = maintenanceDecisions.value.findIndex(d => d.id === formData.id)
        if (index !== -1) {
          maintenanceDecisions.value[index] = { ...formData }
          ElMessage.success('Maintenance decision updated successfully')
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
    initTrendChart()
    initPriorityChart()
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
      fetchDecisions()
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
.maintenance-decisions-page {
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

.chart-card {
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

.chart-container-small {
  width: 100%;
  height: 320px;
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