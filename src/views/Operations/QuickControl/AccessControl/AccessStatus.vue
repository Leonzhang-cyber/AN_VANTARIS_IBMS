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
        <div class="loading-tip">Access Status</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Access Status Page Content -->
  <div v-else class="access-status-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <div class="title-badge">
          <el-icon><Key /></el-icon>
          <span>Access Control</span>
        </div>
        <h1>Access Status</h1>
        <p class="subtitle">Real-time monitoring of door access points, security status, and access events</p>
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
        <div class="stat-change">
          <span class="trend-up">+{{ todayOpen }}</span>
          <span class="trend-label">today</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><Lock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-number">{{ securedDoors }}</div>
          <div class="stat-label">Doors Secured</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><WarningFilled /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-number">{{ alertDoors }}</div>
          <div class="stat-label">Alert/Forced</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-number">{{ activeUsers }}</div>
          <div class="stat-label">Active Users</div>
        </div>
      </div>
    </div>

    <!-- Door Status Grid -->
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
            <span class="stat-label">Last User</span>
            <span class="stat-value">{{ door.lastUser }}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Access Method</span>
            <span class="stat-value">{{ door.accessMethod }}</span>
          </div>
        </div>

        <div class="door-progress">
          <div class="progress-label">Battery Level</div>
          <div class="progress-bar-container">
            <div class="progress-fill" :style="{ width: door.battery + '%', background: getBatteryColor(door.battery) }"></div>
            <span class="progress-value">{{ door.battery }}%</span>
          </div>
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
          <option value="locked">Locked</option>
          <option value="forced">Forced</option>
          <option value="maintenance">Maintenance</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Search</label>
        <input type="text" v-model="searchText" placeholder="Search by door or user..." class="filter-input" />
      </div>
    </div>

    <!-- Access Events Log -->
    <div class="events-section">
      <div class="section-header">
        <div class="header-left">
          <div class="header-icon"><el-icon><Document /></el-icon></div>
          <h3>Recent Access Events</h3>
          <span class="event-count">{{ recentEvents.length }} events</span>
        </div>
        <div class="header-right">
          <button class="view-all-btn">View Full Log →</button>
        </div>
      </div>
      <div class="events-timeline">
        <div v-for="event in recentEvents" :key="event.id" class="event-item">
          <div class="event-time">{{ event.time }}</div>
          <div class="event-icon" :class="event.result">
            <el-icon v-if="event.result === 'granted'"><SuccessFilled /></el-icon>
            <el-icon v-else><CircleCloseFilled /></el-icon>
          </div>
          <div class="event-content">
            <div class="event-title">{{ event.title }}</div>
            <div class="event-detail">{{ event.detail }}</div>
            <div class="event-meta">
              <span class="event-user"><el-icon><User /></el-icon> {{ event.user }}</span>
              <span class="event-door"><el-icon><Lock /></el-icon> {{ event.door }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Access Level Summary -->
    <div class="access-levels-section">
      <div class="section-header">
        <div class="header-left">
          <div class="header-icon"><el-icon><Medal /></el-icon></div>
          <h3>Access Levels Summary</h3>
        </div>
      </div>
      <div class="levels-grid">
        <div v-for="level in accessLevels" :key="level.name" class="level-card">
          <div class="level-header">
            <span class="level-name">{{ level.name }}</span>
            <span class="level-count">{{ level.count }} users</span>
          </div>
          <div class="level-doors">
            <span class="level-label">Accessible Doors:</span>
            <div class="door-tags">
              <span v-for="door in level.doors" :key="door" class="door-tag">{{ door }}</span>
            </div>
          </div>
          <div class="level-progress">
            <el-progress :percentage="level.usage" :color="getUsageColor(level.usage)" :stroke-width="6" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Refresh, Download, Key, Unlock, Lock, WarningFilled, User,
  Document, SuccessFilled, CircleCloseFilled, Medal
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// Loading State
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = ['Preparing...', 'Loading access controls...', 'Fetching door status...', 'Almost ready...']

// Data Models
interface AccessDoor {
  id: number
  name: string
  location: string
  building: string
  status: 'open' | 'closed' | 'locked' | 'forced' | 'maintenance'
  lastAccess: string
  lastUser: string
  accessMethod: string
  battery: number
}

interface AccessEvent {
  id: number
  time: string
  result: 'granted' | 'denied'
  title: string
  detail: string
  user: string
  door: string
}

interface AccessLevel {
  name: string
  count: number
  doors: string[]
  usage: number
}

// State
const buildingFilter = ref('all')
const statusFilter = ref('all')
const searchText = ref('')
let refreshInterval: ReturnType<typeof setInterval> | null = null

// Mock Data
const doors = ref<AccessDoor[]>([
  { id: 1, name: 'Main Entrance', location: 'Building A - Ground Floor', building: 'A', status: 'closed', lastAccess: '08:32 AM', lastUser: 'John Smith', accessMethod: 'Badge', battery: 98 },
  { id: 2, name: 'North Wing Door', location: 'Building A - Floor 1', building: 'A', status: 'open', lastAccess: '09:15 AM', lastUser: 'Sarah Chen', accessMethod: 'Badge', battery: 95 },
  { id: 3, name: 'South Wing Door', location: 'Building A - Floor 1', building: 'A', status: 'closed', lastAccess: '08:45 AM', lastUser: 'Mike Johnson', accessMethod: 'Badge', battery: 87 },
  { id: 4, name: 'Executive Office', location: 'Building A - Floor 2', building: 'A', status: 'locked', lastAccess: '09:00 AM', lastUser: 'Lisa Wong', accessMethod: 'Biometric', battery: 92 },
  { id: 5, name: 'Server Room', location: 'Building B - Ground Floor', building: 'B', status: 'closed', lastAccess: '07:30 AM', lastUser: 'Tom Davis', accessMethod: 'PIN + Badge', battery: 76 },
  { id: 6, name: 'IT Department', location: 'Building B - Floor 1', building: 'B', status: 'closed', lastAccess: '10:00 AM', lastUser: 'Anna Lee', accessMethod: 'Badge', battery: 94 },
  { id: 7, name: 'Emergency Exit East', location: 'Building B - Floor 1', building: 'B', status: 'forced', lastAccess: '08:15 AM', lastUser: 'System Alert', accessMethod: 'Emergency', battery: 65 },
  { id: 8, name: 'Warehouse Door', location: 'Building C - Ground Floor', building: 'C', status: 'closed', lastAccess: '06:30 AM', lastUser: 'David Kim', accessMethod: 'Badge', battery: 88 },
  { id: 9, name: 'Loading Dock', location: 'Building C - Ground Floor', building: 'C', status: 'maintenance', lastAccess: '07:00 AM', lastUser: 'Tech Support', accessMethod: 'Manual', battery: 72 },
  { id: 10, name: 'Security Office', location: 'Building C - Floor 1', building: 'C', status: 'closed', lastAccess: '08:00 AM', lastUser: 'James Wilson', accessMethod: 'Biometric', battery: 96 }
])

const recentEvents = ref<AccessEvent[]>([
  { id: 1, time: '10:32:15', result: 'granted', title: 'Access Granted', detail: 'Main Entrance - Badge swipe', user: 'John Smith', door: 'Main Entrance' },
  { id: 2, time: '10:28:42', result: 'denied', title: 'Access Denied', detail: 'Executive Office - Unauthorized attempt', user: 'Unknown Badge', door: 'Executive Office' },
  { id: 3, time: '10:15:00', result: 'granted', title: 'Access Granted', detail: 'IT Department - Badge swipe', user: 'Anna Lee', door: 'IT Department' },
  { id: 4, time: '09:45:22', result: 'granted', title: 'Access Granted', detail: 'Server Room - Biometric verified', user: 'Tom Davis', door: 'Server Room' },
  { id: 5, time: '09:30:10', result: 'granted', title: 'Access Granted', detail: 'North Wing Door - Badge swipe', user: 'Sarah Chen', door: 'North Wing Door' },
  { id: 6, time: '09:15:33', result: 'denied', title: 'Access Denied', detail: 'Warehouse Door - Expired badge', user: 'Former Employee', door: 'Warehouse Door' }
])

const accessLevels = ref<AccessLevel[]>([
  { name: 'Administrator', count: 8, doors: ['All Doors'], usage: 95 },
  { name: 'Executive', count: 12, doors: ['Executive Office', 'Main Entrance', 'Conference Rooms'], usage: 78 },
  { name: 'Manager', count: 25, doors: ['Main Entrance', 'North Wing', 'South Wing', 'IT Department'], usage: 82 },
  { name: 'Staff', count: 120, doors: ['Main Entrance', 'Office Areas'], usage: 65 },
  { name: 'Maintenance', count: 15, doors: ['All Areas (Limited Hours)'], usage: 45 },
  { name: 'Security', count: 20, doors: ['All Doors', 'Security Office'], usage: 88 }
])

// Computed
const openDoors = computed(() => doors.value.filter(d => d.status === 'open').length)
const securedDoors = computed(() => doors.value.filter(d => d.status === 'closed' || d.status === 'locked').length)
const alertDoors = computed(() => doors.value.filter(d => d.status === 'forced').length)
const todayOpen = computed(() => 12)
const activeUsers = computed(() => 186)

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
    result = result.filter(d =>
        d.name.toLowerCase().includes(search) ||
        d.lastUser.toLowerCase().includes(search) ||
        d.location.toLowerCase().includes(search)
    )
  }
  return result
})

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    open: 'Open',
    closed: 'Closed',
    locked: 'Locked',
    forced: 'Forced Open',
    maintenance: 'Maintenance'
  }
  return map[status] || status
}

