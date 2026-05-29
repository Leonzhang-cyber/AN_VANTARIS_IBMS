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

  <!-- Customer Satisfaction Page Content -->
  <div v-else class="customer-satisfaction-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>Customer Satisfaction</h1>
        <p class="subtitle">Monitor feedback, satisfaction scores, and service quality metrics</p>
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

    <!-- KPI Summary Cards -->
    <div class="kpi-cards">
      <div class="kpi-card overall">
        <div class="kpi-icon">
          <el-icon :size="32"><StarFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ overallScore }}<span class="unit">/5.0</span></div>
          <div class="kpi-label">Overall Satisfaction</div>
        </div>
        <div class="kpi-trend" :class="scoreTrend >= 0 ? 'positive' : 'negative'">
          <el-icon><CaretTop v-if="scoreTrend >= 0" /><CaretBottom v-else /></el-icon>
          {{ Math.abs(scoreTrend) }}%
        </div>
      </div>
      <div class="kpi-card responses">
        <div class="kpi-icon">
          <el-icon :size="32"><ChatDotRound /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ totalResponses }}</div>
          <div class="kpi-label">Total Responses</div>
        </div>
        <div class="kpi-sub">This period</div>
      </div>
      <div class="kpi-card response-rate">
        <div class="kpi-icon">
          <el-icon :size="32"><DataLine /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ responseRate }}%</div>
          <div class="kpi-label">Response Rate</div>
        </div>
        <el-progress :percentage="responseRate" :color="getScoreColor(responseRate)" :stroke-width="8" style="margin-top: 8px" />
      </div>
      <div class="kpi-card nps">
        <div class="kpi-icon">
          <el-icon :size="32"><TrendCharts /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ npsScore }}</div>
          <div class="kpi-label">NPS Score</div>
        </div>
        <div class="kpi-sub">Promoters: {{ promoters }}%</div>
      </div>
    </div>

    <!-- Satisfaction Trend Chart -->
    <div class="chart-card">
      <div class="card-header">
        <h3>Satisfaction Trend</h3>
        <el-radio-group v-model="trendPeriod" size="small" @change="fetchTrendData">
          <el-radio-button label="week">Last 7 Days</el-radio-button>
          <el-radio-button label="month">Last 30 Days</el-radio-button>
          <el-radio-button label="quarter">Last 90 Days</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-container" ref="trendChartRef"></div>
    </div>

    <!-- Satisfaction by Category -->
    <div class="two-columns">
      <div class="chart-card">
        <div class="card-header">
          <h3>Satisfaction by Service Category</h3>
        </div>
        <div class="chart-container" ref="categoryChartRef"></div>
      </div>
      <div class="chart-card">
        <div class="card-header">
          <h3>Rating Distribution</h3>
        </div>
        <div class="chart-container" ref="ratingChartRef"></div>
      </div>
    </div>

    <!-- Customer Feedback Table -->
    <div class="table-card">
      <div class="card-header">
        <h3>Customer Feedback</h3>
        <div class="header-filters">
          <el-select v-model="ratingFilter" placeholder="All Ratings" clearable size="default" style="width: 130px">
            <el-option label="All Ratings" value="all" />
            <el-option label="5 Stars" value="5" />
            <el-option label="4 Stars" value="4" />
            <el-option label="3 Stars" value="3" />
            <el-option label="2 Stars" value="2" />
            <el-option label="1 Star" value="1" />
          </el-select>
          <el-select v-model="categoryFeedbackFilter" placeholder="All Categories" clearable size="default" style="width: 140px">
            <el-option label="All Categories" value="all" />
            <el-option label="HVAC" value="HVAC" />
            <el-option label="Cleaning" value="Cleaning" />
            <el-option label="Maintenance" value="Maintenance" />
            <el-option label="Security" value="Security" />
            <el-option label="Front Desk" value="Front Desk" />
          </el-select>
          <el-input
              v-model="searchText"
              placeholder="Search feedback..."
              :prefix-icon="Search"
              style="width: 200px"
              clearable
          />
        </div>
      </div>
      <el-table :data="paginatedFeedback" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="rating" label="Rating" width="120">
          <template #default="{ row }">
            <div class="rating-stars">
              <el-rate v-model="row.rating" disabled :allow-half="true" :colors="['#f56c6c', '#e6a23c', '#67c23a']" />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="Category" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="feedback" label="Feedback" min-width="250" show-overflow-tooltip />
        <el-table-column prop="customer" label="Customer" width="140" />
        <el-table-column prop="date" label="Date" width="110" sortable />
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewFeedback(row)">View</el-button>
            <el-button link type="success" size="small" @click="respondFeedback(row)">Respond</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredFeedback.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Sentiment Analysis -->
    <div class="sentiment-section">
      <div class="section-header">
        <h2>
          <el-icon><DataAnalysis /></el-icon>
          Sentiment Analysis
        </h2>
        <el-button link type="primary" @click="viewSentimentDetails">View Details →</el-button>
      </div>
      <div class="sentiment-grid">
        <div class="sentiment-card positive">
          <div class="sentiment-icon">
            <el-icon><CircleCheckFilled /></el-icon>
          </div>
          <div class="sentiment-info">
            <div class="sentiment-value">{{ positiveSentiment }}%</div>
            <div class="sentiment-label">Positive</div>
          </div>
        </div>
        <div class="sentiment-card neutral">
          <div class="sentiment-icon">
            <el-icon><Remove /></el-icon>
          </div>
          <div class="sentiment-info">
            <div class="sentiment-value">{{ neutralSentiment }}%</div>
            <div class="sentiment-label">Neutral</div>
          </div>
        </div>
        <div class="sentiment-card negative">
          <div class="sentiment-icon">
            <el-icon><WarningFilled /></el-icon>
          </div>
          <div class="sentiment-info">
            <div class="sentiment-value">{{ negativeSentiment }}%</div>
            <div class="sentiment-label">Negative</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Common Keywords -->
    <div class="keywords-section">
      <div class="section-header">
        <h2>
          <el-icon><Collection /></el-icon>
          Common Keywords in Feedback
        </h2>
      </div>
      <div class="keywords-cloud">
        <span v-for="keyword in keywords" :key="keyword.word" class="keyword-tag" :class="`size-${keyword.size}`">
          {{ keyword.word }} ({{ keyword.count }})
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Refresh,
  Download,
  StarFilled,
  ChatDotRound,
  DataLine,
  TrendCharts,
  Search,
  DataAnalysis,
  CircleCheckFilled,
  Remove,
  WarningFilled,
  Collection,
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
interface FeedbackItem {
  id: number
  rating: number
  category: string
  feedback: string
  customer: string
  date: string
  status: 'new' | 'responded' | 'resolved'
}

