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
        <div class="loading-tip">Digital Twin - Twin Analytics</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="twin-analytics-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Twin Analytics</h1>
        <p>Advanced analytics and insights from your digital twin data with AI-powered predictions</p>
      </div>
      <div class="header-actions">
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            style="width: 260px"
            size="default"
        />
        <el-button type="primary" @click="refreshAnalytics">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
        <el-button @click="exportAnalytics">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon primary-bg">
            <el-icon><DataLine /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalDataPoints }}<span class="stat-unit">M</span></div>
            <div class="stat-label">Total Data Points</div>
            <div class="stat-trend positive">↑ {{ stats.dataPointGrowth }}%</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.insightsGenerated }}</div>
            <div class="stat-label">Insights Generated</div>
            <div class="stat-trend positive">↑ {{ stats.insightGrowth }} this week</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.anomaliesDetected }}</div>
            <div class="stat-label">Anomalies Detected</div>
            <div class="stat-trend negative">↑ {{ stats.anomalyGrowth }}% vs last period</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon info-bg">
            <el-icon><Cpu /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.modelAccuracy }}<span class="stat-unit">%</span></div>
            <div class="stat-label">AI Model Accuracy</div>
            <div class="stat-trend positive">↑ 2.3%</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Main Analytics Tabs -->
    <div class="analytics-tabs">
      <el-tabs v-model="activeTab" @tab-click="handleTabChange">
        <el-tab-pane label="Overview" name="overview" />
        <el-tab-pane label="Performance Metrics" name="performance" />
        <el-tab-pane label="Predictive Analytics" name="predictive" />
        <el-tab-pane label="Anomaly Detection" name="anomaly" />
        <el-tab-pane label="Comparative Analysis" name="comparative" />
      </el-tabs>
    </div>

    <!-- Overview Tab -->
    <div v-show="activeTab === 'overview'">
      <el-row :gutter="20">
        <el-col :xs="24" :lg="16">
          <div class="chart-card">
            <div class="card-header">
              <h3>Key Performance Indicators Trend</h3>
              <el-select v-model="kpiMetric" size="small" style="width: 140px">
                <el-option label="Energy Efficiency" value="energy" />
                <el-option label="Operational Cost" value="cost" />
                <el-option label="Asset Utilization" value="utilization" />
                <el-option label="System Health" value="health" />
              </el-select>
            </div>
            <div ref="kpiTrendChartRef" class="chart-container"></div>
          </div>
        </el-col>
        <el-col :xs="24" :lg="8">
          <div class="chart-card">
            <div class="card-header">
              <h3>Data Quality Score</h3>
            </div>
            <div ref="qualityGaugeRef" class="gauge-container"></div>
            <div class="quality-metrics">
              <div class="metric-item">
                <span>Completeness</span>
                <el-progress :percentage="dataQuality.completeness" :stroke-width="8" />
              </div>
              <div class="metric-item">
                <span>Accuracy</span>
                <el-progress :percentage="dataQuality.accuracy" :stroke-width="8" />
              </div>
              <div class="metric-item">
                <span>Timeliness</span>
                <el-progress :percentage="dataQuality.timeliness" :stroke-width="8" />
              </div>
              <div class="metric-item">
                <span>Consistency</span>
                <el-progress :percentage="dataQuality.consistency" :stroke-width="8" />
              </div>
            </div>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :xs="24" :lg="12">
          <div class="chart-card">
            <div class="card-header">
              <h3>Top Performing Assets</h3>
            </div>
            <div ref="topAssetsChartRef" class="small-chart"></div>
          </div>
        </el-col>
        <el-col :xs="24" :lg="12">
          <div class="chart-card">
            <div class="card-header">
              <h3>Alert Distribution by Severity</h3>
            </div>
            <div ref="alertDistChartRef" class="small-chart"></div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- Performance Metrics Tab -->
    <div v-show="activeTab === 'performance'">
      <el-row :gutter="20">
        <el-col :xs="24" :lg="8">
          <div class="metric-card" v-for="metric in performanceMetrics" :key="metric.name">
            <div class="metric-header">
              <span class="metric-name">{{ metric.name }}</span>
              <el-tag :type="metric.trend === 'up' ? 'danger' : 'success'" size="small">
                {{ metric.trend === 'up' ? '↑' : '↓' }} {{ Math.abs(metric.change) }}%
              </el-tag>
            </div>
            <div class="metric-value">{{ metric.value }}{{ metric.unit }}</div>
            <div class="metric-target">Target: {{ metric.target }}{{ metric.unit }}</div>
            <el-progress :percentage="metric.progress" :stroke-width="6" :color="metric.progress >= 90 ? '#67c23a' : metric.progress >= 70 ? '#e6a23c' : '#f56c6c'" />
          </div>
        </el-col>
        <el-col :xs="24" :lg="16">
          <div class="chart-card">
            <div class="card-header">
              <h3>Performance Benchmarking</h3>
              <el-select v-model="benchmarkMetric" size="small" style="width: 160px">
                <el-option label="Energy Intensity" value="energy" />
                <el-option label="Water Usage" value="water" />
                <el-option label="Carbon Footprint" value="carbon" />
                <el-option label="Maintenance Cost" value="maintenance" />
              </el-select>
            </div>
            <div ref="benchmarkChartRef" class="chart-container"></div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- Predictive Analytics Tab -->
    <div v-show="activeTab === 'predictive'">
      <el-row :gutter="20">
        <el-col :xs="24" :lg="16">
          <div class="chart-card">
            <div class="card-header">
              <h3>Energy Consumption Forecast</h3>
              <el-select v-model="forecastPeriod" size="small" style="width: 100px">
                <el-option label="7 Days" value="7" />
                <el-option label="30 Days" value="30" />
                <el-option label="90 Days" value="90" />
              </el-select>
            </div>
            <div ref="forecastChartRef" class="chart-container"></div>
          </div>
        </el-col>
        <el-col :xs="24" :lg="8">
          <div class="chart-card">
            <div class="card-header">
              <h3>Asset Failure Prediction</h3>
            </div>
            <div ref="failureChartRef" class="failure-chart"></div>
            <div class="prediction-list">
              <div v-for="asset in highRiskAssets" :key="asset.name" class="prediction-item">
                <div class="prediction-name">{{ asset.name }}</div>
                <div class="prediction-risk">
                  <el-progress :percentage="asset.risk" :stroke-width="6" :color="asset.risk >= 70 ? '#f56c6c' : asset.risk >= 40 ? '#e6a23c' : '#67c23a'" />
                </div>
                <div class="prediction-date">{{ asset.predictedFailure }}</div>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- Anomaly Detection Tab -->
    <div v-show="activeTab === 'anomaly'">
      <el-row :gutter="20">
        <el-col :xs="24" :lg="16">
          <div class="chart-card">
            <div class="card-header">
              <h3>Anomaly Detection Timeline</h3>
            </div>
            <div ref="anomalyChartRef" class="chart-container"></div>
          </div>
        </el-col>
        <el-col :xs="24" :lg="8">
          <div class="chart-card">
            <div class="card-header">
              <h3>Anomaly Types</h3>
            </div>
            <div ref="anomalyTypesRef" class="pie-chart"></div>
          </div>
        </el-col>
      </el-row>

      <div class="anomaly-table-wrapper">
        <div class="table-header">
          <h3>Recent Anomalies</h3>
          <el-button size="small" @click="exportAnomalies">Export</el-button>
        </div>
        <el-table :data="recentAnomalies" stripe>
          <el-table-column prop="timestamp" label="Timestamp" width="180" />
          <el-table-column prop="asset" label="Asset" min-width="150" />
          <el-table-column prop="metric" label="Metric" width="120" />
          <el-table-column prop="expectedValue" label="Expected" width="100" />
          <el-table-column prop="actualValue" label="Actual" width="100" />
          <el-table-column prop="severity" label="Severity" width="100">
            <template #default="{ row }">
              <el-tag :type="row.severity === 'critical' ? 'danger' : row.severity === 'warning' ? 'warning' : 'info'" size="small">
                {{ row.severity }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="100">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="investigateAnomaly(row)">Investigate</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- Comparative Analysis Tab -->
    <div v-show="activeTab === 'comparative'">
      <el-row :gutter="20">
        <el-col :xs="24" :lg="12">
          <div class="chart-card">
            <div class="card-header">
              <h3>Year-over-Year Comparison</h3>
              <el-select v-model="compareMetric" size="small" style="width: 140px">
                <el-option label="Energy (MWh)" value="energy" />
                <el-option label="Cost ($k)" value="cost" />
                <el-option label="Emissions (tons)" value="emissions" />
              </el-select>
            </div>
            <div ref="yoyChartRef" class="chart-container"></div>
          </div>
        </el-col>
        <el-col :xs="24" :lg="12">
          <div class="chart-card">
            <div class="card-header">
              <h3>Building Comparison</h3>
            </div>
            <div ref="buildingCompareRef" class="chart-container"></div>
          </div>
        </el-col>
      </el-row>

      <div class="insights-card">
        <div class="card-header">
          <h3>AI-Generated Insights</h3>
          <el-tag type="success">Updated just now</el-tag>
        </div>
        <div class="insights-list">
          <div v-for="insight in aiInsights" :key="insight.id" class="insight-item">
            <el-icon :class="insight.type"><component :is="insight.icon" /></el-icon>
            <div class="insight-content">
              <div class="insight-title">{{ insight.title }}</div>
              <div class="insight-description">{{ insight.description }}</div>
            </div>
            <div class="insight-confidence">{{ insight.confidence }}% confidence</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Investigation Dialog -->
    <el-dialog v-model="investigationDialog.visible" title="Anomaly Investigation" width="600px">
      <div v-if="investigationDialog.anomaly">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Asset">{{ investigationDialog.anomaly.asset }}</el-descriptions-item>
          <el-descriptions-item label="Metric">{{ investigationDialog.anomaly.metric }}</el-descriptions-item>
          <el-descriptions-item label="Timestamp">{{ investigationDialog.anomaly.timestamp }}</el-descriptions-item>
          <el-descriptions-item label="Severity">
            <el-tag :type="investigationDialog.anomaly.severity === 'critical' ? 'danger' : 'warning'">
              {{ investigationDialog.anomaly.severity }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Expected Value">{{ investigationDialog.anomaly.expectedValue }}</el-descriptions-item>
          <el-descriptions-item label="Actual Value">{{ investigationDialog.anomaly.actualValue }}</el-descriptions-item>
          <el-descriptions-item label="Deviation">{{ investigationDialog.anomaly.deviation }}%</el-descriptions-item>
          <el-descriptions-item label="Root Cause Analysis" :span="2">
            <div class="root-cause">{{ investigationDialog.anomaly.rootCause || 'Analysis in progress...' }}</div>
          </el-descriptions-item>
        </el-descriptions>
        <div class="investigation-actions">
          <el-button @click="investigationDialog.visible = false">Close</el-button>
          <el-button type="primary" @click="createWorkOrder">Create Work Order</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Refresh,
  Download,
  DataLine,
  TrendCharts,
  Warning,
  Cpu,
  Sunny,
  Clock,
  Connection,
  Check,
  CircleCheck
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading analytics engine...',
  'Processing twin data...',
  'Almost ready...'
]

// ==================== 响应式状态 ====================
const activeTab = ref('overview')
const dateRange = ref<Date[] | null>(null)
const kpiMetric = ref('energy')
const benchmarkMetric = ref('energy')
const forecastPeriod = ref('30')
const compareMetric = ref('energy')

const stats = reactive({
  totalDataPoints: 24.8,
  dataPointGrowth: 12.5,
  insightsGenerated: 156,
  insightGrowth: 8,
  anomaliesDetected: 23,
  anomalyGrowth: 15,
  modelAccuracy: 94.2
})

const dataQuality = reactive({
  completeness: 96,
  accuracy: 93,
  timeliness: 88,
  consistency: 91
})

const performanceMetrics = ref([
  { name: 'Energy Efficiency (EUI)', value: 125, unit: 'kWh/m²', target: 110, progress: 86, trend: 'down', change: 3.2 },
  { name: 'Water Usage', value: 1850, unit: 'm³', target: 1600, progress: 84, trend: 'up', change: 2.1 },
  { name: 'Carbon Intensity', value: 42, unit: 'kg CO₂/m²', target: 38, progress: 90, trend: 'down', change: 5.5 },
  { name: 'Asset Availability', value: 98.5, unit: '%', target: 99, progress: 99, trend: 'up', change: 0.3 },
  { name: 'Maintenance Cost', value: 12500, unit: '$', target: 10000, progress: 80, trend: 'up', change: 8.2 },
  { name: 'Occupancy Rate', value: 76, unit: '%', target: 85, progress: 89, trend: 'up', change: 4.1 }
])

const highRiskAssets = ref([
  { name: 'Chiller C-101', risk: 85, predictedFailure: '2024-08-15' },
  { name: 'UPS Unit B', risk: 72, predictedFailure: '2024-09-20' },
  { name: 'Cooling Tower CT-3', risk: 68, predictedFailure: '2024-10-05' },
  { name: 'HVAC Fan Coil FC-23', risk: 45, predictedFailure: '2024-11-12' }
])

const recentAnomalies = ref([
  { timestamp: '2024-06-12 14:23:00', asset: 'Chiller C-101', metric: 'Power Consumption', expectedValue: '245 kW', actualValue: '312 kW', severity: 'critical', deviation: 27.3, rootCause: 'Compressor efficiency degradation detected' },
  { timestamp: '2024-06-12 09:15:00', asset: 'Temperature Sensor T-42', metric: 'Temperature', expectedValue: '22.5°C', actualValue: '18.2°C', severity: 'warning', deviation: -19.1, rootCause: 'Sensor calibration drift' },
  { timestamp: '2024-06-11 22:30:00', asset: 'AHU-05', metric: 'Airflow', expectedValue: '850 CFM', actualValue: '620 CFM', severity: 'critical', deviation: -27.1, rootCause: 'Filter blockage detected' },
  { timestamp: '2024-06-11 16:45:00', asset: 'Power Meter PM-12', metric: 'Power Factor', expectedValue: '0.95', actualValue: '0.72', severity: 'warning', deviation: -24.2, rootCause: 'Harmonic distortion issue' }
])

const aiInsights = ref([
  { id: 1, type: 'success', icon: 'CircleCheck', title: 'Energy optimization opportunity detected', description: 'Adjusting HVAC setpoints by 2°C could reduce cooling costs by 15% during peak hours.', confidence: 92 },
  { id: 2, type: 'warning', icon: 'Warning', title: 'Predictive maintenance alert', description: 'Chiller C-101 shows signs of efficiency degradation. Schedule inspection within 30 days.', confidence: 88 },
  { id: 3, type: 'primary', icon: 'TrendCharts', title: 'Occupancy pattern change', description: 'Building occupancy has increased 18% compared to same period last month.', confidence: 96 },
  { id: 4, type: 'info', icon: 'Connection', title: 'IoT data quality improvement', description: 'Data completeness improved 5.2% after gateway firmware update.', confidence: 99 }
])

const investigationDialog = reactive({
  visible: false,
  anomaly: null as any
})

// ==================== 图表引用 ====================
const kpiTrendChartRef = ref<HTMLElement | null>(null)
const qualityGaugeRef = ref<HTMLElement | null>(null)
const topAssetsChartRef = ref<HTMLElement | null>(null)
const alertDistChartRef = ref<HTMLElement | null>(null)
const benchmarkChartRef = ref<HTMLElement | null>(null)
const forecastChartRef = ref<HTMLElement | null>(null)
const failureChartRef = ref<HTMLElement | null>(null)
const anomalyChartRef = ref<HTMLElement | null>(null)
const anomalyTypesRef = ref<HTMLElement | null>(null)
const yoyChartRef = ref<HTMLElement | null>(null)
const buildingCompareRef = ref<HTMLElement | null>(null)

let kpiTrendChart: echarts.ECharts | null = null
let qualityGauge: echarts.ECharts | null = null
let topAssetsChart: echarts.ECharts | null = null
let alertDistChart: echarts.ECharts | null = null
let benchmarkChart: echarts.ECharts | null = null
let forecastChart: echarts.ECharts | null = null
let failureChart: echarts.ECharts | null = null
let anomalyChart: echarts.ECharts | null = null
let anomalyTypes: echarts.ECharts | null = null
let yoyChart: echarts.ECharts | null = null
let buildingCompare: echarts.ECharts | null = null

// ==================== 图表渲染 ====================
const renderKpiTrendChart = () => {
  if (!kpiTrendChartRef.value) return
  if (kpiTrendChart) kpiTrendChart.dispose()

  kpiTrendChart = echarts.init(kpiTrendChartRef.value)

  const dates = Array.from({ length: 30 }, (_, i) => {
    const d = new Date()
    d.setDate(d.getDate() - (29 - i))
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  })

  let data: number[] = []
  if (kpiMetric.value === 'energy') {
    data = Array.from({ length: 30 }, () => 105 + Math.random() * 20)
  } else if (kpiMetric.value === 'cost') {
    data = Array.from({ length: 30 }, () => 8500 + Math.random() * 1500)
  } else if (kpiMetric.value === 'utilization') {
    data = Array.from({ length: 30 }, () => 65 + Math.random() * 25)
  } else {
    data = Array.from({ length: 30 }, () => 88 + Math.random() * 10)
  }

  kpiTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: dates, axisLabel: { rotate: 45, interval: 6 } },
    yAxis: { type: 'value' },
    series: [{
      type: 'line',
      data: data,
      smooth: true,
      lineStyle: { color: '#409eff', width: 2 },
      areaStyle: { opacity: 0.1, color: '#409eff' }
    }]
  })
}

