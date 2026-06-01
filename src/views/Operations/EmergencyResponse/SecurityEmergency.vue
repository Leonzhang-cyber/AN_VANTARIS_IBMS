<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
  RefreshRight, Warning, CircleCheck, Clock,
  Monitor, Tools, Search, Setting,
  Operation, Document, Grid, List,
  Bell, User, Location, Phone,
  VideoCamera, Lock, DataAnalysis,
  Timer, Check, Close, Edit, Delete,
  Key, View
} from "@element-plus/icons-vue"
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Initializing security emergency system...',
  'Connecting to surveillance network...',
  'Loading access control data...',
  'Ready for emergency response...'
]

// Emergency status
const emergencyStatus = ref({
  isActive: false,
  emergencyType: 'None',
  threatLevel: 'None',
  triggeredAt: '',
  affectedZones: [] as string[],
  lockdownStatus: 'Normal',
  policeNotified: false
})

// Security zones
const securityZones = ref([
  { id: 'zone-1', name: 'Main Entrance', status: 'normal', cameras: 4, accessPoints: 2, lastPatrol: '10 min ago', alerts: [] },
  { id: 'zone-2', name: 'Server Room', status: 'secure', cameras: 2, accessPoints: 1, lastPatrol: '5 min ago', alerts: [] },
  { id: 'zone-3', name: 'Executive Office', status: 'normal', cameras: 1, accessPoints: 1, lastPatrol: '15 min ago', alerts: [] },
  { id: 'zone-4', name: 'Data Center', status: 'secure', cameras: 4, accessPoints: 2, lastPatrol: '2 min ago', alerts: [] },
  { id: 'zone-5', name: 'Loading Dock', status: 'warning', cameras: 2, accessPoints: 1, lastPatrol: '30 min ago', alerts: [{ type: 'Unauthorized Access Attempt', time: '09:15:00' }] },
  { id: 'zone-6', name: 'Parking Garage', status: 'normal', cameras: 8, accessPoints: 2, lastPatrol: '20 min ago', alerts: [] },
  { id: 'zone-7', name: 'Security Control Room', status: 'secure', cameras: 2, accessPoints: 1, lastPatrol: '1 min ago', alerts: [] },
  { id: 'zone-8', name: 'Emergency Exits', status: 'normal', cameras: 6, accessPoints: 4, lastPatrol: '25 min ago', alerts: [] }
])

// Active incidents
const activeIncidents = ref([
  { id: 'INC-001', type: 'Unauthorized Access', zone: 'Loading Dock', severity: 'High', time: '09:15:00', status: 'Investigating', responseTeam: 'Security Patrol' },
  { id: 'INC-002', type: 'Suspicious Activity', zone: 'Parking Garage', severity: 'Medium', time: '08:45:00', status: 'Monitoring', responseTeam: 'CCTV Operator' },
  { id: 'INC-003', type: 'Door Forced Open', zone: 'East Exit', severity: 'Critical', time: '09:30:00', status: 'Responding', responseTeam: 'Rapid Response' }
])

// Security personnel
const securityPersonnel = ref([
  { name: 'John Smith', role: 'Security Supervisor', status: 'On Duty', location: 'Control Room', contact: '555-0101' },
  { name: 'Sarah Johnson', role: 'Patrol Officer', status: 'On Duty', location: 'Patrol Zone A', contact: '555-0102' },
  { name: 'Mike Wilson', role: 'CCTV Operator', status: 'On Duty', location: 'Control Room', contact: '555-0103' },
  { name: 'Lisa Brown', role: 'Rapid Response', status: 'Standby', location: 'Ready Room', contact: '555-0104' },
  { name: 'David Lee', role: 'K9 Unit', status: 'On Patrol', location: 'Parking Area', contact: '555-0105' }
])

// Emergency contacts
const emergencyContacts = ref([
  { name: 'Police Department', number: '911', type: 'Emergency', responseTime: '5-10 min' },
  { name: 'Security Control Room', number: '555-0199', type: 'Internal', responseTime: 'Immediate' },
  { name: 'Facility Security', number: '555-0188', type: 'Internal', responseTime: '2 min' },
  { name: 'Crisis Management', number: '555-0177', type: 'Management', responseTime: '5 min' }
])

