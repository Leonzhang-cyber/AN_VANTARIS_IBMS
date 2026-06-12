<script setup lang="ts">
import { ref, onMounted, computed, reactive, watch } from 'vue'
import * as echarts from 'echarts'
import {
  Refresh, Setting, User, Clock,
  Warning, CircleCheck, TrendCharts, DataLine,
  Star, Share, CopyDocument, Delete, Mic,
  Picture, Document, Upload, Download,
  MagicStick, ChatDotRound, Message, Service,
  Search, Edit, Plus, VideoPlay, VideoPause,
  Operation, Headset, Monitor, Cpu, Connection,
  Link, Aim, SuccessFilled, Filter,
  Loading, Check, Close, Right
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing AI diagnostic engine...',
  'Loading workflow templates...',
  'Preparing diagnostic steps...',
  'Almost ready...'
]

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
      // Initialize any charts or data after loading
    }, 400)
  }, 2500)
})

// ==================== Component State ====================
const loading = ref(false)
const selectedFault = ref('')
const currentStep = ref(0)
const diagnosisResult = ref<any>(null)
const detailsVisible = ref(false)
const chartRef = ref(null)

let workflowChart: echarts.ECharts | null = null

// Common fault types
const faultTypes = [
  { value: '', label: 'Select a fault type', disabled: true },
  { value: 'chiller_high_temp', label: 'Chiller - High Temperature', severity: 'critical' },
  { value: 'ahu_low_airflow', label: 'AHU - Low Airflow', severity: 'high' },
  { value: 'pump_vibration', label: 'Pump - Excessive Vibration', severity: 'medium' },
  { value: 'switchboard_overheat', label: 'Switchboard - Overheating', severity: 'critical' },
  { value: 'compressor_failure', label: 'Compressor - Failure to Start', severity: 'high' },
  { value: 'fan_motor_issue', label: 'Fan - Motor Issues', severity: 'medium' }
]

// Diagnostic workflow steps
const workflowSteps = ref([
  { id: 1, name: 'Initial Assessment', icon: '🔍', status: 'pending', description: 'Analyze fault description and initial symptoms' },
  { id: 2, name: 'Data Collection', icon: '📊', status: 'pending', description: 'Collect sensor data and historical logs' },
  { id: 3, name: 'Pattern Analysis', icon: '🧠', status: 'pending', description: 'AI pattern matching and anomaly detection' },
  { id: 4, name: 'Root Cause Identification', icon: '🎯', status: 'pending', description: 'Identify potential root causes' },
  { id: 5, name: 'Recommendation', icon: '💡', status: 'pending', description: 'Generate diagnostic recommendations' }
])

