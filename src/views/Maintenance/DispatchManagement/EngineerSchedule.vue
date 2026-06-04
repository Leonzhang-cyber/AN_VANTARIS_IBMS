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
          <span class="loading-title">Engineer Schedule</span>
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
  <div v-else class="engineer-schedule-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><User /></el-icon>
          Engineer Schedule
        </h1>
        <div class="page-subtitle">Manage engineer shifts and assignments</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddDialog">
          <el-icon><Plus /></el-icon> Add Schedule
        </el-button>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon> Refresh
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
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">Total Engineers</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.onDutyToday }}</div>
          <div class="stat-label">On Duty Today</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Star /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.avgRating }}</div>
          <div class="stat-label">Avg Rating</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><Iphone /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.online }}</div>
          <div class="stat-label">Online Now</div>
        </div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search engineer..."
            style="width: 240px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
          <el-option label="Online" value="online" />
          <el-option label="Busy" value="busy" />
          <el-option label="Offline" value="offline" />
        </el-select>
      </div>
      <div class="filter-right">
        <div class="week-navigation">
          <el-button @click="previousWeek" :icon="ArrowLeft" circle size="small" />
          <span class="week-range">{{ weekRange }}</span>
          <el-button @click="nextWeek" :icon="ArrowRight" circle size="small" />
          <el-button @click="goToToday" size="small">Today</el-button>
        </div>
      </div>
    </div>

    <!-- Date Picker Row -->
    <div class="date-picker-row">
      <el-date-picker
          v-model="selectedDate"
          type="date"
          placeholder="Select date"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="onDateChange"
      />
      <el-radio-group v-model="viewMode" size="small">
        <el-radio-button label="week">Week View</el-radio-button>
        <el-radio-button label="month">Month View</el-radio-button>
      </el-radio-group>
    </div>

    <!-- Week Schedule Table -->
    <div class="schedule-section" v-if="viewMode === 'week'">
      <div class="section-header">
        <h3><el-icon><Calendar /></el-icon> Weekly Schedule</h3>
        <el-button type="primary" link @click="openAddDialog">+ Add Schedule</el-button>
      </div>
      <div class="schedule-table-wrapper">
        <table class="schedule-table week-table">
          <thead>
          <tr>
            <th class="engineer-col">Engineer</th>
            <th v-for="day in weekDays" :key="day.date" class="date-col">
              <div class="date-header">
                <div class="day-name">{{ day.name }}</div>
                <div class="day-date">{{ day.date }}</div>
              </div>
            </th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="engineer in filteredEngineers" :key="engineer.id">
            <td class="engineer-cell">
              <div class="engineer-info-cell">
                <div class="cell-avatar" :class="engineer.status">
                  {{ engineer.name.charAt(0) }}
                </div>
                <div class="engineer-details">
                  <div class="engineer-name-cell">{{ engineer.name }}</div>
                  <div class="engineer-role-cell">{{ engineer.role }}</div>
                </div>
              </div>
            </td>
            <td v-for="day in weekDays" :key="day.date" class="schedule-cell"
                :class="getScheduleCellClass(engineer.id, day.date)"
                @click="openScheduleForDate(engineer, day.date)">
              <div v-if="getScheduleForDay(engineer.id, day.date)" class="schedule-content">
                <div class="shift-badge" :class="getShiftClass(getScheduleForDay(engineer.id, day.date).shift)">
                  {{ getShiftText(getScheduleForDay(engineer.id, day.date).shift) }}
                </div>
                <div class="shift-time">{{ getScheduleForDay(engineer.id, day.date).startTime }} - {{ getScheduleForDay(engineer.id, day.date).endTime }}</div>
                <div class="task-count" v-if="getScheduleForDay(engineer.id, day.date).taskCount > 0">
                  📋 {{ getScheduleForDay(engineer.id, day.date).taskCount }} tasks
                </div>
                <div class="status-badge" :class="getScheduleForDay(engineer.id, day.date).status">
                  {{ getStatusText(getScheduleForDay(engineer.id, day.date).status) }}
                </div>
              </div>
              <div v-else class="empty-schedule" @click.stop="openAddScheduleForDay(engineer, day.date)">
                <span class="add-icon">+</span>
                <span class="add-text">Add</span>
              </div>
            </td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Month View -->
    <div class="schedule-section" v-else>
      <div class="section-header">
        <h3><el-icon><Calendar /></el-icon> Monthly Schedule - {{ currentMonthYear }}</h3>
        <el-button type="primary" link @click="openAddDialog">+ Add Schedule</el-button>
      </div>
      <div class="month-view">
        <div class="month-header">
          <div class="month-day">Mon</div>
          <div class="month-day">Tue</div>
          <div class="month-day">Wed</div>
          <div class="month-day">Thu</div>
          <div class="month-day">Fri</div>
          <div class="month-day">Sat</div>
          <div class="month-day">Sun</div>
        </div>
        <div class="month-grid">
          <div v-for="(day, idx) in monthDays" :key="idx" class="month-cell"
               :class="{ 'other-month': !day.isCurrentMonth, 'has-schedule': day.hasSchedule }"
               @click="openDaySchedule(day.date)">
            <div class="month-day-number">{{ day.day }}</div>
            <div class="month-schedule-count" v-if="day.scheduleCount > 0">
              {{ day.scheduleCount }} schedules
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Schedule Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="scheduleForm" label-width="100px">
        <el-form-item label="Engineer" required>
          <el-select v-model="scheduleForm.engineerId" placeholder="Select engineer" style="width: 100%">
            <el-option
                v-for="eng in engineers"
                :key="eng.id"
                :label="eng.name"
                :value="eng.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Date" required>
          <el-date-picker
              v-model="scheduleForm.date"
              type="date"
              placeholder="Select date"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="Shift" required>
          <el-radio-group v-model="scheduleForm.shift">
            <el-radio value="morning">Morning (09:00 - 18:00)</el-radio>
            <el-radio value="afternoon">Afternoon (14:00 - 23:00)</el-radio>
            <el-radio value="night">Night (22:00 - 07:00)</el-radio>
            <el-radio value="on-call">On Call (24/7)</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Status">
          <el-select v-model="scheduleForm.status" style="width: 100%">
            <el-option label="On Duty" value="on-duty" />
            <el-option label="Off Duty" value="off-duty" />
            <el-option label="On Leave" value="on-leave" />
            <el-option label="On Call" value="on-call" />
          </el-select>
        </el-form-item>
        <el-form-item label="Task Count">
          <el-input-number v-model="scheduleForm.taskCount" :min="0" :max="10" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Notes">
          <el-input v-model="scheduleForm.notes" type="textarea" :rows="2" placeholder="Additional notes..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveSchedule">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  User, Plus, Refresh, Search, Star, Clock, Document,
  Edit, Delete, Message, Calendar, Iphone, ChatDotRound, ArrowLeft, ArrowRight
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading engineer data...',
  'Initializing schedule...',
  'Almost ready...'
]

