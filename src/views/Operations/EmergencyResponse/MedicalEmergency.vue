<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
  RefreshRight, Warning, CircleCheck, Clock,
  Monitor, Tools, Search, Setting,
  Operation, Document, Grid, List,
  Bell, User, Location, Phone,
  VideoCamera, Lock, DataAnalysis,
  Timer, Check, Close, Edit, Delete, Star
} from "@element-plus/icons-vue"
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Initializing medical emergency system...',
  'Connecting to first aid stations...',
  'Loading response teams...',
  'Ready for emergency response...'
]

// Emergency status
const emergencyStatus = ref({
  isActive: false,
  emergencyType: 'None',
  severity: 'None',
  triggeredAt: '',
  location: '',
  patientCondition: '',
  responseDispatched: false
})

// Medical response teams
const responseTeams = ref([
  { id: 'team-1', name: 'First Responders', status: 'Available', members: 4, equipment: 'AED, First Aid Kit', responseTime: '2 min', location: 'Security Office' },
  { id: 'team-2', name: 'Medical Response Team', status: 'Available', members: 6, equipment: 'Advanced Life Support', responseTime: '5 min', location: 'Clinic' },
  { id: 'team-3', name: 'Emergency Medical Services', status: 'Standby', members: 'On Call', equipment: 'Ambulance', responseTime: '8-12 min', location: 'External' },
  { id: 'team-4', name: 'Mental Health Support', status: 'Available', members: 2, equipment: 'Counseling Kit', responseTime: '10 min', location: 'HR Office' }
])

// First aid stations
const firstAidStations = ref([
  { id: 'fas-1', name: 'Main Lobby', location: 'Ground Floor - North', equipment: ['AED', 'First Aid Kit', 'Stretcher'], status: 'Fully Stocked', lastChecked: '2025-01-15' },
  { id: 'fas-2', name: 'Security Office', location: 'Ground Floor - Security', equipment: ['AED', 'First Aid Kit', 'Oxygen'], status: 'Fully Stocked', lastChecked: '2025-01-14' },
  { id: 'fas-3', name: 'Server Room', location: '2nd Floor - IT Area', equipment: ['First Aid Kit'], status: 'Low Stock', lastChecked: '2025-01-10' },
  { id: 'fas-4', name: 'Cafeteria', location: '1st Floor - Dining', equipment: ['AED', 'First Aid Kit'], status: 'Fully Stocked', lastChecked: '2025-01-13' },
  { id: 'fas-5', name: 'Conference Center', location: '1st Floor - Meeting Area', equipment: ['First Aid Kit'], status: 'Fully Stocked', lastChecked: '2025-01-12' }
])

// Active medical incidents
const activeIncidents = ref([
  { id: 'MED-001', type: 'Cardiac Emergency', location: 'Conference Room B', severity: 'Critical', time: '09:15:00', status: 'Responding', patientStatus: 'Unconscious', team: 'First Responders' },
  { id: 'MED-002', type: 'Injury/Fall', location: 'Stairwell A', severity: 'High', time: '09:30:00', status: 'Investigating', patientStatus: 'Conscious', team: 'Medical Response Team' },
  { id: 'MED-003', type: 'Respiratory Distress', location: 'Office 302', severity: 'High', time: '09:45:00', status: 'Monitoring', patientStatus: 'Stable', team: 'First Responders' }
])

// Emergency contacts
const emergencyContacts = ref([
  { name: 'Emergency Medical Services', number: '911', type: 'External', responseTime: '8-12 min' },
  { name: 'Medical Response Team', number: '555-0199', type: 'Internal', responseTime: '2-5 min' },
  { name: 'First Responders', number: '555-0188', type: 'Internal', responseTime: '1-2 min' },
  { name: 'On-site Clinic', number: '555-0177', type: 'Internal', responseTime: '3-5 min' }
])

// Incident history
const incidentHistory = ref([
  { id: 'HST-001', date: '2025-01-15', time: '14:30:00', location: 'Cafeteria', type: 'Minor Injury', resolution: 'First Aid Provided', resolvedBy: 'First Responder' },
  { id: 'HST-002', date: '2025-01-14', time: '22:15:00', location: 'Parking Lot', type: 'Medical Emergency', resolution: 'Ambulance Transported', resolvedBy: 'EMS' },
  { id: 'HST-003', date: '2025-01-13', time: '08:45:00', location: 'Office 205', type: 'Allergic Reaction', resolution: 'Treated On-site', resolvedBy: 'Medical Team' },
  { id: 'HST-004', date: '2025-01-12', time: '16:20:00', location: 'Gym', type: 'Sports Injury', resolution: 'First Aid Applied', resolvedBy: 'First Responder' }
])