// Diagnosis data for different fault types
const diagnosisData: Record<string, any> = {
  chiller_high_temp: {
    symptoms: ['Temperature > 38°C', 'High pressure alarm', 'Compressor cycling frequently', 'Increased power consumption'],
    possibleCauses: [
      { cause: 'Refrigerant leak', probability: 85, evidence: 'Low refrigerant pressure detected' },
      { cause: 'Condenser fouling', probability: 65, evidence: 'Reduced heat exchange efficiency' },
      { cause: 'Compressor wear', probability: 45, evidence: 'Unusual noise from compressor' },
      { cause: 'Cooling tower fan failure', probability: 35, evidence: 'Reduced air flow across condenser' }
    ],
    recommendation: 'Immediate inspection of refrigerant levels and condenser cleaning. Schedule compressor inspection.',
    confidence: 92,
    estimatedCost: '$5,000 - $15,000',
    estimatedTime: '2-4 hours'
  },
  ahu_low_airflow: {
    symptoms: ['Airflow reduced by 40%', 'High static pressure', 'Filter pressure high', 'Increased fan speed'],
    possibleCauses: [
      { cause: 'Clogged filters', probability: 90, evidence: 'Filter differential pressure high' },
      { cause: 'Duct blockage', probability: 55, evidence: 'Uneven airflow distribution' },
      { cause: 'Fan belt slippage', probability: 45, evidence: 'Fan speed inconsistent' },
      { cause: 'Damper actuator failure', probability: 30, evidence: 'Damper position not responding' }
    ],
    recommendation: 'Replace air filters immediately. Inspect ducts for blockages and check fan belt tension.',
    confidence: 88,
    estimatedCost: '$500 - $2,000',
    estimatedTime: '1-2 hours'
  },
  pump_vibration: {
    symptoms: ['Vibration > 4.5 mm/s', 'Unusual noise', 'Temperature elevation', 'Reduced flow rate'],
    possibleCauses: [
      { cause: 'Bearing wear', probability: 85, evidence: 'Vibration frequency analysis indicates bearing fault' },
      { cause: 'Shaft misalignment', probability: 65, evidence: 'Coupling misalignment detected' },
      { cause: 'Cavitation', probability: 40, evidence: 'Noise characteristic of cavitation' },
      { cause: 'Impeller imbalance', probability: 35, evidence: 'Vibration amplitude varies with speed' }
    ],
    recommendation: 'Schedule bearing replacement and alignment check. Inspect for cavitation.',
    confidence: 90,
    estimatedCost: '$2,000 - $5,000',
    estimatedTime: '3-5 hours'
  },
  switchboard_overheat: {
    symptoms: ['Temperature > 70°C', 'Burning smell reported', 'Voltage fluctuation', 'Breaker tripping'],
    possibleCauses: [
      { cause: 'Loose connections', probability: 88, evidence: 'Thermal imaging shows hot spots' },
      { cause: 'Overload condition', probability: 65, evidence: 'Current exceeds rating' },
      { cause: 'Phase imbalance', probability: 45, evidence: 'Current imbalance detected' },
      { cause: 'Deteriorated insulation', probability: 30, evidence: 'Insulation resistance low' }
    ],
    recommendation: 'Immediate thermal scan and connection tightening. Load balancing required.',
    confidence: 91,
    estimatedCost: '$3,000 - $8,000',
    estimatedTime: '2-3 hours'
  },
  compressor_failure: {
    symptoms: ['Compressor not starting', 'Humming noise', 'Breaker trips', 'Overload protection active'],
    possibleCauses: [
      { cause: 'Electrical failure', probability: 75, evidence: 'Winding resistance abnormal' },
      { cause: 'Mechanical seizure', probability: 60, evidence: 'Cannot turn manually' },
      { cause: 'Low refrigerant', probability: 50, evidence: 'Suction pressure low' },
      { cause: 'Start capacitor failure', probability: 45, evidence: 'No start assist' }
    ],
    recommendation: 'Check electrical connections and compressor windings. Test start capacitor.',
    confidence: 85,
    estimatedCost: '$8,000 - $20,000',
    estimatedTime: '4-6 hours'
  },
  fan_motor_issue: {
    symptoms: ['Fan not running', 'Motor overheating', 'Unusual noise', 'Vibration'],
    possibleCauses: [
      { cause: 'Bearing failure', probability: 80, evidence: 'Rough rotation when turned' },
      { cause: 'Motor winding failure', probability: 60, evidence: 'Resistance out of spec' },
      { cause: 'Capacitor failure', probability: 50, evidence: 'No start' },
      { cause: 'Control signal loss', probability: 40, evidence: 'No voltage at motor' }
    ],
    recommendation: 'Inspect motor bearings and windings. Test run capacitor.',
    confidence: 87,
    estimatedCost: '$1,000 - $3,000',
    estimatedTime: '2-3 hours'
  }
}

// AI Diagnostic statistics
const diagStats = reactive({
  totalDiagnoses: 1250,
  accuracy: 94.5,
  avgTime: 2.3,
  activeUsers: 8
})

// Diagnostic history
const diagnosticHistory = ref([
  { id: 'D001', fault: 'Chiller High Temperature', result: 'Refrigerant leak detected', confidence: 92, timestamp: '2024-01-15 10:30:00' },
  { id: 'D002', fault: 'AHU Low Airflow', result: 'Clogged filters identified', confidence: 88, timestamp: '2024-01-14 14:20:00' },
  { id: 'D003', fault: 'VFD Pump Vibration', result: 'Bearing wear confirmed', confidence: 90, timestamp: '2024-01-13 09:15:00' }
])

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 5,
  total: diagnosticHistory.value.length
})