interface Keyword {
  word: string
  count: number
  size: number
}

// ==================== State ====================
const dateRange = ref<[Date, Date] | null>(null)
const trendPeriod = ref<'week' | 'month' | 'quarter'>('month')
const ratingFilter = ref('all')
const categoryFeedbackFilter = ref('all')
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const trendChartRef = ref<HTMLElement | null>(null)
const categoryChartRef = ref<HTMLElement | null>(null)
const ratingChartRef = ref<HTMLElement | null>(null)
let trendChart: echarts.ECharts | null = null
let categoryChart: echarts.ECharts | null = null
let ratingChart: echarts.ECharts | null = null

// ==================== Mock Data ====================
const feedbackItems = ref<FeedbackItem[]>([
  { id: 1, rating: 5, category: 'HVAC', feedback: 'The air conditioning is working perfectly now! Great response time.', customer: 'John Smith', date: '2025-05-28', status: 'responded' },
  { id: 2, rating: 4, category: 'Cleaning', feedback: 'Common areas are clean, but restrooms need more frequent checks.', customer: 'Sarah Chen', date: '2025-05-27', status: 'responded' },
  { id: 3, rating: 2, category: 'Maintenance', feedback: 'Elevator was out for 3 days, very inconvenient for our team.', customer: 'Mike Johnson', date: '2025-05-27', status: 'new' },
  { id: 4, rating: 5, category: 'Security', feedback: 'Security staff are very professional and helpful.', customer: 'Lisa Wong', date: '2025-05-26', status: 'resolved' },
  { id: 5, rating: 3, category: 'HVAC', feedback: 'Temperature fluctuates during afternoon hours.', customer: 'Tom Davis', date: '2025-05-26', status: 'responded' },
  { id: 6, rating: 5, category: 'Front Desk', feedback: 'Front desk team always greets with a smile. Excellent service!', customer: 'Anna Lee', date: '2025-05-25', status: 'resolved' },
  { id: 7, rating: 4, category: 'Cleaning', feedback: 'Carpet cleaning could be improved in high-traffic areas.', customer: 'David Kim', date: '2025-05-25', status: 'responded' },
  { id: 8, rating: 1, category: 'Maintenance', feedback: 'Reported leak two days ago, still not fixed.', customer: 'Maria Garcia', date: '2025-05-24', status: 'new' },
  { id: 9, rating: 4, category: 'Security', feedback: 'Access card system works well, but parking gates are slow.', customer: 'James Wilson', date: '2025-05-24', status: 'responded' },
  { id: 10, rating: 5, category: 'HVAC', feedback: 'Quick resolution of our heating issue. Thank you!', customer: 'Emily Brown', date: '2025-05-23', status: 'resolved' },
  { id: 11, rating: 3, category: 'Cleaning', feedback: 'Trash removal could be more frequent.', customer: 'Robert Taylor', date: '2025-05-23', status: 'new' },
  { id: 12, rating: 4, category: 'Front Desk', feedback: 'Very helpful with visitor registration process.', customer: 'Patricia Martin', date: '2025-05-22', status: 'responded' }
])

