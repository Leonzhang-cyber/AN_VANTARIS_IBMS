<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, Refresh, View, Edit, Delete, Monitor, Connection,
  User, Warning, Clock, OfficeBuilding, Location, UserFilled,
  WindPower, Download, Setting, Document, Checked, Bell, DataAnalysis,
  TrendCharts, Tickets, Coin, VideoCamera, Filter
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing sensors...',
  'Almost ready...'
]

// ==================== Chart Refs ====================
const occupancyChart = ref<HTMLElement | null>(null)
const consumablesChart = ref<HTMLElement | null>(null)
const peakHoursChart = ref<HTMLElement | null>(null)
const usageTrendChart = ref<HTMLElement | null>(null)

// ==================== State ====================
const activeTab = ref('overview')
const searchKeyword = ref('')
const statusFilter = ref('')
const floorFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(12)
const detailsDialogVisible = ref(false)
const addToiletDialogVisible = ref(false)
const workOrderDialogVisible = ref(false)
const selectedToilet = ref<any>(null)
const isConnected = ref(true)

// ==================== Statistics ====================
const statistics = reactive({
  totalToilets: 24,
  occupiedToilets: 8,
  lowConsumables: 3,
  avgVisitDuration: 4.5
})

// ==================== Thresholds ====================
const thresholds = reactive({
  toiletPaper: 20,
  soap: 15,
  odor: 6,
  visitDuration: 15
})

// ==================== Adapter Configuration ====================
const adapterConfig = reactive({
  protocol: 'mqtt',
  endpoint: 'mqtt://smart-toilet.example.com:1883',
  clientId: 'smart_toilet_adapter_01',
  username: '',
  password: '',
  keepAlive: 60,
  qos: 1,
  lastMessageTime: new Date().toISOString(),
  messagesToday: 2843,
  uptime: '12d 4h 23m'
})

// ==================== Toilets Data ====================
interface Toilet {
  id: string
  location: string
  floor: number
  status: 'available' | 'occupied' | 'maintenance' | 'offline'
  occupied: boolean
  odorLevel: number
  signalStrength: number
  toiletPaper: number
  soap: number
  waterLevel: number
  todayVisits: number
  avgVisitTime: number
  totalVisits: number
  lastCleaned: string
  adapterId: string
}

const toilets = ref<Toilet[]>([
  {
    id: 'T-101',
    location: 'North Wing - Floor 1',
    floor: 1,
    status: 'available',
    occupied: false,
    odorLevel: 2,
    signalStrength: 92,
    toiletPaper: 85,
    soap: 78,
    waterLevel: 95,
    todayVisits: 34,
    avgVisitTime: 4.2,
    totalVisits: 1247,
    lastCleaned: new Date().toISOString(),
    adapterId: 'ST_101_01'
  },
  {
    id: 'T-102',
    location: 'North Wing - Floor 1',
    floor: 1,
    status: 'occupied',
    occupied: true,
    odorLevel: 4,
    signalStrength: 88,
    toiletPaper: 45,
    soap: 62,
    waterLevel: 88,
    todayVisits: 28,
    avgVisitTime: 5.1,
    totalVisits: 982,
    lastCleaned: new Date(Date.now() - 7200000).toISOString(),
    adapterId: 'ST_102_01'
  },
  {
    id: 'T-103',
    location: 'South Wing - Floor 1',
    floor: 1,
    status: 'maintenance',
    occupied: false,
    odorLevel: 1,
    signalStrength: 0,
    toiletPaper: 12,
    soap: 8,
    waterLevel: 45,
    todayVisits: 0,
    avgVisitTime: 0,
    totalVisits: 156,
    lastCleaned: new Date(Date.now() - 86400000).toISOString(),
    adapterId: 'ST_103_01'
  },
  {
    id: 'T-201',
    location: 'North Wing - Floor 2',
    floor: 2,
    status: 'available',
    occupied: false,
    odorLevel: 3,
    signalStrength: 94,
    toiletPaper: 92,
    soap: 88,
    waterLevel: 96,
    todayVisits: 42,
    avgVisitTime: 3.8,
    totalVisits: 1567,
    lastCleaned: new Date().toISOString(),
    adapterId: 'ST_201_01'
  },
  {
    id: 'T-202',
    location: 'North Wing - Floor 2',
    floor: 2,
    status: 'occupied',
    occupied: true,
    odorLevel: 5,
    signalStrength: 86,
    toiletPaper: 34,
    soap: 45,
    waterLevel: 76,
    todayVisits: 31,
    avgVisitTime: 6.2,
    totalVisits: 876,
    lastCleaned: new Date(Date.now() - 10800000).toISOString(),
    adapterId: 'ST_202_01'
  },
  {
    id: 'T-203',
    location: 'South Wing - Floor 2',
    floor: 2,
    status: 'offline',
    occupied: false,
    odorLevel: 0,
    signalStrength: 0,
    toiletPaper: 0,
    soap: 0,
    waterLevel: 0,
    todayVisits: 0,
    avgVisitTime: 0,
    totalVisits: 423,
    lastCleaned: new Date(Date.now() - 172800000).toISOString(),
    adapterId: 'ST_203_01'
  },
  {
    id: 'T-301',
    location: 'North Wing - Floor 3',
    floor: 3,
    status: 'available',
    occupied: false,
    odorLevel: 2,
    signalStrength: 91,
    toiletPaper: 78,
    soap: 82,
    waterLevel: 92,
    todayVisits: 23,
    avgVisitTime: 3.5,
    totalVisits: 734,
    lastCleaned: new Date().toISOString(),
    adapterId: 'ST_301_01'
  },
  {
    id: 'T-302',
    location: 'South Wing - Floor 3',
    floor: 3,
    status: 'occupied',
    occupied: true,
    odorLevel: 6,
    signalStrength: 83,
    toiletPaper: 28,
    soap: 35,
    waterLevel: 68,
    todayVisits: 19,
    avgVisitTime: 7.1,
    totalVisits: 567,
    lastCleaned: new Date(Date.now() - 14400000).toISOString(),
    adapterId: 'ST_302_01'
  }
])

