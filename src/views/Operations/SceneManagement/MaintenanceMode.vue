<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
  RefreshRight, Warning, CircleCheck, Clock,
  Monitor, Tools, Search, Setting,
  Operation, Document, Grid, List,
  Sunny, Moon, Connection, HomeFilled,
  Switch, Check, Close, Edit, Delete,
  Plus, CopyDocument, TrendCharts, DataAnalysis,
  Lightning, Timer, Lock, User, Bell
} from "@element-plus/icons-vue"
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Initializing maintenance mode...',
  'Isolating affected systems...',
  'Applying safety protocols...',
  'Ready for operation...'
]

// Scene status
const sceneStatus = ref({
  isActive: false,
  lastActivated: '2025-01-10 09:00:00',
  scheduledStart: '09:00:00',
  scheduledEnd: '17:00:00',
  activeDuration: '8h',
  nextScheduledScene: 'Normal Mode - 17:00',
  maintenanceInProgress: false,
  currentMaintenanceTask: 'None'
})

// Maintenance metrics
const maintenanceMetrics = ref({
  activeWorkOrders: 3,
  completedToday: 2,
  pendingTasks: 5,
  estimatedCompletionTime: '4h 30m',
  affectedZones: 4,
  safetyStatus: 'All Safe'
})

// Device groups and their settings in Maintenance Mode
const deviceGroups = ref([
  {
    id: 'hvac',
    name: 'HVAC Systems',
    icon: 'Connection',
    status: 'limited',
    settings: {
      coolingSetpoint: 23,
      heatingSetpoint: 19,
      fanSpeed: 'Reduced',
      freshAirDamper: 25,
      scheduleEnabled: false,
      maintenanceBypass: true
    },
    devices: [
      { name: 'Chiller 1', currentValue: 'Maintenance Mode', status: 'bypass' },
      { name: 'AHU 1', currentValue: 'Reduced', status: 'limited' },
      { name: 'VAV Boxes', currentValue: 'Partial', status: 'limited' }
    ]
  },
  {
    id: 'lighting',
    name: 'Lighting Systems',
    icon: 'Sunny',
    status: 'limited',
    settings: {
      brightness: 60,
      occupancySensing: true,
      daylightHarvesting: true,
      scheduleEnabled: false,
      emergencyOverride: true
    },
    devices: [
      { name: 'Office Lighting', currentValue: '60%', status: 'limited' },
      { name: 'Conference Room', currentValue: '50%', status: 'limited' },
      { name: 'Work Area', currentValue: '70%', status: 'normal' }
    ]
  },
  {
    id: 'security',
    name: 'Security Systems',
    icon: 'Monitor',
    status: 'active',
    settings: {
      camerasRecording: true,
      motionDetection: true,
      accessControl: 'Maintenance Access',
      alarmMonitoring: true,
      maintenanceOverride: true
    },
    devices: [
      { name: 'CCTV Cameras', currentValue: 'Recording', status: 'active' },
      { name: 'Access Control', currentValue: 'Maintenance Mode', status: 'active' },
      { name: 'Motion Sensors', currentValue: 'Armed', status: 'active' }
    ]
  },
  {
    id: 'power',
    name: 'Power Management',
    icon: 'TrendCharts',
    status: 'limited',
    settings: {
      powerShedding: true,
      peakDemandControl: true,
      upsMode: 'Maintenance Bypass',
      generatorStandby: true,
      loadShedding: true
    },
    devices: [
      { name: 'UPS Systems', currentValue: 'Bypass Mode', status: 'maintenance' },
      { name: 'PDU Load', currentValue: 'Reduced', status: 'limited' },
      { name: 'Generator', currentValue: 'Standby', status: 'ready' }
    ]
  },
  {
    id: 'elevators',
    name: 'Elevator Systems',
    icon: 'Monitor',
    status: 'partial',
    settings: {
      elevatorOperation: 'Limited',
      serviceMode: true,
      priorityAccess: 'Maintenance',
      scheduleEnabled: false
    },
    devices: [
      { name: 'Elevator 1', currentValue: 'Service Mode', status: 'maintenance' },
      { name: 'Elevator 2', currentValue: 'Normal', status: 'active' },
      { name: 'Elevator 3', currentValue: 'Service Mode', status: 'maintenance' }
    ]
  },
  {
    id: 'access',
    name: 'Access Control',
    icon: 'Lock',
    status: 'restricted',
    settings: {
      doorAccess: 'Maintenance Only',
      timeRestrictions: true,
      emergencyAccess: true,
      visitorAccess: 'Restricted'
    },
    devices: [
      { name: 'Main Entrance', currentValue: 'Restricted', status: 'restricted' },
      { name: 'Service Entrance', currentValue: 'Open', status: 'active' },
      { name: 'Secure Areas', currentValue: 'Locked', status: 'restricted' }
    ]
  }
])

