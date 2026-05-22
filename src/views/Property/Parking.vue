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
          <span class="loading-title">Loading Parking System</span>
          <span class="loading-dots">...</span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Parking Management System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Page -->
  <div v-else class="parking-page">
    <!-- Left Panel -->
    <div class="left-panel">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">🚗 Parking Management</h1>
        <div class="current-time" v-if="isFullscreen || isMobile">{{ currentTime }}</div>
      </div>

      <!-- 闸门控制区 -->
      <div class="gate-controls">
        <div class="gate-title">🚪 Gate Control</div>
        <div class="gate-buttons">
          <div class="gate-card entrance" :class="{ active: entranceGateStatus === 'open' }">
            <div class="gate-icon">🚪➡️</div>
            <div class="gate-name">Entrance Gate</div>
            <div class="gate-status" :class="entranceGateStatus">
              <span class="status-dot"></span>
              {{ entranceGateStatus === 'open' ? 'Opened' : 'Closed' }}
            </div>
            <el-button :type="entranceGateStatus === 'open' ? 'danger' : 'success'" size="small" @click="toggleEntranceGate" class="gate-btn">
              <span v-if="entranceGateStatus === 'open'">🔒 Close Gate</span>
              <span v-else>🔓 Open Gate</span>
            </el-button>
          </div>
          <div class="gate-card exit" :class="{ active: exitGateStatus === 'open' }">
            <div class="gate-icon">🚪⬅️</div>
            <div class="gate-name">Exit Gate</div>
            <div class="gate-status" :class="exitGateStatus">
              <span class="status-dot"></span>
              {{ exitGateStatus === 'open' ? 'Opened' : 'Closed' }}
            </div>
            <el-button :type="exitGateStatus === 'open' ? 'danger' : 'success'" size="small" @click="toggleExitGate" class="gate-btn">
              <span v-if="exitGateStatus === 'open'">🔒 Close Gate</span>
              <span v-else>🔓 Open Gate</span>
            </el-button>
          </div>
        </div>
      </div>

      <!-- 区域选择器 -->
      <div class="zone-selector">
        <div class="selector-title">📍 Select Zone</div>
        <div class="zone-buttons">
          <button
              v-for="zone in zones"
              :key="zone.name"
              class="zone-select-btn"
              :class="{ active: selectedZoneName === zone.name }"
              @click="selectZone(zone.name)"
          >
            <span class="zone-icon-circle" :style="{ background: zone.color }">{{ zone.name }}</span>
            <span class="zone-name">Zone</span>
            <span class="zone-badge" :style="{ background: zone.color }">{{ zone.occupancyRate }}%</span>
          </button>
        </div>
      </div>

      <!-- 区域统计卡片 -->
      <div class="zone-stats-panel">
        <div class="stats-header">
          <span class="stats-title">📊 {{ selectedZoneName }} Zone Statistics</span>
          <el-button size="small" type="primary" plain @click="showAvailableSpots">
            <el-icon><Search /></el-icon> Query Available Spots
          </el-button>
        </div>
        <div class="zone-stats-grid">
          <div class="zone-stat-card total">
            <div class="stat-icon">🅿️</div>
            <div class="stat-content">
              <span class="stat-value">{{ currentZoneStats.total }}</span>
              <span class="stat-label">Total Spots</span>
            </div>
          </div>
          <div class="zone-stat-card available">
            <div class="stat-icon">🟢</div>
            <div class="stat-content">
              <span class="stat-value">{{ currentZoneStats.available }}</span>
              <span class="stat-label">Available</span>
            </div>
          </div>
          <div class="zone-stat-card occupied">
            <div class="stat-icon">🔴</div>
            <div class="stat-content">
              <span class="stat-value">{{ currentZoneStats.occupied }}</span>
              <span class="stat-label">Occupied</span>
            </div>
          </div>
          <div class="zone-stat-card disabled">
            <div class="stat-icon">⚠️</div>
            <div class="stat-content">
              <span class="stat-value">{{ currentZoneStats.disabled }}</span>
              <span class="stat-label">Out of Service</span>
            </div>
          </div>
        </div>
        <div class="zone-progress-section">
          <div class="progress-label">Occupancy Rate</div>
          <el-progress :percentage="currentZoneStats.occupancyRate" :stroke-width="12" :color="currentZoneColor" />
        </div>
      </div>

      <!-- 充电桩管理 -->
      <div class="ev-charging-panel">
        <div class="panel-header">
          <span class="panel-title">⚡ EV Charging Stations</span>
          <el-tag size="small" :type="evChargingStats.available > 0 ? 'success' : 'danger'">
            {{ evChargingStats.available }}/{{ evChargingStats.total }} Available
          </el-tag>
        </div>
        <div class="ev-stats-summary">
          <div class="ev-stat">
            <span class="ev-stat-value">{{ evChargingStats.total }}</span>
            <span class="ev-stat-label">Total Chargers</span>
          </div>
          <div class="ev-stat">
            <span class="ev-stat-value success">{{ evChargingStats.available }}</span>
            <span class="ev-stat-label">Available</span>
          </div>
          <div class="ev-stat">
            <span class="ev-stat-value warning">{{ evChargingStats.inUse }}</span>
            <span class="ev-stat-label">In Use</span>
          </div>
          <div class="ev-stat">
            <span class="ev-stat-value danger">{{ evChargingStats.misused }}</span>
            <span class="ev-stat-label">EV Spot Misused</span>
          </div>
        </div>
        <div class="ev-chargers-list">
          <div v-for="charger in evChargers" :key="charger.id" class="ev-charger-item" :class="charger.status">
            <div class="charger-icon">
              <span v-if="charger.status === 'available'">🔌</span>
              <span v-else-if="charger.status === 'charging'">⚡</span>
              <span v-else-if="charger.status === 'misused'">⚠️</span>
              <span v-else>🔧</span>
            </div>
            <div class="charger-info">
              <div class="charger-name">{{ charger.name }}</div>
              <div class="charger-location">{{ charger.location }}</div>
              <div v-if="charger.status === 'charging'" class="charger-vehicle">🚗 {{ charger.vehiclePlate }}</div>
              <div v-if="charger.status === 'misused'" class="charger-warning">⚠️ Non-EV vehicle parked</div>
            </div>
            <div class="charger-status">
              <el-tag :type="getChargerStatusType(charger.status)" size="small">
                {{ getChargerStatusText(charger.status) }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>

      <!-- 车辆进出记录 -->
      <div class="vehicle-records">
        <div class="section-title">
          <span>📋 Vehicle Entry/Exit Records</span>
          <el-tag size="small" type="success">Live</el-tag>
        </div>
        <div class="records-list">
          <div v-for="record in vehicleRecords" :key="record.id" class="record-item">
            <div class="record-direction" :class="record.type">
              <span v-if="record.type === 'entry'">ENTRY</span>
              <span v-else>EXIT</span>
            </div>
            <div class="record-info">
              <span class="record-plate">{{ record.plateNumber }}</span>
              <span class="record-time">{{ record.time }}</span>
            </div>
            <div v-if="record.type === 'exit'" class="record-fee">
              ${{ record.fee }}
            </div>
            <div class="record-vehicle-type">
              <el-tag size="small" :type="record.vehicleType === 'EV' ? 'success' : 'info'">
                {{ record.vehicleType }}
              </el-tag>
            </div>

          </div>
        </div>
      </div>
    </div>

    <!-- Right Panel -->
    <div class="right-panel">
      <!-- 停车场图片 -->
      <div class="image-container" ref="imageContainerRef">
        <el-image :src="parkingImageUrl" fit="contain" class="parking-image" @load="onImageLoad" />
        <div class="image-overlay"></div>
      </div>

      <!-- 动态内容区域 -->
      <div class="dynamic-content" :style="{ height: dynamicContentHeight + 'px' }">
        <!-- 今日统计卡片 -->
        <div class="today-stats">
          <div class="today-stat"><span class="today-icon">💰</span><span class="today-value">${{ todayRevenue }}k</span><span class="today-label">Revenue</span></div>
          <div class="today-stat"><span class="today-icon">🚗</span><span class="today-value">{{ todayEntries }}</span><span class="today-label">Entries</span></div>
          <div class="today-stat"><span class="today-icon">🚙</span><span class="today-value">{{ todayExits }}</span><span class="today-label">Exits</span></div>
          <div class="today-stat"><span class="today-icon">⚡</span><span class="today-value">{{ evChargingStats.total }}</span><span class="today-label">EV Chargers</span></div>
        </div>
      </div>
    </div>
  </div>

  <!-- 可用车位弹窗 -->
  <el-dialog v-model="availableSpotsDialogVisible" title="Available Parking Spots" width="600px" class="spots-dialog">
    <div class="available-spots-list">
      <div class="spots-header">
        <span>Spot Number</span>
        <span>Type</span>
        <span>Location</span>
      </div>
      <div v-for="spot in availableSpotsList" :key="spot.number" class="spot-item">
        <span class="spot-number">{{ spot.number }}</span>
        <span class="spot-type">
          <el-tag :type="spot.type === 'EV' ? 'success' : 'info'" size="small">{{ spot.type === 'EV' ? 'EV Charging' : 'Standard' }}</el-tag>
        </span>
        <span class="spot-location">{{ spot.location }}</span>
        <el-button size="small" type="primary" link @click="reserveSpotFromList(spot)">Reserve</el-button>
      </div>
      <div v-if="availableSpotsList.length === 0" class="no-spots">No available spots in this zone</div>
    </div>
  </el-dialog>

  <!-- 车位详情弹窗 -->
  <el-dialog v-model="spotDetailVisible" :title="`Parking Spot ${selectedSpot?.number}`" width="400px" class="spot-dialog">
    <div class="spot-detail-content">
      <div class="spot-status-large" :class="selectedSpot?.status">
        <span v-if="selectedSpot?.status === 'available'">🟢 Available</span>
        <span v-else-if="selectedSpot?.status === 'occupied'">🔴 Occupied</span>
        <span v-else-if="selectedSpot?.status === 'ev'">⚡ EV Charging</span>
        <span v-else>⚠️ Out of Service</span>
      </div>
      <div v-if="selectedSpot?.status === 'occupied'" class="spot-vehicle-info">
        <div class="info-row"><span class="info-label">Plate:</span><span class="info-value">{{ selectedSpot.plateNumber }}</span></div>
        <div class="info-row"><span class="info-label">Type:</span><span class="info-value">{{ selectedSpot.vehicleType }}</span></div>
        <div class="info-row"><span class="info-label">Entry:</span><span class="info-value">{{ selectedSpot.entryTime }}</span></div>
        <div class="info-row"><span class="info-label">Duration:</span><span class="info-value">{{ selectedSpot.duration }}</span></div>
      </div>
      <div v-if="selectedSpot?.status === 'ev' && selectedSpot?.isCharging" class="charging-info">
        <div class="info-row"><span class="info-label">Charging:</span><span class="info-value">⚡ In Progress</span></div>
        <div class="info-row"><span class="info-label">Power:</span><span class="info-value">50 kW</span></div>
        <div class="info-row"><span class="info-label">SOC:</span><span class="info-value">78%</span></div>
      </div>
      <div v-if="selectedSpot?.status === 'ev' && !selectedSpot?.isCharging" class="charging-warning">
        ⚠️ EV parking spot occupied by non-EV vehicle!
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useCounterStore } from '@/stores/counter.js'
import { getCurrentInstance } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const getStore = () => {
  const instance = getCurrentInstance()
  if (!instance) throw new Error('useStore() must be called within a setup function')
  const pinia = instance.appContext.config.globalProperties.$pinia
  if (!pinia) throw new Error('Pinia instance not found')
  return useCounterStore(pinia)
}
const counterStore = getStore()
const isFullscreen = computed(() => counterStore.isFullscreen)

