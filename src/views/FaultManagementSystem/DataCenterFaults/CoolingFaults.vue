<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted, computed } from 'vue'
import {
  Search, RefreshRight, Warning, CircleCheck, Clock,
  TrendCharts, Monitor, Connection, DataAnalysis,
  Document, Setting, More, ArrowUp, ArrowDown,
  VideoCamera, Histogram, Sunny, ColdDrink
} from "@element-plus/icons-vue"
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Connecting to cooling system...',
  'Loading temperature sensors...',
  'Analyzing cooling performance...'
]

// Cooling Units Data
const coolingUnits = ref([
  {
    id: 'CRAC-01-DC-A',
    name: 'CRAC Unit 1',
    location: 'Data Center A - Row 1',
    type: 'CRAC',
    status: 'warning',
    supplyTemp: 18.5,
    returnTemp: 24.2,
    setpoint: 22,
    humidity: 48,
    fanSpeed: 65,
    coolingCapacity: 85,
    refrigerantPressure: 145,
    compressorStatus: 'running',
    alerts: [
      { severity: 'warning', message: 'Supply temperature below setpoint', timestamp: '2025-01-16 08:30:00' },
      { severity: 'info', message: 'High humidity detected', timestamp: '2025-01-15 14:20:00' }
    ],
    lastMaintenance: '2024-12-15',
    nextMaintenance: '2025-03-15'
  },
  {
    id: 'CRAC-02-DC-A',
    name: 'CRAC Unit 2',
    location: 'Data Center A - Row 1',
    type: 'CRAC',
    status: 'critical',
    supplyTemp: 21.5,
    returnTemp: 28.5,
    setpoint: 22,
    humidity: 52,
    fanSpeed: 45,
    coolingCapacity: 62,
    refrigerantPressure: 98,
    compressorStatus: 'fault',
    alerts: [
      { severity: 'critical', message: 'Low refrigerant pressure - possible leak', timestamp: '2025-01-14 10:15:00' },
      { severity: 'critical', message: 'Compressor fault - unit not cooling', timestamp: '2025-01-14 10:00:00' },
      { severity: 'warning', message: 'High return temperature', timestamp: '2025-01-14 09:45:00' }
    ],
    lastMaintenance: '2024-11-20',
    nextMaintenance: '2025-02-20'
  },
  {
    id: 'CRAH-01-DC-B',
    name: 'CRAH Unit 1',
    location: 'Data Center B - Row 2',
    type: 'CRAH',
    status: 'healthy',
    supplyTemp: 19.2,
    returnTemp: 23.8,
    setpoint: 21,
    humidity: 45,
    fanSpeed: 55,
    coolingCapacity: 92,
    valvePosition: 78,
    pumpStatus: 'running',
    alerts: [],
    lastMaintenance: '2025-01-10',
    nextMaintenance: '2025-04-10'
  },
  {
    id: 'INROW-01-DC-C',
    name: 'InRow Cooler 1',
    location: 'Data Center C - Row 3',
    type: 'InRow',
    status: 'warning',
    supplyTemp: 20.1,
    returnTemp: 26.3,
    setpoint: 22,
    humidity: 49,
    fanSpeed: 72,
    coolingCapacity: 78,
    refrigerantPressure: 128,
    compressorStatus: 'running',
    alerts: [
      { severity: 'warning', message: 'Fan speed high - possible blockage', timestamp: '2025-01-15 11:00:00' }
    ],
    lastMaintenance: '2024-12-28',
    nextMaintenance: '2025-03-28'
  },
  {
    id: 'CHILLER-01',
    name: 'Main Chiller 1',
    location: 'Central Plant',
    type: 'Chiller',
    status: 'healthy',
    chilledWaterSupply: 6.5,
    chilledWaterReturn: 11.2,
    condenserWaterSupply: 28,
    condenserWaterReturn: 33,
    setpoint: 7,
    efficiency: 5.2,
    refrigerantPressure: 185,
    compressorStatus: 'running',
    alerts: [],
    lastMaintenance: '2025-01-05',
    nextMaintenance: '2025-04-05'
  },
  {
    id: 'PUMP-01',
    name: 'Chilled Water Pump 1',
    location: 'Central Plant',
    type: 'Pump',
    status: 'healthy',
    flowRate: 1250,
    pressure: 65,
    motorCurrent: 85,
    motorTemp: 42,
    speed: 1480,
    vibration: 2.3,
    alerts: [],
    lastMaintenance: '2024-12-20',
    nextMaintenance: '2025-03-20'
  }
])

