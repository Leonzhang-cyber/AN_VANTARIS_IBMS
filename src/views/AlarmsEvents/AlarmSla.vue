<template>
  <!-- Loading Screen -->
  <div v-if="!isLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
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
        <div class="loading-tip">Alarm SLA Dashboard</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="alarm-sla-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-left">
        <h1 class="dashboard-title">
          <el-icon><Timer /></el-icon>
          Alarm SLA Dashboard
        </h1>
        <div class="header-stats">
          <div class="stat-badge">
            <el-icon><Calendar /></el-icon>
            {{ currentPeriod }}
          </div>
          <div class="stat-badge">
            <el-icon><TrendCharts /></el-icon>
            {{ totalAlarms }} Total Alarms
          </div>
        </div>
      </div>
      <div class="header-right">
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            :shortcuts="dateShortcuts"
            size="default"
            style="width: 280px"
        />
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
        <el-button type="primary" @click="exportReport">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
      </div>
    </div>

    <!-- Overall SLA Score -->
    <div class="sla-score-card">
      <div class="sla-score-content">
        <div class="sla-score-gauge">
          <el-progress
              type="circle"
              :percentage="overallSlaScore"
              :color="slaScoreColor"
              :width="140"
              :stroke-width="12"
          >
            <template #default>
              <div class="sla-score-text">
                <span class="sla-score-value">{{ overallSlaScore }}</span>
                <span class="sla-score-unit">%</span>
              </div>
            </template>
          </el-progress>
          <div class="sla-score-label">Overall SLA Compliance</div>
          <div class="sla-score-status" :class="slaScoreClass">
            {{ slaScoreStatus }}
          </div>
        </div>
        <div class="sla-score-metrics">
          <div class="sla-metric">
            <div class="metric-value">{{ slaMetAlarms }}</div>
            <div class="metric-label">SLA Met</div>
          </div>
          <div class="sla-metric">
            <div class="metric-value">{{ slaBreachedAlarms }}</div>
            <div class="metric-label">SLA Breached</div>
          </div>
          <div class="sla-metric">
            <div class="metric-value">{{ avgResponseTime }}<span class="unit">min</span></div>
            <div class="metric-label">Avg Response Time</div>
          </div>
          <div class="sla-metric">
            <div class="metric-value">{{ avgResolutionTime }}<span class="unit">min</span></div>
            <div class="metric-label">Avg Resolution Time</div>
          </div>
        </div>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="kpi-grid">
      <div class="kpi-card critical">
        <div class="kpi-header">
          <span class="kpi-title">Critical</span>
          <span class="kpi-target">Target: 5 min / 30 min</span>
        </div>
        <div class="kpi-body">
          <div class="kpi-sla-score">
            <el-progress type="circle" :percentage="criticalSlaScore" :color="getSlaScoreColor(criticalSlaScore)" :width="80" :stroke-width="8">
              <template #default>{{ criticalSlaScore }}%</template>
            </el-progress>
          </div>
          <div class="kpi-stats">
            <div class="stat-row">
              <span>Total:</span>
              <strong>{{ criticalTotal }}</strong>
            </div>
            <div class="stat-row">
              <span>Met:</span>
              <strong class="success">{{ criticalMet }}</strong>
            </div>
            <div class="stat-row">
              <span>Breached:</span>
              <strong class="danger">{{ criticalBreached }}</strong>
            </div>
            <div class="stat-row">
              <span>Avg Response:</span>
              <strong>{{ criticalAvgResponse }} min</strong>
            </div>
          </div>
        </div>
      </div>

      <div class="kpi-card major">
        <div class="kpi-header">
          <span class="kpi-title">Major</span>
          <span class="kpi-target">Target: 15 min / 2 hr</span>
        </div>
        <div class="kpi-body">
          <div class="kpi-sla-score">
            <el-progress type="circle" :percentage="majorSlaScore" :color="getSlaScoreColor(majorSlaScore)" :width="80" :stroke-width="8">
              <template #default>{{ majorSlaScore }}%</template>
            </el-progress>
          </div>
          <div class="kpi-stats">
            <div class="stat-row"><span>Total:</span><strong>{{ majorTotal }}</strong></div>
            <div class="stat-row"><span>Met:</span><strong class="success">{{ majorMet }}</strong></div>
            <div class="stat-row"><span>Breached:</span><strong class="danger">{{ majorBreached }}</strong></div>
            <div class="stat-row"><span>Avg Response:</span><strong>{{ majorAvgResponse }} min</strong></div>
          </div>
        </div>
      </div>

      <div class="kpi-card warning">
        <div class="kpi-header">
          <span class="kpi-title">Warning</span>
          <span class="kpi-target">Target: 1 hr / 8 hr</span>
        </div>
        <div class="kpi-body">
          <div class="kpi-sla-score">
            <el-progress type="circle" :percentage="warningSlaScore" :color="getSlaScoreColor(warningSlaScore)" :width="80" :stroke-width="8">
              <template #default>{{ warningSlaScore }}%</template>
            </el-progress>
          </div>
          <div class="kpi-stats">
            <div class="stat-row"><span>Total:</span><strong>{{ warningTotal }}</strong></div>
            <div class="stat-row"><span>Met:</span><strong class="success">{{ warningMet }}</strong></div>
            <div class="stat-row"><span>Breached:</span><strong class="danger">{{ warningBreached }}</strong></div>
            <div class="stat-row"><span>Avg Response:</span><strong>{{ warningAvgResponse }} min</strong></div>
          </div>
        </div>
      </div>

      <div class="kpi-card info">
        <div class="kpi-header">
          <span class="kpi-title">Info</span>
          <span class="kpi-target">Target: 4 hr / 24 hr</span>
        </div>
        <div class="kpi-body">
          <div class="kpi-sla-score">
            <el-progress type="circle" :percentage="infoSlaScore" :color="getSlaScoreColor(infoSlaScore)" :width="80" :stroke-width="8">
              <template #default>{{ infoSlaScore }}%</template>
            </el-progress>
          </div>
          <div class="kpi-stats">
            <div class="stat-row"><span>Total:</span><strong>{{ infoTotal }}</strong></div>
            <div class="stat-row"><span>Met:</span><strong class="success">{{ infoMet }}</strong></div>
            <div class="stat-row"><span>Breached:</span><strong class="danger">{{ infoBreached }}</strong></div>
            <div class="stat-row"><span>Avg Response:</span><strong>{{ infoAvgResponse }} min</strong></div>
          </div>
        </div>
      </div>
    </div>

    <!-- SLA Trend Chart -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><TrendCharts /></el-icon>
          SLA Compliance Trend (Last 30 Days)
        </div>
        <el-radio-group v-model="trendPeriod" size="small" @change="updateTrendChart">
          <el-radio-button label="week">Weekly</el-radio-button>
          <el-radio-button label="month">Monthly</el-radio-button>
        </el-radio-group>
      </div>
      <div ref="trendChartRef" class="chart-container"></div>
    </div>

    <!-- Breach Analysis -->
    <div class="two-columns">
      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <el-icon><PieChart /></el-icon>
            Breach by Severity
          </div>
        </div>
        <div ref="breachChartRef" class="chart-container-small"></div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <el-icon><List /></el-icon>
            Top Breach Reasons
          </div>
        </div>
        <div class="breach-reasons">
          <div v-for="reason in breachReasons" :key="reason.name" class="reason-item">
            <div class="reason-info">
              <span class="reason-name">{{ reason.name }}</span>
              <span class="reason-count">{{ reason.count }}</span>
            </div>
            <el-progress :percentage="reason.percent" :color="'#f56c6c'" :stroke-width="6" :show-text="false" />
          </div>
        </div>
      </div>
    </div>

    <!-- SLA Exceeded Alarms Table -->
    <div class="card table-card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><WarningFilled /></el-icon>
          SLA Breached Alarms
        </div>
        <div class="table-controls">
          <el-input v-model="searchText" placeholder="Search..." size="small" style="width: 200px" clearable>
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-select v-model="severityFilter" placeholder="Severity" size="small" style="width: 120px" clearable>
            <el-option label="All" value="all" />
            <el-option label="Critical" value="critical" />
            <el-option label="Major" value="major" />
            <el-option label="Warning" value="warning" />
          </el-select>
        </div>
      </div>
      <el-table :data="paginatedBreachedAlarms" stripe border style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="time" label="Time" width="160" sortable />
        <el-table-column prop="title" label="Alarm Title" min-width="200" />
        <el-table-column prop="severity" label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityTag(row.severity)" size="small">{{ row.severity.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="targetResponse" label="Target Response" width="120" />
        <el-table-column prop="actualResponse" label="Actual Response" width="120" sortable>
          <template #default="{ row }">
            <span class="breached-value">{{ row.actualResponse }} min</span>
          </template>
        </el-table-column>
        <el-table-column prop="overBy" label="Over By" width="100" sortable>
          <template #default="{ row }">
            <span class="breached-value">+{{ row.overBy }} min</span>
          </template>
        </el-table-column>
        <el-table-column prop="assignedTo" label="Assigned To" width="120" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Resolved' ? 'success' : 'warning'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="80">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetails(row)">
              Details
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="card-footer">
        <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="filteredBreachedAlarms.length"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handlePageSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`SLA Breach Details - ${selectedAlarm?.title}`" width="550px">
      <el-descriptions :column="2" border v-if="selectedAlarm">
        <el-descriptions-item label="Alarm ID">{{ selectedAlarm.id }}</el-descriptions-item>
        <el-descriptions-item label="Severity">
          <el-tag :type="getSeverityTag(selectedAlarm.severity)">{{ selectedAlarm.severity.toUpperCase() }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Title" :span="2">{{ selectedAlarm.title }}</el-descriptions-item>
        <el-descriptions-item label="Occurred At">{{ selectedAlarm.time }}</el-descriptions-item>
        <el-descriptions-item label="Target Response">{{ selectedAlarm.targetResponse }}</el-descriptions-item>
        <el-descriptions-item label="Actual Response">{{ selectedAlarm.actualResponse }} min</el-descriptions-item>
        <el-descriptions-item label="Over By">{{ selectedAlarm.overBy }} min</el-descriptions-item>
        <el-descriptions-item label="Assigned To">{{ selectedAlarm.assignedTo }}</el-descriptions-item>
        <el-descriptions-item label="Root Cause">{{ selectedAlarm.rootCause || '-' }}</el-descriptions-item>
        <el-descriptions-item label="Action Taken">{{ selectedAlarm.actionTaken || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { Timer, Calendar, TrendCharts, Refresh, Download, PieChart, List, WarningFilled, Search } from '@element-plus/icons-vue'
import { useCounterStore } from '@/stores/counter.js'
import { getCurrentInstance } from 'vue'

const getStore = () => {
  const instance = getCurrentInstance()
  if (!instance) throw new Error('useStore() must be called within a setup function')
  const pinia = instance.appContext.config.globalProperties.$pinia
  if (!pinia) throw new Error('Pinia instance not found')
  return useCounterStore(pinia)
}
const counterStore = getStore()
const isFullscreen = computed(() => counterStore.isFullscreen)
const route = useRoute()

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading SLA data...',
  'Calculating compliance...',
  'Building dashboard...',
  'Almost ready...'
]

// ==================== Data State ====================
const dateRange = ref<[Date, Date] | null>(null)
const searchText = ref('')
const severityFilter = ref('all')
const trendPeriod = ref('month')
const detailDialogVisible = ref(false)
const selectedAlarm = ref<any>(null)

const pagination = ref({ page: 1, pageSize: 10 })

const dateShortcuts = [
  { text: 'Last 7 days', value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 7 * 24 * 60 * 60 * 1000)
      return [start, end]
    }},
  { text: 'Last 30 days', value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 30 * 24 * 60 * 60 * 1000)
      return [start, end]
    }},
  { text: 'This Month', value: () => {
      const now = new Date()
      const start = new Date(now.getFullYear(), now.getMonth(), 1)
      const end = new Date(now.getFullYear(), now.getMonth() + 1, 0)
      return [start, end]
    }}
]

