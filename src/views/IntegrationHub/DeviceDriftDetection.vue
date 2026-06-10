<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, Refresh, View, Edit, Delete, Monitor, Connection,
  User, Warning, Clock, Cpu, DataLine, Message, Upload, Download,
  Setting, Document, Checked, Bell, TrendCharts,
  List, Odometer, Location, Link, Share, VideoCamera, Lock,
  CopyDocument, Switch, Filter, MagicStick, Tickets, Right,
  Sort, FolderOpened, Files, DocumentAdd, Timer, Aim, DataAnalysis
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing drift detection engine...',
  'Analyzing device baselines...',
  'Almost ready...'
]

// ==================== Chart Refs ====================
const driftTrendChart = ref<HTMLElement | null>(null)
const driftDistributionChart = ref<HTMLElement | null>(null)
const deviceHealthChart = ref<HTMLElement | null>(null)

// ==================== State ====================
const activeTab = ref('overview')
const searchKeyword = ref('')
const severityFilter = ref('')
const deviceTypeFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(15)
const thresholdDialogVisible = ref(false)
const calibrationDialogVisible = ref(false)
const historyDialogVisible = ref(false)
const selectedDevice = ref<any>(null)
const selectedDrift = ref<any>(null)

// ==================== Statistics ====================
const statistics = reactive({
  totalDevices: 156,
  devicesWithDrift: 23,
  criticalDrift: 5,
  warningDrift: 12,
  infoDrift: 6,
  avgDriftPercentage: 8.5,
  devicesCalibrated: 34
})

// ==================== Drift Detection Data ====================
interface DriftDetection {
  id: number
  deviceId: string
  deviceName: string
  deviceType: string
  location: string
  parameter: string
  baselineValue: number
  currentValue: number
  driftPercentage: number
  severity: 'critical' | 'warning' | 'info'
  detectedAt: string
  status: 'active' | 'acknowledged' | 'resolved'
  trend: 'increasing' | 'decreasing' | 'stable'
  recommendation: string
}

