<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Refresh, Setting, User, Clock,
  Warning, CircleCheck, TrendCharts, DataLine,
  Star, Share, CopyDocument, Delete, Mic,
  Picture, Document, Upload, Download,
  MagicStick, ChatDotRound, Message, Service,
  Search, Edit, Plus, VideoPlay, VideoPause,
  Operation, Headset, Monitor, Cpu, Connection,
  Sunny, Lightning, Timer, Wallet, Money
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing cost optimization engine...',
  'Analyzing utility tariffs...',
  'Calculating savings opportunities...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const selectedUtility = ref('all')
const detailsVisible = ref(false)
const chartRef = ref(null)
const costChartRef = ref(null)

let costChart: echarts.ECharts | null = null
let breakdownChart: echarts.ECharts | null = null

// Utility type options
const utilityOptions = [
  { value: 'all', label: 'All Utilities' },
  { value: 'electricity', label: 'Electricity' },
  { value: 'water', label: 'Water' },
  { value: 'gas', label: 'Natural Gas' }
]

// Utility cost data
const costData = ref({
  monthlyData: [
    { month: 'Jan', electricity: 2850, water: 450, gas: 320, optimized: 2450 },
    { month: 'Feb', electricity: 2780, water: 440, gas: 310, optimized: 2400 },
    { month: 'Mar', electricity: 2920, water: 460, gas: 340, optimized: 2520 },
    { month: 'Apr', electricity: 2750, water: 430, gas: 300, optimized: 2350 },
    { month: 'May', electricity: 2680, water: 420, gas: 280, optimized: 2280 },
    { month: 'Jun', electricity: 2850, water: 450, gas: 290, optimized: 2450 },
    { month: 'Jul', electricity: 3120, water: 480, gas: 310, optimized: 2680 },
    { month: 'Aug', electricity: 3250, water: 490, gas: 320, optimized: 2800 },
    { month: 'Sep', electricity: 2980, water: 460, gas: 290, optimized: 2550 },
    { month: 'Oct', electricity: 2820, water: 440, gas: 270, optimized: 2420 },
    { month: 'Nov', electricity: 2750, water: 430, gas: 260, optimized: 2350 },
    { month: 'Dec', electricity: 2950, water: 460, gas: 290, optimized: 2550 }
  ],
  breakdown: [
    { source: 'Electricity', cost: 34500, percentage: 68, saving: 4250 },
    { source: 'Water', cost: 5400, percentage: 11, saving: 850 },
    { source: 'Natural Gas', cost: 3600, percentage: 7, saving: 520 },
    { source: 'Demand Charges', cost: 5200, percentage: 10, saving: 1200 },
    { source: 'Other Fees', cost: 2000, percentage: 4, saving: 300 }
  ],
  recommendations: [
    { id: 1, title: 'Peak Demand Reduction', description: 'Shift non-critical loads to off-peak hours', savings: 2850, cost: 5000, payback: '21 months', priority: 'high' },
    { id: 2, title: 'Power Factor Correction', description: 'Install capacitors to improve power factor', savings: 1850, cost: 8000, payback: '52 months', priority: 'medium' },
    { id: 3, title: 'Time-of-Use Optimization', description: 'Optimize schedules for TOU rates', savings: 2250, cost: 2000, payback: '11 months', priority: 'high' },
    { id: 4, title: 'Leak Detection & Repair', description: 'Fix water leaks and optimize usage', savings: 850, cost: 1500, payback: '21 months', priority: 'medium' },
    { id: 5, title: 'Energy Storage Integration', description: 'Install battery storage for peak shaving', savings: 4200, cost: 50000, payback: '143 months', priority: 'low' }
  ]
})

// Cost optimization statistics
const costStats = reactive({
  totalCost: 50700,
  optimizedCost: 41200,
  totalSavings: 9500,
  savingsPercentage: 18.7,
  peakDemand: 450,
  averageRate: 0.125,
  roi: 24
})

// Tariff rates
const tariffRates = ref([
  { period: 'Off-Peak (10pm - 6am)', rate: 0.08, usage: 35 },
  { period: 'Mid-Peak (6am - 2pm)', rate: 0.12, usage: 40 },
  { period: 'Peak (2pm - 10pm)', rate: 0.18, usage: 25 }
])

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 5,
  total: costData.value.recommendations.length
})

const paginatedRecommendations = computed(() => {
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return costData.value.recommendations.slice(start, end)
})

// ==================== Loading Simulation ====================
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
        initBreakdownChart()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  costChart = echarts.init(chartRef.value)
  costChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Electricity', 'Water', 'Natural Gas', 'Optimized Cost'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: costData.value.monthlyData.map(d => d.month) },
    yAxis: { type: 'value', name: 'Cost ($)' },
    series: [
      { name: 'Electricity', type: 'bar', data: costData.value.monthlyData.map(d => d.electricity), stack: 'total', itemStyle: { color: '#F56C6C', borderRadius: [4, 4, 0, 0] } },
      { name: 'Water', type: 'bar', data: costData.value.monthlyData.map(d => d.water), stack: 'total', itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] } },
      { name: 'Natural Gas', type: 'bar', data: costData.value.monthlyData.map(d => d.gas), stack: 'total', itemStyle: { color: '#E6A23C', borderRadius: [4, 4, 0, 0] } },
      { name: 'Optimized Cost', type: 'line', data: costData.value.monthlyData.map(d => d.optimized), smooth: true, lineStyle: { color: '#67C23A', width: 2 }, symbol: 'circle', symbolSize: 8 }
    ]
  })
}

