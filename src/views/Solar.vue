<template>
  <div v-if="!isBackgroundLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">
          <span class="loading-title">Loading Solar Energy</span>
          <span class="loading-dots">...</span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Initializing Solar Power System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <div v-else class="wind-energy-page">
    <!-- 左侧图表区域 -->
    <div class="left-panel">
      <!-- 页面标题区域（增加右侧时间） -->
      <div class="page-header">
        <h1 class="page-title">Solar Energy Analytics</h1>
        <div class="current-time" v-if="isFullscreen || isMobile">{{ currentTime }}</div>
      </div>

      <div class="image-container" v-if="isMobile">
        <el-image src="https://aegisnx.com/wp-content/uploads/2026/05/1778468449446.png" fit="cover" class="wind-image" />
        <div class="image-overlay"></div>
      </div>

      <div class="charts-container">
        <!-- 1. 辐照度趋势 -->
        <div class="chart-item">
          <div class="chart-header">
            <span class="chart-icon">☀️</span>
            <span class="chart-title">Irradiance Trend</span>
            <el-tag size="small" type="success">24h</el-tag>
          </div>
          <div ref="irradianceChart" class="chart-box"></div>
        </div>

        <!-- 2. 面板温度柱状图 -->
        <div class="chart-item">
          <div class="chart-header">
            <span class="chart-icon">🌡️</span>
            <span class="chart-title">Panel Temperature</span>
            <el-tag size="small" type="info">Daily</el-tag>
          </div>
          <div ref="tempChart" class="chart-box"></div>
        </div>

        <!-- 3. 发电量占比饼图 -->
        <div class="chart-item">
          <div class="chart-header">
            <span class="chart-icon">📊</span>
            <span class="chart-title">Generation Share</span>
            <el-tag size="small" type="warning">Live</el-tag>
          </div>
          <div ref="shareChart" class="chart-box"></div>
        </div>

        <!-- 4. 四个仪表盘卡片（一排四个） -->
        <div class="chart-item">
          <div class="chart-header">
            <span class="chart-icon">⚡</span>
            <span class="chart-title">Actual vs Expected</span>
            <el-tag size="small" type="primary">Today</el-tag>
          </div>
          <div class="metrics-row">
            <div class="metric-card">
              <div class="metric-icon">🎯</div>
              <div class="metric-info">
                <span class="metric-label">Achievement</span>
                <span class="metric-value">{{ achievementRate }}<span class="metric-unit">%</span></span>
                <el-progress :percentage="achievementRate" :stroke-width="6" color="#10b981" class="metric-progress" />
              </div>
            </div>
            <div class="metric-card">
              <div class="metric-icon">🔋</div>
              <div class="metric-info">
                <span class="metric-label">Actual Gen.</span>
                <span class="metric-value">{{ formatNumber(actualGen) }}<span class="metric-unit">kWh</span></span>
                <div class="metric-trend up">↑ {{ genTrend }}%</div>
              </div>
            </div>
            <div class="metric-card">
              <div class="metric-icon">📌</div>
              <div class="metric-info">
                <span class="metric-label">Target</span>
                <span class="metric-value">{{ formatNumber(expectedGen) }}<span class="metric-unit">kWh</span></span>
                <div class="metric-target">Daily Goal</div>
              </div>
            </div>
            <div class="metric-card">
              <div class="metric-icon">⚙️</div>
              <div class="metric-info">
                <span class="metric-label">Efficiency</span>
                <span class="metric-value">{{ efficiency }}<span class="metric-unit">%</span></span>
                <el-progress :percentage="efficiency" :stroke-width="6" color="#f59e0b" class="metric-progress" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧数据卡片 -->
    <div class="right-panel">
      <div class="image-container" v-if="!isMobile">
        <el-image src="https://aegisnx.com/wp-content/uploads/2026/05/1778468449446.png" fit="cover" class="wind-image" />
        <div class="image-overlay"></div>
      </div>

      <div class="data-fields-container">
        <div class="data-row">
          <div class="data-field-card">
            <div class="field-icon">☀️</div>
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
            <div class="field-icon">🌞</div>
            <div class="field-info">
              <span class="field-label">Irradiance</span>
              <span class="field-value">{{ irradiance }} <span class="field-unit">W/m²</span></span>
              <span class="field-trend up">↑ {{ irradTrend }}%</span>
            </div>
          </div>
          <div class="data-field-card">
            <div class="field-icon">🌡️</div>
            <div class="field-info">
              <span class="field-label">Panel Temp</span>
              <span class="field-value">{{ panelTemp }} <span class="field-unit">°C</span></span>
              <span class="field-trend">{{ tempTrend === 'up' ? '↑' : '↓' }} {{ tempChange }}%</span>
            </div>
          </div>
        </div>

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
            <div class="field-icon">⏱️</div>
            <div class="field-info">
              <span class="field-label">Sun Hours</span>
              <span class="field-value">{{ sunHours }} <span class="field-unit">h</span></span>
              <span class="field-trend up">↑ {{ sunTrend }}%</span>
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