// ==================== Types ====================
interface Engineer {
  id: number
  name: string
  email: string
  phone: string
  role: string
  skills: string[]
  status: 'online' | 'busy' | 'offline'
  rating: number
}

interface Schedule {
  id: number
  engineerId: number
  engineerName: string
  date: string
  shift: 'morning' | 'afternoon' | 'night' | 'on-call'
  startTime: string
  endTime: string
  status: 'on-duty' | 'off-duty' | 'on-leave' | 'on-call'
  taskCount: number
  notes: string
}

// ==================== Mock Data ====================
const engineers = ref<Engineer[]>([
  { id: 1, name: 'John Chen', email: 'john.chen@ibms.com', phone: '+65 9123 4567', role: 'Senior Technician', skills: ['electrical', 'ups', 'pdu'], status: 'online', rating: 4.8 },
  { id: 2, name: 'Sarah Wong', email: 'sarah.wong@ibms.com', phone: '+65 9234 5678', role: 'HVAC Specialist', skills: ['hvac', 'crac', 'plumbing'], status: 'online', rating: 4.9 },
  { id: 3, name: 'Mike Lim', email: 'mike.lim@ibms.com', phone: '+65 9345 6789', role: 'Electrical Engineer', skills: ['electrical', 'mechanical', 'generator'], status: 'busy', rating: 4.7 },
  { id: 4, name: 'David Tan', email: 'david.tan@ibms.com', phone: '+65 9456 7890', role: 'General Technician', skills: ['hvac', 'plumbing'], status: 'offline', rating: 4.5 },
  { id: 5, name: 'Lisa Ng', email: 'lisa.ng@ibms.com', phone: '+65 9567 8901', role: 'Network Specialist', skills: ['network', 'security'], status: 'online', rating: 5.0 },
  { id: 6, name: 'Kevin Lim', email: 'kevin.lim@ibms.com', phone: '+65 9678 9012', role: 'UPS Specialist', skills: ['electrical', 'ups'], status: 'online', rating: 4.6 },
  { id: 7, name: 'Ahmad Razak', email: 'ahmad.razak@ibms.com', phone: '+65 9789 0123', role: 'HVAC Technician', skills: ['hvac', 'mechanical'], status: 'busy', rating: 4.4 },
  { id: 8, name: 'Tan Wei Ming', email: 'tan.weiming@ibms.com', phone: '+65 9890 1234', role: 'Generator Specialist', skills: ['electrical', 'generator'], status: 'online', rating: 4.7 }
])

