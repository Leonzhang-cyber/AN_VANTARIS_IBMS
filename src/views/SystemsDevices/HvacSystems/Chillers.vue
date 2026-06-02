<template>
  <!-- Global Pre Loading Screen -->
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
        <div class="loading-tip">CHILLER PLANT VISUALIZATION</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Page Content -->
  <div v-else class="chillers-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/systems-devices/device-inventory' }">
            Systems & Devices
          </el-breadcrumb-item>
          <el-breadcrumb-item>HVAC Systems</el-breadcrumb-item>
          <el-breadcrumb-item>Chiller Plant</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button :icon="Refresh" @click="refreshData" :loading="refreshing">Refresh</el-button>
        <el-button type="primary" :icon="Download" @click="exportReport">Export Report</el-button>
      </div>
    </div>

    <!-- Plant Overview Cards -->
    <div class="plant-overview">
      <div class="overview-card">
        <div class="overview-icon"><el-icon><ColdDrink /></el-icon></div>
        <div class="overview-info">
          <span class="overview-value">{{ chillers.length }}</span>
          <span class="overview-label">Total Chillers</span>
        </div>
      </div>
      <div class="overview-card">
        <div class="overview-icon running"><el-icon><CircleCheckFilled /></el-icon></div>
        <div class="overview-info">
          <span class="overview-value">{{ runningCount }}</span>
          <span class="overview-label">Running</span>
        </div>
        <div class="overview-trend up">{{ runningPercent }}%</div>
      </div>
      <div class="overview-card">
        <div class="overview-icon"><el-icon><DataLine /></el-icon></div>
        <div class="overview-info">
          <span class="overview-value">{{ totalCapacity.toFixed(0) }}</span>
          <span class="overview-label">Total Capacity (RT)</span>
        </div>
      </div>
      <div class="overview-card">
        <div class="overview-icon"><el-icon><TrendCharts /></el-icon></div>
        <div class="overview-info">
          <span class="overview-value">{{ avgEfficiency }}</span>
          <span class="overview-label">Avg Efficiency (kW/RT)</span>
        </div>
      </div>
    </div>

    <!-- Chiller Plant Visualization -->
    <div class="plant-visualization">
      <div class="plant-title">
        <h3><el-icon><OfficeBuilding /></el-icon> Central Chiller Plant - Layout</h3>
        <div class="plant-legend">
          <span><span class="legend-dot running"></span> Running</span>
          <span><span class="legend-dot standby"></span> Standby</span>
          <span><span class="legend-dot maintenance"></span> Maintenance</span>
          <span><span class="legend-dot offline"></span> Offline</span>
        </div>
      </div>

      <div class="chiller-grid">
        <div v-for="chiller in chillers" :key="chiller.id" class="chiller-unit" :class="chiller.status" @click="selectChiller(chiller)">
          <div class="chiller-image">
            <!-- 图片URL请在这里填写 -->
            <img :src="chillerImages[chiller.status]" :alt="chiller.name" class="chiller-img" @error="handleImageError">
            <div class="status-badge" :class="chiller.status"></div>
          </div>
          <div class="chiller-info">
            <h4 class="chiller-name">{{ chiller.name }}</h4>
            <p class="chiller-location"><el-icon><Location /></el-icon> {{ chiller.location }}</p>
            <p class="chiller-model">{{ chiller.manufacturer }} {{ chiller.model }}</p>
          </div>
          <div class="chiller-metrics">
            <div class="metric">
              <span class="metric-label">Capacity</span>
              <span class="metric-value">{{ chiller.capacity }} RT</span>
            </div>
            <div class="metric">
              <span class="metric-label">Load</span>
              <span class="metric-value" :class="getLoadClass(chiller.currentLoad)">{{ chiller.currentLoad }}%</span>
            </div>
            <div class="metric">
              <span class="metric-label">Efficiency</span>
              <span class="metric-value">{{ chiller.efficiency }} kW/RT</span>
            </div>
          </div>
          <div class="chiller-footer">
            <el-progress :percentage="chiller.currentLoad" :stroke-width="6" :color="getLoadColor(chiller.currentLoad)" :show-text="false" />
            <div class="chiller-actions">
              <el-button size="small" text @click.stop="viewDetail(chiller)">Details</el-button>
              <el-button size="small" text type="primary" @click.stop="controlChiller(chiller)">Control</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Chiller Location Map -->
    <div class="location-section">
      <el-card class="location-card" shadow="hover">
        <template #header>
          <div class="card-header-title">
            <span><el-icon><Location /></el-icon> Chiller Locations</span>
          </div>
        </template>
        <div class="location-list">
          <div v-for="location in locations" :key="location.name" class="location-item">
            <div class="location-header">
              <el-icon><OfficeBuilding /></el-icon>
              <span class="location-name">{{ location.name }}</span>
              <el-tag :type="location.status === 'all' ? 'success' : 'warning'" size="small">{{ location.chillers.length }} units</el-tag>
            </div>
            <div class="location-chillers">
              <div v-for="chiller in location.chillers" :key="chiller.id" class="location-chiller" @click="selectChiller(chiller)">
                <span class="chiller-status-dot" :class="chiller.status"></span>
                <span class="chiller-name">{{ chiller.name }}</span>
                <span class="chiller-load">{{ chiller.currentLoad }}%</span>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <el-card class="performance-card" shadow="hover">
        <template #header>
          <div class="card-header-title">
            <span><el-icon><TrendCharts /></el-icon> Plant Performance</span>
          </div>
        </template>
        <div ref="performanceChartRef" class="performance-chart"></div>
      </el-card>
    </div>

    <!-- Chiller Details Drawer -->
    <el-drawer v-model="detailDrawerVisible" :title="selectedChiller?.name" size="40%" direction="rtl">
      <div v-if="selectedChiller" class="chiller-detail">
        <div class="detail-header">
          <div class="detail-status" :class="selectedChiller.status">
            <span class="status-dot-large"></span>
            <span>{{ selectedChiller.status.toUpperCase() }}</span>
          </div>
          <h2>{{ selectedChiller.name }}</h2>
          <p>{{ selectedChiller.manufacturer }} {{ selectedChiller.model }}</p>
        </div>

        <el-divider />

        <div class="detail-metrics">
          <div class="metric-row">
            <div class="metric-card">
              <span class="metric-label">Cooling Capacity</span>
              <span class="metric-value">{{ selectedChiller.capacity }} <span class="metric-unit">RT</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Current Load</span>
              <span class="metric-value" :class="getLoadClass(selectedChiller.currentLoad)">{{ selectedChiller.currentLoad }}<span class="metric-unit">%</span></span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Efficiency</span>
              <span class="metric-value">{{ selectedChiller.efficiency }} <span class="metric-unit">kW/RT</span></span>
            </div>
          </div>
          <div class="metric-row">
            <div class="metric-card">
              <span class="metric-label">Evaporator</span>
              <span class="metric-value">{{ selectedChiller.evapTemp }}°C / {{ selectedChiller.evapPress }} kPa</span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Condenser</span>
              <span class="metric-value">{{ selectedChiller.condTemp }}°C / {{ selectedChiller.condPress }} kPa</span>
            </div>
            <div class="metric-card">
              <span class="metric-label">Energy Today</span>
              <span class="metric-value">{{ selectedChiller.energyToday.toLocaleString() }} <span class="metric-unit">kWh</span></span>
            </div>
          </div>
        </div>

        <el-divider />

        <div class="detail-chart">
          <h4>24-Hour Performance Trend</h4>
          <div ref="detailChartRef" class="detail-chart-container"></div>
        </div>

        <el-divider />

        <div class="detail-actions">
          <el-button type="primary" @click="controlChiller(selectedChiller)">Control Chiller</el-button>
          <el-button @click="viewAlarms(selectedChiller)">View Alarms</el-button>
          <el-button @click="exportChillerData(selectedChiller)">Export Data</el-button>
        </div>
      </div>
    </el-drawer>

    <!-- Control Dialog -->
    <el-dialog v-model="controlDialogVisible" :title="`Control - ${selectedChiller?.name}`" width="450px">
      <el-form :model="controlForm" label-width="120px">
        <el-form-item label="Operation Mode">
          <el-radio-group v-model="controlForm.mode">
            <el-radio label="auto">Auto</el-radio>
            <el-radio label="manual">Manual</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Setpoint (°C)">
          <el-input-number v-model="controlForm.setpoint" :min="4" :max="12" :step="0.5" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Capacity Limit">
          <el-slider v-model="controlForm.capacityLimit" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="Commands">
          <el-button-group>
            <el-button type="success" @click="sendCommand('start')" :disabled="selectedChiller?.status === 'running'">Start</el-button>
            <el-button type="warning" @click="sendCommand('stop')" :disabled="selectedChiller?.status !== 'running'">Stop</el-button>
          </el-button-group>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { Refresh, Download, ColdDrink, CircleCheckFilled, DataLine, TrendCharts, OfficeBuilding, Location } from '@element-plus/icons-vue'

