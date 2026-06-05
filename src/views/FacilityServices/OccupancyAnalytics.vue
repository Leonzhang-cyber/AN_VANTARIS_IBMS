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
          <span class="loading-title">Occupancy Analytics</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Space Utilization Intelligence Platform</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="occupancy-analytics-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <div class="title-icon">
            <el-icon><User /></el-icon>
          </div>
          Occupancy Analytics
        </h1>
        <div class="page-subtitle">Real-time space utilization and occupancy intelligence</div>
      </div>
      <div class="header-right">
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 260px"
        />
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
        <el-button type="primary" @click="exportReport">
          <el-icon><Download /></el-icon> Export Report
        </el-button>
      </div>
    </div>

    <!-- Stats Cards with Animation -->
    <div class="stats-grid">
      <div class="stat-card" v-for="(stat, idx) in statsCards" :key="idx">
        <div class="stat-icon" :class="stat.iconClass">
          <el-icon><component :is="stat.icon" /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">
            <span class="counter">{{ animatedStats[idx] }}</span>
            <span class="unit">{{ stat.unit }}</span>
          </div>
          <div class="stat-label">{{ stat.label }}</div>
          <div class="stat-trend" :class="stat.trendClass">
            <el-icon><Top v-if="stat.trend === 'up'" /><Bottom v-else-if="stat.trend === 'down'" /><Right v-else /></el-icon>
            {{ stat.trendText }}
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row 1 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot"></span>
            Occupancy Trend
          </div>
          <div class="chart-actions">
            <el-radio-group v-model="trendView" size="small">
              <el-radio-button label="hourly">Hourly</el-radio-button>
              <el-radio-button label="daily">Daily</el-radio-button>
              <el-radio-button label="weekly">Weekly</el-radio-button>
            </el-radio-group>
            <span class="live-badge">● LIVE</span>
          </div>
        </div>
        <div class="chart-container" ref="trendChartRef"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot orange"></span>
            Occupancy by Area
          </div>
          <span class="update-badge">Auto-refresh</span>
        </div>
        <div class="chart-container" ref="areaChartRef"></div>
      </div>
    </div>

    <!-- Charts Row 2 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot green"></span>
            Space Utilization
          </div>
        </div>
        <div class="chart-container" ref="utilizationChartRef"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot purple"></span>
            Peak Hours Analysis
          </div>
        </div>
        <div class="chart-container" ref="peakChartRef"></div>
      </div>
    </div>

    <!-- Real-time Occupancy Map -->
    <div class="map-card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><Location /></el-icon>
          Real-time Occupancy Map
          <span class="live-indicator"></span>
        </div>
        <div class="legend">
          <span><span class="legend-dot high"></span> High (>80%)</span>
          <span><span class="legend-dot medium"></span> Medium (40-80%)</span>
          <span><span class="legend-dot low"></span> Low (<40%)</span>
        </div>
      </div>
      <div class="occupancy-map">
        <div class="floor-tabs">
          <button
              v-for="floor in floors"
              :key="floor.id"
              class="floor-btn"
              :class="{ active: selectedFloor === floor.id }"
              @click="selectedFloor = floor.id"
          >
            <el-icon><OfficeBuilding /></el-icon>
            {{ floor.name }}
          </button>
        </div>
        <div class="rooms-grid">
          <div
              v-for="room in currentFloorRooms"
              :key="room.id"
              class="room-card"
              :class="room.status"
              @click="showRoomDetail(room)"
          >
            <div class="room-name">{{ room.name }}</div>
            <div class="room-occupancy">{{ room.current }} / {{ room.capacity }}</div>
            <div class="room-percent">{{ Math.round((room.current / room.capacity) * 100) }}%</div>
            <div class="room-bar">
              <div class="bar-fill" :style="{ width: (room.current / room.capacity) * 100 + '%' }"></div>
            </div>
            <div class="room-trend" v-if="room.trend">
              <el-icon><Top v-if="room.trend === 'up'" /><Bottom v-else-if="room.trend === 'down'" /><Right v-else /></el-icon>
            </div>
          </div>
        </div>
      </div>
      <div class="map-footer">
        <div class="total-occupancy">
          <span>Total Occupancy: </span>
          <strong>{{ currentFloorTotalOccupancy }} / {{ currentFloorTotalCapacity }}</strong>
          <span class="percentage">({{ currentFloorOccupancyRate }}%)</span>
        </div>
        <el-button size="small" @click="simulateOccupancyUpdate">Simulate Update</el-button>
      </div>
    </div>

    <!-- Occupancy Details Table -->
    <div class="data-table-container">
      <div class="table-header">
        <span class="table-title">Occupancy Details by Zone</span>
        <div class="table-actions">
          <el-input
              v-model="searchText"
              placeholder="Search by zone or area..."
              style="width: 220px"
              clearable
              :prefix-icon="Search"
              size="small"
          />
          <el-button size="small" @click="exportTableData">
            <el-icon><Download /></el-icon> Export
          </el-button>
        </div>
      </div>
      <el-table :data="filteredZones" stripe border v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="zone" label="Zone / Area" />
        <el-table-column prop="capacity" label="Capacity" />
        <el-table-column prop="current" label="Current Occupancy">
          <template #default="{ row }">
            <span :class="getOccupancyClass(row.current, row.capacity)">{{ row.current }} / {{ row.capacity }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="occupancyRate" label="Occupancy Rate">
          <template #default="{ row }">
            <el-progress
                :percentage="row.occupancyRate"
                :stroke-width="8"
                :color="getRateColor(row.occupancyRate)"
                :show-text="true"
            />
          </template>
        </el-table-column>
        <el-table-column prop="peakHour" label="Peak Hour" />
        <el-table-column prop="peakOccupancy" label="Peak Occupancy" />
        <el-table-column prop="avgStayTime" label="Avg Stay Time">
          <template #default="{ row }">{{ row.avgStayTime }} min</template>
        </el-table-column>
        <el-table-column prop="trend" label="Trend">
          <template #default="{ row }">
            <div class="trend-indicator" :class="row.trend">
              <el-icon><Top v-if="row.trend === 'up'" /><Bottom v-else-if="row.trend === 'down'" /><Right v-else /></el-icon>
              {{ row.trend === 'up' ? 'Increasing' : (row.trend === 'down' ? 'Decreasing' : 'Stable') }}
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Alert">
          <template #default="{ row }">
            <el-tag v-if="row.occupancyRate >= 85" type="danger" size="small">High</el-tag>
            <el-tag v-else-if="row.occupancyRate <= 20" type="info" size="small">Low</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  User, DataLine, OfficeBuilding, Calendar, Download, Refresh,
  Location, Search, Top, Bottom, Right
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Initializing occupancy sensors...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Initializing occupancy sensors...',
  'Loading real-time data streams...',
  'Analyzing space utilization...',
  'Processing IoT sensors...',
  'Almost ready...'
]