// Generate schedules for multiple days
const generateSchedules = (): Schedule[] => {
  const today = new Date()
  const schedules: Schedule[] = []

  const shifts = ['morning', 'afternoon', 'night', 'on-call'] as const
  const statuses = ['on-duty', 'on-duty', 'on-duty', 'on-leave', 'on-call'] as const

  for (let i = -3; i <= 10; i++) {
    const date = new Date(today)
    date.setDate(today.getDate() + i)
    const dateStr = date.toISOString().slice(0, 10)

    engineers.value.forEach((engineer, idx) => {
      if (Math.random() > 0.3) {
        const shiftIdx = (engineer.id + i) % shifts.length
        const statusIdx = (engineer.id + i) % statuses.length
        const shift = shifts[shiftIdx]

        const timeMap = {
          morning: { start: '09:00', end: '18:00' },
          afternoon: { start: '14:00', end: '23:00' },
          night: { start: '22:00', end: '07:00' },
          'on-call': { start: '00:00', end: '24:00' }
        }

        schedules.push({
          id: schedules.length + 1,
          engineerId: engineer.id,
          engineerName: engineer.name,
          date: dateStr,
          shift: shift,
          startTime: timeMap[shift].start,
          endTime: timeMap[shift].end,
          status: statuses[statusIdx],
          taskCount: Math.floor(Math.random() * 5),
          notes: ''
        })
      }
    })
  }

  return schedules
}

const schedules = ref<Schedule[]>(generateSchedules())

// ==================== State ====================
const searchText = ref('')
const statusFilter = ref('')
const dialogVisible = ref(false)
const dialogTitle = ref('Add Schedule')
const editingSchedule = ref<Schedule | null>(null)
const viewMode = ref<'week' | 'month'>('week')
const selectedDate = ref(getTodayDate())
const currentWeekStart = ref(new Date())

const scheduleForm = ref({
  id: null as number | null,
  engineerId: null as number | null,
  date: getTodayDate(),
  shift: 'morning' as 'morning' | 'afternoon' | 'night' | 'on-call',
  status: 'on-duty' as 'on-duty' | 'off-duty' | 'on-leave' | 'on-call',
  taskCount: 0,
  notes: ''
})

// ==================== Helper Functions ====================
function getTodayDate(): string {
  return new Date().toISOString().slice(0, 10)
}

function formatDate(date: Date): string {
  return date.toISOString().slice(0, 10)
}

// ==================== Computed ====================
const filteredEngineers = computed(() => {
  let filtered = engineers.value
  if (searchText.value) {
    filtered = filtered.filter(e => e.name.toLowerCase().includes(searchText.value.toLowerCase()))
  }
  if (statusFilter.value) {
    filtered = filtered.filter(e => e.status === statusFilter.value)
  }
  return filtered
})

const weekDays = computed(() => {
  const days = []
  const start = new Date(currentWeekStart.value)
  for (let i = 0; i < 7; i++) {
    const date = new Date(start)
    date.setDate(start.getDate() + i)
    days.push({
      name: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][date.getDay() === 0 ? 6 : date.getDay() - 1],
      date: formatDate(date),
      fullDate: date
    })
  }
  return days
})

