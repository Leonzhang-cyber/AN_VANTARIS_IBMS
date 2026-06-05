<template>
  <!-- Loading Screen -->
  <div v-if="!isLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">
          <span class="loading-title">Data Center Dashboard</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Real-time Operations Intelligence</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="datacenter-dashboard">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <div class="title-icon">
            <el-icon><Monitor /></el-icon>
          </div>
          Data Center Dashboard
        </h1>
        <div class="page-subtitle">Real-time monitoring and operational insights</div>
      </div>
      <div class="header-actions">
        <div class="live-badge">
          <span class="live-dot"></span>
          LIVE DATA
        </div>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
        <el-button type="primary" @click="exportReport">
          <el-icon><Download /></el-icon> Export
        </el-button>
      </div>
    </div>

    <!-- KPI Cards Row 1 -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-icon blue">
          <el-icon><Lightning /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">2.45<span class="unit">MW</span></div>
          <div class="kpi-label">Total Power Load</div>
          <div class="kpi-trend up">↑ 8% vs yesterday</div>
        </div>
        <div class="kpi-chart">
          <div class="sparkline" ref="powerSparkline"></div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon green">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">1.48</div>
          <div class="kpi-label">PUE</div>
          <div class="kpi-trend down">↓ 0.02 vs target</div>
        </div>
        <div class="kpi-chart">
          <div class="sparkline" ref="pueSparkline"></div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon orange">
          <el-icon><Cpu /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">72<span class="unit">%</span></div>
          <div class="kpi-label">IT Load</div>
          <div class="kpi-trend up">↑ 5% vs yesterday</div>
        </div>
        <div class="kpi-chart">
          <div class="sparkline" ref="loadSparkline"></div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon purple">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">99.995<span class="unit">%</span></div>
          <div class="kpi-label">Uptime (30d)</div>
          <div class="kpi-trend up">↑ 0.002% vs target</div>
        </div>
        <div class="kpi-chart">
          <div class="sparkline" ref="uptimeSparkline"></div>
        </div>
      </div>
    </div>

    <!-- Facility Overview Section -->
    <div class="section-header">
      <h2 class="section-title">Facility Overview</h2>
      <div class="section-actions">
        <el-select v-model="siteFilter" placeholder="Select Site" size="small" style="width: 140px">
          <el-option label="All Sites" value="all" />
          <el-option label="Singapore DC" value="singapore" />
          <el-option label="Hong Kong DC" value="hongkong" />
          <el-option label="Tokyo DC" value="tokyo" />
        </el-select>
      </div>
    </div>

    <div class="facility-grid">
      <div class="facility-card" v-for="facility in filteredFacilities" :key="facility.name">
        <div class="facility-header">
          <div class="facility-name">{{ facility.name }}</div>
          <div class="facility-status" :class="facility.status">{{ facility.status }}</div>
        </div>
        <div class="facility-stats">
          <div class="facility-stat">
            <span class="stat-label">Power Usage</span>
            <span class="stat-value">{{ facility.power }} MW</span>
          </div>
          <div class="facility-stat">
            <span class="stat-label">PUE</span>
            <span class="stat-value" :class="getPUEClass(facility.pue)">{{ facility.pue }}</span>
          </div>
          <div class="facility-stat">
            <span class="stat-label">Temp</span>
            <span class="stat-value" :class="getTempClass(facility.temp)">{{ facility.temp }}°C</span>
          </div>
          <div class="facility-stat">
            <span class="stat-label">Humidity</span>
            <span class="stat-value">{{ facility.humidity }}%</span>
          </div>
        </div>
        <div class="facility-progress">
          <div class="progress-label">Capacity Utilization</div>
          <el-progress :percentage="facility.utilization" :stroke-width="8" :color="getUtilColor(facility.utilization)" />
        </div>
        <div class="facility-footer">
          <span><el-icon><Location /></el-icon> {{ facility.location }}</span>
          <span><el-icon><WarnTriangleFilled /></el-icon> {{ facility.alerts }} alerts</span>
        </div>
      </div>
    </div>

    <!-- Charts Section Row 1 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot"></span>
            Power & Cooling Trends
          </div>
          <div class="chart-legend">
            <span><span class="legend-dot power"></span> IT Load</span>
            <span><span class="legend-dot cooling"></span> Cooling</span>
          </div>
        </div>
        <div class="chart-container" ref="powerTrendChart"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot green"></span>
            PUE Performance
          </div>
        </div>
        <div class="chart-container" ref="puePerformanceChart"></div>
      </div>
    </div>

    <!-- Charts Section Row 2 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot orange"></span>
            Temperature Distribution
          </div>
        </div>
        <div class="chart-container" ref="tempHeatmapChart"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot purple"></span>
            Energy Cost Breakdown
          </div>
        </div>
        <div class="chart-container" ref="energyCostChart"></div>
      </div>
    </div>

    <!-- Alerts & Events -->
    <div class="alerts-card">
      <div class="card-header">
        <span class="card-title">
          <el-icon><Bell /></el-icon>
          Active Alerts & Events
        </span>
        <el-button size="small" type="primary" plain>View All</el-button>
      </div>
      <el-table :data="activeAlerts" stripe border style="width: 100%" size="small">
        <el-table-column prop="time" label="Time" width="160" />
        <el-table-column prop="severity" label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityType(row.severity)" size="small">{{ row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="Source" width="150" />
        <el-table-column prop="message" label="Message" min-width="300" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <span :class="row.status === 'active' ? 'status-active' : 'status-resolved'">{{ row.status }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Equipment Health -->
    <div class="health-card">
      <div class="card-header">
        <span class="card-title">Equipment Health Status</span>
        <el-button size="small" type="primary" plain>View All Equipment</el-button>
      </div>
      <div class="health-grid">
        <div class="health-item" v-for="eq in equipmentHealth" :key="eq.name">
          <div class="health-name">{{ eq.name }}</div>
          <div class="health-score">
            <el-progress
                :percentage="eq.health"
                :stroke-width="8"
                :color="getHealthColor(eq.health)"
                :show-text="true"
                :format="() => `${eq.health}%`"
            />
          </div>
          <div class="health-status" :class="getHealthStatus(eq.health)">{{ getHealthStatusText(eq.health) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Monitor, Refresh, Download, Lightning, TrendCharts, Cpu, Clock,
  Location,WarnTriangleFilled, Bell
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading dashboard data...')
const refreshing = ref(false)

const loadingMessages = [
  'Loading dashboard data...',
  'Fetching real-time metrics...',
  'Updating sensor readings...',
  'Almost ready...'
]

// ==================== State ====================
const siteFilter = ref('all')
let autoRefreshInterval: NodeJS.Timeout

// Sparkline refs
const powerSparkline = ref<HTMLElement | null>(null)
const pueSparkline = ref<HTMLElement | null>(null)
const loadSparkline = ref<HTMLElement | null>(null)
const uptimeSparkline = ref<HTMLElement | null>(null)

// Chart refs
const powerTrendChart = ref<HTMLElement | null>(null)
const puePerformanceChart = ref<HTMLElement | null>(null)
const tempHeatmapChart = ref<HTMLElement | null>(null)
const energyCostChart = ref<HTMLElement | null>(null)

let powerSparklineInstance: echarts.ECharts | null = null
let pueSparklineInstance: echarts.ECharts | null = null
let loadSparklineInstance: echarts.ECharts | null = null
let uptimeSparklineInstance: echarts.ECharts | null = null
let powerTrendInstance: echarts.ECharts | null = null
let puePerformanceInstance: echarts.ECharts | null = null
let tempHeatmapInstance: echarts.ECharts | null = null
let energyCostInstance: echarts.ECharts | null = null

// ==================== Data ====================
const facilities = ref([
  { name: 'Singapore DC', status: 'Operational', power: 2.45, pue: 1.48, temp: 24.5, humidity: 52, utilization: 78, location: 'Singapore', alerts: 2 },
  { name: 'Hong Kong DC', status: 'Operational', power: 1.85, pue: 1.52, temp: 25.2, humidity: 55, utilization: 65, location: 'Hong Kong', alerts: 1 },
  { name: 'Tokyo DC', status: 'Maintenance', power: 1.25, pue: 1.55, temp: 23.8, humidity: 48, utilization: 45, location: 'Tokyo', alerts: 3 },
  { name: 'London DC', status: 'Operational', power: 2.15, pue: 1.46, temp: 24.0, humidity: 50, utilization: 72, location: 'London', alerts: 0 },
  { name: 'New York DC', status: 'Operational', power: 2.85, pue: 1.49, temp: 24.8, humidity: 53, utilization: 82, location: 'New York', alerts: 1 },
  { name: 'Sydney DC', status: 'Warning', power: 1.65, pue: 1.58, temp: 27.5, humidity: 62, utilization: 58, location: 'Sydney', alerts: 4 }
])

const filteredFacilities = computed(() => {
  if (siteFilter.value === 'all') return facilities.value
  return facilities.value.filter(f =>
      f.location.toLowerCase() === siteFilter.value ||
      f.name.toLowerCase().includes(siteFilter.value)
  )
})

const activeAlerts = ref([
  { time: '2024-06-05 14:32:22', severity: 'Critical', source: 'UPS-01', message: 'Battery temperature exceeded threshold', status: 'active' },
  { time: '2024-06-05 13:15:07', severity: 'Warning', source: 'CRAC-02', message: 'High return air temperature', status: 'active' },
  { time: '2024-06-05 11:45:30', severity: 'Info', source: 'PDU-A01', message: 'Load balancing performed', status: 'resolved' },
  { time: '2024-06-05 10:20:15', severity: 'Warning', source: 'Generator-01', message: 'Fuel level below 30%', status: 'active' },
  { time: '2024-06-05 09:00:00', severity: 'Critical', source: 'Chiller-01', message: 'High pressure alarm', status: 'resolved' }
])

const equipmentHealth = ref([
  { name: 'UPS-01', health: 92 },
  { name: 'UPS-02', health: 88 },
  { name: 'CRAC-01', health: 78 },
  { name: 'CRAC-02', health: 85 },
  { name: 'PDU-A01', health: 95 },
  { name: 'Generator-01', health: 65 },
  { name: 'Chiller-01', health: 72 },
  { name: 'Transformer-01', health: 94 }
])

// ==================== Helper Functions ====================
const getPUEClass = (pue: number) => {
  if (pue <= 1.5) return 'good'
  if (pue <= 1.6) return 'warning'
  return 'critical'
}

const getTempClass = (temp: number) => {
  if (temp >= 18 && temp <= 27) return 'good'
  if (temp > 27 && temp <= 30) return 'warning'
  return 'critical'
}

const getUtilColor = (util: number) => {
  if (util <= 65) return '#22c55e'
  if (util <= 80) return '#f59e0b'
  return '#ef4444'
}

const getSeverityType = (severity: string) => {
  const map: Record<string, string> = { Critical: 'danger', Warning: 'warning', Info: 'info' }
  return map[severity] || 'info'
}

const getHealthColor = (health: number) => {
  if (health >= 80) return '#22c55e'
  if (health >= 60) return '#f59e0b'
  return '#ef4444'
}

const getHealthStatus = (health: number) => {
  if (health >= 80) return 'healthy'
  if (health >= 60) return 'warning'
  return 'critical'
}

const getHealthStatusText = (health: number) => {
  if (health >= 80) return 'Healthy'
  if (health >= 60) return 'Warning'
  return 'Critical'
}

const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

const exportReport = () => {
  ElMessage.success('Export started')
  setTimeout(() => {
    ElMessage.success('Dashboard report exported')
  }, 1500)
}

// ==================== Sparkline Charts ====================
const initSparkline = (container: HTMLElement | null, data: number[], color: string) => {
  if (!container) return
  const instance = echarts.init(container)
  instance.setOption({
    grid: { top: 5, left: 5, right: 5, bottom: 5, containLabel: true },
    xAxis: { show: false, type: 'category' },
    yAxis: { show: false },
    series: [{
      type: 'line',
      data: data,
      smooth: true,
      lineStyle: { color: color, width: 2 },
      symbol: 'none',
      areaStyle: { opacity: 0.2, color: color }
    }]
  })
  return instance
}

const initAllSparklines = () => {
  powerSparklineInstance = initSparkline(powerSparkline.value, [2.1, 2.2, 2.3, 2.4, 2.35, 2.45, 2.4, 2.5, 2.45], '#3b82f6')
  pueSparklineInstance = initSparkline(pueSparkline.value, [1.52, 1.51, 1.5, 1.49, 1.48, 1.47, 1.48], '#22c55e')
  loadSparklineInstance = initSparkline(loadSparkline.value, [65, 68, 70, 72, 71, 73, 72], '#f59e0b')
  uptimeSparklineInstance = initSparkline(uptimeSparkline.value, [99.99, 99.99, 99.995, 99.995, 99.995, 99.995, 99.995], '#8b5cf6')
}

// ==================== Main Charts ====================
const initPowerTrendChart = () => {
  if (!powerTrendChart.value) return
  if (powerTrendInstance) powerTrendInstance.dispose()

  powerTrendInstance = echarts.init(powerTrendChart.value)
  powerTrendInstance.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['IT Load', 'Cooling Load'], bottom: 0 },
    grid: { top: 30, left: 50, right: 30, bottom: 40 },
    xAxis: { type: 'category', data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'] },
    yAxis: { type: 'value', name: 'Power (kW)' },
    series: [
      { name: 'IT Load', type: 'line', data: [1850, 1820, 1780, 1950, 2100, 2050, 1900], smooth: true, lineStyle: { color: '#3b82f6', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Cooling Load', type: 'line', data: [650, 640, 620, 680, 750, 720, 670], smooth: true, lineStyle: { color: '#22c55e', width: 2 }, areaStyle: { opacity: 0.1 } }
    ]
  })
}

const initPuePerformanceChart = () => {
  if (!puePerformanceChart.value) return
  if (puePerformanceInstance) puePerformanceInstance.dispose()

  puePerformanceInstance = echarts.init(puePerformanceChart.value)
  puePerformanceInstance.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 30, bottom: 20 },
    xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'] },
    yAxis: { type: 'value', name: 'PUE', min: 1.4, max: 1.65 },
    series: [{
      type: 'line',
      data: [1.58, 1.56, 1.55, 1.52, 1.50, 1.48],
      smooth: true,
      lineStyle: { color: '#22c55e', width: 3 },
      areaStyle: { opacity: 0.1 },
      markLine: { data: [{ yAxis: 1.5, name: 'Target', lineStyle: { color: '#ef4444', type: 'dashed' } }] }
    }]
  })
}

