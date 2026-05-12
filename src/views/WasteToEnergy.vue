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
          <span class="loading-title">Loading Waste-to-Energy</span>
          <span class="loading-dots">...</span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Initializing Waste Power System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Page -->
  <div v-else class="wind-energy-page">
    <!-- Left Panel -->
    <div class="left-panel">
      <!-- 页面标题 + 时间 -->
      <div class="page-header">
        <h1 class="page-title">Waste Energy</h1>
        <div class="current-time">{{ currentTime }}</div>
      </div>

      <div class="charts-container">
        <!-- 1. 垃圾处理量趋势（平滑面积折线图） -->
        <div class="chart-item">
          <div class="chart-header">
            <span class="chart-icon">🗑️</span>
            <span class="chart-title">Waste Processed Trend</span>
            <el-tag size="small" type="success">Weekly</el-tag>
          </div>
          <div ref="wasteTrendChart" class="chart-box"></div>
        </div>

        <!-- 2. 发电功率（胶囊渐变柱状图） -->
        <div class="chart-item">
          <div class="chart-header">
            <span class="chart-icon">⚡</span>
            <span class="chart-title">Power Generation (Hourly)</span>
            <el-tag size="small" type="info">24h</el-tag>
          </div>
          <div ref="powerBarChart" class="chart-box"></div>
        </div>

        <!-- 3. 不同垃圾类型热值（横向条形图） -->
        <div class="chart-item">
          <div class="chart-header">
            <span class="chart-icon">🔥</span>
            <span class="chart-title">Calorific Value by Waste Type</span>
            <el-tag size="small" type="warning">Live</el-tag>
          </div>
          <div ref="calorificBarChart" class="chart-box"></div>
        </div>

        <!-- 4. 垃圾量 vs 发电量（双轴面积+柱状混合，优雅版） -->
        <div class="chart-item">
          <div class="chart-header">
            <span class="chart-icon">📊</span>
            <span class="chart-title">Waste vs Energy Output</span>
            <el-tag size="small" type="primary">Monthly</el-tag>
          </div>
          <div ref="dualChart" class="chart-box"></div>
        </div>
      </div>
    </div>

    <!-- Right Panel -->
    <div class="right-panel">
      <div class="image-container">
        <el-image
            src="https://aegisnx.com/wp-content/uploads/2026/05/1778480539768.png"
            fit="cover"
            class="wind-image"
        />
        <div class="image-overlay"></div>
      </div>

      <div class="data-fields-container">
        <!-- Row 1 -->
        <div class="data-row">
          <div class="data-field-card">
            <div class="field-icon">🔥</div>
            <div class="field-info">
              <span class="field-label">Current Power</span>
              <span class="field-value">{{ formatNumber(currentPower) }} <span class="field-unit">kW</span></span>
              <span class="field-trend up">↑ {{ powerTrend }}%</span>
            </div>
          </div>
          <div class="data-field-card">
            <div class="field-icon">📈</div>
            <div class="field-info">
              <span class="field-label">Today Generation</span>
              <span class="field-value">{{ formatNumber(todayGen) }} <span class="field-unit">kWh</span></span>
              <span class="field-trend up">↑ {{ genTrend }}%</span>
            </div>
          </div>
          <div class="data-field-card">
            <div class="field-icon">🗑️</div>
            <div class="field-info">
              <span class="field-label">Waste Processed</span>
              <span class="field-value">{{ formatNumber(wasteProcessed) }} <span class="field-unit">tons</span></span>
              <span class="field-trend up">↑ {{ wasteTrend }}%</span>
            </div>
          </div>
          <div class="data-field-card">
            <div class="field-icon">🌡️</div>
            <div class="field-info">
              <span class="field-label">Furnace Temp</span>
              <span class="field-value">{{ furnaceTemp }} <span class="field-unit">°C</span></span>
              <span class="field-trend">{{ tempTrend === 'up' ? '↑' : '↓' }} {{ tempChange }}%</span>
            </div>
          </div>
        </div>

        <!-- Row 2 -->
        <div class="data-row">
          <div class="data-field-card">
            <div class="field-icon">💰</div>
            <div class="field-info">
              <span class="field-label">Revenue Today</span>
              <span class="field-value">${{ revenue }}<span class="field-unit">k</span></span>
              <span class="field-trend up">↑ {{ revTrend }}%</span>
            </div>
          </div>
          <div class="data-field-card">
            <div class="field-icon">🌿</div>
            <div class="field-info">
              <span class="field-label">CO₂ Saved</span>
              <span class="field-value">{{ co2 }} <span class="field-unit">tons</span></span>
              <span class="field-trend up">↑ {{ co2Trend }}%</span>
            </div>
          </div>
          <div class="data-field-card">
            <div class="field-icon">⚙️</div>
            <div class="field-info">
              <span class="field-label">Efficiency</span>
              <span class="field-value">{{ efficiency }}<span class="field-unit">%</span></span>
              <span class="field-trend up">↑ {{ effTrend }}%</span>
            </div>
          </div>
          <div class="data-field-card">
            <div class="field-icon">♻️</div>
            <div class="field-info">
              <span class="field-label">Recycling Rate</span>
              <span class="field-value">{{ recyclingRate }}<span class="field-unit">%</span></span>
              <span class="field-trend up">↑ {{ recycleTrend }}%</span>
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