// 图片URL
const parkingImageUrl = ref('https://aegisnx.com/wp-content/uploads/2026/05/52013147654.jpg')

// 区域数据 - EV充电桩数据与车位数据完全对应
const selectedZoneName = ref('A')
const selectedZoneColor = ref('#409eff')

const zones = ref([
  {
    name: 'A', icon: '🅰️', color: '#409eff',
    total: 112, available: 34, occupied: 70, disabled: 8,
    evTotal: 12,      // 总共12个EV充电车位
    evAvailable: 5,   // 空闲的EV车位 = 对应充电桩可用
    evCharging: 4,    // 正在充电的EV车位 = 对应充电桩使用中
    evMisused: 3,     // 被非EV车占用的EV车位 = 对应充电桩被滥用
    occupancyRate: 70
  },
  {
    name: 'B', icon: '🅱️', color: '#67c23a',
    total: 118, available: 33, occupied: 80, disabled: 5,
    evTotal: 10,
    evAvailable: 4,
    evCharging: 4,
    evMisused: 2,
    occupancyRate: 72
  },
  {
    name: 'C', icon: '🇨', color: '#e6a23c',
    total: 110, available: 46, occupied: 58, disabled: 6,
    evTotal: 8,
    evAvailable: 3,
    evCharging: 3,
    evMisused: 2,
    occupancyRate: 58
  },
  {
    name: 'D', icon: '🇩', color: '#f56c6c',
    total: 110, available: 26, occupied: 78, disabled: 6,
    evTotal: 6,
    evAvailable: 2,
    evCharging: 3,
    evMisused: 1,
    occupancyRate: 76
  }
])

