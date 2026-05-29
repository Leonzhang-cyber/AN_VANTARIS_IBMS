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
        <div class="loading-tip">Fault Management System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Active Faults Page Content -->
  <div v-else class="active-faults-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <div class="title-badge">
          <el-icon><WarningFilled /></el-icon>
          <span>FMS - Active Faults</span>
        </div>
        <h1>Active Faults</h1>
        <p class="subtitle">Monitor and manage all currently active system faults requiring attention</p>
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
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-icon critical">
          <el-icon><CircleCloseFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ criticalCount }}</div>
          <div class="kpi-label">Critical</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon major">
          <el-icon><WarningFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ majorCount }}</div>
          <div class="kpi-label">Major</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon minor">
          <el-icon><InfoFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ minorCount }}</div>
          <div class="kpi-label">Minor</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon total">
          <el-icon><List /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ totalActive }}</div>
          <div class="kpi-label">Total Active</div>
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
        <label>Category</label>
        <select v-model="filters.category" class="filter-select">
          <option value="all">All Categories</option>
          <option value="HVAC">HVAC</option>
          <option value="Electrical">Electrical</option>
          <option value="DCIM">DCIM</option>
          <option value="Security">Security</option>
          <option value="Plumbing">Plumbing</option>
          <option value="Lighting">Lighting</option>
          <option value="BMS">BMS</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Status</label>
        <select v-model="filters.status" class="filter-select">
          <option value="all">All Status</option>
          <option value="open">Open</option>
          <option value="investigating">Investigating</option>
          <option value="in-progress">In Progress</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Assigned To</label>
        <select v-model="filters.assignedTo" class="filter-select">
          <option value="all">All Technicians</option>
          <option value="Mike Johnson">Mike Johnson</option>
          <option value="John Smith">John Smith</option>
          <option value="Sarah Chen">Sarah Chen</option>
          <option value="Lisa Wong">Lisa Wong</option>
          <option value="Tom Davis">Tom Davis</option>
          <option value="Unassigned">Unassigned</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Search</label>
        <input type="text" v-model="filters.search" placeholder="Search by title or asset..." class="search-input" />
      </div>
      <button class="clear-btn" @click="clearFilters">Clear All</button>
    </div>

    <!-- Active Faults Table -->
    <div class="table-card">
      <el-table :data="paginatedFaults" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60"  />
        <el-table-column prop="title" label="Fault Title" width="350"  show-overflow-tooltip />
        <el-table-column prop="category" label="Category" >
          <template #default="{ row }">
            <el-tag size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="Severity" >
          <template #default="{ row }">
            <el-tag :type="getSeverityTagType(row.severity)" size="small" effect="dark">
              {{ row.severity.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" >
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="asset" label="Asset"  />
        <el-table-column prop="detectedAt" label="Detected" sortable />
        <el-table-column prop="duration" label="Duration" sortable />
        <el-table-column prop="assignedTo" label="Assigned To">
          <template #default="{ row }">
            <span :class="{ 'text-warning': row.assignedTo === 'Unassigned' }">
              {{ row.assignedTo }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="195" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewFault(row)">Details</el-button>
            <el-button link type="success" size="small" @click="assignFault(row)">Assign</el-button>
            <el-button link type="danger" size="small" @click="escalateFault(row)">Escalate</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="filteredFaults.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Fault Detail Drawer -->
    <el-drawer v-model="detailDrawerVisible" title="Fault Details" size="500px" direction="rtl">
      <div class="drawer-content" v-if="selectedFault">
        <div class="detail-section">
          <div class="detail-header">
            <h3>{{ selectedFault.title }}</h3>
            <div class="detail-badges">
              <el-tag :type="getSeverityTagType(selectedFault.severity)" size="large">
                {{ selectedFault.severity.toUpperCase() }}
              </el-tag>
              <el-tag :type="getStatusTagType(selectedFault.status)" size="large">
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
            <span class="detail-label">Duration:</span>
            <span class="detail-value">{{ selectedFault.duration }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Assigned To:</span>
            <span class="detail-value">{{ selectedFault.assignedTo }}</span>
          </div>
        </div>

        <div class="detail-section">
          <div class="detail-label">Description</div>
          <p class="detail-description">{{ selectedFault.description }}</p>
        </div>

        <div class="detail-section">
          <div class="detail-label">Root Cause Analysis</div>
          <p class="detail-description">{{ selectedFault.rootCause || 'Analysis in progress...' }}</p>
        </div>

        <div class="detail-section">
          <div class="detail-label">Recommended Actions</div>
          <ul class="action-list">
            <li v-for="action in selectedFault.recommendedActions" :key="action">{{ action }}</li>
          </ul>
        </div>

        <div class="drawer-actions">
          <el-button type="primary" @click="assignFault(selectedFault)">Assign to Me</el-button>
          <el-button type="warning" @click="escalateFault(selectedFault)">Escalate</el-button>
          <el-button type="success" @click="resolveFault(selectedFault)">Mark Resolved</el-button>
        </div>
      </div>
    </el-drawer>

    <!-- Assign Dialog -->
    <el-dialog v-model="assignDialogVisible" title="Assign Fault" width="400px">
      <div class="assign-content">
        <p>Assign fault <strong>#{{ assignTarget?.id }}</strong> to:</p>
        <select v-model="assignTo" class="assign-select">
          <option value="Mike Johnson">Mike Johnson (HVAC Specialist)</option>
          <option value="John Smith">John Smith (Electrical Engineer)</option>
          <option value="Sarah Chen">Sarah Chen (DCIM Engineer)</option>
          <option value="Lisa Wong">Lisa Wong (Lighting Tech)</option>
          <option value="Tom Davis">Tom Davis (Plumbing Specialist)</option>
        </select>
      </div>
      <template #footer>
        <el-button @click="assignDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmAssign">Assign</el-button>
      </template>
    </el-dialog>

    <!-- Escalate Dialog -->
    <el-dialog v-model="escalateDialogVisible" title="Escalate Fault" width="400px">
      <div class="escalate-content">
        <p>Escalate fault <strong>#{{ escalateTarget?.id }}</strong> to:</p>
        <select v-model="escalateTo" class="escalate-select">
          <option value="Facilities Manager">Facilities Manager</option>
          <option value="Director of Operations">Director of Operations</option>
          <option value="Emergency Response Team">Emergency Response Team</option>
        </select>
        <div class="escalate-reason">
          <label>Reason for escalation:</label>
          <textarea v-model="escalateReason" rows="3" placeholder="Provide reason for escalation..."></textarea>
        </div>
      </div>
      <template #footer>
        <el-button @click="escalateDialogVisible = false">Cancel</el-button>
        <el-button type="warning" @click="confirmEscalate">Escalate</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Refresh, Download, WarningFilled, CircleCloseFilled, InfoFilled,
  List, CaretTop, CaretBottom
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// Loading State
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)
const loadingMessages = ['Preparing...', 'Loading fault data...', 'Processing active faults...', 'Almost ready...']

// Data Models
interface ActiveFault {
  id: number
  title: string
  category: string
  severity: 'critical' | 'major' | 'minor'
  status: 'open' | 'investigating' | 'in-progress'
  asset: string
  location: string
  detectedAt: string
  duration: string
  assignedTo: string
  description: string
  rootCause: string
  recommendedActions: string[]
}

// State
const filters = ref({
  severity: 'all',
  category: 'all',
  status: 'all',
  assignedTo: 'all',
  search: ''
})
const currentPage = ref(1)
const pageSize = ref(10)
const detailDrawerVisible = ref(false)
const assignDialogVisible = ref(false)
const escalateDialogVisible = ref(false)
const selectedFault = ref<ActiveFault | null>(null)
const assignTarget = ref<ActiveFault | null>(null)
const escalateTarget = ref<ActiveFault | null>(null)
const assignTo = ref('Mike Johnson')
const escalateTo = ref('Facilities Manager')
const escalateReason = ref('')

// Mock Data - Active Faults
const activeFaults = ref<ActiveFault[]>([
  { id: 1001, title: 'AHU-101 Compressor High Discharge Pressure', category: 'HVAC', severity: 'critical', status: 'open', asset: 'AHU-101', location: 'Building A - Mechanical Room', detectedAt: '2025-05-29 08:23:15', duration: '2h 15m', assignedTo: 'Mike Johnson', description: 'Compressor discharge pressure has exceeded normal operating range. Possible causes: condenser fouling, refrigerant overcharge, or non-condensable gases.', rootCause: 'Under investigation', recommendedActions: ['Inspect condenser coils', 'Check refrigerant charge', 'Analyze compressor performance'] },
  { id: 1002, title: 'UPS-01 Battery String Voltage Imbalance', category: 'Electrical', severity: 'major', status: 'investigating', asset: 'UPS-01', location: 'Data Center - UPS Room', detectedAt: '2025-05-29 07:45:22', duration: '2h 53m', assignedTo: 'John Smith', description: 'Voltage imbalance detected across battery string. Individual battery monitoring required.', rootCause: 'Potential battery cell failure', recommendedActions: ['Perform individual battery testing', 'Check interconnecting cables', 'Schedule battery replacement'] },
  { id: 1003, title: 'Server Room Temperature High', category: 'DCIM', severity: 'critical', status: 'open', asset: 'Sensor-T-12', location: 'Data Center - Row A', detectedAt: '2025-05-29 06:30:05', duration: '4h 8m', assignedTo: 'Sarah Chen', description: 'Temperature at rack A3 inlet has exceeded 27°C threshold. Cooling system may be compromised.', rootCause: 'CRAC unit capacity insufficient', recommendedActions: ['Check CRAC operation', 'Verify airflow distribution', 'Review cooling setpoints'] },
  { id: 1004, title: 'Chiller-02 Evaporator Approach Temperature High', category: 'HVAC', severity: 'major', status: 'investigating', asset: 'Chiller-02', location: 'Building B - Plant Room', detectedAt: '2025-05-28 22:15:30', duration: '12h 23m', assignedTo: 'Mike Johnson', description: 'Evaporator approach temperature indicates potential fouling or refrigerant issues.', rootCause: 'Tube fouling suspected', recommendedActions: ['Schedule chiller maintenance', 'Analyze refrigerant quality', 'Check water treatment'] },
  { id: 1005, title: 'Water Leak Detection Sensor Alert', category: 'Plumbing', severity: 'major', status: 'in-progress', asset: 'LL-103', location: 'Building A - Basement', detectedAt: '2025-05-28 14:20:10', duration: '20h 18m', assignedTo: 'Tom Davis', description: 'Water leak detected in basement area near pump room.', rootCause: 'Leak located at pump seal', recommendedActions: ['Isolate water supply', 'Repair pump seal', 'Dry affected area'] },
  { id: 1006, title: 'VFD-105 Overcurrent Fault', category: 'Electrical', severity: 'critical', status: 'investigating', asset: 'VFD-105', location: 'Building A - Electrical Room', detectedAt: '2025-05-27 23:10:15', duration: '1d 11h', assignedTo: 'John Smith', description: 'VFD overcurrent fault triggered during motor start sequence.', rootCause: 'Motor bearing failure detected', recommendedActions: ['Inspect motor windings', 'Check for mechanical binding', 'Review VFD parameters'] },
  { id: 1007, title: 'FCU-205 Fan Motor Locked Rotor', category: 'HVAC', severity: 'major', status: 'open', asset: 'FCU-205', location: 'Building B - Floor 2', detectedAt: '2025-05-27 15:20:00', duration: '1d 19h', assignedTo: 'Mike Johnson', description: 'Fan motor failed to start, locked rotor condition detected.', rootCause: 'Motor failure', recommendedActions: ['Replace fan motor', 'Check capacitor', 'Verify power supply'] },
  { id: 1008, title: 'BMS Gateway Communication Intermittent', category: 'BMS', severity: 'minor', status: 'in-progress', asset: 'BMS-GW-01', location: 'Building B - BMS Room', detectedAt: '2025-05-27 11:00:00', duration: '1d 23h', assignedTo: 'Sarah Chen', description: 'BMS gateway experiencing intermittent communication loss to field controllers.', rootCause: 'Network congestion', recommendedActions: ['Check network switches', 'Review communication logs', 'Reset gateway'] },
  { id: 1009, title: 'Cooling Tower CT-01 Fan Vibration High', category: 'HVAC', severity: 'major', status: 'investigating', asset: 'CT-01', location: 'Building A - Roof', detectedAt: '2025-05-26 20:30:00', duration: '2d 14h', assignedTo: 'Mike Johnson', description: 'Vibration levels on cooling tower fan exceed acceptable limits.', rootCause: 'Bearing wear detected', recommendedActions: ['Inspect fan bearings', 'Check fan balance', 'Schedule maintenance'] },
  { id: 1010, title: 'Generator GEN-01 Fuel Level Low', category: 'Electrical', severity: 'critical', status: 'open', asset: 'GEN-01', location: 'Building B - Generator Room', detectedAt: '2025-05-26 14:15:00', duration: '2d 20h', assignedTo: 'Unassigned', description: 'Emergency generator fuel level below 25%. Refuel required.', rootCause: 'No recent refueling', recommendedActions: ['Schedule fuel delivery', 'Check for leaks', 'Verify fuel gauge accuracy'] },
  { id: 1011, title: 'Access Control Reader Offline', category: 'Security', severity: 'minor', status: 'open', asset: 'RDR-208', location: 'Building B - Security Office', detectedAt: '2025-05-26 09:00:00', duration: '3d 1h', assignedTo: 'Unassigned', description: 'Access control reader not communicating with controller.', rootCause: 'Network connection issue', recommendedActions: ['Check PoE connection', 'Verify network switch', 'Reboot reader'] },
  { id: 1012, title: 'Fire Alarm Panel Zone 3 Fault', category: 'Fire Safety', severity: 'critical', status: 'investigating', asset: 'FA-101', location: 'Building A - Fire Command', detectedAt: '2025-05-25 18:45:00', duration: '3d 16h', assignedTo: 'John Smith', description: 'Fire alarm panel reporting fault on Zone 3 circuit.', rootCause: 'Device communication failure', recommendedActions: ['Check zone wiring', 'Test individual devices', 'Verify panel configuration'] },
  { id: 1013, title: 'VAV Box Actuator Stuck', category: 'HVAC', severity: 'major', status: 'in-progress', asset: 'VAV-309', location: 'Building B - Floor 3', detectedAt: '2025-05-25 12:30:00', duration: '3d 22h', assignedTo: 'Mike Johnson', description: 'VAV box damper actuator not responding to control signals.', rootCause: 'Actuator motor failed', recommendedActions: ['Replace actuator', 'Check control wiring', 'Verify controller output'] },
  { id: 1014, title: 'Lighting Control Panel Communication Lost', category: 'Lighting', severity: 'minor', status: 'open', asset: 'LCP-05', location: 'Building A - Floor 3', detectedAt: '2025-05-25 08:00:00', duration: '4d 2h', assignedTo: 'Lisa Wong', description: 'Lighting control panel offline, manual override active.', rootCause: 'Network switch failure', recommendedActions: ['Check network connection', 'Power cycle panel', 'Verify switch status'] },
  { id: 1015, title: 'Server Room Humidity Low', category: 'DCIM', severity: 'minor', status: 'resolved', asset: 'Sensor-H-02', location: 'Data Center - Row B', detectedAt: '2025-05-24 22:00:00', duration: '4d 12h', assignedTo: 'Sarah Chen', description: 'Humidity level dropped below 40% threshold.', rootCause: 'Humidifier failure', recommendedActions: ['Check humidifier operation', 'Verify water supply', 'Clean humidifier elements'] }
])

// Computed
const criticalCount = computed(() => activeFaults.value.filter(f => f.severity === 'critical' && f.status !== 'resolved').length)
const majorCount = computed(() => activeFaults.value.filter(f => f.severity === 'major' && f.status !== 'resolved').length)
const minorCount = computed(() => activeFaults.value.filter(f => f.severity === 'minor' && f.status !== 'resolved').length)
const totalActive = computed(() => criticalCount.value + majorCount.value + minorCount.value)

const filteredFaults = computed(() => {
  let result = [...activeFaults.value]

  if (filters.value.severity !== 'all') {
    result = result.filter(f => f.severity === filters.value.severity)
  }
  if (filters.value.category !== 'all') {
    result = result.filter(f => f.category === filters.value.category)
  }
  if (filters.value.status !== 'all') {
    result = result.filter(f => f.status === filters.value.status)
  }
  if (filters.value.assignedTo !== 'all') {
    if (filters.value.assignedTo === 'Unassigned') {
      result = result.filter(f => f.assignedTo === 'Unassigned')
    } else {
      result = result.filter(f => f.assignedTo === filters.value.assignedTo)
    }
  }
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    result = result.filter(f =>
        f.title.toLowerCase().includes(search) ||
        f.asset.toLowerCase().includes(search) ||
        f.location.toLowerCase().includes(search)
    )
  }

  // Only show non-resolved faults
  result = result.filter(f => f.status !== 'resolved')

  return result
})

const paginatedFaults = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredFaults.value.slice(start, end)
})

