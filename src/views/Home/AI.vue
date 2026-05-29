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

  <!-- AI Insights Page Content -->
  <div v-else class="ai-insights-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>AI Insights</h1>
        <p class="subtitle">Intelligent analytics and predictive recommendations powered by artificial intelligence</p>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="refreshData">Refresh</el-button>
        <el-button type="primary" :icon="Download" @click="exportReport">Export Report</el-button>
        <el-button :icon="ChatDotRound" @click="openAIAssistant">AI Assistant</el-button>
      </div>
    </div>

    <!-- AI Overview Cards -->
    <div class="ai-cards">
      <div class="ai-card predictions">
        <div class="ai-icon">
          <el-icon :size="32"><TrendCharts /></el-icon>
        </div>
        <div class="ai-info">
          <div class="ai-value">{{ activePredictions }}</div>
          <div class="ai-label">Active Predictions</div>
        </div>
        <div class="ai-confidence">
          <span>Avg Confidence</span>
          <strong>{{ avgConfidence }}%</strong>
        </div>
      </div>
      <div class="ai-card anomalies">
        <div class="ai-icon">
          <el-icon :size="32"><WarningFilled /></el-icon>
        </div>
        <div class="ai-info">
          <div class="ai-value">{{ anomaliesDetected }}</div>
          <div class="ai-label">Anomalies Detected</div>
        </div>
        <div class="ai-trend positive">
          <el-icon><CaretBottom /></el-icon>
          {{ anomalyTrend }}%
        </div>
      </div>
      <div class="ai-card savings">
        <div class="ai-icon">
          <el-icon :size="32"><Money /></el-icon>
        </div>
        <div class="ai-info">
          <div class="ai-value">${{ projectedSavings }}k</div>
          <div class="ai-label">Projected Savings</div>
        </div>
        <div class="ai-trend positive">
          <el-icon><CaretTop /></el-icon>
          +{{ savingsGrowth }}%
        </div>
      </div>
      <div class="ai-card models">
        <div class="ai-icon">
          <el-icon :size="32"><Cpu /></el-icon>
        </div>
        <div class="ai-info">
          <div class="ai-value">{{ activeModels }}</div>
          <div class="ai-label">Active AI Models</div>
        </div>
        <div class="ai-status">All Operational</div>
      </div>
    </div>

    <!-- AI Recommendations Carousel / Top Insights -->
    <div class="insights-card">
      <div class="card-header">
        <h3>
          <el-icon><StarFilled /></el-icon>
          Top AI Recommendations
        </h3>
        <el-tag type="info" size="small">Updated just now</el-tag>
      </div>
      <div class="insights-list">
        <div v-for="insight in topInsights" :key="insight.id" class="insight-item" :class="insight.priority">
          <div class="insight-icon">
            <el-icon><Sunny /></el-icon>
          </div>
          <div class="insight-content">
            <div class="insight-title">{{ insight.title }}</div>
            <div class="insight-description">{{ insight.description }}</div>
            <div class="insight-metrics">
              <span><el-icon><Lightning /></el-icon> Impact: {{ insight.impact }}</span>
              <span><el-icon><Timer /></el-icon> Confidence: {{ insight.confidence }}%</span>
            </div>
          </div>
          <div class="insight-actions">
            <el-button size="small" type="primary" plain @click="applyInsight(insight)">Apply</el-button>
            <el-button size="small" @click="dismissInsight(insight)">Dismiss</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Predictive Analytics Charts -->
    <div class="two-columns">
      <div class="chart-card">
        <div class="card-header">
          <h3>Energy Consumption Forecast</h3>
          <el-tooltip content="AI-powered prediction based on historical data and weather patterns" placement="top">
            <el-icon><InfoFilled /></el-icon>
          </el-tooltip>
        </div>
        <div class="chart-container" ref="forecastChartRef"></div>
      </div>
      <div class="chart-card">
        <div class="card-header">
          <h3>Anomaly Detection Timeline</h3>
          <el-tooltip content="Unusual patterns detected by AI algorithms" placement="top">
            <el-icon><InfoFilled /></el-icon>
          </el-tooltip>
        </div>
        <div class="chart-container" ref="anomalyChartRef"></div>
      </div>
    </div>

    <!-- Predictive Maintenance Alerts -->
    <div class="table-card">
      <div class="card-header">
        <h3>
          <el-icon><Tools /></el-icon>
          Predictive Maintenance Alerts
        </h3>
        <el-select v-model="predictionFilter" placeholder="All Assets" clearable size="default" style="width: 160px">
          <el-option label="All Assets" value="all" />
          <el-option label="HVAC" value="hvac" />
          <el-option label="Electrical" value="electrical" />
          <el-option label="Chillers" value="chillers" />
          <el-option label="AHU" value="ahu" />
        </el-select>
      </div>
      <el-table :data="paginatedPredictions" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="asset" label="Asset" min-width="160" />
        <el-table-column prop="type" label="Type" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="issue" label="Predicted Issue" min-width="200" show-overflow-tooltip />
        <el-table-column prop="probability" label="Failure Probability" width="140">
          <template #default="{ row }">
            <div class="probability-cell">
              <span :class="getProbabilityClass(row.probability)">{{ row.probability }}%</span>
              <el-progress :percentage="row.probability" :color="getProbabilityColor(row.probability)" :stroke-width="6" :show-text="false" style="width: 80px" />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="predictedDate" label="Predicted Date" width="120" sortable />
        <el-table-column prop="recommendedAction" label="Recommended Action" min-width="180" show-overflow-tooltip />
        <el-table-column prop="confidence" label="AI Confidence" width="120" align="center">
          <template #default="{ row }">
            <el-progress type="circle" :percentage="row.confidence" :width="40" :stroke-width="5" :color="getConfidenceColor(row.confidence)" />
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewPrediction(row)">View</el-button>
            <el-button link type="success" size="small" @click="scheduleMaintenance(row)">Schedule</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredPredictions.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- AI Model Performance -->
    <div class="models-section">
      <div class="section-header">
        <h2>
          <el-icon><DataAnalysis /></el-icon>
          AI Model Performance Metrics
        </h2>
      </div>
      <div class="models-grid">
        <div v-for="model in aiModels" :key="model.name" class="model-card">
          <div class="model-header">
            <span class="model-name">{{ model.name }}</span>
            <span class="model-status" :class="model.status">{{ model.status }}</span>
          </div>
          <div class="model-metrics">
            <div class="metric">
              <span>Accuracy</span>
              <strong>{{ model.accuracy }}%</strong>
            </div>
            <div class="metric">
              <span>Precision</span>
              <strong>{{ model.precision }}%</strong>
            </div>
            <div class="metric">
              <span>Recall</span>
              <strong>{{ model.recall }}%</strong>
            </div>
            <div class="metric">
              <span>F1 Score</span>
              <strong>{{ model.f1Score }}%</strong>
            </div>
          </div>
          <div class="model-progress">
            <el-progress :percentage="model.accuracy" :color="getModelColor(model.accuracy)" :stroke-width="6" :show-text="false" />
          </div>
          <div class="model-footer">
            <span>Last trained: {{ model.lastTrained }}</span>
            <el-button link type="primary" size="small" @click="viewModelDetails(model)">Details</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- AI Assistant Quick Actions -->
    <div class="assistant-section">
      <div class="section-header">
        <h2>
          <el-icon><ChatDotRound /></el-icon>
          AI Assistant
        </h2>
        <el-button type="primary" :icon="ChatDotRound" size="small" @click="openAIAssistant">Ask AI</el-button>
      </div>
      <div class="assistant-suggestions">
        <div class="suggestion" v-for="suggestion in assistantSuggestions" :key="suggestion" @click="askQuestion(suggestion)">
          <el-icon><ChatDotSquare /></el-icon>
          <span>{{ suggestion }}</span>
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
  ChatDotRound,
  TrendCharts,
  WarningFilled,
  Money,
  Cpu,
  StarFilled,
  Lightning,
  Timer,
  InfoFilled,
  Tools,
  DataAnalysis,
  ChatDotSquare,
  Sunny,
  CaretTop,
  CaretBottom
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
interface AIInsight {
  id: number
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
  impact: string
  confidence: number
}