const initTempHeatmapChart = () => {
  if (!tempHeatmapChart.value) return
  if (tempHeatmapInstance) tempHeatmapInstance.dispose()

  tempHeatmapInstance = echarts.init(tempHeatmapChart.value)
  tempHeatmapInstance.setOption({
    tooltip: { position: 'top' },
    grid: { top: 30, left: 30, right: 30, bottom: 20, containLabel: true },
    xAxis: { type: 'category', data: ['Row 1', 'Row 2', 'Row 3', 'Row 4', 'Row 5'] },
    yAxis: { type: 'category', data: ['Aisle A', 'Aisle B', 'Aisle C'] },
    visualMap: { min: 18, max: 30, calculable: true, orient: 'horizontal', left: 'center', bottom: 10, inRange: { color: ['#22c55e', '#f59e0b', '#ef4444'] } },
    series: [{
      type: 'heatmap',
      data: [
        [0, 0, 22.5], [1, 0, 24.2], [2, 0, 25.8], [3, 0, 24.5], [4, 0, 23.2],
        [0, 1, 23.5], [1, 1, 26.5], [2, 1, 28.2], [3, 1, 26.8], [4, 1, 24.5],
        [0, 2, 22.8], [1, 2, 23.5], [2, 2, 24.2], [3, 2, 23.5], [4, 2, 22.5]
      ],
      label: { show: true, formatter: (p: any) => p.data[2] + '°C' }
    }]
  })
}

