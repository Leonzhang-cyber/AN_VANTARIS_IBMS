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
        <div class="loading-tip">Daily Checklist System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="daily-checklist">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Daily Checklist</h2>
        <p class="subtitle">Track and manage daily operational tasks and inspections</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="resetToday">
          <el-icon><RefreshRight /></el-icon> Reset Today
        </el-button>
        <el-button @click="exportReport">
          <el-icon><Download /></el-icon> Export Report
        </el-button>
        <el-button @click="refreshData">
          <el-icon><RefreshRight /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Today's Progress Banner -->
    <div class="progress-banner">
      <div class="progress-info">
        <div class="progress-title">Today's Progress</div>
        <div class="progress-stats">{{ completedCount }}/{{ totalTasks }} tasks completed</div>
      </div>
      <div class="progress-bar-wrapper">
        <el-progress :percentage="completionPercentage" :stroke-width="12" :color="progressColor" :show-text="false" />
        <span class="progress-percentage">{{ completionPercentage }}%</span>
      </div>
      <div class="progress-message" :class="{ warning: completionPercentage < 50, success: completionPercentage === 100 }">
        <span v-if="completionPercentage === 100">🎉 All tasks completed! Great job!</span>
        <span v-else-if="completionPercentage >= 75">👍 Good progress! Keep going!</span>
        <span v-else-if="completionPercentage >= 50">📋 Halfway there! Continue!</span>
        <span v-else>⚠️ Please complete your daily tasks</span>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
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
        <div class="stat-icon">⚠️</div>
        <div class="stat-info">
          <div class="stat-value">{{ issuesCount }}</div>
          <div class="stat-label">Issues Reported</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📅</div>
        <div class="stat-info">
          <div class="stat-value">{{ completionPercentage }}%</div>
          <div class="stat-label">Completion Rate</div>
        </div>
      </div>
    </div>

    <!-- Category Tabs -->
    <div class="category-tabs">
      <el-tabs v-model="activeCategory" @tab-click="handleTabClick">
        <el-tab-pane label="All Tasks" name="all" />
        <el-tab-pane label="HVAC" name="hvac" />
        <el-tab-pane label="Electrical" name="electrical" />
        <el-tab-pane label="Plumbing" name="plumbing" />
        <el-tab-pane label="Safety" name="safety" />
        <el-tab-pane label="Security" name="security" />
        <el-tab-pane label="General" name="general" />
      </el-tabs>
    </div>

    <!-- Checklist Items -->
    <div class="checklist-container">
      <div v-for="task in filteredTasks" :key="task.id" class="checklist-item" :class="{ completed: task.completed, hasIssue: task.hasIssue }">
        <div class="item-checkbox">
          <el-checkbox
              :model-value="task.completed"
              @change="toggleTask(task)"
              :disabled="task.hasIssue"
          />
        </div>
        <div class="item-content">
          <div class="item-header">
            <div class="item-title">{{ task.title }}</div>
            <div class="item-category">
              <span :class="['category-tag', task.category]">{{ getCategoryLabel(task.category) }}</span>
              <span :class="['priority-tag', task.priority]">{{ getPriorityLabel(task.priority) }}</span>
            </div>
          </div>
          <div class="item-description">{{ task.description }}</div>
          <div class="item-instructions" v-if="task.instructions">
            <el-icon><InfoFilled /></el-icon>
            <span>{{ task.instructions }}</span>
          </div>
          <div class="item-notes" v-if="task.notes">
            <el-icon><Edit /></el-icon>
            <span>{{ task.notes }}</span>
          </div>
          <div class="item-footer">
            <div class="item-location">
              <el-icon><Location /></el-icon>
              <span>{{ task.location }}</span>
            </div>
            <div class="item-actions">
              <el-button size="small" type="warning" plain @click="reportIssue(task)">
                <el-icon><Warning /></el-icon> Report Issue
              </el-button>
              <el-button size="small" type="info" plain @click="addNote(task)">
                <el-icon><Edit /></el-icon> Add Note
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Issue Report Dialog -->
    <el-dialog v-model="showIssueDialog" title="Report Issue" width="500px">
      <el-form :model="issueForm" label-width="100px">
        <el-form-item label="Task">
          <span>{{ selectedTask?.title }}</span>
        </el-form-item>
        <el-form-item label="Issue Description" required>
          <el-input v-model="issueForm.description" type="textarea" :rows="3" placeholder="Describe the issue..." />
        </el-form-item>
        <el-form-item label="Priority">
          <el-select v-model="issueForm.priority" style="width: 100%">
            <el-option label="High" value="high" />
            <el-option label="Medium" value="medium" />
            <el-option label="Low" value="low" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showIssueDialog = false">Cancel</el-button>
        <el-button type="danger" @click="submitIssue">Report Issue</el-button>
      </template>
    </el-dialog>

    <!-- Add Note Dialog -->
    <el-dialog v-model="showNoteDialog" title="Add Note" width="450px">
      <el-form :model="noteForm" label-width="80px">
        <el-form-item label="Note">
          <el-input v-model="noteForm.note" type="textarea" :rows="3" placeholder="Add a note about this task..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showNoteDialog = false">Cancel</el-button>
        <el-button type="primary" @click="submitNote">Add Note</el-button>
      </template>
    </el-dialog>

    <!-- Weekly Summary -->
    <el-card class="summary-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span><el-icon><TrendCharts /></el-icon> Weekly Performance</span>
          <el-tag type="info" size="small">Last 7 days</el-tag>
        </div>
      </template>
      <div class="weekly-stats">
        <div v-for="day in weeklyData" :key="day.name" class="weekly-item">
          <div class="weekly-day">{{ day.name }}</div>
          <div class="weekly-bar">
            <div class="weekly-progress" :style="{ width: day.percentage + '%', background: day.percentage === 100 ? '#67c23a' : '#409eff' }"></div>
          </div>
          <div class="weekly-percent">{{ day.percentage }}%</div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RefreshRight, Download, InfoFilled, Edit, Location, Warning, TrendCharts } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Loading daily checklist...',
  'Fetching today\'s tasks...',
  'Organizing by category...',
  'Ready for inspection...'
]

