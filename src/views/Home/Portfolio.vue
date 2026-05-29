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

  <!-- Portfolio Dashboard Page Content -->
  <div v-else class="portfolio-dashboard-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>Portfolio Dashboard</h1>
        <p class="subtitle">Aggregated performance metrics across your entire facility portfolio</p>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="refreshData">Refresh</el-button>
        <el-button type="primary" :icon="Download" @click="exportReport">Export Report</el-button>
        <el-select v-model="portfolioFilter" placeholder="All Portfolios" size="default" style="width: 140px">
          <el-option label="All Portfolios" value="all" />
          <el-option label="North Region" value="north" />
          <el-option label="South Region" value="south" />
          <el-option label="East Region" value="east" />
          <el-option label="West Region" value="west" />
        </el-select>
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="kpi-cards">
      <div class="kpi-card total-sites">
        <div class="kpi-icon">
          <el-icon :size="32"><OfficeBuilding /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ totalSites }}</div>
          <div class="kpi-label">Total Sites</div>
        </div>
        <div class="kpi-trend positive">
          <el-icon><CaretTop /></el-icon>
          +2
        </div>
      </div>
      <div class="kpi-card total-area">
        <div class="kpi-icon">
          <el-icon :size="32"><Grid /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ totalArea }}<span class="unit">k m²</span></div>
          <div class="kpi-label">Total Area</div>
        </div>
      </div>
      <div class="kpi-card total-devices">
        <div class="kpi-icon">
          <el-icon :size="32"><Cpu /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ totalDevices }}</div>
          <div class="kpi-label">Connected Devices</div>
        </div>
        <div class="kpi-sub">{{ onlineDevices }} online</div>
      </div>
      <div class="kpi-card avg-health">
        <div class="kpi-icon">
          <el-icon :size="32"><TrendCharts /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ avgHealthScore }}%</div>
          <div class="kpi-label">Avg Site Health</div>
        </div>
        <el-progress :percentage="avgHealthScore" :color="getHealthColor(avgHealthScore)" :stroke-width="8" style="margin-top: 8px" />
      </div>
    </div>

    <!-- Portfolio Map / Site Distribution -->
    <div class="two-columns">
      <div class="chart-card">
        <div class="card-header">
          <h3>Site Distribution by Region</h3>
        </div>
        <div class="chart-container" ref="regionChartRef"></div>
      </div>
      <div class="chart-card">
        <div class="card-header">
          <h3>Portfolio Health Overview</h3>
        </div>
        <div class="chart-container" ref="healthChartRef"></div>
      </div>
    </div>

    <!-- Sites Table -->
    <div class="table-card">
      <div class="card-header">
        <h3>Site Portfolio Details</h3>
        <div class="header-filters">
          <el-select v-model="regionFilter" placeholder="All Regions" clearable size="default" style="width: 140px">
            <el-option label="All Regions" value="all" />
            <el-option label="North" value="North" />
            <el-option label="South" value="South" />
            <el-option label="East" value="East" />
            <el-option label="West" value="West" />
          </el-select>
          <el-select v-model="statusFilter" placeholder="All Status" clearable size="default" style="width: 130px">
            <el-option label="All Status" value="all" />
            <el-option label="Healthy" value="healthy" />
            <el-option label="Warning" value="warning" />
            <el-option label="Critical" value="critical" />
          </el-select>
          <el-input
              v-model="searchText"
              placeholder="Search sites..."
              :prefix-icon="Search"
              style="width: 200px"
              clearable
          />
        </div>
      </div>
      <el-table :data="paginatedSites" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="name" label="Site Name" min-width="180" />
        <el-table-column prop="region" label="Region" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.region }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="area" label="Area (m²)" width="120" align="right">
          <template #default="{ row }">
            {{ formatNumber(row.area) }}
          </template>
        </el-table-column>
        <el-table-column prop="devices" label="Devices" width="100" align="center">
          <template #default="{ row }">
            {{ row.devices }}
          </template>
        </el-table-column>
        <el-table-column prop="healthScore" label="Health Score" width="130" align="center" sortable>
          <template #default="{ row }">
            <div class="health-cell">
              <span :class="getHealthTextClass(row.healthScore)">{{ row.healthScore }}%</span>
              <el-progress :percentage="row.healthScore" :color="getHealthColor(row.healthScore)" :stroke-width="6" :show-text="false" style="width: 80px" />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="activeAlarms" label="Active Alarms" width="120" align="center" sortable>
          <template #default="{ row }">
            <span :class="row.activeAlarms > 0 ? 'text-danger' : 'text-success'">
              {{ row.activeAlarms }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="uptime" label="Uptime" width="100" align="center">
          <template #default="{ row }">
            {{ row.uptime }}%
          </template>
        </el-table-column>
        <el-table-column label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.healthScore)" size="small" effect="dark">
              {{ getStatusLabel(row.healthScore) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewSite(row)">View</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredSites.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Key Metrics Summary -->
    <div class="metrics-section">
      <div class="section-header">
        <h2>
          <el-icon><DataAnalysis /></el-icon>
          Portfolio Key Metrics
        </h2>
      </div>
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-title">Energy Consumption</span>
            <span class="metric-change positive">-5.2%</span>
          </div>
          <div class="metric-value">{{ totalEnergy }}<span class="unit"> kWh</span></div>
          <div class="metric-footer">vs last period</div>
        </div>
        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-title">Carbon Emissions</span>
            <span class="metric-change positive">-8.1%</span>
          </div>
          <div class="metric-value">{{ totalCarbon }}<span class="unit"> tCO₂</span></div>
          <div class="metric-footer">vs last period</div>
        </div>
        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-title">Energy Cost</span>
            <span class="metric-change negative">+3.2%</span>
          </div>
          <div class="metric-value">${{ totalCost }}<span class="unit">k</span></div>
          <div class="metric-footer">vs last period</div>
        </div>
        <div class="metric-card">
          <div class="metric-header">
            <span class="metric-title">SLA Compliance</span>
            <span class="metric-change positive">+2.4%</span>
          </div>
          <div class="metric-value">{{ slaCompliance }}%</div>
          <div class="metric-footer">vs target 95%</div>
        </div>
      </div>
    </div>

    <!-- Top Performing Sites -->
    <div class="top-sites-section">
      <div class="section-header">
        <h2>
          <el-icon><Medal /></el-icon>
          Top Performing Sites
        </h2>
        <el-button link type="primary" @click="viewAllSites">View All →</el-button>
      </div>
      <div class="top-sites-grid">
        <div v-for="(site, index) in topSites" :key="site.id" class="top-site-card">
          <div class="site-rank" :class="getRankClass(index)">
            #{{ index + 1 }}
          </div>
          <div class="site-content">
            <div class="site-name">{{ site.name }}</div>
            <div class="site-location">{{ site.region }}</div>
            <div class="site-stats">
              <div class="stat">
                <span>Health Score</span>
                <strong>{{ site.healthScore }}%</strong>
              </div>
              <div class="stat">
                <span>Uptime</span>
                <strong>{{ site.uptime }}%</strong>
              </div>
              <div class="stat">
                <span>Alarms</span>
                <strong>{{ site.activeAlarms }}</strong>
              </div>
            </div>
            <el-progress :percentage="site.healthScore" :color="getHealthColor(site.healthScore)" :stroke-width="6" />
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
  OfficeBuilding,
  Grid,
  Cpu,
  TrendCharts,
  Search,
  DataAnalysis,
  Medal,
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
interface PortfolioSite {
  id: number
  name: string
  region: string
  area: number
  devices: number
  healthScore: number
  activeAlarms: number
  uptime: number
}

// ==================== State ====================
const portfolioFilter = ref('all')
const regionFilter = ref('all')
const statusFilter = ref('all')
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const regionChartRef = ref<HTMLElement | null>(null)
const healthChartRef = ref<HTMLElement | null>(null)
let regionChart: echarts.ECharts | null = null
let healthChart: echarts.ECharts | null = null

// ==================== Mock Data ====================
const portfolioSites = ref<PortfolioSite[]>([
  { id: 1, name: 'Main Campus', region: 'North', area: 25000, devices: 245, healthScore: 94, activeAlarms: 2, uptime: 99.95 },
  { id: 2, name: 'Data Center East', region: 'East', area: 8500, devices: 189, healthScore: 78, activeAlarms: 5, uptime: 98.5 },
  { id: 3, name: 'West Office Tower', region: 'West', area: 18000, devices: 156, healthScore: 91, activeAlarms: 1, uptime: 99.2 },
  { id: 4, name: 'North Warehouse', region: 'North', area: 32000, devices: 89, healthScore: 62, activeAlarms: 12, uptime: 92.8 },
  { id: 5, name: 'South Satellite', region: 'South', area: 5000, devices: 45, healthScore: 45, activeAlarms: 18, uptime: 78.5 },
  { id: 6, name: 'East Manufacturing', region: 'East', area: 45000, devices: 210, healthScore: 85, activeAlarms: 3, uptime: 98.2 },
  { id: 7, name: 'West R&D Center', region: 'West', area: 12000, devices: 98, healthScore: 88, activeAlarms: 2, uptime: 99.1 },
  { id: 8, name: 'South Retail Hub', region: 'South', area: 8000, devices: 67, healthScore: 72, activeAlarms: 6, uptime: 96.5 }
])

// ==================== Computed Values ====================
const totalSites = computed(() => portfolioSites.value.length)
const totalArea = computed(() => Math.round(portfolioSites.value.reduce((sum, s) => sum + s.area, 0) / 1000))
const totalDevices = computed(() => portfolioSites.value.reduce((sum, s) => sum + s.devices, 0))
const onlineDevices = computed(() => Math.round(totalDevices.value * 0.96))
const avgHealthScore = computed(() => Math.round(portfolioSites.value.reduce((sum, s) => sum + s.healthScore, 0) / portfolioSites.value.length))
const totalEnergy = computed(() => '3.25M')
const totalCarbon = computed(() => 1250)
const totalCost = computed(() => 487)
const slaCompliance = computed(() => 92)

const filteredSites = computed(() => {
  let result = [...portfolioSites.value]
  if (regionFilter.value !== 'all') {
    result = result.filter(s => s.region === regionFilter.value)
  }
  if (statusFilter.value !== 'all') {
    if (statusFilter.value === 'healthy') {
      result = result.filter(s => s.healthScore >= 85)
    } else if (statusFilter.value === 'warning') {
      result = result.filter(s => s.healthScore >= 70 && s.healthScore < 85)
    } else if (statusFilter.value === 'critical') {
      result = result.filter(s => s.healthScore < 70)
    }
  }
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(s => s.name.toLowerCase().includes(search))
  }
  if (portfolioFilter.value !== 'all') {
    // Filter by portfolio region
    const filterMap: Record<string, string> = {
      north: 'North',
      south: 'South',
      east: 'East',
      west: 'West'
    }
    result = result.filter(s => s.region === filterMap[portfolioFilter.value])
  }
  return result
})

const paginatedSites = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredSites.value.slice(start, end)
})

