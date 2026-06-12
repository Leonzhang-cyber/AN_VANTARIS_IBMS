<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Refresh, Setting, User, Clock,
  Warning, CircleCheck, TrendCharts, DataLine,
  Star, Share, CopyDocument, Delete, Mic,
  Picture, Document, Upload, Download,
  MagicStick, ChatDotRound, Message, Service
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing occupancy sensors...',
  'Analyzing space utilization...',
  'Loading historical data...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedZone = ref('all')
const selectedFloor = ref('all')
const detailsVisible = ref(false)
const chartRef = ref(null)
const heatmapRef = ref(null)

let occupancyChart: echarts.ECharts | null = null
let heatmapChart: echarts.ECharts | null = null

// Zone options
const zoneOptions = [
  { value: 'all', label: 'All Zones' },
  { value: 'office', label: 'Office Areas' },
  { value: 'meeting', label: 'Meeting Rooms' },
  { value: 'common', label: 'Common Areas' },
  { value: 'cafeteria', label: 'Cafeteria' }
]

// Floor options
const floorOptions = [
  { value: 'all', label: 'All Floors' },
  { value: '1', label: '1st Floor' },
  { value: '2', label: '2nd Floor' },
  { value: '3', label: '3rd Floor' },
  { value: '4', label: '4th Floor' },
  { value: '5', label: '5th Floor' }
]

// Occupancy data by zone
const zones = ref([
  {
    id: 'Z001', name: 'Main Office Area', zone: 'office', floor: '2',
    current: 156, capacity: 200, percentage: 78, trend: '+12',
    peakTime: '14:30', avgStay: '2h 15m', utilization: 82,
    devices: 12, lastUpdate: '2024-01-15 10:30:00'
  },
  {
    id: 'Z002', name: 'Meeting Room A', zone: 'meeting', floor: '2',
    current: 8, capacity: 12, percentage: 67, trend: '-5',
    peakTime: '11:00', avgStay: '45m', utilization: 71,
    devices: 2, lastUpdate: '2024-01-15 10:28:00'
  },
  {
    id: 'Z003', name: 'Meeting Room B', zone: 'meeting', floor: '2',
    current: 0, capacity: 10, percentage: 0, trend: '0',
    peakTime: 'N/A', avgStay: 'N/A', utilization: 45,
    devices: 2, lastUpdate: '2024-01-15 10:29:00'
  },
  {
    id: 'Z004', name: 'Lounge Area', zone: 'common', floor: '1',
    current: 23, capacity: 50, percentage: 46, trend: '+8',
    peakTime: '12:30', avgStay: '20m', utilization: 68,
    devices: 4, lastUpdate: '2024-01-15 10:31:00'
  },
  {
    id: 'Z005', name: 'Cafeteria', zone: 'cafeteria', floor: '1',
    current: 45, capacity: 100, percentage: 45, trend: '+25',
    peakTime: '12:15', avgStay: '30m', utilization: 72,
    devices: 6, lastUpdate: '2024-01-15 10:27:00'
  },
  {
    id: 'Z006', name: 'Executive Suite', zone: 'office', floor: '5',
    current: 12, capacity: 20, percentage: 60, trend: '+3',
    peakTime: '10:00', avgStay: '3h', utilization: 85,
    devices: 4, lastUpdate: '2024-01-15 10:32:00'
  },
  {
    id: 'Z007', name: 'Open Workspace', zone: 'office', floor: '3',
    current: 89, capacity: 120, percentage: 74, trend: '+18',
    peakTime: '13:45', avgStay: '4h', utilization: 88,
    devices: 8, lastUpdate: '2024-01-15 10:33:00'
  },
  {
    id: 'Z008', name: 'Training Room', zone: 'meeting', floor: '3',
    current: 15, capacity: 25, percentage: 60, trend: '-2',
    peakTime: '09:30', avgStay: '2h', utilization: 65,
    devices: 2, lastUpdate: '2024-01-15 10:31:00'
  }
])

