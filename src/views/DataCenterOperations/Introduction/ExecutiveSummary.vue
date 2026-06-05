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
          <span class="loading-title">Executive Summary</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Data Center Intelligence Dashboard</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="executive-summary-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <div class="title-icon">
            <el-icon><DataBoard /></el-icon>
          </div>
          Executive Summary
        </h1>
        <div class="page-subtitle">High-level overview of data center performance and key metrics</div>
      </div>
      <div class="header-actions">
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 260px"
        />
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
        <el-button type="primary" @click="exportReport">
          <el-icon><Download /></el-icon> Export Report
        </el-button>
      </div>
    </div>

    <!-- Hero Score Card -->
    <div class="hero-card">
      <div class="hero-bg"></div>
      <div class="hero-content">
        <div class="hero-left">
          <div class="hero-badge">
            <span class="badge-icon">🏆</span>
            Overall Performance Score
          </div>
          <div class="hero-score">
            <span class="score-value">{{ overallScore }}</span>
            <span class="score-total">/100</span>
          </div>
          <div class="hero-rank">
            <span class="rank-label">Global Benchmark Ranking</span>
            <span class="rank-value">Top {{ globalRank }}%</span>
            <span class="rank-trend up">↑ 5% vs last quarter</span>
          </div>
        </div>
        <div class="hero-right">
          <div class="performance-gauge">
            <div class="gauge-ring">
              <svg width="140" height="140" viewBox="0 0 140 140">
                <circle cx="70" cy="70" r="58" fill="none" stroke="#e2e8f0" stroke-width="10"/>
                <circle cx="70" cy="70" r="58" fill="none"
                        stroke="url(#gaugeGradient)"
                        stroke-width="10"
                        stroke-dasharray="364"
                        :stroke-dashoffset="364 - (overallScore / 100) * 364"
                        stroke-linecap="round"
                        transform="rotate(-90 70 70)"/>
                <defs>
                  <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:#3b82f6"/>
                    <stop offset="50%" style="stop-color:#8b5cf6"/>
                    <stop offset="100%" style="stop-color:#06b6d4"/>
                  </linearGradient>
                </defs>
              </svg>
              <div class="gauge-label">Excellent</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Dashboard -->
    <div class="metrics-dashboard">
      <div class="metric-card">
        <div class="metric-header">
          <span class="metric-icon">⚡</span>
          <span class="metric-title">Power Usage</span>
        </div>
        <div class="metric-value">2.45<span class="unit">MW</span></div>
        <div class="metric-trend up">↑ 8% vs last month</div>
        <div class="metric-footer">Peak: 2.68 MW</div>
      </div>
      <div class="metric-card">
        <div class="metric-header">
          <span class="metric-icon">🌡️</span>
          <span class="metric-title">PUE</span>
        </div>
        <div class="metric-value">1.48</div>
        <div class="metric-trend down">↓ 0.03 vs last quarter</div>
        <div class="metric-footer">Target: 1.42</div>
      </div>
      <div class="metric-card">
        <div class="metric-header">
          <span class="metric-icon">💧</span>
          <span class="metric-title">WUE</span>
        </div>
        <div class="metric-value">1.25<span class="unit">L/kWh</span></div>
        <div class="metric-trend down">↓ 5% vs last year</div>
        <div class="metric-footer">Industry Avg: 1.82</div>
      </div>
      <div class="metric-card">
        <div class="metric-header">
          <span class="metric-icon">🌍</span>
          <span class="metric-title">Carbon Intensity</span>
        </div>
        <div class="metric-value">0.28<span class="unit">kg/kWh</span></div>
        <div class="metric-trend down">↓ 12% vs last year</div>
        <div class="metric-footer">Renewable: 65%</div>
      </div>
      <div class="metric-card">
        <div class="metric-header">
          <span class="metric-icon">🖥️</span>
          <span class="metric-title">IT Load</span>
        </div>
        <div class="metric-value">1.85<span class="unit">MW</span></div>
        <div class="metric-trend up">↑ 12% YoY</div>
        <div class="metric-footer">Utilization: 72%</div>
      </div>
      <div class="metric-card">
        <div class="metric-header">
          <span class="metric-icon">⏱️</span>
          <span class="metric-title">Uptime</span>
        </div>
        <div class="metric-value">99.995<span class="unit">%</span></div>
        <div class="metric-trend up">↑ 0.002% vs target</div>
        <div class="metric-footer">Downtime: 26 min/year</div>
      </div>
    </div>

    <!-- Charts Row 1 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot"></span>
            PUE Trend (Last 12 Months)
          </div>
        </div>
        <div class="chart-container" ref="pueTrendChart"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot green"></span>
            Energy Consumption by System
          </div>
        </div>
        <div class="chart-container" ref="energyChart"></div>
      </div>
    </div>

    <!-- Charts Row 2 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot orange"></span>
            Cost Breakdown
          </div>
        </div>
        <div class="chart-container" ref="costChart"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot purple"></span>
            Carbon Reduction Progress
          </div>
        </div>
        <div class="chart-container" ref="carbonChart"></div>
      </div>
    </div>

    <!-- Key Initiatives & Highlights -->
    <div class="highlights-card">
      <div class="card-header">
        <span class="card-title">📌 Key Initiatives & Highlights</span>
        <el-tag type="success" size="large">Q2 2024</el-tag>
      </div>
      <div class="highlights-grid">
        <div class="highlight-item">
          <div class="highlight-icon green">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="highlight-content">
            <div class="highlight-title">Cooling Efficiency Upgrade</div>
            <div class="highlight-desc">AI-driven cooling optimization reduced PUE by 0.08, saving $245K annually</div>
            <div class="highlight-progress">
              <el-progress :percentage="85" :stroke-width="6" color="#22c55e" />
            </div>
          </div>
        </div>
        <div class="highlight-item">
          <div class="highlight-icon blue">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="highlight-content">
            <div class="highlight-title">Renewable Energy Expansion</div>
            <div class="highlight-desc">Added 2MW solar capacity, now 65% of energy from renewable sources</div>
            <div class="highlight-progress">
              <el-progress :percentage="65" :stroke-width="6" color="#3b82f6" />
            </div>
          </div>
        </div>
        <div class="highlight-item">
          <div class="highlight-icon orange">
            <el-icon><Cpu /></el-icon>
          </div>
          <div class="highlight-content">
            <div class="highlight-title">Server Consolidation</div>
            <div class="highlight-desc">Virtualized 200+ servers, reducing power consumption by 180kW</div>
            <div class="highlight-progress">
              <el-progress :percentage="92" :stroke-width="6" color="#f59e0b" />
            </div>
          </div>
        </div>
        <div class="highlight-item">
          <div class="highlight-icon purple">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="highlight-content">
            <div class="highlight-title">UPS Replacement Program</div>
            <div class="highlight-desc">Replaced legacy UPS units, improving efficiency by 8%</div>
            <div class="highlight-progress">
              <el-progress :percentage="45" :stroke-width="6" color="#8b5cf6" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Financial Summary -->
    <div class="financial-card">
      <div class="card-header">
        <span class="card-title">💰 Financial Summary</span>
        <el-button size="small" type="primary" plain>View Details</el-button>
      </div>
      <div class="financial-grid">
        <div class="financial-item">
          <div class="financial-label">Total OPEX (Annual)</div>
          <div class="financial-value">$4.85M</div>
          <div class="financial-trend down">↓ 8.2% vs last year</div>
        </div>
        <div class="financial-item">
          <div class="financial-label">Energy Cost (Annual)</div>
          <div class="financial-value">$2.15M</div>
          <div class="financial-trend down">↓ 12.5% vs last year</div>
        </div>
        <div class="financial-item">
          <div class="financial-label">Maintenance Cost (Annual)</div>
          <div class="financial-value">$1.25M</div>
          <div class="financial-trend down">↓ 5.3% vs last year</div>
        </div>
        <div class="financial-item">
          <div class="financial-label">ROI on Efficiency Projects</div>
          <div class="financial-value">187%</div>
          <div class="financial-trend up">↑ 12% vs target</div>
        </div>
      </div>
    </div>

    <!-- Risk & Opportunities -->
    <div class="risk-card">
      <div class="card-header">
        <span class="card-title">⚠️ Risk & Opportunities</span>
      </div>
      <div class="risk-grid">
        <div class="risk-item high">
          <div class="risk-status">High</div>
          <div class="risk-title">Power Capacity Constraint</div>
          <div class="risk-desc">Data center approaching maximum power capacity. Expansion planning needed.</div>
        </div>
        <div class="risk-item medium">
          <div class="risk-status">Medium</div>
          <div class="risk-title">Cooling Infrastructure Age</div>
          <div class="risk-desc">CRAC units reaching end-of-life. Replacement scheduled for Q3.</div>
        </div>
        <div class="risk-item low">
          <div class="risk-status">Opportunity</div>
          <div class="risk-title">Free Cooling Potential</div>
          <div class="risk-desc">Weather data indicates 35% free cooling opportunity. Estimated savings: $180K/year.</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  DataBoard, Refresh, Download, CircleCheck, TrendCharts, Cpu, Warning
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading executive summary...')
const refreshing = ref(false)