const topSites = computed(() => {
  return [...portfolioSites.value]
      .sort((a, b) => b.healthScore - a.healthScore)
      .slice(0, 4)
})

// ==================== Helper Functions ====================
const formatNumber = (value: number): string => {
  return value.toLocaleString()
}

const getHealthColor = (score: number) => {
  if (score >= 85) return '#67c23a'
  if (score >= 70) return '#409eff'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
}

const getHealthTextClass = (score: number) => {
  if (score >= 85) return 'text-success'
  if (score >= 70) return 'text-primary'
  if (score >= 60) return 'text-warning'
  return 'text-danger'
}

const getStatusLabel = (score: number) => {
  if (score >= 85) return 'Healthy'
  if (score >= 70) return 'Warning'
  if (score >= 60) return 'Critical'
  return 'Severe'
}

const getStatusTagType = (score: number) => {
  if (score >= 85) return 'success'
  if (score >= 70) return 'warning'
  return 'danger'
}

const getRankClass = (index: number) => {
  if (index === 0) return 'rank-gold'
  if (index === 1) return 'rank-silver'
  if (index === 2) return 'rank-bronze'
  return ''
}

// ==================== Chart Functions ====================
const initRegionChart = () => {
  if (!regionChartRef.value) return
  if (regionChart) regionChart.dispose()

  regionChart = echarts.init(regionChartRef.value)

  const regionData = [
    { name: 'North', value: 2 },
    { name: 'South', value: 2 },
    { name: 'East', value: 2 },
    { name: 'West', value: 2 }
  ]

  regionChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} sites ({d}%)' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      type: 'pie', radius: '55%', center: ['50%', '50%'],
      data: regionData,
      label: { show: true, formatter: '{b}: {d}%' },
      itemStyle: {
        borderRadius: 8,
        borderColor: '#fff',
        borderWidth: 2,
        color: (params: any) => {
          const colors = ['#409eff', '#67c23a', '#e6a23c', '#8b5cf6']
          return colors[params.dataIndex]
        }
      }
    }]
  })
}

