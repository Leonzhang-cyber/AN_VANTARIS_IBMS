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
          <span class="loading-title">Optimization Potential</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">AI-Powered Efficiency Intelligence</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="optimization-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><TrendCharts /></el-icon>
          Optimization Potential
        </h1>
        <div class="page-subtitle">AI-driven insights to maximize efficiency and reduce costs</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="runOptimizationScan">
          <el-icon><MagicStick /></el-icon> Run AI Scan
        </el-button>
        <el-button @click="exportReport">
          <el-icon><Download /></el-icon> Export Report
        </el-button>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Total Savings Hero Card -->
    <div class="savings-hero">
      <div class="savings-hero-bg"></div>
      <div class="savings-hero-content">
        <div class="hero-left">
          <div class="savings-badge">
            <span class="badge-icon">💰</span>
            Total Identified Savings Potential
          </div>
          <div class="savings-amount">
            <span class="currency">$</span>
            <span class="amount">{{ formatNumber(totalSavings) }}</span>
            <span class="period">/year</span>
          </div>
          <div class="savings-breakdown">
            <div class="breakdown-item">
              <span class="breakdown-label">Energy Savings</span>
              <span class="breakdown-value">${{ formatNumber(energySavings) }}</span>
            </div>
            <div class="breakdown-item">
              <span class="breakdown-label">Operational Savings</span>
              <span class="breakdown-value">${{ formatNumber(operationalSavings) }}</span>
            </div>
            <div class="breakdown-item">
              <span class="breakdown-label">Maintenance Savings</span>
              <span class="breakdown-value">${{ formatNumber(maintenanceSavings) }}</span>
            </div>
          </div>
        </div>
        <div class="hero-right">
          <div class="roi-container">
            <div class="roi-ring">
              <svg width="140" height="140" viewBox="0 0 140 140">
                <circle cx="70" cy="70" r="58" fill="none" stroke="#e2e8f0" stroke-width="10"/>
                <circle cx="70" cy="70" r="58" fill="none"
                        stroke="url(#roiGradient)"
                        stroke-width="10"
                        stroke-dasharray="364"
                        :stroke-dashoffset="364 - (roi / 100) * 364"
                        stroke-linecap="round"
                        transform="rotate(-90 70 70)"/>
                <defs>
                  <linearGradient id="roiGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:#22c55e"/>
                    <stop offset="100%" style="stop-color:#3b82f6"/>
                  </linearGradient>
                </defs>
              </svg>
              <div class="roi-label">
                <span class="roi-value">{{ roi }}%</span>
                <span class="roi-text">ROI</span>
              </div>
            </div>
            <div class="payback-period">Payback: {{ paybackPeriod }} months</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><Lightning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ potentialEnergySavings }}<span class="unit">MWh</span></div>
          <div class="stat-label">Potential Energy Savings</div>
          <div class="stat-trend up">↓ {{ energyReduction }}% reduction</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><PictureRounded /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ carbonReduction }}<span class="unit">tCO2e</span></div>
          <div class="stat-label">Carbon Reduction Potential</div>
          <div class="stat-trend up">🌱 {{ carbonPercent }}% of total emissions</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ pueImprovement }}<span class="unit">pts</span></div>
          <div class="stat-label">PUE Improvement Potential</div>
          <div class="stat-trend up">From {{ currentPue }} to {{ targetPue }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ operationalEfficiency }}<span class="unit">%</span></div>
          <div class="stat-label">Operational Efficiency Gain</div>
          <div class="stat-trend up">+{{ efficiencyGain }}% improvement</div>
        </div>
      </div>
    </div>

    <!-- Optimization Opportunities Section -->
    <div class="section-header">
      <h2 class="section-title">AI-Identified Optimization Opportunities</h2>
      <p class="section-subtitle">Prioritized recommendations based on impact and effort</p>
    </div>

    <div class="opportunities-grid">
      <div class="opportunity-card" v-for="(opp, idx) in opportunities" :key="idx" :class="opp.priority">
        <div class="card-header">
          <div class="opportunity-icon" :class="opp.priority">
            <el-icon><component :is="opp.icon" /></el-icon>
          </div>
          <div class="opportunity-info">
            <div class="opportunity-title">{{ opp.title }}</div>
            <div class="opportunity-category">{{ opp.category }}</div>
          </div>
          <div class="priority-badge" :class="opp.priority">
            {{ opp.priority === 'high' ? 'High Impact' : (opp.priority === 'medium' ? 'Medium Impact' : 'Low Impact') }}
          </div>
        </div>

        <div class="opportunity-description">{{ opp.description }}</div>

        <div class="impact-metrics">
          <div class="metric">
            <span class="metric-label">Annual Savings</span>
            <span class="metric-value">${{ formatNumber(opp.savings) }}</span>
          </div>
          <div class="metric">
            <span class="metric-label">Implementation Cost</span>
            <span class="metric-value">${{ formatNumber(opp.cost) }}</span>
          </div>
          <div class="metric">
            <span class="metric-label">Payback Period</span>
            <span class="metric-value">{{ opp.payback }} months</span>
          </div>
          <div class="metric">
            <span class="metric-label">ROI</span>
            <span class="metric-value">{{ opp.roi }}%</span>
          </div>
        </div>

        <div class="action-buttons">
          <el-button type="primary" size="small" @click="viewOpportunityDetail(opp)">View Details</el-button>
          <el-button size="small" @click="createActionPlan(opp)">Create Action Plan</el-button>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-section">
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot"></span>
            Savings by Category
          </div>
        </div>
        <div class="chart-container" ref="savingsChart"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot green"></span>
            Energy Efficiency Gap Analysis
          </div>
        </div>
        <div class="chart-container" ref="efficiencyChart"></div>
      </div>
    </div>

    <div class="charts-section">
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot orange"></span>
            Implementation Timeline
          </div>
        </div>
        <div class="chart-container" ref="timelineChart"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot purple"></span>
            Impact vs Effort Matrix
          </div>
        </div>
        <div class="chart-container" ref="matrixChart"></div>
      </div>
    </div>

    <!-- Recommendation Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Detailed Optimization Recommendations</span>
        <div class="table-actions">
          <el-input
              v-model="searchText"
              placeholder="Search recommendations..."
              style="width: 200px"
              clearable
              :prefix-icon="Search"
              size="small"
          />
          <el-button size="small" @click="exportTableData">
            <el-icon><Download /></el-icon> Export
          </el-button>
        </div>
      </div>
      <el-table :data="filteredRecommendations" stripe border style="width: 100%">
        <el-table-column prop="area" label="Area" />
        <el-table-column prop="recommendation" label="Recommendation" min-width="250" />
        <el-table-column prop="potentialSavings" label="Potential Savings" />
        <el-table-column prop="implementationCost" label="Implementation Cost" />
        <el-table-column prop="paybackPeriod" label="Payback Period" />
        <el-table-column prop="impact" label="Impact">
          <template #default="{ row }">
            <el-tag :type="row.impact === 'High' ? 'danger' : (row.impact === 'Medium' ? 'warning' : 'success')" size="small">
              {{ row.impact }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Not Started' ? 'info' : (row.status === 'In Progress' ? 'warning' : 'success')" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  TrendCharts, MagicStick, Download, Refresh, Lightning, PictureRounded,
  Clock, Cpu, Monitor, Connection, Search
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Analyzing optimization potential...')
const refreshing = ref(false)

const loadingMessages = [
  'Analyzing optimization potential...',
  'Calculating energy savings...',
  'Identifying efficiency gaps...',
  'Generating AI recommendations...',
  'Almost ready...'
]

// ==================== State ====================
const searchText = ref('')
const totalSavings = ref(1250000)
const energySavings = ref(750000)
const operationalSavings = ref(350000)
const maintenanceSavings = ref(150000)
const roi = ref(187)
const paybackPeriod = ref(6.5)
const potentialEnergySavings = ref(2850)
const energyReduction = ref(18.5)
const carbonReduction = ref(1250)
const carbonPercent = ref(15.2)
const pueImprovement = ref(0.12)
const currentPue = ref(1.48)
const targetPue = ref(1.36)
const operationalEfficiency = ref(24)
const efficiencyGain = ref(18)

// Opportunities data
const opportunities = ref([
  { title: 'Intelligent Cooling Optimization', category: 'Cooling', priority: 'high', icon: 'Cpu', description: 'AI-driven cooling setpoint optimization based on real-time IT load and weather data.', savings: 280000, cost: 85000, payback: 3.6, roi: 329, effort: 'Medium' },
  { title: 'Server Virtualization Consolidation', category: 'IT Infrastructure', priority: 'high', icon: 'Monitor', description: 'Consolidate underutilized servers to reduce power consumption and cooling needs.', savings: 320000, cost: 120000, payback: 4.5, roi: 267, effort: 'High' },
  { title: 'LED Lighting Retrofit', category: 'Lighting', priority: 'medium', icon: 'Lightning', description: 'Replace existing lighting with energy-efficient LED fixtures with motion sensors.', savings: 45000, cost: 28000, payback: 7.5, roi: 161, effort: 'Low' },
  { title: 'Free Cooling Implementation', category: 'Cooling', priority: 'high', icon: 'Connection', description: 'Utilize outside air for cooling during favorable weather conditions.', savings: 185000, cost: 95000, payback: 6.2, roi: 195, effort: 'Medium' },
  { title: 'UPS Efficiency Upgrade', category: 'Power', priority: 'medium', icon: 'Lightning', description: 'Replace legacy UPS units with high-efficiency modular UPS systems.', savings: 120000, cost: 180000, payback: 18, roi: 67, effort: 'High' },
  { title: 'Hot Aisle Containment', category: 'Cooling', priority: 'high', icon: 'Connection', description: 'Install hot aisle containment to improve cooling efficiency and reduce bypass air.', savings: 95000, cost: 45000, payback: 5.7, roi: 211, effort: 'Low' },
  { title: 'Power Metering & Monitoring', category: 'Power', priority: 'medium', icon: 'Monitor', description: 'Install granular power monitoring to identify waste and optimize distribution.', savings: 55000, cost: 65000, payback: 14.2, roi: 85, effort: 'Medium' },
  { title: 'Variable Speed Drives on Fans', category: 'Cooling', priority: 'low', icon: 'Cpu', description: 'Install VSDs on CRAC/CRAH fans for better airflow matching.', savings: 42000, cost: 38000, payback: 10.9, roi: 111, effort: 'Low' }
])

// Recommendations table data
const recommendations = ref([
  { area: 'Cooling', recommendation: 'Optimize cooling setpoints based on IT load', potentialSavings: '$120,000', implementationCost: '$25,000', paybackPeriod: '2.5 months', impact: 'High', status: 'Not Started' },
  { area: 'Cooling', recommendation: 'Implement free cooling during winter months', potentialSavings: '$85,000', implementationCost: '$15,000', paybackPeriod: '2.1 months', impact: 'High', status: 'In Progress' },
  { area: 'Power', recommendation: 'Replace legacy UPS with high-efficiency model', potentialSavings: '$95,000', implementationCost: '$180,000', paybackPeriod: '22.7 months', impact: 'Medium', status: 'Not Started' },
  { area: 'Power', recommendation: 'Install PDU-level power monitoring', potentialSavings: '$45,000', implementationCost: '$65,000', paybackPeriod: '17.3 months', impact: 'Medium', status: 'Not Started' },
  { area: 'IT', recommendation: 'Server virtualization and consolidation', potentialSavings: '$210,000', implementationCost: '$75,000', paybackPeriod: '4.3 months', impact: 'High', status: 'In Progress' },
  { area: 'IT', recommendation: 'Decommission zombie servers', potentialSavings: '$68,000', implementationCost: '$10,000', paybackPeriod: '1.8 months', impact: 'High', status: 'Completed' },
  { area: 'Lighting', recommendation: 'LED retrofit with occupancy sensors', potentialSavings: '$28,000', implementationCost: '$35,000', paybackPeriod: '15 months', impact: 'Low', status: 'Not Started' },
  { area: 'Lighting', recommendation: 'Implement daylight harvesting controls', potentialSavings: '$12,000', implementationCost: '$18,000', paybackPeriod: '18 months', impact: 'Low', status: 'Not Started' },
  { area: 'Facility', recommendation: 'Hot aisle containment installation', potentialSavings: '$75,000', implementationCost: '$45,000', paybackPeriod: '7.2 months', impact: 'High', status: 'Planned' },
  { area: 'Facility', recommendation: 'Variable speed drives on CRAC fans', potentialSavings: '$52,000', implementationCost: '$38,000', paybackPeriod: '8.8 months', impact: 'Medium', status: 'Not Started' }
])

const filteredRecommendations = computed(() => {
  if (!searchText.value) return recommendations.value
  const search = searchText.value.toLowerCase()
  return recommendations.value.filter(r =>
      r.recommendation.toLowerCase().includes(search) ||
      r.area.toLowerCase().includes(search)
  )
})

// ==================== Helper Functions ====================
const formatNumber = (num: number): string => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(0) + 'K'
  return num.toString()
}

