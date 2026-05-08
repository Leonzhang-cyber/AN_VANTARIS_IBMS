<template>
  <div class="dashboard">
    <div class="top-header">
      <div class="header-left"></div>
      <div class="header-title">
        <div class="main-title">SMART BUILDING<br></div>
      </div>
      <div class="datetime">{{ currentTime }}</div>
    </div>

    <div class="content-area">
      <div class="left-panel">
        <div class="glass-card resources">
          <div class="card-title">💧⚡❄️ Building Energy</div>
          <div class="resource-grid">
            <div class="resource-item">
              <el-progress type="circle" :percentage="waterPercent" :width="80" :stroke-width="8" color="#3b82f6" />
              <div class="resource-label">Water</div>
              <div class="resource-value">{{ waterUsage }} L</div>
              <div class="resource-cost">💰 ${{ waterCost }}</div>
            </div>
            <div class="resource-item">
              <el-progress type="circle" :percentage="elecPercent" :width="80" :stroke-width="8" color="#f59e0b" />
              <div class="resource-label">Electricity</div>
              <div class="resource-value">{{ elecUsage }} kWh</div>
              <div class="resource-cost">💰 ${{ elecCost }}</div>
            </div>
            <div class="resource-item">
              <el-progress type="circle" :percentage="hvacPercent" :width="80" :stroke-width="8" color="#10b981" />
              <div class="resource-label">HVAC</div>
              <div class="resource-value">{{ hvacUsage }} kWh</div>
              <div class="resource-cost">💰 ${{ hvacCost }}</div>
            </div>
          </div>
        </div>

        <div class="glass-card parking">
          <div class="card-title">👥 Floor Occupancy</div>
          <div class="parking-stats">
            <div class="parking-info">
              <span>Current: <strong>{{ floorPeople }}</strong> / {{ floorMax }}</span>
              <span>Capacity: <strong>{{ floorPercent }}%</strong></span>
            </div>
            <el-progress :percentage="floorPercent" :stroke-width="12" color="#8b5cf6" />
          </div>
        </div>

        <div class="glass-card device-list">
          <div class="card-title">📊 Equipment Proportion</div>
          <div ref="deviceBarChart" style="height: 220px; width: 100%"></div>
        </div>
      </div>

      <div class="center-void"></div>

      <div class="right-panel">
        <div class="glass-card alert-list-fixed">
          <div class="card-header-line">
            <span class="card-title">🔔 Building Alerts</span>
            <el-tag type="danger" size="small" effect="dark">{{ alerts.length }} unresolved</el-tag>
          </div>
          <div class="alert-items-fixed">
            <div v-for="(alert, idx) in alerts" :key="idx" class="alert-item">
              <div class="alert-device">{{ alert.device }}</div>
              <div class="alert-content">{{ alert.content }}</div>
              <div class="alert-time">{{ alert.time }}</div>
            </div>
          </div>
        </div>

        <div class="glass-card employee-dashboard">
          <div class="card-title">🌡️ Environment Trend</div>
          <div ref="envLineChart" style="height: 180px; width: 100%"></div>
        </div>

        <div class="glass-card energy-report">
          <div class="card-title">📈 24h Energy Trend</div>
          <div ref="energyLineChart" style="height: 180px; width: 100%"></div>
        </div>
      </div>
    </div>

    <div class="glass-card kpi-strip">
      <div class="kpi-item">
        <span class="kpi-label">🏢 Total Devices</span>
        <span class="kpi-value">{{ deviceTotal }}</span>
      </div>
      <div class="kpi-item">
        <span class="kpi-label">📶 Online Rate</span>
        <span class="kpi-value">{{ onlineRate }}%</span>
      </div>
      <div class="kpi-item">
        <span class="kpi-label">🌡️ Avg Temp</span>
        <span class="kpi-value">{{ avgTemp }}℃</span>
      </div>
      <div class="kpi-item">
        <span class="kpi-label">💰 Total Cost</span>
        <span class="kpi-value">{{ totalCost }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

const currentTime = ref('')

const deviceTotal = ref(186)
const onlineRate = ref(97.2)
const totalEnergy = ref(4280)
const avgTemp = ref(25.2)

const waterUsage = ref(860)
const elecUsage = ref(4280)
const hvacUsage = ref(2150)

const waterTarget = 1500
const elecTarget = 6000
const hvacTarget = 3500

const waterPercent = ref(57.3)
const elecPercent = ref(71.3)
const hvacPercent = ref(61.4)

const waterCost = ref(0)
const elecCost = ref(0)
const hvacCost = ref(0)
const totalCost = ref(0)

const floorMax = 350
const floorPeople = ref(210)
const floorPercent = ref(60)

let deviceBarChart = ref(null)
let envLineChart = ref(null)
let energyLineChart = ref(null)

let deviceBarIns = null
let envLineIns = null
let energyLineIns = null

// 改成 24 小时，每 4 小时一个点
const envLineData = ref({
  time: ['00:00','04:00','08:00','12:00','16:00','20:00','24:00'],
  temp: [22,23,25,27,26,24,23],
  humidity: [45,48,52,55,50,46,44],
  co2: [520,560,620,680,630,580,540]
})

const energyLineData = ref({
  time: ['00:00','04:00','08:00','12:00','16:00','20:00','24:00'],
  power: [210,380,650,580,490,270,230]
})

const deviceBarData = ref({
  nameList: ['HVAC','Lighting','Elevator','Security','Sensor'],
  valueList: [42,56,8,26,34]
})
const barColor = ['#3b82f6','#f59e0b','#10b981','#8b5cf6','#ef4444']

const alerts = ref([
  { device: 'Floor 5 HVAC', content: 'Temperature abnormal', time: '09:32' },
  { device: 'Floor 2 Light', content: 'Over current', time: '09:15' },
  { device: 'Pump Room', content: 'Water pressure low', time: '08:50' },
  { device: 'Parking Gate', content: 'Communication lost', time: '08:20' },
])

let timeTimer = null
let dataInterval = null

const updateTime = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  const ms = String(now.getMilliseconds()).padStart(3, '0')
  const tzOffset = -now.getTimezoneOffset() / 60
  const tzSign = tzOffset >= 0 ? '+' : ''
  currentTime.value = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}.${ms} UTC${tzSign}${tzOffset}`
}
updateTime()
timeTimer = setInterval(updateTime, 1000)

function randomVariation(base, rangePercent = 0.05) {
  const change = base * (Math.random() - 0.5) * rangePercent * 2
  return Math.max(0, Math.round((base + change) * 10) / 10)
}

function updateCosts() {
  waterCost.value = (waterUsage.value * 0.5).toFixed(2)
  elecCost.value = (elecUsage.value * 0.13).toFixed(2)
  hvacCost.value = (hvacUsage.value * 0.15).toFixed(2)
  totalCost.value = (
      parseFloat(waterCost.value) +
      parseFloat(elecCost.value) +
      parseFloat(hvacCost.value)
  ).toFixed(2)
}

function refreshChartData() {
  envLineData.value.temp = envLineData.value.temp.map(item =>
      Math.max(18, Math.min(32, randomVariation(item, 0.08)))
  )
  envLineData.value.humidity = envLineData.value.humidity.map(item =>
      Math.max(30, Math.min(70, randomVariation(item, 0.1)))
  )
  envLineData.value.co2 = envLineData.value.co2.map(item =>
      Math.max(400, Math.min(900, randomVariation(item, 0.07)))
  )
  avgTemp.value = (envLineData.value.temp.reduce((a,b)=>a+b,0)/envLineData.value.temp.length).toFixed(1)

  energyLineData.value.power = energyLineData.value.power.map(item =>
      Math.max(100, randomVariation(item, 0.12))
  )

  deviceBarData.value.valueList = deviceBarData.value.valueList.map(item =>
      Math.floor(randomVariation(item, 0.06))
  )

  updateAllCharts()
}

function refreshRealTimeData() {
  deviceTotal.value = Math.floor(randomVariation(186, 0.03))
  onlineRate.value = randomVariation(97.2, 0.02).toFixed(1)

  waterUsage.value = Math.floor(randomVariation(860, 0.07))
  waterPercent.value = Math.min(100, ((waterUsage.value / waterTarget) * 100).toFixed(1))

  elecUsage.value = Math.floor(randomVariation(4280, 0.07))
  elecPercent.value = Math.min(100, ((elecUsage.value / elecTarget) * 100).toFixed(1))

  hvacUsage.value = Math.floor(randomVariation(2150, 0.07))
  hvacPercent.value = Math.min(100, ((hvacUsage.value / hvacTarget) * 100).toFixed(1))

  totalEnergy.value = elecUsage.value + hvacUsage.value
  updateCosts()

  floorPeople.value = Math.min(floorMax, Math.max(50, Math.floor(randomVariation(210, 0.1))))
  floorPercent.value = ((floorPeople.value / floorMax) * 100).toFixed(1)

  const newLen = Math.min(6, Math.max(3, alerts.value.length + (Math.random() > 0.65 ? 1 : -1)))
  if (newLen > alerts.value.length) {
    const devices = ['Floor 3 AC', 'Parking Light', 'Elevator 2', 'Fire Alarm']
    const contents = ['High temp', 'Power surge', 'Door abnormal', 'Sensor fault']
    alerts.value.unshift({
      device: devices[Math.floor(Math.random() * 4)],
      content: contents[Math.floor(Math.random() * 4)],
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    })
    if (alerts.value.length > 6) alerts.value.pop()
  } else if (newLen < alerts.value.length) {
    alerts.value.pop()
  }

  refreshChartData()
}

function initAllCharts() {
  deviceBarIns = echarts.init(deviceBarChart.value)
  envLineIns = echarts.init(envLineChart.value)
  energyLineIns = echarts.init(energyLineChart.value)
  updateAllCharts()
}

function updateAllCharts() {
  deviceBarIns.setOption({
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0,0,0,0.7)',
      borderColor: 'rgba(59,130,246,0.5)',
      textStyle: { color: '#fff' }
    },
    grid: { left: '8%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: deviceBarData.value.nameList,
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.2)' } },
      axisLabel: { color: '#cbd5e1' }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      axisLine: { show: false },
      axisLabel: { color: '#94a3b8' }
    },
    series: [{
      type: 'bar',
      data: deviceBarData.value.valueList.map((val, idx) => ({
        value: val,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: barColor[idx] },
            { offset: 1, color: 'rgba(0,0,0,0.3)' }
          ])
        }
      })),
      barWidth: '40%',
      borderRadius: [6,6,0,6]
    }]
  })

  envLineIns.setOption({
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(0,0,0,0.6)' },
    grid: { left: '3%', right: '4%', bottom: '3%', top:'15%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: envLineData.value.time, axisLine:{lineStyle:{color:'#666'}} },
    yAxis: { type: 'value', splitLine:{lineStyle:{color:'rgba(255,255,255,0.1)'}}, axisLine:{lineStyle:{color:'#666'}} },
    series: [
      { name:'Temp(℃)', type:'line', data:envLineData.value.temp, smooth:true, color:'#f59e0b' },
      { name:'Humidity(%)', type:'line', data:envLineData.value.humidity, smooth:true, color:'#3b82f6' },
      { name:'CO2(ppm)', type:'line', data:envLineData.value.co2, smooth:true, color:'#10b981' }
    ]
  })

  energyLineIns.setOption({
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(0,0,0,0.6)' },
    grid: { left: '3%', right: '4%', bottom: '3%', top:'15%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: energyLineData.value.time, axisLine:{lineStyle:{color:'#666'}} },
    yAxis: { type: 'value', splitLine:{lineStyle:{color:'rgba(255,255,255,0.1)'}}, axisLine:{lineStyle:{color:'#666'}} },
    series: [
      { name:'Power(kWh)', type:'line', data:energyLineData.value.power, smooth:true, color:'#8b5cf6', areaStyle:{color:'rgba(139,92,246,0.2)'} }
    ]
  })
}

function resizeCharts() {
  deviceBarIns?.resize()
  envLineIns?.resize()
  energyLineIns?.resize()
}

onMounted(() => {
  initAllCharts()
  refreshRealTimeData()
  dataInterval = setInterval(refreshRealTimeData, 3000)
  window.addEventListener('resize', resizeCharts)
})

onBeforeUnmount(() => {
  clearInterval(timeTimer)
  clearInterval(dataInterval)
  window.removeEventListener('resize', resizeCharts)
  deviceBarIns?.dispose()
  envLineIns?.dispose()
  energyLineIns?.dispose()
})
</script>

<style scoped>
.dashboard {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  background-image: url('@/images/1778231064187.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
  font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
}
.top-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 28px 8px 28px;
  background: transparent;
  margin: 0px 24px 0 24px;
}
.header-left { width: 140px; }
.header-title { text-align: center; flex-grow: 1; }
.main-title {
  font-size: 44px;
  font-weight: 800;
  line-height: 1.2;
  background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: #f0f9ff;
  text-shadow: 0 0 15px rgba(186, 230, 253, 0.4);
  letter-spacing: 3px;
}
.datetime {
  font-size: 16px;
  color: #0ff;
  font-weight: 600;
  background: transparent;
  padding: 8px 20px;
  border-radius: 12px;
  backdrop-filter: blur(8px);
  width: auto;
  min-width: 280px;
  text-align: center;
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  letter-spacing: 1px;
  box-shadow: 0 0 10px rgba(0, 255, 255, 0.3), inset 0 0 5px rgba(0, 255, 255, 0.1);
  border: 1px solid rgba(0, 255, 255, 0.5);
  text-shadow: 0 0 5px #0ff;
}
.kpi-strip {
  display: flex;
  justify-content: space-around;
  gap: 20px;
  margin: 10px 24px 20px 24px;
  padding: 12px 20px;
}
.kpi-item {
  display: flex;
  gap: 12px;
  align-items: baseline;
  font-size: 15px;
}
.kpi-label {
  color: #94a3b8;
  font-weight: 500;
}
.kpi-value {
  font-size: 24px;
  font-weight: 800;
  color: #facc15;
  font-family: monospace;
  text-shadow: 0 0 5px rgba(250,204,21,0.5);
}
.content-area {
  flex: 1;
  display: flex;
  justify-content: space-between;
  padding: 0 24px 24px 24px;
  gap: 32px;
  overflow-y: auto;
}
.left-panel { width: 320px; flex-shrink: 0; }
.right-panel { width: 380px; flex-shrink: 0; }
.center-void { flex: 1; min-width: 40px; }
.glass-card {
  background: transparent;
  backdrop-filter: none;
  border-radius: 28px;
  border: 1px solid rgba(59, 130, 246, 0.3);
  box-shadow: 0 20px 35px -12px rgba(0, 0, 0, 0.6),
  0 0 0 1px rgba(255, 255, 255, 0.05) inset,
  0 -1px 0 1px rgba(255, 255, 255, 0.02) inset;
  padding: 18px;
  transition: all 0.3s cubic-bezier(0.2, 0.9, 0.4, 1.1);
  margin-bottom: 20px;
}
.glass-card:hover {
  background: rgba(8, 16, 28, 0.6);
  backdrop-filter: blur(8px);
  transform: translateY(-4px);
  border-color: rgba(59, 130, 246, 0.6);
  box-shadow: 0 28px 40px -14px rgba(0, 0, 0, 0.7),
  0 0 0 1px rgba(255, 255, 255, 0.1) inset,
  0 -1px 0 1px rgba(255, 255, 255, 0.04) inset;
}
.card-title {
  font-size: 18px;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 10px;
  padding-left: 8px;
  border-left: 4px solid #3b82f6;
}
.resource-grid {
  display: flex;
  justify-content: space-around;
  text-align: center;
  margin-bottom: 16px;
}
.resource-item .resource-label {
  margin-top: 8px;
  font-size: 13px;
  color: #cbd5e1;
}
.resource-value {
  font-size: 14px;
  font-weight: bold;
  color: #facc15;
}
.resource-cost {
  font-size: 12px;
  color: #a5f3fc;
  margin-top: 4px;
  font-weight: 500;
}
.parking-stats { margin-top: 5px; }
.parking-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  color: #cbd5e1;
  font-size: 14px;
}
.parking-info strong { color: #facc15; }
.alert-list-fixed {
  display: flex;
  flex-direction: column;
  height: 180px;
}
.alert-items-fixed {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.alert-items-fixed::-webkit-scrollbar { display: none; }
.alert-item {
  background: rgba(0,0,0,0.3);
  border-radius: 16px;
  padding: 10px 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: 0.2s;
}
.alert-item:hover {
  background: rgba(239,68,68,0.2);
  border-left: 2px solid #ef4444;
}
.alert-device {
  font-weight: 600;
  color: #facc15;
  font-size: 12px;
}
.alert-content {
  flex: 1;
  margin: 0 10px;
  font-size: 12px;
  color: #e2e8f0;
}
.alert-time {
  font-size: 11px;
  color: #94a3b8;
  font-family: monospace;
}
.energy-timeline {
  display: flex;
  flex-direction: column;
  gap: 0px;
}
.energy-item {
  display: flex;
  align-items: center;
  gap: 12px;
  border-radius: 16px;
  padding: 6px 8px;
  transition: all 0.2s;
}
.energy-item:hover {
  background: rgba(255,255,255,0.05);
  transform: scale(1.01);
}
.time-badge {
  width: 100px;
  font-size: 11px;
  font-weight: 600;
  color: #a5f3fc;
  background: rgba(0,0,0,0.4);
  padding: 4px 8px;
  border-radius: 20px;
  text-align: center;
}
.energy-value {
  width: 80px;
  font-family: monospace;
  font-weight: bold;
  color: #facc15;
  font-size: 14px;
}
.energy-change {
  width: 60px;
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}
.energy-change.positive { color: #f59e0b; }
.energy-change.negative { color: #10b981; }
.energy-bar-container {
  flex: 1;
  height: 6px;
  background: rgba(255,255,255,0.2);
  border-radius: 3px;
  overflow: hidden;
}
.energy-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s;
}
.card-header-line {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 12px;
  border-bottom: 1px dashed rgba(59,130,246,0.4);
  padding-bottom: 6px;
}
:deep(.el-progress-circle__track) {
  stroke: rgba(255,255,255,0.2);
}
:deep(.el-progress__text) {
  color: #fff;
  font-weight: bold;
}
.content-area::-webkit-scrollbar {
  width: 5px;
}
.content-area::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.5);
  border-radius: 4px;
}
.content-area::-webkit-scrollbar-thumb {
  background: #3b82f6;
  border-radius: 4px;
}
</style>