// Temperature zone data
const temperatureZones = ref([
  { zone: 'Zone A1', temp: 22.5, status: 'good', racks: 12 },
  { zone: 'Zone A2', temp: 24.8, status: 'warning', racks: 8 },
  { zone: 'Zone B1', temp: 21.2, status: 'good', racks: 15 },
  { zone: 'Zone B2', temp: 23.1, status: 'good', racks: 10 },
  { zone: 'Zone C1', temp: 26.5, status: 'critical', racks: 6 },
  { zone: 'Zone C2', temp: 22.8, status: 'good', racks: 9 }
])

// Historical fault data
const faultHistory = ref([
  { id: 'CFLT-001', unitId: 'CRAC-02-DC-A', type: 'Compressor Failure', severity: 'critical', timestamp: '2025-01-14 10:00:00', resolved: '', description: 'Compressor not starting - electrical fault' },
  { id: 'CFLT-002', unitId: 'CRAC-01-DC-A', type: 'Temperature Low', severity: 'warning', timestamp: '2025-01-12 15:30:00', resolved: '2025-01-12 16:15:00', description: 'Supply temperature below setpoint' },
  { id: 'CFLT-003', unitId: 'INROW-01-DC-C', type: 'Fan High Speed', severity: 'warning', timestamp: '2025-01-10 09:45:00', resolved: '2025-01-10 11:20:00', description: 'Fan speed exceeded 90% for 30 minutes' },
  { id: 'CFLT-004', unitId: 'CRAC-02-DC-A', type: 'Refrigerant Leak', severity: 'critical', timestamp: '2025-01-08 14:20:00', resolved: '', description: 'Low refrigerant pressure detected' }
])

// Temperature trend data
const tempTrendData = ref([
  { time: '00:00', supply: 19.2, return: 23.5, ambient: 24.0 },
  { time: '02:00', supply: 19.0, return: 23.2, ambient: 23.8 },
  { time: '04:00', supply: 18.8, return: 23.0, ambient: 23.5 },
  { time: '06:00', supply: 18.5, return: 22.8, ambient: 23.2 },
  { time: '08:00', supply: 19.0, return: 23.5, ambient: 24.0 },
  { time: '10:00', supply: 19.5, return: 24.2, ambient: 25.0 },
  { time: '12:00', supply: 20.0, return: 25.0, ambient: 26.0 },
  { time: '14:00', supply: 20.5, return: 25.8, ambient: 27.0 },
  { time: '16:00', supply: 20.2, return: 25.5, ambient: 26.5 },
  { time: '18:00', supply: 19.8, return: 24.8, ambient: 25.5 },
  { time: '20:00', supply: 19.5, return: 24.2, ambient: 24.8 },
  { time: '22:00', supply: 19.2, return: 23.8, ambient: 24.2 }
])

// PUE trend data
const pueTrendData = ref([
  { month: 'Aug', pue: 1.52, coolingEff: 0.38 },
  { month: 'Sep', pue: 1.49, coolingEff: 0.36 },
  { month: 'Oct', pue: 1.47, coolingEff: 0.35 },
  { month: 'Nov', pue: 1.44, coolingEff: 0.33 },
  { month: 'Dec', pue: 1.42, coolingEff: 0.32 },
  { month: 'Jan', pue: 1.41, coolingEff: 0.31 }
])

// Selected cooling unit
const selectedUnit = ref<any>(null)
const detailVisible = ref(false)
const historyVisible = ref(false)
const zoneDetailVisible = ref(false)

