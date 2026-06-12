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
  Sunny, Lightning, Timer, Wallet, WindPower
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing carbon optimization engine...',
  'Analyzing emission patterns...',
  'Calculating reduction strategies...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const selectedYear = ref('2024')
const detailsVisible = ref(false)
const chartRef = ref(null)
const breakdownChartRef = ref(null)

let emissionChart: echarts.ECharts | null = null
let breakdownChart: echarts.ECharts | null = null

// Year options
const yearOptions = ['2024', '2023', '2022', '2021']

// Carbon emission data
const emissionData = ref({
  monthlyData: [
    { month: 'Jan', emissions: 185, target: 195, offset: 12 },
    { month: 'Feb', emissions: 178, target: 190, offset: 10 },
    { month: 'Mar', emissions: 192, target: 200, offset: 15 },
    { month: 'Apr', emissions: 175, target: 185, offset: 14 },
    { month: 'May', emissions: 168, target: 180, offset: 18 },
    { month: 'Jun', emissions: 172, target: 185, offset: 16 },
    { month: 'Jul', emissions: 185, target: 195, offset: 20 },
    { month: 'Aug', emissions: 190, target: 200, offset: 22 },
    { month: 'Sep', emissions: 165, target: 178, offset: 18 },
    { month: 'Oct', emissions: 158, target: 175, offset: 15 },
    { month: 'Nov', emissions: 152, target: 170, offset: 14 },
    { month: 'Dec', emissions: 148, target: 168, offset: 12 }
  ],
  breakdown: [
    { source: 'HVAC', emissions: 425, percentage: 34, reduction: 45 },
    { source: 'Lighting', emissions: 312, percentage: 25, reduction: 38 },
    { source: 'Equipment', emissions: 268, percentage: 21, reduction: 22 },
    { source: 'Transportation', emissions: 156, percentage: 12, reduction: 15 },
    { source: 'Other', emissions: 99, percentage: 8, reduction: 8 }
  ],
  recommendations: [
    { id: 1, title: 'HVAC Efficiency Upgrade', description: 'Upgrade to high-efficiency HVAC systems with VFD controls', reduction: 125, cost: 45000, roi: '24 months', priority: 'high' },
    { id: 2, title: 'LED Lighting Retrofit', description: 'Replace all fluorescent lighting with LED fixtures', reduction: 85, cost: 28000, roi: '18 months', priority: 'high' },
    { id: 3, title: 'Solar Panel Installation', description: 'Install rooftop solar PV system for renewable energy', reduction: 180, cost: 120000, roi: '48 months', priority: 'medium' },
    { id: 4, title: 'Energy Management System', description: 'Implement AI-based energy optimization system', reduction: 65, cost: 35000, roi: '30 months', priority: 'medium' },
    { id: 5, title: 'Electric Vehicle Fleet', description: 'Transition fleet to electric vehicles', reduction: 95, cost: 250000, roi: '60 months', priority: 'low' }
  ]
})

// Carbon optimization statistics
const carbonStats = reactive({
  totalEmissions: 2168,
  totalOffset: 186,
  netEmissions: 1982,
  reductionTarget: 15,
  currentReduction: 12.5,
  carbonCredits: 245,
  renewablePercentage: 32,
  treesEquivalent: 32450
})

// Renewable energy mix
const renewableMix = ref([
  { source: 'Solar', percentage: 45, color: '#E6A23C' },
  { source: 'Wind', percentage: 30, color: '#67C23A' },
  { source: 'Hydro', percentage: 15, color: '#409EFF' },
  { source: 'Biomass', percentage: 10, color: '#9B59B6' }
])

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 5,
  total: emissionData.value.recommendations.length
})

const paginatedRecommendations = computed(() => {
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return emissionData.value.recommendations.slice(start, end)
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

  emissionChart = echarts.init(chartRef.value)
  emissionChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Emissions (tCO₂e)', 'Target', 'Carbon Offset'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: emissionData.value.monthlyData.map(d => d.month) },
    yAxis: { type: 'value', name: 'tCO₂e' },
    series: [
      { name: 'Emissions (tCO₂e)', type: 'line', data: emissionData.value.monthlyData.map(d => d.emissions), smooth: true, lineStyle: { color: '#F56C6C', width: 3 }, areaStyle: { opacity: 0.1, color: '#F56C6C' }, symbol: 'circle', symbolSize: 8 },
      { name: 'Target', type: 'line', data: emissionData.value.monthlyData.map(d => d.target), smooth: true, lineStyle: { color: '#909399', width: 2, type: 'dashed' }, symbol: 'diamond', symbolSize: 6 },
      { name: 'Carbon Offset', type: 'bar', data: emissionData.value.monthlyData.map(d => d.offset), itemStyle: { color: '#67C23A', borderRadius: [4, 4, 0, 0] } }
    ]
  })
}

