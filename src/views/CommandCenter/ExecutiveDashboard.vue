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
        <div class="loading-tip">Executive Dashboard</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="executive-dashboard">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Command Center</el-breadcrumb-item>
            <el-breadcrumb-item>Executive Dashboard</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Executive Dashboard</h1>
        <p class="description">Strategic insights and key performance indicators for enterprise decision making</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
        <el-button type="primary" @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          Refresh Data
        </el-button>
      </div>
    </div>

    <!-- Time Range Selector -->
    <el-card class="time-range-card" shadow="hover">
      <div class="time-range-container">
        <span class="range-label">View:</span>
        <el-radio-group v-model="timeRange" @change="handleTimeRangeChange">
          <el-radio-button value="today">Today</el-radio-button>
          <el-radio-button value="week">This Week</el-radio-button>
          <el-radio-button value="month">This Month</el-radio-button>
          <el-radio-button value="quarter">This Quarter</el-radio-button>
          <el-radio-button value="year">This Year</el-radio-button>
        </el-radio-group>
        <el-date-picker
            v-model="customDateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start"
            end-placeholder="End"
            size="default"
            style="width: 260px; margin-left: auto"
            @change="handleCustomDateChange"
        />
      </div>
    </el-card>

    <!-- KPI Summary Cards -->
    <el-row :gutter="20" class="kpi-row">
      <el-col :xs="24" :sm="12" :lg="6" v-for="kpi in kpiCards" :key="kpi.title">
        <el-card class="kpi-card" shadow="hover" @click="handleKPIClick(kpi)">
          <div class="kpi-content">
            <div class="kpi-info">
              <div class="kpi-title">{{ kpi.title }}</div>
              <div class="kpi-value">{{ kpi.value }}</div>
              <div class="kpi-trend" :class="kpi.trend > 0 ? 'up' : 'down'">
                <el-icon><component :is="kpi.trend > 0 ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
                {{ Math.abs(kpi.trend) }}%
                <span class="trend-label">vs {{ timeRange }}</span>
              </div>
            </div>
            <div class="kpi-icon" :style="{ background: kpi.bgColor }">
              <el-icon :size="28" color="white">
                <component :is="kpi.icon" />
              </el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Main Charts Row -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :lg="16">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Revenue & Cost Trend</span>
              <el-radio-group v-model="trendPeriod" size="small">
                <el-radio-button value="monthly">Monthly</el-radio-button>
                <el-radio-button value="quarterly">Quarterly</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="revenueChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Portfolio Distribution</span>
            </div>
          </template>
          <div ref="portfolioChartRef" class="pie-chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Secondary Charts Row -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :lg="8">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Energy Efficiency</span>
            </div>
          </template>
          <div ref="energyChartRef" class="gauge-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Maintenance KPIs</span>
            </div>
          </template>
          <div ref="maintenanceChartRef" class="horizontal-bar-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Top Performing Sites</span>
              <el-button link type="primary" size="small" @click="viewAllSites">View All</el-button>
            </div>
          </template>
          <div ref="sitesChartRef" class="bar-chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Recent Decisions & Alerts -->
    <el-row :gutter="20" class="recent-row">
      <el-col :xs="24" :lg="12">
        <el-card class="recent-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Recent Decisions</span>
              <el-button link type="primary" size="small" @click="viewAllDecisions">View All</el-button>
            </div>
          </template>
          <el-table :data="recentDecisions" stripe style="width: 100%" size="small">
            <el-table-column prop="date" label="Date" width="100" />
            <el-table-column prop="title" label="Decision" min-width="180" show-overflow-tooltip />
            <el-table-column prop="type" label="Type" width="120">
              <template #default="{ row }">
                <el-tag :type="getDecisionTypeTag(row.type)" size="small">{{ row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusTag(row.status)" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card class="recent-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Critical Alerts</span>
              <el-button link type="primary" size="small" @click="viewAllAlerts">View All</el-button>
            </div>
          </template>
          <div class="alerts-list">
            <div v-for="alert in criticalAlerts" :key="alert.id" class="alert-item" :class="alert.severity.toLowerCase()">
              <div class="alert-icon">
                <el-icon><WarningFilled /></el-icon>
              </div>
              <div class="alert-content">
                <div class="alert-title">{{ alert.title }}</div>
                <div class="alert-description">{{ alert.description }}</div>
                <div class="alert-time">{{ alert.time }}</div>
              </div>
              <div class="alert-action">
                <el-button link type="primary" size="small" @click="viewAlert(alert)">View</el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Strategic Recommendations -->
    <el-card class="recommendations-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>AI Strategic Recommendations</span>
          <el-tag type="success" size="small">Powered by AI</el-tag>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="8" v-for="rec in recommendations" :key="rec.id">
          <div class="recommendation-item">
            <div class="rec-icon" :style="{ background: rec.color }">
              <el-icon :size="24"><component :is="rec.icon" /></el-icon>
            </div>
            <div class="rec-content">
              <div class="rec-title">{{ rec.title }}</div>
              <div class="rec-description">{{ rec.description }}</div>
              <div class="rec-impact">
                <span class="impact-label">Expected Impact:</span>
                <span class="impact-value" :style="{ color: rec.impactColor }">{{ rec.impact }}</span>
              </div>
              <el-button link type="primary" size="small" @click="viewRecommendation(rec)">Review →</el-button>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Download, Setting,
  WarningFilled, OfficeBuilding, DataAnalysis,
  Tickets, User, Cpu
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading executive data...',
  'Compiling KPIs...',
  'Almost ready...'
]

// ==================== Chart References ====================
const revenueChartRef = ref<HTMLElement>()
const portfolioChartRef = ref<HTMLElement>()
const energyChartRef = ref<HTMLElement>()
const maintenanceChartRef = ref<HTMLElement>()
const sitesChartRef = ref<HTMLElement>()

let revenueChart: echarts.ECharts | null = null
let portfolioChart: echarts.ECharts | null = null
let energyChart: echarts.ECharts | null = null
let maintenanceChart: echarts.ECharts | null = null
let sitesChart: echarts.ECharts | null = null

// ==================== State ====================
const timeRange = ref('month')
const customDateRange = ref<[Date, Date] | null>(null)
const trendPeriod = ref<'monthly' | 'quarterly'>('monthly')

// ==================== Mock Data ====================
const kpiCards = ref([
  {
    title: 'Total Revenue',
    value: '$12.4M',
    trend: 8.5,
    icon: 'DataAnalysis',
    bgColor: '#409eff',
    key: 'revenue'
  },
  {
    title: 'Cost Savings',
    value: '$2.1M',
    trend: 12.3,
    icon: 'TrendCharts',
    bgColor: '#67c23a',
    key: 'savings'
  },
  {
    title: 'Energy Efficiency',
    value: '87%',
    trend: 5.2,
    icon: 'DataAnalysis',
    bgColor: '#e6a23c',
    key: 'energy'
  },
  {
    title: 'Decisions Made',
    value: '284',
    trend: 15.8,
    icon: 'Document',
    bgColor: '#f56c6c',
    key: 'decisions'
  }
])

const recentDecisions = ref([
  { date: '2024-01-20', title: 'Chiller Overhaul Approval', type: 'Maintenance Decision', status: 'Approved' },
  { date: '2024-01-19', title: 'LED Retrofit Contract Signed', type: 'Energy Decision', status: 'Implemented' },
  { date: '2024-01-18', title: 'UPS Battery Replacement', type: 'Fault Decision', status: 'In Progress' },
  { date: '2024-01-17', title: 'ESG Compliance Report', type: 'ESG Decision', status: 'Approved' },
  { date: '2024-01-16', title: 'HVAC Optimization Algorithm', type: 'AI Recommendation', status: 'Under Review' }
])

const criticalAlerts = ref([
  {
    id: 1,
    severity: 'critical',
    title: 'Chiller-02 High Temperature Alert',
    description: 'Temperature exceeded threshold by 8°C. Immediate attention required.',
    time: '10 minutes ago'
  },
  {
    id: 2,
    severity: 'warning',
    title: 'UPS Battery Health Degrading',
    description: 'Battery capacity dropped to 65%. Schedule replacement within 30 days.',
    time: '1 hour ago'
  },
  {
    id: 3,
    severity: 'info',
    title: 'Monthly Maintenance Due',
    description: '12 assets require scheduled maintenance this week.',
    time: '3 hours ago'
  }
])

const recommendations = ref([
  {
    id: 1,
    title: 'Optimize HVAC Scheduling',
    description: 'AI analysis suggests 15% energy savings by adjusting setpoints based on occupancy patterns.',
    icon: 'DataAnalysis',
    color: '#409eff',
    impact: '$45,000 annual savings',
    impactColor: '#67c23a'
  },
  {
    id: 2,
    title: 'Expand Predictive Maintenance',
    description: 'Extend predictive maintenance to 20 additional assets to reduce downtime by 30%.',
    icon: 'Cpu',
    color: '#e6a23c',
    impact: '30% downtime reduction',
    impactColor: '#409eff'
  },
  {
    id: 3,
    title: 'Renewable Energy Integration',
    description: 'Solar panel installation could offset 25% of grid electricity consumption.',
    icon: 'TrendCharts',
    color: '#67c23a',
    impact: '250 tCO₂e reduction',
    impactColor: '#67c23a'
  }
])

// ==================== Helper Methods ====================
const getDecisionTypeTag = (type: string): string => {
  const map: Record<string, string> = {
    'Maintenance Decision': 'warning',
    'Energy Decision': 'success',
    'Fault Decision': 'danger',
    'ESG Decision': 'primary',
    'AI Recommendation': 'info'
  }
  return map[type] || 'info'
}

const getStatusTag = (status: string): string => {
  const map: Record<string, string> = {
    'Approved': 'success',
    'Implemented': 'success',
    'In Progress': 'warning',
    'Under Review': 'warning',
    'Rejected': 'danger'
  }
  return map[status] || 'info'
}

// ==================== Chart Initializations ====================
const initRevenueChart = () => {
  if (!revenueChartRef.value) return
  if (revenueChart) revenueChart.dispose()

  revenueChart = echarts.init(revenueChartRef.value)

  const monthlyRevenue = [8.2, 8.5, 8.9, 9.2, 9.5, 9.8, 10.2, 10.5, 10.8, 11.2, 11.5, 12.4]
  const monthlyCost = [6.5, 6.6, 6.7, 6.8, 6.9, 7.0, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6]
  const quarterlyRevenue = [25.6, 28.5, 31.2, 34.1]
  const quarterlyCost = [19.8, 20.5, 21.2, 22.0]

  const revenueData = trendPeriod.value === 'monthly' ? monthlyRevenue : quarterlyRevenue
  const costData = trendPeriod.value === 'monthly' ? monthlyCost : quarterlyCost
  const xAxisData = trendPeriod.value === 'monthly'
      ? ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      : ['Q1', 'Q2', 'Q3', 'Q4']

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Revenue ($M)', 'Cost ($M)'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: { type: 'value', name: 'Amount ($M)' },
    series: [
      { name: 'Revenue ($M)', type: 'line', data: revenueData, smooth: true, lineStyle: { width: 3, color: '#409eff' }, areaStyle: { opacity: 0.1 }, symbolSize: 8 },
      { name: 'Cost ($M)', type: 'line', data: costData, smooth: true, lineStyle: { width: 3, color: '#e6a23c' }, areaStyle: { opacity: 0.1 }, symbolSize: 8 }
    ]
  }

  revenueChart.setOption(option)
  window.addEventListener('resize', () => revenueChart?.resize())
}

