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

  <!-- Temperature Setpoint Page Content -->
  <div v-else class="temperature-setpoint-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>Temperature Setpoint Control</h1>
        <p class="subtitle">Monitor and adjust HVAC temperature setpoints across all zones and equipment</p>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="refreshData">Refresh</el-button>
        <el-button type="primary" :icon="Download" @click="exportReport">Export Report</el-button>
        <el-button :icon="Setting" @click="openSettings">Settings</el-button>
      </div>
    </div>

    <!-- Current Status Summary -->
    <div class="status-cards">
      <div class="status-card">
        <div class="status-icon">
          <el-icon :size="28"><Sunny /></el-icon>
        </div>
        <div class="status-info">
          <div class="status-value">{{ avgSetpoint }}°C</div>
          <div class="status-label">Average Setpoint</div>
        </div>
      </div>
      <div class="status-card">
        <div class="status-icon">
          <el-icon :size="28"><TrendCharts /></el-icon>
        </div>
        <div class="status-info">
          <div class="status-value">{{ avgCurrentTemp }}°C</div>
          <div class="status-label">Average Current Temp</div>
        </div>
      </div>
      <div class="status-card">
        <div class="status-icon">
          <el-icon :size="28"><Timer /></el-icon>
        </div>
        <div class="status-info">
          <div class="status-value">{{ zonesControlled }}</div>
          <div class="status-label">Zones Controlled</div>
        </div>
      </div>
      <div class="status-card">
        <div class="status-icon">
          <el-icon :size="28"><WarningFilled /></el-icon>
        </div>
        <div class="status-info">
          <div class="status-value">{{ zonesOutOfRange }}</div>
          <div class="status-label">Out of Range</div>
        </div>
      </div>
    </div>

    <!-- Temperature Control Grid -->
    <div class="control-grid">
      <div v-for="zone in filteredZones" :key="zone.id" class="zone-card" :class="getZoneStatusClass(zone)">
        <div class="zone-header">
          <div class="zone-name">{{ zone.name }}</div>
          <div class="zone-location">{{ zone.location }}</div>
        </div>
        <div class="zone-temp">
          <div class="current-temp">
            <span class="temp-label">Current</span>
            <span class="temp-value" :class="getTempClass(zone.currentTemp, zone.setpoint)">
              {{ zone.currentTemp }}°C
            </span>
          </div>
          <div class="target-temp">
            <span class="temp-label">Setpoint</span>
            <span class="temp-value">{{ zone.setpoint }}°C</span>
          </div>
          <div class="temp-diff" :class="getDiffClass(zone.currentTemp, zone.setpoint)">
            {{ getTempDiff(zone.currentTemp, zone.setpoint) }}
          </div>
        </div>
        <div class="temp-slider">
          <el-slider
              v-model="zone.setpoint"
              :min="zone.minTemp"
              :max="zone.maxTemp"
              :step="0.5"
              :marks="{ 18: '18°C', 22: '22°C', 26: '26°C' }"
              @change="updateSetpoint(zone)"
          />
        </div>
        <div class="zone-actions">
          <el-button size="small" :icon="Minus" @click="decrementSetpoint(zone)" :disabled="zone.setpoint <= zone.minTemp" />
          <el-button size="small" :icon="Refresh" @click="resetSetpoint(zone)" />
          <el-button size="small" :icon="Plus" @click="incrementSetpoint(zone)" :disabled="zone.setpoint >= zone.maxTemp" />
        </div>
      </div>
    </div>

    <!-- Zone Filters -->
    <div class="filter-bar">
      <el-select v-model="zoneFilter" placeholder="All Zones" clearable size="default" style="width: 160px">
        <el-option label="All Zones" value="all" />
        <el-option label="Building A" value="building-a" />
        <el-option label="Building B" value="building-b" />
        <el-option label="Data Center" value="datacenter" />
      </el-select>
      <el-select v-model="statusFilter" placeholder="All Status" clearable size="default" style="width: 140px">
        <el-option label="All Status" value="all" />
        <el-option label="Normal" value="normal" />
        <el-option label="Warning" value="warning" />
        <el-option label="Critical" value="critical" />
      </el-select>
      <el-input
          v-model="searchText"
          placeholder="Search zones..."
          :prefix-icon="Search"
          style="width: 200px"
          clearable
      />
      <el-button type="primary" :icon="Check" @click="applyBatchSettings">Apply to All</el-button>
    </div>

    <!-- Schedule Settings -->
    <div class="schedule-card">
      <div class="card-header">
        <h3>
          <el-icon><Clock /></el-icon>
          Schedule Settings
        </h3>
        <el-switch v-model="scheduleEnabled" active-text="Schedule Enabled" />
      </div>
      <div class="schedule-table">
        <el-table :data="scheduleRules" stripe size="small" style="width: 100%">
          <el-table-column prop="time" label="Time" width="100" />
          <el-table-column prop="zone" label="Zone" min-width="150" />
          <el-table-column prop="setpoint" label="Setpoint (°C)" width="120" align="center">
            <template #default="{ row }">
              <el-input-number v-model="row.setpoint" :min="18" :max="26" :step="0.5" size="small" controls-position="right" style="width: 80px" />
            </template>
          </el-table-column>
          <el-table-column prop="action" label="Action" width="100" align="center">
            <template #default="{ row }">
              <el-select v-model="row.action" size="small" style="width: 100px">
                <el-option label="Cooling" value="cooling" />
                <el-option label="Heating" value="heating" />
                <el-option label="Auto" value="auto" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="80" align="center">
            <template #default="{ row }">
              <el-button link type="primary" size="small" :icon="Edit" @click="editSchedule(row)" />
              <el-button link type="danger" size="small" :icon="Delete" @click="deleteSchedule(row)" />
            </template>
          </el-table-column>
        </el-table>
        <el-button type="primary" link size="small" style="margin-top: 12px" @click="addScheduleRule">
          <el-icon><Plus /></el-icon> Add Schedule Rule
        </el-button>
      </div>
    </div>

    <!-- Temperature Trend Chart -->
    <div class="chart-card">
      <div class="card-header">
        <h3>Temperature Trend - Last 24 Hours</h3>
        <el-select v-model="chartZone" placeholder="Select Zone" size="small" style="width: 180px">
          <el-option v-for="zone in zones" :key="zone.id" :label="zone.name" :value="zone.id" />
        </el-select>
      </div>
      <div class="chart-container" ref="trendChartRef"></div>
    </div>

    <!-- Audit Log -->
    <div class="audit-card">
      <div class="card-header">
        <h3>
          <el-icon><Document /></el-icon>
          Recent Setpoint Changes
        </h3>
        <el-button link type="primary" size="small">View All</el-button>
      </div>
      <el-table :data="auditLog" stripe size="small" style="width: 100%">
        <el-table-column prop="timestamp" label="Time" width="160" />
        <el-table-column prop="zone" label="Zone" min-width="150" />
        <el-table-column prop="oldValue" label="Old (°C)" width="100" align="center" />
        <el-table-column prop="newValue" label="New (°C)" width="100" align="center" />
        <el-table-column prop="user" label="User" width="140" />
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Refresh,
  Download,
  Setting,
  Sunny,
  TrendCharts,
  Timer,
  WarningFilled,
  Plus,
  Minus,
  Search,
  Check,
  Clock,
  Edit,
  Delete,
  Document
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing...',
  'Almost ready...'
]

