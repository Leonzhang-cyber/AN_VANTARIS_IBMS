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
        <div class="loading-tip">Not Developed Yet</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- ESG Dashboard Page Content -->
  <div v-else class="esg-dashboard-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>ESG Dashboard</h1>
        <p class="subtitle">Environmental, Social, and Governance performance metrics and compliance tracking</p>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="refreshData">Refresh</el-button>
        <el-button type="primary" :icon="Download" @click="exportReport">Export Report</el-button>
        <el-date-picker
            v-model="dateRange"
            type="year"
            placeholder="Select Year"
            :shortcuts="yearShortcuts"
            size="default"
            style="width: 120px"
            @change="handleDateChange"
        />
      </div>
    </div>

    <!-- Overall ESG Score -->
    <div class="overall-score-card">
      <div class="score-container">
        <div class="main-score">
          <el-progress
              type="circle"
              :percentage="overallScore"
              :color="getScoreColor(overallScore)"
              :width="160"
              :stroke-width="12"
          >
            <template #default>
              <div class="score-text">
                <span class="score-value">{{ overallScore }}</span>
                <span class="score-label">Overall ESG Score</span>
              </div>
            </template>
          </el-progress>
        </div>
        <div class="score-breakdown">
          <div class="breakdown-item environmental">
            <div class="breakdown-header">
              <span class="breakdown-name"><el-icon><Sunny /></el-icon> Environmental</span>
              <span class="breakdown-score">{{ environmentalScore }}</span>
            </div>
            <el-progress :percentage="environmentalScore" :color="getScoreColor(environmentalScore)" :stroke-width="8" />
            <div class="breakdown-detail">
              <span>Carbon: -12%</span>
              <span>Energy: -8%</span>
              <span>Water: -15%</span>
            </div>
          </div>
          <div class="breakdown-item social">
            <div class="breakdown-header">
              <span class="breakdown-name"><el-icon><User /></el-icon> Social</span>
              <span class="breakdown-score">{{ socialScore }}</span>
            </div>
            <el-progress :percentage="socialScore" :color="getScoreColor(socialScore)" :stroke-width="8" />
            <div class="breakdown-detail">
              <span>Safety: +5%</span>
              <span>Diversity: +8%</span>
              <span>Training: +15%</span>
            </div>
          </div>
          <div class="breakdown-item governance">
            <div class="breakdown-header">
              <span class="breakdown-name"><el-icon><Setting /></el-icon> Governance</span>
              <span class="breakdown-score">{{ governanceScore }}</span>
            </div>
            <el-progress :percentage="governanceScore" :color="getScoreColor(governanceScore)" :stroke-width="8" />
            <div class="breakdown-detail">
              <span>Compliance: 98%</span>
              <span>Risk: 85%</span>
              <span>Ethics: 100%</span>
            </div>
          </div>
        </div>
      </div>
      <div class="score-rating">
        <div class="rating-badge" :class="getRatingClass()">
          {{ getRatingLabel() }}
        </div>
        <div class="rating-comparison">
          <span>vs Industry Avg: <strong :class="overallScore >= industryAvg ? 'text-success' : 'text-danger'">{{ overallScore >= industryAvg ? '+' : '' }}{{ (overallScore - industryAvg).toFixed(1) }} pts</strong></span>
          <span>vs Last Year: <strong :class="yearOverYear >= 0 ? 'text-success' : 'text-danger'">{{ yearOverYear >= 0 ? '+' : '' }}{{ yearOverYear }} pts</strong></span>
        </div>
      </div>
    </div>

    <!-- ESG Trend Chart -->
    <div class="chart-card">
      <div class="card-header">
        <h3>ESG Performance Trend</h3>
        <el-radio-group v-model="trendPeriod" size="small" @change="fetchTrendData">
          <el-radio-button label="quarter">Quarterly</el-radio-button>
          <el-radio-button label="year">Yearly</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-container" ref="trendChartRef"></div>
    </div>

    <!-- Three Pillar Cards -->
    <div class="three-columns">
      <div class="pillar-card environmental">
        <div class="pillar-header">
          <div class="pillar-icon">
            <el-icon><Sunny /></el-icon>
          </div>
          <div class="pillar-title">Environmental</div>
          <div class="pillar-score">{{ environmentalScore }}</div>
        </div>
        <div class="pillar-metrics">
          <div class="metric-item">
            <span class="metric-label">Carbon Emissions</span>
            <span class="metric-value">12,500 tCO₂</span>
            <span class="metric-trend positive">-8%</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">Energy Consumption</span>
            <span class="metric-value">1.85M kWh</span>
            <span class="metric-trend positive">-5%</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">Renewable Energy</span>
            <span class="metric-value">32%</span>
            <span class="metric-trend positive">+12%</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">Water Usage</span>
            <span class="metric-value">45,000 m³</span>
            <span class="metric-trend positive">-15%</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">Waste Diversion</span>
            <span class="metric-value">68%</span>
            <span class="metric-trend positive">+7%</span>
          </div>
        </div>
      </div>

      <div class="pillar-card social">
        <div class="pillar-header">
          <div class="pillar-icon">
            <el-icon><User /></el-icon>
          </div>
          <div class="pillar-title">Social</div>
          <div class="pillar-score">{{ socialScore }}</div>
        </div>
        <div class="pillar-metrics">
          <div class="metric-item">
            <span class="metric-label">Employee Engagement</span>
            <span class="metric-value">4.2/5</span>
            <span class="metric-trend positive">+0.3</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">Safety Incidents</span>
            <span class="metric-value">12</span>
            <span class="metric-trend positive">-25%</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">Diversity Ratio</span>
            <span class="metric-value">42%</span>
            <span class="metric-trend positive">+4%</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">Training Hours</span>
            <span class="metric-value">4,500 hrs</span>
            <span class="metric-trend positive">+18%</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">Community Investment</span>
            <span class="metric-value">$250k</span>
            <span class="metric-trend positive">+10%</span>
          </div>
        </div>
      </div>

      <div class="pillar-card governance">
        <div class="pillar-header">
          <div class="pillar-icon">
            <el-icon><Setting /></el-icon>
          </div>
          <div class="pillar-title">Governance</div>
          <div class="pillar-score">{{ governanceScore }}</div>
        </div>
        <div class="pillar-metrics">
          <div class="metric-item">
            <span class="metric-label">Board Independence</span>
            <span class="metric-value">60%</span>
            <span class="metric-trend positive">+5%</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">Ethics Compliance</span>
            <span class="metric-value">98%</span>
            <span class="metric-trend positive">+2%</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">Risk Management</span>
            <span class="metric-value">85%</span>
            <span class="metric-trend positive">+8%</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">Data Privacy</span>
            <span class="metric-value">100%</span>
            <span class="metric-trend positive">0%</span>
          </div>
          <div class="metric-item">
            <span class="metric-label">Supply Chain Audit</span>
            <span class="metric-value">92%</span>
            <span class="metric-trend positive">+7%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ESG Metrics Table -->
    <div class="table-card">
      <div class="card-header">
        <h3>ESG Performance Metrics</h3>
        <el-input
            v-model="searchText"
            placeholder="Search metrics..."
            :prefix-icon="Search"
            style="width: 240px"
            clearable
        />
      </div>
      <el-table :data="paginatedMetrics" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="pillar" label="Pillar" width="120">
          <template #default="{ row }">
            <el-tag :type="getPillarTagType(row.pillar)" size="small">{{ row.pillar }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="metric" label="Metric" min-width="200" show-overflow-tooltip />
        <el-table-column prop="value" label="Value" width="140" align="center" sortable />
        <el-table-column prop="target" label="Target" width="140" align="center" sortable />
        <el-table-column prop="progress" label="Progress" width="180">
          <template #default="{ row }">
            <div class="progress-cell">
              <span class="progress-percent">{{ row.progress }}%</span>
              <el-progress :percentage="row.progress" :color="getProgressColor(row.progress)" :stroke-width="6" :show-text="false" style="flex: 1" />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="trend" label="Trend" width="100" align="center">
          <template #default="{ row }">
            <span :class="row.trend >= 0 ? 'text-success' : 'text-danger'">
              <el-icon v-if="row.trend > 0"><CaretTop /></el-icon>
              <el-icon v-else-if="row.trend < 0"><CaretBottom /></el-icon>
              <span v-else>—</span>
              {{ row.trend !== 0 ? Math.abs(row.trend) + '%' : '' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.progress >= 90 ? 'success' : row.progress >= 70 ? 'warning' : 'danger'" size="small" effect="dark">
              {{ row.progress >= 90 ? 'On Track' : row.progress >= 70 ? 'At Risk' : 'Off Track' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredMetrics.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Framework Compliance -->
    <div class="compliance-section">
      <div class="section-header">
        <h2>
          <el-icon><DocumentChecked /></el-icon>
          Framework Compliance
        </h2>
        <el-button link type="primary" @click="viewComplianceDetails">View Details →</el-button>
      </div>
      <div class="compliance-grid">
        <div v-for="framework in frameworks" :key="framework.name" class="compliance-card">
          <div class="framework-header">
            <span class="framework-name">{{ framework.name }}</span>
            <span class="framework-score">{{ framework.score }}%</span>
          </div>
          <div class="framework-progress">
            <el-progress :percentage="framework.score" :color="getScoreColor(framework.score)" :stroke-width="8" />
          </div>
          <div class="framework-details">
            <span>Compliant: {{ framework.compliant }}/{{ framework.total }}</span>
            <span>Gap: {{ framework.gap }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Refresh,
  Download,
  Sunny,
  User,
  Setting,
  Search,
  DocumentChecked,
  CaretTop,
  CaretBottom
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing...',
  'Almost ready...'
]

// ==================== Data Structures ====================
interface ESGPerformanceMetric {
  id: number
  pillar: string
  metric: string
  value: string
  target: string
  progress: number
  trend: number
}

interface FrameworkCompliance {
  name: string
  score: number
  compliant: number
  total: number
  gap: number
}

// ==================== State ====================
const dateRange = ref<Date | null>(null)
const trendPeriod = ref<'quarter' | 'year'>('quarter')
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const trendChartRef = ref<HTMLElement | null>(null)
let trendChart: echarts.ECharts | null = null

// ==================== Mock Data ====================
const esgMetrics = ref<ESGPerformanceMetric[]>([
  { id: 1, pillar: 'Environmental', metric: 'Carbon Emissions Reduction', value: '12,500 tCO₂', target: '11,000 tCO₂', progress: 65, trend: -8 },
  { id: 2, pillar: 'Environmental', metric: 'Renewable Energy Share', value: '32%', target: '50%', progress: 64, trend: 12 },
  { id: 3, pillar: 'Environmental', metric: 'Water Intensity Reduction', value: '45k m³', target: '40k m³', progress: 45, trend: -15 },
  { id: 4, pillar: 'Environmental', metric: 'Waste Diversion Rate', value: '68%', target: '75%', progress: 91, trend: 7 },
  { id: 5, pillar: 'Social', metric: 'Employee Engagement Score', value: '4.2/5', target: '4.5/5', progress: 84, trend: 6 },
  { id: 6, pillar: 'Social', metric: 'Safety Incident Rate', value: '0.8/100', target: '0.5/100', progress: 62, trend: -20 },
  { id: 7, pillar: 'Social', metric: 'Female Leadership Ratio', value: '42%', target: '50%', progress: 84, trend: 8 },
  { id: 8, pillar: 'Social', metric: 'Training Hours per Employee', value: '24 hrs', target: '40 hrs', progress: 60, trend: 20 },
  { id: 9, pillar: 'Governance', metric: 'Board Independence', value: '60%', target: '70%', progress: 86, trend: 5 },
  { id: 10, pillar: 'Governance', metric: 'Supplier ESG Audit', value: '92%', target: '100%', progress: 92, trend: 7 },
  { id: 11, pillar: 'Governance', metric: 'Risk Management Maturity', value: '85%', target: '90%', progress: 94, trend: 8 },
  { id: 12, pillar: 'Governance', metric: 'Data Privacy Compliance', value: '100%', target: '100%', progress: 100, trend: 0 }
])

const frameworks = ref<FrameworkCompliance[]>([
  { name: 'CSRD', score: 68, compliant: 8, total: 12, gap: 4 },
  { name: 'GRI', score: 85, compliant: 17, total: 20, gap: 3 },
  { name: 'TCFD', score: 72, compliant: 9, total: 11, gap: 2 },
  { name: 'ISSB', score: 45, compliant: 5, total: 11, gap: 6 },
  { name: 'SFDR', score: 62, compliant: 8, total: 13, gap: 5 }
])

// ==================== Computed Values ====================
const overallScore = computed(() => 78)
const environmentalScore = computed(() => 74)
const socialScore = computed(() => 82)
const governanceScore = computed(() => 80)
const industryAvg = computed(() => 72)
const yearOverYear = computed(() => 6)

const filteredMetrics = computed(() => {
  let result = [...esgMetrics.value]
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(m =>
        m.metric.toLowerCase().includes(search) ||
        m.pillar.toLowerCase().includes(search)
    )
  }
  return result
})

const paginatedMetrics = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredMetrics.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getScoreColor = (score: number) => {
  if (score >= 80) return '#67c23a'
  if (score >= 70) return '#409eff'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
}

const getProgressColor = (percentage: number) => {
  if (percentage >= 90) return '#67c23a'
  if (percentage >= 70) return '#409eff'
  if (percentage >= 50) return '#e6a23c'
  return '#f56c6c'
}

const getRatingClass = () => {
  if (overallScore.value >= 80) return 'rating-excellent'
  if (overallScore.value >= 70) return 'rating-good'
  if (overallScore.value >= 60) return 'rating-fair'
  return 'rating-poor'
}

const getRatingLabel = () => {
  if (overallScore.value >= 80) return 'Excellent'
  if (overallScore.value >= 70) return 'Good'
  if (overallScore.value >= 60) return 'Fair'
  return 'Needs Improvement'
}

const getPillarTagType = (pillar: string) => {
  const map: Record<string, string> = {
    Environmental: 'success',
    Social: 'primary',
    Governance: 'warning'
  }
  return map[pillar] || 'info'
}

const yearShortcuts = [
  { text: '2024', value: new Date(2024, 0, 1) },
  { text: '2023', value: new Date(2023, 0, 1) },
  { text: '2022', value: new Date(2022, 0, 1) }
]

// ==================== Chart Functions ====================
const generateTrendData = () => {
  if (trendPeriod.value === 'quarter') {
    return {
      labels: ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024', 'Q1 2025'],
      environmental: [68, 70, 72, 73, 74],
      social: [75, 77, 79, 81, 82],
      governance: [74, 75, 77, 79, 80],
      overall: [72, 74, 76, 78, 78]
    }
  }
  return {
    labels: ['2021', '2022', '2023', '2024', '2025'],
    environmental: [62, 65, 68, 72, 74],
    social: [68, 72, 76, 79, 82],
    governance: [66, 70, 73, 77, 80],
    overall: [65, 69, 72, 76, 78]
  }
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)
  const data = generateTrendData()

  trendChart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: (value: number) => value + ' points' },
    legend: { data: ['Environmental', 'Social', 'Governance', 'Overall'], bottom: 0 },
    grid: { left: '3%', right: '4%', top: '10%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', data: data.labels },
    yAxis: { type: 'value', name: 'ESG Score', min: 50, max: 100 },
    series: [
      { name: 'Environmental', type: 'line', data: data.environmental, smooth: true, symbol: 'circle', lineStyle: { width: 2, color: '#67c23a' } },
      { name: 'Social', type: 'line', data: data.social, smooth: true, symbol: 'diamond', lineStyle: { width: 2, color: '#409eff' } },
      { name: 'Governance', type: 'line', data: data.governance, smooth: true, symbol: 'triangle', lineStyle: { width: 2, color: '#e6a23c' } },
      { name: 'Overall', type: 'line', data: data.overall, smooth: true, symbol: 'circle', lineStyle: { width: 3, color: '#8b5cf6' }, areaStyle: { opacity: 0.1, color: '#8b5cf6' } }
    ]
  })
}