// 当前区域统计
const currentZoneStats = computed(() => {
  const zone = zones.value.find(z => z.name === selectedZoneName.value)
  return zone || zones.value[0]
})
const currentZoneColor = computed(() => currentZoneStats.value?.color || '#409eff')

// 今日统计（保留两位小数）
const todayRevenue = ref(8.42)
const todayEntries = ref(342)
const todayExits = ref(318)
const avgStayTime = ref(94)

// 充电桩统计数据 - 直接从区域数据计算，保证数据一致
const evChargingStats = computed(() => {
  const zone = zones.value.find(z => z.name === selectedZoneName.value)
  if (!zone) return { total: 0, available: 0, inUse: 0, misused: 0, usageRate: 0 }

  return {
    total: zone.evTotal,
    available: zone.evAvailable,
    inUse: zone.evCharging,
    misused: zone.evMisused,
    usageRate: zone.evTotal > 0 ? Math.round((zone.evCharging / zone.evTotal) * 100) : 0
  }
})

const evUsageRate = computed(() => evChargingStats.value.usageRate)

// 全局统计
const globalAvailableSpaces = computed(() => {
  return zones.value.reduce((sum, z) => sum + z.available, 0)
})
const globalOccupancyRate = computed(() => {
  const totalSpaces = zones.value.reduce((sum, z) => sum + z.total, 0)
  const totalOccupied = zones.value.reduce((sum, z) => sum + z.occupied, 0)
  return Math.round((totalOccupied / totalSpaces) * 100)
})

// 充电桩列表 - 根据区域数据动态生成，保证数据完全对应
const evChargers = computed(() => {
  const zone = zones.value.find(z => z.name === selectedZoneName.value)
  if (!zone) return []

  const chargers = []
  const spotPrefix = selectedZoneName.value

  // 构建充电桩状态数组
  let statuses = []
  // 添加正在充电的
  for (let i = 0; i < zone.evCharging; i++) {
    statuses.push({ status: 'charging', type: 'charging' })
  }
  // 添加被滥用的
  for (let i = 0; i < zone.evMisused; i++) {
    statuses.push({ status: 'misused', type: 'misused' })
  }
  // 添加可用的
  for (let i = 0; i < zone.evAvailable; i++) {
    statuses.push({ status: 'available', type: 'available' })
  }

  // 打乱顺序，让显示更真实
  for (let i = statuses.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [statuses[i], statuses[j]] = [statuses[j], statuses[i]]
  }

  const vehiclePlates = {
    charging: ['SGEV5678B', 'SGC8901M', 'SGZ7890H', 'SGEV1234C', 'SGEV4567D', 'SGEV8901E'],
    misused: ['SGD1234A', 'SGH9101C', 'SGM5678E', 'SGY1234D']
  }

  let chargingIndex = 0
  let misusedIndex = 0

  for (let i = 0; i < zone.evTotal; i++) {
    const statusInfo = statuses[i]
    const spotNumber = `${spotPrefix}${String(i * 10 + 5).padStart(3, '0')}`
    let vehiclePlate = null
    let soc = null

    if (statusInfo.status === 'charging') {
      vehiclePlate = vehiclePlates.charging[chargingIndex % vehiclePlates.charging.length]
      chargingIndex++
      soc = Math.floor(40 + Math.random() * 50)
    } else if (statusInfo.status === 'misused') {
      vehiclePlate = vehiclePlates.misused[misusedIndex % vehiclePlates.misused.length]
      misusedIndex++
    }

    chargers.push({
      id: i + 1,
      name: `EV Charger #${String(i + 1).padStart(2, '0')}`,
      location: `Zone ${selectedZoneName.value} - Spot ${spotNumber}`,
      status: statusInfo.status,
      power: (i + 1) % 2 === 0 ? '150kW' : '50kW',
      vehiclePlate: vehiclePlate,
      soc: soc
    })
  }

  return chargers
})

