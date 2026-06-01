<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
  RefreshRight, Warning, CircleCheck, Clock,
  Monitor, Tools, Search, Setting,
  Operation, Document, Grid, List,
  Sunny, Moon, Connection, HomeFilled,
  Switch, Check, Close, Edit, Delete,
  Plus, CopyDocument, TrendCharts, DataAnalysis,
  Lightning, Money, Timer
} from "@element-plus/icons-vue"
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
'Initializing energy saving mode...',
'Loading optimization settings...',
'Applying efficiency parameters...',
'Ready for operation...'
]

// Scene status
const sceneStatus = ref({
isActive: false,
lastActivated: '2025-01-15 18:00:00',
scheduledStart: '18:00:00',
scheduledEnd: '06:00:00',
activeDuration: '12h',
nextScheduledScene: 'Normal Mode - 06:00'
})

// Energy savings metrics
const energyMetrics = ref({
currentPower: 168,
powerReduction: 31.4,
dailySaving: 425,
monthlyProjectedSaving: 12750,
co2Reduction: 285,
efficiencyGain: 18.5
})

// Device groups and their settings in Energy Saving Mode
const deviceGroups = ref([
{
id: 'hvac',
name: 'HVAC Systems',
icon: 'Connection',
status: 'optimized',
settings: {
coolingSetpoint: 24,
heatingSetpoint: 18,
fanSpeed: 'Low',
freshAirDamper: 15,
scheduleEnabled: true,
nightPurge: true
},
devices: [
{ name: 'Chiller 1', currentValue: 'Limited', status: 'eco' },
{ name: 'AHU 1', currentValue: '50%', status: 'eco' },
{ name: 'VAV Boxes', currentValue: 'Minimum', status: 'eco' }
]
},
{
id: 'lighting',
name: 'Lighting Systems',
icon: 'Sunny',
status: 'optimized',
settings: {
brightness: 40,
occupancySensing: true,
daylightHarvesting: true,
scheduleEnabled: true,
taskLightingOnly: true
},
devices: [
{ name: 'Office Lighting', currentValue: '40%', status: 'dimmed' },
{ name: 'Conference Room', currentValue: '30%', status: 'dimmed' },
{ name: 'Common Areas', currentValue: '25%', status: 'dimmed' }
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
status: 'optimized',
settings: {
position: 85,
autoAdjust: true,
scheduleEnabled: true,
sunTracking: true,
nightClosure: true
},
devices: [
{ name: 'East Blinds', currentValue: '85%', status: 'closed' },
{ name: 'West Blinds', currentValue: '90%', status: 'closed' },
{ name: 'South Blinds', currentValue: '80%', status: 'closed' }
]
},
{
id: 'power',
name: 'Power Management',
icon: 'TrendCharts',
status: 'optimized',
settings: {
powerShedding: true,
peakDemandControl: true,
upsMode: 'Eco',
generatorStandby: true,
equipmentPowerDown: true
},
devices: [
{ name: 'UPS Systems', currentValue: 'Eco Mode', status: 'eco' },
{ name: 'PDU Load', currentValue: '52%', status: 'reduced' },
{ name: 'Generator', currentValue: 'Standby', status: 'ready' }
]
},
{
id: 'comfort',
name: 'Occupant Comfort',
icon: 'DataAnalysis',
status: 'optimized',
settings: {
co2Target: 500,
humidityTarget: 45,
airQuality: 'Acceptable',
occupancyOptimization: true
},
devices: [
{ name: 'CO2 Sensors', currentValue: '450 ppm', status: 'normal' },
{ name: 'Humidity Sensors', currentValue: '45%', status: 'normal' },
{ name: 'IAQ Monitors', currentValue: 'Good', status: 'normal' }
]
}
])

// Comparison with Normal Mode
const comparisonData = ref([
{ parameter: 'Power Consumption', normal: 245, energySaving: 168, reduction: '31%' },
{ parameter: 'Lighting Usage', normal: 80, energySaving: 40, reduction: '50%' },
{ parameter: 'HVAC Load', normal: 75, energySaving: 55, reduction: '27%' },
{ parameter: 'CO2 Emissions', normal: 320, energySaving: 235, reduction: '27%' }
])

// Scene transition history
const transitionHistory = ref([
{ time: '18:00:00', date: '2025-01-15', fromScene: 'Normal Mode', toScene: 'Energy Saving Mode', operator: 'Schedule' },
{ time: '06:00:00', date: '2025-01-16', fromScene: 'Energy Saving Mode', toScene: 'Normal Mode', operator: 'Schedule' },
{ time: '18:00:00', date: '2025-01-14', fromScene: 'Normal Mode', toScene: 'Energy Saving Mode', operator: 'Schedule' },
{ time: '22:00:00', date: '2025-01-13', fromScene: 'Evening Mode', toScene: 'Night Mode', operator: 'Manual' }
])

// Edit mode
const editingGroup = ref<string | null>(null)
const editSettings = ref<any>({})

  const getStatusColor = (status: string) => {
  switch(status) {
  case 'inactive': return '#F56C6C'
  case 'warning': return '#E6A23C'
  case 'active': return '#67C23A'
  case 'optimized': return '#409EFF'
  case 'eco': return '#67C23A'
  case 'dimmed': return '#E6A23C'
  case 'reduced': return '#409EFF'
  default: return '#909399'
  }
  }

  const getStatusText = (status: string) => {
  switch(status) {
  case 'optimized': return 'Optimized'
  case 'eco': return 'Eco Mode'
  case 'dimmed': return 'Dimmed'
  case 'reduced': return 'Reduced'
  case 'active': return 'Active'
  default: return status
  }
  }

  const getDeviceStatusIcon = (status: string) => {
  if (status === 'active' || status === 'eco') return 'success'
  if (status === 'dimmed' || status === 'reduced') return 'warning'
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
  'Apply Energy Saving Mode now? This will reduce energy consumption across the building.',
  'Apply Energy Saving Mode',
  {
  confirmButtonText: 'Apply Now',
  cancelButtonText: 'Cancel',
  type: 'info'
  }
  ).then(() => {
  ElMessage.success('Energy Saving Mode applied successfully')
  sceneStatus.value.isActive = true
  sceneStatus.value.lastActivated = new Date().toLocaleString()
  }).catch(() => {})
  }

  const scheduleScene = () => {
  ElMessageBox.prompt('Enter time for automatic activation (HH:MM 24h format)', 'Schedule Scene', {
  confirmButtonText: 'Schedule',
  cancelButtonText: 'Cancel',
  inputPattern: /^([0-1][0-9]|2[0-3]):[0-5][0-9]$/,
  inputErrorMessage: 'Invalid time format'
  }).then(({ value }) => {
  ElMessage.success(`Energy Saving Mode scheduled for ${value} daily`)
  }).catch(() => {})
  }

  const resetToDefault = () => {
  ElMessageBox.confirm(
  'Reset all Energy Saving Mode settings to factory defaults? This action cannot be undone.',
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
  coolingSetpoint: 24,
  heatingSetpoint: 18,
  fanSpeed: 'Low',
  freshAirDamper: 15,
  scheduleEnabled: true,
  nightPurge: true
  }
  }

  // Reset Lighting settings
  const lightingGroup = deviceGroups.value.find(g => g.id === 'lighting')
  if (lightingGroup) {
  lightingGroup.settings = {
  brightness: 40,
  occupancySensing: true,
  daylightHarvesting: true,
  scheduleEnabled: true,
  taskLightingOnly: true
  }
  }

  // Reset Blinds settings
  const blindsGroup = deviceGroups.value.find(g => g.id === 'blinds')
  if (blindsGroup) {
  blindsGroup.settings = {
  position: 85,
  autoAdjust: true,
  scheduleEnabled: true,
  sunTracking: true,
  nightClosure: true
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
          <div class="loading-tip">Scene Management - Energy Saving Mode</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="energy-saving-mode">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h2>Energy Saving Mode</h2>
          <p class="subtitle">Optimized building operation for maximum energy efficiency</p>
        </div>
        <div class="header-actions">
          <el-button type="success" @click="applySceneNow">
            <el-icon><Lightning /></el-icon> Apply Now
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
      <div class="status-banner" :class="{ active: sceneStatus.isActive }">
        <div class="status-icon">🌿</div>
        <div class="status-info">
          <div class="status-title">Scene Status: {{ sceneStatus.isActive ? 'ACTIVE' : 'INACTIVE' }}</div>
          <div class="status-desc">Last activated: {{ sceneStatus.lastActivated }} • Scheduled: {{ sceneStatus.scheduledStart }} - {{ sceneStatus.scheduledEnd }}</div>
        </div>
        <div class="status-badge">{{ sceneStatus.activeDuration }} cycle</div>
      </div>

      <!-- Energy Savings Metrics Cards -->
      <div class="metrics-grid">
        <el-card class="metric-card" shadow="hover">
          <div class="metric-content">
            <div class="metric-icon power"><el-icon><Lightning /></el-icon></div>
            <div class="metric-info">
              <div class="metric-value">{{ energyMetrics.currentPower }} kW</div>
              <div class="metric-label">Current Power</div>
              <div class="metric-trend down">-{{ energyMetrics.powerReduction }}% vs Normal</div>
            </div>
          </div>
        </el-card>
        <el-card class="metric-card" shadow="hover">
          <div class="metric-content">
            <div class="metric-icon saving"><el-icon><Money /></el-icon></div>
            <div class="metric-info">
              <div class="metric-value">${{ energyMetrics.dailySaving }}</div>
              <div class="metric-label">Daily Savings</div>
              <div class="metric-trend down">${{ energyMetrics.monthlyProjectedSaving }}/month</div>
            </div>
          </div>
        </el-card>
        <el-card class="metric-card" shadow="hover">
          <div class="metric-content">
            <div class="metric-icon co2"><el-icon><CircleCheck /></el-icon></div>
            <div class="metric-info">
              <div class="metric-value">{{ energyMetrics.co2Reduction }} kg</div>
              <div class="metric-label">CO₂ Reduction</div>
              <div class="metric-trend down">Today</div>
            </div>
          </div>
        </el-card>
        <el-card class="metric-card" shadow="hover">
          <div class="metric-content">
            <div class="metric-icon efficiency"><el-icon><TrendCharts /></el-icon></div>
            <div class="metric-info">
              <div class="metric-value">+{{ energyMetrics.efficiencyGain }}%</div>
              <div class="metric-label">Efficiency Gain</div>
              <div class="metric-trend up">vs Normal Mode</div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- Comparison Chart -->
      <el-card class="comparison-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Energy Consumption Comparison</span>
            <el-tag type="success" size="small">Normal vs Energy Saving</el-tag>
          </div>
        </template>
        <div class="comparison-grid">
          <div v-for="item in comparisonData" :key="item.parameter" class="comparison-item">
            <div class="comparison-label">{{ item.parameter }}</div>
            <div class="comparison-bars">
              <div class="bar-container">
                <div class="bar-label normal">Normal</div>
                <div class="bar normal-bar" :style="{ width: (item.normal / 250 * 100) + '%' }">
                  <span>{{ item.normal }}</span>
                </div>
              </div>
              <div class="bar-container">
                <div class="bar-label saving">Energy Saving</div>
                <div class="bar saving-bar" :style="{ width: (item.energySaving / 250 * 100) + '%' }">
                  <span>{{ item.energySaving }}</span>
                </div>
              </div>
            </div>
            <div class="comparison-reduction">
              <el-tag type="success" size="small">-{{ item.reduction }}</el-tag>
            </div>
          </div>
        </div>
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
            <div class="section-label">Energy Saving Settings</div>

            <!-- HVAC Settings -->
            <div v-if="group.id === 'hvac'" class="settings-grid">
              <div class="setting-item" v-if="editingGroup !== group.id">
                <span class="setting-label">Cooling Setpoint</span>
                <span class="setting-value">{{ group.settings.coolingSetpoint }}°C</span>
              </div>
              <div class="setting-item" v-else>
                <span class="setting-label">Cooling Setpoint</span>
                <el-input-number v-model="editSettings.coolingSetpoint" :min="20" :max="28" size="small" />
              </div>
              <div class="setting-item" v-if="editingGroup !== group.id">
                <span class="setting-label">Heating Setpoint</span>
                <span class="setting-value">{{ group.settings.heatingSetpoint }}°C</span>
              </div>
              <div class="setting-item" v-else>
                <span class="setting-label">Heating Setpoint</span>
                <el-input-number v-model="editSettings.heatingSetpoint" :min="14" :max="22" size="small" />
              </div>
              <div class="setting-item">
                <span class="setting-label">Fan Speed</span>
                <span class="setting-value">{{ group.settings.fanSpeed }}</span>
              </div>
              <div class="setting-item">
                <span class="setting-label">Fresh Air Damper</span>
                <span class="setting-value">{{ group.settings.freshAirDamper }}%</span>
              </div>
              <div class="setting-item">
                <span class="setting-label">Night Purge</span>
                <span class="setting-value">{{ group.settings.nightPurge ? 'Enabled' : 'Disabled' }}</span>
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
                <el-slider v-model="editSettings.brightness" :min="10" :max="70" size="small" style="width: 120px" />
              </div>
              <div class="setting-item">
                <span class="setting-label">Occupancy Sensing</span>
                <span class="setting-value">{{ group.settings.occupancySensing ? 'Enabled' : 'Disabled' }}</span>
              </div>
              <div class="setting-item">
                <span class="setting-label">Task Lighting Only</span>
                <span class="setting-value">{{ group.settings.taskLightingOnly ? 'Enabled' : 'Disabled' }}</span>
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
                <el-slider v-model="editSettings.position" :min="50" :max="100" size="small" style="width: 120px" />
              </div>
              <div class="setting-item">
                <span class="setting-label">Night Closure</span>
                <span class="setting-value">{{ group.settings.nightClosure ? 'Enabled' : 'Disabled' }}</span>
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
          <el-table-column prop="toScene" label="To Scene" align="center" />
          <el-table-column prop="operator" label="Operator" align="center" />
        </el-table>
      </el-card>

      <!-- Energy Tips -->
      <el-card class="tips-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Energy Saving Tips</span>
            <el-tag type="success" size="small">Recommendations</el-tag>
          </div>
        </template>
        <div class="tips-grid">
          <div class="tip-item">
            <div class="tip-icon">💡</div>
            <div class="tip-content">
              <h4>Optimize Setpoints</h4>
              <p>Increase cooling setpoint by 2°C and decrease heating setpoint by 2°C to save up to 15% on HVAC energy.</p>
            </div>
          </div>
          <div class="tip-item">
            <div class="tip-icon">🪟</div>
            <div class="tip-content">
              <h4>Use Natural Light</h4>
              <p>Enable daylight harvesting sensors to automatically dim lights when sufficient natural light is available.</p>
            </div>
          </div>
          <div class="tip-item">
            <div class="tip-icon">⏰</div>
            <div class="tip-content">
              <h4>Schedule Equipment</h4>
              <p>Schedule non-critical equipment to power down during unoccupied hours for maximum savings.</p>
            </div>
          </div>
          <div class="tip-item">
            <div class="tip-icon">📊</div>
            <div class="tip-content">
              <h4>Monitor Performance</h4>
              <p>Review energy analytics weekly to identify additional optimization opportunities.</p>
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
    .energy-saving-mode {
      padding: 24px;
      background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
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
      background: linear-gradient(135deg, #2e7d32, #43a047);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .subtitle {
      margin: 0;
      color: #558b2f;
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
      background: linear-gradient(135deg, #2e7d32, #43a047);
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
      animation: pulse-green 2s infinite;
    }

    @keyframes pulse-green {
      0%, 100% { box-shadow: 0 0 0 0 rgba(46, 125, 50, 0.4); }
      50% { box-shadow: 0 0 0 20px rgba(46, 125, 50, 0); }
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

    .metric-icon.power { background: rgba(33, 150, 243, 0.1); color: #2196F3; }
    .metric-icon.saving { background: rgba(76, 175, 80, 0.1); color: #4CAF50; }
    .metric-icon.co2 { background: rgba(156, 39, 176, 0.1); color: #9C27B0; }
    .metric-icon.efficiency { background: rgba(255, 152, 0, 0.1); color: #FF9800; }

    .metric-info { flex: 1; }
    .metric-value { font-size: 28px; font-weight: 700; color: #303133; line-height: 1.2; }
    .metric-label { font-size: 13px; color: #909399; margin-top: 4px; }
    .metric-trend { font-size: 11px; margin-top: 4px; }
    .metric-trend.down { color: #4CAF50; }
    .metric-trend.up { color: #FF9800; }

    /* Comparison Card */
    .comparison-card {
      border-radius: 20px;
      margin-bottom: 24px;
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 600;
    }

    .comparison-card :deep(.el-card__body) { padding: 20px; }

    .comparison-grid {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .comparison-item {
      display: flex;
      align-items: center;
      gap: 20px;
      flex-wrap: wrap;
    }

    .comparison-label {
      width: 140px;
      font-weight: 600;
      font-size: 14px;
    }

    .comparison-bars {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .bar-container {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .bar-label {
      width: 80px;
      font-size: 12px;
    }

    .bar-label.normal { color: #909399; }
    .bar-label.saving { color: #4CAF50; }

    .bar {
      height: 28px;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: flex-end;
      padding-right: 10px;
      font-size: 12px;
      font-weight: 500;
      color: white;
    }

    .normal-bar { background: #c0c4cc; }
    .saving-bar { background: #4CAF50; }

    .comparison-reduction { min-width: 80px; text-align: right; }

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
      color: #4CAF50;
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
      margin-bottom: 24px;
    }

    /* Tips Card */
    .tips-card {
      border-radius: 20px;
    }

    .tips-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 20px;
    }

    .tip-item {
      display: flex;
      gap: 16px;
      padding: 12px;
      background: #f8f9fa;
      border-radius: 12px;
    }

    .tip-icon { font-size: 32px; }
    .tip-content h4 { margin: 0 0 4px 0; font-size: 14px; font-weight: 600; }
    .tip-content p { margin: 0; font-size: 12px; color: #909399; line-height: 1.4; }

    /* Responsive */
    @media (max-width: 1200px) {
      .metrics-grid { grid-template-columns: repeat(2, 1fr); }
      .groups-grid { grid-template-columns: 1fr; }
      .tips-grid { grid-template-columns: 1fr; }
    }

    @media (max-width: 768px) {
      .energy-saving-mode { padding: 16px; }
      .page-header { flex-direction: column; align-items: stretch; }
      .header-actions { flex-direction: column; }
      .header-actions .el-button { width: 100%; }
      .metrics-grid { grid-template-columns: 1fr; }
      .settings-grid { grid-template-columns: 1fr; }
      .comparison-item { flex-direction: column; align-items: flex-start; }
      .comparison-bars { width: 100%; }
    }
  </style>