<template>
  <!-- Loading Screen -->
  <div v-if="!isLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">
          <span class="loading-title">Mobile Dispatch</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Dispatch Management System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="mobile-dispatch">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <el-icon><Iphone /></el-icon>
          Mobile Dispatch
        </h1>
        <div class="page-subtitle">Real-time task assignment for field engineers</div>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="syncData" :loading="syncing">
          <el-icon><Refresh /></el-icon> Sync
        </el-button>
        <el-button @click="notifyAllEngineers">
          <el-icon><Message /></el-icon> Notify All
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ onlineEngineers }}</div>
          <div class="stat-label">Online Engineers</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ pendingTasks }}</div>
          <div class="stat-label">Pending Tasks</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ avgResponseTime }}<span class="unit">min</span></div>
          <div class="stat-label">Avg Response Time</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><Check /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ completionRate }}<span class="unit">%</span></div>
          <div class="stat-label">Completion Rate</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Left: Pending Tasks -->
      <div class="tasks-panel">
        <div class="panel-header">
          <span class="panel-title">
            <el-icon><List /></el-icon> Pending Tasks
            <el-badge :value="pendingTasks" class="badge" type="danger" v-if="pendingTasks > 0" />
          </span>
          <el-select v-model="priorityFilter" placeholder="Priority" size="small" clearable style="width: 100px">
            <el-option label="All" value="all" />
            <el-option label="Critical" value="critical" />
            <el-option label="High" value="high" />
            <el-option label="Medium" value="medium" />
            <el-option label="Low" value="low" />
          </el-select>
        </div>
        <div class="tasks-container">
          <div
              v-for="task in filteredTasks"
              :key="task.id"
              class="task-card"
              :class="task.priority"
              @click="openDispatchDialog(task)"
          >
            <div class="task-header">
              <div class="task-badge" :class="task.priority">
                {{ task.priority.toUpperCase() }}
              </div>
              <div class="task-time">
                <el-icon><Clock /></el-icon> {{ task.reportedTime }}
              </div>
            </div>
            <div class="task-title">{{ task.title }}</div>
            <div class="task-location">
              <el-icon><Location /></el-icon> {{ task.location }}
            </div>
            <div class="task-skills">
              <el-tag v-for="skill in task.skills.slice(0, 3)" :key="skill" size="small" type="info">
                {{ skill }}
              </el-tag>
              <span v-if="task.skills.length > 3" class="more">+{{ task.skills.length - 3 }}</span>
            </div>
            <div class="task-footer">
              <span class="est-time">⏱️ Est: {{ task.estimatedHours }}h</span>
              <el-button type="primary" size="small" @click.stop="openDispatchDialog(task)">
                Dispatch
              </el-button>
            </div>
          </div>
          <div v-if="filteredTasks.length === 0" class="empty-tasks">
            <el-empty description="No pending tasks" :image-size="80" />
          </div>
        </div>
      </div>

      <!-- Right: Online Engineers -->
      <div class="engineers-panel">
        <div class="panel-header">
          <span class="panel-title">
            <el-icon><UserFilled /></el-icon> Online Engineers
            <el-badge :value="onlineEngineers" class="badge" type="success" />
          </span>
          <el-input v-model="searchEngineer" placeholder="Search..." size="small" style="width: 140px" clearable />
        </div>
        <div class="engineers-container">
          <div
              v-for="engineer in filteredEngineers"
              :key="engineer.id"
              class="engineer-card"
              :class="{ selected: selectedEngineerId === engineer.id }"
              @click="selectEngineer(engineer)"
          >
            <div class="engineer-avatar" :class="engineer.status">
              <span>{{ engineer.name.charAt(0) }}</span>
              <span class="status-dot" :class="engineer.status"></span>
            </div>
            <div class="engineer-info">
              <div class="engineer-name">{{ engineer.name }}</div>
              <div class="engineer-role">{{ engineer.role }}</div>
              <div class="engineer-load">
                <span>Load: {{ engineer.currentLoad }}%</span>
                <el-progress :percentage="engineer.currentLoad" :stroke-width="3" :show-text="false" />
              </div>
            </div>
            <div class="engineer-stats">
              <div class="stat">📋 {{ engineer.activeTasks }}</div>
              <div class="stat">✅ {{ engineer.completedToday }}</div>
            </div>
            <div class="engineer-distance" v-if="engineer.distance">
              <el-icon><Location /></el-icon> {{ engineer.distance }}km
            </div>
          </div>
          <div v-if="filteredEngineers.length === 0" class="empty-engineers">
            <el-empty description="No online engineers" :image-size="80" />
          </div>
        </div>
      </div>
    </div>

    <!-- Dispatch Dialog -->
    <el-dialog v-model="dispatchDialogVisible" title="Dispatch Task" width="500px">
      <div class="dispatch-content" v-if="selectedTask">
        <div class="task-summary">
          <div class="task-header-dialog">
            <span class="task-title-dialog">{{ selectedTask.title }}</span>
            <el-tag :type="getPriorityTagType(selectedTask.priority)" size="small">
              {{ selectedTask.priority.toUpperCase() }}
            </el-tag>
          </div>
          <div class="task-location-dialog">
            <el-icon><Location /></el-icon> {{ selectedTask.location }}
          </div>
          <div class="task-skills-dialog">
            <span>Required Skills:</span>
            <el-tag v-for="skill in selectedTask.skills" :key="skill" size="small" type="primary">
              {{ skill }}
            </el-tag>
          </div>
        </div>
        <el-divider />
        <div class="engineer-selection">
          <div class="select-label">Select Engineer</div>
          <div class="engineer-list-dialog">
            <div
                v-for="engineer in onlineEngineersList"
                :key="engineer.id"
                class="engineer-option"
                :class="{ recommended: isRecommended(engineer, selectedTask), selected: selectedDispatchEngineerId === engineer.id }"
                @click="selectedDispatchEngineerId = engineer.id"
            >
              <div class="engineer-avatar-small" :class="engineer.status">
                {{ engineer.name.charAt(0) }}
              </div>
              <div class="engineer-option-info">
                <div class="engineer-option-name">{{ engineer.name }}</div>
                <div class="engineer-option-detail">
                  Load: {{ engineer.currentLoad }}% | Tasks: {{ engineer.activeTasks }}
                </div>
              </div>
              <div v-if="isRecommended(engineer, selectedTask)" class="recommended-badge">
                ⭐ Recommended
              </div>
            </div>
          </div>
        </div>
        <el-form-item label="Dispatch Notes" style="margin-top: 16px;">
          <el-input v-model="dispatchNotes" type="textarea" :rows="2" placeholder="Add instructions for the engineer..." />
        </el-form-item>
      </div>
      <template #footer>
        <el-button @click="dispatchDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmDispatch" :disabled="!selectedDispatchEngineerId">
          Send Dispatch
        </el-button>
      </template>
    </el-dialog>

    <!-- Notification Dialog -->
    <el-dialog v-model="notifyDialogVisible" title="Broadcast Notification" width="450px">
      <el-input
          v-model="notificationMessage"
          type="textarea"
          :rows="4"
          placeholder="Enter notification message for all engineers..."
      />
      <template #footer>
        <el-button @click="notifyDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="sendNotification">Send</el-button>
      </template>
    </el-dialog>

    <!-- Success Toast -->
    <div v-if="showToast" class="toast-notification" :class="toastType">
      <el-icon><SuccessFilled /></el-icon>
      <span>{{ toastMessage }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Iphone, Refresh, Message, User, Document, Clock, Check,
  List, Location, UserFilled, SuccessFilled
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading engineers...',
  'Syncing tasks...',
  'Initializing dispatch system...',
  'Almost ready...'
]

