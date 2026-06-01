<template>
  <!-- Loading Screen -->
  <div v-if="!isLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">
          <span class="loading-title">Loading</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Occupancy Mapping</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="occupancy-mapping">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Occupancy Mapping</h2>
        <p class="subtitle">Track and visualize space occupancy, utilization, and real-time usage patterns</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="refreshData">
          <el-icon><RefreshRight /></el-icon> Refresh
        </el-button>
        <el-button @click="exportReport">
          <el-icon><Download /></el-icon> Export Report
        </el-button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-info">
          <div class="stat-value">{{ totalOccupancy }}%</div>
          <div class="stat-label">Total Occupancy</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🏢</div>
        <div class="stat-info">
          <div class="stat-value">{{ occupiedSpaces }}</div>
          <div class="stat-label">Occupied Spaces</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🟢</div>
        <div class="stat-info">
          <div class="stat-value">{{ availableSpaces }}</div>
          <div class="stat-label">Available Spaces</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-info">
          <div class="stat-value">{{ peakHour }}</div>
          <div class="stat-label">Peak Hour</div>
        </div>
      </div>
    </div>

    <!-- Building Selector -->
    <div class="building-selector">
      <el-radio-group v-model="selectedBuilding" @change="onBuildingChange">
        <el-radio-button label="all">All Buildings</el-radio-button>
        <el-radio-button v-for="building in buildings" :key="building.id" :label="building.id">
          {{ building.name }}
        </el-radio-button>
      </el-radio-group>
    </div>

    <!-- Floor Tabs -->
    <div class="floor-tabs" v-if="selectedBuilding !== 'all' && currentBuildingFloors.length > 0">
      <el-tabs v-model="selectedFloor" @tab-click="onFloorChange">
        <el-tab-pane v-for="floor in currentBuildingFloors" :key="floor.id" :label="`Floor ${floor.level}`" :name="String(floor.id)" />
      </el-tabs>
    </div>

    <!-- Heatmap / Occupancy Grid -->
    <div class="occupancy-heatmap">
      <div class="heatmap-header">
        <div class="heatmap-title">
          <span>📍 Occupancy Heatmap</span>
          <el-tag type="info" size="small">
            {{ selectedBuilding === 'all' ? 'All Buildings' : selectedBuildingName }}
            {{ selectedFloor !== 'all' ? `- Floor ${currentFloorLevel}` : '' }}
          </el-tag>
        </div>
        <div class="heatmap-legend">
          <div class="legend-item"><span class="legend-color low"></span> Low (0-30%)</div>
          <div class="legend-item"><span class="legend-color medium"></span> Medium (31-60%)</div>
          <div class="legend-item"><span class="legend-color high"></span> High (61-85%)</div>
          <div class="legend-item"><span class="legend-color critical"></span> Critical (86-100%)</div>
        </div>
      </div>
      <div class="heatmap-grid">
        <div v-for="space in displayedSpaces" :key="space.id" class="heatmap-cell" :class="getOccupancyClass(space.occupancy)">
          <div class="cell-room">{{ space.roomNumber }}</div>
          <div class="cell-name">{{ space.name || space.typeLabel }}</div>
          <div class="cell-occupancy">{{ space.occupancy }}%</div>
          <div class="cell-people" v-if="space.currentPeople > 0">
            <el-icon><User /></el-icon> {{ space.currentPeople }}
          </div>
          <div class="cell-status" :class="getStatusClass(space.status)">
            {{ getStatusText(space.status) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Real-time Occupancy Chart -->
    <div class="charts-row">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Occupancy Trend (24 Hours)</span>
            <el-tag type="info" size="small">Real-time Data</el-tag>
          </div>
        </template>
        <div ref="trendChartRef" class="chart"></div>
      </el-card>

      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Occupancy by Space Type</span>
            <el-tag type="success" size="small">Distribution</el-tag>
          </div>
        </template>
        <div ref="distributionChartRef" class="chart"></div>
      </el-card>
    </div>

    <!-- Space Details Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Space Occupancy Details</span>
          <el-input v-model="searchText" placeholder="Search by room number or name..." clearable style="width: 250px" :prefix-icon="Search" />
        </div>
      </template>
      <el-table :data="paginatedSpaces" stripe>
        <el-table-column prop="roomNumber" label="Room No." align="center" />
        <el-table-column prop="name" label="Room Name" align="center" />
        <el-table-column prop="buildingName" label="Building" align="center" />
        <el-table-column prop="floorLevel" label="Floor" align="center" />
        <el-table-column prop="typeLabel" label="Type" align="center" />
        <el-table-column label="Occupancy" align="center">
          <template #default="{ row }">
            <div class="occupancy-cell">
              <el-progress :percentage="row.occupancy" :stroke-width="8" :color="getOccupancyColor(row.occupancy)" :show-text="false" />
              <span class="occupancy-text">{{ row.occupancy }}%</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Current People" align="center">
          <template #default="{ row }">
            <span class="people-count">{{ row.currentPeople }}</span>
            <span class="people-max">/{{ row.capacity || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Status" align="center">
          <template #default="{ row }">
            <span :class="['status-badge', row.status]">{{ getStatusText(row.status) }}</span>
          </template>
        </el-table-column>
<!--        <el-table-column label="Last Updated" width="160" />-->
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredSpaces.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { RefreshRight, Download, Search, User } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Loading occupancy data...',
  'Fetching real-time sensor data...',
  'Generating heatmap...',
  'Almost ready...'
]

// Building data
const buildings = ref([
  { id: 1, name: 'Marina Bay Tower' },
  { id: 2, name: 'Central Plaza' },
  { id: 3, name: 'Tech Park North' }
])

// Floor data
const floors = ref([
  { id: 1, buildingId: 1, level: 1, code: 'L1' },
  { id: 2, buildingId: 1, level: 2, code: 'L2' },
  { id: 3, buildingId: 1, level: 3, code: 'L3' },
  { id: 4, buildingId: 2, level: 1, code: 'G' },
  { id: 5, buildingId: 2, level: 2, code: '2F' },
  { id: 6, buildingId: 3, level: 1, code: '01' },
  { id: 7, buildingId: 3, level: 2, code: '02' }
])

// Space occupancy data
const spaces = ref([
  { id: 1, roomNumber: '101', name: 'Executive Office', buildingId: 1, floorId: 1, type: 'office', occupancy: 85, currentPeople: 3, capacity: 4, status: 'occupied', lastUpdated: '2025-01-16 09:30:00' },
  { id: 2, roomNumber: '102', name: 'Conference Room A', buildingId: 1, floorId: 1, type: 'conference', occupancy: 45, currentPeople: 8, capacity: 20, status: 'occupied', lastUpdated: '2025-01-16 09:28:00' },
  { id: 3, roomNumber: '103', name: 'Break Room', buildingId: 1, floorId: 1, type: 'break', occupancy: 32, currentPeople: 4, capacity: 12, status: 'occupied', lastUpdated: '2025-01-16 09:25:00' },
  { id: 4, roomNumber: '201', name: 'Open Office', buildingId: 1, floorId: 2, type: 'office', occupancy: 78, currentPeople: 22, capacity: 28, status: 'occupied', lastUpdated: '2025-01-16 09:32:00' },
  { id: 5, roomNumber: '202', name: 'Server Room', buildingId: 1, floorId: 2, type: 'technical', occupancy: 0, currentPeople: 0, capacity: 0, status: 'maintenance', lastUpdated: '2025-01-16 08:00:00' },
  { id: 6, roomNumber: '203', name: 'Small Meeting', buildingId: 1, floorId: 2, type: 'meeting', occupancy: 90, currentPeople: 5, capacity: 6, status: 'occupied', lastUpdated: '2025-01-16 09:35:00' },
  { id: 7, roomNumber: '301', name: 'Training Room', buildingId: 1, floorId: 3, type: 'conference', occupancy: 25, currentPeople: 8, capacity: 30, status: 'occupied', lastUpdated: '2025-01-16 09:20:00' },
  { id: 8, roomNumber: 'G-01', name: 'Main Lobby', buildingId: 2, floorId: 4, type: 'lobby', occupancy: 65, currentPeople: 35, capacity: 50, status: 'occupied', lastUpdated: '2025-01-16 09:30:00' },
  { id: 9, roomNumber: 'G-02', name: 'Retail Space', buildingId: 2, floorId: 4, type: 'retail', occupancy: 55, currentPeople: 12, capacity: 25, status: 'occupied', lastUpdated: '2025-01-16 09:28:00' },
  { id: 10, roomNumber: '2F-01', name: 'Office Suite', buildingId: 2, floorId: 5, type: 'office', occupancy: 92, currentPeople: 14, capacity: 15, status: 'occupied', lastUpdated: '2025-01-16 09:33:00' },
  { id: 11, roomNumber: '101', name: 'Production Line', buildingId: 3, floorId: 6, type: 'production', occupancy: 95, currentPeople: 28, capacity: 30, status: 'occupied', lastUpdated: '2025-01-16 09:31:00' },
  { id: 12, roomNumber: '102', name: 'Storage', buildingId: 3, floorId: 6, type: 'storage', occupancy: 15, currentPeople: 0, capacity: 0, status: 'available', lastUpdated: '2025-01-16 08:00:00' },
  { id: 13, roomNumber: '201', name: 'R&D Lab', buildingId: 3, floorId: 7, type: 'office', occupancy: 68, currentPeople: 9, capacity: 14, status: 'occupied', lastUpdated: '2025-01-16 09:29:00' },
  { id: 14, roomNumber: '202', name: 'Testing Lab', buildingId: 3, floorId: 7, type: 'technical', occupancy: 45, currentPeople: 5, capacity: 12, status: 'occupied', lastUpdated: '2025-01-16 09:27:00' }
])

// UI State
const selectedBuilding = ref('all')
const selectedFloor = ref('all')
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const trendChartRef = ref<HTMLElement | null>(null)
const distributionChartRef = ref<HTMLElement | null>(null)
let trendChart: echarts.ECharts | null = null
let distributionChart: echarts.ECharts | null = null

// Occupancy trend data (24 hours)
const occupancyTrend = ref([
  { hour: '00:00', occupancy: 12 },
  { hour: '02:00', occupancy: 8 },
  { hour: '04:00', occupancy: 5 },
  { hour: '06:00', occupancy: 15 },
  { hour: '08:00', occupancy: 45 },
  { hour: '10:00', occupancy: 68 },
  { hour: '12:00', occupancy: 72 },
  { hour: '14:00', occupancy: 78 },
  { hour: '16:00', occupancy: 75 },
  { hour: '18:00', occupancy: 58 },
  { hour: '20:00', occupancy: 32 },
  { hour: '22:00', occupancy: 18 }
])

// Occupancy by space type
const occupancyByType = ref([
  { type: 'Office', occupancy: 78, spaces: 6 },
  { type: 'Meeting/Conference', occupancy: 65, spaces: 4 },
  { type: 'Technical', occupancy: 22, spaces: 3 },
  { type: 'Amenity/Break', occupancy: 32, spaces: 1 },
  { type: 'Lobby/Retail', occupancy: 60, spaces: 2 }
])

// Computed
const totalOccupancy = computed(() => {
  const total = spaces.value.reduce((sum, s) => sum + s.occupancy, 0)
  return Math.round(total / spaces.value.length)
})

const occupiedSpaces = computed(() => spaces.value.filter(s => s.status === 'occupied').length)
const availableSpaces = computed(() => spaces.value.filter(s => s.status === 'available').length)
const peakHour = computed(() => {
  const peak = [...occupancyTrend.value].sort((a, b) => b.occupancy - a.occupancy)[0]
  return peak.hour
})

const selectedBuildingName = computed(() => {
  if (selectedBuilding.value === 'all') return 'All Buildings'
  const building = buildings.value.find(b => b.id === selectedBuilding.value)
  return building?.name || ''
})

const currentBuildingFloors = computed(() => {
  if (selectedBuilding.value === 'all') return []
  return floors.value.filter(f => f.buildingId === selectedBuilding.value)
})

const currentFloorLevel = computed(() => {
  if (selectedFloor.value === 'all') return ''
  const floor = floors.value.find(f => f.id === parseInt(selectedFloor.value))
  return floor?.level || ''
})

const displayedSpaces = computed(() => {
  let filtered = [...spaces.value]

  if (selectedBuilding.value !== 'all') {
    filtered = filtered.filter(s => s.buildingId === selectedBuilding.value)
  }

  if (selectedFloor.value !== 'all') {
    filtered = filtered.filter(s => s.floorId === parseInt(selectedFloor.value))
  }

  return filtered
})

const allSpacesWithLabels = computed(() => {
  return spaces.value.map(s => ({
    ...s,
    buildingName: buildings.value.find(b => b.id === s.buildingId)?.name || '',
    floorLevel: floors.value.find(f => f.id === s.floorId)?.level || '',
    typeLabel: getTypeLabel(s.type)
  }))
})

const filteredSpaces = computed(() => {
  let filtered = [...allSpacesWithLabels.value]

  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    filtered = filtered.filter(s =>
        s.roomNumber.toLowerCase().includes(keyword) ||
        (s.name && s.name.toLowerCase().includes(keyword))
    )
  }

  if (selectedBuilding.value !== 'all') {
    filtered = filtered.filter(s => s.buildingId === selectedBuilding.value)
  }

  if (selectedFloor.value !== 'all') {
    filtered = filtered.filter(s => s.floorId === parseInt(selectedFloor.value))
  }

  return filtered
})

const paginatedSpaces = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredSpaces.value.slice(start, start + pageSize.value)
})