const renderQualityGauge = () => {
  if (!qualityGaugeRef.value) return
  if (qualityGauge) qualityGauge.dispose()

  qualityGauge = echarts.init(qualityGaugeRef.value)

  qualityGauge.setOption({
    series: [{
      type: 'gauge',
      center: ['50%', '55%'],
      radius: '70%',
      startAngle: 210,
      endAngle: -30,
      min: 0,
      max: 100,
      splitNumber: 5,
      progress: { show: true, width: 15, itemStyle: { color: '#67c23a' } },
      axisLine: { lineStyle: { width: 15, color: [[0.85, '#67c23a'], [0.92, '#e6a23c'], [1, '#f56c6c']] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      pointer: { show: false },
      detail: { show: false },
      data: [{ value: 92 }]
    }]
  })
}

const renderTopAssetsChart = () => {
  if (!topAssetsChartRef.value) return
  if (topAssetsChart) topAssetsChart.dispose()

  topAssetsChart = echarts.init(topAssetsChartRef.value)

  const assets = ['Chiller C-101', 'AHU-05', 'UPS Unit B', 'Cooling Tower', 'CRAC-12']
  const efficiency = [94, 91, 96, 89, 93]

  topAssetsChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'category', data: assets, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'Efficiency (%)', max: 100 },
    series: [{
      type: 'bar',
      data: efficiency,
      itemStyle: { color: '#67c23a', borderRadius: [4, 4, 0, 0] }
    }]
  })
}

