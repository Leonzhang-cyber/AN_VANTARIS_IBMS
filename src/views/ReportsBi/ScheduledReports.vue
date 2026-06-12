<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Search, Refresh, Document, Download, Printer,
  Share, Star, Clock, Warning, CircleCheck,
  TrendCharts, DataLine, Calendar, Setting,
  Plus, Upload, Filter, ArrowUp, ArrowDown,
  View, User, Trophy, Medal, Timer, AlarmClock,
  Edit, Delete, VideoPlay, VideoPause,
  Message, Notification, SuccessFilled
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Loading scheduled jobs...',
  'Checking schedules...',
  'Preparing calendar...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedFrequency = ref('all')
const selectedStatus = ref('all')
const scheduleDetailsVisible = ref(false)
const editScheduleVisible = ref(false)
const chartRef = ref(null)

let scheduleChart: echarts.ECharts | null = null

// Frequency filters
const frequencyOptions = [
  { value: 'all', label: 'All Frequencies', icon: '🔄' },
  { value: 'daily', label: 'Daily', icon: '📅' },
  { value: 'weekly', label: 'Weekly', icon: '📆' },
  { value: 'monthly', label: 'Monthly', icon: '📊' },
  { value: 'quarterly', label: 'Quarterly', icon: '📈' },
  { value: 'yearly', label: 'Yearly', icon: '🏆' }
]

// Status filters
const statusOptions = [
  { value: 'all', label: 'All Status' },
  { value: 'active', label: 'Active' },
  { value: 'paused', label: 'Paused' },
  { value: 'completed', label: 'Completed' }
]

// Scheduled reports data
const scheduledReports = ref([
  {
    id: 'SCH001', name: 'Daily System Health Report', frequency: 'daily', time: '08:00 AM',
    recipients: ['admin@system.com', 'ops@system.com'], lastRun: '2024-01-15 08:00:00', nextRun: '2024-01-16 08:00:00',
    status: 'active', format: 'PDF', category: 'system', successRate: 98.5, totalRuns: 245,
    description: 'Daily report on system health metrics and alerts'
  },
  {
    id: 'SCH002', name: 'Weekly Energy Summary', frequency: 'weekly', time: 'Monday 09:00 AM',
    recipients: ['energy@system.com', 'finance@system.com'], lastRun: '2024-01-15 09:00:00', nextRun: '2024-01-22 09:00:00',
    status: 'active', format: 'Excel', category: 'energy', successRate: 99.2, totalRuns: 52,
    description: 'Weekly energy consumption and cost analysis'
  },
  {
    id: 'SCH003', name: 'Monthly Alarm Report', frequency: 'monthly', time: '1st day 10:00 AM',
    recipients: ['security@system.com', 'management@system.com'], lastRun: '2024-01-01 10:00:00', nextRun: '2024-02-01 10:00:00',
    status: 'active', format: 'PDF', category: 'alarms', successRate: 97.8, totalRuns: 24,
    description: 'Monthly alarm statistics and incident analysis'
  },
  {
    id: 'SCH004', name: 'Quarterly Performance Review', frequency: 'quarterly', time: 'Jan 15, Apr 15, Jul 15, Oct 15 11:00 AM',
    recipients: ['executive@system.com', 'board@system.com'], lastRun: '2024-01-15 11:00:00', nextRun: '2024-04-15 11:00:00',
    status: 'paused', format: 'PowerPoint', category: 'performance', successRate: 100, totalRuns: 8,
    description: 'Quarterly executive performance summary'
  },
  {
    id: 'SCH005', name: 'Yearly Sustainability Report', frequency: 'yearly', time: 'Jan 1 12:00 PM',
    recipients: ['sustainability@system.com', 'esg@system.com'], lastRun: '2024-01-01 12:00:00', nextRun: '2025-01-01 12:00:00',
    status: 'active', format: 'PDF', category: 'sustainability', successRate: 100, totalRuns: 3,
    description: 'Annual sustainability and ESG metrics'
  },
  {
    id: 'SCH006', name: 'Daily Maintenance Log', frequency: 'daily', time: '06:00 PM',
    recipients: ['maintenance@system.com'], lastRun: '2024-01-15 18:00:00', nextRun: '2024-01-16 18:00:00',
    status: 'active', format: 'CSV', category: 'maintenance', successRate: 96.5, totalRuns: 180,
    description: 'Daily maintenance activities and work orders'
  },
  {
    id: 'SCH007', name: 'Weekly Security Audit', frequency: 'weekly', time: 'Friday 05:00 PM',
    recipients: ['security@system.com', 'audit@system.com'], lastRun: '2024-01-12 17:00:00', nextRun: '2024-01-19 17:00:00',
    status: 'paused', format: 'PDF', category: 'security', successRate: 99.5, totalRuns: 45,
    description: 'Weekly security audit and compliance report'
  },
  {
    id: 'SCH008', name: 'Monthly Financial Summary', frequency: 'monthly', time: 'Last day 09:00 AM',
    recipients: ['finance@system.com', 'accounting@system.com'], lastRun: '2024-01-31 09:00:00', nextRun: '2024-02-29 09:00:00',
    status: 'active', format: 'Excel', category: 'financial', successRate: 98.9, totalRuns: 18,
    description: 'Monthly financial metrics and cost analysis'
  }
])

