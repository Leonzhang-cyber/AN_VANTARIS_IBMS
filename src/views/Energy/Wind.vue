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
      <!-- 页面标题区域（增加右侧时间） -->
      <div class="page-header">
        <h1 class="page-title">Wind Energy Analytics</h1>
        <div class="current-time" v-if="isFullscreen || isMobile">{{ currentTime }}</div>
      </div>

      <div class="image-container" v-if="isMobile">
        <el-image
            src="https://aegisnx.com/wp-content/uploads/2026/05/1778317798669.png"
            fit="cover"
            class="wind-image"
        />
        <div class="image-overlay"></div>
      </div>

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
      <div class="image-container" v-if="!isMobile">
        <el-image
            src="https://aegisnx.com/wp-content/uploads/2026/05/1778317798669.png"
            fit="cover"
            class="wind-image"
        />
        <div class="image-overlay"></div>
      </div>

      <div class="data-fields-container">
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

        <div class="data-row">
          <div class="data-field-card">
            <div class="field-icon">💰</div>
            <div class="field-info">
              <span class="field-label">Revenue Today</span>
              <span class="field-value">${{ revenueToday }}<span class="field-unit">k</span></span>
              <span class="field-trend up">↑ {{ revenueTrend }}%</span>
            </div>
          </div>

          <div class="data-field-card">
            <div class="field-icon">🌿</div>
            <div class="field-info">
              <span class="field-label">CO₂ Saved</span>
              <span class="field-value">{{ co2Saved }} <span class="field-unit">tons</span></span>
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
import {ref, onMounted, onUnmounted, nextTick, computed} from 'vue'
import * as echarts from 'echarts'
import { useCounterStore } from '@/stores/counter.js'
import { getCurrentInstance } from 'vue'
const getStore = () => {
  const instance = getCurrentInstance()
  if (!instance) {
    throw new Error('useStore() must be called within a setup function')
  }
  // 尝试获取根组件上的 pinia 实例
  const pinia = instance.appContext.config.globalProperties.$pinia
  if (!pinia) {
    throw new Error('Pinia instance not found. Did you forget to call app.use(pinia)?')
  }
  return useCounterStore(pinia) // 手动传入 pinia 实例
}
const counterStore = getStore()
const isFullscreen = computed(() => counterStore.isFullscreen)

// ---------- 加载状态 ----------
const isBackgroundLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing assets...')

// ---------- 数据 ----------
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

// ---------- 当前时间 ----------
const currentTime = ref('')
let timeInterval = null

// ---------- ECharts 实例 ----------
const powerTrendChart = ref(null)
const windSpeedChart = ref(null)
const windDirectionChart = ref(null)
const generationChart = ref(null)
let powerChart = null
let windChart = null
let directionChart = null
let generationChartIns = null

let dataInterval = null
let chartInterval = null

// ---------- 辅助函数 ----------
const formatNumber = (num) => num.toLocaleString()