const driftDetections = ref<DriftDetection[]>([
  {
    id: 1,
    deviceId: 'TEMP_SENSOR_001',
    deviceName: 'Temperature Sensor - Lobby',
    deviceType: 'Temperature',
    location: 'Building A - Floor 1',
    parameter: 'Temperature',
    baselineValue: 22.5,
    currentValue: 24.8,
    driftPercentage: 10.2,
    severity: 'warning',
    detectedAt: '2024-01-15 08:23:45',
    status: 'active',
    trend: 'increasing',
    recommendation: 'Recalibrate sensor or check for environmental changes'
  },
  {
    id: 2,
    deviceId: 'HUMIDITY_002',
    deviceName: 'Humidity Sensor - Office',
    deviceType: 'Humidity',
    location: 'Building A - Floor 2',
    parameter: 'Humidity',
    baselineValue: 55.0,
    currentValue: 48.5,
    driftPercentage: -11.8,
    severity: 'warning',
    detectedAt: '2024-01-15 09:15:22',
    status: 'active',
    trend: 'decreasing',
    recommendation: 'Check sensor calibration and humidity source'
  },
  {
    id: 3,
    deviceId: 'PRESSURE_003',
    deviceName: 'Pressure Sensor - HVAC',
    deviceType: 'Pressure',
    location: 'Building B - Mechanical Room',
    parameter: 'Air Pressure',
    baselineValue: 101.3,
    currentValue: 95.2,
    driftPercentage: -6.0,
    severity: 'critical',
    detectedAt: '2024-01-15 07:45:33',
    status: 'active',
    trend: 'decreasing',
    recommendation: 'Immediate calibration required - possible system issue'
  },
  {
    id: 4,
    deviceId: 'CO2_004',
    deviceName: 'CO2 Sensor - Conference Room',
    deviceType: 'Air Quality',
    location: 'Building A - Floor 3',
    parameter: 'CO2 Level',
    baselineValue: 420,
    currentValue: 445,
    driftPercentage: 6.0,
    severity: 'info',
    detectedAt: '2024-01-15 10:30:18',
    status: 'acknowledged',
    trend: 'increasing',
    recommendation: 'Monitor trend - consider recalibration'
  },
  {
    id: 5,
    deviceId: 'POWER_005',
    deviceName: 'Power Meter - Main',
    deviceType: 'Electrical',
    location: 'Building B - Electrical Room',
    parameter: 'Power Factor',
    baselineValue: 0.95,
    currentValue: 0.88,
    driftPercentage: -7.4,
    severity: 'critical',
    detectedAt: '2024-01-15 06:20:45',
    status: 'active',
    trend: 'decreasing',
    recommendation: 'Urgent: Check power quality and calibration'
  },
  {
    id: 6,
    deviceId: 'FLOW_006',
    deviceName: 'Flow Meter - Water',
    deviceType: 'Flow',
    location: 'Building A - Utility Room',
    parameter: 'Flow Rate',
    baselineValue: 12.5,
    currentValue: 13.2,
    driftPercentage: 5.6,
    severity: 'info',
    detectedAt: '2024-01-14 14:20:33',
    status: 'resolved',
    trend: 'stable',
    recommendation: 'Within acceptable range - continue monitoring'
  },
  {
    id: 7,
    deviceId: 'VIBRATION_007',
    deviceName: 'Vibration Sensor - Motor',
    deviceType: 'Vibration',
    location: 'Building B - Motor Room',
    parameter: 'Vibration',
    baselineValue: 2.5,
    currentValue: 3.8,
    driftPercentage: 52.0,
    severity: 'critical',
    detectedAt: '2024-01-15 11:45:12',
    status: 'active',
    trend: 'increasing',
    recommendation: 'Critical: Immediate maintenance required'
  },
  {
    id: 8,
    deviceId: 'LIGHT_008',
    deviceName: 'Light Sensor - Office',
    deviceType: 'Light',
    location: 'Building A - Floor 2',
    parameter: 'Lux Level',
    baselineValue: 350,
    currentValue: 310,
    driftPercentage: -11.4,
    severity: 'warning',
    detectedAt: '2024-01-15 09:50:28',
    status: 'active',
    trend: 'decreasing',
    recommendation: 'Check sensor cleanliness and calibration'
  },
  {
    id: 9,
    deviceId: 'CURRENT_009',
    deviceName: 'Current Sensor - UPS',
    deviceType: 'Electrical',
    location: 'Data Center - Rack A',
    parameter: 'Current Draw',
    baselineValue: 15.2,
    currentValue: 16.8,
    driftPercentage: 10.5,
    severity: 'warning',
    detectedAt: '2024-01-15 10:15:45',
    status: 'active',
    trend: 'increasing',
    recommendation: 'Monitor load changes, recalibrate if needed'
  },
  {
    id: 10,
    deviceId: 'OCCUPANCY_010',
    deviceName: 'Occupancy Sensor - Hall',
    deviceType: 'Occupancy',
    location: 'Building A - Floor 1',
    parameter: 'Detection Range',
    baselineValue: 8.0,
    currentValue: 7.2,
    driftPercentage: -10.0,
    severity: 'warning',
    detectedAt: '2024-01-15 08:55:33',
    status: 'active',
    trend: 'decreasing',
    recommendation: 'Recalibrate sensor range'
  }
])

// ==================== Baseline History ====================
const baselineHistory = ref([
  { date: '2024-01-01', temp_baseline: 22.3, hum_baseline: 54.2, pressure_baseline: 101.2 },
  { date: '2024-01-02', temp_baseline: 22.4, hum_baseline: 54.5, pressure_baseline: 101.3 },
  { date: '2024-01-03', temp_baseline: 22.5, hum_baseline: 55.0, pressure_baseline: 101.1 },
  { date: '2024-01-04', temp_baseline: 22.6, hum_baseline: 55.2, pressure_baseline: 101.4 },
  { date: '2024-01-05', temp_baseline: 22.5, hum_baseline: 55.1, pressure_baseline: 101.3 },
  { date: '2024-01-06', temp_baseline: 22.4, hum_baseline: 54.8, pressure_baseline: 101.2 },
  { date: '2024-01-07', temp_baseline: 22.3, hum_baseline: 54.5, pressure_baseline: 101.1 }
])