// Medical equipment inventory
const medicalEquipment = ref([
  { name: 'AED Units', total: 5, available: 4, location: 'Various Locations', lastInspected: '2025-01-01' },
  { name: 'First Aid Kits', total: 12, available: 10, location: 'Throughout Building', lastInspected: '2025-01-01' },
  { name: 'Oxygen Tanks', total: 3, available: 2, location: 'Clinic', lastInspected: '2025-01-01' },
  { name: 'Stretchers', total: 4, available: 3, location: 'First Aid Stations', lastInspected: '2025-01-01' }
])

// First aid procedures
const firstAidProcedures = ref([
  { id: 'proc-1', name: 'CPR', steps: '1. Check responsiveness → 2. Call for help → 3. Begin chest compressions → 4. Use AED if available', video: true },
  { id: 'proc-2', name: 'Choking', steps: '1. Encourage coughing → 2. Back blows → 3. Abdominal thrusts → 4. Call EMS if not resolved', video: true },
  { id: 'proc-3', name: 'Bleeding Control', steps: '1. Apply direct pressure → 2. Elevate if possible → 3. Apply pressure bandage → 4. Monitor for shock', video: true },
  { id: 'proc-4', name: 'Shock Management', steps: '1. Lay person down → 2. Elevate feet → 3. Keep warm → 4. Monitor breathing', video: true }
])

// UI State
const showStations = ref(false)
const showEquipment = ref(false)
const showHistory = ref(false)
const showProcedures = ref(false)
const searchKeyword = ref('')