const getBatteryColor = (battery: number) => {
  if (battery >= 80) return '#10b981'
  if (battery >= 50) return '#f59e0b'
  return '#ef4444'
}

const getUsageColor = (usage: number) => {
  if (usage >= 80) return '#10b981'
  if (usage >= 60) return '#3b82f6'
  if (usage >= 40) return '#f59e0b'
  return '#ef4444'
}

// Auto-refresh simulation
const startAutoRefresh = () => {
  if (refreshInterval) clearInterval(refreshInterval)
  refreshInterval = setInterval(() => {
    // Simulate battery drain and random status changes
    doors.value.forEach(door => {
      if (door.battery > 0 && Math.random() > 0.7) {
        door.battery = Math.max(0, door.battery - 1)
      }
    })
    // Random new event
    if (Math.random() > 0.8) {
      const names = ['John Smith', 'Sarah Chen', 'Mike Johnson', 'Lisa Wong']
      const randomUser = names[Math.floor(Math.random() * names.length)]
      recentEvents.value.unshift({
        id: Date.now(),
        time: new Date().toLocaleTimeString().slice(0, 8),
        result: Math.random() > 0.2 ? 'granted' : 'denied',
        title: Math.random() > 0.2 ? 'Access Granted' : 'Access Denied',
        detail: Math.random() > 0.2 ? 'Badge swipe at Main Entrance' : 'Unauthorized attempt',
        user: randomUser,
        door: 'Main Entrance'
      })
      if (recentEvents.value.length > 20) recentEvents.value.pop()
    }
  }, 10000)
}

