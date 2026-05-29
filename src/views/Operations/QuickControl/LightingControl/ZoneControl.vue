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

  <!-- Zone Control Page Content -->
  <div v-else class="zone-control-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>Zone Control</h1>
        <p class="subtitle">Independent control of individual lighting zones with dimming and scheduling capabilities</p>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="refreshData">Refresh</el-button>
        <el-button type="primary" :icon="Download" @click="exportReport">Report</el-button>
        <el-button :icon="Setting" @click="openSettings">Settings</el-button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon"><el-icon><Lightning /></el-icon></div>
        <div class="stat-info">
          <div class="stat-number">{{ totalZones }}</div>
          <div class="stat-label">Total Zones</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><el-icon><Sunny /></el-icon></div>
        <div class="stat-info">
          <div class="stat-number">{{ zonesOn }}</div>
          <div class="stat-label">Zones On</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><el-icon><TrendCharts /></el-icon></div>
        <div class="stat-info">
          <div class="stat-number">{{ totalPower }}<span style="font-size:14px"> kW</span></div>
          <div class="stat-label">Power Consumption</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><el-icon><Timer /></el-icon></div>
        <div class="stat-info">
          <div class="stat-number">{{ avgDimLevel }}%</div>
          <div class="stat-label">Avg Dim Level</div>
        </div>
      </div>
    </div>

    <!-- Filters -->
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
    </div>

    <!-- Zones Grid -->
    <div class="zones-grid">
      <div v-for="zone in filteredZones" :key="zone.id" class="zone-card" :class="{ 'zone-on': zone.status === 'on', 'zone-off': zone.status === 'off' }">
        <!-- Zone Header -->
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

        <!-- Power and Dimming Info -->
        <div class="zone-info">
          <div class="info-item">
            <span class="info-label">Power</span>
            <span class="info-value">{{ zone.power }} kW</span>
          </div>
          <div class="info-item">
            <span class="info-label">Dimming</span>
            <span class="info-value" :class="zone.hasDimming ? 'text-success' : 'text-muted'">
              {{ zone.hasDimming ? 'Supported' : 'Not Supported' }}
            </span>
          </div>
        </div>

        <!-- On/Off Buttons -->
        <div class="control-buttons">
          <el-button
              type="success"
              size="small"
              :icon="Sunny"
              @click="turnOn(zone)"
              :disabled="zone.status === 'on'"
              :loading="zone.loading"
          >
            Turn On
          </el-button>
          <el-button
              type="danger"
              size="small"
              :icon="Remove"
              @click="turnOff(zone)"
              :disabled="zone.status === 'off'"
              :loading="zone.loading"
          >
            Turn Off
          </el-button>
        </div>

        <!-- Dimming Slider (only for zones with dimming support) -->
        <div class="dimming-section" v-if="zone.hasDimming">
          <div class="dimming-header">
            <span class="dimming-label">Dimming Level</span>
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
          <div class="preset-buttons" v-if="zone.status === 'on'">
            <el-button size="small" @click="setPresetDim(zone, 20)">20%</el-button>
            <el-button size="small" @click="setPresetDim(zone, 40)">40%</el-button>
            <el-button size="small" @click="setPresetDim(zone, 60)">60%</el-button>
            <el-button size="small" @click="setPresetDim(zone, 80)">80%</el-button>
            <el-button size="small" @click="setPresetDim(zone, 100)">100%</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- No Results -->
    <div v-if="filteredZones.length === 0" class="empty-state">
      <el-empty description="No lighting zones found matching your filters" />
    </div>

    <!-- Zone Schedule Section -->
    <div class="schedule-section">
      <div class="section-header">
        <h3><el-icon><Clock /></el-icon> Zone Schedules</h3>
        <el-button type="primary" link @click="addSchedule">
          <el-icon><Plus /></el-icon> Add Schedule
        </el-button>
      </div>
      <el-table :data="zoneSchedules" stripe size="small">
        <el-table-column prop="time" label="Time" width="100" />
        <el-table-column prop="zone" label="Zone" min-width="160" />
        <el-table-column prop="action" label="Action" width="80">
          <template #default="{ row }">
            <el-tag :type="row.action === 'on' ? 'success' : 'danger'" size="small">{{ row.action.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="dimLevel" label="Dim Level" width="100">
          <template #default="{ row }">
            {{ row.dimLevel || '-' }}%
          </template>
        </el-table-column>
        <el-table-column prop="schedule" label="Schedule" min-width="160">
          <template #default="{ row }">
            {{ row.days.join(', ') }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="80">
          <template #default="{ row }">
            <el-button link type="primary" :icon="Edit" @click="editSchedule(row)" />
            <el-button link type="danger" :icon="Delete" @click="deleteSchedule(row)" />
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Activity Log -->
    <div class="log-section">
      <div class="section-header">
        <h3><el-icon><Document /></el-icon> Recent Zone Activity</h3>
        <el-button link type="primary" size="small">View All</el-button>
      </div>
      <el-table :data="activityLog" stripe size="small">
        <el-table-column prop="time" label="Time" width="160" />
        <el-table-column prop="zone" label="Zone" min-width="140" />
        <el-table-column prop="action" label="Action" width="100" />
        <el-table-column prop="details" label="Details" min-width="120" />
        <el-table-column prop="user" label="User" width="140" />
      </el-table>
    </div>

    <!-- Add Schedule Dialog -->
    <el-dialog v-model="scheduleDialogVisible" title="Add Zone Schedule" width="450px">
      <el-form :model="newSchedule" label-width="80px">
        <el-form-item label="Zone">
          <el-select v-model="newSchedule.zoneId" placeholder="Select zone" style="width: 100%">
            <el-option v-for="z in lightingZones" :key="z.id" :label="z.name" :value="z.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Action">
          <el-radio-group v-model="newSchedule.action">
            <el-radio-button value="on">Turn On</el-radio-button>
            <el-radio-button value="off">Turn Off</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Dim Level" v-if="newSchedule.action === 'on'">
          <el-slider v-model="newSchedule.dimLevel" :min="0" :max="100" :step="10" />
        </el-form-item>
        <el-form-item label="Time">
          <el-time-picker v-model="newSchedule.time" format="HH:mm" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Repeat">
          <el-select v-model="newSchedule.days" multiple placeholder="Select days" style="width: 100%">
            <el-option label="Monday" value="Mon" />
            <el-option label="Tuesday" value="Tue" />
            <el-option label="Wednesday" value="Wed" />
            <el-option label="Thursday" value="Thu" />
            <el-option label="Friday" value="Fri" />
            <el-option label="Saturday" value="Sat" />
            <el-option label="Sunday" value="Sun" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="scheduleDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveSchedule">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Refresh, Download, Setting, Lightning, Sunny, Remove, Search,
  TrendCharts, Timer, Clock, Plus, Edit, Delete, Document
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// Loading State
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
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
  loading?: boolean
}

interface ZoneSchedule {
  id: number
  zoneId: number
  zoneName: string
  time: string
  action: 'on' | 'off'
  dimLevel?: number
  days: string[]
}

interface ActivityEntry {
  id: number
  time: string
  zone: string
  action: string
  details: string
  user: string
}

// State
const buildingFilter = ref('all')
const floorFilter = ref('all')
const statusFilter = ref('all')
const searchText = ref('')
const scheduleDialogVisible = ref(false)

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

const zoneSchedules = ref<ZoneSchedule[]>([
  { id: 1, zoneId: 1, zoneName: 'Open Office - North', time: '08:00', action: 'on', dimLevel: 80, days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] },
  { id: 2, zoneId: 1, zoneName: 'Open Office - North', time: '18:00', action: 'off', days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] },
  { id: 3, zoneId: 4, zoneName: 'Conference Rooms', time: '09:00', action: 'on', dimLevel: 100, days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] },
  { id: 4, zoneId: 4, zoneName: 'Conference Rooms', time: '17:00', action: 'off', days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] }
])

