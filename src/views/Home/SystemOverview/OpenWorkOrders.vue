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
        <div class="loading-tip">Not Developed Yet</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Open Work Orders Page Content -->
  <div v-else class="open-work-orders-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>Open Work Orders</h1>
        <p class="subtitle">View and manage all pending maintenance work orders</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" :icon="Plus" @click="handleCreateWorkOrder">
          New Work Order
        </el-button>
        <el-button :icon="Refresh" @click="fetchWorkOrders">Refresh</el-button>
      </div>
    </div>

    <!-- Filter Section -->
    <div class="filter-section">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="Type">
          <el-select v-model="filterForm.type" placeholder="All Types" clearable>
            <el-option label="Corrective" value="corrective" />
            <el-option label="Preventive" value="preventive" />
            <el-option label="Predictive" value="predictive" />
            <el-option label="Emergency" value="emergency" />
          </el-select>
        </el-form-item>
        <el-form-item label="Priority">
          <el-select v-model="filterForm.priority" placeholder="All Priorities" clearable>
            <el-option label="Critical" value="critical">
              <el-tag type="danger" size="small">Critical</el-tag>
            </el-option>
            <el-option label="High" value="high">
              <el-tag type="warning" size="small">High</el-tag>
            </el-option>
            <el-option label="Medium" value="medium">
              <el-tag type="primary" size="small">Medium</el-tag>
            </el-option>
            <el-option label="Low" value="low">
              <el-tag type="info" size="small">Low</el-tag>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="Status">
          <el-select v-model="filterForm.status" placeholder="All Statuses" clearable>
            <el-option label="Pending Assignment" value="pending" />
            <el-option label="In Progress" value="in_progress" />
            <el-option label="Under Review" value="review" />
            <el-option label="On Hold" value="on_hold" />
          </el-select>
        </el-form-item>
        <el-form-item label="Area">
          <el-cascader
              v-model="filterForm.area"
              :options="areaOptions"
              placeholder="Select Area"
              clearable
              :props="{ expandTrigger: 'hover' }"
          />
        </el-form-item>
        <el-form-item label="Created Date">
          <el-date-picker
              v-model="filterForm.dateRange"
              type="daterange"
              range-separator="to"
              start-placeholder="Start Date"
              end-placeholder="End Date"
              :shortcuts="dateShortcuts"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">Search</el-button>
          <el-button :icon="RefreshLeft" @click="resetFilters">Reset</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-cards">
      <div class="stat-card total">
        <div class="stat-icon">
          <el-icon :size="28"><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ workOrders.length }}</div>
          <div class="stat-label">Total Open Orders</div>
        </div>
      </div>
      <div class="stat-card critical">
        <div class="stat-icon">
          <el-icon :size="28"><WarningFilled /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ getOrdersByPriority('critical').length }}</div>
          <div class="stat-label">Critical Priority</div>
        </div>
      </div>
      <div class="stat-card progress">
        <div class="stat-icon">
          <el-icon :size="28"><Loading /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ getOrdersByStatus('in_progress').length }}</div>
          <div class="stat-label">In Progress</div>
        </div>
      </div>
      <div class="stat-card pending">
        <div class="stat-icon">
          <el-icon :size="28"><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ getOrdersByStatus('pending').length }}</div>
          <div class="stat-label">Pending Assignment</div>
        </div>
      </div>
    </div>

    <!-- Work Orders Table -->
    <div class="table-container">
      <el-table
          :data="paginatedOrders"
          stripe
          style="width: 100%"
          v-loading="tableLoading"
          @row-click="handleRowClick"
      >
        <el-table-column prop="workOrderNo" label="Work Order No." width="140" />
        <el-table-column prop="title" label="Title" min-width="200" show-overflow-tooltip />
        <el-table-column prop="type" label="Type" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.type)" size="small">
              {{ getTypeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="Priority" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityTagType(row.priority)" size="small" effect="dark">
              {{ getPriorityLabel(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="130">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assignedTo" label="Assigned To" width="140">
          <template #default="{ row }">
            <span :class="{ 'text-muted': !row.assignedTo }">
              {{ row.assignedTo || 'Unassigned' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="Created Date" width="120">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column prop="dueDate" label="Due Date" width="120">
          <template #default="{ row }">
            <span :class="{ 'text-danger': isOverdue(row.dueDate) }">
              {{ formatDate(row.dueDate) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click.stop="handleViewDetail(row)">
              View
            </el-button>
            <el-button link type="success" size="small" @click.stop="handleEdit(row)">
              Edit
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="filteredOrders.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Plus,
  Refresh,
  Search,
  RefreshLeft,
  Document,
  WarningFilled,
  Loading,
  Clock
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing...',
  'Almost ready...'
]

// ==================== Type Definitions ====================
interface WorkOrder {
  id: number
  workOrderNo: string
  title: string
  type: 'corrective' | 'preventive' | 'predictive' | 'emergency'
  priority: 'critical' | 'high' | 'medium' | 'low'
  status: 'pending' | 'in_progress' | 'review' | 'on_hold'
  assignedTo: string | null
  createdAt: string
  dueDate: string
  description?: string
  location?: string
  area?: string[]
}

// ==================== Mock Data ====================
const generateMockWorkOrders = (): WorkOrder[] => {
  const types: WorkOrder['type'][] = ['corrective', 'preventive', 'predictive', 'emergency']
  const priorities: WorkOrder['priority'][] = ['critical', 'high', 'medium', 'low']
  const statuses: WorkOrder['status'][] = ['pending', 'in_progress', 'review', 'on_hold']
  const titles = [
    'HVAC System Malfunction',
    'Chiller Pump Replacement',
    'Server Room Temperature Anomaly',
    'Lighting Control Panel Failure',
    'UPS Battery Replacement',
    'Fire Alarm System Test',
    'Cooling Tower Maintenance',
    'Access Control Door Repair',
    'CCTV Camera Firmware Update',
    'Generator Load Bank Test',
    'Water Leak Detection Sensor Calibration',
    'AHU Filter Replacement',
    'VAV Box Commissioning',
    'Electrical Panel Inspection',
    'BMS Controller Firmware Upgrade'
  ]
  const assignees = ['John Smith', 'Sarah Chen', 'Mike Johnson', 'Lisa Wong', null, null]

  return Array.from({ length: 45 }, (_, i) => {
    const createdAt = new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000)
    const dueDate = new Date(createdAt.getTime() + Math.random() * 14 * 24 * 60 * 60 * 1000)

    return {
      id: i + 1,
      workOrderNo: `WO-${String(i + 1).padStart(5, '0')}`,
      title: titles[Math.floor(Math.random() * titles.length)] + (i % 3 === 0 ? ' (Urgent)' : ''),
      type: types[Math.floor(Math.random() * types.length)],
      priority: priorities[Math.floor(Math.random() * priorities.length)],
      status: statuses[Math.floor(Math.random() * statuses.length)],
      assignedTo: assignees[Math.floor(Math.random() * assignees.length)],
      createdAt: createdAt.toISOString(),
      dueDate: dueDate.toISOString(),
      location: `Building ${Math.floor(Math.random() * 5) + 1}, Floor ${Math.floor(Math.random() * 10) + 1}`,
      area: ['Main Campus', 'Building A', `Floor ${Math.floor(Math.random() * 10) + 1}`]
    }
  })
}

const workOrders = ref<WorkOrder[]>([])

// ==================== Filter Form ====================
const filterForm = ref({
  type: '',
  priority: '',
  status: '',
  area: [],
  dateRange: null as [Date, Date] | null
})

const areaOptions = [
  {
    value: 'main-campus',
    label: 'Main Campus',
    children: [
      {
        value: 'building-a',
        label: 'Building A',
        children: [
          { value: 'floor-1', label: 'Floor 1' },
          { value: 'floor-2', label: 'Floor 2' },
          { value: 'floor-3', label: 'Floor 3' }
        ]
      },
      {
        value: 'building-b',
        label: 'Building B',
        children: [
          { value: 'floor-1', label: 'Floor 1' },
          { value: 'floor-2', label: 'Floor 2' }
        ]
      }
    ]
  },
  {
    value: 'data-center',
    label: 'Data Center',
    children: [
      { value: 'server-room', label: 'Server Room' },
      { value: 'ups-room', label: 'UPS Room' }
    ]
  }
]

const dateShortcuts = [
  {
    text: 'Today',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setHours(0, 0, 0, 0)
      return [start, end]
    }
  },
  {
    text: 'Last 7 Days',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setDate(start.getDate() - 7)
      return [start, end]
    }
  },
  {
    text: 'Last 30 Days',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setDate(start.getDate() - 30)
      return [start, end]
    }
  }
]

// ==================== Computed: Filtered Orders ====================
const filteredOrders = computed(() => {
  let result = [...workOrders.value]

  if (filterForm.value.type) {
    result = result.filter(o => o.type === filterForm.value.type)
  }
  if (filterForm.value.priority) {
    result = result.filter(o => o.priority === filterForm.value.priority)
  }
  if (filterForm.value.status) {
    result = result.filter(o => o.status === filterForm.value.status)
  }
  if (filterForm.value.dateRange && filterForm.value.dateRange[0] && filterForm.value.dateRange[1]) {
    const [start, end] = filterForm.value.dateRange
    result = result.filter(o => {
      const date = new Date(o.createdAt)
      return date >= start && date <= end
    })
  }

  return result
})

// ==================== Computed: Pagination ====================
const currentPage = ref(1)
const pageSize = ref(10)

const paginatedOrders = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredOrders.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    corrective: 'Corrective',
    preventive: 'Preventive',
    predictive: 'Predictive',
    emergency: 'Emergency'
  }
  return map[type] || type
}

const getTypeTagType = (type: string) => {
  const map: Record<string, string> = {
    corrective: 'warning',
    preventive: 'primary',
    predictive: 'info',
    emergency: 'danger'
  }
  return map[type] || 'info'
}

const getPriorityLabel = (priority: string) => {
  const map: Record<string, string> = {
    critical: 'Critical',
    high: 'High',
    medium: 'Medium',
    low: 'Low'
  }
  return map[priority] || priority
}

const getPriorityTagType = (priority: string) => {
  const map: Record<string, string> = {
    critical: 'danger',
    high: 'warning',
    medium: 'primary',
    low: 'info'
  }
  return map[priority] || 'info'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    pending: 'Pending',
    in_progress: 'In Progress',
    review: 'Under Review',
    on_hold: 'On Hold'
  }
  return map[status] || status
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'warning',
    in_progress: 'primary',
    review: 'info',
    on_hold: 'danger'
  }
  return map[status] || 'info'
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const isOverdue = (dueDate: string) => {
  return new Date(dueDate) < new Date() && new Date(dueDate).toDateString() !== new Date().toDateString()
}

const getOrdersByPriority = (priority: string) => {
  return workOrders.value.filter(o => o.priority === priority)
}

const getOrdersByStatus = (status: string) => {
  return workOrders.value.filter(o => o.status === status)
}

// ==================== Actions ====================
const fetchWorkOrders = async () => {
  tableLoading.value = true
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 800))
  workOrders.value = generateMockWorkOrders()
  tableLoading.value = false
  ElMessage.success('Work orders refreshed successfully')
}