const currentPeriod = computed(() => {
  if (dateRange.value && dateRange.value[0] && dateRange.value[1]) {
    return `${dateRange.value[0].toLocaleDateString()} - ${dateRange.value[1].toLocaleDateString()}`
  }
  return 'Last 30 Days'
})

// SLA Data
const totalAlarms = ref(1247)
const slaMetAlarms = ref(1052)
const slaBreachedAlarms = ref(195)
const avgResponseTime = ref(8.5)
const avgResolutionTime = ref(32)

// Critical SLA
const criticalTotal = ref(156)
const criticalMet = ref(142)
const criticalBreached = ref(14)
const criticalAvgResponse = ref(4.2)
const criticalSlaScore = computed(() => Math.round((criticalMet.value / criticalTotal.value) * 100))

// Major SLA
const majorTotal = ref(289)
const majorMet = ref(258)
const majorBreached = ref(31)
const majorAvgResponse = ref(12.5)
const majorSlaScore = computed(() => Math.round((majorMet.value / majorTotal.value) * 100))

// Warning SLA
const warningTotal = ref(423)
const warningMet = ref(385)
const warningBreached = ref(38)
const warningAvgResponse = ref(48)
const warningSlaScore = computed(() => Math.round((warningMet.value / warningTotal.value) * 100))

