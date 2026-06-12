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
  Sunny, ColdDrink, WindPower
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing HVAC optimization engine...',
  'Analyzing system performance...',
  'Calculating optimization strategies...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const selectedZone = ref('all')
const selectedTimeRange = ref('week')
const detailsVisible = ref(false)
const chartRef = ref(null)
const savingsChartRef = ref(null)

let efficiencyChart: echarts.ECharts | null = null
let savingsChart: echarts.ECharts | null = null

// Zone options
const zoneOptions = [
  { value: 'all', label: 'All Zones' },
  { value: 'zone_a', label: 'Zone A - Office' },
  { value: 'zone_b', label: 'Zone B - Meeting Rooms' },
  { value: 'zone_c', label: 'Zone C - Common Areas' },
  { value: 'zone_d', label: 'Zone D - Executive Suite' }
]

// Time range options
const timeRangeOptions = [
  { value: 'day', label: 'Today' },
  { value: 'week', label: 'This Week' },
  { value: 'month', label: 'This Month' },
  { value: 'year', label: 'This Year' }
]

// HVAC performance data
const performanceData = ref({
  zones: [
    { name: 'Zone A', currentTemp: 22.5, setpoint: 22, efficiency: 92, savings: 1250, occupancy: 85 },
    { name: 'Zone B', currentTemp: 23.0, setpoint: 22, efficiency: 88, savings: 980, occupancy: 72 },
    { name: 'Zone C', currentTemp: 22.8, setpoint: 22, efficiency: 85, savings: 750, occupancy: 45 },
    { name: 'Zone D', currentTemp: 21.5, setpoint: 22, efficiency: 95, savings: 2100, occupancy: 90 }
  ],
  hourlyData: [
    { hour: '00:00', temp: 21.5, setpoint: 22, energy: 45 },
    { hour: '02:00', temp: 21.2, setpoint: 22, energy: 42 },
    { hour: '04:00', temp: 21.0, setpoint: 22, energy: 40 },
    { hour: '06:00', temp: 21.3, setpoint: 22, energy: 48 },
    { hour: '08:00', temp: 22.0, setpoint: 22, energy: 65 },
    { hour: '10:00', temp: 22.8, setpoint: 22, energy: 78 },
    { hour: '12:00', temp: 23.2, setpoint: 22, energy: 85 },
    { hour: '14:00', temp: 23.5, setpoint: 22, energy: 88 },
    { hour: '16:00', temp: 23.2, setpoint: 22, energy: 82 },
    { hour: '18:00', temp: 22.8, setpoint: 22, energy: 75 },
    { hour: '20:00', temp: 22.0, setpoint: 22, energy: 62 },
    { hour: '22:00', temp: 21.5, setpoint: 22, energy: 52 }
  ],
  recommendations: [
    { id: 1, title: 'Optimize Setpoints', description: 'Adjust temperature setpoints based on occupancy patterns', savings: 2450, priority: 'high', effort: 'low' },
    { id: 2, title: 'Schedule Optimization', description: 'Modify HVAC schedule to match building occupancy', savings: 1850, priority: 'high', effort: 'medium' },
    { id: 3, title: 'VFD Speed Control', description: 'Implement variable frequency drive optimization', savings: 3200, priority: 'medium', effort: 'high' },
    { id: 4, title: 'Demand Control Ventilation', description: 'Adjust fresh air intake based on CO2 levels', savings: 1200, priority: 'medium', effort: 'medium' }
  ]
})

// Optimization statistics
const optStats = reactive({
  totalSavings: 8750,
  efficiency: 90,
  energyReduction: 15.2,
  co2Reduction: 12.5,
  activeZones: 4,
  optimizedZones: 3
})

// Savings by zone
const savingsByZone = ref([
  { zone: 'Zone A', current: 18500, optimized: 17250 },
  { zone: 'Zone B', current: 14200, optimized: 13220 },
  { zone: 'Zone C', current: 9800, optimized: 9050 },
  { zone: 'Zone D', current: 25600, optimized: 23500 }
])

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 4,
  total: performanceData.value.recommendations.length
})

const paginatedRecommendations = computed(() => {
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return performanceData.value.recommendations.slice(start, end)
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
        initSavingsChart()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  efficiencyChart = echarts.init(chartRef.value)
  efficiencyChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Actual Temperature', 'Setpoint', 'Energy (kWh)'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: performanceData.value.hourlyData.map(d => d.hour) },
    yAxis: [
      { type: 'value', name: 'Temperature (°C)', min: 18, max: 26 },
      { type: 'value', name: 'Energy (kWh)', min: 0, max: 120 }
    ],
    series: [
      { name: 'Actual Temperature', type: 'line', data: performanceData.value.hourlyData.map(d => d.temp), smooth: true, lineStyle: { color: '#F56C6C', width: 2 }, symbol: 'circle', symbolSize: 6 },
      { name: 'Setpoint', type: 'line', data: performanceData.value.hourlyData.map(d => d.setpoint), smooth: true, lineStyle: { color: '#67C23A', width: 2, type: 'dashed' }, symbol: 'diamond', symbolSize: 6 },
      { name: 'Energy (kWh)', type: 'bar', data: performanceData.value.hourlyData.map(d => d.energy), itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] }, yAxisIndex: 1 }
    ]
  })
}