const loadingMessages = [
  'Loading executive summary...',
  'Analyzing key metrics...',
  'Generating insights...',
  'Preparing dashboard...',
  'Almost ready...'
]

// ==================== State ====================
const dateRange = ref<string[]>([])
const overallScore = ref(87)
const globalRank = ref(12)

// Chart refs
const pueTrendChart = ref<HTMLElement | null>(null)
const energyChart = ref<HTMLElement | null>(null)
const costChart = ref<HTMLElement | null>(null)
const carbonChart = ref<HTMLElement | null>(null)

let pueTrendInstance: echarts.ECharts | null = null
let energyChartInstance: echarts.ECharts | null = null
let costChartInstance: echarts.ECharts | null = null
let carbonChartInstance: echarts.ECharts | null = null

// ==================== Helper Functions ====================
const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

const exportReport = () => {
  ElMessage.success('Export started')
  setTimeout(() => {
    ElMessage.success('Executive report exported')
  }, 1500)
}

// ==================== Charts ====================
const initPUETrendChart = () => {
  if (!pueTrendChart.value) return
  if (pueTrendInstance) pueTrendInstance.dispose()

  pueTrendInstance = echarts.init(pueTrendChart.value)
  pueTrendInstance.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 30, bottom: 20 },
    xAxis: { type: 'category', data: ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'] },
    yAxis: { type: 'value', name: 'PUE', min: 1.35, max: 1.65 },
    series: [{
      type: 'line',
      data: [1.58, 1.56, 1.55, 1.54, 1.53, 1.52, 1.51, 1.50, 1.49, 1.48, 1.47, 1.48],
      smooth: true,
      lineStyle: { color: '#3b82f6', width: 3 },
      areaStyle: { opacity: 0.1 },
      symbol: 'circle',
      symbolSize: 8,
      markPoint: { data: [{ type: 'min', name: 'Best' }] }
    }]
  })
}

