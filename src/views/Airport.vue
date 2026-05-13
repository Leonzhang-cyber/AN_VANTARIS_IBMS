<template>
  <div v-if="isBackgroundLoaded" class="dashboard">
    <div class="top-header">
      <div class="header-left"></div>
      <div class="header-title">
        <div class="main-title">SMART AIRPORT<br></div>
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
              <span>Location</span>
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

        <!-- Airport Energy 卡片 -->
        <div class="glass-card resources">
          <div class="card-title">⚡🛫🌡️ Airport Energy</div>
          <div class="resource-grid">
            <div class="resource-item">
              <el-progress type="circle" :percentage="elecPercent" :width="80" :stroke-width="8" color="#f59e0b" />
              <div class="resource-label">Electricity</div>
              <div class="resource-value">{{ elecUsage }} MWh</div>
              <div class="resource-cost">💰 ${{ elecCost }}</div>
            </div>
            <div class="resource-item">
              <el-progress type="circle" :percentage="fuelPercent" :width="80" :stroke-width="8" color="#ef4444" />
              <div class="resource-label">Jet Fuel</div>
              <div class="resource-value">{{ fuelUsage }} kL</div>
              <div class="resource-cost">💰 ${{ fuelCost }}</div>
            </div>
            <div class="resource-item">
              <el-progress type="circle" :percentage="waterPercent" :width="80" :stroke-width="8" color="#3b82f6" />
              <div class="resource-label">Water</div>
              <div class="resource-value">{{ waterUsage }} m³</div>
              <div class="resource-cost">💰 ${{ waterCost }}</div>
            </div>
          </div>
        </div>

        <!-- 候机区域拥挤度监测卡片 -->
        <div class="glass-card waiting-area-card">
          <div class="card-title">🪑 Gate Area Congestion</div>
          <div class="waiting-list">
            <div v-for="gate in gateCongestion" :key="gate.name" class="waiting-row">
              <span class="waiting-name">{{ gate.name }}</span>
              <div class="waiting-progress-wrapper">
                <div class="waiting-progress-bg">
                  <div class="waiting-progress-fill" :style="{ width: gate.congestion + '%', background: gate.color }"></div>
                </div>
              </div>
              <span class="waiting-count">🧑‍🤝‍🧑 {{ gate.passengers }}</span>
              <span class="waiting-status" :style="{ color: gate.color }">{{ gate.status }}</span>
            </div>
          </div>
        </div>

      </div>

      <div class="center-void"></div>

      <div class="right-panel">

        <!-- 航班信息卡片 -->
        <div class="glass-card elevator-card">
          <div class="card-title">✈️ Flight Status</div>
          <div class="elevator-list">
            <div v-for="f in flights" :key="f.id" class="elevator-row">
              <span class="lift-name">{{ f.flight }}</span>
              <span class="lift-floor">{{ f.destination }}</span>
              <span class="lift-status" :class="f.statusClass">{{ f.statusText }}</span>
              <span class="lift-call">{{ f.time }}</span>
            </div>
          </div>
          <div class="elevator-footer">
            <span>🚀 {{ todayFlights }} flights today</span>
            <span>⏱️ {{ avgDelay }} min delay</span>
          </div>
        </div>

        <!-- Airport Services 卡片（与 Airport Energy 样式一致） -->
        <div class="glass-card services">
          <div class="card-title">🛍️ Airport Services</div>
          <div class="resource-grid">
            <div class="resource-item">
              <el-progress type="circle" :percentage="retailPercent" :width="80" :stroke-width="8" color="#8b5cf6" />
              <div class="resource-label">Retail Occupancy</div>
              <div class="resource-value">{{ retailOccupancy }}%</div>
              <div class="resource-cost">🛒 {{ retailShops }} shops</div>
            </div>
            <div class="resource-item">
              <el-progress type="circle" :percentage="diningPercent" :width="80" :stroke-width="8" color="#ec489a" />
              <div class="resource-label">Dining Capacity</div>
              <div class="resource-value">{{ diningCapacity }}%</div>
              <div class="resource-cost">🍽️ {{ diningVenues }} venues</div>
            </div>
            <div class="resource-item">
              <el-progress type="circle" :percentage="loungePercent" :width="80" :stroke-width="8" color="#06b6d4" />
              <div class="resource-label">Lounge Usage</div>
              <div class="resource-value">{{ loungeUsage }}%</div>
              <div class="resource-cost">💺 VIP lounges</div>
            </div>
          </div>
        </div>

        <!-- 安检通道状态卡片 -->
        <div class="glass-card security-card">
          <div class="card-title">🛂 Security Checkpoint Status</div>
          <div class="security-list">
            <div v-for="lane in securityLanes" :key="lane.name" class="security-row">
              <div class="lane-name">{{ lane.name }}</div>
              <div class="lane-queue">
                <span class="queue-count">🧑‍🤝‍🧑 {{ lane.queueLength }}</span>
                <span class="queue-time">⏱️ {{ lane.waitTime }}min</span>
              </div>
              <div class="lane-status" :class="lane.statusClass">{{ lane.statusText }}</div>
            </div>
          </div>
          <div class="security-footer">
            <span>🚪 {{ totalOpenLanes }} lanes open</span>
            <span>📊 Avg wait: {{ avgWaitTime }} min</span>
          </div>
        </div>

      </div>
    </div>

    <!-- KPI 栏 -->
    <div class="glass-card kpi-strip">
      <div class="kpi-item">
        <span class="kpi-label">🛫 Terminals</span>
        <span class="kpi-value">{{ terminals }}</span>
      </div>
      <div class="kpi-item">
        <span class="kpi-label">🧑‍🤝‍🧑 Pax Today</span>
        <span class="kpi-value">{{ passengersToday }}</span>
      </div>
      <div class="kpi-item">
        <span class="kpi-label">✈️ Flights</span>
        <span class="kpi-value">{{ flightsCount }}</span>
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
        <div class="loading-tip">Initializing Smart Airport System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
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

