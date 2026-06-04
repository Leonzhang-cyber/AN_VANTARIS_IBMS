<template>
  <!-- Loading Screen -->
  <div v-if="!isPageLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
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
        <div class="loading-tip">Corrective Work Orders</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="workorders-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-left">
        <h1 class="dashboard-title">
          <div class="title-icon corrective-icon">
            <el-icon><Tools /></el-icon>
          </div>
          Corrective Work Orders
        </h1>
        <div class="header-stats">
          <div class="stat-badge">
            <el-icon><Grid /></el-icon>
            {{ totalOrders }} Total Orders
          </div>
          <div class="stat-badge critical">
            <span class="pulse-dot"></span>
            {{ urgentCount }} Urgent
          </div>
          <div class="stat-badge warning">
            {{ inProgressCount }} In Progress
          </div>
        </div>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleCreateOrder">
          <el-icon><Plus /></el-icon>
          Create Work Order
        </el-button>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-icon" style="background: #fef0f0; color: #f56c6c;">🔴</div>
        <div class="kpi-info">
          <div class="kpi-value">{{ urgentCount }}</div>
          <div class="kpi-label">Urgent Priority</div>
          <div class="kpi-trend up">{{ urgentTrend }}% this week</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon" style="background: #fdf6ec; color: #e6a23c;">🟠</div>
        <div class="kpi-info">
          <div class="kpi-value">{{ highCount }}</div>
          <div class="kpi-label">High Priority</div>
          <div class="kpi-trend stable">{{ highTrend }}% this week</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon" style="background: #fdf6ec; color: #fbbf24;">🟡</div>
        <div class="kpi-info">
          <div class="kpi-value">{{ mediumCount }}</div>
          <div class="kpi-label">Medium Priority</div>
          <div class="kpi-trend down">{{ mediumTrend }}% this week</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon" style="background: #ecf5ff; color: #409eff;">🔵</div>
        <div class="kpi-info">
          <div class="kpi-value">{{ lowCount }}</div>
          <div class="kpi-label">Low Priority</div>
          <div class="kpi-trend stable">{{ lowTrend }}% this week</div>
        </div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-group">
        <el-input v-model="searchText" placeholder="Search by WO #, asset, or description..." size="default" style="width: 260px" clearable>
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="priorityFilter" placeholder="Priority" size="default" style="width: 120px" clearable>
          <el-option label="All" value="all" />
          <el-option label="Urgent" value="urgent" />
          <el-option label="High" value="high" />
          <el-option label="Medium" value="medium" />
          <el-option label="Low" value="low" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" size="default" style="width: 130px" clearable>
          <el-option label="All" value="all" />
          <el-option label="Open" value="open" />
          <el-option label="In Progress" value="in_progress" />
          <el-option label="Pending Parts" value="pending_parts" />
          <el-option label="Completed" value="completed" />
          <el-option label="Closed" value="closed" />
        </el-select>
        <el-select v-model="assetTypeFilter" placeholder="Asset Type" size="default" style="width: 140px" clearable>
          <el-option label="All Assets" value="all" />
          <el-option label="UPS" value="UPS" />
          <el-option label="HVAC" value="HVAC" />
          <el-option label="Server" value="Server" />
          <el-option label="PDU" value="PDU" />
          <el-option label="CRAC" value="CRAC" />
        </el-select>
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            size="default"
            style="width: 260px"
            :shortcuts="dateShortcuts"
        />
      </div>
    </div>

    <!-- Work Orders Table -->
    <div class="card table-card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><List /></el-icon>
          Corrective Work Orders
        </div>
        <div class="table-info">
          Showing {{ paginatedOrders.length }} of {{ filteredOrders.length }} orders
        </div>
      </div>
      <el-table :data="paginatedOrders" stripe border style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="woNumber" label="WO #" width="120" sortable />
        <el-table-column prop="title" label="Title" min-width="150" />
        <el-table-column prop="assetName" label="Asset" width="140" />
        <el-table-column prop="assetType" label="Asset Type" width="100">
          <template #default="{ row }">
            <el-tag :type="getAssetTypeTag(row.assetType)" size="small">{{ row.assetType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="Priority" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityTag(row.priority)" size="small">{{ getPriorityText(row.priority) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assignedTo" label="Assigned To" width="130" />
        <el-table-column prop="reportedDate" label="Reported Date" width="110" sortable />
        <el-table-column prop="dueDate" label="Due Date" width="110" sortable>
          <template #default="{ row }">
            <span :class="{ 'overdue': isOverdue(row.dueDate, row.status) }">{{ row.dueDate }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" fixed="right" width="150">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewOrder(row)">
              <el-icon><View /></el-icon>
              View
            </el-button>
            <el-button type="success" link size="small" @click="editOrder(row)">
              <el-icon><Edit /></el-icon>
              Edit
            </el-button>
            <el-dropdown @command="(cmd) => handleAction(cmd, row)">
              <el-button type="info" link size="small">
                More <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="assign">Assign Technician</el-dropdown-item>
                  <el-dropdown-item command="parts">Order Parts</el-dropdown-item>
                  <el-dropdown-item command="escalate">Escalate Priority</el-dropdown-item>
                  <el-dropdown-item command="complete">Mark Complete</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
      <div class="card-footer">
        <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="filteredOrders.length"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handlePageSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background: #f0f9eb; color: #67c23a;">✅</div>
        <div class="stat-info">
          <div class="stat-value">{{ completedThisMonth }}</div>
          <div class="stat-label">Completed This Month</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fef0f0; color: #f56c6c;">⏰</div>
        <div class="stat-info">
          <div class="stat-value">{{ overdueCount }}</div>
          <div class="stat-label">Overdue Orders</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #ecf5ff; color: #409eff;">⏱️</div>
        <div class="stat-info">
          <div class="stat-value">{{ avgCompletionTime }}<span class="unit">days</span></div>
          <div class="stat-label">Avg Completion Time</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fdf6ec; color: #e6a23c;">💰</div>
        <div class="stat-info">
          <div class="stat-value">${{ avgCost }}<span class="unit">K</span></div>
          <div class="stat-label">Avg Cost per Order</div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Order Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
        <el-form-item label="Title" prop="title">
          <el-input v-model="formData.title" placeholder="Enter work order title" />
        </el-form-item>
        <el-form-item label="Asset" prop="assetName">
          <el-select v-model="formData.assetName" placeholder="Select asset" style="width: 100%">
            <el-option label="UPS-01" value="UPS-01" />
            <el-option label="UPS-02" value="UPS-02" />
            <el-option label="CRAC-01" value="CRAC-01" />
            <el-option label="CRAC-02" value="CRAC-02" />
            <el-option label="PDU-A01" value="PDU-A01" />
            <el-option label="Server-R01" value="Server-R01" />
          </el-select>
        </el-form-item>
        <el-form-item label="Asset Type" prop="assetType">
          <el-select v-model="formData.assetType" placeholder="Select asset type" style="width: 100%">
            <el-option label="UPS" value="UPS" />
            <el-option label="HVAC" value="HVAC" />
            <el-option label="Server" value="Server" />
            <el-option label="PDU" value="PDU" />
            <el-option label="CRAC" value="CRAC" />
          </el-select>
        </el-form-item>
        <el-form-item label="Priority" prop="priority">
          <el-select v-model="formData.priority" placeholder="Select priority" style="width: 100%">
            <el-option label="Urgent" value="urgent" />
            <el-option label="High" value="high" />
            <el-option label="Medium" value="medium" />
            <el-option label="Low" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="Describe the issue" />
        </el-form-item>
        <el-form-item label="Reported By" prop="reportedBy">
          <el-input v-model="formData.reportedBy" placeholder="Enter name" />
        </el-form-item>
        <el-form-item label="Due Date" prop="dueDate">
          <el-date-picker v-model="formData.dueDate" type="date" placeholder="Select due date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Location" prop="location">
          <el-input v-model="formData.location" placeholder="Building / Floor / Room" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitForm">Submit</el-button>
      </template>
    </el-dialog>

    <!-- Order Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Work Order #${selectedOrder?.woNumber}`" width="700px">
      <el-descriptions :column="2" border v-if="selectedOrder">
        <el-descriptions-item label="WO Number">{{ selectedOrder.woNumber }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusTag(selectedOrder.status)">{{ getStatusText(selectedOrder.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Title" :span="2">{{ selectedOrder.title }}</el-descriptions-item>
        <el-descriptions-item label="Asset">{{ selectedOrder.assetName }}</el-descriptions-item>
        <el-descriptions-item label="Asset Type">{{ selectedOrder.assetType }}</el-descriptions-item>
        <el-descriptions-item label="Priority">
          <el-tag :type="getPriorityTag(selectedOrder.priority)">{{ getPriorityText(selectedOrder.priority) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Assigned To">{{ selectedOrder.assignedTo || 'Unassigned' }}</el-descriptions-item>
        <el-descriptions-item label="Reported By">{{ selectedOrder.reportedBy }}</el-descriptions-item>
        <el-descriptions-item label="Reported Date">{{ selectedOrder.reportedDate }}</el-descriptions-item>
        <el-descriptions-item label="Due Date">{{ selectedOrder.dueDate }}</el-descriptions-item>
        <el-descriptions-item label="Completed Date">{{ selectedOrder.completedDate || '-' }}</el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedOrder.description }}</el-descriptions-item>
        <el-descriptions-item label="Root Cause" :span="2">{{ selectedOrder.rootCause || '-' }}</el-descriptions-item>
        <el-descriptions-item label="Resolution" :span="2">{{ selectedOrder.resolution || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Tools, Grid, Plus, Refresh, Search, List, View, Edit, ArrowDown } from '@element-plus/icons-vue'
import { useCounterStore } from '@/stores/counter.js'
import { getCurrentInstance } from 'vue'

const getStore = () => {
  const instance = getCurrentInstance()
  if (!instance) throw new Error('useStore() must be called within a setup function')
  const pinia = instance.appContext.config.globalProperties.$pinia
  if (!pinia) throw new Error('Pinia instance not found')
  return useCounterStore(pinia)
}
const counterStore = getStore()
const isFullscreen = computed(() => counterStore.isFullscreen)
const route = useRoute()

// ==================== Loading State ====================
const isPageLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading work orders...',
  'Checking priorities...',
  'Initializing dashboard...',
  'Almost ready...'
]

// ==================== Data State ====================
const searchText = ref('')
const priorityFilter = ref('all')
const statusFilter = ref('all')
const assetTypeFilter = ref('all')
const dateRange = ref<[Date, Date] | null>(null)
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const dialogTitle = ref('Create Work Order')
const formRef = ref()
const selectedOrder = ref<any>(null)

const pagination = ref({ page: 1, pageSize: 15 })

// Date shortcuts
const dateShortcuts = [
  { text: 'Last 7 days', value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 7 * 24 * 60 * 60 * 1000)
      return [start, end]
    }},
  { text: 'Last 30 days', value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 30 * 24 * 60 * 60 * 1000)
      return [start, end]
    }},
  { text: 'This Month', value: () => {
      const now = new Date()
      const start = new Date(now.getFullYear(), now.getMonth(), 1)
      const end = new Date(now.getFullYear(), now.getMonth() + 1, 0)
      return [start, end]
    }}
]

