<template>
  <!-- Loading Screen -->
  <div v-if="!isLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">
          <span class="loading-title">ESG Compliance Overview</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Sustainability & Governance Intelligence</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="esg-compliance-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Flag /></el-icon>
          ESG Compliance Overview
        </h1>
        <div class="page-subtitle">Environmental, Social & Governance performance monitoring</div>
      </div>
      <div class="header-actions">
        <el-date-picker
            v-model="dateRange"
            type="year"
            placeholder="Select Year"
            format="YYYY"
            value-format="YYYY"
            style="width: 120px"
        />
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
        <el-button type="primary" @click="exportReport">
          <el-icon><Download /></el-icon> Export Report
        </el-button>
      </div>
    </div>

    <!-- ESG Score Hero Card -->
    <div class="esg-hero">
      <div class="esg-hero-bg"></div>
      <div class="esg-hero-content">
        <div class="hero-left">
          <div class="esg-badge">
            <span class="badge-icon">🌱</span>
            Overall ESG Score
          </div>
          <div class="esg-score">
            <span class="score-value">{{ overallScore }}</span>
            <span class="score-total">/100</span>
          </div>
          <div class="esg-rating">
            <span class="rating-label">Rating</span>
            <span class="rating-value" :class="ratingClass">{{ ratingText }}</span>
            <span class="rating-trend up">↑ {{ scoreChange }} pts vs last year</span>
          </div>
          <div class="esg-breakdown">
            <div class="breakdown-item">
              <span class="breakdown-label">Environmental</span>
              <div class="breakdown-bar">
                <div class="bar-fill e" :style="{ width: eScore + '%' }"></div>
              </div>
              <span class="breakdown-value">{{ eScore }}</span>
            </div>
            <div class="breakdown-item">
              <span class="breakdown-label">Social</span>
              <div class="breakdown-bar">
                <div class="bar-fill s" :style="{ width: sScore + '%' }"></div>
              </div>
              <span class="breakdown-value">{{ sScore }}</span>
            </div>
            <div class="breakdown-item">
              <span class="breakdown-label">Governance</span>
              <div class="breakdown-bar">
                <div class="bar-fill g" :style="{ width: gScore + '%' }"></div>
              </div>
              <span class="breakdown-value">{{ gScore }}</span>
            </div>
          </div>
        </div>
        <div class="hero-right">
          <div class="radar-container">
            <div class="radar-chart" ref="radarChart"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Cards - E, S, G -->
    <div class="esg-stats">
      <div class="stat-card environmental">
        <div class="stat-header">
          <div class="stat-icon">
            <el-icon><PictureRounded /></el-icon>
          </div>
          <span class="stat-title">Environmental</span>
          <span class="stat-score">{{ eScore }}<span class="unit">/100</span></span>
        </div>
        <div class="stat-metrics">
          <div class="metric">
            <span class="metric-label">Carbon Footprint</span>
            <span class="metric-value">↓ 24% YoY</span>
          </div>
          <div class="metric">
            <span class="metric-label">Renewable Energy</span>
            <span class="metric-value">65%</span>
          </div>
          <div class="metric">
            <span class="metric-label">Water Reduction</span>
            <span class="metric-value">18%</span>
          </div>
          <div class="metric">
            <span class="metric-label">Waste Recycling</span>
            <span class="metric-value">82%</span>
          </div>
        </div>
        <div class="stat-progress">
          <el-progress :percentage="eScore" :stroke-width="8" color="#22c55e" />
        </div>
      </div>
      <div class="stat-card social">
        <div class="stat-header">
          <div class="stat-icon">
            <el-icon><User /></el-icon>
          </div>
          <span class="stat-title">Social</span>
          <span class="stat-score">{{ sScore }}<span class="unit">/100</span></span>
        </div>
        <div class="stat-metrics">
          <div class="metric">
            <span class="metric-label">Employee Satisfaction</span>
            <span class="metric-value">4.5/5</span>
          </div>
          <div class="metric">
            <span class="metric-label">Diversity Ratio</span>
            <span class="metric-value">42%</span>
          </div>
          <div class="metric">
            <span class="metric-label">Training Hours</span>
            <span class="metric-value">48 hrs/emp</span>
          </div>
          <div class="metric">
            <span class="metric-label">Safety Incidents</span>
            <span class="metric-value">0</span>
          </div>
        </div>
        <div class="stat-progress">
          <el-progress :percentage="sScore" :stroke-width="8" color="#3b82f6" />
        </div>
      </div>
      <div class="stat-card governance">
        <div class="stat-header">
          <div class="stat-icon">
            <el-icon><OfficeBuilding /></el-icon>
          </div>
          <span class="stat-title">Governance</span>
          <span class="stat-score">{{ gScore }}<span class="unit">/100</span></span>
        </div>
        <div class="stat-metrics">
          <div class="metric">
            <span class="metric-label">Board Diversity</span>
            <span class="metric-value">40%</span>
          </div>
          <div class="metric">
            <span class="metric-label">Ethics Training</span>
            <span class="metric-value">100%</span>
          </div>
          <div class="metric">
            <span class="metric-label">Risk Management</span>
            <span class="metric-value">Advanced</span>
          </div>
          <div class="metric">
            <span class="metric-label">Audit Compliance</span>
            <span class="metric-value">98%</span>
          </div>
        </div>
        <div class="stat-progress">
          <el-progress :percentage="gScore" :stroke-width="8" color="#8b5cf6" />
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-section">
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot"></span>
            Carbon Emissions Trend (tCO2e)
          </div>
        </div>
        <div class="chart-container" ref="carbonChart"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot green"></span>
            Energy Mix
          </div>
        </div>
        <div class="chart-container" ref="energyChart"></div>
      </div>
    </div>

    <div class="charts-section">
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot blue"></span>
            Water Consumption (m³)
          </div>
        </div>
        <div class="chart-container" ref="waterChart"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot purple"></span>
            Waste Diversion Rate
          </div>
        </div>
        <div class="chart-container" ref="wasteChart"></div>
      </div>
    </div>

    <!-- Compliance Frameworks -->
    <div class="frameworks-card">
      <div class="card-header">
        <span class="card-title">Compliance Frameworks</span>
        <el-tag type="success" size="large">Compliant</el-tag>
      </div>
      <div class="frameworks-grid">
        <div class="framework-item" v-for="fw in frameworks" :key="fw.name">
          <div class="framework-icon" :class="fw.status">
            <el-icon><CircleCheck v-if="fw.status === 'compliant'" /><Warning v-else-if="fw.status === 'partial'" /><Close v-else /></el-icon>
          </div>
          <div class="framework-info">
            <div class="framework-name">{{ fw.name }}</div>
            <div class="framework-status" :class="fw.status">{{ fw.statusText }}</div>
          </div>
          <div class="framework-score">{{ fw.score }}%</div>
        </div>
      </div>
    </div>

    <!-- ESG Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">ESG Performance Metrics</span>
        <el-input
            v-model="searchText"
            placeholder="Search metrics..."
            style="width: 200px"
            clearable
            :prefix-icon="Search"
            size="small"
        />
      </div>
      <el-table :data="filteredMetrics" stripe border style="width: 100%">
        <el-table-column prop="category" label="Category" />
        <el-table-column prop="metric" label="Metric" />
        <el-table-column prop="currentValue" label="Current Value" />
        <el-table-column prop="target" label="Target" />
        <el-table-column prop="status" label="Status">
          <template #default="{ row }">
            <el-tag :type="row.status === 'on-track' ? 'success' : (row.status === 'at-risk' ? 'warning' : 'danger')" size="small">
              {{ row.status === 'on-track' ? 'On Track' : (row.status === 'at-risk' ? 'At Risk' : 'Behind') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="Progress">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :stroke-width="8" :color="getProgressColor(row.progress)" />
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Flag, Download, Refresh, PictureRounded, User, OfficeBuilding,
  CircleCheck, Warning, Close, Search
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading ESG data...')
const refreshing = ref(false)

const loadingMessages = [
  'Loading ESG data...',
  'Analyzing compliance metrics...',
  'Calculating carbon footprint...',
  'Generating sustainability report...',
  'Almost ready...'
]

// ==================== State ====================
const dateRange = ref('2024')
const searchText = ref('')
const overallScore = ref(85)
const scoreChange = ref(6)
const eScore = ref(82)
const sScore = ref(88)
const gScore = ref(85)

const ratingText = computed(() => {
  if (overallScore.value >= 85) return 'Excellent'
  if (overallScore.value >= 70) return 'Good'
  if (overallScore.value >= 50) return 'Fair'
  return 'Needs Improvement'
})

const ratingClass = computed(() => {
  if (overallScore.value >= 85) return 'excellent'
  if (overallScore.value >= 70) return 'good'
  return 'fair'
})

const frameworks = ref([
  { name: 'GRI Standards', status: 'compliant', statusText: 'Compliant', score: 95 },
  { name: 'SASB Standards', status: 'compliant', statusText: 'Compliant', score: 92 },
  { name: 'TCFD Recommendations', status: 'compliant', statusText: 'Compliant', score: 88 },
  { name: 'UN Global Compact', status: 'compliant', statusText: 'Compliant', score: 90 },
  { name: 'ISO 26000', status: 'partial', statusText: 'Partial', score: 75 },
  { name: 'CDP Disclosure', status: 'compliant', statusText: 'Compliant', score: 85 }
])

const esgMetrics = ref([
  { category: 'Environmental', metric: 'Scope 1 Emissions (tCO2e)', currentValue: '12,500', target: '11,000', status: 'at-risk', progress: 65 },
  { category: 'Environmental', metric: 'Scope 2 Emissions (tCO2e)', currentValue: '8,200', target: '7,500', status: 'on-track', progress: 78 },
  { category: 'Environmental', metric: 'Renewable Energy Ratio (%)', currentValue: '65', target: '75', status: 'on-track', progress: 70 },
  { category: 'Environmental', metric: 'Water Intensity (L/kWh)', currentValue: '1.25', target: '1.10', status: 'at-risk', progress: 55 },
  { category: 'Social', metric: 'Employee Turnover Rate (%)', currentValue: '12', target: '10', status: 'at-risk', progress: 60 },
  { category: 'Social', metric: 'Gender Diversity (%)', currentValue: '42', target: '45', status: 'on-track', progress: 75 },
  { category: 'Social', metric: 'Training Hours per Employee', currentValue: '48', target: '50', status: 'on-track', progress: 85 },
  { category: 'Social', metric: 'Health & Safety Incidents', currentValue: '2', target: '0', status: 'behind', progress: 40 },
  { category: 'Governance', metric: 'Board Independence (%)', currentValue: '60', target: '50', status: 'on-track', progress: 100 },
  { category: 'Governance', metric: 'Ethics Training Completion (%)', currentValue: '98', target: '100', status: 'on-track', progress: 90 },
  { category: 'Governance', metric: 'Risk Assessment Coverage (%)', currentValue: '95', target: '100', status: 'on-track', progress: 85 },
  { category: 'Governance', metric: 'Audit Findings Closed (%)', currentValue: '92', target: '100', status: 'at-risk', progress: 68 }
])

const filteredMetrics = computed(() => {
  if (!searchText.value) return esgMetrics.value
  const search = searchText.value.toLowerCase()
  return esgMetrics.value.filter(m =>
      m.metric.toLowerCase().includes(search) ||
      m.category.toLowerCase().includes(search)
  )
})

// ==================== Helper Functions ====================
const getProgressColor = (progress: number): string => {
  if (progress >= 80) return '#22c55e'
  if (progress >= 50) return '#f59e0b'
  return '#ef4444'
}

const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

const exportReport = () => {
  ElMessage.success('Export started')
  setTimeout(() => {
    ElMessage.success('ESG report exported')
  }, 1500)
}

// ==================== Chart Refs ====================
const radarChart = ref<HTMLElement | null>(null)
const carbonChart = ref<HTMLElement | null>(null)
const energyChart = ref<HTMLElement | null>(null)
const waterChart = ref<HTMLElement | null>(null)
const wasteChart = ref<HTMLElement | null>(null)

let radarChartInstance: echarts.ECharts | null = null
let carbonChartInstance: echarts.ECharts | null = null
let energyChartInstance: echarts.ECharts | null = null
let waterChartInstance: echarts.ECharts | null = null
let wasteChartInstance: echarts.ECharts | null = null

// ==================== Initialize Charts ====================
const initRadarChart = () => {
  if (!radarChart.value) return
  if (radarChartInstance) radarChartInstance.dispose()

  radarChartInstance = echarts.init(radarChart.value)
  radarChartInstance.setOption({
    radar: {
      indicator: [
        { name: 'Carbon Reduction', max: 100 },
        { name: 'Energy Efficiency', max: 100 },
        { name: 'Water Stewardship', max: 100 },
        { name: 'Social Impact', max: 100 },
        { name: 'Governance', max: 100 },
        { name: 'Transparency', max: 100 }
      ],
      shape: 'circle',
      name: { textStyle: { fontSize: 10, color: '#64748b' } }
    },
    series: [{
      type: 'radar',
      data: [{ value: [85, 88, 78, 82, 86, 90], name: 'Your Score' }],
      areaStyle: { color: 'rgba(34, 197, 94, 0.2)' },
      lineStyle: { color: '#22c55e', width: 2 },
      itemStyle: { color: '#22c55e' }
    }]
  })
}

const initCarbonChart = () => {
  if (!carbonChart.value) return
  if (carbonChartInstance) carbonChartInstance.dispose()

  carbonChartInstance = echarts.init(carbonChart.value)
  carbonChartInstance.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 20 },
    xAxis: { type: 'category', data: ['2020', '2021', '2022', '2023', '2024'] },
    yAxis: { type: 'value', name: 'tCO2e (thousands)' },
    series: [{
      type: 'line',
      data: [28.5, 26.8, 24.2, 22.5, 20.7],
      smooth: true,
      lineStyle: { color: '#22c55e', width: 3 },
      areaStyle: { opacity: 0.1 },
      symbol: 'circle',
      symbolSize: 8
    }]
  })
}

