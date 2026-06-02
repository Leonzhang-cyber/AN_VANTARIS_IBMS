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
        <div class="loading-tip">Power Quality Analysis</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="power-quality-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Power Quality</h2>
        <p class="header-subtitle">IEC 61000-4-30 Class A Compliance | Real-time Monitoring</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Overall Compliance Score -->
    <el-row :gutter="20" class="compliance-row">
      <el-col :span="24">
        <el-card shadow="hover" class="compliance-card">
          <div class="compliance-content">
            <div class="compliance-score">
              <el-progress
                  type="circle"
                  :percentage="complianceScore"
                  :color="complianceColor"
                  :width="120"
                  :stroke-width="12"
              >
                <template #default>
                  <div class="score-text">
                    <span class="score-value">{{ complianceScore }}</span>
                    <span class="score-unit">%</span>
                  </div>
                </template>
              </el-progress>
              <div class="score-label">Overall Power Quality Score</div>
              <div class="score-status">
                <el-tag :type="complianceScore >= 90 ? 'success' : (complianceScore >= 70 ? 'warning' : 'danger')" size="large">
                  {{ complianceScore >= 90 ? 'Excellent' : (complianceScore >= 70 ? 'Fair' : 'Poor') }}
                </el-tag>
              </div>
            </div>
            <div class="compliance-metrics">
              <div v-for="metric in complianceMetrics" :key="metric.name" class="metric-item">
                <div class="metric-header">
                  <span class="metric-name">{{ metric.name }}</span>
                  <el-tag :type="metric.status" size="small">{{ metric.statusText }}</el-tag>
                </div>
                <el-progress
                    :percentage="metric.value"
                    :color="metric.progressColor"
                    :stroke-width="8"
                />
                <div class="metric-detail">
                  <span>Current: {{ metric.current }}</span>
                  <span>Limit: {{ metric.limit }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Key Parameters Cards -->
    <el-row :gutter="20" class="params-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="param-card frequency">
          <div class="param-icon">
            <el-icon :size="32"><Timer /></el-icon>
          </div>
          <div class="param-info">
            <div class="param-label">Frequency</div>
            <div class="param-value">{{ parameters.frequency }} <span class="unit">Hz</span></div>
            <div class="param-status">
              <el-tag :type="getFrequencyStatus" size="small">{{ getFrequencyStatusText }}</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="param-card voltage">
          <div class="param-icon">
            <el-icon :size="32"><Histogram /></el-icon>
          </div>
          <div class="param-info">
            <div class="param-label">Voltage Unbalance</div>
            <div class="param-value">{{ parameters.voltageUnbalance }} <span class="unit">%</span></div>
            <div class="param-status">
              <el-tag :type="getUnbalanceStatus" size="small">{{ getUnbalanceStatusText }}</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="param-card harmonic">
          <div class="param-icon">
            <el-icon :size="32"><DataAnalysis /></el-icon>
          </div>
          <div class="param-info">
            <div class="param-label">THD (Voltage)</div>
            <div class="param-value">{{ parameters.thdVoltage }} <span class="unit">%</span></div>
            <div class="param-status">
              <el-tag :type="getThdStatus" size="small">{{ getThdStatusText }}</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="param-card flicker">
          <div class="param-icon">
            <el-icon :size="32"><View /></el-icon>
          </div>
          <div class="param-info">
            <div class="param-label">Flicker (Pst)</div>
            <div class="param-value">{{ parameters.flicker }} <span class="unit">p.u.</span></div>
            <div class="param-status">
              <el-tag :type="getFlickerStatus" size="small">{{ getFlickerStatusText }}</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Charts Row -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :md="14">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Harmonic Spectrum</span>
              <el-radio-group v-model="harmonicType" size="small" @change="updateHarmonicChart">
                <el-radio-button label="voltage">Voltage THD</el-radio-button>
                <el-radio-button label="current">Current THD</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="harmonicChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="10">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>THD Trend (Last 24h)</span>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Harmonics Details Table -->
    <el-card shadow="hover" class="harmonics-card">
      <template #header>
        <div class="card-header">
          <span>Harmonic Details (Odd Orders up to 25th)</span>
          <el-select v-model="harmonicPhase" size="small" style="width: 120px" @change="updateHarmonicTable">
            <el-option label="R Phase" value="R" />
            <el-option label="Y Phase" value="Y" />
            <el-option label="B Phase" value="B" />
          </el-select>
        </div>
      </template>
      <el-table :data="harmonicTableData" stripe border style="width: 100%">
        <el-table-column prop="order" label="Order" width="100" sortable />
        <el-table-column prop="value" label="Value (%)" sortable>
          <template #default="{ row }">
            <el-progress
                :percentage="row.value"
                :stroke-width="8"
                :color="row.value > row.limit ? '#F56C6C' : (row.value > row.limit * 0.7 ? '#E6A23C' : '#67C23A')"
                :show-text="false"
            />
            <span class="progress-value">{{ row.value }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="limit" label="IEC Limit (%)" width="120" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status" size="small">
              {{ row.statusText }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Interharmonics & Events -->
    <el-row :gutter="20">
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="interharmonics-card">
          <template #header>
            <div class="card-header">
              <span>Interharmonics (Non-Integer Orders)</span>
            </div>
          </template>
          <div ref="interharmonicChartRef" class="chart-container-small"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="events-card">
          <template #header>
            <div class="card-header">
              <span>Power Quality Events</span>
              <el-badge :value="pqEvents.length" type="danger" v-if="pqEvents.length > 0" />
            </div>
          </template>
          <el-table :data="pqEvents" stripe border size="small" max-height="280">
            <el-table-column prop="time" label="Time" width="140" />
            <el-table-column prop="type" label="Event Type" width="120">
              <template #default="{ row }">
                <el-tag :type="row.eventType" size="small">{{ row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="duration" label="Duration" width="100" />
            <el-table-column prop="magnitude" label="Magnitude" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- Sag/Swell & Transients -->
    <el-row :gutter="20" class="bottom-row">
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="sagswell-card">
          <template #header>
            <div class="card-header">
              <span>Voltage Sag/Swell Statistics (Last 30 Days)</span>
            </div>
          </template>
          <div ref="sagswellChartRef" class="chart-container-small"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="transients-card">
          <template #header>
            <div class="card-header">
              <span>Transient Events</span>
              <el-button text @click="refreshTransients">Refresh</el-button>
            </div>
          </template>
          <el-table :data="transients" stripe border size="small" max-height="280">
            <el-table-column prop="time" label="Time" width="150" />
            <el-table-column prop="peak" label="Peak (V)" sortable />
            <el-table-column prop="duration" label="Duration (µs)" />
            <el-table-column prop="affectedPhase" label="Phase" width="80" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Download,
  Refresh,
  Timer,
  Histogram,
  DataAnalysis,
  View
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Initializing power quality analyzer...',
  'Analyzing harmonics...',
  'Almost ready...'
]

// ==================== Data State ====================
const complianceScore = ref(92)
const complianceColor = ref('#67C23A')

const harmonicType = ref('voltage')
const harmonicPhase = ref('R')

// Compliance Metrics
const complianceMetrics = ref([
  { name: 'Frequency', value: 100, current: '50.0 Hz', limit: '±0.5 Hz', status: 'success', statusText: 'Excellent', progressColor: '#67C23A' },
  { name: 'Voltage Unbalance', value: 85, current: '0.8%', limit: '< 2%', status: 'success', statusText: 'Good', progressColor: '#67C23A' },
  { name: 'Total Harmonic Distortion', value: 78, current: '2.8%', limit: '< 5%', status: 'warning', statusText: 'Fair', progressColor: '#E6A23C' },
  { name: 'Flicker (Pst)', value: 92, current: '0.6', limit: '< 1.0', status: 'success', statusText: 'Excellent', progressColor: '#67C23A' },
  { name: 'Power Factor', value: 88, current: '0.92', limit: '> 0.85', status: 'success', statusText: 'Good', progressColor: '#67C23A' }
])

// Key Parameters
const parameters = ref({
  frequency: 50.02,
  voltageUnbalance: 0.8,
  thdVoltage: 2.8,
  flicker: 0.6
})

// Computed statuses
const getFrequencyStatus = computed(() => {
  const f = parameters.value.frequency
  if (f >= 49.5 && f <= 50.5) return 'success'
  if (f >= 49 && f <= 51) return 'warning'
  return 'danger'
})

const getFrequencyStatusText = computed(() => {
  const f = parameters.value.frequency
  if (f >= 49.5 && f <= 50.5) return 'Normal'
  if (f >= 49 && f <= 51) return 'Marginal'
  return 'Abnormal'
})

const getUnbalanceStatus = computed(() => {
  const u = parameters.value.voltageUnbalance
  if (u < 1) return 'success'
  if (u < 2) return 'warning'
  return 'danger'
})

const getUnbalanceStatusText = computed(() => {
  const u = parameters.value.voltageUnbalance
  if (u < 1) return 'Good'
  if (u < 2) return 'Fair'
  return 'Poor'
})

const getThdStatus = computed(() => {
  const thd = parameters.value.thdVoltage
  if (thd < 3) return 'success'
  if (thd < 5) return 'warning'
  return 'danger'
})

const getThdStatusText = computed(() => {
  const thd = parameters.value.thdVoltage
  if (thd < 3) return 'Good'
  if (thd < 5) return 'Marginal'
  return 'Excessive'
})

const getFlickerStatus = computed(() => {
  const f = parameters.value.flicker
  if (f < 0.7) return 'success'
  if (f < 1.0) return 'warning'
  return 'danger'
})

const getFlickerStatusText = computed(() => {
  const f = parameters.value.flicker
  if (f < 0.7) return 'Stable'
  if (f < 1.0) return 'Moderate'
  return 'Severe'
})

// Harmonic Table Data
interface HarmonicItem {
  order: string
  value: number
  limit: number
  status: string
  statusText: string
}

const harmonicTableData = ref<HarmonicItem[]>([])

// PQ Events
const pqEvents = ref([
  { time: '2024-01-15 08:23:15', type: 'Voltage Sag', duration: '120ms', magnitude: '-15%', eventType: 'warning' },
  { time: '2024-01-14 14:30:22', type: 'Voltage Swell', duration: '80ms', magnitude: '+12%', eventType: 'warning' },
  { time: '2024-01-13 22:15:03', type: 'Transient', duration: '50µs', magnitude: '850V', eventType: 'danger' },
  { time: '2024-01-12 09:45:30', type: 'Interruption', duration: '2.5s', magnitude: '0V', eventType: 'danger' }
])

// Transients
const transients = ref([
  { time: '2024-01-15 08:23:15', peak: 1250, duration: 45, affectedPhase: 'R' },
  { time: '2024-01-14 14:30:22', peak: 980, duration: 32, affectedPhase: 'Y' },
  { time: '2024-01-13 22:15:03', peak: 1500, duration: 68, affectedPhase: 'B' },
  { time: '2024-01-12 09:45:30', peak: 1100, duration: 28, affectedPhase: 'R' },
  { time: '2024-01-11 16:20:45', peak: 880, duration: 22, affectedPhase: 'Y' }
])

// Generate harmonic data
const generateHarmonicData = (phase: string) => {
  const harmonics = [3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25]
  const limits: Record<number, number> = {
    3: 5.0, 5: 6.0, 7: 5.0, 9: 3.0, 11: 3.5, 13: 3.0,
    15: 2.5, 17: 2.0, 19: 1.5, 21: 1.5, 23: 1.5, 25: 1.5
  }

  const baseValues: Record<number, number> = {
    3: 2.5, 5: 3.8, 7: 2.8, 9: 1.2, 11: 2.0, 13: 1.5,
    15: 1.0, 17: 0.8, 19: 0.6, 21: 0.5, 23: 0.4, 25: 0.3
  }

  return harmonics.map(order => {
    let value = baseValues[order] + (Math.random() - 0.5) * 0.5
    if (phase === 'Y') value += (Math.random() - 0.5) * 0.3
    if (phase === 'B') value += (Math.random() - 0.5) * 0.4
    value = Math.max(0.1, parseFloat(value.toFixed(1)))

    let status = 'success'
    let statusText = 'Good'
    if (value > limits[order] * 0.7) {
      status = 'warning'
      statusText = 'Marginal'
    }
    if (value > limits[order]) {
      status = 'danger'
      statusText = 'Exceed'
    }

    return {
      order: `${order}th`,
      value: value,
      limit: limits[order],
      status: status,
      statusText: statusText
    }
  })
}

const updateHarmonicTable = () => {
  harmonicTableData.value = generateHarmonicData(harmonicPhase.value)
}

// ==================== Chart Functions ====================
const harmonicChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()
const interharmonicChartRef = ref<HTMLElement>()
const sagswellChartRef = ref<HTMLElement>()

let harmonicChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null
let interharmonicChart: echarts.ECharts | null = null
let sagswellChart: echarts.ECharts | null = null

const initCharts = () => {
  nextTick(() => {
    if (harmonicChartRef.value) {
      if (harmonicChart) harmonicChart.dispose()
      harmonicChart = echarts.init(harmonicChartRef.value)
      updateHarmonicChart()
    }

    if (trendChartRef.value) {
      if (trendChart) trendChart.dispose()
      trendChart = echarts.init(trendChartRef.value)
      updateTrendChart()
    }

    if (interharmonicChartRef.value) {
      if (interharmonicChart) interharmonicChart.dispose()
      interharmonicChart = echarts.init(interharmonicChartRef.value)
      updateInterharmonicChart()
    }

    if (sagswellChartRef.value) {
      if (sagswellChart) sagswellChart.dispose()
      sagswellChart = echarts.init(sagswellChartRef.value)
      updateSagSwellChart()
    }
  })
}

const updateHarmonicChart = () => {
  const orders = [3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25]
  let data: number[]

  if (harmonicType.value === 'voltage') {
    data = [2.8, 3.5, 2.5, 1.2, 1.8, 1.3, 0.9, 0.7, 0.5, 0.4, 0.3, 0.2]
  } else {
    data = [5.2, 6.8, 4.5, 2.2, 3.5, 2.8, 1.8, 1.2, 0.9, 0.7, 0.5, 0.4]
  }

  harmonicChart?.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'category', data: orders.map(o => `${o}th`), name: 'Harmonic Order' },
    yAxis: { type: 'value', name: 'Amplitude (%)' },
    series: [{
      type: 'bar',
      data: data,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value > 5) return '#F56C6C'
          if (value > 3) return '#E6A23C'
          return '#409EFF'
        }
      },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const updateTrendChart = () => {
  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const thdData = Array.from({ length: 24 }, () => parseFloat((2 + Math.random() * 3).toFixed(1)))

  trendChart?.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: hours, name: 'Time' },
    yAxis: { type: 'value', name: 'THD (%)' },
    series: [{
      type: 'line',
      data: thdData,
      smooth: true,
      lineStyle: { color: '#409EFF', width: 2 },
      areaStyle: { opacity: 0.1, color: '#409EFF' },
      markLine: {
        data: [{ yAxis: 5, name: 'IEC Limit', lineStyle: { color: '#F56C6C', type: 'dashed' } }]
      }
    }]
  })
}

