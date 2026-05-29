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

  <!-- Occupancy Page Content -->
  <div v-else class="occupancy-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>Occupancy Analytics</h1>
        <p class="subtitle">Monitor real-time and historical space utilization across your facilities</p>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="refreshData">Refresh</el-button>
        <el-button type="primary" :icon="Download" @click="exportReport">Export Report</el-button>
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
      <div class="kpi-card current">
        <div class="kpi-icon">
          <el-icon :size="32"><User /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ currentOccupancy }}<span class="unit"> people</span></div>
          <div class="kpi-label">Current Occupancy</div>
        </div>
        <div class="kpi-trend" :class="occupancyTrend >= 0 ? 'positive' : 'negative'">
          <el-icon><CaretTop v-if="occupancyTrend >= 0" /><CaretBottom v-else /></el-icon>
          {{ Math.abs(occupancyTrend) }}%
        </div>
      </div>
      <div class="kpi-card utilization">
        <div class="kpi-icon">
          <el-icon :size="32"><PieChart /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ utilizationRate }}%</div>
          <div class="kpi-label">Space Utilization</div>
        </div>
        <el-progress :percentage="utilizationRate" :color="getUtilizationColor(utilizationRate)" :stroke-width="8" style="margin-top: 8px" />
      </div>
      <div class="kpi-card peak">
        <div class="kpi-icon">
          <el-icon :size="32"><TrendCharts /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ peakOccupancy }}<span class="unit"> people</span></div>
          <div class="kpi-label">Peak Occupancy (Today)</div>
        </div>
        <div class="kpi-sub">at {{ peakTime }}</div>
      </div>
      <div class="kpi-card capacity">
        <div class="kpi-icon">
          <el-icon :size="32"><OfficeBuilding /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ totalCapacity }}<span class="unit"> seats</span></div>
          <div class="kpi-label">Total Capacity</div>
        </div>
        <div class="kpi-sub">{{ availableCapacity }} available</div>
      </div>
    </div>

    <!-- Occupancy Trend Chart -->
    <div class="chart-card">
      <div class="card-header">
        <h3>Occupancy Trend</h3>
        <el-radio-group v-model="trendPeriod" size="small" @change="fetchTrendData">
          <el-radio-button label="day">Today</el-radio-button>
          <el-radio-button label="week">This Week</el-radio-button>
          <el-radio-button label="month">This Month</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-container" ref="trendChartRef"></div>
    </div>

    <!-- Occupancy by Building and Floor -->
    <div class="two-columns">
      <div class="chart-card">
        <div class="card-header">
          <h3>Occupancy by Building</h3>
          <el-select v-model="buildingFilter" placeholder="Filter by building" clearable size="small" style="width: 140px">
            <el-option label="All Buildings" value="all" />
            <el-option label="Building A" value="building-a" />
            <el-option label="Building B" value="building-b" />
            <el-option label="Data Center" value="datacenter" />
          </el-select>
        </div>
        <div class="chart-container" ref="buildingChartRef"></div>
      </div>
      <div class="chart-card">
        <div class="card-header">
          <h3>Occupancy by Floor</h3>
        </div>
        <div class="chart-container" ref="floorChartRef"></div>
      </div>
    </div>

    <!-- Zone Occupancy Table -->
    <div class="table-card">
      <div class="card-header">
        <h3>Zone Occupancy Details</h3>
        <el-input
            v-model="searchText"
            placeholder="Search by zone..."
            :prefix-icon="Search"
            style="width: 240px"
            clearable
        />
      </div>
      <el-table :data="paginatedZones" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="zoneName" label="Zone Name" min-width="160" />
        <el-table-column prop="building" label="Building" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.building }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="floor" label="Floor" width="100" />
        <el-table-column prop="capacity" label="Capacity" width="100" align="center">
          <template #default="{ row }">
            {{ row.capacity }}
          </template>
        </el-table-column>
        <el-table-column prop="current" label="Current Occupancy" width="130" align="center" sortable>
          <template #default="{ row }">
            <span :class="getOccupancyClass(row.current, row.capacity)">
              {{ row.current }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="utilization" label="Utilization" width="160">
          <template #default="{ row }">
            <div class="utilization-cell">
              <span class="util-percent">{{ row.utilization }}%</span>
              <el-progress :percentage="row.utilization" :color="getUtilizationColor(row.utilization)" :stroke-width="6" :show-text="false" style="flex: 1" />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.utilization)" size="small" effect="dark">
              {{ getStatusLabel(row.utilization) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredZones.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Hourly Occupancy Heatmap -->
    <div class="chart-card">
      <div class="card-header">
        <h3>Hourly Occupancy Heatmap (Week View)</h3>
      </div>
      <div class="chart-container" ref="heatmapChartRef"></div>
    </div>

    <!-- Recommendations -->
    <div class="recommendations-section">
      <div class="section-header">
        <h2>
          <el-icon><EditPen /></el-icon>
          Space Optimization Recommendations
        </h2>
        <el-button link type="primary" @click="viewAllRecommendations">View All →</el-button>
      </div>
      <div class="recommendations-list">
        <div v-for="rec in recommendations" :key="rec.id" class="recommendation-item">
          <div class="rec-icon" :class="rec.priority">
            <el-icon><Check /></el-icon>
          </div>
          <div class="rec-content">
            <div class="rec-title">{{ rec.title }}</div>
            <div class="rec-description">{{ rec.description }}</div>
            <div class="rec-metrics">
              <span><el-icon><TrendCharts /></el-icon> Potential Utilization Gain: +{{ rec.gain }}%</span>
              <span><el-icon><Timer /></el-icon> Est. Savings: {{ rec.savings }}</span>
            </div>
          </div>
          <div class="rec-actions">
            <el-button size="small" type="primary" plain @click="viewRecommendation(rec)">Details</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Refresh,
  Download,
  User,
  PieChart,
  TrendCharts,
  OfficeBuilding,
  Search,
  EditPen,
  Timer,
  Check,
  CaretTop,
  CaretBottom
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
interface ZoneOccupancy {
  id: number
  zoneName: string
  building: string
  floor: string
  capacity: number
  current: number
  utilization: number
}

interface Recommendation {
  id: number
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
  gain: number
  savings: string
}

// ==================== State ====================
const dateRange = ref<[Date, Date] | null>(null)
const trendPeriod = ref<'day' | 'week' | 'month'>('week')
const buildingFilter = ref('all')
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const trendChartRef = ref<HTMLElement | null>(null)
const buildingChartRef = ref<HTMLElement | null>(null)
const floorChartRef = ref<HTMLElement | null>(null)
const heatmapChartRef = ref<HTMLElement | null>(null)
let trendChart: echarts.ECharts | null = null
let buildingChart: echarts.ECharts | null = null
let floorChart: echarts.ECharts | null = null
let heatmapChart: echarts.ECharts | null = null

// ==================== Mock Data ====================
const zoneOccupancy = ref<ZoneOccupancy[]>([
  { id: 1, zoneName: 'Open Workspace - North', building: 'Building A', floor: 'Floor 1', capacity: 80, current: 52, utilization: 65 },
  { id: 2, zoneName: 'Open Workspace - South', building: 'Building A', floor: 'Floor 1', capacity: 75, current: 48, utilization: 64 },
  { id: 3, zoneName: 'Meeting Rooms', building: 'Building A', floor: 'Floor 1', capacity: 40, current: 28, utilization: 70 },
  { id: 4, zoneName: 'Open Workspace', building: 'Building A', floor: 'Floor 2', capacity: 90, current: 62, utilization: 69 },
  { id: 5, zoneName: 'Executive Offices', building: 'Building A', floor: 'Floor 2', capacity: 25, current: 18, utilization: 72 },
  { id: 6, zoneName: 'Open Workspace', building: 'Building B', floor: 'Floor 1', capacity: 100, current: 55, utilization: 55 },
  { id: 7, zoneName: 'Meeting Rooms', building: 'Building B', floor: 'Floor 1', capacity: 35, current: 15, utilization: 43 },
  { id: 8, zoneName: 'Open Workspace', building: 'Building B', floor: 'Floor 2', capacity: 85, current: 42, utilization: 49 },
  { id: 9, zoneName: 'Cafeteria', building: 'Building B', floor: 'Floor 2', capacity: 60, current: 35, utilization: 58 },
  { id: 10, zoneName: 'Data Center Floor', building: 'Data Center', floor: 'Ground', capacity: 50, current: 12, utilization: 24 },
  { id: 11, zoneName: 'Server Room A', building: 'Data Center', floor: 'Ground', capacity: 30, current: 4, utilization: 13 },
  { id: 12, zoneName: 'Break Room', building: 'Building A', floor: 'Floor 1', capacity: 20, current: 8, utilization: 40 }
])

const recommendations = ref<Recommendation[]>([
  { id: 1, title: 'Consolidate Underutilized Spaces', description: 'Building B Floor 2 has 49% utilization. Consider consolidating teams to reduce energy costs.', priority: 'high', gain: 15, savings: '$12,500/year' },
  { id: 2, title: 'Optimize Meeting Room Capacity', description: 'Meeting rooms show peak usage at 2PM. Consider adding more small meeting spaces.', priority: 'medium', gain: 8, savings: '$5,200/year' },
  { id: 3, title: 'Implement Hot Desking', description: 'Open workspace utilization varies significantly. Hot desking could improve space efficiency.', priority: 'high', gain: 20, savings: '$18,000/year' }
])

// ==================== Computed Values ====================
const currentOccupancy = computed(() => 325)
const utilizationRate = computed(() => 58)
const peakOccupancy = computed(() => 412)
const peakTime = computed(() => '14:30')
const totalCapacity = computed(() => 720)
const availableCapacity = computed(() => totalCapacity.value - currentOccupancy.value)
const occupancyTrend = computed(() => 5.2)

const filteredZones = computed(() => {
  let result = [...zoneOccupancy.value]
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(z =>
        z.zoneName.toLowerCase().includes(search) ||
        z.building.toLowerCase().includes(search)
    )
  }
  if (buildingFilter.value !== 'all') {
    const filterMap: Record<string, string> = {
      'building-a': 'Building A',
      'building-b': 'Building B',
      'datacenter': 'Data Center'
    }
    result = result.filter(z => z.building === filterMap[buildingFilter.value])
  }
  return result
})

const paginatedZones = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredZones.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getOccupancyClass = (current: number, capacity: number) => {
  const rate = (current / capacity) * 100
  if (rate >= 80) return 'text-danger'
  if (rate >= 60) return 'text-warning'
  return 'text-success'
}

const getUtilizationColor = (percentage: number) => {
  if (percentage >= 80) return '#f56c6c'
  if (percentage >= 60) return '#e6a23c'
  if (percentage >= 40) return '#409eff'
  return '#67c23a'
}

const getStatusLabel = (utilization: number) => {
  if (utilization >= 80) return 'High'
  if (utilization >= 60) return 'Medium'
  if (utilization >= 40) return 'Low'
  return 'Very Low'
}

const getStatusTagType = (utilization: number) => {
  if (utilization >= 80) return 'danger'
  if (utilization >= 60) return 'warning'
  if (utilization >= 40) return 'primary'
  return 'info'
}

const dateShortcuts = [
  { text: 'Today', value: () => { const end = new Date(); const start = new Date(); start.setHours(0, 0, 0, 0); return [start, end] } },
  { text: 'Last 7 Days', value: () => { const end = new Date(); const start = new Date(); start.setDate(start.getDate() - 7); return [start, end] } },
  { text: 'This Month', value: () => { const end = new Date(); const start = new Date(); start.setDate(1); return [start, end] } }
]

// ==================== Chart Functions ====================
const generateTrendData = () => {
  if (trendPeriod.value === 'day') {
    const hours = ['06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00']
    const occupancy = [45, 78, 145, 268, 312, 348, 365, 378, 412, 398, 356, 298, 189, 112, 56]
    return { labels: hours, occupancy }
  }
  if (trendPeriod.value === 'week') {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    const occupancy = [325, 342, 358, 365, 348, 156, 89]
    return { labels: days, occupancy }
  }
  const weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
  const occupancy = [305, 318, 335, 342]
  return { labels: weeks, occupancy }
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)
  const data = generateTrendData()

  trendChart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: (value: number) => value + ' people' },
    xAxis: { type: 'category', data: data.labels, axisLabel: { rotate: trendPeriod.value === 'day' ? 45 : 0 } },
    yAxis: { type: 'value', name: 'Occupancy (people)' },
    series: [{
      type: 'line', data: data.occupancy, smooth: true, symbol: 'circle',
      lineStyle: { width: 3, color: '#409eff' }, areaStyle: { opacity: 0.1, color: '#409eff' }
    }]
  })
}

