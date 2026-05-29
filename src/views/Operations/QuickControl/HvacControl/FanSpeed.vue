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

  <!-- Fan Speed Control Page Content -->
  <div v-else class="fan-speed-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>Fan Speed Control</h1>
        <p class="subtitle">Monitor and adjust HVAC fan speeds across all equipment for optimal airflow and efficiency</p>
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
        <div class="stat-icon"><el-icon><WindPower /></el-icon></div>
        <div class="stat-info">
          <div class="stat-number">{{ totalUnits }}</div>
          <div class="stat-label">Total Units</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><el-icon><TrendCharts /></el-icon></div>
        <div class="stat-info">
          <div class="stat-number">{{ avgFanSpeed }}%</div>
          <div class="stat-label">Average Fan Speed</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><el-icon><Lightning /></el-icon></div>
        <div class="stat-info">
          <div class="stat-number">{{ totalAirflow }}<span style="font-size:14px"> CFM</span></div>
          <div class="stat-label">Total Airflow</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><el-icon><Timer /></el-icon></div>
        <div class="stat-info">
          <div class="stat-number">{{ energyImpact }}<span style="font-size:14px"> kW</span></div>
          <div class="stat-label">Fan Energy</div>
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
      <el-select v-model="typeFilter" placeholder="Equipment Type" clearable style="width: 140px">
        <el-option label="All Types" value="all" />
        <el-option label="AHU" value="AHU" />
        <el-option label="FCU" value="FCU" />
        <el-option label="CRAC" value="CRAC" />
        <el-option label="VAV" value="VAV" />
      </el-select>
      <el-input v-model="searchText" placeholder="Search..." :prefix-icon="Search" style="width: 200px" clearable />
      <el-button type="primary" :icon="Check" @click="openBatchDialog">Batch Update</el-button>
    </div>

    <!-- Fan Speed Control Grid -->
    <div class="control-grid">
      <div v-for="item in filteredUnits" :key="item.id" class="fan-card" :class="getSpeedClass(item.fanSpeed)">
        <div class="card-header">
          <div>
            <div class="fan-name">{{ item.name }}</div>
            <div class="fan-location">{{ item.location }}</div>
          </div>
          <div class="fan-status">
            <el-tag :type="getSpeedTagType(item.fanSpeed)" size="small" effect="dark">
              {{ item.fanSpeed }}%
            </el-tag>
          </div>
        </div>

        <!-- Fan Speed Display -->
        <div class="fan-speed-display">
          <div class="speed-gauge">
            <div class="gauge-value">{{ item.fanSpeed }}%</div>
            <div class="gauge-label">Current Speed</div>
          </div>
          <div class="airflow-info">
            <div class="airflow-value">{{ item.airflow }} CFM</div>
            <div class="airflow-label">Airflow</div>
          </div>
          <div class="power-info">
            <div class="power-value">{{ item.power }} kW</div>
            <div class="power-label">Power</div>
          </div>
        </div>

        <!-- Fan Speed Slider -->
        <div class="slider-section">
          <div class="slider-label">
            <span>Fan Speed Control</span>
            <span class="speed-range">{{ item.minSpeed }}% - {{ item.maxSpeed }}%</span>
          </div>
          <el-slider
              v-model="item.fanSpeed"
              :min="item.minSpeed"
              :max="item.maxSpeed"
              :step="5"
              :marks="{ 0: '0%', 25: '25%', 50: '50%', 75: '75%', 100: '100%' }"
              @change="updateFanSpeed(item)"
          />
        </div>

        <!-- Preset Buttons -->
        <div class="preset-buttons">
          <el-button size="small" @click="setPresetSpeed(item, 25)" :disabled="item.fanSpeed === 25">25%</el-button>
          <el-button size="small" @click="setPresetSpeed(item, 50)" :disabled="item.fanSpeed === 50">50%</el-button>
          <el-button size="small" @click="setPresetSpeed(item, 75)" :disabled="item.fanSpeed === 75">75%</el-button>
          <el-button size="small" @click="setPresetSpeed(item, 100)" :disabled="item.fanSpeed === 100">100%</el-button>
        </div>

        <!-- Energy Efficiency Indicator -->
        <div class="efficiency-row">
          <div class="efficiency-label">Efficiency</div>
          <el-progress
              :percentage="getEfficiency(item.fanSpeed)"
              :color="getEfficiencyColor(getEfficiency(item.fanSpeed))"
              :stroke-width="8"
              :format="() => getEfficiency(item.fanSpeed) + '%'"
          />
        </div>
      </div>
    </div>

    <!-- Batch Update Dialog -->
    <el-dialog v-model="batchDialogVisible" title="Batch Fan Speed Update" width="400px">
      <div class="batch-dialog">
        <p>Apply to <strong>{{ filteredUnits.length }}</strong> units:</p>
        <div class="batch-speed">
          <span>Fan Speed:</span>
          <el-slider v-model="batchSpeed" :min="0" :max="100" :step="5" style="flex:1" />
          <span class="batch-speed-value">{{ batchSpeed }}%</span>
        </div>
        <div class="batch-warning">
          <el-alert title="This will override current fan speeds for all filtered units" type="warning" :closable="false" />
        </div>
      </div>
      <template #footer>
        <el-button @click="batchDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="applyBatchUpdate">Apply</el-button>
      </template>
    </el-dialog>

    <!-- Fan Speed Schedule -->
    <div class="schedule-section">
      <div class="section-header">
        <h3><el-icon><Clock /></el-icon> Fan Speed Schedule</h3>
        <el-switch v-model="scheduleEnabled" active-text="Schedule Active" />
      </div>
      <el-table :data="scheduleRules" stripe size="small">
        <el-table-column prop="time" label="Time" width="100" />
        <el-table-column prop="zone" label="Zone / Area" min-width="150" />
        <el-table-column prop="fanSpeed" label="Fan Speed" width="120">
          <template #default="{ row }">
            <el-progress :percentage="row.fanSpeed" :stroke-width="8" :show-text="true" :format="(p) => p + '%'" />
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
        <h3><el-icon><Document /></el-icon> Recent Fan Speed Changes</h3>
        <el-button link type="primary" size="small">View All</el-button>
      </div>
      <el-table :data="activityLog" stripe size="small">
        <el-table-column prop="time" label="Time" width="160" />
        <el-table-column prop="unit" label="Unit" min-width="140" />
        <el-table-column prop="oldSpeed" label="Old Speed" width="100" />
        <el-table-column prop="newSpeed" label="New Speed" width="100" />
        <el-table-column prop="user" label="User" width="140" />
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Refresh, Download, Setting, WindPower, TrendCharts, Lightning, Timer,
  Search, Check, Clock, Edit, Delete, Plus, Document
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// Loading State
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = ['Preparing...', 'Loading modules...', 'Initializing...', 'Almost ready...']