// ==================== Data Structures ====================
interface Zone {
  id: number
  name: string
  location: string
  currentTemp: number
  setpoint: number
  minTemp: number
  maxTemp: number
  status: 'normal' | 'warning' | 'critical'
}

interface ScheduleRule {
  id: number
  time: string
  zone: string
  setpoint: number
  action: string
}

interface AuditEntry {
  id: number
  timestamp: string
  zone: string
  oldValue: number
  newValue: number
  user: string
}

// ==================== State ====================
const zoneFilter = ref('all')
const statusFilter = ref('all')
const searchText = ref('')
const scheduleEnabled = ref(true)
const chartZone = ref(1)

// Chart refs
const trendChartRef = ref<HTMLElement | null>(null)
let trendChart: echarts.ECharts | null = null

// ==================== Mock Data ====================
const zones = ref<Zone[]>([
  { id: 1, name: 'Open Office - North', location: 'Building A, Floor 1', currentTemp: 22.5, setpoint: 22.0, minTemp: 18, maxTemp: 26, status: 'normal' },
  { id: 2, name: 'Open Office - South', location: 'Building A, Floor 1', currentTemp: 23.2, setpoint: 22.5, minTemp: 18, maxTemp: 26, status: 'warning' },
  { id: 3, name: 'Executive Suites', location: 'Building A, Floor 2', currentTemp: 21.8, setpoint: 21.5, minTemp: 18, maxTemp: 26, status: 'normal' },
  { id: 4, name: 'Conference Room A', location: 'Building A, Floor 2', currentTemp: 24.5, setpoint: 23.0, minTemp: 18, maxTemp: 26, status: 'warning' },
  { id: 5, name: 'Server Room', location: 'Building A, Ground', currentTemp: 19.2, setpoint: 20.0, minTemp: 16, maxTemp: 24, status: 'normal' },
  { id: 6, name: 'Open Office - East', location: 'Building B, Floor 1', currentTemp: 23.8, setpoint: 22.0, minTemp: 18, maxTemp: 26, status: 'critical' },
  { id: 7, name: 'Open Office - West', location: 'Building B, Floor 1', currentTemp: 22.8, setpoint: 22.0, minTemp: 18, maxTemp: 26, status: 'normal' },
  { id: 8, name: 'Meeting Rooms', location: 'Building B, Floor 2', currentTemp: 23.5, setpoint: 22.5, minTemp: 18, maxTemp: 26, status: 'warning' },
  { id: 9, name: 'Data Hall', location: 'Data Center', currentTemp: 21.5, setpoint: 21.0, minTemp: 18, maxTemp: 24, status: 'normal' },
  { id: 10, name: 'UPS Room', location: 'Data Center', currentTemp: 22.0, setpoint: 22.0, minTemp: 18, maxTemp: 24, status: 'normal' }
])