const initBreakdownChart = () => {
  if (!breakdownChartRef.value) return

  breakdownChart = echarts.init(breakdownChartRef.value)
  breakdownChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: ${c}K ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: costData.value.breakdown.map(b => b.source) },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: costData.value.breakdown.map(b => ({ name: b.source, value: Math.round(b.cost / 1000) })),
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: ${d}%' },
      itemStyle: {
        color: (params: any) => {
          const colors = ['#F56C6C', '#409EFF', '#E6A23C', '#67C23A', '#9B59B6']
          return colors[params.dataIndex % colors.length]
        }
      }
    }]
  })
}

const handleResize = () => {
  costChart?.resize()
  breakdownChart?.resize()
}

// ==================== Cost Functions ====================
const refreshData = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  loading.value = false
  ElMessage.success('Cost data refreshed successfully')
}

const applyRecommendation = async (rec: any) => {
  await ElMessageBox.confirm(
      `Apply cost optimization recommendation: ${rec.title}?`,
      'Confirm Apply',
      {
        confirmButtonText: 'Apply',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  )

  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))
  ElMessage.success(`Recommendation "${rec.title}" applied successfully`)
  loading.value = false
}

const viewDetails = (source: any) => {
  selectedSource.value = source
  detailsVisible.value = true
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'high': return '#F56C6C'
    case 'medium': return '#E6A23C'
    case 'low': return '#67C23A'
    default: return '#909399'
  }
}

const formatCurrency = (value: number) => {
  return `$${value.toLocaleString()}`
}

