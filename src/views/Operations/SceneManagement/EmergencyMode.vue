<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
  RefreshRight, Warning, CircleCheck, Clock,
  Monitor, Tools, Search, Setting,
  Operation, Document, Grid, List,
  Sunny, Moon, Connection, HomeFilled,
  Switch, Check, Close, Edit, Delete,
  Plus, CopyDocument, TrendCharts, DataAnalysis,
  Lightning, Timer, Lock, User, Bell, VideoCamera
} from "@element-plus/icons-vue"
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Initializing emergency protocols...',
  'Activating safety systems...',
  'Notifying response teams...',
  'Ready for operation...'
]

// Scene status
const sceneStatus = ref({
  isActive: false,
  lastActivated: '2025-01-16 00:00:00',
  emergencyType: 'None',
  activeDuration: '0h 0m',
  responseTeam: 'Standby',
  evacuationStatus: 'Normal'
})

// Emergency metrics
const emergencyMetrics = ref({
  activeAlerts: 0,
  responseTime: 'N/A',
  peopleEvacuated: 0,
  safeZones: 12,
  affectedZones: 0,
  emergencyPowerStatus: 'Normal'
})

// Emergency device groups
const deviceGroups = ref([
  {
    id: 'lighting',
    name: 'Emergency Lighting',
    icon: 'Sunny',
    status: 'standby',
    settings: {
      emergencyMode: 'Ready',
      batteryBackup: '100%',
      illuminationLevel: 'Maximum',
      exitSigns: 'Lit'
    },
    devices: [
      { name: 'Emergency Lights', currentValue: 'Standby', status: 'ready' },
      { name: 'Exit Signs', currentValue: 'Lit', status: 'active' },
      { name: 'Stairwell Lights', currentValue: 'Standby', status: 'ready' }
    ]
  },
  {
    id: 'alarm',
    name: 'Alarm Systems',
    icon: 'Bell',
    status: 'active',
    settings: {
      fireAlarm: 'Armed',
      strobes: 'Ready',
      sirens: 'Ready',
      notification: 'Enabled'
    },
    devices: [
      { name: 'Fire Alarms', currentValue: 'Armed', status: 'ready' },
      { name: 'Strobe Lights', currentValue: 'Ready', status: 'ready' },
      { name: 'Mass Notification', currentValue: 'Standby', status: 'ready' }
    ]
  },
  {
    id: 'access',
    name: 'Access Control',
    icon: 'Lock',
    status: 'standby',
    settings: {
      doorLocks: 'Auto Release',
      emergencyExits: 'Unlocked',
      secureDoors: 'Locked',
      accessMode: 'Emergency'
    },
    devices: [
      { name: 'Main Entrances', currentValue: 'Auto Release', status: 'ready' },
      { name: 'Emergency Exits', currentValue: 'Unlocked', status: 'active' },
      { name: 'Secure Doors', currentValue: 'Locked', status: 'secure' }
    ]
  },
  {
    id: 'power',
    name: 'Emergency Power',
    icon: 'Lightning',
    status: 'standby',
    settings: {
      upsStatus: 'Ready',
      generatorStatus: 'Auto',
      criticalLoads: 'Protected',
      powerShedding: 'Active'
    },
    devices: [
      { name: 'UPS Systems', currentValue: 'Ready', status: 'ready' },
      { name: 'Emergency Generator', currentValue: 'Auto', status: 'standby' },
      { name: 'Critical Loads', currentValue: 'Protected', status: 'active' }
    ]
  },
  {
    id: 'cctv',
    name: 'CCTV Monitoring',
    icon: 'VideoCamera',
    status: 'active',
    settings: {
      recordingMode: 'Continuous',
      motionDetection: 'Enhanced',
      remoteAccess: 'Enabled',
      backupRecording: 'Active'
    },
    devices: [
      { name: 'Security Cameras', currentValue: 'Recording', status: 'active' },
      { name: 'Emergency Monitors', currentValue: 'Live', status: 'active' },
      { name: 'Recording System', currentValue: 'Active', status: 'active' }
    ]
  },
  {
    id: 'evacuation',
    name: 'Evacuation Systems',
    icon: 'User',
    status: 'standby',
    settings: {
      evacLights: 'Ready',
      voiceGuidance: 'Standby',
      signageDirection: 'Active',
      assemblyPoints: 'Designated'
    },
    devices: [
      { name: 'Evacuation Lighting', currentValue: 'Ready', status: 'ready' },
      { name: 'Voice Evac System', currentValue: 'Standby', status: 'ready' },
      { name: 'Digital Signage', currentValue: 'Active', status: 'active' }
    ]
  }
])