const paginatedHistory = computed(() => {
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return diagnosticHistory.value.slice(start, end)
})

// Workflow functions
const startDiagnosis = async () => {
  if (!selectedFault.value) {
    ElMessage.warning('Please select a fault type')
    return
  }

  // Reset workflow steps
  workflowSteps.value.forEach(step => {
    step.status = 'pending'
  })
  currentStep.value = 0
  diagnosisResult.value = null

  // Simulate diagnostic process
  loading.value = true

  for (let i = 0; i < workflowSteps.value.length; i++) {
    currentStep.value = i
    workflowSteps.value[i].status = 'processing'
    await new Promise(resolve => setTimeout(resolve, 800))
    workflowSteps.value[i].status = 'completed'
  }

  // Get diagnosis result
  const data = diagnosisData[selectedFault.value]
  diagnosisResult.value = {
    ...data,
    faultType: selectedFault.value,
    timestamp: new Date().toLocaleString()
  }

  // Add to history
  diagnosticHistory.value.unshift({
    id: `D${String(diagnosticHistory.value.length + 1).padStart(3, '0')}`,
    fault: faultTypes.find(f => f.value === selectedFault.value)?.label || selectedFault.value,
    result: data.possibleCauses[0]?.cause || 'Diagnosis completed',
    confidence: data.confidence,
    timestamp: new Date().toLocaleString()
  })

  loading.value = false
  ElMessage.success('Diagnosis completed successfully')
}

const resetDiagnosis = () => {
  selectedFault.value = ''
  currentStep.value = 0
  diagnosisResult.value = null
  workflowSteps.value.forEach(step => {
    step.status = 'pending'
  })
}

const viewDetails = (item: any) => {
  selectedHistoryItem.value = item
  detailsVisible.value = true
}

const initChart = () => {
  if (!chartRef.value || !diagnosisResult.value) return

  const causeData = diagnosisResult.value?.possibleCauses?.map((c: any) => ({
    name: c.cause,
    value: c.probability
  })) || []

  if (workflowChart) {
    workflowChart.dispose()
  }

  workflowChart = echarts.init(chartRef.value)
  workflowChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c}%)' },
    legend: { orient: 'vertical', left: 'left', data: causeData.map((c: any) => c.name) },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: causeData,
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: {d}%' },
      itemStyle: {
        color: (params: any) => {
          const colors = ['#F56C6C', '#E6A23C', '#409EFF', '#67C23A', '#9B59B6']
          return colors[params.dataIndex % colors.length]
        }
      }
    }]
  })
}