// Filters
const searchKeyword = ref('')
const statusFilter = ref('all')
const typeFilter = ref('all')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const tempChartRef = ref<HTMLElement | null>(null)
const pueChartRef = ref<HTMLElement | null>(null)
let tempChart: echarts.ECharts | null = null
let pueChart: echarts.ECharts | null = null

const filteredUnits = computed(() => {
  let filtered = coolingUnits.value

  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(u => u.status === statusFilter.value)
  }

  if (typeFilter.value !== 'all') {
    filtered = filtered.filter(u => u.type === typeFilter.value)
  }

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(u =>
        u.id.toLowerCase().includes(keyword) ||
        u.name.toLowerCase().includes(keyword) ||
        u.location.toLowerCase().includes(keyword)
    )
  }

  return filtered
})

const paginatedUnits = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredUnits.value.slice(start, end)
})

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
}

const getStatusColor = (status: string) => {
  switch(status) {
    case 'critical': return '#F56C6C'
    case 'warning': return '#E6A23C'
    case 'healthy': return '#67C23A'
    default: return '#909399'
  }
}

const getStatusText = (status: string) => {
  switch(status) {
    case 'critical': return 'Critical'
    case 'warning': return 'Warning'
    case 'healthy': return 'Healthy'
    default: return 'Unknown'
  }
}

const getTempColor = (temp: number, type: string) => {
  if (type === 'supply') {
    if (temp > 22) return '#F56C6C'
    if (temp > 20) return '#E6A23C'
    return '#67C23A'
  } else {
    if (temp > 27) return '#F56C6C'
    if (temp > 25) return '#E6A23C'
    return '#67C23A'
  }
}

const viewDetails = (unit: any) => {
  selectedUnit.value = unit
  detailVisible.value = true
}

const viewHistory = (unit: any) => {
  selectedUnit.value = unit
  historyVisible.value = true
}

const viewZoneDetails = () => {
  zoneDetailVisible.value = true
}

const resetUnit = (unit: any) => {
  ElMessageBox.confirm(
      `Reset ${unit.id}? This will restart the cooling unit.`,
      'Confirm Reset',
      {
        confirmButtonText: 'Reset',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    ElMessage.success(`${unit.id} reset initiated`)
  }).catch(() => {})
}

const scheduleMaintenance = (unit: any) => {
  ElMessageBox.confirm(
      `Schedule maintenance for ${unit.id}? This will create a work order.`,
      'Schedule Maintenance',
      {
        confirmButtonText: 'Schedule',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    ElMessage.success(`Maintenance scheduled for ${unit.id}`)
  }).catch(() => {})
}

const clearAlerts = (unit: any) => {
  unit.alerts = []
  ElMessage.success(`Alerts cleared for ${unit.id}`)
}

const refreshData = () => {
  ElMessage.info('Refreshing cooling data...')
  setTimeout(() => {
    ElMessage.success('Data refreshed successfully')
  }, 1000)
}

const initTempChart = () => {
  if (tempChartRef.value) {
    if (tempChart) tempChart.dispose()

    tempChart = echarts.init(tempChartRef.value)
    tempChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: {
        data: ['Supply Temp (°C)', 'Return Temp (°C)', 'Ambient Temp (°C)'],
        left: 'left',
        textStyle: { color: '#606266' }
      },
      grid: { left: '8%', right: '8%', top: '15%', bottom: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: tempTrendData.value.map(d => d.time),
        axisLabel: { rotate: 45 }
      },
      yAxis: {
        type: 'value',
        name: 'Temperature (°C)',
        min: 15,
        max: 30
      },
      series: [
        {
          name: 'Supply Temp (°C)',
          type: 'line',
          data: tempTrendData.value.map(d => d.supply),
          smooth: true,
          lineStyle: { color: '#409EFF', width: 3 },
          areaStyle: { opacity: 0.1, color: '#409EFF' },
          symbol: 'circle',
          symbolSize: 6,
          label: { show: true, position: 'top', formatter: '{c}°C' }
        },
        {
          name: 'Return Temp (°C)',
          type: 'line',
          data: tempTrendData.value.map(d => d.return),
          smooth: true,
          lineStyle: { color: '#F56C6C', width: 3 },
          symbol: 'diamond',
          symbolSize: 6,
          label: { show: true, position: 'top', formatter: '{c}°C' }
        },
        {
          name: 'Ambient Temp (°C)',
          type: 'line',
          data: tempTrendData.value.map(d => d.ambient),
          smooth: true,
          lineStyle: { color: '#E6A23C', width: 2, type: 'dashed' },
          symbol: 'triangle',
          symbolSize: 6,
          label: { show: true, position: 'top', formatter: '{c}°C' }
        }
      ]
    })
  }
}