const scheduleRules = ref<ScheduleRule[]>([
  { id: 1, time: '08:00', zone: 'All Zones', setpoint: 22.0, action: 'auto' },
  { id: 2, time: '18:00', zone: 'All Zones', setpoint: 20.0, action: 'auto' },
  { id: 3, time: '22:00', zone: 'All Zones', setpoint: 19.0, action: 'auto' }
])

const auditLog = ref<AuditEntry[]>([
  { id: 1, timestamp: '2025-05-29 09:15:22', zone: 'Open Office - North', oldValue: 21.5, newValue: 22.0, user: 'admin@ibms.com' },
  { id: 2, timestamp: '2025-05-29 08:30:15', zone: 'Executive Suites', oldValue: 22.0, newValue: 21.5, user: 'schedule' },
  { id: 3, timestamp: '2025-05-28 18:02:10', zone: 'All Zones', oldValue: 22.0, newValue: 20.0, user: 'schedule' },
  { id: 4, timestamp: '2025-05-28 14:20:05', zone: 'Conference Room A', oldValue: 22.0, newValue: 23.0, user: 'john.smith@ibms.com' }
])

// ==================== Computed Values ====================
const avgSetpoint = computed(() => {
  const sum = zones.value.reduce((acc, z) => acc + z.setpoint, 0)
  return (sum / zones.value.length).toFixed(1)
})

const avgCurrentTemp = computed(() => {
  const sum = zones.value.reduce((acc, z) => acc + z.currentTemp, 0)
  return (sum / zones.value.length).toFixed(1)
})

const zonesControlled = computed(() => zones.value.length)
const zonesOutOfRange = computed(() => zones.value.filter(z => z.status !== 'normal').length)

const filteredZones = computed(() => {
  let result = [...zones.value]
  if (zoneFilter.value !== 'all') {
    const filterMap: Record<string, string> = {
      'building-a': 'Building A',
      'building-b': 'Building B',
      'datacenter': 'Data Center'
    }
    result = result.filter(z => z.location.includes(filterMap[zoneFilter.value]))
  }
  if (statusFilter.value !== 'all') {
    result = result.filter(z => z.status === statusFilter.value)
  }
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(z =>
        z.name.toLowerCase().includes(search) ||
        z.location.toLowerCase().includes(search)
    )
  }
  return result
})

// ==================== Helper Functions ====================
const getZoneStatusClass = (zone: Zone) => {
  if (zone.status === 'critical') return 'status-critical'
  if (zone.status === 'warning') return 'status-warning'
  return 'status-normal'
}

const getTempClass = (current: number, setpoint: number) => {
  const diff = Math.abs(current - setpoint)
  if (diff > 2) return 'temp-critical'
  if (diff > 1) return 'temp-warning'
  return 'temp-normal'
}

const getDiffClass = (current: number, setpoint: number) => {
  const diff = current - setpoint
  if (diff > 2) return 'diff-hot'
  if (diff < -2) return 'diff-cold'
  if (diff > 0) return 'diff-warm'
  if (diff < 0) return 'diff-cool'
  return 'diff-normal'
}

const getTempDiff = (current: number, setpoint: number) => {
  const diff = current - setpoint
  if (diff > 0) return `+${diff.toFixed(1)}°C`
  if (diff < 0) return `${diff.toFixed(1)}°C`
  return 'OK'
}

// ==================== Actions ====================
const updateSetpoint = async (zone: Zone) => {
  ElMessage.success(`${zone.name} setpoint changed to ${zone.setpoint}°C`)
  // Add audit log
  auditLog.value.unshift({
    id: Date.now(),
    timestamp: new Date().toLocaleString(),
    zone: zone.name,
    oldValue: zone.currentTemp,
    newValue: zone.setpoint,
    user: 'current-user@ibms.com'
  })
  // Simulate temperature change
  zone.currentTemp = zone.setpoint + (Math.random() - 0.5) * 1.5
  zone.currentTemp = Number(zone.currentTemp.toFixed(1))
  zone.status = Math.abs(zone.currentTemp - zone.setpoint) > 2 ? 'critical' :
      Math.abs(zone.currentTemp - zone.setpoint) > 1 ? 'warning' : 'normal'
}