const initEnergyChart = () => {
  if (!energyChart.value) return
  if (energyChartInstance) energyChartInstance.dispose()

  energyChartInstance = echarts.init(energyChart.value)
  energyChartInstance.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: 42, name: 'IT Equipment', itemStyle: { color: '#3b82f6' } },
        { value: 35, name: 'Cooling', itemStyle: { color: '#22c55e' } },
        { value: 12, name: 'Power Distribution', itemStyle: { color: '#f59e0b' } },
        { value: 8, name: 'Lighting', itemStyle: { color: '#8b5cf6' } },
        { value: 3, name: 'Other', itemStyle: { color: '#ec489a' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })
}

const initCostChart = () => {
  if (!costChart.value) return
  if (costChartInstance) costChartInstance.dispose()

  costChartInstance = echarts.init(costChart.value)
  costChartInstance.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 30, bottom: 20 },
    xAxis: { type: 'category', data: ['Energy', 'Maintenance', 'Labor', 'Software', 'Other'] },
    yAxis: { type: 'value', name: 'Cost ($K)', axisLabel: { formatter: (v: number) => '$' + v + 'K' } },
    series: [{
      type: 'bar',
      data: [2150, 1250, 850, 320, 280],
      itemStyle: { borderRadius: [4, 4, 0, 0], color: (params: any) => {
          const colors = ['#3b82f6', '#22c55e', '#f59e0b', '#8b5cf6', '#ec489a']
          return colors[params.dataIndex]
        } },
      label: { show: true, position: 'top', formatter: (p: any) => '$' + p.value + 'K' }
    }]
  })
}

const initCarbonChart = () => {
  if (!carbonChart.value) return
  if (carbonChartInstance) carbonChartInstance.dispose()

  carbonChartInstance = echarts.init(carbonChart.value)
  carbonChartInstance.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 60, right: 30, bottom: 20 },
    xAxis: { type: 'category', data: ['2020', '2021', '2022', '2023', '2024'] },
    yAxis: { type: 'value', name: 'Carbon Emissions (tCO2e)', axisLabel: { formatter: (v: number) => v + 'K' } },
    series: [{
      type: 'line',
      data: [12500, 11800, 11200, 10500, 9800],
      smooth: true,
      lineStyle: { color: '#22c55e', width: 3 },
      areaStyle: { opacity: 0.1 },
      symbol: 'circle',
      symbolSize: 8,
      label: { show: true, position: 'top', formatter: (p: any) => p.value + 'K' }
    }]
  })
}

