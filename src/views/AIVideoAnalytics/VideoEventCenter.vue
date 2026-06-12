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
        <div class="loading-tip">AI Video Analytics - Video Event Center</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="video-event-center-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Video Event Center</h1>
        <p>Centralized view of all AI-detected video events with real-time monitoring and investigation tools</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
        <el-button @click="exportEvents">
          <el-icon><Download /></el-icon>
          Export Events
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon danger-bg">
            <el-icon><Bell /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalEventsToday }}</div>
            <div class="stat-label">Events Today</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.criticalEvents }}</div>
            <div class="stat-label">Critical Events</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><Check /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.resolvedEvents }}</div>
            <div class="stat-label">Resolved</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon info-bg">
            <el-icon><Camera /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.activeCameras }}</div>
            <div class="stat-label">Active Cameras</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <el-input
          v-model="filters.search"
          placeholder="Search by event ID, description, or location..."
          clearable
          style="width: 260px"
          :prefix-icon="Search"
      />
      <el-select v-model="filters.eventType" placeholder="Event Type" clearable style="width: 150px">
        <el-option label="All Types" value="" />
        <el-option label="PPE Violation" value="PPE_VIOLATION" />
        <el-option label="Intrusion" value="INTRUSION" />
        <el-option label="Fighting" value="FIGHTING" />
        <el-option label="Falling" value="FALLING" />
        <el-option label="Smoke/Fire" value="SMOKE_FIRE" />
        <el-option label="Vehicle Violation" value="VEHICLE_VIOLATION" />
      </el-select>
      <el-select v-model="filters.severity" placeholder="Severity" clearable style="width: 130px">
        <el-option label="All" value="" />
        <el-option label="Critical" value="CRITICAL" />
        <el-option label="High" value="HIGH" />
        <el-option label="Medium" value="MEDIUM" />
        <el-option label="Low" value="LOW" />
      </el-select>
      <el-select v-model="filters.status" placeholder="Status" clearable style="width: 130px">
        <el-option label="All" value="" />
        <el-option label="New" value="NEW" />
        <el-option label="Investigating" value="INVESTIGATING" />
        <el-option label="Resolved" value="RESOLVED" />
        <el-option label="False Alarm" value="FALSE_ALARM" />
      </el-select>
      <el-select v-model="filters.camera" placeholder="Camera" clearable style="width: 160px">
        <el-option label="All Cameras" value="" />
        <el-option v-for="cam in cameras" :key="cam.id" :label="cam.name" :value="cam.id" />
      </el-select>
      <el-date-picker
          v-model="filters.dateRange"
          type="datetimerange"
          range-separator="to"
          start-placeholder="Start"
          end-placeholder="End"
          style="width: 360px"
      />
      <el-button type="primary" @click="handleSearch">
        <el-icon><Search /></el-icon>
        Apply
      </el-button>
      <el-button @click="resetFilters">
        <el-icon><RefreshLeft /></el-icon>
        Reset
      </el-button>
    </div>

    <!-- Main Content: Video Player + Event List -->
    <el-row :gutter="20">
      <!-- Video Player Section -->
      <el-col :xs="24" :lg="14">
        <div class="video-player-card">
          <div class="card-header">
            <h3>Event Playback</h3>
            <div class="player-controls">
              <el-button-group size="small">
                <el-button @click="playVideo" :disabled="!selectedEvent">
                  <el-icon><VideoPlay /></el-icon>
                </el-button>
                <el-button @click="pauseVideo">
                  <el-icon><VideoPause /></el-icon>
                </el-button>
              </el-button-group>
              <span v-if="selectedEvent" class="event-info-badge">
                {{ selectedEvent.type }} - {{ selectedEvent.camera }}
              </span>
            </div>
          </div>
          <div class="video-container">
            <canvas ref="videoCanvasRef" class="video-canvas"></canvas>
            <div v-if="isPlaying && selectedEvent" class="playback-overlay">
              <div class="playback-progress">
                <el-progress :percentage="playbackProgress" :show-text="false" :stroke-width="3" />
              </div>
              <div class="playback-timestamp">{{ playbackTimestamp }}</div>
            </div>
            <div v-if="!selectedEvent" class="no-event-overlay">
              <el-icon><VideoCamera /></el-icon>
              <span>Select an event to view footage</span>
            </div>
          </div>
          <div class="video-meta" v-if="selectedEvent">
            <el-descriptions :column="3" size="small" border>
              <el-descriptions-item label="Event ID">{{ selectedEvent.id }}</el-descriptions-item>
              <el-descriptions-item label="Camera">{{ selectedEvent.camera }}</el-descriptions-item>
              <el-descriptions-item label="Location">{{ selectedEvent.location }}</el-descriptions-item>
              <el-descriptions-item label="Confidence">{{ (selectedEvent.confidence * 100).toFixed(0) }}%</el-descriptions-item>
              <el-descriptions-item label="Severity">
                <el-tag :type="getSeverityTag(selectedEvent.severity)" size="small">
                  {{ selectedEvent.severity }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="Status">
                <el-tag :type="getStatusTag(selectedEvent.status)" size="small">
                  {{ selectedEvent.status }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>
      </el-col>

      <!-- Event List Section -->
      <el-col :xs="24" :lg="10">
        <div class="event-list-card">
          <div class="card-header">
            <h3>Event Timeline</h3>
            <el-badge :value="unreviewedCount" :hidden="unreviewedCount === 0" class="item">
              <el-button size="small" @click="markAllAsReviewed">Mark All Read</el-button>
            </el-badge>
          </div>
          <div class="event-timeline">
            <div
                v-for="event in paginatedEvents"
                :key="event.id"
                class="timeline-item"
                :class="{ selected: selectedEvent?.id === event.id, unread: !event.read }"
                @click="selectEvent(event)"
            >
              <div class="timeline-marker" :class="getSeverityClass(event.severity)">
                <div class="marker-dot"></div>
                <div class="marker-line"></div>
              </div>
              <div class="timeline-content">
                <div class="event-header-row">
                  <span class="event-type">{{ event.type }}</span>
                  <span class="event-time">{{ formatTime(event.timestamp) }}</span>
                </div>
                <div class="event-description">{{ event.description }}</div>
                <div class="event-footer">
                  <span class="event-location">
                    <el-icon><Location /></el-icon>
                    {{ event.camera }}
                  </span>
                  <el-tag :type="getSeverityTag(event.severity)" size="small">
                    {{ event.severity }}
                  </el-tag>
                </div>
                <div class="event-actions" v-if="selectedEvent?.id === event.id">
                  <el-button size="small" link @click.stop="updateEventStatus(event, 'INVESTIGATING')">
                    <el-icon><Search /></el-icon> Investigate
                  </el-button>
                  <el-button size="small" link type="success" @click.stop="updateEventStatus(event, 'RESOLVED')">
                    <el-icon><Check /></el-icon> Resolve
                  </el-button>
                  <el-button size="small" link type="danger" @click.stop="updateEventStatus(event, 'FALSE_ALARM')">
                    <el-icon><Close /></el-icon> False Alarm
                  </el-button>
                  <el-button size="small" link @click.stop="exportEvent(event)">
                    <el-icon><Download /></el-icon> Export
                  </el-button>
                </div>
              </div>
            </div>
            <div v-if="filteredEvents.length === 0" class="no-events">
              <el-empty description="No events found" />
            </div>
          </div>
          <div class="pagination-wrapper" v-if="filteredEvents.length > 0">
            <el-pagination
                v-model:current-page="pagination.currentPage"
                v-model:page-size="pagination.pageSize"
                :page-sizes="[5, 10, 20]"
                :total="pagination.total"
                layout="total, prev, pager, next"
                small
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
            />
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Charts Section -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="card-header">
            <h3>Event Trend (Last 7 Days)</h3>
            <el-select v-model="trendPeriod" size="small" style="width: 100px">
              <el-option label="7 Days" value="7" />
              <el-option label="14 Days" value="14" />
              <el-option label="30 Days" value="30" />
            </el-select>
          </div>
          <div ref="trendChartRef" class="chart-container"></div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="card-header">
            <h3>Events by Camera</h3>
          </div>
          <div ref="cameraChartRef" class="chart-container"></div>
        </div>
      </el-col>
    </el-row>

    <!-- Event Detail Dialog -->
    <el-dialog v-model="detailDialog.visible" title="Event Details" width="650px">
      <div v-if="detailDialog.event">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Event ID">{{ detailDialog.event.id }}</el-descriptions-item>
          <el-descriptions-item label="Type">{{ detailDialog.event.type }}</el-descriptions-item>
          <el-descriptions-item label="Timestamp">{{ formatFullTimestamp(detailDialog.event.timestamp) }}</el-descriptions-item>
          <el-descriptions-item label="Camera">{{ detailDialog.event.camera }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ detailDialog.event.location }}</el-descriptions-item>
          <el-descriptions-item label="Confidence">{{ (detailDialog.event.confidence * 100).toFixed(0) }}%</el-descriptions-item>
          <el-descriptions-item label="Severity">
            <el-tag :type="getSeverityTag(detailDialog.event.severity)">{{ detailDialog.event.severity }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTag(detailDialog.event.status)">{{ detailDialog.event.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ detailDialog.event.description }}</el-descriptions-item>
          <el-descriptions-item label="AI Notes" :span="2">
            <div class="ai-notes">
              <el-icon><MagicStick /></el-icon>
              <span>{{ detailDialog.event.aiNotes || 'No additional AI analysis available' }}</span>
            </div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="detailDialog.visible = false">Close</el-button>
        <el-button type="primary" @click="exportEvent(detailDialog.event)">Export Evidence</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Refresh,
  Download,
  Bell,
  Warning,
  Check,
  Camera,
  Search,
  RefreshLeft,
  VideoPlay,
  VideoPause,
  VideoCamera,
  Location,
  Close,
  MagicStick
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading video events...',
  'Initializing AI models...',
  'Almost ready...'
]

// ==================== Type Definitions ====================
interface VideoEvent {
  id: string
  type: string
  description: string
  camera: string
  cameraId: string
  location: string
  timestamp: Date
  confidence: number
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'
  status: 'NEW' | 'INVESTIGATING' | 'RESOLVED' | 'FALSE_ALARM'
  read: boolean
  aiNotes?: string
  thumbnail?: string
}

interface Camera {
  id: string
  name: string
  location: string
}

// ==================== 模拟数据 ====================
const cameras: Camera[] = [
  { id: 'CAM-001', name: 'Main Entrance', location: 'Building A' },
  { id: 'CAM-002', name: 'Lobby East', location: 'Building A' },
  { id: 'CAM-003', name: 'Corridor North', location: 'Building B' },
  { id: 'CAM-004', name: 'Parking Area', location: 'West Parking' },
  { id: 'CAM-005', name: 'Loading Dock', location: 'South Building' },
  { id: 'CAM-006', name: 'Server Room', location: 'Data Center' },
  { id: 'CAM-007', name: 'Cafeteria', location: 'Building A' }
]

const eventTypes = [
  { type: 'PPE Violation', code: 'PPE_VIOLATION', severity: 'HIGH', desc: 'Missing required safety equipment' },
  { type: 'Intrusion', code: 'INTRUSION', severity: 'CRITICAL', desc: 'Unauthorized access detected' },
  { type: 'Fighting', code: 'FIGHTING', severity: 'CRITICAL', desc: 'Physical altercation detected' },
  { type: 'Falling', code: 'FALLING', severity: 'CRITICAL', desc: 'Person fallen to ground' },
  { type: 'Smoke/Fire', code: 'SMOKE_FIRE', severity: 'CRITICAL', desc: 'Smoke or fire detected' },
  { type: 'Vehicle Violation', code: 'VEHICLE_VIOLATION', severity: 'MEDIUM', desc: 'Vehicle rule violation' }
]

const generateMockEvents = (count: number = 50): VideoEvent[] => {
  const events: VideoEvent[] = []
  const now = new Date()

  for (let i = 0; i < count; i++) {
    const eventType = eventTypes[Math.floor(Math.random() * eventTypes.length)]
    const camera = cameras[Math.floor(Math.random() * cameras.length)]
    const timestamp = new Date(now.getTime() - Math.random() * 7 * 24 * 60 * 60 * 1000)
    const statuses: ('NEW' | 'INVESTIGATING' | 'RESOLVED' | 'FALSE_ALARM')[] = ['NEW', 'INVESTIGATING', 'RESOLVED', 'FALSE_ALARM']
    const status = statuses[Math.floor(Math.random() * statuses.length)]
    const read = status !== 'NEW' && Math.random() > 0.3

    events.push({
      id: `EVT-${String(i + 1).padStart(6, '0')}`,
      type: eventType.type,
      description: `${eventType.desc} in ${camera.location} - ${camera.name}`,
      camera: camera.name,
      cameraId: camera.id,
      location: camera.location,
      timestamp: timestamp,
      confidence: 0.65 + Math.random() * 0.3,
      severity: eventType.severity as 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW',
      status: status,
      read: read,
      aiNotes: generateAINotes(eventType.type)
    })
  }

  return events.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
}

const generateAINotes = (eventType: string): string => {
  const notes: Record<string, string[]> = {
    'PPE Violation': ['Missing hard hat detected', 'Safety vest not visible', 'No eye protection', 'Gloves not detected'],
    'Intrusion': ['Unauthorized access after hours', 'Tailgating detected', 'Multiple failed access attempts'],
    'Fighting': ['Aggressive posture detected', 'Multiple persons involved', 'High motion intensity'],
    'Falling': ['Sudden vertical movement', 'Person stationary after fall', 'Possible medical emergency'],
    'Smoke/Fire': ['Smoke plume detected', 'Abnormal heat signature', 'Flame visual confirmation'],
    'Vehicle Violation': ['Parking violation detected', 'Speeding in parking area', 'Wrong way entry']
  }
  const noteList = notes[eventType] || ['AI analysis complete']
  return noteList[Math.floor(Math.random() * noteList.length)]
}

// ==================== 响应式状态 ====================
const allEvents = ref<VideoEvent[]>([])
const selectedEvent = ref<VideoEvent | null>(null)
const videoCanvasRef = ref<HTMLCanvasElement | null>(null)
const trendChartRef = ref<HTMLElement | null>(null)
const cameraChartRef = ref<HTMLElement | null>(null)

let trendChart: echarts.ECharts | null = null
let cameraChart: echarts.ECharts | null = null
let animationFrameId: number | null = null
let playbackInterval: number | null = null

const trendPeriod = ref('7')
const isPlaying = ref(false)
const playbackProgress = ref(0)
const playbackTimestamp = ref('')

const filters = reactive({
  search: '',
  eventType: '',
  severity: '',
  status: '',
  camera: '',
  dateRange: null as Date[] | null
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

const stats = reactive({
  totalEventsToday: 0,
  criticalEvents: 0,
  resolvedEvents: 0,
  activeCameras: cameras.length
})

const detailDialog = reactive({
  visible: false,
  event: null as VideoEvent | null
})

// ==================== 计算属性 ====================
const filteredEvents = computed(() => {
  let filtered = [...allEvents.value]

  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    filtered = filtered.filter(e =>
        e.id.toLowerCase().includes(searchLower) ||
        e.description.toLowerCase().includes(searchLower) ||
        e.location.toLowerCase().includes(searchLower)
    )
  }

  if (filters.eventType) {
    filtered = filtered.filter(e => {
      const typeMap: Record<string, string> = {
        'PPE_VIOLATION': 'PPE Violation',
        'INTRUSION': 'Intrusion',
        'FIGHTING': 'Fighting',
        'FALLING': 'Falling',
        'SMOKE_FIRE': 'Smoke/Fire',
        'VEHICLE_VIOLATION': 'Vehicle Violation'
      }
      return e.type === typeMap[filters.eventType]
    })
  }

  if (filters.severity) {
    filtered = filtered.filter(e => e.severity === filters.severity)
  }

  if (filters.status) {
    filtered = filtered.filter(e => e.status === filters.status)
  }

  if (filters.camera) {
    filtered = filtered.filter(e => e.cameraId === filters.camera)
  }

  if (filters.dateRange && filters.dateRange.length === 2) {
    const [start, end] = filters.dateRange
    filtered = filtered.filter(e => e.timestamp >= start && e.timestamp <= end)
  }

  pagination.total = filtered.length
  return filtered
})

const paginatedEvents = computed(() => {
  const start = (pagination.currentPage - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filteredEvents.value.slice(start, end)
})

const unreviewedCount = computed(() => allEvents.value.filter(e => !e.read).length)

// ==================== 辅助函数 ====================
const formatTime = (date: Date) => {
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins} min ago`
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)} hr ago`
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

const formatFullTimestamp = (date: Date) => {
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const getSeverityTag = (severity: string) => {
  const map: Record<string, string> = {
    'CRITICAL': 'danger',
    'HIGH': 'danger',
    'MEDIUM': 'warning',
    'LOW': 'info'
  }
  return map[severity] || 'info'
}

const getStatusTag = (status: string) => {
  const map: Record<string, string> = {
    'NEW': 'danger',
    'INVESTIGATING': 'warning',
    'RESOLVED': 'success',
    'FALSE_ALARM': 'info'
  }
  return map[status] || 'info'
}

const getSeverityClass = (severity: string) => {
  const map: Record<string, string> = {
    'CRITICAL': 'critical',
    'HIGH': 'high',
    'MEDIUM': 'medium',
    'LOW': 'low'
  }
  return map[severity] || 'medium'
}

const updateStats = () => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  stats.totalEventsToday = allEvents.value.filter(e => e.timestamp >= today).length
  stats.criticalEvents = allEvents.value.filter(e => e.severity === 'CRITICAL' && e.status !== 'RESOLVED').length
  stats.resolvedEvents = allEvents.value.filter(e => e.status === 'RESOLVED').length
}

// ==================== 视频回放模拟 ====================
const drawFrame = (progress: number) => {
  const canvas = videoCanvasRef.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  canvas.width = canvas.clientWidth
  canvas.height = 360

  // 背景
  const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height)
  gradient.addColorStop(0, '#1a1a2e')
  gradient.addColorStop(1, '#16213e')
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  if (!selectedEvent.value) return

  // 根据进度绘制不同帧
  const frameIndex = Math.floor(progress * 30)
  const time = Date.now() / 1000

  // 绘制模拟场景
  ctx.fillStyle = `rgba(64, 158, 255, ${0.3 + Math.sin(time) * 0.1})`
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  // 绘制区域网格
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)'
  ctx.lineWidth = 1
  for (let i = 0; i < canvas.width; i += 100) {
    ctx.beginPath()
    ctx.moveTo(i, 0)
    ctx.lineTo(i, canvas.height)
    ctx.stroke()
    ctx.beginPath()
    ctx.moveTo(0, i % canvas.height)
    ctx.lineTo(canvas.width, i % canvas.height)
    ctx.stroke()
  }

  // 根据事件类型绘制不同的动画
  const centerX = canvas.width / 2
  const centerY = canvas.height / 2

  ctx.font = 'bold 16px Arial'
  ctx.fillStyle = '#f56c6c'
  ctx.textAlign = 'center'
  ctx.fillText(selectedEvent.value.type, centerX, 50)

  // 绘制检测框
  ctx.strokeStyle = '#f56c6c'
  ctx.lineWidth = 3
  const boxX = centerX - 100 + Math.sin(time * 2) * 10
  const boxY = centerY - 80 + Math.cos(time) * 5
  ctx.strokeRect(boxX, boxY, 200, 150)

  ctx.fillStyle = '#f56c6c'
  ctx.font = 'bold 12px Arial'
  ctx.fillText(`${selectedEvent.value.type} - ${Math.floor(selectedEvent.value.confidence * 100)}%`, boxX, boxY - 5)

  // 绘制时间戳水印
  ctx.fillStyle = 'rgba(255, 255, 255, 0.5)'
  ctx.font = '12px monospace'
  ctx.textAlign = 'right'
  ctx.fillText(playbackTimestamp.value || formatFullTimestamp(selectedEvent.value.timestamp), canvas.width - 10, canvas.height - 10)
}

const startPlayback = () => {
  if (playbackInterval) clearInterval(playbackInterval)

  playbackProgress.value = 0
  const startTime = Date.now()
  const duration = 10000 // 10 seconds playback

  drawFrame(0)

  playbackInterval = window.setInterval(() => {
    const elapsed = Date.now() - startTime
    const progress = Math.min(elapsed / duration, 1)
    playbackProgress.value = progress * 100

    const timestamp = new Date(selectedEvent.value!.timestamp.getTime() + elapsed * 1000)
    playbackTimestamp.value = timestamp.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })

    drawFrame(progress)

    if (progress >= 1) {
      pauseVideo()
    }
  }, 50)
}