const initBuildingChart = () => {
  if (!buildingChartRef.value) return
  if (buildingChart) buildingChart.dispose()

  buildingChart = echarts.init(buildingChartRef.value)

  const buildings = ['Building A', 'Building B', 'Data Center']
  const current = [208, 147, 16]
  const capacity = [330, 280, 80]

  buildingChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: (params: any) => {
        return `${params[0].axisValue}<br/>Current: ${params[0].value} people<br/>Capacity: ${capacity[params[0].dataIndex]} people<br/>Utilization: ${Math.round(params[0].value / capacity[params[0].dataIndex] * 100)}%`
      }},
    legend: { data: ['Current Occupancy'], bottom: 0 },
    grid: { left: '10%', right: '5%', top: '5%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: buildings },
    yAxis: { type: 'value', name: 'Occupancy (people)' },
    series: [{
      type: 'bar', data: current,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: (params: any) => {
          const rate = params.data / capacity[params.dataIndex] * 100
          if (rate >= 80) return '#f56c6c'
          if (rate >= 60) return '#e6a23c'
          return '#67c23a'
        }},
      label: { show: true, position: 'top', formatter: (params: any) => `${params.value} / ${capacity[params.dataIndex]}` }
    }]
  })
}

const initFloorChart = () => {
  if (!floorChartRef.value) return
  if (floorChart) floorChart.dispose()

  floorChart = echarts.init(floorChartRef.value)

  const floors = ['Building A - F1', 'Building A - F2', 'Building B - F1', 'Building B - F2']
  const utilization = [66, 70, 52, 52]

  floorChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: (value: number) => value + '%' },
    grid: { left: '12%', right: '5%', top: '5%', bottom: '5%', containLabel: true },
    xAxis: { type: 'value', name: 'Utilization (%)', max: 100 },
    yAxis: { type: 'category', data: floors },
    series: [{
      type: 'bar', data: utilization,
      itemStyle: { borderRadius: [0, 4, 4, 0], color: (params: any) => {
          if (params.data >= 80) return '#f56c6c'
          if (params.data >= 60) return '#e6a23c'
          if (params.data >= 40) return '#409eff'
          return '#67c23a'
        }},
      label: { show: true, position: 'right', formatter: '{c}%' }
    }]
  })
}