const handleSearch = () => {
  currentPage.value = 1
  ElMessage.info(`Found ${filteredOrders.value.length} work orders`)
}

const resetFilters = () => {
  filterForm.value = {
    type: '',
    priority: '',
    status: '',
    area: [],
    dateRange: null
  }
  currentPage.value = 1
  ElMessage.info('Filters reset')
}

const handleCreateWorkOrder = () => {
  ElMessage.info('Create work order feature coming soon')
}

const handleViewDetail = (row: WorkOrder) => {
  ElMessage.info(`Viewing work order: ${row.workOrderNo}`)
}

const handleEdit = (row: WorkOrder) => {
  ElMessage.info(`Editing work order: ${row.workOrderNo}`)
}

const handleRowClick = (row: WorkOrder) => {
  // Optional: navigate to detail page
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
}

// ==================== Loading Animation ====================
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
    setTimeout(async () => {
      await fetchWorkOrders()
      isLoaded.value = true
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

/* ==================== Main Content ==================== */
.open-work-orders-page {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-title h1 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2f3d;
  margin: 0 0 4px 0;
}

.header-title .subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.filter-section {
  background: white;
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-form :deep(.el-form-item) {
  margin-bottom: 8px;
  margin-right: 16px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-card.total .stat-icon {
  background: #e8f4ff;
  color: #409eff;
}
.stat-card.critical .stat-icon {
  background: #ffe8e8;
  color: #f56c6c;
}
.stat-card.progress .stat-icon {
  background: #e8f8f0;
  color: #67c23a;
}
.stat-card.pending .stat-icon {
  background: #fff7e8;
  color: #e6a23c;
}

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
  color: #909399;
  margin-top: 4px;
}

.table-container {
  background: white;
  border-radius: 12px;
  padding: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

:deep(.el-table) {
  border-radius: 12px;
}

:deep(.el-table th.el-table__cell) {
  background-color: #fafafa;
  font-weight: 600;
  color: #1f2f3d;
}

.text-muted {
  color: #c0c4cc;
  font-style: italic;
}

.text-danger {
  color: #f56c6c;
  font-weight: 500;
}

.pagination-wrapper {
  padding: 20px 24px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
}

:deep(.el-table__row) {
  cursor: pointer;
  transition: background 0.2s;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa !important;
}
</style>