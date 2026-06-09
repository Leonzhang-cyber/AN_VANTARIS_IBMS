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
        <div class="loading-tip">Clean Telemetry Data</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="clean-telemetry-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Data Platform</el-breadcrumb-item>
            <el-breadcrumb-item>Historian</el-breadcrumb-item>
            <el-breadcrumb-item>Clean Telemetry</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Clean Telemetry Data</h1>
        <p class="description">Validated, standardized, and quality-assured telemetry data ready for analytics</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Data
        </el-button>
        <el-button @click="handleQualityReport">
          <el-icon><DataAnalysis /></el-icon>
          Quality Report
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6" v-for="stat in statsCards" :key="stat.title">
        <el-card class="stat-card" shadow="hover" @click="handleCardClick(stat)">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">{{ stat.title }}</div>
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
                <el-icon><component :is="stat.trend > 0 ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
                {{ Math.abs(stat.trend) }}%
                <span class="trend-label">vs last week</span>
              </div>
            </div>
            <div class="stat-icon" :style="{ background: stat.bgColor }">
              <el-icon :size="28" color="white">
                <component :is="stat.icon" />
              </el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Quality Overview Charts -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="14">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Cleaned Telemetry Trends</span>
              <div class="chart-controls">
                <el-select v-model="selectedMetric" size="small" style="width: 150px">
                  <el-option label="Temperature (°C)" value="temperature" />
                  <el-option label="Humidity (%)" value="humidity" />
                  <el-option label="Pressure (kPa)" value="pressure" />
                  <el-option label="Power (kW)" value="power" />
                </el-select>
                <el-select v-model="selectedDevice" size="small" style="width: 160px">
                  <el-option label="All Devices" value="all" />
                  <el-option label="Chiller-01" value="chiller_01" />
                  <el-option label="AHU-03" value="ahu_03" />
                  <el-option label="Cooling Tower-02" value="ct_02" />
                </el-select>
              </div>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="10">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Data Quality Metrics</span>
            </div>
          </template>
          <div ref="qualityChartRef" class="gauge-container"></div>
          <div class="quality-stats">
            <div class="quality-item">
              <span class="quality-label">Completeness</span>
              <el-progress :percentage="99.8" :stroke-width="8" color="#67c23a" />
            </div>
            <div class="quality-item">
              <span class="quality-label">Accuracy</span>
              <el-progress :percentage="98.5" :stroke-width="8" color="#409eff" />
            </div>
            <div class="quality-item">
              <span class="quality-label">Timeliness</span>
              <el-progress :percentage="97.2" :stroke-width="8" color="#e6a23c" />
            </div>
            <div class="quality-item">
              <span class="quality-label">Consistency</span>
              <el-progress :percentage="99.1" :stroke-width="8" color="#67c23a" />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Filters -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-container">
        <div class="filter-row">
          <el-input
              v-model="filters.deviceId"
              placeholder="Device ID"
              clearable
              style="width: 180px"
              @clear="handleSearch"
          />
          <el-select v-model="filters.metricType" placeholder="Metric Type" clearable style="width: 140px">
            <el-option label="Temperature" value="temperature" />
            <el-option label="Humidity" value="humidity" />
            <el-option label="Pressure" value="pressure" />
            <el-option label="Power" value="power" />
            <el-option label="Flow Rate" value="flow_rate" />
          </el-select>
          <el-select v-model="filters.validationStatus" placeholder="Validation Status" clearable style="width: 150px">
            <el-option label="Validated" value="validated" />
            <el-option label="Corrected" value="corrected" />
            <el-option label="Imputed" value="imputed" />
          </el-select>
          <el-date-picker
              v-model="filters.timeRange"
              type="datetimerange"
              range-separator="to"
              start-placeholder="Start Time"
              end-placeholder="End Time"
              style="width: 360px"
          />
          <el-button type="primary" @click="handleSearch">Query</el-button>
          <el-button @click="handleResetFilters">Reset</el-button>
        </div>
      </div>
    </el-card>

    <!-- Data Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Clean Telemetry Records ({{ filteredData.length }} records)</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchData" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedData" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="timestamp" label="Timestamp"  />
        <el-table-column prop="deviceId" label="Device ID"  show-overflow-tooltip />
        <el-table-column prop="deviceName" label="Device Name"  show-overflow-tooltip />
        <el-table-column prop="metric" label="Metric" >
          <template #default="{ row }">
            <el-tag :type="getMetricTag(row.metric)" size="small">{{ formatMetricName(row.metric) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="value" label="Value"  align="right">
          <template #default="{ row }">
            <span class="value-normal">{{ row.value }} {{ row.unit }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="originalValue" label="Original Value" width="120" align="right">
          <template #default="{ row }">
            <span v-if="row.originalValue !== row.value" class="value-corrected">
              {{ row.originalValue }} {{ row.unit }}
            </span>
            <span v-else class="value-original">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="validationStatus" label="Status" >
          <template #default="{ row }">
            <el-tag :type="getValidationTag(row.validationStatus)" size="small">{{ row.validationStatus }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="confidence" label="Confidence" >
          <template #default="{ row }">
            <el-progress :percentage="row.confidence" :stroke-width="6" :color="getConfidenceColor(row.confidence)" />
          </template>
        </el-table-column>
        <el-table-column prop="source" label="Source"  />
        <el-table-column label="Actions"  fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">Details</el-button>
            <el-button link type="info" size="small" @click="viewLineage(row)">Lineage</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[20, 50, 100, 200]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredData.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Data Details Dialog -->
    <el-dialog v-model="detailsDialogVisible" :title="`Clean Telemetry Details - ${currentRecord?.deviceId}`" width="700px" destroy-on-close>
      <div class="telemetry-details" v-if="currentRecord">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Timestamp">{{ currentRecord.timestamp }}</el-descriptions-item>
          <el-descriptions-item label="Device ID">{{ currentRecord.deviceId }}</el-descriptions-item>
          <el-descriptions-item label="Device Name">{{ currentRecord.deviceName }}</el-descriptions-item>
          <el-descriptions-item label="Metric">{{ formatMetricName(currentRecord.metric) }}</el-descriptions-item>
          <el-descriptions-item label="Cleaned Value">{{ currentRecord.value }} {{ currentRecord.unit }}</el-descriptions-item>
          <el-descriptions-item label="Original Value">{{ currentRecord.originalValue || 'N/A' }} {{ currentRecord.unit }}</el-descriptions-item>
          <el-descriptions-item label="Validation Status">
            <el-tag :type="getValidationTag(currentRecord.validationStatus)" size="small">{{ currentRecord.validationStatus }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Confidence">{{ currentRecord.confidence }}%</el-descriptions-item>
          <el-descriptions-item label="Cleaning Method" :span="2">{{ currentRecord.cleaningMethod }}</el-descriptions-item>
          <el-descriptions-item label="Validation Rules" :span="2">{{ currentRecord.validationRules }}</el-descriptions-item>
          <el-descriptions-item label="Quality Score" :span="2">
            <el-progress :percentage="currentRecord.qualityScore" :color="getQualityScoreColor(currentRecord.qualityScore)" />
          </el-descriptions-item>
        </el-descriptions>

        <!-- Data Lineage -->
        <div class="data-lineage" v-if="currentRecord.lineage">
          <h4>Data Lineage</h4>
          <div class="lineage-steps">
            <div class="lineage-step">
              <div class="step-icon raw">📡</div>
              <div class="step-label">Raw Data</div>
              <div class="step-time">{{ currentRecord.lineage.rawTimestamp }}</div>
            </div>
            <div class="lineage-arrow">→</div>
            <div class="lineage-step">
              <div class="step-icon validate">✓</div>
              <div class="step-label">Validation</div>
              <div class="step-time">{{ currentRecord.lineage.validationTime }}</div>
            </div>
            <div class="lineage-arrow">→</div>
            <div class="lineage-step" v-if="currentRecord.lineage.correctionApplied">
              <div class="step-icon correct">✎</div>
              <div class="step-label">Correction</div>
              <div class="step-time">{{ currentRecord.lineage.correctionTime }}</div>
            </div>
            <div class="lineage-arrow" v-if="currentRecord.lineage.correctionApplied">→</div>
            <div class="lineage-step">
              <div class="step-icon clean">✨</div>
              <div class="step-label">Cleaned</div>
              <div class="step-time">{{ currentRecord.timestamp }}</div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailsDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="exportRecord">Export</el-button>
      </template>
    </el-dialog>

    <!-- Lineage Dialog -->
    <el-dialog v-model="lineageDialogVisible" title="Data Lineage - Full Trace" width="800px" destroy-on-close>
      <div class="full-lineage">
        <div ref="lineageChartRef" class="lineage-chart-container"></div>
        <div class="lineage-summary">
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="Raw Data Timestamp">{{ lineageInfo.rawTimestamp }}</el-descriptions-item>
            <el-descriptions-item label="Validation Time">{{ lineageInfo.validationTime }}</el-descriptions-item>
            <el-descriptions-item label="Cleaning Duration">{{ lineageInfo.cleaningDuration }}</el-descriptions-item>
            <el-descriptions-item label="Quality Improvement">{{ lineageInfo.qualityImprovement }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      <template #footer>
        <el-button @click="lineageDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="exportLineage">Export Lineage</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  DataAnalysis
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading clean telemetry data...',
  'Validating quality metrics...',
  'Almost ready...'
]

// ==================== Chart References ====================
const trendChartRef = ref<HTMLElement>()
const qualityChartRef = ref<HTMLElement>()
const lineageChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null
let qualityChart: echarts.ECharts | null = null
let lineageChart: echarts.ECharts | null = null

// ==================== State ====================
const tableLoading = ref(false)
const detailsDialogVisible = ref(false)
const lineageDialogVisible = ref(false)
const currentRecord = ref<any>(null)
const currentPage = ref(1)
const pageSize = ref(20)
const selectedMetric = ref('temperature')
const selectedDevice = ref('all')

const filters = reactive({
  deviceId: '',
  metricType: '',
  validationStatus: '',
  timeRange: null as [Date, Date] | null
})

const lineageInfo = reactive({
  rawTimestamp: '--',
  validationTime: '--',
  cleaningDuration: '--',
  qualityImprovement: '--'
})

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'Total Clean Records', value: '2.38M', trend: 12, icon: 'Document', bgColor: '#409eff', key: 'total' },
  { title: 'Data Quality Score', value: '98.5%', trend: 2.5, icon: 'Checked', bgColor: '#67c23a', key: 'quality' },
  { title: 'Corrections Applied', value: '124,567', trend: -8, icon: 'Edit', bgColor: '#e6a23c', key: 'corrections' },
  { title: 'Avg Processing Time', value: '45ms', trend: -12, icon: 'Clock', bgColor: '#f56c6c', key: 'time' }
])

const cleanTelemetryData = ref([
  {
    id: 1,
    timestamp: '2024-01-20 08:00:00.123',
    deviceId: 'CH-01',
    deviceName: 'Chiller-01',
    metric: 'temperature',
    value: 22.5,
    unit: '°C',
    originalValue: null,
    validationStatus: 'validated',
    confidence: 99.5,
    source: 'BMS',
    cleaningMethod: 'Validation only',
    validationRules: 'Temperature range: 10-30°C',
    qualityScore: 99,
    lineage: {
      rawTimestamp: '2024-01-20 08:00:00.123',
      validationTime: '2024-01-20 08:00:00.245',
      correctionApplied: false
    }
  },
  {
    id: 2,
    timestamp: '2024-01-20 08:00:01.456',
    deviceId: 'CH-01',
    deviceName: 'Chiller-01',
    metric: 'pressure',
    value: 101.3,
    unit: 'kPa',
    originalValue: 101.3,
    validationStatus: 'validated',
    confidence: 98.2,
    source: 'BMS',
    cleaningMethod: 'Validation only',
    validationRules: 'Pressure range: 80-120 kPa',
    qualityScore: 98,
    lineage: {
      rawTimestamp: '2024-01-20 08:00:01.456',
      validationTime: '2024-01-20 08:00:01.578',
      correctionApplied: false
    }
  },
  {
    id: 3,
    timestamp: '2024-01-20 08:00:02.789',
    deviceId: 'AHU-03',
    deviceName: 'Air Handler-03',
    metric: 'temperature',
    value: 18.5,
    unit: '°C',
    originalValue: 18.5,
    validationStatus: 'validated',
    confidence: 99.1,
    source: 'SCADA',
    cleaningMethod: 'Validation only',
    validationRules: 'Temperature range: 10-30°C',
    qualityScore: 99,
    lineage: {
      rawTimestamp: '2024-01-20 08:00:02.789',
      validationTime: '2024-01-20 08:00:02.901',
      correctionApplied: false
    }
  },
  {
    id: 4,
    timestamp: '2024-01-20 08:00:03.012',
    deviceId: 'CT-02',
    deviceName: 'Cooling Tower-02',
    metric: 'temperature',
    value: 24.2,
    unit: '°C',
    originalValue: 245.6,
    validationStatus: 'corrected',
    confidence: 85.3,
    source: 'IoT',
    cleaningMethod: 'Outlier correction (IQR)',
    validationRules: 'Temperature range: 10-40°C',
    qualityScore: 85,
    lineage: {
      rawTimestamp: '2024-01-20 08:00:03.012',
      validationTime: '2024-01-20 08:00:03.134',
      correctionApplied: true,
      correctionTime: '2024-01-20 08:00:03.256'
    }
  },
  {
    id: 5,
    timestamp: '2024-01-20 08:00:04.345',
    deviceId: 'SEN-A1',
    deviceName: 'Sensor Array A1',
    metric: 'humidity',
    value: 52.3,
    unit: '%',
    originalValue: null,
    validationStatus: 'imputed',
    confidence: 76.8,
    source: 'IoT',
    cleaningMethod: 'Median imputation',
    validationRules: 'Humidity range: 20-80%',
    qualityScore: 77,
    lineage: {
      rawTimestamp: '2024-01-20 08:00:04.345',
      validationTime: '2024-01-20 08:00:04.467',
      correctionApplied: true,
      correctionTime: '2024-01-20 08:00:04.589'
    }
  }
])

// Generate more mock data
for (let i = 6; i <= 100; i++) {
  const devices = [
    { id: 'CH-01', name: 'Chiller-01' },
    { id: 'AHU-03', name: 'Air Handler-03' },
    { id: 'CT-02', name: 'Cooling Tower-02' },
    { id: 'SEN-A1', name: 'Sensor Array A1' },
    { id: 'PMP-04', name: 'Pump-04' }
  ]
  const metrics = ['temperature', 'humidity', 'pressure', 'power', 'flow_rate']
  const statuses = ['validated', 'validated', 'validated', 'corrected', 'imputed']
  const device = devices[Math.floor(Math.random() * devices.length)]
  const metric = metrics[Math.floor(Math.random() * metrics.length)]
  const status = statuses[Math.floor(Math.random() * statuses.length)]
  const isCorrected = status === 'corrected'
  const isImputed = status === 'imputed'

  let value, originalValue
  if (metric === 'temperature') {
    value = (Math.random() * 20 + 10).toFixed(1)
    originalValue = isCorrected ? (Math.random() * 50 + 50).toFixed(1) : value
  } else if (metric === 'humidity') {
    value = (Math.random() * 50 + 20).toFixed(1)
    originalValue = isCorrected ? (Math.random() * 100).toFixed(1) : value
  } else if (metric === 'pressure') {
    value = (Math.random() * 40 + 80).toFixed(1)
    originalValue = isCorrected ? (Math.random() * 100 + 50).toFixed(1) : value
  } else if (metric === 'power') {
    value = (Math.random() * 80 + 20).toFixed(1)
    originalValue = isCorrected ? (Math.random() * 200).toFixed(1) : value
  } else {
    value = (Math.random() * 100 + 10).toFixed(1)
    originalValue = isCorrected ? (Math.random() * 500).toFixed(1) : value
  }

  cleanTelemetryData.value.push({
    id: i,
    timestamp: `2024-01-20 08:00:${Math.floor(Math.random() * 60)}.${Math.floor(Math.random() * 1000)}`,
    deviceId: device.id,
    deviceName: device.name,
    metric: metric,
    value: parseFloat(value),
    unit: metric === 'temperature' ? '°C' : metric === 'humidity' ? '%' : metric === 'pressure' ? 'kPa' : metric === 'power' ? 'kW' : 'm³/h',
    originalValue: isCorrected || isImputed ? parseFloat(originalValue) : null,
    validationStatus: status,
    confidence: Math.floor(Math.random() * 30) + 70,
    source: Math.random() > 0.5 ? 'BMS' : 'IoT',
    cleaningMethod: status === 'validated' ? 'Validation only' : (status === 'corrected' ? 'Outlier correction' : 'Statistical imputation'),
    validationRules: `${metric.charAt(0).toUpperCase() + metric.slice(1)} range validation`,
    qualityScore: Math.floor(Math.random() * 30) + 70,
    lineage: {
      rawTimestamp: `2024-01-20 08:00:${Math.floor(Math.random() * 60)}.${Math.floor(Math.random() * 1000)}`,
      validationTime: `2024-01-20 08:00:${Math.floor(Math.random() * 60)}.${Math.floor(Math.random() * 1000)}`,
      correctionApplied: isCorrected || isImputed,
      correctionTime: isCorrected || isImputed ? `2024-01-20 08:00:${Math.floor(Math.random() * 60)}.${Math.floor(Math.random() * 1000)}` : undefined
    }
  })
}

cleanTelemetryData.value.sort((a, b) => a.timestamp.localeCompare(b.timestamp))

// ==================== Computed ====================
const filteredData = computed(() => {
  let filtered = [...cleanTelemetryData.value]

  if (filters.deviceId) {
    filtered = filtered.filter(d => d.deviceId.toLowerCase().includes(filters.deviceId.toLowerCase()))
  }

  if (filters.metricType) {
    filtered = filtered.filter(d => d.metric === filters.metricType)
  }

  if (filters.validationStatus) {
    filtered = filtered.filter(d => d.validationStatus === filters.validationStatus)
  }

  if (filters.timeRange && filters.timeRange[0] && filters.timeRange[1]) {
    filtered = filtered.filter(d => {
      const date = new Date(d.timestamp)
      return date >= filters.timeRange![0] && date <= filters.timeRange![1]
    })
  }

  return filtered
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})

// ==================== Helper Methods ====================
const formatMetricName = (metric: string) => {
  const map: Record<string, string> = {
    'temperature': 'Temperature',
    'humidity': 'Humidity',
    'pressure': 'Pressure',
    'power': 'Power',
    'flow_rate': 'Flow Rate'
  }
  return map[metric] || metric
}

const getMetricTag = (metric: string) => {
  const map: Record<string, string> = {
    'temperature': 'danger',
    'humidity': 'primary',
    'pressure': 'success',
    'power': 'warning',
    'flow_rate': 'info'
  }
  return map[metric] || 'info'
}

const getValidationTag = (status: string) => {
  const map: Record<string, string> = {
    'validated': 'success',
    'corrected': 'warning',
    'imputed': 'info'
  }
  return map[status] || 'info'
}

const getConfidenceColor = (confidence: number) => {
  if (confidence >= 90) return '#67c23a'
  if (confidence >= 70) return '#e6a23c'
  return '#f56c6c'
}

const getQualityScoreColor = (score: number) => {
  if (score >= 90) return '#67c23a'
  if (score >= 70) return '#e6a23c'
  return '#f56c6c'
}

// ==================== Chart Initializations ====================
const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)

  // Generate mock trend data
  const times = Array.from({ length: 50 }, (_, i) => new Date(Date.now() - (50 - i) * 60000))
  const values = times.map(() => {
    if (selectedMetric.value === 'temperature') return Math.random() * 15 + 15
    if (selectedMetric.value === 'humidity') return Math.random() * 40 + 30
    if (selectedMetric.value === 'pressure') return Math.random() * 30 + 85
    return Math.random() * 50 + 30
  })

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'time', name: 'Time' },
    yAxis: { type: 'value', name: 'Value' },
    series: [{
      type: 'line',
      data: times.map((t, i) => [t.getTime(), values[i]]),
      smooth: true,
      lineStyle: { width: 2, color: '#409eff' },
      areaStyle: { opacity: 0.1 },
      symbolSize: 6
    }]
  }

  trendChart.setOption(option)
  window.addEventListener('resize', () => trendChart?.resize())
}

