<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted, computed } from 'vue'
import {
  Search, DataAnalysis, TrendCharts, Clock, Warning,
  CircleCheck, Document, Sort, Download, RefreshRight,
  PieChart, Histogram, ArrowUp, ArrowDown
} from "@element-plus/icons-vue"
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading analytics engine...',
  'Processing fault data...',
  'Generating insights...'
]

// Date range for analytics
const dateRange = ref<[Date, Date]>([
  new Date(new Date().setDate(new Date().getDate() - 30)),
  new Date()
])

// Mock analytics data
const analyticsStats = ref({
  totalFaults: 347,
  avgResponseTime: 12.5,
  avgResolutionTime: 28.3,
  mtbf: 186.5,
  mttr: 4.2,
  recurrenceRate: 8.7,
  peakHour: '14:00-15:00',
  mostAffectedSite: 'Data Center A'
})

// Fault trend data (last 30 days)
const faultTrendData = ref([
  { date: '2024-12-18', count: 12, resolved: 10 },
  { date: '2024-12-19', count: 8, resolved: 7 },
  { date: '2024-12-20', count: 15, resolved: 13 },
  { date: '2024-12-21', count: 10, resolved: 9 },
  { date: '2024-12-22', count: 7, resolved: 7 },
  { date: '2024-12-23', count: 11, resolved: 10 },
  { date: '2024-12-24', count: 9, resolved: 8 },
  { date: '2024-12-25', count: 6, resolved: 6 },
  { date: '2024-12-26', count: 13, resolved: 11 },
  { date: '2024-12-27', count: 14, resolved: 13 },
  { date: '2024-12-28', count: 8, resolved: 8 },
  { date: '2024-12-29', count: 10, resolved: 9 },
  { date: '2024-12-30', count: 12, resolved: 11 },
  { date: '2024-12-31', count: 5, resolved: 5 },
  { date: '2025-01-01', count: 3, resolved: 3 },
  { date: '2025-01-02', count: 9, resolved: 8 },
  { date: '2025-01-03', count: 16, resolved: 14 },
  { date: '2025-01-04', count: 11, resolved: 10 },
  { date: '2025-01-05', count: 8, resolved: 7 },
  { date: '2025-01-06', count: 13, resolved: 12 },
  { date: '2025-01-07', count: 10, resolved: 9 },
  { date: '2025-01-08', count: 14, resolved: 13 },
  { date: '2025-01-09', count: 9, resolved: 8 },
  { date: '2025-01-10', count: 12, resolved: 11 },
  { date: '2025-01-11', count: 7, resolved: 7 },
  { date: '2025-01-12', count: 11, resolved: 10 },
  { date: '2025-01-13', count: 15, resolved: 13 },
  { date: '2025-01-14', count: 10, resolved: 9 },
  { date: '2025-01-15', count: 13, resolved: 12 },
  { date: '2025-01-16', count: 9, resolved: 8 }
])

// Fault by severity distribution
const severityDistribution = ref([
  { name: 'Critical', count: 28, color: '#F56C6C' },
  { name: 'Major', count: 52, color: '#E6A23C' },
  { name: 'Warning', count: 89, color: '#409EFF' },
  { name: 'Minor', count: 78, color: '#909399' },
  { name: 'Info', count: 100, color: '#67C23A' }
])

// Fault by device type
const deviceTypeFaults = ref([
  { name: 'HVAC', count: 86, percentage: 24.8 },
  { name: 'Power System', count: 72, percentage: 20.7 },
  { name: 'Controls/BMS', count: 54, percentage: 15.6 },
  { name: 'Security', count: 42, percentage: 12.1 },
  { name: 'Network', count: 38, percentage: 10.9 },
  { name: 'Lighting', count: 31, percentage: 8.9 },
  { name: 'Other', count: 24, percentage: 7.0 }
])

// Fault by site
const siteFaults = ref([
  { name: 'Data Center A', count: 98, trend: '+5%' },
  { name: 'Data Center B', count: 76, trend: '-2%' },
  { name: 'Central Plant', count: 54, trend: '+8%' },
  { name: 'Office Building', count: 67, trend: '+1%' },
  { name: 'Warehouse', count: 32, trend: '-5%' },
  { name: 'R&D Lab', count: 20, trend: '+12%' }
])

