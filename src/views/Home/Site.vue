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

  <!-- Site Health Dashboard Page Content -->
  <div v-else class="site-health-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>Site Health Dashboard</h1>
        <p class="subtitle">Comprehensive health monitoring across all facility sites and systems</p>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="refreshData">Refresh</el-button>
        <el-button type="primary" :icon="Download" @click="exportReport">Export Report</el-button>
        <el-select v-model="globalPeriod" placeholder="Select Period" size="default" style="width: 120px">
          <el-option label="Today" value="today" />
          <el-option label="This Week" value="week" />
          <el-option label="This Month" value="month" />
          <el-option label="This Quarter" value="quarter" />
        </el-select>
      </div>
    </div>

    <!-- Overall Health Score -->
    <div class="overall-health-card">
      <div class="health-score-container">
        <div class="health-score">
          <el-progress
              type="circle"
              :percentage="overallHealth"
              :color="getHealthColor(overallHealth)"
              :width="140"
              :stroke-width="12"
          >
            <template #default>
              <div class="score-text">
                <span class="score-value">{{ overallHealth }}%</span>
                <span class="score-label">Overall Health</span>
              </div>
            </template>
          </el-progress>
        </div>
        <div class="health-stats">
          <div class="stat-item">
            <div class="stat-value">{{ healthySites }}</div>
            <div class="stat-label">Healthy Sites</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ warningSites }}</div>
            <div class="stat-label">Warning</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ criticalSites }}</div>
            <div class="stat-label">Critical</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ offlineSites }}</div>
            <div class="stat-label">Offline</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Site Cards Grid -->
    <div class="sites-grid">
      <div v-for="site in sites" :key="site.id" class="site-card" :class="getHealthClass(site.healthStatus)">
        <div class="card-header">
          <div class="site-info">
            <div class="site-name">{{ site.name }}</div>
            <div class="site-location">{{ site.location }}</div>
          </div>
          <div class="site-status">
            <el-tag :type="getStatusTagType(site.healthStatus)" size="small" effect="dark">
              {{ getStatusLabel(site.healthStatus) }}
            </el-tag>
          </div>
        </div>

        <div class="card-metrics">
          <div class="metric">
            <span class="metric-label">Devices</span>
            <span class="metric-value">{{ site.deviceCount }}</span>
            <span class="metric-sub">{{ site.onlineDevices }} online</span>
          </div>
          <div class="metric">
            <span class="metric-label">Availability</span>
            <span class="metric-value" :class="getAvailabilityClass(site.availability)">
              {{ site.availability }}%
            </span>
          </div>
          <div class="metric">
            <span class="metric-label">Active Alarms</span>
            <span class="metric-value" :class="site.activeAlarms > 0 ? 'text-danger' : 'text-success'">
              {{ site.activeAlarms }}
            </span>
          </div>
        </div>

        <div class="card-progress">
          <div class="progress-item">
            <div class="progress-header">
              <span>System Uptime</span>
              <span>{{ site.uptime }}%</span>
            </div>
            <el-progress :percentage="site.uptime" :color="getProgressColor(site.uptime)" :stroke-width="6" :show-text="false" />
          </div>
        </div>

        <div class="card-footer">
          <el-button size="small" :icon="Monitor" @click="viewSiteDetails(site)">View Details</el-button>
          <el-button size="small" :icon="DataLine" @click="viewSiteMetrics(site)">Metrics</el-button>
        </div>
      </div>
    </div>

    <!-- System Health Overview Chart -->
    <div class="chart-card">
      <div class="card-header">
        <h3>System Health by Category</h3>
        <el-radio-group v-model="chartPeriod" size="small">
          <el-radio-button label="week">Week</el-radio-button>
          <el-radio-button label="month">Month</el-radio-button>
          <el-radio-button label="quarter">Quarter</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-container" ref="systemChartRef"></div>
    </div>

    <!-- Critical Issues Table -->
    <div class="table-card">
      <div class="card-header">
        <h3>Critical Issues Requiring Attention</h3>
        <el-select v-model="siteFilter" placeholder="All Sites" clearable size="default" style="width: 140px">
          <el-option label="All Sites" value="all" />
          <el-option v-for="site in sites" :key="site.id" :label="site.name" :value="site.name" />
        </el-select>
      </div>
      <el-table :data="paginatedIssues" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="site" label="Site" width="140" />
        <el-table-column prop="issue" label="Issue" min-width="250" show-overflow-tooltip />
        <el-table-column prop="category" label="Category" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityTagType(row.severity)" size="small" effect="dark">
              {{ row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detectedAt" label="Detected" width="160" sortable>
          <template #default="{ row }">
            {{ formatDateTime(row.detectedAt) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getIssueStatusTagType(row.status)" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewIssue(row)">View</el-button>
            <el-button link type="success" size="small" @click="assignIssue(row)">Assign</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredIssues.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Site Comparison -->
    <div class="comparison-section">
      <div class="section-header">
        <h2>
          <el-icon><TrendCharts /></el-icon>
          Site Performance Comparison
        </h2>
      </div>
      <div class="comparison-grid">
        <div v-for="site in sites" :key="site.id" class="comparison-card">
          <div class="comparison-header">
            <span class="site-name">{{ site.name }}</span>
            <span class="site-score" :class="getHealthClass(site.healthStatus)">{{ site.healthScore }}%</span>
          </div>
          <div class="comparison-metrics">
            <div class="comp-metric">
              <span>Uptime</span>
              <el-progress :percentage="site.uptime" :color="getProgressColor(site.uptime)" :stroke-width="6" :show-text="true" :format="(p) => p + '%'" />
            </div>
            <div class="comp-metric">
              <span>Availability</span>
              <el-progress :percentage="site.availability" :color="getProgressColor(site.availability)" :stroke-width="6" :show-text="true" :format="(p) => p + '%'" />
            </div>
            <div class="comp-metric">
              <span>SLA Compliance</span>
              <el-progress :percentage="site.slaCompliance" :color="getProgressColor(site.slaCompliance)" :stroke-width="6" :show-text="true" :format="(p) => p + '%'" />
            </div>
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
  Monitor,
  DataLine,
  TrendCharts,
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
interface Site {
  id: number
  name: string
  location: string
  healthStatus: 'healthy' | 'warning' | 'critical' | 'offline'
  healthScore: number
  deviceCount: number
  onlineDevices: number
  availability: number
  uptime: number
  slaCompliance: number
  activeAlarms: number
}

interface CriticalIssue {
  id: number
  site: string
  issue: string
  category: string
  severity: 'critical' | 'high' | 'medium'
  detectedAt: string
  status: 'open' | 'in-progress' | 'resolved'
}

// ==================== State ====================
const globalPeriod = ref('week')
const chartPeriod = ref('week')
const siteFilter = ref('all')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const systemChartRef = ref<HTMLElement | null>(null)
let systemChart: echarts.ECharts | null = null

// ==================== Mock Data ====================
const sites = ref<Site[]>([
  { id: 1, name: 'Main Campus', location: '123 Business Park, Building A', healthStatus: 'healthy', healthScore: 94, deviceCount: 245, onlineDevices: 242, availability: 99.8, uptime: 99.95, slaCompliance: 97, activeAlarms: 2 },
  { id: 2, name: 'Data Center East', location: '456 Tech Drive', healthStatus: 'warning', healthScore: 78, deviceCount: 189, onlineDevices: 182, availability: 96.2, uptime: 98.5, slaCompliance: 89, activeAlarms: 5 },
  { id: 3, name: 'West Office', location: '789 Corporate Way', healthStatus: 'healthy', healthScore: 91, deviceCount: 156, onlineDevices: 154, availability: 98.7, uptime: 99.2, slaCompliance: 95, activeAlarms: 1 },
  { id: 4, name: 'North Warehouse', location: '321 Logistics Blvd', healthStatus: 'critical', healthScore: 62, deviceCount: 89, onlineDevices: 76, availability: 85.4, uptime: 92.8, slaCompliance: 76, activeAlarms: 12 },
  { id: 5, name: 'South Satellite', location: '555 Remote Road', healthStatus: 'offline', healthScore: 45, deviceCount: 45, onlineDevices: 28, availability: 62.3, uptime: 78.5, slaCompliance: 58, activeAlarms: 18 }
])

const criticalIssues = ref<CriticalIssue[]>([
  { id: 1, site: 'North Warehouse', issue: 'HVAC System Failure - Temperature exceeding threshold', category: 'HVAC', severity: 'critical', detectedAt: '2025-05-29 08:15:00', status: 'open' },
  { id: 2, site: 'Data Center East', issue: 'UPS Battery Low - Critical capacity reached', category: 'Electrical', severity: 'critical', detectedAt: '2025-05-29 06:30:00', status: 'in-progress' },
  { id: 3, site: 'South Satellite', issue: 'Network Connectivity Lost - Site offline', category: 'Network', severity: 'critical', detectedAt: '2025-05-28 22:00:00', status: 'open' },
  { id: 4, site: 'North Warehouse', issue: 'Security Camera Feed Loss - 4 cameras offline', category: 'Security', severity: 'high', detectedAt: '2025-05-28 14:45:00', status: 'in-progress' },
  { id: 5, site: 'Data Center East', issue: 'Cooling Efficiency Degraded - PUE rising', category: 'DCIM', severity: 'high', detectedAt: '2025-05-28 10:20:00', status: 'in-progress' },
  { id: 6, site: 'Main Campus', issue: 'Lighting Control Panel Communication Error', category: 'Lighting', severity: 'medium', detectedAt: '2025-05-28 08:00:00', status: 'resolved' },
  { id: 7, site: 'North Warehouse', issue: 'Water Leak Detected - Loading Dock Area', category: 'Plumbing', severity: 'critical', detectedAt: '2025-05-27 16:30:00', status: 'open' }
])

// ==================== Computed Values ====================
const overallHealth = computed(() => {
  const total = sites.value.reduce((sum, s) => sum + s.healthScore, 0)
  return Math.round(total / sites.value.length)
})

const healthySites = computed(() => sites.value.filter(s => s.healthStatus === 'healthy').length)
const warningSites = computed(() => sites.value.filter(s => s.healthStatus === 'warning').length)
const criticalSites = computed(() => sites.value.filter(s => s.healthStatus === 'critical').length)
const offlineSites = computed(() => sites.value.filter(s => s.healthStatus === 'offline').length)

const filteredIssues = computed(() => {
  let result = [...criticalIssues.value]
  if (siteFilter.value !== 'all') {
    result = result.filter(i => i.site === siteFilter.value)
  }
  return result
})

const paginatedIssues = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredIssues.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getHealthColor = (score: number) => {
  if (score >= 85) return '#67c23a'
  if (score >= 70) return '#409eff'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
}

const getProgressColor = (percentage: number) => {
  if (percentage >= 95) return '#67c23a'
  if (percentage >= 85) return '#409eff'
  if (percentage >= 75) return '#e6a23c'
  return '#f56c6c'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    healthy: 'Healthy',
    warning: 'Warning',
    critical: 'Critical',
    offline: 'Offline'
  }
  return map[status] || status
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    healthy: 'success',
    warning: 'warning',
    critical: 'danger',
    offline: 'info'
  }
  return map[status] || 'info'
}

const getHealthClass = (status: string) => {
  const map: Record<string, string> = {
    healthy: 'status-healthy',
    warning: 'status-warning',
    critical: 'status-critical',
    offline: 'status-offline'
  }
  return map[status] || ''
}

const getAvailabilityClass = (availability: number) => {
  if (availability >= 99) return 'text-success'
  if (availability >= 95) return 'text-warning'
  return 'text-danger'
}

const getSeverityTagType = (severity: string) => {
  const map: Record<string, string> = {
    critical: 'danger',
    high: 'warning',
    medium: 'primary'
  }
  return map[severity] || 'info'
}

const getIssueStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    open: 'danger',
    'in-progress': 'warning',
    resolved: 'success'
  }
  return map[status] || 'info'
}

