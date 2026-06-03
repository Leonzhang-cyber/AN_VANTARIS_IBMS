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
        <div class="loading-tip">Video Loss Monitoring</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="video-loss-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Video Loss Status</h2>
        <p class="header-subtitle">Real-time Video Loss Detection | Signal Health Monitoring</p>
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
          <div class="overview-icon normal">
            <el-icon :size="28"><CircleCheck /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Signal OK</div>
            <div class="overview-value">{{ stats.signalOk }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon loss">
            <el-icon :size="28"><WarningFilled /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Video Loss</div>
            <div class="overview-value" :class="{ 'has-loss': stats.videoLoss > 0 }">{{ stats.videoLoss }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon degraded">
            <el-icon :size="28"><Warning /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Degraded Signal</div>
            <div class="overview-value">{{ stats.degraded }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Video Loss Alert Banner -->
    <div v-if="stats.videoLoss > 0" class="alert-banner">
      <el-alert
          :title="`${stats.videoLoss} camera(s) experiencing video loss. Immediate attention required.`"
          type="error"
          :closable="false"
          show-icon
      >
        <template #default>
          <el-button type="danger" size="small" @click="viewAllLossCameras">View All</el-button>
        </template>
      </el-alert>
    </div>

    <!-- Video Loss Summary Chart -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :md="16">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Video Loss Trend (Last 24 Hours)</span>
              <el-radio-group v-model="trendType" size="small">
                <el-radio-button label="hour">Hourly</el-radio-button>
                <el-radio-button label="day">Daily</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="8">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Camera Status Distribution</span>
            </div>
          </template>
          <div ref="statusChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Video Loss by NVR -->
    <el-card shadow="hover" class="nvr-card">
      <template #header>
        <div class="card-header">
          <span>Video Loss by NVR</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" v-for="nvr in nvrLossStats" :key="nvr.name">
          <div class="nvr-loss-card" :class="getNvrLossClass(nvr.lossCount)">
            <div class="nvr-loss-header">
              <span class="nvr-name">{{ nvr.name }}</span>
              <el-tag :type="getNvrLossTagType(nvr.lossCount)" size="small">
                {{ nvr.lossCount }} Losses
              </el-tag>
            </div>
            <div class="nvr-loss-stats">
              <div class="stat">
                <span>Total Cameras:</span>
                <strong>{{ nvr.totalCameras }}</strong>
              </div>
              <div class="stat">
                <span>Signal OK:</span>
                <strong class="ok">{{ nvr.signalOk }}</strong>
              </div>
              <div class="stat">
                <span>Video Loss:</span>
                <strong class="loss">{{ nvr.videoLoss }}</strong>
              </div>
              <div class="stat">
                <span>Degraded:</span>
                <strong class="degraded">{{ nvr.degraded }}</strong>
              </div>
            </div>
            <div class="nvr-loss-progress">
              <el-progress
                  :percentage="nvr.healthPercent"
                  :color="getHealthColor(nvr.healthPercent)"
                  :stroke-width="8"
                  :show-text="false"
              />
              <span class="health-text">{{ nvr.healthPercent }}% Healthy</span>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- Video Loss Cameras Table -->
    <el-card shadow="hover" class="table-card">
      <template #header>
        <div class="card-header">
          <span>Video Loss Details</span>
          <div class="filter-group">
            <el-select v-model="lossTypeFilter" size="small" style="width: 140px" placeholder="Loss Type" clearable>
              <el-option label="All" value="all" />
              <el-option label="Complete Loss" value="complete" />
              <el-option label="Intermittent" value="intermittent" />
              <el-option label="Noise/Snow" value="noise" />
              <el-option label="Black Screen" value="black" />
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
      <el-table :data="paginatedLossCameras" stripe border style="width: 100%">
        <el-table-column prop="name" label="Camera Name" min-width="160" />
        <el-table-column prop="nvrName" label="NVR" min-width="140" />
        <el-table-column prop="lossType" label="Loss Type" width="130">
          <template #default="{ row }">
            <el-tag :type="getLossTypeTag(row.lossType)" size="small">
              {{ getLossTypeText(row.lossType) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="signalStrength" label="Signal Strength" width="140" sortable>
          <template #default="{ row }">
            <el-progress :percentage="row.signalStrength" :color="getSignalColor(row.signalStrength)" :stroke-width="8" />
          </template>
        </el-table-column>
        <el-table-column prop="lastSeen" label="Last Seen" width="160" sortable />
        <el-table-column prop="duration" label="Duration" width="100" sortable />
        <el-table-column prop="resolution" label="Resolution" width="100" />
        <el-table-column label="Actions" fixed="right" width="140">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetails(row)">
              Details
            </el-button>
            <el-button type="success" link size="small" @click="diagnose(row)">
              Diagnose
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredLossCameras.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Signal Quality Metrics -->
    <el-row :gutter="20" class="quality-row">
      <el-col :xs="24" :md="6">
        <div class="quality-card">
          <div class="quality-icon">
            <el-icon :size="32"><Connection /></el-icon>
          </div>
          <div class="quality-info">
            <div class="quality-label">Average Signal Strength</div>
            <div class="quality-value">{{ signalMetrics.avgStrength }}<span class="unit">%</span></div>
            <el-progress :percentage="signalMetrics.avgStrength" :color="getSignalColor(signalMetrics.avgStrength)" :stroke-width="6" />
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :md="6">
        <div class="quality-card">
          <div class="quality-icon">
            <el-icon :size="32"><Timer /></el-icon>
          </div>
          <div class="quality-info">
            <div class="quality-label">Avg Recovery Time</div>
            <div class="quality-value">{{ signalMetrics.avgRecoveryTime }}<span class="unit">min</span></div>
            <div class="quality-trend" :class="signalMetrics.recoveryTrend > 0 ? 'down' : 'up'">
              {{ Math.abs(signalMetrics.recoveryTrend) }}% vs last week
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :md="6">
        <div class="quality-card">
          <div class="quality-icon">
            <el-icon :size="32"><Warning /></el-icon>
          </div>
          <div class="quality-info">
            <div class="quality-label">Most Common Issue</div>
            <div class="quality-value">{{ signalMetrics.commonIssue }}</div>
            <div class="quality-sub">{{ signalMetrics.commonIssueCount }} occurrences</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :md="6">
        <div class="quality-card">
          <div class="quality-icon">
            <el-icon :size="32"><Clock /></el-icon>
          </div>
          <div class="quality-info">
            <div class="quality-label">Peak Loss Time</div>
            <div class="quality-value">{{ signalMetrics.peakLossTime }}</div>
            <div class="quality-sub">Most frequent losses</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Camera Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Camera Details - ${selectedCamera?.name}`" width="600px">
      <el-descriptions :column="2" border v-if="selectedCamera">
        <el-descriptions-item label="Camera Name">{{ selectedCamera.name }}</el-descriptions-item>
        <el-descriptions-item label="NVR">{{ selectedCamera.nvrName }}</el-descriptions-item>
        <el-descriptions-item label="Loss Type">
          <el-tag :type="getLossTypeTag(selectedCamera.lossType)">{{ getLossTypeText(selectedCamera.lossType) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Signal Strength">{{ selectedCamera.signalStrength }}%</el-descriptions-item>
        <el-descriptions-item label="Last Seen">{{ selectedCamera.lastSeen }}</el-descriptions-item>
        <el-descriptions-item label="Duration">{{ selectedCamera.duration }}</el-descriptions-item>
        <el-descriptions-item label="IP Address">{{ selectedCamera.ipAddress }}</el-descriptions-item>
        <el-descriptions-item label="Channel">{{ selectedCamera.channel }}</el-descriptions-item>
        <el-descriptions-item label="Resolution">{{ selectedCamera.resolution }}</el-descriptions-item>
        <el-descriptions-item label="Bitrate">{{ selectedCamera.bitrate }} Mbps</el-descriptions-item>
        <el-descriptions-item label="Packet Loss">{{ selectedCamera.packetLoss }}%</el-descriptions-item>
        <el-descriptions-item label="Jitter">{{ selectedCamera.jitter }} ms</el-descriptions-item>
        <el-descriptions-item label="Diagnosis" :span="2">{{ selectedCamera.diagnosis }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button type="primary" @click="diagnoseCamera">Run Diagnostic</el-button>
        <el-button @click="detailDialogVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Diagnosis Dialog -->
    <el-dialog v-model="diagnosisDialogVisible" title="Diagnosis Result" width="450px">
      <div class="diagnosis-content">
        <el-result
            :icon="diagnosisResult.passed ? 'success' : 'error'"
            :title="diagnosisResult.title"
            :sub-title="diagnosisResult.message"
        />
        <div class="diagnosis-suggestions" v-if="diagnosisResult.suggestions">
          <h4>Suggestions:</h4>
          <ul>
            <li v-for="suggestion in diagnosisResult.suggestions" :key="suggestion">{{ suggestion }}</li>
          </ul>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="diagnosisDialogVisible = false">Close</el-button>
      </template>
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
  CircleCheck,
  WarningFilled,
  Warning,
  Search,
  Connection,
  Timer,
  Clock
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Checking video signals...',
  'Analyzing loss patterns...',
  'Almost ready...'
]

// ==================== Data State ====================
const trendType = ref('hour')
const lossTypeFilter = ref('all')
const nvrFilter = ref('all')
const searchText = ref('')

interface LossCamera {
  id: number
  name: string
  nvrName: string
  lossType: 'complete' | 'intermittent' | 'noise' | 'black'
  signalStrength: number
  lastSeen: string
  duration: string
  resolution: string
  ipAddress: string
  channel: number
  bitrate: number
  packetLoss: number
  jitter: number
  diagnosis: string
}

interface NvrLossStat {
  name: string
  totalCameras: number
  signalOk: number
  videoLoss: number
  degraded: number
  lossCount: number
  healthPercent: number
}

const cameras = ref<LossCamera[]>([])
const lossCameras = ref<LossCamera[]>([])
const nvrLossStats = ref<NvrLossStat[]>([])
const nvrList = ref<string[]>([])

const signalMetrics = ref({
  avgStrength: 0,
  avgRecoveryTime: 0,
  recoveryTrend: 0,
  commonIssue: '',
  commonIssueCount: 0,
  peakLossTime: ''
})

const stats = computed(() => ({
  totalCameras: cameras.value.length,
  signalOk: cameras.value.filter(c => c.signalStrength >= 80).length,
  videoLoss: cameras.value.filter(c => c.signalStrength < 20).length,
  degraded: cameras.value.filter(c => c.signalStrength >= 20 && c.signalStrength < 80).length
}))

const filteredLossCameras = computed(() => {
  let filtered = lossCameras.value
  if (lossTypeFilter.value !== 'all') {
    filtered = filtered.filter(c => c.lossType === lossTypeFilter.value)
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
const paginatedLossCameras = computed(() => {
  const start = (pagination.value.currentPage - 1) * pagination.value.pageSize
  return filteredLossCameras.value.slice(start, start + pagination.value.pageSize)
})

// Generate mock camera data
const generateCameras = (): LossCamera[] => {
  const nvrs = ['Main NVR-01', 'Main NVR-02', 'Building B NVR', 'Parking NVR', 'Building C NVR']
  const locations = [
    'Entrance', 'Exit', 'Lobby', 'Corridor E', 'Corridor W', 'Staircase A', 'Staircase B',
    'Elevator 1', 'Elevator 2', 'Meeting Room', 'Office Area', 'Server Room', 'Storage',
    'Parking A', 'Parking B', 'Loading Dock', 'Security Gate', 'Reception'
  ]
  const lossTypes: ('complete' | 'intermittent' | 'noise' | 'black')[] = ['complete', 'intermittent', 'noise', 'black']

  nvrList.value = nvrs

  const camerasList: LossCamera[] = []
  let id = 1

  nvrs.forEach(nvr => {
    const numCameras = nvr === 'Main NVR-01' ? 32 : (nvr === 'Main NVR-02' ? 28 : (nvr === 'Building B NVR' ? 48 : (nvr === 'Parking NVR' ? 16 : 36)))
    for (let i = 1; i <= numCameras; i++) {
      // Generate signal strength with some cameras having loss
      let signalStrength: number
      let lossType: 'complete' | 'intermittent' | 'noise' | 'black' = 'complete'
      let diagnosis = ''

      const rand = Math.random()
      if (rand < 0.85) {
        // Normal camera
        signalStrength = Math.floor(85 + Math.random() * 15)
      } else if (rand < 0.92) {
        // Degraded signal
        signalStrength = Math.floor(40 + Math.random() * 40)
        lossType = lossTypes[Math.floor(Math.random() * 2)]
        diagnosis = `Signal ${lossType === 'intermittent' ? 'intermittent' : 'noisy'}. Check cable connection.`
      } else {
        // Complete loss
        signalStrength = Math.floor(0 + Math.random() * 20)
        lossType = rand < 0.96 ? 'complete' : 'black'
        diagnosis = `No video signal. ${lossType === 'complete' ? 'Camera may be offline or cable disconnected.' : 'Black screen detected. Check camera power supply.'}`
      }

      const lastSeen = new Date(Date.now() - Math.random() * 60 * 60 * 1000)
      const durationMinutes = signalStrength < 20 ? Math.floor(5 + Math.random() * 120) : 0

      camerasList.push({
        id: id++,
        name: `${nvr.split(' ')[0]} ${locations[i % locations.length]} ${Math.floor(i / locations.length) + 1}`,
        nvrName: nvr,
        lossType: lossType,
        signalStrength: signalStrength,
        lastSeen: lastSeen.toLocaleString(),
        duration: durationMinutes > 0 ? `${durationMinutes} min` : 'Active',
        resolution: ['1920x1080', '2560x1440', '3840x2160'][Math.floor(Math.random() * 3)],
        ipAddress: `192.168.${Math.floor(1 + Math.random() * 5)}.${Math.floor(10 + Math.random() * 250)}`,
        channel: i,
        bitrate: parseFloat((2 + Math.random() * 8).toFixed(1)),
        packetLoss: signalStrength < 50 ? parseFloat((Math.random() * 10).toFixed(1)) : parseFloat((Math.random() * 2).toFixed(1)),
        jitter: signalStrength < 50 ? Math.floor(10 + Math.random() * 40) : Math.floor(1 + Math.random() * 10),
        diagnosis: diagnosis
      })
    }
  })

  return camerasList
}

// Calculate NVR loss stats
const calculateNvrLossStats = () => {
  const nvrMap = new Map<string, NvrLossStat>()

  cameras.value.forEach(camera => {
    if (!nvrMap.has(camera.nvrName)) {
      nvrMap.set(camera.nvrName, {
        name: camera.nvrName,
        totalCameras: 0,
        signalOk: 0,
        videoLoss: 0,
        degraded: 0,
        lossCount: 0,
        healthPercent: 0
      })
    }

    const stat = nvrMap.get(camera.nvrName)!
    stat.totalCameras++

    if (camera.signalStrength >= 80) {
      stat.signalOk++
    } else if (camera.signalStrength < 20) {
      stat.videoLoss++
      stat.lossCount++
    } else {
      stat.degraded++
    }

    stat.healthPercent = Math.floor((stat.signalOk / stat.totalCameras) * 100)
    nvrMap.set(camera.nvrName, stat)
  })

  nvrLossStats.value = Array.from(nvrMap.values())
}

// Calculate signal metrics
const calculateSignalMetrics = () => {
  const lossCamerasList = cameras.value.filter(c => c.signalStrength < 20)

  const avgStrength = cameras.value.reduce((sum, c) => sum + c.signalStrength, 0) / cameras.value.length

  const lossTypes = ['complete', 'intermittent', 'noise', 'black']
  const lossCounts = lossTypes.map(type => lossCamerasList.filter(c => c.lossType === type).length)
  const maxIndex = lossCounts.indexOf(Math.max(...lossCounts))

  signalMetrics.value = {
    avgStrength: Math.floor(avgStrength),
    avgRecoveryTime: parseFloat((15 + Math.random() * 15).toFixed(1)),
    recoveryTrend: parseFloat((Math.random() * 20 - 10).toFixed(1)),
    commonIssue: getLossTypeText(lossTypes[maxIndex] as any),
    commonIssueCount: Math.max(...lossCounts),
    peakLossTime: '14:00 - 16:00'
  }
}

// Update loss cameras list
const updateLossCameras = () => {
  lossCameras.value = cameras.value.filter(c => c.signalStrength < 80)
}

// Helper functions
const getLossTypeText = (type: string) => {
  const map: Record<string, string> = {
    complete: 'Complete Loss',
    intermittent: 'Intermittent',
    noise: 'Noise/Snow',
    black: 'Black Screen'
  }
  return map[type] || type
}

const getLossTypeTag = (type: string) => {
  const map: Record<string, string> = {
    complete: 'danger',
    intermittent: 'warning',
    noise: 'warning',
    black: 'danger'
  }
  return map[type] || 'info'
}

const getSignalColor = (strength: number) => {
  if (strength >= 80) return '#67C23A'
  if (strength >= 50) return '#E6A23C'
  return '#F56C6C'
}

const getHealthColor = (percent: number) => {
  if (percent >= 90) return '#67C23A'
  if (percent >= 70) return '#E6A23C'
  return '#F56C6C'
}

const getNvrLossClass = (lossCount: number) => {
  if (lossCount === 0) return 'healthy'
  if (lossCount <= 5) return 'warning'
  return 'critical'
}

const getNvrLossTagType = (lossCount: number) => {
  if (lossCount === 0) return 'success'
  if (lossCount <= 5) return 'warning'
  return 'danger'
}

const viewAllLossCameras = () => {
  lossTypeFilter.value = 'all'
  ElMessage.info('Showing all cameras with video loss')
}

// Actions
const detailDialogVisible = ref(false)
const diagnosisDialogVisible = ref(false)
const selectedCamera = ref<LossCamera | null>(null)
const diagnosisResult = ref({
  passed: true,
  title: '',
  message: '',
  suggestions: [] as string[]
})

const viewDetails = (camera: LossCamera) => {
  selectedCamera.value = camera
  detailDialogVisible.value = true
}

const diagnose = (camera: LossCamera) => {
  selectedCamera.value = camera

  if (camera.signalStrength < 20) {
    diagnosisResult.value = {
      passed: false,
      title: 'Video Loss Detected',
      message: `Camera "${camera.name}" is experiencing ${getLossTypeText(camera.lossType)}.`,
      suggestions: [
        'Check camera power supply',
        'Verify network cable connection',
        'Test camera with known good cable',
        'Check NVR recording settings',
        'Reboot camera remotely if possible'
      ]
    }
  } else if (camera.signalStrength < 80) {
    diagnosisResult.value = {
      passed: false,
      title: 'Degraded Signal Quality',
      message: `Signal strength is ${camera.signalStrength}%. Packet loss: ${camera.packetLoss}%, Jitter: ${camera.jitter}ms.`,
      suggestions: [
        'Check cable quality and connectors',
        'Verify network bandwidth availability',
        'Reduce camera bitrate settings',
        'Check for electrical interference',
        'Consider using shielded cables'
      ]
    }
  } else {
    diagnosisResult.value = {
      passed: true,
      title: 'Signal Quality Good',
      message: `Camera signal is healthy at ${camera.signalStrength}%. No action required.`,
      suggestions: []
    }
  }

  diagnosisDialogVisible.value = true
}

const diagnoseCamera = () => {
  if (selectedCamera.value) {
    diagnose(selectedCamera.value)
  }
}

// ==================== Chart Functions ====================
const trendChartRef = ref<HTMLElement>()
const statusChartRef = ref<HTMLElement>()

let trendChart: echarts.ECharts | null = null
let statusChart: echarts.ECharts | null = null

const initCharts = () => {
  nextTick(() => {
    if (trendChartRef.value) {
      if (trendChart) trendChart.dispose()
      trendChart = echarts.init(trendChartRef.value)
      updateTrendChart()
    }

    if (statusChartRef.value) {
      if (statusChart) statusChart.dispose()
      statusChart = echarts.init(statusChartRef.value)
      updateStatusChart()
    }
  })
}

const updateTrendChart = () => {
  let lossCounts: number[] = []
  let xAxisData: string[] = []

  if (trendType.value === 'hour') {
    xAxisData = Array.from({ length: 24 }, (_, i) => `${i}:00`)
    lossCounts = Array.from({ length: 24 }, () => Math.floor(5 + Math.random() * 25))
  } else {
    xAxisData = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    lossCounts = [12, 8, 15, 10, 18, 22, 14]
  }

  trendChart?.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: { type: 'value', name: 'Cameras with Video Loss' },
    series: [{
      type: 'line',
      data: lossCounts,
      smooth: true,
      lineStyle: { color: '#F56C6C', width: 3 },
      areaStyle: { opacity: 0.1, color: '#F56C6C' },
      symbol: 'circle',
      symbolSize: 6
    }]
  })
}

const updateStatusChart = () => {
  statusChart?.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: stats.value.signalOk, name: 'Signal OK', itemStyle: { color: '#67C23A' } },
        { value: stats.value.degraded, name: 'Degraded Signal', itemStyle: { color: '#E6A23C' } },
        { value: stats.value.videoLoss, name: 'Video Loss', itemStyle: { color: '#F56C6C' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })
}

// ==================== Actions ====================
const refreshData = () => {
  cameras.value = generateCameras()
  calculateNvrLossStats()
  updateLossCameras()
  calculateSignalMetrics()
  updateStatusChart()
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
      calculateNvrLossStats()
      updateLossCameras()
      calculateSignalMetrics()
      initCharts()
    }, 400)
  }, 2000)
})

watch([trendChartRef, statusChartRef], () => {
  window.addEventListener('resize', () => {
    trendChart?.resize()
    statusChart?.resize()
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
.video-loss-container {
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
.overview-icon.normal { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
.overview-icon.loss { background: rgba(245, 108, 108, 0.1); color: #F56C6C; }
.overview-icon.degraded { background: rgba(230, 162, 60, 0.1); color: #E6A23C; }

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

.overview-value.has-loss { color: #F56C6C; }

/* Alert Banner */
.alert-banner {
  margin-bottom: 20px;
}

/* Charts */
.chart-row {
  margin-bottom: 24px;
}

.chart-card {
  border-radius: 16px;
}

.chart-container {
  width: 100%;
  height: 350px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

/* NVR Loss Cards */
.nvr-card {
  border-radius: 16px;
  margin-bottom: 20px;
}

.nvr-loss-card {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  transition: all 0.3s ease;
  border-left: 4px solid #67C23A;
}

.nvr-loss-card.healthy { border-left-color: #67C23A; }
.nvr-loss-card.warning { border-left-color: #E6A23C; background: rgba(230, 162, 60, 0.05); }
.nvr-loss-card.critical { border-left-color: #F56C6C; background: rgba(245, 108, 108, 0.05); }

.nvr-loss-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.nvr-name {
  font-weight: 600;
  font-size: 16px;
  color: #1f2f3d;
}

.nvr-loss-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}

.stat {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #606266;
}

.stat strong.ok { color: #67C23A; }
.stat strong.loss { color: #F56C6C; }
.stat strong.degraded { color: #E6A23C; }

.nvr-loss-progress {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nvr-loss-progress .el-progress {
  flex: 1;
}

.health-text {
  font-size: 12px;
  font-weight: 500;
  min-width: 60px;
}

/* Table Card */
.table-card {
  border-radius: 16px;
  margin-bottom: 20px;
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

/* Quality Cards */
.quality-row {
  margin-bottom: 20px;
}

.quality-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.3s ease;
}

.quality-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.quality-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: rgba(64, 158, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409EFF;
}

.quality-info {
  flex: 1;
}

.quality-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.quality-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2f3d;
}

.quality-value .unit {
  font-size: 12px;
  font-weight: normal;
  color: #909399;
}

.quality-trend {
  font-size: 12px;
  margin-top: 4px;
}

.quality-trend.up { color: #67C23A; }
.quality-trend.down { color: #F56C6C; }

.quality-sub {
  font-size: 11px;
  color: #909399;
  margin-top: 4px;
}

/* Diagnosis Dialog */
.diagnosis-content {
  padding: 10px;
}

.diagnosis-suggestions {
  margin-top: 20px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.diagnosis-suggestions h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #606266;
}

.diagnosis-suggestions ul {
  margin: 0;
  padding-left: 20px;
}

.diagnosis-suggestions li {
  font-size: 13px;
  color: #909399;
  margin: 4px 0;
}
</style>