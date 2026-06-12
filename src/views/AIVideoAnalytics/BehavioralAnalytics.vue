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
        <div class="loading-tip">AI Video Analytics - Behavioral Analytics</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="behavioral-analytics-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Behavioral Analytics</h1>
        <p>AI-powered human behavior detection, pattern analysis, and anomaly identification</p>
      </div>
      <div class="header-actions">
        <el-select v-model="selectedCamera" placeholder="Select Camera" style="width: 200px">
          <el-option
              v-for="camera in cameras"
              :key="camera.id"
              :label="camera.name"
              :value="camera.id"
          />
        </el-select>
        <el-button type="primary" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
        <el-button @click="exportReport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.alertsToday }}</div>
            <div class="stat-label">Alerts Today</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon danger-bg">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.anomaliesDetected }}</div>
            <div class="stat-label">Anomalies (Last 24h)</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.avgResponseTime }}</div>
            <div class="stat-label">Avg Response Time</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon info-bg">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.detectionAccuracy }}%</div>
            <div class="stat-label">Detection Accuracy</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Main Content Row -->
    <el-row :gutter="20">
      <!-- Video Feed / Heatmap Area -->
      <el-col :xs="24" :lg="14">
        <div class="video-card">
          <div class="card-header">
            <h3>Live Monitoring</h3>
            <div class="live-badge">
              <span class="live-dot"></span>
              LIVE
            </div>
          </div>
          <div class="video-container" ref="videoContainerRef">
            <canvas ref="videoCanvasRef" class="video-canvas"></canvas>
            <div v-if="selectedEvent" class="event-tooltip" :style="tooltipStyle">
              <div class="event-tooltip-header">
                <strong>{{ selectedEvent.type }}</strong>
                <el-button link @click="selectedEvent = null">✕</el-button>
              </div>
              <div>Confidence: {{ (selectedEvent.confidence * 100).toFixed(0) }}%</div>
              <div>Location: {{ selectedEvent.location }}</div>
              <div>Time: {{ selectedEvent.time }}</div>
            </div>
          </div>
          <div class="video-controls">
            <el-button-group>
              <el-button size="small" @click="playVideo">
                <el-icon><VideoPlay /></el-icon>
              </el-button>
              <el-button size="small" @click="pauseVideo">
                <el-icon><VideoPause /></el-icon>
              </el-button>
            </el-button-group>
            <span class="timestamp">{{ currentTimestamp }}</span>
            <div class="behavior-legend">
              <span><span class="legend-dot running"></span> Running</span>
              <span><span class="legend-dot loitering"></span> Loitering</span>
              <span><span class="legend-dot fighting"></span> Fighting</span>
              <span><span class="legend-dot falling"></span> Falling</span>
            </div>
          </div>
        </div>
      </el-col>

      <!-- Real-time Events Feed -->
      <el-col :xs="24" :lg="10">
        <div class="events-card">
          <div class="card-header">
            <h3>Real-time Events</h3>
            <el-tag type="danger" size="small">{{ pendingEvents.length }} pending</el-tag>
          </div>
          <div class="events-feed">
            <div
                v-for="event in eventsFeed"
                :key="event.id"
                class="event-item"
                :class="{ unread: !event.read }"
                @click="selectEvent(event)"
            >
              <div class="event-icon" :class="getEventColorClass(event.type)">
                <el-icon><component :is="getEventIcon(event.type)" /></el-icon>
              </div>
              <div class="event-content">
                <div class="event-header">
                  <span class="event-type">{{ event.type }}</span>
                  <span class="event-time">{{ formatRelativeTime(event.timestamp) }}</span>
                </div>
                <div class="event-desc">{{ event.description }}</div>
                <div class="event-meta">
                  <span><el-icon><Location /></el-icon> {{ event.camera }} - {{ event.zone }}</span>
                  <span class="confidence">Confidence: {{ (event.confidence * 100).toFixed(0) }}%</span>
                </div>
              </div>
              <el-button
                  v-if="!event.reviewed"
                  size="small"
                  type="primary"
                  link
                  @click.stop="reviewEvent(event)"
              >
                Review
              </el-button>
            </div>
            <div v-if="eventsFeed.length === 0" class="no-events">
              <el-empty description="No recent events" />
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Charts Row -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="card-header">
            <h3>Behavior Trends (Last 7 Days)</h3>
            <el-select v-model="trendPeriod" size="small" style="width: 120px">
              <el-option label="Last 7 Days" value="7" />
              <el-option label="Last 14 Days" value="14" />
              <el-option label="Last 30 Days" value="30" />
            </el-select>
          </div>
          <div ref="trendChartRef" class="chart-container"></div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="card-header">
            <h3>Behavior Distribution</h3>
          </div>
          <div ref="distributionChartRef" class="chart-container"></div>
        </div>
      </el-col>
    </el-row>

    <!-- Heatmap & Zone Analytics -->
    <el-row :gutter="20">
      <el-col :xs="24" :lg="12">
        <div class="heatmap-card">
          <div class="card-header">
            <h3>Activity Heatmap</h3>
            <el-select v-model="heatmapPeriod" size="small" style="width: 100px">
              <el-option label="Today" value="today" />
              <el-option label="This Week" value="week" />
              <el-option label="This Month" value="month" />
            </el-select>
          </div>
          <div ref="heatmapChartRef" class="heatmap-container"></div>
          <div class="heatmap-legend">
            <span>Low</span>
            <div class="gradient-bar"></div>
            <span>High</span>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="zone-card">
          <div class="card-header">
            <h3>Zone Activity</h3>
          </div>
          <div class="zone-list">
            <div v-for="zone in zoneActivity" :key="zone.name" class="zone-item">
              <div class="zone-info">
                <span class="zone-name">{{ zone.name }}</span>
                <span class="zone-count">{{ zone.count }} events</span>
              </div>
              <el-progress :percentage="zone.percentage" :color="getZoneColor(zone.percentage)" :stroke-width="8" />
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Event Detail Dialog -->
    <el-dialog v-model="detailDialog.visible" title="Event Details" width="600px">
      <div v-if="detailDialog.event" class="event-detail">
        <div class="detail-video-placeholder">
          <el-image :src="detailDialog.event.thumbnail" fit="cover">
            <template #error>
              <div class="image-placeholder">
                <el-icon><Camera /></el-icon>
                <span>Thumbnail not available</span>
              </div>
            </template>
          </el-image>
        </div>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Event ID">{{ detailDialog.event.id }}</el-descriptions-item>
          <el-descriptions-item label="Type">
            <el-tag :type="getEventColorClass(detailDialog.event.type)" size="small">
              {{ detailDialog.event.type }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Timestamp">{{ formatTimestamp(detailDialog.event.timestamp) }}</el-descriptions-item>
          <el-descriptions-item label="Camera">{{ detailDialog.event.camera }}</el-descriptions-item>
          <el-descriptions-item label="Zone">{{ detailDialog.event.zone }}</el-descriptions-item>
          <el-descriptions-item label="Confidence">{{ (detailDialog.event.confidence * 100).toFixed(0) }}%</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ detailDialog.event.description }}</el-descriptions-item>
          <el-descriptions-item label="Review Status">
            <el-tag :type="detailDialog.event.reviewed ? 'success' : 'warning'" size="small">
              {{ detailDialog.event.reviewed ? 'Reviewed' : 'Pending Review' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        <div class="detail-actions">
          <el-button @click="markAsReviewed(detailDialog.event)">Mark as Reviewed</el-button>
          <el-button type="primary" @click="exportEvent(detailDialog.event)">Export Evidence</el-button>
        </div>
      </div>
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
  Warning,
  User,
  Timer,
  DataAnalysis,
  VideoPlay,
  VideoPause,
  Location,
  Camera,
  Bell,
  Guide,
  Scissor,
  Aim,
  UserFilled
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading video streams...',
  'Initializing AI models...',
  'Almost ready...'
]

// ==================== Type Definitions ====================
interface BehaviorEvent {
  id: string
  type: string
  description: string
  camera: string
  zone: string
  timestamp: Date
  confidence: number
  read: boolean
  reviewed: boolean
  thumbnail?: string
  location?: { x: number; y: number }
}

interface Camera {
  id: string
  name: string
  location: string
}

interface ZoneActivity {
  name: string
  count: number
  percentage: number
}

// ==================== 模拟数据 ====================
const cameras: Camera[] = [
  { id: 'CAM-001', name: 'Main Entrance', location: 'Building A - Ground Floor' },
  { id: 'CAM-002', name: 'Lobby East', location: 'Building A - Lobby' },
  { id: 'CAM-003', name: 'Corridor North', location: 'Building B - 2nd Floor' },
  { id: 'CAM-004', name: 'Parking Area', location: 'West Parking' },
  { id: 'CAM-005', name: 'Cafeteria', location: 'Building A - 1st Floor' }
]

const behaviorTypes = [
  { type: 'Loitering', icon: 'Guide', color: 'warning', threshold: 0.7 },
  { type: 'Running', icon: 'Guide', color: 'danger', threshold: 0.8 },
  { type: 'Fighting', icon: 'Scissor', color: 'danger', threshold: 0.85 },
  { type: 'Falling', icon: 'UserFilled', color: 'danger', threshold: 0.9 },
  { type: 'Suspicious Activity', icon: 'Aim', color: 'warning', threshold: 0.75 },
  { type: 'Unauthorized Access', icon: 'Bell', color: 'danger', threshold: 0.85 }
]

const zones = ['Entry Gate', 'Lobby', 'Corridor A', 'Corridor B', 'Elevator Area', 'Parking Lot', 'Restroom Area']

// 生成模拟事件
const generateMockEvents = (count: number = 25): BehaviorEvent[] => {
  const events: BehaviorEvent[] = []
  const now = new Date()

  for (let i = 0; i < count; i++) {
    const behavior = behaviorTypes[Math.floor(Math.random() * behaviorTypes.length)]
    const camera = cameras[Math.floor(Math.random() * cameras.length)]
    const zone = zones[Math.floor(Math.random() * zones.length)]
    const timestamp = new Date(now.getTime() - Math.random() * 24 * 60 * 60 * 1000)

    events.push({
      id: `EVT-${String(i + 1).padStart(5, '0')}`,
      type: behavior.type,
      description: `${behavior.type} detected in ${zone}`,
      camera: camera.name,
      zone: zone,
      timestamp: timestamp,
      confidence: 0.6 + Math.random() * 0.35,
      read: Math.random() > 0.7,
      reviewed: Math.random() > 0.8,
      location: { x: 100 + Math.random() * 500, y: 100 + Math.random() * 300 }
    })
  }

  return events.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
}

// ==================== 响应式状态 ====================
const selectedCamera = ref('CAM-001')
const trendPeriod = ref('7')
const heatmapPeriod = ref('today')
const selectedEvent = ref<BehaviorEvent | null>(null)
const tooltipStyle = ref({})
const videoCanvasRef = ref<HTMLCanvasElement | null>(null)
const videoContainerRef = ref<HTMLDivElement | null>(null)
const trendChartRef = ref<HTMLElement | null>(null)
const distributionChartRef = ref<HTMLElement | null>(null)
const heatmapChartRef = ref<HTMLElement | null>(null)

let trendChart: echarts.ECharts | null = null
let distributionChart: echarts.ECharts | null = null
let heatmapChart: echarts.ECharts | null = null
let animationFrameId: number | null = null
let frameCount = 0

const events = ref<BehaviorEvent[]>([])
const pendingEvents = computed(() => events.value.filter(e => !e.reviewed))
const eventsFeed = computed(() => events.value.slice(0, 15))

const stats = reactive({
  alertsToday: 0,
  anomaliesDetected: 0,
  avgResponseTime: '2.4 min',
  detectionAccuracy: 94.7
})

const zoneActivity = ref<ZoneActivity[]>([])

const detailDialog = reactive({
  visible: false,
  event: null as BehaviorEvent | null
})

const currentTimestamp = ref('')

// ==================== 辅助函数 ====================
const getEventIcon = (type: string) => {
  const map: Record<string, any> = {
    'Loitering': Guide,
    'Guide': Guide,
    'Fighting': Scissor,
    'Falling': UserFilled,
    'Suspicious Activity': Aim,
    'Unauthorized Access': Bell
  }
  return map[type] || Bell
}

const getEventColorClass = (type: string) => {
  const map: Record<string, string> = {
    'Loitering': 'warning',
    'Guide': 'danger',
    'Fighting': 'danger',
    'Falling': 'danger',
    'Suspicious Activity': 'warning',
    'Unauthorized Access': 'danger'
  }
  return map[type] || 'info'
}

const formatRelativeTime = (date: Date) => {
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins} min ago`
  if (diffHours < 24) return `${diffHours} hr ago`
  return `${Math.floor(diffHours / 24)} days ago`
}

const formatTimestamp = (date: Date) => {
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const updateTimestamp = () => {
  currentTimestamp.value = new Date().toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const updateStatsFromEvents = () => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  const todayEvents = events.value.filter(e => e.timestamp >= today)
  stats.alertsToday = todayEvents.length
  stats.anomaliesDetected = events.value.filter(e =>
      e.type === 'Fighting' || e.type === 'Falling' || e.type === 'Unauthorized Access'
  ).length
}

// 更新区域活动统计
const updateZoneActivity = () => {
  const zoneCount: Record<string, number> = {}
  zones.forEach(zone => { zoneCount[zone] = 0 })

  events.value.forEach(event => {
    if (zoneCount[event.zone] !== undefined) {
      zoneCount[event.zone]++
    }
  })

  const total = events.value.length
  zoneActivity.value = Object.entries(zoneCount)
      .map(([name, count]) => ({ name, count, percentage: total > 0 ? (count / total) * 100 : 0 }))
      .sort((a, b) => b.count - a.count)
}

const getZoneColor = (percentage: number) => {
  if (percentage > 20) return '#f56c6c'
  if (percentage > 10) return '#e6a23c'
  return '#67c23a'
}

// ==================== 视频画布绘制 ====================
const drawVideoFrame = () => {
  const canvas = videoCanvasRef.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  frameCount++

  // 模拟视频帧绘制
  const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height)
  gradient.addColorStop(0, '#1a1a2e')
  gradient.addColorStop(1, '#16213e')
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  // 绘制网格线
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)'
  ctx.lineWidth = 1
  for (let i = 0; i < canvas.width; i += 100) {
    ctx.beginPath()
    ctx.moveTo(i, 0)
    ctx.lineTo(i, canvas.height)
    ctx.stroke()
    ctx.beginPath()
    ctx.moveTo(0, i)
    ctx.lineTo(canvas.width, i)
    ctx.stroke()
  }

  // 绘制模拟人物轮廓
  const time = Date.now() / 1000
  const persons = [
    { x: 200 + Math.sin(time) * 30, y: 150 + Math.cos(time * 0.7) * 20 },
    { x: 400 + Math.cos(time * 0.5) * 40, y: 250 + Math.sin(time * 0.6) * 25 },
    { x: 550 + Math.sin(time * 0.8) * 25, y: 180 + Math.cos(time * 0.4) * 30 },
    { x: 100 + Math.cos(time * 0.6) * 20, y: 300 + Math.sin(time * 0.5) * 15 }
  ]

  persons.forEach((person, idx) => {
    ctx.fillStyle = `rgba(64, 158, 255, ${0.7 + Math.sin(time * 2 + idx) * 0.2})`
    ctx.beginPath()
    ctx.arc(person.x, person.y, 15, 0, Math.PI * 2)
    ctx.fill()
    ctx.fillStyle = 'white'
    ctx.font = '12px Arial'
    ctx.fillText(`Person ${idx + 1}`, person.x - 20, person.y - 20)
  })

  // 绘制边界框
  if (selectedEvent.value && selectedEvent.value.location) {
    ctx.strokeStyle = '#f56c6c'
    ctx.lineWidth = 3
    ctx.strokeRect(
        selectedEvent.value.location.x - 40,
        selectedEvent.value.location.y - 40,
        80,
        80
    )
    ctx.fillStyle = '#f56c6c'
    ctx.font = 'bold 12px Arial'
    ctx.fillText(selectedEvent.value.type, selectedEvent.value.location.x - 30, selectedEvent.value.location.y - 45)
  }

  animationFrameId = requestAnimationFrame(drawVideoFrame)
}

const initCanvas = () => {
  const canvas = videoCanvasRef.value
  const container = videoContainerRef.value
  if (canvas && container) {
    canvas.width = container.clientWidth
    canvas.height = 400
    drawVideoFrame()
  }
}

const playVideo = () => {
  if (!animationFrameId) {
    drawVideoFrame()
  }
}

const pauseVideo = () => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
    animationFrameId = null
  }
}

// ==================== 图表渲染 ====================
const renderTrendChart = () => {
  if (!trendChartRef.value) return

  if (trendChart) trendChart.dispose()
  trendChart = echarts.init(trendChartRef.value)

  const days = parseInt(trendPeriod.value)
  const dates = []
  const loiteringData = []
  const runningData = []
  const fightingData = []

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    dates.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }))

    loiteringData.push(Math.floor(Math.random() * 25) + 5)
    runningData.push(Math.floor(Math.random() * 15) + 3)
    fightingData.push(Math.floor(Math.random() * 8) + 1)
  }

  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Loitering', 'Running', 'Fighting'], bottom: 0 },
    grid: { left: '3%', right: '4%', top: '10%', bottom: '12%', containLabel: true },
    xAxis: { type: 'category', data: dates, axisLabel: { rotate: 45 } },
    yAxis: { type: 'value', name: 'Event Count' },
    series: [
      { name: 'Loitering', type: 'line', smooth: true, data: loiteringData, lineStyle: { color: '#e6a23c', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Running', type: 'line', smooth: true, data: runningData, lineStyle: { color: '#f56c6c', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Fighting', type: 'line', smooth: true, data: fightingData, lineStyle: { color: '#909399', width: 2 }, areaStyle: { opacity: 0.1 } }
    ]
  })
}

const renderDistributionChart = () => {
  if (!distributionChartRef.value) return

  if (distributionChart) distributionChart.dispose()
  distributionChart = echarts.init(distributionChartRef.value)

  const distribution: Record<string, number> = {}
  behaviorTypes.forEach(bt => { distribution[bt.type] = 0 })
  events.value.forEach(event => {
    if (distribution[event.type] !== undefined) distribution[event.type]++
  })

  distributionChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} events)' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '55%'],
      data: Object.entries(distribution).map(([name, value]) => ({ name, value })),
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })
}

const renderHeatmap = () => {
  if (!heatmapChartRef.value) return

  if (heatmapChart) heatmapChart.dispose()
  heatmapChart = echarts.init(heatmapChartRef.value)

  // 模拟热力图数据
  const hours = 24
  const zones = ['Entrance', 'Lobby', 'Corridor', 'Elevator', 'Parking', 'Cafeteria']
  const data: [number, number, number][] = []

  for (let i = 0; i < hours; i++) {
    for (let j = 0; j < zones.length; j++) {
      let value = 0
      if (i >= 8 && i <= 10) value = Math.floor(Math.random() * 50) + 30
      else if (i >= 12 && i <= 14) value = Math.floor(Math.random() * 60) + 40
      else if (i >= 17 && i <= 19) value = Math.floor(Math.random() * 55) + 35
      else value = Math.floor(Math.random() * 20)
      data.push([i, j, value])
    }
  }

  heatmapChart.setOption({
    tooltip: { position: 'top', formatter: (params: any) => {
        return `${zones[params.value[1]]}<br/>${params.value[0]}:00<br/>Activity: ${params.value[2]} events`
      } },
    xAxis: { type: 'category', data: Array.from({ length: 24 }, (_, i) => `${i}:00`), axisLabel: { rotate: 45 } },
    yAxis: { type: 'category', data: zones },
    visualMap: { min: 0, max: 80, calculable: true, orient: 'horizontal', left: 'center', bottom: 0,
      inRange: { color: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'] }
    },
    series: [{
      type: 'heatmap',
      data: data,
      label: { show: false },
      emphasis: { itemStyle: { shadowBlur: 10 } }
    }]
  })
}

// ==================== 交互事件 ====================
const refreshData = () => {
  events.value = generateMockEvents(25)
  updateStatsFromEvents()
  updateZoneActivity()
  renderDistributionChart()
  renderHeatmap()
  ElMessage.success('Data refreshed successfully')
}

const selectEvent = (event: BehaviorEvent) => {
  event.read = true
  selectedEvent.value = event
  if (event.location) {
    tooltipStyle.value = {
      left: `${event.location.x}px`,
      top: `${event.location.y - 60}px`,
      position: 'absolute'
    }
  }
  setTimeout(() => {
    selectedEvent.value = null
  }, 5000)
}

const reviewEvent = (event: BehaviorEvent) => {
  detailDialog.event = event
  detailDialog.visible = true
}

const markAsReviewed = (event: BehaviorEvent) => {
  event.reviewed = true
  ElMessage.success('Event marked as reviewed')
}

const exportEvent = (event: BehaviorEvent) => {
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

const exportReport = () => {
  const report = {
    generatedAt: new Date().toISOString(),
    summary: stats,
    events: events.value,
    zoneActivity: zoneActivity.value
  }
  const data = JSON.stringify(report, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `behavioral-report-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Report exported successfully')
}

