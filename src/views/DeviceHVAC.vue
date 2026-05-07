<template>
  <div class="hvac-page">
    <h1 class="page-title">HVAC System</h1>

    <div class="main-view">
      <div class="three-columns">
        <!-- 左侧：关键指标 + 能耗趋势图 -->
        <div class="col-left">
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📈 Key Metrics</div>
            <div class="metrics-grid">
              <div class="metric-card">
                <div class="metric-icon">🏭</div>
                <div class="metric-info">
                  <div class="metric-label">Devices</div>
                  <div class="metric-value">{{ totalDevices }}</div>
                </div>
              </div>
              <div class="metric-card">
                <div class="metric-icon">📶</div>
                <div class="metric-info">
                  <div class="metric-label">Online</div>
                  <div class="metric-value">{{ onlineRate }}%</div>
                </div>
              </div>
              <div class="metric-card">
                <div class="metric-icon">⚡</div>
                <div class="metric-info">
                  <div class="metric-label">Energy</div>
                  <div class="metric-value">{{ totalEnergy }} kWh</div>
                </div>
              </div>
              <div class="metric-card">
                <div class="metric-icon">⚠️</div>
                <div class="metric-info">
                  <div class="metric-label">Alerts</div>
                  <div class="metric-value">{{ activeAlerts }}</div>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 能耗趋势图（扩展时间范围到22点） -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📉 Energy Trend (kWh)</div>
            <div ref="trendChartRef" style="height: 300px; width: 100%"></div>
          </el-card>
        </div>

        <!-- 中间：图片 + 子系统表格 -->
        <div class="col-center">
          <div class="card-img">
            <img src="../images/1778147036078.png" alt="HVAC 3D View" />
          </div>
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📊 Core Subsystems Overview</div>
            <div class="custom-table subsystem-table">
              <div class="table-header">
                <div class="th">Subsystem</div>
                <div class="th">Total</div>
                <div class="th">Online</div>
                <div class="th">Alert</div>
                <div class="th">Efficiency</div>
                <div class="th">Power (kW)</div>
              </div>
              <div class="table-body">
                <div v-for="sub in subsystems" :key="sub.name" class="table-row">
                  <div class="td">{{ sub.name }}</div>
                  <div class="td">{{ sub.total }}</div>
                  <div class="td td-online">{{ sub.online }}</div>
                  <div class="td td-alert">{{ sub.alert }}</div>
                  <div class="td">{{ sub.efficiency }}%</div>
                  <div class="td">{{ sub.power }}</div>
                </div>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 右侧：环境仪表盘 + KPI（内含迷你趋势图） -->
        <div class="col-right">
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">🌡️ Environmental Metrics</div>
            <div class="gauges-grid">
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="tempPercent" :color="tempColor" :width="100" :stroke-width="8" />
                <div class="gauge-label">Temperature</div>
                <div class="gauge-value">{{ tempValue }} °C</div>
              </div>
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="humPercent" :color="humColor" :width="100" :stroke-width="8" />
                <div class="gauge-label">Humidity</div>
                <div class="gauge-value">{{ humValue }} %</div>
              </div>
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="co2Percent" :color="co2Color" :width="100" :stroke-width="8" />
                <div class="gauge-label">CO₂</div>
                <div class="gauge-value">{{ co2Value }} ppm</div>
              </div>
              <div class="gauge-item">
                <el-progress type="dashboard" :percentage="presPercent" :color="presColor" :width="100" :stroke-width="8" />
                <div class="gauge-label">Air Pressure</div>
                <div class="gauge-value">{{ presValue }} hPa</div>
              </div>
            </div>
          </el-card>

          <!-- KPI Dashboard + 迷你趋势图（扩展时间） -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📊 KPI Dashboard</div>
            <div class="kpi-row">
              <span>Total Energy</span>
              <strong>12,480 kWh</strong>
              <span class="trend up">↑5.2%</span>
            </div>
            <div class="kpi-row">
              <span>COP (Efficiency)</span>
              <strong>4.2</strong>
              <span class="trend stable">+0.3</span>
            </div>
            <div class="kpi-row">
              <span>Carbon Saved</span>
              <strong>1,284 kg</strong>
              <span class="trend up">↑12%</span>
            </div>
            <div class="mini-chart-container">
              <div ref="kpiTrendChartRef" style="height: 100%; width: 100%"></div>
            </div>
          </el-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