// Work Order Interface
interface WorkOrder {
  id: number
  woNumber: string
  title: string
  assetName: string
  assetType: string
  priority: string
  status: string
  assignedTo: string
  reportedBy: string
  reportedDate: string
  dueDate: string
  completedDate: string | null
  description: string
  rootCause: string | null
  resolution: string | null
  location: string
}

// Mock Work Orders Data
const workOrders = ref<WorkOrder[]>([
  { id: 1, woNumber: 'WO-001', title: 'UPS-01 Overload Alarm', assetName: 'UPS-01', assetType: 'UPS', priority: 'urgent', status: 'in_progress', assignedTo: 'John Chen', reportedBy: 'System', reportedDate: '2024-06-01', dueDate: '2024-06-03', completedDate: null, description: 'UPS reported overload condition at 92% capacity', rootCause: null, resolution: null, location: 'Server Room A' },
  { id: 2, woNumber: 'WO-002', title: 'CRAC-01 High Temperature', assetName: 'CRAC-01', assetType: 'CRAC', priority: 'urgent', status: 'open', assignedTo: 'Sarah Wong', reportedBy: 'System', reportedDate: '2024-06-02', dueDate: '2024-06-04', completedDate: null, description: 'Supply air temperature above threshold', rootCause: null, resolution: null, location: 'Data Center' },
  { id: 3, woNumber: 'WO-003', title: 'PDU-A01 Fan Failure', assetName: 'PDU-A01', assetType: 'PDU', priority: 'high', status: 'in_progress', assignedTo: 'Mike Lim', reportedBy: 'Technician', reportedDate: '2024-05-30', dueDate: '2024-06-05', completedDate: null, description: 'Cooling fan not responding', rootCause: null, resolution: null, location: 'Server Row A' },
  { id: 4, woNumber: 'WO-004', title: 'Server-R01 Disk Failure', assetName: 'Server-R01', assetType: 'Server', priority: 'high', status: 'pending_parts', assignedTo: 'David Wong', reportedBy: 'Monitoring', reportedDate: '2024-05-28', dueDate: '2024-06-06', completedDate: null, description: 'RAID array disk failed, waiting for replacement', rootCause: null, resolution: null, location: 'Server Room B' },
  { id: 5, woNumber: 'WO-005', title: 'UPS-02 Battery Replacement', assetName: 'UPS-02', assetType: 'UPS', priority: 'medium', status: 'completed', assignedTo: 'John Chen', reportedBy: 'Maintenance', reportedDate: '2024-05-20', dueDate: '2024-05-25', completedDate: '2024-05-24', description: 'Battery capacity below threshold', rootCause: 'Battery age exceeded 5 years', resolution: 'Replaced all battery modules', location: 'Electrical Room' },
  { id: 6, woNumber: 'WO-006', title: 'CRAC-02 Water Leak', assetName: 'CRAC-02', assetType: 'CRAC', priority: 'urgent', status: 'in_progress', assignedTo: 'Sarah Wong', reportedBy: 'Technician', reportedDate: '2024-06-03', dueDate: '2024-06-04', completedDate: null, description: 'Water detected under CRAC unit', rootCause: null, resolution: null, location: 'Data Center' },
  { id: 7, woNumber: 'WO-007', title: 'Network Switch Port Failure', assetName: 'SW-01', assetType: 'Network', priority: 'high', status: 'open', assignedTo: 'Mike Lim', reportedBy: 'Network Team', reportedDate: '2024-06-01', dueDate: '2024-06-07', completedDate: null, description: 'Port 24 not responding', rootCause: null, resolution: null, location: 'Network Rack' },
  { id: 8, woNumber: 'WO-008', title: 'PDU-A02 Firmware Update', assetName: 'PDU-A02', assetType: 'PDU', priority: 'low', status: 'closed', assignedTo: 'John Chen', reportedBy: 'System', reportedDate: '2024-05-15', dueDate: '2024-05-30', completedDate: '2024-05-28', description: 'Firmware update required', rootCause: 'Security patch', resolution: 'Firmware updated successfully', location: 'Server Row B' }
])

