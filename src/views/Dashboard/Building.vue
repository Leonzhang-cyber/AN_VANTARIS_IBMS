<template>
  <div v-if="isBackgroundLoaded" class="dashboard">
    <div class="top-header">
      <div class="header-left"></div>
      <div class="header-title">
        <div class="main-title">SMART BUILDING<br></div>
      </div>
      <div class="datetime" v-if="isFullscreen">{{ currentTime }}</div>
    </div>

    <div class="content-area">
      <div class="left-panel">
        <!-- 厕所占用卡片 -->
        <div class="glass-card restroom-card">
          <div class="card-title">🚻 Restroom Availability</div>
          <div class="restroom-table">
            <div class="restroom-row-header">
              <span>Floor</span>
              <span>Status</span>
              <span>Available</span>
            </div>
            <div v-for="r in computedRestrooms" :key="r.floor" class="restroom-row">
              <span class="floor-name">{{ r.floor }}</span>
              <span class="status-badge" :class="r.statusClass">{{ r.statusText }}</span>
              <span class="available-count">
                <span class="count-number">{{ r.free }}</span>
                <span class="count-total">/{{ r.total }}</span>
              </span>
            </div>
          </div>
        </div>

        <!-- Building Energy 卡片 -->
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

        <!-- Equipment Proportion 图表 -->
        <div class="glass-card device-list">
          <div class="card-title">📊 Equipment Proportion</div>
          <div ref="deviceBarChart" style="height: 220px; width: 100%"></div>
        </div>
      </div>

      <div class="center-void"></div>

      <div class="right-panel">
        <!-- 电梯运行卡片 -->
        <div class="glass-card elevator-card">
          <div class="card-title">🚪 Lift Status</div>
          <div class="elevator-list">
            <div v-for="e in elevators" :key="e.id" class="elevator-row">
              <span class="lift-name">{{ e.name }}</span>
              <span class="lift-floor">{{ e.currentFloor }}F</span>
              <span class="lift-status" :class="e.statusClass">{{ e.statusText }}</span>
              <span class="lift-call" v-if="e.callFloor">{{ e.callFloor }}F {{ e.callDirection === 'up' ? '↑' : '↓' }} {{ e.eta }}s</span>
              <span class="lift-call" v-else>—</span>
            </div>
          </div>
          <div class="elevator-footer">
            <span>{{ totalTripsToday }} trips</span>
            <span>{{ totalElevatorEnergy }} kWh</span>
          </div>
        </div>

        <!-- Environment Trend 图表 -->
        <div class="glass-card employee-dashboard">
          <div class="card-title">🌡️ Environment Trend</div>
          <div ref="envLineChart" style="height: 180px; width: 100%"></div>
        </div>

        <!-- 24h Energy Trend 图表 -->
        <div class="glass-card energy-report">
          <div class="card-title">📈 24h Energy Trend</div>
          <div ref="energyLineChart" style="height: 180px; width: 100%"></div>
        </div>
      </div>
    </div>

    <!-- KPI 栏 -->
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

  <!-- Loading 页面 -->
  <div v-else class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">
          <span class="loading-title">Loading</span>
          <span class="loading-dots">...</span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Initializing Smart Building System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
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
// ==================== 响应式数据 ====================
const currentTime = ref('')
const isBackgroundLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing assets...')

// 能耗数据
const deviceTotal = ref(186)
const onlineRate = ref(97.2)
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

// 楼层占用
const floorMax = 350
const floorPeople = ref(210)
const floorPercent = ref(60)

// 厕所数据（占用/总数）
const restrooms = ref([
  { floor: '1F Lobby', total: 8, occupied: 3, statusText: 'Available', statusClass: 'available' },
  { floor: '2F Office', total: 6, occupied: 2, statusText: 'Available', statusClass: 'available' },
  { floor: '3F Office', total: 6, occupied: 5, statusText: 'Limited', statusClass: 'limited' },
  { floor: '4F Meeting', total: 4, occupied: 1, statusText: 'Available', statusClass: 'available' },
  { floor: 'B1 Parking', total: 8, occupied: 6, statusText: 'Limited', statusClass: 'limited' }
])