const weekRange = computed(() => {
  if (weekDays.value.length === 0) return ''
  return `${weekDays.value[0].date} - ${weekDays.value[6].date}`
})

const currentMonthYear = computed(() => {
  const date = new Date(selectedDate.value)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long' })
})

const monthDays = computed(() => {
  const date = new Date(selectedDate.value)
  const year = date.getFullYear()
  const month = date.getMonth()

  const firstDayOfMonth = new Date(year, month, 1)
  const startDayOfWeek = firstDayOfMonth.getDay() === 0 ? 6 : firstDayOfMonth.getDay() - 1

  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const daysInPrevMonth = new Date(year, month, 0).getDate()

  const days = []

  // Previous month days
  for (let i = startDayOfWeek - 1; i >= 0; i--) {
    const dayDate = daysInPrevMonth - i
    const dateStr = formatDate(new Date(year, month - 1, dayDate))
    days.push({
      day: dayDate,
      date: dateStr,
      isCurrentMonth: false,
      hasSchedule: getScheduleCountForDate(dateStr) > 0,
      scheduleCount: getScheduleCountForDate(dateStr)
    })
  }

  // Current month days
  for (let i = 1; i <= daysInMonth; i++) {
    const dateStr = formatDate(new Date(year, month, i))
    days.push({
      day: i,
      date: dateStr,
      isCurrentMonth: true,
      hasSchedule: getScheduleCountForDate(dateStr) > 0,
      scheduleCount: getScheduleCountForDate(dateStr)
    })
  }

  // Next month days (to fill 42 cells - 6 rows)
  const remaining = 42 - days.length
  for (let i = 1; i <= remaining; i++) {
    const dateStr = formatDate(new Date(year, month + 1, i))
    days.push({
      day: i,
      date: dateStr,
      isCurrentMonth: false,
      hasSchedule: getScheduleCountForDate(dateStr) > 0,
      scheduleCount: getScheduleCountForDate(dateStr)
    })
  }

  return days
})

const stats = computed(() => ({
  total: engineers.value.length,
  online: engineers.value.filter(e => e.status === 'online').length,
  busy: engineers.value.filter(e => e.status === 'busy').length,
  onDutyToday: getScheduleCountForDate(getTodayDate()),
  avgRating: (engineers.value.reduce((sum, e) => sum + e.rating, 0) / engineers.value.length).toFixed(1)
}))

// ==================== Schedule Helper Functions ====================
function getScheduleForDay(engineerId: number, date: string): Schedule | undefined {
  return schedules.value.find(s => s.engineerId === engineerId && s.date === date)
}

function getScheduleCountForDate(date: string): number {
  return schedules.value.filter(s => s.date === date).length
}

function getScheduleCellClass(engineerId: number, date: string): string {
  const schedule = getScheduleForDay(engineerId, date)
  if (!schedule) return 'empty'
  if (schedule.status === 'on-leave') return 'leave'
  if (schedule.status === 'on-call') return 'on-call'
  return 'occupied'
}

function getShiftClass(shift: string): string {
  const map: Record<string, string> = {
    morning: 'shift-morning',
    afternoon: 'shift-afternoon',
    night: 'shift-night',
    'on-call': 'shift-oncall'
  }
  return map[shift] || ''
}

// ==================== Navigation Methods ====================
function previousWeek() {
  currentWeekStart.value.setDate(currentWeekStart.value.getDate() - 7)
  currentWeekStart.value = new Date(currentWeekStart.value)
}

function nextWeek() {
  currentWeekStart.value.setDate(currentWeekStart.value.getDate() + 7)
  currentWeekStart.value = new Date(currentWeekStart.value)
}

function goToToday() {
  currentWeekStart.value = new Date()
  const day = currentWeekStart.value.getDay()
  const diff = day === 0 ? 6 : day - 1
  currentWeekStart.value.setDate(currentWeekStart.value.getDate() - diff)
  currentWeekStart.value = new Date(currentWeekStart.value)
  selectedDate.value = getTodayDate()
}

function onDateChange() {
  const date = new Date(selectedDate.value)
  const day = date.getDay()
  const diff = day === 0 ? 6 : day - 1
  currentWeekStart.value = new Date(date)
  currentWeekStart.value.setDate(date.getDate() - diff)
  currentWeekStart.value = new Date(currentWeekStart.value)
}