// Helper Functions
const getSeverityTagType = (severity: string) => {
  const map: Record<string, string> = { critical: 'danger', major: 'warning', minor: 'info' }
  return map[severity] || 'info'
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = { open: 'danger', investigating: 'warning', 'in-progress': 'primary', resolved: 'success' }
  return map[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = { open: 'Open', investigating: 'Investigating', 'in-progress': 'In Progress', resolved: 'Resolved' }
  return map[status] || status
}

const clearFilters = () => {
  filters.value = {
    severity: 'all',
    category: 'all',
    status: 'all',
    assignedTo: 'all',
    search: ''
  }
  currentPage.value = 1
}

// Actions
const refreshData = async () => {
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  ElMessage.success('Active faults data refreshed')
  tableLoading.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting active faults report...')
}

const viewFault = (fault: ActiveFault) => {
  selectedFault.value = fault
  detailDrawerVisible.value = true
}

const assignFault = (fault: ActiveFault) => {
  assignTarget.value = fault
  assignTo.value = fault.assignedTo !== 'Unassigned' ? fault.assignedTo : 'Mike Johnson'
  assignDialogVisible.value = true
}

const confirmAssign = () => {
  if (assignTarget.value) {
    assignTarget.value.assignedTo = assignTo.value
    ElMessage.success(`Fault #${assignTarget.value.id} assigned to ${assignTo.value}`)
    assignDialogVisible.value = false
  }
}

const escalateFault = (fault: ActiveFault) => {
  escalateTarget.value = fault
  escalateReason.value = ''
  escalateDialogVisible.value = true
}

const confirmEscalate = () => {
  if (escalateTarget.value && escalateReason.value) {
    ElMessage.warning(`Fault #${escalateTarget.value.id} escalated to ${escalateTo.value}`)
    escalateDialogVisible.value = false
  } else {
    ElMessage.warning('Please provide a reason for escalation')
  }
}

const resolveFault = (fault: ActiveFault) => {
  ElMessage.success(`Fault #${fault.id} marked as resolved`)
  detailDrawerVisible.value = false
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
    setTimeout(() => { isLoaded.value = true }, 400)
  }, 2000)
})
</script>