// Incident history
const incidentHistory = ref([
  { id: 'HST-001', date: '2025-01-15', time: '14:30:00', zone: 'Main Entrance', type: 'Access Denied', resolution: 'False Alarm', resolvedBy: 'System' },
  { id: 'HST-002', date: '2025-01-14', time: '22:15:00', zone: 'Parking Garage', type: 'Motion Detected', resolution: 'Cleared', resolvedBy: 'Patrol' },
  { id: 'HST-003', date: '2025-01-13', time: '08:45:00', zone: 'Loading Dock', type: 'Door Left Open', resolution: 'Closed', resolvedBy: 'Staff' },
  { id: 'HST-004', date: '2025-01-12', time: '16:20:00', zone: 'Server Room', type: 'Badge Access', resolution: 'Authorized', resolvedBy: 'System' }
])

// System status
const systemStatus = ref({
  camerasOnline: 28,
  camerasTotal: 32,
  accessPointsOnline: 18,
  accessPointsTotal: 20,
  alarmSystem: 'Armed',
  lastSystemTest: '2025-01-15 08:00:00'
})

// UI State
const showIncidents = ref(false)
const showPersonnel = ref(false)
const showHistory = ref(false)
const showCCTV = ref(false)
const searchKeyword = ref('')
const lockdownActive = ref(false)

