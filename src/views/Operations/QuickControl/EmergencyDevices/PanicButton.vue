<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
  RefreshRight, Warning, CircleCheck, Clock,
  Monitor, Tools, Search, Setting,
  Operation, AlarmClock, Document,
  Grid, List, DataLine, Bell,
  Location, User, Phone, VideoCamera
} from "@element-plus/icons-vue"
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Initializing panic button system...',
  'Connecting to emergency response network...',
  'Loading device status...',
  'Ready for operation...'
]

// System status
const systemStatus = ref({
  overallHealth: 98,
  onlineDevices: 24,
  totalDevices: 24,
  activeAlerts: 0,
  lastSystemTest: '2025-01-15 14:30:00',
  responseTeamStatus: 'available'
})

// Panic button locations
const panicButtons = ref([
  {
    id: 'PB-101',
    name: 'Reception Desk',
    location: 'Main Lobby - Reception',
    status: 'active',
    batteryLevel: 98,
    lastTest: '2025-01-15',
    type: 'Fixed',
    zone: 'Lobby',
    assignedResponse: 'Security Team'
  },
  {
    id: 'PB-102',
    name: 'Security Desk',
    location: 'Security Control Room',
    status: 'active',
    batteryLevel: 96,
    lastTest: '2025-01-14',
    type: 'Fixed',
    zone: 'Security',
    assignedResponse: 'Security Team'
  },
  {
    id: 'PB-103',
    name: 'Manager Office',
    location: '2nd Floor - Room 201',
    status: 'active',
    batteryLevel: 94,
    lastTest: '2025-01-13',
    type: 'Fixed',
    zone: 'Admin',
    assignedResponse: 'Security Team'
  },
  {
    id: 'PB-104',
    name: 'Nurse Station',
    location: 'Medical Clinic',
    status: 'active',
    batteryLevel: 97,
    lastTest: '2025-01-12',
    type: 'Fixed',
    zone: 'Medical',
    assignedResponse: 'Medical Team'
  },
  {
    id: 'PB-105',
    name: 'Server Room',
    location: 'Data Center A',
    status: 'active',
    batteryLevel: 99,
    lastTest: '2025-01-11',
    type: 'Fixed',
    zone: 'Critical',
    assignedResponse: 'Security & IT'
  },
  {
    id: 'PB-201',
    name: 'Mobile Guard 1',
    location: 'Patrol Area A',
    status: 'active',
    batteryLevel: 92,
    lastTest: '2025-01-15',
    type: 'Mobile',
    zone: 'Patrol',
    assignedResponse: 'Security Team'
  },
  {
    id: 'PB-202',
    name: 'Mobile Guard 2',
    location: 'Patrol Area B',
    status: 'inactive',
    batteryLevel: 45,
    lastTest: '2024-12-28',
    type: 'Mobile',
    zone: 'Patrol',
    assignedResponse: 'Security Team'
  },
  {
    id: 'PB-106',
    name: 'HR Department',
    location: '3rd Floor - HR Office',
    status: 'active',
    batteryLevel: 95,
    lastTest: '2025-01-10',
    type: 'Fixed',
    zone: 'Admin',
    assignedResponse: 'Security Team'
  },
  {
    id: 'PB-107',
    name: 'Loading Dock',
    location: 'Warehouse Entrance',
    status: 'active',
    batteryLevel: 88,
    lastTest: '2025-01-09',
    type: 'Fixed',
    zone: 'Warehouse',
    assignedResponse: 'Security Team'
  },
  {
    id: 'PB-108',
    name: 'Cafeteria',
    location: '1st Floor - Cafeteria',
    status: 'active',
    batteryLevel: 93,
    lastTest: '2025-01-08',
    type: 'Fixed',
    zone: 'Common Area',
    assignedResponse: 'Security Team'
  }
])

// Alert history
const alertHistory = ref([
  { id: 'ALT-001', time: '14:32:00', date: '2025-01-15', location: 'Reception Desk', triggeredBy: 'Security Officer', responseTime: '45s', status: 'resolved' },
  { id: 'ALT-002', time: '09:15:00', date: '2025-01-14', location: 'Medical Clinic', triggeredBy: 'Nurse', responseTime: '32s', status: 'resolved' },
  { id: 'ALT-003', time: '22:00:00', date: '2025-01-12', location: 'Server Room', triggeredBy: 'System', responseTime: '28s', status: 'resolved' },
  { id: 'ALT-004', time: '16:45:00', date: '2025-01-10', location: 'Manager Office', triggeredBy: 'Manager', responseTime: '52s', status: 'resolved' }
])

