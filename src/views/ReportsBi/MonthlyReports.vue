<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Search, Refresh, Document, Download, Printer,
  Share, Star, Clock, Warning, CircleCheck,
  TrendCharts, DataLine, Calendar, Setting,
  Plus, Upload, Filter, ArrowUp, ArrowDown,
  View, User, Trophy, Medal, Coin,
  Money, PieChart, DataAnalysis
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Loading monthly data...',
  'Aggregating monthly metrics...',
  'Generating monthly reports...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedMonth = ref('')
const selectedCategory = ref('all')
const reportPreviewVisible = ref(false)
const generateReportVisible = ref(false)
const chartRef = ref(null)
const trendChartRef = ref(null)
const distributionChartRef = ref(null)

let monthlyChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null
let distributionChart: echarts.ECharts | null = null

// Month options
const monthOptions = [
  'January 2024', 'February 2024', 'March 2024',
  'April 2024', 'May 2024', 'June 2024',
  'July 2024', 'August 2024', 'September 2024',
  'October 2024', 'November 2024', 'December 2024'
]

// Report categories
const reportCategories = [
  { value: 'all', label: 'All Reports', icon: '📊', color: '#409EFF' },
  { value: 'system', label: 'System Health', icon: '🏥', color: '#409EFF' },
  { value: 'energy', label: 'Energy', icon: '⚡', color: '#67C23A' },
  { value: 'alarms', label: 'Alarms', icon: '🔔', color: '#F56C6C' },
  { value: 'maintenance', label: 'Maintenance', icon: '🔧', color: '#E6A23C' },
  { value: 'financial', label: 'Financial', icon: '💰', color: '#9B59B6' },
  { value: 'sustainability', label: 'Sustainability', icon: '🌱', color: '#1ABC9C' }
]

// Monthly reports data
const monthlyReports = ref([
  {
    id: 'MR001', title: 'January 2024 - System Health Report', category: 'system', month: 'January 2024',
    summary: 'Overall system health at 98.5% this month. Critical incidents reduced by 15%.',
    metrics: { avgHealthScore: 98.5, uptime: 99.96, incidents: 32, critical: 4, mttr: 28 },
    status: 'excellent', author: 'System Analytics', downloads: 89, views: 245,
    tags: ['health', 'monthly', 'overview'], trend: '+1.8%', cost: 0
  },
  {
    id: 'MR002', title: 'January 2024 - Energy Report', category: 'energy', month: 'January 2024',
    summary: 'Total consumption: 385,200 kWh. 4.5% reduction from previous month.',
    metrics: { totalConsumption: 385200, cost: 45200, savings: 4.5, peak: 1850, co2Reduction: 12.5 },
    status: 'excellent', author: 'Energy Team', downloads: 76, views: 198,
    tags: ['energy', 'cost', 'sustainability'], trend: '-4.5%', cost: 45200
  },
  {
    id: 'MR003', title: 'January 2024 - Alarms Summary', category: 'alarms', month: 'January 2024',
    summary: '156 total alarms. 89% resolution rate within SLA.',
    metrics: { total: 156, critical: 18, high: 32, resolved: 139, avgResponse: 18 },
    status: 'good', author: 'Security Team', downloads: 54, views: 167,
    tags: ['alarms', 'incidents', 'security'], trend: '-8%', cost: 0
  },
  {
    id: 'MR004', title: 'January 2024 - Maintenance Report', category: 'maintenance', month: 'January 2024',
    summary: '124 work orders completed. 98% SLA compliance.',
    metrics: { completed: 124, compliance: 98, avgResponse: 38, preventive: 45, cost: 28500 },
    status: 'good', author: 'Maintenance Team', downloads: 48, views: 134,
    tags: ['maintenance', 'work-orders', 'service'], trend: '+5%', cost: 28500
  },
  {
    id: 'MR005', title: 'January 2024 - Financial Summary', category: 'financial', month: 'January 2024',
    summary: 'Total operational cost: $142,500. 3.2% under budget.',
    metrics: { totalCost: 142500, budget: 147200, savings: 4700, roi: 8.5, energyCost: 45200 },
    status: 'excellent', author: 'Finance Team', downloads: 92, views: 223,
    tags: ['financial', 'cost', 'budget'], trend: '-3.2%', cost: 142500
  },
  {
    id: 'MR006', title: 'January 2024 - Sustainability Report', category: 'sustainability', month: 'January 2024',
    summary: 'Carbon footprint reduced by 8%. 65% renewable energy usage.',
    metrics: { carbonFootprint: 18500, renewablePercentage: 65, wasteReduction: 12, waterSaved: 8500 },
    status: 'excellent', author: 'Sustainability Team', downloads: 67, views: 189,
    tags: ['sustainability', 'carbon', 'esg'], trend: '-8%', cost: 0
  },
  {
    id: 'MR007', title: 'December 2023 - System Health', category: 'system', month: 'December 2023',
    summary: 'Overall system health at 97.2% this month.',
    metrics: { avgHealthScore: 97.2, uptime: 99.89, incidents: 38, critical: 6, mttr: 32 },
    status: 'good', author: 'System Analytics', downloads: 78, views: 212,
    tags: ['health', 'monthly', 'overview'], trend: '-0.5%', cost: 0
  },
  {
    id: 'MR008', title: 'December 2023 - Energy Report', category: 'energy', month: 'December 2023',
    summary: 'Total consumption: 403,500 kWh. 2.1% increase due to heating.',
    metrics: { totalConsumption: 403500, cost: 48500, savings: -2.1, peak: 1920, co2Reduction: 8 },
    status: 'warning', author: 'Energy Team', downloads: 65, views: 178,
    tags: ['energy', 'cost', 'sustainability'], trend: '+2.1%', cost: 48500
  }
])