// Data Models
interface FanUnit {
  id: number
  name: string
  location: string
  type: string
  fanSpeed: number
  minSpeed: number
  maxSpeed: number
  airflow: number
  power: number
}

interface ScheduleRule {
  id: number
  time: string
  zone: string
  fanSpeed: number
}

interface ActivityLog {
  id: number
  time: string
  unit: string
  oldSpeed: number
  newSpeed: number
  user: string
}

// State
const buildingFilter = ref('all')
const typeFilter = ref('all')
const searchText = ref('')
const scheduleEnabled = ref(true)
const batchDialogVisible = ref(false)
const batchSpeed = ref(50)

// Mock Data
const fanUnits = ref<FanUnit[]>([
  { id: 1, name: 'AHU-101', location: 'Building A - Floor 1', type: 'AHU', fanSpeed: 65, minSpeed: 30, maxSpeed: 100, airflow: 8500, power: 3.2 },
  { id: 2, name: 'AHU-102', location: 'Building A - Floor 2', type: 'AHU', fanSpeed: 70, minSpeed: 30, maxSpeed: 100, airflow: 9200, power: 3.8 },
  { id: 3, name: 'FCU-201', location: 'Building B - Floor 1', type: 'FCU', fanSpeed: 50, minSpeed: 20, maxSpeed: 90, airflow: 1200, power: 0.6 },
  { id: 4, name: 'FCU-202', location: 'Building B - Floor 2', type: 'FCU', fanSpeed: 45, minSpeed: 20, maxSpeed: 90, airflow: 1080, power: 0.5 },
  { id: 5, name: 'AHU-103', location: 'Building A - Floor 3', type: 'AHU', fanSpeed: 55, minSpeed: 30, maxSpeed: 100, airflow: 7200, power: 2.8 },
  { id: 6, name: 'CRAC-01', location: 'Data Center - Row A', type: 'CRAC', fanSpeed: 80, minSpeed: 40, maxSpeed: 100, airflow: 15000, power: 5.5 },
  { id: 7, name: 'VAV-101', location: 'Building B - Floor 1', type: 'VAV', fanSpeed: 40, minSpeed: 20, maxSpeed: 80, airflow: 600, power: 0.3 },
  { id: 8, name: 'FCU-203', location: 'Building B - Floor 2', type: 'FCU', fanSpeed: 40, minSpeed: 20, maxSpeed: 90, airflow: 960, power: 0.4 },
  { id: 9, name: 'AHU-104', location: 'Building A - Floor 4', type: 'AHU', fanSpeed: 75, minSpeed: 30, maxSpeed: 100, airflow: 9800, power: 4.1 },
  { id: 10, name: 'CRAC-02', location: 'Data Center - Row B', type: 'CRAC', fanSpeed: 65, minSpeed: 40, maxSpeed: 100, airflow: 12200, power: 4.2 }
])

