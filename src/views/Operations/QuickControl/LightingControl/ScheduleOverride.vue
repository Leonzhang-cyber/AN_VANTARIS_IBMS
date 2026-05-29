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
        <div class="loading-tip">Schedule Override</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Schedule Override Page Content -->
  <div v-else class="schedule-override-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <div class="title-badge">
          <el-icon><Timer /></el-icon>
          <span>Override Center</span>
        </div>
        <h1>Schedule Override</h1>
        <p class="subtitle">Temporarily override lighting schedules for special events, maintenance, or emergency situations</p>
      </div>
      <div class="header-actions">
        <button class="action-btn" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          <span>Refresh</span>
        </button>
        <button class="action-btn primary" @click="exportReport">
          <el-icon><Download /></el-icon>
          <span>Export</span>
        </button>
        <button class="action-btn" @click="openSettings">
          <el-icon><Setting /></el-icon>
          <span>Settings</span>
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-number">{{ activeOverridesList.length }}</div>
          <div class="stat-label">Active Overrides</div>
        </div>
        <div class="stat-change" v-if="activeOverridesList.length > 0">
          <span class="trend-up">+{{ activeOverridesList.length }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><Sunny /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-number">{{ zonesOverriddenCount }}</div>
          <div class="stat-label">Zones Affected</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-number">{{ avgDurationValue }}<span class="stat-unit">h</span></div>
          <div class="stat-label">Avg Duration</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><Lightning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-number">{{ energyImpactValue }}<span class="stat-unit">kWh</span></div>
          <div class="stat-label">Energy Impact</div>
        </div>
      </div>
    </div>

    <!-- Create Override Section -->
    <div class="create-section">
      <div class="section-header">
        <div class="header-left">
          <div class="header-icon"><el-icon><Plus /></el-icon></div>
          <h3>Create New Override</h3>
        </div>
        <div class="header-right">
          <span class="info-badge">Immediate Effect</span>
        </div>
      </div>

      <div class="create-form">
        <div class="form-row">
          <div class="form-group">
            <label>Select Zone</label>
            <select v-model="newOverride.zoneId" class="form-select-custom">
              <option :value="null" disabled>Choose a lighting zone</option>
              <option v-for="zone in lightingZones" :key="zone.id" :value="zone.id">
                {{ zone.name }} - {{ zone.location }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Override Action</label>
            <div class="action-toggle">
              <button
                  type="button"
                  class="toggle-btn"
                  :class="{ active: newOverride.action === 'on' }"
                  @click="newOverride.action = 'on'"
              >
                <el-icon><Sunny /></el-icon>
                <span>Turn ON</span>
              </button>
              <button
                  type="button"
                  class="toggle-btn"
                  :class="{ active: newOverride.action === 'off' }"
                  @click="newOverride.action = 'off'"
              >
                <el-icon><Remove /></el-icon>
                <span>Turn OFF</span>
              </button>
            </div>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Duration</label>
            <div class="duration-buttons">
              <button
                  v-for="dur in durationOptions"
                  :key="dur.value"
                  type="button"
                  class="duration-btn"
                  :class="{ active: newOverride.duration === dur.value }"
                  @click="newOverride.duration = dur.value"
              >
                {{ dur.label }}
              </button>
              <button
                  type="button"
                  class="duration-btn custom"
                  :class="{ active: newOverride.duration === 'custom' }"
                  @click="newOverride.duration = 'custom'"
              >
                Custom
              </button>
            </div>
          </div>
          <div class="form-group" v-if="newOverride.duration === 'custom'">
            <label>End Time</label>
            <input type="datetime-local" v-model="newOverride.customEndTime" class="datetime-input" />
          </div>
        </div>

        <div class="form-row" v-if="newOverride.action === 'on'">
          <div class="form-group full">
            <label>Dim Level: <span class="dim-value">{{ newOverride.dimLevel }}%</span></label>
            <input type="range" v-model="newOverride.dimLevel" min="0" max="100" step="10" class="dim-slider" />
            <div class="slider-marks">
              <span>0%</span><span>50%</span><span>100%</span>
            </div>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group full">
            <label>Reason (Optional)</label>
            <input type="text" v-model="newOverride.reason" placeholder="e.g., Client meeting, Maintenance, Emergency" class="reason-input-custom" />
          </div>
        </div>

        <div class="form-actions">
          <button class="apply-btn" @click="createOverride">
            <el-icon><Check /></el-icon>
            <span>Apply Override</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Active Overrides Section -->
    <div class="active-section">
      <div class="section-header">
        <div class="header-left">
          <div class="header-icon warning"><el-icon><WarningFilled /></el-icon></div>
          <h3>Active Overrides</h3>
          <span class="active-count">{{ activeOverridesList.length }}</span>
        </div>
        <div class="header-right">
          <button class="clear-all-btn" @click="clearAllOverrides" :disabled="activeOverridesList.length === 0">
            Clear All
          </button>
        </div>
      </div>

      <div v-if="activeOverridesList.length === 0" class="empty-state-modern">
        <div class="empty-icon">
          <el-icon><Timer /></el-icon>
        </div>
        <h4>No Active Overrides</h4>
        <p>Create an override to temporarily change lighting schedules</p>
      </div>

      <div v-else class="overrides-grid">
        <div v-for="override in activeOverridesList" :key="override.id" class="override-card">
          <div class="override-header">
            <div class="zone-badge" :class="override.action">
              <el-icon><Sunny v-if="override.action === 'on'" /><Remove v-else /></el-icon>
              <span>{{ override.action === 'on' ? 'ON' : 'OFF' }}</span>
            </div>
            <div class="zone-info-header">
              <h4>{{ override.zoneName }}</h4>
              <span class="zone-location">{{ getZoneLocation(override.zoneId) }}</span>
            </div>
          </div>

          <div class="override-timer">
            <div class="timer-info">
              <div class="time-remaining">
                <span class="label">Time Remaining</span>
                <span class="value" :class="getRemainingClass(override.remaining)">{{ override.remaining }}</span>
              </div>
              <div class="time-range">
                <span><el-icon><Clock /></el-icon> {{ override.startTime }}</span>
                <span><el-icon><Timer /></el-icon> {{ override.endTime }}</span>
              </div>
            </div>
          </div>

          <div class="override-details" v-if="override.dimLevel">
            <div class="detail-item">
              <span class="detail-label">Dim Level</span>
              <div class="detail-bar">
                <div class="dim-bar" :style="{ width: override.dimLevel + '%' }"></div>
                <span class="detail-value">{{ override.dimLevel }}%</span>
              </div>
            </div>
          </div>

          <div class="override-footer" v-if="override.reason">
            <div class="reason-tag">
              <el-icon><Edit /></el-icon>
              <span>{{ override.reason }}</span>
            </div>
          </div>

          <div class="override-actions">
            <button class="action-extend" @click="extendOverride(override)">
              <el-icon><RefreshRight /></el-icon> Extend
            </button>
            <button class="action-cancel" @click="cancelOverride(override)">
              <el-icon><Close /></el-icon> Cancel
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Override History Section -->
    <div class="history-section">
      <div class="section-header">
        <div class="header-left">
          <div class="header-icon history"><el-icon><Document /></el-icon></div>
          <h3>Override History</h3>
        </div>
        <div class="header-right">
          <button class="view-all-btn">View All →</button>
        </div>
      </div>

      <div class="history-timeline">
        <div v-for="item in overrideHistoryList" :key="item.id" class="history-item">
          <div class="history-time">
            <div class="time">{{ item.timeDisplay }}</div>
            <div class="date">{{ item.dateDisplay }}</div>
          </div>
          <div class="history-line">
            <div class="line-dot" :class="item.action"></div>
            <div class="line"></div>
          </div>
          <div class="history-content">
            <div class="history-header">
              <span class="zone-name">{{ item.zone }}</span>
              <span class="action-tag" :class="item.action">
                {{ item.action === 'on' ? 'Turned ON' : 'Turned OFF' }}
              </span>
            </div>
            <div class="history-details">
              <span class="duration"><el-icon><Timer /></el-icon> {{ item.duration }}</span>
              <span class="reason"><el-icon><Edit /></el-icon> {{ item.reason }}</span>
              <span class="user"><el-icon><User /></el-icon> {{ item.user }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Extend Dialog -->
    <div v-if="extendDialogVisible" class="modal-overlay" @click.self="extendDialogVisible = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Extend Override Duration</h3>
          <button class="modal-close" @click="extendDialogVisible = false">×</button>
        </div>
        <div class="modal-body">
          <div class="extend-zone">
            <el-icon><Location /></el-icon>
            <span>{{ extendTarget?.zoneName }}</span>
          </div>
          <div class="extend-options">
            <div
                v-for="opt in extendOptions"
                :key="opt.value"
                class="extend-option"
                :class="{ active: extendDuration === opt.value }"
                @click="extendDuration = opt.value"
            >
              <el-icon><Plus /></el-icon>
              <span>+{{ opt.label }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="dialog-btn cancel" @click="extendDialogVisible = false">Cancel</button>
          <button class="dialog-btn confirm" @click="confirmExtend">Apply Extension</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Refresh, Download, Setting, Clock, Sunny, Timer, Lightning, Plus,
  WarningFilled, Document, Remove, Edit, Check, Close, RefreshRight,
  Location, User
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
}

interface ScheduleOverride {
  id: number
  zoneId: number
  zoneName: string
  action: 'on' | 'off'
  dimLevel?: number
  startTime: string
  endTime: string
  remaining: string
  reason: string
}

interface OverrideHistoryEntry {
  id: number
  time: string
  zone: string
  action: 'on' | 'off'
  duration: string
  reason: string
  user: string
  timeDisplay: string
  dateDisplay: string
}

// State
const newOverride = ref({
  zoneId: null as number | null,
  action: 'on' as 'on' | 'off',
  duration: '60',
  customEndTime: '',
  dimLevel: 80,
  reason: ''
})
const extendDialogVisible = ref(false)
const extendTarget = ref<ScheduleOverride | null>(null)
const extendDuration = ref('60')

const durationOptions = [
  { label: '30m', value: '30' },
  { label: '1h', value: '60' },
  { label: '2h', value: '120' },
  { label: '4h', value: '240' },
  { label: '8h', value: '480' },
  { label: '24h', value: '1440' }
]

const extendOptions = [
  { label: '30 minutes', value: '30' },
  { label: '1 hour', value: '60' },
  { label: '2 hours', value: '120' },
  { label: '4 hours', value: '240' }
]

// Mock Data
const lightingZones = ref<LightingZone[]>([
  { id: 1, name: 'Open Office - North', location: 'Building A, Floor 1', building: 'A', floor: '1', status: 'on', power: 2.8, hasDimming: true, dimLevel: 80 },
  { id: 2, name: 'Open Office - South', location: 'Building A, Floor 1', building: 'A', floor: '1', status: 'on', power: 2.6, hasDimming: true, dimLevel: 75 },
  { id: 3, name: 'Executive Offices', location: 'Building A, Floor 2', building: 'A', floor: '2', status: 'on', power: 1.8, hasDimming: true, dimLevel: 70 },
  { id: 4, name: 'Conference Rooms', location: 'Building A, Floor 2', building: 'A', floor: '2', status: 'off', power: 1.2, hasDimming: true, dimLevel: 0 },
  { id: 5, name: 'Meeting Rooms', location: 'Building B, Floor 1', building: 'B', floor: '1', status: 'on', power: 1.5, hasDimming: true, dimLevel: 65 }
])

const activeOverrides = ref<ScheduleOverride[]>([
  { id: 1, zoneId: 4, zoneName: 'Conference Rooms', action: 'on', dimLevel: 100, startTime: '14:00', endTime: '18:00', remaining: '2h 30m', reason: 'Client meeting' },
  { id: 2, zoneId: 1, zoneName: 'Open Office - North', action: 'off', startTime: '13:00', endTime: '15:30', remaining: '1h 15m', reason: 'Maintenance work' }
])

const historyData = ref<OverrideHistoryEntry[]>([
  { id: 1, time: '2025-05-29 14:30:00', zone: 'Conference Rooms', action: 'on', duration: '3 hours', reason: 'Client presentation', user: 'John Smith', timeDisplay: '14:30', dateDisplay: '2025-05-29' },
  { id: 2, time: '2025-05-29 10:15:00', zone: 'Meeting Rooms', action: 'off', duration: '1 hour', reason: 'Cleaning', user: 'Schedule', timeDisplay: '10:15', dateDisplay: '2025-05-29' },
  { id: 3, time: '2025-05-28 19:30:00', zone: 'Executive Offices', action: 'on', duration: '2 hours', reason: 'After-hours work', user: 'Sarah Chen', timeDisplay: '19:30', dateDisplay: '2025-05-28' }
])

let timerInterval: ReturnType<typeof setInterval> | null = null

// Computed
const activeOverridesList = computed(() => activeOverrides.value)
const zonesOverriddenCount = computed(() => new Set(activeOverrides.value.map(o => o.zoneId)).size)
const avgDurationValue = computed(() => activeOverrides.value.length > 0 ? 3 : 0)
const energyImpactValue = computed(() => activeOverrides.value.reduce((sum, o) => sum + 2.5, 0))
const overrideHistoryList = computed(() => historyData.value)

const getZoneLocation = (zoneId: number) => {
  const zone = lightingZones.value.find(z => z.id === zoneId)
  return zone?.location || ''
}

const getRemainingClass = (remaining: string) => {
  if (remaining.includes('m')) {
    const mins = parseInt(remaining)
    if (mins <= 30) return 'critical'
    if (mins <= 60) return 'warning'
  }
  if (remaining.includes('h')) {
    const hours = parseInt(remaining)
    if (hours <= 1) return 'warning'
  }
  return 'normal'
}

// Update remaining times
const updateRemainingTimes = () => {
  for (let i = 0; i < activeOverrides.value.length; i++) {
    const override = activeOverrides.value[i]
    if (override.remaining === '2h 30m') override.remaining = '2h 15m'
    else if (override.remaining === '2h 15m') override.remaining = '2h'
    else if (override.remaining === '2h') override.remaining = '1h 45m'
    else if (override.remaining === '1h 45m') override.remaining = '1h 30m'
    else if (override.remaining === '1h 30m') override.remaining = '1h 15m'
    else if (override.remaining === '1h 15m') override.remaining = '1h'
    else if (override.remaining === '1h') override.remaining = '45m'
    else if (override.remaining === '45m') override.remaining = '30m'
    else if (override.remaining === '30m') override.remaining = '15m'
    else if (override.remaining === '15m') {
      const zone = lightingZones.value.find(z => z.id === override.zoneId)
      if (zone) {
        zone.status = override.action === 'on' ? 'off' : 'on'
      }
      activeOverrides.value.splice(i, 1)
      i--
    }
  }
}

// Actions
const createOverride = () => {
  if (!newOverride.value.zoneId) {
    ElMessage.warning('Please select a zone')
    return
  }
  const zone = lightingZones.value.find(z => z.id === newOverride.value.zoneId)
  if (!zone) return

  const durationMinutes = parseInt(newOverride.value.duration)
  const now = new Date()
  const endTime = new Date(now.getTime() + durationMinutes * 60 * 1000)
  const endHours = endTime.getHours()
  const endMinutes = endTime.getMinutes()
  const ampm = endHours >= 12 ? 'PM' : 'AM'
  const displayHours = endHours % 12 || 12

  zone.status = newOverride.value.action
  if (newOverride.value.action === 'on' && zone.hasDimming) {
    zone.dimLevel = newOverride.value.dimLevel
  }
  if (newOverride.value.action === 'off') {
    zone.dimLevel = 0
  }

  const remainingMinutes = durationMinutes
  let remainingStr = ''
  if (remainingMinutes >= 60) {
    const hours = Math.floor(remainingMinutes / 60)
    const mins = remainingMinutes % 60
    remainingStr = mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
  } else {
    remainingStr = `${remainingMinutes}m`
  }

  activeOverrides.value.push({
    id: Date.now(),
    zoneId: zone.id,
    zoneName: zone.name,
    action: newOverride.value.action,
    dimLevel: newOverride.value.action === 'on' ? newOverride.value.dimLevel : undefined,
    startTime: now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    endTime: `${displayHours}:${endMinutes.toString().padStart(2, '0')} ${ampm}`,
    remaining: remainingStr,
    reason: newOverride.value.reason || (newOverride.value.action === 'on' ? 'Manual override' : 'Manual shutdown')
  })

  ElMessage.success(`Override applied to ${zone.name} - Turned ${newOverride.value.action.toUpperCase()}`)

  newOverride.value = {
    zoneId: null,
    action: 'on',
    duration: '60',
    customEndTime: '',
    dimLevel: 80,
    reason: ''
  }
}

const cancelOverride = (override: ScheduleOverride) => {
  const zone = lightingZones.value.find(z => z.id === override.zoneId)
  if (zone) {
    zone.status = override.action === 'on' ? 'off' : 'on'
    if (zone.hasDimming && zone.status === 'on') zone.dimLevel = 70
    if (zone.status === 'off') zone.dimLevel = 0
  }
  const index = activeOverrides.value.findIndex(o => o.id === override.id)
  if (index !== -1) activeOverrides.value.splice(index, 1)
  ElMessage.success(`Override cancelled for ${override.zoneName}`)
}

const clearAllOverrides = () => {
  for (const override of activeOverrides.value) {
    const zone = lightingZones.value.find(z => z.id === override.zoneId)
    if (zone) {
      zone.status = override.action === 'on' ? 'off' : 'on'
      if (zone.hasDimming && zone.status === 'on') zone.dimLevel = 70
      if (zone.status === 'off') zone.dimLevel = 0
    }
  }
  activeOverrides.value = []
  ElMessage.success('All overrides cleared')
}

const extendOverride = (override: ScheduleOverride) => {
  extendTarget.value = override
  extendDialogVisible.value = true
}

const confirmExtend = () => {
  if (!extendTarget.value) return
  const extraMinutes = parseInt(extendDuration.value)
  ElMessage.success(`Override extended by ${extraMinutes} minutes for ${extendTarget.value.zoneName}`)
  extendDialogVisible.value = false
  extendTarget.value = null
}

const refreshData = () => {
  updateRemainingTimes()
  ElMessage.success('Data refreshed')
}

const exportReport = () => {
  ElMessage.info('Exporting schedule override report...')
}

const openSettings = () => {
  ElMessage.info('Opening schedule override settings...')
}

const startTimer = () => {
  if (timerInterval) clearInterval(timerInterval)
  timerInterval = setInterval(() => {
    updateRemainingTimes()
  }, 60000)
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
    setTimeout(() => {
      isLoaded.value = true
      startTimer()
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})
</script>

<style scoped>
/* Loading Screen -保持不变 */
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
.schedule-override-page {
  padding: 24px;
  background: linear-gradient(135deg, #f0f4f8 0%, #e8edf3 100%);
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
  flex-wrap: wrap;
  gap: 16px;
}
.title-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  color: white;
  margin-bottom: 12px;
}
.header-title h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 8px 0;
}
.header-title .subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}
.header-actions {
  display: flex;
  gap: 12px;
}
.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e2e8f0;
  background: white;
  color: #475569;
}
.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}
.action-btn.primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  color: white;
}
.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 28px;
}
.stat-card {
  background: white;
  border-radius: 24px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}
