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
        <div class="loading-tip">Incident Reporting System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="incident-reporting">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Incident Reporting</h2>
        <p class="subtitle">Log, track and manage facility incidents and safety events</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openReportDialog">
          <el-icon><Plus /></el-icon> Report Incident
        </el-button>
        <el-button @click="refreshData">
          <el-icon><RefreshRight /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total">📋</div>
        <div class="stat-info">
          <div class="stat-value">{{ incidents.length }}</div>
          <div class="stat-label">Total Incidents</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon open">🟡</div>
        <div class="stat-info">
          <div class="stat-value">{{ openCount }}</div>
          <div class="stat-label">Open</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon resolved">✅</div>
        <div class="stat-info">
          <div class="stat-value">{{ resolvedCount }}</div>
          <div class="stat-label">Resolved</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon critical">🚨</div>
        <div class="stat-info">
          <div class="stat-value">{{ criticalCount }}</div>
          <div class="stat-label">Critical</div>
        </div>
      </div>
    </div>

    <!-- Search and Filter Bar -->
    <div class="filter-section">
      <div class="search-wrapper">
        <el-input v-model="searchText" placeholder="Search incidents by title, location or description..." clearable :prefix-icon="Search" />
      </div>
      <div class="filter-wrapper">
        <el-select v-model="filterStatus" placeholder="Status" clearable>
          <el-option label="All Status" value="all" />
          <el-option label="Open" value="open" />
          <el-option label="Investigating" value="investigating" />
          <el-option label="Resolved" value="resolved" />
          <el-option label="Closed" value="closed" />
        </el-select>
        <el-select v-model="filterSeverity" placeholder="Severity" clearable>
          <el-option label="All Severities" value="all" />
          <el-option label="Critical" value="critical" />
          <el-option label="High" value="high" />
          <el-option label="Medium" value="medium" />
          <el-option label="Low" value="low" />
        </el-select>
        <el-select v-model="filterType" placeholder="Type" clearable>
          <el-option label="All Types" value="all" />
          <el-option label="Safety" value="safety" />
          <el-option label="Security" value="security" />
          <el-option label="Equipment" value="equipment" />
          <el-option label="Environmental" value="environmental" />
          <el-option label="Other" value="other" />
        </el-select>
      </div>
    </div>

    <!-- Incidents List -->
    <div class="incidents-list">
      <div v-for="incident in filteredIncidents" :key="incident.id" class="incident-card" :class="incident.severity">
        <div class="card-header">
          <div class="header-left">
            <span class="incident-id">#{{ incident.id }}</span>
            <span class="incident-title">{{ incident.title }}</span>
          </div>
          <div class="header-right">
            <span :class="['severity-badge', incident.severity]">{{ getSeverityLabel(incident.severity) }}</span>
            <span :class="['status-badge', incident.status]">{{ getStatusLabel(incident.status) }}</span>
          </div>
        </div>
        <div class="card-body">
          <div class="incident-details">
            <div class="detail-item">
              <span class="detail-icon">📍</span>
              <span>{{ incident.location }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-icon">🕐</span>
              <span>{{ formatDateTime(incident.reportedAt) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-icon">👤</span>
              <span>Reported by: {{ incident.reportedBy }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-icon">🏷️</span>
              <span>{{ getTypeLabel(incident.type) }}</span>
            </div>
          </div>
          <div class="incident-description">{{ incident.description }}</div>
          <div v-if="incident.resolution" class="incident-resolution">
            <span class="resolution-label">Resolution:</span>
            <span>{{ incident.resolution }}</span>
          </div>
        </div>
        <div class="card-footer">
          <div class="footer-left">
            <span v-if="incident.assignedTo" class="assigned-to">
              <el-icon><User /></el-icon> Assigned: {{ incident.assignedTo }}
            </span>
          </div>
          <div class="footer-right">
            <el-button size="small" type="info" @click="viewDetails(incident)">Details</el-button>
            <el-button v-if="incident.status !== 'resolved' && incident.status !== 'closed'" size="small" type="success" @click="resolveIncident(incident)">Resolve</el-button>
            <el-button size="small" type="danger" @click="deleteIncident(incident)">Delete</el-button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredIncidents.length === 0" class="empty-state">
        <div class="empty-icon">📋</div>
        <div class="empty-title">No incidents found</div>
        <div class="empty-desc">Report an incident to start tracking</div>
        <el-button type="primary" @click="openReportDialog">Report Incident</el-button>
      </div>
    </div>

    <!-- Report Incident Dialog -->
    <el-dialog v-model="showReportDialog" title="Report Incident" width="600px" class="incident-dialog">
      <el-form :model="incidentForm" label-width="100px">
        <el-form-item label="Title" required>
          <el-input v-model="incidentForm.title" placeholder="Enter incident title" />
        </el-form-item>
        <el-form-item label="Location" required>
          <el-input v-model="incidentForm.location" placeholder="Enter location" />
        </el-form-item>
        <el-form-item label="Type">
          <el-select v-model="incidentForm.type" style="width: 100%">
            <el-option label="Safety" value="safety" />
            <el-option label="Security" value="security" />
            <el-option label="Equipment" value="equipment" />
            <el-option label="Environmental" value="environmental" />
            <el-option label="Other" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="Severity">
          <el-select v-model="incidentForm.severity" style="width: 100%">
            <el-option label="Critical" value="critical" />
            <el-option label="High" value="high" />
            <el-option label="Medium" value="medium" />
            <el-option label="Low" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description" required>
          <el-input v-model="incidentForm.description" type="textarea" :rows="4" placeholder="Describe the incident..." />
        </el-form-item>
        <el-form-item label="Assigned To">
          <el-select v-model="incidentForm.assignedTo" placeholder="Assign to team member" clearable style="width: 100%">
            <el-option label="John Zhang" value="John Zhang" />
            <el-option label="Sarah Li" value="Sarah Li" />
            <el-option label="Mike Wang" value="Mike Wang" />
            <el-option label="Emma Zhao" value="Emma Zhao" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showReportDialog = false">Cancel</el-button>
        <el-button type="primary" @click="submitIncident">Report Incident</el-button>
      </template>
    </el-dialog>

    <!-- Incident Details Dialog -->
    <el-dialog v-model="showDetailDialog" :title="`Incident #${selectedIncident?.id}`" width="650px" class="incident-dialog">
      <div v-if="selectedIncident" class="incident-detail">
        <div class="detail-header">
          <div class="detail-badges">
            <span :class="['severity-badge large', selectedIncident.severity]">{{ getSeverityLabel(selectedIncident.severity) }}</span>
            <span :class="['status-badge large', selectedIncident.status]">{{ getStatusLabel(selectedIncident.status) }}</span>
          </div>
        </div>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Title" :span="2">{{ selectedIncident.title }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedIncident.location }}</el-descriptions-item>
          <el-descriptions-item label="Type">{{ getTypeLabel(selectedIncident.type) }}</el-descriptions-item>
          <el-descriptions-item label="Reported By">{{ selectedIncident.reportedBy }}</el-descriptions-item>
          <el-descriptions-item label="Reported At">{{ formatDateTime(selectedIncident.reportedAt) }}</el-descriptions-item>
          <el-descriptions-item label="Assigned To">{{ selectedIncident.assignedTo || 'Unassigned' }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedIncident.description }}</el-descriptions-item>
          <el-descriptions-item v-if="selectedIncident.resolution" label="Resolution" :span="2">{{ selectedIncident.resolution }}</el-descriptions-item>
          <el-descriptions-item v-if="selectedIncident.resolvedAt" label="Resolved At">{{ formatDateTime(selectedIncident.resolvedAt) }}</el-descriptions-item>
          <el-descriptions-item v-if="selectedIncident.resolvedBy" label="Resolved By">{{ selectedIncident.resolvedBy }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">Close</el-button>
        <el-button v-if="selectedIncident?.status !== 'resolved' && selectedIncident?.status !== 'closed'" type="success" @click="resolveIncident(selectedIncident); showDetailDialog = false">Resolve</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus, RefreshRight, Search, User } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Loading incident reporting system...',
  'Fetching recent incidents...',
  'Analyzing incident data...',
  'Ready for reporting...'
]

// Types
interface Incident {
  id: number
  title: string
  location: string
  type: string
  severity: string
  status: string
  description: string
  reportedBy: string
  reportedAt: string
  assignedTo: string | null
  resolution: string | null
  resolvedAt: string | null
  resolvedBy: string | null
}

// Helper functions
const getCurrentTimestamp = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

const formatDateTime = (timestamp: string) => {
  if (!timestamp) return 'N/A'
  const date = new Date(timestamp)
  return date.toLocaleString()
}

const getSeverityLabel = (severity: string) => {
  const labels: Record<string, string> = {
    critical: 'Critical',
    high: 'High',
    medium: 'Medium',
    low: 'Low'
  }
  return labels[severity] || severity
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    open: 'Open',
    investigating: 'Investigating',
    resolved: 'Resolved',
    closed: 'Closed'
  }
  return labels[status] || status
}

const getTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    safety: 'Safety',
    security: 'Security',
    equipment: 'Equipment',
    environmental: 'Environmental',
    other: 'Other'
  }
  return labels[type] || type
}