const initPortfolioChart = () => {
  if (!portfolioChartRef.value) return
  if (portfolioChart) portfolioChart.dispose()

  portfolioChart = echarts.init(portfolioChartRef.value)

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: 35, name: 'Data Centers', itemStyle: { color: '#409eff' } },
        { value: 25, name: 'Commercial Buildings', itemStyle: { color: '#67c23a' } },
        { value: 20, name: 'Industrial Sites', itemStyle: { color: '#e6a23c' } },
        { value: 12, name: 'Retail Spaces', itemStyle: { color: '#f56c6c' } },
        { value: 8, name: 'Other', itemStyle: { color: '#909399' } }
      ],
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  }

  portfolioChart.setOption(option)
  window.addEventListener('resize', () => portfolioChart?.resize())
}

const initEnergyChart = () => {
  if (!energyChartRef.value) return
  if (energyChart) energyChart.dispose()

  energyChart = echarts.init(energyChartRef.value)

  const option: echarts.EChartsOption = {
    tooltip: { formatter: '{b}: {c}%' },
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
      axisLine: { lineStyle: { width: 18, color: [[0.87, '#67c23a'], [1, '#e6e9f0']] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      pointer: { show: false },
      detail: { show: true, offsetCenter: [0, 20], valueAnimation: true, fontSize: 24, fontWeight: 'bold', color: '#303133' },
      title: { show: true, offsetCenter: [0, -20], fontSize: 14, color: '#909399' },
      data: [{ value: 87, name: 'Efficiency' }]
    }]
  }

  energyChart.setOption(option)
  window.addEventListener('resize', () => energyChart?.resize())
}