const renderAlertDistChart = () => {
  if (!alertDistChartRef.value) return
  if (alertDistChart) alertDistChart.dispose()

  alertDistChart = echarts.init(alertDistChartRef.value)

  alertDistChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { name: 'Critical', value: 8, itemStyle: { color: '#f56c6c' } },
        { name: 'Warning', value: 12, itemStyle: { color: '#e6a23c' } },
        { name: 'Info', value: 25, itemStyle: { color: '#409eff' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })
}

const renderBenchmarkChart = () => {
  if (!benchmarkChartRef.value) return
  if (benchmarkChart) benchmarkChart.dispose()

  benchmarkChart = echarts.init(benchmarkChartRef.value)

  const buildings = ['Building A', 'Building B', 'Building C', 'Building D', 'Average']
  let data: number[] = []

  if (benchmarkMetric.value === 'energy') {
    data = [125, 98, 142, 110, 119]
  } else if (benchmarkMetric.value === 'water') {
    data = [1850, 1520, 2100, 1680, 1787]
  } else if (benchmarkMetric.value === 'carbon') {
    data = [42, 35, 48, 38, 41]
  } else {
    data = [12500, 9800, 15200, 11200, 12175]
  }

  benchmarkChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['This Building', 'Benchmark'], top: 0 },
    xAxis: { type: 'category', data: buildings },
    yAxis: { type: 'value' },
    series: [
      { name: 'This Building', type: 'bar', data: data, itemStyle: { color: '#409eff', borderRadius: [4, 4, 0, 0] } },
      { name: 'Benchmark', type: 'line', data: data.map(d => d * 0.9), lineStyle: { color: '#67c23a', width: 2, type: 'dashed' } }
    ]
  })
}