const initBreakdownChart = () => {
  if (!breakdownChartRef.value) return

  breakdownChart = echarts.init(breakdownChartRef.value)
  breakdownChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} tCO₂e)' },
    legend: { orient: 'vertical', left: 'left', data: emissionData.value.breakdown.map(b => b.source) },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: emissionData.value.breakdown.map(b => ({ name: b.source, value: b.emissions })),
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: {d}%' },
      itemStyle: {
        color: (params: any) => {
          const colors = ['#F56C6C', '#E6A23C', '#409EFF', '#67C23A', '#9B59B6']
          return colors[params.dataIndex % colors.length]
        }
      }
    }]
  })
}

const handleResize = () => {
  emissionChart?.resize()
  breakdownChart?.resize()
}

// ==================== Carbon Functions ====================
const refreshData = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  loading.value = false
  ElMessage.success('Carbon data refreshed successfully')
}

const applyRecommendation = async (rec: any) => {
  await ElMessageBox.confirm(
      `Apply carbon reduction recommendation: ${rec.title}?`,
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
          <span class="loading-title">Loading Carbon Optimization</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Energy Optimization - Carbon Optimization</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="carbon-optimization-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Carbon Optimization</h1>
        <p class="page-subtitle">Reduce carbon footprint and achieve sustainability goals</p>
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
        <div class="stat-icon emissions-icon">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ carbonStats.totalEmissions }} t</div>
          <div class="stat-label">Total CO₂e Emissions</div>
        </div>
        <div class="stat-trend">
          <span class="trend-down">{{ carbonStats.reductionTarget }}% reduction target</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon offset-icon">
          <el-icon><WindPower /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ carbonStats.totalOffset }} t</div>
          <div class="stat-label">Carbon Offset</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ carbonStats.carbonCredits }} credits earned</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon renewable-icon">
          <el-icon><Sunny /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ carbonStats.renewablePercentage }}%</div>
          <div class="stat-label">Renewable Energy</div>
        </div>
        <div class="stat-trend">
          <el-progress :percentage="carbonStats.renewablePercentage" :stroke-width="4" :show-text="false" />
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon trees-icon">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ (carbonStats.treesEquivalent / 1000).toFixed(0) }}K</div>
          <div class="stat-label">Trees Equivalent</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+12% this year</span>
        </div>
      </div>
    </div>

    <!-- Carbon Progress -->
    <div class="progress-section">
      <div class="section-header">
        <h3>Carbon Reduction Progress</h3>
        <span class="progress-target">Target: {{ carbonStats.reductionTarget }}% by 2025</span>
      </div>
      <div class="progress-container">
        <div class="progress-bar-large">
          <div class="progress-fill" :style="{ width: (carbonStats.currentReduction / carbonStats.reductionTarget) * 100 + '%' }"></div>
        </div>
        <div class="progress-stats">
          <span>Current: {{ carbonStats.currentReduction }}% reduction</span>
          <span>Target: {{ carbonStats.reductionTarget }}% reduction</span>
          <span>Remaining: {{ (carbonStats.reductionTarget - carbonStats.currentReduction).toFixed(1) }}% to goal</span>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-row">
      <div class="chart-section">
        <div class="section-header">
          <h3>Monthly Emissions vs Target</h3>
          <el-button text type="primary" @click="initChart">Refresh</el-button>
        </div>
        <div ref="chartRef" class="emission-chart" style="height: 320px"></div>
      </div>

      <div class="chart-section">
        <div class="section-header">
          <h3>Emissions Breakdown by Source</h3>
          <el-button text type="primary" @click="initBreakdownChart">Refresh</el-button>
        </div>
        <div ref="breakdownChartRef" class="breakdown-chart" style="height: 320px"></div>
      </div>
    </div>

    <!-- Renewable Energy Mix -->
    <div class="renewable-section">
      <div class="section-header">
        <h3>Renewable Energy Mix</h3>
      </div>
      <div class="renewable-grid">
        <div
            v-for="source in renewableMix"
            :key="source.source"
            class="renewable-card"
        >
          <div class="renewable-icon" :style="{ background: source.color + '20', color: source.color }">
            {{ source.source === 'Solar' ? '☀️' : source.source === 'Wind' ? '💨' : source.source === 'Hydro' ? '💧' : '🌿' }}
          </div>
          <div class="renewable-info">
            <h4>{{ source.source }}</h4>
            <p>{{ source.percentage }}% of total</p>
          </div>
          <div class="renewable-bar">
            <div class="bar-fill" :style="{ width: source.percentage + '%', background: source.color }"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Reduction Recommendations -->
    <div class="recommendations-section">
      <div class="section-header">
        <h3>Carbon Reduction Recommendations</h3>
        <el-tag type="info" size="small">Total potential reduction: {{ emissionData.recommendations.reduce((sum, r) => sum + r.reduction, 0) }} tCO₂e/year</el-tag>
      </div>

      <div class="recommendations-grid">
        <div
            v-for="rec in paginatedRecommendations"
            :key="rec.id"
            class="recommendation-card"
        >
          <div class="rec-header">
            <div class="rec-title">
              <span class="rec-icon">🌱</span>
              <h4>{{ rec.title }}</h4>
            </div>
            <div class="rec-badges">
              <span class="priority-badge" :style="{ background: getPriorityColor(rec.priority) }">
                {{ rec.priority.toUpperCase() }}
              </span>
              <span class="roi-badge">
                ROI: {{ rec.roi }}
              </span>
            </div>
          </div>
          <p class="rec-description">{{ rec.description }}</p>
          <div class="rec-footer">
            <div class="reduction">
              <span class="reduction-label">CO₂ Reduction:</span>
              <span class="reduction-value">{{ rec.reduction }} t/year</span>
            </div>
            <div class="cost">
              <span class="cost-label">Investment:</span>
              <span class="cost-value">${{ (rec.cost / 1000).toFixed(0) }}K</span>
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

    <!-- Source Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="selectedSource?.source" width="500px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="CO₂ Emissions">{{ selectedSource?.emissions }} tCO₂e</el-descriptions-item>
        <el-descriptions-item label="Percentage">{{ selectedSource?.percentage }}%</el-descriptions-item>
        <el-descriptions-item label="Current Reduction">{{ selectedSource?.reduction }} tCO₂e</el-descriptions-item>
        <el-descriptions-item label="Reduction Potential">{{ Math.round(selectedSource?.reduction * 1.5) }} tCO₂e</el-descriptions-item>
      </el-descriptions>
      <div class="recommendation-note">
        <el-alert
            title="Optimization Opportunity"
            type="success"
            show-icon
            :closable="false"
        >
          <template #default>
            <p>Upgrading {{ selectedSource?.source?.toLowerCase() }} systems could reduce emissions by an additional {{ Math.round(selectedSource?.reduction * 0.5) }} tCO₂e annually.</p>
          </template>
        </el-alert>
      </div>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
        <el-button type="primary">View Recommendations</el-button>
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
.carbon-optimization-container {
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

.emissions-icon {
  background: linear-gradient(135deg, #fef0f0 0%, #fcd9d9 100%);
  color: #f56c6c;
}

.offset-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.renewable-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.trees-icon {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #409eff;
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

/* Progress Section */
.progress-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.progress-container {
  margin-top: 16px;
}

.progress-bar-large {
  height: 12px;
  background: #e4e7ed;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 12px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #67c23a, #409eff);
  border-radius: 6px;
  transition: width 0.3s ease;
}

.progress-stats {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #606266;
}

.progress-target {
  font-size: 13px;
  color: #909399;
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

.emission-chart,
.breakdown-chart {
  width: 100%;
}

/* Renewable Section */
.renewable-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.renewable-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
  margin-top: 16px;
}

.renewable-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #fafbfc;
  border-radius: 16px;
  transition: all 0.2s ease;
}

.renewable-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.renewable-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.renewable-info {
  flex: 1;
}

.renewable-info h4 {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: #1e293b;
}

.renewable-info p {
  font-size: 12px;
  color: #909399;
  margin: 0;
}

.renewable-bar {
  width: 100px;
  height: 6px;
  background: #e4e7ed;
  border-radius: 3px;
  overflow: hidden;
}

.renewable-bar .bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

/* Recommendations Section */
.recommendations-section {
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

.roi-badge {
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

.reduction {
  display: flex;
  gap: 6px;
  font-size: 12px;
}

.reduction-label {
  color: #909399;
}

.reduction-value {
  font-weight: 600;
  color: #67c23a;
}

.cost {
  display: flex;
  gap: 6px;
  font-size: 12px;
}

.cost-label {
  color: #909399;
}

.cost-value {
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

  .charts-row {
    grid-template-columns: 1fr;
  }

  .recommendations-grid {
    grid-template-columns: 1fr;
  }

  .progress-stats {
    flex-direction: column;
    gap: 4px;
  }
}

@media (max-width: 768px) {
  .carbon-optimization-container {
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

  .renewable-grid {
    grid-template-columns: 1fr;
  }

  .rec-footer {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>