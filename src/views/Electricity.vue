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
          <span class="loading-title">Loading Power Grid</span>
          <span class="loading-dots">...</span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Initializing Energy System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <div v-else class="wind-energy-page">
    <!-- 左侧图表区域 -->
    <div class="left-panel">
      <!-- 页面标题区域，包含主标题和右侧时间 -->
      <div class="page-header">
        <h1 class="page-title">Power Grid</h1>
        <div class="current-time">{{ currentTime }}</div>
      </div>

      <div class="charts-container">
        <!-- 1. 电网负荷趋势 -->
        <div class="chart-item">
          <div class="chart-header">
            <span class="chart-icon">⚡</span>
            <span class="chart-title">Grid Load Trend</span>
            <el-tag size="small" type="success">24h</el-tag>
          </div>
          <div ref="loadChart" class="chart-box"></div>
        </div>

        <!-- 2. 实时电价柱状图 -->
        <div class="chart-item">
          <div class="chart-header">
            <span class="chart-icon">💲</span>
            <span class="chart-title">Electricity Price</span>
            <el-tag size="small" type="info">Daily</el-tag>
          </div>
          <div ref="priceChart" class="chart-box"></div>
        </div>

        <!-- 3. 四个并排环形仪表盘 -->
        <div class="chart-item">
          <div class="chart-header">
            <span class="chart-icon">📐</span>
            <span class="chart-title">Key Performance Indicators</span>
            <el-tag size="small" type="warning">Live</el-tag>
          </div>
          <div class="gauges-row">
            <div class="gauge-card">
              <el-progress
                  type="circle"
                  :percentage="powerFactor"
                  :stroke-width="6"
                  color="#10b981"
                  class="mini-gauge"
              >
                <template #default="{ percentage }">
                  <span class="gauge-value">{{ percentage }}<span class="gauge-unit">%</span></span>
                </template>
              </el-progress>
              <div class="gauge-title">Power Factor</div>
              <div class="gauge-desc">{{ powerFactor }}%</div>
            </div>
            <div class="gauge-card">
              <el-progress
                  type="circle"
                  :percentage="frequencyStability"
                  :stroke-width="6"
                  color="#f59e0b"
                  class="mini-gauge"
              >
                <template #default="{ percentage }">
                  <span class="gauge-value">{{ percentage }}<span class="gauge-unit">%</span></span>
                </template>
              </el-progress>
              <div class="gauge-title">Freq Stability</div>
              <div class="gauge-desc">{{ frequency }} Hz</div>
            </div>
            <div class="gauge-card">
              <el-progress
                  type="circle"
                  :percentage="efficiency"
                  :stroke-width="6"
                  color="#3b82f6"
                  class="mini-gauge"
              >
                <template #default="{ percentage }">
                  <span class="gauge-value">{{ percentage }}<span class="gauge-unit">%</span></span>
                </template>
              </el-progress>
              <div class="gauge-title">Sys Efficiency</div>
              <div class="gauge-desc">{{ efficiency }}%</div>
            </div>
            <div class="gauge-card">
              <el-progress
                  type="circle"
                  :percentage="loadRatio"
                  :stroke-width="6"
                  color="#8b5cf6"
                  class="mini-gauge"
              >
                <template #default="{ percentage }">
                  <span class="gauge-value">{{ percentage }}<span class="gauge-unit">%</span></span>
                </template>
              </el-progress>
              <div class="gauge-title">Load Ratio</div>
              <div class="gauge-desc">{{ loadRatio }}%</div>
            </div>
          </div>
        </div>

        <!-- 4. 雷达图（替代原来的 Key Metrics 卡片） -->
        <div class="chart-item">
          <div class="chart-header">
            <span class="chart-icon">📊</span>
            <span class="chart-title">Grid Health Radar</span>
            <el-tag size="small" type="primary">Real-time</el-tag>
          </div>
          <div ref="radarChart" class="chart-box"></div>
        </div>
      </div>
    </div>

    <!-- 右侧数据卡片 -->
    <div class="right-panel">
      <div class="image-container">
        <el-image src="https://aegisnx.com/wp-content/uploads/2026/05/1778479404932.png" fit="cover" class="wind-image" />
        <div class="image-overlay"></div>
      </div>

      <div class="data-fields-container">
        <div class="data-row">
          <div class="data-field-card">
            <div class="field-icon">⚡</div>
            <div class="field-info">
              <span class="field-label">Current Load</span>
              <span class="field-value">{{ formatNumber(currentLoad) }} <span class="field-unit">MW</span></span>
              <span class="field-trend up">↑ {{ loadTrend }}%</span>
            </div>
          </div>
          <div class="data-field-card">
            <div class="field-icon">📉</div>
            <div class="field-info">
              <span class="field-label">Today Consumption</span>
              <span class="field-value">{{ formatNumber(todayConsumption) }} <span class="field-unit">MWh</span></span>
              <span class="field-trend up">↑ {{ consumptionTrend }}%</span>
            </div>
          </div>
          <div class="data-field-card">
            <div class="field-icon">💸</div>
            <div class="field-info">
              <span class="field-label">Spot Price</span>
              <span class="field-value">${{ spotPrice }} <span class="field-unit">/MWh</span></span>
              <span class="field-trend">{{ priceTrend === 'up' ? '↑' : '↓' }} {{ priceChange }}%</span>
            </div>
          </div>
          <div class="data-field-card">
            <div class="field-icon">📏</div>
            <div class="field-info">
              <span class="field-label">Power Factor</span>
              <span class="field-value">{{ powerFactor }}<span class="field-unit">%</span></span>
              <span class="field-trend up">↑ {{ pfTrend }}%</span>
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
            <div class="field-icon">🔋</div>
            <div class="field-info">
              <span class="field-label">Grid Frequency</span>
              <span class="field-value">{{ frequency }} <span class="field-unit">Hz</span></span>
              <span class="field-trend">{{ freqTrend === 'up' ? '↑' : '↓' }} {{ freqChange }}%</span>
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
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import * as echarts from 'echarts'

