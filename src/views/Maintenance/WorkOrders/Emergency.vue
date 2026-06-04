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
        <div class="loading-tip">Emergency Work Orders</div>
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
          <div class="title-icon emergency-icon">
            <el-icon><WarningFilled /></el-icon>
          </div>
          Emergency Work Orders
        </h1>
        <div class="header-stats">
          <div class="stat-badge critical">
            <span class="pulse-dot"></span>
            {{ activeEmergencyCount }} Active Emergencies
          </div>
          <div class="stat-badge">
            <el-icon><Clock /></el-icon>
            {{ avgResponseTime }} min avg response
          </div>
        </div>
      </div>
      <div class="header-right">
        <el-button type="danger" @click="handleCreateEmergency">
          <el-icon><Plus /></el-icon>
          Report Emergency
        </el-button>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Emergency SLA Dashboard -->
    <div class="sla-dashboard">
      <div class="sla-card">
        <div class="sla-header">
          <span class="sla-title">SLA Performance</span>
          <span class="sla-period">Last 30 Days</span>
        </div>
        <div class="sla-stats">
          <div class="sla-stat">
            <div class="stat-value">{{ slaMet }}<span class="unit">%</span></div>
            <div class="stat-label">SLA Met</div>
            <div class="stat-target">Target: 95%</div>
          </div>
          <div class="sla-stat">
            <div class="stat-value">{{ avgResponseTime }}<span class="unit">min</span></div>
            <div class="stat-label">Avg Response</div>
            <div class="stat-target">Target: 15 min</div>
          </div>
          <div class="sla-stat">
            <div class="stat-value">{{ avgResolutionTime }}<span class="unit">hrs</span></div>
            <div class="stat-label">Avg Resolution</div>
            <div class="stat-target">Target: 4 hrs</div>
          </div>
        </div>
        <div class="sla-progress">
          <div class="progress-label">SLA Compliance Trend</div>
          <div class="progress-bar-track">
            <div class="progress-bar-fill" :style="{ width: slaMet + '%', background: slaMet >= 90 ? '#67c23a' : '#e6a23c' }"></div>
          </div>
          <div class="progress-value">{{ slaMet }}%</div>
        </div>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="kpi-grid">
      <div class="kpi-card critical">
        <div class="kpi-icon">🔴</div>
        <div class="kpi-info">
          <div class="kpi-value">{{ criticalCount }}</div>
          <div class="kpi-label">Critical (P0)</div>
          <div class="kpi-trend up">Response: {{ criticalResponse }} min</div>
        </div>
      </div>
      <div class="kpi-card high">
        <div class="kpi-icon">🟠</div>
        <div class="kpi-info">
          <div class="kpi-value">{{ highCount }}</div>
          <div class="kpi-label">High (P1)</div>
          <div class="kpi-trend up">Response: {{ highResponse }} min</div>
        </div>
      </div>
      <div class="kpi-card medium">
        <div class="kpi-icon">🟡</div>
        <div class="kpi-info">
          <div class="kpi-value">{{ mediumCount }}</div>
          <div class="kpi-label">Medium (P2)</div>
          <div class="kpi-trend stable">Response: {{ mediumResponse }} min</div>
        </div>
      </div>
      <div class="kpi-card resolved">
        <div class="kpi-icon">✅</div>
        <div class="kpi-info">
          <div class="kpi-value">{{ resolvedToday }}</div>
          <div class="kpi-label">Resolved Today</div>
          <div class="kpi-trend up">+{{ resolvedTrend }}%</div>
        </div>
      </div>
    </div>

    <!-- Urgent Banner -->
    <div v-if="activeEmergencyCount > 0" class="urgent-banner">
      <el-alert
          :title="`${activeEmergencyCount} active emergency work orders require immediate attention!`"
          type="error"
          :closable="false"
          show-icon
      >
        <template #default>
          <el-button type="danger" size="small" @click="viewAllEmergencies">View All Emergencies</el-button>
        </template>
      </el-alert>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-group">
        <el-input v-model="searchText" placeholder="Search by WO #, asset, or issue..." size="default" style="width: 260px" clearable>
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="priorityFilter" placeholder="Priority" size="default" style="width: 130px" clearable>
          <el-option label="All" value="all" />
          <el-option label="Critical (P0)" value="critical" />
          <el-option label="High (P1)" value="high" />
          <el-option label="Medium (P2)" value="medium" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" size="default" style="width: 130px" clearable>
          <el-option label="All" value="all" />
          <el-option label="Open" value="open" />
          <el-option label="In Progress" value="in_progress" />
          <el-option label="Resolved" value="resolved" />
          <el-option label="Closed" value="closed" />
        </el-select>
        <el-select v-model="assetTypeFilter" placeholder="Asset Type" size="default" style="width: 140px" clearable>
          <el-option label="All Assets" value="all" />
          <el-option label="UPS" value="UPS" />
          <el-option label="HVAC" value="HVAC" />
          <el-option label="CRAC" value="CRAC" />
          <el-option label="PDU" value="PDU" />
          <el-option label="Chiller" value="Chiller" />
        </el-select>
      </div>
    </div>

    <!-- Emergency Work Orders Table -->
    <div class="card table-card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><List /></el-icon>
          Emergency Work Orders
          <el-badge :value="activeEmergencyCount" type="danger" v-if="activeEmergencyCount > 0" />
        </div>
        <div class="table-info">
          Showing {{ paginatedOrders.length }} of {{ filteredOrders.length }} emergencies
        </div>
      </div>
      <el-table :data="paginatedOrders" stripe border style="width: 100%" v-loading="tableLoading" :row-class-name="getRowClass">
        <el-table-column prop="woNumber" label="WO #" width="120" sortable />
        <el-table-column prop="title" label="Issue Title" min-width="200" />
        <el-table-column prop="assetName" label="Asset" width="140" />
        <el-table-column prop="assetType" label="Asset Type" width="100">
          <template #default="{ row }">
            <el-tag :type="getAssetTypeTag(row.assetType)" size="small">{{ row.assetType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="Priority" width="110">
          <template #default="{ row }">
            <el-tag :type="getPriorityTag(row.priority)" size="small">
              {{ getPriorityText(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reportedTime" label="Reported" width="140" sortable />
        <el-table-column prop="responseTime" label="Response" width="100" sortable>
          <template #default="{ row }">
            <span :class="{ 'overdue': row.responseTime > getSLATarget(row.priority) }">
              {{ row.responseTime }} min
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="assignedTo" label="Assigned To" width="130" />
        <el-table-column label="Actions" fixed="right" width="160">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewOrder(row)">
              <el-icon><View /></el-icon>
              Details
            </el-button>
            <el-button type="success" link size="small" @click="respondToEmergency(row)" v-if="row.status === 'open'">
              <el-icon><VideoPlay /></el-icon>
              Respond
            </el-button>
            <el-dropdown @command="(cmd) => handleAction(cmd, row)">
              <el-button type="info" link size="small">
                More <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="escalate">Escalate Priority</el-dropdown-item>
                  <el-dropdown-item command="reassign">Reassign Technician</el-dropdown-item>
                  <el-dropdown-item command="resolve">Mark Resolved</el-dropdown-item>
                  <el-dropdown-item command="close">Close WO</el-dropdown-item>
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

    <!-- Response Time Chart -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><TrendCharts /></el-icon>
          Emergency Response Time Trend (Last 7 Days)
        </div>
        <el-radio-group v-model="chartPeriod" size="small">
          <el-radio-button label="day">Daily</el-radio-button>
          <el-radio-button label="hour">Hourly</el-radio-button>
        </el-radio-group>
      </div>
      <div ref="responseChartRef" class="chart-container"></div>
    </div>

    <!-- Create Emergency Dialog -->
    <el-dialog v-model="dialogVisible" title="Report Emergency" width="550px">
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
        <el-form-item label="Issue Title" prop="title">
          <el-input v-model="formData.title" placeholder="Brief description of the emergency" />
        </el-form-item>
        <el-form-item label="Asset" prop="assetName">
          <el-select v-model="formData.assetName" placeholder="Select affected asset" style="width: 100%">
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
        <el-form-item label="Priority" prop="priority">
          <el-select v-model="formData.priority" placeholder="Select priority" style="width: 100%">
            <el-option label="Critical (P0) - System Down" value="critical" />
            <el-option label="High (P1) - Major Impact" value="high" />
            <el-option label="Medium (P2) - Limited Impact" value="medium" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="Detailed description of the issue" />
        </el-form-item>
        <el-form-item label="Reported By" prop="reportedBy">
          <el-input v-model="formData.reportedBy" placeholder="Your name" />
        </el-form-item>
        <el-form-item label="Location" prop="location">
          <el-input v-model="formData.location" placeholder="Building / Floor / Room" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="danger" @click="submitEmergency">Report Emergency</el-button>
      </template>
    </el-dialog>

    <!-- Respond Dialog -->
    <el-dialog v-model="respondDialogVisible" title="Respond to Emergency" width="550px">
      <el-form :model="respondForm" label-width="120px">
        <el-form-item label="WO Number">
          <span>{{ respondForm.woNumber }}</span>
        </el-form-item>
        <el-form-item label="Issue">
          <span>{{ respondForm.title }}</span>
        </el-form-item>
        <el-form-item label="Assigned To" required>
          <el-select v-model="respondForm.assignedTo" placeholder="Select technician" style="width: 100%">
            <el-option label="John Chen - Senior Technician" value="John Chen" />
            <el-option label="Sarah Wong - HVAC Specialist" value="Sarah Wong" />
            <el-option label="Mike Lim - Electrical Engineer" value="Mike Lim" />
            <el-option label="David Wong - UPS Expert" value="David Wong" />
          </el-select>
        </el-form-item>
        <el-form-item label="ETA (minutes)" required>
          <el-input-number v-model="respondForm.eta" :min="5" :max="120" :step="5" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Initial Assessment">
          <el-input v-model="respondForm.assessment" type="textarea" :rows="2" placeholder="Initial assessment of the issue" />
        </el-form-item>
        <el-form-item label="Parts Required">
          <el-input v-model="respondForm.parts" placeholder="List any parts needed" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="respondDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmResponse">Assign & Respond</el-button>
      </template>
    </el-dialog>

    <!-- Order Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Emergency Work Order #${selectedOrder?.woNumber}`" width="700px">
      <el-descriptions :column="2" border v-if="selectedOrder">
        <el-descriptions-item label="WO Number">{{ selectedOrder.woNumber }}</el-descriptions-item>
        <el-descriptions-item label="Priority">
          <el-tag :type="getPriorityTag(selectedOrder.priority)" size="small">{{ getPriorityText(selectedOrder.priority) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusTag(selectedOrder.status)" size="small">{{ getStatusText(selectedOrder.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Reported Time">{{ selectedOrder.reportedTime }}</el-descriptions-item>
        <el-descriptions-item label="Response Time">{{ selectedOrder.responseTime }} min</el-descriptions-item>
        <el-descriptions-item label="Resolution Time">{{ selectedOrder.resolutionTime || '-' }} min</el-descriptions-item>
        <el-descriptions-item label="Asset">{{ selectedOrder.assetName }}</el-descriptions-item>
        <el-descriptions-item label="Asset Type">{{ selectedOrder.assetType }}</el-descriptions-item>
        <el-descriptions-item label="Title" :span="2">{{ selectedOrder.title }}</el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedOrder.description }}</el-descriptions-item>
        <el-descriptions-item label="Root Cause" :span="2">{{ selectedOrder.rootCause || '-' }}</el-descriptions-item>
        <el-descriptions-item label="Resolution" :span="2">{{ selectedOrder.resolution || '-' }}</el-descriptions-item>
        <el-descriptions-item label="Assigned To">{{ selectedOrder.assignedTo || 'Unassigned' }}</el-descriptions-item>
        <el-descriptions-item label="Reported By">{{ selectedOrder.reportedBy }}</el-descriptions-item>
        <el-descriptions-item label="Location">{{ selectedOrder.location }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick,watch  } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'
import { WarningFilled, Grid, Clock, Plus, Refresh, Search, List, View, VideoPlay, ArrowDown, TrendCharts } from '@element-plus/icons-vue'
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
  'Loading emergency work orders...',
  'Checking SLA compliance...',
  'Initializing dashboard...',
  'Almost ready...'
]

// ==================== Data State ====================
const searchText = ref('')
const priorityFilter = ref('all')
const statusFilter = ref('all')
const assetTypeFilter = ref('all')
const chartPeriod = ref('day')
const dialogVisible = ref(false)
const respondDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const formRef = ref()
const selectedOrder = ref<any>(null)

const pagination = ref({ page: 1, pageSize: 15 })

// SLA Stats
const slaMet = ref(92)
const avgResponseTime = ref(12)
const avgResolutionTime = ref(3.5)
const activeEmergencyCount = ref(6)
const criticalResponse = ref(8)
const highResponse = ref(15)
const mediumResponse = ref(25)
const resolvedToday = ref(4)
const resolvedTrend = ref(12)

// KPI Counts
const criticalCount = ref(3)
const highCount = ref(2)
const mediumCount = ref(1)

// Emergency Order Interface
interface EmergencyOrder {
  id: number
  woNumber: string
  title: string
  assetName: string
  assetType: string
  priority: string
  status: string
  reportedTime: string
  responseTime: number
  resolutionTime: number | null
  assignedTo: string | null
  reportedBy: string
  description: string
  rootCause: string | null
  resolution: string | null
  location: string
}

// Mock Emergency Work Orders Data
const workOrders = ref<EmergencyOrder[]>([
  { id: 1, woNumber: 'EM-001', title: 'UPS-01 Complete Failure', assetName: 'UPS-01', assetType: 'UPS', priority: 'critical', status: 'in_progress', reportedTime: '2024-06-04 08:23:15', responseTime: 5, resolutionTime: null, assignedTo: 'John Chen', reportedBy: 'System', description: 'UPS output voltage dropped to 0V. All loads on bypass.', rootCause: null, resolution: null, location: 'Server Room A' },
  { id: 2, woNumber: 'EM-002', title: 'CRAC-01 High Temperature Alarm', assetName: 'CRAC-01', assetType: 'CRAC', priority: 'critical', status: 'open', reportedTime: '2024-06-04 09:45:22', responseTime: 12, resolutionTime: null, assignedTo: null, reportedBy: 'System', description: 'Return air temperature at 32°C, cooling capacity at 95%', rootCause: null, resolution: null, location: 'Data Center' },
  { id: 3, woNumber: 'EM-003', title: 'Chiller-01 Water Leak', assetName: 'Chiller-01', assetType: 'Chiller', priority: 'critical', status: 'in_progress', reportedTime: '2024-06-03 14:30:10', responseTime: 8, resolutionTime: null, assignedTo: 'Mike Lim', reportedBy: 'Technician', description: 'Water detected under chiller unit. Emergency containment deployed.', rootCause: null, resolution: null, location: 'Chiller Plant' },
  { id: 4, woNumber: 'EM-004', title: 'Network Switch Failure', assetName: 'SW-01', assetType: 'Network', priority: 'high', status: 'in_progress', reportedTime: '2024-06-03 16:20:45', responseTime: 15, resolutionTime: null, assignedTo: 'Sarah Wong', reportedBy: 'Network Team', description: 'Core switch port 24 failed. Traffic rerouted.', rootCause: null, resolution: null, location: 'Network Rack' },
  { id: 5, woNumber: 'EM-005', title: 'PDU-A01 Overload', assetName: 'PDU-A01', assetType: 'PDU', priority: 'high', status: 'resolved', reportedTime: '2024-06-02 22:15:30', responseTime: 18, resolutionTime: 45, assignedTo: 'John Chen', reportedBy: 'System', description: 'PDU load exceeded 95% capacity', rootCause: 'Overloaded circuit', resolution: 'Load redistributed to adjacent PDU', location: 'Server Row A' },
  { id: 6, woNumber: 'EM-006', title: 'Fire Alarm Activation', assetName: 'Fire Panel', assetType: 'Safety', priority: 'critical', status: 'closed', reportedTime: '2024-06-02 11:00:00', responseTime: 3, resolutionTime: 25, assignedTo: 'David Wong', reportedBy: 'Security', description: 'Smoke detector activation in server room', rootCause: 'False alarm - dust', resolution: 'Reset alarm, verified no fire', location: 'Server Room B' }
])

// Statistics
const filteredOrders = computed(() => {
  let filtered = workOrders.value

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(o =>
        o.woNumber.toLowerCase().includes(search) ||
        o.title.toLowerCase().includes(search) ||
        o.assetName.toLowerCase().includes(search)
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

  return filtered
})

const paginatedOrders = computed(() => {
  const start = (pagination.value.page - 1) * pagination.value.pageSize
  return filteredOrders.value.slice(start, start + pagination.value.pageSize)
})

// Response time data
const dailyResponseData = ref<number[]>([14, 12, 15, 11, 13, 10, 12])
const hourlyResponseData = ref<number[]>([15, 14, 13, 12, 11, 10, 12, 13, 14, 15, 13, 11, 10, 12, 14, 16, 18, 15, 13, 12, 11, 10, 9, 11])
const dayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const hourLabels = Array.from({ length: 24 }, (_, i) => `${i}:00`)

// Helper functions
const getSLATarget = (priority: string) => {
  const map: Record<string, number> = { critical: 15, high: 30, medium: 60 }
  return map[priority] || 30
}

const getPriorityTag = (priority: string) => {
  const map: Record<string, string> = { critical: 'danger', high: 'danger', medium: 'warning' }
  return map[priority] || 'info'
}

const getPriorityText = (priority: string) => {
  const map: Record<string, string> = { critical: 'Critical (P0)', high: 'High (P1)', medium: 'Medium (P2)' }
  return map[priority] || priority
}

const getStatusTag = (status: string) => {
  const map: Record<string, string> = { open: 'danger', in_progress: 'warning', resolved: 'success', closed: 'info' }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = { open: 'Open', in_progress: 'In Progress', resolved: 'Resolved', closed: 'Closed' }
  return map[status] || status
}

const getAssetTypeTag = (type: string) => {
  const map: Record<string, string> = { UPS: 'danger', HVAC: 'warning', CRAC: 'warning', PDU: 'success', Chiller: 'primary', Network: 'info', Safety: 'danger' }
  return map[type] || 'info'
}

const getRowClass = ({ row }: { row: EmergencyOrder }) => {
  if (row.priority === 'critical' && row.status !== 'resolved' && row.status !== 'closed') {
    return 'critical-row'
  }
  return ''
}

// Actions
const formData = ref({
  title: '',
  assetName: '',
  assetType: '',
  priority: 'high',
  description: '',
  reportedBy: '',
  location: ''
})

const respondForm = ref({
  woNumber: '',
  title: '',
  assignedTo: '',
  eta: 30,
  assessment: '',
  parts: ''
})

const formRules = {
  title: [{ required: true, message: 'Please enter title', trigger: 'blur' }],
  assetName: [{ required: true, message: 'Please select asset', trigger: 'change' }],
  assetType: [{ required: true, message: 'Please select asset type', trigger: 'change' }],
  priority: [{ required: true, message: 'Please select priority', trigger: 'change' }],
  description: [{ required: true, message: 'Please enter description', trigger: 'blur' }],
  reportedBy: [{ required: true, message: 'Please enter name', trigger: 'blur' }],
  location: [{ required: true, message: 'Please enter location', trigger: 'blur' }]
}

const handleCreateEmergency = () => {
  formData.value = {
    title: '',
    assetName: '',
    assetType: '',
    priority: 'high',
    description: '',
    reportedBy: '',
    location: ''
  }
  dialogVisible.value = true
}

const submitEmergency = async () => {
  try {
    await formRef.value?.validate()
    ElMessage.success('Emergency reported successfully. Response team notified.')
    dialogVisible.value = false
  } catch (error) {
    ElMessage.error('Please fill all required fields')
  }
}

const viewOrder = (order: EmergencyOrder) => {
  selectedOrder.value = order
  detailDialogVisible.value = true
}

const respondToEmergency = (order: EmergencyOrder) => {
  respondForm.value = {
    woNumber: order.woNumber,
    title: order.title,
    assignedTo: '',
    eta: 30,
    assessment: '',
    parts: ''
  }
  respondDialogVisible.value = true
}

const confirmResponse = () => {
  if (!respondForm.value.assignedTo) {
    ElMessage.warning('Please assign a technician')
    return
  }
  ElMessage.success(`Emergency ${respondForm.value.woNumber} acknowledged. Technician dispatched.`)
  respondDialogVisible.value = false
}

const viewAllEmergencies = () => {
  priorityFilter.value = 'critical'
  statusFilter.value = 'all'
}

const handleAction = (command: string, order: EmergencyOrder) => {
  if (command === 'escalate') {
    ElMessageBox.confirm(`Escalate priority for ${order.woNumber}?`, 'Confirm', {
      confirmButtonText: 'Escalate',
      cancelButtonText: 'Cancel',
      type: 'warning'
    }).then(() => {
      ElMessage.success(`Priority escalated for ${order.woNumber}`)
    }).catch(() => {})
  } else if (command === 'reassign') {
    ElMessage.info(`Reassign ${order.woNumber} to another technician`)
  } else if (command === 'resolve') {
    ElMessageBox.confirm(`Mark ${order.woNumber} as resolved?`, 'Confirm', {
      confirmButtonText: 'Resolve',
      cancelButtonText: 'Cancel',
      type: 'info'
    }).then(() => {
      order.status = 'resolved'
      order.resolutionTime = Math.floor(Math.random() * 60) + 30
      ElMessage.success(`Emergency ${order.woNumber} resolved`)
    }).catch(() => {})
  } else if (command === 'close') {
    ElMessageBox.confirm(`Close work order ${order.woNumber}?`, 'Confirm', {
      confirmButtonText: 'Close',
      cancelButtonText: 'Cancel',
      type: 'info'
    }).then(() => {
      order.status = 'closed'
      ElMessage.success(`Work order ${order.woNumber} closed`)
    }).catch(() => {})
  }
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  tableLoading.value = false
  refreshing.value = false
  ElMessage.success('Emergency data refreshed')
}

const handlePageSizeChange = () => { pagination.value.page = 1 }
const handlePageChange = () => {}

// ==================== Chart Functions ====================
const responseChartRef = ref<HTMLElement>()
let responseChart: echarts.ECharts | null = null

const initChart = () => {
  nextTick(() => {
    if (!responseChartRef.value) {
      setTimeout(initChart, 200)
      return
    }

    if (responseChart) responseChart.dispose()
    responseChart = echarts.init(responseChartRef.value)
    updateResponseChart()

    window.addEventListener('resize', () => responseChart?.resize())
  })
}

const updateResponseChart = () => {
  if (!responseChart) return

  const isDaily = chartPeriod.value === 'day'
  const data = isDaily ? dailyResponseData.value : hourlyResponseData.value
  const labels = isDaily ? dayLabels : hourLabels
  const targetLine = isDaily ? 15 : 15

  responseChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: { data: ['Response Time (min)', 'SLA Target'], textStyle: { color: '#606266' } },
    grid: { left: '8%', right: '5%', top: '15%', bottom: '5%', containLabel: true },
    xAxis: { type: 'category', data: labels, axisLabel: { rotate: isDaily ? 0 : 45, color: '#606266' }, axisLine: { lineStyle: { color: '#dcdfe6' } } },
    yAxis: { type: 'value', name: 'Response Time (minutes)', axisLabel: { color: '#606266' }, splitLine: { lineStyle: { color: '#ebeef5' } } },
    series: [
      { name: 'Response Time (min)', type: 'line', data: data, smooth: true, lineStyle: { color: '#f56c6c', width: 2 }, symbol: 'circle', symbolSize: 6, areaStyle: { opacity: 0.1, color: '#f56c6c' } },
      { name: 'SLA Target', type: 'line', data: Array(labels.length).fill(targetLine), lineStyle: { color: '#e6a23c', width: 2, type: 'dashed' }, symbol: 'none' }
    ]
  })
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
      nextTick(() => {
        setTimeout(() => {
          initChart()
        }, 100)
      })
    }, 500)
  }, 2500)
}