// Schedule statistics
const scheduleStats = reactive({
  total: 0,
  active: 0,
  paused: 0,
  completed: 0,
  daily: 0,
  weekly: 0,
  monthly: 0,
  quarterly: 0,
  yearly: 0,
  avgSuccessRate: 0,
  totalDeliveries: 0
})

// New schedule form
const newScheduleForm = reactive({
  name: '',
  frequency: 'daily',
  time: '09:00',
  dayOfWeek: 'Monday',
  dayOfMonth: 1,
  recipients: '',
  format: 'PDF',
  category: 'system',
  description: ''
})

// Edit schedule form
const editScheduleForm = reactive({
  id: '',
  name: '',
  frequency: '',
  time: '',
  recipients: '',
  format: '',
  category: '',
  description: '',
  status: ''
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 8,
  total: scheduledReports.value.length
})

// Filtered schedules
const filteredSchedules = computed(() => {
  let filtered = scheduledReports.value
  if (searchKeyword.value) {
    filtered = filtered.filter(s =>
        s.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        s.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        s.description.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedFrequency.value !== 'all') {
    filtered = filtered.filter(s => s.frequency === selectedFrequency.value)
  }
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(s => s.status === selectedStatus.value)
  }
  pagination.total = filtered.length
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// ==================== Loading Simulation ====================
onMounted(() => {
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 12 + 4
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
        initChart()
        updateStats()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  scheduleChart = echarts.init(chartRef.value)
  scheduleChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['Active', 'Paused', 'Completed'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: ['Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly'] },
    yAxis: { type: 'value', name: 'Number of Schedules' },
    series: [
      { name: 'Active', type: 'bar', data: [2, 1, 1, 0, 1], stack: 'total', itemStyle: { color: '#67C23A', borderRadius: [4, 4, 0, 0] } },
      { name: 'Paused', type: 'bar', data: [0, 1, 0, 1, 0], stack: 'total', itemStyle: { color: '#E6A23C', borderRadius: [4, 4, 0, 0] } },
      { name: 'Completed', type: 'bar', data: [0, 0, 0, 0, 0], stack: 'total', itemStyle: { color: '#909399', borderRadius: [4, 4, 0, 0] } }
    ]
  })
}

const updateStats = () => {
  scheduleStats.total = scheduledReports.value.length
  scheduleStats.active = scheduledReports.value.filter(s => s.status === 'active').length
  scheduleStats.paused = scheduledReports.value.filter(s => s.status === 'paused').length
  scheduleStats.completed = scheduledReports.value.filter(s => s.status === 'completed').length
  scheduleStats.daily = scheduledReports.value.filter(s => s.frequency === 'daily').length
  scheduleStats.weekly = scheduledReports.value.filter(s => s.frequency === 'weekly').length
  scheduleStats.monthly = scheduledReports.value.filter(s => s.frequency === 'monthly').length
  scheduleStats.quarterly = scheduledReports.value.filter(s => s.frequency === 'quarterly').length
  scheduleStats.yearly = scheduledReports.value.filter(s => s.frequency === 'yearly').length

  const successRates = scheduledReports.value.map(s => s.successRate)
  scheduleStats.avgSuccessRate = Math.round(successRates.reduce((a, b) => a + b, 0) / successRates.length)
  scheduleStats.totalDeliveries = scheduledReports.value.reduce((sum, s) => sum + s.totalRuns, 0)
}

const handleResize = () => {
  scheduleChart?.resize()
}

// ==================== Schedule Functions ====================
const refreshSchedules = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  loading.value = false
  ElMessage.success('Scheduled reports refreshed successfully')
}

