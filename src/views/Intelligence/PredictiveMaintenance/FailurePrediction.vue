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
  'Initializing prediction engine...',
  'Analyzing equipment data...',
  'Calculating failure probabilities...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedRisk = ref('all')
const selectedType = ref('all')
const detailsVisible = ref(false)
const chartRef = ref(null)
const trendChartRef = ref(null)

let probabilityChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null

// Risk level filters
const riskOptions = [
  { value: 'all', label: 'All Risks' },
  { value: 'high', label: 'High Risk', color: '#F56C6C' },
  { value: 'medium', label: 'Medium Risk', color: '#E6A23C' },
  { value: 'low', label: 'Low Risk', color: '#67C23A' }
]

// Type filters
const typeOptions = [
  { value: 'all', label: 'All Types' },
  { value: 'hvac', label: 'HVAC' },
  { value: 'electrical', label: 'Electrical' },
  { value: 'pump', label: 'Pump' },
  { value: 'chiller', label: 'Chiller' }
]

// Failure prediction data
const predictions = ref([
  {
    id: 'PRED001', name: 'AHU-1', type: 'hvac', risk: 'low',
    failureProbability: 15, estimatedDays: 180, confidence: 85,
    primaryCause: 'Normal wear', recommendation: 'Routine maintenance',
    metrics: { temperature: 22.5, vibration: 0.3, efficiency: 92 },
    nextMaintenance: '2024-02-10', status: 'monitoring'
  },
  {
    id: 'PRED002', name: 'AHU-2', type: 'hvac', risk: 'medium',
    failureProbability: 45, estimatedDays: 45, confidence: 78,
    primaryCause: 'Bearing wear', recommendation: 'Schedule bearing inspection',
    metrics: { temperature: 24.8, vibration: 0.7, efficiency: 78 },
    nextMaintenance: '2024-01-15', status: 'warning'
  },
  {
    id: 'PRED003', name: 'Chiller-1', type: 'chiller', risk: 'high',
    failureProbability: 82, estimatedDays: 12, confidence: 92,
    primaryCause: 'Compressor failure', recommendation: 'IMMEDIATE REPAIR NEEDED',
    metrics: { temperature: 28.5, vibration: 1.2, efficiency: 58 },
    nextMaintenance: '2023-12-20', status: 'critical'
  },
  {
    id: 'PRED004', name: 'VFD Pump', type: 'pump', risk: 'low',
    failureProbability: 22, estimatedDays: 120, confidence: 82,
    primaryCause: 'Seal degradation', recommendation: 'Monitor seal condition',
    metrics: { temperature: 21.0, vibration: 0.4, efficiency: 85 },
    nextMaintenance: '2024-02-05', status: 'monitoring'
  },
  {
    id: 'PRED005', name: 'Main Switchboard', type: 'electrical', risk: 'low',
    failureProbability: 12, estimatedDays: 240, confidence: 88,
    primaryCause: 'Normal aging', recommendation: 'Routine inspection',
    metrics: { temperature: 35.0, vibration: 0.2, efficiency: 94 },
    nextMaintenance: '2024-02-12', status: 'monitoring'
  },
  {
    id: 'PRED006', name: 'Cooling Tower', type: 'hvac', risk: 'medium',
    failureProbability: 58, estimatedDays: 28, confidence: 75,
    primaryCause: 'Fan motor issues', recommendation: 'Schedule motor inspection',
    metrics: { temperature: 26.5, vibration: 0.9, efficiency: 72 },
    nextMaintenance: '2024-01-01', status: 'warning'
  },
  {
    id: 'PRED007', name: 'Chiller-2', type: 'chiller', risk: 'medium',
    failureProbability: 52, estimatedDays: 35, confidence: 80,
    primaryCause: 'Refrigerant leak', recommendation: 'Check refrigerant levels',
    metrics: { temperature: 27.2, vibration: 0.6, efficiency: 75 },
    nextMaintenance: '2024-01-20', status: 'warning'
  },
  {
    id: 'PRED008', name: 'Air Compressor', type: 'pump', risk: 'low',
    failureProbability: 18, estimatedDays: 150, confidence: 86,
    primaryCause: 'Normal wear', recommendation: 'Routine maintenance',
    metrics: { temperature: 23.0, vibration: 0.3, efficiency: 90 },
    nextMaintenance: '2024-02-15', status: 'monitoring'
  }
])

