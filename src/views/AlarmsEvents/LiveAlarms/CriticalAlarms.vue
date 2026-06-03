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
        <div class="loading-tip">Critical Alarms System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="critical-alarms-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-left">
        <h1 class="dashboard-title">
          <span class="critical-dot"></span>
          Critical Alarms
        </h1>
        <div class="header-stats">
          <div class="stat-badge critical">
            <span class="stat-dot"></span>
            {{ criticalCount }} Active Critical
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
      </div>
    </div>

    <!-- KPI Cards Row -->
    <div class="kpi-grid">
      <div class="kpi-card" :class="{ pulse: criticalCount > 0 }">
        <div class="kpi-icon critical-icon">
          <el-icon><WarningFilled /></el-icon>
        </div>
        <div class="kpi-content">
          <span class="kpi-label">Active Critical Alarms</span>
          <span class="kpi-value">{{ criticalCount }}</span>
          <span class="kpi-trend up">{{ criticalTrend }}% vs last hour</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon resolved-icon">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="kpi-content">
          <span class="kpi-label">Resolved (24h)</span>
          <span class="kpi-value">{{ resolvedCount }}</span>
          <span class="kpi-trend down">{{ resolvedTrend }}% resolved</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon mttr-icon">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="kpi-content">
          <span class="kpi-label">Avg Response Time</span>
          <span class="kpi-value">{{ avgResponseTime }}<span class="unit">min</span></span>
          <span class="kpi-trend down">{{ responseTrend }}% vs target</span>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon affected-icon">
          <el-icon><Monitor /></el-icon>
        </div>
        <div class="kpi-content">
          <span class="kpi-label">Affected Systems</span>
          <span class="kpi-value">{{ affectedSystemsCount }}</span>
          <span class="kpi-trend up">{{ affectedTrend }} impacted</span>
        </div>
      </div>
    </div>

    <!-- Main Two-Column Layout -->
    <div class="dashboard-main">
      <!-- Left Column -->
      <div class="main-left">
        <!-- Real-time Critical Alarms -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <span class="live-badge"></span>
              Real-time Critical Alarms
              <el-badge :value="criticalCount" type="danger" v-if="criticalCount > 0" />
            </div>
            <div class="card-actions">
              <el-input v-model="searchText" placeholder="Search critical alarms..." size="small" style="width: 200px" clearable>
                <template #prefix><el-icon><Search /></el-icon></template>
              </el-input>
              <el-select v-model="categoryFilter" placeholder="Category" size="small" style="width: 120px" clearable>
                <el-option label="All" value="all" />
                <el-option label="Environmental" value="Environmental" />
                <el-option label="Power" value="Power" />
                <el-option label="Cooling" value="Cooling" />
                <el-option label="Network" value="Network" />
                <el-option label="Safety" value="Safety" />
              </el-select>
            </div>
          </div>
          <div class="alarm-feed">
            <div v-for="alarm in filteredCriticalAlarms" :key="alarm.id" class="alarm-item critical">
              <div class="alarm-indicator critical"></div>
              <div class="alarm-content">
                <div class="alarm-header">
                  <div class="alarm-title">
                    <el-tag type="danger" size="small">CRITICAL</el-tag>
                    <span>{{ alarm.title }}</span>
                  </div>
                  <div class="alarm-time">{{ alarm.timeAgo }}</div>
                </div>
                <div class="alarm-description">{{ alarm.description }}</div>
                <div class="alarm-footer">
                  <div class="alarm-meta">
                    <span><el-icon><Location /></el-icon> {{ alarm.location }}</span>
                    <span><el-icon><Folder /></el-icon> {{ alarm.category }}</span>
                    <span><el-icon><RefreshRight /></el-icon> {{ alarm.occurrences }} occurrences</span>
                  </div>
                  <div class="alarm-actions" v-if="!alarm.acknowledged">
                    <el-button type="primary" size="small" plain @click="acknowledgeAlarm(alarm)">
                      <el-icon><CircleCheck /></el-icon>
                      Acknowledge
                    </el-button>
                    <el-button type="warning" size="small" plain @click="escalateAlarm(alarm)">
                      <el-icon><Top /></el-icon>
                      Escalate
                    </el-button>
                    <el-button type="info" size="small" plain @click="viewDetails(alarm)">
                      <el-icon><View /></el-icon>
                      Details
                    </el-button>
                  </div>
                  <div class="alarm-ack-status" v-else>
                    <el-tag type="success" size="small">Acknowledged by {{ alarm.acknowledgedBy }}</el-tag>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="filteredCriticalAlarms.length === 0" class="empty-state">
              <el-empty description="No critical alarms" :image-size="80" />
            </div>
          </div>
          <div class="card-footer" v-if="filteredCriticalAlarms.length > pagination.pageSize">
            <el-pagination
                v-model:current-page="pagination.page"
                v-model:page-size="pagination.pageSize"
                :total="filteredCriticalAlarms.length"
                :page-sizes="[10, 20, 50]"
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
            <div class="action-btn" @click="acknowledgeAllCritical">
              <el-icon><CircleCheck /></el-icon>
              <span>Acknowledge All Critical</span>
            </div>
            <div class="action-btn" @click="exportReport">
              <el-icon><Download /></el-icon>
              <span>Export Critical Report</span>
            </div>
            <div class="action-btn" @click="openEscalationMatrix">
              <el-icon><Share /></el-icon>
              <span>Escalation Matrix</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column -->
      <div class="main-right">
        <!-- Critical Alarm Trend Chart -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><TrendCharts /></el-icon>
              Critical Alarm Trend (Last 24 Hours)
            </div>
          </div>
          <div ref="trendChartRef" class="chart-container"></div>
        </div>

        <!-- Alarm by Category -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><PieChart /></el-icon>
              Critical Alarms by Category
            </div>
          </div>
          <div ref="categoryChartRef" class="small-chart"></div>
        </div>

        <!-- Affected Systems -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Monitor /></el-icon>
              Affected Systems
            </div>
          </div>
          <div class="affected-tags">
            <span v-for="system in affectedSystems" :key="system.name" class="affected-tag" :class="system.severity">
              <span class="tag-dot" :class="system.severity"></span>
              {{ system.name }}
              <span class="tag-count">{{ system.alarmCount }}</span>
            </span>
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
  Clock, Refresh, Download, WarningFilled, CircleCheck, Timer, Monitor,
  Search, Location, Folder, RefreshRight, Top, View, TrendCharts, PieChart, Operation, Share
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
  'Connecting to alarm service...',
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