// Types
interface ChecklistTask {
  id: number
  title: string
  description: string
  category: string
  priority: string
  location: string
  instructions: string | null
  completed: boolean
  notes: string | null
  hasIssue: boolean
  issueDescription: string | null
}

// Task data
const tasks = ref<ChecklistTask[]>([
  {
    id: 1,
    title: 'Check Chiller Operation',
    description: 'Verify chiller running parameters, temperatures, and pressures are within normal range',
    category: 'hvac',
    priority: 'high',
    location: 'Central Plant',
    instructions: 'Check supply/return temperatures, refrigerant pressures, and oil levels',
    completed: false,
    notes: null,
    hasIssue: false,
    issueDescription: null
  },
  {
    id: 2,
    title: 'Inspect AHU Filters',
    description: 'Check air handler unit filters for dirt and blockage',
    category: 'hvac',
    priority: 'medium',
    location: 'AHU Rooms - Floors 1-5',
    instructions: 'Visual inspection of all filters, note any that need replacement',
    completed: false,
    notes: null,
    hasIssue: false,
    issueDescription: null
  },
  {
    id: 3,
    title: 'Test UPS Systems',
    description: 'Verify UPS status, battery health, and load levels',
    category: 'electrical',
    priority: 'high',
    location: 'Electrical Rooms',
    instructions: 'Check display for alarms, record battery charge levels',
    completed: false,
    notes: null,
    hasIssue: false,
    issueDescription: null
  },
  {
    id: 4,
    title: 'Inspect Emergency Lighting',
    description: 'Test emergency lights and exit signs',
    category: 'safety',
    priority: 'high',
    location: 'All Floors',
    instructions: 'Press test button on each unit, verify illumination',
    completed: false,
    notes: null,
    hasIssue: false,
    issueDescription: null
  },
  {
    id: 5,
    title: 'Check Fire Alarm Panel',
    description: 'Verify fire alarm panel shows no trouble conditions',
    category: 'safety',
    priority: 'critical',
    location: 'Security Office',
    instructions: 'Check for any active alarms or system faults',
    completed: false,
    notes: null,
    hasIssue: false,
    issueDescription: null
  },
  {
    id: 6,
    title: 'Inspect Cooling Towers',
    description: 'Check cooling tower water levels and fan operation',
    category: 'hvac',
    priority: 'medium',
    location: 'Roof',
    instructions: 'Inspect water level, fan belt tension, and listen for unusual noise',
    completed: false,
    notes: null,
    hasIssue: false,
    issueDescription: null
  },
  {
    id: 7,
    title: 'Check Water Pressure',
    description: 'Verify building water pressure is within normal range',
    category: 'plumbing',
    priority: 'medium',
    location: 'Mechanical Room',
    instructions: 'Record pressure readings at main and booster pumps',
    completed: false,
    notes: null,
    hasIssue: false,
    issueDescription: null
  },
  {
    id: 8,
    title: 'Inspect Access Control',
    description: 'Verify all access points are functioning correctly',
    category: 'security',
    priority: 'medium',
    location: 'All Entrances',
    instructions: 'Test card readers at main entrances and secure areas',
    completed: false,
    notes: null,
    hasIssue: false,
    issueDescription: null
  },
  {
    id: 9,
    title: 'Check Generator Status',
    description: 'Verify generator is in auto mode and fuel levels are adequate',
    category: 'electrical',
    priority: 'high',
    location: 'Generator Room',
    instructions: 'Check control panel for alarms, record fuel level',
    completed: false,
    notes: null,
    hasIssue: false,
    issueDescription: null
  },
  {
    id: 10,
    title: 'Inspect Elevators',
    description: 'Check elevator operation and emergency systems',
    category: 'general',
    priority: 'medium',
    location: 'All Elevators',
    instructions: 'Test call button, door operation, and emergency phone',
    completed: false,
    notes: null,
    hasIssue: false,
    issueDescription: null
  }
])