// ==================== Types ====================
interface MobileTask {
  id: number
  title: string
  priority: 'critical' | 'high' | 'medium' | 'low'
  location: string
  skills: string[]
  reportedTime: string
  estimatedHours: number
  status: 'pending' | 'dispatched' | 'in-progress' | 'completed'
  assignedTo?: string
  assignedToId?: number
}

interface MobileEngineer {
  id: number
  name: string
  role: string
  skills: string[]
  status: 'online' | 'busy' | 'offline'
  currentLoad: number
  activeTasks: number
  completedToday: number
  location: { lat: number; lng: number }
  distance?: number
  phone: string
}

// ==================== Mock Data ====================
const pendingTasksList = ref<MobileTask[]>([
  { id: 1, title: 'UPS-01 Battery Replacement', priority: 'critical', location: 'Server Room A', skills: ['electrical', 'ups'], reportedTime: '08:23', estimatedHours: 2.5, status: 'pending' },
  { id: 2, title: 'CRAC-01 Compressor Failure', priority: 'critical', location: 'Data Center', skills: ['hvac', 'crac'], reportedTime: '09:45', estimatedHours: 4, status: 'pending' },
  { id: 3, title: 'PDU-A01 Firmware Update', priority: 'medium', location: 'Server Row A', skills: ['electrical'], reportedTime: '10:30', estimatedHours: 1.5, status: 'pending' },
  { id: 4, title: 'Chiller-01 Water Leak', priority: 'high', location: 'Chiller Plant', skills: ['hvac', 'plumbing'], reportedTime: '11:15', estimatedHours: 3, status: 'pending' },
  { id: 5, title: 'Network Switch Configuration', priority: 'medium', location: 'Network Room', skills: ['network'], reportedTime: '13:00', estimatedHours: 1, status: 'pending' },
  { id: 6, title: 'Generator Fuel Test', priority: 'low', location: 'Generator Room', skills: ['electrical', 'mechanical'], reportedTime: '14:30', estimatedHours: 2, status: 'pending' },
  { id: 7, title: 'UPS-02 Battery Test', priority: 'high', location: 'Server Room B', skills: ['electrical', 'ups'], reportedTime: '15:00', estimatedHours: 1.5, status: 'pending' },
  { id: 8, title: 'HVAC Filter Replacement', priority: 'low', location: 'Data Center', skills: ['hvac'], reportedTime: '15:30', estimatedHours: 1, status: 'pending' }
])

