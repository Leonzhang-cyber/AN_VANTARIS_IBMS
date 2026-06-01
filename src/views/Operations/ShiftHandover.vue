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
        <div class="loading-tip">Shift Handover System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="shift-handover">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Shift Handover</h2>
        <p class="subtitle">Seamless shift transition and operational status transfer</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="createHandover">
          <el-icon><Plus /></el-icon> New Handover
        </el-button>
        <el-button @click="refreshData">
          <el-icon><RefreshRight /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">🔄</div>
        <div class="stat-info">
          <div class="stat-value">{{ handovers.length }}</div>
          <div class="stat-label">Total Handovers</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <div class="stat-info">
          <div class="stat-value">{{ completedCount }}</div>
          <div class="stat-label">Completed</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⏳</div>
        <div class="stat-info">
          <div class="stat-value">{{ pendingCount }}</div>
          <div class="stat-label">Pending</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-info">
          <div class="stat-value">{{ activeStaff }}</div>
          <div class="stat-label">Active Staff</div>
        </div>
      </div>
    </div>

    <!-- Current Shift Banner -->
    <div class="current-shift-banner">
      <div class="shift-icon">{{ currentShiftIcon }}</div>
      <div class="shift-info">
        <div class="shift-label">Current Shift</div>
        <div class="shift-name">{{ currentShiftDisplay }}</div>
        <div class="shift-time">{{ currentShiftTime }}</div>
      </div>
      <div class="shift-operator">
        <div class="operator-label">On Duty</div>
        <div class="operator-name">{{ getShiftOperator(currentShiftValue) }}</div>
      </div>
      <div class="shift-progress">
        <el-progress :percentage="shiftProgress" :stroke-width="8" :color="progressColor" />
        <div class="progress-label">{{ shiftProgress }}% Complete</div>
      </div>
    </div>

    <!-- Next Shift Preview -->
    <div class="next-shift-preview">
      <div class="preview-icon">⏰</div>
      <div class="preview-info">
        <div class="preview-label">Upcoming Shift</div>
        <div class="preview-name">{{ nextShiftName }}</div>
        <div class="preview-time">Starts in {{ nextShiftMinutes }} minutes</div>
      </div>
      <div class="preview-operator">
        <div class="operator-label">Assigned</div>
        <div class="operator-name">{{ getShiftOperator(nextShiftValue) }}</div>
      </div>
    </div>

    <!-- Handover Form -->
    <transition name="slide-fade">
      <el-card class="handover-card" shadow="hover" v-if="showHandoverForm">
        <template #header>
          <div class="card-header">
            <span><el-icon><Edit /></el-icon> Create Shift Handover</span>
            <el-button type="danger" link @click="showHandoverForm = false">Cancel</el-button>
          </div>
        </template>
        <el-form :model="handoverForm" label-width="120px">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="From Operator" required>
                <el-input v-model="handoverForm.fromOperator" placeholder="Your name" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="To Operator" required>
                <el-select v-model="handoverForm.toOperator" placeholder="Select operator" style="width: 100%">
                  <el-option v-for="op in availableOperators" :key="op" :label="op" :value="op" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="Shift">
            <el-select v-model="handoverForm.shift" style="width: 200px">
              <el-option label="Morning Shift (06:00-14:00)" value="Morning" />
              <el-option label="Afternoon Shift (14:00-22:00)" value="Afternoon" />
              <el-option label="Night Shift (22:00-06:00)" value="Night" />
            </el-select>
          </el-form-item>
          <el-form-item label="System Status">
            <el-radio-group v-model="handoverForm.systemStatus">
              <el-radio value="normal">✅ All Systems Normal</el-radio>
              <el-radio value="minor">⚠️ Minor Issues</el-radio>
              <el-radio value="major">🚨 Major Issues</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="Pending Tasks">
            <el-input v-model="handoverForm.pendingTasks" type="textarea" :rows="2" placeholder="List any pending tasks or issues" />
          </el-form-item>
          <el-form-item label="Notes & Remarks">
            <el-input v-model="handoverForm.notes" type="textarea" :rows="2" placeholder="Additional notes for next shift" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="submitHandover">Submit Handover</el-button>
            <el-button @click="showHandoverForm = false">Cancel</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </transition>

    <!-- Today's Handovers -->
    <el-card class="today-handovers-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span><el-icon><Calendar /></el-icon> Today's Handovers</span>
          <el-input v-model="searchText" placeholder="Search..." clearable style="width: 200px" :prefix-icon="Search" />
        </div>
      </template>
      <div class="handover-timeline">
        <div v-for="handover in filteredHandovers" :key="handover.id" class="handover-item">
          <div class="handover-time">
            <div class="time">{{ handover.time }}</div>
            <div class="date">{{ handover.date }}</div>
          </div>
          <div class="handover-line">
            <div class="line-dot" :class="handover.systemStatus"></div>
            <div class="line-bar"></div>
          </div>
          <div class="handover-content">
            <div class="content-header">
              <div class="operators">
                <span class="from">{{ handover.fromOperator }}</span>
                <el-icon><ArrowRight /></el-icon>
                <span class="to">{{ handover.toOperator }}</span>
              </div>
              <div class="shift-badge" :class="handover.shift.toLowerCase()">{{ handover.shift }} Shift</div>
              <div class="status-badge" :class="handover.status">{{ handover.status }}</div>
            </div>
            <div class="content-body">
              <div class="system-status">
                <span class="label">System Status:</span>
                <span :class="['status-text', handover.systemStatus]">
                  {{ handover.systemStatus === 'normal' ? '✅ All Normal' : handover.systemStatus === 'minor' ? '⚠️ Minor Issues' : '🚨 Major Issues' }}
                </span>
              </div>
              <div class="pending-tasks" v-if="handover.pendingTasks !== 'None'">
                <span class="label">Pending Tasks:</span>
                <span class="tasks">{{ handover.pendingTasks }}</span>
              </div>
              <div class="notes" v-if="handover.notes">
                <span class="label">Notes:</span>
                <span class="notes-text">{{ handover.notes }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="filteredHandovers.length === 0" class="empty-state">
        <el-empty description="No handover records found" />
      </div>
    </el-card>

    <!-- Team Members -->
    <el-card class="team-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span><el-icon><User /></el-icon> Operations Team</span>
          <el-tag type="info" size="small">{{ teamMembers.length }} Members</el-tag>
        </div>
      </template>
      <div class="team-grid">
        <div v-for="member in teamMembers" :key="member.name" class="team-member">
          <div class="member-avatar" :style="{ background: member.color }">
            {{ member.name.charAt(0) }}
          </div>
          <div class="member-info">
            <div class="member-name">{{ member.name }}</div>
            <div class="member-role">{{ member.role }}</div>
          </div>
          <div class="member-status" :class="member.status">{{ member.status === 'on-duty' ? 'On Duty' : 'Off Duty' }}</div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Plus, RefreshRight, Search, Edit, Calendar, User, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Loading shift handover system...',
  'Fetching schedule data...',
  'Loading team information...',
  'Ready for handover...'
]