const updateInterharmonicChart = () => {
  const frequencies = Array.from({ length: 20 }, (_, i) => `${Math.round(50 + (i + 1) * 2.5)}Hz`)
  const amplitudes = Array.from({ length: 20 }, () => parseFloat((0.1 + Math.random() * 0.8).toFixed(2)))

  interharmonicChart?.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: frequencies, name: 'Frequency', axisLabel: { rotate: 45, interval: 3 } },
    yAxis: { type: 'value', name: 'Amplitude (V)' },
    series: [{
      type: 'bar',
      data: amplitudes,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#67C23A' }
    }]
  })
}

const updateSagSwellChart = () => {
  const days = Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`)
  const sagData = Array.from({ length: 30 }, () => Math.floor(Math.random() * 8))
  const swellData = Array.from({ length: 30 }, () => Math.floor(Math.random() * 5))

  sagswellChart?.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Voltage Sags', 'Voltage Swells'] },
    xAxis: { type: 'category', data: days, axisLabel: { rotate: 45, interval: 5 } },
    yAxis: { type: 'value', name: 'Event Count' },
    series: [
      { name: 'Voltage Sags', type: 'bar', data: sagData, itemStyle: { color: '#E6A23C', borderRadius: [4, 4, 0, 0] } },
      { name: 'Voltage Swells', type: 'bar', data: swellData, itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] } }
    ]
  })
}

// ==================== Actions ====================
const refreshData = () => {
  complianceScore.value = Math.floor(70 + Math.random() * 28)
  parameters.value = {
    frequency: parseFloat((49.8 + Math.random() * 0.6).toFixed(2)),
    voltageUnbalance: parseFloat((0.5 + Math.random() * 2).toFixed(1)),
    thdVoltage: parseFloat((2 + Math.random() * 4).toFixed(1)),
    flicker: parseFloat((0.4 + Math.random() * 0.8).toFixed(1))
  }
  updateHarmonicTable()
  updateHarmonicChart()
  updateTrendChart()
  updateInterharmonicChart()
  updateSagSwellChart()
  ElMessage.success('Data refreshed')
}

const refreshTransients = () => {
  transients.value = [
    { time: new Date().toLocaleString(), peak: Math.floor(800 + Math.random() * 800), duration: Math.floor(20 + Math.random() * 60), affectedPhase: ['R', 'Y', 'B'][Math.floor(Math.random() * 3)] },
    ...transients.value.slice(0, 4)
  ]
  ElMessage.success('Transient data refreshed')
}

const handleExport = () => {
  ElMessage.success('Report export started')
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
      updateHarmonicTable()
      initCharts()
    }, 400)
  }, 2000)
})

watch([harmonicChartRef, trendChartRef, interharmonicChartRef, sagswellChartRef], () => {
  window.addEventListener('resize', () => {
    harmonicChart?.resize()
    trendChart?.resize()
    interharmonicChart?.resize()
    sagswellChart?.resize()
  })
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

.loading-tip { font-size: 13px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 8px; font-weight: 500; }
.loading-subtip { font-size: 11px; color: #64748b; letter-spacing: 0.5px; animation: pulse 2s ease-in-out infinite; }

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Main Container */
.power-quality-container {
  padding: 20px;
  background: #f0f2f5;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  background: white;
  padding: 20px 24px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.page-header h2 {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 600;
  color: #1f2f3d;
}

.header-subtitle {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Compliance Card */
.compliance-row {
  margin-bottom: 20px;
}

.compliance-card {
  border-radius: 16px;
}

.compliance-content {
  display: flex;
  gap: 40px;
  padding: 10px;
}

.compliance-score {
  text-align: center;
  min-width: 180px;
}

.score-text {
  text-align: center;
}

.score-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
}

.score-unit {
  font-size: 14px;
  color: #909399;
}

.score-label {
  font-size: 13px;
  color: #909399;
  margin-top: 8px;
}

.score-status {
  margin-top: 12px;
}

.compliance-metrics {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.metric-item {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 12px;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.metric-name {
  font-size: 14px;
  font-weight: 500;
  color: #1f2f3d;
}

.metric-detail {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

/* Parameter Cards */
.params-row {
  margin-bottom: 20px;
}

.param-card {
  border-radius: 16px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
}

.param-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.param-card.frequency .param-icon { color: #409EFF; background: rgba(64, 158, 255, 0.1); }
.param-card.voltage .param-icon { color: #E6A23C; background: rgba(230, 162, 60, 0.1); }
.param-card.harmonic .param-icon { color: #F56C6C; background: rgba(245, 108, 108, 0.1); }
.param-card.flicker .param-icon { color: #67C23A; background: rgba(103, 194, 58, 0.1); }

.param-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.param-info {
  flex: 1;
}

.param-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.param-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
}

.param-value .unit {
  font-size: 12px;
  font-weight: normal;
  color: #909399;
}

.param-status {
  margin-top: 6px;
}

/* Charts */
.charts-row {
  margin-bottom: 20px;
}

.chart-card, .harmonics-card, .interharmonics-card, .events-card, .sagswell-card, .transients-card {
  border-radius: 16px;
  margin-bottom: 20px;
}

.chart-container {
  width: 100%;
  height: 350px;
}

.chart-container-small {
  width: 100%;
  height: 280px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-value {
  margin-left: 8px;
  font-size: 12px;
  color: #606266;
}

.bottom-row {
  margin-bottom: 0;
}
</style>