<template>
  <!-- Loading 页面 -->
  <div v-if="!isBackgroundLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">
          <span class="loading-title">Loading Wind Energy</span>
          <span class="loading-dots">...</span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Initializing Wind Power System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Page -->
  <div v-else class="wind-energy-page">
    <!-- Left Panel -->
    <div class="left-panel">
      <!-- Page Title -->
      <div class="page-header">
        <h1 class="page-title">Wind Energy Analytics</h1>
      </div>

      <!-- Charts Container - Vertical 4 equal sections -->
      <div class="charts-container">
        <div class="chart-item">
          <div class="chart-header">
            <span class="chart-icon">📈</span>
            <span class="chart-title">Power Output Trend</span>
            <el-tag size="small" type="success">24h</el-tag>
          </div>
          <div ref="powerTrendChart" class="chart-box"></div>
        </div>

        <div class="chart-item">
          <div class="chart-header">
            <span class="chart-icon">🌬️</span>
            <span class="chart-title">Wind Speed Variation</span>
            <el-tag size="small" type="info">Weekly</el-tag>
          </div>
          <div ref="windSpeedChart" class="chart-box"></div>
        </div>

        <div class="chart-item">
          <div class="chart-header">
            <span class="chart-icon">🎯</span>
            <span class="chart-title">Wind Direction Distribution</span>
            <el-tag size="small" type="warning">Live</el-tag>
          </div>
          <div ref="windDirectionChart" class="chart-box"></div>
        </div>

        <div class="chart-item">
          <div class="chart-header">
            <span class="chart-icon">⚡</span>
            <span class="chart-title">Generation vs Capacity</span>
            <el-tag size="small" type="primary">Monthly</el-tag>
          </div>
          <div ref="generationChart" class="chart-box"></div>
        </div>
      </div>
    </div>

    <!-- Right Panel -->
    <div class="right-panel">
      <!-- Image Container -->
      <div class="image-container">
        <el-image
            src="https://aegisnx.com/wp-content/uploads/2026/05/1778317798669.png"
            fit="cover"
            class="wind-image"
        />
        <div class="image-overlay"></div>
      </div>

      <!-- Data Fields Container - Two rows, each row with max cards -->
      <div class="data-fields-container">
        <!-- Row 1 -->
        <div class="data-row">
          <div class="data-field-card">
            <div class="field-icon">🌬️</div>
            <div class="field-info">
              <span class="field-label">Current Power</span>
              <span class="field-value">{{ formatNumber(currentPower) }} <span class="field-unit">kW</span></span>
              <span class="field-trend up">↑ {{ powerTrend }}%</span>
            </div>
          </div>

          <div class="data-field-card">
            <div class="field-icon">⚡</div>
            <div class="field-info">
              <span class="field-label">Today Generation</span>
              <span class="field-value">{{ formatNumber(todayGeneration) }} <span class="field-unit">kWh</span></span>
              <span class="field-trend up">↑ {{ generationTrend }}%</span>
            </div>
          </div>

          <div class="data-field-card">
            <div class="field-icon">💨</div>
            <div class="field-info">
              <span class="field-label">Wind Speed</span>
              <span class="field-value">{{ windSpeed }} <span class="field-unit">m/s</span></span>
              <span class="field-trend">{{ windTrend === 'up' ? '↑' : '↓' }} {{ windSpeedChange }}%</span>
            </div>
          </div>

          <div class="data-field-card">
            <div class="field-icon">🧭</div>
            <div class="field-info">
              <span class="field-label">Wind Direction</span>
              <span class="field-value">{{ windDirection }}°</span>
              <span class="field-unit">{{ windDirectionText }}</span>
            </div>
          </div>
        </div>

        <!-- Row 2 -->
        <div class="data-row">
          <div class="data-field-card">
            <div class="field-icon">💰</div>
            <div class="field-info">
              <span class="field-label">Revenue Today</span>
              <span class="field-value">${{ formatNumber(revenueToday) }}<span class="field-unit">k</span></span>
              <span class="field-trend up">↑ {{ revenueTrend }}%</span>
            </div>
          </div>

          <div class="data-field-card">
            <div class="field-icon">🌿</div>
            <div class="field-info">
              <span class="field-label">CO₂ Saved</span>
              <span class="field-value">{{ formatNumber(co2Saved) }} <span class="field-unit">tons</span></span>
              <span class="field-trend up">↑ {{ co2Trend }}%</span>
            </div>
          </div>

          <div class="data-field-card">
            <div class="field-icon">📊</div>
            <div class="field-info">
              <span class="field-label">Capacity Factor</span>
              <span class="field-value">{{ capacityFactor }}<span class="field-unit">%</span></span>
              <span class="field-trend">{{ cfTrend === 'up' ? '↑' : '↓' }} {{ cfChange }}%</span>
            </div>
          </div>

          <div class="data-field-card">
            <div class="field-icon">🔄</div>
            <div class="field-info">
              <span class="field-label">Rotor Speed</span>
              <span class="field-value">{{ rotorRpm }} <span class="field-unit">rpm</span></span>
              <span class="field-trend up">↑ {{ rotorTrend }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'

// ==================== Loading State ====================
const isBackgroundLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing assets...')

// ==================== Reactive Data ====================
const currentPower = ref(2846)
const powerTrend = ref(8.2)
const todayGeneration = ref(68420)
const generationTrend = ref(12.5)
const windSpeed = ref(7.8)
const windTrend = ref('up')
const windSpeedChange = ref(5.2)
const windDirection = ref(245)
const windDirectionText = ref('WSW')
const revenueToday = ref(8.42)
const revenueTrend = ref(10.3)
const co2Saved = ref(48.6)
const co2Trend = ref(15.2)
const capacityFactor = ref(42.6)
const cfTrend = ref('up')
const cfChange = ref(3.8)
const rotorRpm = ref(14.2)
const rotorTrend = ref(3.5)

// Chart Refs
const powerTrendChart = ref(null)
const windSpeedChart = ref(null)
const windDirectionChart = ref(null)
const generationChart = ref(null)
let powerChart = null
let windChart = null
let directionChart = null
let generationChartIns = null

// Timers
let dataInterval = null
let chartInterval = null

// Loading Messages
const loadingMessages = [
  'Preparing assets...',
  'Loading wind data...',
  'Initializing turbines...',
  'Establishing connection...',
  'Starting dashboard...',
  'Almost ready...'
]

// Preload Background Image
const preloadBackground = () => new Promise((resolve) => {
  const img = new Image()
  img.src = 'https://aegisnx.com/wp-content/uploads/2026/05/1778317798669.png'
  let progress = 0
  let msgIdx = 0

  const msgInterval = setInterval(() => {
    if (msgIdx < loadingMessages.length - 1) {
      loadingMessage.value = loadingMessages[++msgIdx]
    }
  }, 800)

  const progInterval = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 10
      loadingProgress.value = Math.min(progress, 90)
    }
  }, 100)

  img.onload = () => {
    clearInterval(msgInterval)
    clearInterval(progInterval)
    loadingMessage.value = 'Ready!'
    loadingProgress.value = 100
    setTimeout(resolve, 500)
  }

  img.onerror = () => {
    clearInterval(msgInterval)
    clearInterval(progInterval)
    loadingProgress.value = 100
    setTimeout(resolve, 300)
  }
})