// ==================== 响应式数据 ====================
const currentTime = ref('')
const isBackgroundLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing assets...')

// 机场 KPI 数据
const terminals = ref(4)
const passengersToday = ref(128500)
const flightsCount = ref(486)

// 能耗数据
const elecUsage = ref(18500)
const fuelUsage = ref(1250)
const waterUsage = ref(3850)

const elecTarget = 25000
const fuelTarget = 2000
const waterTarget = 6000

const elecPercent = ref(74.0)
const fuelPercent = ref(62.5)
const waterPercent = ref(64.2)

const elecCost = ref(0)
const fuelCost = ref(0)
const waterCost = ref(0)
const totalCost = ref(0)

// Airport Services 数据
const retailOccupancy = ref(78)
const retailPercent = ref(78)
const retailShops = ref(42)
const diningCapacity = ref(65)
const diningPercent = ref(65)
const diningVenues = ref(28)
const loungeUsage = ref(52)
const loungePercent = ref(52)

// ========== 厕所数据 ==========
const restrooms = ref([
  { floor: 'T1 Departure', total: 12, occupied: 5, statusText: 'Available', statusClass: 'available' },
  { floor: 'T1 Arrival', total: 10, occupied: 8, statusText: 'Limited', statusClass: 'limited' },
  { floor: 'T2 Arrival', total: 10, occupied: 3, statusText: 'Available', statusClass: 'available' },
  { floor: 'T3 International', total: 15, occupied: 11, statusText: 'Limited', statusClass: 'limited' }
])

// 计算扩展属性
const computedRestrooms = computed(() => {
  return restrooms.value.map(r => ({
    ...r,
    free: r.total - r.occupied,
    percent: (r.occupied / r.total) * 100
  }))
})

// ========== 航班数据 ==========
const flights = ref([
  { id: 1, flight: 'CA1835', destination: 'PEK', statusText: 'Boarding', statusClass: 'moving', time: '14:30' },
  // { id: 2, flight: 'MU5120', destination: 'PVG', statusText: 'Delayed', statusClass: 'warning', time: '15:00' },
  { id: 3, flight: 'CZ3102', destination: 'CAN', statusText: 'On Time', statusClass: 'idle', time: '15:15' },
  { id: 4, flight: 'HU7182', destination: 'HAK', statusText: 'Boarding', statusClass: 'moving', time: '14:45' },
  { id: 5, flight: '3U8882', destination: 'CTU', statusText: 'On Time', statusClass: 'idle', time: '15:30' },
  { id: 6, flight: 'MF8132', destination: 'XMN', statusText: 'Departed', statusClass: 'normal', time: '14:00' }
])