const computedRestrooms = computed(() => {
  return restrooms.value.map(r => ({
    ...r,
    free: r.total - r.occupied,
    percent: (r.occupied / r.total) * 100
  }))
})

// 电梯数据
const elevators = ref([
  { id: 1, name: 'A', currentFloor: 5, passengers: 8, capacity: 15, tripCount: 78, statusText: 'Moving', statusClass: 'moving', callFloor: 9, callDirection: 'up', eta: 12 },
  { id: 2, name: 'B', currentFloor: 1, passengers: 0, capacity: 15, tripCount: 45, statusText: 'Idle', statusClass: 'idle', callFloor: null, callDirection: null, eta: 0 },
  { id: 3, name: 'C', currentFloor: 8, passengers: 12, capacity: 15, tripCount: 92, statusText: 'Moving', statusClass: 'moving', callFloor: 3, callDirection: 'down', eta: 18 },
  { id: 4, name: 'D', currentFloor: 1, passengers: 0, capacity: 15, tripCount: 12, statusText: 'Maint', statusClass: 'maint', callFloor: null, callDirection: null, eta: 0 }
])

// 计算总行程和能耗（示例）
const totalTripsToday = computed(() => elevators.value.reduce((sum, e) => sum + e.tripCount, 0))
const totalElevatorEnergy = computed(() => (totalTripsToday.value * 0.35).toFixed(1))

// 图表相关
const deviceBarChart = ref(null)
const envLineChart = ref(null)
const energyLineChart = ref(null)
let deviceBarIns = null, envLineIns = null, energyLineIns = null

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
  { device: 'Parking Gate', content: 'Communication lost', time: '08:20' }
])

let timeTimer = null, dataInterval = null

// ==================== 辅助函数 ====================
const loadingMessages = ['Preparing assets...', 'Loading background...', 'Initializing modules...', 'Establishing connection...', 'Starting dashboard...', 'Almost ready...']

const preloadBackground = () => new Promise((resolve) => {
  const img = new Image()
  img.src = 'https://aegisnx.com/wp-content/uploads/2026/05/1778231064187.png'
  let progress = 0, msgIdx = 0
  const msgInterval = setInterval(() => { if (msgIdx < loadingMessages.length - 1) loadingMessage.value = loadingMessages[++msgIdx] }, 800)
  const progInterval = setInterval(() => { if (progress < 90) loadingProgress.value = Math.min(progress += Math.random() * 10, 90) }, 100)
  img.onload = () => {
    clearInterval(msgInterval); clearInterval(progInterval)
    loadingMessage.value = 'Ready!'; loadingProgress.value = 100
    setTimeout(resolve, 500)
  }
  img.onerror = () => { clearInterval(msgInterval); clearInterval(progInterval); loadingProgress.value = 100; setTimeout(resolve, 300) }
})