// Top recurring faults
const recurringFaults = ref([
  { pattern: 'Temperature sensor drift', occurrences: 18, device: 'AHU', trend: 'increasing' },
  { pattern: 'Communication timeout', occurrences: 15, device: 'BMS Controller', trend: 'stable' },
  { pattern: 'High vibration alarm', occurrences: 12, device: 'Chiller Pump', trend: 'decreasing' },
  { pattern: 'Power supply fluctuation', occurrences: 10, device: 'UPS', trend: 'increasing' },
  { pattern: 'Filter clogged', occurrences: 9, device: 'CRAC', trend: 'stable' }
])

// Peak hours data
const peakHoursData = ref([
  { hour: '00:00', count: 5 },
  { hour: '01:00', count: 3 },
  { hour: '02:00', count: 2 },
  { hour: '03:00', count: 2 },
  { hour: '04:00', count: 4 },
  { hour: '05:00', count: 3 },
  { hour: '06:00', count: 6 },
  { hour: '07:00', count: 8 },
  { hour: '08:00', count: 15 },
  { hour: '09:00', count: 22 },
  { hour: '10:00', count: 18 },
  { hour: '11:00', count: 16 },
  { hour: '12:00', count: 14 },
  { hour: '13:00', count: 19 },
  { hour: '14:00', count: 25 },
  { hour: '15:00', count: 23 },
  { hour: '16:00', count: 20 },
  { hour: '17:00', count: 17 },
  { hour: '18:00', count: 12 },
  { hour: '19:00', count: 9 },
  { hour: '20:00', count: 7 },
  { hour: '21:00', count: 6 },
  { hour: '22:00', count: 5 },
  { hour: '23:00', count: 4 }
])

// MTBF by device type
const mtbfData = ref([
  { name: 'UPS', mtbf: 1250, trend: 'up' },
  { name: 'Chiller', mtbf: 890, trend: 'down' },
  { name: 'AHU', mtbf: 720, trend: 'stable' },
  { name: 'VFD', mtbf: 650, trend: 'up' },
  { name: 'Controller', mtbf: 980, trend: 'stable' },
  { name: 'Sensor', mtbf: 450, trend: 'down' }
])

// Chart refs
const trendChartRef = ref<HTMLElement | null>(null)
const severityChartRef = ref<HTMLElement | null>(null)
const deviceChartRef = ref<HTMLElement | null>(null)
const siteChartRef = ref<HTMLElement | null>(null)
const peakHoursChartRef = ref<HTMLElement | null>(null)
const mtbfChartRef = ref<HTMLElement | null>(null)

let trendChart: echarts.ECharts | null = null
let severityChart: echarts.ECharts | null = null
let deviceChart: echarts.ECharts | null = null
let siteChart: echarts.ECharts | null = null
let peakHoursChart: echarts.ECharts | null = null
let mtbfChart: echarts.ECharts | null = null

// Initialize all charts
const initTrendChart = () => {
  if (trendChartRef.value) {
    if (trendChart) trendChart.dispose()

    trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: {
        data: ['New Faults', 'Resolved'],
        left: 'left',
        textStyle: { color: '#606266' }
      },
      grid: { left: '3%', right: '4%', top: '15%', bottom: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: faultTrendData.value.map(d => d.date.slice(5)),
        axisLabel: { rotate: 45, interval: 5 }
      },
      yAxis: { type: 'value', name: 'Number of Faults' },
      series: [
        {
          name: 'New Faults',
          type: 'line',
          data: faultTrendData.value.map(d => d.count),
          smooth: true,
          lineStyle: { color: '#F56C6C', width: 3 },
          areaStyle: { opacity: 0.1, color: '#F56C6C' },
          symbol: 'circle',
          symbolSize: 6
        },
        {
          name: 'Resolved',
          type: 'line',
          data: faultTrendData.value.map(d => d.resolved),
          smooth: true,
          lineStyle: { color: '#67C23A', width: 2 },
          symbol: 'diamond',
          symbolSize: 6
        }
      ]
    })
  }
}

const initSeverityChart = () => {
  if (severityChartRef.value) {
    if (severityChart) severityChart.dispose()

    severityChart = echarts.init(severityChartRef.value)
    severityChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} faults)' },
      legend: { orient: 'vertical', left: 'left', top: 'center' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        data: severityDistribution.value.map(s => ({ name: s.name, value: s.count, itemStyle: { color: s.color } })),
        label: { show: true, formatter: '{b}: {d}%' },
        emphasis: { scale: true }
      }]
    })
  }
}