// ==================== State ====================
const dateRange = ref<string[]>([getLastWeekDate(), getTodayDate()])
const trendView = ref('hourly')
const searchText = ref('')
const selectedFloor = ref(1)
let refreshInterval: NodeJS.Timeout

// Chart refs
const trendChartRef = ref<HTMLElement | null>(null)
const areaChartRef = ref<HTMLElement | null>(null)
const utilizationChartRef = ref<HTMLElement | null>(null)
const peakChartRef = ref<HTMLElement | null>(null)

let trendChart: echarts.ECharts | null = null
let areaChart: echarts.ECharts | null = null
let utilizationChart: echarts.ECharts | null = null
let peakChart: echarts.ECharts | null = null

// Animated stats
const animatedStats = ref([0, 0, 0, 0])

const statsCards = ref([
  { label: 'Current Occupancy', value: 0, unit: 'people', icon: 'User', iconClass: 'blue', trend: 'up', trendText: '+8.5% vs yesterday', trendClass: 'up' },
  { label: 'Avg Occupancy Rate', value: 0, unit: '%', icon: 'DataLine', iconClass: 'green', trend: 'up', trendText: '+3.2% vs last week', trendClass: 'up' },
  { label: 'Peak Occupancy', value: 0, unit: 'people', icon: 'OfficeBuilding', iconClass: 'orange', trend: 'up', trendText: '+12% vs yesterday', trendClass: 'up' },
  { label: 'Total Visits', value: 0, unit: 'visits', icon: 'Calendar', iconClass: 'purple', trend: 'up', trendText: '+15.3% vs last week', trendClass: 'up' }
])

// Floors data
const floors = [
  { id: 1, name: '1st Floor' },
  { id: 2, name: '2nd Floor' },
  { id: 3, name: '3rd Floor' },
  { id: 4, name: '4th Floor' }
]