const updateTime = () => {
  const now = new Date()
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

function randomVariation(base, range = 0.05) {
  const change = base * (Math.random() - 0.5) * range * 2
  return Math.max(0, base + change)
}

function updateCosts() {
  waterCost.value = (waterUsage.value * 0.5).toFixed(2)
  elecCost.value = (elecUsage.value * 0.13).toFixed(2)
  hvacCost.value = (hvacUsage.value * 0.15).toFixed(2)
  totalCost.value = (parseFloat(waterCost.value) + parseFloat(elecCost.value) + parseFloat(hvacCost.value)).toFixed(2)
}

function updateRestroomData() {
  restrooms.value.forEach(r => {
    let delta = (Math.random() > 0.65 ? (Math.random() > 0.5 ? 1 : -1) : 0)
    r.occupied = Math.min(r.total, Math.max(0, r.occupied + delta))
    const percent = (r.occupied / r.total) * 100
    if (percent > 70) { r.statusText = 'Limited'; r.statusClass = 'limited' }
    else if (percent > 40) { r.statusText = 'Moderate'; r.statusClass = 'moderate' }
    else { r.statusText = 'Available'; r.statusClass = 'available' }
  })
}

function updateElevatorData() {
  elevators.value.forEach(e => {
    if (e.statusText !== 'Maint' && Math.random() > 0.6) {
      const move = Math.random() > 0.5 ? 1 : -1
      let newFloor = e.currentFloor + move
      if (newFloor < 1) newFloor = 2
      if (newFloor > 12) newFloor = 11
      e.currentFloor = newFloor
      e.statusText = 'Moving'
      e.statusClass = 'moving'
      if (Math.random() > 0.85) {
        const floors = [1,2,3,4,5,6,7,8,9,10,11,12]
        e.callFloor = floors[Math.floor(Math.random() * floors.length)]
        e.callDirection = e.callFloor > e.currentFloor ? 'up' : (e.callFloor < e.currentFloor ? 'down' : null)
        e.eta = Math.floor(Math.random() * 25) + 5
        e.tripCount++
        e.passengers = Math.min(e.capacity, e.passengers + Math.floor(Math.random() * 4) - (Math.random() > 0.5 ? 2 : 0))
      }
      if (e.callFloor === e.currentFloor) {
        e.callFloor = null
        e.callDirection = null
        e.eta = 0
        if (Math.random() > 0.7) e.statusText = 'Idle'
        e.statusClass = e.statusText === 'Idle' ? 'idle' : 'moving'
      }
    }
    if (e.statusText === 'Maint' && Math.random() > 0.97) {
      e.statusText = 'Idle'
      e.statusClass = 'idle'
    }
    if (e.statusText === 'Idle' && Math.random() > 0.85) {
      e.statusText = 'Moving'
      e.statusClass = 'moving'
    }
  })
}

function updateAllCharts() {
  if (!deviceBarIns || !envLineIns || !energyLineIns) return
  deviceBarIns.setOption({
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(0,0,0,0.7)', borderColor: 'rgba(59,130,246,0.5)' },
    grid: { left: '8%', right: '4%', bottom: '15%', top: '10%', containLabel: true },
    xAxis: { type: 'category', data: deviceBarData.value.nameList, axisLine: { lineStyle: { color: 'rgba(255,255,255,0.2)' } }, axisLabel: { color: '#cbd5e1' } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } }, axisLabel: { color: '#94a3b8' } },
    series: [{ type: 'bar', data: deviceBarData.value.valueList.map((val, idx) => ({ value: val, itemStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1, [{ offset: 0, color: barColor[idx] },{ offset: 1, color: 'rgba(0,0,0,0.3)' }]) } })), barWidth: '40%', borderRadius: [6,6,0,6] }]
  })
  envLineIns.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, backgroundColor: 'rgba(0,0,0,0.7)', borderColor: '#3b82f6' },
    legend: { data: ['Temperature (℃)', 'Humidity (%)', 'CO₂ (ppm)'], textStyle: { color: '#94a3b8' }, top: 0, right: 0, itemWidth: 20, itemHeight: 10 },
    grid: { left: '8%', right: '8%', bottom: '5%', top: '15%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: envLineData.value.time, axisLine: { lineStyle: { color: '#334155' } }, axisLabel: { color: '#94a3b8', fontSize: 10 } },
    yAxis: [
      { type: 'value', name: 'CO₂ (ppm)', nameTextStyle: { color: '#64748b', fontSize: 10 }, axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: '#1e293b', type: 'dashed' } }, min: 400, max: 800 },
      { type: 'value', name: 'Temperature (℃) / Humidity (%)', nameTextStyle: { color: '#64748b', fontSize: 10 }, axisLabel: { color: '#94a3b8' }, splitLine: { show: false }, min: 0, max: 100 }
    ],
    series: [
      { name: 'CO₂ (ppm)', type: 'line', data: envLineData.value.co2, smooth: true, symbol: 'circle', symbolSize: 6, lineStyle: { width: 2, color: '#10b981', shadowBlur: 10, shadowColor: '#10b981' }, areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1, [{ offset: 0, color: 'rgba(16,185,129,0.4)' },{ offset: 1, color: 'rgba(16,185,129,0.02)' }]) }, yAxisIndex: 0, tooltip: { valueFormatter: (value) => value + ' ppm' } },
      { name: 'Temperature (℃)', type: 'line', data: envLineData.value.temp, smooth: true, symbol: 'diamond', symbolSize: 8, lineStyle: { width: 2.5, color: '#f59e0b', shadowBlur: 10, shadowColor: '#f59e0b' }, areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1, [{ offset: 0, color: 'rgba(245,158,11,0.35)' },{ offset: 1, color: 'rgba(245,158,11,0.02)' }]) }, yAxisIndex: 1, tooltip: { valueFormatter: (value) => value + ' ℃' } },
      { name: 'Humidity (%)', type: 'line', data: envLineData.value.humidity, smooth: true, symbol: 'roundRect', symbolSize: 6, lineStyle: { width: 2, color: '#3b82f6', type: 'dashed', shadowBlur: 10, shadowColor: '#3b82f6' }, areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1, [{ offset: 0, color: 'rgba(59,130,246,0.3)' },{ offset: 1, color: 'rgba(59,130,246,0.01)' }]) }, yAxisIndex: 1, tooltip: { valueFormatter: (value) => value + ' %' } }
    ]
  })
  energyLineIns.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: energyLineData.value.time },
    yAxis: { type: 'value', name: 'kW' },
    series: [{ name: 'Power(kWh)', type: 'line', data: energyLineData.value.power, smooth: true, color: '#8b5cf6', areaStyle: { color: 'rgba(139,92,246,0.2)' } }]
  })
}