const filteredStations = computed(() => {
  if (!searchKeyword.value) return firstAidStations.value
  return firstAidStations.value.filter(s =>
      s.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      s.location.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

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
const dispatchMedicalTeam = (incident: any) => {
  ElMessageBox.confirm(
      `Dispatch medical team to ${incident.location} for ${incident.type}?`,
      'Dispatch Team',
      {
        confirmButtonText: 'Dispatch',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    incident.status = 'Responding'
    emergencyStatus.value.responseDispatched = true
    ElMessage.success(`Medical team dispatched to ${incident.location}`)
  }).catch(() => {})
}

const callEMS = () => {
  ElMessageBox.confirm(
      'Call Emergency Medical Services (911)?\n\nAmbulance will be dispatched to your location.',
      'Emergency Call',
      {
        confirmButtonText: 'Call 911',
        cancelButtonText: 'Cancel',
        type: 'error'
      }
  ).then(() => {
    ElMessage.success('EMS dispatched - Estimated arrival: 8-12 minutes')
  }).catch(() => {})
}

const activateEmergency = () => {
  ElMessageBox.prompt('Enter patient location and condition', 'Medical Emergency', {
    confirmButtonText: 'Activate',
    cancelButtonText: 'Cancel',
    inputPlaceholder: 'e.g., Conference Room B - Person collapsed',
    inputValidator: (value) => {
      if (!value) return 'Location and condition required'
      return true
    }
  }).then(({ value }) => {
    emergencyStatus.value.isActive = true
    emergencyStatus.value.emergencyType = 'Medical'
    emergencyStatus.value.severity = 'High'
    emergencyStatus.value.triggeredAt = new Date().toLocaleString()
    emergencyStatus.value.location = value || 'Unknown location'
    emergencyStatus.value.patientCondition = 'Awaiting assessment'

    ElMessage.error(`MEDICAL EMERGENCY ACTIVATED at ${value}`)

    // Auto-dispatch first responders
    setTimeout(() => {
      ElMessage.warning('First responders dispatched to location')
      emergencyStatus.value.responseDispatched = true
    }, 2000)
  }).catch(() => {})
}

const deactivateEmergency = () => {
  ElMessageBox.confirm(
      'Deactivate medical emergency?\n\nConfirm that the patient has been treated and is stable.',
      'Deactivate Emergency',
      {
        confirmButtonText: 'Deactivate',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    emergencyStatus.value.isActive = false
    emergencyStatus.value.emergencyType = 'None'
    ElMessage.success('Medical emergency deactivated')
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

const refreshData = () => {
  ElMessage.info('Refreshing medical emergency data...')
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
        <div class="loading-tip">Medical Emergency Response</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="medical-emergency">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Medical Emergency Response</h2>
        <p class="subtitle">Emergency medical response coordination and first aid management</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="showStations = true">
          <el-icon><Location /></el-icon> First Aid Stations
        </el-button>
        <el-button @click="showEquipment = true">
          <el-icon><Tools /></el-icon> Equipment
        </el-button>
        <el-button @click="showProcedures = true">
          <el-icon><Document /></el-icon> Procedures
        </el-button>
        <el-button @click="showHistory = true">
          <el-icon><Document /></el-icon> History
        </el-button>
        <el-button type="primary" @click="refreshData">
          <el-icon><RefreshRight /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- Active Emergency Banner -->
    <div v-if="emergencyStatus.isActive" class="emergency-banner">
      <div class="emergency-icon">🚑</div>
      <div class="emergency-info">
        <div class="emergency-title">MEDICAL EMERGENCY ACTIVE</div>
        <div class="emergency-location">📍 {{ emergencyStatus.location }}</div>
        <div class="emergency-time">🕐 Activated: {{ emergencyStatus.triggeredAt }}</div>
      </div>
      <div class="emergency-actions">
        <el-button type="danger" size="large" @click="deactivateEmergency">CLEAR EMERGENCY</el-button>
      </div>
    </div>

    <!-- Quick Action Buttons -->
    <div class="quick-actions">
      <div class="section-header">
        <span>Emergency Response Actions</span>
        <el-tag type="danger" size="small">Immediate</el-tag>
      </div>
      <div class="action-buttons">
        <el-button type="danger" plain size="large" @click="activateEmergency">
          <el-icon><Bell /></el-icon> Report Emergency
        </el-button>
        <el-button type="warning" plain size="large" @click="callEMS">
          <el-icon><Phone /></el-icon> Call EMS (911)
        </el-button>
      </div>
    </div>

    <!-- Active Medical Incidents -->
    <div class="incidents-section">
      <div class="section-header">
        <span><el-icon><Warning /></el-icon> Active Medical Incidents</span>
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
          <div class="incident-location">📍 {{ incident.location }}</div>
          <div class="incident-time">🕐 {{ incident.time }}</div>
          <div class="incident-status">Status: {{ incident.status }}</div>
          <div class="incident-patient">Patient: {{ incident.patientStatus }}</div>
          <div class="incident-team">Team: {{ incident.team }}</div>
          <div class="incident-actions">
            <el-button size="small" type="primary" @click="dispatchMedicalTeam(incident)">Dispatch</el-button>
            <el-button size="small" type="success" @click="resolveIncident(incident)">Resolve</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Response Teams Status -->
    <div class="teams-section">
      <div class="section-header">
        <span><el-icon><User /></el-icon> Response Teams</span>
        <el-tag type="info" size="small">Available</el-tag>
      </div>
      <div class="teams-grid">
        <div v-for="team in responseTeams" :key="team.id" class="team-card">
          <div class="team-name">{{ team.name }}</div>
          <div class="team-status" :class="team.status === 'Available' ? 'available' : 'standby'">
            {{ team.status }}
          </div>
          <div class="team-members">👥 {{ team.members }} members</div>
          <div class="team-equipment">🩺 {{ team.equipment }}</div>
          <div class="team-response">⏱ Response: {{ team.responseTime }}</div>
          <div class="team-location">📍 {{ team.location }}</div>
        </div>
      </div>
    </div>

    <!-- Emergency Contacts -->
    <el-card class="contacts-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span><el-icon><Phone /></el-icon> Emergency Medical Contacts</span>
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

    <!-- First Aid Stations Dialog -->
    <el-dialog v-model="showStations" title="First Aid Stations" width="800px">
      <el-input v-model="searchKeyword" placeholder="Search stations..." clearable style="width: 250px; margin-bottom: 16px" :prefix-icon="Search" />
      <el-table :data="filteredStations" stripe>
        <el-table-column prop="name" label="Station" min-width="130" />
        <el-table-column prop="location" label="Location" min-width="180" />
        <el-table-column label="Equipment" min-width="200">
          <template #default="{ row }">
            <div class="equipment-tags">
              <el-tag v-for="item in row.equipment" :key="item" size="small" type="info" effect="plain">{{ item }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Fully Stocked' ? 'success' : 'warning'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastChecked" label="Last Checked" width="110" />
      </el-table>
      <template #footer>
        <el-button @click="showStations = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Equipment Inventory Dialog -->
    <el-dialog v-model="showEquipment" title="Medical Equipment Inventory" width="700px">
      <el-table :data="medicalEquipment" stripe>
        <el-table-column prop="name" label="Equipment" min-width="130" />
        <el-table-column prop="available" label="Available" width="100" align="center" />
        <el-table-column prop="total" label="Total" width="80" align="center" />
        <el-table-column prop="location" label="Location" min-width="160" />
        <el-table-column prop="lastInspected" label="Last Inspected" width="110" />
      </el-table>
      <template #footer>
        <el-button @click="showEquipment = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- First Aid Procedures Dialog -->
    <el-dialog v-model="showProcedures" title="First Aid Procedures" width="800px">
      <div class="procedures-grid">
        <div v-for="proc in firstAidProcedures" :key="proc.id" class="procedure-card">
          <div class="procedure-name">{{ proc.name }}</div>
          <div class="procedure-steps">{{ proc.steps }}</div>
          <div class="procedure-video" v-if="proc.video">
            <el-button size="small" type="primary" plain>▶ Watch Video Guide</el-button>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showProcedures = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Incident History Dialog -->
    <el-dialog v-model="showHistory" title="Incident History" width="800px">
      <el-table :data="incidentHistory" stripe>
        <el-table-column prop="date" label="Date" width="100" />
        <el-table-column prop="time" label="Time" width="80" />
        <el-table-column prop="location" label="Location" min-width="130" />
        <el-table-column prop="type" label="Type" min-width="120" />
        <el-table-column prop="resolution" label="Resolution" min-width="140" />
        <el-table-column prop="resolvedBy" label="Resolved By" width="120" />
      </el-table>
      <template #footer>
        <el-button @click="showHistory = false">Close</el-button>
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
.medical-emergency {
  padding: 24px;
  background: linear-gradient(135deg, #f0f5ff 0%, #e8f0fe 100%);
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
  background: linear-gradient(135deg, #0d47a1, #1976d2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  margin: 0;
  color: #0d47a1;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

/* Emergency Banner */
.emergency-banner {
  background: linear-gradient(135deg, #c62828, #ef5350);
  border-radius: 20px;
  padding: 20px 24px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  color: white;
  flex-wrap: wrap;
  animation: pulse-red 1s infinite;
}

@keyframes pulse-red {
  0%, 100% { box-shadow: 0 0 0 0 rgba(198, 40, 40, 0.4); }
  50% { box-shadow: 0 0 0 20px rgba(198, 40, 40, 0); }
}

.emergency-icon { font-size: 48px; }
.emergency-info { flex: 1; }
.emergency-title { font-weight: 700; font-size: 24px; margin-bottom: 4px; }
.emergency-location, .emergency-time { font-size: 13px; opacity: 0.9; }

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
.incident-location, .incident-time, .incident-status, .incident-patient, .incident-team {
  font-size: 12px;
  color: #606266;
  margin-bottom: 4px;
}
.incident-actions { margin-top: 12px; display: flex; gap: 8px; justify-content: flex-end; }

/* Teams Section */
.teams-section {
  background: white;
  border-radius: 20px;
  padding: 16px 20px;
  margin-bottom: 24px;
}

.teams-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.team-card {
  background: #f8f9fa;
  border-radius: 16px;
  padding: 16px;
  transition: all 0.2s ease;
}

.team-name { font-weight: 600; font-size: 16px; margin-bottom: 8px; }
.team-status { font-size: 12px; font-weight: 600; padding: 2px 8px; border-radius: 20px; display: inline-block; margin-bottom: 8px; }
.team-status.available { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
.team-status.standby { background: rgba(230, 162, 60, 0.1); color: #E6A23C; }
.team-members, .team-equipment, .team-response, .team-location {
  font-size: 12px;
  color: #606266;
  margin-bottom: 4px;
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
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
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

/* Equipment Tags */
.equipment-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

/* Procedures Grid */
.procedures-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 16px;
}

.procedure-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 16px;
}

.procedure-name { font-weight: 600; font-size: 16px; margin-bottom: 8px; color: #1976d2; }
.procedure-steps { font-size: 12px; color: #606266; line-height: 1.5; margin-bottom: 12px; }

/* Responsive */
@media (max-width: 768px) {
  .medical-emergency { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .action-buttons { flex-direction: column; }
  .action-buttons .el-button { width: 100%; }
  .incidents-grid { grid-template-columns: 1fr; }
  .teams-grid { grid-template-columns: 1fr; }
}
</style>