const playVideo = () => {
  if (!selectedEvent.value) {
    ElMessage.warning('Please select an event first')
    return
  }
  isPlaying.value = true
  startPlayback()
}

const pauseVideo = () => {
  isPlaying.value = false
  if (playbackInterval) {
    clearInterval(playbackInterval)
    playbackInterval = null
  }
}

// ==================== 图表渲染 ====================
const renderTrendChart = () => {
  if (!trendChartRef.value) return

  if (trendChart) trendChart.dispose()
  trendChart = echarts.init(trendChartRef.value)

  const days = parseInt(trendPeriod.value)
  const dates = []
  const criticalData = []
  const highData = []
  const mediumData = []

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    dates.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }))

    criticalData.push(Math.floor(Math.random() * 8) + 1)
    highData.push(Math.floor(Math.random() * 12) + 3)
    mediumData.push(Math.floor(Math.random() * 20) + 5)
  }

  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Critical', 'High', 'Medium'], bottom: 0 },
    grid: { left: '3%', right: '4%', top: '10%', bottom: '12%', containLabel: true },
    xAxis: { type: 'category', data: dates, axisLabel: { rotate: 45 } },
    yAxis: { type: 'value', name: 'Event Count' },
    series: [
      { name: 'Critical', type: 'bar', data: criticalData, itemStyle: { color: '#f56c6c', borderRadius: [4, 4, 0, 0] } },
      { name: 'High', type: 'bar', data: highData, itemStyle: { color: '#e6a23c', borderRadius: [4, 4, 0, 0] } },
      { name: 'Medium', type: 'bar', data: mediumData, itemStyle: { color: '#409eff', borderRadius: [4, 4, 0, 0] } }
    ]
  })
}