// ========== Loading State ==========
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading chiller plant...')
const loadingMessages = [
  'Initializing chiller plant visualization...',
  'Loading chiller data...',
  'Connecting to BMS...',
  'Rendering plant layout...',
  'Almost ready...'
]

// ========== Chart References ==========
const performanceChartRef = ref<HTMLDivElement | null>(null)
const detailChartRef = ref<HTMLDivElement | null>(null)
let performanceChart: echarts.ECharts | null = null
let detailChart: echarts.ECharts | null = null
let refreshTimer: number | null = null
const refreshing = ref(false)

// ========== Chiller Images ==========
// 请在这里填写您的图片URL
const chillerImages = {
  running: '',      // 填写运行状态图片URL
  standby: '',      // 填写待机状态图片URL
  maintenance: '',  // 填写维护状态图片URL
  offline: '',      // 填写离线状态图片URL
  default: ''       // 填写默认图片URL
}

// 图片加载错误处理
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  if (chillerImages.default) {
    img.src = chillerImages.default
  } else {
    // 如果没有默认图片，显示一个SVG占位符
    img.src = 'https://aegisnx.com/wp-content/uploads/2026/05/52013146723.webp'
  }
}

// ========== Dialog State ==========
const detailDrawerVisible = ref(false)
const controlDialogVisible = ref(false)
const selectedChiller = ref<any>(null)
const controlForm = reactive({
  mode: 'auto',
  setpoint: 7,
  capacityLimit: 80
})