const initSavingsChart = () => {
  if (!savingsChartRef.value) return

  savingsChart = echarts.init(savingsChartRef.value)
  savingsChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Current', 'Optimized'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: savingsByZone.value.map(s => s.zone) },
    yAxis: { type: 'value', name: 'Energy (kWh)' },
    series: [
      { name: 'Current', type: 'bar', data: savingsByZone.value.map(s => s.current), itemStyle: { color: '#F56C6C', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top' } },
      { name: 'Optimized', type: 'bar', data: savingsByZone.value.map(s => s.optimized), itemStyle: { color: '#67C23A', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top' } }
    ]
  })
}

const handleResize = () => {
  efficiencyChart?.resize()
  savingsChart?.resize()
}

// ==================== Optimization Functions ====================
const refreshData = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  loading.value = false
  ElMessage.success('Optimization data refreshed successfully')
}

const applyOptimization = async (rec: any) => {
  await ElMessageBox.confirm(
      `Apply optimization: ${rec.title}?`,
      'Confirm Apply',
      {
        confirmButtonText: 'Apply',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  )

  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))
  ElMessage.success(`Optimization "${rec.title}" applied successfully`)
  loading.value = false
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

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'high': return '#F56C6C'
    case 'medium': return '#E6A23C'
    case 'low': return '#67C23A'
    default: return '#909399'
  }
}