const resizeCharts = () => {
  [pueTrendInstance, energyChartInstance, costChartInstance, carbonChartInstance].forEach(chart => {
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
        initPUETrendChart()
        initEnergyChart()
        initCostChart()
        initCarbonChart()
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
.executive-summary-page {
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
}

/* Hero Card */
.hero-card {
  position: relative;
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-radius: 28px;
  margin-bottom: 24px;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  top: 0;
  right: 0;
  width: 50%;
  height: 100%;
  background: radial-gradient(ellipse at center, rgba(59, 130, 246, 0.15) 0%, transparent 70%);
}

.hero-content {
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

.hero-badge {
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

.hero-score {
  margin-bottom: 12px;
}

.score-value {
  font-size: 64px;
  font-weight: 800;
  color: white;
}

.score-total {
  font-size: 24px;
  color: #64748b;
  margin-left: 4px;
}

.hero-rank {
  margin-bottom: 8px;
}

.rank-label {
  font-size: 13px;
  color: #94a3b8;
  margin-right: 12px;
}

.rank-value {
  font-size: 20px;
  font-weight: 700;
  color: #fbbf24;
  margin-right: 12px;
}

.rank-trend {
  font-size: 12px;
  color: #4ade80;
}

.rank-trend.up { color: #4ade80; }

.hero-right {
  display: flex;
  justify-content: center;
  align-items: center;
}

.performance-gauge {
  position: relative;
}

.gauge-ring {
  position: relative;
}

.gauge-label {
  position: absolute;
  bottom: -30px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 14px;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  padding: 4px 16px;
  border-radius: 30px;
  white-space: nowrap;
}

/* Metrics Dashboard */
.metrics-dashboard {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.metric-card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.metric-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.metric-icon {
  font-size: 20px;
}

.metric-title {
  font-size: 13px;
  font-weight: 500;
  color: #64748b;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.metric-value .unit {
  font-size: 12px;
  font-weight: normal;
  color: #64748b;
  margin-left: 2px;
}

.metric-trend {
  font-size: 11px;
  margin-bottom: 8px;
}

.metric-trend.up { color: #22c55e; }
.metric-trend.down { color: #ef4444; }

.metric-footer {
  font-size: 11px;
  color: #64748b;
  padding-top: 8px;
  border-top: 1px solid #eef2f8;
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

/* Highlights Card */
.highlights-card {
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
  flex-wrap: wrap;
  gap: 12px;
}

.card-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.highlights-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.highlight-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 16px;
  transition: all 0.2s;
}

.highlight-item:hover {
  background: #f1f5f9;
}

.highlight-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

.highlight-icon.green { background: #dcfce7; color: #22c55e; }
.highlight-icon.blue { background: #eef2ff; color: #3b82f6; }
.highlight-icon.orange { background: #fef3c7; color: #f59e0b; }
.highlight-icon.purple { background: #f3e8ff; color: #8b5cf6; }

.highlight-content {
  flex: 1;
}

.highlight-title {
  font-weight: 600;
  font-size: 15px;
  color: #1e293b;
  margin-bottom: 6px;
}

.highlight-desc {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 12px;
  line-height: 1.4;
}

/* Financial Card */
.financial-card {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
}

.financial-card .card-header {
  margin-bottom: 20px;
}

.financial-card .card-title {
  color: white;
}

.financial-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.financial-item {
  text-align: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  backdrop-filter: blur(10px);
}

.financial-label {
  font-size: 13px;
  color: #94a3b8;
  margin-bottom: 8px;
}

.financial-value {
  font-size: 28px;
  font-weight: 700;
  color: white;
  margin-bottom: 8px;
}

.financial-trend {
  font-size: 11px;
}

.financial-trend.down { color: #4ade80; }
.financial-trend.up { color: #f87171; }

/* Risk Card */
.risk-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.risk-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.risk-item {
  padding: 16px;
  border-radius: 16px;
  transition: all 0.2s;
}

.risk-item.high { background: #fef2f2; border-left: 4px solid #ef4444; }
.risk-item.medium { background: #fffbeb; border-left: 4px solid #f59e0b; }
.risk-item.low { background: #f0fdf4; border-left: 4px solid #22c55e; }

.risk-status {
  font-size: 11px;
  font-weight: 600;
  margin-bottom: 8px;
}

.risk-item.high .risk-status { color: #dc2626; }
.risk-item.medium .risk-status { color: #d97706; }
.risk-item.low .risk-status { color: #16a34a; }

.risk-title {
  font-weight: 700;
  font-size: 15px;
  color: #1e293b;
  margin-bottom: 8px;
}

.risk-desc {
  font-size: 13px;
  color: #64748b;
  line-height: 1.4;
}

/* Responsive */
@media (max-width: 1200px) {
  .metrics-dashboard {
    grid-template-columns: repeat(3, 1fr);
  }

  .financial-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .risk-grid {
    grid-template-columns: 1fr;
  }

  .highlights-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1000px) {
  .charts-row {
    grid-template-columns: 1fr;
  }

  .metrics-dashboard {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .metrics-dashboard {
    grid-template-columns: 1fr;
  }

  .financial-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-content {
    flex-direction: column;
    text-align: center;
    padding: 24px;
  }

  .hero-score {
    text-align: center;
  }

  .score-value {
    font-size: 48px;
  }
}
</style>