// Info SLA
const infoTotal = ref(379)
const infoMet = ref(267)
const infoBreached = ref(112)
const infoAvgResponse = ref(210)
const infoSlaScore = computed(() => Math.round((infoMet.value / infoTotal.value) * 100))

// Overall SLA
const overallSlaScore = computed(() => Math.round((slaMetAlarms.value / totalAlarms.value) * 100))
const slaScoreColor = computed(() => {
  const score = overallSlaScore.value
  if (score >= 90) return '#67c23a'
  if (score >= 75) return '#e6a23c'
  return '#f56c6c'
})
const slaScoreClass = computed(() => {
  const score = overallSlaScore.value
  if (score >= 90) return 'excellent'
  if (score >= 75) return 'good'
  if (score >= 60) return 'fair'
  return 'poor'
})
const slaScoreStatus = computed(() => {
  const score = overallSlaScore.value
  if (score >= 90) return 'Excellent'
  if (score >= 75) return 'Good'
  if (score >= 60) return 'Fair'
  return 'Critical'
})

const getSlaScoreColor = (score: number) => {
  if (score >= 90) return '#67c23a'
  if (score >= 75) return '#e6a23c'
  return '#f56c6c'
}

// Breach Reasons
const breachReasons = ref([
  { name: 'Understaffed / Shift Change', count: 48, percent: 24.6 },
  { name: 'Complex Issue Requiring Escalation', count: 35, percent: 17.9 },
  { name: 'Missing Runbook / Documentation', count: 28, percent: 14.4 },
  { name: 'Tool / System Issue', count: 22, percent: 11.3 },
  { name: 'Third Party Dependency', count: 18, percent: 9.2 },
  { name: 'Incorrect Severity Assignment', count: 15, percent: 7.7 },
  { name: 'Other', count: 29, percent: 14.9 }
])

