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
          <span class="loading-title">Cleaning Task Management</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Smart Housekeeping System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="cleaning-task-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Brush /></el-icon>
          Cleaning Task Management
        </h1>
        <div class="page-subtitle">Assign, track and manage cleaning tasks across all zones</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog">
          <el-icon><Plus /></el-icon> Create Task
        </el-button>
        <el-button @click="exportTasks">
          <el-icon><Download /></el-icon> Export
        </el-button>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><List /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalTasks }}</div>
          <div class="stat-label">Total Tasks</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.completedTasks }}</div>
          <div class="stat-label">Completed</div>
          <div class="stat-trend up">↑ {{ stats.completionRate }}% completion rate</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.inProgressTasks }}</div>
          <div class="stat-label">In Progress</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.overdueTasks }}</div>
          <div class="stat-label">Overdue</div>
          <div class="stat-trend down">↓ Requires attention</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Avg Completion Time</div>
        <div class="metric-value">{{ metrics.avgCompletionTime }}<span class="stat-unit">min</span></div>
        <div class="metric-trend positive">↑ {{ metrics.timeImprovement }}% faster than target</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Staff Utilization</div>
        <div class="metric-value">{{ metrics.staffUtilization }}<span class="stat-unit">%</span></div>
        <el-progress :percentage="metrics.staffUtilization" :stroke-width="8" />
      </div>
      <div class="metric-card">
        <div class="metric-title">Satisfaction Score</div>
        <div class="metric-value">{{ metrics.satisfactionScore }}<span class="stat-unit">/5</span></div>
        <div class="metric-trend positive">↑ {{ metrics.satisfactionGrowth }}% vs last month</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Supplies Used</div>
        <div class="metric-value">{{ metrics.suppliesUsed }}<span class="stat-unit">units</span></div>
        <div class="metric-sub">This week</div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            size="default"
            style="width: 260px"
        />
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 130px">
          <el-option label="Pending" value="pending" />
          <el-option label="In Progress" value="in_progress" />
          <el-option label="Completed" value="completed" />
          <el-option label="Overdue" value="overdue" />
          <el-option label="Cancelled" value="cancelled" />
        </el-select>
        <el-select v-model="priorityFilter" placeholder="Priority" clearable style="width: 120px">
          <el-option label="High" value="high" />
          <el-option label="Medium" value="medium" />
          <el-option label="Low" value="low" />
        </el-select>
        <el-select v-model="zoneFilter" placeholder="Zone" clearable style="width: 120px">
          <el-option v-for="z in zones" :key="z" :label="z" :value="z" />
        </el-select>
        <el-input v-model="searchKeyword" placeholder="Search task / staff" style="width: 200px" clearable>
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- View Toggle -->
    <div class="view-toggle">
      <el-radio-group v-model="viewMode" size="default">
        <el-radio-button value="kanban">
          <el-icon><Grid /></el-icon> Kanban
        </el-radio-button>
        <el-radio-button value="table">
          <el-icon><List /></el-icon> Table
        </el-radio-button>
      </el-radio-group>
    </div>

    <!-- Task Kanban Board (手动实现拖拽，不依赖vuedraggable) -->
    <div class="kanban-board" v-if="viewMode === 'kanban'">
      <div
          v-for="column in kanbanColumns"
          :key="column.status"
          class="kanban-column"
          @dragover.prevent
          @drop="onDrop($event, column.status)"
      >
        <div class="kanban-header">
          <span class="kanban-title">
            <span class="status-dot" :class="column.status"></span>
            {{ column.title }}
          </span>
          <span class="kanban-count">{{ column.tasks.length }}</span>
        </div>
        <div class="kanban-body">
          <div class="kanban-list">
            <div
                v-for="task in column.tasks"
                :key="task.id"
                class="task-card"
                draggable="true"
                @dragstart="onDragStart($event, task)"
                @click="viewTaskDetail(task)"
            >
              <div class="task-header">
                <span class="task-id">{{ task.id }}</span>
                <el-tag :type="getPriorityType(task.priority)" size="small">
                  {{ getPriorityLabel(task.priority) }}
                </el-tag>
              </div>
              <div class="task-title">{{ task.title }}</div>
              <div class="task-location">
                <el-icon><Location /></el-icon>
                {{ task.zone }} - {{ task.area }}
              </div>
              <div class="task-meta">
                <div class="task-assignee">
                  <el-avatar :size="24">
                    {{ task.assignee?.charAt(0) }}
                  </el-avatar>
                  <span>{{ task.assignee }}</span>
                </div>
                <div class="task-due" :class="{ overdue: task.status === 'overdue' }">
                  <el-icon><Timer /></el-icon>
                  {{ formatDueDate(task.dueDate) }}
                </div>
              </div>
              <div class="task-progress" v-if="task.status === 'in_progress'">
                <el-progress :percentage="task.progress" :stroke-width="4" :show-text="false" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Task Table View -->
    <div class="table-container" v-if="viewMode === 'table'">
      <div class="table-header">
        <span class="table-title">Task List</span>
      </div>

      <el-table :data="paginatedTasks" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="id" label="Task ID" width="110" />
        <el-table-column prop="title" label="Task Title" min-width="180" />
        <el-table-column prop="zone" label="Zone" width="100" />
        <el-table-column prop="area" label="Area" width="120" />
        <el-table-column prop="assignee" label="Assignee" width="120" />
        <el-table-column prop="dueDate" label="Due Date" width="110" />
        <el-table-column prop="priority" label="Priority" width="90">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">
              {{ getPriorityLabel(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewTaskDetail(row)">Details</el-button>
            <el-button
                link
                type="success"
                size="small"
                @click="updateTaskStatus(row, 'completed')"
                v-if="row.status !== 'completed' && row.status !== 'cancelled'"
            >
              Complete
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredTasks.length"
            layout="total, sizes, prev, pager, next"
            background
        />
      </div>
    </div>

    <!-- Create/Edit Task Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? 'Create New Task' : 'Edit Task'" width="600px">
      <el-form :model="taskForm" label-width="100px" ref="taskFormRef">
        <el-form-item label="Task Title" required>
          <el-input v-model="taskForm.title" placeholder="Enter task title" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input type="textarea" v-model="taskForm.description" :rows="3" placeholder="Enter task description" />
        </el-form-item>
        <el-form-item label="Zone" required>
          <el-select v-model="taskForm.zone" placeholder="Select zone" style="width: 100%">
            <el-option v-for="z in zones" :key="z" :label="z" :value="z" />
          </el-select>
        </el-form-item>
        <el-form-item label="Area">
          <el-input v-model="taskForm.area" placeholder="e.g., Main Lobby, Restroom A, Office Wing" />
        </el-form-item>
        <el-form-item label="Priority">
          <el-radio-group v-model="taskForm.priority">
            <el-radio value="high">High</el-radio>
            <el-radio value="medium">Medium</el-radio>
            <el-radio value="low">Low</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Assignee">
          <el-select v-model="taskForm.assignee" placeholder="Select staff" style="width: 100%">
            <el-option v-for="staff in staffList" :key="staff.id" :label="staff.name" :value="staff.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="Due Date">
          <el-date-picker v-model="taskForm.dueDate" type="datetime" placeholder="Select due date" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveTask">Save</el-button>
      </template>
    </el-dialog>

    <!-- Task Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Task ${selectedTask?.id}`" width="650px">
      <div v-if="selectedTask" class="task-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Task ID">{{ selectedTask.id }}</el-descriptions-item>
          <el-descriptions-item label="Priority">
            <el-tag :type="getPriorityType(selectedTask.priority)" size="small">
              {{ getPriorityLabel(selectedTask.priority) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Title" :span="2">{{ selectedTask.title }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedTask.description || 'No description' }}</el-descriptions-item>
          <el-descriptions-item label="Zone">{{ selectedTask.zone }}</el-descriptions-item>
          <el-descriptions-item label="Area">{{ selectedTask.area }}</el-descriptions-item>
          <el-descriptions-item label="Assignee">{{ selectedTask.assignee }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusType(selectedTask.status)" size="small">
              {{ getStatusLabel(selectedTask.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Created At">{{ selectedTask.createdAt }}</el-descriptions-item>
          <el-descriptions-item label="Due Date">{{ formatDueDate(selectedTask.dueDate) }}</el-descriptions-item>
          <el-descriptions-item label="Completed At">{{ selectedTask.completedAt || 'Not completed' }}</el-descriptions-item>
        </el-descriptions>
        <div class="task-actions" v-if="selectedTask.status !== 'completed' && selectedTask.status !== 'cancelled'">
          <el-button type="success" @click="updateTaskStatus(selectedTask, 'completed')">Mark Complete</el-button>
          <el-button type="warning" @click="updateTaskStatus(selectedTask, 'in_progress')">Start Progress</el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Brush, Plus, Download, Refresh, List, CircleCheck, Clock, Warning,
  Search, RefreshLeft, Location, Timer, Grid
} from '@element-plus/icons-vue'

// ==================== Types ====================
interface CleaningTask {
  id: string
  title: string
  description: string
  zone: string
  area: string
  priority: 'high' | 'medium' | 'low'
  status: 'pending' | 'in_progress' | 'completed' | 'overdue' | 'cancelled'
  assignee: string
  assigneeAvatar?: string
  dueDate: string
  createdAt: string
  completedAt: string | null
  progress: number
}

interface Staff {
  id: string
  name: string
  avatar?: string
  role: string
}

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading cleaning tasks...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading cleaning tasks...',
  'Fetching staff assignments...',
  'Loading zone data...',
  'Calculating metrics...',
  'Almost ready...'
]

// ==================== Mock Data ====================
const zones = ['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E', 'Zone F']

const staffList: Staff[] = [
  { id: 'STF001', name: 'John Smith', role: 'Team Lead' },
  { id: 'STF002', name: 'Sarah Johnson', role: 'Cleaner' },
  { id: 'STF003', name: 'Mike Wilson', role: 'Cleaner' },
  { id: 'STF004', name: 'Emma Davis', role: 'Cleaner' },
  { id: 'STF005', name: 'David Brown', role: 'Supervisor' },
  { id: 'STF006', name: 'Lisa Anderson', role: 'Cleaner' },
]

const generateTasks = (): CleaningTask[] => {
  const tasks: CleaningTask[] = []
  const taskTemplates = [
    { title: 'Restroom Cleaning', description: 'Deep clean all restrooms including fixtures, mirrors, and floors', areas: ['Restroom A', 'Restroom B', 'Restroom C'] },
    { title: 'Floor Mopping', description: 'Mop all hard floor surfaces in common areas', areas: ['Main Lobby', 'Hallway East', 'Hallway West'] },
    { title: 'Trash Collection', description: 'Collect and dispose of all waste', areas: ['All Zones'] },
    { title: 'Window Cleaning', description: 'Clean interior and exterior windows', areas: ['Main Entrance', 'Office Wing', 'Conference Area'] },
    { title: 'Carpet Vacuuming', description: 'Vacuum all carpeted areas', areas: ['Office Area', 'Meeting Rooms', 'Lounge'] },
    { title: 'Surface Disinfection', description: 'Disinfect high-touch surfaces', areas: ['Common Areas', 'Elevators', 'Handrails'] },
    { title: 'Supply Restocking', description: 'Restock soap, paper towels, and toilet paper', areas: ['All Restrooms'] },
    { title: 'Deep Cleaning', description: 'Detailed cleaning of assigned area', areas: ['Kitchen', 'Pantry', 'Break Room'] },
  ]

  const statuses: CleaningTask['status'][] = ['pending', 'in_progress', 'completed', 'overdue']
  const priorities: CleaningTask['priority'][] = ['high', 'medium', 'low']

  for (let i = 0; i < 48; i++) {
    const template = taskTemplates[i % taskTemplates.length]
    const area = template.areas[i % template.areas.length]
    const status = statuses[Math.floor(Math.random() * statuses.length)]
    const priority = priorities[Math.floor(Math.random() * priorities.length)]
    const assignee = staffList[Math.floor(Math.random() * staffList.length)]

    const dueDate = new Date()
    dueDate.setDate(dueDate.getDate() + Math.floor(Math.random() * 7) - 2)
    dueDate.setHours(Math.floor(Math.random() * 24), Math.floor(Math.random() * 60))

    const createdAt = new Date(dueDate)
    createdAt.setDate(createdAt.getDate() - Math.floor(Math.random() * 5))

    let completedAt = null
    let progress = 0
    if (status === 'completed') {
      completedAt = new Date(dueDate)
      completedAt.setHours(dueDate.getHours() - Math.floor(Math.random() * 12))
      progress = 100
    } else if (status === 'in_progress') {
      progress = Math.floor(Math.random() * 70) + 15
    }

    tasks.push({
      id: `TASK-${String(i + 1).padStart(5, '0')}`,
      title: template.title,
      description: template.description,
      zone: zones[Math.floor(Math.random() * zones.length)],
      area: area,
      priority: priority,
      status: status,
      assignee: assignee.name,
      assigneeAvatar: assignee.avatar,
      dueDate: dueDate.toISOString().slice(0, 16).replace('T', ' '),
      createdAt: createdAt.toISOString().slice(0, 16).replace('T', ' '),
      completedAt: completedAt ? completedAt.toISOString().slice(0, 16).replace('T', ' ') : null,
      progress: progress
    })
  }

  return tasks.sort((a, b) => b.createdAt.localeCompare(a.createdAt))
}

const tasks = ref<CleaningTask[]>(generateTasks())

// ==================== State ====================
const viewMode = ref<'kanban' | 'table'>('kanban')
const dateRange = ref<Date[] | null>(null)
const statusFilter = ref('')
const priorityFilter = ref('')
const zoneFilter = ref('')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const selectedTask = ref<CleaningTask | null>(null)
const taskFormRef = ref()
const draggingTask = ref<CleaningTask | null>(null)

const taskForm = ref({
  title: '',
  description: '',
  zone: '',
  area: '',
  priority: 'medium' as 'high' | 'medium' | 'low',
  assignee: '',
  dueDate: null as Date | null
})

// ==================== Kanban Columns ====================
const kanbanColumns = ref([
  { status: 'pending', title: 'Pending', tasks: [] as CleaningTask[] },
  { status: 'in_progress', title: 'In Progress', tasks: [] as CleaningTask[] },
  { status: 'overdue', title: 'Overdue', tasks: [] as CleaningTask[] },
  { status: 'completed', title: 'Completed', tasks: [] as CleaningTask[] }
])

const updateKanbanColumns = () => {
  kanbanColumns.value.forEach(column => {
    column.tasks = tasks.value.filter(t => t.status === column.status)
  })
}

// Drag and drop handlers
const onDragStart = (event: DragEvent, task: CleaningTask) => {
  draggingTask.value = task
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', task.id)
  }
}

const onDrop = (event: DragEvent, newStatus: string) => {
  event.preventDefault()
  if (draggingTask.value) {
    const task = draggingTask.value
    if (task.status !== newStatus) {
      updateTaskStatus(task, newStatus)
    }
    draggingTask.value = null
  }
}

// ==================== Computed ====================
const stats = computed(() => {
  const totalTasks = tasks.value.length
  const completedTasks = tasks.value.filter(t => t.status === 'completed').length
  const inProgressTasks = tasks.value.filter(t => t.status === 'in_progress').length
  const overdueTasks = tasks.value.filter(t => t.status === 'overdue').length
  const completionRate = Math.round((completedTasks / totalTasks) * 100)

  return {
    totalTasks,
    completedTasks,
    inProgressTasks,
    overdueTasks,
    completionRate
  }
})

const metrics = computed(() => {
  const completedTasks = tasks.value.filter(t => t.status === 'completed')
  const avgCompletionTime = completedTasks.length > 0
      ? Math.round(completedTasks.reduce((acc, t) => {
        const created = new Date(t.createdAt)
        const completed = new Date(t.completedAt!)
        return acc + (completed.getTime() - created.getTime()) / (1000 * 60)
      }, 0) / completedTasks.length)
      : 45

  const staffUtilization = Math.min(100, Math.round((tasks.value.filter(t => t.status === 'in_progress').length / staffList.length) * 20))
  const satisfactionScore = (4.2 + Math.random() * 0.6).toFixed(1)

  return {
    avgCompletionTime,
    timeImprovement: 12,
    staffUtilization,
    satisfactionScore: parseFloat(satisfactionScore),
    satisfactionGrowth: 5,
    suppliesUsed: 284
  }
})

const filteredTasks = computed(() => {
  let filtered = [...tasks.value]

  if (statusFilter.value) {
    filtered = filtered.filter(t => t.status === statusFilter.value)
  }
  if (priorityFilter.value) {
    filtered = filtered.filter(t => t.priority === priorityFilter.value)
  }
  if (zoneFilter.value) {
    filtered = filtered.filter(t => t.zone === zoneFilter.value)
  }
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(t =>
        t.id.toLowerCase().includes(keyword) ||
        t.title.toLowerCase().includes(keyword) ||
        t.assignee.toLowerCase().includes(keyword)
    )
  }
  if (dateRange.value && dateRange.value.length === 2) {
    const [start, end] = dateRange.value
    filtered = filtered.filter(t => {
      const dueDate = new Date(t.dueDate)
      return dueDate >= start && dueDate <= end
    })
  }

  return filtered
})

const paginatedTasks = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredTasks.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getPriorityType = (priority: string) => {
  const map: Record<string, string> = { high: 'danger', medium: 'warning', low: 'info' }
  return map[priority] || 'info'
}

const getPriorityLabel = (priority: string) => {
  const map: Record<string, string> = { high: 'High', medium: 'Medium', low: 'Low' }
  return map[priority] || priority
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'info', in_progress: 'primary', completed: 'success',
    overdue: 'danger', cancelled: 'info'
  }
  return map[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    pending: 'Pending', in_progress: 'In Progress', completed: 'Completed',
    overdue: 'Overdue', cancelled: 'Cancelled'
  }
  return map[status] || status
}

const formatDueDate = (dueDate: string) => {
  const date = new Date(dueDate)
  const now = new Date()
  const diff = date.getTime() - now.getTime()
  const hours = Math.floor(diff / (1000 * 60 * 60))

  if (hours < 0) return `Overdue by ${Math.abs(hours)}h`
  if (hours < 24) return `${hours}h remaining`
  return `${Math.floor(hours / 24)}d remaining`
}

const resetFilters = () => {
  statusFilter.value = ''
  priorityFilter.value = ''
  zoneFilter.value = ''
  searchKeyword.value = ''
  dateRange.value = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const viewTaskDetail = (task: CleaningTask) => {
  selectedTask.value = task
  detailDialogVisible.value = true
}

const updateTaskStatus = (task: CleaningTask, newStatus: string) => {
  const index = tasks.value.findIndex(t => t.id === task.id)
  if (index !== -1) {
    tasks.value[index].status = newStatus as CleaningTask['status']
    if (newStatus === 'completed') {
      tasks.value[index].completedAt = new Date().toISOString().slice(0, 16).replace('T', ' ')
      tasks.value[index].progress = 100
    }
    if (newStatus === 'in_progress' && tasks.value[index].progress === 0) {
      tasks.value[index].progress = 10
    }
    updateKanbanColumns()
    ElMessage.success(`Task ${task.id} marked as ${getStatusLabel(newStatus)}`)
  }
}

const showCreateDialog = () => {
  dialogMode.value = 'create'
  taskForm.value = {
    title: '',
    description: '',
    zone: '',
    area: '',
    priority: 'medium',
    assignee: '',
    dueDate: null
  }
  dialogVisible.value = true
}

const saveTask = () => {
  if (!taskForm.value.title || !taskForm.value.zone || !taskForm.value.assignee) {
    ElMessage.warning('Please fill in required fields')
    return
  }

  if (dialogMode.value === 'create') {
    const newTask: CleaningTask = {
      id: `TASK-${String(tasks.value.length + 1).padStart(5, '0')}`,
      title: taskForm.value.title,
      description: taskForm.value.description || 'No description',
      zone: taskForm.value.zone,
      area: taskForm.value.area || 'General',
      priority: taskForm.value.priority,
      status: 'pending',
      assignee: taskForm.value.assignee,
      dueDate: taskForm.value.dueDate?.toISOString().slice(0, 16).replace('T', ' ') || new Date().toISOString().slice(0, 16).replace('T', ' '),
      createdAt: new Date().toISOString().slice(0, 16).replace('T', ' '),
      completedAt: null,
      progress: 0
    }
    tasks.value.unshift(newTask)
    ElMessage.success('Task created successfully')
  }

  dialogVisible.value = false
  updateKanbanColumns()
}

const exportTasks = () => {
  ElMessage.success('Exporting tasks...')
  setTimeout(() => {
    ElMessage.success('Tasks exported successfully')
  }, 1000)
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  tasks.value = generateTasks()
  updateKanbanColumns()
  refreshing.value = false
  tableLoading.value = false
  ElMessage.success('Data refreshed')
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
      updateKanbanColumns()
    }, 500)
  }, 2200)
}

onMounted(() => {
  startLoading()
})

onUnmounted(() => {
  // Cleanup if needed
})
</script>

<style scoped>
.cleaning-task-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 24px;
}

* {
  scrollbar-width: thin;
}
*::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
*::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}
*::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

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
.spinner-ring:nth-child(4) { border-left-color: #ec489a; animation-delay: 0.6s; width: 20%; height: 20%; top: 40%; left: 40%; }

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-bottom: 24px;
  font-size: 24px;
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

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
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
  gap: 12px;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
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
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
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
.stat-icon.red { background: #fee2e2; color: #ef4444; }

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
}

.stat-unit {
  font-size: 14px;
  font-weight: normal;
  color: #64748b;
  margin-left: 4px;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

.stat-trend {
  font-size: 11px;
  margin-top: 4px;
}

.stat-trend.up { color: #22c55e; }
.stat-trend.down { color: #ef4444; }

/* Metrics Row */
.metrics-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.metric-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.metric-title {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.metric-trend {
  font-size: 11px;
  margin-top: 8px;
}

.metric-trend.positive { color: #22c55e; }
.metric-trend.negative { color: #ef4444; }

.metric-sub {
  font-size: 11px;
  color: #64748b;
  margin-top: 4px;
}

/* Filter Bar */
.filter-bar {
  background: white;
  border-radius: 16px;
  padding: 14px 20px;
  margin-bottom: 20px;
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

.filter-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* View Toggle */
.view-toggle {
  margin-bottom: 20px;
  display: flex;
  justify-content: flex-end;
}

/* Kanban Board */
.kanban-board {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.kanban-column {
  background: #f8fafc;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.kanban-header {
  background: white;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e2e8f0;
}

.kanban-title {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.status-dot.pending { background: #94a3b8; }
.status-dot.in_progress { background: #3b82f6; }
.status-dot.overdue { background: #ef4444; }
.status-dot.completed { background: #22c55e; }

.kanban-count {
  background: #e2e8f0;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  color: #475569;
}

.kanban-body {
  padding: 12px;
  min-height: 500px;
  max-height: 600px;
  overflow-y: auto;
}

.kanban-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-card {
  background: white;
  border-radius: 12px;
  padding: 12px;
  cursor: grab;
  transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
}

.task-card:active {
  cursor: grabbing;
}

.task-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #cbd5e1;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.task-id {
  font-size: 11px;
  font-weight: 500;
  color: #64748b;
  font-family: monospace;
}

.task-title {
  font-weight: 600;
  font-size: 13px;
  color: #1e293b;
  margin-bottom: 8px;
  line-height: 1.4;
}

.task-location {
  font-size: 11px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 8px;
}

.task-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.task-assignee {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #475569;
}

.task-due {
  font-size: 10px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 4px;
}

.task-due.overdue {
  color: #ef4444;
  font-weight: 500;
}

.task-progress {
  margin-top: 8px;
}

/* Table Container */
.table-container {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

/* Task Detail */
.task-detail {
  padding: 8px;
}

.task-actions {
  margin-top: 20px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* Responsive */
@media (max-width: 1200px) {
  .kanban-board {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1000px) {
  .stats-grid, .metrics-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid, .metrics-row {
    grid-template-columns: 1fr;
  }
  .kanban-board {
    grid-template-columns: 1fr;
  }
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .filter-left {
    flex-direction: column;
    width: 100%;
  }
  .filter-left .el-input,
  .filter-left .el-select,
  .filter-left .el-date-editor {
    width: 100% !important;
  }
}

/* Element Plus Overrides */
:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
}
:deep(.el-table th.el-table__cell) {
  background-color: #f8fafc !important;
  color: #334155;
}
:deep(.el-button--primary) {
  background: #3b82f6;
  border-color: #3b82f6;
}
:deep(.el-button--primary:hover) {
  background: #2563eb;
}
:deep(.el-pagination.is-background .el-pager li.is-active) {
  background-color: #3b82f6;
}
:deep(.el-dialog__body) {
  padding: 20px;
}
:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}
</style>