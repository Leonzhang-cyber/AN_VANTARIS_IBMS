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
        <div class="loading-tip">Door Access Control</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Door Open / Close Page Content -->
  <div v-else class="door-control-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <div class="title-badge">
          <el-icon><Lock /></el-icon>
          <span>Access Control</span>
        </div>
        <h1>Door Open / Close</h1>
        <p class="subtitle">Remotely control door access, monitor door status, and manage security permissions</p>
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
        <div class="stat-icon green">
          <el-icon><Unlock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-number">{{ openDoors }}</div>
          <div class="stat-label">Doors Open</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><Lock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-number">{{ closedDoors }}</div>
          <div class="stat-label">Doors Closed</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-number">{{ forcedDoors }}</div>
          <div class="stat-label">Forced Open</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-number">{{ heldDoors }}</div>
          <div class="stat-label">Door Held Open</div>
        </div>
      </div>
    </div>

    <!-- Door Control Grid -->
    <div class="doors-grid">
      <div v-for="door in filteredDoors" :key="door.id" class="door-card" :class="door.status">
        <div class="door-header">
          <div class="door-info">
            <h4>{{ door.name }}</h4>
            <span class="door-location">{{ door.location }}</span>
          </div>
          <div class="door-status-badge" :class="door.status">
            <span class="status-dot"></span>
            <span>{{ getStatusText(door.status) }}</span>
          </div>
        </div>

        <div class="door-stats">
          <div class="stat-row">
            <span class="stat-label">Last Access</span>
            <span class="stat-value">{{ door.lastAccess }}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Access Level</span>
            <span class="stat-value">{{ door.accessLevel }}</span>
          </div>
        </div>

        <div class="door-controls">
          <button
              class="control-btn open"
              :disabled="door.status === 'open'"
              @click="openDoor(door)"
          >
            <el-icon><Unlock /></el-icon>
            <span>Open</span>
          </button>
          <button
              class="control-btn close"
              :disabled="door.status === 'closed'"
              @click="closeDoor(door)"
          >
            <el-icon><Lock /></el-icon>
            <span>Close</span>
          </button>
        </div>

        <div class="door-timer" v-if="door.autoCloseTime">
          <el-icon><Timer /></el-icon>
          <span>Auto-close in {{ door.autoCloseTime }}s</span>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <div class="filter-group">
        <label>Building</label>
        <select v-model="buildingFilter" class="filter-select">
          <option value="all">All Buildings</option>
          <option value="A">Building A</option>
          <option value="B">Building B</option>
          <option value="C">Building C</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Status</label>
        <select v-model="statusFilter" class="filter-select">
          <option value="all">All Status</option>
          <option value="open">Open</option>
          <option value="closed">Closed</option>
          <option value="forced">Forced Open</option>
          <option value="held">Held Open</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Search</label>
        <input type="text" v-model="searchText" placeholder="Search doors..." class="filter-input" />
      </div>
      <button class="batch-btn" @click="openBatchDialog">
        <el-icon><Select /></el-icon>
        Batch Control
      </button>
    </div>

    <!-- Access Events Log -->
    <div class="events-section">
      <div class="section-header">
        <div class="header-left">
          <div class="header-icon"><el-icon><Document /></el-icon></div>
          <h3>Recent Access Events</h3>
        </div>
        <div class="header-right">
          <button class="view-all-btn">View All →</button>
        </div>
      </div>
      <div class="events-timeline">
        <div v-for="event in recentEvents" :key="event.id" class="event-item">
          <div class="event-time">{{ event.time }}</div>
          <div class="event-icon" :class="event.type">
            <el-icon v-if="event.type === 'access'"><User /></el-icon>
            <el-icon v-else-if="event.type === 'open'"><Unlock /></el-icon>
            <el-icon v-else><Lock /></el-icon>
          </div>
          <div class="event-content">
            <div class="event-title">{{ event.title }}</div>
            <div class="event-detail">{{ event.detail }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Batch Control Dialog -->
    <div v-if="batchDialogVisible" class="modal-overlay" @click.self="batchDialogVisible = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Batch Door Control</h3>
          <button class="modal-close" @click="batchDialogVisible = false">×</button>
        </div>
        <div class="modal-body">
          <p>Apply to <strong>{{ filteredDoors.length }}</strong> doors:</p>
          <div class="batch-actions">
            <button class="batch-open-btn" @click="batchOpen">
              <el-icon><Unlock /></el-icon>
              Open All
            </button>
            <button class="batch-close-btn" @click="batchClose">
              <el-icon><Lock /></el-icon>
              Close All
            </button>
          </div>
          <div class="batch-warning">
            <el-icon><Warning /></el-icon>
            <span>This will override current status for all filtered doors</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="dialog-btn cancel" @click="batchDialogVisible = false">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Confirm Dialog -->
    <div v-if="confirmDialogVisible" class="modal-overlay" @click.self="confirmDialogVisible = false">
      <div class="modal-content confirm-dialog">
        <div class="modal-header">
          <h3>Confirm Action</h3>
          <button class="modal-close" @click="confirmDialogVisible = false">×</button>
        </div>
        <div class="modal-body">
          <div class="confirm-icon" :class="confirmAction">
            <el-icon v-if="confirmAction === 'open'"><Unlock /></el-icon>
            <el-icon v-else><Lock /></el-icon>
          </div>
          <p>{{ confirmAction === 'open' ? 'Open' : 'Close' }} door <strong>{{ confirmDoor?.name }}</strong>?</p>
          <p class="confirm-note">This action will be logged for security audit.</p>
        </div>
        <div class="modal-footer">
          <button class="dialog-btn cancel" @click="confirmDialogVisible = false">Cancel</button>
          <button class="dialog-btn confirm" @click="executeDoorAction">Confirm</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Refresh, Download, Setting, Lock, Unlock, Warning, Timer,
  Document, User, Select, Plus, Close
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// Loading State
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = ['Preparing...', 'Loading access controls...', 'Initializing door status...', 'Almost ready...']

// Data Models
interface Door {
  id: number
  name: string
  location: string
  building: string
  status: 'open' | 'closed' | 'forced' | 'held'
  lastAccess: string
  accessLevel: string
  autoCloseTime?: number
}

interface AccessEvent {
  id: number
  time: string
  type: 'access' | 'open' | 'close' | 'forced'
  title: string
  detail: string
}

// State
const buildingFilter = ref('all')
const statusFilter = ref('all')
const searchText = ref('')
const batchDialogVisible = ref(false)
const confirmDialogVisible = ref(false)
const confirmAction = ref<'open' | 'close'>('open')
const confirmDoor = ref<Door | null>(null)

// Mock Data
const doors = ref<Door[]>([
  { id: 1, name: 'Main Entrance', location: 'Building A - Ground Floor', building: 'A', status: 'closed', lastAccess: '08:32 AM', accessLevel: 'All Employees' },
  { id: 2, name: 'North Wing Door', location: 'Building A - Floor 1', building: 'A', status: 'open', lastAccess: '09:15 AM', accessLevel: 'Staff Only', autoCloseTime: 30 },
  { id: 3, name: 'South Wing Door', location: 'Building A - Floor 1', building: 'A', status: 'closed', lastAccess: '08:45 AM', accessLevel: 'Staff Only' },
  { id: 4, name: 'Executive Office', location: 'Building A - Floor 2', building: 'A', status: 'closed', lastAccess: '09:00 AM', accessLevel: 'Executives' },
  { id: 5, name: 'Server Room', location: 'Building B - Ground Floor', building: 'B', status: 'closed', lastAccess: '07:30 AM', accessLevel: 'IT Admin' },
  { id: 6, name: 'IT Department', location: 'Building B - Floor 1', building: 'B', status: 'open', lastAccess: '10:00 AM', accessLevel: 'IT Staff', autoCloseTime: 45 },
  { id: 7, name: 'Emergency Exit East', location: 'Building B - Floor 1', building: 'B', status: 'forced', lastAccess: '08:15 AM', accessLevel: 'Emergency Only' },
  { id: 8, name: 'Warehouse Door', location: 'Building C - Ground Floor', building: 'C', status: 'held', lastAccess: '06:30 AM', accessLevel: 'Warehouse Staff' },
  { id: 9, name: 'Loading Dock', location: 'Building C - Ground Floor', building: 'C', status: 'closed', lastAccess: '07:00 AM', accessLevel: 'Logistics' },
  { id: 10, name: 'Security Office', location: 'Building C - Floor 1', building: 'C', status: 'closed', lastAccess: '08:00 AM', accessLevel: 'Security' }
])

const recentEvents = ref<AccessEvent[]>([
  { id: 1, time: '10:32:15', type: 'access', title: 'Access Granted', detail: 'John Smith - Main Entrance (Badge #1245)' },
  { id: 2, time: '10:28:42', type: 'open', title: 'Door Opened', detail: 'North Wing Door - Remote command' },
  { id: 3, time: '10:15:00', type: 'close', title: 'Door Closed', detail: 'Server Room - Auto-close triggered' },
  { id: 4, time: '09:45:22', type: 'forced', title: 'Forced Entry', detail: 'Emergency Exit East - Alarm triggered' },
  { id: 5, time: '09:30:10', type: 'access', title: 'Access Denied', detail: 'Unauthorized attempt - Executive Office' }
])

// Computed
const openDoors = computed(() => doors.value.filter(d => d.status === 'open').length)
const closedDoors = computed(() => doors.value.filter(d => d.status === 'closed').length)
const forcedDoors = computed(() => doors.value.filter(d => d.status === 'forced').length)
const heldDoors = computed(() => doors.value.filter(d => d.status === 'held').length)

const filteredDoors = computed(() => {
  let result = [...doors.value]
  if (buildingFilter.value !== 'all') {
    result = result.filter(d => d.building === buildingFilter.value)
  }
  if (statusFilter.value !== 'all') {
    result = result.filter(d => d.status === statusFilter.value)
  }
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(d => d.name.toLowerCase().includes(search) || d.location.toLowerCase().includes(search))
  }
  return result
})

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    open: 'Open',
    closed: 'Closed',
    forced: 'Forced Open',
    held: 'Held Open'
  }
  return map[status] || status
}