// Helper Functions
const formatNumber = (num) => {
  return num.toLocaleString()
}

// Update Real-time Data
const updateRealTimeData = () => {
  currentPower.value = Math.floor(2600 + Math.random() * 500)
  powerTrend.value = (5 + Math.random() * 8).toFixed(1)
  windSpeed.value = (5 + Math.random() * 5).toFixed(1)
  windDirection.value = Math.floor(0 + Math.random() * 360)
  const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
  windDirectionText.value = directions[Math.floor(windDirection.value / 22.5)]
  todayGeneration.value = 65000 + Math.floor(Math.random() * 8000)
  revenueToday.value = (7.5 + Math.random() * 2).toFixed(2)
  co2Saved.value = (42 + Math.random() * 12).toFixed(1)
  capacityFactor.value = (38 + Math.random() * 12).toFixed(1)
  rotorRpm.value = (12 + Math.random() * 5).toFixed(1)
  rotorTrend.value = (2 + Math.random() * 5).toFixed(1)
}

// Initialize Charts
const initCharts = () => {
  // Power Output Trend Chart
  if (powerTrendChart.value) {
    powerChart = echarts.init(powerTrendChart.value)
    powerChart.setOption({
      tooltip: { trigger: 'axis', backgroundColor: 'rgba(0,0,0,0.7)' },
      grid: { left: '8%', right: '5%', top: 20, bottom: 10, containLabel: true },
      xAxis: { type: 'category', data: ['00', '04', '08', '12', '16', '20', '24'], axisLabel: { color: '#94a3b8', fontSize: 10 }, axisLine: { lineStyle: { color: '#334155' } } },
      yAxis: { type: 'value', name: 'kW', nameTextStyle: { color: '#64748b', fontSize: 10 }, axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: '#1e293b' } } },
      series: [{ data: [42, 38, 56, 78, 82, 68, 45], type: 'line', smooth: true, lineStyle: { width: 2, color: '#10b981' }, areaStyle: { color: 'rgba(16,185,129,0.1)' }, symbol: 'circle', symbolSize: 5 }]
    })
  }

  // Wind Speed Variation Chart
  if (windSpeedChart.value) {
    windChart = echarts.init(windSpeedChart.value)
    windChart.setOption({
      tooltip: { trigger: 'axis', backgroundColor: 'rgba(0,0,0,0.7)' },
      grid: { left: '8%', right: '5%', top: 20, bottom: 10, containLabel: true },
      xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], axisLabel: { color: '#94a3b8', fontSize: 10 }, axisLine: { lineStyle: { color: '#334155' } } },
      yAxis: { type: 'value', name: 'm/s', nameTextStyle: { color: '#64748b', fontSize: 10 }, axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: '#1e293b' } } },
      series: [{ data: [5.2, 6.1, 7.4, 8.2, 7.8, 6.5, 5.8], type: 'bar', barWidth: '50%', itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#06b6d4' }, { offset: 1, color: '#3b82f6' }]), borderRadius: [4, 4, 0, 0] } }]
    })
  }

  // Wind Direction Rose Chart
  if (windDirectionChart.value) {
    directionChart = echarts.init(windDirectionChart.value)
    directionChart.setOption({
      tooltip: { trigger: 'item' },
      legend: { show: false },
      series: [{
        type: 'pie',
        radius: ['45%', '70%'],
        data: [
          { value: 35, name: 'N', itemStyle: { color: '#f59e0b' } },
          { value: 28, name: 'NE', itemStyle: { color: '#10b981' } },
          { value: 42, name: 'E', itemStyle: { color: '#3b82f6' } },
          { value: 38, name: 'SE', itemStyle: { color: '#8b5cf6' } },
          { value: 25, name: 'S', itemStyle: { color: '#ec489a' } },
          { value: 32, name: 'SW', itemStyle: { color: '#06b6d4' } },
          { value: 45, name: 'W', itemStyle: { color: '#f97316' } },
          { value: 30, name: 'NW', itemStyle: { color: '#14b8a6' } }
        ],
        label: { show: true, color: '#94a3b8', fontSize: 10, formatter: '{b}' },
        labelLine: { length: 5, length2: 5 }
      }]
    })
  }

  // Generation vs Capacity Chart
  if (generationChart.value) {
    generationChartIns = echarts.init(generationChart.value)
    generationChartIns.setOption({
      tooltip: { trigger: 'axis', backgroundColor: 'rgba(0,0,0,0.7)' },
      grid: { left: '8%', right: '5%', top: 20, bottom: 10, containLabel: true },
      xAxis: { type: 'category', data: ['Week 1', 'Week 2', 'Week 3', 'Week 4'], axisLabel: { color: '#94a3b8', fontSize: 10 }, axisLine: { lineStyle: { color: '#334155' } } },
      yAxis: { type: 'value', name: 'MWh', nameTextStyle: { color: '#64748b', fontSize: 10 }, axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: '#1e293b' } } },
      series: [
        { name: 'Actual', type: 'bar', barWidth: '35%', data: [420, 480, 510, 490], itemStyle: { color: '#10b981', borderRadius: [4, 4, 0, 0] } },
        { name: 'Capacity', type: 'bar', barWidth: '35%', data: [520, 520, 520, 520], itemStyle: { color: '#64748b', borderRadius: [4, 4, 0, 0] } }
      ]
    })
  }
}

