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
        <div class="loading-tip">Preventive Work Orders</div>
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
          <div class="title-icon preventive-icon">
            <el-icon><Calendar /></el-icon>
          </div>
          Preventive Work Orders
        </h1>
        <div class="header-stats">
          <div class="stat-badge">
            <el-icon><Grid /></el-icon>
            {{ totalOrders }} Total Orders
          </div>
          <div class="stat-badge">
            <el-icon><Clock /></el-icon>
            {{ scheduledCount }} Scheduled
          </div>
          <div class="stat-badge success">
            {{ completedCount }} Completed
          </div>
        </div>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleCreateOrder">
          <el-icon><Plus /></el-icon>
          Schedule Maintenance
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
        <div class="kpi-icon" style="background: #ecf5ff; color: #409eff;">📅</div>
        <div class="kpi-info">
          <div class="kpi-value">{{ scheduledThisMonth }}</div>
          <div class="kpi-label">Scheduled This Month</div>
          <div class="kpi-trend up">{{ scheduleTrend }}% vs last month</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon" style="background: #f0f9eb; color: #67c23a;">✅</div>
        <div class="kpi-info">
          <div class="kpi-value">{{ completedThisMonth }}</div>
          <div class="kpi-label">Completed This Month</div>
          <div class="kpi-trend up">{{ completionTrend }}% vs last month</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon" style="background: #fef0f0; color: #f56c6c;">⏰</div>
        <div class="kpi-info">
          <div class="kpi-value">{{ overdueCount }}</div>
          <div class="kpi-label">Overdue Tasks</div>
          <div class="kpi-trend up">{{ overdueTrend }}% vs last month</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon" style="background: #fdf6ec; color: #e6a23c;">🎯</div>
        <div class="kpi-info">
          <div class="kpi-value">{{ complianceRate }}%</div>
          <div class="kpi-label">PM Compliance Rate</div>
          <div class="kpi-trend up">Target: 95%</div>
        </div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-group">
        <el-input v-model="searchText" placeholder="Search by WO #, asset, or task..." size="default" style="width: 260px" clearable>
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="frequencyFilter" placeholder="Frequency" size="default" style="width: 130px" clearable>
          <el-option label="All" value="all" />
          <el-option label="Daily" value="daily" />
          <el-option label="Weekly" value="weekly" />
          <el-option label="Monthly" value="monthly" />
          <el-option label="Quarterly" value="quarterly" />
          <el-option label="Annually" value="annually" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" size="default" style="width: 130px" clearable>
          <el-option label="All" value="all" />
          <el-option label="Scheduled" value="scheduled" />
          <el-option label="In Progress" value="in_progress" />
          <el-option label="Completed" value="completed" />
          <el-option label="Missed" value="missed" />
        </el-select>
        <el-select v-model="assetTypeFilter" placeholder="Asset Type" size="default" style="width: 140px" clearable>
          <el-option label="All Assets" value="all" />
          <el-option label="UPS" value="UPS" />
          <el-option label="HVAC" value="HVAC" />
          <el-option label="CRAC" value="CRAC" />
          <el-option label="PDU" value="PDU" />
          <el-option label="Chiller" value="Chiller" />
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

    <!-- Preventive Maintenance Schedule Table -->
    <div class="card table-card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><List /></el-icon>
          Preventive Maintenance Schedule
        </div>
        <div class="table-info">
          Showing {{ paginatedOrders.length }} of {{ filteredOrders.length }} tasks
        </div>
      </div>
      <el-table :data="paginatedOrders" stripe border style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="woNumber" label="WO #" width="120" sortable />
        <el-table-column prop="taskName" label="Task Name" min-width="180" />
        <el-table-column prop="assetName" label="Asset" width="140" />
        <el-table-column prop="assetType" label="Asset Type" width="100">
          <template #default="{ row }">
            <el-tag :type="getAssetTypeTag(row.assetType)" size="small">{{ row.assetType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="frequency" label="Frequency" width="100">
          <template #default="{ row }">
            <el-tag :type="getFrequencyTag(row.frequency)" size="small">{{ getFrequencyText(row.frequency) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assignedTo" label="Assigned To" width="130" />
        <el-table-column prop="scheduledDate" label="Scheduled Date" width="110" sortable />
        <el-table-column prop="lastCompleted" label="Last Completed" width="110" sortable />
        <el-table-column prop="nextDue" label="Next Due" width="110" sortable>
          <template #default="{ row }">
            <span :class="{ 'overdue': isOverdue(row.nextDue, row.status) }">{{ row.nextDue }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" fixed="right" width="140">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewOrder(row)">
              <el-icon><View /></el-icon>
              View
            </el-button>
            <el-button type="success" link size="small" @click="executeTask(row)">
              <el-icon><VideoPlay /></el-icon>
              Execute
            </el-button>
            <el-dropdown @command="(cmd) => handleAction(cmd, row)">
              <el-button type="info" link size="small">
                More <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="reschedule">Reschedule</el-dropdown-item>
                  <el-dropdown-item command="assign">Reassign</el-dropdown-item>
                  <el-dropdown-item command="skip">Skip This Cycle</el-dropdown-item>
                  <el-dropdown-item command="history">View History</el-dropdown-item>
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

    <!-- Upcoming Tasks Calendar View -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><Calendar /></el-icon>
          Upcoming Tasks (Next 7 Days)
        </div>
      </div>
      <div class="upcoming-tasks">
        <div v-for="task in upcomingTasks" :key="task.id" class="upcoming-task" :class="task.priority">
          <div class="task-date">
            <div class="date-day">{{ task.day }}</div>
            <div class="date-num">{{ task.date }}</div>
          </div>
          <div class="task-info">
            <div class="task-name">{{ task.taskName }}</div>
            <div class="task-asset">{{ task.assetName }} ({{ task.assetType }})</div>
          </div>
          <div class="task-actions">
            <el-button size="small" type="primary" plain @click="quickExecute(task)">
              Execute
            </el-button>
            <el-button size="small" plain @click="rescheduleTask(task)">
              Reschedule
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- PM Statistics -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background: #f0f9eb; color: #67c23a;">✅</div>
        <div class="stat-info">
          <div class="stat-value">{{ onTimeCompletion }}%</div>
          <div class="stat-label">On-Time Completion</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #ecf5ff; color: #409eff;">⏱️</div>
        <div class="stat-info">
          <div class="stat-value">{{ avgTaskDuration }}<span class="unit">hours</span></div>
          <div class="stat-label">Avg Task Duration</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fdf6ec; color: #e6a23c;">🔧</div>
        <div class="stat-info">
          <div class="stat-value">{{ uptimeImprovement }}%</div>
          <div class="stat-label">Uptime Improvement</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fef0f0; color: #f56c6c;">💰</div>
        <div class="stat-info">
          <div class="stat-value">${{ costSavings }}K</div>
          <div class="stat-label">Cost Savings (YTD)</div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Order Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
        <el-form-item label="Task Name" prop="taskName">
          <el-input v-model="formData.taskName" placeholder="Enter task name" />
        </el-form-item>
        <el-form-item label="Asset" prop="assetName">
          <el-select v-model="formData.assetName" placeholder="Select asset" style="width: 100%">
            <el-option label="UPS-01" value="UPS-01" />
            <el-option label="UPS-02" value="UPS-02" />
            <el-option label="CRAC-01" value="CRAC-01" />
            <el-option label="CRAC-02" value="CRAC-02" />
            <el-option label="Chiller-01" value="Chiller-01" />
            <el-option label="PDU-A01" value="PDU-A01" />
          </el-select>
        </el-form-item>
        <el-form-item label="Asset Type" prop="assetType">
          <el-select v-model="formData.assetType" placeholder="Select asset type" style="width: 100%">
            <el-option label="UPS" value="UPS" />
            <el-option label="HVAC" value="HVAC" />
            <el-option label="CRAC" value="CRAC" />
            <el-option label="PDU" value="PDU" />
            <el-option label="Chiller" value="Chiller" />
          </el-select>
        </el-form-item>
        <el-form-item label="Frequency" prop="frequency">
          <el-select v-model="formData.frequency" placeholder="Select frequency" style="width: 100%">
            <el-option label="Daily" value="daily" />
            <el-option label="Weekly" value="weekly" />
            <el-option label="Monthly" value="monthly" />
            <el-option label="Quarterly" value="quarterly" />
            <el-option label="Annually" value="annually" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="Describe the maintenance task" />
        </el-form-item>
        <el-form-item label="Checklist" prop="checklist">
          <el-input v-model="formData.checklist" type="textarea" :rows="3" placeholder="List inspection items (one per line)" />
        </el-form-item>
        <el-form-item label="Assigned To" prop="assignedTo">
          <el-select v-model="formData.assignedTo" placeholder="Select technician" style="width: 100%">
            <el-option label="John Chen" value="John Chen" />
            <el-option label="Sarah Wong" value="Sarah Wong" />
            <el-option label="Mike Lim" value="Mike Lim" />
            <el-option label="David Wong" value="David Wong" />
          </el-select>
        </el-form-item>
        <el-form-item label="Start Date" prop="startDate">
          <el-date-picker v-model="formData.startDate" type="date" placeholder="Select start date" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitForm">Schedule</el-button>
      </template>
    </el-dialog>

    <!-- Execute Task Dialog -->
    <el-dialog v-model="executeDialogVisible" title="Execute Maintenance Task" width="550px">
      <el-form :model="executeForm" label-width="120px">
        <el-form-item label="Task">
          <span>{{ executeForm.taskName }}</span>
        </el-form-item>
        <el-form-item label="Asset">
          <span>{{ executeForm.assetName }}</span>
        </el-form-item>
        <el-form-item label="Completion Notes" required>
          <el-input v-model="executeForm.notes" type="textarea" :rows="3" placeholder="Enter completion notes" />
        </el-form-item>
        <el-form-item label="Hours Spent">
          <el-input-number v-model="executeForm.hours" :min="0.5" :max="24" :step="0.5" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Parts Used">
          <el-input v-model="executeForm.parts" placeholder="List parts used" />
        </el-form-item>
        <el-form-item label="Issues Found">
          <el-switch v-model="executeForm.issuesFound" active-text="Yes" inactive-text="No" />
        </el-form-item>
        <el-form-item v-if="executeForm.issuesFound" label="Issue Description">
          <el-input v-model="executeForm.issueDesc" type="textarea" :rows="2" placeholder="Describe issues found" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="executeDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmExecute">Complete Task</el-button>
      </template>
    </el-dialog>

    <!-- Order Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Preventive Task #${selectedOrder?.woNumber}`" width="700px">
      <el-descriptions :column="2" border v-if="selectedOrder">
        <el-descriptions-item label="WO Number">{{ selectedOrder.woNumber }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusTag(selectedOrder.status)">{{ getStatusText(selectedOrder.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Task Name" :span="2">{{ selectedOrder.taskName }}</el-descriptions-item>
        <el-descriptions-item label="Asset">{{ selectedOrder.assetName }}</el-descriptions-item>
        <el-descriptions-item label="Asset Type">{{ selectedOrder.assetType }}</el-descriptions-item>
        <el-descriptions-item label="Frequency">{{ getFrequencyText(selectedOrder.frequency) }}</el-descriptions-item>
        <el-descriptions-item label="Assigned To">{{ selectedOrder.assignedTo }}</el-descriptions-item>
        <el-descriptions-item label="Scheduled Date">{{ selectedOrder.scheduledDate }}</el-descriptions-item>
        <el-descriptions-item label="Last Completed">{{ selectedOrder.lastCompleted || '-' }}</el-descriptions-item>
        <el-descriptions-item label="Next Due">{{ selectedOrder.nextDue }}</el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedOrder.description }}</el-descriptions-item>
        <el-descriptions-item label="Checklist" :span="2">
          <ul class="checklist">
            <li v-for="(item, idx) in selectedOrder.checklistItems" :key="idx">{{ item }}</li>
          </ul>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Calendar, Grid, Clock, Plus, Refresh, Search, List, View, VideoPlay, ArrowDown } from '@element-plus/icons-vue'
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
  'Loading preventive schedules...',
  'Checking maintenance calendar...',
  'Initializing dashboard...',
  'Almost ready...'
]

// ==================== Data State ====================
const searchText = ref('')
const frequencyFilter = ref('all')
const statusFilter = ref('all')
const assetTypeFilter = ref('all')
const dateRange = ref<[Date, Date] | null>(null)
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const executeDialogVisible = ref(false)
const dialogTitle = ref('Schedule Preventive Maintenance')
const formRef = ref()
const selectedOrder = ref<any>(null)

const pagination = ref({ page: 1, pageSize: 15 })

// Date shortcuts
const dateShortcuts = [
  { text: 'This Week', value: () => {
      const now = new Date()
      const start = new Date(now.setDate(now.getDate() - now.getDay()))
      const end = new Date(now.setDate(now.getDate() + 6))
      return [start, end]
    }},
  { text: 'This Month', value: () => {
      const now = new Date()
      const start = new Date(now.getFullYear(), now.getMonth(), 1)
      const end = new Date(now.getFullYear(), now.getMonth() + 1, 0)
      return [start, end]
    }},
  { text: 'Next Month', value: () => {
      const now = new Date()
      const start = new Date(now.getFullYear(), now.getMonth() + 1, 1)
      const end = new Date(now.getFullYear(), now.getMonth() + 2, 0)
      return [start, end]
    }}
]

// Work Order Interface
interface PreventiveOrder {
  id: number
  woNumber: string
  taskName: string
  assetName: string
  assetType: string
  frequency: string
  status: string
  assignedTo: string
  scheduledDate: string
  lastCompleted: string | null
  nextDue: string
  description: string
  checklistItems: string[]
}

// Mock Preventive Work Orders Data
const workOrders = ref<PreventiveOrder[]>([
  { id: 1, woNumber: 'PM-001', taskName: 'UPS Battery Capacity Test', assetName: 'UPS-01', assetType: 'UPS', frequency: 'monthly', status: 'scheduled', assignedTo: 'John Chen', scheduledDate: '2024-06-15', lastCompleted: '2024-05-15', nextDue: '2024-06-15', description: 'Perform battery capacity test and record results', checklistItems: ['Check battery voltage', 'Test capacity under load', 'Record temperature', 'Inspect terminals'] },
  { id: 2, woNumber: 'PM-002', taskName: 'CRAC Filter Replacement', assetName: 'CRAC-01', assetType: 'CRAC', frequency: 'monthly', status: 'in_progress', assignedTo: 'Sarah Wong', scheduledDate: '2024-06-10', lastCompleted: '2024-05-10', nextDue: '2024-06-10', description: 'Replace air filters and clean coils', checklistItems: ['Replace pre-filters', 'Replace HEPA filters', 'Clean condenser coils', 'Check fan operation'] },
  { id: 3, woNumber: 'PM-003', taskName: 'Chiller Oil Analysis', assetName: 'Chiller-01', assetType: 'Chiller', frequency: 'quarterly', status: 'scheduled', assignedTo: 'Mike Lim', scheduledDate: '2024-06-20', lastCompleted: '2024-03-20', nextDue: '2024-06-20', description: 'Oil sampling and analysis for wear metals', checklistItems: ['Take oil sample', 'Check oil level', 'Inspect for leaks', 'Record operating parameters'] },
  { id: 4, woNumber: 'PM-004', taskName: 'PDU Firmware Update', assetName: 'PDU-A01', assetType: 'PDU', frequency: 'annually', status: 'scheduled', assignedTo: 'John Chen', scheduledDate: '2024-06-25', lastCompleted: '2023-06-25', nextDue: '2024-06-25', description: 'Update firmware to latest version', checklistItems: ['Backup configuration', 'Verify compatibility', 'Perform update', 'Test functionality'] },
  { id: 5, woNumber: 'PM-005', taskName: 'Cooling Tower Cleaning', assetName: 'CT-01', assetType: 'HVAC', frequency: 'quarterly', status: 'completed', assignedTo: 'David Wong', scheduledDate: '2024-05-28', lastCompleted: '2024-05-28', nextDue: '2024-08-28', description: 'Clean cooling tower basin and fill media', checklistItems: ['Drain and clean basin', 'Inspect fill media', 'Check water treatment', 'Test fan operation'] },
  { id: 6, woNumber: 'PM-006', taskName: 'UPS Thermal Imaging', assetName: 'UPS-02', assetType: 'UPS', frequency: 'monthly', status: 'scheduled', assignedTo: 'John Chen', scheduledDate: '2024-06-18', lastCompleted: '2024-05-18', nextDue: '2024-06-18', description: 'Thermal scan of all connections', checklistItems: ['Scan input connections', 'Scan output connections', 'Scan battery terminals', 'Document hot spots'] },
  { id: 7, woNumber: 'PM-007', taskName: 'CRAC Water Leak Detection', assetName: 'CRAC-02', assetType: 'CRAC', frequency: 'weekly', status: 'in_progress', assignedTo: 'Sarah Wong', scheduledDate: '2024-06-08', lastCompleted: '2024-06-01', nextDue: '2024-06-08', description: 'Check water sensors and drainage', checklistItems: ['Test leak sensors', 'Check drain lines', 'Inspect float switch', 'Verify alarm'] },
  { id: 8, woNumber: 'PM-008', taskName: 'Generator Load Test', assetName: 'GEN-01', assetType: 'Generator', frequency: 'monthly', status: 'scheduled', assignedTo: 'Mike Lim', scheduledDate: '2024-06-22', lastCompleted: '2024-05-22', nextDue: '2024-06-22', description: 'Monthly generator load bank test', checklistItems: ['Start generator', 'Apply load', 'Record parameters', 'Check fuel level'] }
])

// Statistics
const totalOrders = computed(() => workOrders.value.length)
const scheduledCount = computed(() => workOrders.value.filter(o => o.status === 'scheduled').length)
const completedCount = computed(() => workOrders.value.filter(o => o.status === 'completed').length)
const scheduledThisMonth = computed(() => 18)
const completedThisMonth = computed(() => 14)
const overdueCount = computed(() => workOrders.value.filter(o => {
  if (o.status === 'completed') return false
  return new Date(o.nextDue) < new Date()
}).length)
const complianceRate = computed(() => 92)
const onTimeCompletion = computed(() => 88)
const avgTaskDuration = computed(() => 2.5)
const uptimeImprovement = computed(() => 12)
const costSavings = computed(() => 45)

const scheduleTrend = ref(8)
const completionTrend = ref(5)
const overdueTrend = ref(3)

// Upcoming tasks (next 7 days)
const upcomingTasks = ref([
  { id: 1, day: 'MON', date: '10', taskName: 'CRAC Filter Replacement', assetName: 'CRAC-01', assetType: 'CRAC', priority: 'high' },
  { id: 2, day: 'TUE', date: '11', taskName: 'UPS Battery Test', assetName: 'UPS-01', assetType: 'UPS', priority: 'high' },
  { id: 3, day: 'WED', date: '12', taskName: 'PDU Firmware Check', assetName: 'PDU-A01', assetType: 'PDU', priority: 'medium' },
  { id: 4, day: 'THU', date: '13', taskName: 'Cooling Tower Inspection', assetName: 'CT-01', assetType: 'HVAC', priority: 'medium' },
  { id: 5, day: 'FRI', date: '14', taskName: 'Generator Load Test', assetName: 'GEN-01', assetType: 'Generator', priority: 'high' },
  { id: 6, day: 'SAT', date: '15', taskName: 'UPS Thermal Scan', assetName: 'UPS-02', assetType: 'UPS', priority: 'low' }
])

// Filtered orders
const filteredOrders = computed(() => {
  let filtered = workOrders.value

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(o =>
        o.woNumber.toLowerCase().includes(search) ||
        o.taskName.toLowerCase().includes(search) ||
        o.assetName.toLowerCase().includes(search)
    )
  }

  if (frequencyFilter.value !== 'all') {
    filtered = filtered.filter(o => o.frequency === frequencyFilter.value)
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
      const orderDate = new Date(o.scheduledDate)
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
const getFrequencyTag = (frequency: string) => {
  const map: Record<string, string> = {
    daily: 'danger',
    weekly: 'warning',
    monthly: 'primary',
    quarterly: 'success',
    annually: 'info'
  }
  return map[frequency] || 'info'
}

const getFrequencyText = (frequency: string) => {
  const map: Record<string, string> = {
    daily: 'Daily',
    weekly: 'Weekly',
    monthly: 'Monthly',
    quarterly: 'Quarterly',
    annually: 'Annually'
  }
  return map[frequency] || frequency
}

const getStatusTag = (status: string) => {
  const map: Record<string, string> = {
    scheduled: 'primary',
    in_progress: 'warning',
    completed: 'success',
    missed: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    scheduled: 'Scheduled',
    in_progress: 'In Progress',
    completed: 'Completed',
    missed: 'Missed'
  }
  return map[status] || status
}

const getAssetTypeTag = (type: string) => {
  const map: Record<string, string> = {
    UPS: 'danger',
    HVAC: 'warning',
    CRAC: 'warning',
    PDU: 'success',
    Chiller: 'primary',
    Generator: 'danger'
  }
  return map[type] || 'info'
}

const isOverdue = (nextDue: string, status: string) => {
  if (status === 'completed') return false
  return new Date(nextDue) < new Date()
}

// Form data
const formData = ref({
  taskName: '',
  assetName: '',
  assetType: '',
  frequency: 'monthly',
  description: '',
  checklist: '',
  assignedTo: '',
  startDate: ''
})

const executeForm = ref({
  taskName: '',
  assetName: '',
  notes: '',
  hours: 1,
  parts: '',
  issuesFound: false,
  issueDesc: ''
})

const formRules = {
  taskName: [{ required: true, message: 'Please enter task name', trigger: 'blur' }],
  assetName: [{ required: true, message: 'Please select asset', trigger: 'change' }],
  assetType: [{ required: true, message: 'Please select asset type', trigger: 'change' }],
  frequency: [{ required: true, message: 'Please select frequency', trigger: 'change' }],
  description: [{ required: true, message: 'Please enter description', trigger: 'blur' }],
  assignedTo: [{ required: true, message: 'Please select technician', trigger: 'change' }],
  startDate: [{ required: true, message: 'Please select start date', trigger: 'change' }]
}

// Actions
const handleCreateOrder = () => {
  dialogTitle.value = 'Schedule Preventive Maintenance'
  formData.value = {
    taskName: '',
    assetName: '',
    assetType: '',
    frequency: 'monthly',
    description: '',
    checklist: '',
    assignedTo: '',
    startDate: ''
  }
  dialogVisible.value = true
}

const viewOrder = (order: PreventiveOrder) => {
  selectedOrder.value = order
  detailDialogVisible.value = true
}

const executeTask = (order: PreventiveOrder) => {
  executeForm.value = {
    taskName: order.taskName,
    assetName: order.assetName,
    notes: '',
    hours: 1,
    parts: '',
    issuesFound: false,
    issueDesc: ''
  }
  executeDialogVisible.value = true
}

const quickExecute = (task: any) => {
  executeForm.value = {
    taskName: task.taskName,
    assetName: task.assetName,
    notes: '',
    hours: 1,
    parts: '',
    issuesFound: false,
    issueDesc: ''
  }
  executeDialogVisible.value = true
}

const rescheduleTask = (task: any) => {
  ElMessage.info(`Reschedule task: ${task.taskName}`)
}

const confirmExecute = () => {
  if (!executeForm.value.notes) {
    ElMessage.warning('Please enter completion notes')
    return
  }
  ElMessage.success('Task completed successfully')
  executeDialogVisible.value = false
}

const submitForm = async () => {
  try {
    await formRef.value?.validate()
    ElMessage.success('Preventive maintenance scheduled successfully')
    dialogVisible.value = false
  } catch (error) {
    ElMessage.error('Please fill all required fields')
  }
}

const handleAction = (command: string, order: PreventiveOrder) => {
  if (command === 'reschedule') {
    ElMessage.info(`Reschedule ${order.woNumber}`)
  } else if (command === 'assign') {
    ElMessage.info(`Reassign ${order.woNumber}`)
  } else if (command === 'skip') {
    ElMessageBox.confirm(`Skip this cycle for ${order.woNumber}?`, 'Confirm', {
      confirmButtonText: 'Skip',
      cancelButtonText: 'Cancel',
      type: 'warning'
    }).then(() => {
      ElMessage.success(`Task ${order.woNumber} skipped`)
    }).catch(() => {})
  } else if (command === 'history') {
    ElMessage.info(`View history for ${order.woNumber}`)
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

.preventive-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
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

.stat-badge.success {
  background: #f0f9eb;
  color: #67c23a;
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

/* Upcoming Tasks */
.upcoming-tasks {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.upcoming-task {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 12px 16px;
  background: #fafafa;
  border-radius: 12px;
  transition: all 0.2s;
  border-left: 4px solid #67c23a;
}

.upcoming-task:hover {
  background: #f5f7fa;
  transform: translateX(4px);
}

.upcoming-task.high { border-left-color: #f56c6c; }
.upcoming-task.medium { border-left-color: #e6a23c; }
.upcoming-task.low { border-left-color: #67c23a; }

.task-date {
  text-align: center;
  min-width: 60px;
}

.date-day {
  font-size: 12px;
  color: #909399;
  text-transform: uppercase;
}

.date-num {
  font-size: 24px;
  font-weight: 700;
  color: #1f2f3d;
}

.task-info {
  flex: 1;
}

.task-name {
  font-weight: 600;
  font-size: 14px;
  color: #1f2f3d;
  margin-bottom: 4px;
}

.task-asset {
  font-size: 12px;
  color: #909399;
}

.task-actions {
  display: flex;
  gap: 8px;
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

.checklist {
  margin: 0;
  padding-left: 20px;
}

.checklist li {
  font-size: 13px;
  color: #606266;
  margin: 4px 0;
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
  .upcoming-task {
    flex-direction: column;
    text-align: center;
  }
  .task-actions {
    justify-content: center;
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
</style>