const viewScheduleDetails = (schedule: any) => {
  selectedSchedule.value = schedule
  scheduleDetailsVisible.value = true
}

const editSchedule = (schedule: any) => {
  editScheduleForm.id = schedule.id
  editScheduleForm.name = schedule.name
  editScheduleForm.frequency = schedule.frequency
  editScheduleForm.time = schedule.time
  editScheduleForm.recipients = schedule.recipients.join(', ')
  editScheduleForm.format = schedule.format
  editScheduleForm.category = schedule.category
  editScheduleForm.description = schedule.description
  editScheduleForm.status = schedule.status
  editScheduleVisible.value = true
}

const saveScheduleEdit = async () => {
  if (!editScheduleForm.name) {
    ElMessage.warning('Please enter a schedule name')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1000))

  const index = scheduledReports.value.findIndex(s => s.id === editScheduleForm.id)
  if (index !== -1) {
    scheduledReports.value[index] = {
      ...scheduledReports.value[index],
      name: editScheduleForm.name,
      frequency: editScheduleForm.frequency,
      time: editScheduleForm.time,
      recipients: editScheduleForm.recipients.split(',').map(r => r.trim()),
      format: editScheduleForm.format,
      category: editScheduleForm.category,
      description: editScheduleForm.description,
      status: editScheduleForm.status
    }
  }

  updateStats()
  editScheduleVisible.value = false
  ElMessage.success('Schedule updated successfully')
}

const toggleScheduleStatus = async (schedule: any) => {
  const newStatus = schedule.status === 'active' ? 'paused' : 'active'
  const action = newStatus === 'active' ? 'resume' : 'pause'

  await ElMessageBox.confirm(
      `${action === 'resume' ? 'Resume' : 'Pause'} schedule "${schedule.name}"?`,
      'Confirm',
      {
        confirmButtonText: action === 'resume' ? 'Resume' : 'Pause',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  )

  const index = scheduledReports.value.findIndex(s => s.id === schedule.id)
  if (index !== -1) {
    scheduledReports.value[index].status = newStatus
  }

  updateStats()
  ElMessage.success(`Schedule ${action === 'resume' ? 'resumed' : 'paused'} successfully`)
}

const deleteSchedule = async (schedule: any) => {
  await ElMessageBox.confirm(
      `Delete schedule "${schedule.name}"? This action cannot be undone.`,
      'Confirm Delete',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'danger'
      }
  )

  const index = scheduledReports.value.findIndex(s => s.id === schedule.id)
  if (index !== -1) {
    scheduledReports.value.splice(index, 1)
  }

  updateStats()
  ElMessage.success('Schedule deleted successfully')
}

const runNow = async (schedule: any) => {
  ElMessage.info(`Manually running ${schedule.name}...`)
  await new Promise(resolve => setTimeout(resolve, 1500))
  ElMessage.success(`${schedule.name} executed successfully`)
}

const openCreateSchedule = () => {
  newScheduleForm.name = ''
  newScheduleForm.frequency = 'daily'
  newScheduleForm.time = '09:00'
  newScheduleForm.dayOfWeek = 'Monday'
  newScheduleForm.dayOfMonth = 1
  newScheduleForm.recipients = ''
  newScheduleForm.format = 'PDF'
  newScheduleForm.category = 'system'
  newScheduleForm.description = ''
  isCreatingNew.value = true
  editScheduleVisible.value = true
}