// ---------- 加载状态 ----------
const isBackgroundLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing assets...')

// ---------- 右侧数据 ----------
const currentPower = ref(5200)
const powerTrend = ref(5.2)
const todayGen = ref(124800)
const genTrend = ref(7.8)
const wasteProcessed = ref(850)
const wasteTrend = ref(6.5)
const furnaceTemp = ref(1050)
const tempTrend = ref('up')
const tempChange = ref(2.1)
const revenue = ref(28.4)
const revTrend = ref(9.3)
const co2 = ref(152.6)
const co2Trend = ref(11.2)
const efficiency = ref(68.5)
const effTrend = ref(3.2)
const recyclingRate = ref(35.2)
const recycleTrend = ref(4.5)

// ---------- 当前时间 ----------
const currentTime = ref('')
let timeInterval = null

// ---------- 图表实例 ----------
const wasteTrendChart = ref(null)
const powerBarChart = ref(null)
const calorificBarChart = ref(null)
const dualChart = ref(null)
let wasteTrendEChart = null
let powerBarEChart = null
let calorificBarEChart = null
let dualEChart = null

let dataInterval = null
let chartInterval = null

// ---------- 辅助函数 ----------
const formatNumber = (num) => num.toLocaleString()

// ---------- 更新时间（带毫秒）----------
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
  'Loading waste data...',
  'Calibrating incinerators...',
  'Establishing connection...',
  'Starting dashboard...',
  'Almost ready...'
]

