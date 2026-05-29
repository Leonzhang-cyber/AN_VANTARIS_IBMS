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
        <div class="loading-tip">AI Root Cause Analysis</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- AI RCA Page Content -->
  <div v-else class="ai-rca-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <div class="title-badge">
          <el-icon><Cpu /></el-icon>
          <span>AI-Powered RCA</span>
        </div>
        <h1>AI Root Cause Analysis</h1>
        <p class="subtitle">Advanced AI-driven fault diagnosis using machine learning models to identify root causes</p>
      </div>
      <div class="header-actions">
        <button class="action-btn" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          <span>Refresh</span>
        </button>
        <button class="action-btn primary" @click="openAnalysisDialog" :loading="analysisRunning">
          <el-icon><TrendCharts /></el-icon>
          <span>Run AI Analysis</span>
        </button>
        <el-select v-model="selectedModel" class="model-select" placeholder="AI Model">
          <el-option label="GPT-4 Diagnostic Engine" value="gpt4" />
          <el-option label="BERT Fault Classifier" value="bert" />
          <el-option label="LSTM Prediction Model" value="lstm" />
          <el-option label="Ensemble Decision Tree" value="ensemble" />
        </el-select>
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-icon accuracy">
          <el-icon><Medal /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ modelAccuracy }}%</div>
          <div class="kpi-label">Model Accuracy</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon confidence">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ avgConfidence }}%</div>
          <div class="kpi-label">Avg Confidence</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon processed">
          <el-icon><Document /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ totalProcessed }}</div>
          <div class="kpi-label">Faults Analyzed</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon time">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ avgAnalysisTime }}<span class="unit">s</span></div>
          <div class="kpi-label">Avg Analysis Time</div>
        </div>
      </div>
    </div>

    <!-- AI Analysis Input Section -->
    <div class="input-card">
      <div class="card-header">
        <h3>Fault Description Input</h3>
        <span class="card-tip">Enter fault details for AI-powered root cause analysis</span>
      </div>
      <div class="analysis-input">
        <div class="input-row">
          <div class="input-group full">
            <label>Fault Description / Symptoms</label>
            <textarea
                v-model="faultDescription"
                rows="5"
                placeholder='Describe the fault in detail. Include symptoms, error codes, asset information, and observed behavior...

