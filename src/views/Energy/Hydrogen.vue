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
          <span class="loading-title">Loading Hydrogen Energy</span>
          <span class="loading-dots">...</span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Initializing Electrolysis System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Page -->
  <div v-else class="wind-energy-page">
    <!-- Left Panel -->
    <div class="left-panel">
      <div class="page-header">
        <h1 class="page-title">Hydrogen Energy</h1>
        <div class="current-time" v-if="isMobile || isFullscreen">{{ currentTime }}</div>
      </div>

      <div class="image-container" v-if="isMobile">
        <el-image
            src="https://aegisnx.com/wp-content/uploads/2026/05/1778480950258.png"
            fit="cover"
            class="wind-image"
        />
        <div class="image-overlay"></div>
      </div>

      <div class="charts-container">
        <!-- 1. 氢气产量趋势（渐变面积折线图） -->
        <div class="chart-item">
          <div class="chart-header">
            <span class="chart-icon">💧</span>
            <span class="chart-title">Hydrogen Production</span>
            <el-tag size="small" type="success">24h</el-tag>
          </div>
          <div ref="productionChart" class="chart-box"></div>
        </div>

        <!-- 2. 电解槽多仪表盘（三个环形进度条） -->
        <div class="chart-item">
          <div class="chart-header">
            <span class="chart-icon">⚙️</span>
            <span class="chart-title">Electrolyzer KPIs</span>
            <el-tag size="small" type="info">Real-time</el-tag>
          </div>
          <div class="gauges-row">
            <div class="gauge-card">
              <el-progress
                  type="circle"
                  :percentage="efficiency"
                  :stroke-width="6"
                  color="#06b6d4"
                  class="mini-gauge"
              >
                <template #default="{ percentage }">
                  <span class="gauge-value">{{ percentage }}<span class="gauge-unit">%</span></span>
                </template>
              </el-progress>
              <div class="gauge-title">Electrolyzer Eff.</div>
              <div class="gauge-desc">{{ efficiency }}%</div>
            </div>
            <div class="gauge-card">
              <el-progress
                  type="circle"
                  :percentage="hydrogenPurity"
                  :stroke-width="6"
                  color="#10b981"
                  class="mini-gauge"
              >
                <template #default="{ percentage }">
                  <span class="gauge-value">{{ percentage }}<span class="gauge-unit">%</span></span>
                </template>
              </el-progress>
              <div class="gauge-title">H₂ Purity</div>
              <div class="gauge-desc">{{ hydrogenPurity }}%</div>
            </div>
            <div class="gauge-card">
              <el-progress
                  type="circle"
                  :percentage="energyRatio"
                  :stroke-width="6"
                  color="#f59e0b"
                  class="mini-gauge"
              >
                <template #default="{ percentage }">
                  <span class="gauge-value">{{ percentage }}<span class="gauge-unit">%</span></span>
                </template>
              </el-progress>
              <div class="gauge-title">Energy Ratio</div>
              <div class="gauge-desc">{{ energyRatio }}%</div>
            </div>
          </div>
        </div>

        <!-- 3. 氢能应用分布（横向柱状图） -->
        <div class="chart-item">
          <div class="chart-header">
            <span class="chart-icon">📊</span>
            <span class="chart-title">Hydrogen Application</span>
            <el-tag size="small" type="warning">Live</el-tag>
          </div>
          <div ref="applicationChart" class="chart-box"></div>
        </div>

        <!-- 4. 制氢成本 vs 电价（双轴折线图） -->
        <div class="chart-item">
          <div class="chart-header">
            <span class="chart-icon">💰</span>
            <span class="chart-title">Production Cost vs Electricity Price</span>
            <el-tag size="small" type="primary">Weekly</el-tag>
          </div>
          <div ref="costChart" class="chart-box"></div>
        </div>
      </div>
    </div>

    <!-- Right Panel -->
    <div class="right-panel">
      <div class="image-container" v-if="!isMobile">
        <el-image
            src="https://aegisnx.com/wp-content/uploads/2026/05/1778480950258.png"
            fit="cover"
            class="wind-image"
        />
        <div class="image-overlay"></div>
      </div>

      <div class="data-fields-container">
        <div class="data-row">
          <div class="data-field-card">
            <div class="field-icon">💧</div>
            <div class="field-info">
              <span class="field-label">H₂ Production</span>
              <span class="field-value">{{ formatNumber(hydrogenProd) }} <span class="field-unit">kg</span></span>
              <span class="field-trend up">↑ {{ prodTrend }}%</span>
            </div>
          </div>
          <div class="data-field-card">
            <div class="field-icon">⚡</div>
            <div class="field-info">
              <span class="field-label">Power Consumption</span>
              <span class="field-value">{{ formatNumber(powerConsumption) }} <span class="field-unit">MWh</span></span>
              <span class="field-trend up">↑ {{ powerTrend }}%</span>
            </div>
          </div>
          <div class="data-field-card">
            <div class="field-icon">⚙️</div>
            <div class="field-info">
              <span class="field-label">Electrolyzer Eff.</span>
              <span class="field-value">{{ efficiency }}<span class="field-unit">%</span></span>
              <span class="field-trend up">↑ {{ effTrend }}%</span>
            </div>
          </div>
          <div class="data-field-card">
            <div class="field-icon">📈</div>
            <div class="field-info">
              <span class="field-label">H₂ Pressure</span>
              <span class="field-value">{{ pressure }} <span class="field-unit">bar</span></span>
              <span class="field-trend">{{ pressureTrend === 'up' ? '↑' : '↓' }} {{ pressureChange }}%</span>
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
              <span class="field-label">System Efficiency</span>
              <span class="field-value">{{ systemEfficiency }}<span class="field-unit">%</span></span>
              <span class="field-trend up">↑ {{ sysEffTrend }}%</span>
            </div>
          </div>
          <div class="data-field-card">
            <div class="field-icon">📦</div>
            <div class="field-info">
              <span class="field-label">Storage Level</span>
              <span class="field-value">{{ storageLevel }}<span class="field-unit">%</span></span>
              <span class="field-trend up">↑ {{ storageTrend }}%</span>
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