const preloadBackground = () => new Promise((resolve) => {
  const img = new Image()
  img.src = 'https://aegisnx.com/wp-content/uploads/2026/05/1778480539768.png'
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
  currentPower.value = Math.floor(4800 + Math.random() * 1200)
  powerTrend.value = +(2 + Math.random() * 8).toFixed(1)
  todayGen.value = 110000 + Math.floor(Math.random() * 30000)
  genTrend.value = +(4 + Math.random() * 10).toFixed(1)
  wasteProcessed.value = 700 + Math.floor(Math.random() * 300)
  wasteTrend.value = +(3 + Math.random() * 8).toFixed(1)
  furnaceTemp.value = 980 + Math.floor(Math.random() * 120)
  tempTrend.value = furnaceTemp.value > 1050 ? 'up' : 'down'
  tempChange.value = +(1 + Math.random() * 4).toFixed(1)
  revenue.value = +(22 + Math.random() * 12).toFixed(1)
  revTrend.value = +(4 + Math.random() * 10).toFixed(1)
  co2.value = +(130 + Math.random() * 50).toFixed(1)
  co2Trend.value = +(6 + Math.random() * 12).toFixed(1)
  efficiency.value = +(62 + Math.random() * 12).toFixed(1)
  effTrend.value = +(1.5 + Math.random() * 5).toFixed(1)
  recyclingRate.value = +(28 + Math.random() * 15).toFixed(1)
  recycleTrend.value = +(2 + Math.random() * 6).toFixed(1)
}

// ---------- 初始化图表（全新美观风格） ----------
const initCharts = () => {
  // 1. 垃圾处理量趋势 - 平滑面积折线图（渐变填充）
  if (wasteTrendChart.value) {
    wasteTrendEChart = echarts.init(wasteTrendChart.value)
    wasteTrendEChart.setOption({
      tooltip: { trigger: 'axis', valueFormatter: (value) => value + ' tons' },
      grid: { left: '8%', right: '5%', top: 20, bottom: 10, containLabel: true },
      xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], axisLabel: { color: '#cbd5e1' }, axisLine: { lineStyle: { color: '#334155' } } },
      yAxis: { type: 'value', name: 'tons', nameTextStyle: { color: '#94a3b8' }, axisLabel: { color: '#cbd5e1' }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } } },
      series: [{
        data: [720, 800, 850, 820, 780, 740, 690],
        type: 'line', smooth: true, symbol: 'circle', symbolSize: 6,
        lineStyle: { width: 3, color: '#a855f7', shadowBlur: 12, shadowColor: '#a855f7' },
        areaStyle: { opacity: 0.4, color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#a855f7' }, { offset: 1, color: '#0f172a' }]) },
        itemStyle: { color: '#a855f7', borderColor: '#fff', borderWidth: 1 },
        label: { show: true, position: 'top', color: '#e2e8f0', fontSize: 10, formatter: '{c} t' }
      }]
    })
  }

  // 2. 发电功率 - 胶囊渐变柱状图（24小时）
  if (powerBarChart.value) {
    powerBarEChart = echarts.init(powerBarChart.value)
    powerBarEChart.setOption({
      tooltip: { trigger: 'axis', valueFormatter: (value) => value + ' kW' },
      grid: { left: '8%', right: '5%', top: 20, bottom: 10, containLabel: true },
      xAxis: { type: 'category', data: ['0', '2', '4', '6', '8', '10', '12', '14', '16', '18', '20', '22'], axisLabel: { rotate: 30, color: '#cbd5e1' }, axisLine: { lineStyle: { color: '#334155' } } },
      yAxis: { type: 'value', name: 'kW', nameTextStyle: { color: '#94a3b8' }, axisLabel: { color: '#cbd5e1' }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } } },
      series: [{
        data: [4200, 4400, 4600, 5000, 5400, 5600, 5800, 5600, 5400, 5100, 4800, 4500],
        type: 'bar', barWidth: '65%', borderRadius: [10, 10, 0, 0],
        itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#06b6d4' }, { offset: 1, color: '#3b82f6' }]), shadowBlur: 10, shadowColor: '#06b6d4' },
        label: { show: true, position: 'top', color: '#e2e8f0', fontSize: 9, formatter: '{c}' }
      }]
    })
  }

  // 3. 热值分布 - 横向条形图（美观简洁）
  if (calorificBarChart.value) {
    calorificBarEChart = echarts.init(calorificBarChart.value)
    calorificBarEChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}: {c} MJ/kg' },
      grid: { left: '15%', right: '5%', top: 15, bottom: 10, containLabel: true },
      xAxis: { type: 'value', name: 'MJ/kg', nameTextStyle: { color: '#94a3b8' }, axisLabel: { color: '#cbd5e1' }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } } },
      yAxis: { type: 'category', data: ['Plastic', 'Rubber', 'Textile', 'Biomass', 'Paper'], axisLabel: { color: '#cbd5e1' }, axisLine: { show: false }, axisTick: { show: false } },
      series: [{
        data: [38, 32, 16, 14, 12], type: 'bar', orientation: 'horizontal', barWidth: '50%', borderRadius: [0, 8, 8, 0],
        itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{ offset: 0, color: '#f97316' }, { offset: 1, color: '#dc2626' }]), shadowBlur: 6, shadowColor: '#f97316' },
        label: { show: true, position: 'right', color: '#e2e8f0', fontWeight: 'bold', formatter: '{c} MJ/kg' }
      }]
    })
  }

  // 4. 垃圾量 vs 发电量 - 双轴优雅组合图（柱状+平滑折线，面积微填充）
  if (dualChart.value) {
    dualEChart = echarts.init(dualChart.value)
    dualEChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Waste (tons)', 'Energy (MWh)'], textStyle: { color: '#cbd5e1' }, right: 10, top: 0 },
      grid: { left: '8%', right: '8%', top: 40, bottom: 10, containLabel: true },
      xAxis: { type: 'category', data: ['Week 1', 'Week 2', 'Week 3', 'Week 4'], axisLabel: { color: '#cbd5e1' }, axisLine: { lineStyle: { color: '#334155' } } },
      yAxis: [
        { type: 'value', name: 'tons', nameTextStyle: { color: '#94a3b8' }, axisLabel: { color: '#cbd5e1' }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } } },
        { type: 'value', name: 'MWh', nameTextStyle: { color: '#94a3b8' }, axisLabel: { color: '#cbd5e1' }, splitLine: { show: false } }
      ],
      series: [
        { name: 'Waste (tons)', type: 'bar', barWidth: '40%', data: [5200, 5800, 6100, 5900], itemStyle: { borderRadius: [8, 8, 0, 0], color: '#8b5cf6', shadowBlur: 8, shadowColor: '#8b5cf6' }, label: { show: true, position: 'top', color: '#e2e8f0' } },
        { name: 'Energy (MWh)', type: 'line', smooth: true, yAxisIndex: 1, data: [480, 540, 570, 550], lineStyle: { width: 3, color: '#f97316', shadowBlur: 8, shadowColor: '#f97316' }, areaStyle: { opacity: 0.2, color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#f97316' }, { offset: 1, color: '#0f172a' }]) }, symbol: 'circle', symbolSize: 8, itemStyle: { color: '#f97316', borderColor: '#fff', borderWidth: 1 }, label: { show: true, position: 'top', color: '#e2e8f0', formatter: '{c} MWh' } }
      ]
    })
  }
}