const scheduleRules = ref<ScheduleRule[]>([
  { id: 1, time: '08:00', zone: 'All Zones', fanSpeed: 65 },
  { id: 2, time: '12:00', zone: 'All Zones', fanSpeed: 70 },
  { id: 3, time: '18:00', zone: 'All Zones', fanSpeed: 50 },
  { id: 4, time: '22:00', zone: 'All Zones', fanSpeed: 40 }
])

const activityLog = ref<ActivityLog[]>([
  { id: 1, time: '2025-05-29 09:15:22', unit: 'AHU-101', oldSpeed: 60, newSpeed: 65, user: 'admin@ibms.com' },
  { id: 2, time: '2025-05-29 08:30:15', unit: 'FCU-201', oldSpeed: 45, newSpeed: 50, user: 'Schedule' },
  { id: 3, time: '2025-05-28 18:02:10', unit: 'All Zones', oldSpeed: 70, newSpeed: 50, user: 'Schedule' },
  { id: 4, time: '2025-05-28 14:20:05', unit: 'AHU-102', oldSpeed: 65, newSpeed: 70, user: 'john.smith@ibms.com' }
])

// Computed
const totalUnits = computed(() => fanUnits.value.length)
const avgFanSpeed = computed(() => Math.round(fanUnits.value.reduce((s, u) => s + u.fanSpeed, 0) / totalUnits.value))
const totalAirflow = computed(() => fanUnits.value.reduce((s, u) => s + u.airflow, 0).toLocaleString())
const energyImpact = computed(() => fanUnits.value.reduce((s, u) => s + u.power, 0).toFixed(1))

const filteredUnits = computed(() => {
  let result = [...fanUnits.value]
  if (buildingFilter.value !== 'all') {
    result = result.filter(u => u.location.includes(buildingFilter.value))
  }
  if (typeFilter.value !== 'all') {
    result = result.filter(u => u.type === typeFilter.value)
  }
  if (searchText.value) {
    const s = searchText.value.toLowerCase()
    result = result.filter(u => u.name.toLowerCase().includes(s) || u.location.toLowerCase().includes(s))
  }
  return result
})

// Helper Functions
const getSpeedClass = (speed: number) => {
  if (speed >= 80) return 'speed-high'
  if (speed >= 60) return 'speed-medium'
  if (speed >= 40) return 'speed-low'
  return 'speed-min'
}

const getSpeedTagType = (speed: number) => {
  if (speed >= 80) return 'danger'
  if (speed >= 60) return 'warning'
  if (speed >= 40) return 'primary'
  return 'info'
}

const getEfficiency = (speed: number) => {
  // Fan efficiency is optimal between 60-80%
  if (speed >= 60 && speed <= 80) return 95
  if (speed > 80) return 85
  if (speed > 40) return 75
  return 60
}