// Statistics
const totalOrders = computed(() => workOrders.value.length)
const urgentCount = computed(() => workOrders.value.filter(o => o.priority === 'urgent' && o.status !== 'closed' && o.status !== 'completed').length)
const highCount = computed(() => workOrders.value.filter(o => o.priority === 'high' && o.status !== 'closed' && o.status !== 'completed').length)
const mediumCount = computed(() => workOrders.value.filter(o => o.priority === 'medium' && o.status !== 'closed' && o.status !== 'completed').length)
const lowCount = computed(() => workOrders.value.filter(o => o.priority === 'low' && o.status !== 'closed' && o.status !== 'completed').length)
const inProgressCount = computed(() => workOrders.value.filter(o => o.status === 'in_progress').length)
const completedThisMonth = computed(() => workOrders.value.filter(o => o.status === 'completed' && o.completedDate && o.completedDate.startsWith('2024-06')).length)
const overdueCount = computed(() => workOrders.value.filter(o => {
  if (o.status === 'completed' || o.status === 'closed') return false
  return new Date(o.dueDate) < new Date()
}).length)
const avgCompletionTime = computed(() => 4.2)
const avgCost = computed(() => 2.8)

const urgentTrend = ref(15)
const highTrend = ref(5)
const mediumTrend = ref(-8)
const lowTrend = ref(0)

