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

  <!-- Response Time Page Content -->
  <div v-else class="response-time-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>Response Time</h1>
        <p class="subtitle">Monitor system and incident response time performance across all operations</p>
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
      <div class="kpi-card avg-response">
        <div class="kpi-icon">
          <el-icon :size="32"><Timer /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ avgResponseTime }}</div>
          <div class="kpi-label">Avg Response Time</div>
        </div>
        <div class="kpi-trend" :class="avgTrend >= 0 ? 'positive' : 'negative'">
          <el-icon><CaretBottom v-if="avgTrend >= 0" /><CaretTop v-else /></el-icon>
          {{ Math.abs(avgTrend) }}
        </div>
      </div>
      <div class="kpi-card p95">
        <div class="kpi-icon">
          <el-icon :size="32"><DataLine /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ p95ResponseTime }}</div>
          <div class="kpi-label">P95 Response Time</div>
        </div>
        <div class="kpi-sub">95th Percentile</div>
      </div>
      <div class="kpi-card p99">
        <div class="kpi-icon">
          <el-icon :size="32"><TrendCharts /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ p99ResponseTime }}</div>
          <div class="kpi-label">P99 Response Time</div>
        </div>
        <div class="kpi-sub">99th Percentile</div>
      </div>
      <div class="kpi-card sla">
        <div class="kpi-icon">
          <el-icon :size="32"><Medal /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ slaAchievement }}%</div>
          <div class="kpi-label">SLA Achievement</div>
        </div>
        <div class="kpi-sub">Target: 95%</div>
      </div>
    </div>

    <!-- Response Time Trend Chart -->
    <div class="chart-card">
      <div class="card-header">
        <h3>Response Time Trend</h3>
        <el-radio-group v-model="trendPeriod" size="small" @change="fetchTrendData">
          <el-radio-button label="week">Last 7 Days</el-radio-button>
          <el-radio-button label="month">Last 30 Days</el-radio-button>
          <el-radio-button label="quarter">Last 90 Days</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-container" ref="trendChartRef"></div>
    </div>

    <!-- Response Time by Category -->
    <div class="two-columns">
      <div class="chart-card">
        <div class="card-header">
          <h3>Response Time by Category</h3>
        </div>
        <div class="chart-container" ref="categoryChartRef"></div>
      </div>
      <div class="chart-card">
        <div class="card-header">
          <h3>Response Time Distribution</h3>
        </div>
        <div class="chart-container" ref="distributionChartRef"></div>
      </div>
    </div>

    <!-- Incident Response Times Table -->
    <div class="table-card">
      <div class="card-header">
        <h3>Recent Incident Response Times</h3>
        <el-input
            v-model="searchText"
            placeholder="Search incidents..."
            :prefix-icon="Search"
            style="width: 260px"
            clearable
        />
      </div>
      <el-table :data="filteredIncidents" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="incidentId" label="Incident ID" width="120" />
        <el-table-column prop="title" label="Title" min-width="200" show-overflow-tooltip />
        <el-table-column prop="category" label="Category" width="140">
          <template #default="{ row }">
            <el-tag size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="Priority" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityTagType(row.priority)" size="small" effect="dark">
              {{ row.priority }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="responseTime" label="Response Time" width="130">
          <template #default="{ row }">
            <span :class="getResponseTimeClass(row.responseTime, row.targetTime)">
              {{ formatResponseTime(row.responseTime) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="targetTime" label="Target" width="100">
          <template #default="{ row }">
            {{ formatResponseTime(row.targetTime) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="row.responseTime <= row.targetTime ? 'success' : 'danger'" size="small">
              {{ row.responseTime <= row.targetTime ? 'Met' : 'Breached' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assignedTo" label="Assigned To" width="140" />
        <el-table-column prop="timestamp" label="Occurred" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.timestamp) }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewIncident(row)">View</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredIncidents.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Performance by Team -->
    <div class="teams-section">
      <div class="section-header">
        <h2>
          <el-icon><User /></el-icon>
          Team Response Performance
        </h2>
        <el-button link type="primary" @click="viewAllTeams">View All Teams →</el-button>
      </div>
      <div class="teams-grid">
        <div v-for="team in teamPerformance" :key="team.id" class="team-card">
          <div class="team-header">
            <div class="team-name">{{ team.name }}</div>
            <div class="team-badge" :class="getTeamStatusClass(team)">
              {{ getTeamStatus(team) }}
            </div>
          </div>
          <div class="team-stats">
            <div class="stat">
              <span class="stat-label">Avg Response</span>
              <span class="stat-value" :class="getTeamValueClass(team.avgResponse, team.target)">
                {{ team.avgResponse }}
              </span>
            </div>
            <div class="stat">
              <span class="stat-label">Target</span>
              <span class="stat-value">{{ team.target }}</span>
            </div>
            <div class="stat">
              <span class="stat-label">Incidents</span>
              <span class="stat-value">{{ team.incidentsHandled }}</span>
            </div>
            <div class="stat">
              <span class="stat-label">SLA Met</span>
              <span class="stat-value" :class="team.slaMet >= 95 ? 'text-success' : 'text-danger'">
                {{ team.slaMet }}%
              </span>
            </div>
          </div>
          <el-progress
              :percentage="team.slaMet"
              :color="team.slaMet >= 95 ? '#67c23a' : team.slaMet >= 85 ? '#e6a23c' : '#f56c6c'"
              :stroke-width="8"
              :show-text="false"
          />
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
  Timer,
  DataLine,
  TrendCharts,
  Medal,
  CaretTop,
  CaretBottom,
  Search,
  User
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
interface IncidentResponse {
  id: number
  incidentId: string
  title: string
  category: string
  priority: 'Critical' | 'High' | 'Medium' | 'Low'
  responseTime: number
  targetTime: number
  status: string
  assignedTo: string
  timestamp: string
}

interface TeamPerformance {
  id: number
  name: string
  avgResponse: string
  target: string
  incidentsHandled: number
  slaMet: number
}

// ==================== State ====================
const dateRange = ref<[Date, Date] | null>(null)
const trendPeriod = ref<'week' | 'month' | 'quarter'>('month')
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const trendChartRef = ref<HTMLElement | null>(null)
const categoryChartRef = ref<HTMLElement | null>(null)
const distributionChartRef = ref<HTMLElement | null>(null)
let trendChart: echarts.ECharts | null = null
let categoryChart: echarts.ECharts | null = null
let distributionChart: echarts.ECharts | null = null

// ==================== Mock Data ====================
const incidents = ref<IncidentResponse[]>([
  { id: 1, incidentId: 'INC-001', title: 'AHU-101 Complete Failure', category: 'HVAC', priority: 'Critical', responseTime: 4.5, targetTime: 15, status: 'Resolved', assignedTo: 'Mike Johnson', timestamp: '2025-01-28 09:15:00' },
  { id: 2, incidentId: 'INC-002', title: 'Chiller High Temperature Alarm', category: 'HVAC', priority: 'High', responseTime: 8.2, targetTime: 30, status: 'Resolved', assignedTo: 'Sarah Chen', timestamp: '2025-01-28 11:30:00' },
  { id: 3, incidentId: 'INC-003', title: 'UPS Battery Low Warning', category: 'Electrical', priority: 'Critical', responseTime: 3.8, targetTime: 15, status: 'Resolved', assignedTo: 'John Smith', timestamp: '2025-01-28 14:20:00' },
  { id: 4, incidentId: 'INC-004', title: 'Lighting Control Panel Offline', category: 'Lighting', priority: 'Medium', responseTime: 25.5, targetTime: 60, status: 'Resolved', assignedTo: 'Lisa Wong', timestamp: '2025-01-28 16:45:00' },
  { id: 5, incidentId: 'INC-005', title: 'Access Control Door Malfunction', category: 'Security', priority: 'High', responseTime: 12.3, targetTime: 30, status: 'In Progress', assignedTo: 'Mike Johnson', timestamp: '2025-01-29 08:00:00' },
  { id: 6, incidentId: 'INC-006', title: 'Server Room Temperature Spike', category: 'DCIM', priority: 'Critical', responseTime: 2.1, targetTime: 15, status: 'Resolved', assignedTo: 'John Smith', timestamp: '2025-01-29 09:30:00' },
  { id: 7, incidentId: 'INC-007', title: 'CCTV Camera Feed Loss', category: 'Security', priority: 'Medium', responseTime: 18.7, targetTime: 60, status: 'Resolved', assignedTo: 'Sarah Chen', timestamp: '2025-01-29 10:15:00' },
  { id: 8, incidentId: 'INC-008', title: 'Water Leak Detection Alert', category: 'Plumbing', priority: 'Critical', responseTime: 5.2, targetTime: 15, status: 'Resolved', assignedTo: 'Mike Johnson', timestamp: '2025-01-29 13:00:00' },
  { id: 9, incidentId: 'INC-009', title: 'BMS Controller Communication Error', category: 'BMS', priority: 'High', responseTime: 9.5, targetTime: 30, status: 'Resolved', assignedTo: 'Lisa Wong', timestamp: '2025-01-29 15:30:00' },
  { id: 10, incidentId: 'INC-010', title: 'FCU Network Intermittent', category: 'HVAC', priority: 'Medium', responseTime: 35.2, targetTime: 60, status: 'In Progress', assignedTo: 'Sarah Chen', timestamp: '2025-01-30 08:45:00' },
  { id: 11, incidentId: 'INC-011', title: 'Power Quality Issue Detected', category: 'Electrical', priority: 'High', responseTime: 14.8, targetTime: 30, status: 'Resolved', assignedTo: 'John Smith', timestamp: '2025-01-30 10:00:00' },
  { id: 12, incidentId: 'INC-012', title: 'Fire Alarm False Trigger', category: 'Fire Safety', priority: 'High', responseTime: 7.5, targetTime: 30, status: 'Resolved', assignedTo: 'Mike Johnson', timestamp: '2025-01-30 12:15:00' },
  { id: 13, incidentId: 'INC-013', title: 'VAV Box Stuck Position', category: 'HVAC', priority: 'Medium', responseTime: 42.0, targetTime: 60, status: 'In Progress', assignedTo: 'Lisa Wong', timestamp: '2025-01-30 14:30:00' },
  { id: 14, incidentId: 'INC-014', title: 'Generator Fuel Low', category: 'Electrical', priority: 'Critical', responseTime: 4.2, targetTime: 15, status: 'Resolved', assignedTo: 'John Smith', timestamp: '2025-01-31 09:00:00' },
  { id: 15, incidentId: 'INC-015', title: 'Temperature Sensor Calibration', category: 'BMS', priority: 'Low', responseTime: 55.0, targetTime: 120, status: 'Resolved', assignedTo: 'Sarah Chen', timestamp: '2025-01-31 11:00:00' }
])

const teamPerformance = ref<TeamPerformance[]>([
  { id: 1, name: 'HVAC Team', avgResponse: '8.5 min', target: '15 min', incidentsHandled: 124, slaMet: 96 },
  { id: 2, name: 'Electrical Team', avgResponse: '6.2 min', target: '15 min', incidentsHandled: 89, slaMet: 98 },
  { id: 3, name: 'Security Team', avgResponse: '14.8 min', target: '30 min', incidentsHandled: 67, slaMet: 94 },
  { id: 4, name: 'BMS Team', avgResponse: '12.3 min', target: '30 min', incidentsHandled: 56, slaMet: 95 },
  { id: 5, name: 'Data Center Team', avgResponse: '5.8 min', target: '15 min', incidentsHandled: 78, slaMet: 97 }
])

// ==================== Computed Values ====================
const avgResponseTime = computed(() => {
  const total = incidents.value.reduce((sum, i) => sum + i.responseTime, 0)
  const avg = total / incidents.value.length
  return `${avg.toFixed(1)} min`
})

const p95ResponseTime = computed(() => {
  const times = [...incidents.value.map(i => i.responseTime)].sort((a, b) => a - b)
  const index = Math.floor(times.length * 0.95)
  return `${times[index].toFixed(1)} min`
})

const p99ResponseTime = computed(() => {
  const times = [...incidents.value.map(i => i.responseTime)].sort((a, b) => a - b)
  const index = Math.floor(times.length * 0.99)
  return `${times[index].toFixed(1)} min`
})

const slaAchievement = computed(() => {
  const met = incidents.value.filter(i => i.responseTime <= i.targetTime).length
  return ((met / incidents.value.length) * 100).toFixed(1)
})

const avgTrend = computed(() => -0.8)

const filteredIncidents = computed(() => {
  let result = [...incidents.value]
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(i =>
        i.incidentId.toLowerCase().includes(search) ||
        i.title.toLowerCase().includes(search) ||
        i.category.toLowerCase().includes(search) ||
        i.assignedTo.toLowerCase().includes(search)
    )
  }
  if (dateRange.value && dateRange.value[0] && dateRange.value[1]) {
    const [start, end] = dateRange.value
    result = result.filter(i => {
      const date = new Date(i.timestamp)
      return date >= start && date <= end
    })
  }
  return result
})

// ==================== Helper Functions ====================
const formatResponseTime = (minutes: number) => {
  if (minutes < 60) return `${minutes.toFixed(1)} min`
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return `${hours}h ${mins.toFixed(0)}m`
}

const formatDateTime = (dateStr: string) => {
  return dateStr
}

const getPriorityTagType = (priority: string) => {
  const map: Record<string, string> = {
    Critical: 'danger',
    High: 'warning',
    Medium: 'primary',
    Low: 'info'
  }
  return map[priority] || 'info'
}

const getResponseTimeClass = (response: number, target: number) => {
  return response <= target ? 'text-success' : 'text-danger'
}

const getTeamStatusClass = (team: TeamPerformance) => {
  if (team.slaMet >= 95) return 'status-excellent'
  if (team.slaMet >= 85) return 'status-good'
  return 'status-poor'
}

const getTeamStatus = (team: TeamPerformance) => {
  if (team.slaMet >= 95) return 'Excellent'
  if (team.slaMet >= 85) return 'Good'
  return 'Needs Improvement'
}

const getTeamValueClass = (value: string, target: string) => {
  const valNum = parseInt(value)
  const targetNum = parseInt(target)
  return valNum <= targetNum ? 'text-success' : 'text-danger'
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
  const avgTimes: number[] = []
  const p95Times: number[] = []
  const targetLine: number[] = []

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    dates.push(`${date.getMonth() + 1}/${date.getDate()}`)

    const baseAvg = 12 + Math.sin(i * 0.3) * 3 + Math.random() * 2
    const baseP95 = 18 + Math.cos(i * 0.25) * 4 + Math.random() * 2

    avgTimes.push(Number(baseAvg.toFixed(1)))
    p95Times.push(Number(baseP95.toFixed(1)))
    targetLine.push(15)
  }

  return { dates, avgTimes, p95Times, targetLine }
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)
  const data = generateTrendData()

  trendChart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: (value: number) => value + ' min' },
    legend: { data: ['Avg Response Time', 'P95 Response Time', 'SLA Target (15 min)'], bottom: 0 },
    grid: { left: '3%', right: '4%', top: '10%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: data.dates },
    yAxis: { type: 'value', name: 'Response Time (minutes)', axisLabel: { formatter: '{value} min' } },
    series: [
      {
        name: 'Avg Response Time', type: 'line', data: data.avgTimes, smooth: true, symbol: 'circle',
        lineStyle: { width: 3, color: '#409eff' }, areaStyle: { opacity: 0.1, color: '#409eff' }
      },
      {
        name: 'P95 Response Time', type: 'line', data: data.p95Times, smooth: true, symbol: 'diamond',
        lineStyle: { width: 2, color: '#e6a23c' }
      },
      {
        name: 'SLA Target (15 min)', type: 'line', data: data.targetLine, smooth: false, symbol: 'none',
        lineStyle: { width: 2, color: '#f56c6c', type: 'dashed' }
      }
    ]
  })
}