const initPueChart = () => {
  if (pueChartRef.value) {
    if (pueChart) pueChart.dispose()

    pueChart = echarts.init(pueChartRef.value)
    pueChart.setOption({
      tooltip: { trigger: 'axis' },
      legend: {
        data: ['PUE', 'Cooling Efficiency'],
        left: 'left',
        textStyle: { color: '#606266' }
      },
      grid: { left: '8%', right: '8%', top: '15%', bottom: '8%', containLabel: true },
      xAxis: {
        type: 'category',
        data: pueTrendData.value.map(d => d.month),
        axisLabel: { fontWeight: 500 }
      },
      yAxis: [
        { type: 'value', name: 'PUE', min: 1.2, max: 1.6 },
        { type: 'value', name: 'Cooling Efficiency', min: 0.2, max: 0.5 }
      ],
      series: [
        {
          name: 'PUE',
          type: 'line',
          data: pueTrendData.value.map(d => d.pue),
          smooth: true,
          lineStyle: { color: '#409EFF', width: 3 },
          areaStyle: { opacity: 0.1, color: '#409EFF' },
          symbol: 'circle',
          symbolSize: 8,
          label: { show: true, position: 'top', formatter: '{c}' }
        },
        {
          name: 'Cooling Efficiency',
          type: 'line',
          yAxisIndex: 1,
          data: pueTrendData.value.map(d => d.coolingEff),
          smooth: true,
          lineStyle: { color: '#67C23A', width: 3 },
          symbol: 'diamond',
          symbolSize: 8,
          label: { show: true, position: 'top', formatter: '{c}' }
        }
      ]
    })
  }
}

const handleResize = () => {
  tempChart?.resize()
  pueChart?.resize()
}

watch(isLoaded, (loaded) => {
  if (loaded) {
    nextTick(() => {
      initTempChart()
      initPueChart()
      window.addEventListener('resize', handleResize)
    })
  }
})

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
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  tempChart?.dispose()
  pueChart?.dispose()
})

// Helper computed values
const avgSupplyTemp = computed(() => {
  const sum = coolingUnits.value.reduce((acc, u) => acc + (u.supplyTemp || 0), 0)
  return (sum / coolingUnits.value.filter(u => u.supplyTemp).length).toFixed(1)
})

const avgReturnTemp = computed(() => {
  const sum = coolingUnits.value.reduce((acc, u) => acc + (u.returnTemp || 0), 0)
  return (sum / coolingUnits.value.filter(u => u.returnTemp).length).toFixed(1)
})

const criticalZones = computed(() => {
  return temperatureZones.value.filter(z => z.status === 'critical').length
})

