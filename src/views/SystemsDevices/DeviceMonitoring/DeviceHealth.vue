<template>
  <!-- ==================== Loading Screen ==================== -->
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
        <div class="loading-tip">Device Health Monitor</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- ==================== Main Content ==================== -->
  <div v-else class="device-health-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/systems-devices/device-inventory' }">
            Systems & Devices
          </el-breadcrumb-item>
          <el-breadcrumb-item>Device Monitoring</el-breadcrumb-item>
          <el-breadcrumb-item>Device Health</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button :icon="Refresh" @click="refreshData" :loading="refreshing">Refresh</el-button>
        <el-button type="primary" :icon="Download" @click="exportReport">Export Report</el-button>
      </div>
    </div>

    <!-- 健康度统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card healthy">
        <div class="stat-icon"><el-icon><CircleCheckFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.healthy }}</span>
          <span class="stat-label">Healthy (≥80)</span>
        </div>
      </div>
      <div class="stat-card fair">
        <div class="stat-icon"><el-icon><WarningFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.fair }}</span>
          <span class="stat-label">Fair (60-79)</span>
        </div>
      </div>
      <div class="stat-card poor">
        <div class="stat-icon"><el-icon><CircleCloseFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.poor }}</span>
          <span class="stat-label">Poor (40-59)</span>
        </div>
      </div>
      <div class="stat-card critical">
        <div class="stat-icon"><el-icon><WarningFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.critical }}</span>
          <span class="stat-label">Critical (&lt;40)</span>
        </div>
      </div>
    </div>

    <!-- 整体健康度仪表盘 -->
    <div class="dashboard-row">
      <div class="gauge-card">
        <div class="card-header">
          <h3><el-icon><DataBoard /></el-icon> Overall Fleet Health</h3>
        </div>
        <div ref="gaugeChartRef" class="gauge-chart"></div>
        <div class="gauge-stats">
          <div class="gauge-stat">
            <span class="stat-label">Average Health Score</span>
            <span class="stat-value">{{ avgHealthScore.toFixed(1) }}%</span>
          </div>
          <div class="gauge-stat">
            <span class="stat-label">Devices Needing Attention</span>
            <span class="stat-value danger">{{ stats.poor + stats.critical }}</span>
          </div>
        </div>
      </div>

      <div class="trend-card">
        <div class="card-header">
          <h3><el-icon><TrendCharts /></el-icon> Health Trend (Last 30 Days)</h3>
        </div>
        <div ref="trendChartRef" class="trend-chart"></div>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchKeyword"
            placeholder="Search by device name or ID"
            clearable
            :prefix-icon="Search"
            style="width: 240px"
            @clear="filterDevices"
            @keyup.enter="filterDevices"
        />
        <el-select v-model="filterSystem" placeholder="System Type" clearable style="width: 140px" @change="filterDevices">
          <el-option label="All Systems" value="" />
          <el-option label="HVAC" value="hvac" />
          <el-option label="Lighting" value="lighting" />
          <el-option label="Security" value="sas" />
          <el-option label="Fire Alarm" value="fas" />
          <el-option label="Plumbing" value="plumbing" />
        </el-select>
        <el-select v-model="filterHealth" placeholder="Health Status" clearable style="width: 140px" @change="filterDevices">
          <el-option label="All" value="" />
          <el-option label="Healthy (≥80)" value="healthy" />
          <el-option label="Fair (60-79)" value="fair" />
          <el-option label="Poor (40-59)" value="poor" />
          <el-option label="Critical (<40)" value="critical" />
        </el-select>
        <el-select v-model="filterArea" placeholder="Area" clearable style="width: 140px" @change="filterDevices">
          <el-option label="All Areas" value="" />
          <el-option v-for="area in areas" :key="area" :label="area" :value="area" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-switch v-model="showOnlyAttention" active-text="Show Needs Attention" @change="filterDevices" />
      </div>
    </div>

    <!-- 设备健康列表 -->
    <div class="device-table-container">
      <el-table :data="filteredDevices" stripe border style="width: 100%" v-loading="tableLoading" @row-click="showDeviceDetail">
        <el-table-column type="index" label="#" width="50" />
        <el-table-column label="Device" min-width="200">
          <template #default="{ row }">
            <div class="device-cell">
              <el-avatar :src="row.imageUrl" :size="36" shape="square" fit="cover">
                <template #error><el-icon><Cpu /></el-icon></template>
              </el-avatar>
              <div class="device-info">
                <span class="device-name">{{ row.name }}</span>
                <span class="device-model">{{ row.model }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="serialNumber" label="Serial No" width="150" />
        <el-table-column label="System" width="120">
          <template #default="{ row }">
            <el-tag :type="getSystemTagType(row.systemType)" size="small">{{ getSystemLabel(row.systemType) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Health Score" width="150">
          <template #default="{ row }">
            <div class="health-cell">
              <el-progress :percentage="row.healthScore" :stroke-width="10" :color="getHealthColor(row.healthScore)" :show-text="false" style="width: 100px" />
              <span :class="getHealthClass(row.healthScore)" style="margin-left: 12px">{{ row.healthScore.toFixed(1) }}%</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="110">
          <template #default="{ row }">
            <div class="status-cell">
              <div class="status-indicator" :class="row.status"></div>
              <span>{{ row.status.toUpperCase() }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="remainingLife" label="Remaining Life" width="130">
          <template #default="{ row }">
            <span :class="{ 'text-warning': row.remainingLife < 3, 'text-danger': row.remainingLife < 1 }">
              {{ row.remainingLife.toFixed(1) }} years
            </span>
          </template>
        </el-table-column>
        <el-table-column label="MTBF" width="120">
          <template #default="{ row }">{{ row.mtbf.toFixed(0) }} hours</template>
        </el-table-column>
        <el-table-column label="Last Incident" width="160">
          <template #default="{ row }">{{ row.lastIncident ? formatDateTime(row.lastIncident) : '-' }}</template>
        </el-table-column>
        <el-table-column label="Actions" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text @click.stop="viewDetails(row)">Details</el-button>
            <el-button size="small" text type="primary" @click.stop="viewRecommendations(row)">Recommend</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="totalRecords"
            layout="total, sizes, prev, pager, next, jumper"
            background
            @size-change="filterDevices"
            @current-change="filterDevices"
        />
      </div>
    </div>

    <!-- 维护建议面板 -->
    <div class="recommendations-panel" v-if="recommendations.length > 0">
      <div class="recommendations-header">
        <h3><el-icon><Tools /></el-icon> Maintenance Recommendations</h3>
        <el-tag type="warning">{{ recommendations.length }} recommendations</el-tag>
      </div>
      <div class="recommendations-list">
        <div v-for="rec in recommendations" :key="rec.id" class="recommendation-item" :class="rec.priority">
          <div class="rec-icon">
            <el-icon v-if="rec.priority === 'high'"><WarningFilled /></el-icon>
            <el-icon v-else-if="rec.priority === 'medium'"><InfoFilled /></el-icon>
            <el-icon v-else><SuccessFilled /></el-icon>
          </div>
          <div class="rec-content">
            <div class="rec-title">{{ rec.title }}</div>
            <div class="rec-description">{{ rec.description }}</div>
            <div class="rec-device">Device: {{ rec.deviceName }}</div>
          </div>
          <div class="rec-actions">
            <el-button size="small" @click="createWorkOrder(rec)">Create Work Order</el-button>
            <el-button size="small" type="primary" @click="acknowledgeRecommendation(rec)">Acknowledge</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 设备详情对话框 -->
    <el-dialog v-model="detailDialogVisible" :title="selectedDevice?.name || 'Device Health Details'" width="650px">
      <div v-if="selectedDevice" class="device-detail">
        <div class="detail-header">
          <el-avatar :src="selectedDevice.imageUrl" :size="60" shape="square" fit="cover">
            <template #error><el-icon><Cpu /></el-icon></template>
          </el-avatar>
          <div class="detail-title">
            <h2>{{ selectedDevice.name }}</h2>
            <p>{{ selectedDevice.model }} | {{ selectedDevice.manufacturer }}</p>
          </div>
        </div>

        <el-row :gutter="20">
          <el-col :span="12">
            <div class="health-gauge">
              <div ref="detailGaugeRef" class="detail-gauge"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="health-metrics">
              <div class="metric-item">
                <span class="metric-label">Health Score</span>
                <span class="metric-value" :class="getHealthClass(selectedDevice.healthScore)">{{ selectedDevice.healthScore.toFixed(1) }}%</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Remaining Life</span>
                <span class="metric-value">{{ selectedDevice.remainingLife.toFixed(1) }} years</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">MTBF</span>
                <span class="metric-value">{{ selectedDevice.mtbf.toFixed(0) }} hours</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">MTTR</span>
                <span class="metric-value">{{ selectedDevice.mttr.toFixed(1) }} hours</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Availability</span>
                <span class="metric-value">{{ selectedDevice.availability.toFixed(1) }}%</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">Last Maintenance</span>
                <span class="metric-value">{{ formatDate(selectedDevice.lastMaintenance) }}</span>
              </div>
            </div>
          </el-col>
        </el-row>

        <el-divider />

        <div class="health-factors">
          <h4>Health Factors</h4>
          <div v-for="factor in selectedDevice.healthFactors" :key="factor.name" class="factor-item">
            <span class="factor-name">{{ factor.name }}</span>
            <el-progress :percentage="factor.score" :stroke-width="8" :color="getHealthColor(factor.score)" :format="() => `${factor.score.toFixed(1)}%`" />
          </div>
        </div>

        <div class="detail-actions">
          <el-button type="primary" @click="createWorkOrder(selectedDevice)">Create Work Order</el-button>
          <el-button @click="exportDeviceReport(selectedDevice)">Export Report</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Refresh, Download, Search, DataBoard, TrendCharts, CircleCheckFilled,
  WarningFilled, CircleCloseFilled, Tools, InfoFilled, SuccessFilled, Cpu
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading device health data...')
const refreshing = ref(false)
const tableLoading = ref(false)
const loadingMessages = ['Initializing...', 'Loading device data...', 'Analyzing health metrics...', 'Generating recommendations...', 'Almost ready...']

// ==================== State ====================
const searchKeyword = ref('')
const filterSystem = ref('')
const filterHealth = ref('')
const filterArea = ref('')
const showOnlyAttention = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const totalRecords = ref(0)
const detailDialogVisible = ref(false)
const selectedDevice = ref<any>(null)
let gaugeChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null
let detailGauge: echarts.ECharts | null = null
const gaugeChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()
const detailGaugeRef = ref<HTMLElement>()

// ==================== Data ====================
interface DeviceHealth {
  id: string
  name: string
  model: string
  manufacturer: string
  serialNumber: string
  systemType: string
  area: string
  status: 'online' | 'offline' | 'warning' | 'error'
  imageUrl: string
  healthScore: number
  remainingLife: number
  mtbf: number
  mttr: number
  availability: number
  lastMaintenance: string
  lastIncident: string | null
  healthFactors: Array<{ name: string; score: number }>
}

interface Recommendation {
  id: string
  deviceId: string
  deviceName: string
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
}

const devices = ref<DeviceHealth[]>([])
const recommendations = ref<Recommendation[]>([])

// 保留一位小数
const toOneDecimal = (num: number): number => Math.round(num * 10) / 10

// 生成模拟设备健康数据（所有数值保留一位小数）
const generateDevices = (): DeviceHealth[] => {
  const baseDevices = [
    { id: '1', name: 'AHU-B2-01 Air Handler', model: 'Carrier 39G', manufacturer: 'Carrier', serial: 'CA-2024-B201', system: 'hvac', area: 'Basement B2', img: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567.webp', status: 'online' },
    { id: '2', name: 'FCU-B2-01 Fan Coil', model: 'Daikin FXMQ', manufacturer: 'Daikin', serial: 'DK-2024-B201', system: 'hvac', area: 'Basement B2', img: 'https://aegisnx.com/wp-content/uploads/2026/05/52013141234431.webp', status: 'online' },
    { id: '3', name: 'CH-B2-01 Chiller', model: 'Carrier AquaEdge', manufacturer: 'Carrier', serial: 'CA-2024-B202', system: 'hvac', area: 'Basement B2', img: 'https://aegisnx.com/wp-content/uploads/2026/05/52013145678.jpg', status: 'warning' },
    { id: '4', name: 'EF-B2-02 Exhaust Fan', model: 'Greenheck CUBE', manufacturer: 'Greenheck', serial: 'GH-2024-B202', system: 'hvac', area: 'Basement B2', img: 'https://aegisnx.com/wp-content/uploads/2026/05/520131452044.webp', status: 'error' },
    { id: '5', name: 'LIGHT-B2-01 Controller', model: 'Philips Dynalite', manufacturer: 'Philips', serial: 'PH-2024-B201', system: 'lighting', area: 'Basement B2', img: 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp', status: 'online' },
    { id: '6', name: 'ACS-1F-01 Entrance', model: 'HID VertX', manufacturer: 'HID', serial: 'HD-2024-1F01', system: 'sas', area: 'Lobby 1F', img: 'https://aegisnx.com/wp-content/uploads/2026/05/52013147643.jpg', status: 'online' },
    { id: '7', name: 'SD-1F-01 Smoke Detector', model: 'Honeywell XLS', manufacturer: 'Honeywell', serial: 'HW-2024-1F01', system: 'fas', area: 'Lobby 1F', img: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567123.jpg', status: 'online' },
    { id: '8', name: 'PUMP-B2-02 Booster', model: 'Grundfos CR', manufacturer: 'Grundfos', serial: 'GF-2024-B202', system: 'plumbing', area: 'Basement B2', img: 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png', status: 'warning' },
    { id: '9', name: 'AHU-2F-01 Air Handler', model: 'Trane IntelliPak', manufacturer: 'Trane', serial: 'TR-2024-2F01', system: 'hvac', area: 'Office 2F', img: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567.webp', status: 'error' }
  ]

  return baseDevices.map(device => {
    let healthScore: number
    let remainingLife: number
    if (device.id === '3') { healthScore = 65.5; remainingLife = 4.5 }
    else if (device.id === '4') { healthScore = 35.2; remainingLife = 0.5 }
    else if (device.id === '8') { healthScore = 55.8; remainingLife = 2.2 }
    else if (device.id === '9') { healthScore = 28.6; remainingLife = 0.3 }
    else { healthScore = toOneDecimal(75 + Math.random() * 20); remainingLife = toOneDecimal(5 + Math.random() * 8) }

    healthScore = toOneDecimal(Math.min(100, Math.max(0, healthScore)))
    remainingLife = toOneDecimal(remainingLife)

    return {
      id: device.id,
      name: device.name,
      model: device.model,
      manufacturer: device.manufacturer,
      serialNumber: device.serial,
      systemType: device.system,
      area: device.area,
      status: device.status as any,
      imageUrl: device.img,
      healthScore,
      remainingLife,
      mtbf: Math.round(8000 + Math.random() * 4000),
      mttr: toOneDecimal(2 + Math.random() * 6),
      availability: toOneDecimal(95 + Math.random() * 4.9),
      lastMaintenance: new Date(Date.now() - Math.random() * 180 * 24 * 3600000).toISOString().split('T')[0],
      lastIncident: healthScore < 60 ? new Date(Date.now() - Math.random() * 30 * 24 * 3600000).toISOString() : null,
      healthFactors: [
        { name: 'Performance', score: toOneDecimal(Math.min(100, Math.max(0, healthScore + (Math.random() - 0.5) * 15))) },
        { name: 'Reliability', score: toOneDecimal(Math.min(100, Math.max(0, healthScore + (Math.random() - 0.5) * 10))) },
        { name: 'Maintenance', score: toOneDecimal(Math.min(100, Math.max(0, healthScore + (Math.random() - 0.5) * 12))) },
        { name: 'Age', score: toOneDecimal(Math.min(100, Math.max(0, healthScore + (Math.random() - 0.5) * 20))) }
      ]
    }
  })
}

// 生成维护建议
const generateRecommendations = (devicesList: DeviceHealth[]): Recommendation[] => {
  const recs: Recommendation[] = []
  devicesList.forEach(device => {
    if (device.healthScore < 40) {
      recs.push({
        id: `rec-${device.id}`,
        deviceId: device.id,
        deviceName: device.name,
        title: 'Critical Health Alert',
        description: `Device health score is critical (${device.healthScore.toFixed(1)}%). Immediate maintenance required.`,
        priority: 'high'
      })
    } else if (device.healthScore < 60) {
      recs.push({
        id: `rec-${device.id}`,
        deviceId: device.id,
        deviceName: device.name,
        title: 'Preventive Maintenance Recommended',
        description: `Device health score is low (${device.healthScore.toFixed(1)}%). Schedule maintenance soon.`,
        priority: 'medium'
      })
    } else if (device.remainingLife < 1) {
      recs.push({
        id: `rec-life-${device.id}`,
        deviceId: device.id,
        deviceName: device.name,
        title: 'End of Life Approaching',
        description: `Device has less than 1 year of remaining life. Plan for replacement.`,
        priority: 'high'
      })
    } else if (device.remainingLife < 3) {
      recs.push({
        id: `rec-life-${device.id}`,
        deviceId: device.id,
        deviceName: device.name,
        title: 'Lifecycle Review Needed',
        description: `Device has ${device.remainingLife.toFixed(1)} years of remaining life. Consider lifecycle planning.`,
        priority: 'low'
      })
    }
  })
  return recs
}

// 生成健康趋势数据（所有数值保留一位小数）
const generateHealthTrend = () => {
  const days = []
  const scores = []
  const now = new Date()
  for (let i = 29; i >= 0; i--) {
    const date = new Date(now.getTime() - i * 24 * 3600000)
    days.push(`${date.getMonth() + 1}/${date.getDate()}`)
    const baseScore = 75
    const trend = Math.sin(i * 0.2) * 5
    const random = (Math.random() - 0.5) * 3
    scores.push(toOneDecimal(Math.min(100, Math.max(0, baseScore + trend + random))))
  }
  return { days, scores }
}

// 统计
const stats = computed(() => {
  const healthy = devices.value.filter(d => d.healthScore >= 80).length
  const fair = devices.value.filter(d => d.healthScore >= 60 && d.healthScore < 80).length
  const poor = devices.value.filter(d => d.healthScore >= 40 && d.healthScore < 60).length
  const critical = devices.value.filter(d => d.healthScore < 40).length
  return { healthy, fair, poor, critical }
})

const avgHealthScore = computed(() => {
  if (devices.value.length === 0) return 0
  const sum = devices.value.reduce((s, d) => s + d.healthScore, 0)
  return toOneDecimal(sum / devices.value.length)
})

const areas = computed(() => {
  const areaSet = new Set<string>()
  devices.value.forEach(d => areaSet.add(d.area))
  return Array.from(areaSet).sort()
})

const filteredDevices = computed(() => {
  let result = [...devices.value]
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    result = result.filter(d => d.name.toLowerCase().includes(kw) || d.id.includes(kw))
  }
  if (filterSystem.value) result = result.filter(d => d.systemType === filterSystem.value)
  if (filterHealth.value) {
    if (filterHealth.value === 'healthy') result = result.filter(d => d.healthScore >= 80)
    else if (filterHealth.value === 'fair') result = result.filter(d => d.healthScore >= 60 && d.healthScore < 80)
    else if (filterHealth.value === 'poor') result = result.filter(d => d.healthScore >= 40 && d.healthScore < 60)
    else if (filterHealth.value === 'critical') result = result.filter(d => d.healthScore < 40)
  }
  if (filterArea.value) result = result.filter(d => d.area === filterArea.value)
  if (showOnlyAttention.value) result = result.filter(d => d.healthScore < 70 || d.remainingLife < 3)
  totalRecords.value = result.length
  const start = (currentPage.value - 1) * pageSize.value
  return result.slice(start, start + pageSize.value)
})

// Helper 函数
const getSystemLabel = (type: string) => ({ hvac: 'HVAC', lighting: 'Lighting', sas: 'Security', fas: 'Fire Alarm', plumbing: 'Plumbing' }[type] || type)
const getSystemTagType = (type: string) => ({ hvac: 'primary', lighting: 'success', sas: 'danger', fas: 'warning', plumbing: 'info' }[type] || 'info')
const getHealthColor = (score: number) => score >= 80 ? '#67c23a' : score >= 60 ? '#409eff' : score >= 40 ? '#e6a23c' : '#f56c6c'
const getHealthClass = (score: number) => score >= 80 ? 'text-success' : score >= 60 ? 'text-primary' : score >= 40 ? 'text-warning' : 'text-danger'
const formatDate = (dateStr: string) => new Date(dateStr).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
const formatDateTime = (dateStr: string) => new Date(dateStr).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })

// 图表初始化
const initGaugeChart = () => {
  if (!gaugeChartRef.value) return
  if (gaugeChart) gaugeChart.dispose()
  gaugeChart = echarts.init(gaugeChartRef.value)
  gaugeChart.setOption({
    series: [{
      type: 'gauge',
      center: ['50%', '50%'],
      radius: '70%',
      startAngle: 210,
      endAngle: -30,
      min: 0,
      max: 100,
      splitNumber: 5,
      progress: { show: true, width: 18, itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: '#f56c6c' }, { offset: 0.5, color: '#e6a23c' }, { offset: 1, color: '#67c23a' }] } } },
      axisLine: { lineStyle: { width: 18, color: [[0.4, '#f56c6c'], [0.6, '#e6a23c'], [0.8, '#409eff'], [1, '#67c23a']] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      pointer: { show: false },
      detail: { offsetCenter: [0, 20], valueAnimation: true, fontSize: 24, fontWeight: 'bold', color: '#1e293b', formatter: (value: number) => value.toFixed(1) + '%' },
      title: { show: false },
      data: [{ value: avgHealthScore.value, name: 'Health Score' }]
    }]
  })
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()
  trendChart = echarts.init(trendChartRef.value)
  const { days, scores } = generateHealthTrend()
  trendChart.setOption({
    tooltip: { trigger: 'axis', formatter: (params: any) => `${params[0].axisValue}<br/>Health Score: ${params[0].value.toFixed(1)}%` },
    grid: { top: 30, right: 20, bottom: 20, left: 50, containLabel: true },
    xAxis: { type: 'category', data: days, axisLabel: { rotate: 45, interval: 5 } },
    yAxis: { type: 'value', name: 'Health Score (%)', min: 0, max: 100 },
    series: [{
      type: 'line', data: scores, smooth: true, lineStyle: { color: '#409eff', width: 2 },
      areaStyle: { opacity: 0.1, color: '#409eff' }, symbol: 'circle', symbolSize: 6
    }]
  })
}

const initDetailGauge = () => {
  if (!detailGaugeRef.value || !selectedDevice.value) return
  if (detailGauge) detailGauge.dispose()
  detailGauge = echarts.init(detailGaugeRef.value)
  detailGauge.setOption({
    series: [{
      type: 'gauge', center: ['50%', '50%'], radius: '80%', startAngle: 210, endAngle: -30,
      min: 0, max: 100, splitNumber: 5,
      progress: { show: true, width: 15, itemStyle: { color: getHealthColor(selectedDevice.value.healthScore) } },
      axisLine: { lineStyle: { width: 15, color: [[0.4, '#f56c6c'], [0.6, '#e6a23c'], [0.8, '#409eff'], [1, '#67c23a']] } },
      axisTick: { show: false }, splitLine: { show: false }, axisLabel: { show: false }, pointer: { show: false },
      detail: { offsetCenter: [0, 20], valueAnimation: true, fontSize: 20, fontWeight: 'bold', color: getHealthColor(selectedDevice.value.healthScore), formatter: (value: number) => value.toFixed(1) + '%' },
      title: { show: false }, data: [{ value: selectedDevice.value.healthScore, name: 'Health Score' }]
    }]
  })
}

// 数据加载
const loadData = async () => {
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 500))
  devices.value = generateDevices()
  recommendations.value = generateRecommendations(devices.value)
  tableLoading.value = false
  initGaugeChart()
  initTrendChart()
}

const refreshData = async () => {
  refreshing.value = true
  await loadData()
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

const filterDevices = () => { currentPage.value = 1 }

// Actions
const showDeviceDetail = (device: DeviceHealth) => {
  selectedDevice.value = device
  detailDialogVisible.value = true
  nextTick(() => initDetailGauge())
}

const viewDetails = (device: DeviceHealth) => showDeviceDetail(device)
const viewRecommendations = (device: DeviceHealth) => ElMessage.info(`Viewing recommendations for ${device.name}`)
const createWorkOrder = (item: any) => ElMessage.info(`Creating work order for ${item.deviceName || item.name}`)
const acknowledgeRecommendation = (rec: Recommendation) => {
  recommendations.value = recommendations.value.filter(r => r.id !== rec.id)
  ElMessage.success(`Recommendation acknowledged: ${rec.title}`)
}
const exportReport = () => ElMessage.success('Exporting health report')
const exportDeviceReport = (device: DeviceHealth) => ElMessage.success(`Exporting report for ${device.name}`)

// 窗口适配
const handleResize = () => {
  if (gaugeChart) gaugeChart.resize()
  if (trendChart) trendChart.resize()
  if (detailGauge) detailGauge.resize()
}

// 生命周期
onMounted(() => {
  let msgIdx = 0
  const msgInt = setInterval(() => {
    if (msgIdx < loadingMessages.length - 1) {
      msgIdx++
      loadingMessage.value = loadingMessages[msgIdx]
    }
  }, 400)
  const progInt = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)
  setTimeout(() => {
    clearInterval(msgInt)
    clearInterval(progInt)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      loadData()
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (gaugeChart) gaugeChart.dispose()
  if (trendChart) trendChart.dispose()
  if (detailGauge) detailGauge.dispose()
})
</script>

<style scoped>
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
.loading-overlay { position: relative; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; backdrop-filter: blur(2px); }
.loading-content { text-align: center; padding: 40px; border-radius: 32px; background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(20px); border: 1px solid rgba(59, 130, 246, 0.3); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); animation: fadeInUp 0.6s ease-out; }
.loading-spinner { position: relative; width: 80px; height: 80px; margin: 0 auto 24px; }
.spinner-ring { position: absolute; width: 100%; height: 100%; border-radius: 50%; border: 3px solid transparent; animation: spin 1.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite; }
.spinner-ring:nth-child(1) { border-top-color: #3b82f6; animation-delay: 0s; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.loading-text { margin-bottom: 24px; font-size: 28px; font-weight: 700; color: #e2e8f0; display: flex; justify-content: center; align-items: baseline; gap: 4px; }
.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce { 0%, 80%, 100% { transform: scale(0); opacity: 0.3; } 40% { transform: scale(1); opacity: 1; } }
.loading-progress { width: 280px; height: 4px; background: rgba(255, 255, 255, 0.1); border-radius: 4px; overflow: hidden; margin: 0 auto 16px; }
.progress-bar { height: 100%; background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec489a); border-radius: 4px; transition: width 0.3s ease; background-size: 200% auto; animation: shimmer 2s linear infinite; }
@keyframes shimmer { 0% { background-position: 0% 0%; } 100% { background-position: 200% 0%; } }
.loading-tip { font-size: 13px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 8px; font-weight: 500; }
.loading-subtip { font-size: 11px; color: #64748b; letter-spacing: 0.5px; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

.device-health-page { padding: 20px; background: #f5f7fa; min-height: 100%; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }

.stats-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 24px; }
.stat-card { background: white; border-radius: 16px; padding: 20px; display: flex; align-items: center; gap: 16px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); transition: all 0.3s ease; }
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
.stat-card.healthy .stat-icon .el-icon { color: #67c23a; }
.stat-card.fair .stat-icon .el-icon { color: #409eff; }
.stat-card.poor .stat-icon .el-icon { color: #e6a23c; }
.stat-card.critical .stat-icon .el-icon { color: #f56c6c; }
.stat-icon .el-icon { font-size: 32px; }
.stat-info .stat-value { font-size: 28px; font-weight: 700; color: #1e293b; }
.stat-info .stat-label { font-size: 13px; color: #64748b; }

.dashboard-row { display: grid; grid-template-columns: 1fr 1.5fr; gap: 20px; margin-bottom: 24px; }
.gauge-card, .trend-card { background: white; border-radius: 16px; padding: 20px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.card-header { margin-bottom: 16px; }
.card-header h3 { display: flex; align-items: center; gap: 8px; margin: 0; font-size: 16px; }
.gauge-chart { width: 100%; height: 220px; }
.gauge-stats { display: flex; justify-content: space-around; margin-top: 16px; padding-top: 16px; border-top: 1px solid #e2e8f0; }
.gauge-stat { text-align: center; }
.gauge-stat .stat-label { font-size: 12px; color: #64748b; display: block; }
.gauge-stat .stat-value { font-size: 24px; font-weight: 700; color: #1e293b; }
.gauge-stat .stat-value.danger { color: #f56c6c; }
.trend-chart { width: 100%; height: 280px; }

.filter-bar { display: flex; justify-content: space-between; align-items: center; background: white; padding: 16px 20px; border-radius: 12px; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.filter-left { display: flex; gap: 12px; flex-wrap: wrap; }
.filter-right { display: flex; gap: 16px; align-items: center; }

.device-table-container { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.device-cell { display: flex; align-items: center; gap: 12px; }
.device-info { display: flex; flex-direction: column; }
.device-name { font-weight: 600; color: #1e293b; }
.device-model { font-size: 11px; color: #64748b; }
.health-cell { display: flex; align-items: center; }
.status-cell { display: flex; align-items: center; gap: 8px; }
.status-indicator { width: 8px; height: 8px; border-radius: 50%; }
.status-indicator.online { background: #10b981; }
.status-indicator.warning { background: #f59e0b; animation: pulse 2s infinite; }
.status-indicator.error { background: #ef4444; animation: pulse 1s infinite; }
.status-indicator.offline { background: #6b7280; }
.text-success { color: #67c23a; font-weight: 600; }
.text-primary { color: #409eff; font-weight: 600; }
.text-warning { color: #e6a23c; font-weight: 600; }
.text-danger { color: #f56c6c; font-weight: 600; }
.pagination-wrapper { display: flex; justify-content: flex-end; padding: 16px 20px; border-top: 1px solid #e4e7ed; }

.recommendations-panel { margin-top: 20px; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.recommendations-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; }
.recommendations-header h3 { display: flex; align-items: center; gap: 8px; margin: 0; font-size: 16px; }
.recommendations-list { max-height: 300px; overflow-y: auto; }
.recommendation-item { display: flex; align-items: flex-start; gap: 16px; padding: 16px 20px; border-bottom: 1px solid #e2e8f0; transition: background 0.2s; }
.recommendation-item:hover { background: #f8fafc; }
.recommendation-item.high { border-left: 3px solid #f56c6c; }
.recommendation-item.medium { border-left: 3px solid #e6a23c; }
.recommendation-item.low { border-left: 3px solid #409eff; }
.rec-icon .el-icon { font-size: 20px; }
.recommendation-item.high .rec-icon .el-icon { color: #f56c6c; }
.recommendation-item.medium .rec-icon .el-icon { color: #e6a23c; }
.recommendation-item.low .rec-icon .el-icon { color: #409eff; }
.rec-content { flex: 1; }
.rec-title { font-weight: 600; color: #1e293b; margin-bottom: 4px; }
.rec-description { font-size: 13px; color: #64748b; margin-bottom: 4px; }
.rec-device { font-size: 11px; color: #94a3b8; }
.rec-actions { display: flex; gap: 8px; }

.device-detail { padding: 8px; }
.detail-header { display: flex; gap: 20px; margin-bottom: 20px; align-items: center; }
.detail-title h2 { margin: 0 0 4px 0; font-size: 18px; }
.detail-title p { margin: 0; color: #64748b; font-size: 13px; }
.health-gauge { height: 180px; }
.health-metrics { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.metric-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e2e8f0; }
.metric-label { font-size: 13px; color: #64748b; }
.metric-value { font-weight: 600; color: #1e293b; }
.health-factors { margin-top: 16px; }
.health-factors h4 { margin: 0 0 16px 0; font-size: 14px; }
.factor-item { margin-bottom: 16px; }
.factor-name { display: block; font-size: 13px; color: #64748b; margin-bottom: 6px; }
.detail-actions { display: flex; gap: 12px; margin-top: 20px; padding-top: 16px; border-top: 1px solid #e2e8f0; }

@media (max-width: 1024px) { .stats-cards { grid-template-columns: repeat(2, 1fr); } .dashboard-row { grid-template-columns: 1fr; } }
@media (max-width: 768px) { .stats-cards { grid-template-columns: 1fr; } .filter-bar { flex-direction: column; } .filter-left { width: 100%; } .filter-left .el-input, .filter-left .el-select { flex: 1; } .recommendation-item { flex-direction: column; } .rec-actions { align-self: flex-end; } }
</style>