// Emergency procedures
const emergencyProcedures = ref([
  { id: 'PROC-001', name: 'Fire Emergency', steps: 'Activate alarm → Evacuate area → Call 911 → Assemble at meeting point', responseTeam: 'Fire Wardens', lastDrill: '2025-01-10' },
  { id: 'PROC-002', name: 'Medical Emergency', steps: 'Assess situation → Call medical team → Provide first aid → Document incident', responseTeam: 'Medical Response', lastDrill: '2025-01-05' },
  { id: 'PROC-003', name: 'Security Threat', steps: 'Lockdown area → Notify security → Monitor cameras → Await instructions', responseTeam: 'Security Team', lastDrill: '2024-12-15' },
  { id: 'PROC-004', name: 'Power Outage', steps: 'Verify UPS status → Start generator → Monitor critical loads → Restore power', responseTeam: 'Facilities Team', lastDrill: '2025-01-08' }
])

// Scene transition history
const transitionHistory = ref([
  { time: '14:30:00', date: '2025-01-15', fromScene: 'Normal Mode', toScene: 'Fire Drill', operator: 'System', duration: '15 min' },
  { time: '09:00:00', date: '2025-01-10', fromScene: 'Normal Mode', toScene: 'Medical Emergency', operator: 'Manual', duration: '45 min' },
  { time: '22:15:00', date: '2025-01-05', fromScene: 'Normal Mode', toScene: 'Power Outage', operator: 'Auto', duration: '2h 30m' },
  { time: '11:00:00', date: '2024-12-20', fromScene: 'Normal Mode', toScene: 'Security Lockdown', operator: 'Security', duration: '1h' }
])

// Edit mode
const editingGroup = ref<string | null>(null)
const editSettings = ref<any>({})

const getStatusColor = (status: string) => {
  switch(status) {
    case 'critical': return '#F56C6C'
    case 'warning': return '#E6A23C'
    case 'active': return '#67C23A'
    case 'standby': return '#409EFF'
    case 'ready': return '#67C23A'
    case 'secure': return '#F56C6C'
    default: return '#909399'
  }
}

const getStatusText = (status: string) => {
  switch(status) {
    case 'standby': return 'Standby'
    case 'ready': return 'Ready'
    case 'active': return 'Active'
    case 'secure': return 'Secured'
    default: return status
  }
}

const getDeviceStatusIcon = (status: string) => {
  if (status === 'active') return 'success'
  if (status === 'ready') return 'success'
  if (status === 'standby') return 'warning'
  if (status === 'secure') return 'danger'
  return 'info'
}

const startEdit = (group: any) => {
  editingGroup.value = group.id
  editSettings.value = JSON.parse(JSON.stringify(group.settings))
}

const saveSettings = (group: any) => {
  group.settings = { ...editSettings.value }
  editingGroup.value = null
  ElMessage.success(`${group.name} settings updated successfully`)
}

const cancelEdit = () => {
  editingGroup.value = null
  editSettings.value = {}
}

const activateEmergency = (type: string) => {
  ElMessageBox.confirm(
      `ACTIVATE ${type.toUpperCase()} EMERGENCY MODE?\n\nThis will trigger all emergency protocols and alert response teams.`,
      'Emergency Activation',
      {
        confirmButtonText: 'ACTIVATE',
        cancelButtonText: 'Cancel',
        type: 'error'
      }
  ).then(() => {
    sceneStatus.value.isActive = true
    sceneStatus.value.emergencyType = type
    sceneStatus.value.lastActivated = new Date().toLocaleString()
    emergencyMetrics.value.activeAlerts = 1
    emergencyMetrics.value.responseTime = '0s'

    ElMessage.error(`${type.toUpperCase()} EMERGENCY MODE ACTIVATED - All response teams notified`)

    // Simulate automatic response
    setTimeout(() => {
      emergencyMetrics.value.responseTime = '45s'
      ElMessage.warning('Emergency response team dispatched')
    }, 3000)
  }).catch(() => {})
}

