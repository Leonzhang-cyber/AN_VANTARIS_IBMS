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
        <div class="loading-tip">Outlier Detection</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="outlier-detection-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Data Platform</el-breadcrumb-item>
            <el-breadcrumb-item>Data Quality</el-breadcrumb-item>
            <el-breadcrumb-item>Outlier Detection</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Outlier Detection</h1>
        <p class="description">Identify and analyze anomalous data points using statistical methods and ML algorithms</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
        <el-button type="primary" @click="handleScan">
          <el-icon><Search /></el-icon>
          Run Detection
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
                <span class="trend-label">vs last month</span>
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

    <!-- Outlier Visualization -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="14">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Outlier Distribution by Metric</span>
              <el-select v-model="selectedMetric" size="small" style="width: 180px">
                <el-option label="Energy Consumption (kWh)" value="energy" />
                <el-option label="Temperature (°C)" value="temperature" />
                <el-option label="Pressure (PSI)" value="pressure" />
                <el-option label="Response Time (ms)" value="response" />
              </el-select>
            </div>
          </template>
          <div ref="scatterChartRef" class="scatter-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="10">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Outlier Count by Table</span>
            </div>
          </template>
          <div ref="barChartRef" class="bar-chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Box Plot for Selected Metric -->
    <el-card class="boxplot-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Statistical Distribution with Outliers</span>
          <el-button size="small" @click="refreshBoxplot">
            <el-icon><Refresh /></el-icon>
            Refresh
          </el-button>
        </div>
      </template>
      <div ref="boxplotChartRef" class="boxplot-container"></div>
    </el-card>

    <!-- Filters -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-container">
        <div class="filter-row">
          <el-input
              v-model="filters.keyword"
              placeholder="Search by table or column"
              prefix-icon="Search"
              clearable
              style="width: 220px"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
          />
          <el-select v-model="filters.table" placeholder="Table" clearable style="width: 160px">
            <el-option label="energy_consumption" value="energy_consumption" />
            <el-option label="device_readings" value="device_readings" />
            <el-option label="maintenance_logs" value="maintenance_logs" />
          </el-select>
          <el-select v-model="filters.severity" placeholder="Severity" clearable style="width: 120px">
            <el-option label="Extreme" value="Extreme" />
            <el-option label="High" value="High" />
            <el-option label="Medium" value="Medium" />
            <el-option label="Low" value="Low" />
          </el-select>
          <el-select v-model="filters.status" placeholder="Status" clearable style="width: 120px">
            <el-option label="Open" value="Open" />
            <el-option label="Reviewed" value="Reviewed" />
            <el-option label="Resolved" value="Resolved" />
            <el-option label="False Positive" value="False Positive" />
          </el-select>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="handleResetFilters">Reset</el-button>
        </div>
      </div>
    </el-card>

    <!-- Outliers Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Detected Outliers ({{ filteredOutliers.length }} records)</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchOutliers" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedOutliers" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="id" label="ID"  />
        <el-table-column prop="table" label="Table"  show-overflow-tooltip />
        <el-table-column prop="column" label="Column" show-overflow-tooltip />
        <el-table-column prop="value" label="Value"  align="right">
          <template #default="{ row }">
            <span class="outlier-value">{{ row.value }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="expectedRange" label="Expected Range" />
        <el-table-column prop="zScore" label="Z-Score"  align="center">
          <template #default="{ row }">
            <el-tag :type="getZScoreTag(row.zScore)" size="small">{{ row.zScore.toFixed(2) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="Severity" >
          <template #default="{ row }">
            <el-tag :type="getSeverityTag(row.severity)" size="small">{{ row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" >
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detectedAt" label="Detected"  />
        <el-table-column label="Actions"  fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">Details</el-button>
            <el-button link type="success" size="small" @click="handleOutlier(row)">Handle</el-button>
            <el-button link type="info" size="small" @click="markFalsePositive(row)">False Positive</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[15, 30, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredOutliers.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Outlier Details Dialog -->
    <el-dialog v-model="detailsDialogVisible" :title="`Outlier Details - ${currentOutlier?.table}.${currentOutlier?.column}`" width="700px" destroy-on-close>
      <div class="outlier-details" v-if="currentOutlier">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Record ID">{{ currentOutlier.recordId }}</el-descriptions-item>
          <el-descriptions-item label="Table">{{ currentOutlier.table }}</el-descriptions-item>
          <el-descriptions-item label="Column">{{ currentOutlier.column }}</el-descriptions-item>
          <el-descriptions-item label="Detected Value">
            <span class="outlier-value-highlight">{{ currentOutlier.value }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="Expected Range">{{ currentOutlier.expectedRange }}</el-descriptions-item>
          <el-descriptions-item label="Z-Score">
            <el-tag :type="getZScoreTag(currentOutlier.zScore)" size="small">{{ currentOutlier.zScore.toFixed(2) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Severity">
            <el-tag :type="getSeverityTag(currentOutlier.severity)" size="small">{{ currentOutlier.severity }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTag(currentOutlier.status)" size="small">{{ currentOutlier.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Detection Method">{{ currentOutlier.detectionMethod }}</el-descriptions-item>
          <el-descriptions-item label="Detected At">{{ currentOutlier.detectedAt }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ currentOutlier.description }}</el-descriptions-item>
          <el-descriptions-item label="Suggested Action" :span="2">{{ currentOutlier.suggestedAction }}</el-descriptions-item>
        </el-descriptions>

        <!-- Context Data -->
        <div class="context-data">
          <h4>Contextual Information</h4>
          <el-table :data="currentOutlier.contextData || []" size="small" border>
            <el-table-column prop="timestamp" label="Timestamp" width="160" />
            <el-table-column prop="device" label="Device" />
            <el-table-column prop="normalValue" label="Normal Value"  />
            <el-table-column prop="outlierValue" label="Outlier Value"  />
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailsDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="handleOutlier(currentOutlier)">Handle Outlier</el-button>
      </template>
    </el-dialog>

    <!-- Handle Outlier Dialog -->
    <el-dialog v-model="handleDialogVisible" title="Handle Outlier" width="500px">
      <el-form :model="handleForm" label-width="120px">
        <el-form-item label="Action" prop="action">
          <el-select v-model="handleForm.action" placeholder="Select action" style="width: 100%">
            <el-option label="Correct Value" value="correct" />
            <el-option label="Remove Record" value="remove" />
            <el-option label="Mark as Anomaly (Keep)" value="keep" />
            <el-option label="Cap/Floor Value" value="cap" />
            <el-option label="Impute with Median" value="impute" />
          </el-select>
        </el-form-item>
        <el-form-item label="Corrected Value" v-if="handleForm.action === 'correct'">
          <el-input v-model="handleForm.correctedValue" placeholder="Enter corrected value" />
        </el-form-item>
        <el-form-item label="Reason">
          <el-input v-model="handleForm.reason" type="textarea" :rows="2" placeholder="Explain why this is an outlier" />
        </el-form-item>
        <el-form-item label="Apply to Similar">
          <el-switch v-model="handleForm.applyToSimilar" />
          <span style="margin-left: 8px; color: #909399">Apply same action to similar outliers</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitHandle">Apply Action</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  DataAnalysis, Filter, Warning, Delete
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading outlier detection data...',
  'Analyzing statistical distributions...',
  'Almost ready...'
]

// ==================== Chart References ====================
const scatterChartRef = ref<HTMLElement>()
const barChartRef = ref<HTMLElement>()
const boxplotChartRef = ref<HTMLElement>()
let scatterChart: echarts.ECharts | null = null
let barChart: echarts.ECharts | null = null
let boxplotChart: echarts.ECharts | null = null

// ==================== State ====================
const tableLoading = ref(false)
const detailsDialogVisible = ref(false)
const handleDialogVisible = ref(false)
const currentOutlier = ref<any>(null)
const currentPage = ref(1)
const pageSize = ref(15)
const selectedMetric = ref('energy')

const filters = reactive({
  keyword: '',
  table: '',
  severity: '',
  status: ''
})

const handleForm = reactive({
  action: 'correct',
  correctedValue: '',
  reason: '',
  applyToSimilar: false
})

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'Total Outliers', value: 156, trend: -8, icon: 'Warning', bgColor: '#f56c6c', key: 'total' },
  { title: 'Open Issues', value: 89, trend: -12, icon: 'Clock', bgColor: '#e6a23c', key: 'open' },
  { title: 'Resolved', value: 45, trend: 25, icon: 'Checked', bgColor: '#67c23a', key: 'resolved' },
  { title: 'False Positives', value: 22, trend: 10, icon: 'TrendCharts', bgColor: '#909399', key: 'false' }
])

const outliers = ref([
  {
    id: 1,
    table: 'energy_consumption',
    column: 'consumption_kwh',
    recordId: 'REC-1023',
    value: 15200,
    expectedRange: '2000 - 6000',
    zScore: 4.2,
    severity: 'Extreme',
    status: 'Open',
    detectedAt: '2024-01-18 08:30:00',
    detectionMethod: 'Z-Score (3σ)',
    description: 'Unusually high energy consumption spike detected during non-peak hours',
    suggestedAction: 'Investigate potential equipment malfunction or data recording error',
    contextData: [
      { timestamp: '2024-01-18 02:00:00', device: 'Main Meter', normalValue: 3200, outlierValue: 15200 },
      { timestamp: '2024-01-18 01:00:00', device: 'Main Meter', normalValue: 3100, outlierValue: 3100 },
      { timestamp: '2024-01-18 00:00:00', device: 'Main Meter', normalValue: 3050, outlierValue: 3050 }
    ]
  },
  {
    id: 2,
    table: 'device_readings',
    column: 'temperature',
    recordId: 'SEN-0456',
    value: 45.2,
    expectedRange: '18 - 28',
    zScore: 3.8,
    severity: 'High',
    status: 'Under Review',
    detectedAt: '2024-01-17 14:20:00',
    detectionMethod: 'IQR (1.5x rule)',
    description: 'Temperature reading significantly above normal operating range',
    suggestedAction: 'Check sensor calibration and HVAC system status',
    contextData: [
      { timestamp: '2024-01-17 14:00:00', device: 'Sensor A12', normalValue: 22.5, outlierValue: 22.5 },
      { timestamp: '2024-01-17 13:30:00', device: 'Sensor A12', normalValue: 22.3, outlierValue: 22.3 }
    ]
  },
  {
    id: 3,
    table: 'device_readings',
    column: 'pressure',
    recordId: 'SEN-0789',
    value: 85,
    expectedRange: '95 - 105',
    zScore: -3.2,
    severity: 'High',
    status: 'Open',
    detectedAt: '2024-01-17 09:15:00',
    detectionMethod: 'Isolation Forest',
    description: 'Pressure reading below minimum threshold indicating possible leak',
    suggestedAction: 'Inspect pressure system for leaks or sensor issues',
    contextData: []
  },
  {
    id: 4,
    table: 'maintenance_logs',
    column: 'duration_hours',
    recordId: 'MT-2345',
    value: 48,
    expectedRange: '0.5 - 8',
    zScore: 5.1,
    severity: 'Extreme',
    status: 'Resolved',
    detectedAt: '2024-01-16 11:00:00',
    detectionMethod: 'Z-Score (3σ)',
    description: 'Maintenance duration unusually long compared to historical average',
    suggestedAction: 'Review maintenance complexity and resource allocation',
    contextData: []
  },
  {
    id: 5,
    table: 'energy_consumption',
    column: 'cost_usd',
    recordId: 'INV-5678',
    value: -1250,
    expectedRange: '100 - 10000',
    zScore: -2.8,
    severity: 'Medium',
    status: 'Open',
    detectedAt: '2024-01-15 16:45:00',
    detectionMethod: 'Domain Validation',
    description: 'Negative cost value detected in invoice data',
    suggestedAction: 'Verify invoice entry and correct if data entry error',
    contextData: []
  },
  {
    id: 6,
    table: 'energy_consumption',
    column: 'consumption_kwh',
    recordId: 'REC-2341',
    value: 8500,
    expectedRange: '2000 - 6000',
    zScore: 2.9,
    severity: 'Medium',
    status: 'False Positive',
    detectedAt: '2024-01-14 10:30:00',
    detectionMethod: 'Z-Score (3σ)',
    description: 'Peak consumption during scheduled maintenance',
    suggestedAction: 'Mark as expected anomaly (false positive)',
    contextData: []
  }
])

// ==================== Computed ====================
const filteredOutliers = computed(() => {
  let filtered = [...outliers.value]

  if (filters.keyword) {
    filtered = filtered.filter(o =>
        o.table.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        o.column.toLowerCase().includes(filters.keyword.toLowerCase())
    )
  }

  if (filters.table) {
    filtered = filtered.filter(o => o.table === filters.table)
  }

  if (filters.severity) {
    filtered = filtered.filter(o => o.severity === filters.severity)
  }

  if (filters.status) {
    filtered = filtered.filter(o => o.status === filters.status)
  }

  return filtered
})

const paginatedOutliers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredOutliers.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getZScoreTag = (zScore: number) => {
  if (Math.abs(zScore) >= 4) return 'danger'
  if (Math.abs(zScore) >= 3) return 'warning'
  return 'info'
}

const getSeverityTag = (severity: string) => {
  const map: Record<string, string> = {
    'Extreme': 'danger',
    'High': 'warning',
    'Medium': 'info',
    'Low': 'success'
  }
  return map[severity] || 'info'
}

const getStatusTag = (status: string) => {
  const map: Record<string, string> = {
    'Open': 'danger',
    'Under Review': 'warning',
    'Reviewed': 'info',
    'Resolved': 'success',
    'False Positive': 'info'
  }
  return map[status] || 'info'
}

// ==================== Chart Initializations ====================
const initScatterChart = () => {
  if (!scatterChartRef.value) return
  if (scatterChart) scatterChart.dispose()

  scatterChart = echarts.init(scatterChartRef.value)

  // Generate mock scatter data
  const normalData = Array.from({ length: 200 }, () => [
    Math.random() * 100,
    Math.random() * 5000 + 2000
  ])
  const outlierData = [
    [25, 15200],
    [45, 8500],
    [60, 7200],
    [15, 9800],
    [80, 6800]
  ]

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'value', name: 'Time (hours)' },
    yAxis: { type: 'value', name: 'Value' },
    series: [
      { name: 'Normal Values', type: 'scatter', data: normalData, symbolSize: 8, color: '#409eff' },
      { name: 'Outliers', type: 'scatter', data: outlierData, symbolSize: 12, color: '#f56c6c' }
    ]
  }

  scatterChart.setOption(option)
  window.addEventListener('resize', () => scatterChart?.resize())
}

const initBarChart = () => {
  if (!barChartRef.value) return
  if (barChart) barChart.dispose()

  barChart = echarts.init(barChartRef.value)

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'category', data: ['energy_consumption', 'device_readings', 'maintenance_logs'], name: 'Table' },
    yAxis: { type: 'value', name: 'Outlier Count' },
    series: [{
      type: 'bar',
      data: [58, 72, 26],
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: '#f56c6c'
      },
      label: { show: true, position: 'top' }
    }]
  }

  barChart.setOption(option)
  window.addEventListener('resize', () => barChart?.resize())
}