// 车辆进出记录
const vehicleRecords = ref([
  { id: 1, type: 'entry', plateNumber: 'SGD1234A', time: '14:32:15', vehicleType: 'Sedan', fee: null },
  { id: 2, type: 'entry', plateNumber: 'SGEV5678B', time: '14:28:42', vehicleType: 'EV', fee: null },
  { id: 3, type: 'exit', plateNumber: 'SGM5678E', time: '14:25:10', vehicleType: 'SUV', fee: 8.50 },
  { id: 4, type: 'entry', plateNumber: 'SGH9101C', time: '14:20:33', vehicleType: 'SUV', fee: null },
  { id: 5, type: 'exit', plateNumber: 'SGY1234D', time: '14:15:22', vehicleType: 'Sedan', fee: 6.00 },
  { id: 6, type: 'entry', plateNumber: 'SGZ7890H', time: '14:10:05', vehicleType: 'EV', fee: null },
  { id: 7, type: 'exit', plateNumber: 'SGD1234A', time: '14:05:30', vehicleType: 'Sedan', fee: 4.50 },
  { id: 8, type: 'entry', plateNumber: 'SGZ2345J', time: '13:58:20', vehicleType: 'Sedan', fee: null }
])

// 闸门状态
const entranceGateStatus = ref('closed')
const exitGateStatus = ref('closed')

// 弹窗状态
const availableSpotsDialogVisible = ref(false)
const availableSpotsList = ref([])
const spotDetailVisible = ref(false)
const selectedSpot = ref(null)

// 动态高度
const imageContainerRef = ref(null)
const imageHeight = ref(0)
const dynamicContentHeight = ref(300)

// 选择区域
const selectZone = (zoneName) => {
  selectedZoneName.value = zoneName
  const zone = zones.value.find(z => z.name === zoneName)
  if (zone) selectedZoneColor.value = zone.color
}

// 查询可用车位（标准和充电）
const showAvailableSpots = () => {
  const zone = zones.value.find(z => z.name === selectedZoneName.value)
  if (!zone) return

  const spots = []
  // 标准车位空余
  const standardAvailable = zone.available - (zone.evTotal - zone.evAvailable)
  const spotCount = Math.min(standardAvailable + zone.evAvailable, 30)

  let standardCount = 0
  let evCount = 0

  for (let i = 1; i <= spotCount; i++) {
    let isEv = false
    if (evCount < zone.evAvailable && (standardCount >= standardAvailable || Math.random() > 0.6)) {
      isEv = true
      evCount++
    } else {
      standardCount++
    }

    const spotNumber = `${zone.name}${String(Math.floor(Math.random() * 200) + 1).padStart(3, '0')}`
    spots.push({
      number: spotNumber,
      type: isEv ? 'EV' : 'Standard',
      location: `Zone ${zone.name} - ${spotNumber}`
    })
  }
  availableSpotsList.value = spots
  availableSpotsDialogVisible.value = true
}

const reserveSpotFromList = (spot) => {
  ElMessage.success(`Spot ${spot.number} reserved for 30 minutes`)
  availableSpotsDialogVisible.value = false
}

const getChargerStatusType = (status) => {
  const map = { available: 'success', charging: 'warning', misused: 'danger', fault: 'info' }
  return map[status] || 'info'
}

const getChargerStatusText = (status) => {
  const map = { available: 'Available', charging: 'Charging', misused: 'Misused', fault: 'Maintenance' }
  return map[status] || status
}

// 模拟新增进出记录
const addVehicleRecord = (type, plateNumber, vehicleType, fee = null) => {
  const newRecord = {
    id: Date.now(),
    type: type,
    plateNumber: plateNumber,
    time: new Date().toLocaleTimeString(),
    vehicleType: vehicleType,
    fee: fee ? parseFloat(fee.toFixed(2)) : null
  }
  vehicleRecords.value.unshift(newRecord)
  if (vehicleRecords.value.length > 20) vehicleRecords.value.pop()

  if (type === 'entry') {
    todayEntries.value++
  } else {
    todayExits.value++
    if (fee) todayRevenue.value = parseFloat((todayRevenue.value + fee / 1000).toFixed(2))
  }
}

// 图片加载
const onImageLoad = (e) => {
  const img = e?.target
  if (img) {
    const naturalWidth = img.naturalWidth
    const naturalHeight = img.naturalHeight
    const containerWidth = imageContainerRef.value?.clientWidth || window.innerWidth - 520 - 48
    if (containerWidth && naturalWidth) imageHeight.value = (naturalHeight / naturalWidth) * containerWidth
  }
  setTimeout(() => updateLayoutHeights(), 100)
}

