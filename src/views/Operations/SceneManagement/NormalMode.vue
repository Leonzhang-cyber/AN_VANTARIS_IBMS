<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
  RefreshRight, Warning, CircleCheck, Clock,
  Monitor, Tools, Search, Setting,
  Operation, Document, Grid, List,
  Sunny, Moon, Connection, HomeFilled,
  Switch, Check, Close, Edit, Delete,
  Plus, CopyDocument, TrendCharts, DataAnalysis
} from "@element-plus/icons-vue"
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Initializing scene management...',
  'Loading normal mode configuration...',
  'Applying default settings...',
  'Ready for operation...'
]

// Scene status
const sceneStatus = ref({
  isActive: true,
  lastActivated: '2025-01-16 08:00:00',
  scheduledEnd: '2025-01-16 18:00:00',
  activeDuration: '10h 30m',
  nextScheduledScene: 'Energy Saving Mode - 18:00'
})

// Device groups and their settings in Normal Mode
const deviceGroups = ref([
  {
    id: 'hvac',
    name: 'HVAC Systems',
    icon: 'Connection',
    status: 'active',
    settings: {
      coolingSetpoint: 22,
      heatingSetpoint: 20,
      fanSpeed: 'Auto',
      freshAirDamper: 30,
      scheduleEnabled: true
    },
    devices: [
      { name: 'Chiller 1', currentValue: '22°C', status: 'running' },
      { name: 'AHU 1', currentValue: '65%', status: 'running' },
      { name: 'VAV Boxes', currentValue: '22°C avg', status: 'running' }
    ]
  },
  {
    id: 'lighting',
    name: 'Lighting Systems',
    icon: 'Sunny',
    status: 'active',
    settings: {
      brightness: 80,
      occupancySensing: true,
      daylightHarvesting: true,
      scheduleEnabled: true
    },
    devices: [
      { name: 'Office Lighting', currentValue: '80%', status: 'on' },
      { name: 'Conference Room', currentValue: '75%', status: 'on' },
      { name: 'Common Areas', currentValue: '60%', status: 'on' }
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
      accessControl: 'Normal',
      alarmMonitoring: true
    },
    devices: [
      { name: 'CCTV Cameras', currentValue: 'Recording', status: 'active' },
      { name: 'Access Control', currentValue: 'Normal Mode', status: 'active' },
      { name: 'Motion Sensors', currentValue: 'Armed', status: 'active' }
    ]
  },
  {
    id: 'blinds',
    name: 'Window Blinds',
    icon: 'Grid',
    status: 'active',
    settings: {
      position: 40,
      autoAdjust: true,
      scheduleEnabled: true,
      sunTracking: true
    },
    devices: [
      { name: 'East Blinds', currentValue: '40%', status: 'open' },
      { name: 'West Blinds', currentValue: '35%', status: 'open' },
      { name: 'South Blinds', currentValue: '45%', status: 'open' }
    ]
  },
  {
    id: 'power',
    name: 'Power Management',
    icon: 'TrendCharts',
    status: 'active',
    settings: {
      powerShedding: false,
      peakDemandControl: true,
      upsMode: 'Normal',
      generatorStandby: true
    },
    devices: [
      { name: 'UPS Systems', currentValue: 'Normal Mode', status: 'online' },
      { name: 'PDU Load', currentValue: '65%', status: 'normal' },
      { name: 'Generator', currentValue: 'Standby', status: 'ready' }
    ]
  },
  {
    id: 'comfort',
    name: 'Occupant Comfort',
    icon: 'DataAnalysis',
    status: 'active',
    settings: {
      co2Target: 450,
      humidityTarget: 50,
      airQuality: 'Good',
      occupancyOptimization: true
    },
    devices: [
      { name: 'CO2 Sensors', currentValue: '420 ppm', status: 'normal' },
      { name: 'Humidity Sensors', currentValue: '48%', status: 'normal' },
      { name: 'IAQ Monitors', currentValue: 'Good', status: 'normal' }
    ]
  }
])

// Scene transition history
const transitionHistory = ref([
  { time: '08:00:00', date: '2025-01-16', fromScene: 'Night Mode', toScene: 'Normal Mode', operator: 'Schedule' },
  { time: '18:00:00', date: '2025-01-15', fromScene: 'Normal Mode', toScene: 'Energy Saving Mode', operator: 'Schedule' },
  { time: '08:00:00', date: '2025-01-15', fromScene: 'Night Mode', toScene: 'Normal Mode', operator: 'Schedule' },
  { time: '22:00:00', date: '2025-01-14', fromScene: 'Evening Mode', toScene: 'Night Mode', operator: 'Manual' }
])