// ---------- 加载状态 ----------
const isBackgroundLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing assets...')

// ---------- 基础数据 ----------
const currentLoad = ref(1250)
const loadTrend = ref(3.2)
const todayConsumption = ref(28500)
const consumptionTrend = ref(5.1)
const spotPrice = ref(42.5)
const priceTrend = ref('up')
const priceChange = ref(2.3)
const powerFactor = ref(92)
const pfTrend = ref(1.1)
const frequency = ref(50.02)
const freqTrend = ref('down')
const freqChange = ref(0.05)
const efficiency = ref(94.2)
const effTrend = ref(2.3)
const revenue = ref(18.6)
const revTrend = ref(7.4)
const co2 = ref(32.5)
const co2Trend = ref(9.2)

// 额定最大负荷（假设2000 MW）
const maxLoadCapacity = 2000

// 负载率
const loadRatio = computed(() => {
  let ratio = (currentLoad.value / maxLoadCapacity) * 100
  return Math.min(100, Math.max(0, Math.floor(ratio)))
})

// 频率稳定性（0-100）
const frequencyStability = computed(() => {
  let deviation = Math.abs(frequency.value - 50)
  let stability = 100 - deviation * 2
  return Math.min(100, Math.max(80, Math.floor(stability)))
})

// 当前时间（带年月日时分秒毫秒）
const currentTime = ref('')
let timeInterval = null

// ECharts 实例
const loadChart = ref(null)
const priceChart = ref(null)
const radarChart = ref(null)
let loadEChart = null
let priceEChart = null
let radarEChart = null

let dataInterval = null
let chartInterval = null

// 辅助函数
const formatNumber = (num) => num.toLocaleString()