const renderForecastChart = () => {
  if (!forecastChartRef.value) return
  if (forecastChart) forecastChart.dispose()

  forecastChart = echarts.init(forecastChartRef.value)

  const days = parseInt(forecastPeriod.value)
  const dates = Array.from({ length: days }, (_, i) => {
    const d = new Date()
    d.setDate(d.getDate() + i)
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  })

  const historicalData = Array.from({ length: 30 }, () => 120 + Math.random() * 30)
  const forecastData = Array.from({ length: days }, () => {
    const base = historicalData[historicalData.length - 1]
    return base + (Math.random() - 0.5) * 20
  })

  forecastChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Historical', 'Forecast'], top: 0 },
    xAxis: { type: 'category', data: dates.slice(0, 30) },
    yAxis: { type: 'value', name: 'Energy (MWh)' },
    series: [
      { name: 'Historical', type: 'line', data: historicalData, lineStyle: { color: '#8c9aab', width: 1.5 } },
      { name: 'Forecast', type: 'line', data: [...Array(30 - days).fill(null), ...forecastData], lineStyle: { color: '#409eff', width: 2, type: 'dashed' }, areaStyle: { opacity: 0.1 } }
    ]
  })
}

const renderFailureChart = () => {
  if (!failureChartRef.value) return
  if (failureChart) failureChart.dispose()

  failureChart = echarts.init(failureChartRef.value)

  failureChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: highRiskAssets.value.map(a => a.name), axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'Risk (%)', max: 100 },
    series: [{
      type: 'bar',
      data: highRiskAssets.value.map(a => a.risk),
      itemStyle: {
        color: (params: any) => {
          const val = params.data
          return val >= 70 ? '#f56c6c' : val >= 40 ? '#e6a23c' : '#67c23a'
        },
        borderRadius: [4, 4, 0, 0]
      }
    }]
  })
}