const initEnergyCostChart = () => {
  if (!energyCostChart.value) return
  if (energyCostInstance) energyCostInstance.dispose()

  energyCostInstance = echarts.init(energyCostChart.value)
  energyCostInstance.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: 2150, name: 'Energy', itemStyle: { color: '#3b82f6' } },
        { value: 1250, name: 'Maintenance', itemStyle: { color: '#22c55e' } },
        { value: 850, name: 'Labor', itemStyle: { color: '#f59e0b' } },
        { value: 600, name: 'Other', itemStyle: { color: '#8b5cf6' } }
      ],
      label: { show: true, formatter: '{b}: ${d}%' }
    }]
  })
}

const resizeAllCharts = () => {
  const instances = [powerTrendInstance, puePerformanceInstance, tempHeatmapInstance, energyCostInstance,
    powerSparklineInstance, pueSparklineInstance, loadSparklineInstance, uptimeSparklineInstance]
  instances.forEach(instance => instance?.resize())
}

// ==================== Auto Refresh ====================
const startAutoRefresh = () => {
  autoRefreshInterval = setInterval(() => {
    // Simulate real-time data update
    refreshData()
  }, 30000)
}

// ==================== Loading Animation ====================
const startLoading = () => {
  let progress = 0
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 12
      loadingProgress.value = Math.min(progress, 90)
    }
  }, 100)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => {
        initAllSparklines()
        initPowerTrendChart()
        initPuePerformanceChart()
        initTempHeatmapChart()
        initEnergyCostChart()
      })
      window.addEventListener('resize', resizeAllCharts)
      startAutoRefresh()
    }, 500)
  }, 2200)
}

