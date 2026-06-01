<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
  RefreshRight, Warning, CircleCheck, Clock,
  Monitor, Tools, Search, Setting,
  Operation, Document, Grid, List,
  Bell, User, Location, Phone,
  VideoCamera, Connection, DataAnalysis,
  Timer, Check, Close, Edit, Delete
} from "@element-plus/icons-vue"
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Initializing fire emergency system...',
  'Connecting to fire alarm panel...',
  'Loading evacuation plans...',
  'Ready for emergency response...'
]

// Emergency status
const emergencyStatus = ref({
  isActive: false,
  alarmType: 'None',
  alarmLevel: 'None',
  triggeredAt: '',
  affectedZones: [] as string[],
  evacuationStatus: 'Normal',
  estimatedResponseTime: 'N/A'
})

// Fire alarm zones
const fireZones = ref([
  { id: 'zone-1', name: 'Ground Floor - Lobby', status: 'normal', smokeDetectors: 8, lastTest: '2025-01-15', alerts: [] },
  { id: 'zone-2', name: 'Ground Floor - East Wing', status: 'normal', smokeDetectors: 12, lastTest: '2025-01-15', alerts: [] },
  { id: 'zone-3', name: 'Ground Floor - West Wing', status: 'alarm', smokeDetectors: 10, lastTest: '2025-01-14', alerts: [{ type: 'Smoke Detector', location: 'West Corridor', time: '09:15:00' }] },
  { id: 'zone-4', name: 'First Floor - Office Area', status: 'normal', smokeDetectors: 15, lastTest: '2025-01-13', alerts: [] },
  { id: 'zone-5', name: 'First Floor - Conference Center', status: 'normal', smokeDetectors: 8, lastTest: '2025-01-12', alerts: [] },
  { id: 'zone-6', name: 'Second Floor - Server Room', status: 'normal', smokeDetectors: 4, lastTest: '2025-01-11', alerts: [] },
  { id: 'zone-7', name: 'Basement - Parking', status: 'normal', smokeDetectors: 16, lastTest: '2025-01-10', alerts: [] },
  { id: 'zone-8', name: 'Kitchen Area', status: 'normal', smokeDetectors: 6, lastTest: '2025-01-09', alerts: [] }
])

// Fire fighting equipment
const fireEquipment = ref([
  { id: 'FE-001', name: 'Fire Extinguisher - ABC', location: 'Lobby North', status: 'ready', lastInspection: '2025-01-01', type: 'ABC' },
  { id: 'FE-002', name: 'Fire Extinguisher - ABC', location: 'Lobby South', status: 'ready', lastInspection: '2025-01-01', type: 'ABC' },
  { id: 'FE-003', name: 'Fire Extinguisher - CO2', location: 'Server Room', status: 'ready', lastInspection: '2025-01-01', type: 'CO2' },
  { id: 'FE-004', name: 'Fire Hose Cabinet', location: 'East Corridor', status: 'ready', lastInspection: '2025-01-01', type: 'Hose' },
  { id: 'FE-005', name: 'Fire Hose Cabinet', location: 'West Corridor', status: 'ready', lastInspection: '2025-01-01', type: 'Hose' },
  { id: 'FE-006', name: 'Fire Blanket', location: 'Kitchen', status: 'ready', lastInspection: '2025-01-01', type: 'Blanket' }
])

// Evacuation routes
const evacuationRoutes = ref([
  { id: 'route-1', name: 'Main Exit', from: 'Lobby', to: 'North Parking Lot', capacity: 200, status: 'clear' },
  { id: 'route-2', name: 'East Exit', from: 'East Corridor', to: 'East Street', capacity: 150, status: 'clear' },
  { id: 'route-3', name: 'West Exit', from: 'West Corridor', to: 'West Street', capacity: 150, status: 'clear' },
  { id: 'route-4', name: 'Stairwell A', from: '1st Floor', to: 'Ground Level', capacity: 100, status: 'clear' },
  { id: 'route-5', name: 'Stairwell B', from: '2nd Floor', to: 'Ground Level', capacity: 100, status: 'clear' }
])

// Emergency contacts
const emergencyContacts = ref([
  { name: 'Fire Department', number: '911', type: 'Emergency', responseTime: '5-10 min' },
  { name: 'Security Control', number: '555-0199', type: 'Internal', responseTime: '2 min' },
  { name: 'Facility Manager', number: '555-0188', type: 'Internal', responseTime: '5 min' },
  { name: 'Medical Response', number: '555-0177', type: 'Internal', responseTime: '3 min' }
])