const createSchedule = async () => {
  if (!newScheduleForm.name) {
    ElMessage.warning('Please enter a schedule name')
    return
  }

  if (!newScheduleForm.recipients) {
    ElMessage.warning('Please enter at least one recipient')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1000))

  const newSchedule = {
    id: `SCH${String(scheduledReports.value.length + 1).padStart(3, '0')}`,
    name: newScheduleForm.name,
    frequency: newScheduleForm.frequency,
    time: newScheduleForm.frequency === 'daily' ? newScheduleForm.time :
        newScheduleForm.frequency === 'weekly' ? `${newScheduleForm.dayOfWeek} ${newScheduleForm.time}` :
            newScheduleForm.frequency === 'monthly' ? `${newScheduleForm.dayOfMonth}th day ${newScheduleForm.time}` :
                newScheduleForm.time,
    recipients: newScheduleForm.recipients.split(',').map(r => r.trim()),
    lastRun: 'Never',
    nextRun: 'Pending',
    status: 'active',
    format: newScheduleForm.format,
    category: newScheduleForm.category,
    successRate: 100,
    totalRuns: 0,
    description: newScheduleForm.description || 'New scheduled report'
  }

  scheduledReports.value.unshift(newSchedule)
  updateStats()
  editScheduleVisible.value = false
  isCreatingNew.value = false
  ElMessage.success('Schedule created successfully')
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'active': return 'success'
    case 'paused': return 'warning'
    case 'completed': return 'info'
    default: return 'info'
  }
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'active': return VideoPlay
    case 'paused': return VideoPause
    case 'completed': return CircleCheck
    default: return Clock
  }
}

const getFrequencyIcon = (frequency: string) => {
  switch (frequency) {
    case 'daily': return '📅'
    case 'weekly': return '📆'
    case 'monthly': return '📊'
    case 'quarterly': return '📈'
    case 'yearly': return '🏆'
    default: return '🔄'
  }
}

const getFormatColor = (format: string) => {
  switch (format) {
    case 'PDF': return '#F56C6C'
    case 'Excel': return '#67C23A'
    case 'CSV': return '#409EFF'
    case 'PowerPoint': return '#E6A23C'
    default: return '#909399'
  }
}