// Helper functions
const getCurrentTime = () => {
  const now = new Date()
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  return `${hours}:${minutes}`
}

const getCurrentDate = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const getCurrentShift = () => {
  const hour = new Date().getHours()
  if (hour >= 6 && hour < 14) return 'Morning'
  if (hour >= 14 && hour < 22) return 'Afternoon'
  return 'Night'
}

// Shift configuration
const shiftConfig = {
  Morning: { name: 'Morning Shift', time: '06:00 - 14:00', icon: '🌅', next: 'Afternoon' },
  Afternoon: { name: 'Afternoon Shift', time: '14:00 - 22:00', icon: '☀️', next: 'Night' },
  Night: { name: 'Night Shift', time: '22:00 - 06:00', icon: '🌙', next: 'Morning' }
}

// Operators
const shiftOperators = ref({
  Morning: 'John Zhang',
  Afternoon: 'Sarah Li',
  Night: 'Mike Wang'
})

const availableOperators = ['John Zhang', 'Sarah Li', 'Mike Wang', 'Emma Zhao', 'David Sun', 'Lisa Chen']

// Team members
const teamMembers = ref([
  { name: 'John Zhang', role: 'Morning Lead', status: 'on-duty', color: '#409eff' },
  { name: 'Sarah Li', role: 'Afternoon Lead', status: 'off-duty', color: '#e6a23c' },
  { name: 'Mike Wang', role: 'Night Lead', status: 'off-duty', color: '#67c23a' },
  { name: 'Emma Zhao', role: 'HVAC Specialist', status: 'on-duty', color: '#909399' },
  { name: 'David Sun', role: 'Electrical Engineer', status: 'on-duty', color: '#409eff' },
  { name: 'Lisa Chen', role: 'BMS Operator', status: 'off-duty', color: '#e6a23c' }
])