// ---------- 右侧数据 ----------
const hydrogenProd = ref(2450)
const prodTrend = ref(4.2)
const powerConsumption = ref(58.6)
const powerTrend = ref(3.5)
const efficiency = ref(74.5)
const effTrend = ref(2.1)
const pressure = ref(352)
const pressureTrend = ref('up')
const pressureChange = ref(1.8)
const revenue = ref(32.5)
const revTrend = ref(6.4)
const co2 = ref(187.3)
const co2Trend = ref(9.1)
const systemEfficiency = ref(82.3)
const sysEffTrend = ref(3.2)
const storageLevel = ref(68)
const storageTrend = ref(5.4)

// 新增仪表盘指标
const hydrogenPurity = ref(99.2)
const energyRatio = ref(68.5)

// ---------- 当前时间 ----------
const currentTime = ref('')
let timeInterval = null

// ---------- 图表实例 ----------
const productionChart = ref(null)
const applicationChart = ref(null)
const costChart = ref(null)
let productionEChart = null
let applicationEChart = null
let costEChart = null

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
  'Loading hydrogen data...',
  'Starting electrolysis...',
  'Establishing connection...',
  'Starting dashboard...',
  'Almost ready...'
]

const preloadBackground = () => new Promise((resolve) => {
  const img = new Image()
  img.src = 'https://aegisnx.com/wp-content/uploads/2026/05/1778480950258.png'
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
  hydrogenProd.value = Math.floor(2100 + Math.random() * 800)
  prodTrend.value = +(2 + Math.random() * 7).toFixed(1)
  powerConsumption.value = +(52 + Math.random() * 12).toFixed(1)
  powerTrend.value = +(1.5 + Math.random() * 6).toFixed(1)
  efficiency.value = +(68 + Math.random() * 12).toFixed(1)
  effTrend.value = +(0.8 + Math.random() * 4).toFixed(1)
  hydrogenPurity.value = +(98.5 + Math.random() * 1.2).toFixed(1)
  energyRatio.value = +(65 + Math.random() * 8).toFixed(1)
  pressure.value = Math.floor(320 + Math.random() * 60)
  pressureTrend.value = pressure.value > 350 ? 'up' : 'down'
  pressureChange.value = +(1 + Math.random() * 3).toFixed(1)
  revenue.value = +(28 + Math.random() * 12).toFixed(1)
  revTrend.value = +(3 + Math.random() * 8).toFixed(1)
  co2.value = +(160 + Math.random() * 50).toFixed(1)
  co2Trend.value = +(5 + Math.random() * 10).toFixed(1)
  systemEfficiency.value = +(78 + Math.random() * 10).toFixed(1)
  sysEffTrend.value = +(1 + Math.random() * 5).toFixed(1)
  storageLevel.value = Math.floor(55 + Math.random() * 30)
  storageTrend.value = +(2 + Math.random() * 6).toFixed(1)
}

// ---------- 初始化图表 ----------
const initCharts = () => {
  // 1. 氢气产量趋势（渐变面积折线图）
  if (productionChart.value) {
    productionEChart = echarts.init(productionChart.value)
    productionEChart.setOption({
      tooltip: { trigger: 'axis', valueFormatter: (value) => value + ' kg' },
      grid: { left: '0%', right: '0%', top: 40, bottom: 0, containLabel: true },
      xAxis: { type: 'category', data: ['0', '4', '8', '12', '16', '20', '24'], axisLabel: { color: '#cbd5e1' }, axisLine: { lineStyle: { color: '#334155' } } },
      yAxis: { type: 'value', name: 'kg', nameTextStyle: { color: '#94a3b8' }, axisLabel: { color: '#cbd5e1' }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } } },
      series: [{
        data: [180, 210, 260, 320, 310, 270, 230], type: 'line', smooth: true,
        lineStyle: { width: 3, color: '#06b6d4', shadowBlur: 12, shadowColor: '#06b6d4' },
        areaStyle: { opacity: 0.3, color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#06b6d4' }, { offset: 1, color: '#0f172a' }]) },
        symbol: 'circle', symbolSize: 6, itemStyle: { color: '#06b6d4', borderColor: '#fff', borderWidth: 1 }
      }]
    })
  }

  // 3. 氢能应用分布：横向柱状图（条形图）
  if (applicationChart.value) {
    applicationEChart = echarts.init(applicationChart.value)
    applicationEChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '0%', right: '5%', top: 20, bottom: 0, containLabel: true },
      xAxis: { type: 'value', name: 'Hydrogen (kg)', nameTextStyle: { color: '#94a3b8' }, axisLabel: { color: '#cbd5e1' }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } } },
      yAxis: { type: 'category', data: ['Industrial', 'Transport', 'Power Gen', 'Export'], axisLabel: { color: '#cbd5e1' }, axisLine: { show: false }, axisTick: { show: false } },
      series: [{
        data: [1120, 680, 360, 290], type: 'bar', barWidth: '35%', borderRadius: [0, 8, 8, 0],
        itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{ offset: 0, color: '#06b6d4' }, { offset: 1, color: '#3b82f6' }]), shadowBlur: 8, shadowColor: '#06b6d4' },
        label: { show: true, position: 'right', color: '#e2e8f0', formatter: '{c} kg' }
      }]
    })
  }

  // 4. 制氢成本 vs 电价：双轴折线图
  if (costChart.value) {
    costEChart = echarts.init(costChart.value)
    costEChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['H₂ Cost ($/kg)', 'Electricity Price (¢/kWh)'], textStyle: { color: '#cbd5e1' }, right: 10, top: 0 },
      grid: { left: '0%', right: '0%', top: 60, bottom: 0, containLabel: true },
      xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], axisLabel: { color: '#cbd5e1' }, axisLine: { lineStyle: { color: '#334155' } } },
      yAxis: [
        { type: 'value', name: '$ / kg', nameTextStyle: { color: '#94a3b8' }, axisLabel: { color: '#cbd5e1' }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } } },
        { type: 'value', name: '¢ / kWh', nameTextStyle: { color: '#94a3b8' }, axisLabel: { color: '#cbd5e1' }, splitLine: { show: false } }
      ],
      series: [
        { name: 'H₂ Cost ($/kg)', type: 'line', smooth: true, data: [4.2, 4.0, 3.9, 4.1, 4.3, 4.2, 4.0], lineStyle: { width: 2, color: '#10b981', shadowBlur: 6 }, symbol: 'circle', symbolSize: 6, label: { show: true, position: 'top', color: '#e2e8f0', formatter: '{c} $' } },
        { name: 'Electricity Price (¢/kWh)', type: 'line', smooth: true, yAxisIndex: 1, data: [7.2, 7.5, 8.1, 7.8, 7.4, 7.0, 6.8], lineStyle: { width: 2, color: '#f59e0b', shadowBlur: 6 }, symbol: 'diamond', symbolSize: 6, label: { show: true, position: 'bottom', color: '#e2e8f0', formatter: '{c}¢' } }
      ]
    })
  }
}

