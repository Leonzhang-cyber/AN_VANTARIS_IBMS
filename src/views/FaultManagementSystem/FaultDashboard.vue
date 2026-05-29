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
        <div class="loading-tip">Fault Management System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Fault Dashboard Page Content -->
  <div v-else class="fault-dashboard-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <div class="title-badge">
          <el-icon><WarningFilled /></el-icon>
          <span>FMS Dashboard</span>
        </div>
        <h1>Fault Management Dashboard</h1>
        <p class="subtitle">Real-time monitoring and analysis of system faults across your infrastructure</p>
      </div>
      <div class="header-actions">
        <button class="action-btn" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          <span>Refresh</span>
        </button>
        <button class="action-btn primary" @click="exportReport">
          <el-icon><Download /></el-icon>
          <span>Export Report</span>
        </button>
        <select v-model="timeRange" class="time-range-select" @change="updateChartData">
          <option value="today">Today</option>
          <option value="week">Last 7 Days</option>
          <option value="month">Last 30 Days</option>
          <option value="quarter">Last 90 Days</option>
        </select>
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-icon critical">
          <el-icon><CircleCloseFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ criticalFaults }}</div>
          <div class="kpi-label">Critical Faults</div>
        </div>
        <div class="kpi-trend critical">
          <el-icon><CaretTop /></el-icon>
          +12%
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon major">
          <el-icon><WarningFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ majorFaults }}</div>
          <div class="kpi-label">Major Faults</div>
        </div>
        <div class="kpi-trend major">
          <el-icon><CaretBottom /></el-icon>
          -5%
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon minor">
          <el-icon><InfoFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ minorFaults }}</div>
          <div class="kpi-label">Minor Faults</div>
        </div>
        <div class="kpi-trend minor">
          <el-icon><CaretBottom /></el-icon>
          -8%
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon resolved">
          <el-icon><CircleCheckFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ resolvedFaults }}</div>
          <div class="kpi-label">Resolved (MTD)</div>
        </div>
        <div class="kpi-trend resolved">
          <el-icon><CaretTop /></el-icon>
          +18%
        </div>
      </div>
    </div>

    <!-- Second Row Stats -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-header">
          <span class="stat-title">MTBF</span>
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-value">{{ mtbf }}<span class="stat-unit"> hours</span></div>
        <div class="stat-change positive">↑ 5.2% vs last period</div>
      </div>
      <div class="stat-card">
        <div class="stat-header">
          <span class="stat-title">MTTR</span>
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-value">{{ mttr }}<span class="stat-unit"> hours</span></div>
        <div class="stat-change positive">↓ 8.5% vs last period</div>
      </div>
      <div class="stat-card">
        <div class="stat-header">
          <span class="stat-title">System Availability</span>
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="stat-value">{{ availability }}<span class="stat-unit">%</span></div>
        <div class="stat-change positive">↑ 0.8% vs last period</div>
      </div>
      <div class="stat-card">
        <div class="stat-header">
          <span class="stat-title">Mean Time to Detect</span>
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-value">{{ mttd }}<span class="stat-unit"> min</span></div>
        <div class="stat-change positive">↓ 12.3% vs last period</div>
      </div>
    </div>

    <!-- Fault Trend Chart -->
    <div class="chart-card">
      <div class="card-header">
        <h3>Fault Trend Analysis</h3>
        <el-radio-group v-model="trendPeriod" size="small" @change="updateTrendChart">
          <el-radio-button label="week">Weekly</el-radio-button>
          <el-radio-button label="month">Monthly</el-radio-button>
          <el-radio-button label="quarter">Quarterly</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-container" ref="trendChartRef"></div>
    </div>

    <!-- Fault by Category and System -->
    <div class="two-columns">
      <div class="chart-card">
        <div class="card-header">
          <h3>Faults by Category</h3>
        </div>
        <div class="chart-container" ref="categoryChartRef"></div>
      </div>
      <div class="chart-card">
        <div class="card-header">
          <h3>Top Affected Systems</h3>
        </div>
        <div class="chart-container" ref="systemChartRef"></div>
      </div>
    </div>

    <!-- Active Faults Table -->
    <div class="table-card">
      <div class="card-header">
        <h3>Active Faults</h3>
        <div class="filter-group">
          <select v-model="severityFilter" class="filter-select">
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="major">Major</option>
            <option value="minor">Minor</option>
          </select>
          <select v-model="statusFilter" class="filter-select">
            <option value="all">All Status</option>
            <option value="open">Open</option>
            <option value="investigating">Investigating</option>
            <option value="resolved">Resolved</option>
          </select>
          <input type="text" v-model="searchText" placeholder="Search faults..." class="search-input" />
        </div>
      </div>
      <el-table :data="paginatedFaults" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="Fault Title" min-width="200" show-overflow-tooltip />
        <el-table-column prop="category" label="Category" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityTagType(row.severity)" size="small" effect="dark">
              {{ row.severity.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detectedAt" label="Detected" width="160" sortable />
        <el-table-column prop="assignedTo" label="Assigned To" width="140" />
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewFault(row)">View</el-button>
            <el-button link type="success" size="small" @click="assignFault(row)">Assign</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredFaults.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Fault Distribution by Location -->
    <div class="location-card">
      <div class="card-header">
        <h3>Fault Distribution by Location</h3>
      </div>
      <div class="location-grid">
        <div v-for="location in faultLocations" :key="location.name" class="location-item">
          <div class="location-name">{{ location.name }}</div>
          <div class="location-stats">
            <span class="critical-count">C:{{ location.critical }}</span>
            <span class="major-count">M:{{ location.major }}</span>
            <span class="minor-count">N:{{ location.minor }}</span>
          </div>
          <div class="location-progress">
            <div class="progress-bar-custom">
              <div class="progress-critical" :style="{ width: getCriticalPercent(location) + '%' }"></div>
              <div class="progress-major" :style="{ width: getMajorPercent(location) + '%' }"></div>
              <div class="progress-minor" :style="{ width: getMinorPercent(location) + '%' }"></div>
            </div>
          </div>
          <div class="location-total">Total: {{ location.total }} faults</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import {
  Refresh, Download, WarningFilled, CircleCloseFilled, InfoFilled,
  CircleCheckFilled, TrendCharts, Timer, DataLine, Clock,
  CaretTop, CaretBottom
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

// Loading State
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)
const loadingMessages = ['Preparing...', 'Loading fault data...', 'Analyzing trends...', 'Almost ready...']

// Data Models
interface Fault {
  id: number
  title: string
  category: string
  severity: 'critical' | 'major' | 'minor'
  status: 'open' | 'investigating' | 'resolved'
  detectedAt: string
  assignedTo: string
}

interface FaultLocation {
  name: string
  critical: number
  major: number
  minor: number
  total: number
}

// State
const timeRange = ref('week')
const trendPeriod = ref('month')
const severityFilter = ref('all')
const statusFilter = ref('all')
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const trendChartRef = ref<HTMLElement | null>(null)
const categoryChartRef = ref<HTMLElement | null>(null)
const systemChartRef = ref<HTMLElement | null>(null)
let trendChart: echarts.ECharts | null = null
let categoryChart: echarts.ECharts | null = null
let systemChart: echarts.ECharts | null = null

// Mock Data - IBMS真实场景故障数据
const faults = ref<Fault[]>([
  { id: 1001, title: 'AHU-101 Compressor High Discharge Pressure', category: 'HVAC', severity: 'critical', status: 'open', detectedAt: '2025-05-29 08:23:15', assignedTo: 'Mike Johnson' },
  { id: 1002, title: 'UPS-01 Battery String Voltage Imbalance', category: 'Electrical', severity: 'major', status: 'investigating', detectedAt: '2025-05-29 07:45:22', assignedTo: 'John Smith' },
  { id: 1003, title: 'Server Room Rack A3 Inlet Temperature Exceeded', category: 'DCIM', severity: 'critical', status: 'open', detectedAt: '2025-05-29 06:30:05', assignedTo: 'Sarah Chen' },
  { id: 1004, title: 'Chiller-02 Evaporator Approach Temperature High', category: 'HVAC', severity: 'major', status: 'investigating', detectedAt: '2025-05-28 22:15:30', assignedTo: 'Mike Johnson' },
  { id: 1005, title: 'Lighting Control Panel LCP-05 Modbus Communication Lost', category: 'Lighting', severity: 'minor', status: 'resolved', detectedAt: '2025-05-28 18:45:00', assignedTo: 'Lisa Wong' },
  { id: 1006, title: 'Water Leak Detection Sensor LL-103 Alert', category: 'Plumbing', severity: 'major', status: 'open', detectedAt: '2025-05-28 14:20:10', assignedTo: 'Tom Davis' },
  { id: 1007, title: 'Access Control Reader RDR-208 Offline', category: 'Security', severity: 'minor', status: 'resolved', detectedAt: '2025-05-28 09:35:42', assignedTo: 'Security Team' },
  { id: 1008, title: 'VFD-105 Overcurrent Fault', category: 'Electrical', severity: 'critical', status: 'investigating', detectedAt: '2025-05-27 23:10:15', assignedTo: 'John Smith' },
  { id: 1009, title: 'FCU-205 Fan Motor Locked Rotor', category: 'HVAC', severity: 'major', status: 'open', detectedAt: '2025-05-27 15:20:00', assignedTo: 'Mike Johnson' },
  { id: 1010, title: 'BMS Gateway Communication Intermittent', category: 'BMS', severity: 'minor', status: 'resolved', detectedAt: '2025-05-27 11:00:00', assignedTo: 'Sarah Chen' },
  { id: 1011, title: 'Cooling Tower CT-01 Fan Vibration High', category: 'HVAC', severity: 'major', status: 'open', detectedAt: '2025-05-26 20:30:00', assignedTo: 'Mike Johnson' },
  { id: 1012, title: 'Generator GEN-01 Fuel Level Low', category: 'Electrical', severity: 'critical', status: 'investigating', detectedAt: '2025-05-26 14:15:00', assignedTo: 'John Smith' },
  { id: 1013, title: 'Server Room Humidity Low', category: 'DCIM', severity: 'minor', status: 'resolved', detectedAt: '2025-05-26 09:00:00', assignedTo: 'Sarah Chen' },
  { id: 1014, title: 'Fire Alarm Panel FA-101 Zone 3 Fault', category: 'Fire Safety', severity: 'critical', status: 'open', detectedAt: '2025-05-25 18:45:00', assignedTo: 'Tom Davis' },
  { id: 1015, title: 'VAV Box VAV-309 Actuator Stuck', category: 'HVAC', severity: 'major', status: 'investigating', detectedAt: '2025-05-25 12:30:00', assignedTo: 'Mike Johnson' }
])

const faultLocations = ref<FaultLocation[]>([
  { name: 'Building A', critical: 3, major: 5, minor: 8, total: 16 },
  { name: 'Building B', critical: 2, major: 4, minor: 6, total: 12 },
  { name: 'Data Center', critical: 4, major: 3, minor: 2, total: 9 },
  { name: 'Building C', critical: 1, major: 3, minor: 5, total: 9 }
])

// Computed
const criticalFaults = computed(() => faults.value.filter(f => f.severity === 'critical' && f.status !== 'resolved').length)
const majorFaults = computed(() => faults.value.filter(f => f.severity === 'major' && f.status !== 'resolved').length)
const minorFaults = computed(() => faults.value.filter(f => f.severity === 'minor' && f.status !== 'resolved').length)
const resolvedFaults = computed(() => faults.value.filter(f => f.status === 'resolved').length)
const mtbf = computed(() => 1872)
const mttr = computed(() => 4.2)
const availability = computed(() => 99.78)
const mttd = computed(() => 12.5)

const filteredFaults = computed(() => {
  let result = [...faults.value]
  if (severityFilter.value !== 'all') {
    result = result.filter(f => f.severity === severityFilter.value)
  }
  if (statusFilter.value !== 'all') {
    result = result.filter(f => f.status === statusFilter.value)
  }
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(f => f.title.toLowerCase().includes(search))
  }
  return result
})

const paginatedFaults = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredFaults.value.slice(start, end)
})