// Monthly statistics
const monthStats = reactive({
  total: 0,
  excellent: 0,
  good: 0,
  warning: 0,
  totalDownloads: 0,
  totalViews: 0,
  avgHealthScore: 0,
  totalCost: 0,
  totalSavings: 0,
  bestMonth: '',
  topCategory: ''
})

// Generate report form
const generateForm = reactive({
  title: '',
  category: 'system',
  month: monthOptions[0],
  includeCharts: true,
  includeRecommendations: true,
  format: 'pdf',
  sendToEmail: false,
  email: '',
  includeFinancials: false
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 6,
  total: monthlyReports.value.length
})

// Filtered reports
const filteredReports = computed(() => {
  let filtered = monthlyReports.value
  if (searchKeyword.value) {
    filtered = filtered.filter(r =>
        r.title.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        r.summary.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        r.tags.some(t => t.includes(searchKeyword.value.toLowerCase()))
    )
  }
  if (selectedMonth.value) {
    filtered = filtered.filter(r => r.month === selectedMonth.value)
  }
  if (selectedCategory.value !== 'all') {
    filtered = filtered.filter(r => r.category === selectedCategory.value)
  }
  pagination.total = filtered.length
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// Available months for filter
const availableMonths = computed(() => {
  return [...new Set(monthlyReports.value.map(r => r.month))]
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
        initCharts()
        updateStats()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initCharts = () => {
  initMonthlyChart()
  initTrendChart()
  initDistributionChart()
}

const initMonthlyChart = () => {
  if (!chartRef.value) return

  monthlyChart = echarts.init(chartRef.value)
  monthlyChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Health Score', 'Cost ($K)'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: ['Nov', 'Dec', 'Jan', 'Feb', 'Mar'] },
    yAxis: [
      { type: 'value', name: 'Health Score (%)', min: 90, max: 100 },
      { type: 'value', name: 'Cost ($K)', min: 0, max: 200 }
    ],
    series: [
      { name: 'Health Score', type: 'line', data: [96.8, 97.2, 98.5, 98.2, 98.8], smooth: true, lineStyle: { color: '#409EFF', width: 3 }, areaStyle: { opacity: 0.1, color: '#409EFF' }, symbol: 'circle', symbolSize: 8 },
      { name: 'Cost ($K)', type: 'bar', data: [135, 142, 148, 145, 150], itemStyle: { color: '#E6A23C', borderRadius: [4, 4, 0, 0] }, yAxisIndex: 1 }
    ]
  })
}

const initTrendChart = () => {
  if (!trendChartRef.value) return

  trendChart = echarts.init(trendChartRef.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Energy (MWh)', 'Incidents'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: ['Nov', 'Dec', 'Jan', 'Feb', 'Mar'] },
    yAxis: [
      { type: 'value', name: 'Energy (MWh)' },
      { type: 'value', name: 'Incidents' }
    ],
    series: [
      { name: 'Energy (MWh)', type: 'line', data: [380, 403, 385, 392, 378], smooth: true, lineStyle: { color: '#67C23A', width: 3 }, areaStyle: { opacity: 0.1, color: '#67C23A' }, symbol: 'circle', symbolSize: 8 },
      { name: 'Incidents', type: 'bar', data: [42, 38, 32, 35, 30], itemStyle: { color: '#F56C6C', borderRadius: [4, 4, 0, 0] }, yAxisIndex: 1 }
    ]
  })
}

const initDistributionChart = () => {
  if (!distributionChartRef.value) return

  const categoryData = reportCategories.filter(c => c.value !== 'all').map(cat => {
    const reports = monthlyReports.value.filter(r => r.category === cat.value)
    const count = reports.length
    return { name: cat.label, value: count, color: cat.color }
  })

  distributionChart = echarts.init(distributionChartRef.value)
  distributionChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} reports)' },
    legend: { orient: 'vertical', left: 'left', data: categoryData.map(c => c.name) },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: categoryData.map(c => ({ name: c.name, value: c.value })),
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: {d}%' },
      itemStyle: { color: (params: any) => categoryData.find(c => c.name === params.name)?.color || '#909399' }
    }]
  })
}

