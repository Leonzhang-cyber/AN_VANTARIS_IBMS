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
        <div class="loading-tip">NVR / VMS Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="nvr-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>NVR / VMS</h2>
        <p class="header-subtitle">Network Video Recorder | Video Management System</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="handleAddNvr">
          <el-icon><Plus /></el-icon>
          Add NVR
        </el-button>
        <el-button @click="handleExport">
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
            <el-icon :size="28"><Grid /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Total NVRs</div>
            <div class="overview-value">{{ stats.total }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon online">
            <el-icon :size="28"><Link /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Online</div>
            <div class="overview-value">{{ stats.online }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon offline">
            <el-icon :size="28"><Link /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Offline</div>
            <div class="overview-value">{{ stats.offline }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon storage">
            <el-icon :size="28"><Coin /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Total Storage</div>
            <div class="overview-value">{{ stats.totalStorage }} <span class="unit">TB</span></div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- NVR Cards Grid -->
    <div class="section-title">
      <span>NVR Devices</span>
      <div class="filter-group">
        <el-select v-model="statusFilter" size="small" style="width: 120px" placeholder="Status" clearable>
          <el-option label="All" value="all" />
          <el-option label="Online" value="online" />
          <el-option label="Offline" value="offline" />
          <el-option label="Degraded" value="degraded" />
        </el-select>
        <el-input v-model="searchText" placeholder="Search NVR..." style="width: 180px" clearable>
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
    </div>

    <el-row :gutter="20" class="nvrs-row">
      <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="nvr in filteredNvrs" :key="nvr.id">
        <div class="nvr-card" :class="nvr.status">
          <div class="nvr-header">
            <span class="nvr-name">{{ nvr.name }}</span>
            <div class="nvr-status" :class="nvr.status">
              <span class="status-dot"></span>
              {{ getStatusText(nvr.status) }}
            </div>
          </div>
          <div class="nvr-icon">
            <el-icon :size="48"><Monitor /></el-icon>
          </div>
          <div class="nvr-info">
            <div class="info-row">
              <span class="label">Model:</span>
              <span class="value">{{ nvr.model }}</span>
            </div>
            <div class="info-row">
              <span class="label">IP Address:</span>
              <span class="value">{{ nvr.ipAddress }}</span>
            </div>
            <div class="info-row">
              <span class="label">Cameras:</span>
              <span class="value">{{ nvr.cameraCount }} / {{ nvr.maxCameras }}</span>
            </div>
            <div class="info-row">
              <span class="label">Storage:</span>
              <div class="storage-progress">
                <el-progress
                    :percentage="nvr.storageUsedPercent"
                    :color="getStorageColor(nvr.storageUsedPercent)"
                    :stroke-width="6"
                    :show-text="false"
                />
                <span class="storage-text">{{ nvr.storageUsed }} / {{ nvr.storageTotal }} TB</span>
              </div>
            </div>
            <div class="info-row">
              <span class="label">Recording Days:</span>
              <span class="value">{{ nvr.recordingDays }} days</span>
            </div>
            <div class="info-row">
              <span class="label">Health:</span>
              <div class="health-score">
                <el-progress
                    :percentage="nvr.healthScore"
                    :color="getHealthColor(nvr.healthScore)"
                    :stroke-width="6"
                    :show-text="false"
                />
                <span class="health-text">{{ nvr.healthScore }}%</span>
              </div>
            </div>
          </div>
          <div class="nvr-footer">
            <el-button type="primary" link size="small" @click="viewNvrDetails(nvr)">
              Details
            </el-button>
            <el-button type="success" link size="small" @click="remoteAccess(nvr)">
              Remote Access
            </el-button>
            <el-button type="danger" link size="small" @click="rebootNvr(nvr)" v-if="nvr.status === 'online'">
              Reboot
            </el-button>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Storage & Performance Charts -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :md="14">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Storage Usage Trend (Last 30 Days)</span>
              <el-radio-group v-model="chartPeriod" size="small" @change="updateTrendChart">
                <el-radio-button label="week">Weekly</el-radio-button>
                <el-radio-button label="month">Monthly</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="10">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Bandwidth Usage</span>
            </div>
          </template>
          <div ref="bandwidthChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Recording Schedule Table -->
    <el-card shadow="hover" class="schedule-card">
      <template #header>
        <div class="card-header">
          <span>Recording Schedule</span>
          <el-button type="primary" link @click="editSchedule">
            <el-icon><Edit /></el-icon>
            Edit Schedule
          </el-button>
        </div>
      </template>
      <el-table :data="recordingSchedule" stripe border style="width: 100%">
        <el-table-column prop="timeSlot" label="Time Slot" width="120" />
        <el-table-column prop="monday" label="Monday" width="100">
          <template #default="{ row }">
            <el-tag :type="getRecordingTypeTag(row.monday)" size="small">{{ row.monday }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tuesday" label="Tuesday" width="100">
          <template #default="{ row }">
            <el-tag :type="getRecordingTypeTag(row.tuesday)" size="small">{{ row.tuesday }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="wednesday" label="Wednesday" width="100">
          <template #default="{ row }">
            <el-tag :type="getRecordingTypeTag(row.wednesday)" size="small">{{ row.wednesday }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="thursday" label="Thursday" width="100">
          <template #default="{ row }">
            <el-tag :type="getRecordingTypeTag(row.thursday)" size="small">{{ row.thursday }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="friday" label="Friday" width="100">
          <template #default="{ row }">
            <el-tag :type="getRecordingTypeTag(row.friday)" size="small">{{ row.friday }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="saturday" label="Saturday" width="100">
          <template #default="{ row }">
            <el-tag :type="getRecordingTypeTag(row.saturday)" size="small">{{ row.saturday }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sunday" label="Sunday" width="100">
          <template #default="{ row }">
            <el-tag :type="getRecordingTypeTag(row.sunday)" size="small">{{ row.sunday }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- NVR Details Table -->
    <el-card shadow="hover" class="table-card">
      <template #header>
        <div class="card-header">
          <span>NVR Details</span>
        </div>
      </template>
      <el-table :data="paginatedNvrs" stripe border style="width: 100%">
        <el-table-column prop="name" label="NVR Name" min-width="100" />
        <el-table-column prop="model" label="Model" width="140" />
        <el-table-column prop="ipAddress" label="IP Address" width="140" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="cameraCount" label="Cameras" width="100" sortable>
          <template #default="{ row }">{{ row.cameraCount }} / {{ row.maxCameras }}</template>
        </el-table-column>
        <el-table-column prop="storageUsed" label="Storage Used" width="120" sortable>
          <template #default="{ row }">{{ row.storageUsed }} / {{ row.storageTotal }} TB</template>
        </el-table-column>
        <el-table-column prop="storageUsedPercent" label="Usage" width="130" sortable>
          <template #default="{ row }">
            <el-progress :percentage="row.storageUsedPercent" :color="getStorageColor(row.storageUsedPercent)" :stroke-width="6" />
          </template>
        </el-table-column>
        <el-table-column prop="recordingDays" label="Recording Days" width="110" sortable />
        <el-table-column prop="firmwareVersion" label="Firmware" width="120" />
        <el-table-column label="Actions" fixed="right" width="200">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewNvrDetails(row)">
              Details
            </el-button>
            <el-button type="danger" link size="small" @click="rebootNvr(row)">
              Reboot
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredNvrs.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Add NVR Dialog -->
    <el-dialog v-model="dialogVisible" title="Add NVR" width="500px">
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
        <el-form-item label="NVR Name" prop="name">
          <el-input v-model="formData.name" placeholder="Enter NVR name" />
        </el-form-item>
        <el-form-item label="Model" prop="model">
          <el-select v-model="formData.model" placeholder="Select model" style="width: 100%">
            <el-option label="Hikvision DS-9632NI-I8" value="Hikvision DS-9632NI-I8" />
            <el-option label="Dahua NVR5864-4KS2" value="Dahua NVR5864-4KS2" />
            <el-option label="Uniview NVR308-64E" value="Uniview NVR308-64E" />
            <el-option label="AXIS S2216" value="AXIS S2216" />
          </el-select>
        </el-form-item>
        <el-form-item label="IP Address" prop="ipAddress">
          <el-input v-model="formData.ipAddress" placeholder="192.168.1.100" />
        </el-form-item>
        <el-form-item label="Storage Capacity (TB)" prop="storageTotal">
          <el-input-number v-model="formData.storageTotal" :min="1" :max="256" :step="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Max Cameras" prop="maxCameras">
          <el-input-number v-model="formData.maxCameras" :min="16" :max="256" :step="16" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitNvr">Add NVR</el-button>
      </template>
    </el-dialog>

    <!-- NVR Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`NVR Details - ${selectedNvr?.name}`" width="650px">
      <el-descriptions :column="2" border v-if="selectedNvr">
        <el-descriptions-item label="NVR Name">{{ selectedNvr.name }}</el-descriptions-item>
        <el-descriptions-item label="Model">{{ selectedNvr.model }}</el-descriptions-item>
        <el-descriptions-item label="Serial Number">{{ selectedNvr.serialNumber }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusTag(selectedNvr.status)">{{ getStatusText(selectedNvr.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="IP Address">{{ selectedNvr.ipAddress }}</el-descriptions-item>
        <el-descriptions-item label="MAC Address">{{ selectedNvr.macAddress }}</el-descriptions-item>
        <el-descriptions-item label="Firmware Version">{{ selectedNvr.firmwareVersion }}</el-descriptions-item>
        <el-descriptions-item label="Cameras">{{ selectedNvr.cameraCount }} / {{ selectedNvr.maxCameras }}</el-descriptions-item>
        <el-descriptions-item label="Storage">{{ selectedNvr.storageUsed }} / {{ selectedNvr.storageTotal }} TB</el-descriptions-item>
        <el-descriptions-item label="Recording Days">{{ selectedNvr.recordingDays }} days</el-descriptions-item>
        <el-descriptions-item label="Health Score">{{ selectedNvr.healthScore }}%</el-descriptions-item>
        <el-descriptions-item label="CPU Usage">{{ selectedNvr.cpuUsage }}%</el-descriptions-item>
        <el-descriptions-item label="Memory Usage">{{ selectedNvr.memoryUsage }}%</el-descriptions-item>
        <el-descriptions-item label="Network Load">{{ selectedNvr.networkLoad }} Mbps</el-descriptions-item>
        <el-descriptions-item label="Last Reboot">{{ selectedNvr.lastReboot }}</el-descriptions-item>
        <el-descriptions-item label="Uptime">{{ selectedNvr.uptime }}</el-descriptions-item>
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
  Plus,
  Grid,
  Link,
  Coin,
  Monitor,
  Search,
  Edit
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Initializing NVR systems...',
  'Checking recording status...',
  'Almost ready...'
]

// ==================== Data State ====================
const chartPeriod = ref('week')
const statusFilter = ref('all')
const searchText = ref('')

interface Nvr {
  id: number
  name: string
  model: string
  serialNumber: string
  ipAddress: string
  macAddress: string
  status: 'online' | 'offline' | 'degraded'
  cameraCount: number
  maxCameras: number
  storageTotal: number
  storageUsed: number
  storageUsedPercent: number
  recordingDays: number
  healthScore: number
  cpuUsage: number
  memoryUsage: number
  networkLoad: number
  firmwareVersion: string
  lastReboot: string
  uptime: string
}

const nvrs = ref<Nvr[]>([])
const recordingSchedule = ref([
  { timeSlot: '00:00 - 06:00', monday: 'Continuous', tuesday: 'Continuous', wednesday: 'Continuous', thursday: 'Continuous', friday: 'Continuous', saturday: 'Motion', sunday: 'Motion' },
  { timeSlot: '06:00 - 18:00', monday: 'Continuous', tuesday: 'Continuous', wednesday: 'Continuous', thursday: 'Continuous', friday: 'Continuous', saturday: 'Motion', sunday: 'Motion' },
  { timeSlot: '18:00 - 00:00', monday: 'Continuous', tuesday: 'Continuous', wednesday: 'Continuous', thursday: 'Continuous', friday: 'Continuous', saturday: 'Motion', sunday: 'Motion' }
])

const stats = computed(() => ({
  total: nvrs.value.length,
  online: nvrs.value.filter(n => n.status === 'online').length,
  offline: nvrs.value.filter(n => n.status === 'offline').length,
  totalStorage: nvrs.value.reduce((sum, n) => sum + n.storageTotal, 0).toFixed(1)
}))

const filteredNvrs = computed(() => {
  let filtered = nvrs.value
  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(n => n.status === statusFilter.value)
  }
  if (searchText.value) {
    filtered = filtered.filter(n =>
        n.name.toLowerCase().includes(searchText.value.toLowerCase()) ||
        n.ipAddress.includes(searchText.value)
    )
  }
  return filtered
})

const pagination = ref({ currentPage: 1, pageSize: 10 })
const paginatedNvrs = computed(() => {
  const start = (pagination.value.currentPage - 1) * pagination.value.pageSize
  return filteredNvrs.value.slice(start, start + pagination.value.pageSize)
})

// Generate mock NVRs
const generateNvrs = (): Nvr[] => {
  const nvrData = [
    { name: 'Main NVR-01', model: 'Hikvision DS-9632NI-I8', ip: '192.168.1.100', mac: '00:1A:2B:3C:4D:5E', cameras: 28, max: 32, storageTotal: 48 },
    { name: 'Main NVR-02', model: 'Dahua NVR5864-4KS2', ip: '192.168.1.101', mac: '00:1A:2B:3C:4D:5F', cameras: 24, max: 32, storageTotal: 48 },
    { name: 'Building B NVR', model: 'Uniview NVR308-64E', ip: '192.168.1.102', mac: '00:1A:2B:3C:4D:60', cameras: 48, max: 64, storageTotal: 96 },
    { name: 'Parking NVR', model: 'AXIS S2216', ip: '192.168.1.103', mac: '00:1A:2B:3C:4D:61', cameras: 14, max: 16, storageTotal: 24 }
  ]

  return nvrData.map((n, idx) => {
    const storageUsed = parseFloat((n.storageTotal * (0.5 + Math.random() * 0.3)).toFixed(1))
    const storageUsedPercent = Math.floor((storageUsed / n.storageTotal) * 100)
    const healthScore = Math.floor(70 + Math.random() * 25)
    const statuses: ('online' | 'offline' | 'degraded')[] = ['online', 'online', 'online', 'degraded']

    return {
      id: idx + 1,
      name: n.name,
      model: n.model,
      serialNumber: `SN-${n.ip.replace(/\./g, '')}-${idx}`,
      ipAddress: n.ip,
      macAddress: n.mac,
      status: statuses[idx],
      cameraCount: n.cameras,
      maxCameras: n.max,
      storageTotal: n.storageTotal,
      storageUsed: storageUsed,
      storageUsedPercent: storageUsedPercent,
      recordingDays: Math.floor(14 + Math.random() * 21),
      healthScore: healthScore,
      cpuUsage: Math.floor(20 + Math.random() * 40),
      memoryUsage: Math.floor(30 + Math.random() * 40),
      networkLoad: Math.floor(50 + Math.random() * 150),
      firmwareVersion: `v${Math.floor(3 + Math.random() * 2)}.${Math.floor(0 + Math.random() * 5)}.${Math.floor(0 + Math.random() * 10)}`,
      lastReboot: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toLocaleString(),
      uptime: `${Math.floor(7 + Math.random() * 30)} days`
    }
  })
}

// Helper functions
const getStatusText = (status: string) => {
  const map: Record<string, string> = { online: 'Online', offline: 'Offline', degraded: 'Degraded' }
  return map[status] || status
}

const getStatusTag = (status: string) => {
  const map: Record<string, string> = { online: 'success', offline: 'info', degraded: 'warning' }
  return map[status] || 'info'
}

const getStorageColor = (percent: number) => {
  if (percent < 70) return '#67C23A'
  if (percent < 85) return '#E6A23C'
  return '#F56C6C'
}

const getHealthColor = (score: number) => {
  if (score >= 80) return '#67C23A'
  if (score >= 60) return '#E6A23C'
  return '#F56C6C'
}

const getRecordingTypeTag = (type: string) => {
  const map: Record<string, string> = { Continuous: 'danger', Motion: 'warning', 'Event Only': 'info', None: 'info' }
  return map[type] || 'info'
}

// Actions
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const formRef = ref()
const selectedNvr = ref<Nvr | null>(null)

const formData = ref({
  name: '',
  model: '',
  ipAddress: '',
  storageTotal: 48,
  maxCameras: 32
})

const formRules = {
  name: [{ required: true, message: 'Please enter NVR name', trigger: 'blur' }],
  model: [{ required: true, message: 'Please select model', trigger: 'change' }],
  ipAddress: [{ required: true, message: 'Please enter IP address', trigger: 'blur' }]
}

const handleAddNvr = () => {
  formData.value = { name: '', model: '', ipAddress: '', storageTotal: 48, maxCameras: 32 }
  dialogVisible.value = true
}

const submitNvr = async () => {
  try {
    await formRef.value?.validate()

    const newNvr: Nvr = {
      id: nvrs.value.length + 1,
      name: formData.value.name,
      model: formData.value.model,
      serialNumber: `SN-${Date.now()}`,
      ipAddress: formData.value.ipAddress,
      macAddress: '00:00:00:00:00:00',
      status: 'offline',
      cameraCount: 0,
      maxCameras: formData.value.maxCameras,
      storageTotal: formData.value.storageTotal,
      storageUsed: 0,
      storageUsedPercent: 0,
      recordingDays: 0,
      healthScore: 100,
      cpuUsage: 0,
      memoryUsage: 0,
      networkLoad: 0,
      firmwareVersion: 'v1.0.0',
      lastReboot: 'Never',
      uptime: '0 days'
    }

    nvrs.value.push(newNvr)
    dialogVisible.value = false
    ElMessage.success('NVR added successfully')
  } catch (error) {
    ElMessage.error('Please fill all required fields')
  }
}

const viewNvrDetails = (nvr: Nvr) => {
  selectedNvr.value = nvr
  detailDialogVisible.value = true
}

const remoteAccess = (nvr: Nvr) => {
  window.open(`http://${nvr.ipAddress}`, '_blank')
  ElMessage.info(`Opening remote access to ${nvr.name}`)
}

const rebootNvr = (nvr: Nvr) => {
  ElMessageBox.confirm(`Reboot NVR "${nvr.name}"?`, 'Confirm', {
    confirmButtonText: 'Reboot',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    ElMessage.info(`Rebooting ${nvr.name}...`)
    setTimeout(() => {
      nvr.status = 'offline'
      ElMessage.success(`${nvr.name} rebooted successfully`)
      setTimeout(() => {
        nvr.status = 'online'
      }, 30000)
    }, 3000)
  }).catch(() => {})
}

const editSchedule = () => {
  ElMessage.info('Schedule editing feature coming soon')
}

// ==================== Chart Functions ====================
const trendChartRef = ref<HTMLElement>()
const bandwidthChartRef = ref<HTMLElement>()

let trendChart: echarts.ECharts | null = null
let bandwidthChart: echarts.ECharts | null = null

const initCharts = () => {
  nextTick(() => {
    if (trendChartRef.value) {
      if (trendChart) trendChart.dispose()
      trendChart = echarts.init(trendChartRef.value)
      updateTrendChart()
    }

    if (bandwidthChartRef.value) {
      if (bandwidthChart) bandwidthChart.dispose()
      bandwidthChart = echarts.init(bandwidthChartRef.value)
      updateBandwidthChart()
    }
  })
}

const updateTrendChart = () => {
  let storageData: number[] = []
  let xAxisData: string[] = []

  if (chartPeriod.value === 'week') {
    xAxisData = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    storageData = [42, 44, 46, 45, 47, 48, 49]
  } else {
    xAxisData = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    storageData = [42, 44, 46, 48]
  }

  trendChart?.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: { type: 'value', name: 'Storage Used (TB)' },
    series: [{
      type: 'line',
      data: storageData,
      smooth: true,
      lineStyle: { color: '#409EFF', width: 3 },
      areaStyle: { opacity: 0.1 },
      symbol: 'circle',
      symbolSize: 8
    }]
  })
}

const updateBandwidthChart = () => {
  const nvrNames = nvrs.value.map(n => n.name)
  const bandwidthData = nvrs.value.map(n => n.networkLoad)

  bandwidthChart?.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'category', data: nvrNames, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'Bandwidth (Mbps)' },
    series: [{
      type: 'bar',
      data: bandwidthData,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value > 120) return '#F56C6C'
          if (value > 80) return '#E6A23C'
          return '#67C23A'
        }
      },
      label: { show: true, position: 'top', formatter: '{c} Mbps' }
    }]
  })
}

// ==================== Actions ====================
const refreshData = () => {
  nvrs.value = generateNvrs()
  updateBandwidthChart()
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
      nvrs.value = generateNvrs()
      initCharts()
    }, 400)
  }, 2000)
})