const deactivateEmergency = () => {
  ElMessageBox.confirm(
      'Deactivate Emergency Mode?\n\nConfirm that the emergency situation has been resolved.',
      'Deactivate Emergency Mode',
      {
        confirmButtonText: 'Deactivate',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    sceneStatus.value.isActive = false
    sceneStatus.value.emergencyType = 'None'
    emergencyMetrics.value.activeAlerts = 0

    ElMessage.success('Emergency mode deactivated - All clear signal sent')
  }).catch(() => {})
}

const initiateEvacuation = () => {
  ElMessageBox.confirm(
      'INITIATE BUILDING EVACUATION?\n\nThis will activate all evacuation systems and alert all occupants.',
      'Evacuation Warning',
      {
        confirmButtonText: 'START EVACUATION',
        cancelButtonText: 'Cancel',
        type: 'error'
      }
  ).then(() => {
    ElMessage.error('EVACUATION INITIATED - All occupants must proceed to nearest exit')
    sceneStatus.value.evacuationStatus = 'In Progress'
    emergencyMetrics.value.peopleEvacuated = 0

    // Simulate evacuation progress
    const interval = setInterval(() => {
      if (emergencyMetrics.value.peopleEvacuated < 250) {
        emergencyMetrics.value.peopleEvacuated += 50
      } else {
        clearInterval(interval)
        sceneStatus.value.evacuationStatus = 'Complete'
        ElMessage.success('Evacuation complete - All occupants accounted for')
      }
    }, 2000)
  }).catch(() => {})
}

const runDrill = () => {
  ElMessageBox.confirm(
      'Initiate emergency drill? This will test all emergency systems without full activation.',
      'Emergency Drill',
      {
        confirmButtonText: 'Start Drill',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    ElMessage.info('Emergency drill started - Testing all systems')
    setTimeout(() => {
      ElMessage.success('Drill completed - All systems operational')
    }, 5000)
  }).catch(() => {})
}

const resetToDefault = () => {
  ElMessageBox.confirm(
      'Reset all Emergency Mode settings to factory defaults? This action cannot be undone.',
      'Reset to Default',
      {
        confirmButtonText: 'Reset',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    ElMessage.success('All settings reset to default values')
  }).catch(() => {})
}