// Energy metrics for Normal Mode
const energyMetrics = ref({
  currentPower: 245,
  dailyUsage: 1850,
  monthlyAverage: 2250,
  efficiency: 89,
  savingsVsPrevious: 5.2
})

// Edit mode
const editingGroup = ref<string | null>(null)
const editSettings = ref<any>({})

const getStatusColor = (status: string) => {
  switch(status) {
    case 'inactive': return '#F56C6C'
    case 'warning': return '#E6A23C'
    case 'active': return '#67C23A'
    case 'running': return '#67C23A'
    case 'online': return '#67C23A'
    case 'normal': return '#409EFF'
    default: return '#909399'
  }
}

const getDeviceStatusIcon = (status: string) => {
  if (status === 'running' || status === 'active' || status === 'online' || status === 'on') {
    return 'success'
  }
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
      'Apply Normal Mode settings now? This will override current configuration.',
      'Apply Normal Mode',
      {
        confirmButtonText: 'Apply Now',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    ElMessage.success('Normal Mode applied successfully')
    sceneStatus.value.isActive = true
    sceneStatus.value.lastActivated = new Date().toLocaleString()
  }).catch(() => {})
}

const customizeScene = () => {
  ElMessage.info('Customization panel will open. Adjust settings for each device group.')
}

const resetToDefault = () => {
  ElMessageBox.confirm(
      'Reset all Normal Mode settings to factory defaults? This action cannot be undone.',
      'Reset to Default',
      {
        confirmButtonText: 'Reset',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    // Reset HVAC settings
    const hvacGroup = deviceGroups.value.find(g => g.id === 'hvac')
    if (hvacGroup) {
      hvacGroup.settings = {
        coolingSetpoint: 22,
        heatingSetpoint: 20,
        fanSpeed: 'Auto',
        freshAirDamper: 30,
        scheduleEnabled: true
      }
    }

    // Reset Lighting settings
    const lightingGroup = deviceGroups.value.find(g => g.id === 'lighting')
    if (lightingGroup) {
      lightingGroup.settings = {
        brightness: 80,
        occupancySensing: true,
        daylightHarvesting: true,
        scheduleEnabled: true
      }
    }

    // Reset Blinds settings
    const blindsGroup = deviceGroups.value.find(g => g.id === 'blinds')
    if (blindsGroup) {
      blindsGroup.settings = {
        position: 40,
        autoAdjust: true,
        scheduleEnabled: true,
        sunTracking: true
      }
    }

    ElMessage.success('All settings reset to default values')
  }).catch(() => {})
}