watch([trendChartRef, bandwidthChartRef], () => {
  window.addEventListener('resize', () => {
    trendChart?.resize()
    bandwidthChart?.resize()
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
.nvr-container {
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
.overview-icon.online { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
.overview-icon.offline { background: rgba(144, 147, 153, 0.1); color: #909399; }
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

/* Section Title */
.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title span {
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

.filter-group {
  display: flex;
  gap: 12px;
}

/* NVR Cards */
.nvrs-row {
  margin-bottom: 20px;
}

.nvr-card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.3s ease;
  border-top: 3px solid #67C23A;
}

.nvr-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(0,0,0,0.12);
}

.nvr-card.online { border-top-color: #67C23A; }
.nvr-card.offline { border-top-color: #909399; }
.nvr-card.degraded { border-top-color: #E6A23C; }

.nvr-header {
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

.nvr-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 20px;
}

.nvr-status.online { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
.nvr-status.offline { background: rgba(144, 147, 153, 0.1); color: #909399; }
.nvr-status.degraded { background: rgba(230, 162, 60, 0.1); color: #E6A23C; }

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.nvr-icon {
  text-align: center;
  margin: 12px 0;
  color: #409EFF;
}

.nvr-info {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 12px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  font-size: 13px;
  border-bottom: 1px solid #e4e7ed;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label { color: #909399; }
.info-row .value { font-weight: 500; color: #606266; }

.storage-progress {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: flex-end;
}

.storage-progress .el-progress {
  width: 100px;
}

.storage-text {
  font-size: 11px;
  color: #909399;
}

.health-score {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: flex-end;
}

.health-score .el-progress {
  width: 100px;
}

.health-text {
  font-size: 11px;
  font-weight: 500;
}

.nvr-footer {
  display: flex;
  justify-content: space-around;
  gap: 8px;
}

/* Charts */
.charts-row {
  margin-bottom: 20px;
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

/* Schedule Card */
.schedule-card {
  border-radius: 16px;
  margin-bottom: 20px;
}

/* Table */
.table-card {
  border-radius: 16px;
}

.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>