// Alarm history
const alarmHistory = ref([
  { id: 'ALM-001', time: '14:30:00', date: '2025-01-15', zone: 'West Corridor', type: 'Smoke Detector', status: 'Cleared', responseTime: '45s' },
  { id: 'ALM-002', time: '09:15:00', date: '2025-01-14', zone: 'Kitchen', type: 'Heat Detector', status: 'False Alarm', responseTime: '30s' },
  { id: 'ALM-003', time: '22:00:00', date: '2025-01-12', zone: 'Server Room', type: 'Smoke Detector', status: 'Cleared', responseTime: '60s' },
  { id: 'ALM-004', time: '11:30:00', date: '2025-01-10', zone: 'Lobby', type: 'Pull Station', status: 'Drill', responseTime: '90s' }
])

// System tests
const systemTests = ref([
  { id: 'TST-001', date: '2025-01-15', type: 'Monthly Test', result: 'Pass', conductedBy: 'Safety Team' },
  { id: 'TST-002', date: '2025-01-08', type: 'Drill', result: 'Pass', conductedBy: 'Fire Warden' },
  { id: 'TST-003', date: '2024-12-15', type: 'Monthly Test', result: 'Pass', conductedBy: 'Safety Team' },
  { id: 'TST-004', date: '2024-12-01', type: 'Quarterly Test', result: 'Pass', conductedBy: 'External Vendor' }
])

// UI State
const showHistory = ref(false)
const showEquipment = ref(false)
const showEvacuationMap = ref(false)
const searchKeyword = ref('')
const emergencyActive = ref(false)

