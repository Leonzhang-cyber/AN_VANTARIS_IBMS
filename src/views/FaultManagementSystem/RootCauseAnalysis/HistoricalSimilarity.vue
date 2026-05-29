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
        <div class="loading-tip">Historical Similarity</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Historical Similarity Page Content -->
  <div v-else class="similarity-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <div class="title-badge">
          <el-icon><TrendCharts /></el-icon>
          <span>FMS - AI Analytics</span>
        </div>
        <h1>Historical Similarity Analysis</h1>
        <p class="subtitle">AI-powered pattern matching to identify similar historical faults and predict root causes</p>
      </div>
      <div class="header-actions">
        <button class="action-btn" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          <span>Refresh</span>
        </button>
        <button class="action-btn primary" @click="runSimilarityAnalysis" :loading="analysisRunning">
          <el-icon><TrendCharts /></el-icon>
          <span>{{ analysisRunning ? 'Analyzing...' : 'Run Similarity Analysis' }}</span>
        </button>
        <select v-model="timeRange" class="time-range-select" @change="onTimeRangeChange">
          <option value="month">Last 30 Days</option>
          <option value="quarter">Last 90 Days</option>
          <option value="year">Last Year</option>
          <option value="all">All History</option>
        </select>
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-icon total">
          <el-icon><Document /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ totalHistoricalFaults }}</div>
          <div class="kpi-label">Historical Faults</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon resolved">
          <el-icon><CircleCheckFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ resolvedCount }}</div>
          <div class="kpi-label">Resolved Cases</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon similarity">
          <el-icon><Connection /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ avgSimilarityDisplay }}%</div>
          <div class="kpi-label">Avg Match Score</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon accuracy">
          <el-icon><Medal /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ predictionAccuracy }}%</div>
          <div class="kpi-label">Prediction Accuracy</div>
        </div>
      </div>
    </div>

    <!-- Active Fault Input Section -->
    <div class="input-card">
      <div class="card-header">
        <h3>Current Fault Analysis</h3>
        <span class="card-tip">Enter fault details to find similar historical cases</span>
      </div>
      <div class="fault-input">
        <div class="input-row">
          <div class="input-group">
            <label>Fault Title</label>
            <input type="text" v-model="currentFault.title" placeholder="e.g., Chiller High Pressure Trip" class="form-input" />
          </div>
          <div class="input-group">
            <label>Category</label>
            <select v-model="currentFault.category" class="form-select">
              <option value="">Select Category</option>
              <option value="HVAC">HVAC</option>
              <option value="Electrical">Electrical</option>
              <option value="Plumbing">Plumbing</option>
              <option value="Security">Security</option>
              <option value="DCIM">DCIM</option>
              <option value="BMS">BMS</option>
            </select>
          </div>
          <div class="input-group">
            <label>Asset / Equipment</label>
            <input type="text" v-model="currentFault.asset" placeholder="e.g., Chiller-02" class="form-input" />
          </div>
        </div>
        <div class="input-row">
          <div class="input-group full">
            <label>Symptoms / Description</label>
            <textarea v-model="currentFault.symptoms" rows="3" placeholder="Describe the fault symptoms, error codes, and observed behavior..." class="form-textarea"></textarea>
          </div>
        </div>
        <div class="input-row">
          <div class="input-group">
            <label>Error Code (if any)</label>
            <input type="text" v-model="currentFault.errorCode" placeholder="e.g., ERR-101" class="form-input" />
          </div>
          <div class="input-group">
            <label>Sensor Readings</label>
            <input type="text" v-model="currentFault.sensorReadings" placeholder="e.g., Pressure: 180PSI, Temp: 35°C" class="form-input" />
          </div>
        </div>
        <button class="analyze-btn" @click="findSimilarFaults" :disabled="!currentFault.title">
          <el-icon><Search /></el-icon> Find Similar Faults
        </button>
      </div>
    </div>

    <!-- Similarity Results -->
    <div class="results-card" v-loading="resultsLoading">
      <div class="card-header">
        <h3>Similar Historical Faults</h3>
        <span class="results-count">{{ similarFaults.length }} matches found</span>
      </div>

      <div v-if="similarFaults.length === 0 && !resultsLoading" class="empty-results">
        <el-icon><Search /></el-icon>
        <p>No similar faults found</p>
        <span>Try adjusting the fault description or selecting a different category</span>
      </div>

      <div v-else class="similarity-list">
        <div v-for="fault in paginatedSimilarFaults" :key="fault.id" class="similarity-card" :class="getSimilarityClass(fault.similarity)">
          <div class="similarity-header">
            <div class="fault-info">
              <div class="fault-title">{{ fault.title }}</div>
              <div class="fault-meta">
                <span class="fault-date">{{ fault.occurredAt }}</span>
                <span class="fault-category">{{ fault.category }}</span>
                <span class="fault-asset">{{ fault.asset }}</span>
              </div>
            </div>
            <div class="similarity-score">
              <div class="score-circle">
                <span class="score-value">{{ fault.similarity }}%</span>
              </div>
              <span class="score-label">Match</span>
            </div>
          </div>
          <div class="similarity-details">
            <div class="detail-row">
              <span class="detail-label">Root Cause:</span>
              <span class="detail-value">{{ fault.rootCause }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Resolution:</span>
              <span class="detail-value">{{ fault.resolution }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Resolution Time:</span>
              <span class="detail-value">{{ fault.resolutionTime }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Matched Symptoms:</span>
              <div class="symptom-tags">
                <span v-for="sym in fault.matchedSymptoms" :key="sym" class="symptom-tag">{{ sym }}</span>
              </div>
            </div>
          </div>
          <div class="similarity-actions">
            <button class="action-view" @click="viewFaultDetail(fault)">View Full Case</button>
            <button class="action-apply" @click="applyResolution(fault)">Apply Resolution</button>
          </div>
        </div>
      </div>

      <div class="pagination-wrapper" v-if="similarFaults.length > 0">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[5, 10, 20]"
            :total="similarFaults.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Similarity Heatmap / Pattern Visualization -->
    <div class="heatmap-card">
      <div class="card-header">
        <h3>Similarity Pattern Heatmap</h3>
        <el-radio-group v-model="heatmapType" size="small" @change="onHeatmapTypeChange">
          <el-radio-button label="category">By Category</el-radio-button>
          <el-radio-button label="asset">By Asset</el-radio-button>
          <el-radio-button label="time">By Time</el-radio-button>
        </el-radio-group>
      </div>
      <div class="heatmap-container" ref="heatmapChartRef"></div>
    </div>

    <!-- Top Matching Patterns -->
    <div class="patterns-card">
      <div class="card-header">
        <h3>Top Matching Patterns</h3>
      </div>
      <div class="patterns-grid">
        <div v-for="pattern in topPatterns" :key="pattern.id" class="pattern-card">
          <div class="pattern-header">
            <div class="pattern-name">{{ pattern.name }}</div>
            <div class="pattern-count">{{ pattern.count }} cases</div>
          </div>
          <div class="pattern-symptoms">
            <div v-for="sym in pattern.symptoms.slice(0, 3)" :key="sym" class="pattern-symptom">{{ sym }}</div>
          </div>
          <div class="pattern-confidence">
            <el-progress :percentage="pattern.confidence" :stroke-width="6" :show-text="true" />
          </div>
        </div>
      </div>
    </div>

    <!-- Fault Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" title="Historical Fault Details" width="650px">
      <div class="detail-content" v-if="selectedFault">
        <div class="detail-section">
          <div class="detail-title">Fault Information</div>
          <div class="detail-grid">
            <div class="detail-item"><span class="label">ID:</span> #{{ selectedFault.id }}</div>
            <div class="detail-item"><span class="label">Title:</span> {{ selectedFault.title }}</div>
            <div class="detail-item"><span class="label">Category:</span> {{ selectedFault.category }}</div>
            <div class="detail-item"><span class="label">Asset:</span> {{ selectedFault.asset }}</div>
            <div class="detail-item"><span class="label">Occurred:</span> {{ selectedFault.occurredAt }}</div>
            <div class="detail-item"><span class="label">Resolved:</span> {{ selectedFault.resolvedAt }}</div>
          </div>
        </div>
        <div class="detail-section">
          <div class="detail-title">Root Cause Analysis</div>
          <div class="detail-item">{{ selectedFault.rootCause }}</div>
        </div>
        <div class="detail-section">
          <div class="detail-title">Resolution Actions</div>
          <ul class="action-list">
            <li v-for="action in selectedFault.resolutionActions" :key="action">{{ action }}</li>
          </ul>
        </div>
        <div class="detail-section">
          <div class="detail-title">Preventive Measures</div>
          <ul class="action-list">
            <li v-for="measure in selectedFault.preventiveMeasures" :key="measure">{{ measure }}</li>
          </ul>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="applyResolution(selectedFault)">Apply Resolution</el-button>
      </template>
    </el-dialog>

    <!-- Analysis Progress Dialog -->
    <el-dialog v-model="analysisDialogVisible" title="AI Similarity Analysis" width="500px" :close-on-click-modal="false">
      <div class="analysis-progress">
        <div class="analysis-icon">
          <el-icon v-if="analysisStep === 0"><Loading /></el-icon>
          <el-icon v-else-if="analysisStep === 1"><Document /></el-icon>
          <el-icon v-else-if="analysisStep === 2"><Connection /></el-icon>
          <el-icon v-else-if="analysisStep === 3"><TrendCharts /></el-icon>
          <el-icon v-else><CircleCheckFilled /></el-icon>
        </div>
        <div class="analysis-step">{{ analysisSteps[analysisStep] }}</div>
        <el-progress :percentage="analysisProgress" :stroke-width="8" :show-text="false" />
        <div class="analysis-result" v-if="analysisStep === 4">
          <p>✅ Analysis complete!</p>
          <p>📊 Found {{ similarFaults.length }} similar cases with {{ avgSimilarityDisplay }}% average match</p>
        </div>
      </div>
      <template #footer>
        <el-button v-if="analysisStep === 4" type="primary" @click="analysisDialogVisible = false">View Results</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import {
  Refresh, Download, WarningFilled, Document, CircleCheckFilled,
  Connection, Medal, TrendCharts, Search, Loading
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

// Loading State
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const resultsLoading = ref(false)
const analysisRunning = ref(false)
const analysisDialogVisible = ref(false)
const analysisStep = ref(0)
const analysisProgress = ref(0)
const loadingMessages = ['Preparing...', 'Loading historical database...', 'Initializing similarity engine...', 'Almost ready...']

// Data Models
interface HistoricalFault {
  id: number
  title: string
  category: string
  asset: string
  occurredAt: string
  resolvedAt: string
  rootCause: string
  resolution: string
  resolutionTime: string
  resolutionActions: string[]
  preventiveMeasures: string[]
  symptoms: string[]
  errorCode?: string
  sensorReadings?: string
}

interface SimilarFault extends HistoricalFault {
  similarity: number
  matchedSymptoms: string[]
}

interface Pattern {
  id: number
  name: string
  count: number
  symptoms: string[]
  confidence: number
}

// State
const timeRange = ref('month')
const heatmapType = ref('category')
const currentPage = ref(1)
const pageSize = ref(5)
const detailDialogVisible = ref(false)
const selectedFault = ref<HistoricalFault | null>(null)
const analysisSteps = ['Connecting to AI Engine...', 'Extracting fault features...', 'Comparing with historical data...', 'Ranking similar cases...', 'Analysis Complete!']

// 默认填充的当前故障数据
const currentFault = ref({
  title: 'Chiller-02 High Pressure Trip',
  category: 'HVAC',
  asset: 'Chiller-02',
  symptoms: 'High pressure alarm triggered, chiller shutdown, cooling tower fan not responding, building temperature rising',
  errorCode: 'CH-102',
  sensorReadings: 'Pressure: 220PSI, Flow: 45%, Temperature: 38°C'
})

// Chart refs
const heatmapChartRef = ref<HTMLElement | null>(null)
let heatmapChart: echarts.ECharts | null = null

// Mock Historical Data
const historicalFaults = ref<HistoricalFault[]>([
  { id: 1001, title: 'Chiller-02 High Pressure Trip', category: 'HVAC', asset: 'Chiller-02', occurredAt: '2025-05-15 14:30:00', resolvedAt: '2025-05-15 18:45:00', rootCause: 'Condenser water flow reduced due to cooling tower fan bearing failure', resolution: 'Replaced cooling tower fan bearings and reset chiller', resolutionTime: '4h 15m', resolutionActions: ['Replaced fan bearings', 'Cleaned condenser tubes', 'Reset chiller controller'], preventiveMeasures: ['Monthly fan bearing inspection', 'Quarterly vibration analysis'], symptoms: ['High pressure alarm', 'Reduced cooling capacity', 'Fan vibration detected'], errorCode: 'CH-102', sensorReadings: 'Pressure: 220PSI, Flow: 45%' },
  { id: 1002, title: 'Chiller-01 High Pressure Alarm', category: 'HVAC', asset: 'Chiller-01', occurredAt: '2025-05-10 09:15:00', resolvedAt: '2025-05-10 12:30:00', rootCause: 'Condenser fouling due to poor water quality', resolution: 'Chemical cleaning of condenser tubes', resolutionTime: '3h 15m', resolutionActions: ['Chemical cleaning', 'Water treatment adjustment'], preventiveMeasures: ['Weekly water quality testing', 'Monthly condenser inspection'], symptoms: ['High pressure alarm', 'Reduced efficiency'], errorCode: 'CH-101', sensorReadings: 'Pressure: 210PSI' },
  { id: 1003, title: 'UPS-01 Input Power Loss', category: 'Electrical', asset: 'UPS-01', occurredAt: '2025-05-20 07:30:00', resolvedAt: '2025-05-20 10:00:00', rootCause: 'Main breaker tripped due to downstream short circuit', resolution: 'Isolated faulty circuit and reset breaker', resolutionTime: '2h 30m', resolutionActions: ['Identified short circuit location', 'Repaired damaged cable', 'Reset breaker'], preventiveMeasures: ['Quarterly thermal imaging', 'Cable insulation testing'], symptoms: ['Power loss', 'Breaker tripped', 'UPS on battery'], errorCode: 'UPS-401', sensorReadings: 'Input voltage: 0V' },
  { id: 1004, title: 'UPS Battery Low Warning', category: 'Electrical', asset: 'UPS-02', occurredAt: '2025-05-18 11:00:00', resolvedAt: '2025-05-18 16:30:00', rootCause: 'Battery end-of-life reached after 4 years', resolution: 'Replaced battery string', resolutionTime: '5h 30m', resolutionActions: ['Battery capacity test', 'Replaced 40 batteries', 'System test'], preventiveMeasures: ['Annual battery capacity test', 'Quarterly impedance check'], symptoms: ['Low battery warning', 'Reduced runtime'], errorCode: 'UPS-402', sensorReadings: 'Battery voltage: 42V' },
  { id: 1005, title: 'Server Room Temperature High', category: 'DCIM', asset: 'CRAC-03', occurredAt: '2025-05-25 08:00:00', resolvedAt: '2025-05-25 14:20:00', rootCause: 'CRAC compressor capacitor failure', resolution: 'Replaced compressor capacitor and recharged refrigerant', resolutionTime: '6h 20m', resolutionActions: ['Diagnosed compressor issue', 'Replaced capacitor', 'Recharged refrigerant', 'Tested operation'], preventiveMeasures: ['Annual compressor inspection', 'Capacitor replacement schedule'], symptoms: ['High temperature alarm', 'CRAC not cooling', 'Compressor not running'], errorCode: 'DC-305', sensorReadings: 'Temp: 32°C, Supply air: 24°C' },
  { id: 1006, title: 'AHU-201 Filter Clogged', category: 'HVAC', asset: 'AHU-201', occurredAt: '2025-05-12 13:00:00', resolvedAt: '2025-05-12 14:30:00', rootCause: 'Filter maintenance overdue', resolution: 'Replaced air filters', resolutionTime: '1h 30m', resolutionActions: ['Replaced MERV-13 filters', 'Reset pressure sensor'], preventiveMeasures: ['Monthly filter inspection', '60-day replacement schedule'], symptoms: ['Low airflow', 'High static pressure', 'Fan speed high'], errorCode: 'AH-205', sensorReadings: 'Pressure: 180Pa, Airflow: 65%' },
  { id: 1007, title: 'VFD-105 Overcurrent Fault', category: 'Electrical', asset: 'VFD-105', occurredAt: '2025-05-22 15:00:00', resolvedAt: '2025-05-22 17:00:00', rootCause: 'Motor bearing seizure', resolution: 'Replaced motor bearings and reset VFD', resolutionTime: '2h', resolutionActions: ['Motor inspection', 'Bearing replacement', 'VFD parameter reset'], preventiveMeasures: ['Motor vibration monitoring', 'Lubrication schedule'], symptoms: ['Overcurrent fault', 'Motor overheating', 'VFD trip'], errorCode: 'VFD-601', sensorReadings: 'Current: 150A' },
  { id: 1008, title: 'Water Leak Detected - Pump Room', category: 'Plumbing', asset: 'Booster Pump', occurredAt: '2025-05-08 09:00:00', resolvedAt: '2025-05-08 12:00:00', rootCause: 'Mechanical seal failure', resolution: 'Replaced pump mechanical seal', resolutionTime: '3h', resolutionActions: ['Isolated water supply', 'Removed pump', 'Replaced seal', 'Tested operation'], preventiveMeasures: ['Quarterly seal inspection', 'Vibration monitoring'], symptoms: ['Water leak alarm', 'Humidity high', 'Water pressure drop'], errorCode: 'PL-501', sensorReadings: 'Humidity: 75%' }
])

// Computed
const totalHistoricalFaults = computed(() => historicalFaults.value.length)
const resolvedCount = computed(() => historicalFaults.value.length)

// 相似故障列表
const similarFaults = ref<SimilarFault[]>([])
const avgSimilarityDisplay = computed(() => {
  if (similarFaults.value.length === 0) return 0
  const avg = similarFaults.value.reduce((sum, f) => sum + f.similarity, 0) / similarFaults.value.length
  return Math.round(avg)
})
const predictionAccuracy = computed(() => 87)

const paginatedSimilarFaults = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return similarFaults.value.slice(start, end)
})

const topPatterns = ref<Pattern[]>([
  { id: 1, name: 'Chiller High Pressure', count: 12, symptoms: ['High pressure alarm', 'Reduced cooling', 'Flow low'], confidence: 94 },
  { id: 2, name: 'UPS Power Failure', count: 8, symptoms: ['Power loss', 'Breaker trip', 'UPS alarm'], confidence: 91 },
  { id: 3, name: 'High Temperature Event', count: 15, symptoms: ['Temperature high', 'Cooling failure', 'CRAC alarm'], confidence: 89 },
  { id: 4, name: 'Filter Clog Pattern', count: 10, symptoms: ['Low airflow', 'High pressure', 'Fan speed high'], confidence: 86 }
])

// 初始化相似度搜索
const initSimilaritySearch = () => {
  const searchText = currentFault.value.title.toLowerCase()
  const searchSymptoms = currentFault.value.symptoms.toLowerCase()
  const searchCategory = currentFault.value.category
  const searchAsset = currentFault.value.asset.toLowerCase()

  const results = historicalFaults.value.map(fault => {
    let score = 0
    const matchedSymptoms: string[] = []

    if (fault.title.toLowerCase().includes(searchText) || searchText.includes(fault.title.toLowerCase())) {
      score += 40
      matchedSymptoms.push(fault.title)
    }
    if (fault.category === searchCategory) {
      score += 20
    }
    if (fault.asset.toLowerCase().includes(searchAsset) || searchAsset.includes(fault.asset.toLowerCase())) {
      score += 15
    }
    fault.symptoms.forEach(symptom => {
      if (searchSymptoms.includes(symptom.toLowerCase()) || symptom.toLowerCase().includes(searchSymptoms.substring(0, 30))) {
        score += 5
        if (!matchedSymptoms.includes(symptom)) matchedSymptoms.push(symptom)
      }
    })
    if (currentFault.value.errorCode && fault.errorCode === currentFault.value.errorCode) {
      score += 20
      matchedSymptoms.push(`Error code: ${fault.errorCode}`)
    }

    const similarity = Math.min(100, score + Math.random() * 10)
    return { ...fault, similarity: Math.round(similarity), matchedSymptoms: matchedSymptoms.slice(0, 5) }
  })

  similarFaults.value = results.filter(r => r.similarity > 50).sort((a, b) => b.similarity - a.similarity)
}

// 热力图数据生成
const getHeatmapData = () => {
  if (heatmapType.value === 'category') {
    const categories = ['HVAC', 'Electrical', 'DCIM', 'Plumbing', 'Security', 'BMS']
    const similarityMatrix = [
      [100, 45, 32, 28, 15, 42],
      [45, 100, 38, 35, 22, 48],
      [32, 38, 100, 42, 28, 55],
      [28, 35, 42, 100, 35, 38],
      [15, 22, 28, 35, 100, 32],
      [42, 48, 55, 38, 32, 100]
    ]
    const data: [number, number, number][] = []
    for (let i = 0; i < categories.length; i++) {
      for (let j = 0; j < categories.length; j++) {
        data.push([j, i, similarityMatrix[i][j]])
      }
    }
    return { xAxis: categories, yAxis: categories, data }
  } else if (heatmapType.value === 'asset') {
    const assets = ['Chiller-02', 'Chiller-01', 'UPS-01', 'CRAC-03', 'AHU-201', 'VFD-105']
    const similarityMatrix = [
      [100, 85, 25, 30, 35, 28],
      [85, 100, 28, 32, 38, 30],
      [25, 28, 100, 35, 20, 55],
      [30, 32, 35, 100, 42, 38],
      [35, 38, 20, 42, 100, 45],
      [28, 30, 55, 38, 45, 100]
    ]
    const data: [number, number, number][] = []
    for (let i = 0; i < assets.length; i++) {
      for (let j = 0; j < assets.length; j++) {
        data.push([j, i, similarityMatrix[i][j]])
      }
    }
    return { xAxis: assets, yAxis: assets, data }
  } else {
    const timePeriods = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    const similarityMatrix = [
      [100, 65, 45, 30],
      [65, 100, 55, 40],
      [45, 55, 100, 60],
      [30, 40, 60, 100]
    ]
    const data: [number, number, number][] = []
    for (let i = 0; i < timePeriods.length; i++) {
      for (let j = 0; j < timePeriods.length; j++) {
        data.push([j, i, similarityMatrix[i][j]])
      }
    }
    return { xAxis: timePeriods, yAxis: timePeriods, data }
  }
}

// 初始化热力图
const initHeatmapChart = () => {
  nextTick(() => {
    if (!heatmapChartRef.value) {
      console.warn('heatmapChartRef is not ready')
      return
    }
    if (heatmapChart) {
      heatmapChart.dispose()
    }

    heatmapChart = echarts.init(heatmapChartRef.value)
    const chartData = getHeatmapData()

    heatmapChart.setOption({
      tooltip: {
        position: 'top',
        formatter: (params: any) => {
          return `${chartData.yAxis[params.value[1]]} ↔ ${chartData.xAxis[params.value[0]]}: ${params.value[2]}% similarity`
        }
      },
      xAxis: {
        type: 'category',
        data: chartData.xAxis,
        axisLabel: { rotate: 45, interval: 0, fontSize: 10 }
      },
      yAxis: {
        type: 'category',
        data: chartData.yAxis,
        axisLabel: { fontSize: 10 }
      },
      visualMap: {
        min: 0,
        max: 100,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: 0,
        inRange: {
          color: ['#ebedf0', '#dbeafe', '#bfdbfe', '#93c5fd', '#60a5fa', '#3b82f6', '#2563eb']
        }
      },
      series: [{
        type: 'heatmap',
        data: chartData.data,
        label: {
          show: true,
          formatter: (params: any) => params.data[2] + '%',
          fontSize: 10
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    })
  })
}

// 热力图类型切换
const onHeatmapTypeChange = () => {
  initHeatmapChart()
}

// Helper Functions
const getSimilarityClass = (similarity: number) => {
  if (similarity >= 85) return 'high-match'
  if (similarity >= 70) return 'medium-match'
  return 'low-match'
}

// Find Similar Faults
const findSimilarFaults = async () => {
  if (!currentFault.value.title) {
    ElMessage.warning('Please enter fault title')
    return
  }

  resultsLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))

  const searchText = currentFault.value.title.toLowerCase()
  const searchSymptoms = currentFault.value.symptoms.toLowerCase()
  const searchCategory = currentFault.value.category
  const searchAsset = currentFault.value.asset.toLowerCase()

  const results = historicalFaults.value.map(fault => {
    let score = 0
    const matchedSymptoms: string[] = []

    if (fault.title.toLowerCase().includes(searchText) || searchText.includes(fault.title.toLowerCase())) {
      score += 40
      matchedSymptoms.push(fault.title)
    }
    if (fault.category === searchCategory) {
      score += 20
    }
    if (fault.asset.toLowerCase().includes(searchAsset) || searchAsset.includes(fault.asset.toLowerCase())) {
      score += 15
    }
    fault.symptoms.forEach(symptom => {
      if (searchSymptoms.includes(symptom.toLowerCase()) || symptom.toLowerCase().includes(searchSymptoms.substring(0, 30))) {
        score += 5
        if (!matchedSymptoms.includes(symptom)) matchedSymptoms.push(symptom)
      }
    })
    if (currentFault.value.errorCode && fault.errorCode === currentFault.value.errorCode) {
      score += 20
      matchedSymptoms.push(`Error code: ${fault.errorCode}`)
    }

    const similarity = Math.min(100, score + Math.random() * 10)
    return { ...fault, similarity: Math.round(similarity), matchedSymptoms: matchedSymptoms.slice(0, 5) }
  })

  similarFaults.value = results.filter(r => r.similarity > 50).sort((a, b) => b.similarity - a.similarity)
  resultsLoading.value = false

  if (similarFaults.value.length === 0) {
    ElMessage.info('No similar faults found. Try broadening your search criteria.')
  } else {
    ElMessage.success(`Found ${similarFaults.value.length} similar cases`)
  }
}

const runSimilarityAnalysis = async () => {
  analysisRunning.value = true
  analysisDialogVisible.value = true
  analysisStep.value = 0
  analysisProgress.value = 0

  for (let step = 0; step <= 4; step++) {
    analysisStep.value = step
    for (let p = 0; p <= 100; p += 20) {
      if (step === 4 && p > 0) break
      analysisProgress.value = step * 25 + p / 4
      await new Promise(resolve => setTimeout(resolve, 100))
    }
    if (step < 4) await new Promise(resolve => setTimeout(resolve, 500))
  }

  analysisProgress.value = 100
  setTimeout(() => {
    analysisRunning.value = false
  }, 500)
}

const viewFaultDetail = (fault: SimilarFault) => {
  selectedFault.value = fault
  detailDialogVisible.value = true
}

const applyResolution = (fault: HistoricalFault | SimilarFault | null) => {
  if (!fault) return
  ElMessage.success(`Resolution applied: ${fault.resolution}`)
  detailDialogVisible.value = false
}

const refreshData = () => {
  initSimilaritySearch()
  initHeatmapChart()
  ElMessage.success('Data refreshed')
}

const onTimeRangeChange = () => {
  ElMessage.info(`Switched to ${timeRange.value} view`)
}

// Resize handler
const handleResize = () => {
  if (heatmapChart) {
    heatmapChart.resize()
  }
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// Watch for heatmapType changes
watch(heatmapType, () => {
  initHeatmapChart()
})

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
      initSimilaritySearch()
      initHeatmapChart()
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (heatmapChart) {
    heatmapChart.dispose()
  }
})
</script>

<style scoped>
/* 保持原有样式，添加热力图容器高度保证 */
.heatmap-container {
  height: 400px;
  width: 100%;
  min-height: 400px;
}

/* 其他样式保持不变 */
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
.similarity-page {
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
.time-range-select {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: white;
  font-size: 13px;
  cursor: pointer;
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
.kpi-icon.total { background: #e8f4ff; color: #3b82f6; }
.kpi-icon.resolved { background: #d1fae5; color: #059669; }
.kpi-icon.similarity { background: #fef3c7; color: #d97706; }
.kpi-icon.accuracy { background: #f3e8ff; color: #8b5cf6; }
.kpi-info { flex: 1; }
.kpi-value { font-size: 28px; font-weight: 700; color: #1a1a2e; }
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
.fault-input {
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
}
.analyze-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 24px;
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
}

/* Results Card */
.results-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
.results-count {
  font-size: 13px;
  color: #64748b;
  background: #f1f5f9;
  padding: 4px 12px;
  border-radius: 20px;
}
.empty-results {
  text-align: center;
  padding: 60px 20px;
}
.empty-results .el-icon {
  font-size: 48px;
  color: #cbd5e1;
  margin-bottom: 16px;
}
.empty-results p {
  font-size: 16px;
  font-weight: 500;
  color: #475569;
  margin: 0 0 8px 0;
}
.empty-results span {
  font-size: 13px;
  color: #94a3b8;
}

.similarity-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.similarity-card {
  background: #f8fafc;
  border-radius: 16px;
  padding: 20px;
  border-left: 4px solid;
  transition: all 0.2s;
}
.similarity-card:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.similarity-card.high-match { border-left-color: #10b981; }
.similarity-card.medium-match { border-left-color: #f59e0b; }
.similarity-card.low-match { border-left-color: #94a3b8; }
.similarity-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}
.fault-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 6px;
}
.fault-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: #64748b;
  flex-wrap: wrap;
}
.fault-date, .fault-category, .fault-asset {
  padding: 2px 8px;
  background: #f1f5f9;
  border-radius: 12px;
}
.similarity-score {
  text-align: center;
}
.score-circle {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #10b981, #059669);
  border-radius: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.high-match .score-circle { background: linear-gradient(135deg, #10b981, #059669); }
.medium-match .score-circle { background: linear-gradient(135deg, #f59e0b, #d97706); }
.low-match .score-circle { background: linear-gradient(135deg, #94a3b8, #64748b); }
.score-value {
  font-size: 20px;
  font-weight: 700;
  color: white;
}
.score-label {
  font-size: 11px;
  color: #64748b;
  margin-top: 4px;
  display: block;
}
.similarity-details {
  margin-bottom: 16px;
}
.detail-row {
  display: flex;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 8px;
}
.detail-label {
  width: 110px;
  font-size: 12px;
  color: #64748b;
}
.detail-value {
  flex: 1;
  font-size: 13px;
  color: #1a1a2e;
}
.symptom-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.symptom-tag {
  font-size: 10px;
  padding: 2px 8px;
  background: #dbeafe;
  color: #1d4ed8;
  border-radius: 12px;
}
.similarity-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}
.action-view, .action-apply {
  padding: 6px 16px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.action-view {
  background: white;
  border: 1px solid #e2e8f0;
  color: #475569;
}
.action-view:hover {
  background: #f1f5f9;
}
.action-apply {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  border: none;
  color: white;
}
.action-apply:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}
.pagination-wrapper {
  padding-top: 20px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #e2e8f0;
  margin-top: 20px;
}

/* Heatmap Card */
.heatmap-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* Patterns Card */
.patterns-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
.patterns-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.pattern-card {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
}
.pattern-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.pattern-name {
  font-weight: 600;
  color: #1a1a2e;
}
.pattern-count {
  font-size: 11px;
  color: #64748b;
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 12px;
}
.pattern-symptoms {
  margin-bottom: 12px;
}
.pattern-symptom {
  font-size: 11px;
  color: #475569;
  margin-bottom: 4px;
  padding: 2px 0;
}
.pattern-confidence {
  margin-top: 8px;
}

/* Dialog */
.detail-content { padding: 8px 0; }
.detail-section {
  margin-bottom: 24px;
}
.detail-title {
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 12px;
  font-size: 15px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e2e8f0;
}
.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
.detail-item {
  font-size: 13px;
}
.detail-item .label {
  color: #64748b;
  margin-right: 8px;
}
.action-list {
  margin: 8px 0 0 20px;
  padding: 0;
}
.action-list li {
  font-size: 13px;
  color: #475569;
  margin-bottom: 6px;
}

/* Analysis Dialog */
.analysis-progress {
  text-align: center;
  padding: 20px;
}
.analysis-icon {
  font-size: 48px;
  color: #8b5cf6;
  margin-bottom: 20px;
}
.analysis-step {
  font-size: 16px;
  color: #1a1a2e;
  margin-bottom: 20px;
  font-weight: 500;
}
.analysis-result {
  margin-top: 20px;
  padding: 16px;
  background: #d1fae5;
  border-radius: 12px;
  color: #059669;
  font-size: 14px;
}

:deep(.el-table) { border-radius: 12px; }
:deep(.el-table th) { background-color: #fafafa; font-weight: 600; }
:deep(.el-progress__text) { font-size: 11px !important; }
</style>