const initHeatmapChart = () => {
  if (!heatmapChartRef.value) return
  if (heatmapChart) heatmapChart.dispose()

  heatmapChart = echarts.init(heatmapChartRef.value)

  const hours = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00']
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']

  const data: [number, number, number][] = []
  for (let i = 0; i < days.length; i++) {
    for (let j = 0; j < hours.length; j++) {
      let value = 40 + Math.random() * 50
      if (j >= 3 && j <= 7) value = 60 + Math.random() * 35
      if (i === 4) value = value * 0.7
      data.push([j, i, Math.round(value)])
    }
  }

  heatmapChart.setOption({
    tooltip: { position: 'top', formatter: (params: any) => `${days[params.value[1]]} ${hours[params.value[0]]}<br/>Occupancy: ${params.value[2]} people` },
    grid: { left: '8%', right: '5%', top: '10%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', data: hours, axisLabel: { rotate: 45 } },
    yAxis: { type: 'category', data: days },
    visualMap: { min: 0, max: 100, calculable: true, orient: 'horizontal', left: 'center', bottom: 0, inRange: { color: ['#67c23a', '#409eff', '#e6a23c', '#f56c6c'] } },
    series: [{
      type: 'heatmap', data: data, label: { show: true, fontSize: 10 },
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.5)' } }
    }]
  })
}