const floorRooms = ref({
  1: [
    { id: 1, name: 'Lobby', capacity: 50, current: 32, trend: 'up', status: 'medium' },
    { id: 2, name: 'Reception', capacity: 10, current: 4, trend: 'stable', status: 'low' },
    { id: 3, name: 'Conference Room A', capacity: 20, current: 18, trend: 'up', status: 'high' },
    { id: 4, name: 'Conference Room B', capacity: 20, current: 8, trend: 'down', status: 'low' },
    { id: 5, name: 'Open Office North', capacity: 80, current: 65, trend: 'up', status: 'high' },
    { id: 6, name: 'Open Office South', capacity: 80, current: 42, trend: 'stable', status: 'medium' },
    { id: 7, name: 'Break Room', capacity: 30, current: 12, trend: 'down', status: 'low' },
    { id: 8, name: 'Meeting Room 1', capacity: 12, current: 10, trend: 'up', status: 'high' },
    { id: 9, name: 'Meeting Room 2', capacity: 12, current: 6, trend: 'stable', status: 'medium' }
  ],
  2: [
    { id: 10, name: 'Open Office East', capacity: 100, current: 78, trend: 'up', status: 'high' },
    { id: 11, name: 'Open Office West', capacity: 100, current: 55, trend: 'down', status: 'medium' },
    { id: 12, name: 'Executive Offices', capacity: 15, current: 12, trend: 'stable', status: 'high' },
    { id: 13, name: 'Training Room', capacity: 40, current: 25, trend: 'stable', status: 'medium' },
    { id: 14, name: 'IT Server Room', capacity: 5, current: 2, trend: 'stable', status: 'low' },
    { id: 15, name: 'Storage Room', capacity: 10, current: 3, trend: 'down', status: 'low' },
    { id: 16, name: 'Phone Booth 1', capacity: 2, current: 1, trend: 'stable', status: 'low' },
    { id: 17, name: 'Phone Booth 2', capacity: 2, current: 2, trend: 'up', status: 'high' }
  ],
  3: [
    { id: 18, name: 'Data Center', capacity: 20, current: 8, trend: 'stable', status: 'low' },
    { id: 19, name: 'Network Operations', capacity: 15, current: 12, trend: 'up', status: 'high' },
    { id: 20, name: 'Engineering Lab', capacity: 30, current: 22, trend: 'stable', status: 'medium' },
    { id: 21, name: 'R&D Office', capacity: 60, current: 45, trend: 'up', status: 'medium' },
    { id: 22, name: 'QA Lab', capacity: 25, current: 18, trend: 'stable', status: 'medium' },
    { id: 23, name: 'Equipment Room', capacity: 10, current: 4, trend: 'down', status: 'low' }
  ],
  4: [
    { id: 24, name: 'Cafeteria', capacity: 120, current: 45, trend: 'stable', status: 'low' },
    { id: 25, name: 'Gym', capacity: 30, current: 12, trend: 'up', status: 'low' },
    { id: 26, name: 'Lounge Area', capacity: 40, current: 22, trend: 'stable', status: 'medium' },
    { id: 27, name: 'Outdoor Terrace', capacity: 50, current: 18, trend: 'down', status: 'low' },
    { id: 28, name: 'Showers & Lockers', capacity: 20, current: 6, trend: 'stable', status: 'low' },
    { id: 29, name: 'Nursing Room', capacity: 5, current: 1, trend: 'stable', status: 'low' },
    { id: 30, name: 'Prayer Room', capacity: 10, current: 3, trend: 'stable', status: 'low' }
  ]
})