Example: "Chiller-02 tripped on high pressure at 08:23 this morning. Cooling tower fan was not running. Condenser water flow was 45% below normal. Building temperature is rising."'
                class="form-textarea"
            ></textarea>
          </div>
        </div>
        <div class="input-row">
          <div class="input-group">
            <label>Asset Type</label>
            <select v-model="assetType" class="form-select">
              <option value="">Select Asset Type</option>
              <option value="Chiller">Chiller</option>
              <option value="AHU">AHU</option>
              <option value="FCU">FCU</option>
              <option value="UPS">UPS</option>
              <option value="CRAC">CRAC</option>
              <option value="VFD">VFD</option>
              <option value="Pump">Pump</option>
              <option value="Generator">Generator</option>
            </select>
          </div>
          <div class="input-group">
            <label>Error Code (if any)</label>
            <input type="text" v-model="errorCode" placeholder="e.g., ERR-102, CH-101" class="form-input" />
          </div>
          <div class="input-group">
            <label>Sensor Readings (optional)</label>
            <input type="text" v-model="sensorReadings" placeholder="e.g., Pressure: 220PSI, Temp: 38°C" class="form-input" />
          </div>
        </div>
        <div class="example-prompts">
          <span class="example-label">Try an example:</span>
          <button v-for="example in examples" :key="example" class="example-btn" @click="useExample(example)">
            {{ example.substring(0, 40) }}...
          </button>
        </div>
        <button class="analyze-btn" @click="runAIAnalysis" :disabled="!faultDescription || analysisRunning">
          <el-icon><TrendCharts /></el-icon>
          {{ analysisRunning ? 'AI is Analyzing...' : 'Run AI Root Cause Analysis' }}
        </button>
      </div>
    </div>

    <!-- AI Analysis Results -->
    <div class="results-card" v-if="analysisResult">
      <div class="card-header">
        <h3>AI Analysis Results</h3>
        <span class="confidence-badge" :class="getConfidenceClass(analysisResult.confidence)">
          {{ analysisResult.confidence }}% Confidence
        </span>
      </div>

      <!-- Root Cause Section -->
      <div class="result-section root-cause">
        <div class="section-icon">
          <el-icon><Position /></el-icon>
        </div>
        <div class="section-content">
          <div class="section-title">Root Cause</div>
          <div class="section-text">{{ analysisResult.rootCause }}</div>
        </div>
      </div>

      <!-- Supporting Evidence -->
      <div class="result-section evidence">
        <div class="section-icon">
          <el-icon><DocumentChecked /></el-icon>
        </div>
        <div class="section-content">
          <div class="section-title">Supporting Evidence</div>
          <ul class="evidence-list">
            <li v-for="evidence in analysisResult.evidence" :key="evidence">{{ evidence }}</li>
          </ul>
        </div>
      </div>

      <!-- Recommended Actions -->
      <div class="result-section actions">
        <div class="section-icon">
          <el-icon><Setting /></el-icon>
        </div>
        <div class="section-content">
          <div class="section-title">Recommended Actions</div>
          <ul class="action-list">
            <li v-for="action in analysisResult.recommendedActions" :key="action">
              <el-icon><Check /></el-icon>
              <span>{{ action }}</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- Preventive Measures -->
      <div class="result-section preventive">
        <div class="section-icon">
          <el-icon><Lock /></el-icon>
        </div>
        <div class="section-content">
          <div class="section-title">Preventive Measures</div>
          <ul class="preventive-list">
            <li v-for="measure in analysisResult.preventiveMeasures" :key="measure">
              <el-icon><Clock /></el-icon>
              <span>{{ measure }}</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- Confidence Breakdown -->
      <div class="confidence-breakdown">
        <div class="breakdown-title">Confidence Breakdown</div>
        <div class="breakdown-bars">
          <div class="breakdown-item">
            <span class="breakdown-label">Pattern Matching</span>
            <el-progress :percentage="analysisResult.confidenceBreakdown.pattern" :stroke-width="8" :color="getConfidenceColor(analysisResult.confidenceBreakdown.pattern)" />
          </div>
          <div class="breakdown-item">
            <span class="breakdown-label">Historical Similarity</span>
            <el-progress :percentage="analysisResult.confidenceBreakdown.historical" :stroke-width="8" :color="getConfidenceColor(analysisResult.confidenceBreakdown.historical)" />
          </div>
          <div class="breakdown-item">
            <span class="breakdown-label">Sensor Analysis</span>
            <el-progress :percentage="analysisResult.confidenceBreakdown.sensor" :stroke-width="8" :color="getConfidenceColor(analysisResult.confidenceBreakdown.sensor)" />
          </div>
          <div class="breakdown-item">
            <span class="breakdown-label">ML Model Prediction</span>
            <el-progress :percentage="analysisResult.confidenceBreakdown.model" :stroke-width="8" :color="getConfidenceColor(analysisResult.confidenceBreakdown.model)" />
          </div>
        </div>
      </div>

      <!-- Model Details -->
      <div class="model-details">
        <div class="model-info">
          <span class="model-label">AI Model Used:</span>
          <span class="model-value">{{ analysisResult.modelUsed }}</span>
        </div>
        <div class="model-info">
          <span class="model-label">Analysis Time:</span>
          <span class="model-value">{{ analysisResult.analysisTime }} seconds</span>
        </div>
        <div class="model-info">
          <span class="model-label">Similar Cases Found:</span>
          <span class="model-value">{{ analysisResult.similarCases }} historical cases</span>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="result-actions">
        <button class="action-apply" @click="applyResolution">
          <el-icon><SuccessFilled /></el-icon>
          Apply Resolution
        </button>
        <button class="action-feedback" @click="openFeedbackDialog">
          <el-icon><ChatLineRound /></el-icon>
          Provide Feedback
        </button>
        <button class="action-export" @click="exportReport">
          <el-icon><Download /></el-icon>
          Export Report
        </button>
      </div>
    </div>

    <!-- Recent Analysis History -->
    <div class="history-card">
      <div class="card-header">
        <h3>Recent AI Analysis History</h3>
        <el-button link type="primary" size="small">View Full History</el-button>
      </div>
      <el-table :data="analysisHistory" stripe size="small">
        <el-table-column prop="timestamp" label="Time" width="160" />
        <el-table-column prop="description" label="Fault Description" min-width="250" show-overflow-tooltip />
        <el-table-column prop="rootCause" label="Root Cause" min-width="200" show-overflow-tooltip />
        <el-table-column prop="confidence" label="Confidence" width="120" align="center">
          <template #default="{ row }">
            <el-progress :percentage="row.confidence" :stroke-width="6" :show-text="true" :color="getConfidenceColor(row.confidence)" />
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="reanalyze(row)">Re-analyze</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- AI Analysis Progress Dialog -->
    <el-dialog v-model="analysisDialogVisible" title="AI Analysis in Progress" width="500px" :close-on-click-modal="false" :show-close="false">
      <div class="analysis-progress">
        <div class="analysis-animation">
          <div class="ai-pulse"></div>
          <div class="ai-logo">
            <el-icon><Cpu /></el-icon>
          </div>
        </div>
        <div class="analysis-step">{{ currentStepText }}</div>
        <el-progress :percentage="analysisProgress" :stroke-width="8" :show-text="false" :color="getProgressColor(analysisProgress)" />
        <div class="analysis-thinking" v-if="analysisProgress < 100">
          <span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>
        </div>
      </div>
    </el-dialog>

    <!-- Feedback Dialog -->
    <el-dialog v-model="feedbackDialogVisible" title="Feedback on AI Analysis" width="450px">
      <div class="feedback-content">
        <p>Was this root cause analysis helpful?</p>
        <div class="feedback-rating">
          <button v-for="rating in [1, 2, 3, 4, 5]" :key="rating" class="rating-star" @click="selectedRating = rating">
            <el-icon><StarFilled v-if="selectedRating >= rating" /><Star v-else /></el-icon>
          </button>
        </div>
        <div class="feedback-comment">
          <label>Additional comments (optional)</label>
          <textarea v-model="feedbackComment" rows="3" placeholder="Tell us how we can improve the AI analysis..."></textarea>
        </div>
      </div>
      <template #footer>
        <el-button @click="feedbackDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitFeedback">Submit Feedback</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Refresh, Download, Cpu, TrendCharts, Medal, Document, Timer,
  Position, DocumentChecked, Setting, Check, Lock, Clock,
  SuccessFilled, ChatLineRound, StarFilled, Star
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// Loading State
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const analysisRunning = ref(false)
const analysisDialogVisible = ref(false)
const feedbackDialogVisible = ref(false)
const analysisProgress = ref(0)
const currentStepIndex = ref(0)
const loadingMessages = ['Preparing...', 'Loading AI models...', 'Initializing analysis engine...', 'Almost ready...']