// ==================== Actions ====================
const refreshData = async () => {
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  ElMessage.success('Occupancy data refreshed')
  initTrendChart()
  initBuildingChart()
  initFloorChart()
  initHeatmapChart()
  tableLoading.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting occupancy report...')
}

const fetchTrendData = () => {
  initTrendChart()
}

const handleDateChange = () => {
  currentPage.value = 1
}

const viewAllRecommendations = () => {
  ElMessage.info('Viewing all recommendations')
}

const viewRecommendation = (rec: Recommendation) => {
  ElMessage.info(`Viewing recommendation: ${rec.title}`)
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Window Resize Handler ====================
const handleResize = () => {
  trendChart?.resize()
  buildingChart?.resize()
  floorChart?.resize()
  heatmapChart?.resize()
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
        initBuildingChart()
        initFloorChart()
        initHeatmapChart()
      }, 100)
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  buildingChart?.dispose()
  floorChart?.dispose()
  heatmapChart?.dispose()
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
.occupancy-page {
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

.kpi-card.current .kpi-icon { background: #e8f4ff; color: #409eff; }
.kpi-card.utilization .kpi-icon { background: #fff7e8; color: #e6a23c; }
.kpi-card.peak .kpi-icon { background: #ffe8e8; color: #f56c6c; }
.kpi-card.capacity .kpi-icon { background: #e8f8f0; color: #67c23a; }

.kpi-info {
  flex: 1;
}

.kpi-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
  line-height: 1.2;
}

.kpi-value .unit {
  font-size: 14px;
  font-weight: 400;
  color: #909399;
}

.kpi-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.kpi-sub {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 2px;
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

/* Table Styles */
.utilization-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.util-percent {
  font-size: 13px;
  font-weight: 500;
  min-width: 40px;
}

.text-success { color: #67c23a; font-weight: 500; }
.text-warning { color: #e6a23c; font-weight: 500; }
.text-danger { color: #f56c6c; font-weight: 500; }

.pagination-wrapper {
  padding: 20px 0 0;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
  margin-top: 16px;
}

/* Recommendations Section */
.recommendations-section {
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1f2f3d;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recommendation-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 14px;
  transition: all 0.2s;
}

.recommendation-item:hover {
  background: #f5f7fa;
  transform: translateX(4px);
}

.rec-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rec-icon.high { background: #ffe8e8; color: #f56c6c; }
.rec-icon.medium { background: #fff7e8; color: #e6a23c; }
.rec-icon.low { background: #e8f8f0; color: #67c23a; }

.rec-content {
  flex: 1;
}

.rec-title {
  font-weight: 600;
  color: #1f2f3d;
  margin-bottom: 6px;
}

.rec-description {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.rec-metrics {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #909399;
}

.rec-metrics .el-icon {
  vertical-align: middle;
  margin-right: 4px;
}

.rec-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.recommendation-item:hover .rec-actions {
  opacity: 1;
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