// Helper functions
const getTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    office: 'Office',
    meeting: 'Meeting',
    conference: 'Conference',
    break: 'Break Room',
    technical: 'Technical',
    storage: 'Storage',
    lobby: 'Lobby',
    retail: 'Retail',
    production: 'Production'
  }
  return map[type] || type
}

const getOccupancyClass = (occupancy: number) => {
  if (occupancy >= 86) return 'critical'
  if (occupancy >= 61) return 'high'
  if (occupancy >= 31) return 'medium'
  return 'low'
}

const getOccupancyColor = (occupancy: number) => {
  if (occupancy >= 86) return '#f56c6c'
  if (occupancy >= 61) return '#e6a23c'
  if (occupancy >= 31) return '#409eff'
  return '#67c23a'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    occupied: 'Occupied',
    available: 'Available',
    maintenance: 'Maintenance'
  }
  return map[status] || status
}

const getStatusClass = (status: string) => {
  return status
}

// Chart initialization
const initTrendChart = () => {
  if (trendChartRef.value) {
    if (trendChart) trendChart.dispose()
    trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: occupancyTrend.value.map(d => d.hour), axisLabel: { rotate: 45 } },
      yAxis: { type: 'value', name: 'Occupancy (%)', min: 0, max: 100 },
      series: [{
        type: 'line',
        data: occupancyTrend.value.map(d => d.occupancy),
        smooth: true,
        lineStyle: { color: '#409eff', width: 3 },
        areaStyle: { opacity: 0.3, color: '#409eff' },
        symbol: 'circle',
        symbolSize: 6,
        label: { show: true, position: 'top', formatter: '{c}%' }
      }]
    })
  }
}