const renderAnomalyChart = () => {
  if (!anomalyChartRef.value) return
  if (anomalyChart) anomalyChart.dispose()

  anomalyChart = echarts.init(anomalyChartRef.value)

  const dates = Array.from({ length: 30 }, (_, i) => {
    const d = new Date()
    d.setDate(d.getDate() - (29 - i))
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  })

  const values = Array.from({ length: 30 }, () => 85 + Math.random() * 30)
  const anomalies = Array.from({ length: 30 }, () => Math.random() > 0.85 ? values[Math.floor(Math.random() * 30)] + 30 : null)

  anomalyChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: dates, axisLabel: { rotate: 45, interval: 6 } },
    yAxis: { type: 'value' },
    series: [
      { name: 'Normal Values', type: 'line', data: values, smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Anomalies', type: 'scatter', data: anomalies, itemStyle: { color: '#f56c6c', borderColor: 'white', borderWidth: 2 } }
    ]
  })
}

const renderAnomalyTypes = () => {
  if (!anomalyTypesRef.value) return
  if (anomalyTypes) anomalyTypes.dispose()

  anomalyTypes = echarts.init(anomalyTypesRef.value)

  anomalyTypes.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { name: 'Sensor Drift', value: 35, itemStyle: { color: '#e6a23c' } },
        { name: 'Equipment Fault', value: 28, itemStyle: { color: '#f56c6c' } },
        { name: 'Data Gap', value: 22, itemStyle: { color: '#8c9aab' } },
        { name: 'Network Issue', value: 15, itemStyle: { color: '#409eff' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })
}

