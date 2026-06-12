<script setup lang="ts">
import { ref, onMounted, computed, watch, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Camera, Monitor, VideoCamera, BellFilled,
  Refresh, Connection, Setting, VideoPlay, Search
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing Dahua SDK...',
  'Connecting to platform...',
  'Syncing device list...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const liveStreamVisible = ref(false)
const playbackVisible = ref(false)
const configDrawerVisible = ref(false)
const deviceConfigVisible = ref(false)
const onlineChartRef = ref(null)
const alertChartRef = ref(null)
const videoPlayer = ref(null)
const playbackPlayer = ref(null)

let onlineChart: echarts.ECharts | null = null
let alertChart: echarts.ECharts | null = null

const selectedDevice = ref<any>(null)
const selectedPlaybackDate = ref('')
const currentChartPeriod = ref('week')

// Statistics data
const stats = reactive({
  totalCameras: 234,
  onlineRate: 96.5,
  totalNVR: 18,
  totalDVR: 6,
  recordingDevices: 218,
  activeAlerts: 12,
  storageUsed: 68,
  bandwidthUsage: 45
})

// Device list data
const devices = ref([
  { id: 'D001', name: 'Main Entrance Camera', location: 'Main Gate', ip: '192.168.2.101', status: 'online', recording: true, lastHeartbeat: '2024-01-15 10:23:45', rtspUrl: '', type: 'Bullet', resolution: '4K' },
  { id: 'D002', name: 'North Tower Camera', location: 'North Tower', ip: '192.168.2.102', status: 'online', recording: true, lastHeartbeat: '2024-01-15 10:22:30', rtspUrl: '', type: 'PTZ', resolution: '4K' },
  { id: 'D003', name: 'South Tower Camera', location: 'South Tower', ip: '192.168.2.103', status: 'online', recording: true, lastHeartbeat: '2024-01-15 10:24:12', rtspUrl: '', type: 'PTZ', resolution: '4K' },
  { id: 'D004', name: 'Parking Lot Camera', location: 'B1 Parking', ip: '192.168.2.104', status: 'online', recording: false, lastHeartbeat: '2024-01-15 10:20:00', rtspUrl: '', type: 'Dome', resolution: '1080p' },
  { id: 'D005', name: 'Lobby Camera', location: '1F Lobby', ip: '192.168.2.105', status: 'online', recording: true, lastHeartbeat: '2024-01-15 10:23:00', rtspUrl: '', type: 'Dome', resolution: '4K' },
  { id: 'D006', name: 'Corridor Camera', location: '2F Corridor', ip: '192.168.2.106', status: 'offline', recording: false, lastHeartbeat: '2024-01-14 18:30:00', rtspUrl: '', type: 'Bullet', resolution: '1080p' },
  { id: 'D007', name: 'Meeting Room A', location: '3F Meeting Room A', ip: '192.168.2.107', status: 'online', recording: true, lastHeartbeat: '2024-01-15 10:22:15', rtspUrl: '', type: 'Dome', resolution: '2K' },
  { id: 'D008', name: 'Server Room', location: 'B2 Server Room', ip: '192.168.2.108', status: 'online', recording: true, lastHeartbeat: '2024-01-15 10:21:30', rtspUrl: '', type: 'Bullet', resolution: '4K' },
  { id: 'D009', name: 'Elevator A', location: 'Elevator A', ip: '192.168.2.109', status: 'offline', recording: false, lastHeartbeat: '2024-01-14 20:15:00', rtspUrl: '', type: 'Dome', resolution: '1080p' },
  { id: 'D010', name: 'Staircase East', location: 'East Staircase', ip: '192.168.2.110', status: 'online', recording: true, lastHeartbeat: '2024-01-15 10:23:45', rtspUrl: '', type: 'Bullet', resolution: '2K' },
  { id: 'D011', name: 'Loading Dock', location: 'Loading Dock', ip: '192.168.2.111', status: 'online', recording: true, lastHeartbeat: '2024-01-15 10:22:30', rtspUrl: '', type: 'Bullet', resolution: '4K' },
  { id: 'D012', name: 'Security Desk', location: 'Security Office', ip: '192.168.2.112', status: 'online', recording: true, lastHeartbeat: '2024-01-15 10:24:12', rtspUrl: '', type: 'Dome', resolution: '2K' }
])

// Platform configuration
const platformConfig = ref({
  host: 'https://dahua-platform.example.com',
  appKey: '',
  appSecret: '',
  syncInterval: 900,
  maxRetries: 3,
  timeout: 30
})

// Device configuration form
const deviceConfigForm = ref({
  name: '',
  location: '',
  rtspUrl: '',
  recordingSchedule: '247',
  motionDetection: true,
  smartTracking: false,
  recordingQuality: 'high'
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: devices.value.length
})

// Filtered devices
const filteredDevices = computed(() => {
  let filtered = devices.value
  if (searchKeyword.value) {
    filtered = filtered.filter(d =>
        d.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        d.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        d.location.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        d.ip.includes(searchKeyword.value)
    )
  }
  pagination.total = filtered.length
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// Watch for search keyword to reset pagination
watch(searchKeyword, () => {
  pagination.page = 1
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
        initOnlineChart()
        initAlertChart()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initOnlineChart = () => {
  if (!onlineChartRef.value) return

  onlineChart = echarts.init(onlineChartRef.value)
  updateOnlineChart()
}

const updateOnlineChart = () => {
  const weekData = {
    xAxis: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    online: [225, 228, 230, 229, 231, 227, 226],
    offline: [9, 6, 4, 5, 3, 7, 8]
  }

  const monthData = {
    xAxis: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    online: [226, 228, 230, 229],
    offline: [8, 6, 4, 5]
  }

  const data = currentChartPeriod.value === 'week' ? weekData : monthData

  onlineChart?.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Online', 'Offline'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: data.xAxis },
    yAxis: { type: 'value', name: 'Device Count' },
    series: [
      { name: 'Online', type: 'line', data: data.online, smooth: true, lineStyle: { color: '#67C23A', width: 2 }, areaStyle: { opacity: 0.1, color: '#67C23A' }, symbol: 'circle', symbolSize: 8 },
      { name: 'Offline', type: 'line', data: data.offline, smooth: true, lineStyle: { color: '#F56C6C', width: 2 }, symbol: 'diamond', symbolSize: 8 }
    ]
  })
}

const initAlertChart = () => {
  if (!alertChartRef.value) return

  alertChart = echarts.init(alertChartRef.value)
  alertChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c})' },
    legend: { orient: 'vertical', left: 'left', data: ['Motion Detection', 'Network Loss', 'Storage Error', 'Device Offline', 'Smart Detection'] },
    series: [{
      type: 'pie',
      radius: ['40%', '65%'],
      center: ['50%', '50%'],
      data: [
        { name: 'Motion Detection', value: 42, itemStyle: { color: '#E6A23C' } },
        { name: 'Network Loss', value: 23, itemStyle: { color: '#F56C6C' } },
        { name: 'Storage Error', value: 15, itemStyle: { color: '#909399' } },
        { name: 'Device Offline', value: 12, itemStyle: { color: '#67C23A' } },
        { name: 'Smart Detection', value: 8, itemStyle: { color: '#409EFF' } }
      ],
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: {d}%' },
      labelLine: { show: true }
    }]
  })
}

