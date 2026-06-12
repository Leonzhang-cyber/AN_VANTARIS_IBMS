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
  Operation, Headset, Monitor, Cpu, Connection
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing equipment health engine...',
  'Loading sensor data...',
  'Analyzing equipment condition...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedStatus = ref('all')
const selectedType = ref('all')
const detailsVisible = ref(false)
const chartRef = ref(null)
const gaugeRef = ref(null)

let healthChart: echarts.ECharts | null = null
let gaugeChart: echarts.ECharts | null = null

// Status filters
const statusOptions = [
  { value: 'all', label: 'All Status' },
  { value: 'healthy', label: 'Healthy', color: '#67C23A' },
  { value: 'warning', label: 'Warning', color: '#E6A23C' },
  { value: 'critical', label: 'Critical', color: '#F56C6C' }
]

// Type filters
const typeOptions = [
  { value: 'all', label: 'All Types' },
  { value: 'hvac', label: 'HVAC' },
  { value: 'electrical', label: 'Electrical' },
  { value: 'pump', label: 'Pump' },
  { value: 'chiller', label: 'Chiller' }
]

// Equipment health data
const equipment = ref([
  {
    id: 'EQ001', name: 'AHU-1', type: 'hvac', status: 'healthy',
    healthScore: 94, efficiency: 92, remainingLife: '2.5 years',
    lastMaintenance: '2024-01-10', nextMaintenance: '2024-02-10',
    metrics: { temperature: 22.5, vibration: 0.3, runtime: 3450 },
    trend: 'stable', alerts: 0
  },
  {
    id: 'EQ002', name: 'AHU-2', type: 'hvac', status: 'warning',
    healthScore: 72, efficiency: 78, remainingLife: '1.2 years',
    lastMaintenance: '2023-12-15', nextMaintenance: '2024-01-15',
    metrics: { temperature: 24.8, vibration: 0.7, runtime: 4120 },
    trend: 'declining', alerts: 2
  },
  {
    id: 'EQ003', name: 'Chiller-1', type: 'chiller', status: 'critical',
    healthScore: 45, efficiency: 58, remainingLife: '3 months',
    lastMaintenance: '2023-11-20', nextMaintenance: '2023-12-20',
    metrics: { temperature: 28.5, vibration: 1.2, runtime: 8900 },
    trend: 'critical', alerts: 5
  },
  {
    id: 'EQ004', name: 'VFD Pump', type: 'pump', status: 'healthy',
    healthScore: 88, efficiency: 85, remainingLife: '1.8 years',
    lastMaintenance: '2024-01-05', nextMaintenance: '2024-02-05',
    metrics: { temperature: 21.0, vibration: 0.4, runtime: 2100 },
    trend: 'stable', alerts: 0
  },
  {
    id: 'EQ005', name: 'Main Switchboard', type: 'electrical', status: 'healthy',
    healthScore: 96, efficiency: 94, remainingLife: '3.5 years',
    lastMaintenance: '2024-01-12', nextMaintenance: '2024-02-12',
    metrics: { temperature: 35.0, vibration: 0.2, runtime: 5600 },
    trend: 'stable', alerts: 0
  },
  {
    id: 'EQ006', name: 'Cooling Tower', type: 'hvac', status: 'warning',
    healthScore: 68, efficiency: 72, remainingLife: '8 months',
    lastMaintenance: '2023-12-01', nextMaintenance: '2024-01-01',
    metrics: { temperature: 26.5, vibration: 0.9, runtime: 6780 },
    trend: 'declining', alerts: 3
  }
])

// Health statistics
const healthStats = reactive({
  total: 0,
  healthy: 0,
  warning: 0,
  critical: 0,
  avgHealthScore: 0,
  avgEfficiency: 0,
  criticalAlerts: 0
})

// Gauge data for selected equipment
const selectedEquipment = ref<any>(null)

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 8,
  total: equipment.value.length
})