.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}
.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}
.stat-icon.blue { background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; }
.stat-icon.green { background: linear-gradient(135deg, #10b981, #059669); color: white; }
.stat-icon.orange { background: linear-gradient(135deg, #f59e0b, #d97706); color: white; }
.stat-icon.purple { background: linear-gradient(135deg, #8b5cf6, #7c3aed); color: white; }
.stat-info { flex: 1; }
.stat-number { font-size: 28px; font-weight: 700; color: #1a1a2e; }
.stat-unit { font-size: 14px; font-weight: 400; color: #64748b; margin-left: 2px; }
.stat-label { font-size: 13px; color: #64748b; margin-top: 4px; }
.stat-change { text-align: right; }
.trend-up { font-size: 13px; font-weight: 600; color: #10b981; }

/* Create Section */
.create-section, .active-section, .history-section {
  background: white;
  border-radius: 24px;
  padding: 24px;
  margin-bottom: 28px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.header-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}
.header-icon.warning { background: linear-gradient(135deg, #f59e0b, #d97706); }
.header-icon.history { background: linear-gradient(135deg, #64748b, #475569); }
.header-left h3 { font-size: 18px; font-weight: 600; color: #1a1a2e; margin: 0; }
.active-count {
  background: #f1f5f9;
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}
.info-badge {
  background: linear-gradient(135deg, #10b981, #059669);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
  color: white;
}

/* Create Form */
.create-form { margin-top: 8px; }
.form-row {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.form-group {
  flex: 1;
  min-width: 200px;
}
.form-group.full { width: 100%; }
.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #475569;
  margin-bottom: 8px;
}
.form-select-custom {
  width: 100%;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
  background: white;
}
.datetime-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
}

/* Action Toggle */
.action-toggle {
  display: flex;
  gap: 12px;
}
.toggle-btn {
  flex: 1;
  padding: 10px 20px;
  border: 2px solid #e2e8f0;
  background: white;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
  transition: all 0.2s;
}
.toggle-btn:hover { border-color: #cbd5e1; background: #f8fafc; }
.toggle-btn.active {
  border-color: #3b82f6;
  background: #eff6ff;
  color: #2563eb;
}
.toggle-btn:last-child.active { border-color: #ef4444; background: #fef2f2; color: #dc2626; }

/* Duration Buttons */
.duration-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.duration-btn {
  padding: 8px 16px;
  border: 1px solid #e2e8f0;
  background: white;
  border-radius: 10px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  color: #475569;
  transition: all 0.2s;
}
.duration-btn:hover { background: #f1f5f9; }
.duration-btn.active {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
}
.duration-btn.custom.active { background: #8b5cf6; border-color: #8b5cf6; }

.dim-slider { width: 100%; margin: 8px 0; }
.slider-marks { display: flex; justify-content: space-between; font-size: 11px; color: #94a3b8; }
.reason-input-custom {
  width: 100%;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
}

.form-actions { margin-top: 24px; }
.apply-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  border-radius: 14px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s;
}
.apply-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

/* Overrides Grid */
.overrides-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}
.override-card {
  background: #f8fafc;
  border-radius: 20px;
  padding: 20px;
  transition: all 0.2s;
  border: 1px solid #e2e8f0;
}
.override-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
.override-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.zone-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 30px;
  font-size: 12px;
  font-weight: 700;
}
.zone-badge.on { background: #dbeafe; color: #1e40af; }
.zone-badge.off { background: #fee2e2; color: #b91c1c; }
.zone-info-header h4 { font-size: 15px; font-weight: 600; color: #1a1a2e; margin: 0 0 2px 0; }
.zone-location { font-size: 11px; color: #94a3b8; }

.override-timer {
  margin-bottom: 16px;
  padding: 12px;
  background: white;
  border-radius: 16px;
}
.time-remaining { margin-bottom: 8px; }
.time-remaining .label { font-size: 11px; color: #94a3b8; display: block; }
.time-remaining .value { font-size: 20px; font-weight: 700; }
.time-remaining .value.critical { color: #ef4444; }
.time-remaining .value.warning { color: #f59e0b; }
.time-range { display: flex; gap: 16px; font-size: 11px; color: #64748b; }
.time-range .el-icon { margin-right: 4px; vertical-align: middle; }

.override-details { margin-bottom: 12px; }
.detail-item { margin-bottom: 8px; }
.detail-label { font-size: 11px; color: #94a3b8; display: block; margin-bottom: 4px; }
.detail-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #e2e8f0;
  border-radius: 20px;
  height: 8px;
  overflow: hidden;
}
.dim-bar {
  height: 100%;
  background: linear-gradient(90deg, #f59e0b, #10b981);
  border-radius: 20px;
}
.detail-value { font-size: 12px; font-weight: 500; color: #1a1a2e; }

.override-footer { margin-bottom: 16px; }
.reason-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #64748b;
  background: #f1f5f9;
  padding: 4px 10px;
  border-radius: 20px;
}

.override-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}
.action-extend, .action-cancel {
  padding: 6px 14px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
  border: none;
}
.action-extend {
  background: #eff6ff;
  color: #2563eb;
}
.action-extend:hover { background: #dbeafe; }
.action-cancel {
  background: #fef2f2;
  color: #dc2626;
}
.action-cancel:hover { background: #fee2e2; }

.empty-state-modern {
  text-align: center;
  padding: 48px 20px;
}
.empty-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  background: #f1f5f9;
  border-radius: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: #94a3b8;
}
.empty-state-modern h4 { font-size: 16px; font-weight: 600; color: #475569; margin: 0 0 8px 0; }
.empty-state-modern p { font-size: 13px; color: #94a3b8; margin: 0; }

/* History Timeline */
.history-timeline { display: flex; flex-direction: column; gap: 20px; }
.history-item {
  display: flex;
  gap: 20px;
}
.history-time {
  min-width: 80px;
  text-align: right;
}
.history-time .time { font-weight: 600; color: #1a1a2e; }
.history-time .date { font-size: 11px; color: #94a3b8; }
.history-line {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}
.line-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #cbd5e1;
  z-index: 1;
}
.line-dot.on { background: #10b981; box-shadow: 0 0 0 3px #d1fae5; }
.line-dot.off { background: #ef4444; box-shadow: 0 0 0 3px #fee2e2; }
.line {
  width: 2px;
  height: 100%;
  background: #e2e8f0;
  position: absolute;
  top: 12px;
}
.history-content {
  flex: 1;
  background: #f8fafc;
  border-radius: 16px;
  padding: 14px 18px;
}
.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.history-header .zone-name { font-weight: 600; color: #1a1a2e; }
.action-tag {
  font-size: 11px;
  padding: 2px 10px;
  border-radius: 20px;
  font-weight: 600;
}
.action-tag.on { background: #dbeafe; color: #1e40af; }
.action-tag.off { background: #fee2e2; color: #b91c1c; }
.history-details {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #64748b;
}
.history-details .el-icon { margin-right: 4px; vertical-align: middle; }

.clear-all-btn, .view-all-btn {
  background: none;
  border: none;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 8px;
  transition: all 0.2s;
}
.clear-all-btn {
  color: #ef4444;
  background: #fef2f2;
}
.clear-all-btn:hover:not(:disabled) { background: #fee2e2; }
.clear-all-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.view-all-btn { color: #3b82f6; }
.view-all-btn:hover { background: #eff6ff; }

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-content {
  background: white;
  border-radius: 24px;
  width: 420px;
  max-width: 90%;
  overflow: hidden;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}
.modal-header h3 { font-size: 18px; font-weight: 600; color: #1a1a2e; margin: 0; }
.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #94a3b8;
}
.modal-body { padding: 24px; }
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #e2e8f0;
}
.extend-zone {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 24px;
  padding: 12px;
  background: #f1f5f9;
  border-radius: 16px;
}
.extend-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
.extend-option {
  padding: 14px;
  border: 2px solid #e2e8f0;
  border-radius: 14px;
  text-align: center;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 500;
  transition: all 0.2s;
}
.extend-option:hover { border-color: #cbd5e1; background: #f8fafc; }
.extend-option.active { border-color: #3b82f6; background: #eff6ff; color: #2563eb; }
.dialog-btn {
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}
.dialog-btn.cancel {
  background: #f1f5f9;
  color: #64748b;
}
.dialog-btn.cancel:hover { background: #e2e8f0; }
.dialog-btn.confirm {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}
.dialog-btn.confirm:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}
</style>