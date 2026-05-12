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
          <span class="loading-title">Loading Energy Storage</span>
          <span class="loading-dots">...</span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Initializing Battery System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Page -->
  <div v-else class="wind-energy-page">
    <!-- Left Panel -->
    <div class="left-panel">
      <div class="page-header">
        <h1 class="page-title">Energy Storage</h1>
        <div class="current-time">{{ currentTime }}</div>
      </div>

      <div class="charts-container">
        <!-- 1. 充放电功率趋势（正负面积图） -->
        <div class="chart-item">
          <div class="chart-header">
            <span class="chart-icon">🔋⚡</span>
            <span class="chart-title">Power Flow (Charge / Discharge)</span>
            <el-tag size="small" type="success">24h</el-tag>
          </div>
          <div ref="powerChart" class="chart-box"></div>
        </div>

        <!-- 2. SOC 荷电状态变化趋势（折线面积图） -->
        <div class="chart-item">
          <div class="chart-header">
            <span class="chart-icon">📊</span>
            <span class="chart-title">State of Charge (SOC)</span>
            <el-tag size="small" type="info">Daily</el-tag>
          </div>
          <div ref="socChart" class="chart-box"></div>
        </div>

        <!-- 3. 电池健康仪表盘（SOH、温度、循环效率 - 三个环形进度条） -->
        <div class="chart-item">
          <div class="chart-header">
            <span class="chart-icon">❤️</span>
            <span class="chart-title">Battery Health Metrics</span>
            <el-tag size="small" type="warning">Real-time</el-tag>
          </div>
          <div class="gauges-row">
            <div class="gauge-card">
              <el-progress type="circle" :percentage="soh" :stroke-width="6" color="#10b981" class="mini-gauge">
                <template #default><span class="gauge-value">{{ soh }}<span class="gauge-unit">%</span></span></template>
              </el-progress>
              <div class="gauge-title">SOH (Health)</div>
              <div class="gauge-desc">{{ soh }}%</div>
            </div>
            <div class="gauge-card">
              <el-progress type="circle" :percentage="batteryTempPercent" :stroke-width="6" color="#f59e0b" class="mini-gauge">
                <template #default><span class="gauge-value">{{ batteryTemp }}<span class="gauge-unit">°C</span></span></template>
              </el-progress>
              <div class="gauge-title">Temperature</div>
              <div class="gauge-desc">{{ batteryTemp }}°C</div>
            </div>
            <div class="gauge-card">
              <el-progress type="circle" :percentage="cycleEfficiency" :stroke-width="6" color="#06b6d4" class="mini-gauge">
                <template #default><span class="gauge-value">{{ cycleEfficiency }}<span class="gauge-unit">%</span></span></template>
              </el-progress>
              <div class="gauge-title">Cycle Efficiency</div>
              <div class="gauge-desc">{{ cycleEfficiency }}%</div>
            </div>
          </div>
        </div>

        <!-- 4. 削峰填谷收益分析（双轴：放电量 + 电价） -->
        <div class="chart-item">
          <div class="chart-header">
            <span class="chart-icon">💰</span>
            <span class="chart-title">Peak Shaving & Revenue</span>
            <el-tag size="small" type="primary">Weekly</el-tag>
          </div>
          <div ref="revenueChart" class="chart-box"></div>
        </div>
      </div>
    </div>

    <!-- Right Panel -->
    <div class="right-panel">
      <div class="image-container">
        <el-image src="https://aegisnx.com/wp-content/uploads/2026/05/1778490568300.png" fit="cover" class="wind-image" />
        <div class="image-overlay"></div>
      </div>

      <div class="data-fields-container">
        <div class="data-row">
          <div class="data-field-card">
            <div class="field-icon">⚡</div>
            <div class="field-info">
              <span class="field-label">Current Power</span>
              <span class="field-value">{{ currentPower > 0 ? '+' : '' }}{{ formatNumber(Math.abs(currentPower)) }} <span class="field-unit">kW</span></span>
              <span class="field-trend" :class="currentPower > 0 ? 'up' : 'down'">{{ currentPower > 0 ? 'Discharging' : 'Charging' }}</span>
            </div>
          </div>
          <div class="data-field-card">
            <div class="field-icon">🔋</div>
            <div class="field-info">
              <span class="field-label">SOC</span>
              <span class="field-value">{{ soc }}<span class="field-unit">%</span></span>
              <el-progress :percentage="soc" :stroke-width="6" color="#10b981" class="compact-progress" />
            </div>
          </div>
          <div class="data-field-card">
            <div class="field-icon">❤️</div>
            <div class="field-info">
              <span class="field-label">SOH</span>
              <span class="field-value">{{ soh }}<span class="field-unit">%</span></span>
              <span class="field-trend up">↑ {{ sohTrend }}%</span>
            </div>
          </div>
          <div class="data-field-card">
            <div class="field-icon">🌡️</div>
            <div class="field-info">
              <span class="field-label">Battery Temp</span>
              <span class="field-value">{{ batteryTemp }} <span class="field-unit">°C</span></span>
              <span class="field-trend">{{ tempTrend === 'up' ? '↑' : '↓' }} {{ tempChange }}%</span>
            </div>
          </div>
        </div>
        <div class="data-row">
          <div class="data-field-card">
            <div class="field-icon">📈</div>
            <div class="field-info">
              <span class="field-label">Today Discharge</span>
              <span class="field-value">{{ formatNumber(todayDischarge) }} <span class="field-unit">kWh</span></span>
              <span class="field-trend up">↑ {{ dischargeTrend }}%</span>
            </div>
          </div>
          <div class="data-field-card">
            <div class="field-icon">📉</div>
            <div class="field-info">
              <span class="field-label">Today Charge</span>
              <span class="field-value">{{ formatNumber(todayCharge) }} <span class="field-unit">kWh</span></span>
              <span class="field-trend up">↑ {{ chargeTrend }}%</span>
            </div>
          </div>
          <div class="data-field-card">
            <div class="field-icon">💰</div>
            <div class="field-info">
              <span class="field-label">Revenue Today</span>
              <span class="field-value">${{ revenue }}<span class="field-unit">k</span></span>
              <span class="field-trend up">↑ {{ revenueTrend }}%</span>
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
const currentPower = ref(320)        // 正值放电，负值充电
const soc = ref(68.5)
const soh = ref(94.2)
const sohTrend = ref(1.2)
const batteryTemp = ref(32.4)
const tempTrend = ref('up')
const tempChange = ref(2.1)
const todayDischarge = ref(1250)
const dischargeTrend = ref(5.4)
const todayCharge = ref(980)
const chargeTrend = ref(3.8)
const revenue = ref(0.86)
const revenueTrend = ref(7.2)
const co2 = ref(3.2)
const co2Trend = ref(9.5)

