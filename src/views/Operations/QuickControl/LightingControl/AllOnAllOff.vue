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
        <div class="loading-tip">Not Developed Yet</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- All On / All Off Page Content -->
  <div v-else class="lighting-control-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>Lighting Control</h1>
        <p class="subtitle">Master control for all lighting zones - turn on/off all lights or manage individual zones</p>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="refreshData">Refresh</el-button>
        <el-button type="primary" :icon="Download" @click="exportReport">Report</el-button>
      </div>
    </div>

    <!-- Master Control Panel -->
    <div class="master-panel">
      <div class="master-title">
        <el-icon><Lightning /></el-icon>
        <span>Master Control</span>
      </div>
      <div class="master-buttons">
        <el-button size="large" type="success" :icon="Sunny" @click="allOn" :loading="masterLoading">
          <strong>ALL ON</strong>
        </el-button>
        <el-button size="large" type="danger" :icon="Remove" @click="allOff" :loading="masterLoading">
          <strong>ALL OFF</strong>
        </el-button>
      </div>
      <div class="master-stats">
        <div class="stat">
          <span class="stat-label">Zones On</span>
          <span class="stat-value">{{ zonesOn }} / {{ totalZones }}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Power Consumption</span>
          <span class="stat-value">{{ totalPower }} kW</span>
        </div>
        <div class="stat">
          <span class="stat-label">Estimated Savings</span>
          <span class="stat-value text-success">-{{ potentialSavings }}%</span>
        </div>
      </div>
    </div>

    <!-- Zone Selection Filters -->
    <div class="filters">
      <el-select v-model="buildingFilter" placeholder="Building" clearable style="width: 140px">
        <el-option label="All Buildings" value="all" />
        <el-option label="Building A" value="A" />
        <el-option label="Building B" value="B" />
        <el-option label="Data Center" value="DC" />
      </el-select>
      <el-select v-model="floorFilter" placeholder="Floor" clearable style="width: 120px">
        <el-option label="All Floors" value="all" />
        <el-option label="Floor 1" value="1" />
        <el-option label="Floor 2" value="2" />
        <el-option label="Floor 3" value="3" />
        <el-option label="Floor 4" value="4" />
      </el-select>
      <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
        <el-option label="All Status" value="all" />
        <el-option label="On" value="on" />
        <el-option label="Off" value="off" />
      </el-select>
      <el-input v-model="searchText" placeholder="Search zones..." :prefix-icon="Search" style="width: 200px" clearable />
      <el-button type="primary" :icon="Select" @click="openBatchDialog">Batch Update</el-button>
    </div>

    <!-- Batch Update Dialog -->
    <el-dialog v-model="batchDialogVisible" title="Batch Update Zones" width="400px">
      <div class="batch-dialog">
        <p>Apply to <strong>{{ filteredZones.length }}</strong> zones:</p>
        <div class="batch-action">
          <el-button type="success" size="large" @click="batchOn" style="flex:1">Turn ON</el-button>
          <el-button type="danger" size="large" @click="batchOff" style="flex:1">Turn OFF</el-button>
        </div>
        <div class="batch-warning">
          <el-alert title="This will override current status for all filtered zones" type="warning" :closable="false" />
        </div>
      </div>
      <template #footer>
        <el-button @click="batchDialogVisible = false">Cancel</el-button>
      </template>
    </el-dialog>

    <!-- Lighting Zones Grid -->
    <div class="zones-grid">
      <div v-for="zone in filteredZones" :key="zone.id" class="zone-card" :class="{ 'zone-on': zone.status === 'on', 'zone-off': zone.status === 'off' }">
        <div class="zone-header">
          <div>
            <div class="zone-name">{{ zone.name }}</div>
            <div class="zone-location">{{ zone.location }}</div>
          </div>
          <div class="zone-status">
            <div class="status-indicator" :class="zone.status"></div>
            <span class="status-text">{{ zone.status === 'on' ? 'ON' : 'OFF' }}</span>
          </div>
        </div>

        <!-- Power Info -->
        <div class="zone-power">
          <div class="power-value">{{ zone.power }} kW</div>
          <div class="power-label">Power Consumption</div>
        </div>

        <!-- Dimming Slider (for zones that support it) -->
        <div class="dimming-section" v-if="zone.hasDimming">
          <div class="dimming-label">
            <span>Dimming Level</span>
            <span class="dimming-value">{{ zone.dimLevel }}%</span>
          </div>
          <el-slider
              v-model="zone.dimLevel"
              :min="0"
              :max="100"
              :step="5"
              :disabled="zone.status === 'off'"
              @change="updateDimLevel(zone)"
          />
        </div>

        <!-- Control Buttons -->
        <div class="zone-controls">
          <el-button
              :type="zone.status === 'on' ? 'success' : 'default'"
              size="small"
              :icon="Sunny"
              @click="turnOn(zone)"
              :disabled="zone.status === 'on'"
          >
            On
          </el-button>
          <el-button
              :type="zone.status === 'off' ? 'danger' : 'default'"
              size="small"
              :icon="Remove"
              @click="turnOff(zone)"
              :disabled="zone.status === 'off'"
          >
            Off
          </el-button>
        </div>
      </div>
    </div>

    <!-- Schedule Section -->
    <div class="schedule-section">
      <div class="section-header">
        <h3><el-icon><Clock /></el-icon> Lighting Schedule</h3>
        <el-switch v-model="scheduleEnabled" active-text="Schedule Active" />
      </div>
      <el-table :data="scheduleRules" stripe size="small">
        <el-table-column prop="time" label="Time" width="100" />
        <el-table-column prop="zone" label="Zone / Area" min-width="150" />
        <el-table-column prop="action" label="Action" width="100">
          <template #default="{ row }">
            <el-tag :type="row.action === 'on' ? 'success' : 'danger'" size="small">{{ row.action.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="dimLevel" label="Dim Level" width="100" v-if="row => row.dimLevel !== undefined">
          <template #default="{ row }">
            {{ row.dimLevel || '-' }}%
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="80">
          <template #default="{ row }">
            <el-button link type="primary" :icon="Edit" @click="editSchedule(row)" />
            <el-button link type="danger" :icon="Delete" @click="deleteSchedule(row)" />
          </template>
        </el-table-column>
      </el-table>
      <el-button type="primary" link style="margin-top: 12px" @click="addSchedule">
        <el-icon><Plus /></el-icon> Add Schedule
      </el-button>
    </div>

    <!-- Activity Log -->
    <div class="log-section">
      <div class="section-header">
        <h3><el-icon><Document /></el-icon> Recent Lighting Changes</h3>
        <el-button link type="primary" size="small">View All</el-button>
      </div>
      <el-table :data="activityLog" stripe size="small">
        <el-table-column prop="time" label="Time" width="160" />
        <el-table-column prop="zone" label="Zone" min-width="140" />
        <el-table-column prop="action" label="Action" width="100" />
        <el-table-column prop="change" label="Change" min-width="100" />
        <el-table-column prop="user" label="User" width="140" />
      </el-table>
    </div>

    <!-- Confirmation Dialog for All On/Off -->
    <el-dialog v-model="confirmDialogVisible" :title="confirmAction === 'on' ? 'Turn All Lights On?' : 'Turn All Lights Off?'" width="350px" center>
      <div class="confirm-content">
        <p>This will {{ confirmAction === 'on' ? 'turn ON' : 'turn OFF' }} all lighting zones.</p>
        <p class="confirm-impact">Total zones: {{ totalZones }} | Current power: {{ totalPower }} kW</p>
      </div>
      <template #footer>
        <el-button @click="confirmDialogVisible = false">Cancel</el-button>
        <el-button :type="confirmAction === 'on' ? 'success' : 'danger'" @click="confirmAllAction">Confirm</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Refresh, Download, Lightning, Sunny, Remove, Search, Select,
  Clock, Edit, Delete, Plus, Document
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// Loading State
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const masterLoading = ref(false)
const loadingMessages = ['Preparing...', 'Loading modules...', 'Initializing...', 'Almost ready...']

// Data Models
interface LightingZone {
  id: number
  name: string
  location: string
  building: string
  floor: string
  status: 'on' | 'off'
  power: number
  hasDimming: boolean
  dimLevel: number
}

interface ScheduleRule {
  id: number
  time: string
  zone: string
  action: 'on' | 'off'
  dimLevel?: number
}

interface ActivityLog {
  id: number
  time: string
  zone: string
  action: string
  change: string
  user: string
}

// State
const buildingFilter = ref('all')
const floorFilter = ref('all')
const statusFilter = ref('all')
const searchText = ref('')
const scheduleEnabled = ref(true)
const batchDialogVisible = ref(false)
const confirmDialogVisible = ref(false)
const confirmAction = ref<'on' | 'off'>('on')

// Mock Data
const lightingZones = ref<LightingZone[]>([
  { id: 1, name: 'Open Office - North', location: 'Building A - Floor 1', building: 'A', floor: '1', status: 'on', power: 2.8, hasDimming: true, dimLevel: 80 },
  { id: 2, name: 'Open Office - South', location: 'Building A - Floor 1', building: 'A', floor: '1', status: 'on', power: 2.6, hasDimming: true, dimLevel: 75 },
  { id: 3, name: 'Executive Offices', location: 'Building A - Floor 2', building: 'A', floor: '2', status: 'on', power: 1.8, hasDimming: true, dimLevel: 70 },
  { id: 4, name: 'Conference Rooms', location: 'Building A - Floor 2', building: 'A', floor: '2', status: 'off', power: 1.2, hasDimming: true, dimLevel: 0 },
  { id: 5, name: 'Meeting Rooms', location: 'Building B - Floor 1', building: 'B', floor: '1', status: 'on', power: 1.5, hasDimming: true, dimLevel: 65 },
  { id: 6, name: 'Corridor - East', location: 'Building B - Floor 1', building: 'B', floor: '1', status: 'on', power: 0.8, hasDimming: false, dimLevel: 100 },
  { id: 7, name: 'Corridor - West', location: 'Building B - Floor 1', building: 'B', floor: '1', status: 'on', power: 0.8, hasDimming: false, dimLevel: 100 },
  { id: 8, name: 'Break Room', location: 'Building B - Floor 2', building: 'B', floor: '2', status: 'off', power: 0.6, hasDimming: true, dimLevel: 0 },
  { id: 9, name: 'Data Hall', location: 'Data Center - Ground', building: 'DC', floor: 'G', status: 'on', power: 5.2, hasDimming: false, dimLevel: 100 },
  { id: 10, name: 'Server Room', location: 'Data Center - Ground', building: 'DC', floor: 'G', status: 'on', power: 3.5, hasDimming: false, dimLevel: 100 }
])

const scheduleRules = ref<ScheduleRule[]>([
  { id: 1, time: '08:00', zone: 'All Zones', action: 'on', dimLevel: 80 },
  { id: 2, time: '12:00', zone: 'All Zones', action: 'on', dimLevel: 85 },
  { id: 3, time: '18:00', zone: 'All Zones', action: 'off' },
  { id: 4, time: '22:00', zone: 'All Zones', action: 'off' }
])

const activityLog = ref<ActivityLog[]>([
  { id: 1, time: '2025-05-29 09:15:22', zone: 'All Zones', action: 'Master Control', change: 'All ON', user: 'admin@ibms.com' },
  { id: 2, time: '2025-05-29 08:30:15', zone: 'Conference Rooms', action: 'Zone Control', change: 'OFF → ON', user: 'Schedule' },
  { id: 3, time: '2025-05-28 18:02:10', zone: 'All Zones', action: 'Schedule', change: 'All OFF', user: 'System' },
  { id: 4, time: '2025-05-28 14:20:05', zone: 'Open Office - North', action: 'Dimming', change: '65% → 80%', user: 'john.smith@ibms.com' }
])

// Computed
const totalZones = computed(() => lightingZones.value.length)
const zonesOn = computed(() => lightingZones.value.filter(z => z.status === 'on').length)
const totalPower = computed(() => lightingZones.value.reduce((sum, z) => sum + (z.status === 'on' ? z.power : 0), 0).toFixed(1))
const potentialSavings = computed(() => {
  const total = lightingZones.value.reduce((sum, z) => sum + z.power, 0)
  const current = parseFloat(totalPower.value)
  if (total === 0) return 0
  return Math.round((1 - current / total) * 100)
})

const filteredZones = computed(() => {
  let result = [...lightingZones.value]
  if (buildingFilter.value !== 'all') {
    result = result.filter(z => z.building === buildingFilter.value)
  }
  if (floorFilter.value !== 'all') {
    result = result.filter(z => z.floor === floorFilter.value)
  }
  if (statusFilter.value !== 'all') {
    result = result.filter(z => z.status === statusFilter.value)
  }
  if (searchText.value) {
    const s = searchText.value.toLowerCase()
    result = result.filter(z => z.name.toLowerCase().includes(s) || z.location.toLowerCase().includes(s))
  }
  return result
})

// Actions
const allOn = () => {
  confirmAction.value = 'on'
  confirmDialogVisible.value = true
}

const allOff = () => {
  confirmAction.value = 'off'
  confirmDialogVisible.value = true
}

const confirmAllAction = () => {
  confirmDialogVisible.value = false
  masterLoading.value = true

  setTimeout(() => {
    lightingZones.value.forEach(zone => {
      zone.status = confirmAction.value === 'on' ? 'on' : 'off'
      if (confirmAction.value === 'on' && zone.hasDimming && zone.dimLevel === 0) {
        zone.dimLevel = 70
      }
      if (confirmAction.value === 'off') {
        zone.dimLevel = 0
      }
    })

    ElMessage.success(`All lights turned ${confirmAction.value === 'on' ? 'ON' : 'OFF'}`)
    activityLog.value.unshift({
      id: Date.now(),
      time: new Date().toLocaleString(),
      zone: 'All Zones',
      action: 'Master Control',
      change: `All ${confirmAction.value === 'on' ? 'ON' : 'OFF'}`,
      user: 'Current User'
    })
    masterLoading.value = false
  }, 500)
}

const turnOn = (zone: LightingZone) => {
  zone.status = 'on'
  ElMessage.success(`${zone.name} turned ON`)
  activityLog.value.unshift({
    id: Date.now(),
    time: new Date().toLocaleString(),
    zone: zone.name,
    action: 'Zone Control',
    change: 'OFF → ON',
    user: 'Current User'
  })
}

const turnOff = (zone: LightingZone) => {
  zone.status = 'off'
  zone.dimLevel = 0
  ElMessage.success(`${zone.name} turned OFF`)
  activityLog.value.unshift({
    id: Date.now(),
    time: new Date().toLocaleString(),
    zone: zone.name,
    action: 'Zone Control',
    change: 'ON → OFF',
    user: 'Current User'
  })
}

const updateDimLevel = (zone: LightingZone) => {
  if (zone.status === 'on') {
    const powerMultiplier = zone.dimLevel / 100
    zone.power = parseFloat((zone.power / (zone.dimLevel === 0 ? 1 : (zone.dimLevel + 20) / 100) * powerMultiplier).toFixed(1))
    ElMessage.info(`${zone.name} dimming set to ${zone.dimLevel}%`)
    activityLog.value.unshift({
      id: Date.now(),
      time: new Date().toLocaleString(),
      zone: zone.name,
      action: 'Dimming',
      change: `${zone.dimLevel}%`,
      user: 'Current User'
    })
  }
}

const openBatchDialog = () => {
  batchDialogVisible.value = true
}

const batchOn = () => {
  filteredZones.value.forEach(zone => {
    zone.status = 'on'
    if (zone.hasDimming && zone.dimLevel === 0) {
      zone.dimLevel = 70
    }
  })
  ElMessage.success(`${filteredZones.value.length} zones turned ON`)
  batchDialogVisible.value = false
  activityLog.value.unshift({
    id: Date.now(),
    time: new Date().toLocaleString(),
    zone: 'Batch Update',
    action: 'Batch Control',
    change: `${filteredZones.value.length} zones → ON`,
    user: 'Current User'
  })
}

const batchOff = () => {
  filteredZones.value.forEach(zone => {
    zone.status = 'off'
    zone.dimLevel = 0
  })
  ElMessage.success(`${filteredZones.value.length} zones turned OFF`)
  batchDialogVisible.value = false
  activityLog.value.unshift({
    id: Date.now(),
    time: new Date().toLocaleString(),
    zone: 'Batch Update',
    action: 'Batch Control',
    change: `${filteredZones.value.length} zones → OFF`,
    user: 'Current User'
  })
}

const refreshData = () => {
  ElMessage.success('Data refreshed')
}

const exportReport = () => {
  ElMessage.info('Exporting lighting report...')
}

const addSchedule = () => {
  ElMessage.info('Add new schedule rule')
}

const editSchedule = (row: ScheduleRule) => {
  ElMessage.info(`Edit schedule: ${row.time}`)
}

const deleteSchedule = (row: ScheduleRule) => {
  ElMessage.info(`Delete schedule: ${row.time}`)
}

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
.lighting-control-page {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}
.header-title h1 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2f3d;
  margin: 0 0 4px 0;
}
.header-title .subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}
.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* Master Panel */
.master-panel {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 20px;
  padding: 24px 32px;
  margin-bottom: 24px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}