const handleResize = () => {
  onlineChart?.resize()
  alertChart?.resize()
}

// ==================== Actions ====================
const formatTime = (time: string) => {
  return time
}

const toggleChartPeriod = () => {
  currentChartPeriod.value = currentChartPeriod.value === 'week' ? 'month' : 'week'
  updateOnlineChart()
}

const showAlertDetails = () => {
  ElMessage.info('View detailed alert report')
}

const syncDevices = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1500))
    ElMessage.success('Device synchronization completed successfully')
  } catch (error) {
    ElMessage.error('Sync failed')
  } finally {
    loading.value = false
  }
}

const testConnection = async () => {
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('Dahua platform connection successful')
  } catch (error) {
    ElMessage.error('Connection failed')
  }
}

const openConfigDrawer = () => {
  configDrawerVisible.value = true
}

const saveConfig = async () => {
  try {
    await new Promise(resolve => setTimeout(resolve, 800))
    ElMessage.success('Configuration saved successfully')
    configDrawerVisible.value = false
  } catch (error) {
    ElMessage.error('Failed to save configuration')
  }
}

const viewLiveStream = (device: any) => {
  selectedDevice.value = device
  liveStreamVisible.value = true
  setTimeout(() => {
    if (videoPlayer.value) {
      ElMessage.info(`Loading live stream for ${device.name}`)
    }
  }, 500)
}