interface PredictiveAlert {
  id: number
  asset: string
  type: string
  issue: string
  probability: number
  predictedDate: string
  recommendedAction: string
  confidence: number
}

interface AIModel {
  name: string
  status: string
  accuracy: number
  precision: number
  recall: number
  f1Score: number
  lastTrained: string
}

// ==================== State ====================
const predictionFilter = ref('all')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const forecastChartRef = ref<HTMLElement | null>(null)
const anomalyChartRef = ref<HTMLElement | null>(null)
let forecastChart: echarts.ECharts | null = null
let anomalyChart: echarts.ECharts | null = null

// ==================== Mock Data ====================
const activePredictions = ref(28)
const avgConfidence = ref(87)
const anomaliesDetected = ref(12)
const anomalyTrend = ref(8.5)
const projectedSavings = ref(156)
const savingsGrowth = ref(12)
const activeModels = ref(6)

const topInsights = ref<AIInsight[]>([
  { id: 1, title: 'Chiller Efficiency Optimization', description: 'AI analysis suggests adjusting chilled water setpoint by 2°C during off-peak hours to reduce energy consumption by 12%.', priority: 'high', impact: '$18,500/year', confidence: 92 },
  { id: 2, title: 'Predictive Maintenance Alert', description: 'AHU-101 fan bearing shows abnormal vibration pattern. Schedule maintenance within 14 days to prevent failure.', priority: 'high', impact: 'Prevent $45k downtime', confidence: 88 },
  { id: 3, title: 'Lighting Schedule Optimization', description: 'Occupancy pattern analysis indicates lighting can be reduced by 30% on weekends without impact.', priority: 'medium', impact: '$6,200/year', confidence: 85 },
  { id: 4, title: 'HVAC Demand Response Opportunity', description: 'Weather forecast indicates peak demand tomorrow. AI recommends pre-cooling strategy.', priority: 'medium', impact: '$2,800 savings', confidence: 91 }
])

