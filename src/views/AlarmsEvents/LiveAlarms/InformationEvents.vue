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
        <div class="loading-tip">Information Events</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="info-events-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-left">
        <h1 class="dashboard-title">
          <span class="info-dot"></span>
          Information Events
        </h1>
        <div class="header-stats">
          <div class="stat-badge info">
            <span class="stat-dot"></span>
            {{ infoCount }} New Events
          </div>
          <div class="stat-badge">
            <el-icon><Clock /></el-icon>
            {{ currentTime }}
          </div>
        </div>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
        <el-button @click="exportReport">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
        <el-button @click="clearAllEvents">
          <el-icon><Delete /></el-icon>
          Clear All
        </el-button>
      </div>
    </div>

    <!-- KPI Cards Row -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-icon info-icon">
          <el-icon><InfoFilled /></el-icon>
        </div>
        <div class="kpi-content">
          <span class="kpi-label">Total Events (24h)</span>
          <span class="kpi-value">{{ totalEvents }}</span>
          <span class="kpi-trend up">{{ eventTrend }}% vs yesterday</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon system-icon">
          <el-icon><Monitor /></el-icon>
        </div>
        <div class="kpi-content">
          <span class="kpi-label">System Events</span>
          <span class="kpi-value">{{ systemEvents }}</span>
          <span class="kpi-trend up">{{ systemTrend }}%</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon user-icon">
          <el-icon><User /></el-icon>
        </div>
        <div class="kpi-content">
          <span class="kpi-label">User Events</span>
          <span class="kpi-value">{{ userEvents }}</span>
          <span class="kpi-trend down">{{ userTrend }}%</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon audit-icon">
          <el-icon><Document /></el-icon>
        </div>
        <div class="kpi-content">
          <span class="kpi-label">Audit Events</span>
          <span class="kpi-value">{{ auditEvents }}</span>
          <span class="kpi-trend stable">Audit trail</span>
        </div>
      </div>
    </div>

    <!-- Main Two-Column Layout -->
    <div class="dashboard-main">
      <!-- Left Column -->
      <div class="main-left">
        <!-- Real-time Information Events -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <span class="live-badge"></span>
              Real-time Information Events
              <el-badge :value="infoCount" type="info" v-if="infoCount > 0" />
            </div>
            <div class="card-actions">
              <el-input v-model="searchText" placeholder="Search events..." size="small" style="width: 200px" clearable>
                <template #prefix><el-icon><Search /></el-icon></template>
              </el-input>
              <el-select v-model="categoryFilter" placeholder="Category" size="small" style="width: 120px" clearable>
                <el-option label="All" value="all" />
                <el-option label="System" value="System" />
                <el-option label="User" value="User" />
                <el-option label="Audit" value="Audit" />
                <el-option label="Security" value="Security" />
                <el-option label="Maintenance" value="Maintenance" />
              </el-select>
            </div>
          </div>
          <div class="event-feed">
            <div v-for="event in filteredInfoEvents" :key="event.id" class="event-item" :class="event.category.toLowerCase()">
              <div class="event-indicator" :class="event.severity"></div>
              <div class="event-content">
                <div class="event-header">
                  <div class="event-title">
                    <el-tag :type="getCategoryTagType(event.category)" size="small">{{ event.category }}</el-tag>
                    <span>{{ event.title }}</span>
                  </div>
                  <div class="event-time">{{ event.timeAgo }}</div>
                </div>
                <div class="event-description">{{ event.description }}</div>
                <div class="event-footer">
                  <div class="event-meta">
                    <span><el-icon><Location /></el-icon> {{ event.location || 'System' }}</span>
                    <span><el-icon><User /></el-icon> {{ event.user || 'System' }}</span>
                    <span><el-icon><Document /></el-icon> Event ID: {{ event.id }}</span>
                  </div>
                  <div class="event-actions">
                    <el-button type="info" size="small" plain @click="viewDetails(event)">
                      <el-icon><View /></el-icon>
                      Details
                    </el-button>
                    <el-button type="primary" size="small" plain @click="acknowledgeEvent(event)" v-if="!event.acknowledged">
                      <el-icon><CircleCheck /></el-icon>
                      Acknowledge
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="filteredInfoEvents.length === 0" class="empty-state">
              <el-empty description="No information events" :image-size="80" />
            </div>
          </div>
          <div class="card-footer" v-if="filteredInfoEvents.length > pagination.pageSize">
            <el-pagination
                v-model:current-page="pagination.page"
                v-model:page-size="pagination.pageSize"
                :total="filteredInfoEvents.length"
                :page-sizes="[15, 30, 50]"
                layout="total, sizes, prev, pager, next"
                size="small"
            />
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="card quick-actions-card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Operation /></el-icon>
              Quick Actions
            </div>
          </div>
          <div class="quick-actions">
            <div class="action-btn" @click="acknowledgeAllEvents">
              <el-icon><CircleCheck /></el-icon>
              <span>Acknowledge All Events</span>
            </div>
            <div class="action-btn" @click="exportReport">
              <el-icon><Download /></el-icon>
              <span>Export Events Log</span>
            </div>
            <div class="action-btn" @click="openAuditTrail">
              <el-icon><List /></el-icon>
              <span>View Audit Trail</span>
            </div>
            <div class="action-btn" @click="clearAllEvents">
              <el-icon><Delete /></el-icon>
              <span>Clear Events</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column -->
      <div class="main-right">
        <!-- Event Trend Chart -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><TrendCharts /></el-icon>
              Event Trend (Last 24 Hours)
            </div>
          </div>
          <div ref="trendChartRef" class="chart-container"></div>
        </div>

        <!-- Event by Category -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><PieChart /></el-icon>
              Events by Category
            </div>
          </div>
          <div ref="categoryChartRef" class="small-chart"></div>
        </div>

        <!-- Top Users Activity -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><User /></el-icon>
              Top Active Users
            </div>
          </div>
          <div class="user-activity">
            <div v-for="user in topUsers" :key="user.name" class="user-item">
              <div class="user-info">
                <div class="user-avatar">{{ user.name.charAt(0) }}</div>
                <div class="user-details">
                  <div class="user-name">{{ user.name }}</div>
                  <div class="user-role">{{ user.role }}</div>
                </div>
              </div>
              <div class="user-stats">
                <span class="user-count">{{ user.eventCount }} events</span>
                <span class="user-time">{{ user.lastActive }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Event Summary -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><DataLine /></el-icon>
              Event Summary
            </div>
          </div>
          <div class="summary-stats">
            <div class="summary-item">
              <div class="summary-value">{{ systemEvents }}</div>
              <div class="summary-label">System Events</div>
            </div>
            <div class="summary-item">
              <div class="summary-value">{{ userEvents }}</div>
              <div class="summary-label">User Events</div>
            </div>
            <div class="summary-item">
              <div class="summary-value">{{ auditEvents }}</div>
              <div class="summary-label">Audit Events</div>
            </div>
            <div class="summary-item">
              <div class="summary-value">{{ acknowledgedCount }}</div>
              <div class="summary-label">Acknowledged</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Clock, Refresh, Download, Delete, InfoFilled, Monitor, User, Document,
  Search, Location, View, CircleCheck, TrendCharts, PieChart, DataLine,
  Operation, List
} from '@element-plus/icons-vue'
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

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Connecting to event service...',
  'Initializing dashboard...',
  'Almost ready...'
]