// Update Chart Data
const updateCharts = () => {
  if (powerChart) {
    const newData = [38 + Math.random() * 10, 42 + Math.random() * 10, 52 + Math.random() * 15, 72 + Math.random() * 15, 78 + Math.random() * 12, 58 + Math.random() * 12, 42 + Math.random() * 8]
    powerChart.setOption({ series: [{ data: newData }] })
  }
  if (windChart) {
    const newData = [4.8 + Math.random() * 1.5, 5.5 + Math.random() * 1.5, 6.8 + Math.random() * 1.5, 7.5 + Math.random() * 1.5, 7.2 + Math.random() * 1.5, 6.0 + Math.random() * 1.5, 5.2 + Math.random() * 1.2]
    windChart.setOption({ series: [{ data: newData }] })
  }
  if (directionChart) {
    const newData = [
      { value: 30 + Math.random() * 15, name: 'N' }, { value: 25 + Math.random() * 10, name: 'NE' },
      { value: 38 + Math.random() * 15, name: 'E' }, { value: 32 + Math.random() * 12, name: 'SE' },
      { value: 22 + Math.random() * 10, name: 'S' }, { value: 28 + Math.random() * 12, name: 'SW' },
      { value: 40 + Math.random() * 15, name: 'W' }, { value: 26 + Math.random() * 12, name: 'NW' }
    ]
    directionChart.setOption({ series: [{ data: newData }] })
  }
  if (generationChartIns) {
    const newActual = [400 + Math.random() * 50, 460 + Math.random() * 50, 490 + Math.random() * 50, 470 + Math.random() * 50]
    generationChartIns.setOption({ series: [{ data: newActual }] })
  }
}