// Handover data
const handovers = ref([
  {
    id: 1,
    date: getCurrentDate(),
    time: '13:55',
    fromOperator: 'John Zhang',
    toOperator: 'Sarah Li',
    shift: 'Afternoon',
    systemStatus: 'normal',
    pendingTasks: 'Monitor chiller performance - slight efficiency drop observed',
    notes: 'All systems operational. Scheduled maintenance for tomorrow.',
    status: 'completed'
  },
  {
    id: 2,
    date: getCurrentDate(),
    time: '05:55',
    fromOperator: 'Mike Wang',
    toOperator: 'John Zhang',
    shift: 'Morning',
    systemStatus: 'normal',
    pendingTasks: 'Weekly fire alarm test scheduled for 10:00 AM',
    notes: 'Night shift quiet, no incidents reported.',
    status: 'completed'
  },
  {
    id: 3,
    date: getCurrentDate(),
    time: '21:55',
    fromOperator: 'Sarah Li',
    toOperator: 'Mike Wang',
    shift: 'Night',
    systemStatus: 'minor',
    pendingTasks: 'UPS-01 battery health at 72% - schedule inspection',
    notes: 'Generator weekly test completed successfully.',
    status: 'pending'
  },
  {
    id: 4,
    date: getCurrentDate(),
    time: '09:30',
    fromOperator: 'Emma Zhao',
    toOperator: 'John Zhang',
    shift: 'Morning',
    systemStatus: 'minor',
    pendingTasks: 'AHU-03 fan bearing noise - monitor closely',
    notes: 'Vendor scheduled for inspection tomorrow.',
    status: 'completed'
  }
])

// UI State
const showHandoverForm = ref(false)
const searchText = ref('')
let intervalId: any = null
let loadingIntervalId: any = null

const handoverForm = ref({
  fromOperator: '',
  toOperator: '',
  shift: getCurrentShift(),
  systemStatus: 'normal',
  pendingTasks: '',
  notes: ''
})

// Computed
const currentShiftValue = ref(getCurrentShift())
const currentShiftDisplay = computed(() => shiftConfig[currentShiftValue.value].name)
const currentShiftTime = computed(() => shiftConfig[currentShiftValue.value].time)
const currentShiftIcon = computed(() => shiftConfig[currentShiftValue.value].icon)

const nextShiftValue = computed(() => shiftConfig[currentShiftValue.value].next as 'Morning' | 'Afternoon' | 'Night')
const nextShiftName = computed(() => shiftConfig[nextShiftValue.value].name)

const shiftProgress = computed(() => {
  const hour = new Date().getHours()
  const minute = new Date().getMinutes()
  if (currentShiftValue.value === 'Morning') {
    const elapsed = (hour - 6) * 60 + minute
    return Math.min(100, Math.max(0, Math.floor(elapsed / 8 * 100)))
  } else if (currentShiftValue.value === 'Afternoon') {
    const elapsed = (hour - 14) * 60 + minute
    return Math.min(100, Math.max(0, Math.floor(elapsed / 8 * 100)))
  } else {
    let elapsed = (hour + 24 - 22) * 60 + minute
    if (elapsed > 480) elapsed = 480
    return Math.min(100, Math.max(0, Math.floor(elapsed / 8 * 100)))
  }
})