import { useCounterStore } from '@/stores/counter'
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

// ---------- 右侧卡片数据 ----------
const currentPower = ref(1850)
const powerTrend = ref(6.5)
const todayGen = ref(14200)
const genTrend = ref(9.2)
const irradiance = ref(780)
const irradTrend = ref(4.8)
const panelTemp = ref(42.3)
const tempTrend = ref('up')
const tempChange = ref(2.1)
const revenue = ref(2.84)
const revTrend = ref(7.3)
const co2 = ref(11.2)
const co2Trend = ref(13.5)
const efficiency = ref(18.5)
const effTrend = ref(1.2)
const sunHours = ref(5.2)
const sunTrend = ref(3.4)

// ---------- 第四个图表专用数据 ----------
const actualGen = ref(14200)
const expectedGen = ref(20000)
const achievementRate = ref(71)

// ---------- 当前时间（带年月日毫秒） ----------
const currentTime = ref('')
let timeInterval = null

// ---------- ECharts 实例 ----------
const irradianceChart = ref(null)
const tempChart = ref(null)
const shareChart = ref(null)
let irradChart = null
let tempChartIns = null
let shareChartIns = null

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

// ---------- 模拟数据更新 ----------
const updateRealTimeData = () => {
  currentPower.value = Math.floor(1500 + Math.random() * 800)
  powerTrend.value = +(3 + Math.random() * 8).toFixed(1)
  todayGen.value = 12000 + Math.floor(Math.random() * 5000)
  genTrend.value = +(5 + Math.random() * 10).toFixed(1)
  irradiance.value = +(600 + Math.random() * 300).toFixed(1)
  irradTrend.value = +(2 + Math.random() * 7).toFixed(1)
  panelTemp.value = +(35 + Math.random() * 15).toFixed(1)
  tempTrend.value = Math.random() > 0.5 ? 'up' : 'down'
  tempChange.value = +(1 + Math.random() * 5).toFixed(1)
  revenue.value = +(1.8 + Math.random() * 1.5).toFixed(2)
  revTrend.value = +(4 + Math.random() * 10).toFixed(1)
  co2.value = +(8 + Math.random() * 8).toFixed(1)
  co2Trend.value = +(8 + Math.random() * 12).toFixed(1)
  efficiency.value = +(16 + Math.random() * 5).toFixed(1)
  effTrend.value = +(0.5 + Math.random() * 3).toFixed(1)
  sunHours.value = +(4 + Math.random() * 3).toFixed(1)
  sunTrend.value = +(2 + Math.random() * 6).toFixed(1)

  actualGen.value = 10000 + Math.floor(Math.random() * 12000)
  achievementRate.value = Math.min(100, Math.floor((actualGen.value / expectedGen.value) * 100))
}