// Active maintenance tasks
const maintenanceTasks = ref([
  { id: 'MT-001', task: 'Chiller Annual Service', zone: 'Central Plant', priority: 'High', status: 'in-progress', assignedTo: 'John Zhang', startTime: '09:00', estimatedEnd: '12:00' },
  { id: 'MT-002', task: 'AHU Filter Replacement', zone: 'Data Center A', priority: 'Medium', status: 'pending', assignedTo: 'Mike Wang', startTime: '13:00', estimatedEnd: '15:00' },
  { id: 'MT-003', task: 'UPS Battery Testing', zone: 'Electrical Room', priority: 'High', status: 'in-progress', assignedTo: 'Sarah Li', startTime: '08:30', estimatedEnd: '11:30' },
  { id: 'MT-004', task: 'Lighting Control Firmware Update', zone: 'Office Areas', priority: 'Low', status: 'pending', assignedTo: 'Tom Chen', startTime: '14:00', estimatedEnd: '16:00' },
  { id: 'MT-005', task: 'Generator Load Test', zone: 'Generator Room', priority: 'Critical', status: 'scheduled', assignedTo: 'David Sun', startTime: '10:00', estimatedEnd: '12:00' }
])

// Scene transition history
const transitionHistory = ref([
  { time: '09:00:00', date: '2025-01-10', fromScene: 'Normal Mode', toScene: 'Maintenance Mode', operator: 'Admin' },
  { time: '17:00:00', date: '2025-01-09', fromScene: 'Maintenance Mode', toScene: 'Normal Mode', operator: 'Schedule' },
  { time: '09:00:00', date: '2025-01-09', fromScene: 'Normal Mode', toScene: 'Maintenance Mode', operator: 'Admin' },
  { time: '16:30:00', date: '2025-01-08', fromScene: 'Maintenance Mode', toScene: 'Energy Saving Mode', operator: 'Auto' }
])

// Safety alerts
const safetyAlerts = ref([
  { id: 'SAF-001', message: 'Electrical panel LOTO in progress - Do not enter', severity: 'critical', zone: 'Electrical Room', timestamp: '2025-01-16 09:15:00' },
  { id: 'SAF-002', message: 'Scissor lift in use - Watch for moving equipment', severity: 'warning', zone: 'Central Plant', timestamp: '2025-01-16 08:30:00' },
  { id: 'SAF-003', message: 'Floor cleaning in progress - Wet floor signs posted', severity: 'info', zone: 'Lobby', timestamp: '2025-01-16 08:00:00' }
])

// Edit mode
const editingGroup = ref<string | null>(null)
const editSettings = ref<any>({})

const getStatusColor = (status: string) => {
  switch(status) {
    case 'inactive': return '#F56C6C'
    case 'warning': return '#E6A23C'
    case 'active': return '#67C23A'
    case 'limited': return '#409EFF'
    case 'partial': return '#E6A23C'
    case 'restricted': return '#F56C6C'
    case 'bypass': return '#E6A23C'
    case 'maintenance': return '#909399'
    default: return '#909399'
  }
}

