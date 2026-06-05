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
          <span class="loading-title">ANPR Records</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Automatic Number Plate Recognition System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="anpr-records-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Camera /></el-icon>
          ANPR Records
        </h1>
        <div class="page-subtitle">Vehicle entry/exit tracking and license plate recognition</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="exportData">
          <el-icon><Download /></el-icon> Export Records
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
          <el-icon><View /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalRecords }}</div>
          <div class="stat-label">Total Records</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><Right /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.entriesToday }}</div>
          <div class="stat-label">Entries Today</div>
          <div class="stat-trend up">↑ {{ stats.entryGrowth }}% vs yesterday</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><ArrowLeft /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.exitsToday }}</div>
          <div class="stat-label">Exits Today</div>
          <div class="stat-trend down">↓ {{ stats.exitDecline }}% vs yesterday</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.uniqueVehicles }}</div>
          <div class="stat-label">Unique Vehicles</div>
        </div>
      </div>
    </div>

    <!-- Live Camera Feed Row -->
    <div class="camera-row">
      <div class="camera-card">
        <div class="camera-header">
          <span class="camera-title">Entry Gate Camera</span>
          <span class="camera-status online">● Live</span>
        </div>
        <div class="camera-feed">
          <div class="feed-placeholder">
            <el-icon><Camera /></el-icon>
            <span>Live Feed - Entry Gate</span>
            <div class="latest-detection" v-if="latestEntry">
              <el-tag type="success" size="large">{{ latestEntry.plateNumber }}</el-tag>
              <span class="detection-time">{{ latestEntry.time }}</span>
            </div>
          </div>
        </div>
      </div>
      <div class="camera-card">
        <div class="camera-header">
          <span class="camera-title">Exit Gate Camera</span>
          <span class="camera-status online">● Live</span>
        </div>
        <div class="camera-feed">
          <div class="feed-placeholder">
            <el-icon><Camera /></el-icon>
            <span>Live Feed - Exit Gate</span>
            <div class="latest-detection" v-if="latestExit">
              <el-tag type="warning" size="large">{{ latestExit.plateNumber }}</el-tag>
              <span class="detection-time">{{ latestExit.time }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Hourly Traffic Flow</span>
          <span class="chart-subtitle">Last 24 hours</span>
        </div>
        <div class="chart-container" ref="trafficChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Top Vehicle Types</span>
          <span class="chart-subtitle">Vehicle distribution</span>
        </div>
        <div class="chart-container" ref="vehicleTypeChartEl"></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by plate number..."
            style="width: 220px"
            clearable
            :prefix-icon="Search"
        />
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            size="default"
            style="width: 260px"
        />
        <el-select v-model="directionFilter" placeholder="Direction" clearable style="width: 120px">
          <el-option label="Entry" value="entry" />
          <el-option label="Exit" value="exit" />
        </el-select>
        <el-select v-model="gateFilter" placeholder="Gate" clearable style="width: 140px">
          <el-option label="Entry Gate A" value="Entry Gate A" />
          <el-option label="Entry Gate B" value="Entry Gate B" />
          <el-option label="Exit Gate A" value="Exit Gate A" />
          <el-option label="Exit Gate B" value="Exit Gate B" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- ANPR Records Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">ANPR Records</span>
        <el-button size="small" @click="viewAllRecords">View All →</el-button>
      </div>
      <el-table :data="paginatedRecords" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="plateNumber" label="Plate Number" min-width="140">
          <template #default="{ row }">
            <span class="plate-number">{{ row.plateNumber }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="vehicleType" label="Vehicle Type" width="120">
          <template #default="{ row }">
            <el-tag :type="getVehicleTypeTag(row.vehicleType)" size="small">{{ row.vehicleType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="direction" label="Direction" width="100">
          <template #default="{ row }">
            <el-tag :type="row.direction === 'entry' ? 'success' : 'warning'" size="small">
              {{ row.direction === 'entry' ? 'Entry' : 'Exit' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="gate" label="Gate" width="130" />
        <el-table-column prop="time" label="Time" width="160" />
        <el-table-column prop="confidence" label="Confidence" width="120">
          <template #default="{ row }">
            <el-progress :percentage="row.confidence" :stroke-width="6" :color="row.confidence > 90 ? '#22c55e' : (row.confidence > 75 ? '#f59e0b' : '#ef4444')" />
          </template>
        </el-table-column>
        <el-table-column prop="imageUrl" label="Snapshot" width="100">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewSnapshot(row)">View</el-button>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewRecordDetail(row)">Details</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="totalRecords"
            layout="total, sizes, prev, pager, next"
            background
        />
      </div>
    </div>

    <!-- Record Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`ANPR Record - ${selectedRecord?.plateNumber}`" width="700px">
      <div v-if="selectedRecord" class="record-detail">
        <div class="detail-image" v-if="selectedRecord.imageUrl">
          <div class="snapshot-placeholder">
            <el-icon><Camera /></el-icon>
            <span>Snapshot captured at {{ selectedRecord.time }}</span>
          </div>
        </div>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="Record ID">{{ selectedRecord.id }}</el-descriptions-item>
          <el-descriptions-item label="Plate Number">
            <span class="plate-number large">{{ selectedRecord.plateNumber }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="Vehicle Type">
            <el-tag :type="getVehicleTypeTag(selectedRecord.vehicleType)" size="small">{{ selectedRecord.vehicleType }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Direction">
            <el-tag :type="selectedRecord.direction === 'entry' ? 'success' : 'warning'" size="small">
              {{ selectedRecord.direction === 'entry' ? 'Entry' : 'Exit' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Gate">{{ selectedRecord.gate }}</el-descriptions-item>
          <el-descriptions-item label="Time">{{ selectedRecord.time }}</el-descriptions-item>
          <el-descriptions-item label="Confidence">{{ selectedRecord.confidence }}%</el-descriptions-item>
          <el-descriptions-item label="Processing Time">{{ selectedRecord.processingTime }}ms</el-descriptions-item>
          <el-descriptions-item label="Camera ID">{{ selectedRecord.cameraId }}</el-descriptions-item>
          <el-descriptions-item label="Lane Number">{{ selectedRecord.laneNumber }}</el-descriptions-item>
          <el-descriptions-item label="OCR Result" :span="2">{{ selectedRecord.ocrResult }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-section" v-if="selectedRecord.matchedVehicle">
          <div class="section-title">Matched Vehicle Information</div>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="Owner Name">{{ selectedRecord.matchedVehicle.ownerName }}</el-descriptions-item>
            <el-descriptions-item label="Vehicle Model">{{ selectedRecord.matchedVehicle.model }}</el-descriptions-item>
            <el-descriptions-item label="Color">{{ selectedRecord.matchedVehicle.color }}</el-descriptions-item>
            <el-descriptions-item label="Pass Type">{{ selectedRecord.matchedVehicle.passType }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="searchVehicle(selectedRecord)">Search Vehicle History</el-button>
        <el-button type="warning" @click="markAsReview(selectedRecord)">Mark for Review</el-button>
      </template>
    </el-dialog>

    <!-- Snapshot Dialog -->
    <el-dialog v-model="snapshotDialogVisible" title="Vehicle Snapshot" width="500px">
      <div class="snapshot-container">
        <div class="snapshot-placeholder large">
          <el-icon><Camera /></el-icon>
          <span>Snapshot Image</span>
          <div class="snapshot-info">
            <p>Plate: <strong>{{ snapshotPlate }}</strong></p>
            <p>Time: <strong>{{ snapshotTime }}</strong></p>
            <p>Gate: <strong>{{ snapshotGate }}</strong></p>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="snapshotDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="downloadSnapshot">Download</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Camera, Download, Refresh, View, Right, ArrowLeft, User,
  Search, RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading ANPR records...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading ANPR records...',
  'Fetching camera feeds...',
  'Processing plate data...',
  'Analyzing traffic patterns...',
  'Almost ready...'
]

// ==================== Types ====================
interface ANPRRecord {
  id: string
  plateNumber: string
  vehicleType: string
  direction: 'entry' | 'exit'
  gate: string
  time: string
  confidence: number
  imageUrl: string
  processingTime: number
  cameraId: string
  laneNumber: number
  ocrResult: string
  matchedVehicle?: {
    ownerName: string
    model: string
    color: string
    passType: string
  }
}

// ==================== Mock Data ====================
const generateANPRRecords = (): ANPRRecord[] => {
  const records: ANPRRecord[] = []
  const plates = ['SGD1234A', 'SGA5678B', 'SGB9012C', 'SGC3456D', 'SGD7890E', 'SGE2345F', 'SGF6789G', 'SGG0123H', 'SGH4567I', 'SGJ8901J']
  const vehicleTypes = ['Car', 'SUV', 'MPV', 'Van', 'Lorry', 'Motorcycle']
  const gates = ['Entry Gate A', 'Entry Gate B', 'Exit Gate A', 'Exit Gate B']
  const colors = ['White', 'Black', 'Silver', 'Blue', 'Red', 'Grey']
  const models = ['Toyota Camry', 'Honda Civic', 'BMW 3 Series', 'Mercedes C-Class', 'Audi A4', 'Tesla Model 3']

  for (let i = 0; i < 120; i++) {
    const date = new Date()
    date.setDate(date.getDate() - Math.floor(Math.random() * 7))
    date.setHours(Math.floor(Math.random() * 24), Math.floor(Math.random() * 60), Math.floor(Math.random() * 60))
    const timeStr = date.toISOString().replace('T', ' ').slice(0, 19)

    const direction = Math.random() > 0.5 ? 'entry' : 'exit'
    const plateNumber = plates[Math.floor(Math.random() * plates.length)] + (Math.random() > 0.7 ? Math.floor(Math.random() * 9) : '')
    const confidence = Math.floor(85 + Math.random() * 14)
    const vehicleType = vehicleTypes[Math.floor(Math.random() * vehicleTypes.length)]
    const gate = gates[Math.floor(Math.random() * gates.length)]

    records.push({
      id: `ANPR-${String(i + 1).padStart(6, '0')}`,
      plateNumber: plateNumber,
      vehicleType: vehicleType,
      direction: direction,
      gate: gate,
      time: timeStr,
      confidence: confidence,
      imageUrl: `snapshot_${i + 1}.jpg`,
      processingTime: Math.floor(80 + Math.random() * 120),
      cameraId: `CAM-${Math.floor(Math.random() * 8) + 1}`,
      laneNumber: Math.floor(Math.random() * 3) + 1,
      ocrResult: `OCR: ${plateNumber} (${confidence}% confidence)`,
      matchedVehicle: confidence > 90 ? {
        ownerName: ['Tan Ah Kow', 'Lim Bee Hua', 'Wong Wei Ming', 'Goh Siew Lee'][Math.floor(Math.random() * 4)],
        model: models[Math.floor(Math.random() * models.length)],
        color: colors[Math.floor(Math.random() * colors.length)],
        passType: ['Monthly Season', 'Corporate', 'VIP', 'Hourly'][Math.floor(Math.random() * 4)]
      } : undefined
    })
  }

  return records.sort((a, b) => b.time.localeCompare(a.time))
}

const anprRecords = ref<ANPRRecord[]>(generateANPRRecords())

// Get latest entry and exit
const latestEntry = computed(() => {
  return anprRecords.value.find(r => r.direction === 'entry')
})

const latestExit = computed(() => {
  return anprRecords.value.find(r => r.direction === 'exit')
})

// ==================== State ====================
const searchText = ref('')
const dateRange = ref<Date[] | null>(null)
const directionFilter = ref('')
const gateFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const snapshotDialogVisible = ref(false)
const selectedRecord = ref<ANPRRecord | null>(null)
const snapshotPlate = ref('')
const snapshotTime = ref('')
const snapshotGate = ref('')

// Chart refs
let trafficChart: echarts.ECharts | null = null
let vehicleTypeChart: echarts.ECharts | null = null

const trafficChartEl = ref<HTMLElement | null>(null)
const vehicleTypeChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  const totalRecords = anprRecords.value.length
  const today = new Date().toISOString().slice(0, 10)
  const todayRecords = anprRecords.value.filter(r => r.time.startsWith(today))
  const entriesToday = todayRecords.filter(r => r.direction === 'entry').length
  const exitsToday = todayRecords.filter(r => r.direction === 'exit').length
  const uniqueVehicles = new Set(anprRecords.value.map(r => r.plateNumber)).size

  return {
    totalRecords,
    entriesToday,
    exitsToday,
    entryGrowth: 8,
    exitDecline: 3,
    uniqueVehicles
  }
})

const filteredRecords = computed(() => {
  let filtered = [...anprRecords.value]

  if (searchText.value) {
    const search = searchText.value.toUpperCase()
    filtered = filtered.filter(r =>
        r.plateNumber.toUpperCase().includes(search)
    )
  }

  if (directionFilter.value) {
    filtered = filtered.filter(r => r.direction === directionFilter.value)
  }

  if (gateFilter.value) {
    filtered = filtered.filter(r => r.gate === gateFilter.value)
  }

  if (dateRange.value && dateRange.value.length === 2) {
    const [start, end] = dateRange.value
    filtered = filtered.filter(r => {
      const recordDate = new Date(r.time)
      return recordDate >= start && recordDate <= end
    })
  }

  return filtered
})

const totalRecords = computed(() => filteredRecords.value.length)

const paginatedRecords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRecords.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getVehicleTypeTag = (type: string): string => {
  const map: Record<string, string> = {
    Car: 'primary', SUV: 'success', MPV: 'warning', Van: 'info', Lorry: 'danger', Motorcycle: ''
  }
  return map[type] || 'info'
}

const resetFilters = () => {
  searchText.value = ''
  dateRange.value = null
  directionFilter.value = ''
  gateFilter.value = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const viewRecordDetail = (record: ANPRRecord) => {
  selectedRecord.value = record
  detailDialogVisible.value = true
}

const viewSnapshot = (record: ANPRRecord) => {
  snapshotPlate.value = record.plateNumber
  snapshotTime.value = record.time
  snapshotGate.value = record.gate
  snapshotDialogVisible.value = true
}

const searchVehicle = (record: ANPRRecord | null) => {
  if (record) {
    ElMessage.info(`Searching history for vehicle ${record.plateNumber}`)
  }
}

const markAsReview = (record: ANPRRecord | null) => {
  if (record) {
    ElMessage.success(`Record ${record.id} marked for review`)
  }
}

const downloadSnapshot = () => {
  ElMessage.success('Downloading snapshot...')
  setTimeout(() => {
    ElMessage.success('Snapshot downloaded')
  }, 1000)
}

const viewAllRecords = () => {
  ElMessage.info('Viewing all records')
}

const exportData = () => {
  ElMessage.success('Exporting ANPR records...')
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
  anprRecords.value = generateANPRRecords()
  refreshCharts()
  ElMessage.success('Data refreshed')
}

// ==================== Chart Functions ====================
const initTrafficChart = () => {
  if (!trafficChartEl.value) return
  if (trafficChart) {
    trafficChart.dispose()
    trafficChart = null
  }

  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const entries = [12, 8, 5, 3, 2, 5, 25, 65, 85, 72, 58, 45, 38, 35, 42, 55, 68, 75, 62, 48, 35, 28, 18, 10]
  const exits = [5, 3, 2, 2, 3, 8, 18, 35, 55, 68, 62, 55, 48, 42, 38, 45, 58, 72, 68, 55, 42, 32, 22, 15]

  trafficChart = echarts.init(trafficChartEl.value)
  trafficChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Entries', 'Exits'], bottom: 0 },
    grid: { top: 40, left: 60, right: 30, bottom: 40 },
    xAxis: { type: 'category', data: hours, axisLabel: { rotate: 45, interval: 3 } },
    yAxis: { type: 'value', name: 'Number of Vehicles' },
    series: [
      { name: 'Entries', type: 'line', data: entries, lineStyle: { color: '#22c55e', width: 2 }, symbol: 'circle', areaStyle: { opacity: 0.1 } },
      { name: 'Exits', type: 'line', data: exits, lineStyle: { color: '#ef4444', width: 2 }, symbol: 'circle', areaStyle: { opacity: 0.1 } }
    ]
  })
}

const initVehicleTypeChart = () => {
  if (!vehicleTypeChartEl.value) return
  if (vehicleTypeChart) {
    vehicleTypeChart.dispose()
    vehicleTypeChart = null
  }

  const typeCount = new Map<string, number>()
  anprRecords.value.forEach(r => {
    typeCount.set(r.vehicleType, (typeCount.get(r.vehicleType) || 0) + 1)
  })

  const data = Array.from(typeCount.entries()).map(([name, value]) => ({ name, value }))

  vehicleTypeChart = echarts.init(vehicleTypeChartEl.value)
  vehicleTypeChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} vehicles ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: data.map(d => d.name) },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: data,
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initTrafficChart()
    initVehicleTypeChart()
  })
}

// ==================== Watch ====================
watch([searchText, directionFilter, gateFilter, dateRange], () => {
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
      nextTick(() => refreshCharts())
    }, 500)
  }, 2200)
}

onMounted(() => {
  startLoading()
  window.addEventListener('resize', () => {
    if (trafficChart && !trafficChart.isDisposed()) trafficChart.resize()
    if (vehicleTypeChart && !vehicleTypeChart.isDisposed()) vehicleTypeChart.resize()
  })
})

onUnmounted(() => {
  if (trafficChart && !trafficChart.isDisposed()) trafficChart.dispose()
  if (vehicleTypeChart && !vehicleTypeChart.isDisposed()) vehicleTypeChart.dispose()
})
</script>

<style scoped>
.anpr-records-page {
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
.stat-trend.down { color: #ef4444; }

/* Camera Row */
.camera-row {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.camera-card {
  flex: 1;
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.camera-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  color: white;
}

.camera-title {
  font-weight: 600;
  font-size: 16px;
}

.camera-status {
  font-size: 12px;
}

.camera-status.online {
  color: #22c55e;
}

.camera-feed {
  height: 200px;
  background: #1e293b;
  display: flex;
  align-items: center;
  justify-content: center;
}

.feed-placeholder {
  text-align: center;
  color: #64748b;
}

.feed-placeholder .el-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.feed-placeholder span {
  display: block;
  font-size: 14px;
}

.latest-detection {
  margin-top: 16px;
  text-align: center;
}

.latest-detection .el-tag {
  font-size: 18px;
  padding: 8px 16px;
}

.detection-time {
  display: block;
  font-size: 11px;
  color: #94a3b8;
  margin-top: 8px;
}

/* Charts Row */
.charts-row {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  flex: 1;
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.chart-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.chart-subtitle {
  font-size: 12px;
  color: #64748b;
}

.chart-container {
  height: 280px;
  width: 100%;
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

.plate-number {
  font-family: monospace;
  font-weight: 600;
  letter-spacing: 1px;
}

.plate-number.large {
  font-size: 20px;
}

/* Record Detail */
.record-detail {
  padding: 8px;
}

.detail-image {
  margin-bottom: 20px;
}

.snapshot-placeholder {
  background: #1e293b;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  color: #64748b;
}

.snapshot-placeholder .el-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.snapshot-placeholder.large {
  padding: 60px;
}

.snapshot-info {
  margin-top: 16px;
  text-align: left;
  color: #94a3b8;
}

.snapshot-info p {
  margin: 4px 0;
}

.detail-section {
  margin-top: 20px;
}

.section-title {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
  margin-bottom: 12px;
  padding-left: 10px;
  border-left: 3px solid #3b82f6;
}

/* Snapshot Dialog */
.snapshot-container {
  text-align: center;
}

/* Responsive */
@media (max-width: 1000px) {
  .stats-grid, .camera-row, .charts-row {
    grid-template-columns: repeat(2, 1fr);
    flex-direction: column;
  }
  .camera-row {
    flex-direction: column;
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
  .filter-left {
    flex-direction: column;
    width: 100%;
  }
  .filter-left .el-input,
  .filter-left .el-select,
  .filter-left .el-date-editor {
    width: 100% !important;
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