// ==================== Real-time Clock ====================
const currentTime = ref('')
const updateTime = () => {
  const now = new Date()
  const sgTime = new Date(now.getTime() + (8 * 3600000))
  currentTime.value = sgTime.toLocaleString('en-SG', {
    hour: '2-digit', minute: '2-digit', second: '2-digit',
    hour12: false
  })
}
let clockTimer: ReturnType<typeof setInterval> | null = null

// ==================== Data State ====================
const searchText = ref('')
const categoryFilter = ref('all')

const pagination = ref({ page: 1, pageSize: 15 })

// Information Events Data
interface InfoEvent {
  id: number
  title: string
  description: string
  severity: string
  category: string
  location: string
  user: string
  time: Date
  timeAgo: string
  acknowledged: boolean
  acknowledgedBy: string | null
}

const infoEvents = ref<InfoEvent[]>([
  { id: 1001, title: 'System Startup Complete', description: 'All services initialized successfully. System ready.', severity: 'info', category: 'System', location: 'Main Server', user: 'System', time: new Date(Date.now() - 2 * 60 * 1000), timeAgo: '2 min ago', acknowledged: false, acknowledgedBy: null },
  { id: 1002, title: 'User Login Successful', description: 'User john.doe logged into the system from 192.168.1.100', severity: 'info', category: 'User', location: 'Web Portal', user: 'john.doe', time: new Date(Date.now() - 5 * 60 * 1000), timeAgo: '5 min ago', acknowledged: false, acknowledgedBy: null },
  { id: 1003, title: 'Backup Completed', description: 'Daily backup completed successfully. 2.5GB data backed up.', severity: 'info', category: 'System', location: 'Backup Server', user: 'System', time: new Date(Date.now() - 10 * 60 * 1000), timeAgo: '10 min ago', acknowledged: false, acknowledgedBy: null },
  { id: 1004, title: 'Configuration Change', description: 'Network settings updated by administrator.', severity: 'info', category: 'Audit', location: 'Network Config', user: 'admin', time: new Date(Date.now() - 15 * 60 * 1000), timeAgo: '15 min ago', acknowledged: true, acknowledgedBy: 'Security Team' },
  { id: 1005, title: 'Scheduled Maintenance Started', description: 'Weekly maintenance window started. Expected duration: 2 hours.', severity: 'info', category: 'Maintenance', location: 'Data Center', user: 'System', time: new Date(Date.now() - 20 * 60 * 1000), timeAgo: '20 min ago', acknowledged: false, acknowledgedBy: null },
  { id: 1006, title: 'New Device Detected', description: 'New UPS device added to monitoring system.', severity: 'info', category: 'System', location: 'Electrical Room', user: 'auto-discovery', time: new Date(Date.now() - 30 * 60 * 1000), timeAgo: '30 min ago', acknowledged: false, acknowledgedBy: null },
  { id: 1007, title: 'Password Change Successful', description: 'User sara.chen changed password successfully.', severity: 'info', category: 'User', location: 'Security', user: 'sara.chen', time: new Date(Date.now() - 45 * 60 * 1000), timeAgo: '45 min ago', acknowledged: false, acknowledgedBy: null },
  { id: 1008, title: 'Audit Log Export', description: 'Audit logs exported by compliance officer.', severity: 'info', category: 'Audit', location: 'Audit System', user: 'compliance', time: new Date(Date.now() - 60 * 60 * 1000), timeAgo: '1 hour ago', acknowledged: false, acknowledgedBy: null },
  { id: 1009, title: 'Software Update Available', description: 'New version v2.5.0 available for dashboard.', severity: 'info', category: 'System', location: 'Update Server', user: 'System', time: new Date(Date.now() - 2 * 60 * 60 * 1000), timeAgo: '2 hours ago', acknowledged: false, acknowledgedBy: null },
  { id: 1010, title: 'User Logout', description: 'User mike.lim logged out from system.', severity: 'info', category: 'User', location: 'Web Portal', user: 'mike.lim', time: new Date(Date.now() - 3 * 60 * 60 * 1000), timeAgo: '3 hours ago', acknowledged: true, acknowledgedBy: 'System Auto' }
])