// ==================== Drift Thresholds ====================
const driftThresholds = ref({
  temperature: { warning: 5, critical: 10 },
  humidity: { warning: 8, critical: 15 },
  pressure: { warning: 3, critical: 7 },
  'air quality': { warning: 10, critical: 20 },
  electrical: { warning: 8, critical: 15 },
  flow: { warning: 5, critical: 12 },
  vibration: { warning: 15, critical: 30 },
  light: { warning: 10, critical: 20 },
  occupancy: { warning: 12, critical: 25 }
})

// ==================== Calibration History ====================
const calibrationHistory = ref([
  { id: 1, deviceId: 'TEMP_SENSOR_001', date: '2024-01-10', type: 'Auto', result: 'Success', driftCorrected: 1.2 },
  { id: 2, deviceId: 'PRESSURE_003', date: '2024-01-12', type: 'Manual', result: 'Success', driftCorrected: 3.5 },
  { id: 3, deviceId: 'CO2_004', date: '2024-01-08', type: 'Auto', result: 'Success', driftCorrected: 0.8 },
  { id: 4, deviceId: 'FLOW_006', date: '2024-01-05', type: 'Manual', result: 'Failed', driftCorrected: 0 },
  { id: 5, deviceId: 'VIBRATION_007', date: '2024-01-14', type: 'Auto', result: 'Success', driftCorrected: 8.2 }
])

// ==================== Computed ====================
const filteredDrifts = computed(() => {
  let filtered = driftDetections.value
  if (searchKeyword.value) {
    filtered = filtered.filter(d =>
        d.deviceName.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        d.deviceId.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        d.location.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (severityFilter.value) {
    filtered = filtered.filter(d => d.severity === severityFilter.value)
  }
  if (deviceTypeFilter.value) {
    filtered = filtered.filter(d => d.deviceType === deviceTypeFilter.value)
  }
  return filtered
})

const paginatedDrifts = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredDrifts.value.slice(start, end)
})

const criticalCount = computed(() => driftDetections.value.filter(d => d.severity === 'critical').length)
const warningCount = computed(() => driftDetections.value.filter(d => d.severity === 'warning').length)
const infoCount = computed(() => driftDetections.value.filter(d => d.severity === 'info').length)

// ==================== Methods ====================
const getSeverityType = (severity: string) => {
  const types: Record<string, string> = {
    critical: 'danger',
    warning: 'warning',
    info: 'info'
  }
  return types[severity] || 'info'
}

const getSeverityIcon = (severity: string) => {
  const icons: Record<string, any> = {
    critical: Warning,
    warning: Bell,
    info: Info
  }
  return icons[severity] || Bell
}

const getTrendIcon = (trend: string) => {
  const icons: Record<string, string> = {
    increasing: '📈',
    decreasing: '📉',
    stable: '➡️'
  }
  return icons[trend] || '➡️'
}

const getTrendColor = (trend: string) => {
  const colors: Record<string, string> = {
    increasing: '#ff4d4f',
    decreasing: '#faad14',
    stable: '#52c41a'
  }
  return colors[trend] || '#666'
}

const formatDateTime = (datetime: string) => {
  if (!datetime) return 'N/A'
  return datetime
}

const handleViewDetails = (drift: DriftDetection) => {
  selectedDrift.value = drift
  historyDialogVisible.value = true
}

const handleAcknowledge = (drift: DriftDetection) => {
  ElMessageBox.confirm(
      `Acknowledge drift detection for "${drift.deviceName}"?`,
      'Confirm Acknowledge',
      { type: 'info' }
  ).then(() => {
    const index = driftDetections.value.findIndex(d => d.id === drift.id)
    if (index !== -1) {
      driftDetections.value[index].status = 'acknowledged'
      ElMessage.success('Drift detection acknowledged')
    }
  }).catch(() => {})
}

const handleResolve = (drift: DriftDetection) => {
  ElMessageBox.confirm(
      `Mark drift detection for "${drift.deviceName}" as resolved?`,
      'Confirm Resolution',
      { type: 'success' }
  ).then(() => {
    const index = driftDetections.value.findIndex(d => d.id === drift.id)
    if (index !== -1) {
      driftDetections.value[index].status = 'resolved'
      ElMessage.success('Drift detection resolved')
    }
  }).catch(() => {})
}

const handleCalibrate = (drift: DriftDetection) => {
  selectedDevice.value = drift
  calibrationDialogVisible.value = true
}

const handleStartCalibration = () => {
  if (selectedDevice.value) {
    ElMessage.success(`Calibration started for ${selectedDevice.value.deviceName}`)
    calibrationDialogVisible.value = false
  }
}