// Breached Alarms Data
interface BreachedAlarm {
  id: number
  time: string
  title: string
  severity: string
  targetResponse: string
  actualResponse: number
  overBy: number
  assignedTo: string
  status: string
  rootCause: string
  actionTaken: string
}

const breachedAlarms = ref<BreachedAlarm[]>([
  { id: 1, time: '2024-06-03 08:23:15', title: 'UPS Overload - Critical', severity: 'critical', targetResponse: '5 min', actualResponse: 12, overBy: 7, assignedTo: 'John Doe', status: 'Resolved', rootCause: 'Team was in meeting', actionTaken: 'Escalated to backup' },
  { id: 2, time: '2024-06-03 09:45:22', title: 'Temperature Critical', severity: 'critical', targetResponse: '5 min', actualResponse: 8, overBy: 3, assignedTo: 'Sarah Chen', status: 'Resolved', rootCause: 'Delayed notification', actionTaken: 'Adjusted alert routing' },
  { id: 3, time: '2024-06-02 14:30:10', title: 'High CPU Usage', severity: 'major', targetResponse: '15 min', actualResponse: 22, overBy: 7, assignedTo: 'Mike Lim', status: 'Resolved', rootCause: 'Investigation took longer', actionTaken: 'Added runbook' },
  { id: 4, time: '2024-06-02 16:20:45', title: 'Network Latency Spike', severity: 'major', targetResponse: '15 min', actualResponse: 18, overBy: 3, assignedTo: 'David Wong', status: 'Resolved', rootCause: 'Required escalation', actionTaken: 'Updated escalation policy' },
  { id: 5, time: '2024-06-01 22:15:30', title: 'Disk Space Warning', severity: 'warning', targetResponse: '1 hr', actualResponse: 95, overBy: 35, assignedTo: 'Lisa Tan', status: 'Resolved', rootCause: 'Night shift understaffed', actionTaken: 'Added night shift rotation' },
  { id: 6, time: '2024-06-01 11:00:00', title: 'Memory High Usage', severity: 'warning', targetResponse: '1 hr', actualResponse: 85, overBy: 25, assignedTo: 'James Lee', status: 'Pending', rootCause: 'Complex root cause', actionTaken: 'Pending analysis' }
])