const progressColor = computed(() => {
  if (shiftProgress.value < 50) return '#409eff'
  if (shiftProgress.value < 80) return '#e6a23c'
  return '#67c23a'
})

const nextShiftMinutes = computed(() => {
  const now = new Date()
  let targetHour = 6
  let targetMinute = 0
  if (currentShiftValue.value === 'Morning') targetHour = 14
  else if (currentShiftValue.value === 'Afternoon') targetHour = 22
  else targetHour = 6

  const target = new Date()
  target.setHours(targetHour, targetMinute, 0)
  if (target <= now) target.setDate(target.getDate() + 1)
  return Math.round((target.getTime() - now.getTime()) / 60000)
})

const completedCount = computed(() => handovers.value.filter(h => h.status === 'completed').length)
const pendingCount = computed(() => handovers.value.filter(h => h.status === 'pending').length)
const activeStaff = computed(() => teamMembers.value.filter(m => m.status === 'on-duty').length)

const filteredHandovers = computed(() => {
  if (!searchText.value) return handovers.value
  const keyword = searchText.value.toLowerCase()
  return handovers.value.filter(h =>
      h.fromOperator.toLowerCase().includes(keyword) ||
      h.toOperator.toLowerCase().includes(keyword) ||
      (h.pendingTasks && h.pendingTasks.toLowerCase().includes(keyword))
  )
})

// Methods
const getShiftOperator = (shift: string) => {
  return shiftOperators.value[shift as keyof typeof shiftOperators.value]
}

const createHandover = () => {
  handoverForm.value = {
    fromOperator: getShiftOperator(currentShiftValue.value),
    toOperator: '',
    shift: currentShiftValue.value,
    systemStatus: 'normal',
    pendingTasks: '',
    notes: ''
  }
  showHandoverForm.value = true
}

const submitHandover = () => {
  if (!handoverForm.value.fromOperator || !handoverForm.value.toOperator) {
    ElMessage.warning('Please fill in all required fields')
    return
  }

  const newHandover = {
    id: Date.now(),
    date: getCurrentDate(),
    time: getCurrentTime(),
    fromOperator: handoverForm.value.fromOperator,
    toOperator: handoverForm.value.toOperator,
    shift: handoverForm.value.shift,
    systemStatus: handoverForm.value.systemStatus,
    pendingTasks: handoverForm.value.pendingTasks || 'None',
    notes: handoverForm.value.notes || '',
    status: 'pending'
  }

  handovers.value.unshift(newHandover)
  ElMessage.success('Handover created successfully')
  showHandoverForm.value = false
}

const refreshData = () => {
  ElMessage.success('Data refreshed')
}

// Update shift every minute
const updateCurrentShift = () => {
  currentShiftValue.value = getCurrentShift()
}

// Loading animation
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
    }, 400)
  }, 2000)

  intervalId = setInterval(updateCurrentShift, 60000)
})

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId)
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

