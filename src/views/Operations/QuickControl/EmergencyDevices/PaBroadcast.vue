<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
  RefreshRight, Warning, CircleCheck, Clock,
  Monitor, Tools, Search, Setting,
  Operation, AlarmClock, Document,
  Grid, List, DataLine, Mic,
  VideoPlay, VideoPause, Download,
  Message, Bell, Loading, User,
  Microphone
} from "@element-plus/icons-vue"
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Initializing PA system...',
  'Connecting to audio zones...',
  'Loading broadcast schedules...',
  'Ready for operation...'
]

// System status
const systemStatus = ref({
  overallHealth: 98,
  onlineZones: 12,
  totalZones: 12,
  activeBroadcasts: 1,
  lastSystemTest: '2025-01-15 14:30:00',
  microphoneStatus: 'ready'
})

// Audio Zones
const audioZones = ref([
  { id: 'zone-1', name: 'Lobby', status: 'active', speakerCount: 8, volume: 75, emergencyEnabled: true, description: 'Main entrance and reception area' },
  { id: 'zone-2', name: 'Ground Floor - East Wing', status: 'active', speakerCount: 12, volume: 70, emergencyEnabled: true, description: 'East corridor and offices' },
  { id: 'zone-3', name: 'Ground Floor - West Wing', status: 'active', speakerCount: 10, volume: 70, emergencyEnabled: true, description: 'West corridor and meeting rooms' },
  { id: 'zone-4', name: 'First Floor - North', status: 'active', speakerCount: 14, volume: 72, emergencyEnabled: true, description: 'North offices and break room' },
  { id: 'zone-5', name: 'First Floor - South', status: 'active', speakerCount: 11, volume: 72, emergencyEnabled: true, description: 'South offices and storage' },
  { id: 'zone-6', name: 'Server Room', status: 'active', speakerCount: 2, volume: 80, emergencyEnabled: true, description: 'Critical infrastructure area' },
  { id: 'zone-7', name: 'Data Center', status: 'active', speakerCount: 4, volume: 80, emergencyEnabled: true, description: 'Server halls and IT areas' },
  { id: 'zone-8', name: 'Cafeteria', status: 'active', speakerCount: 6, volume: 65, emergencyEnabled: true, description: 'Staff dining area' },
  { id: 'zone-9', name: 'Conference Center', status: 'inactive', speakerCount: 8, volume: 60, emergencyEnabled: true, description: 'Meeting rooms and auditorium' },
  { id: 'zone-10', name: 'Parking Garage', status: 'active', speakerCount: 16, volume: 85, emergencyEnabled: true, description: 'B1 and B2 parking levels' },
  { id: 'zone-11', name: 'Loading Dock', status: 'active', speakerCount: 5, volume: 85, emergencyEnabled: true, description: 'Shipping and receiving' },
  { id: 'zone-12', name: 'Emergency Stairwells', status: 'active', speakerCount: 9, volume: 90, emergencyEnabled: true, description: 'All emergency exit stairwells' }
])

// Pre-recorded messages
const prerecordedMessages = ref([
  { id: 'msg-1', name: 'Opening Announcement', duration: '0:45', type: 'Welcome', lastUsed: '2025-01-15' },
  { id: 'msg-2', name: 'Closing Announcement', duration: '0:30', type: 'Farewell', lastUsed: '2025-01-14' },
  { id: 'msg-3', name: 'Fire Drill Alert', duration: '0:20', type: 'Emergency', lastUsed: '2025-01-10' },
  { id: 'msg-4', name: 'Weather Advisory', duration: '0:25', type: 'Alert', lastUsed: '2025-01-12' },
  { id: 'msg-5', name: 'Security Alert', duration: '0:15', type: 'Emergency', lastUsed: '2025-01-08' },
  { id: 'msg-6', name: 'Maintenance Notice', duration: '0:20', type: 'Info', lastUsed: '2025-01-13' }
])