const activityLog = ref<ActivityEntry[]>([
  { id: 1, time: '2025-05-29 09:15:22', zone: 'Open Office - North', action: 'Turn On', details: 'Dim level: 80%', user: 'admin@ibms.com' },
  { id: 2, time: '2025-05-29 08:30:15', zone: 'Conference Rooms', action: 'Dimming', details: 'Changed to 70%', user: 'john.smith@ibms.com' },
  { id: 3, time: '2025-05-28 18:02:10', zone: 'Open Office - South', action: 'Turn Off', details: '-', user: 'Schedule' },
  { id: 4, time: '2025-05-28 14:20:05', zone: 'Executive Offices', action: 'Dimming', details: 'Changed to 65%', user: 'sarah.chen@ibms.com' }
])

const newSchedule = ref({
  zoneId: null as number | null,
  action: 'on' as 'on' | 'off',
  dimLevel: 70,
  time: null as Date | null,
  days: [] as string[]
})

// Computed
const totalZones = computed(() => lightingZones.value.length)
const zonesOn = computed(() => lightingZones.value.filter(z => z.status === 'on').length)
const totalPower = computed(() => lightingZones.value.reduce((sum, z) => sum + (z.status === 'on' ? z.power : 0), 0).toFixed(1))
const avgDimLevel = computed(() => {
  const zonesWithDim = lightingZones.value.filter(z => z.hasDimming && z.status === 'on')
  if (zonesWithDim.length === 0) return 0
  return Math.round(zonesWithDim.reduce((sum, z) => sum + z.dimLevel, 0) / zonesWithDim.length)
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
const turnOn = async (zone: LightingZone) => {
  zone.loading = true
  await new Promise(resolve => setTimeout(resolve, 300))
  zone.status = 'on'
  if (zone.hasDimming && zone.dimLevel === 0) {
    zone.dimLevel = 70
  }
  zone.loading = false
  ElMessage.success(`${zone.name} turned ON`)
  activityLog.value.unshift({
    id: Date.now(),
    time: new Date().toLocaleString(),
    zone: zone.name,
    action: 'Turn On',
    details: `Dim level: ${zone.dimLevel}%`,
    user: 'Current User'
  })
}

const turnOff = async (zone: LightingZone) => {
  zone.loading = true
  await new Promise(resolve => setTimeout(resolve, 300))
  zone.status = 'off'
  zone.dimLevel = 0
  zone.loading = false
  ElMessage.success(`${zone.name} turned OFF`)
  activityLog.value.unshift({
    id: Date.now(),
    time: new Date().toLocaleString(),
    zone: zone.name,
    action: 'Turn Off',
    details: '-',
    user: 'Current User'
  })
}

const updateDimLevel = async (zone: LightingZone) => {
  if (zone.status === 'on') {
    await new Promise(resolve => setTimeout(resolve, 200))
    ElMessage.info(`${zone.name} dimming set to ${zone.dimLevel}%`)
    activityLog.value.unshift({
      id: Date.now(),
      time: new Date().toLocaleString(),
      zone: zone.name,
      action: 'Dimming',
      details: `Changed to ${zone.dimLevel}%`,
      user: 'Current User'
    })
  }
}

const setPresetDim = (zone: LightingZone, level: number) => {
  zone.dimLevel = level
  updateDimLevel(zone)
}

const refreshData = () => {
  ElMessage.success('Data refreshed')
}

const exportReport = () => {
  ElMessage.info('Exporting zone control report...')
}

const openSettings = () => {
  ElMessage.info('Opening zone control settings...')
}

const addSchedule = () => {
  newSchedule.value = {
    zoneId: null,
    action: 'on',
    dimLevel: 70,
    time: null,
    days: []
  }
  scheduleDialogVisible.value = true
}

const saveSchedule = () => {
  if (!newSchedule.value.zoneId || !newSchedule.value.time || newSchedule.value.days.length === 0) {
    ElMessage.warning('Please fill all required fields')
    return
  }
  const zone = lightingZones.value.find(z => z.id === newSchedule.value.zoneId)
  if (zone) {
    const timeStr = newSchedule.value.time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
    zoneSchedules.value.push({
      id: Date.now(),
      zoneId: newSchedule.value.zoneId,
      zoneName: zone.name,
      time: timeStr,
      action: newSchedule.value.action,
      dimLevel: newSchedule.value.action === 'on' ? newSchedule.value.dimLevel : undefined,
      days: newSchedule.value.days
    })
    ElMessage.success('Schedule added')
  }
  scheduleDialogVisible.value = false
}

const editSchedule = (row: ZoneSchedule) => {
  ElMessage.info(`Edit schedule for ${row.zoneName} at ${row.time}`)
}

const deleteSchedule = (row: ZoneSchedule) => {
  const index = zoneSchedules.value.findIndex(s => s.id === row.id)
  if (index !== -1) {
    zoneSchedules.value.splice(index, 1)
    ElMessage.success(`Schedule deleted for ${row.zoneName}`)
  }
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
.zone-control-page {
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

/* Stats Row */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}
.stat-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: #e8f4ff;
  color: #409eff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}
.stat-number { font-size: 28px; font-weight: 700; color: #1f2f3d; }
.stat-label { font-size: 13px; color: #909399; margin-top: 4px; }

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
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
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

.zone-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}
.info-item { text-align: center; flex: 1; }
.info-label { display: block; font-size: 11px; color: #909399; margin-bottom: 4px; }
.info-value { font-size: 14px; font-weight: 600; color: #1f2f3d; }
.text-success { color: #67c23a; }
.text-muted { color: #c0c4cc; }

.control-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-bottom: 16px;
}

.dimming-section { margin-top: 12px; }
.dimming-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}
.dimming-label { font-size: 12px; color: #606266; }
.dimming-value { font-size: 12px; font-weight: 600; color: #409eff; }
.preset-buttons {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  justify-content: center;
}

/* Empty State */
.empty-state {
  background: white;
  border-radius: 16px;
  padding: 40px;
  margin-bottom: 24px;
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

:deep(.el-table) { border-radius: 12px; }
:deep(.el-table th) { background-color: #fafafa; font-weight: 600; }
</style>