// 子系统数据（包含负载字段，但未使用饼图，保留）
const subsystems = ref([
  { name: 'Chiller Plant', total: 12, online: 10, alert: 1, efficiency: 88, power: 320, load: 75 },
  { name: 'AHU', total: 23, online: 22, alert: 0, efficiency: 92, power: 145, load: 62 },
  { name: 'FAU (PAU)', total: 8, online: 8, alert: 0, efficiency: 94, power: 67, load: 48 },
  { name: 'FCU', total: 45, online: 42, alert: 2, efficiency: 86, power: 210, load: 55 },
  { name: 'VAV Terminals', total: 67, online: 65, alert: 1, efficiency: 90, power: 98, load: 70 },
  { name: 'Cooling Tower', total: 4, online: 4, alert: 0, efficiency: 92, power: 55, load: 82 }
])

// 全局统计
const totalDevices = ref(159)
const onlineRate = ref(91.8)
const totalEnergy = ref(12480)
const activeAlerts = ref(4)

// 环境指标
const tempValue = ref(24.5)
const humValue = ref(58)
const co2Value = ref(412)
const presValue = ref(1013)
const tempPercent = ref(61)
const humPercent = ref(58)
const co2Percent = ref(32)
const presPercent = ref(55)

// 颜色配置
const tempColor = [
  { color: '#3b82f6', percentage: 50 },
  { color: '#f59e0b', percentage: 75 },
  { color: '#ef4444', percentage: 100 }
]
const humColor = '#34d399'
const co2Color = [
  { color: '#10b981', percentage: 40 },
  { color: '#f97316', percentage: 70 },
  { color: '#ef4444', percentage: 100 }
]
const presColor = '#8b5cf6'

// 图表实例
const trendChartRef = ref(null)
const kpiTrendChartRef = ref(null)
let trendChart = null
let kpiTrendChart = null

// 扩展时间范围：00:00 ~ 22:00 (每2小时一个点, 共12个点)
// const fullTimeLabels = ['00:00','02:00','04:00','06:00','08:00','10:00','12:00','14:00','16:00','18:00','20:00','22:00']
// 左侧大图初始数据
// const fullData = [320, 380, 540, 780, 920, 860, 750, 690, 580, 490, 430, 380]
const fullTimeLabels = [
  '00:00','01:00','02:00','03:00','04:00','05:00',
  '06:00','07:00','08:00','09:00','10:00','11:00',
  '12:00','13:00','14:00','15:00','16:00','17:00',
  '18:00','19:00','20:00','21:00','22:00','23:00'
];

const fullData = [
  310, 300, 290, 280, 290, 300,
  350, 420, 520, 650, 780, 850,
  890, 860, 800, 730, 670, 620,
  580, 540, 500, 460, 420, 380
];

// 迷你图使用8个点（00:00 ~ 14:00）
const miniTimeLabels = ['00:00','02:00','04:00','06:00','08:00','10:00','12:00','14:00']
const miniData = [400, 360, 520, 760, 900, 840, 720, 650]