const engineersList = ref<MobileEngineer[]>([
  { id: 1, name: 'John Chen', role: 'Senior Technician', skills: ['electrical', 'ups', 'pdu'], status: 'online', currentLoad: 65, activeTasks: 3, completedToday: 2, location: { lat: 1.3521, lng: 103.8198 }, phone: '+65 9123 4567' },
  { id: 2, name: 'Sarah Wong', role: 'HVAC Specialist', skills: ['hvac', 'crac', 'plumbing'], status: 'online', currentLoad: 45, activeTasks: 2, completedToday: 3, location: { lat: 1.3525, lng: 103.8200 }, phone: '+65 9234 5678' },
  { id: 3, name: 'Mike Lim', role: 'Electrical Engineer', skills: ['electrical', 'mechanical', 'generator'], status: 'busy', currentLoad: 85, activeTasks: 4, completedToday: 1, location: { lat: 1.3518, lng: 103.8195 }, phone: '+65 9345 6789' },
  { id: 4, name: 'David Tan', role: 'General Technician', skills: ['hvac', 'plumbing'], status: 'online', currentLoad: 30, activeTasks: 1, completedToday: 2, location: { lat: 1.3530, lng: 103.8205 }, phone: '+65 9456 7890' },
  { id: 5, name: 'Lisa Ng', role: 'Network Specialist', skills: ['network', 'security'], status: 'online', currentLoad: 25, activeTasks: 1, completedToday: 3, location: { lat: 1.3523, lng: 103.8190 }, phone: '+65 9567 8901' },
  { id: 6, name: 'Kevin Lim', role: 'UPS Specialist', skills: ['electrical', 'ups'], status: 'online', currentLoad: 50, activeTasks: 2, completedToday: 1, location: { lat: 1.3515, lng: 103.8192 }, phone: '+65 9678 9012' }
])

