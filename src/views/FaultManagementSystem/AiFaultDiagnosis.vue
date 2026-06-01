<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted, computed } from 'vue'
import {
  Search, RefreshRight, Warning, CircleCheck, Clock,
  TrendCharts, Monitor, Connection, DataAnalysis,
  Document, Setting, More, ArrowUp, ArrowDown,
  VideoCamera, Histogram, Grid, Platform, Link,
  Tickets, Timer, PieChart, Medal, Rank, Cpu,
  ChatDotRound, Share, CopyDocument, Sunny
} from "@element-plus/icons-vue"
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Initializing AI Engine...')

const loadingMessages = [
  'Initializing AI Engine...',
  'Loading neural networks...',
  'Analyzing fault patterns...',
  'Training diagnostic models...',
  'Ready for analysis...'
]

// Active diagnosis sessions
const activeDiagnosis = ref([
  {
    id: 'DIA-001',
    assetId: 'CH-01',
    assetName: 'Chiller Unit 1',
    faultSymptoms: ['Unusual vibration', 'Increased power consumption', 'Reduced cooling capacity'],
    confidence: 94.5,
    diagnosis: 'Compressor bearing wear - Recommended immediate inspection',
    recommendedActions: [
      'Perform vibration analysis on compressor',
      'Check oil pressure and quality',
      'Schedule bearing replacement',
      'Monitor discharge temperature'
    ],
    estimatedCost: 12500,
    estimatedTime: '8-12 hours',
    priority: 'High',
    status: 'active',
    timestamp: '2025-01-16 08:30:00'
  },
  {
    id: 'DIA-002',
    assetId: 'UPS-02',
    assetName: 'UPS Unit 2',
    faultSymptoms: ['Battery runtime degradation', 'Frequent self-test failures', 'High internal temperature'],
    confidence: 87.2,
    diagnosis: 'Battery cell degradation - 3 cells showing reduced capacity',
    recommendedActions: [
      'Run full battery capacity test',
      'Replace affected battery strings',
      'Check charging parameters',
      'Verify thermal management'
    ],
    estimatedCost: 8500,
    estimatedTime: '6-8 hours',
    priority: 'Medium',
    status: 'active',
    timestamp: '2025-01-16 09:15:00'
  },
  {
    id: 'DIA-003',
    assetId: 'AHU-03',
    assetName: 'AHU Unit 3',
    faultSymptoms: ['Low airflow', 'Temperature fluctuation', 'Unusual noise from fan'],
    confidence: 91.8,
    diagnosis: 'Fan belt slippage with partial motor bearing failure',
    recommendedActions: [
      'Inspect and replace fan belt',
      'Check bearing alignment',
      'Lubricate motor bearings',
      'Verify VFD parameters'
    ],
    estimatedCost: 3200,
    estimatedTime: '3-4 hours',
    priority: 'Medium',
    status: 'active',
    timestamp: '2025-01-16 10:00:00'
  }
])

// Historical AI diagnoses
const historicalDiagnosis = ref([
  {
    id: 'DIA-098',
    assetId: 'CRAC-02',
    assetName: 'CRAC Unit 2',
    diagnosis: 'Refrigerant leak detected',
    confidence: 96.3,
    resolved: true,
    resolutionTime: '4.5 hours',
    timestamp: '2025-01-10'
  },
  {
    id: 'DIA-097',
    assetId: 'VFD-04',
    assetName: 'VFD Pump 4',
    diagnosis: 'Parameter corruption - restored from backup',
    confidence: 89.7,
    resolved: true,
    resolutionTime: '2 hours',
    timestamp: '2025-01-09'
  },
  {
    id: 'DIA-096',
    assetId: 'SW-AGG-01',
    assetName: 'Aggregation Switch',
    diagnosis: 'Broadcast storm detected - loop in network',
    confidence: 94.2,
    resolved: true,
    resolutionTime: '1.5 hours',
    timestamp: '2025-01-08'
  }
])