// Actions
const openDoor = (door: Door) => {
  confirmAction.value = 'open'
  confirmDoor.value = door
  confirmDialogVisible.value = true
}

const closeDoor = (door: Door) => {
  confirmAction.value = 'close'
  confirmDoor.value = door
  confirmDialogVisible.value = true
}

const executeDoorAction = () => {
  if (!confirmDoor.value) return

  if (confirmAction.value === 'open') {
    confirmDoor.value.status = 'open'
    confirmDoor.value.autoCloseTime = 30
    ElMessage.success(`${confirmDoor.value.name} opened successfully`)
    recentEvents.value.unshift({
      id: Date.now(),
      time: new Date().toLocaleTimeString(),
      type: 'open',
      title: 'Door Opened',
      detail: `${confirmDoor.value.name} - Remote command by operator`
    })
  } else {
    confirmDoor.value.status = 'closed'
    confirmDoor.value.autoCloseTime = undefined
    ElMessage.success(`${confirmDoor.value.name} closed successfully`)
    recentEvents.value.unshift({
      id: Date.now(),
      time: new Date().toLocaleTimeString(),
      type: 'close',
      title: 'Door Closed',
      detail: `${confirmDoor.value.name} - Remote command by operator`
    })
  }
  confirmDialogVisible.value = false
  confirmDoor.value = null
}