// ========== Chiller Data ==========
interface Chiller {
  id: string
  name: string
  manufacturer: string
  model: string
  status: 'running' | 'standby' | 'maintenance' | 'offline'
  capacity: number
  currentLoad: number
  efficiency: number
  evapTemp: number
  evapPress: number
  condTemp: number
  condPress: number
  energyToday: number
  energyMonth: number
  location: string
}

const chillers = ref<Chiller[]>([
  { id: '1', name: 'Chiller-01', manufacturer: 'Carrier', model: 'AquaEdge 19XR', status: 'running', capacity: 800, currentLoad: 72, efficiency: 0.62, evapTemp: 6.2, evapPress: 350, condTemp: 32.5, condPress: 820, energyToday: 12500, energyMonth: 375000, location: 'Basement B2' },
  { id: '2', name: 'Chiller-02', manufacturer: 'Trane', model: 'CenTraVac CVHE', status: 'running', capacity: 650, currentLoad: 58, efficiency: 0.58, evapTemp: 5.8, evapPress: 320, condTemp: 31.2, condPress: 780, energyToday: 9800, energyMonth: 294000, location: 'Basement B2' },
  { id: '3', name: 'Chiller-03', manufacturer: 'Daikin', model: 'EWYQ', status: 'standby', capacity: 550, currentLoad: 0, efficiency: 0.60, evapTemp: 7.0, evapPress: 340, condTemp: 30.5, condPress: 760, energyToday: 0, energyMonth: 0, location: 'Basement B2' },
  { id: '4', name: 'Chiller-04', manufacturer: 'Johnson Controls', model: 'York YK', status: 'maintenance', capacity: 700, currentLoad: 0, efficiency: 0.65, evapTemp: 8.0, evapPress: 360, condTemp: 33.0, condPress: 850, energyToday: 0, energyMonth: 150000, location: 'Basement B2' },
  { id: '5', name: 'Roof Chiller', manufacturer: 'Carrier', model: 'AquaSnap 30XA', status: 'running', capacity: 500, currentLoad: 45, efficiency: 0.55, evapTemp: 6.5, evapPress: 330, condTemp: 31.8, condPress: 790, energyToday: 6200, energyMonth: 186000, location: 'Roof' },
  { id: '6', name: 'Backup Chiller', manufacturer: 'Mitsubishi', model: 'CITY MULTI', status: 'offline', capacity: 400, currentLoad: 0, efficiency: 0.61, evapTemp: 7.2, evapPress: 345, condTemp: 32.0, condPress: 800, energyToday: 0, energyMonth: 0, location: 'Mechanical Room' }
])