// ---------- 初始化 ECharts 图表 ----------
const initCharts = () => {
  if (irradianceChart.value) {
    irradChart = echarts.init(irradianceChart.value)
    irradChart.setOption({
      tooltip: { trigger: 'axis', valueFormatter: (value) => (value !== undefined ? value.toFixed(1) + ' W/m²' : '') },
      grid: { left: '0%', right: '0%', top: 50, bottom: 0, containLabel: true },
      xAxis: { type: 'category', data: ['6', '8', '10', '12', '14', '16', '18'], axisLabel: { color: '#cbd5e1' }, axisLine: { lineStyle: { color: '#334155' } } },
      yAxis: { type: 'value', name: 'W/m²', nameTextStyle: { color: '#94a3b8' }, axisLabel: { color: '#cbd5e1' }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } } },
      series: [{
        data: [120, 320, 680, 850, 790, 540, 210], type: 'line', smooth: true,
        lineStyle: { width: 3, color: '#f97316', shadowBlur: 12, shadowColor: '#f97316' },
        areaStyle: { opacity: 0.3, color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#f97316' }, { offset: 1, color: '#0f172a' }]) },
        symbol: 'circle', symbolSize: 6, itemStyle: { color: '#f97316', borderColor: '#fff', borderWidth: 1 }
      }]
    })
  }
  if (tempChart.value) {
    tempChartIns = echarts.init(tempChart.value)
    tempChartIns.setOption({
      tooltip: { trigger: 'axis', valueFormatter: (value) => (value !== undefined ? value.toFixed(1) + ' °C' : '') },
      grid: { left: '0%', right: '0%', top: 50, bottom: 0, containLabel: true },
      xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], axisLabel: { color: '#cbd5e1' }, axisLine: { lineStyle: { color: '#334155' } } },
      yAxis: { type: 'value', name: '°C', nameTextStyle: { color: '#94a3b8' }, axisLabel: { color: '#cbd5e1' }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } } },
      series: [{
        data: [38, 42, 45, 48, 44, 41, 39], type: 'bar', barWidth: '55%', borderRadius: [8, 8, 0, 0],
        itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#ef4444' }, { offset: 1, color: '#b91c1c' }]), shadowBlur: 8, shadowColor: '#ef4444' },
        label: { show: true, position: 'top', color: '#e2e8f0', fontSize: 10, fontWeight: 'bold', formatter: '{c}°C' }
      }]
    })
  }
  if (shareChart.value) {
    shareChartIns = echarts.init(shareChart.value)
    shareChartIns.setOption({
      tooltip: { trigger: 'item', backgroundColor: 'rgba(0,0,0,0.8)' },
      legend: { show: true, textStyle: { color: '#cbd5e1' }, orient: 'vertical', left: 'left' },
      series: [{
        type: 'pie', radius: '55%', data: [
          { value: 65, name: 'Self-Consumption', itemStyle: { color: '#10b981' } },
          { value: 35, name: 'Grid Export', itemStyle: { color: '#3b82f6' } }
        ], label: { color: '#cbd5e1' }, labelLine: { length: 10 }, emphasis: { scale: true }
      }]
    })
  }
}

// ---------- 动态更新图表数据 ----------
const updateCharts = () => {
  if (irradChart) {
    const newData = [
      +(150 + Math.random() * 80).toFixed(1),
      +(350 + Math.random() * 100).toFixed(1),
      +(650 + Math.random() * 100).toFixed(1),
      +(820 + Math.random() * 80).toFixed(1),
      +(750 + Math.random() * 100).toFixed(1),
      +(500 + Math.random() * 100).toFixed(1),
      +(180 + Math.random() * 60).toFixed(1)
    ]
    irradChart.setOption({ series: [{ data: newData }] })
  }
  if (tempChartIns) {
    const newData = [
      +(35 + Math.random() * 6).toFixed(1),
      +(38 + Math.random() * 6).toFixed(1),
      +(42 + Math.random() * 5).toFixed(1),
      +(44 + Math.random() * 5).toFixed(1),
      +(40 + Math.random() * 5).toFixed(1),
      +(37 + Math.random() * 5).toFixed(1),
      +(35 + Math.random() * 5).toFixed(1)
    ]
    tempChartIns.setOption({ series: [{ data: newData }] })
  }
}