const handleConfigureThresholds = () => {
  thresholdDialogVisible.value = true
}

const handleSaveThresholds = () => {
  ElMessage.success('Thresholds saved successfully')
  thresholdDialogVisible.value = false
}

const handleRefresh = () => {
  ElMessage.info('Refreshing data...')
  setTimeout(() => {
    ElMessage.success('Data refreshed')
  }, 1000)
}

const handleExportReport = () => {
  const reportData = {
    summary: statistics,
    detections: driftDetections.value,
    exportDate: new Date().toISOString()
  }
  const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `drift_detection_report_${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Report exported successfully')
}

const handleBulkCalibrate = () => {
  ElMessageBox.confirm(
      'Start bulk calibration for all devices with drift?',
      'Bulk Calibration',
      { type: 'warning' }
  ).then(() => {
    ElMessage.success('Bulk calibration started')
  }).catch(() => {})
}

// ==================== Initialize Charts ====================
const initCharts = () => {
  if (!driftTrendChart.value) return

  // Drift Trend Chart (Line)
  const trendChart = echarts.init(driftTrendChart.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Temperature Drift (%)', 'Humidity Drift (%)', 'Pressure Drift (%)'] },
    xAxis: { type: 'category', data: baselineHistory.value.map(h => h.date.substring(5)) },
    yAxis: { type: 'value', name: 'Drift Percentage (%)' },
    series: [
      {
        name: 'Temperature Drift (%)',
        type: 'line',
        data: [2.1, 2.3, 2.5, 2.8, 3.2, 3.5, 4.1],
        smooth: true,
        lineStyle: { color: '#ff4d4f', width: 2 },
        itemStyle: { color: '#ff4d4f' }
      },
      {
        name: 'Humidity Drift (%)',
        type: 'line',
        data: [1.5, 1.8, 2.2, 2.5, 2.9, 3.2, 3.8],
        smooth: true,
        lineStyle: { color: '#1890ff', width: 2 },
        itemStyle: { color: '#1890ff' }
      },
      {
        name: 'Pressure Drift (%)',
        type: 'line',
        data: [0.8, 0.9, 1.1, 1.3, 1.5, 1.7, 2.0],
        smooth: true,
        lineStyle: { color: '#52c41a', width: 2 },
        itemStyle: { color: '#52c41a' }
      }
    ]
  })

  // Drift Distribution Chart (Pie)
  const distChart = echarts.init(driftDistributionChart.value)
  distChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { top: 'bottom' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: criticalCount.value, name: 'Critical', itemStyle: { color: '#ff4d4f' } },
        { value: warningCount.value, name: 'Warning', itemStyle: { color: '#faad14' } },
        { value: infoCount.value, name: 'Info', itemStyle: { color: '#1890ff' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })

  // Device Health Chart (Gauge)
  const healthChart = echarts.init(deviceHealthChart.value)
  healthChart.setOption({
    series: [{
      type: 'gauge',
      center: ['50%', '50%'],
      radius: '70%',
      min: 0,
      max: 100,
      splitNumber: 10,
      progress: { show: true, width: 18, itemStyle: { color: '#52c41a' } },
      axisLine: { lineStyle: { width: 18, color: [[0.7, '#ff4d4f'], [0.85, '#faad14'], [1, '#52c41a']] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      pointer: { show: false },
      detail: { offsetCenter: [0, 0], valueAnimation: true, fontSize: 24, fontWeight: 'bold' },
      title: { show: false },
      data: [{ value: 85.5, name: 'Overall Health' }]
    }]
  })

  // Handle resize
  window.addEventListener('resize', () => {
    trendChart.resize()
    distChart.resize()
    healthChart.resize()
  })
}

// ==================== Watch for Tab Changes ====================
watch(activeTab, (newTab) => {
  if (newTab === 'dashboard' || newTab === 'analytics') {
    nextTick(() => {
      initCharts()
    })
  }
})

// ==================== Loading on Mount ====================
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
      if (activeTab.value === 'dashboard' || activeTab.value === 'analytics') {
        initCharts()
      }
    }, 400)
  }, 2000)
})
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
          <span class="loading-title">Loading Device Drift Detection</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="device-drift-detection">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2>Device Drift Detection</h2>
        <p>Monitor and detect sensor drift across all devices, automatically identify calibration needs, and prevent measurement inaccuracies</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleConfigureThresholds">
          <el-icon><Setting /></el-icon>
          Thresholds
        </el-button>
        <el-button @click="handleBulkCalibrate">
          <el-icon><Tools /></el-icon>
          Bulk Calibrate
        </el-button>
        <el-button @click="handleExportReport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
        <el-button @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-cards">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #e8f4ff">
            <el-icon color="#1890ff" size="28"><Monitor /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.totalDevices }}</div>
            <div class="stat-label">Total Devices</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #e6f7e6">
            <el-icon color="#52c41a" size="28"><Checked /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.totalDevices - statistics.devicesWithDrift }}</div>
            <div class="stat-label">Healthy Devices</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #fff7e6">
            <el-icon color="#faad14" size="28"><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.devicesWithDrift }}</div>
            <div class="stat-label">Devices with Drift</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #fdf0e8">
            <el-icon color="#ff7a45" size="28"><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.devicesCalibrated }}</div>
            <div class="stat-label">Calibrated (30d)</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Main Tabs -->
    <el-tabs v-model="activeTab" class="drift-tabs">
      <!-- Dashboard Tab -->
      <el-tab-pane label="Dashboard" name="dashboard">
        <el-row :gutter="16">
          <el-col :xs="24" :lg="16">
            <el-card class="dashboard-card" header="Drift Trend Analysis">
              <div ref="driftTrendChart" style="height: 350px"></div>
            </el-card>
          </el-col>
          <el-col :xs="24" :lg="8">
            <el-card class="dashboard-card" header="Drift Distribution">
              <div ref="driftDistributionChart" style="height: 350px"></div>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="16" style="margin-top: 16px">
          <el-col :span="24">
            <el-card class="dashboard-card" header="Device Health Overview">
              <div ref="deviceHealthChart" style="height: 300px"></div>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="16" style="margin-top: 16px">
          <el-col :span="24">
            <el-card class="dashboard-card" header="Recent Calibrations">
              <el-table :data="calibrationHistory.slice(0, 5)" style="width: 100%" stripe>
                <el-table-column prop="date" label="Date" width="120" />
                <el-table-column prop="deviceId" label="Device ID" width="150" />
                <el-table-column prop="type" label="Type" width="100">
                  <template #default="{ row }">
                    <el-tag :type="row.type === 'Auto' ? 'success' : 'warning'" size="small">{{ row.type }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="driftCorrected" label="Drift Corrected" width="120">
                  <template #default="{ row }">
                    <span>{{ row.driftCorrected }}%</span>
                  </template>
                </el-table-column>
                <el-table-column prop="result" label="Result" width="100">
                  <template #default="{ row }">
                    <el-tag :type="row.result === 'Success' ? 'success' : 'danger'" size="small">{{ row.result }}</el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- Active Drifts Tab -->
      <el-tab-pane label="Active Drifts" name="active">
        <div class="toolbar">
          <div class="toolbar-left">
            <el-input
                v-model="searchKeyword"
                placeholder="Search by device name or ID..."
                clearable
                style="width: 260px"
                :prefix-icon="Search"
            />
            <el-select v-model="severityFilter" placeholder="Severity" clearable style="width: 120px">
              <el-option label="All" value="" />
              <el-option label="Critical" value="critical" />
              <el-option label="Warning" value="warning" />
              <el-option label="Info" value="info" />
            </el-select>
            <el-select v-model="deviceTypeFilter" placeholder="Device Type" clearable style="width: 150px">
              <el-option label="All Types" value="" />
              <el-option label="Temperature" value="Temperature" />
              <el-option label="Humidity" value="Humidity" />
              <el-option label="Pressure" value="Pressure" />
              <el-option label="Air Quality" value="Air Quality" />
              <el-option label="Electrical" value="Electrical" />
              <el-option label="Flow" value="Flow" />
              <el-option label="Vibration" value="Vibration" />
            </el-select>
          </div>
          <div class="toolbar-right">
            <el-button type="primary" @click="handleBulkCalibrate">
              <el-icon><Tools /></el-icon>
              Bulk Calibrate
            </el-button>
          </div>
        </div>

        <el-table :data="paginatedDrifts" style="width: 100%; margin-top: 16px" stripe>
          <el-table-column prop="deviceName" label="Device" min-width="180">
            <template #default="{ row }">
              <div>
                <div class="device-name">{{ row.deviceName }}</div>
                <div class="device-id">{{ row.deviceId }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="location" label="Location" min-width="150" />
          <el-table-column prop="parameter" label="Parameter" width="120" />
          <el-table-column label="Drift" width="140">
            <template #default="{ row }">
              <div class="drift-indicator">
                <span class="drift-value" :class="row.driftPercentage > 0 ? 'positive' : 'negative'">
                  {{ row.driftPercentage > 0 ? '+' : '' }}{{ row.driftPercentage }}%
                </span>
                <span class="trend-icon">{{ getTrendIcon(row.trend) }}</span>
              </div>
              <div class="baseline-info">
                {{ row.baselineValue }} → {{ row.currentValue }}
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="severity" label="Severity" width="100">
            <template #default="{ row }">
              <el-tag :type="getSeverityType(row.severity)" size="small">
                {{ row.severity.toUpperCase() }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="Status" width="120">
            <template #default="{ row }">
              <el-tag :type="row.status === 'resolved' ? 'success' : row.status === 'acknowledged' ? 'warning' : 'danger'" size="small">
                {{ row.status.toUpperCase() }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="detectedAt" label="Detected" width="160" />
          <el-table-column label="Actions" width="200" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="handleViewDetails(row)">
                <el-icon><View /></el-icon>
                Details
              </el-button>
              <el-button v-if="row.status === 'active'" link type="warning" size="small" @click="handleAcknowledge(row)">
                <el-icon><Checked /></el-icon>
                Ack
              </el-button>
              <el-button v-if="row.status !== 'resolved'" link type="success" size="small" @click="handleCalibrate(row)">
                <el-icon><Tools /></el-icon>
                Calibrate
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- Pagination -->
        <div class="pagination-wrapper">
          <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[15, 30, 50, 100]"
              :total="filteredDrifts.length"
              layout="total, sizes, prev, pager, next, jumper"
          />
        </div>
      </el-tab-pane>

      <!-- Analytics Tab -->
      <el-tab-pane label="Analytics" name="analytics">
        <div class="analytics-container">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-card class="analytics-card" header="Drift by Device Type">
                <div class="drift-stats">
                  <div class="stat-row" v-for="type in ['Temperature', 'Humidity', 'Pressure', 'Air Quality', 'Electrical']" :key="type">
                    <span class="type-name">{{ type }}</span>
                    <div class="progress-bar-container">
                      <el-progress :percentage="Math.floor(Math.random() * 30) + 5" :color="'#ff4d4f'" />
                    </div>
                    <span class="percentage">{{ Math.floor(Math.random() * 30) + 5 }}%</span>
                  </div>
                </div>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card class="analytics-card" header="Calibration Success Rate">
                <div class="success-rate">
                  <div class="rate-circle">
                    <el-progress type="circle" :percentage="92" :width="150" :stroke-width="12" color="#52c41a">
                      <span class="rate-text">92%</span>
                    </el-progress>
                  </div>
                  <div class="rate-details">
                    <div class="detail-item">
                      <span class="label">Successful:</span>
                      <span class="value success">42</span>
                    </div>
                    <div class="detail-item">
                      <span class="label">Failed:</span>
                      <span class="value danger">4</span>
                    </div>
                    <div class="detail-item">
                      <span class="label">Avg Drift Fixed:</span>
                      <span class="value">5.2%</span>
                    </div>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="16" style="margin-top: 16px">
            <el-col :span="24">
              <el-card class="analytics-card" header="Drift Detection History">
                <el-table :data="driftDetections.slice(0, 10)" style="width: 100%" stripe>
                  <el-table-column prop="detectedAt" label="Date" width="160" />
                  <el-table-column prop="deviceName" label="Device" min-width="180" />
                  <el-table-column prop="parameter" label="Parameter" width="120" />
                  <el-table-column label="Drift" width="100">
                    <template #default="{ row }">
                      <span :class="row.driftPercentage > 0 ? 'positive' : 'negative'">
                        {{ row.driftPercentage > 0 ? '+' : '' }}{{ row.driftPercentage }}%
                      </span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="severity" label="Severity" width="100">
                    <template #default="{ row }">
                      <el-tag :type="getSeverityType(row.severity)" size="small">{{ row.severity }}</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="Resolution" width="120">
                    <template #default="{ row }">
                      <span v-if="row.status === 'resolved'">Resolved</span>
                      <span v-else-if="row.status === 'acknowledged'">Acknowledged</span>
                      <span v-else>Pending</span>
                    </template>
                  </el-table-column>
                </el-table>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>

      <!-- Calibration History Tab -->
      <el-tab-pane label="Calibration History" name="history">
        <div class="history-container">
          <div class="history-header">
            <h3>Calibration Records</h3>
            <el-button type="primary" @click="handleExportReport">
              <el-icon><Download /></el-icon>
              Export History
            </el-button>
          </div>

          <el-table :data="calibrationHistory" style="width: 100%; margin-top: 16px" stripe>
            <el-table-column prop="date" label="Date" width="120" />
            <el-table-column prop="deviceId" label="Device ID" width="150" />
            <el-table-column prop="type" label="Type" width="100">
              <template #default="{ row }">
                <el-tag :type="row.type === 'Auto' ? 'success' : 'warning'" size="small">{{ row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="driftCorrected" label="Drift Corrected" width="140">
              <template #default="{ row }">
                <span>{{ row.driftCorrected }}%</span>
              </template>
            </el-table-column>
            <el-table-column prop="result" label="Result" width="100">
              <template #default="{ row }">
                <el-tag :type="row.result === 'Success' ? 'success' : 'danger'" size="small">{{ row.result }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Actions" width="120">
              <template #default="{ row }">
                <el-button link type="primary" size="small">
                  <el-icon><View /></el-icon>
                  Details
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Threshold Configuration Dialog -->
    <el-dialog v-model="thresholdDialogVisible" title="Drift Detection Thresholds" width="600px">
      <el-form :model="driftThresholds" label-width="140px">
        <div v-for="(threshold, deviceType) in driftThresholds" :key="deviceType" class="threshold-group">
          <div class="threshold-title">{{ deviceType.toUpperCase() }}</div>
          <el-form-item :label="'Warning (%)'">
            <el-slider v-model="threshold.warning" :min="0" :max="30" :step="1" />
            <span class="threshold-value">{{ threshold.warning }}%</span>
          </el-form-item>
          <el-form-item :label="'Critical (%)'">
            <el-slider v-model="threshold.critical" :min="0" :max="50" :step="1" />
            <span class="threshold-value">{{ threshold.critical }}%</span>
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="thresholdDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleSaveThresholds">Save</el-button>
      </template>
    </el-dialog>

    <!-- Calibration Dialog -->
    <el-dialog v-model="calibrationDialogVisible" :title="`Calibrate - ${selectedDevice?.deviceName}`" width="500px">
      <el-form label-width="120px">
        <el-form-item label="Device ID">
          <span>{{ selectedDevice?.deviceId }}</span>
        </el-form-item>
        <el-form-item label="Current Drift">
          <span :class="selectedDevice?.driftPercentage > 0 ? 'positive' : 'negative'">
            {{ selectedDevice?.driftPercentage > 0 ? '+' : '' }}{{ selectedDevice?.driftPercentage }}%
          </span>
        </el-form-item>
        <el-form-item label="Calibration Type">
          <el-radio-group v-model="calibrationType">
            <el-radio label="auto">Auto Calibration</el-radio>
            <el-radio label="manual">Manual Calibration</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Notes">
          <el-input type="textarea" :rows="3" placeholder="Enter calibration notes..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="calibrationDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleStartCalibration">Start Calibration</el-button>
      </template>
    </el-dialog>

    <!-- Drift Details Dialog -->
    <el-dialog v-model="historyDialogVisible" :title="`Drift Details - ${selectedDrift?.deviceName}`" width="700px">
      <div v-if="selectedDrift" class="drift-details">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Device ID">{{ selectedDrift.deviceId }}</el-descriptions-item>
          <el-descriptions-item label="Device Name">{{ selectedDrift.deviceName }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedDrift.location }}</el-descriptions-item>
          <el-descriptions-item label="Device Type">{{ selectedDrift.deviceType }}</el-descriptions-item>
          <el-descriptions-item label="Parameter">{{ selectedDrift.parameter }}</el-descriptions-item>
          <el-descriptions-item label="Severity">
            <el-tag :type="getSeverityType(selectedDrift.severity)">{{ selectedDrift.severity.toUpperCase() }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Baseline Value">{{ selectedDrift.baselineValue }}</el-descriptions-item>
          <el-descriptions-item label="Current Value">{{ selectedDrift.currentValue }}</el-descriptions-item>
          <el-descriptions-item label="Drift Percentage">
            <span :class="selectedDrift.driftPercentage > 0 ? 'positive' : 'negative'">
              {{ selectedDrift.driftPercentage > 0 ? '+' : '' }}{{ selectedDrift.driftPercentage }}%
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="Trend">
            <span :style="{ color: getTrendColor(selectedDrift.trend) }">
              {{ getTrendIcon(selectedDrift.trend) }} {{ selectedDrift.trend }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="Detected At">{{ selectedDrift.detectedAt }}</el-descriptions-item>
          <el-descriptions-item label="Status">{{ selectedDrift.status }}</el-descriptions-item>
          <el-descriptions-item label="Recommendation" :span="2">
            <el-alert :title="selectedDrift.recommendation" type="warning" :closable="false" />
          </el-descriptions-item>
        </el-descriptions>
      </div>
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
  font-size: 20px;
  font-weight: 600;
  color: #e2e8f0;
  display: flex;
  justify-content: center;
  align-items: baseline;
  gap: 4px;
}

.loading-title {
  font-size: 20px;
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
  font-weight: 500;
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
.device-drift-detection {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: calc(100vh - 60px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.header-left h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.header-left p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
}

.stat-label {
  font-size: 14px;
  color: #8c8c8c;
  margin-top: 4px;
}

.drift-tabs {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.toolbar-left {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.toolbar-right {
  display: flex;
  gap: 12px;
}

/* Dashboard */
.dashboard-card {
  height: 100%;
}

/* Device Table */
.device-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.device-id {
  font-size: 12px;
  color: #999;
  font-family: monospace;
}

.drift-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.drift-value {
  font-weight: 600;
  font-size: 14px;
}

.drift-value.positive {
  color: #ff4d4f;
}

.drift-value.negative {
  color: #52c41a;
}

.baseline-info {
  font-size: 11px;
  color: #999;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

/* Analytics */
.analytics-container {
  padding: 16px 0;
}

.analytics-card {
  height: 100%;
}

.drift-stats {
  padding: 16px;
}

.stat-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.stat-row .type-name {
  width: 100px;
  font-weight: 500;
}

.stat-row .progress-bar-container {
  flex: 1;
}

.stat-row .percentage {
  width: 45px;
  font-weight: 500;
  color: #ff4d4f;
}

.success-rate {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.rate-circle {
  margin-bottom: 24px;
}

.rate-text {
  font-size: 24px;
  font-weight: bold;
}

.rate-details {
  width: 100%;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 8px;
}

.rate-details .detail-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
}

.detail-item .label {
  color: #666;
}

.detail-item .value.success {
  color: #52c41a;
  font-weight: 600;
}

.detail-item .value.danger {
  color: #ff4d4f;
  font-weight: 600;
}

/* Threshold Dialog */
.threshold-group {
  margin-bottom: 24px;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 8px;
}

.threshold-title {
  font-weight: 600;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e8e8e8;
}

.threshold-value {
  margin-left: 12px;
  font-size: 12px;
  color: #666;
}

/* History */
.history-container {
  padding: 16px 0;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-header h3 {
  margin: 0;
}

/* Drift Details */
.drift-details {
  padding: 8px 0;
}

.positive {
  color: #ff4d4f;
}

.negative {
  color: #52c41a;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
  }

  .header-right {
    margin-top: 16px;
    width: 100%;
  }

  .toolbar {
    flex-direction: column;
    gap: 12px;
  }

  .toolbar-left {
    width: 100%;
  }

  .toolbar-right {
    width: 100%;
  }
}

:deep(.el-card__header) {
  font-weight: 600;
  background-color: #fafafa;
  border-bottom: 1px solid #f0f0f0;
}

:deep(.el-tabs__header) {
  margin-bottom: 20px;
}

:deep(.el-table) {
  font-size: 13px;
}
</style>