// ==================== State ====================
const priorityFilter = ref('all')
const searchEngineer = ref('')
const selectedEngineerId = ref<number | null>(null)
const selectedTask = ref<MobileTask | null>(null)
const selectedDispatchEngineerId = ref<number | null>(null)
const dispatchDialogVisible = ref(false)
const notifyDialogVisible = ref(false)
const notificationMessage = ref('')
const dispatchNotes = ref('')
const syncing = ref(false)

// Toast
const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('success')
let toastTimer: NodeJS.Timeout

// ==================== Computed ====================
const onlineEngineers = computed(() => {
  return engineersList.value.filter(e => e.status === 'online').length
})

const pendingTasks = computed(() => {
  return pendingTasksList.value.filter(t => t.status === 'pending').length
})

const avgResponseTime = computed(() => {
  return 4.2
})

const completionRate = computed(() => {
  return 94
})

const filteredTasks = computed(() => {
  let filtered = pendingTasksList.value.filter(t => t.status === 'pending')
  if (priorityFilter.value !== 'all') {
    filtered = filtered.filter(t => t.priority === priorityFilter.value)
  }
  return filtered
})

const filteredEngineers = computed(() => {
  let filtered = engineersList.value.filter(e => e.status === 'online')
  if (searchEngineer.value) {
    filtered = filtered.filter(e => e.name.toLowerCase().includes(searchEngineer.value.toLowerCase()))
  }
  return filtered
})

const onlineEngineersList = computed(() => {
  return engineersList.value.filter(e => e.status === 'online')
})

// ==================== Methods ====================
const getPriorityTagType = (priority: string) => {
  const map: Record<string, string> = { critical: 'danger', high: 'danger', medium: 'warning', low: 'info' }
  return map[priority] || 'info'
}

const isRecommended = (engineer: MobileEngineer, task: MobileTask) => {
  const hasSkills = task.skills.some(s => engineer.skills.includes(s))
  const lowLoad = engineer.currentLoad < 60
  return hasSkills && lowLoad
}

const selectEngineer = (engineer: MobileEngineer) => {
  selectedEngineerId.value = engineer.id
}

const openDispatchDialog = (task: MobileTask) => {
  selectedTask.value = task
  selectedDispatchEngineerId.value = null
  dispatchNotes.value = ''
  dispatchDialogVisible.value = true
}

const confirmDispatch = () => {
  if (!selectedDispatchEngineerId.value || !selectedTask.value) {
    ElMessage.warning('Please select an engineer')
    return
  }

  const engineer = engineersList.value.find(e => e.id === selectedDispatchEngineerId.value)
  const task = selectedTask.value

  if (engineer && task) {
    // Update task status
    const taskIndex = pendingTasksList.value.findIndex(t => t.id === task.id)
    if (taskIndex !== -1) {
      pendingTasksList.value[taskIndex].status = 'dispatched'
      pendingTasksList.value[taskIndex].assignedTo = engineer.name
      pendingTasksList.value[taskIndex].assignedToId = engineer.id
    }

    // Update engineer load
    const engineerIndex = engineersList.value.findIndex(e => e.id === engineer.id)
    if (engineerIndex !== -1) {
      engineersList.value[engineerIndex].activeTasks++
      engineersList.value[engineerIndex].currentLoad = Math.min(100, engineersList.value[engineerIndex].currentLoad + 15)
      if (engineersList.value[engineerIndex].currentLoad > 70) {
        engineersList.value[engineerIndex].status = 'busy'
      }
    }

    // Show success toast
    showToastMessage(`✅ Dispatched to ${engineer.name}`, 'success')

    // Add to dispatch log (would be saved to backend)
    console.log(`Dispatched ${task.title} to ${engineer.name}`, dispatchNotes.value)

    dispatchDialogVisible.value = false
    selectedTask.value = null
    selectedDispatchEngineerId.value = null
  }
}