// Zones data
const zones = ref([
  { zone: 'Lobby & Reception', capacity: 60, current: 36, occupancyRate: 60, peakHour: '09:00-10:00', peakOccupancy: 42, avgStayTime: 5, trend: 'stable' },
  { zone: 'Open Office - North', capacity: 80, current: 65, occupancyRate: 81, peakHour: '14:00-15:00', peakOccupancy: 72, avgStayTime: 180, trend: 'up' },
  { zone: 'Open Office - South', capacity: 80, current: 42, occupancyRate: 53, peakHour: '11:00-12:00', peakOccupancy: 58, avgStayTime: 165, trend: 'stable' },
  { zone: 'Open Office - East', capacity: 100, current: 78, occupancyRate: 78, peakHour: '15:00-16:00', peakOccupancy: 85, avgStayTime: 190, trend: 'up' },
  { zone: 'Open Office - West', capacity: 100, current: 55, occupancyRate: 55, peakHour: '13:00-14:00', peakOccupancy: 62, avgStayTime: 175, trend: 'down' },
  { zone: 'Conference Rooms', capacity: 64, current: 42, occupancyRate: 66, peakHour: '10:00-11:00', peakOccupancy: 48, avgStayTime: 60, trend: 'up' },
  { zone: 'Meeting Rooms', capacity: 24, current: 16, occupancyRate: 67, peakHour: '11:00-12:00', peakOccupancy: 20, avgStayTime: 45, trend: 'stable' },
  { zone: 'Executive Offices', capacity: 15, current: 12, occupancyRate: 80, peakHour: '10:00-11:00', peakOccupancy: 14, avgStayTime: 240, trend: 'stable' },
  { zone: 'Training Room', capacity: 40, current: 25, occupancyRate: 63, peakHour: '14:00-15:00', peakOccupancy: 35, avgStayTime: 120, trend: 'down' },
  { zone: 'IT & Engineering', capacity: 45, current: 34, occupancyRate: 76, peakHour: '13:00-14:00', peakOccupancy: 38, avgStayTime: 210, trend: 'up' },
  { zone: 'Data Center', capacity: 20, current: 8, occupancyRate: 40, peakHour: '10:00-11:00', peakOccupancy: 12, avgStayTime: 30, trend: 'stable' },
  { zone: 'Cafeteria', capacity: 120, current: 45, occupancyRate: 38, peakHour: '12:00-13:00', peakOccupancy: 85, avgStayTime: 25, trend: 'stable' },
  { zone: 'Break Room & Lounge', capacity: 70, current: 34, occupancyRate: 49, peakHour: '11:00-12:00', peakOccupancy: 48, avgStayTime: 20, trend: 'down' },
  { zone: 'Wellness Area', capacity: 50, current: 18, occupancyRate: 36, peakHour: '17:00-18:00', peakOccupancy: 25, avgStayTime: 45, trend: 'up' }
])

// ==================== Computed ====================
const currentFloorRooms = computed(() => {
  return floorRooms.value[selectedFloor.value as keyof typeof floorRooms.value] || []
})

const currentFloorTotalOccupancy = computed(() => {
  return currentFloorRooms.value.reduce((sum, r) => sum + r.current, 0)
})

const currentFloorTotalCapacity = computed(() => {
  return currentFloorRooms.value.reduce((sum, r) => sum + r.capacity, 0)
})

const currentFloorOccupancyRate = computed(() => {
  if (currentFloorTotalCapacity.value === 0) return 0
  return Math.round((currentFloorTotalOccupancy.value / currentFloorTotalCapacity.value) * 100)
})

const filteredZones = computed(() => {
  if (!searchText.value) return zones.value
  const search = searchText.value.toLowerCase()
  return zones.value.filter(z => z.zone.toLowerCase().includes(search))
})

// ==================== Helper Functions ====================
function getTodayDate(): string {
  return new Date().toISOString().slice(0, 10)
}

function getLastWeekDate(): string {
  const date = new Date()
  date.setDate(date.getDate() - 7)
  return date.toISOString().slice(0, 10)
}

function getOccupancyClass(current: number, capacity: number): string {
  const rate = (current / capacity) * 100
  if (rate >= 80) return 'occupancy-high'
  if (rate >= 40) return 'occupancy-medium'
  return 'occupancy-low'
}

function getRateColor(rate: number): string {
  if (rate >= 80) return '#ef4444'
  if (rate >= 40) return '#f59e0b'
  return '#22c55e'
}

function showRoomDetail(room: any) {
  ElMessage.info(`${room.name}: ${room.current}/${room.capacity} people (${Math.round((room.current / room.capacity) * 100)}%)`)
}

// ==================== Data Fetching Simulation ====================
const fetchStatsData = async () => {
  await new Promise(resolve => setTimeout(resolve, 300))

  const totalOccupancy = zones.value.reduce((sum, z) => sum + z.current, 0)
  const totalCapacity = zones.value.reduce((sum, z) => sum + z.capacity, 0)
  const avgRate = Math.round((totalOccupancy / totalCapacity) * 100)
  const peakOccupancy = 85
  const totalVisits = 2847

  statsCards.value[0].value = totalOccupancy
  statsCards.value[1].value = avgRate
  statsCards.value[2].value = peakOccupancy
  statsCards.value[3].value = totalVisits

  animateCounters()
}