const renderYoYChart = () => {
  if (!yoyChartRef.value) return
  if (yoyChart) yoyChart.dispose()

  yoyChart = echarts.init(yoyChartRef.value)

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  let currentYear: number[] = []
  let previousYear: number[] = []

  if (compareMetric.value === 'energy') {
    currentYear = Array.from({ length: 12 }, () => 110 + Math.random() * 30)
    previousYear = Array.from({ length: 12 }, () => 120 + Math.random() * 35)
  } else if (compareMetric.value === 'cost') {
    currentYear = Array.from({ length: 12 }, () => 8 + Math.random() * 4)
    previousYear = Array.from({ length: 12 }, () => 9 + Math.random() * 5)
  } else {
    currentYear = Array.from({ length: 12 }, () => 35 + Math.random() * 15)
    previousYear = Array.from({ length: 12 }, () => 40 + Math.random() * 18)
  }

  yoyChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Current Year', 'Previous Year'], top: 0 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value' },
    series: [
      { name: 'Current Year', type: 'line', data: currentYear, smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Previous Year', type: 'line', data: previousYear, smooth: true, lineStyle: { color: '#8c9aab', width: 1.5, type: 'dashed' } }
    ]
  })
}

const renderBuildingCompare = () => {
  if (!buildingCompareRef.value) return
  if (buildingCompare) buildingCompare.dispose()

  buildingCompare = echarts.init(buildingCompareRef.value)

  buildingCompare.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['Energy (kWh/m²)', 'Water (m³)', 'CO₂ (kg/m²)', 'Cost ($/m²)'] },
    yAxis: { type: 'value' },
    series: [
      { name: 'This Building', type: 'bar', data: [125, 1.85, 42, 125], itemStyle: { color: '#409eff', borderRadius: [4, 4, 0, 0] } },
      { name: 'Portfolio Avg', type: 'bar', data: [110, 1.62, 38, 112], itemStyle: { color: '#8c9aab', borderRadius: [4, 4, 0, 0] } }
    ]
  })
}