function openDaySchedule(date: string) {
  selectedDate.value = date
  viewMode.value = 'week'
  onDateChange()
}

function openScheduleForDate(engineer: Engineer, date: string) {
  const schedule = getScheduleForDay(engineer.id, date)
  if (schedule) {
    editSchedule(schedule)
  } else {
    openAddScheduleForDay(engineer, date)
  }
}

function openAddScheduleForDay(engineer: Engineer, date: string) {
  dialogTitle.value = `Add Schedule for ${engineer.name}`
  editingSchedule.value = null
  scheduleForm.value = {
    id: null,
    engineerId: engineer.id,
    date: date,
    shift: 'morning',
    status: 'on-duty',
    taskCount: 0,
    notes: ''
  }
  dialogVisible.value = true
}

// ==================== CRUD Methods ====================
const getShiftText = (shift: string) => {
  const map: Record<string, string> = {
    morning: 'Morning', afternoon: 'Afternoon', night: 'Night', 'on-call': 'On Call'
  }
  return map[shift] || shift
}

const getShiftTagType = (shift: string) => {
  const map: Record<string, string> = {
    morning: 'primary', afternoon: 'warning', night: 'info', 'on-call': 'danger'
  }
  return map[shift] || ''
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    online: 'success', busy: 'warning', offline: 'info',
    'on-duty': 'success', 'off-duty': 'info', 'on-leave': 'danger', 'on-call': 'warning'
  }
  return map[status] || ''
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    online: 'Online', busy: 'Busy', offline: 'Offline',
    'on-duty': 'On Duty', 'off-duty': 'Off Duty', 'on-leave': 'On Leave', 'on-call': 'On Call'
  }
  return map[status] || status
}

const getStarRating = (rating: number) => {
  const fullStars = Math.floor(rating)
  const hasHalfStar = rating % 1 >= 0.5
  const stars = []
  for (let i = 0; i < fullStars; i++) stars.push('full')
  if (hasHalfStar) stars.push('half')
  while (stars.length < 5) stars.push('empty')
  return stars
}

const getEngineerTodayShift = (engineerId: number) => {
  const schedule = getScheduleForDay(engineerId, getTodayDate())
  return schedule ? getShiftText(schedule.shift) : 'Not Scheduled'
}

const getEngineerTodayTasks = (engineerId: number) => {
  const schedule = getScheduleForDay(engineerId, getTodayDate())
  return schedule?.taskCount || 0
}

const openAddDialog = () => {
  dialogTitle.value = 'Add Schedule'
  editingSchedule.value = null
  scheduleForm.value = {
    id: null,
    engineerId: null,
    date: getTodayDate(),
    shift: 'morning',
    status: 'on-duty',
    taskCount: 0,
    notes: ''
  }
  dialogVisible.value = true
}

const openScheduleForEngineer = (engineer: Engineer) => {
  dialogTitle.value = `Add Schedule for ${engineer.name}`
  editingSchedule.value = null
  scheduleForm.value = {
    id: null,
    engineerId: engineer.id,
    date: getTodayDate(),
    shift: 'morning',
    status: 'on-duty',
    taskCount: 0,
    notes: ''
  }
  dialogVisible.value = true
}

const editSchedule = (schedule: Schedule) => {
  dialogTitle.value = 'Edit Schedule'
  editingSchedule.value = schedule
  scheduleForm.value = {
    id: schedule.id,
    engineerId: schedule.engineerId,
    date: schedule.date,
    shift: schedule.shift,
    status: schedule.status,
    taskCount: schedule.taskCount,
    notes: schedule.notes
  }
  dialogVisible.value = true
}