const filteredZones = computed(() => {
  if (!searchKeyword.value) return fireZones.value
  return fireZones.value.filter(z =>
      z.name.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

const getZoneStatusColor = (status: string) => {
  switch(status) {
    case 'alarm': return '#F56C6C'
    case 'warning': return '#E6A23C'
    case 'normal': return '#67C23A'
    default: return '#909399'
  }
}

const getZoneStatusText = (status: string) => {
  switch(status) {
    case 'alarm': return 'ALARM'
    case 'warning': return 'Warning'
    case 'normal': return 'Normal'
    default: return 'Unknown'
  }
}

// Emergency actions
const activateEmergency = () => {
  ElMessageBox.confirm(
      'ACTIVATE FIRE EMERGENCY PROTOCOL?\n\nThis will:\n- Sound all fire alarms\n- Activate emergency lighting\n- Notify all occupants to evacuate\n- Alert emergency services\n\nOnly use in actual emergency!',
      'Fire Emergency Activation',
      {
        confirmButtonText: 'ACTIVATE EMERGENCY',
        cancelButtonText: 'Cancel',
        type: 'error'
      }
  ).then(() => {
    emergencyActive.value = true
    emergencyStatus.value.isActive = true
    emergencyStatus.value.alarmType = 'Fire'
    emergencyStatus.value.alarmLevel = 'Critical'
    emergencyStatus.value.triggeredAt = new Date().toLocaleString()
    emergencyStatus.value.evacuationStatus = 'In Progress'

    // Set affected zones
    const alarmZones = fireZones.value.filter(z => z.status === 'alarm')
    emergencyStatus.value.affectedZones = alarmZones.map(z => z.name)

    ElMessage.error('FIRE EMERGENCY ACTIVATED - EVACUATE IMMEDIATELY')

    // Update zone status
    alarmZones.forEach(zone => {
      zone.status = 'alarm'
    })
  }).catch(() => {})
}

const deactivateEmergency = () => {
  ElMessageBox.confirm(
      'Deactivate Fire Emergency?\n\nConfirm that the fire has been extinguished and area is safe.',
      'Deactivate Emergency',
      {
        confirmButtonText: 'Deactivate',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    emergencyActive.value = false
    emergencyStatus.value.isActive = false
    emergencyStatus.value.evacuationStatus = 'Complete'
    ElMessage.success('Emergency deactivated - All clear')

    // Reset zone status
    fireZones.value.forEach(zone => {
      if (zone.status === 'alarm') {
        zone.status = 'normal'
      }
    })
  }).catch(() => {})
}

const initiateEvacuation = () => {
  ElMessageBox.confirm(
      'Initiate BUILDING EVACUATION?\n\nThis will notify all occupants to leave the building immediately.',
      'Evacuation Warning',
      {
        confirmButtonText: 'START EVACUATION',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    ElMessage.error('EVACUATION INITIATED - All occupants must evacuate')
    emergencyStatus.value.evacuationStatus = 'In Progress'
  }).catch(() => {})
}

const callEmergencyServices = () => {
  ElMessageBox.confirm(
      'Call Emergency Services (911)?',
      'Emergency Call',
      {
        confirmButtonText: 'Call Now',
        cancelButtonText: 'Cancel',
        type: 'error'
      }
  ).then(() => {
    ElMessage.success('Dialing 911... Emergency services notified')
  }).catch(() => {})
}

const resetAlarm = (zone: any) => {
  ElMessageBox.confirm(
      `Reset alarm for ${zone.name}?`,
      'Reset Alarm',
      {
        confirmButtonText: 'Reset',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    zone.status = 'normal'
    zone.alerts = []
    ElMessage.success(`Alarm reset for ${zone.name}`)
  }).catch(() => {})
}

const runSystemTest = () => {
  ElMessageBox.confirm(
      'Run fire alarm system test? This will test all alarms and notifications.',
      'System Test',
      {
        confirmButtonText: 'Start Test',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    ElMessage.info('System test in progress...')
    setTimeout(() => {
      ElMessage.success('System test completed - All devices operational')
    }, 3000)
  }).catch(() => {})
}

const refreshData = () => {
  ElMessage.info('Refreshing fire emergency data...')
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
        <div class="loading-tip">Fire Emergency Response</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="fire-emergency">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Fire Emergency Response</h2>
        <p class="subtitle">Real-time fire detection, alarm management and evacuation coordination</p>
      </div>
      <div class="header-actions">
        <el-button type="danger" @click="runSystemTest">
          <el-icon><Operation /></el-icon> Test System
        </el-button>
        <el-button @click="showEquipment = true">
          <el-icon><Tools /></el-icon> Equipment
        </el-button>
        <el-button @click="showHistory = true">
          <el-icon><Document /></el-icon> History
        </el-button>
        <el-button type="primary" @click="refreshData">
          <el-icon><RefreshRight /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- Emergency Alert Banner -->
    <div v-if="emergencyActive" class="emergency-banner">
      <div class="emergency-icon">🔥</div>
      <div class="emergency-info">
        <div class="emergency-title">FIRE EMERGENCY ACTIVE</div>
        <div class="emergency-desc">Evacuation in progress • Stay calm • Follow exit signs</div>
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
          <el-icon><Bell /></el-icon> Activate Alarm
        </el-button>
        <el-button type="warning" plain size="large" @click="initiateEvacuation">
          <el-icon><Operation /></el-icon> Evacuate Building
        </el-button>
        <el-button type="danger" plain size="large" @click="callEmergencyServices">
          <el-icon><Phone /></el-icon> Call 911
        </el-button>
      </div>
    </div>

    <!-- Fire Zones Status -->
    <div class="zones-section">
      <div class="section-header">
        <span>Fire Alarm Zones</span>
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
            <div class="zone-stat">Smoke Detectors: {{ zone.smokeDetectors }}</div>
            <div class="zone-stat">Last Test: {{ zone.lastTest }}</div>
          </div>
          <div class="zone-alerts" v-if="zone.alerts.length > 0">
            <div v-for="alert in zone.alerts" :key="alert.time" class="alert-item-small">
              <el-icon><Warning /></el-icon> {{ alert.type }} at {{ alert.location }} ({{ alert.time }})
            </div>
          </div>
          <div class="zone-actions" v-if="zone.status === 'alarm'">
            <el-button size="small" type="danger" @click="resetAlarm(zone)">Reset Alarm</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Evacuation Routes -->
    <el-card class="routes-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span><el-icon><Location /></el-icon> Evacuation Routes</span>
          <el-button type="primary" link @click="showEvacuationMap = true">View Map</el-button>
        </div>
      </template>
      <div class="routes-grid">
        <div v-for="route in evacuationRoutes" :key="route.id" class="route-card">
          <div class="route-name">{{ route.name }}</div>
          <div class="route-path">{{ route.from }} → {{ route.to }}</div>
          <div class="route-capacity">Capacity: {{ route.capacity }} people</div>
          <div class="route-status" :class="route.status">Status: {{ route.status }}</div>
        </div>
      </div>
    </el-card>

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

    <!-- Fire Equipment Dialog -->
    <el-dialog v-model="showEquipment" title="Fire Fighting Equipment" width="700px">
      <el-table :data="fireEquipment" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="Equipment" min-width="160" />
        <el-table-column prop="location" label="Location" min-width="150" />
        <el-table-column prop="type" label="Type" width="80" />
        <el-table-column label="Status" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'ready' ? 'success' : 'danger'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastInspection" label="Last Inspection" width="110" />
      </el-table>
      <template #footer>
        <el-button @click="showEquipment = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Alarm History Dialog -->
    <el-dialog v-model="showHistory" title="Alarm History" width="800px">
      <el-table :data="alarmHistory" stripe>
        <el-table-column prop="date" label="Date" width="100" />
        <el-table-column prop="time" label="Time" width="80" />
        <el-table-column prop="zone" label="Zone" min-width="140" />
        <el-table-column prop="type" label="Type" width="110" />
        <el-table-column label="Status" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Cleared' ? 'success' : row.status === 'False Alarm' ? 'info' : 'warning'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="responseTime" label="Response Time" width="100" />
      </el-table>
      <template #footer>
        <el-button @click="showHistory = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Evacuation Map Dialog -->
    <el-dialog v-model="showEvacuationMap" title="Evacuation Map" width="800px">
      <div class="evacuation-map">
        <div class="map-placeholder">
          <div class="map-grid">
            <div class="floor-label">Floor 2</div>
            <div class="floor-layout">
              <div class="room">Office</div>
              <div class="corridor">← Corridor →</div>
              <div class="stairwell">Stairwell B</div>
              <div class="room">Server Room</div>
            </div>
            <div class="exit-label">▼ Exit to Ground</div>

            <div class="floor-label" style="margin-top: 20px;">Floor 1</div>
            <div class="floor-layout">
              <div class="stairwell">Stairwell A</div>
              <div class="corridor">← Main Corridor →</div>
              <div class="room">Conference</div>
              <div class="room">Lobby</div>
            </div>
            <div class="exit-label">▼ Main Exit → Parking Lot</div>

            <div class="floor-label" style="margin-top: 20px;">Ground Floor</div>
            <div class="floor-layout">
              <div class="exit-gate">EAST EXIT → Street</div>
              <div class="exit-gate">WEST EXIT → Street</div>
              <div class="exit-gate">MAIN EXIT → Parking</div>
            </div>
            <div class="assembly-point">📌 Assembly Point: North Parking Lot</div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showEvacuationMap = false">Close</el-button>
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
.fire-emergency {
  padding: 24px;
  background: linear-gradient(135deg, #fff5f5 0%, #ffe0e0 100%);
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
  background: linear-gradient(135deg, #c62828, #ef5350);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  margin: 0;
  color: #c62828;
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
.emergency-desc { font-size: 14px; opacity: 0.9; }

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
  min-width: 180px;
}

/* Zones Section */
.zones-section {
  background: white;
  border-radius: 20px;
  padding: 16px 20px;
  margin-bottom: 24px;
}

.zones-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.zone-card {
  background: #f8f9fa;
  border-radius: 16px;
  padding: 16px;
  transition: all 0.2s ease;
  border-left: 4px solid #67C23A;
}

.zone-card.alarm { border-left-color: #F56C6C; background: #fff0f0; }
.zone-card.warning { border-left-color: #E6A23C; }

.zone-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.zone-name { font-weight: 600; font-size: 16px; }
.zone-status { font-weight: 600; font-size: 14px; }

.zone-stats {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
  margin-bottom: 12px;
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

/* Routes Card */
.routes-card {
  border-radius: 20px;
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.routes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}

.route-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 12px;
}

.route-name { font-weight: 600; margin-bottom: 4px; }
.route-path { font-size: 12px; color: #606266; margin-bottom: 4px; }
.route-capacity { font-size: 11px; color: #909399; margin-bottom: 4px; }
.route-status.clear { color: #67C23A; font-weight: 500; font-size: 12px; }
.route-status.blocked { color: #F56C6C; }

/* Contacts Card */
.contacts-card {
  border-radius: 20px;
  margin-bottom: 24px;
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

/* Evacuation Map */
.evacuation-map {
  padding: 20px;
}

.map-placeholder {
  background: #f0f2f5;
  border-radius: 16px;
  padding: 20px;
  min-height: 400px;
}

.map-grid {
  font-family: monospace;
}

.floor-label {
  font-weight: 600;
  margin-bottom: 8px;
  color: #606266;
}

.floor-layout {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}

.room, .corridor, .stairwell, .exit-gate {
  padding: 8px 12px;
  background: #e4e7ed;
  border-radius: 8px;
  font-size: 12px;
}

.stairwell { background: #fff3e0; color: #E6A23C; }
.exit-gate { background: #fde2e2; color: #F56C6C; }
.exit-label { color: #F56C6C; font-size: 12px; margin-top: 8px; }
.assembly-point { margin-top: 20px; padding: 12px; background: #e8f5e9; border-radius: 8px; color: #67C23A; font-weight: 500; }

/* Responsive */
@media (max-width: 768px) {
  .fire-emergency { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .action-buttons { flex-direction: column; }
  .action-buttons .el-button { width: 100%; }
  .zones-grid { grid-template-columns: 1fr; }
}
</style>