// ---------- 动态更新图表数据 ----------
const updateCharts = () => {
  if (productionEChart) {
    const newProd = [180 + Math.random() * 40, 210 + Math.random() * 50, 260 + Math.random() * 60, 320 + Math.random() * 40, 310 + Math.random() * 50, 270 + Math.random() * 40, 230 + Math.random() * 40].map(v => Math.floor(v))
    productionEChart.setOption({ series: [{ data: newProd }] })
  }
  if (applicationEChart) {
    const newApp = [1000 + Math.random() * 300, 600 + Math.random() * 200, 320 + Math.random() * 100, 250 + Math.random() * 100].map(v => Math.floor(v))
    applicationEChart.setOption({ series: [{ data: newApp }] })
  }
  if (costEChart) {
    const newCost = [3.8 + Math.random() * 0.6, 3.6 + Math.random() * 0.8, 3.5 + Math.random() * 0.7, 3.7 + Math.random() * 0.7, 3.9 + Math.random() * 0.7, 3.8 + Math.random() * 0.6, 3.6 + Math.random() * 0.6].map(v => +v.toFixed(1))
    const newPrice = [6.8 + Math.random() * 1.2, 7.0 + Math.random() * 1.2, 7.5 + Math.random() * 1.2, 7.2 + Math.random() * 1.2, 6.8 + Math.random() * 1.2, 6.5 + Math.random() * 1.2, 6.3 + Math.random() * 1.2].map(v => +v.toFixed(1))
    costEChart.setOption({ series: [{ data: newCost }, { data: newPrice }] })
  }
}

// ---------- 窗口/全屏自适应 ----------
const handleResize = () => {
  setTimeout(() => {
    productionEChart?.resize()
    applicationEChart?.resize()
    costEChart?.resize()
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
  productionEChart?.dispose()
  applicationEChart?.dispose()
  costEChart?.dispose()
})
</script>

<style scoped>
/* ===== 完全复用 Wind.vue 的样式，并添加多个仪表盘相关样式 ===== */
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
.left-panel, .right-panel, .charts-container, .data-fields-container, .chart-item {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.left-panel::-webkit-scrollbar, .right-panel::-webkit-scrollbar, .charts-container::-webkit-scrollbar, .data-fields-container::-webkit-scrollbar, .chart-item::-webkit-scrollbar {
  display: none;
}

/* 电解槽多仪表盘样式 */
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