const pagination = ref({ page: 1, pageSize: 10 })

// Critical Alarms Data
interface Alarm {
  id: number
  title: string
  description: string
  severity: string
  location: string
  category: string
  time: Date
  timeAgo: string
  occurrences: number
  acknowledged: boolean
  acknowledgedBy: string | null
}

const criticalAlarms = ref<Alarm[]>([
  { id: 1, title: 'Temperature Critical', description: 'Server room temperature exceeded 35°C threshold. Immediate action required.', severity: 'critical', location: 'Data Center - Row A', category: 'Environmental', time: new Date(Date.now() - 2 * 60 * 1000), timeAgo: '2 min ago', occurrences: 3, acknowledged: false, acknowledgedBy: null },
  { id: 2, title: 'UPS Overload', description: 'UPS load exceeds 90% capacity. Risk of power failure.', severity: 'critical', location: 'Electrical Room', category: 'Power', time: new Date(Date.now() - 5 * 60 * 1000), timeAgo: '5 min ago', occurrences: 2, acknowledged: false, acknowledgedBy: null },
  { id: 3, title: 'Chiller Failure', description: 'Primary chiller offline, backup unit running at 60% capacity.', severity: 'critical', location: 'HVAC Room', category: 'Cooling', time: new Date(Date.now() - 12 * 60 * 1000), timeAgo: '12 min ago', occurrences: 1, acknowledged: false, acknowledgedBy: null },
  { id: 4, title: 'Fire Alarm', description: 'Smoke detected in server room. Evacuation procedure initiated.', severity: 'critical', location: 'Data Center', category: 'Safety', time: new Date(Date.now() - 18 * 60 * 1000), timeAgo: '18 min ago', occurrences: 1, acknowledged: true, acknowledgedBy: 'John Doe' },
  { id: 5, title: 'Network Core Down', description: 'Core switch unreachable. Redundant path active but degraded.', severity: 'critical', location: 'Network Rack B', category: 'Network', time: new Date(Date.now() - 25 * 60 * 1000), timeAgo: '25 min ago', occurrences: 5, acknowledged: false, acknowledgedBy: null },
  { id: 6, title: 'Cooling Pump Failure', description: 'Secondary cooling pump failed. Redundancy compromised.', severity: 'critical', location: 'Chiller Plant', category: 'Cooling', time: new Date(Date.now() - 35 * 60 * 1000), timeAgo: '35 min ago', occurrences: 2, acknowledged: false, acknowledgedBy: null },
  { id: 7, title: 'Power Sag Detected', description: 'Voltage sag below 200V on Phase B.', severity: 'critical', location: 'Main Distribution', category: 'Power', time: new Date(Date.now() - 42 * 60 * 1000), timeAgo: '42 min ago', occurrences: 1, acknowledged: true, acknowledgedBy: 'Sarah Chen' }
])

