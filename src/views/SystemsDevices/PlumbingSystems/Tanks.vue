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
        <div class="loading-tip">Tank Storage Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="tanks-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Tanks</h2>
        <p class="header-subtitle">Storage Tank Monitoring | Level & Volume Control</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- System Overview Cards -->
    <el-row :gutter="20" class="overview-row">
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon total">
            <el-icon :size="28"><Grid /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Total Tanks</div>
            <div class="overview-value">{{ stats.total }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon capacity">
            <el-icon :size="28"><DataAnalysis /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Total Capacity</div>
            <div class="overview-value">{{ stats.totalCapacity }} <span class="unit">m³</span></div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon current">
            <el-icon :size="28"><DataLine /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Current Volume</div>
            <div class="overview-value">{{ stats.currentVolume }} <span class="unit">m³</span></div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon fill">
            <el-icon :size="28"><PieChart /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Avg Fill Level</div>
            <div class="overview-value">{{ stats.avgFillLevel }}<span class="unit">%</span></div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Tank Level Gauges Row -->
    <div class="section-title">
      <span>Tank Level Status</span>
      <el-select v-model="tankTypeFilter" size="small" style="width: 150px" placeholder="Filter by type" clearable>
        <el-option label="All Types" value="all" />
        <el-option label="Water Tank" value="Water" />
        <el-option label="Fuel Tank" value="Fuel" />
        <el-option label="Chemical Tank" value="Chemical" />
        <el-option label="Storage Tank" value="Storage" />
      </el-select>
    </div>

    <el-row :gutter="20" class="tanks-row">
      <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="tank in filteredTanks" :key="tank.id">
        <div class="tank-card" :class="getTankLevelClass(tank.fillPercentage)">
          <div class="tank-header">
            <span class="tank-name">{{ tank.name }}</span>
            <el-tag :type="getTankStatusTag(tank)" size="small">
              {{ getTankStatus(tank) }}
            </el-tag>
          </div>
          <div class="tank-icon">
            <el-icon :size="48"><House /></el-icon>
          </div>
          <div class="tank-level">
            <div class="level-label">Fill Level</div>
            <div class="level-value">{{ tank.fillPercentage }}%</div>
            <el-progress
                :percentage="tank.fillPercentage"
                :color="getLevelColor(tank.fillPercentage)"
                :stroke-width="12"
                :show-text="false"
            />
            <div class="level-detail">
              <span>{{ tank.currentVolume }} / {{ tank.capacity }} m³</span>
            </div>
          </div>
          <div class="tank-parameters">
            <div class="param">
              <span class="label">Liquid Type:</span>
              <span class="value">{{ tank.liquidType }}</span>
            </div>
            <div class="param">
              <span class="label">Temperature:</span>
              <span class="value" :class="getTempClass(tank.temperature)">{{ tank.temperature }}°C</span>
            </div>
            <div class="param">
              <span class="label">Pressure:</span>
              <span class="value">{{ tank.pressure }} bar</span>
            </div>
            <div class="param">
              <span class="label">Inflow Rate:</span>
              <span class="value">{{ tank.inflowRate }} m³/h</span>
            </div>
            <div class="param">
              <span class="label">Outflow Rate:</span>
              <span class="value">{{ tank.outflowRate }} m³/h</span>
            </div>
          </div>
          <div class="tank-actions">
            <el-button type="primary" size="small" @click="viewTankDetails(tank)">
              <el-icon><View /></el-icon>
              Details
            </el-button>
            <el-button type="warning" size="small" @click="showAlarmSettings(tank)" v-if="tank.fillPercentage > 90 || tank.fillPercentage < 10">
              <el-icon><Bell /></el-icon>
              Alarm
            </el-button>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Charts Row -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :md="14">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Level & Flow Trend (Last 24 Hours)</span>
              <el-radio-group v-model="chartPeriod" size="small" @change="updateTrendChart">
                <el-radio-button label="hour">Hourly</el-radio-button>
                <el-radio-button label="day">Daily</el-radio-button>
                <el-radio-button label="week">Weekly</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="10">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Capacity Distribution</span>
            </div>
          </template>
          <div ref="capacityChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Tank Details Table -->
    <el-card shadow="hover" class="table-card">
      <template #header>
        <div class="card-header">
          <span>Tank Details</span>
          <el-input v-model="searchText" placeholder="Search tank..." style="width: 200px" clearable>
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </template>
      <el-table :data="paginatedTanks" stripe border style="width: 100%">
        <el-table-column prop="name" label="Tank Name" min-width="150" />
        <el-table-column prop="liquidType" label="Liquid Type" min-width="120">
          <template #default="{ row }">
            <el-tag :type="getLiquidTypeTag(row.liquidType)" size="small">{{ row.liquidType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="capacity" label="Capacity (m³)" min-width="110" sortable />
        <el-table-column prop="currentVolume" label="Current Volume (m³)" min-width="130" sortable />
        <el-table-column prop="fillPercentage" label="Fill Level" min-width="150" sortable>
          <template #default="{ row }">
            <el-progress :percentage="row.fillPercentage" :color="getLevelColor(row.fillPercentage)" :stroke-width="8" />
          </template>
        </el-table-column>
        <el-table-column prop="temperature" label="Temp (°C)" min-width="100" sortable>
          <template #default="{ row }">
            <span :class="getTempClass(row.temperature)">{{ row.temperature }}°C</span>
          </template>
        </el-table-column>
        <el-table-column prop="pressure" label="Pressure (bar)" min-width="100" sortable />
        <el-table-column prop="inflowRate" label="Inflow (m³/h)" min-width="110" sortable />
        <el-table-column prop="outflowRate" label="Outflow (m³/h)" min-width="110" sortable />
        <el-table-column label="Status" min-width="100">
          <template #default="{ row }">
            <el-tag :type="getTankStatusTag(row)" size="small">{{ getTankStatus(row) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" fixed="right" min-width="120">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewTankDetails(row)">
              <el-icon><View /></el-icon>
              View
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredTableTanks.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Tank Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Tank Details - ${selectedTank?.name}`" width="600px">
      <el-descriptions :column="2" border v-if="selectedTank">
        <el-descriptions-item label="Tank Name">{{ selectedTank.name }}</el-descriptions-item>
        <el-descriptions-item label="Liquid Type">{{ selectedTank.liquidType }}</el-descriptions-item>
        <el-descriptions-item label="Capacity">{{ selectedTank.capacity }} m³</el-descriptions-item>
        <el-descriptions-item label="Current Volume">{{ selectedTank.currentVolume }} m³</el-descriptions-item>
        <el-descriptions-item label="Fill Level" :span="2">
          <el-progress :percentage="selectedTank.fillPercentage" :color="getLevelColor(selectedTank.fillPercentage)" :stroke-width="10" />
        </el-descriptions-item>
        <el-descriptions-item label="Temperature">{{ selectedTank.temperature }} °C</el-descriptions-item>
        <el-descriptions-item label="Pressure">{{ selectedTank.pressure }} bar</el-descriptions-item>
        <el-descriptions-item label="Inflow Rate">{{ selectedTank.inflowRate }} m³/h</el-descriptions-item>
        <el-descriptions-item label="Outflow Rate">{{ selectedTank.outflowRate }} m³/h</el-descriptions-item>
        <el-descriptions-item label="Min Level Alarm">{{ selectedTank.minLevelAlarm }} m</el-descriptions-item>
        <el-descriptions-item label="Max Level Alarm">{{ selectedTank.maxLevelAlarm }} m</el-descriptions-item>
        <el-descriptions-item label="Last Maintenance">{{ selectedTank.lastMaintenance }}</el-descriptions-item>
        <el-descriptions-item label="Next Maintenance">{{ selectedTank.nextMaintenance }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button type="primary" @click="showMaintenanceSchedule">Schedule Maintenance</el-button>
        <el-button @click="detailDialogVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Alarm Dialog -->
    <el-dialog v-model="alarmDialogVisible" title="Tank Alarm" width="400px">
      <div class="alarm-content" v-if="alarmTank">
        <el-alert
            :title="`${alarmTank.name} - ${alarmTank.fillPercentage > 90 ? 'High Level Warning' : 'Low Level Warning'}`"
            :type="alarmTank.fillPercentage > 90 ? 'warning' : 'danger'"
            :closable="false"
            show-icon
        >
          <template #default>
            <p>Current fill level: {{ alarmTank.fillPercentage }}%</p>
            <p>Threshold: {{ alarmTank.fillPercentage > 90 ? '90%' : '10%' }}</p>
            <p>Please take immediate action.</p>
          </template>
        </el-alert>
        <div class="alarm-actions">
          <el-button type="primary" @click="acknowledgeAlarm">Acknowledge</el-button>
          <el-button @click="alarmDialogVisible = false">Ignore</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Download,
  Refresh,
  Grid,
  DataAnalysis,
  DataLine,
  PieChart,
  House,
  View,
  Bell,
  Search,
  ArrowUp,
  ArrowDown
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Initializing tank sensors...',
  'Reading level data...',
  'Almost ready...'
]

// ==================== Data State ====================
const chartPeriod = ref('hour')
const tankTypeFilter = ref('all')
const searchText = ref('')

interface Tank {
  id: number
  name: string
  liquidType: string
  capacity: number
  currentVolume: number
  fillPercentage: number
  temperature: number
  pressure: number
  inflowRate: number
  outflowRate: number
  minLevelAlarm: number
  maxLevelAlarm: number
  lastMaintenance: string
  nextMaintenance: string
}

const tanks = ref<Tank[]>([])

const stats = computed(() => {
  const total = tanks.value.length
  const totalCapacity = tanks.value.reduce((sum, t) => sum + t.capacity, 0)
  const currentVolume = tanks.value.reduce((sum, t) => sum + t.currentVolume, 0)
  const avgFillLevel = total > 0 ? (currentVolume / totalCapacity * 100).toFixed(1) : 0
  return {
    total,
    totalCapacity: totalCapacity.toFixed(1),
    currentVolume: currentVolume.toFixed(1),
    avgFillLevel
  }
})

const filteredTanks = computed(() => {
  if (tankTypeFilter.value === 'all') return tanks.value
  return tanks.value.filter(t => t.liquidType === tankTypeFilter.value)
})

const filteredTableTanks = computed(() => {
  if (!searchText.value) return tanks.value
  return tanks.value.filter(t =>
      t.name.toLowerCase().includes(searchText.value.toLowerCase()) ||
      t.liquidType.toLowerCase().includes(searchText.value.toLowerCase())
  )
})

const pagination = ref({ currentPage: 1, pageSize: 10 })
const paginatedTanks = computed(() => {
  const start = (pagination.value.currentPage - 1) * pagination.value.pageSize
  return filteredTableTanks.value.slice(start, start + pagination.value.pageSize)
})

// Generate mock tanks
const generateTanks = (): Tank[] => {
  const tankNames = [
    'Chilled Water Tank', 'Hot Water Tank', 'Fire Reserve Tank',
    'Raw Water Tank', 'Treated Water Tank', 'Diesel Fuel Tank',
    'Chemical Storage Tank', 'Wastewater Tank', 'RO Feed Tank',
    'Cooling Tower Basin', 'Expansion Tank', 'Storage Tank A',
    'Storage Tank B', 'Emergency Reserve'
  ]

  const liquidTypes = ['Water', 'Water', 'Water', 'Water', 'Water', 'Fuel', 'Chemical', 'Wastewater', 'Water', 'Water', 'Water', 'Storage', 'Storage', 'Water']

  return tankNames.map((name, idx) => {
    const capacity = [500, 300, 800, 600, 400, 200, 150, 1000, 350, 250, 100, 750, 650, 900][idx % 14]
    const fillPercentage = parseFloat((30 + Math.random() * 60).toFixed(1))
    const currentVolume = parseFloat((capacity * fillPercentage / 100).toFixed(1))
    const temperature = parseFloat((15 + Math.random() * 25).toFixed(1))
    const pressure = parseFloat((0.5 + Math.random() * 2).toFixed(1))
    const inflowRate = parseFloat((10 + Math.random() * 50).toFixed(1))
    const outflowRate = parseFloat((8 + Math.random() * 45).toFixed(1))

    return {
      id: idx + 1,
      name: name,
      liquidType: liquidTypes[idx % liquidTypes.length],
      capacity: capacity,
      currentVolume: currentVolume,
      fillPercentage: fillPercentage,
      temperature: temperature,
      pressure: pressure,
      inflowRate: inflowRate,
      outflowRate: outflowRate,
      minLevelAlarm: capacity * 0.1,
      maxLevelAlarm: capacity * 0.9,
      lastMaintenance: '2024-01-15',
      nextMaintenance: '2024-04-15'
    }
  })
}

// Helper functions
const getTankLevelClass = (percentage: number) => {
  if (percentage >= 90) return 'high'
  if (percentage <= 10) return 'low'
  return 'normal'
}

const getTankStatus = (tank: Tank) => {
  if (tank.fillPercentage >= 90) return 'High Level'
  if (tank.fillPercentage <= 10) return 'Low Level'
  return 'Normal'
}

const getTankStatusTag = (tank: Tank) => {
  if (tank.fillPercentage >= 90) return 'danger'
  if (tank.fillPercentage <= 10) return 'warning'
  return 'success'
}

const getLevelColor = (percentage: number) => {
  if (percentage >= 90) return '#F56C6C'
  if (percentage <= 10) return '#E6A23C'
  return '#67C23A'
}

const getTempClass = (temp: number) => {
  if (temp > 35 || temp < 5) return 'danger'
  if (temp > 30 || temp < 10) return 'warning'
  return ''
}

const getLiquidTypeTag = (type: string) => {
  const map: Record<string, string> = {
    Water: 'primary',
    Fuel: 'warning',
    Chemical: 'danger',
    Wastewater: 'info',
    Storage: ''
  }
  return map[type] || 'info'
}

// ==================== Chart Functions ====================
const trendChartRef = ref<HTMLElement>()
const capacityChartRef = ref<HTMLElement>()

let trendChart: echarts.ECharts | null = null
let capacityChart: echarts.ECharts | null = null

const initCharts = () => {
  nextTick(() => {
    if (trendChartRef.value) {
      if (trendChart) trendChart.dispose()
      trendChart = echarts.init(trendChartRef.value)
      updateTrendChart()
    }

    if (capacityChartRef.value) {
      if (capacityChart) capacityChart.dispose()
      capacityChart = echarts.init(capacityChartRef.value)
      updateCapacityChart()
    }
  })
}

const updateTrendChart = () => {
  let levelData: number[] = []
  let inflowData: number[] = []
  let outflowData: number[] = []
  let xAxisData: string[] = []

  if (chartPeriod.value === 'hour') {
    xAxisData = Array.from({ length: 24 }, (_, i) => `${i}:00`)
    levelData = Array.from({ length: 24 }, () => parseFloat((45 + Math.random() * 30).toFixed(1)))
    inflowData = Array.from({ length: 24 }, () => parseFloat((30 + Math.random() * 40).toFixed(1)))
    outflowData = Array.from({ length: 24 }, () => parseFloat((25 + Math.random() * 35).toFixed(1)))
  } else if (chartPeriod.value === 'day') {
    xAxisData = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    levelData = [55, 58, 52, 60, 65, 62, 58]
    inflowData = [42, 48, 45, 52, 58, 50, 40]
    outflowData = [38, 42, 40, 48, 52, 46, 38]
  } else {
    xAxisData = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    levelData = [55, 58, 52, 60]
    inflowData = [45, 48, 46, 52]
    outflowData = [40, 44, 42, 48]
  }

  trendChart?.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Fill Level (%)', 'Inflow Rate (m³/h)', 'Outflow Rate (m³/h)'] },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: [
      { type: 'value', name: 'Fill Level (%)', min: 0, max: 100 },
      { type: 'value', name: 'Flow Rate (m³/h)' }
    ],
    series: [
      {
        name: 'Fill Level (%)',
        type: 'line',
        data: levelData,
        smooth: true,
        lineStyle: { color: '#409EFF', width: 3 },
        areaStyle: { opacity: 0.1 },
        yAxisIndex: 0,
        markLine: { data: [{ yAxis: 90, name: 'High Alarm', lineStyle: { color: '#F56C6C' } }, { yAxis: 10, name: 'Low Alarm', lineStyle: { color: '#E6A23C' } }] }
      },
      {
        name: 'Inflow Rate (m³/h)',
        type: 'line',
        data: inflowData,
        smooth: true,
        lineStyle: { color: '#67C23A', width: 2 },
        yAxisIndex: 1
      },
      {
        name: 'Outflow Rate (m³/h)',
        type: 'line',
        data: outflowData,
        smooth: true,
        lineStyle: { color: '#E6A23C', width: 2 },
        yAxisIndex: 1
      }
    ]
  })
}

const updateCapacityChart = () => {
  const data = tanks.value.map(t => ({
    name: t.name.length > 10 ? t.name.substring(0, 10) + '...' : t.name,
    value: t.capacity,
    fill: t.currentVolume
  }))

  capacityChart?.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'category', data: data.map(d => d.name), axisLabel: { rotate: 30, interval: 0 } },
    yAxis: { type: 'value', name: 'Volume (m³)' },
    series: [
      {
        name: 'Capacity',
        type: 'bar',
        data: data.map(d => d.value),
        itemStyle: { borderRadius: [4, 4, 0, 0], color: '#e4e7ed' }
      },
      {
        name: 'Current Volume',
        type: 'bar',
        data: data.map(d => d.fill),
        itemStyle: { borderRadius: [4, 4, 0, 0], color: (params: any) => {
            const percent = (params.value / data[params.dataIndex].value) * 100
            if (percent >= 90) return '#F56C6C'
            if (percent <= 10) return '#E6A23C'
            return '#67C23A'
          } }
      }
    ]
  })
}

// ==================== Actions ====================
const detailDialogVisible = ref(false)
const alarmDialogVisible = ref(false)
const selectedTank = ref<Tank | null>(null)
const alarmTank = ref<Tank | null>(null)

const viewTankDetails = (tank: Tank) => {
  selectedTank.value = tank
  detailDialogVisible.value = true
}

const showAlarmSettings = (tank: Tank) => {
  alarmTank.value = tank
  alarmDialogVisible.value = true
}

const acknowledgeAlarm = () => {
  alarmDialogVisible.value = false
  ElMessage.success('Alarm acknowledged')
}

const showMaintenanceSchedule = () => {
  ElMessage.info('Maintenance scheduling feature coming soon')
}

const refreshData = () => {
  tanks.value = generateTanks()
  updateCapacityChart()
  updateTrendChart()
  ElMessage.success('Data refreshed')
}

const handleExport = () => {
  ElMessage.success('Report export started')
}

const handleSizeChange = () => { pagination.value.currentPage = 1 }
const handleCurrentChange = () => {}

// ==================== Lifecycle ====================
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
      tanks.value = generateTanks()
      initCharts()
    }, 400)
  }, 2000)
})

watch([trendChartRef, capacityChartRef], () => {
  window.addEventListener('resize', () => {
    trendChart?.resize()
    capacityChart?.resize()
  })
})

watch([tankTypeFilter, searchText], () => {
  pagination.value.currentPage = 1
})
</script>

<style scoped>
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

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Main Container */
.tanks-container {
  padding: 20px;
  background: #f0f2f5;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  background: white;
  padding: 20px 24px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.page-header h2 {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 600;
  color: #1f2f3d;
}

.header-subtitle {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Overview Cards */
.overview-row {
  margin-bottom: 24px;
}

.overview-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.overview-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.overview-icon.total { background: rgba(64, 158, 255, 0.1); color: #409EFF; }
.overview-icon.capacity { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
.overview-icon.current { background: rgba(230, 162, 60, 0.1); color: #E6A23C; }
.overview-icon.fill { background: rgba(245, 108, 108, 0.1); color: #F56C6C; }

.overview-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.overview-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
}

.overview-value .unit {
  font-size: 12px;
  font-weight: normal;
  color: #909399;
}

/* Section Title */
.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title span {
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

/* Tank Cards */
.tanks-row {
  margin-bottom: 20px;
}

.tank-card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.3s ease;
  border-top: 4px solid #67C23A;
}

.tank-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(0,0,0,0.12);
}

.tank-card.high { border-top-color: #F56C6C; }
.tank-card.low { border-top-color: #E6A23C; }
.tank-card.normal { border-top-color: #67C23A; }

.tank-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.tank-name {
  font-weight: 600;
  font-size: 16px;
  color: #1f2f3d;
}

.tank-icon {
  text-align: center;
  margin: 12px 0;
  color: #409EFF;
}

.tank-level {
  text-align: center;
  margin-bottom: 16px;
}

.level-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.level-value {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 8px;
}

.level-detail {
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
}

.tank-parameters {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 16px;
}

.param {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  padding: 4px 0;
}

.param .label { color: #909399; }
.param .value { font-weight: 500; color: #606266; }
.param .value.danger { color: #F56C6C; }
.param .value.warning { color: #E6A23C; }

.tank-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
}

/* Charts */
.charts-row {
  margin-bottom: 20px;
}

.chart-card {
  border-radius: 16px;
}

.chart-container {
  width: 100%;
  height: 350px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Table */
.table-card {
  border-radius: 16px;
}

.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

/* Alarm Dialog */
.alarm-content {
  text-align: center;
}

.alarm-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 20px;
}
</style>