const filteredZones = computed(() => {
  if (!searchKeyword.value) return securityZones.value
  return securityZones.value.filter(z =>
      z.name.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

const getZoneStatusColor = (status: string) => {
  switch(status) {
    case 'alert': return '#F56C6C'
    case 'warning': return '#E6A23C'
    case 'secure': return '#67C23A'
    case 'normal': return '#409EFF'
    default: return '#909399'
  }
}

const getZoneStatusText = (status: string) => {
  switch(status) {
    case 'alert': return 'ALERT'
    case 'warning': return 'Warning'
    case 'secure': return 'Secured'
    case 'normal': return 'Normal'
    default: return 'Unknown'
  }
}

const getSeverityColor = (severity: string) => {
  switch(severity) {
    case 'Critical': return '#F56C6C'
    case 'High': return '#E6A23C'
    case 'Medium': return '#409EFF'
    case 'Low': return '#67C23A'
    default: return '#909399'
  }
}

// Emergency actions
const activateLockdown = () => {
  ElMessageBox.confirm(
      'ACTIVATE BUILDING LOCKDOWN?\n\nThis will:\n- Lock all exterior doors\n- Restrict access to secure areas\n- Alert all security personnel\n- Trigger lockdown protocols\n\nOnly use in genuine security threat!',
      'Lockdown Activation',
      {
        confirmButtonText: 'ACTIVATE LOCKDOWN',
        cancelButtonText: 'Cancel',
        type: 'error'
      }
  ).then(() => {
    lockdownActive.value = true
    emergencyStatus.value.isActive = true
    emergencyStatus.value.emergencyType = 'Lockdown'
    emergencyStatus.value.threatLevel = 'High'
    emergencyStatus.value.triggeredAt = new Date().toLocaleString()
    emergencyStatus.value.lockdownStatus = 'Active'

    // Update zone status
    securityZones.value.forEach(zone => {
      if (zone.status === 'normal') zone.status = 'secure'
    })

    ElMessage.error('BUILDING LOCKDOWN ACTIVATED - All exterior doors secured')
  }).catch(() => {})
}

const deactivateLockdown = () => {
  ElMessageBox.confirm(
      'Deactivate building lockdown?\n\nConfirm that the security threat has been resolved.',
      'Deactivate Lockdown',
      {
        confirmButtonText: 'Deactivate',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    lockdownActive.value = false
    emergencyStatus.value.isActive = false
    emergencyStatus.value.lockdownStatus = 'Normal'
    ElMessage.success('Lockdown deactivated - Building恢复正常 operation')
  }).catch(() => {})
}

const callPolice = () => {
  ElMessageBox.confirm(
      'Call Police Department (911)?\n\nThis will dispatch law enforcement to your location.',
      'Emergency Call',
      {
        confirmButtonText: 'Call Now',
        cancelButtonText: 'Cancel',
        type: 'error'
      }
  ).then(() => {
    emergencyStatus.value.policeNotified = true
    ElMessage.success('Police dispatched - ETA 5-10 minutes')
  }).catch(() => {})
}

const dispatchResponse = (incident: any) => {
  ElMessageBox.confirm(
      `Dispatch response team to ${incident.zone} for ${incident.type}?`,
      'Dispatch Team',
      {
        confirmButtonText: 'Dispatch',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    incident.status = 'Responding'
    ElMessage.success(`Response team dispatched to ${incident.zone}`)
  }).catch(() => {})
}

const resolveIncident = (incident: any) => {
  ElMessageBox.confirm(
      `Mark incident ${incident.id} as resolved?`,
      'Resolve Incident',
      {
        confirmButtonText: 'Resolve',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    incident.status = 'Resolved'
    ElMessage.success(`Incident ${incident.id} marked as resolved`)
  }).catch(() => {})
}

const viewCameraFeed = (zone: any) => {
  ElMessage.info(`Loading camera feed for ${zone.name}...`)
  showCCTV.value = true
}

const refreshData = () => {
  ElMessage.info('Refreshing security data...')
  setTimeout(() => {
    ElMessage.success('Data refreshed successfully')
  }, 1000)
}

onMounted(() => {
  let progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)

  setTimeout(() => {
    clearInterval(progressInterval)
    loadingProgress.value = 100
    setTimeout(() => { isLoaded.value = true }, 400)
  }, 2000)
})
</script>

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
          <span class="loading-dots"><span>.</span><span>.</span><span>.</span></span>
        </div>
        <div class="loading-progress"><div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div></div>
        <div class="loading-tip">Security Emergency Response</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="security-emergency">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Security Emergency Response</h2>
        <p class="subtitle">Real-time threat monitoring, access control and emergency response coordination</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="showPersonnel = true">
          <el-icon><User /></el-icon> Personnel
        </el-button>
        <el-button @click="showHistory = true">
          <el-icon><Document /></el-icon> History
        </el-button>
        <el-button type="primary" @click="refreshData">
          <el-icon><RefreshRight /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- System Status Banner -->
    <div class="status-banner">
      <div class="status-item">
        <span class="status-label">Cameras:</span>
        <span class="status-value">{{ systemStatus.camerasOnline }}/{{ systemStatus.camerasTotal }} Online</span>
      </div>
      <div class="status-item">
        <span class="status-label">Access Points:</span>
        <span class="status-value">{{ systemStatus.accessPointsOnline }}/{{ systemStatus.accessPointsTotal }} Active</span>
      </div>
      <div class="status-item">
        <span class="status-label">Alarm System:</span>
        <span class="status-value" :style="{ color: systemStatus.alarmSystem === 'Armed' ? '#67C23A' : '#909399' }">
          {{ systemStatus.alarmSystem }}
        </span>
      </div>
      <div class="status-item">
        <span class="status-label">Last Test:</span>
        <span class="status-value">{{ systemStatus.lastSystemTest }}</span>
      </div>
    </div>

    <!-- Active Lockdown Banner -->
    <div v-if="lockdownActive" class="lockdown-banner">
      <div class="lockdown-icon">🔒</div>
      <div class="lockdown-info">
        <div class="lockdown-title">BUILDING LOCKDOWN ACTIVE</div>
        <div class="lockdown-desc">All exterior doors secured • Access restricted • Security on high alert</div>
      </div>
      <div class="lockdown-actions">
        <el-button type="danger" size="large" @click="deactivateLockdown">DEACTIVATE LOCKDOWN</el-button>
      </div>
    </div>

    <!-- Quick Action Buttons -->
    <div class="quick-actions">
      <div class="section-header">
        <span>Emergency Response Actions</span>
        <el-tag type="danger" size="small">Immediate</el-tag>
      </div>
      <div class="action-buttons">
        <el-button type="danger" plain size="large" @click="activateLockdown">
          <el-icon><Lock /></el-icon> Building Lockdown
        </el-button>
        <el-button type="warning" plain size="large" @click="callPolice">
          <el-icon><Phone /></el-icon> Call Police (911)
        </el-button>
      </div>
    </div>

    <!-- Active Incidents -->
    <div class="incidents-section">
      <div class="section-header">
        <span><el-icon><Warning /></el-icon> Active Incidents</span>
        <el-tag type="danger" size="small">{{ activeIncidents.length }} Active</el-tag>
      </div>
      <div class="incidents-grid">
        <div v-for="incident in activeIncidents" :key="incident.id" class="incident-card">
          <div class="incident-header">
            <div class="incident-id">{{ incident.id }}</div>
            <div class="incident-severity" :style="{ color: getSeverityColor(incident.severity) }">
              {{ incident.severity }}
            </div>
          </div>
          <div class="incident-type">{{ incident.type }}</div>
          <div class="incident-location">📍 {{ incident.zone }}</div>
          <div class="incident-time">🕐 {{ incident.time }}</div>
          <div class="incident-status">Status: {{ incident.status }}</div>
          <div class="incident-team">Team: {{ incident.responseTeam }}</div>
          <div class="incident-actions">
            <el-button size="small" type="primary" @click="dispatchResponse(incident)">Dispatch</el-button>
            <el-button size="small" type="success" @click="resolveIncident(incident)">Resolve</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Security Zones -->
    <div class="zones-section">
      <div class="section-header">
        <span>Security Zones</span>
        <el-input v-model="searchKeyword" placeholder="Search zones..." clearable style="width: 200px" :prefix-icon="Search" />
      </div>
      <div class="zones-grid">
        <div v-for="zone in filteredZones" :key="zone.id" class="zone-card" :class="zone.status">
          <div class="zone-header">
            <div class="zone-name">{{ zone.name }}</div>
            <div class="zone-status" :style="{ color: getZoneStatusColor(zone.status) }">
              {{ getZoneStatusText(zone.status) }}
            </div>
          </div>
          <div class="zone-stats">
            <div class="zone-stat">📹 {{ zone.cameras }} cameras</div>
            <div class="zone-stat">🔑 {{ zone.accessPoints }} access points</div>
            <div class="zone-stat">🕐 Last patrol: {{ zone.lastPatrol }}</div>
          </div>
          <div class="zone-alerts" v-if="zone.alerts.length > 0">
            <div v-for="alert in zone.alerts" :key="alert.time" class="alert-item-small">
              <el-icon><Warning /></el-icon> {{ alert.type }} at {{ alert.time }}
            </div>
          </div>
          <div class="zone-actions">
            <el-button size="small" type="primary" plain @click="viewCameraFeed(zone)">
              <el-icon><VideoCamera /></el-icon> View Cameras
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Emergency Contacts -->
    <el-card class="contacts-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span><el-icon><Phone /></el-icon> Emergency Contacts</span>
          <el-tag type="danger" size="small">24/7 Available</el-tag>
        </div>
      </template>
      <div class="contacts-grid">
        <div v-for="contact in emergencyContacts" :key="contact.name" class="contact-card">
          <div class="contact-name">{{ contact.name }}</div>
          <div class="contact-number"><el-icon><Phone /></el-icon> {{ contact.number }}</div>
          <div class="contact-type">{{ contact.type }} • Response: {{ contact.responseTime }}</div>
        </div>
      </div>
    </el-card>

    <!-- Personnel Dialog -->
    <el-dialog v-model="showPersonnel" title="Security Personnel" width="700px">
      <el-table :data="securityPersonnel" stripe>
        <el-table-column prop="name" label="Name" min-width="130" />
        <el-table-column prop="role" label="Role" min-width="130" />
        <el-table-column label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'On Duty' ? 'success' : 'info'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="Location" min-width="120" />
        <el-table-column prop="contact" label="Contact" width="100" />
      </el-table>
      <template #footer>
        <el-button @click="showPersonnel = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Incident History Dialog -->
    <el-dialog v-model="showHistory" title="Incident History" width="800px">
      <el-table :data="incidentHistory" stripe>
        <el-table-column prop="date" label="Date" width="100" />
        <el-table-column prop="time" label="Time" width="80" />
        <el-table-column prop="zone" label="Zone" min-width="130" />
        <el-table-column prop="type" label="Type" min-width="120" />
        <el-table-column prop="resolution" label="Resolution" min-width="120" />
        <el-table-column prop="resolvedBy" label="Resolved By" width="100" />
      </el-table>
      <template #footer>
        <el-button @click="showHistory = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- CCTV Feed Dialog -->
    <el-dialog v-model="showCCTV" title="Camera Feed" width="800px">
      <div class="cctv-grid">
        <div class="cctv-feed">
          <div class="feed-placeholder">
            <el-icon><VideoCamera /></el-icon>
            <span>Camera Feed Loading...</span>
          </div>
        </div>
        <div class="cctv-controls">
          <el-button type="primary" size="small">Live View</el-button>
          <el-button size="small">Playback</el-button>
          <el-button size="small">Snapshot</el-button>
          <el-button size="small">PTZ Control</el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="showCCTV = false">Close</el-button>
      </template>
    </el-dialog>
  </div>
</template>

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

.loading-tip { font-size: 13px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 8px; font-weight: 500; }
.loading-subtip { font-size: 11px; color: #64748b; letter-spacing: 0.5px; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

/* Main Content */
.security-emergency {
  padding: 24px;
  background: linear-gradient(135deg, #f0f5ff 0%, #e0e8f5 100%);
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
  background: linear-gradient(135deg, #1a237e, #283593);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  margin: 0;
  color: #1a237e;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

/* Status Banner */
.status-banner {
  background: white;
  border-radius: 16px;
  padding: 16px 20px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  gap: 20px;
}

.status-item {
  display: flex;
  gap: 8px;
  font-size: 14px;
}

.status-label { color: #909399; }
.status-value { font-weight: 600; color: #303133; }

/* Lockdown Banner */
.lockdown-banner {
  background: linear-gradient(135deg, #1a237e, #283593);
  border-radius: 20px;
  padding: 20px 24px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  color: white;
  flex-wrap: wrap;
  animation: pulse-blue 1s infinite;
}

@keyframes pulse-blue {
  0%, 100% { box-shadow: 0 0 0 0 rgba(26, 35, 126, 0.4); }
  50% { box-shadow: 0 0 0 20px rgba(26, 35, 126, 0); }
}

.lockdown-icon { font-size: 48px; }
.lockdown-info { flex: 1; }
.lockdown-title { font-weight: 700; font-size: 24px; margin-bottom: 4px; }
.lockdown-desc { font-size: 14px; opacity: 0.9; }

/* Quick Actions */
.quick-actions {
  background: white;
  border-radius: 20px;
  padding: 16px 20px;
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 600;
  font-size: 15px;
}

.action-buttons {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.action-buttons .el-button {
  flex: 1;
  min-width: 200px;
}

/* Incidents Section */
.incidents-section {
  background: white;
  border-radius: 20px;
  padding: 16px 20px;
  margin-bottom: 24px;
}

.incidents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.incident-card {
  background: #fff5f5;
  border-radius: 16px;
  padding: 16px;
  border-left: 4px solid #F56C6C;
}

.incident-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.incident-id { font-weight: 600; font-family: monospace; }
.incident-severity { font-weight: 600; font-size: 12px; }
.incident-type { font-weight: 600; font-size: 16px; margin-bottom: 8px; }
.incident-location, .incident-time, .incident-status, .incident-team {
  font-size: 12px;
  color: #606266;
  margin-bottom: 4px;
}
.incident-actions { margin-top: 12px; display: flex; gap: 8px; justify-content: flex-end; }

/* Zones Section */
.zones-section {
  background: white;
  border-radius: 20px;
  padding: 16px 20px;
  margin-bottom: 24px;
}

.zones-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.zone-card {
  background: #f8f9fa;
  border-radius: 16px;
  padding: 16px;
  transition: all 0.2s ease;
  border-left: 4px solid #409EFF;
}

.zone-card.alert { border-left-color: #F56C6C; background: #fff0f0; }
.zone-card.warning { border-left-color: #E6A23C; }
.zone-card.secure { border-left-color: #67C23A; }

.zone-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.zone-name { font-weight: 600; font-size: 16px; }
.zone-status { font-weight: 600; font-size: 13px; }

.zone-stats {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.zone-alerts {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #ebeef5;
}

.alert-item-small {
  font-size: 12px;
  color: #F56C6C;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 4px;
}

.zone-actions {
  margin-top: 12px;
  text-align: right;
}

/* Contacts Card */
.contacts-card {
  border-radius: 20px;
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.contacts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}

.contact-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 12px;
}

.contact-name { font-weight: 600; margin-bottom: 4px; }
.contact-number { font-size: 13px; color: #409EFF; margin-bottom: 4px; display: flex; align-items: center; gap: 4px; }
.contact-type { font-size: 11px; color: #909399; }

/* CCTV Dialog */
.cctv-grid {
  text-align: center;
}

.cctv-feed {
  background: #1a1a2e;
  border-radius: 12px;
  padding: 60px;
  margin-bottom: 16px;
}

.feed-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #666;
}

.feed-placeholder .el-icon { font-size: 48px; }

.cctv-controls {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

/* Responsive */
@media (max-width: 768px) {
  .security-emergency { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .action-buttons { flex-direction: column; }
  .action-buttons .el-button { width: 100%; }
  .zones-grid { grid-template-columns: 1fr; }
  .incidents-grid { grid-template-columns: 1fr; }
  .status-banner { flex-direction: column; }
}
</style>