// Step texts for analysis
const stepTexts = [
  'Initializing AI Model...',
  'Processing fault description...',
  'Analyzing symptom patterns...',
  'Matching with historical cases...',
  'Generating root cause hypothesis...',
  'Validating with sensor data...',
  'Finalizing analysis results...'
]

const currentStepText = computed(() => stepTexts[currentStepIndex.value] || 'Analyzing...')

// State
// State
const selectedModel = ref('gpt4')
const faultDescription = ref('Chiller-02 tripped on high pressure at 08:23 this morning. Cooling tower fan was not running. Condenser water flow was 45% below normal. Building temperature is rising.')
const assetType = ref('Chiller')
const errorCode = ref('CH-102')
const sensorReadings = ref('Pressure: 220PSI, Flow: 45%, Temperature: 38°C')
const analysisResult = ref<any>(null)
const selectedRating = ref(0)
const feedbackComment = ref('')

// Mock Data
const modelAccuracy = computed(() => {
  const map: Record<string, number> = { gpt4: 94, bert: 89, lstm: 91, ensemble: 93 }
  return map[selectedModel.value] || 92
})

const avgConfidence = computed(() => 87)
const totalProcessed = ref(245)
const avgAnalysisTime = computed(() => {
  const map: Record<string, number> = { gpt4: 2.8, bert: 1.9, lstm: 2.2, ensemble: 3.1 }
  return map[selectedModel.value] || 2.5
})