// Filtered orders
const filteredOrders = computed(() => {
  let filtered = workOrders.value

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(o =>
        o.woNumber.toLowerCase().includes(search) ||
        o.title.toLowerCase().includes(search) ||
        o.description.toLowerCase().includes(search)
    )
  }

  if (priorityFilter.value !== 'all') {
    filtered = filtered.filter(o => o.priority === priorityFilter.value)
  }

  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(o => o.status === statusFilter.value)
  }

  if (assetTypeFilter.value !== 'all') {
    filtered = filtered.filter(o => o.assetType === assetTypeFilter.value)
  }

  if (dateRange.value && dateRange.value[0] && dateRange.value[1]) {
    const [start, end] = dateRange.value
    filtered = filtered.filter(o => {
      const orderDate = new Date(o.reportedDate)
      return orderDate >= start && orderDate <= end
    })
  }

  return filtered
})

const paginatedOrders = computed(() => {
  const start = (pagination.value.page - 1) * pagination.value.pageSize
  return filteredOrders.value.slice(start, start + pagination.value.pageSize)
})

// Helper functions
const getPriorityTag = (priority: string) => {
  const map: Record<string, string> = {
    urgent: 'danger',
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return map[priority] || 'info'
}

const getPriorityText = (priority: string) => {
  const map: Record<string, string> = {
    urgent: 'Urgent',
    high: 'High',
    medium: 'Medium',
    low: 'Low'
  }
  return map[priority] || priority
}

const getStatusTag = (status: string) => {
  const map: Record<string, string> = {
    open: 'danger',
    in_progress: 'warning',
    pending_parts: 'warning',
    completed: 'success',
    closed: 'info'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    open: 'Open',
    in_progress: 'In Progress',
    pending_parts: 'Pending Parts',
    completed: 'Completed',
    closed: 'Closed'
  }
  return map[status] || status
}

const getAssetTypeTag = (type: string) => {
  const map: Record<string, string> = {
    UPS: 'danger',
    HVAC: 'warning',
    Server: 'primary',
    PDU: 'success',
    CRAC: 'warning',
    Network: 'info'
  }
  return map[type] || 'info'
}

const isOverdue = (dueDate: string, status: string) => {
  if (status === 'completed' || status === 'closed') return false
  return new Date(dueDate) < new Date()
}

// Form data
const formData = ref({
  title: '',
  assetName: '',
  assetType: '',
  priority: 'medium',
  description: '',
  reportedBy: '',
  dueDate: '',
  location: ''
})

const formRules = {
  title: [{ required: true, message: 'Please enter title', trigger: 'blur' }],
  assetName: [{ required: true, message: 'Please select asset', trigger: 'change' }],
  assetType: [{ required: true, message: 'Please select asset type', trigger: 'change' }],
  priority: [{ required: true, message: 'Please select priority', trigger: 'change' }],
  description: [{ required: true, message: 'Please enter description', trigger: 'blur' }],
  reportedBy: [{ required: true, message: 'Please enter name', trigger: 'blur' }],
  dueDate: [{ required: true, message: 'Please select due date', trigger: 'change' }]
}

// Actions
const handleCreateOrder = () => {
  dialogTitle.value = 'Create Work Order'
  formData.value = {
    title: '',
    assetName: '',
    assetType: '',
    priority: 'medium',
    description: '',
    reportedBy: '',
    dueDate: '',
    location: ''
  }
  dialogVisible.value = true
}

const editOrder = (order: WorkOrder) => {
  dialogTitle.value = 'Edit Work Order'
  formData.value = {
    title: order.title,
    assetName: order.assetName,
    assetType: order.assetType,
    priority: order.priority,
    description: order.description,
    reportedBy: order.reportedBy,
    dueDate: order.dueDate,
    location: order.location
  }
  dialogVisible.value = true
}

const viewOrder = (order: WorkOrder) => {
  selectedOrder.value = order
  detailDialogVisible.value = true
}

const submitForm = async () => {
  try {
    await formRef.value?.validate()
    ElMessage.success(dialogTitle.value === 'Create Work Order' ? 'Work order created successfully' : 'Work order updated successfully')
    dialogVisible.value = false
  } catch (error) {
    ElMessage.error('Please fill all required fields')
  }
}

const handleAction = (command: string, order: WorkOrder) => {
  if (command === 'assign') {
    ElMessage.info(`Assign technician to ${order.woNumber}`)
  } else if (command === 'parts') {
    ElMessage.info(`Order parts for ${order.woNumber}`)
  } else if (command === 'escalate') {
    ElMessageBox.confirm(`Escalate priority for ${order.woNumber}?`, 'Confirm', {
      confirmButtonText: 'Escalate',
      cancelButtonText: 'Cancel',
      type: 'warning'
    }).then(() => {
      ElMessage.success(`Priority escalated for ${order.woNumber}`)
    }).catch(() => {})
  } else if (command === 'complete') {
    ElMessageBox.confirm(`Mark ${order.woNumber} as completed?`, 'Confirm', {
      confirmButtonText: 'Complete',
      cancelButtonText: 'Cancel',
      type: 'info'
    }).then(() => {
      order.status = 'completed'
      order.completedDate = new Date().toISOString().split('T')[0]
      ElMessage.success(`Work order ${order.woNumber} completed`)
    }).catch(() => {})
  }
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  tableLoading.value = false
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

const handlePageSizeChange = () => { pagination.value.page = 1 }
const handlePageChange = () => {}

// Export
const exportReport = () => {
  ElMessage.success('Exporting work orders...')
}

// ==================== Loading Animation ====================
const startLoading = () => {
  let progress = 0
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 12
      loadingProgress.value = Math.min(progress, 90)
    }
  }, 100)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(() => {
      isPageLoaded.value = true
    }, 500)
  }, 2500)
}