const initEnergyChart = () => {
  if (!energyChart.value) return
  if (energyChartInstance) energyChartInstance.dispose()

  energyChartInstance = echarts.init(energyChart.value)
  energyChartInstance.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: 35, name: 'Grid (Non-renewable)', itemStyle: { color: '#94a3b8' } },
        { value: 45, name: 'Solar', itemStyle: { color: '#fbbf24' } },
        { value: 20, name: 'Wind', itemStyle: { color: '#22c55e' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })
}

const initWaterChart = () => {
  if (!waterChart.value) return
  if (waterChartInstance) waterChartInstance.dispose()

  waterChartInstance = echarts.init(waterChart.value)
  waterChartInstance.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 20 },
    xAxis: { type: 'category', data: ['Q1', 'Q2', 'Q3', 'Q4'] },
    yAxis: { type: 'value', name: 'm³ (thousands)' },
    series: [{
      type: 'bar',
      data: [45, 42, 38, 35],
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#3b82f6' },
      label: { show: true, position: 'top' }
    }]
  })
}

const initWasteChart = () => {
  if (!wasteChart.value) return
  if (wasteChartInstance) wasteChartInstance.dispose()

  wasteChartInstance = echarts.init(wasteChart.value)
  wasteChartInstance.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 20 },
    xAxis: { type: 'category', data: ['2020', '2021', '2022', '2023', '2024'] },
    yAxis: { type: 'value', name: 'Diversion Rate (%)', max: 100 },
    series: [{
      type: 'line',
      data: [68, 72, 76, 80, 82],
      smooth: true,
      lineStyle: { color: '#8b5cf6', width: 3 },
      areaStyle: { opacity: 0.1 },
      symbol: 'circle',
      symbolSize: 8
    }]
  })
}