const deleteSchedule = (schedule: Schedule) => {
  ElMessageBox.confirm(
      `Delete schedule for ${schedule.engineerName} on ${schedule.date}?`,
      'Confirm Delete',
      { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' }
  ).then(() => {
    const index = schedules.value.findIndex(s => s.id === schedule.id)
    if (index !== -1) {
      schedules.value.splice(index, 1)
      ElMessage.success('Schedule deleted')
    }
  }).catch(() => {})
}

const saveSchedule = () => {
  if (!scheduleForm.value.engineerId || !scheduleForm.value.date) {
    ElMessage.warning('Please fill all required fields')
    return
  }

  const engineer = engineers.value.find(e => e.id === scheduleForm.value.engineerId)
  if (!engineer) return

  const getTimeRange = (shift: string) => {
    const map: Record<string, { start: string; end: string }> = {
      morning: { start: '09:00', end: '18:00' },
      afternoon: { start: '14:00', end: '23:00' },
      night: { start: '22:00', end: '07:00' },
      'on-call': { start: '00:00', end: '24:00' }
    }
    return map[shift] || { start: '09:00', end: '18:00' }
  }

  const timeRange = getTimeRange(scheduleForm.value.shift)

  if (scheduleForm.value.id) {
    const index = schedules.value.findIndex(s => s.id === scheduleForm.value.id)
    if (index !== -1) {
      schedules.value[index] = {
        ...schedules.value[index],
        engineerId: scheduleForm.value.engineerId,
        engineerName: engineer.name,
        date: scheduleForm.value.date,
        shift: scheduleForm.value.shift,
        startTime: timeRange.start,
        endTime: timeRange.end,
        status: scheduleForm.value.status,
        taskCount: scheduleForm.value.taskCount,
        notes: scheduleForm.value.notes
      }
      ElMessage.success('Schedule updated')
    }
  } else {
    const newId = Math.max(...schedules.value.map(s => s.id), 0) + 1
    schedules.value.push({
      id: newId,
      engineerId: scheduleForm.value.engineerId,
      engineerName: engineer.name,
      date: scheduleForm.value.date,
      shift: scheduleForm.value.shift,
      startTime: timeRange.start,
      endTime: timeRange.end,
      status: scheduleForm.value.status,
      taskCount: scheduleForm.value.taskCount,
      notes: scheduleForm.value.notes
    })
    ElMessage.success('Schedule added')
  }

  dialogVisible.value = false
}

const refreshData = () => {
  ElMessage.success('Data refreshed')
}

// ==================== Lifecycle ====================
onMounted(() => {
  let messageIndex = 0
  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 90) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 90) loadingProgress.value = 90
    }
  }, 200)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(() => {
      isLoaded.value = true
      goToToday()
    }, 400)
  }, 2200)
})
</script>

<style scoped>
* {
  scrollbar-width: none;
  -ms-overflow-style: none;
}
*::-webkit-scrollbar {
  display: none;
}

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