// AI performance metrics
const aiPerformance = ref({
  accuracy: 94.5,
  avgDiagnosisTime: 3.2,
  totalDiagnoses: 156,
  falsePositiveRate: 5.2,
  preventedDowntime: 1240,
  topPerformingModel: 'Deep Neural Network',
  trainedSamples: 28500
})

// Fault type distribution from AI analysis
const faultTypeDistribution = ref([
  { type: 'Mechanical', percentage: 35, count: 55 },
  { type: 'Electrical', percentage: 28, count: 44 },
  { type: 'Sensor/Calibration', percentage: 18, count: 28 },
  { type: 'Communication', percentage: 12, count: 19 },
  { type: 'Software/Config', percentage: 7, count: 10 }
])

// AI confidence trend
const confidenceTrend = ref([
  { month: 'Aug', confidence: 88.5, diagnoses: 18 },
  { month: 'Sep', confidence: 89.2, diagnoses: 22 },
  { month: 'Oct', confidence: 90.8, diagnoses: 25 },
  { month: 'Nov', confidence: 92.1, diagnoses: 28 },
  { month: 'Dec', confidence: 93.5, diagnoses: 31 },
  { month: 'Jan', confidence: 94.5, diagnoses: 32 }
])

// Real-time analysis input
const analysisInput = ref('')
const isAnalyzing = ref(false)
const analysisResult = ref<any>(null)

// Chart refs
const confidenceChartRef = ref<HTMLElement | null>(null)
const distributionChartRef = ref<HTMLElement | null>(null)
let confidenceChart: echarts.ECharts | null = null
let distributionChart: echarts.ECharts | null = null

// Selected diagnosis for detail
const selectedDiagnosis = ref<any>(null)
const detailVisible = ref(false)

const getPriorityColor = (priority: string) => {
  switch(priority) {
    case 'High': return '#F56C6C'
    case 'Medium': return '#E6A23C'
    case 'Low': return '#67C23A'
    default: return '#909399'
  }
}

const getConfidenceColor = (confidence: number) => {
  if (confidence >= 90) return '#67C23A'
  if (confidence >= 75) return '#E6A23C'
  return '#F56C6C'
}

const runAIDiagnosis = () => {
  if (!analysisInput.value.trim()) {
    ElMessage.warning('Please enter fault symptoms or select an asset')
    return
  }

  isAnalyzing.value = true

  // Simulate AI analysis
  setTimeout(() => {
    const mockResult = {
      assetId: 'ANALYSIS-001',
      diagnosis: 'Based on the symptoms provided, the AI model predicts a cooling system inefficiency with 92.3% confidence. The pattern matches known issues with condenser fouling.',
      confidence: 92.3,
      rootCauses: [
        'Condenser coil fouling (68% probability)',
        'Refrigerant undercharge (22% probability)',
        'Compressor inefficiency (10% probability)'
      ],
      recommendations: [
        'Schedule condenser cleaning',
        'Check refrigerant pressure levels',
        'Monitor compressor current draw',
        'Review maintenance logs for pattern'
      ],
      estimatedTimeToFix: '4-6 hours',
      priority: 'Medium'
    }
    analysisResult.value = mockResult
    isAnalyzing.value = false
    ElMessage.success('AI analysis completed')
  }, 2000)
}

const clearAnalysis = () => {
  analysisInput.value = ''
  analysisResult.value = null
}

const viewDetails = (diagnosis: any) => {
  selectedDiagnosis.value = diagnosis
  detailVisible.value = true
}

const implementFix = (diagnosis: any) => {
  ElMessageBox.confirm(
      `Create work order for ${diagnosis.assetId} with recommended actions?`,
      'Create Work Order',
      {
        confirmButtonText: 'Create',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    ElMessage.success(`Work order created for ${diagnosis.assetId}`)
  }).catch(() => {})
}

const refreshData = () => {
  ElMessage.info('Refreshing AI diagnostic data...')
  setTimeout(() => {
    ElMessage.success('Data refreshed successfully')
  }, 1000)
}