const getStatusText = (status: string) => {
  switch(status) {
    case 'limited': return 'Limited Operation'
    case 'partial': return 'Partial Service'
    case 'restricted': return 'Restricted'
    case 'bypass': return 'Bypass Mode'
    case 'maintenance': return 'Maintenance'
    case 'active': return 'Active'
    default: return status
  }
}

const getPriorityColor = (priority: string) => {
  switch(priority) {
    case 'Critical': return '#F56C6C'
    case 'High': return '#E6A23C'
    case 'Medium': return '#409EFF'
    case 'Low': return '#67C23A'
    default: return '#909399'
  }
}

const getDeviceStatusIcon = (status: string) => {
  if (status === 'active' || status === 'normal') return 'success'
  if (status === 'limited' || status === 'partial') return 'warning'
  if (status === 'maintenance' || status === 'restricted') return 'danger'
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

const applySceneNow = () => {
  ElMessageBox.confirm(
      'Activate Maintenance Mode? This will apply safety protocols and isolate affected systems.',
      'Activate Maintenance Mode',
      {
        confirmButtonText: 'Activate',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    ElMessage.success('Maintenance Mode activated - Safety protocols applied')
    sceneStatus.value.isActive = true
    sceneStatus.value.lastActivated = new Date().toLocaleString()
    sceneStatus.value.maintenanceInProgress = true
  }).catch(() => {})
}

const deactivateScene = () => {
  ElMessageBox.confirm(
      'Deactivate Maintenance Mode? Systems will return to normal operation.',
      'Deactivate Maintenance Mode',
      {
        confirmButtonText: 'Deactivate',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    ElMessage.success('Maintenance Mode deactivated - Systems restored')
    sceneStatus.value.isActive = false
    sceneStatus.value.maintenanceInProgress = false
  }).catch(() => {})
}

const scheduleScene = () => {
  ElMessageBox.prompt('Enter time for automatic activation (HH:MM 24h format)', 'Schedule Maintenance', {
    confirmButtonText: 'Schedule',
    cancelButtonText: 'Cancel',
    inputPattern: /^([0-1][0-9]|2[0-3]):[0-5][0-9]$/,
    inputErrorMessage: 'Invalid time format'
  }).then(({ value }) => {
    ElMessage.success(`Maintenance Mode scheduled for ${value} daily`)
  }).catch(() => {})
}

const resetToDefault = () => {
  ElMessageBox.confirm(
      'Reset all Maintenance Mode settings to factory defaults? This action cannot be undone.',
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
  ElMessage.info('Refreshing maintenance data...')
  setTimeout(() => {
    ElMessage.success('Data refreshed successfully')
  }, 1000)
}

const completeTask = (task: any) => {
  ElMessageBox.confirm(
      `Mark task "${task.task}" as completed?`,
      'Complete Task',
      {
        confirmButtonText: 'Complete',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    task.status = 'completed'
    ElMessage.success(`Task "${task.task}" marked as completed`)
    maintenanceMetrics.value.completedToday++
    maintenanceMetrics.value.pendingTasks--
  }).catch(() => {})
}

const acknowledgeAlert = (alert: any) => {
  const index = safetyAlerts.value.findIndex(a => a.id === alert.id)
  if (index !== -1) {
    safetyAlerts.value.splice(index, 1)
    ElMessage.success(`Alert acknowledged: ${alert.message}`)
  }
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
    Connection, Sunny, Monitor, Grid, TrendCharts, DataAnalysis, Lock
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
        <div class="loading-tip">Scene Management - Maintenance Mode</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="maintenance-mode">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Maintenance Mode</h2>
        <p class="subtitle">Safe operation during scheduled maintenance and repairs</p>
      </div>
      <div class="header-actions">
        <el-button v-if="!sceneStatus.isActive" type="warning" @click="applySceneNow">
          <el-icon><Tools /></el-icon> Activate Mode
        </el-button>
        <el-button v-else type="success" @click="deactivateScene">
          <el-icon><Check /></el-icon> Deactivate
        </el-button>
        <el-button @click="scheduleScene">
          <el-icon><Timer /></el-icon> Schedule
        </el-button>
        <el-button @click="resetToDefault">
          <el-icon><RefreshRight /></el-icon> Reset Defaults
        </el-button>
        <el-button type="primary" @click="refreshData">
          <el-icon><RefreshRight /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- Scene Status Banner -->
    <div class="status-banner" :class="{ active: sceneStatus.isActive, warning: sceneStatus.isActive }">
      <div class="status-icon">🔧</div>
      <div class="status-info">
        <div class="status-title">Maintenance Mode: {{ sceneStatus.isActive ? 'ACTIVE' : 'INACTIVE' }}</div>
        <div class="status-desc" v-if="sceneStatus.isActive">
          Last activated: {{ sceneStatus.lastActivated }} • Expected until: {{ sceneStatus.scheduledEnd }}
        </div>
        <div class="status-desc" v-else>
          Scheduled: {{ sceneStatus.scheduledStart }} - {{ sceneStatus.scheduledEnd }}
        </div>
      </div>
      <div class="status-badge">{{ sceneStatus.activeDuration }} window</div>
    </div>

    <!-- Maintenance Metrics Cards -->
    <div class="metrics-grid">
      <el-card class="metric-card" shadow="hover">
        <div class="metric-content">
          <div class="metric-icon workorders"><el-icon><Tools /></el-icon></div>
          <div class="metric-info">
            <div class="metric-value">{{ maintenanceMetrics.activeWorkOrders }}</div>
            <div class="metric-label">Active Work Orders</div>
          </div>
        </div>
      </el-card>
      <el-card class="metric-card" shadow="hover">
        <div class="metric-content">
          <div class="metric-icon completed"><el-icon><CircleCheck /></el-icon></div>
          <div class="metric-info">
            <div class="metric-value">{{ maintenanceMetrics.completedToday }}</div>
            <div class="metric-label">Completed Today</div>
          </div>
        </div>
      </el-card>
      <el-card class="metric-card" shadow="hover">
        <div class="metric-content">
          <div class="metric-icon pending"><el-icon><Clock /></el-icon></div>
          <div class="metric-info">
            <div class="metric-value">{{ maintenanceMetrics.pendingTasks }}</div>
            <div class="metric-label">Pending Tasks</div>
          </div>
        </div>
      </el-card>
      <el-card class="metric-card" shadow="hover">
        <div class="metric-content">
          <div class="metric-icon safety"><el-icon><CircleCheck /></el-icon></div>
          <div class="metric-info">
            <div class="metric-value">{{ maintenanceMetrics.safetyStatus }}</div>
            <div class="metric-label">Safety Status</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Safety Alerts -->
    <div v-if="safetyAlerts.length > 0" class="alerts-section">
      <div class="section-header">
        <span><el-icon><Bell /></el-icon> Safety Alerts</span>
        <el-tag type="danger" size="small">{{ safetyAlerts.length }} Active</el-tag>
      </div>
      <div class="alerts-list">
        <div v-for="alert in safetyAlerts" :key="alert.id" class="alert-item" :class="alert.severity">
          <div class="alert-icon">
            <span v-if="alert.severity === 'critical'">🚨</span>
            <span v-else-if="alert.severity === 'warning'">⚠️</span>
            <span v-else>ℹ️</span>
          </div>
          <div class="alert-content">
            <div class="alert-message">{{ alert.message }}</div>
            <div class="alert-meta">{{ alert.zone }} • {{ alert.timestamp }}</div>
          </div>
          <el-button size="small" type="primary" plain @click="acknowledgeAlert(alert)">Acknowledge</el-button>
        </div>
      </div>
    </div>

    <!-- Active Maintenance Tasks -->
    <el-card class="tasks-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Active Maintenance Tasks</span>
          <el-tag type="warning" size="small">{{ maintenanceTasks.filter(t => t.status === 'in-progress').length }} In Progress</el-tag>
        </div>
      </template>
      <el-table :data="maintenanceTasks" stripe>
        <el-table-column prop="id" label="Task ID" align="center" />
        <el-table-column prop="task" label="Task" align="center" />
        <el-table-column prop="zone" label="Zone" align="center" />
        <el-table-column label="Priority" align="center">
          <template #default="{ row }">
            <el-tag :type="row.priority === 'Critical' ? 'danger' : row.priority === 'High' ? 'warning' : row.priority === 'Medium' ? 'primary' : 'info'" size="small">
              {{ row.priority }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Status" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : row.status === 'in-progress' ? 'warning' : 'info'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assignedTo" label="Assigned To" align="center" />
        <el-table-column prop="estimatedEnd" label="Est. End" align="center" />
        <el-table-column label="Actions" align="center">
          <template #default="{ row }">
            <el-button v-if="row.status !== 'completed'" type="success" link size="small" @click="completeTask(row)">Complete</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Device Groups Grid -->
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
          <div class="section-label">Maintenance Settings</div>

          <!-- HVAC Settings -->
          <div v-if="group.id === 'hvac'" class="settings-grid">
            <div class="setting-item" v-if="editingGroup !== group.id">
              <span class="setting-label">Cooling Setpoint</span>
              <span class="setting-value">{{ group.settings.coolingSetpoint }}°C</span>
            </div>
            <div class="setting-item" v-else>
              <span class="setting-label">Cooling Setpoint</span>
              <el-input-number v-model="editSettings.coolingSetpoint" :min="18" :max="26" size="small" />
            </div>
            <div class="setting-item" v-if="editingGroup !== group.id">
              <span class="setting-label">Heating Setpoint</span>
              <span class="setting-value">{{ group.settings.heatingSetpoint }}°C</span>
            </div>
            <div class="setting-item" v-else>
              <span class="setting-label">Heating Setpoint</span>
              <el-input-number v-model="editSettings.heatingSetpoint" :min="16" :max="22" size="small" />
            </div>
            <div class="setting-item">
              <span class="setting-label">Maintenance Bypass</span>
              <span class="setting-value">{{ group.settings.maintenanceBypass ? 'Enabled' : 'Disabled' }}</span>
            </div>
          </div>

          <!-- Lighting Settings -->
          <div v-else-if="group.id === 'lighting'" class="settings-grid">
            <div class="setting-item" v-if="editingGroup !== group.id">
              <span class="setting-label">Brightness</span>
              <span class="setting-value">{{ group.settings.brightness }}%</span>
            </div>
            <div class="setting-item" v-else>
              <span class="setting-label">Brightness</span>
              <el-slider v-model="editSettings.brightness" :min="30" :max="100" size="small" style="width: 120px" />
            </div>
            <div class="setting-item">
              <span class="setting-label">Emergency Override</span>
              <span class="setting-value">{{ group.settings.emergencyOverride ? 'Enabled' : 'Disabled' }}</span>
            </div>
          </div>

          <!-- Access Control Settings -->
          <div v-else-if="group.id === 'access'" class="settings-grid">
            <div class="setting-item">
              <span class="setting-label">Door Access</span>
              <span class="setting-value">{{ group.settings.doorAccess }}</span>
            </div>
            <div class="setting-item">
              <span class="setting-label">Visitor Access</span>
              <span class="setting-value">{{ group.settings.visitorAccess }}</span>
            </div>
          </div>

          <!-- Other groups summary -->
          <div v-else class="settings-summary">
            <div class="setting-item" v-for="(value, key) in group.settings" :key="key">
              <span class="setting-label">{{ key.replace(/([A-Z])/g, ' $1').trim() }}</span>
              <span class="setting-value">{{ value === true ? 'Enabled' : value === false ? 'Disabled' : value }}</span>
            </div>
          </div>
        </div>

        <!-- Devices Preview -->
        <div class="devices-preview">
          <div class="section-label">Connected Devices</div>
          <div class="devices-list">
            <div v-for="device in group.devices" :key="device.name" class="device-item">
              <span class="device-name">{{ device.name }}</span>
              <span class="device-value">{{ device.currentValue }}</span>
              <el-tag :type="getDeviceStatusIcon(device.status)" size="small">{{ device.status }}</el-tag>
            </div>
          </div>
        </div>

        <!-- Edit Actions -->
        <div class="group-actions">
          <el-button v-if="editingGroup !== group.id" size="small" @click="startEdit(group)">
            <el-icon><Edit /></el-icon> Edit
          </el-button>
          <template v-else>
            <el-button size="small" type="success" @click="saveSettings(group)">
              <el-icon><Check /></el-icon> Save
            </el-button>
            <el-button size="small" @click="cancelEdit">
              <el-icon><Close /></el-icon> Cancel
            </el-button>
          </template>
        </div>
      </div>
    </div>

    <!-- Transition History -->
    <el-card class="history-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Scene Transition History</span>
          <el-tag type="info" size="small">Last 4 transitions</el-tag>
        </div>
      </template>
      <el-table :data="transitionHistory" stripe>
        <el-table-column prop="date" label="Date" align="center" />
        <el-table-column prop="time" label="Time" align="center" />
        <el-table-column prop="fromScene" label="From Scene" align="center" />
        <el-table-column prop="toScene" label="To Scene" align="center" />
        <el-table-column prop="operator" label="Operator" align="center" />
      </el-table>
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
.maintenance-mode {
  padding: 24px;
  background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%);
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
  background: linear-gradient(135deg, #e65100, #ff9800);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  margin: 0;
  color: #ef6c00;
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
  background: linear-gradient(135deg, #e65100, #ff9800);
  border-radius: 20px;
  padding: 20px 24px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  color: white;
  flex-wrap: wrap;
}

.status-banner.active {
  animation: pulse-orange 2s infinite;
}

@keyframes pulse-orange {
  0%, 100% { box-shadow: 0 0 0 0 rgba(230, 81, 0, 0.4); }
  50% { box-shadow: 0 0 0 20px rgba(230, 81, 0, 0); }
}

.status-icon { font-size: 48px; }
.status-info { flex: 1; }
.status-title { font-weight: 700; font-size: 20px; margin-bottom: 4px; }
.status-desc { font-size: 13px; opacity: 0.9; }
.status-badge { padding: 6px 16px; background: rgba(255,255,255,0.2); border-radius: 20px; font-size: 13px; font-weight: 500; }

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

.metric-icon.workorders { background: rgba(33, 150, 243, 0.1); color: #2196F3; }
.metric-icon.completed { background: rgba(76, 175, 80, 0.1); color: #4CAF50; }
.metric-icon.pending { background: rgba(255, 152, 0, 0.1); color: #FF9800; }
.metric-icon.safety { background: rgba(76, 175, 80, 0.1); color: #4CAF50; }

.metric-info { flex: 1; }
.metric-value { font-size: 28px; font-weight: 700; color: #303133; line-height: 1.2; }
.metric-label { font-size: 13px; color: #909399; margin-top: 4px; }

/* Alerts Section */
.alerts-section {
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

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  border-radius: 12px;
  background: #f8f9fa;
}

.alert-item.critical { border-left: 4px solid #F56C6C; }
.alert-item.warning { border-left: 4px solid #E6A23C; }
.alert-item.info { border-left: 4px solid #409EFF; }

.alert-icon { font-size: 24px; }
.alert-content { flex: 1; }
.alert-message { font-weight: 500; margin-bottom: 4px; }
.alert-meta { font-size: 11px; color: #909399; }

/* Tasks Card */
.tasks-card {
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
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
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
  color: #FF9800;
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

.settings-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-bottom: 16px;
}

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

.group-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

/* History Card */
.history-card {
  border-radius: 20px;
}

/* Responsive */
@media (max-width: 1200px) {
  .metrics-grid { grid-template-columns: repeat(2, 1fr); }
  .groups-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .maintenance-mode { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .metrics-grid { grid-template-columns: 1fr; }
  .settings-grid { grid-template-columns: 1fr; }
  .alert-item { flex-direction: column; text-align: center; }
}
</style>