// Filtered equipment
const filteredEquipment = computed(() => {
  let filtered = equipment.value
  if (searchKeyword.value) {
    filtered = filtered.filter(e =>
        e.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        e.id.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(e => e.status === selectedStatus.value)
  }
  if (selectedType.value !== 'all') {
    filtered = filtered.filter(e => e.type === selectedType.value)
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
        updateStats()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  healthChart = echarts.init(chartRef.value)
  healthChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Health Score', 'Efficiency'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: equipment.value.map(e => e.name), axisLabel: { rotate: 30, interval: 0 } },
    yAxis: { type: 'value', name: 'Score (%)', min: 0, max: 100 },
    series: [
      { name: 'Health Score', type: 'bar', data: equipment.value.map(e => e.healthScore), itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top' } },
      { name: 'Efficiency', type: 'line', data: equipment.value.map(e => e.efficiency), smooth: true, lineStyle: { color: '#67C23A', width: 2 }, symbol: 'circle', symbolSize: 8 }
    ]
  })
}

const initGauge = (healthScore: number) => {
  if (!gaugeRef.value) return

  // Determine color based on health score
  let color = '#67C23A'
  if (healthScore < 50) color = '#F56C6C'
  else if (healthScore < 70) color = '#E6A23C'

  gaugeChart = echarts.init(gaugeRef.value)
  gaugeChart.setOption({
    series: [{
      type: 'gauge',
      center: ['50%', '50%'],
      radius: '70%',
      min: 0,
      max: 100,
      splitNumber: 5,
      axisLine: {
        lineStyle: {
          width: 15,
          color: [[0.5, '#F56C6C'], [0.7, '#E6A23C'], [1, '#67C23A']]
        }
      },
      pointer: { show: true, length: '60%', width: 8 },
      detail: { offsetCenter: [0, 25], valueAnimation: true, fontSize: 20 },
      title: { show: false },
      data: [{ value: healthScore, name: 'Health Score' }]
    }]
  })
}

const updateStats = () => {
  healthStats.total = equipment.value.length
  healthStats.healthy = equipment.value.filter(e => e.status === 'healthy').length
  healthStats.warning = equipment.value.filter(e => e.status === 'warning').length
  healthStats.critical = equipment.value.filter(e => e.status === 'critical').length
  healthStats.avgHealthScore = Math.round(equipment.value.reduce((sum, e) => sum + e.healthScore, 0) / equipment.value.length)
  healthStats.avgEfficiency = Math.round(equipment.value.reduce((sum, e) => sum + e.efficiency, 0) / equipment.value.length)
  healthStats.criticalAlerts = equipment.value.reduce((sum, e) => sum + e.alerts, 0)
}

const handleResize = () => {
  healthChart?.resize()
  gaugeChart?.resize()
}

// ==================== Equipment Functions ====================
const refreshData = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  initChart()
  loading.value = false
  ElMessage.success('Equipment data refreshed successfully')
}

const viewDetails = (equip: any) => {
  selectedEquipment.value = equip
  detailsVisible.value = true
  setTimeout(() => {
    initGauge(equip.healthScore)
  }, 100)
}

const scheduleMaintenance = (equip: any) => {
  ElMessage.info(`Scheduling maintenance for ${equip.name}`)
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'healthy': return '✅'
    case 'warning': return '⚠️'
    case 'critical': return '🔴'
    default: return '❓'
  }
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'healthy': return '#67C23A'
    case 'warning': return '#E6A23C'
    case 'critical': return '#F56C6C'
    default: return '#909399'
  }
}