const initBoxplotChart = () => {
  if (!boxplotChartRef.value) return
  if (boxplotChart) boxplotChart.dispose()

  boxplotChart = echarts.init(boxplotChartRef.value)

  // Boxplot data: [min, Q1, median, Q3, max]
  const normalData = [1200, 2500, 3200, 4200, 5800]
  const outlierData = [15200, 8500, 7200]

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    title: { show: false },
    xAxis: { type: 'category', data: ['Energy Consumption (kWh)'] },
    yAxis: { type: 'value', name: 'Value' },
    series: [
      {
        name: 'boxplot',
        type: 'boxplot',
        data: [normalData],
        itemStyle: { color: '#409eff', borderWidth: 2 },
        boxWidth: [40, 60]
      },
      {
        name: 'outliers',
        type: 'scatter',
        data: outlierData.map(v => [0, v]),
        symbolSize: 10,
        itemStyle: { color: '#f56c6c' }
      }
    ]
  }

  boxplotChart.setOption(option)
  window.addEventListener('resize', () => boxplotChart?.resize())
}

const refreshBoxplot = () => {
  initBoxplotChart()
  ElMessage.success('Chart refreshed')
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleResetFilters = () => {
  filters.keyword = ''
  filters.table = ''
  filters.severity = ''
  filters.status = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredOutliers.value.length} outlier records...`)
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const handleScan = () => {
  ElMessage.info('Running outlier detection algorithms...')
  setTimeout(() => {
    ElMessage.success('Detection completed. Found 8 new outliers.')
  }, 3000)
}

const fetchOutliers = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Outliers refreshed')
  }, 500)
}

const viewDetails = (outlier: any) => {
  currentOutlier.value = outlier
  detailsDialogVisible.value = true
}

const handleOutlier = (outlier: any) => {
  currentOutlier.value = outlier
  handleForm.action = 'correct'
  handleForm.correctedValue = ''
  handleForm.reason = ''
  handleForm.applyToSimilar = false
  handleDialogVisible.value = true
}

const markFalsePositive = (outlier: any) => {
  ElMessageBox.confirm(`Mark "${outlier.table}.${outlier.column}" as false positive?`, 'Confirm', {
    confirmButtonText: 'Yes',
    cancelButtonText: 'No',
    type: 'info'
  }).then(() => {
    const index = outliers.value.findIndex(o => o.id === outlier.id)
    if (index !== -1) {
      outliers.value[index].status = 'False Positive'
      ElMessage.success('Marked as false positive')
    }
  }).catch(() => {})
}

const submitHandle = () => {
  ElMessage.success(`Outlier handled: ${handleForm.action}`)
  handleDialogVisible.value = false
  // Update status
  if (currentOutlier.value) {
    const index = outliers.value.findIndex(o => o.id === currentOutlier.value.id)
    if (index !== -1) {
      outliers.value[index].status = 'Resolved'
    }
  }
}

const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {}

// ==================== Loading Simulation ====================
const initCharts = async () => {
  await nextTick()
  setTimeout(() => {
    initScatterChart()
    initBarChart()
    initBoxplotChart()
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
      fetchOutliers()
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
.outlier-detection-page {
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
  }
}

.scatter-container, .bar-chart-container {
  width: 100%;
  height: 320px;
}

.boxplot-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}

.boxplot-container {
  width: 100%;
  height: 400px;
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

.outlier-details {
  .context-data {
    margin-top: 20px;

    h4 {
      margin-bottom: 12px;
      color: #303133;
    }
  }
}

.outlier-value {
  font-weight: 600;
  color: #f56c6c;
}

.outlier-value-highlight {
  font-weight: 600;
  color: #f56c6c;
  font-size: 16px;
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
}
</style>