const updateLayoutHeights = () => {
  const rightPanel = document.querySelector('.right-panel')
  if (!rightPanel) return
  const panelHeight = rightPanel.clientHeight
  const calculatedHeight = panelHeight - imageHeight.value - 32
  dynamicContentHeight.value = Math.max(calculatedHeight, 280)
}

const handleWindowResize = () => {
  const containerWidth = imageContainerRef.value?.clientWidth || window.innerWidth - 520 - 48
  if (containerWidth) {
    const imgElement = document.querySelector('.parking-image')
    if (imgElement && imgElement.naturalWidth) imageHeight.value = (imgElement.naturalHeight / imgElement.naturalWidth) * containerWidth
  }
  setTimeout(() => updateLayoutHeights(), 150)
}

// 当前时间
const currentTime = ref('')
let timeInterval = null
let dataInterval = null

const updateCurrentTime = () => {
  const now = new Date()
  const utc = now.getTime() + (now.getTimezoneOffset() * 60000)
  const sgTime = new Date(utc + (8 * 3600000))
  currentTime.value = `${sgTime.getFullYear()}-${String(sgTime.getMonth()+1).padStart(2,'0')}-${String(sgTime.getDate()).padStart(2,'0')} ${String(sgTime.getHours()).padStart(2,'0')}:${String(sgTime.getMinutes()).padStart(2,'0')}:${String(sgTime.getSeconds()).padStart(2,'0')}.${String(sgTime.getMilliseconds()).padStart(3,'0')} SGT`
}

// 模拟实时更新 - 保持EV车位和充电桩数据同步
const updateRealTimeData = () => {
  // 随机选择一个区域
  const zoneNames = ['A', 'B', 'C', 'D']
  const randomZoneName = zoneNames[Math.floor(Math.random() * zoneNames.length)]
  const zoneIndex = zones.value.findIndex(z => z.name === randomZoneName)

  if (zoneIndex !== -1) {
    const zone = zones.value[zoneIndex]

    // 随机改变一个EV车位的状态
    const evChangeType = Math.floor(Math.random() * 4) // 0:无变化, 1:可用变充电, 2:充电变可用, 3:滥用变可用

    let newEvAvailable = zone.evAvailable
    let newEvCharging = zone.evCharging
    let newEvMisused = zone.evMisused

    if (evChangeType === 1 && zone.evAvailable > 0) {
      // 一个空闲EV车位开始充电
      newEvAvailable--
      newEvCharging++
      addVehicleRecord('entry', `SGEV${Math.floor(Math.random() * 9000 + 1000)}${String.fromCharCode(65 + Math.floor(Math.random() * 26))}`, 'EV')
    } else if (evChangeType === 2 && zone.evCharging > 0) {
      // 一个充电中的车离开
      newEvCharging--
      newEvAvailable++
      const fee = parseFloat((Math.random() * 15 + 5).toFixed(2))
      addVehicleRecord('exit', 'SGEV' + Math.floor(Math.random() * 9000 + 1000) + 'X', 'EV', fee)
    } else if (evChangeType === 3 && zone.evMisused > 0) {
      // 被占用的EV车位被清空
      newEvMisused--
      newEvAvailable++
      addVehicleRecord('exit', 'SGD' + Math.floor(Math.random() * 9000 + 1000) + 'X', 'Sedan')
    }

    // 更新区域数据
    zones.value[zoneIndex] = {
      ...zone,
      evAvailable: newEvAvailable,
      evCharging: newEvCharging,
      evMisused: newEvMisused
    }
  }

  // 保留两位小数
  todayRevenue.value = parseFloat(todayRevenue.value.toFixed(2))
}

// 闸门控制
const toggleEntranceGate = async () => {
  const action = entranceGateStatus.value === 'open' ? 'close' : 'open'
  await ElMessageBox.confirm(`${action === 'open' ? 'Open' : 'Close'} entrance gate?`, 'Gate Control', { confirmButtonText: 'Confirm', cancelButtonText: 'Cancel', type: 'warning' })
  entranceGateStatus.value = entranceGateStatus.value === 'open' ? 'closed' : 'open'
  ElMessage.success(`Entrance gate ${entranceGateStatus.value === 'open' ? 'opened' : 'closed'}`)
}

const toggleExitGate = async () => {
  const action = exitGateStatus.value === 'open' ? 'close' : 'open'
  await ElMessageBox.confirm(`${action === 'open' ? 'Open' : 'Close'} exit gate?`, 'Gate Control', { confirmButtonText: 'Confirm', cancelButtonText: 'Cancel', type: 'warning' })
  exitGateStatus.value = exitGateStatus.value === 'open' ? 'closed' : 'open'
  ElMessage.success(`Exit gate ${exitGateStatus.value === 'open' ? 'opened' : 'closed'}`)
}

// 加载动画
const isBackgroundLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing assets...')
const loadingMessages = ['Preparing assets...', 'Loading parking data...', 'Initializing sensors...', 'Establishing connection...', 'Starting dashboard...', 'Almost ready...']