const runOptimizationScan = () => {
  ElMessage.success('AI optimization scan initiated')
  setTimeout(() => {
    ElMessage.success('Scan complete - 8 opportunities identified')
  }, 2000)
}

const viewOpportunityDetail = (opp: any) => {
  ElMessage.info(`Viewing details for: ${opp.title}`)
}

const createActionPlan = (opp: any) => {
  ElMessage.success(`Action plan created for: ${opp.title}`)
}

const exportReport = () => {
  ElMessage.success('Export started')
  setTimeout(() => {
    ElMessage.success('Optimization report exported')
  }, 1500)
}

const exportTableData = () => {
  ElMessage.success('Table data exported')
}

const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

// ==================== Chart Refs ====================
const savingsChart = ref<HTMLElement | null>(null)
const efficiencyChart = ref<HTMLElement | null>(null)
const timelineChart = ref<HTMLElement | null>(null)
const matrixChart = ref<HTMLElement | null>(null)

let savingsChartInstance: echarts.ECharts | null = null
let efficiencyChartInstance: echarts.ECharts | null = null
let timelineChartInstance: echarts.ECharts | null = null
let matrixChartInstance: echarts.ECharts | null = null

// ==================== Initialize Charts ====================
const initSavingsChart = () => {
  if (!savingsChart.value) return
  if (savingsChartInstance) savingsChartInstance.dispose()

  savingsChartInstance = echarts.init(savingsChart.value)
  savingsChartInstance.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: 750000, name: 'Energy Savings', itemStyle: { color: '#3b82f6' } },
        { value: 350000, name: 'Operational Savings', itemStyle: { color: '#22c55e' } },
        { value: 150000, name: 'Maintenance Savings', itemStyle: { color: '#f59e0b' } }
      ],
      label: { show: true, formatter: '{b}: ${d}%' }
    }]
  })
}