// 初始化左侧能耗趋势图（12个点）
const initTrendChart = () => {
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { top: 10, bottom: 0, left: 0, right: 0, containLabel: true },
      xAxis: { type: 'category', data: fullTimeLabels, axisLabel: { color: '#cbd5e1', rotate: 30, interval: 2 }, axisLine: { lineStyle: { color: '#334155' } } },
      yAxis: { type: 'value', name: 'kWh', nameTextStyle: { color: '#94a3b8' }, axisLabel: { color: '#cbd5e1' }, splitLine: { lineStyle: { color: '#1e293b' } } },
      series: [{ type: 'line', smooth: true, lineStyle: { width: 3, color: '#3b82f6' }, areaStyle: { opacity: 0.2, color: '#3b82f6' }, symbol: 'circle', symbolSize: 6, itemStyle: { color: '#3b82f6', borderColor: '#fff', borderWidth: 1 }, data: fullData }]
    })
  }
}

// 初始化 KPI 卡片内的迷你趋势图（8个点）
const initKpiTrendChart = () => {
  if (kpiTrendChartRef.value) {
    kpiTrendChart = echarts.init(kpiTrendChartRef.value)
    kpiTrendChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { top: 0, left: 0, right: 0, bottom: 0, containLabel: false },
      xAxis: { type: 'category', data: miniTimeLabels, axisLabel: { color: '#94a3b8', fontSize: 9, rotate: 20 }, axisLine: { show: false }, axisTick: { show: false } },
      yAxis: { type: 'value', show: false, min: 200, max: 1000 },
      series: [{ type: 'line', smooth: true, lineStyle: { width: 2, color: '#facc15' }, symbol: 'circle', symbolSize: 4, areaStyle: { opacity: 0.2, color: '#facc15' }, data: miniData }]
    })
  }
}

// 更新左侧大图数据（随机波动）
const updateTrendChart = () => {
  if (trendChart) {
    const newData = fullData.map(v => Math.max(200, v + (Math.random() - 0.5) * 80))
    trendChart.setOption({ series: [{ data: newData }] })
  }
}

// 更新迷你图数据
const updateKpiTrendChart = () => {
  if (kpiTrendChart) {
    const newData = miniData.map(v => Math.max(200, v + (Math.random() - 0.5) * 80))
    kpiTrendChart.setOption({ series: [{ data: newData }] })
  }
}

// 更新关键指标
const updateStats = () => {
  totalDevices.value = Math.floor(150 + Math.random() * 30)
  onlineRate.value = parseFloat((85 + Math.random() * 10).toFixed(1))
  totalEnergy.value = Math.floor(11000 + Math.random() * 3000)
  activeAlerts.value = Math.floor(Math.random() * 8)
}

// 环境指标百分比转换
const valueToPercent = (val, min, max) => {
  const percent = ((val - min) / (max - min)) * 100
  return Math.round(percent * 10) / 10
}

const updatePercentages = () => {
  tempPercent.value = valueToPercent(tempValue.value, 0, 40)
  humPercent.value = humValue.value
  co2Percent.value = valueToPercent(co2Value.value, 300, 800)
  presPercent.value = valueToPercent(presValue.value, 980, 1040)
}

// 定时刷新所有数据
let intervalId = null
const startMockUpdate = () => {
  intervalId = setInterval(() => {
    tempValue.value = parseFloat((20 + Math.random() * 10).toFixed(1))
    humValue.value = Math.round(40 + Math.random() * 30)
    co2Value.value = Math.round(380 + Math.random() * 200)
    presValue.value = Math.round(1000 + Math.random() * 30)
    updatePercentages()
    updateStats()
    updateTrendChart()
    updateKpiTrendChart()
  }, 5000)
}

onMounted(() => {
  initTrendChart()
  initKpiTrendChart()
  updatePercentages()
  startMockUpdate()
  window.addEventListener('resize', () => {
    trendChart?.resize()
    kpiTrendChart?.resize()
  })
})

onBeforeUnmount(() => {
  if (intervalId) clearInterval(intervalId)
  window.removeEventListener('resize', () => {})
  trendChart?.dispose()
  kpiTrendChart?.dispose()
})
</script>