const refreshData = () => {
  ElMessage.info('Refreshing emergency data...')
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

// Helper function to get icon component
const getIconComponent = (iconName: string) => {
  const icons: Record<string, any> = {
    Sunny, Bell, Lock, Lightning, VideoCamera, User
  }
  return icons[iconName] || Setting
}
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
        <div class="loading-tip">Scene Management - Emergency Mode</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="emergency-mode">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Emergency Mode</h2>
        <p class="subtitle">Emergency response and life safety systems management</p>
      </div>
      <div class="header-actions">
        <el-button type="danger" @click="runDrill">
          <el-icon><Operation /></el-icon> Run Drill
        </el-button>
        <el-button @click="resetToDefault">
          <el-icon><RefreshRight /></el-icon> Reset Defaults
        </el-button>
        <el-button type="primary" @click="refreshData">
          <el-icon><RefreshRight /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- Active Emergency Banner -->
    <div v-if="sceneStatus.isActive" class="active-emergency-banner" :class="{ active: sceneStatus.isActive }">
      <div class="emergency-icon">🚨</div>
      <div class="emergency-info">
        <div class="emergency-title">EMERGENCY MODE ACTIVE</div>
        <div class="emergency-type">Type: {{ sceneStatus.emergencyType }}</div>
        <div class="emergency-time">Activated: {{ sceneStatus.lastActivated }}</div>
      </div>
      <div class="emergency-actions">
        <el-button type="danger" size="large" @click="deactivateEmergency">DEACTIVATE</el-button>
      </div>
    </div>

    <!-- Quick Emergency Actions -->
    <div class="quick-actions">
      <div class="section-header">
        <span>Quick Emergency Response</span>
        <el-tag type="danger" size="small">Immediate Action</el-tag>
      </div>
      <div class="action-buttons">
        <el-button type="danger" plain size="large" @click="activateEmergency('Fire')">
          <el-icon><Warning /></el-icon> Fire Emergency
        </el-button>
        <el-button type="warning" plain size="large" @click="activateEmergency('Medical')">
          <el-icon><User /></el-icon> Medical Emergency
        </el-button>
        <el-button type="danger" plain size="large" @click="activateEmergency('Security')">
          <el-icon><Lock /></el-icon> Security Threat
        </el-button>
        <el-button type="warning" plain size="large" @click="activateEmergency('Power Outage')">
          <el-icon><Lightning /></el-icon> Power Outage
        </el-button>
        <el-button type="danger" plain size="large" @click="initiateEvacuation">
          <el-icon><Operation /></el-icon> Building Evacuation
        </el-button>
      </div>
    </div>

    <!-- Emergency Status Metrics -->
    <div class="metrics-grid">
      <el-card class="metric-card" shadow="hover">
        <div class="metric-content">
          <div class="metric-icon status"><el-icon><Bell /></el-icon></div>
          <div class="metric-info">
            <div class="metric-value">{{ sceneStatus.isActive ? 'ACTIVE' : 'STANDBY' }}</div>
            <div class="metric-label">Emergency Status</div>
          </div>
        </div>
      </el-card>
      <el-card class="metric-card" shadow="hover">
        <div class="metric-content">
          <div class="metric-icon response"><el-icon><Clock /></el-icon></div>
          <div class="metric-info">
            <div class="metric-value">{{ emergencyMetrics.responseTime }}</div>
            <div class="metric-label">Response Time</div>
          </div>
        </div>
      </el-card>
      <el-card class="metric-card" shadow="hover">
        <div class="metric-content">
          <div class="metric-icon evac"><el-icon><User /></el-icon></div>
          <div class="metric-info">
            <div class="metric-value">{{ emergencyMetrics.peopleEvacuated }}</div>
            <div class="metric-label">Evacuated</div>
          </div>
        </div>
      </el-card>
      <el-card class="metric-card" shadow="hover">
        <div class="metric-content">
          <div class="metric-icon safety"><el-icon><CircleCheck /></el-icon></div>
          <div class="metric-info">
            <div class="metric-value">{{ emergencyMetrics.safeZones }}</div>
            <div class="metric-label">Safe Zones</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Emergency Procedures -->
    <el-card class="procedures-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Emergency Response Procedures</span>
          <el-tag type="info" size="small">Standard Operating Procedures</el-tag>
        </div>
      </template>
      <el-table :data="emergencyProcedures" stripe>
        <el-table-column prop="name" label="Emergency Type" align="center" />
        <el-table-column prop="steps" label="Response Steps" align="center" />
        <el-table-column prop="responseTeam" label="Response Team" align="center" />
        <el-table-column prop="lastDrill" label="Last Drill" align="center" />
      </el-table>
    </el-card>

    <!-- Emergency Systems Grid -->
    <div class="groups-grid">
      <div v-for="group in deviceGroups" :key="group.id" class="group-card">
        <div class="group-header">
          <div class="group-title">
            <el-icon><component :is="getIconComponent(group.icon)" /></el-icon>
            <span>{{ group.name }}</span>
          </div>
          <div class="group-status">
            <span class="status-dot" :style="{ background: getStatusColor(group.status) }"></span>
            <span>{{ getStatusText(group.status) }}</span>
          </div>
        </div>

        <!-- Settings Section -->
        <div class="settings-section">
          <div class="section-label">Emergency Settings</div>
          <div class="settings-grid">
            <div class="setting-item" v-for="(value, key) in group.settings" :key="key">
              <span class="setting-label">{{ key.replace(/([A-Z])/g, ' $1').trim() }}</span>
              <span class="setting-value">{{ value }}</span>
            </div>
          </div>
        </div>

        <!-- Devices Preview -->
        <div class="devices-preview">
          <div class="section-label">System Status</div>
          <div class="devices-list">
            <div v-for="device in group.devices" :key="device.name" class="device-item">
              <span class="device-name">{{ device.name }}</span>
              <span class="device-value">{{ device.currentValue }}</span>
              <el-tag :type="getDeviceStatusIcon(device.status)" size="small">{{ device.status }}</el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Transition History -->
    <el-card class="history-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Emergency Event History</span>
          <el-tag type="info" size="small">Last 4 events</el-tag>
        </div>
      </template>
      <el-table :data="transitionHistory" stripe>
        <el-table-column prop="date" label="Date" align="center" />
        <el-table-column prop="time" label="Time" align="center"/>
        <el-table-column prop="fromScene" label="Previous Mode" align="center" />
        <el-table-column prop="toScene" label="Event Type" align="center" />
        <el-table-column prop="operator" label="Triggered By" align="center"/>
        <el-table-column prop="duration" label="Duration" align="center" />
      </el-table>
    </el-card>

    <!-- Safety Instructions -->
    <el-card class="safety-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Safety Instructions</span>
          <el-tag type="warning" size="small">Read Carefully</el-tag>
        </div>
      </template>
      <div class="safety-grid">
        <div class="safety-item">
          <div class="safety-icon">🚪</div>
          <div class="safety-content">
            <h4>Know Your Exits</h4>
            <p>Locate the nearest emergency exit and alternate exit routes in your area.</p>
          </div>
        </div>
        <div class="safety-item">
          <div class="safety-icon">🚨</div>
          <div class="safety-content">
            <h4>Alarm Recognition</h4>
            <p>Familiarize yourself with fire alarm sounds and emergency announcement patterns.</p>
          </div>
        </div>
        <div class="safety-item">
          <div class="safety-icon">🆘</div>
          <div class="safety-content">
            <h4>Emergency Contacts</h4>
            <p>Security: 555-0199 • Medical: 555-0119 • Fire: 555-0099</p>
          </div>
        </div>
        <div class="safety-item">
          <div class="safety-icon">📢</div>
          <div class="safety-content">
            <h4>Follow Instructions</h4>
            <p>Always follow instructions from emergency personnel and voice evacuation systems.</p>
          </div>
        </div>
      </div>
    </el-card>
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
.emergency-mode {
  padding: 24px;
  background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
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

/* Active Emergency Banner */
.active-emergency-banner {
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
.emergency-type { font-size: 14px; opacity: 0.9; }
.emergency-time { font-size: 12px; opacity: 0.8; margin-top: 4px; }

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
  min-width: 150px;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.metric-card {
  border-radius: 20px;
  transition: all 0.3s ease;
  background: white;
}

.metric-card:hover { transform: translateY(-4px); }
.metric-card :deep(.el-card__body) { padding: 20px; }

.metric-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.metric-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.metric-icon.status { background: rgba(245, 108, 108, 0.1); color: #F56C6C; }
.metric-icon.response { background: rgba(33, 150, 243, 0.1); color: #2196F3; }
.metric-icon.evac { background: rgba(76, 175, 80, 0.1); color: #4CAF50; }
.metric-icon.safety { background: rgba(76, 175, 80, 0.1); color: #4CAF50; }

.metric-info { flex: 1; }
.metric-value { font-size: 24px; font-weight: 700; color: #303133; line-height: 1.2; }
.metric-label { font-size: 13px; color: #909399; margin-top: 4px; }

/* Procedures Card */
.procedures-card {
  border-radius: 20px;
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

/* Groups Grid */
.groups-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.group-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.group-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1); }

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.group-title {
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.group-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.status-dot { width: 8px; height: 8px; border-radius: 50%; }

.section-label {
  font-size: 12px;
  font-weight: 600;
  color: #F56C6C;
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.setting-label { font-size: 12px; color: #909399; }
.setting-value { font-size: 13px; font-weight: 500; color: #303133; }

.devices-preview {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 16px;
}

.devices-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.device-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.device-name { color: #606266; }
.device-value { font-weight: 500; color: #303133; }

/* History Card */
.history-card {
  border-radius: 20px;
  margin-bottom: 24px;
}

/* Safety Card */
.safety-card {
  border-radius: 20px;
}

.safety-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.safety-item {
  display: flex;
  gap: 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 12px;
}

.safety-icon { font-size: 32px; }
.safety-content h4 { margin: 0 0 4px 0; font-size: 14px; font-weight: 600; }
.safety-content p { margin: 0; font-size: 12px; color: #909399; line-height: 1.4; }

/* Responsive */
@media (max-width: 1200px) {
  .metrics-grid { grid-template-columns: repeat(2, 1fr); }
  .groups-grid { grid-template-columns: 1fr; }
  .safety-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .emergency-mode { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .metrics-grid { grid-template-columns: 1fr; }
  .action-buttons { flex-direction: column; }
  .action-buttons .el-button { width: 100%; }
  .settings-grid { grid-template-columns: 1fr; }
}
</style>