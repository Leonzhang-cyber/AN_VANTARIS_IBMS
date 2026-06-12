<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Refresh, Setting, User, Clock,
  Warning, CircleCheck, TrendCharts, DataLine,
  Star, Share, CopyDocument, Delete, Mic,
  Picture, Document, Upload, Download,
  MagicStick, ChatDotRound, Message, Service,
  Search, Edit, Plus, VideoPlay, VideoPause,
  Operation, Headset, Monitor, Cpu, Connection,
  Sunny, Lightning, Timer, Wallet
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing demand response engine...',
  'Analyzing peak demand patterns...',
  'Calculating response strategies...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const selectedEvent = ref('')
const eventDetailsVisible = ref(false)
const chartRef = ref(null)
const loadChartRef = ref(null)

let demandChart: echarts.ECharts | null = null
let loadChart: echarts.ECharts | null = null

// Demand response events
const events = ref([
  {
    id: 'DR001', name: 'Peak Demand Reduction', status: 'active', type: 'curtailment',
    startTime: '2024-01-15 14:00:00', endTime: '2024-01-15 16:00:00',
    targetReduction: 250, achievedReduction: 185, participation: 74,
    incentive: 1250, participants: 8, savings: 3420
  },
  {
    id: 'DR002', name: 'Grid Stress Response', status: 'scheduled', type: 'load_shifting',
    startTime: '2024-01-16 15:00:00', endTime: '2024-01-16 18:00:00',
    targetReduction: 300, achievedReduction: 0, participation: 0,
    incentive: 1500, participants: 6, savings: 0
  },
  {
    id: 'DR003', name: 'Price Spike Response', status: 'completed', type: 'load_shedding',
    startTime: '2024-01-14 13:00:00', endTime: '2024-01-14 15:00:00',
    targetReduction: 200, achievedReduction: 210, participation: 105,
    incentive: 1800, participants: 10, savings: 4560
  },
  {
    id: 'DR004', name: 'Emergency Load Reduction', status: 'completed', type: 'emergency',
    startTime: '2024-01-12 16:00:00', endTime: '2024-01-12 18:00:00',
    targetReduction: 350, achievedReduction: 320, participation: 91,
    incentive: 2800, participants: 12, savings: 6780
  }
])

// Load data by hour
const loadData = ref([
  { hour: '00:00', load: 320, optimized: 320 },
  { hour: '01:00', load: 280, optimized: 280 },
  { hour: '02:00', load: 250, optimized: 250 },
  { hour: '03:00', load: 240, optimized: 240 },
  { hour: '04:00', load: 245, optimized: 245 },
  { hour: '05:00', load: 280, optimized: 280 },
  { hour: '06:00', load: 350, optimized: 350 },
  { hour: '07:00', load: 420, optimized: 420 },
  { hour: '08:00', load: 520, optimized: 520 },
  { hour: '09:00', load: 580, optimized: 580 },
  { hour: '10:00', load: 620, optimized: 620 },
  { hour: '11:00', load: 650, optimized: 650 },
  { hour: '12:00', load: 680, optimized: 680 },
  { hour: '13:00', load: 720, optimized: 650 },
  { hour: '14:00', load: 780, optimized: 560 },
  { hour: '15:00', load: 750, optimized: 540 },
  { hour: '16:00', load: 700, optimized: 620 },
  { hour: '17:00', load: 650, optimized: 650 },
  { hour: '18:00', load: 580, optimized: 580 },
  { hour: '19:00', load: 520, optimized: 520 },
  { hour: '20:00', load: 480, optimized: 480 },
  { hour: '21:00', load: 420, optimized: 420 },
  { hour: '22:00', load: 380, optimized: 380 },
  { hour: '23:00', load: 350, optimized: 350 }
])

// Demand response statistics
const drStats = reactive({
  totalEvents: 8,
  activeEvents: 1,
  completedEvents: 7,
  totalSavings: 24580,
  totalIncentives: 12450,
  avgParticipation: 86,
  peakReduction: 320
})