// ==================== Alerts Data ====================
const alerts = ref([
  { id: 1, time: '2024-01-15 09:23:45', toiletId: 'T-103', location: 'South Wing - Floor 1', type: 'Low Paper', message: 'Toilet paper level below 15%', acknowledged: false },
  { id: 2, time: '2024-01-15 10:05:12', toiletId: 'T-202', location: 'North Wing - Floor 2', type: 'High Odor', message: 'Odor level exceeding threshold (6/10)', acknowledged: false },
  { id: 3, time: '2024-01-15 10:30:22', toiletId: 'T-203', location: 'South Wing - Floor 2', type: 'Device Offline', message: 'No signal for over 2 hours', acknowledged: false },
  { id: 4, time: '2024-01-15 11:15:33', toiletId: 'T-302', location: 'South Wing - Floor 3', type: 'Low Soap', message: 'Soap level below 20%', acknowledged: false },
  { id: 5, time: '2024-01-15 11:45:18', toiletId: 'T-102', location: 'North Wing - Floor 1', type: 'Long Visit', message: 'Occupancy exceeds 15 minutes', acknowledged: false }
])

// ==================== Work Orders ====================
const workOrders = ref([
  { id: 'WO-001', toiletId: 'T-103', location: 'South Wing - Floor 1', type: 'Repair', description: 'Sensor malfunction - no data', status: 'In Progress', assignedTo: 'John Smith', createdAt: '2024-01-14', updatedAt: '2024-01-15' },
  { id: 'WO-002', toiletId: 'T-203', location: 'South Wing - Floor 2', type: 'Maintenance', description: 'Replace toilet paper dispenser', status: 'Pending', assignedTo: 'Mike Johnson', createdAt: '2024-01-15', updatedAt: '2024-01-15' },
  { id: 'WO-003', toiletId: 'T-302', location: 'South Wing - Floor 3', type: 'Refill', description: 'Refill soap dispenser', status: 'Completed', assignedTo: 'Sarah Williams', createdAt: '2024-01-14', updatedAt: '2024-01-14' }
])

// ==================== Payload Mappings ====================
const payloadMappings = ref([
  { id: 1, sourceField: 'payload.occupancy', targetField: 'occupied', description: 'Map occupancy sensor data' },
  { id: 2, sourceField: 'payload.paper_level', targetField: 'toiletPaper', description: 'Map toilet paper level' },
  { id: 3, sourceField: 'payload.soap_level', targetField: 'soap', description: 'Map soap dispenser level' },
  { id: 4, sourceField: 'payload.odor_sensor', targetField: 'odorLevel', description: 'Map odor sensor reading' }
])

// ==================== New Toilet Form ====================
const newToilet = ref({
  id: '',
  location: '',
  floor: 1,
  adapterId: ''
})

// ==================== New Work Order ====================
const newWorkOrder = ref({
  toiletId: '',
  type: '',
  description: '',
  assignedTo: ''
})

// ==================== Computed ====================
const filteredToilets = computed(() => {
  let filtered = toilets.value
  if (searchKeyword.value) {
    filtered = filtered.filter(t =>
        t.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        t.location.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (statusFilter.value) {
    filtered = filtered.filter(t => t.status === statusFilter.value)
  }
  if (floorFilter.value) {
    filtered = filtered.filter(t => t.floor.toString() === floorFilter.value)
  }
  return filtered
})

const paginatedToilets = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredToilets.value.slice(start, end)
})

