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

  <!-- ESG Score Page Content -->
  <div v-else class="esg-score-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>ESG Score</h1>
        <p class="subtitle">Monitor Environmental, Social, and Governance performance metrics</p>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="refreshData">Refresh</el-button>
        <el-button type="primary" :icon="Download" @click="exportReport">Export Report</el-button>
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            :shortcuts="dateShortcuts"
            size="default"
            style="width: 260px"
            @change="handleDateChange"
        />
      </div>
    </div>

    <!-- Overall ESG Score Card -->
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
          <div class="breakdown-item">
            <div class="breakdown-header">
              <span class="breakdown-name">Environmental (E)</span>
              <span class="breakdown-score">{{ environmentalScore }}</span>
            </div>
            <el-progress :percentage="environmentalScore" :color="getScoreColor(environmentalScore)" :stroke-width="8" />
          </div>
          <div class="breakdown-item">
            <div class="breakdown-header">
              <span class="breakdown-name">Social (S)</span>
              <span class="breakdown-score">{{ socialScore }}</span>
            </div>
            <el-progress :percentage="socialScore" :color="getScoreColor(socialScore)" :stroke-width="8" />
          </div>
          <div class="breakdown-item">
            <div class="breakdown-header">
              <span class="breakdown-name">Governance (G)</span>
              <span class="breakdown-score">{{ governanceScore }}</span>
            </div>
            <el-progress :percentage="governanceScore" :color="getScoreColor(governanceScore)" :stroke-width="8" />
          </div>
        </div>
      </div>
      <div class="score-rating">
        <div class="rating-badge" :class="getRatingClass()">
          {{ getRatingLabel() }}
        </div>
        <div class="rating-comparison">
          <span>Industry Average: {{ industryAverage }}</span>
          <span :class="overallScore >= industryAverage ? 'text-success' : 'text-danger'">
            {{ overallScore >= industryAverage ? 'Above Average' : 'Below Average' }}
          </span>
        </div>
      </div>
    </div>

    <!-- ESG Score Trend Chart -->
    <div class="chart-card">
      <div class="card-header">
        <h3>ESG Score Trend</h3>
        <el-radio-group v-model="trendPeriod" size="small" @change="fetchTrendData">
          <el-radio-button label="quarter">Quarterly</el-radio-button>
          <el-radio-button label="year">Yearly</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-container" ref="trendChartRef"></div>
    </div>

    <!-- ESG Pillar Details -->
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
            <span class="metric-label">Energy Efficiency</span>
            <span class="metric-value">85%</span>
            <span class="metric-trend positive">+5%</span>
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
            <span class="metric-label">Waste Recycling</span>
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
            <span class="metric-label">Employee Satisfaction</span>
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

    <!-- ESG Ratings Comparison Table -->
    <div class="table-card">
      <div class="card-header">
        <h3>ESG Ratings Comparison</h3>
        <el-input
            v-model="searchText"
            placeholder="Search by metric..."
            :prefix-icon="Search"
            style="width: 240px"
            clearable
        />
      </div>
      <el-table :data="paginatedMetrics" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="category" label="Category" width="140">
          <template #default="{ row }">
            <el-tag :type="getCategoryTagType(row.category)" size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="metric" label="Metric" min-width="200" show-overflow-tooltip />
        <el-table-column prop="ourScore" label="Our Score" width="120" align="center" sortable>
          <template #default="{ row }">
            <span class="score-value-cell">{{ row.ourScore }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="industryAvg" label="Industry Avg" width="120" align="center" sortable>
          <template #default="{ row }">
            {{ row.industryAvg }}
          </template>
        </el-table-column>
        <el-table-column prop="peerBest" label="Peer Best" width="120" align="center" sortable>
          <template #default="{ row }">
            {{ row.peerBest }}
          </template>
        </el-table-column>
        <el-table-column prop="gap" label="Gap to Best" width="120" align="center" sortable>
          <template #default="{ row }">
            <span :class="row.gap <= 0 ? 'text-success' : 'text-warning'">
              {{ row.gap > 0 ? '+' : '' }}{{ row.gap }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Performance" width="100">
          <template #default="{ row }">
            <el-tag :type="getPerformanceTagType(row.ourScore, row.industryAvg)" size="small" effect="dark">
              {{ getPerformanceLabel(row.ourScore, row.industryAvg) }}
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

    <!-- Improvement Recommendations -->
    <div class="recommendations-section">
      <div class="section-header">
        <h2>
          <el-icon><TrendCharts /></el-icon>
          Improvement Recommendations
        </h2>
        <el-button link type="primary" @click="viewAllRecommendations">View All →</el-button>
      </div>
      <div class="recommendations-list">
        <div v-for="rec in recommendations" :key="rec.id" class="recommendation-item">
          <div class="rec-icon" :class="rec.priority">
            <el-icon><Check /></el-icon>
          </div>
          <div class="rec-content">
            <div class="rec-title">{{ rec.title }}</div>
            <div class="rec-description">{{ rec.description }}</div>
            <div class="rec-metrics">
              <span><el-icon><TrendCharts /></el-icon> Impact: +{{ rec.impact }} points</span>
              <span><el-icon><Timer /></el-icon> Timeline: {{ rec.timeline }}</span>
            </div>
          </div>
          <div class="rec-actions">
            <el-button size="small" type="primary" plain @click="viewRecommendation(rec)">Details</el-button>
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
  TrendCharts,
  Search,
  Timer,
  Check,
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
interface ESGMonthlyMetric {
  id: number
  category: string
  metric: string
  ourScore: number
  industryAvg: number
  peerBest: number
  gap: number
}

interface Recommendation {
  id: number
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
  impact: number
  timeline: string
}

// ==================== State ====================
const dateRange = ref<[Date, Date] | null>(null)
const trendPeriod = ref<'quarter' | 'year'>('quarter')
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const trendChartRef = ref<HTMLElement | null>(null)
let trendChart: echarts.ECharts | null = null

// ==================== Mock Data ====================
const esgMetrics = ref<ESGMonthlyMetric[]>([
  { id: 1, category: 'Environmental', metric: 'Carbon Emissions Reduction', ourScore: 72, industryAvg: 68, peerBest: 85, gap: -13 },
  { id: 2, category: 'Environmental', metric: 'Renewable Energy Usage', ourScore: 65, industryAvg: 58, peerBest: 80, gap: -15 },
  { id: 3, category: 'Environmental', metric: 'Water Efficiency', ourScore: 78, industryAvg: 70, peerBest: 88, gap: -10 },
  { id: 4, category: 'Environmental', metric: 'Waste Management', ourScore: 82, industryAvg: 72, peerBest: 90, gap: -8 },
  { id: 5, category: 'Social', metric: 'Employee Satisfaction', ourScore: 84, industryAvg: 75, peerBest: 92, gap: -8 },
  { id: 6, category: 'Social', metric: 'Health & Safety', ourScore: 88, industryAvg: 80, peerBest: 95, gap: -7 },
  { id: 7, category: 'Social', metric: 'Diversity & Inclusion', ourScore: 76, industryAvg: 70, peerBest: 88, gap: -12 },
  { id: 8, category: 'Social', metric: 'Training & Development', ourScore: 80, industryAvg: 72, peerBest: 90, gap: -10 },
  { id: 9, category: 'Governance', metric: 'Board Independence', ourScore: 75, industryAvg: 68, peerBest: 85, gap: -10 },
  { id: 10, category: 'Governance', metric: 'Ethics Compliance', ourScore: 92, industryAvg: 85, peerBest: 98, gap: -6 },
  { id: 11, category: 'Governance', metric: 'Risk Management', ourScore: 82, industryAvg: 74, peerBest: 90, gap: -8 },
  { id: 12, category: 'Governance', metric: 'Data Privacy', ourScore: 90, industryAvg: 82, peerBest: 95, gap: -5 }
])

const recommendations = ref<Recommendation[]>([
  { id: 1, title: 'Increase Renewable Energy Procurement', description: 'Sign additional PPA agreements to increase renewable energy share to 50% by 2026.', priority: 'high', impact: 8, timeline: '12 months' },
  { id: 2, title: 'Enhance Diversity Recruitment', description: 'Implement targeted recruitment programs to increase diversity ratio to 50%.', priority: 'high', impact: 6, timeline: '6 months' },
  { id: 3, title: 'Expand ESG Reporting', description: 'Adopt TCFD recommendations and enhance disclosure quality.', priority: 'medium', impact: 4, timeline: '8 months' },
  { id: 4, title: 'Supply Chain ESG Audit', description: 'Expand supplier ESG audit coverage to 95% of spend.', priority: 'medium', impact: 5, timeline: '10 months' }
])

// ==================== Computed Values ====================
const overallScore = computed(() => 78)
const environmentalScore = computed(() => 74)
const socialScore = computed(() => 82)
const governanceScore = computed(() => 80)
const industryAverage = computed(() => 73)

const filteredMetrics = computed(() => {
  let result = [...esgMetrics.value]
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(m =>
        m.metric.toLowerCase().includes(search) ||
        m.category.toLowerCase().includes(search)
    )
  }
  if (dateRange.value && dateRange.value[0] && dateRange.value[1]) {
    // Filter logic if needed
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

const getCategoryTagType = (category: string) => {
  const map: Record<string, string> = {
    Environmental: 'success',
    Social: 'primary',
    Governance: 'warning'
  }
  return map[category] || 'info'
}

const getPerformanceTagType = (ourScore: number, industryAvg: number) => {
  if (ourScore >= industryAvg + 5) return 'success'
  if (ourScore >= industryAvg) return 'primary'
  if (ourScore >= industryAvg - 5) return 'warning'
  return 'danger'
}

const getPerformanceLabel = (ourScore: number, industryAvg: number) => {
  if (ourScore >= industryAvg + 5) return 'Leader'
  if (ourScore >= industryAvg) return 'Above Avg'
  if (ourScore >= industryAvg - 5) return 'Average'
  return 'Below Avg'
}

const dateShortcuts = [
  { text: 'Last 4 Quarters', value: () => { const end = new Date(); const start = new Date(); start.setMonth(start.getMonth() - 12); return [start, end] } },
  { text: 'Year to Date', value: () => { const end = new Date(); const start = new Date(); start.setMonth(0, 1); return [start, end] } },
  { text: 'Last Year', value: () => { const end = new Date(); const start = new Date(); start.setFullYear(start.getFullYear() - 1); return [start, end] } }
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
  ElMessage.success('ESG score data refreshed')
  initTrendChart()
  tableLoading.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting ESG score report...')
}

const fetchTrendData = () => {
  initTrendChart()
}

const handleDateChange = () => {
  currentPage.value = 1
}

const viewAllRecommendations = () => {
  ElMessage.info('Viewing all recommendations')
}

const viewRecommendation = (rec: Recommendation) => {
  ElMessage.info(`Viewing recommendation: ${rec.title}`)
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
.esg-score-page {
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
}

.breakdown-score {
  font-size: 18px;
  font-weight: 700;
  color: #1f2f3d;
}

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
  gap: 16px;
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
.score-value-cell {
  font-weight: 600;
  font-size: 16px;
  color: #1f2f3d;
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

/* Recommendations Section */
.recommendations-section {
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

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recommendation-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 14px;
  transition: all 0.2s;
}

.recommendation-item:hover {
  background: #f5f7fa;
  transform: translateX(4px);
}

.rec-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rec-icon.high {
  background: #ffe8e8;
  color: #f56c6c;
}

.rec-icon.medium {
  background: #fff7e8;
  color: #e6a23c;
}

.rec-icon.low {
  background: #e8f8f0;
  color: #67c23a;
}

.rec-content {
  flex: 1;
}

.rec-title {
  font-weight: 600;
  color: #1f2f3d;
  margin-bottom: 6px;
}

.rec-description {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.rec-metrics {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #909399;
}

.rec-metrics .el-icon {
  vertical-align: middle;
  margin-right: 4px;
}

.rec-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.recommendation-item:hover .rec-actions {
  opacity: 1;
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