const initMaintenanceChart = () => {
  if (!maintenanceChartRef.value) return
  if (maintenanceChart) maintenanceChart.dispose()

  maintenanceChart = echarts.init(maintenanceChartRef.value)

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '15%', containLabel: true },
    xAxis: { type: 'value', name: 'Days', max: 10 },
    yAxis: { type: 'category', data: ['MTTR', 'MTBF', 'Response Time'], axisLabel: { fontSize: 12 } },
    series: [{
      type: 'bar',
      data: [3.2, 8.5, 2.4],
      itemStyle: {
        borderRadius: [0, 4, 4, 0],
        color: '#409eff'
      },
      label: { show: true, position: 'right' }
    }]
  }

  maintenanceChart.setOption(option)
  window.addEventListener('resize', () => maintenanceChart?.resize())
}

const initSitesChart = () => {
  if (!sitesChartRef.value) return
  if (sitesChart) sitesChart.dispose()

  sitesChart = echarts.init(sitesChartRef.value)

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '10%', containLabel: true },
    xAxis: { type: 'category', data: ['Site A', 'Site B', 'Site C', 'Site D', 'Site E'], axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'Performance Score' },
    series: [{
      type: 'bar',
      data: [94, 89, 85, 82, 78],
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: '#67c23a'
      },
      label: { show: true, position: 'top' }
    }]
  }

  sitesChart.setOption(option)
  window.addEventListener('resize', () => sitesChart?.resize())
}