// 仪表盘额外数据
const cycleEfficiency = ref(92.5)
const batteryTempPercent = ref(65)    // 用于环形图显示温度比例（0-100范围，35°C对应70%等）

// ---------- 当前时间 ----------
const currentTime = ref('')
let timeInterval = null

// ---------- 图表实例 ----------
const powerChart = ref(null)
const socChart = ref(null)
const revenueChart = ref(null)
let powerEChart = null
let socEChart = null
let revenueEChart = null

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
  'Loading battery data...',
  'Calibrating BMS...',
  'Establishing connection...',
  'Starting dashboard...',
  'Almost ready...'
]

const preloadBackground = () => new Promise((resolve) => {
  const img = new Image()
  img.src = 'https://aegisnx.com/wp-content/uploads/2026/05/1778490568300.png'
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
  // 功率在 -400 到 500 之间波动
  currentPower.value = Math.floor(-350 + Math.random() * 850)
  soc.value = +(55 + Math.random() * 35).toFixed(1)
  soh.value = +(92 + Math.random() * 5).toFixed(1)
  sohTrend.value = +(0.5 + Math.random() * 2).toFixed(1)
  batteryTemp.value = +(28 + Math.random() * 12).toFixed(1)
  tempTrend.value = batteryTemp.value > 35 ? 'up' : 'down'
  tempChange.value = +(1 + Math.random() * 4).toFixed(1)
  todayDischarge.value = 1000 + Math.floor(Math.random() * 800)
  dischargeTrend.value = +(2 + Math.random() * 8).toFixed(1)
  todayCharge.value = 800 + Math.floor(Math.random() * 600)
  chargeTrend.value = +(1.5 + Math.random() * 7).toFixed(1)
  revenue.value = +(0.6 + Math.random() * 0.8).toFixed(2)
  revenueTrend.value = +(3 + Math.random() * 10).toFixed(1)
  co2.value = +(2.5 + Math.random() * 2.5).toFixed(1)
  co2Trend.value = +(4 + Math.random() * 12).toFixed(1)
  cycleEfficiency.value = +(88 + Math.random() * 9).toFixed(1)
  // 温度对应的环形百分比：0°C->0%, 50°C->100%
  batteryTempPercent.value = Math.min(100, Math.max(0, (batteryTemp.value / 50) * 100))
}

// ---------- 初始化图表 ----------
const initCharts = () => {
  // 1. 充放电功率趋势（正负面积图）
  if (powerChart.value) {
    powerEChart = echarts.init(powerChart.value)
    powerEChart.setOption({
      tooltip: { trigger: 'axis', valueFormatter: (value) => value + ' kW' },
      grid: { left: '8%', right: '5%', top: 20, bottom: 10, containLabel: true },
      xAxis: { type: 'category', data: ['0', '4', '8', '12', '16', '20', '24'], axisLabel: { color: '#cbd5e1' }, axisLine: { lineStyle: { color: '#334155' } } },
      yAxis: { type: 'value', name: 'kW', nameTextStyle: { color: '#94a3b8' }, axisLabel: { color: '#cbd5e1' }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } } },
      series: [{
        data: [120, 280, -150, -320, -180, 240, 380], type: 'line', smooth: true,
        lineStyle: { width: 2, color: '#10b981' },
        areaStyle: {
          opacity: 0.3,
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#10b981' },
            { offset: 1, color: '#0f172a' }
          ])
        },
        symbol: 'circle', symbolSize: 6,
        itemStyle: { color: (params) => params.value >= 0 ? '#10b981' : '#ef4444', borderColor: '#fff' }
      }]
    })
  }

  // 2. SOC 趋势（带目标线）
  if (socChart.value) {
    socEChart = echarts.init(socChart.value)
    socEChart.setOption({
      tooltip: { trigger: 'axis', valueFormatter: (value) => value + '%' },
      grid: { left: '8%', right: '5%', top: 20, bottom: 10, containLabel: true },
      xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], axisLabel: { color: '#cbd5e1' }, axisLine: { lineStyle: { color: '#334155' } } },
      yAxis: { type: 'value', name: 'SOC (%)', nameTextStyle: { color: '#94a3b8' }, axisLabel: { color: '#cbd5e1' }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } } },
      series: [{
        data: [58, 62, 71, 68, 64, 59, 61], type: 'line', smooth: true,
        lineStyle: { width: 3, color: '#06b6d4', shadowBlur: 8 },
        areaStyle: { opacity: 0.2, color: '#06b6d4' },
        symbol: 'circle', symbolSize: 6, label: { show: true, position: 'top', formatter: '{c}%', color: '#e2e8f0' }
      }]
    })
  }

  // 3. 健康仪表盘用 element-plus 进度条，上面已经渲染

  // 4. 削峰填谷收益：双轴（放电量柱状 + 电价折线）
  if (revenueChart.value) {
    revenueEChart = echarts.init(revenueChart.value)
    revenueEChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Discharge Energy (kWh)', 'Electricity Price ($/kWh)'], textStyle: { color: '#cbd5e1' }, right: 10, top: 0 },
      grid: { left: '8%', right: '8%', top: 40, bottom: 10, containLabel: true },
      xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], axisLabel: { color: '#cbd5e1' }, axisLine: { lineStyle: { color: '#334155' } } },
      yAxis: [
        { type: 'value', name: 'kWh', nameTextStyle: { color: '#94a3b8' }, axisLabel: { color: '#cbd5e1' }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } } },
        { type: 'value', name: '$/kWh', nameTextStyle: { color: '#94a3b8' }, axisLabel: { color: '#cbd5e1' }, splitLine: { show: false } }
      ],
      series: [
        { name: 'Discharge Energy (kWh)', type: 'bar', barWidth: '40%', data: [320, 450, 520, 480, 410, 380, 290], itemStyle: { borderRadius: [8, 8, 0, 0], color: '#10b981' }, label: { show: true, position: 'top', color: '#e2e8f0' } },
        { name: 'Electricity Price ($/kWh)', type: 'line', smooth: true, yAxisIndex: 1, data: [0.12, 0.15, 0.18, 0.16, 0.14, 0.11, 0.10], lineStyle: { width: 2, color: '#f59e0b' }, symbol: 'diamond', symbolSize: 6, label: { show: true, position: 'top', color: '#e2e8f0', formatter: '{c} $' } }
      ]
    })
  }
}