const initCategoryChart = () => {
  if (!categoryChartRef.value) return
  if (categoryChart) categoryChart.dispose()

  categoryChart = echarts.init(categoryChartRef.value)

  const categories = ['HVAC', 'Electrical', 'Security', 'BMS', 'DCIM', 'Plumbing', 'Fire Safety', 'Lighting']
  const avgTimes = [12.5, 8.2, 15.8, 11.3, 6.5, 14.2, 9.8, 28.5]
  const targetTimes = categories.map(() => 15)

  categoryChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: (value: number) => value + ' min' },
    legend: { data: ['Avg Response Time', 'Target (15 min)'], bottom: 0 },
    grid: { left: '10%', right: '5%', top: '5%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: categories, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: 'Response Time (minutes)', axisLabel: { formatter: '{value} min' } },
    series: [
      {
        name: 'Avg Response Time', type: 'bar', data: avgTimes,
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
          color: (params: any) => {
            const value = params.data
            if (value <= 15) return '#67c23a'
            if (value <= 30) return '#e6a23c'
            return '#f56c6c'
          }
        },
        label: { show: true, position: 'top', formatter: '{c} min', fontSize: 10 }
      },
      {
        name: 'Target (15 min)', type: 'line', data: targetTimes, symbol: 'none',
        lineStyle: { width: 2, color: '#f56c6c', type: 'dashed' }
      }
    ]
  })
}