const renderCameraChart = () => {
  if (!cameraChartRef.value) return

  if (cameraChart) cameraChart.dispose()
  cameraChart = echarts.init(cameraChartRef.value)

  const cameraStats: Record<string, number> = {}
  cameras.forEach(cam => { cameraStats[cam.name] = 0 })
  allEvents.value.forEach(event => {
    cameraStats[event.camera] = (cameraStats[event.camera] || 0) + 1
  })

  cameraChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', top: '5%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value', name: 'Event Count' },
    yAxis: { type: 'category', data: Object.keys(cameraStats), axisLabel: { fontSize: 11 } },
    series: [{
      type: 'bar',
      data: Object.values(cameraStats),
      itemStyle: { color: '#409eff', borderRadius: [0, 4, 4, 0] }
    }]
  })
}

// ==================== 交互事件 ====================
const refreshData = () => {
  allEvents.value = generateMockEvents(50)
  updateStats()
  renderCameraChart()
  renderTrendChart()
  ElMessage.success('Data refreshed successfully')
}

const selectEvent = (event: VideoEvent) => {
  pauseVideo()
  selectedEvent.value = event
  event.read = true
  playbackProgress.value = 0
  drawFrame(0)
}

const updateEventStatus = (event: VideoEvent, newStatus: VideoEvent['status']) => {
  event.status = newStatus
  if (newStatus !== 'NEW') {
    event.read = true
  }
  ElMessage.success(`Event status updated to ${newStatus}`)
  updateStats()
}