// ---------- 动态更新图表数据 ----------
const updateCharts = () => {
  if (powerEChart) {
    const newPower = [100 + Math.random() * 200, 250 + Math.random() * 150, -100 - Math.random() * 200, -250 - Math.random() * 150, -120 - Math.random() * 150, 200 + Math.random() * 200, 350 + Math.random() * 150].map(v => Math.floor(v))
    powerEChart.setOption({ series: [{ data: newPower }] })
  }
  if (socEChart) {
    const newSoc = [55 + Math.random() * 10, 60 + Math.random() * 12, 68 + Math.random() * 10, 65 + Math.random() * 10, 62 + Math.random() * 10, 57 + Math.random() * 10, 59 + Math.random() * 10].map(v => +v.toFixed(1))
    socEChart.setOption({ series: [{ data: newSoc }] })
  }
  if (revenueEChart) {
    const newDischarge = [300 + Math.random() * 150, 420 + Math.random() * 150, 500 + Math.random() * 120, 460 + Math.random() * 120, 400 + Math.random() * 120, 370 + Math.random() * 120, 280 + Math.random() * 120].map(v => Math.floor(v))
    const newPrice = [0.11 + Math.random() * 0.05, 0.13 + Math.random() * 0.06, 0.16 + Math.random() * 0.06, 0.14 + Math.random() * 0.06, 0.12 + Math.random() * 0.05, 0.10 + Math.random() * 0.05, 0.09 + Math.random() * 0.05].map(v => +v.toFixed(2))
    revenueEChart.setOption({ series: [{ data: newDischarge }, { data: newPrice }] })
  }
}