const animateCounters = () => {
  statsCards.value.forEach((card, idx) => {
    const target = card.value
    let current = 0
    const step = Math.ceil(target / 30)
    const interval = setInterval(() => {
      current += step
      if (current >= target) {
        current = target
        clearInterval(interval)
      }
      animatedStats.value[idx] = current
    }, 20)
  })
}

const simulateOccupancyUpdate = () => {
  const floorsCopy = { ...floorRooms.value }
  Object.keys(floorsCopy).forEach(floorKey => {
    const floor = floorsCopy[Number(floorKey) as keyof typeof floorsCopy]
    floor.forEach(room => {
      const change = Math.floor(Math.random() * 10) - 5
      let newCurrent = room.current + change
      newCurrent = Math.max(0, Math.min(newCurrent, room.capacity))
      room.current = newCurrent

      if (change > 3) room.trend = 'up'
      else if (change < -3) room.trend = 'down'
      else room.trend = 'stable'

      const rate = (room.current / room.capacity) * 100
      if (rate >= 80) room.status = 'high'
      else if (rate >= 40) room.status = 'medium'
      else room.status = 'low'
    })
  })
  floorRooms.value = floorsCopy
  updateZonesFromRooms()
  refreshCharts()
  ElMessage.success('Occupancy data updated')
}

const updateZonesFromRooms = () => {
  zones.value = zones.value.map(zone => {
    const change = Math.floor(Math.random() * 10) - 5
    let newCurrent = zone.current + change
    newCurrent = Math.max(0, Math.min(newCurrent, zone.capacity))
    return {
      ...zone,
      current: newCurrent,
      occupancyRate: Math.round((newCurrent / zone.capacity) * 100)
    }
  })
}

// ==================== Charts ====================
const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  const hourlyData = {
    xAxis: ['06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00'],
    series: [12, 18, 45, 85, 120, 145, 135, 155, 175, 190, 185, 165, 125, 85, 45]
  }

  const dailyData = {
    xAxis: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    series: [165, 180, 175, 190, 185, 95, 45]
  }

  const weeklyData = {
    xAxis: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    series: [1250, 1320, 1280, 1350]
  }

  let data
  if (trendView.value === 'hourly') data = hourlyData
  else if (trendView.value === 'daily') data = dailyData
  else data = weeklyData

  trendChart = echarts.init(trendChartRef.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis', formatter: '{b}<br/>Occupancy: {c} people' },
    grid: { top: 30, left: 50, right: 30, bottom: 30, containLabel: true },
    xAxis: { type: 'category', data: data.xAxis, axisLabel: { rotate: trendView.value === 'hourly' ? 45 : 0, interval: 0 } },
    yAxis: { type: 'value', name: 'Occupancy (people)' },
    series: [{
      type: 'line',
      data: data.series,
      smooth: true,
      lineStyle: { color: '#3b82f6', width: 3 },
      areaStyle: { opacity: 0.1, color: '#3b82f6' },
      symbol: 'circle',
      symbolSize: 8,
      markPoint: { data: [{ type: 'max', name: 'Peak' }] }
    }]
  })
  window.addEventListener('resize', () => trendChart?.resize())
}

const initAreaChart = () => {
  if (!areaChartRef.value) return
  if (areaChart) areaChart.dispose()

  const categories = ['Open Office', 'Conference Rooms', 'Cafeteria', 'Meeting Rooms', 'Executive', 'IT/Engineering', 'Training Room', 'Lobby']
  const values = [255, 42, 45, 16, 12, 34, 25, 36]

  areaChart = echarts.init(areaChartRef.value)
  areaChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}<br/>Occupancy: {c} people' },
    grid: { top: 30, left: 80, right: 30, bottom: 30, containLabel: true },
    xAxis: { type: 'value', name: 'Occupancy (people)' },
    yAxis: { type: 'category', data: categories, axisLabel: { fontSize: 11 } },
    series: [{
      type: 'bar',
      data: values,
      itemStyle: {
        borderRadius: [0, 4, 4, 0],
        color: (params: any) => {
          const colors = ['#3b82f6', '#22c55e', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4', '#ec489a', '#84cc16']
          return colors[params.dataIndex]
        }
      },
      label: { show: true, position: 'right', formatter: '{c}' }
    }]
  })
  window.addEventListener('resize', () => areaChart?.resize())
}