const initEfficiencyChart = () => {
  if (!efficiencyChart.value) return
  if (efficiencyChartInstance) efficiencyChartInstance.dispose()

  efficiencyChartInstance = echarts.init(efficiencyChart.value)
  efficiencyChartInstance.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 30, bottom: 20 },
    xAxis: { type: 'category', data: ['Cooling', 'Power', 'IT', 'Lighting', 'Facility'] },
    yAxis: { type: 'value', name: 'Efficiency Gap (%)' },
    series: [{
      type: 'bar',
      data: [28, 22, 35, 45, 30],
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const colors = ['#ef4444', '#f59e0b', '#22c55e', '#3b82f6', '#8b5cf6']
          return colors[params.dataIndex]
        }
      },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initTimelineChart = () => {
  if (!timelineChart.value) return
  if (timelineChartInstance) timelineChartInstance.dispose()

  timelineChartInstance = echarts.init(timelineChart.value)
  timelineChartInstance.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 30, bottom: 20 },
    xAxis: { type: 'category', data: ['Q1', 'Q2', 'Q3', 'Q4'] },
    yAxis: { type: 'value', name: 'Cumulative Savings ($K)' },
    series: [{
      type: 'line',
      data: [125, 320, 580, 850],
      smooth: true,
      lineStyle: { color: '#22c55e', width: 3 },
      areaStyle: { opacity: 0.1 },
      symbol: 'circle',
      symbolSize: 8,
      label: { show: true, position: 'top', formatter: '${c}K' }
    }]
  })
}