const analysisHistory = ref([
  { timestamp: '2025-05-29 14:23:15', description: 'Chiller-02 high pressure trip, cooling tower fan not running', rootCause: 'Condenser water flow reduced due to cooling tower fan bearing failure', confidence: 94 },
  { timestamp: '2025-05-29 10:15:22', description: 'UPS-01 input power loss, breaker tripped', rootCause: 'Main switchboard breaker tripped due to downstream short circuit', confidence: 92 },
  { timestamp: '2025-05-28 16:30:05', description: 'Server room temperature high, CRAC-03 not cooling', rootCause: 'CRAC compressor capacitor failure', confidence: 96 },
  { timestamp: '2025-05-28 09:45:30', description: 'AHU-201 low airflow, high static pressure', rootCause: 'Filter maintenance overdue - 90 days since last change', confidence: 88 },
  { timestamp: '2025-05-27 22:20:15', description: 'VFD-105 overcurrent fault, motor overheating', rootCause: 'Motor bearing seizure', confidence: 86 }
])

const examples = [
  'Chiller-02 tripped on high pressure at 08:23 this morning. Cooling tower fan was not running. Condenser water flow was 45% below normal.',
  'UPS-01 lost input power. Main breaker tripped. Downstream PDU showing overload alarm.',
  'Server room temperature reached 32°C. CRAC-03 compressor not running. Rack inlet temperature alarm triggered.',
  'AHU-201 airflow dropped to 65% of setpoint. Differential pressure shows 180Pa. Fan speed at maximum.'
]