const criticalCount = computed(() => criticalAlarms.value.filter(a => !a.acknowledged).length)
const resolvedCount = computed(() => criticalAlarms.value.filter(a => a.acknowledged).length)
const criticalTrend = ref(15)
const resolvedTrend = ref(8)
const avgResponseTime = ref(8.5)
const responseTrend = ref(12)
const affectedSystemsCount = ref(5)
const affectedTrend = ref(3)

const filteredCriticalAlarms = computed(() => {
  let filtered = criticalAlarms.value.filter(a => !a.acknowledged)
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(a => a.title.toLowerCase().includes(search) || a.description.toLowerCase().includes(search))
  }
  if (categoryFilter.value !== 'all') {
    filtered = filtered.filter(a => a.category === categoryFilter.value)
  }
  const start = (pagination.value.page - 1) * pagination.value.pageSize
  return filtered.slice(start, start + pagination.value.pageSize)
})

interface AffectedSystem {
  name: string
  icon: string
  alarmCount: number
  severity: string
  status: string
}

const affectedSystems = ref<AffectedSystem[]>([
  { name: 'HVAC System', icon: 'Snowflake', alarmCount: 2, severity: 'critical', status: 'Critical' },
  { name: 'Power Distribution', icon: 'Lightning', alarmCount: 1, severity: 'critical', status: 'Critical' },
  { name: 'Server Infrastructure', icon: 'Monitor', alarmCount: 1, severity: 'critical', status: 'Critical' },
  { name: 'Network Core', icon: 'Connection', alarmCount: 1, severity: 'critical', status: 'Critical' }
])

// Category distribution for chart
const categoryDistribution = computed(() => {
  const unacknowledged = criticalAlarms.value.filter(a => !a.acknowledged)
  const categories: Record<string, number> = {}
  unacknowledged.forEach(a => {
    categories[a.category] = (categories[a.category] || 0) + 1
  })
  return Object.entries(categories).map(([name, count]) => ({ name, count, percent: (count / unacknowledged.length) * 100 }))
})

// Trend data - 固定数据用于图表展示
const trendHours = ref<string[]>([])
const trendData = ref<number[]>([])

const initTrendData = () => {
  const hours = ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00']
  const data = [2, 1, 0, 1, 5, 8, 6, 4, 3, 2, 1, 0]
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
    console.log('Chart refs not ready, retrying...')
    setTimeout(initCharts, 200)
    return
  }

  // 初始化趋势图
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
      name: 'Critical Alarms',
      nameTextStyle: { color: '#94a3b8' },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: '#1e293b' } }
    },
    series: [{
      name: 'Critical Alarms',
      type: 'line',
      data: trendData.value,
      smooth: true,
      lineStyle: { color: '#ef4444', width: 2 },
      areaStyle: { opacity: 0.2, color: '#ef4444' },
      symbol: 'circle',
      symbolSize: 6,
      itemStyle: { color: '#ef4444' }
    }]
  })

  // 初始化分类饼图
  if (categoryChart) categoryChart.dispose()
  categoryChart = echarts.init(categoryChartRef.value)
  updateCategoryChart()

  // 监听窗口大小变化
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
    Environmental: '#34d399',
    Power: '#f97316',
    Cooling: '#60a5fa',
    Network: '#fbbf24',
    Safety: '#ef4444'
  }
  return colors[category] || '#94a3b8'
}

// ==================== Actions ====================
const acknowledgeAlarm = (alarm: Alarm) => {
  ElMessageBox.confirm(`Acknowledge critical alarm "${alarm.title}"?`, 'Confirm', {
    confirmButtonText: 'Acknowledge',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    alarm.acknowledged = true
    alarm.acknowledgedBy = 'Current User'
    ElMessage.success(`Critical alarm "${alarm.title}" acknowledged`)
    updateCategoryChart()
  }).catch(() => {})
}

const escalateAlarm = (alarm: Alarm) => {
  ElMessageBox.confirm(`Escalate critical alarm "${alarm.title}" to management?`, 'Confirm', {
    confirmButtonText: 'Escalate',
    cancelButtonText: 'Cancel',
    type: 'error'
  }).then(() => {
    ElMessage.success(`Critical alarm "${alarm.title}" escalated to management`)
  }).catch(() => {})
}

const viewDetails = (alarm: Alarm) => {
  ElMessage.info(`Viewing details for ${alarm.title}`)
}