const viewPlayback = (device: any) => {
  selectedDevice.value = device
  selectedPlaybackDate.value = new Date().toISOString().split('T')[0]
  playbackVisible.value = true
}

const searchPlayback = () => {
  if (selectedDevice.value && selectedPlaybackDate.value) {
    ElMessage.info(`Searching playback for ${selectedDevice.value.name} on ${selectedPlaybackDate.value}`)
    if (playbackPlayer.value) {
      setTimeout(() => {
        ElMessage.success('Playback video loaded')
      }, 1000)
    }
  }
}

const showDeviceConfig = (device: any) => {
  selectedDevice.value = device
  deviceConfigForm.value = {
    name: device.name,
    location: device.location,
    rtspUrl: device.rtspUrl || '',
    recordingSchedule: '247',
    motionDetection: true,
    smartTracking: device.type === 'PTZ',
    recordingQuality: 'high'
  }
  deviceConfigVisible.value = true
}

const saveDeviceConfig = async () => {
  if (selectedDevice.value) {
    selectedDevice.value.name = deviceConfigForm.value.name
    selectedDevice.value.location = deviceConfigForm.value.location
    selectedDevice.value.rtspUrl = deviceConfigForm.value.rtspUrl
    ElMessage.success('Device configuration saved successfully')
    deviceConfigVisible.value = false
  }
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const refreshDevices = () => {
  syncDevices()
}

const formatStorage = (percentage: number) => {
  return `${percentage}%`
}

const getDeviceTypeIcon = (type: string) => {
  return type === 'PTZ' ? '🔄' : type === 'Dome' ? '🔵' : '📷'
}
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
          <span class="loading-title">Loading Dahua Platform</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Dahua Platform Adapter</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="dahua-platform-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h2>Dahua Platform Adapter</h2>
        <el-tag type="success" effect="dark">Online</el-tag>
      </div>
      <div class="header-stats">
        <el-tag type="info" effect="plain">SDK Version: v2.4.1</el-tag>
      </div>
    </div>

    <!-- Stat Cards -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon camera-icon">
            <el-icon><Camera /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalCameras }}</div>
            <div class="stat-label">Total Cameras</div>
            <div class="stat-trend">
              <el-progress :percentage="stats.onlineRate" :color="'#67C23A'" :stroke-width="6" />
              <span class="online-rate-text">{{ stats.onlineRate }}% Online</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon nvr-icon">
            <el-icon><Monitor /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalNVR }}</div>
            <div class="stat-label">NVR Devices</div>
            <div class="stat-sub-value">{{ stats.totalDVR }} DVR</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon record-icon">
            <el-icon><VideoCamera /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.recordingDevices }}</div>
            <div class="stat-label">Recording Devices</div>
            <div class="stat-trend">
              <span class="storage-text">Storage: {{ formatStorage(stats.storageUsed) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon alert-icon">
            <el-icon><BellFilled /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.activeAlerts }}</div>
            <div class="stat-label">Active Alerts</div>
            <div class="stat-trend">
              <span class="bandwidth-text">Bandwidth: {{ stats.bandwidthUsage }}%</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Chart Section -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Device Online Trend</span>
              <el-button text type="primary" @click="toggleChartPeriod">
                {{ currentChartPeriod === 'week' ? 'This Week' : 'This Month' }}
              </el-button>
            </div>
          </template>
          <div ref="onlineChartRef" class="chart" style="height: 300px"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Alert Distribution</span>
              <el-button text type="primary" @click="showAlertDetails">Details</el-button>
            </div>
          </template>
          <div ref="alertChartRef" class="chart" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Device Table -->
    <el-card shadow="never" class="device-table-card">
      <template #header>
        <div class="table-header">
          <span>Camera Device List</span>
          <div class="table-actions">
            <el-input
                v-model="searchKeyword"
                placeholder="Search devices..."
                :prefix-icon="Search"
                style="width: 220px"
                clearable
            />
            <el-button type="primary" @click="syncDevices" :loading="loading">
              <el-icon><Refresh /></el-icon>
              Sync Devices
            </el-button>
            <el-button @click="openConfigDrawer">
              <el-icon><Setting /></el-icon>
              Platform Settings
            </el-button>
            <el-button @click="testConnection">
              <el-icon><Connection /></el-icon>
              Test Connection
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredDevices" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="Device ID" width="100" />
        <el-table-column prop="name" label="Device Name" min-width="180" />
        <el-table-column prop="location" label="Location" width="140" />
        <el-table-column prop="ip" label="IP Address" width="130" />
        <el-table-column prop="type" label="Type" width="80" align="center">
          <template #default="{ row }">
            <span>{{ getDeviceTypeIcon(row.type) }} {{ row.type }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="resolution" label="Resolution" width="80" align="center" />
        <el-table-column label="Status" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'online' ? 'success' : 'danger'" size="small">
              {{ row.status === 'online' ? 'Online' : 'Offline' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Recording" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.recording ? 'primary' : 'info'" size="small">
              {{ row.recording ? 'Recording' : 'Stopped' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Last Heartbeat" width="155">
          <template #default="{ row }">
            {{ formatTime(row.lastHeartbeat) }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="210" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewLiveStream(row)">
              <el-icon><VideoPlay /></el-icon> Live
            </el-button>
            <el-button link type="primary" size="small" @click="viewPlayback(row)">
              <el-icon><VideoCamera /></el-icon> Playback
            </el-button>
            <el-button link type="danger" size="small" @click="showDeviceConfig(row)">
              <el-icon><Setting /></el-icon> Config
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- Live Stream Dialog -->
    <el-dialog v-model="liveStreamVisible" title="Live Preview" width="900px" destroy-on-close>
      <div class="video-container">
        <div class="video-info" v-if="selectedDevice">
          <span>{{ selectedDevice.name }} - {{ selectedDevice.location }}</span>
          <el-tag size="small" type="success">LIVE</el-tag>
        </div>
        <video ref="videoPlayer" controls autoplay style="width: 100%; height: 400px"></video>
      </div>
    </el-dialog>

    <!-- Playback Dialog -->
    <el-dialog v-model="playbackVisible" title="Playback" width="900px" destroy-on-close>
      <div class="playback-controls">
        <el-date-picker
            v-model="selectedPlaybackDate"
            type="date"
            placeholder="Select date"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
        />
        <el-button type="primary" @click="searchPlayback">Search</el-button>
      </div>
      <div class="video-container playback-container">
        <div class="video-info" v-if="selectedDevice">
          <span>{{ selectedDevice.name }} - Playback</span>
        </div>
        <video ref="playbackPlayer" controls style="width: 100%; height: 350px"></video>
      </div>
    </el-dialog>

    <!-- Platform Configuration Drawer -->
    <el-drawer v-model="configDrawerVisible" title="Platform Configuration" direction="rtl" size="500px">
      <el-form :model="platformConfig" label-width="120px">
        <el-form-item label="Platform URL">
          <el-input v-model="platformConfig.host" placeholder="https://your-dahua-platform.com" />
        </el-form-item>
        <el-form-item label="App Key">
          <el-input v-model="platformConfig.appKey" placeholder="Enter App Key" />
        </el-form-item>
        <el-form-item label="App Secret">
          <el-input v-model="platformConfig.appSecret" type="password" show-password />
        </el-form-item>
        <el-form-item label="Sync Interval">
          <el-select v-model="platformConfig.syncInterval">
            <el-option label="5 minutes" :value="300" />
            <el-option label="15 minutes" :value="900" />
            <el-option label="30 minutes" :value="1800" />
            <el-option label="1 hour" :value="3600" />
          </el-select>
        </el-form-item>
        <el-form-item label="Max Retries">
          <el-input-number v-model="platformConfig.maxRetries" :min="1" :max="10" />
        </el-form-item>
        <el-form-item label="Timeout (s)">
          <el-input-number v-model="platformConfig.timeout" :min="5" :max="120" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveConfig">Save Configuration</el-button>
          <el-button @click="testConnection">Test Connection</el-button>
        </el-form-item>
      </el-form>
    </el-drawer>

    <!-- Device Configuration Dialog -->
    <el-dialog v-model="deviceConfigVisible" :title="`Device Configuration - ${selectedDevice?.name}`" width="600px">
      <el-form :model="deviceConfigForm" label-width="140px">
        <el-form-item label="Device Name">
          <el-input v-model="deviceConfigForm.name" />
        </el-form-item>
        <el-form-item label="Location">
          <el-input v-model="deviceConfigForm.location" />
        </el-form-item>
        <el-form-item label="RTSP URL">
          <el-input v-model="deviceConfigForm.rtspUrl" placeholder="rtsp://username:password@ip:port/stream" />
        </el-form-item>
        <el-form-item label="Recording Schedule">
          <el-select v-model="deviceConfigForm.recordingSchedule">
            <el-option label="24/7" value="247" />
            <el-option label="Business Hours" value="business" />
            <el-option label="Motion Detection" value="motion" />
            <el-option label="Custom" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="Recording Quality">
          <el-select v-model="deviceConfigForm.recordingQuality">
            <el-option label="High" value="high" />
            <el-option label="Medium" value="medium" />
            <el-option label="Low" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="Motion Detection">
          <el-switch v-model="deviceConfigForm.motionDetection" />
        </el-form-item>
        <el-form-item label="Smart Tracking" v-if="selectedDevice?.type === 'PTZ'">
          <el-switch v-model="deviceConfigForm.smartTracking" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="deviceConfigVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveDeviceConfig">Save Changes</el-button>
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
.dahua-platform-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e4e7ed;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  color: #303133;
}

.stat-cards {
  margin: 20px 0;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 10px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
}

.camera-icon {
  background-color: #e6f7ff;
  color: #409eff;
}

.nvr-icon {
  background-color: #f0f9ff;
  color: #67c23a;
}

.record-icon {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.alert-icon {
  background-color: #fef0f0;
  color: #f56c6c;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.stat-sub-value {
  font-size: 12px;
  color: #67c23a;
  margin-top: 2px;
}

.stat-trend {
  margin-top: 8px;
}

.online-rate-text {
  font-size: 12px;
  color: #67c23a;
  margin-left: 8px;
}

.storage-text {
  font-size: 12px;
  color: #e6a23c;
}

.bandwidth-text {
  font-size: 12px;
  color: #409eff;
}

.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  height: 380px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.device-table-card {
  margin-top: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.table-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.video-container {
  background-color: #000;
  border-radius: 8px;
  overflow: hidden;
}

.video-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: linear-gradient(to bottom, rgba(0,0,0,0.7), transparent);
  color: white;
  font-size: 14px;
}

.playback-controls {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  justify-content: center;
}

.playback-container {
  margin-top: 15px;
}

.chart {
  width: 100%;
}

:deep(.el-card__header) {
  border-bottom: 1px solid #ebeef5;
  padding: 15px 20px;
}

:deep(.el-card__body) {
  padding: 20px;
}

@media (max-width: 1200px) {
  .table-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .table-actions {
    width: 100%;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>