const initHealthChart = () => {
  if (!healthChartRef.value) return
  if (healthChart) healthChart.dispose()

  healthChart = echarts.init(healthChartRef.value)

  const statuses = ['Healthy (85-100)', 'Warning (70-84)', 'Critical (<70)']
  const counts = [4, 2, 2]

  healthChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '10%', right: '5%', top: '5%', bottom: '5%', containLabel: true },
    xAxis: { type: 'value', name: 'Number of Sites' },
    yAxis: { type: 'category', data: statuses },
    series: [{
      type: 'bar', data: counts,
      itemStyle: {
        borderRadius: [0, 4, 4, 0],
        color: (params: any) => {
          const colors = ['#67c23a', '#e6a23c', '#f56c6c']
          return colors[params.dataIndex]
        }
      },
      label: { show: true, position: 'right' }
    }]
  })
}

// ==================== Actions ====================
const refreshData = async () => {
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  ElMessage.success('Portfolio data refreshed')
  initRegionChart()
  initHealthChart()
  tableLoading.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting portfolio report...')
}

const viewSite = (site: PortfolioSite) => {
  ElMessage.info(`Viewing site: ${site.name}`)
}

const viewAllSites = () => {
  ElMessage.info('Viewing all sites')
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Window Resize Handler ====================
const handleResize = () => {
  regionChart?.resize()
  healthChart?.resize()
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
        initRegionChart()
        initHealthChart()
      }, 100)
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  regionChart?.dispose()
  healthChart?.dispose()
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
.portfolio-dashboard-page {
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

.kpi-card.total-sites .kpi-icon { background: #e8f4ff; color: #409eff; }
.kpi-card.total-area .kpi-icon { background: #e8f8f0; color: #67c23a; }
.kpi-card.total-devices .kpi-icon { background: #f0e8ff; color: #8b5cf6; }
.kpi-card.avg-health .kpi-icon { background: #fff7e8; color: #e6a23c; }

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
.health-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.text-success {
  color: #67c23a;
  font-weight: 500;
}

.text-primary {
  color: #409eff;
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

/* Metrics Section */
.metrics-section {
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

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.metric-card {
  background: #fafafa;
  border-radius: 14px;
  padding: 16px;
  text-align: center;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.metric-title {
  font-size: 13px;
  color: #909399;
}

.metric-change {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 20px;
}

.metric-change.positive {
  background: #e8f8f0;
  color: #67c23a;
}

.metric-change.negative {
  background: #ffe8e8;
  color: #f56c6c;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
  margin-bottom: 8px;
}

.metric-value .unit {
  font-size: 14px;
  font-weight: 400;
  color: #909399;
}

.metric-footer {
  font-size: 11px;
  color: #c0c4cc;
}

/* Top Sites Section */
.top-sites-section {
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.top-sites-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.top-site-card {
  background: #fafafa;
  border-radius: 14px;
  padding: 16px;
  position: relative;
  transition: all 0.2s;
}

.top-site-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.site-rank {
  position: absolute;
  top: -8px;
  left: -8px;
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  background: #f5f7fa;
  color: #606266;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.site-rank.rank-gold { background: #fff7e8; color: #e6a23c; }
.site-rank.rank-silver { background: #f0f0f0; color: #909399; }
.site-rank.rank-bronze { background: #fdf4ea; color: #cd9452; }

.site-content {
  margin-top: 8px;
}

.site-name {
  font-weight: 600;
  font-size: 15px;
  color: #1f2f3d;
  margin-bottom: 4px;
}

.site-location {
  font-size: 12px;
  color: #909399;
  margin-bottom: 12px;
}

.site-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}

.site-stats .stat {
  text-align: center;
}

.site-stats .stat span {
  display: block;
  font-size: 10px;
  color: #909399;
  margin-bottom: 2px;
}

.site-stats .stat strong {
  font-size: 14px;
  color: #1f2f3d;
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