const infoCount = computed(() => infoEvents.value.filter(e => !e.acknowledged).length)
const totalEvents = computed(() => infoEvents.value.length)
const systemEvents = computed(() => infoEvents.value.filter(e => e.category === 'System').length)
const userEvents = computed(() => infoEvents.value.filter(e => e.category === 'User').length)
const auditEvents = computed(() => infoEvents.value.filter(e => e.category === 'Audit').length)
const acknowledgedCount = computed(() => infoEvents.value.filter(e => e.acknowledged).length)

const eventTrend = ref(12)
const systemTrend = ref(8)
const userTrend = ref(5)

const filteredInfoEvents = computed(() => {
  let filtered = infoEvents.value.filter(e => !e.acknowledged)
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(e => e.title.toLowerCase().includes(search) || e.description.toLowerCase().includes(search))
  }
  if (categoryFilter.value !== 'all') {
    filtered = filtered.filter(e => e.category === categoryFilter.value)
  }
  const start = (pagination.value.page - 1) * pagination.value.pageSize
  return filtered.slice(start, start + pagination.value.pageSize)
})

const topUsers = ref([
  { name: 'john.doe', role: 'System Administrator', eventCount: 24, lastActive: '5 min ago' },
  { name: 'sara.chen', role: 'Security Analyst', eventCount: 18, lastActive: '15 min ago' },
  { name: 'admin', role: 'Super Admin', eventCount: 15, lastActive: '30 min ago' },
  { name: 'mike.lim', role: 'Operator', eventCount: 12, lastActive: '1 hour ago' }
])