// ==================== Actions ====================
const refreshData = async () => {
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  ElMessage.success('ESG dashboard data refreshed')
  initTrendChart()
  tableLoading.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting ESG report...')
}

const fetchTrendData = () => {
  initTrendChart()
}

const handleDateChange = () => {
  currentPage.value = 1
}

const viewComplianceDetails = () => {
  ElMessage.info('Viewing compliance details')
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Window Resize Handler ====================
const handleResize = () => {
  trendChart?.resize()
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
      setTimeout(() => {
        initTrendChart()
      }, 100)
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
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
.esg-dashboard-page {
  padding: 24px;
  background: #f5f7fa;
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

.header-title h1 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2f3d;
  margin: 0 0 4px 0;
}

.header-title .subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* Overall Score Card */
.overall-score-card {
  background: white;
  border-radius: 20px;
  padding: 28px 32px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.score-container {
  display: flex;
  align-items: center;
  gap: 48px;
  flex-wrap: wrap;
}

.main-score {
  flex-shrink: 0;
}

.score-text {
  text-align: center;
}

.score-value {
  display: block;
  font-size: 32px;
  font-weight: 700;
  color: #1f2f3d;
}

.score-label {
  font-size: 12px;
  color: #909399;
}

.score-breakdown {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.breakdown-item {
  width: 100%;
}

.breakdown-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.breakdown-name {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 6px;
}

.breakdown-score {
  font-size: 18px;
  font-weight: 700;
  color: #1f2f3d;
}

.breakdown-detail {
  display: flex;
  gap: 20px;
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.breakdown-item.environmental .breakdown-name { color: #67c23a; }
.breakdown-item.social .breakdown-name { color: #409eff; }
.breakdown-item.governance .breakdown-name { color: #e6a23c; }

.score-rating {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.rating-badge {
  padding: 8px 24px;
  border-radius: 40px;
  font-size: 18px;
  font-weight: 600;
}

.rating-badge.rating-excellent {
  background: #e8f8f0;
  color: #67c23a;
}

.rating-badge.rating-good {
  background: #e8f4ff;
  color: #409eff;
}

.rating-badge.rating-fair {
  background: #fff7e8;
  color: #e6a23c;
}

.rating-badge.rating-poor {
  background: #ffe8e8;
  color: #f56c6c;
}

.rating-comparison {
  font-size: 14px;
  color: #606266;
  display: flex;
  gap: 24px;
}

/* Chart Cards */
.chart-card, .table-card {
  background: white;
  border-radius: 16px;
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
  color: #1f2f3d;
}

.chart-container {
  height: 350px;
  width: 100%;
}

/* Three Columns */
.three-columns {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.pillar-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s;
}

.pillar-card:hover {
  transform: translateY(-2px);
}

.pillar-card.environmental { border-top: 4px solid #67c23a; }
.pillar-card.social { border-top: 4px solid #409eff; }
.pillar-card.governance { border-top: 4px solid #e6a23c; }

.pillar-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.pillar-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pillar-card.environmental .pillar-icon { background: #e8f8f0; color: #67c23a; }
.pillar-card.social .pillar-icon { background: #e8f4ff; color: #409eff; }
.pillar-card.governance .pillar-icon { background: #fff7e8; color: #e6a23c; }

.pillar-title {
  flex: 1;
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

.pillar-score {
  font-size: 24px;
  font-weight: 700;
}

.pillar-card.environmental .pillar-score { color: #67c23a; }
.pillar-card.social .pillar-score { color: #409eff; }
.pillar-card.governance .pillar-score { color: #e6a23c; }

.pillar-metrics {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.metric-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.metric-label {
  font-size: 13px;
  color: #909399;
}

.metric-value {
  font-size: 14px;
  font-weight: 500;
  color: #1f2f3d;
}

.metric-trend {
  font-size: 12px;
  font-weight: 500;
}

.metric-trend.positive { color: #67c23a; }
.metric-trend.negative { color: #f56c6c; }

/* Table Styles */
.progress-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-percent {
  font-size: 13px;
  font-weight: 500;
  min-width: 40px;
}

.text-success {
  color: #67c23a;
  font-weight: 500;
}

.text-warning {
  color: #e6a23c;
  font-weight: 500;
}

.text-danger {
  color: #f56c6c;
  font-weight: 500;
}

.pagination-wrapper {
  padding: 20px 0 0;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
  margin-top: 16px;
}

/* Compliance Section */
.compliance-section {
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1f2f3d;
}

.compliance-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.compliance-card {
  background: #fafafa;
  border-radius: 14px;
  padding: 16px;
}

.framework-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.framework-name {
  font-weight: 600;
  font-size: 15px;
  color: #1f2f3d;
}

.framework-score {
  font-size: 20px;
  font-weight: 700;
}

.framework-details {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
  font-size: 12px;
  color: #909399;
}

:deep(.el-table) {
  border-radius: 12px;
}

:deep(.el-table th.el-table__cell) {
  background-color: #fafafa;
  font-weight: 600;
  color: #1f2f3d;
}
</style>