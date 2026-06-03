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
        <div class="loading-tip">Recording Status Monitoring</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="recording-status-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Recording Status</h2>
        <p class="header-subtitle">Real-time Recording Monitoring | Storage Health</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- System Overview Cards -->
    <el-row :gutter="20" class="overview-row">
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon total">
            <el-icon :size="28"><Camera /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Total Cameras</div>
            <div class="overview-value">{{ stats.totalCameras }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon recording">
            <el-icon :size="28"><VideoCamera /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Recording</div>
            <div class="overview-value">{{ stats.recording }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon stopped">
            <el-icon :size="28"><VideoPause /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Stopped / Fault</div>
            <div class="overview-value" :class="{ 'has-warning': stats.stopped > 0 }">{{ stats.stopped }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon storage">
            <el-icon :size="28"><Coin /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Total Storage Used</div>
            <div class="overview-value">{{ stats.totalStorageUsed }} <span class="unit">TB</span></div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Recording Health Status -->
    <el-row :gutter="20" class="health-row">
      <el-col :span="24">
        <el-card shadow="hover" class="health-card">
          <template #header>
            <div class="card-header">
              <span>Recording Health Status</span>
              <el-tag :type="getOverallHealthType" size="large">{{ getOverallHealthText }}</el-tag>
            </div>
          </template>
          <div class="health-metrics">
            <div class="health-item">
              <div class="health-label">Recording Success Rate</div>
              <el-progress :percentage="healthMetrics.successRate" :color="getRateColor(healthMetrics.successRate)" :stroke-width="12" />
              <span class="health-value">{{ healthMetrics.successRate }}%</span>
            </div>
            <div class="health-item">
              <div class="health-label">Storage Health</div>
              <el-progress :percentage="healthMetrics.storageHealth" :color="getHealthColor(healthMetrics.storageHealth)" :stroke-width="12" />
              <span class="health-value">{{ healthMetrics.storageHealth }}%</span>
            </div>
            <div class="health-item">
              <div class="health-label">Video Integrity</div>
              <el-progress :percentage="healthMetrics.videoIntegrity" :color="getHealthColor(healthMetrics.videoIntegrity)" :stroke-width="12" />
              <span class="health-value">{{ healthMetrics.videoIntegrity }}%</span>
            </div>
            <div class="health-item">
              <div class="health-label">Archive Completion</div>
              <el-progress :percentage="healthMetrics.archiveCompletion" :color="getHealthColor(healthMetrics.archiveCompletion)" :stroke-width="12" />
              <span class="health-value">{{ healthMetrics.archiveCompletion }}%</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Camera Recording Status Table -->
    <el-card shadow="hover" class="table-card">
      <template #header>
        <div class="card-header">
          <span>Camera Recording Status</span>
          <div class="filter-group">
            <el-select v-model="statusFilter" size="small" style="width: 130px" placeholder="Status" clearable>
              <el-option label="All" value="all" />
              <el-option label="Recording" value="recording" />
              <el-option label="Stopped" value="stopped" />
              <el-option label="Fault" value="fault" />
              <el-option label="Scheduled" value="scheduled" />
            </el-select>
            <el-select v-model="nvrFilter" size="small" style="width: 150px" placeholder="NVR" clearable>
              <el-option label="All NVRs" value="all" />
              <el-option v-for="nvr in nvrList" :key="nvr" :label="nvr" :value="nvr" />
            </el-select>
            <el-input v-model="searchText" placeholder="Search camera..." style="width: 180px" clearable>
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
        </div>
      </template>
      <el-table :data="paginatedCameras" stripe border style="width: 100%">
        <el-table-column prop="name" label="Camera Name" min-width="160" />
        <el-table-column prop="nvrName" label="NVR" min-width="140" />
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">
              <el-icon v-if="row.status === 'recording'"><VideoCamera /></el-icon>
              <el-icon v-else-if="row.status === 'stopped'"><VideoPause /></el-icon>
              <el-icon v-else><WarningFilled /></el-icon>
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="recordingType" label="Recording Type" width="120">
          <template #default="{ row }">
            <el-tag :type="getRecordingTypeTag(row.recordingType)" size="small">{{ row.recordingType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="schedule" label="Schedule" min-width="180" />
        <el-table-column prop="storageUsed" label="Storage Used" width="120" sortable>
          <template #default="{ row }">{{ row.storageUsed }} GB</template>
        </el-table-column>
        <el-table-column prop="retentionDays" label="Retention (days)" width="110" sortable />
        <el-table-column prop="lastRecorded" label="Last Recorded" width="160" sortable />
        <el-table-column prop="health" label="Health" width="130">
          <template #default="{ row }">
            <el-progress :percentage="row.health" :color="getHealthColor(row.health)" :stroke-width="6" />
          </template>
        </el-table-column>
        <el-table-column label="Actions" fixed="right" width="120">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetails(row)">
              Details
            </el-button>
            <el-button v-if="row.status !== 'recording'" type="success" link size="small" @click="startRecording(row)">
              Start
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredCameras.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Recording Schedule by NVR -->
    <el-row :gutter="20" class="schedule-row">
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="schedule-card">
          <template #header>
            <div class="card-header">
              <span>Recording Schedule - Main NVR-01</span>
              <el-button type="primary" link @click="editSchedule">Edit Schedule</el-button>
            </div>
          </template>
          <el-table :data="scheduleData" stripe border size="small">
            <el-table-column prop="timeSlot" label="Time Slot" width="100" />
            <el-table-column prop="weekday" label="Weekday" />
            <el-table-column prop="weekend" label="Weekend" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="storage-card">
          <template #header>
            <div class="card-header">
              <span>Storage Usage by NVR</span>
            </div>
          </template>
          <div ref="storageChartRef" class="chart-container-small"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Recording Trend Chart -->
    <el-card shadow="hover" class="trend-card">
      <template #header>
        <div class="card-header">
          <span>Recording Activity Trend (Last 7 Days)</span>
          <el-radio-group v-model="trendType" size="small">
            <el-radio-button label="hours">By Hour</el-radio-button>
            <el-radio-button label="days">By Day</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <div ref="trendChartRef" class="chart-container"></div>
    </el-card>

    <!-- Failed Recordings List -->
    <el-card shadow="hover" class="failed-card" v-if="failedRecordings.length > 0">
      <template #header>
        <div class="card-header">
          <span class="failed-title">
            <el-icon><WarningFilled /></el-icon>
            Failed Recordings / Alerts
          </span>
          <el-badge :value="failedRecordings.length" type="danger" />
        </div>
      </template>
      <el-table :data="failedRecordings" stripe border size="small">
        <el-table-column prop="time" label="Time" width="160" />
        <el-table-column prop="cameraName" label="Camera" min-width="160" />
        <el-table-column prop="nvrName" label="NVR" width="140" />
        <el-table-column prop="errorType" label="Error Type" width="140">
          <template #default="{ row }">
            <el-tag type="danger" size="small">{{ row.errorType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="Message" min-width="200" />
        <el-table-column label="Action" width="100">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="retryRecording(row)">Retry</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Camera Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Recording Details - ${selectedCamera?.name}`" width="600px">
      <el-descriptions :column="2" border v-if="selectedCamera">
        <el-descriptions-item label="Camera Name">{{ selectedCamera.name }}</el-descriptions-item>
        <el-descriptions-item label="NVR">{{ selectedCamera.nvrName }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusTag(selectedCamera.status)">{{ getStatusText(selectedCamera.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Recording Type">{{ selectedCamera.recordingType }}</el-descriptions-item>
        <el-descriptions-item label="Schedule">{{ selectedCamera.schedule }}</el-descriptions-item>
        <el-descriptions-item label="Storage Used">{{ selectedCamera.storageUsed }} GB</el-descriptions-item>
        <el-descriptions-item label="Retention Period">{{ selectedCamera.retentionDays }} days</el-descriptions-item>
        <el-descriptions-item label="Resolution">{{ selectedCamera.resolution }}</el-descriptions-item>
        <el-descriptions-item label="Frame Rate">{{ selectedCamera.frameRate }} fps</el-descriptions-item>
        <el-descriptions-item label="Bitrate">{{ selectedCamera.bitrate }} Mbps</el-descriptions-item>
        <el-descriptions-item label="Last Recorded">{{ selectedCamera.lastRecorded }}</el-descriptions-item>
        <el-descriptions-item label="Recording Start">{{ selectedCamera.recordingStart }}</el-descriptions-item>
        <el-descriptions-item label="Health">{{ selectedCamera.health }}%</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Download,
  Refresh,
  Camera,
  VideoCamera,
  VideoPause,
  WarningFilled,
  Coin,
  Search
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Checking recording status...',
  'Analyzing storage usage...',
  'Almost ready...'
]

// ==================== Data State ====================
const statusFilter = ref('all')
const nvrFilter = ref('all')
const searchText = ref('')
const trendType = ref('days')

interface CameraRecording {
  id: number
  name: string
  nvrName: string
  status: 'recording' | 'stopped' | 'fault' | 'scheduled'
  recordingType: 'Continuous' | 'Motion' | 'Schedule' | 'Event'
  schedule: string
  storageUsed: number
  retentionDays: number
  lastRecorded: string
  recordingStart: string
  health: number
  resolution: string
  frameRate: number
  bitrate: number
}

interface FailedRecording {
  id: number
  time: string
  cameraName: string
  nvrName: string
  errorType: string
  message: string
}

const cameras = ref<CameraRecording[]>([])
const failedRecordings = ref<FailedRecording[]>([])
const nvrList = ref<string[]>([])

const scheduleData = ref([
  { timeSlot: '00:00 - 08:00', weekday: 'Motion Detection', weekend: 'Motion Detection' },
  { timeSlot: '08:00 - 18:00', weekday: 'Continuous', weekend: 'Motion Detection' },
  { timeSlot: '18:00 - 00:00', weekday: 'Continuous', weekend: 'Motion Detection' }
])

const healthMetrics = ref({
  successRate: 98.5,
  storageHealth: 87,
  videoIntegrity: 96,
  archiveCompletion: 94
})

const stats = computed(() => ({
  totalCameras: cameras.value.length,
  recording: cameras.value.filter(c => c.status === 'recording').length,
  stopped: cameras.value.filter(c => c.status === 'stopped' || c.status === 'fault').length,
  totalStorageUsed: cameras.value.reduce((sum, c) => sum + c.storageUsed, 0) / 1024
}))

const getOverallHealthType = computed(() => {
  const avg = (healthMetrics.value.successRate + healthMetrics.value.storageHealth + healthMetrics.value.videoIntegrity) / 3
  if (avg >= 90) return 'success'
  if (avg >= 75) return 'warning'
  return 'danger'
})

const getOverallHealthText = computed(() => {
  const avg = (healthMetrics.value.successRate + healthMetrics.value.storageHealth + healthMetrics.value.videoIntegrity) / 3
  if (avg >= 90) return 'Excellent'
  if (avg >= 75) return 'Fair'
  return 'Poor'
})

const filteredCameras = computed(() => {
  let filtered = cameras.value
  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(c => c.status === statusFilter.value)
  }
  if (nvrFilter.value !== 'all') {
    filtered = filtered.filter(c => c.nvrName === nvrFilter.value)
  }
  if (searchText.value) {
    filtered = filtered.filter(c =>
        c.name.toLowerCase().includes(searchText.value.toLowerCase()) ||
        c.nvrName.toLowerCase().includes(searchText.value.toLowerCase())
    )
  }
  return filtered
})

const pagination = ref({ currentPage: 1, pageSize: 15 })
const paginatedCameras = computed(() => {
  const start = (pagination.value.currentPage - 1) * pagination.value.pageSize
  return filteredCameras.value.slice(start, start + pagination.value.pageSize)
})

// Generate mock camera data
const generateCameras = (): CameraRecording[] => {
  const nvrs = ['Main NVR-01', 'Main NVR-02', 'Building B NVR', 'Parking NVR']
  const locations = [
    'Entrance', 'Exit', 'Lobby', 'Corridor E1', 'Corridor E2', 'Corridor W1', 'Corridor W2',
    'Meeting Room 1', 'Meeting Room 2', 'Office 101', 'Office 102', 'Office 103',
    'Server Room', 'Storage', 'Parking Level 1', 'Parking Level 2', 'Elevator Lobby'
  ]

  nvrList.value = nvrs

  const camerasList: CameraRecording[] = []
  let id = 1

  nvrs.forEach(nvr => {
    const numCameras = nvr === 'Main NVR-01' ? 32 : (nvr === 'Main NVR-02' ? 28 : (nvr === 'Building B NVR' ? 48 : 16))
    for (let i = 1; i <= numCameras; i++) {
      const statuses: ('recording' | 'stopped' | 'fault' | 'scheduled')[] =
          ['recording', 'recording', 'recording', 'recording', 'recording', 'stopped', 'recording', 'recording', 'fault', 'scheduled']
      const status = statuses[Math.floor(Math.random() * statuses.length)]
      const recordingTypes = ['Continuous', 'Motion', 'Schedule', 'Event']
      const recordingType = recordingTypes[Math.floor(Math.random() * recordingTypes.length)]
      const health = status === 'fault' ? Math.floor(40 + Math.random() * 30) : Math.floor(75 + Math.random() * 25)

      camerasList.push({
        id: id++,
        name: `${nvr.split(' ')[0]} ${locations[i % locations.length]} ${Math.floor(i / locations.length) + 1}`,
        nvrName: nvr,
        status: status,
        recordingType: recordingType as any,
        schedule: recordingType === 'Continuous' ? '24/7' : (recordingType === 'Motion' ? 'Motion Activated' : '08:00-20:00 Weekdays'),
        storageUsed: parseFloat((Math.random() * 200 + 50).toFixed(1)),
        retentionDays: Math.floor(14 + Math.random() * 21),
        lastRecorded: new Date(Date.now() - Math.random() * 60 * 60 * 1000).toLocaleString(),
        recordingStart: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toLocaleString(),
        health: health,
        resolution: ['1920x1080', '2560x1440', '3840x2160'][Math.floor(Math.random() * 3)],
        frameRate: [15, 25, 30][Math.floor(Math.random() * 3)],
        bitrate: parseFloat((2 + Math.random() * 8).toFixed(1))
      })
    }
  })

  return camerasList
}

// Generate failed recordings
const generateFailedRecordings = (): FailedRecording[] => {
  const failed = cameras.value.filter(c => c.status === 'fault' || c.status === 'stopped').slice(0, 5)
  const errorTypes = ['Storage Full', 'Network Error', 'Camera Offline', 'Recording Failed', 'Schedule Mismatch']

  return failed.map((c, idx) => ({
    id: idx + 1,
    time: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toLocaleString(),
    cameraName: c.name,
    nvrName: c.nvrName,
    errorType: errorTypes[Math.floor(Math.random() * errorTypes.length)],
    message: `Recording ${errorTypes[Math.floor(Math.random() * errorTypes.length)].toLowerCase()} detected for camera ${c.name}`
  }))
}

// Helper functions
const getStatusText = (status: string) => {
  const map: Record<string, string> = { recording: 'Recording', stopped: 'Stopped', fault: 'Fault', scheduled: 'Scheduled' }
  return map[status] || status
}

const getStatusTag = (status: string) => {
  const map: Record<string, string> = { recording: 'success', stopped: 'info', fault: 'danger', scheduled: 'warning' }
  return map[status] || 'info'
}

const getRecordingTypeTag = (type: string) => {
  const map: Record<string, string> = { Continuous: 'danger', Motion: 'success', Schedule: 'warning', Event: 'info' }
  return map[type] || 'info'
}

const getRateColor = (rate: number) => {
  if (rate >= 95) return '#67C23A'
  if (rate >= 85) return '#E6A23C'
  return '#F56C6C'
}

const getHealthColor = (health: number) => {
  if (health >= 85) return '#67C23A'
  if (health >= 70) return '#E6A23C'
  return '#F56C6C'
}

// Actions
const detailDialogVisible = ref(false)
const selectedCamera = ref<CameraRecording | null>(null)

const viewDetails = (camera: CameraRecording) => {
  selectedCamera.value = camera
  detailDialogVisible.value = true
}

const startRecording = (camera: CameraRecording) => {
  ElMessageBox.confirm(`Start recording for "${camera.name}"?`, 'Confirm', {
    confirmButtonText: 'Start',
    cancelButtonText: 'Cancel',
    type: 'info'
  }).then(() => {
    camera.status = 'recording'
    camera.health = 95
    ElMessage.success(`Recording started for ${camera.name}`)
  }).catch(() => {})
}

const retryRecording = (failed: FailedRecording) => {
  const camera = cameras.value.find(c => c.name === failed.cameraName)
  if (camera) {
    startRecording(camera)
    failedRecordings.value = failedRecordings.value.filter(f => f.id !== failed.id)
  }
}

const editSchedule = () => {
  ElMessage.info('Schedule editing feature coming soon')
}

// ==================== Chart Functions ====================
const storageChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()

let storageChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null

const initCharts = () => {
  nextTick(() => {
    if (storageChartRef.value) {
      if (storageChart) storageChart.dispose()
      storageChart = echarts.init(storageChartRef.value)
      updateStorageChart()
    }

    if (trendChartRef.value) {
      if (trendChart) trendChart.dispose()
      trendChart = echarts.init(trendChartRef.value)
      updateTrendChart()
    }
  })
}

const updateStorageChart = () => {
  const nvrNames = Array.from(new Set(cameras.value.map(c => c.nvrName)))
  const storageData = nvrNames.map(nvr => {
    const nvrCameras = cameras.value.filter(c => c.nvrName === nvr)
    return nvrCameras.reduce((sum, c) => sum + c.storageUsed, 0) / 1024
  })

  storageChart?.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'category', data: nvrNames, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'Storage Used (TB)' },
    series: [{
      type: 'bar',
      data: storageData,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value > 40) return '#F56C6C'
          if (value > 25) return '#E6A23C'
          return '#67C23A'
        }
      },
      label: { show: true, position: 'top', formatter: '{c} TB' }
    }]
  })
}

const updateTrendChart = () => {
  let recordingData: number[] = []
  let xAxisData: string[] = []

  if (trendType.value === 'hours') {
    xAxisData = Array.from({ length: 24 }, (_, i) => `${i}:00`)
    recordingData = Array.from({ length: 24 }, () => Math.floor(85 + Math.random() * 15))
  } else {
    xAxisData = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    recordingData = [92, 94, 91, 95, 96, 88, 85]
  }

  trendChart?.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: { type: 'value', name: 'Recording Success Rate (%)', min: 70, max: 100 },
    series: [{
      type: 'line',
      data: recordingData,
      smooth: true,
      lineStyle: { color: '#409EFF', width: 3 },
      areaStyle: { opacity: 0.1 },
      markLine: { data: [{ yAxis: 95, name: 'Target', lineStyle: { color: '#67C23A' } }] }
    }]
  })
}

// ==================== Actions ====================
const refreshData = () => {
  cameras.value = generateCameras()
  failedRecordings.value = generateFailedRecordings()
  updateStorageChart()
  updateTrendChart()
  ElMessage.success('Data refreshed')
}

const handleExport = () => {
  ElMessage.success('Report export started')
}

const handleSizeChange = () => { pagination.value.currentPage = 1 }
const handleCurrentChange = () => {}

// ==================== Lifecycle ====================
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
      cameras.value = generateCameras()
      failedRecordings.value = generateFailedRecordings()
      initCharts()
    }, 400)
  }, 2000)
})

watch([storageChartRef, trendChartRef], () => {
  window.addEventListener('resize', () => {
    storageChart?.resize()
    trendChart?.resize()
  })
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

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Main Container */
.recording-status-container {
  padding: 20px;
  background: #f0f2f5;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  background: white;
  padding: 20px 24px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.page-header h2 {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 600;
  color: #1f2f3d;
}

.header-subtitle {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Overview Cards */
.overview-row {
  margin-bottom: 24px;
}

.overview-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.overview-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.overview-icon.total { background: rgba(64, 158, 255, 0.1); color: #409EFF; }
.overview-icon.recording { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
.overview-icon.stopped { background: rgba(245, 108, 108, 0.1); color: #F56C6C; }
.overview-icon.storage { background: rgba(230, 162, 60, 0.1); color: #E6A23C; }

.overview-info {
  flex: 1;
}

.overview-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.overview-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
}

.overview-value .unit {
  font-size: 12px;
  font-weight: normal;
  color: #909399;
}

.overview-value.has-warning { color: #F56C6C; }

/* Health Card */
.health-row {
  margin-bottom: 24px;
}

.health-card {
  border-radius: 16px;
}

.health-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.health-item {
  text-align: center;
}

.health-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 12px;
}

.health-value {
  display: block;
  margin-top: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #1f2f3d;
}

/* Table Card */
.table-card {
  border-radius: 16px;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-group {
  display: flex;
  gap: 12px;
}

.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

/* Schedule Row */
.schedule-row {
  margin-bottom: 20px;
}

.schedule-card, .storage-card {
  border-radius: 16px;
}

.chart-container-small {
  width: 100%;
  height: 280px;
}

/* Trend Card */
.trend-card {
  border-radius: 16px;
  margin-bottom: 20px;
}

.chart-container {
  width: 100%;
  height: 350px;
}

/* Failed Card */
.failed-card {
  border-radius: 16px;
}

.failed-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #F56C6C;
  font-weight: 600;
}
</style>