// Hourly occupancy data
const hourlyData = ref([
  { hour: '06:00', occupancy: 5, forecast: 3 },
  { hour: '07:00', occupancy: 15, forecast: 12 },
  { hour: '08:00', occupancy: 45, forecast: 48 },
  { hour: '09:00', occupancy: 78, forecast: 82 },
  { hour: '10:00', occupancy: 112, forecast: 108 },
  { hour: '11:00', occupancy: 135, forecast: 128 },
  { hour: '12:00', occupancy: 156, forecast: 158 },
  { hour: '13:00', occupancy: 142, forecast: 145 },
  { hour: '14:00', occupancy: 128, forecast: 132 },
  { hour: '15:00', occupancy: 98, forecast: 105 },
  { hour: '16:00', occupancy: 76, forecast: 82 },
  { hour: '17:00', occupancy: 45, forecast: 52 },
  { hour: '18:00', occupancy: 23, forecast: 28 },
  { hour: '19:00', occupancy: 12, forecast: 15 },
  { hour: '20:00', occupancy: 8, forecast: 10 }
])

// Occupancy statistics
const occupancyStats = reactive({
  totalCurrent: 0,
  totalCapacity: 0,
  overallPercentage: 0,
  peakOccupancy: 0,
  peakTime: '',
  avgStayTime: '0h',
  activeZones: 0,
  recommendedCleaning: ''
})

// Heatmap data for floor layout
const heatmapData = ref([
  [45, 32, 28, 15, 8],
  [78, 89, 67, 34, 12],
  [112, 98, 76, 45, 23],
  [89, 67, 45, 23, 8],
  [34, 28, 15, 8, 3]
])

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 8,
  total: zones.value.length
})

// Filtered zones
const filteredZones = computed(() => {
  let filtered = zones.value
  if (searchKeyword.value) {
    filtered = filtered.filter(z =>
        z.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        z.id.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedZone.value !== 'all') {
    filtered = filtered.filter(z => z.zone === selectedZone.value)
  }
  if (selectedFloor.value !== 'all') {
    filtered = filtered.filter(z => z.floor === selectedFloor.value)
  }
  pagination.total = filtered.length
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
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
        initChart()
        initHeatmap()
        updateStats()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  occupancyChart = echarts.init(chartRef.value)
  occupancyChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Actual Occupancy', 'Forecast'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: hourlyData.value.map(h => h.hour) },
    yAxis: { type: 'value', name: 'People Count' },
    series: [
      { name: 'Actual Occupancy', type: 'line', data: hourlyData.value.map(h => h.occupancy), smooth: true, lineStyle: { color: '#409EFF', width: 3 }, areaStyle: { opacity: 0.1, color: '#409EFF' }, symbol: 'circle', symbolSize: 8 },
      { name: 'Forecast', type: 'line', data: hourlyData.value.map(h => h.forecast), smooth: true, lineStyle: { color: '#E6A23C', width: 2, type: 'dashed' }, symbol: 'diamond', symbolSize: 8 }
    ]
  })
}

const initHeatmap = () => {
  if (!heatmapRef.value) return

  const maxValue = Math.max(...heatmapData.value.flat())

  heatmapChart = echarts.init(heatmapRef.value)
  heatmapChart.setOption({
    tooltip: { position: 'top', formatter: (params: any) => `Occupancy: ${params.data[2]} people` },
    grid: { left: '3%', right: '4%', top: '3%', containLabel: true },
    xAxis: { type: 'category', data: ['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E'], axisLabel: { rotate: 0 } },
    yAxis: { type: 'category', data: ['Floor 5', 'Floor 4', 'Floor 3', 'Floor 2', 'Floor 1'], axisLabel: { rotate: 0 } },
    visualMap: {
      min: 0,
      max: maxValue,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: 0,
      inRange: { color: ['#67C23A', '#E6A23C', '#F56C6C'] }
    },
    series: [{
      type: 'heatmap',
      data: heatmapData.value.flatMap((row, i) => row.map((value, j) => [j, i, value])),
      label: { show: true, formatter: (params: any) => params.data[2] },
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' } }
    }]
  })
}