const resizeCharts = () => {
  [radarChartInstance, carbonChartInstance, energyChartInstance, waterChartInstance, wasteChartInstance].forEach(chart => {
    if (chart) chart.resize()
  })
}

// ==================== Loading Animation ====================
const startLoading = () => {
  let progress = 0
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 12
      loadingProgress.value = Math.min(progress, 90)
    }
  }, 100)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => {
        initRadarChart()
        initCarbonChart()
        initEnergyChart()
        initWaterChart()
        initWasteChart()
      })
      window.addEventListener('resize', resizeCharts)
    }, 500)
  }, 2200)
}

onMounted(() => {
  startLoading()
})
</script>

<style scoped>
* {
  scrollbar-width: thin;
}
*::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
*::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}
*::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

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
.spinner-ring:nth-child(4) { border-left-color: #ec489a; animation-delay: 0.6s; width: 20%; height: 20%; top: 40%; left: 40%; }

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

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

/* ==================== Main Page ==================== */
.esg-compliance-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 24px;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* ESG Hero */
.esg-hero {
  position: relative;
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-radius: 28px;
  margin-bottom: 24px;
  overflow: hidden;
}

.esg-hero-bg {
  position: absolute;
  top: 0;
  right: 0;
  width: 50%;
  height: 100%;
  background: radial-gradient(ellipse at center, rgba(34, 197, 94, 0.1) 0%, transparent 70%);
}

.esg-hero-content {
  position: relative;
  padding: 32px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 30px;
}

.hero-left {
  flex: 1;
}

.esg-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 6px 14px;
  border-radius: 30px;
  font-size: 13px;
  color: #94a3b8;
  margin-bottom: 20px;
}