const updateStats = () => {
  monthStats.total = monthlyReports.value.length
  monthStats.excellent = monthlyReports.value.filter(r => r.status === 'excellent').length
  monthStats.good = monthlyReports.value.filter(r => r.status === 'good').length
  monthStats.warning = monthlyReports.value.filter(r => r.status === 'warning').length
  monthStats.totalDownloads = monthlyReports.value.reduce((sum, r) => sum + r.downloads, 0)
  monthStats.totalViews = monthlyReports.value.reduce((sum, r) => sum + r.views, 0)

  const healthScores = monthlyReports.value.map(r => r.metrics.avgHealthScore).filter(s => s)
  if (healthScores.length > 0) {
    monthStats.avgHealthScore = Math.round(healthScores.reduce((a, b) => a + b, 0) / healthScores.length)
  }

  monthStats.totalCost = monthlyReports.value.reduce((sum, r) => sum + (r.cost || 0), 0)
  monthStats.totalSavings = monthlyReports.value.reduce((sum, r) => sum + (r.metrics.savings || 0), 0)

  // Find best month
  const monthPerformance = [...new Set(monthlyReports.value.map(r => r.month))].map(month => {
    const reports = monthlyReports.value.filter(r => r.month === month)
    const avgScore = reports.reduce((sum, r) => sum + (r.metrics.avgHealthScore || 95), 0) / reports.length
    return { month, score: avgScore }
  })
  const best = monthPerformance.reduce((best, curr) => curr.score > best.score ? curr : monthPerformance[0] || { month: '', score: 0 })
  monthStats.bestMonth = best.month

  // Find top category
  const categoryPerformance = reportCategories.filter(c => c.value !== 'all').map(cat => {
    const reports = monthlyReports.value.filter(r => r.category === cat.value)
    const count = reports.length
    return { category: cat.label, count }
  })
  const top = categoryPerformance.reduce((top, curr) => curr.count > top.count ? categoryPerformance[0] : { category: '', count: 0 })
  monthStats.topCategory = top.category
}

const handleResize = () => {
  monthlyChart?.resize()
  trendChart?.resize()
  distributionChart?.resize()
}

// ==================== Report Functions ====================
const refreshReports = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  loading.value = false
  ElMessage.success('Monthly reports refreshed successfully')
}