const isCreatingNew = ref(false)
const selectedSchedule = ref<any>(null)
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
          <span class="loading-title">Loading Scheduled Reports</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Reports & BI - Scheduled Reports</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="scheduled-reports-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Scheduled Reports</h1>
        <p class="page-subtitle">Automate report delivery to your team</p>
      </div>
      <div class="header-right">
        <el-button type="primary" size="large" @click="openCreateSchedule">
          <el-icon><Plus /></el-icon>
          New Schedule
        </el-button>
        <el-button size="large" @click="refreshSchedules" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total-icon">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ scheduleStats.total }}</div>
          <div class="stat-label">Total Schedules</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ scheduleStats.active }} Active</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon success-icon">
          <el-icon><SuccessFilled /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ scheduleStats.avgSuccessRate }}%</div>
          <div class="stat-label">Avg Success Rate</div>
        </div>
        <div class="stat-progress">
          <el-progress :percentage="scheduleStats.avgSuccessRate" :stroke-width="4" :show-text="false" />
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon deliveries-icon">
          <el-icon><Message /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ scheduleStats.totalDeliveries.toLocaleString() }}</div>
          <div class="stat-label">Total Deliveries</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">↑ 245 this month</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon paused-icon">
          <el-icon><VideoPause /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ scheduleStats.paused }}</div>
          <div class="stat-label">Paused</div>
        </div>
        <div class="stat-trend">
          <span class="trend-neutral">{{ scheduleStats.completed }} Completed</span>
        </div>
      </div>
    </div>

    <!-- Chart Section -->
    <div class="chart-section">
      <div class="section-header">
        <h3>Schedule Distribution by Frequency</h3>
        <el-button text type="primary" @click="initChart">Refresh</el-button>
      </div>
      <div ref="chartRef" class="schedule-chart" style="height: 320px"></div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-bar">
      <div class="filters-left">
        <div class="search-box">
          <el-input
              v-model="searchKeyword"
              placeholder="Search schedules..."
              :prefix-icon="Search"
              clearable
              style="width: 260px"
          />
        </div>
        <div class="frequency-filters">
          <button
              v-for="freq in frequencyOptions"
              :key="freq.value"
              class="frequency-chip"
              :class="{ active: selectedFrequency === freq.value }"
              @click="selectedFrequency = freq.value"
          >
            <span class="chip-icon">{{ freq.icon }}</span>
            <span>{{ freq.label }}</span>
          </button>
        </div>
      </div>
      <div class="filters-right">
        <el-select v-model="selectedStatus" placeholder="Status" clearable style="width: 120px">
          <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
        </el-select>
      </div>
    </div>

    <!-- Schedules Grid - Card Style -->
    <div class="schedules-grid">
      <div
          v-for="schedule in filteredSchedules"
          :key="schedule.id"
          class="schedule-card"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="card-category" :style="{ background: getFormatColor(schedule.format) }">
            {{ schedule.format.charAt(0) }}
          </div>
          <div class="card-status">
            <el-tag :type="getStatusType(schedule.status)" size="small" effect="light">
              <el-icon><component :is="getStatusIcon(schedule.status)" /></el-icon>
              {{ schedule.status.toUpperCase() }}
            </el-tag>
          </div>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <h4 class="card-title">{{ schedule.name }}</h4>
          <p class="card-description">{{ schedule.description }}</p>

          <!-- Schedule Info -->
          <div class="schedule-info">
            <div class="info-row">
              <span class="info-label">Frequency:</span>
              <span class="info-value">
                <span class="frequency-icon">{{ getFrequencyIcon(schedule.frequency) }}</span>
                {{ schedule.frequency.charAt(0).toUpperCase() + schedule.frequency.slice(1) }}
              </span>
            </div>
            <div class="info-row">
              <span class="info-label">Time:</span>
              <span class="info-value">
                <el-icon><Timer /></el-icon>
                {{ schedule.time }}
              </span>
            </div>
            <div class="info-row">
              <span class="info-label">Format:</span>
              <span class="info-value">
                <span class="format-badge" :style="{ background: getFormatColor(schedule.format) + '20', color: getFormatColor(schedule.format) }">
                  {{ schedule.format }}
                </span>
              </span>
            </div>
            <div class="info-row">
              <span class="info-label">Recipients:</span>
              <span class="info-value recipients">
                <el-icon><User /></el-icon>
                {{ schedule.recipients.length }} recipient(s)
              </span>
            </div>
          </div>

          <!-- Run Info -->
          <div class="run-info">
            <div class="run-item">
              <span class="run-label">Last Run:</span>
              <span class="run-value">{{ schedule.lastRun }}</span>
            </div>
            <div class="run-item">
              <span class="run-label">Next Run:</span>
              <span class="run-value">{{ schedule.nextRun }}</span>
            </div>
          </div>

          <!-- Success Rate -->
          <div class="success-rate">
            <div class="rate-header">
              <span>Success Rate</span>
              <span class="rate-value">{{ schedule.successRate }}%</span>
            </div>
            <el-progress :percentage="schedule.successRate" :stroke-width="6" :show-text="false" />
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="footer-stats">
            <span class="stat-item">
              <el-icon><Document /></el-icon>
              {{ schedule.totalRuns }} runs
            </span>
          </div>
          <div class="card-actions">
            <el-button circle size="small" @click="runNow(schedule)">
              <el-icon><VideoPlay /></el-icon>
            </el-button>
            <el-button circle size="small" type="primary" @click="editSchedule(schedule)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button circle size="small" @click="viewScheduleDetails(schedule)">
              <el-icon><View /></el-icon>
            </el-button>
            <el-button circle size="small" type="danger" @click="deleteSchedule(schedule)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredSchedules.length === 0" class="empty-state">
      <el-empty description="No scheduled reports found">
        <el-button type="primary" @click="openCreateSchedule">Create Schedule</el-button>
      </el-empty>
    </div>

    <!-- Pagination -->
    <div v-if="filteredSchedules.length > 0" class="pagination-wrapper">
      <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[8, 12, 16, 24]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
      />
    </div>

    <!-- Schedule Details Dialog -->
    <el-dialog v-model="scheduleDetailsVisible" :title="selectedSchedule?.name" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Schedule ID">{{ selectedSchedule?.id }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusType(selectedSchedule?.status)" size="small">
            {{ selectedSchedule?.status?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Frequency">{{ selectedSchedule?.frequency?.toUpperCase() }}</el-descriptions-item>
        <el-descriptions-item label="Time">{{ selectedSchedule?.time }}</el-descriptions-item>
        <el-descriptions-item label="Format">{{ selectedSchedule?.format }}</el-descriptions-item>
        <el-descriptions-item label="Category">{{ selectedSchedule?.category?.toUpperCase() }}</el-descriptions-item>
        <el-descriptions-item label="Success Rate">{{ selectedSchedule?.successRate }}%</el-descriptions-item>
        <el-descriptions-item label="Total Runs">{{ selectedSchedule?.totalRuns }}</el-descriptions-item>
        <el-descriptions-item label="Last Run">{{ selectedSchedule?.lastRun }}</el-descriptions-item>
        <el-descriptions-item label="Next Run">{{ selectedSchedule?.nextRun }}</el-descriptions-item>
        <el-descriptions-item label="Recipients" :span="2">
          <div class="recipients-list">
            <el-tag v-for="r in selectedSchedule?.recipients" :key="r" size="small" style="margin: 2px">
              {{ r }}
            </el-tag>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedSchedule?.description }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="scheduleDetailsVisible = false">Close</el-button>
        <el-button type="primary" @click="runNow(selectedSchedule)">Run Now</el-button>
      </template>
    </el-dialog>

    <!-- Create/Edit Schedule Dialog -->
    <el-dialog v-model="editScheduleVisible" :title="isCreatingNew ? 'New Schedule' : 'Edit Schedule'" width="550px">
      <el-form v-if="isCreatingNew" :model="newScheduleForm" label-width="120px">
        <el-form-item label="Schedule Name" required>
          <el-input v-model="newScheduleForm.name" placeholder="Enter schedule name" />
        </el-form-item>
        <el-form-item label="Frequency" required>
          <el-select v-model="newScheduleForm.frequency" style="width: 100%">
            <el-option v-for="f in frequencyOptions.slice(1)" :key="f.value" :label="f.label" :value="f.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Time" required>
          <el-time-picker
              v-model="newScheduleForm.time"
              format="HH:mm"
              value-format="HH:mm"
              placeholder="Select time"
              style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="Recipients" required>
          <el-input
              v-model="newScheduleForm.recipients"
              placeholder="email@example.com, another@example.com"
          />
          <div class="form-hint">Separate multiple emails with commas</div>
        </el-form-item>
        <el-form-item label="Format">
          <el-select v-model="newScheduleForm.format" style="width: 100%">
            <el-option label="PDF" value="PDF" />
            <el-option label="Excel" value="Excel" />
            <el-option label="CSV" value="CSV" />
            <el-option label="PowerPoint" value="PowerPoint" />
          </el-select>
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="newScheduleForm.category" style="width: 100%">
            <el-option label="System Health" value="system" />
            <el-option label="Energy" value="energy" />
            <el-option label="Alarms" value="alarms" />
            <el-option label="Maintenance" value="maintenance" />
            <el-option label="Financial" value="financial" />
            <el-option label="Sustainability" value="sustainability" />
            <el-option label="Security" value="security" />
            <el-option label="Performance" value="performance" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description">
          <el-input
              v-model="newScheduleForm.description"
              type="textarea"
              rows="2"
              placeholder="Optional description"
          />
        </el-form-item>
      </el-form>

      <el-form v-else :model="editScheduleForm" label-width="120px">
        <el-form-item label="Schedule Name" required>
          <el-input v-model="editScheduleForm.name" placeholder="Enter schedule name" />
        </el-form-item>
        <el-form-item label="Frequency" required>
          <el-select v-model="editScheduleForm.frequency" style="width: 100%">
            <el-option v-for="f in frequencyOptions.slice(1)" :key="f.value" :label="f.label" :value="f.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Time" required>
          <el-time-picker
              v-model="editScheduleForm.time"
              format="HH:mm"
              value-format="HH:mm"
              placeholder="Select time"
              style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="Recipients" required>
          <el-input
              v-model="editScheduleForm.recipients"
              placeholder="email@example.com, another@example.com"
          />
          <div class="form-hint">Separate multiple emails with commas</div>
        </el-form-item>
        <el-form-item label="Format">
          <el-select v-model="editScheduleForm.format" style="width: 100%">
            <el-option label="PDF" value="PDF" />
            <el-option label="Excel" value="Excel" />
            <el-option label="CSV" value="CSV" />
            <el-option label="PowerPoint" value="PowerPoint" />
          </el-select>
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="editScheduleForm.category" style="width: 100%">
            <el-option label="System Health" value="system" />
            <el-option label="Energy" value="energy" />
            <el-option label="Alarms" value="alarms" />
            <el-option label="Maintenance" value="maintenance" />
            <el-option label="Financial" value="financial" />
            <el-option label="Sustainability" value="sustainability" />
            <el-option label="Security" value="security" />
            <el-option label="Performance" value="performance" />
          </el-select>
        </el-form-item>
        <el-form-item label="Status">
          <el-select v-model="editScheduleForm.status" style="width: 100%">
            <el-option label="Active" value="active" />
            <el-option label="Paused" value="paused" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description">
          <el-input
              v-model="editScheduleForm.description"
              type="textarea"
              rows="2"
              placeholder="Optional description"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="editScheduleVisible = false">Cancel</el-button>
        <el-button type="primary" @click="isCreatingNew ? createSchedule() : saveScheduleEdit()">
          {{ isCreatingNew ? 'Create Schedule' : 'Save Changes' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

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

.spinner-ring:nth-child(1) {
  border-top-color: #3b82f6;
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  border-right-color: #f59e0b;
  animation-delay: 0.2s;
  width: 70%;
  height: 70%;
  top: 15%;
  left: 15%;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #10b981;
  animation-delay: 0.4s;
  width: 40%;
  height: 40%;
  top: 30%;
  left: 30%;
}

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
.scheduled-reports-container {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #eef2f6 100%);
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #1e293b 0%, #2d3a4e 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
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
  margin-bottom: 28px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.total-icon {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #409eff;
}

.success-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.deliveries-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.paused-icon {
  background: linear-gradient(135deg, #fef0f0 0%, #fcd9d9 100%);
  color: #f56c6c;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  margin-top: 4px;
}

.stat-trend {
  position: absolute;
  top: 16px;
  right: 16px;
}

.trend-up {
  font-size: 11px;
  color: #67c23a;
  background: #f0f9ff;
  padding: 4px 8px;
  border-radius: 20px;
}

.trend-neutral {
  font-size: 11px;
  color: #909399;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 20px;
}

.stat-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
}

/* Chart Section */
.chart-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
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
  color: #1e293b;
  margin: 0;
}

.schedule-chart {
  width: 100%;
}

/* Filters Bar */
.filters-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 24px;
}

.filters-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.frequency-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.frequency-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 40px;
  font-size: 13px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s ease;
}

.frequency-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.frequency-chip.active {
  background: #409eff;
  border-color: #409eff;
  color: white;
}

.chip-icon {
  font-size: 14px;
}

.filters-right {
  display: flex;
  gap: 12px;
}

/* Schedules Grid */
.schedules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.schedule-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
}