// ==================== 数据加载 ====================
const loadData = () => {
  events.value = generateMockEvents(30)
  updateStatsFromEvents()
  updateZoneActivity()

  nextTick(() => {
    renderTrendChart()
    renderDistributionChart()
    renderHeatmap()
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
      initCanvas()
      updateTimestamp()
      setInterval(updateTimestamp, 1000)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
  }
  window.removeEventListener('resize', () => {
    trendChart?.resize()
    distributionChart?.resize()
    heatmapChart?.resize()
  })
})

// 监听窗口大小变化
watch(isLoaded, (loaded) => {
  if (loaded) {
    window.addEventListener('resize', () => {
      trendChart?.resize()
      distributionChart?.resize()
      heatmapChart?.resize()
      const canvas = videoCanvasRef.value
      const container = videoContainerRef.value
      if (canvas && container) {
        canvas.width = container.clientWidth
      }
    })
  }
})

watch(trendPeriod, () => renderTrendChart())
watch(heatmapPeriod, () => renderHeatmap())
watch(events, () => {
  updateZoneActivity()
  renderDistributionChart()
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
.behavioral-analytics-page {
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

.warning-bg { background-color: #fff3e0; color: #e6a23c; }
.danger-bg { background-color: #fef0f0; color: #f56c6c; }
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

/* Video Card */
.video-card, .events-card, .chart-card, .heatmap-card, .zone-card {
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

.live-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  background-color: #fef0f0;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  color: #f56c6c;
}

.live-dot {
  width: 8px;
  height: 8px;
  background-color: #f56c6c;
  border-radius: 50%;
  animation: pulse-red 1.5s infinite;
}

@keyframes pulse-red {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

.video-container {
  position: relative;
  background-color: #1a1a2e;
  border-radius: 8px;
  overflow: hidden;
}

.video-canvas {
  width: 100%;
  height: 400px;
  display: block;
}

.event-tooltip {
  position: absolute;
  background: rgba(0, 0, 0, 0.85);
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  pointer-events: none;
  z-index: 100;
  min-width: 160px;
}

.event-tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.video-controls {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.timestamp {
  font-size: 13px;
  color: #8c9aab;
  font-family: monospace;
}

.behavior-legend {
  display: flex;
  gap: 16px;
  margin-left: auto;
}

.legend-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 4px;
}

.legend-dot.running { background-color: #f56c6c; }
.legend-dot.loitering { background-color: #e6a23c; }
.legend-dot.fighting { background-color: #909399; }
.legend-dot.falling { background-color: #f56c6c; }

/* Events Feed */
.events-feed {
  max-height: 500px;
  overflow-y: auto;
}

.event-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background-color 0.2s;
}

.event-item:hover {
  background-color: #f5f7fa;
}

.event-item.unread {
  background-color: #ecf5ff;
}

.event-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.event-icon.warning { background-color: #fff3e0; color: #e6a23c; }
.event-icon.danger { background-color: #fef0f0; color: #f56c6c; }
.event-icon.info { background-color: #ecf5ff; color: #409eff; }

.event-content {
  flex: 1;
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
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

.event-desc {
  font-size: 12px;
  color: #5e6e82;
  margin-bottom: 4px;
}

.event-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: #8c9aab;
}

.event-meta .el-icon {
  font-size: 11px;
}

.confidence {
  color: #67c23a;
}

.no-events {
  padding: 40px 0;
}

/* Charts */
.charts-row {
  margin-bottom: 0;
}

.chart-container {
  height: 280px;
  width: 100%;
}

/* Heatmap */
.heatmap-container {
  height: 320px;
  width: 100%;
}

.heatmap-legend {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 12px;
  font-size: 12px;
  color: #8c9aab;
}

.gradient-bar {
  width: 200px;
  height: 8px;
  border-radius: 4px;
  background: linear-gradient(90deg, #3b82f6, #10b981, #f59e0b, #ef4444);
}

/* Zone Activity */
.zone-list {
  padding: 8px 0;
}

.zone-item {
  margin-bottom: 16px;
}

.zone-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 13px;
}

.zone-name {
  font-weight: 500;
  color: #1f2f3d;
}

.zone-count {
  color: #8c9aab;
}

/* Event Detail Dialog */
.event-detail {
  padding: 8px 0;
}

.detail-video-placeholder {
  height: 200px;
  background: linear-gradient(135deg, #1a1a2e, #16213e);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.image-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #8c9aab;
}

.detail-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
}

:deep(.el-progress-bar__outer) {
  background-color: #ebeef5;
}
</style>