const initDistributionChart = () => {
  if (!distributionChartRef.value) return
  if (distributionChart) distributionChart.dispose()

  distributionChart = echarts.init(distributionChartRef.value)

  const ranges = ['0-5 min', '5-10 min', '10-15 min', '15-30 min', '30-60 min', '60+ min']
  const counts = [12, 28, 35, 42, 18, 5]

  distributionChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}: {c} incidents' },
    grid: { left: '10%', right: '5%', top: '5%', bottom: '5%', containLabel: true },
    xAxis: { type: 'category', data: ranges, axisLabel: { rotate: 15 } },
    yAxis: { type: 'value', name: 'Number of Incidents' },
    series: [{
      type: 'bar', data: counts,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const range = params.name
          if (range === '0-5 min' || range === '5-10 min' || range === '10-15 min') return '#67c23a'
          if (range === '15-30 min') return '#e6a23c'
          return '#f56c6c'
        }
      },
      label: { show: true, position: 'top', formatter: '{c}' }
    }]
  })
}

// ==================== Actions ====================
const refreshData = async () => {
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  ElMessage.success('Response time data refreshed')
  initTrendChart()
  initCategoryChart()
  initDistributionChart()
  tableLoading.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting response time report...')
}

const fetchTrendData = () => {
  initTrendChart()
}

