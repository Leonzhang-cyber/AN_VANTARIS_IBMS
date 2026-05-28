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

  <!-- SLA Compliance Page Content -->
  <div v-else class="sla-compliance-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>SLA Compliance</h1>
        <p class="subtitle">Track and monitor Service Level Agreement compliance across all operations</p>
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
      <div class="kpi-card overall">
        <div class="kpi-icon">
          <el-icon :size="32"><Medal /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ overallCompliance }}%</div>
          <div class="kpi-label">Overall SLA Compliance</div>
        </div>
        <div class="kpi-trend" :class="overallTrend >= 0 ? 'positive' : 'negative'">
          <el-icon><CaretTop v-if="overallTrend >= 0" /><CaretBottom v-else /></el-icon>
          {{ Math.abs(overallTrend) }}%
        </div>
      </div>
      <div class="kpi-card met">
        <div class="kpi-icon">
          <el-icon :size="32"><CircleCheck /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ slasMet }}</div>
          <div class="kpi-label">SLAs Met</div>
        </div>
        <div class="kpi-sub">{{ totalSLAs }} Total</div>
      </div>
      <div class="kpi-card breached">
        <div class="kpi-icon">
          <el-icon :size="32"><WarningFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ slasBreached }}</div>
          <div class="kpi-label">SLAs Breached</div>
        </div>
        <div class="kpi-sub">{{ breachedRate }}% Breach Rate</div>
      </div>
      <div class="kpi-card response">
        <div class="kpi-icon">
          <el-icon :size="32"><Timer /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ avgResponseTime }}</div>
          <div class="kpi-label">Avg Response Time</div>
        </div>
        <div class="kpi-sub">Target: {{ responseTarget }}</div>
      </div>
    </div>

    <!-- SLA Trend Chart -->
    <div class="chart-card">
      <div class="card-header">
        <h3>SLA Compliance Trend</h3>
        <el-radio-group v-model="trendPeriod" size="small" @change="fetchTrendData">
          <el-radio-button label="week">Last 7 Days</el-radio-button>
          <el-radio-button label="month">Last 30 Days</el-radio-button>
          <el-radio-button label="quarter">Last 90 Days</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-container" ref="trendChartRef"></div>
    </div>

    <!-- SLA by Category -->
    <div class="two-columns">
      <div class="chart-card">
        <div class="card-header">
          <h3>SLA Compliance by Category</h3>
        </div>
        <div class="chart-container" ref="categoryChartRef"></div>
      </div>
      <div class="chart-card">
        <div class="card-header">
          <h3>Top SLA Breach Reasons</h3>
        </div>
        <div class="chart-container" ref="breachChartRef"></div>
      </div>
    </div>

    <!-- SLA Performance by Vendor/Team -->
    <div class="table-card">
      <div class="card-header">
        <h3>SLA Performance by Vendor / Team</h3>
        <el-input
            v-model="searchText"
            placeholder="Search vendors..."
            :prefix-icon="Search"
            style="width: 260px"
            clearable
        />
      </div>
      <el-table :data="filteredVendors" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="name" label="Vendor / Team" min-width="180">
          <template #default="{ row }">
            <div class="vendor-cell">
              <el-avatar :size="32" :src="row.avatar" v-if="row.avatar">
                {{ row.name.charAt(0) }}
              </el-avatar>
              <div class="vendor-info">
                <span class="vendor-name">{{ row.name }}</span>
                <span class="vendor-type">{{ row.type }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="Category" width="140">
          <template #default="{ row }">
            <el-tag size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="compliance" label="SLA Compliance" width="180">
          <template #default="{ row }">
            <div class="compliance-cell">
              <span :class="getComplianceClass(row.compliance)">{{ row.compliance }}%</span>
              <el-progress
                  :percentage="row.compliance"
                  :color="getComplianceColor(row.compliance)"
                  :stroke-width="6"
                  :show-text="false"
                  style="width: 100px"
              />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="target" label="Target" width="100">
          <template #default="{ row }">
            ≥ {{ row.target }}%
          </template>
        </el-table-column>
        <el-table-column prop="met" label="Met" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.met >= row.target ? 'success' : 'danger'" size="small">
              {{ row.met }}/{{ row.total }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="breached" label="Breached" width="80" align="center">
          <template #default="{ row }">
            <span class="text-danger">{{ row.breached }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="avgResponseTime" label="Avg Response" width="120">
          <template #default="{ row }">
            {{ row.avgResponseTime }}
          </template>
        </el-table-column>
        <el-table-column label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.compliance, row.target)" size="small" effect="dark">
              {{ getStatusLabel(row.compliance, row.target) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredVendors.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Recent SLA Breaches -->
    <div class="alerts-section">
      <div class="section-header">
        <h2>
          <el-icon><Warning /></el-icon>
          Recent SLA Breaches
        </h2>
        <el-button link type="primary" @click="viewAllBreaches">View All Breaches →</el-button>
      </div>
      <div class="breaches-list">
        <div v-for="breach in recentBreaches" :key="breach.id" class="breach-item" :class="breach.severity">
          <div class="breach-icon">
            <el-icon><WarningFilled /></el-icon>
          </div>
          <div class="breach-content">
            <div class="breach-title">{{ breach.title }}</div>
            <div class="breach-desc">{{ breach.description }}</div>
            <div class="breach-meta">
              <span><el-icon><Clock /></el-icon> {{ formatRelativeTime(breach.timestamp) }}</span>
              <span><el-icon><User /></el-icon> {{ breach.vendor }}</span>
              <span>Target: {{ breach.target }} | Actual: {{ breach.actual }}</span>
            </div>
          </div>
          <div class="breach-actions">
            <el-button size="small" type="primary" link @click="viewBreachDetails(breach)">Details</el-button>
          </div>
        </div>
        <div v-if="recentBreaches.length === 0" class="no-breaches">
          <el-empty description="No SLA breaches in the selected period" :image-size="80" />
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
  Medal,
  CircleCheck,
  WarningFilled,
  Timer,
  CaretTop,
  CaretBottom,
  Search,
  Warning,
  Clock,
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
interface VendorSLA {
  id: number
  name: string
  type: string
  category: string
  compliance: number
  target: number
  met: number
  total: number
  breached: number
  avgResponseTime: string
  avatar?: string
}

interface SLABreach {
  id: number
  title: string
  description: string
  severity: 'critical' | 'warning' | 'info'
  timestamp: string
  vendor: string
  target: string
  actual: string
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
const breachChartRef = ref<HTMLElement | null>(null)
let trendChart: echarts.ECharts | null = null
let categoryChart: echarts.ECharts | null = null
let breachChart: echarts.ECharts | null = null

// ==================== Mock Data ====================
const vendors = ref<VendorSLA[]>([
  { id: 1, name: 'Johnson Controls', type: 'HVAC Vendor', category: 'HVAC', compliance: 98.5, target: 99, met: 197, total: 200, breached: 3, avgResponseTime: '15 min', avatar: '' },
  { id: 2, name: 'Schneider Electric', type: 'Electrical Vendor', category: 'Electrical', compliance: 99.2, target: 99, met: 248, total: 250, breached: 2, avgResponseTime: '12 min', avatar: '' },
  { id: 3, name: 'Siemens', type: 'BMS Vendor', category: 'BMS', compliance: 97.8, target: 98, met: 195, total: 200, breached: 5, avgResponseTime: '22 min', avatar: '' },
  { id: 4, name: 'Honeywell', type: 'Security Vendor', category: 'Security', compliance: 96.5, target: 98, met: 193, total: 200, breached: 7, avgResponseTime: '28 min', avatar: '' },
  { id: 5, name: 'Daikin', type: 'HVAC Vendor', category: 'HVAC', compliance: 99.5, target: 99, met: 199, total: 200, breached: 1, avgResponseTime: '8 min', avatar: '' },
  { id: 6, name: 'Vertiv', type: 'Data Center Vendor', category: 'DCIM', compliance: 98.9, target: 99, met: 198, total: 200, breached: 2, avgResponseTime: '18 min', avatar: '' },
  { id: 7, name: 'In-House Team A', type: 'Internal', category: 'Maintenance', compliance: 94.5, target: 95, met: 189, total: 200, breached: 11, avgResponseTime: '35 min', avatar: '' },
  { id: 8, name: 'In-House Team B', type: 'Internal', category: 'Operations', compliance: 96.2, target: 95, met: 192, total: 200, breached: 8, avgResponseTime: '25 min', avatar: '' },
  { id: 9, name: 'Cisco', type: 'Network Vendor', category: 'Network', compliance: 99.8, target: 99, met: 199, total: 200, breached: 1, avgResponseTime: '5 min', avatar: '' },
  { id: 10, name: 'Eaton', type: 'UPS Vendor', category: 'Electrical', compliance: 98.2, target: 99, met: 196, total: 200, breached: 4, avgResponseTime: '20 min', avatar: '' }
])

const recentBreaches = ref<SLABreach[]>([
  { id: 1, title: 'HVAC Response Time Exceeded', description: 'AHU-101 repair request exceeded SLA response time by 12 minutes.', severity: 'warning', timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString(), vendor: 'Johnson Controls', target: '30 min', actual: '42 min' },
  { id: 2, title: 'Security Incident Response Delayed', description: 'Access control failure response exceeded 4-hour resolution SLA.', severity: 'critical', timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), vendor: 'Honeywell', target: '4 hours', actual: '5.5 hours' },
  { id: 3, title: 'Preventive Maintenance Missed', description: 'Quarterly chiller maintenance was not completed on schedule.', severity: 'warning', timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(), vendor: 'Daikin', target: 'Within quarter', actual: '5 days overdue' },
  { id: 4, title: 'BMS Controller Update Failure', description: 'Firmware update took 45 minutes longer than SLA target.', severity: 'info', timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(), vendor: 'Siemens', target: '30 min', actual: '75 min' }
])

// ==================== Computed Values ====================
const overallCompliance = computed(() => {
  const total = vendors.value.reduce((sum, v) => sum + v.compliance, 0)
  return (total / vendors.value.length).toFixed(1)
})

const slasMet = computed(() => {
  return vendors.value.reduce((sum, v) => sum + v.met, 0)
})

const slasBreached = computed(() => {
  return vendors.value.reduce((sum, v) => sum + v.breached, 0)
})

const totalSLAs = computed(() => {
  return vendors.value.reduce((sum, v) => sum + v.total, 0)
})

const breachedRate = computed(() => {
  return ((slasBreached.value / totalSLAs.value) * 100).toFixed(1)
})

const avgResponseTime = computed(() => {
  const times = vendors.value.map(v => {
    const match = v.avgResponseTime.match(/(\d+)/)
    return match ? parseInt(match[1]) : 0
  })
  const avg = times.reduce((a, b) => a + b, 0) / times.length
  return `${Math.round(avg)} min`
})

const responseTarget = computed(() => '30 min')

const overallTrend = computed(() => 1.2)

const filteredVendors = computed(() => {
  let result = [...vendors.value]
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(v =>
        v.name.toLowerCase().includes(search) ||
        v.type.toLowerCase().includes(search) ||
        v.category.toLowerCase().includes(search)
    )
  }
  return result
})

// ==================== Helper Functions ====================
const getComplianceClass = (compliance: number) => {
  if (compliance >= 99) return 'compliance-excellent'
  if (compliance >= 98) return 'compliance-good'
  if (compliance >= 95) return 'compliance-fair'
  return 'compliance-poor'
}

const getComplianceColor = (compliance: number) => {
  if (compliance >= 99) return '#67c23a'
  if (compliance >= 98) return '#409eff'
  if (compliance >= 95) return '#e6a23c'
  return '#f56c6c'
}

const getStatusLabel = (compliance: number, target: number) => {
  if (compliance >= target) return 'On Track'
  if (compliance >= target - 2) return 'At Risk'
  return 'Breached'
}

const getStatusTagType = (compliance: number, target: number) => {
  if (compliance >= target) return 'success'
  if (compliance >= target - 2) return 'warning'
  return 'danger'
}

const formatRelativeTime = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins} min ago`
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
  return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
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
  const target: number[] = []

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    dates.push(`${date.getMonth() + 1}/${date.getDate()}`)

    const baseOverall = 97.5 + Math.sin(i * 0.2) * 0.8 + Math.random() * 0.3
    overall.push(Number(baseOverall.toFixed(1)))
    target.push(98)
  }

  return { dates, overall, target }
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)
  const data = generateTrendData()

  trendChart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: (value: number) => value + '%' },
    legend: { data: ['SLA Compliance', 'Target (98%)'], bottom: 0 },
    grid: { left: '3%', right: '4%', top: '10%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: data.dates },
    yAxis: { type: 'value', name: 'Compliance (%)', min: 94, max: 100, axisLabel: { formatter: '{value}%' } },
    series: [
      {
        name: 'SLA Compliance', type: 'line', data: data.overall, smooth: true, symbol: 'circle',
        lineStyle: { width: 3, color: '#409eff' }, areaStyle: { opacity: 0.1, color: '#409eff' }
      },
      {
        name: 'Target (98%)', type: 'line', data: data.target, smooth: false, symbol: 'none',
        lineStyle: { width: 2, color: '#f56c6c', type: 'dashed' }
      }
    ]
  })
}

const initCategoryChart = () => {
  if (!categoryChartRef.value) return
  if (categoryChart) categoryChart.dispose()

  categoryChart = echarts.init(categoryChartRef.value)

  const categories = ['HVAC', 'Electrical', 'Security', 'Maintenance', 'DCIM', 'Network', 'BMS']
  const complianceData = [98.2, 98.7, 96.5, 94.8, 98.9, 99.2, 97.5]
  const targetData = categories.map(() => 98)

  categoryChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: (value: number) => value + '%' },
    legend: { data: ['Actual Compliance', 'Target (98%)'], bottom: 0 },
    grid: { left: '10%', right: '5%', top: '5%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: categories, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: 'Compliance (%)', min: 90, max: 100, axisLabel: { formatter: '{value}%' } },
    series: [
      {
        name: 'Actual Compliance', type: 'bar', data: complianceData,
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
          color: (params: any) => {
            const value = params.data
            if (value >= 98) return '#67c23a'
            if (value >= 95) return '#e6a23c'
            return '#f56c6c'
          }
        },
        label: { show: true, position: 'top', formatter: '{c}%', fontSize: 11 }
      },
      {
        name: 'Target (98%)', type: 'line', data: targetData, symbol: 'none',
        lineStyle: { width: 2, color: '#f56c6c', type: 'dashed' }
      }
    ]
  })
}

const initBreachChart = () => {
  if (!breachChartRef.value) return
  if (breachChart) breachChart.dispose()

  breachChart = echarts.init(breachChartRef.value)

  const reasons = [
    'Response Time Exceeded',
    'Resolution Time Exceeded',
    'Missed Scheduled Maintenance',
    'Incomplete Documentation',
    'Quality Issues'
  ]
  const counts = [28, 22, 15, 8, 5]

  breachChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} breaches ({d}%)' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      type: 'pie', radius: '55%', center: ['50%', '50%'],
      data: reasons.map((name, i) => ({ name, value: counts[i] })),
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: {d}%', fontSize: 11 },
      itemStyle: {
        borderRadius: 8,
        borderColor: '#fff',
        borderWidth: 2,
        color: (params: any) => {
          const colors = ['#f56c6c', '#e6a23c', '#f56c6c', '#409eff', '#67c23a']
          return colors[params.dataIndex]
        }
      }
    }]
  })
}

// ==================== Actions ====================
const refreshData = async () => {
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  ElMessage.success('SLA data refreshed')
  initTrendChart()
  initCategoryChart()
  initBreachChart()
  tableLoading.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting SLA compliance report...')
}

const fetchTrendData = () => {
  initTrendChart()
}

const handleDateChange = () => {
  ElMessage.info(`Date range updated: ${dateRange.value?.[0]?.toLocaleDateString()} - ${dateRange.value?.[1]?.toLocaleDateString()}`)
}

const viewAllBreaches = () => {
  ElMessage.info('Viewing all SLA breaches')
}

const viewBreachDetails = (breach: SLABreach) => {
  ElMessage.info(`Viewing breach details: ${breach.title}`)
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Window Resize Handler ====================
const handleResize = () => {
  trendChart?.resize()
  categoryChart?.resize()
  breachChart?.resize()
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
        initBreachChart()
      }, 100)
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  categoryChart?.dispose()
  breachChart?.dispose()
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
.sla-compliance-page {
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
.kpi-card.met .kpi-icon { background: #e8f8f0; color: #67c23a; }
.kpi-card.breached .kpi-icon { background: #ffe8e8; color: #f56c6c; }
.kpi-card.response .kpi-icon { background: #f0e8ff; color: #8b5cf6; }

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

/* Vendor Table */
.vendor-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.vendor-info {
  display: flex;
  flex-direction: column;
}

.vendor-name {
  font-weight: 500;
  color: #1f2f3d;
}

.vendor-type {
  font-size: 12px;
  color: #909399;
}

.compliance-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.compliance-excellent { color: #67c23a; font-weight: 600; }
.compliance-good { color: #409eff; font-weight: 500; }
.compliance-fair { color: #e6a23c; }
.compliance-poor { color: #f56c6c; }

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

/* Alerts Section */
.alerts-section {
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

.breaches-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.breach-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 14px 16px;
  background: #fafafa;
  border-radius: 12px;
  transition: background 0.2s;
}

.breach-item:hover {
  background: #f5f7fa;
}

.breach-item.critical .breach-icon { color: #f56c6c; }
.breach-item.warning .breach-icon { color: #e6a23c; }
.breach-item.info .breach-icon { color: #409eff; }

.breach-icon .el-icon {
  font-size: 20px;
}

.breach-content {
  flex: 1;
}

.breach-title {
  font-weight: 600;
  color: #1f2f3d;
  margin-bottom: 4px;
}

.breach-desc {
  font-size: 13px;
  color: #606266;
  margin-bottom: 6px;
}

.breach-meta {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #909399;
}

.breach-meta .el-icon {
  vertical-align: middle;
  margin-right: 4px;
}

.breach-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.breach-item:hover .breach-actions {
  opacity: 1;
}

.no-breaches {
  padding: 40px 0;
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