.loading-tip { font-size: 13px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 8px; font-weight: 500; }
.loading-subtip { font-size: 11px; color: #64748b; letter-spacing: 0.5px; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

/* Main Content */
.shift-handover {
  padding: 24px;
  background: linear-gradient(135deg, #f0f7ff 0%, #e8f0fe 100%);
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
  background: linear-gradient(135deg, #1565c0, #1976d2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  margin: 0;
  color: #1565c0;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 36px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

/* Current Shift Banner */
.current-shift-banner {
  background: linear-gradient(135deg, #1a237e, #283593);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 20px;
  color: white;
}

.shift-icon {
  font-size: 48px;
  background: rgba(255,255,255,0.2);
  width: 70px;
  height: 70px;
  border-radius: 35px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.shift-info {
  flex: 1;
}

.shift-label {
  font-size: 12px;
  opacity: 0.8;
  margin-bottom: 4px;
}

.shift-name {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 4px;
}

.shift-time {
  font-size: 13px;
  opacity: 0.8;
}

.shift-operator {
  text-align: center;
  padding: 0 20px;
  border-left: 1px solid rgba(255,255,255,0.2);
  border-right: 1px solid rgba(255,255,255,0.2);
}

.operator-label {
  font-size: 11px;
  opacity: 0.7;
  margin-bottom: 4px;
}

.operator-name {
  font-size: 16px;
  font-weight: 500;
}

.shift-progress {
  width: 200px;
}

.progress-label {
  font-size: 11px;
  text-align: center;
  margin-top: 8px;
  opacity: 0.8;
}

/* Next Shift Preview */
.next-shift-preview {
  background: white;
  border-radius: 16px;
  padding: 16px 20px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.preview-icon {
  font-size: 32px;
}

.preview-info {
  flex: 1;
}

.preview-label {
  font-size: 11px;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.preview-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-top: 4px;
}

.preview-time {
  font-size: 12px;
  color: #e6a23c;
  margin-top: 4px;
}

.preview-operator {
  text-align: right;
}

/* Handover Card */
.handover-card {
  border-radius: 20px;
  margin-bottom: 24px;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

/* Today's Handovers */
.today-handovers-card {
  border-radius: 20px;
  margin-bottom: 24px;
}

.handover-timeline {
  display: flex;
  flex-direction: column;
}

.handover-item {
  display: flex;
  gap: 20px;
  padding: 20px 0;
  border-bottom: 1px solid #f0f0f0;
}

.handover-item:last-child {
  border-bottom: none;
}

.handover-time {
  min-width: 70px;
}

.handover-time .time {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.handover-time .date {
  font-size: 11px;
  color: #c0c4cc;
  margin-top: 4px;
}

.handover-line {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 30px;
}

.line-dot {
  width: 12px;
  height: 12px;
  border-radius: 6px;
  background: #67c23a;
}

.line-dot.normal { background: #67c23a; }
.line-dot.minor { background: #e6a23c; }
.line-dot.major { background: #f56c6c; }

.line-bar {
  width: 2px;
  flex: 1;
  background: #e4e7ed;
  margin: 8px 0;
}

.handover-item:last-child .line-bar {
  display: none;
}

.handover-content {
  flex: 1;
}

.content-header {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.operators {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.operators .from { color: #409eff; }
.operators .to { color: #67c23a; }

.shift-badge {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
}

.shift-badge.morning { background: #e6f7ff; color: #409eff; }
.shift-badge.afternoon { background: #fff7e6; color: #e6a23c; }
.shift-badge.night { background: #f3e5f5; color: #9c27b0; }

.status-badge {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
}

.status-badge.completed { background: #e8f5e9; color: #67c23a; }
.status-badge.pending { background: #fff7e6; color: #e6a23c; }

.content-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.system-status, .pending-tasks, .notes {
  font-size: 13px;
}

.label {
  color: #909399;
  margin-right: 8px;
}

.status-text {
  font-weight: 500;
}

.status-text.normal { color: #67c23a; }
.status-text.minor { color: #e6a23c; }
.status-text.major { color: #f56c6c; }

.tasks, .notes-text {
  color: #606266;
}

/* Team Card */
.team-card {
  border-radius: 20px;
}

.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.team-member {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 16px;
  transition: all 0.2s ease;
}

.team-member:hover {
  background: #f0f2f5;
  transform: translateX(4px);
}

.member-avatar {
  width: 48px;
  height: 48px;
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 600;
  color: white;
}

.member-info {
  flex: 1;
}

.member-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.member-role {
  font-size: 12px;
  color: #909399;
}

.member-status {
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 20px;
  font-weight: 500;
}

.member-status.on-duty { background: #e8f5e9; color: #67c23a; }
.member-status.off-duty { background: #f5f5f5; color: #909399; }

.empty-state {
  padding: 40px;
  text-align: center;
}

/* Responsive */
@media (max-width: 768px) {
  .shift-handover { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .current-shift-banner { flex-direction: column; text-align: center; }
  .shift-operator { border-left: none; border-right: none; padding: 12px 0; }
  .shift-progress { width: 100%; }
  .next-shift-preview { flex-direction: column; text-align: center; }
  .preview-operator { text-align: center; }
  .handover-item { flex-direction: column; }
  .handover-line { display: none; }
  .team-grid { grid-template-columns: 1fr; }
}
</style>