const filteredBreachedAlarms = computed(() => {
  let filtered = breachedAlarms.value

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(a => a.title.toLowerCase().includes(search))
  }

  if (severityFilter.value !== 'all') {
    filtered = filtered.filter(a => a.severity === severityFilter.value)
  }

  return filtered
})

const paginatedBreachedAlarms = computed(() => {
  const start = (pagination.value.page - 1) * pagination.value.pageSize
  return filteredBreachedAlarms.value.slice(start, start + pagination.value.pageSize)
})

// Trend data
const weeklySlaData = ref<number[]>([92, 88, 94, 86, 90, 85, 82])
const monthlySlaData = ref<number[]>([90, 87, 85, 84])
const weekLabels = ref<string[]>(['Week 1', 'Week 2', 'Week 3', 'Week 4'])
const monthLabels = ref<string[]>(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'])

// ==================== Chart Refs ====================
const trendChartRef = ref<HTMLElement>()
const breachChartRef = ref<HTMLElement>()

let trendChart: echarts.ECharts | null = null
let breachChart: echarts.ECharts | null = null

const initCharts = () => {
  nextTick(() => {
    // Trend Chart
    if (trendChartRef.value) {
      if (trendChart) trendChart.dispose()
      trendChart = echarts.init(trendChartRef.value)
      updateTrendChart()
    }

    // Breach Chart
    if (breachChartRef.value) {
      if (breachChart) breachChart.dispose()
      breachChart = echarts.init(breachChartRef.value)
      breachChart.setOption({
        backgroundColor: 'transparent',
        tooltip: { trigger: 'item' },
        legend: { orient: 'vertical', left: 'left', textStyle: { color: '#606266' } },
        series: [{
          type: 'pie', radius: '55%', center: ['50%', '50%'],
          data: [
            { value: criticalBreached.value, name: 'Critical', itemStyle: { color: '#f56c6c' } },
            { value: majorBreached.value, name: 'Major', itemStyle: { color: '#e6a23c' } },
            { value: warningBreached.value, name: 'Warning', itemStyle: { color: '#fbbf24' } },
            { value: infoBreached.value, name: 'Info', itemStyle: { color: '#409eff' } }
          ],
          label: { show: true, formatter: '{b}: {d}%', color: '#606266' }
        }]
      })
    }

    window.addEventListener('resize', handleResize)
  })
}

const updateTrendChart = () => {
  if (!trendChart) return

  let data: number[]
  let labels: string[]

  if (trendPeriod.value === 'week') {
    labels = weekLabels.value
    data = weeklySlaData.value
  } else {
    labels = monthLabels.value
    data = monthlySlaData.value
  }

  trendChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: '8%', right: '5%', top: '10%', bottom: '5%', containLabel: true },
    xAxis: { type: 'category', data: labels, axisLabel: { color: '#606266' }, axisLine: { lineStyle: { color: '#dcdfe6' } } },
    yAxis: { type: 'value', name: 'SLA Compliance (%)', min: 70, max: 100, axisLabel: { color: '#606266', formatter: '{value}%' }, splitLine: { lineStyle: { color: '#ebeef5' } } },
    series: [{
      type: 'line', data: data, smooth: true,
      lineStyle: { color: '#409eff', width: 3 },
      areaStyle: { opacity: 0.1, color: '#409eff' },
      symbol: 'circle', symbolSize: 8, itemStyle: { color: '#409eff' },
      label: { show: true, position: 'top', formatter: '{c}%', color: '#409eff' }
    }]
  })
}