const viewReport = (report: any) => {
  selectedReport.value = report
  reportPreviewVisible.value = true
}

const downloadReport = async (report: any) => {
  ElMessage.info(`Downloading ${report.title}...`)
  await new Promise(resolve => setTimeout(resolve, 1000))
  report.downloads++
  ElMessage.success(`${report.title} downloaded successfully`)
}

const shareReport = (report: any) => {
  ElMessage.success(`Share link generated for ${report.title}`)
}

const favoriteReport = (report: any) => {
  ElMessage.success(`${report.title} added to favorites`)
}

const openGenerateReport = () => {
  generateForm.title = ''
  generateForm.category = 'system'
  generateForm.month = monthOptions[0]
  generateForm.includeCharts = true
  generateForm.includeRecommendations = true
  generateForm.format = 'pdf'
  generateForm.sendToEmail = false
  generateForm.email = ''
  generateForm.includeFinancials = false
  generateReportVisible.value = true
}

const generateReport = async () => {
  if (!generateForm.title) {
    ElMessage.warning('Please enter a report title')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1500))

  const newReport = {
    id: `MR${String(monthlyReports.value.length + 1).padStart(3, '0')}`,
    title: generateForm.title,
    category: generateForm.category,
    month: generateForm.month,
    summary: 'Monthly report generated successfully',
    metrics: { avgHealthScore: 98, uptime: 99.9, incidents: 0 },
    status: 'good',
    author: 'Current User',
    downloads: 0,
    views: 0,
    tags: ['generated', generateForm.category],
    trend: '0%',
    cost: 0
  }

  monthlyReports.value.unshift(newReport)
  updateStats()
  generateReportVisible.value = false
  ElMessage.success('Monthly report generated successfully')
}

const exportAllReports = () => {
  const data = monthlyReports.value.map(r => ({
    ID: r.id,
    Title: r.title,
    Category: r.category,
    Month: r.month,
    Status: r.status,
    Downloads: r.downloads,
    Views: r.views,
    Trend: r.trend,
    Cost: r.cost ? `$${r.cost.toLocaleString()}` : 'N/A'
  }))

  const csv = convertToCSV(data)
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `monthly_reports_${new Date().toISOString()}.csv`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('All monthly reports exported successfully')
}

const convertToCSV = (data: any[]) => {
  const headers = Object.keys(data[0])
  const rows = data.map(obj => headers.map(header => JSON.stringify(obj[header])).join(','))
  return [headers.join(','), ...rows].join('\n')
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'excellent': return Trophy
    case 'good': return Medal
    case 'warning': return Warning
    default: return Clock
  }
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'excellent': return 'success'
    case 'good': return 'success'
    case 'warning': return 'warning'
    default: return 'danger'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'excellent': return 'Excellent'
    case 'good': return 'Good'
    case 'warning': return 'Warning'
    default: return 'Critical'
  }
}

const getTrendIcon = (trend: string) => {
  if (!trend) return null
  const isPositive = trend.startsWith('+') || (trend.startsWith('-') && trend.includes('reduction'))
  const isIncrease = trend.startsWith('+')
  if (isPositive && isIncrease) return ArrowUp
  if (isPositive && !isIncrease) return ArrowDown
  return null
}

const getTrendClass = (trend: string) => {
  if (!trend) return ''
  if (trend.startsWith('+')) return 'trend-positive'
  if (trend.startsWith('-')) return 'trend-negative'
  return ''
}

const formatCurrency = (value: number) => {
  if (!value) return 'N/A'
  return `$${value.toLocaleString()}`
}