const incrementSetpoint = (zone: Zone) => {
  if (zone.setpoint < zone.maxTemp) {
    zone.setpoint += 0.5
    updateSetpoint(zone)
  }
}

const decrementSetpoint = (zone: Zone) => {
  if (zone.setpoint > zone.minTemp) {
    zone.setpoint -= 0.5
    updateSetpoint(zone)
  }
}

const resetSetpoint = (zone: Zone) => {
  zone.setpoint = 22.0
  updateSetpoint(zone)
}

const applyBatchSettings = () => {
  const newSetpoint = 22.0
  zones.value.forEach(zone => {
    zone.setpoint = newSetpoint
  })
  ElMessage.success('Batch update applied to all zones')
  refreshData()
}

const openSettings = () => {
  ElMessage.info('Opening temperature settings...')
}

const refreshData = async () => {
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 500))
  initTrendChart()
  tableLoading.value = false
  ElMessage.success('Data refreshed')
}

const exportReport = () => {
  ElMessage.info('Exporting temperature report...')
}

const addScheduleRule = () => {
  ElMessage.info('Add new schedule rule')
}

const editSchedule = (row: ScheduleRule) => {
  ElMessage.info(`Editing schedule for ${row.time}`)
}

const deleteSchedule = (row: ScheduleRule) => {
  ElMessage.info(`Deleting schedule for ${row.time}`)
}

// ==================== Chart Functions ====================
const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)

  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const temperatures = hours.map(() => 21 + Math.random() * 3)

  trendChart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: (value: number) => value + '°C' },
    xAxis: { type: 'category', data: hours, axisLabel: { rotate: 45, interval: 3 } },
    yAxis: { type: 'value', name: 'Temperature (°C)', min: 18, max: 26 },
    series: [{
      type: 'line', data: temperatures, smooth: true, symbol: 'circle',
      lineStyle: { width: 2, color: '#409eff' }, areaStyle: { opacity: 0.1, color: '#409eff' }
    }]
  })
}

// ==================== Lifecycle ====================
onMounted(() => {
  let messageIndex = 0
  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 400)

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      setTimeout(() => {
        initTrendChart()
      }, 100)
      window.addEventListener('resize', () => trendChart?.resize())
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  trendChart?.dispose()
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
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

.loading-dots {
  display: inline-flex;
  gap: 2px;
}

.loading-dots span {
  animation: bounce 1.4s infinite ease-in-out both;
}

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

/* ==================== Main Content ==================== */
.temperature-setpoint-page {
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

/* Status Cards */
.status-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.status-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.status-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e8f4ff;
  color: #409eff;
}

.status-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
  line-height: 1.2;
}

.status-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

/* Control Grid */
.control-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.zone-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
}

.zone-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.zone-card.status-normal { border-left: 4px solid #67c23a; }
.zone-card.status-warning { border-left: 4px solid #e6a23c; }
.zone-card.status-critical { border-left: 4px solid #f56c6c; }

.zone-header {
  margin-bottom: 16px;
}

.zone-name {
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

.zone-location {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.zone-temp {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.current-temp, .target-temp {
  text-align: center;
}

.temp-label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.temp-value {
  font-size: 28px;
  font-weight: 700;
}

.temp-value.temp-normal { color: #67c23a; }
.temp-value.temp-warning { color: #e6a23c; }
.temp-value.temp-critical { color: #f56c6c; }

.temp-diff {
  font-size: 14px;
  font-weight: 500;
}

.temp-diff.diff-normal { color: #67c23a; }
.temp-diff.diff-warm { color: #e6a23c; }
.temp-diff.diff-hot { color: #f56c6c; }
.temp-diff.diff-cool { color: #409eff; }
.temp-diff.diff-cold { color: #8b5cf6; }

.temp-slider {
  margin-bottom: 16px;
}

.zone-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

/* Filter Bar */
.filter-bar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 24px;
  padding: 16px;
  background: white;
  border-radius: 12px;
  align-items: center;
}

/* Schedule Card */
.schedule-card, .chart-card, .audit-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.card-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1f2f3d;
}

.chart-container {
  height: 350px;
  width: 100%;
}

:deep(.el-slider) {
  width: 100%;
}

:deep(.el-slider__runway) {
  margin: 12px 0;
}

:deep(.el-table) {
  border-radius: 12px;
}

:deep(.el-table th.el-table__cell) {
  background-color: #fafafa;
  font-weight: 600;
  color: #1f2f3d;
}
</style>