const preloadBackground = () => new Promise((resolve) => {
  const img = new Image()
  img.src = parkingImageUrl.value
  let progress = 0, msgIdx = 0
  const msgInterval = setInterval(() => { if (msgIdx < loadingMessages.length - 1) loadingMessage.value = loadingMessages[++msgIdx] }, 800)
  const progInterval = setInterval(() => { if (progress < 90) { progress += Math.random() * 10; loadingProgress.value = Math.min(progress, 90) } }, 100)
  img.onload = () => { clearInterval(msgInterval); clearInterval(progInterval); loadingMessage.value = 'Ready!'; loadingProgress.value = 100; setTimeout(resolve, 500) }
  img.onerror = () => { clearInterval(msgInterval); clearInterval(progInterval); loadingProgress.value = 100; setTimeout(resolve, 300) }
})

// 移动端检测
const isMobile = ref(false)
const checkMobile = () => { isMobile.value = window.innerWidth < 768; setTimeout(() => updateLayoutHeights(), 100) }
const observeRightPanel = () => {
  const rightPanel = document.querySelector('.right-panel')
  if (rightPanel && window.ResizeObserver) {
    const resizeObserver = new ResizeObserver(() => updateLayoutHeights())
    resizeObserver.observe(rightPanel)
  }
}

