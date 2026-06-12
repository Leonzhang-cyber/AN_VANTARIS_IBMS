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
  Search as SearchIcon, Link, Aim, SuccessFilled,
  Filter
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing fault database...',
  'Building similarity index...',
  'Preparing search engine...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchQuery = ref('')
const searchResults = ref<any[]>([])
const selectedSeverity = ref('all')
const selectedSimilarity = ref('all')
const detailsVisible = ref(false)
const chartRef = ref(null)

let similarityChart: echarts.ECharts | null = null

// Severity filters
const severityOptions = [
  { value: 'all', label: 'All Severities' },
  { value: 'critical', label: 'Critical', color: '#F56C6C' },
  { value: 'high', label: 'High', color: '#F56C6C' },
  { value: 'medium', label: 'Medium', color: '#E6A23C' },
  { value: 'low', label: 'Low', color: '#67C23A' }
]

// Similarity filters
const similarityOptions = [
  { value: 'all', label: 'All Similarity' },
  { value: 'high', label: 'High Similarity (>80%)' },
  { value: 'medium', label: 'Medium Similarity (50-80%)' },
  { value: 'low', label: 'Low Similarity (<50%)' }
]

// Fault database
const faultDatabase = ref([
  {
    id: 'FLT001', fault: 'Chiller High Temperature Alarm', severity: 'critical',
    symptoms: ['Temperature exceeds 35°C', 'High pressure alarm', 'Compressor cycling'],
    rootCause: 'Compressor failure / Refrigerant leak',
    solution: 'Replace compressor, repair leak',
    confidence: 92, resolvedBy: 'HVAC Team',
    timestamp: '2024-01-15', resolvedAt: '2024-01-18',
    equipment: 'Chiller-1', system: 'HVAC'
  },
  {
    id: 'FLT002', fault: 'AHU Low Airflow', severity: 'high',
    symptoms: ['Reduced air output', 'High static pressure', 'Filter dirty'],
    rootCause: 'Clogged filters / Duct blockage',
    solution: 'Replace filters, inspect ducts',
    confidence: 88, resolvedBy: 'HVAC Team',
    timestamp: '2024-01-10', resolvedAt: '2024-01-12',
    equipment: 'AHU-2', system: 'HVAC'
  },
  {
    id: 'FLT003', fault: 'VFD Pump Vibration', severity: 'medium',
    symptoms: ['Excessive vibration', 'Unusual noise', 'Temperature rise'],
    rootCause: 'Bearing wear / Misalignment',
    solution: 'Replace bearings, realign shaft',
    confidence: 94, resolvedBy: 'Mechanical Team',
    timestamp: '2024-01-05', resolvedAt: '2024-01-08',
    equipment: 'VFD Pump', system: 'Pump'
  },
  {
    id: 'FLT004', fault: 'Switchboard Overheating', severity: 'critical',
    symptoms: ['High temperature reading', 'Burning smell', 'Voltage fluctuation'],
    rootCause: 'Loose connections / Overload',
    solution: 'Tighten connections, balance load',
    confidence: 91, resolvedBy: 'Electrical Team',
    timestamp: '2024-01-03', resolvedAt: '2024-01-06',
    equipment: 'Main Switchboard', system: 'Electrical'
  },
  {
    id: 'FLT005', fault: 'Cooling Tower Fan Failure', severity: 'critical',
    symptoms: ['Fan not running', 'Motor overheating', 'Breaker trips'],
    rootCause: 'Motor bearing failure',
    solution: 'Replace motor bearings',
    confidence: 96, resolvedBy: 'HVAC Team',
    timestamp: '2023-12-28', resolvedAt: '2024-01-02',
    equipment: 'Cooling Tower', system: 'HVAC'
  },
  {
    id: 'FLT006', fault: 'Network Switch Intermittent', severity: 'medium',
    symptoms: ['Random reboots', 'Packet loss', 'Error logs'],
    rootCause: 'Faulty power supply',
    solution: 'Replace power supply unit',
    confidence: 89, resolvedBy: 'IT Team',
    timestamp: '2023-12-20', resolvedAt: '2023-12-22',
    equipment: 'Core Switch', system: 'Network'
  },
  {
    id: 'FLT007', fault: 'Lighting Panel No Communication', severity: 'low',
    symptoms: ['No response', 'LED error', 'Timeout errors'],
    rootCause: 'Firmware corruption',
    solution: 'Update firmware, reset controller',
    confidence: 78, resolvedBy: 'Controls Team',
    timestamp: '2023-12-15', resolvedAt: '2023-12-18',
    equipment: 'Lighting Controller', system: 'Lighting'
  },
  {
    id: 'FLT008', fault: 'Chiller Low Efficiency', severity: 'medium',
    symptoms: ['Increased runtime', 'Higher energy use', 'Reduced cooling'],
    rootCause: 'Refrigerant undercharge',
    solution: 'Leak repair, recharge system',
    confidence: 87, resolvedBy: 'HVAC Team',
    timestamp: '2023-12-10', resolvedAt: '2023-12-15',
    equipment: 'Chiller-2', system: 'HVAC'
  }
])

