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

  <!-- Sustainability Summary Page Content -->
  <div v-else class="sustainability-summary-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>Sustainability Summary</h1>
        <p class="subtitle">Track environmental impact, carbon reduction progress, and sustainability goal achievement</p>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="refreshData">Refresh</el-button>
        <el-button type="primary" :icon="Download" @click="exportReport">Export Report</el-button>
        <el-select v-model="yearFilter" placeholder="Select Year" size="default" style="width: 120px">
          <el-option label="2025" value="2025" />
          <el-option label="2024" value="2024" />
          <el-option label="2023" value="2023" />
        </el-select>
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="kpi-cards">
      <div class="kpi-card carbon">
        <div class="kpi-icon">
          <el-icon :size="32"><Cloudy /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ totalCarbon }}<span class="unit"> tCO₂e</span></div>
          <div class="kpi-label">Total Carbon Emissions</div>
        </div>
        <div class="kpi-trend positive">
          <el-icon><CaretBottom /></el-icon>
          {{ carbonReduction }}%
        </div>
      </div>
      <div class="kpi-card energy">
        <div class="kpi-icon">
          <el-icon :size="32"><Lightning /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ renewablePercentage }}%</div>
          <div class="kpi-label">Renewable Energy</div>
        </div>
        <div class="kpi-trend positive">
          <el-icon><CaretTop /></el-icon>
          +{{ renewableGrowth }}%
        </div>
      </div>
      <div class="kpi-card water">
        <div class="kpi-icon">
          <el-icon :size="32"><Flag /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ waterSaved }}<span class="unit"> m³</span></div>
          <div class="kpi-label">Water Saved</div>
        </div>
        <div class="kpi-trend positive">
          <el-icon><CaretBottom /></el-icon>
          {{ waterReduction }}%
        </div>
      </div>
      <div class="kpi-card waste">
        <div class="kpi-icon">
          <el-icon :size="32"><Delete /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ wasteDiversion }}%</div>
          <div class="kpi-label">Waste Diversion Rate</div>
        </div>
        <el-progress :percentage="wasteDiversion" :color="getProgressColor(wasteDiversion)" :stroke-width="8" style="margin-top: 8px" />
      </div>
    </div>

    <!-- Carbon Emissions Breakdown -->
    <div class="two-columns">
      <div class="chart-card">
        <div class="card-header">
          <h3>Carbon Emissions by Scope</h3>
        </div>
        <div class="chart-container" ref="scopeChartRef"></div>
      </div>
      <div class="chart-card">
        <div class="card-header">
          <h3>Emissions by Category</h3>
        </div>
        <div class="chart-container" ref="categoryChartRef"></div>
      </div>
    </div>

    <!-- Annual Carbon Trend -->
    <div class="chart-card">
      <div class="card-header">
        <h3>Annual Carbon Emissions Trend</h3>
        <el-radio-group v-model="trendPeriod" size="small" @change="fetchTrendData">
          <el-radio-button label="year">Yearly</el-radio-button>
          <el-radio-button label="quarter">Quarterly</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-container" ref="trendChartRef"></div>
    </div>

    <!-- Sustainability Metrics Table -->
    <div class="table-card">
      <div class="card-header">
        <h3>Sustainability Performance Metrics</h3>
        <el-input
            v-model="searchText"
            placeholder="Search metrics..."
            :prefix-icon="Search"
            style="width: 240px"
            clearable
        />
      </div>
      <el-table :data="paginatedMetrics" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="metric" label="Metric" min-width="200" show-overflow-tooltip />
        <el-table-column prop="value" label="Current Value" width="140" align="center" sortable />
        <el-table-column prop="baseline" label="Baseline (2023)" width="140" align="center" sortable />
        <el-table-column prop="target" label="2025 Target" width="140" align="center" sortable />
        <el-table-column prop="progress" label="Progress" width="180">
          <template #default="{ row }">
            <div class="progress-cell">
              <span class="progress-percent">{{ row.progress }}%</span>
              <el-progress :percentage="row.progress" :color="getProgressColor(row.progress)" :stroke-width="6" :show-text="false" style="flex: 1" />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
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

    <!-- Certifications & Recognitions -->
    <div class="certifications-section">
      <div class="section-header">
        <h2>
          <el-icon><Medal /></el-icon>
          Certifications & Recognitions
        </h2>
      </div>
      <div class="certifications-grid">
        <div v-for="cert in certifications" :key="cert.name" class="cert-card">
          <div class="cert-icon">
            <el-icon><CircleCheckFilled /></el-icon>
          </div>
          <div class="cert-info">
            <div class="cert-name">{{ cert.name }}</div>
            <div class="cert-date">Achieved: {{ cert.date }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Sustainability Goals -->
    <div class="goals-section">
      <div class="section-header">
        <h2>
          <el-icon><Aim /></el-icon>
          Sustainability Goals (2030)
        </h2>
      </div>
      <div class="goals-grid">
        <div v-for="goal in sustainabilityGoals" :key="goal.name" class="goal-card">
          <div class="goal-header">
            <span class="goal-name">{{ goal.name }}</span>
            <span class="goal-target">{{ goal.target }}</span>
          </div>
          <div class="goal-progress">
            <el-progress :percentage="goal.progress" :color="getProgressColor(goal.progress)" :stroke-width="10" :format="(p) => p + '%'" />
          </div>
          <div class="goal-status" :class="getGoalStatusClass(goal.progress)">
            {{ getGoalStatus(goal.progress) }}
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
  Cloudy,
  Lightning,
  Flag,
  Delete,
  Search,
  Medal,
  CircleCheckFilled,
  Aim,
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
interface SustainabilityMetric {
  id: number
  metric: string
  value: string
  baseline: string
  target: string
  progress: number
}

interface Certification {
  name: string
  date: string
}

interface SustainabilityGoal {
  name: string
  target: string
  progress: number
}

// ==================== State ====================
const yearFilter = ref('2025')
const trendPeriod = ref<'year' | 'quarter'>('year')
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const scopeChartRef = ref<HTMLElement | null>(null)
const categoryChartRef = ref<HTMLElement | null>(null)
const trendChartRef = ref<HTMLElement | null>(null)
let scopeChart: echarts.ECharts | null = null
let categoryChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null

// ==================== Mock Data ====================
const totalCarbon = ref(12500)
const carbonReduction = ref(12.5)
const renewablePercentage = ref(42)
const renewableGrowth = ref(8)
const waterSaved = ref(45000)
const waterReduction = ref(15.2)
const wasteDiversion = ref(68)

const sustainabilityMetrics = ref<SustainabilityMetric[]>([
  { id: 1, metric: 'Carbon Emissions (tCO₂e)', value: '12,500', baseline: '15,200', target: '10,000', progress: 68 },
  { id: 2, metric: 'Energy Intensity (kWh/m²)', value: '42.5', baseline: '48.2', target: '38.0', progress: 72 },
  { id: 3, metric: 'Renewable Energy Share (%)', value: '42%', baseline: '28%', target: '60%', progress: 70 },
  { id: 4, metric: 'Water Intensity (m³/m²)', value: '0.85', baseline: '1.05', target: '0.70', progress: 71 },
  { id: 5, metric: 'Waste Diversion Rate (%)', value: '68%', baseline: '55%', target: '75%', progress: 81 },
  { id: 6, metric: 'Sustainable Procurement (%)', value: '45%', baseline: '30%', target: '70%', progress: 64 },
  { id: 7, metric: 'Green Building Certifications', value: '4', baseline: '2', target: '8', progress: 50 },
  { id: 8, metric: 'EV Charging Stations', value: '25', baseline: '10', target: '50', progress: 50 }
])

const certifications = ref<Certification[]>([
  { name: 'ISO 14001:2015', date: '2024-03-15' },
  { name: 'LEED Platinum', date: '2024-01-20' },
  { name: 'Energy Star Certified', date: '2023-11-10' },
  { name: 'WELL Health-Safety Rating', date: '2024-06-01' },
  { name: 'CDP B Rating', date: '2024-02-28' }
])

const sustainabilityGoals = ref<SustainabilityGoal[]>([
  { name: 'Net Zero Emissions', target: '2030', progress: 42 },
  { name: '100% Renewable Energy', target: '2030', progress: 42 },
  { name: 'Zero Waste to Landfill', target: '2030', progress: 55 },
  { name: 'Water Neutral', target: '2030', progress: 35 }
])

// ==================== Computed Values ====================
const filteredMetrics = computed(() => {
  let result = [...sustainabilityMetrics.value]
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(m => m.metric.toLowerCase().includes(search))
  }
  return result
})