const predictiveAlerts = ref<PredictiveAlert[]>([
  { id: 1, asset: 'Chiller-01', type: 'HVAC', issue: 'Compressor wear detected', probability: 78, predictedDate: '2025-06-15', recommendedAction: 'Schedule compressor inspection and lubrication', confidence: 85 },
  { id: 2, asset: 'AHU-101', type: 'AHU', issue: 'Fan bearing failure imminent', probability: 92, predictedDate: '2025-06-05', recommendedAction: 'Replace fan bearings within 7 days', confidence: 94 },
  { id: 3, asset: 'UPS-01', type: 'Electrical', issue: 'Battery capacity degradation', probability: 65, predictedDate: '2025-07-20', recommendedAction: 'Monitor battery health, plan replacement', confidence: 82 },
  { id: 4, asset: 'FCU-205', type: 'HVAC', issue: 'Valve actuator stuck', probability: 71, predictedDate: '2025-06-25', recommendedAction: 'Inspect and lubricate actuator', confidence: 79 },
  { id: 5, asset: 'Cooling Tower CT-01', type: 'HVAC', issue: 'Fan motor overheating', probability: 84, predictedDate: '2025-06-10', recommendedAction: 'Clean cooling fins and check motor bearings', confidence: 88 },
  { id: 6, asset: 'VFD-03', type: 'Electrical', issue: 'Capacitor aging detected', probability: 59, predictedDate: '2025-08-01', recommendedAction: 'Monitor and plan capacitor replacement', confidence: 76 },
  { id: 7, asset: 'Pump-02', type: 'Plumbing', issue: 'Seal leakage predicted', probability: 72, predictedDate: '2025-06-18', recommendedAction: 'Inspect seals and schedule maintenance', confidence: 83 },
  { id: 8, asset: 'CRAC-01', type: 'DCIM', issue: 'Compressor short cycling', probability: 68, predictedDate: '2025-07-05', recommendedAction: 'Check refrigerant levels and controls', confidence: 81 }
])

const aiModels = ref<AIModel[]>([
  { name: 'Energy Prediction Model', status: 'active', accuracy: 94, precision: 92, recall: 91, f1Score: 91, lastTrained: '2025-05-15' },
  { name: 'Anomaly Detection', status: 'active', accuracy: 89, precision: 87, recall: 90, f1Score: 88, lastTrained: '2025-05-10' },
  { name: 'Predictive Maintenance', status: 'active', accuracy: 91, precision: 89, recall: 92, f1Score: 90, lastTrained: '2025-05-20' },
  { name: 'Occupancy Prediction', status: 'active', accuracy: 86, precision: 85, recall: 84, f1Score: 84, lastTrained: '2025-05-18' },
  { name: 'Demand Response', status: 'active', accuracy: 88, precision: 87, recall: 86, f1Score: 86, lastTrained: '2025-05-12' },
  { name: 'Fault Diagnosis', status: 'active', accuracy: 92, precision: 91, recall: 90, f1Score: 90, lastTrained: '2025-05-22' }
])