const syncData = async () => {
  syncing.value = true
  showToastMessage('🔄 Syncing data...', 'info')
  await new Promise(resolve => setTimeout(resolve, 1500))
  showToastMessage('✅ Sync completed', 'success')
  syncing.value = false
}

const notifyAllEngineers = () => {
  notificationMessage.value = ''
  notifyDialogVisible.value = true
}

const sendNotification = () => {
  if (notificationMessage.value.trim()) {
    showToastMessage(`📢 Notification sent to ${onlineEngineers.value} engineers`, 'success')
    notifyDialogVisible.value = false
    notificationMessage.value = ''
  } else {
    ElMessage.warning('Please enter a message')
  }
}

const showToastMessage = (message: string, type: 'success' | 'error' | 'info' = 'success') => {
  if (toastTimer) clearTimeout(toastTimer)
  toastMessage.value = message
  toastType.value = type
  showToast.value = true
  toastTimer = setTimeout(() => {
    showToast.value = false
  }, 3000)
}

// Simulate real-time location updates
const simulateLocationUpdates = () => {
  setInterval(() => {
    engineersList.value.forEach(engineer => {
      if (engineer.status === 'online') {
        // Random distance simulation (1-15 km)
        engineer.distance = Math.floor(Math.random() * 15) + 1
      }
    })
  }, 30000)
}

// ==================== Loading Animation ====================
const startLoading = () => {
  let progress = 0
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 12
      loadingProgress.value = Math.min(progress, 90)
    }
  }, 100)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(() => {
      isLoaded.value = true
      simulateLocationUpdates()
    }, 500)
  }, 2200)
}