const refreshData = () => {
  ElMessage.info('Refreshing scene data...')
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
    Connection, Sunny, Monitor, Grid, TrendCharts, DataAnalysis
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
        <div class="loading-tip">Scene Management - Normal Mode</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="normal-mode">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Normal Mode</h2>
        <p class="subtitle">Standard building operation scene with optimized comfort and efficiency</p>
      </div>
      <div class="header-actions">
        <el-button type="success" @click="applySceneNow">
          <el-icon><Check /></el-icon> Apply Now
        </el-button>
        <el-button @click="customizeScene">
          <el-icon><Edit /></el-icon> Customize
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
    <div class="status-banner" :class="{ active: sceneStatus.isActive }">
      <div class="status-icon">🏢</div>
      <div class="status-info">
        <div class="status-title">Scene Status: {{ sceneStatus.isActive ? 'ACTIVE' : 'INACTIVE' }}</div>
        <div class="status-desc">Last activated: {{ sceneStatus.lastActivated }} • Expected until: {{ sceneStatus.scheduledEnd }}</div>
      </div>
      <div class="status-badge">{{ sceneStatus.activeDuration }} active</div>
    </div>

    <!-- Energy Metrics Cards -->
    <div class="metrics-grid">
      <el-card class="metric-card" shadow="hover">
        <div class="metric-content">
          <div class="metric-icon"><el-icon><TrendCharts /></el-icon></div>
          <div class="metric-info">
            <div class="metric-value">{{ energyMetrics.currentPower }} kW</div>
            <div class="metric-label">Current Power</div>
          </div>
        </div>
      </el-card>
      <el-card class="metric-card" shadow="hover">
        <div class="metric-content">
          <div class="metric-icon"><el-icon><Clock /></el-icon></div>
          <div class="metric-info">
            <div class="metric-value">{{ energyMetrics.dailyUsage }} kWh</div>
            <div class="metric-label">Today's Usage</div>
          </div>
        </div>
      </el-card>
      <el-card class="metric-card" shadow="hover">
        <div class="metric-content">
          <div class="metric-icon"><el-icon><DataAnalysis /></el-icon></div>
          <div class="metric-info">
            <div class="metric-value">{{ energyMetrics.efficiency }}%</div>
            <div class="metric-label">System Efficiency</div>
          </div>
        </div>
      </el-card>
      <el-card class="metric-card" shadow="hover">
        <div class="metric-content">
          <div class="metric-icon savings"><el-icon><TrendCharts /></el-icon></div>
          <div class="metric-info">
            <div class="metric-value savings">+{{ energyMetrics.savingsVsPrevious }}%</div>
            <div class="metric-label">vs Previous Mode</div>
          </div>
        </div>
      </el-card>
    </div>

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
            <span>{{ group.status === 'active' ? 'Active' : 'Inactive' }}</span>
          </div>
        </div>

        <!-- Settings Section -->
        <div class="settings-section">
          <div class="section-label">Current Settings</div>

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
              <el-input-number v-model="editSettings.heatingSetpoint" :min="16" :max="24" size="small" />
            </div>
            <div class="setting-item">
              <span class="setting-label">Fan Speed</span>
              <span class="setting-value">{{ group.settings.fanSpeed }}</span>
            </div>
            <div class="setting-item">
              <span class="setting-label">Fresh Air Damper</span>
              <span class="setting-value">{{ group.settings.freshAirDamper }}%</span>
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
              <el-slider v-model="editSettings.brightness" :min="0" :max="100" size="small" style="width: 120px" />
            </div>
            <div class="setting-item">
              <span class="setting-label">Occupancy Sensing</span>
              <span class="setting-value">{{ group.settings.occupancySensing ? 'Enabled' : 'Disabled' }}</span>
            </div>
            <div class="setting-item">
              <span class="setting-label">Daylight Harvesting</span>
              <span class="setting-value">{{ group.settings.daylightHarvesting ? 'Enabled' : 'Disabled' }}</span>
            </div>
          </div>

          <!-- Blinds Settings -->
          <div v-else-if="group.id === 'blinds'" class="settings-grid">
            <div class="setting-item" v-if="editingGroup !== group.id">
              <span class="setting-label">Position</span>
              <span class="setting-value">{{ group.settings.position }}%</span>
            </div>
            <div class="setting-item" v-else>
              <span class="setting-label">Position</span>
              <el-slider v-model="editSettings.position" :min="0" :max="100" size="small" style="width: 120px" />
            </div>
            <div class="setting-item">
              <span class="setting-label">Auto Adjust</span>
              <span class="setting-value">{{ group.settings.autoAdjust ? 'Enabled' : 'Disabled' }}</span>
            </div>
            <div class="setting-item">
              <span class="setting-label">Sun Tracking</span>
              <span class="setting-value">{{ group.settings.sunTracking ? 'Enabled' : 'Disabled' }}</span>
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
        <el-table-column prop="toScene" label="To Scene"align="center" />
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
.normal-mode {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
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

/* Status Banner */
.status-banner {
  background: linear-gradient(135deg, #667eea, #764ba2);
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
  background: linear-gradient(135deg, #11998e, #38ef7d);
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
  background: rgba(64, 158, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #409EFF;
}

.metric-icon.savings { background: rgba(103, 194, 58, 0.1); color: #67C23A; }

.metric-info { flex: 1; }
.metric-value { font-size: 28px; font-weight: 700; color: #303133; line-height: 1.2; }
.metric-value.savings { color: #67C23A; }
.metric-label { font-size: 13px; color: #909399; margin-top: 4px; }

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
  color: #909399;
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

/* Responsive */
@media (max-width: 1200px) {
  .metrics-grid { grid-template-columns: repeat(2, 1fr); }
  .groups-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .normal-mode { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .metrics-grid { grid-template-columns: 1fr; }
  .settings-grid { grid-template-columns: 1fr; }
  .settings-summary { grid-template-columns: 1fr; }
}
</style>