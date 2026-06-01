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
        <div class="loading-tip">Assigned Faults</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Assigned Faults Page Content -->
  <div v-else class="assigned-faults-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <div class="title-badge">
          <el-icon><User /></el-icon>
          <span>FMS - My Work</span>
        </div>
        <h1>Assigned Faults</h1>
        <p class="subtitle">View and manage faults assigned to you and your team</p>
      </div>
      <div class="header-actions">
        <button class="action-btn" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          <span>Refresh</span>
        </button>
        <button class="action-btn primary" @click="exportReport">
          <el-icon><Download /></el-icon>
          <span>Export</span>
        </button>
        <select v-model="filterTeam" class="team-filter">
          <option value="all">All Teams</option>
          <option value="My Team">My Team</option>
          <option value="HVAC Team">HVAC Team</option>
          <option value="Electrical Team">Electrical Team</option>
          <option value="Facilities Team">Facilities Team</option>
          <option value="IT Team">IT Team</option>
        </select>
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-icon total">
          <el-icon><Document /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ assignedFaults.length }}</div>
          <div class="kpi-label">Assigned to Me</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon in-progress">
          <el-icon><Loading /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ inProgressCount }}</div>
          <div class="kpi-label">In Progress</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon overdue">
          <el-icon><WarningFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ overdueCount }}</div>
          <div class="kpi-label">Overdue</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon sla">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ slaCompliance }}%</div>
          <div class="kpi-label">SLA Compliance</div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <div class="filter-group">
        <label>Severity</label>
        <select v-model="filters.severity" class="filter-select">
          <option value="all">All Severities</option>
          <option value="critical">Critical</option>
          <option value="major">Major</option>
          <option value="minor">Minor</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Status</label>
        <select v-model="filters.status" class="filter-select">
          <option value="all">All Status</option>
          <option value="assigned">Assigned</option>
          <option value="in-progress">In Progress</option>
          <option value="pending-review">Pending Review</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Category</label>
        <select v-model="filters.category" class="filter-select">
          <option value="all">All Categories</option>
          <option value="HVAC">HVAC</option>
          <option value="Electrical">Electrical</option>
          <option value="Plumbing">Plumbing</option>
          <option value="Security">Security</option>
          <option value="DCIM">DCIM</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Search</label>
        <input type="text" v-model="filters.search" placeholder="Search by title or ID..." class="search-input" />
      </div>
    </div>

    <!-- Assigned Faults Table -->
    <div class="table-card">
      <el-table :data="paginatedFaults" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="Fault Title" min-width="200" show-overflow-tooltip />
        <el-table-column prop="category" label="Category" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityTag(row.severity)" size="small" effect="dark">
              {{ row.severity.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="130">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assignedTo" label="Assigned To" width="140" />
        <el-table-column prop="assignedAt" label="Assigned Date" width="110" sortable />
        <el-table-column prop="slaRemaining" label="SLA Remaining" width="120" sortable>
          <template #default="{ row }">
            <span :class="getSlaClass(row.slaRemaining)">{{ row.slaRemaining }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">View</el-button>
            <el-button link type="success" size="small" @click="startWork(row)" v-if="row.status === 'assigned'">Start</el-button>
            <el-button link type="warning" size="small" @click="updateProgress(row)" v-else>Update</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredFaults.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Fault Detail Drawer -->
    <el-drawer v-model="detailDrawerVisible" title="Fault Details" size="600px" direction="rtl">
      <div class="drawer-content" v-if="selectedFault">
        <div class="detail-section">
          <div class="detail-header">
            <h3>{{ selectedFault.title }}</h3>
            <div class="detail-badges">
              <el-tag :type="getSeverityTag(selectedFault.severity)" size="large">
                {{ selectedFault.severity.toUpperCase() }}
              </el-tag>
              <el-tag :type="getStatusTag(selectedFault.status)" size="large">
                {{ getStatusLabel(selectedFault.status) }}
              </el-tag>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <div class="detail-row">
            <span class="detail-label">Fault ID:</span>
            <span class="detail-value">#{{ selectedFault.id }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Category:</span>
            <span class="detail-value">{{ selectedFault.category }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Asset:</span>
            <span class="detail-value">{{ selectedFault.asset }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Location:</span>
            <span class="detail-value">{{ selectedFault.location }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Detected:</span>
            <span class="detail-value">{{ selectedFault.detectedAt }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Assigned To:</span>
            <span class="detail-value">{{ selectedFault.assignedTo }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Assigned At:</span>
            <span class="detail-value">{{ selectedFault.assignedAt }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">SLA Remaining:</span>
            <span class="detail-value" :class="getSlaClass(selectedFault.slaRemaining)">{{ selectedFault.slaRemaining }}</span>
          </div>
        </div>

        <div class="detail-section">
          <div class="detail-label">Description</div>
          <p class="detail-description">{{ selectedFault.description }}</p>
        </div>

        <div class="detail-section" v-if="selectedFault.symptoms">
          <div class="detail-label">Symptoms</div>
          <p class="detail-description">{{ selectedFault.symptoms }}</p>
        </div>

        <div class="detail-section" v-if="selectedFault.errorCode">
          <div class="detail-label">Error Code</div>
          <p class="detail-description">{{ selectedFault.errorCode }}</p>
        </div>

        <div class="detail-section">
          <div class="detail-label">Resolution Notes</div>
          <el-input
              v-model="resolutionNotes"
              type="textarea"
              :rows="4"
              placeholder="Add your investigation notes and resolution steps..."
          />
        </div>

        <div class="drawer-actions">
          <el-button v-if="selectedFault.status === 'assigned'" type="primary" @click="startWorkAction">
            <el-icon><VideoPlay /></el-icon> Start Work
          </el-button>
          <el-button v-if="selectedFault.status === 'in-progress'" type="success" @click="markForReview">
            <el-icon><Check /></el-icon> Mark for Review
          </el-button>
          <el-button type="info" @click="addComment">
            <el-icon><ChatLineRound /></el-icon> Add Comment
          </el-button>
        </div>
      </div>
    </el-drawer>

    <!-- Update Progress Dialog -->
    <el-dialog v-model="progressDialogVisible" title="Update Progress" width="450px">
      <div class="progress-content">
        <div class="progress-fault">
          <strong>{{ selectedFault?.title }}</strong>
        </div>
        <div class="progress-slider">
          <label>Completion Progress</label>
          <el-slider v-model="completionProgress" :min="0" :max="100" :step="10" :marks="{ 0: '0%', 50: '50%', 100: '100%' }" />
        </div>
        <div class="progress-notes">
          <label>Progress Notes</label>
          <textarea v-model="progressNotes" rows="3" placeholder="Describe what has been done..."></textarea>
        </div>
        <div class="progress-estimate">
          <label>Remaining Time Estimate</label>
          <select v-model="remainingEstimate">
            <option value="1h">1 hour</option>
            <option value="2h">2 hours</option>
            <option value="4h">4 hours</option>
            <option value="8h">8 hours</option>
            <option value="1d">1 day</option>
            <option value="2d">2 days</option>
          </select>
        </div>
      </div>
      <template #footer>
        <el-button @click="progressDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveProgress">Update Progress</el-button>
      </template>
    </el-dialog>

    <!-- Success Toast -->
    <div v-if="toastVisible" class="toast-notification success">
      <el-icon><CircleCheckFilled /></el-icon>
      <span>{{ toastMessage }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Refresh, Download, User, Document, Loading, WarningFilled,
  Timer, VideoPlay, Check, ChatLineRound, CircleCheckFilled
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// Loading State
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)
const loadingMessages = ['Preparing...', 'Loading assigned faults...', 'Fetching team data...', 'Almost ready...']

// Data Models
interface AssignedFault {
  id: number
  title: string
  category: string
  severity: 'critical' | 'major' | 'minor'
  status: 'assigned' | 'in-progress' | 'pending-review'
  asset: string
  location: string
  detectedAt: string
  assignedTo: string
  assignedAt: string
  slaRemaining: string
  description: string
  symptoms?: string
  errorCode?: string
  team: string
}

// State
const filterTeam = ref('all')
const filters = ref({
  severity: 'all',
  status: 'all',
  category: 'all',
  search: ''
})
const currentPage = ref(1)
const pageSize = ref(10)
const detailDrawerVisible = ref(false)
const progressDialogVisible = ref(false)
const selectedFault = ref<AssignedFault | null>(null)
const resolutionNotes = ref('')
const completionProgress = ref(0)
const progressNotes = ref('')
const remainingEstimate = ref('4h')
const toastVisible = ref(false)
const toastMessage = ref('')
let toastTimeout: ReturnType<typeof setTimeout> | null = null

// Mock Data - Assigned Faults
const assignedFaults = ref<AssignedFault[]>([
  { id: 1001, title: 'Chiller-02 High Pressure Trip', category: 'HVAC', severity: 'critical', status: 'in-progress', asset: 'Chiller-02', location: 'Building A - Plant Room', detectedAt: '2025-06-01 08:23:15', assignedTo: 'Mike Johnson', assignedAt: '2025-06-01 08:30:00', slaRemaining: '2h 15m', description: 'Chiller tripped on high pressure alarm. Cooling tower fan not responding.', symptoms: 'High pressure alarm, cooling tower fan not running', errorCode: 'CH-102', team: 'HVAC Team' },
  { id: 1002, title: 'UPS-01 Input Power Loss', category: 'Electrical', severity: 'critical', status: 'assigned', asset: 'UPS-01', location: 'Data Center - UPS Room', detectedAt: '2025-06-01 07:45:22', assignedTo: 'John Smith', assignedAt: '2025-06-01 08:00:00', slaRemaining: '3h 30m', description: 'UPS lost input power, running on battery.', errorCode: 'UPS-401', team: 'Electrical Team' },
  { id: 1003, title: 'Server Room Temperature High', category: 'DCIM', severity: 'critical', status: 'in-progress', asset: 'CRAC-03', location: 'Data Center - Row A', detectedAt: '2025-06-01 06:30:05', assignedTo: 'Sarah Chen', assignedAt: '2025-06-01 06:45:00', slaRemaining: '1h 45m', description: 'Server room temperature exceeded 32°C threshold.', team: 'Facilities Team' },
  { id: 1004, title: 'AHU-201 Filter Clogged', category: 'HVAC', severity: 'major', status: 'assigned', asset: 'AHU-201', location: 'Building B - Mechanical Room', detectedAt: '2025-05-31 22:15:30', assignedTo: 'Mike Johnson', assignedAt: '2025-05-31 22:30:00', slaRemaining: '6h', description: 'High differential pressure indicating clogged filters.', team: 'HVAC Team' },
  { id: 1005, title: 'Water Leak Detected', category: 'Plumbing', severity: 'major', status: 'pending-review', asset: 'LL-103', location: 'Building A - Basement', detectedAt: '2025-05-31 14:20:10', assignedTo: 'Tom Davis', assignedAt: '2025-05-31 14:35:00', slaRemaining: '1d 2h', description: 'Water leak detected in basement area.', team: 'Facilities Team' },
  { id: 1006, title: 'VFD-105 Overcurrent Fault', category: 'Electrical', severity: 'major', status: 'in-progress', asset: 'VFD-105', location: 'Building A - Electrical Room', detectedAt: '2025-05-31 11:35:42', assignedTo: 'John Smith', assignedAt: '2025-05-31 11:50:00', slaRemaining: '3h', description: 'VFD overcurrent fault during motor start.', team: 'Electrical Team' },
  { id: 1007, title: 'Access Control Reader Offline', category: 'Security', severity: 'minor', status: 'assigned', asset: 'RDR-208', location: 'Building B - Floor 1', detectedAt: '2025-05-31 09:00:00', assignedTo: 'Security Team', assignedAt: '2025-05-31 09:15:00', slaRemaining: '1d 8h', description: 'Access reader not communicating.', team: 'IT Team' },
  { id: 1008, title: 'BMS Gateway Communication Error', category: 'BMS', severity: 'minor', status: 'pending-review', asset: 'BMS-GW-01', location: 'Building B - BMS Room', detectedAt: '2025-05-30 20:30:00', assignedTo: 'Sarah Chen', assignedAt: '2025-05-30 20:45:00', slaRemaining: '12h', description: 'BMS gateway intermittent communication.', team: 'Facilities Team' }
])

// Computed
const inProgressCount = computed(() => assignedFaults.value.filter(f => f.status === 'in-progress').length)
const overdueCount = computed(() => assignedFaults.value.filter(f => {
  const remaining = f.slaRemaining
  return remaining.includes('h') && parseInt(remaining) < 2 && f.status !== 'pending-review'
}).length)
const slaCompliance = computed(() => 92)

const filteredFaults = computed(() => {
  let result = [...assignedFaults.value]
  if (filterTeam.value !== 'all') {
    result = result.filter(f => f.team === filterTeam.value)
  }
  if (filters.value.severity !== 'all') {
    result = result.filter(f => f.severity === filters.value.severity)
  }
  if (filters.value.status !== 'all') {
    result = result.filter(f => f.status === filters.value.status)
  }
  if (filters.value.category !== 'all') {
    result = result.filter(f => f.category === filters.value.category)
  }
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    result = result.filter(f =>
        f.title.toLowerCase().includes(search) ||
        f.id.toString().includes(search)
    )
  }
  return result
})

const paginatedFaults = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredFaults.value.slice(start, end)
})

// Helper Functions
const getSeverityTag = (severity: string) => {
  const map: Record<string, string> = { critical: 'danger', major: 'warning', minor: 'info' }
  return map[severity] || 'info'
}

const getStatusTag = (status: string) => {
  const map: Record<string, string> = { assigned: 'warning', 'in-progress': 'primary', 'pending-review': 'info' }
  return map[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = { assigned: 'Assigned', 'in-progress': 'In Progress', 'pending-review': 'Pending Review' }
  return map[status] || status
}

const getSlaClass = (sla: string) => {
  if (sla.includes('h')) {
    const hours = parseInt(sla)
    if (hours < 2) return 'sla-critical'
    if (hours < 4) return 'sla-warning'
  }
  return 'sla-normal'
}

const showToast = (message: string) => {
  toastMessage.value = message
  toastVisible.value = true
  if (toastTimeout) clearTimeout(toastTimeout)
  toastTimeout = setTimeout(() => {
    toastVisible.value = false
  }, 3000)
}

// Actions
const refreshData = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    showToast('Data refreshed')
  }, 500)
}

const exportReport = () => {
  ElMessage.info('Exporting assigned faults report...')
}

const viewDetails = (fault: AssignedFault) => {
  selectedFault.value = fault
  resolutionNotes.value = ''
  detailDrawerVisible.value = true
}

const startWork = (fault: AssignedFault) => {
  fault.status = 'in-progress'
  showToast(`Started work on fault #${fault.id}`)
}

const startWorkAction = () => {
  if (selectedFault.value) {
    selectedFault.value.status = 'in-progress'
    detailDrawerVisible.value = false
    showToast(`Started work on fault #${selectedFault.value.id}`)
  }
}

const updateProgress = (fault: AssignedFault) => {
  selectedFault.value = fault
  completionProgress.value = 0
  progressNotes.value = ''
  progressDialogVisible.value = true
}

const saveProgress = () => {
  if (selectedFault.value) {
    showToast(`Progress updated for fault #${selectedFault.value.id} (${completionProgress.value}% complete)`)
    progressDialogVisible.value = false
    if (completionProgress.value === 100) {
      selectedFault.value.status = 'pending-review'
    }
  }
}

const markForReview = () => {
  if (selectedFault.value) {
    selectedFault.value.status = 'pending-review'
    detailDrawerVisible.value = false
    showToast(`Fault #${selectedFault.value.id} marked for review`)
  }
}

const addComment = () => {
  ElMessage.info('Comment feature - would add note to fault')
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// Lifecycle
onMounted(() => {
  let idx = 0
  const msgInterval = setInterval(() => {
    if (idx < loadingMessages.length - 1) {
      idx++
      loadingMessage.value = loadingMessages[idx]
    }
  }, 400)
  const progInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)
  setTimeout(() => {
    clearInterval(msgInterval)
    clearInterval(progInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
    }, 400)
  }, 2000)
})
</script>

<style scoped>
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
.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
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

/* Main Content */
.assigned-faults-page {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}
.title-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  color: white;
  margin-bottom: 12px;
}
.header-title h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 8px 0;
}
.header-title .subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}
.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e2e8f0;
  background: white;
  color: #475569;
}
.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.action-btn.primary {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border: none;
  color: white;
}
.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
}
.team-filter {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: white;
  font-size: 13px;
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}
.kpi-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
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
.kpi-icon.total { background: #e8f4ff; color: #3b82f6; }
.kpi-icon.in-progress { background: #fef3c7; color: #d97706; }
.kpi-icon.overdue { background: #fee2e2; color: #dc2626; }
.kpi-icon.sla { background: #d1fae5; color: #059669; }
.kpi-info { flex: 1; }
.kpi-value { font-size: 28px; font-weight: 700; color: #1a1a2e; }
.kpi-label { font-size: 13px; color: #64748b; margin-top: 4px; }

/* Filters Bar */
.filters-bar {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: white;
  border-radius: 16px;
  align-items: flex-end;
}
.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.filter-group label {
  font-size: 12px;
  font-weight: 500;
  color: #64748b;
}
.filter-select, .search-input {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 13px;
  background: white;
  min-width: 130px;
}
.search-input { width: 200px; }

/* Table Card */
.table-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
.pagination-wrapper {
  padding-top: 16px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #e2e8f0;
  margin-top: 16px;
}
.sla-normal { color: #10b981; }
.sla-warning { color: #f59e0b; font-weight: 500; }
.sla-critical { color: #dc2626; font-weight: 600; }

/* Drawer Styles */
.drawer-content { padding: 16px; }
.detail-section {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}
.detail-section:last-child { border-bottom: none; }
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}
.detail-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0;
}
.detail-badges { display: flex; gap: 8px; }
.detail-row {
  display: flex;
  margin-bottom: 12px;
}
.detail-label {
  width: 110px;
  color: #64748b;
  font-size: 13px;
}
.detail-value {
  color: #1a1a2e;
  font-size: 13px;
  font-weight: 500;
}
.detail-description {
  color: #475569;
  font-size: 13px;
  line-height: 1.5;
  margin: 0;
}
.drawer-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

/* Progress Dialog */
.progress-content {
  padding: 8px 0;
}
.progress-fault {
  font-size: 14px;
  font-weight: 500;
  color: #1a1a2e;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
}
.progress-slider, .progress-notes, .progress-estimate {
  margin-bottom: 20px;
}
.progress-slider label, .progress-notes label, .progress-estimate label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #475569;
  margin-bottom: 8px;
}
.progress-notes textarea, .progress-estimate select {
  width: 100%;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 13px;
}
.progress-notes textarea {
  resize: vertical;
}

/* Toast Notification */
.toast-notification {
  position: fixed;
  bottom: 30px;
  right: 30px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 12px;
  background: #1e293b;
  color: white;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  z-index: 1100;
  animation: slideIn 0.3s ease;
}
.toast-notification.success .el-icon { color: #10b981; }
@keyframes slideIn {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

:deep(.el-table) { border-radius: 12px; }
:deep(.el-table th) { background-color: #fafafa; font-weight: 600; }
:deep(.el-drawer__header) { margin-bottom: 0; padding: 16px 20px; border-bottom: 1px solid #e2e8f0; }
</style>