const initUtilizationChart = () => {
  if (!utilizationChartRef.value) return
  if (utilizationChart) utilizationChart.dispose()

  const roomData = currentFloorRooms.value
  const highCount = roomData.filter(r => (r.current / r.capacity) * 100 >= 80).length
  const mediumCount = roomData.filter(r => {
    const rate = (r.current / r.capacity) * 100
    return rate >= 40 && rate < 80
  }).length
  const lowCount = roomData.filter(r => (r.current / r.capacity) * 100 < 40).length

  utilizationChart = echarts.init(utilizationChartRef.value)
  utilizationChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} rooms ({d}%)' },
    legend: { orient: 'vertical', left: 'left', textStyle: { color: '#475569' } },
    series: [{
      type: 'pie',
      radius: ['45%', '65%'],
      center: ['50%', '50%'],
      data: [
        { value: highCount, name: 'High Utilization (>80%)', itemStyle: { color: '#ef4444' } },
        { value: mediumCount, name: 'Medium Utilization (40-80%)', itemStyle: { color: '#f59e0b' } },
        { value: lowCount, name: 'Low Utilization (<40%)', itemStyle: { color: '#22c55e' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
  window.addEventListener('resize', () => utilizationChart?.resize())
}

const initPeakChart = () => {
  if (!peakChartRef.value) return
  if (peakChart) peakChart.dispose()

  peakChart = echarts.init(peakChartRef.value)
  peakChart.setOption({
    tooltip: { trigger: 'axis', formatter: '{b}<br/>Avg Occupancy: {c} people' },
    grid: { top: 30, left: 50, right: 30, bottom: 30 },
    xAxis: { type: 'category', data: ['06-08', '08-10', '10-12', '12-14', '14-16', '16-18', '18-20'], axisLabel: { interval: 0 } },
    yAxis: { type: 'value', name: 'Average Occupancy' },
    series: [{
      type: 'bar',
      data: [25, 85, 160, 175, 190, 165, 95],
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const colors = ['#94a3b8', '#f59e0b', '#3b82f6', '#22c55e', '#ef4444', '#8b5cf6', '#64748b']
          return colors[params.dataIndex]
        }
      },
      label: { show: true, position: 'top', formatter: '{c}' }
    }]
  })
  window.addEventListener('resize', () => peakChart?.resize())
}

const refreshCharts = () => {
  nextTick(() => {
    initTrendChart()
    initAreaChart()
    initUtilizationChart()
    initPeakChart()
  })
}

// ==================== Export Functions ====================
const exportReport = () => {
  ElMessage.success('Export started')
  setTimeout(() => {
    ElMessage.success('Occupancy report exported')
  }, 1500)
}

const exportTableData = () => {
  ElMessage.success('Table data exported')
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  await fetchStatsData()
  simulateOccupancyUpdate()
  tableLoading.value = false
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

// ==================== Watch for chart updates ====================
watch(trendView, () => {
  nextTick(() => initTrendChart())
})

watch(selectedFloor, () => {
  nextTick(() => initUtilizationChart())
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

  setTimeout(async () => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    await fetchStatsData()

    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => {
        initTrendChart()
        initAreaChart()
        initUtilizationChart()
        initPeakChart()
      })
    }, 500)
  }, 2200)
}

// ==================== Auto Refresh ====================
const startAutoRefresh = () => {
  refreshInterval = setInterval(() => {
    simulateOccupancyUpdate()
  }, 30000)
}

// ==================== Lifecycle ====================
onMounted(() => {
  startLoading()
  startAutoRefresh()
})

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval)
  if (trendChart) trendChart.dispose()
  if (areaChart) areaChart.dispose()
  if (utilizationChart) utilizationChart.dispose()
  if (peakChart) peakChart.dispose()
})
</script>

<style scoped>
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

/* ==================== Loading Screen ==================== */
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
  font-size: 28px;
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

/* ==================== Main Page ==================== */
.occupancy-analytics-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 24px;
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

.header-left {
  flex: 1;
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

.title-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
}