const handleDateChange = () => {
  currentPage.value = 1
}

const viewIncident = (incident: IncidentResponse) => {
  ElMessage.info(`Viewing incident: ${incident.incidentId}`)
}

const viewAllTeams = () => {
  ElMessage.info('Viewing all teams performance')
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Window Resize Handler ====================
const handleResize = () => {
  trendChart?.resize()
  categoryChart?.resize()
  distributionChart?.resize()
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
        initCategoryChart()
        initDistributionChart()
      }, 100)
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  categoryChart?.dispose()
  distributionChart?.dispose()
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
.response-time-page {
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

.kpi-card.avg-response .kpi-icon { background: #e8f4ff; color: #409eff; }
.kpi-card.p95 .kpi-icon { background: #fff7e8; color: #e6a23c; }
.kpi-card.p99 .kpi-icon { background: #ffe8e8; color: #f56c6c; }
.kpi-card.sla .kpi-icon { background: #e8f8f0; color: #67c23a; }

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
  height: 320px;
  width: 100%;
}

.two-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

/* Table Styles */
.text-success {
  color: #67c23a;
  font-weight: 500;
}

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

/* Teams Section */
.teams-section {
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

.teams-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.team-card {
  background: #fafafa;
  border-radius: 14px;
  padding: 16px;
  transition: all 0.2s;
}

.team-card:hover {
  background: #f5f7fa;
  transform: translateY(-2px);
}

.team-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.team-name {
  font-weight: 600;
  font-size: 16px;
  color: #1f2f3d;
}

.team-badge {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 20px;
  font-weight: 500;
}

.team-badge.status-excellent {
  background: #e8f8f0;
  color: #67c23a;
}

.team-badge.status-good {
  background: #fff7e8;
  color: #e6a23c;
}

.team-badge.status-poor {
  background: #ffe8e8;
  color: #f56c6c;
}

.team-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.stat {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 11px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-value {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
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