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
        <div class="loading-tip">AI Video Analytics - Video Health Monitoring</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="video-health-monitoring-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Video Health Monitoring</h1>
        <p>Real-time monitoring of camera health, signal quality, and system performance</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
        <el-button @click="exportHealthReport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon primary-bg">
            <el-icon><Camera /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalCameras }}</div>
            <div class="stat-label">Total Cameras</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.onlineCameras }}</div>
            <div class="stat-label">Online</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon danger-bg">
            <el-icon><CircleClose /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.offlineCameras }}</div>
            <div class="stat-label">Offline</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.criticalIssues }}</div>
            <div class="stat-label">Critical Issues</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Overall Health Gauge & Signal Quality -->
    <el-row :gutter="20">
      <el-col :xs="24" :lg="12">
        <div class="health-card">
          <div class="card-header">
            <h3>Overall System Health</h3>
            <el-tag :type="getOverallHealthType(overallHealth)" size="large">
              {{ overallHealth }}% Healthy
            </el-tag>
          </div>
          <div ref="gaugeChartRef" class="gauge-container"></div>
          <div class="health-breakdown">
            <div class="health-item">
              <span>Excellent</span>
              <el-progress :percentage="healthBreakdown.excellent" :color="'#67c23a'" :stroke-width="8" />
            </div>
            <div class="health-item">
              <span>Good</span>
              <el-progress :percentage="healthBreakdown.good" :color="'#409eff'" :stroke-width="8" />
            </div>
            <div class="health-item">
              <span>Fair</span>
              <el-progress :percentage="healthBreakdown.fair" :color="'#e6a23c'" :stroke-width="8" />
            </div>
            <div class="health-item">
              <span>Poor</span>
              <el-progress :percentage="healthBreakdown.poor" :color="'#f56c6c'" :stroke-width="8" />
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="signal-card">
          <div class="card-header">
            <h3>Average Signal Quality by Location</h3>
          </div>
          <div ref="signalChartRef" class="signal-chart-container"></div>
        </div>
      </el-col>
    </el-row>

    <!-- Camera Health Table -->
    <div class="camera-table-wrapper">
      <div class="table-header">
        <h3>Camera Health Status</h3>
        <div class="table-filters">
          <el-select v-model="statusFilter" placeholder="Filter by Status" clearable style="width: 140px">
            <el-option label="All" value="" />
            <el-option label="Online" value="ONLINE" />
            <el-option label="Offline" value="OFFLINE" />
            <el-option label="Degraded" value="DEGRADED" />
          </el-select>
          <el-select v-model="locationFilter" placeholder="Filter by Location" clearable style="width: 160px">
            <el-option label="All Locations" value="" />
            <el-option v-for="loc in locations" :key="loc" :label="loc" :value="loc" />
          </el-select>
          <el-input
              v-model="searchFilter"
              placeholder="Search camera..."
              clearable
              style="width: 200px"
              :prefix-icon="Search"
          />
        </div>
      </div>
      <el-table :data="filteredCameras" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="name" label="Camera Name" min-width="180">
          <template #default="{ row }">
            <div class="camera-name-cell">
              <el-icon><VideoCamera /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="Location" width="160" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              <span class="status-dot" :class="getStatusDotClass(row.status)"></span>
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="signalQuality" label="Signal Quality" width="150">
          <template #default="{ row }">
            <el-progress
                :percentage="row.signalQuality"
                :color="getSignalQualityColor(row.signalQuality)"
                :stroke-width="8"
                :show-text="false"
            />
            <span class="signal-value">{{ row.signalQuality }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="fps" label="FPS" width="80">
          <template #default="{ row }">
            <span :class="{ degraded: row.fps < 15 }">{{ row.fps }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="latency" label="Latency (ms)" width="100">
          <template #default="{ row }">
            <span :class="{ degraded: row.latency > 200 }">{{ row.latency }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="lastHeartbeat" label="Last Heartbeat" width="160">
          <template #default="{ row }">
            {{ formatRelativeTime(row.lastHeartbeat) }}
          </template>
        </el-table-column>
        <el-table-column prop="uptime" label="Uptime" width="120">
          <template #default="{ row }">
            {{ row.uptime }}%
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewCameraDetails(row)">
              Details
            </el-button>
            <el-button link type="danger" size="small" @click="testConnection(row)">
              Test
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Issues & Alerts Section -->
    <el-row :gutter="20" class="issues-row">
      <el-col :xs="24" :lg="14">
        <div class="issues-card">
          <div class="card-header">
            <h3>Recent Issues & Alerts</h3>
            <el-button size="small" @click="clearAlerts">Clear All</el-button>
          </div>
          <div class="issues-list">
            <div
                v-for="alert in recentAlerts"
                :key="alert.id"
                class="issue-item"
                :class="alert.severity"
            >
              <div class="issue-icon">
                <el-icon><WarningFilled /></el-icon>
              </div>
              <div class="issue-content">
                <div class="issue-header">
                  <span class="issue-title">{{ alert.title }}</span>
                  <span class="issue-time">{{ formatRelativeTime(alert.timestamp) }}</span>
                </div>
                <div class="issue-description">{{ alert.description }}</div>
                <div class="issue-actions">
                  <el-button link size="small" @click="acknowledgeAlert(alert)">Acknowledge</el-button>
                  <el-button link size="small" type="primary" @click="resolveAlert(alert)">Resolve</el-button>
                </div>
              </div>
            </div>
            <div v-if="recentAlerts.length === 0" class="no-issues">
              <el-empty description="No active issues" />
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="10">
        <div class="trend-card">
          <div class="card-header">
            <h3>Health Trend (Last 7 Days)</h3>
            <el-select v-model="trendPeriod" size="small" style="width: 100px">
              <el-option label="7 Days" value="7" />
              <el-option label="14 Days" value="14" />
              <el-option label="30 Days" value="30" />
            </el-select>
          </div>
          <div ref="trendChartRef" class="trend-chart-container"></div>
        </div>
      </el-col>
    </el-row>

    <!-- Camera Detail Dialog -->
    <el-dialog v-model="detailDialog.visible" :title="detailDialog.camera?.name" width="600px">
      <div v-if="detailDialog.camera" class="camera-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Camera ID">{{ detailDialog.camera.id }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ detailDialog.camera.location }}</el-descriptions-item>
          <el-descriptions-item label="IP Address">{{ detailDialog.camera.ipAddress }}</el-descriptions-item>
          <el-descriptions-item label="Model">{{ detailDialog.camera.model }}</el-descriptions-item>
          <el-descriptions-item label="Firmware">{{ detailDialog.camera.firmware }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(detailDialog.camera.status)">{{ detailDialog.camera.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Signal Quality">
            <el-progress :percentage="detailDialog.camera.signalQuality" :stroke-width="10" />
          </el-descriptions-item>
          <el-descriptions-item label="Uptime">{{ detailDialog.camera.uptime }}%</el-descriptions-item>
          <el-descriptions-item label="FPS">{{ detailDialog.camera.fps }}</el-descriptions-item>
          <el-descriptions-item label="Latency">{{ detailDialog.camera.latency }}ms</el-descriptions-item>
          <el-descriptions-item label="Resolution">{{ detailDialog.camera.resolution }}</el-descriptions-item>
          <el-descriptions-item label="Bandwidth">{{ detailDialog.camera.bandwidth }} Mbps</el-descriptions-item>
          <el-descriptions-item label="Packet Loss">{{ detailDialog.camera.packetLoss }}%</el-descriptions-item>
          <el-descriptions-item label="Jitter">{{ detailDialog.camera.jitter }}ms</el-descriptions-item>
          <el-descriptions-item label="Last Heartbeat" :span="2">{{ formatFullTimestamp(detailDialog.camera.lastHeartbeat) }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- Test Connection Result -->
    <el-dialog v-model="testDialog.visible" title="Connection Test" width="400px">
      <div v-if="testDialog.result" class="test-result">
        <div class="test-icon" :class="testDialog.result.success ? 'success' : 'danger'">
          <el-icon v-if="testDialog.result.success"><CircleCheck /></el-icon>
          <el-icon v-else><CircleClose /></el-icon>
        </div>
        <div class="test-message">{{ testDialog.result.message }}</div>
        <div class="test-details" v-if="testDialog.result.details">
          <el-descriptions :column="1" size="small">
            <el-descriptions-item label="Response Time">{{ testDialog.result.details.responseTime }}ms</el-descriptions-item>
            <el-descriptions-item label="Packet Loss">{{ testDialog.result.details.packetLoss }}%</el-descriptions-item>
            <el-descriptions-item label="Test Time">{{ testDialog.result.details.timestamp }}</el-descriptions-item>
          </el-descriptions>
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
  Camera,
  CircleCheck,
  CircleClose,
  Warning,
  VideoCamera,
  Search,
  WarningFilled
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Checking camera status...',
  'Analyzing signal quality...',
  'Almost ready...'
]

// ==================== Type Definitions ====================
interface CameraHealth {
  id: string
  name: string
  location: string
  status: 'ONLINE' | 'OFFLINE' | 'DEGRADED'
  signalQuality: number
  fps: number
  latency: number
  uptime: number
  lastHeartbeat: Date
  ipAddress: string
  model: string
  firmware: string
  resolution: string
  bandwidth: number
  packetLoss: number
  jitter: number
}

interface Alert {
  id: string
  title: string
  description: string
  severity: 'critical' | 'warning' | 'info'
  timestamp: Date
  acknowledged: boolean
  resolved: boolean
}

// ==================== 模拟数据生成 ====================
const locations = ['Building A', 'Building B', 'Building C', 'Parking', 'Data Center', 'Cafeteria', 'Lobby', 'Corridors']

const generateMockCameras = (): CameraHealth[] => {
  const cameras: CameraHealth[] = []
  const statuses: ('ONLINE' | 'OFFLINE' | 'DEGRADED')[] = ['ONLINE', 'ONLINE', 'ONLINE', 'ONLINE', 'ONLINE', 'OFFLINE', 'DEGRADED']

  for (let i = 1; i <= 48; i++) {
    const status = statuses[Math.floor(Math.random() * statuses.length)]
    const signalQuality = status === 'ONLINE'
        ? 85 + Math.random() * 14
        : status === 'DEGRADED'
            ? 40 + Math.random() * 35
            : 0
    const uptime = status === 'ONLINE'
        ? 95 + Math.random() * 5
        : status === 'DEGRADED'
            ? 70 + Math.random() * 20
            : Math.random() * 50

    cameras.push({
      id: `CAM-${String(i).padStart(3, '0')}`,
      name: `Camera ${i}`,
      location: locations[Math.floor(Math.random() * locations.length)],
      status: status,
      signalQuality: Math.floor(signalQuality),
      fps: status === 'ONLINE' ? 25 + Math.floor(Math.random() * 5) : status === 'DEGRADED' ? 10 + Math.floor(Math.random() * 10) : 0,
      latency: status === 'ONLINE' ? 30 + Math.floor(Math.random() * 70) : status === 'DEGRADED' ? 150 + Math.floor(Math.random() * 150) : 999,
      uptime: Math.floor(uptime),
      lastHeartbeat: new Date(Date.now() - (status === 'OFFLINE' ? Math.random() * 3600000 : Math.random() * 60000)),
      ipAddress: `192.168.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
      model: ['Hikvision DS-2CD', 'Dahua IPC-HFW', 'Axis P1447', 'Sony SNC-VB770'][Math.floor(Math.random() * 4)],
      firmware: `v${Math.floor(Math.random() * 5) + 1}.${Math.floor(Math.random() * 10)}.${Math.floor(Math.random() * 10)}`,
      resolution: ['1920x1080', '2560x1440', '1280x720', '3840x2160'][Math.floor(Math.random() * 4)],
      bandwidth: Number((1 + Math.random() * 8).toFixed(1)),
      packetLoss: status === 'ONLINE' ? Number((Math.random() * 0.5).toFixed(2)) : status === 'DEGRADED' ? Number((Math.random() * 5).toFixed(2)) : 100,
      jitter: status === 'ONLINE' ? Math.floor(Math.random() * 10) : Math.floor(Math.random() * 50) + 20
    })
  }

  return cameras
}

const generateMockAlerts = (cameras: CameraHealth[]): Alert[] => {
  const alerts: Alert[] = []
  const now = new Date()

  const offlineCameras = cameras.filter(c => c.status === 'OFFLINE')
  const degradedCameras = cameras.filter(c => c.status === 'DEGRADED')

  offlineCameras.forEach(cam => {
    alerts.push({
      id: `ALT-${Math.random().toString(36).substr(2, 8)}`,
      title: `Camera Offline: ${cam.name}`,
      description: `Camera ${cam.name} at ${cam.location} has lost connection. Last heartbeat received ${formatRelativeTimeForAlert(cam.lastHeartbeat)}.`,
      severity: 'critical',
      timestamp: new Date(now.getTime() - Math.random() * 3600000),
      acknowledged: false,
      resolved: false
    })
  })

  degradedCameras.slice(0, 5).forEach(cam => {
    alerts.push({
      id: `ALT-${Math.random().toString(36).substr(2, 8)}`,
      title: `Signal Degradation: ${cam.name}`,
      description: `Camera ${cam.name} at ${cam.location} is experiencing poor signal quality (${cam.signalQuality}%). FPS: ${cam.fps}, Latency: ${cam.latency}ms.`,
      severity: 'warning',
      timestamp: new Date(now.getTime() - Math.random() * 7200000),
      acknowledged: false,
      resolved: false
    })
  })

  // Add some additional random alerts
  if (Math.random() > 0.5) {
    alerts.push({
      id: `ALT-${Math.random().toString(36).substr(2, 8)}`,
      title: 'High Network Latency Detected',
      description: 'Network latency spike detected affecting multiple cameras in Building A.',
      severity: 'warning',
      timestamp: new Date(now.getTime() - Math.random() * 1800000),
      acknowledged: false,
      resolved: false
    })
  }

  return alerts.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
}

const formatRelativeTimeForAlert = (date: Date): string => {
  const diffMs = Date.now() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  if (diffMins < 60) return `${diffMins} minutes ago`
  return `${Math.floor(diffMins / 60)} hours ago`
}

// ==================== 响应式状态 ====================
const allCameras = ref<CameraHealth[]>([])
const allAlerts = ref<Alert[]>([])
const statusFilter = ref('')
const locationFilter = ref('')
const searchFilter = ref('')
const trendPeriod = ref('7')

const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

const stats = reactive({
  totalCameras: 0,
  onlineCameras: 0,
  offlineCameras: 0,
  criticalIssues: 0
})

const overallHealth = ref(92.5)
const healthBreakdown = reactive({
  excellent: 65,
  good: 20,
  fair: 10,
  poor: 5
})

const recentAlerts = computed(() => allAlerts.value.filter(a => !a.resolved).slice(0, 8))

const detailDialog = reactive({
  visible: false,
  camera: null as CameraHealth | null
})

const testDialog = reactive({
  visible: false,
  result: null as { success: boolean; message: string; details?: any } | null
})

let gaugeChart: echarts.ECharts | null = null
let signalChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null

const gaugeChartRef = ref<HTMLElement | null>(null)
const signalChartRef = ref<HTMLElement | null>(null)
const trendChartRef = ref<HTMLElement | null>(null)

// ==================== 计算属性 ====================
const filteredCameras = computed(() => {
  let filtered = [...allCameras.value]

  if (statusFilter.value) {
    filtered = filtered.filter(c => c.status === statusFilter.value)
  }

  if (locationFilter.value) {
    filtered = filtered.filter(c => c.location === locationFilter.value)
  }

  if (searchFilter.value) {
    const searchLower = searchFilter.value.toLowerCase()
    filtered = filtered.filter(c =>
        c.name.toLowerCase().includes(searchLower) ||
        c.id.toLowerCase().includes(searchLower)
    )
  }

  pagination.total = filtered.length

  const start = (pagination.currentPage - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// ==================== 辅助函数 ====================
const formatRelativeTime = (date: Date) => {
  const diffMs = Date.now() - date.getTime()
  const diffSecs = Math.floor(diffMs / 1000)
  const diffMins = Math.floor(diffSecs / 60)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffSecs < 60) return 'Just now'
  if (diffMins < 60) return `${diffMins} min ago`
  if (diffHours < 24) return `${diffHours} hr ago`
  return `${diffDays} days ago`
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

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    'ONLINE': 'success',
    'OFFLINE': 'danger',
    'DEGRADED': 'warning'
  }
  return map[status] || 'info'
}

const getStatusDotClass = (status: string) => {
  const map: Record<string, string> = {
    'ONLINE': 'dot-online',
    'OFFLINE': 'dot-offline',
    'DEGRADED': 'dot-degraded'
  }
  return map[status] || 'dot-online'
}

const getSignalQualityColor = (quality: number) => {
  if (quality >= 80) return '#67c23a'
  if (quality >= 60) return '#409eff'
  if (quality >= 30) return '#e6a23c'
  return '#f56c6c'
}

const getOverallHealthType = (health: number) => {
  if (health >= 90) return 'success'
  if (health >= 70) return 'warning'
  return 'danger'
}

const updateStats = () => {
  stats.totalCameras = allCameras.value.length
  stats.onlineCameras = allCameras.value.filter(c => c.status === 'ONLINE').length
  stats.offlineCameras = allCameras.value.filter(c => c.status === 'OFFLINE').length
  stats.criticalIssues = allAlerts.value.filter(a => a.severity === 'critical' && !a.resolved).length

  // Calculate overall health
  const avgSignal = allCameras.value.reduce((sum, c) => sum + c.signalQuality, 0) / allCameras.value.length
  const onlineRatio = stats.onlineCameras / stats.totalCameras
  overallHealth.value = Math.floor((avgSignal * 0.6 + onlineRatio * 100 * 0.4))

  // Update breakdown
  const excellentCount = allCameras.value.filter(c => c.signalQuality >= 85 && c.status === 'ONLINE').length
  const goodCount = allCameras.value.filter(c => c.signalQuality >= 70 && c.signalQuality < 85 && c.status === 'ONLINE').length
  const fairCount = allCameras.value.filter(c => (c.signalQuality >= 50 && c.signalQuality < 70) || c.status === 'DEGRADED').length
  const poorCount = allCameras.value.filter(c => c.signalQuality < 50 || c.status === 'OFFLINE').length

  healthBreakdown.excellent = Math.floor((excellentCount / stats.totalCameras) * 100)
  healthBreakdown.good = Math.floor((goodCount / stats.totalCameras) * 100)
  healthBreakdown.fair = Math.floor((fairCount / stats.totalCameras) * 100)
  healthBreakdown.poor = 100 - healthBreakdown.excellent - healthBreakdown.good - healthBreakdown.fair
}

// ==================== 图表渲染 ====================
const renderGaugeChart = () => {
  if (!gaugeChartRef.value) return
  if (gaugeChart) gaugeChart.dispose()

  gaugeChart = echarts.init(gaugeChartRef.value)
  gaugeChart.setOption({
    series: [{
      type: 'gauge',
      center: ['50%', '55%'],
      radius: '80%',
      startAngle: 210,
      endAngle: -30,
      min: 0,
      max: 100,
      splitNumber: 5,
      progress: { show: true, width: 18, itemStyle: { color: '#409eff' } },
      axisLine: { lineStyle: { width: 18, color: [[0.7, '#f56c6c'],[0.85, '#e6a23c'],[1, '#67c23a']] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      pointer: { show: false },
      detail: { show: false },
      title: { show: false },
      data: [{ value: overallHealth.value, name: 'Health' }]
    }]
  })
}

const renderSignalChart = () => {
  if (!signalChartRef.value) return
  if (signalChart) signalChart.dispose()

  signalChart = echarts.init(signalChartRef.value)

  const locationStats: Record<string, { sum: number; count: number }> = {}
  allCameras.value.forEach(cam => {
    if (!locationStats[cam.location]) {
      locationStats[cam.location] = { sum: 0, count: 0 }
    }
    locationStats[cam.location].sum += cam.signalQuality
    locationStats[cam.location].count++
  })

  const locations_data = Object.keys(locationStats)
  const avgSignals = locations_data.map(loc => (locationStats[loc].sum / locationStats[loc].count).toFixed(0))

  signalChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', top: '5%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value', name: 'Signal Quality (%)', max: 100 },
    yAxis: { type: 'category', data: locations_data, axisLabel: { fontSize: 11 } },
    series: [{
      type: 'bar',
      data: avgSignals,
      itemStyle: {
        color: (params: any) => getSignalQualityColor(parseFloat(params.data)),
        borderRadius: [0, 4, 4, 0]
      }
    }]
  })
}

const renderTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)

  const days = parseInt(trendPeriod.value)
  const dates = []
  const healthData = []
  const onlineData = []

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    dates.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }))

    healthData.push(85 + Math.random() * 10 - (i === days - 1 ? 0 : Math.random() * 5))
    onlineData.push(92 + Math.random() * 6 - (i === days - 1 ? 0 : Math.random() * 3))
  }

  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Overall Health', 'Online Rate'], bottom: 0 },
    grid: { left: '3%', right: '4%', top: '10%', bottom: '12%', containLabel: true },
    xAxis: { type: 'category', data: dates, axisLabel: { rotate: 45 } },
    yAxis: { type: 'value', name: 'Percentage (%)', min: 70, max: 100 },
    series: [
      { name: 'Overall Health', type: 'line', smooth: true, data: healthData, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Online Rate', type: 'line', smooth: true, data: onlineData, lineStyle: { color: '#67c23a', width: 2 }, areaStyle: { opacity: 0.1 } }
    ]
  })
}

// ==================== 交互事件 ====================
const refreshData = () => {
  tableLoading.value = true
  setTimeout(() => {
    allCameras.value = generateMockCameras()
    allAlerts.value = generateMockAlerts(allCameras.value)
    updateStats()
    renderGaugeChart()
    renderSignalChart()
    renderTrendChart()
    tableLoading.value = false
    ElMessage.success('Health data refreshed')
  }, 500)
}

const viewCameraDetails = (camera: CameraHealth) => {
  detailDialog.camera = camera
  detailDialog.visible = true
}

const testConnection = (camera: CameraHealth) => {
  // Simulate connection test
  const success = Math.random() > 0.3
  testDialog.result = {
    success: success,
    message: success ? `Successfully connected to ${camera.name}` : `Failed to connect to ${camera.name}`,
    details: success ? {
      responseTime: Math.floor(Math.random() * 100) + 20,
      packetLoss: (Math.random() * 2).toFixed(2),
      timestamp: new Date().toLocaleString()
    } : null
  }
  testDialog.visible = true

  if (!success) {
    ElMessage.warning(`Connection test failed for ${camera.name}`)
  }
}

const acknowledgeAlert = (alert: Alert) => {
  alert.acknowledged = true
  ElMessage.info(`Alert acknowledged: ${alert.title}`)
}

const resolveAlert = (alert: Alert) => {
  alert.resolved = true
  ElMessage.success(`Alert resolved: ${alert.title}`)
}

const clearAlerts = () => {
  allAlerts.value = allAlerts.value.filter(a => !a.resolved).map(a => ({ ...a, resolved: true }))
  ElMessage.success('All alerts cleared')
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.currentPage = 1
}

const handleCurrentChange = (page: number) => {
  pagination.currentPage = page
}

const exportHealthReport = () => {
  const report = {
    generatedAt: new Date().toISOString(),
    summary: stats,
    overallHealth: overallHealth.value,
    cameras: allCameras.value,
    alerts: allAlerts.value
  }
  const data = JSON.stringify(report, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `video-health-report-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Health report exported')
}

// ==================== 数据加载 ====================
const loadData = () => {
  allCameras.value = generateMockCameras()
  allAlerts.value = generateMockAlerts(allCameras.value)
  updateStats()

  nextTick(() => {
    renderGaugeChart()
    renderSignalChart()
    renderTrendChart()
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
  window.removeEventListener('resize', () => {
    gaugeChart?.resize()
    signalChart?.resize()
    trendChart?.resize()
  })
})

watch(isLoaded, (loaded) => {
  if (loaded) {
    window.addEventListener('resize', () => {
      gaugeChart?.resize()
      signalChart?.resize()
      trendChart?.resize()
    })
  }
})

watch(trendPeriod, () => renderTrendChart())
watch([statusFilter, locationFilter, searchFilter], () => {
  pagination.currentPage = 1
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
.video-health-monitoring-page {
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

.primary-bg { background-color: #ecf5ff; color: #409eff; }
.success-bg { background-color: #f0f9eb; color: #67c23a; }
.danger-bg { background-color: #fef0f0; color: #f56c6c; }
.warning-bg { background-color: #fff3e0; color: #e6a23c; }

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

/* Health Cards */
.health-card, .signal-card, .issues-card, .trend-card, .camera-table-wrapper {
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

.gauge-container {
  height: 240px;
  width: 100%;
}

.signal-chart-container {
  height: 300px;
  width: 100%;
}

.trend-chart-container {
  height: 280px;
  width: 100%;
}

.health-breakdown {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.health-item {
  margin-bottom: 12px;
}

.health-item span {
  display: block;
  margin-bottom: 4px;
  font-size: 13px;
  color: #5e6e82;
}

/* Camera Table */
.camera-table-wrapper {
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.table-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

.table-filters {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.camera-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.signal-value {
  margin-left: 8px;
  font-size: 12px;
  color: #5e6e82;
}

.degraded {
  color: #e6a23c;
}

.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}

.dot-online { background-color: #67c23a; box-shadow: 0 0 0 2px rgba(103, 194, 58, 0.2); }
.dot-offline { background-color: #f56c6c; box-shadow: 0 0 0 2px rgba(245, 108, 108, 0.2); }
.dot-degraded { background-color: #e6a23c; box-shadow: 0 0 0 2px rgba(230, 162, 60, 0.2); }

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding-top: 16px;
  margin-top: 16px;
  border-top: 1px solid #ebeef5;
}

/* Issues List */
.issues-list {
  max-height: 320px;
  overflow-y: auto;
}

.issue-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
  transition: background-color 0.2s;
}

.issue-item:hover {
  background-color: #f5f7fa;
}

.issue-item.critical .issue-icon { color: #f56c6c; }
.issue-item.warning .issue-icon { color: #e6a23c; }
.issue-item.info .issue-icon { color: #409eff; }

.issue-icon {
  font-size: 20px;
}

.issue-content {
  flex: 1;
}

.issue-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.issue-title {
  font-weight: 600;
  font-size: 14px;
  color: #1f2f3d;
}

.issue-time {
  font-size: 11px;
  color: #8c9aab;
}

.issue-description {
  font-size: 12px;
  color: #5e6e82;
  margin-bottom: 8px;
}

.issue-actions {
  display: flex;
  gap: 12px;
}

.no-issues {
  padding: 40px 0;
}

/* Test Result Dialog */
.test-result {
  text-align: center;
  padding: 20px;
}

.test-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.test-icon.success { color: #67c23a; }
.test-icon.danger { color: #f56c6c; }

.test-message {
  font-size: 16px;
  margin-bottom: 20px;
}

.test-details {
  text-align: left;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

/* Camera Detail */
.camera-detail {
  padding: 8px 0;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
}

:deep(.el-progress__text) {
  font-size: 11px !important;
}
</style>