// UI State
const activeCategory = ref('all')
const showIssueDialog = ref(false)
const showNoteDialog = ref(false)
const selectedTask = ref<ChecklistTask | null>(null)

const issueForm = ref({
  description: '',
  priority: 'medium'
})

const noteForm = ref({
  note: ''
})

// Weekly performance data
const weeklyData = ref([
  { name: 'Mon', percentage: 85 },
  { name: 'Tue', percentage: 90 },
  { name: 'Wed', percentage: 78 },
  { name: 'Thu', percentage: 82 },
  { name: 'Fri', percentage: 88 },
  { name: 'Sat', percentage: 65 },
  { name: 'Sun', percentage: 70 }
])

// Computed
const totalTasks = computed(() => tasks.value.length)
const completedCount = computed(() => tasks.value.filter(t => t.completed).length)
const pendingCount = computed(() => tasks.value.filter(t => !t.completed && !t.hasIssue).length)
const issuesCount = computed(() => tasks.value.filter(t => t.hasIssue).length)
const completionPercentage = computed(() => Math.round((completedCount.value / totalTasks.value) * 100))

const progressColor = computed(() => {
  if (completionPercentage.value === 100) return '#67c23a'
  if (completionPercentage.value >= 75) return '#409eff'
  if (completionPercentage.value >= 50) return '#e6a23c'
  return '#f56c6c'
})

const filteredTasks = computed(() => {
  if (activeCategory.value === 'all') {
    return tasks.value
  }
  return tasks.value.filter(t => t.category === activeCategory.value)
})

// Methods
const getCategoryLabel = (category: string) => {
  const labels: Record<string, string> = {
    hvac: 'HVAC',
    electrical: 'Electrical',
    plumbing: 'Plumbing',
    safety: 'Safety',
    security: 'Security',
    general: 'General'
  }
  return labels[category] || category
}

const getPriorityLabel = (priority: string) => {
  const labels: Record<string, string> = {
    critical: 'Critical',
    high: 'High',
    medium: 'Medium',
    low: 'Low'
  }
  return labels[priority] || priority
}

const toggleTask = (task: ChecklistTask) => {
  if (task.hasIssue) {
    ElMessage.warning('Please resolve the reported issue before completing this task')
    return
  }
  task.completed = !task.completed
  ElMessage.success(task.completed ? `Task "${task.title}" completed` : `Task "${task.title}" reopened`)
}

const reportIssue = (task: ChecklistTask) => {
  selectedTask.value = task
  issueForm.value = { description: '', priority: 'medium' }
  showIssueDialog.value = true
}

const submitIssue = () => {
  if (!issueForm.value.description.trim()) {
    ElMessage.warning('Please enter issue description')
    return
  }

  if (selectedTask.value) {
    selectedTask.value.hasIssue = true
    selectedTask.value.issueDescription = issueForm.value.description
    selectedTask.value.completed = false
    ElMessage.warning(`Issue reported for "${selectedTask.value.title}"`)
  }
  showIssueDialog.value = false
}

const addNote = (task: ChecklistTask) => {
  selectedTask.value = task
  noteForm.value = { note: task.notes || '' }
  showNoteDialog.value = true
}