const getEfficiencyColor = (efficiency: number) => {
  if (efficiency >= 90) return '#67c23a'
  if (efficiency >= 75) return '#409eff'
  if (efficiency >= 60) return '#e6a23c'
  return '#f56c6c'
}

// Actions
const updateFanSpeed = (unit: FanUnit) => {
  // Update airflow and power based on fan speed (cubic relationship)
  const speedRatio = unit.fanSpeed / 100
  unit.airflow = Math.round(unit.airflow / (unit.fanSpeed / 100) * speedRatio)
  unit.power = Number((unit.power / Math.pow(unit.fanSpeed / 100, 3) * Math.pow(speedRatio, 3)).toFixed(1))

  ElMessage.success(`${unit.name} fan speed set to ${unit.fanSpeed}%`)
  activityLog.value.unshift({
    id: Date.now(),
    time: new Date().toLocaleString(),
    unit: unit.name,
    oldSpeed: unit.fanSpeed,
    newSpeed: unit.fanSpeed,
    user: 'Current User'
  })
}

const setPresetSpeed = (unit: FanUnit, speed: number) => {
  unit.fanSpeed = speed
  updateFanSpeed(unit)
}

const openBatchDialog = () => {
  batchSpeed.value = 50
  batchDialogVisible.value = true
}

const applyBatchUpdate = () => {
  const newSpeed = batchSpeed.value
  filteredUnits.value.forEach(unit => {
    unit.fanSpeed = newSpeed
    const speedRatio = newSpeed / 100
    unit.airflow = Math.round(unit.airflow / (unit.fanSpeed / 100) * speedRatio)
    unit.power = Number((unit.power / Math.pow(unit.fanSpeed / 100, 3) * Math.pow(speedRatio, 3)).toFixed(1))
  })
  ElMessage.success(`Batch update: ${filteredUnits.value.length} units set to ${newSpeed}%`)
  batchDialogVisible.value = false
  activityLog.value.unshift({
    id: Date.now(),
    time: new Date().toLocaleString(),
    unit: 'Batch Update',
    oldSpeed: 0,
    newSpeed: newSpeed,
    user: 'Current User'
  })
}

const refreshData = () => {
  ElMessage.success('Data refreshed')
}

const exportReport = () => {
  ElMessage.info('Exporting fan speed report...')
}

const openSettings = () => {
  ElMessage.info('Opening fan speed settings...')
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
.fan-speed-page {
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

/* Control Grid */
.control-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}
.fan-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
}
.fan-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}
.fan-card.speed-high { border-left: 4px solid #f56c6c; }
.fan-card.speed-medium { border-left: 4px solid #e6a23c; }
.fan-card.speed-low { border-left: 4px solid #409eff; }
.fan-card.speed-min { border-left: 4px solid #67c23a; }

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}
.fan-name { font-size: 16px; font-weight: 600; color: #1f2f3d; }
.fan-location { font-size: 12px; color: #909399; margin-top: 2px; }

.fan-speed-display {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}
.speed-gauge, .airflow-info, .power-info { text-align: center; }
.gauge-value, .airflow-value, .power-value { font-size: 24px; font-weight: 700; color: #1f2f3d; }
.gauge-label, .airflow-label, .power-label { font-size: 11px; color: #909399; margin-top: 4px; }

.slider-section { margin-bottom: 16px; }
.slider-label {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #606266;
  margin-bottom: 12px;
}
.speed-range { color: #909399; font-size: 12px; }
:deep(.el-slider__marks) { white-space: nowrap; }

.preset-buttons {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  justify-content: center;
}
.efficiency-row { margin-top: 8px; }
.efficiency-label { font-size: 12px; color: #909399; margin-bottom: 6px; }

/* Batch Dialog */
.batch-dialog { padding: 8px 0; }
.batch-dialog p { margin-bottom: 20px; color: #606266; }
.batch-speed {
  display: flex;
  align-items: center;
  gap: 16px;
  margin: 20px 0;
}
.batch-speed-value { font-size: 18px; font-weight: 600; color: #409eff; min-width: 50px; text-align: center; }
.batch-warning { margin-top: 16px; }

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