// ---------- 窗口/全屏自适应 ----------
const handleResize = () => {
  setTimeout(() => {
    powerEChart?.resize()
    socEChart?.resize()
    revenueEChart?.resize()
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
  powerEChart?.dispose()
  socEChart?.dispose()
  revenueEChart?.dispose()
})
</script>

<style scoped>
/* ===== 完整复用 Wind.vue 的样式（包括 loading、布局、卡片等），并添加额外小仪表盘样式 ===== */
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
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
}
.field-trend.up {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
}
.field-trend.down {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
}
.compact-progress {
  margin-top: 6px;
  width: 100%;
}
.compact-progress :deep(.el-progress-bar__outer) {
  background-color: rgba(255,255,255,0.1);
}
.left-panel, .right-panel, .charts-container, .data-fields-container, .chart-item {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.left-panel::-webkit-scrollbar, .right-panel::-webkit-scrollbar, .charts-container::-webkit-scrollbar, .data-fields-container::-webkit-scrollbar, .chart-item::-webkit-scrollbar {
  display: none;
}

/* 三个仪表盘的小环形图样式 */
.gauges-row {
  flex: 1;
  display: flex;
  justify-content: space-around;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  min-height: 0;
}
.gauge-card {
  flex: 1;
  text-align: center;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 16px;
  padding: 8px 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.mini-gauge {
  width: 80px;
  height: 80px;
}
.mini-gauge :deep(.el-progress-circle) {
  width: 80px !important;
  height: 80px !important;
}
.gauge-value {
  font-size: 16px;
  font-weight: bold;
  color: #facc15;
}
.gauge-unit {
  font-size: 10px;
  color: #64748b;
}
.gauge-title {
  font-size: 11px;
  color: #94a3b8;
  font-weight: 500;
}
.gauge-desc {
  font-size: 12px;
  color: #cbd5e1;
  font-weight: 600;
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