// Broadcast history
const broadcastHistory = ref([
  { id: 'brd-1', time: '09:00:00', date: '2025-01-16', zone: 'All Zones', message: 'Morning Announcement', duration: '0:45', operator: 'System' },
  { id: 'brd-2', time: '12:00:00', date: '2025-01-16', zone: 'Cafeteria', message: 'Lunch Service', duration: '0:15', operator: 'Admin' },
  { id: 'brd-3', time: '14:30:00', date: '2025-01-16', zone: 'Conference Center', message: 'Meeting Reminder', duration: '0:10', operator: 'Admin' },
  { id: 'brd-4', time: '10:00:00', date: '2025-01-15', zone: 'All Zones', message: 'Fire Drill Test', duration: '0:20', operator: 'System' }
])

// Live broadcast state
const isBroadcasting = ref(false)
const selectedZones = ref<string[]>([])
const broadcastMode = ref<'live' | 'prerecorded'>('live')
const selectedMessage = ref<any>(null)
const broadcastText = ref('')
const broadcastVolume = ref(75)
const broadcastDuration = ref(0)
const countdown = ref(0)

// Recording state
const isRecording = ref(false)
const recordingDuration = ref(0)
const recordingTimer = ref<any>(null)

// UI State
const showHistory = ref(false)
const showSchedules = ref(false)
const searchKeyword = ref('')

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

const filteredZones = computed(() => {
  if (!searchKeyword.value) return audioZones.value
  return audioZones.value.filter(z =>
      z.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      z.description.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

const toggleZone = (zoneId: string) => {
  const index = selectedZones.value.indexOf(zoneId)
  if (index === -1) {
    selectedZones.value.push(zoneId)
  } else {
    selectedZones.value.splice(index, 1)
  }
}

const selectAllZones = () => {
  if (selectedZones.value.length === audioZones.value.length) {
    selectedZones.value = []
  } else {
    selectedZones.value = audioZones.value.map(z => z.id)
  }
}

const startLiveBroadcast = () => {
  if (selectedZones.value.length === 0) {
    ElMessage.warning('Please select at least one zone')
    return
  }

  if (!broadcastText.value.trim()) {
    ElMessage.warning('Please enter announcement text')
    return
  }

  ElMessageBox.confirm(
      `Start live broadcast to ${selectedZones.value.length} zone(s)?\n\nText: "${broadcastText.value}"\nVolume: ${broadcastVolume.value}%`,
      'Confirm Broadcast',
      {
        confirmButtonText: 'Start Broadcast',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    isBroadcasting.value = true
    countdown.value = 3

    const countdownInterval = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(countdownInterval)
        ElMessage.success(`Broadcasting to ${selectedZones.value.length} zone(s)...`)

        // Simulate broadcast
        setTimeout(() => {
          stopBroadcast()
          ElMessage.success('Broadcast completed')

          // Add to history
          broadcastHistory.value.unshift({
            id: `brd-${Date.now()}`,
            time: new Date().toLocaleTimeString(),
            date: new Date().toISOString().split('T')[0],
            zone: selectedZones.value.length === audioZones.value.length ? 'All Zones' : `${selectedZones.value.length} zones`,
            message: broadcastText.value.substring(0, 50),
            duration: `${Math.ceil(broadcastText.value.length / 10)}s`,
            operator: 'Live'
          })
        }, 3000)
      }
    }, 1000)
  }).catch(() => {})
}

const startPrerecordedBroadcast = () => {
  if (selectedZones.value.length === 0) {
    ElMessage.warning('Please select at least one zone')
    return
  }

  if (!selectedMessage.value) {
    ElMessage.warning('Please select a message')
    return
  }

  ElMessageBox.confirm(
      `Play "${selectedMessage.value.name}" to ${selectedZones.value.length} zone(s)?`,
      'Confirm Broadcast',
      {
        confirmButtonText: 'Play',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    isBroadcasting.value = true
    ElMessage.success(`Playing "${selectedMessage.value.name}"...`)

    // Simulate playback
    setTimeout(() => {
      stopBroadcast()
      ElMessage.success('Message playback completed')

      broadcastHistory.value.unshift({
        id: `brd-${Date.now()}`,
        time: new Date().toLocaleTimeString(),
        date: new Date().toISOString().split('T')[0],
        zone: selectedZones.value.length === audioZones.value.length ? 'All Zones' : `${selectedZones.value.length} zones`,
        message: selectedMessage.value.name,
        duration: selectedMessage.value.duration,
        operator: 'System'
      })
    }, 3000)
  }).catch(() => {})
}