const initDeviceChart = () => {
  if (deviceChartRef.value) {
    if (deviceChart) deviceChart.dispose()

    deviceChart = echarts.init(deviceChartRef.value)
    deviceChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '0%', right: '15%', top: '5%', bottom: '5%', containLabel: true },
      xAxis: { type: 'value', name: 'Number of Faults' },
      yAxis: { type: 'category', data: deviceTypeFaults.value.map(d => d.name), axisLabel: { fontWeight: 500 } },
      series: [{
        type: 'bar',
        data: deviceTypeFaults.value.map(d => d.count),
        itemStyle: { color: '#409EFF', borderRadius: [0, 4, 4, 0] },
        label: { show: true, position: 'right' }
      }]
    })
  }
}

const initSiteChart = () => {
  if (siteChartRef.value) {
    if (siteChart) siteChart.dispose()

    siteChart = echarts.init(siteChartRef.value)
    siteChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '3%', right: '4%', top: '5%', bottom: '5%', containLabel: true },
      xAxis: { type: 'category', data: siteFaults.value.map(s => s.name), axisLabel: { rotate: 30 } },
      yAxis: { type: 'value', name: 'Fault Count' },
      series: [{
        type: 'bar',
        data: siteFaults.value.map(s => s.count),
        itemStyle: {
          color: '#E6A23C',
          borderRadius: [4, 4, 0, 0],
          shadowColor: 'rgba(230, 162, 60, 0.3)',
          shadowBlur: 8
        },
        label: { show: true, position: 'top' }
      }]
    })
  }
}

const initPeakHoursChart = () => {
  if (peakHoursChartRef.value) {
    if (peakHoursChart) peakHoursChart.dispose()

    peakHoursChart = echarts.init(peakHoursChartRef.value)
    peakHoursChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '5%', right: '4%', top: '10%', bottom: '5%', containLabel: true },
      xAxis: { type: 'category', data: peakHoursData.value.map(h => h.hour), axisLabel: { rotate: 45, interval: 3 } },
      yAxis: { type: 'value', name: 'Fault Count' },
      series: [{
        type: 'line',
        data: peakHoursData.value.map(h => h.count),
        smooth: true,
        lineStyle: { color: '#909399', width: 2 },
        areaStyle: { opacity: 0.3, color: '#909399' },
        symbol: 'circle',
        symbolSize: 6
      }]
    })
  }
}

const initMtbfChart = () => {
  if (mtbfChartRef.value) {
    if (mtbfChart) mtbfChart.dispose()

    mtbfChart = echarts.init(mtbfChartRef.value)
    mtbfChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '0%', right: '15%', top: '5%', bottom: '5%', containLabel: true },
      xAxis: { type: 'value', name: 'MTBF (hours)' },
      yAxis: { type: 'category', data: mtbfData.value.map(m => m.name), axisLabel: { fontWeight: 500 } },
      series: [{
        type: 'bar',
        data: mtbfData.value.map(m => m.mtbf),
        itemStyle: {
          color: (params: any) => {
            const trend = mtbfData.value[params.dataIndex].trend
            return trend === 'up' ? '#67C23A' : trend === 'down' ? '#F56C6C' : '#409EFF'
          },
          borderRadius: [0, 4, 4, 0]
        },
        label: { show: true, position: 'right', formatter: '{c} hrs' }
      }]
    })
  }
}

const handleResize = () => {
  trendChart?.resize()
  severityChart?.resize()
  deviceChart?.resize()
  siteChart?.resize()
  peakHoursChart?.resize()
  mtbfChart?.resize()
}

watch(isLoaded, (loaded) => {
  if (loaded) {
    nextTick(() => {
      initTrendChart()
      initSeverityChart()
      initDeviceChart()
      initSiteChart()
      initPeakHoursChart()
      initMtbfChart()
      window.addEventListener('resize', handleResize)
    })
  }
})

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
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  severityChart?.dispose()
  deviceChart?.dispose()
  siteChart?.dispose()
  peakHoursChart?.dispose()
  mtbfChart?.dispose()
})

const refreshData = () => {
  ElMessage.info('Refreshing analytics data...')
  setTimeout(() => {
    ElMessage.success('Data refreshed successfully')
  }, 1000)
}

