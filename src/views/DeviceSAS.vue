<!-- DeviceHSAS.vue -->
<template>
  <div class="hvac-page">
    <h1 class="page-title">SAS System</h1>

    <div class="main-view">
      <div class="three-columns">
        <!-- 左侧：关键指标 + 事件趋势图 -->
        <div class="col-left">
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📈 Key Metrics</div>
            <div class="metrics-grid">
              <div class="metric-card">
                <div class="metric-icon">🔐</div>
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
                <div class="metric-icon">⚠️</div>
                <div class="metric-info">
                  <div class="metric-label">Events</div>
                  <div class="metric-value">{{ totalEvents }}</div>
                </div>
              </div>
              <div class="metric-card">
                <div class="metric-icon">🚨</div>
                <div class="metric-info">
                  <div class="metric-label">Alerts</div>
                  <div class="metric-value">{{ activeAlerts }}</div>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 安防事件趋势图 -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📉 Security Event Trend</div>
            <div ref="trendChartRef" style="height: 300px; width: 100%"></div>
          </el-card>
        </div>

        <!-- 中间：图片 + 子系统表格 -->
        <div class="col-center">
          <div class="card-img">
            <img src="../images/1778147271130.png" alt="Security 3D View" />
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
                <div class="th">Status</div>
              </div>
              <div class="table-body">
                <div v-for="sub in subsystems" :key="sub.name" class="table-row">
                  <div class="td">{{ sub.name }}</div>
                  <div class="td">{{ sub.total }}</div>
                  <div class="td td-online">{{ sub.online }}</div>
                  <div class="td td-alert">{{ sub.alert }}</div>
                  <div class="td">{{ sub.efficiency }}%</div>
                  <div class="td">{{ sub.status }}</div>
                </div>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 右侧：环境指标 + KPI（内含迷你趋势图） -->
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

          <!-- KPI Dashboard + 迷你趋势图 -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">📊 KPI Dashboard</div>
            <div class="kpi-row">
              <span>Total Events</span>
              <strong>{{ totalEvents }} /day</strong>
              <span class="trend up">↑8.3%</span>
            </div>
            <div class="kpi-row">
              <span>Response Time</span>
              <strong>2.4 min</strong>
              <span class="trend stable">-0.2</span>
            </div>
            <div class="kpi-row">
              <span>Incident Rate</span>
              <strong>0.8%</strong>
              <span class="trend up">↑0.1%</span>
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

// 安防子系统数据
const subsystems = ref([
  { name: 'Access Control', total: 45, online: 43, alert: 1, efficiency: 96, status: 'Healthy' },
  { name: 'CCTV', total: 128, online: 124, alert: 2, efficiency: 94, status: 'Degraded' },
  { name: 'Intrusion Detection', total: 32, online: 30, alert: 0, efficiency: 98, status: 'Healthy' },
  { name: 'Visitor Management', total: 12, online: 12, alert: 0, efficiency: 99, status: 'Healthy' },
  { name: 'Patrol System', total: 8, online: 7, alert: 1, efficiency: 87, status: 'Alert' },
  { name: 'Emergency Comm', total: 15, online: 15, alert: 0, efficiency: 95, status: 'Healthy' }
])

// 全局统计
const totalDevices = ref(240)
const onlineRate = ref(95.2)
const totalEvents = ref(186)
const activeAlerts = ref(4)

// 环境指标（可保持不变）
const tempValue = ref(23.8)
const humValue = ref(52)
const co2Value = ref(398)
const presValue = ref(1015)
const tempPercent = ref(60)
const humPercent = ref(52)
const co2Percent = ref(28)
const presPercent = ref(58)

// 颜色配置（沿用）
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

// 事件趋势（24小时数据）
const fullTimeLabels = [
  '00:00','01:00','02:00','03:00','04:00','05:00',
  '06:00','07:00','08:00','09:00','10:00','11:00',
  '12:00','13:00','14:00','15:00','16:00','17:00',
  '18:00','19:00','20:00','21:00','22:00','23:00'
];
const fullData = [
  12, 8, 5, 3, 2, 4,
  15, 28, 42, 55, 48, 52,
  46, 38, 44, 52, 48, 45,
  38, 32, 28, 22, 18, 14
];

// 迷你图数据（8个点）
const miniTimeLabels = ['00:00','02:00','04:00','06:00','08:00','10:00','12:00','14:00']
const miniData = [15, 10, 6, 8, 22, 38, 45, 42]

// 初始化左侧趋势图
const initTrendChart = () => {
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { top: 10, bottom: 0, left: 0, right: 0, containLabel: true },
      xAxis: { type: 'category', data: fullTimeLabels, axisLabel: { color: '#cbd5e1', rotate: 30, interval: 2 }, axisLine: { lineStyle: { color: '#334155' } } },
      yAxis: { type: 'value', name: 'Events', nameTextStyle: { color: '#94a3b8' }, axisLabel: { color: '#cbd5e1' }, splitLine: { lineStyle: { color: '#1e293b' } } },
      series: [{ type: 'line', smooth: true, lineStyle: { width: 3, color: '#ef4444' }, areaStyle: { opacity: 0.2, color: '#ef4444' }, symbol: 'circle', symbolSize: 6, itemStyle: { color: '#ef4444', borderColor: '#fff', borderWidth: 1 }, data: fullData }]
    })
  }
}

// 初始化迷你趋势图
const initKpiTrendChart = () => {
  if (kpiTrendChartRef.value) {
    kpiTrendChart = echarts.init(kpiTrendChartRef.value)
    kpiTrendChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { top: 0, left: 0, right: 0, bottom: 0, containLabel: false },
      xAxis: { type: 'category', data: miniTimeLabels, axisLabel: { color: '#94a3b8', fontSize: 9, rotate: 20 }, axisLine: { show: false }, axisTick: { show: false } },
      yAxis: { type: 'value', show: false, min: 0, max: 80 },
      series: [{ type: 'line', smooth: true, lineStyle: { width: 2, color: '#facc15' }, symbol: 'circle', symbolSize: 4, areaStyle: { opacity: 0.2, color: '#facc15' }, data: miniData }]
    })
  }
}

// 更新左侧大图数据
const updateTrendChart = () => {
  if (trendChart) {
    const newData = fullData.map(v => Math.max(0, v + (Math.random() - 0.5) * 10))
    trendChart.setOption({ series: [{ data: newData }] })
  }
}

// 更新迷你图数据
const updateKpiTrendChart = () => {
  if (kpiTrendChart) {
    const newData = miniData.map(v => Math.max(0, v + (Math.random() - 0.5) * 12))
    kpiTrendChart.setOption({ series: [{ data: newData }] })
  }
}

// 更新关键指标
const updateStats = () => {
  totalDevices.value = Math.floor(220 + Math.random() * 30)
  onlineRate.value = parseFloat((92 + Math.random() * 5).toFixed(1))
  totalEvents.value = Math.floor(150 + Math.random() * 60)
  activeAlerts.value = Math.floor(Math.random() * 6)
}

// 环境指标转换
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

// 定时刷新
let intervalId = null
const startMockUpdate = () => {
  intervalId = setInterval(() => {
    tempValue.value = parseFloat((18 + Math.random() * 10).toFixed(1))
    humValue.value = Math.round(35 + Math.random() * 30)
    co2Value.value = Math.round(380 + Math.random() * 80)
    presValue.value = Math.round(1005 + Math.random() * 20)
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