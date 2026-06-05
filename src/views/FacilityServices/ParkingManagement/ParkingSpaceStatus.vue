<template>
  <!-- Loading Screen -->
  <div v-if="!isLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">
          <span class="loading-title">Parking Space Status</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Real-time Parking Space Monitoring</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="parking-space-status-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Place /></el-icon>
          Parking Space Status
        </h1>
        <div class="page-subtitle">Real-time monitoring of parking space availability and occupancy</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="exportData">
          <el-icon><Download /></el-icon> Export Report
        </el-button>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><Place /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalSpots }}</div>
          <div class="stat-label">Total Spots</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.availableSpots }}</div>
          <div class="stat-label">Available</div>
          <div class="stat-trend up">↑ {{ stats.availablePercent }}% of total</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Loading /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.occupiedSpots }}</div>
          <div class="stat-label">Occupied</div>
          <div class="stat-trend up">Occupancy: {{ stats.occupancyRate }}%</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.reservedSpots }}</div>
          <div class="stat-label">Reserved</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Peak Hour Occupancy</div>
        <div class="metric-value">{{ metrics.peakOccupancy }}<span class="stat-unit">%</span></div>
        <div class="metric-sub">{{ metrics.peakTime }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">EV Charging Spots</div>
        <div class="metric-value">{{ metrics.evAvailable }}/{{ metrics.evTotal }}</div>
        <el-progress :percentage="metrics.evUsage" :stroke-width="8" :color="metrics.evUsage > 80 ? '#ef4444' : (metrics.evUsage > 50 ? '#f59e0b' : '#22c55e')" />
      </div>
      <div class="metric-card">
        <div class="metric-title">Disabled Spots</div>
        <div class="metric-value">{{ metrics.disabledAvailable }}/{{ metrics.disabledTotal }}</div>
        <div class="metric-sub">{{ metrics.disabledAvailable }} available</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Turnover Rate</div>
        <div class="metric-value">{{ metrics.turnoverRate }}<span class="stat-unit">/day</span></div>
        <div class="metric-trend positive">↑ {{ metrics.turnoverGrowth }}%</div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by spot ID or vehicle..."
            style="width: 200px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="zoneFilter" placeholder="Zone" clearable style="width: 120px">
          <el-option v-for="z in zones" :key="z" :label="z" :value="z" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
          <el-option label="Available" value="available" />
          <el-option label="Occupied" value="occupied" />
          <el-option label="Reserved" value="reserved" />
          <el-option label="EV Charging" value="ev" />
          <el-option label="Disabled" value="disabled" />
        </el-select>
        <el-select v-model="spotTypeFilter" placeholder="Spot Type" clearable style="width: 130px">
          <el-option label="Regular" value="regular" />
          <el-option label="EV Charging" value="ev" />
          <el-option label="Disabled" value="disabled" />
          <el-option label="Reserved" value="reserved" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Parking Map Grid -->
    <div class="parking-map">
      <div class="map-legend">
        <span><span class="legend-box available"></span> Available</span>
        <span><span class="legend-box occupied"></span> Occupied</span>
        <span><span class="legend-box reserved"></span> Reserved</span>
        <span><span class="legend-box ev"></span> EV Charging</span>
        <span><span class="legend-box disabled"></span> Disabled</span>
      </div>

      <div class="zone-sections">
        <div v-for="zone in uniqueZones" :key="zone" class="zone-section">
          <div class="zone-title">{{ zone }}</div>
          <div class="zone-grid">
            <div
                v-for="spot in getSpotsByZone(zone)"
                :key="spot.id"
                class="parking-spot"
                :class="spot.status"
                @click="showSpotDetail(spot)"
            >
              <div class="spot-number">{{ spot.number }}</div>
              <div class="spot-status-icon" v-if="spot.status === 'ev'">⚡</div>
              <div class="spot-status-icon" v-if="spot.status === 'disabled'">♿</div>
              <div class="spot-status-icon" v-if="spot.status === 'reserved'">🔒</div>
              <div class="spot-status-icon" v-if="spot.status === 'occupied'">🚗</div>
              <div class="spot-status-icon" v-if="spot.status === 'available'">✅</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Parking Spots Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Parking Spots Details</span>
        <el-button size="small" @click="viewAllSpots">View All →</el-button>
      </div>
      <el-table :data="paginatedSpots" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="number" label="Spot Number" width="110" />
        <el-table-column prop="zone" label="Zone" width="100" />
        <el-table-column prop="status" label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="Type" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.type)" size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="currentVehicle" label="Current Vehicle" min-width="140">
          <template #default="{ row }">
            <span v-if="row.currentVehicle">{{ row.currentVehicle }}</span>
            <span v-else class="empty-text">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="parkedSince" label="Parked Since" width="150">
          <template #default="{ row }">
            <span v-if="row.parkedSince">{{ row.parkedSince }}</span>
            <span v-else class="empty-text">—</span>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="Duration" width="100">
          <template #default="{ row }">
            <span v-if="row.duration">{{ row.duration }}</span>
            <span v-else class="empty-text">—</span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="showSpotDetail(row)">Details</el-button>
            <el-button link type="success" size="small" v-if="row.status === 'occupied'" @click="releaseSpot(row)">Release</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[15, 30, 50]"
            :total="totalRecords"
            layout="total, sizes, prev, pager, next"
            background
        />
      </div>
    </div>

    <!-- Spot Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Parking Spot ${selectedSpot?.number}`" width="550px">
      <div v-if="selectedSpot" class="spot-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Spot ID">{{ selectedSpot.id }}</el-descriptions-item>
          <el-descriptions-item label="Spot Number">{{ selectedSpot.number }}</el-descriptions-item>
          <el-descriptions-item label="Zone">{{ selectedSpot.zone }}</el-descriptions-item>
          <el-descriptions-item label="Type">
            <el-tag :type="getTypeTagType(selectedSpot.type)" size="small">{{ selectedSpot.type }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(selectedSpot.status)" size="small">{{ getStatusLabel(selectedSpot.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Current Vehicle" v-if="selectedSpot.currentVehicle">{{ selectedSpot.currentVehicle }}</el-descriptions-item>
          <el-descriptions-item label="Parked Since" v-if="selectedSpot.parkedSince">{{ selectedSpot.parkedSince }}</el-descriptions-item>
          <el-descriptions-item label="Duration" v-if="selectedSpot.duration">{{ selectedSpot.duration }}</el-descriptions-item>
          <el-descriptions-item label="Sensor Status" :span="2">
            <el-tag :type="selectedSpot.sensorStatus === 'Online' ? 'success' : 'danger'" size="small">
              {{ selectedSpot.sensorStatus }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-section" v-if="selectedSpot.status === 'occupied'">
          <div class="section-title">Release Options</div>
          <el-button type="primary" @click="releaseSpot(selectedSpot)">Release Spot</el-button>
          <el-button @click="sendReminder(selectedSpot)">Send Reminder to Driver</el-button>
        </div>

        <div class="detail-section" v-if="selectedSpot.status === 'reserved'">
          <div class="section-title">Reservation Details</div>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="Reserved For">{{ selectedSpot.reservedFor || 'VIP Guest' }}</el-descriptions-item>
            <el-descriptions-item label="Reserved Until">{{ selectedSpot.reservedUntil || 'Today 18:00' }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button v-if="selectedSpot?.status === 'occupied'" type="primary" @click="releaseSpot(selectedSpot)">Release Spot</el-button>
      </template>
    </el-dialog>

    <!-- Release Confirmation -->
    <el-dialog v-model="releaseDialogVisible" title="Release Parking Spot" width="400px">
      <div class="release-confirm">
        <p>Are you sure you want to release spot <strong>{{ releaseSpotData?.number }}</strong>?</p>
        <p class="release-info">Vehicle: {{ releaseSpotData?.currentVehicle }}</p>
        <p class="release-info">Parked since: {{ releaseSpotData?.parkedSince }}</p>
      </div>
      <template #footer>
        <el-button @click="releaseDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmRelease">Confirm Release</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Place, CircleCheck, Loading, Warning, Download, Refresh,
  Search, RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading parking space data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading parking space data...',
  'Fetching occupancy status...',
  'Loading sensor data...',
  'Almost ready...'
]

// ==================== Types ====================
interface ParkingSpot {
  id: string
  number: string
  zone: string
  status: 'available' | 'occupied' | 'reserved' | 'ev' | 'disabled'
  type: string
  currentVehicle?: string
  parkedSince?: string
  duration?: string
  sensorStatus: string
  reservedFor?: string
  reservedUntil?: string
}

// ==================== Mock Data ====================
const zones = ['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E']

const generateParkingSpots = (): ParkingSpot[] => {
  const spots: ParkingSpot[] = []
  let spotCounter = 1

  for (const zone of zones) {
    const zoneLetter = zone.charAt(zone.length - 1)
    for (let i = 1; i <= 20; i++) {
      const spotNumber = `${zoneLetter}${String(i).padStart(2, '0')}`

      // Determine status based on position
      let status: ParkingSpot['status'] = 'available'
      let type = 'Regular'
      let currentVehicle: string | undefined
      let parkedSince: string | undefined
      let duration: string | undefined

      // EV spots at positions 1-3 in each zone
      if (i <= 3) {
        type = 'EV Charging'
        status = Math.random() > 0.4 ? 'ev' : (Math.random() > 0.6 ? 'occupied' : 'available')
        if (status === 'ev') status = 'ev'
        else if (status === 'occupied') {
          status = 'occupied'
          currentVehicle = `SGD${Math.floor(Math.random() * 9000 + 1000)}`
          const hoursAgo = Math.floor(Math.random() * 3) + 1
          parkedSince = `${hoursAgo} hour${hoursAgo > 1 ? 's' : ''} ago`
          duration = `${hoursAgo}h ${Math.floor(Math.random() * 60)}m`
        }
      }
      // Disabled spots at positions 4-5
      else if (i <= 5) {
        type = 'Disabled'
        status = 'disabled'
      }
      // Reserved spots at positions 18-20
      else if (i >= 18) {
        type = 'Reserved'
        status = Math.random() > 0.5 ? 'reserved' : 'available'
      }
      // Regular spots
      else {
        type = 'Regular'
        const random = Math.random()
        if (random < 0.55) status = 'available'
        else {
          status = 'occupied'
          currentVehicle = `SGD${Math.floor(Math.random() * 9000 + 1000)}`
          const hoursAgo = Math.floor(Math.random() * 4) + 1
          parkedSince = `${hoursAgo} hour${hoursAgo > 1 ? 's' : ''} ago`
          duration = `${hoursAgo}h ${Math.floor(Math.random() * 60)}m`
        }
      }

      spots.push({
        id: `SPOT-${String(spotCounter).padStart(4, '0')}`,
        number: spotNumber,
        zone: zone,
        status: status,
        type: type,
        currentVehicle: currentVehicle,
        parkedSince: parkedSince,
        duration: duration,
        sensorStatus: Math.random() > 0.05 ? 'Online' : 'Offline',
        reservedFor: status === 'reserved' ? 'VIP Guest' : undefined,
        reservedUntil: status === 'reserved' ? 'Today 18:00' : undefined
      })
      spotCounter++
    }
  }
  return spots
}

const parkingSpots = ref<ParkingSpot[]>(generateParkingSpots())

// ==================== State ====================
const searchText = ref('')
const zoneFilter = ref('')
const statusFilter = ref('')
const spotTypeFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(15)
const detailDialogVisible = ref(false)
const releaseDialogVisible = ref(false)
const selectedSpot = ref<ParkingSpot | null>(null)
const releaseSpotData = ref<ParkingSpot | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  const totalSpots = parkingSpots.value.length
  const availableSpots = parkingSpots.value.filter(s => s.status === 'available').length
  const occupiedSpots = parkingSpots.value.filter(s => s.status === 'occupied').length
  const reservedSpots = parkingSpots.value.filter(s => s.status === 'reserved').length
  const availablePercent = Math.round((availableSpots / totalSpots) * 100)
  const occupancyRate = Math.round((occupiedSpots / totalSpots) * 100)

  return { totalSpots, availableSpots, occupiedSpots, reservedSpots, availablePercent, occupancyRate }
})

const metrics = computed(() => {
  const peakOccupancy = 92
  const peakTime = '10:30 - 11:30'
  const evSpots = parkingSpots.value.filter(s => s.type === 'EV Charging')
  const evTotal = evSpots.length
  const evOccupied = evSpots.filter(s => s.status === 'occupied').length
  const evAvailable = evTotal - evOccupied
  const evUsage = Math.round((evOccupied / evTotal) * 100)

  const disabledSpots = parkingSpots.value.filter(s => s.type === 'Disabled')
  const disabledTotal = disabledSpots.length
  const disabledOccupied = disabledSpots.filter(s => s.status === 'occupied').length
  const disabledAvailable = disabledTotal - disabledOccupied

  const turnoverRate = 3.2
  const turnoverGrowth = 8

  return {
    peakOccupancy,
    peakTime,
    evTotal,
    evAvailable,
    evUsage,
    disabledTotal,
    disabledAvailable,
    turnoverRate,
    turnoverGrowth
  }
})

const uniqueZones = computed(() => {
  return [...new Set(parkingSpots.value.map(s => s.zone))]
})

const getSpotsByZone = (zone: string) => {
  let spots = parkingSpots.value.filter(s => s.zone === zone)

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    spots = spots.filter(s =>
        s.number.toLowerCase().includes(search) ||
        (s.currentVehicle && s.currentVehicle.toLowerCase().includes(search))
    )
  }

  if (statusFilter.value) {
    spots = spots.filter(s => s.status === statusFilter.value)
  }

  if (spotTypeFilter.value) {
    spots = spots.filter(s => s.type.toLowerCase() === spotTypeFilter.value.toLowerCase())
  }

  return spots
}

const filteredSpots = computed(() => {
  let filtered = [...parkingSpots.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(s =>
        s.number.toLowerCase().includes(search) ||
        (s.currentVehicle && s.currentVehicle.toLowerCase().includes(search))
    )
  }

  if (zoneFilter.value) {
    filtered = filtered.filter(s => s.zone === zoneFilter.value)
  }

  if (statusFilter.value) {
    filtered = filtered.filter(s => s.status === statusFilter.value)
  }

  if (spotTypeFilter.value) {
    filtered = filtered.filter(s => s.type.toLowerCase() === spotTypeFilter.value.toLowerCase())
  }

  return filtered
})

const totalRecords = computed(() => filteredSpots.value.length)

const paginatedSpots = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredSpots.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getStatusLabel = (status: string): string => {
  const map: Record<string, string> = {
    available: 'Available', occupied: 'Occupied', reserved: 'Reserved',
    ev: 'EV Charging', disabled: 'Disabled'
  }
  return map[status] || status
}

const getStatusTagType = (status: string): string => {
  const map: Record<string, string> = {
    available: 'success', occupied: 'danger', reserved: 'warning',
    ev: 'primary', disabled: 'info'
  }
  return map[status] || 'info'
}

const getTypeTagType = (type: string): string => {
  const map: Record<string, string> = {
    Regular: 'info', 'EV Charging': 'primary', Disabled: 'warning', Reserved: 'danger'
  }
  return map[type] || 'info'
}

const resetFilters = () => {
  searchText.value = ''
  zoneFilter.value = ''
  statusFilter.value = ''
  spotTypeFilter.value = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const showSpotDetail = (spot: ParkingSpot) => {
  selectedSpot.value = spot
  detailDialogVisible.value = true
}

const releaseSpot = (spot: ParkingSpot) => {
  releaseSpotData.value = spot
  releaseDialogVisible.value = true
}

const confirmRelease = () => {
  if (releaseSpotData.value) {
    const index = parkingSpots.value.findIndex(s => s.id === releaseSpotData.value!.id)
    if (index !== -1) {
      parkingSpots.value[index] = {
        ...parkingSpots.value[index],
        status: 'available',
        currentVehicle: undefined,
        parkedSince: undefined,
        duration: undefined
      }
      ElMessage.success(`Spot ${releaseSpotData.value.number} released successfully`)
    }
  }
  releaseDialogVisible.value = false
  detailDialogVisible.value = false
}

const sendReminder = (spot: ParkingSpot) => {
  ElMessage.success(`Reminder sent to vehicle ${spot.currentVehicle}`)
}

const viewAllSpots = () => {
  ElMessage.info('Viewing all parking spots')
}

const exportData = () => {
  ElMessage.success('Exporting parking space data...')
  setTimeout(() => {
    ElMessage.success('Data exported successfully')
  }, 1000)
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  tableLoading.value = false
  parkingSpots.value = generateParkingSpots()
  ElMessage.success('Data refreshed')
}

// ==================== Watch ====================
watch([searchText, zoneFilter, statusFilter, spotTypeFilter], () => {
  currentPage.value = 1
})

// ==================== Loading Animation ====================
const startLoading = () => {
  let progress = 0
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 12
      loadingProgress.value = Math.min(progress, 90)
    }
  }, 100)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(() => {
      isLoaded.value = true
    }, 500)
  }, 2200)
}

onMounted(() => {
  startLoading()
})
</script>

<style scoped>
.parking-space-status-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 24px;
}

* {
  scrollbar-width: thin;
}
*::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
*::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}
*::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

/* Loading Screen */
.loading-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: center;
}

.loading-overlay {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  backdrop-filter: blur(2px);
}

.loading-content {
  text-align: center;
  padding: 40px;
  border-radius: 32px;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(59, 130, 246, 0.3);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  animation: fadeInUp 0.6s ease-out;
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
  animation: spin 1.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
}

.spinner-ring:nth-child(1) { border-top-color: #3b82f6; animation-delay: 0s; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }
.spinner-ring:nth-child(4) { border-left-color: #ec489a; animation-delay: 0.6s; width: 20%; height: 20%; top: 40%; left: 40%; }

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-bottom: 24px;
  font-size: 24px;
  font-weight: 700;
  color: #e2e8f0;
  display: flex;
  justify-content: center;
  align-items: baseline;
  gap: 4px;
}

.loading-dots {
  display: inline-flex;
  gap: 2px;
}

.loading-dots span {
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
  40% { transform: scale(1); opacity: 1; }
}

.loading-progress {
  width: 280px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin: 0 auto 16px;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec489a);
  border-radius: 4px;
  transition: width 0.3s ease;
  background-size: 200% auto;
  animation: shimmer 2s linear infinite;
}

@keyframes shimmer {
  0% { background-position: 0% 0%; }
  100% { background-position: 200% 0%; }
}

.loading-tip {
  font-size: 13px;
  color: #94a3b8;
  letter-spacing: 1px;
  margin-bottom: 8px;
  font-weight: 500;
}

.loading-subtip {
  font-size: 11px;
  color: #64748b;
  letter-spacing: 0.5px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.blue { background: #eef2ff; color: #3b82f6; }
.stat-icon.green { background: #dcfce7; color: #22c55e; }
.stat-icon.orange { background: #fef3c7; color: #f59e0b; }
.stat-icon.red { background: #fee2e2; color: #ef4444; }

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
}

.stat-unit {
  font-size: 14px;
  font-weight: normal;
  color: #64748b;
  margin-left: 4px;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

.stat-trend {
  font-size: 11px;
  margin-top: 4px;
}

.stat-trend.up { color: #22c55e; }

/* Metrics Row */
.metrics-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.metric-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.metric-title {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.metric-unit {
  font-size: 14px;
  font-weight: normal;
  color: #64748b;
}

.metric-trend {
  font-size: 12px;
  margin: 8px 0 4px;
}

.metric-trend.positive { color: #22c55e; }

.metric-sub {
  font-size: 11px;
  color: #64748b;
  margin-top: 4px;
}

/* Filter Bar */
.filter-bar {
  background: white;
  border-radius: 16px;
  padding: 14px 20px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.filter-left {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Parking Map */
.parking-map {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.map-legend {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eef2f8;
  font-size: 13px;
  flex-wrap: wrap;
}

.legend-box {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 4px;
  margin-right: 6px;
  vertical-align: middle;
}

.legend-box.available { background: #dcfce7; border: 1px solid #22c55e; }
.legend-box.occupied { background: #fee2e2; border: 1px solid #ef4444; }
.legend-box.reserved { background: #fef3c7; border: 1px solid #f59e0b; }
.legend-box.ev { background: #eef2ff; border: 1px solid #3b82f6; }
.legend-box.disabled { background: #f3e8ff; border: 1px solid #8b5cf6; }

.zone-sections {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.zone-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 12px;
  padding-left: 8px;
  border-left: 3px solid #3b82f6;
}

.zone-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(70px, 85px));
  gap: 10px;
}

.parking-spot {
  aspect-ratio: 1;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.parking-spot:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.parking-spot.available { background: #dcfce7; border: 2px solid #22c55e; }
.parking-spot.occupied { background: #fee2e2; border: 2px solid #ef4444; }
.parking-spot.reserved { background: #fef3c7; border: 2px solid #f59e0b; }
.parking-spot.ev { background: #eef2ff; border: 2px solid #3b82f6; }
.parking-spot.disabled { background: #f3e8ff; border: 2px solid #8b5cf6; }

.spot-number {
  font-size: 12px;
  font-weight: 600;
}

.spot-status-icon {
  font-size: 18px;
  margin-top: 4px;
}

/* Table Container */
.table-container {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

/* Spot Detail */
.spot-detail {
  padding: 8px;
}

.detail-section {
  margin-top: 20px;
}

.section-title {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
  margin-bottom: 12px;
}

.empty-text {
  color: #94a3b8;
}

/* Release Confirm */
.release-confirm {
  text-align: center;
}

.release-info {
  color: #64748b;
  margin-top: 8px;
}

/* Responsive */
@media (max-width: 1000px) {
  .stats-grid, .metrics-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .zone-grid {
    grid-template-columns: repeat(auto-fill, minmax(60px, 70px));
  }
}

@media (max-width: 768px) {
  .stats-grid, .metrics-row {
    grid-template-columns: 1fr;
  }
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .filter-left {
    flex-direction: column;
    width: 100%;
  }
  .filter-left .el-input,
  .filter-left .el-select {
    width: 100% !important;
  }
  .zone-grid {
    grid-template-columns: repeat(auto-fill, minmax(55px, 60px));
  }
  .spot-number {
    font-size: 10px;
  }
  .spot-status-icon {
    font-size: 14px;
  }
  .map-legend {
    gap: 12px;
  }
}

/* Element Plus Overrides */
:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
}
:deep(.el-table th.el-table__cell) {
  background-color: #f8fafc !important;
  color: #334155;
}
:deep(.el-table .el-table__row:hover > td.el-table__cell) {
  background-color: #f0f7ff;
}
:deep(.el-button--primary) {
  background: #3b82f6;
  border-color: #3b82f6;
}
:deep(.el-button--primary:hover) {
  background: #2563eb;
}
:deep(.el-pagination.is-background .el-pager li.is-active) {
  background-color: #3b82f6;
}
:deep(.el-dialog__body) {
  padding: 20px;
}
:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}
</style>