// 更新当前时间（YYYY-MM-DD HH:MM:SS.ms）
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

// 模拟数据更新（保留小数点）
const updateRealTimeData = () => {
  currentLoad.value = Math.floor(1000 + Math.random() * 800)
  loadTrend.value = +(1 + Math.random() * 6).toFixed(1)
  todayConsumption.value = 25000 + Math.floor(Math.random() * 8000)
  consumptionTrend.value = +(2 + Math.random() * 8).toFixed(1)
  spotPrice.value = +(35 + Math.random() * 20).toFixed(1)
  priceTrend.value = Math.random() > 0.5 ? 'up' : 'down'
  priceChange.value = +(1 + Math.random() * 5).toFixed(1)
  powerFactor.value = Math.floor(85 + Math.random() * 13)
  pfTrend.value = +(0.5 + Math.random() * 3).toFixed(1)
  let newFreq = +(49.9 + Math.random() * 0.2).toFixed(2)
  frequency.value = newFreq
  freqTrend.value = newFreq > 50 ? 'up' : 'down'
  freqChange.value = +(Math.abs(newFreq - 50) * 100 / 50).toFixed(2)
  efficiency.value = +(91 + Math.random() * 7).toFixed(1)
  effTrend.value = +(0.8 + Math.random() * 4).toFixed(1)
  revenue.value = +(12 + Math.random() * 12).toFixed(2)
  revTrend.value = +(3 + Math.random() * 9).toFixed(1)
  co2.value = +(25 + Math.random() * 18).toFixed(1)
  co2Trend.value = +(5 + Math.random() * 12).toFixed(1)
}

// 初始化 ECharts 图表
const initCharts = () => {
  // 负荷趋势图
  if (loadChart.value) {
    loadEChart = echarts.init(loadChart.value)
    loadEChart.setOption({
      tooltip: { trigger: 'axis', valueFormatter: (value) => value?.toFixed(1) + ' MW' },
      grid: { left: '8%', right: '5%', top: 20, bottom: 10, containLabel: true },
      xAxis: { type: 'category', data: ['0', '4', '8', '12', '16', '20', '24'], axisLabel: { color: '#cbd5e1' }, axisLine: { lineStyle: { color: '#334155' } } },
      yAxis: { type: 'value', name: 'MW', nameTextStyle: { color: '#94a3b8' }, axisLabel: { color: '#cbd5e1', formatter: (value) => value.toFixed(1) }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } } },
      series: [{
        data: [850, 780, 920, 1350, 1420, 1280, 980], type: 'line', smooth: true,
        lineStyle: { width: 3, color: '#3b82f6', shadowBlur: 12, shadowColor: '#3b82f6' },
        areaStyle: { opacity: 0.3, color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#3b82f6' }, { offset: 1, color: '#0f172a' }]) },
        symbol: 'circle', symbolSize: 6, itemStyle: { color: '#3b82f6', borderColor: '#fff', borderWidth: 1 }
      }]
    })
  }
  // 电价柱状图
  if (priceChart.value) {
    priceEChart = echarts.init(priceChart.value)
    priceEChart.setOption({
      tooltip: { trigger: 'axis', valueFormatter: (value) => '$' + value?.toFixed(1) + '/MWh' },
      grid: { left: '8%', right: '5%', top: 20, bottom: 10, containLabel: true },
      xAxis: { type: 'category', data: ['Off-peak', 'Mid-peak', 'Peak', 'Evening'], axisLabel: { color: '#cbd5e1' }, axisLine: { lineStyle: { color: '#334155' } } },
      yAxis: { type: 'value', name: '$/MWh', nameTextStyle: { color: '#94a3b8' }, axisLabel: { color: '#cbd5e1', formatter: (value) => value.toFixed(1) }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } } },
      series: [{
        data: [28, 45, 68, 52], type: 'bar', barWidth: '55%',
        itemStyle: { borderRadius: [8, 8, 0, 0], color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#f59e0b' }, { offset: 1, color: '#d97706' }]), shadowBlur: 8, shadowColor: '#f59e0b' },
        label: { show: true, position: 'top', color: '#e2e8f0', formatter: '${c}' }
      }]
    })
  }
  // 雷达图
  if (radarChart.value) {
    radarEChart = echarts.init(radarChart.value)
    radarEChart.setOption({
      tooltip: { trigger: 'item' },
      radar: {
        indicator: [
          { name: 'Power Factor', max: 100 },
          { name: 'Freq Stability', max: 100 },
          { name: 'System Efficiency', max: 100 },
          { name: 'Load Ratio', max: 100 },
          { name: 'Response Capability', max: 100 }
        ],
        shape: 'circle',
        center: ['50%', '50%'],
        radius: '60%',
        name: { textStyle: { color: '#cbd5e1', fontSize: 8 } },
        splitArea: { areaStyle: { color: ['rgba(59,130,246,0.1)', 'rgba(59,130,246,0.2)'] } },
        axisLine: { lineStyle: { color: '#334155' } }
      },
      series: [{
        type: 'radar',
        data: [{ value: [92, 98, 94, 62, 85], name: 'Current Status' }],
        areaStyle: { color: 'rgba(16,185,129,0.3)' },
        lineStyle: { width: 2, color: '#10b981' },
        itemStyle: { color: '#facc15' }
      }]
    })
  }
}