// ---------- 动态更新图表数据 ----------
const updateCharts = () => {
  if (wasteTrendEChart) {
    const newWaste = [660 + Math.random() * 140, 740 + Math.random() * 140, 790 + Math.random() * 140, 770 + Math.random() * 140, 720 + Math.random() * 140, 690 + Math.random() * 140, 640 + Math.random() * 140].map(v => Math.floor(v))
    wasteTrendEChart.setOption({ series: [{ data: newWaste }] })
  }
  if (powerBarEChart) {
    const newPower = Array.from({ length: 12 }, () => Math.floor(4100 + Math.random() * 900))
    powerBarEChart.setOption({ series: [{ data: newPower }] })
  }
  if (calorificBarEChart) {
    const newHeat = [32 + Math.random() * 8, 28 + Math.random() * 8, 14 + Math.random() * 5, 12 + Math.random() * 4, 10 + Math.random() * 4].map(v => +(v.toFixed(1)))
    calorificBarEChart.setOption({ series: [{ data: newHeat }] })
  }
  if (dualEChart) {
    const newWaste = [5000 + Math.random() * 1200, 5400 + Math.random() * 1200, 5800 + Math.random() * 1200, 5600 + Math.random() * 1200].map(v => Math.floor(v))
    const newEnergy = newWaste.map(w => Math.floor(w * 0.092 + Math.random() * 20))
    dualEChart.setOption({ series: [{ data: newWaste }, { data: newEnergy }] })
  }
}