const keywords = ref<Keyword[]>([
  { word: 'excellent', count: 24, size: 5 },
  { word: 'response time', count: 18, size: 4 },
  { word: 'cleaning', count: 15, size: 4 },
  { word: 'temperature', count: 12, size: 3 },
  { word: 'professional', count: 11, size: 3 },
  { word: 'maintenance', count: 10, size: 3 },
  { word: 'helpful', count: 9, size: 2 },
  { word: 'elevator', count: 8, size: 2 },
  { word: 'security', count: 8, size: 2 },
  { word: 'leak', count: 7, size: 2 },
  { word: 'parking', count: 6, size: 1 },
  { word: 'friendly', count: 6, size: 1 }
])

// ==================== Computed Values ====================
const overallScore = computed(() => 4.2)
const totalResponses = computed(() => 156)
const responseRate = computed(() => 68)
const npsScore = computed(() => 42)
const promoters = computed(() => 52)
const scoreTrend = computed(() => 3.8)

const positiveSentiment = computed(() => 62)
const neutralSentiment = computed(() => 24)
const negativeSentiment = computed(() => 14)

const filteredFeedback = computed(() => {
  let result = [...feedbackItems.value]
  if (ratingFilter.value !== 'all') {
    result = result.filter(f => f.rating === parseInt(ratingFilter.value))
  }
  if (categoryFeedbackFilter.value !== 'all') {
    result = result.filter(f => f.category === categoryFeedbackFilter.value)
  }
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(f =>
        f.feedback.toLowerCase().includes(search) ||
        f.customer.toLowerCase().includes(search)
    )
  }
  if (dateRange.value && dateRange.value[0] && dateRange.value[1]) {
    const [start, end] = dateRange.value
    result = result.filter(f => {
      const date = new Date(f.date)
      return date >= start && date <= end
    })
  }
  return result
})

const paginatedFeedback = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredFeedback.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getScoreColor = (score: number) => {
  if (score >= 75) return '#67c23a'
  if (score >= 60) return '#409eff'
  if (score >= 50) return '#e6a23c'
  return '#f56c6c'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    new: 'New',
    responded: 'Responded',
    resolved: 'Resolved'
  }
  return map[status] || status
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    new: 'danger',
    responded: 'warning',
    resolved: 'success'
  }
  return map[status] || 'info'
}

const dateShortcuts = [
  { text: 'Last 7 Days', value: () => { const end = new Date(); const start = new Date(); start.setDate(start.getDate() - 7); return [start, end] } },
  { text: 'Last 30 Days', value: () => { const end = new Date(); const start = new Date(); start.setDate(start.getDate() - 30); return [start, end] } },
  { text: 'This Month', value: () => { const end = new Date(); const start = new Date(); start.setDate(1); return [start, end] } }
]