const getTrendIcon = (trend: string) => {
  switch (trend) {
    case 'stable': return '➡️'
    case 'declining': return '📉'
    case 'critical': return '📉'
    default: return '➡️'
  }
}
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
          <span class="loading-title">Loading Equipment Health</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Predictive Maintenance - Equipment Health</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="equipment-health-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Equipment Health</h1>
        <p class="page-subtitle">Monitor real-time health status of critical equipment</p>
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
          <el-icon><Monitor /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ healthStats.total }}</div>
          <div class="stat-label">Total Equipment</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ healthStats.healthy }} Healthy</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon health-icon">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ healthStats.avgHealthScore }}%</div>
          <div class="stat-label">Avg Health Score</div>
        </div>
        <div class="stat-trend">
          <el-progress :percentage="healthStats.avgHealthScore" :stroke-width="4" :show-text="false" />
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon efficiency-icon">
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ healthStats.avgEfficiency }}%</div>
          <div class="stat-label">Avg Efficiency</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+2% this month</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon alerts-icon">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ healthStats.criticalAlerts }}</div>
          <div class="stat-label">Active Alerts</div>
        </div>
        <div class="stat-trend">
          <span class="trend-down">{{ healthStats.critical }} Critical</span>
        </div>
      </div>
    </div>

    <!-- Chart Section -->
    <div class="chart-section">
      <div class="section-header">
        <h3>Equipment Health & Efficiency Overview</h3>
        <el-button text type="primary" @click="initChart">Refresh</el-button>
      </div>
      <div ref="chartRef" class="health-chart" style="height: 320px"></div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-bar">
      <div class="filters-left">
        <div class="search-box">
          <el-input
              v-model="searchKeyword"
              placeholder="Search equipment..."
              :prefix-icon="Search"
              clearable
              style="width: 240px"
          />
        </div>
        <div class="status-filters">
          <button
              v-for="s in statusOptions"
              :key="s.value"
              class="status-chip"
              :class="{ active: selectedStatus === s.value }"
              @click="selectedStatus = s.value"
          >
            <span class="chip-dot" :style="{ background: s.color }"></span>
            <span>{{ s.label }}</span>
          </button>
        </div>
      </div>
      <div class="filters-right">
        <el-select v-model="selectedType" placeholder="Equipment Type" clearable style="width: 150px">
          <el-option v-for="t in typeOptions.slice(1)" :key="t.value" :label="t.label" :value="t.value" />
        </el-select>
      </div>
    </div>

    <!-- Equipment Grid -->
    <div class="equipment-grid">
      <div
          v-for="equip in filteredEquipment"
          :key="equip.id"
          class="equipment-card"
          :class="equip.status"
          @click="viewDetails(equip)"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="equipment-type">
            <span class="type-icon">{{ equip.type === 'hvac' ? '❄️' : equip.type === 'electrical' ? '⚡' : equip.type === 'pump' ? '💧' : '🔧' }}</span>
            <span class="type-name">{{ equip.type.toUpperCase() }}</span>
          </div>
          <div class="health-score" :style="{ background: getStatusColor(equip.status) }">
            {{ equip.healthScore }}%
          </div>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <h4 class="equipment-name">{{ equip.name }}</h4>

          <!-- Health Bar -->
          <div class="health-bar">
            <div class="bar-fill" :style="{ width: equip.healthScore + '%', background: getStatusColor(equip.status) }"></div>
          </div>

          <!-- Key Metrics -->
          <div class="key-metrics">
            <div class="metric">
              <span class="metric-label">Efficiency</span>
              <span class="metric-value">{{ equip.efficiency }}%</span>
            </div>
            <div class="metric">
              <span class="metric-label">Remaining Life</span>
              <span class="metric-value">{{ equip.remainingLife }}</span>
            </div>
            <div class="metric">
              <span class="metric-label">Trend</span>
              <span class="metric-value">{{ getTrendIcon(equip.trend) }} {{ equip.trend }}</span>
            </div>
          </div>

          <!-- Maintenance Info -->
          <div class="maintenance-info">
            <div class="info-item">
              <span class="info-label">Last Maintenance:</span>
              <span class="info-value">{{ equip.lastMaintenance }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Next Due:</span>
              <span class="info-value" :class="{ overdue: new Date(equip.nextMaintenance) < new Date() }">
                {{ equip.nextMaintenance }}
              </span>
            </div>
          </div>

          <!-- Status Badge -->
          <div class="status-badge" :style="{ background: getStatusColor(equip.status) + '20', color: getStatusColor(equip.status) }">
            {{ getStatusIcon(equip.status) }} {{ equip.status.toUpperCase() }}
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="alert-count" v-if="equip.alerts > 0">
            <el-icon><Warning /></el-icon>
            <span>{{ equip.alerts }} alerts</span>
          </div>
          <div class="card-actions">
            <el-button size="small" @click.stop="viewDetails(equip)">Details</el-button>
            <el-button size="small" type="primary" @click.stop="scheduleMaintenance(equip)">Schedule</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredEquipment.length === 0" class="empty-state">
      <el-empty description="No equipment found">
        <el-button type="primary">Reset Filters</el-button>
      </el-empty>
    </div>

    <!-- Pagination -->
    <div v-if="filteredEquipment.length > 0" class="pagination-wrapper">
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

    <!-- Equipment Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="selectedEquipment?.name" width="650px">
      <div class="dialog-content">
        <div class="gauge-container">
          <div ref="gaugeRef" class="gauge-chart" style="height: 250px"></div>
        </div>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="Equipment ID">{{ selectedEquipment?.id }}</el-descriptions-item>
          <el-descriptions-item label="Type">{{ selectedEquipment?.type?.toUpperCase() }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <span class="status-text" :style="{ color: getStatusColor(selectedEquipment?.status) }">
              {{ getStatusIcon(selectedEquipment?.status) }} {{ selectedEquipment?.status?.toUpperCase() }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="Health Score">{{ selectedEquipment?.healthScore }}%</el-descriptions-item>
          <el-descriptions-item label="Efficiency">{{ selectedEquipment?.efficiency }}%</el-descriptions-item>
          <el-descriptions-item label="Remaining Life">{{ selectedEquipment?.remainingLife }}</el-descriptions-item>
          <el-descriptions-item label="Last Maintenance">{{ selectedEquipment?.lastMaintenance }}</el-descriptions-item>
          <el-descriptions-item label="Next Maintenance">{{ selectedEquipment?.nextMaintenance }}</el-descriptions-item>
          <el-descriptions-item label="Runtime Hours">{{ selectedEquipment?.metrics?.runtime?.toLocaleString() }}</el-descriptions-item>
          <el-descriptions-item label="Temperature">{{ selectedEquipment?.metrics?.temperature }}°C</el-descriptions-item>
          <el-descriptions-item label="Vibration">{{ selectedEquipment?.metrics?.vibration }} mm/s</el-descriptions-item>
          <el-descriptions-item label="Active Alerts">{{ selectedEquipment?.alerts }}</el-descriptions-item>
        </el-descriptions>

        <div v-if="selectedEquipment?.status === 'warning' || selectedEquipment?.status === 'critical'" class="recommendation">
          <el-alert
              :title="selectedEquipment?.status === 'critical' ? 'Immediate action required!' : 'Maintenance recommended soon'"
              :type="selectedEquipment?.status === 'critical' ? 'error' : 'warning'"
              show-icon
              :closable="false"
          >
            <template #default>
              <p v-if="selectedEquipment?.status === 'critical'">
                Equipment health is critical. Schedule maintenance immediately to prevent failure.
              </p>
              <p v-else>
                Equipment efficiency is declining. Schedule preventive maintenance within 7 days.
              </p>
            </template>
          </el-alert>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
        <el-button type="primary" @click="scheduleMaintenance(selectedEquipment)">Schedule Maintenance</el-button>
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
.equipment-health-container {
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

.health-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.efficiency-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.alerts-icon {
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

.trend-down {
  color: #f56c6c;
}

/* Chart Section */
.chart-section {
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
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.health-chart {
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

.status-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.status-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 40px;
  font-size: 13px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s ease;
}

.status-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.status-chip.active {
  background: #409eff;
  border-color: #409eff;
  color: white;
}

.chip-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.filters-right {
  display: flex;
  gap: 12px;
}

/* Equipment Grid */
.equipment-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.equipment-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.equipment-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.equipment-card.critical {
  border-left: 4px solid #F56C6C;
}

.equipment-card.warning {
  border-left: 4px solid #E6A23C;
}

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 0 20px;
}

.equipment-type {
  display: flex;
  align-items: center;
  gap: 8px;
}

.type-icon {
  font-size: 20px;
}

.type-name {
  font-size: 12px;
  font-weight: 600;
  color: #409eff;
  background: #e6f7ff;
  padding: 4px 8px;
  border-radius: 12px;
}

.health-score {
  font-size: 20px;
  font-weight: 700;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
}

/* Card Body */
.card-body {
  padding: 16px 20px;
}

.equipment-name {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 16px 0;
}

.health-bar {
  height: 8px;
  background: #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 16px;
}

.health-bar .bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.key-metrics {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  padding: 12px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.metric {
  text-align: center;
  flex: 1;
}

.metric-label {
  font-size: 11px;
  color: #909399;
  display: block;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
}

.maintenance-info {
  margin-bottom: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  margin-bottom: 6px;
}

.info-label {
  color: #909399;
}

.info-value {
  color: #1e293b;
  font-weight: 500;
}

.info-value.overdue {
  color: #f56c6c;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

/* Card Footer */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px 16px 20px;
  border-top: 1px solid #f0f0f0;
  background: #fafbfc;
}

.alert-count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #f56c6c;
}

.card-actions {
  display: flex;
  gap: 8px;
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

/* Dialog Styles */
.dialog-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.gauge-container {
  display: flex;
  justify-content: center;
}

.gauge-chart {
  width: 100%;
  max-width: 350px;
}

.status-text {
  font-weight: 600;
}

.recommendation {
  margin-top: 10px;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .equipment-grid {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }
}

@media (max-width: 768px) {
  .equipment-health-container {
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

  .status-filters {
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

  .equipment-grid {
    grid-template-columns: 1fr;
  }

  .key-metrics {
    flex-direction: column;
    gap: 8px;
  }
}
</style>