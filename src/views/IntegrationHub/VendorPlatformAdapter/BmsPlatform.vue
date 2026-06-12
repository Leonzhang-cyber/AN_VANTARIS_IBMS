<script setup lang="ts">
import { ref, onMounted, computed, watch, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Monitor, BellFilled, Refresh, Connection, Setting,
  Search, DataLine, WindPower, HomeFilled,
  Lightning, Sunny, Clock
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing BMS SDK...',
  'Connecting to building controllers...',
  'Syncing HVAC systems...',
  'Loading energy meters...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const deviceDetailVisible = ref(false)
const configDrawerVisible = ref(false)
const setpointVisible = ref(false)
const tempChartRef = ref(null)
const energyChartRef = ref(null)
const hvacChartRef = ref(null)

let tempChart: echarts.ECharts | null = null
let energyChart: echarts.ECharts | null = null
let hvacChart: echarts.ECharts | null = null

const selectedDevice = ref<any>(null)
const currentChartPeriod = ref('week')

// Statistics data
const stats = reactive({
  totalBuildings: 8,
  onlineBuildings: 8,
  totalHVAC: 156,
  onlineHVAC: 152,
  totalLighting: 245,
  onlineLighting: 238,
  totalSensors: 890,
  onlineSensors: 875,
  totalEnergyMeters: 45,
  todayEnergyKWh: 12450,
  monthEnergyKWh: 342000,
  energyCost: 51200,
  co2Reduction: 12.5
})

// BMS Devices
const devices = ref([
  { id: 'BMS001', name: 'AHU-1', location: 'Building A - 1F', type: 'AHU', status: 'online', value: 22.5, unit: '°C', setpoint: 22, lastHeartbeat: '2024-01-15 10:23:45', energy: 45.2, controller: 'BAS-01' },
  { id: 'BMS002', name: 'AHU-2', location: 'Building A - 2F', type: 'AHU', status: 'online', value: 23.0, unit: '°C', setpoint: 22, lastHeartbeat: '2024-01-15 10:22:30', energy: 42.8, controller: 'BAS-01' },
  { id: 'BMS003', name: 'Chiller-1', location: 'Plant Room', type: 'Chiller', status: 'online', value: 7.2, unit: '°C', setpoint: 7, lastHeartbeat: '2024-01-15 10:24:12', energy: 125.5, controller: 'BAS-02' },
  { id: 'BMS004', name: 'Chiller-2', location: 'Plant Room', type: 'Chiller', status: 'online', value: 7.5, unit: '°C', setpoint: 7, lastHeartbeat: '2024-01-15 10:20:00', energy: 118.3, controller: 'BAS-02' },
  { id: 'BMS005', name: 'Cooling Tower-1', location: 'Roof', type: 'Cooling Tower', status: 'online', value: 28.5, unit: '°C', setpoint: 28, lastHeartbeat: '2024-01-15 10:23:00', energy: 35.6, controller: 'BAS-02' },
  { id: 'BMS006', name: 'VAV-101', location: 'Building A - 3F', type: 'VAV', status: 'online', value: 350, unit: 'CFM', setpoint: 350, lastHeartbeat: '2024-01-15 10:22:15', energy: 12.3, controller: 'BAS-03' },
  { id: 'BMS007', name: 'VAV-102', location: 'Building A - 3F', type: 'VAV', status: 'offline', value: 0, unit: 'CFM', setpoint: 350, lastHeartbeat: '2024-01-14 18:30:00', energy: 0, controller: 'BAS-03' },
  { id: 'BMS008', name: 'Lighting Panel-L1', location: 'Building A - 1F', type: 'Lighting', status: 'online', value: 85, unit: '%', setpoint: 80, lastHeartbeat: '2024-01-15 10:21:30', energy: 28.4, controller: 'BAS-04' },
  { id: 'BMS009', name: 'Lighting Panel-L2', location: 'Building A - 2F', type: 'Lighting', status: 'online', value: 75, unit: '%', setpoint: 80, lastHeartbeat: '2024-01-15 10:23:45', energy: 25.6, controller: 'BAS-04' },
  { id: 'BMS010', name: 'Temp Sensor - Lobby', location: 'Building A - Lobby', type: 'Temperature', status: 'online', value: 22.3, unit: '°C', setpoint: null, lastHeartbeat: '2024-01-15 10:24:00', energy: null, controller: 'BAS-05' },
  { id: 'BMS011', name: 'Humidity Sensor', location: 'Building A - Lobby', type: 'Humidity', status: 'online', value: 55, unit: '%', setpoint: null, lastHeartbeat: '2024-01-15 10:23:50', energy: null, controller: 'BAS-05' },
  { id: 'BMS012', name: 'CO2 Sensor', location: 'Building A - 2F', type: 'CO2', status: 'online', value: 420, unit: 'ppm', setpoint: 1000, lastHeartbeat: '2024-01-15 10:23:30', energy: null, controller: 'BAS-05' },
  { id: 'BMS013', name: 'Power Meter-Main', location: 'Electrical Room', type: 'Power', status: 'online', value: 245, unit: 'kW', setpoint: null, lastHeartbeat: '2024-01-15 10:22:00', energy: 245.5, controller: 'BAS-06' },
  { id: 'BMS014', name: 'Boiler-1', location: 'Boiler Room', type: 'Boiler', status: 'online', value: 65, unit: '°C', setpoint: 65, lastHeartbeat: '2024-01-15 10:21:15', energy: 98.2, controller: 'BAS-07' },
  { id: 'BMS015', name: 'Pump-1', location: 'Plant Room', type: 'Pump', status: 'online', value: 85, unit: '%', setpoint: 85, lastHeartbeat: '2024-01-15 10:24:20', energy: 22.5, controller: 'BAS-02' }
])

// Building zones
const zones = ref([
  { name: 'Zone A', temp: 22.5, humidity: 52, co2: 410, occupancy: 85 },
  { name: 'Zone B', temp: 23.0, humidity: 55, co2: 425, occupancy: 72 },
  { name: 'Zone C', temp: 22.8, humidity: 50, co2: 405, occupancy: 68 },
  { name: 'Zone D', temp: 23.2, humidity: 58, co2: 440, occupancy: 90 }
])

// Platform configuration
const platformConfig = ref({
  host: 'https://bms-platform.example.com',
  apiKey: '',
  bacnetPort: 47808,
  modbusPort: 502,
  syncInterval: 300,
  tempUnit: 'celsius',
  alarmThresholds: {
    tempHigh: 26,
    tempLow: 18,
    humidityHigh: 70,
    co2High: 1000
  },
  energyCostRate: 0.15
})

// Device setpoint form
const setpointForm = ref({
  deviceId: '',
  setpoint: 0,
  reason: ''
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: devices.value.length
})

// Filtered devices
const filteredDevices = computed(() => {
  let filtered = devices.value
  if (searchKeyword.value) {
    filtered = filtered.filter(d =>
        d.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        d.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        d.location.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        d.type.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  pagination.total = filtered.length
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// Watch for search keyword to reset pagination
watch(searchKeyword, () => {
  pagination.page = 1
})

// ==================== Loading Simulation ====================
onMounted(() => {
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 12 + 4
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
      setTimeout(() => {
        initTempChart()
        initEnergyChart()
        initHVACChart()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initTempChart = () => {
  if (!tempChartRef.value) return

  tempChart = echarts.init(tempChartRef.value)
  updateTempChart()
}

const updateTempChart = () => {
  const weekData = {
    xAxis: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    indoor: [22.5, 22.8, 22.6, 23.0, 22.7, 22.9, 22.4],
    outdoor: [28, 29, 27, 30, 28, 26, 25]
  }

  const monthData = {
    xAxis: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    indoor: [22.6, 22.8, 22.9, 22.7],
    outdoor: [27.5, 28.2, 28.5, 27.8]
  }

  const data = currentChartPeriod.value === 'week' ? weekData : monthData

  tempChart?.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Indoor Temperature', 'Outdoor Temperature'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: data.xAxis },
    yAxis: { type: 'value', name: 'Temperature (°C)' },
    series: [
      { name: 'Indoor Temperature', type: 'line', data: data.indoor, smooth: true, lineStyle: { color: '#409EFF', width: 2 }, areaStyle: { opacity: 0.1, color: '#409EFF' }, symbol: 'circle', symbolSize: 8 },
      { name: 'Outdoor Temperature', type: 'line', data: data.outdoor, smooth: true, lineStyle: { color: '#E6A23C', width: 2 }, symbol: 'diamond', symbolSize: 8 }
    ]
  })
}

const initEnergyChart = () => {
  if (!energyChartRef.value) return

  energyChart = echarts.init(energyChartRef.value)
  updateEnergyChart()
}

const updateEnergyChart = () => {
  const weekData = {
    xAxis: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    hvac: [3200, 3150, 3300, 3250, 3400, 3100, 2950],
    lighting: [1850, 1820, 1880, 1850, 1900, 1650, 1550],
    other: [950, 920, 980, 960, 990, 850, 800]
  }

  const monthData = {
    xAxis: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    hvac: [22500, 22800, 23200, 22100],
    lighting: [12800, 13000, 13200, 12600],
    other: [6600, 6700, 6800, 6500]
  }

  const data = currentChartPeriod.value === 'week' ? weekData : monthData

  energyChart?.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['HVAC', 'Lighting', 'Other'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: data.xAxis },
    yAxis: { type: 'value', name: 'Energy (kWh)' },
    series: [
      { name: 'HVAC', type: 'bar', data: data.hvac, stack: 'total', itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] } },
      { name: 'Lighting', type: 'bar', data: data.lighting, stack: 'total', itemStyle: { color: '#67C23A', borderRadius: [4, 4, 0, 0] } },
      { name: 'Other', type: 'bar', data: data.other, stack: 'total', itemStyle: { color: '#E6A23C', borderRadius: [4, 4, 0, 0] } }
    ]
  })
}

const initHVACChart = () => {
  if (!hvacChartRef.value) return

  hvacChart = echarts.init(hvacChartRef.value)
  hvacChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c})' },
    legend: { orient: 'vertical', left: 'left', data: ['AHU', 'Chiller', 'VAV', 'Cooling Tower', 'Pump'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { name: 'AHU', value: 45, itemStyle: { color: '#409EFF' } },
        { name: 'Chiller', value: 32, itemStyle: { color: '#67C23A' } },
        { name: 'VAV', value: 12, itemStyle: { color: '#E6A23C' } },
        { name: 'Cooling Tower', value: 6, itemStyle: { color: '#F56C6C' } },
        { name: 'Pump', value: 5, itemStyle: { color: '#909399' } }
      ],
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })
}