const handleResize = () => {
  trendChart?.resize()
  breachChart?.resize()
}

// ==================== Helper Functions ====================
const getSeverityTag = (severity: string) => {
  const map: Record<string, string> = {
    critical: 'danger',
    major: 'warning',
    warning: 'warning',
    info: 'info'
  }
  return map[severity] || 'info'
}

const viewDetails = (alarm: BreachedAlarm) => {
  selectedAlarm.value = alarm
  detailDialogVisible.value = true
}

const exportReport = () => {
  ElMessage.success('Exporting SLA report...')
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  tableLoading.value = false
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

const handlePageSizeChange = () => { pagination.value.page = 1 }
const handlePageChange = () => {}

// ==================== Loading Animation ====================
const startLoading = () => {
  let progress = 0
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 12
      loadingProgress.value = Math.min(progress, 90)
    }
  }, 100)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => {
        setTimeout(() => {
          initCharts()
        }, 100)
      })
    }, 500)
  }, 2500)
}

watch(trendPeriod, () => {
  updateTrendChart()
})

// ==================== Lifecycle ====================
onMounted(() => {
  startLoading()
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
.spinner-ring:nth-child(4) { border-left-color: #ec489a; animation-delay: 0.6s; width: 20%; height: 20%; top: 40%; left: 40%; }

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

/* ==================== Main Dashboard Styles ==================== */
.alarm-sla-dashboard {
  min-height: 100vh;
  background: #ffffff;
  padding: 24px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.dashboard-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 600;
  color: #1f2f3d;
  margin: 0;
}

.dashboard-title .el-icon {
  color: #409eff;
}

.header-stats {
  display: flex;
  gap: 16px;
  margin-top: 8px;
}

.stat-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  background: #f5f7fa;
  border-radius: 20px;
  font-size: 13px;
  color: #606266;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* SLA Score Card */
.sla-score-card {
  background: linear-gradient(135deg, #1f2f3d 0%, #0f1a24 100%);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 24px;
  color: #fff;
}

.sla-score-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 32px;
}

.sla-score-gauge {
  text-align: center;
}

.sla-score-text {
  text-align: center;
}

.sla-score-value {
  font-size: 28px;
  font-weight: 700;
}

.sla-score-unit {
  font-size: 14px;
}

.sla-score-label {
  margin-top: 12px;
  font-size: 14px;
  opacity: 0.8;
}

.sla-score-status {
  margin-top: 8px;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 20px;
  display: inline-block;
}

.sla-score-status.excellent { background: rgba(103, 194, 58, 0.2); color: #67c23a; }
.sla-score-status.good { background: rgba(230, 162, 60, 0.2); color: #e6a23c; }
.sla-score-status.fair { background: rgba(245, 108, 108, 0.2); color: #f56c6c; }
.sla-score-status.poor { background: rgba(245, 108, 108, 0.4); color: #ff6b6b; }

.sla-score-metrics {
  display: flex;
  gap: 32px;
  flex-wrap: wrap;
}

.sla-metric {
  text-align: center;
  min-width: 100px;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
}

.metric-value .unit {
  font-size: 12px;
  font-weight: normal;
  opacity: 0.7;
}

.metric-label {
  font-size: 12px;
  opacity: 0.7;
  margin-top: 4px;
}

/* KPI Cards Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.kpi-card {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.kpi-card.critical .kpi-header { background: linear-gradient(135deg, #fef0f0, #fff); border-bottom-color: #f56c6c; }
.kpi-card.major .kpi-header { background: linear-gradient(135deg, #fdf6ec, #fff); border-bottom-color: #e6a23c; }
.kpi-card.warning .kpi-header { background: linear-gradient(135deg, #fdf6ec, #fff); border-bottom-color: #fbbf24; }
.kpi-card.info .kpi-header { background: linear-gradient(135deg, #ecf5ff, #fff); border-bottom-color: #409eff; }

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 3px solid;
}

.kpi-title {
  font-weight: 600;
  font-size: 16px;
}

.kpi-target {
  font-size: 11px;
  color: #909399;
}

.kpi-body {
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.kpi-sla-score {
  flex-shrink: 0;
}

.kpi-stats {
  flex: 1;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  padding: 4px 0;
  border-bottom: 1px solid #f5f7fa;
}

.stat-row .success { color: #67c23a; }
.stat-row .danger { color: #f56c6c; }

/* Card */
.card {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  flex-wrap: wrap;
  gap: 12px;
  background: #fafafa;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1f2f3d;
}

.card-title .el-icon {
  color: #409eff;
}

/* Charts */
.chart-container {
  width: 100%;
  height: 320px;
  padding: 8px;
}

.chart-container-small {
  width: 100%;
  height: 280px;
  padding: 8px;
}

/* Two Columns */
.two-columns {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.two-columns .card {
  flex: 1;
  margin-bottom: 0;
}

/* Breach Reasons */
.breach-reasons {
  padding: 16px;
}

.reason-item {
  margin-bottom: 16px;
}

.reason-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 13px;
}

.reason-name {
  color: #606266;
}

.reason-count {
  font-weight: 600;
  color: #f56c6c;
}

/* Table */
.table-card {
  overflow-x: auto;
}

.table-controls {
  display: flex;
  gap: 12px;
}

.card-footer {
  padding: 16px 20px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  justify-content: flex-end;
  background: #fafafa;
}

.breached-value {
  color: #f56c6c;
  font-weight: 600;
}

/* Responsive */
@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .sla-score-content {
    flex-direction: column;
    text-align: center;
  }
  .sla-score-metrics {
    justify-content: center;
  }
}

@media (max-width: 1000px) {
  .two-columns {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .alarm-sla-dashboard {
    padding: 16px;
  }
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  .kpi-body {
    flex-direction: column;
    text-align: center;
  }
  .sla-score-metrics {
    gap: 16px;
  }
  .sla-metric {
    min-width: 80px;
  }
  .table-controls {
    flex-direction: column;
    width: 100%;
  }
}

/* Element Plus 样式覆盖 */
:deep(.el-table) {
  background: transparent;
  --el-table-header-bg-color: #fafafa;
  --el-table-row-hover-bg-color: #f5f7fa;
  --el-table-border-color: #e4e7ed;
}

:deep(.el-table th.el-table__cell) {
  background-color: #fafafa;
  color: #1f2f3d;
}

:deep(.el-table td.el-table__cell) {
  color: #606266;
}

:deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
  --el-pagination-button-bg-color: #f5f7fa;
  --el-pagination-hover-color: #409eff;
}

:deep(.el-dialog) {
  background: #ffffff;
  border-radius: 12px;
}

:deep(.el-dialog__title) {
  color: #1f2f3d;
}
</style>