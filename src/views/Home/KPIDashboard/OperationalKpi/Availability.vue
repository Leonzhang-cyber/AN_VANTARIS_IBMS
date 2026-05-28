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
        <div class="loading-tip">Not Developed Yet</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Availability Page Content -->
  <div v-else class="availability-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>Availability</h1>
        <p class="subtitle">Monitor system and device availability metrics across your facilities</p>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="refreshData">Refresh</el-button>
        <el-button :icon="Download" @click="exportReport">Export</el-button>
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            :shortcuts="dateShortcuts"
            size="default"
            style="width: 260px"
            @change="handleDateChange"
        />
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="kpi-cards">
      <div class="kpi-card overall">
        <div class="kpi-icon">
          <el-icon :size="32"><Monitor /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ overallAvailability }}%</div>
          <div class="kpi-label">Overall Availability</div>
        </div>
        <div class="kpi-trend" :class="overallTrend >= 0 ? 'positive' : 'negative'">
          <el-icon><CaretTop v-if="overallTrend >= 0" /><CaretBottom v-else /></el-icon>
          {{ Math.abs(overallTrend) }}%
        </div>
      </div>
      <div class="kpi-card systems">
        <div class="kpi-icon">
          <el-icon :size="32"><Cpu /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ systemAvailability }}%</div>
          <div class="kpi-label">System Availability</div>
        </div>
        <div class="kpi-trend" :class="systemTrend >= 0 ? 'positive' : 'negative'">
          <el-icon><CaretTop v-if="systemTrend >= 0" /><CaretBottom v-else /></el-icon>
          {{ Math.abs(systemTrend) }}%
        </div>
      </div>
      <div class="kpi-card devices">
        <div class="kpi-icon">
          <el-icon :size="32"><Connection /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ deviceAvailability }}%</div>
          <div class="kpi-label">Device Availability</div>
        </div>
        <div class="kpi-trend" :class="deviceTrend >= 0 ? 'positive' : 'negative'">
          <el-icon><CaretTop v-if="deviceTrend >= 0" /><CaretBottom v-else /></el-icon>
          {{ Math.abs(deviceTrend) }}%
        </div>
      </div>
      <div class="kpi-card uptime">
        <div class="kpi-icon">
          <el-icon :size="32"><Timer /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ avgUptime }}</div>
          <div class="kpi-label">Avg. Uptime (MTBF)</div>
        </div>
        <div class="kpi-trend uptime-trend">
          {{ uptimeChange }} days
        </div>
      </div>
    </div>

    <!-- Availability Trend Chart -->
    <div class="chart-card">
      <div class="card-header">
        <h3>Availability Trend</h3>
        <el-radio-group v-model="trendPeriod" size="small" @change="fetchTrendData">
          <el-radio-button label="week">Last 7 Days</el-radio-button>
          <el-radio-button label="month">Last 30 Days</el-radio-button>
          <el-radio-button label="quarter">Last 90 Days</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-container" ref="trendChartRef"></div>
    </div>

    <!-- Availability by System Type -->
    <div class="two-columns">
      <div class="chart-card">
        <div class="card-header">
          <h3>Availability by System Type</h3>
        </div>
        <div class="chart-container" ref="systemChartRef"></div>
      </div>
      <div class="chart-card">
        <div class="card-header">
          <h3>Top Performing Systems</h3>
        </div>
        <div class="ranking-list">
          <div v-for="(item, index) in topSystems" :key="item.id" class="ranking-item">
            <div class="ranking-index" :class="getRankingClass(index)">
              {{ index + 1 }}
            </div>
            <div class="ranking-info">
              <div class="ranking-name">{{ item.name }}</div>
              <div class="ranking-location">{{ item.location }}</div>
            </div>
            <div class="ranking-value">
              {{ item.availability }}%
              <el-progress :percentage="item.availability" :stroke-width="4" :show-text="false" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Devices Table -->
    <div class="table-card">
      <div class="card-header">
        <h3>Device Availability Status</h3>
        <el-input
            v-model="searchText"
            placeholder="Search devices..."
            :prefix-icon="Search"
            style="width: 260px"
            clearable
        />
      </div>
      <el-table :data="filteredDevices" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="deviceName" label="Device Name" min-width="180" />
        <el-table-column prop="deviceType" label="Type" width="140">
          <template #default="{ row }">
            <el-tag size="small">{{ row.deviceType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="Location" width="160" />
        <el-table-column prop="availability" label="Availability" width="140">
          <template #default="{ row }">
            <div class="availability-cell">
              <span :class="getAvailabilityClass(row.availability)">{{ row.availability }}%</span>
              <el-progress
                  :percentage="row.availability"
                  :color="getAvailabilityColor(row.availability)"
                  :stroke-width="6"
                  :show-text="false"
                  style="width: 80px"
              />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="uptime" label="Uptime (Days)" width="120">
          <template #default="{ row }">
            {{ row.uptime }}
          </template>
        </el-table-column>
        <el-table-column prop="downtime" label="Downtime (Hours)" width="130">
          <template #default="{ row }">
            <span :class="{ 'text-danger': row.downtime > 24 }">{{ row.downtime }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="lastIncident" label="Last Incident" width="140">
          <template #default="{ row }">
            {{ row.lastIncident || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.availability)" size="small" effect="dark">
              {{ getStatusLabel(row.availability) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredDevices.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Refresh,
  Download,
  Monitor,
  Cpu,
  Connection,
  Timer,
  CaretTop,
  CaretBottom,
  Search
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing...',
  'Almost ready...'
]

// ==================== Data Structures ====================
interface DeviceAvailability {
  id: number
  deviceName: string
  deviceType: string
  location: string
  availability: number
  uptime: number
  downtime: number
  lastIncident: string | null
}

interface SystemPerformance {
  id: number
  name: string
  location: string
  type: string
  availability: number
}

// ==================== State ====================
const dateRange = ref<[Date, Date] | null>(null)
const trendPeriod = ref<'week' | 'month' | 'quarter'>('month')
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const trendChartRef = ref<HTMLElement | null>(null)
const systemChartRef = ref<HTMLElement | null>(null)
let trendChart: echarts.ECharts | null = null
let systemChart: echarts.ECharts | null = null

// ==================== Mock Data ====================
const devices = ref<DeviceAvailability[]>([
  { id: 1, deviceName: 'AHU-101 (Building A)', deviceType: 'AHU', location: 'Building A, Floor 1', availability: 99.95, uptime: 365, downtime: 4.38, lastIncident: '2024-12-15' },
  { id: 2, deviceName: 'AHU-102 (Building A)', deviceType: 'AHU', location: 'Building A, Floor 2', availability: 99.87, uptime: 358, downtime: 11.4, lastIncident: '2025-01-08' },
  { id: 3, deviceName: 'Chiller-1', deviceType: 'Chiller', location: 'Building A, Basement', availability: 99.92, uptime: 362, downtime: 7.0, lastIncident: '2024-12-28' },
  { id: 4, deviceName: 'Chiller-2', deviceType: 'Chiller', location: 'Building A, Basement', availability: 98.45, uptime: 340, downtime: 13.6, lastIncident: '2025-01-20' },
  { id: 5, deviceName: 'FCU-201', deviceType: 'FCU', location: 'Building B, Floor 2', availability: 97.80, uptime: 325, downtime: 19.3, lastIncident: '2025-01-25' },
  { id: 6, deviceName: 'FCU-202', deviceType: 'FCU', location: 'Building B, Floor 2', availability: 98.20, uptime: 335, downtime: 15.8, lastIncident: '2025-01-18' },
  { id: 7, deviceName: 'VAV-301', deviceType: 'VAV', location: 'Building B, Floor 3', availability: 96.50, uptime: 312, downtime: 30.7, lastIncident: '2025-01-30' },
  { id: 8, deviceName: 'UPS-DataCenter', deviceType: 'UPS', location: 'Data Center', availability: 99.98, uptime: 370, downtime: 1.75, lastIncident: '2024-11-20' },
  { id: 9, deviceName: 'PDU-01', deviceType: 'PDU', location: 'Data Center', availability: 99.95, uptime: 365, downtime: 4.38, lastIncident: '2024-12-10' },
  { id: 10, deviceName: 'CRAC-01', deviceType: 'CRAC', location: 'Data Center', availability: 99.30, uptime: 348, downtime: 15.3, lastIncident: '2025-01-12' },
  { id: 11, deviceName: 'CRAC-02', deviceType: 'CRAC', location: 'Data Center', availability: 98.90, uptime: 342, downtime: 24.1, lastIncident: '2025-01-22' },
  { id: 12, deviceName: 'Lighting Panel LP-01', deviceType: 'Lighting', location: 'Building A, Floor 1', availability: 99.85, uptime: 356, downtime: 13.1, lastIncident: '2024-12-05' },
  { id: 13, deviceName: 'Access Control AC-01', deviceType: 'Access Control', location: 'Main Entrance', availability: 99.92, uptime: 362, downtime: 7.0, lastIncident: '2024-11-28' },
  { id: 14, deviceName: 'Camera NVR-01', deviceType: 'CCTV', location: 'Security Room', availability: 99.75, uptime: 350, downtime: 21.9, lastIncident: '2025-01-15' },
  { id: 15, deviceName: 'BMS Controller', deviceType: 'Controller', location: 'Building A, BMS Room', availability: 99.98, uptime: 370, downtime: 1.75, lastIncident: '2024-10-30' }
])

const systemPerformance = ref<SystemPerformance[]>([
  { id: 1, name: 'Chiller Plant', location: 'Building A', type: 'HVAC', availability: 99.89 },
  { id: 2, name: 'AHU Network', location: 'Building A & B', type: 'HVAC', availability: 99.45 },
  { id: 3, name: 'FCU Network', location: 'Building B', type: 'HVAC', availability: 98.20 },
  { id: 4, name: 'Power Distribution', location: 'All Buildings', type: 'Electrical', availability: 99.95 },
  { id: 5, name: 'UPS Systems', location: 'Data Center', type: 'Electrical', availability: 99.98 },
  { id: 6, name: 'Lighting Control', location: 'All Buildings', type: 'Lighting', availability: 99.85 },
  { id: 7, name: 'Access Control', location: 'All Buildings', type: 'Security', availability: 99.92 },
  { id: 8, name: 'CCTV System', location: 'All Buildings', type: 'Security', availability: 99.75 },
  { id: 9, name: 'Data Center Cooling', location: 'Data Center', type: 'DCIM', availability: 99.10 },
  { id: 10, name: 'Environmental Monitoring', location: 'Data Center', type: 'DCIM', availability: 99.98 }
])

// ==================== Computed Values ====================
const overallAvailability = computed(() => {
  const total = devices.value.reduce((sum, d) => sum + d.availability, 0)
  return (total / devices.value.length).toFixed(2)
})

const systemAvailability = computed(() => {
  const total = systemPerformance.value.reduce((sum, s) => sum + s.availability, 0)
  return (total / systemPerformance.value.length).toFixed(2)
})

const deviceAvailability = computed(() => {
  const total = devices.value.reduce((sum, d) => sum + d.availability, 0)
  return (total / devices.value.length).toFixed(2)
})

const avgUptime = computed(() => {
  const total = devices.value.reduce((sum, d) => sum + d.uptime, 0)
  return (total / devices.value.length).toFixed(0) + ' days'
})

const overallTrend = computed(() => 0.35)
const systemTrend = computed(() => -0.12)
const deviceTrend = computed(() => 0.28)
const uptimeChange = computed(() => '+2.5')

const topSystems = computed(() => {
  return [...systemPerformance.value]
      .sort((a, b) => b.availability - a.availability)
      .slice(0, 5)
})

const filteredDevices = computed(() => {
  let result = [...devices.value]
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(d =>
        d.deviceName.toLowerCase().includes(search) ||
        d.deviceType.toLowerCase().includes(search) ||
        d.location.toLowerCase().includes(search)
    )
  }
  return result
})

const paginatedDevices = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredDevices.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getAvailabilityClass = (availability: number) => {
  if (availability >= 99.9) return 'availability-excellent'
  if (availability >= 99.0) return 'availability-good'
  if (availability >= 98.0) return 'availability-fair'
  return 'availability-poor'
}

const getAvailabilityColor = (availability: number) => {
  if (availability >= 99.9) return '#67c23a'
  if (availability >= 99.0) return '#85ce61'
  if (availability >= 98.0) return '#e6a23c'
  return '#f56c6c'
}

const getStatusLabel = (availability: number) => {
  if (availability >= 99.9) return 'Excellent'
  if (availability >= 99.0) return 'Good'
  if (availability >= 98.0) return 'Fair'
  return 'Poor'
}

const getStatusTagType = (availability: number) => {
  if (availability >= 99.9) return 'success'
  if (availability >= 99.0) return 'primary'
  if (availability >= 98.0) return 'warning'
  return 'danger'
}

const getRankingClass = (index: number) => {
  if (index === 0) return 'gold'
  if (index === 1) return 'silver'
  if (index === 2) return 'bronze'
  return ''
}

const dateShortcuts = [
  { text: 'Last 7 Days', value: () => { const end = new Date(); const start = new Date(); start.setDate(start.getDate() - 7); return [start, end] } },
  { text: 'Last 30 Days', value: () => { const end = new Date(); const start = new Date(); start.setDate(start.getDate() - 30); return [start, end] } },
  { text: 'This Month', value: () => { const end = new Date(); const start = new Date(); start.setDate(1); return [start, end] } }
]

// ==================== Chart Functions ====================
const generateTrendData = () => {
  const days = trendPeriod.value === 'week' ? 7 : trendPeriod.value === 'month' ? 30 : 90
  const dates: string[] = []
  const overall: number[] = []
  const systems: number[] = []
  const devices: number[] = []

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    dates.push(`${date.getMonth() + 1}/${date.getDate()}`)

    const baseOverall = 99.2 + Math.sin(i * 0.3) * 0.3 + Math.random() * 0.2
    const baseSystems = 98.8 + Math.cos(i * 0.25) * 0.4 + Math.random() * 0.2
    const baseDevices = 98.5 + Math.sin(i * 0.35) * 0.5 + Math.random() * 0.2

    overall.push(Number(baseOverall.toFixed(2)))
    systems.push(Number(baseSystems.toFixed(2)))
    devices.push(Number(baseDevices.toFixed(2)))
  }

  return { dates, overall, systems, devices }
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)
  const data = generateTrendData()

  trendChart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: (value: number) => value + '%' },
    legend: { data: ['Overall Availability', 'System Availability', 'Device Availability'], bottom: 0 },
    grid: { left: '3%', right: '4%', top: '10%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: data.dates },
    yAxis: { type: 'value', name: 'Availability (%)', min: 97, max: 100, axisLabel: { formatter: '{value}%' } },
    series: [
      { name: 'Overall Availability', type: 'line', data: data.overall, smooth: true, symbol: 'circle', lineStyle: { width: 3, color: '#409eff' }, areaStyle: { opacity: 0.1, color: '#409eff' } },
      { name: 'System Availability', type: 'line', data: data.systems, smooth: true, symbol: 'diamond', lineStyle: { width: 2, color: '#67c23a' } },
      { name: 'Device Availability', type: 'line', data: data.devices, smooth: true, symbol: 'triangle', lineStyle: { width: 2, color: '#e6a23c' } }
    ]
  })
}