// ==================== Lifecycle ====================
onMounted(() => {
  startLoading()
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

.spinner-ring:nth-child(1) { border-top-color: #3b82f6; animation-delay: 0s; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }
.spinner-ring:nth-child(4) { border-left-color: #ec489a; animation-delay: 0.6s; width: 20%; height: 20%; top: 40%; left: 40%; }

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

/* ==================== Main Dashboard Styles ==================== */
.workorders-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #eef2f5 100%);
  padding: 24px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
  background: white;
  padding: 16px 24px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.dashboard-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 700;
  color: #1f2f3d;
  margin: 0;
}

.title-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.corrective-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.header-stats {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.stat-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  background: #f5f7fa;
  border-radius: 20px;
  font-size: 13px;
  color: #606266;
}

.stat-badge.critical {
  background: #fef0f0;
  color: #f56c6c;
}

.stat-badge.warning {
  background: #fdf6ec;
  color: #e6a23c;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background: #f56c6c;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* KPI Cards */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.kpi-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.kpi-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.kpi-info {
  flex: 1;
}

.kpi-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
}

.kpi-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.kpi-trend {
  font-size: 11px;
  margin-top: 4px;
  display: block;
}

.kpi-trend.up { color: #f56c6c; }
.kpi-trend.down { color: #67c23a; }
.kpi-trend.stable { color: #909399; }

/* Filter Bar */
.filter-bar {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.filter-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

/* Card */
.card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1f2f3d;
}

.table-info {
  font-size: 13px;
  color: #909399;
}

.card-footer {
  padding: 16px 20px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  justify-content: flex-end;
  background: #fafafa;
}

.table-card {
  overflow-x: auto;
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
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #1f2f3d;
}

.stat-value .unit {
  font-size: 12px;
  font-weight: normal;
  color: #909399;
  margin-left: 2px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* Overdue text */
.overdue {
  color: #f56c6c;
  font-weight: 600;
}

/* Responsive */
@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 900px) {
  .filter-group {
    flex-direction: column;
    align-items: stretch;
  }
  .filter-group .el-input,
  .filter-group .el-select,
  .filter-group .el-date-picker {
    width: 100% !important;
  }
}

@media (max-width: 768px) {
  .workorders-dashboard {
    padding: 16px;
  }
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  .stats-grid {
    grid-template-columns: 1fr;
  }
}

/* Element Plus 样式覆盖 */
:deep(.el-table) {
  background: transparent;
  --el-table-header-bg-color: #fafafa;
  --el-table-row-hover-bg-color: #f5f7fa;
  --el-table-border-color: #e4e7ed;
}

:deep(.el-table th.el-table__cell) {
  background-color: #fafafa;
  color: #1f2f3d;
}

:deep(.el-table td.el-table__cell) {
  color: #606266;
}

:deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
  --el-pagination-button-bg-color: #f5f7fa;
  --el-pagination-hover-color: #409eff;
}

:deep(.el-dialog) {
  background: #ffffff;
  border-radius: 12px;
}

:deep(.el-dialog__title) {
  color: #1f2f3d;
}

:deep(.el-form-item) {
  margin-bottom: 18px;
}
</style>