const assistantSuggestions = ref([
  'What is the predicted energy consumption for next week?',
  'Which assets require maintenance in the next 30 days?',
  'Show me optimization opportunities for HVAC systems',
  'Analyze anomaly patterns from last month'
])

// ==================== Computed Values ====================
const filteredPredictions = computed(() => {
  let result = [...predictiveAlerts.value]
  if (predictionFilter.value !== 'all') {
    result = result.filter(p => p.type.toLowerCase() === predictionFilter.value)
  }
  return result
})

const paginatedPredictions = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredPredictions.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getProbabilityClass = (probability: number) => {
  if (probability >= 80) return 'text-danger'
  if (probability >= 60) return 'text-warning'
  return 'text-success'
}

const getProbabilityColor = (probability: number) => {
  if (probability >= 80) return '#f56c6c'
  if (probability >= 60) return '#e6a23c'
  return '#67c23a'
}

const getConfidenceColor = (confidence: number) => {
  if (confidence >= 90) return '#67c23a'
  if (confidence >= 75) return '#409eff'
  return '#e6a23c'
}

const getModelColor = (accuracy: number) => {
  if (accuracy >= 90) return '#67c23a'
  if (accuracy >= 80) return '#409eff'
  return '#e6a23c'
}

// ==================== Chart Functions ====================
const initForecastChart = () => {
  if (!forecastChartRef.value) return
  if (forecastChart) forecastChart.dispose()

  forecastChart = echarts.init(forecastChartRef.value)

  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  const actual = [12500, 12800, 13200, 13500, 13800, 14200, 14000]
  const predicted = [12700, 13000, 13400, 13700, 14000, 14400, 14200]
  const upperBound = predicted.map(v => v * 1.05)
  const lowerBound = predicted.map(v => v * 0.95)

  forecastChart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: (value: number) => value.toLocaleString() + ' kWh' },
    legend: { data: ['Actual', 'AI Prediction', 'Confidence Band'], bottom: 0 },
    grid: { left: '3%', right: '4%', top: '10%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', data: days },
    yAxis: { type: 'value', name: 'Energy (kWh)' },
    series: [
      { name: 'Actual', type: 'line', data: actual, smooth: true, symbol: 'circle', lineStyle: { width: 2, color: '#409eff' } },
      { name: 'AI Prediction', type: 'line', data: predicted, smooth: true, symbol: 'diamond', lineStyle: { width: 2, color: '#e6a23c', type: 'dashed' } },
      { name: 'Confidence Band', type: 'band', data: [lowerBound, upperBound], lineStyle: { opacity: 0 }, bandStyle: { color: '#409eff', opacity: 0.2 } }
    ]
  })
}

const initAnomalyChart = () => {
  if (!anomalyChartRef.value) return
  if (anomalyChart) anomalyChart.dispose()

  anomalyChart = echarts.init(anomalyChartRef.value)

  const dates = ['5/20', '5/21', '5/22', '5/23', '5/24', '5/25', '5/26', '5/27', '5/28', '5/29']
  const values = [12500, 12800, 13100, 13400, 13200, 18900, 13600, 13800, 14200, 14000]
  const anomalies = [null, null, null, null, null, 18900, null, null, null, null]

  anomalyChart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: (value: number) => value.toLocaleString() + ' kWh' },
    legend: { data: ['Normal Pattern', 'AI-Detected Anomaly'], bottom: 0 },
    grid: { left: '3%', right: '4%', top: '10%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', data: dates },
    yAxis: { type: 'value', name: 'Energy (kWh)' },
    series: [
      { name: 'Normal Pattern', type: 'line', data: values, smooth: true, symbol: 'circle', lineStyle: { width: 2, color: '#67c23a' }, areaStyle: { opacity: 0.1, color: '#67c23a' } },
      { name: 'AI-Detected Anomaly', type: 'scatter', data: anomalies, symbol: 'circle', symbolSize: 15, itemStyle: { color: '#f56c6c' } }
    ]
  })
}

// ==================== Actions ====================
const refreshData = async () => {
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  ElMessage.success('AI insights data refreshed')
  initForecastChart()
  initAnomalyChart()
  tableLoading.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting AI insights report...')
}

const openAIAssistant = () => {
  ElMessage.info('Opening AI Assistant...')
}

const applyInsight = (insight: AIInsight) => {
  ElMessage.success(`Applying recommendation: ${insight.title}`)
}