// 按位置分组
const locations = computed(() => {
  const locationMap = new Map<string, Chiller[]>()
  chillers.value.forEach(chiller => {
    if (!locationMap.has(chiller.location)) {
      locationMap.set(chiller.location, [])
    }
    locationMap.get(chiller.location)!.push(chiller)
  })

  const result: { name: string; chillers: Chiller[]; status: string }[] = []
  locationMap.forEach((chillers, name) => {
    const hasOffline = chillers.some(c => c.status === 'offline' || c.status === 'maintenance')
    result.push({ name, chillers, status: hasOffline ? 'warning' : 'all' })
  })
  return result
})

// 统计数据
const runningCount = computed(() => chillers.value.filter(c => c.status === 'running').length)
const runningPercent = computed(() => chillers.value.length ? Math.round(runningCount.value / chillers.value.length * 100) : 0)
const totalCapacity = computed(() => chillers.value.reduce((sum, c) => sum + c.capacity, 0))
const avgEfficiency = computed(() => {
  const running = chillers.value.filter(c => c.status === 'running')
  if (running.length === 0) return '0.00'
  const avg = running.reduce((sum, c) => sum + c.efficiency, 0) / running.length
  return avg.toFixed(2)
})

// Helper Functions
const getLoadClass = (load: number) => {
  if (load < 30) return 'load-low'
  if (load < 70) return 'load-medium'
  return 'load-high'
}

const getLoadColor = (load: number) => {
  if (load < 30) return '#67c23a'
  if (load < 70) return '#409eff'
  return '#e6a23c'
}

// 生成性能趋势数据
const generatePerformanceData = () => {
  const timestamps = []
  const totalLoad = []
  const efficiency = []
  const now = new Date()

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    timestamps.push(`${String(time.getHours()).padStart(2, '0')}:00`)

    const loadVariation = Math.sin(i * 0.3) * 15 + 50
    totalLoad.push(Math.min(100, Math.max(20, Number(loadVariation.toFixed(1)))))

    const effVariation = 0.62 + Math.sin(i * 0.2) * 0.05 + (Math.random() - 0.5) * 0.02
    efficiency.push(Number(effVariation.toFixed(3)))
  }

  return { timestamps, totalLoad, efficiency }
}

// 初始化性能图表
const initPerformanceChart = async () => {
  await nextTick()
  if (!performanceChartRef.value) {
    setTimeout(() => initPerformanceChart(), 100)
    return
  }

  if (performanceChart) performanceChart.dispose()
  performanceChart = echarts.init(performanceChartRef.value)

  const data = generatePerformanceData()

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Total Plant Load (%)', 'Average Efficiency (kW/RT)'], bottom: 0 },
    grid: { top: 30, right: 20, bottom: 40, left: 50, containLabel: true },
    xAxis: { type: 'category', data: data.timestamps, axisLabel: { rotate: 45, interval: 4, fontSize: 10 } },
    yAxis: [
      { type: 'value', name: 'Load (%)', min: 0, max: 100, position: 'left' },
      { type: 'value', name: 'Efficiency (kW/RT)', position: 'right', min: 0.4, max: 0.8 }
    ],
    series: [
      { name: 'Total Plant Load (%)', type: 'line', data: data.totalLoad, smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Average Efficiency (kW/RT)', type: 'line', yAxisIndex: 1, data: data.efficiency, smooth: true, lineStyle: { color: '#67c23a', width: 2 } }
    ]
  }
  performanceChart.setOption(option)
}

// 生成单个制冷机趋势数据
const generateChillerTrendData = (chiller: Chiller) => {
  const timestamps = []
  const load = []
  const efficiency = []
  const now = new Date()

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    timestamps.push(`${String(time.getHours()).padStart(2, '0')}:00`)

    const loadVariation = chiller.currentLoad + Math.sin(i * 0.3) * 15 + (Math.random() - 0.5) * 5
    load.push(Math.min(100, Math.max(0, Number(loadVariation.toFixed(1)))))

    const effVariation = chiller.efficiency + Math.sin(i * 0.2) * 0.03 + (Math.random() - 0.5) * 0.01
    efficiency.push(Number(effVariation.toFixed(3)))
  }

  return { timestamps, load, efficiency }
}

