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

  <!-- Mode Control Page Content -->
  <div v-else class="mode-control-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>HVAC Mode Control</h1>
        <p class="subtitle">Control operating modes for HVAC equipment including Cooling, Heating, Fan, and Auto</p>
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
        <div class="stat-icon blue">
          <el-icon><ColdDrink /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-number">{{ coolingCount }}</div>
          <div class="stat-label">Cooling Mode</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><HotWater /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-number">{{ heatingCount }}</div>
          <div class="stat-label">Heating Mode</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><WindPower /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-number">{{ fanCount }}</div>
          <div class="stat-label">Fan Only</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><Refresh /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-number">{{ autoCount }}</div>
          <div class="stat-label">Auto Mode</div>
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
      <el-select v-model="modeFilter" placeholder="Mode" clearable style="width: 120px">
        <el-option label="All Modes" value="all" />
        <el-option label="Cooling" value="cooling" />
        <el-option label="Heating" value="heating" />
        <el-option label="Fan" value="fan" />
        <el-option label="Auto" value="auto" />
      </el-select>
      <el-input v-model="searchText" placeholder="Search..." :prefix-icon="Search" style="width: 200px" clearable />
      <el-button type="primary" :icon="Check" @click="openBatchDialog">Batch Update</el-button>
    </div>

    <!-- Equipment Grid -->
    <div class="equipment-grid">
      <div v-for="item in filteredEquipment" :key="item.id" class="equipment-card" :class="`mode-${item.mode}`">
        <div class="card-header">
          <div>
            <div class="equipment-name">{{ item.name }}</div>
            <div class="equipment-location">{{ item.location }}</div>
          </div>
          <el-tag :type="getModeTagType(item.mode)" size="small" effect="dark">
            {{ item.mode.toUpperCase() }}
          </el-tag>
        </div>

        <div class="temperature-row">
          <div class="temp-box">
            <div class="temp-label">Current</div>
            <div class="temp-value" :class="getTempDiffClass(item.currentTemp, item.setpoint)">
              {{ item.currentTemp }}°C
            </div>
          </div>
          <div class="temp-box">
            <div class="temp-label">Setpoint</div>
            <div class="temp-value">{{ item.setpoint }}°C</div>
          </div>
          <div class="temp-diff">{{ getTempDiff(item.currentTemp, item.setpoint) }}</div>
        </div>

        <div class="mode-selector">
          <div class="section-label">Operation Mode</div>
          <el-radio-group v-model="item.mode" @change="updateMode(item)">
            <el-radio-button value="cooling">
              <el-icon><ColdDrink /></el-icon> Cool
            </el-radio-button>
            <el-radio-button value="heating">
              <el-icon><HotWater /></el-icon> Heat
            </el-radio-button>
            <el-radio-button value="fan">
              <el-icon><WindPower /></el-icon> Fan
            </el-radio-button>
            <el-radio-button value="auto">
              <el-icon><Refresh /></el-icon> Auto
            </el-radio-button>
          </el-radio-group>
        </div>

        <div class="fan-speed-row">
          <div class="section-label">Fan Speed: {{ item.fanSpeed }}%</div>
          <el-slider v-model="item.fanSpeed" :min="0" :max="100" :step="10" @change="updateFanSpeed(item)" />
        </div>
      </div>
    </div>

    <!-- Batch Update Dialog -->
    <el-dialog v-model="batchDialogVisible" title="Batch Update Mode" width="400px">
      <div class="batch-dialog">
        <p>Apply to all {{ filteredEquipment.length }} units:</p>
        <el-radio-group v-model="batchMode" size="large">
          <el-radio-button value="cooling">Cooling</el-radio-button>
          <el-radio-button value="heating">Heating</el-radio-button>
          <el-radio-button value="fan">Fan Only</el-radio-button>
          <el-radio-button value="auto">Auto</el-radio-button>
        </el-radio-group>
      </div>
      <template #footer>
        <el-button @click="batchDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="applyBatchUpdate">Apply</el-button>
      </template>
    </el-dialog>

    <!-- Schedule Table -->
    <div class="schedule-section">
      <div class="section-header">
        <h3><el-icon><Clock /></el-icon> Mode Schedule</h3>
        <el-switch v-model="scheduleEnabled" active-text="Schedule Active" />
      </div>
      <el-table :data="scheduleRules" stripe size="small">
        <el-table-column prop="time" label="Time" width="100" />
        <el-table-column prop="zone" label="Zone / Area" min-width="150" />
        <el-table-column prop="mode" label="Mode" width="100">
          <template #default="{ row }">
            <el-tag :type="getModeTagType(row.mode)" size="small">{{ row.mode }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="fanSpeed" label="Fan Speed" width="100" />
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
        <h3><el-icon><Document /></el-icon> Recent Changes</h3>
        <el-button link type="primary" size="small">View All</el-button>
      </div>
      <el-table :data="activityLog" stripe size="small">
        <el-table-column prop="time" label="Time" width="160" />
        <el-table-column prop="equipment" label="Equipment" min-width="140" />
        <el-table-column prop="action" label="Action" width="100" />
        <el-table-column prop="change" label="Change" min-width="120" />
        <el-table-column prop="user" label="User" width="140" />
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Refresh, Download, Setting, ColdDrink, HotWater, WindPower,
  Search, Check, Clock, Edit, Delete, Plus, Document
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// Loading State
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = ['Preparing...', 'Loading modules...', 'Initializing...', 'Almost ready...']

// Data Models
interface HVACEquipment {
  id: number
  name: string
  location: string
  currentTemp: number
  setpoint: number
  mode: 'cooling' | 'heating' | 'fan' | 'auto'
  fanSpeed: number
}

interface ScheduleRule {
  id: number
  time: string
  zone: string
  mode: string
  fanSpeed: number
}

interface ActivityLog {
  id: number
  time: string
  equipment: string
  action: string
  change: string
  user: string
}

// State
const buildingFilter = ref('all')
const modeFilter = ref('all')
const searchText = ref('')
const scheduleEnabled = ref(true)
const batchDialogVisible = ref(false)
const batchMode = ref('auto')

// Mock Data
const equipment = ref<HVACEquipment[]>([
  { id: 1, name: 'AHU-101', location: 'Building A - Floor 1', currentTemp: 22.5, setpoint: 22.0, mode: 'cooling', fanSpeed: 65 },
  { id: 2, name: 'AHU-102', location: 'Building A - Floor 2', currentTemp: 23.2, setpoint: 22.5, mode: 'cooling', fanSpeed: 70 },
  { id: 3, name: 'FCU-201', location: 'Building B - Floor 1', currentTemp: 21.8, setpoint: 22.0, mode: 'heating', fanSpeed: 50 },
  { id: 4, name: 'FCU-202', location: 'Building B - Floor 2', currentTemp: 20.5, setpoint: 21.0, mode: 'heating', fanSpeed: 45 },
  { id: 5, name: 'AHU-103', location: 'Building A - Floor 3', currentTemp: 23.5, setpoint: 23.0, mode: 'auto', fanSpeed: 55 },
  { id: 6, name: 'CRAC-01', location: 'Data Center - Row A', currentTemp: 21.0, setpoint: 21.0, mode: 'cooling', fanSpeed: 80 },
  { id: 7, name: 'AHU-201', location: 'Building B - Floor 1', currentTemp: 22.2, setpoint: 22.0, mode: 'auto', fanSpeed: 60 },
  { id: 8, name: 'FCU-203', location: 'Building B - Floor 2', currentTemp: 19.8, setpoint: 20.5, mode: 'heating', fanSpeed: 40 },
  { id: 9, name: 'AHU-104', location: 'Building A - Floor 4', currentTemp: 24.0, setpoint: 23.5, mode: 'cooling', fanSpeed: 75 },
  { id: 10, name: 'CRAC-02', location: 'Data Center - Row B', currentTemp: 21.5, setpoint: 21.5, mode: 'fan', fanSpeed: 65 }
])

const scheduleRules = ref<ScheduleRule[]>([
  { id: 1, time: '08:00', zone: 'All Zones', mode: 'cooling', fanSpeed: 65 },
  { id: 2, time: '12:00', zone: 'All Zones', mode: 'cooling', fanSpeed: 75 },
  { id: 3, time: '18:00', zone: 'All Zones', mode: 'heating', fanSpeed: 50 },
  { id: 4, time: '22:00', zone: 'All Zones', mode: 'auto', fanSpeed: 40 }
])

const activityLog = ref<ActivityLog[]>([
  { id: 1, time: '2025-05-29 09:15:22', equipment: 'AHU-101', action: 'Mode Change', change: 'cooling → auto', user: 'admin@ibms.com' },
  { id: 2, time: '2025-05-29 08:30:15', equipment: 'FCU-201', action: 'Mode Change', change: 'heating → cooling', user: 'Schedule' },
  { id: 3, time: '2025-05-28 18:02:10', equipment: 'All Zones', action: 'Schedule', change: 'cooling → heating', user: 'System' },
  { id: 4, time: '2025-05-28 14:20:05', equipment: 'AHU-102', action: 'Fan Speed', change: '60% → 70%', user: 'john.smith@ibms.com' }
])

// Computed
const coolingCount = computed(() => equipment.value.filter(e => e.mode === 'cooling').length)
const heatingCount = computed(() => equipment.value.filter(e => e.mode === 'heating').length)
const fanCount = computed(() => equipment.value.filter(e => e.mode === 'fan').length)
const autoCount = computed(() => equipment.value.filter(e => e.mode === 'auto').length)

const filteredEquipment = computed(() => {
  let result = [...equipment.value]
  if (buildingFilter.value !== 'all') {
    result = result.filter(e => e.location.includes(buildingFilter.value))
  }
  if (modeFilter.value !== 'all') {
    result = result.filter(e => e.mode === modeFilter.value)
  }
  if (searchText.value) {
    const s = searchText.value.toLowerCase()
    result = result.filter(e => e.name.toLowerCase().includes(s) || e.location.toLowerCase().includes(s))
  }
  return result
})

// Helper Functions
const getModeTagType = (mode: string) => {
  const map: Record<string, string> = { cooling: 'primary', heating: 'danger', fan: 'info', auto: 'success' }
  return map[mode] || 'info'
}

const getTempDiffClass = (current: number, setpoint: number) => {
  const diff = Math.abs(current - setpoint)
  if (diff > 2) return 'temp-critical'
  if (diff > 1) return 'temp-warning'
  return 'temp-normal'
}

const getTempDiff = (current: number, setpoint: number) => {
  const diff = current - setpoint
  if (diff > 0) return `+${diff.toFixed(1)}°C`
  if (diff < 0) return `${diff.toFixed(1)}°C`
  return '✓'
}

// Actions
const updateMode = (item: HVACEquipment) => {
  ElMessage.success(`${item.name} set to ${item.mode.toUpperCase()} mode`)
  activityLog.value.unshift({
    id: Date.now(),
    time: new Date().toLocaleString(),
    equipment: item.name,
    action: 'Mode Change',
    change: `→ ${item.mode}`,
    user: 'Current User'
  })
}

const updateFanSpeed = (item: HVACEquipment) => {
  ElMessage.info(`${item.name} fan speed: ${item.fanSpeed}%`)
}

const openBatchDialog = () => {
  batchDialogVisible.value = true
}

const applyBatchUpdate = () => {
  const newMode = batchMode.value as 'cooling' | 'heating' | 'fan' | 'auto'
  filteredEquipment.value.forEach(item => {
    item.mode = newMode
  })
  ElMessage.success(`Batch update: ${filteredEquipment.value.length} units set to ${newMode.toUpperCase()} mode`)
  batchDialogVisible.value = false
  activityLog.value.unshift({
    id: Date.now(),
    time: new Date().toLocaleString(),
    equipment: 'Batch',
    action: 'Batch Mode',
    change: `${filteredEquipment.value.length} units → ${newMode}`,
    user: 'Current User'
  })
}

const refreshData = () => {
  ElMessage.success('Data refreshed')
}

const exportReport = () => {
  ElMessage.info('Exporting mode control report...')
}

const openSettings = () => {
  ElMessage.info('Opening settings...')
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
.mode-control-page {
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
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}
.stat-icon.blue { background: #e8f4ff; color: #409eff; }
.stat-icon.red { background: #ffe8e8; color: #f56c6c; }
.stat-icon.green { background: #e8f8f0; color: #67c23a; }
.stat-icon.purple { background: #f0e8ff; color: #8b5cf6; }
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

/* Equipment Grid */
.equipment-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}
.equipment-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
  border-top: 4px solid #ddd;
}
.equipment-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}
.equipment-card.mode-cooling { border-top-color: #409eff; }
.equipment-card.mode-heating { border-top-color: #f56c6c; }
.equipment-card.mode-fan { border-top-color: #67c23a; }
.equipment-card.mode-auto { border-top-color: #8b5cf6; }
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}
.equipment-name { font-size: 16px; font-weight: 600; color: #1f2f3d; }
.equipment-location { font-size: 12px; color: #909399; margin-top: 2px; }

.temperature-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}
.temp-box { text-align: center; }
.temp-label { font-size: 12px; color: #909399; margin-bottom: 4px; }
.temp-value { font-size: 24px; font-weight: 700; }
.temp-value.temp-normal { color: #67c23a; }
.temp-value.temp-warning { color: #e6a23c; }
.temp-value.temp-critical { color: #f56c6c; }
.temp-diff { font-size: 14px; font-weight: 500; color: #67c23a; }

.mode-selector, .fan-speed-row { margin-top: 16px; }
.section-label { font-size: 13px; font-weight: 500; color: #606266; margin-bottom: 8px; }
:deep(.el-radio-group) { display: flex; width: 100%; }
:deep(.el-radio-button) { flex: 1; }
:deep(.el-radio-button__inner) { display: flex; align-items: center; justify-content: center; gap: 6px; width: 100%; }

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
.batch-dialog {
  text-align: center;
  padding: 20px;
}
.batch-dialog p { margin-bottom: 20px; color: #606266; }
:deep(.el-table) { border-radius: 12px; }
:deep(.el-table th) { background-color: #fafafa; font-weight: 600; }
</style>