const updateStats = () => {
  occupancyStats.totalCurrent = zones.value.reduce((sum, z) => sum + z.current, 0)
  occupancyStats.totalCapacity = zones.value.reduce((sum, z) => sum + z.capacity, 0)
  occupancyStats.overallPercentage = Math.round((occupancyStats.totalCurrent / occupancyStats.totalCapacity) * 100)
  occupancyStats.activeZones = zones.value.filter(z => z.current > 0).length

  const peakHour = hourlyData.value.reduce((max, curr) => curr.occupancy > max.occupancy ? curr : max, hourlyData.value[0])
  occupancyStats.peakOccupancy = peakHour.occupancy
  occupancyStats.peakTime = peakHour.hour

  // Calculate average stay time
  const stays = zones.value.filter(z => z.avgStay !== 'N/A').map(z => {
    const hours = parseInt(z.avgStay.split('h')[0]) || 0
    const minutes = parseInt(z.avgStay.split('h')[1]?.split('m')[0]) || 0
    return hours * 60 + minutes
  })
  const avgMinutes = stays.reduce((a, b) => a + b, 0) / stays.length
  occupancyStats.avgStayTime = `${Math.floor(avgMinutes / 60)}h ${Math.round(avgMinutes % 60)}m`

  // Recommend cleaning based on peak occupancy
  if (occupancyStats.peakOccupancy > 150) {
    occupancyStats.recommendedCleaning = 'High traffic areas need cleaning now'
  } else if (occupancyStats.peakOccupancy > 100) {
    occupancyStats.recommendedCleaning = 'Schedule cleaning in next 2 hours'
  } else {
    occupancyStats.recommendedCleaning = 'Regular cleaning schedule OK'
  }
}

const handleResize = () => {
  occupancyChart?.resize()
  heatmapChart?.resize()
}

// ==================== Occupancy Functions ====================
const refreshData = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  loading.value = false
  ElMessage.success('Occupancy data refreshed successfully')
}