const markAllAsReviewed = () => {
  allEvents.value.forEach(e => { e.read = true })
  ElMessage.success('All events marked as read')
}

const handleSearch = () => {
  pagination.currentPage = 1
  ElMessage.success('Filters applied')
}

const resetFilters = () => {
  filters.search = ''
  filters.eventType = ''
  filters.severity = ''
  filters.status = ''
  filters.camera = ''
  filters.dateRange = null
  pagination.currentPage = 1
  ElMessage.info('Filters reset')
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.currentPage = 1
}

const handleCurrentChange = (page: number) => {
  pagination.currentPage = page
}

const exportEvent = (event: VideoEvent) => {
  const data = JSON.stringify(event, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `event-${event.id}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Event exported successfully')
}

const exportEvents = () => {
  const report = {
    generatedAt: new Date().toISOString(),
    summary: stats,
    events: filteredEvents.value
  }
  const data = JSON.stringify(report, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `video-events-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Events exported successfully')
}

// ==================== 数据加载 ====================
const loadData = () => {
  allEvents.value = generateMockEvents(50)
  updateStats()

  nextTick(() => {
    renderTrendChart()
    renderCameraChart()
    drawFrame(0)
  })
}

// ==================== 生命周期 ====================
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
      loadData()
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (playbackInterval) clearInterval(playbackInterval)
  window.removeEventListener('resize', () => {
    trendChart?.resize()
    cameraChart?.resize()
  })
})