// ==================== 交互事件 ====================
const refreshAnalytics = () => {
  ElMessage.success('Analytics data refreshed')
  nextTick(() => {
    renderKpiTrendChart()
    renderQualityGauge()
    renderTopAssetsChart()
    renderAlertDistChart()
    renderBenchmarkChart()
    renderForecastChart()
    renderFailureChart()
    renderAnomalyChart()
    renderAnomalyTypes()
    renderYoYChart()
    renderBuildingCompare()
  })
}

const exportAnalytics = () => {
  const exportData = {
    generatedAt: new Date().toISOString(),
    stats: stats,
    dataQuality: dataQuality,
    performanceMetrics: performanceMetrics.value,
    recentAnomalies: recentAnomalies.value,
    aiInsights: aiInsights.value
  }
  const data = JSON.stringify(exportData, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `twin-analytics-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Analytics exported')
}

const exportAnomalies = () => {
  const data = JSON.stringify(recentAnomalies.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `anomalies-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Anomalies exported')
}

const investigateAnomaly = (anomaly: any) => {
  investigationDialog.anomaly = anomaly
  investigationDialog.visible = true
}

const createWorkOrder = () => {
  ElMessage.success('Work order created for investigation')
  investigationDialog.visible = false
}

const handleTabChange = () => {
  nextTick(() => {
    if (activeTab.value === 'overview') {
      renderKpiTrendChart()
      renderQualityGauge()
      renderTopAssetsChart()
      renderAlertDistChart()
    } else if (activeTab.value === 'performance') {
      renderBenchmarkChart()
    } else if (activeTab.value === 'predictive') {
      renderForecastChart()
      renderFailureChart()
    } else if (activeTab.value === 'anomaly') {
      renderAnomalyChart()
      renderAnomalyTypes()
    } else if (activeTab.value === 'comparative') {
      renderYoYChart()
      renderBuildingCompare()
    }
  })
}

// ==================== 数据加载 ====================
const loadData = () => {
  nextTick(() => {
    renderKpiTrendChart()
    renderQualityGauge()
    renderTopAssetsChart()
    renderAlertDistChart()
    renderBenchmarkChart()
    renderForecastChart()
    renderFailureChart()
    renderAnomalyChart()
    renderAnomalyTypes()
    renderYoYChart()
    renderBuildingCompare()
  })
}

// ==================== 生命周期 ====================
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
      loadData()
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', () => {
    kpiTrendChart?.resize()
    qualityGauge?.resize()
    topAssetsChart?.resize()
    alertDistChart?.resize()
    benchmarkChart?.resize()
    forecastChart?.resize()
    failureChart?.resize()
    anomalyChart?.resize()
    anomalyTypes?.resize()
    yoyChart?.resize()
    buildingCompare?.resize()
  })
})