const handleResize = () => {
  workflowChart?.resize()
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getStepIcon = (step: any) => {
  if (step.status === 'completed') return CircleCheck
  if (step.status === 'processing') return Loading
  return Clock
}

const getStepType = (step: any) => {
  if (step.status === 'completed') return 'success'
  if (step.status === 'processing') return 'warning'
  return 'info'
}

const selectedHistoryItem = ref<any>(null)

// Watch for diagnosis result to update chart
watch(diagnosisResult, (newVal) => {
  if (newVal && chartRef.value) {
    setTimeout(() => {
      initChart()
    }, 100)
  }
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
          <span class="loading-title">Loading AI Diagnostic Workflow</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Fault Diagnostics - AI Diagnostic Workflow</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="ai-diagnostic-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">AI Diagnostic Workflow</h1>
        <p class="page-subtitle">Intelligent fault diagnosis powered by AI and machine learning</p>
      </div>
      <div class="header-right">
        <el-button size="large" @click="resetDiagnosis">
          <el-icon><Delete /></el-icon>
          Reset
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
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ diagStats.totalDiagnoses.toLocaleString() }}</div>
          <div class="stat-label">Total Diagnoses</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+245 this month</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon accuracy-icon">
          <el-icon><Star /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ diagStats.accuracy }}%</div>
          <div class="stat-label">Diagnostic Accuracy</div>
        </div>
        <div class="stat-trend">
          <el-progress :percentage="diagStats.accuracy" :stroke-width="4" :show-text="false" />
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon time-icon">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ diagStats.avgTime }} min</div>
          <div class="stat-label">Avg Diagnosis Time</div>
        </div>
        <div class="stat-trend">
          <span class="trend-down">-0.5 min</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon users-icon">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ diagStats.activeUsers }}</div>
          <div class="stat-label">Active Users</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+2 this week</span>
        </div>
      </div>
    </div>

    <!-- Main Diagnostic Section -->
    <div class="diagnostic-section">
      <!-- Fault Selection -->
      <div class="fault-selection">
        <h3>1. Select Fault Type</h3>
        <el-select v-model="selectedFault" placeholder="Select a fault type" style="width: 100%" size="large">
          <el-option
              v-for="fault in faultTypes"
              :key="fault.value"
              :label="fault.label"
              :value="fault.value"
              :disabled="fault.disabled"
          />
        </el-select>
        <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="startDiagnosis"
            :disabled="!selectedFault"
            style="margin-top: 16px; width: 100%"
        >
          <el-icon><MagicStick /></el-icon>
          Start AI Diagnosis
        </el-button>
      </div>

      <!-- Workflow Steps -->
      <div class="workflow-steps">
        <h3>2. Diagnostic Workflow</h3>
        <div class="steps-container">
          <div
              v-for="(step, index) in workflowSteps"
              :key="step.id"
              class="step-item"
              :class="{ active: currentStep === index, completed: step.status === 'completed' }"
          >
            <div class="step-number">
              <el-icon v-if="step.status === 'completed'"><CircleCheck /></el-icon>
              <span v-else>{{ step.id }}</span>
            </div>
            <div class="step-content">
              <div class="step-name">{{ step.name }}</div>
              <div class="step-desc">{{ step.description }}</div>
            </div>
            <div v-if="index < workflowSteps.length - 1" class="step-connector"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Diagnosis Results -->
    <div v-if="diagnosisResult" class="results-section">
      <div class="results-header">
        <h3>3. Diagnosis Results</h3>
        <el-tag type="success" size="large">Confidence: {{ diagnosisResult.confidence }}%</el-tag>
      </div>

      <div class="results-grid">
        <!-- Symptoms -->
        <div class="result-card">
          <div class="card-header">
            <span class="card-icon">🔍</span>
            <h4>Detected Symptoms</h4>
          </div>
          <div class="symptoms-list">
            <div v-for="symptom in diagnosisResult.symptoms" :key="symptom" class="symptom-item">
              <el-icon><CircleCheck /></el-icon>
              <span>{{ symptom }}</span>
            </div>
          </div>
        </div>

        <!-- Possible Causes Chart -->
        <div class="result-card">
          <div class="card-header">
            <span class="card-icon">📊</span>
            <h4>Possible Causes Analysis</h4>
          </div>
          <div ref="chartRef" class="cause-chart" style="height: 250px"></div>
        </div>

        <!-- Root Cause Details -->
        <div class="result-card">
          <div class="card-header">
            <span class="card-icon">🎯</span>
            <h4>Root Cause Details</h4>
          </div>
          <div class="causes-list">
            <div v-for="cause in diagnosisResult.possibleCauses" :key="cause.cause" class="cause-item">
              <div class="cause-header">
                <span class="cause-name">{{ cause.cause }}</span>
                <el-tag :type="cause.probability > 70 ? 'danger' : cause.probability > 50 ? 'warning' : 'info'" size="small">
                  {{ cause.probability }}% probability
                </el-tag>
              </div>
              <div class="cause-evidence">
                <span class="evidence-label">Evidence:</span>
                <span class="evidence-text">{{ cause.evidence }}</span>
              </div>
              <el-progress :percentage="cause.probability" :stroke-width="6" :show-text="false" />
            </div>
          </div>
        </div>

        <!-- Recommendation -->
        <div class="result-card recommendation-card">
          <div class="card-header">
            <span class="card-icon">💡</span>
            <h4>AI Recommendation</h4>
          </div>
          <div class="recommendation-content">
            <p>{{ diagnosisResult.recommendation }}</p>
            <div class="recommendation-meta">
              <div class="meta-item">
                <span class="meta-label">Estimated Cost:</span>
                <span class="meta-value">{{ diagnosisResult.estimatedCost }}</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">Estimated Time:</span>
                <span class="meta-value">{{ diagnosisResult.estimatedTime }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Diagnostic History -->
    <div class="history-section">
      <div class="section-header">
        <h3>Recent Diagnostic History</h3>
        <el-tag type="info" size="small">{{ diagnosticHistory.length }} records</el-tag>
      </div>

      <el-table :data="paginatedHistory" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="fault" label="Fault Type" min-width="200" />
        <el-table-column prop="result" label="Diagnosis Result" min-width="250" />
        <el-table-column label="Confidence" width="120" align="center">
          <template #default="{ row }">
            <el-progress :percentage="row.confidence" :stroke-width="6" :show-text="false" />
            <span style="font-size: 12px">{{ row.confidence }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="timestamp" label="Timestamp" width="180" />
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">
              Details
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[5, 10, 15, 20]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- History Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="selectedHistoryItem?.fault" width="500px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="Diagnosis ID">{{ selectedHistoryItem?.id }}</el-descriptions-item>
        <el-descriptions-item label="Fault Type">{{ selectedHistoryItem?.fault }}</el-descriptions-item>
        <el-descriptions-item label="Diagnosis Result">{{ selectedHistoryItem?.result }}</el-descriptions-item>
        <el-descriptions-item label="Confidence">{{ selectedHistoryItem?.confidence }}%</el-descriptions-item>
        <el-descriptions-item label="Timestamp">{{ selectedHistoryItem?.timestamp }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
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
.ai-diagnostic-container {
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

.accuracy-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.time-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.users-icon {
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

/* Diagnostic Section */
.diagnostic-section {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 24px;
  margin-bottom: 24px;
}

.fault-selection,
.workflow-steps {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.fault-selection h3,
.workflow-steps h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 16px 0;
}

/* Workflow Steps */
.steps-container {
  position: relative;
}

.step-item {
  display: flex;
  position: relative;
  margin-bottom: 24px;
}

.step-item:last-child {
  margin-bottom: 0;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: #909399;
  margin-right: 12px;
  flex-shrink: 0;
  position: relative;
  z-index: 2;
}

.step-item.active .step-number {
  background: #409eff;
  color: white;
}

.step-item.completed .step-number {
  background: #67c23a;
  color: white;
}

.step-content {
  flex: 1;
}

.step-name {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.step-desc {
  font-size: 12px;
  color: #909399;
}

.step-connector {
  position: absolute;
  left: 15px;
  top: 32px;
  width: 2px;
  height: 24px;
  background: #e4e7ed;
}

.step-item.completed + .step-connector {
  background: #67c23a;
}

/* Results Section */
.results-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.results-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.result-card {
  background: #fafbfc;
  border-radius: 16px;
  padding: 16px;
}

.result-card .card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.card-icon {
  font-size: 20px;
}

.result-card .card-header h4 {
  font-size: 14px;
  font-weight: 600;
  margin: 0;
  color: #1e293b;
}

.symptoms-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.symptom-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #606266;
}

.symptom-item .el-icon {
  color: #67c23a;
}

.causes-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.cause-item {
  border-bottom: 1px solid #e4e7ed;
  padding-bottom: 12px;
}

.cause-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.cause-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  flex-wrap: wrap;
  gap: 8px;
}

.cause-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 13px;
}

.cause-evidence {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.evidence-label {
  font-weight: 500;
}

.recommendation-card {
  grid-column: span 2;
}

.recommendation-content p {
  font-size: 14px;
  color: #1e293b;
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.recommendation-meta {
  display: flex;
  gap: 24px;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}

.meta-item {
  display: flex;
  gap: 8px;
  font-size: 13px;
}

.meta-label {
  color: #909399;
}

.meta-value {
  font-weight: 600;
  color: #409eff;
}

.cause-chart {
  width: 100%;
}

/* History Section */
.history-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .diagnostic-section {
    grid-template-columns: 1fr;
  }

  .results-grid {
    grid-template-columns: 1fr;
  }

  .recommendation-card {
    grid-column: span 1;
  }
}

@media (max-width: 768px) {
  .ai-diagnostic-container {
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

  .recommendation-meta {
    flex-direction: column;
    gap: 12px;
  }

  .results-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>