const submitNote = () => {
  if (selectedTask.value) {
    selectedTask.value.notes = noteForm.value.note
    ElMessage.success('Note added successfully')
  }
  showNoteDialog.value = false
}

const resetToday = () => {
  ElMessageBox.confirm(
      'Reset all tasks for today? All completed tasks will be marked as incomplete.',
      'Reset Confirmation',
      {
        confirmButtonText: 'Reset',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    tasks.value.forEach(task => {
      task.completed = false
    })
    ElMessage.success('All tasks reset')
  }).catch(() => {})
}

const exportReport = () => {
  ElMessage.success('Exporting report...')
  setTimeout(() => {
    ElMessage.success('Report exported: daily_checklist_' + new Date().toISOString().split('T')[0] + '.pdf')
  }, 1500)
}

const refreshData = () => {
  ElMessage.success('Data refreshed')
}

const handleTabClick = () => {}

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
.daily-checklist {
  padding: 24px;
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
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
  background: linear-gradient(135deg, #2e7d32, #43a047);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  margin: 0;
  color: #2e7d32;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

/* Progress Banner */
.progress-banner {
  background: white;
  border-radius: 20px;
  padding: 20px 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 8px;
}

.progress-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.progress-stats {
  font-size: 14px;
  color: #909399;
}

.progress-bar-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

.progress-bar-wrapper .el-progress {
  flex: 1;
}

.progress-percentage {
  font-size: 18px;
  font-weight: 700;
  color: #409eff;
  min-width: 50px;
}

.progress-message {
  font-size: 13px;
  padding: 8px 12px;
  border-radius: 8px;
  background: #f8f9fa;
}

.progress-message.warning { background: #fff7e6; color: #e6a23c; }
.progress-message.success { background: #e8f5e9; color: #67c23a; }

/* Stats Cards */
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

/* Category Tabs */
.category-tabs {
  background: white;
  border-radius: 20px;
  padding: 0 20px;
  margin-bottom: 20px;
}

.category-tabs :deep(.el-tabs__header) {
  margin-bottom: 0;
}

.category-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

/* Checklist Container */
.checklist-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.checklist-item {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  gap: 16px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #67c23a;
}

.checklist-item.completed {
  background: #f8f9fa;
  opacity: 0.85;
  border-left-color: #67c23a;
}

.checklist-item.hasIssue {
  border-left-color: #f56c6c;
  background: #fff5f5;
}

.checklist-item:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.item-checkbox {
  padding-top: 2px;
}

.item-content {
  flex: 1;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 8px;
}

.item-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.item-category {
  display: flex;
  gap: 8px;
}

.category-tag {
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
}

.category-tag.hvac { background: #e6f7ff; color: #409eff; }
.category-tag.electrical { background: #fff7e6; color: #e6a23c; }
.category-tag.plumbing { background: #e8f5e9; color: #67c23a; }
.category-tag.safety { background: #ffefef; color: #f56c6c; }
.category-tag.security { background: #f3e5f5; color: #9c27b0; }
.category-tag.general { background: #f5f5f5; color: #909399; }

.priority-tag {
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
}

.priority-tag.critical { background: #ffefef; color: #f56c6c; }
.priority-tag.high { background: #ffefef; color: #f56c6c; }
.priority-tag.medium { background: #fff7e6; color: #e6a23c; }
.priority-tag.low { background: #e8f5e9; color: #67c23a; }

.item-description {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
  line-height: 1.4;
}

.item-instructions, .item-notes {
  font-size: 12px;
  color: #409eff;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.item-notes {
  color: #e6a23c;
}

.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.item-location {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
}

.item-actions {
  display: flex;
  gap: 8px;
}

/* Summary Card */
.summary-card {
  border-radius: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.weekly-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.weekly-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.weekly-day {
  width: 40px;
  font-size: 13px;
  font-weight: 500;
}

.weekly-bar {
  flex: 1;
  height: 8px;
  background: #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.weekly-progress {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.weekly-percent {
  width: 45px;
  font-size: 12px;
  color: #909399;
}

/* Responsive */
@media (max-width: 768px) {
  .daily-checklist { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .item-header { flex-direction: column; align-items: flex-start; }
  .item-footer { flex-direction: column; align-items: flex-start; }
  .item-actions { width: 100%; justify-content: flex-end; }
  .progress-info { flex-direction: column; align-items: flex-start; }
}
</style>