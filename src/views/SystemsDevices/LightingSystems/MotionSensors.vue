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
        <div class="loading-tip">Motion Sensors Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="motion-sensors-container">
    <!-- Page Header -->
    <div class="page-header">
      <h2>Motion Sensors</h2>
      <div class="header-actions">
        <el-button type="primary" @click="handleAddSensor">
          <el-icon><Plus /></el-icon>
          Add Sensor
        </el-button>
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">Total Sensors</div>
              <div class="stat-value">{{ stats.total }}</div>
            </div>
            <div class="stat-icon total">
              <el-icon><Grid /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">Online</div>
              <div class="stat-value online">{{ stats.online }}</div>
            </div>
            <div class="stat-icon online-bg">
              <el-icon><Link /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">Offline</div>
              <div class="stat-value offline">{{ stats.offline }}</div>
            </div>
            <div class="stat-icon offline-bg">
              <el-icon><Link /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">Avg Detection (today)</div>
              <div class="stat-value detection">{{ stats.avgDetection }}</div>
            </div>
            <div class="stat-icon detection-bg">
              <el-icon><View /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Charts Row -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :md="16">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Motion Detection Trend (Last 7 Days)</span>
              <el-button text @click="refreshChart">Refresh</el-button>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="8">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Sensor Status Distribution</span>
            </div>
          </template>
          <div ref="statusChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Filters -->
    <el-card shadow="hover" class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="Sensor Name">
          <el-input v-model="filters.sensorName" placeholder="Search by name" clearable />
        </el-form-item>
        <el-form-item label="Location">
          <el-select v-model="filters.location" placeholder="All Locations" clearable>
            <el-option v-for="loc in locationOptions" :key="loc" :label="loc" :value="loc" />
          </el-select>
        </el-form-item>
        <el-form-item label="Status">
          <el-select v-model="filters.status" placeholder="All Status" clearable>
            <el-option label="Online" value="online" />
            <el-option label="Offline" value="offline" />
            <el-option label="Maintenance" value="maintenance" />
            <el-option label="Fault" value="fault" />
          </el-select>
        </el-form-item>
        <el-form-item label="Sensor Type">
          <el-select v-model="filters.sensorType" placeholder="All Types" clearable>
            <el-option label="PIR" value="PIR" />
            <el-option label="Microwave" value="Microwave" />
            <el-option label="Ultrasonic" value="Ultrasonic" />
            <el-option label="Dual Tech" value="Dual Tech" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            Search
          </el-button>
          <el-button @click="resetFilters">Reset</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Data Table -->
    <el-card shadow="hover" class="table-card">
      <template #header>
        <div class="card-header">
          <span>Motion Sensors List</span>
          <el-button text @click="toggleFullscreen">
            <el-icon><FullScreen /></el-icon>
          </el-button>
        </div>
      </template>

      <el-table :data="paginatedSensors" stripe border style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="name" label="Sensor Name" min-width="150" />
        <el-table-column prop="location" label="Location" min-width="120" />
        <el-table-column prop="zone" label="Zone" min-width="100" />
        <el-table-column prop="sensorType" label="Sensor Type" min-width="120">
          <template #default="{ row }">
            <el-tag :type="getSensorTypeTag(row.sensorType)">{{ row.sensorType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" min-width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">
              <el-icon v-if="row.status === 'online'"><Link /></el-icon>
              <el-icon v-else-if="row.status === 'offline'"><Link /></el-icon>
              <el-icon v-else-if="row.status === 'fault'"><WarningFilled /></el-icon>
              <el-icon v-else><Tools /></el-icon>
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="batteryLevel" label="Battery Level" min-width="130" sortable>
          <template #default="{ row }">
            <span>{{ row.batteryLevel }}%</span>
            <el-progress :percentage="row.batteryLevel" :stroke-width="6" :color="getBatteryColor(row.batteryLevel)" />
          </template>
        </el-table-column>
        <el-table-column prop="detectionCount" label="Detections Today" min-width="140" sortable>
          <template #default="{ row }">{{ row.detectionCount }}</template>
        </el-table-column>
        <el-table-column prop="signalStrength" label="Signal" min-width="120" sortable>
          <template #default="{ row }">
            <el-tag :type="getSignalTag(row.signalStrength)" size="small">
              {{ getSignalText(row.signalStrength) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastDetection" label="Last Detection" min-width="170" sortable />
        <el-table-column prop="lastUpdated" label="Last Updated" min-width="170" sortable />
        <el-table-column label="Actions" fixed="right" min-width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewDetails(row)">
              <el-icon><View /></el-icon>
              View
            </el-button>
            <el-button type="success" link @click="controlSensor(row)">
              <el-icon><Operation /></el-icon>
              Control
            </el-button>
            <el-button type="danger" link @click="confirmDelete(row)">
              <el-icon><Delete /></el-icon>
              Delete
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="filteredSensors.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Add/Edit Sensor Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
        <el-form-item label="Sensor Name" prop="name">
          <el-input v-model="formData.name" placeholder="Enter sensor name" />
        </el-form-item>
        <el-form-item label="Location" prop="location">
          <el-select v-model="formData.location" placeholder="Select location" style="width: 100%">
            <el-option v-for="loc in locationOptions" :key="loc" :label="loc" :value="loc" />
          </el-select>
        </el-form-item>
        <el-form-item label="Zone" prop="zone">
          <el-input v-model="formData.zone" placeholder="Enter zone" />
        </el-form-item>
        <el-form-item label="Sensor Type" prop="sensorType">
          <el-select v-model="formData.sensorType" placeholder="Select type" style="width: 100%">
            <el-option label="PIR" value="PIR" />
            <el-option label="Microwave" value="Microwave" />
            <el-option label="Ultrasonic" value="Ultrasonic" />
            <el-option label="Dual Tech" value="Dual Tech" />
          </el-select>
        </el-form-item>
        <el-form-item label="Battery Capacity" prop="batteryCapacity">
          <el-input-number v-model="formData.batteryCapacity" :min="0" :max="100" :step="1" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitForm">Confirm</el-button>
      </template>
    </el-dialog>

    <!-- Control Dialog -->
    <el-dialog v-model="controlDialogVisible" title="Sensor Control" width="450px">
      <div class="control-content" v-if="selectedSensor">
        <div class="current-status">
          <span>Current Status:</span>
          <el-tag :type="getStatusTag(selectedSensor.status)" size="large">
            {{ getStatusText(selectedSensor.status) }}
          </el-tag>
        </div>
        <el-divider />
        <div class="sensor-info">
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="Battery Level">{{ selectedSensor.batteryLevel }}%</el-descriptions-item>
            <el-descriptions-item label="Signal Strength">{{ getSignalText(selectedSensor.signalStrength) }}</el-descriptions-item>
            <el-descriptions-item label="Detections Today">{{ selectedSensor.detectionCount }}</el-descriptions-item>
          </el-descriptions>
        </div>
        <el-divider />
        <div class="control-buttons">
          <el-button type="success" @click="sendCommand('calibrate')">
            <el-icon><RefreshRight /></el-icon>
            Calibrate
          </el-button>
          <el-button type="warning" @click="sendCommand('test')">
            <el-icon><View /></el-icon>
            Test Mode
          </el-button>
          <el-button type="danger" @click="sendCommand('reset')">
            <el-icon><Refresh /></el-icon>
            Reset
          </el-button>
        </div>
        <el-divider />
        <div class="sensitivity-control">
          <span>Sensitivity:</span>
          <el-slider v-model="sensitivityLevel" :min="0" :max="100" @change="sendSensitivityCommand" />
          <span class="sensitivity-value">{{ sensitivityLevel }}%</span>
        </div>
      </div>
    </el-dialog>

    <!-- Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" title="Sensor Details" width="700px">
      <el-descriptions :column="2" border v-if="selectedSensor">
        <el-descriptions-item label="Sensor Name">{{ selectedSensor.name }}</el-descriptions-item>
        <el-descriptions-item label="Location">{{ selectedSensor.location }}</el-descriptions-item>
        <el-descriptions-item label="Zone">{{ selectedSensor.zone }}</el-descriptions-item>
        <el-descriptions-item label="Sensor Type">{{ selectedSensor.sensorType }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusTag(selectedSensor.status)">{{ getStatusText(selectedSensor.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Battery Level">
          <span>{{ selectedSensor.batteryLevel }}%</span>
          <el-progress :percentage="selectedSensor.batteryLevel" :stroke-width="8" style="margin-top: 8px;" />
        </el-descriptions-item>
        <el-descriptions-item label="Signal Strength">
          <el-tag :type="getSignalTag(selectedSensor.signalStrength)">{{ getSignalText(selectedSensor.signalStrength) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Sensitivity">{{ selectedSensor.sensitivity }}%</el-descriptions-item>
        <el-descriptions-item label="Detection Range">{{ selectedSensor.detectionRange }} m</el-descriptions-item>
        <el-descriptions-item label="Detection Angle">{{ selectedSensor.detectionAngle }}°</el-descriptions-item>
        <el-descriptions-item label="Detections Today">{{ selectedSensor.detectionCount }}</el-descriptions-item>
        <el-descriptions-item label="Detections Week">{{ selectedSensor.detectionWeek }}</el-descriptions-item>
        <el-descriptions-item label="Last Detection">{{ selectedSensor.lastDetection }}</el-descriptions-item>
        <el-descriptions-item label="Last Updated">{{ selectedSensor.lastUpdated }}</el-descriptions-item>
        <el-descriptions-item label="Installation Date" :span="2">{{ selectedSensor.installDate }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus,
  Download,
  Refresh,
  Grid,
  Link,
  View,
  Search,
  FullScreen,
  Operation,
  Delete,
  WarningFilled,
  Tools,
  RefreshRight
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing...',
  'Almost ready...'
]

// ==================== Data State ====================
const tableLoading = ref(false)
const stats = ref({
  total: 0,
  online: 0,
  offline: 0,
  avgDetection: 0
})

// Mock Sensor Data
interface MotionSensor {
  id: number
  name: string
  location: string
  zone: string
  sensorType: string
  status: 'online' | 'offline' | 'maintenance' | 'fault'
  batteryLevel: number
  signalStrength: number
  sensitivity: number
  detectionRange: number
  detectionAngle: number
  detectionCount: number
  detectionWeek: number
  lastDetection: string
  lastUpdated: string
  installDate: string
}

const sensors = ref<MotionSensor[]>([])

// Options for filters
const locationOptions = ref<string[]>([])

// Generate mock data
const generateMockData = (): MotionSensor[] => {
  const locations = ['Building A', 'Building B', 'Building C', 'Warehouse', 'Lobby', 'Corridor East', 'Corridor West']
  const zones = ['Floor 1', 'Floor 2', 'Floor 3', 'Ground Floor', 'Entrance', 'Meeting Room A', 'Meeting Room B', 'Office Area']
  const sensorTypes = ['PIR', 'Microwave', 'Ultrasonic', 'Dual Tech']
  const statuses: ('online' | 'offline' | 'maintenance' | 'fault')[] = ['online', 'online', 'online', 'online', 'offline', 'maintenance', 'fault']

  const data: MotionSensor[] = []
  for (let i = 1; i <= 32; i++) {
    const batteryLevel = Math.floor(Math.random() * 100)
    const signalStrength = 40 + Math.floor(Math.random() * 60)
    const sensitivity = 50 + Math.floor(Math.random() * 50)
    const detectionCount = Math.floor(Math.random() * 200)
    const detectionWeek = detectionCount * 5 + Math.floor(Math.random() * 100)

    data.push({
      id: i,
      name: `MS-${String(i).padStart(3, '0')}`,
      location: locations[Math.floor(Math.random() * locations.length)],
      zone: zones[Math.floor(Math.random() * zones.length)],
      sensorType: sensorTypes[Math.floor(Math.random() * sensorTypes.length)],
      status: statuses[Math.floor(Math.random() * statuses.length)],
      batteryLevel: batteryLevel,
      signalStrength: signalStrength,
      sensitivity: sensitivity,
      detectionRange: parseFloat((5 + Math.random() * 10).toFixed(1)),
      detectionAngle: [90, 180, 360][Math.floor(Math.random() * 3)],
      detectionCount: detectionCount,
      detectionWeek: detectionWeek,
      lastDetection: new Date(Date.now() - Math.random() * 60 * 60 * 1000).toLocaleString(),
      lastUpdated: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toLocaleString(),
      installDate: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toLocaleDateString()
    })
  }
  return data
}

// Update location options
const updateLocationOptions = () => {
  const locations = new Set(sensors.value.map(s => s.location))
  locationOptions.value = Array.from(locations).sort()
}

// Filters
const filters = ref({
  sensorName: '',
  location: '',
  status: '',
  sensorType: ''
})

// Pagination
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// Filtered sensors
const filteredSensors = computed(() => {
  let filtered = sensors.value

  if (filters.value.sensorName) {
    filtered = filtered.filter(s => s.name.toLowerCase().includes(filters.value.sensorName.toLowerCase()))
  }
  if (filters.value.location) {
    filtered = filtered.filter(s => s.location === filters.value.location)
  }
  if (filters.value.status) {
    filtered = filtered.filter(s => s.status === filters.value.status)
  }
  if (filters.value.sensorType) {
    filtered = filtered.filter(s => s.sensorType === filters.value.sensorType)
  }

  return filtered
})

// Paginated sensors
const paginatedSensors = computed(() => {
  const start = (pagination.value.currentPage - 1) * pagination.value.pageSize
  const end = start + pagination.value.pageSize
  return filteredSensors.value.slice(start, end)
})

// Update stats
const updateStats = () => {
  stats.value.total = sensors.value.length
  stats.value.online = sensors.value.filter(s => s.status === 'online').length
  stats.value.offline = sensors.value.filter(s => s.status === 'offline').length

  const totalDetections = sensors.value.reduce((sum, s) => sum + s.detectionCount, 0)
  stats.value.avgDetection = sensors.value.length > 0 ? Math.round(totalDetections / sensors.value.length) : 0
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
      trendChart.setOption({
        tooltip: { trigger: 'axis' },
        legend: { data: ['Detections', 'Active Sensors'] },
        xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
        yAxis: [{ type: 'value', name: 'Detections' }, { type: 'value', name: 'Active Sensors' }],
        series: [
          {
            name: 'Detections',
            type: 'line',
            data: [1240, 1350, 1280, 1420, 1560, 1680, 1320],
            smooth: true,
            lineStyle: { color: '#409EFF', width: 3 },
            areaStyle: { opacity: 0.1 }
          },
          {
            name: 'Active Sensors',
            type: 'bar',
            data: [28, 29, 28, 30, 29, 27, 26],
            itemStyle: { borderRadius: [4, 4, 0, 0], color: '#67C23A' }
          }
        ]
      })
    }

    if (statusChartRef.value) {
      if (statusChart) statusChart.dispose()
      statusChart = echarts.init(statusChartRef.value)
      statusChart.setOption({
        tooltip: { trigger: 'item' },
        legend: { orient: 'vertical', left: 'left' },
        series: [{
          type: 'pie',
          radius: '55%',
          data: [
            { value: stats.value.online, name: 'Online', itemStyle: { color: '#67C23A' } },
            { value: stats.value.offline, name: 'Offline', itemStyle: { color: '#909399' } },
            { value: sensors.value.filter(s => s.status === 'maintenance').length, name: 'Maintenance', itemStyle: { color: '#E6A23C' } },
            { value: sensors.value.filter(s => s.status === 'fault').length, name: 'Fault', itemStyle: { color: '#F56C6C' } }
          ],
          emphasis: { scale: true },
          label: { show: true, formatter: '{b}: {d}%' }
        }]
      })
    }
  })
}

const refreshChart = () => {
  if (trendChart) {
    trendChart.setOption({
      series: [
        { data: [1240 + Math.random() * 200, 1350 + Math.random() * 200, 1280 + Math.random() * 200, 1420 + Math.random() * 200, 1560 + Math.random() * 200, 1680 + Math.random() * 200, 1320 + Math.random() * 200] },
        { data: [28 + Math.floor(Math.random() * 3), 29 + Math.floor(Math.random() * 3), 28 + Math.floor(Math.random() * 3), 30 + Math.floor(Math.random() * 3), 29 + Math.floor(Math.random() * 3), 27 + Math.floor(Math.random() * 3), 26 + Math.floor(Math.random() * 3)] }
      ]
    })
  }
  ElMessage.success('Chart data refreshed')
}

// ==================== CRUD Operations ====================
const dialogVisible = ref(false)
const dialogTitle = ref('Add Sensor')
const formRef = ref()
const formData = ref({
  name: '',
  location: '',
  zone: '',
  sensorType: '',
  batteryCapacity: 100
})

const formRules = {
  name: [{ required: true, message: 'Please enter sensor name', trigger: 'blur' }],
  location: [{ required: true, message: 'Please select location', trigger: 'change' }],
  zone: [{ required: true, message: 'Please enter zone', trigger: 'blur' }],
  sensorType: [{ required: true, message: 'Please select sensor type', trigger: 'change' }]
}

const handleAddSensor = () => {
  dialogTitle.value = 'Add Sensor'
  formData.value = { name: '', location: '', zone: '', sensorType: '', batteryCapacity: 100 }
  dialogVisible.value = true
}

const submitForm = async () => {
  try {
    await formRef.value?.validate()

    const newSensor: MotionSensor = {
      id: sensors.value.length + 1,
      name: formData.value.name,
      location: formData.value.location,
      zone: formData.value.zone,
      sensorType: formData.value.sensorType,
      status: 'online',
      batteryLevel: formData.value.batteryCapacity,
      signalStrength: 75,
      sensitivity: 70,
      detectionRange: 8,
      detectionAngle: 180,
      detectionCount: 0,
      detectionWeek: 0,
      lastDetection: new Date().toLocaleString(),
      lastUpdated: new Date().toLocaleString(),
      installDate: new Date().toLocaleDateString()
    }

    sensors.value.push(newSensor)
    updateStats()
    updateLocationOptions()
    initCharts()
    dialogVisible.value = false
    ElMessage.success('Sensor added successfully')
  } catch (error) {
    ElMessage.error('Please fill in all required fields')
  }
}

const confirmDelete = (row: MotionSensor) => {
  ElMessageBox.confirm(`Are you sure to delete sensor "${row.name}"?`, 'Warning', {
    confirmButtonText: 'Confirm',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = sensors.value.findIndex(s => s.id === row.id)
    if (index > -1) {
      sensors.value.splice(index, 1)
      updateStats()
      updateLocationOptions()
      initCharts()
      ElMessage.success('Sensor deleted successfully')
    }
  }).catch(() => {})
}

// ==================== Sensor Control ====================
const controlDialogVisible = ref(false)
const selectedSensor = ref<MotionSensor | null>(null)
const sensitivityLevel = ref(70)

const controlSensor = (row: MotionSensor) => {
  selectedSensor.value = row
  sensitivityLevel.value = row.sensitivity
  controlDialogVisible.value = true
}

const sendCommand = (command: string) => {
  if (!selectedSensor.value) return

  tableLoading.value = true
  setTimeout(() => {
    if (command === 'calibrate') {
      ElMessage.info('Calibration in progress...')
      setTimeout(() => {
        selectedSensor.value!.sensitivity = 70
        selectedSensor.value!.lastUpdated = new Date().toLocaleString()
        ElMessage.success('Sensor calibrated successfully')
      }, 1500)
    } else if (command === 'test') {
      ElMessage.info('Test mode activated for 30 seconds')
      selectedSensor.value!.lastUpdated = new Date().toLocaleString()
    } else if (command === 'reset') {
      selectedSensor.value!.status = 'online'
      selectedSensor.value!.sensitivity = 70
      selectedSensor.value!.lastUpdated = new Date().toLocaleString()
      ElMessage.success('Sensor reset successfully')
    }
    updateStats()
    tableLoading.value = false
    controlDialogVisible.value = false
  }, 500)
}

const sendSensitivityCommand = (value: number) => {
  if (!selectedSensor.value) return
  selectedSensor.value.sensitivity = value
  selectedSensor.value.lastUpdated = new Date().toLocaleString()
  ElMessage.info(`Sensitivity set to ${value}%`)
}

// ==================== Detail View ====================
const detailDialogVisible = ref(false)

const viewDetails = (row: MotionSensor) => {
  selectedSensor.value = row
  detailDialogVisible.value = true
}

// ==================== Helper Functions ====================
const getStatusTag = (status: string) => {
  const map: Record<string, string> = {
    online: 'success',
    offline: 'info',
    maintenance: 'warning',
    fault: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    online: 'Online',
    offline: 'Offline',
    maintenance: 'Maintenance',
    fault: 'Fault'
  }
  return map[status] || status
}

const getSensorTypeTag = (type: string) => {
  const map: Record<string, string> = {
    PIR: 'primary',
    Microwave: 'success',
    Ultrasonic: 'warning',
    'Dual Tech': 'danger'
  }
  return map[type] || 'info'
}

const getSignalTag = (strength: number) => {
  if (strength >= 80) return 'success'
  if (strength >= 50) return 'warning'
  return 'danger'
}

const getSignalText = (strength: number) => {
  if (strength >= 80) return 'Excellent'
  if (strength >= 50) return 'Good'
  if (strength >= 30) return 'Fair'
  return 'Poor'
}

const getBatteryColor = (level: number) => {
  if (level >= 70) return '#67C23A'
  if (level >= 30) return '#E6A23C'
  return '#F56C6C'
}

// ==================== Actions ====================
const refreshData = () => {
  tableLoading.value = true
  setTimeout(() => {
    sensors.value = generateMockData()
    updateStats()
    updateLocationOptions()
    initCharts()
    tableLoading.value = false
    ElMessage.success('Data refreshed')
  }, 800)
}

const handleExport = () => {
  ElMessage.success('Export started')
}

const handleSearch = () => {
  pagination.value.currentPage = 1
  ElMessage.success(`Found ${filteredSensors.value.length} sensors`)
}

const resetFilters = () => {
  filters.value = { sensorName: '', location: '', status: '', sensorType: '' }
  pagination.value.currentPage = 1
  ElMessage.success('Filters reset')
}

const handleSizeChange = () => {
  pagination.value.currentPage = 1
}

const handleCurrentChange = () => {}

const toggleFullscreen = () => {
  ElMessage.info('Fullscreen mode')
}

// Watch for window resize
watch([trendChartRef, statusChartRef], () => {
  window.addEventListener('resize', () => {
    trendChart?.resize()
    statusChart?.resize()
  })
})

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
      sensors.value = generateMockData()
      updateStats()
      updateLocationOptions()
      initCharts()
    }, 400)
  }, 2000)
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