const formatDateTime = (dateStr: string) => {
  return dateStr
}

// ==================== Chart Functions ====================
const initSystemChart = () => {
  if (!systemChartRef.value) return
  if (systemChart) systemChart.dispose()

  systemChart = echarts.init(systemChartRef.value)

  const categories = ['HVAC', 'Electrical', 'Lighting', 'Security', 'Plumbing', 'Network']
  const healthScores = [82, 78, 91, 85, 72, 68]

  systemChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: (value: number) => value + '%' },
    grid: { left: '10%', right: '5%', top: '5%', bottom: '5%', containLabel: true },
    xAxis: { type: 'value', name: 'Health Score (%)', max: 100 },
    yAxis: { type: 'category', data: categories },
    series: [{
      type: 'bar', data: healthScores,
      itemStyle: { borderRadius: [0, 4, 4, 0], color: (params: any) => getHealthColor(params.data) },
      label: { show: true, position: 'right', formatter: '{c}%' }
    }]
  })
}

// ==================== Actions ====================
const refreshData = async () => {
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  ElMessage.success('Site health data refreshed')
  initSystemChart()
  tableLoading.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting site health report...')
}

const viewSiteDetails = (site: Site) => {
  ElMessage.info(`Viewing details for ${site.name}`)
}

const viewSiteMetrics = (site: Site) => {
  ElMessage.info(`Viewing metrics for ${site.name}`)
}