// ---------- 更新时间（YYYY-MM-DD HH:MM:SS.ms）----------
const updateCurrentTime = () => {
  const now = new Date()
  // 获取 UTC 毫秒数并转换为新加坡时间 (UTC+8，无夏令时)
  const utc = now.getTime() + (now.getTimezoneOffset() * 60000)
  const sgTime = new Date(utc + (8 * 3600000))

  const year = sgTime.getFullYear()
  const month = String(sgTime.getMonth() + 1).padStart(2, '0')
  const day = String(sgTime.getDate()).padStart(2, '0')
  const hours = String(sgTime.getHours()).padStart(2, '0')
  const minutes = String(sgTime.getMinutes()).padStart(2, '0')
  const seconds = String(sgTime.getSeconds()).padStart(2, '0')
  const ms = String(sgTime.getMilliseconds()).padStart(3, '0')

  currentTime.value = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}.${ms} SGT`
}

// ---------- 加载动画 ----------
const loadingMessages = [
  'Preparing assets...',
  'Loading wind data...',
  'Initializing turbines...',
  'Establishing connection...',
  'Starting dashboard...',
  'Almost ready...'
]

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

// ---------- 模拟数据更新 ----------
const updateRealTimeData = () => {
  currentPower.value = Math.floor(2600 + Math.random() * 500)
  powerTrend.value = +(5 + Math.random() * 8).toFixed(1)
  windSpeed.value = +(5 + Math.random() * 5).toFixed(1)
  windDirection.value = Math.floor(0 + Math.random() * 360)
  const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
  windDirectionText.value = directions[Math.floor(windDirection.value / 22.5)]
  todayGeneration.value = 65000 + Math.floor(Math.random() * 8000)
  revenueToday.value = +(7.5 + Math.random() * 2).toFixed(2)
  co2Saved.value = +(42 + Math.random() * 12).toFixed(1)
  capacityFactor.value = +(38 + Math.random() * 12).toFixed(1)
  rotorRpm.value = +(12 + Math.random() * 5).toFixed(1)
  rotorTrend.value = +(2 + Math.random() * 5).toFixed(1)
  generationTrend.value = +(10 + Math.random() * 8).toFixed(1)
  revenueTrend.value = +(8 + Math.random() * 6).toFixed(1)
  co2Trend.value = +(12 + Math.random() * 8).toFixed(1)
  cfTrend.value = Math.random() > 0.5 ? 'up' : 'down'
  cfChange.value = +(2 + Math.random() * 6).toFixed(1)
  windTrend.value = Math.random() > 0.5 ? 'up' : 'down'
  windSpeedChange.value = +(3 + Math.random() * 7).toFixed(1)
}

// ---------- 初始化图表 ----------
const initCharts = () => {
  if (powerTrendChart.value) {
    powerChart = echarts.init(powerTrendChart.value)
    powerChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, backgroundColor: 'rgba(0,0,0,0.8)', borderColor: '#10b981', borderWidth: 1 },
      grid: { left: '0%', right: '0%', top: 50, bottom: 0, containLabel: true },
      xAxis: { type: 'category', data: ['00', '04', '08', '12', '16', '20', '24'], axisLabel: { color: '#cbd5e1', fontSize: 10, fontWeight: 500 }, axisLine: { lineStyle: { color: '#334155' } }, axisTick: { show: false } },
      yAxis: { type: 'value', name: 'kW', nameTextStyle: { color: '#94a3b8', fontSize: 10 }, axisLabel: { color: '#cbd5e1' }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } } },
      series: [{
        data: [42, 38, 56, 78, 82, 68, 45],
        type: 'line', smooth: true,
        symbol: 'circle', symbolSize: 8,
        lineStyle: { width: 3, color: '#10b981', shadowBlur: 12, shadowColor: '#10b981' },
        areaStyle: { opacity: 0.3, color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#10b981' }, { offset: 1, color: '#0f172a' }]) },
        markPoint: { data: [{ type: 'max', name: 'Peak' }, { type: 'min', name: 'Trough' }], symbolSize: 30, label: { color: '#fff', fontSize: 9 } },
        itemStyle: { color: '#10b981', borderColor: '#fff', borderWidth: 2 }
      }]
    })
  }
  if (windSpeedChart.value) {
    windChart = echarts.init(windSpeedChart.value)
    windChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, backgroundColor: 'rgba(0,0,0,0.8)' },
      grid: { left: '0%', right: '0%', top: 50, bottom: 0, containLabel: true },
      xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], axisLabel: { color: '#cbd5e1', fontSize: 10 }, axisLine: { show: false }, axisTick: { show: false } },
      yAxis: { type: 'value', name: 'm/s', nameTextStyle: { color: '#94a3b8', fontSize: 10 }, axisLabel: { color: '#cbd5e1' }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } } },
      series: [{
        data: [5.2, 6.1, 7.4, 8.2, 7.8, 6.5, 5.8], type: 'bar', barWidth: '55%', borderRadius: [8, 8, 0, 0],
        itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#06b6d4' }, { offset: 1, color: '#3b82f6' }]), shadowBlur: 12, shadowColor: 'rgba(59,130,246,0.5)' },
        label: { show: true, position: 'top', color: '#e2e8f0', fontSize: 10, fontWeight: 'bold', formatter: '{c} m/s' },
        emphasis: { focus: 'series' }
      }]
    })
  }
  if (windDirectionChart.value) {
    directionChart = echarts.init(windDirectionChart.value)
    const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    directionChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, backgroundColor: 'rgba(0,0,0,0.8)' },
      grid: { left: '0%', right: '0%', top: 50, bottom: 0, containLabel: true },
      xAxis: { type: 'category', data: directions, axisLabel: { rotate: 45, color: '#cbd5e1', fontSize: 9, interval: 0 }, axisLine: { lineStyle: { color: '#334155' } } },
      yAxis: { type: 'value', name: 'Frequency', nameTextStyle: { color: '#94a3b8', fontSize: 10 }, axisLabel: { color: '#cbd5e1' }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } } },
      series: [{
        data: [35, 28, 42, 38, 25, 32, 45, 30, 20, 27, 33, 40, 36, 22, 29, 31], type: 'bar', barWidth: '60%',
        itemStyle: { borderRadius: [6, 6, 0, 0], color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#f97316' }, { offset: 1, color: '#ef4444' }]), shadowBlur: 8, shadowColor: '#f97316' },
        label: { show: true, position: 'top', color: '#e2e8f0', fontSize: 9, formatter: '{c}' }
      }]
    })
  }
  if (generationChart.value) {
    generationChartIns = echarts.init(generationChart.value)
    generationChartIns.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, backgroundColor: 'rgba(0,0,0,0.8)' },
      legend: { data: ['Actual Generation'], textStyle: { color: '#cbd5e1' }, right: 10, top: 0 },
      grid: { left: '0%', right: '0%', top: 50, bottom: 0, containLabel: true },
      xAxis: { type: 'category', data: ['Week 1', 'Week 2', 'Week 3', 'Week 4'], axisLabel: { color: '#cbd5e1', fontSize: 10 }, axisLine: { lineStyle: { color: '#334155' } } },
      yAxis: { type: 'value', name: 'MWh', nameTextStyle: { color: '#94a3b8', fontSize: 10 }, axisLabel: { color: '#cbd5e1' }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } } },
      series: [{
        name: 'Actual Generation', type: 'bar', data: [420, 480, 510, 490], barWidth: '50%',
        itemStyle: { borderRadius: [8, 8, 0, 0], color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#10b981' }, { offset: 1, color: '#059669' }]), shadowBlur: 10, shadowColor: '#10b981' },
        label: { show: true, position: 'top', color: '#e2e8f0', fontWeight: 'bold', formatter: '{c} MWh' },
        markLine: { silent: false, symbol: 'none', lineStyle: { type: 'dashed', width: 2, color: '#f59e0b', shadowBlur: 6, shadowColor: '#f59e0b' }, data: [{ yAxis: 520, name: 'Capacity Target', label: { formatter: 'Target: 520 MWh', color: '#fcd34d', position: 'end' } }], label: { show: true, position: 'end', color: '#fcd34d', fontSize: 10 } }
      }]
    })
  }
}

const updateCharts = () => {
  if (powerChart) {
    const newData = [ +(38 + Math.random() * 10).toFixed(1), +(42 + Math.random() * 10).toFixed(1), +(52 + Math.random() * 15).toFixed(1), +(72 + Math.random() * 15).toFixed(1), +(78 + Math.random() * 12).toFixed(1), +(58 + Math.random() * 12).toFixed(1), +(42 + Math.random() * 8).toFixed(1) ]
    powerChart.setOption({ series: [{ data: newData }] })
  }
  if (windChart) {
    const newData = [ +(4.8 + Math.random() * 1.5).toFixed(1), +(5.5 + Math.random() * 1.5).toFixed(1), +(6.8 + Math.random() * 1.5).toFixed(1), +(7.5 + Math.random() * 1.5).toFixed(1), +(7.2 + Math.random() * 1.5).toFixed(1), +(6.0 + Math.random() * 1.5).toFixed(1), +(5.2 + Math.random() * 1.2).toFixed(1) ]
    windChart.setOption({ series: [{ data: newData }] })
  }
  if (directionChart) {
    const newDirectionData = Array.from({ length: 16 }, () => Math.floor(20 + Math.random() * 40))
    directionChart.setOption({ series: [{ data: newDirectionData }] })
  }
  if (generationChartIns) {
    const newActual = [ +(400 + Math.random() * 50).toFixed(0), +(460 + Math.random() * 50).toFixed(0), +(490 + Math.random() * 50).toFixed(0), +(470 + Math.random() * 50).toFixed(0) ]
    generationChartIns.setOption({ series: [{ data: newActual }] })
  }
}

const handleResize = () => {
  setTimeout(() => {
    powerChart?.resize()
    windChart?.resize()
    directionChart?.resize()
    generationChartIns?.resize()
  }, 100)
}

const isMobile = ref(false)
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

// ---------- 生命周期 ----------
onMounted(async () => {
  checkMobile();
  await preloadBackground()
  isBackgroundLoaded.value = true
  await nextTick()

  setTimeout(() => initCharts(), 100)

  // 启动时间更新
  updateCurrentTime()
  timeInterval = setInterval(updateCurrentTime, 100)

  dataInterval = setInterval(updateRealTimeData, 3000)
  chartInterval = setInterval(updateCharts, 5000)
  window.addEventListener('resize', handleResize)
  document.addEventListener('fullscreenchange', handleResize)
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
  if (dataInterval) clearInterval(dataInterval)
  if (chartInterval) clearInterval(chartInterval)
  window.removeEventListener('resize', handleResize)
  document.removeEventListener('fullscreenchange', handleResize)
  powerChart?.dispose()
  windChart?.dispose()
  directionChart?.dispose()
  generationChartIns?.dispose()
})
</script>

<style scoped>
/* ===== Loading 样式（与原代码完全一致） ===== */
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

/* ===== 主页面布局 ===== */
.wind-energy-page {
  display: flex;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #0a0f1a 0%, #0f172a 100%);
  animation: fadeIn 0.5s;
}
/* 左侧面板 */
.left-panel {
  width: 520px;
  padding: 26px 20px;
  background: rgba(15, 23, 42, 0.75);
  backdrop-filter: blur(12px);
  border-right: 1px dashed rgba(59, 130, 246, 0.3);
  z-index: 2;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

/* 页面头部：flex 布局，标题靠左，时间靠右 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(59, 130, 246, 0.3);
  flex-shrink: 0;
  width: 100%;
}
.page-title {
  font-size: 20px;
  font-weight: 800;
  background: linear-gradient(135deg, #e0f2fe, #bae6fd);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  letter-spacing: 1px;
  margin: 0;
}
/* 美化后的时间样式 */
.current-time {
  font-size: 13px;
  font-family: 'Monaco', 'Monospace', monospace;
  color: #a5f3c3;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  padding: 6px 12px;
  border-radius: 20px;
  letter-spacing: 0.3px;
  border: 1px solid rgba(16, 185, 129, 0.3);
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.2);
  transition: all 0.2s;
}
.current-time:hover {
  border-color: #10b981;
  background: rgba(0, 0, 0, 0.7);
  box-shadow: 0 0 12px rgba(16, 185, 129, 0.4);
}

.charts-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: visible;
  margin: 0;
  padding: 0;
  gap: 0;
}
.chart-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin: 0;
  padding: 8px 0;
  background: transparent;
  min-height: 0;
  position: relative;
}
.chart-item:not(:last-child)::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 4px;
  right: 4px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.4), transparent);
  pointer-events: none;
}
.chart-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
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

/* 右侧面板 */
.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 20px 24px 24px 24px;
  overflow: hidden;
}
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
.data-fields-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: hidden;
  min-height: 0;
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
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  overflow: hidden;
}
.data-field-card:hover {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.6);
}
.field-icon {
  font-size: 24px;
  filter: drop-shadow(0 0 6px rgba(59, 130, 246, 0.5));
  flex-shrink: 0;
}
.field-info {
  flex: 1;
  min-width: 0;
}
.field-label {
  font-size: 15px;
  font-weight: 500;
  color: #94a3b8;
  display: block;
  margin-bottom: 2px;
  font-weight: bold;
  letter-spacing: 0.5px;
}
.field-value {
  font-size: 18px;
  font-weight: 800;
  color: #facc15;
  font-family: monospace;
  line-height: 1.2;
  white-space: nowrap;
  overflow-x: hidden;
  text-overflow: ellipsis;
}
.field-unit {
  font-size: 18px;
  font-weight: 500;
  color: #facc15;
  margin-left: 2px;
}
.field-trend {
  font-size: 9px;
  font-weight: 600;
  display: inline-block;
  margin-top: 2px;
  padding: 1px 5px;
  margin-left: 10px;
  border-radius: 20px;
  white-space: nowrap;
  color: #f87171;
  background: rgba(239, 68, 68, 0.15);
}
.field-trend.up {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
}
.field-trend.down {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
}

/* 隐藏所有滚动条 */
.left-panel,
.right-panel,
.charts-container,
.data-fields-container,
.chart-item {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.left-panel::-webkit-scrollbar,
.right-panel::-webkit-scrollbar,
.charts-container::-webkit-scrollbar,
.data-fields-container::-webkit-scrollbar,
.chart-item::-webkit-scrollbar {
  display: none;
}


/* ========== 移动端适配 (屏幕宽度 ≤ 768px) ========== */
/* ========== 移动端适配 (屏幕宽度 ≤ 768px) ========== */
@media (max-width: 768px) {
  /* 根容器：强制占满屏幕高度 + 允许纵向滚动 */
  .wind-energy-page {
    flex-direction: column;
    width: 100%;
    height: 100vh !important;
    overflow-y: auto !important;
    overflow-x: hidden;
    display: block;
  }

  /* 左侧面板：取消固定高度、取消右侧边框、自适应高度 */
  .left-panel {
    width: 100% !important;
    height: auto !important;
    overflow: visible !important;
    border-right: none;
    border-bottom: 1px dashed rgba(59, 130, 246, 0.3);
  }

  /* 右侧面板：取消固定高度、正常滚动 */
  .right-panel {
    width: 100% !important;
    height: auto !important;
    overflow: visible !important;
    flex: none;
    padding-bottom: 140px;
  }

  /* 头部标题换行 */
  .page-header {
    display: flex;
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }

  /* 数据卡片：手机端 2列布局（更美观） */
  .data-row {
    grid-template-columns: repeat(2, 1fr) !important;
    gap: 12px !important;
  }

  /* 图表容器：取消最小高度限制 */
  .charts-container {
    overflow: visible !important;
  }
  .chart-item {
    overflow: visible !important;
    min-height: 200px !important;
  }
}
</style>