// Response teams
const responseTeams = ref([
  { name: 'Security Team', status: 'available', members: 8, responseTime: '30s' },
  { name: 'Medical Team', status: 'available', members: 4, responseTime: '60s' },
  { name: 'Facility Team', status: 'available', members: 6, responseTime: '120s' },
  { name: 'IT Emergency', status: 'standby', members: 3, responseTime: '180s' }
])

// Active alert state
const activeAlert = ref<any>(null)
const alertCountdown = ref(0)
const alertTimer = ref<any>(null)

// UI State
const showHistory = ref(false)
const searchKeyword = ref('')
const selectedZone = ref('all')

const getStatusColor = (status: string) => {
  switch(status) {
    case 'inactive': return '#F56C6C'
    case 'warning': return '#E6A23C'
    case 'active': return '#67C23A'
    default: return '#909399'
  }
}

const getStatusText = (status: string) => {
  switch(status) {
    case 'inactive': return 'Inactive'
    case 'warning': return 'Warning'
    case 'active': return 'Active'
    default: return 'Unknown'
  }
}

const filteredButtons = computed(() => {
  let filtered = panicButtons.value

  if (selectedZone.value !== 'all') {
    filtered = filtered.filter(b => b.zone === selectedZone.value)
  }

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(b =>
        b.id.toLowerCase().includes(keyword) ||
        b.name.toLowerCase().includes(keyword) ||
        b.location.toLowerCase().includes(keyword)
    )
  }

  return filtered
})

const uniqueZones = computed(() => {
  const zones = new Set(panicButtons.value.map(b => b.zone))
  return Array.from(zones)
})

const triggerPanic = (button: any) => {
  ElMessageBox.confirm(
      `EMERGENCY: Trigger panic button at ${button.location}?\n\nThis will immediately notify ${button.assignedResponse} and activate emergency protocols.`,
      'Panic Button Activation',
      {
        confirmButtonText: 'ACTIVATE EMERGENCY',
        cancelButtonText: 'Cancel',
        type: 'error'
      }
  ).then(() => {
    // Create active alert
    activeAlert.value = {
      id: `ALT-${Date.now()}`,
      location: button.location,
      device: button.name,
      triggeredAt: new Date().toLocaleTimeString(),
      team: button.assignedResponse,
      status: 'active'
    }

    alertCountdown.value = 60
    ElMessage.error(`EMERGENCY ALERT ACTIVATED at ${button.location}! Response team dispatched.`)

    // Start countdown timer
    alertTimer.value = setInterval(() => {
      alertCountdown.value--
      if (alertCountdown.value <= 0) {
        clearInterval(alertTimer.value)
        resolveAlert()
      }
    }, 1000)

    // Add to history
    alertHistory.value.unshift({
      id: `ALT-${Date.now()}`,
      time: new Date().toLocaleTimeString(),
      date: new Date().toISOString().split('T')[0],
      location: button.location,
      triggeredBy: 'Manual',
      responseTime: '0s',
      status: 'active'
    })

    // Update button status
    button.status = 'warning'

  }).catch(() => {})
}

const resolveAlert = () => {
  if (alertTimer.value) {
    clearInterval(alertTimer.value)
    alertTimer.value = null
  }

  if (activeAlert.value) {
    ElMessage.success(`Emergency at ${activeAlert.value.location} resolved. All clear.`)

    // Update history entry
    const historyEntry = alertHistory.value.find(h => h.location === activeAlert.value.location && h.status === 'active')
    if (historyEntry) {
      historyEntry.status = 'resolved'
      historyEntry.responseTime = `${60 - alertCountdown.value}s`
    }

    // Reset button status
    const button = panicButtons.value.find(b => b.name === activeAlert.value.device)
    if (button) {
      button.status = 'active'
    }

    activeAlert.value = null
    alertCountdown.value = 0
  }
}

const testDevice = (button: any) => {
  ElMessageBox.confirm(
      `Test panic button at ${button.location}? This will send a test alert to the response team.`,
      'Test Device',
      {
        confirmButtonText: 'Run Test',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    ElMessage.info(`Testing ${button.name}...`)
    setTimeout(() => {
      ElMessage.success(`${button.name} test passed - Signal received`)
      button.lastTest = new Date().toISOString().split('T')[0]
    }, 2000)
  }).catch(() => {})
}

const scheduleMaintenance = (button: any) => {
  ElMessageBox.confirm(
      `Schedule maintenance for ${button.name}?`,
      'Schedule Maintenance',
      {
        confirmButtonText: 'Schedule',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    ElMessage.success(`Maintenance scheduled for ${button.name}`)
  }).catch(() => {})
}