// AI Analysis Function
const runAIAnalysis = async () => {
  if (!faultDescription.value) {
    ElMessage.warning('Please enter fault description')
    return
  }

  analysisRunning.value = true
  analysisDialogVisible.value = true
  analysisProgress.value = 0
  currentStepIndex.value = 0

  // Simulate AI processing steps
  for (let step = 0; step < stepTexts.length; step++) {
    currentStepIndex.value = step
    for (let p = 0; p <= 100; p += 20) {
      if (step === stepTexts.length - 1 && p > 0) break
      analysisProgress.value = Math.min(100, (step / (stepTexts.length - 1)) * 100 + (p / (stepTexts.length - 1)))
      await new Promise(resolve => setTimeout(resolve, 80))
    }
    await new Promise(resolve => setTimeout(resolve, 200))
  }

  analysisProgress.value = 100
  await new Promise(resolve => setTimeout(resolve, 500))

  // Generate AI analysis result based on input
  const description = faultDescription.value.toLowerCase()
  let rootCause = ''
  let evidence: string[] = []
  let recommendedActions: string[] = []
  let preventiveMeasures: string[] = []
  let confidence = 0
  let confidenceBreakdown = { pattern: 0, historical: 0, sensor: 0, model: 0 }

  // Chiller related
  if (description.includes('chiller') && description.includes('high pressure')) {
    rootCause = 'Condenser water flow reduced due to cooling tower fan bearing failure'
    evidence = ['Cooling tower fan status: NOT RUNNING', 'Condenser water flow: 45% below normal', 'Chiller approach temperature: +3.5°C', 'Fan vibration reading: 0.35 mm/s (normal: <0.15)']
    recommendedActions = ['Restore cooling tower fan operation', 'Inspect and replace fan bearings if needed', 'Reset chiller after flow restoration', 'Check condenser water pump operation']
    preventiveMeasures = ['Monthly fan bearing inspection', 'Quarterly vibration analysis', 'Install vibration monitoring system']
    confidence = 94
    confidenceBreakdown = { pattern: 95, historical: 92, sensor: 88, model: 96 }
  }
  // UPS related
  else if (description.includes('ups') && description.includes('power loss')) {
    rootCause = 'Main switchboard breaker tripped due to downstream short circuit'
    evidence = ['Main breaker status: OPEN', 'Downstream PDU: Overload alarm', 'Input voltage: 0V', 'UPS on battery: 100%']
    recommendedActions = ['Isolate downstream loads', 'Identify short circuit location', 'Repair damaged cable', 'Reset breaker and restore power']
    preventiveMeasures = ['Quarterly thermal imaging', 'Cable insulation testing', 'Install short circuit protection']
    confidence = 92
    confidenceBreakdown = { pattern: 90, historical: 94, sensor: 85, model: 95 }
  }
  // Temperature / CRAC related
  else if (description.includes('temperature') && (description.includes('server') || description.includes('crac'))) {
    rootCause = 'CRAC compressor capacitor failure causing cooling capacity loss'
    evidence = ['CRAC status: FAULT', 'Compressor current: 0A', 'Supply air temperature: 24°C (setpoint: 18°C)', 'Room temperature: 32°C']
    recommendedActions = ['Diagnose compressor issue', 'Replace compressor capacitor', 'Recharge refrigerant if needed', 'Verify cooling operation']
    preventiveMeasures = ['Annual compressor inspection', 'Capacitor replacement schedule (3-5 years)', 'Real-time temperature monitoring']
    confidence = 96
    confidenceBreakdown = { pattern: 98, historical: 95, sensor: 92, model: 97 }
  }
  // AHU / Filter related
  else if (description.includes('ahu') && (description.includes('airflow') || description.includes('filter'))) {
    rootCause = 'Filter maintenance overdue - 90 days since last change'
    evidence = ['Differential pressure: 180Pa (normal: 80Pa)', 'Airflow: 65% of setpoint', 'Fan speed: 100%', 'Last filter change: 90 days ago']
    recommendedActions = ['Replace AHU filters', 'Reset differential pressure sensor', 'Verify airflow restoration', 'Update maintenance schedule']
    preventiveMeasures = ['Monthly filter inspection', '60-day filter replacement schedule', 'Install differential pressure monitoring']
    confidence = 88
    confidenceBreakdown = { pattern: 85, historical: 90, sensor: 82, model: 86 }
  }
  // VFD related
  else if (description.includes('vfd') && description.includes('overcurrent')) {
    rootCause = 'Motor bearing seizure causing excessive current draw'
    evidence = ['VFD fault code: OC-1', 'Motor current: 150A (rated: 100A)', 'Motor temperature: 85°C', 'Vibration reading: 0.45 mm/s']
    recommendedActions = ['Isolate power to VFD', 'Inspect motor bearings', 'Replace bearings if seized', 'Reset VFD and test operation']
    preventiveMeasures = ['Motor vibration monitoring', 'Quarterly lubrication schedule', 'Bearing replacement plan']
    confidence = 86
    confidenceBreakdown = { pattern: 82, historical: 88, sensor: 80, model: 85 }
  }
  // Generator related
  else if (description.includes('generator')) {
    rootCause = 'Fuel delivery schedule missed - tank below minimum level'
    evidence = ['Fuel level: 12% (minimum: 25%)', 'Last fuel delivery: 45 days ago', 'Generator test failure', 'Fuel pressure: low']
    recommendedActions = ['Schedule emergency fuel delivery', 'Verify fuel system operation', 'Test generator after refueling', 'Review fuel monitoring schedule']
    preventiveMeasures = ['Weekly fuel level check', 'Automated fuel monitoring alerts', 'Monthly generator test']
    confidence = 90
    confidenceBreakdown = { pattern: 88, historical: 92, sensor: 86, model: 91 }
  }
  // Default / Other
  else {
    rootCause = 'Based on pattern analysis, the fault appears to be related to component degradation in the cooling system'
    evidence = ['Historical failure pattern detected', 'Multiple similar cases in database', 'Sensor readings show degradation trend', 'Operating hours indicate wear']
    recommendedActions = ['Perform comprehensive system inspection', 'Check all relevant components', 'Review maintenance history', 'Run diagnostic tests']
    preventiveMeasures = ['Implement condition-based monitoring', 'Update maintenance schedule', 'Install additional sensors']
    confidence = 82
    confidenceBreakdown = { pattern: 85, historical: 80, sensor: 75, model: 84 }
  }

  // Add asset-specific evidence
  if (assetType.value && !evidence.some(e => e.includes(assetType.value))) {
    evidence.unshift(`Asset type: ${assetType.value}`)
  }
  if (errorCode.value && !evidence.some(e => e.includes(errorCode.value))) {
    evidence.push(`Error code: ${errorCode.value}`)
  }
  if (sensorReadings.value && !evidence.some(e => e.includes('sensor'))) {
    evidence.push(`Sensor readings: ${sensorReadings.value}`)
  }

  analysisResult.value = {
    rootCause,
    evidence,
    recommendedActions,
    preventiveMeasures,
    confidence,
    confidenceBreakdown,
    modelUsed: selectedModel.value === 'gpt4' ? 'GPT-4 Diagnostic Engine' :
        selectedModel.value === 'bert' ? 'BERT Fault Classifier' :
            selectedModel.value === 'lstm' ? 'LSTM Prediction Model' : 'Ensemble Decision Tree',
    analysisTime: avgAnalysisTime.value,
    similarCases: Math.floor(Math.random() * 50) + 10
  }

  // Add to history
  analysisHistory.value.unshift({
    timestamp: new Date().toLocaleString(),
    description: faultDescription.value.substring(0, 100),
    rootCause: rootCause,
    confidence: confidence
  })

  analysisDialogVisible.value = false
  analysisRunning.value = false
  ElMessage.success('AI analysis completed successfully')
}