// Lifecycle Hooks
onMounted(async () => {
  await preloadBackground()
  isBackgroundLoaded.value = true
  await nextTick()

  setTimeout(() => {
    initCharts()
  }, 100)

  dataInterval = setInterval(() => {
    updateRealTimeData()
  }, 3000)

  chartInterval = setInterval(() => {
    updateCharts()
  }, 5000)
})

onUnmounted(() => {
  if (dataInterval) clearInterval(dataInterval)
  if (chartInterval) clearInterval(chartInterval)
  powerChart?.dispose()
  windChart?.dispose()
  directionChart?.dispose()
  generationChartIns?.dispose()
})
</script>

<style scoped>
/* Loading Styles */
.loading-container {
  position: fixed;
  inset: 0;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: center;
}

.loading-content {
  text-align: center;
  padding: 40px;
  border-radius: 32px;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(59, 130, 246, 0.3);
  animation: fadeInUp 0.6s;
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
  animation: spin 1.5s infinite;
}

.spinner-ring:nth-child(1) { border-top-color: #3b82f6; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; width: 70%; height: 70%; top: 15%; left: 15%; animation-delay: 0.2s; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; width: 40%; height: 40%; top: 30%; left: 30%; animation-delay: 0.4s; }

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text { font-size: 28px; font-weight: 700; color: #e2e8f0; margin-bottom: 24px; }
.loading-progress { width: 280px; height: 4px; background: rgba(255,255,255,0.1); border-radius: 4px; margin: 0 auto 16px; overflow: hidden; }
.progress-bar { height: 100%; background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec489a); transition: width 0.3s; background-size: 200% auto; animation: shimmer 2s linear infinite; }
@keyframes shimmer { 0% { background-position: 0% 0%; } 100% { background-position: 200% 0%; } }
.loading-tip { font-size: 13px; color: #94a3b8; margin-bottom: 8px; }
.loading-subtip { font-size: 11px; color: #64748b; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

/* Main Page */
.wind-energy-page {
  display: flex;
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, #0a0f1a 0%, #0f172a 100%);
  overflow: hidden;
  animation: fadeIn 0.5s;
}

/* Left Panel - Vertical 4 Charts */
.left-panel {
  width: 520px;
  padding: 24px 20px;
  background: rgba(15, 23, 42, 0.75);
  backdrop-filter: blur(12px);
  border-right: 1px solid rgba(59, 130, 246, 0.3);
  z-index: 2;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.page-header {
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(59, 130, 246, 0.3);
  flex-shrink: 0;
}

.page-title {
  font-size: 24px;
  font-weight: 800;
  background: linear-gradient(135deg, #e0f2fe, #bae6fd);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  letter-spacing: 1px;
  margin: 0;
}

/* Charts Container - Vertical 4 equal sections */
.charts-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0;
  overflow: hidden;
}

.chart-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 8px 0;
  border-bottom: 1px solid rgba(59, 130, 246, 0.15);
}

.chart-item:last-child {
  border-bottom: none;
}

.chart-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  padding: 0 4px;
  flex-shrink: 0;
}

.chart-icon { font-size: 18px; }
.chart-title { flex: 1; font-size: 13px; font-weight: 600; color: #e2e8f0; letter-spacing: 0.5px; }

.chart-box {
  flex: 1;
  width: 100%;
  min-height: 0;
}

/* Right Panel */
.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 20px 24px 24px 0;
  overflow: hidden;
}

/* Image Container */
.image-container {
  position: relative;
  width: 100%;
  border-radius: 20px;
  overflow: hidden;
  margin-bottom: 20px;
  box-shadow: 0 20px 35px -12px rgba(0, 0, 0, 0.5);
  flex-shrink: 0;
}

.wind-image {
  width: 100%;
  height: auto;
  display: block;
  aspect-ratio: 16 / 9;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.3) 0%, rgba(15, 23, 42, 0.1) 100%);
  pointer-events: none;
}

