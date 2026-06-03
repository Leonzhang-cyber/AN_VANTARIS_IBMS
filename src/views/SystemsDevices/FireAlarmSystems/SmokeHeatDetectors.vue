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
        <div class="loading-tip">Smoke & Heat Detectors</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="detectors-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Smoke / Heat Detectors</h2>
        <p class="header-subtitle">Fire Detection System | Real-time Monitoring</p>
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
            <el-icon :size="28"><Grid /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Total Detectors</div>
            <div class="overview-value">{{ stats.total }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon normal">
            <el-icon :size="28"><CircleCheck /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Normal</div>
            <div class="overview-value">{{ stats.normal }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon alarm">
            <el-icon :size="28"><WarningFilled /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Alarm / Fault</div>
            <div class="overview-value" :class="{ 'has-alarm': stats.alarm > 0 }">{{ stats.alarm }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon maintenance">
            <el-icon :size="28"><Tools /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Maintenance Due</div>
            <div class="overview-value">{{ stats.maintenanceDue }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Active Alarms Section -->
    <div v-if="activeAlarms.length > 0" class="alarm-section">
      <div class="section-title">
        <span class="alarm-title">
          <el-icon><WarningFilled /></el-icon>
          Active Alarms
        </span>
        <el-badge :value="activeAlarms.length" type="danger" />
      </div>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" v-for="alarm in activeAlarms" :key="alarm.id">
          <div class="alarm-card" :class="alarm.severity">
            <div class="alarm-header">
              <span class="alarm-location">{{ alarm.location }}</span>
              <el-tag :type="alarm.severity === 'critical' ? 'danger' : 'warning'" size="small">
                {{ alarm.severity === 'critical' ? 'FIRE' : 'FAULT' }}
              </el-tag>
            </div>
            <div class="alarm-details">
              <div class="alarm-detail">
                <span class="label">Detector:</span>
                <span class="value">{{ alarm.detectorName }}</span>
              </div>
              <div class="alarm-detail">
                <span class="label">Type:</span>
                <span class="value">{{ alarm.detectorType }}</span>
              </div>
              <div class="alarm-detail">
                <span class="label">Reading:</span>
                <span class="value warning">{{ alarm.reading }} {{ alarm.unit }}</span>
              </div>
              <div class="alarm-detail">
                <span class="label">Detected:</span>
                <span class="value">{{ alarm.detectedAt }}</span>
              </div>
            </div>
            <div class="alarm-actions">
              <el-button type="primary" size="small" @click="investigateAlarm(alarm)">
                <el-icon><Search /></el-icon>
                Investigate
              </el-button>
              <el-button type="success" size="small" @click="acknowledgeAlarm(alarm)">
                <el-icon><CircleCheck /></el-icon>
                Acknowledge
              </el-button>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- Zone Status Row -->
    <el-row :gutter="20" class="zone-row">
      <el-col :span="24">
        <el-card shadow="hover" class="zone-card">
          <template #header>
            <div class="card-header">
              <span>Zone Status Overview</span>
              <el-select v-model="zoneFilter" size="small" style="width: 150px" placeholder="Filter by zone" clearable>
                <el-option label="All Zones" value="all" />
                <el-option label="Zone A" value="Zone A" />
                <el-option label="Zone B" value="Zone B" />
                <el-option label="Zone C" value="Zone C" />
                <el-option label="Zone D" value="Zone D" />
              </el-select>
            </div>
          </template>
          <el-row :gutter="16">
            <el-col :xs="12" :sm="8" :md="6" :lg="4" v-for="zone in filteredZones" :key="zone.name">
              <div class="zone-status" :class="zone.status">
                <div class="zone-name">{{ zone.name }}</div>
                <div class="zone-stats">
                  <span>Total: {{ zone.total }}</span>
                  <span>Normal: {{ zone.normal }}</span>
                </div>
                <div class="zone-alarm" v-if="zone.alarm > 0">
                  <el-icon><WarningFilled /></el-icon>
                  {{ zone.alarm }} Alarms
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <!-- Detector Grid -->
    <div class="section-title">
      <span>Detectors</span>
      <div class="filter-group">
        <el-select v-model="typeFilter" size="small" style="width: 130px" placeholder="Type" clearable>
          <el-option label="All Types" value="all" />
          <el-option label="Smoke" value="Smoke" />
          <el-option label="Heat" value="Heat" />
          <el-option label="Multi" value="Multi" />
        </el-select>
        <el-select v-model="statusFilter" size="small" style="width: 130px" placeholder="Status" clearable>
          <el-option label="All Status" value="all" />
          <el-option label="Normal" value="normal" />
          <el-option label="Alarm" value="alarm" />
          <el-option label="Fault" value="fault" />
          <el-option label="Test" value="test" />
        </el-select>
      </div>
    </div>

    <el-row :gutter="20" class="detectors-row">
      <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="detector in filteredDetectors" :key="detector.id">
        <div class="detector-card" :class="detector.status">
          <div class="detector-header">
            <span class="detector-name">{{ detector.name }}</span>
            <div class="detector-status" :class="detector.status">
              <span class="status-dot"></span>
              {{ getStatusText(detector.status) }}
            </div>
          </div>
          <div class="detector-icon">
            <el-icon :size="40" v-if="detector.type === 'Smoke'"><Warning /></el-icon>
            <el-icon :size="40" v-else-if="detector.type === 'Heat'"><Temperature /></el-icon>
            <el-icon :size="40" v-else><Cpu /></el-icon>
          </div>
          <div class="detector-readings">
            <div class="reading" v-if="detector.type !== 'Heat'">
              <span class="label">Smoke Level:</span>
              <div class="reading-value">
                <el-progress
                    :percentage="detector.smokeLevel"
                    :color="getSmokeColor(detector.smokeLevel)"
                    :stroke-width="8"
                />
                <span class="percentage">{{ detector.smokeLevel }}%</span>
              </div>
            </div>
            <div class="reading" v-if="detector.type !== 'Smoke'">
              <span class="label">Temperature:</span>
              <div class="reading-value">
                <el-progress
                    :percentage="detector.tempPercent"
                    :color="getTempColor(detector.temperature)"
                    :stroke-width="8"
                />
                <span class="percentage">{{ detector.temperature }}°C</span>
              </div>
            </div>
            <div class="reading">
              <span class="label">Battery:</span>
              <el-progress :percentage="detector.battery" :stroke-width="6" :show-text="false" style="width: 120px" />
              <span class="percentage small">{{ detector.battery }}%</span>
            </div>
            <div class="reading">
              <span class="label">Sensitivity:</span>
              <span class="value">{{ detector.sensitivity }}%</span>
            </div>
          </div>
          <div class="detector-location">
            <el-icon><Location /></el-icon>
            {{ detector.location }} - {{ detector.zone }}
          </div>
          <div class="detector-footer">
            <span class="last-check">Last Test: {{ detector.lastTestDate }}</span>
            <el-button type="primary" link size="small" @click="viewDetectorDetails(detector)">
              Details
            </el-button>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Charts Row -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :md="14">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Detection Readings Trend (Last 24 Hours)</span>
              <el-radio-group v-model="chartPeriod" size="small" @change="updateTrendChart">
                <el-radio-button label="hour">Hourly</el-radio-button>
                <el-radio-button label="day">Daily</el-radio-button>
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
              <span>Detector Status Distribution</span>
            </div>
          </template>
          <div ref="statusChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Detector Details Table -->
    <el-card shadow="hover" class="table-card">
      <template #header>
        <div class="card-header">
          <span>Detector Details</span>
          <el-input v-model="searchText" placeholder="Search detector..." style="width: 200px" clearable>
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </template>
      <el-table :data="paginatedDetectors" stripe border style="width: 100%">
        <el-table-column prop="name" label="Detector Name" min-width="140" />
        <el-table-column prop="type" label="Type" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'Smoke' ? 'primary' : (row.type === 'Heat' ? 'danger' : 'warning')" size="small">
              {{ row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="Location" min-width="150" />
        <el-table-column prop="zone" label="Zone" width="100" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="smokeLevel" label="Smoke (%)" width="110" v-if="hasSmokeDetector">
          <template #default="{ row }">
            <span v-if="row.type !== 'Heat'">{{ row.smokeLevel }}%</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="temperature" label="Temp (°C)" width="100">
          <template #default="{ row }">
            <span :class="getTempWarningClass(row.temperature)">{{ row.temperature }}°C</span>
          </template>
        </el-table-column>
        <el-table-column prop="battery" label="Battery (%)" width="100" sortable />
        <el-table-column prop="lastTestDate" label="Last Test" width="120" />
        <el-table-column label="Actions" fixed="right" width="100">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetectorDetails(row)">
              Details
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredTableDetectors.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Detector Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Detector Details - ${selectedDetector?.name}`" width="600px">
      <el-descriptions :column="2" border v-if="selectedDetector">
        <el-descriptions-item label="Detector Name">{{ selectedDetector.name }}</el-descriptions-item>
        <el-descriptions-item label="Type">
          <el-tag :type="selectedDetector.type === 'Smoke' ? 'primary' : (selectedDetector.type === 'Heat' ? 'danger' : 'warning')" size="small">
            {{ selectedDetector.type }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Location">{{ selectedDetector.location }}</el-descriptions-item>
        <el-descriptions-item label="Zone">{{ selectedDetector.zone }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusTag(selectedDetector.status)">{{ getStatusText(selectedDetector.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Address">{{ selectedDetector.address }}</el-descriptions-item>
        <el-descriptions-item label="Smoke Level" v-if="selectedDetector.type !== 'Heat'">{{ selectedDetector.smokeLevel }}%</el-descriptions-item>
        <el-descriptions-item label="Temperature">{{ selectedDetector.temperature }}°C</el-descriptions-item>
        <el-descriptions-item label="Battery">{{ selectedDetector.battery }}%</el-descriptions-item>
        <el-descriptions-item label="Sensitivity">{{ selectedDetector.sensitivity }}%</el-descriptions-item>
        <el-descriptions-item label="Last Test">{{ selectedDetector.lastTestDate }}</el-descriptions-item>
        <el-descriptions-item label="Installation Date">{{ selectedDetector.installDate }}</el-descriptions-item>
        <el-descriptions-item label="Serial Number">{{ selectedDetector.serialNumber }}</el-descriptions-item>
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
  Grid,
  CircleCheck,
  WarningFilled,
  Tools,
  Search,
  Location,
  Warning,
  Cpu
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Initializing detectors...',
  'Reading sensor data...',
  'Almost ready...'
]

// ==================== Data State ====================
const chartPeriod = ref('hour')
const zoneFilter = ref('all')
const typeFilter = ref('all')
const statusFilter = ref('all')
const searchText = ref('')

interface Detector {
  id: number
  name: string
  type: 'Smoke' | 'Heat' | 'Multi'
  location: string
  zone: string
  status: 'normal' | 'alarm' | 'fault' | 'test'
  smokeLevel: number
  temperature: number
  tempPercent: number
  battery: number
  sensitivity: number
  address: string
  lastTestDate: string
  installDate: string
  serialNumber: string
}

interface ZoneStatus {
  name: string
  total: number
  normal: number
  alarm: number
  status: string
}

interface AlarmEvent {
  id: number
  detectorName: string
  detectorType: string
  location: string
  severity: 'critical' | 'warning'
  reading: number
  unit: string
  detectedAt: string
}

const detectors = ref<Detector[]>([])
const zones = ref<ZoneStatus[]>([])
const activeAlarms = ref<AlarmEvent[]>([])

const stats = computed(() => ({
  total: detectors.value.length,
  normal: detectors.value.filter(d => d.status === 'normal').length,
  alarm: detectors.value.filter(d => d.status === 'alarm' || d.status === 'fault').length,
  maintenanceDue: detectors.value.filter(d => {
    const lastTest = new Date(d.lastTestDate)
    const monthsSince = (new Date().getTime() - lastTest.getTime()) / (1000 * 60 * 60 * 24 * 30)
    return monthsSince > 11
  }).length
}))

const hasSmokeDetector = computed(() => detectors.value.some(d => d.type !== 'Heat'))

const filteredDetectors = computed(() => {
  let filtered = detectors.value
  if (typeFilter.value !== 'all') {
    filtered = filtered.filter(d => d.type === typeFilter.value)
  }
  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(d => d.status === statusFilter.value)
  }
  return filtered
})

const filteredZones = computed(() => {
  if (zoneFilter.value === 'all') return zones.value
  return zones.value.filter(z => z.name === zoneFilter.value)
})

const filteredTableDetectors = computed(() => {
  if (!searchText.value) return filteredDetectors.value
  return filteredDetectors.value.filter(d =>
      d.name.toLowerCase().includes(searchText.value.toLowerCase()) ||
      d.location.toLowerCase().includes(searchText.value.toLowerCase())
  )
})

const pagination = ref({ currentPage: 1, pageSize: 10 })
const paginatedDetectors = computed(() => {
  const start = (pagination.value.currentPage - 1) * pagination.value.pageSize
  return filteredTableDetectors.value.slice(start, start + pagination.value.pageSize)
})

// Generate mock detectors
const generateDetectors = (): Detector[] => {
  const locations = [
    'Lobby', 'Corridor East', 'Corridor West', 'Meeting Room 1', 'Meeting Room 2',
    'Office 101', 'Office 102', 'Office 103', 'Server Room', 'Data Center',
    'Kitchen', 'Cafeteria', 'Storage Room', 'Electrical Room', 'HVAC Room',
    'Parking Level 1', 'Parking Level 2', 'Staircase A', 'Staircase B', 'Restroom'
  ]
  const zones = ['Zone A', 'Zone B', 'Zone C', 'Zone D']
  const types: ('Smoke' | 'Heat' | 'Multi')[] = ['Smoke', 'Smoke', 'Heat', 'Smoke', 'Multi', 'Smoke', 'Heat', 'Smoke', 'Multi', 'Smoke']

  return locations.map((location, idx) => {
    const type = types[idx % types.length]
    const statuses: ('normal' | 'alarm' | 'fault' | 'test')[] =
        ['normal', 'normal', 'normal', 'normal', 'normal', 'normal', 'alarm', 'normal', 'fault', 'normal', 'normal', 'normal', 'normal', 'normal', 'test', 'normal', 'normal', 'normal', 'normal', 'normal']

    const smokeLevel = type !== 'Heat' ? Math.floor(5 + Math.random() * 95) : 0
    const temperature = parseFloat((20 + Math.random() * 15).toFixed(1))
    const tempPercent = Math.min(100, Math.floor((temperature / 60) * 100))

    const lastTest = new Date()
    lastTest.setMonth(lastTest.getMonth() - Math.floor(Math.random() * 18))

    return {
      id: idx + 1,
      name: `${type === 'Smoke' ? 'SD' : (type === 'Heat' ? 'HD' : 'MD')}-${String(idx + 1).padStart(3, '0')}`,
      type: type,
      location: location,
      zone: zones[idx % zones.length],
      status: statuses[idx % statuses.length],
      smokeLevel: smokeLevel,
      temperature: temperature,
      tempPercent: tempPercent,
      battery: Math.floor(70 + Math.random() * 30),
      sensitivity: Math.floor(50 + Math.random() * 40),
      address: `${Math.floor(1 + Math.random() * 255)}.${Math.floor(1 + Math.random() * 255)}`,
      lastTestDate: lastTest.toISOString().split('T')[0],
      installDate: '2023-01-15',
      serialNumber: `SN-${Math.random().toString(36).substring(2, 10).toUpperCase()}`
    }
  })
}

// Generate zones summary
const generateZones = (): ZoneStatus[] => {
  const zoneNames = ['Zone A', 'Zone B', 'Zone C', 'Zone D']
  return zoneNames.map(name => {
    const zoneDetectors = detectors.value.filter(d => d.zone === name)
    return {
      name: name,
      total: zoneDetectors.length,
      normal: zoneDetectors.filter(d => d.status === 'normal').length,
      alarm: zoneDetectors.filter(d => d.status === 'alarm' || d.status === 'fault').length,
      status: zoneDetectors.some(d => d.status === 'alarm') ? 'alarm' :
          zoneDetectors.some(d => d.status === 'fault') ? 'fault' : 'normal'
    }
  })
}

// Generate active alarms
const generateActiveAlarms = (): AlarmEvent[] => {
  const alarmDetectors = detectors.value.filter(d => d.status === 'alarm' || d.status === 'fault')
  return alarmDetectors.map((d, idx) => ({
    id: idx + 1,
    detectorName: d.name,
    detectorType: d.type,
    location: d.location,
    severity: d.status === 'alarm' ? 'critical' : 'warning',
    reading: d.type !== 'Heat' ? d.smokeLevel : d.temperature,
    unit: d.type !== 'Heat' ? '%' : '°C',
    detectedAt: new Date(Date.now() - Math.random() * 30 * 60 * 1000).toLocaleString()
  }))
}

// Helper functions
const getStatusText = (status: string) => {
  const map: Record<string, string> = { normal: 'Normal', alarm: 'ALARM', fault: 'Fault', test: 'Test' }
  return map[status] || status
}

const getStatusTag = (status: string) => {
  const map: Record<string, string> = { normal: 'success', alarm: 'danger', fault: 'warning', test: 'info' }
  return map[status] || 'info'
}

const getSmokeColor = (level: number) => {
  if (level < 30) return '#67C23A'
  if (level < 60) return '#E6A23C'
  return '#F56C6C'
}

const getTempColor = (temp: number) => {
  if (temp < 40) return '#67C23A'
  if (temp < 55) return '#E6A23C'
  return '#F56C6C'
}

const getTempWarningClass = (temp: number) => {
  if (temp > 55) return 'danger-text'
  if (temp > 40) return 'warning-text'
  return ''
}

// Actions
const detailDialogVisible = ref(false)
const selectedDetector = ref<Detector | null>(null)

const viewDetectorDetails = (detector: Detector) => {
  selectedDetector.value = detector
  detailDialogVisible.value = true
}

const investigateAlarm = (alarm: AlarmEvent) => {
  ElMessage.info(`Investigating alarm at ${alarm.location}`)
}

const acknowledgeAlarm = (alarm: AlarmEvent) => {
  ElMessageBox.confirm(`Acknowledge alarm at ${alarm.location}?`, 'Confirm', {
    confirmButtonText: 'Acknowledge',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const detector = detectors.value.find(d => d.name === alarm.detectorName)
    if (detector) {
      detector.status = 'normal'
      if (detector.type !== 'Heat') detector.smokeLevel = Math.floor(Math.random() * 15)
      detector.temperature = parseFloat((20 + Math.random() * 10).toFixed(1))
    }
    activeAlarms.value = activeAlarms.value.filter(a => a.id !== alarm.id)
    zones.value = generateZones()
    updateStatusChart()
    ElMessage.success('Alarm acknowledged')
  }).catch(() => {})
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
  let smokeData: number[] = []
  let tempData: number[] = []
  let xAxisData: string[] = []

  if (chartPeriod.value === 'hour') {
    xAxisData = Array.from({ length: 24 }, (_, i) => `${i}:00`)
    smokeData = Array.from({ length: 24 }, () => Math.floor(5 + Math.random() * 30))
    tempData = Array.from({ length: 24 }, () => parseFloat((22 + Math.random() * 8).toFixed(1)))
  } else {
    xAxisData = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    smokeData = [8, 12, 10, 25, 45, 15, 9]
    tempData = [23, 24, 22, 26, 28, 25, 23]
  }

  trendChart?.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Average Smoke Level (%)', 'Average Temperature (°C)'] },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: [
      { type: 'value', name: 'Smoke Level (%)', min: 0, max: 100 },
      { type: 'value', name: 'Temperature (°C)' }
    ],
    series: [
      {
        name: 'Average Smoke Level (%)',
        type: 'line',
        data: smokeData,
        smooth: true,
        lineStyle: { color: '#909399', width: 3 },
        areaStyle: { opacity: 0.1 },
        yAxisIndex: 0,
        markLine: { data: [{ yAxis: 30, name: 'Warning', lineStyle: { color: '#E6A23C' } }, { yAxis: 60, name: 'Alarm', lineStyle: { color: '#F56C6C' } }] }
      },
      {
        name: 'Average Temperature (°C)',
        type: 'line',
        data: tempData,
        smooth: true,
        lineStyle: { color: '#F56C6C', width: 3 },
        yAxisIndex: 1,
        markLine: { data: [{ yAxis: 40, name: 'Warning', lineStyle: { color: '#E6A23C' } }, { yAxis: 55, name: 'Alarm', lineStyle: { color: '#F56C6C' } }] }
      }
    ]
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
        { value: stats.value.normal, name: 'Normal', itemStyle: { color: '#67C23A' } },
        { value: detectors.value.filter(d => d.status === 'alarm').length, name: 'Alarm', itemStyle: { color: '#F56C6C' } },
        { value: detectors.value.filter(d => d.status === 'fault').length, name: 'Fault', itemStyle: { color: '#E6A23C' } },
        { value: detectors.value.filter(d => d.status === 'test').length, name: 'Test', itemStyle: { color: '#909399' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })
}

// ==================== Actions ====================
const refreshData = () => {
  detectors.value = generateDetectors()
  zones.value = generateZones()
  activeAlarms.value = generateActiveAlarms()
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
      detectors.value = generateDetectors()
      zones.value = generateZones()
      activeAlarms.value = generateActiveAlarms()
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
.detectors-container {
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
.overview-icon.alarm { background: rgba(245, 108, 108, 0.1); color: #F56C6C; }
.overview-icon.maintenance { background: rgba(230, 162, 60, 0.1); color: #E6A23C; }

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

.overview-value.has-alarm { color: #F56C6C; }

/* Alarm Section */
.alarm-section {
  margin-bottom: 24px;
}

.alarm-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #F56C6C;
  font-weight: 600;
}

.alarm-card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 20px;
  border-left: 4px solid #E6A23C;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.alarm-card.critical { border-left-color: #F56C6C; background: rgba(245, 108, 108, 0.02); }

.alarm-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.alarm-location {
  font-weight: 600;
  font-size: 16px;
}

.alarm-details {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 16px;
}

.alarm-detail {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 13px;
}

.alarm-detail .label { color: #909399; }
.alarm-detail .value { font-weight: 500; }
.alarm-detail .value.warning { color: #F56C6C; font-weight: 600; }

.alarm-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* Zone Status */
.zone-row {
  margin-bottom: 24px;
}

.zone-card {
  border-radius: 16px;
}

.zone-status {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 12px;
  text-align: center;
  margin-bottom: 12px;
  transition: all 0.3s ease;
}

.zone-status:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.zone-status.normal { border-left: 3px solid #67C23A; }
.zone-status.alarm { border-left: 3px solid #F56C6C; background: rgba(245, 108, 108, 0.05); }
.zone-status.fault { border-left: 3px solid #E6A23C; background: rgba(230, 162, 60, 0.05); }

.zone-name {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 8px;
}

.zone-stats {
  display: flex;
  justify-content: center;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.zone-alarm {
  margin-top: 8px;
  font-size: 12px;
  color: #F56C6C;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
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

/* Detector Cards */
.detectors-row {
  margin-bottom: 20px;
}

.detector-card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.3s ease;
  border-top: 3px solid #67C23A;
}

.detector-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(0,0,0,0.12);
}

.detector-card.alarm { border-top-color: #F56C6C; background: rgba(245, 108, 108, 0.02); }
.detector-card.fault { border-top-color: #E6A23C; background: rgba(230, 162, 60, 0.02); }
.detector-card.test { border-top-color: #909399; }

.detector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.detector-name {
  font-weight: 600;
  font-size: 16px;
  color: #1f2f3d;
}

.detector-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 20px;
}

.detector-status.normal { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
.detector-status.alarm { background: rgba(245, 108, 108, 0.1); color: #F56C6C; }
.detector-status.fault { background: rgba(230, 162, 60, 0.1); color: #E6A23C; }
.detector-status.test { background: rgba(144, 147, 153, 0.1); color: #909399; }

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.detector-icon {
  text-align: center;
  margin: 12px 0;
  color: #409EFF;
}

.detector-card.alarm .detector-icon { color: #F56C6C; }

.detector-readings {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 12px;
}

.reading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  font-size: 13px;
}

.reading .label { color: #909399; }
.reading .value { font-weight: 500; }

.reading-value {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  justify-content: flex-end;
}

.reading-value .el-progress { width: 100px; }
.percentage { font-size: 12px; font-weight: 500; min-width: 40px; text-align: right; }
.percentage.small { font-size: 11px; }

.detector-location {
  font-size: 12px;
  color: #909399;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.detector-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: #c0c4cc;
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

/* Table */
.table-card {
  border-radius: 16px;
}

.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

/* Text colors */
.warning-text { color: #E6A23C; font-weight: 500; }
.danger-text { color: #F56C6C; font-weight: 500; }
</style>