// Sample incidents data
const incidents = ref<Incident[]>([
  {
    id: 1001,
    title: 'Water Leak in Server Room',
    location: 'Data Center A - Server Room',
    type: 'equipment',
    severity: 'critical',
    status: 'investigating',
    description: 'Water detected under raised floor near CRAC unit. Possible condensate drain blockage.',
    reportedBy: 'John Zhang',
    reportedAt: getCurrentTimestamp(),
    assignedTo: 'Mike Wang',
    resolution: null,
    resolvedAt: null,
    resolvedBy: null
  },
  {
    id: 1002,
    title: 'Unauthorized Access Attempt',
    location: 'Main Entrance - East Door',
    type: 'security',
    severity: 'high',
    status: 'open',
    description: 'Failed badge swipe attempt after hours. Security camera shows individual trying multiple cards.',
    reportedBy: 'Security System',
    reportedAt: getCurrentTimestamp(),
    assignedTo: 'Sarah Li',
    resolution: null,
    resolvedAt: null,
    resolvedBy: null
  },
  {
    id: 1003,
    title: 'Elevator Malfunction',
    location: 'North Tower - Elevator 3',
    type: 'equipment',
    severity: 'high',
    status: 'resolved',
    description: 'Elevator stuck between floors for 15 minutes. All passengers safely evacuated.',
    reportedBy: 'Emma Zhao',
    reportedAt: getCurrentTimestamp(),
    assignedTo: 'David Sun',
    resolution: 'Reset controller and tested operation. Elevator returned to service.',
    resolvedAt: getCurrentTimestamp(),
    resolvedBy: 'David Sun'
  },
  {
    id: 1004,
    title: 'Spill in Cafeteria',
    location: 'Cafeteria - Serving Area',
    type: 'safety',
    severity: 'low',
    status: 'resolved',
    description: 'Water spill near serving station. Area cordoned off and cleaned.',
    reportedBy: 'Cafeteria Staff',
    reportedAt: getCurrentTimestamp(),
    assignedTo: 'Housekeeping',
    resolution: 'Spill cleaned, area dried, signs removed.',
    resolvedAt: getCurrentTimestamp(),
    resolvedBy: 'Housekeeping'
  },
  {
    id: 1005,
    title: 'HVAC Overheating Alarm',
    location: 'Mechanical Room - Floor 3',
    type: 'equipment',
    severity: 'medium',
    status: 'open',
    description: 'AHU-05 reported high temperature alarm. Fan motor running hot.',
    reportedBy: 'BMS System',
    reportedAt: getCurrentTimestamp(),
    assignedTo: 'Mike Wang',
    resolution: null,
    resolvedAt: null,
    resolvedBy: null
  }
])