const initDistributionChart = () => {
  if (distributionChartRef.value) {
    if (distributionChart) distributionChart.dispose()
    distributionChart = echarts.init(distributionChartRef.value)
    distributionChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      xAxis: { type: 'category', data: occupancyByType.value.map(t => t.type), axisLabel: { rotate: 30 } },
      yAxis: { type: 'value', name: 'Occupancy (%)', min: 0, max: 100 },
      series: [{
        type: 'bar',
        data: occupancyByType.value.map(t => t.occupancy),
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
          color: (params: any) => {
            const val = params.value
            if (val >= 70) return '#f56c6c'
            if (val >= 50) return '#e6a23c'
            return '#67c23a'
          }
        },
        label: { show: true, position: 'top', formatter: '{c}%' }
      }]
    })
  }
}

const handleResize = () => {
  trendChart?.resize()
  distributionChart?.resize()
}

// Methods
const onBuildingChange = () => {
  selectedFloor.value = 'all'
}

const onFloorChange = () => {}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
}

const refreshData = () => {
  ElMessage.success('Data refreshed')
  // Simulate real-time data update
  spaces.value.forEach(space => {
    const variation = (Math.random() - 0.5) * 10
    let newOccupancy = Math.min(100, Math.max(0, space.occupancy + variation))
    space.occupancy = Math.round(newOccupancy)
    if (space.capacity > 0) {
      space.currentPeople = Math.min(space.capacity, Math.round(space.occupancy * space.capacity / 100))
    }
    space.lastUpdated = new Date().toLocaleString()
  })
  ElMessage.success('Real-time data updated')
}

