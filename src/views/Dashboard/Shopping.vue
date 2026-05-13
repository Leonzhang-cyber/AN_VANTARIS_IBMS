<template>
  <div v-if="isBackgroundLoaded" class="dashboard">
    <div class="top-header">
      <div class="header-left"></div>
      <div class="header-title">
        <div class="main-title">SHOPPING MALL<br></div>
      </div>
      <div class="datetime" v-if="isFullscreen">{{ currentTime }}</div>
    </div>

    <div class="content-area">
      <div class="left-panel">

        <!-- 卫生间使用情况 -->
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

        <!-- 商场能耗 -->
        <div class="glass-card resources">
          <div class="card-title">💧⚡❄️ Mall Energy</div>
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
          <div class="resource-grid second-row">
            <div class="resource-item">
              <el-progress type="circle" :percentage="lightingPercent" :width="80" :stroke-width="8" color="#a855f7" />
              <div class="resource-label">Lighting</div>
              <div class="resource-value">{{ lightingUsage }} kWh</div>
              <div class="resource-cost">💰 ${{ lightingCost }}</div>
            </div>
            <div class="resource-item">
              <el-progress type="circle" :percentage="escalatorPercent" :width="80" :stroke-width="8" color="#ec489a" />
              <div class="resource-label">Escalator</div>
              <div class="resource-value">{{ escalatorUsage }} kWh</div>
              <div class="resource-cost">💰 ${{ escalatorCost }}</div>
            </div>
            <div class="resource-item">
              <el-progress type="circle" :percentage="waterHeatingPercent" :width="80" :stroke-width="8" color="#06b6d4" />
              <div class="resource-label">Water Heating</div>
              <div class="resource-value">{{ waterHeatingUsage }} kWh</div>
              <div class="resource-cost">💰 ${{ waterHeatingCost }}</div>
            </div>
          </div>
        </div>

        <!-- 客流统计 + 车流量 -->
        <div class="glass-card parking">
          <div class="card-title">🧑‍🤝‍🧑 Passenger & Traffic Flow</div>

          <!-- 行人客流 -->
          <div class="flow-section">
            <div class="section-subtitle">🚶 Pedestrian Flow</div>
            <div class="parking-stats">
              <div class="parking-info">
                <span>Current: <strong>{{ floorPeople }}</strong> / {{ floorMax }}</span>
                <span>Capacity: <strong>{{ floorPercent }}%</strong></span>
              </div>
              <el-progress :percentage="floorPercent" :stroke-width="12" color="#8b5cf6" />
            </div>
          </div>

          <!-- 车流量（停车场） -->
          <div class="flow-section">
            <div class="section-subtitle">🚗 Parking Traffic</div>
            <div class="parking-stats">
              <div class="parking-info">
                <span>Vehicles: <strong>{{ parkingCars }}</strong> / {{ parkingCapacity }}</span>
                <span>Occupancy: <strong>{{ parkingPercent }}%</strong></span>
              </div>
              <el-progress :percentage="parkingPercent" :stroke-width="12" color="#f59e0b" />
            </div>
            <div class="traffic-details">
              <div class="traffic-item">
                <span>🚙 Entered today:</span>
                <strong>{{ carsEntered }}</strong>
              </div>
              <div class="traffic-item">
                <span>🚗 Exited today:</span>
                <strong>{{ carsExited }}</strong>
              </div>
              <div class="traffic-item">
                <span>⏱️ Avg stay:</span>
                <strong>{{ avgStayTime }}</strong>
              </div>
            </div>
          </div>
        </div>

      </div>

      <div class="center-void"></div>

      <div class="right-panel">

        <!-- 门店销售 Top 5 横向柱状图 -->
        <div class="glass-card sales-card">
          <div class="card-title">🏆 Top 5 Store Sales</div>
          <div class="sales-bar-list">
            <div v-for="(store, index) in topStores" :key="store.name" class="sales-bar-item">
              <div class="sales-rank" :class="'rank-' + (index + 1)">
                {{ index + 1 }}
              </div>
              <div class="sales-info">
                <div class="sales-name-line">
                  <span class="sales-name" :style="{ color: store.nameColor }">{{ store.name }}</span>
                  <span class="sales-category">{{ store.category }}</span>
                </div>
                <div class="sales-bar-wrapper">
                  <div class="sales-bar-bg">
                    <div
                        class="sales-bar-fill"
                        :style="{ width: store.percent + '%', background: store.barColor }"
                    ></div>
                  </div>
                  <div class="sales-value-group">
                    <span class="sales-value">¥{{ store.sales }}k</span>
                    <span class="sales-trend" :class="store.trendClass">
                      {{ store.trend }} {{ store.trend === '↑' ? '▲' : '▼' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="sales-footer">
            <span>📊 Total: ¥{{ totalSales }}k</span>
            <span>🏪 {{ activeStores }} stores active</span>
          </div>
        </div>

        <!-- 区域人流数据 -->
        <div class="glass-card people-flow-card">
          <div class="card-title">👥 Zone People Flow</div>
          <div class="people-flow-list">
            <div v-for="flow in zonePeopleFlow" :key="flow.zone" class="flow-row">
              <span class="flow-zone">{{ flow.zone }}</span>
              <div class="flow-progress-wrapper">
                <div class="flow-progress-bg">
                  <div class="flow-progress-fill" :style="{ width: flow.percentage + '%', background: flow.color }"></div>
                </div>
              </div>
              <span class="flow-count">👥 {{ flow.currentPeople }}</span>
              <span class="flow-status" :style="{ color: flow.color }">{{ flow.status }}</span>
            </div>
          </div>
          <div class="people-flow-footer">
            <span>📊 Total: {{ totalPeopleFlow }} visitors</span>
            <span>🔄 Peak: {{ peakHourFlow }}</span>
          </div>
        </div>

        <!-- 区域店铺营业数据 -->
        <div class="glass-card store-data-card">
          <div class="card-title">🏪 Store Operation Status</div>
          <div class="store-compact-grid">
            <div v-for="zone in storeZones" :key="zone.name" class="store-compact-item">
              <div class="store-compact-header">
                <span class="store-compact-name">{{ zone.name }}</span>
                <div class="store-compact-numbers">
                  <span class="store-open-badge">{{ zone.openStores }}/{{ zone.totalStores }}</span>
                  <span class="store-rate-value" :style="{ color: zone.progressColor }">{{ zone.openRate }}%</span>
                </div>
              </div>
              <div class="store-compact-bar">
                <div class="store-bar-fill" :style="{ width: zone.openRate + '%', background: zone.progressColor }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- KPI 栏 -->
    <div class="glass-card kpi-strip">
      <div class="kpi-item">
        <span class="kpi-label">🏬 Total Stores</span>
        <span class="kpi-value">{{ deviceTotal }}</span>
      </div>
      <div class="kpi-item">
        <span class="kpi-label">📶 Device Online</span>
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
        <div class="loading-tip">Initializing Shopping Mall System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
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
const deviceTotal = ref(128)
const onlineRate = ref(98.5)
const avgTemp = ref(24.8)
const waterUsage = ref(3860)
const elecUsage = ref(18600)
const hvacUsage = ref(9400)
const lightingUsage = ref(5200)
const escalatorUsage = ref(3800)
const waterHeatingUsage = ref(2100)

const waterTarget = 6000
const elecTarget = 28000
const hvacTarget = 15000
const lightingTarget = 8000
const escalatorTarget = 6000
const waterHeatingTarget = 3500

const waterPercent = ref(64.3)
const elecPercent = ref(66.4)
const hvacPercent = ref(62.7)
const lightingPercent = ref(65.0)
const escalatorPercent = ref(63.3)
const waterHeatingPercent = ref(60.0)

const waterCost = ref(0)
const elecCost = ref(0)
const hvacCost = ref(0)
const lightingCost = ref(0)
const escalatorCost = ref(0)
const waterHeatingCost = ref(0)
const totalCost = ref(0)

// 商场客流
const floorMax = 2800
const floorPeople = ref(1680)
const floorPercent = ref(60)

// 停车场车流量数据
const parkingCapacity = 1200
const parkingCars = ref(680)
const parkingPercent = ref(56.7)
const carsEntered = ref(2840)
const carsExited = ref(2560)
const avgStayTime = ref('1h 24m')

// 门店销售 Top 5 数据 - 每个门店独立颜色
const allStores = ref([
  { name: 'Apple Store', category: 'Electronics', sales: 456, trend: '↑', trendValue: 0.08, nameColor: '#60a5fa', barColor: '#3b82f6' },
  { name: 'ZARA', category: 'Fashion', sales: 389, trend: '↑', trendValue: 0.05, nameColor: '#f472b6', barColor: '#ec489a' },
  { name: 'Starbucks', category: 'F&B', sales: 342, trend: '↓', trendValue: -0.02, nameColor: '#6ee7b7', barColor: '#10b981' },
  { name: 'UNIQLO', category: 'Fashion', sales: 298, trend: '↑', trendValue: 0.12, nameColor: '#fbbf24', barColor: '#f59e0b' },
  { name: 'H&M', category: 'Fashion', sales: 267, trend: '↓', trendValue: -0.03, nameColor: '#c084fc', barColor: '#a855f7' },
  { name: 'Nike', category: 'Sportswear', sales: 245, trend: '↑', trendValue: 0.06, nameColor: '#fb923c', barColor: '#f97316' },
  { name: 'Samsung', category: 'Electronics', sales: 223, trend: '↑', trendValue: 0.04, nameColor: '#2dd4bf', barColor: '#14b8a6' },
  { name: 'MUJI', category: 'Lifestyle', sales: 198, trend: '↓', trendValue: -0.01, nameColor: '#a5f3fc', barColor: '#06b6d4' },
  { name: 'Adidas', category: 'Sportswear', sales: 185, trend: '↑', trendValue: 0.07, nameColor: '#fda4af', barColor: '#f43f5e' },
  { name: 'Decathlon', category: 'Sportswear', sales: 167, trend: '↓', trendValue: -0.02, nameColor: '#d8b4fe', barColor: '#8b5cf6' }
])

const topStores = ref([])
const totalSales = ref(0)
const activeStores = ref(128)

// 计算 Top 5
function updateTopStores() {
  // 按销售额排序并取前5
  const sorted = [...allStores.value].sort((a, b) => b.sales - a.sales)
  const top5 = sorted.slice(0, 5)
  const maxSales = top5[0].sales

  top5.forEach(store => {
    store.percent = (store.sales / maxSales) * 100
    // 根据趋势设置趋势样式
    if (store.trend === '↑') {
      store.trendClass = 'trend-up'
    } else {
      store.trendClass = 'trend-down'
    }
  })

  topStores.value = top5
  totalSales.value = sorted.reduce((sum, s) => sum + s.sales, 0)
}

// 随机更新门店销售数据
function updateStoreSales() {
  allStores.value.forEach(store => {
    // 随机波动 -8% 到 +12%
    let variation = (Math.random() - 0.4) * 0.2
    let newSales = store.sales * (1 + variation)
    newSales = Math.max(120, Math.min(680, newSales))
    store.sales = Math.floor(newSales)

    // 更新趋势
    if (variation > 0.02) {
      store.trend = '↑'
      store.trendValue = variation
    } else if (variation < -0.02) {
      store.trend = '↓'
      store.trendValue = variation
    }
  })

  // 随机打乱排名，让 Top 5 动态变化
  if (Math.random() > 0.7) {
    const idx1 = Math.floor(Math.random() * allStores.value.length)
    const idx2 = Math.floor(Math.random() * allStores.value.length)
    if (idx1 !== idx2) {
      const temp = { ...allStores.value[idx1] }
      allStores.value[idx1] = { ...allStores.value[idx2] }
      allStores.value[idx2] = temp
    }
  }

  updateTopStores()
}

// 区域店铺营业数据
const storeZones = ref([
  { name: 'B1 Food Hall', totalStores: 24, openStores: 22, openRate: 92, avgRating: 4.6, progressColor: '#10b981' },
  { name: '1F Luxury', totalStores: 18, openStores: 16, openRate: 89, avgRating: 4.8, progressColor: '#8b5cf6' },
  { name: '2F Fashion', totalStores: 32, openStores: 29, openRate: 91, avgRating: 4.5, progressColor: '#f59e0b' },
  { name: '3F Entertainment', totalStores: 15, openStores: 12, openRate: 80, avgRating: 4.3, progressColor: '#3b82f6' },
  { name: '4F Cinema', totalStores: 8, openStores: 8, openRate: 100, avgRating: 4.7, progressColor: '#ec489a' }
])

// 区域人流数据
const zonePeopleFlow = ref([
  { zone: 'B1 Food Hall', currentPeople: 345, capacity: 600, percentage: 58, status: 'Moderate', color: '#3b82f6' },
  { zone: '1F Luxury', currentPeople: 180, capacity: 400, percentage: 45, status: 'Moderate', color: '#3b82f6' },
  { zone: '2F Fashion', currentPeople: 520, capacity: 700, percentage: 74, status: 'Busy', color: '#f59e0b' },
  { zone: '3F Entertainment', currentPeople: 290, capacity: 450, percentage: 64, status: 'Busy', color: '#f59e0b' },
  { zone: '4F Cinema', currentPeople: 380, capacity: 500, percentage: 76, status: 'Busy', color: '#f97316' },
  { zone: 'Parking', currentPeople: 210, capacity: 350, percentage: 60, status: 'Moderate', color: '#3b82f6' }
])

const totalPeopleFlow = computed(() => {
  return zonePeopleFlow.value.reduce((sum, zone) => sum + zone.currentPeople, 0)
})

const peakHourFlow = ref('14:00-15:00')

// ========== 卫生间数据 ==========
const restrooms = ref([
  { floor: 'B1 Parking', total: 12, occupied: 4, statusText: 'Available', statusClass: 'available' },
  { floor: '1F Lobby', total: 10, occupied: 3, statusText: 'Available', statusClass: 'available' },
  { floor: '2F Fashion', total: 10, occupied: 7, statusText: 'Limited', statusClass: 'limited' },
  { floor: '3F Food', total: 14, occupied: 5, statusText: 'Available', statusClass: 'available' },
  { floor: '4F Cinema', total: 12, occupied: 9, statusText: 'Limited', statusClass: 'limited' }
])

const computedRestrooms = computed(() => {
  return restrooms.value.map(r => ({
    ...r,
    free: r.total - r.occupied,
    percent: (r.occupied / r.total) * 100
  }))
})

let timeTimer = null, dataInterval = null

// ==================== 辅助函数 ====================
const loadingMessages = ['Preparing assets...', 'Loading background...', 'Initializing modules...', 'Establishing connection...', 'Starting dashboard...', 'Almost ready...']

const preloadBackground = () => new Promise((resolve) => {
  const img = new Image()
  img.src = 'https://aegisnx.com/wp-content/uploads/2026/05/1778306389013.png'
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
  waterCost.value = (waterUsage.value * 0.5).toFixed(2)
  elecCost.value = (elecUsage.value * 0.13).toFixed(2)
  hvacCost.value = (hvacUsage.value * 0.15).toFixed(2)
  lightingCost.value = (lightingUsage.value * 0.12).toFixed(2)
  escalatorCost.value = (escalatorUsage.value * 0.11).toFixed(2)
  waterHeatingCost.value = (waterHeatingUsage.value * 0.14).toFixed(2)
  totalCost.value = (parseFloat(waterCost.value) + parseFloat(elecCost.value) + parseFloat(hvacCost.value) + parseFloat(lightingCost.value) + parseFloat(escalatorCost.value) + parseFloat(waterHeatingCost.value)).toFixed(2)
}

// 更新停车场车流量数据
function updateParkingData() {
  // 车辆数波动 -10% 到 +10%
  let variation = (Math.random() - 0.5) * 0.2
  let newCars = parkingCars.value * (1 + variation)
  newCars = Math.min(parkingCapacity, Math.max(200, newCars))
  parkingCars.value = Math.floor(newCars)
  parkingPercent.value = parseFloat(((parkingCars.value / parkingCapacity) * 100).toFixed(1))

  // 进出车辆数波动
  carsEntered.value = Math.floor(randomVariation(2840, 0.08))
  carsExited.value = Math.floor(randomVariation(2560, 0.08))

  // 平均停留时间变化
  const hours = Math.floor(1 + Math.random() * 2)
  const minutes = Math.floor(Math.random() * 45) + 15
  avgStayTime.value = `${hours}h ${minutes}m`
}

// 更新卫生间数据
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

// 更新店铺营业数据
function updateStoreZones() {
  storeZones.value.forEach(zone => {
    let variation = (Math.random() - 0.5) * 0.06
    let newOpenRate = Math.min(100, Math.max(70, zone.openRate + variation))
    zone.openRate = Math.floor(newOpenRate)
    zone.openStores = Math.floor((zone.openRate / 100) * zone.totalStores)
    zone.avgRating = parseFloat((zone.avgRating + (Math.random() - 0.5) * 0.1).toFixed(1))
    zone.avgRating = Math.min(5, Math.max(3.5, zone.avgRating))

    if (zone.openRate >= 85) zone.progressColor = '#10b981'
    else if (zone.openRate >= 75) zone.progressColor = '#f59e0b'
    else zone.progressColor = '#ef4444'
  })
}

// 更新区域人流数据
function updateZonePeopleFlow() {
  zonePeopleFlow.value.forEach(zone => {
    let variation = (Math.random() - 0.5) * 0.12
    let newPeople = Math.floor(zone.currentPeople * (1 + variation))
    newPeople = Math.min(zone.capacity, Math.max(20, newPeople))
    zone.currentPeople = newPeople
    zone.percentage = Math.floor((zone.currentPeople / zone.capacity) * 100)

    if (zone.percentage >= 75) {
      zone.status = 'Critical'
      zone.color = '#ef4444'
    } else if (zone.percentage >= 60) {
      zone.status = 'Busy'
      zone.color = '#f97316'
    } else if (zone.percentage >= 40) {
      zone.status = 'Moderate'
      zone.color = '#f59e0b'
    } else {
      zone.status = 'Quiet'
      zone.color = '#10b981'
    }
  })

  const hours = ['10:00-11:00', '11:00-12:00', '12:00-13:00', '13:00-14:00', '14:00-15:00', '15:00-16:00', '16:00-17:00', '17:00-18:00', '18:00-19:00', '19:00-20:00']
  peakHourFlow.value = hours[Math.floor(Math.random() * hours.length)]
}

function refreshData() {
  deviceTotal.value = Math.floor(randomVariation(128, 0.03))
  onlineRate.value = randomVariation(98.5, 0.02).toFixed(1)

  waterUsage.value = Math.floor(randomVariation(3860, 0.07))
  waterPercent.value = parseFloat(((waterUsage.value / waterTarget) * 100).toFixed(1))
  elecUsage.value = Math.floor(randomVariation(18600, 0.07))
  elecPercent.value = parseFloat(((elecUsage.value / elecTarget) * 100).toFixed(1))
  hvacUsage.value = Math.floor(randomVariation(9400, 0.07))
  hvacPercent.value = parseFloat(((hvacUsage.value / hvacTarget) * 100).toFixed(1))
  lightingUsage.value = Math.floor(randomVariation(5200, 0.08))
  lightingPercent.value = parseFloat(((lightingUsage.value / lightingTarget) * 100).toFixed(1))
  escalatorUsage.value = Math.floor(randomVariation(3800, 0.08))
  escalatorPercent.value = parseFloat(((escalatorUsage.value / escalatorTarget) * 100).toFixed(1))
  waterHeatingUsage.value = Math.floor(randomVariation(2100, 0.08))
  waterHeatingPercent.value = parseFloat(((waterHeatingUsage.value / waterHeatingTarget) * 100).toFixed(1))

  updateCosts()

  floorPeople.value = Math.min(floorMax, Math.max(300, Math.floor(randomVariation(1680, 0.15))))
  floorPercent.value = parseFloat(((floorPeople.value / floorMax) * 100).toFixed(1))

  updateParkingData()
  updateRestroomData()
  updateStoreSales()
  updateStoreZones()
  updateZonePeopleFlow()

  avgTemp.value = (22 + Math.random() * 6).toFixed(1)
  activeStores.value = Math.floor(randomVariation(128, 0.05))
}

// 初始化 Top 5
updateTopStores()

onMounted(async () => {
  updateTime()
  timeTimer = setInterval(updateTime, 1000)
  await preloadBackground()
  isBackgroundLoaded.value = true
  await nextTick()
  setTimeout(() => { refreshData(); dataInterval = setInterval(refreshData, 3000) }, 100)
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
.dashboard { height: 100%; width: 100%; display: flex; flex-direction: column; background-image: url('https://aegisnx.com/wp-content/uploads/2026/05/1778306389013.png'); background-size: cover; background-position: center; background-attachment: fixed; animation: fadeIn 0.5s; }
.top-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 28px 8px; margin: 0 24px; }
.header-left { width: 140px; }
.header-title { text-align: center; flex: 1; }
.main-title { font-size: 44px; font-weight: 800; background: linear-gradient(135deg, #e0f2fe, #bae6fd); -webkit-background-clip: text; background-clip: text; color: transparent; letter-spacing: 3px; }
.datetime { font-size: 16px; color: #0ff; font-weight: 600; background: transparent; padding: 8px 20px; border-radius: 12px; backdrop-filter: blur(8px); min-width: 280px; text-align: center; font-family: monospace; border: 1px solid rgba(0,255,255,0.5); box-shadow: 0 0 10px rgba(0,255,255,0.3); }
.kpi-strip { display: flex; justify-content: space-around; gap: 20px; margin: 10px 24px 20px; padding: 12px 20px; background: transparent; border-radius: 24px; border: 1px solid rgba(59,130,246,0.3); }
.kpi-item { display: flex; gap: 12px; align-items: baseline; }
.kpi-label { color: #94a3b8; font-weight: 500; }
.kpi-value { font-size: 24px; font-weight: 800; color: #facc15; font-family: monospace; text-shadow: 0 0 8px rgba(250,204,21,0.4); }
.content-area { flex: 1; display: flex; padding: 0 24px 24px; gap: 32px; overflow-y: auto; }
.left-panel { width: 340px; flex-shrink: 0; }
.right-panel { width: 420px; flex-shrink: 0; }
.center-void { flex: 1; }

/* 透明玻璃卡片 */
.glass-card { background: transparent; border-radius: 28px; border: 1px solid rgba(59,130,246,0.4); box-shadow: 0 20px 35px -12px rgba(0,0,0,0.6); padding: 18px; transition: all 0.3s; margin-bottom: 20px; }
.glass-card:hover { background: rgba(8,16,28,0.6); backdrop-filter: blur(8px); transform: translateY(-4px); border-color: rgba(59,130,246,0.6); }
.card-title { font-size: 18px; font-weight: 800; color: #f0f9ff; margin-bottom: 14px; padding-left: 10px; border-left: 4px solid #3b82f6; text-shadow: 0 0 4px rgba(59,130,246,0.5); }

/* 资源卡片 */
.resource-grid { display: flex; justify-content: space-around; text-align: center; }
.second-row { margin-top: 20px; padding-top: 16px; border-top: 1px solid rgba(59,130,246,0.3); }
.resource-item .resource-label { margin-top: 8px; font-size: 12px; font-weight: 600; color: #cbd5e1; }
.resource-value { font-size: 13px; font-weight: 800; color: #facc15; text-shadow: 0 0 4px rgba(250,204,21,0.3); }
.resource-cost { font-size: 11px; font-weight: 600; color: #a5f3fc; margin-top: 4px; }

/* 客流统计 + 车流量 */
.flow-section { margin-bottom: 18px; }
.flow-section:last-child { margin-bottom: 0; }
.section-subtitle { font-size: 13px; font-weight: 700; color: #a5f3fc; margin-bottom: 10px; padding-left: 6px; border-left: 2px solid #f59e0b; }
.parking-stats { margin-bottom: 12px; }
.parking-info { display: flex; justify-content: space-between; margin-bottom: 10px; color: #cbd5e1; font-size: 13px; font-weight: 500; }
.parking-info strong { color: #facc15; }
.traffic-details { display: flex; justify-content: space-between; gap: 12px; margin-top: 12px; padding-top: 10px; border-top: 1px solid rgba(59,130,246,0.3); }
.traffic-item { display: flex; flex-direction: column; align-items: center; gap: 4px; font-size: 11px; color: #94a3b8; }
.traffic-item strong { font-size: 14px; color: #facc15; font-family: monospace; }

/* 门店销售 Top 5 横向柱状图 */
.sales-bar-list { display: flex; flex-direction: column; gap: 14px; }
.sales-bar-item { display: flex; align-items: center; gap: 6px; }
.sales-rank { width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; border-radius: 8px; font-size: 14px; font-weight: 800; background: rgba(255,255,255,0.1); color: #cbd5e1; }
.sales-rank.rank-1 { background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #1e293b; box-shadow: 0 0 8px rgba(245,158,11,0.5); }
.sales-rank.rank-2 { background: linear-gradient(135deg, #94a3b8, #64748b); color: #1e293b; }
.sales-rank.rank-3 { background: linear-gradient(135deg, #cd7f32, #b8860b); color: #1e293b; }
.sales-info { flex: 1; }
.sales-name-line { display: flex; justify-content: space-between; margin-bottom: 4px; }
.sales-name { font-size: 13px; font-weight: 700; }
.sales-category { font-size: 10px; font-weight: 600; color: #64748b; background: rgba(100,116,139,0.3); padding: 2px 6px; border-radius: 10px; }
.sales-bar-wrapper { display: flex; align-items: center; gap: 10px; }
.sales-bar-bg { flex: 1; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden; }
.sales-bar-fill { height: 100%; border-radius: 4px; transition: width 0.5s ease; }
.sales-value-group { display: flex; align-items: center; gap: 6px; min-width: 70px; }
.sales-value { font-size: 12px; font-weight: 800; color: #facc15; font-family: monospace; }
.sales-trend { font-size: 11px; font-weight: 700; padding: 2px 5px; border-radius: 12px; }
.trend-up { background: rgba(16,185,129,0.2); color: #10b981; }
.trend-down { background: rgba(239,68,68,0.2); color: #ef4444; }
.sales-footer { display: flex; justify-content: space-between; margin-top: 14px; padding-top: 12px; border-top: 1px solid rgba(59,130,246,0.35); font-size: 11px; font-weight: 700; color: #94a3b8; }

/* 紧凑型店铺营业数据 */
.store-compact-grid { display: flex; flex-direction: column; gap: 0px; }
.store-compact-item { padding: 0px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
.store-compact-item:last-child { border-bottom: none; }
.store-compact-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.store-compact-name { font-size: 13px; font-weight: 700; color: #e2e8f0; }
.store-compact-numbers { display: flex; align-items: center; gap: 8px; }
.store-open-badge { font-size: 11px; font-weight: 700; color: #a5f3fc; background: rgba(59,130,246,0.2); padding: 2px 8px; border-radius: 12px; }
.store-compact-bar { height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; overflow: hidden; margin-bottom: 6px; }
.store-bar-fill { height: 100%; border-radius: 2px; transition: width 0.3s; }
.store-rate-value { font-size: 12px; font-weight: 800; }

/* 区域人流卡片 */
.people-flow-list { display: flex; flex-direction: column; gap: 12px; }
.flow-row { display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 6px 0; }
.flow-zone { width: 95px; font-size: 12px; font-weight: 700; color: #cbd5e1; }
.flow-progress-wrapper { flex: 1; }
.flow-progress-bg { height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden; }
.flow-progress-fill { height: 100%; border-radius: 3px; transition: width 0.3s; }
.flow-count { width: 70px; font-size: 11px; font-weight: 600; color: #a5f3fc; text-align: right; }
.flow-status { width: 65px; font-size: 11px; font-weight: 700; text-align: right; }
.people-flow-footer { display: flex; justify-content: space-between; margin-top: 12px; padding-top: 10px; border-top: 1px solid rgba(59,130,246,0.35); font-size: 11px; font-weight: 700; color: #94a3b8; }

/* 厕所卡片 */
.restroom-table { width: 100%; }
.restroom-row-header { display: flex; justify-content: space-between; padding: 8px 4px; font-size: 11px; font-weight: 700; color: #60a5fa; text-transform: uppercase; letter-spacing: 0.8px; border-bottom: 1px solid rgba(59,130,246,0.4); margin-bottom: 8px; }
.restroom-row-header span { flex: 1; }
.restroom-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 4px; border-bottom: 1px solid rgba(255,255,255,0.06); transition: all 0.2s; }
.restroom-row:hover { background: rgba(59,130,246,0.12); border-radius: 8px; transform: translateX(4px); }
.floor-name { flex: 1; font-size: 13px; font-weight: 700; color: #e2e8f0; }
.status-badge { flex: 1; text-align: center; font-size: 11px; font-weight: 800; padding: 5px 10px; border-radius: 24px; width: fit-content; margin: 0 auto; }
.status-badge.available { background: rgba(16,185,129,0.2); color: #34d399; }
.status-badge.moderate { background: rgba(245,158,11,0.2); color: #fbbf24; }
.status-badge.limited { background: rgba(239,68,68,0.2); color: #f87171; }
.available-count { flex: 1; text-align: right; font-family: monospace; }
.count-number { font-size: 16px; font-weight: 800; color: #facc15; text-shadow: 0 0 4px rgba(250,204,21,0.4); }
.count-total { font-size: 11px; font-weight: 600; color: #94a3b8; margin-left: 2px; }

/* 滚动条 */
.content-area::-webkit-scrollbar { width: 5px; }
.content-area::-webkit-scrollbar-track { background: rgba(15,23,42,0.5); border-radius: 4px; }
.content-area::-webkit-scrollbar-thumb { background: #3b82f6; border-radius: 4px; }

/* Element Plus 进度条 */
:deep(.el-progress-circle__track) { stroke: rgba(255,255,255,0.2); }
:deep(.el-progress__text) { color: #fff !important; font-weight: 700 !important; font-size: 14px !important; text-shadow: 0 0 4px rgba(0,0,0,0.5); }
:deep(.el-progress-bar__outer) { background-color: rgba(255,255,255,0.1); }
:deep(.el-progress-bar__inner) { border-radius: 10px; }

/* ========== 移动端适配 (宽度 ≤ 768px) ========== */
@media (max-width: 768px) {
  .top-header {
    flex-direction: column;
    padding: 12px 16px 8px;
    margin: 0 12px;
    gap: 8px;
  }
  .header-left { display: none; }
  .main-title {
    font-size: 28px;
    letter-spacing: 1px;
  }
  .datetime {
    font-size: 11px;
    padding: 4px 12px;
    min-width: auto;
    width: auto;
    border-radius: 20px;
    backdrop-filter: blur(4px);
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
    gap: 8px;
  }
  .kpi-label {
    font-size: 12px;
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
  .glass-card:hover {
    transform: none; /* 手机端禁用上浮效果 */
    backdrop-filter: blur(8px);
  }
  .card-title {
    font-size: 16px;
    margin-bottom: 12px;
    padding-left: 8px;
  }

  /* 资源卡片：6个环形进度条自动换行，调整尺寸 */
  .resource-grid {
    flex-wrap: wrap;
    gap: 12px;
    justify-content: center;
  }
  .resource-item {
    flex: 1 1 30%;
    min-width: 90px;
  }
  .resource-item .resource-label {
    font-size: 11px;
    margin-top: 6px;
  }
  .resource-value {
    font-size: 12px;
  }
  .resource-cost {
    font-size: 10px;
  }
  :deep(.el-progress-circle) {
    width: 70px !important;
    height: 70px !important;
  }
  :deep(.el-progress__text) {
    font-size: 11px !important;
  }

  /* 客流统计 + 车流量 */
  .flow-section .parking-info {
    font-size: 12px;
  }
  .traffic-details {
    gap: 8px;
  }
  .traffic-item {
    font-size: 10px;
  }
  .traffic-item strong {
    font-size: 12px;
  }

  /* 门店销售 Top 5 */
  .sales-bar-list {
    gap: 10px;
  }
  .sales-rank {
    width: 24px;
    height: 24px;
    font-size: 12px;
  }
  .sales-name {
    font-size: 12px;
  }
  .sales-category {
    font-size: 9px;
    padding: 1px 4px;
  }
  .sales-value {
    font-size: 11px;
  }
  .sales-trend {
    font-size: 9px;
    padding: 1px 4px;
  }

  /* 区域人流卡片 */
  .flow-zone {
    width: 80px;
    font-size: 11px;
  }
  .flow-count {
    width: 55px;
    font-size: 10px;
  }
  .flow-status {
    width: 55px;
    font-size: 10px;
  }
  .people-flow-footer {
    font-size: 10px;
  }

  /* 店铺营业数据 */
  .store-compact-name {
    font-size: 12px;
  }
  .store-open-badge {
    font-size: 10px;
    padding: 2px 6px;
  }
  .store-rate-value {
    font-size: 11px;
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

  /* 滚动条更细 */
  .content-area::-webkit-scrollbar {
    width: 3px;
  }
}
</style>