// Helper Functions
const getSeverityTagType = (severity: string) => {
  const map: Record<string, string> = { critical: 'danger', major: 'warning', minor: 'info' }
  return map[severity] || 'info'
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = { open: 'danger', investigating: 'warning', resolved: 'success' }
  return map[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = { open: 'Open', investigating: 'Investigating', resolved: 'Resolved' }
  return map[status] || status
}

const getCriticalPercent = (location: FaultLocation) => {
  if (location.total === 0) return 0
  return (location.critical / location.total) * 100
}

const getMajorPercent = (location: FaultLocation) => {
  if (location.total === 0) return 0
  return (location.major / location.total) * 100
}

const getMinorPercent = (location: FaultLocation) => {
  if (location.total === 0) return 0
  return (location.minor / location.total) * 100
}

// Chart Functions
const getTrendData = () => {
  if (trendPeriod.value === 'week') {
    return {
      xAxis: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      critical: [3, 2, 4, 3, 2, 1, 2],
      major: [5, 4, 6, 5, 4, 2, 3],
      minor: [4, 3, 5, 4, 3, 2, 2]
    }
  } else if (trendPeriod.value === 'month') {
    return {
      xAxis: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
      critical: [8, 6, 7, 5],
      major: [12, 10, 9, 8],
      minor: [15, 14, 12, 10]
    }
  } else {
    return {
      xAxis: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
      critical: [12, 10, 11, 9, 8, 7, 6, 5, 7, 8, 6, 5],
      major: [18, 16, 17, 15, 14, 13, 12, 11, 13, 14, 12, 10],
      minor: [22, 20, 21, 19, 18, 17, 16, 15, 17, 18, 16, 14]
    }
  }
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)
  const data = getTrendData()
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Critical', 'Major', 'Minor'], bottom: 0 },
    grid: { left: '3%', right: '4%', top: '10%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', data: data.xAxis },
    yAxis: { type: 'value', name: 'Number of Faults' },
    series: [
      { name: 'Critical', type: 'line', data: data.critical, smooth: true, lineStyle: { width: 2, color: '#f56c6c' }, symbol: 'circle', areaStyle: { opacity: 0.1, color: '#f56c6c' } },
      { name: 'Major', type: 'line', data: data.major, smooth: true, lineStyle: { width: 2, color: '#e6a23c' }, symbol: 'diamond', areaStyle: { opacity: 0.1, color: '#e6a23c' } },
      { name: 'Minor', type: 'line', data: data.minor, smooth: true, lineStyle: { width: 2, color: '#409eff' }, symbol: 'triangle', areaStyle: { opacity: 0.1, color: '#409eff' } }
    ]
  })
}