// Savings by month
const savingsByMonth = ref([
  { month: 'Jul', savings: 1850 },
  { month: 'Aug', savings: 2100 },
  { month: 'Sep', savings: 1950 },
  { month: 'Oct', savings: 2250 },
  { month: 'Nov', savings: 2450 },
  { month: 'Dec', savings: 2680 },
  { month: 'Jan', savings: 2890 }
])

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
        initLoadChart()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  demandChart = echarts.init(chartRef.value)
  demandChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Savings ($)'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: savingsByMonth.value.map(s => s.month) },
    yAxis: { type: 'value', name: 'Savings ($)' },
    series: [{
      name: 'Savings ($)',
      type: 'line',
      data: savingsByMonth.value.map(s => s.savings),
      smooth: true,
      lineStyle: { color: '#67C23A', width: 3 },
      areaStyle: { opacity: 0.1, color: '#67C23A' },
      symbol: 'circle',
      symbolSize: 8,
      label: { show: true, position: 'top' }
    }]
  })
}

const initLoadChart = () => {
  if (!loadChartRef.value) return

  loadChart = echarts.init(loadChartRef.value)
  loadChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Normal Load', 'With Demand Response'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: loadData.value.map(d => d.hour), axisLabel: { rotate: 45, interval: 2 } },
    yAxis: { type: 'value', name: 'Load (kW)' },
    series: [
      { name: 'Normal Load', type: 'line', data: loadData.value.map(d => d.load), smooth: true, lineStyle: { color: '#F56C6C', width: 2 }, symbol: 'circle', symbolSize: 4 },
      { name: 'With Demand Response', type: 'line', data: loadData.value.map(d => d.optimized), smooth: true, lineStyle: { color: '#67C23A', width: 2 }, areaStyle: { opacity: 0.1, color: '#67C23A' }, symbol: 'diamond', symbolSize: 4 }
    ]
  })
}

const handleResize = () => {
  demandChart?.resize()
  loadChart?.resize()
}

// ==================== Demand Response Functions ====================
const refreshData = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  loading.value = false
  ElMessage.success('Demand response data refreshed successfully')
}

const joinEvent = async (event: any) => {
  await ElMessageBox.confirm(
      `Join demand response event: ${event.name}?`,
      'Confirm Participation',
      {
        confirmButtonText: 'Join',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  )

  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))
  ElMessage.success(`Successfully joined ${event.name}`)
  loading.value = false
}

const viewEventDetails = (event: any) => {
  selectedEventDetail.value = event
  eventDetailsVisible.value = true
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'active': return '#F56C6C'
    case 'scheduled': return '#E6A23C'
    case 'completed': return '#67C23A'
    default: return '#909399'
  }
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'active': return '🔴'
    case 'scheduled': return '🟡'
    case 'completed': return '🟢'
    default: return '⚪'
  }
}

const getTypeIcon = (type: string) => {
  switch (type) {
    case 'curtailment': return '📉'
    case 'load_shifting': return '🔄'
    case 'load_shedding': return '⚡'
    case 'emergency': return '🚨'
    default: return '📊'
  }
}