.master-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
}
.master-buttons {
  display: flex;
  gap: 16px;
}
.master-stats {
  display: flex;
  gap: 32px;
}
.master-stats .stat {
  text-align: center;
}
.master-stats .stat-label {
  font-size: 12px;
  opacity: 0.7;
  display: block;
  margin-bottom: 4px;
}
.master-stats .stat-value {
  font-size: 20px;
  font-weight: 700;
}
.text-success { color: #67c23a; }

/* Filters */
.filters {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 24px;
  padding: 16px;
  background: white;
  border-radius: 12px;
  align-items: center;
}

/* Zones Grid */
.zones-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}
.zone-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
  border-left: 4px solid #ddd;
}
.zone-card.zone-on { border-left-color: #67c23a; }
.zone-card.zone-off { border-left-color: #909399; }
.zone-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}
.zone-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}
.zone-name { font-size: 16px; font-weight: 600; color: #1f2f3d; }
.zone-location { font-size: 12px; color: #909399; margin-top: 2px; }
.zone-status {
  display: flex;
  align-items: center;
  gap: 6px;
}
.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.status-indicator.on { background: #67c23a; box-shadow: 0 0 6px #67c23a; }
.status-indicator.off { background: #909399; }
.status-text { font-size: 12px; font-weight: 500; }

.zone-power {
  text-align: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}
.power-value { font-size: 24px; font-weight: 700; color: #1f2f3d; }
.power-label { font-size: 11px; color: #909399; margin-top: 4px; }

.dimming-section { margin-bottom: 16px; }
.dimming-label {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #606266;
  margin-bottom: 8px;
}
.dimming-value { font-weight: 500; color: #409eff; }

.zone-controls {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 8px;
}

/* Schedule & Log Sections */
.schedule-section, .log-section {
  background: white;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1f2f3d;
}

/* Batch Dialog */
.batch-dialog {
  padding: 8px 0;
  text-align: center;
}
.batch-dialog p { margin-bottom: 20px; color: #606266; }
.batch-action {
  display: flex;
  gap: 16px;
  margin: 20px 0;
}
.batch-warning { margin-top: 16px; }

/* Confirm Dialog */
.confirm-content {
  text-align: center;
  padding: 16px 0;
}
.confirm-impact {
  font-size: 13px;
  color: #909399;
  margin-top: 12px;
}

:deep(.el-table) { border-radius: 12px; }
:deep(.el-table th) { background-color: #fafafa; font-weight: 600; }
</style>