const initQualityGauge = () => {
  if (!qualityChartRef.value) return
  if (qualityChart) qualityChart.dispose()

  qualityChart = echarts.init(qualityChartRef.value)

  const option: echarts.EChartsOption = {
    series: [{
      type: 'gauge',
      center: ['50%', '50%'],
      radius: '70%',
      startAngle: 180,
      endAngle: 0,
      min: 0,
      max: 100,
      splitNumber: 5,
      progress: { show: true, width: 18, itemStyle: { color: '#67c23a' } },
      axisLine: { lineStyle: { width: 18, color: [[0.985, '#67c23a'], [1, '#e6e9f0']] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      pointer: { show: false },
      detail: { show: true, offsetCenter: [0, 20], valueAnimation: true, fontSize: 24, fontWeight: 'bold', color: '#303133' },
      title: { show: true, offsetCenter: [0, -20], fontSize: 14, color: '#909399' },
      data: [{ value: 98.5, name: 'Quality Score' }]
    }]
  }

  qualityChart.setOption(option)
  window.addEventListener('resize', () => qualityChart?.resize())
}

const initLineageChart = () => {
  if (!lineageChartRef.value) return
  if (lineageChart) lineageChart.dispose()

  lineageChart = echarts.init(lineageChartRef.value)

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'sankey',
      layout: 'none',
      data: [
        { name: 'Raw Telemetry' },
        { name: 'Validation' },
        { name: 'Outlier Detection' },
        { name: 'Data Correction' },
        { name: 'Clean Telemetry' }
      ],
      links: [
        { source: 'Raw Telemetry', target: 'Validation', value: 1 },
        { source: 'Validation', target: 'Outlier Detection', value: 1 },
        { source: 'Outlier Detection', target: 'Data Correction', value: 0.15 },
        { source: 'Validation', target: 'Clean Telemetry', value: 0.85 },
        { source: 'Data Correction', target: 'Clean Telemetry', value: 0.15 }
      ],
      lineStyle: { color: 'gradient', curveness: 0.5 }
    }]
  }

  lineageChart.setOption(option)
  window.addEventListener('resize', () => lineageChart?.resize())
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleSearch = () => {
  currentPage.value = 1
  initTrendChart()
}