onMounted(() => {
  startLoading()
})
</script>

<style scoped>
* {
  scrollbar-width: thin;
}
*::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
*::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}
*::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

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
.spinner-ring:nth-child(4) { border-left-color: #ec489a; animation-delay: 0.6s; width: 20%; height: 20%; top: 40%; left: 40%; }

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

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

/* ==================== Main Page ==================== */
.datacenter-dashboard {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 24px;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.title-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.live-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: #fee2e2;
  border-radius: 30px;
  font-size: 12px;
  font-weight: 600;
  color: #dc2626;
}

.live-dot {
  width: 8px;
  height: 8px;
  background: #dc2626;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

/* KPI Cards */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.kpi-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.kpi-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.kpi-icon.blue { background: #eef2ff; color: #3b82f6; }
.kpi-icon.green { background: #dcfce7; color: #22c55e; }
.kpi-icon.orange { background: #fef3c7; color: #f59e0b; }
.kpi-icon.purple { background: #f3e8ff; color: #8b5cf6; }

.kpi-info {
  flex: 1;
  margin-left: 16px;
}

.kpi-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.kpi-value .unit {
  font-size: 12px;
  font-weight: normal;
  color: #64748b;
  margin-left: 2px;
}

.kpi-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

.kpi-trend {
  font-size: 11px;
  margin-top: 6px;
}

.kpi-trend.up { color: #22c55e; }
.kpi-trend.down { color: #ef4444; }

.kpi-chart {
  width: 80px;
  height: 40px;
}

.sparkline {
  width: 100%;
  height: 100%;
}

/* Section Header */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

/* Facility Grid */
.facility-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.facility-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.facility-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.facility-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.facility-name {
  font-weight: 700;
  font-size: 16px;
  color: #1e293b;
}

.facility-status {
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 20px;
}

.facility-status.Operational { background: #dcfce7; color: #16a34a; }
.facility-status.Maintenance { background: #fef3c7; color: #d97706; }
.facility-status.Warning { background: #fee2e2; color: #dc2626; }

.facility-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
}

.facility-stat {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 11px;
  color: #64748b;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.stat-value.good { color: #22c55e; }
.stat-value.warning { color: #f59e0b; }
.stat-value.critical { color: #ef4444; }

.facility-progress {
  margin-bottom: 16px;
}

.progress-label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 6px;
}

.facility-footer {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #64748b;
  padding-top: 12px;
  border-top: 1px solid #eef2f8;
}

.facility-footer span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

/* Charts Row */
.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.title-dot {
  width: 8px;
  height: 8px;
  background: #3b82f6;
  border-radius: 50%;
}

.title-dot.green { background: #22c55e; }
.title-dot.orange { background: #f59e0b; }
.title-dot.purple { background: #8b5cf6; }

.chart-legend {
  display: flex;
  gap: 16px;
  font-size: 12px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 4px;
}

.legend-dot.power { background: #3b82f6; }
.legend-dot.cooling { background: #22c55e; }

.chart-container {
  height: 280px;
  width: 100%;
}

/* Alerts Card */
.alerts-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.status-active { color: #f59e0b; font-weight: 500; }
.status-resolved { color: #22c55e; font-weight: 500; }

/* Health Card */
.health-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.health-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.health-item {
  padding: 16px;
  background: #f8fafc;
  border-radius: 16px;
}

.health-name {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
  margin-bottom: 12px;
}

.health-score {
  margin-bottom: 8px;
}

.health-status {
  font-size: 12px;
  font-weight: 500;
}

.health-status.healthy { color: #22c55e; }
.health-status.warning { color: #f59e0b; }
.health-status.critical { color: #ef4444; }

/* Responsive */
@media (max-width: 1000px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-row {
    grid-template-columns: 1fr;
  }

  .facility-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .kpi-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .facility-stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .health-grid {
    grid-template-columns: 1fr;
  }
}
</style>