// Similar fault search function
const performSearch = async () => {
  loading.value = true

  // If search query is empty, use default search or show message
  if (!searchQuery.value.trim()) {
    // Option 1: Show a default list of faults
    const defaultResults = faultDatabase.value.map(fault => ({
      ...fault,
      similarity: Math.floor(Math.random() * 60) + 20
    })).sort((a, b) => b.similarity - a.similarity).slice(0, 10)

    searchResults.value = defaultResults

    if (similarityChart) {
      similarityChart.setOption({
        xAxis: { data: defaultResults.map(r => r.fault.substring(0, 20) + (r.fault.length > 20 ? '...' : '')) },
        series: [{ data: defaultResults.map(r => r.similarity) }]
      })
    }

    loading.value = false
    ElMessage.info('Showing sample faults. Enter a description to search.')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1500))

  // Simulate similarity search
  const results = faultDatabase.value.map(fault => {
    let similarity = 0
    const query = searchQuery.value.toLowerCase()
    const faultText = fault.fault.toLowerCase()
    const symptomText = fault.symptoms.join(' ').toLowerCase()

    // Simple similarity calculation
    if (faultText.includes(query) || query.includes(faultText.split(' ')[0])) {
      similarity = Math.floor(Math.random() * 30) + 70
    } else if (symptomText.includes(query.split(' ')[0])) {
      similarity = Math.floor(Math.random() * 30) + 50
    } else {
      similarity = Math.floor(Math.random() * 40) + 20
    }

    return { ...fault, similarity }
  }).sort((a, b) => b.similarity - a.similarity).slice(0, 10)

  searchResults.value = results

  // Update chart
  if (similarityChart) {
    similarityChart.setOption({
      xAxis: { data: results.map(r => r.fault.substring(0, 20) + (r.fault.length > 20 ? '...' : '')) },
      series: [{ data: results.map(r => r.similarity) }]
    })
  }

  loading.value = false
  ElMessage.success(`Found ${results.length} similar faults`)
}

const clearSearch = () => {
  searchQuery.value = ''
  searchResults.value = []
  if (similarityChart) {
    similarityChart.setOption({
      xAxis: { data: [] },
      series: [{ data: [] }]
    })
  }
}

const viewDetails = (fault: any) => {
  selectedFault.value = fault
  detailsVisible.value = true
}