onMounted(async () => {
  checkMobile()
  await preloadBackground()
  isBackgroundLoaded.value = true
  await nextTick()
  setTimeout(() => { updateLayoutHeights(); observeRightPanel() }, 200)
  updateCurrentTime()
  timeInterval = setInterval(updateCurrentTime, 100)
  dataInterval = setInterval(updateRealTimeData, 8000)
  window.addEventListener('resize', handleWindowResize)
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
  if (dataInterval) clearInterval(dataInterval)
  window.removeEventListener('resize', handleWindowResize)
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
/* ... 保持原有样式 ... */
.zone-icon-circle {
  width: 30px;
  height: 25px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  color: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  transition: transform 0.2s;
}
.zone-select-btn:hover .zone-icon-circle {
  transform: scale(1.05);
}
/* Loading样式保持不变 */
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
.progress-bar { height: 100%; background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec489a); transition: width 0.3s; }
.loading-tip { font-size: 13px; color: #94a3b8; margin-bottom: 8px; }
.loading-subtip { font-size: 11px; color: #64748b; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

/* 主页面 */
.parking-page { display: flex; width: 100%; height: 100%; background: linear-gradient(135deg, #0a0f1a 0%, #0f172a 100%); overflow: hidden; }

/* 左侧面板 */
.left-panel { width: 620px; padding: 20px; background: rgba(15,23,42,0.75); backdrop-filter: blur(12px); border-right: 1px dashed rgba(59,130,246,0.3); display: flex; flex-direction: column; height: 100%; overflow-y: auto; }

/* 右侧面板 */
.right-panel { flex: 1; display: flex; flex-direction: column; height: 100%; padding: 20px 24px; overflow-y: auto; }

/* 页面头部 */
.page-header { display: flex; justify-content: space-between; align-items: baseline; padding-bottom: 12px; border-bottom: 1px solid rgba(59,130,246,0.3); flex-shrink: 0; }
.page-title { font-size: 22px; font-weight: 800; background: linear-gradient(135deg, #e0f2fe, #bae6fd); -webkit-background-clip: text; background-clip: text; color: transparent; margin: 0; }
.current-time { font-size: 16px; font-family: monospace; color: #a5f3c3; background: rgba(0,0,0,0.5); padding: 4px 10px; border-radius: 20px; border: 1px solid rgba(16,185,129,0.3); }

/* 闸门控制 */
.gate-controls { background: linear-gradient(135deg, rgba(0,0,0,0.4), rgba(0,0,0,0.2)); border-radius: 20px; padding: 16px; margin: 16px 0; border: 1px solid rgba(59,130,246,0.2); }
.gate-title { font-size: 14px; font-weight: 600; color: #e2e8f0; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
.gate-title::before { content: '🚪'; font-size: 16px; }
.gate-buttons { display: flex; gap: 20px; }
.gate-card { flex: 1; background: rgba(0,0,0,0.4); border-radius: 16px; padding: 16px; text-align: center; transition: all 0.3s; border: 1px solid rgba(255,255,255,0.05); }
.gate-card.entrance.active, .gate-card.exit.active { background: linear-gradient(135deg, rgba(16,185,129,0.15), rgba(16,185,129,0.05)); border-color: #10b981; box-shadow: 0 4px 15px rgba(16,185,129,0.2); }
.gate-icon { font-size: 28px; margin-bottom: 8px; }
.gate-name { font-size: 14px; font-weight: 600; color: #e2e8f0; margin-bottom: 8px; }
.gate-status { font-size: 12px; display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 20px; margin-bottom: 12px; }
.gate-status.open { background: rgba(16,185,129,0.2); color: #34d399; }
.gate-status.closed { background: rgba(239,68,68,0.2); color: #f87171; }
.status-dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }
.gate-status.open .status-dot { background: #10b981; box-shadow: 0 0 5px #10b981; }
.gate-status.closed .status-dot { background: #ef4444; }
.gate-btn { width: 100%; margin-top: 4px; }

/* 区域选择器 */
.zone-selector { margin-bottom: 16px; }
.selector-title { font-size: 12px; font-weight: 500; color: #94a3b8; margin-bottom: 8px; }
.zone-buttons { display: flex; gap: 12px; }
.zone-select-btn { flex: 1; background: rgba(0,0,0,0.4); border: 2px solid transparent; border-radius: 16px; padding: 12px 8px; display: flex; align-items: center; justify-content: center; gap: 8px; cursor: pointer; transition: all 0.2s; color: #e2e8f0; }
.zone-select-btn:hover { background: rgba(59,130,246,0.2); transform: translateY(-2px); }
.zone-select-btn.active { background: rgba(59,130,246,0.2); border-color: #409eff; box-shadow: 0 2px 10px rgba(64,158,255,0.3); }
.zone-icon { font-size: 18px; }
.zone-name { font-size: 14px; font-weight: 600; }
.zone-badge { padding: 2px 8px; border-radius: 20px; font-size: 11px; font-weight: 600; color: white; }

/* 区域统计面板 */
.zone-stats-panel { background: rgba(0,0,0,0.3); border-radius: 20px; padding: 16px; margin-bottom: 16px; }
.stats-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.stats-title { font-size: 15px; font-weight: 700; color: #e2e8f0; }
.zone-stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }
.zone-stat-card { background: rgba(0,0,0,0.2); border-radius: 16px; padding: 12px; display: flex; align-items: center; gap: 12px; }
.zone-stat-card.total .stat-icon { color: #409eff; }
.zone-stat-card.available .stat-icon { color: #10b981; }
.zone-stat-card.occupied .stat-icon { color: #ef4444; }
.zone-stat-card.disabled .stat-icon { color: #f59e0b; }
.stat-icon { font-size: 24px; }
.stat-content { flex: 1; }
.stat-value { font-size: 24px; font-weight: 700; color: #facc15; display: block; }
.stat-label { font-size: 10px; color: #94a3b8; }
.zone-progress-section { margin-top: 8px; }
.progress-label { font-size: 11px; color: #94a3b8; margin-bottom: 6px; }

/* 充电桩面板 */
.ev-charging-panel { background: rgba(0,0,0,0.3); border-radius: 20px; padding: 16px; margin-bottom: 16px; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.panel-title { font-size: 15px; font-weight: 700; color: #e2e8f0; }
.ev-stats-summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid rgba(59,130,246,0.2); }
.ev-stat { text-align: center; }
.ev-stat-value { font-size: 24px; font-weight: 700; color: #facc15; display: block; }
.ev-stat-value.success { color: #10b981; }
.ev-stat-value.warning { color: #f59e0b; }
.ev-stat-value.danger { color: #ef4444; }
.ev-stat-label { font-size: 10px; color: #94a3b8; }
.ev-chargers-list { max-height: 200px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
.ev-charger-item { background: rgba(0,0,0,0.2); border-radius: 12px; padding: 12px; display: flex; align-items: center; gap: 12px; transition: all 0.2s; }
.ev-charger-item.available { border-left: 3px solid #10b981; }
.ev-charger-item.charging { border-left: 3px solid #3b82f6; background: rgba(59,130,246,0.1); }
.ev-charger-item.misused { border-left: 3px solid #f59e0b; background: rgba(245,158,11,0.1); }
.ev-charger-item.fault { border-left: 3px solid #ef4444; }
.charger-icon { font-size: 24px; width: 40px; text-align: center; }
.charger-info { flex: 1; }
.charger-name { font-size: 13px; font-weight: 600; color: #e2e8f0; }
.charger-location { font-size: 10px; color: #94a3b8; }
.charger-vehicle { font-size: 10px; color: #3b82f6; margin-top: 2px; }
.charger-warning { font-size: 10px; color: #f59e0b; margin-top: 2px; }
.charger-status { flex-shrink: 0; }

/* 车辆进出记录 - 新增样式 */
.vehicle-records { background: rgba(0,0,0,0.3); border-radius: 16px; padding: 16px; margin-top: 8px; }
.section-title { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; font-size: 14px; font-weight: 600; color: #e2e8f0; }
.records-list { max-height: 280px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
.record-item { background: rgba(0,0,0,0.2); border-radius: 12px; padding: 10px 12px; display: flex; align-items: center; gap: 12px; transition: all 0.2s; }
.record-item:hover { background: rgba(59,130,246,0.1); }
.record-direction { width: 100px; font-size: 11px; font-weight: 600; padding: 4px 8px; border-radius: 20px; text-align: center; }
.record-direction.entry { background: rgba(16,185,129,0.2); color: #34d399; }
.record-direction.exit { background: rgba(239,68,68,0.2); color: #f87171; }
.record-info { flex: 1; display: flex; flex-direction: column;margin-left: 100px }
.record-plate { font-size: 13px; font-weight: 700; color: #facc15; font-family: monospace; }
.record-time { font-size: 10px; color: #94a3b8; }
.record-fee { font-size: 12px; font-weight: 600; color: #10b981; min-width: 50px; text-align: right; }
.record-vehicle-type { flex-shrink: 0; }

/* 右侧面板样式 (保持不变) */
.image-container { width: 100%; border-radius: 20px; overflow: hidden; margin-bottom: 16px; box-shadow: 0 20px 35px -12px rgba(0,0,0,0.5); flex-shrink: 0; }
.parking-image { width: 100%; height: auto; display: block; object-fit: contain; }
.image-overlay { position: absolute; inset: 0; background: linear-gradient(135deg, rgba(15,23,42,0.2) 0%, rgba(15,23,42,0.05) 100%); pointer-events: none; }
.dynamic-content { display: flex; flex-direction: column; gap: 16px; overflow-y: auto;margin-top: 20px }
.today-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; background: rgba(0,0,0,0.3); border-radius: 16px; padding: 16px; }
.today-stat { text-align: center; padding: 8px; background: rgba(255,255,255,0.05); border-radius: 12px; }
.today-icon { font-size: 20px; display: block; margin-bottom: 6px; }
.today-value { font-size: 18px; font-weight: 700; color: #facc15; display: block; }
.today-label { font-size: 10px; color: #94a3b8; display: block; margin-top: 4px; }
.realtime-stats { background: rgba(0,0,0,0.3); border-radius: 16px; padding: 16px; }
.stats-header { font-size: 13px; font-weight: 600; color: #e2e8f0; margin-bottom: 12px; }
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.rt-stat { text-align: center; }
.rt-label { font-size: 10px; color: #94a3b8; display: block; margin-bottom: 4px; }
.rt-value { font-size: 16px; font-weight: 700; color: #facc15; }
.rt-unit { font-size: 10px; font-weight: 400; }
.zones-overview { background: rgba(0,0,0,0.3); border-radius: 16px; padding: 16px; }
.overview-header { font-size: 13px; font-weight: 600; color: #e2e8f0; margin-bottom: 12px; }
.overview-grid { display: grid; gap: 10px; }
.overview-card { background: rgba(0,0,0,0.2); border-radius: 12px; padding: 12px; border-left: 3px solid; cursor: pointer; transition: all 0.2s; }
.overview-card:hover { transform: translateX(3px); background: rgba(59,130,246,0.1); }
.overview-name { font-size: 13px; font-weight: 600; color: #e2e8f0; margin-bottom: 8px; }
.overview-numbers { display: flex; justify-content: space-between; font-size: 11px; color: #94a3b8; margin-bottom: 8px; }
.overview-rate { font-weight: 600; color: #facc15; }
.overview-bar { height: 4px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden; }
.overview-fill { height: 100%; border-radius: 4px; transition: width 0.3s; }
.trend-indicators { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; background: rgba(0,0,0,0.3); border-radius: 16px; padding: 16px; }
.trend-item { text-align: center; }
.trend-icon { font-size: 20px; display: block; margin-bottom: 6px; }
.trend-label { font-size: 10px; color: #94a3b8; display: block; }
.trend-value { font-size: 12px; font-weight: 600; color: #facc15; display: block; margin-top: 4px; }

/* 弹窗样式 */
.spots-dialog :deep(.el-dialog__body) { padding: 20px; }
.available-spots-list { max-height: 400px; overflow-y: auto; }
.spots-header { display: grid; grid-template-columns: 1.5fr 1fr 1.5fr 0.8fr; padding: 8px 12px; background: #f8fafc; border-radius: 8px; font-size: 12px; font-weight: 600; color: #1e293b; margin-bottom: 8px; }
.spot-item { display: grid; grid-template-columns: 1.5fr 1fr 1.5fr 0.8fr; align-items: center; padding: 10px 12px; border-bottom: 1px solid #e4e7ed; font-size: 13px; }
.spot-item:hover { background: #f5f7fa; }
.spot-number { font-family: monospace; font-weight: 600; color: #1e293b; }
.no-spots { text-align: center; padding: 40px; color: #94a3b8; }

.spot-dialog :deep(.el-dialog__body) { padding: 20px; }
.spot-detail-content { display: flex; flex-direction: column; gap: 16px; }
.spot-status-large { font-size: 16px; font-weight: 700; text-align: center; padding: 12px; border-radius: 12px; }
.spot-status-large.available { background: rgba(16,185,129,0.2); color: #34d399; }
.spot-status-large.occupied { background: rgba(239,68,68,0.2); color: #f87171; }
.spot-status-large.ev { background: rgba(59,130,246,0.2); color: #60a5fa; }
.info-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(0,0,0,0.05); }
.info-label { font-weight: 600; color: #64748b; font-size: 12px; }
.info-value { color: #1e293b; font-weight: 500; font-size: 12px; }
.charging-info, .charging-warning { padding: 12px; border-radius: 8px; text-align: center; }
.charging-info { background: rgba(59,130,246,0.1); color: #3b82f6; }
.charging-warning { background: rgba(245,158,11,0.1); color: #f59e0b; }

/* 滚动条 */
.left-panel::-webkit-scrollbar, .right-panel::-webkit-scrollbar, .dynamic-content::-webkit-scrollbar, .records-list::-webkit-scrollbar, .ev-chargers-list::-webkit-scrollbar { width: 4px; }
.left-panel::-webkit-scrollbar-track, .right-panel::-webkit-scrollbar-track { background: rgba(59,130,246,0.1); border-radius: 4px; }
.left-panel::-webkit-scrollbar-thumb, .right-panel::-webkit-scrollbar-thumb { background: rgba(59,130,246,0.3); border-radius: 4px; }

/* 移动端 */
@media (max-width: 768px) {
  .parking-page { flex-direction: column; overflow-y: auto; }
  .left-panel { width: 100%; border-right: none; border-bottom: 1px dashed rgba(59,130,246,0.3); }
  .right-panel { width: 100%; }
  .gate-buttons { flex-direction: column; gap: 12px; }
  .zone-buttons { flex-wrap: wrap; }
  .zone-stats-grid { grid-template-columns: repeat(2, 1fr); }
  .ev-stats-summary { grid-template-columns: repeat(2, 1fr); }
  .today-stats { grid-template-columns: repeat(2, 1fr); }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .trend-indicators { grid-template-columns: 1fr; gap: 8px; }
  .spots-header, .spot-item { grid-template-columns: 1fr 0.8fr 1fr 0.6fr; font-size: 10px; }
  .record-item { flex-wrap: wrap; }
  .record-direction { width: 60px; font-size: 9px; }
}
</style>