// ==================== Chart Functions ====================
const generateTrendData = () => {
  if (trendPeriod.value === 'week') {
    return {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      scores: [4.1, 4.2, 4.3, 4.1, 4.4, 4.2, 4.0],
      target: [4.2, 4.2, 4.2, 4.2, 4.2, 4.2, 4.2]
    }
  }
  if (trendPeriod.value === 'month') {
    const days = Array.from({ length: 30 }, (_, i) => `${i + 1}`)
    const scores = days.map(() => Number((3.8 + Math.random() * 0.8).toFixed(1)))
    const target = days.map(() => 4.2)
    return { labels: days, scores, target }
  }
  return {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    scores: [3.9, 4.0, 4.1, 4.2, 4.2, 4.3],
    target: [4.0, 4.1, 4.1, 4.2, 4.2, 4.3]
  }
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)
  const data = generateTrendData()

  trendChart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: (value: number) => value + ' / 5.0' },
    legend: { data: ['Satisfaction Score', 'Target (4.2)'], bottom: 0 },
    grid: { left: '3%', right: '4%', top: '10%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', data: data.labels, axisLabel: { rotate: trendPeriod.value === 'month' ? 45 : 0, interval: trendPeriod.value === 'month' ? 5 : 0 } },
    yAxis: { type: 'value', name: 'Rating (out of 5)', min: 3, max: 5 },
    series: [
      { name: 'Satisfaction Score', type: 'line', data: data.scores, smooth: true, symbol: 'circle', lineStyle: { width: 3, color: '#409eff' }, areaStyle: { opacity: 0.1, color: '#409eff' } },
      { name: 'Target (4.2)', type: 'line', data: data.target, smooth: false, symbol: 'none', lineStyle: { width: 2, color: '#f56c6c', type: 'dashed' } }
    ]
  })
}

const initCategoryChart = () => {
  if (!categoryChartRef.value) return
  if (categoryChart) categoryChart.dispose()

  categoryChart = echarts.init(categoryChartRef.value)

  const categories = ['HVAC', 'Cleaning', 'Maintenance', 'Security', 'Front Desk']
  const scores = [4.5, 3.8, 3.5, 4.2, 4.8]
  const target = [4.2, 4.2, 4.2, 4.2, 4.2]

  categoryChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: (value: number) => value + ' / 5.0' },
    legend: { data: ['Current Score', 'Target'], bottom: 0 },
    grid: { left: '10%', right: '5%', top: '5%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: categories },
    yAxis: { type: 'value', name: 'Rating (out of 5)', min: 3, max: 5 },
    series: [
      { name: 'Current Score', type: 'bar', data: scores, itemStyle: { borderRadius: [4, 4, 0, 0], color: (params: any) => params.data >= 4.2 ? '#67c23a' : params.data >= 3.8 ? '#e6a23c' : '#f56c6c' }, label: { show: true, position: 'top', formatter: '{c}' } },
      { name: 'Target', type: 'line', data: target, symbol: 'none', lineStyle: { width: 2, color: '#409eff', type: 'dashed' } }
    ]
  })
}

const initRatingChart = () => {
  if (!ratingChartRef.value) return
  if (ratingChart) ratingChart.dispose()

  ratingChart = echarts.init(ratingChartRef.value)

  ratingChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} responses ({d}%)' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      type: 'pie', radius: '55%', center: ['50%', '50%'],
      data: [
        { name: '5 Stars', value: 48, itemStyle: { color: '#67c23a' } },
        { name: '4 Stars', value: 42, itemStyle: { color: '#409eff' } },
        { name: '3 Stars', value: 28, itemStyle: { color: '#e6a23c' } },
        { name: '2 Stars', value: 22, itemStyle: { color: '#f56c6c' } },
        { name: '1 Star', value: 16, itemStyle: { color: '#f56c6c' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 }
    }]
  })
}

// ==================== Actions ====================
const refreshData = async () => {
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  ElMessage.success('Customer satisfaction data refreshed')
  initTrendChart()
  initCategoryChart()
  initRatingChart()
  tableLoading.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting customer satisfaction report...')
}