watch(chartPeriod, () => {
  updateResponseChart()
})

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

.emergency-icon {
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

/* SLA Dashboard */
.sla-dashboard {
  margin-bottom: 24px;
}

.sla-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.sla-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.sla-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

.sla-period {
  font-size: 12px;
  color: #909399;
}

.sla-stats {
  display: flex;
  gap: 32px;
  margin-bottom: 20px;
}

.sla-stat {
  text-align: center;
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
}

.stat-value .unit {
  font-size: 12px;
  font-weight: normal;
  color: #909399;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.stat-target {
  font-size: 11px;
  color: #c0c4cc;
  margin-top: 2px;
}

.sla-progress {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-label {
  font-size: 12px;
  color: #606266;
  min-width: 120px;
}

.progress-bar-track {
  flex: 1;
  height: 8px;
  background: #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s;
}

.progress-value {
  font-size: 14px;
  font-weight: 600;
  min-width: 45px;
  text-align: right;
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

.kpi-card.critical { border-left: 4px solid #f56c6c; }
.kpi-card.high { border-left: 4px solid #e6a23c; }
.kpi-card.medium { border-left: 4px solid #fbbf24; }
.kpi-card.resolved { border-left: 4px solid #67c23a; }

.kpi-icon {
  font-size: 32px;
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
.kpi-trend.stable { color: #909399; }

/* Urgent Banner */
.urgent-banner {
  margin-bottom: 20px;
}

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

/* Overdue text */
.overdue {
  color: #f56c6c;
  font-weight: 600;
}

/* Chart */
.chart-container {
  width: 100%;
  height: 320px;
  padding: 16px;
}

/* Critical row highlight */
:deep(.critical-row) {
  background-color: rgba(245, 108, 108, 0.05) !important;
}

/* Responsive */
@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .sla-stats {
    flex-direction: column;
    gap: 16px;
  }
}

@media (max-width: 900px) {
  .filter-group {
    flex-direction: column;
    align-items: stretch;
  }
  .filter-group .el-input,
  .filter-group .el-select {
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
  .sla-progress {
    flex-direction: column;
    align-items: stretch;
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

:deep(.el-alert) {
  border-radius: 12px;
}
</style>