// ==================== Interactive Methods ====================
const handleExport = () => {
  ElMessage.success('Executive report export started...')
}

const handleRefresh = () => {
  ElMessage.success('Dashboard data refreshed')
  initRevenueChart()
  initPortfolioChart()
  initEnergyChart()
  initMaintenanceChart()
  initSitesChart()
}

const handleTimeRangeChange = () => {
  ElMessage.info(`Switched to ${timeRange.value} view`)
  handleRefresh()
}

const handleCustomDateChange = () => {
  if (customDateRange.value) {
    ElMessage.success(`Custom date range applied: ${customDateRange.value[0].toLocaleDateString()} - ${customDateRange.value[1].toLocaleDateString()}`)
    handleRefresh()
  }
}

const handleKPIClick = (kpi: any) => {
  ElMessage.info(`Viewing detailed report for ${kpi.title}`)
}

const viewAllDecisions = () => {
  ElMessage.info('Navigating to full decisions list...')
}

const viewAllAlerts = () => {
  ElMessage.info('Navigating to alerts center...')
}

const viewAllSites = () => {
  ElMessage.info('Navigating to sites overview...')
}

const viewAlert = (alert: any) => {
  ElMessage.info(`Viewing alert: ${alert.title}`)
}

const viewRecommendation = (rec: any) => {
  ElMessage.info(`Reviewing recommendation: ${rec.title}`)
}

// ==================== Loading Simulation ====================
const initCharts = async () => {
  await nextTick()
  setTimeout(() => {
    initRevenueChart()
    initPortfolioChart()
    initEnergyChart()
    initMaintenanceChart()
    initSitesChart()
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

/* ==================== Main Dashboard Styles ==================== */
.executive-dashboard {
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

.time-range-card {
  margin-bottom: 20px;

  .time-range-container {
    display: flex;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;

    .range-label {
      font-weight: 600;
      color: #303133;
    }
  }
}

.kpi-row {
  margin-bottom: 20px;
}

.kpi-card {
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
  }

  .kpi-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .kpi-info {
    flex: 1;
  }

  .kpi-title {
    font-size: 14px;
    color: #909399;
    margin-bottom: 8px;
  }

  .kpi-value {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }

  .kpi-trend {
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

  .kpi-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.charts-row {
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

.chart-container {
  width: 100%;
  height: 350px;
}

.pie-chart-container {
  width: 100%;
  height: 330px;
}

.gauge-container {
  width: 100%;
  height: 280px;
}

.horizontal-bar-container {
  width: 100%;
  height: 280px;
}

.bar-chart-container {
  width: 100%;
  height: 280px;
}

.recent-row {
  margin-bottom: 20px;
}

.recent-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}

.alerts-list {
  max-height: 300px;
  overflow-y: auto;

  .alert-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px;
    border-bottom: 1px solid #ebeef5;
    transition: background 0.2s;

    &:hover {
      background: #f5f7fa;
    }

    .alert-icon {
      flex-shrink: 0;

      .el-icon {
        font-size: 20px;
      }
    }

    .alert-content {
      flex: 1;

      .alert-title {
        font-weight: 600;
        font-size: 14px;
        color: #303133;
        margin-bottom: 4px;
      }

      .alert-description {
        font-size: 12px;
        color: #606266;
        margin-bottom: 4px;
      }

      .alert-time {
        font-size: 11px;
        color: #909399;
      }
    }

    &.critical .alert-icon .el-icon {
      color: #f56c6c;
    }

    &.warning .alert-icon .el-icon {
      color: #e6a23c;
    }

    &.info .alert-icon .el-icon {
      color: #409eff;
    }
  }
}

.recommendations-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}

.recommendation-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 12px;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .rec-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    flex-shrink: 0;
  }

  .rec-content {
    flex: 1;

    .rec-title {
      font-weight: 600;
      font-size: 15px;
      color: #303133;
      margin-bottom: 6px;
    }

    .rec-description {
      font-size: 12px;
      color: #606266;
      margin-bottom: 8px;
      line-height: 1.4;
    }

    .rec-impact {
      font-size: 12px;
      margin-bottom: 8px;

      .impact-label {
        color: #909399;
      }

      .impact-value {
        font-weight: 600;
        margin-left: 4px;
      }
    }
  }
}

:deep(.el-table) {
  font-size: 13px;
}
</style>