// UI State
const showReportDialog = ref(false)
const showDetailDialog = ref(false)
const searchText = ref('')
const filterStatus = ref('all')
const filterSeverity = ref('all')
const filterType = ref('all')
const selectedIncident = ref<Incident | null>(null)

const incidentForm = ref({
  title: '',
  location: '',
  type: 'safety',
  severity: 'medium',
  description: '',
  assignedTo: ''
})

// Computed
const openCount = computed(() => incidents.value.filter(i => i.status === 'open' || i.status === 'investigating').length)
const resolvedCount = computed(() => incidents.value.filter(i => i.status === 'resolved' || i.status === 'closed').length)
const criticalCount = computed(() => incidents.value.filter(i => i.severity === 'critical').length)

const filteredIncidents = computed(() => {
  let filtered = [...incidents.value]

  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    filtered = filtered.filter(i =>
        i.title.toLowerCase().includes(keyword) ||
        i.location.toLowerCase().includes(keyword) ||
        i.description.toLowerCase().includes(keyword)
    )
  }

  if (filterStatus.value !== 'all') {
    filtered = filtered.filter(i => i.status === filterStatus.value)
  }

  if (filterSeverity.value !== 'all') {
    filtered = filtered.filter(i => i.severity === filterSeverity.value)
  }

  if (filterType.value !== 'all') {
    filtered = filtered.filter(i => i.type === filterType.value)
  }

  return filtered.sort((a, b) => new Date(b.reportedAt).getTime() - new Date(a.reportedAt).getTime())
})