/* ==================== Main Page ==================== */
.engineer-schedule-page {
  min-height: 100vh;
  background: #f5f7fb;
  padding: 20px;
  overflow-x: hidden;
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

.header-actions {
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

.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

/* Filter Bar */
.filter-bar {
  background: white;
  border-radius: 16px;
  padding: 14px 20px;
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.filter-left {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.week-navigation {
  display: flex;
  align-items: center;
  gap: 12px;
}

.week-range {
  font-weight: 500;
  color: #1e293b;
  min-width: 200px;
  text-align: center;
}

/* Date Picker Row */
.date-picker-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 16px;
  flex-wrap: wrap;
}

/* Engineer Grid (保持不变) */
.engineer-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.engineer-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.engineer-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 16px;
}

.engineer-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  font-size: 20px;
  position: relative;
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

.engineer-basic {
  flex: 1;
}

.engineer-name {
  font-weight: 700;
  font-size: 16px;
  color: #1e293b;
}

.engineer-role {
  font-size: 12px;
  color: #64748b;
  margin-top: 2px;
}

.card-skills {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eef2f8;
}

.card-stats {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #475569;
}

.stat-item .stars {
  display: inline-flex;
  margin-left: 8px;
  gap: 2px;
}

.star {
  font-size: 12px;
  color: #cbd5e1;
}

.star.full { color: #fbbf24; }
.star.half { color: #fbbf24; position: relative; overflow: hidden; width: 8px; display: inline-block; }

.card-contact {
  background: #f8fafc;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 16px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #475569;
  margin-bottom: 6px;
}

.contact-item:last-child {
  margin-bottom: 0;
}

.card-actions {
  display: flex;
  gap: 10px;
}

/* ==================== Week Schedule Table ==================== */
.schedule-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.schedule-table-wrapper {
  overflow-x: auto;
}

.schedule-table {
  width: 100%;
  border-collapse: collapse;
}

.schedule-table th,
.schedule-table td {
  border: 1px solid #eef2f8;
  vertical-align: top;
}

.engineer-col {
  width: 200px;
  background: #f8fafc;
  padding: 12px;
}

.date-col {
  width: 140px;
  background: #f8fafc;
  padding: 12px;
  text-align: center;
}

.date-header {
  text-align: center;
}

.day-name {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
}

.day-date {
  font-size: 11px;
  color: #64748b;
  margin-top: 4px;
}

.engineer-cell {
  padding: 12px;
  background: white;
}

.engineer-info-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.cell-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
}

.cell-avatar.online { box-shadow: 0 0 0 2px #22c55e; }
.cell-avatar.busy { box-shadow: 0 0 0 2px #f97316; }
.cell-avatar.offline { box-shadow: 0 0 0 2px #94a3b8; }

.engineer-details {
  flex: 1;
}

.engineer-name-cell {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
}

.engineer-role-cell {
  font-size: 11px;
  color: #64748b;
  margin-top: 2px;
}

.schedule-cell {
  padding: 10px;
  cursor: pointer;
  transition: all 0.2s;
  min-height: 100px;
}

.schedule-cell.empty {
  background: #fafcff;
}

.schedule-cell.empty:hover {
  background: #f1f5f9;
}

.schedule-cell.occupied {
  background: #eef2ff;
}

.schedule-cell.leave {
  background: #fee2e2;
}

.schedule-cell.on-call {
  background: #fef3c7;
}

.schedule-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.shift-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 20px;
  text-align: center;
}

.shift-morning { background: #dbeafe; color: #2563eb; }
.shift-afternoon { background: #fed7aa; color: #c2410c; }
.shift-night { background: #e0e7ff; color: #4f46e5; }
.shift-oncall { background: #f3e8ff; color: #7e22ce; }

.shift-time {
  font-size: 11px;
  color: #475569;
  text-align: center;
}

.task-count {
  font-size: 11px;
  color: #059669;
  text-align: center;
  background: #d1fae5;
  padding: 2px 6px;
  border-radius: 12px;
  display: inline-block;
}

.status-badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 12px;
  text-align: center;
}

.status-badge.on-duty { background: #d1fae5; color: #059669; }
.status-badge.on-leave { background: #fee2e2; color: #dc2626; }
.status-badge.on-call { background: #fef3c7; color: #d97706; }

.empty-schedule {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 80px;
  color: #94a3b8;
  transition: all 0.2s;
}

.empty-schedule:hover {
  color: #3b82f6;
}

.add-icon {
  font-size: 20px;
  font-weight: 300;
}

.add-text {
  font-size: 10px;
  margin-top: 4px;
}

/* Month View */
.month-view {
  margin-top: 16px;
}

.month-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: #f8fafc;
  border-radius: 12px;
  overflow: hidden;
}

.month-day {
  padding: 12px;
  text-align: center;
  font-weight: 600;
  font-size: 13px;
  color: #1e293b;
  border-right: 1px solid #eef2f8;
}

.month-day:last-child {
  border-right: none;
}

.month-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: white;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #eef2f8;
}

.month-cell {
  min-height: 100px;
  padding: 8px;
  border-right: 1px solid #eef2f8;
  border-bottom: 1px solid #eef2f8;
  cursor: pointer;
  transition: all 0.2s;
}

.month-cell:hover {
  background: #f8fafc;
}

.month-cell.other-month {
  background: #fafcff;
  color: #94a3b8;
}

.month-cell.has-schedule {
  background: #eef2ff;
}

.month-day-number {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
}

.month-schedule-count {
  font-size: 11px;
  color: #3b82f6;
  background: white;
  padding: 2px 6px;
  border-radius: 12px;
  display: inline-block;
}

/* Responsive */
@media (max-width: 900px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .engineer-grid {
    grid-template-columns: 1fr;
  }

  .engineer-col {
    width: 150px;
  }

  .date-col {
    width: 110px;
  }
}

@media (max-width: 600px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .schedule-table {
    font-size: 12px;
  }

  .engineer-col {
    width: 120px;
  }

  .date-col {
    width: 90px;
  }
}
</style>