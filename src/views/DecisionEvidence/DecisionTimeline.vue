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
        <div class="loading-tip">Decision Timeline</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="decision-timeline-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Decision & Evidence</el-breadcrumb-item>
            <el-breadcrumb-item>Decision Timeline</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Decision Timeline</h1>
        <p class="description">Track and visualize the complete lifecycle of all decisions from creation to closure</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
        <el-button type="primary" @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6" v-for="stat in statsCards" :key="stat.title">
        <el-card class="stat-card" shadow="hover" @click="handleCardClick(stat)">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">{{ stat.title }}</div>
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
                <el-icon><component :is="stat.trend > 0 ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
                {{ Math.abs(stat.trend) }}%
                <span class="trend-label">vs last month</span>
              </div>
            </div>
            <div class="stat-icon" :style="{ background: stat.bgColor }">
              <el-icon :size="28" color="white">
                <component :is="stat.icon" />
              </el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Timeline Overview Chart -->
    <el-card class="timeline-chart-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Decision Lifecycle Overview</span>
          <div class="chart-controls">
            <el-button size="small" @click="chartView = 'timeline'">Timeline</el-button>
            <el-button size="small" type="primary" @click="chartView = 'gantt'">Gantt</el-button>
          </div>
        </div>
      </template>

      <!-- Timeline View -->
      <div v-if="chartView === 'timeline'" class="custom-timeline-container">
        <div v-for="decision in chartDecisions" :key="decision.id" class="custom-timeline-item">
          <div class="timeline-item-label">{{ decision.name }}</div>
          <div class="timeline-item-bar-container">
            <div
                class="timeline-item-bar"
                :style="{
                left: getBarLeftPosition(decision.startDate),
                width: getBarWidth(decision.startDate, decision.endDate),
                backgroundColor: getBarColor(decision.status)
              }"
                @click="showDecisionDetail(decision)"
            >
              <span class="bar-label">{{ decision.status }}</span>
            </div>
            <div class="timeline-marker" :style="{ left: getCurrentDatePosition() }"></div>
          </div>
        </div>
        <div class="timeline-scale">
          <div v-for="month in months" :key="month.value" class="scale-mark" :style="{ left: month.position + '%' }">
            {{ month.label }}
          </div>
        </div>
      </div>

      <!-- Gantt Chart View -->
      <div v-else ref="ganttChartRef" class="gantt-chart-container"></div>
    </el-card>

    <!-- Filters -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-container">
        <div class="filter-row">
          <el-input
              v-model="filters.keyword"
              placeholder="Search by decision title"
              prefix-icon="Search"
              clearable
              style="width: 220px"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
          />
          <el-select v-model="filters.decisionType" placeholder="Decision Type" clearable style="width: 150px">
            <el-option label="Fault Decision" value="Fault Decision" />
            <el-option label="Maintenance Decision" value="Maintenance Decision" />
            <el-option label="ESG Decision" value="ESG Decision" />
            <el-option label="Energy Decision" value="Energy Decision" />
            <el-option label="AI Recommendation" value="AI Recommendation" />
          </el-select>
          <el-select v-model="filters.status" placeholder="Status" clearable style="width: 130px">
            <el-option label="Draft" value="Draft" />
            <el-option label="In Review" value="In Review" />
            <el-option label="Approved" value="Approved" />
            <el-option label="Rejected" value="Rejected" />
            <el-option label="Implemented" value="Implemented" />
            <el-option label="Closed" value="Closed" />
          </el-select>
          <el-select v-model="filters.priority" placeholder="Priority" clearable style="width: 120px">
            <el-option label="Critical" value="Critical" />
            <el-option label="High" value="High" />
            <el-option label="Medium" value="Medium" />
            <el-option label="Low" value="Low" />
          </el-select>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="handleResetFilters">Reset</el-button>
        </div>
      </div>
    </el-card>

    <!-- Timeline View -->
    <el-card class="timeline-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Decision Timeline History</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchTimelineData" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <div class="timeline-container">
        <el-timeline>
          <el-timeline-item
              v-for="item in paginatedTimeline"
              :key="item.id"
              :timestamp="item.timestamp"
              :type="getTimelineType(item.eventType)"
              placement="top"
              size="large"
          >
            <el-card shadow="hover" class="timeline-card-item">
              <div class="timeline-item-header">
                <div class="timeline-item-title">
                  <span class="decision-title">{{ item.decisionTitle }}</span>
                  <el-tag :type="getDecisionTypeTag(item.decisionType)" size="small">{{ item.decisionType }}</el-tag>
                  <el-tag :type="getStatusTag(item.status)" size="small">{{ item.status }}</el-tag>
                </div>
                <div class="timeline-item-actions">
                  <el-button link type="primary" size="small" @click="viewDecision(item)">View Details</el-button>
                </div>
              </div>
              <div class="timeline-item-content">
                <div class="timeline-item-event">
                  <el-icon><component :is="getEventIcon(item.eventType)" /></el-icon>
                  <span class="event-description">{{ item.eventDescription }}</span>
                </div>
                <div class="timeline-item-details" v-if="item.details">
                  <el-descriptions :column="2" size="small" border>
                    <el-descriptions-item label="Initiator">{{ item.initiator }}</el-descriptions-item>
                    <el-descriptions-item label="Department">{{ item.department }}</el-descriptions-item>
                    <el-descriptions-item label="Approver" v-if="item.approver">{{ item.approver }}</el-descriptions-item>
                    <el-descriptions-item label="Time Taken" v-if="item.timeTaken">{{ item.timeTaken }}</el-descriptions-item>
                    <el-descriptions-item label="Comments" :span="2" v-if="item.comments">{{ item.comments }}</el-descriptions-item>
                  </el-descriptions>
                </div>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredTimeline.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Decision Detail Dialog -->
    <el-dialog v-model="dialogVisible" title="Decision Details" width="700px" destroy-on-close>
      <el-descriptions :column="2" border v-if="selectedDecision">
        <el-descriptions-item label="Decision ID">{{ selectedDecision.decisionId }}</el-descriptions-item>
        <el-descriptions-item label="Title">{{ selectedDecision.decisionTitle }}</el-descriptions-item>
        <el-descriptions-item label="Type">
          <el-tag :type="getDecisionTypeTag(selectedDecision.decisionType)" size="small">{{ selectedDecision.decisionType }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusTag(selectedDecision.status)" size="small">{{ selectedDecision.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Priority">
          <el-tag :type="getPriorityTag(selectedDecision.priority)" size="small">{{ selectedDecision.priority }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Initiator">{{ selectedDecision.initiator }}</el-descriptions-item>
        <el-descriptions-item label="Department">{{ selectedDecision.department }}</el-descriptions-item>
        <el-descriptions-item label="Event Time">{{ selectedDecision.timestamp }}</el-descriptions-item>
        <el-descriptions-item label="Event Type">
          <el-tag :type="getTimelineType(selectedDecision.eventType)" size="small">{{ selectedDecision.eventType }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedDecision.eventDescription }}</el-descriptions-item>
        <el-descriptions-item label="Comments" :span="2" v-if="selectedDecision.comments">{{ selectedDecision.comments }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="dialogVisible = false">Close</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  Edit, CircleCheck, CircleClose, User
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading decision timeline...',
  'Building chronology...',
  'Almost ready...'
]

// ==================== Interfaces ====================
interface TimelineEvent {
  id: number
  decisionId: number
  decisionTitle: string
  decisionType: string
  status: string
  priority: string
  eventType: string
  eventDescription: string
  timestamp: string
  initiator: string
  department: string
  approver?: string
  timeTaken?: string
  comments?: string
  details?: boolean
}

interface ChartDecision {
  id: number
  name: string
  startDate: Date
  endDate: Date
  status: string
  type: string
}

interface StatCard {
  title: string
  value: string | number
  trend: number
  icon: string
  bgColor: string
  key: string
}

// ==================== Chart References ====================
const ganttChartRef = ref<HTMLElement>()
let ganttChart: echarts.ECharts | null = null

const chartView = ref<'timeline' | 'gantt'>('timeline')
const dateRange = ref<[Date, Date]>([new Date(2024, 0, 1), new Date(2024, 1, 28)])

// ==================== Mock Data ====================
const statsCards = ref<StatCard[]>([
  { title: 'Total Decisions', value: 284, trend: 12, icon: 'Document', bgColor: '#409eff', key: 'total' },
  { title: 'Avg Decision Time', value: '4.2 days', trend: -8, icon: 'Clock', bgColor: '#e6a23c', key: 'avgTime' },
  { title: 'On-time Rate', value: '87%', trend: 5, icon: 'Checked', bgColor: '#67c23a', key: 'ontime' },
  { title: 'Active Decisions', value: 42, trend: -3, icon: 'TrendCharts', bgColor: '#f56c6c', key: 'active' }
])

const timelineEvents = ref<TimelineEvent[]>([
  {
    id: 1,
    decisionId: 101,
    decisionTitle: 'Chiller Overhaul Decision',
    decisionType: 'Maintenance Decision',
    status: 'Implemented',
    priority: 'High',
    eventType: 'Created',
    eventDescription: 'Decision created by John Smith for chiller overhaul',
    timestamp: '2024-01-05 09:30:00',
    initiator: 'John Smith',
    department: 'Facilities',
    details: true
  },
  {
    id: 2,
    decisionId: 101,
    decisionTitle: 'Chiller Overhaul Decision',
    decisionType: 'Maintenance Decision',
    status: 'In Review',
    priority: 'High',
    eventType: 'Submitted',
    eventDescription: 'Decision submitted for technical review',
    timestamp: '2024-01-05 10:15:00',
    initiator: 'John Smith',
    department: 'Facilities',
    approver: 'Technical Review Team',
    details: true,
    comments: 'Awaiting technical assessment'
  },
  {
    id: 3,
    decisionId: 101,
    decisionTitle: 'Chiller Overhaul Decision',
    decisionType: 'Maintenance Decision',
    status: 'Approved',
    priority: 'High',
    eventType: 'Approved',
    eventDescription: 'Technical review approved by David Wang',
    timestamp: '2024-01-06 14:20:00',
    initiator: 'David Wang',
    department: 'Engineering',
    approver: 'David Wang',
    timeTaken: '1 day 4 hours',
    details: true,
    comments: 'Approved with recommended modifications'
  },
  {
    id: 4,
    decisionId: 101,
    decisionTitle: 'Chiller Overhaul Decision',
    decisionType: 'Maintenance Decision',
    status: 'Implemented',
    priority: 'High',
    eventType: 'Implemented',
    eventDescription: 'Decision implemented - chiller overhaul completed',
    timestamp: '2024-01-12 16:45:00',
    initiator: 'Mike Johnson',
    department: 'Maintenance',
    approver: 'John Smith',
    timeTaken: '6 days',
    details: true,
    comments: 'Overhaul completed successfully, efficiency improved by 15%'
  },
  {
    id: 5,
    decisionId: 102,
    decisionTitle: 'LED Lighting Retrofit',
    decisionType: 'Energy Decision',
    status: 'Approved',
    priority: 'Medium',
    eventType: 'Created',
    eventDescription: 'Decision created by Lisa Zhang for lighting upgrade',
    timestamp: '2024-01-08 11:00:00',
    initiator: 'Lisa Zhang',
    department: 'Energy',
    details: true
  },
  {
    id: 6,
    decisionId: 102,
    decisionTitle: 'LED Lighting Retrofit',
    decisionType: 'Energy Decision',
    status: 'In Review',
    priority: 'Medium',
    eventType: 'Review',
    eventDescription: 'Energy team review initiated',
    timestamp: '2024-01-08 13:30:00',
    initiator: 'System',
    department: 'Energy',
    approver: 'Energy Team',
    details: true
  },
  {
    id: 7,
    decisionId: 102,
    decisionTitle: 'LED Lighting Retrofit',
    decisionType: 'Energy Decision',
    status: 'Approved',
    priority: 'Medium',
    eventType: 'Approved',
    eventDescription: 'Decision approved by Sarah Chen',
    timestamp: '2024-01-10 09:00:00',
    initiator: 'Sarah Chen',
    department: 'Operations',
    approver: 'Sarah Chen',
    timeTaken: '2 days',
    details: true,
    comments: 'Good ROI, proceed with implementation'
  },
  {
    id: 8,
    decisionId: 103,
    decisionTitle: 'UPS Battery Replacement',
    decisionType: 'Fault Decision',
    status: 'Approved',
    priority: 'Critical',
    eventType: 'Created',
    eventDescription: 'Emergency decision for UPS battery failure',
    timestamp: '2024-01-10 08:15:00',
    initiator: 'Tom Harris',
    department: 'IT',
    details: true
  },
  {
    id: 9,
    decisionId: 103,
    decisionTitle: 'UPS Battery Replacement',
    decisionType: 'Fault Decision',
    status: 'Approved',
    priority: 'Critical',
    eventType: 'Escalated',
    eventDescription: 'Escalated to Operations Director due to criticality',
    timestamp: '2024-01-10 09:45:00',
    initiator: 'System',
    department: 'IT',
    approver: 'Operations Director',
    details: true,
    comments: 'Urgent attention required'
  },
  {
    id: 10,
    decisionId: 103,
    decisionTitle: 'UPS Battery Replacement',
    decisionType: 'Fault Decision',
    status: 'Approved',
    priority: 'Critical',
    eventType: 'Approved',
    eventDescription: 'Emergency approval granted by Sarah Chen',
    timestamp: '2024-01-10 11:30:00',
    initiator: 'Sarah Chen',
    department: 'Operations',
    approver: 'Sarah Chen',
    timeTaken: '3 hours 15 minutes',
    details: true,
    comments: 'Approved for immediate replacement'
  },
  {
    id: 11,
    decisionId: 104,
    decisionTitle: 'Solar Panel Installation',
    decisionType: 'ESG Decision',
    status: 'In Review',
    priority: 'High',
    eventType: 'Created',
    eventDescription: 'Proposal for rooftop solar installation',
    timestamp: '2024-01-12 14:00:00',
    initiator: 'Emily Zhao',
    department: 'ESG',
    details: true
  },
  {
    id: 12,
    decisionId: 105,
    decisionTitle: 'HVAC Optimization Algorithm',
    decisionType: 'AI Recommendation',
    status: 'Rejected',
    priority: 'Medium',
    eventType: 'Created',
    eventDescription: 'AI-generated recommendation for HVAC optimization',
    timestamp: '2024-01-09 08:00:00',
    initiator: 'AI System',
    department: 'Intelligence',
    details: true
  },
  {
    id: 13,
    decisionId: 105,
    decisionTitle: 'HVAC Optimization Algorithm',
    decisionType: 'AI Recommendation',
    status: 'Rejected',
    priority: 'Medium',
    eventType: 'Rejected',
    eventDescription: 'Recommendation rejected due to budget constraints',
    timestamp: '2024-01-11 15:20:00',
    initiator: 'John Smith',
    department: 'Facilities',
    approver: 'John Smith',
    timeTaken: '2 days',
    details: true,
    comments: 'Deferred to next fiscal year'
  }
])

// ==================== Reactive Variables ====================
const tableLoading = ref(false)
const dialogVisible = ref(false)
const selectedDecision = ref<TimelineEvent | null>(null)
const currentPage = ref(1)
const pageSize = ref(10)
const chartDecisions = ref<ChartDecision[]>([])

const filters = reactive({
  keyword: '',
  decisionType: '',
  status: '',
  priority: ''
})

// Months for timeline scale
const months = [
  { label: 'Jan 1', value: '2024-01-01', position: 0 },
  { label: 'Jan 15', value: '2024-01-15', position: 12.5 },
  { label: 'Feb 1', value: '2024-02-01', position: 25 },
  { label: 'Feb 15', value: '2024-02-15', position: 37.5 },
  { label: 'Mar 1', value: '2024-03-01', position: 50 },
  { label: 'Mar 15', value: '2024-03-15', position: 62.5 },
  { label: 'Apr 1', value: '2024-04-01', position: 75 },
  { label: 'Apr 15', value: '2024-04-15', position: 87.5 },
  { label: 'May 1', value: '2024-05-01', position: 100 }
]

// ==================== Computed ====================
const filteredTimeline = computed(() => {
  let filtered = [...timelineEvents.value]

  if (filters.keyword) {
    filtered = filtered.filter(t =>
        t.decisionTitle.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        t.eventDescription.toLowerCase().includes(filters.keyword.toLowerCase())
    )
  }

  if (filters.decisionType) {
    filtered = filtered.filter(t => t.decisionType === filters.decisionType)
  }

  if (filters.status) {
    filtered = filtered.filter(t => t.status === filters.status)
  }

  if (filters.priority) {
    filtered = filtered.filter(t => t.priority === filters.priority)
  }

  return filtered.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
})

const paginatedTimeline = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredTimeline.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getPriorityTag = (priority: string): string => {
  const map: Record<string, string> = {
    'Critical': 'danger',
    'High': 'warning',
    'Medium': 'info',
    'Low': 'success'
  }
  return map[priority] || 'info'
}

const getDecisionTypeTag = (type: string): string => {
  const map: Record<string, string> = {
    'Fault Decision': 'danger',
    'Maintenance Decision': 'warning',
    'ESG Decision': 'success',
    'Energy Decision': 'primary',
    'AI Recommendation': 'info'
  }
  return map[type] || 'info'
}

const getStatusTag = (status: string): string => {
  const map: Record<string, string> = {
    'Draft': 'info',
    'In Review': 'warning',
    'Approved': 'success',
    'Rejected': 'danger',
    'Implemented': 'success',
    'Closed': 'info'
  }
  return map[status] || 'info'
}

const getTimelineType = (eventType: string): string => {
  const map: Record<string, string> = {
    'Created': 'primary',
    'Submitted': 'primary',
    'Review': 'warning',
    'Approved': 'success',
    'Rejected': 'danger',
    'Implemented': 'success',
    'Escalated': 'danger',
    'Updated': 'info'
  }
  return map[eventType] || 'info'
}

const getEventIcon = (eventType: string) => {
  const map: Record<string, any> = {
    'Created': Document,
    'Submitted': Edit,
    'Review': User,
    'Approved': CircleCheck,
    'Rejected': CircleClose,
    'Implemented': Checked,
    'Escalated': TrendCharts,
    'Updated': Edit
  }
  return map[eventType] || Document
}

const getBarColor = (status: string): string => {
  const map: Record<string, string> = {
    'Implemented': '#67c23a',
    'Approved': '#67c23a',
    'In Review': '#e6a23c',
    'Rejected': '#f56c6c',
    'Draft': '#909399',
    'Closed': '#409eff'
  }
  return map[status] || '#409eff'
}

// Calculate position percentage based on date (Jan 1, 2024 to May 1, 2024)
const getPositionPercentage = (date: Date): number => {
  const start = new Date(2024, 0, 1).getTime()
  const end = new Date(2024, 4, 1).getTime()
  const current = date.getTime()
  return ((current - start) / (end - start)) * 100
}

const getBarLeftPosition = (startDate: Date): string => {
  return `${Math.max(0, getPositionPercentage(startDate))}%`
}

const getBarWidth = (startDate: Date, endDate: Date): string => {
  const startPos = getPositionPercentage(startDate)
  const endPos = Math.min(100, getPositionPercentage(endDate))
  return `${Math.max(2, endPos - startPos)}%`
}

const getCurrentDatePosition = (): string => {
  const today = new Date()
  if (today < new Date(2024, 0, 1)) return '0%'
  if (today > new Date(2024, 4, 1)) return '100%'
  return `${getPositionPercentage(today)}%`
}

const showDecisionDetail = (decision: ChartDecision) => {
  // Find a sample event for this decision
  const event = timelineEvents.value.find(e => e.decisionId === decision.id)
  if (event) {
    selectedDecision.value = event
    dialogVisible.value = true
  }
}

// ==================== Chart Initialization ====================
const initChartDecisions = () => {
  const decisionMap = new Map<number, { title: string; type: string; startDate: Date; endDate: Date; status: string }>()

  timelineEvents.value.forEach(event => {
    if (!decisionMap.has(event.decisionId)) {
      decisionMap.set(event.decisionId, {
        title: event.decisionTitle,
        type: event.decisionType,
        startDate: new Date(event.timestamp),
        endDate: new Date(event.timestamp),
        status: event.status
      })
    }

    const decision = decisionMap.get(event.decisionId)!
    const eventDate = new Date(event.timestamp)

    if (eventDate < decision.startDate) {
      decision.startDate = eventDate
    }

    if (eventDate > decision.endDate) {
      decision.endDate = eventDate
    }

    // Update status to final status
    if (event.status === 'Implemented' || event.status === 'Closed' || event.status === 'Rejected') {
      decision.status = event.status
    }
  })

  chartDecisions.value = Array.from(decisionMap.entries()).map(([id, data]) => ({
    id,
    name: data.title.length > 30 ? data.title.substring(0, 30) + '...' : data.title,
    startDate: data.startDate,
    endDate: data.endDate,
    status: data.status,
    type: data.type
  })).sort((a, b) => a.startDate.getTime() - b.startDate.getTime())
}

const initGanttChart = () => {
  if (!ganttChartRef.value) return
  if (ganttChart) ganttChart.dispose()

  ganttChart = echarts.init(ganttChartRef.value)

  const ganttData = chartDecisions.value.map(d => ({
    name: d.name,
    start: d.startDate.getTime(),
    end: d.endDate.getTime(),
    status: d.status,
    type: d.type
  }))

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        if (!params || params.length === 0) return ''
        const data = params[0]
        const item = ganttData[data.dataIndex]
        const startDate = new Date(item.start).toLocaleDateString()
        const endDate = new Date(item.end).toLocaleDateString()
        const days = Math.ceil((item.end - item.start) / (1000 * 60 * 60 * 24))
        return `<strong>${item.name}</strong><br/>
                Type: ${item.type}<br/>
                Status: ${item.status}<br/>
                Start: ${startDate}<br/>
                End: ${endDate}<br/>
                Duration: ${days} days`
      }
    },
    xAxis: {
      type: 'time',
      name: 'Date',
      axisLabel: {
        formatter: (value: number) => {
          return new Date(value).toLocaleDateString()
        }
      }
    },
    yAxis: {
      type: 'category',
      data: ganttData.map((_, i) => `Decision ${i + 1}`),
      axisLabel: {
        formatter: (value: string, index: number) => {
          return ganttData[index]?.name || value
        },
        width: 120,
        overflow: 'break'
      }
    },
    grid: {
      left: '22%',
      right: '5%',
      top: '10%',
      bottom: '8%'
    },
    series: [{
      type: 'bar',
      name: 'Decision Lifecycle',
      data: ganttData.map(d => ({
        value: [d.start, d.end],
        itemStyle: {
          color: getBarColor(d.status)
        }
      })),
      barCategoryGap: '30%',
      barGap: '30%',
      encode: {
        x: [0, 1],
        y: 0
      }
    }]
  }

  ganttChart.setOption(option)

  const handleResize = () => {
    ganttChart?.resize()
  }
  window.addEventListener('resize', handleResize)
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: StatCard) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleResetFilters = () => {
  filters.keyword = ''
  filters.decisionType = ''
  filters.status = ''
  filters.priority = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleRefresh = () => {
  initChartDecisions()
  initGanttChart()
  fetchTimelineData()
  ElMessage.success('Data refreshed')
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredTimeline.value.length} timeline events...`)
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const fetchTimelineData = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
  }, 500)
}

const viewDecision = (item: TimelineEvent) => {
  selectedDecision.value = item
  dialogVisible.value = true
}

const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {}

// ==================== Watch for view change ====================
const refreshCharts = () => {
  if (chartView.value === 'gantt') {
    setTimeout(() => {
      initGanttChart()
    }, 100)
  }
}

// ==================== Loading Simulation ====================
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
      initChartDecisions()
      initGanttChart()
      fetchTimelineData()
    }, 400)
  }, 2000)
})
</script>

<style scoped lang="scss">
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

/* ==================== Main Page Styles ==================== */
.decision-timeline-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;

  .breadcrumb {
    margin-bottom: 8px;
  }

  h1 {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 8px 0;
  }

  .description {
    color: #909399;
    font-size: 14px;
    margin: 0;
  }

  .header-actions {
    display: flex;
    gap: 12px;
  }
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
  }

  .stat-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .stat-info {
    flex: 1;
  }

  .stat-title {
    font-size: 14px;
    color: #909399;
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }

  .stat-trend {
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 4px;

    &.up { color: #67c23a; }
    &.down { color: #f56c6c; }

    .trend-label {
      color: #909399;
      margin-left: 4px;
    }
  }

  .stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.timeline-chart-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;

    .chart-controls {
      display: flex;
      gap: 8px;
    }
  }
}

.custom-timeline-container {
  padding: 20px;
  min-height: 400px;
  position: relative;

  .custom-timeline-item {
    display: flex;
    align-items: center;
    margin-bottom: 24px;
    position: relative;

    .timeline-item-label {
      width: 200px;
      font-size: 13px;
      font-weight: 500;
      color: #303133;
      flex-shrink: 0;
    }

    .timeline-item-bar-container {
      flex: 1;
      position: relative;
      height: 32px;
      background-color: #f5f7fa;
      border-radius: 4px;
      overflow: visible;

      .timeline-item-bar {
        position: absolute;
        height: 100%;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
        min-width: 40px;

        &:hover {
          opacity: 0.85;
          transform: scaleY(1.05);
        }

        .bar-label {
          font-size: 11px;
          color: white;
          font-weight: 500;
          text-shadow: 0 0 2px rgba(0,0,0,0.3);
        }
      }

      .timeline-marker {
        position: absolute;
        width: 2px;
        height: 40px;
        background-color: #f56c6c;
        top: -4px;
        z-index: 10;

        &::before {
          content: '';
          position: absolute;
          top: -6px;
          left: -4px;
          width: 10px;
          height: 10px;
          background-color: #f56c6c;
          border-radius: 50%;
        }
      }
    }
  }

  .timeline-scale {
    position: relative;
    height: 30px;
    margin-top: 20px;
    margin-left: 200px;
    border-top: 1px solid #dcdfe6;

    .scale-mark {
      position: absolute;
      transform: translateX(-50%);
      font-size: 11px;
      color: #909399;
      top: 5px;
    }
  }
}

.gantt-chart-container {
  width: 100%;
  height: 450px;
}

.filter-card {
  margin-bottom: 20px;

  .filter-container {
    .filter-row {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
    }
  }
}

.timeline-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .table-actions {
    display: flex;
    gap: 8px;
    align-items: center;
  }
}

.timeline-container {
  max-height: 600px;
  overflow-y: auto;
  padding: 10px;

  .timeline-card-item {
    margin-bottom: 16px;

    .timeline-item-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      flex-wrap: wrap;
      gap: 10px;

      .timeline-item-title {
        display: flex;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;

        .decision-title {
          font-weight: 600;
          font-size: 16px;
          color: #303133;
        }
      }
    }

    .timeline-item-content {
      .timeline-item-event {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
        padding: 8px 12px;
        background: #f5f7fa;
        border-radius: 6px;

        .event-description {
          color: #606266;
          font-size: 14px;
        }
      }
    }
  }
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-timeline-item__wrapper) {
  padding-left: 28px;
}

:deep(.el-timeline-item__tail) {
  left: 4px;
}

:deep(.el-timeline-item__node) {
  width: 16px;
  height: 16px;
  left: -2px;
}

:deep(.el-descriptions) {
  margin-top: 8px;
}
</style>