watch(isLoaded, (loaded) => {
  if (loaded) {
    window.addEventListener('resize', () => {
      trendChart?.resize()
      cameraChart?.resize()
    })
  }
})

watch(trendPeriod, () => renderTrendChart())
watch(allEvents, () => {
  renderCameraChart()
  updateStats()
}, { deep: true })
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

/* ==================== Main Content Styles ==================== */
.video-event-center-page {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #1f2f3d;
}

.page-header p {
  margin: 0;
  color: #5e6e82;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.danger-bg { background-color: #fef0f0; color: #f56c6c; }
.warning-bg { background-color: #fff3e0; color: #e6a23c; }
.success-bg { background-color: #f0f9eb; color: #67c23a; }
.info-bg { background-color: #ecf5ff; color: #409eff; }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #8c9aab;
  margin-top: 4px;
}

.filter-bar {
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

/* Video Player */
.video-player-card, .event-list-card, .chart-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

.player-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.event-info-badge {
  font-size: 12px;
  color: #5e6e82;
  background: #f5f7fa;
  padding: 4px 12px;
  border-radius: 16px;
}

.video-container {
  position: relative;
  background-color: #1a1a2e;
  border-radius: 8px;
  overflow: hidden;
}

.video-canvas {
  width: 100%;
  height: 360px;
  display: block;
}

.no-event-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  font-size: 16px;
}

.no-event-overlay .el-icon {
  font-size: 48px;
  opacity: 0.5;
}

.playback-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  padding: 12px;
}

.playback-progress {
  margin-bottom: 8px;
}

.playback-timestamp {
  text-align: right;
  font-size: 12px;
  color: white;
  font-family: monospace;
}

.video-meta {
  margin-top: 16px;
}

/* Event Timeline */
.event-timeline {
  max-height: 520px;
  overflow-y: auto;
}

.timeline-item {
  display: flex;
  position: relative;
  cursor: pointer;
  transition: background-color 0.2s;
}

.timeline-item:hover {
  background-color: #f5f7fa;
}

.timeline-item.selected {
  background-color: #ecf5ff;
}

.timeline-item.unread .timeline-content {
  border-left: 3px solid #409eff;
}

.timeline-marker {
  position: relative;
  width: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.marker-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-top: 16px;
  z-index: 1;
}

.timeline-marker.critical .marker-dot { background-color: #f56c6c; box-shadow: 0 0 0 3px rgba(245, 108, 108, 0.2); }
.timeline-marker.high .marker-dot { background-color: #f56c6c; box-shadow: 0 0 0 3px rgba(245, 108, 108, 0.2); }
.timeline-marker.medium .marker-dot { background-color: #e6a23c; box-shadow: 0 0 0 3px rgba(230, 162, 60, 0.2); }
.timeline-marker.low .marker-dot { background-color: #409eff; box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.2); }

.marker-line {
  flex: 1;
  width: 2px;
  background-color: #ebeef5;
  margin-top: 4px;
}

.timeline-item:last-child .marker-line {
  display: none;
}

.timeline-content {
  flex: 1;
  padding: 12px 12px 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.event-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.event-type {
  font-weight: 600;
  font-size: 14px;
  color: #1f2f3d;
}

.event-time {
  font-size: 11px;
  color: #8c9aab;
}

.event-description {
  font-size: 12px;
  color: #5e6e82;
  margin-bottom: 8px;
}

.event-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.event-location {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #8c9aab;
}

.event-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid #ebeef5;
}

.no-events {
  padding: 40px 0;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
  margin-top: 8px;
}

/* Charts */
.charts-row {
  margin-bottom: 0;
}

.chart-container {
  height: 280px;
  width: 100%;
}

/* AI Notes */
.ai-notes {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #67c23a;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
}

:deep(.el-progress-bar__outer) {
  background-color: rgba(255, 255, 255, 0.2);
}
</style>