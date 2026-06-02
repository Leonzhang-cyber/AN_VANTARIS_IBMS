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
        <div class="loading-tip">Online/Offline Monitoring</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- ==================== Main Content ==================== -->
  <div v-else class="online-offline-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/systems-devices/device-inventory' }">
            Systems & Devices
          </el-breadcrumb-item>
          <el-breadcrumb-item>Device Monitoring</el-breadcrumb-item>
          <el-breadcrumb-item>Online/Offline Status</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <div class="connection-status">
          <span class="status-dot" :class="{ online: wsConnected, offline: !wsConnected }"></span>
          <span>{{ wsConnected ? 'Real-time Connected' : 'Reconnecting...' }}</span>
        </div>
        <el-button :icon="Refresh" @click="refreshData" :loading="refreshing">Refresh</el-button>
        <el-button type="primary" :icon="BellFilled" @click="openAlertSettings">Alert Settings</el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card online" @click="filterStatus = 'online'">
        <div class="stat-icon"><el-icon><CircleCheckFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.online }}</span>
          <span class="stat-label">Online</span>
        </div>
        <div class="stat-percent">{{ stats.onlinePercent }}%</div>
      </div>
      <div class="stat-card offline" @click="filterStatus = 'offline'">
        <div class="stat-icon"><el-icon><RemoveFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.offline }}</span>
          <span class="stat-label">Offline</span>
        </div>
        <div class="stat-percent">{{ stats.offlinePercent }}%</div>
      </div>
      <div class="stat-card warning" @click="filterStatus = 'warning'">
        <div class="stat-icon"><el-icon><WarningFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.warning }}</span>
          <span class="stat-label">Warning</span>
        </div>
        <div class="stat-percent">{{ stats.warningPercent }}%</div>
      </div>
      <div class="stat-card error" @click="filterStatus = 'error'">
        <div class="stat-icon"><el-icon><CircleCloseFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.error }}</span>
          <span class="stat-label">Error</span>
        </div>
        <div class="stat-percent">{{ stats.errorPercent }}%</div>
      </div>
    </div>

    <!-- 在线率趋势图 -->
    <div class="chart-card">
      <div class="chart-header">
        <h3><el-icon><TrendCharts /></el-icon> Uptime Trend (Last 30 Days)</h3>
        <div class="chart-legend">
          <span><span class="legend-dot online"></span> Online Rate</span>
          <span><span class="legend-dot offline"></span> Offline Rate</span>
        </div>
      </div>
      <div ref="uptimeChartRef" class="uptime-chart"></div>
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
            @clear="loadDevices"
            @keyup.enter="loadDevices"
        />
        <el-select v-model="filterSystem" placeholder="System Type" clearable style="width: 140px" @change="loadDevices">
          <el-option label="All Systems" value="" />
          <el-option label="HVAC" value="hvac" />
          <el-option label="Lighting" value="lighting" />
          <el-option label="Security" value="sas" />
          <el-option label="Fire Alarm" value="fas" />
          <el-option label="Plumbing" value="plumbing" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="Status" clearable style="width: 120px" @change="loadDevices">
          <el-option label="All Status" value="" />
          <el-option label="Online" value="online" />
          <el-option label="Warning" value="warning" />
          <el-option label="Error" value="error" />
          <el-option label="Offline" value="offline" />
        </el-select>
        <el-select v-model="filterArea" placeholder="Area" clearable style="width: 140px" @change="loadDevices">
          <el-option label="All Areas" value="" />
          <el-option v-for="area in areas" :key="area" :label="area" :value="area" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-switch v-model="showOnlyOffline" active-text="Show Offline Only" @change="loadDevices" />
        <el-tooltip content="Auto-refresh every 10 seconds">
          <el-switch v-model="autoRefresh" active-text="Auto" />
        </el-tooltip>
      </div>
    </div>

    <!-- 设备状态表格 -->
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
        <el-table-column label="Status" width="120">
          <template #default="{ row }">
            <div class="status-cell">
              <div class="status-indicator" :class="row.status"></div>
              <span class="status-text" :class="row.status">{{ row.status.toUpperCase() }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Last Heartbeat" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.lastHeartbeat) }}
            <span v-if="isHeartbeatStale(row.lastHeartbeat)" class="stale-badge">Stale</span>
          </template>
        </el-table-column>
        <el-table-column label="Uptime (30d)" width="180">
          <template #default="{ row }">
            <el-progress :percentage="row.uptime30d" :stroke-width="8" :color="getUptimeColor(row.uptime30d)" :show-text="false" style="width: 100px" />
            <span :class="getUptimeClass(row.uptime30d)">{{ row.uptime30d }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="Last Offline" width="180">
          <template #default="{ row }">
            {{ row.lastOffline ? formatDateTime(row.lastOffline) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="Offline Count" width="110">
          <template #default="{ row }">
            <span :class="{ 'text-warning': row.offlineCount > 5 }">{{ row.offlineCount }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text @click.stop="viewHistory(row)">History</el-button>
            <el-button size="small" text type="primary" @click.stop="diagnose(row)">Diagnose</el-button>
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
            @size-change="loadDevices"
            @current-change="loadDevices"
        />
      </div>
    </div>

    <!-- 离线告警列表 -->
    <div class="alerts-panel" v-if="offlineAlerts.length > 0">
      <div class="alerts-header">
        <h3><el-icon><BellFilled /></el-icon> Offline Alerts ({{ offlineAlerts.length }})</h3>
        <el-button size="small" text @click="clearAlerts">Clear All</el-button>
      </div>
      <div class="alerts-list">
        <div v-for="alert in offlineAlerts" :key="alert.id" class="alert-item">
          <div class="alert-icon"><el-icon><CircleCloseFilled /></el-icon></div>
          <div class="alert-content">
            <div class="alert-title">{{ alert.deviceName }}</div>
            <div class="alert-message">Device went offline at {{ formatDateTime(alert.timestamp) }}</div>
            <div class="alert-duration">Duration: {{ alert.duration }}</div>
          </div>
          <div class="alert-actions">
            <el-button size="small" @click="acknowledgeAlert(alert)">Acknowledge</el-button>
            <el-button size="small" type="primary" @click="investigateAlert(alert)">Investigate</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 设备详情对话框 -->
    <el-dialog v-model="detailDialogVisible" :title="selectedDevice?.name || 'Device Details'" width="600px">
      <div v-if="selectedDevice" class="device-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Device Name">{{ selectedDevice.name }}</el-descriptions-item>
          <el-descriptions-item label="Model">{{ selectedDevice.model }}</el-descriptions-item>
          <el-descriptions-item label="Serial Number">{{ selectedDevice.serialNumber }}</el-descriptions-item>
          <el-descriptions-item label="System Type">{{ getSystemLabel(selectedDevice.systemType) }}</el-descriptions-item>
          <el-descriptions-item label="Area">{{ selectedDevice.area }}</el-descriptions-item>
          <el-descriptions-item label="IP Address">{{ selectedDevice.ipAddress || '-' }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <div class="status-cell"><div class="status-indicator" :class="selectedDevice.status"></div>{{ selectedDevice.status.toUpperCase() }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="Last Heartbeat">{{ formatDateTime(selectedDevice.lastHeartbeat) }}</el-descriptions-item>
          <el-descriptions-item label="Uptime (30d)"><el-progress :percentage="selectedDevice.uptime30d" :stroke-width="10" :color="getUptimeColor(selectedDevice.uptime30d)" :format="() => `${selectedDevice.uptime30d}%`" /></el-descriptions-item>
          <el-descriptions-item label="Offline Count">{{ selectedDevice.offlineCount }} times</el-descriptions-item>
          <el-descriptions-item label="Last Offline">{{ selectedDevice.lastOffline ? formatDateTime(selectedDevice.lastOffline) : '-' }}</el-descriptions-item>
          <el-descriptions-item label="Avg Response Time">{{ selectedDevice.avgResponseTime || '-' }} ms</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- 历史记录对话框 -->
    <el-dialog v-model="historyDialogVisible" :title="`Connection History - ${historyDevice?.name}`" width="700px">
      <div ref="historyChartRef" class="history-chart"></div>
      <el-table :data="historyRecords" stripe size="small" max-height="300" style="margin-top: 20px">
        <el-table-column prop="timestamp" label="Time" width="180"><template #default="{ row }">{{ formatDateTime(row.timestamp) }}</template></el-table-column>
        <el-table-column prop="status" label="Status" width="100"><template #default="{ row }"><el-tag :type="row.status === 'online' ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag></template></el-table-column>
        <el-table-column prop="duration" label="Duration" width="120" />
        <el-table-column prop="reason" label="Reason" min-width="200" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { Refresh, BellFilled, Search, TrendCharts, CircleCheckFilled, RemoveFilled, WarningFilled, CircleCloseFilled, Cpu } from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Connecting to monitoring system...')
const refreshing = ref(false)
const tableLoading = ref(false)
const loadingMessages = ['Initializing...', 'Connecting to devices...', 'Fetching status data...', 'Rendering charts...', 'Almost ready...']

// ==================== State ====================
const searchKeyword = ref('')
const filterSystem = ref('')
const filterStatus = ref('')
const filterArea = ref('')
const showOnlyOffline = ref(false)
const autoRefresh = ref(true)
const wsConnected = ref(true)
const currentPage = ref(1)
const pageSize = ref(20)
const totalRecords = ref(0)
const detailDialogVisible = ref(false)
const historyDialogVisible = ref(false)
const selectedDevice = ref<any>(null)
const historyDevice = ref<any>(null)
let uptimeChart: echarts.ECharts | null = null
let historyChart: echarts.ECharts | null = null
const uptimeChartRef = ref<HTMLElement>()
const historyChartRef = ref<HTMLElement>()
let refreshTimer: number

// ==================== Data ====================
interface DeviceStatus {
  id: string
  name: string
  model: string
  manufacturer: string
  serialNumber: string
  systemType: string
  area: string
  floor: string
  status: 'online' | 'offline' | 'warning' | 'error'
  imageUrl: string
  lastHeartbeat: string
  uptime30d: number
  offlineCount: number
  lastOffline: string | null
  ipAddress?: string
  avgResponseTime?: number
}

interface OfflineAlert {
  id: string
  deviceId: string
  deviceName: string
  timestamp: string
  duration: string
}

interface HistoryRecord {
  timestamp: string
  status: 'online' | 'offline'
  duration: string
  reason: string
}

const devices = ref<DeviceStatus[]>([])
const offlineAlerts = ref<OfflineAlert[]>([])
const historyRecords = ref<HistoryRecord[]>([])

// 生成模拟设备数据
const generateDevices = (): DeviceStatus[] => {
  const now = new Date()
  const baseDevices = [
    { id: '1', name: 'AHU-B2-01 Air Handler', model: 'Carrier 39G', manufacturer: 'Carrier', serial: 'CA-2024-B201', system: 'hvac', area: 'Basement B2', floor: 'B2', img: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567.webp', ip: '192.168.1.101' },
    { id: '2', name: 'FCU-B2-01 Fan Coil', model: 'Daikin FXMQ', manufacturer: 'Daikin', serial: 'DK-2024-B201', system: 'hvac', area: 'Basement B2', floor: 'B2', img: 'https://aegisnx.com/wp-content/uploads/2026/05/52013141234431.webp', ip: '192.168.1.102' },
    { id: '3', name: 'CH-B2-01 Chiller', model: 'Carrier AquaEdge', manufacturer: 'Carrier', serial: 'CA-2024-B202', system: 'hvac', area: 'Basement B2', floor: 'B2', img: 'https://aegisnx.com/wp-content/uploads/2026/05/52013145678.jpg', ip: '192.168.1.103' },
    { id: '4', name: 'EF-B2-02 Exhaust Fan', model: 'Greenheck CUBE', manufacturer: 'Greenheck', serial: 'GH-2024-B202', system: 'hvac', area: 'Basement B2', floor: 'B2', img: 'https://aegisnx.com/wp-content/uploads/2026/05/520131452044.webp', ip: '192.168.1.104' },
    { id: '5', name: 'LIGHT-B2-01 Controller', model: 'Philips Dynalite', manufacturer: 'Philips', serial: 'PH-2024-B201', system: 'lighting', area: 'Basement B2', floor: 'B2', img: 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp', ip: '192.168.1.105' },
    { id: '6', name: 'ACS-1F-01 Entrance', model: 'HID VertX', manufacturer: 'HID', serial: 'HD-2024-1F01', system: 'sas', area: 'Lobby 1F', floor: '1F', img: 'https://aegisnx.com/wp-content/uploads/2026/05/52013147643.jpg', ip: '192.168.1.106' },
    { id: '7', name: 'SD-1F-01 Smoke Detector', model: 'Honeywell XLS', manufacturer: 'Honeywell', serial: 'HW-2024-1F01', system: 'fas', area: 'Lobby 1F', floor: '1F', img: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567123.jpg', ip: '192.168.1.107' },
    { id: '8', name: 'PUMP-B2-02 Booster', model: 'Grundfos CR', manufacturer: 'Grundfos', serial: 'GF-2024-B202', system: 'plumbing', area: 'Basement B2', floor: 'B2', img: 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png', ip: '192.168.1.108' },
    { id: '9', name: 'AHU-2F-01 Air Handler', model: 'Trane IntelliPak', manufacturer: 'Trane', serial: 'TR-2024-2F01', system: 'hvac', area: 'Office 2F', floor: '2F', img: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567.webp', ip: '192.168.1.109' }
  ]

  return baseDevices.map(device => {
    const statusRand = Math.random()
    let status: 'online' | 'offline' | 'warning' | 'error'
    if (device.id === '3') status = 'warning'
    else if (device.id === '4') status = 'error'
    else if (device.id === '9') status = 'error'
    else status = statusRand > 0.85 ? 'offline' : 'online'

    const uptime = status === 'online' ? 95 + Math.random() * 5 : 60 + Math.random() * 30
    const lastHeartbeat = new Date(now.getTime() - (status === 'online' ? Math.random() * 60000 : Math.random() * 3600000))

    return {
      id: device.id,
      name: device.name,
      model: device.model,
      manufacturer: device.manufacturer,
      serialNumber: device.serial,
      systemType: device.system,
      area: device.area,
      floor: device.floor,
      status,
      imageUrl: device.img,
      lastHeartbeat: lastHeartbeat.toISOString(),
      uptime30d: Math.round(uptime * 10) / 10,
      offlineCount: status === 'offline' ? Math.floor(Math.random() * 10) + 1 : Math.floor(Math.random() * 3),
      lastOffline: status === 'offline' ? new Date(now.getTime() - Math.random() * 86400000).toISOString() : null,
      ipAddress: device.ip,
      avgResponseTime: status === 'online' ? Math.floor(Math.random() * 100) + 20 : null
    }
  })
}

// 生成离线告警
const generateOfflineAlerts = (devicesList: DeviceStatus[]): OfflineAlert[] => {
  const offlineDevices = devicesList.filter(d => d.status === 'offline' || d.status === 'error')
  return offlineDevices.map(device => ({
    id: `alert-${device.id}`,
    deviceId: device.id,
    deviceName: device.name,
    timestamp: new Date(Date.now() - Math.random() * 3600000).toISOString(),
    duration: `${Math.floor(Math.random() * 60) + 1} minutes`
  }))
}

// 生成历史记录
const generateHistoryRecords = (deviceId: string): HistoryRecord[] => {
  const records: HistoryRecord[] = []
  const now = new Date()
  for (let i = 30; i >= 0; i--) {
    const date = new Date(now.getTime() - i * 86400000)
    const isOffline = Math.random() < 0.1
    records.push({
      timestamp: date.toISOString(),
      status: isOffline ? 'offline' : 'online',
      duration: isOffline ? `${Math.floor(Math.random() * 120) + 5} min` : '-',
      reason: isOffline ? 'Network timeout / Power issue' : 'Normal operation'
    })
  }
  return records
}

// 生成在线率趋势数据
const generateUptimeTrendData = () => {
  const days = []
  const onlineRates = []
  const offlineRates = []
  const now = new Date()
  for (let i = 29; i >= 0; i--) {
    const date = new Date(now.getTime() - i * 86400000)
    days.push(`${date.getMonth() + 1}/${date.getDate()}`)
    const onlineRate = 85 + Math.random() * 14
    onlineRates.push(Math.round(onlineRate * 10) / 10)
    offlineRates.push(Math.round((100 - onlineRate) * 10) / 10)
  }
  return { days, onlineRates, offlineRates }
}

// 统计
const stats = computed(() => {
  const total = devices.value.length
  const online = devices.value.filter(d => d.status === 'online').length
  const offline = devices.value.filter(d => d.status === 'offline').length
  const warning = devices.value.filter(d => d.status === 'warning').length
  const error = devices.value.filter(d => d.status === 'error').length
  return { total, online, offline, warning, error, onlinePercent: total ? Math.round(online / total * 100) : 0, offlinePercent: total ? Math.round(offline / total * 100) : 0, warningPercent: total ? Math.round(warning / total * 100) : 0, errorPercent: total ? Math.round(error / total * 100) : 0 }
})

const areas = computed(() => {
  const areaSet = new Set<string>()
  devices.value.forEach(d => areaSet.add(d.area))
  return Array.from(areaSet).sort()
})

const filteredDevices = computed(() => {
  let result = [...devices.value]
  if (searchKeyword.value) { const kw = searchKeyword.value.toLowerCase(); result = result.filter(d => d.name.toLowerCase().includes(kw) || d.id.includes(kw)) }
  if (filterSystem.value) result = result.filter(d => d.systemType === filterSystem.value)
  if (filterStatus.value) result = result.filter(d => d.status === filterStatus.value)
  if (filterArea.value) result = result.filter(d => d.area === filterArea.value)
  if (showOnlyOffline.value) result = result.filter(d => d.status === 'offline' || d.status === 'error')
  totalRecords.value = result.length
  const start = (currentPage.value - 1) * pageSize.value
  return result.slice(start, start + pageSize.value)
})

// Helper 函数
const getSystemLabel = (type: string) => ({ hvac: 'HVAC', lighting: 'Lighting', sas: 'Security', fas: 'Fire Alarm', plumbing: 'Plumbing' }[type] || type)
const getSystemTagType = (type: string) => ({ hvac: 'primary', lighting: 'success', sas: 'danger', fas: 'warning', plumbing: 'info' }[type] || 'info')
const getUptimeColor = (uptime: number) => uptime >= 95 ? '#67c23a' : uptime >= 80 ? '#e6a23c' : '#f56c6c'
const getUptimeClass = (uptime: number) => uptime >= 95 ? 'text-success' : uptime >= 80 ? 'text-warning' : 'text-danger'
const isHeartbeatStale = (heartbeat: string) => new Date(heartbeat).getTime() < Date.now() - 300000
const formatDateTime = (dateStr: string) => new Date(dateStr).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' })

// 图表初始化
const initUptimeChart = () => {
  if (!uptimeChartRef.value) return
  if (uptimeChart) uptimeChart.dispose()
  uptimeChart = echarts.init(uptimeChartRef.value)
  const { days, onlineRates, offlineRates } = generateUptimeTrendData()
  uptimeChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['Online Rate (%)', 'Offline Rate (%)'], top: 0, right: 0 },
    grid: { top: 40, right: 20, bottom: 30, left: 50, containLabel: true },
    xAxis: { type: 'category', data: days, axisLabel: { rotate: 45, interval: 5 } },
    yAxis: { type: 'value', name: 'Percentage (%)', min: 0, max: 100 },
    series: [
      { name: 'Online Rate (%)', type: 'line', data: onlineRates, smooth: true, lineStyle: { color: '#67c23a', width: 2 }, areaStyle: { opacity: 0.1, color: '#67c23a' }, symbol: 'circle', symbolSize: 6 },
      { name: 'Offline Rate (%)', type: 'line', data: offlineRates, smooth: true, lineStyle: { color: '#f56c6c', width: 2 }, areaStyle: { opacity: 0.1, color: '#f56c6c' }, symbol: 'diamond', symbolSize: 6 }
    ]
  })
}

const initHistoryChart = () => {
  if (!historyChartRef.value) return
  if (historyChart) historyChart.dispose()
  historyChart = echarts.init(historyChartRef.value)
  const records = historyRecords.value
  const dates = records.map(r => new Date(r.timestamp).toLocaleDateString())
  const statusValues = records.map(r => r.status === 'online' ? 1 : 0)
  historyChart.setOption({
    tooltip: { trigger: 'axis', formatter: (params: any) => `${params[0].axisValue}<br/>Status: ${params[0].value === 1 ? 'Online' : 'Offline'}` },
    grid: { top: 30, right: 20, bottom: 30, left: 50, containLabel: true },
    xAxis: { type: 'category', data: dates, axisLabel: { rotate: 45, interval: 5 } },
    yAxis: { type: 'value', name: 'Status', min: -0.5, max: 1.5, axisLabel: { formatter: (val: number) => val === 1 ? 'Online' : 'Offline' } },
    series: [{ type: 'line', data: statusValues, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.1 }, symbol: 'circle', symbolSize: 8, step: 'end' }]
  })
}

// 数据加载
const loadDevices = async () => {
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 300))
  devices.value = generateDevices()
  offlineAlerts.value = generateOfflineAlerts(devices.value)
  tableLoading.value = false
}

const refreshData = async () => {
  refreshing.value = true
  await loadDevices()
  initUptimeChart()
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

// Actions
const showDeviceDetail = (device: DeviceStatus) => { selectedDevice.value = device; detailDialogVisible.value = true }
const viewHistory = async (device: DeviceStatus) => { historyDevice.value = device; historyRecords.value = generateHistoryRecords(device.id); historyDialogVisible.value = true; await nextTick(); initHistoryChart() }
const diagnose = (device: DeviceStatus) => ElMessage.info(`Running diagnostics for ${device.name}...`)
const acknowledgeAlert = (alert: OfflineAlert) => { offlineAlerts.value = offlineAlerts.value.filter(a => a.id !== alert.id); ElMessage.success(`Alert acknowledged: ${alert.deviceName}`) }
const investigateAlert = (alert: OfflineAlert) => ElMessage.info(`Investigating offline issue for ${alert.deviceName}`)
const clearAlerts = () => { offlineAlerts.value = []; ElMessage.success('All alerts cleared') }
const openAlertSettings = () => ElMessage.info('Opening alert settings')

// 自动刷新
const startAutoRefresh = () => { refreshTimer = window.setInterval(() => { if (autoRefresh.value) refreshData() }, 10000) }

// 窗口适配
const handleResize = () => { if (uptimeChart) uptimeChart.resize(); if (historyChart) historyChart.resize() }

// Lifecycle
onMounted(() => {
  let msgIdx = 0
  const msgInt = setInterval(() => { if (msgIdx < loadingMessages.length - 1) { msgIdx++; loadingMessage.value = loadingMessages[msgIdx] } }, 400)
  const progInt = setInterval(() => { if (loadingProgress.value < 100) { loadingProgress.value += Math.random() * 15 + 5; if (loadingProgress.value > 100) loadingProgress.value = 100 } }, 200)
  setTimeout(() => {
    clearInterval(msgInt); clearInterval(progInt); loadingProgress.value = 100; loadingMessage.value = 'Ready!'
    setTimeout(() => { isLoaded.value = true; loadDevices(); initUptimeChart(); startAutoRefresh(); window.addEventListener('resize', handleResize) }, 400)
  }, 2000)
})

onUnmounted(() => { clearInterval(refreshTimer); window.removeEventListener('resize', handleResize); if (uptimeChart) uptimeChart.dispose(); if (historyChart) historyChart.dispose() })
watch(autoRefresh, (val) => { if (val && !refreshTimer) startAutoRefresh() })
</script>

<style scoped>
.loading-container { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); z-index: 9999; display: flex; justify-content: center; align-items: center; }
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

.online-offline-page { padding: 20px; background: #f5f7fa; min-height: 100%; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }
.header-right { display: flex; align-items: center; gap: 16px; }
.connection-status { display: flex; align-items: center; gap: 8px; font-size: 13px; padding: 6px 12px; background: white; border-radius: 20px; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; }
.status-dot.online { background: #10b981; box-shadow: 0 0 6px #10b981; }
.status-dot.offline { background: #ef4444; animation: pulse 1s infinite; }

.stats-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 24px; }
.stat-card { background: white; border-radius: 16px; padding: 20px; display: flex; align-items: center; justify-content: space-between; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
.stat-card.online .stat-icon .el-icon { color: #10b981; }
.stat-card.offline .stat-icon .el-icon { color: #6b7280; }
.stat-card.warning .stat-icon .el-icon { color: #f59e0b; }
.stat-card.error .stat-icon .el-icon { color: #ef4444; }
.stat-icon .el-icon { font-size: 32px; }
.stat-info { text-align: center; }
.stat-value { font-size: 28px; font-weight: 700; color: #1e293b; }
.stat-label { font-size: 13px; color: #64748b; }
.stat-percent { font-size: 20px; font-weight: 600; color: #3b82f6; }

.chart-card { background: white; border-radius: 16px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px; }
.chart-header h3 { display: flex; align-items: center; gap: 8px; margin: 0; font-size: 16px; }
.chart-legend { display: flex; gap: 16px; }
.legend-dot { width: 10px; height: 10px; display: inline-block; border-radius: 50%; margin-right: 6px; }
.legend-dot.online { background: #67c23a; }
.legend-dot.offline { background: #f56c6c; }
.uptime-chart { width: 100%; height: 350px; }

.filter-bar { display: flex; justify-content: space-between; align-items: center; background: white; padding: 16px 20px; border-radius: 12px; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.filter-left { display: flex; gap: 12px; flex-wrap: wrap; }
.filter-right { display: flex; gap: 16px; align-items: center; }

.device-table-container { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.device-cell { display: flex; align-items: center; gap: 12px; }
.device-info { display: flex; flex-direction: column; }
.device-name { font-weight: 600; color: #1e293b; }
.device-model { font-size: 11px; color: #64748b; }
.status-cell { display: flex; align-items: center; gap: 8px; }
.status-indicator { width: 10px; height: 10px; border-radius: 50%; }
.status-indicator.online { background: #10b981; box-shadow: 0 0 6px #10b981; }
.status-indicator.warning { background: #f59e0b; box-shadow: 0 0 6px #f59e0b; animation: pulse 2s infinite; }
.status-indicator.error { background: #ef4444; box-shadow: 0 0 6px #ef4444; animation: pulse 1s infinite; }
.status-indicator.offline { background: #6b7280; }
.status-text.online { color: #10b981; font-weight: 600; }
.status-text.warning { color: #f59e0b; font-weight: 600; }
.status-text.error { color: #ef4444; font-weight: 600; }
.stale-badge { background: #fef0f0; color: #f56c6c; font-size: 10px; padding: 2px 6px; border-radius: 10px; margin-left: 8px; }
.text-success { color: #67c23a; font-weight: 500; }
.text-warning { color: #f59e0b; font-weight: 500; }
.text-danger { color: #f56c6c; font-weight: 500; }
.pagination-wrapper { display: flex; justify-content: flex-end; padding: 16px 20px; border-top: 1px solid #e4e7ed; }

.alerts-panel { position: fixed; bottom: 20px; right: 20px; width: 400px; background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); z-index: 100; overflow: hidden; }
.alerts-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; }
.alerts-header h3 { display: flex; align-items: center; gap: 8px; margin: 0; font-size: 14px; }
.alerts-list { max-height: 300px; overflow-y: auto; }
.alert-item { display: flex; align-items: flex-start; gap: 12px; padding: 12px 16px; border-bottom: 1px solid #e2e8f0; }
.alert-item:hover { background: #f8fafc; }
.alert-icon .el-icon { font-size: 18px; color: #ef4444; }
.alert-content { flex: 1; }
.alert-title { font-size: 13px; font-weight: 600; color: #1e293b; }
.alert-message { font-size: 12px; color: #64748b; margin-top: 2px; }
.alert-duration { font-size: 11px; color: #94a3b8; margin-top: 4px; }
.alert-actions { display: flex; gap: 8px; }

.device-detail { padding: 8px; }
.history-chart { width: 100%; height: 200px; }

@media (max-width: 1024px) { .stats-cards { grid-template-columns: repeat(2, 1fr); } .alerts-panel { width: 320px; } }
@media (max-width: 768px) { .stats-cards { grid-template-columns: 1fr; } .filter-bar { flex-direction: column; } .filter-left { width: 100%; } .filter-left .el-input, .filter-left .el-select { flex: 1; } .alerts-panel { left: 20px; right: 20px; width: auto; } .uptime-chart { height: 250px; } }
</style>