function refreshData() {
  deviceTotal.value = Math.floor(randomVariation(186, 0.03))
  onlineRate.value = randomVariation(97.2, 0.02).toFixed(1)
  waterUsage.value = Math.floor(randomVariation(860, 0.07))
  waterPercent.value = parseFloat(((waterUsage.value / waterTarget) * 100).toFixed(1))
  elecUsage.value = Math.floor(randomVariation(4280, 0.07))
  elecPercent.value = parseFloat(((elecUsage.value / elecTarget) * 100).toFixed(1))
  hvacUsage.value = Math.floor(randomVariation(2150, 0.07))
  hvacPercent.value = parseFloat(((hvacUsage.value / hvacTarget) * 100).toFixed(1))
  updateCosts()
  floorPeople.value = Math.min(floorMax, Math.max(50, Math.floor(randomVariation(210, 0.1))))
  floorPercent.value = parseFloat(((floorPeople.value / floorMax) * 100).toFixed(1))
  updateRestroomData()
  updateElevatorData()

  envLineData.value.temp = envLineData.value.temp.map(v => Math.max(18, Math.min(32, randomVariation(v, 0.08))))
  envLineData.value.humidity = envLineData.value.humidity.map(v => Math.max(30, Math.min(70, randomVariation(v, 0.1))))
  envLineData.value.co2 = envLineData.value.co2.map(v => Math.max(400, Math.min(900, randomVariation(v, 0.07))))
  avgTemp.value = (envLineData.value.temp.reduce((a,b)=>a+b,0)/envLineData.value.temp.length).toFixed(1)
  energyLineData.value.power = energyLineData.value.power.map(v => Math.max(100, randomVariation(v, 0.12)))
  deviceBarData.value.valueList = deviceBarData.value.valueList.map(v => Math.floor(randomVariation(v, 0.06)))

  if (Math.random() > 0.65) {
    const devices = ['Floor 3 AC', 'Parking Light', 'Elevator 2', 'Fire Alarm']
    const contents = ['High temp', 'Power surge', 'Door abnormal', 'Sensor fault']
    alerts.value.unshift({ device: devices[Math.floor(Math.random()*4)], content: contents[Math.floor(Math.random()*4)], time: new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'}) })
    if (alerts.value.length > 6) alerts.value.pop()
  }
  updateAllCharts()
}

function initCharts() {
  if (!deviceBarChart.value || !envLineChart.value || !energyLineChart.value) return false
  try {
    if (deviceBarIns) deviceBarIns.dispose()
    if (envLineIns) envLineIns.dispose()
    if (energyLineIns) energyLineIns.dispose()
    deviceBarIns = echarts.init(deviceBarChart.value)
    envLineIns = echarts.init(envLineChart.value)
    energyLineIns = echarts.init(energyLineChart.value)
    updateAllCharts()
    return true
  } catch(e) { return false }
}

function resizeCharts() { deviceBarIns?.resize(); envLineIns?.resize(); energyLineIns?.resize() }

onMounted(async () => {
  updateTime()
  timeTimer = setInterval(updateTime, 1000)
  await preloadBackground()
  isBackgroundLoaded.value = true
  await nextTick()
  setTimeout(() => { initCharts(); refreshData(); dataInterval = setInterval(refreshData, 3000) }, 100)
  window.addEventListener('resize', resizeCharts)
})

onBeforeUnmount(() => {
  clearInterval(timeTimer); clearInterval(dataInterval); window.removeEventListener('resize', resizeCharts)
  deviceBarIns?.dispose(); envLineIns?.dispose(); energyLineIns?.dispose()
})
</script>

<style scoped>
/* Loading 样式 */
.loading-container { position: fixed; inset: 0; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); z-index: 9999; display: flex; justify-content: center; align-items: center; }
.loading-content { text-align: center; padding: 40px; border-radius: 32px; background: rgba(15,23,42,0.6); backdrop-filter: blur(20px); border: 1px solid rgba(59,130,246,0.3); animation: fadeInUp 0.6s; }
.loading-spinner { position: relative; width: 80px; height: 80px; margin: 0 auto 24px; }
.spinner-ring { position: absolute; width: 100%; height: 100%; border-radius: 50%; border: 3px solid transparent; animation: spin 1.5s infinite; }
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

/* 主页面 */
.dashboard { height: 100%; width: 100%; display: flex; flex-direction: column; background-image: url('https://aegisnx.com/wp-content/uploads/2026/05/1778231064187.png'); background-size: cover; background-position: center; background-attachment: fixed; animation: fadeIn 0.5s; }
.top-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 28px 8px; margin: 0 24px; }
.header-left { width: 140px; }
.header-title { text-align: center; flex: 1; }
.main-title { font-size: 44px; font-weight: 800; background: linear-gradient(135deg, #e0f2fe, #bae6fd); -webkit-background-clip: text; background-clip: text; color: transparent; letter-spacing: 3px; }
.datetime { font-size: 16px; color: #0ff; font-weight: 600; background: transparent; padding: 8px 20px; border-radius: 12px; backdrop-filter: blur(8px); min-width: 280px; text-align: center; font-family: monospace; border: 1px solid rgba(0,255,255,0.5); box-shadow: 0 0 10px rgba(0,255,255,0.3); }
.kpi-strip { display: flex; justify-content: space-around; gap: 20px; margin: 10px 24px 20px; padding: 12px 20px; }
.kpi-item { display: flex; gap: 12px; align-items: baseline; }
.kpi-label { color: #94a3b8; }
.kpi-value { font-size: 24px; font-weight: 800; color: #facc15; font-family: monospace; }
.content-area { flex: 1; display: flex; padding: 0 24px 24px; gap: 32px; overflow-y: auto; }
.left-panel { width: 320px; flex-shrink: 0; }
.right-panel { width: 380px; flex-shrink: 0; }
.center-void { flex: 1; }
.glass-card { background: transparent; border-radius: 28px; border: 1px solid rgba(59,130,246,0.3); box-shadow: 0 20px 35px -12px rgba(0,0,0,0.6); padding: 18px; transition: all 0.3s; margin-bottom: 20px; }
.glass-card:hover { background: rgba(8,16,28,0.6); backdrop-filter: blur(8px); transform: translateY(-4px); border-color: rgba(59,130,246,0.6); }
.card-title { font-size: 18px; font-weight: 700; color: #e2e8f0; margin-bottom: 10px; padding-left: 8px; border-left: 4px solid #3b82f6; }
.resource-grid { display: flex; justify-content: space-around; text-align: center; }
.resource-item .resource-label { margin-top: 8px; font-size: 13px; color: #fff; font-weight: bold }
.resource-value { font-size: 14px; font-weight: bold; color: #facc15; }
.resource-cost { font-size: 12px; color: #a5f3fc; margin-top: 4px; }
.parking-info { display: flex; justify-content: space-between; margin-bottom: 10px; color: #cbd5e1; font-size: 14px; }
.parking-info strong { color: #facc15; }

/* 厕所卡片样式 */
.restroom-table { width: 100%; }
.restroom-row-header { display: flex; justify-content: space-between; padding: 8px 4px; font-size: 11px; color: #fff; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid rgba(59,130,246,0.3); margin-bottom: 8px; font-weight: bold; }
.restroom-row-header span { flex: 1; }
.restroom-row-header span:first-child { text-align: left; }
.restroom-row-header span:nth-child(2) { text-align: center; }
.restroom-row-header span:last-child { text-align: right; }
.restroom-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 4px; border-bottom: 1px solid rgba(255,255,255,0.05); transition: all 0.2s; }
.restroom-row:hover { background: rgba(59,130,246,0.1); border-radius: 8px; transform: translateX(4px); }
.floor-name { flex: 1; font-size: 13px; font-weight: 500; color: #e2e8f0; }
.status-badge { flex: 1; text-align: center; font-size: 11px; font-weight: 600; padding: 4px 8px; border-radius: 20px; width: fit-content; margin: 0 auto; }
.status-badge.available { background: rgba(16,185,129,0.15); color: #10b981; }
.status-badge.moderate { background: rgba(245,158,11,0.15); color: #f59e0b; }
.status-badge.limited { background: rgba(239,68,68,0.15); color: #ef4444; }
.available-count { flex: 1; text-align: right; font-family: monospace; }
.count-number { font-size: 16px; font-weight: 700; color: #facc15; }
.count-total { font-size: 11px; color: #64748b; margin-left: 2px; }

/* 电梯卡片样式 */
.elevator-list { display: flex; flex-direction: column; }
.elevator-row { display: flex; align-items: center; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
.lift-name { width: 30px; font-weight: 600; color: #e2e8f0; }
.lift-floor { width: 45px; font-weight: 600; color: #facc15; font-family: monospace; }
.lift-status { width: 65px; font-size: 12px; }
.lift-status.moving { color: #60a5fa; }
.lift-status.idle { color: #94a3b8; }
.lift-status.maint { color: #ef4444; }
.lift-call { flex: 1; text-align: right; font-size: 11px; color: #f59e0b; font-family: monospace; }
.elevator-footer { display: flex; justify-content: space-between; margin-top: 12px; padding-top: 10px; border-top: 1px solid rgba(59,130,246,0.3); font-size: 11px; color: #64748b; }

/* 告警列表样式（未使用但保留） */
.alert-list-fixed { height: 180px; display: flex; flex-direction: column; }
.alert-items-fixed { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; scrollbar-width: none; }
.alert-items-fixed::-webkit-scrollbar { display: none; }
.alert-item { background: rgba(0,0,0,0.3); border-radius: 16px; padding: 10px 14px; display: flex; justify-content: space-between; align-items: center; transition: 0.2s; }
.alert-item:hover { background: rgba(239,68,68,0.2); border-left: 2px solid #ef4444; }
.alert-device { font-weight: 600; color: #facc15; font-size: 12px; }
.alert-content { flex: 1; margin: 0 10px; font-size: 12px; color: #e2e8f0; }
.alert-time { font-size: 11px; color: #94a3b8; font-family: monospace; }

.content-area::-webkit-scrollbar { width: 5px; }
.content-area::-webkit-scrollbar-track { background: rgba(15,23,42,0.5); border-radius: 4px; }
.content-area::-webkit-scrollbar-thumb { background: #3b82f6; border-radius: 4px; }
:deep(.el-progress-circle__track) { stroke: rgba(255,255,255,0.2); }
:deep(.el-progress__text) { color: #fff; font-weight: bold; }

/* ========== 移动端适配 (屏幕宽度 <= 768px) ========== */
@media (max-width: 768px) {
  .top-header {
    flex-direction: column;
    padding: 12px 16px 8px;
    margin: 0 12px;
    gap: 8px;
  }
  .header-left { display: none; }
  .main-title {
    font-size: 24px;
    letter-spacing: 1px;
  }
  .datetime {
    font-size: 10px;
    padding: 4px 12px;
    min-width: auto;
    width: auto;
    border-radius: 20px;
    box-shadow: 0 0 5px rgba(0,255,255,0.3);
  }
  .kpi-strip {
    flex-wrap: wrap;
    gap: 12px;
    margin: 8px 16px 16px;
    padding: 12px;
    justify-content: center;
  }
  .kpi-item {
    flex: 1 1 40%;
    justify-content: space-between;
    gap: 6px;
  }
  .kpi-value {
    font-size: 18px;
  }
  .content-area {
    flex-direction: column;
    padding: 0 16px 16px;
    gap: 0;
  }
  .left-panel,
  .right-panel {
    width: 100%;
    flex-shrink: 1;
  }
  .center-void {
    display: none;
  }
  .glass-card {
    border-radius: 20px;
    padding: 14px;
    margin-bottom: 16px;
  }
  .card-title {
    font-size: 16px;
    margin-bottom: 12px;
  }
  .resource-grid {
    gap: 12px;
    flex-wrap: wrap;
  }
  .resource-item {
    flex: 1 1 30%;
    min-width: 90px;
  }
  .resource-item .resource-label {
    font-size: 12px;
  }
  .resource-value {
    font-size: 12px;
  }
  .resource-cost {
    font-size: 10px;
  }
  /* 环形进度条尺寸缩小 */
  :deep(.el-progress-circle) {
    width: 70px !important;
    height: 70px !important;
  }
  :deep(.el-progress__text) {
    font-size: 12px !important;
  }
  /* 厕所卡片调整 */
  .restroom-row {
    padding: 8px 0;
  }
  .floor-name {
    font-size: 12px;
  }
  .status-badge {
    font-size: 10px;
    padding: 2px 6px;
  }
  .count-number {
    font-size: 14px;
  }
  .count-total {
    font-size: 10px;
  }
  /* 电梯卡片调整 */
  .lift-name {
    width: 25px;
    font-size: 13px;
  }
  .lift-floor {
    width: 35px;
    font-size: 14px;
  }
  .lift-status {
    width: 55px;
    font-size: 10px;
  }
  .lift-call {
    font-size: 10px;
  }
  .elevator-footer {
    font-size: 10px;
  }
  /* 图表容器高度缩小 */
  .device-list [ref="deviceBarChart"],
  .employee-dashboard [ref="envLineChart"],
  .energy-report [ref="energyLineChart"] {
    height: 160px !important;
  }
  /* 修正图表容器实际高度（因为是用ref动态渲染，需覆盖内联样式） */
  .device-list div[style*="height: 220px"],
  .employee-dashboard div[style*="height: 180px"],
  .energy-report div[style*="height: 180px"] {
    height: 160px !important;
  }
}
</style>