// Methods
const openReportDialog = () => {
  incidentForm.value = {
    title: '',
    location: '',
    type: 'safety',
    severity: 'medium',
    description: '',
    assignedTo: ''
  }
  showReportDialog.value = true
}

const submitIncident = () => {
  if (!incidentForm.value.title.trim()) {
    ElMessage.warning('Please enter a title')
    return
  }
  if (!incidentForm.value.location.trim()) {
    ElMessage.warning('Please enter a location')
    return
  }
  if (!incidentForm.value.description.trim()) {
    ElMessage.warning('Please enter a description')
    return
  }

  const newIncident: Incident = {
    id: Date.now(),
    title: incidentForm.value.title,
    location: incidentForm.value.location,
    type: incidentForm.value.type,
    severity: incidentForm.value.severity,
    status: 'open',
    description: incidentForm.value.description,
    reportedBy: 'Current User',
    reportedAt: getCurrentTimestamp(),
    assignedTo: incidentForm.value.assignedTo || null,
    resolution: null,
    resolvedAt: null,
    resolvedBy: null
  }

  incidents.value.unshift(newIncident)
  ElMessage.success('Incident reported successfully')
  showReportDialog.value = false
}

const viewDetails = (incident: Incident) => {
  selectedIncident.value = incident
  showDetailDialog.value = true
}

const resolveIncident = (incident: Incident) => {
  ElMessageBox.prompt('Enter resolution details', 'Resolve Incident', {
    confirmButtonText: 'Resolve',
    cancelButtonText: 'Cancel',
    inputType: 'textarea',
    inputPlaceholder: 'Describe how the incident was resolved...'
  }).then(({ value }) => {
    incident.status = 'resolved'
    incident.resolution = value || 'Resolved'
    incident.resolvedAt = getCurrentTimestamp()
    incident.resolvedBy = 'Current User'
    ElMessage.success('Incident marked as resolved')
    showDetailDialog.value = false
  }).catch(() => {})
}