// 初始化详情图表
const initDetailChart = () => {
  if (!detailChartRef.value || !selectedChiller.value) return
  if (detailChart) detailChart.dispose()

  detailChart = echarts.init(detailChartRef.value)
  const data = generateChillerTrendData(selectedChiller.value)

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Load (%)', 'Efficiency (kW/RT)'], bottom: 0 },
    grid: { top: 30, right: 20, bottom: 40, left: 50, containLabel: true },
    xAxis: { type: 'category', data: data.timestamps, axisLabel: { rotate: 45, interval: 4, fontSize: 10 } },
    yAxis: [
      { type: 'value', name: 'Load (%)', min: 0, max: 100, position: 'left' },
      { type: 'value', name: 'Efficiency (kW/RT)', position: 'right' }
    ],
    series: [
      { name: 'Load (%)', type: 'line', data: data.load, smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Efficiency (kW/RT)', type: 'line', yAxisIndex: 1, data: data.efficiency, smooth: true, lineStyle: { color: '#67c23a', width: 2 } }
    ]
  }
  detailChart.setOption(option)
}

// 更新实时数据
const updateRealtimeData = () => {
  for (const chiller of chillers.value) {
    if (chiller.status === 'running') {
      const change = (Math.random() - 0.5) * 3
      let newLoad = chiller.currentLoad + change
      newLoad = Math.max(20, Math.min(95, newLoad))
      chiller.currentLoad = Number(newLoad.toFixed(1))

      const energyIncrement = chiller.capacity * (chiller.currentLoad / 100) * 0.25
      chiller.energyToday += energyIncrement
      chiller.energyMonth += energyIncrement

      const effChange = (Math.random() - 0.5) * 0.01
      chiller.efficiency = Number((chiller.efficiency + effChange).toFixed(3))

      chiller.evapTemp = Number((chiller.evapTemp + (Math.random() - 0.5) * 0.2).toFixed(1))
      chiller.condTemp = Number((chiller.condTemp + (Math.random() - 0.5) * 0.2).toFixed(1))
    }
  }
}

// 刷新性能图表
const updatePerformanceChart = () => {
  if (!performanceChart) return
  const data = generatePerformanceData()
  performanceChart.setOption({
    xAxis: { data: data.timestamps },
    series: [{ data: data.totalLoad }, { data: data.efficiency }]
  })
}

// 窗口大小适配
const handleResize = () => {
  if (performanceChart) performanceChart.resize()
  if (detailChart) detailChart.resize()
}

// Actions
const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 500))
  updateRealtimeData()
  updatePerformanceChart()
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

const selectChiller = (chiller: Chiller) => {
  selectedChiller.value = chiller
  detailDrawerVisible.value = true
  setTimeout(() => initDetailChart(), 100)
}

const viewDetail = (chiller: Chiller) => {
  selectChiller(chiller)
}

const controlChiller = (chiller: Chiller) => {
  selectedChiller.value = chiller
  controlForm.setpoint = chiller.evapTemp + 1
  controlForm.capacityLimit = chiller.currentLoad
  controlDialogVisible.value = true
}

const sendCommand = (command: string) => {
  ElMessage.success(`${command.toUpperCase()} command sent to ${selectedChiller.value.name}`)
  if (command === 'start') {
    selectedChiller.value.status = 'running'
    selectedChiller.value.currentLoad = 30
  } else if (command === 'stop') {
    selectedChiller.value.status = 'standby'
    selectedChiller.value.currentLoad = 0
  }
  controlDialogVisible.value = false
  updatePerformanceChart()
}

const viewAlarms = (chiller: Chiller) => {
  ElMessage.info(`Viewing alarms for ${chiller.name}`)
}

const exportChillerData = (chiller: Chiller) => {
  ElMessage.success(`Exporting data for ${chiller.name}`)
}

const exportReport = () => {
  ElMessage.success('Exporting chiller plant report')
}

// 自动刷新
const startAutoRefresh = () => {
  refreshTimer = window.setInterval(() => {
    updateRealtimeData()
    updatePerformanceChart()
  }, 5000)
}