const exportReport = () => {
  ElMessage.success('Exporting report...')
}
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
          <span class="loading-title">Loading</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Fault Analytics Platform</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="fault-analytics">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Fault Analytics</h2>
        <p class="subtitle">Comprehensive fault data analysis and insights</p>
      </div>
      <div class="header-actions">
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            size="default"
            style="width: 260px"
        />
        <el-button type="primary" @click="refreshData">
          <el-icon><RefreshRight /></el-icon> Refresh
        </el-button>
        <el-button @click="exportReport">
          <el-icon><Download /></el-icon> Export
        </el-button>
      </div>
    </div>

    <!-- KPI Cards Row -->
    <div class="kpi-grid">
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-header">
          <span class="kpi-title">Total Faults</span>
          <el-icon class="kpi-icon-total"><Warning /></el-icon>
        </div>
        <div class="kpi-value">{{ analyticsStats.totalFaults }}</div>
        <div class="kpi-footer">Last 30 days</div>
      </el-card>
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-header">
          <span class="kpi-title">MTBF</span>
          <el-icon class="kpi-icon-mtbf"><TrendCharts /></el-icon>
        </div>
        <div class="kpi-value">{{ analyticsStats.mtbf }}h</div>
        <div class="kpi-footer">Mean Time Between Failures</div>
      </el-card>
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-header">
          <span class="kpi-title">MTTR</span>
          <el-icon class="kpi-icon-mttr"><Clock /></el-icon>
        </div>
        <div class="kpi-value">{{ analyticsStats.mttr }}h</div>
        <div class="kpi-footer">Mean Time To Repair</div>
      </el-card>
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-header">
          <span class="kpi-title">Recurrence Rate</span>
          <el-icon class="kpi-icon-recur"><CircleCheck /></el-icon>
        </div>
        <div class="kpi-value">{{ analyticsStats.recurrenceRate }}%</div>
        <div class="kpi-footer">Faults recurring within 30d</div>
      </el-card>
    </div>

    <!-- Trend Chart - Full Width -->
    <el-card class="analytics-card full-width" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Fault Trend Analysis (Last 30 Days)</span>
          <el-tag type="danger" size="small">Live</el-tag>
        </div>
      </template>
      <div ref="trendChartRef" class="trend-chart"></div>
    </el-card>

    <!-- Two Column Charts Row -->
    <div class="charts-row">
      <el-card class="analytics-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Faults by Severity</span>
            <el-icon><PieChart /></el-icon>
          </div>
        </template>
        <div ref="severityChartRef" class="chart"></div>
      </el-card>

      <el-card class="analytics-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Faults by Device Type</span>
            <el-icon><Histogram /></el-icon>
          </div>
        </template>
        <div ref="deviceChartRef" class="chart"></div>
      </el-card>
    </div>

    <!-- Second Row Charts -->
    <div class="charts-row">
      <el-card class="analytics-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Faults by Site</span>
            <el-icon><DataAnalysis /></el-icon>
          </div>
        </template>
        <div ref="siteChartRef" class="chart"></div>
      </el-card>

      <el-card class="analytics-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Peak Hours Analysis</span>
            <el-tag type="warning" size="small">Peak: {{ analyticsStats.peakHour }}</el-tag>
          </div>
        </template>
        <div ref="peakHoursChartRef" class="chart"></div>
      </el-card>
    </div>

    <!-- Third Row: MTBF + Recurring Faults -->
    <div class="charts-row">
      <el-card class="analytics-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>MTBF by Device Type</span>
            <el-tag type="success" size="small">Up ▲ / Down ▼</el-tag>
          </div>
        </template>
        <div ref="mtbfChartRef" class="chart"></div>
      </el-card>

      <el-card class="analytics-card recurring-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Top Recurring Fault Patterns</span>
            <el-tag type="danger" size="small">Needs Attention</el-tag>
          </div>
        </template>
        <el-table :data="recurringFaults" stripe style="width: 100%">
          <el-table-column prop="pattern" label="Fault Pattern"  align="center" />
          <el-table-column prop="device" label="Affected Device"   align="center" />
          <el-table-column prop="occurrences" label="Occurrences"  align="center">
            <template #default="{ row }">
              <el-tag :type="row.occurrences > 15 ? 'danger' : row.occurrences > 10 ? 'warning' : 'info'">
                {{ row.occurrences }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Trend" align="center">
            <template #default="{ row }">
              <span :class="row.trend">
                <el-icon v-if="row.trend === 'increasing'"><ArrowUp /></el-icon>
                <el-icon v-else-if="row.trend === 'decreasing'"><ArrowDown /></el-icon>
                <span v-else>→</span>
                {{ row.trend }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- Insights Footer -->
    <el-card class="insights-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>📊 Key Insights & Recommendations</span>
          <el-tag type="primary" size="small">AI Generated</el-tag>
        </div>
      </template>
      <div class="insights-grid">
        <div class="insight-item">
          <div class="insight-icon warning">⚠️</div>
          <div class="insight-content">
            <h4>Peak Fault Hours</h4>
            <p>Faults peak at {{ analyticsStats.peakHour }}. Consider adding additional monitoring during this period.</p>
          </div>
        </div>
        <div class="insight-item">
          <div class="insight-icon danger">🔥</div>
          <div class="insight-content">
            <h4>Recurring Issues</h4>
            <p>"Temperature sensor drift" accounts for {{ recurringFaults[0].occurrences }} occurrences. Schedule preventive maintenance for AHU sensors.</p>
          </div>
        </div>
        <div class="insight-item">
          <div class="insight-icon success">📈</div>
          <div class="insight-content">
            <h4>Improvement Opportunity</h4>
            <p>MTTR improved by 8% this month. Continue root cause analysis to further reduce resolution time.</p>
          </div>
        </div>
        <div class="insight-item">
          <div class="insight-icon info">🏢</div>
          <div class="insight-content">
            <h4>Site Focus</h4>
            <p>{{ analyticsStats.mostAffectedSite }} has the highest fault count. Recommend infrastructure review.</p>
          </div>
        </div>
      </div>
    </el-card>
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
.fault-analytics {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 28px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h2 {
  margin: 0 0 4px 0;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #303133, #606266);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

/* KPI Cards */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.kpi-card {
  border-radius: 20px;
  transition: all 0.3s ease;
}

.kpi-card:hover {
  transform: translateY(-4px);
}

.kpi-card :deep(.el-card__body) {
  padding: 20px;
}

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.kpi-title {
  font-size: 14px;
  color: #909399;
  font-weight: 500;
}

.kpi-icon-total { color: #F56C6C; font-size: 24px; }
.kpi-icon-mtbf { color: #409EFF; font-size: 24px; }
.kpi-icon-mttr { color: #E6A23C; font-size: 24px; }
.kpi-icon-recur { color: #67C23A; font-size: 24px; }

.kpi-value {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
  margin-bottom: 8px;
}

.kpi-footer {
  font-size: 12px;
  color: #C0C4CC;
}

/* Analytics Cards */
.analytics-card {
  border-radius: 20px;
  margin-bottom: 20px;
}

.analytics-card.full-width {
  margin-bottom: 20px;
}

.analytics-card :deep(.el-card__body) {
  padding: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 15px;
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.trend-chart {
  width: 100%;
  height: 380px;
}

.chart {
  width: 100%;
  height: 320px;
}

/* Recurring Card */
.recurring-card :deep(.el-card__body) {
  padding: 0;
}

.recurring-card :deep(.el-table) {
  border-radius: 0 0 20px 20px;
}

.increasing {
  color: #F56C6C;
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

.decreasing {
  color: #67C23A;
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

/* Insights Card */
.insights-card {
  border-radius: 20px;
}

.insights-card :deep(.el-card__body) {
  padding: 20px;
}

.insights-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.insight-item {
  display: flex;
  gap: 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 12px;
  transition: all 0.2s ease;
}

.insight-item:hover {
  background: #f0f1f3;
}

.insight-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.insight-icon.warning { background: rgba(230, 162, 60, 0.1); }
.insight-icon.danger { background: rgba(245, 108, 108, 0.1); }
.insight-icon.success { background: rgba(103, 194, 58, 0.1); }
.insight-icon.info { background: rgba(64, 158, 255, 0.1); }

.insight-content h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.insight-content p {
  margin: 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.4;
}

/* Responsive */
@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-row {
    grid-template-columns: 1fr;
  }

  .insights-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .fault-analytics {
    padding: 16px;
  }

  .kpi-grid {
    grid-template-columns: 1fr;
  }

  .header-actions {
    width: 100%;
    flex-direction: column;
  }

  .header-actions .el-date-picker,
  .header-actions .el-button {
    width: 100%;
  }

  .trend-chart {
    height: 280px;
  }

  .chart {
    height: 260px;
  }
}
</style>