.header-right {
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
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
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
.stat-icon.purple { background: #f3e8ff; color: #8b5cf6; }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

.stat-value .unit {
  font-size: 12px;
  font-weight: normal;
  color: #64748b;
  margin-left: 2px;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

.stat-trend {
  font-size: 11px;
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 2px;
}

.stat-trend.up { color: #22c55e; }
.stat-trend.down { color: #ef4444; }

/* Charts Row */
.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.title-dot {
  width: 8px;
  height: 8px;
  background: #3b82f6;
  border-radius: 50%;
}

.title-dot.orange { background: #f59e0b; }
.title-dot.green { background: #22c55e; }
.title-dot.purple { background: #8b5cf6; }

.chart-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.live-badge {
  font-size: 10px;
  font-weight: 600;
  color: #22c55e;
  background: #dcfce7;
  padding: 2px 8px;
  border-radius: 20px;
}

.update-badge {
  font-size: 10px;
  color: #64748b;
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 20px;
}

.chart-container {
  height: 300px;
  width: 100%;
}

/* Map Card */
.map-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.live-indicator {
  width: 8px;
  height: 8px;
  background: #22c55e;
  border-radius: 50%;
  animation: livePulse 1.5s infinite;
}

@keyframes livePulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

.legend {
  display: flex;
  gap: 16px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 6px;
}

.legend-dot.high { background: #ef4444; box-shadow: 0 0 0 2px #fee2e2; }
.legend-dot.medium { background: #f59e0b; box-shadow: 0 0 0 2px #fef3c7; }
.legend-dot.low { background: #22c55e; box-shadow: 0 0 0 2px #dcfce7; }

.occupancy-map {
  border-radius: 16px;
  background: #f8fafc;
  padding: 20px;
}

.floor-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.floor-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  border: none;
  background: #f1f5f9;
  border-radius: 30px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.floor-btn:hover {
  background: #e2e8f0;
}

.floor-btn.active {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: white;
}

.rooms-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.room-card {
  background: white;
  border-radius: 12px;
  padding: 12px;
  text-align: center;
  border-left: 4px solid;
  transition: all 0.2s;
  position: relative;
  cursor: pointer;
}

.room-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.room-card.high { border-left-color: #ef4444; background: #fef2f2; }
.room-card.medium { border-left-color: #f59e0b; background: #fffbeb; }
.room-card.low { border-left-color: #22c55e; background: #f0fdf4; }

.room-name {
  font-weight: 600;
  font-size: 13px;
  color: #1e293b;
  margin-bottom: 6px;
}

.room-occupancy {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.room-percent {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 8px;
}

.room-card.high .room-percent { color: #ef4444; }
.room-card.medium .room-percent { color: #f59e0b; }
.room-card.low .room-percent { color: #22c55e; }

.room-bar {
  height: 4px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s;
}

.room-card.high .bar-fill { background: #ef4444; }
.room-card.medium .bar-fill { background: #f59e0b; }
.room-card.low .bar-fill { background: #22c55e; }

.room-trend {
  position: absolute;
  top: 8px;
  right: 8px;
  font-size: 10px;
}

.room-trend .el-icon { font-size: 12px; }
.room-card.high .room-trend { color: #ef4444; }
.room-card.medium .room-trend { color: #f59e0b; }
.room-card.low .room-trend { color: #22c55e; }

.map-footer {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #eef2f8;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.total-occupancy {
  font-size: 14px;
  color: #64748b;
}

.total-occupancy strong {
  font-size: 18px;
  color: #1e293b;
}

.total-occupancy .percentage {
  color: #3b82f6;
  font-weight: 500;
}

/* Data Table */
.data-table-container {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.table-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.table-actions {
  display: flex;
  gap: 12px;
}

.occupancy-high { color: #ef4444; font-weight: 600; }
.occupancy-medium { color: #f59e0b; font-weight: 600; }
.occupancy-low { color: #22c55e; font-weight: 600; }

.trend-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.trend-indicator.up { color: #ef4444; }
.trend-indicator.down { color: #22c55e; }
.trend-indicator.stable { color: #3b82f6; }

/* Responsive */
@media (max-width: 1000px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-row {
    grid-template-columns: 1fr;
  }

  .rooms-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .rooms-grid {
    grid-template-columns: 1fr;
  }

  .legend {
    flex-wrap: wrap;
  }

  .map-footer {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
}
</style>