const viewIssue = (issue: CriticalIssue) => {
  ElMessage.info(`Viewing issue: ${issue.issue}`)
}

const assignIssue = (issue: CriticalIssue) => {
  ElMessage.info(`Assigning issue: ${issue.issue}`)
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Window Resize Handler ====================
const handleResize = () => {
  systemChart?.resize()
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
        initSystemChart()
      }, 100)
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  systemChart?.dispose()
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
.site-health-page {
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

/* Overall Health Card */
.overall-health-card {
  background: white;
  border-radius: 20px;
  padding: 24px 32px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.health-score-container {
  display: flex;
  align-items: center;
  gap: 48px;
  flex-wrap: wrap;
}

.health-score {
  flex-shrink: 0;
}

.score-text {
  text-align: center;
}

.score-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
}

.score-label {
  font-size: 12px;
  color: #909399;
}

.health-stats {
  display: flex;
  gap: 32px;
  flex-wrap: wrap;
}

.stat-item {
  text-align: center;
  min-width: 80px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

/* Sites Grid */
.sites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.site-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border-left: 4px solid transparent;
}

.site-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.site-card.status-healthy { border-left-color: #67c23a; }
.site-card.status-warning { border-left-color: #e6a23c; }
.site-card.status-critical { border-left-color: #f56c6c; }
.site-card.status-offline { border-left-color: #909399; }

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.site-name {
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
  margin-bottom: 4px;
}

.site-location {
  font-size: 12px;
  color: #909399;
}

.card-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.metric {
  text-align: center;
}

.metric-label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.metric-value {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: #1f2f3d;
}

.metric-sub {
  display: block;
  font-size: 10px;
  color: #c0c4cc;
  margin-top: 2px;
}

.card-progress {
  margin-bottom: 16px;
}

.progress-item {
  margin-bottom: 12px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #606266;
  margin-bottom: 6px;
}

.card-footer {
  display: flex;
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
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

/* Table Styles */
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

/* Comparison Section */
.comparison-section {
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

.comparison-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.comparison-card {
  background: #fafafa;
  border-radius: 14px;
  padding: 16px;
}

.comparison-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.comparison-header .site-name {
  font-weight: 600;
  font-size: 15px;
}

.comparison-header .site-score {
  font-size: 20px;
  font-weight: 700;
}

.comparison-header .site-score.status-healthy { color: #67c23a; }
.comparison-header .site-score.status-warning { color: #e6a23c; }
.comparison-header .site-score.status-critical { color: #f56c6c; }
.comparison-header .site-score.status-offline { color: #909399; }

.comparison-metrics {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comp-metric span {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
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