const deleteIncident = (incident: Incident) => {
  ElMessageBox.confirm(
      `Delete incident "${incident.title}"? This action cannot be undone.`,
      'Delete Incident',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    const index = incidents.value.findIndex(i => i.id === incident.id)
    if (index !== -1) {
      incidents.value.splice(index, 1)
      ElMessage.success('Incident deleted')
    }
  }).catch(() => {})
}

const refreshData = () => {
  ElMessage.success('Data refreshed')
}

// Loading animation
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
    }, 400)
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

.loading-tip { font-size: 13px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 8px; font-weight: 500; }
.loading-subtip { font-size: 11px; color: #64748b; letter-spacing: 0.5px; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

/* Main Content */
.incident-reporting {
  padding: 24px;
  background: linear-gradient(135deg, #fef9e7 0%, #fdf2e3 100%);
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h2 {
  margin: 0 0 4px 0;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #d84315, #ff6f00);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  margin: 0;
  color: #d84315;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

/* Stats Cards */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 36px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

/* Filter Section */
.filter-section {
  background: white;
  border-radius: 20px;
  padding: 16px 20px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.search-wrapper {
  flex: 1;
  min-width: 250px;
}

.filter-wrapper {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-wrapper .el-select {
  width: 140px;
}

/* Incidents List */
.incidents-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.incident-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  border-left: 4px solid;
}

.incident-card.critical { border-left-color: #f56c6c; }
.incident-card.high { border-left-color: #e6a23c; }
.incident-card.medium { border-left-color: #409eff; }
.incident-card.low { border-left-color: #67c23a; }

.incident-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 12px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.incident-id {
  font-family: monospace;
  font-size: 12px;
  color: #909399;
  background: #f5f5f5;
  padding: 2px 8px;
  border-radius: 4px;
}

.incident-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.header-right {
  display: flex;
  gap: 8px;
}

.severity-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.severity-badge.critical { background: #ffefef; color: #f56c6c; }
.severity-badge.high { background: #fff7e6; color: #e6a23c; }
.severity-badge.medium { background: #e6f7ff; color: #409eff; }
.severity-badge.low { background: #e8f5e9; color: #67c23a; }
.severity-badge.large { padding: 6px 16px; font-size: 14px; }

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.open { background: #ffefef; color: #f56c6c; }
.status-badge.investigating { background: #fff7e6; color: #e6a23c; }
.status-badge.resolved { background: #e8f5e9; color: #67c23a; }
.status-badge.closed { background: #e8e8e8; color: #909399; }
.status-badge.large { padding: 6px 16px; font-size: 14px; }

.card-body {
  margin-bottom: 16px;
}

.incident-details {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 12px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #606266;
}

.detail-icon {
  font-size: 14px;
}

.incident-description {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
  margin-bottom: 8px;
}

.incident-resolution {
  font-size: 13px;
  color: #67c23a;
  padding: 8px 12px;
  background: #e8f5e9;
  border-radius: 8px;
  margin-top: 8px;
}

.resolution-label {
  font-weight: 600;
  margin-right: 8px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.assigned-to {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
}

.footer-right {
  display: flex;
  gap: 8px;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 60px;
  background: white;
  border-radius: 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: #909399;
  margin-bottom: 24px;
}

/* Dialog */
.incident-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.incident-detail {
  padding: 0 0 16px 0;
}

.detail-header {
  margin-bottom: 20px;
}

.detail-badges {
  display: flex;
  gap: 12px;
}

/* Responsive */
@media (max-width: 768px) {
  .incident-reporting { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .filter-section { flex-direction: column; }
  .search-wrapper { width: 100%; }
  .filter-wrapper { width: 100%; justify-content: space-between; }
  .filter-wrapper .el-select { flex: 1; }
  .card-header { flex-direction: column; align-items: flex-start; }
  .card-footer { flex-direction: column; align-items: flex-start; }
}
</style>