const initSystemChart = () => {
  if (!systemChartRef.value) return
  if (systemChart) systemChart.dispose()

  systemChart = echarts.init(systemChartRef.value)

  const data = systemPerformance.value
      .sort((a, b) => b.availability - a.availability)
      .slice(0, 8)

  systemChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: (value: number) => value + '%' },
    grid: { left: '15%', right: '5%', top: '5%', bottom: '5%', containLabel: true },
    xAxis: { type: 'value', name: 'Availability (%)', min: 97, max: 100, axisLabel: { formatter: '{value}%' } },
    yAxis: { type: 'category', data: data.map(d => d.name), axisLabel: { fontSize: 11 } },
    series: [{
      name: 'Availability', type: 'bar', data: data.map(d => d.availability),
      itemStyle: {
        borderRadius: [0, 4, 4, 0],
        color: (params: any) => {
          const value = params.data
          if (value >= 99.9) return '#67c23a'
          if (value >= 99.0) return '#409eff'
          if (value >= 98.0) return '#e6a23c'
          return '#f56c6c'
        }
      },
      label: { show: true, position: 'right', formatter: '{c}%', fontSize: 11 }
    }]
  })
}

// ==================== Actions ====================
const refreshData = async () => {
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  ElMessage.success('Availability data refreshed')
  initTrendChart()
  initSystemChart()
  tableLoading.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting availability report...')
}