// Category distribution for chart
const categoryDistribution = computed(() => {
  const categories: Record<string, number> = {}
  infoEvents.value.forEach(e => {
    categories[e.category] = (categories[e.category] || 0) + 1
  })
  return Object.entries(categories).map(([name, count]) => ({ name, count, percent: (count / infoEvents.value.length) * 100 }))
})

// Trend data
const trendHours = ref<string[]>([])
const trendData = ref<number[]>([])

const initTrendData = () => {
  const hours = ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00']
  const data = [8, 6, 4, 5, 15, 25, 30, 22, 18, 12, 10, 7]
  trendHours.value = hours
  trendData.value = data
}

// ==================== Chart Refs ====================
const trendChartRef = ref<HTMLElement>()
const categoryChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null
let categoryChart: echarts.ECharts | null = null

const initCharts = () => {
  if (!trendChartRef.value || !categoryChartRef.value) {
    setTimeout(initCharts, 200)
    return
  }

  if (trendChart) trendChart.dispose()
  trendChart = echarts.init(trendChartRef.value)
  trendChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '10%', right: '5%', top: '10%', bottom: '5%', containLabel: true },
    xAxis: {
      type: 'category',
      data: trendHours.value,
      axisLabel: { rotate: 45, interval: 2, color: '#94a3b8' },
      axisLine: { lineStyle: { color: '#334155' } }
    },
    yAxis: {
      type: 'value',
      name: 'Event Count',
      nameTextStyle: { color: '#94a3b8' },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: '#1e293b' } }
    },
    series: [{
      name: 'Information Events',
      type: 'line',
      data: trendData.value,
      smooth: true,
      lineStyle: { color: '#60a5fa', width: 2 },
      areaStyle: { opacity: 0.2, color: '#60a5fa' },
      symbol: 'circle',
      symbolSize: 6,
      itemStyle: { color: '#60a5fa' }
    }]
  })

  if (categoryChart) categoryChart.dispose()
  categoryChart = echarts.init(categoryChartRef.value)
  updateCategoryChart()

  window.addEventListener('resize', () => {
    trendChart?.resize()
    categoryChart?.resize()
  })
}

const updateCategoryChart = () => {
  if (!categoryChart) return
  const data = categoryDistribution.value.map(item => ({
    name: item.name,
    value: item.count,
    itemStyle: { color: getCategoryColor(item.name) }
  }))
  categoryChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left', textStyle: { color: '#94a3b8' } },
    series: [{
      type: 'pie',
      radius: ['40%', '60%'],
      center: ['50%', '50%'],
      data: data,
      label: { show: true, formatter: '{b}: {d}%', color: '#cbd5e1' },
      emphasis: { scale: true }
    }]
  })
}