const todayFlights = ref(486)
const avgDelay = ref(12)

// ========== 候机区域拥挤度数据 ==========
const gateCongestion = ref([
  { name: 'Gate A1', passengers: 85, congestion: 75, status: 'Busy', color: '#f59e0b' },
  { name: 'Gate A2', passengers: 42, congestion: 38, status: 'Moderate', color: '#3b82f6' },
  { name: 'Gate B1', passengers: 156, congestion: 92, status: 'Critical', color: '#ef4444' },
  { name: 'Gate B2', passengers: 28, congestion: 25, status: 'Quiet', color: '#10b981' },
  { name: 'Gate C1', passengers: 98, congestion: 82, status: 'Very Busy', color: '#f97316' },
  { name: 'Gate C2', passengers: 35, congestion: 31, status: 'Moderate', color: '#3b82f6' }
])

// ========== 安检通道数据 ==========
const securityLanes = ref([
  { name: 'Lane 1', queueLength: 23, waitTime: 12, statusText: 'Busy', statusClass: 'security-busy' },
  { name: 'Lane 2', queueLength: 8, waitTime: 4, statusText: 'Fast', statusClass: 'security-fast' },
  { name: 'Lane 3', queueLength: 31, waitTime: 16, statusText: 'Critical', statusClass: 'security-critical' },
  { name: 'Lane 4', queueLength: 5, waitTime: 3, statusText: 'Fast', statusClass: 'security-fast' },
  // { name: 'Lane 5 (Priority)', queueLength: 12, waitTime: 6, statusText: 'Moderate', statusClass: 'security-moderate' },
  // { name: 'Lane 6', queueLength: 19, waitTime: 10, statusText: 'Busy', statusClass: 'security-busy' }
])

const totalOpenLanes = computed(() => securityLanes.value.length)
const avgWaitTime = computed(() => {
  const total = securityLanes.value.reduce((sum, lane) => sum + lane.waitTime, 0)
  return Math.floor(total / securityLanes.value.length)
})

let timeTimer = null, dataInterval = null

// ==================== 辅助函数 ====================
const loadingMessages = ['Preparing assets...', 'Loading background...', 'Initializing modules...', 'Establishing connection...', 'Starting dashboard...', 'Almost ready...']