.schedule-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 0 20px;
}

.card-category {
  width: 44px;
  height: 44px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 600;
  color: white;
}

/* Card Body */
.card-body {
  padding: 16px 20px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 10px 0;
  line-height: 1.4;
}

.card-description {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.schedule-info {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 12px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  color: #909399;
}

.info-value {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #1e293b;
  font-weight: 500;
}

.frequency-icon {
  font-size: 14px;
}

.format-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.recipients {
  color: #409eff;
}

.run-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 12px;
}

.run-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.run-label {
  color: #909399;
  font-size: 11px;
}

.run-value {
  color: #1e293b;
  font-weight: 500;
  font-size: 12px;
}

.success-rate {
  margin-top: 12px;
}

.rate-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 12px;
  color: #606266;
}

.rate-value {
  font-weight: 600;
  color: #67c23a;
}

/* Card Footer */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px 16px 20px;
  border-top: 1px solid #f0f0f0;
  background: #fafbfc;
}

.footer-stats {
  display: flex;
  gap: 12px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #606266;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.card-actions .el-button {
  background: white;
  border: 1px solid #e4e7ed;
}

.card-actions .el-button:hover {
  transform: scale(1.05);
}

/* Empty State */
.empty-state {
  padding: 60px 0;
  text-align: center;
}

/* Pagination */
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
}

/* Form Hint */
.form-hint {
  font-size: 11px;
  color: #909399;
  margin-top: 4px;
}

/* Recipients List */
.recipients-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .schedules-grid {
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  }
}

@media (max-width: 768px) {
  .scheduled-reports-container {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filters-left {
    flex-direction: column;
  }

  .frequency-filters {
    justify-content: center;
  }

  .page-header {
    flex-direction: column;
    text-align: center;
  }

  .header-right {
    width: 100%;
    justify-content: center;
  }

  .schedules-grid {
    grid-template-columns: 1fr;
  }
}
</style>