const initChart = () => {
  if (!chartRef.value) return

  similarityChart = echarts.init(chartRef.value)
  similarityChart.setOption({
    tooltip: { trigger: 'axis', formatter: '{b}<br/>Similarity: {c}%' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: [], axisLabel: { rotate: 30, interval: 0 } },
    yAxis: { type: 'value', name: 'Similarity (%)', min: 0, max: 100 },
    series: [{
      type: 'bar',
      data: [],
      itemStyle: {
        color: (params: any) => {
          const value = params.value
          if (value >= 80) return '#F56C6C'
          if (value >= 50) return '#E6A23C'
          return '#67C23A'
        },
        borderRadius: [4, 4, 0, 0]
      },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const handleResize = () => {
  similarityChart?.resize()
}

// Filtered results
const filteredResults = computed(() => {
  let filtered = searchResults.value
  if (selectedSeverity.value !== 'all') {
    filtered = filtered.filter(r => r.severity === selectedSeverity.value)
  }
  if (selectedSimilarity.value !== 'all') {
    if (selectedSimilarity.value === 'high') {
      filtered = filtered.filter(r => r.similarity >= 80)
    } else if (selectedSimilarity.value === 'medium') {
      filtered = filtered.filter(r => r.similarity >= 50 && r.similarity < 80)
    } else if (selectedSimilarity.value === 'low') {
      filtered = filtered.filter(r => r.similarity < 50)
    }
  }
  return filtered
})

const getSimilarityClass = (similarity: number) => {
  if (similarity >= 80) return 'similarity-high'
  if (similarity >= 50) return 'similarity-medium'
  return 'similarity-low'
}

const getSeverityIcon = (severity: string) => {
  switch (severity) {
    case 'critical': return '🔴'
    case 'high': return '🟠'
    case 'medium': return '🟡'
    case 'low': return '🟢'
    default: return '⚪'
  }
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const pagination = reactive({
  page: 1,
  pageSize: 6,
  total: 0
})

const selectedFault = ref<any>(null)

// Watch filtered results for pagination
watch(filteredResults, (newVal) => {
  pagination.total = newVal.length
  pagination.page = 1
})

const paginatedResults = computed(() => {
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filteredResults.value.slice(start, end)
})

// Load initial sample data on mount
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
        window.addEventListener('resize', handleResize)
        // Load sample data automatically after loading completes
        performSearch()
      }, 100)
    }, 400)
  }, 2500)
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
          <span class="loading-title">Loading Similar Fault Search</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Fault Diagnostics - Similar Fault Search</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="similar-fault-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Similar Fault Search</h1>
        <p class="page-subtitle">Find historical faults with similar symptoms and solutions</p>
      </div>
      <div class="header-right">
        <el-button size="large" @click="clearSearch">
          <el-icon><Delete /></el-icon>
          Clear
        </el-button>
        <el-button size="large">
          <el-icon><Setting /></el-icon>
          Settings
        </el-button>
      </div>
    </div>

    <!-- Search Section -->
    <div class="search-section">
      <div class="search-container">
        <el-input
            v-model="searchQuery"
            type="textarea"
            :rows="3"
            placeholder="Describe the fault you're experiencing... (e.g., 'Chiller temperature too high', 'AHU airflow low', 'Pump vibrating')"
            resize="none"
        />
        <div class="search-actions">
          <el-button type="primary" size="large" :loading="loading" @click="performSearch">
            <el-icon><Search /></el-icon>
            Find Similar Faults
          </el-button>
          <el-button size="large" @click="clearSearch">
            Clear
          </el-button>
        </div>
      </div>
    </div>

    <!-- Results Section -->
    <div v-if="searchResults.length > 0" class="results-section">
      <!-- Stats Summary -->
      <div class="results-stats">
        <div class="stat-item">
          <span class="stat-label">Total Matches:</span>
          <span class="stat-value">{{ searchResults.length }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Best Match:</span>
          <span class="stat-value">{{ searchResults[0]?.similarity }}% - {{ searchResults[0]?.fault }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Avg Similarity:</span>
          <span class="stat-value">{{ searchResults.length ? Math.round(searchResults.reduce((a,b) => a + b.similarity, 0) / searchResults.length) : 0 }}%</span>
        </div>
      </div>

      <!-- Similarity Chart -->
      <div class="chart-section">
        <div class="section-header">
          <h3>Similarity Scores</h3>
          <el-button text type="primary" @click="initChart">Refresh</el-button>
        </div>
        <div ref="chartRef" class="similarity-chart" style="height: 280px"></div>
      </div>

      <!-- Filters -->
      <div class="filters-bar">
        <div class="filters-left">
          <div class="severity-filters">
            <span class="filter-label">Severity:</span>
            <button
                v-for="s in severityOptions"
                :key="s.value"
                class="severity-chip"
                :class="{ active: selectedSeverity === s.value }"
                @click="selectedSeverity = s.value"
            >
              <span class="chip-dot" :style="{ background: s.color }"></span>
              <span>{{ s.label }}</span>
            </button>
          </div>
          <div class="similarity-filters">
            <span class="filter-label">Similarity:</span>
            <button
                v-for="sim in similarityOptions"
                :key="sim.value"
                class="similarity-chip"
                :class="{ active: selectedSimilarity === sim.value }"
                @click="selectedSimilarity = sim.value"
            >
              {{ sim.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- Results Grid -->
      <div class="results-grid">
        <div
            v-for="fault in paginatedResults"
            :key="fault.id"
            class="fault-card"
            @click="viewDetails(fault)"
        >
          <!-- Similarity Badge -->
          <div class="similarity-badge" :class="getSimilarityClass(fault.similarity)">
            {{ fault.similarity }}% Match
          </div>

          <!-- Card Header -->
          <div class="card-header">
            <div class="fault-title">
              <span class="severity-icon">{{ getSeverityIcon(fault.severity) }}</span>
              <h4>{{ fault.fault }}</h4>
            </div>
            <el-tag :type="fault.severity === 'critical' || fault.severity === 'high' ? 'danger' : fault.severity === 'medium' ? 'warning' : 'success'" size="small">
              {{ fault.severity.toUpperCase() }}
            </el-tag>
          </div>

          <!-- Card Body -->
          <div class="card-body">
            <div class="symptoms">
              <span class="label">Symptoms:</span>
              <div class="symptoms-list">
                <span v-for="symptom in fault.symptoms.slice(0, 2)" :key="symptom" class="symptom-tag">
                  {{ symptom }}
                </span>
                <span v-if="fault.symptoms.length > 2" class="more">+{{ fault.symptoms.length - 2 }}</span>
              </div>
            </div>
            <div class="root-cause">
              <span class="label">Root Cause:</span>
              <span class="value">{{ fault.rootCause }}</span>
            </div>
            <div class="solution">
              <span class="label">Solution:</span>
              <span class="value">{{ fault.solution }}</span>
            </div>
          </div>

          <!-- Card Footer -->
          <div class="card-footer">
            <div class="meta">
              <span><el-icon><Monitor /></el-icon> {{ fault.equipment }}</span>
              <span><el-icon><Clock /></el-icon> {{ fault.timestamp }}</span>
              <span><el-icon><User /></el-icon> {{ fault.resolvedBy }}</span>
            </div>
            <div class="confidence">
              Confidence: {{ fault.confidence }}%
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[6, 9, 12, 18]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="searchQuery && !loading && searchResults.length === 0" class="empty-state">
      <el-empty description="No similar faults found. Try different keywords.">
        <el-button type="primary" @click="performSearch">Try Again</el-button>
      </el-empty>
    </div>

    <!-- Initial State -->
    <div v-else class="initial-state">
      <el-empty description="Enter a fault description to find similar historical cases">
        <template #image>
          <el-icon :size="80" color="#c0c4cc"><Search /></el-icon>
        </template>
        <el-button type="primary" @click="performSearch">Start Searching</el-button>
      </el-empty>
      <div class="example-queries">
        <h4>Example queries:</h4>
        <div class="example-tags">
          <el-tag @click="searchQuery = 'Chiller temperature too high'; performSearch()">Chiller temperature too high</el-tag>
          <el-tag @click="searchQuery = 'Airflow low from AHU'; performSearch()">Airflow low from AHU</el-tag>
          <el-tag @click="searchQuery = 'Pump making noise and vibrating'; performSearch()">Pump making noise and vibrating</el-tag>
          <el-tag @click="searchQuery = 'Switchboard overheating'; performSearch()">Switchboard overheating</el-tag>
          <el-tag @click="searchQuery = 'Fan not running'; performSearch()">Fan not running</el-tag>
        </div>
      </div>
    </div>

    <!-- Fault Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="selectedFault?.fault" width="650px">
      <div class="dialog-content">
        <div class="similarity-highlight" :class="getSimilarityClass(selectedFault?.similarity)">
          {{ selectedFault?.similarity }}% Similarity Match
        </div>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="Fault ID">{{ selectedFault?.id }}</el-descriptions-item>
          <el-descriptions-item label="Equipment">{{ selectedFault?.equipment }}</el-descriptions-item>
          <el-descriptions-item label="System">{{ selectedFault?.system }}</el-descriptions-item>
          <el-descriptions-item label="Severity">
            <el-tag :type="selectedFault?.severity === 'critical' || selectedFault?.severity === 'high' ? 'danger' : selectedFault?.severity === 'medium' ? 'warning' : 'success'" size="small">
              {{ selectedFault?.severity?.toUpperCase() }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Symptoms" :span="2">
            <div class="symptoms-list">
              <el-tag v-for="s in selectedFault?.symptoms" :key="s" size="small" style="margin: 2px">
                {{ s }}
              </el-tag>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="Root Cause" :span="2">{{ selectedFault?.rootCause }}</el-descriptions-item>
          <el-descriptions-item label="Solution" :span="2">{{ selectedFault?.solution }}</el-descriptions-item>
          <el-descriptions-item label="Resolved By">{{ selectedFault?.resolvedBy }}</el-descriptions-item>
          <el-descriptions-item label="Confidence">{{ selectedFault?.confidence }}%</el-descriptions-item>
          <el-descriptions-item label="Occurred">{{ selectedFault?.timestamp }}</el-descriptions-item>
          <el-descriptions-item label="Resolved">{{ selectedFault?.resolvedAt }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
        <el-button type="primary" @click="performSearch">Search Similar</el-button>
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
.similar-fault-container {
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

/* Search Section */
.search-section {
  background: white;
  border-radius: 24px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.search-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.search-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* Results Section */
.results-section {
  margin-top: 24px;
}

.results-stats {
  display: flex;
  gap: 32px;
  padding: 16px 20px;
  background: white;
  border-radius: 16px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.stat-item {
  display: flex;
  gap: 8px;
  font-size: 14px;
}

.stat-label {
  color: #909399;
}

.stat-value {
  font-weight: 600;
  color: #409eff;
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

.similarity-chart {
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
  gap: 24px;
  flex-wrap: wrap;
}

.filter-label {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

.severity-filters,
.similarity-filters {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.severity-chip,
.similarity-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 20px;
  font-size: 12px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s ease;
}

.severity-chip:hover,
.similarity-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.severity-chip.active,
.similarity-chip.active {
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

/* Results Grid */
.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.fault-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.fault-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.similarity-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  color: white;
}

.similarity-badge.similarity-high {
  background: #f56c6c;
}

.similarity-badge.similarity-medium {
  background: #e6a23c;
}

.similarity-badge.similarity-low {
  background: #67c23a;
}

.card-header {
  padding: 16px 20px 8px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.fault-title {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.severity-icon {
  font-size: 16px;
}

.fault-title h4 {
  font-size: 15px;
  font-weight: 600;
  margin: 0;
  color: #1e293b;
}

.card-body {
  padding: 0 20px 12px 20px;
}

.symptoms,
.root-cause,
.solution {
  margin-bottom: 8px;
  font-size: 13px;
}

.label {
  color: #909399;
  font-weight: 500;
  display: inline-block;
  width: 75px;
}

.value {
  color: #1e293b;
}

.symptoms-list {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 6px;
}

.symptom-tag {
  background: #f5f7fa;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  color: #606266;
}

.more {
  font-size: 11px;
  color: #909399;
}

.card-footer {
  padding: 12px 20px;
  background: #fafbfc;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.meta {
  display: flex;
  gap: 12px;
  color: #909399;
}

.meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.confidence {
  color: #67c23a;
  font-weight: 500;
}

/* Pagination */
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
}

/* Empty State */
.empty-state,
.initial-state {
  padding: 60px 0;
  text-align: center;
}

.example-queries {
  margin-top: 32px;
}

.example-queries h4 {
  font-size: 14px;
  color: #909399;
  margin-bottom: 16px;
}

.example-tags {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

.example-tags .el-tag {
  cursor: pointer;
  transition: all 0.2s ease;
}

.example-tags .el-tag:hover {
  background: #409eff;
  color: white;
  border-color: #409eff;
}

/* Dialog Styles */
.dialog-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.similarity-highlight {
  text-align: center;
  padding: 12px;
  border-radius: 12px;
  font-size: 18px;
  font-weight: 600;
}

.similarity-highlight.similarity-high {
  background: #fef0f0;
  color: #f56c6c;
}

.similarity-highlight.similarity-medium {
  background: #fdf6ec;
  color: #e6a23c;
}

.similarity-highlight.similarity-low {
  background: #f0f9ff;
  color: #67c23a;
}

/* Responsive */
@media (max-width: 1200px) {
  .results-grid {
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  }
}

@media (max-width: 768px) {
  .similar-fault-container {
    padding: 16px;
  }

  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filters-left {
    flex-direction: column;
    align-items: stretch;
  }

  .severity-filters,
  .similarity-filters {
    flex-wrap: wrap;
  }

  .page-header {
    flex-direction: column;
    text-align: center;
  }

  .header-right {
    width: 100%;
    justify-content: center;
  }

  .results-stats {
    flex-direction: column;
    gap: 8px;
  }

  .results-grid {
    grid-template-columns: 1fr;
  }

  .search-actions {
    flex-direction: column;
  }

  .card-footer {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }

  .meta {
    flex-wrap: wrap;
  }

  .example-tags {
    flex-direction: column;
    align-items: center;
  }
}
</style>