const selectedReport = ref<any>(null)
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
          <span class="loading-title">Loading Monthly Reports</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Reports & BI - Monthly Reports</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="monthly-reports-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Monthly Reports</h1>
        <p class="page-subtitle">Comprehensive monthly performance analysis and insights</p>
      </div>
      <div class="header-right">
        <el-button type="primary" size="large" @click="openGenerateReport">
          <el-icon><Plus /></el-icon>
          Generate Report
        </el-button>
        <el-button size="large" @click="exportAllReports">
          <el-icon><Download /></el-icon>
          Export All
        </el-button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total-icon">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ monthStats.total }}</div>
          <div class="stat-label">Total Reports</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+2 this month</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon health-icon">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ monthStats.avgHealthScore }}%</div>
          <div class="stat-label">Avg Health Score</div>
        </div>
        <div class="stat-progress">
          <el-progress :percentage="monthStats.avgHealthScore" :stroke-width="4" :show-text="false" />
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon cost-icon">
          <el-icon><Coin /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ formatCurrency(monthStats.totalCost) }}</div>
          <div class="stat-label">Total Cost</div>
        </div>
        <div class="stat-trend">
          <span class="trend-down">↓ {{ formatCurrency(monthStats.totalSavings) }} saved</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon engagement-icon">
          <el-icon><View /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ monthStats.totalViews.toLocaleString() }}</div>
          <div class="stat-label">Total Views</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">↑ 18%</span>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-section">
        <div class="section-header">
          <h3>Monthly Performance Overview</h3>
          <el-button text type="primary" @click="initMonthlyChart">Refresh</el-button>
        </div>
        <div ref="chartRef" class="monthly-chart" style="height: 280px"></div>
      </div>

      <div class="chart-section">
        <div class="section-header">
          <h3>Energy & Incidents Trend</h3>
          <el-button text type="primary" @click="initTrendChart">Refresh</el-button>
        </div>
        <div ref="trendChartRef" class="trend-chart" style="height: 280px"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-section">
        <div class="section-header">
          <h3>Report Distribution by Category</h3>
          <el-button text type="primary" @click="initDistributionChart">Refresh</el-button>
        </div>
        <div ref="distributionChartRef" class="distribution-chart" style="height: 280px"></div>
      </div>

      <!-- Highlights Bar -->
      <div class="highlights-bar">
        <div class="highlight-item">
          <span class="highlight-icon">🏆</span>
          <span class="highlight-label">Best Month</span>
          <span class="highlight-value">{{ monthStats.bestMonth || 'January 2024' }}</span>
        </div>
        <div class="highlight-item">
          <span class="highlight-icon">📊</span>
          <span class="highlight-label">Top Category</span>
          <span class="highlight-value">{{ monthStats.topCategory || 'System Health' }}</span>
        </div>
        <div class="highlight-item">
          <span class="highlight-icon">📥</span>
          <span class="highlight-label">Total Downloads</span>
          <span class="highlight-value">{{ monthStats.totalDownloads.toLocaleString() }}</span>
        </div>
        <div class="highlight-item">
          <span class="highlight-icon">⭐</span>
          <span class="highlight-label">Excellent Reports</span>
          <span class="highlight-value">{{ monthStats.excellent }}</span>
        </div>
      </div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-bar">
      <div class="filters-left">
        <div class="search-box">
          <el-input
              v-model="searchKeyword"
              placeholder="Search reports..."
              :prefix-icon="Search"
              clearable
              style="width: 260px"
          />
        </div>
        <div class="category-filters">
          <button
              v-for="cat in reportCategories"
              :key="cat.value"
              class="category-chip"
              :class="{ active: selectedCategory === cat.value }"
              @click="selectedCategory = cat.value"
          >
            <span class="chip-icon">{{ cat.icon }}</span>
            <span>{{ cat.label }}</span>
          </button>
        </div>
      </div>
      <div class="filters-right">
        <el-select v-model="selectedMonth" placeholder="Filter by month" clearable style="width: 160px">
          <el-option v-for="month in availableMonths" :key="month" :label="month" :value="month" />
        </el-select>
        <el-button @click="refreshReports" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Reports Grid - Card Style -->
    <div class="reports-grid">
      <div
          v-for="report in filteredReports"
          :key="report.id"
          class="report-card"
          @click="viewReport(report)"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="card-category" :style="{ background: reportCategories.find(c => c.value === report.category)?.color || '#409EFF' }">
            {{ reportCategories.find(c => c.value === report.category)?.icon }}
          </div>
          <div class="card-status">
            <el-tag :type="getStatusType(report.status)" size="small" effect="light">
              <el-icon><component :is="getStatusIcon(report.status)" /></el-icon>
              {{ getStatusText(report.status) }}
            </el-tag>
          </div>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <h4 class="card-title">{{ report.title }}</h4>
          <p class="card-summary">{{ report.summary }}</p>

          <!-- Trend Indicator -->
          <div v-if="report.trend" class="trend-indicator" :class="getTrendClass(report.trend)">
            <el-icon v-if="getTrendIcon(report.trend)"><component :is="getTrendIcon(report.trend)" /></el-icon>
            <span>{{ report.trend }} vs previous month</span>
          </div>

          <!-- Metrics -->
          <div class="card-metrics">
            <div v-for="(value, key) in report.metrics" :key="key" class="metric-item">
              <span class="metric-label">{{ key.replace(/([A-Z])/g, ' $1').trim() }}:</span>
              <span class="metric-value">
                {{ typeof value === 'number' ?
                  (key === 'avgHealthScore' || key === 'uptime' || key === 'compliance' || key === 'renewablePercentage' ? value + '%' :
                      key === 'totalCost' || key === 'cost' || key === 'budget' || key === 'energyCost' ? '$' + value.toLocaleString() :
                          value.toLocaleString()) : value }}
              </span>
            </div>
          </div>

          <!-- Cost Highlight -->
          <div v-if="report.cost" class="cost-highlight">
            <span class="cost-label">Total Cost:</span>
            <span class="cost-value">{{ formatCurrency(report.cost) }}</span>
          </div>

          <!-- Tags -->
          <div class="card-tags">
            <span v-for="tag in report.tags.slice(0, 3)" :key="tag" class="tag">{{ tag }}</span>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="footer-info">
            <span class="info-item">
              <el-icon><Calendar /></el-icon>
              {{ report.month }}
            </span>
            <span class="info-item">
              <el-icon><User /></el-icon>
              {{ report.author }}
            </span>
          </div>
          <div class="footer-stats">
            <span class="stat-item">
              <el-icon><View /></el-icon>
              {{ report.views }}
            </span>
            <span class="stat-item">
              <el-icon><Download /></el-icon>
              {{ report.downloads }}
            </span>
          </div>
        </div>

        <!-- Action Buttons (appear on hover) -->
        <div class="card-actions">
          <el-button circle size="small" @click.stop="viewReport(report)">
            <el-icon><View /></el-icon>
          </el-button>
          <el-button circle size="small" type="primary" @click.stop="downloadReport(report)">
            <el-icon><Download /></el-icon>
          </el-button>
          <el-button circle size="small" @click.stop="shareReport(report)">
            <el-icon><Share /></el-icon>
          </el-button>
          <el-button circle size="small" @click.stop="favoriteReport(report)">
            <el-icon><Star /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination-wrapper">
      <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[6, 9, 12, 18]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
      />
    </div>

    <!-- Report Preview Dialog -->
    <el-dialog v-model="reportPreviewVisible" :title="selectedReport?.title" width="800px" top="5vh">
      <div class="report-preview">
        <div class="preview-header">
          <div class="preview-meta">
            <span><el-icon><Calendar /></el-icon> {{ selectedReport?.month }}</span>
            <span><el-icon><User /></el-icon> {{ selectedReport?.author }}</span>
            <el-tag :type="getStatusType(selectedReport?.status)" size="small">
              {{ getStatusText(selectedReport?.status) }}
            </el-tag>
          </div>
          <h2>{{ selectedReport?.title }}</h2>
          <p class="preview-summary">{{ selectedReport?.summary }}</p>
          <div v-if="selectedReport?.trend" class="preview-trend" :class="getTrendClass(selectedReport?.trend)">
            Monthly Trend: {{ selectedReport?.trend }}
          </div>
        </div>

        <el-divider />

        <div class="preview-metrics">
          <h4>Key Monthly Metrics</h4>
          <div class="metrics-grid">
            <div v-for="(value, key) in selectedReport?.metrics" :key="key" class="preview-metric">
              <div class="metric-label">{{ key.replace(/([A-Z])/g, ' $1').trim() }}</div>
              <div class="metric-value">{{ typeof value === 'number' ?
                  (key === 'avgHealthScore' || key === 'uptime' || key === 'compliance' || key === 'renewablePercentage' ? value + '%' :
                      key === 'totalCost' || key === 'cost' || key === 'budget' ? '$' + value.toLocaleString() :
                          value.toLocaleString()) : value }}</div>
            </div>
          </div>
        </div>

        <div v-if="selectedReport?.cost" class="preview-cost">
          <h4>Financial Summary</h4>
          <div class="cost-box">
            <span class="cost-label">Total Cost:</span>
            <span class="cost-value">{{ formatCurrency(selectedReport.cost) }}</span>
          </div>
        </div>

        <div class="preview-tags">
          <h4>Tags</h4>
          <div class="tags-list">
            <span v-for="tag in selectedReport?.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="reportPreviewVisible = false">Close</el-button>
        <el-button type="primary" @click="downloadReport(selectedReport)">
          <el-icon><Download /></el-icon> Download PDF
        </el-button>
        <el-button @click="shareReport(selectedReport)">
          <el-icon><Share /></el-icon> Share
        </el-button>
      </template>
    </el-dialog>

    <!-- Generate Report Dialog -->
    <el-dialog v-model="generateReportVisible" title="Generate Monthly Report" width="500px">
      <el-form :model="generateForm" label-width="130px">
        <el-form-item label="Report Title" required>
          <el-input v-model="generateForm.title" placeholder="Enter report title" />
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="generateForm.category" style="width: 100%">
            <el-option v-for="cat in reportCategories.slice(1)" :key="cat.value" :label="cat.label" :value="cat.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Month">
          <el-select v-model="generateForm.month" style="width: 100%">
            <el-option v-for="month in monthOptions" :key="month" :label="month" :value="month" />
          </el-select>
        </el-form-item>
        <el-form-item label="Include Charts">
          <el-switch v-model="generateForm.includeCharts" />
        </el-form-item>
        <el-form-item label="Include Recommendations">
          <el-switch v-model="generateForm.includeRecommendations" />
        </el-form-item>
        <el-form-item label="Include Financials">
          <el-switch v-model="generateForm.includeFinancials" />
        </el-form-item>
        <el-form-item label="Output Format">
          <el-radio-group v-model="generateForm.format">
            <el-radio value="pdf">PDF</el-radio>
            <el-radio value="excel">Excel</el-radio>
            <el-radio value="csv">CSV</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Send to Email">
          <el-switch v-model="generateForm.sendToEmail" />
        </el-form-item>
        <el-form-item v-if="generateForm.sendToEmail" label="Email Address">
          <el-input v-model="generateForm.email" placeholder="recipient@example.com" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="generateReportVisible = false">Cancel</el-button>
        <el-button type="primary" @click="generateReport">Generate Report</el-button>
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
.monthly-reports-container {
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
  margin-bottom: 28px;
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

.health-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.cost-icon {
  background: linear-gradient(135deg, #fef0f0 0%, #fcd9d9 100%);
  color: #f56c6c;
}

.engagement-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
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
}

.trend-up {
  font-size: 11px;
  color: #67c23a;
  background: #f0f9ff;
  padding: 4px 8px;
  border-radius: 20px;
}

.trend-down {
  font-size: 11px;
  color: #f56c6c;
  background: #fef0f0;
  padding: 4px 8px;
  border-radius: 20px;
}

.stat-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
}