const updateTrendChart = () => {
  if (trendChart) {
    const data = getTrendData()
    trendChart.setOption({
      xAxis: { data: data.xAxis },
      series: [
        { data: data.critical },
        { data: data.major },
        { data: data.minor }
      ]
    })
  }
}

const initCategoryChart = () => {
  if (!categoryChartRef.value) return
  if (categoryChart) categoryChart.dispose()

  categoryChart = echarts.init(categoryChartRef.value)
  categoryChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '12%', right: '5%', top: '5%', bottom: '5%', containLabel: true },
    xAxis: { type: 'value', name: 'Number of Faults' },
    yAxis: { type: 'category', data: ['HVAC', 'Electrical', 'DCIM', 'Security', 'Plumbing', 'Lighting', 'BMS', 'Fire Safety'] },
    series: [{
      type: 'bar', data: [32, 22, 15, 12, 10, 8, 6, 4],
      itemStyle: { borderRadius: [0, 4, 4, 0], color: '#409eff', label: { show: true, position: 'right', formatter: '{c}' } }
    }]
  })
}

const initSystemChart = () => {
  if (!systemChartRef.value) return
  if (systemChart) systemChart.dispose()

  systemChart = echarts.init(systemChartRef.value)
  systemChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} faults ({d}%)' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      type: 'pie', radius: '55%', center: ['50%', '50%'],
      data: [
        { name: 'AHU Systems', value: 18, itemStyle: { color: '#f56c6c' } },
        { name: 'Chillers', value: 14, itemStyle: { color: '#e6a23c' } },
        { name: 'UPS Systems', value: 10, itemStyle: { color: '#409eff' } },
        { name: 'FCU Network', value: 9, itemStyle: { color: '#67c23a' } },
        { name: 'Lighting Panels', value: 7, itemStyle: { color: '#8b5cf6' } },
        { name: 'VFDs', value: 6, itemStyle: { color: '#f59e0b' } },
        { name: 'Other', value: 5, itemStyle: { color: '#94a3b8' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 }
    }]
  })
}