const selectedEventDetail = ref<any>(null)
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
          <span class="loading-title">Loading Demand Response</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Energy Optimization - Demand Response</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="demand-response-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Demand Response</h1>
        <p class="page-subtitle">Participate in demand response events to reduce peak load and earn incentives</p>
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
        <div class="stat-icon events-icon">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ drStats.totalEvents }}</div>
          <div class="stat-label">Total Events</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ drStats.activeEvents }} Active</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon savings-icon">
          <el-icon><Wallet /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">${{ (drStats.totalSavings / 1000).toFixed(1) }}K</div>
          <div class="stat-label">Total Savings</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+23% vs last year</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon incentives-icon">
          <el-icon><Star /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">${{ (drStats.totalIncentives / 1000).toFixed(1) }}K</div>
          <div class="stat-label">Incentives Earned</div>
        </div>
        <div class="stat-trend">
          <el-progress :percentage="drStats.avgParticipation" :stroke-width="4" :show-text="false" />
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon reduction-icon">
          <el-icon><Lightning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ drStats.peakReduction }} kW</div>
          <div class="stat-label">Peak Reduction</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ drStats.avgParticipation }}% Participation</span>
        </div>
      </div>
    </div>

    <!-- Active Events Section -->
    <div class="active-events-section">
      <div class="section-header">
        <h3>Active & Upcoming Events</h3>
        <el-tag type="danger" size="small">{{ events.filter(e => e.status === 'active').length }} Active Now</el-tag>
      </div>

      <div class="events-grid">
        <div
            v-for="event in events"
            :key="event.id"
            class="event-card"
            :class="event.status"
        >
          <div class="event-header">
            <div class="event-type">
              <span class="type-icon">{{ getTypeIcon(event.type) }}</span>
              <span class="type-name">{{ event.type.replace('_', ' ').toUpperCase() }}</span>
            </div>
            <div class="event-status" :style="{ color: getStatusColor(event.status) }">
              {{ getStatusIcon(event.status) }} {{ event.status.toUpperCase() }}
            </div>
          </div>

          <h4 class="event-name">{{ event.name }}</h4>

          <div class="event-time">
            <el-icon><Clock /></el-icon>
            {{ event.startTime }} - {{ event.endTime }}
          </div>

          <div class="event-metrics">
            <div class="metric">
              <span class="metric-label">Target Reduction</span>
              <span class="metric-value">{{ event.targetReduction }} kW</span>
            </div>
            <div class="metric">
              <span class="metric-label">Achieved</span>
              <span class="metric-value" :class="{ achieved: event.achievedReduction >= event.targetReduction }">
                {{ event.achievedReduction }} kW
              </span>
            </div>
            <div class="metric">
              <span class="metric-label">Incentive</span>
              <span class="metric-value">${{ event.incentive.toLocaleString() }}</span>
            </div>
            <div class="metric">
              <span class="metric-label">Participants</span>
              <span class="metric-value">{{ event.participants }}</span>
            </div>
          </div>

          <el-progress
              :percentage="event.participation"
              :stroke-width="8"
              :color="event.participation >= 100 ? '#67C23A' : '#E6A23C'"
          />

          <div class="event-footer">
            <el-button
                v-if="event.status === 'active' || event.status === 'scheduled'"
                type="primary"
                size="small"
                @click="joinEvent(event)"
            >
              Join Event
            </el-button>
            <el-button size="small" @click="viewEventDetails(event)">Details</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-row">
      <div class="chart-section">
        <div class="section-header">
          <h3>Monthly Savings Trend</h3>
          <el-button text type="primary" @click="initChart">Refresh</el-button>
        </div>
        <div ref="chartRef" class="savings-chart" style="height: 300px"></div>
      </div>

      <div class="chart-section">
        <div class="section-header">
          <h3>Load Profile - Demand Response Impact</h3>
          <el-button text type="primary" @click="initLoadChart">Refresh</el-button>
        </div>
        <div ref="loadChartRef" class="load-chart" style="height: 300px"></div>
      </div>
    </div>

    <!-- Benefits Summary -->
    <div class="benefits-section">
      <div class="section-header">
        <h3>Program Benefits</h3>
      </div>
      <div class="benefits-grid">
        <div class="benefit-card">
          <div class="benefit-icon">💰</div>
          <div class="benefit-content">
            <h4>Financial Incentives</h4>
            <p>Earn ${{ (drStats.totalIncentives / 1000).toFixed(0) }}K in incentives from participation</p>
          </div>
        </div>
        <div class="benefit-card">
          <div class="benefit-icon">🌱</div>
          <div class="benefit-content">
            <h4>Environmental Impact</h4>
            <p>Reduced {{ Math.round(drStats.peakReduction * 0.4) }} tons of CO₂ emissions</p>
          </div>
        </div>
        <div class="benefit-card">
          <div class="benefit-icon">⚡</div>
          <div class="benefit-content">
            <h4>Grid Reliability</h4>
            <p>Helped prevent {{ drStats.activeEvents + drStats.completedEvents }} grid stress events</p>
          </div>
        </div>
        <div class="benefit-card">
          <div class="benefit-icon">📈</div>
          <div class="benefit-content">
            <h4>ROI Performance</h4>
            <p>Average payback period of 18 months on DR investments</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Event Details Dialog -->
    <el-dialog v-model="eventDetailsVisible" :title="selectedEventDetail?.name" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Event ID">{{ selectedEventDetail?.id }}</el-descriptions-item>
        <el-descriptions-item label="Type">{{ selectedEventDetail?.type?.replace('_', ' ')?.toUpperCase() }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <span :style="{ color: getStatusColor(selectedEventDetail?.status) }">
            {{ selectedEventDetail?.status?.toUpperCase() }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="Duration">
          {{ selectedEventDetail?.startTime }} - {{ selectedEventDetail?.endTime }}
        </el-descriptions-item>
        <el-descriptions-item label="Target Reduction">{{ selectedEventDetail?.targetReduction }} kW</el-descriptions-item>
        <el-descriptions-item label="Achieved Reduction">{{ selectedEventDetail?.achievedReduction }} kW</el-descriptions-item>
        <el-descriptions-item label="Participation Rate">{{ selectedEventDetail?.participation }}%</el-descriptions-item>
        <el-descriptions-item label="Incentive Earned">${{ selectedEventDetail?.incentive.toLocaleString() }}</el-descriptions-item>
        <el-descriptions-item label="Total Savings">${{ selectedEventDetail?.savings.toLocaleString() }}</el-descriptions-item>
        <el-descriptions-item label="Participants">{{ selectedEventDetail?.participants }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="eventDetailsVisible = false">Close</el-button>
        <el-button v-if="selectedEventDetail?.status !== 'completed'" type="primary" @click="joinEvent(selectedEventDetail)">
          Join Event
        </el-button>
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
.demand-response-container {
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

.events-icon {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #409eff;
}

.savings-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.incentives-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.reduction-icon {
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
}

.trend-up {
  color: #67c23a;
}

/* Active Events Section */
.active-events-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.events-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.event-card {
  background: #fafbfc;
  border-radius: 16px;
  padding: 16px;
  transition: all 0.2s ease;
  border-left: 4px solid;
}

.event-card.active {
  border-left-color: #f56c6c;
}

.event-card.scheduled {
  border-left-color: #e6a23c;
}

.event-card.completed {
  border-left-color: #67c23a;
}

.event-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.event-type {
  display: flex;
  align-items: center;
  gap: 6px;
}

.type-icon {
  font-size: 14px;
}

.type-name {
  font-size: 11px;
  font-weight: 600;
  color: #409eff;
  background: #e6f7ff;
  padding: 2px 8px;
  border-radius: 10px;
}

.event-status {
  font-size: 11px;
  font-weight: 600;
}

.event-name {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.event-time {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
  margin-bottom: 12px;
}

.event-metrics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 12px;
  padding: 12px 0;
  border-top: 1px solid #e4e7ed;
  border-bottom: 1px solid #e4e7ed;
}

.metric {
  text-align: center;
}

.metric-label {
  font-size: 11px;
  color: #909399;
  display: block;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.metric-value.achieved {
  color: #67c23a;
}

.event-footer {
  display: flex;
  gap: 8px;
  margin-top: 12px;
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

.savings-chart,
.load-chart {
  width: 100%;
}

/* Benefits Section */
.benefits-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.benefits-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 16px;
}

.benefit-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #fafbfc;
  border-radius: 16px;
  transition: all 0.2s ease;
}

.benefit-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.benefit-icon {
  font-size: 32px;
}

.benefit-content h4 {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: #1e293b;
}

.benefit-content p {
  font-size: 12px;
  color: #64748b;
  margin: 0;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-row {
    grid-template-columns: 1fr;
  }

  .events-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
}

@media (max-width: 768px) {
  .demand-response-container {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    text-align: center;
  }

  .header-right {
    width: 100%;
    justify-content: center;
  }

  .event-metrics {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .benefits-grid {
    grid-template-columns: 1fr;
  }
}
</style>