const handleResetFilters = () => {
  filters.deviceId = ''
  filters.metricType = ''
  filters.validationStatus = ''
  filters.timeRange = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
  initTrendChart()
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredData.value.length} clean telemetry records...`)
}

const handleQualityReport = () => {
  ElMessage.info('Generating quality report...')
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const fetchData = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Data refreshed')
  }, 500)
}

const viewDetails = (record: any) => {
  currentRecord.value = record
  detailsDialogVisible.value = true
}

const viewLineage = (record: any) => {
  currentRecord.value = record
  lineageInfo.rawTimestamp = record.lineage?.rawTimestamp || '--'
  lineageInfo.validationTime = record.lineage?.validationTime || '--'
  lineageInfo.cleaningDuration = '~150ms'
  lineageInfo.qualityImprovement = '+12.5%'
  lineageDialogVisible.value = true
  nextTick(() => {
    initLineageChart()
  })
}

const exportRecord = () => {
  ElMessage.success('Record exported')
}

const exportLineage = () => {
  ElMessage.success('Lineage exported')
}

const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {}

// ==================== Loading Simulation ====================
const initCharts = async () => {
  await nextTick()
  setTimeout(() => {
    initTrendChart()
    initQualityGauge()
  }, 100)
}

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
      initCharts()
      fetchData()
    }, 400)
  }, 2000)
})
</script>

<style scoped lang="scss">
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

/* ==================== Main Page Styles ==================== */
.clean-telemetry-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;

  .breadcrumb {
    margin-bottom: 8px;
  }

  h1 {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 8px 0;
  }

  .description {
    color: #909399;
    font-size: 14px;
    margin: 0;
  }

  .header-actions {
    display: flex;
    gap: 12px;
  }
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
  }

  .stat-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .stat-info {
    flex: 1;
  }

  .stat-title {
    font-size: 14px;
    color: #909399;
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }

  .stat-trend {
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 4px;

    &.up { color: #67c23a; }
    &.down { color: #f56c6c; }

    .trend-label {
      color: #909399;
      margin-left: 4px;
    }
  }

  .stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;

    .chart-controls {
      display: flex;
      gap: 12px;
      align-items: center;
    }
  }
}

.chart-container {
  width: 100%;
  height: 320px;
}

.gauge-container {
  width: 100%;
  height: 250px;
}

.quality-stats {
  margin-top: 16px;
  padding: 0 16px;

  .quality-item {
    margin-bottom: 12px;

    .quality-label {
      display: inline-block;
      width: 100px;
      font-size: 13px;
      color: #606266;
      margin-bottom: 4px;
    }
  }
}

.filter-card {
  margin-bottom: 20px;

  .filter-container {
    .filter-row {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
    }
  }
}

.table-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .table-actions {
    display: flex;
    gap: 8px;
    align-items: center;
  }
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.value-normal {
  color: #303133;
  font-weight: 500;
}

.value-corrected {
  color: #e6a23c;
  font-weight: 500;
  text-decoration: line-through;
  text-decoration-color: #f56c6c;
}

.value-original {
  color: #c0c4cc;
}

.telemetry-details {
  .data-lineage {
    margin-top: 20px;

    h4 {
      margin-bottom: 12px;
      color: #303133;
    }

    .lineage-steps {
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #f5f7fa;
      padding: 20px;
      border-radius: 8px;

      .lineage-step {
        text-align: center;

        .step-icon {
          font-size: 28px;
          margin-bottom: 8px;

          &.raw { filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1)); }
          &.validate { color: #67c23a; }
          &.correct { color: #e6a23c; }
          &.clean { color: #409eff; }
        }

        .step-label {
          font-size: 12px;
          font-weight: 500;
          color: #303133;
        }

        .step-time {
          font-size: 10px;
          color: #909399;
          margin-top: 4px;
        }
      }

      .lineage-arrow {
        font-size: 20px;
        color: #c0c4cc;
      }
    }
  }
}

.full-lineage {
  .lineage-chart-container {
    width: 100%;
    height: 400px;
    margin-bottom: 20px;
  }
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
}
</style>