const systemTest = () => {
  ElMessageBox.confirm(
      `Run system-wide panic button test? This will test all devices simultaneously.`,
      'System Test',
      {
        confirmButtonText: 'Start System Test',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    ElMessage.info('System test initiated...')
    setTimeout(() => {
      ElMessage.success('System test completed - All devices operational')
      systemStatus.value.lastSystemTest = new Date().toISOString().replace('T', ' ').slice(0, 19)
    }, 3000)
  }).catch(() => {})
}

const refreshData = () => {
  ElMessage.info('Refreshing panic button data...')
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
        <div class="loading-tip">Panic Button System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="panic-button-system">
    <!-- Active Alert Banner -->
    <div v-if="activeAlert" class="alert-banner">
      <div class="alert-icon">🚨</div>
      <div class="alert-info">
        <div class="alert-title">EMERGENCY ALERT ACTIVE</div>
        <div class="alert-location">{{ activeAlert.location }} - {{ activeAlert.device }}</div>
        <div class="alert-team">Responding: {{ activeAlert.team }}</div>
      </div>
      <div class="alert-timer">
        <div class="timer-circle">{{ alertCountdown }}</div>
        <div class="timer-label">seconds</div>
      </div>
      <el-button type="danger" size="large" @click="resolveAlert">RESOLVE</el-button>
    </div>

    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Panic Button System</h2>
        <p class="subtitle">Emergency alert monitoring and response management</p>
      </div>
      <div class="header-actions">
        <el-button type="danger" @click="systemTest" :disabled="activeAlert">
          <el-icon><Operation /></el-icon> System Test
        </el-button>
        <el-button @click="showHistory = true">
          <el-icon><Document /></el-icon> Alert History
        </el-button>
        <el-button type="primary" @click="refreshData">
          <el-icon><RefreshRight /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- System Status Cards -->
    <div class="stats-grid">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon total"><el-icon><Monitor /></el-icon></div>
          <div class="stat-info"><div class="stat-value">{{ systemStatus.onlineDevices }}/{{ systemStatus.totalDevices }}</div><div class="stat-label">Online Devices</div></div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon health"><el-icon><CircleCheck /></el-icon></div>
          <div class="stat-info"><div class="stat-value">{{ systemStatus.overallHealth }}%</div><div class="stat-label">System Health</div></div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon alerts"><el-icon><Warning /></el-icon></div>
          <div class="stat-info"><div class="stat-value">{{ systemStatus.activeAlerts }}</div><div class="stat-label">Active Alerts</div></div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon response"><el-icon><User /></el-icon></div>
          <div class="stat-info"><div class="stat-value">{{ systemStatus.responseTeamStatus }}</div><div class="stat-label">Response Team</div></div>
        </div>
      </el-card>
    </div>

    <!-- Response Teams Status -->
    <div class="teams-section">
      <div class="section-header">
        <span>Response Teams Status</span>
        <el-tag type="info" size="small">Ready</el-tag>
      </div>
      <div class="teams-grid">
        <div v-for="team in responseTeams" :key="team.name" class="team-card">
          <div class="team-name">{{ team.name }}</div>
          <div class="team-status" :class="team.status">
            {{ team.status.toUpperCase() }}
          </div>
          <div class="team-stats">
            <span>{{ team.members }} members</span>
            <span>Response: {{ team.responseTime }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Search and Filter -->
    <div class="search-bar">
      <el-input v-model="searchKeyword" placeholder="Search by ID, name or location..." clearable :prefix-icon="Search" style="width: 300px" />
      <el-select v-model="selectedZone" placeholder="Filter by zone" clearable style="width: 160px">
        <el-option label="All Zones" value="all" />
        <el-option v-for="zone in uniqueZones" :key="zone" :label="zone" :value="zone" />
      </el-select>
      <span class="results-count">{{ filteredButtons.length }} devices</span>
    </div>

    <!-- Panic Buttons Grid -->
    <div class="buttons-grid">
      <div v-for="button in filteredButtons" :key="button.id" class="button-card" :class="button.status">
        <div class="button-header">
          <div class="button-id">{{ button.id }}</div>
          <div class="button-status-dot" :style="{ background: getStatusColor(button.status) }"></div>
        </div>
        <div class="button-name">{{ button.name }}</div>
        <div class="button-location">
          <el-icon><Location /></el-icon> {{ button.location }}
        </div>
        <div class="button-details">
          <div class="detail-item">
            <span class="detail-label">Type</span>
            <span class="detail-value">{{ button.type }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Battery</span>
            <span class="detail-value" :style="{ color: button.batteryLevel < 70 ? '#E6A23C' : '#67C23A' }">
              {{ button.batteryLevel }}%
            </span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Last Test</span>
            <span class="detail-value">{{ button.lastTest }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Response Team</span>
            <span class="detail-value">{{ button.assignedResponse }}</span>
          </div>
        </div>
        <div class="button-actions">
          <el-button type="danger" size="small" @click="triggerPanic(button)" :disabled="activeAlert">
            <el-icon><Bell /></el-icon> PANIC
          </el-button>
          <el-button size="small" @click="testDevice(button)" :disabled="activeAlert">Test</el-button>
          <el-button size="small" type="warning" @click="scheduleMaintenance(button)" v-if="button.batteryLevel < 70">Maint</el-button>
        </div>
      </div>
    </div>

    <!-- Alert History Dialog -->
    <el-dialog v-model="showHistory" title="Alert History" width="800px">
      <el-table :data="alertHistory" stripe>
        <el-table-column prop="date" label="Date" width="110" />
        <el-table-column prop="time" label="Time" width="100" />
        <el-table-column prop="location" label="Location" min-width="160" />
        <el-table-column prop="triggeredBy" label="Triggered By" width="130" />
        <el-table-column prop="responseTime" label="Response Time" width="120" />
        <el-table-column label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'resolved' ? 'success' : 'danger'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
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
.panic-button-system {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
  min-height: 100vh;
}

/* Alert Banner */
.alert-banner {
  background: linear-gradient(135deg, #F56C6C, #FF4949);
  border-radius: 20px;
  padding: 20px 24px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  color: white;
  flex-wrap: wrap;
  animation: pulse-red-bg 1s infinite;
}

@keyframes pulse-red-bg {
  0%, 100% { box-shadow: 0 0 0 0 rgba(245, 108, 108, 0.4); }
  50% { box-shadow: 0 0 0 20px rgba(245, 108, 108, 0); }
}

.alert-icon { font-size: 48px; }
.alert-info { flex: 1; }
.alert-title { font-weight: 700; font-size: 20px; margin-bottom: 4px; }
.alert-location { font-size: 14px; opacity: 0.9; }
.alert-team { font-size: 12px; opacity: 0.8; margin-top: 4px; }

.alert-timer { text-align: center; }
.timer-circle { width: 60px; height: 60px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 700; }
.timer-label { font-size: 10px; margin-top: 4px; }

/* Page Header */
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
  background: linear-gradient(135deg, #303133, #606266);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 16px;
  transition: all 0.3s ease;
}

.stat-card:hover { transform: translateY(-4px); }
.stat-card :deep(.el-card__body) { padding: 16px; }

.stat-content {
  display: flex;
  align-items: center;
  gap: 12px;
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

.stat-icon.total { background: rgba(64, 158, 255, 0.1); color: #409EFF; }
.stat-icon.health { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
.stat-icon.alerts { background: rgba(245, 108, 108, 0.1); color: #F56C6C; }
.stat-icon.response { background: rgba(230, 162, 60, 0.1); color: #E6A23C; }

.stat-info { flex: 1; }
.stat-value { font-size: 24px; font-weight: 700; color: #303133; line-height: 1.2; }
.stat-label { font-size: 12px; color: #909399; margin-top: 4px; }

/* Teams Section */
.teams-section {
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

.teams-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.team-card {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 12px;
  text-align: center;
}

.team-name { font-weight: 600; margin-bottom: 8px; }
.team-status { font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 20px; display: inline-block; margin-bottom: 8px; }
.team-status.available { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
.team-status.standby { background: rgba(230, 162, 60, 0.1); color: #E6A23C; }
.team-status.busy { background: rgba(245, 108, 108, 0.1); color: #F56C6C; }
.team-stats { font-size: 11px; color: #909399; display: flex; justify-content: center; gap: 12px; }

/* Search Bar */
.search-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.results-count { font-size: 13px; color: #909399; }

/* Buttons Grid */
.buttons-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

.button-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  border-left: 4px solid #67C23A;
}

.button-card.inactive { border-left-color: #F56C6C; }
.button-card.warning { border-left-color: #E6A23C; }

.button-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1); }

.button-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.button-id { font-family: monospace; font-weight: 600; font-size: 13px; color: #909399; }
.button-status-dot { width: 10px; height: 10px; border-radius: 50%; }

.button-name { font-size: 18px; font-weight: 600; margin-bottom: 4px; }
.button-location { font-size: 13px; color: #909399; margin-bottom: 16px; display: flex; align-items: center; gap: 4px; }

.button-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 12px 0;
  border-top: 1px solid #ebeef5;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
}

.detail-label { font-size: 10px; color: #c0c4cc; }
.detail-value { font-size: 13px; font-weight: 500; }

.button-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .teams-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .panic-button-system { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .stats-grid { grid-template-columns: 1fr; }
  .teams-grid { grid-template-columns: 1fr; }
  .buttons-grid { grid-template-columns: 1fr; }
  .alert-banner { flex-direction: column; text-align: center; }
}
</style>