// Failure statistics
const failureStats = reactive({
  total: 0,
  high: 0,
  medium: 0,
  low: 0,
  avgProbability: 0,
  criticalCount: 0,
  avgConfidence: 0,
  earliestFailure: 0
})

// Trend data
const trendData = ref([
  { week: 'Week 1', probability: 12, high: 1, medium: 2, low: 5 },
  { week: 'Week 2', probability: 15, high: 1, medium: 2, low: 5 },
  { week: 'Week 3', probability: 18, high: 2, medium: 2, low: 4 },
  { week: 'Week 4', probability: 22, high: 2, medium: 3, low: 3 },
  { week: 'Week 5', probability: 25, high: 2, medium: 3, low: 3 },
  { week: 'Week 6', probability: 28, high: 2, medium: 4, low: 2 }
])

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 8,
  total: predictions.value.length
})

// Filtered predictions
const filteredPredictions = computed(() => {
  let filtered = predictions.value
  if (searchKeyword.value) {
    filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        p.id.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedRisk.value !== 'all') {
    filtered = filtered.filter(p => p.risk === selectedRisk.value)
  }
  if (selectedType.value !== 'all') {
    filtered = filtered.filter(p => p.type === selectedType.value)
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
        initTrendChart()
        updateStats()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  probabilityChart = echarts.init(chartRef.value)
  probabilityChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Failure Probability (%)'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: predictions.value.map(p => p.name), axisLabel: { rotate: 30, interval: 0 } },
    yAxis: { type: 'value', name: 'Probability (%)', min: 0, max: 100 },
    series: [{
      name: 'Failure Probability (%)',
      type: 'bar',
      data: predictions.value.map(p => p.failureProbability),
      itemStyle: {
        color: (params: any) => {
          const value = params.value
          if (value >= 70) return '#F56C6C'
          if (value >= 40) return '#E6A23C'
          return '#67C23A'
        },
        borderRadius: [4, 4, 0, 0]
      },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initTrendChart = () => {
  if (!trendChartRef.value) return

  trendChart = echarts.init(trendChartRef.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Avg Failure Probability (%)'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: trendData.value.map(t => t.week) },
    yAxis: { type: 'value', name: 'Probability (%)', min: 0, max: 50 },
    series: [{
      name: 'Avg Failure Probability (%)',
      type: 'line',
      data: trendData.value.map(t => t.probability),
      smooth: true,
      lineStyle: { color: '#F56C6C', width: 3 },
      areaStyle: { opacity: 0.1, color: '#F56C6C' },
      symbol: 'circle',
      symbolSize: 8,
      label: { show: true, position: 'top' }
    }]
  })
}

const updateStats = () => {
  failureStats.total = predictions.value.length
  failureStats.high = predictions.value.filter(p => p.risk === 'high').length
  failureStats.medium = predictions.value.filter(p => p.risk === 'medium').length
  failureStats.low = predictions.value.filter(p => p.risk === 'low').length
  failureStats.avgProbability = Math.round(predictions.value.reduce((sum, p) => sum + p.failureProbability, 0) / predictions.value.length)
  failureStats.criticalCount = predictions.value.filter(p => p.failureProbability >= 70).length
  failureStats.avgConfidence = Math.round(predictions.value.reduce((sum, p) => sum + p.confidence, 0) / predictions.value.length)

  const earliest = Math.min(...predictions.value.map(p => p.estimatedDays))
  failureStats.earliestFailure = earliest
}

const handleResize = () => {
  probabilityChart?.resize()
  trendChart?.resize()
}

// ==================== Prediction Functions ====================
const refreshData = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  initChart()
  loading.value = false
  ElMessage.success('Prediction data refreshed successfully')
}

const viewDetails = (pred: any) => {
  selectedPrediction.value = pred
  detailsVisible.value = true
}

const scheduleInspection = (pred: any) => {
  ElMessage.info(`Scheduling inspection for ${pred.name}`)
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getRiskColor = (risk: string) => {
  switch (risk) {
    case 'high': return '#F56C6C'
    case 'medium': return '#E6A23C'
    case 'low': return '#67C23A'
    default: return '#909399'
  }
}

const getRiskIcon = (risk: string) => {
  switch (risk) {
    case 'high': return '🔴'
    case 'medium': return '🟠'
    case 'low': return '🟢'
    default: return '⚪'
  }
}

const getProbabilityColor = (probability: number) => {
  if (probability >= 70) return '#F56C6C'
  if (probability >= 40) return '#E6A23C'
  return '#67C23A'
}

const selectedPrediction = ref<any>(null)
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
          <span class="loading-title">Loading Failure Prediction</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Predictive Maintenance - Failure Prediction</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="failure-prediction-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Failure Prediction</h1>
        <p class="page-subtitle">AI-powered failure prediction and risk assessment</p>
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
          <div class="stat-value">{{ failureStats.total }}</div>
          <div class="stat-label">Total Equipment</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ failureStats.high }} High Risk</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon probability-icon">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ failureStats.avgProbability }}%</div>
          <div class="stat-label">Avg Failure Probability</div>
        </div>
        <div class="stat-trend">
          <el-progress :percentage="failureStats.avgProbability" :stroke-width="4" :show-text="false" />
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon confidence-icon">
          <el-icon><Star /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ failureStats.avgConfidence }}%</div>
          <div class="stat-label">Avg Confidence</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+5% this month</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon alert-icon">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ failureStats.criticalCount }}</div>
          <div class="stat-label">Critical Items</div>
        </div>
        <div class="stat-trend">
          <span class="trend-down">Earliest: {{ failureStats.earliestFailure }} days</span>
        </div>
      </div>
    </div>

    <!-- Chart Section -->
    <div class="charts-row">
      <div class="chart-section">
        <div class="section-header">
          <h3>Failure Probability by Equipment</h3>
          <el-button text type="primary" @click="initChart">Refresh</el-button>
        </div>
        <div ref="chartRef" class="probability-chart" style="height: 320px"></div>
      </div>

      <div class="chart-section">
        <div class="section-header">
          <h3>Trend Analysis (6 Weeks)</h3>
          <el-button text type="primary" @click="initTrendChart">Refresh</el-button>
        </div>
        <div ref="trendChartRef" class="trend-chart" style="height: 320px"></div>
      </div>
    </div>

    <!-- Risk Legend -->
    <div class="risk-legend">
      <div class="legend-item">
        <span class="legend-dot high"></span>
        <span>High Risk (>70%) - Immediate Action Required</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot medium"></span>
        <span>Medium Risk (40-70%) - Schedule Inspection</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot low"></span>
        <span>Low Risk (<40%) - Monitor Only</span>
      </div>
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
        <div class="risk-filters">
          <button
              v-for="r in riskOptions"
              :key="r.value"
              class="risk-chip"
              :class="{ active: selectedRisk === r.value }"
              @click="selectedRisk = r.value"
          >
            <span class="chip-dot" :style="{ background: r.color }"></span>
            <span>{{ r.label }}</span>
          </button>
        </div>
      </div>
      <div class="filters-right">
        <el-select v-model="selectedType" placeholder="Equipment Type" clearable style="width: 150px">
          <el-option v-for="t in typeOptions.slice(1)" :key="t.value" :label="t.label" :value="t.value" />
        </el-select>
      </div>
    </div>

    <!-- Predictions Grid -->
    <div class="predictions-grid">
      <div
          v-for="pred in filteredPredictions"
          :key="pred.id"
          class="prediction-card"
          :class="pred.risk"
          @click="viewDetails(pred)"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="equipment-type">
            <span class="type-icon">{{ pred.type === 'hvac' ? '❄️' : pred.type === 'electrical' ? '⚡' : pred.type === 'pump' ? '💧' : '🔧' }}</span>
            <span class="type-name">{{ pred.type.toUpperCase() }}</span>
          </div>
          <div class="risk-badge" :style="{ background: getRiskColor(pred.risk) }">
            {{ getRiskIcon(pred.risk) }} {{ pred.risk.toUpperCase() }}
          </div>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <h4 class="equipment-name">{{ pred.name }}</h4>

          <!-- Probability Circle -->
          <div class="probability-circle">
            <div class="circle-value" :style="{ color: getProbabilityColor(pred.failureProbability) }">
              {{ pred.failureProbability }}%
            </div>
            <div class="circle-label">Failure Probability</div>
            <div class="probability-bar">
              <div class="bar-fill" :style="{ width: pred.failureProbability + '%', background: getProbabilityColor(pred.failureProbability) }"></div>
            </div>
          </div>

          <!-- Key Metrics -->
          <div class="key-metrics">
            <div class="metric">
              <span class="metric-label">Est. Days</span>
              <span class="metric-value">{{ pred.estimatedDays }} days</span>
            </div>
            <div class="metric">
              <span class="metric-label">Confidence</span>
              <span class="metric-value">{{ pred.confidence }}%</span>
            </div>
            <div class="metric">
              <span class="metric-label">Cause</span>
              <span class="metric-value">{{ pred.primaryCause.substring(0, 15) }}...</span>
            </div>
          </div>

          <!-- Recommendation -->
          <div class="recommendation" :class="pred.risk">
            <span class="rec-icon">💡</span>
            <span class="rec-text">{{ pred.recommendation }}</span>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="next-maintenance">
            <span class="label">Next Maintenance:</span>
            <span class="value" :class="{ overdue: new Date(pred.nextMaintenance) < new Date() }">
              {{ pred.nextMaintenance }}
            </span>
          </div>
          <div class="card-actions">
            <el-button size="small" @click.stop="viewDetails(pred)">Details</el-button>
            <el-button size="small" type="primary" @click.stop="scheduleInspection(pred)">Schedule</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredPredictions.length === 0" class="empty-state">
      <el-empty description="No predictions found">
        <el-button type="primary">Reset Filters</el-button>
      </el-empty>
    </div>

    <!-- Pagination -->
    <div v-if="filteredPredictions.length > 0" class="pagination-wrapper">
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

    <!-- Prediction Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="selectedPrediction?.name" width="650px">
      <div class="dialog-content">
        <div class="risk-summary" :class="selectedPrediction?.risk">
          <div class="risk-score">
            <span class="score-value">{{ selectedPrediction?.failureProbability }}%</span>
            <span class="score-label">Failure Probability</span>
          </div>
          <div class="risk-info">
            <div class="info-item">
              <span class="label">Risk Level:</span>
              <span class="value" :style="{ color: getRiskColor(selectedPrediction?.risk) }">
                {{ selectedPrediction?.risk?.toUpperCase() }}
              </span>
            </div>
            <div class="info-item">
              <span class="label">Est. Time to Failure:</span>
              <span class="value">{{ selectedPrediction?.estimatedDays }} days</span>
            </div>
            <div class="info-item">
              <span class="label">Prediction Confidence:</span>
              <span class="value">{{ selectedPrediction?.confidence }}%</span>
            </div>
          </div>
        </div>

        <el-divider />

        <el-descriptions :column="2" border>
          <el-descriptions-item label="Equipment ID">{{ selectedPrediction?.id }}</el-descriptions-item>
          <el-descriptions-item label="Type">{{ selectedPrediction?.type?.toUpperCase() }}</el-descriptions-item>
          <el-descriptions-item label="Primary Cause">{{ selectedPrediction?.primaryCause }}</el-descriptions-item>
          <el-descriptions-item label="Temperature">{{ selectedPrediction?.metrics?.temperature }}°C</el-descriptions-item>
          <el-descriptions-item label="Vibration">{{ selectedPrediction?.metrics?.vibration }} mm/s</el-descriptions-item>
          <el-descriptions-item label="Efficiency">{{ selectedPrediction?.metrics?.efficiency }}%</el-descriptions-item>
          <el-descriptions-item label="Next Maintenance">{{ selectedPrediction?.nextMaintenance }}</el-descriptions-item>
          <el-descriptions-item label="Recommendation" :span="2">{{ selectedPrediction?.recommendation }}</el-descriptions-item>
        </el-descriptions>

        <div v-if="selectedPrediction?.risk === 'high'" class="critical-alert">
          <el-alert
              title="CRITICAL: Immediate action required!"
              type="error"
              show-icon
              :closable="false"
          >
            <template #default>
              <p>Equipment failure predicted within {{ selectedPrediction?.estimatedDays }} days. Schedule repair immediately to prevent system downtime.</p>
            </template>
          </el-alert>
        </div>

        <div v-else-if="selectedPrediction?.risk === 'medium'" class="warning-alert">
          <el-alert
              title="Action Recommended"
              type="warning"
              show-icon
              :closable="false"
          >
            <template #default>
              <p>Schedule inspection within {{ selectedPrediction?.estimatedDays }} days to prevent escalation.</p>
            </template>
          </el-alert>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
        <el-button type="primary" @click="scheduleInspection(selectedPrediction)">Schedule Inspection</el-button>
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
.failure-prediction-container {
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

.probability-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.confidence-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.alert-icon {
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

.probability-chart,
.trend-chart {
  width: 100%;
}

/* Risk Legend */
.risk-legend {
  display: flex;
  justify-content: center;
  gap: 32px;
  margin-bottom: 24px;
  padding: 12px 20px;
  background: white;
  border-radius: 40px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #606266;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-dot.high { background: #F56C6C; }
.legend-dot.medium { background: #E6A23C; }
.legend-dot.low { background: #67C23A; }

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

.risk-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.risk-chip {
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

.risk-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.risk-chip.active {
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

/* Predictions Grid */
.predictions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.prediction-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.prediction-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.prediction-card.high {
  border-left: 4px solid #F56C6C;
}

.prediction-card.medium {
  border-left: 4px solid #E6A23C;
}

.prediction-card.low {
  border-left: 4px solid #67C23A;
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

.risk-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  color: white;
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

.probability-circle {
  text-align: center;
  margin-bottom: 16px;
}

.circle-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 4px;
}

.circle-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 12px;
}

.probability-bar {
  height: 8px;
  background: #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.probability-bar .bar-fill {
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

.recommendation {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 12px;
  margin-bottom: 8px;
}

.recommendation.high {
  background: #fef0f0;
}

.recommendation.medium {
  background: #fdf6ec;
}

.recommendation.low {
  background: #f0f9ff;
}

.rec-icon {
  font-size: 14px;
}

.rec-text {
  font-size: 12px;
  font-weight: 500;
}

.recommendation.high .rec-text { color: #f56c6c; }
.recommendation.medium .rec-text { color: #e6a23c; }
.recommendation.low .rec-text { color: #67c23a; }

/* Card Footer */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px 16px 20px;
  border-top: 1px solid #f0f0f0;
  background: #fafbfc;
}

.next-maintenance {
  display: flex;
  gap: 8px;
  font-size: 12px;
}

.next-maintenance .label {
  color: #909399;
}

.next-maintenance .value {
  color: #1e293b;
  font-weight: 500;
}

.next-maintenance .value.overdue {
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

.risk-summary {
  display: flex;
  gap: 24px;
  padding: 20px;
  border-radius: 16px;
}

.risk-summary.high {
  background: linear-gradient(135deg, #fef0f0 0%, #fcd9d9 100%);
}

.risk-summary.medium {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
}

.risk-summary.low {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
}

.risk-score {
  text-align: center;
  min-width: 120px;
}

.score-value {
  font-size: 48px;
  font-weight: 700;
}

.risk-summary.high .score-value { color: #f56c6c; }
.risk-summary.medium .score-value { color: #e6a23c; }
.risk-summary.low .score-value { color: #67c23a; }

.score-label {
  font-size: 12px;
  color: #909399;
}

.risk-info {
  flex: 1;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.info-item .label {
  color: #909399;
}

.info-item .value {
  font-weight: 600;
  color: #1e293b;
}

.critical-alert,
.warning-alert {
  margin-top: 10px;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-row {
    grid-template-columns: 1fr;
  }

  .predictions-grid {
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  }

  .risk-legend {
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .failure-prediction-container {
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

  .risk-filters {
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

  .predictions-grid {
    grid-template-columns: 1fr;
  }

  .risk-summary {
    flex-direction: column;
    align-items: center;
  }

  .risk-legend {
    flex-direction: column;
    align-items: center;
    gap: 12px;
  }

  .key-metrics {
    flex-direction: column;
    gap: 8px;
  }

  .card-footer {
    flex-direction: column;
    gap: 12px;
  }

  .next-maintenance {
    justify-content: space-between;
    width: 100%;
  }
}
</style>