// ==================== Lifecycle ====================
onMounted(() => {
  startLoading()
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
.spinner-ring:nth-child(4) { border-left-color: #ec489a; animation-delay: 0.6s; width: 20%; height: 20%; top: 40%; left: 40%; }

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

/* ==================== Main Page Styles ==================== */
* {
  scrollbar-width: none;
  -ms-overflow-style: none;
}
*::-webkit-scrollbar {
  display: none;
}

.mobile-dispatch {
  min-height: 100vh;
  background: #f0f2f6;
  padding: 20px;
  font-family: 'Segoe UI', system-ui, sans-serif;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 6px 0;
}

.page-subtitle {
  font-size: 13px;
  color: #64748b;
}

.header-right {
  display: flex;
  gap: 12px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.blue { background: #eef2ff; color: #3b82f6; }
.stat-icon.green { background: #dcfce7; color: #22c55e; }
.stat-icon.orange { background: #fef3c7; color: #f59e0b; }
.stat-icon.purple { background: #f3e8ff; color: #8b5cf6; }

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.stat-value .unit {
  font-size: 12px;
  font-weight: normal;
  color: #64748b;
  margin-left: 2px;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

/* Main Content */
.main-content {
  display: flex;
  gap: 20px;
}

.tasks-panel {
  flex: 1.2;
  background: white;
  border-radius: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: 650px;
}

.engineers-panel {
  flex: 0.9;
  background: white;
  border-radius: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: 650px;
}

.panel-header {
  padding: 16px 20px;
  border-bottom: 1px solid #eef2f8;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #1e293b;
  flex-wrap: wrap;
  gap: 12px;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

/* Tasks Container */
.tasks-container {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.task-card {
  background: #fafcff;
  border-radius: 16px;
  padding: 14px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #eef2f8;
  position: relative;
}

.task-card:hover {
  transform: translateX(3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.task-card.critical { border-left: 4px solid #ef4444; }
.task-card.high { border-left: 4px solid #f97316; }
.task-card.medium { border-left: 4px solid #eab308; }
.task-card.low { border-left: 4px solid #22c55e; }

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.task-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 20px;
}

.task-badge.critical { background: #fee2e2; color: #dc2626; }
.task-badge.high { background: #fff3e3; color: #ea580c; }
.task-badge.medium { background: #fef9c3; color: #ca8a04; }
.task-badge.low { background: #dcfce7; color: #16a34a; }

.task-time {
  font-size: 11px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 4px;
}

.task-title {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
  margin-bottom: 8px;
}

.task-location {
  font-size: 12px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 8px;
}

.task-skills {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.task-skills .more {
  font-size: 10px;
  color: #64748b;
  margin-left: 4px;
}

.task-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.est-time {
  font-size: 11px;
  color: #8b5cf6;
}

/* Engineers Container */
.engineers-container {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.engineer-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  margin-bottom: 10px;
  background: #fafcff;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #eef2f8;
}

.engineer-card:hover {
  background: #f1f5f9;
  transform: translateX(2px);
}

.engineer-card.selected {
  background: #eef2ff;
  border-color: #3b82f6;
}

.engineer-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 18px;
  position: relative;
  flex-shrink: 0;
}

.status-dot {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid white;
}

.status-dot.online { background: #22c55e; }
.status-dot.busy { background: #f97316; }
.status-dot.offline { background: #94a3b8; }

.engineer-info {
  flex: 1;
}

.engineer-name {
  font-weight: 700;
  font-size: 14px;
  color: #1e293b;
  margin-bottom: 2px;
}

.engineer-role {
  font-size: 11px;
  color: #64748b;
  margin-bottom: 6px;
}

.engineer-load {
  font-size: 10px;
  color: #5b6e8c;
}

.engineer-stats {
  text-align: right;
  font-size: 11px;
  color: #475569;
}

.engineer-stats .stat {
  margin-bottom: 2px;
}

.engineer-distance {
  font-size: 11px;
  color: #3b82f6;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: 8px;
}

/* Dialog Styles */
.dispatch-content {
  padding: 8px;
}

.task-summary {
  background: #f8fafc;
  padding: 16px;
  border-radius: 12px;
}

.task-header-dialog {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.task-title-dialog {
  font-weight: 700;
  font-size: 15px;
  color: #1e293b;
}

.task-location-dialog {
  font-size: 13px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
}

.task-skills-dialog {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  font-size: 12px;
}

.select-label {
  font-weight: 600;
  margin-bottom: 12px;
  color: #1e293b;
}

.engineer-list-dialog {
  max-height: 300px;
  overflow-y: auto;
}

.engineer-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  margin-bottom: 8px;
  background: #f8fafc;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #eef2f8;
}

.engineer-option:hover {
  background: #f1f5f9;
}

.engineer-option.selected {
  background: #eef2ff;
  border-color: #3b82f6;
}

.engineer-option.recommended {
  background: linear-gradient(135deg, #fef3c7, #fffbeb);
  border-color: #f59e0b;
}

.engineer-avatar-small {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 16px;
  flex-shrink: 0;
}

.engineer-avatar-small.online { box-shadow: 0 0 0 2px #22c55e; }
.engineer-avatar-small.busy { box-shadow: 0 0 0 2px #f97316; }

.engineer-option-info {
  flex: 1;
}

.engineer-option-name {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
}

.engineer-option-detail {
  font-size: 11px;
  color: #64748b;
  margin-top: 2px;
}

.recommended-badge {
  font-size: 11px;
  background: #f59e0b;
  color: white;
  padding: 4px 10px;
  border-radius: 20px;
}

/* Toast Notification */
.toast-notification {
  position: fixed;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  background: white;
  border-radius: 40px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  z-index: 10000;
  animation: slideUp 0.3s ease-out;
}

.toast-notification.success {
  background: #10b981;
  color: white;
}

.toast-notification.error {
  background: #ef4444;
  color: white;
}

.toast-notification.info {
  background: #3b82f6;
  color: white;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

/* Empty States */
.empty-tasks, .empty-engineers {
  text-align: center;
  padding: 40px;
}

/* Responsive */
@media (max-width: 1000px) {
  .main-content {
    flex-direction: column;
  }

  .tasks-panel, .engineers-panel {
    max-height: 500px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .mobile-dispatch {
    padding: 12px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>