const warningZones = computed(() => {
  return temperatureZones.value.filter(z => z.status === 'warning').length
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
          <span class="loading-title">Loading</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Cooling Fault Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="cooling-faults">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Cooling System Fault Management</h2>
        <p class="subtitle">Real-time monitoring and fault analysis for data center cooling systems</p>
      </div>
      <div class="header-actions">
        <el-input
            v-model="searchKeyword"
            placeholder="Search by ID or Location..."
            clearable
            style="width: 260px"
            :prefix-icon="Search"
        />
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 130px">
          <el-option label="All" value="all" />
          <el-option label="Healthy" value="healthy" />
          <el-option label="Warning" value="warning" />
          <el-option label="Critical" value="critical" />
        </el-select>
        <el-select v-model="typeFilter" placeholder="Type" clearable style="width: 130px">
          <el-option label="All" value="all" />
          <el-option label="CRAC" value="CRAC" />
          <el-option label="CRAH" value="CRAH" />
          <el-option label="InRow" value="InRow" />
          <el-option label="Chiller" value="Chiller" />
          <el-option label="Pump" value="Pump" />
        </el-select>
        <el-button type="primary" @click="refreshData">
          <el-icon><RefreshRight /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Statistics Overview -->
    <div class="stats-grid">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon total">
            <el-icon><Monitor /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ coolingUnits.length }}</div>
            <div class="stat-label">Total Units</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon healthy">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ coolingUnits.filter(u => u.status === 'healthy').length }}</div>
            <div class="stat-label">Healthy</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon warning">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ coolingUnits.filter(u => u.status === 'warning').length }}</div>
            <div class="stat-label">Warning</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon critical">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ coolingUnits.filter(u => u.status === 'critical').length }}</div>
            <div class="stat-label">Critical</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon temp">
            <el-icon><ColdDrink /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ avgSupplyTemp }}°C</div>
            <div class="stat-label">Avg Supply Temp</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Temperature Zones Summary -->
    <div class="zones-summary">
      <div class="zones-header">
        <span>Temperature Zones Status</span>
        <el-button type="primary" link @click="viewZoneDetails">View Details</el-button>
      </div>
      <div class="zones-grid">
        <div v-for="zone in temperatureZones" :key="zone.zone" class="zone-card" :class="zone.status">
          <div class="zone-name">{{ zone.zone }}</div>
          <div class="zone-temp">{{ zone.temp }}°C</div>
          <div class="zone-racks">{{ zone.racks }} racks</div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Temperature Trends (24 Hours)</span>
            <el-tag type="info" size="small">Live Monitoring</el-tag>
          </div>
        </template>
        <div ref="tempChartRef" class="chart"></div>
      </el-card>

      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>PUE & Cooling Efficiency Trend</span>
            <el-tag type="success" size="small">Improving</el-tag>
          </div>
        </template>
        <div ref="pueChartRef" class="chart"></div>
      </el-card>
    </div>

    <!-- Cooling Units Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="table-header">
          <span class="table-title">Cooling Units Overview</span>
          <span class="table-subtitle">{{ filteredUnits.length }} units displayed</span>
        </div>
      </template>
      <el-table :data="paginatedUnits" stripe style="width: 100%" align="center" >
        <el-table-column prop="id" label="Unit ID" width="130" align="center"  />
        <el-table-column prop="name" label="Name" min-width="150" align="center"  />
        <el-table-column prop="location" label="Location" min-width="180" show-overflow-tooltip />
        <el-table-column prop="type" label="Type"  align="center"  />
        <el-table-column label="Status" align="center" >
          <template #default="{ row }">
            <div class="status-indicator">
              <span class="status-dot" :style="{ background: getStatusColor(row.status) }"></span>
              <span>{{ getStatusText(row.status) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Supply/Return"  align="center" >
          <template #default="{ row }">
            <div class="temp-cell">
              <span :style="{ color: getTempColor(row.supplyTemp, 'supply') }">{{ row.supplyTemp || '-' }}°C</span>
              <span class="separator">→</span>
              <span :style="{ color: getTempColor(row.returnTemp, 'return') }">{{ row.returnTemp || '-' }}°C</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Setpoint" align="center" >
          <template #default="{ row }">
            <span>{{ row.setpoint || '-' }}°C</span>
          </template>
        </el-table-column>
        <el-table-column prop="fanSpeed" label="Fan"  align="center"  >
          <template #default="{ row }">
            <span v-if="row.fanSpeed">{{ row.fanSpeed }}%</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="Alerts" align="center" class-name="alert-column">
          <template #default="{ row }">
            <div style="position: relative; height: 100%; display: flex; align-items: center; justify-content: center;">
              <el-badge
                  :value="row.alerts.length"
                  :hidden="row.alerts.length === 0"
                  type="danger"
                  :offset="[-2, 8]"
              >
                <el-button size="small" text @click="viewDetails(row)">
                  <el-icon><Warning /></el-icon>
                </el-button>
              </el-badge>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="180" align="center"  fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetails(row)">Details</el-button>
            <el-button type="info" link size="small" @click="viewHistory(row)">History</el-button>
            <el-button type="warning" link size="small" @click="resetUnit(row)" v-if="row.status !== 'healthy'">Reset</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredUnits.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Cooling Unit Detail Dialog -->
    <el-dialog v-model="detailVisible" :title="selectedUnit?.name" width="750px">
      <div v-if="selectedUnit" class="unit-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Unit ID">{{ selectedUnit.id }}</el-descriptions-item>
          <el-descriptions-item label="Type">{{ selectedUnit.type }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedUnit.location }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <span class="status-indicator">
              <span class="status-dot" :style="{ background: getStatusColor(selectedUnit.status) }"></span>
              {{ getStatusText(selectedUnit.status) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="Last Maintenance">{{ selectedUnit.lastMaintenance }}</el-descriptions-item>
          <el-descriptions-item label="Next Maintenance">{{ selectedUnit.nextMaintenance }}</el-descriptions-item>
          <el-descriptions-item label="Supply Temp">
            <span :style="{ color: getTempColor(selectedUnit.supplyTemp, 'supply') }">{{ selectedUnit.supplyTemp }}°C</span>
          </el-descriptions-item>
          <el-descriptions-item label="Return Temp">
            <span :style="{ color: getTempColor(selectedUnit.returnTemp, 'return') }">{{ selectedUnit.returnTemp }}°C</span>
          </el-descriptions-item>
          <el-descriptions-item label="Setpoint">{{ selectedUnit.setpoint }}°C</el-descriptions-item>
          <el-descriptions-item label="Humidity">{{ selectedUnit.humidity || '-' }}%</el-descriptions-item>
          <el-descriptions-item label="Fan Speed">{{ selectedUnit.fanSpeed || '-' }}%</el-descriptions-item>
          <el-descriptions-item label="Cooling Capacity">{{ selectedUnit.coolingCapacity || '-' }}%</el-descriptions-item>
          <el-descriptions-item v-if="selectedUnit.refrigerantPressure" label="Refrigerant Pressure">{{ selectedUnit.refrigerantPressure }} psi</el-descriptions-item>
          <el-descriptions-item v-if="selectedUnit.efficiency" label="Efficiency">COP {{ selectedUnit.efficiency }}</el-descriptions-item>
        </el-descriptions>

        <div v-if="selectedUnit.alerts.length > 0" class="alerts-section">
          <h4>Active Alerts</h4>
          <el-table :data="selectedUnit.alerts" size="small">
            <el-table-column label="Severity" width="100">
              <template #default="{ row }">
                <el-tag :type="row.severity === 'critical' ? 'danger' : row.severity === 'warning' ? 'warning' : 'info'" size="small">
                  {{ row.severity }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="message" label="Message" />
            <el-table-column prop="timestamp" label="Timestamp" width="160" />
          </el-table>
          <div class="alerts-actions">
            <el-button type="primary" size="small" @click="clearAlerts(selectedUnit)">Clear Alerts</el-button>
          </div>
        </div>

        <div class="detail-actions">
          <el-button type="warning" @click="resetUnit(selectedUnit)">Reset Unit</el-button>
          <el-button type="primary" @click="scheduleMaintenance(selectedUnit)">Schedule Maintenance</el-button>
          <el-button type="info" @click="viewHistory(selectedUnit)">View Fault History</el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Zone Details Dialog -->
    <el-dialog v-model="zoneDetailVisible" title="Temperature Zone Details" width="700px">
      <el-table :data="temperatureZones" stripe>
        <el-table-column prop="zone" label="Zone" width="100" />
        <el-table-column label="Temperature" width="120">
          <template #default="{ row }">
            <span :style="{ color: row.status === 'critical' ? '#F56C6C' : row.status === 'warning' ? '#E6A23C' : '#67C23A' }">
              {{ row.temp }}°C
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'critical' ? 'danger' : row.status === 'warning' ? 'warning' : 'success'" size="small">
              {{ row.status.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="racks" label="Racks Affected" width="130" />
        <el-table-column label="Recommendation">
          <template #default="{ row }">
            <span v-if="row.status === 'critical'">Immediate cooling intervention required</span>
            <span v-else-if="row.status === 'warning'">Monitor temperature, consider adjusting airflow</span>
            <span v-else>Operating within normal range</span>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="zoneDetailVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Fault History Dialog -->
    <el-dialog v-model="historyVisible" :title="`Fault History - ${selectedUnit?.id}`" width="800px">
      <el-table :data="faultHistory.filter(f => f.unitId === selectedUnit?.id)" stripe>
        <el-table-column prop="id" label="Fault ID" width="100" />
        <el-table-column prop="type" label="Fault Type" width="140" />
        <el-table-column label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="row.severity === 'critical' ? 'danger' : 'warning'" size="small">
              {{ row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="Description" min-width="200" />
        <el-table-column prop="timestamp" label="Occurred" width="160" />
        <el-table-column prop="resolved" label="Resolved" width="160">
          <template #default="{ row }">
            <span v-if="row.resolved">{{ row.resolved }}</span>
            <span v-else class="unresolved">Unresolved</span>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="historyVisible = false">Close</el-button>
      </template>
    </el-dialog>
  </div>
</template>

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

/* Main Content */
.cooling-faults {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
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
  background: linear-gradient(135deg, #303133, #606266);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  margin: 0;
  color: #909399;
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
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 16px;
}

.stat-card :deep(.el-card__body) {
  padding: 16px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.total { background: rgba(64, 158, 255, 0.1); color: #409EFF; }
.stat-icon.healthy { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
.stat-icon.warning { background: rgba(230, 162, 60, 0.1); color: #E6A23C; }
.stat-icon.critical { background: rgba(245, 108, 108, 0.1); color: #F56C6C; }
.stat-icon.temp { background: rgba(64, 158, 255, 0.1); color: #409EFF; }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* Zones Summary */
.zones-summary {
  background: white;
  border-radius: 16px;
  padding: 16px 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.zones-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 600;
  font-size: 15px;
}

.zones-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
}

.zone-card {
  padding: 12px;
  border-radius: 12px;
  text-align: center;
  transition: all 0.2s ease;
}

.zone-card.good {
  background: rgba(103, 194, 58, 0.1);
  border-left: 3px solid #67C23A;
}

.zone-card.warning {
  background: rgba(230, 162, 60, 0.1);
  border-left: 3px solid #E6A23C;
}

.zone-card.critical {
  background: rgba(245, 108, 108, 0.1);
  border-left: 3px solid #F56C6C;
}

.zone-name {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
}

.zone-temp {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 4px;
}

.zone-card.good .zone-temp { color: #67C23A; }
.zone-card.warning .zone-temp { color: #E6A23C; }
.zone-card.critical .zone-temp { color: #F56C6C; }

.zone-racks {
  font-size: 11px;
  color: #909399;
}

/* Charts */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  border-radius: 16px;
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
  border-radius: 16px;
}

.table-card :deep(.el-card__body) {
  padding: 0;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-title {
  font-size: 16px;
  font-weight: 600;
}

.table-subtitle {
  font-size: 12px;
  color: #909399;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.temp-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.separator {
  color: #c0c4cc;
  font-size: 12px;
}

.pagination-wrapper {
  padding: 16px 20px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
}

/* Detail Dialog */
.unit-detail {
  padding: 0 0 16px 0;
}

.alerts-section {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.alerts-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
}

.alerts-actions {
  margin-top: 12px;
  text-align: right;
}

.detail-actions {
  margin-top: 20px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  flex-wrap: wrap;
}

.unresolved {
  color: #F56C6C;
  font-style: italic;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  }

  .charts-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .cooling-faults {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions {
    flex-direction: column;
  }

  .header-actions .el-input,
  .header-actions .el-select,
  .header-actions .el-button {
    width: 100%;
  }

  .chart {
    height: 260px;
  }

  .zones-grid {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  }
}
</style>