// 动态更新图表数据
const updateCharts = () => {
  if (loadEChart) {
    const newLoad = [
      +(800 + Math.random() * 200).toFixed(1),
      +(750 + Math.random() * 200).toFixed(1),
      +(900 + Math.random() * 200).toFixed(1),
      +(1300 + Math.random() * 200).toFixed(1),
      +(1400 + Math.random() * 200).toFixed(1),
      +(1250 + Math.random() * 200).toFixed(1),
      +(950 + Math.random() * 200).toFixed(1)
    ]
    loadEChart.setOption({ series: [{ data: newLoad }] })
  }
  if (priceEChart) {
    const newPrices = [
      +(25 + Math.random() * 10).toFixed(1),
      +(40 + Math.random() * 15).toFixed(1),
      +(65 + Math.random() * 15).toFixed(1),
      +(48 + Math.random() * 12).toFixed(1)
    ]
    priceEChart.setOption({ series: [{ data: newPrices }] })
  }
  if (radarEChart) {
    const responseCapability = Math.floor(60 + Math.random() * 40)
    const newRadarData = [
      powerFactor.value,
      frequencyStability.value,
      efficiency.value,
      loadRatio.value,
      responseCapability
    ]
    radarEChart.setOption({
      series: [{ data: [{ value: newRadarData, name: 'Current Status' }] }]
    })
  }
}

// 窗口/全屏自适应
const handleResize = () => {
  setTimeout(() => {
    loadEChart?.resize()
    priceEChart?.resize()
    radarEChart?.resize()
  }, 100)
}

// 生命周期
onMounted(async () => {
  // 预加载图片
  const img = new Image()
  img.src = 'https://aegisnx.com/wp-content/uploads/2026/05/1778479404932.png'
  let progress = 0, msgIdx = 0
  const loadingMessages = ['Preparing assets...', 'Loading grid data...', 'Syncing SCADA...', 'Establishing connection...', 'Starting dashboard...', 'Almost ready...']
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

  // 启动定时器
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
  loadEChart?.dispose()
  priceEChart?.dispose()
  radarEChart?.dispose()
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
  font-weight: bold;
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

/* 第三个图表：一排四个环形进度条 */
.gauges-row {
  flex: 1;
  display: flex;
  justify-content: space-around;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
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
  width: 70px;
  height: 70px;
}
.mini-gauge :deep(.el-progress-circle) {
  width: 70px !important;
  height: 70px !important;
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