watch([kpiMetric, benchmarkMetric, forecastPeriod, compareMetric], () => {
  nextTick(() => {
    if (activeTab.value === 'overview') renderKpiTrendChart()
    if (activeTab.value === 'performance') renderBenchmarkChart()
    if (activeTab.value === 'predictive') renderForecastChart()
    if (activeTab.value === 'comparative') renderYoYChart()
  })
})

watch(isLoaded, (loaded) => {
  if (loaded) {
    window.addEventListener('resize', () => {
      kpiTrendChart?.resize()
      qualityGauge?.resize()
      topAssetsChart?.resize()
      alertDistChart?.resize()
      benchmarkChart?.resize()
      forecastChart?.resize()
      failureChart?.resize()
      anomalyChart?.resize()
      anomalyTypes?.resize()
      yoyChart?.resize()
      buildingCompare?.resize()
    })
  }
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

/* ==================== Main Content Styles ==================== */
.twin-analytics-page {
  padding: 24px;
  background-color: #f5f7fa;
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

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #1f2f3d;
}

.page-header p {
  margin: 0;
  color: #5e6e82;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.primary-bg { background-color: #ecf5ff; color: #409eff; }
.success-bg { background-color: #f0f9eb; color: #67c23a; }
.warning-bg { background-color: #fff3e0; color: #e6a23c; }
.info-bg { background-color: #f5f7fa; color: #8c9aab; }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
  line-height: 1.2;
}

.stat-unit {
  font-size: 14px;
  font-weight: normal;
  color: #8c9aab;
  margin-left: 4px;
}

.stat-label {
  font-size: 13px;
  color: #8c9aab;
  margin-top: 4px;
}

.stat-trend {
  font-size: 11px;
  margin-top: 4px;
}

.stat-trend.positive { color: #67c23a; }
.stat-trend.negative { color: #f56c6c; }

/* Analytics Tabs */
.analytics-tabs {
  background: white;
  border-radius: 12px;
  padding: 0 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

/* Chart Cards */
.chart-card, .metric-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

.chart-container {
  height: 320px;
  width: 100%;
}

.small-chart {
  height: 240px;
  width: 100%;
}

.gauge-container {
  height: 180px;
  width: 100%;
}

.pie-chart {
  height: 240px;
  width: 100%;
}

.failure-chart {
  height: 220px;
  width: 100%;
}

/* Quality Metrics */
.quality-metrics {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.metric-item {
  margin-bottom: 12px;
}

.metric-item span {
  display: block;
  margin-bottom: 4px;
  font-size: 12px;
  color: #5e6e82;
}

/* Metric Cards */
.metric-card {
  margin-bottom: 16px;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.metric-name {
  font-weight: 600;
  font-size: 14px;
  color: #1f2f3d;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2f3d;
}

.metric-target {
  font-size: 11px;
  color: #8c9aab;
  margin-bottom: 8px;
}

/* Prediction List */
.prediction-list {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.prediction-item {
  margin-bottom: 16px;
}

.prediction-name {
  font-weight: 500;
  font-size: 13px;
  margin-bottom: 6px;
}

.prediction-date {
  font-size: 10px;
  color: #8c9aab;
  margin-top: 4px;
}

/* Anomaly Table */
.anomaly-table-wrapper {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

/* Insights Card */
.insights-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.insights-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.insight-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.insight-item .el-icon {
  font-size: 20px;
}

.insight-item .el-icon.success { color: #67c23a; }
.insight-item .el-icon.warning { color: #e6a23c; }
.insight-item .el-icon.primary { color: #409eff; }
.insight-item .el-icon.info { color: #8c9aab; }

.insight-content {
  flex: 1;
}

.insight-title {
  font-weight: 600;
  font-size: 13px;
  margin-bottom: 4px;
}

.insight-description {
  font-size: 12px;
  color: #5e6e82;
}

.insight-confidence {
  font-size: 11px;
  color: #67c23a;
  white-space: nowrap;
}

/* Investigation Dialog */
.root-cause {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 8px;
  font-size: 13px;
}

.investigation-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
}

:deep(.el-tabs__header) {
  margin-bottom: 0;
}

:deep(.el-tabs__nav-wrap::after) {
  display: none;
}
</style>