const refreshData = () => {
  ElMessage.success('Access status refreshed')
}

const exportReport = () => {
  ElMessage.info('Exporting access status report...')
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
      startAutoRefresh()
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
.access-status-page {
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
.stat-change { text-align: right; }
.trend-up { font-size: 16px; font-weight: 700; color: #10b981; display: block; }
.trend-label { font-size: 10px; color: #94a3b8; }

/* Doors Grid */
.doors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
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
.door-card.locked { border-left-color: #8b5cf6; }
.door-card.forced { border-left-color: #ef4444; background: #fef2f2; }
.door-card.maintenance { border-left-color: #f59e0b; background: #fffbeb; }
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
.door-status-badge.locked { background: #ede9fe; color: #6d28d9; }
.door-status-badge.forced { background: #fee2e2; color: #dc2626; }
.door-status-badge.maintenance { background: #fef3c7; color: #d97706; }
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.door-status-badge.open .status-dot { background: #10b981; }
.door-status-badge.closed .status-dot { background: #3b82f6; }
.door-status-badge.locked .status-dot { background: #8b5cf6; }
.door-status-badge.forced .status-dot { background: #ef4444; }
.door-status-badge.maintenance .status-dot { background: #f59e0b; }

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

.door-progress { margin-top: 12px; }
.progress-label { font-size: 11px; color: #64748b; margin-bottom: 6px; }
.progress-bar-container {
  background: #e2e8f0;
  border-radius: 10px;
  height: 8px;
  position: relative;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  border-radius: 10px;
  transition: width 0.3s ease;
}
.progress-value {
  position: absolute;
  right: 8px;
  top: -18px;
  font-size: 10px;
  font-weight: 500;
  color: #475569;
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

/* Events Section */
.events-section {
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
.event-count {
  background: #f1f5f9;
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  color: #475569;
}
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
  transition: all 0.2s;
}
.event-item:hover {
  background: #f1f5f9;
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
.event-icon.granted { background: #d1fae5; color: #10b981; }
.event-icon.denied { background: #fee2e2; color: #ef4444; }
.event-content { flex: 1; }
.event-title { font-weight: 600; color: #1a1a2e; margin-bottom: 2px; }
.event-detail { font-size: 12px; color: #64748b; margin-bottom: 4px; }
.event-meta {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: #94a3b8;
}
.event-meta .el-icon { margin-right: 2px; vertical-align: middle; }

/* Access Levels Section */
.access-levels-section {
  background: white;
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}
.levels-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}
.level-card {
  background: #f8fafc;
  border-radius: 16px;
  padding: 16px;
  transition: all 0.2s;
}
.level-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
.level-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e2e8f0;
}
.level-name { font-weight: 600; color: #1a1a2e; }
.level-count { font-size: 12px; color: #64748b; }
.level-doors { margin-bottom: 12px; }
.level-label { font-size: 11px; color: #94a3b8; display: block; margin-bottom: 6px; }
.door-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.door-tag {
  font-size: 10px;
  padding: 2px 8px;
  background: #e2e8f0;
  border-radius: 12px;
  color: #475569;
}

:deep(.el-progress__text) { font-size: 11px !important; }
</style>