const dismissInsight = (insight: AIInsight) => {
  ElMessage.info(`Dismissed: ${insight.title}`)
  topInsights.value = topInsights.value.filter(i => i.id !== insight.id)
}

const viewPrediction = (row: PredictiveAlert) => {
  ElMessage.info(`Viewing prediction for ${row.asset}`)
}

const scheduleMaintenance = (row: PredictiveAlert) => {
  ElMessage.success(`Maintenance scheduled for ${row.asset}`)
}

const viewModelDetails = (model: AIModel) => {
  ElMessage.info(`Viewing details for ${model.name} model`)
}

const askQuestion = (question: string) => {
  ElMessage.info(`AI Assistant: Processing "${question}"...`)
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Window Resize Handler ====================
const handleResize = () => {
  forecastChart?.resize()
  anomalyChart?.resize()
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
        initForecastChart()
        initAnomalyChart()
      }, 100)
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  forecastChart?.dispose()
  anomalyChart?.dispose()
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
.ai-insights-page {
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

/* AI Cards */
.ai-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.ai-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s, box-shadow 0.2s;
}

.ai-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.ai-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-card.predictions .ai-icon { background: linear-gradient(135deg, #e8f4ff, #d4e8ff); color: #409eff; }
.ai-card.anomalies .ai-icon { background: linear-gradient(135deg, #ffe8e8, #ffd4d4); color: #f56c6c; }
.ai-card.savings .ai-icon { background: linear-gradient(135deg, #e8f8f0, #d4f0e0); color: #67c23a; }
.ai-card.models .ai-icon { background: linear-gradient(135deg, #f0e8ff, #e0d4ff); color: #8b5cf6; }

.ai-info {
  flex: 1;
}

.ai-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
  line-height: 1.2;
}

.ai-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.ai-confidence {
  text-align: right;
  font-size: 12px;
  color: #909399;
}

.ai-confidence strong {
  display: block;
  font-size: 18px;
  color: #1f2f3d;
}

.ai-trend {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 13px;
  font-weight: 500;
}

.ai-trend.positive { color: #67c23a; }
.ai-trend.negative { color: #f56c6c; }

.ai-status {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 20px;
  background: #e8f8f0;
  color: #67c23a;
}

/* Insights Card */
.insights-card {
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
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1f2f3d;
}

.insights-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.insight-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 14px;
  transition: all 0.2s;
}

.insight-item:hover {
  background: #f5f7fa;
  transform: translateX(4px);
}

.insight-item.high { border-left: 4px solid #f56c6c; }
.insight-item.medium { border-left: 4px solid #e6a23c; }
.insight-item.low { border-left: 4px solid #409eff; }

.insight-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e8f4ff;
  color: #409eff;
  font-size: 22px;
}

.insight-content {
  flex: 1;
}

.insight-title {
  font-weight: 600;
  color: #1f2f3d;
  margin-bottom: 6px;
}

.insight-description {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.insight-metrics {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #909399;
}

.insight-metrics .el-icon {
  vertical-align: middle;
  margin-right: 4px;
}

.insight-actions {
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.insight-item:hover .insight-actions {
  opacity: 1;
}

/* Chart Cards */
.chart-card, .table-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
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
.probability-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.text-success { color: #67c23a; font-weight: 500; }
.text-warning { color: #e6a23c; font-weight: 500; }
.text-danger { color: #f56c6c; font-weight: 500; }

.pagination-wrapper {
  padding: 20px 0 0;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
  margin-top: 16px;
}

/* Models Section */
.models-section {
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  margin-bottom: 24px;
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

.models-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.model-card {
  background: #fafafa;
  border-radius: 14px;
  padding: 16px;
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.model-name {
  font-weight: 600;
  color: #1f2f3d;
}

.model-status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 20px;
}

.model-status.active {
  background: #e8f8f0;
  color: #67c23a;
}

.model-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-bottom: 12px;
  text-align: center;
}

.model-metrics .metric span {
  display: block;
  font-size: 10px;
  color: #909399;
  margin-bottom: 2px;
}

.model-metrics .metric strong {
  font-size: 16px;
  color: #1f2f3d;
}

.model-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  font-size: 10px;
  color: #c0c4cc;
}

/* Assistant Section */
.assistant-section {
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.assistant-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 16px;
}

.suggestion {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #f5f7fa;
  border-radius: 30px;
  font-size: 13px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion:hover {
  background: #409eff;
  color: white;
}

.suggestion .el-icon {
  font-size: 16px;
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