const getCategoryColor = (category: string) => {
  const colors: Record<string, string> = {
    System: '#60a5fa',
    User: '#34d399',
    Audit: '#fbbf24',
    Security: '#ef4444',
    Maintenance: '#8b5cf6'
  }
  return colors[category] || '#94a3b8'
}

const getCategoryTagType = (category: string) => {
  const map: Record<string, string> = {
    System: 'primary',
    User: 'success',
    Audit: 'warning',
    Security: 'danger',
    Maintenance: 'info'
  }
  return map[category] || 'info'
}

// ==================== Actions ====================
const acknowledgeEvent = (event: InfoEvent) => {
  event.acknowledged = true
  event.acknowledgedBy = 'Current User'
  ElMessage.success(`Event "${event.title}" acknowledged`)
  updateCategoryChart()
}

const acknowledgeAllEvents = () => {
  const unacknowledged = infoEvents.value.filter(e => !e.acknowledged)
  if (unacknowledged.length === 0) {
    ElMessage.warning('No unacknowledged events')
    return
  }
  ElMessageBox.confirm(`Acknowledge all ${unacknowledged.length} information events?`, 'Confirm', {
    confirmButtonText: 'Acknowledge All',
    cancelButtonText: 'Cancel',
    type: 'info'
  }).then(() => {
    unacknowledged.forEach(e => { e.acknowledged = true; e.acknowledgedBy = 'Bulk Action' })
    ElMessage.success(`Acknowledged ${unacknowledged.length} events`)
    updateCategoryChart()
  }).catch(() => {})
}

const viewDetails = (event: InfoEvent) => {
  ElMessage.info(`Viewing details for ${event.title}`)
}

const clearAllEvents = () => {
  const unacknowledged = infoEvents.value.filter(e => !e.acknowledged)
  if (unacknowledged.length === 0) {
    ElMessage.warning('No events to clear')
    return
  }
  ElMessageBox.confirm(`Clear all ${unacknowledged.length} unacknowledged events?`, 'Confirm', {
    confirmButtonText: 'Clear All',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    infoEvents.value = infoEvents.value.filter(e => e.acknowledged)
    ElMessage.success(`Cleared ${unacknowledged.length} events`)
    updateCategoryChart()
  }).catch(() => {})
}

const exportReport = () => {
  ElMessage.success('Exporting events log...')
}

const openAuditTrail = () => {
  ElMessage.info('Opening audit trail...')
}

const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  ElMessage.success('Events refreshed')
}

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

watch(categoryDistribution, () => {
  if (isLoaded.value) {
    updateCategoryChart()
  }
}, { deep: true })

// ==================== Lifecycle ====================
onMounted(() => {
  updateTime()
  clockTimer = setInterval(updateTime, 1000)

  initTrendData()
  startLoading()
})

onBeforeUnmount(() => {
  if (clockTimer) clearInterval(clockTimer)
  if (trendChart) trendChart.dispose()
  if (categoryChart) categoryChart.dispose()
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
.info-events-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 100%);
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
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #fff, #60a5fa);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  margin: 0 0 12px 0;
}

.info-dot {
  width: 12px;
  height: 12px;
  background: #60a5fa;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
  display: inline-block;
}

.header-stats {
  display: flex;
  gap: 16px;
}

.stat-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  font-size: 13px;
  color: #94a3b8;
}