// ---------- 窗口 / 全屏自适应 ----------
const handleResize = () => {
  setTimeout(() => {
    irradChart?.resize()
    tempChartIns?.resize()
    shareChartIns?.resize()
  }, 100)
}
const isMobile = ref(false)
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}
// ---------- 生命周期 ----------
onMounted(async () => {
  checkMobile();
  const img = new Image()
  img.src = 'https://aegisnx.com/wp-content/uploads/2026/05/1778468449446.png'
  let progress = 0, msgIdx = 0
  const loadingMessages = ['Preparing assets...', 'Loading solar data...', 'Calibrating panels...', 'Establishing connection...', 'Starting dashboard...', 'Almost ready...']
  const msgInterval = setInterval(() => { if (msgIdx < loadingMessages.length - 1) loadingMessage.value = loadingMessages[++msgIdx] }, 800)
  const progInterval = setInterval(() => { if (progress < 90) { progress += Math.random() * 10; loadingProgress.value = Math.min(progress, 90) } }, 100)
  img.onload = () => {
    clearInterval(msgInterval); clearInterval(progInterval)
    loadingMessage.value = 'Ready!'; loadingProgress.value = 100
    setTimeout(async () => {
      isBackgroundLoaded.value = true
      await nextTick()
      setTimeout(initCharts, 100)
    }, 500)
  }
  img.onerror = () => {
    clearInterval(msgInterval); clearInterval(progInterval)
    loadingProgress.value = 100
    setTimeout(async () => {
      isBackgroundLoaded.value = true
      await nextTick()
      setTimeout(initCharts, 100)
    }, 300)
  }

  // 启动时间定时器（每100ms刷新）
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
  irradChart?.dispose()
  tempChartIns?.dispose()
  shareChartIns?.dispose()
})
</script>

<style scoped>
/* ===== Loading 样式 ===== */
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
.left-panel, .right-panel, .charts-container, .data-fields-container, .chart-item {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.left-panel::-webkit-scrollbar, .right-panel::-webkit-scrollbar, .charts-container::-webkit-scrollbar, .data-fields-container::-webkit-scrollbar, .chart-item::-webkit-scrollbar {
  display: none;
}

/* ===== 第四个图表：一排四个指标卡片 ===== */
.metrics-row {
  flex: 1;
  display: flex;
  flex-direction: row;
  gap: 12px;
  padding: 8px 0;
  min-height: 0;
}
.metric-card {
  flex: 1;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 16px;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  transition: all 0.3s ease;
}
.metric-card:hover {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.6);
  transform: translateY(-2px);
}
.metric-icon {
  font-size: 28px;
  margin-bottom: 8px;
}
.metric-info {
  width: 100%;
}
.metric-label {
  font-size: 12px;
  color: #94a3b8;
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
}
.metric-value {
  font-size: 20px;
  font-weight: 800;
  color: #facc15;
  font-family: monospace;
  line-height: 1.2;
}
.metric-unit {
  font-size: 12px;
  font-weight: 500;
  color: #64748b;
  margin-left: 2px;
}
.metric-trend {
  font-size: 10px;
  font-weight: 600;
  display: inline-block;
  margin-top: 6px;
  padding: 2px 6px;
  border-radius: 20px;
}
.metric-trend.up {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
}
.metric-target {
  font-size: 10px;
  color: #64748b;
  margin-top: 6px;
}
.metric-progress {
  margin-top: 8px;
  width: 90%;
}
.metric-progress :deep(.el-progress-bar__outer) {
  background-color: rgba(255,255,255,0.1);
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