const selectedSource = ref<any>(null)
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
          <span class="loading-title">Loading Utility Cost Optimization</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Energy Optimization - Utility Cost Optimization</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="cost-optimization-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Utility Cost Optimization</h1>
        <p class="page-subtitle">Optimize utility costs through rate analysis and usage efficiency</p>
      </div>
      <div class="header-right">
        <el-button size="large" @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
        <el-button size="large">
          <el-icon><Setting /></el-icon>
          Settings
        </el-button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total-icon">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">${{ (costStats.totalCost / 1000).toFixed(0) }}K</div>
          <div class="stat-label">Annual Cost</div>
        </div>
        <div class="stat-trend">
          <span class="trend-down">-${{ (costStats.totalSavings / 1000).toFixed(0) }}K potential</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon savings-icon">
          <el-icon><Wallet /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">${{ (costStats.totalSavings / 1000).toFixed(0) }}K</div>
          <div class="stat-label">Potential Savings</div>
        </div>
        <div class="stat-trend">
          <el-progress :percentage="costStats.savingsPercentage" :stroke-width="4" :show-text="false" />
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon demand-icon">
          <el-icon><Lightning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ costStats.peakDemand }} kW</div>
          <div class="stat-label">Peak Demand</div>
        </div>
        <div class="stat-trend">
          <span class="trend-down">-12% from peak</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon rate-icon">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">${{ costStats.averageRate }}/kWh</div>
          <div class="stat-label">Avg Electricity Rate</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ costStats.roi }}% ROI expected</span>
        </div>
      </div>
    </div>

    <!-- Tariff Rate Section -->
    <div class="tariff-section">
      <div class="section-header">
        <h3>Time-of-Use Tariff Rates</h3>
      </div>
      <div class="tariff-grid">
        <div
            v-for="tariff in tariffRates"
            :key="tariff.period"
            class="tariff-card"
        >
          <div class="tariff-period">{{ tariff.period }}</div>
          <div class="tariff-rate">${{ tariff.rate }}/kWh</div>
          <div class="tariff-usage">
            <span class="usage-label">Current Usage:</span>
            <span class="usage-value">{{ tariff.usage }}%</span>
          </div>
          <el-progress :percentage="tariff.usage" :stroke-width="6" :color="tariff.rate > 0.15 ? '#F56C6C' : '#67C23A'" />
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-row">
      <div class="chart-section">
        <div class="section-header">
          <h3>Monthly Utility Cost Breakdown</h3>
          <el-button text type="primary" @click="initChart">Refresh</el-button>
        </div>
        <div ref="chartRef" class="cost-chart" style="height: 320px"></div>
      </div>

      <div class="chart-section">
        <div class="section-header">
          <h3>Cost Breakdown by Category</h3>
          <el-button text type="primary" @click="initBreakdownChart">Refresh</el-button>
        </div>
        <div ref="breakdownChartRef" class="breakdown-chart" style="height: 320px"></div>
      </div>
    </div>

    <!-- Savings Opportunities -->
    <div class="savings-section">
      <div class="section-header">
        <h3>Cost Saving Opportunities</h3>
        <el-tag type="info" size="small">Total potential savings: ${{ costData.recommendations.reduce((sum, r) => sum + r.savings, 0).toLocaleString() }}/year</el-tag>
      </div>

      <div class="recommendations-grid">
        <div
            v-for="rec in paginatedRecommendations"
            :key="rec.id"
            class="recommendation-card"
        >
          <div class="rec-header">
            <div class="rec-title">
              <span class="rec-icon">💰</span>
              <h4>{{ rec.title }}</h4>
            </div>
            <div class="rec-badges">
              <span class="priority-badge" :style="{ background: getPriorityColor(rec.priority) }">
                {{ rec.priority.toUpperCase() }}
              </span>
              <span class="payback-badge">
                Payback: {{ rec.payback }}
              </span>
            </div>
          </div>
          <p class="rec-description">{{ rec.description }}</p>
          <div class="rec-footer">
            <div class="savings">
              <span class="savings-label">Annual Savings:</span>
              <span class="savings-value">${{ rec.savings.toLocaleString() }}</span>
            </div>
            <div class="investment">
              <span class="investment-label">Investment:</span>
              <span class="investment-value">${{ rec.cost.toLocaleString() }}</span>
            </div>
            <el-button type="primary" size="small" @click="applyRecommendation(rec)">Apply</el-button>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[5, 10, 15]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- Cost Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="selectedSource?.source" width="500px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Annual Cost">${{ (selectedSource?.cost / 1000).toFixed(1) }}K</el-descriptions-item>
        <el-descriptions-item label="Percentage">{{ selectedSource?.percentage }}%</el-descriptions-item>
        <el-descriptions-item label="Current Savings">${{ selectedSource?.saving?.toLocaleString() }}</el-descriptions-item>
        <el-descriptions-item label="Optimization Potential">${{ Math.round(selectedSource?.saving * 0.5).toLocaleString() }}</el-descriptions-item>
      </el-descriptions>
      <div class="recommendation-note">
        <el-alert
            title="Optimization Opportunity"
            type="success"
            show-icon
            :closable="false"
        >
          <template #default>
            <p>Implementing demand response and efficiency measures could reduce {{ selectedSource?.source }} costs by an additional {{ Math.round((selectedSource?.saving * 0.3) / 1000) }}K annually.</p>
          </template>
        </el-alert>
      </div>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
        <el-button type="primary">View Detailed Analysis</el-button>
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
.cost-optimization-container {
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

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.total-icon {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #409eff;
}

.savings-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.demand-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.rate-icon {
  background: linear-gradient(135deg, #fef0f0 0%, #fcd9d9 100%);
  color: #f56c6c;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  margin-top: 4px;
}

.stat-trend {
  position: absolute;
  top: 16px;
  right: 16px;
  font-size: 11px;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 20px;
}

.trend-up {
  color: #67c23a;
}

.trend-down {
  color: #f56c6c;
}

/* Tariff Section */
.tariff-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.tariff-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-top: 16px;
}

.tariff-card {
  background: #fafbfc;
  border-radius: 16px;
  padding: 16px;
  text-align: center;
  transition: all 0.2s ease;
}

.tariff-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.tariff-period {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.tariff-rate {
  font-size: 24px;
  font-weight: 700;
  color: #409eff;
  margin-bottom: 12px;
}

.tariff-usage {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  margin-bottom: 8px;
}

.usage-label {
  color: #909399;
}

.usage-value {
  font-weight: 600;
  color: #1e293b;
}

/* Charts Row */
.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.chart-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.cost-chart,
.breakdown-chart {
  width: 100%;
}

/* Savings Section */
.savings-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.recommendation-card {
  background: #fafbfc;
  border-radius: 16px;
  padding: 16px;
  transition: all 0.2s ease;
}

.recommendation-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.rec-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 8px;
}

.rec-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rec-icon {
  font-size: 18px;
}

.rec-title h4 {
  font-size: 15px;
  font-weight: 600;
  margin: 0;
  color: #1e293b;
}

.rec-badges {
  display: flex;
  gap: 8px;
}

.priority-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 600;
  color: white;
}

.payback-badge {
  padding: 4px 8px;
  background: #e4e7ed;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 500;
  color: #606266;
}

.rec-description {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.rec-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.savings {
  display: flex;
  gap: 6px;
  font-size: 12px;
}

.savings-label {
  color: #909399;
}

.savings-value {
  font-weight: 600;
  color: #67c23a;
}

.investment {
  display: flex;
  gap: 6px;
  font-size: 12px;
}

.investment-label {
  color: #909399;
}

.investment-value {
  font-weight: 600;
  color: #1e293b;
}

/* Pagination */
.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

/* Dialog */
.recommendation-note {
  margin-top: 16px;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .tariff-grid {
    grid-template-columns: 1fr;
  }

  .charts-row {
    grid-template-columns: 1fr;
  }

  .recommendations-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .cost-optimization-container {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    text-align: center;
  }

  .header-right {
    width: 100%;
    justify-content: center;
  }

  .rec-footer {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>