// ==================== Methods ====================
const getStatusClass = (status: string) => {
  const classes: Record<string, string> = {
    available: 'status-available',
    occupied: 'status-occupied',
    maintenance: 'status-maintenance',
    offline: 'status-offline'
  }
  return classes[status] || ''
}

const getStatusTagType = (status: string) => {
  const types: Record<string, string> = {
    available: 'success',
    occupied: 'warning',
    maintenance: 'danger',
    offline: 'info'
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    available: 'Available',
    occupied: 'Occupied',
    maintenance: 'Maintenance',
    offline: 'Offline'
  }
  return texts[status] || status
}

const getProgressColor = (percentage: number) => {
  if (percentage >= 60) return '#52c41a'
  if (percentage >= 30) return '#faad14'
  return '#ff4d4f'
}

const getAlertType = (type: string) => {
  const types: Record<string, string> = {
    'Low Paper': 'warning',
    'Low Soap': 'warning',
    'High Odor': 'danger',
    'Device Offline': 'info',
    'Long Visit': 'warning'
  }
  return types[type] || 'info'
}

const getMaintenanceTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    'Repair': 'danger',
    'Maintenance': 'warning',
    'Refill': 'success'
  }
  return colors[type] || 'info'
}

const getMaintenanceStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    'Pending': 'warning',
    'In Progress': 'primary',
    'Completed': 'success'
  }
  return colors[status] || 'info'
}

const formatTime = (timestamp: string) => {
  if (!timestamp) return 'Never'
  const date = new Date(timestamp)
  return date.toLocaleString()
}

const handleToggleOccupancy = (toilet: Toilet) => {
  toilet.occupied = !toilet.occupied
  toilet.status = toilet.occupied ? 'occupied' : 'available'
  ElMessage.success(`${toilet.id} is now ${toilet.occupied ? 'occupied' : 'available'}`)
}

const handleViewDetails = (toilet: Toilet) => {
  selectedToilet.value = toilet
  detailsDialogVisible.value = true
}

const handleAddToilet = () => {
  newToilet.value = { id: '', location: '', floor: 1, adapterId: '' }
  addToiletDialogVisible.value = true
}

const handleSaveToilet = () => {
  if (!newToilet.value.id || !newToilet.value.location) {
    ElMessage.warning('Please fill in all required fields')
    return
  }
  const toilet: Toilet = {
    id: newToilet.value.id,
    location: newToilet.value.location,
    floor: newToilet.value.floor,
    status: 'offline',
    occupied: false,
    odorLevel: 0,
    signalStrength: 0,
    toiletPaper: 0,
    soap: 0,
    waterLevel: 0,
    todayVisits: 0,
    avgVisitTime: 0,
    totalVisits: 0,
    lastCleaned: new Date().toISOString(),
    adapterId: newToilet.value.adapterId
  }
  toilets.value.push(toilet)
  addToiletDialogVisible.value = false
  ElMessage.success('Toilet added successfully')
}

const handleRefresh = () => {
  ElMessage.info('Refreshing data...')
  setTimeout(() => {
    statistics.totalMessages += Math.floor(Math.random() * 100)
    ElMessage.success('Data refreshed')
  }, 500)
}

const handleExportData = () => {
  ElMessage.success('Export started...')
}

const handleAcknowledgeAlert = (alert: any) => {
  alert.acknowledged = true
  const index = alerts.value.findIndex(a => a.id === alert.id)
  if (index !== -1) {
    alerts.value.splice(index, 1)
  }
  ElMessage.success('Alert acknowledged')
}

const handleCreateWorkOrder = () => {
  newWorkOrder.value = { toiletId: '', type: '', description: '', assignedTo: '' }
  workOrderDialogVisible.value = true
}

const handleSaveWorkOrder = () => {
  if (!newWorkOrder.value.toiletId || !newWorkOrder.value.type) {
    ElMessage.warning('Please fill in required fields')
    return
  }
  const workOrder = {
    id: `WO-${String(workOrders.value.length + 1).padStart(3, '0')}`,
    ...newWorkOrder.value,
    status: 'Pending',
    createdAt: new Date().toISOString().split('T')[0],
    updatedAt: new Date().toISOString().split('T')[0]
  }
  workOrders.value.push(workOrder)
  workOrderDialogVisible.value = false
  ElMessage.success('Work order created successfully')
}

const handleUpdateWorkOrder = (order: any) => {
  ElMessage.info(`Updating work order: ${order.id}`)
}