const paginatedMetrics = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredMetrics.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getProgressColor = (percentage: number) => {
  if (percentage >= 90) return '#67c23a'
  if (percentage >= 70) return '#409eff'
  if (percentage >= 50) return '#e6a23c'
  return '#f56c6c'
}

const getGoalStatusClass = (progress: number) => {
  if (progress >= 75) return 'status-good'
  if (progress >= 50) return 'status-warning'
  return 'status-poor'
}

const getGoalStatus = (progress: number) => {
  if (progress >= 75) return 'On Track'
  if (progress >= 50) return 'In Progress'
  return 'Behind Schedule'
}

// ==================== Chart Functions ====================
const initScopeChart = () => {
  if (!scopeChartRef.value) return
  if (scopeChart) scopeChart.dispose()

  scopeChart = echarts.init(scopeChartRef.value)

  scopeChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} tCO₂e ({d}%)' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      type: 'pie', radius: '55%', center: ['50%', '50%'],
      data: [
        { name: 'Scope 1 (Direct)', value: 2850, itemStyle: { color: '#f56c6c' } },
        { name: 'Scope 2 (Energy)', value: 5200, itemStyle: { color: '#e6a23c' } },
        { name: 'Scope 3 (Indirect)', value: 4450, itemStyle: { color: '#409eff' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 }
    }]
  })
}