const batchOpen = () => {
  filteredDoors.value.forEach(door => {
    door.status = 'open'
    door.autoCloseTime = 30
  })
  ElMessage.success(`${filteredDoors.value.length} doors opened`)
  batchDialogVisible.value = false
  recentEvents.value.unshift({
    id: Date.now(),
    time: new Date().toLocaleTimeString(),
    type: 'open',
    title: 'Batch Door Open',
    detail: `${filteredDoors.value.length} doors opened via batch control`
  })
}

const batchClose = () => {
  filteredDoors.value.forEach(door => {
    door.status = 'closed'
    door.autoCloseTime = undefined
  })
  ElMessage.success(`${filteredDoors.value.length} doors closed`)
  batchDialogVisible.value = false
  recentEvents.value.unshift({
    id: Date.now(),
    time: new Date().toLocaleTimeString(),
    type: 'close',
    title: 'Batch Door Close',
    detail: `${filteredDoors.value.length} doors closed via batch control`
  })
}

const openBatchDialog = () => {
  batchDialogVisible.value = true
}

const refreshData = () => {
  ElMessage.success('Door status refreshed')
}

const exportReport = () => {
  ElMessage.info('Exporting door access report...')
}

const openSettings = () => {
  ElMessage.info('Opening door control settings...')
}

// Auto-close timer simulation
let autoCloseInterval: ReturnType<typeof setInterval> | null = null

const startAutoCloseTimer = () => {
  if (autoCloseInterval) clearInterval(autoCloseInterval)
  autoCloseInterval = setInterval(() => {
    doors.value.forEach(door => {
      if (door.status === 'open' && door.autoCloseTime && door.autoCloseTime > 0) {
        door.autoCloseTime -= 5
        if (door.autoCloseTime <= 0) {
          door.status = 'closed'
          door.autoCloseTime = undefined
          recentEvents.value.unshift({
            id: Date.now(),
            time: new Date().toLocaleTimeString(),
            type: 'close',
            title: 'Auto-Close',
            detail: `${door.name} - Auto-closed after timeout`
          })
        }
      }
    })
  }, 5000)
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
      startAutoCloseTimer()
    }, 400)
  }, 2000)
})
</script>