.stat-badge.info .stat-dot {
  width: 8px;
  height: 8px;
  background: #60a5fa;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.kpi-card {
  background: rgba(15, 25, 45, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s;
}

.kpi-card:hover {
  transform: translateY(-2px);
  border-color: rgba(59, 130, 246, 0.5);
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

.info-icon { background: rgba(96, 165, 250, 0.15); color: #60a5fa; }
.system-icon { background: rgba(59, 130, 246, 0.15); color: #3b82f6; }
.user-icon { background: rgba(52, 211, 153, 0.15); color: #34d399; }
.audit-icon { background: rgba(251, 191, 36, 0.15); color: #fbbf24; }

.kpi-content {
  flex: 1;
}

.kpi-label {
  font-size: 13px;
  color: #94a3b8;
  display: block;
  margin-bottom: 4px;
}

.kpi-value {
  font-size: 32px;
  font-weight: 700;
  color: #fff;
}

.kpi-trend {
  font-size: 11px;
  display: block;
  margin-top: 4px;
}

.kpi-trend.up { color: #ef4444; }
.kpi-trend.down { color: #34d399; }
.kpi-trend.stable { color: #fbbf24; }

.dashboard-main {
  display: flex;
  gap: 24px;
}

.main-left {
  flex: 1.2;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.main-right {
  flex: 0.8;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card {
  background: rgba(15, 25, 45, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 20px;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
  flex-wrap: wrap;
  gap: 12px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #e2e8f0;
}

.live-badge {
  width: 8px;
  height: 8px;
  background: #60a5fa;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

.card-actions {
  display: flex;
  gap: 12px;
}

.event-feed {
  max-height: 500px;
  overflow-y: auto;
  padding: 8px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.event-feed::-webkit-scrollbar {
  display: none;
}

.event-item {
  display: flex;
  gap: 12px;
  padding: 14px;
  margin-bottom: 10px;
  background: rgba(96, 165, 250, 0.03);
  border-radius: 12px;
  transition: all 0.2s;
  border: 1px solid rgba(96, 165, 250, 0.1);
}

.event-item:hover {
  background: rgba(96, 165, 250, 0.06);
}

.event-indicator {
  width: 4px;
  border-radius: 2px;
}

.event-indicator.info { background: #60a5fa; }

.event-content {
  flex: 1;
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  flex-wrap: wrap;
  gap: 8px;
}

.event-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #e2e8f0;
}

.event-time {
  font-size: 11px;
  color: #64748b;
}

.event-description {
  font-size: 13px;
  color: #94a3b8;
  margin-bottom: 10px;
}

.event-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.event-meta {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: #64748b;
}

.event-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.event-actions {
  display: flex;
  gap: 8px;
}

.card-footer {
  padding: 12px 16px;
  border-top: 1px solid rgba(148, 163, 184, 0.1);
  display: flex;
  justify-content: flex-end;
}

.empty-state {
  padding: 40px;
  text-align: center;
}

.chart-container {
  width: 100%;
  height: 280px;
  padding: 8px;
}

.small-chart {
  width: 100%;
  height: 260px;
}

.user-activity {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.user-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  background: rgba(96, 165, 250, 0.15);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: #60a5fa;
}

.user-name {
  font-weight: 500;
  color: #e2e8f0;
  font-size: 13px;
}

.user-role {
  font-size: 11px;
  color: #64748b;
}

.user-stats {
  text-align: right;
}

.user-count {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #facc15;
}

.user-time {
  font-size: 10px;
  color: #64748b;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  padding: 20px;
}

.summary-item {
  text-align: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
}

.summary-value {
  font-size: 28px;
  font-weight: 700;
  color: #60a5fa;
}

.summary-label {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 4px;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(59, 130, 246, 0.08);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  color: #94a3b8;
}

.action-btn:hover {
  background: rgba(59, 130, 246, 0.15);
  transform: translateX(2px);
  color: #60a5fa;
}

/* Responsive */
@media (max-width: 1200px) {
  .dashboard-main {
    flex-direction: column;
  }
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .info-events-dashboard {
    padding: 16px;
  }
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .header-stats {
    flex-wrap: wrap;
  }
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  .card-actions {
    flex-direction: column;
    width: 100%;
  }
  .event-actions {
    flex-wrap: wrap;
  }
}
</style>