const stopBroadcast = () => {
  isBroadcasting.value = false
  countdown.value = 0
  broadcastText.value = ''
  selectedMessage.value = null
  selectedZones.value = []
}

const emergencyBroadcast = () => {
  ElMessageBox.confirm(
      'EMERGENCY BROADCAST: This will override all ongoing broadcasts and play the emergency alert tone to ALL zones.\n\nAre you sure?',
      'Emergency Broadcast',
      {
        confirmButtonText: 'EMERGENCY ACTIVATE',
        cancelButtonText: 'Cancel',
        type: 'error'
      }
  ).then(() => {
    isBroadcasting.value = true
    ElMessage.error('EMERGENCY BROADCAST ACTIVATED - Alert tone playing to all zones')

    // Simulate emergency broadcast
    setTimeout(() => {
      stopBroadcast()
      ElMessage.success('Emergency broadcast completed')
    }, 5000)
  }).catch(() => {})
}

const startRecording = () => {
  ElMessageBox.confirm(
      'Start recording audio message? Maximum recording time: 60 seconds.',
      'Start Recording',
      {
        confirmButtonText: 'Start',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    isRecording.value = true
    recordingDuration.value = 0

    recordingTimer.value = setInterval(() => {
      recordingDuration.value++
      if (recordingDuration.value >= 60) {
        stopRecording()
      }
    }, 1000)

    ElMessage.info('Recording started... Speak into microphone')
  }).catch(() => {})
}

const stopRecording = () => {
  if (recordingTimer.value) {
    clearInterval(recordingTimer.value)
    recordingTimer.value = null
  }

  isRecording.value = false

  ElMessageBox.confirm(
      `Recording stopped (${recordingDuration.value} seconds). Save this message?`,
      'Save Recording',
      {
        confirmButtonText: 'Save',
        cancelButtonText: 'Discard',
        type: 'info'
      }
  ).then(() => {
    const newMessage = {
      id: `msg-${Date.now()}`,
      name: `Custom Message ${prerecordedMessages.value.length + 1}`,
      duration: `${Math.floor(recordingDuration.value / 60)}:${(recordingDuration.value % 60).toString().padStart(2, '0')}`,
      type: 'Custom',
      lastUsed: new Date().toISOString().split('T')[0]
    }
    prerecordedMessages.value.unshift(newMessage)
    ElMessage.success('Recording saved to message library')
  }).catch(() => {})
  recordingDuration.value = 0
}

const adjustVolume = (zone: any, value: number) => {
  zone.volume = value
  ElMessage.success(`${zone.name} volume set to ${value}%`)
}