/* Charts Row */
.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 20px;
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
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.monthly-chart,
.trend-chart,
.distribution-chart {
  width: 100%;
}

/* Highlights Bar */
.highlights-bar {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  padding: 20px;
  color: white;
}

.highlight-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-align: center;
}

.highlight-icon {
  font-size: 28px;
}

.highlight-label {
  font-size: 12px;
  opacity: 0.8;
}

.highlight-value {
  font-size: 16px;
  font-weight: 600;
}

/* Filters Bar */
.filters-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 24px;
  margin-top: 20px;
}

.filters-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.category-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.category-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 40px;
  font-size: 13px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s ease;
}

.category-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.category-chip.active {
  background: #409eff;
  border-color: #409eff;
  color: white;
}

.chip-icon {
  font-size: 14px;
}

.filters-right {
  display: flex;
  gap: 12px;
}

/* Reports Grid */
.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.report-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.report-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 30px -12px rgba(0, 0, 0, 0.15);
}

.report-card:hover .card-actions {
  opacity: 1;
}

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 0 20px;
}

.card-category {
  width: 44px;
  height: 44px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: white;
}

/* Card Body */
.card-body {
  padding: 16px 20px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 10px 0;
  line-height: 1.4;
}

.card-summary {
  font-size: 14px;
  color: #64748b;
  line-height: 1.5;
  margin: 0 0 12px 0;
}