const openAnalysisDialog = () => {
  if (!faultDescription.value) {
    ElMessage.warning('Please enter fault description first')
    return
  }
  runAIAnalysis()
}

const useExample = (example: string) => {
  faultDescription.value = example
}

const getConfidenceClass = (confidence: number) => {
  if (confidence >= 90) return 'high'
  if (confidence >= 80) return 'medium'
  return 'low'
}

const getConfidenceColor = (confidence: number) => {
  if (confidence >= 90) return '#67c23a'
  if (confidence >= 80) return '#409eff'
  if (confidence >= 70) return '#e6a23c'
  return '#f56c6c'
}

const getProgressColor = (progress: number) => {
  if (progress >= 80) return '#67c23a'
  if (progress >= 50) return '#409eff'
  return '#e6a23c'
}

const applyResolution = () => {
  ElMessage.success('Resolution applied to work order system')
}

const openFeedbackDialog = () => {
  selectedRating.value = 0
  feedbackComment.value = ''
  feedbackDialogVisible.value = true
}

const submitFeedback = () => {
  if (selectedRating.value === 0) {
    ElMessage.warning('Please select a rating')
    return
  }
  ElMessage.success('Thank you for your feedback! This helps improve AI accuracy.')
  feedbackDialogVisible.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting AI analysis report...')
}

const reanalyze = (row: any) => {
  faultDescription.value = row.description
  runAIAnalysis()
}

const refreshData = () => {
  ElMessage.success('Data refreshed')
}

// Lifecycle
onMounted(() => {
  let idx = 0
  const msgInterval = setInterval(() => {
    if (idx < loadingMessages.length - 1) {
      idx++
      loadingMessage.value = loadingMessages[idx]
    }
  }, 400)
  const progInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)
  setTimeout(() => {
    clearInterval(msgInterval)
    clearInterval(progInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
    }, 400)
  }, 2000)
})
</script>

<style scoped>
/* Loading Screen */
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
.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
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