const initCategoryChart = () => {
  if (!categoryChartRef.value) return
  if (categoryChart) categoryChart.dispose()

  categoryChart = echarts.init(categoryChartRef.value)

  categoryChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: (value: number) => value + ' tCO₂e' },
    grid: { left: '15%', right: '5%', top: '5%', bottom: '5%', containLabel: true },
    xAxis: { type: 'value', name: 'Emissions (tCO₂e)' },
    yAxis: { type: 'category', data: ['Electricity', 'Natural Gas', 'Transportation', 'Waste', 'Business Travel', 'Purchased Goods'] },
    series: [{
      type: 'bar', data: [4850, 1200, 1850, 450, 680, 1620],
      itemStyle: { borderRadius: [0, 4, 4, 0], color: '#409eff' },
      label: { show: true, position: 'right' }
    }]
  })
}

const generateTrendData = () => {
  if (trendPeriod.value === 'year') {
    return {
      labels: ['2021', '2022', '2023', '2024', '2025'],
      emissions: [15800, 15200, 14500, 13500, 12500],
      target: [15800, 15200, 14500, 13500, 12000]
    }
  }
  return {
    labels: ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024', 'Q1 2025'],
    emissions: [3450, 3380, 3320, 3250, 3100],
    target: [3500, 3400, 3350, 3300, 3200]
  }
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)
  const data = generateTrendData()

  trendChart.setOption({
    tooltip: { trigger: 'axis', valueFormatter: (value: number) => value + ' tCO₂e' },
    legend: { data: ['Actual Emissions', 'Target Trajectory'], bottom: 0 },
    grid: { left: '3%', right: '4%', top: '10%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', data: data.labels },
    yAxis: { type: 'value', name: 'Carbon Emissions (tCO₂e)' },
    series: [
      { name: 'Actual Emissions', type: 'line', data: data.emissions, smooth: true, symbol: 'circle', lineStyle: { width: 3, color: '#409eff' }, areaStyle: { opacity: 0.1, color: '#409eff' } },
      { name: 'Target Trajectory', type: 'line', data: data.target, smooth: true, symbol: 'diamond', lineStyle: { width: 2, color: '#f56c6c', type: 'dashed' } }
    ]
  })
}

// ==================== Actions ====================
const refreshData = async () => {
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  ElMessage.success('Sustainability data refreshed')
  initScopeChart()
  initCategoryChart()
  initTrendChart()
  tableLoading.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting sustainability report...')
}

const fetchTrendData = () => {
  initTrendChart()
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Window Resize Handler ====================
const handleResize = () => {
  scopeChart?.resize()
  categoryChart?.resize()
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
        initScopeChart()
        initCategoryChart()
        initTrendChart()
      }, 100)
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  scopeChart?.dispose()
  categoryChart?.dispose()
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
.sustainability-summary-page {
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

.kpi-card.carbon .kpi-icon { background: #e8f4ff; color: #409eff; }
.kpi-card.energy .kpi-icon { background: #e8f8f0; color: #67c23a; }
.kpi-card.water .kpi-icon { background: #e8f0ff; color: #8b5cf6; }
.kpi-card.waste .kpi-icon { background: #fff7e8; color: #e6a23c; }

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

.pagination-wrapper {
  padding: 20px 0 0;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
  margin-top: 16px;
}

/* Certifications Section */
.certifications-section {
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

.certifications-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.cert-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #fafafa;
  border-radius: 12px;
}

.cert-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e8f8f0;
  color: #67c23a;
  font-size: 20px;
}

.cert-info {
  flex: 1;
}

.cert-name {
  font-weight: 600;
  color: #1f2f3d;
  margin-bottom: 4px;
}

.cert-date {
  font-size: 11px;
  color: #909399;
}

/* Goals Section */
.goals-section {
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.goals-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.goal-card {
  background: #fafafa;
  border-radius: 14px;
  padding: 16px;
}

.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 12px;
}

.goal-name {
  font-weight: 600;
  color: #1f2f3d;
  font-size: 15px;
}

.goal-target {
  font-size: 12px;
  color: #909399;
}

.goal-status {
  margin-top: 12px;
  font-size: 12px;
  font-weight: 500;
  text-align: center;
}

.goal-status.status-good { color: #67c23a; }
.goal-status.status-warning { color: #e6a23c; }
.goal-status.status-poor { color: #f56c6c; }

:deep(.el-table) {
  border-radius: 12px;
}

:deep(.el-table th.el-table__cell) {
  background-color: #fafafa;
  font-weight: 600;
  color: #1f2f3d;
}
</style>