const preloadBackground = () => new Promise((resolve) => {
  const img = new Image()
  img.src = 'https://aegisnx.com/wp-content/uploads/2026/05/1778306317503.png'
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

// const updateTime = () => {
//   const now = new Date()
//   currentTime.value = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}.${String(now.getMilliseconds()).padStart(3, '0')} UTC+8`
// }

const updateTime = () => {
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

function randomVariation(base, range = 0.05) {
  const change = base * (Math.random() - 0.5) * range * 2
  return Math.max(0, base + change)
}

function updateCosts() {
  elecCost.value = (elecUsage.value * 0.12).toFixed(2)
  fuelCost.value = (fuelUsage.value * 0.85).toFixed(2)
  waterCost.value = (waterUsage.value * 0.45).toFixed(2)
  totalCost.value = (parseFloat(elecCost.value) + parseFloat(fuelCost.value) + parseFloat(waterCost.value)).toFixed(2)
}

// 更新服务数据
function updateServicesData() {
  retailOccupancy.value = Math.floor(randomVariation(78, 0.1))
  retailPercent.value = Math.min(100, Math.max(0, retailOccupancy.value))
  retailShops.value = Math.floor(randomVariation(42, 0.05))

  diningCapacity.value = Math.floor(randomVariation(65, 0.12))
  diningPercent.value = Math.min(100, Math.max(0, diningCapacity.value))
  diningVenues.value = Math.floor(randomVariation(28, 0.05))

  loungeUsage.value = Math.floor(randomVariation(52, 0.08))
  loungePercent.value = Math.min(100, Math.max(0, loungeUsage.value))
}

// 更新厕所数据
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

// 更新航班数据
function updateFlightData() {
  const statuses = [
    { text: 'Boarding', class: 'moving' },
    { text: 'On Time', class: 'idle' },
    { text: 'Delayed', class: 'warning' },
    { text: 'Departed', class: 'normal' }
  ]
  flights.value.forEach(f => {
    if (Math.random() > 0.7) {
      const newStatus = statuses[Math.floor(Math.random() * statuses.length)]
      f.statusText = newStatus.text
      f.statusClass = newStatus.class
    }
  })
  todayFlights.value = Math.floor(randomVariation(486, 0.03))
  avgDelay.value = Math.floor(randomVariation(12, 0.15))
}

// 更新候机区域数据
function updateGateCongestion() {
  gateCongestion.value.forEach(gate => {
    let variation = (Math.random() - 0.5) * 0.15
    let newPassengers = Math.floor(gate.passengers * (1 + variation))
    newPassengers = Math.max(5, Math.min(200, newPassengers))
    gate.passengers = newPassengers
    gate.congestion = Math.floor((newPassengers / 180) * 100)

    if (gate.congestion >= 80) {
      gate.status = 'Critical'
      gate.color = '#ef4444'
    } else if (gate.congestion >= 60) {
      gate.status = 'Very Busy'
      gate.color = '#f97316'
    } else if (gate.congestion >= 40) {
      gate.status = 'Busy'
      gate.color = '#f59e0b'
    } else if (gate.congestion >= 20) {
      gate.status = 'Moderate'
      gate.color = '#3b82f6'
    } else {
      gate.status = 'Quiet'
      gate.color = '#10b981'
    }
  })
}

// 更新安检数据
function updateSecurityLanes() {
  securityLanes.value.forEach(lane => {
    let variation = (Math.random() - 0.5) * 0.2
    let newQueue = Math.floor(lane.queueLength * (1 + variation))
    newQueue = Math.max(2, Math.min(50, newQueue))
    lane.queueLength = newQueue
    lane.waitTime = Math.floor(newQueue / 2) + Math.floor(Math.random() * 3)

    if (lane.queueLength >= 30) {
      lane.statusText = 'Critical'
      lane.statusClass = 'security-critical'
    } else if (lane.queueLength >= 20) {
      lane.statusText = 'Busy'
      lane.statusClass = 'security-busy'
    } else if (lane.queueLength >= 10) {
      lane.statusText = 'Moderate'
      lane.statusClass = 'security-moderate'
    } else {
      lane.statusText = 'Fast'
      lane.statusClass = 'security-fast'
    }
  })
}

function refreshData() {
  passengersToday.value = Math.floor(randomVariation(128500, 0.05))
  flightsCount.value = Math.floor(randomVariation(486, 0.03))

  elecUsage.value = Math.floor(randomVariation(18500, 0.06))
  elecPercent.value = parseFloat(((elecUsage.value / elecTarget) * 100).toFixed(1))
  fuelUsage.value = Math.floor(randomVariation(1250, 0.07))
  fuelPercent.value = parseFloat(((fuelUsage.value / fuelTarget) * 100).toFixed(1))
  waterUsage.value = Math.floor(randomVariation(3850, 0.05))
  waterPercent.value = parseFloat(((waterUsage.value / waterTarget) * 100).toFixed(1))
  updateCosts()

  updateServicesData()
  updateRestroomData()
  updateFlightData()
  updateGateCongestion()
  updateSecurityLanes()
}

onMounted(async () => {
  updateTime()
  timeTimer = setInterval(updateTime, 1000)
  await preloadBackground()
  isBackgroundLoaded.value = true
  await nextTick()
  setTimeout(() => { refreshData(); dataInterval = setInterval(refreshData, 5000) }, 100)
})

onBeforeUnmount(() => {
  clearInterval(timeTimer); clearInterval(dataInterval)
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
.dashboard { height: 100%; width: 100%; display: flex; flex-direction: column; background-image: url('https://aegisnx.com/wp-content/uploads/2026/05/1778306317503.png'); background-size: cover; background-position: center; background-attachment: fixed; animation: fadeIn 0.5s; }
.top-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 28px 8px; margin: 0 24px; }
.header-left { width: 140px; }
.header-title { text-align: center; flex: 1; }
.main-title { font-size: 44px; font-weight: 800; background: linear-gradient(135deg, #e0f2fe, #bae6fd); -webkit-background-clip: text; background-clip: text; color: transparent; text-shadow: 0 0 30px rgba(96,165,250,0.5); letter-spacing: 3px; }
.datetime { font-size: 15px; color: #a5f3fc; font-weight: 600; background: transparent; backdrop-filter: blur(8px); padding: 8px 20px; border-radius: 12px; min-width: 280px; text-align: center; font-family: monospace; border: 1px solid rgba(165,243,252,0.3); text-shadow: 0 0 5px #a5f3fc; }
.kpi-strip { display: flex; justify-content: space-around; gap: 20px; margin: 10px 24px 20px; padding: 12px 20px; background: transparent;  border-radius: 24px; border: 1px solid rgba(59,130,246,0.3); }
.kpi-item { display: flex; gap: 12px; align-items: baseline; }
.kpi-label { color: #94a3b8; font-weight: 500; letter-spacing: 0.5px; }
.kpi-value { font-size: 24px; font-weight: 800; color: #facc15; font-family: monospace; text-shadow: 0 0 8px rgba(250,204,21,0.4); }
.content-area { flex: 1; display: flex; padding: 0 24px 24px; gap: 32px; overflow-y: auto; }
.left-panel { width: 320px; flex-shrink: 0; }
.right-panel { width: 420px; flex-shrink: 0; }
.center-void { flex: 1; }

/* 透明玻璃卡片 */
.glass-card {
  background: transparent !important;
  border-radius: 24px;
  border: 1px solid rgba(59, 130, 246, 0.4);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.25);
  padding: 18px;
  transition: all 0.3s ease;
  margin-bottom: 20px;
}
.glass-card:hover {
  backdrop-filter: blur(16px);
  border-color: rgba(59, 130, 246, 0.7);
  transform: translateY(-3px);
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.35);
}

/* 卡片标题 */
.card-title {
  font-size: 18px;
  font-weight: 800;
  color: #f0f9ff;
  margin-bottom: 14px;
  padding-left: 10px;
  border-left: 4px solid #3b82f6;
  text-shadow: 0 0 4px rgba(59,130,246,0.5);
  letter-spacing: 0.5px;
}

/* 资源卡片内的文字 */
.resource-grid { display: flex; justify-content: space-around; text-align: center; }
.resource-item .resource-label { margin-top: 8px; font-size: 13px; font-weight: 600; color: #cbd5e1; letter-spacing: 0.5px; }
.resource-value { font-size: 15px; font-weight: 800; color: #facc15; text-shadow: 0 0 4px rgba(250,204,21,0.3); }
.resource-cost { font-size: 12px; font-weight: 600; color: #a5f3fc; margin-top: 4px; }

/* 候机区域样式 - 单行显示 */
.waiting-list { display: flex; flex-direction: column; gap: 10px; }
.waiting-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 6px 0; }
.waiting-name { width: 60px; font-size: 13px; font-weight: 700; color: #cbd5e1; letter-spacing: 0.3px; }
.waiting-progress-wrapper { flex: 1; }
.waiting-progress-bg { height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden; }
.waiting-progress-fill { height: 100%; border-radius: 3px; transition: width 0.3s; }
.waiting-count { width: 70px; font-size: 12px; font-weight: 600; color: #a5f3fc; text-align: right; }
.waiting-status { width: 75px; font-size: 11px; font-weight: 700; text-align: right; }

/* 安检通道样式 */
.security-list { display: flex; flex-direction: column; }
.security-row { display: flex; align-items: center; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.06); }
.lane-name { width: 100px; font-weight: 700; color: #e2e8f0; font-size: 13px; }
.lane-queue { width: 100px; display: flex; gap: 12px; }
.queue-count, .queue-time { font-size: 12px; font-weight: 600; color: #a5f3fc; width: 20px; text-align: center }
.lane-status { width: 70px; text-align: center; font-size: 12px; font-weight: 800; padding: 4px 10px; border-radius: 20px; }
.security-fast { background: rgba(16,185,129,0.2); color: #34d399; }
.security-moderate { background: rgba(59,130,246,0.2); color: #60a5fa; }
.security-busy { background: rgba(245,158,11,0.2); color: #fbbf24; }
.security-critical { background: rgba(239,68,68,0.2); color: #f87171; }
.security-footer { display: flex; justify-content: space-between; margin-top: 12px; padding-top: 10px; border-top: 1px solid rgba(59,130,246,0.35); font-size: 11px; font-weight: 700; color: #94a3b8; letter-spacing: 0.5px; }

/* 滚动条 */
.content-area::-webkit-scrollbar { width: 5px; }
.content-area::-webkit-scrollbar-track { background: rgba(15,23,42,0.5); border-radius: 4px; }
.content-area::-webkit-scrollbar-thumb { background: #3b82f6; border-radius: 4px; }

/* Element Plus 进度条文字 */
:deep(.el-progress-circle__track) { stroke: rgba(255,255,255,0.2); }
:deep(.el-progress__text) { color: #fff !important; font-weight: 700 !important; font-size: 14px !important; text-shadow: 0 0 4px rgba(0,0,0,0.5); }

/* 厕所卡片样式 */
.restroom-table { width: 100%; }
.restroom-row-header { display: flex; justify-content: space-between; padding: 8px 4px; font-size: 11px; font-weight: 700; color: #60a5fa; text-transform: uppercase; letter-spacing: 0.8px; border-bottom: 1px solid rgba(59,130,246,0.4); margin-bottom: 8px; }
.restroom-row-header span { flex: 1; }
.restroom-row-header span:first-child { text-align: left; }
.restroom-row-header span:nth-child(2) { text-align: center; }
.restroom-row-header span:last-child { text-align: right; }
.restroom-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 4px; border-bottom: 1px solid rgba(255,255,255,0.06); transition: all 0.2s; }
.restroom-row:hover { background: rgba(59,130,246,0.12); border-radius: 8px; transform: translateX(4px); }
.floor-name { flex: 1; font-size: 13px; font-weight: 700; color: #e2e8f0; letter-spacing: 0.3px; }
.status-badge { flex: 1; text-align: center; font-size: 11px; font-weight: 800; padding: 5px 10px; border-radius: 24px; width: fit-content; margin: 0 auto; letter-spacing: 0.5px; }
.status-badge.available { background: rgba(16,185,129,0.2); color: #34d399; text-shadow: 0 0 2px rgba(16,185,129,0.3); }
.status-badge.moderate { background: rgba(245,158,11,0.2); color: #fbbf24; text-shadow: 0 0 2px rgba(245,158,11,0.3); }
.status-badge.limited { background: rgba(239,68,68,0.2); color: #f87171; text-shadow: 0 0 2px rgba(239,68,68,0.3); }
.available-count { flex: 1; text-align: right; font-family: monospace; }
.count-number { font-size: 16px; font-weight: 800; color: #facc15; text-shadow: 0 0 4px rgba(250,204,21,0.4); }
.count-total { font-size: 11px; font-weight: 600; color: #94a3b8; margin-left: 2px; }

/* 航班卡片样式 */
.elevator-list { display: flex; flex-direction: column; }
.elevator-row { display: flex; align-items: center; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.06); }
.lift-name { width: 70px; font-weight: 800; color: #e2e8f0; letter-spacing: 0.5px; }
.lift-floor { width: 65px; font-weight: 700; color: #a5f3fc; letter-spacing: 0.3px; }
.lift-status { width: 80px; font-size: 12px; font-weight: 800; }
.lift-status.moving { color: #60a5fa; text-shadow: 0 0 3px rgba(96,165,250,0.5); }
.lift-status.idle { color: #94a3b8; }
.lift-status.warning { color: #f87171; text-shadow: 0 0 3px rgba(248,113,113,0.5); }
.lift-status.normal { color: #34d399; text-shadow: 0 0 3px rgba(52,211,153,0.5); }
.lift-call { flex: 1; text-align: right; font-size: 12px; font-weight: 700; color: #facc15; font-family: monospace; text-shadow: 0 0 4px rgba(250,204,21,0.4); }
.elevator-footer { display: flex; justify-content: space-between; margin-top: 12px; padding-top: 10px; border-top: 1px solid rgba(59,130,246,0.35); font-size: 11px; font-weight: 700; color: #94a3b8; letter-spacing: 0.5px; }

/* 图表文字颜色 */
:deep(.xaxis-label), :deep(.yaxis-label) { fill: #94a3b8 !important; font-weight: 500 !important; }
:deep(.legend-text) { color: #cbd5e1 !important; font-weight: 600 !important; }

/* ========== 移动端适配 (屏幕宽度 <= 768px) ========== */
@media (max-width: 768px) {
  /* 顶部区域 */
  .top-header {
    flex-direction: column;
    padding: 12px 16px 8px;
    margin: 0 12px;
    gap: 10px;
  }
  .header-left {
    display: none;
  }
  .main-title {
    font-size: 28px;
    letter-spacing: 1px;
    text-shadow: 0 0 15px rgba(96,165,250,0.4);
  }
  .datetime {
    font-size: 11px;
    padding: 4px 12px;
    min-width: auto;
    width: auto;
    border-radius: 20px;
    backdrop-filter: blur(4px);
  }

  /* KPI 条 */
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
    gap: 8px;
  }
  .kpi-label {
    font-size: 12px;
  }
  .kpi-value {
    font-size: 18px;
  }

  /* 主内容区改为垂直排列 */
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

  /* 卡片通用调整 */
  .glass-card {
    border-radius: 20px;
    padding: 14px;
    margin-bottom: 16px;
  }
  .glass-card:hover {
    transform: none; /* 移动端禁用上浮效果 */
    backdrop-filter: blur(8px);
  }
  .card-title {
    font-size: 16px;
    margin-bottom: 12px;
    padding-left: 8px;
  }

  /* 资源卡片环形进度条缩小 */
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
    margin-top: 6px;
  }
  .resource-value {
    font-size: 13px;
  }
  .resource-cost {
    font-size: 10px;
  }
  :deep(.el-progress-circle) {
    width: 70px !important;
    height: 70px !important;
  }
  :deep(.el-progress__text) {
    font-size: 12px !important;
  }

  /* 厕所卡片 */
  .restroom-row {
    padding: 8px 0;
  }
  .floor-name {
    font-size: 12px;
  }
  .status-badge {
    font-size: 10px;
    padding: 3px 6px;
  }
  .count-number {
    font-size: 14px;
  }
  .count-total {
    font-size: 10px;
  }

  /* 候机区域卡片 */
  .waiting-row {
    gap: 8px;
    padding: 5px 0;
  }
  .waiting-name {
    width: 50px;
    font-size: 11px;
  }
  .waiting-progress-wrapper {
    min-width: 80px;
  }
  .waiting-count {
    width: 55px;
    font-size: 10px;
  }
  .waiting-status {
    width: 65px;
    font-size: 10px;
  }

  /* 安检通道卡片 */
  .security-row {
    padding: 8px 0;
  }
  .lane-name {
    width: 70px;
    font-size: 12px;
  }
  .lane-queue {
    width: 70px;
    gap: 6px;
  }
  .queue-count, .queue-time {
    font-size: 11px;
    width: auto;
  }
  .lane-status {
    width: 60px;
    font-size: 10px;
    padding: 3px 6px;
  }
  .security-footer {
    font-size: 10px;
    margin-top: 8px;
    padding-top: 8px;
  }

  /* 航班卡片 */
  .elevator-row {
    padding: 8px 0;
  }
  .lift-name {
    width: 55px;
    font-size: 13px;
  }
  .lift-floor {
    width: 50px;
    font-size: 11px;
  }
  .lift-status {
    width: 70px;
    font-size: 11px;
  }
  .lift-call {
    font-size: 11px;
  }
  .elevator-footer {
    font-size: 10px;
  }

  /* 滚动条保持细条，但可忽略 */
  .content-area::-webkit-scrollbar {
    width: 3px;
  }
}
</style>