// ========== Lifecycle ==========
onMounted(async () => {
  let msgIdx = 0
  const msgInt = setInterval(() => {
    if (msgIdx < loadingMessages.length - 1) {
      msgIdx++
      loadingMessage.value = loadingMessages[msgIdx]
    }
  }, 400)

  const progInt = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)

  setTimeout(async () => {
    clearInterval(msgInt)
    clearInterval(progInt)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(async () => {
      isLoaded.value = true
      await nextTick()
      setTimeout(() => {
        initPerformanceChart()
        startAutoRefresh()
        window.addEventListener('resize', handleResize)
      }, 200)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
  if (performanceChart) performanceChart.dispose()
  if (detailChart) detailChart.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped lang="scss">
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

.loading-spinner { position: relative; width: 80px; height: 80px; margin: 0 auto 24px; }
.spinner-ring { position: absolute; width: 100%; height: 100%; border-radius: 50%; border: 3px solid transparent; animation: spin 1.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite; }
.spinner-ring:nth-child(1) { border-top-color: #3b82f6; animation-delay: 0s; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

.loading-text { margin-bottom: 24px; font-size: 28px; font-weight: 700; color: #e2e8f0; display: flex; justify-content: center; align-items: baseline; gap: 4px; }
.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce { 0%, 80%, 100% { transform: scale(0); opacity: 0.3; } 40% { transform: scale(1); opacity: 1; } }

.loading-progress { width: 280px; height: 4px; background: rgba(255, 255, 255, 0.1); border-radius: 4px; overflow: hidden; margin: 0 auto 16px; }
.progress-bar { height: 100%; background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec489a); border-radius: 4px; transition: width 0.3s ease; background-size: 200% auto; animation: shimmer 2s linear infinite; }
@keyframes shimmer { 0% { background-position: 0% 0%; } 100% { background-position: 200% 0%; } }

.loading-tip { font-size: 13px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 8px; font-weight: 500; }
.loading-subtip { font-size: 11px; color: #64748b; letter-spacing: 0.5px; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

/* Page Content */
.chillers-container { padding: 20px; background: #f5f7fa; min-height: 100%; }

.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }

.plant-overview { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 24px; }
.overview-card { background: white; border-radius: 16px; padding: 20px; display: flex; align-items: center; gap: 16px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); transition: all 0.3s ease; }
.overview-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
.overview-icon .el-icon { font-size: 36px; color: #409eff; }
.overview-icon.running .el-icon { color: #67c23a; }
.overview-info { flex: 1; }
.overview-value { font-size: 28px; font-weight: 700; color: #1e293b; }
.overview-label { font-size: 13px; color: #64748b; display: block; }
.overview-trend { font-size: 14px; font-weight: 600; }
.overview-trend.up { color: #67c23a; }

/* Plant Visualization */
.plant-visualization { background: white; border-radius: 20px; padding: 20px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.plant-title { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.plant-title h3 { display: flex; align-items: center; gap: 8px; margin: 0; font-size: 18px; }
.plant-legend { display: flex; gap: 20px; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 6px; }
.legend-dot.running { background: #67c23a; box-shadow: 0 0 4px #67c23a; }
.legend-dot.standby { background: #409eff; }
.legend-dot.maintenance { background: #e6a23c; }
.legend-dot.offline { background: #f56c6c; }

.chiller-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; }
.chiller-unit { background: #f8fafc; border-radius: 16px; padding: 16px; cursor: pointer; transition: all 0.3s ease; border-left: 4px solid; }
.chiller-unit.running { border-left-color: #67c23a; background: linear-gradient(135deg, #f8fafc, #f0fdf4); }
.chiller-unit.standby { border-left-color: #409eff; }
.chiller-unit.maintenance { border-left-color: #e6a23c; background: linear-gradient(135deg, #f8fafc, #fefce8); }
.chiller-unit.offline { border-left-color: #f56c6c; background: linear-gradient(135deg, #f8fafc, #fef2f2); opacity: 0.8; }
.chiller-unit:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); }

.chiller-image { position: relative; display: flex; justify-content: center; margin-bottom: 12px; }
.chiller-img { width: 100px; height: 100px; object-fit: contain; }
.status-badge { position: absolute; top: 0; right: 0; width: 12px; height: 12px; border-radius: 50%; }
.status-badge.running { background: #67c23a; box-shadow: 0 0 8px #67c23a; animation: pulse 2s infinite; }
.status-badge.standby { background: #409eff; }
.status-badge.maintenance { background: #e6a23c; }
.status-badge.offline { background: #f56c6c; }

.chiller-info { text-align: center; margin-bottom: 12px; }
.chiller-name { margin: 0 0 4px 0; font-size: 16px; font-weight: 600; color: #1e293b; }
.chiller-location { margin: 0; font-size: 11px; color: #64748b; display: flex; align-items: center; justify-content: center; gap: 4px; }
.chiller-model { margin: 4px 0 0 0; font-size: 11px; color: #94a3b8; }

.chiller-metrics { display: flex; justify-content: space-around; margin-bottom: 12px; padding: 8px 0; border-top: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0; }
.metric { text-align: center; }
.metric-label { display: block; font-size: 10px; color: #64748b; }
.metric-value { font-size: 14px; font-weight: 600; color: #1e293b; }
.metric-value.load-low { color: #67c23a; }
.metric-value.load-medium { color: #409eff; }
.metric-value.load-high { color: #e6a23c; }

.chiller-footer { margin-top: 8px; }
.chiller-actions { display: flex; justify-content: center; gap: 8px; margin-top: 8px; }

/* Location Section */
.location-section { display: grid; grid-template-columns: 1fr 1.5fr; gap: 20px; margin-bottom: 24px; }
.location-card, .performance-card { border-radius: 16px; }

.location-list { display: flex; flex-direction: column; gap: 16px; }
.location-item { border-bottom: 1px solid #e2e8f0; padding-bottom: 12px; }
.location-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.location-name { font-weight: 600; color: #1e293b; flex: 1; }
.location-chillers { display: flex; flex-wrap: wrap; gap: 8px; margin-left: 28px; }
.location-chiller { display: flex; align-items: center; gap: 6px; padding: 4px 8px; background: #f1f5f9; border-radius: 20px; cursor: pointer; transition: all 0.2s; font-size: 12px; }
.location-chiller:hover { background: #e2e8f0; }
.chiller-status-dot { width: 6px; height: 6px; border-radius: 50%; }
.chiller-status-dot.running { background: #67c23a; }
.chiller-status-dot.standby { background: #409eff; }
.chiller-status-dot.maintenance { background: #e6a23c; }
.chiller-status-dot.offline { background: #f56c6c; }
.chiller-load { font-size: 10px; color: #64748b; }

.performance-chart { width: 100%; height: 300px; }

/* Drawer Styles */
.chiller-detail { padding: 8px; }
.detail-header { text-align: center; margin-bottom: 16px; }
.detail-status { display: inline-flex; align-items: center; gap: 8px; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; margin-bottom: 12px; }
.detail-status.running { background: #f0fdf4; color: #67c23a; }
.detail-status.standby { background: #eff6ff; color: #409eff; }
.detail-status.maintenance { background: #fefce8; color: #e6a23c; }
.detail-status.offline { background: #fef2f2; color: #f56c6c; }
.status-dot-large { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.detail-status.running .status-dot-large { background: #67c23a; }
.detail-status.standby .status-dot-large { background: #409eff; }
.detail-status.maintenance .status-dot-large { background: #e6a23c; }
.detail-status.offline .status-dot-large { background: #f56c6c; }
.detail-header h2 { margin: 8px 0 4px 0; font-size: 20px; }
.detail-header p { margin: 0; color: #64748b; font-size: 13px; }

.detail-metrics { display: flex; flex-direction: column; gap: 12px; }
.metric-row { display: flex; gap: 12px; }
.metric-card { flex: 1; background: #f8fafc; border-radius: 12px; padding: 12px; text-align: center; }
.metric-card .metric-label { font-size: 11px; color: #64748b; display: block; margin-bottom: 4px; }
.metric-card .metric-value { font-size: 18px; font-weight: 700; color: #1e293b; }
.metric-unit { font-size: 12px; font-weight: normal; color: #64748b; }

.detail-chart { margin-top: 16px; }
.detail-chart h4 { margin: 0 0 12px 0; font-size: 14px; }
.detail-chart-container { width: 100%; height: 200px; }

.detail-actions { display: flex; gap: 12px; margin-top: 16px; flex-wrap: wrap; }

@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

@media (max-width: 1200px) {
  .plant-overview { grid-template-columns: repeat(2, 1fr); }
  .location-section { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .chillers-container { padding: 12px; }
  .plant-overview { grid-template-columns: 1fr; }
  .chiller-grid { grid-template-columns: 1fr; }
  .plant-title { flex-direction: column; align-items: flex-start; }
  .metric-row { flex-wrap: wrap; }
}
</style>