.trend-indicator {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 14px;
}

.trend-positive {
  background: #f0f9ff;
  color: #67c23a;
}

.trend-negative {
  background: #fef0f0;
  color: #f56c6c;
}

.card-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 12px;
  padding: 12px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.metric-item {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.metric-label {
  font-size: 11px;
  color: #909399;
  text-transform: capitalize;
}

.metric-value {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
}

.cost-highlight {
  background: linear-gradient(135deg, #fef0f0 0%, #fcd9d9 100%);
  padding: 8px 12px;
  border-radius: 12px;
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
}

.cost-label {
  font-size: 12px;
  color: #f56c6c;
  font-weight: 500;
}

.cost-value {
  font-size: 14px;
  font-weight: 700;
  color: #f56c6c;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  font-size: 11px;
  padding: 4px 10px;
  background: #f5f7fa;
  border-radius: 20px;
  color: #606266;
}

/* Card Footer */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px 16px 20px;
  border-top: 1px solid #f0f0f0;
  background: #fafbfc;
}

.footer-info {
  display: flex;
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
}

.footer-stats {
  display: flex;
  gap: 12px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #606266;
}

/* Card Actions (Hover) */
.card-actions {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  gap: 12px;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  padding: 12px 20px;
  border-radius: 60px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.card-actions .el-button {
  background: white;
  border: none;
}

.card-actions .el-button:hover {
  transform: scale(1.1);
}

/* Pagination */
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
}

/* Report Preview */
.report-preview {
  max-height: 60vh;
  overflow-y: auto;
}

.preview-header {
  text-align: center;
  margin-bottom: 24px;
}

.preview-meta {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #909399;
}

.preview-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.preview-header h2 {
  font-size: 24px;
  margin: 0 0 12px 0;
}

.preview-summary {
  font-size: 14px;
  color: #64748b;
  line-height: 1.6;
}

.preview-trend {
  display: inline-block;
  margin-top: 12px;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
}

.preview-metrics h4,
.preview-cost h4,
.preview-tags h4 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px 0;
  color: #1e293b;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.preview-metric {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 12px;
  text-align: center;
}

.preview-metric .metric-label {
  font-size: 12px;
  color: #909399;
  text-transform: capitalize;
  margin-bottom: 4px;
}

.preview-metric .metric-value {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

.cost-box {
  background: linear-gradient(135deg, #fef0f0 0%, #fcd9d9 100%);
  padding: 16px;
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.cost-box .cost-label {
  font-size: 14px;
  font-weight: 500;
  color: #f56c6c;
}

.cost-box .cost-value {
  font-size: 20px;
  font-weight: 700;
  color: #f56c6c;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-row {
    grid-template-columns: 1fr;
  }

  .reports-grid {
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  }

  .highlights-bar {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .monthly-reports-container {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filters-left {
    flex-direction: column;
  }

  .category-filters {
    justify-content: center;
  }

  .page-header {
    flex-direction: column;
    text-align: center;
  }

  .header-right {
    width: 100%;
    justify-content: center;
  }

  .highlights-bar {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}

@media (max-width: 480px) {
  .reports-grid {
    grid-template-columns: 1fr;
  }
}
</style>