const fetchTrendData = () => {
  initTrendChart()
}

const handleDateChange = () => {
  ElMessage.info(`Date range updated: ${dateRange.value?.[0]?.toLocaleDateString()} - ${dateRange.value?.[1]?.toLocaleDateString()}`)
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Window Resize Handler ====================
const handleResize = () => {
  trendChart?.resize()
  systemChart?.resize()
}

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
      setTimeout(() => {
        initTrendChart()
        initSystemChart()
      }, 100)
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  systemChart?.dispose()
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
.availability-page {
  padding: 24px;
  background: #f5f7fa;
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

.header-title h1 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2f3d;
  margin: 0 0 4px 0;
}

.header-title .subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* KPI Cards */
.kpi-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.kpi-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s, box-shadow 0.2s;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.kpi-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.kpi-card.overall .kpi-icon { background: #e8f4ff; color: #409eff; }
.kpi-card.systems .kpi-icon { background: #e8f8f0; color: #67c23a; }
.kpi-card.devices .kpi-icon { background: #fff7e8; color: #e6a23c; }
.kpi-card.uptime .kpi-icon { background: #f0e8ff; color: #8b5cf6; }

.kpi-info {
  flex: 1;
}

.kpi-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
  line-height: 1.2;
}

.kpi-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.kpi-trend {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 13px;
  font-weight: 500;
}

.kpi-trend.positive { color: #67c23a; }
.kpi-trend.negative { color: #f56c6c; }
.uptime-trend { color: #8b5cf6; }

/* Chart Cards */
.chart-card, .table-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.card-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: #1f2f3d;
}

.chart-container {
  height: 350px;
  width: 100%;
}

.two-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

/* Ranking List */
.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.ranking-item:last-child {
  border-bottom: none;
}

.ranking-index {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  background: #f5f7fa;
  color: #606266;
}

.ranking-index.gold { background: #fff7e8; color: #e6a23c; }
.ranking-index.silver { background: #f0f0f0; color: #909399; }
.ranking-index.bronze { background: #fdf4ea; color: #cd9452; }

.ranking-info {
  flex: 1;
}

.ranking-name {
  font-weight: 500;
  color: #1f2f3d;
  margin-bottom: 2px;
}

.ranking-location {
  font-size: 12px;
  color: #909399;
}

.ranking-value {
  text-align: right;
  font-weight: 600;
  color: #1f2f3d;
  min-width: 120px;
}

.ranking-value .el-progress {
  margin-top: 4px;
}

/* Table Styles */
.availability-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.availability-excellent { color: #67c23a; font-weight: 600; }
.availability-good { color: #409eff; font-weight: 500; }
.availability-fair { color: #e6a23c; }
.availability-poor { color: #f56c6c; }

.text-danger {
  color: #f56c6c;
  font-weight: 500;
}

.pagination-wrapper {
  padding: 20px 0 0;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
  margin-top: 16px;
}

:deep(.el-table) {
  border-radius: 12px;
}

:deep(.el-table th.el-table__cell) {
  background-color: #fafafa;
  font-weight: 600;
  color: #1f2f3d;
}
</style>