/* Main Content */
.ai-rca-page {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}
.title-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  color: white;
  margin-bottom: 12px;
}
.header-title h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 8px 0;
}
.header-title .subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}
.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e2e8f0;
  background: white;
  color: #475569;
}
.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.action-btn.primary {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  border: none;
  color: white;
}
.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(139, 92, 246, 0.3);
}
.model-select {
  width: 180px;
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}
.kpi-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
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
.kpi-icon.accuracy { background: #d1fae5; color: #059669; }
.kpi-icon.confidence { background: #e8f4ff; color: #3b82f6; }
.kpi-icon.processed { background: #fef3c7; color: #d97706; }
.kpi-icon.time { background: #f3e8ff; color: #8b5cf6; }
.kpi-info { flex: 1; }
.kpi-value { font-size: 28px; font-weight: 700; color: #1a1a2e; }
.unit { font-size: 14px; font-weight: 400; margin-left: 2px; }
.kpi-label { font-size: 13px; color: #64748b; margin-top: 4px; }

/* Input Card */
.input-card {
  background: white;
  border-radius: 20px;
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
  color: #1a1a2e;
}
.card-tip {
  font-size: 12px;
  color: #94a3b8;
}
.analysis-input {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.input-row {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}
.input-group {
  flex: 1;
  min-width: 200px;
}
.input-group.full {
  width: 100%;
}
.input-group label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #475569;
  margin-bottom: 6px;
}
.form-input, .form-select, .form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 13px;
  background: white;
}
.form-textarea {
  resize: vertical;
  font-family: inherit;
}
.example-prompts {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
}
.example-label {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
}
.example-btn {
  padding: 4px 12px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  font-size: 11px;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s;
}
.example-btn:hover {
  background: #e8f4ff;
  border-color: #3b82f6;
  color: #2563eb;
}
.analyze-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 24px;
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 8px;
}
.analyze-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(139, 92, 246, 0.3);
}
.analyze-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* Results Card */
.results-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
.confidence-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}
.confidence-badge.high { background: #d1fae5; color: #059669; }
.confidence-badge.medium { background: #dbeafe; color: #1d4ed8; }
.confidence-badge.low { background: #fee2e2; color: #dc2626; }

.result-section {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 16px;
}
.section-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e8f4ff;
  color: #3b82f6;
  font-size: 22px;
}
.section-content {
  flex: 1;
}
.section-title {
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 8px;
  font-size: 14px;
}
.section-text {
  color: #475569;
  font-size: 14px;
  line-height: 1.5;
}
.evidence-list, .action-list, .preventive-list {
  margin: 0;
  padding-left: 20px;
}
.evidence-list li, .action-list li, .preventive-list li {
  color: #475569;
  font-size: 13px;
  margin-bottom: 6px;
}
.action-list li {
  display: flex;
  align-items: center;
  gap: 8px;
}
.action-list li .el-icon {
  color: #10b981;
}

.confidence-breakdown {
  margin-bottom: 24px;
  padding: 16px;
  background: #f1f5f9;
  border-radius: 16px;
}
.breakdown-title {
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 12px;
  font-size: 14px;
}
.breakdown-bars {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.breakdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
}
.breakdown-label {
  width: 120px;
  font-size: 12px;
  color: #64748b;
}
.breakdown-item :deep(.el-progress) {
  flex: 1;
}

.model-details {
  display: flex;
  gap: 24px;
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.model-info {
  display: flex;
  gap: 8px;
  font-size: 12px;
}
.model-label {
  color: #64748b;
}
.model-value {
  color: #1a1a2e;
  font-weight: 500;
}

.result-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}
.action-apply, .action-feedback, .action-export {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.action-apply {
  background: linear-gradient(135deg, #10b981, #059669);
  border: none;
  color: white;
}
.action-apply:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}
.action-feedback {
  background: white;
  border: 1px solid #e2e8f0;
  color: #475569;
}
.action-feedback:hover {
  background: #f1f5f9;
}
.action-export {
  background: white;
  border: 1px solid #e2e8f0;
  color: #475569;
}
.action-export:hover {
  background: #f1f5f9;
}

/* History Card */
.history-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* Analysis Dialog */
.analysis-progress {
  text-align: center;
  padding: 30px 20px;
}
.analysis-animation {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
}
.ai-pulse {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  border-radius: 50%;
  animation: pulse 1.5s ease-out infinite;
  opacity: 0.5;
}
.ai-logo {
  position: absolute;
  top: 12px;
  left: 12px;
  right: 12px;
  bottom: 12px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: #8b5cf6;
}
@keyframes pulse {
  0% { transform: scale(0.8); opacity: 0.8; }
  100% { transform: scale(1.2); opacity: 0; }
}
.analysis-step {
  font-size: 16px;
  color: #1a1a2e;
  margin-bottom: 20px;
  font-weight: 500;
}
.analysis-thinking {
  margin-top: 16px;
}
.analysis-thinking .dot {
  font-size: 24px;
  animation: thinking 1.4s infinite;
  display: inline-block;
}
.analysis-thinking .dot:nth-child(1) { animation-delay: 0s; }
.analysis-thinking .dot:nth-child(2) { animation-delay: 0.2s; }
.analysis-thinking .dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes thinking {
  0%, 60%, 100% { opacity: 0.3; transform: translateY(0); }
  30% { opacity: 1; transform: translateY(-4px); }
}

/* Feedback Dialog */
.feedback-content {
  text-align: center;
}
.feedback-rating {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin: 20px 0;
}
.rating-star {
  background: none;
  border: none;
  font-size: 28px;
  cursor: pointer;
  color: #fbbf24;
  transition: transform 0.2s;
}
.rating-star:hover {
  transform: scale(1.1);
}
.feedback-comment {
  text-align: left;
  margin-top: 16px;
}
.feedback-comment label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #475569;
  margin-bottom: 8px;
}
.feedback-comment textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 13px;
  resize: vertical;
}

:deep(.el-table) { border-radius: 12px; }
:deep(.el-table th) { background-color: #fafafa; font-weight: 600; }
:deep(.el-progress__text) { font-size: 11px !important; }
</style>