const getEffortIcon = (effort: string) => {
  switch (effort) {
    case 'low': return '🟢'
    case 'medium': return '🟡'
    case 'high': return '🔴'
    default: return '⚪'
  }
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
          <span class="loading-title">Loading HVAC Optimization</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Energy Optimization - HVAC Optimization</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="hvac-optimization-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">HVAC Optimization</h1>
        <p class="page-subtitle">AI-powered HVAC system optimization for maximum efficiency</p>
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
        <div class="stat-icon savings-icon">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">${{ optStats.totalSavings.toLocaleString() }}</div>
          <div class="stat-label">Annual Savings</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+15% vs last year</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon efficiency-icon">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ optStats.efficiency }}%</div>
          <div class="stat-label">System Efficiency</div>
        </div>
        <div class="stat-trend">
          <el-progress :percentage="optStats.efficiency" :stroke-width="4" :show-text="false" />
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon energy-icon">
          <el-icon><Lightning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ optStats.energyReduction }}%</div>
          <div class="stat-label">Energy Reduction</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">Target: 20%</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon co2-icon">
          <el-icon><Sunny /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ optStats.co2Reduction }}%</div>
          <div class="stat-label">CO₂ Reduction</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ optStats.optimizedZones }}/{{ optStats.activeZones }} Zones Optimized</span>
        </div>
      </div>
    </div>

    <!-- Zone Performance Cards -->
    <div class="zones-section">
      <h3>Zone Performance</h3>
      <div class="zones-grid">
        <div
            v-for="zone in performanceData.zones"
            :key="zone.name"
            class="zone-card"
            @click="viewDetails(zone)"
        >
          <div class="zone-header">
            <span class="zone-name">{{ zone.name }}</span>
            <span class="zone-efficiency" :style="{ color: zone.efficiency > 90 ? '#67C23A' : zone.efficiency > 80 ? '#E6A23C' : '#F56C6C' }">
              {{ zone.efficiency }}% efficiency
            </span>
          </div>
          <div class="zone-metrics">
            <div class="metric">
              <span class="metric-label">Current Temp</span>
              <span class="metric-value">{{ zone.currentTemp }}°C</span>
            </div>
            <div class="metric">
              <span class="metric-label">Setpoint</span>
              <span class="metric-value">{{ zone.setpoint }}°C</span>
            </div>
            <div class="metric">
              <span class="metric-label">Savings</span>
              <span class="metric-value">${{ zone.savings.toLocaleString() }}</span>
            </div>
            <div class="metric">
              <span class="metric-label">Occupancy</span>
              <span class="metric-value">{{ zone.occupancy }}%</span>
            </div>
          </div>
          <el-progress :percentage="zone.efficiency" :stroke-width="6" :color="zone.efficiency > 90 ? '#67C23A' : zone.efficiency > 80 ? '#E6A23C' : '#F56C6C'" />
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-row">
      <div class="chart-section">
        <div class="section-header">
          <h3>Temperature & Energy Trend</h3>
          <el-button text type="primary" @click="initChart">Refresh</el-button>
        </div>
        <div ref="chartRef" class="efficiency-chart" style="height: 320px"></div>
      </div>

      <div class="chart-section">
        <div class="section-header">
          <h3>Energy Savings by Zone</h3>
          <el-button text type="primary" @click="initSavingsChart">Refresh</el-button>
        </div>
        <div ref="savingsChartRef" class="savings-chart" style="height: 320px"></div>
      </div>
    </div>

    <!-- Optimization Recommendations -->
    <div class="recommendations-section">
      <div class="section-header">
        <h3>AI-Powered Recommendations</h3>
        <el-tag type="info" size="small">Estimated annual savings: ${{ performanceData.recommendations.reduce((sum, r) => sum + r.savings, 0).toLocaleString() }}</el-tag>
      </div>

      <div class="recommendations-grid">
        <div
            v-for="rec in paginatedRecommendations"
            :key="rec.id"
            class="recommendation-card"
        >
          <div class="rec-header">
            <div class="rec-title">
              <span class="rec-icon">💡</span>
              <h4>{{ rec.title }}</h4>
            </div>
            <div class="rec-badges">
              <span class="priority-badge" :style="{ background: getPriorityColor(rec.priority) }">
                {{ rec.priority.toUpperCase() }}
              </span>
              <span class="effort-badge">
                {{ getEffortIcon(rec.effort) }} {{ rec.effort }} effort
              </span>
            </div>
          </div>
          <p class="rec-description">{{ rec.description }}</p>
          <div class="rec-footer">
            <div class="savings">
              <span class="savings-label">Estimated Savings:</span>
              <span class="savings-value">${{ rec.savings.toLocaleString() }}/year</span>
            </div>
            <el-button type="primary" size="small" @click="applyOptimization(rec)">Apply</el-button>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[4, 8, 12]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- Zone Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="selectedZoneDetail?.name" width="550px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Current Temperature">{{ selectedZoneDetail?.currentTemp }}°C</el-descriptions-item>
        <el-descriptions-item label="Setpoint">{{ selectedZoneDetail?.setpoint }}°C</el-descriptions-item>
        <el-descriptions-item label="Efficiency">{{ selectedZoneDetail?.efficiency }}%</el-descriptions-item>
        <el-descriptions-item label="Annual Savings">${{ selectedZoneDetail?.savings?.toLocaleString() }}</el-descriptions-item>
        <el-descriptions-item label="Occupancy">{{ selectedZoneDetail?.occupancy }}%</el-descriptions-item>
        <el-descriptions-item label="Optimization Status">
          <el-tag :type="selectedZoneDetail?.efficiency > 90 ? 'success' : selectedZoneDetail?.efficiency > 80 ? 'warning' : 'danger'" size="small">
            {{ selectedZoneDetail?.efficiency > 90 ? 'Optimized' : selectedZoneDetail?.efficiency > 80 ? 'Partial' : 'Needs Attention' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
      <div class="recommendation-note">
        <el-alert
            :title="selectedZoneDetail?.efficiency > 90 ? 'Zone performing well' : 'Recommendations available'"
            :type="selectedZoneDetail?.efficiency > 90 ? 'success' : 'warning'"
            show-icon
            :closable="false"
        >
          <template #default>
            <p v-if="selectedZoneDetail?.efficiency <= 90">
              Consider adjusting setpoint based on occupancy patterns to improve efficiency.
            </p>
            <p v-else>
              Current settings are optimal. Continue monitoring for sustained performance.
            </p>
          </template>
        </el-alert>
      </div>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
        <el-button type="primary" @click="detailsVisible = false">Apply Optimization</el-button>
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
.hvac-optimization-container {
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

.savings-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.efficiency-icon {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #409eff;
}

.energy-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.co2-icon {
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

/* Zones Section */
.zones-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.zones-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 16px 0;
}

.zones-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.zone-card {
  background: #fafbfc;
  border-radius: 16px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.zone-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.zone-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.zone-name {
  font-weight: 600;
  color: #1e293b;
}

.zone-efficiency {
  font-size: 12px;
  font-weight: 500;
}

.zone-metrics {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
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

.efficiency-chart,
.savings-chart {
  width: 100%;
}

/* Recommendations Section */
.recommendations-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.recommendation-card {
  background: #fafbfc;
  border-radius: 16px;
  padding: 16px;
  transition: all 0.2s ease;
}

.recommendation-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.rec-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 8px;
}

.rec-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rec-icon {
  font-size: 18px;
}

.rec-title h4 {
  font-size: 15px;
  font-weight: 600;
  margin: 0;
  color: #1e293b;
}

.rec-badges {
  display: flex;
  gap: 8px;
}

.priority-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 600;
  color: white;
}

.effort-badge {
  padding: 4px 8px;
  background: #e4e7ed;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 500;
  color: #606266;
}

.rec-description {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.rec-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.savings {
  display: flex;
  gap: 8px;
  font-size: 12px;
}

.savings-label {
  color: #909399;
}

.savings-value {
  font-weight: 600;
  color: #67c23a;
}

/* Pagination */
.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

/* Dialog */
.recommendation-note {
  margin-top: 16px;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-row {
    grid-template-columns: 1fr;
  }

  .recommendations-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .hvac-optimization-container {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .zones-grid {
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

  .rec-header {
    flex-direction: column;
  }
}
</style>