const initConfidenceChart = () => {
  if (confidenceChartRef.value) {
    if (confidenceChart) confidenceChart.dispose()

    confidenceChart = echarts.init(confidenceChartRef.value)
    confidenceChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: {
        data: ['AI Confidence (%)', 'Number of Diagnoses'],
        left: 'left',
        textStyle: { color: '#606266' }
      },
      grid: { left: '8%', right: '8%', top: '15%', bottom: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: confidenceTrend.value.map(d => d.month),
        axisLabel: { fontWeight: 500 }
      },
      yAxis: [
        { type: 'value', name: 'Confidence (%)', min: 85, max: 100 },
        { type: 'value', name: 'Diagnoses Count', min: 0 }
      ],
      series: [
        {
          name: 'AI Confidence (%)',
          type: 'line',
          data: confidenceTrend.value.map(d => d.confidence),
          smooth: true,
          lineStyle: { color: '#409EFF', width: 3 },
          areaStyle: { opacity: 0.1, color: '#409EFF' },
          symbol: 'circle',
          symbolSize: 8,
          label: { show: true, position: 'top', formatter: '{c}%' }
        },
        {
          name: 'Number of Diagnoses',
          type: 'bar',
          yAxisIndex: 1,
          data: confidenceTrend.value.map(d => d.diagnoses),
          itemStyle: { color: '#E6A23C', borderRadius: [4, 4, 0, 0] },
          label: { show: true, position: 'top' }
        }
      ]
    })
  }
}

const initDistributionChart = () => {
  if (distributionChartRef.value) {
    if (distributionChart) distributionChart.dispose()

    distributionChart = echarts.init(distributionChartRef.value)
    distributionChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} cases)' },
      legend: { orient: 'vertical', left: 'left', top: 'center', textStyle: { color: '#606266' } },
      series: [
        {
          name: 'Fault Type Distribution',
          type: 'pie',
          radius: ['40%', '65%'],
          data: faultTypeDistribution.value.map(t => ({ name: t.type, value: t.count })),
          label: { show: true, formatter: '{b}: {d}%' },
          emphasis: { scale: true },
          itemStyle: {
            borderRadius: 8,
            borderColor: '#fff',
            borderWidth: 2
          }
        }
      ]
    })
  }
}

const handleResize = () => {
  confidenceChart?.resize()
  distributionChart?.resize()
}