const refreshData = () => {
  ElMessage.info('Refreshing PA system data...')
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
        <div class="loading-tip">Public Address System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="pa-broadcast">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Public Address System</h2>
        <p class="subtitle">Centralized audio broadcasting and zone management</p>
      </div>
      <div class="header-actions">
        <el-button type="danger" @click="emergencyBroadcast" :disabled="isBroadcasting">
          <el-icon><Bell /></el-icon> Emergency Alert
        </el-button>
        <el-button @click="showHistory = true">
          <el-icon><Document /></el-icon> History
        </el-button>
        <el-button type="primary" @click="refreshData">
          <el-icon><RefreshRight /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- System Status -->
    <div class="status-banner">
      <div class="status-icon">🎙️</div>
      <div class="status-info">
        <div class="status-title">PA System Status: Operational</div>
        <div class="status-desc">{{ systemStatus.onlineZones }}/{{ systemStatus.totalZones }} zones online • Microphone ready</div>
      </div>
      <div class="status-badge healthy">All Systems Go</div>
    </div>

    <!-- Broadcast Control Panel -->
    <div class="broadcast-panel">
      <div class="panel-header">
        <span class="panel-title">
          <el-icon><Mic /></el-icon> Broadcast Controller
        </span>
        <div class="mode-switch">
          <el-radio-group v-model="broadcastMode" size="small">
            <el-radio-button label="live">Live Broadcast</el-radio-button>
            <el-radio-button label="prerecorded">Prerecorded</el-radio-button>
          </el-radio-group>
        </div>
      </div>

      <!-- Live Broadcast Mode -->
      <div v-if="broadcastMode === 'live'" class="live-broadcast">
        <div class="broadcast-input">
          <el-input
              v-model="broadcastText"
              type="textarea"
              :rows="3"
              placeholder="Enter announcement text to broadcast..."
              :disabled="isBroadcasting"
          />
        </div>
        <div class="broadcast-controls">
          <div class="control-group">
            <label>Volume: {{ broadcastVolume }}%</label>
            <el-slider v-model="broadcastVolume" :min="0" :max="100" :disabled="isBroadcasting" />
          </div>
          <div class="control-group">
            <el-button
                type="primary"
                size="large"
                @click="startLiveBroadcast"
                :disabled="isBroadcasting || !broadcastText.trim()"
            >
              <el-icon><Microphone /></el-icon> Start Live Broadcast
            </el-button>
          </div>
        </div>
      </div>

      <!-- Prerecorded Mode -->
      <div v-else class="prerecorded-broadcast">
        <div class="message-selector">
          <el-select
              v-model="selectedMessage"
              placeholder="Select prerecorded message"
              value-key="id"
              :disabled="isBroadcasting"
              style="width: 100%"
          >
            <el-option
                v-for="msg in prerecordedMessages"
                :key="msg.id"
                :label="`${msg.name} (${msg.duration}) - ${msg.type}`"
                :value="msg"
            />
          </el-select>
          <el-button type="primary" @click="startPrerecordedBroadcast" :disabled="isBroadcasting || !selectedMessage">
            <el-icon><VideoPlay /></el-icon> Play Message
          </el-button>
          <el-button type="success" @click="startRecording" :disabled="isRecording || isBroadcasting">
            <el-icon><Mic /></el-icon> {{ isRecording ? `Recording: ${recordingDuration}s` : 'Record Message' }}
          </el-button>
        </div>
      </div>

      <!-- Broadcast Status -->
      <div v-if="isBroadcasting" class="broadcast-status">
        <div v-if="countdown > 0" class="countdown">
          Broadcast starting in... <span class="countdown-number">{{ countdown }}</span>
        </div>
        <div v-else class="broadcasting">
          <div class="pulse"></div>
          <span>LIVE BROADCAST IN PROGRESS...</span>
        </div>
        <el-button type="danger" size="small" @click="stopBroadcast">Stop</el-button>
      </div>
    </div>

    <!-- Selected Zones Summary -->
    <div class="selection-summary" v-if="selectedZones.length > 0">
      <span class="summary-label">Selected zones:</span>
      <span class="summary-count">{{ selectedZones.length }} zones selected</span>
      <el-button size="small" @click="selectAllZones">Deselect All</el-button>
    </div>

    <!-- Zones Grid -->
    <div class="zones-grid">
      <div v-for="zone in filteredZones" :key="zone.id" class="zone-card" :class="zone.status">
        <div class="zone-header">
          <div class="zone-select">
            <el-checkbox
                :model-value="selectedZones.includes(zone.id)"
                @change="toggleZone(zone.id)"
                :disabled="isBroadcasting"
            />
          </div>
          <div class="zone-info">
            <div class="zone-name">{{ zone.name }}</div>
            <div class="zone-description">{{ zone.description }}</div>
          </div>
          <div class="zone-status">
            <span class="status-dot" :style="{ background: getStatusColor(zone.status) }"></span>
            <span>{{ getStatusText(zone.status) }}</span>
          </div>
        </div>
        <div class="zone-details">
          <div class="zone-stat">
            <span class="stat-label">Speakers</span>
            <span class="stat-value">{{ zone.speakerCount }}</span>
          </div>
          <div class="zone-stat">
            <span class="stat-label">Volume</span>
            <div class="volume-control">
              <el-slider
                  v-model="zone.volume"
                  :min="0"
                  :max="100"
                  size="small"
                  :disabled="isBroadcasting"
                  @change="adjustVolume(zone, zone.volume)"
              />
            </div>
          </div>
          <div class="zone-stat">
            <span class="stat-label">Emergency</span>
            <el-tag :type="zone.emergencyEnabled ? 'danger' : 'info'" size="small">
              {{ zone.emergencyEnabled ? 'Enabled' : 'Disabled' }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- Broadcast History Dialog -->
    <el-dialog v-model="showHistory" title="Broadcast History" width="700px">
      <el-table :data="broadcastHistory" stripe>
        <el-table-column prop="date" label="Date" width="110" />
        <el-table-column prop="time" label="Time" width="100" />
        <el-table-column prop="zone" label="Zone" min-width="140" />
        <el-table-column prop="message" label="Message" min-width="180" />
        <el-table-column prop="duration" label="Duration" width="90" />
        <el-table-column prop="operator" label="Operator" width="100" />
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
.pa-broadcast {
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
  background: linear-gradient(135deg, #1a73e8, #0d47a1);
  border-radius: 16px;
  padding: 20px 24px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  color: white;
  flex-wrap: wrap;
}

.status-icon { font-size: 32px; }
.status-info { flex: 1; }
.status-title { font-weight: 600; font-size: 18px; margin-bottom: 4px; }
.status-desc { font-size: 13px; opacity: 0.9; }
.status-badge { padding: 6px 16px; background: rgba(255,255,255,0.2); border-radius: 20px; font-size: 13px; font-weight: 500; }
.status-badge.healthy { background: rgba(103, 194, 58, 0.3); }

/* Broadcast Panel */
.broadcast-panel {
  background: white;
  border-radius: 20px;
  margin-bottom: 24px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.live-broadcast, .prerecorded-broadcast {
  padding: 20px;
}

.broadcast-input { margin-bottom: 20px; }

.broadcast-controls {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.control-group label { font-size: 13px; color: #606266; margin-bottom: 8px; display: block; }

.message-selector {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.message-selector .el-select { flex: 1; min-width: 250px; }

.broadcast-status {
  padding: 16px 20px;
  background: #f0f7ff;
  border-top: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.countdown { font-size: 16px; font-weight: 500; }
.countdown-number { font-size: 24px; font-weight: 700; color: #409EFF; margin-left: 8px; }

.broadcasting { display: flex; align-items: center; gap: 12px; }
.pulse { width: 12px; height: 12px; background: #F56C6C; border-radius: 50%; animation: pulse-red 1s infinite; }
@keyframes pulse-red { 0% { opacity: 1; transform: scale(1); } 100% { opacity: 0; transform: scale(2); } }

/* Selection Summary */
.selection-summary {
  background: #ecf5ff;
  border-radius: 12px;
  padding: 12px 20px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.summary-label { font-weight: 600; }
.summary-count { color: #409EFF; font-weight: 600; }

/* Zones Grid */
.zones-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 16px;
}

.zone-card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
  border-left: 4px solid #67C23A;
}

.zone-card.inactive { border-left-color: #F56C6C; }
.zone-card.warning { border-left-color: #E6A23C; }

.zone-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1); }

.zone-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.zone-info { flex: 1; }
.zone-name { font-size: 16px; font-weight: 600; margin-bottom: 4px; }
.zone-description { font-size: 12px; color: #909399; }

.zone-status { display: flex; align-items: center; gap: 6px; font-size: 13px; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; }

.zone-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.zone-stat { display: flex; flex-direction: column; gap: 4px; }
.zone-stat .stat-label { font-size: 11px; color: #909399; }
.zone-stat .stat-value { font-size: 14px; font-weight: 600; }

.volume-control { width: 100px; }

/* Responsive */
@media (max-width: 768px) {
  .pa-broadcast { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .zones-grid { grid-template-columns: 1fr; }
  .message-selector { flex-direction: column; }
  .message-selector .el-select { width: 100%; }
  .zone-details { grid-template-columns: 1fr; gap: 8px; }
}
</style>