const acknowledgeAllCritical = () => {
  const unacknowledged = criticalAlarms.value.filter(a => !a.acknowledged)
  if (unacknowledged.length === 0) {
    ElMessage.warning('No unacknowledged critical alarms')
    return
  }
  ElMessageBox.confirm(`Acknowledge all ${unacknowledged.length} critical alarms?`, 'Confirm', {
    confirmButtonText: 'Acknowledge All',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    unacknowledged.forEach(a => { a.acknowledged = true; a.acknowledgedBy = 'Bulk Action' })
    ElMessage.success(`Acknowledged ${unacknowledged.length} critical alarms`)
    updateCategoryChart()
  }).catch(() => {})
}

const exportReport = () => {
  ElMessage.success('Exporting critical alarms report...')
}

const openEscalationMatrix = () => {
  ElMessage.info('Opening escalation matrix...')
}

const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  ElMessage.success('Critical alarms refreshed')
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
      // 等待 DOM 渲染完成后初始化图表
      nextTick(() => {
        setTimeout(() => {
          initCharts()
        }, 100)
      })
    }, 500)
  }, 2500)
}

// 监听数据变化，更新饼图
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

.spinner-ring:nth-child(4) {
  border-left-color: #ec489a;
  animation-delay: 0.6s;
  width: 20%;
  height: 20%;
  top: 40%;
  left: 40%;
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

/* ==================== Main Dashboard Styles ==================== */
.critical-alarms-dashboard {
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
  background: linear-gradient(135deg, #fff, #ef4444);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  margin: 0 0 12px 0;
}

.critical-dot {
  width: 12px;
  height: 12px;
  background: #ef4444;
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

.stat-badge.critical .stat-dot {
  width: 8px;
  height: 8px;
  background: #ef4444;
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

.kpi-card.pulse {
  animation: borderPulse 2s infinite;
}

@keyframes borderPulse {
  0%, 100% { border-color: rgba(239, 68, 68, 0.3); }
  50% { border-color: rgba(239, 68, 68, 0.8); }
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

.critical-icon { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
.resolved-icon { background: rgba(52, 211, 153, 0.15); color: #34d399; }
.mttr-icon { background: rgba(96, 165, 250, 0.15); color: #60a5fa; }
.affected-icon { background: rgba(251, 191, 36, 0.15); color: #fbbf24; }

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

.kpi-value .unit {
  font-size: 14px;
  font-weight: normal;
  color: #64748b;
  margin-left: 4px;
}

.kpi-trend {
  font-size: 11px;
  display: block;
  margin-top: 4px;
}

.kpi-trend.up { color: #ef4444; }
.kpi-trend.down { color: #34d399; }

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
  background: #ef4444;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

.card-actions {
  display: flex;
  gap: 12px;
}

.alarm-feed {
  max-height: 450px;
  overflow-y: auto;
  padding: 8px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.alarm-feed::-webkit-scrollbar {
  display: none;
}

.alarm-item {
  display: flex;
  gap: 12px;
  padding: 16px;
  margin-bottom: 12px;
  background: rgba(239, 68, 68, 0.05);
  border-radius: 12px;
  transition: all 0.2s;
  border: 1px solid rgba(239, 68, 68, 0.15);
}

.alarm-item:hover {
  background: rgba(239, 68, 68, 0.1);
}

.alarm-indicator {
  width: 4px;
  border-radius: 2px;
}

.alarm-indicator.critical { background: #ef4444; }

.alarm-content {
  flex: 1;
}

.alarm-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  flex-wrap: wrap;
  gap: 8px;
}

.alarm-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #e2e8f0;
}

.alarm-time {
  font-size: 11px;
  color: #64748b;
}

.alarm-description {
  font-size: 13px;
  color: #94a3b8;
  margin-bottom: 12px;
}

.alarm-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.alarm-meta {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: #64748b;
}

.alarm-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.alarm-actions {
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

.affected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 16px;
}

.affected-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: rgba(239, 68, 68, 0.08);
  border-radius: 24px;
  font-size: 13px;
  color: #e2e8f0;
  border: 1px solid rgba(239, 68, 68, 0.2);
  transition: all 0.2s;
}

.affected-tag:hover {
  background: rgba(239, 68, 68, 0.15);
  transform: translateY(-1px);
}

.affected-tag.critical {
  border-color: rgba(239, 68, 68, 0.4);
}

.tag-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.tag-dot.critical { background: #ef4444; }
.tag-dot.warning { background: #f97316; }

.tag-count {
  background: rgba(239, 68, 68, 0.2);
  padding: 2px 8px;
  border-radius: 16px;
  font-size: 11px;
  font-weight: 600;
  color: #ef4444;
  min-width: 24px;
  text-align: center;
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
  .critical-alarms-dashboard {
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
  .alarm-actions {
    flex-wrap: wrap;
  }
}
</style>