<style scoped>
/* 全部样式保持原有，仅补充迷你图表容器优化 */
.hvac-page {
  height: 100%;
  background: radial-gradient(circle at 10% 20%, #0a1620, #03060c);
  padding: 24px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}
.page-title {
  text-align: center;
  margin-bottom: 12px;
  font-size: 32px;
  font-weight: 800;
  background: linear-gradient(135deg, #e2e8f0, #60a5fa);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  letter-spacing: 1px;
  text-shadow: 0 0 8px rgba(96,165,250,0.4);
  flex-shrink: 0;
}
.main-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.three-columns {
  flex: 1;
  display: flex;
  gap: 20px;
  align-items: stretch;
  min-height: 0;
}
.col-left, .col-right {
  width: 320px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.col-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 0;
}
.glass-card, .card-img {
  background: rgba(15,25,45,0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(59,130,246,0.3);
  border-radius: 20px;
  transition: all 0.3s;
}
.glass-card:hover {
  background: rgba(15,25,45,0.8);
  border-color: rgba(59,130,246,0.6);
  transform: translateY(-3px);
}
.card {
  background: transparent;
}
.card-img {
  overflow: hidden;
  background: rgba(0,0,0,0.3);
}
.card-img img {
  width: 100%;
  display: block;
  border-radius: 20px;
}
.card-header {
  font-weight: 600;
  margin-bottom: 16px;
  font-size: 16px;
  color: #e2e8f0;
  border-left: 4px solid #3b82f6;
  padding-left: 10px;
}
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 5px;
}
.metric-card {
  display: flex;
  align-items: center;
  gap: 2px;
  background: rgba(0,0,0,0.3);
  border-radius: 16px;
  padding: 12px;
}
.metric-icon {
  font-size: 22px;
  margin-right: 5px;
}
.metric-label {
  font-size: 15px;
  color: #94a3b8;
}
.metric-value {
  margin-top: 5px;
  font-size: 12px;
  font-weight: 700;
  color: #facc15;
}
.custom-table {
  width: 100%;
  font-size: 13px;
}
.subsystem-table .table-header,
.subsystem-table .table-row {
  grid-template-columns: 1.3fr 0.6fr 0.6fr 0.6fr 0.8fr 0.8fr;
}
.table-header {
  display: grid;
  padding: 12px 0;
  border-bottom: 1px solid rgba(59,130,246,0.4);
  color: #a0b3c9;
  font-weight: 600;
  background: rgba(0,0,0,0.2);
  border-radius: 12px 12px 0 0;
}
.th, .td { padding: 0 6px; text-align: center; }
.td { color: #ccc9cd; }
.table-body { display: flex; flex-direction: column; }
.table-row {
  display: grid;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  transition: all 0.2s;
}
.table-row:hover {
  background: rgba(59,130,246,0.1);
  border-radius: 12px;
  transform: translateX(4px);
}
.td-online { color: #34d399; font-weight: 600; }
.td-alert { color: #fbbf24; font-weight: 600; }
.gauges-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 8px;
}
.gauge-item { text-align: center; }
.gauge-label { font-size: 13px; color: #cbd5e1; margin-top: 8px; }
.gauge-value { font-size: 14px; font-weight: 700; color: #facc15; margin-top: 4px; }
.kpi-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  font-size: 13px;
  color: #cbd5e6;
}
.kpi-row strong {
  font-size: 16px;
  color: #facc15;
}
.trend {
  font-size: 12px;
  margin-left: 8px;
}
.trend.up { color: #34d399; }
.trend.stable { color: #fbbf24; }
.mini-chart-container {
  margin-top: 20px;
  width: 100%;
  border-top: 1px solid rgba(59,130,246,0.2);
}
.mini-chart-label {
  text-align: center;
  font-size: 12px;
  color: #a0b3c9;
  margin-top: 8px;
  letter-spacing: 0.5px;
}
.glass-card::-webkit-scrollbar,
.el-card__body::-webkit-scrollbar {
  display: none;
}
</style>

<style>
.el-card__body {
  scrollbar-width: none;
  -ms-overflow-style: none;
}
</style>