const viewDetails = (zone: any) => {
  selectedZoneDetail.value = zone
  detailsVisible.value = true
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getTrendIcon = (trend: string) => {
  if (trend.startsWith('+')) return '📈'
  if (trend.startsWith('-')) return '📉'
  return '➡️'
}

const getTrendClass = (trend: string) => {
  if (trend.startsWith('+')) return 'trend-up'
  if (trend.startsWith('-')) return 'trend-down'
  return 'trend-neutral'
}

const getPercentageColor = (percentage: number) => {
  if (percentage < 50) return '#67C23A'
  if (percentage < 80) return '#E6A23C'
  return '#F56C6C'
}

const selectedZoneDetail = ref<any>(null)
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
          <span class="loading-title">Loading Occupancy Intelligence</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Intelligence - Occupancy Intelligence</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="occupancy-intelligence-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Occupancy Intelligence</h1>
        <p class="page-subtitle">Real-time space utilization and occupancy analytics</p>
      </div>
      <div class="header-right">
        <el-button size="large" @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
        <el-button size="large">
          <el-icon><Setting /></el-icon>
          Settings
        </el-button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total-icon">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ occupancyStats.totalCurrent }}</div>
          <div class="stat-label">Current Occupancy</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ occupancyStats.overallPercentage }}% of capacity</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon capacity-icon">
          <el-icon><OfficeBuilding /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ occupancyStats.totalCapacity }}</div>
          <div class="stat-label">Total Capacity</div>
        </div>
        <div class="stat-trend">
          <span class="trend-neutral">{{ occupancyStats.activeZones }} Active Zones</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon peak-icon">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ occupancyStats.peakOccupancy }}</div>
          <div class="stat-label">Peak Occupancy</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">at {{ occupancyStats.peakTime }}</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon stay-icon">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ occupancyStats.avgStayTime }}</div>
          <div class="stat-label">Avg Stay Duration</div>
        </div>
        <div class="stat-trend">
          <span class="trend-neutral">{{ occupancyStats.recommendedCleaning }}</span>
        </div>
      </div>
    </div>

    <!-- Chart Section -->
    <div class="charts-row">
      <div class="chart-section">
        <div class="section-header">
          <h3>Occupancy Trend (24 Hours)</h3>
          <el-button text type="primary" @click="initChart">Refresh</el-button>
        </div>
        <div ref="chartRef" class="occupancy-chart" style="height: 300px"></div>
      </div>

      <div class="chart-section">
        <div class="section-header">
          <h3>Floor Occupancy Heatmap</h3>
          <el-button text type="primary" @click="initHeatmap">Refresh</el-button>
        </div>
        <div ref="heatmapRef" class="heatmap" style="height: 300px"></div>
      </div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-bar">
      <div class="filters-left">
        <div class="search-box">
          <el-input
              v-model="searchKeyword"
              placeholder="Search zones..."
              :prefix-icon="Search"
              clearable
              style="width: 220px"
          />
        </div>
        <div class="zone-filters">
          <button
              v-for="z in zoneOptions"
              :key="z.value"
              class="zone-chip"
              :class="{ active: selectedZone === z.value }"
              @click="selectedZone = z.value"
          >
            <span>{{ z.label }}</span>
          </button>
        </div>
      </div>
      <div class="filters-right">
        <el-select v-model="selectedFloor" placeholder="Floor" clearable style="width: 140px">
          <el-option v-for="f in floorOptions.slice(1)" :key="f.value" :label="f.label" :value="f.value" />
        </el-select>
      </div>
    </div>

    <!-- Zones Grid -->
    <div class="zones-grid">
      <div
          v-for="zone in filteredZones"
          :key="zone.id"
          class="zone-card"
          @click="viewDetails(zone)"
      >
        <div class="card-header">
          <h4 class="zone-name">{{ zone.name }}</h4>
          <div class="zone-status">
            <span class="trend-indicator" :class="getTrendClass(zone.trend)">
              {{ getTrendIcon(zone.trend) }} {{ zone.trend }}
            </span>
          </div>
        </div>

        <div class="occupancy-display">
          <div class="occupancy-value">
            <span class="current">{{ zone.current }}</span>
            <span class="separator">/</span>
            <span class="capacity">{{ zone.capacity }}</span>
          </div>
          <div class="occupancy-label">Current Occupancy</div>
          <el-progress
              :percentage="zone.percentage"
              :color="getPercentageColor(zone.percentage)"
              :stroke-width="8"
          />
        </div>

        <div class="zone-stats">
          <div class="stat-item">
            <span class="stat-label">Utilization</span>
            <span class="stat-value">{{ zone.utilization }}%</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Peak Time</span>
            <span class="stat-value">{{ zone.peakTime }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Avg Stay</span>
            <span class="stat-value">{{ zone.avgStay }}</span>
          </div>
        </div>

        <div class="card-footer">
          <div class="footer-info">
            <el-icon><Clock /></el-icon>
            <span>{{ zone.lastUpdate.substring(11, 16) }}</span>
          </div>
          <el-button link type="primary" size="small">Details</el-button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredZones.length === 0" class="empty-state">
      <el-empty description="No zones found">
        <el-button type="primary">Reset Filters</el-button>
      </el-empty>
    </div>

    <!-- Pagination -->
    <div v-if="filteredZones.length > 0" class="pagination-wrapper">
      <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[8, 12, 16, 24]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
      />
    </div>

    <!-- Zone Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="selectedZoneDetail?.name" width="550px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Zone ID">{{ selectedZoneDetail?.id }}</el-descriptions-item>
        <el-descriptions-item label="Floor">{{ selectedZoneDetail?.floor }}th Floor</el-descriptions-item>
        <el-descriptions-item label="Current Occupancy">
          <span class="dialog-occupancy">{{ selectedZoneDetail?.current }}/{{ selectedZoneDetail?.capacity }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="Utilization Rate">{{ selectedZoneDetail?.utilization }}%</el-descriptions-item>
        <el-descriptions-item label="Peak Time">{{ selectedZoneDetail?.peakTime }}</el-descriptions-item>
        <el-descriptions-item label="Average Stay">{{ selectedZoneDetail?.avgStay }}</el-descriptions-item>
        <el-descriptions-item label="Trend">
          <span :class="getTrendClass(selectedZoneDetail?.trend)">
            {{ getTrendIcon(selectedZoneDetail?.trend) }} {{ selectedZoneDetail?.trend }}%
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="Sensors">{{ selectedZoneDetail?.devices }} devices</el-descriptions-item>
        <el-descriptions-item label="Last Update">{{ selectedZoneDetail?.lastUpdate }}</el-descriptions-item>
        <el-descriptions-item label="Recommendation" :span="2">
          <span v-if="selectedZoneDetail?.percentage > 80">
            ⚠️ High traffic - Consider adding more space
          </span>
          <span v-else-if="selectedZoneDetail?.percentage > 50">
            📊 Moderate usage - Optimal utilization
          </span>
          <span v-else>
            ✅ Low occupancy - Energy saving opportunities
          </span>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
        <el-button type="primary">Export Report</el-button>
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
.occupancy-intelligence-container {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #eef2f6 100%);
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #1e293b 0%, #2d3a4e 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.header-right {
  display: flex;
  gap: 12px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.total-icon {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #409eff;
}

.capacity-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.peak-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.stay-icon {
  background: linear-gradient(135deg, #fef0f0 0%, #fcd9d9 100%);
  color: #f56c6c;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  margin-top: 4px;
}

.stat-trend {
  position: absolute;
  top: 16px;
  right: 16px;
  font-size: 11px;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 20px;
  color: #67c23a;
}

.trend-up {
  color: #f56c6c;
}

.trend-neutral {
  color: #909399;
}

/* Charts Row */
.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.chart-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.occupancy-chart,
.heatmap {
  width: 100%;
}

/* Filters Bar */
.filters-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 24px;
}

.filters-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.zone-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.zone-chip {
  padding: 8px 16px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 40px;
  font-size: 13px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s ease;
}

.zone-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.zone-chip.active {
  background: #409eff;
  border-color: #409eff;
  color: white;
}

.filters-right {
  display: flex;
  gap: 12px;
}

/* Zones Grid */
.zones-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.zone-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  cursor: pointer;
  padding: 20px;
}

.zone-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.zone-name {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.trend-indicator {
  font-size: 13px;
  padding: 4px 8px;
  border-radius: 20px;
}

.trend-up {
  background: #fef0f0;
  color: #f56c6c;
}

.trend-down {
  background: #f0f9ff;
  color: #67c23a;
}

.trend-neutral {
  background: #f5f7fa;
  color: #909399;
}

.occupancy-display {
  text-align: center;
  margin-bottom: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 16px;
}

.occupancy-value {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 8px;
}

.occupancy-value .current {
  color: #409eff;
}

.occupancy-value .capacity {
  color: #909399;
  font-size: 24px;
}

.occupancy-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 12px;
}

.zone-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  padding: 12px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-item {
  text-align: center;
  flex: 1;
}

.stat-label {
  font-size: 11px;
  color: #909399;
  display: block;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-info {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
}

/* Empty State */
.empty-state {
  padding: 60px 0;
  text-align: center;
}

/* Pagination */
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
}

/* Dialog */
.dialog-occupancy {
  font-weight: 600;
  color: #409eff;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-row {
    grid-template-columns: 1fr;
  }

  .zones-grid {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }
}

@media (max-width: 768px) {
  .occupancy-intelligence-container {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filters-left {
    flex-direction: column;
  }

  .zone-filters {
    justify-content: center;
  }

  .page-header {
    flex-direction: column;
    text-align: center;
  }

  .header-right {
    width: 100%;
    justify-content: center;
  }

  .zones-grid {
    grid-template-columns: 1fr;
  }
}
</style>