/* Data Fields Container - Two rows */
.data-fields-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: hidden;
}

.data-row {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  min-height: 0;
}

.data-field-card {
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 16px;
  padding: 14px;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.3s ease;
}

.data-field-card:hover {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.6);
  transform: translateY(-2px);
}

.field-icon { font-size: 28px; filter: drop-shadow(0 0 6px rgba(59, 130, 246, 0.5)); }
.field-info { flex: 1; }
.field-label { font-size: 11px; font-weight: 500; color: #94a3b8; display: block; margin-bottom: 4px; letter-spacing: 0.5px; }
.field-value { font-size: 20px; font-weight: 800; color: #facc15; font-family: monospace; line-height: 1.2; }
.field-unit { font-size: 10px; font-weight: 500; color: #64748b; margin-left: 2px; }
.field-trend { font-size: 10px; font-weight: 600; display: inline-block; margin-top: 4px; padding: 2px 6px; border-radius: 20px; }
.field-trend.up { background: rgba(16, 185, 129, 0.15); color: #34d399; }
.field-trend.down { background: rgba(239, 68, 68, 0.15); color: #f87171; }

/* Hide Scrollbars */
.charts-container::-webkit-scrollbar,
.data-fields-container::-webkit-scrollbar {
  display: none;
}
.charts-container,
.data-fields-container {
  -ms-overflow-style: none;
  scrollbar-width: none;
}


/* ==================== 隐藏所有滚动条 ==================== */
.left-panel::-webkit-scrollbar,
.right-panel::-webkit-scrollbar,
.charts-container::-webkit-scrollbar,
.data-fields-container::-webkit-scrollbar,
.chart-item::-webkit-scrollbar {
  display: none;
}

.left-panel,
.right-panel,
.charts-container,
.data-fields-container,
.chart-item {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

/* 确保容器不会溢出滚动 */
.left-panel,
.right-panel,
.charts-container,
.data-fields-container {
  overflow-y: auto;
  overflow-x: hidden;
}
</style>