const handleResize = () => {
  tempChart?.resize()
  energyChart?.resize()
  hvacChart?.resize()
}

// ==================== Actions ====================
const formatTime = (time: string) => {
  return time
}

const formatEnergy = (kwh: number) => {
  return `${kwh.toLocaleString()} kWh`
}

const formatCost = (cost: number) => {
  return `$${cost.toLocaleString()}`
}

const toggleChartPeriod = () => {
  currentChartPeriod.value = currentChartPeriod.value === 'week' ? 'month' : 'week'
  updateTempChart()
  updateEnergyChart()
}

const syncDevices = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1500))
    ElMessage.success('BMS device synchronization completed successfully')
  } catch (error) {
    ElMessage.error('Sync failed')
  } finally {
    loading.value = false
  }
}

const testConnection = async () => {
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('BMS platform connection successful')
  } catch (error) {
    ElMessage.error('Connection failed')
  }
}

const openConfigDrawer = () => {
  configDrawerVisible.value = true
}

const saveConfig = async () => {
  try {
    await new Promise(resolve => setTimeout(resolve, 800))
    ElMessage.success('Configuration saved successfully')
    configDrawerVisible.value = false
  } catch (error) {
    ElMessage.error('Failed to save configuration')
  }
}

const viewDeviceDetails = (device: any) => {
  selectedDevice.value = device
  deviceDetailVisible.value = true
}