<style scoped>
/* Loading Screen */
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
.door-control-page {
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
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
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
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border: none;
  color: white;
}
.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
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
.stat-icon.green { background: linear-gradient(135deg, #10b981, #059669); color: white; }
.stat-icon.blue { background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; }
.stat-icon.orange { background: linear-gradient(135deg, #f59e0b, #d97706); color: white; }
.stat-icon.purple { background: linear-gradient(135deg, #8b5cf6, #7c3aed); color: white; }
.stat-info { flex: 1; }
.stat-number { font-size: 28px; font-weight: 700; color: #1a1a2e; }
.stat-label { font-size: 13px; color: #64748b; margin-top: 4px; }

/* Doors Grid */
.doors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
  margin-bottom: 28px;
}
.door-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  transition: all 0.2s;
  border-left: 4px solid #cbd5e1;
}
.door-card.open { border-left-color: #10b981; }
.door-card.closed { border-left-color: #3b82f6; }
.door-card.forced { border-left-color: #ef4444; }
.door-card.held { border-left-color: #f59e0b; }
.door-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}
.door-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}
.door-info h4 { font-size: 16px; font-weight: 600; color: #1a1a2e; margin: 0 0 4px 0; }
.door-location { font-size: 12px; color: #64748b; }
.door-status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}
.door-status-badge.open { background: #d1fae5; color: #059669; }
.door-status-badge.closed { background: #dbeafe; color: #1d4ed8; }
.door-status-badge.forced { background: #fee2e2; color: #dc2626; }
.door-status-badge.held { background: #fef3c7; color: #d97706; }
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.door-status-badge.open .status-dot { background: #10b981; }
.door-status-badge.closed .status-dot { background: #3b82f6; }
.door-status-badge.forced .status-dot { background: #ef4444; }
.door-status-badge.held .status-dot { background: #f59e0b; }

.door-stats {
  background: #f8fafc;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 16px;
}
.stat-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}
.stat-row:last-child { margin-bottom: 0; }
.stat-label { font-size: 12px; color: #64748b; }
.stat-value { font-size: 13px; font-weight: 500; color: #1a1a2e; }

.door-controls {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}
.control-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}
.control-btn.open {
  background: #10b981;
  color: white;
}
.control-btn.open:hover:not(:disabled) { background: #059669; }
.control-btn.close {
  background: #3b82f6;
  color: white;
}
.control-btn.close:hover:not(:disabled) { background: #1d4ed8; }
.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.door-timer {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #f59e0b;
  background: #fef3c7;
  padding: 6px 10px;
  border-radius: 10px;
}

/* Filters Bar */
.filters-bar {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 28px;
  padding: 16px 20px;
  background: white;
  border-radius: 16px;
  align-items: flex-end;
}
.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.filter-group label {
  font-size: 12px;
  font-weight: 500;
  color: #64748b;
}
.filter-select, .filter-input {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 13px;
  background: white;
  min-width: 140px;
}
.batch-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  border: none;
  border-radius: 10px;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.batch-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}

/* Events Section */
.events-section {
  background: white;
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.header-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #64748b, #475569);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}
.header-left h3 { font-size: 18px; font-weight: 600; color: #1a1a2e; margin: 0; }
.view-all-btn {
  background: none;
  border: none;
  color: #3b82f6;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 8px;
}
.view-all-btn:hover { background: #eff6ff; }

.events-timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.event-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 14px;
}
.event-time {
  font-size: 12px;
  font-weight: 500;
  color: #64748b;
  min-width: 70px;
}
.event-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}
.event-icon.access { background: #dbeafe; color: #3b82f6; }
.event-icon.open { background: #d1fae5; color: #10b981; }
.event-icon.close { background: #fee2e2; color: #ef4444; }
.event-icon.forced { background: #fef3c7; color: #f59e0b; }
.event-content { flex: 1; }
.event-title { font-weight: 600; color: #1a1a2e; margin-bottom: 2px; }
.event-detail { font-size: 12px; color: #64748b; }

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
.modal-body { padding: 24px; text-align: center; }
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #e2e8f0;
}

.batch-actions {
  display: flex;
  gap: 16px;
  margin: 20px 0;
}
.batch-open-btn, .batch-close-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  border: none;
}
.batch-open-btn {
  background: #10b981;
  color: white;
}
.batch-close-btn {
  background: #3b82f6;
  color: white;
}
.batch-warning {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: #fef3c7;
  border-radius: 12px;
  font-size: 12px;
  color: #d97706;
}

.confirm-dialog .modal-body { padding: 24px; }
.confirm-icon {
  width: 60px;
  height: 60px;
  margin: 0 auto 16px;
  border-radius: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}
.confirm-icon.open { background: #d1fae5; color: #10b981; }
.confirm-icon.close { background: #fee2e2; color: #ef4444; }
.confirm-note { font-size: 12px; color: #64748b; margin-top: 12px; }

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
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
}
.dialog-btn.confirm:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}
</style>