.esg-score {
  margin-bottom: 12px;
}

.score-value {
  font-size: 64px;
  font-weight: 800;
  color: white;
}

.score-total {
  font-size: 24px;
  color: #64748b;
  margin-left: 4px;
}

.esg-rating {
  margin-bottom: 24px;
}

.rating-label {
  font-size: 13px;
  color: #94a3b8;
  margin-right: 12px;
}

.rating-value {
  font-size: 20px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 30px;
  margin-right: 12px;
}

.rating-value.excellent { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
.rating-value.good { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
.rating-value.fair { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }

.rating-trend {
  font-size: 12px;
  color: #4ade80;
}

.esg-breakdown {
  max-width: 300px;
}

.breakdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.breakdown-label {
  width: 45px;
  font-size: 12px;
  color: #94a3b8;
}

.breakdown-bar {
  flex: 1;
  height: 6px;
  background: #334155;
  border-radius: 3px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 3px;
}

.bar-fill.e { background: #22c55e; }
.bar-fill.s { background: #3b82f6; }
.bar-fill.g { background: #8b5cf6; }

.breakdown-value {
  width: 35px;
  font-size: 12px;
  font-weight: 600;
  color: white;
}

.hero-right {
  display: flex;
  justify-content: center;
  align-items: center;
}

.radar-container {
  width: 280px;
  height: 280px;
}

.radar-chart {
  width: 100%;
  height: 100%;
}

/* ESG Stats Cards */
.esg-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.stat-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.stat-card.environmental .stat-icon { background: #dcfce7; color: #22c55e; }
.stat-card.social .stat-icon { background: #eef2ff; color: #3b82f6; }
.stat-card.governance .stat-icon { background: #f3e8ff; color: #8b5cf6; }

.stat-title {
  flex: 1;
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.stat-score {
  font-size: 24px;
  font-weight: 700;
}

.stat-card.environmental .stat-score { color: #22c55e; }
.stat-card.social .stat-score { color: #3b82f6; }
.stat-card.governance .stat-score { color: #8b5cf6; }

.stat-score .unit {
  font-size: 12px;
  font-weight: normal;
  color: #64748b;
}

.stat-metrics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
}

.metric {
  display: flex;
  flex-direction: column;
}

.metric-label {
  font-size: 11px;
  color: #64748b;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.stat-progress {
  margin-top: 8px;
}

/* Charts Section */
.charts-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.chart-header {
  margin-bottom: 20px;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.title-dot {
  width: 8px;
  height: 8px;
  background: #ef4444;
  border-radius: 50%;
}

.title-dot.green { background: #22c55e; }
.title-dot.blue { background: #3b82f6; }
.title-dot.purple { background: #8b5cf6; }

.chart-container {
  height: 280px;
  width: 100%;
}

/* Frameworks Card */
.frameworks-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.frameworks-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.framework-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 16px;
  transition: all 0.2s;
}

.framework-item:hover {
  transform: translateY(-2px);
  background: #f1f5f9;
}

.framework-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.framework-icon.compliant { background: #dcfce7; color: #22c55e; }
.framework-icon.partial { background: #fef3c7; color: #f59e0b; }
.framework-icon.non-compliant { background: #fee2e2; color: #ef4444; }

.framework-info {
  flex: 1;
}

.framework-name {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
  margin-bottom: 4px;
}

.framework-status {
  font-size: 11px;
}

.framework-status.compliant { color: #22c55e; }
.framework-status.partial { color: #f59e0b; }

.framework-score {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

/* Table Container */
.table-container {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.table-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

/* Responsive */
@media (max-width: 1000px) {
  .esg-stats {
    grid-template-columns: 1fr;
  }

  .charts-section {
    grid-template-columns: 1fr;
  }

  .frameworks-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .esg-hero-content {
    flex-direction: column;
    text-align: center;
  }

  .esg-breakdown {
    max-width: 100%;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .frameworks-grid {
    grid-template-columns: 1fr;
  }

  .esg-hero-content {
    padding: 24px;
  }

  .score-value {
    font-size: 48px;
  }
}
</style>