const updateChartData = () => {
  initTrendChart()
}

// Actions
const refreshData = async () => {
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  ElMessage.success('Fault data refreshed')
  initTrendChart()
  initCategoryChart()
  initSystemChart()
  tableLoading.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting fault report...')
}

const viewFault = (row: Fault) => {
  ElMessage.info(`Viewing fault #${row.id}: ${row.title}`)
}

const assignFault = (row: Fault) => {
  ElMessage.info(`Assigning fault #${row.id} to technician`)
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// 确保DOM渲染完成后再初始化图表
const initCharts = () => {
  nextTick(() => {
    initTrendChart()
    initCategoryChart()
    initSystemChart()
  })
}

// Lifecycle
onMounted(() => {
  let idx = 0
  const msgInterval = setInterval(() => {
    if (idx < loadingMessages.length - 1) {
      idx++
      loadingMessage.value = loadingMessages[idx]
    }
  }, 400)
  const progInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)
  setTimeout(() => {
    clearInterval(msgInterval)
    clearInterval(progInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      initCharts()
      window.addEventListener('resize', () => {
        trendChart?.resize()
        categoryChart?.resize()
        systemChart?.resize()
      })
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  trendChart?.dispose()
  categoryChart?.dispose()
  systemChart?.dispose()
})
</script>

<style scoped>
/* Loading Screen - 保持不变 */
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

/* Main Content */
.fault-dashboard-page {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}
.title-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #ef4444, #dc2626);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  color: white;
  margin-bottom: 12px;
}
.header-title h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 8px 0;
}
.header-title .subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}
.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}
.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e2e8f0;
  background: white;
  color: #475569;
}
.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.action-btn.primary {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border: none;
  color: white;
}
.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
}
.time-range-select {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: white;
  font-size: 13px;
  cursor: pointer;
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}
.kpi-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
}
.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}
.kpi-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}
.kpi-icon.critical { background: #fee2e2; color: #dc2626; }
.kpi-icon.major { background: #fef3c7; color: #d97706; }
.kpi-icon.minor { background: #dbeafe; color: #2563eb; }
.kpi-icon.resolved { background: #d1fae5; color: #059669; }
.kpi-info { flex: 1; }
.kpi-value { font-size: 28px; font-weight: 700; color: #1a1a2e; }
.kpi-label { font-size: 13px; color: #64748b; margin-top: 4px; }
.kpi-trend { font-size: 12px; font-weight: 600; display: flex; align-items: center; gap: 2px; }
.kpi-trend.critical { color: #dc2626; }
.kpi-trend.major { color: #d97706; }
.kpi-trend.minor { color: #2563eb; }
.kpi-trend.resolved { color: #059669; }

/* Stats Row */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}
.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}
.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.stat-title { font-size: 14px; font-weight: 500; color: #64748b; }
.stat-header .el-icon { font-size: 20px; color: #94a3b8; }
.stat-value { font-size: 28px; font-weight: 700; color: #1a1a2e; }
.stat-unit { font-size: 14px; font-weight: 400; color: #94a3b8; margin-left: 4px; }
.stat-change { font-size: 12px; margin-top: 8px; padding-top: 8px; border-top: 1px solid #e2e8f0; }
.stat-change.positive { color: #10b981; }
.stat-change.negative { color: #ef4444; }

/* Chart Cards */
.chart-card, .table-card, .location-card {
  background: white;
  border-radius: 20px;
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
.card-header h3 { font-size: 16px; font-weight: 600; margin: 0; color: #1a1a2e; }
.chart-container { height: 350px; width: 100%; }
.two-columns { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }

/* Table Styles */
.filter-group { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
.filter-select, .search-input { padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 10px; font-size: 13px; background: white; cursor: pointer; }
.search-input { width: 200px; cursor: text; }
.pagination-wrapper { padding-top: 16px; display: flex; justify-content: flex-end; border-top: 1px solid #e2e8f0; margin-top: 16px; }

/* Location Distribution */
.location-grid { display: flex; flex-direction: column; gap: 16px; }
.location-item { padding: 16px; background: #f8fafc; border-radius: 12px; }
.location-name { font-weight: 600; color: #1a1a2e; margin-bottom: 8px; font-size: 14px; }
.location-stats { display: flex; gap: 16px; margin-bottom: 8px; font-size: 12px; }
.critical-count { color: #dc2626; font-weight: 600; }
.major-count { color: #d97706; font-weight: 600; }
.minor-count { color: #2563eb; font-weight: 600; }
.progress-bar-custom { display: flex; height: 8px; border-radius: 4px; overflow: hidden; margin-bottom: 8px; }
.progress-critical { background: #dc2626; }
.progress-major { background: #d97706; }
.progress-minor { background: #2563eb; }
.location-total { font-size: 12px; color: #64748b; }

:deep(.el-table) { border-radius: 12px; }
:deep(.el-table th) { background-color: #fafafa; font-weight: 600; }
:deep(.el-pagination) { margin-top: 16px; }
</style>