const exportReport = () => {
  const data = JSON.stringify(filteredSpaces.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `occupancy_report_${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Export completed')
}

// Simulate real-time updates
let intervalId: any = null

const startRealTimeUpdates = () => {
  intervalId = setInterval(() => {
    spaces.value.forEach(space => {
      const variation = (Math.random() - 0.5) * 8
      let newOccupancy = Math.min(100, Math.max(0, space.occupancy + variation))
      space.occupancy = Math.round(newOccupancy)
      if (space.capacity > 0) {
        space.currentPeople = Math.min(space.capacity, Math.round(space.occupancy * space.capacity / 100))
      }
      space.lastUpdated = new Date().toLocaleString()
      space.status = space.occupancy > 10 ? 'occupied' : (space.occupancy > 0 ? 'occupied' : 'available')
    })
  }, 30000)
}

// Loading animation
onMounted(() => {
  let messageIndex = 0
  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 400)

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => {
        initTrendChart()
        initDistributionChart()
        window.addEventListener('resize', handleResize)
        startRealTimeUpdates()
      })
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId)
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  distributionChart?.dispose()
})
</script>

<style scoped>
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

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-bottom: 24px;
  font-size: 28px;
  font-weight: 700;
  color: #e2e8f0;
  display: flex;
  justify-content: center;
  align-items: baseline;
  gap: 4px;
}

.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
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

.loading-tip { font-size: 13px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 8px; font-weight: 500; }
.loading-subtip { font-size: 11px; color: #64748b; letter-spacing: 0.5px; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

/* Main Content */
.occupancy-mapping {
  padding: 24px;
  background: linear-gradient(135deg, #f0f5ff 0%, #e8f0fe 100%);
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h2 {
  margin: 0 0 4px 0;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #1565c0, #1976d2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  margin: 0;
  color: #1565c0;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 36px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

/* Building Selector */
.building-selector {
  background: white;
  border-radius: 20px;
  padding: 12px 20px;
  margin-bottom: 20px;
}

/* Floor Tabs */
.floor-tabs {
  background: white;
  border-radius: 20px;
  padding: 0 20px;
  margin-bottom: 20px;
}

.floor-tabs :deep(.el-tabs__header) {
  margin-bottom: 0;
}

/* Heatmap */
.occupancy-heatmap {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
}

.heatmap-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.heatmap-title {
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 12px;
}

.heatmap-legend {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.legend-color.low { background: #67c23a; }
.legend-color.medium { background: #409eff; }
.legend-color.high { background: #e6a23c; }
.legend-color.critical { background: #f56c6c; }

.heatmap-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.heatmap-cell {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 12px;
  text-align: center;
  transition: all 0.2s ease;
  border-left: 4px solid;
}

.heatmap-cell.low { border-left-color: #67c23a; }
.heatmap-cell.medium { border-left-color: #409eff; }
.heatmap-cell.high { border-left-color: #e6a23c; }
.heatmap-cell.critical { border-left-color: #f56c6c; }

.heatmap-cell:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.cell-room {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.cell-name {
  font-size: 11px;
  color: #909399;
  margin-bottom: 8px;
}

.cell-occupancy {
  font-size: 20px;
  font-weight: 700;
  margin: 8px 0;
}

.cell-people {
  font-size: 12px;
  color: #606266;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.cell-status {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 12px;
  display: inline-block;
  margin-top: 8px;
}

.cell-status.occupied { background: #e6f7ff; color: #409eff; }
.cell-status.available { background: #e8f5e9; color: #67c23a; }
.cell-status.maintenance { background: #ffefef; color: #f56c6c; }

/* Charts */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  border-radius: 20px;
}

.chart-card :deep(.el-card__body) {
  padding: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.chart {
  width: 100%;
  height: 320px;
}

/* Table */
.table-card {
  border-radius: 20px;
}

.table-card :deep(.el-card__body) {
  padding: 0;
}

.occupancy-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
}

.occupancy-text {
  font-size: 12px;
  font-weight: 500;
  min-width: 40px;
}

.people-count {
  font-weight: 600;
  color: #303133;
}

.people-max {
  color: #909399;
  font-size: 12px;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
}

.status-badge.occupied { background: #e6f7ff; color: #409eff; }
.status-badge.available { background: #e8f5e9; color: #67c23a; }
.status-badge.maintenance { background: #ffefef; color: #f56c6c; }

.pagination-wrapper {
  padding: 16px 20px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
}

/* Responsive */
@media (max-width: 768px) {
  .occupancy-mapping { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .charts-row { grid-template-columns: 1fr; }
  .heatmap-grid { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); }
  .heatmap-header { flex-direction: column; align-items: flex-start; }
  .heatmap-legend { flex-wrap: wrap; }
}
</style>