const handleToggleConnection = () => {
  isConnected.value = !isConnected.value
  ElMessage.success(`Adapter ${isConnected.value ? 'connected' : 'disconnected'}`)
}

const handleSaveThresholds = () => {
  ElMessage.success('Thresholds saved successfully')
}

const handleEditMapping = (mapping: any) => {
  ElMessage.info(`Editing mapping: ${mapping.sourceField} -> ${mapping.targetField}`)
}

// ==================== Initialize Charts ====================
const initCharts = () => {
  if (!occupancyChart.value) return

  // Occupancy Overview Chart (Pie)
  const occupancy = echarts.init(occupancyChart.value)
  occupancy.setOption({
    tooltip: { trigger: 'item' },
    legend: { top: 'bottom' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: 16, name: 'Available', itemStyle: { color: '#52c41a' } },
        { value: 8, name: 'Occupied', itemStyle: { color: '#faad14' } },
        { value: 2, name: 'Maintenance', itemStyle: { color: '#ff4d4f' } },
        { value: 2, name: 'Offline', itemStyle: { color: '#8c8c8c' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })

  // Consumables Status Chart (Gauge)
  const consumables = echarts.init(consumablesChart.value)
  consumables.setOption({
    tooltip: { trigger: 'axis' },
    radar: {
      indicator: [
        { name: 'Toilet Paper', max: 100 },
        { name: 'Soap', max: 100 },
        { name: 'Water', max: 100 },
        { name: 'Air Quality', max: 10 }
      ],
      shape: 'circle',
      center: ['50%', '50%'],
      radius: '65%'
    },
    series: [{
      type: 'radar',
      data: [{ value: [72, 65, 82, 3.2], name: 'Average Levels' }],
      areaStyle: { color: 'rgba(24, 144, 255, 0.2)' },
      lineStyle: { color: '#1890ff', width: 2 },
      itemStyle: { color: '#1890ff' }
    }]
  })

  // Peak Hours Chart (Bar)
  const peakHours = echarts.init(peakHoursChart.value)
  peakHours.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['8AM', '9AM', '10AM', '11AM', '12PM', '1PM', '2PM', '3PM', '4PM', '5PM', '6PM'] },
    yAxis: { type: 'value', name: 'Visits' },
    series: [{
      data: [12, 23, 31, 45, 67, 58, 42, 38, 35, 28, 19],
      type: 'bar',
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#faad14' }
    }]
  })

  // Usage Trends Chart (Line)
  const usageTrend = echarts.init(usageTrendChart.value)
  usageTrend.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
    yAxis: { type: 'value', name: 'Total Visits' },
    series: [{
      data: [245, 267, 289, 312, 356, 289, 234],
      type: 'line',
      smooth: true,
      areaStyle: { opacity: 0.3 },
      lineStyle: { color: '#1890ff', width: 2 },
      itemStyle: { color: '#1890ff' }
    }]
  })

  // Handle resize
  window.addEventListener('resize', () => {
    occupancy.resize()
    consumables.resize()
    peakHours.resize()
    usageTrend.resize()
  })
}

// ==================== Watch for Tab Changes ====================
watch(activeTab, (newTab) => {
  if (newTab === 'monitoring') {
    nextTick(() => {
      initCharts()
    })
  }
})