<style scoped>
/* Loading Screen */
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
.active-faults-page {
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
  background: linear-gradient(135deg, #ef4444, #dc2626);
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
.kpi-icon.critical { background: #fee2e2; color: #dc2626; }
.kpi-icon.major { background: #fef3c7; color: #d97706; }
.kpi-icon.minor { background: #dbeafe; color: #2563eb; }
.kpi-icon.total { background: #e8f4ff; color: #3b82f6; }
.kpi-info { flex: 1; }
.kpi-value { font-size: 28px; font-weight: 700; color: #1a1a2e; }
.kpi-label { font-size: 13px; color: #64748b; margin-top: 4px; }

/* Filters Bar */
.filters-bar {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 24px;
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
.search-input {
  width: 200px;
}
.clear-btn {
  padding: 8px 20px;
  background: #f1f5f9;
  border: none;
  border-radius: 10px;
  color: #64748b;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  align-self: center;
}
.clear-btn:hover {
  background: #e2e8f0;
}

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
.text-warning {
  color: #d97706;
  font-style: italic;
}

/* Drawer Styles */
.drawer-content {
  padding: 16px;
}
.detail-section {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}
.detail-section:last-child {
  border-bottom: none;
}
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
.detail-badges {
  display: flex;
  gap: 8px;
}
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
.action-list {
  margin: 8px 0 0;
  padding-left: 20px;
}
.action-list li {
  color: #475569;
  font-size: 13px;
  margin-bottom: 6px;
}
.drawer-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

/* Dialog Styles */
.assign-content, .escalate-content {
  padding: 8px 0;
}
.assign-select, .escalate-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  margin-top: 12px;
}
.escalate-reason {
  margin-top: 16px;
}
.escalate-reason label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #475569;
  margin-bottom: 8px;
}
.escalate-reason textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 13px;
  resize: vertical;
}

:deep(.el-table) { border-radius: 12px; }
:deep(.el-table th) { background-color: #fafafa; font-weight: 600; }
:deep(.el-drawer__header) { margin-bottom: 0; padding: 16px 20px; border-bottom: 1px solid #e2e8f0; }
</style>