const fetchTrendData = () => {
  initTrendChart()
}

const handleDateChange = () => {
  currentPage.value = 1
}

const viewFeedback = (row: FeedbackItem) => {
  ElMessage.info(`Viewing feedback #${row.id}`)
}

const respondFeedback = (row: FeedbackItem) => {
  ElMessage.info(`Responding to feedback #${row.id}`)
}

const viewSentimentDetails = () => {
  ElMessage.info('Viewing sentiment analysis details')
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Window Resize Handler ====================
const handleResize = () => {
  trendChart?.resize()
  categoryChart?.resize()
  ratingChart?.resize()
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
        initCategoryChart()
        initRatingChart()
      }, 100)
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  categoryChart?.dispose()
  ratingChart?.dispose()
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
.customer-satisfaction-page {
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

/* KPI Cards */
.kpi-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.kpi-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s, box-shadow 0.2s;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.kpi-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.kpi-card.overall .kpi-icon { background: #fff7e8; color: #e6a23c; }
.kpi-card.responses .kpi-icon { background: #e8f4ff; color: #409eff; }
.kpi-card.response-rate .kpi-icon { background: #e8f8f0; color: #67c23a; }
.kpi-card.nps .kpi-icon { background: #f0e8ff; color: #8b5cf6; }

.kpi-info {
  flex: 1;
}

.kpi-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
  line-height: 1.2;
}

.kpi-value .unit {
  font-size: 14px;
  font-weight: 400;
  color: #909399;
}

.kpi-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.kpi-sub {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 2px;
}

.kpi-trend {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 13px;
  font-weight: 500;
}

.kpi-trend.positive { color: #67c23a; }
.kpi-trend.negative { color: #f56c6c; }

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

.header-filters {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.chart-container {
  height: 320px;
  width: 100%;
}

.two-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

/* Table Styles */
.rating-stars {
  display: flex;
  align-items: center;
}

:deep(.el-rate) {
  height: auto;
}

.pagination-wrapper {
  padding: 20px 0 0;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
  margin-top: 16px;
}

/* Sentiment Section */
.sentiment-section {
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  margin-bottom: 24px;
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

.sentiment-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.sentiment-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: 14px;
}

.sentiment-card.positive {
  background: linear-gradient(135deg, #e8f8f0 0%, #d4edda 100%);
}

.sentiment-card.neutral {
  background: linear-gradient(135deg, #e8f4ff 0%, #cce5ff 100%);
}

.sentiment-card.negative {
  background: linear-gradient(135deg, #ffe8e8 0%, #f8d7da 100%);
}

.sentiment-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.8);
  font-size: 28px;
}

.sentiment-card.positive .sentiment-icon { color: #67c23a; }
.sentiment-card.neutral .sentiment-icon { color: #409eff; }
.sentiment-card.negative .sentiment-icon { color: #f56c6c; }

.sentiment-info {
  flex: 1;
}

.sentiment-value {
  font-size: 32px;
  font-weight: 700;
  color: #1f2f3d;
}

.sentiment-label {
  font-size: 13px;
  color: #606266;
  margin-top: 4px;
}

/* Keywords Section */
.keywords-section {
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.keywords-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  justify-content: center;
  min-height: 150px;
}

.keyword-tag {
  padding: 6px 14px;
  border-radius: 30px;
  background: #f5f7fa;
  color: #606266;
  transition: all 0.2s;
  cursor: default;
}

.keyword-tag:hover {
  background: #409eff;
  color: white;
  transform: scale(1.05);
}

.keyword-tag.size-1 { font-size: 12px; }
.keyword-tag.size-2 { font-size: 14px; }
.keyword-tag.size-3 { font-size: 16px; font-weight: 500; }
.keyword-tag.size-4 { font-size: 18px; font-weight: 600; }
.keyword-tag.size-5 { font-size: 22px; font-weight: 700; }

:deep(.el-table) {
  border-radius: 12px;
}

:deep(.el-table th.el-table__cell) {
  background-color: #fafafa;
  font-weight: 600;
  color: #1f2f3d;
}
</style>