// ==================== Loading on Mount ====================
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
      if (activeTab.value === 'monitoring') {
        initCharts()
      }
    }, 400)
  }, 2000)
})
</script>

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
          <span class="loading-title">Loading Smart Toilet Adapter</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="smart-toilet-adapter">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2>Smart Toilet Adapter</h2>
        <p>Monitor and manage smart toilet devices with real-time occupancy tracking, consumables monitoring, and hygiene analytics</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleAddToilet">
          <el-icon><Plus /></el-icon>
          Add Toilet
        </el-button>
        <el-button @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-cards">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #e8f4ff">
            <el-icon color="#1890ff" size="28"><OfficeBuilding /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.totalToilets }}</div>
            <div class="stat-label">Total Toilets</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #e6f7e6">
            <el-icon color="#52c41a" size="28"><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.occupiedToilets }}</div>
            <div class="stat-label">Occupied</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #fff7e6">
            <el-icon color="#faad14" size="28"><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.lowConsumables }}</div>
            <div class="stat-label">Low Consumables</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #fdf0e8">
            <el-icon color="#ff7a45" size="28"><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.avgVisitDuration }}</div>
            <div class="stat-label">Avg Visit (min)</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Main Tabs -->
    <el-tabs v-model="activeTab" class="toilet-tabs">
      <!-- Toilet Overview Tab -->
      <el-tab-pane label="Toilet Overview" name="overview">
        <div class="toolbar">
          <div class="toolbar-left">
            <el-input
                v-model="searchKeyword"
                placeholder="Search by location or ID..."
                clearable
                style="width: 260px"
                :prefix-icon="Search"
            />
            <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 130px">
              <el-option label="All" value="" />
              <el-option label="Available" value="available" />
              <el-option label="Occupied" value="occupied" />
              <el-option label="Maintenance" value="maintenance" />
              <el-option label="Offline" value="offline" />
            </el-select>
            <el-select v-model="floorFilter" placeholder="Floor" clearable style="width: 120px">
              <el-option label="All Floors" value="" />
              <el-option label="Floor 1" value="1" />
              <el-option label="Floor 2" value="2" />
              <el-option label="Floor 3" value="3" />
            </el-select>
          </div>
          <div class="toolbar-right">
            <el-button type="success" @click="handleExportData">
              <el-icon><Download /></el-icon>
              Export Report
            </el-button>
          </div>
        </div>

        <!-- Toilet Grid View -->
        <div class="toilet-grid">
          <el-card
              v-for="toilet in paginatedToilets"
              :key="toilet.id"
              class="toilet-card"
              :class="getStatusClass(toilet.status)"
              shadow="hover"
          >
            <div class="toilet-header">
              <div class="toilet-id">
                <el-icon><Monitor /></el-icon>
                <span>{{ toilet.id }}</span>
              </div>
              <el-tag :type="getStatusTagType(toilet.status)" size="small">
                {{ getStatusText(toilet.status) }}
              </el-tag>
            </div>

            <div class="toilet-location">
              <el-icon><Location /></el-icon>
              <span>{{ toilet.location }}</span>
            </div>

            <div class="toilet-sensors">
              <div class="sensor-item">
                <el-icon><UserFilled /></el-icon>
                <span :class="{ occupied: toilet.occupied }">
                  {{ toilet.occupied ? 'Occupied' : 'Available' }}
                </span>
              </div>
              <div class="sensor-item">
                <el-icon><WindPower /></el-icon>
                <span>Odor: {{ toilet.odorLevel }}/10</span>
              </div>
              <div class="sensor-item">
                <el-icon><Connection /></el-icon>
                <span>Signal: {{ toilet.signalStrength }}%</span>
              </div>
            </div>

            <div class="consumables">
              <div class="consumable-item">
                <span class="label">Toilet Paper:</span>
                <el-progress
                    :percentage="toilet.toiletPaper"
                    :color="getProgressColor(toilet.toiletPaper)"
                    :stroke-width="6"
                />
              </div>
              <div class="consumable-item">
                <span class="label">Soap:</span>
                <el-progress
                    :percentage="toilet.soap"
                    :color="getProgressColor(toilet.soap)"
                    :stroke-width="6"
                />
              </div>
              <div class="consumable-item">
                <span class="label">Water:</span>
                <el-progress
                    :percentage="toilet.waterLevel"
                    :color="getProgressColor(toilet.waterLevel)"
                    :stroke-width="6"
                />
              </div>
            </div>

            <div class="toilet-footer">
              <div class="visit-stats">
                <span>Today: {{ toilet.todayVisits }} visits</span>
                <span>Avg: {{ toilet.avgVisitTime }}min</span>
              </div>
              <div class="actions">
                <el-button
                    :type="toilet.occupied ? 'danger' : 'success'"
                    size="small"
                    @click="handleToggleOccupancy(toilet)"
                >
                  {{ toilet.occupied ? 'Mark Available' : 'Mark Occupied' }}
                </el-button>
                <el-button size="small" @click="handleViewDetails(toilet)">
                  Details
                </el-button>
              </div>
            </div>
          </el-card>
        </div>

        <!-- Pagination -->
        <div class="pagination-wrapper">
          <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[12, 24, 48, 96]"
              :total="filteredToilets.length"
              layout="total, sizes, prev, pager, next, jumper"
          />
        </div>
      </el-tab-pane>

      <!-- Real-time Monitoring Tab -->
      <el-tab-pane label="Real-time Monitoring" name="monitoring">
        <div class="monitoring-container">
          <el-row :gutter="16">
            <el-col :xs="24" :sm="12" :lg="8">
              <el-card class="monitoring-card" header="Occupancy Overview">
                <div ref="occupancyChart" style="height: 280px"></div>
              </el-card>
            </el-col>
            <el-col :xs="24" :sm="12" :lg="8">
              <el-card class="monitoring-card" header="Consumables Status">
                <div ref="consumablesChart" style="height: 280px"></div>
              </el-card>
            </el-col>
            <el-col :xs="24" :sm="24" :lg="8">
              <el-card class="monitoring-card" header="Peak Usage Hours">
                <div ref="peakHoursChart" style="height: 280px"></div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="16" style="margin-top: 16px">
            <el-col :span="24">
              <el-card class="monitoring-card" header="Usage Trends (Last 7 Days)">
                <div ref="usageTrendChart" style="height: 320px"></div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="16" style="margin-top: 16px">
            <el-col :span="24">
              <el-card class="monitoring-card" header="Alerts & Notifications">
                <el-table :data="alerts" style="width: 100%" stripe>
                  <el-table-column prop="time" label="Time" width="180" />
                  <el-table-column prop="toiletId" label="Toilet ID" width="120" />
                  <el-table-column prop="location" label="Location" width="150" />
                  <el-table-column prop="type" label="Alert Type" width="150">
                    <template #default="{ row }">
                      <el-tag :type="getAlertType(row.type)" size="small">{{ row.type }}</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="message" label="Message" />
                  <el-table-column label="Actions" width="100">
                    <template #default="{ row }">
                      <el-button link type="primary" size="small" @click="handleAcknowledgeAlert(row)">
                        Acknowledge
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>

      <!-- Configuration Tab -->
      <el-tab-pane label="Adapter Configuration" name="config">
        <el-row :gutter="16">
          <el-col :span="16">
            <el-card class="config-card" header="Protocol Settings">
              <el-form :model="adapterConfig" label-width="140px">
                <el-form-item label="Protocol Type">
                  <el-select v-model="adapterConfig.protocol" style="width: 100%">
                    <el-option label="MQTT" value="mqtt" />
                    <el-option label="CoAP" value="coap" />
                    <el-option label="HTTP Webhook" value="http" />
                    <el-option label="WebSocket" value="websocket" />
                  </el-select>
                </el-form-item>

                <el-form-item label="Broker/Endpoint">
                  <el-input v-model="adapterConfig.endpoint" placeholder="mqtt://broker.example.com:1883" />
                </el-form-item>

                <el-form-item label="Client ID">
                  <el-input v-model="adapterConfig.clientId" />
                </el-form-item>

                <el-form-item label="Username">
                  <el-input v-model="adapterConfig.username" placeholder="Optional" />
                </el-form-item>

                <el-form-item label="Password">
                  <el-input v-model="adapterConfig.password" type="password" placeholder="Optional" />
                </el-form-item>

                <el-form-item label="Keep Alive (seconds)">
                  <el-input-number v-model="adapterConfig.keepAlive" :min="10" :max="300" />
                </el-form-item>

                <el-form-item label="QoS Level">
                  <el-radio-group v-model="adapterConfig.qos">
                    <el-radio :label="0">0 - At most once</el-radio>
                    <el-radio :label="1">1 - At least once</el-radio>
                    <el-radio :label="2">2 - Exactly once</el-radio>
                  </el-radio-group>
                </el-form-item>
              </el-form>
            </el-card>
          </el-col>

          <el-col :span="8">
            <el-card class="config-card" header="Connection Status">
              <div class="connection-status">
                <div class="status-indicator">
                  <div class="status-dot" :class="{ connected: isConnected }"></div>
                  <span class="status-text">{{ isConnected ? 'Connected' : 'Disconnected' }}</span>
                </div>
                <div class="connection-details">
                  <div class="detail-item">
                    <span class="label">Last Message:</span>
                    <span class="value">{{ formatTime(adapterConfig.lastMessageTime) }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">Messages Today:</span>
                    <span class="value">{{ adapterConfig.messagesToday }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">Uptime:</span>
                    <span class="value">{{ adapterConfig.uptime }}</span>
                  </div>
                </div>
                <el-button
                    :type="isConnected ? 'danger' : 'success'"
                    style="width: 100%; margin-top: 16px"
                    @click="handleToggleConnection"
                >
                  {{ isConnected ? 'Disconnect' : 'Connect' }}
                </el-button>
              </div>
            </el-card>

            <el-card class="config-card" header="Alert Thresholds" style="margin-top: 16px">
              <el-form label-width="120px" size="small">
                <el-form-item label="Toilet Paper">
                  <el-slider v-model="thresholds.toiletPaper" :min="0" :max="100" />
                  <span class="threshold-value">{{ thresholds.toiletPaper }}%</span>
                </el-form-item>
                <el-form-item label="Soap Level">
                  <el-slider v-model="thresholds.soap" :min="0" :max="100" />
                  <span class="threshold-value">{{ thresholds.soap }}%</span>
                </el-form-item>
                <el-form-item label="Odor Level">
                  <el-slider v-model="thresholds.odor" :min="0" :max="10" />
                  <span class="threshold-value">{{ thresholds.odor }}/10</span>
                </el-form-item>
                <el-form-item label="Visit Duration">
                  <el-slider v-model="thresholds.visitDuration" :min="5" :max="60" />
                  <span class="threshold-value">{{ thresholds.visitDuration }} min</span>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" size="small" @click="handleSaveThresholds">Save Thresholds</el-button>
                </el-form-item>
              </el-form>
            </el-card>
          </el-col>
        </el-row>

        <el-card class="config-card" header="Payload Mapping" style="margin-top: 16px">
          <el-table :data="payloadMappings" style="width: 100%" stripe>
            <el-table-column prop="sourceField" label="Source Field" min-width="180">
              <template #default="{ row }">
                <code>{{ row.sourceField }}</code>
              </template>
            </el-table-column>
            <el-table-column prop="targetField" label="Target Field" min-width="180">
              <template #default="{ row }">
                <code>{{ row.targetField }}</code>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="Description" />
            <el-table-column label="Actions" width="100">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="handleEditMapping(row)">
                  <el-icon><Edit /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- Maintenance Tab -->
      <el-tab-pane label="Maintenance" name="maintenance">
        <div class="maintenance-container">
          <div class="maintenance-header">
            <h3>Maintenance Schedule</h3>
            <el-button type="primary" @click="handleCreateWorkOrder">
              <el-icon><Plus /></el-icon>
              Create Work Order
            </el-button>
          </div>

          <el-table :data="workOrders" style="width: 100%; margin-top: 16px" stripe>
            <el-table-column prop="id" label="Order ID" width="120" />
            <el-table-column prop="toiletId" label="Toilet ID" width="120" />
            <el-table-column prop="location" label="Location" width="150" />
            <el-table-column prop="type" label="Type" width="120">
              <template #default="{ row }">
                <el-tag :type="getMaintenanceTypeColor(row.type)">{{ row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="Description" />
            <el-table-column prop="status" label="Status" width="120">
              <template #default="{ row }">
                <el-tag :type="getMaintenanceStatusColor(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="assignedTo" label="Assigned To" width="140" />
            <el-table-column prop="createdAt" label="Created" width="120" />
            <el-table-column label="Actions" width="100">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="handleUpdateWorkOrder(row)">
                  Update
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Toilet Details Dialog -->
    <el-dialog v-model="detailsDialogVisible" :title="`Toilet Details - ${selectedToilet?.id}`" width="600px">
      <div v-if="selectedToilet" class="toilet-details">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Location">{{ selectedToilet.location }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(selectedToilet.status)">{{ getStatusText(selectedToilet.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Today Visits">{{ selectedToilet.todayVisits }}</el-descriptions-item>
          <el-descriptions-item label="Average Visit Time">{{ selectedToilet.avgVisitTime }} minutes</el-descriptions-item>
          <el-descriptions-item label="Total Visits (All Time)">{{ selectedToilet.totalVisits }}</el-descriptions-item>
          <el-descriptions-item label="Last Cleaned">{{ formatTime(selectedToilet.lastCleaned) }}</el-descriptions-item>
          <el-descriptions-item label="Toilet Paper Level" :span="2">
            <el-progress :percentage="selectedToilet.toiletPaper" :color="getProgressColor(selectedToilet.toiletPaper)" />
          </el-descriptions-item>
          <el-descriptions-item label="Soap Level" :span="2">
            <el-progress :percentage="selectedToilet.soap" :color="getProgressColor(selectedToilet.soap)" />
          </el-descriptions-item>
          <el-descriptions-item label="Odor Level" :span="2">
            <el-rate v-model="selectedToilet.odorLevel" disabled :max="10" show-score />
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- Add Toilet Dialog -->
    <el-dialog v-model="addToiletDialogVisible" title="Add New Smart Toilet" width="500px">
      <el-form :model="newToilet" label-width="120px">
        <el-form-item label="Toilet ID" required>
          <el-input v-model="newToilet.id" placeholder="e.g., T-101" />
        </el-form-item>
        <el-form-item label="Location" required>
          <el-input v-model="newToilet.location" placeholder="e.g., Floor 1 - North Wing" />
        </el-form-item>
        <el-form-item label="Floor">
          <el-input-number v-model="newToilet.floor" :min="1" :max="50" />
        </el-form-item>
        <el-form-item label="Adapter ID">
          <el-input v-model="newToilet.adapterId" placeholder="Device adapter identifier" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addToiletDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleSaveToilet">Add</el-button>
      </template>
    </el-dialog>

    <!-- Work Order Dialog -->
    <el-dialog v-model="workOrderDialogVisible" title="Create Work Order" width="550px">
      <el-form :model="newWorkOrder" label-width="120px">
        <el-form-item label="Toilet ID" required>
          <el-select v-model="newWorkOrder.toiletId" placeholder="Select toilet" style="width: 100%">
            <el-option v-for="toilet in toilets" :key="toilet.id" :label="`${toilet.id} - ${toilet.location}`" :value="toilet.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Work Type" required>
          <el-select v-model="newWorkOrder.type" placeholder="Select type" style="width: 100%">
            <el-option label="Repair" value="Repair" />
            <el-option label="Maintenance" value="Maintenance" />
            <el-option label="Refill" value="Refill" />
            <el-option label="Cleaning" value="Cleaning" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="newWorkOrder.description" type="textarea" :rows="3" placeholder="Describe the issue or task" />
        </el-form-item>
        <el-form-item label="Assign To">
          <el-input v-model="newWorkOrder.assignedTo" placeholder="Assignee name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="workOrderDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleSaveWorkOrder">Create</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
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

.spinner-ring:nth-child(1) {
  border-top-color: #3b82f6;
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  border-right-color: #f59e0b;
  animation-delay: 0.2s;
  width: 70%;
  height: 70%;
  top: 15%;
  left: 15%;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #10b981;
  animation-delay: 0.4s;
  width: 40%;
  height: 40%;
  top: 30%;
  left: 30%;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-bottom: 24px;
  font-size: 20px;
  font-weight: 600;
  color: #e2e8f0;
  display: flex;
  justify-content: center;
  align-items: baseline;
  gap: 4px;
}

.loading-title {
  font-size: 20px;
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
  font-weight: 500;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ==================== Main Content ==================== */
.smart-toilet-adapter {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: calc(100vh - 60px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.header-left h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.header-left p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 12px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
}

.stat-label {
  font-size: 14px;
  color: #8c8c8c;
  margin-top: 4px;
}

.toilet-tabs {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.toolbar-left {
  display: flex;
  gap: 12px;
  align-items: center;
}

.toolbar-right {
  display: flex;
  gap: 12px;
}

/* Toilet Grid */
.toilet-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.toilet-card {
  transition: all 0.3s ease;
  border-left: 4px solid #d9d9d9;
}

.toilet-card.status-available {
  border-left-color: #52c41a;
}

.toilet-card.status-occupied {
  border-left-color: #faad14;
}

.toilet-card.status-maintenance {
  border-left-color: #ff4d4f;
}

.toilet-card.status-offline {
  border-left-color: #8c8c8c;
}

.toilet-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.toilet-id {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

.toilet-location {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 13px;
  margin-bottom: 16px;
}

.toilet-sensors {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 8px;
}

.sensor-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.sensor-item .occupied {
  color: #faad14;
  font-weight: 500;
}

.consumables {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.consumable-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.consumable-item .label {
  width: 90px;
  font-size: 13px;
  color: #666;
}

.consumable-item :deep(.el-progress) {
  flex: 1;
}

.toilet-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.visit-stats {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: #999;
}

.actions {
  display: flex;
  gap: 8px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

/* Monitoring */
.monitoring-container {
  padding: 16px 0;
}

.monitoring-card {
  height: 100%;
}

/* Configuration */
.config-card {
  margin-bottom: 0;
}

.connection-status {
  text-align: center;
  padding: 16px;
}

.status-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 20px;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #ff4d4f;
  animation: pulse-red 2s infinite;
}

.status-dot.connected {
  background-color: #52c41a;
  animation: pulse-green 2s infinite;
}

@keyframes pulse-red {
  0% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
  100% { opacity: 1; transform: scale(1); }
}

@keyframes pulse-green {
  0% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
  100% { opacity: 1; transform: scale(1); }
}

.status-text {
  font-size: 16px;
  font-weight: 600;
}

.connection-details {
  text-align: left;
  margin-top: 16px;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 8px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 13px;
  border-bottom: 1px solid #f0f0f0;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-item .label {
  color: #666;
}

.detail-item .value {
  font-weight: 500;
  color: #1a1a1a;
}

.threshold-value {
  margin-left: 12px;
  font-size: 12px;
  color: #666;
}

/* Maintenance */
.maintenance-container {
  padding: 16px 0;
}

.maintenance-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Toilet Details */
.toilet-details {
  padding: 8px 0;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .toilet-grid {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
  }

  .header-right {
    margin-top: 16px;
    width: 100%;
  }

  .toolbar {
    flex-direction: column;
    gap: 12px;
  }

  .toolbar-left {
    width: 100%;
    flex-wrap: wrap;
  }

  .toolbar-right {
    width: 100%;
  }

  .toilet-grid {
    grid-template-columns: 1fr;
  }
}

:deep(.el-card__header) {
  font-weight: 600;
  background-color: #fafafa;
  border-bottom: 1px solid #f0f0f0;
}

:deep(.el-tabs__header) {
  margin-bottom: 20px;
}
</style>