const initMatrixChart = () => {
  if (!matrixChart.value) return
  if (matrixChartInstance) matrixChartInstance.dispose()

  matrixChartInstance = echarts.init(matrixChart.value)
  matrixChartInstance.setOption({
    tooltip: { trigger: 'item' },
    xAxis: { type: 'value', name: 'Implementation Effort', min: 0, max: 100 },
    yAxis: { type: 'value', name: 'Impact/Savings', min: 0, max: 100 },
    series: [{
      type: 'scatter',
      data: [
        [25, 85], [35, 90], [65, 75], [30, 80], [70, 60], [20, 70], [45, 65], [55, 55]
      ],
      symbolSize: 20,
      itemStyle: { color: (params: any) => {
          const impact = params.data[1]
          if (impact >= 80) return '#22c55e'
          if (impact >= 60) return '#f59e0b'
          return '#ef4444'
        } },
      label: {
        show: true,
        formatter: (params: any) => ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'][params.dataIndex],
        position: 'inside'
      }
    }]
  })
}

const resizeCharts = () => {
  [savingsChartInstance, efficiencyChartInstance, timelineChartInstance, matrixChartInstance].forEach(chart => {
    if (chart) chart.resize()
  })
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
        initSavingsChart()
        initEfficiencyChart()
        initTimelineChart()
        initMatrixChart()
      })
      window.addEventListener('resize', resizeCharts)
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
.optimization-page {
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

.page-subtitle {
  font-size: 14px;
  color: #64748b;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Savings Hero */
.savings-hero {
  position: relative;
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-radius: 28px;
  margin-bottom: 24px;
  overflow: hidden;
}

.savings-hero-bg {
  position: absolute;
  top: 0;
  right: 0;
  width: 50%;
  height: 100%;
  background: radial-gradient(ellipse at center, rgba(34, 197, 94, 0.1) 0%, transparent 70%);
}

.savings-hero-content {
  position: relative;
  padding: 32px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 30px;
}

.hero-left {
  flex: 1;
}

.savings-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 6px 14px;
  border-radius: 30px;
  font-size: 13px;
  color: #94a3b8;
  margin-bottom: 20px;
}

.savings-amount {
  margin-bottom: 16px;
}

.currency {
  font-size: 32px;
  font-weight: 600;
  color: #94a3b8;
}

.amount {
  font-size: 64px;
  font-weight: 800;
  color: white;
}

.period {
  font-size: 18px;
  color: #64748b;
  margin-left: 8px;
}

.savings-breakdown {
  display: flex;
  gap: 24px;
}

.breakdown-item {
  display: flex;
  flex-direction: column;
}

.breakdown-label {
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 4px;
}

.breakdown-value {
  font-size: 18px;
  font-weight: 700;
  color: white;
}

.hero-right {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.roi-container {
  text-align: center;
}

.roi-ring {
  position: relative;
  margin-bottom: 12px;
}

.roi-label {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.roi-value {
  font-size: 28px;
  font-weight: 800;
  color: white;
}

.roi-text {
  font-size: 12px;
  color: #94a3b8;
  display: block;
}

.payback-period {
  font-size: 14px;
  color: #4ade80;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.blue { background: #eef2ff; color: #3b82f6; }
.stat-icon.green { background: #dcfce7; color: #22c55e; }
.stat-icon.orange { background: #fef3c7; color: #f59e0b; }
.stat-icon.purple { background: #f3e8ff; color: #8b5cf6; }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.stat-value .unit {
  font-size: 12px;
  font-weight: normal;
  color: #64748b;
  margin-left: 2px;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

.stat-trend {
  font-size: 11px;
  margin-top: 6px;
}

.stat-trend.up { color: #22c55e; }

/* Section Header */
.section-header {
  margin-bottom: 24px;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.section-subtitle {
  font-size: 14px;
  color: #64748b;
}

/* Opportunities Grid */
.opportunities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.opportunity-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.opportunity-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.opportunity-card.high { border-left: 4px solid #ef4444; }
.opportunity-card.medium { border-left: 4px solid #f59e0b; }
.opportunity-card.low { border-left: 4px solid #22c55e; }

.card-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 16px;
}

.opportunity-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.opportunity-icon.high { background: #fee2e2; color: #ef4444; }
.opportunity-icon.medium { background: #fef3c7; color: #f59e0b; }
.opportunity-icon.low { background: #dcfce7; color: #22c55e; }

.opportunity-info {
  flex: 1;
}

.opportunity-title {
  font-weight: 700;
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 4px;
}

.opportunity-category {
  font-size: 12px;
  color: #64748b;
}

.priority-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
}

.priority-badge.high { background: #fee2e2; color: #dc2626; }
.priority-badge.medium { background: #fef3c7; color: #d97706; }
.priority-badge.low { background: #dcfce7; color: #16a34a; }

.opportunity-description {
  font-size: 13px;
  color: #475569;
  line-height: 1.5;
  margin-bottom: 16px;
}

.impact-metrics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
}

.metric {
  display: flex;
  flex-direction: column;
}

.metric-label {
  font-size: 11px;
  color: #64748b;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

/* Charts Section */
.charts-section {
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

.chart-container {
  height: 280px;
  width: 100%;
}

/* Table Container */
.table-container {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.table-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

/* Responsive */
@media (max-width: 1000px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-section {
    grid-template-columns: 1fr;
  }

  .opportunities-grid {
    grid-template-columns: 1fr;
  }

  .savings-hero-content {
    flex-direction: column;
    text-align: center;
  }

  .savings-breakdown {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .impact-metrics {
    grid-template-columns: 1fr;
  }

  .savings-hero-content {
    padding: 24px;
  }

  .amount {
    font-size: 48px;
  }
}
</style>