// ---------- 窗口/全屏自适应 ----------
const handleResize = () => {
  setTimeout(() => {
    wasteTrendEChart?.resize()
    powerBarEChart?.resize()
    calorificBarEChart?.resize()
    dualEChart?.resize()
  }, 100)
}

// ---------- 生命周期 ----------
onMounted(async () => {
  await preloadBackground()
  isBackgroundLoaded.value = true
  await nextTick()

  setTimeout(() => initCharts(), 100)

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
  wasteTrendEChart?.dispose()
  powerBarEChart?.dispose()
  calorificBarEChart?.dispose()
  dualEChart?.dispose()
})
</script>

<style scoped>
/* 样式完全复用 Wind.vue，仅复制一份保证完整，无需改动 */
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
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.loading-text { font-size: 28px; font-weight: 700; color: #e2e8f0; margin-bottom: 24px; }
.loading-progress { width: 280px; height: 4px; background: rgba(255,255,255,0.1); border-radius: 4px; margin: 0 auto 16px; overflow: hidden; }
.progress-bar { height: 100%; background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec489a); transition: width 0.3s; background-size: 200% auto; animation: shimmer 2s linear infinite; }
@keyframes shimmer { 0% { background-position: 0% 0%; } 100% { background-position: 200% 0%; } }
.loading-tip { font-size: 13px; color: #94a3b8; margin-bottom: 8px; }
.loading-subtip { font-size: 11px; color: #64748b; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.wind-energy-page {
  display: flex;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #0a0f1a 0%, #0f172a 100%);
  animation: fadeIn 0.5s;
}
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
.current-time {
  font-size: 13px;
  font-family: 'Monaco', monospace;
  color: #a5f3c3;
  background: rgba(0,0,0,0.5);
  backdrop-filter: blur(4px);
  padding: 6px 12px;
  border-radius: 20px;
  letter-spacing: 0.3px;
  border: 1px solid rgba(16,185,129,0.3);
  box-shadow: 0 0 8px rgba(16,185,129,0.2);
  transition: all 0.2s;
}
.current-time:hover {
  border-color: #10b981;
  background: rgba(0,0,0,0.7);
  box-shadow: 0 0 12px rgba(16,185,129,0.4);
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
  background: linear-gradient(90deg, transparent, rgba(59,130,246,0.4), transparent);
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
.chart-box { flex: 1; width: 100%; min-height: 0; }
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
  box-shadow: 0 20px 35px -12px rgba(0,0,0,0.5);
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
  background: linear-gradient(135deg, rgba(15,23,42,0.3), rgba(15,23,42,0.1));
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
  background: rgba(15,23,42,0.5);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(59,130,246,0.3);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
  overflow: hidden;
}
.data-field-card:hover {
  background: rgba(59,130,246,0.1);
  border-color: rgba(59,130,246,0.6);
}
.field-icon {
  font-size: 24px;
  filter: drop-shadow(0 0 6px rgba(59,130,246,0.5));
  flex-shrink: 0;
}
.field-info { flex: 1; min-width: 0; }
.field-label {
  font-size: 15px;
  font-weight: bold;
  color: #94a3b8;
  display: block;
  margin-bottom: 2px;
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
  background: rgba(239,68,68,0.15);
  color: #f87171;
}
.field-trend.up {
  background: rgba(16,185,129,0.15);
  color: #34d399;
}
.field-trend.down {
  background: rgba(239,68,68,0.15);
  color: #f87171;
}
.left-panel, .right-panel, .charts-container, .data-fields-container, .chart-item {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.left-panel::-webkit-scrollbar, .right-panel::-webkit-scrollbar, .charts-container::-webkit-scrollbar, .data-fields-container::-webkit-scrollbar, .chart-item::-webkit-scrollbar {
  display: none;
}
</style>