watch(isLoaded, (loaded) => {
  if (loaded) {
    nextTick(() => {
      initConfidenceChart()
      initDistributionChart()
      window.addEventListener('resize', handleResize)
    })
  }
})

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
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  confidenceChart?.dispose()
  distributionChart?.dispose()
})
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
          <span class="loading-title">AI Engine Starting</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">AI Fault Diagnosis System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="ai-fault-diagnosis">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>AI Fault Diagnosis</h2>
        <p class="subtitle">Intelligent fault detection and root cause analysis powered by machine learning</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="refreshData">
          <el-icon><RefreshRight /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- AI Performance KPI Cards -->
    <div class="kpi-grid">
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-content">
          <div class="kpi-icon accuracy">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ aiPerformance.accuracy }}%</div>
            <div class="kpi-label">Diagnosis Accuracy</div>
          </div>
        </div>
      </el-card>
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-content">
          <div class="kpi-icon time">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ aiPerformance.avgDiagnosisTime }}m</div>
            <div class="kpi-label">Avg Diagnosis Time</div>
          </div>
        </div>
      </el-card>
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-content">
          <div class="kpi-icon total">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ aiPerformance.totalDiagnoses }}</div>
            <div class="kpi-label">Total Diagnoses</div>
          </div>
        </div>
      </el-card>
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-content">
          <div class="kpi-icon prevented">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ aiPerformance.preventedDowntime }}h</div>
            <div class="kpi-label">Prevented Downtime</div>
          </div>
        </div>
      </el-card>
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-content">
          <div class="kpi-icon model">
            <el-icon><Cpu /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ aiPerformance.trainedSamples / 1000 }}k</div>
            <div class="kpi-label">Trained Samples</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Real-time AI Diagnosis Input -->
    <el-card class="analysis-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span><el-icon><ChatDotRound /></el-icon> AI Diagnostic Assistant</span>
          <el-tag type="success" size="small">Real-time Analysis</el-tag>
        </div>
      </template>
      <div class="analysis-input-area">
        <el-input
            v-model="analysisInput"
            type="textarea"
            :rows="3"
            placeholder="Describe fault symptoms or select an asset for AI analysis... (e.g., 'Chiller making unusual noise and temperature rising')"
            :disabled="isAnalyzing"
        />
        <div class="analysis-actions">
          <el-button type="primary" @click="runAIDiagnosis" :loading="isAnalyzing">
            <el-icon><Cpu /></el-icon> Run AI Diagnosis
          </el-button>
          <el-button @click="clearAnalysis" v-if="analysisResult || analysisInput">
            Clear
          </el-button>
        </div>
      </div>

      <!-- Analysis Result -->
      <div v-if="analysisResult" class="analysis-result">
        <div class="result-header">
          <div class="result-title">
            <el-icon><CircleCheck /></el-icon>
            AI Analysis Result
          </div>
          <div class="result-confidence">
            Confidence:
            <span :style="{ color: getConfidenceColor(analysisResult.confidence), fontWeight: 'bold' }">
              {{ analysisResult.confidence }}%
            </span>
          </div>
        </div>
        <div class="result-diagnosis">
          <strong>Diagnosis:</strong> {{ analysisResult.diagnosis }}
        </div>
        <div class="result-section">
          <strong>Root Causes:</strong>
          <ul>
            <li v-for="(cause, idx) in analysisResult.rootCauses" :key="idx">{{ cause }}</li>
          </ul>
        </div>
        <div class="result-section">
          <strong>Recommended Actions:</strong>
          <ul>
            <li v-for="(rec, idx) in analysisResult.recommendations" :key="idx">{{ rec }}</li>
          </ul>
        </div>
        <div class="result-footer">
          <div class="result-meta">
            <span>Estimated Fix Time: {{ analysisResult.estimatedTimeToFix }}</span>
            <span>Priority: <span :style="{ color: getPriorityColor(analysisResult.priority) }">{{ analysisResult.priority }}</span></span>
          </div>
          <el-button type="primary" size="small">Create Work Order</el-button>
        </div>
      </div>
    </el-card>

    <!-- Charts Row -->
    <div class="charts-row">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>AI Confidence & Diagnosis Trend</span>
            <el-tag type="info" size="small">Improving Accuracy</el-tag>
          </div>
        </template>
        <div ref="confidenceChartRef" class="chart"></div>
      </el-card>

      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Fault Type Distribution (AI Classified)</span>
            <el-tag type="warning" size="small">Pattern Analysis</el-tag>
          </div>
        </template>
        <div ref="distributionChartRef" class="chart"></div>
      </el-card>
    </div>

    <!-- Active AI Diagnoses -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Active AI Diagnoses</span>
          <el-tag type="danger" size="small">Requires Attention</el-tag>
        </div>
      </template>
      <el-table :data="activeDiagnosis" stripe>
        <el-table-column prop="id" label="Diagnosis ID" align="center" min-width="100" />
        <el-table-column prop="assetId" label="Asset ID" align="center" min-width="100" />
        <el-table-column prop="assetName" label="Asset Name" align="center" min-width="140" />
        <el-table-column label="Symptoms" align="center" min-width="180">
          <template #default="{ row }">
            <div class="symptoms-tags">
              <el-tag v-for="(symptom, idx) in row.faultSymptoms.slice(0, 2)" :key="idx" size="small" type="info" effect="plain">
                {{ symptom }}
              </el-tag>
              <el-tooltip v-if="row.faultSymptoms.length > 2" :content="row.faultSymptoms.slice(2).join(', ')" placement="top">
                <el-tag size="small" type="info">+{{ row.faultSymptoms.length - 2 }}</el-tag>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Confidence" align="center" min-width="100">
          <template #default="{ row }">
            <el-progress :percentage="row.confidence" :stroke-width="8" :color="getConfidenceColor(row.confidence)" />
          </template>
        </el-table-column>
        <el-table-column prop="diagnosis" label="AI Diagnosis" align="center" min-width="200" show-overflow-tooltip />
        <el-table-column label="Priority" align="center" min-width="90">
          <template #default="{ row }">
            <el-tag :type="row.priority === 'High' ? 'danger' : 'warning'" size="small">
              {{ row.priority }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" align="center" min-width="150">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetails(row)">Details</el-button>
            <el-button type="success" link size="small" @click="implementFix(row)">Create Work Order</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Historical Diagnoses -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Historical AI Diagnoses</span>
          <el-tag type="success" size="small">Resolved Cases</el-tag>
        </div>
      </template>
      <el-table :data="historicalDiagnosis" stripe>
        <el-table-column prop="id" label="Diagnosis ID" align="center" min-width="100" />
        <el-table-column prop="assetId" label="Asset ID" align="center" min-width="100" />
        <el-table-column prop="assetName" label="Asset Name" align="center" min-width="140" />
        <el-table-column prop="diagnosis" label="AI Diagnosis" align="center" min-width="200" show-overflow-tooltip />
        <el-table-column label="Confidence" align="center" min-width="100">
          <template #default="{ row }">
            <span :style="{ color: getConfidenceColor(row.confidence), fontWeight: 'bold' }">
              {{ row.confidence }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Resolution Time" align="center" min-width="120">
          <template #default="{ row }">
            {{ row.resolutionTime }}
          </template>
        </el-table-column>
        <el-table-column prop="timestamp" label="Date" align="center" min-width="110" />
        <el-table-column label="Actions" align="center" min-width="100">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetails(row)">Details</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Diagnosis Detail Dialog -->
    <el-dialog v-model="detailVisible" :title="`AI Diagnosis - ${selectedDiagnosis?.id}`" width="700px">
      <div v-if="selectedDiagnosis" class="diagnosis-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Asset ID">{{ selectedDiagnosis.assetId }}</el-descriptions-item>
          <el-descriptions-item label="Asset Name">{{ selectedDiagnosis.assetName }}</el-descriptions-item>
          <el-descriptions-item label="Confidence" :span="2">
            <el-progress :percentage="selectedDiagnosis.confidence" :stroke-width="10" :color="getConfidenceColor(selectedDiagnosis.confidence)" />
          </el-descriptions-item>
          <el-descriptions-item label="Diagnosis" :span="2">{{ selectedDiagnosis.diagnosis }}</el-descriptions-item>
          <el-descriptions-item v-if="selectedDiagnosis.faultSymptoms" label="Symptoms" :span="2">
            <div class="symptoms-tags">
              <el-tag v-for="(symptom, idx) in selectedDiagnosis.faultSymptoms" :key="idx" size="small" type="info" effect="plain">
                {{ symptom }}
              </el-tag>
            </div>
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedDiagnosis.recommendedActions" label="Recommended Actions" :span="2">
            <ul class="action-list">
              <li v-for="(action, idx) in selectedDiagnosis.recommendedActions" :key="idx">{{ action }}</li>
            </ul>
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedDiagnosis.estimatedCost" label="Estimated Cost">${{ selectedDiagnosis.estimatedCost.toLocaleString() }}</el-descriptions-item>
          <el-descriptions-item v-if="selectedDiagnosis.estimatedTime" label="Estimated Time">{{ selectedDiagnosis.estimatedTime }}</el-descriptions-item>
          <el-descriptions-item label="Priority">
            <el-tag :type="selectedDiagnosis.priority === 'High' ? 'danger' : selectedDiagnosis.priority === 'Medium' ? 'warning' : 'info'" size="small">
              {{ selectedDiagnosis.priority }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedDiagnosis.resolutionTime" label="Resolution Time">{{ selectedDiagnosis.resolutionTime }}</el-descriptions-item>
          <el-descriptions-item v-if="selectedDiagnosis.timestamp" label="Timestamp">{{ selectedDiagnosis.timestamp }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button v-if="selectedDiagnosis?.recommendedActions" type="primary" @click="implementFix(selectedDiagnosis)">
            Create Work Order
          </el-button>
          <el-button @click="detailVisible = false">Close</el-button>
        </div>
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
.ai-fault-diagnosis {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h2 {
  margin: 0 0 4px 0;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #303133, #606266);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

/* ==================== KPI Cards ==================== */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.kpi-card {
  border-radius: 20px;
  transition: all 0.3s ease;
  border: none;
}

.kpi-card:hover {
  transform: translateY(-4px);
}

.kpi-card :deep(.el-card__body) {
  padding: 20px;
}

.kpi-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.kpi-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.kpi-icon.accuracy { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
.kpi-icon.time { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; }
.kpi-icon.total { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; }
.kpi-icon.prevented { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; }
.kpi-icon.model { background: linear-gradient(135deg, #f6d365 0%, #fda085 100%); color: white; }

.kpi-info {
  flex: 1;
}

.kpi-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.kpi-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

/* ==================== Analysis Card ==================== */
.analysis-card {
  border-radius: 20px;
  margin-bottom: 24px;
  border: none;
}

.analysis-card :deep(.el-card__body) {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 15px;
}

.analysis-input-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.analysis-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.analysis-result {
  margin-top: 24px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 16px;
  border-left: 4px solid #409EFF;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.result-title {
  font-size: 16px;
  font-weight: 600;
  color: #409EFF;
  display: flex;
  align-items: center;
  gap: 8px;
}

.result-confidence {
  font-size: 14px;
}

.result-diagnosis {
  margin-bottom: 16px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  line-height: 1.5;
}

.result-section {
  margin-bottom: 16px;
}

.result-section strong {
  display: block;
  margin-bottom: 8px;
}

.result-section ul {
  margin: 0;
  padding-left: 20px;
}

.result-section li {
  margin: 6px 0;
  line-height: 1.4;
}

.result-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}

.result-meta {
  display: flex;
  gap: 24px;
  font-size: 13px;
  color: #606266;
}

/* ==================== Charts ==================== */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  border-radius: 20px;
  border: none;
}

.chart-card :deep(.el-card__body) {
  padding: 16px;
}

.chart {
  width: 100%;
  height: 360px;
}

/* ==================== Tables ==================== */
.table-card {
  border-radius: 20px;
  margin-bottom: 24px;
  border: none;
}

.table-card :deep(.el-card__body) {
  padding: 0;
}

.table-card :deep(.el-table__header-wrapper th) {
  text-align: center;
  background-color: #fafafa;
  font-weight: 600;
}

.table-card :deep(.el-table td) {
  text-align: center;
}

.symptoms-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: center;
}

/* ==================== Dialog ==================== */
.diagnosis-detail {
  padding: 0 0 16px 0;
}

.action-list {
  margin: 0;
  padding-left: 20px;
}

.action-list li {
  margin: 6px 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* ==================== Responsive ==================== */
@media (max-width: 1400px) {
  .kpi-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
}

@media (max-width: 1200px) {
  .charts-row {
    grid-template-columns: 1fr;
  }

  .chart {
    height: 320px;
  }
}

@media (max-width: 768px) {
  .ai-fault-diagnosis {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .kpi-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .chart {
    height: 280px;
  }

  .result-footer {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .result-meta {
    flex-direction: column;
    gap: 8px;
  }

  .table-card :deep(.el-table__body-wrapper) {
    overflow-x: auto;
  }

  .table-card :deep(.el-table) {
    min-width: 900px;
  }
}
</style>