const openSetpointControl = (device: any) => {
  selectedDevice.value = device
  setpointForm.value = {
    deviceId: device.id,
    setpoint: device.setpoint || 0,
    reason: ''
  }
  setpointVisible.value = true
}

const saveSetpoint = async () => {
  if (selectedDevice.value) {
    ElMessage.info(`Adjusting setpoint for ${selectedDevice.value.name} to ${setpointForm.value.setpoint}...`)
    await new Promise(resolve => setTimeout(resolve, 1000))
    selectedDevice.value.setpoint = setpointForm.value.setpoint
    ElMessage.success(`Setpoint updated successfully`)
    setpointVisible.value = false
  }
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getDeviceIcon = (type: string) => {
  const icons: Record<string, any> = {
    'AHU': WindPower,
    'Chiller': Temperature,
    'VAV': DataLine,
    'Cooling Tower': Water,
    'Lighting': Sunny,
    'Temperature': Temperature,
    'Humidity': Water,
    'CO2': WindPower,
    'Power': Lightning,
    'Boiler': Temperature,
    'Pump': Water
  }
  return icons[type] || Monitor
}

const getStatusColor = (value: number, unit: string, setpoint: number | null) => {
  if (!setpoint) return '#67C23A'
  const diff = Math.abs(value - setpoint)
  if (diff <= 1) return '#67C23A'
  if (diff <= 3) return '#E6A23C'
  return '#F56C6C'
}
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
          <span class="loading-title">Loading BMS Platform</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Building Management System Adapter</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="bms-platform-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h2>BMS Platform Adapter</h2>
        <el-tag type="success" effect="dark">Connected</el-tag>
      </div>
      <div class="header-stats">
        <el-tag type="info" effect="plain">BACnet/IP | Modbus/TCP</el-tag>
      </div>
    </div>

    <!-- Stat Cards Row 1 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon building-icon">
            <el-icon><HomeFilled /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalBuildings }}</div>
            <div class="stat-label">Buildings</div>
            <div class="stat-sub-value">All Online</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon hvac-icon">
            <el-icon><WindPower /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.onlineHVAC }}/{{ stats.totalHVAC }}</div>
            <div class="stat-label">HVAC Systems</div>
            <div class="stat-trend">
              <el-progress :percentage="(stats.onlineHVAC / stats.totalHVAC) * 100" :color="'#67C23A'" :stroke-width="6" />
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon lighting-icon">
            <el-icon><Sunny /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.onlineLighting }}/{{ stats.totalLighting }}</div>
            <div class="stat-label">Lighting Systems</div>
            <div class="stat-trend">
              <el-progress :percentage="(stats.onlineLighting / stats.totalLighting) * 100" :color="'#E6A23C'" :stroke-width="6" />
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon sensor-icon">
            <el-icon><DataLine /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.onlineSensors }}/{{ stats.totalSensors }}</div>
            <div class="stat-label">Sensors</div>
            <div class="stat-sub-value">{{ stats.co2Reduction }}% CO₂ Reduction</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Stat Cards Row 2 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon energy-icon">
            <el-icon><Lightning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ formatEnergy(stats.todayEnergyKWh) }}</div>
            <div class="stat-label">Today's Energy</div>
            <div class="stat-trend">
              <span class="energy-text">Peak: 1,450 kW</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon cost-icon">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ formatCost(stats.energyCost) }}</div>
            <div class="stat-label">Monthly Cost</div>
            <div class="stat-sub-value">@ $0.15/kWh</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon meter-icon">
            <el-icon><Monitor /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalEnergyMeters }}</div>
            <div class="stat-label">Energy Meters</div>
            <div class="stat-sub-value">{{ formatEnergy(stats.monthEnergyKWh) }} Monthly</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon efficiency-icon">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">87.5%</div>
            <div class="stat-label">System Efficiency</div>
            <div class="stat-trend">
              <el-progress :percentage="87.5" :color="'#67C23A'" :stroke-width="6" />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Zone Status Cards -->
    <el-row :gutter="20" class="zone-row">
      <el-col :span="6" v-for="zone in zones" :key="zone.name">
        <el-card shadow="hover" class="zone-card">
          <div class="zone-header">
            <span class="zone-name">{{ zone.name }}</span>
          </div>
          <div class="zone-metrics">
            <div class="metric">
              <el-icon><WindPower /></el-icon>
              <span>{{ zone.temp }}°C</span>
            </div>
            <div class="metric">
              <el-icon><HomeFilled /></el-icon>
              <span>{{ zone.humidity }}%</span>
            </div>
            <div class="metric">
              <el-icon><WindPower /></el-icon>
              <span>{{ zone.co2 }} ppm</span>
            </div>
          </div>
          <el-progress :percentage="zone.occupancy" :color="zone.occupancy > 80 ? '#F56C6C' : '#67C23A'" :stroke-width="6" />
          <div class="occupancy-label">Occupancy: {{ zone.occupancy }}%</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Chart Section -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Temperature Trends</span>
              <el-button text type="primary" @click="toggleChartPeriod">
                {{ currentChartPeriod === 'week' ? 'This Week' : 'This Month' }}
              </el-button>
            </div>
          </template>
          <div ref="tempChartRef" class="chart" style="height: 280px"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Energy Consumption by System</span>
              <el-button text type="primary" @click="syncDevices">Refresh</el-button>
            </div>
          </template>
          <div ref="energyChartRef" class="chart" style="height: 280px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>HVAC Device Distribution</span>
              <el-button text type="primary">Details</el-button>
            </div>
          </template>
          <div ref="hvacChartRef" class="chart" style="height: 280px"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="never" class="alerts-card">
          <template #header>
            <div class="card-header">
              <span>Recent Alerts</span>
              <el-button text type="primary">View All</el-button>
            </div>
          </template>
          <div class="alerts-list">
            <div class="alert-item warning">
              <el-icon><Warning /></el-icon>
              <span>VAV-102 offline since 2024-01-14 18:30</span>
            </div>
            <div class="alert-item info">
              <el-icon><BellFilled /></el-icon>
              <span>High CO2 detected in Zone D (440 ppm)</span>
            </div>
            <div class="alert-item success">
              <el-icon><SuccessFilled /></el-icon>
              <span>Energy savings achieved: 12.5% this month</span>
            </div>
            <div class="alert-item warning">
              <el-icon><Warning /></el-icon>
              <span>Chiller-2 efficiency below threshold</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Devices Table -->
    <el-card shadow="never" class="device-table-card">
      <template #header>
        <div class="table-header">
          <span>BMS Devices & Points</span>
          <div class="table-actions">
            <el-input
                v-model="searchKeyword"
                placeholder="Search devices..."
                :prefix-icon="Search"
                style="width: 220px"
                clearable
            />
            <el-button type="primary" @click="syncDevices" :loading="loading">
              <el-icon><Refresh /></el-icon>
              Sync Devices
            </el-button>
            <el-button @click="openConfigDrawer">
              <el-icon><Setting /></el-icon>
              Platform Settings
            </el-button>
            <el-button @click="testConnection">
              <el-icon><Connection /></el-icon>
              Test Connection
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredDevices" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="Device ID" width="90" />
        <el-table-column prop="name" label="Device Name" min-width="150" />
        <el-table-column prop="location" label="Location" width="160" />
        <el-table-column prop="type" label="Type" width="110" />
        <el-table-column label="Value" width="100" align="center">
          <template #default="{ row }">
            <span :style="{ color: getStatusColor(row.value, row.unit, row.setpoint), fontWeight: 'bold' }">
              {{ row.value }} {{ row.unit }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Setpoint" width="80" align="center">
          <template #default="{ row }">
            <span v-if="row.setpoint !== null">{{ row.setpoint }} {{ row.unit }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'online' ? 'success' : 'danger'" size="small">
              {{ row.status === 'online' ? 'Online' : 'Offline' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="energy" label="Energy (kWh)" width="100" align="center">
          <template #default="{ row }">
            {{ row.energy !== null ? row.energy : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDeviceDetails(row)">
              Details
            </el-button>
            <el-button
                v-if="row.setpoint !== null"
                link type="warning"
                size="small"
                @click="openSetpointControl(row)"
            >
              Setpoint
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- Device Details Dialog -->
    <el-dialog v-model="deviceDetailVisible" :title="`Device Details - ${selectedDevice?.name}`" width="550px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Device ID">{{ selectedDevice?.id }}</el-descriptions-item>
        <el-descriptions-item label="Device Name">{{ selectedDevice?.name }}</el-descriptions-item>
        <el-descriptions-item label="Type">{{ selectedDevice?.type }}</el-descriptions-item>
        <el-descriptions-item label="Location">{{ selectedDevice?.location }}</el-descriptions-item>
        <el-descriptions-item label="Controller">{{ selectedDevice?.controller }}</el-descriptions-item>
        <el-descriptions-item label="IP Address">{{ selectedDevice?.ip || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="Current Value">
          <span :style="{ color: getStatusColor(selectedDevice?.value, selectedDevice?.unit, selectedDevice?.setpoint), fontWeight: 'bold' }">
            {{ selectedDevice?.value }} {{ selectedDevice?.unit }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="Setpoint">
          {{ selectedDevice?.setpoint !== null ? `${selectedDevice?.setpoint} ${selectedDevice?.unit}` : 'N/A' }}
        </el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="selectedDevice?.status === 'online' ? 'success' : 'danger'" size="small">
            {{ selectedDevice?.status === 'online' ? 'Online' : 'Offline' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Last Heartbeat">{{ selectedDevice?.lastHeartbeat }}</el-descriptions-item>
        <el-descriptions-item label="Energy Consumption" :span="2" v-if="selectedDevice?.energy">
          {{ selectedDevice?.energy }} kWh
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button type="primary" @click="deviceDetailVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Setpoint Control Dialog -->
    <el-dialog v-model="setpointVisible" :title="`Setpoint Control - ${selectedDevice?.name}`" width="450px">
      <el-form :model="setpointForm" label-width="100px">
        <el-form-item :label="`Setpoint (${selectedDevice?.unit})`">
          <el-input-number
              v-model="setpointForm.setpoint"
              :min="selectedDevice?.type === 'Temperature' ? 16 : 0"
              :max="selectedDevice?.type === 'Temperature' ? 30 : 100"
              :step="0.5"
          />
        </el-form-item>
        <el-form-item label="Reason">
          <el-input v-model="setpointForm.reason" type="textarea" rows="2" placeholder="Reason for adjustment" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="setpointVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveSetpoint">Apply Setpoint</el-button>
      </template>
    </el-dialog>

    <!-- Platform Configuration Drawer -->
    <el-drawer v-model="configDrawerVisible" title="Platform Configuration" direction="rtl" size="500px">
      <el-form :model="platformConfig" label-width="140px">
        <el-form-item label="Platform URL">
          <el-input v-model="platformConfig.host" placeholder="https://your-bms-platform.com" />
        </el-form-item>
        <el-form-item label="API Key">
          <el-input v-model="platformConfig.apiKey" placeholder="Enter API key" />
        </el-form-item>
        <el-divider>Protocol Settings</el-divider>
        <el-form-item label="BACnet Port">
          <el-input-number v-model="platformConfig.bacnetPort" :min="1024" :max="65535" />
        </el-form-item>
        <el-form-item label="Modbus Port">
          <el-input-number v-model="platformConfig.modbusPort" :min="1024" :max="65535" />
        </el-form-item>
        <el-form-item label="Sync Interval (s)">
          <el-input-number v-model="platformConfig.syncInterval" :min="60" :max="3600" />
        </el-form-item>
        <el-form-item label="Temperature Unit">
          <el-select v-model="platformConfig.tempUnit">
            <el-option label="Celsius" value="celsius" />
            <el-option label="Fahrenheit" value="fahrenheit" />
          </el-select>
        </el-form-item>
        <el-divider>Alarm Thresholds</el-divider>
        <el-form-item label="High Temperature">
          <el-input-number v-model="platformConfig.alarmThresholds.tempHigh" :min="20" :max="40" /> °C
        </el-form-item>
        <el-form-item label="Low Temperature">
          <el-input-number v-model="platformConfig.alarmThresholds.tempLow" :min="10" :max="20" /> °C
        </el-form-item>
        <el-form-item label="High Humidity">
          <el-input-number v-model="platformConfig.alarmThresholds.humidityHigh" :min="50" :max="90" /> %
        </el-form-item>
        <el-form-item label="High CO2">
          <el-input-number v-model="platformConfig.alarmThresholds.co2High" :min="500" :max="2000" /> ppm
        </el-form-item>
        <el-divider>Energy Settings</el-divider>
        <el-form-item label="Energy Cost Rate">
          <el-input-number v-model="platformConfig.energyCostRate" :min="0.05" :max="0.50" :step="0.01" /> $/kWh
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveConfig">Save Configuration</el-button>
          <el-button @click="testConnection">Test Connection</el-button>
        </el-form-item>
      </el-form>
    </el-drawer>
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

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ==================== Main Content ==================== */
.bms-platform-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e4e7ed;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  color: #303133;
}

.stat-cards {
  margin: 20px 0;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 10px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
}

.building-icon {
  background-color: #e6f7ff;
  color: #409eff;
}

.hvac-icon {
  background-color: #f0f9ff;
  color: #67c23a;
}

.lighting-icon {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.sensor-icon {
  background-color: #fef0f0;
  color: #f56c6c;
}

.energy-icon {
  background-color: #e8f8f5;
  color: #1abc9c;
}

.cost-icon {
  background-color: #f3e8ff;
  color: #9b59b6;
}

.meter-icon {
  background-color: #e8f4fd;
  color: #3498db;
}

.efficiency-icon {
  background-color: #fdeded;
  color: #e74c3c;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.stat-sub-value {
  font-size: 12px;
  color: #67c23a;
  margin-top: 2px;
}

.stat-trend {
  margin-top: 8px;
}

.energy-text {
  font-size: 12px;
  color: #e6a23c;
}

.zone-row {
  margin-bottom: 20px;
}

.zone-card {
  text-align: center;
}

.zone-header {
  margin-bottom: 15px;
}

.zone-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.zone-metrics {
  display: flex;
  justify-content: space-around;
  margin-bottom: 15px;
}

.metric {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  color: #606266;
}

.occupancy-label {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
  text-align: center;
}

.chart-row {
  margin-bottom: 20px;
}

.chart-card,
.alerts-card {
  height: 360px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alerts-list {
  max-height: 280px;
  overflow-y: auto;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
  font-size: 13px;
}

.alert-item.warning {
  color: #e6a23c;
}

.alert-item.info {
  color: #409eff;
}

.alert-item.success {
  color: #67c23a;
}

.alert-item:last-child {
  border-bottom: none;
}

.device-table-card {
  margin-top: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.table-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.chart {
  width: 100%;
}

:deep(.el-card__header) {
  border-bottom: 1px solid #ebeef5;
  padding: 15px 20px;
}

:deep(.el-card__body) {
  padding: 20px;
}

@media (max-width: 1200px) {
  .table-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .table-actions {
    width: 100%;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .zone-metrics {
    flex-direction: column;
    gap: 8px;
  }
}
</style>