/* ==================== Main Content ==================== */
.motion-sensors-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: white;
  padding: 16px 20px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 12px;
}

.stat-card:hover {
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
  font-weight: bold;
}

.stat-value.online {
  color: #67C23A;
}

.stat-value.offline {
  color: #909399;
}

.stat-value.detection {
  color: #409EFF;
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

.stat-icon.total {
  background: rgba(64, 158, 255, 0.1);
  color: #409EFF;
}

.stat-icon.online-bg {
  background: rgba(103, 194, 58, 0.1);
  color: #67C23A;
}

.stat-icon.offline-bg {
  background: rgba(144, 147, 153, 0.1);
  color: #909399;
}

.stat-icon.detection-bg {
  background: rgba(64, 158, 255, 0.1);
  color: #409EFF;
}

.charts-row {
  margin-bottom: 20px;
}

.chart-card {
  border-radius: 12px;
}

.chart-container {
  width: 100%;
  height: 350px;
}

.filter-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.table-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.control-content {
  padding: 10px;
}

.current-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  font-weight: 500;
}

.sensor-info {
  margin: 10px 0;
}

.control-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin: 20px 0;
}

.sensitivity-control {
  display: flex;
  align-items: center;
  gap: 16px;
}

.sensitivity-control .el-slider {
  flex: 1;
}

.sensitivity-value {
  min-width: 45px;
  font-size: 14px;
  color: #409EFF;
}
</style>